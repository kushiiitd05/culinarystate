#!/usr/bin/env python3
"""S118 Part I.4: recompute H_STATE evidence-cell support on the Food.com Gold versions (observed, no forecast multiplier, no questions).

  /opt/anaconda3/bin/python tools/hstate_coverage_foodcom.py   # prints + writes reports/gold/foodcom_hstate_coverage.json

Same compatibility rule as tools/build_hstate_r_candidates.py (S114): a recipe-evidence pair = (recipe, ING, PROC) such that, at some
cut, an alive derived entity descends from a base ingredient whose concept maps to that ING and the PROC was applied before the cut,
and the EVD ledger holds a retention cell for (ING, PROC). Compares S117 (v1) with S118 (v1.1). Reads local gold; output is text-free.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.state_graph.engine import Add, replay  # noqa: E402
from culinarystate.state_graph.prefix_state import prefix_state  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

G = ROOT / "annotation" / "gold"


def load_docs(d):
    joint = G / d / "foodcom_v1_1_joint.json"
    if joint.exists():
        return json.loads(joint.read_text())["recipes"]
    return [json.loads(f.read_text()) for f in sorted((G / d / "Kush").glob("*.json"))]


def pairs_for(docs, ing, proc, cells):
    pairs, per_recipe = set(), defaultdict(set)
    for d in docs:
        rid, ev = d["recipe_id"], to_events(d)
        concept = {l["entity"]: l["concept"] for l in d["ingredient_lines"]}
        adds = {e.label for e in ev if isinstance(e, Add)}
        idx = [i for i, e in enumerate(ev) if not isinstance(e, Add)]
        for n in range(1, len(idx)):
            k = idx[n - 1] + 1
            g = replay(ev[:k])
            anc, procs, _, _ = prefix_state(ev, k, concept)
            for ent in [a for a in g.alive() if a not in adds]:
                for b in anc.get(ent, {ent}):
                    iid = ing.get(norm(concept.get(b, "")))
                    for pr in procs.get(ent, set()) | procs.get(b, set()):
                        pid = proc.get(pr)
                        if iid and pid and cells.get((iid, pid)):
                            pairs.add((rid, iid, pid))
                            per_recipe[rid].add((iid, pid))
    return pairs, per_recipe


def main():
    st = LedgerStore()
    ing = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
    pfam = {p["id"]: p.get("family") or p.get("process_family") for p in st.all_latest("PROC")}
    cells = defaultdict(list)
    for e in st.all_latest("EVD"):
        i, p = e["matrix"].get("ingredient_id"), e["process"].get("process_id")
        if e["status"] == "ACTIVE" and (e.get("derived") or {}).get("retention_factor") and i and p:
            cells[(i, p)].append((e["id"], e["source_family_id"]))
    out = {}
    for name, d in (("v1_S117", "foodcom_ai_assisted"), ("v1_1_S118", "foodcom_ai_assisted_v1_1")):
        pairs, per = pairs_for(load_docs(d), ing, proc, cells)
        uniq = {(i, p) for _, i, p in pairs}
        out[name] = {"supported_recipes": len(per), "supported_recipe_evidence_pairs": len(pairs), "unique_ingredient_process_cells": len(uniq),
                     "process_families": sorted({str(pfam.get(p)) for _, p in uniq}), "evidence_source_families": sorted({s for c in uniq for _, s in cells[c]}),
                     "evd_rows_behind_cells": sum(len(cells[c]) for c in uniq),
                     "effective_recipe_clusters": len(per), "per_recipe_pairs": {r: len(v) for r, v in sorted(per.items())}}
    out["reference_S114_pilot20"] = {"supported_recipes": 8, "supported_pairs": 14}
    (ROOT / "reports" / "gold" / "foodcom_hstate_coverage.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "per_recipe_pairs"} for k, v in out.items()}, indent=1))
    print(out["v1_1_S118"]["per_recipe_pairs"])


if __name__ == "__main__":
    main()
