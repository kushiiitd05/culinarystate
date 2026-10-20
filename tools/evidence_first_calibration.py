#!/usr/bin/env python3
"""S116: how reliable is compiler-proposed evidence-first matching?  Compare (recipe, ingredient x process) cells proposed by
compile_recipe on the RAW text of the 20 Gold-v1.1 recipes against the cells derived from the Gold events (S114).
Local only (Gold text is BBC). Output: reports/h_state/evidence_first_calibration.json. Used to discount forecasts.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import evidence_first_candidates as efc  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

GOLD = ROOT / "annotation" / "gold" / "pilot_20_adjudicated_v1_1"


def main():
    st = LedgerStore()
    ing = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
    cells = defaultdict(list)
    for e in st.all_latest("EVD"):
        i, p = e["matrix"].get("ingredient_id"), e["process"].get("process_id")
        if e["status"] == "ACTIVE" and (e.get("derived") or {}).get("retention_factor") and i and p:
            cells[(i, p)].append(e["id"])
    efc.G.update({"ing": ing, "proc": proc, "cells": cells, "names": set(ing)})
    gold = {(r["recipe_id"], r["ingredient_id"], r["process"]) for r in csv.DictReader((ROOT / "benchmark/h_state/evidence_cut_candidates.csv").open())}
    pred = set()
    for f in sorted(GOLD.glob("*.ADJUDICATED.json")):
        d = json.loads(f.read_text())
        rows = efc._one(("bbc", d["recipe_id"], d["recipe_id"], [l["text"] for l in d["ingredient_lines"]], [s["text"] for s in d["steps"]]))[4]
        pred |= {(d["recipe_id"], r["ingredient_id"], r["process"]) for r in rows}
    tp = len(gold & pred)
    out = {"gold_cells": len(gold), "predicted_cells": len(pred), "true_positive": tp,
           "precision": round(tp / len(pred), 3) if pred else None, "recall": round(tp / len(gold), 3) if gold else None,
           "gold_recipes_with_cell": len({g[0] for g in gold}), "pred_recipes_with_cell": len({p[0] for p in pred}),
           "note": "cell = (recipe, ingredient, process); gold = Gold-v1.1 state-derived (any valid cut); pred = rule compiler on raw text"}
    (ROOT / "reports" / "h_state" / "evidence_first_calibration.json").write_text(json.dumps(out, indent=1))
    print(out)


if __name__ == "__main__":
    main()
