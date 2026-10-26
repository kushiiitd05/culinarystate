# READER "impl" — CulinaryState implementation reality audit (2026-10-22)

Scope: read-only inventory of `/home/manjot23309/kush_work/culinarystate` (code, tests, tools, ledgers, registry, schemas, gate/freeze JSONs, step contracts, reports). Diagnostics were run only with shell tools and stdlib `python3 -I` (json/csv). Helper scripts live in `scratchpad/mpa/impl_scripts/` (outside the repo). No repo file was modified.
Conventions: repo paths are relative to the repo root. `SSOT Lnnnn` = line in `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`; `MP Lnnnn` = line in `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md`. "36-step plan" text is NOT in the repo (ctx.md). Wherever I say what a spine step "requires", that is my reconstruction from repo artifacts and the SSOT; it is not a quote from the missing plan.

---

## 0. Executive status table (component → status → evidence)

Ledger counts below are latest-version unique ids from my own recount (`impl_scripts/ledger_stats.py`). Line counts include version history (e.g. EVD has 57,280 lines and 18,156 ids).

| Component | Status | Evidence (path: fact) |
|---|---|---|
| Evidence EVD (plane B) | **IMPLEMENTED (infrastructure) / PARTIAL (content), contract FROZEN** | `ledgers/data/EVD.jsonl`: 17,978 ACTIVE + 178 DEPRECATED. All tier E3. Origin DATABASE_AGGREGATE 14,108 / PRIMARY_STUDY 3,870. Verification UNVERIFIED 14,108 / AI_PRECHECKED 3,870 / **human-verified 0**. Censored 5,894. Linked: ingredient_id 11,569, process_id 17,821. ES-1.1 export gate PASS (`reports/es1/es1_1_audit.md` L3–L8, L36–L45). The export jsonl is git-ignored and **absent on this machine**; the manifest sha256 of the ledger matches my recompute (5b3b1939…). |
| STUDY / source lineage | **PARTIAL (skeletal); Step 08 NOT STARTED** | `STUDY.jsonl` 125 rows, all `design="UNKNOWN"`. EVD `study_id_status`: NOT_IDENTIFIABLE 14,108 / PRESENT 3,870. 127 distinct `independence_group` values (125 PE papers, plus BOGNAR-2002 and USDA-RETN-R6 as one group each). There are no DOCUMENT/EXPERIMENT/SAMPLE/AGGREGATE ledgers. MP L2049–L2072 designs a `SAMPLE-` ledger, but no schema exists for it. |
| MEAS (measurement methods) | **PARTIAL** | 3 MEAS rows: MEAS-000001 USDA %TR calc, MEAS-000002 Bognár true retention, MEAS-000003 gravimetric yield. PE rows have method = null (3,870). `registry/measurement_method_registry_v1.csv` has 11 rows. The step07 report says "no platform is recorded in any current row" (`reports/step07/step07_report.md` L22). |
| Recipes (plane A) | **FROZEN** | `ledgers/recipe_base/recipe_base_v1.parquet`: 612,782 members, sha256 5545da58… matches `reports/step07/step07hr_freeze_manifest.json` (I verified it). Breakdown: FOODCOM 522,517, GUTENBERG_SEGMENT 73,955, A1_BBC 11,934, WIKIBOOKS 3,676, TASTESET 700 (`reports/step07/step07h_full_recipe_base_report.md` L5–L12). REC ledger has 89,565 unique ids (107,760 lines). |
| Recipe semantics (derived mentions) | **FROZEN by hash, but MISSING locally** | Hashes are listed in the 07H-R freeze manifest: 5 parquets, 33,719,014 rows, ~584 MB. `ledgers/recipe_semantics/` does not exist on this machine. |
| Recipe identity (07I-R) | **PROVISIONAL (gate PASS, calibration gate OPEN)** | `reports/step07i/step07ir_gate_result.json`: 611,714 exact reps, 8,639,518 candidate pairs, 744,615 kept, 6,589 provisional edges, 605,476 families (PROVISIONAL_STAR_V1, calibrated=false), 46,697 dish candidates. The 400-pair packet has `labels_filled: 0` (`duplicate_calibration_packet_manifest.json`). |
| Gold (recipe/state) | **PROVISIONAL / BLOCKED_HUMAN; content files absent locally** | 40 recipes are GOLD_PENDING_INDEPENDENT_IAA (20 A1 pilot Gold-v1.1 + 20 Food.com v1.1) and 10 are GOLD_CANDIDATE_SCREENED_NOT_ANNOTATED (`step07h_full_recipe_base_report.md` L10–L13). There is no DEEP_GOLD or GOLD_LIGHT (`registry/recipe_quality_tier_registry_v1.csv`). Only manifests exist in `annotation/gold/`; the Gold JSONs are git-ignored and were not copied. HV-004 is BLOCKED_HUMAN (`registry/human_verification_queue.csv`). |
| NER (ingredient lines) | **FROZEN / CLOSED** | CulinaryNER-KF v1 is DeBERTa-base+CRF. TASTEset TEST exact micro F1 0.9371 ± 0.0024, unseen 0.7008 (`reports/ner/culinaryner_kf_final_report.md` L1–L16). Router R6 ACCEPT error 0.0213. FOOD/PART/PHYSICAL_QUALITY always go to REVIEW. Checkpoint: `data/interim/models/ner/deberta-v3-base_crf`. **It was not run over the 612k base** (D-024; ingredient link status there is exact-alias only). |
| Linker | **FROZEN / CLOSED (D3)** | BGE top-1, strict Acc@1 0.881 (0.849–0.912) on the 850-item human gold. That gold had **pre-adjudication κ 0.317** (`reports/ner_v2/culinary_link_decision_final_report.md` L6, L11). No safe autonomous NIL. Sealed sets: 441 and 850. |
| Instruction-level NER/events | **NOT STARTED** | SX-08-05 MISSING (`registry/ssot15_state_experiment_map.csv`). |
| Quantities / CQPO / POR | **PARTIAL** | `quantity/grammar.py`, `normalize.py` (Q0/Q6 levels), `units.py`. UNIT has 74 rows (4 NEEDS_SOURCE). QNT/POR/ALLOC have 0 rows. `registry/ingredients/fdc_portion_candidates_v0.csv` has 1,204 candidates (D-006 requires human verification). The quantity-mentions parquet (4.28M) is missing locally. |
| Ingredients / aliases | **PARTIAL** | ING 2,048 ACTIVE (2,110 ids), ALIAS 4,103 ACTIVE. `scientific_identity_status` is UNKNOWN for all 2,110. `facets` are populated for 238 (form only). The FoodOn, OFF and FDC crosswalks are candidates (`registry/ingredients/*`). |
| Processes | **PARTIAL** | PROC: 156 (147 ACTION, 9 ENDPOINT), 18 families. `mechanism_families` are AI-drafted on 93 (HV-010 NOT_STARTED). `required_condition_axes` are present on 106. Target is ≥300 (`reports/step07i/max_plan_consensus.md` L21). |
| Tools | **PARTIAL** | TOOL: 119 (7 categories). `registry/recipe_tool_structural_class_map_v1.csv` has 14 classes, DETERMINISTIC_RULE_UNVERIFIED. Wikidata QIDs: `registry/tools/tool_wikidata_v1.csv`. Process↔tool links: 610. |
| Conditions (Step 07) | **automated: FROZEN (07H/07H-R gates PASS); human sub-gate: PENDING (packet v4, 0 judgements)** | `reports/step07/step07h_gate_result.json` all_pass. `step07hr_gate_result.json` all_pass. `step07h_human_gate_result.json` = **NOT_COUNTED_PROVENANCE_INVALID** on packet v3 (fingerprint a5991a9cda56). Packet v4 (fingerprint e7d589136275) is "the ONLY valid audit input" (`reports/step07/condition_audit_protocol.md` L97–L99). No v4 result exists. |
| EVT / ENTITY / STATE / GRAPH engine | **PARTIAL (engine code only; ledgers 0 rows)** | `state_graph/engine.py`, `rule_compiler.py`, `symqty.py`, `source_class.py`, `prefix_state.py`. Compiler vs pilot_20 Gold-v1: state-field acc 0.102 [0.04, 0.16], alive F1 0.312, merge/split F1 0.343 (`reports/del3/compiler_vs_gold_v1.md` table). 30 sessions are AI_DRAFTED and 0 are reviewed (`reports/del3/sessions_v1.md`). |
| RXN / mechanism | **NOT STARTED (schema only)** | `ledgers/schemas/RXN.schema.json` has relation enum FORMED…UNKNOWN_TRANSFORMATION, confidence HIGH/MEDIUM/LOW/UNKNOWN, and no rate-law fields. 0 rows. Mechanism EVD rows = 0 (`reports/ssot15/data_foundation_audit.md` L25). |
| Formula / model registry | **NOT STARTED** | `MODEL.schema.json` is an ML model card (name, family, training_dataset_ids, split_ids, checkpoint_path, reproduction_status) with 0 rows. There is no mechanistic formula/equation registry schema. |
| Parameter registry | **NOT STARTED** | No schema, no file. |
| KINETIC | **NOT STARTED** | No schema. Listed only as "0 → 0 BLOCKED_FUTURE_STEP" in the sync matrix (`step07h_full_recipe_base_report.md` sec. B). SX-06-04 / SX-13-02 MISSING. |
| SIM (simulation plane) | **NOT STARTED (contract only)** | `registry/simulated_state_changes_schema_v1.csv` (19 fields: E7 only, `may_enter_gold_evaluation` always false). `state_graph/source_class.py`. There is no `SIM` JSON schema in `ledgers/schemas/`, and no simulation data (`data_foundation_audit.md` L31). |
| WARN / conflict | **WARN NOT STARTED; conflict PARTIAL** | WARN schema has 0 rows. `registry/evidence/conflict_queue.csv` has 16 rows (human_status column). EVD has a `conflict_cluster` field. The retriever/confidence layer has a CONFLICTING mode (`decision/confidence.py` L16–L19). |
| Claims | **PARTIAL** | The C17 checker is implemented (`generation/claims.py`, `enforce.py`). The `CLM` ledger has 0 rows. |
| Splits | **PARTIAL** | `transition/splits.py`: random, pair_holdout, matrix_disjoint, process_disjoint, study_disjoint (refuses when impossible). NER benchmark splits are frozen (`benchmark/ner/`). **SPLIT ledger has 0 rows.** No recipe-level duplicate-group/family-disjoint split is frozen ("no split frozen", `max_plan_consensus.md` L29). |
| Transition models | **PARTIAL (baselines run; bootstrap contract DRAFT, not run)** | DEL-2 D0–D7 results are in EXP-000001..4 DONE (`reports/del2/*`). `reports/h_state/transition_bootstrap_v0_contract.md` is "defined, NOT run". TabPFN was SKIPPED. |
| Representations z_m / z_i / z_R / z_C | **NOT STARTED** | `classical/` and `silver/` are empty packages. MOL has 1,726 rows with PubChem 881-bit fingerprint + descriptors and no ECFP. IMAP has 30,294 rows. The similarity registry has 21 types, FROZEN, mostly MISSING/DATA-MISSING (`registry/ssot15_similarity_registry.csv`). |
| RAG / decision layer C1–C18 | **PARTIAL (rule baseline, silver-evaluated only)** | `decision/*` (15 modules), `retrieval/*` (5), `generation/*` (6). Silver dev results are in `reports/del4`, `reports/del5`. C9 (transition fallback) is not wired, and C2 coreference is absent (details in §1.6). |
| Experiment/gate map | **0 SSOT gates passed** | `registry/ssot15_state_experiment_map.csv`: 123 rows: MISSING 75, PARTIAL 40, COMPLETE 5, BLOCKED_HUMAN 2, DONE_NEGATIVE 1. The 5 COMPLETE are all NER/linker/quantity-law items. |

### 0.1 Code and test inventory

- `src/culinarystate/`: 22 packages, 14,091 LOC. Modules per package: annotation 6, decision 15, eda 2, evidence 13, generation 6, identity 11, ingest 13, kg 5, ledgers 6, molecules 2, ner 10, process 3, quantity 4, recipes 4, retrieval 5, scoring 4, sources 3, state_graph 6, transition 6, vocab 6. `classical/` and `silver/` contain only `__init__.py` (empty).
- Largest modules: `evidence/condition_normalizer.py` 558, `ledgers/registry.py` 429, `state_graph/engine.py` 352, `recipes/probe.py` 302.
- Tests: **678 test functions** in 92 files. Breakdown: unit 542 / 83 files, contract 66 / 3, integration 18 / 3, property 16 / 2, top-level 36 / 7. Fixtures: `tests/fixtures/ledger_examples.py`, `mini_foodon.owl`. Golden: `tests/golden/condition_syntax_golden_v1.json`. WORKLOG S134 reports "3482 suite tests pass" (parametrised cases) with "1 pre-existing unrelated hang in test_transition deselected" (WORKLOG L920–L925). So the suite is **not fully green** (UNVERIFIED here: no test run allowed).
- Function counts by area (approximate grouping by file):
  - Condition/Step-07: ~72 (normalizer 16, conditions 13, properties 10, units/open_bounds/trajectory/dialect 6 each, schema 5, golden 2, agreement 2)
  - Decision/RAG: ~150 (policy 17, session_state 16, candidates 15, selector 14, constraints 13, verbalize 13, …) plus contract 66
  - Ledgers: 38
  - NER/linker: ~45
  - Quantity: 25 (15 + 10 property)
  - Identity: 11
  - Evidence ingest/linking/export: ~45 (evd_export 11)
  - State engine/gold: ~55 (state_engine 15, gold 8, evidence_first_gold 9, …)
  - Transition: 10 (transition 7, del2 1, cross_source 2)
  - Retrieval/scoring: ~29
  - Vocab/KG/sources: ~60
- Tools: `tools/` has 176 entries (175 `.py` + `download_cosylab_data.sh`). Pipeline families:
  - Ingestion: `ingest_*`, `crawl_*`
  - Registry builders: `build_*_registry.py`, `build_mp1_registries.py`, `build_step07_registries.py`
  - ES-1: `build_evd_export_v1.py`, `validate_evd_export_v1.py`, `build_es12_*`, `es12_*`
  - Step 07: `step07_*`, `step07h_gate.py`, `step07h_regression.py`, `step07hr_{gate,finalize,freeze,report}.py`, `build_recipe_base.py`, `build_gold_index.py`, `recipe_preflight.py`
  - 07I: `step07i_*` (`step07i_identity.py` is the phased orchestrator)
  - DEL-2: `run_del2.py`, `run_cross_source.py`
  - DEL-3: `eval_compiler_vs_gold.py`, `run_sessions.py`, gold tooling
  - DEL-4: `eval_retrieval_silver.py`, `eval_rq1603.py`, `eval_graph_expansion.py`, `rerank_silver.py`
  - DEL-5: `ask.py`, `run_ladder.py`
  - NER/linker: `final_test_eval.py`, `router_eval.py`, `v2dm_*`, `linker_v2_eval.py`
  - H_STATE: `build_hstate_*`, `hstate_*`, `validate_hstate_questions.py`
  - Human-review appliers: `apply_human_review.py`, `apply_link_review.py`, `apply_gold_corrections.py`
- Environment: tools assume `/opt/anaconda3/bin/python` (Mac; `CLAUDE.md` L5–L6). `transition/splits.py` imports pandas, and identity uses pyarrow/numpy. Neither pandas nor pyarrow exists in system Python on this Linux server (ctx.md). **The DEL-2, identity and 07H-R pipelines cannot be re-run here without an environment decision.**

### 0.2 Data the user copied under `data/` (directory level only) and what is missing

- `data/raw/` (334 MB): bognar, chemtastesdb, doi_resolve, fdc, flavorgraph, foodon, fsis, fssai, gutenberg, off, openalex, openpi, phenol_explorer, pubchem, tasteset, usda_r6, wikibooks, wikidata.
- `data/external/` (521 MB): allerstack, bittersweet, cosylab_companion, drugadr, fndds, foodcom (recipes.parquet + PROVENANCE.json: Kaggle CC0 declared, authority unverified), hierarchical_clustering, infoods (AnFooD2.0, density_v2, uFiSh1.0), nova_food_processing, recipedb2, recipedb3_ner, recipe_knowledge_mining (+ results csv), recipe_ner_dl, spice_disease, sustainablefooddb (Recipe_cfp.csv, 118,083 ingredient lists, un-indexed per `max_plan_consensus.md` L46), sweetpreddb, usda_yields (cooking_yields_meat_poultry_r2 + DD).
- `data/interim/` (1.3 GB): embeddings (329 MB), evidence_first, foodoscope_probe, gutenberg, models (712 MB; `ner/deberta-v3-base_crf`), openpi, retrieval, rq1603, troubleshooting, wikibooks.
- `data/manifests/`: **empty**.
- Also present: `ledgers/recipe_base/*.parquet` (4 files; hashes match the freeze) and `ledgers/recipe_identity/*.parquet` (12 tables + 2 work pickles + run manifest). `features/` is present.

**MISSING on this machine:**
1. `ledgers/recipe_semantics/` (5 frozen parquets: expression_probe 8,166,098; condition_mentions 3,904,986; ingredient_mentions 4,964,190; quantity_mentions 4,281,956; process_mentions 12,401,784 rows).
2. The A1 BBC raw corpus. `recipes/corpus.py` L35 reads `../a1/A1 3/data/processed/recipes_processed.jsonl` (sibling dir, not present), so the 07H-R base cannot be rebuilt here.
3. `annotation/gold/*` Gold JSONs (pilot_20 v1/v1.1, `foodcom_ai_assisted_v1_1/`, independent blank bundles). Only manifests are present.
4. `annotation/condition_audit/*.csv` (packets v1–v4).
5. `exports/evd/evd_export_v1.jsonl` (deterministic and regenerable; manifest present).
6. `benchmark/h_state/authoring_pack/`, `annotation/ai_review/`, `annotation/parv_pack/`.
7. `gpu/*/runs/` (git-ignored).

---

## 1. Definitions, entities and data contracts (field-level)

### 1.1 Common ledger envelope and store
- `ledgers/common.py` / `ledgers/store.py`. Every record carries `id, version, status, provenance{method, source_ids, snapshot_ids, agent, locator, notes}, verification{status, verifier, verified_at, ai_reviewer, notes}, created_at, created_by, schema_version, record_type, external_refs, notes`.
- The store is append-only and versioned (JSONL per prefix), with a never-reuse ID minter (`_ids.jsonl`, 200,118 minted ids). Scientific values use QVALUE: `{status ∈ MEASURED|RANGE|QUALITATIVE|CENSORED|UNKNOWN|NOT_APPLICABLE…, value, low, high, unit, uncertainty, qualitative, censor, raw}`.
- 37 schemas exist in `ledgers/schemas/` (exported from `ledgers/registry.py` by `tools/export_schemas.py`). Populated: 18 record types. Zero rows: ALLOC, API, CLM, ENTITY, EVT, GATE, GRAPH, INST, MODEL, POR, QNT, REF, RQ, RS, RXN, SPLIT, STATE, WARN.

### 1.2 EVD (evidence) — field level (`ledgers/schemas/EVD.schema.json`)
- Top-level fields: `origin_type, source_id, source_family_id, study_ids[], study_id_status, extraction_version, matrix{ingredient_id, raw_name, food_group, variety, part, form, prior_processing, initial_state, geometry, storage_ripeness}, process{process_id, raw_name, family, tool_ids, steps, step_process_ids, modifiers, medium, condition_id}, target{state_variable_id, raw_name, molecule_id, reaction_id, basis}, before QVALUE, after QVALUE, measurement_method_id, derived{delta, percent_change, retention_factor, log_fold_change, yield_factor (QVALUE each), direction}, design, n_replicates, tier, conflict_cluster, independence_group, applicability, censored`.
- Populated values (my recount):
  - design: DATABASE_AGGREGATE 14,108 / UNKNOWN 3,870
  - applicability: GENERIC 14,108 / EXACT 3,870
  - target.basis: RETENTION_TR_OR_AR 7,018, TRUE_RETENTION 6,594, FRESH_WEIGHT 3,402, PER_VOLUME 960, DRY 4
  - derived.direction: DECREASE 10,789, UNKNOWN 5,918, INCREASE 1,180, NO_CHANGE 91
  - before/after populated only for PE (3,870)
- `registry/evd_contract_v1.csv` (MP-1 contract, 27 fields): required/optional, current population, action, semantics-when-unavailable. Examples:
  - `study_id` "study_id_status = NOT_IDENTIFIABLE, never blank"
  - `lod/loq` "ADD explicit lod/loq in the export view where the source gives them"
  - `confidence` "ADD only if a calibrated definition is agreed; do not invent a score"
- ES-1.1 export view adds: `evidence_tier, verification_status, design_strength, provenance_class, matrix_id (hash), prior_state_id (PST- hash), lod/loq (null; NOT_REPORTED_BY_SOURCE_ROW), delta_value 3,870, log_fold_change 3,787, log_retention_factor 11,503, *_reason_if_unknown, target_state_variable_id + canonical_variable_id` (`reports/es1/es1_1_audit.md` L10–L30; D-018 at DECISIONS L115).
- Tier ladder: `registry/evidence_tier_provenance_map_v1.csv`. E1 controlled experiment … E7 simulator output. Only E3 has rows (17,978). Ruling C1 (D-018): tier, verification status, design strength and provenance class are separate fields, and "A human review never changes the tier".
- Provenance classes: `registry/provenance_class_registry_v1.csv` (EXPLICIT_SOURCE, EXTERNAL_VERIFIED, DERIVED_DETERMINISTIC, INFERRED_LLM, MODEL_ESTIMATED, IMPUTED, SIMULATED, UNKNOWN; `state_representation_contract_v1.md` L51).

### 1.3 COND (conditions) and the Step-07 vocabulary
- `COND.schema.json` properties: `duration, temperatures[], trajectory, ph_initial, ph_final, moisture, water_activity, pressure, oxygen, salt, sugar, fat, medium, particle_size, geometry, agitation, power, humidity, heat_transfer_mode, tool_ids, biological, completeness_mask`.
- Ledger rows populate only duration/temperatures/medium/power/pressure + mask. Moisture/pH/aw are UNKNOWN in 100% (`data_foundation_audit.md` L24).
- Canonical condition value schema: `registry/schemas/condition_value_v1.schema.json`. Value types POINT/INTERVAL/TRAJECTORY/QUALITATIVE/UNKNOWN. Statuses VALID/INVALID/AMBIGUOUS/UNKNOWN + reason codes (`reports/step07/step07_report.md` L6–L9; D-020).
- `registry/condition_variable_registry_v1.csv` has 40 variables:
  - time CV-001..004
  - temperature CV-005..012: setpoint, medium, surface, core, unspecified, trajectory, rate, preheat
  - chemical CV-013..023: pH, TA, aw, moisture, dry matter, salt, sugar, fat, O2 headspace, solvent, additive/enzyme
  - physical CV-024..036: pressure, RH, heat-transfer mode, agitation, flow, MW power/frequency, shape, thickness, particle size, S/V, batch size, container material
  - biological CV-037..040: strain, inoculum, maturity, storage age
- Bounds: `registry/condition_variable_bounds_registry_v1.csv` (hard vs plausibility; D-023).
- Other registries: measurement basis (MB-001..), retention types (RT-001..006), censoring, value origin, measurement location, measurement method, heat-transfer mode, notation rules (13), source dialect (22 mappings).
- Laws enforced in the normaliser: "nothing is inferred … boiling is never 100 C, pH is never defaulted, moisture/aw/pressure/O2 absent is never 0" (`condition_normalizer.py` docstring); "calendar month/year are calendar durations, never converted to seconds" (D-023).
- Frozen fingerprint: combined `e7d58913…` (07H-R, commit 5476cf35). The 07H (commit 4e7db137) fingerprint `a5991a9c…` is superseded.

### 1.4 Recipe plane
- `recipe_base_v1.parquet` holds pointers + hashes only. REC is immutable (D-024). Quality tiers (`registry/recipe_quality_tier_registry_v1.csv`): SOURCE_RAW, SILVER_AUTO, SILVER_REVIEWED, GOLD_LIGHT, DEEP_GOLD, GOLD_PENDING_INDEPENDENT_IAA, REJECTED, UNKNOWN. Each tier states its allowed training/calibration/test use. DEEP_GOLD requires "independent blind double annotation with adjudication and reported IAA … requires Step-19 style blind re-annotation".
- Recipe text is `source_plane=RECIPE`, `observation_class=TEXT_STATED`, with no E-tier (`step07h_full_recipe_base_report.md` L3).
- `recipe_simulation_readiness_v1.parquet` records **text availability only, NOT simulation eligibility** (sec. E): PARTIAL_CONDITIONS 448,093, PROCEDURALLY_RICH 97,055, INSUFFICIENT 37,208, QUALITATIVE_ONLY 29,547, UNKNOWN 879.
- Usage/licence (`registry/recipe_source_usage_registry_v1.csv`, `reports/step07i/final_recipe_database_statistics.md` L37–L64): LICENCE_UNVERIFIED 523,217; PUBLIC_OPEN 73,955; LOCAL_RESEARCH_ONLY 11,934; REDISTRIBUTABLE_WITH_ATTRIBUTION 3,676. **training_allowed = YES only for 73,955 (Gutenberg)**; UNKNOWN 535,151. Open H2 items: Food.com SRC + licence, TASTEset, A1/BBC training/redistribution, Wikibooks share-alike.

### 1.5 Identity (07I-R)
Pre-registration: `reports/step07i/preregistration_v1.md` L5–L39.
- **Levels.** Level A DUPLICATE_GROUP is deterministic: raw_hash, rec_content_sha256, norm_text_hash, A1 canonical_url. Level B RECIPE_FAMILY is PROVISIONAL_STAR_V1. Level C DISH_FAMILY_CANDIDATE is INFERRED_CANDIDATE.
- **Relation classes.** Only EXACT_BINARY_COPY, EXACT_NORMALIZED_COPY and MIRRORED_COPY coalesce.
- **Pair features.** Missing values are flagged, never 0. Ranking-score weights are fixed (title 0.15, ingredient_idf 0.30, ingredient_id 0.10, multiset 0.10, instruction_shingle 0.20, process_seq 0.05, condition 0.05, quantity 0.05). The score ranks pairs and is not a decision.
- **Edge rule.** IDF-ingredient Jaccard ≥0.80 AND title Jaccard ≥0.50 AND (shingle ≥0.30 OR process-seq ≥0.70 with ≥3 mapped processes), AND no cuisine conflict.
- **Clustering and amendment.** Star clustering with no chaining. Amendment A1: ingredient-LSH restricted to ≥4 tokens, bucket cap 50.
- **Output tables** (`ledgers/recipe_identity/`): duplicate_group_members, candidate_pairs, recipe_family_{registry, members, consensus, consistency, field_support}, dish_family_candidates, gold_firewall (`split_lock_group_id`), recipe_identity_fk (recipe_id → duplicate_group_id → recipe_family_id), recipe_view_membership, recipe_identity_features. Views: RECIPE_SOURCE_ALL, DEDUP_EXACT, FAMILY_VIEW, MODEL_ELIGIBLE, RELEASE_ELIGIBLE, GOLD.
- **Recall diagnostic.** `identity_summary_v1.json`: ing-LSH buckets skipped over cap = 4,745, covering 791,511 record-bucket memberships. Candidate recall for large common-ingredient buckets is therefore limited (UNVERIFIED magnitude).

### 1.6 State / event plane (code contracts, no data)
- **Engine.** `state_graph/engine.py` docstring: identity layers are "concept = ING id; entity = physical lot/intermediate; version = entity's state". Event types in Gold: Add, Transform, Merge, Transfer, Split, Reserve, Recombine, Discard (`data_foundation_audit.md` L12).
- **EVT.schema.** `recipe_id, step_index, ordinal, process_id, action_raw, input_state_ids, output_state_ids, tool_ids, condition_id, endpoint, optional, trajectory ∈ {PLANNED, OBSERVED_SESSION, PREDICTED}, omitted_step_candidate, span`.
- **ENTITY.schema.** `recipe_id, ingredient_id, label, kind, ordinal`.
- **STATE.schema.** `entity_id, state_version, previous_state_id, produced_by_event_id, belief ∈ {PREDICTED, OBSERVED, PLANNED}, overrides_state_id, variables{<svar>: QVALUE-like}, quantity, location, form`.
- **GRAPH / REF / ALLOC / INST.** GRAPH: `recipe_id, session_id, edges, event_ids, replay_sha256`. REF (coref): `mention_text, mention_span, resolves_to_entity_ids, kind`. ALLOC: `parent_entity_id, child_entity_id, fraction, basis, kind, event_id`. INST: `step_index, raw_text, normalized_text, sentence_spans, event_ids`.
- **Factorised state** (frozen contract): `reports/h_state/state_representation_contract_v1.md` L16–L32. S = {C, P^phys, Y^sens, N, Q, R, X, U}. Q/R/X are plan extensions beyond SSOT 106 (L19). Profiles are never one embedding.
- **State variable registry.** `registry/state_variable_registry_v1.csv`: 254 rows. Statuses: ACTIVE 59, PROVISIONAL 73, MISSING_EVIDENCE 81, DUPLICATE 11, FUTURE 30. Families: CHEMICAL 230, PHYSICAL 13, PROCEDURAL 5, SENSORY 3, SAFETY 3. `simulation_eligible`: NO_BY_DEFAULT 236; POTENTIAL_ONLY_WITH_A_VALIDATED_SIMULATOR 17 (+1 mass-balance). Status rule (contract L35): ACTIVE = ≥50 active EVD rows, ≥3 process signatures, single analyte.
- **Source-class firewall.** `state_graph/source_class.py` + `docs/simulator_data_contract.md`: "a STRUCTURAL_RECIPE source may say that a process occurred; it may NOT by itself define the measured physical/chemical magnitude". Mapping: STRUCTURAL_RECIPE→R only; COMPOSITION→E3; MEASURED_TRANSITION→E1/E2/E4; COMPILED_RETENTION→E3; KINETIC→E1/E2/E4 if fitted with uncertainty; MOLECULAR/SENSORY_PRIOR/MODEL_GENERATED→E6; SYNTHETIC→E7 (contract L59).
- **Simulation contract.** `registry/simulated_state_changes_schema_v1.csv`: simulation_id, ingredient_id_or_entity, matrix_descriptor, process_id, conditions, input_state, predicted_output_state, state_variable_ids (subset of the validated scope), simulator_id, simulator_version, parameters (with source or SIMULATED_PARAMETER), uncertainty (unquantified = UNKNOWN), validation_scope, extrapolation_flag, provenance_class=SIMULATED, evidence_tier=E7, may_enter_gold_evaluation=false.

### 1.7 Mechanism / formula / parameter / kinetic
- **RXN.schema.** `relation` (FORMED, DEGRADED, RETAINED, LEACHED, VOLATILIZED, OXIDIZED, REDUCED, ISOMERIZED, DENATURED, AGGREGATED, GELATINIZED, FERMENTED, CONSUMED, UNKNOWN_TRANSFORMATION), `reactant_ids, product_ids, stoichiometry_known, mechanism_family, condition_id, reaction_smarts, matrix_applicability, evidence_ids, confidence`. It **lacks the "rate law / kinetic parameters when identified" and "condition window" fields** that MP W6 (MP L1689–L1726) asks for.
- PROC has `mechanism_families` (e.g. ["leaching","starch_gelatinisation","protein_denaturation","cell_wall_softening"]) and `required_condition_axes`. These are AI-drafted and unverified (contract C7, L71).
- No FORMULA/MECH_MODEL, PARAM or KINETIC schema exists. MODEL is for ML artifacts.
- SSOT gate text for this area: G15-4 / G15-RXN / G15-HYB / G15-INV (SSOT L22376–L22427; quoted in §4).

### 1.8 Molecules / ingredient–molecule / KG
- MOL: 1,726 rows (PubChem CID, SMILES, InChIKey, descriptors, 881-bit fingerprints, stereo_status).
- IMAP: 30,294 rows. Relations: PRESENCE 29,656, PROCESS_CHANGE 419, MEASURED_CONCENTRATION 219. Fields: `basis, concentration, state_id_or_form, evidence_ids`.
- KGE: 45,201 active, 22 predicates. Top: ING_CO_OCCURS 34,394, ING_USED_IN_CUISINE 2,330, ING_PROCESSED_BY 2,132, MOL_HAS_TASTE 737, ING_ALTERNATIVE_TO 220. Bands: LOW 20,392 / MEDIUM 17,173 / HIGH 7,636 (Wilson lower bound, D-011). These are recipe/co-occurrence-derived, not chemistry.

### 1.9 Decision/RAG layer — C1–C18 implementation map
SSOT 257B (L28539–L29335) defines 18 module contracts. Every module shares the same obligations: typed inputs, raw preserved, version attached, UNKNOWN/UNRESOLVED, failure reasons, deterministic replay, oracle-upstream and predicted-upstream eval. The promotion rule (e.g. L28583) reads "promoted only if it improves the relevant downstream or module-specific gate against the strongest simpler baseline".

| C | SSOT (inputs → outputs) | Repo implementation | Status |
|---|---|---|---|
| C1 query/intent parser | L28545–L28547 raw query+session → intent, targets, mode | `decision/relevance.py` (intent cues, rule-based), `decision/pipeline.py` slots, `decision/targets.py` | PARTIAL (rules; slot acc on templated Qs: ingredient 0.994, process 0.945, target 0.994, `reports/del4/rq1603_pilot_v1.md`) |
| C2 entity/coref | L28589–L28591 | `vocab/line_link.py` + frozen BGE linker; no coreference module | PARTIAL / coref NOT STARTED (108/113 Gold coref mentions UNKNOWN) |
| C3 state reconstructor | L28633–L28635 | `state_graph/engine.py`, `decision/state_conditioning.py` (B4) | PARTIAL |
| C4 process-history | L28677–L28679 | `session_state.process_history`, `state_graph/prefix_state.py` | PARTIAL |
| C5 goal/constraint | L28721–L28723 | `decision/constraints.py` (13 tests) | PARTIAL |
| C6 multi-index retriever | L28765–L28767 | `retrieval/bm25.py`, `retriever.py` (BM25 ∪ structured; rank = 0.35·bm25 + 0.65·compat), `food_graph.py` (R4), dense embeddings tool | PARTIAL (silver: R2 RRF BM25+e5-large MRR@10 0.7616; structured oracle 0.8555, `reports/del4/retrieval_silver_v1.md`) |
| C7 compatibility | L28809–L28811 | `retrieval/compatibility.py` (MATCH/NEAR/MISMATCH/UNKNOWN per axis; "UNKNOWN is never a mismatch") | PARTIAL |
| C8 direct transition lookup | L28853–L28855 | packet `direct`/`near` pools in `retriever.py`; comparator uses direct else near | PARTIAL |
| C9 transition fallback | L28897–L28899 supported query + L15 model → prediction+interval+OOD | **not wired**: `confidence.py` accepts `model=` but nothing produces it | NOT STARTED (consistent with G16-TRANS) |
| C10 candidates | L28941 | `decision/candidates.py` | PARTIAL |
| C11 feasibility | L28985 | `decision/feasibility.py` | PARTIAL |
| C12 comparator | L29029 | `decision/comparator.py` (median per independence group) | PARTIAL |
| C13 relevance gate | L29073 | `decision/relevance.py` | PARTIAL |
| C14 uncertainty/OOD | L29117–L29119 ALLOW/WARN/QUALITATIVE/ABSTAIN | `decision/ood.py`, `decision/confidence.py` (sufficiency modes DIRECT/NEAR_PARTIAL/MODEL_INTERPOLATION/BROAD_QUALITATIVE/CONFLICTING; precision cap) | PARTIAL (not calibrated) |
| C15 selector | L29161 | `decision/selector.py` (Pareto; UNKNOWN valid) | PARTIAL |
| C16 generator | L29205 | `generation/verbalize.py` (B5T template = promoted), `llm.py` (Ollama via A100 tunnel), `prompts.py` | PARTIAL (promoted template; LLM rephrase unpromoted, `reports/del5/generator_c16_v1.md`) |
| C17 citation/provenance | L29249 | `generation/claims.py`, `enforce.py` | PARTIAL; CLM ledger 0 rows |
| C18 session updater | L29293 | `decision/session_state.py` | PARTIAL |

Decision modes (`decision/policy.py`): ANSWER / COMPARE / ASK / DIAGNOSE / RECOVER / RECOMMEND / ABSTAIN. All evaluations are silver and AI-authored (20 dev questions in DEL-5). The locked benchmark (D-008, human) does not exist.

---

## 2. Models and baseline ladders (simple → strong → advanced), as implemented

1. **Transition (DEL-2, `transition/baselines.py`).** D0 persistence (RF=1) → D1 global mean → D2 process mean → D3 hierarchical shrinkage → D4 nearest compatible evidence → D5 gradient boosting (categorical + mask features) → D7 biased MF with side info. D6 TabPFN was SKIPPED ("not installed; GPU", `reports/del2/USDA-RETN-R6_results.md` L6). Censored rows are trained at a lower bound of 0.975 (an assumption, L7). Results:
   - **USDA R6** (6,994 rows; 38 matrices; 77 process signatures):
     - Random split: D5 MAE 0.0251 vs D0 0.1205.
     - **Matrix-disjoint: D0 0.0590 [0.0407, 0.0711] beats D5 0.0692 and D4 0.0567 ~ D0.**
     - Process-disjoint: D0 0.0728 vs D5 0.0672 (CIs overlap). Conformal-90 coverage drops to 0.72–0.78 for D4/D5.
   - **Phenol-Explorer** (3,870 rows; 146 matrices; 33 processes; 161 targets; grid density 0.00267):
     - D0 is best or tied on every cold split: matrix 0.767 vs D5 0.909; process 0.368 vs D5 0.600; study-disjoint 0.558 vs D5 0.755.
     - The log-RF target does not fix this.
   - **Bognár** (6,594 rows; 7 process signatures):
     - Matrix-disjoint: D5 0.0463 vs D0 0.0621.
     - Process-disjoint: D5 0.0096 vs D0 0.0385, but **the CI is degenerate ([0.0096, 0.0096])**, i.e. a single held-out group. The inventory's "Bognar supported incl. cold" (`ssot15_state_program_inventory.md` L47) rests on this.
2. **TRANSITION_BOOTSTRAP_V0 ladder (contract, not run).** B-0 persistence → B-1 global mean delta → B-2 ingredient-conditioned mean (shrinkage to food group) → B-3 process-conditioned mean → B-4 ingredient×process lookup with hierarchical fallback → B-5 simple tabular (GB / regularised regression) "only after B-0..B-4 are reported". "No neural model … TabPFN or learned models are out of scope for V0" (`transition_bootstrap_v0_contract.md` L16–L17).
3. **Retrieval (DEL-4).** R0 BM25 → R1 dense (BGE/E5/GTE) → R2 RRF hybrid → R3 structured (oracle slots) → R4 structured + dense → R5 cross-encoder rerank. Reranking hurt: bge-reranker-large Δ MRR −0.0559 [−0.0908, −0.0174] (`retrieval_silver_v1.md`). RQ16-03 pilot: structured S2 > CE S1 on HARD negatives (+0.071 [+0.055, +0.090]); silver labels only.
4. **Generator (DEL-5).** B0 LLM-only → B2 hybrid RAG → B5 packet+decision → B5F per-route facts → B5F+E enforcement → B5T deterministic template. B5T was promoted (0 unsupported / 0 violations), and B5F+E ties it but is unpromoted (`generator_c16_v1.md`).
5. **NER.** Rule floor (TASTEset micro F1 0.791 exact, `docs/RESOURCE_GAP_MAP.md`) → encoder ± CRF → DeBERTa-base+CRF (frozen). deberta-v3-large challenger: ΔF1 +0.0000 [−0.0053, +0.0054]. kNN-NER null; metadata fusion rejected.
6. **Linker.** BGE top-1 (kept) vs E5, zero-shot CE (0.619), Tev1-4B, Nimble, CD-L1/CD-L2 (distilled). DISTILL-A: CD-L2 − CD-L1 = +0.064 [+0.038, +0.089], but the student < BGE.
7. **State compiler.** Rule baseline "B-rules" (`state_graph/rule_compiler.py`) vs Gold. No learned event extractor exists.
8. **H_STATE (EXP-000007, PLANNED).** B3 (no state) vs B4-predicted vs B4-gold (`compiler_vs_gold_v1.md` "Consequence for H_STATE").
9. **Identity.** Deterministic hashes → LSH candidates → interpretable features → fixed-weight ranking (not a decision) → pre-registered conservative edge rule. Old monolith vs new pipeline: bit-identical on the 1-in-20 sample (`identity_benchmark_report.md` L69–L75).

---

## 3. Experiments / hypotheses / RQs present in the repo

- EXP ledger (`ledgers/data/EXP.jsonl`, 7 ids): EXP-000001..4 DEL-2 D0–D7 (USDA, PE raw, PE log, Bognár) DONE; EXP-000005 Part K hybrid NER on TASTEset DONE; EXP-000006 RQ16-03 compatibility reranker silver pilot DONE; **EXP-000007 H_STATE (B4 vs B3) PLANNED**. Cards are in `experiments/EXP-00000N/`.
- `registry/ssot15_state_experiment_map.csv` (123 rows): 70 SX (defined in Master Plan v4.0, not the SSOT: "The SSOT v15 file defines no SX-* experiment ids", `ssot15_state_program_inventory.md` L9), 47 gates, 6 RQs (RQ16-01/13/14/15/20/24). Key MISSING items:
  - SX-03-01 classical L7–L8 code
  - SX-04-02 ECFP/MACCS/odor benchmark
  - SX-06-03 volatiles
  - SX-06-04 kinetic table
  - SX-06-05 pH (100% UNKNOWN)
  - SX-06-06 alliinase/myrosinase/LOX/PPO (0 rows)
  - SX-06-07 WARN
  - SX-07-02 Silver factory
  - SX-08-05 instruction weak labels
  - SX-10-03 POR
  - SX-11-03 coref
  - SX-12-02 thermal dose/Arrhenius
  - SX-13-02 kinetics
  - SX-13-05 simulator data
  - SX-14-* all representation/similarity tests

  BLOCKED_HUMAN: SX-06-08 (634-row verification queue, 0/40 verified) and SX-07-01 (independent Gold).
- The H_STATE coverage experiment (S114/S116) is complete as a forecast:
  - Supported stratum: n=14 over 8 recipes on pilot_20 Gold-v1.1 (`h_state_benchmark_v1.md` L34–L43).
  - Food.com v1.1 gives 51 pairs over 15 recipes (`reports/gold/foodcom_ai_assisted_v1_to_v1_1.md`).
  - Evidence-first compiler matching: precision 0.25, recall 0.29 (`h_state_coverage_lift_forecast.md` L14).
  - Recommended route: Path A +20 independent Gold, with Path B +5 cells in parallel (L54–L58).
- Data-foundation numbers (`data_foundation_audit.md` L48–L53):
  - Recipe→evidence coverage: exact EVD cell for 24 of 2,132 ING_PROCESSED_BY edges (3.0% of recipe support); near-only 738; none 1,370.
  - Top missing by recipe support: salt/season 20,293, cream/beat 14,019, pepper/season 11,497, butter/melt 7,293…
  - Coverage cube: 245 non-empty cells (food group × process family × svar family × tier), all chemical except the yield rows. 485 exact ING×PROC cells (220 with ≥10 rows).
- Calibration packets (human, unlabeled):
  - Duplicate calibration: 400 pairs over 10 strata (S03 boundary-family-rule 60, S02 high 50, …), `labels_filled: 0`.
  - Condition audit: packet v4, 100 conditions, strata S1–S6.

---

## 4. Gates, promotion and stop rules (ids and thresholds verbatim)

### 4.1 Repo gates (executed or pending)

**ES-1.1 EVD export** — PASS (`reports/es1/es1_1_audit.md` L36–L45). The seven conditions are all True: "every source row accounted for", "no scientific value invented", "source lineage preserved", "duplicate mapping reversible", "deterministic derivations reproducible", "schema validation succeeds", "canonical source rows unchanged".

**Step 07 human sub-gate** — PENDING.
- Protocol (`reports/step07/condition_audit_protocol.md` L94): "Gate (preregistered): pooled Cohen's kappa >= 0.80 AND no systematic disagreement on a critical field (temperature location, pressure reference, basis, retention type, censoring) -- a flagged critical field forces adjudication even if overall kappa passes."
- Also L95: "If the normalizer changes after reviewers start, the audit is invalid and must be rerun. Do not tune the normalizer on the labels."
- v3 result (`step07h_human_gate_result.json`): `"gate": "NOT_COUNTED_PROVENANCE_INVALID"`, `"pooled_kappa": 0.9978`, `"gate_as_computed": "FAIL_OR_ADJUDICATE"`, `"counts_as_human_gate": false`. Reasons: files written 11 s apart; basis/retention_type/censoring prevalence 1.00 ("kappa paradox risk"). Content finding: "6 months → 1.57785e7 s". Packet v4 supersedes it (protocol L97–L98).

**07H automated gate** — G1..G10 all PASS (`step07h_gate_result.json`): G7_current_data_regression_completed_4414_17978, G8_source_ledgers_byte_identical, G9_deterministic_two_rebuilds, G10_no_unsupported_abbreviation_promoted. Test groups passed: 45/138/123/49/6/10.

**07H-R gate** — G1..G7 all PASS (`step07hr_gate_result.json`): "G2_4414_condition_regression_0_unexplained", "G4_scientific_and_vocab_ledgers_byte_identical", "G5_two_complete_rebuilds_deterministic", "G7_no_bulk_gold_promotion". Regression: 15,872 fields compared, 1,110 changed, 0 unexplained.

**07I-R gate** — `"status": "PASS (provisional identity layer; calibration gate open)"`. Checks include `"no_unvalidated_threshold_used_for_destructive_coalescence": true` and `"measured_memory_within_configured_limit": {"peak_process_tree_rss_gb": 1.909, "limit_gb": 4.5}`. `"human_gates_pending": ["Step-07 condition audit packet v4 (Kush, Parv blind)", "duplicate calibration packet v1 (400 pairs, unlabeled, Kush, Parv blind)"]`, `"step_08": "NOT STARTED / NOT AUTHORISED"`.

**TRANSITION_BOOTSTRAP_V0 pre-registered criteria** (`transition_bootstrap_v0_contract.md` L26–L29):
- "**Supported** only if a baseline above B-0 beats B-0 with paired lower bound > 0 on S-3 or S-4 (cold) for T1 or T2 separately, and no gain is explained by source/basis shortcuts (re-run with source-family and basis held constant)."
- "Failure is a valid, reportable outcome; no model-complexity escalation on V0."
- Headline = "S-2..S-5 min; S-1 not used for claims" (L20).

**State variable ACTIVE rule**: "≥50 active EVD rows, ≥3 process signatures, single analyte" (contract L35).

**NER router**: eps = 0.02 finite-sample risk control, thresholds fitted on CALIBRATION only (`culinaryner_kf_final_report.md`). The linker S6 degradation threshold is "n>=30 degradation threshold of -15 pts" (`culinary_link_decision_final_report.md` L24).

**Scripted sessions contract**: "≥ 30 reviewed" — currently 0/30 (`reports/del3/sessions_v1.md`; `annotation/sessions.py` cites plan line 1250 AH6, "≥ 30 course minimum, 80–100 target").

**H_STATE**: EXP-000007 planned ≥40 supported questions among 60, but at most 14 are achievable (`h_state_benchmark_v1.md` L18, L37).

**Tier rules**:
- "Primary evaluation eligibility: E1-E4 only. E5-E7 never become Gold truth." (contract L52)
- "E5 -> E4 promotion requires human verification against the cited source span/table" (L52).

**HV queue**: HV-001 "634 ranked literature rows (0 verified); first target >=40, aim 60-80 across several mechanisms" (`registry/human_verification_queue.csv`).

### 4.2 SSOT gates that consume these artifacts
- **G14** (SSOT L17074–L17104): G14-1 versioned process-event schema + provenance/tier/missingness; G14-2 dataset card with per-field coverage and source/study/platform distribution; **G14-3 human-verified held-out test labels**; G14-4 shortcut/null/tabular baselines; G14-5 ingredient×process pair-holdout; G14-6 source/study-disjoint where study IDs exist; G14-7 condition contribution vs label-only; G14-8 missingness robustness; G14-9 calibration/interval/risk–coverage; G14-10 evidence-quality stratification; G14-11 multiple-seed/clustered uncertainty; G14-12 final decision record. Promotion: "If LightGBM/TabPFN > FiLM/cross-attention under the strongest splits, ship/report the simpler model."
- **G15** (SSOT L22376–L22427):
  - G15-1 data audit ("Every quantitative row has source/study, evidence tier, units/target definition, yield/normalization status, and censoring/missingness status").
  - G15-2 "Canonical D0–D6 are reported on all eligible headline splits before D7+ claims".
  - G15-3 process signal on a process-disjoint split.
  - G15-4 "At least one focused D-C dataset supports an identifiable/useful kinetic fit with profile/bootstrap/posterior uncertainty".
  - G15-5 condition-OOD.
  - G15-6 "Real, study-disjoint calibration".
  - G15-7 abstention on REAL calibration data.
  - G15-8 consistency.
  - G15-9 completion.
  - G15-10 "no synthetic/imputed target enters final test/calibration".
  - G15-11 "A trust horizon is empirically established on D-C/D-D where true intermediate states exist; no rollout claim otherwise".
  - G15-12 inverse design.
  - G15-R reproducibility.
  - G15-H "Every LLM-extracted row used in held-out test/calibration is human verified against the cited source span/table".
  - G15-I integration.
  - G15-RXN (5 conditions), G15-HYB, G15-INV ("inverse-design ceiling ≤ forward-model credibility").
- **G16** (SSOT L27444–L27487): G16-DATA "Deep Gold exists with independent annotation/adjudication"; G16-QTY "food-specific portion conversions have provenance; qualitative/unknown quantities are not fabricated"; G16-CAL "calibrated on held-out independent gold"; G16-TRANS "No Level-15 fallback is used for a target/domain until the relevant G15 gates pass"; G16-PROV; G16-OOD; G16-FT.
- **Stop rules** (SSOT L27488–L27502), e.g. "Silver does not improve held-out Gold performance", "human verification cost exceeds the value of the proposed feature". Promotion order (L27503–L27521): Rules/lookup → strong simple baseline → structured model → learned model → agentic/optimization layer.
- **SSOT 236** (L25587–L25658): tiers Deep Gold ~750–1,000; Gold-Light ~3,000–5,000; Silver 60,000–100,000; large weak corpus 1M+; "the target is 100k structured real recipes, not 100k gold recipes" (L25599–L25602). Stage 0..10 scale-up (L25623–L25638). Batch checkpoints every 5k–10k (L25639–L25654).

Current standing against SSOT gates: per the experiment map, **none passed**. G14-3 is MISSING (0 human-verified EVD). G15-H applies to any future E4 row.

---

## 5. Data requirements and named sources (licence notes)

- **Held now (E3).**
  - USDA R6: 7,018 rows; licence ASSUMED public domain; row-level imputation not identifiable (`provenance_note = SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE`).
  - Bognár 2002: 7,090 rows; ASSUMED; "INGESTED 28/39 Part-2 tables" (manifest DS-002), so 11 tables are skipped.
  - Phenol-Explorer 3.6: 3,870 rows / 125 papers; redistribution needs permission; licence re-check failed with a TLS mismatch (manifest DS-003).
- **Local but not ingested / not in SRC.** USDA Cooking Yields R2 (`data/external/usda_yields`, DS-006 P0, CC0 reported by catalog), FNDDS, INFOODS density/AnFooD/uFiSh (DS-014, licence UNKNOWN), sustainablefooddb, CoSyLab sets (D-015, ASSUMED/DERIVED_ONLY), FDC raw/cooked pairs (867 pairs / 16,365 ratios; E6 candidates; "circular against R6" for imputed values, `reports/del2/fdc_pairs_v1.md`).
- **Acquisition manifest** (`registry/data_source_acquisition_manifest.csv`, 64 sources): EXISTING 19, P0 3 (DS-006 USDA cooking yields, DS-032 Europe PMC, DS-040 OA food-science publishers), P1 16, P2 17, BLOCKED 7 (IFCT, FoodAtlas NC, FlavorDB, paywalled TDM, thermophysical handbooks, KEGG/MetaCyc, RecipeDB API), PARK 2. **`time_series_available = no` for every row**: there is no structured open source for kinetic/physical time series (D-019: "structured open sources for mechanism/kinetic/physical time series not found (SOURCE_GAP for 13 of 16 priority-cell rows)").
- **Kinetic/mechanism routes are literature only**: DS-043 (OA physical-property/drying literature), DS-045 (OA kinetic-parameter literature), DS-046 Rhea (CC BY 4.0), DS-047 BRENDA (CC BY 4.0 with acceptance), DS-044 ComBase (terms unverified), DS-049 EFSA acrylamide occurrence. `docs/RESOURCE_GAP_MAP.md` notes "BioModels BIOMD0000000052 (§175.3) Maillard ODE (sugar–casein) open — later (P9)". This is a candidate first-simulator reference (UNVERIFIED here; needs research).
- **Recipe licences.** Only Gutenberg is training_allowed=YES (73,955). Food.com (522,517) is CC0 as declared by the uploader, but the uploader's authority is not verified. BBC A1 is RESTRICTED / LOCAL_RESEARCH_ONLY. Wikibooks is CC BY-SA (share-alike constraint on release).
- **External data used as checks.** OpenPI food subset (MIT; 197 procedures, 7,629 free-text state changes; "Not measured physics", `data_foundation_audit.md` L39). TASTEset (licence UNVERIFIED per usage registry; MIT per RESOURCE_GAP_MAP: conflict).
- **H2 approvals pending**: `reports/h_state/es_1_2_h2_approval_queue.md` (21 items). Census L138 asks for decisions #1/#3/#4 before the Step 10 pilot.

---

## 6. Dependencies on other levels/steps (as the artifacts encode them)

- Step 07 human sub-gate → "Step 08 only after the gate" (WORKLOG S133 L913–L918). The 07I-R gate lists both packets as pending human gates.
- Step 08 (lineage) must fill `STUDY.design`, platform (MEAS), replicates, study/publication ids, independence groups for USDA/Bognár, and the PE "design_strength UNKNOWN". These are needed for G14-6 / G15-6 study-disjoint evaluation; S-6 is currently "Phenol-Explorer only" (`transition_bootstrap_v0_contract.md` L20).
- Step 10 is defined in repo text as "STEP 10 / ES-1.3 -- 20-row mechanism evidence extraction + human-verification pilot. Required first: your review of this census and H2 decisions #1, #3, #4 … the choice of the pilot mechanism. The counts favour potato frying/acrylamide (Q05: 910 OA full-text hits …) over garlic alliinase (Q01: 404 / 24) and onion LFS (Q03: 34 / 2)" (`reports/h_state/es_1_2_source_census.md` L138). It depends on HV-001/HV-002 protocols.
- Steps 16–17: D-020 "Steps 16-17 later reuse the frozen components for instruction/event semantics only" (DECISIONS L121). NER covers ingredient lines only, so the instruction-level gap (SX-08-05) is "the real upstream gap for B11" (`ssot15_state_program_inventory.md` L57).
- Step 18 (event sourcing): the engine exists, and the EVT/STATE/GRAPH migration is "BLOCKED_FUTURE_STEP". The join key `recipe_identity_fk_v1` (recipe → group → family) exists.
- Step 19 (Gold trajectory pilot): the tier registry explicitly references "Step-19 style blind re-annotation" for DEEP_GOLD. Gold firewall: 50 Gold, 0 same-group non-Gold members, 2 with family relatives (`final_recipe_database_statistics.md` L176–L184). The identity calibration labels (400 pairs) gate any family-disjoint split.
- Step 29 (TRANSITION_BOOTSTRAP_V0) depends on the ES-1.1 export, the SVAR duplicate mapping, split families S-1..S-7 and grouping rules (contract L20). Its DEL-2 machinery (pandas) needs an environment.
- Step 36 / RAG: `decision/*` depends on EVD packets, compatibility and the frozen linker. C9 is blocked by G16-TRANS until G15 gates pass.
- Representation (Step 35): MOL/IMAP exist. ECFP is derivable ("RDKit in base python" on the Mac; inventory L26; UNVERIFIED on this server). `classical/` is empty, so L7–L8 baselines (n_ij, IDF, null models) are missing.

---

## 7. Risks / failure modes visible in the implementation

1. **Human-gate bottleneck.** Every scientific promotion is blocked on Kush/Parv. 10 HV queue items are NOT_STARTED/BLOCKED_HUMAN. The v1 and v3 condition packets were returned with implausible provenance (11 s apart; identical columns). This is a repeated integrity risk for "human" labels (protocol L86, L98).
2. **Thin, single-tier evidence.** 0 E1/E2/E4. Moisture/pH/aw are 0%, temperature 33%, duration 17%, mechanism rows 0. One physical SVAR (yield). EVD touches 165 of 2,048 ING and 36 of 156 PROC (`data_foundation_audit.md` L44–L45).
3. **Negative cold results.** On USDA/PE, D0 persistence wins or ties under matrix/process/study-disjoint splits. The one positive cold result (Bognár process-disjoint) rests on a degenerate CI. Do not overclaim.
4. **Censoring assumption.** Training at lower bound 0.975 for censored rows is an assumption (33% of rows are censored). Bognár is ~50% censored.
5. **Retention semantics mixed.** USDA %TR vs %AR is not distinguished at row level. PE retention type RT-003 is AMBIGUOUS. 278 PE rows have retention ≠ (after/before)×yield (conflict C4/C5).
6. **Gold quality.** All Gold is AI-drafted + human batch-approved ("reviewed it all, all good", `reports/gold/foodcom_ai_assisted_human_review.md` L4). The Kush and Parv sets are identical, so agreement is non-informative. 108/113 coref mentions are UNKNOWN. The linker gold had κ 0.317 before adjudication, so **semantic IAA on hard items is low**, and Deep Gold sizing must budget adjudication.
7. **Compiler weakness.** State-field accuracy is 0.10 and Transform is over-generated (169 vs 64). Predicted-state experiments would test extraction rather than state value.
8. **Identity recall.** 4,745 ingredient-LSH buckets were skipped over cap. Near-duplicate recall is unmeasured. Calibration is unlabeled, so families can't yet be used as split locks (only exact groups can).
9. **Licence.** 535,151 recipes have training_allowed UNKNOWN. Silver at 60–100k would mostly come from Food.com and needs an H2 decision before any model training.
10. **Reproducibility on this machine.** recipe_semantics, A1 raw, Gold JSONs and packets are absent. pandas/pyarrow are missing. A100 throughput over VPN is 13–90 KB/s (D-025). Re-running frozen pipelines here is impossible without the Mac or new copies.
11. **Test suite.** A known hang in test_transition is deselected (S134).
12. **Schema look-ahead gaps** (detail in §10): no SIM/KINETIC/PARAM/FORMULA/SAMPLE schemas; the SPLIT strategy enum lacks group/family/condition/platform/publication; RXN has no rate law.
13. **Fixed scalar blends** in places the SSOT forbids a priori weights. Retriever rank 0.35·bm25 + 0.65·compat (`retrieval/retriever.py` docstring). Identity ranking weights (allowed only "because the score ranks", `max_plan_consensus.md` L43). `confidence_vector` emits `retrieval: 0.0` when there is no evidence: minor, but it's a numeric 0 rather than None.

---

## 8. MAPPING TO THE 36-STEP SPINE (what this implementation material requires per step)

This is a reconstruction; the step-card text is unavailable. Statuses come from repo evidence.

- **01 Freeze project authority** — DONE in substance: `registry/plan_authority_map_v1.csv` (28 rows), `reports/step07i/plan_authority_inventory.md`. Requires adding the missing 36-step plan v1 and MAX v3.0 as "NOT FOUND", and regenerating `STATUS.md` (stale since S083). Output: an authority map with versions/hashes. Gate: no unresolved SSOT_CONFLICT (07I consensus found none).
- **02 Audit implementation state** — DONE as MP-0 (`ssot15_state_program_inventory.md`, `data_foundation_audit.md`, experiment map 123 rows) and refreshed by this audit. Requires a machine-portable inventory (which artifacts are local vs Mac-only) and a status-per-component table (§0 above).
- **03 Freeze state semantics** — DONE as MP-1 DRAFT (`state_representation_contract_v1.md` "Status: DRAFT FOR REVIEW", L3). Open conflicts C1–C8 (L64–L72); C1 was ruled (D-018) and C2–C8 have no recorded ruling (UNVERIFIED). Needs: ruling on C2 (E3 bootstrap ≠ Gold), C3 (SVAR duplicates; mapping exists), C7 (AI-drafted PROC mechanism families), C8 (Q/R/X profiles); state_variable_registry status rules; STATE/EVT/ENTITY schemas (exist).
- **04 Freeze evidence / provenance / similarity contracts** — DONE in substance: evd_contract_v1, tier map, provenance classes, `simulated_state_changes_schema_v1.csv`, similarity registry 21 types FROZEN. Missing: lineage contract (SOURCE→DOCUMENT→STUDY→EXPERIMENT→SAMPLE→MEASUREMENT→AGGREGATE→DERIVED) — only SRC/STUDY/MEAS/EVD exist.
- **05 Normalize EVD** — DONE (ES-1.1 PASS). Inputs: EVD/SVAR/COND/PROC/ING/SRC ledgers. Outputs: export (sha e61d7db4…, regenerable), matrix/prior-state tables, SVAR duplicate mapping (11 pairs + 7 equivalent candidates not merged). Residual: the 7 EQUIVALENT_CANDIDATE SVARs need an analytical review.
- **06 Freeze source acquisition manifest** — DONE as ES-1.2 (64 sources, capability matrix, 30 query templates, 16 priority-cell rows, 21 H2 items). Residual: H2 decisions #1/#3/#4; SRC registration for Food.com/TASTEset/USDA yields/FNDDS/INFOODS (manifest notes "provenance gaps to close before use", census L9).
- **07 Condition & measurement normalization** — Automated: FROZEN (07H, 07H-R, fp e7d58913). **Human sub-gate: PENDING on packet v4** (κ ≥ 0.80 + no critical-field flag). 07H-R recipe base FROZEN; 07I-R identity PROVISIONAL with the 400-pair calibration open. Required before Step 08 per WORKLOG: a genuine blind v4 pass and a recorded `step07_agreement.py` result. Also: the content finding (calendar months stored as seconds at ingest) was fixed in 07H-R; confirm in the v4 audit.
- **08 Scientific source lineage** — NOT STARTED. From this material it must produce: STUDY design (currently UNKNOWN ×125), platform/method per study (MEAS 3 → per-platform), replicates (`n_replicates` exists but is unpopulated), study↔publication↔lab grouping, aggregate→primary-source links for USDA/Bognár where identifiable (else NOT_IDENTIFIABLE), donor groups for USDA imputations, and independence groups usable by the S-6 study-disjoint split (`transition/splits.py` study_disjoint "refuses when impossible"). Gate idea: every EVD row has a lineage status (no blanks), and connected-component study groups are computable.
- **09 Evidence extraction & verification machinery** — PARTIAL: `evidence/precheck.py` (AI/rule pre-check, "Never human verification"), `doi_resolve.py`, `literature.py` (OpenAlex), `link_review.py` (human-signed), `tools/apply_human_review.py`, `registry/evidence/human_review_pack_v1.csv` (55 rows), verification queue (634). Requires: an E5→E4 promotion workflow tied to source span/table (G15-H), a design-strength vs verification split (D-018), a two-person protocol for benchmark-critical rows (HV-002), and a timing measurement per row (forecast assumes 2–5 h per cell).
- **10 20-row mechanism pilot** — NOT STARTED. Defined in census L138. Inputs: Europe PMC/OA routes (DS-032/040), query templates (`registry/evidence_query_matrix_v1.csv`). Output: 20 E4-candidate rows with COND populated, including pH/moisture where reported. Metric: human-hours per verified row, extraction precision. Choice: acrylamide vs garlic alliinase (decision pending).
- **11 Wave-1 verified mechanism evidence** — NOT STARTED. Target from HV-001: "first target >=40, aim 60-80 across several mechanisms". Must populate mechanism SVARs (currently FUTURE/MISSING) and RXN-like relations.
- **12 Structured database evidence** — PARTIAL (E3 retention only). Immediate wins named in census L8: USDA Cooking Yields R2 (local), 11 skipped Bognár tables, USDA Flavonoid DB 3.3, FNDDS/FDC portions, FDC Foundation Foods, CoFID, FSIS temperatures. FDC pairs must stay E6 (circular).
- **13 Large literature discovery corpus** — PARTIAL: verification queue 634 (OpenAlex), 30 Europe PMC query templates with metadata counts. Required: per-article licence, no full-text capture until H2 #1.
- **14 Coverage-driven evidence growth** — PARTIAL: `reports/h_state/hstate_missing_evidence_cells_ranked.csv` (58 real targets), `make_evidence_queue.py`, priority cells (`data_foundation_audit.md` L80–L81 top-20). Must use recipe demand (2,132 edges, 3.0% exact coverage) and Gold/H_STATE needs.
- **15 Freeze DATA-EVIDENCE v1** — NOT STARTED. Needs: a DATASET release record (DATASET ledger currently has only 5 recipe-corpus rows), SPLIT records (0), a dataset card per G14-2 / SSOT 236.7, and a human-verified held-out subset (G14-3).
- **16 Instruction semantic schema** — schemas exist (INST, EVT, ENTITY, STATE, REF, ALLOC, GRAPH, QNT). Must reconcile with the Gold handbook label set (`annotation/gold.py`: FOOD QUANTITY UNIT SIZE FORM STATE ACTION TOOL MEDIUM TIME T…) and the engine event types.
- **17 Instruction-level extraction** — NOT STARTED (SX-08-05). Baseline: rule compiler (state-field acc 0.102). Reuse the frozen NER/linker only (D-020). Must run over the 612k base in streamed partitions (pattern: `identity/pipeline.py`).
- **18 Event-sourcing engine** — PARTIAL: engine + 15 tests + replay contract tests. Needs persisted EVT/STATE/GRAPH ledgers (0 rows), a migration, and session review (0/30).
- **19 Gold state-trajectory pilot** — BLOCKED_HUMAN: 40 GOLD_PENDING_INDEPENDENT_IAA. Blank independent bundles are frozen (`annotation/gold/evidence_first_expansion/freeze_hashes.json`). S116 eligibility is 0/84 confirmed (HV-005). Forecast: +20 independent Gold = ~32–49 h human (`h_state_coverage_lift_forecast.md` L49).
- **20 Scale procedural semantic corpus** — NOT STARTED: `silver/` is empty. Requires licence clearance (training_allowed UNKNOWN for 535k), SSOT 236.5 stages, and identity-group dedup before sampling.
- **21 Effect / mechanism ontology** — NOT STARTED. Seeds: RXN relation enum, PROC.mechanism_families (AI-drafted), SVAR registry.
- **22 Event → effect signatures** — NOT STARTED. Inputs: EVT (empty), PROC.required_condition_axes (106 PROC), KGE ING_PROCESSED_BY.
- **23 Mechanism applicability engine** — NOT STARTED. Requires COND axes populated (pH/aw/moisture/O2 are 0% today) and matrix facets (variety/part/geometry/storage_ripeness mostly null).
- **24 Formula / model registry** — NOT STARTED (no schema; MODEL is the ML card).
- **25 Parameter-compatibility retrieval** — NOT STARTED. The closest artifact is `retrieval/compatibility.py` (axis vector MATCH/NEAR/MISMATCH/UNKNOWN), which could be extended to parameter domains.
- **26–28 Simulation** — NOT STARTED. Contract only (`simulated_state_changes_schema_v1.csv`, source_class.py). The validation-scope field requires held-out E1/E2/E4 data, of which there are 0 rows.
- **29 TRANSITION_BOOTSTRAP_V0** — contract DRAFT, NOT RUN. Inputs ready: ES-1.1 export; ING+PROC-linked retention rows (USDA 3,274 measured / 1,847 censored; Bognár 1,240/1,011; PE 3,718/0; yield 496, 323 linked). Independent units: USDA 171, Bognár retention 123, PE 287, Bognár yield 417 (contract L9–L10). Splits S-1..S-7; metrics L23–L24; criteria L26–L29.
- **30 Strong tabular / sparsity bake-off** — PARTIAL via DEL-2 (D5 GBM, D7 MF, propensity AUC 0.81–0.91, IPW). TabPFN SKIPPED (G15-2 requires D0–D6 including D6).
- **31 Physics / condition features** — NOT STARTED (SX-12-02 thermal dose/Arrhenius; temperature known 33%).
- **32 Focused kinetics** — NOT STARTED (no time-series source; G15-4).
- **33 Mechanistic vs ML vs hybrid** — NOT STARTED (G15-HYB).
- **34 Short rollout** — NOT STARTED. G15-11 requires true intermediate states; there are none.
- **35 Representation ladder** — NOT STARTED: MOL/IMAP data exist, `classical/` is empty, ECFP is not stored, and the similarity registry is FROZEN with mostly MISSING metrics.
- **36 Evidence compiler → RAG → FlavorTwin** — PARTIAL rule baseline (C1–C18 map in §1.9), silver-evaluated only. Missing: a locked human benchmark (D-008 PROPOSED), calibration on independent gold (G16-CAL), C9.

---

## 9. Contradictions, stale items, underspecified parts, open questions

1. **Step 07 human gate.** ctx.md flags `step07h_human_gate_result.json` as NOT_COUNTED. Verified, but it is also **stale**: it is computed on packet v3 (fingerprint a5991a9cda56), and the protocol says v3 is invalid and v4 (e7d589136275) is the only valid input (`condition_audit_protocol.md` L97–L98). No v4 result exists. Current status: PENDING_HUMAN_SUBGATE.
2. **Similarity type count.** `ssot15_state_program_inventory.md` L3 and L32 say 15 types. `registry/ssot15_similarity_registry.csv` and contract §9 (L61–L62) say 21 types FROZEN v1. The inventory is stale.
3. **Family counts collide.** The 07H-R report says "recipe families: 611,700 (REC family_id kept; Food.com/TASTEset singleton identity families)" (L7). 07I-R reports 605,476 families (PROVISIONAL_STAR_V1). The two family notions share a name; downstream code must pick one explicitly.
4. **Gold accounting.**
   - `data_foundation_audit.md` L12 lists "DATA-SEM-GOLD … 20 recipes (Food.com)".
   - The compiler-vs-gold and S114 H_STATE numbers use the A1 pilot_20 Gold-v1/v1.1 (BBC).
   - The recipe base counts 40 GOLD_PENDING (20 A1 + 20 Food.com).
   - The Food.com v1.1 file has 310 events; the A1 pilot is reported elsewhere.

   Any plan must keep the two 20-recipe sets distinct.
5. **The Bognár "cold supported" claim** (inventory L47) relies on a degenerate CI (one held-out group): `BOGNAR-2002_results.md` process_disjoint D5 [0.0096, 0.0096].
6. **TASTEset licence.** MIT per `docs/RESOURCE_GAP_MAP.md` and `tools/eval_tasteset.py` docstring, vs LICENCE_UNVERIFIED / UNREGISTERED:TASTESET in the recipe usage registry and D-024. Needs a ruling.
7. **Frozen artifacts absent locally.** The 07H-R gate's determinism list includes 5 `ledgers/recipe_semantics/*` parquets that are not on this machine, so the freeze cannot be verified here for those files. (recipe_base hashes do match.)
8. **Schema vs sync-matrix mismatch.** The sync matrix lists SIM, KINETIC, HYP and LOT/ENT as ledgers with 0 rows (BLOCKED_FUTURE_STEP), but no schemas exist for them in `ledgers/schemas/` (37 schemas; none named SIM/KINETIC/HYP/LOT).
9. **MP W5 STUDY fields** (design, sample prep, controls, replicates, platform, equipment, condition completeness, quality flags; MP L1675–L1686) vs implemented STUDY (design + source_id only). **MP X7 SAMPLE-** (MP L2049–L2070) is not implemented.
10. **RXN schema vs MP W6**: rate law/kinetic parameters and condition window are missing.
11. **SPLIT.strategy enum** {RANDOM, PAIR_HOLDOUT, INGREDIENT_DISJOINT, PROCESS_DISJOINT, STUDY_DISJOINT, SOURCE_FAMILY_DISJOINT, TEMPORAL, OTHER} lacks duplicate-group/family-disjoint, condition-OOD, platform-disjoint, publication-disjoint and matrix-OOD (brief §33).
12. **STATUS.md** is stale (body S083; header 2026-10-22). The WORKLOG is authoritative (07I plan_authority_inventory L84).
13. **Test suite** not fully green (S134: hang deselected).
14. **NER/linker never applied to the 612k base.** D-024: "the frozen NER/linker/router were NOT re-run -- needs a GPU-server run". The GPU plan conflicts with ctx (server GPUs are not to be used). Is CPU inference of DeBERTa-base over ~5M ingredient lines feasible? UNVERIFIED; needs a quick estimate.
15. **MISSINGNESS semantics** in `final_recipe_database_statistics.md` L214–L250 (e.g. Gutenberg has_quantities 0.9305). The values appear to be missing-fractions despite "has_" labels (UNVERIFIED interpretation; clarify).
16. **Experiment-map columns** input/baseline/arm/metric/split are "NOT_SPECIFIED_IN_PLAN" for many SX ids (inventory L85). They must be frozen in experiment cards before running.
17. **Open research questions** (external):
    - (a) First simulator candidate: BioModels BIOMD0000000052 Maillard ODE is listed (RESOURCE_GAP_MAP). Verify its existence, scope and validation data.
    - (b) Whether any open time-series datasets exist for vitamin C / chlorophyll / acrylamide kinetics in foods (manifest says none structured).
    - (c) USDA R6 %TR vs %AR documentation, and whether row-level identification is possible.
    - (d) Phenol-Explorer retention-factor definition (primary source; RT-003 AMBIGUOUS).
    - (e) Near-duplicate threshold calibration literature (SSOT 264.8 forbids a universal threshold).
    - (f) IAA targets for event/state annotation, given the observed κ 0.317 on linking.
    - (g) Licence of USDA Cooking Yields R2, INFOODS density, CoFID, FoodEx2/LanguaL.
    - (h) Feasibility of CPU NER over the base.

---

## 10. LOOK-AHEAD: fields earlier steps must capture so this material is usable later

**Step 03/04 (state + evidence contracts)**
- Add a lineage entity chain with ids: `document_id` (publication), `study_id`, `experiment_id`, `sample_id` (MP X7 fields: lot/source, preparation, mass, geometry, replicate, QC/calibration, operator, date), `measurement_id`, `aggregate_of[]` (for database rows citing primary studies), `derived_from[]`.
- Add a `simulator/model registry` contract: model_id, mechanism_id, equation, state vars, parameters with units/source, assumptions, IC/BC, matrix/condition scope, calibration/validation sources, identifiability, solver, uncertainty, status.
- Add a `parameter` record: value/interval, unit, T_ref, matrix, condition window, source EVD/KINETIC ids, fit method, covariance.
- Add `KINETIC` (time-series points with t, T(t), C(t), replicate, censoring).
- Add a `SIM` ledger schema matching `simulated_state_changes_schema_v1.csv`.
- Extend `SPLIT.strategy` with DUPLICATE_GROUP_DISJOINT, FAMILY_DISJOINT, CONDITION_OOD, PLATFORM_DISJOINT, PUBLICATION_DISJOINT, MATRIX_OOD.
- Extend `RXN` with rate_law, kinetic_parameter_ids, condition_window, inhibitors/competing mechanisms.

**Step 05 (EVD)**
- Keep `basis`, `retention_type`, `censor{kind, limit}`, `value_origin` (SOURCE_IMPUTATION_POSSIBLE), `canonical_variable_id`, `matrix_id`, `prior_state_id`.
- Add `n_replicates`, `sd/se`, `uncertainty_type`, `lod/loq` when the source gives them.
- Add `time_point_index`/`series_id` for trajectories.
- Add `table/figure locator` (provenance.locator exists; make it required for E4).

**Step 06 (manifest)**
- Per-source `time_series_available`, `replicate_information`, `study_lineage_available`, `per_article_licence`, `full-text capture permission`.
- SRC registration for every local file before ingestion (Food.com, TASTEset, USDA yields, FNDDS, INFOODS).

**Step 07 (conditions)**
- Ensure the COND ledger actually populates `ph_initial/ph_final`, `moisture` (with WET/DRY basis), `water_activity`, `oxygen`, `salt/sugar/fat`, `geometry/thickness/particle_size`, `heat_transfer_mode`, `temp_core vs setpoint vs medium vs surface`, `trajectory` (common time axis), `preheat_status`, `batch_size`, `container material`, `maturity/storage_age`.
- These are needed by Step 23 applicability (activation windows), Step 26 simulator ICs/BCs and Step 31 thermal-dose features. Keep the AMBIGUOUS reason codes; never default.

**Step 08 (lineage)**
- `study_id` for every row (or NOT_IDENTIFIABLE with reason), `publication_id`, `lab/group`, `platform` (HPLC/LC-MS/…, MP W5), `extraction protocol`, `calibration`, `controls`, `randomisation`, `independence_group` that survives to SPLIT, `donor_group` for USDA imputations, and a shared yield-source id for PE (103 yield records; contract C5).
- These enable G14-6 / G15-6 study-disjoint and platform-disjoint splits.

**Step 09 (verification)**
- `verifier`, `verified_at`, `verification_span/table`, `second_verifier` (benchmark-critical), `disagreement/adjudication log`, `time_spent_minutes` (human-hour model), and `design_strength` separate from tier (D-018).

**Steps 10–15 (acquisition)**
- For each row capture: before/after with units and basis; process conditions per §Step 07; matrix facets (variety, part, form, geometry, ripeness, prior processing); sample mass/size; replicate count and dispersion; measurement time points (for kinetics); the mechanism the authors claim (as a claim, not truth); competing products measured; censoring/LOD/LOQ.
- Without time points and condition windows, Steps 24–27 have nothing to fit or validate (G15-4 needs "profile/bootstrap/posterior uncertainty").
- Step 15 release must emit DATASET + SPLIT records with `assignment_sha256` and `leakage_report_path`.

**Steps 16–20 (recipe semantics)**
- INST `sentence_spans`; EVT `input_state_ids/output_state_ids`, `tool_ids`, `condition_id` (linked to normalised condition mentions), `endpoint` (ENDPOINT family has 906k expressions), `trajectory=PLANNED` for recipe text, `omitted_step_candidate`.
- STATE `variables` restricted to observable procedural/physical descriptors with belief=PLANNED; REF coref chains; ALLOC fractions with basis; QNT `q_level` + `conversion_path` + `portion_id` (POR only after human-verified FDC links, D-006).
- Carry `duplicate_group_id`/`recipe_family_id`/`split_lock_group_id` on every derived row, `source usage_class` / `training_allowed`, and `extractor version` + model hash. This is what Steps 22 (event→effect), 29 (state-conditioned transition), 36 (state reconstruction C3/C4) and Gold leakage control need.
- Record `source_plane=RECIPE` and `observation_class=TEXT_STATED` so no recipe value is ever used as a magnitude (`source_class.py`).

**For Step 35/36 consumers**
- Keep IMAP `basis/concentration/state_id_or_form` (presence ≠ abundance).
- Store ECFP/MACCS per MOL when computed, with the fingerprint parameters (frozen baseline: Morgan r2, 2048-bit, chirality on, binary Tanimoto, contract L62).
- For RAG, every EVD/packet row needs `independence_group`, `conflict_cluster`, `verification_status` and `applicability` so C12/C14 can compute support without collapsing duplicates.
