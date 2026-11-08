# Step 29-diag: early diagnostic on the bootstrap evidence — pre-registration (DRAFT, UNSIGNED)

Status: **DRAFT_PENDING_SIGNATURE** (Kush). Drafted S173 (2026-11-08) by the coding agent from the Step 29 card
(plan v2 L1256–1300), the TB-V0 contract (`reports/h_state/transition_bootstrap_v0_contract.md`) and the 15.0 rulings
(D-068). It counts as signed only through `reports/step29/29diag_prereg_signature.json` carrying the SHA-256 of this
exact text (`evaluation/freeze_records.py`); any edit after signing voids it.

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
- Ladder: D0 = B-0 persistence, D1 = B-1 global mean, D2 = B-3 process-conditioned mean, D3 = B-2
  ingredient-conditioned mean with food-group shrinkage, D5 = DEL-2 HistGB with categorical and mask features. No
  new model family.
- Splits: S-1 random (reference), S-2 pair holdout, S-3 matrix-disjoint, S-4 process-disjoint, S-5 food-group
  disjoint, all grouped by `independence_group`. Seeds and group keys are hashed in the run manifest before
  scoring.
- Metrics: TB §5 (MAE on retention, paired differences with bootstrap intervals over groups).

## 4. The two diagnostics this run exists for

1. **Cap artefact (`cap_artefact_stratified.md`):** DEL-2 trained censored rows at the bound 0.975. Report every
   rung separately for rows at the cap and below it, and with the cap rows excluded, so it shows whether D5's
   pair-holdout lead comes from the cap.
2. **Shortcut and D7 ≡ D1 review (`d7_vs_d1_review.md`):** rerun with source family and basis removed, as TB §6
   requires. Explain why DEL-2's D7a matched D1 to four decimals on Phenol-Explorer.

## 5. Outputs and conduct

`reports/step29/diag/{diag_audit.md, diag_results.md, cap_artefact_stratified.md, d7_vs_d1_review.md}` plus a
manifest (code hashes, snapshot id, split hashes). The run is deterministic and repeated twice; the two outputs must
match byte for byte (G15-R). No result changes the TB-V0 contract or any paper-grade Step 29 threshold.

## Signature (human only; D-071)

Kush signs by committing `reports/step29/29diag_prereg_signature.json`:
`{"prereg_sha256": "<sha256 of this file>", "signed_by": "Kush Tokas", "signed_date": "YYYY-MM-DD"}`.
