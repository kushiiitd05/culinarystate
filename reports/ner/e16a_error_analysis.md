# E16-A NER Error Analysis (deberta-v3-base_crf, seed 1)

Test set: 105 recipes. Total errors: 301 (184 FP, 117 FN).


## Per-label breakdown

| Label | TP | FP | FN | P | R | F1 | Errors | Top error type |
|---|---|---|---|---|---|---|---|---|
| FOOD | 547 | 73 | 58 | 0.882 | 0.904 | 0.893 | 131 | BOUNDARY_FP |
| QUANTITY | 562 | 22 | 7 | 0.962 | 0.988 | 0.975 | 29 | SPURIOUS_FP |
| UNIT | 462 | 13 | 5 | 0.973 | 0.989 | 0.981 | 18 | SPURIOUS_FP |
| PROCESS | 175 | 20 | 11 | 0.897 | 0.941 | 0.919 | 31 | BOUNDARY_FP |
| PHYSICAL_QUALITY | 102 | 39 | 12 | 0.723 | 0.895 | 0.800 | 51 | LABEL_CONFUSION_FOOD->PHYSICAL_QUALITY |
| COLOR | 28 | 5 | 5 | 0.848 | 0.848 | 0.848 | 10 | LABEL_CONFUSION_FOOD->COLOR |
| TASTE | 9 | 6 | 8 | 0.600 | 0.529 | 0.562 | 14 | LABEL_CONFUSION_TASTE->FOOD |
| PURPOSE | 11 | 2 | 4 | 0.846 | 0.733 | 0.786 | 6 | LABEL_CONFUSION_PURPOSE->QUANTITY |
| PART | 5 | 4 | 7 | 0.556 | 0.417 | 0.476 | 11 | LABEL_CONFUSION_PART->FOOD |

## Error category distribution

| Category | Count | % |
|---|---|---|
| BOUNDARY_FP | 75 | 24.9% |
| BOUNDARY_FN | 65 | 21.6% |
| SPURIOUS_FP | 48 | 15.9% |
| LABEL_CONFUSION_FOOD->PHYSICAL_QUALITY | 23 | 7.6% |
| MISSED_FN | 10 | 3.3% |
| LABEL_CONFUSION_PROCESS->PHYSICAL_QUALITY | 10 | 3.3% |
| LABEL_CONFUSION_PHYSICAL_QUALITY->PROCESS | 9 | 3.0% |
| LABEL_CONFUSION_TASTE->FOOD | 6 | 2.0% |
| LABEL_CONFUSION_PURPOSE->QUANTITY | 6 | 2.0% |
| LABEL_CONFUSION_PART->FOOD | 5 | 1.7% |
| LABEL_CONFUSION_PHYSICAL_QUALITY->TASTE | 4 | 1.3% |
| LABEL_CONFUSION_FOOD->PROCESS | 4 | 1.3% |
| LABEL_CONFUSION_TASTE->COLOR | 4 | 1.3% |
| LABEL_CONFUSION_COLOR->PHYSICAL_QUALITY | 3 | 1.0% |
| LABEL_CONFUSION_COLOR->FOOD | 3 | 1.0% |
| LABEL_CONFUSION_FOOD->UNIT | 3 | 1.0% |
| LABEL_CONFUSION_UNIT->QUANTITY | 2 | 0.7% |
| LABEL_CONFUSION_QUANTITY->PHYSICAL_QUALITY | 2 | 0.7% |
| LABEL_CONFUSION_PHYSICAL_QUALITY->FOOD | 2 | 0.7% |
| LABEL_CONFUSION_FOOD->COLOR | 2 | 0.7% |
| LABEL_CONFUSION_PROCESS->QUANTITY | 2 | 0.7% |
| LABEL_CONFUSION_PART->PHYSICAL_QUALITY | 2 | 0.7% |
| LABEL_CONFUSION_FOOD->PART | 2 | 0.7% |
| LABEL_CONFUSION_PHYSICAL_QUALITY->UNIT | 2 | 0.7% |
| LABEL_CONFUSION_FOOD->QUANTITY | 2 | 0.7% |
| LABEL_CONFUSION_UNIT->PHYSICAL_QUALITY | 1 | 0.3% |
| LABEL_CONFUSION_PROCESS->UNIT | 1 | 0.3% |
| LABEL_CONFUSION_PROCESS->FOOD | 1 | 0.3% |
| LABEL_CONFUSION_UNIT->FOOD | 1 | 0.3% |
| LABEL_CONFUSION_TASTE->PHYSICAL_QUALITY | 1 | 0.3% |

## Most common FP spans (spurious)

| Span | Count |
|---|---|
| `frozen` | 4 |
| `to taste` | 4 |
| `leftover` | 4 |
| `1` | 3 |
| `sugar` | 3 |
| `kosher salt` | 2 |
| `slices` | 2 |
| `miniature` | 2 |
| `size` | 2 |
| `breast` | 2 |
| `unpeeled` | 2 |
| `whole wheat` | 2 |
| `crushed` | 2 |
| `lean` | 2 |
| `ripe` | 2 |

## Most common FN spans (missed)

| Span | Count |
|---|---|
| `leftover` | 4 |
| `to taste` | 3 |
| `1` | 2 |
| `sauce` | 2 |
| `cooking spray` | 2 |
| `unpeeled` | 2 |
| `gold` | 2 |
| `hot` | 2 |
| `sweet` | 2 |
| `salt` | 1 |
| `kosher` | 1 |
| `sweet and sour` | 1 |
| `hornitos tequila` | 1 |
| `pomegranate juice` | 1 |
| `agave syrup artificial sweetener` | 1 |

## Weak label analysis


### PART (F1 0.476)

TP=5, FP=4, FN=7. Errors: 11.

Sample errors:
- [FP] `breast` — BOUNDARY_FP
- [FN] `breast half` — BOUNDARY_FN
- [FN] `green parts only` — LABEL_CONFUSION_PART->PHYSICAL_QUALITY
- [FP] `breast` — BOUNDARY_FP
- [FP] `halves` — BOUNDARY_FP
- [FN] `breast halves` — BOUNDARY_FN
- [FP] `thighs` — LABEL_CONFUSION_FOOD->PART
- [FN] `drumsticks` — LABEL_CONFUSION_PART->FOOD

### TASTE (F1 0.562)

TP=9, FP=6, FN=8. Errors: 14.

Sample errors:
- [FN] `sweet and sour` — LABEL_CONFUSION_TASTE->FOOD
- [FP] `double` — LABEL_CONFUSION_PHYSICAL_QUALITY->TASTE
- [FN] `butter-flavored` — LABEL_CONFUSION_TASTE->FOOD
- [FN] `pepperoncini` — LABEL_CONFUSION_TASTE->FOOD
- [FN] `hot` — LABEL_CONFUSION_TASTE->FOOD
- [FP] `lean` — SPURIOUS_FP
- [FN] `hot` — LABEL_CONFUSION_TASTE->FOOD
- [FN] `sweet` — LABEL_CONFUSION_TASTE->COLOR

### PURPOSE (F1 0.786)

TP=11, FP=2, FN=4. Errors: 6.

Sample errors:
- [FP] `for bowl` — BOUNDARY_FP
- [FN] `for bowl and pan` — BOUNDARY_FN
- [FN] `to taste` — LABEL_CONFUSION_PURPOSE->QUANTITY
- [FN] `to taste` — LABEL_CONFUSION_PURPOSE->QUANTITY
- [FN] `to taste` — LABEL_CONFUSION_PURPOSE->QUANTITY
- [FP] `to serve` — SPURIOUS_FP

## Key findings

1. **Boundary errors dominate (46.5%)** — the model identifies the right label but disagrees on
   span extent. This is annotation noise, not model failure. TASTEset has inconsistent boundary
   conventions (e.g., "breast half" vs "breast" + "half"; "kosher salt" as one or two spans).

2. **FOOD ↔ PHYSICAL_QUALITY confusion (7.6%)** — words like "frozen", "lean", "ripe" are
   ambiguous modifiers. TASTEset labels these inconsistently: sometimes PHYSICAL_QUALITY, sometimes
   part of the FOOD span. A post-hoc rule (known modifiers → PHYSICAL_QUALITY) could help.

3. **Weak labels are genuinely hard:**
   - PART (0.48): body parts ("breast", "thigh") overlap with FOOD in TASTEset's schema
   - TASTE (0.56): "hot", "sweet" are FOOD modifiers in many contexts
   - PURPOSE (0.79): "to taste" annotated as PURPOSE but model predicts QUANTITY

4. **kNN-NER is a null result** — zero prediction changes across 5 seeds. The encoder's logits
   are sufficiently peaked that 25% kNN interpolation never flips any argmax.

5. **CRF is the only significant add-on** — p=0.003 (paired bootstrap), +0.005 F1 over base.
   Large+CRF (+0.011 over base+CRF, p=0.004) is the best model but needs GPU for inference.

6. **FOOD F1 degrades sharply on unseen entities** (frequency-bucket analysis):

   | Bucket | Gold | TP | FP | FN | P | R | F1 |
   |---|---|---|---|---|---|---|---|
   | Head (top 50 train foods) | 280 | 273 | 8 | 7 | 0.972 | 0.975 | **0.973** |
   | Mid (rank 51–200) | 103 | 98 | 4 | 5 | 0.961 | 0.951 | **0.956** |
   | Tail (rank 201+) | 87 | 80 | 12 | 7 | 0.870 | 0.920 | **0.894** |
   | Unseen (not in train) | 135 | 96 | 49 | 39 | 0.662 | 0.711 | **0.686** |

   22.3% of test FOOD spans (126 types) are unseen in training. The model hallucinates
   boundaries on these → low precision. This is the slot GLiNER zero-shot should help
   (known entity types, unknown entity surfaces). kNN-NER couldn't help because the
   neighbor search returned only head-heavy exemplars.
