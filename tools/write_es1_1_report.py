#!/usr/bin/env python3
"""ES-1.1 audit report (numbers copied from reports/es1/es1_1_evd_export_audit.json)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
a = json.loads((ROOT / "reports/es1/es1_1_evd_export_audit.json").read_text())
m = json.loads((ROOT / "exports/evd/evd_export_v1.manifest.json").read_text())
c = a["checks"]
fmt = lambda d: "; ".join(f"{k} {v:,}" for k, v in d.items())
dup = [x for x in a["duplicate_variable_mappings"] if x["relation"] == "DUPLICATE_SAME_ANALYTE"]
eqc = [x for x in a["duplicate_variable_mappings"] if x["relation"] != "DUPLICATE_SAME_ANALYTE"]
u = a["unknown_counts"]
txt = f"""# ES-1.1 -- EVD export audit (frozen MP-1 contract implemented as a non-destructive export)

**GATE RESULT: {a['gate']}.** Generated from `reports/es1/es1_1_evd_export_audit.json` by `tools/write_es1_1_report.py`. Validator: `tools/validate_evd_export_v1.py` (independent re-derivation). Code: `src/culinarystate/evidence/evd_export.py`, builder `tools/build_evd_export_v1.py`, tests `tests/unit/test_evd_export.py`, schema `registry/schemas/evd_export_v1.schema.json`, mapping `registry/svar_duplicate_mapping_v1.csv`, tables `exports/evd/evd_matrix_table_v1.csv`, `evd_prior_state_table_v1.csv`, manifest `exports/evd/evd_export_v1.manifest.json`. The 37 MB export `exports/evd/evd_export_v1.jsonl` is deterministic, reproducible by the builder and git-ignored; its sha256 is `{a['export_sha256']}`.

## Accounting
- Ledger version lines read: {a['ledger_version_lines']:,}; latest ids: {a['ledger_ids_latest']:,}; **input rows (ACTIVE latest): {a['input_row_count_active']:,}**; **output rows: {a['output_row_count']:,}**; excluded latest ids: {fmt(c['1_every_active_row_accounted']['detail']['excluded_latest_by_status'])} (superseded/deprecated rows, accounted by status).
- Schema validation failures: **{a['validation_failures']}**. Source-lineage hash match: {c['3_source_lineage_and_copied_values']['detail']['lineage_hash_ok']:,} of {a['output_row_count']:,}; copied-value mismatches: {c['3_source_lineage_and_copied_values']['detail']['copied_value_mismatches']}.
- Canonical ledgers (EVD, SVAR, COND, PROC, ING, SRC) sha256 identical before and after the run: **{c['7_canonical_ledgers_unchanged']['pass']}**. Two independent rebuilds are byte-identical to the file: **{c['8_deterministic_rebuild_identical']['pass']}**.

## Separate fields (ruling C1)
- evidence_tier: {fmt(a['evidence_tier_counts'])}
- provenance_class: {fmt(a['provenance_counts'])}  (USDA R6 rows carry `provenance_note = SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE`; the source states many values are imputed from similar foods but does not mark which)
- verification_status: {fmt(a['verification_counts'])}; human-verified rows: 0
- design_strength: {fmt(a['design_strength_counts'])} (copied from the ledger `design`; Phenol-Explorer primary-study design is not recorded in the source rows, so UNKNOWN; nothing was inferred or promoted)
- A synthetic test confirms that HUMAN_VERIFIED does not change an E3 tier or the design field.

## Deterministic derived fields (only where inputs are MEASURED, uncensored, same unit, mathematically defined)
- delta_value (after - before): {a['deterministic_derived_field_counts']['delta_value']:,}
- log_fold_change (ln(after/before), both > 0): {a['deterministic_derived_field_counts']['log_fold_change']:,}
- log_retention_factor (ln of reported MEASURED retention factor, > 0): {a['deterministic_derived_field_counts']['log_retention_factor']:,}  -- kept separate from log_fold_change on purpose (conflict C4): a reported retention factor may include a yield correction or be apparent, so it is not assumed to be a concentration ratio. All three are DERIVED_DETERMINISTIC at field level; 0 violations in independent recomputation (tolerance 1e-12); no derivation from censored values.
- Reasons a derived field is null are recorded per row (`*_reason_if_unknown`): {json.dumps(a['unknown_reasons'])}

## UNKNOWN counts (of {a['output_row_count']:,} rows)
{fmt(u)}.
`lod` and `loq` are null in every row: the source rows contain only GT_CAP upper-cap censoring (USDA R6, Bognar) and no LOD/LOQ values; `lod_loq_status = NOT_REPORTED_BY_SOURCE_ROW`. `prior_state_id` is a hash of the normalised raw descriptor (`PST-...`, vocabulary pending); it is null where the source has no initial_state/prior_processing. `matrix_id` is a hash of the normalised matrix object with a reversible lookup table.

## Duplicate / equivalent-candidate SVAR mapping (reversible; no ID deleted or rewritten)
- {len(dup)} DUPLICATE_SAME_ANALYTE pairs (name rule, measurement-basis equivalence **not verified**, status PROVISIONAL): {', '.join(x['duplicate_id'] + '->' + x['canonical_id'] for x in dup)}.
- {len(eqc)} EQUIVALENT_CANDIDATE_NOT_MERGED entries (e.g. Folate, Vitamin C, Naringenin variants) pending human/analytical check.
- Every export row keeps both `target_state_variable_id` (original) and `canonical_variable_id`; evidence rows on the {len(dup)} duplicate ids: {c['6_duplicate_mapping_reversible']['detail']['evd_rows_on_duplicate_ids']:,}; group counts are additive after mapping: {c['6_duplicate_mapping_reversible']['detail']['group_counts_additive']}.

## Diagnostics (non-gating; reported, not corrected)
- Phenol-Explorer rows with before, after, retention and yield (n = {c['D1_PE_retention≈(after/before)*yield (diagnostic)']['detail']['checked']:,}): {c['D1_PE_retention≈(after/before)*yield (diagnostic)']['detail']['outside_0.02']} rows have reported retention differing from (after/before) x yield by more than 0.02. This supports keeping log_retention separate and is an open data-quality observation, not an export defect.
- percent_change versus (after-before)/before x 100: {c['D2_percent_change≈(after-before)/before*100 (diagnostic)']['detail']['outside_0.05']} of {c['D2_percent_change≈(after-before)/before*100 (diagnostic)']['detail']['checked']:,} outside 0.05.

## Gate conditions
| Condition | Result |
|---|---|
| every source row accounted for | {c['1_every_active_row_accounted']['pass']} |
| no scientific value invented | {c['4_derivations_reproducible_and_no_invention']['pass'] and c['5_unknown_stays_unknown(lod,loq,prior_state)']['pass']} |
| source lineage preserved | {c['3_source_lineage_and_copied_values']['pass']} |
| duplicate mapping reversible | {c['6_duplicate_mapping_reversible']['pass']} |
| deterministic derivations reproducible | {c['4_derivations_reproducible_and_no_invention']['pass'] and c['8_deterministic_rebuild_identical']['pass']} |
| schema validation succeeds | {c['2_schema_validation']['pass']} |
| canonical source rows unchanged | {c['7_canonical_ledgers_unchanged']['pass']} |

Not done by design: no new literature, scraping, downloads, E5 rows, verification, mechanism pilot, simulation, training, Gold edits, or E1-E7 ontology change.
Next if accepted: ES-1.2 (source acquisition manifest and literature/data-source census) -- not started.
"""
(ROOT / "reports/es1/es1_1_audit.md").write_text(txt)
print(len(txt))
