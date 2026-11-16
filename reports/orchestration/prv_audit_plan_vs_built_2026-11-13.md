# prv audit — SSOT v15 / original plan vs what was built vs what was cut (13 Nov 2026)

Auditor: **prv (AI, D-085)**, at Kush's request ("for audit use prv"). AI_PRECHECKED · NON_CITABLE ·
AI_VERDICT_PENDING_HUMAN_REVIEW. Sources are cited per row; nothing here changes a frozen result or decision.

## 1. Was state change the plan, or a drift?

**It was the plan.** SSOT §5.1–5.2 (L667–681): working title *"From Ingredients to States: Selective Process-Effect
Reasoning…"*; central RQ *"Can explicit modeling of food-state transitions and process-induced effects improve
retrieval-augmented culinary guidance…"*. §4 (L524–666) makes **food state transitions the shared research spine** of
both projects, and §112 (L6330–6374) calls state-transition learning "the core research bridge".

The intended layering was:

| Layer | SSOT | Role | Data it needs |
|---|---|---|---|
| State graph (what is in the pot, which entities merge/split/transform) | §4, §62–63, §106 | RQ1/H1 backbone | recipe text — **available** (612,782 recipes) |
| Process effects (what a process does to nutrients/texture) | §5.3 RQ2/H2, §201 | grounding for answers | evidence rows — **available** (EVD 17,978 rows, 3 sources) |
| Kinetics (how fast, at what T: order, k, Ea, Arrhenius, Weibull) | §210–211 (L18617–19700) | quantitative SIMULATE mode under H2 | **raw time-course lab data with assay basis** — scarce |

So state change was built first because it is the spine **and** the only layer whose data exists at scale. Kinetics
was always the top, data-hungry layer, gated by validation.

## 2. Kinetics: what was planned, built, and why it narrowed

| Planned (SSOT / 36-step plan) | Built | Why it stopped there | Evidence |
|---|---|---|---|
| Step 09 KIN/KINPT kinetic-experiment + raw time-point tables, dual blind extraction | schemas, units (D-079 KINETIC unit type, 11 units minted), extraction machinery | few lawful open-access papers report raw series; numeric extraction error rates 47–88 % in literature (change log Step 09 WHY) | `36_step_change_log_v2.md` Step 09; D-079 |
| Step 10 focused-system choice by pre-registered rule | **ascorbic acid (AA) chosen**; chlorophyll fallback; acrylamide "never first" | chosen by validation-data availability, not impressiveness | change log Step 10; D-076 |
| AA pilot fit | **Model A**: shared Ea 64.4 kJ/mol (SE 10.4), 7 rows, 2 papers, 70–95 °C, dof 4 | two papers is the fitter's minimum; 5 of the licence-checked papers NOT_ACQUIRED (sites refuse scripts; human browser download never done) | D-091; `aa_pilot_model_a_fit_D085.json` |
| Step 27 held-out simulator validation (≥5 lab groups) | SIM-VAL extraction 19 rows, precheck 6 PASS / 12 FLAG / 1 REJECT → **0 computationally eligible** | SIM-VAL had 4 papers vs minimum 5; assay basis incompatible | D-084 item 4 (descriptive pilot accepted as recorded deviation); Parv S204 |
| Step 28 synthetic prior (TIER-E7), Step 33 mechanistic/ML/hybrid | **not run** | both need a Step-27-PASS simulator | H8-05, H8-06 (D-089) |
| G15 simulator gates | 13 gates scored, **0 PASS** | same data gap | `G15_T5_scorecard_2026-11-11.md` |

**Verdict:** kinetics was *not rejected as an idea*; it was **gated out by its own pre-registered validation rules**
because validation-grade data do not exist in the sources we can lawfully hold. `sim_aa_1` stays
NOT_VALIDATED / RESEARCH_ONLY. This is the correct outcome under the plan's laws ("no invented scientific values").

**prv criticism (for the report):** a large share of engineering went into kinetic machinery (schemas, PARAM/FORM
lineage, SIMULATE gates, firewalls) that produced no validated number. The report must say this plainly as a
negative/limitation, not imply a working simulator. The one cheap action never taken: a human browser download of
AAK-02/04/05/08/10, which could raise SIM-VAL rows (may still stay 0).

## 3. Whole plan — built vs cut

### Built (with honest status)
| Deliverable / claim | What exists | Result status |
|---|---|---|
| D1 state/evidence dataset | ledgers EVD 17,978 rows (USDA/Bognar/Phenol-Explorer), full-corpus census 612,782 recipes / 14.6 M events, 15a seal | built; AI_PRECHECKED |
| D3 state graph engine | Rung A parser, replay engine, rule compiler; gold 7 (P1-A) + 40 dev | built; D-097 typed P 0.52–0.62, not independent |
| NER deployment | frozen DeBERTa+CRF on 4.17 M lines | built; agreement with lexicon 94.6–98.4 % |
| Router / decision layer (DIRECT/SIMULATE/…/ABSTAIN) | router 0.4.1, strict-v3 demo | built; demo 1,000-call audit 0 violations |
| D5 benchmark + ladder B0–B7 | 74 frozen questions | **H1 RULE_NOT_MET** (B4 = B1 = B2 = 0.25, n = 24); **H3 RULE_NOT_MET** (P3 abstention fails) |
| 29-diag learning diagnostic (D2-shaped) | rungs D0–D7 × 5 splits × 3 sources | DIAGNOSTIC only; USDA rungs beat D0, Phenol-Explorer mostly worse |
| Kinetics (AA) | Model A fit | NOT_VALIDATED; 0 SIM-VAL eligible |

### Cut (H8 register, D-089) or not delivered at scale
| ID | Planned | Status |
|---|---|---|
| H8-01 | D2 learned process-transition model | DIAGNOSTIC only |
| H8-02 | full proposal H2 (process vs food identity, unseen pairs/studies) | DECLARED_NOT_RUN |
| H8-03 | proposal H4 (feasibility + mistake recovery; SSOT H3+H4) | DECLARED_NOT_RUN |
| H8-04 | Step 20 procedural semantic corpus (Silver 1k–60k) | DECLARED_NOT_RUN |
| H8-05 | Step 28 synthetic prior | DECLARED_NOT_RUN (needs Step 27 PASS) |
| H8-06 | Step 33 mechanistic/ML/hybrid comparison | DECLARED_NOT_RUN (same) |
| H8-07 | Step 34 multi-step composition / trust horizon | DECLARED_NOT_RUN |
| H8-08 | FlavorTwin (Project B substitution) | DECLARED_NOT_RUN |
| H8-09 | D3 gold of 40 recipes (independent) | NOT_DELIVERED_AT_THIS_SCALE (40 dev, AI-assisted) |
| H8-10 | 8-scenario demo | NOT_DELIVERED_AT_THIS_SCALE |
| H8-11 | SSOT Levels 10–11 (vector/matrix, molecular structure) | DECLARED_NOT_RUN |
| — | SSOT H5 selective routing quality vs calls | relevance-gate P/R NOT_RUN |
| — | 07.A human condition audit | v4 human FAIL on record; R1 NOT_RUN (D-085: personas not inter-rater) |

## 4. prv summary verdicts (for Kush/Parv ok / not ok)

| # | Verdict |
|---|---|
| PRV-A1 | State-transition work is on-plan (SSOT §4, §5.2, §112); no scope drift. |
| PRV-A2 | Kinetics was gated out by pre-registered validation rules for lack of data, not abandoned; report it as a negative result with the numbers above. |
| PRV-A3 | The central hypothesis H1 was tested but under-powered (n = 24, AI gold); the report must not read RULE_NOT_MET as "state does not help". |
| PRV-A4 | Biggest honest gap vs proposal: H2 full, H4, H5 not run; say so on one slide (H8 register). |
| PRV-A5 | Cheapest remaining improvement to the kinetics story: human browser download of the 5 AAK papers before 21 Nov. |
