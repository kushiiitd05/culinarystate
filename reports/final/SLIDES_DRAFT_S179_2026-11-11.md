# CulinaryState — Group 17

Kush Tokas · Parv Goyal

Draft, 11 November 2026. **AI_DRAFTED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**
Talk date, duration and author contributions require confirmation. Counts and IDs only; no recipe text.
All diagnostic figures retain the labels shown here. This Markdown deck is for author review, not a final export.

---

# What we built

- Recipe-state extraction and deterministic replay.
- A process-effect evidence resource with explicit missingness and provenance.
- Evidence-aware retrieval, answer routing and abstention.
- A narrow ascorbic-acid kinetics pilot, **NOT_VALIDATED / RESEARCH_ONLY**.

The engineering pipeline exists; its construction does not establish the proposal's scientific hypotheses.
Source: `FINAL_REPORT_DRAFT_S179_2026-11-11.md` and the cited component reports.

---

# Scope and evaluation

**MODEL_ASSISTED_GOLD / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

D5 frozen benchmark: **74 questions**; S1=12, S2=12, P1/P2/P3/C=10 each, U/X=5 each.
The S questions use AI_DRAFTED_GOLD. No independent human gold or inter-rater agreement is claimed.
Near-duplicate leakage is not controlled.

Full H2, H4 and later learning lanes are not run before the talk. Step 35 is designed, not run.
Sources: D-089, D-090; `registry/h8_scope_cut_register_v1.csv`.

---

# D1: imported evidence and missing conditions

**E3_UNVERIFIED / COND_UNAUDITED / BOOTSTRAP_UNVERIFIED / NON_CITABLE.**

**17,978 ACTIVE rows**, **0/40** hand-verified D1 literature rows.
All rows are E3. Both temperature and duration are stated on **1,575 rows**; pH is UNKNOWN on all rows.
An imported row is not an independently checked primary experiment.

Figure candidate: `reports/s178/evd/fig_evd_coverage_by_family_v2.svg`.
Preserve its full-corpus versus sampled denominators in the caption.
Source: `sections/S179_D1_evidence_resource_DRAFT.md`.

---

# D3: deterministic engineering, weak gold agreement

The replay corpus has **599,971 non-BBC instruction texts**.
**12,046/12,046** selected texts reproduce across process hash seeds.
**12,774/599,971** texts fail an invariant. Structural consistency is not recipe-event correctness.

Non-independent gold comparisons use the rule compiler, not a direct Rung A EventGraph scorer.
The P1 set has **7 recipes** and HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND labels; its handbook requires revision.
No independent accuracy claim is made.

Sources: `sections/S179_D3_state_tracking_DRAFT.md`,
`reports/s178/corpus/replay_invariants_corpus_v2.json`. Split: near-duplicate leakage not controlled.

---

# H1: rule not met

**NON_CITABLE / MODEL_ASSISTED_GOLD / CIRCULAR_SELF_CONSISTENCY_ONLY / NO_HUMAN_SIGNOFF_D085.**

Accuracy on **24** S questions: B0 **2/24**, B1=B2=B4 **6/24**.
B4 versus each comparator: **4 discordant pairs**, exact two-sided McNemar **p=1.0**.
**RULE_NOT_MET**; the small sample does not establish equivalence.

The raw score has H1 NOT_COMPUTED. D-092 uses the separate rung-blind resolution supplement, retained beside it.
Sources: `reports/del5/d5_score_v1_D085/d5_h1_after_rung_blind_check_D085.json`; D-092.
Split: near-duplicate leakage not controlled.

---

# H2: diagnostic, no direction established

**DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / PRIOR_EXPOSURE_REANALYSIS /
PROVISIONAL_08A / COND_UNAUDITED / NO_HUMAN_SIGNOFF_D085.**

On the provisional Phenol-Explorer study-key split, process-mean loss minus ingredient-mean loss is
**0.0992 [−0.0446, 0.2401]**, **362 rows / 20 clusters**. The interval crosses zero.
USDA and Bognár each have one lineage group; no study-disjoint estimate exists there.
D7 equals D1 on the Phenol-Explorer random predictions.

Full H2 is **DECLARED_NOT_RUN**. The G08-3 lineage audit failed; publication keys are provisional.
Source: `sections/S179_H2_and_lineage_statements_DRAFT.md` and 29-diag memos.

---

# D4/H3: a favourable sign test does not pass the rule

**DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

B7 is rule-based evidence-sufficiency abstention, **uncalibrated**.
The unsupported-claim sign test favours B7 **16–0**, two-sided **p=0.000030517578125**.
But on P3, B7 abstains **0/10**, versus B2 **3/10**: **H3 RULE_NOT_MET**.

NEG-0051: gold uses an exact/parent-food boundary; the decision layer admits broad cross-food evidence.
The 30-claim audit was NOT_RUN; it could not reverse the failed conjunction.
Source: `sections/S179_D4_retrieval_and_abstention_DRAFT.md`; D-092.

---

# Retrieval and routing limits

**DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

B2 retrieval recall is available on **20 questions**, with plain R@1 **0.2** and R@10 **0.375**.
The compatibility-recall values contradict their explanatory note; no compatible-recall claim is made.
Source-family stratification is not a train-source-held-out experiment.

Router accuracy is **6/10** with branch gold, **INCOMPLETE_GOLD_BRANCH**; this is not accuracy over all 74 questions.
Source: frozen D5 score JSON; D4 section documents the field paths and missing coverage.

---

# AA pilot: conditional diagnostic only

**DIAGNOSTIC / NON_CITABLE / AI_PRECHECKED / NO_HUMAN_SIGNOFF_D085.**

Frozen Model A: **7 rows, 2 papers, 4 residual degrees of freedom**.
Ea **64.40 kJ/mol**. Conditional Student-t 95% interval **[35.57, 93.22] kJ/mol**;
the separately reported asymptotic profile interval is narrower and uses a different calibration.

Practical precision: **NOT_ASSESSED**, no locked precision criterion. **NOT_VALIDATED / RESEARCH_ONLY**.
Model B sensitivity and separate-context SIM-VAL extraction/precheck are complete.
The precheck leaves **0 eligible held-out rows**; no prediction/error metric is emitted.
PARAM/domain provenance and production calibration remain incomplete.
Sources: D-091; `reports/step10/identifiability_report_v1.md`.

---

# What the results cannot establish

- No independent human-gold H1 result or inter-rater result from AI personas.
- No passed H3 conjunction, calibrated B7 abstention or independent-study H2 generalisation.
- No validated recipe simulator, food-safety advice or whole-system reliability claim.
- No full H4, FlavorTwin, learned Step 35 or later-lane result before the talk.
- Failed 07.A, G08-3 and the handbook revision requirement remain visible.

Original results, deviations and negative findings are retained in the report and release card.
Next: resolve the exact learned-model artifact and scientific provenance gaps, then author edits and an actual
timed rehearsal. A dated amendment may create a new experiment; it cannot replace the original failed result.

---

# Local completion — 12 November

**ENGINEERING_DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

- Restored checksum-matched tier-1 data; frozen D5 exposure audit now covers all selected recipes.
- All 79 P/C gold EVD IDs already appear in DEL-2; shared evidence is disclosed.
- Separate strict-v2: 1,000 metadata calls, zero retention figures without exact context.
- 53 physics steps, 141 numeric display fields: zero missing provenance in this sample.
- Public-filtered and local loopback HTTP checks pass. No hosted deployment claimed.
- Exact frozen NER checkpoint still absent; optional v3 checkpoint was not substituted.

Sources: `reports/s179/d5_frozen_split_leakage_v3.md`, `strict_runtime_audit_2026-11-12.json`,
`strict_http_smoke_2026-11-12.json`, `optional_model_bundle_check_2026-11-12.json`.
Original failed gates and scientific limitations remain unchanged.

---

# Architecture freeze — 15 November

**DIAGNOSTIC_ONLY / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

Pipeline frozen: Event IR → `S_t=(G,C,Q,Y,P)` → invariant validator → evidence compiler →
claim packet → verbalizer → claim verifier with template fallback.

- Steps 1–10 complete. **No new architecture**: every item already had an SSOT-v16 CR.
- Compatibility schema now carries **all 13 axes**, not salt/acid/lipid. 9 implemented · 2 in compiler · 2 schema-only.
- An unavailable axis stays UNKNOWN **with a reason** — never dropped.
- Unit suite 5,960 passed. 116 decisions, **none without an approver line**.

Source: `sections/S180_freeze_results_DRAFT.md`. D-134/135/136 are AI-delegated; human sign-off owed.

---

# Layer-1: the validator decides, and here it had to

**DIAGNOSTIC_ONLY · no gold · not accuracy.**

Three model runs, 60 sealed hard cases, same prompt contract:
**zero `(event_id, field)` slot agreement in every pair.** They never picked the same event to answer about.

- Not a capability failure: 108 returns, **schema 1.000, spans 100%, numeric attempts 0**.
- Cause: `condition_profile_id` was a **reference field with no referent** — so `pan`, `chicken`, `bowl_content` passed as condition profiles.
- Removed it. Coreference triggers have no licensed destination; `VNEXT_FAT_STAYS` was already resolved by the rule.
- **LLM surface is now one field on one trigger** → 13 accepted proposals, **none graded**.

That is what "rules first, LLM only on ambiguity, validator decides" converges to.
Figure: `fig_s180_2_layer1_surface`. Recorded numbers kept; prereg amendment A3 declares the gate change.

---

# pH: the table arrived, and tomato is still not acidic

**FDA/CFSAN 2003, public domain · `UNVERIFIED_CROSSWALK_AI_DRAFTED` · human verification owed.**

479 rows → **140 ingredient bands**. 31 acidic · 101 low-acid · **8 inconclusive**.

- Earlier limitation: "no sourced pH table, so tomato sauce is not yet acidic."
- The table is now here. The system **still** declines — tomato is **4.3–4.9**, straddling 4.6.
- **No midpoints, no clipping** (D-013). An interval crossing the threshold is `INCONCLUSIVE`, not rounded to a side.
- `C_t` stays **unwired** (D-136): the table measures the ingredient **as purchased, not the lot in the pot**.

Figure: `fig_s180_4_ph_bands`. Existing pH coverage figures are unchanged and remain accurate as measured.

---

# 72B vs 7B: scale helps at choosing, not at grounding

**DIAGNOSTIC_ONLY · AI_DELEGATED_D085 · no gold · not accuracy.**

Same 60 sealed cases, same prompt, 60/60 answered by both.

| | 7B | 72B |
|---|---|---|
| Values naming a real choice | 7/14 — 50% | **13/16 — 81%** |
| Spans that ground the value | **0/13** | **0/16** |

- 72B avoided every 7B failure mode, and found two alternatives 7B missed — one a **lipid swap**.
- Neither produced a single usable span. `frying_fat_or_butter` → span `'out 5 mm).\nHeat t'`.
- **The models read correctly and then report the wrong location.**
- Under the grounding rule the directive always required, **both arms accept zero**.

Registered in advance (amendment A4) as a reportable result, not a failed run.
**Span grounding, not model scale, is the binding constraint on Layer-1.**

---

# Contributions and questions

**Author contribution statement pending from Kush and Parv.**

References and artifact index: `FINAL_REPORT_DRAFT_S179_2026-11-11.md`, `RELEASE_CARD.md`,
`registry/compute_runs_v1.csv`, `registry/negative_results_register_v1.csv`, and round-6 acceptance audit.
Before presenting: confirm slot/length, finish report/deck leakage checks, export the approved deck and run it timed.
