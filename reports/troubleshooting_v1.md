# Troubleshooting candidates v1 (RQ16-18/19 proposer evidence)

- documents scanned: {'GUTENBERG-PD': 73778, 'WIKIBOOKS-COOKBOOK': 4757}; statements: 1,881 (CAUSE 169, PREVENTION 1,379, RECOVERY 333)
- distinct (relation, failure, text) keys: 1,689; with support ≥ 2 sources: 126
- registry CSV carries Gutenberg (public domain) text only; Wikibooks text stays local (CC BY-SA).
- candidates, not verified causes; precision sample in data/interim/troubleshooting/precision_sample.jsonl
- AI-judged precision on fresh random samples (not human verification): 37/40 (mixed, seed 7); 17/20 RECOVERY before noise filter; 26/30 strict / 28/30 lenient (mixed, seed 23). Known noise: condition spans from unrelated if-clauses, vague actions.

| failure   |   CAUSE |   PREVENTION |   RECOVERY |
|:----------|--------:|-------------:|-----------:|
| BOIL_OVER |       0 |            0 |          1 |
| BURN      |      29 |          637 |         30 |
| CRACK     |      25 |           22 |          7 |
| CURDLE    |      17 |           98 |         21 |
| GRAINY    |       1 |            2 |          2 |
| HEAVY     |       5 |           13 |          0 |
| LUMPY     |       5 |          115 |          7 |
| OILY      |       1 |            4 |          2 |
| SEIZE     |       0 |            0 |          2 |
| SINK      |      25 |           81 |         14 |
| SOGGY     |       0 |            5 |          1 |
| SPLIT     |      26 |           16 |         17 |
| STICK     |      17 |          349 |         39 |
| TOO_DRY   |       2 |            8 |         30 |
| TOO_SALTY |       1 |            3 |          6 |
| TOO_THICK |       2 |            3 |        120 |
| TOO_THIN  |       1 |            1 |         31 |
| TOUGH     |      11 |           22 |          3 |
| TURN      |       1 |            0 |          0 |
