# D5 leakage audit: findings (S178, T9-C09-R2)

Status: AI_DRAFTED, counts only, nothing frozen or approved (D-071). Numbers come from `reports/s178/leakage_audit_d5.json`
(`tools/s178_leakage_audit_d5.py`, module `src/culinarystate/evaluation/leakage_audit_d5.py`). The D5 benchmark is still a draft
(40 S questions, 60 P/C cells); every count must be re-run when the frozen benchmark exists.

## S blocks: 40 questions, 40 distinct recipes (S1 20, S2 20)

| # | Check | Result | Reading |
|---|---|---|---|
| S-1 | S recipes vs the 50 gold recipes, their duplicate groups and recipe families | 0 / 0 / 0 | Clean. The identity ledger is provisional (star clustering, uncalibrated): absence there is weak evidence |
| S-2 | S recipes vs 7 seeded Rung A dev / census samples re-derived from their seeds (20261104 x3 subsets, dryrun-2026-11-04, d073 exploration and precision, router-demo) | 0 overlaps in all 7; expected by chance 0.03-0.27 | Clean. Every seed string was confirmed by the sha256 recorded in committed reports (1-33 reports each). The D-074 R1 precision pool is 400 recipes; the 60 labelled items are a subset, so this is pool-level |
| S-3 | S recipes vs the J4 sample (hashed ids) | 0 of 68 | Clean |
| S-4 | S recipes vs NER training data | no S recipe is in TASTESET; only 2 S recipes have ingredient lines (9 lines). Exact normalised line matches: RecipeDB3 train 1, test 1, dev 0, calibration 0; TASTEset 2 (lines of 2 and 4 tokens) | Low risk, and the 38 Gutenberg recipes have no ingredient lines, so the test has no denominator for them. Rung A does not use the trained NER |
| S-5 | S1 gold ING ids (54) and P/C question ING ids (39) vs the linker concept split (tools/build_linker_data.py buckets) | S1 gold: 40 train, 7 dev, 7 test. P/C: 23 train, 6 dev, 10 test | Exposure of the id space only. The S1 scorer links with the rule-based lexicon, not the learned linker; if a learned linker is ever used for scoring, report by bucket |
| S-6 | Tracked files outside the D5 draft that name an S recipe id | 6 files: `registry/recipes/gutenberg_ingredient_links_v1.csv` (38 S recipes) and `wikibooks_ingredient_links_v1.csv` (2) hold the ledger-build recipe-to-ING links of all 40 S recipes; the surface-form registries and the troubleshooting candidates list at most 3 example ids per form (5, 3, 1 and 1 S ids) | Not a tuning pool, but note two things. (a) The ingredient-link registries are text-linker output for exactly these recipes: no rung context or scorer may read them (they would hand over ING ids). (b) Rung A rules and lexicon were written against corpus-wide counts that include these recipes, and every S recipe sits inside the full-corpus label-free census runs; census and binding code was adjusted after reading those counts (D-073). Rung A is not blind to this kind of text |
| S-7 | Composition | 38 of 40 recipes are Gutenberg segments, 2 Wikibooks; 38 of 40 carry no ingredient lines | **MEDIUM.** The draft is 95 % nineteenth-century step prose. H1 can only be stated for that text type. The prereg says "Wikibooks and Gutenberg"; a family floor is a human decision |

Not measured, and not claimable: near-duplicate or edition-level duplicates between S recipes and the rest of the corpus beyond the
provisional identity ledger; pre-training contamination of the generator LLM (Gutenberg and Wikibooks text is public, so B0 may
reproduce it from memory; there is no way to test that from here). Label every recipe-level H1 result "source-family-disjoint
not verified; near-duplicate leakage not controlled" (consensus T9-C09-R3).

## P / C blocks: 60 cells, 101 distinct gold EVD rows (P1 29, P2 29, C 57 with overlaps; P3 has none)

| # | Check | Result | Reading |
|---|---|---|---|
| PC-1 | Gold rows vs the DEL-2 / 29-diag pool (all ACTIVE retention rows, seed-7 splits) | 101 of 101 in the pool. Roles of the gold rows under random / pair-holdout / matrix-disjoint / process-disjoint: train 59 / 71 / 70 / 65, calibration 14 / 13 / 17 / 15, test 28 / 17 / 14 / 21 | **HIGH for any learned-model claim; none for the lookup rungs.** DEL-2 trained and scored on every gold row. B5 / B7 read EVD rows by lookup, so no training leakage reaches them, but a DEL-2 model (or a 29-diag number) offered as validation of these cells is exposed. Any learned rung on D5 needs these cells held out |
| PC-2 | Gold rows vs the retrieval silver set (600 templated cell queries, seed 20261018, reproduced; BM25 top-100 identical for 30 of 30 checked queries) | 2 of 101 gold rows are silver-relevant rows (both P2); 1 of 61 gold cells is a silver query cell; but 20 of 65 D5 (ingredient, process) pairs occur in silver-relevant rows | **MEDIUM.** Row-level overlap is tiny. The (ingredient, process) space overlaps, and the retriever choice (BM25 + dense RRF) was made on those pairs. State it; do not claim D5 P/C is untouched by retrieval development |
| PC-3 | P3 (gold ABSTAIN) cells whose ingredient-process pair has rows for another target | 3 of 15 | **LOW.** "Ledger silent" is target-specific; B0 / B2 may legitimately know the pair. Keep the P3 wording as "no evidence for this target" |
| PC-4 | D5 P/C question text vs the 20 DEV ladder questions | 0 exact matches | Clean (the prereg says the ladder is not reused) |

## Related findings from the registry build (`reports/s178/split_registry_report.json`)

- 29-diag S-1..S-4 pre-seal splits are byte-identical to the DEL-2 splits (same seed 7, same rows, split hashes equal the DEL-2 reports'). They are a rerun, not new held-out data; the prereg already labels it PRIOR_EXPOSURE_REANALYSIS.
- Independence-group leakage in those splits is complete for USDA-RETN-R6 and BOGNAR-2002 (test share of groups seen in train = 1.0 in S-1..S-4: each is one lineage cluster) and partial for PHENOL-EXPLORER-3.6 (0.49-0.96 except S-5). The prereg text says all splits are grouped by `independence_group`; the runner groups S-2/S-3/S-4 by matrix / process keys.
- The prereg names S-5 "food-group disjoint"; the runner builds `study_disjoint`, which is possible only for PHENOL-EXPLORER-3.6 (USDA and BOGNAR refuse). One of the two must change before the 10 Nov edit lock.
- 5 of the 69 conditions behind the D5 gold rows are in the 07.A-R1 audit packet.

## Recommended actions (PROPOSED; humans decide)

1. Report H1 on S rows as engine self-consistency until the gold is blind-first human gold (`gold_origin` HUMAN_BLIND); use `h1_rungs.independent_context` (pre-cut retrieval, no answer line).
2. Declare the 101 gold EVD rows (and the 61 gold cells) test-only for any learned model; if a DEL-2 model is ever a D5 rung, refit without them.
3. Add one sentence to the D5 report: retrieval development used (ingredient, process) pairs that overlap 20 of 65 D5 pairs.
4. Decide a family floor for S recipes (Wikibooks with ingredient lines) before the freeze, or state the Gutenberg-prose scope.
5. Re-run `tools/s178_leakage_audit_d5.py` after the review has dropped / replaced questions and again after the 15a.R seal.
