# CulinaryNER-KF v1 -- final TEST report and A-N closeout

Frozen before TEST: `test_freeze_manifest.json` (commit 4ee0582). TEST was evaluated once (`tools/final_test_eval.py`, raw `_final_test.json`); no threshold, calibrator, stratum, feature, linker or checkpoint choice was changed afterwards. Disclosures: TASTEset TEST aggregates of E0 models were viewed once at E0 (recorded in the contract); linker held-out alias/concept sets were viewed during development as report-only sets. Hypothesis status: RESEARCH HYPOTHESIS; no SOTA wording.

## TASTEset -- TEST (105 docs, 2078 predicted spans, span accuracy 0.9249)

### Span quality (exact match unless stated; mean ± sd over seeds)

| System | seeds | exact micro F1 | exact macro F1 | relaxed micro F1 | boundary err | type err | train min | peak GPU GB |
|---|---|---|---|---|---|---|---|---|
| PRIMARY deberta-base+CRF | 5 | 0.9371 ± 0.0024 | 0.8772 ± 0.0122 | 0.9610 ± 0.0005 | 0.0268 ± 0.0031 | 0.0192 ± 0.0011 | 2.4 | 3.6 |
| FROZEN ACCURACY/COMPUTE CHALLENGER deberta-v3-large+CRF | 5 | 0.9371 ± 0.0035 | 0.8667 ± 0.0233 | 0.9610 ± 0.0023 | 0.0257 ± 0.0021 | 0.0177 ± 0.0006 | 3.7 | 10.5 |

Challenger vs primary (paired grouped bootstrap over TEST docs, seed-matched): dF1 +0.0000 [CI -0.0053, +0.0054], seeds won 2/5, d unseen F1 -0.0072, d macro -0.0105. Not used for selection; v1 stays DeBERTa-base+CRF.

Generalisation (exact F1, primary): head 0.9877 ± 0.0009 (n=None); mid 0.9558 ± 0.0054 (n=None); tail 0.8998 ± 0.0065 (n=None); unseen 0.7008 ± 0.0091 (n=None); seen_alias 0.9700 ± 0.0020 (n=None).  Per-label F1: COLOR 0.859; FOOD 0.908; PART 0.787; PHYSICAL_QUALITY 0.801; PROCESS 0.939; PURPOSE 0.830; QUANTITY 0.979; TASTE 0.815; UNIT 0.978.

### Calibration of span correctness (TEST spans)

| Probability | NLL | Brier | ECE | FOOD NLL / ECE | unseen-mention NLL / ECE | AURC (risk ranking) |
|---|---|---|---|---|---|---|
| raw_conf | 0.3090 | 0.0585 | 0.0586 | 0.406 / 0.072 | 1.093 / 0.225 | 0.01183 |
| calibrated | 0.1986 | 0.0506 | 0.0353 | 0.262 / 0.053 | 0.653 / 0.152 | 0.01286 |
| calibrated+M6 | 0.1846 | 0.0486 | 0.0315 | 0.240 / 0.043 | 0.521 / 0.106 | 0.01257 |

**A. probability calibration vs B. risk discrimination:** calibration and M6 lower NLL/Brier/ECE, but the raw CRF confidence ranks errors best (lowest AURC); isotonic calibration coarsens the ranking and M6 recovers only part of it. They are separate properties and the report treats them separately.

### Router (thresholds from CALIBRATION only; eps = 0.02; cost per 100 spans: accepted error 10, review 1, rejected-correct 3)

| Router | ACCEPT coverage | ACCEPT error [95% CI] | REVIEW rate | REJECT rate | error capture outside ACCEPT | cost/100 |
|---|---|---|---|---|---|---|
| R1_raw_span | 0.856 | 0.0253 [0.0171, 0.0349] | 0.144 | 0.000 | 0.712 | 36.0 |
| R2_calibrated_span | 0.859 | 0.0258 [0.0175, 0.0352] | 0.141 | 0.000 | 0.705 | 36.3 |
| R3_calibrated_span+M6 | 0.873 | 0.0259 [0.0169, 0.0354] | 0.127 | 0.000 | 0.699 | 35.3 |
| R3s_label_strata | 0.579 | 0.0266 [0.0165, 0.0396] | 0.421 | 0.000 | 0.795 | 57.5 |
| R6_FINAL_label_x_unseen | 0.587 | 0.0213 [0.0135, 0.0315] | 0.403 | 0.010 | 0.833 | 52.8 |

Frozen thresholds reproduce S127: True. Review-only error capture 0.699.

Per label (R6 final): | label | n | span error | ACCEPT rate | ACCEPT error | REVIEW | REJECT |
|---|---|---|---|---|---|---|
| COLOR | 32 | 0.156 | 0.781 | 0.0400 | 0.219 | 0.000 |
| FOOD | 610 | 0.093 | 0.000 | - | 0.990 | 0.010 |
| PART | 10 | 0.100 | 0.000 | - | 1.000 | 0.000 |
| PHYSICAL_QUALITY | 142 | 0.268 | 0.000 | - | 0.951 | 0.049 |
| PROCESS | 193 | 0.083 | 0.699 | 0.0148 | 0.285 | 0.016 |
| PURPOSE | 13 | 0.077 | 0.538 | 0.0000 | 0.462 | 0.000 |
| QUANTITY | 580 | 0.033 | 0.981 | 0.0193 | 0.014 | 0.005 |
| TASTE | 17 | 0.118 | 0.471 | 0.0000 | 0.529 | 0.000 |
| UNIT | 481 | 0.035 | 0.988 | 0.0253 | 0.008 | 0.004 |

**Labels that never satisfy eps = 2% and always route to REVIEW (a result, not a defect): FOOD, PART, PHYSICAL_QUALITY.**
Seen mentions: n 1820, ACCEPT rate 0.654, ACCEPT error 0.0193 (span error 0.041). Unseen mentions: n 258, ACCEPT rate 0.112, ACCEPT error 0.1034 (span error 0.314) -- the claimed tolerance does NOT hold on the few unseen spans that are accepted (small strata borrow the pooled threshold).

NOVEL advisory (never an action): 35 FOOD spans (0.057 of FOOD) carry the tag; 0.7714 are correct spans; 0.0571 have a ledger exact hit; 0 of them were nevertheless ACCEPTed by the span router (the tag does not gate).

## RecipeDB3 (grouped benchmark split) -- TEST (2554 docs, 9017 predicted spans, span accuracy 0.9513)

### Span quality (exact match unless stated; mean ± sd over seeds)

| System | seeds | exact micro F1 | exact macro F1 | relaxed micro F1 | boundary err | type err | train min | peak GPU GB |
|---|---|---|---|---|---|---|---|---|
| PRIMARY deberta-base+CRF | 3 | 0.9581 ± 0.0012 | 0.9545 ± 0.0037 | 0.9751 ± 0.0013 | 0.0181 ± 0.0002 | 0.0030 ± 0.0002 | 34.5 | 3.0 |
| FROZEN ACCURACY/COMPUTE CHALLENGER deberta-v3-large+CRF | 3 | 0.9595 ± 0.0004 | 0.9505 ± 0.0032 | 0.9755 ± 0.0003 | 0.0172 ± 0.0002 | 0.0029 ± 0.0006 | 67.4 | 9.3 |

Challenger vs primary (paired grouped bootstrap over TEST docs, seed-matched): dF1 +0.0014 [CI -0.0009, +0.0039], seeds won 3/3, d unseen F1 +0.0125, d macro -0.0040. Not used for selection; v1 stays DeBERTa-base+CRF.

Generalisation (exact F1, primary): head 0.9787 ± 0.0004 (n=None); mid 0.9338 ± 0.0024 (n=None); tail 0.9124 ± 0.0043 (n=None); unseen 0.8553 ± 0.0070 (n=None); seen_alias 0.9692 ± 0.0006 (n=None).  Per-label F1: DF 0.966; NAME 0.929; QUANTITY 0.987; STATE 0.940; TEMP 0.930; UNIT 0.974.

### Calibration of span correctness (TEST spans)

| Probability | NLL | Brier | ECE | FOOD NLL / ECE | unseen-mention NLL / ECE | AURC (risk ranking) |
|---|---|---|---|---|---|---|
| raw_conf | 0.2737 | 0.0449 | 0.0443 | 0.420 / 0.069 | 0.825 / 0.142 | 0.01548 |
| calibrated | 0.1468 | 0.0365 | 0.0066 | 0.209 / 0.021 | 0.388 / 0.074 | 0.02385 |
| calibrated+M6 | 0.1452 | 0.0367 | 0.0056 | 0.216 / 0.017 | 0.335 / 0.050 | 0.01934 |

**A. probability calibration vs B. risk discrimination:** calibration and M6 lower NLL/Brier/ECE, but the raw CRF confidence ranks errors best (lowest AURC); isotonic calibration coarsens the ranking and M6 recovers only part of it. They are separate properties and the report treats them separately.

### Router (thresholds from CALIBRATION only; eps = 0.02; cost per 100 spans: accepted error 10, review 1, rejected-correct 3)

| Router | ACCEPT coverage | ACCEPT error [95% CI] | REVIEW rate | REJECT rate | error capture outside ACCEPT | cost/100 |
|---|---|---|---|---|---|---|
| R1_raw_span | 0.937 | 0.0245 [0.0208, 0.0284] | 0.063 | 0.000 | 0.528 | 29.3 |
| R2_calibrated_span | 0.940 | 0.0250 [0.0211, 0.0290] | 0.060 | 0.000 | 0.517 | 29.5 |
| R3_calibrated_span+M6 | 0.936 | 0.0277 [0.0238, 0.0318] | 0.064 | 0.000 | 0.467 | 32.4 |
| R3s_label_strata | 0.504 | 0.0209 [0.0166, 0.0256] | 0.496 | 0.000 | 0.784 | 60.2 |
| R6_FINAL_label_x_unseen | 0.717 | 0.0209 [0.0172, 0.0249] | 0.278 | 0.005 | 0.692 | 43.1 |

Frozen thresholds reproduce S127: True. Review-only error capture 0.617.

Per label (R6 final): | label | n | span error | ACCEPT rate | ACCEPT error | REVIEW | REJECT |
|---|---|---|---|---|---|---|
| DF | 246 | 0.037 | 0.000 | - | 1.000 | 0.000 |
| NAME | 2912 | 0.077 | 0.668 | 0.0267 | 0.323 | 0.009 |
| QUANTITY | 2488 | 0.014 | 0.998 | 0.0117 | 0.001 | 0.001 |
| STATE | 1247 | 0.082 | 0.000 | - | 0.992 | 0.008 |
| TEMP | 67 | 0.104 | 0.000 | - | 0.985 | 0.015 |
| UNIT | 2057 | 0.031 | 0.990 | 0.0265 | 0.008 | 0.002 |

**Labels that never satisfy eps = 2% and always route to REVIEW (a result, not a defect): DF, STATE, TEMP.**
Seen mentions: n 8136, ACCEPT rate 0.793, ACCEPT error 0.0206 (span error 0.037). Unseen mentions: n 881, ACCEPT rate 0.018, ACCEPT error 0.1250 (span error 0.160) -- the claimed tolerance does NOT hold on the few unseen spans that are accepted (small strata borrow the pooled threshold).

NOVEL advisory (never an action): 431 FOOD spans (0.148 of FOOD) carry the tag; 0.8794 are correct spans; 0.0603 have a ledger exact hit; 211 of them were nevertheless ACCEPTed by the span router (the tag does not gate).

## Linking (frozen operational linker: BGE-large; E5-large documented Pareto alternative; linker_data_v2, 5 seeds; held-out alias / concept sets)

| | BGE (frozen) | E5 (alternate) |
|---|---|---|
| dev_alias Acc@1 (selection set, n=61) | 0.708 | 0.682 |
| held-out alias Acc@1 (n=96) | 0.704 | 0.662 |
| held-out alias Recall@5 | 0.854 | 0.840 |
| held-out alias MRR | 0.765 | 0.733 |
| tail / head held-out alias Acc@1 | 0.711 / 0.691 | 0.652 / 0.680 |
| NIL AUROC (held-out concepts vs aliases) | 0.665 | 0.660 |
| NIL recall at dev-chosen tau | 0.796 | 0.723 |
| false-NIL rate on known aliases | 0.567 | 0.475 |

NIL/NOVEL stays advisory: cosine-based NIL AUROC about 0.66 and no span-level novelty truth. Paired BGE-E5 evidence: {"n": 61, "acc1_diff_BGE_minus_E5": 0.02622950819672131, "ci95": [-0.02950819672131148, 0.08196721311475409]} (indistinguishable; BGE frozen for v1 on DEV evidence and operational simplicity, not on TEST).

## Compute (A100-PCIE-40GB, shared, bf16; indicative)

| Component | bs1 latency | bs32 latency | memory |
|---|---|---|---|
| deberta-base encoder / +CRF decode / +marginals | 19.5 / 21.0 / 50.9 ms | 19.3 / 129 / 493 ms | 0.88 GB |
| deberta-v3-large encoder / +CRF decode / +marginals | 33.5 / 36.7 / 80.6 ms | 34.3 / 144 / 527 ms | 2.63 GB |
| linker|bge-large-en-v1.5 (query + top-10 over 2,031 surfaces) | 16.4 ms | 15.6 ms (256 queries) | 2.06 GB |
| linker|e5-large-v2 (query + top-10 over 2,031 surfaces) | 15.7 ms | 15.7 ms (256 queries) | 2.08 GB |
| M6 gazetteer features (CPU) | 0.19 ms/span | - | - |
| calibrator + router (CPU) | <0.001 ms/span | - | - |

## External / unseen validation (what exists, kept separate)
| Evidence type | Status |
|---|---|
| Cross-dataset confirmation (TASTEset + RecipeDB3, same frozen pipeline, separate calibrators) | **done**: M6 calibration gain significant on TASTEset, neutral on RecipeDB3; M1/M2 reverse; routing behaviour qualitatively the same |
| Unseen-surface evaluation (mention-disjoint strata) | **done**: span F1 on unseen mentions 0.70 (TASTEset) / 0.86 (RecipeDB3) vs 0.97 seen; router accepts few unseen spans and those it accepts have 10-12% error |
| Held-out-concept linker evaluation (linker_data_v2) | **done**: held-out alias Acc@1 0.70, NIL AUROC 0.66 (advisory only) |
| Synthetic / diagnostic robustness | alias-swap / coverage stress tests were not run for the final system; MiniMax synthetic augmentation was a closed auxiliary lane (no effect used) |
| True external-domain validation (FoodBase or independently annotated recipe text) | **unavailable**: FoodBase not obtained; RecipeDB3 has no source field, so no source-disjoint test; Food.com Gold has no NER span annotation for this model |

# A-N closeout
**A. Fair RecipeDB3 reproduction.** Their protocol (random 80/20, select on test): macro 0.9543 ± 0.0020 (5 seeds), reproduced in region (notebook 0.9557). Clean grouped split, selection on dev: macro 0.9504 ± 0.0034, micro 0.9594; their protocol leaks (13.6% masked-family overlap, 5.4% exact duplicate test rows; leaked rows micro 0.9937 vs 0.9558); gap +0.0039 (Welch p = 0.067). Our frozen primary on the grouped TEST: micro 0.9581 ± 0.0012, macro 0.9545 ± 0.0037 (no improvement over the clean baseline: same encoder family). `recipedb3_matched_reproduction.md`.
**B. SPAN_CHAMPION / Pareto.** Champion for v1: DeBERTa-base+CRF. Pareto set: + DeBERTa-v3-large+CRF as the pre-frozen accuracy/compute challenger. TEST: TASTEset micro equal (0.9371 vs 0.9371, paired dF1 +0.0000 [-0.0053, +0.0054]); RecipeDB3 +0.0014 [-0.0009, +0.0039], 3/3 seeds, below the +0.003 rule. Cost: 2.0x train time (67 vs 34 min on RecipeDB3), 3.1x memory (9.3 vs 3.0 GB), 1.7x inference latency. Answer to the Pareto question: spending ~2x compute buys no accuracy distinguishable from zero on TEST.
**C. CRF.** No significant F1 gain (DEV +0.0006 TASTEset; equal on RecipeDB3). Retained because it supplies legal-sequence decoding and span marginals, the confidence signal that calibration and routing consume (cost: marginals dominate latency, 51 ms vs 21 ms per document).
**D. Knowledge prompts.** K1/K2/K3/K4 all below the pre-declared +0.003 rule (-0.0002 to -0.0022): REJECTED.
**E. Linker.** BGE frozen operational linker, E5 documented Pareto alternative (indistinguishable on 61 dev aliases and downstream calibration); contrastive fine-tuning beats zero-shot (E5 held-out alias Acc@1 0.625 zero-shot -> 0.66 fine-tuned on v1; BGE fine-tuned 0.70 on v2); reranker, ING-format and type-specific variants rejected; cosine NIL AUROC 0.66 so NOVEL is advisory only.
**F. Metadata.** PROMOTED: M6 (train-gazetteer exact+fuzzy agreement, all spans, calibration only). REJECTED: M1 (reverses across datasets), M3, M4, G1/G2 (ledger aliases add nothing beyond the train gazetteer), M7 (rule agreement). INCONCLUSIVE, left out: M2, M5. M6 acts as an unseen-mention detector; its benefit is regime-conditional.
**G. Calibration.** See tables: calibrated confidence + M6 improves NLL/Brier/ECE on both TEST sets (largest on unseen mentions) but not risk ranking (raw AURC best). Logistic + isotonic on [logit conf, M6] is the simplest method supported on both datasets.
**H. Fusion.** Concat, gated and M6-only fusion all rejected (DEV -0.0027 / -0.0028 for M6-only, 1/5 seeds); metadata stays outside the encoder.
**I. Span head.** Auxiliary boundary head rejected (-0.0008 vs its control; boundary errors not reduced).
**J. Exact architecture.** DeBERTa-base + CRF (per-dataset, seed 1 for calibrator and router; 5-fold OOF calibrator fit) -> CRF span marginal confidence -> logistic+isotonic calibrator on [logit conf, M6 exact, M6 fuzzy] -> router R6 (eps = 0.02, label x seen/unseen thresholds from CALIBRATION via finite-sample risk control with pooled borrow for strata < 30, REJECT if calibrated P < 1/3, otherwise REVIEW) -> BGE linker for candidates and an advisory NOVEL tag (never an action).
**K. Router result.** See per-dataset tables. The system identifies a subset (59% of TASTEset spans, 72% of RecipeDB3 spans) whose ACCEPT error is 2.13% [1.35, 3.15] and 2.09% [1.72, 2.49]: consistent with the 2% target but not demonstrably below it. Seen mentions: 1.9% / 2.1%. It fails on accepted unseen mentions (10.3% / 12.5%, few spans). Global thresholds (raw, calibrated, +M6) violate the tolerance more (2.5-2.8%) and hide per-label risk. Labels that never meet 2% and always go to REVIEW: TASTEset FOOD, PART, PHYSICAL_QUALITY; RecipeDB3 DF, STATE, TEMP. REVIEW + REJECT capture 83% / 69% of all span errors. NOVEL is advisory only.
**L. Compute / runtime Pareto.** DeBERTa-base+CRF: 2.4 / 34 min training (TASTEset / RecipeDB3), 3.6 / 3.0 GB, 19.5 ms encoder + 1.5 ms decode + ~30 ms for marginals per document (unbatched forward-backward is the bottleneck). v3-large: 3.7 / 67 min, 10.5 / 9.3 GB, 33.5 ms encoder. Linker: ~16 ms per query, 0.15 min training. Calibrator, router, gazetteer: sub-millisecond per span on CPU.
**M. H6 claim status: H6-C** (strong system contribution without benchmark superiority). Reasons: the span F1 equals the clean DeBERTa baseline (RecipeDB3 micro 0.9581 vs control 0.9594) and no external-domain validation exists; benchmark F1 superiority is not shown, and the literature comparison is not like-for-like (their protocol leaks). What is defensible: (i) a leakage-controlled benchmark and a corrected reproduction, (ii) a measured negative-result map (knowledge prompts, span head, fusion, type-specific, reranker, ledger aliases, rule agreement all fail pre-declared rules), (iii) a calibrated, risk-aware routing layer with an honest account of where tolerance holds (seen mentions, near-deterministic labels) and where it does not (unseen mentions, FOOD/STATE/DF), (iv) the dissociation between probability calibration and risk ranking. H6-B is not claimed: it would need evidence of Pareto leadership against external systems.
**N. One next scientific action.** Validate the risk-control claim on a true external domain (FoodBase or an independently annotated sample of non-benchmark recipe text) with a stratum for unseen mentions large enough to give per-stratum control, to test whether the 2% tolerance transfers off-distribution and whether the unseen-mention failure is fixable by stratum-specific calibration.

# Component ledger
**PROMOTED:** DeBERTa-base; CRF (for decoding and marginals, no F1 gain); calibrated confidence; M6 outside the encoder; label x seen/unseen risk routing; frozen BGE linker as candidate generator / advisory signal.
**REJECTED:** K1/K2/K3/K4 knowledge prefixes; span auxiliary head; type-specific NER; reranker; M1; M3; M4; M7; G1/G2 ledger aliases; metadata fusion (concat, gated, M6-only); linker as ACCEPT gate; RoBERTa-large; ING-format linker.
**INCONCLUSIVE / ADVISORY:** M2; M5; automatic NOVEL (advisory only); BGE vs E5 superiority (unresolved: Pareto set); v3-large superiority (not shown on TEST; kept as documented challenger).

# Limitations / future work (nothing below was acted on after TEST)
Router tolerance is met only on seen mentions and near-deterministic labels; accepted unseen-mention spans have 10-12% error (strata too small, pooled thresholds); FOOD/STATE/DF/TEMP/PART/PHYSICAL_QUALITY are always REVIEW at eps = 2%; global calibration does not improve risk ranking; calibrator and router are per-dataset and fit on one seed; NOVEL has no span-level truth; link correctness is unobserved on the benchmarks (no gold canonical IDs); no source-disjoint or external-domain test; NIL cosine AUROC 0.66; the cost model (10/1/3) is an assumption; span marginals are the latency bottleneck; TASTEset TEST was exposed once at E0 and linker held-out sets were viewed during development.
