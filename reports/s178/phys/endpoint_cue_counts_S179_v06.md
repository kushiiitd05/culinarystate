# Endpoint cues per heat event, non-BBC corpus (S178 PHYS2, T4-C03-R1)

Status: DRAFT / AI_DRAFTED, counts only. Endpoint cues ("until golden", "until tender", "until reduced by half", a food-probe target temperature) are stored in the `endpoint` block of each Layer 1 heat record, outside `inputs`, and never enter a feature row (SSOT 199.8). The lexicon is `registry/endpoint_cue_lexicon_v1.csv` (AI_DRAFTED); a clause with a trigger and no lexicon word is counted as UNTIL_CLAUSE_UNCLASSIFIED, not dropped.

**All non-BBC families: 1,696,743 heat events, 513,739 with at least one endpoint cue (30.3%).**

| source family | heat events | with a cue | share | cues | unclassified share of cues | target-temperature cues |
|---|---:|---:|---:|---:|---:|---:|
| FOODCOM | 1,503,261 | 487,376 | 0.3242 | 580,025 | 0.0723 | 3457 |
| GUTENBERG_SEGMENT | 182,049 | 23,046 | 0.1266 | 25,759 | 0.1902 | 26 |
| WIKIBOOKS | 11,433 | 3,317 | 0.2901 | 4,059 | 0.0744 | 168 |
| TASTESET | 0 | 0 | n/a | 0 | 0.0 | 0 |

## Cue classes (all non-BBC families)

| class | cues |
|---|---:|
| COLOUR | 130,204 |
| SOFTEN | 113,925 |
| INTERNAL_DONENESS | 68,832 |
| UNTIL_CLAUSE_UNCLASSIFIED | 47,133 |
| MELT_DISSOLVE_SMOOTH | 41,243 |
| THICKEN | 33,585 |
| BUBBLE_BOIL | 25,562 |
| CRISP | 20,470 |
| SET_FIRM | 19,804 |
| EVAPORATE_REDUCE | 19,392 |
| DONENESS_TEST | 17,738 |
| TRANSLUCENT_OPAQUE | 16,852 |
| HOT_WARM | 16,581 |
| TEXTURE_STATE | 13,857 |
| AROMA | 6,952 |
| PUFF_RISE | 5,896 |
| WILT | 3,864 |
| TARGET_FOOD_TEMPERATURE | 3,651 |
| SERVE_OR_USE | 1,922 |
| COOL_COLD | 1,731 |
| CANDY_STAGE | 649 |

## Cues per heat event

| cues in the event | events |
|---|---:|
| 0 | 1,183,004 |
| 1 | 423,838 |
| 2 | 84,195 |
| 3+ | 5,706 |

## By heat family: events with a cue; cue with no stated duration; cue with no stated temperature

| heat family | events with a cue | cue and no duration | cue and no temperature |
|---|---:|---:|---:|
| DRY_HEAT | 152,544 | 45,909 | 100,128 |
| FAT_HEAT | 69,895 | 50,157 | 69,668 |
| HEAT_GENERAL | 213,423 | 150,569 | 211,427 |
| WET_HEAT | 77,877 | 50,397 | 49,908 |

## Until-clause check (S178 FIX-PHYS, SCI-A M1)

515,412 until / till clauses. A TEXT_STATED temperature that Layer 1 still binds as the medium temperature may lie inside an until-clause only when it is exempt (the liquid's or the medium's own temperature, a syrup / candy stage, a setting phrase such as 'until golden at 350 F', a medium thermometer); every other temperature there is a target of the food (endpoint).

| role of the temperature inside the clause | temperatures | of which bound as the medium T |
|---|---:|---:|
| EXEMPT_LIQUID_OR_MEDIUM_SUBJECT | 171 | 156 |
| EXEMPT_MEDIUM_THERMOMETER | 228 | 220 |
| EXEMPT_SETTING_PHRASE | 39 | 35 |
| EXEMPT_SYRUP_OR_CANDY | 104 | 102 |
| TARGET_LIST | 28 | 0 |
| TARGET_STRONG_CUE | 2,108 | 0 |
| TARGET_UNTIL_CLAUSE | 540 | 0 |
