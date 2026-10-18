# Ledger EDA summary (2026-10-18T06:47:22+00:00)

| Ledger | records | versions | verification |
|---|---|---|---|
| ALIAS | 2,031 | 2,043 | {'UNVERIFIED': 2031} |
| ALLERGEN | 8 | 8 | {'UNVERIFIED': 8} |
| COND | 4,140 | 4,140 | {'UNVERIFIED': 4140} |
| EVD | 10,888 | 21,776 | {'UNVERIFIED': 10888} |
| IMAP | 592 | 592 | {'UNVERIFIED': 592} |
| ING | 2,009 | 2,027 | {'UNVERIFIED': 2009} |
| MEAS | 1 | 1 | {'UNVERIFIED': 1} |
| MOL | 131 | 131 | {'UNVERIFIED': 131} |
| PROC | 148 | 294 | {'UNVERIFIED': 148} |
| REC | 11,934 | 11,934 | {'UNVERIFIED': 11934} |
| SNAP | 3 | 3 | {'UNVERIFIED': 3} |
| SRC | 138 | 138 | {'UNVERIFIED': 129, 'AI_PRECHECKED': 5, 'NEEDS_SOURCE': 4} |
| STUDY | 125 | 125 | {'UNVERIFIED': 125} |
| SVAR | 187 | 318 | {'UNVERIFIED': 187} |
| TOOL | 76 | 76 | {'UNVERIFIED': 76} |
| UNIT | 74 | 74 | {'UNVERIFIED': 70, 'NEEDS_SOURCE': 4} |

## Evidence

- **rows**: 10888
- **tier**: {'E3': 10888}
- **origin_type**: {'DATABASE_AGGREGATE': 7018, 'PRIMARY_STUDY': 3870}
- **source_family**: {'USDA-RETN-R6': 7018, 'PHENOL-EXPLORER-3.6': 3870}
- **study_lineage**: {'NOT_IDENTIFIABLE': 7018, 'PRESENT': 3870}
- **independent_groups**: 126
- **censored_rows**: 2620
- **retention_factor_status**: {'CENSORED': 2620, 'MEASURED': 8244, 'UNKNOWN': 24}
- **direction**: {'UNKNOWN': 2644, 'DECREASE': 7146, 'NO_CHANGE': 80, 'INCREASE': 1018}
- **target_basis**: {'RETENTION_TR_OR_AR': 7018, 'FRESH_WEIGHT': 2906, 'PER_VOLUME': 960, 'DRY': 4}
- **ingredient_id_linked**: 0.5322
- **process_id_linked**: 0.9879
- **rows_with_temperature**: 2228
- **unique_matrices**: 184
- **unique_step_sequences**: 67
- **unique_targets**: 187
- **unique_cells**: 8651
- **matrix_process_density**: 0.0372
- **matrix_long_tail**: {'matrices_with_1_row': 10, 'median_rows_per_matrix': 17}
- **process_steps_top**: [('boil', 1630), ('simmer', 1534), ('store-ambient', 1132), ('bake', 910), ('store-refrigerated', 908), ('fry', 869), ('reheat', 727), ('drain', 598), ('broil', 546), ('brown', 520), ('cook', 312), ('store-frozen', 245), ('freeze', 226), ('roast', 224), ('steam', 214)]
- **replicate_rows_same_cell_same_group**: 2181
- **conflict_candidates**: 17

## Ingredients

- **concepts**: 2009
- **active**: 1997
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
- **with_evidence**: 36
- **corpus_actions_without_evidence**: 102
- **top_unevidenced_by_corpus_freq**: ['put', 'add', 'serve', 'mix', 'remove', 'reserve', 'pour', 'preheat', 'cover', 'cool', 'flip', 'sprinkle', 'spoon', 'cut', 'toss', 'rest', 'spread', 'melt', 'beat', 'season', 'chop', 'roll', 'line', 'whisk', 'drizzle']
