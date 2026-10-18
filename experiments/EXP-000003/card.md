# DEL-2 D0–D7 on Phenol-Explorer (log-RF target)

**Hypothesis:** Learned transition models (D3–D7) reduce retention-factor error versus D0 'nothing changes' persistence, and the gain survives cold-start splits (unseen matrix / process / study).

**Command:** `/opt/anaconda3/bin/python tools/run_del2.py --source PHENOL-EXPLORER-3.6 --n-boot 100 --log-target`
**Data:** 3,870 rows (0 censored); matrices 146, process signatures 33, targets 161; seed 7

| split | D0 MAE | best model | best MAE [95% CI] | median AE | beats D0 beyond CI? |
|---|---|---|---|---|---|
| random | 0.8616 | D5_gradient_boosting+log | 0.5664 [0.285, 0.939] | 0.1416 | no |
| pair_holdout | 0.7298 | D0_persistence | 0.7298 [0.43, 0.9535] | 0.3 | no |
| matrix_disjoint | 0.7670 | D7_biased_mf_side_info+log | 0.7383 [0.4648, 0.9422] | 0.3639 | no |
| process_disjoint | 0.3676 | D0_persistence | 0.3676 [0.2211, 0.4289] | 0.22 | no |
| study_disjoint | 0.5577 | D1_global_mean+log | 0.4871 [0.2376, 0.7278] | 0.2058 | no |

**Verdict:** NOT SUPPORTED.

Notes: D6 TabPFN: SKIPPED (not installed; GPU); censored rows trained at lower bound 0.975 (assumption); conformal coverage is empirical (AH4)
