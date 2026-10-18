# Ledger EDA summary (2026-10-18T06:11:31+00:00)

| Ledger | records | versions | verification |
|---|---|---|---|
| ALIAS | 2,031 | 2,031 | {'UNVERIFIED': 2031} |
| COND | 270 | 270 | {'UNVERIFIED': 270} |
| EVD | 7,018 | 7,018 | {'UNVERIFIED': 7018} |
| ING | 2,009 | 2,009 | {'UNVERIFIED': 2009} |
| MEAS | 1 | 1 | {'UNVERIFIED': 1} |
| PROC | 148 | 160 | {'UNVERIFIED': 148} |
| SNAP | 2 | 2 | {'UNVERIFIED': 2} |
| SRC | 2 | 2 | {'UNVERIFIED': 2} |
| SVAR | 26 | 26 | {'UNVERIFIED': 26} |

## Evidence

- **rows**: 7018
- **tier**: {'E3': 7018}
- **origin_type**: {'DATABASE_AGGREGATE': 7018}
- **source_family**: {'USDA-RETN-R6': 7018}
- **study_lineage**: {'NOT_IDENTIFIABLE': 7018}
- **independent_groups**: 1
- **censored_rows**: 2620
- **retention_factor_status**: {'CENSORED': 2620, 'MEASURED': 4374, 'UNKNOWN': 24}
- **direction**: {'UNKNOWN': 2644, 'DECREASE': 4374}
- **target_basis**: {'RETENTION_TR_OR_AR': 7018}
- **ingredient_id_linked**: 0.0
- **process_id_linked**: 0.0
- **rows_with_temperature**: 0
- **unique_matrices**: 38
- **unique_step_sequences**: 42
- **unique_targets**: 26
- **unique_cells**: 7018
- **matrix_process_density**: 0.1071
- **matrix_long_tail**: {'matrices_with_1_row': 0, 'median_rows_per_matrix': 130}
- **process_steps_top**: [('simmer', 1534), ('boil', 1144), ('bake', 832), ('fry', 780), ('reheat', 727), ('drain', 598), ('broil', 546), ('brown', 520), ('cook', 312), ('roast', 208), ('saute', 182), ('stir', 181), ('braise', 156), ('bake|simmer', 155), ('steam', 130)]
- **replicate_rows_same_cell_same_group**: 0
- **conflict_candidates**: 0

## Ingredients

- **concepts**: 2009
- **active**: 2009
- **ambiguity**: {'LOW': 1994, 'HIGH': 15}
- **with_parent**: 325
- **scientific_identity**: {'UNKNOWN': 2009}
- **crosswalks**: {'fdc': {'UNRESOLVED_EXTERNAL': 2009}, 'flavordb': {'UNRESOLVED_EXTERNAL': 2009}, 'foodon': {'UNRESOLVED_EXTERNAL': 2009}, 'recipedb': {'UNRESOLVED_EXTERNAL': 2009}}
- **frequency_share_top10pct**: 0.7338
- **aliases**: 2031

## Processes

- **processes**: 148
- **family**: {'DRY_HEAT': 8, 'HEAT_GENERAL': 6, 'FAT_HEAT': 10, 'WET_HEAT': 12, 'HEAT_CONTROL': 2, 'COOLING': 4, 'RESTING': 1, 'MECHANICAL_CUT': 22, 'MECHANICAL_MIX': 14, 'SEPARATION': 10, 'COMBINATION': 13, 'FERMENT_LEAVEN': 5, 'TRANSFER': 15, 'SHAPING': 10, 'PRESERVATION': 5, 'RESERVATION': 1, 'SERVING': 1, 'ENDPOINT': 9}
- **kind**: {'ACTION': 139, 'ENDPOINT': 9}
- **with_evidence**: 27
- **corpus_actions_without_evidence**: 109
- **top_unevidenced_by_corpus_freq**: ['put', 'add', 'serve', 'mix', 'remove', 'reserve', 'pour', 'preheat', 'cover', 'cool', 'flip', 'sprinkle', 'spoon', 'cut', 'toss', 'rest', 'spread', 'melt', 'beat', 'season', 'chop', 'roll', 'line', 'whisk', 'drizzle']
