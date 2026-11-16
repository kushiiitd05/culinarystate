# D4 contract metrics — what exists, what was computed, what cannot be (S181, 2026-11-17)

**Labels on every figure below: MODEL_ASSISTED_GOLD · NO_HUMAN_SIGNOFF_D085 · POST_HOC_DIAGNOSTIC** (also NON_CITABLE, AI_DRAFTED).

Every figure here was computed, or re-read, **after** the D5 results were seen. They are descriptive statistics on the
frozen 74-question D5 benchmark, whose gold is model-assisted / AI-delegated (D-085), not independent human gold. They
are not pre-registered tests and not the accuracy of the system in general. H1 and H3 remain **RULE_NOT_MET** (D-092);
nothing here re-tests or bears on either rule. No frozen file, scorer, gate or ledger was changed.

Machine output: `reports/s181/d4_contract_metrics.json` (script `tools/s181_d4_contract_metrics.py`, `--check`
reproduces it byte for byte; sha256 of all nine inputs recorded; the four inputs pinned by the D5 freeze match it).

The proposal checks D4 by four metrics. Outcome of each:

| Contract metric | Outcome | Headline |
|---|---|---|
| Condition-compatible Recall@K | **COMPUTED_NOW, degenerate** (plain Recall@K: ALREADY_REPORTED) | 0.20 / 0.34 / 0.375 / 0.375 at K = 1 / 3 / 5 / 10, n = 20, identical to plain recall by construction; the condition-discriminating version is NOT_COMPUTABLE |
| Risk–coverage | **ALREADY_REPORTED** (curve points); AURC **COMPUTED_NOW** | B7 partial AURC 0.0977 over coverage 0.45–1.0 (mean risk over span 0.178); n = 40 |
| Unsupported-claim rate | **ALREADY_REPORTED** in the frozen score JSON (not yet quoted in the report prose) | B7 4/34 = 0.118; B2 24/43 = 0.558 (machine checker; no human audit) |
| ECE | **NOT_COMPUTABLE** | no per-item numeric confidence exists; the system emits categorical classes only |

## 1. Condition-compatible Recall@K

- **Plain Recall@K — ALREADY_REPORTED**: `reports/del5/d5_score_v1_D085/d5_scoring_result.json`,
  `retrieval_d4_m1.rungs.B2.blocks.pooled_P1_P2_C`, transcribed in
  `reports/final/sections/S179_D4_retrieval_and_abstention_DRAFT.md`. Recomputed here from the run records: equal.
- **Condition-compatible Recall@K — COMPUTED_NOW, qualifier DEGENERATE_EQUALS_PLAIN_RECALL.** Definition is the
  amendment's M1: a retrieved gold row counts if the frozen `compatibility()` returns no MISMATCH on matrix, process,
  target, time, temperature or medium (`d4_metrics.compat_ok`); UNKNOWN is not a mismatch; mean over questions.

| K | Compatible recall (now) | Plain recall (frozen) | Frozen "compat" as recorded | Gold hits scored |
|---|---:|---:|---:|---:|
| 1 | 0.2 | 0.2 | 0.0 | 6 |
| 3 | 0.3417 | 0.3417 | 0.0 | 11 |
| 5 | 0.375 | 0.375 | 0.0 | 13 |
| 10 | 0.375 | 0.375 | 0.0 | 13 |

- **n = 20 questions** (P1 10, P2 10), rung **B2 only**. Denominator: P1/P2/C questions with gold ids and a dumped
  ranked list. The 10 C questions have no dumped list and are **not** in it, so the frozen label "pooled_P1_P2_C" is
  P1+P2 in fact. B0, B5, B5T and B7 dumped no list (NA_NO_RETRIEVAL_LIST): **the decision-layer retriever that D4 is
  about was not measured**; this is the B2 hybrid baseline list.
- **Ranked lists hold 5 ids**, so K = 10 equals K = 5 and is not a true top-10 figure.
- **Why it is degenerate.** No benchmark question states a time, temperature or medium (0 of 20; the benchmark has no
  condition column), and B2 retrieved with an empty query (`tools/s179_d5_run_rungs.py:110`). All 13 retrieved gold
  rows therefore have all six axes UNKNOWN, nothing can mismatch, and the value equals plain recall — as the amendment
  said in advance. It shows nothing about condition-aware retrieval.
- **Condition-discriminating variant — NOT_COMPUTABLE.** Missing input: benchmark questions that state a condition
  axis, plus the stated-condition query / `gold_compat` vectors in the run records (neither field was dumped).
- **The frozen 0.0 explained.** The scorer recorded 0.0 because the run carries no `gold_compat` vectors and
  `compat_ok` treats a missing vector as incompatible (`d4_metrics.py:106-110`). It is a missing-input artifact, not a
  measured zero. The frozen JSON is left as it is; the S179 draft already flags the inconsistency.
- The low absolute values stand: 62.5 % of gold evidence is not in the top 5, and all gold is in the top 5 for 7 of 20
  questions.

## 2. Risk–coverage

- **Curve points — ALREADY_REPORTED**: same score JSON,
  `d4_m2_risk_coverage.decision_layer_rungs.<rung>.primary_precision_class.points`; table in the S179 D4 section.
- **AURC — COMPUTED_NOW.** Trapezoid between the four observed points, exact fractions, over the observed coverage span
  0.45–1.0 only (nothing extrapolated to coverage 0). "Mean risk over span" = area / 0.55. n = 40 P/C questions per
  rung; error E1; ordering score is the ordinal precision class, not a probability.

| Rung | Partial AURC (0.45–1.0) | Mean risk over span | All-answered risk | Risk non-decreasing in coverage |
|---|---:|---:|---:|---|
| B5 | 0.3528 | 0.6414 | 28/40 = 0.70 | no |
| B5T | 0.0351 | 0.0638 | 5/40 = 0.125 | no |
| B7 | 0.0977 | 0.1777 | 14/40 = 0.35 | yes |

- **This AURC is outside the frozen amendment**, which deliberately computes no area ("a handful of tied levels"). It is
  a post-hoc addition over four tied levels, has no interval, and is not comparable to a full-range AURC from a
  continuous confidence.
- Unflattering readings kept: B7's area is 2.8 times B5T's; B5 and B5T curves are not monotone (risk falls slightly at
  the last step); at full coverage B7 is wrong on 14 of 40.

## 3. Unsupported-claim rate

**ALREADY_REPORTED** in the frozen score JSON: `h3_summaries.rungs.<rung>.all` (`ucr`, `n_unsupported`,
`n_numeric_claims`) and `h3_summaries.enforcement_checker_ucr`. The S179 D4 section and the final report draft do not
quote it; that is a prose gap, not a computation gap. Recomputed x/n equals the frozen value for every rung.

| Rung | Unsupported / numeric claims | UCR (independent checker) | Enforcement checker (not independent) | Answers with no claim and no abstention |
|---|---:|---:|---:|---:|
| B0 | 8 / 8 | 1.0 | 4/4 = 1.0 | 36 |
| B2 | 24 / 43 | 0.5581 | 8/42 = 0.1905 | 4 |
| B5 | 35 / 76 | 0.4605 | 12/74 = 0.1622 | 0 |
| B5T | 4 / 57 | 0.0702 | 0/57 = 0.0 | 1 |
| B7 | 4 / 34 | 0.1176 | 0/34 = 0.0 | 17 |

- Unit: numeric claims in the 40 P/C answers per rung (claim-level). UCR is undefined for an answer with no number.
- Both checkers are machine checkers against the EVD ledger. The human claim audit was **not run** (D-092), so no
  human-verified rate exists.
- B7 is not at zero under the independent checker (4/34), its own enforcement checker reports 0/34, and 17 of its 40
  answers make no numeric claim at all, so its low rate is partly bought by saying less. B5T is lower than B7.

## 4. ECE

**NOT_COMPUTABLE.** Missing input: a per-item numeric confidence in [0, 1]. The 150 decision-layer run records
(B5, B5T, B7) carry only `mode`, `precision`, `sufficiency`, `reason`, `per_option`, `comparison`, `ood` — all
categorical; the script scans them and finds no numeric confidence field.

No mapping from class to number is used, because none is defined as a probability in the frozen code:
- `src/culinarystate/decision/confidence.py:3-4`: the confidence vector holds "ordinal features in [0, 1] for a later
  calibrator (§242.4) — not probabilities" — and that vector is not saved in the run records either;
- `src/culinarystate/evaluation/d4_metrics.py:56-57` (frozen `NOT_REPORTED`): "B7 emits an ordinal rule-based label,
  not a probability; no calibrator disjoint from D5 exists";
- the §242.4 calibrator was never built; fitting one on the 40 D5 questions and scoring it on the same 40 would be
  circular.

Binning that would apply if a confidence existed: 10 equal-width bins (implemented and unit-tested). The ECE figures
under `reports/ner/` are for the NER linker (D1) and are not a substitute. The same reason blocks Brier, reliability
diagrams and AUROC. **The word "calibrated" in the D4 title is not supported by any measurement.**

## Sentence for the final report (D4)

> "Of the four checks the proposal names for D4, three are reported as post-hoc diagnostics on the 74-question D5 benchmark with model-assisted gold (MODEL_ASSISTED_GOLD, NO_HUMAN_SIGNOFF_D085; not independent human gold, not pre-registered): Recall@K for the B2 baseline list is 0.20, 0.34 and 0.375 at K = 1, 3 and 5 (n = 20; lists hold five ids, and condition-compatible recall equals plain recall because no question states a condition, so it does not test condition-aware retrieval); the risk–coverage curve for the rule-based decision layer B7 runs from 2/18 errors at coverage 0.45 to 14/40 at coverage 1.0 (partial area 0.098); and B7's unsupported-claim rate is 4 of 34 numeric claims (0.118) against 24 of 43 (0.558) for B2, by a machine checker with no human audit. ECE is not reported: the system emits ordinal evidence classes, not probabilities, and no calibrator was built, so abstention is rule-based and uncalibrated. H3 remains RULE_NOT_MET."

## Updated D4 row for the compliance matrix

Detail block:

| | |
|---|---|
| **Status** | **STRONG CORE; 3 OF 4 METRICS REPORTED AS POST-HOC DIAGNOSTICS; ECE NOT_COMPUTABLE** |
| Met | Compatibility layer with UNKNOWN-neutral semantics, evidence classes, answer-ask-abstain routing, unsupported-claim enforcement. Recall@K (B2, n = 20), risk–coverage points + partial AURC (B5/B5T/B7, n = 40) and unsupported-claim rate (all rungs) are reported — MODEL_ASSISTED_GOLD · NO_HUMAN_SIGNOFF_D085 · POST_HOC_DIAGNOSTIC |
| Not demonstrated | **ECE / calibration**: no numeric confidence is emitted and no calibrator exists. **Condition-aware** recall: no benchmark question states a condition, so compatible recall equals plain recall; the decision-layer retriever (B5/B7) dumped no ranked list. No human claim audit. H3 RULE_NOT_MET stands |
| Evidence | `reports/s181/d4_contract_metrics.{json,md}`, `tools/s181_d4_contract_metrics.py`, `reports/del5/d5_score_v1_D085/d5_scoring_result.json`, `reports/final/sections/S179_D4_retrieval_and_abstention_DRAFT.md` |
| Report wording | the sentence above |

Summary row:

| D4 | STRONG CORE | ECE NOT_COMPUTABLE (no numeric confidence, no calibrator); condition-compatible Recall@K degenerate (= plain recall, no condition stated; B2 only, n = 20); risk–coverage and unsupported-claim rate reported, post-hoc, model-assisted gold | agent |
