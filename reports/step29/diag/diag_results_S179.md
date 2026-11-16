# 29-diag results (S179). DIAGNOSTIC, BOOTSTRAP_UNVERIFIED, NON_CITABLE, PRIOR_EXPOSURE_REANALYSIS, NO_HUMAN_SIGNOFF_D085

- **Run:** `tools/run_29diag.py`, RUN-S179-DIAG29-001, code `1b7505a`.
- **Reproducibility:** two runs, byte-identical (G15-R PASS).
- **Data:** the frozen 15A-BOOT snapshot. 17,978 ACTIVE EVD rows; 14,423 remain after the 15a.R RESERVED groups are
  removed.
- **Sign-off:** the freeze approval and the prereg lock are **AI-delegated (D-085)**; no human signed.
- **Status:** none of this is a claim; the data were already used by DEL-2 and Step 30. Numbers are MAE on the
  retention factor (censor-aware); full tables are in `diag_results_S179.json`.

## 1. D7 = D1 review (prereg §4 item 2)

- **Phenol-Explorer:** the maximum absolute difference between the D7 and D1 predictions is **0.0** on the random
  split. D7 (biased MF) returns the global mean there, so DEL-2's D7 equalling D1 was a model collapse, not a
  coincidence (NEG-0050).
- **USDA-RETN-R6 and BOGNAR-2002:** D7 differs from D1 (maximum difference 0.65 and 0.28).
- **Shortcut rerun:** removing `basis` leaves D5 unchanged on every family (0.0251 / 0.0499 / 0.5468), so D5 does not
  lean on basis.

## 2. Imputation-duplicate control (§4 item 5)

A duplicate group is rows with the same process, target and retention value on >= 2 matrices, within one family.

| Family | groups | rows in groups | share |
|---|---:|---:|---:|
| BOGNAR-2002 | 748 | 4,916 | **0.949** |
| USDA-RETN-R6 | 750 | 3,314 | **0.587** |
| PHENOL-EXPLORER-3.6 | 138 | 354 | 0.111 |

Most Bognár rows, and over half the USDA rows, repeat one value across matrices. Splits that ignore this leak.
The duplicate-safe S-2 and S-3 reruns are in the JSON (`duplicate_control.mae`). Any held-out reading of USDA or
Bognár must use them.

## 3. D2 (process mean) minus B2 (ingredient mean), paired cluster bootstrap (§4 item 3)

The estimate is the mean loss of D2 minus that of B2, so a positive value means lower loss for B2.

| Family | split | estimate [95 %] | clusters | label |
|---|---|---|---:|---|
| PHENOL-EXPLORER-3.6 | S-3 matrix-disjoint | 0.289 [0.040, 0.658] | 25 | DIAGNOSTIC |
| PHENOL-EXPLORER-3.6 | S-4 process-disjoint | -0.012 [-0.074, 0.043] | 34 | DIAGNOSTIC |
| PHENOL-EXPLORER-3.6 | **S-6 study-disjoint** | 0.099 [-0.045, 0.240] | 20 | DIAGNOSTIC |
| USDA-RETN-R6 | S-3 | 0.013 [0.003, 0.023] | 35 | ONE_LINEAGE_CLUSTER |
| USDA-RETN-R6 | S-4 | 0.022 [0.014, 0.030] | 33 | ONE_LINEAGE_CLUSTER |
| BOGNAR-2002 | S-3 | -0.008 [-0.014, -0.002] | 18 | ONE_LINEAGE_CLUSTER |
| BOGNAR-2002 | S-4 | 0.006 [-0.004, 0.012] | 4 | DIAGNOSTIC_ONLY |

- **Equal terms:** S-3 and S-4 are lopsided by construction, so only S-6 compares the two on equal terms. There the
  interval includes 0: **no direction is shown** between process information and food identity on the one
  study-disjoint split.
- **USDA and Bognár:** these are single lineage clusters (clusters are matrix x process groups), and their rows are
  mostly duplicates (§2). No H2-shaped reading is possible there.

## 4. Splits and rungs

- **S-5 food-group-disjoint:** ran on all three families.
- **S-6 study-disjoint:** NOT POSSIBLE for USDA and Bognár, which are single source clusters.
- **Persistence (D0):** on USDA and Phenol-Explorer, D0 is at least as good as D1 / D2 on several splits; on
  Phenol-Explorer process-disjoint D1 = D2 = D7 (0.371) and D0 is 0.390.
- **Cap sensitivity** (bound 0.95 / 0.975 / 1.0) is in `cap_sensitivity` per family. Differences below 0.025 are not
  interpreted (R6 is rounded to 5 %).

## What this does not support

Any statement that a learned model beats the baselines, any H2 support, or any held-out performance figure for USDA
or Bognár without the duplicate control.
