# CulinaryState — integrated report draft, 11 November 2026

Group 17: Kush Tokas and Parv Goyal. **AI_DRAFTED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**
This is a reviewable report draft, not a final submission or scientific validation. The authors must supply their
own contribution statement and final edits. Presentation date, slot and length remain unconfirmed.

## Abstract

CulinaryState implements a recipe-state engine, a process-effect evidence resource and an evidence-aware answer
pipeline. Engineering runs cover the recipe corpus, but the scientific claims remain limited by provisional
lineage, unverified evidence and non-independent gold. The D5 benchmark contains 74 questions. Both H1 and H3
are RULE_NOT_MET under the recorded decisions; neither result is repaired by a favourable secondary statistic.
The AA pilot's frozen fit uses two papers and remains NOT_VALIDATED / RESEARCH_ONLY. The report describes
these limits and the negative results alongside the engineering outputs.

Every result below retains the labels and denominator of its source section. AI-delegated approvals under D-085
are not human verification or independent inter-rater evidence. Historical human audit results are identified as
such. Original frozen artifacts remain unchanged; this document assembles existing evidence, not a new run.

## Research questions, benchmark and scope

Proposal H1 concerns state-aware retrieval; H2 concerns process information versus food identity; H3 concerns
unsupported claims with abstention; H4 concerns feasibility and recovery. The SSOT uses different H2–H5 labels.
The explicit mapping is in `reports/final/sections/S179_hypothesis_and_task_crosswalk_DRAFT.md`.
D-080 accepts the Task 5/6 adaptation merge. It does not imply that every task was evaluated.

D-090 freezes S1=12, S2=12, P1/P2/P3/C=10 each and U/X=5 each (74 total), below the planned S sample.
D-089 and `registry/h8_scope_cut_register_v1.csv` declare full H2, H4 and later learning lanes not run before the
talk. Step 35 is designed, not run. These omissions remain part of the scope disclosure.

## H1 result and provenance

**NON_CITABLE / MODEL_ASSISTED_GOLD / CIRCULAR_SELF_CONSISTENCY_ONLY / NO_HUMAN_SIGNOFF_D085.**
H1 uses 24 AI-gold recipe questions (22 Gutenberg and 2 Wikibooks). Near-duplicate leakage is not controlled;
no source-family-disjoint result or independent human gold is claimed. Accuracy is B0=2/24 and
B1=B2=B4=6/24. B4 versus each comparator has 4 discordant pairs and exact two-sided McNemar p=1.0.
D-092 records **RULE_NOT_MET**, not equivalence between methods and not evidence of absence of an effect.
The small sample cannot sustain a precise comparative conclusion.

The original `reports/del5/d5_score_v1_D085/d5_scoring_result.json` leaves H1 NOT_COMPUTED due to unresolved
answers. The separately retained `d5_h1_after_rung_blind_check_D085.json` in that directory resolves six answers,
all as wrong, and supplies the H1 result cited by D-092. This supplement is AI-delegated review, not human
adjudication. The report preserves the distinction rather than overwriting the original scoring artifact.

## D1: evidence resource and its limits (S179 report draft, 2026-11-11)

Status: AI_DRAFTED. All counts below describe imported records: E3_UNVERIFIED, COND_UNAUDITED,
BOOTSTRAP_UNVERIFIED, NON_CITABLE. This is a resource description, not a performance or evidence-quality claim.
New report assembly is AI_PRECHECKED; no human review of this new section is recorded.

### Sources, targets and tiers

The evidence resource contains **17,978 ACTIVE rows**, with **178 deprecated ids excluded**. Its sources are
Bognár (7,090 rows), USDA retention factors R6 (7,018), and Phenol-Explorer 3.6 (3,870). Every ACTIVE row is E3;
14,108 are UNVERIFIED and 3,870 AI_PRECHECKED. **Human-verified D1 rows: 0/40.** These are counts of database
imports, not independent primary experiments. Source: `reports/s178/analysis/evd_dataset_card_v1.json`,
`s203_9_1_total_rows`, `s203_9_6_evidence_tiers` and `labels`.

There are 224 SVAR target ids (213 canonical variables after duplicate mapping). By target subfamily, the row
counts are NUTRIENT_CONTENT 12,116; PHENOLIC_COMPOUND_CONTENT 3,870; GROUP_AGGREGATE 1,496; MASS_YIELD 496.
These categories sum to the ACTIVE total. Source: same JSON, `s203_9_5_target_types`.

### Conditions: preserve missingness

Every figure in this table is an E3_UNVERIFIED / COND_UNAUDITED diagnostic count. No UNKNOWN is filled with zero.

| Axis | MEASURED | Two-sided RANGE | One-sided censored | UNKNOWN | Not recorded | NOT_APPLICABLE |
|---|---:|---:|---:|---:|---:|---:|
| Temperature | 2,430 | 216 | 3,369 | 11,963 | 0 | 0 |
| Duration | 2,607 | 476 | 0 | 14,895 | 0 | 0 |
| pH | 0 | 0 | 0 | 17,978 | 0 | 0 |
| Moisture | 0 | 0 | 0 | 17,978 | 0 | 0 |
| Pressure | 129 | 0 | 0 | 0 | 10,831 | 7,018 |

Source: same JSON, `s203_9_9_condition_coverage.<axis>.rows_by_status`. Water activity is in the schema but
never populated (0/17,978). Temperature and duration are both stated on 1,575 rows (8.76%), all from
Phenol-Explorer. A stated condition does not imply it has been checked against the primary paper.

### Supply against recipe demand

The paired coverage analysis is distinct from condition completeness. EVD has 338 routable (ING, PROC) pairs.
A seeded 1,000-recipe non-BBC sample has 12,501 distinct pairs, of which 111 (0.89%) have an EVD pair.
At process level, 63.47% of 4,724,493 non-BBC process events use a process with some EVD row; this is an upper
bound that ignores the ingredient. For vitamin C, 102 of 125,172 full-corpus distinct pairs have an EVD pair
(0.08%). Source: `reports/s178/evd/evd_coverage_vs_corpus_demand_v2.json` and its companion Markdown table.
These are different denominators and must not be collapsed into one coverage percentage.

Figure for report/deck: `reports/s178/evd/fig_evd_coverage_by_family_v2.svg`, whose adjacent JSON/CSV carry the
numbers. Its caption must retain NON_CITABLE / E3_UNVERIFIED / COND_UNAUDITED and distinguish full-corpus
process counts from sampled pair counts. Tables above are the source/target and condition panels; no new
scientific run was performed for this section.

### Lineage and permitted interpretation

There are 127 provisional independence groups: Bognár 1, USDA 1 and Phenol-Explorer 125. The feasibility report's
headline under reading A is **publication-component CV**, not confirmed study-disjoint evaluation. Reading B,
which also requires human verification, has zero eligible rows and uses leave-one-source-family-out.
Source: dataset-card JSON `s203_9_7_study_source_counts` and
`exports/lineage/step08a_v1/feasibility.json` / `feasibility_report.txt`.
The human edge audit G08-3 is FAIL; exact audit counts and slide wording are in
`S179_H2_and_lineage_statements_DRAFT.md`. Imported row count cannot be read as independent study count.

No claim is made about comprehensive chemistry coverage, primary-paper correctness, study-independent
prediction, or human-verified evidence. Phenol-Explorer raw-table redistribution remains restricted; only
counts and ids enter this section. See `S179_licence_and_split_labels_DRAFT.md` and D-079.

Acceptance remaining: human review of this new section/figure captions and incorporation into the final report
and slides. D-079 accepted earlier drafts; it is not a review of this newly written section.

Source section: `reports/final/sections/S179_D1_evidence_resource_DRAFT.md`.

## Report section draft: D3 state-tracking engine (S179)

Status: **AI_DRAFTED** for the final report (board items T9-C16-R1 and T3-C17-R2). Counts only. No figure here is
an accuracy claim. Written 2026-11-10 by the Mac agent on `kush/s179-finish-fixes`.

**One-line verdict for the report.** D3 is built and has run on the full corpus. Its replay is deterministic and
catches every planted structural error. Gold comparison is limited to 7 P1 recipes and 40 AI-assisted development
recipes, none of them independent; on those, the rule compiler ends with the gold final state on 11-20 % of state
fields.

### 1. What D3 is and where it ran

- **Pipeline.** Recipe text goes through the rule compiler (`state_graph.rule_compiler`, also Rung A's verb slot) to
  an event log. The replay engine (`state_graph.engine`) turns the log into a per-step state graph.
- **Corpus run.** The Step 18 replay ran on every non-BBC recipe with instructions: 599,971 texts (Food.com 522,517;
  Gutenberg segments 73,778; Wikibooks 3,676).
  - Source: `reports/s178/corpus/replay_invariants_corpus_v2.json`, sha256 `2abe7ae7…`, run RUN-S179-CORP-002.
  - Not run: TASTEset has no instruction text, and BBC is not on the server (D-003).

### 2. Metrics that need no gold (T9-C16-R1: replay consistency and property tests)

| Check | Result | Source |
|---|---|---|
| Same-worker determinism (texts replayed twice) | 12,046 of 12,046 identical (Food.com 10,416; Gutenberg 1,550; Wikibooks 80) | replay invariants v2 |
| Cross-process determinism (PYTHONHASHSEED 0 vs 1) | 12,046 of 12,046 identical snapshot and JSONL | same |
| Engine vs an independent re-derivation of the 7 structural invariants | 0 disagreements on 599,971 texts | same |
| Planted errors detected at the planted position: double consume | 28,854 / 28,854 | same (mutation power) |
| Planted errors: order swap | 29,945 / 29,945 | same |
| Planted errors: reuse after discard | 902 / 902 | same |
| Planted errors: split fractions above one | 390 / 390 | same |
| Texts whose replay FAILs an invariant | 12,774 of 599,971 (2.1 %) | same |

**Limits.**
- These tests show the engine applies its own rules consistently. They say nothing about whether the events match
  the recipe.
- The split-sum check is almost empty: 0 of 88,817 partition groups have a checkable basis and fraction.
- Lot accounting, invented values and quantity propagation are not checked by replay (`not_checked_by_replay`).

### 3. Gold comparison (T3-C11-R1, T3-C17-R2)

Sources:
- `reports/del3/compiler_vs_gold_pooled_S179.json` (RUN-S179-GOLD-001) and
  `reports/del3/event_type_table_S179.json` (RUN-S179-GOLD-002);
- method and caveats: `reports/del3/compiler_vs_gold_pooled_S179.md`.

All three sets are **NOT INDEPENDENT**. The engine was developed with them in view, and every set began as an AI
draft. Split label: near-duplicate leakage not controlled.

**Pooled counts, Wilson 95 % intervals:**

| Set | n | Label basis | Final state fields correct | Loose-event F1 | Event-type F1 |
|---|---:|---|---|---:|---:|
| P1, side A | 7 | HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND | 5 / 31 = 0.16 [0.07, 0.33] | 0.24 | 0.61 |
| pilot_20 v1.1 (BBC) | 20 | AI-assisted, human-reviewed dev gold | 9 / 79 = 0.11 [0.06, 0.20] | 0.27 | 0.69 |
| Food.com v1.1 | 20 | AI-assisted, human-reviewed dev gold | 24 / 120 = 0.20 [0.14, 0.28] | 0.32 | 0.71 |

**Event types at level P, P1 set (7 recipes).** Matched is the per-recipe count match, min(gold, predicted). Intervals
come from a recipe-cluster bootstrap with 2,000 resamples.

| Type | Gold | Predicted | Matched | Precision | Recall |
|---|---:|---:|---:|---|---|
| Merge | 36 | 21 | 21 | 1.00 [1.00, 1.00] | 0.58 [0.43, 0.72] |
| Transform | 35 | 63 | 33 | 0.52 [0.40, 0.70] | 0.94 [0.81, 1.00] |
| Transfer | 22 | 6 | 6 | 1.00 [1.00, 1.00] | 0.27 [0.05, 0.47] |
| Split | 8 | 1 | 0 | 0.00 | 0.00 |
| Discard | 1 | 1 | 0 | 0.00 | 0.00 |
| Reserve | 0 | 3 | 0 | 0.00 | n/a |

The dev sets show the same shape:
- Transform: precision 0.54-0.55, recall 0.96-0.98.
- Merge: precision 0.97, recall 0.67-0.74.
- Transfer and Split: under 0.6 on recall in both sets.
- Reserve: too few gold events to read (8 and 1).

The compiler emits a Transform for almost every heat or process verb. It misses many merges and most transfers and
splits. The P1 handbook finding agrees: two human-accepted passes disagree most on final_state (0.82 per pair) and
event_type (0.76).

### 4. Allowed and forbidden wording

- **Allowed:** "built and run on 599,971 texts"; "replay deterministic and catches 100 % of planted structural
  errors"; "against 7 P1 and 40 AI-assisted development recipes (not independent), 11-20 % of final state fields
  match".
- **Forbidden:** "accurate", "validated", "state tracking works", or any number without its n, its label basis and
  "not independent".
- **D3 accuracy** stays NOT MEASURED until an independent gold exists. That is P1b or later, and the decision on the
  minimum gold size is human (Q28).

### 5. Not done

- **Rung A extractor:** the 17a EventGraph is not scored directly; there is no adapter to engine events.
- **P1 side B:** not in this tree.
- **BBC replay invariants:** a Mac run is possible but has not been done.

Source section: `reports/final/sections/S179_D3_state_tracking_DRAFT.md`.

## H2 and lineage: report/deck wording (S179 draft, 2026-11-11)

Status: AI_DRAFTED / AI_PRECHECKED. The passages below are ready for report/deck assembly. They do not record a
human reading of this new draft. T2-C06-R2 and T6-C04-R3 human-review acceptance remains open.

### Lineage statement (T2-C06-R2)

The G08-3 edge-audit gate **FAILED for both reviewers**. In the committed audit, STRONG edges are 50/50 correct
for each reviewer, Wilson lower bound 0.9286523998213857. For B2, the audit records 49/50 for Kush
(lower bound 0.8950455630610349) and 0/50 for Parv (lower bound 0.0). For B3 the corresponding counts are
13/50 (lower bound 0.15871527430089563) and 0/50 (lower bound 0.0). The gate's Wilson lower-bound threshold
is 0.9. Uncertain edges count as errors under the registered conservative rule. These are historical human
audit results, transcribed without assigning a new AI reviewer a human identity.

Source, exact fields: `reports/step08/step08a_audit_result_v2.json`,
`G08-3`, `edge_precision.<reviewer>.<stratum>.correct`, `.n` and `.wilson_lower`.
The miss-rate check is REPORT_ONLY: 2/200 duplicates for Kush and 0/200 for Parv
(`THR-08A-18_miss_rate`). It does not repair the edge gate.

The provisional feasibility export has 127 groups, with USDA and Bognár one group each. Its headline under
reading A (tier eligibility alone) is **publication-component CV**; the weakest label across target families
and readings is **leave-one-source-family-out**. Under reading B (also human verification), eligible pool n=0.
Phenol-Explorer has 125 publication-key groups; these are not confirmed experiment boundaries. Lab-disjoint
feasibility is NEED_DATA. Source: `exports/lineage/step08a_v1/feasibility.json` and `feasibility_report.txt`.

**One-line implication for every H2 figure:** provisional publication keys and the failed lineage edge audit
prevent reading these diagnostics as evidence of generalisation across independently verified studies.
USDA and Bognár have no study-disjoint estimate.

### Honest H2 slide text (T6-C04-R3)

**Title:** Process information versus food identity: diagnostic, no direction established.

**Labels applying to every slide number:** DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE /
PRIOR_EXPOSURE_REANALYSIS / PROVISIONAL_08A / COND_UNAUDITED / NO_HUMAN_SIGNOFF_D085.

On Phenol-Explorer's provisional publication/study-key-disjoint split, process-mean loss minus ingredient-mean
loss is **0.0992 [−0.0446, 0.2401]**, with **362 rows / 20 clusters**. Positive means lower ingredient-mean
loss; the interval crosses zero. Matrix-disjoint favours the process arm by construction; process-disjoint
favours the ingredient arm. Only the provisional study-key split compares the arms on equal terms.

Source: `reports/step29/diag/diag_results_S179.json`,
`result.families.PHENOL-EXPLORER-3.6.contrast_d2_vs_b2.splits.study_disjoint`.

Bognár repeated-value share is **0.9489** and USDA **0.5874** within their diagnostic subsets
(`duplicate_control.share_of_rows`); each source is one lineage group. The original data were already used
by DEL-2 and the exploratory Step 30 run. This is prior-exposure reanalysis, not a fresh independent test.
D7's Phenol-Explorer random predictions equal the global mean D1 exactly
(`d7_vs_d1_max_abs_pred_diff = 0.0`); no learned-model advantage follows.

**Conclusion to show:** Full proposal H2 is DECLARED_NOT_RUN before the talk (D-089; H8-02). The diagnostic
cannot replace that test. No process-information advantage or independent-study generalisation is claimed.

### Review and assembly boundary

The writer checked these statements against the cited committed files. This is an AI precheck, not a human
signature or inter-rater result. The original audit, feasibility export, failed gate and frozen outputs remain
unchanged. Human review required by the board and incorporation into the final deck remain pending.

Source section: `reports/final/sections/S179_H2_and_lineage_statements_DRAFT.md`.

## D4: evidence-aware retrieval and abstention (S179 report draft, 2026-11-11)

Status: AI_DRAFTED · DIAGNOSTIC · BOOTSTRAP_UNVERIFIED · NON_CITABLE · NO_HUMAN_SIGNOFF_D085. D5 uses MODEL_ASSISTED_GOLD and author-only review (AI-delegated).
This section transcribes committed outputs; no scorer, benchmark, prompt or frozen result is changed.

### Frozen-benchmark scope and the headline result

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

### Retrieval (M1)

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

### Answer risk and coverage (M2)

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

### Earlier retrieval development study (silver; not D5)

`reports/del4/retrieval_silver_v2_analysis.md` analyses 600 templated development queries over 17,978 EVD rows.
These are **SILVER_DEV_ONLY / NON_CITABLE** figures, not independently labelled questions or recipe-step chunks.
RRF BM25+e5-large-v2 MRR@10 was 0.762 versus 0.704 for the bge-small RRF list, paired delta
+0.057 [0.035, 0.082]. Structured+dense R4 versus structured R3 had delta +0.005 [-0.006, 0.015]; the dense
blend was not promoted. The source analysis notes oracle-slot R3=0.856. Model selection used this dev study,
so it is not an independent test of the selected embedding. The frozen D5 run, with its different task and
small denominators, is reported separately above.

### Limits and acceptance remaining

The gold is AI-drafted/AI-reviewed, not independent human gold. Qualitative answers found by broad cross-food
retrieval do not resolve the P3 definition mismatch. The formal H3 rule remains failed; no post-hoc boundary
choice replaces D-092. The raw score's H1 NOT_COMPUTED is also retained: the separate rung-blind supplemental
check gives H1 RULE_NOT_MET (see the hypothesis crosswalk).

This report text satisfies the evidence-traceability portion of T8-C19-R1. Final report/deck assembly, human
reading where required, and an amendment-only resolution of the recorded compatibility-recall inconsistency
remain separate work. No claim of calibration or scientific validation follows from these diagnostics.

Source section: `reports/final/sections/S179_D4_retrieval_and_abstention_DRAFT.md`.

## AA pilot: frozen Model A identifiability diagnostic

Date: 2026-11-11. Board item: T5-C12-R2.

**DIAGNOSTIC / NON_CITABLE / AI_PRECHECKED / NO_HUMAN_SIGNOFF_D085.**
Model A remains **NOT_VALIDATED / RESEARCH_ONLY**. Reviewer: author-only review (AI-delegated).
This report profiles the already frozen estimates; it neither refits Model A nor opens SIM-VAL.
No parameter-precision gate is passed by this report.

### Inputs and reproducibility

- Frozen fit: `reports/step10/aa_pilot_model_a_fit_D085.json`, SHA-256
  `b9247db03e98423f8866fa50b24e2ecd33831d907f3aace00b1f7e4f2ea9543f` (D-091).
- Frozen model: unweighted OLS on ln k, separate paper intercepts and shared Ea,
  `src/culinarystate/simulation/aa_pilot_fit.py`, version `aa-pilot-fit-0.1.0-draft`.
- New tool: `tools/s179_aa_profile_summary.py`; new output:
  `reports/step10/aa_identifiability_profile_summary_S179.json`. The tool checks both code hashes
  recorded by the frozen fit, refuses an existing output path and records the fit/tool SHA-256 values.
- Command: `python tools/s179_aa_profile_summary.py --fit reports/step10/aa_pilot_model_a_fit_D085.json
  --out reports/step10/aa_identifiability_profile_summary_S179.json`.
- Source rows are AI_PRECHECKED under D-085, not human verified. There are **7 included rows from 2 papers,
  3 regression coefficients and 4 residual degrees of freedom**. Original CAL verification sheets and
  paper texts are absent from this checkout; the diagnostic uses the frozen sufficient summaries only.

All numerical results below have the four diagnostic labels above. No bootstrap was performed.

### Method and why the summaries are sufficient

Let beta be the three regression coefficients, C the frozen OLS covariance, s the frozen residual SD,
n = 7 and nu = 4. The frozen fitter uses C = s²(X'X)^-1 and SSR_min = nu s². For coefficient j fixed
at b, minimising over all nuisance coefficients gives the exact quadratic profile

`SSR_profile(b) = SSR_min + s² (b - beta_j)² / C_jj`.

Profiling the unknown common Gaussian variance gives

`LR(b) = n log[SSR_profile(b) / SSR_min]`.

This algebra reconstructs the unconstrained profile from the committed summary without raw observations,
refitting, a scan-width choice or a new optimiser. The 95% **asymptotic** likelihood interval uses
`LR <= chi²_1(.95) = 3.841458820694124`; its half-width is
`sqrt(C_jj * nu * expm1(chi²_1(.95) / n))`.
The confidence level is a disclosed diagnostic choice, not a new acceptance threshold.

Because only four residual degrees of freedom remain, the table separately includes the Student-t interval
`beta_j +/- t_4(.975) sqrt(C_jj)`. This is finite-sample conditional inference under the fixed-design,
independent, homoscedastic Gaussian-error model; it does not account for paper dependence, verification error,
assay mismatch, model misspecification or extrapolation to another matrix. The t interval is wider here.
The likelihood profile is exact algebraically; its chi-square confidence calibration is asymptotic.

Method references: the [NIST likelihood-ratio test description](https://www.itl.nist.gov/div898/handbook/apr/section2/apr233.htm)
gives the chi-square calibration, while [NIST's linear-regression uncertainty example](https://pages.nist.gov/ml_uncertainty_py/toy_regression.html)
uses residual degrees of freedom for Student-t inference. The displayed profile identity is derived above from
the frozen fitter's OLS equations, rather than inferred from an unscaled covariance condition number.

### Per-parameter results

Reference temperature is 363.15 K. The ln k_ref intercepts use k in min^-1 as in the frozen AA fitter.
Ea is displayed in kJ/mol; the JSON retains J/mol.

| Parameter | Estimate | Asymptotic profile 95% interval | Conditional Student-t 95% interval | Profile status | Practical gate status |
|---|---:|---|---|---|---|
| ln k_ref, AAK-01 | -4.3152 | [-4.5445, -4.0859] | [-4.6875, -3.9429] | BOUNDED_CONDITIONAL_ON_OLS_MODEL | NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION |
| ln k_ref, AAK-06 | -3.1251 | [-3.4142, -2.8360] | [-3.5944, -2.6558] | BOUNDED_CONDITIONAL_ON_OLS_MODEL | NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION |
| Shared Ea, kJ/mol | 64.3978 | [46.6419, 82.1536] | [35.5707, 93.2249] | BOUNDED_CONDITIONAL_ON_OLS_MODEL | NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION |

The recorded covariance is positive definite; within the fitted linear model there is no flat coefficient
profile. This establishes bounded model-conditional intervals, not sufficient scientific precision for a use
case. No locked precision or relative-width criterion was found in the AA pilot preregistration. Proposed
G26-CAL settings must not silently become signed rules. A raw covariance condition number would mix units of
dimensionless ln k and J/mol; no such number is presented as an identifiability test.

### Checks and limits

`tests/unit/test_s179_aa_profile_summary.py`: **10 passed** under Python 3.11.9. A failing collection first
confirmed the new tool was absent. Synthetic constrained OLS refits at both endpoints for every coefficient
reproduce the likelihood-ratio cutoff. Tests distinguish profile and t intervals, preserve the caller's input,
and refuse invalid degrees of freedom, residual SD, covariance or paper identities.

The new tool reads no recipe text, CAL sheets or SIM-VAL material. It checks existing hashes rather than
replacing the fit or its code. Existing failed gates and frozen outputs remain unchanged.

- Two papers provide very little information about between-paper heterogeneity. The fitted between-paper SD
  is not a random-effects variance estimate with a profiled confidence interval here.
- No residual checks, leverage analysis, per-temperature checks, raw-unit revalidation or per-paper Model B
  sensitivity can be reconstructed reliably from the summary. They remain open pending the CAL packet.
- The likelihood profile assumes a common Gaussian residual variance and no within-paper dependence.
  Bounded intervals under that model are not evidence of robust practical identifiability under alternatives.
- The report supplies parameter profiles and explicit parameter statuses for T5-C12-R2. Its practical gate
  remains unassessed; a reviewer may accept the report artifact without approving a scientific gate.
- PARAM minting, SIMULATE calibration, domain/basis checks, SIM-VAL extraction and prediction, and the T5 G15
  scorecard retain their own requirements. This report changes none of them.

Source section: `reports/step10/identifiability_report_v1.md`.

## Report section draft: data licences and split labels (S179)

Status: **AI_DRAFTED** for the final report and the release card (board items T9-C28-R1 and T9-C09-R3). D-079
records Kush's acceptance of the licence paragraph. It states what the registries record and
does not verify or change any licence. Written 2026-11-10 by the Mac agent on `kush/s179-finish-fixes`.

Sources: `registry/recipe_source_usage_registry_v1.csv`, `registry/data_source_acquisition_manifest.csv`, the SRC
ledger, `DECISIONS.md` D-003, `src/culinarystate/decision/public_mode.py`, `registry/split_registry_v1.csv` and
`reports/s178/leakage_audit_d5_findings.md`.

### 1. Licence and redistribution paragraph (T9-C28-R1)

> **Data, licences and what is shown.** The project reads five recipe sources. Their status, as recorded in
> `registry/recipe_source_usage_registry_v1.csv`, is:
> - **BBC Good Food** (11,934 recipes, scraped for an earlier course assignment) is third-party copyright,
>   LOCAL_RESEARCH_ONLY. Its text stays on one researcher's machine. It never goes to a server or an external
>   service, and it is never committed (D-003).
> - **Food.com** (Kaggle download) is declared CC0 by the uploader, but that authority is not verified
>   (LICENCE_UNVERIFIED), so its text is not redistributed either.
> - **TASTEset** is LICENCE_UNVERIFIED in the usage registry. The acquisition manifest notes an MIT licence, but no
>   source row confirms it.
> - **Wikibooks Cookbook** pages are CC BY-SA 4.0, with attribution by page and revision.
> - **Project Gutenberg** cookbooks (338 books) are public domain in the USA under the Project Gutenberg licence.
>
> Process-effect evidence comes from:
> - the USDA retention tables (US government work, public domain);
> - Phenol-Explorer 3.6, a free public resource whose redistribution needs the authors' permission. We therefore
>   publish only derived counts and identifiers from it, never its tables. The publications it cites remain under
>   publisher copyright and are cited, not reproduced.
>
> Everything committed or shown in this report, the slides and the demo screenshots is counts, identifiers, hashes
> and figures computed from them. No recipe text from BBC Good Food or Food.com appears.
>
> The demo has a public mode for anything that is not the researcher's own machine. It drops every knowledge-graph
> edge computed over the BBC corpus before any answer is built, and it omits the carbon figures, whose upstream
> licence is unverified. In local mode, any request that arrives through a tunnel or proxy is refused (HTTP 503).


Update: D-079 accepted the licence paragraph. No new source licence is verified by this assembly.

Source section: `reports/final/sections/S179_licence_and_split_labels_DRAFT.md`.

## Limitations and unfinished work

07.A v4 FAIL and G08-3 FAIL remain on record. 07.A-R1 is NOT_RUN under D-085 because two personas of one model
cannot supply independent labels. AI_DRAFTED_GOLD does not become HUMAN_BLIND through delegation.
The H3 30-claim audit was not run; no positive claim is made in its absence. The compatible-recall inconsistency
in D4 remains unresolved in the frozen output. A proposed future evidence-boundary amendment is separate at
`reports/del5/D5_P3_evidence_boundary_amendment_PROPOSAL_2026-11-11.md`; it is not adopted or executed.

AA Model B sensitivity, raw-row source checks, PARAM provenance, calibration/domain integration, SIM-VAL
extraction and descriptive prediction remain incomplete. The missing private files are not replaced with
synthetic scientific data. No clinical, dietary or food-safety recommendation is made by the research demo.

The final 1,000-session emission-contract corpus scan, completed report/deck recipe-text leakage comparison,
updated frozen split registry, post-19-Nov MPU score and actual timed rehearsal on 24 Nov remain separate acceptance
items. A source-field scan alone would not certify absence of verbatim recipe text.

## Author contributions

**PENDING — to be written by Kush and Parv from their own contribution facts.** No effort allocation or
individual scientific contribution is inferred from commit authorship, delegated AI personas or this session.

## Reproducibility and review index

- Original run records: `registry/compute_runs_v1.csv`; D5 RUN-S179-D5-001 and 29-diag RUN-S179-DIAG29-001.
- D5 freezes: `registry/freezes/D5-BENCH-2026-11-10.json` and supplementary `D5-BENCH-2026-11-10b.json`.
- Gate provenance: `reports/final/sections/S179_gate_provenance_DRAFT.md`; decisions D-079..D-092.
- Negatives: `registry/negative_results_register_v1.csv`, including NEG-0050 and NEG-0051.
- Acceptance checklist: `reports/orchestration/S179_round6_acceptance_audit.csv` and companion Markdown.
- Artifact versions/limits: `reports/final/RELEASE_CARD.md`.
- Proposed work windows: `reports/s179/schedule_to_talk_DRAFT_2026-11-11.md`.

Frozen outputs must not be edited, retuned or silently rescored. Any new experiment requires its own dated
amendment, freeze, output path and run record, with the original result retained beside it.
