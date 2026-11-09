# SYNTHETIC_FIXTURE_NOT_A_RESULT: D5 scoring harness, synthetic fixture run

**SYNTHETIC_FIXTURE_NOT_A_RESULT.** Invented data (tests/fixtures/d5_synthetic, manifest-hashed). These numbers test the harness; they are not D5 results and say nothing about any rung.

Tool `s178-d5-score-0.1.0-draft`; harness `d5_scoring@0.1`, `d4_metrics@0.1`, `ablation@0.1`, `frozen_guard@0.1`.

## Router branch accuracy (T8-C01-R1)

accuracy 14/16 = 0.875 (CP95 [0.6165, 0.9845]); status OK; X controls 1/2

## H1 (exact two-sided McNemar)

verdict RULE_NOT_MET (not supported at this n); gold label INDEPENDENT_GOLD
- B4_vs_B1: b 5 / c 0, p 0.0625, diff 0.8333 (Newcombe [0.2767, 0.9699]): cannot be significant at this n: 5 discordant pairs < 6
- B4_vs_B2: b 5 / c 0, p 0.0625, diff 0.8333 (Newcombe [0.2767, 0.9699]): cannot be significant at this n: 5 discordant pairs < 6

## H3 (independent scorer; all options, the lock picks one)

- H3-B|one-sided: meets rule = False; b 4 / c 1, p 0.1875: not shown at this n
- H3-A|one-sided: meets rule = False; b 4 / c 1, p 0.1875: not shown at this n
- H3-B|two-sided: meets rule = False; b 4 / c 1, p 0.375: cannot be shown at this n: 5 discordant questions < 6
- H3-A|two-sided: meets rule = False; b 4 / c 1, p 0.375: cannot be shown at this n: 5 discordant questions < 6
- H3-C: meets rule = False; bootstrap upper95 0.19047619047619047

## D4 risk-coverage (primary score), decision-layer rungs

- B5T: QUANTITATIVE cov 0.4286 risk 0/3; INTERVAL cov 0.5714 risk 0/4; QUALITATIVE cov 0.7143 risk 0/5; ABSTAIN cov 1.0 risk 0/7
- B7: QUANTITATIVE cov 0.4286 risk 1/3; INTERVAL cov 0.5714 risk 1/4; QUALITATIVE cov 0.7143 risk 1/5; ABSTAIN cov 1.0 risk 1/7

## Retrieval Recall@K (pooled P1+P2+C)

- B0: NA_NO_RETRIEVAL_LIST
- B2: n 5; R@1 0.45 (compat 0.45); R@3 0.7 (compat 0.7); R@5 0.8 (compat 0.7); R@10 0.8 (compat 0.7); MRR 0.65 (EXPLORATORY)
- B5: NA_NO_RETRIEVAL_LIST
- B5T: NA_NO_RETRIEVAL_LIST
- B7: n 5; R@1 0.85 (compat 0.85); R@3 1.0 (compat 0.9); R@5 1.0 (compat 0.9); R@10 1.0 (compat 0.9); MRR 1.0 (EXPLORATORY)

## C block, OOD abstention, enforcement

- C B0: agreement 0/2, cannot separate 0/2, wrong order 0, unresolved 2
- C B2: agreement 1/2, cannot separate 0/2, wrong order 0, unresolved 1
- C B5: agreement 0/2, cannot separate 0/2, wrong order 0, unresolved 2
- C B5T: agreement 2/2, cannot separate 1/2, wrong order 0, unresolved 0
- C B7: agreement 2/2, cannot separate 1/2, wrong order 0, unresolved 0
- OOD B0: P3 abstain 0/2; false abstain P1+P2 0/3
- OOD B2: P3 abstain 1/2; false abstain P1+P2 0/3
- OOD B5: P3 abstain 1/2; false abstain P1+P2 0/3
- OOD B5T: P3 abstain 2/2; false abstain P1+P2 0/3
- OOD B7: P3 abstain 2/2; false abstain P1+P2 0/3
- enforcement B7: removed 2 sentences, fallback 2/7, mean words 10.71

## Ablations (EXPLORATORY, descriptive)

- state reconstruction: RUN (errors added 0, removed 0)
- quantity grounding: NOT_RUN (no quantity-grounding switch in the D5 answer path)
- structured retrieval: NOT_RUN (B3 (structured metadata RAG) is not built)
- evidence compatibility: RUN (errors added 1, removed 0)
- conflict/lineage processing: NOT_RUN (no switch separates conflict / lineage handling from the packet builder)
- transition fallback: NOT_RUN (B6 (Level-15 transition fallback) is not built)
- uncertainty/OOD gate: RUN (errors added 1, removed 0)
- feasibility filtering: NOT_RUN (not in the board's cheap subset)
- provenance/claim ledger: RUN (errors added 1, removed 0)

Full detail: `SYNTHETIC_FIXTURE_d5_scoring_result.json` (every section carries `prereg_status`).
