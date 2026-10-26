# READER ssot_l16 — SSOT Level 16 §§230–257 (L25082–L27868)

Source: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (SSOT). All "L#####" are SSOT line numbers unless prefixed "plan L" (= `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md`). Read in full: §230 (L25082–25175) through §257 (L27846–27868). Spot-read §257P (L42705–42743) only because it holds the L16 scale/claim checklist that §§249/252 depend on. The annexes §257A–§257O (L27869–42704) are OUTSIDE this assignment and were NOT read. Several things in §§230–257 point into them (numeric thresholds, field semantics, RQ protocols); those are marked "→ annex, UNVERIFIED here".
The 36-step plan ("Master Execution Plan v1") is NOT available. Section 8 maps SSOT content onto the spine **titles** in brief §9 only. Nothing below is quoted from step cards.

Repo cross-checks were read-only: `ledgers/schemas/*.schema.json`, `registry/provenance_class_registry_v1.csv`, `registry/value_origin_registry_v1.csv`, `registry/recipe_quality_tier_registry_v1.csv`, `registry/recipe_source_usage_registry_v1.csv`, `DECISIONS.md` D-016/D-017, `reports/gold/foodcom_ai_assisted_human_review.md`, `reports/step07/step07hr_freeze_manifest.json`, and master plan blocks B07–B11/B16/B17 (plan L370–530).

---

## 0. One-paragraph orientation

L16 is the "system and data" level. It defines no new science. It turns L12–L15 into: (a) a recipe-semantic data factory (vocabulary, CQPO quantities, event-sourced state graphs, Gold/Silver tiers, LLM annotation contract, validators); (b) a runtime CulinaryState-RAG (18 modules C1–C18, multi-stage retrieval, compatibility vectors, conflict and lineage handling, a confidence vector, a sufficiency/abstention cascade, a decision policy with feasibility, VOI, diagnosis and recovery); (c) an evaluation and governance shell (12 benchmark families, baseline ladder B0–B7, 30 RQs, 12 experiment families E16-A…L, 14 G16 gates, stop rules, licensing, reproducibility). Status line L25086–25092 says: spec COMPLETE; data construction, implementation and empirical validation OPEN; FlavorTwin V2 frozen at its current boundary; L17 multimodal optional.

---

## 1. Definitions, entities and data contracts

### 1.1 System identity and invariants (§230)
- Architecture chain (L25096–25112): Molecule → Ingredient → Recipe → Cuisine → State → Transition → Evidence-aware decision / inverse search.
- CulinaryState-RAG = State + Evidence + Transition + Constraints + Uncertainty + Decision (L25116–25121).
- FlavorTwin V2 = Target + Candidate Retrieval + Process Conditioning + Constraints + Evidence/OOD + Inverse Search (L25125–25130).
- Problem statement, 8 capabilities (L25134–25143): normalize; reconstruct state over time; retrieve proof-bearing evidence matched on state/process/conditions; separate observed / external / deterministic / estimated / imputed / simulated / unknown; predict effects only within the L14–15 evidence regime; decide answer/compare/ask/diagnose/recover/recommend/abstain; generate from a structured packet with claim-level provenance; reuse the core for FlavorTwin.
- **24 permanent L16 invariants (L25147–25170).** The ones that bind the plan most:
  - #1 the LLM is interface/proposer/annotator, not the world model;
  - #2 the schema controls the annotator;
  - #3 raw sources are immutable;
  - #4 UNKNOWN is first-class;
  - #5 the provenance classes stay distinct forever;
  - #6 recipe labels ≠ chemistry truth;
  - #7 unit conversion ≠ ingredient-specific grounding;
  - #8 canonical food ≠ alias/form/state/variety/size/brand;
  - #9 canonical process ≠ surface phrase/modifier;
  - #10 direct evidence outranks model completion;
  - #11 semantic similarity ≠ experimental compatibility;
  - #12 every claim traces to a span/evidence atom/model output;
  - #13 confidence is a vector first;
  - #14 calibration needs held-out, independently verified gold;
  - #15 synthetic/imputed data never enter the final test/calibration sets;
  - #16 Gold must not be produced by showing the model answer first;
  - #17 near-duplicates/source families stay in one split;
  - #18 state-based stop criteria are preferred;
  - #19 recommendation is multi-objective;
  - #20 flavour/chemical similarity ≠ sensory equivalence;
  - #21 corpus size doesn't fix provenance;
  - #22 coverage/correctness outrank numeric targets ("exactly 10,000 vocabulary items");
  - #23 complexity is promoted by held-out evidence;
  - #24 L17 optional.

### 1.2 Module registry C1–C18 (§231.2, L25198–25217)
Each row gives inputs → outputs, a permanent rule and a headline metric:
- **C1** query/intent parser: multi-intent, raw query preserved; metrics intent F1 and OOD intent rate.
- **C2** entity/coreference resolver: "do not force unresolved pronouns"; metrics entity F1 and unresolved calibration.
- **C3** state reconstructor: timestamped belief fields with explicit-vs-inferred provenance; metrics field accuracy, calibration, contradiction recovery.
- **C4** process-history tracker: H_t + event DAG; "event order immutable except adjudication"; metrics event order and edge F1.
- **C5** goal/constraint parser: "do not invent priorities".
- **C6** multi-index retriever (hybrid lexical/dense/structured/graph): Recall@K and condition-compatible Recall@K.
- **C7** evidence compatibility layer: match vector over food/process/state/condition/target; **"unknown condition != mismatch"** (L25206); evaluated on human support labels and calibration.
- **C8** direct transition lookup: "retrieve before predict"; direct-evidence precision.
- **C9** transition fallback: "only models that passed relevant G15 gates"; OOD/cold metrics, interval coverage.
- **C10** candidate action generator: "LLM may propose; verifier decides"; candidate Recall@K.
- **C11** feasibility/prerequisite filter: hard constraints before utility; violation rate.
- **C12** outcome comparator: multi-objective outputs.
- **C13** relevance gate: "relevance is not causality".
- **C14** uncertainty/OOD gate: ALLOW / WARN / QUALITATIVE / ABSTAIN; risk–coverage.
- **C15** multi-objective selector: Pareto set, "no arbitrary global utility".
- **C16** grounded response generator: "verbalize; do not invent second analysis".
- **C17** citation/provenance layer: claim ledger; citation precision/recall.
- **C18** session-state updater: "direct current observation overrides old prediction on observable fields"; state replay consistency.

Separation of responsibilities (§231.3, L25221–25226). LLM: parse, propose links, extract events, propose actions, assist literature extraction, verbalize. Deterministic code: IDs, schema validation, arithmetic, unit conversion, fractions, graph integrity, hashes, duplicate grouping, statistics, split assignment. Ontologies: canonical semantics and conversions. Scientific evidence engine. L15 transition service, only after gates. Humans: Deep Gold, adjudication, ambiguous vocab, hard quantity mappings, scientific evidence verification, failure/recovery gold.

### 1.3 Semantic engine / evidence compiler (§232)
- Central object: typed, provenance-bearing semantic atoms. A RAG chunk is only one retrieval artifact. Flow (L25235–25245): Raw Source → Semantic Parse → Typed Objects → Evidence/State Graph → Query-specific Packet.
- **Evidence atom** E_k = (subject, relation, object, conditions, measurement, provenance) (L25251). It must answer: what was measured or asserted; which food/matrix/state; which process/conditions; which method; what fidelity/precision; which document/table/row/span; and which provenance class (L25256–25262).
- **Evidence planes** D^recipe, D^scientific, D^estimated, D^simulated (L25268–25272). They join by canonical ID but are "not interchangeable".
- **Query views** q_text, q_struct, q_graph, q_chem, q_state (L25279). The planner picks views by intent. Quantity queries may bypass dense RAG entirely (L25282).
- **Semantic evidence packet**, 15 sections (L25289–25304): QUERY; CURRENT STATE; HISTORY; GOAL; CONSTRAINTS; DIRECT FACTS; DIRECT EXPERIMENTAL EVIDENCE; NEAR / INTERPOLATION EVIDENCE; MECHANISTIC BACKGROUND; MODEL ESTIMATES; CONFLICTING EVIDENCE; KNOWN UNKNOWNS; FEASIBLE ACTIONS / HYPOTHESES; DISALLOWED CLAIMS; CITATION MAP. These match brief §27 exactly.
- **Lineage** (L25309): "Five webpages repeating the same underlying paper are one independent measurement lineage". Deduplicate derived copies before agreement analysis.
- **Unknown/conflict semantics** (L25313–25316): UNKNOWN ≠ NO EFFECT; NOT MEASURED ≠ NON-DETECT; CONFLICTING ≠ low confidence. A conflict is declared only after checking units, target definition, food/matrix, process, conditions, platform and source independence.
- Context reconstruction is not summarization (L25320). Compression must not erase conditions, units, caveats or conflict structure.

### 1.4 State, memory, event sourcing (§233)
- State graph G_t = (V_t, E_t, P_t) (L25327). Nodes are ingredients, intermediates, tools, actions, observations and state snapshots. Edges are transformation, part-of, location, merge/split, reserve/discard/recombine and provenance (L25331).
- **State field as belief** (L25338–25345): field; value or interval; unit; source/provenance class; timestamp; evidence/model reference; uncertainty/unknown flag. An observation overrides an older prediction for the same observable field, and the old prediction stays in the audit trail (L25347).
- Event sourcing (L25351–25358): no destructive overwrite; current state is derived from ordered events. Gains: replay, correction, causal inspection, provenance, merge/split accounting, session continuation.
- Intermediate entities are mandatory when multiple inputs create a meaningful downstream entity. Preserve parentage and allocations (L25362).
- **Relation enum** (L25369–25378): MERGES_INTO, SPLITS_INTO, RESERVED_AS, DISCARDED_FROM, RECOMBINED_WITH, TRANSFORMS_INTO, TRANSFERRED_TO, PART_OF, LOCATED_IN, OBSERVED_AS.
- Quantity propagation (L25383): propagate distributions/intervals through explicit fractions; no false precision.
- **Five memory classes** (L25387–25391): Source, Semantic, Episode/session, Evidence, Model. Model memory holds predictions, imputations AND simulations. Boxed law Model Memory ≠ Evidence Memory (L25396).

### 1.5 Vocabulary/ontology (§234)
- 19 vocabulary families (L25407–25425): V_FOOD, V_FOOD_ALIAS, V_VARIETY, V_FORM, V_STATE, V_PROCESS, V_PROCESS_ALIAS, V_TOOL, V_QUANTITY_UNIT, V_PORTION, V_SIZE, V_CONTAINER, V_PACKING, V_ROLE, V_CONDITION, V_SENSORY, V_FAILURE, V_RECOVERY, V_CHEMICAL.
- Canonical concept ≠ surface string. Worked example L25435–25441: "2 large ripe tomatoes, roughly chopped" → food = tomato, quantity = 2 count, size = large, state = ripe, form = roughly_chopped.
- "10,000+ canonical ingredient concepts" is a target scale, not a quota (L25445). Coverage(K) = mapped mentions / all mentions (L25450). Aim for a declared target "such as 98–99%" with separate long-tail/regional reporting (L25453).
- Aliases: tens of thousands expected. Keep language, locale, source frequency and alias type (L25457).
- Processes: keep compact and compositional with modifiers (granularity, intensity, geometry, endpoint). Do NOT force 10,000 canonical processes (L25461).
- External alignment: internal IDs are authoritative. FoodOn/FDC are alignments, not identities. Keep unmapped internal concepts (L25465).
- **Proposal states** (L25470–25478): EXISTING_ALIAS, EXISTING_CONCEPT_WITH_MODIFIERS, TRUE_NEW_CONCEPT, AMBIGUOUS, POLYSEMOUS, COMPOUND_FOOD, BRAND, NON_FOOD, NEEDS_HUMAN_REVIEW.
- Growth-control checklist for new concepts (L25485–25493): exact aliases, spelling, singular/plural, regional names, parent category, form/state modifiers, brand/product, compound food, multilingual transliteration.
- Long-tail policy (L25497): don't drop rare ingredients. Reserve review budget for traditional/regional foods, fermentation starters, spices/herbs, local grains and seafood.

### 1.6 CQPO (§235)
- Three separate problems that must never be collapsed (L25506–25510): (1) deterministic physical conversion; (2) locale-aware volume-to-volume culinary conversion; (3) ingredient/form/packing/locale-specific volume/count → mass grounding.
- q = (value, range, unit, size, packing, form, ingredient, locale, qualifiers) (L25515). Qualifiers: approximately, heaped, level, packed, loosely packed, divided, reserved, optional, to taste, enough-to-cover (L25518).
- **Portion evidence ladder** (L25523–25529): Q0 EXACT_PHYSICAL, Q1 AUTHORITATIVE_PORTION, Q2 AUTHORITATIVE_DENSITY, Q3 MULTISOURCE_ESTIMATE, Q4 RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION, Q5 MODEL_ESTIMATE, Q6 UNKNOWN.
- Count units (egg, clove, fillet, bunch, slice, head) are ingredient-specific distributions conditional on size/form/locale (L25534).
- Qualitative quantities (to taste, pinch, dash, handful, splash, as needed, enough to cover) stay qualitative. "Do not generate grams by common sense" (L25538).
- Store raw_value, raw_unit, normalized_value, normalized_unit, conversion_method, conversion_source, conversion_uncertainty (L25545–25551).
- Quantity encoder z_q = [log(1+m_g), log(1+v_mL), log(1+count), z_unit, z_size, z_packing, z_form, z_locale, mask, uncertainty] (L25561). Ingredient-in-recipe h_{i,R} = [z_i; z_q; z_state; z_role; z_position] (L25567). Missing values are masked, never zero (L25570).
- Empirical P(mass | ingredient, size, state, form, locale). Report median, mean, quantiles, source count and source diversity. Outliers go to review, not silent clipping (L25577–25580).
- Validation (L25584): dimensional consistency, impossible unit–food pairs, outliers, contradictory count+mass, locale ambiguity, arithmetic. "Validators flag; they do not silently rewrite."

### 1.7 Data tiers (§236.1, L25591–25597)
| Tier | Scale | Use |
|---|---|---|
| Deep Gold | ~750–1,000 real recipes, independent dual annotation + adjudication | final evaluation, calibration, hardest cases |
| Gold-Light | ~3,000–5,000, targeted human verification | parser/linker tuning, active learning, quantity/state QA |
| Silver | 60,000–100,000, LLM/SLM + deterministic validators | representation/parser training, vocab statistics, state graphs |
| Large weak corpus | 1M+ "when permitted" | pretraining, alias statistics, long-tail discovery |
| Synthetic/Bronze | as needed | stress tests/augmentation; "never final real test" |

"The target is 100k structured real recipes, not 100k gold recipes" (L25601).

### 1.8 Field dictionary (§238, L25745–26101)
**Caveat.** Every field in §238 has the same boilerplate description: "required to be typed/versioned; nullable only according to the schema; raw provenance preserved where applicable". No types, enums or null semantics are given here. The real per-field semantics are presumably in §257C "FIELD-LEVEL DATA DICTIONARY" (L29336+, → annex, UNVERIFIED here). The subsection numbers (238.15, 238.45, 238.68, 238.89, 238.103, 238.129, 238.151, 238.175, 238.189, 238.211, 238.238, 238.253) are non-sequential and look like generation artifacts. Shared validation notes repeated per entity: IDs stable, never inferred from display text; unknown/null semantics documented per field; every normalized field has a derivation route; versioned migrations, no silent reinterpretation (e.g. L25780–25783).

Field lists, verbatim names:
- **Recipe** (L25751–25776): recipe_id, dataset_version, source_id, source_url, source_domain, license_class, source_checksum, title_raw, title_normalized, language, locale, cuisine_labels, dish_categories, servings_raw, servings_normalized, ingredient_mention_ids, event_ids, entity_ids, recipe_graph_id, duplicate_group_id, annotation_tier, annotation_model, prompt_version, schema_version, validation_status, validation_flags.
- **IngredientMention** (L25789–25807): mention_id, recipe_id, raw_text, source_span, canonical_ingredient_id, candidate_ids, variety, form, state, size, quantity_id, role, optional, divided, reserved, brand, canonicalization_status, provenance, annotation_confidence_features.
- **CanonicalIngredient** (L25820–25836): ingredient_id, preferred_name, food_category, parent_id, scientific_name, foodon_id, fdc_ids, aliases, regional_aliases, languages, known_forms, known_states, portion_profile_ids, chemistry_link_ids, status, version_created, human_verified.
- **Alias** (L25849–25858): alias_id, surface, canonical_ingredient_id, language, locale, alias_type, source_count, source_domains, verification, first_seen_version.
- **Quantity** (L25871–25892): quantity_id, raw_text, quantity_type, value, lower, upper, fraction, count, unit_id, unit_locale, size, packing, container, approximate, qualitative_term, optional, divided, reserved, normalized_mass_g, normalized_volume_ml, conversion_record_id, provenance.
- **PortionProfile** (L25905–25922): portion_profile_id, ingredient_id, state, form, size_class, packing, portion_value, portion_unit, unit_locale, mass_g, mass_low_g, mass_high_g, conversion_class, source_type, source_record, sample_count, source_diversity, verification.
- **Event** (L25935–25954): event_id, recipe_id, event_index, process_id, process_modifiers, input_entity_ids, output_entity_ids, tool_ids, medium, temperature_C, temperature_raw, duration_s, duration_raw, pressure, pH, moisture_condition, endpoint_states, source_span, provenance, validation_flags.
- **Entity** (L25967–25976): entity_id, recipe_id, entity_type, canonical_food_id, name, parent_entity_ids, created_by_event, destroyed_or_consumed_by_event, quantity_state_id, current_state_id.
- **State** (L25989–26006): state_id, entity_id, event_index, timestamp, form, physical_state, visual_state, thermal_state, texture_state, temperature_C, moisture, water_activity, pH, quantity_mass_g, chemical_state_ref, field_provenance, uncertainty, observation_source.
- **EvidenceAtom** (L26019–26041): evidence_id, subject_type, subject_id, relation, object_type, object_id, process_id, conditions, measurement_target, measurement_value, measurement_unit, metric, matrix_description, analytical_method, study_id, source_id, doi, table_or_figure, source_span, evidence_class, verification, independence_group, quality_features.
- **ClaimLedger** (L26054–26064): claim_id, response_id, claim_text, claim_type, evidence_ids, model_id, model_version, confidence_class, citation_required, citation_refs, verification_status.
- **InverseDesignTrial** (L26077–26092): trial_id, initial_state_id, target_state, candidate_ingredient_ids, candidate_process, candidate_conditions, constraints, optimizer, forward_model_version, predicted_state, prediction_interval, evidence_distance, OOD_flag, feasible_flag, heldout_or_real_outcome, target_error.

**Repo comparison (read-only; top-level `properties` of `ledgers/schemas/*.schema.json`).** The repo uses its own ledger names. A mapping table is needed, because no repo file is named as in §244.4.
- REC: content_sha256, cuisine, family_id, raw_location, source_url, title, n_steps, n_ingredient_lines, and provenance.method ∈ {MANUAL, IMPORT, RULE, LLM, MODEL, DERIVED, SCRAPE}. **No top-level** license_class, language, locale, dish_categories, servings_raw/normalized, duplicate_group_id (family_id instead), annotation_tier/model, prompt_version, validation_flags. These may live in `ledgers/recipe_base/recipe_base_v1.parquet` columns. UNVERIFIED: no pyarrow on this server.
- EVT: condition_id (indirection to COND), endpoint, omitted_step_candidate, trajectory, input_state_ids/output_state_ids (state-based, not entity-based), tool_ids, span. No inline medium/temperature/duration/pH; these are presumably in COND.
- ENTITY: ingredient_id, kind, label, ordinal. No parent_entity_ids, created_by_event or destroyed_or_consumed_by_event. Lineage is probably in GRAPH.edges / ALLOC (UNVERIFIED).
- STATE: belief ∈ {PREDICTED, OBSERVED, PLANNED}; variables{status ∈ MEASURED/RANGE/QUALITATIVE/CENSORED/UNKNOWN/NOT_APPLICABLE, value, low, high…}; overrides_state_id; previous_state_id; produced_by_event_id. This is consistent with §233.2/§233.3 and in places richer (CENSORED, PLANNED).
- QNT: q_level enum Q0–Q6, which matches §235.3. Also parsed.kind ∈ {NUMBER, RANGE, FRACTION, MIXED, MULTIPLIER, PACKAGE, QUALITATIVE, NONE}, conversion_method, conversion_path, locale, mass_g, volume_ml, portion_id, raw.
- POR: basis ∈ {MEASURED, DATABASE, CONVENTION, RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION}, grams_per_unit, density_g_per_ml, form, packing, locale. **No** mass_low/high, sample_count, source_diversity or size_class, which §235.8 and §238.129 require for distributions.
- EVD (EVD.schema.json): independence_group, conflict_cluster, censored, n_replicates, measurement_method_id, tier E1–E7, study_ids, study_id_status, source_family_id, applicability, matrix{ingredient_id, raw_name, food_group, variety, part…}, target{state_variable_id, molecule_id, reaction_id…}, process{process_id, family, tool_ids…}. No top-level doi / table_or_figure / source_span / quality_features (may be in external_refs; UNVERIFIED).
- CLM: statement, claim_type, evidence_ids, experiment_ids, gate_ids, approval. This is a research-claim ledger, not the runtime per-response ClaimLedger of §238.238 (no response_id, model_id, citation_refs or confidence_class).
- GRAPH: edges, event_ids, replay_sha256, session_id. SPLIT: assignment_sha256, strategy, seed, leakage_report_path.
- No InverseDesignTrial schema. That is acceptable until Step 36 / FlavorTwin.

### 1.9 Provenance enum (§239.1 L26117–26125)
EXPLICIT_SOURCE, EXTERNAL_VERIFIED, DERIVED_DETERMINISTIC, INFERRED_LLM, MODEL_ESTIMATED, IMPUTED, SIMULATED, UNKNOWN. Rule 4 (L26126): never promote INFERRED_LLM/MODEL_ESTIMATED/IMPUTED/SIMULATED to observed/gold.
- Repo `registry/provenance_class_registry_v1.csv` has the identical 8 classes and adds tier and eval-use columns (EXPLICIT_SOURCE E1–E4; INFERRED_LLM "only after human verification"; SIMULATED E7 "no").
- Repo UNKNOWN is defined as "origin not recorded … legacy rows". That is a *provenance-unknown* meaning, whereas §239.1 rule 2 uses UNKNOWN as *value-unknown*. See §9.

### 1.10 Other enums
- Sufficiency modes (§242.6 L26413–26421): DIRECT/FULL SUPPORT; NEAR/PARTIAL SUPPORT; MODEL-SUPPORTED INTERPOLATION; BROAD QUALITATIVE SUPPORT; IRRELEVANT EVIDENCE; NO EVIDENCE; CONFLICTING EVIDENCE.
- Decision modes (§243.1 L26452): ANSWER, COMPARE, ASK, DIAGNOSE, RECOVER, RECOMMEND, ABSTAIN. Information actions: ASK, OBSERVE, MEASURE (L26483).
- Recoverability (L26479): REVERSIBLE, PARTIALLY_REVERSIBLE, CONTAINABLE, IRREVERSIBLE, UNKNOWN.
- QA reviewer output (L26237): PASS / PASS_WITH_WARNINGS / REANNOTATE / HUMAN_REVIEW.
- Compatibility match types (L26347): EXACT, SAME_SPECIES, SAME_FOOD_GROUP, SAME_PROCESS_FAMILY, GENERIC_MECHANISM.
- FlavorTwin evidence classes (L26758–26764): OBSERVED_MATCH, STRUCTURAL_MATCH, SENSORY_SUPPORTED_MATCH, MODEL_ESTIMATED_MATCH, PROCESS_SIMULATED_MATCH, EXTRAPOLATED, UNSUPPORTED.
- Table evidence: plot-digitized values are labelled **DIGITIZED** with extraction uncertainty (L26374).
- Gate decision outputs of C14: ALLOW / WARN / QUALITATIVE / ABSTAIN (L25213).

### 1.11 Retrieval, confidence and decision definitions
- Retrieval stages R1–R8 (L26325–26332): structured filters → BM25 → dense → graph/evidence expansion → cross-encoder rerank → state/process/condition/target compatibility → dedup + lineage + conflict → packet compile.
- RRF as fusion baseline (L26337).
- Compatibility vector m_j = [m_food, m_state, m_process, m_T, m_t, m_pH, m_target, m_matrix, m_measurement, m_source] (L26344). Keep categorical match types BEFORE learning any scalar (L26347).
- Confidence vector q = [retrieval, entity, quantity, process, condition, target, source, measurement, extraction, agreement, state, model, OOD] (13 dims, L26384).
- Seven separately calibratable probabilities (L26391–26397).
- Output precision policy, boxed: output precision ≤ evidence precision (L26425–26431).
- Decision cascade (L26437–26441): DIRECT → supported interpolation → calibrated L15 estimate → broad qualitative → abstain.
- VOI(x) = U_before − E[U_after observing x], with user burden considered (L26488–26491).
- Receding-horizon loop (L26499–26505).
- "Practical POMDP": state estimate + uncertainty + VOI + short-horizon action, not full POMDP/RL (L26511).
- Candidate record (L26467): action/conditions/stop criterion, predicted outcome, evidence route, evidence class, uncertainty, OOD/support distance, feasibility, goal-match vector.
- FlavorTwin target factorization Z* = {chemical, sensory, functional, process, culinary} (L26721). candidate = ingredient + state + process + conditions (L26742). Contextual substitution score(i→j | recipe, role, process, quantity) (L26750).

---

## 2. Models and baseline ladders

### 2.1 System baseline ladder (§245.12, L26669–26678)
- B0 LLM only
- B1 dense RAG
- B2 BM25 + dense hybrid RAG
- B3 structured metadata RAG
- B4 state-aware RAG
- B5 state + evidence compatibility/conflict packet
- B6 + L15 transition fallback (plan L3295: "only if G16-TRANS passed")
- B7 + calibrated recommend/ask/abstain decision layer

Minimum course deliverable is "at least B0–B5" (L27657). B7 sits in the stronger deliverable (L27665).

### 2.2 Global promotion order (§249.3, L27505–27519)
Rules/lookup → strong simple baseline → structured model → learned model → agentic/optimization layer. "No stage is skipped merely because the later stage sounds more novel." The negative-results policy (L27439) says that if simpler parsing, retrieval, LightGBM, direct evidence or static FlavorTwin matches complex approaches, retain the simpler one.

### 2.3 Per-component ladders implied in L16
- **Semantic parsing (E16-A, L27391):** rules → smaller encoders → LLM extraction → distilled parser → hybrid verifier. The master plan reproduces the SOTA from outside L16 (plan L392–396: RecipeDB3 DeBERTa macro-F1 0.9557; TASTEset 0.935/0.943, etc.). Those numbers are plan claims and were not re-verified here. The repo NER/linker block is closed (S128 per ctx).
- **Annotation pipeline:** one-shot mega-prompt (control) vs multi-pass (RQ16-11). LLM alone vs LLM + validators (RQ16-12). Strong LLM, then distilled cheaper specialist for routine extraction (L26258).
- **Vocabulary:** raw normalized strings (control) → canonical concepts + modifiers (RQ16-08).
- **Quantity:** raw text / unit-only (control) → CQPO grounding (RQ16-07). Representation: incidence; grams only; then hybrid z_q encoder (RQ16-23).
- **Recipe graph:** text/set baseline → explicit graph model (RQ16-24).
- **Retrieval:** dense → BM25+dense (RRF) → + structured filters → + graph expansion → + cross-encoder → + structured compatibility (RQ16-02, RQ16-03). Generic cross-encoder is the control for the compatibility reranker.
- **Context:** raw top-k chunks → role-structured packet (RQ16-04).
- **Confidence:** LLM verbal/self score (control) → logistic/Platt/isotonic/small calibrated trees on the confidence vector (L26405, RQ16-05). "A huge opaque confidence model is not automatically better."
- **Sufficiency:** always-answer RAG → selective cascade (RQ16-06).
- **State memory:** chat transcript only → structured event-sourced state graph (RQ16-14). Prediction-retaining → field-level observation override (RQ16-15).
- **Decision:** RAG/LLM action list → structured feasibility filter (RQ16-16). NeverAsk / AskEverything → VOIAsk (L26661, RQ16-17).
- **Diagnosis/recovery:** generic LLM troubleshooting → proposer + verifier (RQ16-18). Cause→inverse heuristic → separate recovery index (RQ16-19).
- **Transition integration:** retrieval-only → retrieval + gated L15 fallback (RQ16-20, E16-J).
- **Conflict:** majority / first-hit → condition-aware conflict resolver (RQ16-22).
- **FlavorTwin (L26777):** random / category / ECFP / descriptors / static embeddings / static multiview → process-conditioned → process + recipe-context. Static baselines are mandatory (L26745, L27641).
- **Storage (L26537–26540):** relational first. Vector index for passages/atoms. Lexical index for exact terms. A graph DB is optional; adjacency tables come first.

---

## 3. Experiments / hypotheses / RQs

### 3.1 30 RQs (§247, L26783–27385)
Uniform card fields: question, data required, baseline/control, proposed method, headline split, metrics, promotion criterion, main risk, decision use. Every card has the same decision-use clause: "a positive, null or negative result is retained … not repeated until the desired architecture wins" (e.g. L26803). Compact table:

| RQ (line) | Hypothesis core | Data | Control | Split | Metrics | Promotion |
|---|---|---|---|---|---|---|
| 01 (L26785) | state reconstruction helps retrieval and next action | Deep Gold state/action + evidence benchmark | B2/B3 no state | source/duplicate-disjoint | ConditionCompatible@K, ModeF1, UCR | "only if improvement persists beyond bootstrap CI" |
| 02 (L26805) | structured retrieval improves citation correctness | Deep Gold evidence queries | dense RAG | source-disjoint | Recall@K, citation precision, UCR | "improve support without excessive recall loss" |
| 03 (L26825) | condition-aware compatibility beats generic cross-encoder on hard negatives | human-labelled query/evidence pairs | generic CE | food/process/source cold | support AUROC/F1, compatible R@K | gain on hard negatives |
| 04 (L26845) | packet reduces unsupported claims vs raw chunks | same retrieval, two formats | raw chunks | same test queries | UCR, citation precision, conflict handling | packet improves grounding |
| 05 (L26865) | confidence vector beats LLM self-confidence | Deep Gold calib/test | LLM verbal score | held-out calib/test | Brier, ECE, error AUROC, risk–coverage | better calibration |
| 06 (L26885) | DIRECT→INTERPOLATED→MODEL→QUALITATIVE→ABSTAIN cascade | queries stratified by support regime | always-answer | support-regime held-out | risk–coverage, UCR, quant error | lower risk at useful coverage |
| 07 (L26905) | CQPO grounding helps representation/state accounting | Deep Gold quantity + downstream | raw/unit-only | ingredient/source cold | mass error/coverage + downstream | "improve both grounding and at least one downstream task" |
| 08 (L26925) | canonicalization reduces OOD alias errors/fragmentation | 100k aliases + Deep Gold links | raw strings | source/locale cold | link acc, fragmentation, recipe-model gain | higher cold-link acc / fewer duplicate concepts |
| 09 (L26945) | Silver utility at 10k/25k/60k/100k | incremental Silver + fixed Gold test | Gold only | fixed source-disjoint gold test | macro F1, calibration | "identify saturation curve" |
| 10 (L26965) | active learning beats random per label | pool + budget | random | same budget | F1/coverage per label | higher gain per label |
| 11 (L26985) | multi-pass beats one-shot | Deep Gold | one-shot | matched model/budget | field F1, graph F1, provenance violations | higher quality/reliability |
| 12 (L27005) | deterministic validators reduce critical errors | Silver pilot + Gold error labels | LLM alone | source-disjoint | critical error rate, review precision | "large reduction" |
| 13 (L27025) | duplicate leakage inflation | 100k duplicate groups | random split | comparison | inflation delta | quantify |
| 14 (L27045) | event-sourced session memory beats chat history | simulated/real multi-turn sessions | transcript | session-level | state/action consistency, contradiction recovery | clear gain |
| 15 (L27065) | observation override reduces compounding errors | sessions with corrective obs | prediction-retaining | held-out sessions | state error vs horizon | reduced error |
| 16 (L27085) | feasibility filter | decision gold valid/invalid | RAG/LLM list | scenario | violation rate, action R@K | violations down, recall acceptable |
| 17 (L27105) | VOI questions | ambiguous scenarios | never/ask-all | scenario | quality vs #/cost questions | Pareto improvement |
| 18 (L27125) | diagnosis proposer→verifier | failure/recovery gold | LLM | failure/source | HypothesisRecall@K, evidence precision | higher supported diagnosis |
| 19 (L27145) | separate recovery evidence | failure + recovery labels | cause→inverse | failure-type | recovery validity, unsupported rate | safer recovery |
| 20 (L27165) | L15 fallback adds coverage without raising UCR | no-direct-but-in-support queries | retrieval-only | cold pair/study | coverage, error, UCR, calibration | useful coverage gain |
| 21 (L27185) | exposing imputed/model evidence class | completion queries + user/system eval | unlabelled completion | same queries | trust calibration/UCR/mode | lower overclaiming |
| 22 (L27205) | condition-aware conflict clustering | curated conflict cases | majority/first | source-disjoint | conflict resolution F1 | better recognition |
| 23 (L27225) | learned z_q beyond incidence and grams | L13 quantity-rich subset | incidence; grams | recipe/source cold | held-out task | incremental gain |
| 24 (L27245) | explicit graphs beat flat encoders for next step/state | Gold/Silver sequences | text/set | source/process cold | step F1, state acc | measurable value |
| 25 (L27265) | process-conditioned FlavorTwin beats static | held-out processed targets | ECFP/descriptors/static emb | ingredient/process cold | Recall@K/profile error/OOD | gain with acceptable support |
| 26 (L27285) | recipe-context reranker reduces implausible substitutions | substitution benchmark | global sim | recipe/source cold | NDCG, violations | better contextual ranking |
| 27 (L27305) | chemical/descriptor vs human similarity | small sensory study "if feasible" | chemical sim | participant/target holdout | correlation/ranking/agreement | quantify ceiling |
| 28 (L27325) | source/domain shift degradation | source-disjoint benchmark | random-split estimate | unseen domains | per-module deltas | quantify |
| 29 (L27345) | long-tail sampling helps rare linking | balanced long-tail gold | frequency-only | rare vs common | macro/link acc by frequency | long-tail gain |
| 30 (L27365) | full B7 beats B0–B5 and ablations explain it | complete L16 benchmark | B0–B5 | **locked final test** | ModeF1, UCR, citation precision, feasibility, risk–coverage | headline + ablations |

**Note.** Nearly every RQ promotion criterion is qualitative ("large reduction", "useful coverage gain", "acceptable recall"). Only RQ16-01 names a statistical rule (bootstrap CI). The pre-registered numeric versions are presumably in §257E/§257L (→ annex, UNVERIFIED here).

### 3.2 Experiment families (§248.1, L27390–27425)
- E16-A semantic parsing
- E16-B quantity
- E16-C vocabulary / cold start
- E16-D recipe graph (incl. next-state prediction)
- E16-E evidence retrieval with scientific hard negatives
- E16-F packet / grounded generation
- E16-G confidence / abstention
- E16-H decision policy
- E16-I diagnosis / recovery
- E16-J transition integration
- E16-K FlavorTwin static → process-conditioned
- E16-L full system on locked final test across factual, comparison, state, action, diagnosis, recovery, OOD and conflict scenarios

### 3.3 Benchmark families and metrics (§245)
- 12 families (L26608–26621): SEM, LINK, QTY, GRAPH, RET, EVID, CONF, TRANS, DEC, DIAG, REC, FT.
- Metrics:
  - span P/R/F1 per FOOD, QUANTITY, UNIT, FORM, STATE, TOOL, ACTION, DURATION, TEMPERATURE, macro required (L26625);
  - linking Acc@1, Recall@5, hierarchical accuracy, OOD alias/source (L26629);
  - quantity structure exact match, mass/volume error **only on authoritative ground truth**, interval coverage/width (L26633);
  - graph node/edge/merge-split F1, coreference, event order, replay consistency (L26637);
  - retrieval Recall@K/MRR/NDCG + **condition-compatible Recall@K** (L26641);
  - citation precision/recall, entailment/manual verification, UCR = unsupported factual claims / all factual claims (L26645–26649);
  - sufficiency mode F1 + risk–coverage (L26653);
  - decision Action R@K, violation rate, mode F1, goal-state error, paraphrase/unit consistency (L26657);
  - VOI NeverAsk/AskEverything/VOIAsk (L26661);
  - diagnosis/recovery Hypothesis R@K, useful-next-test rate, recovery validity, recoverability classification (L26665).
- Mandatory one-at-a-time ablations (L26684–26692): state reconstruction; quantity grounding; structured retrieval; evidence compatibility; conflict/lineage; transition fallback; uncertainty/OOD gate; feasibility filtering; provenance/claim ledger. "A module that adds no measurable value should not be retained" (L26694).
- Oracle cascades: oracle vs predicted upstream state/evidence, to localize error propagation (L26698).
- Robustness (L26702–26709): paraphrase; exact unit invariance (C↔F, kg↔g); locale sensitivity (cup); state sensitivity; constraint sensitivity; goal sensitivity; evidence sensitivity; source-disjoint/cold ingredient/process.

### 3.4 Publication units (§248.2, L27430–27433; §253.3–253.6)
1. Semantic corpus + CQPO (dataset paper: "Recipe Semantic State Graph + Culinary Quantity/Portion Ontology", L27669).
2. State- and evidence-aware culinary RAG.
3. Sparse process-state transition modelling (L15).
4. Process-conditioned FlavorTwin, only if it beats static baselines (L27681).

Demo suite of 8 scenarios (L27687–27694).

---

## 4. Gates, promotion and stop rules (exact text, with lines)

### 4.1 G16 core gates (§249.1). None has a numeric threshold in §249.
- **G16-DATA** (L27446–27447): "Deep Gold exists with independent annotation/adjudication; Silver quality and source/duplicate controls documented."
- **G16-VOCAB** (L27449–27450): "High mention coverage is achieved; high-frequency unresolved/ambiguous concepts below declared threshold; concept/alias fragmentation audited." The only numeric hint is §234.3 "such as 98–99%" (L25453). Master plan adds: processes "≥ 95% of process mentions in the Gold seed map to an ID or an explicit UNMAPPED with the raw verb kept" (plan L347), and "ACCEPT-band precision ≥ the pre-registered budget" (plan L426).
- **G16-QTY** (L27452–27453): "Deterministic units correct; food-specific portion conversions have provenance; qualitative/unknown quantities are not fabricated; interval calibration reported where distributional." Master plan SX-10-02 "Invented-grams audit (must be 0)" (plan L441).
- **G16-SEM** (L27455–27456): "Ingredient/action/state/coreference parsers meet declared Deep-Gold thresholds and source-disjoint performance is reported."
- **G16-GRAPH** (L27458–27459): "Recipe graph temporal integrity, intermediate, merge/split and coreference metrics meet declared acceptance criteria."
- **G16-EVID** (L27461–27462): "Evidence retrieval has acceptable compatible Recall@K/citation support and preserves exact provenance."
- **G16-CONFLICT** (L27464–27465): "Conflicting evidence is detected/qualified rather than silently collapsed."
- **G16-CAL** (L27467–27468): "Confidence/abstention calibrated on held-out independent gold; risk–coverage reported."
- **G16-TRANS** (L27470–27471): "No Level-15 fallback is used for a target/domain until the relevant G15 gates pass."
- **G16-DEC** (L27473–27474): "Structured decision system reduces unsupported/infeasible actions relative to strong RAG baselines while maintaining useful coverage."
- **G16-REC** (L27476–27477): "Diagnosis/recovery relations are separately evidenced and recoverability uncertainty is explicit."
- **G16-PROV** (L27479–27480): "Every factual/scientific response claim is traceable to evidence or explicit model output."
- **G16-OOD** (L27482–27483): "Cold ingredient/process/source/condition behavior and abstention are measured."
- **G16-FT** (L27485–27486): "FlavorTwin process/context complexity is promoted only if it beats static baselines on process-sensitive held-out tasks."

### 4.2 Stop rules (§249.2, L27490–27501)
"Stop increasing complexity and invest in data/evidence when":
- Silver does not improve held-out Gold performance;
- canonicalization errors dominate parser errors;
- quantity conversions are mostly unsupported;
- structured retrieval does not beat strong hybrid RAG;
- confidence is uncalibrated under source shift;
- the L15 model adds coverage but materially increases unsupported claims;
- feasibility rules remove too many gold-valid actions;
- diagnosis gold is too ambiguous for strong causal claims;
- process-conditioned FlavorTwin fails to beat static baselines;
- human verification cost exceeds the value of the proposed feature.

### 4.3 Roadmap phase exits (§252)
- Phase 0 exit (L27591): "100–500 difficult recipes can be represented without schema improvisation."
- Phase 1 exit (L27597): "errors are understood and schema/prompt v1 is stable enough for pilot."
- Phase 2 exit (L27603): "high-frequency ingredients/units resolve reliably; conversion provenance works end-to-end."
- Phase 3 (L27607–27609): "Do not scale further until audit." Exit: "validation failure rate, vocab growth, source bias and human-review workload are acceptable/documented."
- Phases 4–12 have no explicit exits. Phase 6 says "Potentially scale to 100k if gates justify it" (L27621). Phase 11 runs "Only after shared state/evidence/transition core is usable" (L27641). Phase 12 runs "Only if … core system is empirically validated" (L27645).

### 4.4 Scale-up stage gates (§236.5 L27626–27636) and batch checkpoints (§236.6 L25641–25653)
- Stage 9 "100k Silver if gates pass".
- Every 5k–10k records, rerun 11 audits: near-dup grouping, new-concept audit, alias merge audit, unmapped high-frequency terms, new quantity terms, mass conversion outliers, graph integrity, source/cuisine/process imbalance, unknown-field distributions, disagreement/review queue, prompt/schema drift.
- Release statistics are listed in §236.7 (L25657).

### 4.5 Large-build and claim checklists (§257P, L42705–42743; spot-read, outside range but referenced by plan L386)
- "Do not authorize 60k–100k production annotation until" 15 boxes are ticked. Among them: provenance enum enforced in code; raw checksum/manifest; ≥100–500 difficult Gold seed cases; unit engine passes property-based tests; QA reviewer flags fabricated chemistry; pilot cost and reannotation rate known; duplicate grouping before split; Deep-Gold annotators independent of Silver; rollback/reprocess strategy.
- Final RAG claims need, among others: compatible retrieval benchmark; UCR measured; calibration on held-out gold; L15 fallback domains whitelisted by gates; "locked test data have not been used for iterative prompt/model tuning".
- Strong FlavorTwin claims need: static baselines; process-conditioned beats static on held-out process-sensitive task; sensory wording backed or avoided.
- Master plan B07 gate: "§257P checklist fully ticked before scaling past 10k" (plan L386).

### 4.6 Definition of Done (§257, L27848–27866)
17 reproducible demonstrations. Items with direct gate meaning:
- #5 "a Deep-Gold benchmark exists independently of Silver predictions";
- #6 "source/duplicate-safe splits are frozen";
- #9 calibration on held-out gold;
- #10 L15 fallback only in validated domains;
- #14 "strong RAG baselines are beaten or the simpler baseline is retained";
- #16 negative results retained;
- #17 rerunnable from dataset/split/code/model/prompt versions.

### 4.7 Validator rules acting as hard gates (§240.2, L26275–26304; 29 rules)
The ones most relevant to the spine:
- "Every EXPLICIT_SOURCE field has a source span" (L26280);
- "No count portion is converted to mass without a food-specific portion record or empirical distribution" (L26284);
- "No chemistry value appears from a recipe-only annotation pass" (L26288);
- "Model-estimated/imputed/simulated fields are excluded from observed-gold target tables" (L26290);
- "Duplicate-group members remain in the same final split" (L26291);
- "LLM-extracted scientific rows entering final evaluation are human verified" (L26293);
- "Source lineage prevents multiple copies of one study from counting as independent evidence" (L26294);
- "Current state can be replayed from event history" (L26296);
- "License/redistribution status is recorded when source text may be released" (L26301);
- "FlavorTwin sensory-equivalence wording is blocked without sensory evidence" (L26304).

---

## 5. Data requirements and named sources (licence notes)

L16 names almost no external datasets. Named in-range:
- **FoodOn** and **FDC** (USDA FoodData Central) as alignment targets only: §234.6 L25465; fields `foodon_id`, `fdc_ids` L25825–25826.
- "Licensed/public recipe corpora" for the 1M+ weak tier "when permitted" (L25596).
- Recipe comments/Q&A as a possible failure/recovery mining source, with PII minimisation (§250.3 L27534).

Everything else (RecipeDB3, TASTEset, CulinaryDB, FlavorDB, FooDB, Archana's Kitchen) appears only in the master plan blocks (plan L392–418), not in §§230–257.

**Data requirements implied by L16.**
- Deep Gold 750–1,000 with dual independent annotation (L25593). Seed 100–500 difficult cases first (L25627, L27591).
- Gold-Light 3–5k. Silver 60–100k, stratified on 11 dimensions (L25605–25617): source domain; cuisine/region/country; dish category; process family; ingredient-count bin; step-count/graph-complexity bin; quantity completeness; rare/regional bin; language/locale; source licence/release constraints; failure/troubleshooting presence.
- **Authoritative portion and density tables** for Q1/Q2 (L25524–25525, Epic C "density/portion imports where allowed" L27761). No specific source is named in range; candidates must be researched (see §9).
- **Human-labelled query/evidence support pairs** with scientific hard negatives (RQ16-03, L26351).
- **Curated conflict cases** (RQ16-22).
- **Multi-turn session data**, simulated or real (RQ16-14/15).
- **Decision gold** with valid/invalid actions (RQ16-16).
- **Ambiguous decision scenarios** (RQ16-17).
- **Failure/recovery gold** (RQ16-18/19).
- **Substitution benchmark** (RQ16-26).
- **Held-out processed targets** for FlavorTwin (RQ16-25).
- **Optional small human sensory study**: "cost/ethics/sample size" (RQ16-27).
- **Queries with no direct but in-support model coverage** (RQ16-20). This needs L15 support regions first.

**Licence rules (§250).**
- Record licence, terms and redistribution status. "Do not assume that publicly viewable commercial recipe text can be redistributed". Release derived annotations/IDs/statistics where necessary (L27526).
- Raw snapshots and checksums "where permitted" (L27530).
- Release tiers (L27551–27557): open vocab/ontology; portion records "permitted by source terms"; derived annotations linked to source IDs; gold text "only where licensing permits"; evidence atoms with citations, not full papers; code/prompts/validators/splits.
- Repo state: `registry/recipe_source_usage_registry_v1.csv` already encodes training_allowed / raw_redistribution_allowed / derived_redistribution_allowed / H2_required per source. A1 BBC Good Food is LOCAL_RESEARCH_ONLY, training UNKNOWN, raw redistribution NO, RESTRICTED (11,934 recipes). Wikibooks is CC BY-SA 4.0 share-alike. Gutenberg is public domain in the US ("non-US status not assessed"). So §236.3's "source license/release constraints" stratum is implementable from existing registry columns. Deep Gold drawn from BBC would block gold text release (§250.7) and may block training use pending H2.
- §250.6 provider independence (L27546): schemas must not depend on a provider. Repo D-016 records that OpenAI GPT-5.6 drafted the pilot_20 annotations. That is consistent with provider-neutrality but makes §239.10 logging (model/provider/version/settings, L26256) mandatory.

---

## 6. Dependencies on other levels/steps

- **L15 gates → G16-TRANS / C9 / B6 / RQ16-20 / E16-J** (L25208, L27471, L27859). No transition fallback until the relevant G15 gates pass per target/domain. RQ16-20 also needs L15 "support distance" outputs.
- **L14 process-conditioned evidence → evidence ledger, compatibility vector, packet DIRECT EXPERIMENTAL EVIDENCE.** "L14/15 evidence acquisition: Critical long-pole … PARALLEL LONG-POLE" (L27733). Phase 4 runs "while recipe Silver scales. These tracks do not wait for 100k completion" (L27613).
- **L12 molecule/ingredient baselines → FlavorTwin static baselines** (ECFP/descriptors, L26777) and chemistry_link_ids (L25833). Marked PARALLEL (L27732).
- **L13 recipe representation ← Recipe Semantic Corpus + Quantity Ontology** (dependency graph L27702–27706). RQ16-23 uses "Level-13 tasks with quantity-rich subset".
- **L13E (§§260–279):** not referenced in §§230–257. §262 is the L12↔L13↔L13E↔L16 interface contract (L43277; outside range, UNVERIFIED here). Duplicate/source-family grouping (inv. #17, RQ16-13) overlaps L13E §264 recipe identity, i.e. completed Step 07I in the repo.
- **§254 dependency graph** (L27699–27721). The arrows are "dependencies, not a demand to execute every block sequentially. Schema/data/evidence work can run in parallel with Level-12 and Level-15 baselines." FlavorTwin V2 is last.
- **§255 decision matrix** (L27725–27738): freeze schemas DO NOW; Deep Gold DO EARLY; quantity engine DO EARLY; 10k pilot DO BEFORE SCALE; 60k→100k SCALE CONDITIONALLY; L12 PARALLEL; L14/15 evidence PARALLEL LONG-POLE; state-aware retrieval AFTER DATA SEED; confidence BEFORE FINAL SYSTEM; decision/diagnosis AFTER RETRIEVAL; FlavorTwin LATER; L17 DEFER.
- **Intra-L16 hard dependencies:**
  - Deep Gold → calibration (G16-CAL) → selective policy → decision layer;
  - duplicate groups → split registry → any Gold test;
  - vocab + CQPO → Silver pilot;
  - schemas/prompts/validators v0 → everything (Stage 0, L25626);
  - evidence ledger + lineage → conflict → packet;
  - feasibility → utility ranking (L26463).
- **Annex dependencies (UNVERIFIED here):** numeric thresholds and field semantics (§257C, §257D gold test catalog, §257E/§257L RQ protocols, §257G release audit tables, §257H few-shot design, §257A.15 split construction, §257A.5 evidence hierarchy, §257A.6 chemistry enrichment firewall, §257A.9 failure ontology starter).

---

## 7. Risks / failure modes

§251 register (L27561–27582), 20 rows, each with risk → mechanism → consequence → control:
- Vocabulary explosion
- Over-merging foods
- Quantity false precision
- Locale unit ambiguity
- LLM fabrication
- **Gold anchoring** (control: independent annotation before seeing model output)
- **Duplicate leakage**
- **Source template leakage** (parser learns website format; control: source-disjoint benchmark)
- **MNAR evidence bias** (control: propensity/sensitivity + bucket reporting)
- **Evidence lineage duplication**
- Conflict collapse
- **Retriever semantic shortcut** (control: structured compatibility + hard negatives)
- Confidence theater
- **Transition overreach** (control: G15 gates + OOD + downgrade/abstain)
- Optimizer exploitation (inverse search exploits model error)
- Procedure/chemistry conflation
- Sensory overclaim
- **Cascade errors** (control: module benchmarks + oracle upstream)
- **Cost blow-up** (100k multi-pass strong-model calls; control: pilot scaling + distillation + tiered models)
- Scope creep

Additional failure modes stated elsewhere in range:
- RQ risks: state parser errors erase gain (RQ01); over-filtering under sparse evidence (RQ02); label cost (RQ03); packet omits nuance (RQ04); dataset shift (RQ05); false abstention (RQ06); portion data sparse/biased (RQ07); over-merging (RQ08); Silver noise (RQ09); selection bias (RQ10); duplicate detector imperfect (RQ13); noisy user observation (RQ15); ontology incomplete (RQ16); VOI unreliable (RQ17); cause labels uncertain (RQ18); few gold conflicts (RQ22); cost/ethics (RQ27).
- **Endpoint-phrase leakage** (L26495): "Endpoint phrases are invalid leakage when used as future-label inputs during training, but valid execution-time stopping observations". Critical for Steps 19/29.
- **MNAR** (§240.5 L26317): completion/propensity methods "never convert missingness into observed truth". Sparsity is measured and reported, not filled (§240.4 L26313).
- **Silent annotation-policy mixing** (L26257): reprocess old Silver only under explicit dataset-version migration.
- **Gold-Light drift into the benchmark** (L25719).
- **Locked-test contamination** by iterative prompt tuning (§257P L42733).

Repo-observed realised risks:
- Gold anchoring has **already occurred**. DECISIONS D-016/D-017: pilot_20 is AI-drafted, human-reviewed, agreement "1.0 by construction … not inter-annotator agreement". `reports/gold/foodcom_ai_assisted_human_review.md`: "AI_ASSISTED_HUMAN_REVIEWED. NOT independent annotation", 126 proposed events not written.
- `registry/recipe_quality_tier_registry_v1.csv` marks DEEP_GOLD "none present yet … requires Step-19 style blind re-annotation". GOLD_PENDING_INDEPENDENT_IAA is the current status of the Food.com and A1 pilot sets.
- ctx reports `step07h_human_gate_result.json` = NOT_COUNTED_PROVENANCE_INVALID.
- So G16-DATA is **not met**, and inv. #16 must drive Step 19.

---

## 8. MAPPING TO THE 36-STEP SPINE (titles from brief §9; step-card content unavailable, reconstructed)

- **01 Freeze project authority.** L16 asserts spec COMPLETE and implementation OPEN (L25086–25092). The 24 invariants (L25147–25170) and §249.3 promotion order are laws to freeze. Required output: an authority note stating that L16 §§230–257 + annexes are SSOT authority, and that §244.3 repo layout / §244.4 artifact names are superseded by actual repo naming (needs a mapping table; see §9).
- **02 Audit implementation state.** Use §257 DoD (17 items, L27850–27866) and §257P checkboxes as the audit checklist. Mark each IMPLEMENTED / PARTIAL / NOT STARTED. Evidence available now: provenance enum present (registry), QNT Q0–Q6 present, STATE belief/override present, EVD independence_group/conflict_cluster present, identity/duplicate groups present (07I); Deep Gold absent; ClaimLedger runtime schema absent; InverseDesignTrial absent; retrieval/confidence/decision modules not started (UNVERIFIED beyond schema presence).
- **03 Freeze state semantics.** Must include:
  - §233.2 belief-field tuple (value/interval, unit, provenance class, timestamp, evidence/model ref, uncertainty/unknown);
  - observation-over-prediction rule (L25347);
  - five memory classes (L25387) and four evidence planes (L25268);
  - State fields (L25989–26006) incl. physical/visual/thermal/texture_state, moisture, water_activity, pH, chemical_state_ref, field_provenance, observation_source;
  - the relation enum (L25369–25378).
  Gate: "No pH/water-activity value appears unless explicit/external/model/simulated provenance is declared" (L26289). Repo `reports/h_state/state_representation_contract_v1.md` should be checked against these (not read by me).
- **04 Freeze evidence / provenance / similarity contracts.** Must include:
  - Evidence atom 6-tuple (L25251) and the 23 EvidenceAtom fields (L26019–26041);
  - 8-class provenance enum + rule 4 (L26117–26126);
  - DIGITIZED label (L26374);
  - UNKNOWN / NO EFFECT / NOT MEASURED / NON-DETECT / CONFLICTING distinctions (L25313–25315);
  - compatibility vector + categorical match types (L26344–26347);
  - inv. #11 (semantic sim ≠ compatibility) and #20 (chemical ≠ sensory);
  - FlavorTwin Z* factorization, no universal scalar (L26721–26724);
  - ClaimLedger contract (L26054–26064).
  Output: a reconciliation of the 3 repo provenance vocabularies (provenance_class, value_origin, REC.provenance.method).
- **05 Normalize EVD.** Every EVD row must be able to populate: measurement_target, value, unit, metric, matrix_description, analytical_method, study_id, source_id, doi, table_or_figure, source_span, evidence_class, verification, independence_group, quality_features (L26027–26041). Table headers, captions, units and footnotes preserved (L26374). Gate: units/metric definitions harmonized (needed before any contradiction, L26295, L26357).
- **06 Freeze source acquisition manifest.** §250.1/250.7 licence + redistribution per source. §236.3 "source license/release constraints" stratum. PII policy for comments (L27534). Raw snapshot + checksum "where permitted" (L27530). The manifest should record which sources may feed Deep Gold text release vs derived-only.
- **07 Condition & measurement normalization.**
  - Event condition fields temperature_C + temperature_raw, duration_s + duration_raw, pressure, pH, moisture_condition, medium, endpoint_states (L25943–25951). "CONDITIONS: temperature, time, pH, pressure, moisture, medium and endpoint are independent fields" (L26154).
  - Endpoints are qualitative stop criteria, not hidden numbers (L25674, L26155).
  - Compatibility needs per-dimension m_T, m_t, m_pH, m_matrix, m_measurement (L26344). Unknown condition must be representable as UNKNOWN, distinct from mismatch (L25206).
  - Measurement-side: analytical_method/platform is needed for contradiction step 6 (L26362).
  - Robustness test C↔F unit invariance (L26703) means the normalizer is benchmarked.
  - The 07H human gate still being invalid matters for G16-QTY/SEM claims built on conditions.
- **08 Scientific source lineage.** §232.6 lineage (L25309); validator L26294; contradiction step 7 (L26363); EvidenceAtom.study_id/source_id/doi/independence_group; risk "Evidence lineage duplication" (L27572). Outputs needed downstream: independence groups usable for study-disjoint splits (RQ16-20 "cold pair/study", RQ16-22 source-disjoint) and for conflict dedup "before agreement analysis". (Not executing Step 08; mapping only.)
- **09 Evidence extraction & verification machinery.**
  - §239.9 researcher prompt (L26242–26247): extract only measured values, conditions, units, matrix, method, provenance; return UNKNOWN; distinguish raw composition, processed composition, kinetic and mechanistic evidence.
  - §239.10 frozen prompt IDs/hashes, separate passes, logged model/provider.
  - V1–V6 validation stack (L26265–26270).
  - "LLM-extracted scientific rows entering final evaluation are human verified" (L26293).
  - DIGITIZED handling.
  - Metrics: extraction precision vs human verification. Cost accounting (L27542).
- **10 20-row mechanism pilot.** L16 gives no row count. Relevant L16 requirements: the pilot rows should exercise evidence classes (raw / processed / kinetic / mechanistic, L26246), table/figure provenance and verification. Seed the hard-negative and conflict-case sets that RQ16-03/22 need later.
- **11 Wave-1 verified mechanism evidence.** Must accumulate human-verified EXTERNAL_VERIFIED rows (needed for calibration, inv. #14) and record independence_group. Begin curated conflict cases (RQ16-22, "few gold conflicts" risk).
- **12 Structured database evidence.** Q1/Q2 authoritative portion/density tables belong here or in 16–17 as CQPO imports (Epic C, L27761). FDC alignment (L25826). Per-source licence for portion records (L27553).
- **13 Large literature discovery corpus.** Feeds R2 BM25 / R3 dense indexes over evidence atoms and passages (L26326–26327, L26538–26539). MNAR observation propensity must be logged (§240.5). Hard negatives: same food wrong process, same process wrong T/t, related food, raw vs processed, wrong endpoint (L26351).
- **14 Coverage-driven evidence growth.** Driven by C14 gaps and RQ16-20 "no direct but in-support" queries. Risk–coverage per support regime (§242.6) defines what "coverage" means for the RAG side. Bucket reporting for MNAR (L27571).
- **15 Freeze DATA-EVIDENCE v1.** Must freeze: evidence version (part of every experiment, L26601); lineage/independence groups; conflict clusters; split registry for study-/source-disjoint evaluation; release tier (§250.7). Gate candidates: G16-EVID prerequisites (exact provenance), G16-CONFLICT representation.
- **16 Instruction semantic schema.**
  - §234 vocab families (19) and proposal states (L25470–25478);
  - §235 CQPO (q tuple, Q0–Q6, raw+normalized fields);
  - §238 Recipe/IngredientMention/CanonicalIngredient/Alias/Quantity/PortionProfile/Event/Entity/State contracts;
  - §237 handbook rules (L25663–25687) and hard-case list (L25726–25742);
  - §244.4 frozen artifacts (schemas, vocab_v0, handbook_v0, master_prompt_v0, validation_rules_v0.yaml, prompt_registry_v0.json, split_registry_v0.json).
  Phase 0 exit (L27591): 100–500 difficult recipes representable without improvisation. §257P items 1–2. Repo has `annotation/annotation_handbook_v1.md` + Addendum A (D-017); compare to §237 (not done here).
- **17 Instruction-level extraction.**
  - §239 prompt pack: master instruction (L26106–26159) and ingredient (L26163–26171), curator (L26175–26188), quantity parser (L26192–26197), quantity grounding (L26202–26211), event parser (L26215–26221), state reconstructor (L26225–26230) and QA reviewer (L26234–26238) prompts. Multi-pass order structural parse → canonicalization → state graph → quantity grounding → QA → optional evidence enrichment (L26255).
  - Baselines: rules / small encoders / LLM / distilled / hybrid (E16-A); one-shot vs multi-pass (RQ16-11); LLM vs LLM+validators (RQ16-12).
  - Metrics §245.2–245.4.
  - Gates G16-SEM, G16-VOCAB, G16-QTY.
  - Must reuse the frozen NER/linker (S128) as the "smaller encoder" rung rather than reopening it.
- **18 Event-sourcing engine.** §233.3–233.6; Event/Entity/State contracts; validator rules L26277–26279 (no consumption before creation, every intermediate has a producing event, consistent split/merge refs) and L26296 (replay); interval propagation through fractions (L25383); C4/C18 rules. Metrics §245.5 (node/edge/merge-split F1, event order, replay consistency). Gate G16-GRAPH. RQ16-14/15/24 consume it. The repo GRAPH.replay_sha256 / STATE.overrides_state_id already exist.
- **19 Gold state-trajectory pilot.**
  - §237.2 Deep-Gold workflow (L25692–25700): source freeze + checksum → A independent → B independent → auto disagreement report → adjudication → validators → lock → split by duplicate/source group.
  - §237.3 per-task agreement (L25705–25715).
  - §237.5 hard-case sampling.
  - Stage 1 "100–500 difficult Deep-Gold seed cases" (L25627).
  - G16-DATA. Inv. #16 / L25665: annotators must not see Silver first.
  - The repo tier registry explicitly assigns DEEP_GOLD creation to "Step-19 style blind re-annotation".
  - Output must include the locked calibration/test split (needed for G16-CAL).
- **20 Scale procedural semantic corpus.**
  - §236.5 Stages 3–10 (10k pilot → audit → 25k → Gold-Light AL → 60k → consolidation → 100k if gates → freeze v1 + splits + dataset card);
  - §236.6 checkpoints every 5–10k; §236.7 release statistics;
  - §236.3 stratification; §236.4 anti-bias;
  - §240.3 active learning (RQ16-10); RQ16-09 saturation curve; RQ16-13 leakage inflation;
  - §250.5 cost per accepted record; §257P checklist before >10k (plan L386).
  - Stop rule "Silver does not improve held-out Gold performance" (L27492).
  - Sampling must be from the 612,782-recipe base / 611,714 exact reps (ctx); the base is the "large weak corpus" tier.
- **21 Effect / mechanism ontology.** L16 contributes V_FAILURE, V_RECOVERY, V_SENSORY, V_CHEMICAL vocab families (L25422–25425). Failure cause ≠ recovery annotation (L25686). Recoverability enum (L26479). The failure ontology starter is in §257A.9 (→ annex, UNVERIFIED here). Main mechanism content is L14/L15, outside this range.
- **22 Event → effect signatures.** L16 constrains it: "Do not infer process chemistry from a generic cooking action without approved scientific evidence" (L26136); "No chemistry value appears from a recipe-only annotation pass" (L26288); inv. #6. Signatures must be EvidenceAtom-backed or labelled MODEL_ESTIMATED/QUALITATIVE.
- **23 Mechanism applicability engine.** Is the runtime C7 compatibility layer applied to mechanisms: categorical match types before a scalar (L26347); "unknown condition != mismatch" (L25206). Output feeds C14 ALLOW/WARN/QUALITATIVE/ABSTAIN. Mapping of applicability → sufficiency modes (§242.6).
- **24 Formula / model registry.** L16 says little. ClaimLedger.model_id/model_version (L26059–26060) and InverseDesignTrial.forward_model_version (L26085) must resolve to registry IDs. G16-TRANS needs a per-target/domain whitelist of models that passed G15 (§257P "explicitly whitelisted").
- **25 Parameter-compatibility retrieval.** §241 R1–R8; RRF fusion baseline; compatibility vector; hard negatives (L26351); RQ16-02/03; E16-E; metrics condition-compatible Recall@K, MRR, NDCG; G16-EVID.
- **26–28 Simulator / validation / E7 prior.** L16 requirements: separate D^simulated plane (L25268); SIMULATED provenance never promoted (L26126); "Synthetic/Bronze … never final real test" (L25597); inv. #15; validator L26290; FlavorTwin PROCESS_SIMULATED_MATCH class (L26762); risk "Optimizer exploitation" (L27577). Imputed/simulated "may assist internal models but cannot masquerade as direct evidence" (L26444).
- **29 TRANSITION_BOOTSTRAP_V0.** C8 "retrieve before predict" (L25207). Endpoint-phrase leakage rule (L26495). State fields as targets need field_provenance. Repo `reports/h_state/transition_bootstrap_v0_contract.md` should be checked for the endpoint-leakage rule (not read here).
- **30–34 Tabular bake-off / physics features / kinetics / hybrid / short rollout.**
  - LightGBM named as an acceptable simpler winner (L27439).
  - C9 must output prediction + interval + support distance (L25208).
  - Interval coverage metric (L25208, L26633).
  - G16-TRANS; RQ16-20/21; E16-J.
  - Short rollout fits §243.10 receding horizon ("recommend one supported step → observe → update"), which is preferred over whole-recipe planning (L26507).
- **35 Representation ladder.**
  - z_q quantity encoder and h_{i,R} (L25561–25567), masks not zeros;
  - RQ16-07/23/24;
  - FlavorTwin static baselines random/category/ECFP/descriptors/static embeddings/multiview (L26777);
  - Z* factorization; contextual substitution score (L26750);
  - G16-FT.
- **36 Evidence compiler → selective CulinaryState-RAG → later FlavorTwin.**
  - Everything in §231 (C1–C18), §232.4–232.8 (query views, packet), §241–§243, §245 (benchmark/B0–B7/ablations/oracle/robustness), §246, RQ16-01–06, 14–22, 25–30, E16-E…L, gates G16-EVID/CONFLICT/CAL/TRANS/DEC/REC/PROV/OOD/FT;
  - §252 Phases 7–11; §253 deliverables and demo; §257 DoD; §244 services/storage/versioning.
  - Minimum viable: B0–B5 + confidence/abstention demo + one state-aware action/diagnosis case (L27650–27661).
- **Cross-cutting split work (no single spine step).** Inv. #17, validator L26291, §237.2 last step, RQ16-13/28 and DoD #6 all need a frozen split registry (`split_registry_v0.json`, L26596). The likely homes are Step 15 (evidence) and Step 20 (recipes), built on 07I identity.

---

## 9. Contradictions, stale items, underspecified parts, open questions

**Contradictions / inconsistencies**
1. **Vocabulary review enum mismatch.** §234.7 has `NEEDS_HUMAN_REVIEW` (L25478); the curator prompt §239.3 has `HUMAN_REVIEW` (L26185). Pick one.
2. **Quantity ladder mismatch.** §235.3 has 7 levels including Q5 MODEL_ESTIMATE (L25528). The grounding prompt §239.5 has 6 steps ending "otherwise UNKNOWN" with no model-estimate step (L26203–26208). Repo POR.basis has a `CONVENTION` value with no Q-level counterpart. Needs an explicit mapping (is a convention table Q1, Q3 or something else?).
3. **Provenance UNKNOWN overloaded.** §239.1 uses UNKNOWN as a field-provenance class meaning "evidence absent" (L26116, L26125). Repo `provenance_class_registry_v1.csv` defines UNKNOWN as "origin not recorded … legacy rows". Repo also has two other origin vocabularies: `value_origin_registry_v1.csv` (MEASURED, REPORTED, DERIVED_DETERMINISTIC, SOURCE_IMPUTED, SOURCE_IMPUTATION_POSSIBLE, UNKNOWN) and REC.provenance.method (MANUAL/IMPORT/RULE/LLM/MODEL/DERIVED/SCRAPE). Value-unknown vs provenance-unknown needs disambiguation in Steps 03/04. DIGITIZED (L26374) is also absent from the 8-class enum.
4. **Planes vs memory classes.** §232.3 separates D^estimated and D^simulated (L25268). §233.7 folds predictions, imputations and simulations into one "Model memory" (L25391). Brief §13 wants SIMULATION MEMORY as its own plane. Recommend keeping simulated as a separate plane, consistent with §232.3.
5. **Cascade with/without ASK.** §242.8 (L26437–26441) and RQ16-06 (L26887) have no ASK level. Brief §28 specifies DIRECT → INTERPOLATE → MODEL → QUALITATIVE → ASK → ABSTAIN. ASK exists only as a decision mode (§243.1) and VOI action (§243.8). The plan should state where ASK sits (before ABSTAIN when VOI > cost).
6. **Calibration-data independence vs repo tier policy.** Inv. #14 and §242.3 (L26401) require independently verified Deep-Gold calibration data. Repo tier GOLD_PENDING_INDEPENDENT_IAA allows calibration use "yes (development/calibration only)", and GOLD_LIGHT allows test use "only if never used for tuning and family-disjoint", whereas §237.4 says Gold-Light "should not silently become the final unbiased benchmark" (L25719). Tighten: no G16-CAL claim from AI-assisted gold.
7. **Gold anchoring already happened.** D-016/D-017 and the S117 Food.com review are AI-drafted Gold accepted by humans. This violates inv. #16 / §237.1 L25665 for any evaluation use. The repo labels it correctly as development Gold; Deep Gold = 0.
8. **§244.3 repo layout and §244.4 artifact names are stale.** The actual repo uses `ledgers/schemas/{REC,EVT,STATE,ENTITY,QNT,POR,ING,ALIAS,CLM,GRAPH,SPLIT,EVD,...}.schema.json`, `registry/`, `annotation/`, `src/`. The runtime ClaimLedger (§238.238) differs from repo CLM (research claims), which is a semantic collision. Field gaps vs §238 are listed in §1.8 (REC licence/locale/language/servings/annotation_* fields; ENTITY parentage/creation/destruction; POR interval/sample_count/source_diversity/size_class; EVD doi/table_or_figure/source_span/quality_features). Some may live in parquet or nested objects: UNVERIFIED.
9. **Master plan numbering collision.** Plan blocks B07–B11 (B08 = NER/semantic engine, B10 = quantity) vs spine Step 08 = source lineage, Step 10 = mechanism pilot. Also plan L519 says "SX-16-01 … SX-16-12 map 1:1 to E16-E…L", but E16-E…L is 8 families, so 8 + 2 named (SX-16-11/12) ≠ 12.
10. **RQ16-14 "simulated/real multi-turn sessions" (L27047).** Simulated sessions are synthetic. Under inv. #15 they cannot be the headline test. The plan must require real held-out sessions for the claim.
11. **Course framing.** "semester implementation" (L26511), "course scope" (L25091, §253). The timeline is not reconciled with the 36-step spine; unknown whether course constraints still apply.

**Underspecified**
- G16 gates have no numbers ("declared threshold", "acceptable", "useful coverage"). Same for RQ promotion criteria. Pre-registration (thresholds, CIs, minimum detectable effects) must be written before Steps 17–20/36 run. Possibly in §257E/§257L (UNVERIFIED here).
- §238 per-field types/null semantics are boilerplate; §257C must be read by another reader.
- Deep Gold size (750–1,000) has no power justification. Per-task calibration of 7 separate probabilities (§242.2), 12 benchmark families, macro reporting over 9 span types, and per-split (source/cold/long-tail) reporting may leave very small cells.
- The duplicate-group definition used for splits is not stated in L16. Repo 07I has 6,589 provisional edges and a 400-pair blind packet UNLABELED (ctx/WORKLOG S134), so near-duplicate calibration is incomplete. §236.6 requires re-running grouping every 5–10k records.
- Decision gold, failure/recovery gold, conflict cases, VOI scenarios and sessions have no size, source or protocol in range.
- Silver selection from 612k: §236.3 lists strata but gives no allocation (proportional vs equal vs Neyman), and no rule for how the duplicate families interact with sampling (one rep per family?).
- "Large weak corpus 1M+ when permitted" — not needed; 612k is in hand.
- Cost model for 60–100k multi-pass LLM calls (§250.5, risk "Cost blow-up") is not quantified. Provider is not fixed (Claude per §239 title vs GPT-5.6 used in D-016).

**Open questions needing external research (candidates; none verified in this pass)**
- IAA design/thresholds for span + relation + graph annotation (kappa vs F1-based agreement for spans; sample sizes for adjudicated sets). Orientation sources to check: Artstein & Poesio 2008 (Computational Linguistics) on agreement measures; Hripcsak & Rothschild 2005 on F-measure as agreement. UNVERIFIED.
- LLM-as-annotator reliability and anchoring bias in human-in-the-loop labelling (2023–2026 literature). UNVERIFIED.
- Calibration with ~1k items: ECE estimator bias, binning, Brier decomposition; conformal / selective-prediction risk control as an alternative or complement to Platt/isotonic (e.g. Angelopoulos & Bates conformal tutorial; Geifman & El-Yaniv selective classification). UNVERIFIED.
- Citation/attribution metrics for RAG (ALCE citation precision/recall, Gao et al. 2023 EMNLP; claim-level entailment checking). UNVERIFIED.
- RRF baseline (Cormack, Clarke & Büttcher 2009, SIGIR). UNVERIFIED.
- Authoritative portion/density sources for Q1/Q2: USDA FNDDS portion weights / FDC food portions; FAO/INFOODS density database; country-specific household-measure tables (e.g. Indian household measures referenced by plan SX-10-05). Licence and coverage must be checked.
- FoodOn alignment practicality and licence (CC BY 4.0, UNVERIFIED); LanguaL/FoodEx2 for facet factorization (brief §14).
- Active learning for structured prediction / NER with budget comparisons vs random (RQ16-10).
- VOI / clarifying-question policies in task-oriented dialogue (RQ16-17).
- Sensory-similarity human study feasibility/ethics (RQ16-27). Likely DEFER.

---

## 10. LOOK-AHEAD: what earlier steps must capture so L16 is usable later

**Steps 03/04 (state + evidence/provenance contracts)**
- Field-level provenance on every state/event/quantity field, using the 8-class enum. Disambiguate VALUE_UNKNOWN from PROVENANCE_UNKNOWN. Add DIGITIZED (or a flag) for plot-extracted values (L26374).
- Evidence-null semantics as distinct codes: NOT_MEASURED, NON_DETECT (with LOD/LOQ if given), NO_EFFECT, CONFLICTING, UNKNOWN (L25313–25315).
- Compatibility-vector dimensions must be derivable per EVD row: food (ID + species + food group), state/form, process leaf + family, T, t, pH, target (SVAR) definition, matrix, measurement method/platform, source quality (L26344). Categorical match levels (EXACT, SAME_SPECIES, SAME_FOOD_GROUP, SAME_PROCESS_FAMILY, GENERIC_MECHANISM) need taxonomy parents in ING and PROC.
- Runtime ClaimLedger fields (claim_id, response_id, claim_type, evidence_ids, model_id/version, confidence_class, citation_refs, verification_status). Distinguish from research CLM.
- State belief tuple: value or interval + unit + provenance + timestamp + evidence/model ref + uncertainty (L25338–25345); observation_source; PLANNED vs OBSERVED vs PREDICTED.

**Step 05 (EVD normalize)**
- Per row: doi, table_or_figure, row/column headers, caption, footnotes, source_span (L26374, L26036–26037); analytical_method; metric definition (needed for unit/metric harmonization before conflicts); evidence_class (raw composition / processed composition / kinetic / mechanistic, L26246); quality_features; verification state with who/when.

**Step 06 (manifest)**
- Per source: licence_class, training_allowed, raw/derived redistribution, PII presence (comments), raw snapshot + checksum, release tier eligibility (§250.7). Already mostly present in `recipe_source_usage_registry_v1.csv`; extend to scientific sources and portion/density tables.

**Step 07 (conditions/measurements)**
- Keep raw + normalized for temperature, duration, pressure, pH, moisture, medium and endpoint as separate fields (L26154).
- Explicit UNKNOWN vs NOT_APPLICABLE vs CENSORED for conditions.
- Locale for ambiguous units (cup, tablespoon, oven marks) and the C↔F source dialect, both needed for robustness tests (L26703–26704).
- Endpoint phrases tagged as STATE/STOP observations (not conditions) and flagged as leakage-sensitive for transition training (L26495).
- Measurement platform/method IDs (contradiction check step 6).

**Step 08 (lineage), not executed, look-ahead only**
- study_id, document → study → experiment → sample hierarchy; citation ancestry / derived-copy links; independence_group; publication and lab/author grouping to support study-disjoint and publication-disjoint splits (RQ16-20 "cold pair/study"; RQ16-22 source-disjoint; validator L26294).
- Conflict-cluster IDs must be assignable only after lineage dedup.

**Step 09 (extraction/verification)**
- Extraction pass ID, prompt ID + hash, model/provider/version/settings (L26252, L26256); human verifier ID; verification outcome; time per row (cost accounting L27542); extraction uncertainty for digitized values.

**Steps 10–15 (acquisition)**
- MNAR observation-propensity covariates per cell: food popularity, analytical method, publication venue/year, detectability (L26317). These are needed for L15 sensitivity and C14 OOD.
- Deliberately captured scientific hard negatives: same food/other process, same process/other T-t, related food same target, raw vs processed, wrong endpoint (L26351). Without them, RQ16-03 and G16-EVID cannot be evaluated.
- Curated conflict cases with resolution labels (RQ16-22).
- Support-regime labels per query cell (direct / near / model-only / qualitative / none / conflict) for RQ16-06/20 and §245.8.
- Authoritative portion/density records (Q1/Q2) with ingredient, form, state, size_class, packing, locale, mass + low/high, sample_count, source_diversity, licence (L25905–25922). The repo POR schema lacks the interval and sample-count fields, so add them before import.
- Evidence version stamping for Step 15 freeze (L26601).

**Steps 16–20 (procedure/state)**
- Recipe-level: language, locale, licence_class, source_domain, cuisine_labels, dish_categories, servings_raw/normalized, duplicate_group_id (from 07I), annotation_tier, annotation_model, prompt_version, schema_version, validation_flags (L25751–25776). These are also the §236.3 sampling strata, so they must exist before Silver sampling.
- Mention-level: raw span; candidate_ids for ambiguity; variety/form/state/size/role/brand separate; optional/divided/reserved; canonicalization_status (the 9 proposal states); annotation_confidence_features (needed by the confidence vector q_entity, q_quantity, q_extraction, q_agreement).
- Event-level: input/output entity IDs, tool_ids, medium, process modifiers (granularity/intensity/geometry/endpoint), span, and the relation enum incl. RESERVED_AS / DISCARDED_FROM / RECOMBINED_WITH / TRANSFERRED_TO.
- Entity-level: parent_entity_ids, created_by_event, destroyed_or_consumed_by_event, allocation fraction (for interval propagation L25383).
- Failure/troubleshooting presence flag and comment-derived failure/recovery candidates (with PII policy) to seed V_FAILURE / V_RECOVERY and RQ16-18/19.
- Gold workflow metadata: annotator ID, blind flag (saw model output? Y/N), adjudicator, adjudication reason/version (L25682), freeze checksum, split assignment by duplicate/source group (L25700).
- Batch statistics per §236.7 and checkpoint audits per §236.6, logged from the first 10k pilot.
- Session-level schema (session_id, observation events, user-supplied observations with source) so RQ16-14/15 can use real sessions. Repo GRAPH has session_id.

**For Steps 29–36 specifically**
- Per-target/domain G15 gate results must be machine-readable (whitelist) for G16-TRANS.
- Every model output stored with model_id/version, interval, support distance and OOD flag (C9, InverseDesignTrial fields), so the ClaimLedger and C14 can consume them.
