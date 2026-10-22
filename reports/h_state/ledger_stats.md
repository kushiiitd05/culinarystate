# Ledger statistics drop (non-recipe ledgers; read-only)

Latest version per id; `history_lines` counts the append-only lines. REC (recipes) excluded except its row count.

| ledger | latest ids | history lines | ACTIVE | other status | verification (top) | provenance method (top) |
|---|---|---|---|---|---|---|
| SRC | 488 | 609 | 488 | {} | {'UNVERIFIED': 479, 'AI_PRECHECKED': 5, 'NEEDS_SOURCE': 4} | {'MANUAL': 363, 'IMPORT': 125} |
| SNAP | 346 | 347 | 346 | {} | {'UNVERIFIED': 346} | {'SCRAPE': 339, 'IMPORT': 7} |
| STUDY | 125 | 125 | 125 | {} | {'UNVERIFIED': 125} | {'IMPORT': 125} |
| ING | 2110 | 5387 | 2048 | {'SUPERSEDED': 49, 'DEPRECATED': 13} | {'UNVERIFIED': 2110} | {'MODEL': 2013, 'IMPORT': 97} |
| ALIAS | 4116 | 4183 | 4103 | {'DEPRECATED': 13} | {'UNVERIFIED': 4116} | {'MODEL': 2065, 'IMPORT': 2051} |
| ALLERGEN | 8 | 11 | 8 | {} | {'UNVERIFIED': 8} | {'MANUAL': 8} |
| PROC | 156 | 552 | 156 | {} | {'UNVERIFIED': 156} | {'MANUAL': 156} |
| TOOL | 119 | 297 | 119 | {} | {'UNVERIFIED': 119} | {'MANUAL': 119} |
| UNIT | 74 | 74 | 74 | {} | {'UNVERIFIED': 70, 'NEEDS_SOURCE': 4} | {'MANUAL': 74} |
| SVAR | 224 | 355 | 224 | {} | {'UNVERIFIED': 224} | {'IMPORT': 224} |
| MEAS | 3 | 3 | 3 | {} | {'UNVERIFIED': 3} | {'IMPORT': 3} |
| COND | 4414 | 4746 | 4414 | {} | {'UNVERIFIED': 4414} | {'IMPORT': 4414} |
| EVD | 18156 | 57280 | 17978 | {'DEPRECATED': 178} | {'UNVERIFIED': 14286, 'AI_PRECHECKED': 3870} | {'IMPORT': 18156} |
| MOL | 1726 | 1726 | 1726 | {} | {'UNVERIFIED': 1726} | {'IMPORT': 1726} |
| IMAP | 30294 | 31972 | 30294 | {} | {'UNVERIFIED': 30294} | {'IMPORT': 29656, 'DERIVED': 638} |
| KGE | 48181 | 80607 | 45201 | {'DEPRECATED': 2980} | {'UNVERIFIED': 48181} | {'IMPORT': 30066, 'DERIVED': 18115} |
| EXP | 7 | 8 | 7 | {} | {'UNVERIFIED': 7} | {'DERIVED': 7} |
| REC | (excluded) | 107760 | | | | |

## SRC

- **status**: {"ACTIVE": 488}
- **verification**: {"UNVERIFIED": 479, "AI_PRECHECKED": 5, "NEEDS_SOURCE": 4}
- **provenance_method**: {"MANUAL": 363, "IMPORT": 125}
- **kind**: {"BOOK": 338, "PAPER": 125, "DATABASE": 9, "AUTHORITY_STANDARD": 5, "PROJECT": 4, "DATASET": 3, "API": 2, "WEBSITE": 1, "REPO": 1}
- **licence_status**: {"VERIFIED": 345, "UNKNOWN": 125, "ASSUMED": 17, "RESTRICTED": 1}
- **primary_or_secondary**: {"PRIMARY": 470, "SECONDARY": 14, "UNKNOWN": 4}

## SNAP

- **status**: {"ACTIVE": 346}
- **verification**: {"UNVERIFIED": 346}
- **provenance_method**: {"SCRAPE": 339, "IMPORT": 7}
- **http_status**: {"200": 345, "None": 1}
- **bytes**: {"n": 346, "sum": 130502063, "median": 188011, "max": 9185858}

## STUDY

- **status**: {"ACTIVE": 125}
- **verification**: {"UNVERIFIED": 125}
- **provenance_method**: {"IMPORT": 125}
- **design**: {"UNKNOWN": 125}
- **source_id**: {"SRC-000013": 1, "SRC-000014": 1, "SRC-000015": 1, "SRC-000016": 1, "SRC-000017": 1, "SRC-000018": 1, "SRC-000019": 1, "SRC-000020": 1, "SRC-000021": 1, "SRC-000022": 1, "SRC-000023": 1, "SRC-000024": 1}

## ING

- **status**: {"ACTIVE": 2048, "SUPERSEDED": 49, "DEPRECATED": 13}
- **verification**: {"UNVERIFIED": 2110}
- **provenance_method**: {"MODEL": 2013, "IMPORT": 97}
- **canonical_names_unique**: 2110
- **ambiguity**: {"LOW": 1998, "MEDIUM": 97, "HIGH": 15}
- **with_parent**: 323
- **corpus_frequency**: {"n": 2013, "sum": 114869, "median": 9, "max": 3476}
- **facet_keys**: {"{}": 1872, "{\"form\": \"paste\"}": 46, "{\"form\": \"sauce\"}": 36, "{\"form\": \"powder\"}": 29, "{\"form\": \"seed\"}": 28, "{\"form\": \"oil\"}": 26, "{\"form\": \"juice\"}": 16, "{\"form\": \"stock\"}": 10}
- **crosswalk_fdc**: {"UNRESOLVED_EXTERNAL": 2110}
- **crosswalk_foodon**: {"NO_MATCH": 1216, "LINKED": 576, "CANDIDATE": 306, "UNRESOLVED_EXTERNAL": 12}
- **top_by_frequency**: [["butter", 3476], ["garlic", 3463], ["olive oil", 3195], ["egg", 2796], ["onion", 2056], ["lemon", 2037], ["plain flour", 1812], ["coriander", 1442], ["caster sugar", 1203], ["tomato", 1128]]

## ALIAS

- **status**: {"ACTIVE": 4103, "DEPRECATED": 13}
- **verification**: {"UNVERIFIED": 4116}
- **provenance_method**: {"MODEL": 2065, "IMPORT": 2051}
- **alias_type**: {"SYNONYM": 2641, "TRANSLATION": 1463, "PLURAL": 12}
- **link_band**: {"HIGH": 2063, "EXACT": 1963, "MEDIUM": 90}
- **language**: {"en": 2653, "hi": 172, "ta": 156, "ml": 143, "bn": 141, "kn": 136, "pa": 135, "ur": 121, "te": 111, "mr": 96, "or": 82, "gu": 74}
- **unique_normalized**: 4107
- **unique_target_ingredients**: 2014
- **corpus_frequency**: {"n": 2220, "sum": 118529, "median": 7, "max": 3997}

## ALLERGEN

- **status**: {"ACTIVE": 8}
- **verification**: {"UNVERIFIED": 8}
- **provenance_method**: {"MANUAL": 8}
- **names**: ["Cereals containing gluten", "Crustacean", "Egg", "Fish", "Milk", "Nut", "Soy", "Sulphite"]

## PROC

- **status**: {"ACTIVE": 156}
- **verification**: {"UNVERIFIED": 156}
- **provenance_method**: {"MANUAL": 156}
- **kind**: {"ACTION": 147, "ENDPOINT": 9}
- **family**: {"MECHANICAL_CUT": 22, "TRANSFER": 15, "WET_HEAT": 14, "MECHANICAL_MIX": 14, "COMBINATION": 13, "FAT_HEAT": 12, "SEPARATION": 11, "SHAPING": 10, "DRY_HEAT": 9, "ENDPOINT": 9, "HEAT_GENERAL": 7, "PRESERVATION": 6, "FERMENT_LEAVEN": 5, "COOLING": 4, "HEAT_CONTROL": 2, "RESTING": 1, "RESERVATION": 1, "SERVING": 1}
- **mechanism_families**: {"cell_rupture_enzymatic_reactions": 22, "maillard": 21, "moisture_loss": 21, "lipid_oxidation": 21, "protein_denaturation": 21, "leaching": 14, "starch_gelatinisation": 14, "cell_wall_softening": 14, "emulsification": 14, "aeration": 14, "gluten_development": 14, "oil_uptake": 12, "acrylamide_formation_starchy": 12, "caramelisation": 9, "phase_change": 7, "water_activity_reduction": 6, "acidification": 6, "microbial_inactivation": 6, "microbial_fermentation": 5, "co2_leavening": 5}
- **corpus_frequency**: {"n": 156, "sum": 212764, "median": 451, "max": 12430}
- **evidence_coverage**: {"n": 156, "sum": 19651, "median": 0, "max": 2997}
- **with_evidence**: 37
- **top_by_frequency**: [["put", 12430], ["add", 11948], ["cook", 9864], ["stir", 8579], ["serve", 8371], ["mix", 7713], ["remove", 7474], ["heat", 7109], ["reserve", 7105], ["bake", 5372], ["pour", 5172], ["preheat", 5170], ["cover", 4987], ["cool", 4467], ["flip", 4013]]

## TOOL

- **status**: {"ACTIVE": 119}
- **verification**: {"UNVERIFIED": 119}
- **provenance_method**: {"MANUAL": 119}
- **category**: {"UTENSIL": 44, "COOKWARE": 29, "APPLIANCE": 22, "OTHER": 8, "VESSEL": 6, "HEAT_SOURCE": 5, "MEASURE": 5}
- **material**: {"None": 119}
- **max_safe_temp_status**: {"UNKNOWN": 119}
- **unique_aliases**: 204
- **top_by_mentions**: []

## UNIT

- **status**: {"ACTIVE": 74}
- **verification**: {"UNVERIFIED": 70, "NEEDS_SOURCE": 4}
- **provenance_method**: {"MANUAL": 74}
- **dimension**: {"COUNT": 36, "VOLUME": 15, "NONE": 15, "MASS": 5, "LENGTH": 3}
- **aliases_total**: 204
- **with_ambiguity_note**: 5
- **with_conventions**: 8
- **names**: ["bag", "ball", "bar", "block", "bottle", "box", "bulb", "bunch", "can", "carton", "cl", "clove", "cm", "cube", "cup", "dash", "dl", "dollop", "drizzle", "drop", "dsp", "ear", "fillet", "fl_oz", "g", "gallon", "glass", "glug", "grating", "handful", "head", "inch", "jar", "joint", "katori", "kg", "knob", "l", "lb", "leaf", "loaf", "mg", "ml", "mm", "mug", "oz", "pack", "piece", "pinch", "pint", "pod", "pot", "pouch", "punnet", "quart", "rasher", "sachet", "scattering", "shaving", "sheet", "slice", "smidgen", "splash", "sprig", "sprinkle", "squeeze", "stalk", "stick", "strip", "tbsp", "tray", "tsp", "tub", "wedge"]

## SVAR

- **status**: {"ACTIVE": 224}
- **verification**: {"UNVERIFIED": 224}
- **provenance_method**: {"IMPORT": 224}
- **family**: {"CHEMICAL": 223, "PHYSICAL": 1}
- **dimension**: {"mass/mass": 223, "mass": 1}
- **observable_in_session**: {"False": 223, "True": 1}
- **unique_names**: 223

## MEAS

- **status**: {"ACTIVE": 3}
- **verification**: {"UNVERIFIED": 3}
- **provenance_method**: {"IMPORT": 3}
- **family**: {"CALCULATION": 2, "GRAVIMETRY": 1}
- **basis**: {"UNKNOWN": 2, "FRESH_WEIGHT": 1}

## COND

- **status**: {"ACTIVE": 4414}
- **verification**: {"UNVERIFIED": 4414}
- **provenance_method**: {"IMPORT": 4414}
- **mask_temperature**: {"MEASURED": 2113, "UNKNOWN": 2025, "RANGE": 276}
- **mask_duration**: {"MEASURED": 2358, "UNKNOWN": 2030, "RANGE": 26}
- **mask_pressure**: {"None": 4015, "NOT_APPLICABLE": 270, "MEASURED": 129}
- **mask_moisture**: {"UNKNOWN": 4414}
- **mask_ph**: {"UNKNOWN": 4414}
- **temperature_locations**: {"UNSPECIFIED": 2409, "CORE": 165, "SETPOINT": 35, "MEDIUM": 21}
- **temperature_entries**: 2630
- **medium**: {"None": 3455, "water": 697, "steam": 139, "oil": 122, "liquid": 1}
- **duration_raw_unique**: 192
- **duration_status**: {"MEASURED": 2358, "UNKNOWN": 2030, "RANGE": 26}

## EVD

- **status**: {"ACTIVE": 17978, "DEPRECATED": 178}
- **verification**: {"UNVERIFIED": 14286, "AI_PRECHECKED": 3870}
- **provenance_method**: {"IMPORT": 18156}
- **tier**: {"E3": 18156}
- **design**: {"DATABASE_AGGREGATE": 14286, "UNKNOWN": 3870}
- **origin_type**: {"DATABASE_AGGREGATE": 14286, "PRIMARY_STUDY": 3870}
- **source_family**: {"BOGNAR-2002": 7268, "USDA-RETN-R6": 7018, "PHENOL-EXPLORER-3.6": 3870}
- **applicability**: {"GENERIC": 14286, "EXACT": 3870}
- **censored**: {"False": 12262, "True": 5894}
- **unique_ingredients**: 166
- **unique_matrix_raw_names**: 619
- **unique_food_groups**: {"meat based dishes": 2389, "Vegetables and Vegetable Products": 1378, "Finfish and Shellfish Products": 1040, "poultry based dishes": 1036, "fish based dishes": 996, "Pork Products": 988, "vegetable based dishes": 969, "Beef Products": 676, "Lamb, Veal, and Game Products": 597, "offal based dishes": 512, "crustaceans and molluscs based dishes": 498, "Legumes and Legume Products": 494, "mushrooms based dishes": 390, "Cereal Grains and Pasta": 364, "Fruits and fruit products / Fruits - Berries": 360}
- **unique_processes**: 37
- **unique_conditions**: 4414
- **unique_target_svars**: 224
- **unique_studies**: 125
- **target_basis**: {"RETENTION_TR_OR_AR": 7018, "TRUE_RETENTION": 6594, "FRESH_WEIGHT": 3580, "PER_VOLUME": 960, "DRY": 4}
- **direction**: {"DECREASE": 10947, "UNKNOWN": 5918, "INCREASE": 1198, "NO_CHANGE": 93}
- **retention_status**: {"MEASURED": 11564, "CENSORED": 5894, "None": 674, "UNKNOWN": 24}

## MOL

- **status**: {"ACTIVE": 1726}
- **verification**: {"UNVERIFIED": 1726}
- **provenance_method**: {"IMPORT": 1726}
- **with_smiles**: 1726
- **descriptor_keys**: {"{\"HBondAcceptorCount\": 2.0, \"HBondDonorC": 632, "{\"HBondAcceptorCount\": 1.0, \"HBondDonorC": 507, "{\"HBondAcceptorCount\": 3.0, \"HBondDonorC": 167, "{\"HBondAcceptorCount\": 0.0, \"HBondDonorC": 142, "{\"HBondAcceptorCount\": 4.0, \"HBondDonorC": 59, "{\"HBondAcceptorCount\": 5.0, \"HBondDonorC": 36}
- **unique_smiles**: 1576

## IMAP

- **status**: {"ACTIVE": 30294}
- **verification**: {"UNVERIFIED": 30294}
- **provenance_method**: {"IMPORT": 29656, "DERIVED": 638}
- **basis**: {"None": 30075, "FRESH_WEIGHT": 197, "PER_VOLUME": 22}
- **concentration_status**: {"QUALITATIVE": 29656, "None": 419, "MEASURED": 219}
- **unique_ingredients**: 313
- **unique_molecules**: 1659
- **unit**: {"None": 30075, "mg/100 g fresh weight": 197, "mg/100 ml": 15, "mg/100 mL": 7}

## KGE

- **status**: {"ACTIVE": 45201, "DEPRECATED": 2980}
- **verification**: {"UNVERIFIED": 48181}
- **provenance_method**: {"IMPORT": 30066, "DERIVED": 18115}
- **predicate**: {"ING_CO_OCCURS": 36212, "ING_USED_IN_CUISINE": 2752, "ING_PROCESSED_BY": 2470, "ING_MEASURED_IN_UNIT": 1160, "ING_COSYLAB_CATEGORY": 964, "MOL_HAS_TASTE": 941, "PROC_USES_TOOL": 672, "ING_HAS_CATEGORY": 631, "ING_PREP_FORM": 600, "ING_HEALTH_ASSOCIATION": 497, "ING_PARENT": 315, "ING_ALTERNATIVE_TO": 262, "PROC_IN_FAMILY": 156, "ING_CARBON_FOOTPRINT": 134, "TOOL_HAS_CATEGORY": 119}
- **method**: {"EXTERNAL_SOURCE": 30066, "CO_OCCURRENCE": 16770, "ONTOLOGY": 631, "STRUCTURAL": 315, "CURATED": 275, "SEQUENCE": 75, "TEXT_CONDITION": 49}
- **confidence_band**: {"LOW": 20795, "MEDIUM": 18651, "HIGH": 8735}
- **corpus_ids**: {"FLAVORGRAPH-RECIPE1M": 27530, "BBCGF-A1": 13166, "GUTENBERG-PD": 8347, "WIKIBOOKS-COOKBOOK": 8051, "None": 1270, "RECIPEDB2": 964, "BITTERSWEET": 524, "SPICEDISEASE": 497, "CHEMTASTESDB": 408, "SUEATABLE": 134}
- **unique_subjects**: 2549
- **unique_objects**: 1508

## EXP

- **status**: {"ACTIVE": 7}
- **verification**: {"UNVERIFIED": 7}
- **provenance_method**: {"DERIVED": 7}
- **compute**: {"CPU (Mac M2)": 4, "A100 (VPN) + CPU": 1, "CPU + A100 (CE scoring)": 1, "CPU (Mac); no GPU needed": 1}
