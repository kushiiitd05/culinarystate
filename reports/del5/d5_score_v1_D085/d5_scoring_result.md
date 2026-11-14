# D5 scoring (frozen benchmark)

Freeze D5-BENCH-2026-11-10b; files {"benchmark/d5/d5_benchmark_v1_D085_PC.csv": "829bce2e13a25f67bd0c01f5e40b1e7f676a5a8792d09ae216094ac89c9783b0", "benchmark/d5/d5_benchmark_v1_D085_S.csv": "74d256ba046fcb664afee6d1bf14b9affbd8ff0245dc30541e7d7dd0068b4404", "benchmark/d5/d5_benchmark_v1_D085_UX.csv": "0adaa0a28266bdc4c24d5497762e59d1bcf05b87da3e33c5c75f7d3866eb9eaf", "benchmark/d5/d5_relatives_v1_D085.json": "cf19acb7fe9fc1d849c83c0a3bd24cc08a554c0147e6385484824819a1076ce0", "ledgers/data/EVD.jsonl": "5b3b1939c7993283dd3ee9083a5e418b4aa550fdebf10d982f297d39d0fc2c56"}; runs sha256 e796be568c1a7bf3f29745cdc9b2ab29f6a91e3f76239078dca9e029e023db2e.
Label: MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers.

## Router branch accuracy (T8-C01-R1)

accuracy 6/10 = 0.6 (CP95 [0.2624, 0.8784]); status INCOMPLETE_GOLD_BRANCH; X controls 4/5

## H1 (exact two-sided McNemar)

verdict NOT_COMPUTED (None); gold label CIRCULAR_SELF_CONSISTENCY_ONLY
- B4_vs_B1: BLOCKED_UNRESOLVED_OR_MISSING
- B4_vs_B2: BLOCKED_UNRESOLVED_OR_MISSING

## H3 (independent scorer; all options, the lock picks one)

- H3-B|one-sided: meets rule = False; b 16 / c 0, p 0.0: B7 better (p <= 0.05)
- H3-A|one-sided: meets rule = False; b 16 / c 0, p 0.0: B7 better (p <= 0.05)
- H3-B|two-sided: meets rule = False; b 16 / c 0, p 0.0: B7 better (p <= 0.05)
- H3-A|two-sided: meets rule = False; b 16 / c 0, p 0.0: B7 better (p <= 0.05)
- H3-C: meets rule = False; bootstrap upper95 -0.2741367159971811

## D4 risk-coverage (primary score), decision-layer rungs

- B5: QUANTITATIVE cov 0.45 risk 12/18; INTERVAL cov 0.75 risk 18/30; QUALITATIVE cov 0.975 risk 27/39; ABSTAIN cov 1.0 risk 28/40
- B5T: QUANTITATIVE cov 0.45 risk 0/18; INTERVAL cov 0.75 risk 2/30; QUALITATIVE cov 0.975 risk 5/39; ABSTAIN cov 1.0 risk 5/40
- B7: QUANTITATIVE cov 0.45 risk 2/18; INTERVAL cov 0.75 risk 4/30; QUALITATIVE cov 0.975 risk 13/39; ABSTAIN cov 1.0 risk 14/40

## Retrieval Recall@K (pooled P1+P2+C)

- B0: NA_NO_RETRIEVAL_LIST
- B2: n 20; R@1 0.2 (compat 0.0); R@3 0.3417 (compat 0.0); R@5 0.375 (compat 0.0); R@10 0.375 (compat 0.0); MRR 0.3417 (EXPLORATORY)
- B5: NA_NO_RETRIEVAL_LIST
- B5T: NA_NO_RETRIEVAL_LIST
- B7: NA_NO_RETRIEVAL_LIST

## C block, OOD abstention, enforcement

- C B0: agreement 0/10, cannot separate 0/10, wrong order 0, unresolved 10
- C B2: agreement 0/10, cannot separate 0/10, wrong order 0, unresolved 10
- C B5: agreement 9/10, cannot separate 10/10, wrong order 0, unresolved 0
- C B5T: agreement 9/10, cannot separate 10/10, wrong order 0, unresolved 0
- C B7: agreement 9/10, cannot separate 10/10, wrong order 0, unresolved 0
- OOD B0: P3 abstain 0/10; false abstain P1+P2 0/20
- OOD B2: P3 abstain 3/10; false abstain P1+P2 4/20
- OOD B5: P3 abstain 0/10; false abstain P1+P2 1/20
- OOD B5T: P3 abstain 8/10; false abstain P1+P2 1/20
- OOD B7: P3 abstain 0/10; false abstain P1+P2 0/20
- enforcement B7: removed 10 sentences, fallback 2/40, mean words 21.95

Full detail: `d5_scoring_result.json` (every section carries `prereg_status`).
