# SP-002 pre-normalisation: rc2 grounding before / after (S178, T3-C07-R1)

Status: AI_DRAFTED / PROPOSED. Counts only (no line, no id, no unit token). Engineering coverage, not a quality estimate, not a gold score.
Tool `s178-corpus-prenorm-rerun-0.1.0-draft`; pre-normaliser `CQPO_SP002_PRENORM_V1_DRAFT` rules SP002_U2044, SP002_GLUED_REFUSE, SP002_HYPHEN_MIXED; BEFORE = frozen `CQPO_RC2_GROUNDING_V1_DRAFT` / `CQPO_PARSE_TO_AST_V2`. Locale from the legacy family map (Food.com US; others ambiguous). No POR records, no ingredient links.
Sample: full families.

## Lines changed per family

| family | recipes | lines | lines touched by a rule | % | rc2 record changes (markers aside) | amount changes | legacy parse changes | refused (glued) | rule counts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| FOODCOM | 522,517 | 4,129,433 | 1,275,154 | 30.88 | 1,275,123 (30.879 %) | 1,275,123 (30.879 %) | 1,275,153 | 0 | {'SP002_HYPHEN_MIXED': 1, 'SP002_U2044': 1275153} |
| WIKIBOOKS | 3,676 | 32,036 | 0 | 0.0 | 0 (0.0 %) | 0 (0.0 %) | 0 | 0 | {} |
| TASTESET | 700 | 3,788 | 443 | 11.695 | 441 (11.642 %) | 414 (10.929 %) | 441 | 0 | {'SP002_HYPHEN_MIXED': 2, 'SP002_U2044': 441} |
| GUTENBERG_SEGMENT | NOT_AVAILABLE | | | | | | | | NO_INGREDIENT_LINES_S177_F6 |
| A1_BBC_GOOD_FOOD | NOT_ON_THIS_SERVER | | | | | | | | D_003_BBC_DATA_NOT_PRESENT |

## FOODCOM: before and after

| measure | before | after | delta |
|---|---:|---:|---:|
| lines_total | 4,129,433 | 4,129,433 | +0 |
| lines_grounded | 4,129,433 | 4,129,433 | +0 |
| lines_with_rc2_mass | 87 | 127 | +40 |
| lines_with_rc2_volume | 0 | 0 | +0 |
| lines_with_rc2_count | 3,935,631 | 3,932,984 | -2,647 |
| lines_flagged | 193,716 | 1,468,840 | +1,275,124 |
| lines_contract_valid | 4,129,433 | 4,129,433 | +0 |
| mass_route = AST_EXACT_PHYSICAL | 87 | 127 | +40 |
| mass_route = NO_INGREDIENT_LINK | 3,935,631 | 3,932,984 | -2,647 |
| mass_route = UNSUPPORTED_EXPRESSION | 2,487 | 5,094 | +2,607 |
| unit_resolution = COUNT | 3,935,631 | 3,932,974 | -2,657 |
| unit_resolution = MASS_PHYSICAL | 87 | 127 | +40 |
| unit_resolution = NONE | 193,715 | 196,322 | +2,607 |
| unit_resolution = PACKAGE | 0 | 10 | +10 |
| ast_root = RANGE | 62,433 | 76,145 | +13,712 |
| ast_root = RATIONAL | 3,873,285 | 3,856,966 | -16,319 |
| ast_root = UNKNOWN | 193,715 | 196,322 | +2,607 |
| arithmetic_status = KNOWN | 3,873,285 | 3,856,966 | -16,319 |
| arithmetic_status = RANGE | 62,433 | 76,145 | +13,712 |
| arithmetic_status = UNKNOWN | 193,715 | 196,322 | +2,607 |
| q_level = Q0 | 87 | 127 | +40 |
| q_level = Q6 | 4,129,346 | 4,129,306 | -40 |
| flag MASS_FLOAT_REPRESENTATION | 0 | 3 | +3 |
| flag NONTERMINATING_RANGE_BOUND | 0 | 1,482 | +1,482 |
| flag NORMALIZATION_FLOAT_PRECISION_LIMIT | 0 | 101,860 | +101,860 |
| flag PRENORM_SP002_HYPHEN_MIXED | 0 | 1 | +1 |
| flag PRENORM_SP002_U2044 | 0 | 1,275,153 | +1,275,153 |
| flag UNSUPPORTED_COMPOUND_AMOUNT | 2,155 | 3,280 | +1,125 |

Unaffected unique lines re-checked through the opt-in path: 18,723 sampled (capped: the first lines of each worker chunk, not a random sample) of 79,196 unaffected unique lines; 18,723 of the 18,723 identical.
BEFORE vs committed S161 counts: **IDENTICAL** (0 differences).

Transitions among affected lines (lines):

- `valueclass__E1__TO__LT1`: 911,130
- `valueclass__E1__TO__FRACTIONAL_GT1`: 172,208
- `valueclass__INT_GT1__TO__LT1`: 119,827
- `flag_added__NORMALIZATION_FLOAT_PRECISION_LIMIT`: 101,860
- `valueclass__INT_GT1__TO__FRACTIONAL_GT1`: 52,615
- `arithmetic_status__KNOWN__TO__RANGE`: 13,740
- `ast_root__RATIONAL__TO__RANGE`: 13,740
- `valueclass__E1__TO__RANGE`: 13,333
- `valueclass__INT_GT1__TO__RANGE`: 3,279
- `mass_route__NO_INGREDIENT_LINK__TO__UNSUPPORTED_EXPRESSION`: 2,607
- `unit_resolution__COUNT__TO__NONE`: 2,607
- `arithmetic_status__KNOWN__TO__UNKNOWN`: 2,579
- `ast_root__RATIONAL__TO__UNKNOWN`: 2,579
- `valueclass__E1__TO__UNKNOWN`: 2,285
- `flag_added__NONTERMINATING_RANGE_BOUND`: 1,482
- `flag_added__UNSUPPORTED_COMPOUND_AMOUNT`: 1,125
- `valueclass__INT_GT1__TO__UNKNOWN`: 320
- `mass_route__NO_INGREDIENT_LINK__TO__AST_EXACT_PHYSICAL`: 40
- `q_level__Q6__TO__Q0`: 40
- `unit_resolution__COUNT__TO__MASS_PHYSICAL`: 40
- `rc2_mass_status__UNKNOWN__TO__MEASURED`: 39
- `arithmetic_status__RANGE__TO__UNKNOWN`: 28
- `ast_root__RANGE__TO__UNKNOWN`: 28
- `unit_resolution__COUNT__TO__PACKAGE`: 10
- `flag_added__MASS_FLOAT_REPRESENTATION`: 3

## WIKIBOOKS: before and after

| measure | before | after | delta |
|---|---:|---:|---:|
| lines_total | 32,036 | 32,036 | +0 |
| lines_grounded | 32,036 | 32,036 | +0 |
| lines_with_rc2_mass | 3,020 | 3,020 | +0 |
| lines_with_rc2_volume | 532 | 532 | +0 |
| lines_with_rc2_count | 6,142 | 6,142 | +0 |
| lines_flagged | 22,859 | 22,859 | +0 |
| lines_contract_valid | 32,034 | 32,034 | +0 |

Unaffected unique lines re-checked through the opt-in path: 18,986 sampled (capped: the first lines of each worker chunk, not a random sample) of 20,806 unaffected unique lines; 18,986 of the 18,986 identical.
BEFORE vs committed S161 counts: **IDENTICAL** (0 differences).

Transitions among affected lines (lines):


## TASTESET: before and after

| measure | before | after | delta |
|---|---:|---:|---:|
| lines_total | 3,788 | 3,788 | +0 |
| lines_grounded | 3,788 | 3,788 | +0 |
| lines_with_rc2_mass | 410 | 465 | +55 |
| lines_with_rc2_volume | 16 | 16 | +0 |
| lines_with_rc2_count | 1,264 | 858 | -406 |
| lines_flagged | 2,376 | 2,784 | +408 |
| lines_contract_valid | 3,788 | 3,788 | +0 |
| mass_route = AST_EXACT_PHYSICAL | 397 | 453 | +56 |
| mass_route = NO_INGREDIENT_LINK | 2,666 | 2,610 | -56 |
| mass_route = PARENTHETICAL_SOURCE_STATED | 13 | 12 | -1 |
| mass_route = UNSUPPORTED_EXPRESSION | 289 | 290 | +1 |
| unit_resolution = COUNT | 1,264 | 858 | -406 |
| unit_resolution = MASS_PHYSICAL | 397 | 453 | +56 |
| unit_resolution = NONE | 712 | 713 | +1 |
| unit_resolution = VOLUME_LOCALE_AMBIGUOUS | 1,399 | 1,748 | +349 |
| ast_root = RANGE | 33 | 36 | +3 |
| ast_root = RATIONAL | 3,043 | 3,039 | -4 |
| ast_root = UNKNOWN | 610 | 611 | +1 |
| arithmetic_status = KNOWN | 3,043 | 3,039 | -4 |
| arithmetic_status = RANGE | 33 | 36 | +3 |
| arithmetic_status = UNKNOWN | 610 | 611 | +1 |
| q_level = Q0 | 410 | 465 | +55 |
| q_level = Q6 | 3,378 | 3,323 | -55 |
| flag COMPATIBILITY_CHANNEL_MASKED | 40 | 45 | +5 |
| flag LOCALE_AMBIGUOUS | 1,399 | 1,748 | +349 |
| flag MASS_FLOAT_REPRESENTATION | 345 | 402 | +57 |
| flag NORMALIZATION_FLOAT_PRECISION_LIMIT | 233 | 314 | +81 |
| flag PARENTHETICAL_EXPRESSION_SEPARATE | 22 | 23 | +1 |
| flag PRENORM_SP002_HYPHEN_MIXED | 0 | 2 | +2 |
| flag PRENORM_SP002_U2044 | 0 | 441 | +441 |
| flag UNSUPPORTED_COMPOUND_AMOUNT | 9 | 10 | +1 |
| flag locale_ambiguous | 1,510 | 1,881 | +371 |

Unaffected unique lines re-checked through the opt-in path: all 2,739 unaffected unique lines (exhaustive); 2,739 of the 2,739 identical.
BEFORE vs committed S161 counts: **IDENTICAL** (0 differences).

Transitions among affected lines (lines):

- `flag_added__locale_ambiguous`: 371
- `flag_added__LOCALE_AMBIGUOUS`: 349
- `unit_resolution__COUNT__TO__VOLUME_LOCALE_AMBIGUOUS`: 349
- `valueclass__E1__TO__LT1`: 302
- `flag_added__NORMALIZATION_FLOAT_PRECISION_LIMIT`: 81
- `flag_added__MASS_FLOAT_REPRESENTATION`: 57
- `unit_resolution__COUNT__TO__MASS_PHYSICAL`: 56
- `q_level__Q6__TO__Q0`: 55
- `mass_route__NO_INGREDIENT_LINK__TO__AST_EXACT_PHYSICAL`: 54
- `rc2_mass_status__UNKNOWN__TO__MEASURED`: 54
- `valueclass__E1__TO__FRACTIONAL_GT1`: 51
- `valueclass__INT_GT1__TO__LT1`: 37
- `valueclass__INT_GT1__TO__FRACTIONAL_GT1`: 18
- `flag_added__COMPATIBILITY_CHANNEL_MASKED`: 5
- `valueclass__E1__TO__RANGE`: 4
- `arithmetic_status__KNOWN__TO__RANGE`: 3
- `ast_root__RATIONAL__TO__RANGE`: 3
- `mass_route__PARENTHETICAL_SOURCE_STATED__TO__AST_EXACT_PHYSICAL`: 2
- `arithmetic_status__KNOWN__TO__UNKNOWN`: 1
- `ast_root__RATIONAL__TO__UNKNOWN`: 1
- `flag_added__PARENTHETICAL_EXPRESSION_SEPARATE`: 1
- `flag_added__UNSUPPORTED_COMPOUND_AMOUNT`: 1
- `mass_route__NO_INGREDIENT_LINK__TO__PARENTHETICAL_SOURCE_STATED`: 1
- `mass_route__NO_INGREDIENT_LINK__TO__UNSUPPORTED_EXPRESSION`: 1
- `rc2_mass_status__UNKNOWN__TO__RANGE`: 1
