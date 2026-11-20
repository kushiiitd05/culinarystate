# Final component inventory — what is actually built

**`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · 17 Nov 2026.** A component is BUILT only if its file was found
on disk on 17 Nov (branch `kush/s181-explorer-build`). Labels: **BUILT / PARTIAL / PLANNED_ONLY / CUT /
DEFERRED**. "Gate" = scientific gate; **no scientific gate is PASS** unless stated. All paths under
`src/culinarystate/` are abbreviated `…/`.

Source keys: `[SI]` `reports/s179/state_inventory_FINAL_2026-11-15.md` · `[IR]` `docs/EVENT_IR_CONTRACT.md` ·
`[ST]` `STATUS.md` · `[BT]` `docs/BUILD_TRACKER.md` · `[NER]` `reports/ner/culinaryner_kf_final_report.md` ·
`[S7]` `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md` · `[D]` `DECISIONS.md` ·
`[CM]` `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md` · `[DEP]` `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md` ·
`[MP]` `handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md` · `[FILL]` `reports/s179/state_dataset_fill_full_2026-11-14.json` ·
`[SRC:x]` = read directly from source file x.

## Table A — identity

| # | Component | Label | Motivation | 36-step owner | D-owner | Model / rule / database | Artifact path |
|---|---|---|---|---|---|---|---|
| 1 | Recipe corpus | BUILT | text to compile into state | NOT_EVIDENCED | D3/D5 | 4 source families: A1_BBC_GOOD_FOOD, FOODCOM, GUTENBERG_SEGMENT, WIKIBOOKS `[FILL]` | `data/raw/` (git-ignored, third-party text) |
| 2 | NER (CulinaryNER-KF v1) | BUILT (not on the State v2 path; exact frozen checkpoint "missing" locally `[ST]`) | span extraction | NOT_EVIDENCED | D3 | DeBERTa-base + CRF `[NER]` | `…/ner/`, `reports/ner/culinaryner_kf_final_report.md` |
| 3 | Entity linking | BUILT | mention → ING id | NOT_EVIDENCED | D3 | BGE-large frozen linker; lexicon+alias `LineLinker` `[NER]`,`[BT C2]` | `…/evidence/linker.py`, `…/lotstate/linker.py` |
| 4 | Quantity grounding | PARTIAL; mass fractions **DEFERRED** `[SI §6]` | amounts/units | NOT_EVIDENCED | D3 | grammar + unit rules | `…/quantity/` (grammar.py, rc2_grounding.py, units.py) |
| 5 | Process recognition | BUILT | step → PROC id + family | NOT_EVIDENCED | D3 | Rung A rules + lexicon; PROC ledger ("PROC 156" `[BT RQ08]`) | `…/extraction/rung_a_rules.py`, `rung_a_lexicon.py`, `ledgers/data/PROC.jsonl` |
| 6 | Typed Event IR | BUILT | one contract for rule and LLM producers | Step 17a; 36A.3 `[IR]`,`[SI §2]` | D3 | frozen dataclasses | `…/extraction/interfaces.py`, `docs/EVENT_IR_CONTRACT.md` |
| 7 | Invariant validator V1–V4 | BUILT (module status `DRAFT_PENDING_16c` `[IR]`) | reject malformed graphs | Step 17a / 18 `[IR]` | D3 | deterministic checks | `…/extraction/validators.py`, `invariants.py`, `auditor.py` |
| 8 | Coreference / lineage vNext | BUILT — **DIAGNOSTIC** | "the sauce" continues the prior lot; alternatives; fat stays | "lineage vNext (D-132)" `[SI §2]` | D3 | rules, flag `lineage_vnext=True` `[SRC:rung_a.py]` | `…/extraction/rung_a.py`, `rung_a_binding.py` |
| 9 | Lot graph (`EventGraph`) | BUILT | lot identity, merge/split | B11 (SSOT) `[SI §3]` | D3 | the only event graph `[IR]` | `…/extraction/interfaces.py` |
| 10 | Event replay / state engine | BUILT (replay-from-history invariant **open** `[IR §5]`) | event-sourced state | C3 `[BT]` | D3 | rules | `…/state_graph/engine.py`, `rule_compiler.py` |
| 11 | State v2 `S_t=(G,C,Q,Y,P)` | BUILT | explicit per-(food, step) state | SSOT B12 `[SI §1]` | D3 | assembled from existing producers only `[SRC:state_full.py]` | `…/composition/state_full.py` |
| 12 | State delta ΔS | PARTIAL — only **vector** delta `delta()` found `[SRC:state_vector.py]`; a cell-level S_t→S_{t+1} diff function: NOT_EVIDENCED | show what a step changed | NOT_EVIDENCED | D3/D5 | arithmetic on masked vectors | `…/composition/state_vector.py` |
| 13 | State vector V0 / V1 | BUILT — `DIAGNOSTIC_RETRIEVAL_ONLY` | retrieval view of state | NOT_EVIDENCED | D4 | hand-specified, nothing learned; V0 51 dims `[SI]` | `…/composition/state_vector.py` |
| 14 | Evidence ledger (EVD) | BUILT | sourced process-effect rows | NOT_EVIDENCED | **D1** | append-only JSONL | `ledgers/data/EVD.jsonl`, `reports/h_state/ledger_stats.json` |
| 15 | Compatibility axes registry (13) | BUILT | canonical axis space | 36A.3 `[SI §2]` | D4 | CSV registry | `registry/rag/compatibility_axes_v1.csv` |
| 16 | Compatibility engine (9 axes) | BUILT | UNKNOWN-neutral matching | C7 `[BT]` | D4 | rule table `VALUE={MATCH 1.0, NEAR 0.5, UNKNOWN 0.25, MISMATCH 0.0}` `[IR]` | `…/retrieval/compatibility.py` |
| 17 | pH bands (axis 7) | BUILT in compiler; **`C_t` not wired** (D-136) | acidity applicability | freeze step 8 `[SI]` | D4 | FDA/CFSAN 2003 table + AI-drafted crosswalk | `…/composition/ph_bands.py`, `registry/food_ph_fda2003_v1.csv`, `registry/food_ph_fda_ing_crosswalk_draft_v1.csv` |
| 18 | Evidence router | BUILT | route per (event, ingredient, target) | NOT_EVIDENCED | D4 | frozen router 0.4.1 + composition-aware routing `[SRC:state_full.py]` | `…/mechanism/router_demo.py`, `…/composition/router_v12.py` |
| 19 | Structured retrieval | BUILT | primary retrieval | C6 `[BT]` | D4 | structured index + food graph | `…/retrieval/retriever.py`, `food_graph.py` |
| 20 | Lexical retrieval (BM25) | BUILT | free-text fallback | C6 `[BT]` | D4 | BM25 | `…/retrieval/bm25.py` |
| 21 | Dense retrieval | PARTIAL — reported in `[BT C6]` (RRF BM25 + e5-large-v2); **source file path NOT_EVIDENCED** in this pass | fallback blend | C6 | D4 | e5-large-v2 `[BT]` | NOT_EVIDENCED |
| 22 | Query-specific evidence compiler | BUILT | pick axes *before* retrieval | 36A `[SI §2]` | D4 | registry-driven rules | `…/composition/evidence_compiler.py` |
| 23 | Claim Packet | BUILT | bound what may be said | 36A (CR-65) `[SI §2]` | D4/D5 | deterministic | `…/composition/claim_packet.py` |
| 24 | LLM Layer-1 proposer | BUILT — surface = **ONE field `alternative_group` on ONE trigger `VNEXT_ALTERNATIVE_SKIPPED`** (D-135) | resolve one ambiguity class | 36C / 36A.3 `[SI §2]`,`[D]` | beyond contract ("no GPU required" `[CM]`) | qwen2.5 7B / 72B via Ollama, offline only `[S7]`,`[ST]` | `…/composition/layer1_proposer.py`, `reports/s180/step7_arm_*.json` |
| 25 | Verbalizer | **Template: BUILT.** LLM rephrase: PARTIAL, **unpromoted** `[BT C16]` | phrase the packet | C16 | D5 | template | `…/generation/verbalize.py` |
| 26 | Claim verifier / template fallback | BUILT | check text against packet | 36C `[SI §2]` | D4/D5 | deterministic number/axis checks `[SRC:claim_verifier.py]` | `…/composition/claim_verifier.py`, `…/generation/claims.py`, `enforce.py` |
| 27 | Benchmark | BUILT (n = 74) | D5 evaluation | NOT_EVIDENCED | D5 | 8 task types (D-090) `[CM]` | `benchmark/d5/`, `reports/del5/` |
| 28 | 8 demo scenarios | BUILT (backend runner) | contractual scenarios | NOT_EVIDENCED | D5 | authored cases | `tools/s179_submission_demo.py` |
| 29 | Demo server | BUILT | local/public JSON API | NOT_EVIDENCED | D5 | Python stdlib `ThreadingHTTPServer`; `GET /api/health`, `POST /api/ask` `[SRC:server.py]` | `…/app/server.py`, `strict_server_v3.py`, `app/static/{index,strict_v3}.html` |
| 30 | Deployment: Vercel static snapshot + Next.js UI | **PLANNED_ONLY** — `web/` and `tools/build_demo_snapshot.py` **absent on disk 17 Nov** | default serving path `[DEP]` | — | D5 | — | spec only: `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md`, `design/*.md` |
| 31 | Deployment: live gateway on presenter Mac via Cloudflare Tunnel | **PLANNED_ONLY** (server exists; tunnel/BFF/`/api/trace` scheduled 19 Nov `[DEP §8]`) | optional live path | — | D5 | no Ollama on request path `[DEP]` | spec only |
| 32 | Streamlit demo (as named in proposal) | **CUT** — "no Streamlit app exists" `[CM]`; substitution must be declared | — | — | D5 | — | — |
| 33 | Learned compatibility, causal graph, multimodal input, new evidence KG, probabilistic uncertainty engine, learned state encoder, FoodOn/FNDDS expansion, simulator expansion | **CUT** by the 15 Nov directive `[ST]` | — | — | — | — | — |
| 34 | Molecule set (IMAP) in state; water:food ratio; a_w; enzyme state; browning/texture | **DEFERRED** / schema-only `[SI §3]` | — | — | — | — | see `docs/final/FINAL_STATE_SCHEMA.md` table 2 |
| 35 | Vitamin C Model A formula | BUILT — `FORMULA_RESEARCH_ONLY`, NOT_VALIDATED `[SRC:state_full.py]` | illustrative Y cell | Step 10 `[SI]` | D3 | fitted formula | `tools/s179_state_dataset_fill.py` (`l2_cells`) |

## Table B — flow, evaluation, limits

| # | Input → internal processing → output | Evaluation | Current result (source) | Gate | Novelty status | Limitation | Next consumer |
|---|---|---|---|---|---|---|---|
| 1 | source files → ingest → recipe records | count | 612,782 recipes in the fill run `[FILL]`; 611,902 in the vNext differential `[D] D-134` (**two different counts**) | n/a | not novel | BBC text licence-restricted (D-003 `[MP]`) | 2–5 |
| 2 | line text → encoder+CRF → typed spans + confidence | grouped TEST, seeds | RecipeDB3 micro 0.9581 ± 0.0012, macro 0.9545 ± 0.0037; TASTEset micro 0.9371 ± 0.0024 `[NER]` | TIE with clean baseline | **not novel as a model**; novel finding = protocol leak (13.6% / 5.4%) `[NER]` | unseen-mention F1 0.8553 (RecipeDB3) / 0.7008 (TASTEset) `[NER]`; no external-domain test | 3 |
| 3 | mention → embed / lexicon → ING id or NIL | held-out alias | Acc@1 0.704 (n=96), Recall@5 0.854, NIL AUROC 0.665 `[NER]` | advisory | system only | false-NIL on known aliases 0.567 `[NER]` | 8, 11 |
| 4 | quantity string → grammar → value/unit | coverage | "90% lines" `[BT RQ07]`; mass 0.6% groundable `[SI §3]` | none | system only | `MASS_NOT_GROUNDED` everywhere in C | (none in State v2) |
| 5 | step text → lexicon/rules → `proc_id`, family | fill | `process_id` filled 99.08–99.82% of rows by family `[FILL]` | none | system only | no accuracy vs gold: NOT_EVIDENCED | 6 |
| 6 | producer output → `EventCandidate`/`EntityCandidate`/`AllocationCandidate` → `EventGraph` | unit tests | 12 tests for the new fields/invariant `[IR §7]` | none | system contribution | `condition_profile_id` has no referent/consumer `[D] D-135` | 7 |
| 7 | `EventGraph` → V1 span round-trip, V2 quantity, V3 vocabulary, V4 invariants → issues (never repairs) | unit tests | 5 invariants pre-existing + alternatives closed 15 Nov; 5 open scopes `[IR §4–5]` | `DRAFT_PENDING_16c` | system contribution | open: replay, mass-balance scope `[IR §5]` | 10, 11 |
| 8 | parsed steps → rules A guard / B fat stays / C mixture coref / D alternatives → lot bindings + flags | differential only | 29.3% of recipes changed — **DIAGNOSTIC**; flags MIXTURE_COREF 140,828 · FAT_STAYS 68,868 · ALTERNATIVE_SKIPPED 48,520; 0 exceptions raised over 611,902 `[D] D-134` | **DIAGNOSTIC; no gold regression set** | not claimed | spot checks Wikibooks-only, informal `[D] D-134` | 9, 24 |
| 9 | entities+events → parentage → lots | V4 | — | none | prior art exists `[MP §7]` | — | 10, 11 |
| 10 | events → replay → state | 30 scripted sessions | "30 sessions pass" `[BT C3]` | 40-gold evaluation **not performed** `[CM]` | system contribution | sessions are AI-drafted `[BT E16-D]` | 11 |
| 11 | recipe text → Rung A parse + physics L1/L2 + context v1.2 + router → list of per-(food, step) cells `{v,b}` / `{v:None,u}` | corpus fill | see `FINAL_STATE_SCHEMA.md` | none (`scientific_gate_pass: False` `[SRC:s179_state_dataset_fill.py]`) | **core contribution (integration)** | sparse; markers AI-drafted, salt/acid AI check FAILED (D-128 `[SI §7]`) | 13, 22, 23 |
| 12 | two vectors → per-dim difference | none | NOT_EVIDENCED | none | — | not a cell-level diff | UI ΔS (planned) |
| 13 | state → named masked dims → (values, mask) | retrieval diagnostic | chance Jaccard 0.001; overlaps 0.0455–0.1164; 34/40 queries share nothing across three views `[ST]` | DIAGNOSTIC_ONLY | not claimed | weights unvalidated; V0 has Q = 2 of 51 dims `[SI §4]` | retrieval diagnostic only; "never decides" `[SI §7]` |
| 14 | sources → curated rows with source + tier | ledger stats | 17,978 ACTIVE; all tier E3; **0 human-verified** `[CM]` | D1 PARTIAL | resource | 0 of ≥40 hand-verified rows | 18, 19 |
| 15–16 | (query state, evidence row) → per-axis match → MATCH / NEAR / UNKNOWN / MISMATCH | unit tests | 9 implemented · 2 in compiler (7, 9) · 2 schema-only (8, 12) `[ST]` (verified against the CSV) | none | system contribution | axis 9 reports `QUERY_ONLY`, never EVALUABLE `[ST]` | 22 |
| 17 | ING id → EXACT/FULL crosswalk → band vs 4.6 | 15 tests `[SI]` | 479 rows → 140 ING bands: 31 acidic, 101 low-acid, 8 inconclusive `[ST]` | crosswalk `UNVERIFIED_CROSSWALK_AI_DRAFTED` | system | ingredient as purchased, not the lot (D-136) | 22 |
| 18 | router item + context → route + reasons + evidence / near evidence | — | NOT_EVIDENCED (aggregate) | none | system | two targets only: vitamin C (SVAR-000009), lycopene (SVAR-000025) `[SRC:state_full.py]` | 11 (Y block) |
| 19–21 | query → index lookup / BM25 / dense → candidates | silver | structured MRR 0.856 vs hybrid 0.704 vs BM25 0.597; free-text RRF 0.762 `[BT]` | NEED_DATA (human-labelled pairs) `[BT RQ03]` | system only | silver, not gold; Recall@K / ECE not reported `[CM]` | 16, 22 |
| 22 | (state, target, question kind) → `select_axes` → per-axis cells incl. `ph_axis_cell`, `geometry_axis_cell` → compiled evidence | unit tests | covers all 13 axes `[ST]` | none | system contribution | — | 23 |
| 23 | compiled evidence → allowed/forbidden claims, caveats, evidence ids, max precision, UNKNOWN reasons | unit tests | NOT_EVIDENCED (no aggregate metric) | none | system contribution | — | 25, 26 |
| 24 | (raw, graph, flags) → trigger licensing → model proposals → `review` gate incl. `span_grounds_value` → accepted proposals → `apply` → V4 | sealed 60 cases | 72B v3: 63 returned, 21 accepted, 21 grounded `[S7]` | DIAGNOSTIC_ONLY, NOT_GOLD | not claimed as accuracy | no gold; recall unmeasured; endpoint filter incomplete; duplicates unchecked `[S7 §5]` | 6, 7 |
| 25 | packet → template sentence(s) | contract cases | "0 unsupported / 0 violations" (template) `[BT C16]` | readability needs humans `[BT]` | not novel | LLM path unpromoted | 26 |
| 26 | (text, packet) → number / axis-word / reason checks → pass or `template_answer` | unit tests | NOT_EVIDENCED (aggregate) | none | system contribution | lexical instrument | answer |
| 27 | questions → ladder B0…B5, ablations | H1/H3 | H1, H3 **RULE_NOT_MET** (see `reports/final/CLAIM_AND_SOTA_MATRIX.md`) | RULE_NOT_MET | — | AI gold, NON_CITABLE | report |
| 28–29 | question (+recipe) → `DemoContext.respond` → JSON | 8 guard cases | "Eight authored backend demo guard cases pass … Not eight implemented features, broad accuracy or an actual human rehearsal" `[ST]` | none | — | load ~153 MB JSONL, 9.7 s, 1.21 GB RSS; query ~30 ms `[MP §15–17]` | UI |

## Contradictions / NOT_EVIDENCED

- Corpus size: **612,782** `[FILL]` vs **611,902** `[D] D-134` — different runs; do not merge.
- Unit-test count: 5,960 and 5,968 `[ST]`, 5,977 `[MP]` — three values on three dates.
- Deployment: `[MP §15–17]` diagram shows "FastAPI gateway on the research server … + Ollama";
  `[DEP]` decides stdlib gateway on the presenter's Mac with Ollama removed. `[DEP]` is the later,
  more specific document; `[MP]` diagram is stale.
- The explorer UI named by the branch (`s181-explorer-build`) was **not found on disk** (`web/` absent).
- 36-step owners marked NOT_EVIDENCED were not stated in any file opened.
