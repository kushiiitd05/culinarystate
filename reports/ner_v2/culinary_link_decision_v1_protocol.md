# CulinaryLinkDecision-v1 -- pre-registration (written and committed BEFORE any teacher label or student is produced)

## 0. Frozen premise (V2-LINK-B, closed evidence)
Fresh human gold (441 items, sealed, never used for training or development). Strict View-A Acc@1: BGE 0.796, E5 0.817, cross-encoder 0.649, **Tev1-4B 0.901**, Nimble 0.874; Tev - BGE +0.105 [0.058, 0.152]; Nimble - Tev -0.026 [-0.063, +0.010]. Claim status: **V2-LINK-B** -- strong/Pareto-useful semantic decision reranking; concept-choice superiority established; NIL superiority NOT established (AUROC +0.031 [-0.007, +0.070]); not upgraded to A. Tev1-4B stays the teacher (predeclared primary, smaller/faster, no significant Nimble advantage).

## 1. Hypothesis
A compact local student (<< 4B parameters) trained on legitimate TRAIN-side candidate-decision data recovers most of Tev's candidate-selection gain over BGE; and Tev distillation adds value beyond gold supervision alone.

## 2. Data (TRAIN / OOF / DEV only; never the 441 gold, TASTEset/RecipeDB3 TEST, or any sealed label)
Source: ingredient ledger surfaces in `features/linker_data_v2.json` (TRAIN concept bucket: 1,446 concepts). **Concept- and alias-grouped 5-fold OOF candidate generation:** for fold k, a BGE-large retriever (frozen v2 recipe: lr 1e-5, 4 epochs, cls pool, seed 1) is trained on TRAIN queries excluding (i) every surface of the concepts assigned to fold k and (ii) the aliases assigned to alias-fold k; the gallery excludes the same surfaces. Fold-k examples: **positives** = alias-fold-k aliases of concepts that remain in the gallery (gold = their concept); **NIL** = all surfaces of fold-k held-out concepts (gold = NONE). Candidates = top-K (K=10, truncated to 5 for the primary) from that fold's retriever; candidate aliases are shown from the fold gallery only (the query's own surface never appears). Fold assignment by SHA-256 of concept id / (alias, concept). DEV = existing `dev_alias` (61) + `dev` NIL (252) of linker_data_v2 with the frozen full-train BGE candidates (concept-disjoint from TRAIN). `unseen_alias`/`unseen_concept` are viewed report-only sets and are not used for selection.
PARENT: retained only where the ledger/gold supplies it (TRAIN-side data has none); not synthesised.

## 3. Teacher (frozen): `TEV-LINK-v0` unchanged (tev1:4b, same prompt/ordering/NONE definition, deterministic settings). Saved as `TEV_TEACHER_RAW`: chosen option, probability of each option and of NONE, margin, entropy; **never treated as calibrated or as ground truth**; only a soft signal.

## 4. Students (all smaller than Tev1-4B)
- **CD-L0** structured baseline: gradient-boosted classifier over per-candidate features (BGE score, rank, margin to next, exact/token-overlap with candidate names/aliases, lengths, candidate-set size, E5-free); no text encoder. Purpose: how much of the gain is explainable without text reasoning.
- **CD-L1** text-aware cross-encoder (`BAAI/bge-small-en-v1.5`, ~33M parameters): scores (mention, candidate text) for each candidate and a learned NONE option, softmax over K+1; gold supervision only.
- **CD-L2** same architecture and budget as CD-L1, loss `L = L_gold + lambda * KL(teacher || student)` over the K+1 options (teacher temperature-softened; lambda chosen on DEV from {0.3, 1.0}); no calibration loss at this stage.
Seeds: 3 per student (1-3); budget identical across CD-L1/CD-L2.

## 5. Ablations (DEV only)
(a) **Distillation:** CD-L2 vs CD-L1 -- if CD-L2 does not beat CD-L1 (paired, CI), the distillation claim is rejected even if the student works. (b) **K:** 5 vs 10. (c) **NIL design:** NONE as an option (primary) vs a separate NIL head (secondary, if time). (d) **Context:** mention-only is the primary; mention + sentence context **cannot be trained or evaluated with gold** because no legitimate gold-labelled mentions-in-context exist outside the sealed set -> the context ablation is deferred to the next dataset (stated limitation, not silently dropped).

## 6. Metrics and statistics
Primary: strict and lenient Acc@1 on DEV positives (View A, forced choice), Recall@K, MRR, paired bootstrap gains over BGE top-1 and the zero-shot cross-encoder, CD-L2 vs CD-L1; latency (ms per mention, batch 1) and memory. Secondary: NIL AUROC/AUPRC, NIL recall, false-NONE rate, by head/tail, qualified vs short mentions. Candidate-pool oracle reported separately. Small DEV (n=61) is acknowledged: decisions use paired intervals and are marked provisional until the new sealed set.

## 7. Promotion gate
D1: student reproduces most of Tev's gain over BGE (DEV strict Acc@1 >= 95% of Tev's DEV Acc@1 and paired gain over BGE with lower bound > 0) at materially lower latency/memory. D2: improves over BGE but loses too much of Tev's gain. D3: no reproduction of the decision-model gain. A DEV-level D1 only selects the student to freeze; the claim needs a **new independent, sealed human evaluation set designed after the student and hyper-parameters are frozen**, with explicit acceptable-concept sets for ambiguous items and deliberate regional/multilingual coverage (RecipeDB regional API pool if legitimately available).

## 8. Rules
No use of the 441 gold or any TEST; no tuning on viewed sets; Tev teacher unchanged; v1 NER untouched; any deviation = dated amendment.
