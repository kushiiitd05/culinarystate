"""STEP 07H-R: recipe-facing derived rows (ingredient mentions, process mentions, readiness) built from the existing designed vocabularies (ALIAS/ING/PROC/TOOL/UNIT ledgers).
No model inference: ingredient LINK status comes from exact normalised alias lookup only (method ALIAS_EXACT_LOOKUP); the frozen NER/linker/router are NOT re-run here (router status NOT_RUN)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LED = ROOT / "ledgers/data"


def _latest(name):
    d = {}
    for line in open(LED / f"{name}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            d[r["id"]] = r
    return {k: v for k, v in d.items() if v.get("status", "ACTIVE") == "ACTIVE"}


def norm(s) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


class Vocab:
    def __init__(self):
        ing, alias = _latest("ING"), _latest("ALIAS")
        self.ing = ing
        self.by_alias: dict[str, list] = {}
        for a in alias.values():
            self.by_alias.setdefault(a["normalized"], []).append((a.get("ingredient_id"), a.get("link_band"), a["id"]))
        self.by_name = {norm(i["canonical_name"]): i["id"] for i in ing.values()}
        proc = _latest("PROC")
        self.proc_forms: dict[str, str] = {}
        for p in proc.values():
            for base in [p["canonical_name"]] + list(p.get("aliases") or []):
                for f in verb_forms(norm(base)):
                    self.proc_forms.setdefault(f, p["id"])
        self.proc_name = {p["id"]: p["canonical_name"] for p in proc.values()}
        self.proc_kind = {p["id"]: p.get("kind") for p in proc.values()}
        self.units: dict[str, str] = {}
        for u in _latest("UNIT").values():
            for w in [u["canonical_name"]] + list(u.get("aliases") or []):
                self.units.setdefault(norm(w).replace("_", " "), u["id"])
        self.tools: dict[str, tuple] = {}
        for t in _latest("TOOL").values():
            for w in [t["canonical_name"]] + list(t.get("aliases") or []):
                self.tools.setdefault(norm(w), (t["id"], t.get("category")))


def verb_forms(v: str):
    v = v.strip()
    if not re.fullmatch(r"[a-z]+", v):
        return {v}
    out = {v, v + "s", v + "es", v + "ing", v + "ed"}
    if v.endswith("e"):
        out |= {v[:-1] + "ing", v + "d"}
    if v.endswith("y"):
        out |= {v[:-1] + "ies", v[:-1] + "ied"}
    if re.search(r"[^aeiou][aeiou][^aeiouwxy]$", v):
        out |= {v + v[-1] + "ing", v + v[-1] + "ed"}
    return out


_V = None


def vocab() -> Vocab:
    global _V
    if _V is None:
        _V = Vocab()
    return _V


def link(surface: str):
    """exact normalised alias / canonical-name lookup -> (ingredient_id|None, status, method, band)"""
    v = vocab()
    s = norm(surface)
    hits = v.by_alias.get(s)
    if hits:
        ids = {h[0] for h in hits if h[0]}
        band = hits[0][1]
        if len(ids) == 1:
            return next(iter(ids)), ("ACCEPT" if band in ("EXACT", "HIGH") else "REVIEW"), "ALIAS_EXACT_LOOKUP", band
        return None, "REVIEW", "ALIAS_EXACT_LOOKUP_MULTI_TARGET", band
    if s in v.by_name:
        return v.by_name[s], "ACCEPT", "CANONICAL_NAME_EXACT", "EXACT"
    return None, "UNRESOLVED", "NO_EXACT_ALIAS", None


_QTY_RX = None
TOKEN = re.compile(r"[A-Za-z]+")


def ingredient_mentions(rec: dict, units_rx) -> list[dict]:
    """one row per ingredient mention candidate; raw_span is a pointer (line index + char offsets), never copied text beyond the surface string"""
    rows = []
    rid, fam = rec["recipe_id"], rec["source_family"]

    def add(idx, line, surface, start, end, method, qty_raw=None, unit_raw=None, mods=None, ext=None):
        ing_id, status, lm, band = link(surface) if surface else (None, "UNRESOLVED", "NO_SURFACE", None)
        rows.append({"mention_id": f"MEN-{rid}-{idx}-{start}", "recipe_id": rid, "source_family": fam, "ingredient_index": idx, "raw_span": surface, "char_start": start, "char_end": end, "extraction_method": method,
                     "candidate_ingredient_id": ing_id, "link_status": status, "link_method": lm, "link_band": band, "link_confidence": None, "router_status": "NOT_RUN_FROZEN_MODEL_PENDING", "quantity_raw": qty_raw, "unit_raw": unit_raw,
                     "quantity_pointer": f"{rid}#ingredient={idx}", "form_state_modifiers": mods, "external_label": ext, "source_plane": "RECIPE"})

    if fam == "A1_BBC_GOOD_FOOD":
        for m in rec["extra"].get("mentions") or []:
            surf = m.get("ingredient_surface") or m.get("ingredient_normalized") or ""
            add(int(m["ingredient_index"]), m.get("raw_phrase"), surf, (m.get("raw_phrase") or "").lower().find(surf.lower()) if surf else -1, None, "A1_" + str(m.get("extraction_method")), m.get("quantity_raw"), m.get("unit_raw"), m.get("processing_state"))
    elif fam in ("WIKIBOOKS", "FOODCOM"):
        for i, line in enumerate(rec["ingredient_lines"]):
            if fam == "FOODCOM":
                parts, qs = rec["extra"]["ingredient_parts"], rec["extra"]["ingredient_quantities"]
                add(i, line, (parts[i] or "").strip(), line.find(parts[i] or ""), None, "FOODCOM_INGREDIENT_PART", (qs[i] or None) if qs[i] else None)
            else:
                m = units_rx.match(line) if units_rx else None
                rest = line[m.end():] if m else line
                surf = re.split(r"[,(;]", rest, 1)[0].strip()
                add(i, line, surf, line.find(surf), None, "RULE_STRIP_QUANTITY_PREFIX", m.group("x").strip() if m else None)
    elif fam == "TASTESET":
        try:
            ents = json.loads(rec["extra"]["entities_json"])
        except Exception:
            ents = []
        text = "\n".join(rec["ingredient_lines"])
        for e in ents:
            if e.get("type") == "FOOD":
                add(0, None, e.get("entity"), e.get("start"), e.get("end"), "TASTESET_HUMAN_ENTITY", ext="TASTESET:FOOD")
    elif fam == "GUTENBERG_SEGMENT":
        for j, iid in enumerate(rec["extra"].get("legacy_ing_ids") or []):
            rows.append({"mention_id": f"MEN-{rid}-L{j}", "recipe_id": rid, "source_family": fam, "ingredient_index": None, "raw_span": None, "char_start": None, "char_end": None, "extraction_method": "LEGACY_ING_IDS_OLD_PIPELINE",
                         "candidate_ingredient_id": iid, "link_status": "REVIEW", "link_method": "LEGACY_ID_NO_SPAN", "link_band": None, "link_confidence": None, "router_status": "NOT_RUN_FROZEN_MODEL_PENDING", "quantity_raw": None, "unit_raw": None,
                         "quantity_pointer": None, "form_state_modifiers": None, "external_label": None, "source_plane": "RECIPE"})
    return rows


def process_mentions(rec: dict, expr_by_step: dict) -> list[dict]:
    """per sentence: mapped PROC candidates (verb-form match) + the leading token as UNMAPPED when no PROC matched. No mechanism, no chemistry."""
    v = vocab()
    rows = []
    for si, step in enumerate(rec["steps"]):
        sents = re.split(r"(?<=[.!?])\s+", step)
        pos = 0
        for sj, sent in enumerate(sents):
            start = step.find(sent, pos)
            pos = start + len(sent)
            found = []
            first = TOKEN.search(sent)
            for m in TOKEN.finditer(sent):
                w = m.group(0).lower()
                pid = v.proc_forms.get(w)
                if pid:
                    # homograph with an ingredient name (butter, salt, oil...): count as an action only when imperative-initial or after 'to/and/then'
                    if (w in v.by_alias or w in v.by_name) and not (first is not None and m.start() == first.start()) and not re.search(r"\b(?:to|and|then|until)\s+$", sent[max(0, m.start() - 6): m.start()], re.I):
                        continue
                    found.append((m.start(), m.end(), pid, m.group(0)))
            cond_ids = ",".join(expr_by_step.get((si, sj), []))
            if found:
                for a, b, pid, w in found:
                    rows.append({"recipe_id": rec["recipe_id"], "instruction_index": si, "sentence_index": sj, "char_start": start + a, "char_end": start + b, "raw_action": w, "candidate_proc_id": pid, "proc_kind": v.proc_kind.get(pid),
                                 "mapping_status": "CANDIDATE_VERB_FORM_MATCH_POS_UNCHECKED", "modifier": None, "endpoint_phrase": None, "condition_expression_ids": cond_ids, "source_plane": "RECIPE"})
            else:
                m = TOKEN.match(sent.strip())
                if m and len(sent.strip()) > 3:
                    rows.append({"recipe_id": rec["recipe_id"], "instruction_index": si, "sentence_index": sj, "char_start": start, "char_end": start + len(m.group(0)), "raw_action": m.group(0), "candidate_proc_id": None, "proc_kind": None,
                                 "mapping_status": "UNMAPPED", "modifier": None, "endpoint_phrase": None, "condition_expression_ids": cond_ids, "source_plane": "RECIPE"})
    return rows


def readiness(rec: dict, expr: list[dict]) -> dict:
    fam = lambda *f: [e for e in expr if e["expression_family"] in f]
    num = lambda e: e["normalized_status"] in ("VALID", "AMBIGUOUS") and (e["canonical_value"] is not None or e["canonical_low"] is not None or e["canonical_high"] is not None)
    temps = [e for e in fam("TEMPERATURE") if num(e)]
    d = {"has_time": any(num(e) for e in fam("TIME", "TIME_STRUCTURED_FIELD")), "has_numeric_temperature": bool(temps), "has_temperature_location": any(e["measurement_location"] not in (None, "UNSPECIFIED") for e in temps), "has_pressure": any(num(e) for e in fam("PRESSURE")),
         "has_power": any(num(e) for e in fam("POWER")), "has_qualitative_heat": bool(fam("QUALITATIVE_HEAT", "GAS_MARK")), "has_endpoint_condition": bool(fam("ENDPOINT")),
         "has_quantity_information": any(e["normalized_status"] == "VALID" for e in fam("QUANTITY")), "has_geometry_information": bool(fam("GEOMETRY")), "has_medium_information": bool(fam("MEDIUM"))}
    if not rec["steps"]:
        status = "UNKNOWN"
    elif d["has_time"] and d["has_numeric_temperature"] and d["has_temperature_location"] and d["has_quantity_information"]:
        status = "PROCEDURALLY_RICH"
    elif d["has_time"] or d["has_numeric_temperature"] or d["has_pressure"] or d["has_power"]:
        status = "PARTIAL_CONDITIONS"
    elif d["has_qualitative_heat"] or d["has_endpoint_condition"] or fam("TIME_QUALITATIVE"):
        status = "QUALITATIVE_ONLY"
    else:
        status = "INSUFFICIENT_CONDITIONS"
    d["readiness_status"] = status
    return d


# ---------- quantity mentions via the EXISTING deterministic quantity grammar (src/culinarystate/quantity; SSOT 235) ----------
LOCALE = {"A1_BBC_GOOD_FOOD": "UK", "FOODCOM": "US"}  # others: unknown -> locale-ambiguous ranges kept, never guessed


def _ch(d: dict, k: str):
    return d.get("status"), d.get("value"), d.get("low"), d.get("high"), d.get("unit")


def quantity_mentions(rec: dict) -> list[dict]:
    from culinarystate.quantity.grammar import parse_line
    from culinarystate.quantity.normalize import normalize
    rows = []
    loc = LOCALE.get(rec["source_family"])
    for i, line in enumerate(rec["ingredient_lines"]):
        if not line or not line.strip():
            continue
        p = parse_line(line)
        n = normalize(p, loc)
        ms, mv, ml, mh, mu = _ch(n.mass_g, "mass")
        vs, vv, vl, vh, vu = _ch(n.volume_ml, "vol")
        cs, cv, cl, ch, cu = _ch(n.count, "count")
        rows.append({"recipe_id": rec["recipe_id"], "source_family": rec["source_family"], "ingredient_index": i, "mention_pointer": f"{rec['recipe_id']}#ingredient={i}", "raw_quantity": line[p.span[0]:p.span[1]] if p.span else None,
                     "parse_kind": p.kind, "number": p.value, "range_low": p.low, "range_high": p.high, "unit_key": p.unit_key, "unit_raw": p.unit_raw, "multiplier": p.multiplier, "package_key": p.package_key,
                     "qualitative_amount": (n.mass_g.get("qualitative") if p.kind == "QUALITATIVE" else None), "qualifiers": ",".join(p.qualifiers) or None, "size_word": p.size, "part": p.part, "locale_used": loc,
                     "q_level": n.q_level, "conversion_method": n.conversion_method, "conversion_path": " | ".join(n.path) or None, "flags": ",".join(n.flags) or None,
                     "mass_status": ms, "mass_value": mv, "mass_low": ml, "mass_high": mh, "volume_status": vs, "volume_value": vv, "volume_low": vl, "volume_high": vh, "count_status": cs, "count_value": cv, "count_low": cl, "count_high": ch, "count_unit": cu,
                     "uncertainty": "RANGE_OR_LOCALE_RANGE" if "RANGE" in (ms, vs, cs) else None, "source_plane": "RECIPE", "grammar": "quantity.grammar_v0"})
    return rows
