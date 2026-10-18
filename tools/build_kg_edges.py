#!/usr/bin/env python3
"""X3c: KGE ledger — typed concept edges with support, association and confidence over BBC + Wikibooks (D-011).

  /opt/anaconda3/bin/python tools/build_kg_edges.py
Writes ledgers/data/KGE.jsonl, registry/kg/kg_edges_v1.csv (IDs + stats, no text), reports/kg_edges_v1.md.
Statistical edges are corpus associations, not facts: confidence = Wilson lower bound, never human-verified.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.conditions import extract_conditions  # noqa: E402
from culinarystate.kg import corpus  # noqa: E402
from culinarystate.kg.edges import PairCounter, quantile_confidence, quantiles  # noqa: E402
from culinarystate.kg.mine import alternatives, endpoints, forms, is_optional, media  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.process.tools import find_tools  # noqa: E402
from culinarystate.process.vocab import BY_CANON  # noqa: E402
from culinarystate.quantity.grammar import parse_line  # noqa: E402
from culinarystate.state_graph.rule_compiler import step_processes  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402
from culinarystate.vocab.line_link import LineLinker  # noqa: E402

A1 = ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl"
WB = ROOT / "data" / "interim" / "wikibooks"
AGENT, CB = "kg_edges@0.1", "Kush+Claude"
TIMED = {"DRY_HEAT", "FAT_HEAT", "WET_HEAT", "HEAT_GENERAL", "COOLING", "RESTING", "FERMENT_LEAVEN", "MECHANICAL_MIX",
         "PRESERVATION"}
# predicate: (min recipe support, min lift, top-k per subject)
PARAMS = {"ING_PROCESSED_BY": (10, 1.3, 15), "PROC_USES_TOOL": (10, 1.5, 8), "PROC_FOLLOWED_BY": (10, 1.2, 8),
          "ING_CO_OCCURS": (15, 2.0, 10), "ING_USED_IN_CUISINE": (5, 1.5, 5), "ING_MEASURED_IN_UNIT": (10, 0.0, 3),
          "COMPONENT_CONTAINS_ING": (5, 1.5, 5), "ING_ALTERNATIVE_TO": (5, 1.5, 8), "ING_OFTEN_OPTIONAL": (10, 1.5, 1),
          "ING_PREP_FORM": (10, 1.5, 5), "PROC_USES_MEDIUM": (10, 1.3, 5), "PROC_ENDPOINT_STATE": (10, 1.3, 8)}
VALUE_OBJ = {"ING_USED_IN_CUISINE", "COMPONENT_CONTAINS_ING", "ING_OFTEN_OPTIONAL", "ING_PREP_FORM", "PROC_USES_MEDIUM",
             "PROC_ENDPOINT_STATE"}
GUT = ROOT / "data" / "interim" / "gutenberg" / "recipes.jsonl"


def lookups(st: LedgerStore):
    ings = [i for i in st.all_latest("ING") if i["status"] == "ACTIVE"]
    names = {norm(i["canonical_name"]): i["id"] for i in ings}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en" and a["alias_type"] != "AMBIGUOUS":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    surfaces = defaultdict(set)
    for k, iid in names.items():
        if len(k) > 2:
            surfaces[iid].add(k)
    proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
    tool = {t["canonical_name"]: t["id"] for t in st.all_latest("TOOL") if t["status"] == "ACTIVE"}
    unit = {}
    for u in st.all_latest("UNIT"):
        for a in (u["canonical_name"], *(u.get("aliases") or [])):
            unit.setdefault(a.lower(), u["id"])
    return ings, names, surfaces, proc, tool, unit


def recipes(st: LedgerStore, names: dict, unit: dict, linker: LineLinker):
    recs = st.all_latest("REC")
    bbc_ids = {r["external_refs"][0].split(":", 1)[1]: r["id"] for r in recs
               if r["status"] == "ACTIVE" and (r.get("external_refs") or [""])[0].startswith("A1:")}
    wb_ids = {int(r["external_refs"][0].split(":")[1]): r["id"] for r in recs
              if r["status"] == "ACTIVE" and (r.get("external_refs") or [""])[0].startswith("WIKIBOOKS:")}
    cuisine_of = {r["id"]: r.get("cuisine") for r in recs}
    yield from corpus.bbc(A1, bbc_ids, linker, names)
    yield from corpus.wikibooks(WB / "recipes.jsonl", ROOT / "registry" / "recipes" / "wikibooks_ingredient_links_v1.csv",
                                wb_ids, cuisine_of)
    if GUT.exists():
        yield from corpus.gutenberg(GUT)


def scan(st: LedgerStore):
    ings, names, surfaces, proc, tool, unit = lookups(st)
    pcs = {k: PairCounter() for k in PARAMS}
    cuisine_pc, comp_pc = pcs["ING_USED_IN_CUISINE"], pcs["COMPONENT_CONTAINS_ING"]
    dur, temp = defaultdict(list), defaultdict(list)
    n_by_src = Counter()
    linker = LineLinker(names, set(unit))
    for rv in recipes(st, names, unit, linker):
        n_by_src[rv.family] += 1
        lines = [(t, i or (linker.link(t)[0] if t else None)) for t, i in rv.lines]
        line_ings = {i for _, i in lines if i}
        alt = {x for t, _ in lines if " or " in t.lower()
               for x in [alternatives(t, lambda ph: linker.match_phrase(linker.phrase(ph)))] if x}
        pcs["ING_ALTERNATIVE_TO"].add_recipe(rv.family, rv.ing_ids | line_ings, rv.ing_ids | line_ings,
                                             alt | {(b, a) for a, b in alt})
        opt = {(i, "OPTIONAL") for t, i in lines if i and is_optional(t)}
        pcs["ING_OFTEN_OPTIONAL"].add_recipe(rv.family, line_ings, {"OPTIONAL"} if opt else set(), opt)
        fpairs = {(i, f) for t, i in lines if i for f in forms(t)}
        pcs["ING_PREP_FORM"].add_recipe(rv.family, line_ings, {f for _, f in fpairs}, fpairs)
        med_pairs, end_pairs = set(), set()
        ing_procs, proc_tools, transitions, seq, all_procs, all_tools = set(), set(), set(), [], set(), set()
        for s in rv.steps:
            pos_ps = [(pos, p) for pos, p in step_processes(s) if p in proc]
            ps = [p for _, p in pos_ps]
            med_pairs |= {(proc[p], m) for p in ps if BY_CANON[p].family in TIMED for m in media(s)}
            end_pairs |= {(proc[p], e) for p, e in endpoints(s, pos_ps)}
            ts = {t for _, t, _ in find_tools(s) if t in tool}
            all_procs.update(ps)
            all_tools.update(ts)
            text = f" {norm(s)} "
            mentioned = {i for i in rv.ing_ids if any(f" {x} " in text for x in surfaces.get(i, ()))}
            ing_procs |= {(i, proc[p]) for i in mentioned for p in ps}
            proc_tools |= {(proc[p], tool[t]) for p in ps for t in ts}
            seq += ps
            timed = {p for p in ps if BY_CANON[p].family in TIMED}
            if len(timed) == 1:
                p = proc[next(iter(timed))]
                c = extract_conditions(s)
                for d in c["durations"]:
                    v = d.get("value") if d["status"] == "MEASURED" else (d["low"] + d["high"]) / 2
                    if 0 < v <= 2880:
                        dur[p].append(v)
                for t in c["temperatures"]:
                    q = t["value"]
                    if q["status"] not in ("MEASURED", "RANGE"):          # stated bounds ("above 180 °C") skipped
                        continue
                    v = q.get("value") if q["status"] == "MEASURED" else (q["low"] + q["high"]) / 2
                    v = (v - 32) * 5 / 9 if q["unit"] == "degF" else v
                    if -40 <= v <= 300:
                        temp[p].append(v)
        dedup = [p for i, p in enumerate(seq) if i == 0 or p != seq[i - 1]]
        transitions = {(proc[a], proc[b]) for a, b in zip(dedup, dedup[1:])}
        pid_set = {proc[p] for p in all_procs}
        pcs["ING_PROCESSED_BY"].add_recipe(rv.family, rv.ing_ids, pid_set, ing_procs)
        pcs["PROC_USES_TOOL"].add_recipe(rv.family, pid_set, {tool[t] for t in all_tools}, proc_tools)
        pcs["PROC_FOLLOWED_BY"].add_recipe(rv.family, pid_set, pid_set, transitions)
        pcs["ING_CO_OCCURS"].add_recipe(rv.family, rv.ing_ids, rv.ing_ids,
                                        {(a, b) for a in rv.ing_ids for b in rv.ing_ids if a != b})
        pcs["PROC_USES_MEDIUM"].add_recipe(rv.family, pid_set, {m for _, m in med_pairs}, med_pairs)
        pcs["PROC_ENDPOINT_STATE"].add_recipe(rv.family, pid_set, {e for _, e in end_pairs}, end_pairs)
        units = {(i, unit[q.unit_key]) for t, i in lines if i and (q := parse_line(t)).unit_key in unit}
        pcs["ING_MEASURED_IN_UNIT"].add_recipe(rv.family, {i for i, _ in units}, {u for _, u in units}, units)
        if rv.cuisines:
            cuisine_pc.add_recipe(rv.family, rv.ing_ids, set(rv.cuisines), {(i, c) for i in rv.ing_ids for c in rv.cuisines})
        if rv.components:
            cp = {(i, c) for c, ids in rv.components.items() for i in ids}
            comp_pc.add_recipe(rv.family, {i for i, _ in cp}, set(rv.components), cp)
    return ings, proc, tool, pcs, dur, temp, n_by_src


def record(st, pred, subj, obj_id, obj_val, support, conf, band_, method, src_ids, assoc=None, quant=None):
    key = f"{pred}|{subj}|{obj_id or obj_val}"
    rec = {"id": st.ids.mint("KGE", key=key), "record_type": "KGE", "status": "ACTIVE", "created_by": CB,
           "provenance": {"method": "DERIVED", "source_ids": src_ids, "agent": AGENT},
           "verification": {"status": "UNVERIFIED"}, "predicate": pred, "subject_id": subj,
           "object_id": obj_id, "object_value": obj_val, "support": support, "confidence": conf,
           "confidence_band": band_, "method": method, "corpus_ids": sorted(support.get("by_source_family", {})) or None}
    if rec["corpus_ids"] is None:
        rec.pop("corpus_ids")
    if assoc:
        rec["association"] = assoc
    if quant:
        rec["quantiles"] = quant
    return rec


def main() -> None:
    st = LedgerStore()
    src_ids = [s for s in (st.ids.lookup("SRC", "a1:bbcgoodfood:ingredient_mentions"),
                           st.ids.lookup("SRC", "wikibooks:cookbook")) if s]
    ings, proc, tool, pcs, dur, temp, n_by_src = scan(st)
    recs, rows = [], []
    for pred, pc in pcs.items():
        mn, lift, k = PARAMS[pred]
        value_obj = pred in VALUE_OBJ
        method = "SEQUENCE" if pred == "PROC_FOLLOWED_BY" else "CO_OCCURRENCE"
        for e in pc.edges(mn, lift, k):
            sup = {"recipes": e["support"], "mentions": e["mentions"], "subject_recipes": e["subject_recipes"],
                   "object_recipes": e["object_recipes"], "by_source_family": e["by_source"]}
            assoc = {"p_object_given_subject": e["p"], "lift": e["lift"]}
            if e["pmi"] is not None:
                assoc["pmi"] = e["pmi"]
            recs.append(record(st, pred, e["subject"], None if value_obj else e["object"],
                               e["object"] if value_obj else None, sup, e["confidence"], e["band"], method, src_ids,
                               assoc))
    for pred, data, unit_ in (("PROC_TYPICAL_DURATION", dur, "min"), ("PROC_TYPICAL_TEMPERATURE", temp, "degC")):
        for pid, vals in data.items():
            if len(vals) >= 15:
                c, b = quantile_confidence(len(vals))
                recs.append(record(st, pred, pid, None, None, {"recipes": len(vals)}, c, b, "TEXT_CONDITION",
                                   src_ids, quant=quantiles(vals, unit_)))
    for i in ings:
        sup = {"recipes": i.get("corpus_frequency") or 0}
        if i.get("category"):
            fo = (i.get("crosswalks") or {}).get("foodon") or {}
            recs.append(record(st, "ING_HAS_CATEGORY", i["id"], None, i["category"], sup, fo.get("score") or 0.8,
                               "HIGH" if fo.get("status") == "LINKED" else "MEDIUM", "ONTOLOGY", src_ids))
        for par in i.get("parent_ids") or []:
            recs.append(record(st, "ING_PARENT", i["id"], par, None, sup, 0.8, "MEDIUM", "STRUCTURAL", src_ids))
    for p in st.all_latest("PROC"):
        if p["status"] == "ACTIVE":
            recs.append(record(st, "PROC_IN_FAMILY", p["id"], None, p["family"], {"recipes": p.get("corpus_frequency") or 0},
                               0.9, "MEDIUM", "CURATED", src_ids))
    for t in st.all_latest("TOOL"):
        if t["status"] == "ACTIVE":
            recs.append(record(st, "TOOL_HAS_CATEGORY", t["id"], None, t["category"], {"recipes": 0}, 0.9, "MEDIUM",
                               "CURATED", src_ids))
    writes, live = Counter(), set()
    for r in recs:
        writes[st.upsert(r)[0]] += 1
        live.add(r["id"])
        rows.append({"kge_id": r["id"], "predicate": r["predicate"], "subject_id": r["subject_id"],
                     "object": r["object_id"] or r["object_value"], "support": r["support"]["recipes"],
                     "lift": (r.get("association") or {}).get("lift"), "confidence": r["confidence"],
                     "band": r["confidence_band"], "p50": (r.get("quantiles") or {}).get("p50")})
    for old in st.all_latest("KGE"):                      # edges this builder no longer derives: deprecate
        if old["status"] == "ACTIVE" and old["id"] not in live and old["provenance"].get("agent") == AGENT:
            writes["deprecated"] += st.upsert({**old, "status": "DEPRECATED", "notes": "no longer derived"})[0] == "revised"
    report(rows, writes, n_by_src, proc, tool, ings)


def report(rows, writes, n_by_src, proc, tool, ings) -> None:
    df = pd.DataFrame(rows)
    out = ROOT / "registry" / "kg"
    out.mkdir(parents=True, exist_ok=True)
    df.sort_values(["predicate", "subject_id", "confidence"], ascending=[True, True, False]).to_csv(
        out / "kg_edges_v1.csv", index=False)
    name = {**{v: k for k, v in proc.items()}, **{v: k for k, v in tool.items()},
            **{i["id"]: i["canonical_name"] for i in ings}}
    tab = df.groupby("predicate").agg(edges=("kge_id", "size"), high=("band", lambda b: (b == "HIGH").sum()),
                                      medium=("band", lambda b: (b == "MEDIUM").sum()),
                                      median_support=("support", "median")).reset_index()
    ex = lambda p, n=6: "; ".join(  # noqa: E731
        f"{name.get(r.subject_id, r.subject_id)}→{name.get(r.object, r.object)} (n={r.support}, lift={r.lift})"
        for r in df[df.predicate == p].sort_values("support", ascending=False).head(n).itertuples())
    timers = df[df.predicate == "PROC_TYPICAL_DURATION"].sort_values("support", ascending=False).head(10)
    lines = ["# KGE concept edges v1 (X3c, D-011)", "", f"Recipes scanned: {dict(n_by_src)}", "",
             tab.to_markdown(index=False), "", f"Ledger writes: {dict(writes)}", "",
             "Examples:", f"- PROC_USES_TOOL: {ex('PROC_USES_TOOL')}", f"- PROC_FOLLOWED_BY: {ex('PROC_FOLLOWED_BY')}",
             f"- ING_PROCESSED_BY: {ex('ING_PROCESSED_BY')}", f"- ING_CO_OCCURS: {ex('ING_CO_OCCURS')}",
             f"- ING_USED_IN_CUISINE: {ex('ING_USED_IN_CUISINE')}",
             f"- ING_ALTERNATIVE_TO: {ex('ING_ALTERNATIVE_TO')}", f"- ING_PREP_FORM: {ex('ING_PREP_FORM')}",
             f"- PROC_USES_MEDIUM: {ex('PROC_USES_MEDIUM')}", f"- PROC_ENDPOINT_STATE: {ex('PROC_ENDPOINT_STATE', 10)}",
             f"- ING_OFTEN_OPTIONAL: {ex('ING_OFTEN_OPTIONAL')}",
             "- typical durations (median min, n): " + ", ".join(
                 f"{name.get(r.subject_id)} {r.p50} (n={r.support})" for r in timers.itertuples()),
             "", "Statistical edges are corpus associations (recipe text), not chemistry; confidence = 95% Wilson lower "
                 "bound of P(object|subject); durations/temperatures are as written in steps (setpoint vs core unknown)."]
    (ROOT / "reports" / "kg_edges_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:]))


if __name__ == "__main__":
    main()
