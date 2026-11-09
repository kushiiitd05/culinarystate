# CulinaryState progress audit vs the SSOT and the 36-step plan (S170, 2026-11-07)

AI audit (coding agent) for Kush and Parv to check. Sources: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`
(§0, §6, §12–14, §39 via `docs/SSOT_INDEX.md`), `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`,
`reports/review/project_completion_roadmap.md`, STATUS.md, DECISIONS.md through D-076, WORKLOG through S170, the
committed reports, manjot-server `~/kush_work/culinarystate` (read S171, see below).

**Scoring rubric (agent's judgment, fixed before scoring):** 1.0 done and accepted · 0.6–0.8 built and run on real
data, gate not passed or addenda pending · 0.3–0.5 built, tested on synthetic data or a partial real run · 0.1–0.2
draft schema, scaffold or old prototype · 0 not started. A failed gate is recorded, never scored as done.

## Lens 1 — 36-step plan: **≈ 35 %** (12.45 / 36)

| Steps | Score | Basis |
|---|---|---|
| 01 authority, 05 EVD | 1.0 each | done (ES-1.1 PASS) |
| 03 state semantics, 04 contracts | 0.9 each | done; v1.1 addenda pending |
| 02 audit, 06 source manifest | 0.8 each | done/automated; H2 items open |
| 07 condition normalisation | 0.7 | frozen; **07.A gate FAILED** (redo in M2) |
| 08 lineage | 0.5 | 08a run, **G08-3 FAILED**; 08b-v0 only |
| 09 extraction machinery | 0.2 | prototypes |
| 10 mechanism pilot, 11 verified kinetics | 0 | **not started: 0 PARAM rows** (M3) |
| 12 structured DB, 13 literature corpus | 0.3 each | partial staging / seeds |
| 14 coverage growth | 0.2 | partial |
| 15 data freeze | 0.3 | 15.0 ruled, **15a.R sealed**; 15a/15b not frozen |
| 16 instruction schema | 0.5 | draft pack; 16c freeze waits for P1b/H4 |
| 17 extraction (Rung A) | 0.6 | full corpus, invented 0; no gold comparison |
| 18 event engine / replay | 0.6 | 14.6 M events replayed; G18 not evaluated |
| 19 gold pilot | 0.5 | P1 scored: HANDBOOK_REVISION_REQUIRED; P1b waits on nonce |
| 20 scale procedural corpus | 0 | not started |
| 21 mechanism ontology, 22 effect signatures | 0.2 each | drafts; 14 expert questions open |
| 23 applicability router | 0.35 | engine synthetic-tested; **real-recipe demo mode added S170** |
| 24 formula registry | 0.2 | schemas + fitting library, no data |
| 25 parameter compatibility | 0.1 | inside 24, no data |
| 26 simulator | 0.3 | sim_aa_1/sim_chl_1 code, no parameters; census: SIMULATE 0 |
| 27 validation, 28 synthetic prior | 0 | blocked by 26 |
| 29 bootstrap, 30 bake-off | 0.2 each | scaffolds; 29-diag 2 blockers left |
| 31 physics features, 33 hybrid, 34 rollout | 0 | blocked / not started |
| 32 focused kinetics | 0.1 | library only |
| 35 representation ladder | 0.3 | synthetic-tested; signature pending |
| 36 evidence compiler → selective RAG | 0.2 | old partial prototype; silver ladder |

## Lens 2 — proposal deliverables (what the course grades): **≈ 25 %; hypotheses 0 of 4 tested**

| Item | Score | Basis |
|---|---|---|
| D1 evidence ledger | 0.5 | ≥1,000 public rows met; 0 of 40 hand-verified literature rows |
| D2 completion benchmark | 0 | not run |
| D3 state-tracking engine | 0.6 | built and run; no gold comparison |
| D4 retrieval with abstention | 0.1 | router demo started S170 |
| D5 end-to-end RAG + B0–B5 | 0.1 | 20-question silver ladder only (DEL-5) |
| H1–H4 | 0 | untested |

## Lens 3 — SSOT §14 Minimum Publishable Unit (Project A): **≈ 20 %** (1.6 / 8)

| MPU item | Score | Basis |
|---|---|---|
| 1 structured state schema | 0.7 | Step 16 draft + engine |
| 2 evidence-backed process-effect dataset | 0.4 | 17,978 E3 rows, unverified; 0 literature kinetics |
| 3 state-aware retrieval/reasoning pipeline | 0.3 | engine + router demo; not end to end |
| 4 3–5 benchmark task types (§12) | 0 | none built |
| 5 baseline/ablation ladder | 0.2 | silver B0–B5T on 20 questions |
| 6 quantitative evaluation | 0 | none valid |
| 7 human / food-science evaluation | 0 | none |
| 8 working demo | 0 | none (M6) |

**Out of course scope (0 %, not planned before 25 Nov):** Project B FlavorTwin (SSOT §15–19), multimodal encoders,
fine-tuning, audio/video (§21–36), SaaS/game (§46–47), Step 20 scale corpus, Steps 28 and 31–34.

## What the finish plan changes if M1–M6 land (estimate, not a result)

36-step plan ≈ 43 % (07.A redo, Step 10, 23–27 for ascorbic acid, 36 for D4/D5); proposal deliverables ≈ 60 %
with H1 and H3 tested; SSOT MPU ≈ 65 % (items 3, 4, 5, 6, 8 move; 7 only if Kush and Parv's reviews count as the
human evaluation). Remaining after 25 Nov: H2, H4, D2, Steps 20 and 28–34, FlavorTwin, multimodal.

## SSOT design points the finish plan must honour

- §6 architecture: parser → state tracker S_t → **process relevance gate** → process-effect module T(S_t, P, θ) →
  hybrid retrieval → constraint checker → action reasoner → S_{t+1}. M1 is the relevance-gate/router layer; M3 fills
  T for ascorbic acid; M4 is hybrid retrieval + abstention; M6 shows the whole loop.
- §39 query router: intent → SQL/API (exact metadata) | graph | vectors | **process model + evidence** |
  multimodal. M4 must route by intent, not vector-search everything.
- §12 task types to cover in the M5 benchmark (3–5 of 9): current-state tracking, next action, process
  substitution, process comparison, chemistry relevance.
- §0 scope rule: no universal "best process"; quality is relative to intent, state, target and constraints.

## manjot-server review (S171, 2026-11-08, read-only)

`~/kush_work/culinarystate` is a 26 Oct snapshot (= local commit `f963895`); a size-only dry-run rsync found **0 files
absent locally** in gpu/, features/, data/interim/, reports/, registry/, tools/. Its pipelines are the October NER and
linker GPU benches (`gpu/ner_bench`, `gpu/ner_tasteset`, `gpu/ner_recipedb3`), already local. Nothing to pull, so no
score changes. Reusable for M4: the 18 Oct retrieval stack in `data/interim/retrieval/` (EVD texts, BM25 top-100,
bge-reranker base/large) and `data/interim/embeddings/` (bge-small/base/large, e5-small/large, gte-large). Other
folders on that host are unrelated projects. GPU 1 was free at review time; GPU 0 was 38/40 GB in use.
