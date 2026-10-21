# Fresh linker / NIL evaluation set (V2-DM Track C) -- protocol, written before any label exists

Purpose: the `unseen_alias` / `unseen_concept` sets were viewed during development, so the final v2 linker claim needs genuinely fresh evidence. TEV-LINK-v0 is frozen (`TEV_LINK_v0_freeze.json`); nothing about prompts, K, scoring or thresholds may change after this set is opened.

## 1. Sampling frame (built: `tools/v2dm_fresh_set_build.py`, local-only output, frame sha256 prefix 9fb8075bee67cbf0)
Source: FOOD/NAME **gold mentions of the TASTEset and RecipeDB3 CALIBRATION splits** (not used for linker selection; v1 TEST not used), deduplicated by normalised surface; every surface of the viewed linker sets (dev_alias, unseen_alias, dev, unseen_concept) is excluded. Deterministic hash order per stratum.
| Stratum (rule, priority order) | target | selected |
|---|---|---|
| S1 exact gallery surface (known concepts; regression check) | 60 | 60 |
| S5 regional / multilingual | 40 | **1** (benchmarks contain almost no regional tokens) |
| S4 ambiguous generic head (head word in >= 8 ledger surfaces) | 60 | 60 |
| S3 head word absent from the ledger (likely novel concept / NIL) | 120 | 120 |
| S6 long qualified mention (>= 3 tokens, head known) | 40 | 40 |
| S2 alias-like (head in ledger, surface not) | 160 | 160 |
Total 441 (RecipeDB3 394, TASTEset 47). **Known gap:** regional/multilingual aliases are not represented; filling S5 needs new text (the RecipeDB regional API pool, amendment A3) and is recorded as a limitation until then. Head vs tail is analysed post hoc from train frequency, not sampled.

## 2. Labelling (human; no AI labels)
Kush and Parv label **independently** (blank identical sheets, not shared until both finish): for each mention + its context line, choose the ledger concept from a **pooled, shuffled candidate list** = union of top-5 of BGE, E5, the cross-encoder and the Tev1-4B choice (pooling is generated **after** every system is frozen and has scored the mentions, so no system sees labels), plus options: NONE of these (type the ingredient name if known) / ambiguous (name the readings). Cohen's kappa and adjudication reported; disagreements adjudicated jointly; ambiguous items kept as a separate stratum, not forced. Estimated effort about 25 s per mention, about 3 h each for 441.

## 3. Freeze and single use
Freeze manifest (written before labels are opened): frame hash, sampled-id hash, TEV-LINK-v0 manifest hash, BGE/E5/cross-encoder/Nimble configurations, calibrated NIL thresholds (from DEV sets only), metrics list. Then **one** scoring run: L0 BGE top-1, L1 E5 top-1, L2 conventional cross-encoder (same candidates), L3 Tev1-4B, L4 Nimble, L5 calibrated BGE NIL, L6 decision-model NONE probability, L7 calibrated combination; TOP5_ORACLE; reranker efficiency = (acc - top1) / (top5_oracle - top1); retrieval-failure vs reranking-failure decomposition; NIL AUROC/AUPRC, NIL recall, false-NONE rate; head/tail/ambiguous strata; latency and memory. Paired bootstrap over mentions. No change after opening; issues become limitations.
