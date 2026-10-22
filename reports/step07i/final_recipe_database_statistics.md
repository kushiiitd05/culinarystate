# Final recipe database statistics (STEP 07I)

Provisional, uncalibrated identity layer. Source memory is untouched; counts below are FINDINGS, not targets.

## Counts

| measure | value |
|---|---|
| RAW_SOURCE_RECIPES | 612,782 |
| LOCAL_ANALYSIS_ELIGIBLE | 612,605 |
| RELEASE_ELIGIBLE_strict(raw_redistribution=YES) | 73,778 |
| RELEASE_CONDITIONAL(attribution/share-alike, needs H2) | 3,676 |
| EXACT_DUPLICATE_GROUPS(>=2 members) | 1,039 |
| RECORDS_IN_EXACT_DUPLICATE_GROUPS | 2,107 |
| EXACT_DEDUP_LOGICAL_RECIPES | 611,714 |
| HIGH_CONFIDENCE_NEAR_DUPLICATE_GROUPS | 0 |
| NEAR_DUPLICATE_CANDIDATE_PAIRS_STORED | 744,615 |
| RECIPE_FAMILIES_PROVISIONAL | 605,476 |
| MULTI_GROUP_FAMILIES | 5,803 |
| DISH_FAMILY_CANDIDATES | 46,697 |
| MODEL_ELIGIBLE(training_allowed=YES) | 73,778 |
| GOLD_PENDING | 40 |
| GOLD_CANDIDATES_NOT_ANNOTATED | 10 |

## SOURCE

```json
{
 "FOODCOM": 522517,
 "GUTENBERG_SEGMENT": 73955,
 "A1_BBC_GOOD_FOOD": 11934,
 "WIKIBOOKS": 3676,
 "TASTESET": 700
}
```

## LICENCE_USAGE

```json
{
 "registry_rows": 342,
 "recipes_by_usage_class": {
  "LICENCE_UNVERIFIED": 523217,
  "PUBLIC_OPEN": 73955,
  "LOCAL_RESEARCH_ONLY": 11934,
  "REDISTRIBUTABLE_WITH_ATTRIBUTION": 3676
 },
 "training_allowed": {
  "UNKNOWN": 535151,
  "YES": 73955,
  "CONDITIONAL": 3676
 },
 "raw_redistribution_allowed": {
  "NO": 535151,
  "YES": 73955,
  "CONDITIONAL": 3676
 },
 "h2_items": [
  "Food.com SRC registration + licence",
  "TASTEset SRC registration + licence",
  "A1/BBC training/redistribution",
  "Wikibooks share-alike training/release"
 ]
}
```

## DUPLICATION

```json
{
 "exact_relation_member_counts": {
  "EXACT_BINARY_COPY": 688,
  "EXACT_NORMALIZED_COPY": 380
 },
 "exact_group_stats": {
  "EXACT_BINARY_COPY|raw_hash": {
   "groups": 665,
   "records": 1351
  },
  "EXACT_BINARY_COPY|rec_content_sha256": {
   "groups": 230,
   "records": 475
  },
  "EXACT_NORMALIZED_COPY|norm_text_hash": {
   "groups": 1039,
   "records": 2107
  },
  "MIRRORED_COPY|canonical_url": {
   "groups": 0,
   "records": 0
  }
 },
 "cross_source_exact_groups": 0,
 "candidate_retrieval_diagnostics": {
  "ing_lsh_buckets_skipped_over_cap": 4745,
  "ing_lsh_records_in_skipped_buckets": 791511,
  "pairs_by_source_bit": {
   "1": 678114,
   "2": 58612,
   "4": 7940499,
   "8": 716
  },
  "pairs_total_candidates": 8639518,
  "partitions": 87,
  "raw_pairs_by_source": {
   "family": 716,
   "ing": 8476318,
   "steps": 256346,
   "title": 678114
  },
  "steps_lsh_buckets_skipped_over_cap": 0,
  "steps_lsh_records_in_skipped_buckets": 0,
  "title_blocks_subblocked": 77,
  "title_subblocks_skipped_over_60": 1
 },
 "human_benchmark": "none exists; blind ~400-pair calibration packet created UNLABELED; near-duplicates are NOT auto-coalesced",
 "legacy_signal": "REC family_id + 7 A1 near-duplicate pairs (word-5-shingle Jaccard>=0.8)"
}
```

## RECIPE_FAMILY

```json
{
 "method": "PROVISIONAL_STAR_V1 (pre-registered, uncalibrated)",
 "families": 605476,
 "multi_recipe_families": 6787,
 "multi_group_families": 5803,
 "heterogeneous": 25,
 "families_with_conflicts": 0,
 "family_size_distribution_recipes": {
  "1": 598689,
  "2": 6379,
  "3": 339,
  "4": 48,
  "5": 15,
  "6": 2,
  "7": 3,
  "18": 1
 },
 "largest": [
  [
   "RF-00601414",
   18
  ],
  [
   "RF-00255205",
   7
  ],
  [
   "RF-00098507",
   7
  ],
  [
   "RF-00117712",
   7
  ],
  [
   "RF-00055424",
   6
  ]
 ]
}
```

## GOLD_SILVER_RAW

```json
{
 "SOURCE_RAW": 600828,
 "SILVER_AUTO": 11914,
 "GOLD_PENDING_INDEPENDENT_IAA": 40
}
```

## GOLD_FIREWALL

```json
{
 "gold_in_index": 50,
 "gold_with_same_group_non_gold_members": 0,
 "gold_with_family_relatives": 2
}
```

## SIMULATION_READINESS

```json
{
 "recipe": {
  "PARTIAL_CONDITIONS": 448093,
  "PROCEDURALLY_RICH": 97055,
  "INSUFFICIENT_CONDITIONS": 37208,
  "QUALITATIVE_ONLY": 29547,
  "UNKNOWN": 879
 },
 "family": {
  "PARTIAL_CONDITIONS": 443153,
  "PROCEDURALLY_RICH": 96058,
  "INSUFFICIENT_CONDITIONS": 36526,
  "QUALITATIVE_ONLY": 28860,
  "UNKNOWN": 879
 },
 "extras": {
  "families_with_multiple_independent_procedural_sources": 2015,
  "families_with_conflicting_condition_fields": 0,
  "families_with_usable_T_and_time_in_one_recipe": 100667,
  "families_with_only_qualitative_conditions": 27578,
  "disclaimer": "text availability only; NOT simulation eligibility"
 }
}
```

## MISSINGNESS

```json
{
 "A1_BBC_GOOD_FOOD": {
  "has_ingredients": 0.0,
  "has_quantities": 0.0032,
  "has_instructions": 0.0,
  "has_conditions": 0.0003
 },
 "FOODCOM": {
  "has_ingredients": 0.0042,
  "has_quantities": 0.0056,
  "has_instructions": 0.0,
  "has_conditions": 0.0005
 },
 "GUTENBERG_SEGMENT": {
  "has_ingredients": 0.0024,
  "has_quantities": 0.9305,
  "has_instructions": 0.0024,
  "has_conditions": 0.4252
 },
 "TASTESET": {
  "has_ingredients": 0.0,
  "has_quantities": 0.27,
  "has_instructions": 1.0,
  "has_conditions": 0.9971
 },
 "WIKIBOOKS": {
  "has_ingredients": 0.0,
  "has_quantities": 0.16,
  "has_instructions": 0.0,
  "has_conditions": 0.0832
 }
}
```

## CONFLICTS

```json
{
 "families_with_conflicting_condition_fields": 0
}
```

## CULTURE_REGION_HISTORY

```json
{
 "source_share_pct": {
  "FOODCOM": 85.27,
  "GUTENBERG_SEGMENT": 12.07,
  "A1_BBC_GOOD_FOOD": 1.95,
  "WIKIBOOKS": 0.6,
  "TASTESET": 0.11
 },
 "language": {
  "en": 612782
 },
 "locale": {
  "en-US": 522517,
  "en-historic": 73955,
  "en-GB": 11934,
  "en": 4376
 },
 "explicit_cuisine_labelled_pct": 9.81,
 "explicit_cuisine_by_source": {
  "A1_BBC_GOOD_FOOD": 58.46,
  "FOODCOM": 0.0,
  "GUTENBERG_SEGMENT": 69.63,
  "TASTESET": 0.0,
  "WIKIBOOKS": 45.57
 },
 "top_explicit_cuisines": {
  "American": 35516,
  "English": 7640,
  "British": 3411,
  "French": 3382,
  "Jewish": 1932,
  "Italian": 1566,
  "Creole": 618,
  "Indian": 501,
  "Roman": 455,
  "Mexican": 422,
  "Canadian": 382,
  "Australian": 349,
  "Belgian": 300,
  "Chinese": 260,
  "Asian": 221
 },
 "era_known_pct": 93.03,
 "era_distribution": {
  "PUBLISHED_2007": 70204,
  "PUBLISHED_2008": 69485,
  "PUBLISHED_2009": 58036,
  "PUBLISHED_2006": 51409,
  "PUBLISHED_2005": 41002,
  "PUBLISHED_2010": 37375,
  "PUBLISHED_2002": 32456,
  "PUBLISHED_2003": 29372,
  "PUBLISHED_2004": 26686,
  "UNKNOWN": 26373,
  "PUBLISHED_2011": 24993,
  "AUTHOR_BORN_1850s": 21673,
  "PUBLISHED_2012": 20895,
  "AUTHOR_BORN_1800s": 19082,
  "PUBLISHED_2013": 18203,
  "PUBLISHED_2014": 8638,
  "PUBLISHED_2001": 7714,
  "AUTHOR_BORN_1750s": 5663,
  "PUBLISHED_2017": 4998,
  "PUBLISHED_2015": 4845,
  "PUBLISHED_2016": 4269,
  "PUBLISHED_1999": 3673,
  "PUBLISHED_2018": 3035,
  "PUBLISHED_2000": 1886,
  "PUBLISHED_2019": 1789
 },
 "steps_per_recipe_by_source": {
  "A1_BBC_GOOD_FOOD": {
   "0.0": 1.0,
   "0.25": 2.0,
   "0.5": 3.0,
   "0.75": 4.0,
   "0.9": 5.0,
   "0.99": 9.0,
   "1.0": 27.0
  },
  "FOODCOM": {
   "0.0": 0.0,
   "0.25": 4.0,
   "0.5": 6.0,
   "0.75": 8.0,
   "0.9": 12.0,
   "0.99": 21.0,
   "1.0": 107.0
  },
  "GUTENBERG_SEGMENT": {
   "0.0": 0.0,
   "0.25": 4.0,
   "0.5": 7.0,
   "0.75": 11.0,
   "0.9": 19.0,
   "0.99": 46.0,
   "1.0": 241.0
  },
  "TASTESET": {
   "0.0": 0.0,
   "0.25": 0.0,
   "0.5": 0.0,
   "0.75": 0.0,
   "0.9": 0.0,
   "0.99": 0.0,
   "1.0": 0.0
  },
  "WIKIBOOKS": {
   "0.0": 1.0,
   "0.25": 4.0,
   "0.5": 6.0,
   "0.75": 8.0,
   "0.9": 11.0,
   "0.99": 20.0,
   "1.0": 36.0
  }
 },
 "ingredient_lines_per_recipe_by_source": {
  "A1_BBC_GOOD_FOOD": {
   "0.0": 2.0,
   "0.25": 7.0,
   "0.5": 9.0,
   "0.75": 12.0,
   "0.9": 15.0,
   "0.99": 22.0,
   "1.0": 60.0
  },
  "FOODCOM": {
   "0.0": 0.0,
   "0.25": 5.0,
   "0.5": 7.0,
   "0.75": 10.0,
   "0.9": 13.0,
   "0.99": 19.0,
   "1.0": 44.0
  },
  "GUTENBERG_SEGMENT": {
   "0.0": 0.0,
   "0.25": 0.0,
   "0.5": 0.0,
   "0.75": 0.0,
   "0.9": 0.0,
   "0.99": 0.0,
   "1.0": 0.0
  },
  "TASTESET": {
   "0.0": 1.0,
   "0.25": 5.0,
   "0.5": 6.0,
   "0.75": 7.0,
   "0.9": 7.0,
   "0.99": 7.0,
   "1.0": 7.0
  },
  "WIKIBOOKS": {
   "0.0": 1.0,
   "0.25": 6.0,
   "0.5": 8.0,
   "0.75": 11.0,
   "0.9": 15.0,
   "0.99": 23.0,
   "1.0": 42.0
  }
 },
 "representativeness_statement": "NOT globally representative: dominated by Food.com (US user content) and historic English-language Gutenberg text; cuisine/region labels are dataset-derived and sparse; no claim of cultural coverage is made"
}
```

## INGREDIENTS_ALIASES

```json
{
 "total_mentions": 4964190,
 "mentions_by_source": {
  "FOODCOM": 4129433,
  "GUTENBERG_SEGMENT": 675103,
  "A1_BBC_GOOD_FOOD": 123598,
  "WIKIBOOKS": 32036,
  "TASTESET": 4020
 },
 "unique_raw_ingredient_strings": 22643,
 "canonical_ING_active": 2048,
 "canonical_ING_matched_distinct": 1875,
 "alias_active": 4103,
 "alias_exact_lookup_hits": 2925525,
 "alias_distinct_surface_forms_matched": 2045,
 "status_counts": {
  "ACCEPT": 2701449,
  "UNRESOLVED": 1320689,
  "REVIEW": 942052
 },
 "mapped_rate_pct(ACCEPT)": 54.42,
 "ambiguous_review_rate_pct": 18.98,
 "unmapped_rate_pct": 26.6,
 "status_by_source_pct": {
  "A1_BBC_GOOD_FOOD": {
   "ACCEPT": 68.36,
   "UNRESOLVED": 30.43,
   "REVIEW": 1.21
  },
  "FOODCOM": {
   "ACCEPT": 63.0,
   "UNRESOLVED": 30.59,
   "REVIEW": 6.4
  },
  "GUTENBERG_SEGMENT": {
   "REVIEW": 100.0
  },
  "TASTESET": {
   "ACCEPT": 65.67,
   "UNRESOLVED": 30.17,
   "REVIEW": 4.15
  },
  "WIKIBOOKS": {
   "UNRESOLVED": 57.97,
   "ACCEPT": 39.54,
   "REVIEW": 2.48
  }
 },
 "unmapped_unique_strings": 20527,
 "unmapped_coverage_top100_pct": 49.63,
 "unmapped_coverage_top1000_pct": 88.14,
 "unmapped_long_tail_strings_with_count_le_5": 16059,
 "unmapped_long_tail_mentions_share_pct": 1.69,
 "top_ingredients_global": [
  [
   "salt",
   260162
  ],
  [
   "butter",
   195507
  ],
  [
   "sugar",
   157911
  ],
  [
   "water",
   123449
  ],
  [
   "onion",
   105847
  ],
  [
   "pepper",
   93573
  ],
  [
   "flour",
   92279
  ],
  [
   "olive oil",
   81572
  ],
  [
   "milk",
   80853
  ],
  [
   "egg",
   67087
  ],
  [
   "garlic",
   63960
  ],
  [
   "cinnamon",
   52637
  ],
  [
   "plain flour",
   49337
  ],
  [
   "brown sugar",
   44656
  ],
  [
   "baking powder",
   44078
  ],
  [
   "parsley",
   41474
  ],
  [
   "lemon juice",
   37869
  ],
  [
   "vanilla",
   37297
  ],
  [
   "bicarbonate of soda",
   34655
  ],
  [
   "parmesan",
   33993
  ],
  [
   "black pepper",
   29920
  ],
  [
   "vanilla extract",
   29158
  ],
  [
   "ginger",
   28889
  ],
  [
   "sour cream",
   27841
  ],
  [
   "nutmeg",
   27068
  ]
 ],
 "top_ingredients_by_source": {
  "A1_BBC_GOOD_FOOD": [
   [
    "butter",
    3845
   ],
   [
    "garlic",
    3578
   ],
   [
    "olive oil",
    3397
   ],
   [
    "plain flour",
    1873
   ],
   [
    "lemon",
    1793
   ],
   [
    "onion",
    1481
   ],
   [
    "caster sugar",
    1306
   ],
   [
    "golden caster sugar",
    1232
   ]
  ],
  "FOODCOM": [
   [
    "salt",
    225622
   ],
   [
    "butter",
    162469
   ],
   [
    "sugar",
    132670
   ],
   [
    "onion",
    93243
   ],
   [
    "water",
    89953
   ],
   [
    "pepper",
    77177
   ],
   [
    "olive oil",
    76724
   ],
   [
    "flour",
    71781
   ]
  ],
  "GUTENBERG_SEGMENT": [
   [
    "water",
    32560
   ],
   [
    "salt",
    32322
   ],
   [
    "butter",
    28596
   ],
   [
    "egg",
    26123
   ],
   [
    "sugar",
    24315
   ],
   [
    "flour",
    20059
   ],
   [
    "milk",
    18234
   ],
   [
    "pepper",
    15772
   ]
  ],
  "TASTESET": [
   [
    "salt",
    184
   ],
   [
    "sugar",
    151
   ],
   [
    "butter",
    129
   ],
   [
    "pepper",
    119
   ],
   [
    "milk",
    99
   ],
   [
    "water",
    92
   ],
   [
    "olive oil",
    68
   ],
   [
    "garlic",
    58
   ]
  ],
  "WIKIBOOKS": [
   [
    "salt",
    1533
   ],
   [
    "water",
    615
   ],
   [
    "butter",
    468
   ],
   [
    "olive oil",
    429
   ],
   [
    "pepper",
    424

```

## QUANTITIES_UNITS

```json
{
 "quantity_lines": 4281956,
 "parse_kind": {
  "NUMBER": 3988266,
  "NONE": 203166,
  "RANGE": 64897,
  "FRACTION": 10609,
  "QUALITATIVE": 6519,
  "PACKAGE": 5521,
  "MIXED": 2006,
  "MULTIPLIER": 972
 },
 "quantity_present_pct": 95.26,
 "numeric_parse_pct": 95.12,
 "range_pct": 1.52,
 "qualitative_pct": 0.15,
 "unit_coverage_pct_of_numeric": 2.55,
 "unit_alias_resolved_pct_of_unit_raw": 99.41,
 "container_package_expressions": 6650,
 "multiplier_expressions": 972,
 "mass_grounded_pct": 0.92,
 "volume_grounded_pct": 1.26,
 "count_channel_pct": 93.1,
 "ambiguous_conversion_pct(locale range)": 0.37,
 "conversion_method": {
  "NONE": 4189413,
  "LOCALE_CONVENTION": 45017,
  "EXACT_PHYSICAL": 39900,
  "SOURCE_STATED": 7626
 },
 "q_level": {
  "Q6": 4242456,
  "Q0": 39500
 },
 "top_units": {
  "g": 29657,
  "tbsp": 22672,
  "tsp": 16094,
  "ml": 6794,
  "cup": 6727,
  "clove": 4949,
  "handful": 2258,
  "can": 2219,
  "pack": 2007,
  "bunch": 1444,
  "pinch": 1353,
  "head": 1309,
  "kg": 1069,
  "lb": 906,
  "oz": 906,
  "slice": 871,
  "piece": 686,
  "l": 548,
  "bag": 471,
  "pot": 428
 },
 "units_by_locale": {
  "UK": {
   "g": 27953,
   "tbsp": 18235,
   "tsp": 11503,
   "ml": 6317,
   "handful": 2192,
   "pack": 1941,
   "can": 1809,
   "bunch": 1316
  },
  "UNKNOWN": {
   "cup": 6642,
   "tsp": 4591,
   "tbsp": 4437,
   "g": 1617,
   "lb": 897,
   "oz": 863,
   "clove": 594,
   "ml": 477
  },
  "US": {
   "clove": 4192,
   "head": 1104,
   "bulb": 252,
   "leaf": 112,
   "g": 87,
   "pot": 22,
   "fillet": 17,
   "joint": 3
  }
 },
 "by_source_mass_grounded_pct": {
  "A1_BBC_GOOD_FOOD": 29.84,
  "FOODCOM": 0.0,
  "TASTESET": 11.88,
  "WIKIBOOKS": 12.93
 },
 "no_invented_grams": "pinch/handful/cup carry no gram value without POR evidence (q_level Q6 / UNKNOWN)"
}
```

## PROCESSES_HIERARCHY

```json
{
 "process_mentions": 12401784,
 "unique_raw_action_phrases": 14224,
 "canonical_PROC_active": 156,
 "canonical_PROC_matched_distinct": 148,
 "mapping_status": {
  "CANDIDATE_VERB_FORM_MATCH_POS_UNCHECKED": 12010066,
  "UNMAPPED": 391718
 },
 "mapped_rate_pct": 96.84,
 "unmapped_rate_pct": 3.16,
 "note": "mapped = verb-form candidate match to PROC (POS unchecked); UNMAPPED = leading token of a sentence with no PROC match",
 "process_family_coverage_pct_of_mapped": 100.0,
 "mentions_by_PROC_family": {
  "COMBINATION": 2267330,
  "MECHANICAL_MIX": 1754667,
  "TRANSFER": 1667113,
  "HEAT_GENERAL": 1281787,
  "MECHANICAL_CUT": 1134539,
  "WET_HEAT": 511875,
  "SEPARATION": 506891,
  "DRY_HEAT": 447827,
  "ENDPOINT": 404076,
  "SHAPING": 367820,
  "FAT_HEAT": 356044,
  "COOLING": 346649,
  "SERVING": 326188,
  "PRESERVATION": 205257,
  "HEAT_CONTROL": 152934,
  "RESERVATION": 105313,
  "RESTING": 99329,
  "FERMENT_LEAVEN": 74427
 },
 "top_processes": [
  [
   "add",
   859982
  ],
  [
   "mix",
   637604
  ],
  [
   "put",
   627625
  ],
  [
   "heat",
   600255
  ],
  [
   "cook",
   501487
  ],
  [
   "stir",
   479394
  ],
  [
   "serve",
   326188
  ],
  [
   "remove",
   311840
  ],
  [
   "trim",
   293337
  ],
  [
   "bake",
   272306
  ],
  [
   "season",
   251362
  ],
  [
   "boil",
   249344
  ],
  [
   "cover",
   244945
  ],
  [
   "brown",
   222631
  ],
  [
   "brush",
   217631
  ],
  [
   "pour",
   206043
  ],
  [
   "cool",
   193308
  ],
  [
   "cut",
   178772
  ],
  [
   "spread",
   174240
  ],
  [
   "beat",
   162913
  ],
  [
   "slice",
   157097
  ],
  [
   "squeeze",
   151007
  ],
  [
   "blend",
   146653
  ],
  [
   "sprinkle",
   142009
  ],
  [
   "melt",
   132275
  ]
 ],
 "top_processes_by_source": {
  "A1_BBC_GOOD_FOOD": [
   [
    "heat",
    22525
   ],
   [
    "put",
    17124
   ],
   [
    "add",
    16351
   ],
   [
    "cook",
    15721
   ],
   [
    "stir",
    11998
   ],
   [
    "mix",
    11694
   ]
  ],
  "FOODCOM": [
   [
    "add",
    768855
   ],
   [
    "mix",
    592908
   ],
   [
    "heat",
    556905
   ],
   [
    "put",
    519371
   ],
   [
    "cook",
    447600
   ],
   [
    "stir",
    439417
   ]
  ],
  "GUTENBERG_SEGMENT": [
   [
    "put",
    87464
   ],
   [
    "add",
    68672
   ],
   [
    "boil",
    64588
   ],
   [
    "remove",
    40814
   ],
   [
    "season",
    36732
   ],
   [
    "serve",
    34747
   ]
  ],
  "WIKIBOOKS": [
   [
    "add",
    6104
   ],
   [
    "heat",
    4673
   ],
   [
    "mix",
    4214
   ],
   [
    "put",
    3666
   ],
   [
    "cook",
    3562
   ],
   [
    "stir",
    2819
   ]
  ]
 },
 "mapped_process_mentions_per_recipe": {
  "0.0": 1.0,
  "0.25": 11.0,
  "0.5": 17.0,
  "0.75": 25.0,
  "0.9": 36.0,
  "0.99": 66.0,
  "1.0": 303.0
 },
 "recipes_with_no_mapped_process": 1240
}
```

## TOOLS_UTENSILS_MACHINES

```json
{
 "tool_mentions": 2745700,
 "canonical_TOOL_active": 119,
 "canonical_TOOL_matched_distinct": 119,
 "recipes_with_tool_mention": 554413,
 "structural_class_mentions": {
  "COOKWARE": 689106,
  "CONTAINER": 548770,
  "HEATING_APPLIANCE": 403021,
  "BAKEWARE": 303713,
  "MIXING_TOOL": 232963,
  "HAND_TOOL": 224704,
  "MECHANICAL_APPLIANCE": 112783,
  "OTHER": 104137,
  "COOLING_APPLIANCE": 57486,
  "CUTTING_TOOL": 42369,
  "MEASUREMENT_TOOL": 16562,
  "PRESSURE_EQUIPMENT": 5327,
  "UNKNOWN": 4737,
  "FERMENTATION/STORAGE_EQUIPMENT": 22
 },
 "structural_class_vocabulary": {
  "HAND_TOOL": 22,
  "HEATING_APPLIANCE": 16,
  "COOKWARE": 16,
  "MIXING_TOOL": 11,
  "BAKEWARE": 11,
  "CUTTING_TOOL": 9,
  "MECHANICAL_APPLIANCE": 7,
  "MEASUREMENT_TOOL": 6,
  "OTHER": 6,
  "CONTAINER": 5,
  "UNKNOWN": 5,
  "COOLING_APPLIANCE": 3,
  "PRESSURE_EQUIPMENT": 1,
  "FERMENTATION/STORAGE_EQUIPMENT": 1
 },
 "top_tools": [
  [
   "saucepan",
   481406
  ],
  [
   "bowl",
   345513
  ],
  [
   "oven",
   271741
  ],
  [
   "frying pan",
   135198
  ],
  [
   "baking dish",
   106346
  ],
  [
   "baking tray",
   104325
  ],
  [
   "wooden spoon",
   80908
  ],
  [
   "plate",
   78302
  ],
  [
   "whisk",
   72736
  ],
  [
   "wire rack",
   58716
  ],
  [
   "container",
   53668
  ],
  [
   "foil",
   49443
  ],
  [
   "grill",
   49314
  ],
  [
   "casserole",
   43011
  ],
  [
   "chopping board",
   42563
  ],
  [
   "fridge",
   42501
  ],
  [
   "blender",
   37478
  ],
  [
   "food processor",
   37203
  ],
  [
   "glass",
   36836
  ],
  [
   "pastry brush",
   35905
  ]
 ],
 "top_appliances": [
  [
   "oven",
   271741
  ],
  [
   "grill",
   49314
  ],
  [
   "fridge",
   42501
  ],
  [
   "blender",
   37478
  ],
  [
   "food processor",
   37203
  ],
  [
   "stand mixer",
   33613
  ],
  [
   "microwave",
   33111
  ],
  [
   "hob",
   15488
  ],
  [
   "freezer",
   13511
  ],
  [
   "slow cooker",
   10634
  ]
 ],
 "mapped_rate_note": "tool mentions are lexicon matches (mapped by construction); the unmapped rate is estimated by the review queue below from a text sample",
 "tool_mentions_by_source_per_1000_recipes": {
  "A1_BBC_GOOD_FOOD": 7901.1,
  "FOODCOM": 4753.4,
  "GUTENBERG_SEGMENT": 2037.5,
  "WIKIBOOKS": 4622.7
 },
 "top_tool_process_cooccurrence": [
  [
   "bowl",
   "mix",
   166689
  ],
  [
   "saucepan",
   "heat",
   131280
  ],
  [
   "oven",
   "preheat",
   117339
  ],
  [
   "saucepan",
   "put",
   111628
  ],
  [
   "saucepan",
   "add",
   107255
  ],
  [
   "saucepan",
   "cook",
   89559
  ],
  [
   "bowl",
   "put",
   84012
  ],
  [
   "frying pan",
   "heat",
   78942
  ],
  [
   "saucepan",
   "stir",
   70120
  ],
  [
   "saucepan",
   "remove",
   68718
  ],
  [
   "bowl",
   "add",
   68481
  ],
  [
   "saucepan",
   "boil",
   66374
  ],
  [
   "whisk",
   "whisk",
   65579
  ],
  [
   "oven",
   "bake",
   62090
  ],
  [
   "saucepan",
   "mix",
   61165
  ],
  [
   "oven",
   "put",
   56132
  ],
  [
   "bowl",
   "stir",
   51885
  ],
  [
   "saucepan",
   "brush",
   48376
  ],
  [
   "frying pan",
   "add",
   46795
  ],
  [
   "frying pan",
   "cook",
   46618
  ],
  [
   "baking tray",
   "put",
   45601
  ],
  [
   "saucepan",
   "pour",
   44567
  ],
  [
   "wooden spoon",
   "spoon",
   44216
  ],
  [
   "oven",
   "heat",
   43215
  ],
  [
   "saucepan",
   "cover",
   41579
  ]
 ]
}
```

## CONDITIONS_TEMPORAL_ENDPOINTS

```json
{
 "recipe_level_pct": {
  "has_time": 88.88,
  "has_numeric_temperature": 16.68,
  "has_temperature_location": 16.01,
  "has_pressure": 0.01,
  "has_power": 0.03,
  "has_qualitative_heat": 25.97,
  "has_endpoint_condition": 69.13,
  "has_quantity_information": 88.16,
  "has_geometry_information": 14.84,
  "has_medium_information": 14.26
 },
 "family_level_pct": {
  "has_time": 88.98,
  "has_numeric_temperature": 16.7,
  "has_temperature_location": 16.04,
  "has_pressure": 0.01,
  "has_power": 0.03,
  "has_qualitative_heat": 25.95,
  "has_endpoint_condition": 69.11,
  "has_quantity_information": 88.31,
  "has_geometry_information": 14.88,
  "has_medium_information": 14.25
 },
 "mentions": {
  "condition_mentions": 3904986,
  "by_family_status": {
   "ENDPOINT": {
    "VALID": 906295
   },
   "GAS_MARK": {
    "VALID": 7994
   },
   "MEDIUM": {
    "VALID": 102404
   },
   "POWER": {
    "VALID": 258,
    "AMBIGUOUS": 5
   },
   "PRESSURE": {
    "AMBIGUOUS": 99
   },
   "QUALITATIVE_HEAT": {
    "VALID": 192678
   },
   "TEMPERATURE": {
    "VALID": 126849,
    "AMBIGUOUS": 105423,
    "INVALID": 14
   },
   "TIME": {
    "VALID": 925701,
    "AMBIGUOUS": 4972,
    "INVALID": 340
   },
   "TIME_QUALITATIVE": {
    "VALID": 52166
   },
   "TIME_STRUCTURED_FIELD": {
    "VALID": 1479788
   }
  },
  "temperature_location": {
   "SETPOINT": 205527,
   "UNSPECIFIED": 18357,
   "CORE": 4903,
   "MEDIUM": 3499
  },
  "top_temporal_patterns": {
   "# minutes": 443926,
   "#-# minutes": 119784,
   "# to # minutes": 73936,
   "# hours": 49685,
   "# minute": 41684,
   "# hour": 36481,
   "# mins": 21364,
   "# seconds": 20609,
   "#-# hours": 13424,
   "# min": 10313,
   "#-# mins": 10067,
   "# days": 7848,
   "# to # hours": 7230,
   "# - # minutes": 6806,
   "# #/# hours": 5393
  },
  "top_endpoint_openers": {
   "until smooth": 45374,
   "until tender": 22326,
   "until golden brown": 21350,
   "until well blended": 12829,
   "until blended": 10532,
   "until it is": 10169,
   "until combined": 9955,
   "until golden": 9198,
   "until ready to": 9187,
   "until soft": 9074,
   "until lightly browned": 8828,
   "until the mixture": 8758,
   "until they are": 8148,
   "until thickened": 8058,
   "until done": 7930
  },
  "medium_values": {
   "water": 22504,
   "oil": 17271,
   "cold water": 14214,
   "boiling water": 11351,
   "milk": 10887,
   "hot water": 5159,
   "hot oil": 3327,
   "warm water": 2695,
   "salted water": 2469,
   "broth": 2404,
   "vinegar": 2045,
   "simmering water": 1857
  },
  "by_source": {
   "A1_BBC_GOOD_FOOD": {
    "TIME": 32158,
    "ENDPOINT": 27531,
    "TIME_STRUCTURED_FIELD": 11924,
    "TEMPERATURE": 11755,
    "GAS_MARK": 5787,
    "QUALITATIVE_HEAT": 4532,
    "MEDIUM": 1975,
    "TIME_QUALITATIVE": 1715,
    "POWER": 17
   },
   "FOODCOM": {
    "TIME_STRUCTURED_FIELD": 1467864,
    "TIME": 878024,
    "ENDPOINT": 830220,
    "TEMPERATURE": 215281,
    "QUALITATIVE_HEAT": 176686,
    "MEDIUM": 79984,
    "TIME_QUALITATIVE": 45898,
    "GAS_MARK": 2156,
    "POWER": 235,
    "PRESSURE": 93
   },
   "GUTENBERG_SEGMENT": {
    "ENDPOINT": 42927,
    "MEDIUM": 19585,
    "TIME": 15757,
    "QUALITATIVE_HEAT": 9909,
    "TIME_QUALITATIVE": 3959,
    "TEMPERATURE": 3185,
    "POWER": 4,
    "PRESSURE": 3
   },
   "TASTESET": {
    "TIME": 3,
    "TEMPERATURE": 1
   },
   "WIKIBOOKS": {
    "ENDPOINT": 5617,
    "TIME": 5071,
    "TEMPERATURE": 2064,
    "QUALITATIVE_HEAT": 1551,
    "MEDIUM": 860,
    "TIME_QUAL
```

## UNMAPPED TERMS / DATA QUALITY

See the three review-queue CSVs in this folder and the gate result.
