# CulinaryLinkDecision-v1 -- FINAL report (one scoring run, 850-item human gold)

Protocol: `culinary_link_decision_final_eval_protocol.md` (aef4b2d). Systems frozen: `CULINARY_LINK_DECISION_FINAL_FREEZE_MANIFEST.json` (5c4a753). Gold frozen before scoring: `FINAL_LINK_GOLD_FREEZE_MANIFEST.json` (472d50e); scorer `tools/v2dm_final_score.py` (9296cfa); raw numbers `_final_link_scores.json`. Pool key never opened. No threshold, K, lambda or model changed after DEV.

## Gold
850 items, double independent human annotation (kappa 0.317 before adjudication) + human adjudication of 446 disagreements. NONE 391, MATCH 293, AMBIGUOUS 137 (set-valued; NONE may be a member of the set, decided before scoring), PARENT 29. S5 regional unavailable. Caveats: adjudication reasons are templated; the candidate pool is the union of system picks (pooling bias); View A = 430 strict / 459 lenient concept-bearing items.

## Results (View A forced choice, strict; lenient in parentheses)
| System | Acc@1 strict (95% CI) | lenient | View B (frozen op. pt) | NIL AUROC | ms |
|---|---|---|---|---|---|
| BGE | 0.881 (0.849-0.912) | 0.861 | 0.764 | 0.852 | - |
| E5 | 0.851 | 0.826 | 0.752 | 0.844 | - |
| zero-shot CE | 0.619 | 0.595 | - | 0.801 | - |
| Tev1-4B | 0.872 | 0.856 | 0.686 | 0.838 | 53.8 |
| Nimble | 0.881 | 0.871 | 0.680 | 0.825 | 93.2 |
| **CD-L2** (3 seeds) | 0.862 (0.832-0.891) | 0.840 | 0.737 | 0.828 | 16.3 |
| CD-L1 (3 seeds) | 0.798 | 0.778 | 0.712 | 0.762 | 16.2 |

## Questions
- **Q1 student vs BGE/E5:** CD-L2 - BGE = -0.019 [-0.043, +0.005] strict, -0.020 [-0.046, +0.004] lenient; CD-L2 - E5 = +0.011 [-0.016, +0.039]. No significant gain over either. 
- **Q2 retention:** not interpretable. Tev - BGE = -0.009 [-0.042, +0.021] (strict): the teacher itself shows no gain over BGE on this set, so the denominator is ~0 (point 2.08, CI [-6.0, 8.3]). The DEV-observed Tev gain (+11.5 pts, n=61) did not reproduce.
- **Q3 CD-L2 vs CD-L1:** +0.064 [+0.038, +0.089] strict, +0.062 [+0.038, +0.088] lenient; NIL AUROC +0.047 [+0.020, +0.076]. All 3 seeds of CD-L2 (0.858-0.867) exceed all 3 of CD-L1 (0.781-0.812).
- **Q4 efficiency:** 33.4M params, ~16 ms vs Tev 4B ~54 ms and Nimble 9B ~93 ms (stored per-call latencies, not a controlled benchmark). CD-L2 is statistically indistinguishable from Tev (-0.010 [-0.038, +0.018]) and ~1.9 pts below Nimble.
- **Q5 strata (CD-L2 - BGE, strict):** S1 -0.004, S2 0.000, S3 -0.032, S4 -0.004, S6 **-0.093** [-0.185, 0.000] (n=54; below n>=30 degradation threshold of -15 pts, not triggered). Head/tail by train frequency: not computed.
- **NIL (secondary):** BGE has the best AUROC (0.852); CD-L2 -0.021 [-0.038, -0.003] vs BGE. At frozen operating points BGE (0.764) > CD-L2 (0.737) > Tev (0.686). No system gives a safe autonomous NIL.
- **Retrieval vs reranking:** MATCH oracle 0.983 (BGE top-5) / 0.990 (K=10); remaining errors are reranking errors, not retrieval.

## Classification (gates fixed in the protocol)
- **D3: not reproduced.** CD-L2 does not beat BGE or E5 with a positive lower bound; the teacher's DEV advantage did not carry to the larger human gold. D1-STRONG/D1/D2 all fail the first gate.
- **DISTILL-A:** CD-L2 beats CD-L1 with paired lower bound > 0 (strict, lenient and NIL). Teacher-KL supervision helps the student relative to gold-only training; this does not make the student better than the BGE baseline.

## Honest reading
The gold-only cross-encoder is worse than BGE; teacher distillation recovers the gap to BGE-level but not beyond. The LLM-decision teachers (Tev, Nimble) are not better than BGE top-1 here. BGE top-1 remains the best-or-tied linker by accuracy, NIL AUROC and operating-point accuracy on this set. DEV (n=61) overestimated the teacher gain; the larger set resolves this. Not supported: that a decision-model reranker improves linking over BGE; safe autonomous NIL. Not tested: synthetic augmentation, regional data. CulinarySpanDecision is not started by this result alone (decision for the user).
