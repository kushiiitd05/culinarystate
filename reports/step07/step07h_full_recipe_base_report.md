# STEP 07H-R -- full recipe-base consolidation, ledger synchronisation, parser freeze

**STEP 08 NOT STARTED.** Recipe text is a procedural observation (`source_plane=RECIPE`, `observation_class=TEXT_STATED`), never a measurement.

## A. Canonical base

- **recipe_base_v1**: 612,782 recipes (`ledgers/recipe_base/recipe_base_v1.parquet`; REC stays immutable, base holds pointers + hashes)
- REC history lines 107,760 = 89,565 unique ids + 18,195 version-2 lines (**the earlier '107,760 recipes' counted history lines**)
- by source family: FOODCOM 522,517, GUTENBERG_SEGMENT 73,955, A1_BBC_GOOD_FOOD 11,934, WIKIBOOKS 3,676, TASTESET 700
- recipe families: 611,700 (REC family_id kept; Food.com/TASTEset singleton identity families -- no algorithm invented)
- tier totals: SOURCE_RAW 600,828, SILVER_AUTO 11,914, GOLD_PENDING_INDEPENDENT_IAA 40
- Gold index rows: 50 -> {'GOLD_PENDING_INDEPENDENT_IAA': 40, 'GOLD_CANDIDATE_SCREENED_NOT_ANNOTATED': 10}
- tiers by source: `{"A1_BBC_GOOD_FOOD": {"GOLD_PENDING_INDEPENDENT_IAA": 20, "SILVER_AUTO": 11914, "SOURCE_RAW": 0}, "FOODCOM": {"GOLD_PENDING_INDEPENDENT_IAA": 20, "SILVER_AUTO": 0, "SOURCE_RAW": 522497}, "GUTENBERG_SEGMENT": {"GOLD_PENDING_INDEPENDENT_IAA": 0, "SILVER_AUTO": 0, "SOURCE_RAW": 73955}, "TASTESET": {"GOLD_PENDING_INDEPENDENT_IAA": 0, "SILVER_AUTO": 0, "SOURCE_RAW": 700}, "WIKIBOOKS": {"GOLD_PENDING_INDEPENDENT_IAA": 0, "SILVER_AUTO": 0, "SOURCE_RAW": 3676}}`
- **bulk recipes were NOT promoted to Gold**: no DEEP_GOLD / GOLD_LIGHT assigned; all existing Gold is AI-drafted + human-reviewed (D-016/D-017) -> GOLD_PENDING_INDEPENDENT_IAA

## B. Ledger synchronisation

Full matrix: `reports/step07/step07h_ledger_sync_matrix.csv` (every designed ledger/registry: before, after, action, reason, plane, owner).

| object | before | after | action |
|---|---|---|---|
| SRC | 609 | 609 | NO_CHANGE_REQUIRED |
| REC | 107760 | 107760 | REINDEXED |
| FAM | 0 | 612782 | REBUILT_DERIVED |
| ING | 5387 | 5387 | VALIDATED_ONLY |
| ALIAS | 4183 | 4183 | VALIDATED_ONLY |
| PROC | 552 | 552 | VALIDATED_ONLY |
| TOOL | 297 | 297 | VALIDATED_ONLY |
| UNIT | 74 | 74 | VALIDATED_ONLY |
| DATASET | 0 | 5 | POPULATED |
| recipe_base_v1 | 0 | 612782 | POPULATED |
| gold_recipe_index_v1 | 0 | 50 | POPULATED |
| recipe_expression_probe_v1 | 0 | 8166098 | POPULATED |
| recipe_condition_mentions_v1 | 0 | 3904986 | POPULATED |
| recipe_ingredient_mentions_v1 | 0 | 4964190 | POPULATED |
| recipe_quantity_mentions_v1 | 0 | 4281956 | POPULATED |
| recipe_process_mentions_v1 | 0 | 12401784 | POPULATED |
| recipe_simulation_readiness_v1 | 0 | 612782 | POPULATED |
| vocab_corpus_frequency_v1 | 0 | 5302 | POPULATED |
| COND | 4746 | 4746 | NO_CHANGE_REQUIRED |
| EVD | 57280 | 57280 | NO_CHANGE_REQUIRED |
| MEAS | 3 | 3 | NO_CHANGE_REQUIRED |
| SVAR | 355 | 355 | NO_CHANGE_REQUIRED |
| STUDY | 125 | 125 | NO_CHANGE_REQUIRED |
| MOL | 1726 | 1726 | NO_CHANGE_REQUIRED |
| IMAP | 31972 | 31972 | NO_CHANGE_REQUIRED |
| KGE | 80607 | 80607 | BLOCKED_FUTURE_STEP |
| SNAP | 347 | 347 | NO_CHANGE_REQUIRED |
| EXP | 8 | 8 | NO_CHANGE_REQUIRED |
| ALLERGEN | 11 | 11 | NO_CHANGE_REQUIRED |
| QNT | 0 | 0 | BLOCKED_FUTURE_STEP |
| POR | 0 | 0 | BLOCKED_FUTURE_STEP |
| INST | 0 | 0 | BLOCKED_FUTURE_STEP |
| ENTITY | 0 | 0 | BLOCKED_FUTURE_STEP |
| EVT | 0 | 0 | BLOCKED_FUTURE_STEP |
| STATE | 0 | 0 | BLOCKED_FUTURE_STEP |
| SPLIT | 0 | 0 | BLOCKED_FUTURE_STEP |
| RXN | 0 | 0 | BLOCKED_FUTURE_STEP |
| WARN | 0 | 0 | BLOCKED_FUTURE_STEP |
| HYP | 0 | 0 | BLOCKED_FUTURE_STEP |
| SIM | 0 | 0 | BLOCKED_FUTURE_STEP |
| KINETIC | 0 | 0 | BLOCKED_FUTURE_STEP |
| LOT/ENT | 0 | 0 | BLOCKED_FUTURE_STEP |
| GRAPH/CLM/REF/RQ/RS/GATE/MODEL/API/ALLOC | 0 | 37 | BLOCKED_FUTURE_STEP |
| data_source_acquisition_manifest | 0 | 64 | NO_CHANGE_REQUIRED |
| recipe_quality_tier_registry_v1 | 0 | 8 | POPULATED |
| recipe_*_surface_forms_v1 (condition/quantity/temporal/process) | 0 | 20000 | POPULATED |

## C. Parser / normalizer

- expressions (final): 8,166,098; condition mentions 3,904,986; ingredient mentions 4,964,190; quantity mentions 4,281,956; process mentions 12,401,784
- first pass vs second pass VALID% by expression family (pass 2 after deterministic-syntax fixes):

| family | pass1 total | pass1 VALID% | pass2 total | pass2 VALID% | pass2 other statuses |
|---|---|---|---|---|---|
| ENDPOINT | 906,295 | 100.0 | 906,295 | 100.0 | {} |
| GAS_MARK | 7,932 | 100.0 | 7,994 | 100.0 | {} |
| GEOMETRY | 125,579 | 85.7 | 125,579 | 86.3 | {'AMBIGUOUS': 17208} |
| MEDIUM | 102,404 | 100.0 | 102,404 | 100.0 | {} |
| POWER | 263 | 39.9 | 263 | 98.1 | {'AMBIGUOUS': 5} |
| PRESSURE | 99 | 0.0 | 99 | 0.0 | {'AMBIGUOUS': 99} |
| QUALITATIVE_HEAT | 192,678 | 100.0 | 192,678 | 100.0 | {} |
| QUANTITY | 4,135,533 | 98.6 | 4,135,533 | 98.6 | {'AMBIGUOUS': 56739} |
| TEMPERATURE | 247,407 | 50.3 | 232,286 | 54.6 | {'AMBIGUOUS': 105423, 'INVALID': 14} |
| TIME | 931,013 | 99.4 | 931,013 | 99.4 | {'AMBIGUOUS': 4972, 'INVALID': 340} |
| TIME_QUALITATIVE | 52,166 | 100.0 | 52,166 | 100.0 | {} |
| TIME_STRUCTURED_FIELD | 1,479,788 | 100.0 | 1,479,788 | 100.0 | {} |

- pass-1 fixes (deterministic syntax only): bare `350°` and `350 degrees` -> `TEMPERATURE_SCALE_NOT_STATED` (was UNIT_MISSING / unparsed); `degrees Fahrenheit/Celsius`; `8″` inch mark; `W/watts`; false temperature `1/2 c.` (a cup) removed; compound `1 hr 30 mins`; `2 1/2`, `1-1/2`, `1/2`, vulgar fractions; calendar-at-ingest guard; U+2044 fraction slash.
- remaining ambiguity is by design: tsp/tbsp/cup etc. (recognised, not converted in the expression ledger; the quantity ledger uses the existing locale-aware grammar), multi-dimension sizes, calendar months/years, temperatures with no stated location/scale, bare psi.

### BBC / A1 dialect findings

```json
{
 "a1_expressions": 209908,
 "by_family": {
  "QUANTITY": 107557,
  "TIME": 32158,
  "ENDPOINT": 27531,
  "TIME_STRUCTURED_FIELD": 11924,
  "TEMPERATURE": 11755,
  "GAS_MARK": 5787,
  "GEOMETRY": 4957,
  "QUALITATIVE_HEAT": 4532,
  "MEDIUM": 1975,
  "TIME_QUALITATIVE": 1715,
  "POWER": 17
 },
 "gas_mark_expressions": 5787,
 "oven_compound_groups": 5726,
 "fan_marked_temperatures": 4536,
 "temperature_location": {
  "SETPOINT": 11363,
  "UNSPECIFIED": 259,
  "MEDIUM": 70,
  "CORE": 63
 },
 "top_temperature_patterns": {
  "#c": 7109,
  "#c fan": 4529,
  "# degrees": 27,
  "#°c": 22,
  "# c": 15,
  "#f": 10,
  "#-#c": 8,
  "# degrees c": 7
 },
 "top_time_patterns": {
  "# mins": 15328,
  "#-# mins": 7797,
  "# min": 1421,
  "# hr": 1213,
  "# hrs": 1191,
  "# minutes": 1156,
  "#-# minutes": 691,
  "# days": 516
 },
 "top_gas_patterns": {
  "gas #": 5625,
  "gas mark #": 60,
  "gas ½": 30,
  "gas ¼": 24,
  "gas #½": 17
 },
 "top_endpoint_openers": {
  "until smooth": 1061,
  "until golden": 754,
  "until golden and": 703,
  "until you have": 628,
  "until tender": 604,
  "until the mixture": 545,
  "until softened": 514,
  "until golden brown": 433
 },
 "time_non_valid": {
  "CALENDAR_DURATION_NOT_CONVERTED": 333,
  "INTERVAL_REVERSED,SLASH_NOTATION_RANGE_OR_ALTERNATIVES": 30,
  "RAW_TEXT_PRESENT_BUT_NOT_PARSED": 20,
  "SLASH_NOTATION_RANGE_OR_ALTERNATIVES": 3
 }
}
```
- gas marks are kept as `GAS_MARK` QUALITATIVE with `UNSUPPORTED_NO_SOURCED_MAPPING`; `180C/160C fan/gas 4` components share a `compound_group_id` and are NOT merged or converted.
- USDA/other unresolved abbreviations (CKD, BKD, BLD, DRND, BKD/SIMMRD, +) remain UNVERIFIED; nothing was learned from recipe co-occurrence.

## D. Gold safety

- Gold links: {'GOLD_PENDING_INDEPENDENT_IAA': 40, 'GOLD_CANDIDATE_SCREENED_NOT_ANNOTATED': 10}
- leakage proxy (exact normalised title, no splits frozen): 7 of 40 Gold recipes have a bulk-corpus title twin
- cross-source same-title groups: 6,249; A1/BBC cross-source groups 1,853; singleton families 610,649; largest [['FAM-G77115_21', 18], ['FAM-G77115_101', 4], ['FAM-WB199312', 4]]
- sealed linker sets (441 / 850) were not read or used; protected Gold labels were not used to tune any rule (parser rules derive from recipe TEXT only).

## E. Simulation readiness (TEXT availability only -- NOT simulation eligibility)

| source | status counts |
|---|---|
| A1_BBC_GOOD_FOOD | {'PARTIAL_CONDITIONS': 6722, 'PROCEDURALLY_RICH': 5208, 'INSUFFICIENT_CONDITIONS': 3, 'QUALITATIVE_ONLY': 1} |
| FOODCOM | {'PARTIAL_CONDITIONS': 430825, 'PROCEDURALLY_RICH': 91030, 'QUALITATIVE_ONLY': 407, 'INSUFFICIENT_CONDITIONS': 253, 'UNKNOWN': 2} |
| GUTENBERG_SEGMENT | {'INSUFFICIENT_CONDITIONS': 36609, 'QUALITATIVE_ONLY': 28429, 'PARTIAL_CONDITIONS': 8717, 'UNKNOWN': 177, 'PROCEDURALLY_RICH': 23} |
| TASTESET | {'UNKNOWN': 700} |
| WIKIBOOKS | {'PARTIAL_CONDITIONS': 1829, 'PROCEDURALLY_RICH': 794, 'QUALITATIVE_ONLY': 710, 'INSUFFICIENT_CONDITIONS': 343} |
| **ALL** | {'PARTIAL_CONDITIONS': 448093, 'PROCEDURALLY_RICH': 97055, 'INSUFFICIENT_CONDITIONS': 37208, 'QUALITATIVE_ONLY': 29547, 'UNKNOWN': 879} |

## F. Tests / gate

```json
{
 "gates": {
  "G1_tests_pass_no_unexplained_failures": true,
  "G2_4414_condition_regression_0_unexplained": true,
  "G3_recipe_base_validators_all_pass": true,
  "G4_scientific_and_vocab_ledgers_byte_identical": true,
  "G5_two_complete_rebuilds_deterministic": true,
  "G6_no_unsupported_abbreviation_promoted": true,
  "G7_no_bulk_gold_promotion": true
 },
 "all_pass": true,
 "test_groups": {
  "condition_unit_schema_golden_bound_trajectory_property_dialect": {
   "passed": 421,
   "returncode": 0
  },
  "recipe_probe": {
   "passed": 7,
   "returncode": 0
  },
  "recipe_base_integrity_gold_silver_family_reference": {
   "passed": 5,
   "returncode": 0
  },
  "step07_other": {
   "passed": 17,
   "returncode": 0
  }
 },
 "determinism": {
  "ran": true,
  "byte_identical_per_artifact": {
   "ledgers/recipe_base/recipe_base_v1.parquet": true,
   "ledgers/recipe_base/recipe_simulation_readiness_v1.parquet": true,
   "ledgers/recipe_semantics/recipe_expression_probe_v1.parquet": true,
   "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet": true,
   "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet": true,
   "ledgers/recipe_semantics/recipe_quantity_mentions_v1.parquet": true,
   "ledgers/recipe_semantics/recipe_process_mentions_v1.parquet": true,
   "registry/recipe_condition_surface_forms_v1.csv": true,
   "registry/recipe_quantity_surface_forms_v1.csv": true,
   "registry/recipe_temporal_surface_forms_v1.csv": true,
   "registry/recipe_process_surface_forms_v1.csv": true
  },
  "all_identical": true
 },
 "regression": {
  "conditions_audited": 4414,
  "evd_references_covered": 17978,
  "fields_compared": 15872,
  "fields_changed": 1110,
  "unexplained_field_changes": 0
 }
}
```

## G. Freeze

```json
{
 "artifact_manifest": {
  "ledgers/recipe_base/recipe_base_v1.parquet": {
   "bytes": 84553667,
   "rows": 612782
  },
  "ledgers/recipe_base/gold_recipe_index_v1.parquet": {
   "bytes": 7689,
   "rows": 50
  },
  "ledgers/recipe_base/recipe_simulation_readiness_v1.parquet": {
   "bytes": 7250470,
   "rows": 612782
  },
  "ledgers/recipe_base/vocab_corpus_frequency_v1.parquet": {
   "bytes": 23760,
   "rows": 5302
  },
  "ledgers/recipe_semantics/recipe_expression_probe_v1.parquet": {
   "bytes": 229431539,
   "rows": 8166098
  },
  "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet": {
   "bytes": 137042383,
   "rows": 3904986
  },
  "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet": {
   "bytes": 71012177,
   "rows": 4964190
  },
  "ledgers/recipe_semantics/recipe_quantity_mentions_v1.parquet": {
   "bytes": 41927180,
   "rows": 4281956
  },
  "ledgers/recipe_semantics/recipe_process_mentions_v1.parquet": {
   "bytes": 104251908,
   "rows": 12401784
  },
  "registry/condition_variable_registry_v1.csv": {
   "bytes": 4147,
   "rows": null
  },
  "registry/condition_variable_bounds_registry_v1.csv": {
   "bytes": 2633,
   "rows": null
  },
  "registry/notation_rule_registry_v1.csv": {
   "bytes": 3457,
   "rows": null
  },
  "registry/source_dialect_mapping_registry_v1.csv": {
   "bytes": 3809,
   "rows": null
  },
  "registry/recipe_location_cues_v1.csv": {
   "bytes": 767,
   "rows": null
  },
  "registry/recipe_quality_tier_registry_v1.csv": {
   "bytes": 2201,
   "rows": null
  },
  "registry/recipe_condition_surface_forms_v1.csv": {
   "bytes": 2988024,
   "rows": null
  },
  "registry/recipe_quantity_surface_forms_v1.csv": {
   "bytes": 104266,
   "rows": null
  },
  "registry/recipe_temporal_surface_forms_v1.csv": {
   "bytes": 90073,
   "rows": null
  },
  "registry/recipe_process_surface_forms_v1.csv": {
   "bytes": 1039738,
   "rows": null
  }
 },
 "frozen": true,
 "freeze_commit": "5476cf35a491c3e2381eaa3c70890f6ad6a9ee94",
 "uncommitted_among_frozen_files": null,
 "condition_normalizer_fingerprint": {
  "normalizer_version": "condition_normalizer@2.0.0-07H",
  "code_sha256": {
   "condition_normalizer.py": "d0ceaa91ac73a7aa748f82127211df7cb6229448ce4925b49b6dbf2419c10168",
   "condition_parser.py": "5bc2e4400c423b8a9c3bec54c6dd2303d9a7d4e96c9418f85cad1b1bca57677b",
   "condition_units.py": "fd3a3f433619d0f853d229b90b976b9cf29e272bce722fa354c07cb0b365abc9",
   "source_dialect.py": "9b750341fa0264ca988a3e50118ac1b3d3302ee22ee85aa2b3533837136fa6f9"
  },
  "schema_sha256": "530bf87498d71ccbb0e2dbf57ec6efdfe996d1f4a85ca9d932ea3f628b0bede4",
  "registry_sha256": {
   "condition_variable_registry_v1.csv": "0c036cce18d8fbe87b6e9b6c76fa756448501a901f1b98eef925b42ccced57ac",
   "condition_variable_bounds_registry_v1.csv": "f1b96e95ee77657b27edda142289ea166ccc8309a97017d1534dd2d5c2adaafa",
   "notation_rule_registry_v1.csv": "6579f5a8d928bb2eb0dcd5f6a8a4389de53c198596210aa91250cd6a6a49f97d",
   "source_dialect_mapping_registry_v1.csv": "41934ee6b92289ece51066c9a890cf0f5dbf9c89060b026304b9b6eceb5c9812",
   "measurement_basis_registry_v1.csv": "b257186948d0a10ebda7bb5de4bf42c686495197648b61dc1641ec6919e81f0b",
   "measurement_location_registry_v1.csv": "a36d6042138ac4b3e7e89c34554563426944ebea8397f34befa0471e685bd84b",
   "measurement_method_registry_v1.csv": "6e75d96a2e000aa4dfc86bc0669a8fba35842a228af8d89cd7074cfbfacceb7d",
   "censoring_registry_v1.csv": "bd3c4808771630efc608813b508816c0b4014001a61b4acb74b
```
