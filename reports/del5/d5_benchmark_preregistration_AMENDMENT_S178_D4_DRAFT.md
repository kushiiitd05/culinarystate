# D5 pre-registration: D4 descriptive metrics, pre-signature amendment draft (S178, GOVDOC lane)

Status: **AI_DRAFTED / PROPOSED. Not a decision, not a signature, not an approval (D-071).** Written 2026-11-09 by the
S178 GOVDOC lane (an AI agent) for ledger item **T9-C12-R2** ("add D4 metrics to the prereg as descriptive"). It is a
companion to `reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md` (PREREG lane), which does **not**
contain the D4 metrics (board `registry/execution_board_S178.csv` T9-C12-R2 notes). Nothing here edits
`reports/del5/d5_benchmark_preregistration_DRAFT.md`, the other amendment draft, or any signed file; the Mac scribe
applies the chosen options inside the Tue 10 Nov lock, or the metrics cannot be pre-registered and are then reported
as `EXPLORATORY_POST_HOC` (not shown in the talk).

- Base text amended: `reports/del5/d5_benchmark_preregistration_DRAFT.md`, sha256
  `53ad89b7c13db57800e4546efb2ccfe29cdb2ef617b49c462c8b78f51415aa6b` (server worktree, 2026-11-09). Stop if the Mac
  copy differs. Sibling amendment (read, not edited), sha256
  `fd2c50321bd88f389e5309f1ebc96cfb73817cd92c81dee592a70df1582a15e3`; its change ids C1-C9 are not reused here (this
  file uses D4-1 to D4-4) and its C7 bullet ("Descriptive: ...") is the line this amendment extends.
- The D5 benchmark does not exist yet and no rung has run on it, so adding these metrics now is not post hoc. They
  carry **no hypothesis, no alpha and no pass/fail rule**; H1 and H3 decision rules are untouched.

## 0. What the sitting must decide

| Id | Question | Options | Type | AI recommendation |
|---|---|---|---|---|
| D-D4-1 | Add the two D4 descriptive metrics to the D5 prereg before signature | **A** add both (text below) · **B** add Recall@K only · **C** do not add (they become exploratory) | choice | A |
| D-D4-2 | Ordinal score for the B7 risk-coverage curve | **P** output-precision class after the OOD cap (primary, 4 points) · **S** evidence-sufficiency mode (7 levels, secondary) · **both** | choice | both, P primary |
| D-D4-3 | What counts as an "error" for risk | **E1** question-level: an unsupported claim under the independent H3 scorer, or no abstention when gold is ABSTAIN · **E2** E1 plus a gold-range miss on the retention value | choice | E1 (E2 needs the gold range to be human-reviewed first) |

## 1. Why this is not a post-hoc weakening

D4 ("evidence-aware retrieval with abstention", D-075, finish plan M4) is already built (router, retriever, policy,
claim enforcement). The proposal lists D4 among the deliverables, but the D5 prereg tests only H1 (S blocks) and H3
(P and C blocks). Without a pre-registered description of how D4 is scored, any recall or abstention curve shown in
the talk would be chosen after seeing results. This amendment fixes the definitions, the denominators, the
intervals and the list of things that will **not** be reported, before the benchmark exists. It adds no test that
could make a claim easier to pass.

## 2. Changes (old text -> new text)

### D4-1. §4 Metrics (after the C7 "Descriptive" bullet): new sub-section

```diff
 - n is small: every result is reported with its interval. A null result is reported as a null result (R-19), and
   with the power note above.
+
+### 4.1 D4 descriptive metrics (no hypothesis, no alpha, no decision rule)
+
+Computed once, on the frozen benchmark, after the rung runs. Labelled `DESCRIPTIVE, MODEL_ASSISTED_GOLD, PILOT`.
+Nothing in this section changes the H1 or H3 verdict.
+
+**M1. Condition-compatible Recall@K (blocks P1, P2, and each arm of C).**
+- Retrieval list: for B1 and B2 the ranked list of EVD ids the rung puts in its context; for B4, B5 and B7 the
+  ranked evidence packet of `retrieval.retriever.EvidenceRetriever` (BM25 + condition compatibility, deduplicated by
+  cell and independence group). B0 retrieves nothing and is shown as NA. K in {1, 3, 5, 10}, fixed now.
+- Gold ids: `gold_evd_ids` (and `gold_evd_ids_2` for the second arm of a C question) of the reviewed benchmark row,
+  i.e. the EVD ids "that a correct answer may use". A question with no gold id (all of P3) is excluded from the
+  recall denominator.
+- Recall@K (plain) for question q = |gold(q) ∩ top-K(q)| / |gold(q)|.
+- Condition-compatible Recall@K = |{g in gold(q) ∩ top-K(q): compat_ok(q, g)}| / |gold(q)|, where `compat_ok` means
+  `retrieval.compatibility.compatibility(query, row, cond, proc_family)` returns **no MISMATCH** on matrix, process,
+  target, and none on time, temperature or medium where both sides state a value. UNKNOWN is never a mismatch (the
+  repository rule). When a question states no condition axis the two recalls are identical by construction, and the
+  table says so.
+- Aggregate: mean over the questions with at least one gold id, per block and per rung. Interval: question-level
+  percentile bootstrap, 10,000 resamples, seed `d5-d4-recall`, 95 %. Also reported as counts: "x of n questions
+  have every gold id in the top-K", with the Clopper-Pearson 95 % interval.
+- P3 (gold ABSTAIN) is reported separately: the share of P3 questions for which the rung returned at least one
+  evidence row anyway (descriptive; it is not a recall).
+
+**M2. Risk-coverage curve of the B7 abstention rule.**
+- Score (ordinal, not a probability): the **output-precision class** B7 emits after the OOD cap
+  (`decision.confidence.output_precision` then `decision.ood.cap_precision`), ordered
+  QUANTITATIVE > INTERVAL > QUALITATIVE > REPORT_CONFLICT > ABSTAIN. Secondary score [D-D4-2 = S or both]: the
+  evidence-sufficiency mode (`decision.confidence.sufficiency`), ordered DIRECT > NEAR_PARTIAL >
+  MODEL_INTERPOLATION > BROAD_QUALITATIVE > CONFLICTING > IRRELEVANT_EVIDENCE > NO_EVIDENCE. The order is this
+  pre-registration's own plotting convention; the code defines the levels, not an order.
+- Coverage at threshold t = share of all P and C questions (P3 included) whose score is at least t (the question is
+  "answered"). Risk at t = share of the answered questions with error = 1.
+- Error (per question) [D-D4-3 = E1]: 1 if (a) the answer contains at least one unsupported numeric or directional
+  claim under the independent H3 scorer chosen at D-D5-5 (`evaluation/h3_independent.score_answer`), or (b) the gold
+  mode is ABSTAIN and the rung did not abstain; else 0. [E2: also 1 if a stated retention value lies outside the
+  reviewed gold range.]
+- One point per distinct score level (at most 5 for the primary score, 7 for the secondary), plotted as a step
+  curve with the Clopper-Pearson 95 % interval on each risk. Reference points on the same axes: B5 (no abstention,
+  coverage 1) and random abstention at the same coverage (expected risk = the all-answered risk).
+- No area under the curve is computed (a handful of tied levels), and no "calibration" word is used for B7.
+
+**Not reported (by design).** ECE, Brier score, reliability diagrams and AUROC. B7 emits an ordinal rule-based
+label, not a probability (`decision/confidence.py`: values are "ordinal features ... not probabilities"), and no
+calibrator fitted on data disjoint from D5 exists (SSOT §242.4 calibrator not built). A calibrated-probability
+metric may be added only by a dated amendment that names the calibrator and its disjoint calibration set before any
+D5 rung runs.
```

### D4-2. §5 Leakage and conduct: one sentence

```diff
+The retriever, the compatibility weights and the precision cap are frozen (code sha256 in the lock record) before
+any rung runs; no M1 or M2 number is used to change them.
```

### D4-3. Signatures: unchanged

The signature file binds the prereg hash. These changes must be written **into** `d5_benchmark_preregistration_DRAFT.md`
before the lock, like C1-C9 of the sibling amendment.

## 3. Interval widths the reader should expect (exact, scipy beta quantiles; reported so nobody over-reads the plots)

Clopper-Pearson 95 % interval for a proportion k/n. The D5 blocks are small (P1, P2, P3, C: at most 10 questions
each after review).

| n | k = 0 | k = n/2 | k = n |
|---|---|---|---|
| 10 | 0.000 - 0.308 | 0.187 - 0.813 (k = 5) | 0.692 - 1.000 |
| 20 | 0.000 - 0.168 | 0.272 - 0.728 (k = 10) | 0.832 - 1.000 |
| 30 | 0.000 - 0.116 | 0.313 - 0.687 (k = 15) | 0.884 - 1.000 |

So a per-block recall or risk at n = 10 cannot separate 0.3 from 0.7, and a risk-coverage point on the pooled P and C
set (n up to 40) is still a width of about 0.3 near 0.5. Statement for the talk: "descriptive only; intervals are
wide; no rung is ranked on D4".

## 4. Code needed so M1 and M2 are computable (not written by this lane)

| Item | Where | State |
|---|---|---|
| Ranked evidence list per rung, top-K ids | B1/B2 context builders in `evaluation/h1_rungs.py` (dense/hybrid), `EvidenceRetriever` for B4/B5/B7 | rankings exist; a per-question dump of ids in rank order must be written to the run output |
| `compat_ok` flag per (question, gold row) | `retrieval/compatibility.compatibility` | function exists; a 10-line wrapper to call it for gold rows |
| Recall@K, bootstrap, Clopper-Pearson | `evaluation/h3_independent.clopper_pearson` (present, uncommitted when this was written); bootstrap helper to write | partly present |
| B7 precision class and sufficiency mode per question | `decision/policy.decide` output fields `precision`, `sufficiency` (read by the D5 runner) | present in the decision dict; must be saved per question |
| Error flag per question | `h3_independent.score_answer` + `gold_mode` | present |
| Plot | counts-only table and a step plot with intervals (SVG, as `reports/s178/analysis` figures) | to write |

## 5. Hash after lock

Same procedure as section 5 of the sibling amendment (`git show <LOCK>:... | sha256sum`; compare; the lock record
carries the hash of this file for provenance).

Sources: board T9-C12-R2 and T8-C20-R1; consensus T9-C12 row; finish plan M4 / M5; D-075; sibling amendment C3, C6, C7;
`src/culinarystate/retrieval/{retriever,compatibility}.py`, `src/culinarystate/decision/{confidence,policy,ood}.py`,
`src/culinarystate/evaluation/h3_independent.py`; `benchmark/d5/d5_draft_PC_v1.csv` columns (`gold_mode`,
`gold_evd_ids`, `gold_evd_ids_2`).
