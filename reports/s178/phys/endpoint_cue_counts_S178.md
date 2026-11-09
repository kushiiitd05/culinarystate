# Endpoint cues per heat event, non-BBC corpus (S178 PHYS2, T4-C03-R1)

Status: DRAFT / AI_DRAFTED, counts only. Endpoint cues ("until golden", "until tender", "until reduced by half", a food-probe target temperature) are stored in the `endpoint` block of each Layer 1 heat record, outside `inputs`, and never enter a feature row (SSOT 199.8). The lexicon is `registry/endpoint_cue_lexicon_v1.csv` (AI_DRAFTED); a clause with a trigger and no lexicon word is counted as UNTIL_CLAUSE_UNCLASSIFIED, not dropped.

**All non-BBC families: 1,696,743 heat events, 513,698 with at least one endpoint cue (30.3%).**

| source family | heat events | with a cue | share | cues | unclassified share of cues | target-temperature cues |
|---|---:|---:|---:|---:|---:|---:|
| FOODCOM | 1,503,261 | 487,334 | 0.3242 | 579,716 | 0.0732 | 2621 |
| GUTENBERG_SEGMENT | 182,049 | 23,047 | 0.1266 | 25,756 | 0.1908 | 8 |
| WIKIBOOKS | 11,433 | 3,317 | 0.2901 | 4,032 | 0.0776 | 130 |
| TASTESET | 0 | 0 | n/a | 0 | 0.0 | 0 |

## Cue classes (all non-BBC families)

| class | cues |
|---|---:|
| COLOUR | 130,204 |
| SOFTEN | 113,925 |
| INTERNAL_DONENESS | 68,832 |
| UNTIL_CLAUSE_UNCLASSIFIED | 47,686 |
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
| TARGET_FOOD_TEMPERATURE | 2,759 |
| SERVE_OR_USE | 1,922 |
| COOL_COLD | 1,731 |
| CANDY_STAGE | 649 |

## Cues per heat event

| cues in the event | events |
|---|---:|
| 0 | 1,183,045 |
| 1 | 424,030 |
| 2 | 84,008 |
| 3+ | 5,660 |

## By heat family: events with a cue; cue with no stated duration; cue with no stated temperature

| heat family | events with a cue | cue and no duration | cue and no temperature |
|---|---:|---:|---:|
| DRY_HEAT | 152,526 | 45,901 | 101,856 |
| FAT_HEAT | 69,891 | 50,153 | 69,593 |
| HEAT_GENERAL | 213,407 | 150,554 | 211,183 |
| WET_HEAT | 77,874 | 50,395 | 49,875 |
