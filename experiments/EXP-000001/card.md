# DEL-2 D0–D7 on USDA retention factors (R6)

**Hypothesis:** Learned transition models (D3–D7) reduce retention-factor error versus D0 'nothing changes' persistence, and the gain survives cold-start splits (unseen matrix / process / study).

**Command:** `/opt/anaconda3/bin/python tools/run_del2.py --source USDA-RETN-R6 --n-boot 100`
**Data:** 6,994 rows (2,620 censored); matrices 38, process signatures 77, targets 26; seed 7

| split | D0 MAE | best model | best MAE [95% CI] | median AE | beats D0 beyond CI? |
|---|---|---|---|---|---|
| random | 0.1205 | D5_gradient_boosting | 0.0251 [0.0198, 0.0292] | 0.0108 | yes |
| pair_holdout | 0.1093 | D5_gradient_boosting | 0.0390 [0.0296, 0.0518] | 0.0158 | yes |
| matrix_disjoint | 0.0590 | D4_nearest_compatible_evidence | 0.0567 [0.0344, 0.0872] | 0.0288 | no |
| process_disjoint | 0.0728 | D5_gradient_boosting | 0.0672 [0.034, 0.0853] | 0.0315 | no |

**Verdict:** SUPPORTED on random split only; NOT supported under cold-start.

Notes: study_disjoint: NOT POSSIBLE (single source family or one giant component) — not reported; D6 TabPFN: SKIPPED (not installed; GPU); censored rows trained at lower bound 0.975 (assumption); conformal coverage is empirical (AH4)

**Caveat:** USDA is a single source (study_disjoint impossible); 100 reported as censored ≥ 0.975.
