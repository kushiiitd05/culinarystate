# CulinaryState: final course report (AI DRAFT S168)

**Course:** Computational Gastronomy (CGAS), IIIT Delhi. **Group 17:** Kush Tokas, Parv Goyal. **Presentation:** 25-26 Nov 2026 (date as recorded in the handoff; confirm).

> **DRAFT STATUS.** Written by an AI agent for the two authors to edit. Nothing here is a human gate result, a signature, or a scientific validation. Every number is cited to a committed file as it stands; numbers that could not be checked against a file are marked UNVERIFIED. "AI reviewers" below means the AI personas ksh and prv, which check AI drafts and are not the humans. Quantity figures from Steps 16, 17 and 26 carry the **SP-002 caveat** (section 8.1). Statements about the human workflow follow D-045 (AI verdict first, then Kush and Parv review). Parv's agreement is mostly recorded as "relayed by Kush" in DECISIONS.md.

---

## 1. Abstract

CulinaryState builds infrastructure for a state-aware, evidence-bounded cooking assistant: a 612,782-recipe base, provenance ledgers, quantity grounding, rule-based step extraction, a deterministic event-replay engine, a pilot gold set and a simulator-input contract. Counts-only runs cover the full corpus. The scientific layer is not done. G08-3 FAIL, 07.A FAIL and the P1 handbook gate HANDBOOK_REVISION_REQUIRED are on record. Pilot labels are human-accepted AI drafts from one model family on one machine, so they give an engineering score, not inter-annotator agreement. No simulator run exists (0 of 14,594,812 engine events routed to SIMULATE, by construction), and no comparison against baselines has been run. About 29.8 % of ingredient lines carry a character the shared quantity parser misreads. D1's 40 hand-verified literature rows are 0, D2/D4/D5 and H1-H4 are untested, licences rest on an owner assertion, and 07I-C 0.88 is single-reviewer and not computed. No state-of-the-art or reliability claim is made.

---

## 2. Problem and aims

Source: `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf`, pp. 1-5.

Cooking assistants built on an LLM or plain RAG treat a recipe as text: they do not track the food's current state, do not know what a process does under given conditions, ignore the cook's constraints, and answer confidently without evidence. Evidence on process effects is sparse, heterogeneous and confounded, so the proposal treats sparsity as a first-class property: model what has and has not been measured, never invent chemistry, and let the system abstain.

**Central question.** Can explicit food-state tracking plus evidence-bounded process-effect reasoning improve context-aware guidance over text-only and dense RAG, and can the system know when it does not know?

**Hypotheses.** H1 state-aware retrieval beats text-only and dense RAG on current-state and next-action questions. H2 process information beats food-identity-only models on unseen pairs and studies. H3 evidence-class routing with calibrated abstention lowers the unsupported-claim rate. H4 feasibility filtering and recovery reasoning respect constraints better than a generic chatbot.

**Deliverables.** D1 evidence ledger (at least 1,000 public rows plus at least 40 hand-verified literature rows); D2 sparsity-aware completion benchmark; D3 event-sourced state-tracking engine; D4 evidence-aware retrieval with abstention; D5 end-to-end RAG with about 80 questions and baselines B0-B5.

**Proposed vs achieved** (proposal pp. 1-5 checked against the records; a cell that cannot be verified is marked UNVERIFIED):

| Item | Proposed | Status |
|---|---|---|
| D1 | at least 1,000 public rows + at least 40 hand-verified literature rows | **Partial.** Public rows met (DEL-1); 0 of 40 hand-verified literature rows. |
| D2 | sparsity-aware completion benchmark | **Not run.** |
| D3 | event-sourced state-tracking engine, evaluated on 40 gold recipes and 30 scripted sessions | **Engine built, rule-based.** No gold comparison; G18 not evaluated. |
| D4 | evidence-aware retrieval with abstention | **Not started.** |
| D5 | end-to-end RAG, about 80 questions, B0-B5, demo | **Not run; no demo.** |
| H1-H4 | four hypotheses | **Untested.** |

Against the proposal, we delivered a partial D1 and the engine layer of D3 plus supporting infrastructure; D2, D4, D5 and all four hypotheses remain unaddressed. Time went to upstream hardening, not to the retrieval and abstention work the proposal centred on.

**Honest scope.** Work since 18 Oct 2026 was mostly D1 and D3 hardening plus the upstream layers (a 36-step spine, D-027). H1-H4 have **not** been tested; D2, D4 and D5 are not reported as results (6.8).

---

## 3. System overview

Pipeline in dependency order (step numbers follow the 36-step spine, D-027): (1) evidence ledgers EVD/COND/SRC/MEAS/SNAP/STUDY and lineage (Steps 05-08); (2) recipe base, 612,782 recipes (07H-R freeze); (3) quantity grounding (Step 16): quantity AST, units, exact mass Q0, invented-value audit; (4) Rung A extraction (Step 17): deterministic rules from step text to events, validators V1-V4; (5) event engine and replay (Step 18); (6) pilot gold (Step 19, wave P1); (7) simulator contract and census (Step 26g); (8) representation and evaluation scaffolds (Steps 15, 29-35), which refuse to run until human values and signatures exist.

Stages are connected by interfaces, not approvals: a later stage can run on counts while an earlier gate is unmet, and every such run is labelled counts-only and not a human gate.

---

## 4. Data

### 4.1 Recipes
612,782 recipes in five source families (STATUS.md; `reports/step16/S161_real_data_runs.md` s3.1; the family counts sum to 612,782): A1/BBC Good Food 11,934; Food.com 522,517; Gutenberg segments 73,955; TASTEset 700; Wikibooks 3,676. D-026 marks all as `USABLE_FOR_PROJECT_USE`. This is an **owner assertion**: licences were not independently verified, and raw redistribution is not asserted (BBC and Food.com raw = NO). A TASTEset licence inconsistency and CoSyLab/Phenol-Explorer permissions are untouched.

Two structural facts matter for later numbers: Gutenberg segments have 0 ingredient lines by design (historical prose), and TASTEset has 0 step texts (`rung_a_dryrun_counts_full_corpus_final.json`, per-family blocks).

### 4.2 Evidence ledgers
- Current EVD basis: 17,978 rows (STATUS.md; D-027). The EVD file is append-only (57,280 lines, 18,156 ids); the latest line per id gives 17,978 ACTIVE rows: USDA-RETN-R6 7,018 + BOGNAR-2002 7,090 + Phenol-Explorer 3,870. The DEL-1 data card (`reports/DEL1_data_card.md`, 2026-10-18) predates the Bognar ingest (S038) and reported USDA + Phenol-Explorer = 10,888 (all tier E3, 2,620 censored). The two figures are consistent.
- DEL-1 acceptance as committed: public rows at least 1,000 **met** (10,888); hand-verified literature rows at least 40 **not met (0)**; ID normalisation to internal ING 53.2 %; normalisation to RecipeDB/FlavorDB UNRESOLVED_EXTERNAL (API pending).
- Matrix-by-process density 0.0372 (DEL-1), which is the sparsity the proposal builds on.

### 4.3 Protections
EVD/COND/SRC/MEAS/SNAP stay byte-identical (checked against baseline hashes: `verify_baseline` 7/7, before and after every run reported here); STUDY and `_ids` are append-only. Recipe text and per-item worksheets are git-ignored; committed reports are counts, hashes and codes only (`contains_text` and `contains_ids` false in the run JSONs). Pilot packets use salted commitments so that tracked files do not reveal draw order (D-054).

---

## 5. Methods per stage

**Evidence and lineage (05-08).** 07H-R freeze of the condition normaliser and recipe base. 08a lineage resolution for the existing EVD rows with pre-registered thresholds THR-08A-01..23 (D-030); 08b-v0 reusable lineage library (D-035). 07.A human condition audit (100 conditions, two reviewers); 07I-C identity calibration.

**Step 16 (rc2).** Conservative parse to a typed quantity AST (`quantity/parse_adapter.py`) via the shared legacy `grammar.parse_line`; unit resolution; exact mass Q0 only when supported; invented-value audit. A versioned zero-preserving normaliser fixes a legacy zero-multiplier defect. rc2 never turns a legacy UNKNOWN into a value.

**Step 17 (Rung A).** Lexicon-and-rules baseline for mentions, actions, linking, references, step quantities and events; validators V1-V4; an auditor that checks every emitted value and unit against its source span.

**Step 18.** Append-only event log, deterministic transactional replay with snapshot hashes; the older L1-L8 engine is untouched.

**Step 19.** Six-stage synthetic rehearsal, handbook v1 plus Addendum A, then wave P1: 21 rows in 7 strata drawn by a SHA-256 rank rule bound to a joint nonce (D-048); 14 packets (annotators A and B, 7 each), labelled model-assisted (section 7).

**Step 26g.** Simulation-input contract with null `sim_run_id` links; a counts-only census of whether the eight inputs of the selected system are present per engine event. D-052 selected `sim_aa_1` (ascorbic acid) **before** the Step 10/11 census; no selection criterion was claimed as met.

**Scaffolds (15, 29-35).** 15a.R seal, group-disjoint splits and leakage checks, 29-diag, Step 30 bake-off with no default margin, Step 35 representation ladder (35c/d/e synthetic-tested). All refuse to run without signed records or human-supplied values. The earlier DEL-2..5 experiments (silver, development-only) are summarised in 6.8.

---

## 6. Results per stage

All counts are as committed. All are engineering counts, not gate results, unless a gate is named.

### 6.1 Gate outcomes (stated as recorded)

| Gate / record | Outcome | Source |
|---|---|---|
| 07.A (condition audit, 100 conditions) | **FAIL** on the registered statistic: pooled kappa 0.0 on original labels (kappa paradox: one reviewer's codes had no variation), raw agreement 0.9944, 5 of 100 conditions disputed and adjudicated in Kush's favour. Threshold: kappa at least 0.80. Hard gates for Steps 15, 23, 26d/27, 29-33 stay closed. | `reports/step07/step07_v4_adjudication_result.md`; `step07_v4_agreement_result_run2.json` |
| 07I-C identity | Original blind kappas 0.571 / 0.588 retained. D-033's 0.88 is **Kush-stated on an adjudicated single-reviewer basis, not computed**. Parv's own written confirmation pending. | D-033; STATUS.md |
| G08-3 (08a edge audit) | **FAIL.** B3 correct 13/50 (Kush) and 0/50 (Parv); B2 49/50 (Kush) and 0/50 (Parv, 49 UNCERTAIN); STRONG 50/50 both. B3 cut kept at 0.75. B2/B3 edges stay PROVISIONAL; no claim that needs G08-3 may be made. | D-034 |
| P1 handbook gate (THR-19P-16/31) | **HANDBOOK_REVISION_REQUIRED.** Flagged: coref, entity_type, event_argument, event_type, final_state (threshold 0.2). | `reports/step19/p1_agreement_counts_S166.json` |
| THR-19P reading (prv, M3) | Most rows **NOT_EVALUABLE** under W2 and D-064: THR-11/12 provenance, 13-15 timing, 18 alpha, 19 falsification, 20/34 CIs, 21/22 class statistics. THR-23 PASS. THR-25 FAIL; the D-070 stamp records triage only. SP-001 and SP-004 remain open and SP-004 carries a BLOCKING risk. STOP-SCHEMA not triggered. THR-35 descriptive only. | `handoff/REVIEW_SHEET_AI_VERDICTS.md` M3; D-070 |
| G16 / G17 / G18 | Not evaluated. | STATUS.md |
| Step 35 | No signed record; runner refuses. No real evaluation. | STATUS.md |
| Step 15 seal, 29-diag, Step 30 | Refuse (RESERVED fraction, seed, margins unset). | S161 report s6 |

### 6.2 Step 16 quantity grounding (SP-002 caveat applies)
Source: `reports/step16/S161_real_data_runs.md` s3.1.
- Recipes 612,782; ingredient lines 4,281,956; contract-valid 4,281,954; exceptions 0. The 2 invalid lines are Wikibooks `INVERTED_INTERVAL`.
- Invented grams: 0 (reported through the issue codes). `invented_count 0` means no value or unit lies outside its source span (a span check); it does not mean the extraction is correct.
- rc2 mass Q0: 33,373 lines (**0.78 %**). Q6 (no gram value): 4,248,583.
- Mass routes: `NO_INGREDIENT_LINK` 4,018,242 (no POR records or ingredient links were supplied to this dry run), `NO_QUANTITY` 201,078, **`UNSUPPORTED_EXPRESSION` 21,172**, `AST_EXACT_PHYSICAL` 27,626, and five smaller routes (`AST_PACKAGE_SOURCE_STATED` 4,567; `QUALITATIVE` 5,913; others under 2,200).
- Legacy vs rc2: legacy MEASURED to rc2 UNKNOWN 6,047; QUALITATIVE to UNKNOWN 6,519. Lines flagged 270,737.

The low 0.78 % is mostly a missing-input effect (no ingredient links), not a parser verdict. It is also depressed by SP-002.

### 6.3 Step 17 Rung A, full corpus (SP-002 caveat applies to quantity items)
Source: `reports/step17/rung_a_dryrun_counts_full_corpus_final.json`; `S161_real_data_runs.md` s3.2b. Run on vinayak-server, CPU only, final auditor version.
- Recipes 612,782; with steps 611,902; without 880; exceptions 0; baseline PASS before and after.
- Events 9,470,190. Entities: ingredient lots 5,124,622; intermediates 7,428,106; mixtures 1,782,741; reserved portions 83,901. Ambiguity count 801,279.
- Values checked 89,316,045; **invented_count 0** after two test-first auditor fixes. `invented_count 0` means no value or unit lies outside its source span (a span check); it does not mean the extraction is correct.
- Validators: V1 0 texts failed. **V2 3,848 texts failed, `INVERTED_INTERVAL` 4,511.** V3 0 failed (categorical fields without a vocabulary are listed as not checked). V4 0 failed, with its five scope items "not checked" by design and `FRACTION_BASIS_UNSPECIFIED` 91,606.
- Stage failures: quantity grounding `UNRESOLVED` 397,989, `PARSE_FAIL` 10,028; linking `NO_VALID_CANDIDATE` 569,839, `UNRESOLVED` 80,096; references `UNRESOLVED` 108,716, `NO_VALID_CANDIDATE` 41,316.
- Step-quantity grounding: `MASS_GROUNDED` 44,461; `UNSUPPORTED_EXPRESSION` 10,028.

**Auditor history.** 1,000-recipe sample: invented_count 23 (all `UNIT_NOT_IN_SPAN`, U+00BA degree-sign false positives), fixed test-first to 0. Full corpus: 626 (226 texts), then 4, then 0 after two further test-first fixes (degree prefix before C/F; lowercase c/f). These were auditor false positives, not invented values. Only 8 of the 626 rest on shape masks and boolean checks; **the other 618 rest on the before/after difference** (S163 review), and the scratch scripts are not committed. The three JSONs do not record the auditor commit.

**V2 inverted intervals (J4).** `reports/step17/j4_inverted_interval_counts_S166.json`: 4,511 cases in 3,848 texts (Food.com 2,786; Gutenberg 1,721 cases; A1/BBC 2; Wikibooks 2), matching the full-corpus V2 counts. The dominant shape is `9-9/9 a` (4,276 of 4,511), which looks like a mixed number or range being misread, but this is an interpretation: 69 excerpts were sampled for Kush and Parv to read (D-059), and there are no reader verdicts recorded yet (all 69 rows blank).

### 6.4 Step 18 event engine and replay
Counts only here; the old engine is unchanged and G18 is not evaluated. In the P1 pilot, all 14 labelled packets validate with 0 replay issues and all 7 pairs have `replay_ok` true (`p1_agreement_counts_S166.json`; WORKLOG S167).

### 6.5 Step 19 pilot P1 (7 pairs; human-accepted AI drafts, not blind)
**Required wording (prv, review block M6, accepted in D-067):** "P1 was scored on seven recipe pairs whose labels are human-accepted AI drafts from the same model family, produced on one machine; the result is an engineering score, not blind inter-annotator agreement, and provides no timing or reliability evidence. Agreement is low on state fields (0.26) and strict events (0.56), with disagreements concentrated in coreference and entity type, and four open schema or tooling problems (SP-001..004) point to handbook and tool revisions before P2. No state-of-the-art or reliability claim is made."

Mean over the 7 pairs (`p1_agreement_counts_S166.json`):

| Measure | Mean |
|---|---|
| spans exact F1 / relaxed F1 | 0.8427 / 0.8797 |
| concept agreement | 0.9037 |
| coref B-cubed F1 | 0.8363 |
| process-link F1 | 0.7979 |
| relation F1 / structural relation F1 | 0.6648 / 0.7492 |
| event F1 strict / loose | 0.5592 / 0.5994 |
| alive-entity F1 / intermediate-entity F1 | 0.619 / 0.8178 |
| state-field agreement | 0.2643 |
| unknown-disagreement rate | 0.0476 |

Denominators: spans 881, coref 226, events 194, state 71, lines 57. Disagreements: coref 108, entity_type 104, event_type 74, quantity 35, final_state 29, event_argument 22, boundary 14, canonical_identity 6.

Handbook gate (threshold 0.2), tool rate / per-pair rate: coref 0.4779 / 0.9558; final_state 0.4085 / 0.8169; event_type 0.3814 / 0.7629; entity_type 0.118 / 0.2361; event_argument 0.1134 / 0.2268; quantity 0.0397 / 0.0795. Verdict **HANDBOOK_REVISION_REQUIRED**. The U+2044 sensitivity block gives identical numbers.

**Reading limits.** Both label sets come from the same model family; A and B were built on the same Mac after Parv's laptop failed (D-064, a recorded deviation from the one-annotator-per-machine rule); "snapshot times" are not annotation timing. Per-pair rates are category-level and cannot be attributed to single causes. 

**Schema and tooling problems** (`pilot_schema_problem_log.md`, stamped D-070): SP-001 an ingredient named only in the steps cannot become an entity (SCHEMA_GAP, routed to 16A). SP-002 U+2044 fractions parse as a count of 1 (TOOLING, parser fix after the presentation). SP-003 unstated shares (HANDBOOK_GAP, Addendum B). SP-004 alternative or conditional values only free text (SCHEMA_GAP, routed to 16B, with a BLOCKING risk). Addendum B (8 issued rules, 10 held) is in force from P1b/P2; P1 labels are never edited or re-scored under it. P2 is not authorised; P1b was approved in principle with its size and draw still human-supplied.

### 6.6 Step 26g simulability census (SP-002 caveat applies to quantity inputs)
Source: `reports/step26/simulability_census_full_corpus_S169.json` (census 0.2.0; S166 file kept for the record); `CENSUS_FILES.md`.
- 612,782 recipes; 611,902 texts with steps; **14,594,812 engine events**; 14,507,823 transactions applied and 86,989 rejected in replay.
- **SIMULATE: 0. SIM_PROHIBITED: 14,594,812.** All 8 inputs (`duration`, `lid_state`, `matrix_class`, `medium`, `piece_size_class`, `start_mode`, `temperature_profile`, `water_ratio`) are UNKNOWN for every event; applicability UNKNOWN 14,594,812.
- Other reasons: `LOT_INTRODUCTION` 5,124,622 (35.1 %); `NO_CONSUMED_ENTITY` 1,027,834 (7.0 %); `REPLAY_HAS_ISSUES` 269,062; `EVENT_REJECTED_IN_REPLAY` 86,989. Exceptions 0; invented 0; baseline PASS before and after.
- The census 0.1.0 reason NO_CONSUMED_ENTITY (6,152,456 of 14,594,812 events, 42 %) mostly counted the synthetic lot-introduction events, which consume nothing by design (an AI engine diagnosis, S168, D-071). With census 0.2.0 these carry LOT_INTRODUCTION: on the seeded 1,000-recipe sample, 35.1 % of events are lot introductions and **7.1 % are real actions with no consumed entity** (verbs without a stated object, e.g. "stir", "bake until done"; `reports/step26/simulability_census_real_sample_counts_S168.json`). The full-corpus 0.2.0 run confirms it: 35.1 % lot introductions and **7.0 % real actions with no consumed entity**, the exact split of the 0.1.0 count, every other reason unchanged. Even with bindings, those 7 % could not be simulated until Rung A binds an implicit object. Of the two candidate rules, one was withdrawn and the other failed its pre-registered precision check (4 of 60 correct; D-074), so those events stay UNKNOWN.
- Engine events = 9,470,190 Rung A events + 5,124,622 synthetic lot-introduction events (one INTRODUCE_LOT per ingredient lot; `src/culinarystate/state_graph/event_adapter.py`).
- **All-prohibited is by construction** (no condition or applicability bindings exist yet). It is not a finding about the corpus, and it is not a simulator result. The simulators exist as data-free code with no parameter values; no simulator has been validated on real held-out data.
- `git_commit` is null (no `.git` on the server copy); module and tree hashes pin the code.

### 6.7 Evidence 09/12/13a-0 and tests
`S161_real_data_runs.md` s3.3-3.5: 12.0 proposed 3 SRC and 7 SNAP rows (staging only, no ledger append; D-049 re-baseline pending). 12-local staged 173 USDA R2 rows and 1,693 Bognar cells (T36: 0 cells; the report's own `estimated_cells` is 528, an unresolved discrepancy). 13a-0: 715 seeds (703 with a DOI), metadata only. Full unit suite on the Mac with data (S161): 3,215 passed, 2 skipped, 1 deselected, 0 failed (as of S161, 2026-11-04); current head UNVERIFIED. S168 Mac subset (Step 16-19/26 subset, 2026-11-06): 583 passed, 1 skipped.

### 6.8 What has NOT been measured
No result exists for H1-H4. D2 (completion benchmark) and D5 (end-to-end RAG vs B0-B5) are not run; D4 is not started. The proposed-vs-achieved table is in section 2: a partial D1 and the engine layer of D3 were delivered; D2, D4, D5 and H1-H4 remain unaddressed. The earlier DEL-3/4/5 numbers are silver or AI-authored development diagnostics, not evaluations: DEL-3 compares the compiler with a non-blind AI-assisted Gold-v1 (state-field accuracy 0.102 [0.04, 0.16], n = 20); DEL-4 (silver, templated queries) found a general cross-encoder worse than the baseline list (-0.056 and -0.091 MRR@10, CIs excluding 0); DEL-5 is an 8-question smoke test (not a benchmark), then a 20-question AI-authored silver ladder (`reports/del5/ladder_smoke_v1.md`, `ladder_v2_qwen32b.md`). None supports a claim over a baseline on a held-out human benchmark.

---

## 7. Human-in-the-loop workflow and governance

**D-045 (2026-11-03).** Every gate, choice and label first gets an AI verdict, labelled as AI; Kush and Parv then review, and their review is final. "ksh" and "prv" are AI personas, not the humans. W2: annotations are AI first-pass labels reviewed by both humans (`MODEL_ASSISTED`), reported as "human review of AI drafts", not blind independent annotation. W3: the professor's permission is as stated by Kush; **no written copy is in the repository (UNVERIFIED)**.

**Decisions log and review blocks.** All DECISIONS.md entries were typed by the coding agent as scribe from the humans' statements; the humans decided. DECISIONS.md D-001..D-070 give the decider, the source quote and what is not covered. Review blocks A-O in `handoff/REVIEW_SHEET_AI_VERDICTS.md` list each AI verdict and the human decision needed. Parv's agreement is mostly "relayed by Kush" and is labelled so. Values only a human can supply (nonce, capacity, budget, seeds, signatures, licences) are never produced by a verdict; an "ok" does not stand in for them (D-047, D-053).

**Provenance and commitments.** Start record signed (D-048, joint nonce not reproduced here); THR-19P-01..35 signed (D-046). Packet rows and key hashes are salted commitments; an earlier unsalted design leaked packet order and was replaced (D-054). Label files are bound by `commitments_{A,B}_P1.json` (0 recipe ids). A's and B's packet salts were both agent-generated at Kush's instruction (D-057, D-064); B's private material shares one Mac with A's.

**Leak safety.** Recipe text is git-ignored; committed outputs are counts-only; a leak test mounts a public-data attack. Recipe text, ids, salts and keys are absent from this report.

**Honest records.** Failed gates are not erased or loosened (R-20); 07.A kappa is not recomputed after adjudication; G08-3 stays FAIL.

---

## 8. Failures, limitations and threats to validity

### 8.1 SP-002 (quantity parser misreads U+2044), the largest known defect
Source: `reports/step16/sp002_fix_design_ksh_S168.md` (AI verdict, Kush decided: D-070).
- 1,275,782 of 4,281,956 corpus ingredient lines (**29.8 %**; Food.com 1,275,153, A1 188, TASTEset 441) contain U+2044 FRACTION SLASH. Measured directly by the main session in S168 (counts-only corpus scan; D-069).
- The legacy parser reads "1/4 tsp" written with U+2044 as a count of 1 with no unit: a silent wrong value that the invented-value audit does not catch. The rc2 path calls the same parser, so **S161 Step 16 numbers, the 26g census quantity block, and any Rung A expression that already carries U+2044 are affected.**
- Unchanged by the fix and carrying the defect: `recipe_quantity_mentions_v1.parquet` (frozen), KGE `ING_MEASURED_IN_UNIT`, the FDC crosswalk, rule NER, line link, rule compiler, gold `_base_from_text` (P1 labels and replay). Annotator A's affected quantities are unreliable for scoring; B used ASCII overrides.
- **Fix scheduled after the presentation (D-070)** as a new versioned rc2 result next to S161. Expected direction (not measured): mass Q0 coverage rises modestly, unsupported and UNKNOWN counts grow. Magnitude needs a rerun.

### 8.2 Failed and open gates
G08-3 FAIL; 07.A FAIL; P1 handbook gate HANDBOOK_REVISION_REQUIRED; THR-19P many rows NOT_EVALUABLE; 07I-C 0.88 not computed and single-reviewer; Parv's own written 07.A/07I-C confirmation pending; the Parv "go with Kush's" adjudication relay was not seen as a message (UNVERIFIED, per the 07.A adjudication note). Hard gates that depend on a valid 07.A stay closed. D-039/D-040 are Parv's unsigned single-reviewer choices.

### 8.3 Measurement-validity threats
1. D-061 limit: Kush accepted 62 flagged judgement calls without line-by-line edits; the humans did not independently label, so P1 contains no human annotation. P1 labels are AI drafts from one model family, accepted by humans with `human_edits=NONE` for the committed sets; A and B are not independent. This inflates agreement on shared systematic errors and makes the numbers non-comparable to blind IAA.
2. No timing, alpha or confidence intervals (NOT_EVALUABLE); only 7 pairs, small denominators (lines 57, state 71).
3. A and B private material lived on one Mac (D-064); per-pair rates are category-level and cannot be attributed to single rules.

### 8.4 Engineering and data limits
- Rung A is a rule baseline with large unresolved mass (linking `NO_VALID_CANDIDATE` 569,839; references `UNRESOLVED` 108,716). No gold comparison of Rung A exists for the full corpus.
- The auditor is a span checker: zero invented values means no value or unit outside the span, not correct extraction.
- V3 and V4 mostly list "not checked" scopes; zero failures is not a pass of those scopes.
- Bognar `estimated_cells` (528) disagrees with 1,693 staged cells; method mapping is positional-only for 1,268 cells.
- Full runs need vinayak-server (CPU only, about 3.5-4 h each); the 8 GB Mac swaps. Server copies have no `.git`. The `test_transition` hang is only worked around with thread caps.
- Parv's exploratory Step 30 D0-D2 run is DIAGNOSTIC_ONLY and not citable (agent-chosen seed, margin 0.0, ran before the seal).
- The 15.0 draft's 1/5 RESERVED fraction is the agent's reading, not a value Parv stated. D-068 (the 15.0 ruling) is prepared but not yet appended by Kush, so the 15a.R seal has not run (status at drafting).
- Packet salts: A's and B's were both agent-generated at Kush's instruction (D-057, D-064); B's private material shares one Mac with A's.
- Licences: D-026 is an owner assertion; DS-014 UNKNOWN; H2 items open. MECH v1.1 sources UNVERIFIED (hosts blocked); 14 expert questions open. `sim_aa_1` was selected before the evidence census. Cuisine labels cover 12.9 % of recipes.

### 8.5 Scope limits
No recipe or cuisine headline claim without 07I-S. No health or sensory-equivalence claim. No simulator output. No end-to-end user study. No chef review. Nothing here shows the system is more reliable than any baseline.

---

## 9. What remains (critical path after 26 Nov)

1. **SP-002 parser fix** as a versioned rc2 adapter change, test-first, with a before/after diff; rerun Step 16 and the 26g quantity block as a new result beside S161 (D-070 O1).
2. **Handbook and schema:** adjudicate the true causes of coref (0.96 per-pair) and event_type (0.76); run P1b (3-4 new recipes, fresh draw and salts, human-supplied size and nonce); decide SP-001 (16A) and SP-004 (16B).
3. **Independent annotation:** pilot agreement and timing are not evidence until annotators label without AI pre-fill; this needs a design amendment and changes the 40 h arithmetic.
4. **Human readings pending:** J4 sample, 12.0 rows and the D-049 re-baseline, the 12-local G12 audit, unsupported-expression counts, Step 17b V2.
5. **Seal and Step 35:** RESERVED fraction, seed, the 15.0 ruling in Kush's own entry, P-1..P-5, S-1/S-2, thresholds (delta_30, rho, c_floor, 34c) and signatures; only then 15a.R, Step 35, 29-diag, Step 30.
6. **Evidence lane:** 07.A and G08-3 are not to be reinterpreted; 08b-v1 and evidence-quality gates need human work; D1's 40 hand-verified literature rows are 0 so far.
7. **Simulator:** condition and applicability bindings, 26.0 pre-registration numbers, real held-out validation (Step 27); only then a synthetic prior (Step 28).
8. **D2 and D5:** completion benchmark and the B0-B5 end-to-end comparison on a human-reviewed benchmark.
9. **Governance:** a written copy of the professor's permission (if one exists); Parv's own written statements.

---

## 10. Contributions (from DECISIONS.md and WORKLOG.md; authors to correct)

All DECISIONS.md entries were typed by the coding agent as scribe from the humans' statements; the humans decided.

**Kush Tokas (human):** decider on nearly every entry D-020..D-070; owner decisions on recipe usage (D-026) and plan governance (D-027); approved the H4 contracts (D-029); signed the 08a pre-registration and authorised 08a/08b-v0 (D-030..D-035); recorded the G08-3 FAIL and the cut (D-034); stated the 07I-C figure (D-033); selected `sim_aa_1` (D-052); stamped the ksh/prv AI drafts without edits (D-061; D-060..D-066); approved the SP-002 design and Addendum B stamp (D-070); supplied nonce string, capacity and budget (D-048); ran full-corpus jobs on vinayak-server.

**Parv Goyal (human):** reviewed or passed the AI verdicts for S154-S160 (D-046/D-047, D-049..D-053), mostly relayed by Kush; his B stamps (D-065, D-066) and block-M pass (D-067) were relayed by Kush; own Step 35 and cuisine review choices (D-039, D-040; single-reviewer, unsigned); rebuilt the P1 frame and drew P1 locally on 2026-11-04 under D-048 (STATUS.md, Step 19 row); reviewer in 07.A and G08-3. His own written 07.A/07I-C statement and Step 16 comments are pending.

**AI agents (not the humans):** the coding agent implemented Steps 16-19 and 26 tools, the runs and the scribe entries; "ksh" and "prv" personas produced the first-pass labels and cross-checks for annotators A and B (D-060..D-066), the SP triage, the SP-002 design and the Addendum B consolidation. The 2026-10-28 AI precheck is AI review, not expert verification. DEL-1..5 authorship is UNVERIFIED from the files read; the DEL-3 Gold-v1 draft came from an external model with Kush's review and Parv's delegated to Kush (D-016/D-017, as cited in that report). Parv's laptop failure moved B's build to Kush's Mac (D-064).

---

## Appendix: Slide outline (9 slides, about 10 minutes)

1. **Problem:** recipe-as-text assistants do not track state, ignore evidence limits, answer without support; central question and H1-H4.
2. **Proposed vs achieved:** the section 2 table. Partial D1 and the D3 engine layer delivered; D2, D4, D5 and H1-H4 unaddressed; time went to upstream hardening.
3. **Pipeline:** ledgers, 612,782-recipe base, quantity grounding, Rung A, event engine, pilot gold, simulator contract.
4. **Funnel:** 4.28 M ingredient lines to 33 k exact mass (0.78 %), with the 29.8 % U+2044 flag; 14.6 M events to 0 SIMULATE; 35 % are lot introductions (by design) and 7 % real actions with no consumed entity (census 0.2.0, 1,000 sample). `invented_count 0` is a span check, not correctness.
5. **Gates:** 07.A FAIL, G08-3 FAIL, P1 handbook gate HANDBOOK_REVISION_REQUIRED; 07I-C 0.88 single-reviewer, not computed.
6. **P1 panel:** 7 pairs; spans 0.84, strict events 0.56, state fields 0.26; stamped "human-accepted AI drafts, not IAA".
7. **Governance:** D-045, AI verdict first, decisions log typed by the coding agent as scribe, salted commitments, leak safety, what AI cannot supply.
8. **Limitations:** SP-002, owner-asserted licences, single machine, no human annotation, D1 literature rows 0.
9. **Remaining work:** SP-002 fix, P1b, independent annotation, seal and Step 35, simulator validation, D2/D4/D5.

**Key figures and tables to show:** (1) the proposed-vs-achieved table (section 2); (2) the funnel figure for slide 4 (6.2 and 6.6 counts); (3) the P1 agreement table (6.5).
