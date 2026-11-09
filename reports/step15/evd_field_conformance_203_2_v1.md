# EVD rows vs the SSOT 203.2 process-event schema: field-by-field conformance (S178, T2-C01-R1)

Status: AI_DRAFTED / PROPOSED, **not reviewed** (the board asks Kush to review). Counts only, no recipe or paper text. `tools/s178_evd_conformance.py` (s178-evd-conformance-0.1.0-draft); deterministic. Every row of this table sums to **17,978** = the export v1 row count (asserted).

Source families: {'BOGNAR-2002': 7090, 'PHENOL-EXPLORER-3.6': 3870, 'USDA-RETN-R6': 7018}. All rows are tier E3, UNVERIFIED or AI_PRECHECKED, COND_UNAUDITED (07.A condition-audit gate not passed).

## What the D1 claim can say

- The 203.2 minimum schema has 45 lines, 55 fields once the value / range / type lines are split.
- **Carried with a value on every row (10):** event_id, target_type, target_variable, censor_flag, source_id, evidence_tier, verification_status, extraction_method, explicit_or_inferred, dataset_version.
- **Populated on some rows only (19):** ingredient_id, ingredient_state_in, process_leaf, process_family, T_value, T_lo, T_hi, T_type, t_value, t_lo, t_hi, medium, pressure_value, target_value, target_lo, unit, direction_label, study_id, doi_or_citation.
- **In the schema but never populated (18):** tool, geometry, moisture_value, moisture_range, water_activity_value, water_activity_range, pH_value, pH_range, pH_type, pressure_range, oxygen_value, oxygen_category, mixing, target_compound, target_hi, LOD, verified_by, notes. No row carries a value for these (UNKNOWN, or NOT_APPLICABLE where the form makes it moot).
- **No field exists (8):** ingredient_state_out, t_type, moisture_type, water_activity_type, pressure_type, ordinal_band, platform, split_id. (split_id is absent from export v1 only; export v2 adds split_group_id on every row, a SCRATCH_PROVISIONAL assignment, see below.)
- Other: none.

## Table

Statuses: PRESENT = value stated; CENSORED_BOUND_ONLY = only a one-sided bound; UNKNOWN = explicit UNKNOWN/null (never 0, never imputed); NOT_APPLICABLE = does not apply by form; ABSENT = no such field in the schemas or export. Carrier: X export v1 column, XC export v1 plus COND join, C COND record only (v1 keeps the completeness mask), L EVD ledger only, J joined ledger, V2 export v2 column, - none.

| field | carrier | match | PRESENT | CENSORED_BOUND_ONLY | UNKNOWN | NOT_APPLICABLE | ABSENT |
|---|---|---|---:|---:|---:|---:|---:|
| event_id | X | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| ingredient_id | X | EXACT | 11,569 | 0 | 6,409 | 0 | 0 |
| ingredient_state_in | XC | PARTIAL | 12,442 | 0 | 5,536 | 0 | 0 |
| ingredient_state_out | - | NONE | 0 | 0 | 0 | 0 | 17,978 |
| process_leaf | X | EXACT | 17,821 | 0 | 157 | 0 | 0 |
| process_family | XC | EXACT | 17,821 | 0 | 157 | 0 | 0 |
| T_value | C | EXACT | 2,430 | 3,369 | 11,963 | 216 | 0 |
| T_lo | C | EXACT | 216 | 0 | 11,963 | 5,799 | 0 |
| T_hi | C | EXACT | 216 | 0 | 11,963 | 5,799 | 0 |
| T_type | C | EXACT | 3,843 | 0 | 14,135 | 0 | 0 |
| t_value | C | EXACT | 2,607 | 0 | 14,895 | 476 | 0 |
| t_lo | C | EXACT | 476 | 0 | 14,895 | 2,607 | 0 |
| t_hi | C | EXACT | 476 | 0 | 14,895 | 2,607 | 0 |
| t_type | - | NONE | 0 | 0 | 0 | 0 | 17,978 |
| medium | XC | EXACT | 4,416 | 0 | 13,562 | 0 | 0 |
| tool | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| geometry | C | PARTIAL | 0 | 0 | 17,978 | 0 | 0 |
| moisture_value | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| moisture_range | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| moisture_type | - | NONE | 0 | 0 | 0 | 0 | 17,978 |
| water_activity_value | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| water_activity_range | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| water_activity_type | - | NONE | 0 | 0 | 0 | 0 | 17,978 |
| pH_value | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| pH_range | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| pH_type | C | PARTIAL | 0 | 0 | 17,978 | 0 | 0 |
| pressure_value | C | EXACT | 129 | 0 | 10,831 | 7,018 | 0 |
| pressure_range | C | EXACT | 0 | 0 | 10,831 | 7,147 | 0 |
| pressure_type | - | NONE | 0 | 0 | 0 | 0 | 17,978 |
| oxygen_value | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| oxygen_category | C | PARTIAL | 0 | 0 | 17,978 | 0 | 0 |
| mixing | C | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| target_type | J | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| target_variable | X | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| target_compound | L | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| target_value | X | EXACT | 12,060 | 5,894 | 24 | 0 | 0 |
| target_lo | X | PARTIAL | 0 | 5,894 | 24 | 12,060 | 0 |
| target_hi | X | PARTIAL | 0 | 0 | 24 | 17,954 | 0 |
| unit | X | EXACT | 17,954 | 0 | 24 | 0 | 0 |
| direction_label | X | EXACT | 12,060 | 0 | 5,918 | 0 | 0 |
| ordinal_band | - | NONE | 0 | 0 | 0 | 0 | 17,978 |
| censor_flag | X | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| LOD | X | PARTIAL | 0 | 0 | 17,978 | 0 | 0 |
| platform | - | NONE | 0 | 0 | 0 | 0 | 17,978 |
| study_id | X | EXACT | 3,870 | 0 | 14,108 | 0 | 0 |
| source_id | X | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| doi_or_citation | J | PARTIAL | 3,678 | 0 | 14,300 | 0 | 0 |
| evidence_tier | X | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| verified_by | L | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| verification_status | X | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| extraction_method | L | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| explicit_or_inferred | X | EXACT | 17,978 | 0 | 0 | 0 | 0 |
| notes | L | EXACT | 0 | 0 | 17,978 | 0 | 0 |
| dataset_version | X | PROXY | 17,978 | 0 | 0 | 0 | 0 |
| split_id | V2 | PROXY | 0 | 0 | 0 | 0 | 17,978 |

Notes per field, per-source-family PRESENT counts and the detail codes are in the CSV and JSON next to this file.

## Export v2 (not part of v1; for the split_id and study_id lines)

- split_group_id on 17,978 of 17,978 rows (127 distinct groups); assignment status {'SCRATCH_PROVISIONAL': 17978}.
- study_id: v1 `study_ids` is filled on 3,870 rows, v2 `study_id` on 3,678 rows (the other 192 Phenol-Explorer rows have no resolvable publication); lineage study_id status {'NOT_IDENTIFIABLE': 14300, 'PRESENT': 3678}; independence resolution {'SOURCE_FAMILY_ONLY': 14108, 'PUBLICATION_ONLY': 3678, 'UNKNOWN': 192}.

## Findings that change other documents

1. COND has a `water_activity` field (and `ph_initial`, `ph_final`, `moisture`, `oxygen`, `agitation`, `tool_ids`, `geometry`); none is populated on any ACTIVE row. The dataset card's wording `NOT_IN_COND_SCHEMA` for water activity is true only of the completeness mask, not of the COND schema.
2. The completeness mask labels a one-sided stated temperature (for example "above 75 C", GT_STATED) as RANGE, so the card's temperature `RANGE 3,585` mixes true two-sided ranges with one-sided bounds. In the COND temperature entries the split is shown by the T_value row (CENSORED_BOUND_ONLY) against T_lo / T_hi (PRESENT).
3. `doi_or_citation` is exact only for the Phenol-Explorer publications (DOI); USDA and Bognar rows cite one database record each.
