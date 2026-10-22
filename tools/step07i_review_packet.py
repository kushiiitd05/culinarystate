#!/usr/bin/env python3
"""STEP 07I part 6: UNLABELED blind near-duplicate calibration packet (~400 pairs, stratified) + sealed key. No labels are filled by the agent.
  -> annotation/duplicate_calibration/duplicate_pairs_v1_{Kush,Parv}.csv (git-ignored: third-party recipe text) and ..._KEY_SEALED.csv"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.recipes import corpus as C  # noqa: E402

OUT = ROOT / "annotation/duplicate_calibration"
SEED = "step07i-dup-calibration-v1"
STRATA = [("S01_very_high", lambda d: d.score >= 0.95, 40), ("S02_high", lambda d: (d.score >= 0.85) & (d.score < 0.95), 50), ("S03_boundary_family_rule", lambda d: d.ingredient_idf.between(0.70, 0.90) & (d.title_token.fillna(0) >= 0.4), 60),
          ("S04_moderate", lambda d: d.score.between(0.60, 0.85) & ~d.family_edge, 40), ("S05_same_title_low_structure", lambda d: (d.title_token >= 0.8) & (d.ingredient_idf.fillna(0) < 0.30), 40),
          ("S06_cross_source", lambda d: d.cross_source_family & (d.score >= 0.70), 40), ("S07_same_source", lambda d: d.same_source & (d.score >= 0.70), 30), ("S08_scaled_variant_hint", lambda d: d.hint.notna(), 30),
          ("S09_high_ingredient_diff_process", lambda d: (d.ingredient_idf >= 0.80) & (d.instruction_shingle.fillna(1) < 0.15), 40), ("S10_high_text_diff_ingredient", lambda d: (d.instruction_shingle >= 0.60) & (d.ingredient_idf.fillna(0) < 0.50), 40),
          ("S11_regional_cultural_hint", lambda d: (d.title_token >= 0.5) & ((d.cuisine_agree == False) | (d.locale_agree == False)), 20)]  # noqa: E712


def main():
    d = pd.read_parquet(ROOT / "ledgers/recipe_identity/candidate_pairs_v1.parquet")
    d = d[d.relation_status == "CANDIDATE_NEAR_DUPLICATE"].copy()
    d["pk"] = [hashlib.sha256((SEED + a + b).encode()).hexdigest() for a, b in zip(d.a_recipe_id, d.b_recipe_id)]
    picked, rows = set(), []
    for name, fn, k in STRATA:
        sub = d[fn(d)]
        sub = sub[~sub.pk.isin(picked)].sort_values("pk")
        take = sub.head(k)
        picked.update(take.pk)
        for _, r in take.iterrows():
            rows.append((name, r, len(sub)))
    ids = {r.a_recipe_id for _, r, _ in rows} | {r.b_recipe_id for _, r, _ in rows}
    txt = {}
    rec = C.rec_latest()
    for it in (C.iter_rec_corpora(rec), C.iter_foodcom(), C.iter_tasteset()):
        for r in it:
            if r["recipe_id"] in ids:
                txt[r["recipe_id"]] = r
    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["pair_id", "a_recipe_id", "a_title", "a_ingredients", "a_steps_excerpt", "b_recipe_id", "b_title", "b_ingredients", "b_steps_excerpt", "label", "reason"]
    short = lambda r: ("; ".join(r["ingredient_lines"][:25])[:900], " ".join(r["steps"])[:1100])
    key, out = [], []
    order = sorted(rows, key=lambda x: hashlib.sha256((SEED + "order" + x[1].pk).encode()).hexdigest())   # strata hidden by shuffling
    for n, (name, r, pool) in enumerate(order, 1):
        A, B = txt.get(r.a_recipe_id), txt.get(r.b_recipe_id)
        if A is None or B is None:
            continue
        ai, asx = short(A)
        bi, bsx = short(B)
        pid = f"DP-{n:04d}"
        out.append({"pair_id": pid, "a_recipe_id": r.a_recipe_id, "a_title": A["title"], "a_ingredients": ai, "a_steps_excerpt": asx, "b_recipe_id": r.b_recipe_id, "b_title": B["title"], "b_ingredients": bi, "b_steps_excerpt": bsx, "label": "", "reason": ""})
        key.append({"pair_id": pid, "stratum": name, "stratum_pool_size": pool, "score": r.score, "family_edge": r.family_edge, "ingredient_idf": r.ingredient_idf, "title_token": r.title_token, "instruction_shingle": r.instruction_shingle, "cross_source": r.cross_source_family, "same_source": r.same_source, "hint": r.hint})
    for who in ("Kush", "Parv"):
        with open(OUT / f"duplicate_pairs_v1_{who}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, cols)
            w.writeheader()
            w.writerows(out)
    pd.DataFrame(key).to_csv(OUT / "duplicate_pairs_v1_KEY_SEALED.csv", index=False)
    (OUT / "LABELS_AND_INSTRUCTIONS.md").write_text("""# Duplicate calibration packet (blind)
Label each pair with exactly one of: SAME_RECIPE_COPY, SAME_RECIPE_MINOR_VARIANT, SAME_DISH_DIFFERENT_RECIPE, RELATED, DISTINCT, UNCERTAIN.
Judge only the texts shown (title, first ingredient lines, first steps). Do not look up the sources; do not look at the other reviewer's file; do not open the KEY_SEALED file.
A false merge is worse than a missed duplicate: when unsure choose UNCERTAIN. Scores/strata are hidden on purpose.
""")
    s = {"pairs": len(out), "by_stratum": dict(pd.DataFrame(key).stratum.value_counts()), "sha256_packet": hashlib.sha256((OUT / "duplicate_pairs_v1_Kush.csv").read_bytes()).hexdigest(), "labels_filled": 0}
    (ROOT / "reports/step07i/duplicate_calibration_packet_manifest.json").write_text(json.dumps(s, indent=1, default=str))
    print(s)


if __name__ == "__main__":
    main()
