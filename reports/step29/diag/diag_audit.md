# 29-diag contract audit

Status: AI_DRAFTED, 2026-11-11. **Every number in this memo carries DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / PRIOR_EXPOSURE_REANALYSIS / COND_UNAUDITED / PROVISIONAL_08A / NO_HUMAN_SIGNOFF_D085.**

Source: `reports/step29/diag/diag_results_S179.json`, RUN-S179-DIAG29-001 (D-085; WORKLOG S191).
This is a read-only transcription/interpretation of committed output, not a new model run or a new gate.
No human skim of this newly separated memo is recorded. Existing combined memo remains unchanged.

## Contract and scope audit

The snapshot id is `15A-BOOT-2026-11-08`. There were 17,978 ACTIVE EVD rows before the seal filter;
3,555 reserved rows were excluded and 14,423 remained. The exclusion arithmetic reconciles.
Freeze and prereg signoff are AI_DELEGATED_D085 (`signoff`), not human signatures.
The runner's persisted `status` remains DRAFT_PENDING_29diag_PREREG and its exclusion status
DRAFT_PENDING_15aR_15b; these stale enum strings are preserved beside the actual signoff fields.
The committed run log and S191 record G15-R: two byte-identical runs. This is an engineering
reproducibility check, not an inference gate.

`result.families` reports source-specific retention subsets (not the entire retained EVD resource):

| Family | Rows in diagnostic | Censored rows |
|---|---:|---:|
| BOGNAR-2002 | 5181 | 2598 |
| PHENOL-EXPLORER-3.6 | 3177 | 0 |
| USDA-RETN-R6 | 5642 | 2181 |

Counts are under `result.families.<family>.rows` and `.censored`; do not equate their sum with
all retained EVD rows, which also include rows outside the retention modelling subset.
The run reports random, pair-holdout, matrix-disjoint, process-disjoint and food-group-disjoint splits.
Study-disjoint is absent for USDA and Bognár, whose current key is a single source group each.
Phenol-Explorer study ids are provisional publication keys, not confirmed experimental boundaries.

The ladder's B2 is the ingredient mean; D2 is the process mean; D3 is a target×process mean shrunk
to the process mean and does not use ingredient identity. Labels follow the frozen preregistration.
The earlier DEL-2 and Step 30 runs already exposed these data. No held-out claim or proposal-H2
conclusion follows, and the failed G08-3 record remains in force.

## Output map and unresolved checks

The four original prereg memo files are `diag_audit.md`, `diag_results.md`,
`cap_artefact_stratified.md`, `d7_vs_d1_review.md`. The adopted companion analyses are separated into
`contrast_d2_vs_b2.md`, `cap_sensitivity.md`, and `duplicate_control.md`.
All tables below are derived from existing JSON only. Human review required by board acceptance
has not occurred in this agent session; no reviewer identity or agreement is invented.
