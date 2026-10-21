# ES-1.1 -- EVD export audit (frozen MP-1 contract implemented as a non-destructive export)

**GATE RESULT: PASS.** Generated from `reports/es1/es1_1_evd_export_audit.json` by `tools/write_es1_1_report.py`. Validator: `tools/validate_evd_export_v1.py` (independent re-derivation). Code: `src/culinarystate/evidence/evd_export.py`, builder `tools/build_evd_export_v1.py`, tests `tests/unit/test_evd_export.py`, schema `registry/schemas/evd_export_v1.schema.json`, mapping `registry/svar_duplicate_mapping_v1.csv`, tables `exports/evd/evd_matrix_table_v1.csv`, `evd_prior_state_table_v1.csv`, manifest `exports/evd/evd_export_v1.manifest.json`. The 37 MB export `exports/evd/evd_export_v1.jsonl` is deterministic, reproducible by the builder and git-ignored; its sha256 is `e61d7db4dc709ff3a4cb95ec6889a63d491e7f10d30222b421761f428aedd457`.

## Accounting
- Ledger version lines read: 57,280; latest ids: 18,156; **input rows (ACTIVE latest): 17,978**; **output rows: 17,978**; excluded latest ids: DEPRECATED 178 (superseded/deprecated rows, accounted by status).
- Schema validation failures: **0**. Source-lineage hash match: 17,978 of 17,978; copied-value mismatches: 0.
- Canonical ledgers (EVD, SVAR, COND, PROC, ING, SRC) sha256 identical before and after the run: **True**. Two independent rebuilds are byte-identical to the file: **True**.

## Separate fields (ruling C1)
- evidence_tier: E3 17,978
- provenance_class: EXPLICIT_SOURCE 17,978  (USDA R6 rows carry `provenance_note = SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE`; the source states many values are imputed from similar foods but does not mark which)
- verification_status: UNVERIFIED 14,108; AI_PRECHECKED 3,870; human-verified rows: 0
- design_strength: DATABASE_AGGREGATE 14,108; UNKNOWN 3,870 (copied from the ledger `design`; Phenol-Explorer primary-study design is not recorded in the source rows, so UNKNOWN; nothing was inferred or promoted)
- A synthetic test confirms that HUMAN_VERIFIED does not change an E3 tier or the design field.

## Deterministic derived fields (only where inputs are MEASURED, uncensored, same unit, mathematically defined)
- delta_value (after - before): 3,870
- log_fold_change (ln(after/before), both > 0): 3,787
- log_retention_factor (ln of reported MEASURED retention factor, > 0): 11,503  -- kept separate from log_fold_change on purpose (conflict C4): a reported retention factor may include a yield correction or be apparent, so it is not assumed to be a concentration ratio. All three are DERIVED_DETERMINISTIC at field level; 0 violations in independent recomputation (tolerance 1e-12); no derivation from censored values.
- Reasons a derived field is null are recorded per row (`*_reason_if_unknown`): {"delta_reason_if_unknown": {"inputs_not_measured_or_censored": 14108}, "log_fold_change_reason_if_unknown": {"inputs_not_measured_or_censored": 14108, "non_positive_value": 83}, "log_retention_reason_if_unknown": {"retention_not_measured_or_censored": 6414, "non_positive_value": 61}}

## UNKNOWN counts (of 17,978 rows)
prior_state_id 5,536; ingredient_id 6,409; process_id 157; measurement_id 3,870; before_value 14,108; after_value 14,108; delta_value 14,108; log_fold_change 14,191; log_retention_factor 6,475; retention_fraction 6,414; yield_fraction 13,612; lod 17,978; loq 17,978; direction_UNKNOWN 5,918; condition_temperature_UNKNOWN 11,963; condition_duration_UNKNOWN 14,895; condition_moisture_UNKNOWN 17,978; condition_ph_UNKNOWN 17,978.
`lod` and `loq` are null in every row: the source rows contain only GT_CAP upper-cap censoring (USDA R6, Bognar) and no LOD/LOQ values; `lod_loq_status = NOT_REPORTED_BY_SOURCE_ROW`. `prior_state_id` is a hash of the normalised raw descriptor (`PST-...`, vocabulary pending); it is null where the source has no initial_state/prior_processing. `matrix_id` is a hash of the normalised matrix object with a reversible lookup table.

## Duplicate / equivalent-candidate SVAR mapping (reversible; no ID deleted or rewritten)
- 11 DUPLICATE_SAME_ANALYTE pairs (name rule, measurement-basis equivalence **not verified**, status PROVISIONAL): SVAR-000193->SVAR-000006, SVAR-000194->SVAR-000005, SVAR-000195->SVAR-000001, SVAR-000196->SVAR-000003, SVAR-000197->SVAR-000004, SVAR-000198->SVAR-000002, SVAR-000199->SVAR-000008, SVAR-000200->SVAR-000007, SVAR-000209->SVAR-000012, SVAR-000210->SVAR-000013, SVAR-000211->SVAR-000018.
- 7 EQUIVALENT_CANDIDATE_NOT_MERGED entries (e.g. Folate, Vitamin C, Naringenin variants) pending human/analytical check.
- Every export row keeps both `target_state_variable_id` (original) and `canonical_variable_id`; evidence rows on the 11 duplicate ids: 2,048; group counts are additive after mapping: True.

## Diagnostics (non-gating; reported, not corrected)
- Phenol-Explorer rows with before, after, retention and yield (n = 3,859): 278 rows have reported retention differing from (after/before) x yield by more than 0.02. This supports keeping log_retention separate and is an open data-quality observation, not an export defect.
- percent_change versus (after-before)/before x 100: 0 of 3,859 outside 0.05.

## Gate conditions
| Condition | Result |
|---|---|
| every source row accounted for | True |
| no scientific value invented | True |
| source lineage preserved | True |
| duplicate mapping reversible | True |
| deterministic derivations reproducible | True |
| schema validation succeeds | True |
| canonical source rows unchanged | True |

Not done by design: no new literature, scraping, downloads, E5 rows, verification, mechanism pilot, simulation, training, Gold edits, or E1-E7 ontology change.
Next if accepted: ES-1.2 (source acquisition manifest and literature/data-source census) -- not started.
