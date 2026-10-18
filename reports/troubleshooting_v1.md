# Troubleshooting candidates v1 (RQ16-18/19 proposer evidence)

- documents scanned: {'GUTENBERG-PD': 73778, 'WIKIBOOKS-COOKBOOK': 4757}; statements: 1,676 (CAUSE 173, PREVENTION 1,344, RECOVERY 159)
- distinct (relation, failure, text) keys: 1,514; with support ≥ 2 sources: 105
- registry CSV carries Gutenberg (public domain) text only; Wikibooks text stays local (CC BY-SA).
- candidates, not verified causes; precision sample in data/interim/troubleshooting/precision_sample.jsonl

| failure   |   CAUSE |   PREVENTION |   RECOVERY |
|:----------|--------:|-------------:|-----------:|
| BURN      |      29 |          635 |          7 |
| CRACK     |      25 |           21 |          4 |
| CURDLE    |      17 |           97 |         14 |
| GRAINY    |       1 |            2 |          0 |
| HEAVY     |       5 |            8 |          0 |
| LUMPY     |       6 |          115 |          3 |
| OILY      |       1 |            4 |          1 |
| SINK      |      26 |           74 |          8 |
| SOGGY     |       0 |            5 |          0 |
| SPLIT     |      27 |           13 |          4 |
| STICK     |      17 |          341 |         13 |
| TOO_DRY   |       3 |            8 |         17 |
| TOO_SALTY |       1 |            3 |          5 |
| TOO_THICK |       2 |            3 |         66 |
| TOO_THIN  |       1 |            1 |         17 |
| TOUGH     |      11 |           14 |          0 |
| TURN      |       1 |            0 |          0 |
