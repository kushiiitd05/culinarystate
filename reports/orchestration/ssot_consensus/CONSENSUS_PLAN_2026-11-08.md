# CulinaryState — consensus plan to 25 Nov and after (2026-11-08)

Status: **AI_DRAFTED / PROPOSED** (final editor, S176 consensus audit). Nothing here is a signature, approval or decision (D-071). Built from `registry/component_ledger_v1.csv` (493 rows after round 2), `reports/orchestration/ssot_consensus/CONSENSUS_DRAFT.md`, `contested_round1.json` and the round-2 votes of R-FEAS, R-SCI and R-SSOT. Hours are ledger estimates (UNVERIFIED). Status comes from the repo paths in the ledger, not from plan text. Today is 2026-11-08; the talk is 25-26 Nov.

**How to use this file:** read section 1, then the table in section 4 (that is the work for the next 17 days). Section 6 lists the decisions only Kush and Parv can make; most are due 9-12 Nov. Sections 3 and 5 are the full reference lists.

## 1. Verdict: where the project stands against the SSOT

Of the 217 SSOT components the audit found, **13 are DONE** (a gate passed or a contract closed) and **25 have RUN** at scale without validation; 70 exist as code only, 35 as drafts, 29 are not started, 25 are blocked (almost all on a human step) and 20 are out of scope for the course. The front of the chain is real and full scale: the 612,782-recipe base and identity layer (07I), the E3 evidence plane (17,978 ACTIVE EVD rows, 4,746 COND rows), Rung A extraction (9,470,190 events, `reports/step17/rung_a_dryrun_counts_full_corpus_final.json`), replay and the 26g census (14,594,812 engine events, SIMULATE 0, `reports/step26/simulability_census_full_corpus_S169.json`), Layer 1 / Layer 2 physics over 1,746,405 heat events (only 3.4 % driver-ready from the text alone, 5.3 % bounded by ranges; `reports/step26/binding_census_L1_*_full_S17{3,4}.json`), and the router census (DIRECT 274,058 = 0.754 % of 36,359,902 checks). The middle and back of the SSOT are not there yet: **no PARAM, no calibrated or held-out-validated model, no gold comparison for the state tracker (D3), no frozen D5 benchmark, and no confirmatory result (H1/H3 not run, H2 diagnostic only).** Every one of those waits first on a human step (signatures, 07.A-R1 labels, AA row verification, D5 review), not on compute. Two gates are FAILED on record (07.A kappa, G08-3 lineage) and must stay visible. Levels 12-17, learned representations, D2 and H4 are out of reach before 25 Nov. Honest summary for the talk: a working, audited, full-corpus pipeline up to the router, whose main finding is how little the data supports (mostly UNKNOWN), plus — if the humans finish their 9-16 Nov tasks — one research-only SIMULATE pilot (vitamin C) and a pre-registered H1/H3 result.

Two facts the review packet gets wrong and the report must not repeat: `handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md` §4 calls 14,594,812 "Rung A events" (it is the 26g census engine-event total; Rung A is 9,470,190), and it says `registry/scenario_defaults_v1.csv` has 28 rows (it has 27 data rows).

## 2. Done vs not done

### 2.1 Components by status, per topic

| Topic | DONE | RUN | CODE | DRAFT | NOT_STARTED | BLOCKED | OUT_OF_SCOPE | Total |
|---|---|---|---|---|---|---|---|---|
| T0 SSOT core, laws, router, output contract | 1 | 2 | 7 | 3 | 2 | 2 | 2 | 19 |
| T2 Evidence plane (EVD/COND, 07.A, lineage, AA extraction, D1) | 4 | 2 | 5 | 4 | 1 | 4 | 1 | 21 |
| T3 Recipe semantics and state tracking (Rung A, replay, NER, lot state) | 3 | 8 | 3 | 6 | 2 | 2 | 1 | 25 |
| T4 Process conditions and physics (Layer 1 / Layer 2, non-heat) | 0 | 5 | 10 | 2 | 7 | 1 | 1 | 26 |
| T5 Mechanisms, kinetics, simulation (AA pilot, router SIMULATE) | 0 | 2 | 7 | 2 | 3 | 3 | 5 | 22 |
| T6 Transition learning and sparsity (29-diag, H2, D2) | 0 | 1 | 8 | 2 | 2 | 2 | 5 | 20 |
| T7 Representations and similarity (Step 35, Levels 12-13) | 0 | 0 | 5 | 3 | 8 | 7 | 4 | 27 |
| T8 Application layer (RAG, D4/D5, H1/H3, demo) | 0 | 5 | 15 | 3 | 1 | 1 | 0 | 25 |
| T9 Governance, evaluation design, deliverables, timeline | 5 | 0 | 10 | 10 | 3 | 3 | 1 | 32 |
| **All** | 13 | 25 | 70 | 35 | 29 | 25 | 20 | **217** |

There is no T1 topic file; T0 covers the SSOT core and Levels 7-11 (open question in section 6).

### 2.2 Open items per topic, by priority

| Topic | MUST | SHOULD | COULD | AFTER | Open items |
|---|---|---|---|---|---|
| T0 | 4 | 10 | 4 | 7 | 25 |
| T2 | 12 | 22 | 13 | 17 | 64 |
| T3 | 5 | 30 | 22 | 7 | 64 |
| T4 | 5 | 20 | 14 | 13 | 52 |
| T5 | 11 | 19 | 14 | 12 | 56 |
| T6 | 8 | 10 | 4 | 29 | 51 |
| T7 | 1 | 27 | 18 | 16 | 62 |
| T8 | 17 | 9 | 11 | 6 | 43 |
| T9 | 21 | 21 | 10 | 3 | 55 |
| **All** | 84 | 168 | 110 | 110 | **472** |

### 2.3 DONE components (13)

| Component | Evidence (repo paths) |
|---|---|
| T0-C01 Final decision, scope rule and frozen project laws | DECISIONS.md D-027 (original 36-step spine governs); reports/master_plan/review_queue/rulings_D-027_R01-R20.md; handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md §2.3 (frozen rules) |
| T2-C01 EVD endpoint ledger + export v1 (process-event table, E3 plane) | ledgers/data/EVD.jsonl (57,280 version lines, 18,156 ids, 17,978 ACTIVE, 178 DEPRECATED; all tier E3); SRC split of ACTIVE: USDA R6 SRC-000001 7,018 / Bognar SRC-000141 7,090 / Phenol-Explorer SRC-000012 3,870; reports/es1/es1_1_audit.md (GATE PASS, 17,978 in … |
| T2-C03 SVAR registry (state variables) and physical/history variables | ledgers/data/SVAR.jsonl 355 rows: 354 CHEMICAL, 1 PHYSICAL; registry/state_variable_registry_v1.csv; registry/svar_duplicate_mapping_v1.csv |
| T2-C04 COND ledger and condition normaliser (07 automated part) | ledgers/data/COND.jsonl 4,746 ACTIVE rows; reports/step07/step07h_gate_result.json (G1-G10 PASS), step07hr_gate_result.json (G1-G7 PASS), step07hr_freeze_manifest.json (fingerprint e7d58913...); reports/step07/step07_condition_coverage_audit.json |
| T2-C14 Pre-freeze rulings (15.0) and 15a.R reserved-group seal | D-068 (RESERVED_FRACTION 1/5, STUDY_THEN_CELL, stratify SOURCE_FAMILY, seed hash 73d3ed4d...); reports/step15/15a_R_seal_commitment_v1.json (886 groups, 177 reserved, 3,555 rows, sealed 2026-11-06, list outside git); … |
| T3-C15 Gold pilot P1 (7 recipes, dual annotation, counts-only scoring) | reports/step19/p1_agreement_counts_S166.json; reports/step19/pilot_start_record.SIGNED.json (D-048); DECISIONS D-057..D-067 |
| T3-C20 Recipe identity, duplicates, families and split groups (07I) | reports/step07i/step07ir_gate_result.json; reports/step07i/identity_summary_v1.json; reports/step07i/identity_benchmark_report.md |
| T3-C23 Recipe-level metadata, source/licence fields and recipe base | ledgers/recipe_base/recipe_base_v1.parquet; registry/recipe_source_usage_registry_v1.csv; DECISIONS D-026 (all 612,782 usable for project use) |
| T9-C01 Steps 01-02: project authority + implementation audit | registry/plan_authority_map_v1.csv (28 rows); reports/step07i/plan_authority_inventory.md; registry/negative_results_register_v1.csv (31 rows) |
| T9-C02 Step 03: state semantics / SVAR registry / MP-1 contract | registry/state_variable_registry_v1.csv (254 rows; packet says 355 SVAR: 354 chem + 1 physical); reports/h_state/state_representation_contract_v1.md; DECISIONS D-018, D-029 |
| T9-C03 Step 04: evidence / provenance / similarity contracts + lineage min-contracts | reports/step04/{lineage_contract_v1_1,04_2_min_value_documentation,04_6_min_data_plane_rules,04_9_min_namespace_reservation}.md; registry/schemas/{DOC,LIN,SEXP,SMP,OBS,KIN,KINPT,FORM,PARAM,VAL}.draft_*.schema.json; DECISIONS D-029, D-051 |
| T9-C04 Step 05: EVD normalisation (17,978 E3 rows) + EVD export view | reports/es1/es1_1_audit.md (gate PASS 2026-10-22); ledgers/data/EVD.jsonl (57,280 lines; 17,978 ACTIVE); exports/lineage/step08a_v1/evd_export_v2.manifest.json |
| T9-C07 Human-gate registry H1-H8 and D-045 / D-071 delegation rules | DECISIONS.md D-045 (W1-W3), D-071, D-068, D-057/D-064 (agent-generated salts); handoff/REVIEW_SHEET_AI_VERDICTS.md; registry/human_verification_queue.csv (HV-001..010) |

A DONE component can still have open items (for example T9-C07 keeps R2-R4: the written permission copy, the D-071 report section and the H8 scope register).

### 2.4 RUN components (ran at scale; none is validated)

| Component | Evidence (repo paths, from the topic inventories) |
|---|---|
| T0-C03 Shared research spine: state S_t, process P_t, transition T | Rung A 9,470,190 events (reports/step17/rung_a_dryrun_counts_full_corpus_final.json); 26g census 14,594,812 engine events; src/culinarystate/state_graph + extraction/rung_a*.py; registry/state_variable_registry_v1.csv; reports/h_state/state_representation_contract_v1.md; D-027, D-070..D-074 |
| T0-C04 Process representation and local driver trajectories theta(x,t) | registry/scenario_defaults_v1.csv (27 data rows, SOURCE_UNVERIFIED_AGENT_RECALLED); src/culinarystate/simulation/{condition_binding,scenario_layer,physics_drivers,sim_core,choi_okos}.py; reports/step26/binding_census_L1_*, scenario_L2_*; DECISIONS D-077; handoff/FINISH_PLAN S174 log: 1,746,405 heat … |
| T2-C06 Source lineage 08a on the 17,978 EVD rows (study / lineage root / split group keys) | reports/step08/step08a_audit_result_v2.json (G08-3 FAIL: B3 13/50 Kush, 0/50 Parv; B2 49/50 vs 0/50 with 49 UNCERTAIN; STRONG 50/50 both); D-032, D-033, D-034 (B3 cut 0.75 kept); ledgers/data/DOC.jsonl 1,967; STUDY.jsonl 257 version lines (all design UNKNOWN); SRC_08A_YIELD.jsonl 7; … |
| T2-C17 EVD to ingredient/process linkage (ING, PROC, prior_state) for routing | src/culinarystate/evidence/{linker,link_review}.py; registry/evidence/evd_ingredient_link_decisions.csv (389 rows: LINKED 237, HELD 129, CONCEPT_MISSING 23); reports/es1/es1_1_audit.md (ingredient_id UNKNOWN 6,409, prior_state UNKNOWN 5,536, process_id UNKNOWN 157); HV-008 NOT_STARTED, HV-010 … |
| T3-C03 Vocabulary: ING / ALIAS ingredient concepts and canonicalization tree | reports/ingredient_registry_v1.md; registry/ingredients/{ingredient_registry_v1,alias_registry_v1}.csv; ledgers/data/ING/ALIAS (protected from our edits); reports/ner/alias_leakage_audit.md |
| T3-C05 Process vocabulary (PROC) and process hierarchy | reports/process_registry_v1.md; registry/processes/{process_registry_v1,process_hierarchy_v1_DRAFT,endpoint_vocabulary_v1_DRAFT}.csv; handoff/PROCESS_COVERAGE_PLAN_2026-11-08.md |
| T3-C06 Tool vocabulary (TOOL) and tool-role registry | reports/tool_registry_v1.md; ledgers/data/TOOL.jsonl (297 rows); registry/recipe_semantics/tool_role_registry_v1_DRAFT.csv |
| T3-C07 Quantity parsing and normalisation (CQPO quantity layer) | reports/step16/S161_real_data_runs.md; reports/step16/rc2_grounding_dryrun_counts.json; reports/step16/sp002_fix_design_ksh_S168.md; reports/quantity_coverage_v0.md; D-069,D-070 |
| T3-C09 Ingredient-line NER deployment and MENTION ledger draft | reports/ner_v2/ner_corpus_counts_S174.json; registry/compute_runs_v1.csv RUN-S174-003; reports/ner/culinaryner_kf_final_report.md; handoff/NER_RUNBOOK.md; reports/ner_v2/final_link_human_agreement.md |
| T3-C11 Rung A deterministic instruction extraction (events, quantities in steps, references) | reports/step17/rung_a_dryrun_counts_full_corpus_final.json; reports/step17/S155_build_note.md; reports/step17/d073_r1_precision_S170.json; DECISIONS D-073,D-074; tests/unit/test_step17a_*.py |
| T3-C12 Event-sourcing replay engine and event log | reports/step18/S156_build_note.md; reports/step18/S156_engine_audit.md; src/culinarystate/state_graph/{replay,event_log,event_adapter}.py; reports/step26/simulability_census_full_corpus_S169.json; WORKLOG S169 (census 0.2.0: 612,782 recipes, 14,594,812 events, exceptions 0) |
| T3-C14 Deep-Gold sampling frame, strata and hard-case sampling | tools/step16b_build_frame.py; tools/step16b_text_strata.py; reports/step16/16b_text_strata_README.md (431,458 frame rows); reports/step19/pilot_start_record.SIGNED.json; registry/recipe_semantics/deep_gold_pilot_v1/ |
| T4-C02 Condition schema: raw-first typed condition tuple, POINT/INTERVAL/QUALITATIVE/UNKNOWN, COND/CV … | ledgers/schemas/COND.schema.json; registry/condition_variable_registry_v1.csv (40 CV rows); registry/recipe_condition_surface_forms_v1.csv; reports/master_plan/working_notes/notes/ssot_l14.md s1.11-1.12; DECISIONS D-024; handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md (07.A FAILED, 07.A-R1 pending) |
| T4-C04 Layer 1 TEXT_STATED binder over the full corpus (heat families) | src/culinarystate/simulation/{condition_binding,binding_census}.py; tools/binding_census.py; reports/step26/binding_census_L1_{A1,FOODCOM,GUTENBERG_SEGMENT,WIKIBOOKS,TASTESET}_full_S17[34].json; reports/step26/binding_census_L1_1000_S172.json; registry/compute_runs_v1.csv RUN-S172..S174; … |
| T4-C05 Layer 2 SCENARIO driver trajectories (GENTLE/TYPICAL/INTENSE) for heat events | src/culinarystate/simulation/scenario_layer.py; tools/scenario_layer_run.py; registry/scenario_defaults_v1.csv; reports/step26/scenario_L2_*_full_S17[34].json (FOODCOM: SCENARIO_COMPUTED 667,634; SCENARIO_UNKNOWN 768,753; UNSUPPORTED_MEDIUM 66,874; core_known True 55,146); packet s4: 810,951 heat … |
| T4-C07 Heat-conduction physics driver (infinite slab, convective boundary) and thermal-dose integrals | src/culinarystate/simulation/physics_drivers.py (slab eigen-series, equivalent minutes z=10/33, trajectory dose); tests/*/test_s172_physics_drivers.py (6 tests); 33 tests in test_s172* + choi_okos pass in this audit; used inside scenario_L2 full runs |
| T4-C21 Step 26g recipe-event to simulation-input adapter and simulability census (physical inputs side) | reports/step26/simulability_census_full_corpus_S169.json (14,594,812 events, SIMULATE 0, exceptions 0, invented 0); src/culinarystate/simulation/recipe_adapter.py; tests/*/test_step26g_recipe_adapter.py; reports/step26/CENSUS_FILES.md |
| T5-C05 Applicability / formula router 23a (APPDEC engine, gates G0-G9, Kleene logic, demo mode) | src/culinarystate/mechanism/applicability.py (677 lines); router_census.py, router_demo.py, tools/router_demo_census.py, tools/router_eval.py; reports/step23/router_demo_census_vitc_full_corpus_S171.json (36,359,902 checks, DIRECT 274,058 = 0.754 %, UNKNOWN 36,085,844); … |
| T5-C09 Counts-only physical drivers: Layer 1 TEXT_STATED binding, Layer 2 SCENARIO heat drivers, slab … | src/culinarystate/simulation/{condition_binding,binding_census,scenario_layer,physics_drivers,choi_okos,census_chain,recipe_adapter}.py; reports/step26/binding_census_L1_*_full_S173/S174.json; reports/step26/scenario_L2_*_full_S173/S174.json; registry/scenario_defaults_v1.csv (28 rows … |
| T6-C02 Baseline ladder D0-D5 and D7a implementation + DEL-2 results (the existing transition benchmark) | reports/del2/USDA-RETN-R6_results.md; reports/del2/BOGNAR-2002_results.md; reports/del2/PHENOL-EXPLORER-3.6_results.md; reports/del2/PHENOL-EXPLORER-3.6_log_results.md; reports/del2/cross_source_v1.md; src/culinarystate/transition/{baselines,splits,evaluate,dataset,cross_source}.py; … |
| T8-C04 State reconstruction interface for RAG (C3 state reconstructor, C4 process-history, C18 … | src/culinarystate/decision/session_state.py; src/culinarystate/decision/state_conditioning.py; tests/unit/test_s171_d5_state.py; registry/compute_runs_v1.csv (Step 17/18 census 14,594,812 events) |
| T8-C06 C6 multi-index retriever (BM25 + structured filter + dense + graph expansion) | src/culinarystate/retrieval/retriever.py; retrieval/bm25.py; retrieval/food_graph.py; reports/del4/retrieval_silver_v1.md; reports/del4/retrieval_silver_v2_analysis.md; reports/del4/graph_expansion_v1.md; reports/del4/rq1603_pilot_v1.md; tests/integration/test_retrieval_regression.py |
| T8-C15 C16 grounded response generator + LLM backend (Ollama, template B5T) | src/culinarystate/generation/{llm,prompts,verbalize}.py; reports/del5/ladder_v2_qwen7b.md; reports/del5/ladder_v2_qwen32b.md; reports/del5/generator_c16_v1.md; registry/compute_runs_v1.csv |
| T8-C16 C17 citation/provenance layer: claim checker + post-hoc enforcement (UCR) | src/culinarystate/generation/claims.py; generation/enforce.py; tests/unit/test_enforce.py; reports/del5/ladder_v2_qwen7b.md (B5F+E UCR 0.0) |
| T8-C19 D4 deliverable: evidence-aware retrieval with abstention (report) | reports/del4/*; FINISH_PLAN M4 core DONE S171 |

RUN means "executed on real data, counts only". It never means validated, calibrated or evidence_supported. RUN rows still lack `registry/compute_runs_v1.csv` ids for Rung A, rc2 and the replay / 26g census (NER corpus tagging has RUN-S174-003; only 14 run rows exist; open question in section 6).

## 3. What remains, by work type (MUST, SHOULD, COULD; AFTER items are in section 5)

Each item is listed once, under its main work type (order: signature > expert review > download > human review > GPU > training/fitting > CPU > code > analysis > writing; pure decisions go to 3.11). Other work types of the item are in the "also" column. Effort: A = agent hours, H = human hours. Host: where the ledger says it runs (`any` = any agent host; BBC work only on the Mac, D-003).

| Work type | MUST | SHOULD | COULD | Total |
|---|---|---|---|---|
| Code to build | 12 | 60 | 31 | 103 |
| CPU compute (host runs) | 9 | 29 | 25 | 63 |
| GPU compute | 2 | 0 | 4 | 6 |
| Training / fitting | 2 | 1 | 1 | 4 |
| Analysis | 18 | 20 | 14 | 52 |
| Downloads / acquisition | 2 | 5 | 6 | 13 |
| Human review | 9 | 18 | 11 | 38 |
| Human signatures | 7 | 10 | 3 | 20 |
| Expert review | 0 | 3 | 3 | 6 |
| Writing | 5 | 7 | 2 | 14 |
| Decisions | 18 | 15 | 10 | 43 |

### 3.1 Code to build (103)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T0-C06-R2 | End-to-end contract audit: property tests plus a corpus scan that no emitted answer contains a food-chemistry number lacking an EVD id or a frozen-model id; include app … | A 5-8 / H 0 | any (Mac for hypothesis) | T0-C06-R1 | MUST | ANALYSIS |
| T5-C07-R3 | Mint PARAM rows ONLY from rows both humans VERIFIED (K>=K1, source locator, fitted_on block); automated check 0 PARAM from K0 aggregates. | A 2-4 / H 0 | any | T5-C10-R4 | MUST | — |
| T5-C11-R4 | Wire router SIMULATE branch end-to-end: eligible AA events (steam/sealed medium) -> retention INTERVAL with PARAM id and basis; all else UNKNOWN; record in SIM output … | A 6-10 / H 0 | any | T5-C10-R5 | MUST | — |
| T6-C02-R1 | Write registry/transition_ladder_crosswalk_v1.csv (B-0=D0, B-1=D1, B-2=D3 matrix arm, B-3=D2, B-4=D4, B-5=D5; M0..M11 map) and fix label mismatch between 29-diag prereg … | A 1-2 / H 0 | any | — | MUST | WRITING |
| T6-C03-R5 | Add paired D2-process-mean vs D3-ingredient-mean contrast (H2 shape: process info vs food-identity-only) on S-3/S-4/S-6 inside the diag memo, DIAGNOSTIC only, using … | A 2-3 / H 0 | any | T6-C03-R3 | MUST | ANALYSIS |
| T6-C19-R1 | Record the learning environment per host (mac pinned versions; vinayak; manjot CPU) in a lock file; run a smoke import and the transition test suite on each. | A 1-2 / H 0.3 (Parv authorises) | any | — | MUST | DECISION |
| T8-C01-R1 | Score router branch accuracy on the frozen D5 80 questions (never tune on them); report confusion matrix incl. X controls | A 1-2 / H 0 | any | T8-C20-R3 | MUST | ANALYSIS |
| T8-C20-R3 | Freeze benchmark (sha256) and run freeze check | A 0.5 / H 0.3 | any | T8-C20-R2 | MUST | — |
| T9-C07-R3 | Report section stating exactly which gates were AI-delegated (D-071) vs human-signed, generated from DECISIONS (script, counts only) | A 1-2 / H 0.5 | any | D-071 | MUST | WRITING |
| T9-C09-R1 | Build and hash a SPLIT registry for the three evaluations that will run (D5 benchmark questions, 29-diag S-1..S-5, 07.A packet) and record in ledgers via orchestrator | A 3-5 / H 0 | any | T9-C10; T9-C17 | MUST | ANALYSIS |
| T9-C25-R4 | Log every new S176 run row in compute_runs_v1.csv (orchestrator merges); counts-only outputs; sha256 | A 0.5 per run / H 0 | any | — | MUST | — |
| T9-C28-R2 | Check slides/report/demo screenshots for recipe text leakage (automated grep of committed outputs against git-ignored text hashes) | A 1-2 / H 0 | any | T9-C20; T9-C21 | MUST | ANALYSIS |
| T0-C06-R3 | Show the three-way label and basis (EVD/Layer 2/ASSUMED) on every demo claim chip. | A 2-3 / H 0 | mac | M6 demo | SHOULD | — |
| T0-C09-R2 | End-to-end regression suite for the whole loop (parse -> state -> route -> packet -> answer) on 50 recipes with golden outputs. | A 3-4 / H 0 | any | none | SHOULD | — |
| T2-C02-R1 | Decide the storage form for the AA pilot rows (KIN/KINPT ledger vs staged CSV) and add KIN/KINPT/XTR/ADJ schemas to ledgers/schemas | A 4-8 / H 0.5-1 | any | T2-C02 validator; D-076 | SHOULD | DECISION |
| T2-C02-R2 | Orchestrator-owned append of verified AA rows as new KIN/KINPT ledger (not protected EVD) with hashes | A 1-2 / H 0-0 | any | T2-C09-R4; T2-C02-R1 | SHOULD | — |
| T2-C03-R2 | Append additive SVAR v1.1 rows (physical/history) via orchestrator, before the 15a freeze is approved or as 15a.1 | A 3-6 / H 0-0 | any | T2-C03-R1; T2-C15-R3 | SHOULD | — |
| T2-C08-R1 | Build golden fixtures (synthetic tables with seeded fabricated values, unit/basis traps, censoring footnotes, figure-only series, empty document) and the G09-1..G09-7 … | A 8-16 / H 1-2 | any | T2-C02-R1 | SHOULD | — |
| T3-C01-R1 | Fold SP-001 and SP-004 plus lot-state fields into STATE/ENTITY v1.1 drafts under new ids (R-18: new versions only) with validator tests | A 6-10 / H 0 | any | T3-C25 design decision | SHOULD | WRITING |
| T3-C08-R1 | Build POR candidate records from SR Legacy food_portion (basis SR_PORTION, interval low/high, sample_count) after the C04 decision | A 4-6 / H 0 | manjot | T3-C04-R3; T3-C04-R1 | SHOULD | — |
| T3-C11-R1 | Diagnostic comparison of Rung A events against the P1 gold (7 recipes) and the 40 AI-assisted dev-Gold recipes using tools/eval_compiler_vs_gold.py, labelled NOT … | A 4-6 (BBC recipes need the … / H 0.5 | mac | T3-C15 | SHOULD | ANALYSIS |
| T3-C12-R3 | Add §233.2 belief fields (timestamp, provenance class, unknown flag) to replay output records per lot-step | A 4-6 / H 0 | any | T3-C22-R1 | SHOULD | — |
| T3-C14-R1 | Frame update for P1b: exclude all 21 P1 manifest rows and groups; wave-scoped files and --wave P1b support in pilot_real/pilot_commit/packet maker/scorer (test-first) | A 4-6 / H 0 | any | Kush nonce and size (T3-C16) | SHOULD | — |
| T3-C20-R1 | State the calibration caveat on every split used by T3 items; add a conservative union grouping check (exact U provisional family U title) for any gold/test partition | A 2-3 / H 0 | manjot | — | SHOULD | ANALYSIS |
| T3-C21-R1 | Draft SVAR v1.1 physical/history registry (definitions, units, allowed types, UNKNOWN semantics) as additive file; no write to SVAR.jsonl | A 4-6 / H 0 | any | T3-C25-R1 | SHOULD | WRITING |
| T3-C24-R1 | Extract the Q and V cases into a machine-readable fixture file (text only from SSOT; no third-party text) and run rc2 / vocab / link against it as a conformance report | A 8-14 / H 0 | any | T3-C07-R1 | SHOULD | ANALYSIS |
| T4-C01-R1 | Freeze a PROC to process-family registry (one row per PROC, one primary family, secondary flag) covering all 93 PROCs and the 8 non-heat families, with verb ambiguity … | A 3-5 / H 1-2 | any | PROCESS_COVERAGE_PLAN | SHOULD | DECISION |
| T4-C02-R2 | Add per-axis provenance (basis code, span id, layer L1/L2) to the physical-record schema so every field is the SSOT tuple (value,unit,type,mask,provenance) | A 3-5 / H 0 | any | T4-C20 | SHOULD | — |
| T4-C05-R3 | Q1 circularity control: basis masks on every Layer 2 feature plus an ablation that removes Layer 2 before any use in Steps 30-35 (lean b of packet) | A 3-5 / H 1 | any | Kush decision on Q1 | SHOULD | DECISION |
| T4-C06-R3 | Add defaults for non-heat families (cold bath T fridge/freezer, brine strength, soak durations, drying air T/RH, storage T, cut half-thickness for cube/cylinder) | A 4-6 / H 0 | any | T4-C12 | SHOULD | ANALYSIS |
| T4-C07-R1 | Verification pack: compare slab series with a finite-difference solve and with textbook chart values for several (Bi, Fo); report max error; add convergence test for … | A 3-5 / H 0 | any | none | SHOULD | ANALYSIS |
| T4-C08-R1 | Add finite-cylinder and sphere eigen-series (Bi roots, Heisler products) and a cut-class/ingredient-class to shape map, keeping slab as the stated bound | A 5-8 / H 0 | any | T4-C07-R1 | SHOULD | — |
| T4-C11-R2 | Generalise Binder to the non-heat families (time, target T, medium, size where stated, else UNKNOWN) with tests on constructed and real samples | A 8-14 / H 0 | any | T4-C11-R1; T4-C01-R1 | SHOULD | — |
| T4-C12-R1 | Build driver + scenario defaults + Layer 1 binding for COOLING family and unit tests | A 6-12 / H 0.5 | any | T4-C11-R2; T4-C06-R3 | SHOULD | ANALYSIS |
| T4-C14-R1 | Build driver + scenario defaults + Layer 1 binding for FERMENT_LEAVEN family and unit tests | A 6-12 / H 0.5 | any | T4-C11-R2; T4-C06-R3 | SHOULD | ANALYSIS |
| T5-C01-R1 | Author 20-32 MECH entries as JSONL from the roster, each with >=1 evidence id with document type (use EVD/SRC/DOC ids already in repo; literature DOC for rest), … | A 6-8 / H 0 | any | T5-C01-R4 decision on prefix/enums (can start under AI_DRAFTED … | SHOULD | WRITING |
| T5-C01-R2 | Pre-build the 32-entry screen subset needed by the lot-state mechanism screen (alliinase, onion LFS, PPO, myrosinase, Maillard, caramelisation, starch gelatinisation, … | A 4-6 / H 0 | any | T5-C01-R1 | SHOULD | — |
| T5-C02-R2 | Implement the Kleene three-valued mechanism screen (reactants present / drivers in window / inhibitors) over lot state producing POSSIBLE / NOT_POSSIBLE / UNKNOWN per … | A 8-14 / H 0 | any | T5-C01-R1; T5-C02-R1 | SHOULD | — |
| T5-C07-R2 | Mint FORM rows for first-order Arrhenius AA (reference-T form), zero-order and Weibull stubs; reproduce >=1 source figure/table within tolerance (/dC/C0/<=0.02 on … | A 6-10 / H 1-2 review | any | T5-C07-R1; T5-C10-R3 | SHOULD | ANALYSIS, WRITING |
| T5-C07-R5 | Kinetic units rows (min^-1, s^-1, kJ/mol, kcal/mol) into UNIT ledger via orchestrator; wire units.py checks to ledger. | A 1-2 / H 0 | any | — | SHOULD | DECISION |
| T5-C08-R1 | Freeze KIN/KINPT after AA rows exist to test it; write AA pilot rows into KIN/KINPT form (not only a CSV packet). | A 3-5 / H 1 | any | T5-C10-R3 | SHOULD | DECISION |
| T5-C13-R1 | Implement baselines (S27-B1 persistence/mean-retention, S27-B3) and negative controls NC-1..4 and cluster sign-flip inference; test on synthetic. | A 8-12 / H 0 | any | — | SHOULD | — |
| T6-C01-R1 | Freeze one canonical cell definition (food key, process key, target key, condition bin) and recompute density / support / cold-start-type counts per source and pooled on … | A 3-5 / H 0.5-1 | any | freeze record 15A-BOOT approved (T6-C03-R1) | SHOULD | ANALYSIS, WRITING |
| T6-C02-R2 | Diagnose and fix or document the test_transition hang (WORKLOG S134 deselected) so the transition suite runs in CI on every host. | A 1-3 / H 0 | any | — | SHOULD | — |
| T6-C07-R1 | Diagnose D7a == D1 on PE (implementation vs sparsity: density 0.00267) and document; fix side-info learning if implementation. | A 2-4 / H 0 | any | T6-C03-R3 | SHOULD | ANALYSIS |
| T6-C09-R2 | Add property tests: no zero/mean/half-minimum target imputation reaches dataset cells; tier I rows cannot be in test/calibration roles; E5-E7 excluded from TB-V0. | A 2-3 / H 0 | any | — | SHOULD | — |
| T7-C01-R4 | After signature, copy THR-35P-01..43 into registry/preregistered_thresholds_v1.csv (Step 01.6) and freeze preregistration_v1.md + sha256; orchestrator-only edit. | A 1-2 / H 0 | any | T7-C01-R1 | SHOULD | WRITING |
| T7-C02-R1 | Write molecule split auditor: InChIKey full + 14-char connectivity overlap check, tau881 cluster splits with label-free tau_cluster (99th pct over 20,000 seeded pairs … | A 8-12 / H 0 | any | signature not needed for code on synthetic fixtures (THR-35P-02) | SHOULD | — |
| T7-C03-R1 | Write 35a scoring (no-rdkit arm): CACTVS-881 decode unit test (222 hex = 881 bits MSB-first + 7 pad), E0 identity, E1 Tanimoto, six PubChem descriptors, label prior, … | A 14-22 / H 0 | any | T7-C02-R1 | SHOULD | — |
| T7-C05-R1 | Write x_ij builder producing ingredient_profile_xij_v1 and ingredient_profile_coverage_v1 (git-ignored features/step35/) with tier, value-or-UNKNOWN, unit, basis, … | A 6-10 / H 0 | any | T7-C02 | SHOULD | ANALYSIS |
| T7-C05-R3 | BAN-35-1 enforcement: static check that no arm, comparator or tie-breaker reads KGE ING_CO_OCCURS or any FlavorGraph/Recipe1M-derived edge/embedding (57,496 lines); … | A 3-5 / H 0 | any | T7-C05-R1 | SHOULD | — |
| T7-C06-R1 | Implement ingredient E0/E1 metrics, null percentile with B >= max(1000, ceil(20m/q)) (THR-35P-37), cardinality slope, dropout and shuffle controls, matched-coverage … | A 12-18 / H 0 | any | T7-C05-R1 | SHOULD | — |
| T7-C12-R2 | Build 35c task harness: masked-ingredient recovery (Recall@K, MRR, nDCG), partial-recipe completion, size-matched evaluation, frequency panel (SSOT §191.7 seven arms), … | A 16-24 / H 0 | mac | T7-C02; T7-C04-R3 for LightGBM | SHOULD | — |
| T7-C14-R1 | Implement remaining cuisine pieces: Curveball-calibrated Z / MX null path, E (era/source) null, macro-F1 classifier with minimum class support and source-identity … | A 14-22 / H 0 | any | T7-C02-R2 | SHOULD | — |
| T7-C16-R2 | Generate registry/similarity_registry_v2.csv and registry/representation_registry_v1.csv from the 21 v1 rows + notions, run lint, add BAN-35-1 and G35-SEP checks. | A 6-10 / H 0 | any | T7-C16-R1 | SHOULD | WRITING |
| T7-C19-R1 | Build one audit module producing G35-0/COV/CIRC/NULL/SEP verdict JSON per run with negative results kept visible (law 8). | A 8-12 / H 0 | any | T7-C02; T7-C06-R1; T7-C12-R2 | SHOULD | — |
| T7-C23-R1 | Create representation registry files and the output manifest writer (dataset/preprocessing/split versions, seed 20261104, code commit, sha256) used by every Step 35 run; … | A 4-6 / H 0 | any | T7-C16-R2 | SHOULD | WRITING |
| T8-C07-R1 | Decide how packets present CONFLICTING evidence (range + conflict flag) and add a small conflict test set from EVD strata | A 3-4 / H 0.5 | any | T8-C20-R1 | SHOULD | DECISION |
| T8-C08-R1 | Wire first SIMULATE (sim_aa_1 vitamin C) into the cascade as B6 only as a RESEARCH_ONLY rung after the fit freeze and the descriptive SIM-VAL report exist; otherwise … | A 3-5 / H 0 | any | Step 10 verification; Step 26/27 fit + SIM-VAL | SHOULD | DECISION |
| T8-C15-R3 | Pin Ollama model digest/version and prompt hash in the run record (§244.5) | A 0.5 / H 0 | any | — | SHOULD | — |
| T8-C17-R1 | Create prompt_registry (prompt sha, model digest) + claim_ledger schema for D5 answers; record versions per experiment | A 2-3 / H 0 | any | — | SHOULD | WRITING |
| T8-C18-R2 | Deploy hosted demo with template-only (no key) fallback; health check; DEMO_ONLY/NON_CITABLE banner | A 3-5 / H 0.5 | any | T8-C18-R1 | SHOULD | — |
| T9-C06-R1 | Write a §238 conformance table: each SSOT field -> schema property -> populated? (counts only) | A 2-3 / H 0 | any | — | SHOULD | ANALYSIS, WRITING |
| T9-C06-R2 | Decide: materialise a counts-only CLM (claim ledger) for demo answers or declare it runtime-only for the talk | A 2-4 / H 0.5 | mac | M4 (T-other) | SHOULD | DECISION |
| T9-C11-R1 | Back-fill EXP rows (or a registry/experiments_S171_S175.csv) for M1..M9 runs using the SSOT §257A.20 fields | A 2-3 / H 0 | any | compute_runs_v1.csv | SHOULD | WRITING |
| T9-C11-R2 | Complete missing start/end times and output sha256 in run log (orchestrator edits CSV); require new S176 runs to follow header | A 0.5-1 / H 0 | any | — | SHOULD | — |
| T9-C12-R2 | Add D4 metrics to prereg as descriptive: condition-compatible Recall@K on P blocks and risk-coverage curve of B7 abstention (ordinal score; no ECE/Brier unless a … | A 3-5 / H 0 | mac | D5 freeze | SHOULD | ANALYSIS |
| T9-C18-R1 | Compute D4 descriptive metrics on frozen D5 benchmark: router branch accuracy, compatible Recall@K, abstention precision/recall, risk-coverage and selective risk at … | A 3-4 / H 0 | mac | T9-C17-R1 | SHOULD | ANALYSIS |
| T9-C20-R2 | Figures: architecture (SSOT fig1), data tier/provenance, state-graph example, router route histogram, risk-coverage, ladder/ablation, decision register | A 4-6 / H 0 | mac | T9-C18-R1 | SHOULD | WRITING |
| T9-C21-R2 | Recorded demo fallback video/screens if hosting or VPN fails | A 1-2 / H 0.5 | mac | T9-C22 | SHOULD | WRITING |
| T9-C22-R2 | Scenario script: pick >=5 of the 8 SSOT scenarios feasible with real data; each labelled with evidence class | A 3-4 / H 0.5 | mac | M4 | SHOULD | WRITING |
| T9-C32-R1 | Number-class lint for deck/report: every number tagged EVD(E3-unverified/COND-unaudited) / TEXT_STATED / SCENARIO/ASSUMED_DEFAULT / MODEL_DERIVED/NON_CITABLE / … | A 2 / H 0.5 (exceptions list, 22-23 Nov) | any | T9-C20-R1 | SHOULD | WRITING |
| T0-C03-R2 | Build Step 03.3 clock registry and state_representation_contract_v1_1 (additive); add physical and history SVARs (moisture, a_w, thermal dose, time since disruption, … | A 4-6 / H 1 (H4 approval) | any | Step 03 H4 approval | COULD | WRITING, DECISION |
| T2-C10-R3 | Ingest human decisions into EVD verification status (new version lines, tier stays E3 unless dual-verified) via orchestrator | A 1-2 / H 0-0 | any | T2-C10-R1; T2-C14 | COULD | — |
| T2-C15-R3 | SPLIT schema v1.1 (add lineage-component, duplicate-group, lab, condition-OOD, matrix-OOD, platform, calibration strategies) and SPLIT.jsonl for 15a diagnostics | A 4-8 / H 0.5 | any | T2-C06 | COULD | — |
| T3-C01-R3 | Representability check of the 20 hard-case prompts (17 synthetic + SSOT §237.5 list) against the v1.1 schemas | A 3-5 / H 0 | any | T3-C01-R1 | COULD | ANALYSIS |
| T3-C03-R4 | Implement §234.7 vocabulary proposal states + §234.8 growth control as a registry column and a validator | A 3-5 / H 0 | any | — | COULD | — |
| T3-C22-R3 | Solute load (g salt, g sugar per g water) and water-activity estimate as MODEL_DERIVED intervals, only where masses are known | A 4-6 / H 0 | any | T3-C22-R1 | COULD | — |
| T4-C04-R2 | Extend binder to bind lid, pressure (pressure-cooker), start mode, product vs medium temperature and water:food ratio where stated (Step 26 EVT fields) | A 6-10 / H 0 | any | T4-C20 | COULD | — |
| T4-C09-R2 | If built: two-zone surface/drying-front driver giving time-to-surface-dry and surface temperature bracket, flagged QUALITATIVE_ONLY | A 8-14 / H 1 | any | T4-C09-R1; T4-C08-R1 | COULD | ANALYSIS |
| T4-C10-R2 | Wire Choi-Okos into Layer 2 where lot composition is known (water, fat, protein fractions), otherwise keep defaults | A 4-6 / H 0 | any | lot-state composition (T-lot topic); T4-C10-R1 | COULD | — |
| T4-C13-R1 | Build driver + scenario defaults + Layer 1 binding for SEPARATION family and unit tests | A 6-12 / H 0.5 | any | T4-C11-R2; T4-C06-R3 | COULD | ANALYSIS |
| T4-C16-R1 | Build driver + scenario defaults + Layer 1 binding for MECHANICAL_CUT family and unit tests | A 6-12 / H 0.5 | any | T4-C11-R2; T4-C06-R3 | COULD | ANALYSIS |
| T4-C18-R1 | Build driver + scenario defaults + Layer 1 binding for RESTING family and unit tests | A 6-12 / H 0.5 | any | T4-C11-R2; T4-C06-R3 | COULD | ANALYSIS |
| T5-C03-R1 | Freeze vocabularies (drop _DRAFT suffix) after H4; add analyte-form token registry; map route enum to §214.30 evidence-class labels in a documented table. | A 3-5 / H 1 | any | T5-C01-R4; T5-C01-R5 | COULD | DECISION, WRITING |
| T5-C07-R4 | Build standalone param_compat retrieval (categorical axis match vector, NO_COMPATIBLE_SET with reasons, ensemble/CONFLICT, domain location) and a >=60-query locked … | A 10-16 / H 4-6 Kush + 3-5 Parv label | any | T5-C07-R3 | COULD | ANALYSIS |
| T5-C18-R1 | I0 finite counterfactual comparison table over existing DIRECT/EVD retention (same ingredient, different process), with evidence class labels and abstention; demo only. | A 4-6 / H 0.5 | any | T5-C05-R2 | COULD | ANALYSIS |
| T7-C02-R2 | Implement cuisine split families S-cui-src / S-cui-hold (cuisine-level) and source-stratified recipe partitions (lowest-recipe_id stratum rule THR-35P-42), plus … | A 6-10 / H 0 | any | T7-C14; T7-C13 | COULD | — |
| T7-C04-R2 | Implement E2/E3 rung module (Morgan r0-3 bit/count 2048 and 4096 sensitivity, FCFP, MACCS, atom-pair, RDKit2D standardised, Murcko scaffold split, Butina clusters, … | A 16-24 / H 0 | mac | T7-C04-R1; T7-C03-R1 | COULD | — |
| T7-C09-R1 | Implement NUTRITIONAL similarity (cosine/Mahalanobis on stated basis, masked) once >= N crosswalks are human-verified; basis checks and food-group stratification. | A 6-10 / H 0 | any | ING->FDC crosswalk (other topic) | COULD | ANALYSIS |
| T7-C11-R1 | Define explicit per-lot-step feature vector from lot state + Layer-1/Layer-2 drivers (masked UNKNOWN, Layer 2 tagged ASSUMED_DEFAULT), with similarity and kNN/completion … | A 10-16 / H 1 | vinayak | lot-state layer (other topic); T7-C01-R1 | COULD | DECISION |
| T7-C13-R3 | Identity baseline ladder on labelled pairs: title-only, ingredient Jaccard, +quantity, +role, +process (Levenshtein/DTW/graph edit), then learned comparator; … | A 12-20 / H 0 | any | T7-C13-R2; Steps 16-18 event outputs | COULD | ANALYSIS |
| T7-C17-R1 | Implement process-bag Jaccard and normalised Levenshtein over the canonical event sequence; step-count confound control; report extraction-error sensitivity against the … | A 10-16 / H 0 | any | P1b gold (human nonce); Steps 17-18 outputs | COULD | ANALYSIS |
| T8-C02-R1 | Build METADATA handler: exact EVD/USDA SR lookup (public-domain) returning cited values or UNKNOWN | A 3-5 / H 0 | any | ING->SR crosswalk (lot-state topic) | COULD | — |
| T8-C05-R1 | Constraint-sensitivity robustness mini-test (oven vs pan only) as unit/property tests, no benchmark claim | A 1-2 / H 0 | any | — | COULD | — |
| T8-C06-R3 | Index literature passages/PARAM rows once verified (Step 10 rows) into retriever | A 3-5 / H 0 | any | Step 10 verification (human) | COULD | — |
| T8-C14-R1 | Minimal ASK evaluation: ASK-when-missing-slot-flips-route vs NeverAsk vs AskEverything on the X/vague block (descriptive) | A 3-4 / H 0 | any | T8-C20-R3 | COULD | ANALYSIS |
| T8-C18-R3 | Resume demo polish after H1/H3 results (show lot state/L2 labels, examples with DIRECT evidence) | A 3-4 / H 0.5 | any | T8-C21-R2 | COULD | — |
| T8-C21-R4 | Build B3 (structured metadata RAG) rung | A 2-3 / H 0 | any | — | COULD | — |
| T8-C23-R1 | Unit-invariance + paraphrase invariance mini-suite for the RAG (C<->F, kg<->g) | A 3-4 / H 0 | any | T8-C20-R3 | COULD | ANALYSIS |
| T9-C01-R2 | Materialise missing Step 01/04 v1.1 registries (authority map v1.1, namespace registry) or record that 04_9_min doc is the accepted substitute | A 1-2 / H 0.25 | any | T9-C01-R1 | COULD | WRITING |
| T9-C05-R3 | Fix manifest DS-006 replicate_information and add v1.1 columns (UNKNOWN allowed) - append-only new file | A 1 / H 0 | any | — | COULD | — |
| T9-C19-R2 | Optional: 5 hand-written feasibility/constraint demo cases using existing decision modules (no hypothesis test) | A 4-6 / H 0.5 | mac | M6 | COULD | — |

### 3.2 CPU compute (host runs) (63)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T2-C05-R3 | Score with tools/step07ar_agreement.py; verify freeze (step07hr_freeze.py --verify); write result JSON + diagnostics (kappa, PABAK, per-field, bootstrap CI) | A 0.5-1 / H 0-0 | any | T2-C05-R2 | MUST | ANALYSIS |
| T2-C15-R1 | Build the dataset-card generator and publish counts-only card for the 17,978 ACTIVE E3 rows (all §203.9 outputs, COND_UNAUDITED / BOOTSTRAP_UNVERIFIED tags) | A 8-12 total / H 1-2 review | manjot | T2-C01; T2-C04; T2-C06 | MUST | CODE, ANALYSIS |
| T3-C03-R2 | Coverage census: fraction of Food.com / Wikibooks / TASTEset ingredient mentions (NER FOOD spans and Rung A links) that hit ING/ALIAS, by mention frequency, counts-only | A 3-5 / H 0 | manjot | T3-C09-R1 | MUST | ANALYSIS |
| T4-C11-R1 | Census of events per non-heat family across the full corpus (counts, how many state time/T/medium/size) to size the work and rank families by volume | A 2-4 / H 0 | vinayak | T4-C01-R1 | MUST | ANALYSIS |
| T5-C05-R1 | Install hypothesis in an env where installs are allowed (Mac or vinayak) and run the >=10^4 randomised property test 'UNKNOWN/NOT_APPLICABLE never reaches SIMULATE' … | A 0.5 / H 0 | mac | T9-C25-R5 | MUST | CODE |
| T6-C03-R3 | Run 29-diag twice on the Mac (CPU, minutes) and verify byte-identical outputs (G15-R). | A 0.5-1.5 / H 0 | mac | T6-C03-R1; T6-C03-R2 | MUST | — |
| T8-C06-R1 | Run retrieval metrics (Recall@K, MRR, condition-compatible Recall@K, source-disjoint split) on frozen D5 P/C questions as the D4 real evaluation | A 2-4 / H 0 | manjot | T8-C20-R3 | MUST | ANALYSIS |
| T8-C22-R1 | Execute H3 analysis on frozen P/C blocks; decision-mode F1; handle zero-claim denominators | A 3-4 / H 0 | manjot | T8-C21-R1 | MUST | ANALYSIS |
| T9-C09-R2 | Leakage audit: D5 S-block recipes vs NER/linker/gold training splits and vs Rung A dev sets; P/C cells vs EVD rows used in DEL-2 / retrieval silver | A 2-3 / H 0 | manjot | D5 draft | MUST | ANALYSIS |
| T2-C01-R2 | Confirm EVD export v2 (08a.7) builder output is regenerated and byte-reproducible after the last ledger state, and record hash in compute_runs | A 0.5-1 / H 0-0 | any | T2-C06 | SHOULD | ANALYSIS |
| T2-C07-R2 | Register the AA pilot PDFs (7 fetched + 5 after browser download) and DOIs through register_document into scratch DOC library and run propose_edges to confirm no shared … | A 1-2 / H 0-0 | mac | T2-C09-R2 | SHOULD | ANALYSIS |
| T2-C13-R1 | Counts-only coverage statement for the talk: EVD pair/cell coverage against corpus demand, per process family, with the 07.A-unaudited tag | A 4-8 / H 0.5 | manjot | T2-C01; T2-C17 | SHOULD | ANALYSIS |
| T2-C15-R4 | Reproducibility record: seeds, versions, hashes, splits, run rows for every evidence-plane run (G15-R) | A 2-3 / H 0-0 | any | T2-C15-R1 | SHOULD | WRITING |
| T3-C04-R1 | Deterministic scored lexical matcher ING -> SR Legacy (7,793 foods), AI-drafted, with confidence and method fields; counts-only report | A 6-10 / H 0 | manjot | T3-C03-R2 | SHOULD | CODE |
| T3-C05-R1 | Verb-coverage census of Rung A on Food.com + Gutenberg + Wikibooks steps (share of ACTION events mapped to PROC; top unmapped verbs, counts-only) | A 2-3 / H 0 | manjot | — | SHOULD | ANALYSIS |
| T3-C07-R1 | Implement SP-002 pre-normalisation in parse_quantity_v2 (versioned rc2 result beside S161), re-run grounding on non-BBC families, report before/after counts | A 3-5 code + 1-2 run (non-BBC; … / H 0.5 review | manjot | — | SHOULD | CODE |
| T3-C08-R2 | Re-run rc2 grounding with ingredient links + POR supplied; report Q-level distribution by family | A 2-3 / H 0 | manjot | T3-C08-R1; T3-C07-R1 | SHOULD | ANALYSIS |
| T3-C09-R1 | NER vs Rung A mention agreement diagnostic (span overlap, FOOD span in lexicon-missed lines), counts-only, labelled DIAGNOSTIC not gold | A 4-6 / H 0 | manjot | spans on vinayak copied or run there | SHOULD | ANALYSIS |
| T3-C12-R1 | Replay-invariant property tests at corpus scale (order, consumption, split fractions sum, no resurrection of discarded lots) with counts-only violation report | A 4-6 / H 0 | manjot | — | SHOULD | CODE |
| T3-C13-R1 | Measure the fraction of recipes with a fully known or interval-bounded mass graph after C07/C08 fixes (counts-only) | A 2-3 / H 0 | manjot | T3-C08-R2 | SHOULD | ANALYSIS |
| T3-C22-R1 | Step 1-2 slice: lot members + presence-only composition from ING->SR match; mass interval only where grams are known (UNKNOWN otherwise); record per lot-step with … | A 10-16 / H 0 | manjot | T3-C04-R1; T3-C08-R1; T3-C12-R3 | SHOULD | CODE |
| T4-C03-R1 | Add endpoint-cue extractor output (stopping criterion field) and a leakage unit test plus corpus count of endpoint cues per heat event | A 4-6 / H 0 | vinayak | T4-C04 | SHOULD | CODE |
| T4-C11-R3 | Full-corpus non-heat L1 run on non-BBC families, BBC on Mac, counts-only reports and run log rows | A 2-4 / H 0 | vinayak | T4-C11-R2 | SHOULD | — |
| T4-C12-R2 | Full non-BBC corpus run and counts-only report for COOLING family with run-log rows | A 1-2 / H 0 | vinayak | T4-C12-R1 | SHOULD | — |
| T4-C14-R2 | Full non-BBC corpus run and counts-only report for FERMENT_LEAVEN family with run-log rows | A 1-2 / H 0 | vinayak | T4-C14-R1 | SHOULD | — |
| T4-C20-R2 | Reproduce FOODCOM L1/L2 on a second host (manjot, 16-32 workers) and compare counts and hashes | A 3-5 (job hours ~4-8) / H 0 | manjot | code sync | SHOULD | ANALYSIS |
| T4-C21-R1 | Re-run 26g census with Layer 1 bindings supplying T, t, medium and size so MISSING_* reasons drop for bound events; keep SIMULATE 0 until PARAM human verified | A 4-6 / H 0 | vinayak | T4-C04; M3 gate for any SIMULATE | SHOULD | CODE |
| T5-C02-R3 | Full-corpus run of the screen on non-BBC families (Food.com 522,517; Gutenberg 73,955; Wikibooks 3,676; TASTESET 700) and BBC on Mac only. | A 1-2 (compute 1-3 h wall) / H 0 | vinayak | T5-C02-R2 | SHOULD | — |
| T5-C05-R2 | Router re-run on the full non-BBC corpus after lot state + mechanism screen + PARAM exist (targets beyond vitamin C where EVD has rows), counts-only; BBC on Mac. | A 2-4 / H 0 | vinayak | T5-C02-R2; T5-C10-R6; T5-C07-R3 | SHOULD | — |
| T5-C05-R3 | Extend router targets from vitamin C to every SVAR with EVD rows (folate, thiamin, carotene etc.) for the DIRECT/INTERPOLATE paths; keep SIMULATE only for AA. | A 4-8 / H 0 | any | T5-C05-R2 | SHOULD | CODE |
| T5-C06-R2 | If 07.A PASS and 15b frozen: run 23b on real COND rows and report. | A 3-5 / H 0.5 | any | T5-C06-R1; 15b freeze | SHOULD | ANALYSIS |
| T5-C12-R1 | Run the pre-registered G26-VER suite and the >=200-dataset recovery grid; write verification_report_v1.md with pass/fail per criterion. | A 3-5 (compute ~1-2 h CPU) / H 0.5 | manjot | T5-C11-R1 | SHOULD | ANALYSIS |
| T6-C02-R3 | Re-run DEL-2 ladder with paired tests (delta = baseline loss - challenger loss, cluster bootstrap) so every claimed gain over D0 on cold splits has a paired CI; reuses … | A 3-5 / H 0 | mac | T6-C03; T6-C06-R1 | SHOULD | CODE, ANALYSIS |
| T6-C08-R1 | Build propensity model with available covariates (food frequency in recipe corpus as popularity proxy, process family, target class, source), clipping sweep, positivity … | A 5-8 / H 0 | any | T6-C01-R1 | SHOULD | CODE, ANALYSIS |
| T7-C02-R3 | Run splits on real data and write sha256 manifests (registry/splits/step35_split_hash_manifest_v1.json, reports/step35/output_hash_manifest_v1.json); per-item outputs … | A 1-2 / H 0 | mac | T7-C01-R1; T7-C02-R1 | SHOULD | ANALYSIS |
| T7-C12-R3 | After signature only: run R0/R2 descriptive and primary PE-35c on real recipes incl. link-coverage floor with/without masking; 1,000-recipe sample before full run; BBC … | A 3-6 / H 0 | mac | T7-C01-R1; T7-C12-R2; recipe_ingredient_mentions parquet | SHOULD | ANALYSIS |
| T8-C21-R2 | Cheap ablations: remove state conditioning, evidence compat, claim enforcement, OOD gate one at a time on frozen set | A 3-5 / H 0 | manjot | T8-C21-R1 | SHOULD | CODE, ANALYSIS |
| T9-C24-R2 | Rerun-from-registry check: pick 3 run ids (router census, binding census Wikibooks, H1/H3) and reproduce on manjot; compare sha256 | A 2-3 / H 0 | manjot | compute log | SHOULD | ANALYSIS |
| T0-C15-R1 | Implement classical layer on toy data from §80/§130 (unit tests) then on FlavorGraph/FooDB-derived profiles (licence internal-only): n_ij, N_s(R), N_s(C), 4 nulls, Delta … | A 16-24 / H 1 (review) | manjot | Step 35 signature; MOL ledger (1,726 molecules) | COULD | CODE |
| T2-C11-R1 | Stage-only use of R2 yields and SR retention factors for the lot-state mass-balance (no ledger append): counts-only report | A 2-4 / H 0-0 | manjot | T2-C11 staging | COULD | ANALYSIS |
| T2-C17-R2 | Re-run router census with updated links to refresh the coverage numbers | A 1-3 / H 0-0 | vinayak | T2-C17-R1 | COULD | — |
| T3-C06-R1 | Reconcile TOOL ledger (297) vs registry (119); coverage census on Food.com steps | A 1-2 / H 0 | manjot | — | COULD | ANALYSIS |
| T3-C07-R2 | BBC A1 re-run of the SP-002-fixed grounding on the Mac (BBC has only 188 U+2044 lines; low urgency) | A 0.5 / H 0 | mac | T3-C07-R1 | COULD | — |
| T3-C08-R4 | Empirical portion distributions per ING from stated-mass lines (§235.8) for sanity cross-check of SR portions | A 3-4 / H 0 | manjot | T3-C07-R1 | COULD | ANALYSIS |
| T3-C09-R2 | MENTION ledger DRAFT as a git-ignored derived table (mention_id, line_id, span offsets, label, model hash, confidence) plus a counts-only committed schema and summary | A 3-5 / H 0 | vinayak | T3-C01-R1 | COULD | CODE |
| T3-C11-R4 | Re-run Rung A after SP-002 + vocab fixes with a version bump on non-BBC families on manjot (CPU 32 workers) and BBC on Mac | A 1-2 + Mac 0.5 / H 0 | manjot | T3-C07-R1 | COULD | — |
| T3-C19-R1 | Package the existing Rung A + replay outputs as a documented T0 weak corpus (counts-only manifest, per-recipe file in git-ignored data/derived) with release tier labels | A 4-6 / H 0 | manjot | T3-C11-R4 | COULD | CODE |
| T3-C22-R5 | Non-heat process families feeding the same lot record (cool, drain, marinate/brine, dry, cut, mix, rest, store) as TEXT_STATED/SCENARIO records | A 20-30 / H 0 | manjot | T3-C22-R1; process coverage plan (topic physical state, note T5/T6) | COULD | CODE |
| T3-C22-R6 | Full-corpus lot-state run on manjot (non-BBC) with nice -n 10, 32 workers; BBC on the Mac; counts-only reports; outputs in data/derived | A 3-5 (run) + Mac 1 / H 0 | manjot | T3-C22-R1 | COULD | — |
| T4-C05-R2 | Reduce UNKNOWN: add default durations per PROC where text lacks time (cited quantile source) and more media defaults, keeping UNKNOWN-first rule | A 5-8 / H 0 | vinayak | T4-C06 | COULD | CODE |
| T4-C13-R2 | Full non-BBC corpus run and counts-only report for SEPARATION family with run-log rows | A 1-2 / H 0 | vinayak | T4-C13-R1 | COULD | — |
| T4-C16-R2 | Full non-BBC corpus run and counts-only report for MECHANICAL_CUT family with run-log rows | A 1-2 / H 0 | vinayak | T4-C16-R1 | COULD | — |
| T4-C18-R2 | Full non-BBC corpus run and counts-only report for RESTING family with run-log rows | A 1-2 / H 0 | vinayak | T4-C18-R1 | COULD | — |
| T4-C22-R2 | 31.0 cooking-vs-storage census of lineage components with within-study condition variation (data present in EVD/COND) | A 3-5 / H 0 | manjot | COND ledger; Step 08 lineage ids | COULD | ANALYSIS |
| T5-C11-R5 | SIM ledger writer with firewall tests and SIMLINK_v1 link table for the corpus (additive, counts-only, SIM plane). | A 4-6 / H 0 | vinayak | T5-C11-R4 | COULD | CODE |
| T6-C15-R1 | 34a.0 circularity check (are USDA multi-step factors derived multiplicatively?) and, if clean, run 34a on USDA/PE with the best one-step rung from the diag ladder as a … | A 3-6 / H 0 | any | T6-C03-R3 | COULD | ANALYSIS, CODE |
| T7-C03-R2 | After the 35.0 v2 signature only: run 35a no-rdkit arm on the 603 taste-labelled molecules and publish molecule_leaderboard_v1 with wide intervals and NEED_DATA classes … | A 2-4 / H 0 | mac | T7-C01-R1; T7-C03-R1; T7-C04-R1 | COULD | ANALYSIS |
| T7-C06-R2 | Run 35b PRESENCE arms on IMAP (descriptive then primary endpoint PE-35b incl. cold-start PE-35b-cold) and report slope/CI per arm. | A 2-4 / H 0 | any | T7-C01-R1; T7-C06-R1 | COULD | ANALYSIS |
| T7-C07-R1 | Implement kernel-mean, symmetrised best-match, top-k mean on 881-bit Tanimoto (no-rdkit variant now, ECFP variant after C04) and descriptor-mean embedding cosine; OT … | A 8-14 / H 0 | mac | T7-C06-R1; T7-C04-R2 | COULD | CODE |
| T7-C12-R4 | R3 quantity-weighted mass-share arm on the quantity-bearing subset (Step 16 rc2 Q0 mass lines) once coverage is audited. | A 3-5 / H 0 | any | Step 16 rc2 outputs | COULD | ANALYSIS |
| T7-C14-R2 | After signature only: run C0-C2 descriptive on labelled recipes and pre-registered classes (>=100 recipes, >=2 source families); report class table and COVERAGE/NULL … | A 3-5 / H 0 | mac | T7-C01-R1; T7-C15-R1; T7-C14-R1 | COULD | ANALYSIS |
| T7-C16-R3 | Run separation tests (Spearman rank agreement and kNN-overlap@k between notions; 'structure -> taste' STRUCTURAL x SENSORY test) on whatever data exist. | A 4-8 / H 0 | any | T7-C01-R1; T7-C03-R2; T7-C06-R2 | COULD | ANALYSIS |
| T7-C25-R1 | One bounded chain only (AH12): per-source rank-frequency with alternative-model comparison + M0 null lattice on Food.com web-era descriptors; label 'descriptive, not … | A 16-26 / H 0 | any | T7-C24-R2; T7-C14-R1 | COULD | CODE, ANALYSIS |

### 3.3 GPU compute (6)

GPU work for 25 Nov is only the D5 ladder and H1 runs on vinayak (Ollama, qwen2.5:7b). manjot agents use no GPU (shared-server rule).

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T8-C15-R1 | Run B0/B1/B2/B4/B5/B7/B5T on frozen D5 benchmark with qwen2.5:7b (temp 0, seed fixed), log run in compute_runs_v1.csv | A 3-5 / H 0 | vinayak | T8-C20-R3; VPN to vinayak; Ollama up | MUST | ANALYSIS |
| T8-C21-R1 | Execute H1 runs on frozen S1/S2 (B0,B1,B2,B4 + B5/B7), compute McNemar/Newcombe | A 2-3 / H 0 | vinayak | T8-C20-R3; T8-C15-R1 | MUST | ANALYSIS |
| T2-C08-R2 | Prompt/model registry and Extractor B: run a second, different-family local model (Ollama on vinayak) blind on the AA CAL papers and diff field by field | A 4-8 / H 0-0 | vinayak | T2-C09-R3 | COULD | ANALYSIS |
| T3-C09-R3 | Tag BBC ingredient lines on the Mac (CPU/MPS) for completeness, counts-only | A 1-2 / H 0 | mac | — | COULD | CPU_COMPUTE |
| T3-C10-R1 | Decision and run: link unique normalised FOOD spans (deduped) with the frozen CD-L2 or BGE top-1 for lines Rung A failed to link; output as MODEL_DERIVED candidates with … | A 6-10 / H 0.5 | vinayak | T3-C09-R1; T3-C03-R2 | COULD | DECISION, CODE |
| T8-C15-R2 | Sensitivity run with qwen2.5:32b on same questions (robustness only) | A 1-2 / H 0 | vinayak | T8-C15-R1 | COULD | — |

### 3.4 Training / fitting (4)

No neural training is planned before 25 Nov. The only fit is the AA pilot Model A (T5-C10-R5) and its calibration (T5-C11-R3).

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T5-C10-R5 | Fit Model A on verified SIM-CAL rows, run Model B sensitivity, freeze fit JSON with sha256 and code hash BEFORE any SIM-VAL text is opened; ensure report says fit spec … | A 3-5 / H 0.5 | any | T5-C10-R4 | MUST | CPU_COMPUTE, ANALYSIS |
| T5-C11-R3 | Calibrate sim_aa_1 with frozen Model A PARAM (26d on SIM-CAL only), produce calibration report + identifiability report on real data; issue SIMM-AA-1 card with … | A 6-10 / H 1 | any | T5-C10-R5; T5-C10-R6 | MUST | CPU_COMPUTE, ANALYSIS, CODE |
| T5-C11-R6 | Recipe simulability census v1 re-run with calibrated sim_aa_1 (counts only). | A 2-3 / H 0 | vinayak | T5-C11-R4 | SHOULD | CPU_COMPUTE, ANALYSIS |
| T5-C15-R1 | After PARAM exist: fit hierarchical Arrhenius, run leave-one-paper-out condition-OOD against best non-kinetic baseline (G15-5 test) only if >=2 matrices; else report … | A 6-10 / H 0.5 | manjot | T5-C10-R5 | COULD | CODE, ANALYSIS |

### 3.5 Analysis (52)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T2-C06-R2 | Slide-level honest statement of lineage: counts, G08-3 FAIL, publication-component CV label, one-line implication for every H2 claim | A 1-2 / H 0.5 | any | T2-C06 reports | MUST | WRITING |
| T2-C09-R3 | AI extraction of CAL rows from newly downloaded SIM-CAL papers with spans (SIM-VAL papers stay unopened until fit freeze) | A 3-5 / H 0-0 | mac | T2-C09-R2 | MUST | WRITING |
| T2-C21-R1 | Write the D1 section and figures: sources, counts by tier/source/target, coverage (T/t/pH/a_w), lineage label, verified rows n/40, what is not claimed | A 4-8 / H 1-2 review | any | T2-C15-R1; T2-C10-R1; T2-C06-R2 | MUST | WRITING |
| T4-C04-R1 | Write 'what the corpus can say' analysis: coverage by family, source and process, share with both t and T, ranges, gas-mark-only, per-family top unbound reasons, for the … | A 3-5 / H 1 | any | existing census JSONs | MUST | WRITING |
| T4-C25-R1 | Draft physical-layer slides/figures (coverage funnel, bracket spread, UNKNOWN reasons, non-heat families status) with wording audit against §141 | A 3-5 / H 1 each | any | T4-C04-R1; T4-C05-R1 | MUST | WRITING |
| T5-C12-R2 | Identifiability report for the AA pilot fit (profile CI for ln k_ref and Ea; practical-identifiability test). | A 2-3 / H 0.5 | any | T5-C10-R5 | MUST | — |
| T5-C21-R1 | Produce an honest G15 gate scorecard for T5 gates (G15-4,5,8,11,12,HYB,RXN,INV, partial 1,6,7,H,R) with file evidence and PASS/PARTIAL/NOT_MET/NEED_DATA, to feed report … | A 3-5 / H 1 | any | T5-C10-R5; T5-C12-R2 | MUST | WRITING |
| T6-C03-R4 | Write the four diag memos with every number labelled DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE and no words 'supported', 'beats', 'validated'; explain DEL-2 D7a == … | A 3-5 / H 0.5-1 review | any | T6-C19-R1; T6-C03-R1; T6-C03-R2 | MUST | WRITING |
| T8-C04-R2 | Report circularity caveat and an engine-vs-human-edited-gold agreement figure for S blocks | A 1 / H 0 | any | T8-C20-R2 | MUST | WRITING |
| T8-C10-R1 | Score C-block comparisons vs reviewed gold; report 'cannot separate' rate | A 1 / H 0 | any | T8-C20-R3 | MUST | — |
| T8-C13-R1 | Evaluate OOD gate on P3 (gold=ABSTAIN) vs P1/P2: abstain recall/false-abstain rate | A 1 / H 0 | any | T8-C20-R3 | MUST | — |
| T8-C16-R2 | Report enforcement cost: sentences removed, fallback rate, answer length/coverage per rung | A 1 / H 0 | any | T8-C15-R1 | MUST | — |
| T9-C12-R1 | Power/MDE note for H1/H3 (exact McNemar at n=30, discordance assumptions) added to prereg amendment BEFORE signature | A 1 / H 0 | any | T9-C08-R2 | MUST | WRITING |
| T9-C16-R1 | Report D3 as 'built + run, gold comparison limited to P1 (7 pairs, AI-drafted, human-accepted)' with intervals; add replay-consistency and merge/split property tests as … | A 2-3 / H 0 | any | — | MUST | WRITING |
| T9-C20-R1 | Final report and slides (one item): skeleton with placeholders 13 Nov, fill tables from committed JSON as each result lands, full draft 21 Nov, human edit 22-23 Nov, … | A 15-22 total / H 4-6 each | mac | T9-C17-R2; T9-C14-R4; T9-C13-R2 | MUST | WRITING |
| T9-C23-R2 | Re-score MPU table after M1-M6 outcomes (true numbers) | A 1 / H 0 | any | H1/H3 results | MUST | — |
| T9-C25-R1 | Aggregate compute ledger: remaining runs by host with agent-hours and wall-clock estimates (from all topics' inventories), VPN risk and disk budget | A 2 / H 0 | any | T1..T10 inventories | MUST | WRITING |
| T9-C26-R4 | Single human-time ledger + human-only items sheet: de-duplicated hours per person by task and week (approx. 16-20 h each over 9-16 Nov: signatures ~2, 07.A 3-4, AA … | A 1-2 / H 0.5 | any | T9-C26-R1 | MUST | WRITING |
| T0-C01-R2 | Write the 'SSOT v15 status block vs reality' delta table (what §128 says vs what repo evidence shows) for the report appendix. | A 2-3 / H 0 | any | handoff/PROGRESS_AUDIT_2026-11-07.md | SHOULD | WRITING |
| T0-C02-R1 | Targeted related-work re-search (state-tracking food RAG, evidence-gated abstention, process-conditioned food representations); verify each citation by opening the … | A 6-10 / H 1-2 (review) | any | OpenAlex access (Step 13) | SHOULD | WRITING |
| T0-C19-R1 | SSOT coverage map for sections no topic anchors: §121-§127/§80-§86/§159-§160 classical pairing; §152-§158, §161-§170 course ontology + midsem imports; §99-§102, … | A 3-5 / H 0.5 | any | T0-C01-R2 | SHOULD | WRITING |
| T2-C01-R1 | Field-by-field conformance table of the §203.2 process-event schema vs EVD export v1 (PRESENT / UNKNOWN-by-source / ABSENT with counts), so the D1 claim is exact | A 3-5 / H 0-0 | any | T2-C01 export v1 | SHOULD | WRITING |
| T2-C03-R3 | Reconcile SVAR ledger (ledgers/data/SVAR.jsonl 355 lines / 224 distinct ids; 354 CHEMICAL, 1 PHYSICAL) vs registry/state_variable_registry_v1.csv (254 rows) and correct … | A 1-2 / H 0 | any | — | SHOULD | WRITING |
| T2-C09-R7 | Record what the pilot is not: n, papers, lab groups UNKNOWN, no E4 promotion, DEL-1 0/40 unaffected; kinetic_series_availability for AA (and chlorophyll if time) as a … | A 2-4 / H 0.5 | any | T2-C09-R6 | SHOULD | WRITING |
| T2-C14-R1 | Seal integrity check before any 15a/29-diag read (reserved list hash vs commitment, access log) | A 0.5 / H 0-0 | mac | seed on Kush Mac | SHOULD | — |
| T2-C16-R1 | Run the 15b readiness checklist and publish an explicit NOT_FROZEN/ BLOCKED_BY list for the report (honest negative) | A 2-3 / H 0.5 | any | T2-C05; T2-C10; T2-C13 | SHOULD | WRITING |
| T3-C03-R1 | Reconcile ING counts (1,951 report vs 5,387 packet vs ledgers/data/ING.jsonl rows) and publish a counts-only vocab status table | A 1-2 / H 0 | manjot | — | SHOULD | — |
| T3-C07-R4 | Empirical measurement: share of Food.com lines whose quantity is a bare count vs whether NER UNIT/QUANTITY ratio agrees (confirm the unit-drop mechanism is source-level, … | A 1-2 / H 0 | manjot | T3-C09-R1 | SHOULD | — |
| T3-C17-R2 | Event-type and state-label confusion matrix of Rung A vs P1 gold, counts-only, for the slides | A 2-3 / H 0 | any | T3-C11-R1 | SHOULD | — |
| T4-C05-R1 | Sensitivity report: bracket width (INTENSE-GENTLE) per family, share of events where bracket spread changes a qualitative conclusion (e.g. core reaches 70 C), reasons … | A 2-4 / H 0 | any | existing L2 JSONs | SHOULD | — |
| T4-C26-R1 | Layer 1 binder precision audit, AI pass only: n=100 seeded bound heat events (seed 20261104, stratified by family, non-BBC families on manjot) checked against the text … | A 3-4 / H 0 (COULD: adjudicate 20 events after 16 … | manjot | T4-C04; T8-C20-R3 (D5 freeze 16 Nov) | SHOULD | — |
| T6-C11-R1 | D2-lite for the talk: assemble existing DEL-2 + 29-diag numbers into a one-page density, MNAR and cold-split negative-result summary, labelled DIAGNOSTIC and NOT a … | A 3-4 / H 0.5 | any | T6-C03-R4; T6-C01-R1 | SHOULD | WRITING |
| T7-C01-R5 | Verify on manjot (and vinayak) which bound inputs are present: ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet and gold_firewall are NOT visible in this … | A 0.5 / H 0 | any | — | SHOULD | — |
| T7-C22-R1 | Write decision records v1 for Level-12 and Level-13 stating per rung PROMOTED / FAILED / DATA-BLOCKED with evidence paths (expect mostly DATA-BLOCKED/BASELINE); include … | A 2-3 / H 1-2 (review) | any | T7-C01-R2; whatever explicit runs exist | SHOULD | WRITING |
| T8-C03-R1 | Measure slot extraction accuracy (ingredient/process/target) on the frozen D5 questions as a diagnostic | A 1-2 / H 0 | any | T8-C20-R3 | SHOULD | — |
| T9-C24-R1 | Write RELEASE_CARD.md (counts only) per §257A.16 for recipe base v1, EVD export, benchmark v1, physical L1/L2 layers, NER outputs | A 3-4 / H 0.5 | any | T9-C28 | SHOULD | WRITING |
| T9-C29-R1 | Generate G16 gate status table (14 gates: NOT_EVALUATED / FAIL / PARTIAL with path) and stop-rule check list for the report | A 2 / H 0.25 | any | — | SHOULD | WRITING |
| T9-C30-R1 | Produce DoD/checklist scorecard (17 + 21 items) with MET/PARTIAL/NOT_MET and evidence path; include in report appendix | A 2-3 / H 0.25 | any | T9-C17-R2 | SHOULD | WRITING |
| T0-C16-R1 | Map each §137 open question to a plan step or 'parked' in a one-page register (Q-P1 professor endpoint, Q-N2 licences, Q-RS1-13 extraction). | A 3-4 / H 0 | any | — | COULD | WRITING |
| T2-C05-R6 | Produce the card's diagnostics annex for v4 (PABAK, AC1, specific agreement, disagreement matrix) as DIAGNOSTIC_ONLY without re-labelling the verdict | A 1-2 / H 0-0 | any | step07_v4 files | COULD | — |
| T3-C10-R2 | Measure how much composition coverage (mention mass) linker adds over Rung A lexicon | A 2 / H 0 | manjot | T3-C10-R1 | COULD | — |
| T3-C12-R2 | G18 gate record: replay agreement with P1/P1b gold alive-entity and process-link metrics | A 2-3 / H 0 | any | T3-C11-R1; T3-C16 | COULD | WRITING |
| T5-C05-R6 | Deliver UNKNOWN census (G23.6) on DATA-EVIDENCE v1 to Step 14 in the agreed format (reformat existing census). | A 1-2 / H 0 | any | — | COULD | WRITING |
| T5-C19-R1 | Report R0/R1 rollout limits honestly in talk (no trust horizon); constraint-violation counters (negative conc, balance) reported for sim_aa_1 only. | A 2-3 / H 0 | any | T5-C12-R1 | COULD | WRITING |
| T6-C13-R3 | Kinetic census of Phenol-Explorer storage pseudo-series (reconcile 29 vs 8 definitions), as feasibility for KA ablation. | A 3-5 / H 0 | any | — | COULD | — |
| T7-C24-R2 | Audit dated-source coverage (Gutenberg, Wikibooks, Food.com submission dates) and write G13E-01/02 table with interval-censored dates; add nullable historical block spec … | A 6-10 / H 0 | any | T7-C24-R1 | COULD | WRITING |
| T8-C07-R2 | Hard-negative evaluation of compatibility (same food/different process rows) as ablation | A 1-2 / H 0 | any | T8-C6-R1 | COULD | — |
| T8-C11-R1 | Measure relevance-gate precision/recall on X controls + S/P blocks (diagnostic) | A 0.5 / H 0 | any | T8-C20-R3 | COULD | — |
| T8-C21-R3 | Oracle-state vs predicted-state cascade on S blocks using human-corrected gold state | A 2 / H 0 | any | T8-C20-R2 | COULD | — |
| T9-C11-R3 | Lightweight cost/time ledger: LLM tokens (H1/H3 Ollama calls), GPU hours, human review minutes per block (log from review sheets) | A 1-2 / H 0.5 | any | M5 | COULD | WRITING |
| T9-C24-R3 | Latency note for runtime RAG (query time of B5T/B7 in demo; cached assets listed) | A 1 / H 0 | mac | M6 | COULD | — |
| T9-C31-R1 | Build risk-control evidence table (20 risks) and RQ16 decision register for the 30 RQs (most NEED_DATA/OUT_OF_SCOPE) citing owning topic | A 3-4 / H 0.5 | any | T1..T10 inventories | COULD | WRITING |

### 3.6 Downloads / acquisition (13)

Licence rules: no BBC Good Food data on this server (D-003); Food.com is uploader-declared CC0 (unverified, LOCAL research use, source UNREGISTERED, H2 approval item); USDA SR Legacy/FNDDS/yields public domain; Gutenberg public domain; Wikibooks CC BY-SA. "H2" here is the **human licence/acquisition approval queue** (DECISIONS: "21 actions are isolated in the H2 queue"), not hypothesis H2. Agents never self-register keys with the user's email (T2-C12-R1). Third-party text never enters committed files. Paywalled handbooks (T4-C10-R1, T4-C14-R3) need library access; otherwise the values stay SOURCE_UNVERIFIED_AGENT_RECALLED with ranges.

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T2-C09-R2 | Browser-download the 5 PDFs that refuse scripted download (AAK-02,04,05,08,10) into data/raw/aa_pilot/ on the Mac; confirm licence on the publisher page | A 0 / H 0.5-1 | human | T2-C09-R1 | MUST | HUMAN_REVIEW |
| T3-C07-R3 | Decision: how Food.com no-unit lines are treated (presence-only composition; or find original data with units; or flagged imputation) | A 1 (sourcing check) / H 0.5-1 | human | — | MUST | DECISION |
| T0-C04-R1 | Source from opened handbooks (page + range) the <=8 scenario defaults (of the 27 rows in registry/scenario_defaults_v1.csv) used by the AA/steam/boil examples on slides; … | A 3-5 / H 2 total | human | Q2 | SHOULD | ANALYSIS, HUMAN_REVIEW |
| T2-C10-R2 | Library/proxy access for the 110 non-OA Phenol-Explorer papers (human permission or institutional login) | A 0 / H 1-3 | human | IIITD library | SHOULD | HUMAN_REVIEW |
| T3-C22-R2 | FDA pH registry (draft exists, lane L-PH): human-verify source status and parse, wire to the ING crosswalk, and record whether member pH enters Layer 2 defaults or stays … | A 4-6 / H 0 | manjot | T3-C22-R1; T3-C04-R1 | SHOULD | CODE |
| T4-C10-R1 | Verify Choi-Okos coefficients against the 1986 paper or Rahman handbook, record page cites | A 2-4 / H 0 | any | paper access | SHOULD | ANALYSIS |
| T4-C14-R3 | Source diffusion coefficients (salt, acid, sugar in meat/vegetable) as ranges from handbooks | A 3-5 / H 0 | any | — | SHOULD | ANALYSIS |
| T2-C12-R1 | H2 decisions and user-created keys (OpenAlex/Crossref email, NCBI key if used) for Europe PMC, OpenAlex, Unpaywall | A 0 / H 0.5-1 | human | es_1_2_h2_approval_queue.md #1,#3,#4 | COULD | DECISION |
| T4-C07-R2 | Arrhenius exposure integral Omega with representative Ea grid and temperature-trajectory input (needs literature Ea per target class, not tuned on test studies) | A 4-6 / H 1 | any | Step 24 Ea sources | COULD | CODE |
| T4-C08-R2 | Whole-item size defaults (potato, egg, chicken, joint) as ranges with source | A 3-5 / H 1 | any | T4-C06 | COULD | ANALYSIS |
| T5-C02-R1 | Build mechanism condition-window registry for ~14 screen mechanisms: window interval, matrix scope, gate type, source id (primary source opened) and range, otherwise … | A 10-18 / H 0 | any | T5-C01-R2 | COULD | WRITING, CODE |
| T5-C10-R7 | Find at least one extra AA source with cooking-water/leachate assay or water-immersion design so k_L and K_p are not UNKNOWN (optional). | A 3-6 / H 1-2 | any | T5-C10-R4 | COULD | ANALYSIS |
| T7-C04-R3 | Install LightGBM (and scikit-learn) in the Mac env (and optionally manjot/vinayak venv) as pinned dependency; log in compute_runs registry. | A 0.5 / H 0.5 | mac | T7-C04-R1 | COULD | — |

### 3.7 Human review (38)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T2-C05-R2 | Kush and Parv each independently label the 100-condition R1 packet (9 fields + overall), alone, blind, no external source | A 0 / H 3-4 each | human | T2-C05-R1 | MUST | — |
| T2-C05-R4 | Joint adjudication of disagreements, DECISIONS entry (counted by orchestrator), statistic never recomputed after adjudication | A 0.5 / H 0.5-1 each | human | T2-C05-R3 | MUST | DECISION |
| T2-C09-R4 | Kush and Parv each verify every CAL row (VERIFIED / CORRECTED / REJECTED) against the paper span, blind to the other | A 0 / H 3 each | human | T2-C09-R1 | MUST | — |
| T5-C10-R6 | Then extract and verify SIM-VAL rows (AAK-12/07/03/05) and compute descriptive prediction error and interval coverage (Step 27 pilot). | A 3-5 / H 1.5-2 each (4 papers) | any | T5-C10-R5 | MUST | ANALYSIS |
| T8-C16-R1 | Add citation precision/recall and a manual-verification sample (30 claims) to H3 reporting, so UCR is not self-graded only | A 2-3 / H 1-1.5 each | any | T8-C21-R1 | MUST | CODE |
| T8-C20-R2 | Kush and Parv independently review 100 questions (KEEP/EDIT/DROP), reconcile; agent assembles benchmark | A 1 / H 5-7 each (incl. S-gold re-derivation) | human | T8-C20-R1 | MUST | ANALYSIS |
| T9-C08-R4 | Add NEG rows for S171-S176 negatives (router DIRECT 0.754 %, D-074 R1 4/60, Food.com no-units, NER UNIT<<QUANTITY, SP-002 29.8 %, P1 HANDBOOK_REVISION_REQUIRED, scenario … | A 1-2 / H 0.5-1 | any | — | MUST | WRITING |
| T9-C20-R3 | Authors read and correct contributions section, confirm presentation date 25-26 Nov | A 0 / H 1 | human | — | MUST | — |
| T9-C26-R3 | Timed dry run of the talk on 24 Nov including the live-demo fallback, plus a one-page 'cannot claim' Q&A sheet drafted by the agent (H2 diagnostic only, 0 PARAM except … | A 1-2 (Q&A sheet) / H 1.5-2 each | human | T9-C21-R1 | MUST | WRITING |
| T0-C07-R1 | Build an annotated gate set (~100 queries incl. D5 X controls), measure precision/recall with false-negatives reported separately; no tuning on D5 test items. | A 3-4 / H 1-2 (labels) | any | D5 benchmark review | SHOULD | ANALYSIS, CODE |
| T0-C17-R1 | Kush supplies or confirms: professor endpoint access/terms status and a written copy of permission. | A 0.5 / H 0.5-1 | human | — | SHOULD | DECISION |
| T2-C10-R1 | Strip the AI suggestion columns and have Kush verify the 40 MAIN rows against the cited papers (Parv audits a predeclared sample; RESERVE 15 as replacements) | A 1-2 / H 6-12 Kush; 3-6 Parv | human | T2-C10-R2 | SHOULD | — |
| T2-C17-R1 | Kush resolves the 129 HELD and 23 CONCEPT_MISSING ingredient links (HV-008) | A 1 / H 2-4 | human | evd_ingredient_link_decisions.csv | SHOULD | — |
| T3-C03-R3 | Human review queue for the top-frequency unmapped / polysemous ingredients (top ~300 covering ~80 % of Food.com mentions) | A 2-3 (queue build) / H 6-10 (Kush+Parv, UNVERIFIED) | human | T3-C03-R2 | SHOULD | — |
| T3-C04-R2 | Human verification of matches for the top ingredients by corpus frequency | A 1 / H 4-8 (UNVERIFIED) | human | T3-C04-R1 | SHOULD | — |
| T3-C09-R4 | Small human-labelled Food.com line sample (200-300 lines) to measure NER and Rung A accuracy under no-unit shift | A 2 / H 3-5 (Kush+Parv, UNVERIFIED) | human | T3-C09-R1 | SHOULD | ANALYSIS |
| T3-C11-R2 | Per-rule precision audit on a seeded sample for the 5 highest-volume rules (COMBINE_WITH_CURRENT, AMBIGUOUS_REFERENCE, LEXICAL_COREF_DESCENDANT, PLURAL_STRIP, TOOL … | A 3-4 (sample + prereg) / H 4-6 (labelling) | human | — | SHOULD | ANALYSIS |
| T3-C20-R2 | 07I-C family threshold calibration on a human-labelled pair sample | A 3-4 / H 3-5 | human | — | SHOULD | ANALYSIS |
| T4-C01-R2 | Human review of the 27 process_medium_map rows and PROC mechanism_families for the physical families (Kush/Parv; AI personas may only propose) | A 0 / H 2-3 | human | T4-C01-R1 | SHOULD | — |
| T5-C01-R3 | Blind dual review of every entry (Kush, Parv) plus adjudication log with technical independence safeguards (07H provenance failures); under D-071 AI personas may decide … | A 0 / H 12-20 (Kush 6-10, Parv 6-10) | human | T5-C01-R1 | SHOULD | — |
| T5-C01-R6 | PROC->MECH crosswalk for 156 PROC (HV-010): AI-draft all, humans verify the PROC used by the AA pilot and blanch/boil/steam/simmer (G21.7). | A 3-5 / H 3-6 (Parv owner, Kush reviewer) | any | HV-001 protocol; T5-C01-R1 | SHOULD | CODE |
| T7-C01-R3 | Kush answers the open D35 checklist items not covered by Parv: D35-1 (sign THR rows), -2 (rdkit as project dependency, pin 2026.3.6; Parv already directed go, Kush not), … | A 1 / H 2-3 | human | reports/step35/README.md section 4 | SHOULD | DECISION |
| T7-C05-R2 | Parv audits the 50 ING<->FlavorGraph crosswalks / profile joins (D35-7). | A 1 (prepare sheet) / H 2 (Parv) | human | — | SHOULD | — |
| T7-C13-R1 | Parv writes his own 07I-C confirmation; Kush/Parv label or adjudicate any remaining calibration pairs; record the agreement figure as computed inter-reviewer value … | A 1 / H 2-3 (Parv) + 1 (Kush) | human | — | SHOULD | — |
| T8-C18-R1 | Provide hosting account (or approve tunnel route) and decide LLM path (API key vs template-only) | A 0 / H 0.5-1 (Kush) | human | — | SHOULD | DECISION |
| T8-C20-R4 | Author U (substitution) and X (control) blocks (5 each) which have no drafts | A 1-2 / H 0.5 each review | any | T8-C20-R1 | SHOULD | WRITING |
| T9-C25-R3 | VPN/route fix confirmation before server jobs (human network action) and fallback: Mac-only plan if VPN down | A 0 / H 0.25 | human | — | SHOULD | DECISION |
| T2-C05-R7 | 07.A-R1 error-detection sensitivity: optionally plant a small, prereg-disclosed set of known-wrong normalisations (hidden from raters); report detection rate per rater … | A 1-2 / H 0.3 each (maximum) | any | T2-C05-R1 (must precede signature); T9-C26-R5 | COULD | DESIGN |
| T2-C10-R4 | HV-003: predeclare sample size and audit 3,870 AI_PRECHECKED PE rows (Parv) | A 1 / H 3-6 | human | T2-C10-R2 | COULD | — |
| T3-C02-R1 | Integrate Addendum B + 10 held rules into handbook v2; dual-review the hard-case catalog answer keys | A 3-5 / H 3-6 (Kush+Parv, UNVERIFIED) | human | T3-C16 result | COULD | WRITING |
| T3-C05-R2 | Freeze PROC hierarchy v1 (parents, endpoint split) after human review | A 2-3 / H 2-4 | human | T3-C01-R2 | COULD | WRITING |
| T3-C08-R3 | Human verification of the top ~100 portion records by usage | A 1 / H 2-4 | human | T3-C08-R1 | COULD | — |
| T3-C11-R3 | Review the 4,511 inverted-interval V2 cases summary and decide the rule (UNKNOWN vs swap) | A 0.5 / H 1 | human | — | COULD | DECISION |
| T3-C16-R2 | Run P1b annotation (AI first pass ksh/prv under D-060, human stamps) and score with the same scorer | A 3-5 / H 6-12 (Kush+Parv; UNVERIFIED, P1 timing … | human | T3-C16-R1; T3-C14-R1 | COULD | ANALYSIS |
| T3-C24-R2 | Human spot review of failing cases to decide code fix vs SSOT note | A 1 / H 2-3 | human | T3-C24-R1 | COULD | — |
| T5-C04-R1 | Author >=72 (plan card) or 250 (packet figure) shared mechanism cases (event + state -> expected candidate MECH set) BEFORE any rules; Kush authors, Parv blind-labels, … | A 3-5 (templates, AI-assisted … / H 10-18 (Kush 6-10, Parv 4-8) | human | T5-C01-R2 | COULD | WRITING |
| T9-C03-R1 | Human review of similarity registry SIM-01..21 (freeze_status) - or mark 'unreviewed' in report | A 0.5 / H 1-2 | human | — | COULD | — |
| T9-C13-R5 | Review 30 AI-drafted scripted sessions (HV-006) as the D3 session set, or declare D3 session evaluation NOT_RUN | A 1 / H 3-5 | human | — | COULD | DECISION |

### 3.8 Human signatures (20)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T2-C05-R1 | Kush and Parv sign the 07A_R1 pre-registration (sha-bound signature file) before opening the packet | A 0.2 / H 0.5-1 each | human | 07A_R1_preregistration_DRAFT.md | MUST | — |
| T2-C09-R1 | Sign the AA pilot pre-registration (before any verdict is read) | A 0.1 / H 0.3-0.5 each | human | aa_pilot_preregistration_DRAFT.md | MUST | — |
| T6-C03-R1 | Kush approves the 15A-BOOT freeze record (sets FROZEN, approved_by, approved_date). No agent or persona may set it as a signature (D-071 limits). | A 0 / H 0.2 | human | — | MUST | — |
| T6-C03-R2 | Kush signs the 29-diag prereg: commits reports/step29/29diag_prereg_signature.json with SHA-256 of the unchanged prereg text (agent first fixes rung-list wording per … | A 0.5 / H 0.5-1 | human | T6-C03-R1; T6-C02-R1 | MUST | HUMAN_REVIEW |
| T8-C20-R1 | Kush and Parv sign D5/H1/H3 prereg | A 0 / H 0.3 each | human | — | MUST | — |
| T9-C07-R2 | Obtain/record a written copy (email/screenshot) of Prof. Bagler's permission for the D-045 AI-first workflow; else keep 'as stated by Kush' wording in report | A 0 / H 0.25-0.5 | human | — | MUST | DECISION |
| T9-C07-R4 | H8 scope decision: formally drop/defer D2, H2 full test, H4, Steps 20/28/33/34, FlavorTwin before the talk | A 0.5 / H 0.5 | human | T9-C14; T9-C15; T9-C19 | MUST | DECISION |
| T2-C08-R3 | Pre-register the Step 10/11 accuracy gate (precision/recall LB thresholds, human-first fallback) before any further extraction counts | A 1-2 / H 0.5-1 each | any | T2-C08 | SHOULD | WRITING |
| T3-C01-R2 | Step 16c freeze: Kush and Parv review contract v1, vocabulary hierarchy, handbook v2, hard-case keys and sign | A 1-2 (assemble packet) / H 4-8 (Kush 2-4, Parv 2-4, UNVERIFIED … | human | T3-C01-R1; T3-C02-R2 | SHOULD | HUMAN_REVIEW |
| T3-C16-R1 | Kush supplies size (3 or 4), writes the new nonce, signs the start-record amendment for P1b | A 0 / H 0.5-1 | human | — | SHOULD | DECISION |
| T5-C01-R4 | H4 decisions D21-1..D21-8 (MECH prefix, plane P-MOD, edge_semantics STATE_TRANSITION, effect-type additions, bound statuses, family tokens, directions) and freeze schema … | A 1-2 / H 1-2 | human | — | SHOULD | DECISION |
| T5-C11-R1 | Pre-register G26-VER/G26-CAL numbers and the exact no-water-assay design (O6); sign (separate files). | A 1-2 (draft) / H 1-2 | human | — | SHOULD | DECISION |
| T5-C13-R2 | Write and co-sign Step 27 pre-registration before opening SIM-VAL rows; run single confirmatory analysis; state RESEARCH_ONLY for AA (4 labs) rather than VALIDATED. | A 4-6 / H 3-5 (Kush+Parv) + audit | human | T5-C10-R6; T5-C13-R1 | SHOULD | ANALYSIS, WRITING |
| T6-C04-R1 | Decide and pre-register the H2 operational test: which row sets, splits (S-2 pair, S-3 matrix, S-6 study), margin delta_H2, K_min, who may see test; mark H2 as … | A 2-3 / H 1-2 | human | T6-C05; 07.A gate (R-05) for paper-grade | SHOULD | DECISION, WRITING |
| T7-C01-R1 | Kush and Parv each sign the v2 package (Route B on the Mac: regenerate template, confirm sha256 009c9047..., confirm not_bound_absent_here empty, fill signers/date, set … | A 0 / H 2-4 (Kush ~3 h + Parv ~3 h per sheet; … | human | reports/step35/35_0_v2_signature_sheet.md; answers to P-1..P-5, S-1, … | SHOULD | — |
| T9-C07-R5 | H7 decision: repo push/visibility for presentation (private vs public), BBC-derived counts statement | A 0 / H 0.25 | human | — | SHOULD | DECISION |
| T9-C13-R4 | Parv writes own confirmation of 07.A/07I-C statements and Step 16 comments | A 0 / H 0.5 | human | — | SHOULD | — |
| T2-C07-R1 | Sign THR-08B-05 or accept 08b-v0 as 'no claim' intake only; answer step08b_questions_for_kush.md | A 0 / H 0.5-1 | human | T2-C07 | COULD | DECISION |
| T5-C04-R2 | Seal the case set with a human-held nonce (D-071: AI cannot set nonce) and record manifest; only then author rules. | A 0.5 / H 0.5-1 | human | T5-C04-R1 | COULD | — |
| T9-C10-R2 | 15b freeze (needs 07.A valid pass + AA SIM-CAL/VAL lock) | A 3-4 / H 1-2 | mac | 07.A-R1; M3 | COULD | DECISION, CODE |

### 3.9 Expert review (6)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T2-C06-R1 | Expert/Kush reading of the USDA R6 vs Bognar overlap verdict (8 vs 11 references, Bognar cites USDA 1998) before cross_source_v1 is called independent | A 0.5 / H 0.5-2 | human | usda_bognar_overlap_v1.md | SHOULD | HUMAN_REVIEW |
| T7-C03-R3 | Chemistry-aware reviewer approves taste-label normalisation map (THR-35P-04) and the scored-class support rule (THR-35P-05); establishes the reason for the 204 … | A 1 / H 4-6 (expert) + 1 (Kush to arrange) | human | named chemistry reviewer (Kush to arrange; Parv will not nominate … | SHOULD | HUMAN_REVIEW |
| T9-C17-R3 | Add outside check: >=1 non-author reviewer (peer or food-science student) on a 20-question subset, or declare 'author-only review' limitation | A 1 / H 1-2 | human | — | SHOULD | HUMAN_REVIEW |
| T5-C01-R5 | Food-chemistry expert answers to EQ21-01..14 (aerobic/anaerobic AA pathway, ascorbate oxidase, chlorophyllase, SBO ids, analyte-form tokens, window necessity rule E-7, … | A 1-2 (prepare packet) / H 4-8 expert | human | — | COULD | — |
| T5-C11-R2 | H5 inputs: Choi-Okos coefficient check vs source, tau_h per size class, M&S limits, solver tolerances, KiSAO id check; food-engineer review of equations and assumptions. | A 2-4 / H 2-4 + expert 4-8 | human | — | COULD | WRITING |
| T7-C15-R1 | Kush names a cuisine-aware reviewer; reviewer audits artefacts ('American/French', Jewish, Roman, New...) and approves the support rule (>=100 recipes, >=2 source … | A 1 / H 4-6 (expert) + 0.5 (Kush) | human | D35-9 | COULD | HUMAN_REVIEW, DECISION |

### 3.10 Writing (14)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T0-C11-R3 | Add a documented crosswalk SSOT Task 1-9 <-> D5 blocks <-> D-008 T1-T8, and state which tasks are not covered. | A 1 / H 0 | any | — | MUST | — |
| T6-C04-R3 | For the talk: one honest H2 slide (diagnostic numbers, what cannot be concluded, prior exposure, single-study sources). | A 1-2 / H 0.5 | any | T6-C03-R4 | MUST | — |
| T8-C19-R1 | Write D4 section/report from frozen-benchmark P/C results + silver dev study (silver labelled) | A 3-4 / H 1 each | any | T8-C6-R1; T8-C21-R1 | MUST | — |
| T9-C09-R3 | Source-disjoint report line: all recipe-level results labelled source-family-disjoint or 'near-duplicate leakage not controlled' per 07I-C failure rule | A 0.5 / H 0 | any | — | MUST | — |
| T9-C28-R1 | Write licence/redistribution paragraph for report + release card (what is shown: counts only; BBC never on server; Food.com CC0 unverified) | A 1 / H 0.25 | any | T9-C05-R2 | MUST | — |
| T3-C15-R1 | Write the P1 closeout: report that states the negative gate verdict, the basis caveat, SP triage and what P1b tests; include no model-generated text as human voice | A 2-3 / H 0.5 | any | — | SHOULD | — |
| T3-C23-R1 | Record Food.com licence/units limitations in a one-page data card (counts-only) used by every T3 report | A 1-2 / H 0 | any | — | SHOULD | — |
| T6-C08-R3 | Write MNAR claim-boundary paragraph (allowed vs forbidden wording) for the talk and paper. | A 0.5-1 / H 0.3 | any | — | SHOULD | — |
| T6-C20-R1 | Draft the learning claim-boundary page and slide wording (H2 diagnostic, D2-lite, negative results kept visible). | A 2-3 / H 0.5-1 | any | T6-C03-R4 | SHOULD | — |
| T7-C22-R2 | Presentation material for the representation ladder: one slide for the ladder + nine notions + current status, one slide for negative/blocked results. | A 2-4 / H 1 | any | T7-C22-R1 | SHOULD | — |
| T7-C27-R1 | State the FlavorTwin boundary in one slide and in the 35h hand-off manifest (what is NOT claimed: no universal flavour scalar, no sensory equivalence from structure or … | A 1-2 / H 0.5 | any | T7-C22-R1 | SHOULD | — |
| T9-C01-R3 | Refresh STATUS.md to S174/S175 truth (orchestrator-only file; hand to orchestrator) | A 0.5 / H 0 | mac | — | SHOULD | — |
| T5-C21-R2 | Draft 216.13 decision record items (kinetics identifiable? simulator vs baseline? etc.) as text with NEED_DATA where applicable. | A 2-3 / H 0.5 | any | T5-C21-R1 | COULD | — |
| T6-C16-R1 | Design-only: write the DATA-SIM card and ratio-sweep control spec as DRAFT so the firewall rules are fixed before any simulator output exists. | A 3-5 / H 0.5 | any | — | COULD | — |

### 3.11 Decisions (agent drafts options, humans decide; see section 6) (43)

| Id | What | Effort | Host | Depends on | Priority | Also |
|---|---|---|---|---|---|---|
| T0-C06-R1 | Freeze the mode-to-§141 crosswalk (human-approved): DIRECT -> evidence_supported tagged E3_UNVERIFIED + COND_UNAUDITED_07A with EVD id; INTERPOLATE -> evidence_supported … | A 1-2 / H 0.5-1 | human | R-18 maturity (human decision on support enum) | MUST | WRITING |
| T0-C07-R2 | Write SSOT H1-H5 to proposal H1-H4 mapping into the report. | A 0.5 / H 0.5 | any | — | MUST | WRITING |
| T2-C05-R5 | Written ruling reconciling the plan card (R-06: AC1 diagnostic only, original kappa rule) with the R1 gating statistic, and stating what a valid 07.A unlocks given 15b … | A 0.5 / H 0.5-1 | human | — | MUST | — |
| T3-C04-R3 | Decision: SR Legacy as portion/composition authority under new basis codes (SR_PORTION) vs strict HUMAN_VERIFIED rule of rc2 | A 0.5 / H 0.5 | human | — | MUST | — |
| T3-C17-R1 | Decision on the minimum gold size and wording for the D3 claim at the talk (diagnostic on 7+40 recipes versus nothing) | A 0.5 / H 0.5 | human | T3-C11-R1 | MUST | — |
| T3-C22-R7 | Decision Q39: is lot-state worth doing before 25 Nov versus all time on H1/H3 + first SIMULATE; fix the minimal slice | A 0.5 / H 0.5 | human | — | MUST | — |
| T4-C09-R1 | Decide scope: two-zone surface model (surface at ~100 C until dry) QUALITATIVE only, or leave as stated limitation for 25 Nov | A 0 / H 0.5-1 | human | Kush | MUST | — |
| T4-C22-R1 | Decide how Layer 1/2 features enter Step 31: EVD-row arm only (as in plan) or add a recipe-event diagnostic arm with Layer 2 masked (Q1) | A 0 / H 1 | human | Q1 decision | MUST | — |
| T5-C05-R4 | Decisions Q20 (is mostly-UNKNOWN a result), Q22 (what counts as bracketing), Q23 (ASK rule) for the demo. | A 0 / H 1 | human | — | MUST | — |
| T5-C07-R1 | DECISION: FORM- prefix (vs MODEL-), freeze FORM/PARAM/VAL schemas. | A 0.5 / H 0.5-1 | human | — | MUST | — |
| T5-C13-R3 | Decision: does the talk accept descriptive pilot validation (D-076) in place of the plan's formal gate; record the deviation. | A 0 / H 0.5 | human | — | MUST | — |
| T7-C01-R2 | DECISION for the course: either sign and run descriptive explicit rungs (35a-lite, 35b PRESENCE arms, 35c R0/R2 descriptive, 35d descriptive, 35e registry) or formally … | A 0.5 / H 0.5 | human | T7-C01-R1 | MUST | — |
| T8-C02-R2 | SEMANTIC branch: keep explicit abstention for 25 Nov and state it in the demo/report (decision) | A 0.2 / H 0.2 | human | — | MUST | WRITING |
| T8-C06-R2 | Resolve embedding choice for B1/B2 (bge vs e5-large-v2) before freeze and document | A 0.2 / H 0.3 | human | — | MUST | — |
| T8-C12-R1 | Reword H3/B7 as 'rule-based evidence-sufficiency abstention (uncalibrated)' in prereg + deck; no calibration claim | A 0.3 / H 0.5 | human | — | MUST | WRITING |
| T9-C26-R1 | Publish consolidated day-by-day schedule (8-25 Nov) with human tasks front-loaded and slip triggers (e.g. no benchmark freeze by 17 Nov => H1/H3 reported as NOT_RUN) | A 1-2 / H 0.5 | any | T9-C25-R1 | MUST | WRITING |
| T9-C26-R2 | Declare fallback levels: (L0) full plan, (L1) H1 only, (L2) benchmark frozen but not run, (L3) results = router census + gates only; pre-write wording for each in report | A 1 / H 0.5 | any | T9-C26-R1 | MUST | WRITING |
| T9-C26-R5 | Prereg edit-lock: all pre-signature edits (07A ruling T2-C05-R5, H3/B7 reword T8-C12-R1 + H1 circularity caveat T8-C04-R2, power note T9-C12-R1, embedding choice … | A 2-3 / H 0.5 | any | T2-C05-R5; T8-C12-R1; T9-C12-R1; T8-C06-R2; T6-C03-R5 | MUST | WRITING |
| T0-C01-R1 | Decide whether to apply the v16 change set / a status addendum before 25 Nov (Q40). Agent lean: do NOT apply; ship a one-page 'SSOT v15 vs current state' delta in the … | A 1-2 / H 0.5-1 | human | Q40 | SHOULD | — |
| T0-C18-R2 | Formalise D-071 line (AI persona decision vs human signature) in DECISIONS (Q37). | A 0.5 / H 0.5 | human | D-071 | SHOULD | — |
| T2-C03-R1 | Decide the physical/history SVAR v1.1 set and definitions (shared with the lot-state topic) | A 0.5-1 / H 1-2 | human | lot-state topic | SHOULD | — |
| T2-C04-R1 | Rule whether 07.B COND v1.1 axes and 07.C platform vocabulary are adopted now (new AA/literature rows need them) or stay as raw-text SEXP optional fields | A 0.5 / H 0.5-1 | human | T2-C09 | SHOULD | — |
| T2-C11-R2 | Decision on ordering: ingest R2 + Bognar remainder into EVD before approving the 15a freeze, or defer to 15a.1 (new version) | A 0.2 / H 0.3 | human | T2-C15-R3 | SHOULD | — |
| T2-C18-R1 | Kush rules on the H2 queue items needed before 25 Nov: #1/#3/#4 (Europe PMC, NCBI, Unpaywall), #6 (CoFID OGL), #16 (Food.com) | A 0 / H 0.5-1 | human | es_1_2_h2_approval_queue.md | SHOULD | — |
| T3-C25-R1 | Write a short design note fixing belief fields and class tags (source/semantic/episode/evidence/model) for every lot-step field; reviewed by Kush/Parv | A 2-3 / H 1-2 | human | — | SHOULD | WRITING |
| T5-C02-R4 | Decision Q21: may POSSIBLE screens from unreviewed MECH give QUALITATIVE direction labelled AI_DRAFTED; Q15 acceptable sources for windows. | A 0 / H 0.5-1 | human | — | SHOULD | — |
| T7-C04-R1 | Kush confirms (or reverses) the RDKit dependency decision D35-2 and the Open Babel stance D35-3. | A 0 / H 0.5 | human | — | SHOULD | — |
| T7-C08-R1 | Decide and document ingredient-level SENSORY as UNSUPPORTED for 25 Nov (talk wording) and keep structural != sensory as a stated boundary. | A 1 / H 0.5 | human | — | SHOULD | WRITING |
| T7-C16-R1 | Kush decides sim_id scheme and status mapping (D35-12), SIM-13 home (D35-11), and which statuses count as 'supported' for G35-SEP. | A 0.5 / H 1 | human | — | SHOULD | — |
| T7-C20-R1 | Write the explicit statement 'learned rungs deferred; entry rule LR-1..LR-5' into the 35h record and talk (limitation slide). | A 1 / H 0.5 | human | — | SHOULD | WRITING |
| T7-C24-R1 | DECISION: L13E = optional, parked (AH12) except one bounded descriptive null/rank-frequency chain; record 'not primary deliverable' and §279.8 first-paper choice. | A 0.5 / H 0.5 | human | — | SHOULD | — |
| T9-C07-R1 | Fill H3 compute threshold (node-hours) and record that D-077 compute (vinayak, manjot, mac) is inside it | A 0.25 / H 0.25 | human | T9-C25 | SHOULD | — |
| T9-C25-R5 | Environment/installs authorisation decision (D-number): install sklearn/lightgbm/hypothesis/lxml/rdkit/torch on manjot vs run on Mac/vinayak; list exact packages per … | A 0.5-1 / H 0.3-0.5 | human | — | SHOULD | — |
| T0-C15-R3 | Decide which §123 null models (ingredient-shuffle, category-preserving, frequency-preserving) are in scope for the talk; list the rest as uncovered; xref T7-C06/C14 so … | A 1 / H 0.5 | any | T7-C01-R2 | COULD | WRITING |
| T2-C10-R6 | Record 11.D formally: AA chosen at 26.0 (D-052) before Step 11 evidence (R-14 intended choice from verified evidence); state this in the decision log | A 0.2 / H 0.2 | human | D-052 | COULD | — |
| T2-C13-R2 | Choose the anchor set after a coverage audit and register the READY/PARTIAL/NEED_DATA readiness ledger for consumers (26/27, 29/30, 23 negatives) | A 6-12 / H 1-2 | any | T2-C06; T2-C09 | COULD | ANALYSIS |
| T2-C19-R1 | Record the E6/E7 reconciliation in the v16 change set (decision only) | A 0.5 / H 0.3 | human | v16 change set | COULD | WRITING |
| T3-C09-R5 | Decide retrain vs accept (Q34): fine-tune on unit-less Food.com lines or accept | A 0.5 / H 0.5 | human | T3-C09-R4 | COULD | — |
| T4-C23-R1 | Decide: add as extra Layer 2 spread or state as out of scope | A 0 / H 0.5 | human | — | COULD | — |
| T6-C09-R3 | Decide TRUE_ZERO code addition to censoring registry (additive change). | A 0.2 / H 0.2 | human | — | COULD | — |
| T7-C10-R1 | DECISION on a cheaper non-circular first version (packet Q31): similarity of mechanism-screen profiles or of EVD before/after retention vectors (vit C, phenolics) on … | A 1 / H 1 | human | Step 15 freeze | COULD | — |
| T7-C12-R1 | Resolve the 9 build-note ambiguities (idf formula, unseen df, tf form, R3 masking, bin edges, floor equality) by registry rows or explicit confirmation. | A 1 / H 1 | human | T7-C01-R1 | COULD | WRITING |
| T9-C23-R1 | Choose paper angle (RAG paper §253.4 vs dataset §253.3 vs transition §253.5), outline sections and required missing evidence; record as DECISION | A 2 / H 1 | human | T9-C17-R2 | COULD | WRITING |

## 4. The 25 Nov plan

MUST items: **84** (after round 2: T5-C22-R1 folded into T0-C06-R2, T9-C32-R1 moved to SHOULD, T9-C26-R3 raised to MUST). Agent effort for MUST, summed from the ledger ranges: about 134-208 h (rough; per-run and 'total' rows counted once). Human MUST hours that fall in 9-16 Nov, summed over the ledger items: about 26-35 h (review and signature items are per person; joint decisions are counted once). That is more than R-FEAS's de-duplicated estimate of 16-20 h each (T9-C26-R4, UNVERIFIED). **This week is the bottleneck.** The cheapest saving is the decision sitting: the agent writes each decision as one recommended option plus alternatives, so most take minutes, not the ledger's 0.5-1 h. Kush and Parv must state their own availability for 9-16 Nov (not repo evidence).

### 4.1 Key dates and slip triggers (adopted on T9-C26-R2)

| Date | Gate | If it slips (pre-written fallback) |
|---|---|---|
| 9 Nov | Q39 lot-state ruling (T3-C22-R7), 07.A AC1-vs-kappa ruling (T2-C05-R5) | lot-state deferred to stretch (agent lean); without the 07.A ruling the R1 prereg cannot be signed -> 07.A stays FAILED-on-record |
| 10 Nov | prereg edit lock + hashes (T9-C26-R5); AA PDFs (T2-C09-R2); Step 35 decision (T7-C01-R2) | no edits after the lock; missing PDFs -> fit on the 4 papers already present, the missing paper dropped and recorded; Step 35 -> DESIGNED, NOT RUN |
| 10-11 Nov | signatures: 07A_R1, AA, D5/H1/H3, 15A-BOOT + 29-diag | each unsigned prereg -> its result is reported NOT_RUN (never run on an AI signature) |
| 13 Nov | 07.A-R1 labels in (T2-C05-R2) | 07.A FAILED-on-record; 23b stays closed |
| 14 Nov | D5 runner dry run on vinayak (T8-C15-R1) | fix route; plan the manjot-CPU fallback |
| 15 Nov | AA CAL rows dual-verified (T2-C09-R4) | no PARAM, no SIMULATE result; SIMULATE wiring shipped "code-tested only"; Model A NEED_DATA if below the prereg minimum |
| 16 Nov | D5 reviewed and frozen (T8-C20-R2/R3); Model A fit frozen (T5-C10-R5) | fallback L2: benchmark frozen but not run, H1/H3 NOT_RUN; SIM-VAL (T5-C10-R6) drops to SHOULD |
| 17 Nov | vinayak reachable | run deterministic rungs B0/B1/B2/B4/B5T on manjot CPU; LLM rungs NOT_RUN (C07, written into the D5 prereg in the lock) |
| 19 Nov | results in | fallback L3: report = router census + gate table only |
| 21 Nov | **code and result freeze**; full report draft | nothing new enters the talk after this |
| 22-23 Nov | human edit of report and deck | agent ships the draft with every number cited to a file |
| 24 Nov | timed rehearsal + "cannot claim" Q&A sheet (T9-C26-R3) | — |

### 4.2 MUST items in date and dependency order

Owners: Kush, Parv, agent-on-manjot, agent-on-Mac, vinayak (agent on vinayak). "Kush + Parv" means each does it separately where the item says "each".

| When | Id | What | Owner | Effort | Depends on |
|---|---|---|---|---|---|
| 08-09 Nov | T9-C25-R1 | Aggregate compute ledger: remaining runs by host with agent-hours and wall-clock estimates (from all topics' inventories), VPN risk and disk budget | agent-on-manjot drafts; Kush confirms calendar 10 Nov | A 2 / H 0 | T1..T10 inventories |
| 08-09 Nov | T9-C26-R1 | Publish consolidated day-by-day schedule (8-25 Nov) with human tasks front-loaded and slip triggers (e.g. no benchmark freeze by 17 Nov => H1/H3 … | agent-on-manjot drafts; Kush confirms calendar 10 Nov | A 1-2 / H 0.5 | T9-C25-R1 |
| 08-09 Nov | T9-C26-R2 | Declare fallback levels: (L0) full plan, (L1) H1 only, (L2) benchmark frozen but not run, (L3) results = router census + gates only; pre-write … | agent-on-manjot drafts; Kush confirms calendar 10 Nov | A 1 / H 0.5 | T9-C26-R1 |
| 08-09 Nov | T9-C26-R4 | Single human-time ledger + human-only items sheet: de-duplicated hours per person by task and week (approx. 16-20 h each over 9-16 Nov: signatures … | agent-on-manjot drafts; Kush confirms calendar 10 Nov | A 1-2 / H 0.5 | T9-C26-R1 |
| every run, 08-21 Nov | T9-C25-R4 | Log every new S176 run row in compute_runs_v1.csv (orchestrator merges); counts-only outputs; sha256 | agent on each host (orchestrator merges) | A 0.5 per run / H 0 | — |
| 09 Nov | T6-C02-R1 | Write registry/transition_ladder_crosswalk_v1.csv (B-0=D0, B-1=D1, B-2=D3 matrix arm, B-3=D2, B-4=D4, B-5=D5; M0..M11 map) and fix label mismatch … | agent-on-manjot (before the 29-diag signature) | A 1-2 / H 0 | — |
| 09 Nov | T3-C22-R7 | Decision Q39: is lot-state worth doing before 25 Nov versus all time on H1/H3 + first SIMULATE; fix the minimal slice | Kush + Parv (agent drafts options) | A 0.5 / H 0.5 | — |
| 09 Nov | T2-C05-R5 | Written ruling reconciling the plan card (R-06: AC1 diagnostic only, original kappa rule) with the R1 gating statistic, and stating what a valid 07.A … | Kush + Parv (agent drafts options) | A 0.5 / H 0.5-1 | — |
| 10 Nov (edit lock) | T8-C12-R1 | Reword H3/B7 as 'rule-based evidence-sufficiency abstention (uncalibrated)' in prereg + deck; no calibration claim | agent drafts; Kush + Parv approve | A 0.3 / H 0.5 | — |
| 10 Nov (edit lock) | T9-C12-R1 | Power/MDE note for H1/H3 (exact McNemar at n=30, discordance assumptions) added to prereg amendment BEFORE signature | agent drafts; Kush + Parv approve | A 1 / H 0 | T9-C08-R2 |
| 10 Nov (edit lock) | T8-C06-R2 | Resolve embedding choice for B1/B2 (bge vs e5-large-v2) before freeze and document | agent drafts; Kush + Parv approve | A 0.2 / H 0.3 | — |
| 10 Nov text in prereg; compute 12-14 Nov | T6-C03-R5 | Add paired D2-process-mean vs D3-ingredient-mean contrast (H2 shape: process info vs food-identity-only) on S-3/S-4/S-6 inside the diag memo, … | agent-on-Mac | A 2-3 / H 0 | T6-C03-R3 |
| 10 Nov (lock + hash) | T9-C26-R5 | Prereg edit-lock: all pre-signature edits (07A ruling T2-C05-R5, H3/B7 reword T8-C12-R1 + H1 circularity caveat T8-C04-R2, power note T9-C12-R1, … | agent-on-manjot + Kush | A 2-3 / H 0.5 | T2-C05-R5; T8-C12-R1; T9-C12-R1; T8-C06-R2; T6-C03-R5 |
| 10 Nov | T7-C01-R2 | DECISION for the course: either sign and run descriptive explicit rungs (35a-lite, 35b PRESENCE arms, 35c R0/R2 descriptive, 35d descriptive, 35e … | Kush + Parv | A 0.5 / H 0.5 | T7-C01-R1 |
| 10-12 Nov (decision sitting) | T0-C06-R1 | Freeze the mode-to-§141 crosswalk (human-approved): DIRECT -> evidence_supported tagged E3_UNVERIFIED + COND_UNAUDITED_07A with EVD id; INTERPOLATE … | Kush + Parv (agent drafts) | A 1-2 / H 0.5-1 | R-18 maturity (human decision on support enum) |
| 10-12 Nov (decision sitting) | T5-C07-R1 | DECISION: FORM- prefix (vs MODEL-), freeze FORM/PARAM/VAL schemas. | Kush + Parv (agent drafts) | A 0.5 / H 0.5-1 | — |
| 10-12 Nov (decision sitting) | T3-C04-R3 | Decision: SR Legacy as portion/composition authority under new basis codes (SR_PORTION) vs strict HUMAN_VERIFIED rule of rc2 | Kush + Parv (agent drafts) | A 0.5 / H 0.5 | — |
| 10-12 Nov (decision sitting) | T3-C07-R3 | Decision: how Food.com no-unit lines are treated (presence-only composition; or find original data with units; or flagged imputation) | Kush + Parv (agent drafts) | A 1 (sourcing check) / H 0.5-1 | — |
| 10-12 Nov (decision sitting) | T4-C09-R1 | Decide scope: two-zone surface model (surface at ~100 C until dry) QUALITATIVE only, or leave as stated limitation for 25 Nov | Kush + Parv (agent drafts) | A 0 / H 0.5-1 | Kush |
| 10-12 Nov (decision sitting) | T4-C22-R1 | Decide how Layer 1/2 features enter Step 31: EVD-row arm only (as in plan) or add a recipe-event diagnostic arm with Layer 2 masked (Q1) | Kush + Parv (agent drafts) | A 0 / H 1 | Q1 decision |
| 10-12 Nov (decision sitting) | T5-C05-R4 | Decisions Q20 (is mostly-UNKNOWN a result), Q22 (what counts as bracketing), Q23 (ASK rule) for the demo. | Kush + Parv (agent drafts) | A 0 / H 1 | — |
| 10-12 Nov (decision sitting) | T5-C13-R3 | Decision: does the talk accept descriptive pilot validation (D-076) in place of the plan's formal gate; record the deviation. | Kush + Parv (agent drafts) | A 0 / H 0.5 | — |
| 10-12 Nov (decision sitting) | T8-C02-R2 | SEMANTIC branch: keep explicit abstention for 25 Nov and state it in the demo/report (decision) | Kush + Parv (agent drafts) | A 0.2 / H 0.2 | — |
| 10-12 Nov (decision sitting) | T3-C17-R1 | Decision on the minimum gold size and wording for the D3 claim at the talk (diagnostic on 7+40 recipes versus nothing) | Kush + Parv (agent drafts) | A 0.5 / H 0.5 | T3-C11-R1 |
| 10-12 Nov (decision sitting) | T9-C07-R4 | H8 scope decision: formally drop/defer D2, H2 full test, H4, Steps 20/28/33/34, FlavorTwin before the talk | Kush + Parv (agent drafts) | A 0.5 / H 0.5 | T9-C14; T9-C15; T9-C19 |
| 10-12 Nov (decision sitting) | T9-C07-R2 | Obtain/record a written copy (email/screenshot) of Prof. Bagler's permission for the D-045 AI-first workflow; else keep 'as stated by Kush' wording … | Kush + Parv (agent drafts) | A 0 / H 0.25-0.5 | — |
| 10-11 Nov | T6-C19-R1 | Record the learning environment per host (mac pinned versions; vinayak; manjot CPU) in a lock file; run a smoke import and the transition test suite … | agent-on-Mac; Parv authorises | A 1-2 / H 0.3 (Parv authorises) | — |
| 10 Nov (after lock) | T2-C09-R1 | Sign the AA pilot pre-registration (before any verdict is read) | Kush + Parv (never AI, D-071) | A 0.1 / H 0.3-0.5 each | aa_pilot_preregistration_DRAFT.md |
| 10 Nov (right after the AA signature) | T2-C09-R2 | Browser-download the 5 PDFs that refuse scripted download (AAK-02,04,05,08,10) into data/raw/aa_pilot/ on the Mac; confirm licence on the publisher … | Kush (browser, Mac) | A 0 / H 0.5-1 | T2-C09-R1 |
| 10-11 Nov (after lock) | T2-C05-R1 | Kush and Parv sign the 07A_R1 pre-registration (sha-bound signature file) before opening the packet | Kush + Parv (never AI, D-071) | A 0.2 / H 0.5-1 each | 07A_R1_preregistration_DRAFT.md |
| 10-11 Nov (after lock) | T8-C20-R1 | Kush and Parv sign D5/H1/H3 prereg | Kush + Parv (never AI, D-071) | A 0 / H 0.3 each | — |
| 10-11 Nov (after lock) | T6-C03-R1 | Kush approves the 15A-BOOT freeze record (sets FROZEN, approved_by, approved_date). No agent or persona may set it as a signature (D-071 limits). | Kush (never AI, D-071) | A 0 / H 0.2 | — |
| 10-11 Nov (after lock) | T6-C03-R2 | Kush signs the 29-diag prereg: commits reports/step29/29diag_prereg_signature.json with SHA-256 of the unchanged prereg text (agent first fixes … | Kush (never AI, D-071) | A 0.5 / H 0.5-1 | T6-C03-R1; T6-C02-R1 |
| 10-14 Nov build; go/no-go 16 Nov | T5-C11-R4 | Wire router SIMULATE branch end-to-end: eligible AA events (steam/sealed medium) -> retention INTERVAL with PARAM id and basis; all else UNKNOWN; … | agent-on-manjot | A 6-10 / H 0 | T5-C10-R5 |
| 11-13 Nov | T2-C05-R2 | Kush and Parv each independently label the 100-condition R1 packet (9 fields + overall), alone, blind, no external source | Kush + Parv (3-4 h each, blind) | A 0 / H 3-4 each | T2-C05-R1 |
| 11-12 Nov | T2-C09-R3 | AI extraction of CAL rows from newly downloaded SIM-CAL papers with spans (SIM-VAL papers stay unopened until fit freeze) | agent-on-Mac | A 3-5 / H 0-0 | T2-C09-R2 |
| 11-14 Nov | T6-C03-R3 | Run 29-diag twice on the Mac (CPU, minutes) and verify byte-identical outputs (G15-R). | agent-on-Mac | A 0.5-1.5 / H 0 | T6-C03-R1; T6-C03-R2 |
| 11-15 Nov build; final scan 19-20 Nov | T0-C06-R2 | End-to-end contract audit: property tests plus a corpus scan that no emitted answer contains a food-chemistry number lacking an EVD id or a … | agent-on-manjot (+ Mac for hypothesis) | A 5-8 / H 0 | T0-C06-R1 |
| 11-15 Nov | T9-C09-R1 | Build and hash a SPLIT registry for the three evaluations that will run (D5 benchmark questions, 29-diag S-1..S-5, 07.A packet) and record in ledgers … | agent-on-manjot | A 3-5 / H 0 | T9-C10; T9-C17 |
| 11-15 Nov | T9-C09-R2 | Leakage audit: D5 S-block recipes vs NER/linker/gold training splits and vs Rung A dev sets; P/C cells vs EVD rows used in DEL-2 / retrieval silver | agent-on-manjot | A 2-3 / H 0 | D5 draft |
| 11-15 Nov | T2-C15-R1 | Build the dataset-card generator and publish counts-only card for the 17,978 ACTIVE E3 rows (all §203.9 outputs, COND_UNAUDITED / … | agent-on-manjot | A 8-12 total / H 1-2 review | T2-C01; T2-C04; T2-C06 |
| 11-15 Nov | T3-C03-R2 | Coverage census: fraction of Food.com / Wikibooks / TASTEset ingredient mentions (NER FOOD spans and Rung A links) that hit ING/ALIAS, by mention … | agent-on-manjot | A 3-5 / H 0 | T3-C09-R1 |
| 11-15 Nov | T4-C04-R1 | Write 'what the corpus can say' analysis: coverage by family, source and process, share with both t and T, ranges, gas-mark-only, per-family top … | agent-on-manjot | A 3-5 / H 1 | existing census JSONs |
| 11-15 Nov | T4-C11-R1 | Census of events per non-heat family across the full corpus (counts, how many state time/T/medium/size) to size the work and rank families by volume | vinayak (fallback agent-on-manjot); do SHOULD T4-C01-R1 first | A 2-4 / H 0 | T4-C01-R1 |
| 11-16 Nov | T8-C20-R2 | Kush and Parv independently review 100 questions (KEEP/EDIT/DROP), reconcile; agent assembles benchmark | Kush + Parv (5-7 h each) | A 1 / H 5-7 each (incl. S-gold re-derivation) | T8-C20-R1 |
| by 12 Nov | T5-C05-R1 | Install hypothesis in an env where installs are allowed (Mac or vinayak) and run the >=10^4 randomised property test 'UNKNOWN/NOT_APPLICABLE never … | agent-on-Mac (needs install OK, T9-C25-R5) | A 0.5 / H 0 | T9-C25-R5 |
| 12-15 Nov | T2-C09-R4 | Kush and Parv each verify every CAL row (VERIFIED / CORRECTED / REJECTED) against the paper span, blind to the other | Kush + Parv (3 h each, blind) | A 0 / H 3 each | T2-C09-R1 |
| 12-14 Nov | T9-C08-R4 | Add NEG rows for S171-S176 negatives (router DIRECT 0.754 %, D-074 R1 4/60, Food.com no-units, NER UNIT<<QUANTITY, SP-002 29.8 %, P1 … | agent-on-manjot; Kush/Parv review | A 1-2 / H 0.5-1 | — |
| skeleton 13 Nov; draft 21 Nov; edit 22-23 Nov | T9-C20-R1 | Final report and slides (one item): skeleton with placeholders 13 Nov, fill tables from committed JSON as each result lands, full draft 21 Nov, human … | agent-on-Mac; Kush + Parv edit | A 15-22 total / H 4-6 each | T9-C17-R2; T9-C14-R4; T9-C13-R2 |
| 14 Nov | T6-C03-R4 | Write the four diag memos with every number labelled DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE and no words 'supported', 'beats', 'validated'; … | agent-on-Mac; Kush/Parv review | A 3-5 / H 0.5-1 review | T6-C19-R1; T6-C03-R1; T6-C03-R2 |
| 14 Nov | T2-C05-R3 | Score with tools/step07ar_agreement.py; verify freeze (step07hr_freeze.py --verify); write result JSON + diagnostics (kappa, PABAK, per-field, … | agent-on-manjot | A 0.5-1 / H 0-0 | T2-C05-R2 |
| 14-15 Nov | T2-C05-R4 | Joint adjudication of disagreements, DECISIONS entry (counted by orchestrator), statistic never recomputed after adjudication | Kush + Parv | A 0.5 / H 0.5-1 each | T2-C05-R3 |
| dry run 14 Nov; runs 17-19 Nov | T8-C15-R1 | Run B0/B1/B2/B4/B5/B7/B5T on frozen D5 benchmark with qwen2.5:7b (temp 0, seed fixed), log run in compute_runs_v1.csv | vinayak (fallback: deterministic rungs on manjot CPU) | A 3-5 / H 0 | T8-C20-R3; VPN to vinayak; Ollama up |
| 15 Nov | T6-C04-R3 | For the talk: one honest H2 slide (diagnostic numbers, what cannot be concluded, prior exposure, single-study sources). | agent-on-Mac | A 1-2 / H 0.5 | T6-C03-R4 |
| 16 Nov | T8-C20-R3 | Freeze benchmark (sha256) and run freeze check | agent-on-manjot; Kush + Parv confirm | A 0.5 / H 0.3 | T8-C20-R2 |
| 16 Nov | T5-C10-R5 | Fit Model A on verified SIM-CAL rows, run Model B sensitivity, freeze fit JSON with sha256 and code hash BEFORE any SIM-VAL text is opened; ensure … | agent-on-manjot | A 3-5 / H 0.5 | T5-C10-R4 |
| 16 Nov | T5-C07-R3 | Mint PARAM rows ONLY from rows both humans VERIFIED (K>=K1, source locator, fitted_on block); automated check 0 PARAM from K0 aggregates. | agent-on-manjot | A 2-4 / H 0 | T5-C10-R4 |
| 16-17 Nov | T5-C12-R2 | Identifiability report for the AA pilot fit (profile CI for ln k_ref and Ea; practical-identifiability test). | agent-on-manjot | A 2-3 / H 0.5 | T5-C10-R5 |
| 17-19 Nov | T8-C21-R1 | Execute H1 runs on frozen S1/S2 (B0,B1,B2,B4 + B5/B7), compute McNemar/Newcombe | vinayak | A 2-3 / H 0 | T8-C20-R3; T8-C15-R1 |
| 17-19 Nov | T8-C22-R1 | Execute H3 analysis on frozen P/C blocks; decision-mode F1; handle zero-claim denominators | agent-on-manjot | A 3-4 / H 0 | T8-C21-R1 |
| 17-19 Nov | T8-C06-R1 | Run retrieval metrics (Recall@K, MRR, condition-compatible Recall@K, source-disjoint split) on frozen D5 P/C questions as the D4 real evaluation | agent-on-manjot | A 2-4 / H 0 | T8-C20-R3 |
| 17-19 Nov | T8-C01-R1 | Score router branch accuracy on the frozen D5 80 questions (never tune on them); report confusion matrix incl. X controls | agent-on-manjot | A 1-2 / H 0 | T8-C20-R3 |
| 17-19 Nov | T8-C10-R1 | Score C-block comparisons vs reviewed gold; report 'cannot separate' rate | agent-on-manjot | A 1 / H 0 | T8-C20-R3 |
| 17-19 Nov | T8-C13-R1 | Evaluate OOD gate on P3 (gold=ABSTAIN) vs P1/P2: abstain recall/false-abstain rate | agent-on-manjot | A 1 / H 0 | T8-C20-R3 |
| 17-19 Nov | T8-C16-R2 | Report enforcement cost: sentences removed, fallback rate, answer length/coverage per rung | agent-on-manjot | A 1 / H 0 | T8-C15-R1 |
| 17-19 Nov | T8-C16-R1 | Add citation precision/recall and a manual-verification sample (30 claims) to H3 reporting, so UCR is not self-graded only | agent-on-manjot + Kush/Parv (30-claim blind sample) | A 2-3 / H 1-1.5 each | T8-C21-R1 |
| 17-18 Nov | T5-C10-R6 | Then extract and verify SIM-VAL rows (AAK-12/07/03/05) and compute descriptive prediction error and interval coverage (Step 27 pilot). | agent-on-manjot + Kush/Parv (1.5-2 h each) | A 3-5 / H 1.5-2 each (4 papers) | T5-C10-R5 |
| 17-19 Nov | T5-C11-R3 | Calibrate sim_aa_1 with frozen Model A PARAM (26d on SIM-CAL only), produce calibration report + identifiability report on real data; issue SIMM-AA-1 … | agent-on-manjot | A 6-10 / H 1 | T5-C10-R5; T5-C10-R6 |
| 18-20 Nov (edits by 20 Nov) | T4-C25-R1 | Draft physical-layer slides/figures (coverage funnel, bracket spread, UNKNOWN reasons, non-heat families status) with wording audit against §141 | agent-on-Mac; Kush/Parv edit | A 3-5 / H 1 each | T4-C04-R1; T4-C05-R1 |
| 19-20 Nov | T5-C21-R1 | Produce an honest G15 gate scorecard for T5 gates (G15-4,5,8,11,12,HYB,RXN,INV, partial 1,6,7,H,R) with file evidence and … | agent-on-manjot | A 3-5 / H 1 | T5-C10-R5; T5-C12-R2 |
| 19-20 Nov | T8-C04-R2 | Report circularity caveat and an engine-vs-human-edited-gold agreement figure for S blocks | agent-on-manjot | A 1 / H 0 | T8-C20-R2 |
| 19-21 Nov | T9-C16-R1 | Report D3 as 'built + run, gold comparison limited to P1 (7 pairs, AI-drafted, human-accepted)' with intervals; add replay-consistency and … | agent-on-Mac (report); humans read in 22-23 Nov edit | A 2-3 / H 0 | — |
| 19-21 Nov | T2-C06-R2 | Slide-level honest statement of lineage: counts, G08-3 FAIL, publication-component CV label, one-line implication for every H2 claim | agent-on-Mac (report); humans read in 22-23 Nov edit | A 1-2 / H 0.5 | T2-C06 reports |
| 19-21 Nov | T2-C21-R1 | Write the D1 section and figures: sources, counts by tier/source/target, coverage (T/t/pH/a_w), lineage label, verified rows n/40, what is not claimed | agent-on-Mac (report); humans read in 22-23 Nov edit | A 4-8 / H 1-2 review | T2-C15-R1; T2-C10-R1; T2-C06-R2 |
| 19-21 Nov | T8-C19-R1 | Write D4 section/report from frozen-benchmark P/C results + silver dev study (silver labelled) | agent-on-Mac (report); humans read in 22-23 Nov edit | A 3-4 / H 1 each | T8-C6-R1; T8-C21-R1 |
| 19-21 Nov | T9-C23-R2 | Re-score MPU table after M1-M6 outcomes (true numbers) | agent-on-Mac (report); humans read in 22-23 Nov edit | A 1 / H 0 | H1/H3 results |
| 19-21 Nov | T0-C11-R3 | Add a documented crosswalk SSOT Task 1-9 <-> D5 blocks <-> D-008 T1-T8, and state which tasks are not covered. | agent-on-Mac (report); humans read in 22-23 Nov edit | A 1 / H 0 | — |
| 19-21 Nov | T0-C07-R2 | Write SSOT H1-H5 to proposal H1-H4 mapping into the report. | agent-on-Mac (report); humans read in 22-23 Nov edit | A 0.5 / H 0.5 | — |
| 19-21 Nov | T9-C07-R3 | Report section stating exactly which gates were AI-delegated (D-071) vs human-signed, generated from DECISIONS (script, counts only) | agent-on-Mac (report); humans read in 22-23 Nov edit | A 1-2 / H 0.5 | D-071 |
| 19-21 Nov | T9-C28-R1 | Write licence/redistribution paragraph for report + release card (what is shown: counts only; BBC never on server; Food.com CC0 unverified) | agent-on-Mac (report); humans read in 22-23 Nov edit | A 1 / H 0.25 | T9-C05-R2 |
| 19-21 Nov | T9-C09-R3 | Source-disjoint report line: all recipe-level results labelled source-family-disjoint or 'near-duplicate leakage not controlled' per 07I-C failure … | agent-on-Mac (report); humans read in 22-23 Nov edit | A 0.5 / H 0 | — |
| 21 Nov (freeze day) | T9-C28-R2 | Check slides/report/demo screenshots for recipe text leakage (automated grep of committed outputs against git-ignored text hashes) | agent-on-Mac | A 1-2 / H 0 | T9-C20; T9-C21 |
| 22-23 Nov | T9-C20-R3 | Authors read and correct contributions section, confirm presentation date 25-26 Nov | Kush + Parv | A 0 / H 1 | — |
| Q&A sheet 23 Nov; dry run 24 Nov | T9-C26-R3 | Timed dry run of the talk on 24 Nov including the live-demo fallback, plus a one-page 'cannot claim' Q&A sheet drafted by the agent (H2 diagnostic … | agent drafts sheet; Kush + Parv rehearse | A 1-2 (Q&A sheet) / H 1.5-2 each | T9-C21-R1 |

Dependency notes the agent must respect: T4-C11-R1 (MUST) depends on T4-C01-R1, which is only SHOULD — do T4-C01-R1 first. T5-C05-R1 needs the install authorisation T9-C25-R5 (SHOULD); if it is not given by 12 Nov, the report says the hypothesis property tests were not run. T0-C06-R2 now carries R-SCI's four composed-pipeline rules (C03). T9-C20-R1 now carries the number-class check (C04). T8-C04-R2 has two parts: the circularity caveat goes into the prereg by 10 Nov; the agreement figure is made 19-20 Nov.

### 4.3 SHOULD and COULD (only after the week's MUST items are green)

SHOULD: 168 items, COULD: 110 items (full lists in section 3). The SHOULD items that most help the talk:

| Id | What | Effort | Host | When |
|---|---|---|---|---|
| T9-C25-R5 | Environment/installs authorisation decision (D-number): install sklearn/lightgbm/hypothesis/lxml/rdkit/torch on manjot vs run on … | A 0.5-1 / H 0.3-0.5 | human | by 10 Nov (unblocks T5-C05-R1, T6-C03-R3) |
| T9-C25-R3 | VPN/route fix confirmation before server jobs (human network action) and fallback: Mac-only plan if VPN down | A 0 / H 0.25 | human | by 13 Nov |
| T4-C01-R1 | Freeze a PROC to process-family registry (one row per PROC, one primary family, secondary flag) covering all 93 PROCs and the 8 non-heat … | A 3-5 / H 1-2 | any | 10-11 Nov (before T4-C11-R1) |
| T9-C32-R1 | Number-class lint for deck/report: every number tagged EVD(E3-unverified/COND-unaudited) / TEXT_STATED / SCENARIO/ASSUMED_DEFAULT / … | A 2 / H 0.5 (exceptions list, 22-23 Nov) | any | script by 21 Nov, else manual deck check |
| T4-C26-R1 | Layer 1 binder precision audit, AI pass only: n=100 seeded bound heat events (seed 20261104, stratified by family, non-BBC families on … | A 3-4 / H 0 (COULD: adjudicate 20 events after 16 … | manjot | 17-20 Nov (after D5 freeze, AI-only) |
| T0-C19-R1 | SSOT coverage map for sections no topic anchors: §121-§127/§80-§86/§159-§160 classical pairing; §152-§158, §161-§170 course ontology + … | A 3-5 / H 0.5 | any | 12-18 Nov (agent pass) |
| T0-C01-R1 | Decide whether to apply the v16 change set / a status addendum before 25 Nov (Q40). Agent lean: do NOT apply; ship a one-page 'SSOT v15 vs … | A 1-2 / H 0.5-1 | human | decide by 12 Nov |
| T0-C06-R3 | Show the three-way label and basis (EVD/Layer 2/ASSUMED) on every demo claim chip. | A 2-3 / H 0 | mac | 18-21 Nov |
| T9-C20-R2 | Figures: architecture (SSOT fig1), data tier/provenance, state-graph example, router route histogram, risk-coverage, ladder/ablation, … | A 4-6 / H 0 | mac | 18-21 Nov |
| T9-C21-R2 | Recorded demo fallback video/screens if hosting or VPN fails | A 1-2 / H 0.5 | mac | 21-23 Nov |
| T9-C17-R3 | Add outside check: >=1 non-author reviewer (peer or food-science student) on a 20-question subset, or declare 'author-only review' … | A 1 / H 1-2 | human | during D5 review, else state limitation |
| T8-C08-R1 | Wire first SIMULATE (sim_aa_1 vitamin C) into the cascade as B6 only as a RESEARCH_ONLY rung after the fit freeze and the descriptive … | A 3-5 / H 0 | any | after 18 Nov only if fit frozen + SIM-VAL report exist |
| T3-C22-R1 | Step 1-2 slice: lot members + presence-only composition from ING->SR match; mass interval only where grams are known (UNKNOWN otherwise); … | A 10-16 / H 0 | manjot | only if Q39 says "do the slice" |
| T4-C05-R3 | Q1 circularity control: basis masks on every Layer 2 feature plus an ablation that removes Layer 2 before any use in Steps 30-35 (lean b of … | A 3-5 / H 1 | any | before any Layer 2 use in learning |
| T6-C04-R1 | Decide and pre-register the H2 operational test: which row sets, splits (S-2 pair, S-3 matrix, S-6 study), margin delta_H2, K_min, who may … | A 2-3 / H 1-2 | human | with the 29-diag signature |
| T7-C20-R1 | Write the explicit statement 'learned rungs deferred; entry rule LR-1..LR-5' into the 35h record and talk (limitation slide). | A 1 / H 0.5 | human | report, 19-21 Nov |
| T7-C08-R1 | Decide and document ingredient-level SENSORY as UNSUPPORTED for 25 Nov (talk wording) and keep structural != sensory as a stated boundary. | A 1 / H 0.5 | human | decision sitting 10-12 Nov |

COULD items are done only if an agent is idle and no human hours are needed; T2-C05-R7 (planted errors) is allowed only inside the 10 Nov lock (C06).

### 4.4 CUT for 25 Nov (explicit)

- All **AFTER** items (section 5): 110 items.
- All **OUT_OF_SCOPE** components (20): T0-C10 Decision formulation and recovery (RQ3/RQ4, feasible-action …; T0-C16 Levels 12-17 frozen status and legacy invariants; T2-C20 Raw-vs-cooked volatile literature anchors and platform …; T3-C19 Scale procedural corpus (T0 weak corpus, T1 Silver 1k-10k, …; T4-C24 Learned numerical embeddings, dense trajectory encoders, …; T5-C16 Hybrid mechanistic-neural models and UDE (D9, D10, D11, …; T5-C17 Reaction-network learning (species graph, stoichiometric …; T5-C18 Counterfactual and inverse design (forward credibility …; T5-C19 Rollout trust horizon and open-system balance (R0-R5, …; T5-C20 E7 synthetic prior generator (Step 28) and simulator …; T6-C12 Step 31 (learning side): physics/condition features …; T6-C14 Step 33: mechanistic vs ML vs hybrid three-arm comparison …; T6-C16 Synthetic-data tiers and synthetic-prior pretraining …; T6-C17 Active learning, value of information, acquisition design, …; T6-C18 Neural / probabilistic transition models (D10, D11) and …; T7-C20 Level 12 learned rungs and fusion: z_m encoders (GNN, …; T7-C21 Level 13 learned recipe/cuisine encoders: R4-R9, objectives …; T7-C26 Level 13E extended models: fitness/context fitness …; T7-C27 FlavorTwin boundary, cultural prior and historical RAG …; T9-C19 Hypothesis H4 / feasibility filter and recovery (proposal ….
- H8 scope register (T9-C07-R4, to be signed): D2, the full H2 test, H4, Steps 20/28/33/34, FlavorTwin.
- If the agent leans are accepted: Step 35 runs (DESIGNED, NOT RUN, T7-C01-R2); lot-state beyond a minimal slice (Q39, T3-C22-R7); Level 13E (T7-C24-R1); SEMANTIC branch answers (explicit abstention, T8-C02-R2).
- All neural training, learned encoders, GPU work other than the D5/H1 ladder; all new literature corpora (13a) and new database downloads (FDC Foundation, CoFID, Flavonoid DB).
- No claim words without a gate: "validated", "calibrated", "supported", "beats" (C04).

## 5. After 25 Nov (paper backlog)

110 AFTER items. The paper angle itself is a decision (T9-C23-R1, COULD: RAG paper §253.4 vs dataset §253.3 vs transition §253.5). Order of value for a paper: first finish the evidence plane properly (07.A valid pass, 15b freeze, Step 11 wave-1 rows), then H2 paper-grade, then D2, then learned models.

### T0 — SSOT core, laws, router, output contract (7)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T0-C05-R6 | Steps 28,31-34 (E7 prior, features at scale, hybrid, rollout) and learned heads for L2/L3. | TRAINING; GPU_COMPUTE | A 40-80 / H 5+ | vinayak |
| T0-C08-R3 | Vision/audio branch. | TRAINING | A - / H - | vinayak |
| T0-C10-R2 | Recovery benchmark and state-distance model. | TRAINING; ANALYSIS; EXPERT_REVIEW | A 30-50 / H 10+ + expert | vinayak |
| T0-C11-R5 | Locked-tier benchmark (240) and Tasks 3,5,7. | WRITING; HUMAN_REVIEW | A 10-15 / H 55-80 split | human |
| T0-C14-R2 | Learned encoders / embeddings of ingredient-state (GPU). | TRAINING; GPU_COMPUTE | A 20-40 / H 2 | vinayak |
| T0-C15-R2 | Similarity sensitivity pass (raw/Jaccard/Ochiai/IDF/chance-adjusted) on the cuisine conclusion. | ANALYSIS; CPU_COMPUTE | A 6-10 / H 0 | manjot |
| T0-C16-R2 | Level 12-16 empirical programmes. | TRAINING; GPU_COMPUTE; ANALYSIS | A 100+ / H 20+ | vinayak |

### T2 — Evidence plane (EVD/COND, 07.A, lineage, AA extraction, D1) (17)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T2-C04-R2 | Define the condition-bucket scheme per process family (bin edges for T, t, pH, a_w; treatment of INTERVAL/QUALITATIVE) | WRITING; DECISION | A 3-6 / H 1-2 | any |
| T2-C04-R3 | If 07.A-R1 fails: repair normaliser as 07H.v2 with full regression and issue packet v5 | CODE; ANALYSIS | A 8-24 / H 1-2 | any |
| T2-C06-R3 | Optional detector rework and a second 150-edge human audit as a NEW version (08a.1); D-034 says no retune of v1 | CODE; HUMAN_REVIEW | A 8-16 / H 2-4 each | any |
| T2-C06-R4 | Capture lab/author groups and study design for the PE 125 papers (needs reading of papers, library access) | DOWNLOAD; HUMAN_REVIEW | A 3-6 / H 10-30 | human |
| T2-C08-R4 | Figure digitisation tooling (DIGITIZED value_origin with tool/version/uncertainty) | CODE | A 6-12 / H 0-0 | any |
| T2-C09-R8 | Chlorophyll (sim_chl_1) second system: extraction and comparison per R-14 | ANALYSIS; HUMAN_REVIEW | A 8-16 / H 3-6 each | any |
| T2-C10-R5 | 11b breadth: mechanism/negative/conflict rows for the 32 MECH entries (>=10 negative, >=3 conflict candidates), partition lock | ANALYSIS; HUMAN_REVIEW; EXPERT_REVIEW | A 40-80 / H 40-80 Kush; 30-60 Parv; 10-20 expert | human |
| T2-C11-R3 | Ingest R2 + Bognar remaining tables after audit sample >=75 rows per source with 0 transcription errors and H2 decisions | CODE; HUMAN_REVIEW | A 8-16 / H 4-8 Kush; 4-8 Parv | any |
| T2-C11-R4 | Download/stage FDC Foundation Foods, Flavonoid DB 3.3, UK CoFID after licence confirmation | DOWNLOAD; DECISION | A 3-6 / H 0.5-1 | manjot |
| T2-C12-R2 | 13a metadata-only discovery for AA and chlorophyll systems: query log, licence/OA status per DOI, 100 abstracts double-labelled | DOWNLOAD; ANALYSIS; HUMAN_REVIEW | A 6-12 / H 3-6 each | manjot |
| T2-C12-R3 | Full 13a corpus with propensity universe and known-item recall >= 0.90, then triage classifier decision | DOWNLOAD; CPU_COMPUTE; ANALYSIS | A 20-40 / H 6-12 each | manjot |
| T2-C13-R3 | Active acquisition scheduler with random stream >= 30% and stop rules, acquisition log | CODE; DOWNLOAD | A 16-40 / H 40-120 each | any |
| T2-C16-R2 | Actual 15b freeze (verified test subset, sealed locked test H5, release licence matrix) | HUMAN_SIGNATURE; CODE; HUMAN_REVIEW | A 16-24 / H 12-20 Kush; 6-13 Parv; 2-3 expert | any |
| T2-C18-R2 | Send permission/terms emails (H1 Bagler: RecipeDB/FlavorDB keys; INFOODS; IFCT; Phenol-Explorer authors; CoSyLab written confirmation) | HUMAN_SIGNATURE; DECISION | A 1-2 drafting / H 1-2 | human |
| T2-C18-R3 | Register local unregistered files into SRC/SNAP (12.0) with orchestrator minting ids | CODE | A 2-4 / H 0-0 | any |
| T2-C19-R2 | Implement conflict-record builder with compatibility checks and human adjudication states | CODE | A 6-10 / H 1-2 review | any |
| T2-C20-R1 | Defer: curate 5-7 anchor foods (onion, garlic, potato, tomato, chicken, beef, coffee) matched raw-vs-cooked volatile studies with platform recorded | DOWNLOAD; ANALYSIS; HUMAN_REVIEW; EXPERT_REVIEW | A 20-40 / H 20-40 each | human |

### T3 — Recipe semantics and state tracking (Rung A, replay, NER, lot state) (7)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T3-C02-R2 | Outside expert (food scientist / culinary annotator) sample check of handbook state attributes (cooked, cut, hydrated) for 10-20 events | EXPERT_REVIEW | A 1 / H 1-3 expert | human |
| T3-C11-R5 | Rung B/C extraction cascade (local LLM + V1-V6 + two-model disagreement + confident learning) | CODE; GPU_COMPUTE; TRAINING | A 40-80 / H 0 | vinayak |
| T3-C18-R1 | 19-S sizing decision from measured P1/P1b throughput (NEED_HUMAN_CAPACITY if too low) | DECISION; ANALYSIS | A 1 / H 1 | human |
| T3-C18-R2 | Annotate Deep-Gold cohort (fallback 20 recipes at depth A2) and adjudicate | HUMAN_REVIEW | A 8-12 (tooling, packets) / H 40-100 (UNVERIFIED) | human |
| T3-C19-R2 | §257P checklist status report for Step 20 gates | WRITING; ANALYSIS | A 3-4 / H 0 | any |
| T3-C19-R3 | H2 licence decision for Food.com / TASTEset / A1 (LLM processing, training) | DECISION; HUMAN_SIGNATURE | A 0.5 / H 1-2 | human |
| T3-C19-R4 | T1 Silver pilot 1k -> 5k -> 10k (LLM cascade) with batch audits | GPU_COMPUTE; TRAINING; HUMAN_REVIEW | A 40-80 / H 30-60 audit labels (UNVERIFIED) | vinayak |

### T4 — Process conditions and physics (Layer 1 / Layer 2, non-heat) (13)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T4-C01-R3 | Map PROC leaves to FoodOn/LanguaL process terms as a side table (no replacement of the custom hierarchy) | CODE; DOWNLOAD | A 4-8 / H 0 | any |
| T4-C15-R1 | Build driver + scenario defaults + Layer 1 binding for PRESERVATION family and unit tests | CODE; ANALYSIS | A 6-12 / H 0.5 | any |
| T4-C15-R2 | Full non-BBC corpus run and counts-only report for PRESERVATION family with run-log rows | CPU_COMPUTE | A 1-2 / H 0 | vinayak |
| T4-C17-R1 | Build driver + scenario defaults + Layer 1 binding for MECHANICAL_MIX family and unit tests | CODE; ANALYSIS | A 2-4 / H 0.5 | any |
| T4-C17-R2 | Full non-BBC corpus run and counts-only report for MECHANICAL_MIX family with run-log rows | CPU_COMPUTE | A 1-2 / H 0 | vinayak |
| T4-C19-R1 | Build driver + scenario defaults + Layer 1 binding for STORAGE family and unit tests | CODE; ANALYSIS | A 6-12 / H 0.5 | any |
| T4-C19-R2 | Full non-BBC corpus run and counts-only report for STORAGE family with run-log rows | CPU_COMPUTE | A 1-2 / H 0 | vinayak |
| T4-C19-R3 | Storage kinetics entry through Step 32 PARAM for one system (likely ascorbic acid at storage T) | TRAINING; HUMAN_REVIEW | A 4-8 / H 2-4 | manjot |
| T4-C22-R3 | Build physics_feature_registry_v1.csv and 31a feature code (raw, log(1+t), 1/T_K, bounds, dose, time above threshold) inside Step 30 harness | CODE | A 8-12 / H 0 | any |
| T4-C22-R4 | Run condition-contribution ablation A1..A5 with paired cluster CIs; pre-registration signed by Kush | TRAINING; CPU_COMPUTE; HUMAN_SIGNATURE | A 8-14 / H 3 | manjot |
| T4-C22-R5 | Expert review of Ea grid, temperature semantics (setpoint vs product) and heat-mode map | EXPERT_REVIEW | A 0 / H 4 | human |
| T4-C23-R2 | If added: altitude-dependent boil T and oven offset parameter in scenario layer | CODE | A 2-3 / H 0 | any |
| T4-C24-R1 | Revisit after G15-2 passes and focused kinetic data exist | DECISION | A 0 / H 0.5 | human |

### T5 — Mechanisms, kinetics, simulation (AA pilot, router SIMULATE) (12)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T5-C01-R7 | Mechanism xref table (SBO/GO/ChEBI/KEGG/FoodOn) with collision audit; 0 xrefs ACCEPTED without a human. | DOWNLOAD; CODE; HUMAN_REVIEW | A 4-8 / H 2-3 | any |
| T5-C04-R3 | Author signature rules from non-test cases and run G22.1-G22.5 (recall>=0.90 Wilson LB>=0.80, B1 precision>=B0, process-label permutation drop>=0.30, … | CODE; ANALYSIS | A 8-12 / H 1 | any |
| T5-C04-R4 | Freeze EFFSIG schema and generate 22b event candidate export over the corpus (regenerable). | CODE; CPU_COMPUTE | A 3-5 / H 0.5 | vinayak |
| T5-C05-R5 | Pre-register false-activation tolerance and B0/B2 baselines; prepare locked test set from Step-11 verified positives/negatives labelled by someone … | DECISION; HUMAN_REVIEW; EXPERT_REVIEW | A 3-5 / H 6-10 + expert 6-10 | human |
| T5-C13-R4 | Collect >=5 independent lab groups of AA kinetic series for a formal VALIDATED_HELD_OUT (new sources, new verification). | DOWNLOAD; HUMAN_REVIEW | A 10-20 / H 8-12 | any |
| T5-C14-R1 | Only if AA fails: 11.D record then chlorophyll literature sweep (K1/K2 series, pH-controlled). | DECISION; DOWNLOAD; ANALYSIS | A 10-20 / H 3-5 | any |
| T5-C15-R2 | Check licence and scope of Phenol-Explorer time/temperature rows as a second K1 source (non-AA). | ANALYSIS; DECISION | A 2-4 / H 0.5 | any |
| T5-C16-R1 | After Step 27 VALIDATED_HELD_OUT: endpoint-residual hybrid first, three-way benchmark, residual-off ablation, //f_NN// vs //f_known//. | CODE; TRAINING; GPU_COMPUTE | A 30-60 / H 3-5 | vinayak |
| T5-C17-R1 | Known-pathway rate fitting A->B->C only if a multi-species AA series (AA, DHA, DKG) is found; randomized-topology and leave-one-reaction controls. | DOWNLOAD; TRAINING; ANALYSIS | A 20-40 / H 2-4 | any |
| T5-C18-R2 | Full inverse design (grid, random, LCB, Pareto) within safe support region. | CODE; GPU_COMPUTE | A 30-50 / H 3-5 | vinayak |
| T5-C20-R1 | Generate DATA-SIM v1 only from a VALIDATED_HELD_OUT simulator; firewall tests; C-7 span check; ablation controls spec. | CODE; CPU_COMPUTE | A 10-16 / H 3-5 | vinayak |
| T5-C21-R3 | Add delta-compatibility type to SVAR design (state-semantics topic owns); here only request. | DECISION | A 0 / H 0.5 | human |

### T6 — Transition learning and sparsity (29-diag, H2, D2) (29)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T6-C01-R2 | Add missing mask/weight metadata (replicate n, SD/range, yield or normalisation status RT-004 resolution, year, platform) to the EVD export view used … | CODE; ANALYSIS | A 4-8 / H 0 | any |
| T6-C01-R3 | Expert check of retention basis (TR vs AR, fresh vs dry weight) and the cap semantics 'values >100 reported as 100' / Bognar '1.00' for G15-1 and … | EXPERT_REVIEW | A 0 / H 2 | human |
| T6-C04-R2 | Run paper-grade H2 on DATA-EVIDENCE v1 (after 15b freeze + valid 07.A) with study-level bootstrap CIs; report negative result if so. | CPU_COMPUTE; TRAINING; ANALYSIS | A 6-10 / H 2 | mac |
| T6-C05-R1 | Draft 29.0 pre-model audit, 29.1 crosswalk, 29.2 prereg amendment (K_min, G29-A) and 29.3 engineering preconditions as DRAFT documents; SPLIT.jsonl … | WRITING; CODE | A 6-10 / H 0 | any |
| T6-C05-R3 | Run D0-D5 on S-1..S-6 on frozen DATA-EVIDENCE v1, twice, with cluster-bootstrap paired CIs; write v0_results.md and decision_record_v0.md. | CPU_COMPUTE; TRAINING; ANALYSIS; WRITING | A 4-6 / H 1 | mac |
| T6-C05-R4 | Kush signs amendment and decision record; Parv authorises Python environment. | HUMAN_SIGNATURE | A 0 / H 1-2 | human |
| T6-C06-R1 | Pre-register Step 30.0: delta_30, K_min, bootstrap vs sign-flip cut-off, eligible splits, D6 activation rule; commit … | DECISION; WRITING; HUMAN_SIGNATURE | A 2-3 / H 1-2 | human |
| T6-C06-R2 | Implement D3-full (hierarchical shrinkage over food class, process family, target class, study) as numpy/statsmodels-free partial pooling; unit tests … | CODE; TRAINING | A 6-10 / H 0 | any |
| T6-C06-R4 | Train D5-tuned (LightGBM/XGBoost, grouped CV for hyperparameters, censored/AFT or interval objective arm) and D6 TabPFN (CPU, <=7k rows per source) … | TRAINING; CPU_COMPUTE | A 6-12 / H 0 | vinayak |
| T6-C06-R5 | Write §221.18 9-item completion audit, §222.10 anti-inflation report, G30-B/C decision records, MODEL.jsonl card drafts. | ANALYSIS; WRITING | A 6-10 / H 2 | any |
| T6-C07-R2 | Implement D7e soft-impute, D7b BPMF/Gibbs (numpy), D7d factorisation machine with side features (food group, FDC composition vector, process family, … | CODE; TRAINING | A 12-24 / H 0 | any |
| T6-C07-R3 | Run §221.18 protocol: masked real cells, cold food, cold process, cold target (PE only), cold pair, study-disjoint (PE), frequency buckets, coverage; … | CPU_COMPUTE; TRAINING; ANALYSIS | A 8-16 / H 0 | vinayak |
| T6-C07-R4 | Kush signs G15-9 decision record; a REJECT is a valid outcome (R-20: negative results visible). | HUMAN_SIGNATURE | A 0 / H 1 | human |
| T6-C08-R2 | Frequency/support-bucket error report (does the model work only on popular cells?) and with/without mask-indicator ablation. | CODE; ANALYSIS | A 3-5 / H 0 | any |
| T6-C09-R1 | Censored training arm (interval/Tobit objective in a small numpy fit and in AFT-capable GBDT) and cap-drop arm; compare on S-3/S-4 as DIAGNOSTIC. | CODE; TRAINING; CPU_COMPUTE | A 4-8 / H 0 | any |
| T6-C10-R1 | Implement group-disjoint split-conformal (calibration roles from group_aware_split) plus weighted/Mondrian sensitivity and risk-coverage curves; … | CODE; CPU_COMPUTE; ANALYSIS | A 6-10 / H 0 | any |
| T6-C10-R2 | Write c9_transition_fallback_spec (when the router may offer a calibrated model estimate vs ABSTAIN) consistent with section 141 contract; consumed … | WRITING; DECISION | A 2-3 / H 1 | any |
| T6-C11-R2 | Full D2: freeze FoodProc-ColdStart split manifests, run C02/C06/C07/C08/C10 stack, write D2 report with study-level CIs and negative results. | CPU_COMPUTE; TRAINING; ANALYSIS; WRITING | A 30-50 / H 6-10 | vinayak |
| T6-C11-R3 | Confirm licence/terms for releasing derived non-raw benchmark manifests (USDA public domain; Bognar citation; Phenol-Explorer terms). | HUMAN_REVIEW; DECISION | A 0.5 / H 1-2 | human |
| T6-C12-R1 | Define physics_feature_registry_v1 (log(1+t), 1/T_K, Omega with Ea grid) with source row ids; Layer 2 excluded by construction. | CODE; WRITING | A 4-6 / H 0 | any |
| T6-C12-R2 | Run A3/A4/A5 ablation on identical row sets, cooking stratum (PE conditions), paired cluster CIs; Kush signs prereg; expert reviews Ea grid and … | CPU_COMPUTE; TRAINING; ANALYSIS; HUMAN_SIGNATURE; EXPERT_REVIEW | A 6-10 / H 3 + expert 4 | vinayak |
| T6-C13-R4 | KA0-KA6 model-form ablation, hierarchical fit (PyMC/NumPyro or custom), G15-4 record, expert review of forms and plausibility. | TRAINING; CPU_COMPUTE; EXPERT_REVIEW; HUMAN_SIGNATURE | A 15-25 / H 4 + expert 8-12 | vinayak |
| T6-C14-R1 | Pre-register three-arm test (M, ML, H=sequential residual) with Holm correction and physical-consistency alternative; run only after G15-4 PASS. | DECISION; WRITING; TRAINING; CPU_COMPUTE | A 15-25 / H 4-6 | any |
| T6-C15-R2 | Kush supplies tau, eps_max, h_trust ids and STOP/DOWNGRADE actions and signs the 34c abstention spec (consumed by Step-36 tests; D4/D5 topic). | DECISION; HUMAN_SIGNATURE | A 0.5 / H 1-2 | human |
| T6-C15-R3 | Search for staged cooking datasets with measured intermediates (raw -> pretreat -> dry -> fry) for 34b. | DOWNLOAD; ANALYSIS | A 2-4 / H 1 | human |
| T6-C15-R4 | Broader §212 stack: semigroup and repeated-process tests on supported subsets, merge/split transitions, state-space baselines, MC/ensemble rollout, … | CODE; TRAINING; ANALYSIS | A 30-60 / H 0 | any |
| T6-C16-R2 | After Step 27 PASS only: generate DATA-SIM v1, run ratio sweep and TSTR with real study-disjoint test, plus controls. | CPU_COMPUTE; TRAINING; ANALYSIS | A 20-40 / H 4 | vinayak |
| T6-C17-R1 | Simulated active-learning demo on a known kinetic system (random vs factorial vs info-gain; number of experiments to stable k, Ea), stating the … | CODE; CPU_COMPUTE; ANALYSIS | A 8-14 / H 0 | any |
| T6-C18-R1 | After D0-D7 decision records: one residual-MLP / FiLM ablation with GPU env (vinayak A100; torch setup on manjot GPU 1 if wanted) only if gates … | TRAINING; GPU_COMPUTE | A 10-20 / H 0 | vinayak |

### T7 — Representations and similarity (Step 35, Levels 12-13) (16)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T7-C03-R4 | Odour-label tasks and OpenPOM-style reproduction (SSOT L11036 mandatory comparator for any molecule-level odour claim): acquire GS-LF/Keller/Pyrfume … | DOWNLOAD; GPU_COMPUTE; TRAINING | A 20-40 / H 1-2 (licence call) | vinayak |
| T7-C04-R4 | Run E2/E3 rungs on the 603 taste-labelled molecules with scaffold split; report OOD gap (random minus scaffold) vs E1 baseline. | CPU_COMPUTE; ANALYSIS | A 3-6 / H 0 | mac |
| T7-C08-R2 | Acquire an odour/taste-threshold compilation and sensory panel labels (source and licence to be selected; none verified here) to enable OAV and … | DOWNLOAD; HUMAN_REVIEW | A 6-10 (after source chosen) / H 2 (licence) | manjot |
| T7-C10-R2 | Implement raw-vs-cooked discrimination on study-disjoint EVD with matrix-shuffled control, static vs process-response comparison on a held-out … | CODE; ANALYSIS | A 12-20 / H 0 | any |
| T7-C13-R4 | Novelty measure beyond rarity (set/quantity/process/density components; expert-aligned signal after rarity and source controls, G13E-08); needs a … | CODE; EXPERT_REVIEW | A 8-12 / H 3-6 (expert) | any |
| T7-C14-R3 | Expert review of C1/C2 definitions (triplet NPMI generalisation, K-1 vs C-1, support thresholds 20/10). | EXPERT_REVIEW | A 1 / H 2-3 | human |
| T7-C18-R1 | Commission 200-300 blind two-annotator substitution pairs with recipe context (needs food-literate annotators; Kush/Parv as annotators carries … | HUMAN_REVIEW; EXPERT_REVIEW | A 4 (build packets) / H 8-15 (expert) or Kush/Parv time | human |
| T7-C18-R2 | Baselines (co-occurrence-context kNN, LLM zero-shot via Ollama) on the frozen set. | CODE; GPU_COMPUTE | A 8-12 / H 0 | vinayak |
| T7-C20-R2 | Post-course: encoder bake-off on taste task (frozen pretrained + linear probe, GNN at matched capacity, label-prior), only if an explicit rung leaves … | TRAINING; GPU_COMPUTE; DOWNLOAD | A 60-120 / H 4-8 | vinayak |
| T7-C20-R3 | Post-course: set-aggregator and multi-view fusion comparison (G7, G5, G12-DEC-3..7) after OAV/threshold data exist. | TRAINING; GPU_COMPUTE | A 80-160 / H 4 | vinayak |
| T7-C21-R1 | Post-course: Phase 1 recipe-set encoder bake-off (mean vs Deep Sets vs attention at parameter-matched control) on licence-cleared recipes; … | TRAINING; GPU_COMPUTE | A 60-100 / H 2-4 | vinayak |
| T7-C21-R2 | Post-course: objective bake-off (same-recipe multi-view contrastive, masked ingredient, cuisine supervised) with non-circular secondary evaluation … | TRAINING; GPU_COMPUTE | A 80-140 / H 3-5 | vinayak |
| T7-C25-R2 | Kinouchi M1 exact copy-mutate reproduction and M2 category-constrained variant (G13E-04/05). | CODE; CPU_COMPUTE | A 20-30 / H 0 | any |
| T7-C26-R1 | Park: record in the roadmap as post-course; no work before 25 Nov. Reopen only if a dated, source-diverse corpus is acquired. | DECISION | A 0 / H 0 | human |
| T7-C26-R2 | Post-course: acquire dated historical corpora (RELISH, Open Recipe Archive, historical cookbooks; licences unverified here) and run E3-E6. | DOWNLOAD; CPU_COMPUTE; TRAINING | A 80-200 / H 6-12 | vinayak |
| T7-C27-R2 | Post-course: FlavorTwin static -> process-conditioned prototype and separable cultural reranker (E13E-17). | CODE; TRAINING; GPU_COMPUTE | A 80-160 / H 4-8 | vinayak |

### T8 — Application layer (RAG, D4/D5, H1/H3, demo) (6)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T8-C05-R2 | H4 feasibility/recovery evaluation (§245.9, .11) | CODE; ANALYSIS; HUMAN_REVIEW | A 10-20 / H 4-6 | any |
| T8-C09-R1 | Candidate Recall@K and diagnosis Recall@K benchmark (DEC/DIAG/REC families) | ANALYSIS; HUMAN_REVIEW | A 8-16 / H 4-6 | any |
| T8-C12-R3 | Calibrated recommend/ask/abstain model (Platt/isotonic) on independently verified labels | TRAINING; HUMAN_REVIEW; ANALYSIS | A 6-10 / H 8-12 | manjot |
| T8-C14-R2 | Full VOI benchmark | CODE; ANALYSIS; HUMAN_REVIEW | A 10-15 / H 4-6 | any |
| T8-C16-R3 | Qualitative/directional claim checker (e.g. 'leaches') against mechanism registry | CODE | A 4-6 / H 0 | any |
| T8-C23-R2 | Remaining families (DEC/DIAG/REC/FT) benchmark | CODE; HUMAN_REVIEW; ANALYSIS | A 20-40 / H 8-12 | any |

### T9 — Governance, evaluation design, deliverables, timeline (3)

| Id | What | Work types | Effort | Host |
|---|---|---|---|---|
| T9-C09-R4 | Study-disjoint / pair-holdout / ingredient-disjoint splits for D2 (needs 15a freeze, independence_group join) | CODE; ANALYSIS | A 4-6 / H 0 | mac |
| T9-C15-R2 | Full D2 benchmark (pair-holdout, ingredient-disjoint, study-disjoint, propensity-weighted metrics, conformal) | CODE; CPU_COMPUTE; ANALYSIS | A 12-20 / H 1 | vinayak |
| T9-C23-R3 | Food-science / chef review of a subset of answers and mechanism windows (outside expert) | EXPERT_REVIEW | A 1-2 / H 2-4 expert | human |

## 6. HUMAN DECISIONS needed

### 6.1 From the contested items

**None left.** All 9 contested issues (C01-C09) got 3/3 AGREE in round 2 (R-FEAS, R-SCI, R-SSOT), so each became AMENDED-UNANIMOUS and was applied to the ledger (section 7). The C02 fallback ("use R-FEAS's ids if anyone objects") was not needed. Humans still own the gates these items touch. Two of them put text into the 10 Nov edit lock: the D5 VPN-fallback sentence (C07) and the optional 07.A-R1 planted-error design (C06, COULD).

### 6.2 Decisions due 9-12 Nov (MUST, or blocking a MUST)

The agent drafts each one as a DECISIONS entry with a recommended option. Kush and Parv choose. The agent never records a choice as made (D-071).

| # | Id | Decision | Options | Agent / reviewer lean | Due |
|---|---|---|---|---|---|
| 1 | T3-C22-R7 | Q39: lot-state layer before 25 Nov? | (a) defer to stretch; (b) minimal slice only (lot members + presence-only composition, T3-C22-R1) if an agent is idle; (c) full layer [K] (ranked #1 in the packet, but it competes with H1/H3 and the first SIMULATE) | (a), R-FEAS | 9 Nov |
| 2 | T2-C05-R5 | 07.A gate statistic: plan card R-06 (kappa gate, AC1 diagnostic only) vs the R1 prereg's gate | (a) keep kappa as the gate, AC1 diagnostic; (b) gate on AC1 as a named, pre-registered deviation on the fresh R1 packet, with the v4 FAIL kept on record | either is valid if decided **before** signing; R-SCI: (b) only as a recorded deviation | 9 Nov |
| 3 | T7-C01-R2 | Step 35 for the course | (a) DESIGNED, pre-registered, NOT RUN; (b) sign and run descriptive explicit rungs (35a-lite, 35b PRESENCE, 35c R0/R2, 35d, 35e registry) | (a), R-FEAS | 10 Nov |
| 4 | T8-C06-R2 | Embedding for rungs B1/B2 | (a) bge; (b) e5-large-v2 | agent proposes in the lock; one model named in the signed prereg | 10 Nov |
| 5 | T8-C12-R1 | H3/B7 wording | (a) "rule-based evidence-sufficiency abstention (uncalibrated)", no calibration claim; (b) keep the current wording and add a calibration study (not feasible before 25 Nov) | (a), R-FEAS | 10 Nov |
| 6 | T9-C12-R1 + T8-C04-R2 | Power/MDE note for H1/H3 and the H1 circularity caveat in the prereg | (a) add both before signing; (b) sign without them (a null result then reads as "untested") | (a) | 10 Nov |
| 7 | T6-C03-R5 | Add the D2-process-mean vs D3-ingredient-mean contrast to the 29-diag prereg | (a) add it before signing; (b) leave it out, so any contrast is EXPLORATORY and cut | (a), R-FEAS/R-SCI | 10 Nov |
| 8 | T0-C06-R1 | Freeze the mode-to-§141 crosswalk (DIRECT/INTERPOLATE → evidence_supported with EVD ids; SIMULATE/SCENARIO/QUALITATIVE → physically_possible; UNKNOWN/ASK/ABSTAIN → unsupported) | (a) approve as written; (b) amend | (a) | 11 Nov |
| 9 | T5-C07-R1 | Id prefix and schema freeze for formulas | (a) FORM- and freeze FORM/PARAM/VAL; (b) MODEL- | decide before PARAM minting on 16 Nov | 12 Nov |
| 10 | T5-C13-R3 | Accept descriptive pilot validation (D-076) instead of the formal gate | (a) accept, record the deviation, sim_aa_1 stays NOT_VALIDATED / RESEARCH_ONLY, VAL-5 NOT_MET; (b) no SIMULATE result in the talk | (a), R-SCI: the label never moves | 12 Nov |
| 11 | T3-C17-R1 | D3 claim at the talk | (a) diagnostic on P1 (7 recipes) plus P1b if signed, with intervals and caveat; (b) no D3 accuracy claim, "built and run" only | (a) with explicit n, or (b) if P1b is not signed | 12 Nov |
| 12 | T5-C05-R4 | Q20 (is "mostly UNKNOWN" a result?), Q22 (what counts as bracketing), Q23 (ASK rule) | yes/no and a rule for each | Q20 yes (it is the main finding) | 12 Nov |
| 13 | T3-C07-R3 | Food.com lines with no units | (a) presence-only composition; (b) find the original data with units (download, H2 licence gate); (c) flagged imputation | (a) for 25 Nov | 12 Nov |
| 14 | T3-C04-R3 | SR Legacy as portion/composition authority | (a) yes, under new basis codes (SR_PORTION); (b) strict HUMAN_VERIFIED rule of rc2 | moot if Q39 = defer | 12 Nov |
| 15 | T4-C09-R1 | Two-zone surface model | (a) QUALITATIVE only; (b) stated limitation for 25 Nov | (b) | 12 Nov |
| 16 | T4-C22-R1 | How Layer 1/2 enter Step 31 | (a) EVD-row arm only (as planned); (b) add a recipe-event diagnostic arm with Layer 2 masked | (a); Step 31 is AFTER anyway | 12 Nov |
| 17 | T8-C02-R2 | SEMANTIC branch | (a) explicit abstention, stated in the demo and report; (b) build it (no time) | (a) | 12 Nov |
| 18 | T9-C07-R4 | H8 scope-cut register | sign the drop/defer of D2, the full H2 test, H4, Steps 20/28/33/34, FlavorTwin | sign | 12 Nov |
| 19 | T9-C07-R2 | Prof. Bagler's permission for the D-045 AI-first workflow | (a) store a written copy (email/screenshot); (b) report says "as stated by Kush" | (a) | 12 Nov |
| 20 | T9-C25-R5 (SHOULD) | Install authorisation per host (hypothesis, sklearn, lightgbm, …) | (a) pinned installs in a Mac venv only; (b) also on manjot; (c) none, so T5-C05-R1 and the hypothesis tests are reported NOT_RUN | (a); it unblocks T5-C05-R1 and T6-C03-R3 | 10 Nov |
| 21 | T9-C25-R3 (SHOULD) | VPN/route to vinayak | confirm ssh works, or accept the manjot-CPU fallback now | confirm by 13 Nov | 13 Nov |
| 22 | T0-C01-R1 (SHOULD) | Q40: apply the SSOT v16 change set before 25 Nov? | (a) do not apply, ship a one-page "SSOT v15 vs current state" delta; (b) apply v16 | (a) | 12 Nov |
| 23 | T9-C26-R1 | Kush's calendar for 9-16 Nov (availability to be stated by Kush and Parv) | confirm or correct | needed for the schedule | 10 Nov |

### 6.3 Human signatures (never AI; D-071)

| Id | What | Who | When |
|---|---|---|---|
| T2-C05-R1 | 07A_R1 pre-registration | Kush + Parv | 10-11 Nov, before opening the packet |
| T2-C09-R1 | AA pilot pre-registration | Kush + Parv | 10-11 Nov, before any verification |
| T8-C20-R1 | D5 / H1 / H3 pre-registration | Kush + Parv | 10-11 Nov |
| T6-C03-R1 | 15A-BOOT freeze record | Kush | 10-11 Nov |
| T6-C03-R2 | 29-diag pre-registration | Kush | 10-11 Nov, after the rung-label fix T6-C02-R1 |
| T9-C07-R4 | H8 scope-cut register | Kush (+ Parv) | 12 Nov |

Other signature items are SHOULD or AFTER (for example T3-C16-R1 P1b start record, T3-C01-R2 16c freeze, T5-C11-R1 G26 prereg). They are in sections 3.8 and 5.

### 6.4 Other SHOULD/COULD decisions (decide only if time allows; the agent's default holds otherwise and is stated in the report)

T0-C17-R1 professor endpoint terms; T0-C18-R2 D-071 line in DECISIONS (Q37); T2-C02-R1 storage form for AA rows; T2-C03-R1 SVAR v1.1 set; T2-C04-R1 07.B/07.C axes; T2-C11-R2 R2 + Bognar ingestion order vs the 15a freeze; T2-C18-R1 H2-queue rulings (Europe PMC, NCBI, Unpaywall, CoFID, Food.com); T3-C16-R1 P1b size and nonce; T3-C25-R1 belief-field design note; T4-C05-R3 Layer 2 circularity control; T5-C01-R4 MECH schema decisions D21-1..8; T5-C02-R4 Q21 QUALITATIVE from unreviewed MECH; T5-C11-R1 G26 numbers prereg; T6-C04-R1 H2 operational test (diagnostic-only for 25 Nov); T7-C01-R3 / T7-C04-R1 / T7-C16-R1 open D35 items (RDKit, Open Babel, sim_id); T7-C08-R1 sensory UNSUPPORTED wording; T7-C20-R1 "learned rungs deferred" statement; T7-C24-R1 park L13E; T8-C07-R1 conflicting-evidence display; T8-C08-R1 B6 SIMULATE rung; T8-C18-R1 hosting and LLM path; T9-C06-R2 claim ledger; T9-C07-R1 H3 compute threshold; T9-C07-R5 H7 repo visibility. The COULD decisions are listed in section 3.11.

### 6.5 Open questions carried from round 1 (CONSENSUS_DRAFT §8)

| Question | Options | Lean |
|---|---|---|
| Merge promotions (highest alias wins): T2-C01-R2, T2-C18-R1, T3-C20-R2 → SHOULD; T9-C23-R2 → MUST | keep or demote | keep T9-C23-R2 MUST (cheap, 1 agent h); T3-C20-R2 could drop back to AFTER (it needs a human-labelled pair sample) |
| RUN claims without a run-row id (Rung A, rc2, replay / 26g census; NER has RUN-S174-003) | (a) back-fill rows (T9-C11-R2, SHOULD) before the report; (b) cite report paths only and say so | (a), orchestrator-only edit |
| T3-C04 / T3-C22 / T4-C08..C16 status: untracked lane code exists (`src/culinarystate/lotstate/`, `nonheat_drivers.py`, `registry/food_ph_fda_draft_v1.csv`) | re-grade when the S176 lane reports arrive | only `S176_L-PH_report.md` exists today; statuses stay DRAFT/CODE until the reports arrive |
| No T1 topic file | confirm T1 was merged into T0 | confirm |
| T8-C16-R1 (MUST) adds 1-1.5 h of blind judging per person on 17-19 Nov | accept, or cut to a 15-claim sample | it is in the section 4 schedule; record it in the T9-C26-R4 human-time ledger |

## 7. Consensus record

| Stage | UNANIMOUS | AMENDED | AMENDED-UNANIMOUS | CONTESTED | HUMAN |
|---|---|---|---|---|---|
| Round 1 (ledger rows) | 414 | 67 | 0 | 12 | — |
| **Final (ledger rows, 493)** | **413** | **62** | **18** | **0** | **0** |
| Contested issues (9) | — | — | 9 (C01-C09, 3/3 AGREE each) | 0 | 0 |

- No reviewer cast a REJECT in either round. Rows that changed in round 2: 18. They are the 12 CONTESTED rows (T0-C19-R1, T2-C05-R7, T2-C09-R1..R4, T4-C26-R1, T5-C10-R6, T5-C22-R1 → now T5-C22-XREF, T9-C25-R3, T9-C26-R3, T9-C32-R1) plus 6 rows that carry an adopted amendment: T9-C16-R1 (C01), T5-C10-R5 (C02), T0-C06-R2 (C03), T9-C20-R1 (C04), T9-C26-R2 and T9-C26-R5 (C07/C06). No other row was touched.
- What was applied: **C01** T9-C16 NOT_STARTED (Rung A 9,470,190 / census 14,594,812; xref T3-C12, T3-C17). **C02** T2-C09 owns the pre-fit chain (R1-R4) and T5-C10 the post-freeze chain (R5 fit 16 Nov, R6 SIM-VAL 18 Nov). **C03** T5-C22-R1 folded into T0-C06-R2 (rules a-d with planted-violation fixtures, 5-8 agent h). **C04** number-class lint is an acceptance clause of T9-C20-R1; the script T9-C32-R1 is SHOULD (2 h) with a manual check on 21 Nov as fallback. **C05** T4-C26-R1 SHOULD, AI-only n=100 after 16 Nov, labelled AI_CHECKED. **C06** T2-C05-R7 COULD, only inside the 10 Nov lock. **C07** no new MUST; manjot-CPU deterministic-rung fallback added to T9-C26-R2 and to the lock (T9-C26-R5); T9-C25-R3 stays SHOULD. **C08** T9-C26-R3 raised to MUST (24 Nov dry run + Q&A sheet). **C09** T0-C19-R1 SHOULD coverage map for the 87 unanchored SSOT sections.
- Priorities after round 2 (open items, 472): MUST 84, SHOULD 168, COULD 110, AFTER 110. Before the topic merge there were 127 MUST items.
- Ledger: `registry/component_ledger_v1.csv` (CRLF kept; same 17 columns; 493 rows: 472 open items, 13 `-DONE` rows, 8 `-XREF` rows).
