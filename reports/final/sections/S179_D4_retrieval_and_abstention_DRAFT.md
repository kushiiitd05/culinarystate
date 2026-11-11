# D4: evidence-aware retrieval and abstention (S179 report draft, 2026-11-11)

Status: AI_DRAFTED · DIAGNOSTIC · BOOTSTRAP_UNVERIFIED · NON_CITABLE · NO_HUMAN_SIGNOFF_D085. D5 uses MODEL_ASSISTED_GOLD and author-only review (AI-delegated).
This section transcribes committed outputs; no scorer, benchmark, prompt or frozen result is changed.

## Frozen-benchmark scope and the headline result

D-090 froze n=74 questions: S1 12, S2 12, P1/P2/P3/C 10 each, U/X 5 each. D4's answer/risk analysis uses the
40 P/C questions. Rungs ran in RUN-S179-D5-001. Freeze `D5-BENCH-2026-11-10b` added the EVD and relatives
scorer inputs after rung execution started and before scoring (D-092); benchmark/scorer/prereg hashes were
unchanged. No independent human gold or inter-rater result exists. Split label: near-duplicate leakage not
controlled; this is not a source-held-out benchmark.

H3 is **RULE_NOT_MET** (D-092). The exact two-sided sign test has 16 discordant questions in B7's direction,
0 in the other direction, p=0.000030517578125. The additional P3 condition fails: B7 abstains 0/10 against
B2 3/10. Therefore the sign-test result alone cannot establish the preregistered conjunction. The 30-claim veto
audit was NOT_RUN because it cannot turn an already failed conjunction into a pass. B7 is **rule-based
evidence-sufficiency abstention (uncalibrated)**. NEG-0051 records the mismatch between the gold's exact/parent
food evidence boundary and the decision layer's broad cross-food evidence boundary.

Source for the test: `reports/del5/d5_score_v1_D085/d5_scoring_result.json`, `h3_selected` / `ood_abstention`,
plus D-092. The raw Markdown rounds the displayed p to 0.0; the exact JSON value above is retained here.

## Retrieval (M1)

Source throughout: same score JSON, `retrieval_d4_m1.rungs.B2.blocks.pooled_P1_P2_C`.
B2 has retrieval lists for **20** questions; the pooled label does not mean all 30 P1/P2/C questions were
scored. Ten questions lack a list (`n_questions_without_list`). Rungs B0/B5/B5T/B7 expose no retrieval list and
are NA_NO_RETRIEVAL_LIST, not zero-recall systems.

| K | Plain recall (mean per question) | Compatibility recall (as recorded) |
|---|---:|---:|
| 1 | 0.2 | 0.0 |
| 3 | 0.3417 | 0.0 |
| 5 | 0.375 | 0.0 |
| 10 | 0.375 | 0.0 |

MRR is 0.3417, explicitly EXPLORATORY_NOT_IN_PREREG. No question states a condition axis (n=0).
The nested JSON note claims compatibility recall equals plain recall by construction, but the recorded compatibility
vector is 0.0 at every K while plain recall is nonzero. This internal output inconsistency is retained and flagged;
no compatibility-recall claim is made from it, and the frozen output is not silently repaired.

The `source_disjoint_diagnostic` field stratifies by **gold source family**: USDA 16 questions,
Phenol-Explorer 3, Bognár 1, labelled DIAGNOSTIC_ONLY. It is not a retraining or retrieval run with a source
family held out. P3 returned evidence on 10/10 questions; that rate is descriptive and is not recall.

## Answer risk and coverage (M2)

Source: same JSON, `d4_m2_risk_coverage.decision_layer_rungs.<rung>.primary_precision_class.points`.
Risk is the recorded E1 error count divided by the included question count, and thresholds are ordinal rules,
not calibrated probabilities. Every cell below is a NON_CITABLE diagnostic on the 40 P/C questions.

| Inclusion threshold | Coverage | B5 errors/n | B5T errors/n | B7 errors/n |
|---|---:|---:|---:|---:|
| QUANTITATIVE | 0.45 | 12/18 | 0/18 | 2/18 |
| INTERVAL | 0.75 | 18/30 | 2/30 | 4/30 |
| QUALITATIVE | 0.975 | 27/39 | 5/39 | 13/39 |
| ABSTAIN | 1.0 | 28/40 | 5/40 | 14/40 |

The ABSTAIN threshold is the endpoint that includes all questions; coverage 1.0 is not an assertion that all
questions received substantive answers. C-block agreement is 9/10 for B5, B5T and B7; each reports
cannot-separate on 10/10. This scorer field is descriptive, not a separate hypothesis result
(`c_block.rungs`). Router accuracy is only 6/10, status INCOMPLETE_GOLD_BRANCH, with X controls 4/5
(`router`); it must not be presented as accuracy over all 74 questions.

## Earlier retrieval development study (silver; not D5)

`reports/del4/retrieval_silver_v2_analysis.md` analyses 600 templated development queries over 17,978 EVD rows.
These are **SILVER_DEV_ONLY / NON_CITABLE** figures, not independently labelled questions or recipe-step chunks.
RRF BM25+e5-large-v2 MRR@10 was 0.762 versus 0.704 for the bge-small RRF list, paired delta
+0.057 [0.035, 0.082]. Structured+dense R4 versus structured R3 had delta +0.005 [-0.006, 0.015]; the dense
blend was not promoted. The source analysis notes oracle-slot R3=0.856. Model selection used this dev study,
so it is not an independent test of the selected embedding. The frozen D5 run, with its different task and
small denominators, is reported separately above.

## Limits and acceptance remaining

The gold is AI-drafted/AI-reviewed, not independent human gold. Qualitative answers found by broad cross-food
retrieval do not resolve the P3 definition mismatch. The formal H3 rule remains failed; no post-hoc boundary
choice replaces D-092. The raw score's H1 NOT_COMPUTED is also retained: the separate rung-blind supplemental
check gives H1 RULE_NOT_MET (see the hypothesis crosswalk).

This report text satisfies the evidence-traceability portion of T8-C19-R1. Final report/deck assembly, human
reading where required, and an amendment-only resolution of the recorded compatibility-recall inconsistency
remain separate work. No claim of calibration or scientific validation follows from these diagnostics.
