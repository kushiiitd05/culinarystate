# DEL-2 D0–D7 on Phenol-Explorer (raw RF scale)

**Hypothesis:** Learned transition models (D3–D7) reduce retention-factor error versus D0 'nothing changes' persistence, and the gain survives cold-start splits (unseen matrix / process / study).

**Command:** `/opt/anaconda3/bin/python tools/run_del2.py --source PHENOL-EXPLORER-3.6 --n-boot 100`
**Data:** 3,870 rows (0 censored); matrices 146, process signatures 33, targets 161; seed 7

| split | D0 MAE | best model | best MAE [95% CI] | median AE | beats D0 beyond CI? |
|---|---|---|---|---|---|
| random | 0.8616 | D4_nearest_compatible_evidence | 0.7338 [0.436, 1.1012] | 0.1645 | no |
| pair_holdout | 0.7298 | D1_global_mean | 0.7263 [0.4122, 0.9667] | 0.2814 | no |
| matrix_disjoint | 0.7670 | D0_persistence | 0.7670 [0.4163, 1.0564] | 0.38 | no |
| process_disjoint | 0.3676 | D0_persistence | 0.3676 [0.2211, 0.4289] | 0.22 | no |
| study_disjoint | 0.5577 | D0_persistence | 0.5577 [0.3473, 0.7583] | 0.39 | no |

**Verdict:** NOT SUPPORTED.

Notes: D6 TabPFN: SKIPPED (not installed; GPU); censored rows trained at lower bound 0.975 (assumption); conformal coverage is empirical (AH4)

**Caveat:** Raw RF up to ~100 dominates MAE; read with the log-target card.
