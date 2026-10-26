# READER "gov" — Governance, step history, gates, negative results (CulinaryState)

Scope read in full: `WORKLOG.md` (S001–S134, 925 lines), `DECISIONS.md` (D-001..D-025, 143 lines), `STATUS.md` (129 lines), `registry/plan_authority_map_v1.csv` (28 rows), `reports/step07i/plan_authority_inventory.md`, `reports/step07i/max_plan_consensus.md`. Bodies of the step reports that define gates were also read: `reports/h_state/ssot15_state_program_inventory.md` (MP-0), `reports/h_state/state_representation_contract_v1.md` (MP-1), `reports/h_state/transition_bootstrap_v0_contract.md`, `reports/es1/es1_1_audit.md`, `reports/h_state/es_1_2_source_census.md`, `reports/h_state/es_1_2_h2_approval_queue.md`, `reports/step07/step07_report.md`, `step07h_normalizer_hardening_report.md`, `step07h_full_recipe_base_report.md` (§A–G), `condition_audit_protocol.md`, the four gate JSONs (`step07h_gate_result.json`, `step07h_human_gate_result.json`, `step07hr_gate_result.json`, `step07ir_gate_result.json`), `reports/step07i/preregistration_v1.md`, `identity_benchmark_report.md`, `identity_summary_v1.json`, `duplicate_calibration_packet_manifest.json`, `experiments/EXP-000001..7/card.md` (headers), `registry/human_verification_queue.csv`, `reports/step07/step07h_ledger_sync_matrix.csv`, `docs/BACKLOG_NONBLOCKING.md`, selected NER/linker closeout reports, and `git log` (read-only). Small read-only stdlib diagnostic on `ledgers/data/EVD.jsonl` (independence groups / study status).

Citation key: `W L###` = WORKLOG.md line; `DEC L###` = DECISIONS.md line; `ST L##` = STATUS.md line; `MP0 L##` = ssot15_state_program_inventory.md; `MP1 L##` = state_representation_contract_v1.md; `TB L##` = transition_bootstrap_v0_contract.md; `ES11 L##`, `ES12 L##`, `H2Q L##`, `S07 L##`, `PROT L##` (condition_audit_protocol.md), `PRE L##` (07I preregistration), `CONS` = max_plan_consensus.md, `PAI` = plan_authority_inventory.md, `MPv4 L####` = Final Master Plan v4.0. Commit hashes refer to `git log` of this clone (main @ f36b525).

**Headline governance facts**
1. The 36-step spine numbering appears in the repo only from S129–S134 (2026-10-22). Everything before (S001–S128) was organised by Master-Plan blocks B00–B17, course deliverables DEL-1..DEL-5, the D-009 expansion queue X1–X15, and "S119 block" NER work. No artifact named "Step 01"–"Step 04" exists; Steps 01–06 must be reconstructed from MP-0 / MP-1 / ES-1.1 / ES-1.2 artifacts (mapping below is INFERRED, not stated by any repo file, except Step 06 = ES-1.2, which is implied by "Step-06 source-note corrections" in S07 L28 and `step07h_ledger_sync_matrix.csv` row SRC "Step 06 / H2").
2. WORKLOG has a **gap**: ~75 commits on 2026-10-21 10:06 → 2026-10-22 00:00 (V2-DM decision model, fresh linker gold, CulinaryLinkDecision D3, CulinarySpanDecision CSD-C, external validation protocol, data-foundation audit, MP-0, MP-1) have **no S-entry**. S128 (W L878, 10-21 01:55) jumps to S129 (W L885, 10-22 00:13). Evidence for those steps exists only in commits (e.g. cf2bf25…44a2bb1, a87b614, 1095204, 5e8faae, 763e51a, 084df7e, d0ce5f5) and reports (`reports/ner_v2/*`, `reports/h_state/*`, `reports/ssot15/*`). This violates the "one entry per step" rule (W L3).
3. No SSOT-level empirical gate for L12–L16 is passed (MP0 L10, L49: "Gates (47 listed): PARTIAL 21, MISSING 26, none passed").
4. The Step-07 human condition audit has **not** validly passed: `step07h_human_gate_result.json` → `"gate": "NOT_COUNTED_PROVENANCE_INVALID"`, `"pooled_kappa": 0.9978`, `"gate_as_computed": "FAIL_OR_ADJUDICATE"`, `"counts_as_human_gate": false` (v3 files written 11 s apart, 899/900 identical cells). Packets v1–v3 are invalid; only packet v4 (fingerprint e7d589136275) is valid and it is unlabeled (PROT "Update (07H-R, packet v4)"; D-024 DEC L133–137 last sentence; S133 W L918).
5. Step 08 is explicitly NOT authorised (S132 W L911, S133 W L918, S134 W L925; D-025 DEC L139–143 "Step 08 remains unauthorised").

---

## 1. Definitions, entities and data contracts (field-level where given)

### 1.1 Ledger system (governance-level)
- 36 record types as JSON Schema 2020-12 with common envelope (version, status, provenance, verification): SRC SNAP API STUDY MEAS ING ALIAS ENTITY MOL IMAP PROC TOOL COND SVAR UNIT QNT POR ALLOC REC INST EVT STATE REF GRAPH EVD RXN WARN ALLERGEN DATASET SPLIT MODEL EXP GATE RQ RS CLM (S006 W L38). Later KGE added (D-011 DEC L70–74; S036 W L248). D-002 (DEC L10–13): JSON Schema + Python semantic validators, not pydantic (reversible, flagged for review).
- Encoded laws (S006 W L38): AI ≠ human verification; E4 needs HUMAN_VERIFIED; AH1 origin_type/study_ids; locator for E1–E4; percent-change consistency; censor flag; no invented grams (QNT needs POR for non-mass units); POR needs source; IMAP 4 relation types; 'medium heat' never numeric; STATE append-only + observation override; FlavorDB never allergen authority; SOTA claim needs GATE; TEST-selected checkpoint ≠ clean reproduction.
- Append-only store; `LedgerStore.upsert`; IDs never reused (CLAUDE.md; D-010 DEC L65–68: version number is authoritative order; pre-S035 `created_at` on v≥2 means v1 time).
- AH1 (MPv4 L2757–2783): `origin_type ∈ {PRIMARY_STUDY, DATABASE_AGGREGATE, REVIEW_AGGREGATE, AUTHORITY_STANDARD, PROJECT_MEASUREMENT}`; `source_family_id` always required; `study_ids` required for primary-study/literature rows when identifiable, optional for database aggregates, **never fabricated**. Current data (read-only diagnostic of EVD.jsonl): DATABASE_AGGREGATE 14,108 (USDA-RETN-R6 7,018; BOGNAR-2002 7,090) with `study_id_status = NOT_IDENTIFIABLE`; PRIMARY_STUDY 3,870 (PHENOL-EXPLORER-3.6) with `PRESENT`; `independence_group` distinct values: USDA 1, Bognár 1, PE 125 → **127 independence groups in total**. `design`: DATABASE_AGGREGATE (14,108), UNKNOWN (3,870 PE).

### 1.2 MP-1 identities and state (MP1 L6–47) — Step 03 material
- Identities never collapsed (MP1 L6–14): A `ING-` concept; B `ENTITY-`/`STATE-` lot/version (append-only); C state S_{i,t}; D `PROC-` action family ("a process name is not a chemical cause"); E `COND-` full condition profile θ, each axis MEASURED/RANGE/UNKNOWN/NOT_APPLICABLE; F history H_t as explicit event list; G evidence `EVD-`/`RXN-`/`SIM-` with tier + provenance class; H learned z (optional, never replaces explicit state).
- Factorised state (MP1 L17): S_{i,t} = {C chemical, P^phys physical, Y^sens sensory, N nutrition, Q quantity/mass, R procedural, X safety, U uncertainty/missingness/evidence metadata}. Q, R, X are extensions beyond SSOT 106 (MP1 L19; conflict C8 L72). V/A observations out of scope (L18).
- State-variable record fields (MP1 L34): state_variable_id, name, family, subfamily, definition, datatype, unit, before_allowed, after_allowed, delta_allowed, direction_allowed, retention_allowed, logfold_allowed, measurement_family, gold_eligible, simulation_eligible, evidence_required, current_row_count, current_evidence_tiers, current_coverage_status, SSOT_source, status (+ canonical_variable_id, n_distinct_process_signatures, source_families, notes).
- Registry result (MP1 L35): 254 rows — ACTIVE 59, PROVISIONAL 73, MISSING_EVIDENCE 81, DUPLICATE 11, FUTURE 30. Rules: **ACTIVE = ≥50 active EVD rows, ≥3 process signatures, single analyte; PROVISIONAL = 10–49 rows or aggregate; MISSING_EVIDENCE = <10 rows**; FUTURE ids `SVAR-FUT-###` provisional (L36).
- UNKNOWN/missingness (MP1 L38–43): UNKNOWN first-class, never 0, never LLM guess; censoring carried through every metric; `delta`/`log_fold_change` derived only from MEASURED eligible inputs; log requires strictly positive, never from censored retention; basis part of the value; no cross-basis pooling; yield is its own mass-profile target; a PE yield factor attached to a concentration row is a covariate, not an independent observation.
- Frozen output contract (MP1 L47, citing SSOT 141): each proposed transition is `unsupported` / `physically_possible` / `evidence_supported`; numeric yield only from measured change or calibrated model with initial conditions.

### 1.3 Tier vs provenance class (MP1 L49–53; `registry/evidence_tier_provenance_map_v1.csv`; D-018 DEC L115) — Step 04 material
- Tier E1 controlled experiment with measured conditions; E2 partial conditions; E3 database aggregate; E4 structured/LLM extraction human-verified; E5 extraction unverified; E6 mechanism rule/MODEL_ESTIMATED; E7 SIMULATED.
- Provenance class: EXPLICIT_SOURCE, EXTERNAL_VERIFIED, DERIVED_DETERMINISTIC, INFERRED_LLM, MODEL_ESTIMATED, IMPUTED, SIMULATED, UNKNOWN.
- Primary evaluation eligibility: E1–E4 only; E5–E7 never Gold truth; held-out test/calibration labels need human verification (G14-3, G15-H) (MP1 L52).
- Ruling C1 (D-018): `evidence_tier`, `verification_status`, `design_strength`, `provenance_class` are four separate export fields; human review never changes tier; E3 aggregates never promoted to E1/E2; E1–E7 ontology unchanged.
- FDC raw/cooked pairs (867) are E6 candidates, not ingested (tier map row E6; S050 W L344–348).

### 1.4 EVD export contract (ES-1.1; ES11 L1–47; D-018) — Step 05 material
Fields added in an export view (no ledger rewrite): `evidence_tier`, `verification_status`, `design_strength`, `provenance_class`, `provenance_note` (USDA: `SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE`), `matrix_id` (hash of normalised matrix object + reversible lookup `exports/evd/evd_matrix_table_v1.csv`), `prior_state_id` (`PST-` hash of raw descriptor; vocabulary pending MP-5A), `lod`/`loq` (null everywhere; `lod_loq_status = NOT_REPORTED_BY_SOURCE_ROW`), `delta_value`, `log_fold_change`, `log_retention_factor` (separate from log_fold_change, conflict C4), `*_reason_if_unknown`, `target_state_variable_id` + `canonical_variable_id` (11 duplicate SVAR pairs; 7 EQUIVALENT_CANDIDATE_NOT_MERGED). Counts: delta 3,870; log_fold_change 3,787; log_retention 11,503 (ES11 L18–20). UNKNOWN counts ES11 L24 (e.g. ingredient_id 6,409; prior_state_id 5,536; moisture/pH 17,978).

### 1.5 Condition representation (Step 07; D-020..D-024; S07 L6–23)
- Value types POINT / INTERVAL (open ends allowed) / TRAJECTORY / QUALITATIVE / UNKNOWN; status VALID / INVALID / AMBIGUOUS / UNKNOWN + reason codes (D-020 DEC L121–122).
- 40 condition variables (time 4, temperature 8 incl. setpoint/medium/surface/core/unspecified/trajectory/rate/preheat, chemical 11, physical 13, biological 4) plus 9 more controlled registries (value type, measurement basis, quantity form, retention type, censoring, value origin, measurement location, measurement method, heat-transfer mode) (S07 L6). Censoring codes: DETECTED, NON_DETECT, BELOW_LOD, BELOW_LOQ, ABOVE_CAP, CENSORED_UNKNOWN, NOT_REPORTED (S07 L9).
- Rules: "boiling" never 100 °C (BOILING_POINT_NOT_ASSUMED); absent pH/aw/moisture/pressure/O2 stay UNKNOWN; mixture pH never averaged; bare psi/bar AMBIGUOUS; percent vs fraction bare numbers AMBIGUOUS; moisture requires WET/DRY basis; reversed intervals INVALID, never swapped; trajectory temperature needs stated location (S07 L9). 07H (D-023 DEC L130–131): `> x` → low=x, open_low=True; month/year calendar durations never converted to seconds; hard bounds (INVALID PHYSICALLY_IMPOSSIBLE) vs plausibility bounds (AMBIGUOUS OUTSIDE_TYPICAL_CULINARY_RANGE); pH 0–14 plausibility only; uncertainty separate from range; pressure DIFFERENTIAL; Pint NOT adopted (test oracle only). D-022 (DEC L127–128): 13 notation rules in `registry/notation_rule_registry_v1.csv`; USDA abbreviations UNKNOWN_UNVERIFIED.
- D-013 (DEC L83–91): stated bounds are CENSORED GT_STATED/LT_STATED; approximations MEASURED with qualifier in raw.

### 1.6 Recipe base and identity (07H-R/07I-R; D-024, D-025; PRE)
- `recipe_base_v1.parquet` = 612,782 indexed members (89,565 REC ids + 522,517 Food.com + 700 TASTEset); REC immutable, base = pointers + hashes (D-024 DEC L133–134). Tiers SOURCE_RAW 600,828; SILVER_AUTO 11,914; GOLD_PENDING_INDEPENDENT_IAA 40; no DEEP_GOLD/GOLD_LIGHT. Food.com/TASTEset `source_id=UNREGISTERED:*` (H2 item). 177 Gutenberg ids RAW_SEGMENT_MISSING_LOCALLY.
- Derived recipe ledgers: `source_plane=RECIPE`, `observation_class=TEXT_STATED`, no E-tier (D-024). EVT/STATE/ENTITY/INST/QNT/POR/SPLIT/RXN/KINETIC/SIM **not created (BLOCKED_FUTURE_STEP)**. Note `ledgers/recipe_semantics/` is NOT present on this machine (ctx.md).
- Identity Levels (PRE L53–55): A DUPLICATE_GROUP deterministic only (raw_hash, rec_content_sha256, norm_text_hash, A1 canonical_url); B RECIPE_FAMILY `PROVISIONAL_STAR_V1`, `calibrated=false`; C DISH_FAMILY_CANDIDATE `INFERRED_CANDIDATE`. Relation classes (PRE L58): EXACT_BINARY_COPY, EXACT_NORMALIZED_COPY, MIRRORED_COPY, NEAR_DUPLICATE_SAME_RECIPE (reserved), SCALED_VARIANT, MINOR_FORMULATION_VARIANT, SAME_DISH_VARIANT, RELATED_DISH, DISTINCT, UNCERTAIN — only the first three coalesce.
- FK join table `ledgers/recipe_identity/recipe_identity_fk_v1.parquet`: `recipe_id → duplicate_group_id → recipe_family_id` (D-025; CONS row "Recipe state graphs").
- Calibration labels (PRE L80): SAME_RECIPE_COPY, SAME_RECIPE_MINOR_VARIANT, SAME_DISH_DIFFERENT_RECIPE, RELATED, DISTINCT, UNCERTAIN.
- Views (PRE L77): RECIPE_SOURCE_ALL, RECIPE_DEDUP_EXACT, RECIPE_FAMILY_VIEW, RECIPE_MODEL_ELIGIBLE (`training_allowed == YES`), RECIPE_RELEASE_ELIGIBLE (`raw_redistribution_allowed == YES`), RECIPE_GOLD.

### 1.7 Simulation contract (MP1 L58–59)
`provenance_class = SIMULATED`, tier E7, `may_enter_gold_evaluation = false`, simulator id/version/parameters/uncertainty/validation scope mandatory, `extrapolation_flag`. Eligibility per validated simulator: physical variables potentially eligible; chemical/sensory/nutrition/safety NOT_BY_DEFAULT. source_class mapping from `docs/simulator_data_contract.md`: STRUCTURAL_RECIPE → R only (never a magnitude); COMPOSITION → C/N, E3; MEASURED_TRANSITION → E1/E2/E4; COMPILED_RETENTION → E3; KINETIC → E1/E2/E4 if fitted to measured data with uncertainty; MOLECULAR_PRIOR/SENSORY_PRIOR/MODEL_GENERATED → E6; SYNTHETIC → E7. No `simulated_state_changes.csv` exists (MP0 L79).

### 1.8 Similarity registry (MP1 L61–62)
`registry/ssot15_similarity_registry.csv` — **21 rows SIM-01..SIM-21**, `freeze_status` column; fields OBJECT_A, OBJECT_B, REPRESENTATION, METRIC, REQUIRED_DATA, CONFOUNDS, BASELINE, GOLD_REQUIREMENT, CURRENT_STATUS. Frozen baseline fingerprint Morgan r2, 2048-bit, chirality on, binary Tanimoto, Dice excluded. Reaction-center similarity DATA-MISSING/RESEARCH-REQUIRED.

### 1.9 Benchmark task types (D-008 DEC L40–52) — later steps (36)
REVISED list (supersedes S024): T1 CURRENT_STATE · T2 NEXT_ACTION · T3 TRANSFORMATION_EXPLANATION · T4 PROCESS_SUBSTITUTION · T5 ADAPTATION (SSOT T5 equipment + T6 ingredient merged) · T6 MISTAKE_RECOVERY · T7 PROCESS_COMPARISON · T8 CHEMISTRY_RELEVANCE; evidence regimes as slices DIRECT / NEAR / UNSUPPORTED (ABSTAIN) / CONFLICT / AMBIGUOUS (ASK). Merge choice **open for Kush/Parv** (DEC L52). Tiers min 104 / target 320 / stretch 440 (S024 W L164).

### 1.10 KGE confidence (D-011 DEC L70–74)
Association confidence = 95% Wilson lower bound of P(object|subject); bands **HIGH (support ≥30, lift ≥2) / MEDIUM (≥10, ≥1.5) / LOW**; quantile edges n/(n+20); LLM-proposed edges never HIGH without human verification.

---

## 2. Models and baseline ladders (simple → strong → advanced)

### 2.1 Transition/retention (DEL-2 → TRANSITION_BOOTSTRAP_V0)
- DEL-2 ladder (S017 W L115): D0 persistence, D1 global, D2 process mean, D3 hierarchical shrinkage, D4 nearest compatible evidence, D5 HistGradientBoosting (categorical + masks), D7 biased MF with side-info; D6 TabPFN SKIPPED (not installed / GPU). LogTarget wrapper + median AE + MAE-log (S040 W L276). Censor-aware MAE, IPW MAE, split-conformal 90%.
- TRANSITION_BOOTSTRAP_V0 (TB L16–17, defined NOT run): **B-0 persistence (retention=1, yield=1); B-1 global mean delta; B-2 ingredient-conditioned mean (shrinkage to food group); B-3 process-conditioned mean; B-4 ingredient×process lookup with hierarchical fallback (exact → same ingredient + process family → same food group + process → global); B-5 simple tabular only after B-0..B-4 reported.** "No neural model is selected here; TabPFN or learned models are out of scope for V0."
- Cross-source agreement (S039 W L269): USDA vs Bognár L1 67 cells MAE 0.075, Spearman 0.61; L2 249 cells MAE 0.083, Spearman 0.69.

### 2.2 Retrieval / decision (DEL-4/5)
BM25 → dense (bge-small/base/large, e5-small/large, gte-large) → RRF hybrid → structured compatibility with oracle slots; cross-encoder rerankers (S057, S068 W L395, L472). Decision: structured primary, e5-large free-text fallback, no reranker, no dense blend (W L472). RQ16-03: structured compat vs CE-large (W L500). Generator ladder B0/B2/B5/B5F/B5T; deterministic template promoted, LLM rephrase unpromoted (S065–S066 W L451, L458).

### 2.3 NER / linker (closed)
Rules 0.774 → encoders 0.919–0.925 → +CRF 0.929 → large+CRF 0.933 (EXP-000005, S063 W L437); frozen v1 = DeBERTa-base+CRF + calibrator (logistic+isotonic on conf+M6) + router R6 (S127–S128 W L873, L880); TEST once (ACCEPT err 2.13%/2.09%, coverage 0.59/0.72). Linker: char TF-IDF 0.555 → e5 zero-shot 0.607 (S094 W L642) → contrastive +0.035 (S124) → BGE frozen (strict Acc@1 0.881 on 850 human gold; CulinaryLinkDecision closeout). **Contradiction**: EXP-000005 card says "KEEP DeBERTa-large+CRF" but the frozen v1 is DeBERTa-base+CRF (v3-large challenger, no TEST gain) — card is stale.

### 2.4 Recipe identity
Exact hashes → candidate generation (title blocks, instruction-shingle MinHash LSH 64 perms 16×4 word 4-grams, ingredient-token MinHash 32 perms 8×4, REC family co-membership) → pair features (missing stays missing) → fixed-weight **ranking** score (title_token 0.15, ingredient_idf 0.30, ingredient_id 0.10, multiset 0.10, instruction_shingle 0.20, process_seq 0.05, condition 0.05, quantity_profile 0.05) → provisional star family (PRE L61–65). Ranking-only; SSOT 264.2 forbids a-priori scalar weights as a decision (CONS B#3).

### 2.5 State compilation
Rule compiler (S014) vs Gold; event-sourced engine (S011); oracle cascade O1 gold concepts / O2 gold Adds (S107 W L733).

---

## 3. Experiments / hypotheses / RQs (governance record)
- EXP-000001..4 (DEL-2 retention; cards in `experiments/`): verdicts USDA "SUPPORTED on random split only; NOT supported under cold-start"; PE raw "NOT SUPPORTED"; PE log "NOT SUPPORTED"; Bognár "SUPPORTED incl. cold-start" with caveat "factors are averaged and largely templated … NOT evidence of generalisation to new foods".
- EXP-000005 NER Part-K layers (supported encoder>rules, CRF; kNN NULL).
- EXP-000006 RQ16-03 silver pilot (pre-registered 2026-10-18): success gate met on silver "mostly by construction"; KEEP structured; headline NEED_DATA (W L500).
- EXP-000007 H_STATE (RQ16-01), pre-registered 2026-10-19, NOT RUN (W L684; card header). Amendment A1 (S114 W L782): max supported H_STATE-R = 14 over 8 recipes; target 40 not forced. Needs human-written questions (HV-007 BLOCKED_HUMAN).
- SX map (`registry/ssot15_state_experiment_map.csv`, 123 rows): MISSING 75, PARTIAL 40, COMPLETE 5 (SX-08-01/02/03, SX-09-03, SX-10-02), BLOCKED_HUMAN 2 (SX-06-08 LLM extraction vs human; SX-07-01 annotation pilot agreement), DONE_NEGATIVE 1 (SX-08-04 retrieval/exemplar augmentation). SX ids exist only in the Master Plan, not in SSOT (MP0 L9).
- D-008 hypothesis labels H1–H4 (proposal) collide with human-gate labels H1–H8 (MPv4 L135–142) and with Master Plan section ids "H1. ID scheme", "H2. The ledgers" (MPv4 L533, L554). Naming collision → governance ambiguity (e.g. CONS cites "Master Plan H1 FAM- via MinHash ≥0.8" meaning section H1, not gate H1).

---

## 4. Gates, promotion and stop rules (exact ids/thresholds)

### 4.1 Human gates H1–H8 (MPv4 L135–142; ST L129)
| Gate | Definition (MPv4) | Current state (repo evidence) |
|---|---|---|
| H1 External communication | emails to Prof. Bagler / dataset owners | Draft `handoff/H1_email_bagler.md` (S089 W L605–610, item 4 = CoSyLab permissions); "Kush sends" — **send status UNVERIFIED**; Foodoscope key still pending (S111 W L764, S113 W L778); ES-1.2 H2Q #14–15 "CONTINUE H1", "OBTAIN written confirmation" |
| H2 Licences and acquisition | new scrape target, unclear licence, storing raw third-party text | 21-item queue, nothing executed (H2Q L1–27); Food.com/TASTEset UNREGISTERED H2 item (D-024); USDA abbreviation lookup (BACKLOG L11); Gate 1 (S116 W L796) approved Food.com LOCAL research use only |
| H3 Compute and money | jobs above `{{COMPUTE_BUDGET_THRESHOLD}}` | **Threshold placeholder never filled** (MPv4 L137, L1170) |
| H4 Schema/ontology MAJOR change | label split/merge, ID scheme, provenance enum | Pending candidates: INGREDIENT_LIST_ONLY tier (CONS B#6 / "Future change request"), MP-5A SVAR duplicate migration (MP1 L67), PST- prior-state vocabulary |
| H5 Gold data | starting/changing/unsealing Deep Gold / sealed test | No Deep Gold; sealed linker sets 441/850 not read (step07h report §D) |
| H6 Claims | SOTA/"beats X"/causal claims | H6-C recorded for NER (S128 W L880): no SOTA claim |
| H7 Repository | push to main, public, collaborators | Pending; GitHub size limit D-012 (REC.jsonl ~90 MB, ST L77) |
| H8 Scope | add/drop Level/Block/deliverable | Pending ("H8 semester scope cut", ST L129); sustainablefooddb indexing = SCOPE_CHANGE_REQUIRED (D-025, CONS B#6) |

### 4.2 Step-level gates and outcomes
| Spine step / substep | Gate definition (exact) | Outcome |
|---|---|---|
| ES-1.1 (Step 05) | 7 conditions: every source row accounted; no value invented; lineage preserved; duplicate mapping reversible; derivations reproducible; schema validation succeeds; canonical rows unchanged (ES11 L36–45); validator "9/9 gating checks" (W L889) | **PASS** (ES11 L3; D-018; S129) |
| ES-1.2 (Step 06) | 7-item pass-gate check (ES12 L124–132) | Self-assessed all "yes"; STATUS says "ES-1.2 closed" (ST L4). No human review of census recorded; H2 decisions pending (ES12 L138) |
| Step 07 automated (S131) | normalizer audit 0 INVALID; ledgers sha256 unchanged | PASS (S07 L3) |
| Step 07 human sub-gate | "pooled Cohen's kappa >= 0.80 AND no systematic disagreement on a critical field (temperature location, pressure reference, basis, retention type, censoring) — a flagged critical field forces adjudication even if overall kappa passes" (PROT L25); also "files not identical" (gate JSON `note`) | v1/v2 not accepted (D-021); v3 `NOT_COUNTED_PROVENANCE_INVALID` (κ 0.998; critical-field flags on basis/retention_type/censoring prevalence 1.00 → kappa-paradox risk); **v4 PENDING, 0 judgements** |
| 07H (S132) | G1–G10 (unit, schema, golden, open-bound, trajectory, property, 4414/17978 regression, ledgers byte-identical, deterministic rebuilds, no unsupported abbreviation) | **10/10 PASS**; combined hash a5991a9cda56; freeze commit 4e7db13 |
| 07H-R (S133) | G1–G7 (tests, 4414 regression 0 unexplained, base validators, scientific/vocab ledgers byte-identical, two rebuilds deterministic, no abbreviation promoted, **no bulk Gold promotion**) | **7/7 PASS**; fingerprint e7d58913; fields_changed 1,110, unexplained 0 |
| 07I-R (S134) | checks list in `step07ir_gate_result.json`: plan consensus, no unresolved plan conflict, feature file COMPLETE_REUSABLE, resumable, peak RSS 1.909 GB ≤ 4.5 GB limit, no all-pairs in memory, reproducible exact/near-dup scoring, **no_unvalidated_threshold_used_for_destructive_coalescence: true**, sources intact 612,782, provenance traceable, scientific ledgers unchanged | PASS (computational/integrity); final_hash 963466d8f207; scientific calibration **not done** (400-pair packet `labels_filled: 0`) |
| TRANSITION_BOOTSTRAP_V0 (future Step 29) | "Supported only if a baseline above B-0 beats B-0 with paired lower bound > 0 on S-3 or S-4 (cold) for T1 or T2 separately, and no gain is explained by source/basis shortcuts" (TB L23); "Headline = S-2..S-5 min; S-1 not used for claims" (TB L19); "Failure is a valid, reportable outcome; no model-complexity escalation on V0" (TB L26) | Defined, NOT run |
| NER benchmark v1 (closed) | dev-only checkpoint; min effect 0.003 + paired grouped bootstrap + Holm; Pareto promotion; router epsilon 0.02 (S119 W L817) | Closed (S128) |
| Gold pilot handbook gate | ">20%" disagreement-category mechanical gate flag (S102 W L698) | NOT_EVALUATED (D-017) |
| EXP-000007 | CC@5 primary, paired grouped bootstrap; success/null/negative/invalid gates (W L684) | NOT RUN |
| State-variable status | ACTIVE ≥50 rows & ≥3 signatures (MP1 L35) | Applied |
| 07I family edge | ≥4 ingredient tokens; IDF-ingredient Jaccard ≥0.80; title Jaccard ≥0.50; instruction-shingle ≥0.30 OR ordered process-seq ≥0.70 with ≥3 mapped processes; not differing explicit cuisines; star clustering, HETEROGENEOUS if member-to-center <0.60 (PRE L64–65) | Applied as *provisional, uncalibrated*; 44 FAMILY_CANDIDATE_REVIEW |

### 4.3 Stop / no-escalation rules found in governance
- "FILE EXISTS != EXPERIMENT COMPLETE" (MP0 L4).
- Normalizer may not be modified based on a reviewer's file until kappa and adjudication are recorded; if frozen files change after review starts the audit is invalid (PROT L13, L25, last para).
- Pre-registration: nothing may be changed after global duplicate/family counts are seen; "database size is a FINDING (not a target)" (PRE L50); Amendment A1 permitted only for computational feasibility, before full run (PRE L86).
- Parsing success never promotes a tier (D-024).
- NER: "no more model development" (S128 W L883); D-020 NER/linker/span CLOSED/FROZEN; Steps 16–17 reuse only.
- V0: no complexity escalation on failure (TB L26).
- Backlog items never interrupt the current step (BACKLOG L3).

---

## 5. Data requirements and named sources (licence notes from governance)
- EVD origins (ES12 L14; S130 W L894): USDA-RETN-R6 7,018 (PD ASSUMED; imputation from similar foods not row-identifiable); BOGNAR-2002 7,090 (6,594 retention + 496 yield; open access KIT, licence ASSUMED, DERIVED_ONLY); PHENOL-EXPLORER-3.6 3,870 / 125 papers (free; commercial use/redistribution needs authors' permission; D-005 scrape approved by Kush 2026-10-18; H2Q #5 says DO NOT crawl more, SEND permission email). All E3; 0 human-verified; 3,870 AI_PRECHECKED (S030 W L206).
- Recipe sources: A1/BBC 11,934 RESTRICTED local-only (D-003, D-007); Wikibooks 3,676 CC BY-SA (share-alike); Gutenberg segments 73,955 PD (silver, precision ~80–85%, D-012); Food.com 522,517 CC0 declared by uploader, authority unverified, LOCAL research use only (S116 Gate 1); TASTEset 700 MIT/LICENCE_UNVERIFIED in usage registry (CONS §C lists TASTEset LICENCE_UNVERIFIED although STATUS X10 says MIT — **inconsistency**).
- CoSyLab datasets (RecipeDB2, spice-disease, SweetpredDB, SustainableFoodDB, RecipeDB3 NER): `licence_status: ASSUMED`, `storage_rule: DERIVED_ONLY` (D-015 DEC L106–107), verbal permission reported by Kush, not independently verified; S088 (W L598–603) had reverted these ingests before D-015 re-allowed them.
- Ontology/aux: FoodOn CC BY 4.0; OFF ODbL; Wikidata CC0; FlavorGraph Apache-2.0 repo but NC upstream (no redistribution, S046 W L318); ChemTastesDB CC BY 4.0; bittersweet AGPL; OpenPI MIT; FoodAtlas CC BY-NC since 2026-10-09 (manual, S051); FSSAI allergens (S021).
- Local copies without SRC family (provenance gap): USDA cooking yields, FNDDS, INFOODS density/AnFooD/uFiSh, Food.com, AllerStack, NOVA, SustainableFoodDB, CoSyLab companion sets, FDC SR Legacy (ES12 L44).
- Priority sources (ES12 L53–71): P0 DS-040 OA food-science publishers, DS-032 Europe PMC, DS-006 USDA Cooking Yields R2; P1 incl. DS-043 physical-property literature, DS-045 kinetic literature, DS-033 PMC OA (bulk route change Aug-2026 unconfirmed), DS-005 FDC Foundation, DS-047 BRENDA (CC BY 4.0 with acceptance), DS-046 Rhea, DS-008 CoFID (OGL unverified), DS-009 AFCD (licence CONFLICT), DS-014 INFOODS (no statement), DS-062 FSIS (manual). IFCT 2017 BLOCKED_LICENSE (H2Q #8).
- Structured open mechanism/kinetic/physical time-series sources: **SOURCE_GAP for 13 of 16 priority cells** (ES12 L7; D-019).
- Human resources: Kush and Parv only (CLAUDE.md); HV-001..HV-010 queue (all NOT_STARTED / BLOCKED_HUMAN / PLANNED).
- Compute (governance record): Mac M2 Pro 8 GB (identity benchmark report L3); A100 over VPN with outages (S092 W L628) and 13–90 KB/s throughput (D-025); private GPU Ollama used in S066.

---

## 6. Dependencies on other levels/steps (governance view)
- Step 05 (ES-1.1) depends on MP-1 contract (D-018 "implements the MP-1 contract"); Step 06 (ES-1.2) feeds Step 07 source notes and Step 10 (ES-1.3) (ES12 L138).
- Step 07 human sub-gate is a precondition stated for Step 08 ("Step 08 only after the gate", S133 W L918). Note: S131 W L904 listed "STEP 08 source lineage (not started); human condition audit pending" as parallel items; S133/S134 then made the human gate a hard prerequisite. Whether Step 08 *scientifically* depends on the condition audit (lineage ≠ conditions) is a sequencing question for the audit (see §9).
- Step 10 (ES-1.3 pilot) requires: human review of census + H2 decisions #1, #3, #4 + choice of pilot mechanism (ES12 L138).
- Steps 16–20 own INST/ENTITY/EVT/STATE ledgers (`step07h_ledger_sync_matrix.csv` rows 33–36); CQPO programme owns QNT/POR (rows 31–32); "mechanism steps" own RXN (row 38); SPLIT/SIM/KINETIC/WARN/HYP/KGE rebuild "later".
- Steps 16–17 reuse frozen NER v1/linker D3/span CSD-C for instruction/event semantics only (S07 L32; D-020). MP0 L57: v1 NER covers ingredient lines, not instruction steps; SX-08-05 instruction weak labels never pursued → "the real upstream gap for B11".
- Identity (07I-R) supplies duplicate_group_id as split lock unit; families only after calibration (CONS row "Split leakage"); Gold firewall: 50 indexed, 0 same-group non-Gold members, 2 with family relatives (CONS row "Gold / Gold-Light / Silver"); 7/40 Gold have an exact-title twin in bulk corpus (step07h report §D).
- HV-001 (E4 verification) blocked on "MP-1 contracts reviewed; MP-5A schema"; HV-002 on "HV-001 protocol; MP-5B extraction"; HV-007 on "ledger evidence coverage (MP-5)" (`registry/human_verification_queue.csv`).
- MP ladder labels referenced but **not defined in repo**: MP-0 (inventory), MP-1 (contracts), MP-2/3 (representation; MP0 L90), MP-5 / MP-5A (schema migration: SVAR duplicates, prior-state vocabulary, MEAS study-level methods), MP-5B (mechanism extraction), MP-8 (SX-11-01 resolver on 20 Gold), MP-10A (SX-12-01 shortcut baselines). Their full definitions are UNVERIFIED (source plan not in repo).

---

## 7. Risks / failure modes (from history)
1. **Human-gate provenance failures (recurrent).** Condition audit v1 (Kush/Parv columns identical 100/100, D-021), v3 (11 s apart, 899/900 cells, gate JSON); linker annotation "annotator files byte-identical" (commit d3339b9) and "corrected Parv file still cell-identical to Kush" (5e91d38); Gold pilot_20 Parv review delegated to Kush (D-017: agreement 1.0 by construction, NOT_INDEPENDENT); Food.com Gold batch-level approval with no row-level decisions (S122 W L838). Any plan relying on "Kush+Parv blind double annotation" has a demonstrated failure mode. Real independent passes did happen for the linker gold (κ 0.13 → 0.50 on 441 set after correction, commits e4045f4/c192b51; κ 0.32 on final set, e49e7ba) — i.e. genuine human agreement on hard semantic tasks is low.
2. **AI-drafted content entering Gold**: pilot_20 drafted by OpenAI GPT-5.6 Sol (D-016); Food.com v1.1 AI_REAUTHORED_SOURCE_GROUNDED (S120 W L824); 13 unconverted events, 108/113 coref UNKNOWN, 78/113 coref mentions were the letters "it" inside words (S109 W L747).
3. **Governance drift**: STATUS stale since S083 (ST L3); WORKLOG gap 10-21; plan_authority_map lists DECISIONS as "D-001..D-024" and WORKLOG "S001..S133" (stale by one each); MP-1 contract header "DRAFT FOR REVIEW" (MP1 L3) vs plan_authority_map status "FROZEN_CONTRACT" vs ES-1.1 "frozen MP-1 contract"; similarity registry 15 types (MP0 L32, plan_authority_map) vs 21 rows / "FROZEN v1, 21 types" (MP1 L61).
4. **Licence risk**: majority of recipe base (523,217 records) LICENCE_UNVERIFIED (CONS row "Licence / use"); CoSyLab ASSUMED; PE redistribution needs permission; FlavorGraph NC upstream; Wikibooks share-alike could bind derived artefacts.
5. **Single-source / templated evidence** inflates apparent generalisation (Bognár caveat EXP-000004; USDA imputed factors S017 W L117).
6. **Infrastructure**: Mac 8 GB memory pressure (07I failure analysis: LIKELY_MEMORY_PRESSURE + LIKELY_SWAP_THRASHING, D-025); VPN outages and 13–90 KB/s.
7. **Identity recall gap**: ingredient-LSH skipped 4,745 buckets over cap containing 791,511 records (`identity_summary_v1.json`); near-duplicate recall is unmeasured → leakage across splits possible until calibrated.
8. **Data-model bugs found late** (all fixed, but show fragility): '-20°C' parsed as +20 (266 COND, S030); ingest rerun wiped 6,594 process / 2,251 ingredient links (D-013); calendar months stored as seconds at ingest (956 conditions, D-024); open-bound flags reversed (D-023); previous consensus tool rewrote frozen recipe_base in place (CONS B#4).
9. **Test-selection slip**: S124 (W L852) model conclusions redone on DEV after a TEST-selection slip; RecipeDB3 published protocol selects on TEST (S091).
10. **Course deadline pressure**: presentation 25–26 Nov 2026 (W L5; ST L80–88) vs research-grade gates; STATUS W1–W6 plan items largely unmet (e.g. "humans verify ≥40 lit rows" by W2: 0/40).

---

## 8. MAPPING TO THE 36-STEP SPINE (brief §9)
Mapping of sessions/artifacts to spine steps is RECONSTRUCTED from repo labels; the step cards of "CulinaryState Master Execution Plan v1" are not available, so no card text is quoted.

### Step 01 — Freeze project authority
- Artifacts: S001 (W L7–11: SSOT v15, Master Plan v4.0, R&D plan v2, Max prompt v2 copied to docs/); S003 SSOT index verified (W L19–23: 45,697 lines, 309 H1, 30/30 RQ16, 14/14 G16, 18/18 G15); D-001 (rebuild locally); formal authority artifacts arrived only in **S134**: `registry/plan_authority_map_v1.csv` + `plan_authority_inventory.md` (precedence 1 SSOT → 2 Master Plan decisions → 3 DECISIONS → 4 frozen spine/active step contract → 5 MAX plans → 6 STATUS/WORKLOG → 7 code → 8 historical; PAI L3).
- Gate outcome: no explicit Step-01 gate artifact; consensus found "no SSOT_CONFLICT" (CONS Result line) — scope limited to recipe identity.
- Requirements for the audit: the authority map must be extended beyond identity topics, record the missing 36-step plan and missing v3.0 MAX plan as ABSENT, fix stale rows (D-024/S133), and note the Master Plan's own different authority order (MPv4 AG4 L2744–2752 ranks the course proposal contract 2nd and live human decisions 7th) vs the brief §2 order.
- Status: PARTIAL (de facto, retrofitted at S134).

### Step 02 — Audit implementation state
- Artifacts: MP-0 inventory (commits 5e8faae, 763e51a; 2026-10-21 23:46–23:47), `reports/ssot15/data_foundation_audit.md|json` (a87b614, 1095204, d0ce5f5), `registry/ssot15_state_experiment_map.csv` (123 rows), `reports/h_state/ledger_stats.*`, `reports/step07i/final_recipe_database_statistics.*`; earlier S100 readiness audit (W L682–687: "VERIFIED: replay determinism only"), S093 dataset plan, S097 DONE_FROM_SSOT.
- Gate: rule "FILE EXISTS != EXPERIMENT COMPLETE"; outcome: B03 MISSING, B04/B05/B06/B07/B10/B11/B13 PARTIAL, B08/B09 COMPLETE (closed), B12/B14 MISSING; 0 of 47 gates passed (MP0 L37–49).
- No WORKLOG entry (gap). Status: DONE (unlogged), but counts now stale (e.g. MP-0 counts REC 89,565 pre-07H-R; recipe base now 612,782).

### Step 03 — Freeze state semantics
- Artifacts: MP-1 `state_representation_contract_v1.md` §1–5 (084df7e), `registry/state_variable_registry_v1.csv` (254 rows).
- Requires (for later steps): factorised S with explicit masks; UNKNOWN semantics; trajectory ∈ {PLANNED, OBSERVED_SESSION, PREDICTED} (MP0 L108 recommendation); identity A–H separation; output contract unsupported/physically_possible/evidence_supported.
- Gate: none explicit; header says "DRAFT FOR REVIEW". Rulings: only C1 recorded (D-018). C2–C8 rulings not recorded in DECISIONS (C3/C4 implemented in ES-1.1 export choices; C2 implemented in TB "unverified" label). Status: PARTIAL/PROVISIONAL-FROZEN (authority ambiguous).

### Step 04 — Freeze evidence / provenance / similarity contracts
- Artifacts: MP-1 §6–9, `evidence_tier_provenance_map_v1.csv`, `provenance_class_registry_v1.csv`, `evd_contract_v1.csv` (27 field rows), `simulated_state_changes_schema_v1.csv`, `ssot15_similarity_registry.csv` (21 types), `registry/human_verification_queue.csv` (HV-001..HV-010), `transition_bootstrap_v0_contract.md`.
- Gate: ruling C1 (D-018). Outcome: contracts exist; open conflicts C2 (E3 Gold eligibility), C5 (PE yield non-independence), C7 (AI-drafted fields cannot gate claims until HV-010), C8 (Q/R/X extension) unresolved.
- Missing for downstream: no formal independence-group / study-lineage contract (deferred to Step 08); similarity registry not reviewed by humans (MP0 L110 "review and freeze").

### Step 05 — Normalize EVD
- Artifact: ES-1.1 (S129 W L885–890; D-018; `reports/es1/es1_1_audit.md`; export sha256 e61d7db4…). **Gate PASS**.
- Outputs consumed later: `evidence_tier` etc., `matrix_id`, `prior_state_id` (PST- hash, vocab pending), `canonical_variable_id`, `log_retention_factor`, reason-if-unknown fields.
- Retained deficits (ES12 §8 L111–122): 0 human-verified rows; 6,409 rows w/o ingredient_id; 5,536 w/o prior_state_id; LOD/LOQ absent; PE design strength UNKNOWN; 278 PE retention discrepancies; 7 SVAR equivalences unresolved; physical coverage sparse; mechanism rows 0.

### Step 06 — Freeze source acquisition manifest
- Artifact: ES-1.2 (S130 W L892–897; D-019): 64-source manifest, 20-claim capability matrix, 30 query templates (Europe PMC counts), 16 priority cells, 21-item H2 queue; Step-06 source-note corrections in S131 (S07 L28–29: Europe PMC route/per-article licence; NCBI E-utilities; Unpaywall search endpoint retired 2026-09-18 "stated in the instruction, not independently re-verified").
- Gate: ES12 L124–132 self-check all yes; H2 human decisions **all pending**. Status: AUTOMATED-COMPLETE, HUMAN-PENDING. "34% of manifest cells UNKNOWN by design" (D-019).

### Step 07 — Condition & measurement normalization (with substeps)
- 07 (S131 W L899–904; D-020): 10 vocabularies, schema, normalizer, audit over 4,414 conditions/17,978 EVD, 0 INVALID; human packet v1.
- 07 fixes (D-021, D-022; commits a28ae5e…8a9b56b): RAW_TEXT_PRESENT_BUT_NOT_PARSED (245 durations), slash notation (18), spaced dash (24), multiple values same location (472); notation registry (13 rules); packet v2.
- 07H (S132 W L906–911; D-023): 3-layer parser/normalizer/dialect, G1–G10 PASS, freeze 4e7db13, packet v3.
- 07H-R (S133 W L913–918; D-024): 612,782 recipe base, 8.17M expressions, derived recipe ledgers, DATASET rows, gate 7/7, fingerprint e7d58913, packet v4. **Scope note**: recipe-base consolidation is recipe-plane work placed inside the evidence-plane Step 07 as a "bounded completion substep".
- 07I-R (S134 W L920–925; D-025): identity (exact 611,714 reps; 8,639,518 candidate pairs; 744,615 kept; 6,589 provisional edges; 605,476 families; 5,803 multi-rep; 46,697 dish candidates), plan consensus, memory-safe pipeline; 400-pair packet UNLABELED.
- Pending human gates: condition packet v4 (κ ≥ 0.80 + no critical-field flag + files not identical); duplicate calibration packet (400 pairs; strata S01–S11, sha256 1cc5ded6…).
- Status: AUTOMATED INFRASTRUCTURE FROZEN; HUMAN AUDIT PENDING; identity PROVISIONAL (uncalibrated).

### Step 08 — Scientific source lineage
- NOT STARTED; NOT AUTHORISED (S131 W L904 "STEP 08 source lineage (not started)"; S07 L35; S133/S134).
- Inputs available: STUDY 125 rows (all `design: UNKNOWN`, UNVERIFIED); SRC 488 active / 151 families (ES12 L14) (sync matrix says SRC 609 lines); EVD `independence_group` (127 values), `study_id_status` (NOT_IDENTIFIABLE for all USDA/Bognár), PE `pe_pub:*` SRC with licence UNKNOWN; 121/125 PE DOIs resolved, 15 OA (S030 W L206); verification queue 634 rows (Route A PE papers + Route B OpenAlex) with lineage-duplicate flag vs PE (S022 W L150); PE shared yield sources (103 distinct yield records; TB L13, MP1 C5); FDC analytical vs imputed source codes (S050).
- Requirements implied by governance (no card text available): must support study-disjoint splits (S017: "study_disjoint via row→study connected components (refuses when single source/giant component, AM3)"); must type database compilations as DATABASE_AGGREGATE, never fabricate study_ids (AH1); must capture cross-source lineage overlap (e.g. whether Bognár compiles from the same primary studies as USDA — UNVERIFIED), mirror/repost detection (MPv4 W12 L1896–1903 "never count mirrors/reposts as independent evidence"), PE yield-source sharing; must resolve PE design strength (HV-003) and 278 discrepancies.

### Steps 09–36 — what the repo says they contain (statements found)
- Step 10 = "ES-1.3 — 20-row mechanism evidence extraction + human-verification pilot"; candidate mechanisms potato frying/acrylamide (Q05 910 OA full-text hits / 89 title-abstract OA) vs garlic alliinase (Q01 404/24) vs onion LFS (Q03 34/2); "garlic remains the higher-priority zero-row cell" (ES12 L138; W L897). Precision is "a deliverable of ES-1.3" (ES12 L98).
- Steps 16–20 own INST, ENTITY, EVT, STATE (sync matrix rows 33–36); Steps 16–17 reuse frozen NER/linker/span for instruction/event semantics only (S07 L32; D-020).
- "CQPO programme" owns QNT/POR (sync matrix rows 31–32) — not mapped to a spine number in repo.
- "mechanism steps" own RXN (row 38) (consistent with Phase E 21–25, UNVERIFIED).
- TRANSITION_BOOTSTRAP_V0 contract (TB) = Step 29's name in the spine; contract already defines targets T1 retention / T2 yield, B-0..B-5, splits S-1..S-7, metrics, success rule.
- E7 synthetic prior (Step 28) — only the simulation contract (MP1 §8) exists.
- Waves A–E in ES12 L103–109 correspond to Steps 11–14 by content (Wave A structured = Step 12; Wave B targeted literature = Step 11/13; Wave C physical/kinetic = Steps 13/14 and 24/32 inputs; Wave D extraction at scale "only after the ES-1.3 pilot reports extraction precision and verification throughput"; Wave E recipe semantic expansion = Steps 16–20). This mapping is MY inference.
- No repo text states contents of Steps 09, 11–15, 21–28, 30–36 by number.

### Spine-step requirements this governance material imposes later
- Step 09 (extraction & verification machinery): must implement E5→E4 promotion only via human verification against cited span/table (MP1 L52); AI_PRECHECKED is not verification (D-014 caveat; S030 apply tool rejects verifier=Claude); must record verification provenance per row (HV queue); must measure LLM extraction accuracy vs human (SX-06-08 BLOCKED_HUMAN); evidence-key extraction baseline recall 0.588 / lineage precision ≥0.508 (`reports/ner/evidence_key_baseline.json`) is the prior baseline for recipe-side evidence keys.
- Step 15 (freeze DATA-EVIDENCE v1): DATASET/SPLIT ledgers (SPLIT not frozen, sync row 37); independence units "matrix × process signatures: USDA 171, Bognár retention 123, PE 287, Bognár yield 417" (TB L14) — these, not row counts, are the sample size.
- Step 19 (Gold trajectory pilot): Gold tier contract `registry/recipe_quality_tier_registry_v1.csv` (DEEP_GOLD needs independent blind double annotation + adjudication + reported IAA above pre-registered threshold); Gold firewall via duplicate_group_id / split_lock_group_id.
- Step 29: TB contract; must include source/basis shortcut controls.
- Step 36: D-008 task list; decision modes ANSWER…ABSTAIN; claim checker (UCR) and template verbaliser as baseline.

---

## 9. Contradictions, stale items, underspecified parts, open questions
1. **Missing authoritative 36-step plan** — all step mapping above is reconstructed. Missing v3.0 MAX plan. Parv's DELTA/LANE/ACQUISITION/COVERAGE plans known only second-hand (plan_authority_map rows from `parv-origin/main`, not in this clone).
2. **WORKLOG gap 2026-10-21** (no S-entries for ~75 commits incl. MP-0/MP-1) — violates W L3; S129 cites "frozen MP-1 contract" without a logged freeze step.
3. **MP-1 status ambiguity**: "DRAFT FOR REVIEW" (MP1 L3) vs "FROZEN_CONTRACT" (plan_authority_map) vs "frozen" (S129). Rulings C2–C8 not in DECISIONS.
4. **Similarity registry count**: 15 (MP0 L32; plan_authority_map) vs 21 rows and "FROZEN v1, 21 types" (MP1 L61).
5. **plan_authority_map stale**: DECISIONS "D-001..D-024", WORKLOG "S001..S133" (actual D-025, S134). PAI says 28 rows (correct).
6. **Authority order conflict**: brief §2 vs Master Plan AG4 (MPv4 L2744–2752, course proposal contract rank 2) vs PAI L3 (frozen execution spine rank 4).
7. **Gate-label collision**: H1–H8 (human gates) vs H1–H4 (proposal hypotheses, D-008) vs Master Plan sections H1/H2 vs H_STATE.
8. **Step-08 prerequisite**: S131 W L904 treats Step 08 and the condition audit as parallel; S133 W L918 makes the audit a prerequisite ("Step 08 only after the gate"). Scientific dependency of source lineage on condition audit is weak; needs explicit decision.
9. **ES-1.2 "Next: STEP 10 / ES-1.3"** (W L897; ES12 L138) skipped Steps 07–09; then S131 inserted Step 07 → spine apparently re-sequenced after S130. Which numbering/contract is authoritative is UNVERIFIED.
10. **Step 07 scope creep**: 07H-R and 07I-R (recipe base, identity) are recipe-plane deliverables labelled as Step 07 substeps; spine has no explicit recipe-identity step (closest: 16–20 or 15/19 leakage). Needs a home decision (substep vs Step 16 prerequisite).
11. **TASTEset licence**: MIT (STATUS X10, S044 W L304) vs LICENCE_UNVERIFIED in usage registry (CONS §C).
12. **EXP-000005 card stale** ("KEEP DeBERTa-large+CRF") vs frozen DeBERTa-base+CRF.
13. **USDA retention basis**: %TR vs %AR mixed, not row-identifiable (S007 W L45; MP1 C4) — basis covariate required; true retention vs apparent cannot be resolved from source.
14. **PE retention type** RT-003 yield-adjusted AMBIGUOUS "description comes from a secondary snippet; primary-source check pending" (S07 L10).
15. **PE data-point discrepancy**: list pages advertise 4,407 data points vs 3,870 parsed (S025 W L171) — "to investigate, not assumed"; never resolved in log.
16. **Unpaywall search endpoint retirement 2026-09-18** stated by instruction, not verified (S07 L29); PMC FTP Article Datasets removal Aug 2026 unconfirmed (H2Q #2) — need external verification (Step 06/13).
17. **H3 threshold** `{{COMPUTE_BUDGET_THRESHOLD}}` unfilled.
18. **H1 email** send status unknown; Foodoscope key; CoSyLab written confirmation; PE permission; IFCT permission — external dependencies.
19. **D-008 task merge** still open; course says 8 task types, SSOT §12 names 9.
20. **State variable FUTURE rows** come from Master Plan W3 list; SSOT authority for Q/R/X profiles (C8) open.
21. **Bognár ↔ USDA independence**: whether Bognár 2002 compiles values derived from USDA or shared primary literature is UNVERIFIED (open research question for Step 08; affects source-disjoint S-7 and cross-source agreement interpretation S039).
22. **USDA R6 dating**: all rows dated 09/1975 placeholder (S007 W L45) — temporal metadata unreliable.
23. **Identity**: recall diagnostic (791,511 records in skipped ingredient-LSH buckets) not converted to a recall estimate; quantity distance cosine vs SSOT 264.4 log-ratio baseline (CONS B#8); d_role and d_G unavailable (CONS row "Level-13 representation").
24. **sustainablefooddb** 118,083 ingredient-list recipes un-indexed (SCOPE_CHANGE_REQUIRED); 48 A1 raw rows without REC id (CONS §C).
25. **H_STATE feasibility**: card requires ≥40 supported of 60; observed max 14 (BBC Gold) / 51 pairs over 15 recipes (Food.com v1.1, AI-authored) — card amendment status for Food.com set unclear (S118 W L810, S120 W L824).

Questions needing external research (for other agents): Bognár/USDA lineage overlap; PE yield-correction semantics (primary source); current PMC/Europe PMC bulk OA routes and Unpaywall API status; CoFID OGL, AFCD licence, INFOODS terms; annotation-reliability thresholds for condition/event/identity labels (κ ≥0.80 justification; kappa paradox under prevalence 1.00); calibration sample size for near-duplicate threshold.

---

## 10. LOOK-AHEAD — fields/metadata earlier steps must capture
**For Step 08 (lineage) to serve Step 15 study-disjoint splits and Step 27 held-out validation:**
- per EVD row: `study_id` (or explicit NOT_IDENTIFIABLE), `document_id`/DOI, `publication_id`, `source_family_id`, `compilation_source_ids` for aggregates (e.g. Bognár table → cited primary references when listed), `independence_group_id` at study level (not source family), `lab/author group` (to catch same-lab studies), `mirror_of`/`derived_from` (repost/mirror detection, MPv4 W12), `yield_source_id` (PE 103 shared yield records), `imputation_flag` (USDA source-side imputation), `donor_food_id` where identifiable (TB L19 "USDA values imputed from similar foods must stay in the same fold as their donors"), `measurement_platform`/analytical method (currently UNKNOWN 4,366 / CALCULATION 13,612; S07 L22), `replicate count`, `sample_id`, `cultivar/variety`, `date` (USDA placeholder 1975).
**For Step 07/09 conditions to serve Step 23 applicability and Step 26–27 simulation:** temperature *location* (only 221/4,414 stated; S07 L21), medium, pressure reference, geometry/size (matrix.geometry exists in schema, MP1 L4), initial state / prior processing vocabulary (PST- pending), moisture/pH/aw (100% UNKNOWN; COND has no fields), oxygen, agitation, time-temperature trajectories (none exist), heat-transfer mode registry already exists.
**For Steps 10–14 acquisition to serve Steps 24–27 (formula/parameter registry, simulator validation) and Step 30–33:** before/after values (only PE has them: 3,870), units and basis, LOD/LOQ and censoring kind, uncertainty (SD/SE/n), time series points, kinetic parameters with fitting method and temperature range, design strength (E1/E2 classification evidence), per-article licence and attribution (Europe PMC), extraction locator (page/table/span) for E4 verification, verifier identity + timestamp + blind flag.
**For Steps 16–20 recipe semantics to serve Steps 22, 29, 36:** duplicate_group_id / recipe_family_id / split_lock_group_id from 07I-R (already in FK table), usage class (`training_allowed`, `raw_redistribution_allowed`), tier (SOURCE_RAW/SILVER_AUTO/GOLD_*), provenance of each annotation (AI_DRAFTED / AI_ASSISTED_HUMAN_REVIEWED / HUMAN_INDEPENDENT / ADJUDICATED — the repo already uses these strings), annotator independence flag, recipe era/culture as provenance only (CONS row "Historical variants"), condition mentions with TEXT_STATED observation class (never E-tier), quantity Q-levels, unresolved/NIL mentions kept UNRESOLVED (MP0 L58).
**For Step 15/19 Gold protection:** Gold index must carry duplicate/family/title-twin flags (7/40 title twins), sealed-set hashes (441/850 linker sets, NER TEST manifest), and "never read" audit trail.
**For governance itself (all steps):** each step needs a WORKLOG entry, a gate JSON with `counts_as_human_gate` and provenance check (pattern from step07h_human_gate_result.json), a freeze manifest/fingerprint, and a DECISIONS entry for every contract ruling (C1 pattern) — missing for MP-0/MP-1 and C2–C8.

### Negative/partial empirical results that MUST be retained (consolidated)
| Area | Result | Source |
|---|---|---|
| DEL-2 USDA | random D5 0.025 vs D0 0.121; matrix_disjoint D0 0.059 ≈ D4 0.057 (CIs overlap); process_disjoint D0 0.073 vs D5 0.067 (not beyond CI); conformal-90 empirical coverage 0.72–0.87 on cold splits; study-disjoint impossible | S017 W L117; EXP-000001 |
| DEL-2 PE | raw and log targets NOT SUPPORTED; study_disjoint best = persistence/global mean (median AE 0.21); outlier/formation RF up to ~100 | S029 W L199; S040 W L276; EXP-000002/3 |
| DEL-2 Bognár | supported incl. cold-start but templated factors; process split degenerate (1 group) | EXP-000004; S038 W L262 |
| Cross-source | USDA vs Bognár mineral conflict boiled veg/poultry (~0.9 vs ~0.5) | S039 W L269 |
| FDC pairs vs R6 | within 0.10 for 46% (analytical), Spearman 0.31 | S050 W L346 |
| Retrieval | rerankers −0.056/−0.091 MRR; structured+dense +0.005 n.s.; RQ16-03 success "mostly by construction", NEED_DATA | S068 W L472; S072 W L500 |
| Graph expansion | siblings worse than baseline; unlinked-food NEAR rule Δ +0.018 worse | S070 W L486 |
| Generator | LLM ladder B2 UCR 0.80 (3 fabricated ids), B5 UCR 0.71; LLM rephrase unpromoted | S065 W L451; S066 W L458 |
| Slot parsing | target right 20.5% before lexicon fix (0.994 on templated, optimistic) | S071 W L493 |
| Gold oracle / state | compiler vs Gold: state-field 0.102→0.140→0.132→0.106; alive F1 0.29–0.40; merge/split 0.34–0.38; oracle concepts/Adds ≤+0.02–0.03 (no gain) → event construction is the bottleneck; Transform 169 pred vs 97 gold | S107–S110 W L733–754 |
| Gold independence | pilot_20 and Food.com Gold NOT independent; handbook gate NOT_EVALUATED | D-016, D-017; S122 |
| H_STATE coverage | 10/20 recipes have any retention cell, 5 at chosen cuts; max 14 supported pairs vs ≥40 target; evidence-first calibration precision 0.25 / recall 0.29 | S112 W L768; S114 W L782; `h_state_coverage_lift_forecast.md` L14 |
| Evidence keys | recipe evidence-key extraction recall 0.588, precision vs Gold lineage 0.508 (lower bound) | `reports/ner/evidence_key_baseline.json` (commit 318f7b0) |
| NER | kNN-NER null; GLiNER zero-shot exact 0.232; unseen FOOD F1 ~0.70; K1–K4 knowledge prompts reject; neural fusion reject; CRF not significant on DEV; v3-large no TEST gain; M3.1 verifier NO-GO (55% = trivial rule); CSD-C choosers no gain | S077, S083, S124–S128; `knowledge_augmentation_ablation.md`; `fusion_decision.md`; `m31_aux_result.md`; `csd_s0_s3_result.md` |
| RecipeDB3 | published protocol selects on TEST; 13.6% masked-family leakage; headline flattered ~0.45 micro-F1 points; theirs − clean +0.0039 macro (n.s.) | `recipedb3_matched_reproduction.md`; S091–S092 |
| Linker | Tev1-4B beat BGE on 441 fresh set (0.901 vs 0.796) but lost on 850 final (0.872 vs 0.881) → BGE retained; DEV n=61 misleading; no safe autonomous NIL; DISTILL-A partial; human κ 0.13/0.50/0.32 | `culinary_link_decision_closeout.md`; `fresh_linker_final_report.md`; commits e4045f4, c192b51, e49e7ba |
| Condition audit | v1, v2, v3 not counted (provenance); κ 0.998 non-informative | D-021, D-024; gate JSON |
| Identity | no calibrated near-dup threshold; 400 pairs unlabeled; LSH recall gap | D-025; identity_summary_v1.json |
| Troubleshoot miner | AI-judged precision 35/40 → 37/40 (not human) | S062 W L430 |
| Gutenberg silver | segmentation precision ~80–85% (30-sample) | D-012; S043 |
| Scripted sessions | 30 AI-drafted, 0 human-reviewed | S055 W L381 |
| DEL-1 | 4/6 clauses; 0/40 human-verified rows | S022, S029; ST L38 |
