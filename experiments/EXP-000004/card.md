# DEL-2 D0–D7 on Bognár (2002) retention factors

**Hypothesis:** Learned transition models (D3–D7) reduce retention-factor error versus D0 'nothing changes' persistence, and the gain survives cold-start splits (unseen matrix / process / study).

**Command:** `/opt/anaconda3/bin/python tools/run_del2.py --source BOGNAR-2002 --n-boot 100`
**Data:** 6,594 rows (3,274 censored); matrices 28, process signatures 7, targets 36; seed 7

| split | D0 MAE | best model | best MAE [95% CI] | median AE | beats D0 beyond CI? |
|---|---|---|---|---|---|
| random | 0.0873 | D5_gradient_boosting | 0.0483 [0.0377, 0.0586] | 0.0231 | yes |
| pair_holdout | 0.0892 | D5_gradient_boosting | 0.0443 [0.0354, 0.0524] | 0.0253 | yes |
| matrix_disjoint | 0.0621 | D5_gradient_boosting | 0.0463 [0.0386, 0.0509] | 0.03 | yes |
| process_disjoint | 0.0385 | D5_gradient_boosting | 0.0096 [0.0096, 0.0096] | 0.0033 | n/a (degenerate split, 1 group) |

**Verdict:** SUPPORTED incl. cold-start.

Notes: study_disjoint: NOT POSSIBLE (single source family or one giant component) — not reported; D6 TabPFN: SKIPPED (not installed; GPU); censored rows trained at lower bound 0.975 (assumption); conformal coverage is empirical (AH4)

**Caveat:** Bognár factors are averaged and largely templated across food groups (many identical columns), so matrix-disjoint is easy here; this is NOT evidence of generalisation to new foods.
