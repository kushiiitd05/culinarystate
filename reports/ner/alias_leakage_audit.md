# Alias / concept leakage audit (S119, design contract D.7)

Verdict: **ALLOWED_AS_EXTERNAL_GAZETTEER**

- Ledger surfaces (ING canonical + ALIAS, normalised): 2725
- Records whose provenance/crosswalks mention the benchmark corpora: 0
- Provenance: {'ING:a1_ner+registry_build': 1951, 'ING:wikibooks_links': 97, 'ALIAS:a1_ner+registry_build': 2052, 'ALIAS:off_taxonomy': 1896, 'ALIAS:wikibooks_links': 155}

| split | gold FOOD/NAME spans | ledger exact cover | unseen spans | cover of unseen | tail spans | cover of tail |
|---|---|---|---|---|---|---|
| tasteset:dev | 618 | 0.7071 | 144 | 0.375 | 128 | 0.5859 |
| tasteset:calibration | 377 | 0.6764 | 102 | 0.2647 | 64 | 0.5938 |
| recipedb3:dev | 2938 | 0.4568 | 784 | 0.0408 | 488 | 0.2398 |
| recipedb3:calibration | 2940 | 0.4595 | 798 | 0.0414 | 488 | 0.291 |

TEST surfaces were not inspected. Coverage is an upper bound on what an external gazetteer could contribute.

Conditions: use only for features/calibrator, ablated with and without (feature removed -> measure); never include test surfaces when building or filtering the gazetteer; re-run this audit if the ledgers are rebuilt from any new corpus
