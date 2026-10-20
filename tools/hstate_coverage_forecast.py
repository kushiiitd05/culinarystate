#!/usr/bin/env python3
"""S116: coverage-lift forecasts for H_STATE-R (A new evidence-first Gold, B new evidence, C hybrid). Deterministic; no system output.

  /opt/anaconda3/bin/python tools/hstate_coverage_forecast.py
A: greedy evidence-first selection of N recipes from the Food.com compiler-proposed candidates (data/interim/evidence_first/foodcom_server_raw.csv):
   marginal gain of a recipe = sum over its (<=3) best cells of 1/(1+times the cell is already covered) + 0.5 new ingredient + 0.5 new process family;
   ties by recipe_id. Families are deduplicated first (one recipe per normalised-title family). Supported items = distinct (recipe, cell) pairs with a
   later event (candidate_cut_count>0), <=3 per recipe (materially different dependencies).
   Conservative = x precision 0.25 (measured on the 20 Gold recipes, tools/evidence_first_calibration.py); optimistic = x1.0 (a human screens candidates
   BEFORE annotation, costing ~N/0.25 screenings).
B: from reports/h_state/hstate_missing_evidence_cells_ranked.csv + missing_cells_gold20_detail.json: top-K targets; supported = distinct (recipe, cell) pairs;
   optimistic = every target finds a verifiable same-ingredient same-process source; conservative = ASSUMED 1/3 do (assumption, not measured).
C: hybrid = A(n) + B(k) from disjoint sources (new recipes vs old recipes), added.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
H = ROOT / "reports" / "h_state"
BASE_PAIRS, BASE_RECIPES = 14, 8                       # frozen S114 baseline
PRECISION = json.loads((H / "evidence_first_calibration.json").read_text())["precision"]
B_CONSERVATIVE_PASS = 1 / 3                            # ASSUMPTION (flagged in the report)


def load_proc_family():
    sys.path.insert(0, str(ROOT / "src"))
    from culinarystate.ledgers.store import LedgerStore
    return {p["id"]: p.get("family") for p in LedgerStore().all_latest("PROC")}


def forecast_a(fam, ns=(10, 20, 30, 40)):
    d = pd.read_csv(ROOT / "data" / "interim" / "evidence_first" / "foodcom_server_raw.csv", dtype=str, usecols=["recipe_id", "recipe_family", "ingredient_id", "process", "matched_evidence_ids", "candidate_cut_count"])
    d = d[d.candidate_cut_count.astype(int) > 0].drop_duplicates(["recipe_id", "ingredient_id", "process"])
    cells_by, fam_of, evd_by = {}, {}, {}
    for rid, f, i, p, e in zip(d.recipe_id, d.recipe_family, d.ingredient_id, d.process, d.matched_evidence_ids):
        cells_by.setdefault(rid, []).append((i, p))
        fam_of[rid] = f
        evd_by[(i, p)] = e
    best = {}                                                                     # one recipe per title family: most distinct cells, then id
    for rid, cs in cells_by.items():
        f = fam_of[rid]
        if f not in best or (len(cs), rid) > (len(cells_by[best[f]]), best[f]):
            best[f] = rid
    cand = sorted(best.values())
    cov, ings, pfams, chosen, picks, out = {}, set(), set(), set(), {}, {}
    for n in range(1, max(ns) + 1):
        top = None
        for rid in cand:
            if rid in chosen:
                continue
            ws = sorted(((1 / (1 + cov.get(c, 0))) + 0.5 * (c[0] not in ings) + 0.5 * (fam.get(c[1]) not in pfams), c) for c in cells_by[rid])[::-1][:3]
            key = (sum(w for w, _ in ws), rid)
            if top is None or key[0] > top[0][0] or (key[0] == top[0][0] and rid < top[0][1]):
                top = (key, rid, [c for _, c in ws])
        _, rid, cells = top
        chosen.add(rid)
        picks[rid] = cells
        for c in cells:
            cov[c] = cov.get(c, 0) + 1
            ings.add(c[0])
            pfams.add(fam.get(c[1]))
        if n in ns:
            sel = [(r, c) for r, cs in picks.items() for c in cs]
            evd = set()
            for _, c in sel:
                evd |= set(evd_by[c].split("|"))
            out[n] = {"candidate_recipe_families_available": len(cand), "selected_recipes": n, "unique_families": len({fam_of[r] for r in picks}),
                      "unique_ingredients": len({c[0] for _, c in sel}), "unique_process_families": len({fam.get(c[1]) for _, c in sel}),
                      "distinct_cells": len({c for _, c in sel}), "distinct_evidence_ids": len(evd), "supported_cuts_pairs_optimistic": len(sel),
                      "supported_conservative": round(len(sel) * PRECISION, 1), "screening_needed_to_reach_optimistic": round(n / PRECISION),
                      "effective_independent_clusters_total": n + BASE_RECIPES}
    return out, len(cand), len(d)


def forecast_b(ks=(5, 10, 20)):
    r = pd.read_csv(H / "hstate_missing_evidence_cells_ranked.csv", dtype=str)
    det = json.loads((H / "missing_cells_gold20_detail.json").read_text())
    out = {}
    for k in ks:
        top = r.head(k)
        recs, cuts, pairs, ing, pr = set(), set(), 0, set(), set()
        for t in top.itertuples():
            d = det[f"{t.ingredient_id}|{t.process_id}"]
            recs |= set(d["recipes"]); cuts |= set(d["cuts"]); pairs += len(d["recipes"]); ing.add(t.ingredient_id); pr.add(t.process_id)
        out[k] = {"new_evidence_cells": k, "gold_recipes_newly_supported": len(recs), "cuts_newly_supported": len(cuts), "new_supported_pairs_optimistic": pairs,
                  "new_supported_pairs_conservative": round(pairs * B_CONSERVATIVE_PASS, 1), "ingredients": len(ing), "processes": len(pr),
                  "evidence_types": top.evidence_type_needed.value_counts().to_dict(), "verification_cost_mix": top.estimated_verification_cost.value_counts().to_dict()}
    return out


def main():
    fam = load_proc_family()
    a, n_fam, n_rows = forecast_a(fam)
    b = forecast_b()
    c = {}
    for na, kb in ((10, 5), (20, 5), (20, 10), (30, 10)):
        A, B = a[na], b[kb]
        c[f"+{na} Gold +{kb} cells"] = {
            "supported_optimistic": BASE_PAIRS + A["supported_cuts_pairs_optimistic"] + B["new_supported_pairs_optimistic"],
            "supported_conservative": round(BASE_PAIRS + A["supported_conservative"] + B["new_supported_pairs_conservative"], 1),
            "effective_clusters": na + BASE_RECIPES + B["gold_recipes_newly_supported"] - 0, "annotation_recipes": na, "evidence_cells_to_curate": kb}
    res = {"baseline_s114": {"supported_pairs": BASE_PAIRS, "recipes": BASE_RECIPES}, "precision_used": PRECISION, "B_conservative_pass_rate_ASSUMED": B_CONSERVATIVE_PASS,
           "foodcom_candidate_families": n_fam, "foodcom_candidate_rows_deduped": n_rows, "A": a, "B": b, "C": c}
    (H / "h_state_coverage_lift_forecast.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
