#!/usr/bin/env python3
"""S116: turn the raw scan outputs into the committed deliverables.
 reports/h_state/evidence_first_recipe_candidates.csv        local pools (BBC text-free, Wikibooks CC BY-SA)
 reports/h_state/evidence_first_foodcom_candidates.csv       Food.com: top 25 family-deduplicated rows per evidence cell, TEXT-FREE (licence authority unverified)
 reports/h_state/evidence_first_foodcom_strata.csv           candidate counts per (ingredient, process) stratum
Full Food.com rows with instruction spans stay in data/interim/evidence_first/ (git-ignored).
"""
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "reports" / "h_state"
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

st = LedgerStore()
pname = {p["id"]: (p["canonical_name"], p.get("family")) for p in st.all_latest("PROC")}
iname = {i["id"]: i["canonical_name"] for i in st.all_latest("ING")}


def enrich(d, source, provenance):
    d = d.copy()
    d["source"] = source
    d["ingredient"] = d.ingredient_id.map(iname)
    d["process_id"] = d.process
    d["process"] = d.process_id.map(lambda p: pname[p][0])
    d["process_family"] = d.process_id.map(lambda p: pname[p][1])
    d["evidence_ids"] = d.matched_evidence_ids
    d["provenance"] = provenance
    return d


COLS = ["recipe_id", "recipe_name", "source", "ingredient_id", "ingredient", "process_id", "process", "process_family", "instruction_span", "step_index",
        "evidence_ids", "evidence_tier", "conditions_available", "candidate_cut_count", "recipe_family", "duplicate_family", "selection_score", "licence", "provenance"]


def main():
    loc = pd.concat([enrich(pd.read_csv(H / f"evidence_first_recipe_candidates_{t}.csv", dtype=str), t, f"tools/evidence_first_candidates.py rule-compiler match, pool={t}")
                     for t in ("bbc", "wikibooks")])
    loc[COLS].to_csv(H / "evidence_first_recipe_candidates.csv", index=False)
    raw = H / "evidence_first_recipe_candidates_foodcom_server.csv" if (H / "evidence_first_recipe_candidates_foodcom_server.csv").exists() else ROOT / "data" / "interim" / "evidence_first" / "foodcom_server_raw.csv"
    full = enrich(pd.read_csv(raw, dtype=str), "foodcom", "Kaggle irkaal CC0-declared; hash-ordered 150k prefilter-survivor sample; compiler-proposed (precision ~0.25 on Gold)")
    out = ROOT / "data" / "interim" / "evidence_first"
    out.mkdir(parents=True, exist_ok=True)
    full[COLS].to_csv(out / "foodcom_full_with_spans.csv", index=False)
    full["selection_score"] = full.selection_score.astype(float)
    ded = full.sort_values(["selection_score", "recipe_id"], ascending=[False, True]).drop_duplicates(["recipe_family", "ingredient_id", "process_id"])
    top = ded.groupby(["ingredient_id", "process_id"], group_keys=False).head(25).copy()
    top["instruction_span"] = ""
    top["recipe_name"] = top.recipe_name.str[:80]
    top[COLS].to_csv(H / "evidence_first_foodcom_candidates.csv", index=False)
    strata = ded.groupby(["ingredient", "process", "process_family"]).agg(families=("recipe_family", "nunique"), with_time_or_temp=("conditions_available", lambda s: int(s.fillna("").ne("").sum()))).reset_index().sort_values("families", ascending=False)
    strata.to_csv(H / "evidence_first_foodcom_strata.csv", index=False)
    if raw.parent == H:
        shutil.move(str(raw), str(out / "foodcom_server_raw.csv"))
    print(len(loc), len(top), len(strata))
    print(strata.head(12).to_string(index=False))
    print(strata.groupby("process_family").families.sum().sort_values(ascending=False).to_dict())


if __name__ == "__main__":
    main()
