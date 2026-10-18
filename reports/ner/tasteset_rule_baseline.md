# TASTEset — rule baseline (X10)

TASTEset @ 80bb783f5210 (MIT): 700 recipes, 13,362 gold spans. Rule NER = quantity grammar + closed vocabularies + ING lexicon.

| label | exact P | exact R | exact F1 | relaxed F1 |
|---|---|---|---|---|
| COLOR | 0.8391 | 0.8355 | 0.8373 | 0.859 |
| FOOD | 0.7824 | 0.7264 | 0.7534 | 0.9518 |
| PART | 0.5233 | 0.8182 | 0.6383 | 0.7234 |
| PHYSICAL_QUALITY | 0.6776 | 0.4691 | 0.5544 | 0.5902 |
| PROCESS | 0.8023 | 0.7067 | 0.7515 | 0.847 |
| PURPOSE | 0.4808 | 0.7979 | 0.6 | 0.608 |
| QUANTITY | 0.8672 | 0.8138 | 0.8396 | 0.9603 |
| TASTE | 0.656 | 0.6508 | 0.6534 | 0.6853 |
| UNIT | 0.9842 | 0.7683 | 0.863 | 0.8637 |
| micro | 0.8406 | 0.7462 | 0.7906 | 0.8977 |
| macro F1 | | | 0.7212 | 0.7876 |

Test split only (105 recipes, same split as encoder runs): micro exact F1 0.7738 (95% CI 0.7392–0.8076), relaxed 0.8953
