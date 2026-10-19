#!/usr/bin/env python3
"""D-016: convert the OpenAI GPT-5.6 Sol review draft (annotation/ai_review/pilot_20) into gold-1.0 files under handbook v1 + Addendum A.

  /opt/anaconda3/bin/python tools/convert_ai_review.py            # writes Kush files only (DONE if valid+replay-clean); Parv's stay blank
Mechanical rules only; every judgment call is logged in annotation/ai_review/pilot_20/conversion_log.csv for the human review.
Provenance stays in each file's `notes` (AI_DRAFT_HUMAN_REVIEWED). The frozen recipe text is asserted unchanged. Refuses to
overwrite a pilot_20 file that already holds work other than a blank draft or an earlier conversion.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import validate_gold, to_events  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

AI = ROOT / "annotation" / "ai_review" / "pilot_20"
LAB = {"AMOUNT": "QUANTITY", "FOOD_MENTION": "FOOD", "HEAT_TEMPERATURE": "TEMPERATURE", "DURATION": "TIME",
       "PREP_STATE": "STATE", "INTERMEDIATE_MENTION": "INTERMEDIATE"}
DROP = {"QUALITATIVE_AMOUNT", "PURPOSE"}                     # handbook: 'some' -> UNKNOWN, no span; no PURPOSE label
TIME_RE = re.compile(r"\d+\s*(?:[-–]\s*\d+\s*)?(?:mins?|minutes?|hours?|hrs?|secs?|seconds?)\b|few mins?|overnight|few minutes", re.I)
TEMP_RE = re.compile(r"\d+\s*°|\d+\s*C\b|gas \d|fan\b|degrees|(?:low|medium|high|medium-high|medium-low)\s+heat|simmer|boil", re.I)
TOOL_RE = re.compile(r"\b(pan|pot|oven|bowl|tray|tin|sheet|jar|processor|blender|grill|wok|dish|saucepan|skillet|microwave|steamer|colander|sieve|board)\b", re.I)
log: list[dict] = []
skipped: dict = {}


def note(rid, where, kind, detail):
    log.append({"recipe_id": rid, "where": where, "kind": kind, "detail": detail})


def registry():
    """surface (normalised) -> ING canonical name, from the ING ledger and its English aliases."""
    from culinarystate.ledgers.store import LedgerStore
    st = LedgerStore()
    ings = {i["id"]: i["canonical_name"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    names = {norm(c): c for c in ings.values()}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a["language"] == "en" and a.get("ingredient_id") in ings:
            names.setdefault(norm(a["normalized"]), ings[a["ingredient_id"]])
    return names


def concept_for(rid, li, names):
    cand = str(li["concept_candidate"] or "")
    first = re.split(r"\s+OR\s+|/", cand, flags=re.I)[0].strip()
    if norm(first) in names:
        return names[norm(first)]
    words = norm(first).split()
    for n in range(len(words), 0, -1):                       # right-most longest n-gram = head match (flagged for review)
        for i in range(len(words) - n, -1, -1):
            g = " ".join(words[i:i + n])
            if g in names:
                note(rid, f"line {li['line_index']}", "CONCEPT_BY_HEAD_MATCH", f"'{cand}' -> '{names[g]}'")
                return names[g]
    note(rid, f"line {li['line_index']}", "CONCEPT_UNKNOWN", f"'{cand}' not in ING registry")
    return "UNKNOWN"


def short(s):
    return re.sub(r"\s+", " ", re.sub(r"^R\d+_ING_\d+_", "", s).replace("_", " ")).strip().lower()


def parse_cond(rid, where, cond, endpoint):
    out, rest = {}, []
    parts = [] if not cond else ([p.strip() for p in cond.split(";")] if isinstance(cond, str) else [])
    for p in parts:
        if not p or re.search(r"not (?:numerically )?stated|not stated|unknown", p, re.I):
            continue
        if TIME_RE.search(p) and "time" not in out:
            out["time"] = p
        elif TEMP_RE.search(p) and "temperature" not in out and not re.search(r"water at", p, re.I):
            out["temperature"] = p
        elif re.search(r"water at|oil|stock|boiling|hot ", p, re.I) and "medium" not in out:
            out["medium"] = p
        elif TOOL_RE.search(p) and "tool" not in out:
            out["tool"] = p
        else:
            rest.append(p)
    if endpoint:
        out["endpoint"] = endpoint
    if rest:
        note(rid, where, "CONDITION_NOT_MAPPED", "; ".join(rest))
    return out


def convert(x, names):
    rid = x["recipe_id"]
    doc = {"schema_version": "gold-1.0", "recipe_id": rid, "source_ref": x["source_ref"], "locale": x.get("locale") or "UK",
           "ingredient_lines": [], "steps": [], "unknowns": [], "notes": ""}
    alias, succ, alive, used, contained = {}, {}, set(), set(), set()

    def label_for(base):
        b, k = base, 2
        while b in used:
            b, k = f"{base} {k}", k + 1
        used.add(b)
        return b
    for li in x["ingredient_lines"]:
        spans = []
        for s in li["spans"]:
            if s["label"] in DROP:
                note(rid, f"line {li['line_index']}", "SPAN_DROPPED", f"{s['label']}:{s['text']}")
                continue
            spans.append({"start": s["start"], "end": s["end"], "label": LAB.get(s["label"], s["label"]), "text": s["text"]})
        food = next((s["text"] for s in spans if s["label"] == "FOOD"), li["concept_candidate"] or li["text"])
        ent = label_for(short(li["entity"]) or norm(food))
        row = {"line_index": li["line_index"], "text": li["text"], "spans": spans, "entity": ent,
               "concept": concept_for(rid, li, names)}
        if any(s["label"] == "OPTIONAL" for s in spans):
            row["optional"] = True
        alts = [s["text"] for s in spans if s["label"] == "ALTERNATIVE"]
        if alts:
            row["alternatives"] = alts
        doc["ingredient_lines"].append(row)
        alive.add(ent)
        alias[ent] = ent
        if row["concept"] != "UNKNOWN":
            alias.setdefault(norm(row["concept"]), ent)
        alias[short(li["entity"])] = ent
        alias[norm(food)] = alias.get(norm(food), ent)
        alias[(li["concept_candidate"] or "").lower()] = alias.get((li["concept_candidate"] or "").lower(), ent)

    def follow(n):
        while n is not None and n not in alive and n in succ:
            n = succ[n]
        return n

    def res(name, where=None):
        n = alias.get(str(name).lower()) or alias.get(norm(str(name))) or alias.get(short(str(name)))
        if n is None:                                       # unique token-overlap match among alias keys (logged)
            q = set(norm(str(name)).split())
            best = []
            for key, lab in alias.items():
                t = set(norm(key).split())
                if q and t and (q <= t or t <= q):
                    best.append((len(q & t) / len(q | t), lab))
            if best:
                top = max(b[0] for b in best)
                labs = {lab for sc, lab in best if sc == top}
                if top >= 0.5 and len(labs) == 1:
                    n = labs.pop()
                    note(rid, where or "", "FUZZY_REFERENCE", f"'{name}' -> '{n}'")
        if n is None:                                       # longest alias key fully contained in the phrase (logged)
            q = set(norm(str(name)).split())
            cand = [(len(norm(k).split()), lab) for k, lab in alias.items()
                    if norm(k) and set(norm(k).split()) <= q and len(norm(k)) >= 3]
            if cand:
                top = max(c[0] for c in cand)
                labs = {lab for ln, lab in cand if ln == top}
                if len(labs) == 1:
                    n = labs.pop()
                    contained.add(str(name).lower())
                    note(rid, where or "", "FUZZY_CONTAINMENT", f"'{name}' -> '{n}'")
        return follow(n)

    def reg_out(outn, label):
        if outn:
            for part in re.split(r"\s\+\s", outn):
                alias[part.strip().lower()] = label

    for st in x["steps"]:
        k = st["step_index"]
        spans = []
        for s in st["spans"]:
            if s["label"] in DROP:
                note(rid, f"step {k}", "SPAN_DROPPED", f"{s['label']}:{s['text']}")
                continue
            spans.append({"start": s["start"], "end": s["end"], "label": LAB.get(s["label"], s["label"]), "text": s["text"]})
        evs = []
        for e in st["events"]:
            op, act = e["operation"], e["action"]
            where = f"step {k} {e['event_id']}"
            pairs = [(nm, res(nm, where)) for nm in e["inputs"]]
            liquid = [nm for nm, lab in pairs if lab is None and re.search(r"\b(water|juices?|stock|liquid)\b", nm, re.I)]
            ins = [lab for nm, lab in pairs if lab is not None]
            if liquid:
                note(rid, where, "IMPLICIT_LIQUID", f"{op} {act}: {liquid} is not an ingredient; kept as medium/split output, not an entity")
            miss = [nm for nm, lab in pairs if lab is None and nm not in liquid]
            if not ins:
                note(rid, where, "UNRESOLVED_REFERENCE", f"{op} {act}: {miss or e['inputs']} not an ingredient or earlier output; event not written")
                skipped[rid] = skipped.get(rid, 0) + 1
                continue
            if miss:
                note(rid, where, "PARTIAL_INPUTS", f"{op} {act}: written with {ins}; unresolved inputs dropped: {miss}")
            cond = parse_cond(rid, where, e.get("conditions"), e.get("endpoint"))
            outn = e.get("output")
            if liquid and op != "SPLIT" and "medium" not in cond:
                cond["medium"] = liquid[0]
            ev = None
            if op in ("TRANSFORM", "WAIT") and len(ins) == 1:
                ev = {"type": "Transform", "target": ins[0], "process": act if op == "TRANSFORM" else "rest" if not act else act, **cond}
                reg_out(outn, ins[0])
                if op == "WAIT":
                    note(rid, where, "WAIT_AS_TRANSFORM", f"'{act}' recorded as Transform")
            elif op == "TRANSFORM":
                out = label_for(short(outn) or "+".join(ins))
                ev = {"type": "Merge", "inputs": ins, "output": out, "process": act}
                note(rid, where, "MULTI_INPUT_TRANSFORM_AS_MERGE", f"{act}: {e['inputs']} -> {out}")
                evs.append(ev)
                alive -= set(ins)
                for i in ins:
                    succ[i] = out
                alive.add(out)
                alias[(outn or out).lower()] = out
                if cond:
                    ev = {"type": "Transform", "target": out, "process": act, **cond}
                else:
                    ev = None
            elif op == "MERGE":
                if len(set(ins)) < 2 and ins:
                    ev = {"type": "Transform", "target": ins[0], "process": act, **cond}
                    note(rid, where, "SINGLE_INPUT_MERGE_AS_TRANSFORM", f"{act} {e['inputs']}")
                else:
                    out = label_for(short(outn) or "+".join(ins))
                    ev = {"type": "Merge", "inputs": list(dict.fromkeys(ins)), "output": out, "process": act}
                    alive -= set(ins)
                    for i in ins:
                        succ[i] = out
                    alive.add(out)
                    alias[(outn or out).lower()] = out
            elif op == "RECOMBINE":
                if len(set(ins)) < 2:
                    ev = {"type": "Transform", "target": ins[0], "process": act, **cond}
                else:
                    out = label_for(short(outn) or "+".join(ins))
                    ev = {"type": "Merge", "inputs": list(dict.fromkeys(ins)), "output": out, "process": act}
                    alive -= set(ins)
                    for i in ins:
                        succ[i] = out
                    alive.add(out)
                    alias[(outn or out).lower()] = out
                note(rid, where, "RECOMBINE_AS_MERGE", f"'{act}' is adding a component, not returning a reserved portion")
            elif op == "RESERVE":
                qm = re.match(r"\s*(\d+(?:\.\d+)?\s*(?:tbsp|tsp|g|kg|ml|l|cups?|cloves?|slices?)\b.*)", e["inputs"][0], re.I)
                if qm and e["inputs"][0].lower() in contained:
                    out = label_for("reserved " + short(re.sub(r"^[\d.]+\s*\w+\s+", "", e["inputs"][0])))
                    ev = {"type": "Reserve", "target": ins[0], "output": out, "portion": qm.group(1)}
                    alive.add(out)
                    reg_out(outn, out)
                    alias[e["inputs"][0].lower()] = out
                    note(rid, where, "RESERVE_PORTION_WRITTEN", f"'{e['inputs'][0]}' -> Reserve(portion) from '{ins[0]}'")
                else:
                    note(rid, where, "RESERVE_NOT_WRITTEN", f"'{act}' of the whole {e['inputs']}: not a portion; alias only")
                    if ins:
                        reg_out(outn, ins[0])
            elif op == "DISCARD":
                ev = {"type": "Discard", "target": ins[0]}
                if e["inputs"][0].lower() in contained:
                    ev["portion"] = e["inputs"][0]
                    note(rid, where, "DISCARD_PARTIAL_AS_PORTION", f"'{e['inputs'][0]}' discarded from '{ins[0]}' (amount unknown)")
                else:
                    alive.discard(ins[0])
            elif op == "TRANSFER":
                loc = None
                m = re.search(r"\b(?:on|in|into|onto|to)\s+(?:a|an|the)?\s*([a-z][\w \-]+)$", outn or "", re.I)
                loc = (m.group(1).strip() if m else None) or (cond.get("tool")) or (outn or "").strip()
                ev = {"type": "Transfer", "target": ins[0], "location": loc}
                note(rid, where, "TRANSFER_LOCATION_PARSED", f"'{outn}' -> '{loc}'")
                reg_out(outn, ins[0])
            elif op == "SPLIT":
                note(rid, where, "SPLIT_REVIEW", f"{act}: inputs={e['inputs']} output={outn!r} cond={e.get('conditions')!r}")
                tgt = ins[0]
                parts = [p.strip() for p in re.split(r"\s\+\s", outn or "") if p.strip()]
                eq = "equal" in str(e.get("conditions", "")).lower()
                outs, plabels = [], []
                if len(parts) == 1 and re.match(r"\d+\s+\S", parts[0]) and len(ins) == 1:
                    n = int(re.match(r"(\d+)", parts[0]).group(1))
                    base = short(re.sub(r"^\d+\s+", "", parts[0])).rstrip("s")
                    outs = [{"label": label_for(f"{base} {j + 1}"), "fraction": f"1/{n}" if eq else None} for j in range(n)]
                    plabels = [(parts[0], outs[0]["label"])]
                else:
                    for p in parts or [outn or f"{tgt} part"]:
                        lab = label_for(short(re.sub(r"^\d+\s+", "", p)) or f"{tgt} part")
                        outs.append({"label": lab, "fraction": None})
                        plabels.append((p, lab))
                    if len(outs) == 1:
                        outs.append({"label": label_for(f"{tgt} remainder"), "fraction": None})
                        note(rid, where, "SPLIT_SINGLE_OUTPUT_PADDED", f"{act}: one output named; remainder added")
                ev = {"type": "Split", "target": tgt, "outputs": outs}
                alive.discard(tgt)
                for o in outs:
                    alive.add(o["label"])
                succ[tgt] = outs[0]["label"]
                for p, lab in plabels:
                    alias[p.lower()] = lab
                    alias[re.sub(r"^\d+\s+", "", p).lower()] = lab
                alias[(outn or "").lower()] = outs[0]["label"]
                for nm in e["inputs"][1:]:                       # e.g. 'cooking water' separated by draining
                    alias.setdefault(nm.lower(), outs[-1]["label"])
            else:
                note(rid, where, "OPERATION_NOT_MAPPED", f"{op} {act}")
            if ev:
                evs.append(ev)
        coref = []
        for c in st["coref"]:
            tgt = res(c.get("target", ""))
            coref.append({"mention": c["mention"], "start": c["start"], "end": c["end"], "entity": tgt or "UNKNOWN"})
            if not tgt:
                note(rid, f"step {k}", "COREF_TARGET_UNRESOLVED", f"'{c['mention']}' -> UNKNOWN (draft target: {c.get('target')!r})")
        doc["steps"].append({"step_index": k, "text": st["text"], "spans": spans, "events": evs, "coref": coref})
    doc["unknowns"] = [{"what": u, "why": "stated unknown/limitation in the AI review draft"} for u in x["unknowns"]]
    return doc, x.get("final_state_summary"), x.get("review_note", "")


def main():
    names = registry()
    data = json.loads((AI / "pilot20_AI_REVIEW_combined.json").read_text())
    summary = []
    for x in data:
        doc, fs, rn = convert(x, names)
        rid = doc["recipe_id"]
        for who in ("Kush",):                       # Parv annotates blind: never receives the AI draft (D-016)
            p = ROOT / "annotation" / "gold" / "pilot_20" / who / f"{rid}.{who}.json"
            cur = json.loads(p.read_text())
            if (cur["status"] == "DONE" or any(l["spans"] for l in cur["ingredient_lines"])) and "AI_DRAFT_HUMAN_REVIEWED" not in cur.get("notes", ""):
                summary.append((rid, who, "SKIPPED_EXISTING_WORK"))
                continue
            assert [l["text"] for l in cur["ingredient_lines"]] == [l["text"] for l in doc["ingredient_lines"]]
            assert [s["text"] for s in cur["steps"]] == [s["text"] for s in doc["steps"]]
            e = json.loads(json.dumps(doc))
            e["annotator"] = who
            who_txt = ("reviewed in full and accepted by Kush (his statement); converted by Claude to gold-1.0, "
                       "conversion log: annotation/ai_review/pilot_20/conversion_log.csv" if who == "Kush"
                       else "pending review by Parv; converted by Claude to gold-1.0")
            e["notes"] = (f"[{skipped.get(rid, 0)} draft events could not be converted, see conversion_log.csv] "
                          f"AI_DRAFT_HUMAN_REVIEWED (D-016): drafted by OpenAI GPT-5.6 Sol 2026-10-19 (blind_human_gold=false); "
                          f"{who_txt}. Not an independent blind annotation. Draft final state: {fs}. {rn}").strip()
            errs = validate_gold({**e, "status": "DONE"})
            iss = [] if errs else list(replay(to_events(e)).issues)
            e["status"] = "DONE" if (who == "Kush" and not errs and not iss) else "DRAFT"
            p.write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n")
            summary.append((rid, who, e["status"], errs[:1], iss[:2]))
    with (AI / "conversion_log.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["recipe_id", "where", "kind", "detail"])
        w.writeheader()
        w.writerows(log)
    for s in summary:
        if s[1] == "Kush":
            print(s)
    from collections import Counter
    print(Counter(r["kind"] for r in log))


if __name__ == "__main__":
    main()
