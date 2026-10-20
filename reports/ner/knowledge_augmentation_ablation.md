# Knowledge-augmentation ablation (TASTEset DEV, deberta-base+CRF, 5 seeds, rule: promote only if +0.003 micro F1 with paired CI excluding 0)
| variant | DEV micro | delta vs K0 | CI95 | seeds won | delta unseen F1 | decision |
|---|---|---|---|---|---|---|
| K0 base+CRF | 0.9396 | — | — | — | — | MAINLINE |
| K1 definitions | 0.9394 | −0.0002 | [−0.0033, +0.0032] | 2/5 | +0.0104 | REJECT (backflow K0) |
| K2 + train aliases | 0.9383 | −0.0013 | [−0.0048, +0.0019] | 1/5 | +0.0071 | REJECT |
| K3 + non-entity words | 0.9374 | −0.0022 | [−0.0065, +0.0022] | 0/5 | −0.0047 | REJECT |
| K4 contrastive, word-budgeted | 0.9391 | −0.0005 | — | — | — | REJECT (rule-based shortlist) |
Type-specific K-TS (RecipeBERT-KA-style, our reimplementation) is in lane S; it is reported separately and does not reopen K1-K4.
Interpretation: the encoder already captures what these prompts state; unseen-surface F1 moves +0.007–0.010 for K1/K2 but not enough to meet the rule. Not reopened; no K5/K6.
