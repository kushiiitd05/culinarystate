# S176 REV-B: evaluation statistics, governance and delivery review of the Max-plan packet

Persona: evaluation statistician + research-governance auditor + delivery planner (external "Max plan" reviewer).
Date: 2026-11-08 (Sunday). Status: AI_DRAFTED review; every recommendation is PROPOSED, nothing here is a decision,
signature or approval. READ-ONLY on the repo except this file.

Scope answered: Q20-Q28, Q30, Q33-Q40; (C-eval) missing evaluation/governance items; (D) ranked cut-down plan to 25-26 Nov,
CUT list, and what the paper needs later. Not answered here: Q1-Q19, Q29, Q31, Q32 and the section-5 state-vector design.

## 0. Evidence base and what I verified

Read in full: the packet; D-027 (R-06), D-029..D-031, D-034, D-045..D-047, D-060..D-077 in `DECISIONS.md`;
`reports/step07/07A_R1_preregistration_DRAFT.md`, `07A_R1_packet_manifest.json`, `step07_v4_agreement_result_run2.json`,
`step07_v4_adjudication_result.md`, `step07_v4_hash_notes.md`, `condition_audit_protocol.md`;
`src/culinarystate/evidence/condition_agreement.py`, `tools/step07ar_{agreement,build_packet}.py`;
`reports/del5/d5_benchmark_preregistration_DRAFT.md`, `src/culinarystate/evaluation/{paired_stats,h1_rungs,d5_state,d5_draft,freeze_records,abstention_spec}.py`,
`src/culinarystate/generation/{claims,enforce}.py`, `benchmark/d5/d5_draft_{S,PC}_v1.csv` (columns and counts only),
`reports/del5/ladder_*`, `reports/step10/aa_pilot_preregistration_DRAFT.md`, `reports/step29/29diag_preregistration_DRAFT.md`,
`registry/freezes/15A-BOOT-2026-11-08.json`, `registry/compute_runs_v1.csv`, `reports/step23/router_demo_census_vitc_full_corpus_S171.json`,
`handoff/FINISH_PLAN_2026-11-07.md`, `PROGRESS_AUDIT_2026-11-07.md`, `PROJECT_FLOW_VERDICT_2026-11-08.md`,
plan v2 cards for Steps 15, 23, 29, 35, 36.

Computed (scripts in `/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad/revb/`):
`power.py` (exact McNemar splits and power, using the project's own `paired_stats.py`), `ac1.py` (AC1 vs kappa using the
project's own `condition_agreement.py`, Clopper-Pearson bounds, Wilson sample sizes).

Could not inspect (Mac-only, git-ignored): the v4 label files and the D5 review sheets. The v4 AC1 below is therefore
reconstructed from the committed result JSON and hash notes (one reviewer constant, five one-sided disagreements), which
reproduces the committed kappa = 0.0 and raw agreement 0.99444 exactly. I did not run the Newcombe code against an
independent implementation; I checked the formula by reading and hand-checked one case (12,4,4,10 gives +-0.185).

## A. Verdict

The plan's honesty posture (failed gates kept, NON_CITABLE labels, UNKNOWN never 0, human gates named) is good and above
what a course project usually does. But three of the five evaluation instruments in the packet cannot show what they
claim, and the governance record has two real breaches that should be repaired in writing before the talk.

1. **07.A-R1 does not test the normaliser.** Both the old kappa gate and the new AC1 gate measure whether two reviewers agree,
   not whether the normaliser is right; two reviewers who both code every cell WRONG_VALUE would score AC1 = 1 and PASS.
   At the prevalence seen in v4, AC1 >= 0.80 tolerates about 179 of 900 disagreeing cells (19.9 %) while the kappa
   gate it replaces tolerated about 2 to 7. The v4 failure was a kappa-paradox artefact on the five critical fields
   (0 of 500 critical cells disagreed), but it also exposed a degenerate reviewer (900 of 900 codes identical), which AC1
   rewards rather than detects. Switching the statistic is defensible only with the changes in Q24.
2. **H1 is circular on S1.** The S1 gold ("ingredients heated so far") is computed by `d5_state.heated_ingredient_ids` on the
   Rung A graph; the B4 context contains `state_block`, which prints "Heated so far:" from the same function on the same graph.
   B4 is handed the gold. Separately, the B1/B2/B4 retrieval pool is built from all steps, including steps after the cut.
3. **H3 is close to tautological.** B7 is built by `enforce()`, which deletes sentences that `claims.check_claims` flags; H3 scores
   UCR with the same `check_claims`. UCR(B7) = 0 by construction (already 0.0 in both smoke ladders, as is the plain template
   B5T). The test then passes whenever B2 has at least 3 questions with an unsupported claim.
4. **Governance.** No D-071 decision (D-072 to D-074) closed a human-defined gate. But D-071 as written does not exclude independent
   human labelling gates, its prv half rests on a relay (Parv has not confirmed it), and two earlier records crossed the line
   (D-046 Parv signature by relay; D-068 human-only record appended by the agent under a verbal waiver).
5. **Delivery.** The lot-state layer (Q39) should be cut for 25 Nov; the critical path is: sign preregs, D5 review (fixed),
   AA verification, then H1/H3 and one SIMULATE row. 07.A-R1 cannot open anything before 25 Nov (23b also needs 15b, which
   cannot be frozen by then), so it is the best candidate to slip.

## A2. Findings that drive the answers (evidence)

| ID | Finding | Evidence | Consequence |
|---|---|---|---|
| F-01 | v4 had 0 disagreements in all 5 critical fields; all 5 disagreements are one-sided (Kush SHOULD_BE_AMBIGUOUS, Parv CORRECT), in duration (4) and temperature_value (1), in 5 distinct conditions, and all sit in the 108 cells whose normalised status is AMBIGUOUS (agreement 0.954 there, 1.000 elsewhere) | `step07_v4_agreement_result_run2.json`; `step07_v4_adjudication_result.md` | The failure is mostly the paradox, but the residual signal is real: the normaliser's handling of ambiguous durations. Duration is the key kinetic input, yet it is not in the critical set |
| F-02 | Parv's nine field codes are CORRECT in all 900 cells, so kappa = 0.000 exactly (p_e = p_o). Her first file used non-codebook codes (`INCORRECT`, 102 problems); CA-037 changed from INCORRECT to CORRECT after the tool listed the row as invalid. Same reviewer, G08-3: B2 49/50 UNCERTAIN, B3 0/50 correct, versus Kush 49/50 and 13/50 | `step07_v4_hash_notes.md`; D-034 | Two audits, two degenerate reviewer outputs (opposite directions). Common cause is process (no calibration, no controls, no validator), not a person |
| F-03 | Reconstructed v4 pooled AC1 (q = 7) = 0.9944; every critical field AC1 = 1.0. Under the R1 scorer, v4 behaviour would PASS | `ac1.py` | The R1 gate would have passed the attempt it replaces; that must be disclosed with the statistic switch |
| F-04 | R1 scorer flags a critical field only on AC1 < 0.80, exact < 0.90, or a repeated ordered pair >= 3. It never looks at WRONG_*/INFERRED frequency | `condition_agreement.py` L130-134 | Agreement-only gate; correctness is untested |
| F-05 | `IDENTICAL_JUDGEMENTS` makes a perfectly agreeing pair NOT_COUNTED | `_provenance` | A gate that can be passed only if the raters differ somewhere is perverse; it is a proxy for "did they copy" and should be replaced by a timestamp and free-text check |
| F-06 | R1 packet source mix: Phenol-Explorer 78, Bognar 18, USDA 4 of 100 conditions; USDA + Bognar hold about 14.1k of the 17,978 EVD rows (7,018 + 7,090) | manifest; D-031 | Pass/fail says almost nothing about the USDA dialect that dominates EVD rows |
| F-07 | The three signature-bearing preregs (07.A-R1, D5, AA pilot) end in a text block "Kush Tokas: ____"; only 29-diag has a hash-bound signature file. All signature checks (`HUMANS` tuple, `_signer_is_kush`) test a JSON text field the agent could write | `freeze_records.py`, `abstention_spec.py` | "Human only" is a convention, not a control |
| F-08 | The freeze record is named `FREEZE_15A_BOOTSTRAP` / `15A-BOOT-...` although Step 15a has a HARD dependency on 08a, whose G08-3 FAILED (D-034). 29-diag itself needs only the snapshot hash, 15.0 and the 15a.R seal | Step 15 card; D-034; freeze file | Approving a record called "15a" can be misread as satisfying Step 15a |
| F-09 | AA pilot SIM-VAL = 4 papers. Step 15 G15-f needs >= 30 % and >= 5 groups, else Step 27 RESEARCH_ONLY. The agent is extractor and fitter; the SIM-VAL firewall is behavioural. If AAK-05 (browser download) is missing, SIM-VAL has 3 papers | AA prereg s3; Step 15 card | First SIMULATE is RESEARCH_ONLY by the plan's own rule; say so up front |
| F-10 | Compute log: 14 rows; start blank in 10, end blank in 14, output sha blank in 3; no input-hash, code-hash or environment column in the header (the packet says "code and input hashes"); no lockfile or pinned requirements in the tree; Ollama model digest, NER checkpoint hash and embedding versions not logged; two commits shown as `none (no .git...)` | `compute_runs_v1.csv`; `pyproject.toml` | Not enough for a paper (Q35) |
| F-11 | Router census: 36,359,902 items = (event x linked ingredient) pairs, each scored for vitamin C; 25 EVD ingredients of 1,843 seen; every item carries DOMAIN_UNKNOWN, INPUT_UNOBSERVED, NO_FORM, PARAM_UNCONFIRMABLE, SAFETY_UNKNOWN | census JSON | DIRECT 0.754 % has a meaningless denominator (flour x vitamin C is in it). DIRECT is an EVD lookup, not router skill |
| F-12 | P-block strata are defined by EVD-index membership (`d5_draft.stratum`), and B7's route is also an EVD lookup; gold ABSTAIN means "ledger silent", not "unknowable" | `d5_draft.py` | P3 abstention is guaranteed for B7 and B5T; B0 may know the answer and be marked wrong |
| F-13 | S1 gold = `d5_state.heated_ingredient_ids` on the Rung A graph; B4 context `state_block` prints "Heated so far" from the same function and graph. B1/B2/B4 retrieval chunks are built from all steps (the unit test passes the full recipe with `cut=2`), so future steps can be retrieved. Scoring links free text to ING ids with the same linker the engine used, so B4's own surface strings always resolve, while an LLM's names may not | `d5_state.py`, `h1_rungs.py`, `tests/unit/test_s173_h1_rungs.py`, `benchmark/d5/d5_draft_S_v1.csv` (gold = heated ingredient ids) | B4 is handed the S1 gold; H1 on S1 measures engine self-consistency. Future-step leakage and linker asymmetry bias every rung, in different directions |

## B. Q-by-Q answers (answers Q20-Q28, Q30, Q33-Q40)

Legend. The packet states an explicit "Lean" only for Q1-Q4, Q7, Q8, Q13, Q32, so none of my 18 questions has an explicit
lean; "implied lean" below is inferred from the question framing, the packet section 7 ranking and the finish plan.

| Q | Implied agent lean | Agree? | One-line recommendation |
|---|---|---|---|
| Q20 | Mostly-UNKNOWN is honest; coverage rises with lot state + PARAM | PARTLY | Abstention is a result only if UNKNOWN is shown correct on a labelled set; fix the denominator; lot state will not move coverage |
| Q21 | AI_DRAFTED QUALITATIVE allowed when labelled | PARTLY | Demo-only, as `physically_possible` with an unreviewed-mechanism flag; never in the benchmark or any claim |
| Q22 | Taxonomy / group bracketing, similarity finds candidates only | PARTLY | Use taxonomy donors, output a donor interval, require >= 2 independent donors, and set the group definition by cold-split coverage |
| Q23 | Flip rule is enough | AGREE | Call it a flip-sensitivity rule, not VOI; ASK is untestable in one-shot Q&A |
| Q24 | Switching to AC1 is defensible | PARTLY | Defensible only as a new attempt with an explicit R-06 amendment, a stricter threshold, an accuracy co-gate and seeded controls |
| Q25 | Add an outside reviewer for a subset | AGREE (and more) | Blind-first gold for S blocks, outside reviewer on 20 items, report as MODEL_ASSISTED_GOLD pilot |
| Q26 | Accept as pilot with Newcombe | PARTLY | Accept as pilot only after the S1 fix; enlarge S to 60; state the MDE; sign test for H3 |
| Q27 | Present H1 and H3 as tested, H2 diagnostic | AGREE | With wording: "pilot", "0 of 4 confirmed", and H3 re-specified |
| Q28 | (none) | n/a | No D3 accuracy claim now; minimum for one is >= 30 blind recipes, >= 2 annotators |
| Q30 | (none) | n/a | Food.com: analysis and internal diagnostics yes; released or headline learned rungs no |
| Q33 | NER agreement as diagnostic only | AGREE | Plus precision/recall of each detector on a human-labelled random sample; agreement of two systems is not accuracy |
| Q34 | (none) | n/a | Accept for now, measure on 200 human-labelled Food.com lines, retrain with unit-drop augmentation if needed |
| Q35 | "Enough for a paper?" with hashes logged | DISAGREE | Not enough; the log lacks input/code/env hashes and times |
| Q36 | (none) | n/a | Counts are low-risk; the real exposure is the hosted demo and any BBC-derived example |
| Q37 | (none) | n/a | The line is "AI may tighten, defer or refuse; never loosen, close or sign" (section B2.1) |
| Q38 | (none) | n/a | Fallback ladder in section D.3; 07.A-R1 is the first to slip |
| Q39 | Lot state is item 1 (high/high) | DISAGREE | Cut it for 25 Nov |
| Q40 | (none) | n/a | Do not apply v16 before the talk |

Tally: AGREE 4 (Q23, Q25, Q27, Q33), PARTLY 5 (Q20, Q21, Q22, Q24, Q26), DISAGREE 2 (Q35, Q39), no lean to compare 7.

---

### Q20. Router usefulness (DIRECT 0.754 %)

- **Recommendation.** Treat mostly-UNKNOWN as a result, but only after two changes: (1) re-denominate; (2) show on a labelled set that the UNKNOWNs were correct and the DIRECTs were right. Report a funnel, not one percentage: items -> target-bearing ingredient (vitamin C > 0 in SR) -> heat or leach process -> linked ingredient -> an EVD cell exists -> condition-compatible. Report DIRECT per source family and per reason code.
- **Agree?** Partly. Agree that abstention is honest. Disagree that 0.754 % is a coverage figure (F-11), and disagree that lot state raises it: DIRECT is an EVD lookup (115 vitamin C pairs, 25 ingredients) and SIMULATE needs PARAM rows (0 today, about 16 CAL rows after M3). Lot state adds inputs to G7; it adds no evidence or parameters.
- **Reason.** An all-UNKNOWN router has false-activation 0 and passes any safety test trivially; the plan already knows this (G23.3: recall on complete-input positives >= 0.70 so an all-UNKNOWN engine cannot pass). No case set exists, so G23.1 and G23.3 are unevaluated; the census alone measures nothing about correctness. Also validated-model plus assumed inputs is not a validated output: a SIMULATE number driven by Layer 2 defaults must be emitted as the GENTLE-INTENSE bracket, and the bracket may be too wide to be useful (then QUALITATIVE).
- **Coverage target.** Do not set a percentage. Pre-register an upper bound instead: after M3, SIMULATE can fire only on (vitamin C-bearing ingredient) x (aqueous heat event) x (60 <= T <= 100 C in the fit domain) x (lot water present). Compute that bound now from the census and print it as "SIMULATE <= X %".
- **Risk if ignored.** The talk reads as "the router does nothing" (the S173 demo problem) or, worse, a reviewer asks for the false-activation rate and there is none.
- **Settle.** (a) 60-item dev case set (the card asks for 60-100 dev, >= 150 locked, >= 30 % negative, >= 20 % missing-input): 40 minutes of human labelling per person on a stratified sample of 100 UNKNOWN items by reason code ("was UNKNOWN right?") is a cheap first estimate of unnecessary-UNKNOWN rate; (b) compute the funnel (agent, vinayak, about 25 min); (c) G23.1 on the locked set stays post-talk and needs a labeller who is not a MECH author.

### Q21. QUALITATIVE direction from unreviewed MECH entries

- **Recommendation.** Allowed only in the NON_CITABLE demo, as class `physically_possible` carrying `AI_DRAFTED_MECH_UNREVIEWED`; never `evidence_supported`; never counted in H1/H3, the router case set, or any number on a slide.
- **Agree?** Partly (I agree with the labelled-demo idea; I would not let it near a claim).
- **Reason.** 32 MECH entries are AI-drafted, 0 reviewed (G21.6 needs blind dual review); law 5 says recalled constants are `SOURCE_UNVERIFIED_AGENT_RECALLED`. Section 141 permits `physically_possible`, but the mechanism table behind it is itself unverified, so the label must say so.
- **Risk if ignored.** An audience member sees "acid + chlorophyll: loses green" with a router badge and takes it as validated; or the unreviewed screen leaks into the H3 "coverage" denominator.
- **Settle.** Review only the mechanisms that actually fire in the demo (probably 8-10 of 32): Kush and Parv blind, then an outside food-science reader for those entries (plan Step 21 card needs an expert anyway). Metric: share of fired directions a reviewer marks textbook-consistent, with n stated.

### Q22. INTERPOLATE from similar-food evidence

- **Recommendation.** Define "similar" by taxonomy (the ING parent in `d5_draft.stratum` is a taxonomy parent, not an embedding), never by embedding distance. INTERPOLATE emits an interval [min, max] of donor values, never a point; require >= 2 donors that are independent under the 08a lineage (USDA is one cluster and Bognar is one cluster, so USDA-only donors count as n_eff = 1); carry the donor count and fallback level. Choose the grouping rule (same ingredient family, same SR food group, plus water-content band) by empirical coverage on a cold-food split of DEV (fraction of held-out true values inside the donor bracket, per group), then test once on RESERVED.
- **Agree?** Partly: the plan's D4 hierarchical-fallback rule (Step 29) is exactly this; I add the independence and coverage requirements.
- **Reason.** Bracketing is a claim about transfer; without a coverage estimate it is an assumption. 17,978 E3 rows with unverified, partly imputed factors and capped censoring mean the bracket is a bracket of table values, not of truth; say so.
- **Risk if ignored.** P2 questions get an answer whose interval has unknown coverage; "evidence class" is silently upgraded.
- **Settle.** Cold-food coverage table (agent, Mac, CPU, minutes). If coverage under nominal 0.90 falls below the plan's c_floor 0.85, downgrade to QUALITATIVE for that group. Score P2 as "states the evidence is from a parent or similar food and gives an interval", not as a point match.

### Q23. ASK branch

- **Recommendation.** Use the flip rule: ASK iff some admissible value of the missing input changes the route or the sign of the direction. For discrete inputs enumerate the domain; for monotone continuous inputs evaluate the interval endpoints. Name it "flip-sensitivity", not value of information.
- **Agree?** Yes.
- **Reason.** H3 as pre-registered has no ASK gold (modes ANSWER / ANSWER_SIMILAR_ONLY / ABSTAIN / COMPARE), and ASK needs an interactive channel that Step 36 marks design-only; nothing can be shown about ASK quality in a one-shot benchmark.
- **Risk if ignored.** Claiming ASK works from the 5 X-block controls.
- **Settle.** Report ASK precision on the X block descriptively (5 items, intervals); defer ASK quality to H4.

### Q24. 07.A redo: is switching to Gwet AC1 defensible?

Statistics first.

| Dominant prevalence (both raters) | po needed for kappa >= 0.80 | disagreeing cells of 900 allowed by kappa >= 0.80 | disagreeing cells allowed by AC1(q=7) >= 0.80 | kappa at the AC1 = 0.80 boundary |
|---|---|---|---|---|
| 0.50 | 0.900 | 90 | 159 | 0.65 |
| 0.70 | 0.916 | 76 | 165 | 0.56 |
| 0.90 | 0.964 | 32 | 174 | -0.08 |
| 0.95 | 0.981 | 17 | 177 | -1.07 |
| 0.98 | 0.992 | 7 | 179 | -4.07 |
| 0.995 (v4: 0.9972) | 0.998 | 2 | 180 | -19 |

Behaviour: kappa's chance term p_e = sum of products of marginals tends to 1 as one code dominates, so kappa collapses to
about 0 even at raw agreement 0.99; with one rater constant (v4) kappa = 0 exactly. AC1's chance term 2p(1-p)/(q-1) tends to 0,
so AC1 tends to raw agreement. There is no "equivalent threshold": AC1 >= 0.80 equals kappa about 0.65 at prevalence 0.5 and is
indifferent to ~20 % disagreement at the prevalence that matters. Matching the strictness of "kappa 0.80 at balanced prevalence"
needs AC1 >= 0.89 (q = 7); matching the same disagreement budget at v4 prevalence needs AC1 of about 0.996-0.998.

Case against the draft as written, then the fix list.

- **Recommendation.** Keep AC1 as the reliability statistic but change the gate before anyone signs (the file is DRAFT_PENDING_SIGNATURES, so edits are free until then):
  1. **Threshold.** Pooled AC1 >= 0.95 (about <= 45 disagreeing cells of 900) instead of 0.80, still with the critical-field rules. State in the prereg that 0.80 would have passed v4 (AC1 0.994) and would pass with 19.9 % disagreement.
  2. **Accuracy co-gate (the missing half).** After joint adjudication, count conditions with any WRONG_*/INFERRED/SHOULD_BE_AMBIGUOUS in a critical field. Proposed: <= 1 of 100 (one-sided 95 % Clopper-Pearson upper bound 4.66 %; 0 gives 2.95 %), and <= 4 of 100 for any-field defects (upper bound 8.9 %; 5 of 100 gives 10.2 %). Both are PROPOSED values for the humans to set; the statistic and the rule form are the point.
  3. **Seeded controls.** Add 10 planted-defect rows (a known-wrong normalised value made by a deterministic edit of a real condition outside the 100) and require each reviewer to flag >= 8 of 10, else that reviewer's file is NOT_COUNTED. This is the only design that can detect a constant-code reviewer in advance; v4 forbade attention checks (R-07) but R1 is a new packet. A reviewer with true detection 0.9 passes with probability 0.93; one with 0.7 passes with probability 0.38.
  4. **Critical set.** Add `duration_judgement` (and `temperature_value_judgement`) to the critical fields for R1. F-01 shows the residual v4 signal is exactly there, and kinetics need duration. The repeated-pair rule (>= 3 of the same ordered pair) would have flagged v4's 4 duration disagreements.
  5. **Informative-cell sensitivity.** Report AC1 and agreement on cells whose status is VALID or AMBIGUOUS only; about 46 % of v4 cells (NA 184 + UNKNOWN 235 of 900) are trivially correct and inflate prevalence.
  6. **Replace `IDENTICAL_JUDGEMENTS`** (F-05) with: file timestamps, free-text `reason_if_not_correct` overlap, and the seeded-control result.
  7. **Source stratification.** Floor of 20 USDA-dialect conditions (F-06), e.g. S-quotas drawn per source family within strata.
  8. **Positive specific agreement** on flagged cells (2 x both-flagged / (flagged by A + flagged by B)) as a printed diagnostic: v4 gives 0.0, which is the "real disagreement" lens AC1 hides.
  9. **Condition-cluster interval.** The bootstrap by condition is right; gate on the lower 95 % bound of AC1, not the point estimate.
- **Governance.** D-027 R-06 says AC1 and PABAK are "diagnostics only" and the Step 07, 15 (G15-g) and 23 (G23.7) cards repeat it; D-075 (Kush) authorises a redo with a statistic "robust to the kappa paradox" but does not edit R-06. The adjudication note itself says a different statistic "would need a NEW pre-registered gate". So the route is legitimate if: (i) a new DECISIONS entry written by Kush amends R-06 for attempt 07.A-R1 only and updates the three cards; (ii) both humans sign before the packet opens; (iii) the report says "gate redefined after a failed gate"; (iv) the v4 FAIL is never relabelled.
- **Agree?** Partly (statistic yes; 0.80 and agreement-only logic no).
- **Risk if ignored.** A PASS that a reviewer reads as shopping for a metric until the gate passes, and a downstream 23b/15b built on a gate that would pass a bad normaliser.
- **Settle.** Amend the prereg (agent, today), humans sign Monday/Tuesday, labels by 13 Nov (soft) / 20 Nov (hard), score with the committed scorer after adding the controls and criteria above. Also give reviewers a validator (`tools` script, run before returning) and a dropdown sheet; v4 needed three file replays.
- **Does 07.A-R1 matter for 25 Nov?** Only as credibility. Even a PASS does not open 23b (prereg s5: 15b also needed, and 15b needs 08b, Steps 11, 12, 14 verdicts and a human-verified test subset). It costs 3-4 h per person, the most expensive human item for the least talk value.

### Q25. Benchmark independence

- **Recommendation.** You cannot argue independence while the system authors are the only reviewers and the gold is the system's own output (F-13 for S, F-12 for P and C). Do four things: (1) **blind-first**: for every S question the reviewer writes the answer from the recipe text before seeing the engine's gold (Step 36 G36-B requires `seen_system_output = false`; anchoring raises expert-LLM agreement from 43.9 % to 71.5 % per the plan's own citation); (2) record KEEP/EDIT/DROP rates per reviewer and Kush-Parv agreement (AC1, with the number of items) as the measure of AI-gold error; (3) an **outside reviewer** (TA, senior student, or food-science acquaintance) for a random 20-item subset: all P3, 5 S1, 5 S2, 5 P1; 1 hour; (4) label the benchmark `MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers` on every slide.
- **Agree?** Agree with the outside reviewer; the blind-first change goes beyond the agent's lean and is the part that matters.
- **Reason.** P and C gold are ledger lookups (mechanical), so independence there concerns who defined strata and tolerances, not human judgement; S gold is engine output, where independence is absent.
- **Risk if ignored.** H1 "supported" is reported on circular gold and exposed in questions.
- **Settle.** Change the review sheet columns before issue (hide `gold_*` for S rows). Cost to reviewers about 2-2.5 h each including P/C checks. Compare their blind answers to the engine gold: that comparison is itself a D3 datapoint (engine vs blind humans, n = 30 questions).

### Q26. Power of H1 (exact McNemar, n <= 30)

The prereg pools S1 + S2 (n = 30); "n <= 30 per block" in the packet overstates. Per block (15) is descriptive only.

Minimum discordant split that reaches two-sided exact p <= 0.05 (project code, `paired_stats.mcnemar_exact`):

| discordant pairs d | 5 | 6 | 7 | 8 | 9 | 10 | 12 | 14 | 16 | 20 | 24 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| minimum split (B4 only : B1 only) | none | 6-0 | 7-0 | 8-0 | 8-1 | 9-1 | 10-2 | 12-2 | 13-3 | 15-5 | 18-6 | 21-9 |
| accuracy difference at n = 30 | | 0.20 | 0.23 | 0.27 | 0.23 | 0.27 | 0.27 | 0.33 | 0.33 | 0.33 | 0.40 | 0.40 |

For a single block of 15, the smallest detectable result is 6-0 (0.40) or 12-3 (0.60). Exact power (alpha 0.05, direction correct), n = 30:

| true accuracy gap (discordant rate, share favouring B4) | power at n = 30 | power at n = 45 | power at n = 60 |
|---|---|---|---|
| 0.30 (0.40, 0.875) | 0.71 | 0.91 | 0.97 |
| 0.20 (0.30, 0.833) | 0.40 | 0.64 | 0.80 |
| 0.15 (0.25, 0.80) | 0.24 | 0.42 | 0.58 |
| 0.10 (0.20, 0.75) | 0.10 | not computed | not computed |

Smallest true gap with 80 % power: n = 30 needs about 0.28-0.33; n = 60 needs about 0.16-0.24. H1 requires both B4 > B1 and B4 > B2 significant
(an intersection-union test: no alpha correction, size <= 0.025 in the direction, but power falls to roughly 0.5 when each comparison
has 0.71).

- **Recommendation.** Accept as a pilot only after fixing S1 (F-13, G-05). Enlarge the S pool to 30 + 30 (the S questions are cheap: engine-drafted, 2-2.5 h of blind answering for 60 items); keep P, C, U, X as is. State the MDE on the slide: "at n = 30 a null result is uninformative; only gaps of 0.25 or more can show". Pre-register one more rule: a recipe appears in at most one S question (check S1/S2 overlap by `recipe_id`).
- **Newcombe.** Method 10 as implemented matches the published formula. Examples from the project code (n = 30): (14,10,1,5): +0.300, 95 % CI (0.091, 0.475), exact p 0.012; (10,8,2,10): +0.200, CI (-0.006, 0.380), p 0.109; (20,5,0,5): +0.167, CI (0.016, 0.318) but exact p 0.0625. The last shows the interval can exclude 0 when the pre-registered exact test does not: tell the audience in advance that the decision rule is the exact test and the interval is descriptive.
- **Agree?** Partly (pilot yes; n = 30 and circularity no).
- **Risk if ignored.** Either a spuriously large effect (circular S1) or a null that is read as evidence against H1.
- **Settle.** Run the power script on the realised discordance; if realised d < 8, say "cannot be significant at this n".

### Q27. Presenting only H1 and H3 as tested, H2 diagnostic, H4 not started

- **Recommendation.** Yes, with wording: "0 of 4 hypotheses confirmed; H1 and H3 piloted at n = 30 and n = 40; H2 diagnostic on re-exposed data; H4 not started". Replace the packet's "tested".
- **Agree?** Yes.
- **Reason.** 29-diag is `PRIOR_EXPOSURE_REANALYSIS` with no pass gate (DEL-2 and the S160 Step 30 run already read these rows); the plan requires 15b and a valid 07.A for any H2 claim. H3 as pre-registered will "pass" almost by construction (F-12 and Q26 above), so calling it tested invites the obvious question.
- **Risk if ignored.** Over-claim, and the talk loses its strongest asset (the failure register).
- **Settle.** Put one slide "what failed and what is still unproven" (07.A, G08-3, D-074 R1 4/60, DEL-2 D7 = D1, unit drop, S1 circularity found in review). Use the claims register in C-eval (G-09).

### Q28. Gold for D3 (state tracker)

- **Recommendation.** No D3 accuracy claim at the talk. Present D3 as "run on 612,782 recipes, 14.6 M events, invented values 0; scored against 7 + 7 committed P1 packets as an engineering score of human-accepted AI drafts". For a claim: >= 30 recipes, annotated blind (no AI prefill) by >= 2 annotators, field-level accuracy with a recipe-cluster bootstrap interval. Sample-size logic (Wilson): to show true field accuracy >= 0.80 when observed 0.90 needs about 54 independent items; with 20 cells per recipe and an intra-recipe correlation 0.2 (design effect 4.8) that is about 260 cells; observed 0.95 with lower bound 0.85 needs about 45 items (about 216 cells).
- **Reason.** Every P1 label is AI-drafted and human-accepted (D-061, D-063, D-066; same model family for both passes; same Mac for A and B, D-064; the SP-002 caveat on quantities). Agreement with it measures shared bias.
- **Risk if ignored.** An accuracy number on the slide that is circular.
- **Settle.** The cheap D3 datapoint is Q25's blind S answers (engine vs blind human, n = 30). P1b needs only Kush's nonce, capacity and budget (5 minutes) but 3-4 more recipes buys little; do it only if the nonce arrives by 12 Nov and human hours remain (it will not).

### Q30. Training licence (Food.com)

- **Recommendation.** Food.com is acceptable for analysis, censuses and internal non-released diagnostics, labelled "licence UNVERIFIED". Do not use it for any learned model that is released, shown as a result, or that depends on units (the source dropped them). Learned rungs are DEFER (Step 35g) and not needed for 25 Nov anyway.
- **Reason.** An uploader's CC0 label on a re-hosted dump cannot grant rights the uploader may not hold in user-submitted recipes; I have not opened the Kaggle page or the upstream terms, so this is a risk statement, not a finding. Wikibooks is CC BY-SA (attribution and share-alike obligations on adaptations); only Gutenberg is `training_allowed = YES`.
- **Risk if ignored.** A released model or dataset with an unclearable component; a hosted demo that shows Food.com text publicly.
- **Settle.** Ask the supervisor in writing (same email as the AI-workflow permission, G-02 below) and check the Kaggle licence field plus the upstream site terms; paper: restrict learned rungs to Gutenberg + Wikibooks or get a written answer.

### Q33. NER role without letting it become gold

- **Recommendation.** Agreement with Rung A as a diagnostic only, plus two guards: (1) every NER-derived link carries `source = NER_MODEL`, a mask and `UNVERIFIED`, and is never consumed by Layer 1 TEXT_STATED nor promoted to an ING link without a deterministic rule or a human; (2) estimate each detector's precision and recall on a human-labelled random sample (200 Food.com lines, 100 Wikibooks/Gutenberg), because agreement of two systems with correlated lexical biases overstates accuracy.
- **Agree?** Yes.
- **Risk if ignored.** NER-filled lots quietly become inputs to composition and the router; a 0.94 DEV F1 (in-domain, TASTEset) is quoted as corpus accuracy.
- **Settle.** 300 lines, about 45 minutes per annotator; report entity-level F1 with Wilson or bootstrap intervals; run on manjot (CPU) or the Mac; no GPU needed for scoring.

### Q34. NER domain shift (no units in Food.com)

- **Recommendation.** Accept now; measure on the same 200 human-labelled Food.com lines (Q33); if FOOD-entity F1 lower bound < 0.90, retrain with unit-drop augmentation (delete UNIT tokens from TASTEset training lines at p = 0.5-1.0), which reproduces the known shift exactly and costs about one GPU-hour on vinayak.
- **Reason.** The shift is understood (UNIT absent) and synthetic reproducibility is possible; a retrain before measuring is effort without a metric.
- **Risk if ignored.** UNIT hallucination or mis-tagged quantities on 85 % of the corpus.
- **Settle.** As above; low priority for the talk (rank 9).

### Q35. Reproducibility

- **Recommendation.** Not enough for a paper. Extend the log additively (new columns, old rows backfilled where recoverable): `input_sha256` (recipe base, ledgers, NER checkpoint), `code_tree_sha256` plus dirty flag (the census JSONs already record `src_tree_sha256`; copy it), `env_lock_sha256` (add a lockfile first), `model_digest` (Ollama digest, embedding model revisions), `seed`, true start and end, determinism check (repeat run, same output hash), `git_commit` verified on the host. Add a `tools/log_run.py` that fills these; add pinned requirements for `.venv312`.
- **Agree?** No (the packet says "runs are logged with code and input hashes"; the header has neither).
- **Evidence.** F-10: 14 rows, start blank 10, end blank 14, output hash blank 3 (`RUN-S171-002`, `RUN-S172-002`, `RUN-S174-001`), no env or input columns, no lockfile, deps unpinned, LLM settings `temperature 0, seed 7, num_ctx 4096, num_predict 200` without model digest (GPU decoding is not guaranteed deterministic and 200 tokens can truncate citations).
- **Risk if ignored.** Results that cannot be re-derived; a run whose commit does not match the code that ran (vinayak has no `.git`).
- **Settle.** Agent task, about 2 hours, before the H1/H3 runs; run H1/H3 three times and report the spread of the LLM-dependent numbers.

### Q36. BBC counts

- **Recommendation.** Counts and aggregates are low licence risk (facts, no expression, not a substantial extraction of the database), provided: no BBC text, recipe ids, ingredient lists, per-recipe outputs or NER spans leave the Mac; small cells are not tabulated by title or author; slides and the hosted demo use no BBC example. The real exposure is the possession and use terms of the A1 dataset, which I cannot see; treat D-003 as binding and ask the supervisor to confirm course use in the same email (G-02).
- **Reason.** Reports that sum BBC and non-BBC (the 36.4 M router census) cannot be reproduced by anyone without BBC.
- **Risk if ignored.** A hosted demo or screenshot with BBC-derived content; a paper whose headline numbers need data nobody can obtain.
- **Settle.** Report family-wise tables plus a "reproducible non-BBC subtotal" line in the paper; demo examples from Gutenberg (public domain) or user-pasted text; keep BBC runs flagged `Mac only` in the compute log.

### Q37. Governance: where is the line

See section B2.1 to B2.3 (rule, table, audit of past decisions, repairs). Short answer: an AI persona decision can never close a human gate, and D-071 as written does not say so for independent-labelling gates.

### Q38. Timeline fallback

See sections D.2 and D.3 (calendar and fallbacks). Short answer: nothing on the critical path to H1/H3 tolerates a slip beyond Tue 17 Nov (benchmark freeze) and Wed 18 (runs); 07.A-R1 can slip to 20 Nov; the AA verification can slip to Tue 17.

### Q39. Is the lot-state layer worth doing before 25 Nov?

- **Recommendation.** Cut it for 25 Nov. Keep at most a design slide of the section 5.2 table and, if time allows, a 20-recipe demonstration on Gutenberg/Wikibooks (units present).
- **Agree?** No (the packet ranks it item 1, high/high).
- **Reasons.** (1) Food.com has no units, so composition is presence-only for 85 % of the corpus (Q8). (2) ING to SR crosswalk is 0 % resolved and needs human verification of hundreds of rows, competing with the same two humans' critical path. (3) Every output would be MODEL_DERIVED / NON_CITABLE with no gold: pH flags, mixture composition and interaction edges cannot be evaluated, and all 32 MECH entries are unreviewed, so the layer cannot show what it claims. (4) No hypothesis H1-H3 depends on it; H4 is out of scope. (5) The router after lot state is still DIRECT/UNKNOWN (F-11), so the headline number does not move. (6) No DECISIONS entry authorises it (D-077 covers heating layers and NER; the packet calls section 5 "not frozen"). (7) The plan's own Step 35 is a chemistry representation ladder (molecule to cuisine), not a lot-state encoder; Q29's "rung 0" reuses the Step 35 name for something else.
- **Risk if ignored.** The agent's time goes to an unevaluable layer in the three weeks that decide whether H1/H3 and the first SIMULATE exist.
- **Settle.** If Kush insists: a 1-recipe vertical slice with units stated, composition as USDA-derived intervals, shown as design, not result.

### Q40. SSOT v16

- **Recommendation.** Do not apply before the talk. Freeze v15 as the authority cited by every prereg; publish a one-page addenda list (D-077 layers, physical SVAR gap, any v16 items that touch a claim) and apply v16 after 26 Nov with human sign-off.
- **Reason.** Preregistrations cite v15 sections; changing the authority between registration and run invalidates the "registered before" claim, and the change set is a draft nobody has reviewed.
- **Risk if ignored.** A moving authority during the sprint; every prereg needs a re-sign.
- **Settle.** One DECISIONS line by Kush: "v15 governs through 26 Nov; v16 not applied".

---

## B2. Governance (full answer to Q37)

### B2.1 The rule, and where AI-persona decisions may NOT close a gate

Proposed rule (crisp enough to enforce): **an AI persona (ksh, prv) may tighten, defer, withdraw or refuse; it may never loosen, close or sign.** Anything that moves an item to PASS, FROZEN, SIGNED, VERIFIED, UNSEALED or RELEASED is human only.

| Class | What | Who may close |
|---|---|---|
| H1. Signature acts | pre-registration signatures; freeze approvals (`approved_by`); seal and unseal; nonces and seeds the drawing agent must not choose; amendments to signed records; DECISIONS entries that amend a ruling (R-xx) | named human, own hand (own signed commit) |
| H2. Independent-judgement gates | 07.A labels; 07I-C; G08-H edge audit; G21.6 blind dual MECH review; G23 case labels (not only MECH authors); Step 10/11 row verification (D-076: "Kush and Parv each verify"); Step 19 annotation; D5 review and blind-first gold; any gate whose statistic assumes independent raters | the two humans separately; an ksh/prv verdict cannot stand in, and agreement between ksh and prv is not inter-rater evidence (D-072 itself says so) |
| H3. Outcome-contingent changes | any change of statistic, threshold, exclusion or gold after an outcome of that analysis has been seen (R-20); relabelling a failed gate | nobody; a new pre-registered attempt only |
| H4. Facts only a person knows | professor's permission (D-045 W3); authorship and DEL contributions; Parv's own confirmations; capacity and budget | the person |
| H5. Licence, safety and release | licence interpretations; locked-test unsealing (H5); claim release (H6); any safety-relevant claim | humans (plus supervisor where applicable) |
| A. AI persona may decide (D-071) | engineering and design choices among drafted options; triage and ranking; accepting or rejecting a code fix; adding a negative result; withdrawing or not landing a change (D-074 pattern); drafting anything | ksh/prv, recorded "AI under D-071" |

### B2.2 Did any past decision cross the line?

| Decision | Finding | Crossed? | Repair |
|---|---|---|---|
| D-045 W1-W3 | AI verdict first, humans review; W3 professor permission "as stated by Kush", no written copy in repo | No crossing; an unverifiable H4 fact | Written permission (G-02) |
| D-046 (3 Nov) | THR-19P-01..35 recorded `signed_by Kush Tokas; Parv Goyal (Parv's ok relayed by Kush)` | **Yes, borderline**: a signature recorded for a person who did not sign (D-071's own list names "Parv's own written confirmations" as human-only) | Parv writes or signs her own line ratifying D-046 and the other relays |
| D-060 to D-066, D-070 | Human accepts ksh/prv drafts ("passok", "all passed"); labels `MODEL_ASSISTED_HUMAN_ACCEPTED, human_edits = NONE`; B built on Kush's Mac (D-064) | No gate closed as human gold; labels honest. Weak but disclosed | Keep "human-accepted AI draft" wording; never report as human annotation or timing |
| D-068 | The agent appended the 15.0 ruling (a human-only record per the 15a.R rule and, afterwards, D-071) on a verbal waiver; the 15a.R seed was generated by the agent at Kush's instruction | **Yes**: a human-only record authored by the agent, though with an explicit human waiver and a recorded instruction | Kush ratifies D-068 in his own signed commit before 15b relies on it |
| D-071 | Kush delegates Parv's decisions ("prv is Parv"); Parv's consent is not on record; scope does not exclude independent-labelling gates | **Structural gap** | Parv's own confirmation; add the exclusion list (D1) as a new D-entry |
| D-072 | J4 read by two AIs of one family (kappa 1.0); parser change decided and deferred past the talk | No (engineering decision, tightening-neutral, caveat recorded) | None |
| D-073 | Census reason fix decided by ksh | No | None |
| D-074 | R1 rule not landed on ksh labels (4/60); prereg written by the agent, never signed, called "pre-registered" | No gate closed (a conservative decision). The word "pre-registered" is loose for an unsigned AI file | Call such files "dated AI draft" unless a human signed |
| D-075, D-076, D-077 | Kush decided; D-075 changes the 07.A route without editing R-06 | No crossing; R-06 amendment missing (Q24) | Amend R-06 for 07.A-R1 only |
| 07.A v4 | Amendment signed after labels; Parv's "go with Kush's" relayed; Parv's file replaced after the tool flagged an invalid row | Process deviation, all recorded | None; keep recorded |

Result: no D-071 decision (D-072 to D-074) closed a human gate. Two pre-delegation or waiver records need written repair (D-046, D-068), and D-071's prv half is unratified.

### B2.3 Enforcement and clean-up (cheap)

- Make signature a control: require the commit that adds a signature file to be SSH- or GPG-signed by a human key listed in the repo; the freeze and prereg checks (`freeze_records.prereg_signed`, `freeze_problems`) verify `git log --format=%G? -1 <file>` plus the prereg sha256. Reuse the 29-diag pattern for 07.A-R1, D5 and the AA prereg (F-07).
- Rename `FREEZE_15A_BOOTSTRAP` to a 29-diag snapshot name and state in the record that Step 15a is not satisfied while 08a G08-3 is FAILED (F-08).
- In every `Approver` field write `ksh-AI` / `prv-AI`; never "(Parv)" or "(Kush)" next to an AI decision.
- A `closer_type` column (HUMAN / AI_PERSONA / AGENT) in the gate and run registries, with a validator that rejects AI_PERSONA on classes H1-H5.
- AA pilot firewall: store SIM-VAL PDFs outside the agent's reach until the CAL fit hash is committed, or have a separate session extract SIM-VAL rows (F-09).

---

## C-eval. Missing evaluation and governance items, mapped to plan steps

| ID | Missing item | Why (evidence) | Plan step / gate | Owner | Cost | Before 25 Nov? |
|---|---|---|---|---|---|---|
| G-01 | Accuracy co-gate, seeded controls, critical-set and threshold changes for 07.A-R1 (Q24) | F-01 to F-06 | Step 07 card; G15-g; G23.7 | agent drafts, humans sign | agent 2 h | Yes (before signing) |
| G-02 | Written permission from the supervisor for the AI-assisted workflow, AI-persona delegation, Food.com use and BBC course use | D-045 W3 has no written copy; Q30, Q36 | Step 01 authority / DECISIONS | Kush (email) | 15 min | Yes |
| G-03 | New D-entry: D-071 exclusion list (D1), Parv's own ratification of D-071, D-046; Kush's own ratification of D-068; R-06 amendment for R1 only; "v15 governs" (Q40) | D2 | DECISIONS | Kush, Parv (own hand) | 30 min each | Yes (Mon 9 Nov) |
| G-04 | Hash-bound signature for 07.A-R1, D5 and AA preregs, signed-commit verification | F-07 | freeze_records; Step 15 | agent | 2 h | Yes |
| G-05 | H1 S1 fix: blind-first gold; B4 not given the gold; retrieval pool restricted to `steps[:cut]` for B1/B2/B4; scoring free of linker asymmetry (report per-rung link-failure rate or have a rung-blind human score a sample) | `h1_rungs.state_block`, `d5_state`, test passes all `STEPS` with cut = 2 | Step 36 G36-B, D5 prereg s2-s4 | agent, then humans | agent 3 h | Yes, before sheets issue |
| G-06 | S pool 30 + 30, one question per recipe, S recipes excluded from any Rung A/lexicon tuning pools (check overlap with the D-073/D-074 seeded samples and P1 packets) | Q26; leakage | Step 15 / 07I-S split groups; Step 36 | agent | 1 h | Yes |
| G-07 | H3 re-specification: sign test as the gating exact test (needs >= 5 questions with a B2 unsupported claim and B7 zero; one-sided p = 0.5^5 = 0.031) with the bootstrap as interval (the bootstrap needs only 3 of 40 questions, p about 0.044, anti-conservative for rare events); compare with B5T; co-primary coverage; false-abstention on P1 and P2; selective risk with Clopper-Pearson bounds; the prereg text mixes "exact one-sided test" with a bootstrap | `paired_stats.ucr_diff_upper95`; plan G36-ABST, G36-DEC | Step 36 | agent + sign | agent 3 h | Yes, before freeze |
| G-08 | Independent claim audit: human check of 40-60 randomly drawn numeric or directional claims per rung (B2, B5T, B7), rung-blind, including relevance (right ingredient, process, target), and C17 precision/recall of "unsupported" against those labels; C17's NUM regex counts only percentages and 0.x or 1.x decimals | `claims.py` | Step 36 AIS audit; G36-B | humans 1 h each | Yes (Thu 19-Fri 20 Nov) |
| G-09 | Claims register: one table mapping every slide sentence to report, hash, status (MEASURED / PILOT / DIAGNOSTIC / NON_CITABLE / FAILED) and intervals; plus the negative-results register updated (07.A, G08-3, D-074, DEL-2, unit drop, S1 circularity) | Q27 | Step 36 / report M8 | agent | 2 h | Yes |
| G-10 | Cluster-aware inference for P/C blocks: questions from USDA R6 (one lineage cluster) and Bognar (one cluster) are not independent sources; cluster by (source family, ingredient) and report per-family results | Step 15 card ("USDA and Bognar are one cluster each") | Step 15 split registry; Step 36 | agent | 1 h | Yes |
| G-11 | Run manifest standard and lockfile (Q35); LLM digest and three-run spread | F-10 | Step 15 G15-e, G15-R | agent | 2 h | Yes |
| G-12 | Decision on what "supported" means for a cited number (value within tolerance of a cited row is syntactic; require the cited row's ingredient, process and target to match the question) and scope H3 as "evidence-conditional faithfulness", not truth | `claims.py` TOL = 0.03; F-12 | Step 36 C17 version bump | agent | 2 h | Yes |
| G-13 | Safety layer for the hosted demo: refuse food-safety questions (pathogen, "safe to eat") explicitly; X-block includes 3 safety items with gold REFUSE; SAFETY_UNKNOWN is already in every reason code | packet s9 item 3 | Step 36 router controls | agent | 1 h | Yes |
| G-14 | Hosted-demo data governance: no BBC, no Food.com verbatim text, no API key in the tree, no logging of user inputs without notice | Q36, Q30 | M6 | agent + Kush | 1 h | Yes |
| G-15 | Layer 2 as features (Q1): mandatory ablation, and no "evidence_supported" label from scenario-driven runs; SIMULATE outputs from defaults are brackets | D-077 | Step 31 | agent | later | No (post-talk; flag in report) |
| G-16 | Pre-announce Step 27 RESEARCH_ONLY for the AA pilot (4 SIM-VAL papers < 5; possibly 3) | F-09 | Step 27, G15-f | agent | 0.5 h | Yes |
| G-17 | Rater calibration: 10 shared items with discussion before blind work, dropdown form + validator script | F-02 | Step 07, 10, 19, 36 | agent | 1.5 h | Yes |
| G-18 | Reviewer burden log: minutes per item and KEEP/EDIT/DROP rates (plan requires minutes per item) | Step 36 card | Step 36 | humans | 0 | Yes |
| G-19 | Router case set (60-100 dev) with a not-only-MECH-author labeller; false-activation CP bound | Step 23 G23.1 | Step 23 | later | later | No (descriptive 100-item UNKNOWN check only) |
| G-20 | Outside food-science reviewer for MECH entries that fire and for 20 benchmark items | packet s9 item 11 | Steps 21, 36 | Kush finds | 1-2 h | Partly |
| G-21 | Prior-exposure and forking-paths log: every prompt, rung or threshold change after the freeze is a dated amendment; freeze LLM, prompt text and `num_predict` in the prereg | D5 prereg s5 | Step 36 | agent | 0.5 h | Yes |

---

## D. Ranked, cut-down plan to 25-26 Nov (today Sunday 8 Nov)

Owners: H = human (Kush, Parv), A = agent. Servers: manjot = this server (CPU overflow, validators, scorer runs, bootstraps), vinayak (A100 x2: Ollama LLM runs, router and derived census re-runs), Mac (authoritative ledgers, BBC only, demo build, private seeds and signatures).

### D.1 Ranking (value for the talk; paper value in the last column)

| Rank | Item | Why | Human hours (each) | Paper value |
|---|---|---|---|---|
| 1 | Governance pack G-02, G-03, G-04 and preregs signed | Unlocks everything; cheap; fixes the record | 1 | High |
| 2 | D5 benchmark with the H1 and H3 fixes (G-05 to G-08, G-12), then freeze and runs | The only hypothesis evidence the course grades | 3 + 1 | High |
| 3 | AA pilot to PARAM rows, fit, SIM-VAL (RESEARCH_ONLY) and router re-run (first SIMULATE count) | First non-lookup number; the physics-chain unblocker | 2.5 + 0.3 | High |
| 4 | M4/M6 demo (D4 retrieval with abstention; hosted or cached) | The "story" artefact; low risk | 1.5 rehearsal | Medium |
| 5 | 29-diag (signature, one CPU run, memo) | 2 h agent; resolves the D7 = D1 shortcut question; honest H2 diagnostic | 0.3 | Medium |
| 6 | Claims register, failure slide, report and slides from real results (M8) | Prevents over-claim | 3 | Medium |
| 7 | 07.A-R1 labelling and score | Credibility of COND; opens nothing before 25 Nov | 3.5 | High |
| 8 | Reproducibility hardening (G-11) | Cheap; needed anyway | 0 | High |
| 9 | NER human sample (Q33, Q34) | Low | 0.75 | Medium |

### D.2 Calendar

| Date | Agent | Human | Server |
|---|---|---|---|
| Sun 8 Nov | Amend 07.A-R1 prereg (G-01), D5 prereg (G-05 to G-07, G-12), sign-file mechanism (G-04), D-078 draft (D1 exclusion list); S-pool overlap check; rename freeze record; extend run log header | none | manjot: scorer tests; Mac: drafts |
| Mon 9 | Re-issue packets and blind-first review sheets after signature; validator script | Kush and Parv read and sign preregs (about 45 min each); Parv writes her ratification; Kush ratifies D-068; Kush sends the permission email (G-02) | Mac |
| Tue 10 | AA CAL extraction continues; start 29-diag run if freeze approved | Kush: A4 due today, no asks | Mac: 29-diag; vinayak: idle or census funnel |
| Wed 11 | D5 sheets live; 07.A-R1 sheets live | Kush: download the 5 PDFs (20 min, browser); start D5 review | |
| Thu 12 | AA extraction complete, verification sheets issued; funnel and cold-coverage tables (Q20, Q22) | Kush: other commitment, no asks | vinayak/manjot: census funnel |
| Fri 13 | 07.A-R1 collects returns (soft deadline) | 07.A-R1 labels due (soft) | |
| Sat 14 to Sun 15 | | AA verification, 2-3 h each, due Sun 15 | |
| Mon 16 | Collect D5 sheets | D5 review due | |
| Tue 17 | Reconcile; freeze benchmark (hash, signed commit); AA fit freeze (hash) then open SIM-VAL; router re-run | Joint reconcile 30 min; sign freeze | vinayak: router census (about 25 min) |
| Wed 18 | H1/H3 runs, three repeats, `temperature 0`; stored packets | | vinayak: Ollama on A100 |
| Thu 19 | Results, intervals, power note; claim-audit sheets | | manjot: bootstraps |
| Fri 20 | 07.A-R1 score (hard deadline); claims register | Claim audit 1 h each | manjot |
| Sat 21 | Demo hosted or cached fallback; report draft | | |
| Sun 22 to Tue 24 | Slides and report from real results only | Edit pass (3 h each); rehearsal Tue | |
| Wed 25 to Thu 26 | Presentation | | |

### D.3 Fallbacks if human items slip

| Item | Soft / hard deadline | If it slips | What the talk says |
|---|---|---|---|
| Preregs signed | Mon 9 / Wed 11 | Nothing downstream may start (labels cannot open before signing). If one human is unavailable, record "signed by Kush; Parv pending"; do not record a relayed signature | "Pre-registered by one author; second signature pending" |
| D5 review | Mon 16 / Tue 17 (freeze Wed 18 latest) | Freeze the items both reviewers kept by Wed 18 (the overdraft design keeps blocks full; minimum 40 reviewed items); drop P2/U/X to descriptive. If < 40 reviewed: no H1/H3 numbers | "Benchmark drafted, N reviewed; H1/H3 not run" is acceptable; do not present runs on unreviewed AI gold |
| AA verification | Sun 15 / Tue 17 | Verify only the 16 CAL rows from the 7 PDFs already fetched; skip the 5 browser PDFs (SIM-VAL then has <= 3 papers, say so) | "AI-extracted candidate rows, N verified; fit frozen; SIM-VAL k of N inside the interval; RESEARCH_ONLY" or, with 0 verified rows, "no SIMULATE route exists" |
| 07.A-R1 | Fri 13 / Fri 20 | Present as "second attempt pre-registered, labels pending"; it changes nothing the talk shows | Status line only |
| 29-diag | sign by Thu 12 | Drop; keep the DEL-2 D7 = D1 suspicion on the failure slide | "Diagnostic not run" |
| Hosted demo | Sat 21 | Cached answers for 15-20 demo queries and a screen recording; the A100 tunnel is a single point of failure | Live local demo with Gutenberg examples |
| Governance pack | Tue 10 | Ship with "relays unratified" disclosed in the report's method section | Honest limitation |

---

### D.4 CUT list (explicit)

| Cut | Reason |
|---|---|
| Lot-state [K] full-corpus run, ING to SR crosswalk verification queue, mechanism condition-window registry, interaction edges (Q39) | No evaluation possible; competes for the same human time; Food.com has no units; moves no H1-H3 number |
| Non-heat process families beyond what manjot already runs; surface two-zone model; shape factors; equipment and altitude (Q3-Q6) | Out of the hypotheses; every output NON_CITABLE |
| Step 35 rungs over lot-state sequences (Q29); learned rungs (35g); process-response similarity (35f) | Plan card says 35g default DEFER; 35 is a chemistry ladder; no non-circular target |
| P1b pilot wave (nonce) and Step 35 v2 signature | Little gain per human hour; do only if supplied unprompted |
| SSOT v16 application (Q40) | Moves the authority under live preregs |
| H4, D2, Steps 20, 28, 33, 34, FlavorTwin, multimodal | Already out of scope; keep out |
| Router re-run "with lot state" (packet rank 8) | Keep only the re-run with PARAM (rank 3) |
| New DIRECT-coverage targets and any percentage headline for the router | Meaningless denominator (F-11); replace with the funnel |
| Per-block (15) H1 inference | Cannot reach significance except at 6-0 or 12-3; descriptive only |
| NER retraining before measuring (Q34) | No metric yet |

### D.5 What the paper needs later (not before 26 Nov)

| Need | Why | Step |
|---|---|---|
| 15b freeze with a valid 07.A and an accuracy co-gate result, 08b, Steps 11/12/14 verdicts, human-verified test subset | HARD gates for any condition-dependent claim | 07, 15, 23b |
| >= 40 dual-verified literature kinetic rows (D1) and >= 10 held-out clusters per headline split; SIM-VAL >= 5 groups | G15-c, G15-f; the pilot has 4 | 10, 11, 15, 27 |
| Locked benchmark >= 240 with blind-authored gold, outside food-science labeller, one sealed read per claim | G36-B, G36-LOCK; D5 is a pilot | 36 |
| D3 gold >= 30 recipes, blind, two annotators | Q28 | 19 |
| Router case set (>= 150 locked, labeller not a MECH author), false-activation Clopper-Pearson bound <= 0.05, recall on complete-input positives >= 0.70 | G23.1, G23.3 | 23 |
| Human or expert review of the mechanisms and windows that matter | G21.6 | 21, 22 |
| Layer 2 ablation and an end-to-end check against a recipe with measured retention | Q1; validated model with assumed inputs is not a validated output | 31, 33 |
| Reproducibility package: lockfile, run manifests with input, code, env and model hashes, determinism checks, non-BBC reproducible subtotal | Q35, Q36 | 15 |
| Licence clearance (Food.com, Phenol-Explorer redistribution, Wikibooks share-alike) in writing | Q30 | 06, 15b.R |
| Paper-grade Step 29 with cold splits and the cap-stratified result; D7 = D1 explained | H2 | 29 |
| Novelty check against the literature before any claim (R-20) and an AI-use and contribution statement | Course and venue norms | 01 |
