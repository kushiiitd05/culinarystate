# Step 07.A packet v4: adjudication and outcome (2026-10-27)

## Adjudication of the five disputed cells
Cells: CA-016 (temperature_value), CA-037, CA-046, CA-047, CA-054 (duration). Reviewer codes: Kush `SHOULD_BE_AMBIGUOUS`, Parv `CORRECT`. Outcome: Kush's code adopted for all five (`SHOULD_BE_AMBIGUOUS`). Basis: Kush's decision; Parv reportedly said "go with Kush's" (relayed by Kush, 2026-10-27; NOT seen as a message by Claude, UNVERIFIED, Parv's own confirmation still needed). Working sheet (local, untracked): `annotation/condition_audit/adjudication_sheet_v4_5rows.csv`.
The five critical fields flagged for prevalence (temperature_location, pressure, basis, retention_type, censoring) have 0 disagreeing cells between the two reviewers, so there was nothing to adjudicate in them beyond recording that all 100 cells agree.

## Outcome under the signed gate (not loosened; D-027 R-06, R-20)
- Pooled kappa on the ORIGINAL labels stays 0.0 (THR-07A-06 discharge rule: kappa is not recomputed after adjudication). Gate requires >= 0.80 and no systematic critical-field failure: **the statistical gate is NOT met** (kappa paradox: one reviewer's codes have no variation). Raw agreement 0.9944.
- Honest label: `FAIL_REVIEWER_DISAGREEMENT` on the registered statistic, with 5 of 100 conditions disputed and adjudicated in Kush's favour. This is not a `PASS`, so the hard gates that need a valid 07.A (Steps 15, 23, 26d/27, 29-33; D-027 R-05) stay CLOSED. Step 08 is unaffected (soft dependency).
- Any different statistic (for example a prevalence-robust one) would need a NEW pre-registered gate; it cannot replace the signed one after seeing results.
## Process deviations that the report must state
1. Amendment v4.1 signed after both reviewers had returned labels.
2. Kush's first recorded hash was of the blank packet, not the returned file.
3. Parv's first file (`.txt`) used non-packet codes; his resubmission changed CA-037 from `INCORRECT` to `CORRECT` after the tool listed that row as invalid input.
4. Parv's `overall_judgement` was mapped CORRECT->ACCEPT in a derived copy (rule written before computing; 0/100 rows contradicted his field codes).
5. Parv's reported signature of the amendment and his "go with Kush's" are relayed statements.
