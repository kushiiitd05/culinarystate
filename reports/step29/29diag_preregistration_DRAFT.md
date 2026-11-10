# Step 29-diag: early diagnostic on the bootstrap evidence — pre-registration (DRAFT, UNSIGNED)

Status: **DRAFT_PENDING_SIGNATURE** (Kush). Drafted S173 (2026-11-08) by the coding agent from the Step 29 card
(plan v2 L1256–1300), the TB-V0 contract (`reports/h_state/transition_bootstrap_v0_contract.md`) and the 15.0 rulings
(D-068). It counts as signed only through `reports/step29/29diag_prereg_signature.json` carrying the SHA-256 of this
exact text (`evaluation/freeze_records.py`); any edit after signing voids it.
Amended before signature with the S178 options
(`reports/step29/29diag_preregistration_AMENDMENT_S178_DRAFT.md`) as chosen in D-080 / D-081 / D-082 (ksh and prv, AI under D-071; not a human sitting). Until Kush signs, this file is a dated AI draft.

Note on the snapshot record: `registry/freezes/15A-BOOT-2026-11-08.json` is named `FREEZE_15A_BOOTSTRAP`, but
approving it **does not satisfy Step 15a**: Step 15a has a hard dependency on 08a, whose G08-3 FAILED (D-034). The
approval fixes a snapshot for this diagnostic only.

## 1. What this run is and is not

- **Is:** the plan card's 29-diag. A cap-stratified rerun of the DEL-2 ladder plus an audit against the TB-V0
  contract, on the frozen bootstrap snapshot, to find shortcuts and artefacts before paper-grade Step 29.
- **Is not:** a performance claim, a hypothesis test or a gate. **29-diag has no pass gate.** Its memo may not
  say "supported", "beats" or "validated"; every number carries `DIAGNOSTIC`, `BOOTSTRAP_UNVERIFIED` and
  `NON_CITABLE`.
- **Prior exposure (declared):** DEL-2 (October) already trained and scored on these 17,978 E3 rows, and the S160
  Step 30 exploratory run read them too. Every result is labelled `PRIOR_EXPOSURE_REANALYSIS`.

## 2. Data (frozen before any read)

- Snapshot: `registry/freezes/15A-BOOT-2026-11-08.json`, SHA-256 of EVD, COND, SRC, MEAS, SNAP, STUDY, PROC, ING and
  SVAR and of the 15a.R seal commitment. It is proposed by the agent and counts only once a human has approved it.
  The runner refuses on any hash mismatch.
- RESERVED groups (15a.R seal, D-068) are removed by `DiagContext.filter_dev_rows` before any row is read; the
  sealed list stays private.
- Status per row is never null (value may be UNKNOWN). Censored GT_CAP rows are kept and flagged, not imputed.

## 3. Targets, ladder, splits, metrics (TB-V0, unchanged)

- T1 retention factor (MEASURED rows; GT_CAP censored rows analysed in their own stratum); T2 yield where present.
- Ladder (names as in `transition/baselines.py`): D0 = B-0 persistence; D1 = B-1 global mean; D2 = B-3
  process-conditioned mean (per process signature); D3 = target x process cell mean shrunk to the process mean
  (k_proc 5, k_cell 3) — a B-3 variant, **not** B-2, and it does not read the food; D4 = nearest compatible
  evidence; D5 = DEL-2 HistGB with categorical and mask features; D7 = biased matrix factorisation (for the
  D7-vs-D1 review only). Added before signature: **B2 = TB-V0 B-2 ingredient-conditioned mean**, the mean per
  matrix shrunk to its food-group mean, the food-group mean shrunk to the global mean, both with k = 5, falling back
  to food group, then global, for an unseen matrix. It is a deterministic mean from the TB-V0 contract, written
  because the code lacked it; no learned model family is added.
- Splits (TB-V0 names; runner names in brackets): S-1 random (reference) [random]; S-2 pair holdout
  [pair_holdout]; S-3 matrix-disjoint [matrix_disjoint]; S-4 process-disjoint [process_disjoint]; S-5 food-group
  disjoint [food_group_disjoint, added before signature: grouped by `food_group`]; S-6 study-disjoint
  [study_disjoint; Phenol-Explorer only, NOT POSSIBLE for USDA and Bognar, which are single source clusters].
  Seed 7 (the runner default) and every group key are hashed in the run manifest before scoring.
- Metrics: TB §5 (MAE on retention, paired differences with bootstrap intervals over groups).

## 4. The two diagnostics this run exists for

1. **Cap artefact (`cap_artefact_stratified.md`):** DEL-2 trained censored rows at the bound 0.975. Report every
   rung separately for rows at the cap and below it, and with the cap rows excluded, so it shows whether D5's
   pair-holdout lead comes from the cap.
2. **Shortcut and D7 ≡ D1 review (`d7_vs_d1_review.md`):** rerun with source family and basis removed, as TB §6
   requires. Explain why DEL-2's D7a matched D1 to four decimals on Phenol-Explorer.
3. **Process vs food-identity contrast (`contrast_d2_vs_b2.md`):** per source family, on S-3, S-4 and S-6,
   the paired loss difference D2 (process mean) minus B2 (ingredient mean) on the same test rows, with
   `evaluation/bakeoff.paired_cluster_bootstrap` (margin 0.0, 2,000 resamples, confidence 0.95, seed
   `29diag-contrast-2026-11-10`, weighting CLUSTER). Clusters = `independence_group` where a split's test set has
   >= 2 of them; otherwise (matrix, process) groups, labelled `ONE_LINEAGE_CLUSTER`. Every row reports n_rows and
   n_clusters; with n_clusters < 10 (K_min, PROPOSED) the row is `DIAGNOSTIC_ONLY` and no direction is read from it.
   Stated before any run: the contrast is lopsided by construction. On S-3 every test matrix is unseen, so B2 can
   only use the food-group mean; on S-4 every process is unseen, so D2 can only use the global mean. Each split
   therefore favours one arm; only S-6 (study-disjoint, Phenol-Explorer) compares them on equal terms.
4. **Cap sensitivity (`cap_sensitivity.md`) [REV-A Q18]:** the censored GT_CAP rows (USDA "100", read as >= 0.975)
   are refitted and rescored with the bound set to 0.95, 0.975 and 1.0; every rung's MAE (all, below cap, at cap) is
   reported for each value. R6 values are rounded to the nearest 5 %, so differences below 0.025 are not
   interpreted. The cap is meaningful for true retention only; apparent retention can exceed 1, and R6 does not say
   which a row is (RT-004).
5. **Imputation-duplicate control (`duplicate_control.md`) [REV-A Q19 / N6]:** a duplicate group is >= 2 rows of
   one source family with the same process signature, the same target and the same retention value at the
   reported precision, on >= 2 distinct matrices. Reported: number of groups, rows in groups, share of rows. Then
   S-2 and S-3 (and item 3) are rerun with each duplicate group kept inside one fold (fold units = connected
   components of the split key and the duplicate group), and D2, D3, B2 and D5 MAE are shown both ways.

## 5. Outputs and conduct

`reports/step29/diag/{diag_audit.md, diag_results.md, cap_artefact_stratified.md, d7_vs_d1_review.md}` plus, as
chosen, `{contrast_d2_vs_b2.md, cap_sensitivity.md, duplicate_control.md}` and a manifest (code hashes, snapshot id,
split hashes, the duplicate-group hash). The run is deterministic and repeated twice; the two outputs must match
byte for byte (G15-R). No result changes the TB-V0 contract or any paper-grade Step 29 threshold. Any analysis not
named in this file is `EXPLORATORY_POST_HOC` and is not shown in the talk.

## Signature (human only; D-071)

Kush signs by committing `reports/step29/29diag_prereg_signature.json`:
`{"prereg_sha256": "<sha256 of this file>", "signed_by": "Kush Tokas", "signed_date": "YYYY-MM-DD"}`.
