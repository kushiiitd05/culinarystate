#!/usr/bin/env python3
"""DEL-2 source-disjoint check: agreement + transfer between evidence source families (explicit harmonisation).

  /opt/anaconda3/bin/python tools/run_cross_source.py
Writes reports/del2/cross_source_v1.md/json.
"""
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.transition.cross_source import agreement, prepare, prepare_groups  # noqa: E402
from culinarystate.transition.dataset import build_cells  # noqa: E402

st = LedgerStore()
portion = {e["id"]: (e["process"].get("modifiers") or {}).get("portion") for e in st.all_latest("EVD")
           if e["source_family_id"] == "BOGNAR-2002"}
names = {i["id"]: i["canonical_name"] for i in st.all_latest("ING")}
fams = ["USDA-RETN-R6", "BOGNAR-2002", "PHENOL-EXPLORER-3.6"]
prep = {f: prepare(build_cells(st, f).df, portion_a_only=f == "BOGNAR-2002", evd_portion=portion) for f in fams}
grp = {f: prepare_groups(build_cells(st, f).df, portion if f == "BOGNAR-2002" else None) for f in fams[:2]}
res = {}
for a, b in combinations(fams, 2):
    r = agreement(prep[a], prep[b])
    for d in r.get("largest_disagreements", []):
        d["ingredient"] = names.get(d.pop("ingredient_id"))
    res[f"L1 ingredient-level: {a} vs {b}"] = r
r = agreement(grp["USDA-RETN-R6"], grp["BOGNAR-2002"])
for d in r.get("largest_disagreements", []):
    d["ingredient"] = d.pop("ingredient_id")
res["L2 food-group x step-family: USDA-RETN-R6 vs BOGNAR-2002"] = r
out = ROOT / "reports" / "del2"
(out / "cross_source_v1.json").write_text(json.dumps(res, indent=1))
lines = ["# DEL-2 cross-source agreement v1 (source-disjoint, SSOT split 6)", "",
         "Harmonisation: nutrient keys, Bognár portion A only, aligned on (ingredient, first step, nutrient); censored at lower bound.",
         "Phenol-Explorer targets are polyphenols, so it has no nutrient overlap with USDA/Bognár (expected).", ""]
for k, r in res.items():
    lines.append(f"## {k}")
    lines += [f"- {kk}: {vv}" for kk, vv in r.items() if kk != "largest_disagreements"]
    for d in r.get("largest_disagreements", [])[:6]:
        lines.append(f"  - {d['ingredient']} / {d['step']} / {d['nutrient']}: A={d['y_a']} B={d['y_b']}")
    lines.append("")
(out / "cross_source_v1.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
