# Fresh linker evaluation -- final report (single frozen run)

Provenance: gold = HUMAN_INDEPENDENT_DOUBLE_ANNOTATED + HUMAN_ADJUDICATED, 441 items (freeze commit ccb8650, manifest `FRESH_LINKER_GOLD_FREEZE_MANIFEST.json`); scored once with the pre-registered plan (`fresh_linker_scoring_plan.md`); the candidate pool key was opened only after the freeze commit. Raw numbers: `_fresh_linker_scores.json`. No model output entered the gold; nothing was tuned on it. The 441 items are sealed evaluation data and never training data.

**Human agreement (before adjudication):** exact 276/441 (62.6%), class 284/441, kappa 0.50; concept agreement when both committed 180/195; 165 rows adjudicated. **Final gold:** MATCH 191, PARENT 31, NONE 80, AMBIGUOUS 139 (none with explicit ING-id answer sets, so AMBIGUOUS is excluded from accuracy and reported only as a count).

## Concept choice (View A: forced choice among candidates; strict n = 191 MATCH, lenient n = 222 MATCH+PARENT; 95% bootstrap CI)
| System | strict Acc@1 | lenient Acc@1 | NIL AUROC | NIL AUPRC |
|---|---|---|---|---|
| L0 BGE top-1 | 0.796 [0.738, 0.853] | 0.761 [0.703, 0.815] | 0.891 | 0.760 |
| L1 E5 top-1 | 0.817 [0.759, 0.869] | 0.766 [0.712, 0.820] | 0.848 | 0.683 |
| L2 cross-encoder (zero-shot) | 0.649 [0.581, 0.717] | 0.572 [0.509, 0.635] | 0.812 | 0.580 |
| **L4 Tev1-4B (primary)** | **0.901 [0.859, 0.942]** | **0.847 [0.797, 0.892]** | **0.922** | **0.834** |
| L5 Nimble (alternative) | 0.874 [0.827, 0.921] | 0.842 [0.793, 0.887] | 0.902 | 0.788 |
L3 (fine-tuned cross-encoder) and L6 (calibrated NIL combination) were not scored: no configuration was frozen before gold.

## Paired differences (View A; bootstrap CI, exact McNemar)
strict: Tev - BGE +0.105 [0.058, 0.152] (p<0.001); Tev - E5 +0.084 [0.037, 0.136]; Tev - CE +0.251 [0.183, 0.320]; Nimble - BGE +0.079 [0.031, 0.131]; **Nimble - Tev -0.026 [-0.063, +0.010] (p=0.30)**; CE - BGE -0.147 [-0.220, -0.073].
lenient: Tev - BGE +0.086 [0.036, 0.135]; Tev - E5 +0.081 [0.032, 0.131]; Tev - CE +0.275 [0.203, 0.347]; Nimble - Tev -0.005 [-0.045, +0.036].
NIL AUROC: Tev - BGE +0.031 [-0.007, +0.070]; Nimble - BGE +0.011 [-0.034, +0.054]; Tev - CE +0.110 [0.066, 0.155].

## Candidate pool, retrieval vs reranking failure, reranker efficiency
BGE top-5 pool oracle: strict 0.984 (3 retrieval failures of 191), lenient 0.973 (6 of 222). BGE top-1 reranking failures 36 (strict); Tev 16; Nimble 21; E5 28; cross-encoder 67 (its candidate list is the BGE top-10, oracle 1.00). Reranker efficiency = (acc - BGE top-1)/(oracle - BGE top-1): **Tev 0.56 strict / 0.41 lenient; Nimble 0.42 / 0.38**. Nearly all errors are reranking failures, not retrieval failures. **Pooling caveat:** the annotators saw a pool built from these systems, so a concept missed by every system would have been labelled NONE; retrieval failures common to all systems are invisible here, and the near-1.0 oracle is partly an artefact of pooling.

## NIL / NONE at each system's frozen operating point (known n = 222, NONE n = 80)
BGE (dev tau 0.862): recall 0.988, false-NONE on known 0.514, specificity 0.486, balanced accuracy 0.737. E5 (tau 0.858): 0.975 / 0.450 / 0.550 / 0.762. **Tev default NONE choice: recall 0.850, false-NONE 0.189, specificity 0.811, balanced accuracy 0.830.** Nimble: 0.800 / 0.144 / 0.856 / 0.828. Cross-encoder has no frozen operating point. End-to-end (View B) accuracy: strict BGE 0.664, E5 0.701, Tev 0.827 [0.782, 0.871], Nimble 0.812; lenient BGE 0.603, E5 0.639, Tev 0.765, Nimble 0.762.

## PARENT items (n = 31) -- picked the parent concept
BGE 17, E5 14, cross-encoder 3, Tev 16, Nimble 20 (reported separately, not folded into strict).

## Strata (strict View A accuracy; n)
S1 known surfaces (58): BGE 1.00, Tev 1.00 | S2 alias-like (48): BGE 0.65, Tev 0.83, Nimble 0.81, CE 0.58 | S3 likely novel (55): BGE 0.80, Tev 0.91 | S4 ambiguous generic (10): 0.50 / 0.70 | S5 (0) | S6 long qualified (20): 0.70 / 0.85. By human confidence: both-3 (77): BGE 0.96, Tev 0.97; lower (114): BGE 0.68, Tev 0.85. Mention length: <= 2 tokens (154): 0.82 / 0.91; >= 3 tokens (37): 0.70 / 0.87. Post-hoc slices are descriptive.

## Latency / failures
Tev1-4B median 112 ms per mention, Nimble 91 ms (shared A100 under load; earlier idle-GPU measurements 51 / 92 ms); BGE/E5 retrieval about 16 ms. Failed or malformed decision calls: 0.

## Claim status (pre-registered gate)
**V2-LINK-B (strong).** Tev beats BGE, E5 and the cross-encoder on concept choice with paired lower bounds > 0 under both strict and lenient scoring, and has the best NIL AUROC/AUPRC and a far better frozen NONE operating point; the pre-registered V2-LINK-A requirement that the **NIL AUROC advantage over BGE have a lower bound > 0 is not met** (+0.031, CI [-0.007, +0.070]), so A is not claimed. Tev stays primary over Nimble (no paired advantage). Limits: 139 AMBIGUOUS items (31%) are unscored, S5 regional is unrepresented, pooling bias, one mention-only prompt, one 441-item set, single seed, zero-shot models.

## Next scientific action
Pre-register and run `CulinaryLinkDecision-v1`: distil the Tev1-4B decision behaviour (mention/context + top-K candidate names/aliases + retrieval scores -> candidate or NONE) into a smaller model we own, trained only on legitimate TRAIN data with Tev as teacher, compared against BGE, the cross-encoder and Tev on a *new* sealed set (the 441 items stay sealed).
