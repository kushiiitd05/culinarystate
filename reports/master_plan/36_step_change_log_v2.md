# 36-step change log v2

Generated 2026-10-22 by the CulinaryState plan-research audit (PLAN ONLY; STEP 08 NOT STARTED). Built from 9 phase drafts; the planned adversarial-critique/revision round was SKIPPED for usage-limit reasons, so treat every item as DRAFT FOR HUMAN REVIEW.

No top-level step is added or removed; numbering is preserved. Changes are substeps, dependency edits, gates and artifacts inside existing steps.

## Step 01
- **OLD:** Authority map v1 scoped to recipe identity (S134); stale rows (D-001..D-024, S001..S133, similarity '15 types'); missing docs not recorded; course proposal PDF absent from map
- **NEW:** Substep 01.1: registry/plan_authority_map_v1_1.csv programme-wide with ABSENT rows (36-step plan v1, MAX v3.0, Recipe_Compiler v1.2, Parv supplemental plans) and course-proposal row; v1 kept frozen
- **WHY:** Authority must be traceable; stale rows mislead later steps
- **SOURCE / EVIDENCE:** PAM rows 13/14/16; DEC L139 (D-025); W L920 (S134); docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf present; MP A3 L48-61
- **IMPACT:** All steps cite one map
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 01
- **OLD:** Three conflicting authority orders (brief §2; MP A3 L48-61 humans override 2-4; MP AG4 L2742-2751 live human decisions last) + PAI L3
- **NEW:** Substep 01.2: DECISIONS D-026 ratifies brief §2 order + clauses: human decisions bind only as DECISIONS entries, SSOT only via CR; empirical results override expectations; D-027 records MP-1 status
- **WHY:** Unresolvable conflicts otherwise; MP-1 DRAFT vs FROZEN ambiguity
- **SOURCE / EVIDENCE:** mp_part2 §9; gov §9 items 3,6; MP1 L3; PAM row 10
- **IMPACT:** Clarifies which contract governs Steps 03-05 and later
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 01
- **OLD:** No namespace control; collisions SIM- (similarity SIM-01..21 vs simulation ids MP1 L13), MODEL- (ML card vs formula registry), MEAS- (method), EXP- (ML run), CLM (research vs runtime), E7/D/B/T/S ladder labels, H1-H8 vs H1-H4, 'recipe family' 611,700 vs 605,476
- **NEW:** Substep 01.3: registry/namespace_registry_v1.csv with canonical prefixes (TIER-E#, D#, SYS-B#, L14-T#, SEXP-, OBS-, FMOD-, SIMRUN- or SIMTYPE-, RCLM-)
- **WHY:** Collisions already caused misreadings and would blur data planes
- **SOURCE / EVIDENCE:** r_evidence_model §0; r_mechanism_registry; ssot_l14/l15a/l15b/mp_part1 collision lists; repo similarity registry ids
- **IMPACT:** New ledgers in Steps 08, 21-28, 36 use non-colliding prefixes
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 01
- **OLD:** H3 compute gate threshold {{COMPUTE_BUDGET_THRESHOLD}} unfilled
- **NEW:** Substep 01.4: registry/human_gate_registry_v1.csv with H3 trigger expressed for real compute (A100 jobs, shared-server CPU-hours, paid API/LLM batches)
- **WHY:** H3 has no operational trigger
- **SOURCE / EVIDENCE:** MP L137, L1170; ctx.md compute reality
- **IMPACT:** Governs any GPU/LLM batch in Steps 17, 20, 30, 35
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 01
- **OLD:** No gate has a numeric threshold (47 SSOT L12-L16 gates; G16; §257A 'declared')
- **NEW:** Substep 01.6: registry/preregistered_thresholds_v1.csv + rule: a gate runs only if its threshold row predates data access; loosening requires CR + DECISIONS and keeps old result
- **WHY:** Enforces the no-post-hoc-gate-weakening law
- **SOURCE / EVIDENCE:** MP0 L49; ssot_l16 §4.1; ssot_annexA §4; Kapoor & Narayanan 2023 [r_eval_splits]
- **IMPACT:** Every gate from Step 08 onward
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 01
- **OLD:** Open human decisions scattered (§279.8 first thread; D-008; Step-08 prerequisite S131 vs S133; TASTEset licence; RD §21 items; L13E lane)
- **NEW:** Substep 01.5: registry/open_human_decisions_v1.csv with owner and blocked steps; 01.7 adopt reports/master_plan/ssot_change_requests_v2.md as CR log; 01.8 WORKLOG back-fill for 2026-10-21 gap
- **WHY:** Decisions must be owned; MP D5 CR file absent; WORKLOG gap violates one-entry-per-step
- **SOURCE / EVIDENCE:** SSOT L45631-45645; DEC L40-52; W L878->L885; gov §9
- **IMPACT:** Makes Step-08 authorisation decision explicit
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 02
- **OLD:** One-off MP-0 inventory (stale counts, unlogged)
- **NEW:** Retro-fix 02.1-02.8 (implementation_status_v2, artifact presence manifest, environment manifest, negative-results register, gate-status registry, count definitions, STATUS.md regeneration, test-hang ticket) + recurring checkpoint 02.R before Steps 08, 15, 20, 29, 36
- **WHY:** Status drifted within a day; Mac/Linux divergence; hidden environment prerequisite for Steps 29-35
- **SOURCE / EVIDENCE:** impl §0, §0.2, §9; gov §7; ctx.md L20, L25
- **IMPACT:** Prevents sequencing on stale facts; exposes BLOCKED_ENV
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 03
- **OLD:** MP-1 v1 DRAFT; open conflicts C2-C8; one provenance enum used for origin and status; UNKNOWN overloaded
- **NEW:** Retro-fix 03.1-03.2: v1.1 addendum with orthogonal origin_provenance / field_status / claim_route and a missingness-code superset (adds ROUNDED_INTERVAL, RANGE_ONLY, TRUE_ZERO, NO_EFFECT, NOT_MEASURED); rulings C2-C8 in DECISIONS
- **WHY:** Three SSOT vocabularies conflict (§239.1, §257A.4, §257A.14); UNKNOWN != NOT_APPLICABLE != NON_DETECT
- **SOURCE / EVIDENCE:** ssot_annexA C1; ssot_l16 §9 item 3; SSOT L25313-25315, L28076-28093
- **IMPACT:** Steps 05, 09, 16-19, 36 inherit one status model
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 03
- **OLD:** No clock semantics; generic time fields
- **NEW:** Retro-fix 03.3: clock registry (tau process time, event_index, text_order vs depends_on, observed_at, historical t) with validator rejecting untagged time
- **WHY:** SSOT two-clock law; kinetics need cumulative process time
- **SOURCE / EVIDENCE:** SSOT L43001-43008 (ssot_l13e); ssot_annexA U7
- **IMPACT:** Steps 09 (trajectories), 16-18, 34, 35-E
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 03
- **OLD:** ENTITY schema lacks parentage/creation/consumption; EVT lacks event_kind/modality/alternatives/temporal relation/implicit args; STATE beliefs not plane-mapped; no prefix cutoff
- **NEW:** Retro-fix 03.4/03.5/03.8: entity lifecycle + parentage + allocation; event_kind/modality/alternative_group/temporal_relation/implicit_args; belief->plane mapping, observation override, evidence_cutoff {ONLINE_PREFIX, OFFLINE_FULL}
- **WHY:** Procedure-semantics literature and S109 Gold audit gaps; endpoint-phrase leakage
- **SOURCE / EVIDENCE:** r_recipe_semantics_gold Q1/Q3; SSOT L26495, L25347; RD L327-333, L584
- **IMPACT:** Step 16 schema freeze, 18 engine, 19 Gold, 29/34 leakage control
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 03
- **OLD:** SVAR registry lacks delta semantics, observability, target-rung eligibility, history-dependence, compartment
- **NEW:** Retro-fix 03.6: state_variable_registry_v1_1.csv additive columns; 03.10 SSOT view crosswalk; 03.9 MP-1 §1.G corrected so SIM outputs are not 'evidence'
- **WHY:** Needed by Steps 22-23, 29-34, 36; MP-1 §1.G conflicts with SSOT §232.3/§233.7
- **SOURCE / EVIDENCE:** ssot_l15a Step-03; ssot_l14 Step-03; r_mechanism_registry Q5; MP1 L13
- **IMPACT:** Transition targets and applicability engine
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** No evidence entity/lineage/independence contract; Step 08 prerequisite stated as Step-07 condition audit (S133/S134)
- **NEW:** Retro-fix 04.1 (P0): SRC->DOC->STUDY->SEXP->SMP->OBS->AGG/DRV + LIN + XTR; three independence keys (study_id, lineage_root_id, split_group_id) + independence_resolution; giant-component rule; this contract (plus 01.6 thresholds) becomes the HARD prerequisite of Step 08; condition audit proposed SOFT for Step 08 (human decision)
- **WHY:** Step 08 has no target definition otherwise; lineage does not depend on condition semantics
- **SOURCE / EVIDENCE:** r_evidence_model §3-4; Cochrane ch.5/23; von Elm 2004; MP AM3 L3597-3613; W L904 vs W L918
- **IMPACT:** Changes Step 08 dependency edge; unblocks evidence critical path once approved
- **BREAKING?** YES
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** EVD has no SD/n/LOD/dispersion type, no document type, no method per observation; censoring registry lacks ROUNDED_INTERVAL/RANGE_ONLY/TRUE_ZERO
- **NEW:** Retro-fix 04.2: measurement & value documentation (dispersion_type, n_bio/n_tech, statistic, censor_kind v2, basis, method/platform per OBS, EuroFIR-style value_type/method_indicator/acquisition_type/matrix_unit, DIGITIZED, evidence_class incl. OCCURRENCE, per-row licence, document type)
- **WHY:** Effect-size variance, censored likelihood and platform splits need them; never impute
- **SOURCE / EVIDENCE:** r_evidence_model Q2/Q4; SSOT L28108-28121, L26374; registry/censoring_registry_v1.csv
- **IMPACT:** Steps 05 (export v2), 08, 09, 12, 15, 30
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** Kinetic schema split across SSOT §210.29/§211.50/§216.2; no KINETIC schema; EVD endpoint-only
- **NEW:** Retro-fix 04.3 (MOVE EARLIER of an artifact): unified KINETIC/trajectory schema (series_id, timepoints, T(t), T-location, replicate, K-rung, fit_origin, effective_or_mechanistic, identifiability) frozen before Step 09
- **WHY:** Otherwise series are flattened at extraction and Steps 24/26/27/32 lose inputs
- **SOURCE / EVIDENCE:** r_acquisition (HIGH); ssot_l15a C10; r_mechanism_registry
- **IMPACT:** Steps 09-14 extraction, 24-27, 31-34
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** Tier vocabularies inconsistent (SSOT E1-E6; repo E1-E7; class I imputed; §223.13 fidelity); EXTERNAL_VERIFIED means 'DB/study reports' in SSOT but 'independently human-checked' in repo
- **NEW:** Retro-fix 04.4/04.5: tier crosswalk with TIER-E# namespace; provenance v1.1 (SSOT meaning of EXTERNAL_VERIFIED; human checking moves to verification_status; add MODEL_ASSISTED_HUMAN_REVIEWED, INDEPENDENT_HUMAN, ADJUDICATED, HISTORICAL_CULTURAL, SYNTHETIC_HISTORY; Q-level mapping for CONVENTION)
- **WHY:** Wrong claim language and leakage of model-assisted labels
- **SOURCE / EVIDENCE:** ssot_sparsity; ssot_annexA C1/C2/R3; r_recipe_semantics_gold Q8; ssot_l13e Step-04
- **IMPACT:** Steps 09, 16, 19, 28, 36 claim language
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** No data-plane contract; COND/STATE/KGE/IMAP shared across planes; no plane field on any JSONL ledger
- **NEW:** Retro-fix 04.6 (P0): registry/data_plane_registry_v1.csv + firewall rules FW-01..FW-16 (parts/M0_data_planes.md)
- **WHY:** Recipe conditions would enter evidence COND via EVT.condition_id; PREDICTED/PLANNED/OBSERVED states in one ledger; KGE recipe statistics; IMAP duplicates of EVD
- **SOURCE / EVIDENCE:** this audit (repo schemas, KGE/IMAP recount); SSOT §232.3, §233.7
- **IMPACT:** Steps 08, 12, 16-18, 26-29, 35, 36
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** Similarity registry 21 types FROZEN but never human-reviewed; ids SIM-01..21 collide with simulation; COMPOSITIONAL/PROCEDURAL/process-response missing; fingerprint spec inconsistent
- **NEW:** Retro-fix 04.7: similarity registry v1.1 (alias to SIMTYPE-##; add COMPOSITIONAL, PROCEDURAL, PROCESS_RESPONSE, z_m^culinary, identity p_same; per-type null/eval set/split family/valid domain/evidence requirement; SIM-06 baseline + ECFP4-count comparator); human review
- **WHY:** No universal similarity scalar; structural != sensory; cultural != flavour
- **SOURCE / EVIDENCE:** r_representation_flavortwin Q1/Q9; ssot_l12; MP0 L110
- **IMPACT:** Steps 07I-C, 35, 36 FlavorTwin
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** SPLIT strategy enum lacks group/lineage/condition/platform/matrix options; no calibration partition; split groups = exact duplicate groups only
- **NEW:** Retro-fix 04.8: split contract (additive strategies; TRAIN/VAL/CALIBRATION/TEST; claim_id; feasibility_status; unit_of_independence; sealed-test access log; recipe split_group_id distinct from duplicate_group_id)
- **WHY:** Claim-first splits; SSOT §191.3 near-duplicates in one group; §257A.15 four partitions
- **SOURCE / EVIDENCE:** r_eval_splits; SSOT L14774-14801, L28326-28340; impl §9 item 11
- **IMPACT:** 07I-C, Steps 15, 16-20, 29-36
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** No annotation-independence contract; human gates failed on provenance (07H v3 files 11 s apart); GOLD_PENDING_INDEPENDENT_IAA allowed for calibration; EXP ledger lacks §257A.20 fields
- **NEW:** Retro-fix 04.10: annotation records with annotator_id, saw_model_output, blind packet hash, timestamps, hash commitment, adjudication log; validity checks; tier policy tightened (no G16-CAL claim from AI-assisted Gold); EXP template extended to 19 fields
- **WHY:** Anchoring evidence (Schroeder 2025; Choi 2024); repeated repo failures; SSOT inv. #14/#16
- **SOURCE / EVIDENCE:** r_recipe_semantics_gold Q8; reports/step07/step07h_human_gate_result.json; registry/recipe_quality_tier_registry_v1.csv row 7; SSOT L28408-28432
- **IMPACT:** Step-07 audit v4, 07I-C, 09, 19, 29-36
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** No reserved namespaces for later registries; MODEL- is the ML card
- **NEW:** Retro-fix 04.9 (P0): reserve DOC-, SEXP-, SMP-, OBS-, AGG-, DRV-, LIN-, XTR-, KIN-, MECH-, EFFSIG-, FMOD-, PARAM-, VAL-, APPDEC-, SIMRUN-/SIMTYPE-, SPLITGRP-, RCLM-; 04.11 confidence/applicability vocabulary (compatibility tri-state, match types, certainty-profile domains, recommendation labels) before Step 23
- **WHY:** Cheap now, expensive after ledgers exist
- **SOURCE / EVIDENCE:** r_mechanism_registry; r_rag_confidence; SSOT L26344-26347, L25206; RD L2429
- **IMPACT:** Steps 21-28, 36
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 05
- **OLD:** EVD export v1 (64 fields) has no independence_group, no lineage keys, no dispersion/n status, no aggregation level/method indicator, USDA rounding/imputation only in free-text notes
- **NEW:** 05.1 additive export v2 (exports/evd/evd_export_v2.jsonl) adding independence_group, study_id/publication_id/lineage_root_id/split_group_id/independence_resolution, evidence_level+parent_ids, aggregation_method, method_indicator, dispersion_type/n status (NOT_REPORTED_BY_SOURCE_ROW), censor_kind ROUNDED_INTERVAL, retention_definition, platform, regime, target_type, doi/table_or_figure; v1 untouched; built inside Step 08
- **WHY:** Step 08/15/29/36 need lineage keys and value documentation in the consumer view; EuroFIR/FAO value documentation; SSOT G15-1
- **SOURCE / EVIDENCE:** registry/schemas/evd_export_v1.schema.json (verified 64 props, no independence_group); r_evidence_model Q2/Q4; SSOT L22382, L16632
- **IMPACT:** Step 15 freeze and Step 29 read v2; no change to frozen v1
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 05
- **OLD:** Cap semantics USDA '100'->GT_CAP 97.5, Bognar '1.00'->0.995 undocumented; TRUE_ZERO, ROUNDED_INTERVAL, RANGE_ONLY, DIGITIZED, ESTIMATED_FROM_SUMMARY absent from registries
- **NEW:** 05.2 cap-semantics audit record (source pointer or downgrade to CENSORED_UNKNOWN); 05.4 registry v1.1 additions coordinated with Step 04/07.D
- **WHY:** censored-likelihood training and E4 extraction need complete status codes; SSOT L23973 has TRUE_ZERO
- **SOURCE / EVIDENCE:** registry/censoring_registry_v1.csv, value_origin_registry_v1.csv (verified); ssot_sparsity sec 9 item 4
- **IMPACT:** Steps 09, 29, 30
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 06
- **OLD:** Manifest records DS-006 USDA Cooking Yields replicate_information=no; 2026 API terms partly stale; 58/64 study_lineage_available UNKNOWN; no regime/K-level/platform/template columns; occurrence sources absent
- **NEW:** 06.2 corrections (DS-006 n/SD yes; DS-031/033/035/036 terms; add Abertay Glycation DB, Scheijen 2016, eBASIS, VCF, Zenodo occurrence sets as OCCURRENCE plane UNVERIFIED) and 06.3 additive columns regime, k_level_capability, member_lineage_recoverable, analytical_platform, per_article_licence_route, source_domain_template_id, full_text_capture_permission
- **WHY:** Step 08 needs member-lineage recoverability; Steps 11-14 need K-level-aware acquisition; occurrence data must not enter process-effect EVD
- **SOURCE / EVIDENCE:** data/external/usda_yields CSV header (n, SD verified); r_acquisition sec 2.4, 5; SSOT L19089-19110, L23445-23464
- **IMPACT:** Steps 08, 10-15
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 06
- **OLD:** H2 queue 21 items pending; census review unrecorded
- **NEW:** 06.1 recorded human decisions #1/#3/#4 before Steps 10/13; 06.4 SRC/SNAP registration of unregistered local files; 06.5 licence rulings queue (TASTEset, FlavorDB2, PE permission, CoSyLab)
- **WHY:** no first request to a new source without H2; no dataset without provenance/licence
- **SOURCE / EVIDENCE:** reports/h_state/es_1_2_source_census.md L138; MP L131-142
- **IMPACT:** gates Steps 10, 12, 13
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 07
- **OLD:** Human condition sub-gate = pooled kappa>=0.80 + no critical-field systematic disagreement; v3 counted only by file-provenance afterthought
- **NEW:** 07.A pre-label protocol amendment for packet v4: keep existing gate verbatim and ADD technical provenance-validity precheck (separate packet IDs, hash-commit before opening other file, mtime/identical-distribution tests), PABAK + raw + positive/negative agreement for fields with prevalence>0.9, per-item timing
- **WHY:** kappa paradox at prevalence 1.00; repeated reviewer-provenance failures; a strengthening made before any v4 label exists is not post-hoc weakening
- **SOURCE / EVIDENCE:** reports/step07/step07h_human_gate_result.json; condition_audit_protocol.md L25-29; r_eval_splits R-6, Q7; r_recipe_semantics_gold IAA
- **IMPACT:** gate for Step 15 condition fields and Steps 23, 29-33
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 07
- **OLD:** WORKLOG S133/S134: 'Step 08 only after the gate' (condition audit hard prerequisite of lineage)
- **NEW:** 07-DEP: Step 08 SOFT-depends on 07.A; 07.A HARD gate for Step 15 and any condition-using experiment (23, 29-33); 07I-C/07I-S HARD gate for recipe-level test splits (15 recipe plane, 16-20, 35, 36), not for Step 08
- **WHY:** lineage operates on SRC/DOC/STUDY, not on condition values; removes a false critical-path block
- **SOURCE / EVIDENCE:** W L904 vs L918; gov sec 9 item 8
- **IMPACT:** Step 08 can run in parallel with human audits; critical path shortens
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 07
- **OLD:** 07I-R provisional star families (6,589 strict edges) are the only identity product; 400-pair packet unlabeled; no split group
- **NEW:** 07I-C identity calibration substep (pre-registered Y_copy/Y_dish mapping, two blind reviewers, kappa/AC1, weighted calibrator, OP-MERGE + OP-SPLIT, sealed v2 packet with recall probes, >=30 scaled and >=60 cultural pairs) and 07I-S recall-oriented SPLIT_GROUP v1 (ledgers/recipe_identity/recipe_split_groups_v1.parquet)
- **WHY:** precision-oriented families under-group near-duplicates (leakage); no literature threshold transfers; SSOT 257A.15 groups before split
- **SOURCE / EVIDENCE:** r_l13e_identity; r_eval_splits Q4, R-2; SSOT L28326-28340
- **IMPACT:** Step 15 recipe splits, 16-20, 35, 36; absorbs L13E E13E-05/SX-14-03 (single owner)
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 07
- **OLD:** COND/MEAS vocab lacks water:food ratio, lid, start mode, geometry class, O2/headspace, tissue vs medium pH, per-axis provenance, condition_grid_id, endpoint cue flag; MEAS.family lacks SPME_GC_MS/extraction technique/instrument settings
- **NEW:** 07.B COND v1.1 and 07.C MEAS v1.1 additive registries (new axes UNKNOWN for existing rows; frozen data not re-normalized); 07R home declaration of 07H-R/07I-R as recipe-plane lane
- **WHY:** Steps 23/26/27/31-33 and platform/condition-OOD splits need these axes; leaching vs degradation confound
- **SOURCE / EVIDENCE:** r_simulator_vv (Delchier 2014); r_acquisition sec 5; ssot_l14 sec 1.7, 1.11; MEAS.schema.json enum verified
- **IMPACT:** Steps 09, 15, 23, 26-27, 31-33
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 08
- **OLD:** Step 08 undefined (missing card); no DOC/EXPERIMENT/SAMPLE/OBS/AGG/DRV levels; STUDY stubs; independence = source family or PE publication
- **NEW:** Defined deliverables 08.0-08.9: pre-registration; DOC, LIN, SEXP/SMP/OBS schemas; STUDY append versions; detector B0-B3 with seeded-copy recall; USDA<->Bognar overlap verdict; three-key independence registry (study_id, lineage_root_id, split_group_id + independence_resolution) with DRV parent-union merge; component-feasibility report; export v2; gates G08-1..9, G08-H
- **WHY:** Cochrane study-not-report unit; PROV/ISA/SOSA layering; SSOT Split 6, L25307-25310; MP AM3 giant-component rule
- **SOURCE / EVIDENCE:** r_evidence_model (HIGH); r_eval_splits Q3/Q4; SSOT L16886-16891, L23656-23667; MP L3597-3613
- **IMPACT:** Steps 09, 11-15, 24-27, 29-33, 36
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 08
- **OLD:** Lineage as a one-off step
- **NEW:** Split 08a (existing corpus, freeze v1) and 08b (lineage library src/culinarystate/lineage/ reused by Steps 11-14 at discovery time)
- **WHY:** duplicates must be linked before extraction, not after; propensity universe needs metadata for all discovered papers
- **SOURCE / EVIDENCE:** r_evidence_model sec 5; ssot_sparsity LA-14
- **IMPACT:** Steps 11-14 call 08b
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 09
- **OLD:** Machinery = AI/rule pre-check + human review packs; endpoint-only EVD schema; no XTR/ADJ/KIN
- **NEW:** Dual-extraction architecture (table-aware parse -> study-level record -> extractor A -> independent blind extractor B -> deterministic validators -> blind adjudication -> E5/E4), XTR/ADJ records, SciFact-style verifier label, DIGITIZED figure path, KIN/KINPT kinetic-experiment + raw time-point tables, provisional kinetic-parameter capture subset, field-class registry, prompt registry, gates G09-1..7
- **WHY:** MECIR C46; Buscemi 2006; Shankar 2026 (numeric 47-88%, omissions 60-74%); series must not be flattened before Step 11
- **SOURCE / EVIDENCE:** r_evidence_model Q7; r_acquisition sec 5; r_mechanism_registry Q7; r_rag_confidence; SSOT L16676-16690, L17299-17316, L19111-19136, L22800-22824, L34731-34756
- **IMPACT:** Steps 10-15, 21-27, 32, 36
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 09
- **OLD:** Accuracy expectation implicit in a 20-row pilot (Step 10)
- **NEW:** Step 10 = protocol shake-down; E4-at-scale accuracy gate pre-registered in Step 09 (PROPOSED_PILOT precision Wilson LB>=0.90 and omission-recall LB>=0.85 per critical field class on >=150 adjudicated instances; AI precision<0.85 -> human-first)
- **WHY:** 20 rows at 95% observed accuracy give CI [0.76,0.99]
- **SOURCE / EVIDENCE:** r_evidence_model Q7; RD gate via plan_detailed
- **IMPACT:** Steps 10, 11, 13, 14 sizing and human hours
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 09
- **OLD:** Extractor provider unspecified
- **NEW:** Local or licence-permitted model only; no licensed full text to external APIs without per-article licence + H2; prompts/models versioned (PROMPT-)
- **WHY:** RD L950 never send licensed text externally; licence law
- **SOURCE / EVIDENCE:** plan_detailed (RD L950); MP AY7 PROMPT-
- **IMPACT:** compute: local GPU helpful; A100 only after measured throughput + H3
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 10
- **OLD:** 20-row mechanism evidence extraction + human-verification pilot (ES-1.3); census leaned to potato acrylamide vs garlic alliinase
- **NEW:** Pre-registered protocol shake-down + extractability census: ~100 abstracts/system double-labelled for K-rung; 20 dual-extracted rows with hard-case mix (>=5 AA series, >=3 chlorophyll, >=2 negative cases, ND/LOD, RF>1, bracketed, figure-digitised, >=3 PE Route-A); focused-system decision by pre-registered rule (AA primary, chlorophyll fallback, acrylamide never first); no accuracy gate at n=20
- **WHY:** 20 rows cannot certify accuracy (95% obs -> CI [0.76,0.99]); first-system choice must be driven by validation data availability, not impressiveness
- **SOURCE / EVIDENCE:** r_evidence_model Q7; r_simulator_vv Q1/§6; r_acquisition §2.5/§4; es_1_2_source_census.md §11; SSOT §203.6 L17299-17316, §210.29A L19137-19163
- **IMPACT:** Sizes Steps 11/13/14; fixes Step 26 system; exposes schema defects before volume
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 10
- **OLD:** Dependencies implicit (census review + H2)
- **NEW:** HARD deps added: 04.K contract addendum, 08 schemas+detector v0, 09 dual-extraction protocol; 07 human audit SOFT (not blocking acquisition)
- **WHY:** Pilot must test the final protocol; lineage and trajectory fields must exist before extraction
- **SOURCE / EVIDENCE:** r_acquisition §5; r_evidence_model §4; gov §9 item 8
- **IMPACT:** Step 10 cannot start until 04.K/08/09 exist
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 11
- **OLD:** Single Wave-1 of verified mechanism rows (HV-001: >=40, aim 60-80)
- **NEW:** Three lanes: 11a focused-system K1/K2 depth with lab-level partition lock at acquisition; 11b AI5 12-family breadth incl. >=10 negative/inhibited and >=3 conflict candidates; 11c PE Route-A seed verification; machine-assisted E4 only after >=150 adjudicated instances/field class with Wilson LB >=0.90
- **WHY:** Depth (simulation/kinetics) and breadth (applicability/RAG) need different evidence shapes; lab is the unit of independence; numeric LLM accuracy 47-88%
- **SOURCE / EVIDENCE:** r_simulator_vv §5; r_evidence_model Q3/Q7; MP AI5 L3092-3110; MP AH7 L2868-2885; Shankar et al. 2026
- **IMPACT:** Creates first verified test subset; enables 21-24 and 26a; prevents validation contamination
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 12
- **OLD:** Serial Phase-C step after 10/11
- **NEW:** PARALLELIZE / MOVE EARLIER: run as soon as 04.x fields + 06.U SRC registration exist; three sub-planes (process-effect E3 / side-info / occurrence OCC-) + property-model candidates (Choi-Okos -> Step 24) + aggregate bibliography edges for Step 08
- **WHY:** No dependency on extraction machinery; prevents plane mixing; supplies physical/yield rows with n/SD
- **SOURCE / EVIDENCE:** r_acquisition §2.1-2.2, §3 R1/R4; SSOT §211.48 L19782-19793; §219.6 L23445-23463; MP AX2/AX3 L4380-4408
- **IMPACT:** Earlier physical/yield targets for 29/30; lineage edges for 08; plausibility bounds for 27/32
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 13
- **OLD:** Large literature discovery corpus (implicitly full-text harvest)
- **NEW:** 13a metadata+abstract CC0 corpus with per-document licence/OA status, K-rung triage, query log, duplicate linkage at discovery and paper-level metadata for ALL discovered papers (propensity universe), runs in parallel with Step 10; 13b extraction-at-scale gated on Step 10 metrics and G11-3
- **WHY:** PMC bulk retired Aug 2026; OpenAlex metered; MNAR propensity needs the studied universe; duplicates inflate effects
- **SOURCE / EVIDENCE:** r_acquisition §2.4; sparsity notes LA-14/LA-16; Tramer 1997; von Elm 2004; MP W10 L1837-1854
- **IMPACT:** Enables C3 MNAR analysis and active-learning evaluation; licence-clean release
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 14
- **OLD:** Coverage-driven growth (unit unspecified)
- **NEW:** Coverage cell = matrix-family x process-family x target-class x K-rung x condition-bracket, counted in independent lineage components (lab groups for kinetics); multi-criteria queue (no unjustified scalar) + >=30% random audit stream + acquisition log; consumer-readiness ledger (READY/PARTIAL/NEED_DATA per consumer 22-36); per-cell stop rules; declared-gap register
- **WHY:** Only 127 independence groups today; row counts mislead; active-learning gains unreliable without random stream
- **SOURCE / EVIDENCE:** r_eval_splits; r_transition_ml; SSOT §203.10 L17375-17385, §224 L24269-24387; MP W11 L1856-1890; Lowell et al. 2019
- **IMPACT:** Makes later NEED_DATA explicit; bounds human cost
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 15
- **OLD:** Single freeze of DATA-EVIDENCE v1 at end of Phase C
- **NEW:** 15a DATA-EVIDENCE v0-BOOTSTRAP right after Step 08 (existing E3 + lineage + claim-mapped split registry + dataset card + tensor/mask; labels BOOTSTRAP_UNVERIFIED; test cells inherited unchanged by 15b) and 15b full v1 (adds verified subset, KIN, SIM-CAL/SIM-VAL partitions, calibration split, licence matrix, conflict clusters, propensity covariates, sealed locked test with access log)
- **WHY:** Lets Steps 29/30 run on CPU in parallel with acquisition (SSOT §229.2 order: audit -> D0-D6 floor); prevents re-splitting after results
- **SOURCE / EVIDENCE:** SSOT §229.2-229.3 L24926-25001; §257A.15 L28326-28338; §257G.9 L34854-34862; r_eval_splits §4; MP AI5 L3102-3110
- **IMPACT:** Shortens critical path; requires ruling C2 on unverified E3 test labels
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 04
- **OLD:** EVD contract endpoint-only (no KIN/trajectory table; no SD/n/aggregation level; three overlapping SSOT kinetic lists)
- **NEW:** Substep 04.K: unified kinetic-experiment/trajectory table + dispersion/aggregation/censor_kind/K-rung/regime/DIGITIZED/occurrence/acquisition-log/SPLIT.strategy extension; prefixes SEXP-/OBS-/SMP-/DOC-/LIN-/XTR- (MEAS-/EXP- collisions)
- **WHY:** Without it acquired series are flattened to endpoints and Steps 24-27 lose inputs
- **SOURCE / EVIDENCE:** r_acquisition §2.0/§5; ssot_l15a C10; r_evidence_model §0/§3.1; SSOT §210.29 L19111-19136, §216.2 L22800-22824
- **IMPACT:** HARD prerequisite of Step 10
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 06
- **OLD:** ES-1.2 manifest (64 sources) with 2026 API rows partly stale
- **NEW:** Substep 06.U: update DS-031/033/035/036 (OpenAlex metered; PMC FTP/OA API retired Aug 2026; Crossref limits; Unpaywall 100k/day); add Abertay Glycation DB, Scheijen 2016, eBASIS, VCF, Zenodo monitoring sets; add K-rung/platform/matched-before-after columns; SRC registration for local files; close H2 #1/#3/#4/#5/#6/#9/#10
- **WHY:** Acquisition legality and rate planning
- **SOURCE / EVIDENCE:** r_acquisition §2.4/§5; es_1_2_h2_approval_queue.md
- **IMPACT:** HARD prerequisite of 10/12/13
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 07
- **OLD:** COND schema lacks product-vs-medium T, water ratio, lid, geometry, tissue pH, O2, kinetic units
- **NEW:** Substep 07.C additive COND axes + T_K + kinetic UNIT entries + per-axis provenance + texture/colour instrument settings; the 07 human audit v4 is SOFT for Phase C (blocks condition-derived claims, not acquisition)
- **WHY:** Simulator ICs/BCs, applicability windows and leaching identification
- **SOURCE / EVIDENCE:** r_simulator_vv §5.1; ssot_l15a §10; impl §10
- **IMPACT:** Fields land structured instead of raw text
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 16
- **OLD:** Instruction semantic schema (card missing; implied scope: schema for instruction semantics only, serially after Step 15)
- **NEW:** Schema pack v1 (EVT/ENTITY/STATE/QNT/POR/ALLOC/REF/INST/GRAPH with event_kind, implicit_args, alternative_group_id, modality, temporal_relation, condition_profile_id, transformation_mode, tool_roles, entity parentage/lifecycle, 3-axis field metadata, quantity intervals, POR distributions, annotation_mode) + PROC/TOOL/ING-facet hierarchy (ENDPOINT moved to V_ENDPOINT) + handbook v2 + hard-case answer keys + DG-0 design pilot + pre-registered Deep-Gold sampling frame; runs in parallel with Phase C
- **WHY:** SSOT 257C/238 give field names only (no types); 257D has no answer keys and no entity/state cases; PROC has 0 parents; Gold needs a frozen schema and frame; no artifact dependency on Steps 08-15
- **SOURCE / EVIDENCE:** SSOT L25323-25499, L29336-31464, L31465-33895, L27725-27738, L42824-42838; r_recipe_semantics_gold Q1-Q6; ssot_annexA/B; repo recount PROC/ING/TOOL
- **IMPACT:** Steps 17-20, 22, 23, 29, 35, 36 get stable fields; Gold can start earlier
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 17
- **OLD:** Instruction-level extraction (card missing)
- **NEW:** Typed P2'-P7 pipeline with B0 rules/compiler, B1 frozen NER/linker, B2 supervised graph parser (mandatory strong baseline), B3/B4 local LLM + validators/repair, B5 cascade; oracle cascade mandatory; CQPO grounding substep 17.3 owning POR import (human-verified, licence-checked); per-field error table; invented-value audit = 0; selection on DG-1 dev only
- **WHY:** LLMs build structure poorly vs graph parsers (PAGED 2024; Gajo et al. 2026); repo compiler shows event construction is the bottleneck; CQPO/POR had no spine owner; G13-3 needs extraction-error estimates
- **SOURCE / EVIDENCE:** r_recipe_semantics_gold Q2/Q6; MP AW3/AW8/AW9 L4145-4330; SSOT L15171, L26255; reports/del3/compiler_vs_gold_v1.md
- **IMPACT:** Silver engine chosen empirically; downstream confidence features get real error rates
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 18
- **OLD:** Event-sourcing engine (card missing; engine prototype exists)
- **NEW:** Persist v1 ledgers; hard invariants; correlated interval propagation; online vs offline prefix; exports transition_tuples_v1 (occurrence only, magnitude_eligible=false, endpoint-leakage flag, split_group_id) and prefix_packets_v1; engine fidelity (oracle events >= 0.95) separated from predicted-event accuracy
- **WHY:** Steps 22/29/36 need a defined interface; simulator data contract forbids recipe magnitudes; state errors must be attributable to extraction not engine
- **SOURCE / EVIDENCE:** SSOT L25323-25399, L26277-26296, L34966-34969; RD L592-599, L1612; docs/simulator_data_contract.md
- **IMPACT:** Clean recipe-to-transition interface; no chemistry leakage from procedure
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 19
- **OLD:** Gold state-trajectory pilot after Steps 17-18 (card missing)
- **NEW:** Start right after the Step-16 gate, in parallel with 17/18: re-tier 40 AI-assisted Gold to MODEL_ASSISTED_HUMAN_REVIEWED (Gold-Light) and remove their calibration eligibility; build DG-1 (200 recipes at A2, 60 at A4; fallback 100) by probability sample from held-out SPLIT_GROUPs; technically enforced blind dual annotation + adjudication; partitions dev/calibration/sealed test frozen before any model scoring; timing log; human-reviewed sessions; shared human queue with 07I-C and Step-07 audit v4
- **WHY:** No independent Gold exists; anchoring evidence (Schroeder 2025; Choi 2024); repo gate provenance failures; SSOT says Deep Gold DO EARLY; Step 17 selection needs Gold dev
- **SOURCE / EVIDENCE:** SSOT L25659-25744, L25147-25170, L27446, L28326-28338, L42712, L42721; r_recipe_semantics_gold Q7-Q10; r_eval_splits Q7-Q8; D-016/D-017
- **IMPACT:** G16-DATA becomes achievable; Step-17 gate becomes scorable; human-time demand front-loaded
- **BREAKING?** YES
- **REQUIRES HUMAN APPROVAL?** YES

## Step 20
- **OLD:** Scale procedural semantic corpus (implied 60k-100k Silver from the 612k base)
- **NEW:** Tiered corpus: T0 deterministic over all 611,714 exact reps; T1 Silver 1k->5k->10k pilot then 25k/60k only if pre-registered Silver-utility gain on DG-dev; one rep per SPLIT_GROUP, Food.com capped, inclusion weights; T2 Gold-Light 3-5k units with >=30% random; 257P all-but-P-A11 before pilot, all 15 before >10k; DATA-SEM-SILVER v1 release with 257G audit tables
- **WHY:** Brief 31 forbids treating all 612k as expensive annotation; Silver utility unproven (RD L148, L158-163); licence: training_allowed UNKNOWN for 535,151 recipes; SSOT vs MP 257P scope must be reconciled
- **SOURCE / EVIDENCE:** SSOT L25587-25658, L27490-27501, L42705-42743; MP L386, L3802-3810; r_recipe_semantics_gold 3.5
- **IMPACT:** Bounded cost; no fabricated scale; honest licence-limited corpus
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 07I-C (lookahead substep of Step 07)
- **OLD:** 400-pair duplicate calibration packet unlabeled; families PROVISIONAL_STAR_V1 used as the only grouping
- **NEW:** Identity calibration substep 07I-C: blind dual labels, kappa + Gwet AC1, weighted calibrator, OP-MERGE/OP-SPLIT, sealed v2 with recall probes, recipe_split_groups_v1 (recall-oriented) separate from precision-oriented identity relations; parallel to 08-15, must pass before any recipe-level test split is frozen
- **WHY:** Precision-oriented families under-group near-duplicates (6,589 edges of 744,615 pairs); SSOT 191.3 requires near-duplicates in one split group; split groups are a hidden prerequisite of Steps 16.5, 17, 19, 20, 35, 36
- **SOURCE / EVIDENCE:** r_l13e_identity 3B; r_eval_splits Q4/R-2; SSOT L14782-14785, L43395-43537, L44868-44891
- **IMPACT:** Leakage-safe recipe splits; Gold firewall extends to near-duplicates
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 21
- **OLD:** Title only (step card missing): 'Effect / mechanism ontology'
- **NEW:** Mechanism & effect registry (MECH-): small native append-only registry (~20-40 entries) with preconditions, three-valued per-axis condition gates, inhibitors, competes_with, history dependence, marker_unique=false, external ontologies xref-only (human-verified); no numeric parameters; substeps 21a schema (pulled earlier, before Step 09/10 freezes), 21b seeds, 21c effect vocabulary, 21d PROC->MECH crosswalk (HV-010), 21e xref audit
- **WHY:** No OBO ontology covers food mechanisms; RXNO Strecker reaction/degradation label collision makes auto-mapping unsafe; extraction steps 09/10 need the schema to know what to capture
- **SOURCE / EVIDENCE:** r_mechanism_registry F4.1/F5.1-F5.4; SSOT 144.1 L8976-8986; MP W6 L1689-1725; PROC.jsonl 156/156 UNVERIFIED; contract C7 L71
- **IMPACT:** Phase-E schema work becomes a parallel lane runnable before Step 09 freeze; does not block Step 08
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 21/24
- **OLD:** MODEL- namespace = ML model registry (MP X6 L2028-2046; ledgers/schemas/MODEL.schema.json)
- **NEW:** New FORM- namespace for formula/kinetic models (or model_kind discriminator), plus MECH-, EFFSIG-, PARAM-, VAL-, APPDEC- reserved in Step 04 (retro-fix 04.x-ME1)
- **WHY:** Name collision would conflate ML checkpoints with mechanistic equations
- **SOURCE / EVIDENCE:** r_mechanism_registry s3.2; MP X6; repo MODEL.schema fields
- **IMPACT:** ID scheme change (H4); MODEL has 0 rows so no migration
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 22
- **OLD:** Title only (step card missing): 'Event -> effect signatures'
- **NEW:** EFFSIG- signatures separating (A) direct deterministic changes referenced from Step-18 engine and (B) candidate effects (mechanism, target, allowed directions) with is_evidence=false; split 22a process-level (after 21) / 22b event-bound (after 16,18); shared expert case set with Step 23
- **WHY:** Prevents verb->chemistry shortcuts (MP L82), duplication of Step-18 mass/geometry logic, and EFFSIG leakage into evidence plane
- **SOURCE / EVIDENCE:** SSOT 199.6 L16173-16183; 199.8 L16209-16233; simulator_data_contract.md; r_mechanism_registry s4
- **IMPACT:** 22a can run in parallel with Phase D; 22b stays after 18
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 23
- **OLD:** Title only (step card missing): 'Mechanism applicability engine'
- **NEW:** Evidence-first gate sequence G0-G9 with three-valued verdicts, decision unit entity_version x event x target, competing-mechanism gate, input-observability gate, calibration vs validated vs M&S-limit domains, route enum DIRECT/INTERPOLATE/SIMULATE/QUALITATIVE/ASK/UNKNOWN (+orthogonal CONFLICT), replayable APPDEC records; primary safety gate = false-activation CP upper bound <=0.05 [PROPOSED-PILOT] plus hard invariant UNKNOWN never -> SIMULATE
- **WHY:** Brief s20 chain is sound only as the simulation branch; needs six corrections
- **SOURCE / EVIDENCE:** r_mechanism_registry F6.1, F2.2-F2.4; r_simulator_vv Q5; r_rag_confidence; SSOT 231.2 C7/C8 L25206-25207; 215.60 L22525-22539
- **IMPACT:** Step 36 consumes route enum and APPDEC; Step 26 callable only via SIMULATE routes
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 24
- **OLD:** Title only (step card missing): 'Formula / model registry'
- **NEW:** FORM/PARAM/VAL registries (substeps 24a schema pulled earlier; 24b populate SIM-AA-1/SIM-CHL-1 + PROPERTY_MODEL Choi-Okos; 24c REPRODUCED tests; 24d VAL plan hash-linked to Step-15 partitions; 24e = Step 25); lifecycle CANDIDATE->REIMPLEMENTED->REPRODUCED->CALIBRATED->VALIDATED_HELD_OUT/RESEARCH_ONLY; MCP calibration domain; Constraint-expression assumptions; KiSAO solver; SBML/FSKX export only
- **WHY:** Fit != validation (QMRF); box domain inadequate (Sahigara 2012; Baranyi 1996); matrix-specific parameters (Ea ~12->130+ kJ/mol for AA); no open food kinetic-parameter DB
- **SOURCE / EVIDENCE:** r_mechanism_registry F1.1-F3.1, F7.1; r_simulator_vv Q1-Q4; r_acquisition s2.3; SSOT 210.27-210.30, 211.38/211.48/211.50
- **IMPACT:** 24b is NEED_DATA until Steps 10-11 deliver verified K1/K2 series; Step 32 must reuse registry (no second registry)
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 25
- **OLD:** Title only (step card missing): separate top-level step 'Parameter-compatibility retrieval'
- **NEW:** Executed as substep 24e inside the Step-24 work package (spine number 25 retained); rule-first hard filters + categorical match vector + declared lexicographic axis priority + domain location + lineage-deduplicated multiplicity handling; NO_COMPATIBLE_SET hard-blocks SIMULATE
- **WHY:** No independent inputs or consumers before Step 26; dense retrieval inappropriate (semantic similarity != experimental compatibility; repo rerankers hurt)
- **SOURCE / EVIDENCE:** r_mechanism_registry F8.1; SSOT 241.3 L26339-26347; 211.38 L19669-19683; reports/del4/retrieval_silver_v1.md via r_rag_confidence
- **IMPACT:** Reduces orchestration overhead; no renumbering
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 03
- **OLD:** SVAR registry: SVAR-FUT-019 'kinetic parameter' registered as a state variable; no enzyme_activity_state / cell_integrity / thermal-dose SVARs; aw and precursor conc. not_applicable_yet
- **NEW:** Retro-fix substeps 03.x-ME1 (add history/state SVARs, activate SVAR-FUT-002/014, add delta_semantics and bounds_type) and 03.x-ME2 (retire SVAR-FUT-019 to PARAM)
- **WHY:** Mechanism preconditions and history dependence need state; parameters are not state
- **SOURCE / EVIDENCE:** registry/state_variable_registry_v1.csv; r_mechanism_registry F5.4(v); SSOT 199.6
- **IMPACT:** Additive registry change; nothing re-run
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 07
- **OLD:** UNIT ledger has no kinetic units; COND mask lacks water:food ratio, lid, start mode, tissue vs medium pH; condition human audit NOT_COUNTED
- **NEW:** Retro-fix 07.x-ME1 (kinetic UNIT entries, T_K derived column, additive COND axes) and 07.x-ME2 (condition-gated PASS capped at UNKNOWN until audit v4 validly passes)
- **WHY:** Step 24 dimensional checks; Step 23 input observability; provenance law
- **SOURCE / EVIDENCE:** ssot_l15a s1.9; reports/step07/step07h_human_gate_result.json; r_simulator_vv s5.1
- **IMPACT:** Additive; frozen fingerprint untouched for existing fields (new version for additions)
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step RXN (21/24)
- **OLD:** RXN.schema lacks rate law, condition window, kinetic parameter ids
- **NEW:** Additive fields rate_law_form_id, kinetic_parameter_ids, condition_window, mechanism_id; RXN rows only for species-resolved, evidenced reactions
- **WHY:** MP W6 requires rate law/condition window; G15-RXN; 'never manufacture a balanced reaction'
- **SOURCE / EVIDENCE:** ledgers/schemas/RXN.schema.json; MP L1689-1725; SSOT L22402-22410
- **IMPACT:** Schema additive; 0 rows
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 26
- **OLD:** Implement one focused deterministic simulator (system unspecified; SSOT §210.29A/§226.5 anchors = acrylamide/potato frying and glucose/glycine Maillard)
- **NEW:** SIM-AA-1 ascorbic acid (water/steam, 60-100 C; degradation + lumped leaching) as first simulator; SIM-CHL-1 chlorophyll as single pre-registered fallback; acrylamide/Maillard moved to Step 32 extension as RESEARCH_ONLY; selection fixed by Step 10/11 census decision record before fitting
- **WHY:** Largest independent K1/K2 literature, established equation, low COU risk, answers MP L614/L2200 leaching-vs-destruction question, aligns with SSOT §144.3 broccoli x steam/boil curation cell; acrylamide is precursor-dependent, safety-critical and poorly identified
- **SOURCE / EVIDENCE:** r_simulator_vv Q1 (Giannakourou & Taoukis 2021 [V]; Knol et al. 2009 [V-meta]; Steet & Tong 1996 [V]); r_acquisition R3; SSOT L19137-19162, L24541-24547, L8992-8998
- **IMPACT:** Steps 10-14 acquisition targets AA/CHL series; Steps 21-25 populate AA/CHL entries first; SSOT CR PROPOSED_ONLY
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 26
- **OLD:** Kinetic fitting machinery implicitly located in Step 32 (Focused kinetics), after its consumer
- **NEW:** Substep 26a: shared kinetic fitting + identifiability + D-optimal design library (one-step global ref-T Arrhenius, censored likelihood, profile/cluster bootstrap, hierarchical, §211.50 report); Step 32 reuses it
- **WHY:** Simulator calibration is itself a focused kinetic fit; hidden prerequisite placed after its consumer
- **SOURCE / EVIDENCE:** r_simulator_vv Q7 (HIGH); ssot_l15a C3; r_transition_ml (Step 32 must reuse Step 26 artifacts); SSOT §211 L19188-19853
- **IMPACT:** Step 32 re-scoped to K-ablation (KA0-KA6) and second system; no renumbering
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 26
- **OLD:** Step 26 sequential after Phase E
- **NEW:** PARALLELIZE data-free substeps 26a/26b/26c (library, code, verification incl. synthetic truth recovery) with Phases C-E once Step 24 FORM/PARAM and Step 04 SIM/KIN schemas are frozen; 26a D-optimal helper feeds Step 11/14 acquisition targets; 26d calibration still waits for Step 15
- **WHY:** No real data needed for verification; early design guidance raises acquisition yield (SSOT §224.4-224.5)
- **SOURCE / EVIDENCE:** SSOT L24300-24323; r_mechanism_registry §5 (freeze schemas early)
- **IMPACT:** Earlier detection of identifiability problems; requires Step 24 schema freeze earlier
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 26
- **OLD:** No verification/credibility contract
- **NEW:** G26-VER (code + solution verification, synthetic truth recovery coverage, negative-design identifiability) and G26-CAL (practical identifiability; G15-4 candidate evidence); model card SIMM- with COU, model-risk grade, domain of verification, calibration domain (MCP+kNN), M&S limits, validation_status=NOT_VALIDATED
- **WHY:** Brief §41 'no simulator without validation'; NASA-STD-7009B / ASME V&V 40 vocabulary; SSOT §273.2 recovery-first logic
- **SOURCE / EVIDENCE:** r_simulator_vv Q3 (NASA-STD-7009B [V], FDA 2023 [V]); r_mechanism_registry Q1-Q3
- **IMPACT:** New artifacts registry/simulator_model_cards/, reports/step26/*; SIMM- prefix (SIM- stays per-run id)
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 27
- **OLD:** Validate simulator on real held-out evidence (design unspecified)
- **NEW:** One-shot pre-registered lockbox frozen in Step 15; unit = lab group; tiers HV-1 (gated)/HV-2/HV-3 (mapping)/HV-L; baselines S27-B0..B4; controls NC-1..NC-4; cluster bootstrap or sign-flip; >=5 validation groups eligibility; domain-of-validity artifact; NASA-7009B levels; RESEARCH_ONLY on fail
- **WHY:** Fit != predictivity (QMRF); labs publish many papers; adaptive holdout reuse overfits; few clusters break cluster-robust SEs
- **SOURCE / EVIDENCE:** r_simulator_vv Q3-Q5; r_eval_splits (Cameron 2008, Bates 2023); r_mechanism_registry Q2-Q3; SSOT L19529-19538, L21106-21124, L24119-24121
- **IMPACT:** Step 15 must freeze SIM-CAL/SIM-VAL/DS-TEST for AA and CHL; Step 08 must provide lab-level lineage
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 27
- **OLD:** USDA R6/Bognar vitamin C aggregates could be read as validation data
- **NEW:** E3 rows (423 active) used only as plausibility envelope labelled NOT_VALIDATION; never gated
- **WHY:** Conditions UNKNOWN (0 rows with both T and t), study NOT_IDENTIFIABLE; validation with imputed inputs violates no-invented-value law; SSOT L19782-19792
- **SOURCE / EVIDENCE:** G_F read-only recount of EVD/COND 2026-10-22; correction of r_simulator_vv count (1,196 = version lines)
- **IMPACT:** No change to data; prevents a false validation claim
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 28
- **OLD:** Generate controlled E7 synthetic prior (runs after 27 in spine)
- **NEW:** DEFER-by-gate: prior/pretraining generation only from a VALIDATED_HELD_OUT sim_version; before that only identifiability/design/method-benchmark uses; renamed TIER-E7
- **WHY:** SSOT §223.2 S-MECH strongest only when a validated model exists; §274.5 simulators first for validation/stress testing, pretraining gated; namespace collision with L12 E7, L13E Phase E7, MP E0-E14
- **SOURCE / EVIDENCE:** SSOT L24078-24080, L44385-44394; mp_part1 gap #2; r_simulator_vv Q6
- **IMPACT:** Step 30/33 E7 ablation arms only after 27 PASS
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 28
- **OLD:** SSOT §223 controls: ratio sweep, TSTR/TRTR, memorisation checks
- **NEW:** Add C-2 real-n learning curve, C-4 matched-volume randomized/wrong-physics simulator control, C-5 calibration-leakage partition algebra, C-7 variability-span check, C-8 pre-registered calibration-damage threshold; full per-row provenance; separate DATA-SIM plane with CI firewall; simulator_family/clock tags
- **WHY:** Gains may reflect extra examples (§274.2 analogue); calibration studies could leak into downstream test; Read et al. 2019 span precondition; G15-10 'unacceptable calibration damage' unquantified
- **SOURCE / EVIDENCE:** r_simulator_vv Q6 (Read et al. 2019 [V-meta], Shumailov 2024 [V], Esteban 2017 [V]); SSOT L44358-44360, L22391; ssot_l13e GAP (simulator_family/clock)
- **IMPACT:** Controls executed in Steps 30/33; Step 04 schema additions
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 28
- **OLD:** Reaction-network discovery (SINDy/CRNN) without spine home
- **NEW:** Housed in Step 28 as optional RESEARCH_ONLY method benchmarks on simulated trajectories (simulator recovery studies)
- **WHY:** SSOT §213.43A: SINDy/CRNN belongs to simulator recovery studies or unusually dense D-C data
- **SOURCE / EVIDENCE:** ssot_l15b §2.2, §8 (Step 28), gap 11
- **IMPACT:** No new step; Step 33 reaction arm stays deferred
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 32
- **OLD:** Focused kinetics as first owner of kinetic fitting and G15-4
- **NEW:** (cross-phase note for G_G) Re-scope to KA0-KA6 kinetic ablation vs Steps 30/31 on the same study-disjoint test, model-family selection, second system only after 27 PASS; reuse 26a + PARAM; G15-4 first evidenced in 26d and re-confirmed in 32
- **WHY:** Avoid duplicate fitting; ownership clarity
- **SOURCE / EVIDENCE:** r_simulator_vv Q7; r_transition_ml Step 32
- **IMPACT:** Gate ownership change G15-4
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 29
- **OLD:** Step 29 sits after Phase F (26-28) in the linear spine
- **NEW:** Step 29 hard-depends only on 05, 08 and a Step-15 E3-stratum freeze. It runs in parallel with Phases C-F. Numbering is preserved.
- **WHY:** Nothing produced by Steps 16-28 is an input to the endpoint bootstrap. SSOT §216.9 lists retention baselines as runnable now.
- **SOURCE / EVIDENCE:** SSOT §216.7 L22898-22929, §216.9; TB contract inputs; ssot_l15b §6
- **IMPACT:** Earlier C9 fallback for Step 36 and an earlier VoI signal for Step 14
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 29
- **OLD:** Ladders D0-D11 (SSOT), AZ6 D-numbering (MP L4700-4711), TB B-0..B-5 and M0-M11 coexist with no crosswalk
- **NEW:** SSOT §209.17 is canonical. Publish registry/transition_ladder_crosswalk_v1.csv and retire MP AZ6 numbering.
- **WHY:** AZ6 contradicts the SSOT and the plan's own AI6, and places neural rungs before completion (forbidden, L18607)
- **SOURCE / EVIDENCE:** SSOT L18543-18613; MP L3127-3139 vs L4700-4711; TB L17
- **IMPACT:** G15-2 'D0-D6' becomes interpretable
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 29
- **OLD:** Headline rule ambiguity: SSOT §202.3 (pair-holdout + study-disjoint) vs TB section 6 (support only on S-3/S-4 cold)
- **NEW:** Keep TB section 6 as the primary pre-registered criterion. Report pair-holdout with C-classes as the secondary 'compositional, non-cold' headline. S-6 is PE-only, S-7 is DIAGNOSTIC_ONLY, and a both-new abstention stratum is added.
- **WHY:** DEL-2 already showed D5 winning pair-holdout on USDA/Bognar, so promoting pair-holdout to the success criterion now would be post-hoc gate weakening
- **SOURCE / EVIDENCE:** SSOT L16898-16900; TB L19-L29; reports/del2/*
- **IMPACT:** Prevents post-hoc weakening and makes the headline split explicit
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 29
- **OLD:** Conformal calibration on random calibration partitions (DEL-2)
- **NEW:** Calibration partitions are group-disjoint in the same family as each test split and lineage-disjoint (Dunn et al. 2023 subsampling / CV+); worst-cluster coverage is reported
- **WHY:** Cold-split under-coverage of 0.72-0.87 at nominal 0.90
- **SOURCE / EVIDENCE:** WORKLOG S017 L117; r_transition_ml Q6; r_eval_splits Q6
- **IMPACT:** Honest coverage; required for G15-6 and Step-36 MODEL rung eligibility
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 29
- **OLD:** Phase-G results on existing E3 rows treated as confirmatory
- **NEW:** PG-5: all results on the 17,978 DEL-2-inspected rows are labelled 'pre-registered re-analysis with known prior exposure'. Fresh confirmatory status applies only to rows first sealed at Step 15.
- **WHY:** DEL-2 already read outcomes on every split of these rows
- **SOURCE / EVIDENCE:** reports/del2/*; r_eval_splits Q5 (Dwork et al. 2015 adaptive reuse)
- **IMPACT:** Claim wording in the paper map and the decision records
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 29
- **OLD:** No preconditions on D7 reuse, the test hang or the environment
- **NEW:** Substep 29.3: fix or explain the test_transition hang; get a human-authorised Python environment; run a read-only diagnosis of D7 == D1 on PE before any D7 number is reused
- **WHY:** D7 reproduces D1 to 4 decimals on every PE split; the suite is not green; pandas is absent on this server
- **SOURCE / EVIDENCE:** reports/del2/PHENOL-EXPLORER-3.6_results.md (checked); WORKLOG L924; ctx.md
- **IMPACT:** Prevents propagating a degenerate baseline
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 29
- **OLD:** Censor handling: training at bound 0.975; only aggregated censor-aware MAE is reported
- **NEW:** Report censored and uncensored strata separately in V0. Interval/Tobit training arms are added in Step 30. The bound arm is kept for continuity only.
- **WHY:** Bound substitution conflicts with SSOT §201.9/§222.5. 37% of USDA rows are GT_CAP and D0 median AE is 0.0 on USDA matrix-disjoint, so persistence's cold advantage may be partly a cap artefact (UNVERIFIED magnitude).
- **SOURCE / EVIDENCE:** SSOT L16705, L23998; reports/del2/USDA-RETN-R6_results.md
- **IMPACT:** May change the interpretation of the DEL-2 negative result (retained either way)
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 30
- **OLD:** D3 = nested target x process -> process -> global shrinkage; D6 skipped ('GPU'); D7 = biased MF only
- **NEW:** Add D3-full (crossed random-effects censored GLMM incl. food group, process family, target class and study/source), D3-R ridge, D5-tuned (CatBoost/LightGBM, nested grouped CV), D6 TabPFN v2 on CPU (licence priorlabs-1-1 = Apache-2.0 + attribution, HF card checked), and D7a (fixed), D7d FM with side features, D7e soft-impute, D7b BPMF if practical
- **WHY:** The repo D3 under-implements SSOT D3 (L18565-18572). G15-2 requires D6. The SSOT mandates MF/FM/soft-impute before any neural CF.
- **SOURCE / EVIDENCE:** SSOT L18565-18595, §220.4 L23606, L23781, L23892; HF Prior-Labs/TabPFN-v2-reg card; Karamcheti et al. 2025
- **IMPACT:** Makes G15-2 passable and G15-9 decidable
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 30
- **OLD:** G15-9 compares D7 against D5/D6 only and has no margin or decision record
- **NEW:** G15-9 operationalised: >=2 of 4 cold families, D7 vs max(D3-full, D5, D6), paired-cluster LB > delta_30, worst-cluster coverage not worsened by more than 0.05. A formal ACCEPT/REJECT record is written.
- **WHY:** SSOT §220.4 says D3 serves the same purpose as factorisation, so D7 must beat it. 'Beats' has no threshold in the SSOT.
- **SOURCE / EVIDENCE:** SSOT L22390, L23590-23606; ssot_sparsity §9 #11
- **IMPACT:** Prevents promoting completion over an unbuilt control
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 30
- **OLD:** Propensity from marginal frequencies; IPW-MAE reported next to headline numbers
- **NEW:** Covariate propensity model (year, platform, source type, popularity) once Step 08/13 metadata exist; until then marginal frequency labelled 'proxy'. Clipped IPS, positivity/overlap report, sensitivity-only use.
- **WHY:** SSOT §220.5/220.10; MP AM4; the propensity universe needs metadata on unextracted papers
- **SOURCE / EVIDENCE:** SSOT L23612-23688; WORKLOG S017 L115; ssot_sparsity LA-14
- **IMPACT:** Adds a look-ahead requirement on Step 13
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 31
- **OLD:** Single Step 31 placed before focused kinetics, run as its own modelling step
- **NEW:** 31a: generic features (log t, 1/T_K, Omega at a pre-declared 3-value literature Ea grid, heat mode, water contact) as an ablation inside the Step-30 harness on identical rows with measured conditions, with cooking and storage strata reported separately. 31b: Omega from fitted posteriors after Step 32.
- **WHY:** SSOT §215.71 vs §216.7 order conflict; fitted features need Step 32 outputs; PE series are mostly storage
- **SOURCE / EVIDENCE:** SSOT L22707-22722 vs L22914-22918; L18856; r_transition_ml; r_simulator_vv
- **IMPACT:** Resolves the ordering conflict without renumbering
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 31
- **OLD:** No human gate on condition values
- **NEW:** HARD HUMAN gate: the Step-07 condition audit (packet v4) is validly passed and the months->seconds content bug is fixed before any condition-feature claim
- **WHY:** The 07H human gate is NOT_COUNTED_PROVENANCE_INVALID; condition values are not human-validated
- **SOURCE / EVIDENCE:** reports/step07/step07h_human_gate_result.json; r_eval_splits Q0
- **IMPACT:** Step 31 is blocked until Step 07 retro-fix 07.x completes
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 32
- **OLD:** Step 32 owns kinetic fitting and identifiability, after the simulator (26-28)
- **NEW:** The single-system fitting/identifiability library moves to Step 26a (shared). Step 32 becomes the K0-K6 ablation plus cross-study hierarchical generalisation against Step 30/31 on the same study-disjoint test. Second system (chlorophyll or acrylamide/Maillard RESEARCH_ONLY) only after Step 27 PASS.
- **WHY:** Calibrating the Step-26 simulator is itself a focused kinetic fit, so the machinery is a hidden prerequisite of Step 26
- **SOURCE / EVIDENCE:** r_simulator_vv Q7; ssot_l15a C3; SSOT §211, §215.57
- **IMPACT:** Removes duplication and fixes a hidden prerequisite
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 32
- **OLD:** Implicit assumption that kinetic data can be derived
- **NEW:** 32.0 census gate with PROPOSED quotas (>=30 K1+ series from >=10 groups, >=3 K2-design groups); NEED_DATA until met; no Arrhenius from D-A aggregates
- **WHY:** 0 D-C series in the repo; ES-1.2 SOURCE_GAP; SSOT L19790
- **SOURCE / EVIDENCE:** r_simulator_vv §0; r_acquisition; DECISIONS L119
- **IMPACT:** Sends quotas to Steps 10-14
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 33
- **OLD:** Hybrid comparison without explicit E7 controls or scope limits
- **NEW:** Three arms on identical rows (mechanistic / best ML / sequential endpoint-residual hybrid). E7 arm only from a Step-27-passed sim_version, with ratio sweep, matched-volume randomized-simulator control, real-n learning curve and calibration-leakage audit. Reaction-network arm moves out of scope to a Step-28 simulator-recovery study.
- **WHY:** SSOT §223 lacks L15 randomized-simulator and leakage controls; G15-RXN prerequisites are absent
- **SOURCE / EVIDENCE:** r_simulator_vv Q6; SSOT L21211, L22402-22414; Read et al. 2019
- **IMPACT:** Prevents E7 smuggling test-study information
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 34
- **OLD:** Single short-rollout step requiring intermediate states
- **NEW:** 34a composition/semigroup test on existing USDA (1,429) and PE (195) composite rows, after a USDA multiplicativity circularity check; 34b trust horizon NEED_DATA; 34c rollout abstention spec consumed by Step 36
- **WHY:** There are no intermediate states; composite rows still allow a cheap falsification test of chaining one-step models
- **SOURCE / EVIDENCE:** r_transition_ml Q9; SSOT §212.52A L20537-20549, L20556-20566, G15-8/G15-11
- **IMPACT:** Gives Step 36 a rule for multi-step queries now
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 29-34
- **OLD:** Gate thresholds absent or labelled 'acceptable/meaningful/declared'
- **NEW:** registry/phase_g_preregistration_v1.csv holds every numeric threshold (K, delta, c_floor, coverage window, Ea grid, dead band, rho, c_min/eps_max/tau), PROPOSED_PILOT, frozen before the first locked read; changes are logged in DECISIONS and affected results are labelled exploratory
- **WHY:** G15 gates have no numbers; §202.17 pilot values are unrecoverable; no post-hoc gate weakening
- **SOURCE / EVIDENCE:** SSOT L22380-22396, L17105-17115; ssot_l14 §4.5
- **IMPACT:** Every Phase-G gate becomes falsifiable
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** Single late step after Phase G (serial 34->35) covering all of L12+L13.
- **NEW:** Step 35 kept at its number but split into substeps 35.0-35h + optional 35-E; explicit rungs (35.0-35e, 35-E) run as a parallel CPU lane once Step 04 contracts and 07I-C split groups exist; learned (35g) and process-conditioned (35f) rungs stay late.
- **WHY:** No artifact dependency of explicit rungs on 29-34; SSOT calls L12 empirical 'CORE EXECUTION PRIORITY' and 'PARALLEL'; L15 must not depend on L12 embeddings.
- **SOURCE / EVIDENCE:** SSOT L169, L13219-13244, L27732, L22967-22977 (§216.10); MP L237 (B04 parallel after B02)
- **IMPACT:** Earlier availability of static FlavorTwin baselines and L12/L13 decision records; no change to critical path (08-34 do not consume 35).
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** L12 threads T8/T9 (process kinetics, reaction-graph neural ODE) inside the representation programme.
- **NEW:** T8/T9 homed in Steps 29-34 (kinetics, hybrid, rollout); Step 35 only consumes promoted, validated transition outputs in 35f.
- **WHY:** Duplication of Steps 29-34; same data (time-resolved compound series) and gates (G8/G9 ~ G15-4/HYB).
- **SOURCE / EVIDENCE:** SSOT L10905-10960, L10987; ssot_l12 notes §8/§9 C1; §216.10
- **IMPACT:** Removes duplicate work; 35f becomes a consumer, not a producer of kinetics.
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** SSOT gates G3/G4/G7 defined on GS-LF/Keller/ingredient sensory labels; Gates A-E and §183.B 1-10 without thresholds.
- **NEW:** Gates re-scoped to available tasks and pre-registered: G35-PRE, G35-0 (=G0+G13-0), G35-COV, G35-CIRC, G35-SEP, G35-NULL (=G13E-06), G35-PROC (=§246.8/G16-FT), promotion rule (lower CI of gain > delta on >=2 task families x 2 split types); sensory clauses recorded DATA-BLOCKED, not waived.
- **WHY:** Sensory labels absent and marked out of scope; unthresholded gates invite post-hoc weakening.
- **SOURCE / EVIDENCE:** SSOT L10796-10900, L12451-12468, L13146-13157; RESOURCE_GAP_MAP L19; brief §3
- **IMPACT:** Gates become evaluable; any later acquisition of licensed sensory labels re-activates G3/G4/G7 unchanged.
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** Similarity registry SIM-01..21 (definitions only; no null/eval/split/domain/licence fields).
- **NEW:** registry/similarity_registry_v2.csv: nine notions (STRUCTURAL, CHEMICAL, COMPOSITIONAL, SENSORY, FUNCTIONAL, NUTRITIONAL, CULTURAL, PROCEDURAL, PROCESS-CONDITIONED) mapped onto SIM-01..21 with null_model, eval_set, split_family, valid_domain, evidence_class_required, licence_scope, status; CHEMICAL (ingredient->compound) separated from COMPOSITIONAL (recipe->ingredient); SIM-14 learned similarity registered under a notion with its training objective; no fused scalar.
- **WHY:** Brief §24 nine notions; §246.2 no universal scalar; MP B14 'each has its own metric, evaluation set and null model' but no field design.
- **SOURCE / EVIDENCE:** registry/ssot15_similarity_registry.csv; SSOT L26721-26724, L13410; MP L485-495
- **IMPACT:** Schema owned by Step 04 (look-ahead); Step 36 may only expose notions with status BASELINE/PROMOTED.
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** Ingredient ladder includes concentration- and OAV-weighted pooling as early rungs.
- **NEW:** Tiered x_ij (PRESENCE / MEASURED_CONC / THRESHOLD / OAV_DERIVED with matrix, basis, study, source_family, licence_scope); OAV-weighted and ingredient-sensory rungs marked NEED_DATA; UNKNOWN never imputed.
- **WHY:** Repo: 31,334 presence edges, 219 polyphenol concentrations, 0 thresholds.
- **SOURCE / EVIDENCE:** ledgers/data/IMAP.jsonl (verified); SSOT L11654-11679, L11451-11463
- **IMPACT:** Prevents invented values; routes OAV need to Steps 12/14 acquisition.
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 35
- **OLD:** Recipe ladder rung R2 ambiguous (IDF-weighted pooling of z_i vs explicit IDF vector); Phase 0 requires Level-12 z_i.
- **NEW:** R2 split into R2-explicit (z_i-free TF-IDF incidence, Phase 0) and R2-pooled (needs z_i); explicit L13 baselines (R0, R2-explicit, C0-C2, motifs, audits) run without L12 z_i.
- **WHY:** Explicit baselines do not need z_i; L12 is 0/12 complete.
- **SOURCE / EVIDENCE:** SSOT L13782, L14738, L15106; ssot_l13 notes §9 #5-6
- **IMPACT:** Unblocks L13 explicit work; SSOT change request.
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** Recipe splits by duplicate_group_id / provisional families.
- **NEW:** All recipe/cuisine evaluation uses recall-oriented recipe_split_groups_v1 from 07I-C (or conservative fallback grouping); mandatory kNN memorisation baseline and RQ16-13 leakage-inflation comparison; cross-split groups must be 0.
- **WHY:** duplicate_group_id is exact-only; families are precision-oriented (6,589 strict edges); SSOT §191.3 requires near-duplicates in one split group.
- **SOURCE / EVIDENCE:** SSOT L14782-14785, L34857; reports/step07i/preregistration_v1.md; Allamanis 2019; Lee et al. ACL 2022
- **IMPACT:** Hard dependency 07I-C -> 35c/35d; avoids leakage-inflated recipe metrics.
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** L13E has no spine home.
- **NEW:** Optional CPU lane 35-E (E13E-01 rank-frequency Clauset protocol, E13E-04 null lattice + Curveball, E13E-02 Kinouchi reproduction from publication parameters, E13E-03 only if licensed); E13E-05 identity calibration moved to 07I-C; E13E-17/18 as deferred Step 36 sub-experiments; kill switch RQ13E-01.
- **WHY:** SSOT: parallel, non-blocking; identity calibration is a hidden prerequisite of all recipe splits.
- **SOURCE / EVIDENCE:** SSOT L42927, L45449, L45589, L44496; MP L244, L497-501, L2941-2953; r_l13e_identity
- **IMPACT:** No new top-level step (brief §4 A-D not met).
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** Learned recipe/cuisine encoders implicitly trainable on full 612k corpus.
- **NEW:** Learned models trained only on training_allowed=YES rows (73,778 Gutenberg) until H2 licence decisions; explicit statistics on other rows are analysis-only; derived FlavorGraph profiles not redistributed.
- **WHY:** Repo usage registry: 535,151 rows training_allowed UNKNOWN; FlavorGraph DERIVED_ONLY with NC upstream.
- **SOURCE / EVIDENCE:** registry/recipe_source_usage_registry_v1.csv via ssot_l13 §5.2; SRC-000451
- **IMPACT:** Licence-safe; may weaken learned-rung substrate (another reason to DEFER 35g).
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 35
- **OLD:** FlavorTwin consumes 'representations' loosely.
- **NEW:** Step 35 hands off flavortwin_rag_handoff_v1.md listing per notion: status, allowed tasks, forbidden uses, valid domain, licence scope; FlavorTwin baselines extended with LLM zero-shot/RAG and GISMo/LLM-substitution; process-conditioned FlavorTwin claim deferred until 35f PASS + volatile evidence (NEED_DATA).
- **WHY:** §246.8 evaluation boundary; 2024-2026 related work narrows novelty; no volatile before/after evidence in EVD.
- **SOURCE / EVIDENCE:** SSOT L26712-26770, L42736-42742, L45610-45613; r_representation_flavortwin Q8
- **IMPACT:** FlavorTwin novelty claim narrowed to evidence-gated state/process-aware inverse search with typed similarities and non-circular evaluation.
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36
- **OLD:** Step 36 monolithic 'Evidence compiler -> selective RAG -> later FlavorTwin'
- **NEW:** Substeps 36.0 audit / 36A compiler / 36B benchmark+pilots / 36C selective RAG / 36D FlavorTwin; numbering preserved
- **WHY:** Compiler schema and benchmark authoring generate backward requirements and the human long pole; evaluated claims must wait for gates
- **SOURCE / EVIDENCE:** SSOT §241-§246, §257P L42705-42743; research/r_rag_confidence.md §4; brief §4/§12
- **IMPACT:** 36A/36B can start in parallel with 08-20; no new top-level step
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36A
- **OLD:** Cascade variants: SSOT §242.8 (no ASK), MP AI7 (CONFLICT as rung), MP AZ8 (no CONFLICT), brief §28 (ASK before ABSTAIN), repo evidence_class
- **NEW:** Canonical rung enum DIRECT/INTERPOLATE/MODEL/QUALITATIVE/ASK/ABSTAIN; ASK pre-emptive by VOI; conflict_status orthogonal -> REPORT_CONFLICT; crosswalk registry
- **WHY:** Four incompatible lists; CONFLICT is a status, not a support level
- **SOURCE / EVIDENCE:** SSOT L26411-26446, L26481-26491, L22525-22540; MP L3222-3228, L4751; notes/mp_part2.md §9 item 5
- **IMPACT:** Single enum used by packet, policy, benchmark labels and claim templates
- **BREAKING?** YES
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36C
- **OLD:** SSOT §241.1 R5 generic cross-encoder rerank as a pipeline stage
- **NEW:** Generic CE dropped (control only); compatibility classifier on scientific hard negatives as candidate, promoted only on human labels
- **WHY:** Repo negative result: bge-reranker-large dMRR -0.056 [-0.091,-0.017]; topicality != cell compatibility
- **SOURCE / EVIDENCE:** reports/del4/retrieval_silver_v2_analysis.md; SSOT L26825 RQ16-03
- **IMPACT:** Lower compute; retained negative result
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 36A
- **OLD:** Confidence vector q (13 dims) with calibrators 'logistic/Platt/isotonic/small trees'
- **NEW:** 10-domain ordinal certainty profile D1-D10 (no products, UNKNOWN never coerced) + per-decision Platt calibrators (1-6 features); isotonic forbidden below ~1,000 labels; equal-mass + debiased ECE
- **WHY:** Small label budget; GRADE domain template; isotonic overfits small n; binned ECE biased
- **SOURCE / EVIDENCE:** SSOT L26379-26410; Guo 2017; Kumar 2019; scikit-learn calibration docs; GRADE (Guyatt 2008)
- **IMPACT:** Calibratable per decision; profile shown to users
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36A
- **OLD:** Repo EvidencePacket 11 fields; brief §27 15 fields; MP AO1 11 fields
- **NEW:** PKT v2 JSON Schema = §257M header + brief §27 15 sections + condition differences, certainty profile, evidence status, rejected candidates, independence summary, assumptions, applicability, answerability/VOI, RCL pointer, safety, licence flags, retrieval trace, recoverability, what-would-change
- **WHY:** §257M mandatory fields absent; auditability of precision cap, lineage and licence
- **SOURCE / EVIDENCE:** SSOT L42160-42329, L25289-25304; MP L3698-3708; retriever.py L40-50
- **IMPACT:** New schema ledgers/schemas/PKT.schema.json
- **BREAKING?** YES
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36A
- **OLD:** Direction-only conflict detector (INCREASE vs DECREASE)
- **NEW:** §241.5 8-step harmonise-first clustering with status {NONE, EXPLAINED_BY_CONDITION, GENUINE, UNRESOLVED} and trace; no LLM vote
- **WHY:** Most apparent conflicts are basis/condition/lineage artefacts
- **SOURCE / EVIDENCE:** SSOT L26353-26367, L42208-42218; Xu et al. EMNLP 2024; MP W12 L1915
- **IMPACT:** G16-CONFLICT becomes testable
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 36B
- **OLD:** Benchmark tiers 104/320/440 without claim mapping; benchmark authored at the end
- **NEW:** Locked >=240 minimum for any paired 10 pp claim; 104 descriptive only; 4 partitions incl. calibration; items nested in SPLIT_GROUP/evidence cells; sealed with access log; protocol and P1/P2 pilots start in parallel with 08-20
- **WHY:** McNemar 10 pp needs ~155-233 items; CP bound n=104 ~10.9%; human labels are the long pole
- **SOURCE / EVIDENCE:** MP AH5 L2834-2850, AH13 L2961; SSOT L28336; research/r_eval_splits.md Q8
- **IMPACT:** Earlier human scheduling; honest claim sizes
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36C
- **OLD:** C9 transition fallback 'when available'
- **NEW:** MODEL rung only for (target, domain) in registry/rag/l15_fallback_whitelist_v1.csv from the G15 §216.13 decision record, or simulator IN_VALIDATION_DOMAIN; empty today so B6 == B5 (reported)
- **WHY:** G16-TRANS; DEL-2 cold-split negative (persistence wins)
- **SOURCE / EVIDENCE:** SSOT L27470-27471, L22376-22427, L23034-23049; reports/del2/*
- **IMPACT:** No transition overreach
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 36D
- **OLD:** 'later FlavorTwin' unspecified; inverse design without spine home
- **NEW:** 36D.1 static after Step 35; 36D.2 process-conditioned NEED_DATA; 36D.3 inverse design housed here (I0 COMPARE in 36C; I1+ G15-INV gated); 36D.4 cultural prior DEFER
- **WHY:** SSOT §246.1 boundary; no volatiles; novelty narrowed by 2024-26 work
- **SOURCE / EVIDENCE:** SSOT L26712-26782, L22393, L22416-22426; notes/ssot_l15b.md §9 item 10; research/r_representation_flavortwin.md Q8
- **IMPACT:** Scope contained; no unsupported FlavorTwin claims
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36C
- **OLD:** Historical-context RAG (E13E-18) unplaced
- **NEW:** 36C.9 / 36-H DEFERRED until G13E-01/02 pass
- **WHY:** Food.com years are upload years; Gutenberg era is author-birth proxy
- **SOURCE / EVIDENCE:** research/r_l13e_identity.md; SSOT §279.6 L45591-45614
- **IMPACT:** Off critical path
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** no

## Step 36.0
- **OLD:** MP AI9 B-ladder (calibrated abstention in B5; B7 = decision/VOI); DEL-5 B5T/B5F labels
- **NEW:** SSOT §245.12 B0-B7 canonical; B5T/B5F are generator variants within B5
- **WHY:** Semantic drift between plan and SSOT
- **SOURCE / EVIDENCE:** SSOT L26667-26679; MP L3289-3296; notes/mp_part2.md §2.4
- **IMPACT:** Comparable ladder results
- **BREAKING?** no
- **REQUIRES HUMAN APPROVAL?** YES

## Step 36A
- **OLD:** Research-claim ledger CLM reused for runtime response claims
- **NEW:** New runtime response-claim ledger RCL- (claim_route, evidence ids, allowed precision, disallowed checks)
- **WHY:** Semantic collision between research CLM and SSOT §238 runtime ClaimLedger
- **SOURCE / EVIDENCE:** notes/ssot_l16.md §9 item 8; SSOT L26054-26064; MP AO3 L3736-3745
- **IMPACT:** New schema ledgers/schemas/RCL.schema.json; ID scheme change
- **BREAKING?** YES
- **REQUIRES HUMAN APPROVAL?** YES
