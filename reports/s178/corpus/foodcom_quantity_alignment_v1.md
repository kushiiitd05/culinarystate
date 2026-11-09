# Food.com quantity / part misalignment: diagnostic and proposed rule (S178)

Status: AI_DRAFTED / PROPOSED. Counts and rates only; no recipe text. NON_CITABLE. No behaviour change: `recipes.corpus.iter_foodcom` is untouched; the rules are opt-in in `culinarystate.quantity.foodcom_pairing` (`S178_FOODCOM_PAIRING_V1_DRAFT`).

Recipes: 522,517; part lines: 4,129,433.

## Diagnostic

| relation (quantities vs parts) | recipes | % |
|---|---:|---:|
| EQUAL | 114,981 | 22.005 |
| QUANTITIES_LONGER | 385,756 | 73.826 |
| QUANTITIES_SHORTER | 21,780 | 4.168 |

- Quantity strings 4,882,431 (null 298,706) against 4,129,433 parts: the quantity list is longer by 752,998 entries (1.441 per recipe).
- Mechanism (hypothesis, not established): the quantity list looks like one entry per source ingredient line (null when the line has no quantity) and the parts list like the lines in which a food part was extracted; lines with no extracted part (quantities longer, 73.8 percent of recipes, even for recipes with one part) and lines with two foods (parts longer) would shift every later position. The lists carry no line index, so this cannot be checked against the source.
- Unequal recipes: **407,536 (77.995 %)**; lines inside them: 3,172,362 (76.823 %).
- Positional pairing today: 3,937,847 lines get a quantity, 191,586 none; 779,502 quantity strings are dropped beyond the parts list (of them 208,406 with U+2044).
- Recipes with zero parts: 2,219; with zero quantities: 20.

Length difference (quantities minus parts), recipes:

| diff | recipes |
|---:|---:|
| M5 | 51 |
| M4 | 99 |
| M3 | 574 |
| M2 | 3,040 |
| M1 | 18,016 |
| P0 | 114,981 |
| P1 | 159,307 |
| P2 | 121,697 |
| P3 | 64,055 |
| P4 | 26,483 |
| P5 | 9,429 |
| P6 | 3,118 |
| P7 | 1,045 |
| P8 | 346 |
| P9 | 149 |
| P10 | 127 |

Share of recipes with equal lists by recipe length (a per-line drop mechanism makes long recipes unequal more often):

| parts | recipes | equal | % equal |
|---|---:|---:|---:|
| 1 | 8,672 | 13 | 0.15 |
| 2 | 19,653 | 2,232 | 11.357 |
| 3_4 | 73,271 | 13,245 | 18.077 |
| 5_8 | 210,801 | 48,888 | 23.192 |
| 9_15 | 186,832 | 46,533 | 24.906 |
| 16_PLUS | 21,069 | 4,050 | 19.223 |

## Proposed rule (default: EQUAL_LENGTH_ONLY)

Pair quantity and part only when the two lists have the same length (114,981 of 522,517 recipes, 23.177 % of lines); in every other recipe give the parts NO quantity (UNKNOWN). The current positional rule mispairs lines after the first drop in the other 77.995 % of recipes (76.823 % of lines).

Lines paired: 957,071 (23.177 %); lines left without a quantity: 3,172,362. equal length is necessary, not sufficient: a recipe that lost one part AND gained one stray quantity is indistinguishable; the rate of that case is unknown.

## Experimental alternative: ALIGN_MODEL (validated by simulation only)

Model trained on 68,935 equal-length train-split recipes (573,462 lines); skip cost 4.5 nats chosen on dev. Test-split simulation (truth known):

| scenario | recipes | parts | positional correct % | MAP alignment correct % | gated 0.9: coverage % | gated 0.9: precision % | gated 0.99: coverage % | gated 0.99: precision % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PARTS_dropped_1 | 4,000 | 31,115 | 50.018 | 78.798 | 44.879 | 91.786 | 11.654 | 96.635 |
| PARTS_dropped_2 | 4,000 | 27,115 | 33.878 | 66.664 | 22.914 | 89.554 | 3.983 | 94.444 |
| PARTS_dropped_3 | 4,000 | 24,704 | 25.441 | 57.355 | 12.431 | 85.998 | 1.477 | 92.603 |
| QUANTITIES_dropped_1 | 4,000 | 35,115 | 44.32 | 75.435 | 36.819 | 94.091 | 8.822 | 97.708 |
| QUANTITIES_dropped_2 | 4,000 | 35,115 | 26.16 | 61.364 | 15.452 | 92.462 | 2.236 | 96.688 |
| QUANTITIES_dropped_3 | 4,000 | 36,704 | 17.123 | 50.308 | 6.858 | 88.439 | 0.755 | 88.087 |

Real unequal recipes (likelihood diagnostic, mean -log P(quantity bucket | part), nats per part):

- equal-length recipes, positional (aligned reference): 1.5365; posterior-weighted: 1.4822
- unequal recipes, positional prefix pairing: 1.8476; posterior-weighted: 1.4341
- simulated (test split, equal-length recipes corrupted), positional / posterior-weighted: PARTS_dropped_1 1.7172 / 1.4374; PARTS_dropped_2 1.8371 / 1.4051; PARTS_dropped_3 1.8985 / 1.3781; QUANTITIES_dropped_1 1.744 / 1.5147; QUANTITIES_dropped_2 1.8621 / 1.5502; QUANTITIES_dropped_3 1.9111 / 1.5768

compare like with like: positional with positional, posterior-weighted with posterior-weighted (the latter is lower even on aligned recipes because it picks the best-fitting quantity). A real-unequal positional value clearly above the equal-length one means positional pairing fits the unequal recipes worse, as in the simulation; it is a likelihood diagnostic, not a pairing accuracy.

## Limits

- No ground truth exists for any Food.com pairing; the simulation corrupts equal-length recipes, so it measures the method on the corruption it assumes.
- The model sees only the magnitude bucket of the quantity and the food name; it never sees a unit (there is none).
- A human spot-check of 100 aligned pairs per rule would be the first real accuracy estimate (not done).
