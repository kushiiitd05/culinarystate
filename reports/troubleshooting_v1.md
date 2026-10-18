# Troubleshooting candidates v1 (RQ16-18/19 proposer evidence)

- documents scanned: {'GUTENBERG-PD': 73778, 'WIKIBOOKS-COOKBOOK': 4757}; statements: 1,831 (CAUSE 116, PREVENTION 1,388, RECOVERY 327)
- distinct (relation, failure, text) keys: 1,644; with support ≥ 2 sources: 121
- registry CSV carries Gutenberg (public domain) text only; Wikibooks text stays local (CC BY-SA).
- candidates, not verified causes; precision sample in data/interim/troubleshooting/precision_sample.jsonl
- AI-judged precision on fresh random samples (not human verification): 37/40 (mixed, seed 7); 17/20 RECOVERY before noise filter; 26/30 strict / 28/30 lenient (mixed, seed 23). Known noise: condition spans from unrelated if-clauses, vague actions.
- v1.1 filters (2026-10-18): 'separately', 'if preferred', doneness signals ('sinks when done'), medical text; 'unless X' / 'less liable to … if X' -> PREVENTION; cause span stops at the clause comma. Fresh sample seed 31: 28/30 before the medical filter (both misses medical, now filtered). Multi-source CAUSE keys 9 -> 3.

| failure   |   CAUSE |   PREVENTION |   RECOVERY |
|:----------|--------:|-------------:|-----------:|
| BOIL_OVER |       0 |            0 |          1 |
| BURN      |      23 |          639 |         29 |
| CRACK     |      17 |           23 |          7 |
| CURDLE    |      13 |          100 |         21 |
| GRAINY    |       1 |            2 |          2 |
| HEAVY     |       5 |           13 |          0 |
| LUMPY     |       4 |          115 |          7 |
| OILY      |       1 |            4 |          2 |
| SEIZE     |       0 |            0 |          1 |
| SINK      |      21 |           83 |         14 |
| SOGGY     |       0 |            5 |          1 |
| SPLIT     |      10 |           17 |         11 |
| STICK     |       8 |          351 |         41 |
| TOO_DRY   |       2 |            8 |         30 |
| TOO_SALTY |       0 |            3 |          6 |
| TOO_THICK |       2 |            2 |        120 |
| TOO_THIN  |       1 |            1 |         31 |
| TOUGH     |       7 |           22 |          3 |
| TURN      |       1 |            0 |          0 |
