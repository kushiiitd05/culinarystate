# READER ssot_annexA — SSOT v15 §257A / §257B / §257C (L27869–L31464)

Reader: ssot_annexA · Date 2026-10-22 · Read-only audit. All SSOT line numbers refer to
`docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (45,697 lines). Repo paths are relative to
`/home/manjot23309/kush_work/culinarystate`. The 36-step Master Execution Plan v1 is NOT present (ctx.md);
step mappings in §8 are my reconstruction from SSOT + repo, NOT quoted step-card text.

## 0. What the range actually contains (read-coverage statement)

- §257A L27869–28538 (25 subsections): read **in full**, line by line. This is the only part of the range with
  substantive, section-specific content (decision trees, enums, test strings, checklists).
- §257B L28539–29335 (C1–C18): read in full. **Every one of the 18 contracts is the same template.** Verified
  mechanically: each of the 34 non-heading body lines (10 implementation obligations, 12 unit tests, 8
  evaluation-reporting items, 1 promotion rule, 3 subheadings) occurs exactly 18 times in the range. The only
  per-module content is the two lines "Primary inputs"/"Primary outputs". The SSOT itself says the section "is
  intentionally repetitive" (L28541). Module-specific rules/metrics live in **§231.2 L25196–25217** (the "18-module
  registry"), which I read to fill the gap.
- §257C L29336–31464: read in full. **All 210 field entries (12 entities) are the same 8-bullet template**
  (verified: each of the 8 bullet texts occurs exactly 210 times after masking the field/entity name). Only the
  field *names* are entity-specific. No types, enums, units, ranges, nullability or cardinalities are given.
  The field list is **byte-identical to §238** (L25745–26101; diffed: 210 = 210, identical order), whose entries are
  also boilerplate ("required to be typed/versioned; nullable only according to the schema…").
- Consequence (major): §257C is a **field-name inventory plus a generic discipline**, not a data dictionary in the
  usual sense. Types/enums/units must be designed (Steps 03/04/16) — they cannot be "looked up" in the SSOT.

---

## 1. Definitions, entities and data contracts

### 1.1 Ingredient canonicalisation decision tree (§257A.1, L27873–27914)
Six steps for every new ingredient surface phrase:
1. Typography normalisation only (lowercase where language permits, Unicode normalise, whitespace; **preserve raw
   phrase separately**) L27878–27882.
2. Parse modifiers: quantity, unit, size, packing, variety/cultivar, form/cut, state/preparation, brand,
   **geographic qualifier**, **compound-food phrase** L27884–27894.
3. Remove non-identity modifiers *conceptually*; search canonical vocabulary + alias table L27896–27897.
4. Decide — 7-way outcome enum (L27899–27906):
   `EXISTING_ALIAS` · `EXISTING_CONCEPT_WITH_MODIFIERS` · `AMBIGUOUS/POLYSEMOUS` · `BRAND_ALIAS / PRODUCT_VARIANT` ·
   `COMPOUND_FOOD` · `TRUE_NEW_CONCEPT` · `NON_FOOD`.
5. External alignment to an approved ontology/database "when useful"; **preserve internal ID even if no external
   mapping exists** L27908–27910.
6. Provenance: first-seen source, frequency, locales, model/human decision L27912–27913.

Factorisation examples (§257A.1.1 L27916–27945) — these are de-facto schema requirements:
- "large red onion, finely chopped" → food=onion, variety/color=red, size=large, form=finely_chopped.
- "roasted unsalted peanuts" → food=peanut, state=roasted, **salt_state=unsalted** (a facet that has no §257C field).
- "frozen spinach, thawed and squeezed dry" → food=spinach, **source_state=frozen**, event/state history
  thawed → squeezed_dry (i.e. ingredient-line text can encode *events*, not only state).
- "1 can diced tomatoes" → food=tomato, form=diced, container=can, quantity separate.
- "garlic cloves" → food=garlic, portion/count unit=clove; do NOT create concept "garlic clove" unless anatomical
  portion is intentionally modelled as a child concept (L27944).

Human-review triggers (§257A.1.2 L27947–27957): above "a **declared** frequency threshold" and unresolved (number
NOT declared anywhere in SSOT — grep finds only L27951); two plausible foods with materially different
composition/role; cultural/regional specificity with ontology disagreement; branded formulation-dependent product;
compound food whose decomposition loses meaning; fermentation starter/culture; preparation whose identity changes
(stock, paste, concentrate).

### 1.2 Quantity normalisation decision tree (§257A.2, L27959–28005)
Input = raw quantity phrase + ingredient + form/state + **source locale** (L27962).
1 numeric structure: exact scalar / fraction / range / count / qualitative.
2 raw unit class: physical SI/imperial / culinary volume / count-portion / container / informal qualitative.
3 locale: explicit source locale / dataset-level locale / unresolved.
4 deterministic conversion (mass↔mass, volume↔volume) → `DERIVED_DETERMINISTIC` (L27985).
5 food-specific conversion needed? volume→mass, count→mass, container→mass, size→mass.
6 lookup hierarchy (L27993–27999): authoritative exact portion → authoritative density → other approved national
  table → multi-source verified estimate → empirical corpus distribution → model estimate **only if task explicitly
  permits**.
7 output: exact if authoritative/deterministic; **interval/distribution if variable**; `UNKNOWN` if unsupported.
Relation to §235.3 Q-ladder (L25520–25530: Q0 EXACT_PHYSICAL … Q6 UNKNOWN): §257A.2 inserts "other approved
national table" which has no Q-level; see §9.

Test strings (§257A.2.1 L28007–28045, 33 cases) — mandatory hard cases for the parser/validator suite: plain/
mixed fraction/unicode-range ("1½–2 cups water"), counts with size ("2 large eggs", "1 small/medium/large onion"),
count + event ("2 eggs, beaten"), nested container ("1 (14 oz) can tomatoes", "one 400 g tin"), anatomical portion
("3 cloves garlic") vs homograph spice ("1/4 tsp ground cloves"), part-of-fruit ("juice of 1/2 lemon", "zest of one
lemon"), packing qualifiers (heaped/level/packed/loosely packed), qualitative (pinch/dash/splash/handful/as
needed/for frying/to taste/for dusting), multipliers ("2 x 200 g", "three 250-mL bottles"), and **intra-recipe
reference quantities** ("half the reserved sauce", "one third of the dough", "remaining batter").
Expected output = "structural parsing plus evidence-grounded conversion status, **not invented gram values**" (L28047).
(§257D L31465ff. expands these into Q00x gold cases — outside this range.)

### 1.3 Process/action canonicalisation (§257A.3, L28049–28074)
surface phrase → head action → modifiers (**intensity, geometry, granularity, medium, endpoint**) → canonical process
leaf → process family → retain original phrase → create event with explicit inputs/outputs/conditions.
Examples: finely/roughly chop → CHOP+granularity; pan fry → FRY/PAN_FRY "depending ontology granularity"; deep fry →
FRY+immersion=deep "/ dedicated leaf if justified"; simmer gently → SIMMER+intensity=gentle; bake until golden →
BAKE+endpoint=golden. Rule: don't make chop variants unrelated concepts "unless an experiment explicitly requires
separate canonical leaves" (L28074). Leaf-vs-modifier decision is left open (two hedges in L28068–28069).

### 1.4 State field policy — 10-value field-status enum (§257A.4, L28076–28093)
`KNOWN_EXPLICIT · KNOWN_EXTERNAL · DETERMINISTICALLY_DERIVED · INFERRED · MODEL_ESTIMATED · IMPUTED · SIMULATED ·
UNKNOWN · CONFLICTING · NOT_APPLICABLE`. "UNKNOWN and NOT_APPLICABLE are not the same" (L28093).
**Conflicts with the 8-value provenance enum of §239.1 L26117–26125** that the repo adopted (see §9 C1).

### 1.5 Scientific evidence acquisition hierarchy (§257A.5, L28095–28122)
Priority: 1 primary controlled experimental paper/table; 2 curated authoritative DB retaining primary provenance;
3 systematic review/meta-analysis with extractable conditions; 4 high-quality review for mechanism/context only;
5 secondary source only as lead to primary; 6 "**LLM knowledge is never a scientific evidence source**" (L28104).
Per quantitative row capture (L28108–28121, 13 items): food/matrix; food state/form; process leaf/family;
T/time/pH/moisture/pressure/medium where reported; target variable/compound; before/after **or trajectory** values;
units/**basis (wet/dry/yield-corrected)**; analytical method; replicates/sample information; study/source ID;
exact table/figure/span; **extraction method**; human verification status.

### 1.6 Chemistry enrichment firewall (§257A.6, L28124–28147)
Allowed: recipe ingredient→external evidence link with `EXTERNAL_VERIFIED` provenance. Not allowed: setting this
batch's compound concentration = database average. Allowed model behaviour: external prior "with explicit
uncertainty/model provenance". (Note: uses §239 vocabulary `EXTERNAL_VERIFIED`, not §257A.4 `KNOWN_EXTERNAL`.)

### 1.7 Other definitional lists in §257A
- Localisation (§257A.7 L28149–28161): record source country/locale, language, measurement system, regional aliases,
  transliteration variants, cuisine labels **as source metadata**, locale-sensitive portion conventions; never infer
  ethnicity/nationality from ingredient names.
- Multilingual boundary (§257A.8 L28163–28171): 5 entry conditions (language-independent schema, stable concepts,
  language-specific alias tables, per-language annotation evaluation, MT never silently treated as gold).
- Failure/recovery ontology starter (§257A.9 L28173–28226): 7 parent families (THERMAL, MOISTURE, EMULSION_PHASE,
  TEXTURE_STRUCTURE, FERMENTATION_LEAVENING, SEASONING_BALANCE, PROCEDURAL) with 32 leaves; **cause, symptom,
  recovery are separate relation types**, many-to-many, "or no reliable recovery" (L28226).
- Decision modes (§257A.10 L28228–28238): ANSWER/PROCESS_EFFECT, COMPARE, DIAGNOSE, RECOVER, RECOMMEND, ASK,
  ABSTAIN or QUALITATIVE.
- Candidate-action schema (§257A.11 L28240–28263, 18 fields): action_type, canonical_process_id, target_entity_ids,
  condition changes, duration or stop criterion, tool req., medium req., state prerequisites, hard constraints, soft
  preferences, expected state effects, evidence/model route, evidence class, predictive interval, OOD/support
  distance, feasibility result, rejection reasons, goal-match vector.
- Rejection reason registry (§257A.12 L28265–28283, 15 codes): MISSING_TOOL, MISSING_MEDIUM, INCOMPATIBLE_STATE,
  UNMET_PREREQUISITE, TIME_CONSTRAINT, USER_CONSTRAINT, NO_EVIDENCE, LOW_SUPPORT, HIGH_UNCERTAINTY, HIGH_OOD,
  MODEL_NOT_VALIDATED, DOMINATED_OPTION, RECOVERY_NOT_EVIDENCED, IRREVERSIBLE_STATE, UNKNOWN_STATE_CRITICAL.
- DISALLOWED_CLAIMS packet field (§257A.13 L28285–28296), 6 examples (no exact pH; no exact vitamin conc.; no
  calling model-completed values measured; no structural=sensory; no causality from cross-study association; no
  citing a review as the primary experiment when the primary is available).
- Claim-language by provenance (§257A.14 L28298–28324), 8 classes with verbatim templates: EXPLICIT/MEASURED,
  EXTERNAL_VERIFIED, **INTERPOLATED** (not in either provenance enum), MODEL_ESTIMATED, IMPUTED, SIMULATED,
  CONFLICTING, UNKNOWN.
- Release semantics (§257A.16 L28341–28356, 10 fields): dataset_version, schema_version, ontology_version,
  quantity_database_version, source_snapshot_date, annotation_model/prompt versions, human gold revision,
  **split registry hash**, license/redistribution notes, known limitations.
- Experiment registry template (§257A.20 L28408–28432, 19 fields): experiment_id, research_question_id, hypothesis,
  code_commit, dataset_version, split_version, schema_version, ontology_version, prompt/model versions, baselines,
  model config, random seeds, compute, metrics, confidence intervals, artifacts, failure notes,
  decision KEEP/MODIFY/DROP/NEED_DATA, next dependency.

### 1.8 Module contracts C1–C18 (§257B; per-module rules from §231.2 L25198–25217)
Common obligations for all 18 (L28550–28559 etc.): typed input contract, reject malformed/ambiguous (no silent
coercion); preserve raw form; attach module/schema/upstream-artifact versions to every persisted result; explicit
UNKNOWN/UNRESOLVED; machine-readable rejection reasons; no responsibility creep; deterministic replay on frozen
versions "where technically possible"; emit provenance/features for downstream calibration; **oracle-upstream
evaluation** and **predicted-upstream end-to-end evaluation** (cascade error). 12 common unit tests (L28562–28573).
8 common reporting items (L28576–28583): micro, macro over entity/process/source buckets, **source-disjoint**,
long-tail/frequency bucket, error taxonomy, calibration when probabilistic, latency & cost, human-review burden.

| C | §257B line | Inputs → Outputs (§257B) | Permanent rule (§231.2) | Headline eval (§231.2) |
|---|---|---|---|---|
| C1 Query/intent | L28543 | raw query+session → intents, targets, mode | multi-intent; preserve raw query | intent/multi-intent F1; OOD intent rate |
| C2 Entity/coref | L28587 | mentions+ontology+session graph → entity IDs+links+**unresolved candidates** | do not force unresolved pronouns | entity F1; coref acc.; unresolved calibration |
| C3 State reconstructor | L28631 | entities/events/observations → field-wise state beliefs+provenance | explicit vs inferred provenance | field accuracy; calibration; contradiction recovery |
| C4 Process-history | L28675 | event stream → ordered history/event DAG | event order immutable except adjudication | event order / graph edge F1 |
| C5 Goal/constraint | L28719 | query+context → goals+hard/soft constraints | do not invent priorities | goal F1; constraint violation |
| C6 Multi-index retriever | L28763 | structured/text/graph query → candidate evidence | hybrid lexical/dense/structured/graph | Recall@K; condition-compatible Recall@K |
| C7 Compatibility | L28807 | query+candidate → compatibility vector+support class | **unknown condition != mismatch** | human support labels; calibration |
| C8 Direct transition lookup | L28851 | state/process/target → observed/near-observed transition | retrieve before predict | direct-evidence precision |
| C9 Transition fallback | L28895 | supported query+L15 model → prediction+interval+OOD/support | only models that passed relevant G15 gates | OOD/cold metrics; interval coverage |
| C10 Candidate actions | L28939 | state+goal+ontology/evidence → action candidates | LLM may propose; verifier decides | candidate Recall@K |
| C11 Feasibility | L28983 | action+state+constraints → allow/reject+reason | hard constraints before utility | violation rate; rejection accuracy |
| C12 Outcome comparator | L29027 | feasible candidates → predicted outcomes+trade-off vectors | preserve multi-objective | goal error; robust ranking |
| C13 Relevance gate | L29071 | predicted changes+goal → goal-relevant dimensions | relevance is not causality | relevance P/R |
| C14 Uncertainty/OOD | L29115 | state/evidence/model uncertainty → ALLOW/WARN/QUALITATIVE/ABSTAIN | separate uncertainty sources | risk–coverage; error detection |
| C15 Multi-objective | L29159 | candidate records → Pareto/trade-off set | no arbitrary global utility | Pareto validity; consistency |
| C16 Grounded generator | L29203 | evidence packet+decision → answer | verbalise; no second analysis | claim support; factual consistency |
| C17 Citation/provenance | L29247 | claims+evidence/model refs → claim ledger+citations | claim-level traceability | citation P/R |
| C18 Session updater | L29291 | observation/action+prior graph → new versioned graph | direct observation overrides prediction on observable fields | state replay consistency |

### 1.9 Field-level data dictionary (§257C) — field names only (types NOT specified)
Template applied to all 210 fields (e.g. L29343–29350): one stable meaning per schema version; explicit types, no
stringly-typed polymorphism unless declared tagged union; null/UNKNOWN/NOT_APPLICABLE documented separately, **zero or
empty string never a generic missing code**; source-/science-/quantity-derived fields retain span/derivation record;
validate allowed values, referential integrity, units/ranges, cross-field consistency; reinterpretation requires a
migration, old releases not rewritten; **per-field error logging** for learned outputs; downstream models get a
**mask/quality/provenance indicator** where reliability varies.

- **Recipe** (26; L29340–29601): recipe_id, dataset_version, source_id, source_url, source_domain, license_class,
  source_checksum, title_raw, title_normalized, language, locale, cuisine_labels, dish_categories, servings_raw,
  servings_normalized, ingredient_mention_ids, event_ids, entity_ids, recipe_graph_id, duplicate_group_id,
  annotation_tier, annotation_model, prompt_version, schema_version, validation_status, validation_flags.
- **IngredientMention** (19; L29602–29793): mention_id, recipe_id, raw_text, source_span, canonical_ingredient_id,
  candidate_ids, variety, form, state, size, quantity_id, role, optional, divided, reserved, brand,
  canonicalization_status, provenance, annotation_confidence_features.
- **CanonicalIngredient** (17; L29794–29965): ingredient_id, preferred_name, food_category, parent_id,
  scientific_name, foodon_id, fdc_ids, aliases, regional_aliases, languages, known_forms, known_states,
  portion_profile_ids, chemistry_link_ids, status, version_created, human_verified.
- **Alias** (10; L29966–30067): alias_id, surface, canonical_ingredient_id, language, locale, alias_type,
  source_count, source_domains, verification, first_seen_version.
- **Quantity** (22; L30068–30289): quantity_id, raw_text, quantity_type, value, lower, upper, fraction, count,
  unit_id, unit_locale, size, packing, container, approximate, qualitative_term, optional, divided, reserved,
  normalized_mass_g, normalized_volume_ml, conversion_record_id, provenance.
- **PortionProfile** (18; L30290–30471): portion_profile_id, ingredient_id, state, form, size_class, packing,
  portion_value, portion_unit, unit_locale, mass_g, mass_low_g, mass_high_g, conversion_class, source_type,
  source_record, sample_count, source_diversity, verification.
- **Event** (20; L30472–30673): event_id, recipe_id, event_index, process_id, process_modifiers, input_entity_ids,
  output_entity_ids, tool_ids, medium, temperature_C, temperature_raw, duration_s, duration_raw, pressure, pH,
  moisture_condition, endpoint_states, source_span, provenance, validation_flags.
- **Entity** (10; L30674–30775): entity_id, recipe_id, entity_type, canonical_food_id, name, parent_entity_ids,
  created_by_event, destroyed_or_consumed_by_event, quantity_state_id, current_state_id.
- **State** (18; L30776–30957): state_id, entity_id, event_index, timestamp, form, physical_state, visual_state,
  thermal_state, texture_state, temperature_C, moisture, water_activity, pH, quantity_mass_g, chemical_state_ref,
  field_provenance, uncertainty, observation_source.
- **EvidenceAtom** (23; L30958–31189): evidence_id, subject_type, subject_id, relation, object_type, object_id,
  process_id, conditions, measurement_target, measurement_value, measurement_unit, metric, matrix_description,
  analytical_method, study_id, source_id, doi, table_or_figure, source_span, evidence_class, verification,
  independence_group, quality_features.
- **ClaimLedger** (11; L31190–31301): claim_id, response_id, claim_text, claim_type, evidence_ids, model_id,
  model_version, confidence_class, citation_required, citation_refs, verification_status.
- **InverseDesignTrial** (16; L31302–31462): trial_id, initial_state_id, target_state, candidate_ingredient_ids,
  candidate_process, candidate_conditions, constraints, optimizer, forward_model_version, predicted_state,
  prediction_interval, evidence_distance, OOD_flag, feasible_flag, heldout_or_real_outcome, target_error.

### 1.10 Repo reality vs these contracts (verified read-only)
- Ledgers present (`ledgers/data/*.jsonl`): ING 5,387; ALIAS 4,183; PROC 552; TOOL 297; UNIT 74; COND 4,746;
  EVD 57,280; STUDY 125; SVAR 355; MEAS 3; EXP 8 … **No QNT, POR, INST, ENTITY, EVT, STATE, SPLIT, CLM ledgers**
  — all listed `BLOCKED_FUTURE_STEP` in `reports/step07/step07h_full_recipe_base_report.md` L51–L67 (QNT, POR,
  INST, ENTITY, EVT, STATE, SPLIT, RXN, WARN, HYP, SIM, KINETIC, GRAPH/CLM…).
  `recipe_quantity_mentions_v1` (4,281,956 rows) exists in `ledgers/recipe_semantics/` per the report (L36) but that
  directory is NOT on this machine (ctx.md).
- ING ledger fields vs CanonicalIngredient: has canonical_name, parent_ids (854/5,387 non-empty), crosswalks
  {fdc, flavordb, foodon, recipedb}, facets (only `form` on 616), scientific_identity_status (UNKNOWN for all 5,387),
  verification (UNVERIFIED for all 5,387). Crosswalks: fdc/flavordb/recipedb **UNRESOLVED_EXTERNAL for 5,387/5,387**;
  FoodOn LINKED 1,147, CANDIDATE 572, NO_MATCH 1,540, UNRESOLVED_EXTERNAL 2,128. Missing vs §257C: food_category,
  known_forms/known_states (as lists), portion_profile_ids, chemistry_link_ids, human_verified, version_created.
- ALIAS ledger: alias_type SYNONYM 2,708 / TRANSLATION 1,463 / PLURAL 12; language en 2,720 + 13 Indic languages
  (hi 172, ta 156, ml 143, bn 141, …); region GB 2,127, IN 1,463, null 593; link_band EXACT/HIGH/MEDIUM. Missing vs
  §257C: source_count (has corpus_frequency), source_domains, first_seen_version.
- PROC ledger: kind ACTION 534 / ENDPOINT 18; 18 families; has required_condition_axes, mechanism_families,
  evidence_coverage — richer than anything in §257C (§257C has no Process entity at all).
- Provenance enum adopted in repo = §239.1 8-value (`registry/provenance_class_registry_v1.csv`;
  `reports/h_state/state_representation_contract_v1.md` L51); plus a separate value_origin registry
  (`registry/value_origin_registry_v1.csv`: MEASURED/REPORTED/DERIVED_DETERMINISTIC/SOURCE_IMPUTED/
  SOURCE_IMPUTATION_POSSIBLE/UNKNOWN); condition axes use MEASURED/RANGE/UNKNOWN/NOT_APPLICABLE (state contract L11).
- EVD row (EVD-000001) already carries censoring (`derived.retention_factor.censor {kind: GT_CAP, limit 97.5}`),
  `design`, `origin_type`, `tier`, `study_ids`, `study_id_status` (NOT_IDENTIFIABLE), `independence_group`,
  `measurement_method_id`, `provenance.locator` (line-level) — richer than EvidenceAtom on censoring/design, but no
  `doi`, `table_or_figure` as separate fields (locator string instead).
- EXP ledger fields: card_path, command, compute, hypothesis, notes, results_path, run_status … **lacks**
  research_question_id, code_commit, dataset/split/schema/ontology versions, baselines, seeds, CIs, decision,
  next_dependency required by §257A.20.
- C1–C18: `docs/BUILD_TRACKER.md` L12–L32 (dated 2026-10-18, after S056) reports a v1 prototype of all 18 modules
  (11 ✅, 7 🟡 incl. C9 "not routed (G16-TRANS not passed: gains vanish cold)"). These were built during the earlier
  DEL-1..5 course track over EVD, before the 36-step spine; they are not evidence that Step 36 is done (status
  UNVERIFIED beyond the tracker's own claims; I did not run tests).
- `src/culinarystate/quantity/normalize.py` L6: "count / volume -> grams: only with a POR- record (none supplied yet)
  -> UNKNOWN (Q6)" — consistent with §257A.2 step 6–7; no PortionProfile data exist.

---

## 2. Models and baseline ladders (simple → strong → advanced)

The annex contains **no model-family ladders** of its own; it contains cost/escalation ladders and a promotion rule.
- **Annotation cost ladder** (§257A.17 L28363–28366): deterministic parser/regex/unit logic → smaller semantic model
  for routine cases → stronger LLM for ambiguous → human only for high-value unresolved. Track: cost per raw recipe,
  per accepted Silver recipe, per human-verified Gold-Light example, human minutes per adjudicated Deep-Gold recipe,
  re-annotation rate, validator failure rate (L28372–28377). Premise: "The project is predominantly
  data/evidence-limited" (L28360).
- **Quantity conversion ladder** (§257A.2 step 6 L27993–27999) — effectively the "model" ladder for mass: authoritative
  lookups first, empirical corpus distribution, model estimate last and only if the task permits.
- **Evidence route ladder** implied by C8→C9 (§231.2 L25207–25208; MVP L28504): direct evidence → gated Level-15
  fallback; decision outputs ALLOW/WARN/QUALITATIVE/ABSTAIN (C14) and ASK mode (§257A.10 L28236).
- **Universal promotion rule** (identical in all 18 contracts, e.g. L28585): "the module is promoted only if it
  improves the relevant downstream or module-specific gate against the **strongest simpler baseline**; otherwise
  retain the simpler implementation." The *identity* of the strongest simpler baseline per module is NOT given in
  §257B (only §231.2 hints: C6 "hybrid lexical/dense/structured/graph"; C10 "LLM may propose; verifier decides";
  C16 "verbalize; do not invent second analysis").
- **Process granularity** as an experiment-controlled choice (L28074): canonical leaves split only if an experiment
  requires — i.e. the baseline is the coarser leaf+modifier representation.
- Representation-related: none here (see §235.7 L25556–25570 quantity encoder z_q with masks — outside range).

---

## 3. Experiments / hypotheses / RQs

The annex defines the *form* of experiments, not specific RQs:
- Experiment record template §257A.20 (19 fields, listed §1.7). Every experiment requires research_question_id,
  baselines, seeds, CIs and a KEEP/MODIFY/DROP/NEED_DATA decision (L28430).
- Implicit experiments/hypotheses embedded in the annex:
  - E-A1 (process granularity): do separate canonical leaves for modifier variants (chop fine/rough; pan/deep fry)
    improve any downstream task vs leaf+modifier? (L28068–28074).
  - E-A2 (quantity): structural parsing accuracy on the 33 hard expressions + conversion-status correctness (no
    fabricated grams) (L28007–28047); interval calibration where distributional (cf. G16-QTY L27452–27453).
  - E-A3 (cascade): oracle-upstream vs predicted-upstream performance for every module (L28558–28559) — cascade-error
    measurement is mandatory, not optional.
  - E-A4 (source-disjoint) reporting for every module (L28578).
  - E-A5 (cost curve): cost/human minutes per tier (L28372–28377) and active-learning annotation curve (figure 8,
    L28464).
  - E-A6 (MVP end-to-end scenario) §257A.24 L28493–28511 — one real recipe/session through the whole chain.
- Paper artefacts (§257A.22 L28453–28476): 10 figures (architecture; data-tier/provenance; recipe state graph;
  quantity conversion flow; evidence packet; risk–coverage/calibration; RAG baseline/ablation; active-learning curve;
  transition evidence-support map; FlavorTwin static vs process-conditioned) and 7 tables (dataset stats by
  source/cuisine/process; vocabulary/quantity coverage; semantic parser metrics; retrieval/citation metrics;
  decision/abstention metrics; Level-15 integration; RQ decision register).
- RQ16 identities live in §247 / §257E / §257L (outside range).

---

## 4. Gates, promotion and stop rules (exact)

The annex contains **no numeric thresholds**. Every gate-like statement is qualitative or refers to "declared"
thresholds defined nowhere in the range.

| ID / anchor | Exact text (abridged only where marked) | Line |
|---|---|---|
| Promotion rule (C1–C18) | "promoted only if it improves the relevant downstream or module-specific gate against the strongest simpler baseline; otherwise retain the simpler implementation" | L28585 (+17 copies to L29333) |
| Result-to-decision POSITIVE | "promote only if gain survives required cold/source split and uncertainty." | L28437–28438 |
| NULL | "prefer simpler baseline unless another strong benefit (calibration/latency/provenance) exists." | L28440–28441 |
| NEGATIVE | "record and drop/modify architecture; do not hide." | L28443–28444 |
| INCONCLUSIVE | "identify whether cause is data power, label ambiguity, leakage, implementation or model inadequacy." | L28446–28447 |
| DATA-LIMITED | "stop model escalation and acquire/curate evidence." | L28449–28450 |
| Split freeze | "7 freeze split registry / 8 never move examples after looking at final test performance" | L28337–28338 |
| Split order | groups assigned "before train/val/calibration/test split" (note: **4 partitions incl. calibration**) | L28336 |
| Vocab review | "above a declared frequency threshold and remains unresolved" (threshold undeclared) | L27951 |
| Quantity | model estimate "only if task explicitly permits"; output UNKNOWN if unsupported | L27999, L28004 |
| Evidence | "LLM knowledge is never a scientific evidence source." | L28104 |
| Multilingual entry | 5 conditions all required | L28165–28171 |
| Professor API | 7-step procedure ending "freeze a new evidence/data version before experiments" | L28398–28406 |
| Anti-creep | "Defer unless core gates pass": full POMDP/RL; long-horizon planner; universal neural world model; atomistic reaction generation across all recipes; broad PDE heat/mass simulation; multimodal stack; mobile polish; SaaS billing/auth; multilingual rollout without benchmarks; preference optimisation without sensory data | L28480–28491 |
| Completion checklist | 21 boxes, incl. "gold is independently annotated", "duplicate/source leakage is controlled", "quantity conversions expose their evidence class", "unknown chemistry remains unknown", "confidence is calibrated rather than self-reported", "transition model is gated by Level-15 results", "negative results are recorded", "FlavorTwin does not overclaim sensory equivalence", "Level 17 remains optional" | L28515–28537 |
| C9 | "only models that passed relevant G15 gates" | §231.2 L25208 |
| C18 | "direct current observation overrides old prediction on observable fields" | §231.2 L25217 |
| Related G16 gates (outside range, for reference) | G16-DATA L27446, G16-VOCAB L27449 ("below declared threshold"), G16-QTY L27452, G16-SEM L27455 ("declared Deep-Gold thresholds"), G16-GRAPH L27458, G16-EVID L27461, G16-CONFLICT L27464, G16-CAL L27467, G16-TRANS L27470, G16-DEC L27473 — also numberless | L27442–27475 |

Stop rules embodied: DATA-LIMITED → stop escalation (L28449); anti-creep list (L28480); "never move examples after
looking at final test" (L28338). Status vs repo: EXP-000001 (DEL-2 transition models) note "SUPPORTED on random split
only; NOT supported under cold-start" (`ledgers/data/EXP.jsonl`) → under L28437 this is NOT promotable, consistent
with C9 unrouted in BUILD_TRACKER L23.

---

## 5. Data requirements and named sources (licence notes)

The annex names almost no specific sources:
- FoodOn and FDC appear only as field names (`foodon_id` L29846, `fdc_ids` L29856). No LanguaL/FoodEx2/GS1 field.
- "authoritative exact portion / authoritative density / other approved national table" (L27994–27996) — no table is
  named (USDA FNDDS/SR portion tables, FAO/INFOODS density DB etc. would be candidates — UNVERIFIED here; another
  reader/researcher should confirm which national tables are licensable).
- Professor-provided APIs (§257A.19 L28396–28406) — CoSyLab/Foodoscope per repo (`tests/unit/test_foodoscope_client.py`
  exists; ctx.md: D-015 licence ASSUMED/DERIVED_ONLY).
- Licence requirements: Recipe.license_class (L29392), release "license/redistribution notes" (L28354). No licence
  field on EvidenceAtom, Alias, PortionProfile (provenance only). Repo SRC has `licence`, `licence_status`,
  `storage_rule` — exceeds annex.
- Data requirements implied:
  - Portion/density records per (ingredient, state, form, size_class, packing, locale) with sample_count and
    source_diversity (PortionProfile). Currently 0 POR records.
  - Per-row evidence capture list L28108–28121 (13 items) — the de-facto acquisition spec for Steps 10–14.
  - Locale/measurement-system metadata per source (L28153–28155) — needed to resolve cup/tbsp variants.
  - Recipe source snapshot date (release field L28350) — not a Recipe field.

---

## 6. Dependencies on other levels/steps

- §257A.15 depends on L16 identity (§192.5 `duplicate_group_id`), L13E lineage (§271.5) — per
  `reports/step07i/plan_authority_inventory.md` L25–L28.
- C9 depends on Level-15 G15 gates (§215; §231.2 L25208) and G16-TRANS (L27470).
- C6/C7/C8 depend on EvidenceAtom + COND compatibility (Steps 05/07/12–15) and on precomputed indexes (§257A.18
  L28384–28392: entity embeddings, evidence-atom embeddings, BM25, ontology adjacency, common conversions, **study
  lineage**, versioned cached packets) → study lineage (Step 08) is a runtime-latency dependency too.
- C3/C4/C18 depend on Event/Entity/State (Steps 16–20).
- C2 depends on CanonicalIngredient/Alias (Step 07H/07I vocab, NER/linker block closed S128).
- C10/C11 depend on the failure/recovery ontology (§257A.9) + rejection registry (§257A.12) + tool/medium ledgers.
- InverseDesignTrial depends on a forward model with OOD + prediction_interval (Steps 29–34) and FlavorTwin boundary
  (Step 36 "later FlavorTwin").
- §257A.16 release semantics depends on a split registry (none frozen: SPLIT ledger BLOCKED; 07I-R gate
  `human_gates_pending` includes 400-pair duplicate calibration packet, `reports/step07i/step07ir_gate_result.json`).
- §257A.20 depends on a research_question registry (§247/§257E) and code_commit capture.

---

## 7. Risks / failure modes

R1 **Contract illusion**: §257B and §257C look comprehensive (≈2,900 lines) but carry ~3% unique content. Teams may
   believe types/enums are specified when they are not → schema drift between Steps 03/04/16/17.
R2 **Provenance-enum divergence** (§9 C1): three vocabularies (§239.1, §257A.4, §257A.14). If Step 03 freezes the
   §239 8-value set (as the repo has), CONFLICTING and NOT_APPLICABLE have no provenance home at the field level →
   either NULL misuse (violates L29345) or conflicts collapsed silently (violates G16-CONFLICT L27464).
R3 **EXTERNAL_VERIFIED semantic drift**: SSOT uses it for "the referenced database/study reports" (L28304–28305,
   L28133), while the repo registry defines it as "checked against the cited source by an independent human or
   authority" (`registry/provenance_class_registry_v1.csv` row 3) and labels USDA R6 rows EXPLICIT_SOURCE. Claim
   language (§257A.14) generated from repo enums would say "The study measured…" for database aggregates.
R4 **Scalar normalized mass**: Quantity has only `normalized_mass_g`/`normalized_volume_ml` (L30250–30269); §257A.2
   step 7 requires interval/distribution output (L28003). Implementers will collapse intervals to point values.
R5 **Reference-quantity blindness**: "half the reserved sauce", "remaining batter", "juice of 1/2 lemon" (L28042–28044,
   L28023) require a reference to an Entity or a part-of relation; Quantity/IngredientMention have no such field.
R6 **Event condition under-specification**: Event has single `temperature_C`, `duration_s`, `pressure`, `pH`,
   `moisture_condition`, `medium`; no setpoint vs product-temperature distinction, no aw, oxygen, geometry/size,
   heat-transfer mode/power, lid/cover, agitation, vessel material — but the repo COND profile already includes many
   (state contract L11) and mechanism applicability (Step 23) and simulation (Steps 26–27) need them.
R7 **Missing InstructionStep/Process/Tool/Condition/Study entities** in §257C — Step 16 "instruction semantic schema"
   has no field dictionary to inherit; STUDY/EXPERIMENT/SAMPLE hierarchy (brief §18) is absent (EvidenceAtom has
   only study_id + independence_group).
R8 **EvidenceAtom gaps vs §257A.5**: no basis (wet/dry/yield), no replicates/n/SD/SE, no censoring, no before/after
   pairing or trajectory id, no extraction_method, no licence — though §257A.5 L28108–28121 mandates capturing them.
R9 **Split partitions**: §257A.15 names four partitions incl. calibration (L28336); if Step 15/29 builds only
   train/val/test, C14/G16-CAL calibration on held-out independent gold (L27467) leaks into val/test.
R10 **Template families not yet built**: §257A.15 step 5 "identify source-domain/template families" (L28335) has
   no artefact in 07I-R (grep finds only the inventory restatement); near-duplicates through site templates can
   leak across splits.
R11 **"Course" framing staleness**: §257A.23–25 speak of "course scope" / "course system complete" (L28478, L28515)
   — a semester-project frame; the 36-step research spine is larger. Anti-creep list remains valid but "complete"
   checklist is not a research-completion gate.
R12 **Cascade evaluation burden**: oracle+predicted-upstream evaluation for 18 modules (L28558–28559) requires
   gold at every interface; without Gold Event/State, C3/C4/C18 cannot be evaluated (EVT/STATE ledgers empty).
R13 **Cost tracking missing**: §257A.17 metrics not instrumented in repo (no ledger/report found; UNVERIFIED beyond
   grep of registry/ledgers).
R14 **Undeclared thresholds**: "declared frequency threshold" (L27951), G16-VOCAB/SEM "declared" thresholds — risk
   of post-hoc threshold setting (violates "no post-hoc gate weakening" law) unless pre-registered.

---

## 8. MAPPING TO THE 36-STEP SPINE (reconstructed; not quoted from the missing plan)

| Step | What this annex material requires |
|---|---|
| 01 Freeze authority | Record that §257B/§257C are template expansions of §231.2/§238; authority for per-module rules = §231.2; for field names = §238≡§257C; types = to be decided. Record the three provenance vocabularies and which one is authoritative (needs a DECISIONS entry; currently none found — D-001..D-025 not checked in detail, UNVERIFIED). |
| 02 Audit state | Use §257A.25 checklist (L28517–28537) as audit rubric; record C1–C18 prototype status from BUILD_TRACKER L12–32 as PROTOTYPE (pre-spine), not spine completion. Note missing ledgers QNT/POR/INST/ENTITY/EVT/STATE/SPLIT/CLM. |
| 03 Freeze state semantics | **Must** resolve field-status enum: adopt §257A.4 10-value set (or §239 8 + CONFLICTING + NOT_APPLICABLE + INTERPOLATED) and a mapping table to §239/§257A.14 claim language. Define State fields (§257C.State L30776–30957) with types, units, observability flags, per-field provenance (State.16) and uncertainty (State.17) representation; separate identity (CanonicalIngredient) from state (form/physical/thermal/texture). Output: state schema JSON + enum registry + mapping. Gate: every State field has type, unit, missingness codes, provenance enum; NOT_APPLICABLE vs UNKNOWN test cases. |
| 04 Evidence/provenance/similarity contracts | Freeze EvidenceAtom (23 fields) **extended** with §257A.5 capture items (basis, replicates/n, dispersion, censoring, before/after/trajectory id, extraction_method, licence) and STUDY→EXPERIMENT→SAMPLE→MEASUREMENT links; fix EXTERNAL_VERIFIED semantics; freeze claim-language templates §257A.14 and DISALLOWED_CLAIMS §257A.13; firewall §257A.6 as validator rule. Output: evd schema v2 + validator. |
| 05 Normalize EVD | Map existing EVD (57,280 ledger / 17,978 export) onto EvidenceAtom fields; populate `evidence_class`, `independence_group`, `table_or_figure` (split from provenance.locator), `doi`. Gate: no row lacks source span/locator; no LLM-only rows (L28104). |
| 06 Source acquisition manifest | Rank sources by §257A.5 hierarchy (primary > curated DB > SR/MA > review-context-only > secondary-lead-only); record licence/redistribution (L28354); professor-API procedure §257A.19. Add "approved national portion/density tables" as acquisition targets for PortionProfile (none acquired). |
| 07 Condition & measurement normalization | Event condition fields (temperature_C/raw, duration_s/raw, pressure, pH, moisture_condition, medium) must be derivable from COND; keep raw + normalised (L30564–30603); measurement units/basis for EvidenceAtom.11. Pending human audit (step07h_human_gate_result NOT_COUNTED_PROVENANCE_INVALID per ctx.md) blocks claiming condition fields are verified. |
| 08 Scientific source lineage | Supply `study_id`, `source_id`, `doi`, `independence_group` (EvidenceAtom.15–17, .22) and the study-lineage cache required by §257A.18 L28391; lineage must support "do not cite a review as the primary experiment" (L28295) → need review→primary links. (Not to be executed in this run.) |
| 09 Extraction & verification machinery | Enforce "LLM knowledge is never evidence" (L28104); extraction_method + human verification status per row (L28120–28121); claim of AI_PRECHECKED ≠ human verified; module obligations (typed contract, rejection reasons, replay) apply to extractors too. |
| 10 20-row mechanism pilot | Pilot must exercise all 13 capture items of L28108–28121 incl. trajectories and basis; measure field completeness per item. |
| 11 Wave-1 verified evidence | Human verification status per row; independence_group assigned; conflicts recorded as CONFLICTING, not resolved. |
| 12 Structured database evidence | Curated DBs = tier 2 of the hierarchy; must "retain primary provenance" (L28100) — DB rows without traceable primary study get study_id_status NOT_IDENTIFIABLE (as EVD-000001) and cannot support study-disjoint claims. |
| 13 Literature discovery corpus | Reviews = tier 4 (context only) / secondary = tier 5 (lead only): corpus must tag document type so reviews never become measurement rows. |
| 14 Coverage-driven growth | Prioritise by data-support map (§257A.19 step 6 L28405) and DATA-LIMITED rule (L28449): acquisition is the response to model failure. |
| 15 Freeze DATA-EVIDENCE v1 | Release must declare the 10 §257A.16 fields incl. split registry hash; split built by §257A.15 order with **train/val/calibration/test** (L28336); never move after test (L28338). Also feed §257A.22 table 1/2. |
| 16 Instruction semantic schema | Must define the entities that §257C lacks: InstructionStep (raw text, step index, span), Process leaf/family/modifiers (§257A.3 modifiers: intensity, geometry, granularity, medium, endpoint), Tool, intra-recipe reference/part-of relations; Event (20 fields) + Entity (10) + State (18) types; split/merge/reserve/discard graph ops (§239.1 rule 18 L26140). Decide leaf vs modifier granularity by experiment (L28074). |
| 17 Instruction-level extraction | Cost ladder §257A.17 (deterministic → small model → strong LLM → human); track the 6 cost metrics; per-field error logging (L29349); source-disjoint and long-tail reporting (L28578–28579); handle 33 quantity hard cases + "eggs, beaten" event-in-ingredient-line. |
| 18 Event-sourcing engine | C3/C4/C18 contracts: event order immutable except adjudication (L25203); new versioned state graph per update (L29295); deterministic replay; validator rules §240.2 (no consumption before existence etc., L26277–26279). Entity.created_by_event / destroyed_or_consumed_by_event mandatory. |
| 19 Gold state-trajectory pilot | Gold for State fields with per-field provenance; independent annotation (L28520); oracle-upstream test sets for C3/C4 (L28558). |
| 20 Scale procedural semantic corpus | Tiering & cost per accepted Silver recipe (L28373); masks/quality indicators per field for downstream models (L29350); do not annotate all 612k expensively (consistent with brief §31). |
| 21 Effect/mechanism ontology | Failure/recovery ontology §257A.9 (cause/symptom/recovery separate relations) belongs here or in 22; process family ids from §257A.3. |
| 22 Event→effect signatures | Event fields must carry what signatures key on (process_id + modifiers + medium + conditions + endpoint_states). Endpoint ("until golden") is an observation/stop criterion, not a duration. |
| 23 Applicability engine | C7 rule "unknown condition != mismatch" (L25206); compatibility vector across food/process/state/condition/target; needs aw, oxygen, geometry not in Event (§10). |
| 24 Formula/model registry | `model_id`, `model_version`, `forward_model_version` referenced by ClaimLedger.6–7 and InverseDesignTrial.9 — registry ids must be stable and versioned. |
| 25 Parameter-compatibility retrieval | C6 hybrid index + precomputed indexes §257A.18; condition-compatible Recall@K (L25205). |
| 26–27 Simulator + validation | Claim language "The simulator predicts under its assumptions…" (L28316–28317); SIMULATED never in observed-gold tables (§240.2 L26290); anti-creep: "broad PDE heat/mass simulation" deferred (L28486) → supports a single focused simulator. |
| 28 E7 synthetic prior | SIMULATED/IMPUTED provenance enforced; never enters final real evaluation; release must flag. |
| 29 TRANSITION_BOOTSTRAP_V0 | C8 "retrieve before predict"; experiment records per §257A.20; POSITIVE only if gain survives cold/source split (L28437) — EXP-000001/2 already show cold-start failure. |
| 30 Tabular/sparsity bake-off | NULL rule (L28440): keep simpler baseline; record seeds/CIs. |
| 31–33 Physics features, kinetics, hybrid | Result-to-decision rules; DATA-LIMITED stop (L28449). |
| 34 Short rollout | Anti-creep: "long-horizon autonomous recipe planner", "universal neural cooking world model", "full POMDP/RL" deferred (L28482–28484) → rollout must stay short and gated. |
| 35 Representation ladder | DISALLOWED: structural similarity ≠ sensory equivalence (L28293); FlavorTwin figure "static vs process-conditioned" (L28466). |
| 36 Evidence compiler → CulinaryState-RAG → FlavorTwin | Entire §257B C1–C18; decision modes §257A.10; candidate-action schema §257A.11; rejection registry §257A.12; DISALLOWED_CLAIMS §257A.13; claim language §257A.14; latency/caching §257A.18; MVP scenario §257A.24 as the Step-36 acceptance demo; ClaimLedger (11 fields); InverseDesignTrial (16 fields) for later FlavorTwin; completion checklist §257A.25. Gates: G16-EVID/CONFLICT/CAL/TRANS/DEC (L27461–27474). Baselines: "strongest simpler baseline" per module must be named in the step card (not given by SSOT). |

---

## 9. Contradictions, stale items, underspecified parts, open questions

Contradictions
- **C1 Three provenance/field-status vocabularies.** §239.1 L26117–26125 (8: EXPLICIT_SOURCE, EXTERNAL_VERIFIED,
  DERIVED_DETERMINISTIC, INFERRED_LLM, MODEL_ESTIMATED, IMPUTED, SIMULATED, UNKNOWN) vs §257A.4 L28081–28090 (10:
  KNOWN_EXPLICIT, KNOWN_EXTERNAL, DETERMINISTICALLY_DERIVED, INFERRED, MODEL_ESTIMATED, IMPUTED, SIMULATED, UNKNOWN,
  CONFLICTING, NOT_APPLICABLE) vs §257A.14 L28301–28323 claim classes (EXPLICIT/MEASURED, EXTERNAL_VERIFIED,
  INTERPOLATED, MODEL_ESTIMATED, IMPUTED, SIMULATED, CONFLICTING, UNKNOWN). §257A itself mixes them
  (DERIVED_DETERMINISTIC at L27985, EXTERNAL_VERIFIED at L28133 vs KNOWN_* at L28081). Repo adopted §239.1. Needs a
  SSOT change request (PROPOSED_ONLY) + a frozen crosswalk: e.g. provenance (origin) ⟂ status (CONFLICTING/
  NOT_APPLICABLE are statuses, not origins) ⟂ claim-language class (INTERPOLATED is a retrieval/inference route).
- **C2 EXTERNAL_VERIFIED meaning** (SSOT "database/study reports" L28304–28305 vs repo "independently human checked").
- **C3 Quantity output form**: interval/distribution required (L28003) but Quantity has no interval fields for
  normalised mass (only PortionProfile has mass_low_g/high_g). Also Quantity.lower/upper are raw-range bounds, not
  conversion uncertainty.
- **C4 Lookup ladder vs Q-ladder**: §257A.2 "other approved national table" (L27996) has no Q-level in §235.3; Q0
  EXACT_PHYSICAL is step 4 not step 6. PortionProfile.conversion_class enum not defined — use Q0–Q6 + a rank for
  "national table" (needs decision).
- **C5 Split partitions**: §257A.15 includes calibration (L28336); check whether other SSOT split sections (§264,
  §257E.13) and the repo state contract define 3 or 4 partitions — UNVERIFIED in this reader.

Stale / framing
- "course scope" / "course system complete" (L28478, L28515) and "Level 17 remains optional" (L28537): course-era frame.
- §257B "18-module registry" written for a semester runtime; BUILD_TRACKER shows prototypes already exist from
  DEL-1..5 (2026-10-18) — the spine's Step 36 should re-evaluate them, not assume rebuild-from-zero.
- §257A.19 assumes "professor-provided APIs" pending (also SSOT header L5 "professor API endpoints still pending").

Underspecified
- U1 No types/enums/units/nullability for any of 210 fields (§257C and §238 both boilerplate).
- U2 Enums named but undefined: canonicalization_status (presumably §257A.1 step-4 outcomes — not stated),
  alias_type, quantity_type, conversion_class, source_type, entity_type, evidence_class, relation (EvidenceAtom.4),
  claim_type, confidence_class, verification(_status), annotation_tier, role, physical/visual/thermal/texture_state.
- U3 No "strongest simpler baseline" named per module.
- U4 No numeric thresholds anywhere (L27951 "declared", G16 "declared").
- U5 Process leaf granularity left to "ontology granularity"/"if justified" (L28068–28069).
- U6 Template-family detection method (L28335) unspecified.
- U7 `timestamp` in State (L30808) vs `event_index` — wall-clock vs logical time not defined; recipes rarely give
  absolute times; cumulative elapsed time (needed for kinetics) has no field.
- U8 Entity.quantity_state_id (L30756) references a "quantity state" type that is not defined anywhere in §257C.
- U9 State.chemical_state_ref (L30918) — target of reference undefined (EvidenceAtom? SIM? KINETIC?).
- U10 EvidenceAtom.conditions (L31030) — structured vs free; must be the COND id.

Open questions needing external research
- Q1 Which authoritative portion/density tables are usable and licensable (USDA FNDDS portion weights, USDA SR
  Legacy measures, FAO/INFOODS density database, UK McCance & Widdowson, Indian IFCT)? Licence and coverage per
  locale (UNVERIFIED; for the research agent).
- Q2 Ontology alignment target(s) for CanonicalIngredient beyond FoodOn/FDC: LanguaL facets, EFSA FoodEx2 facets —
  do they offer form/state/cut/processing facets that match §257A.1 factorisation? (brief §14).
- Q3 Process ontology candidates for §257A.3 (FoodOn process branch, LanguaL "cooking method" facet, FoodEx2
  process facets) and whether modifiers (intensity/granularity) have standard representations.
- Q4 Standard provenance models to resolve C1 (W3C PROV-O; evidence/assertion ontologies such as ECO) — whether to
  split origin vs status vs claim route.
- Q5 Calibration-split sizing for C14/G16-CAL selective prediction (conformal/risk-coverage literature).
- Q6 Evidence-atom schema comparators (e.g. food-composition data interchange standards such as INFOODS/EuroFIR
  component/value metadata incl. basis, method, n, SD) to fill EvidenceAtom gaps.

---

## 10. LOOK-AHEAD: fields that earlier steps must capture

For Steps 03/04 (schema freeze)
- Separate **origin provenance** enum, **field status** (CONFLICTING, NOT_APPLICABLE, UNKNOWN) and **claim route**
  (DIRECT/INTERPOLATED/MODEL/SIMULATED) as three orthogonal fields; every State/Event/Quantity field gets all three
  plus an uncertainty object (point/interval/distribution/censored) — needed by C3, C14, C17 claim language.
- Mask/quality indicator per field (L29350) as a first-class column for Step 30–35 models.
- Typed ids with version (`*_version` / `schema_version`) on every persisted record (C-obligation L28552).
- EvidenceAtom additions: `basis` (wet/dry/yield-corrected/per-serving), `n_replicates`, `dispersion` (SD/SE/CI +
  type), `censoring` (kind, limit), `pair_id`/`trajectory_id` + time point, `extraction_method`, `licence`,
  `experiment_id`, `sample_id`, `measurement_platform`, `conflict_group_id`, `primary_or_review` document type.
- ClaimLedger additions: `claim_route` (§257A.14 class), `disallowed_claim_checks`, `evidence_packet_id`,
  `conflict_ids`.

For Steps 05/07 (EVD + conditions)
- Condition fields at the granularity Event needs: setpoint vs product/core temperature; temperature profile or
  ramp; time-at-temperature; medium (water/oil/steam/air/dry pan); heat-transfer mode; pressure; pH; aw; oxygen/
  packaging; geometry/size/thickness; agitation; lid; vessel material; each axis MEASURED/RANGE/UNKNOWN/
  NOT_APPLICABLE (already in the state contract L11 — keep and add setpoint/product distinction).
- Raw + normalised for every condition (Event.temperature_raw / duration_raw pattern L30574, L30594).
- Locale/measurement system per source and per recipe (L28153–28155) for gas mark / °F / cup variants.

For Step 08 (lineage — not executed now)
- study_id, source_id, doi, table_or_figure, source_span, independence_group, review→primary links (for L28295),
  publication year (temporal splits), lab/platform group (platform-disjoint splits); study-lineage cache artefact
  for runtime (L28391).

For Step 09 (verification machinery)
- verification status enum distinguishing UNVERIFIED / AI_PRECHECKED / HUMAN_VERIFIED / ADJUDICATED; verifier id;
  extraction method/model+prompt version (release field L28351).

For Steps 10–15 (acquisition)
- All 13 capture items of L28108–28121; explicit `before`/`after` with matched basis; trajectories retained as
  series, not collapsed to endpoints (Steps 32 kinetics, 27 validation need them).
- Food state/form of the matrix (raw/blanched/frozen; whole/diced) using the SAME form/state vocabularies as
  IngredientMention.form/state, so C7 can match recipe state to evidence matrix.
- Process leaf/family ids from the same PROC ledger as Event.process_id.
- Portion/density acquisition (currently 0 POR rows) with state/form/size_class/packing/locale, sample_count,
  source_diversity (PortionProfile L30290–30471) — needed by Quantity normalisation for any mass-based features
  (Steps 30–35) and FlavorTwin quantity weighting.
- Split metadata for Step 15: duplicate group, recipe family, **template family** (L28335), source domain,
  study/publication/platform group; four partitions incl. calibration.

For Steps 16–20 (procedure/state)
- Recipe additions: raw ingredient-line and instruction text references (Recipe has only title_raw), `family_id`
  (repo REC has it; §257C has only duplicate_group_id), source publication/snapshot date, author/source-template id
  (L13E + template families), split group id.
- IngredientMention additions: geographic qualifier and compound-food flag (parsed in §257A.1 step 2 but no field);
  facet slots seen in examples: salt_state, source_state vs current state, colour; language/locale; negation;
  embedded events ("beaten", "thawed and squeezed dry") linked to Event ids; canonicalization_status =
  §257A.1 7-way enum.
- Quantity additions: normalised mass/volume **interval or distribution** + conversion_class (Q-ladder) +
  evidence class (L28523); `reference_entity_id` and `fraction_of` for intra-recipe references (L28042–28044);
  `part_of` relation (juice/zest of lemon L28023–28024); multiplier (2 x 200 g) explicitly; packing qualifiers.
- Event additions: process family, modifiers typed by §257A.3 axes (intensity, geometry, granularity, medium,
  endpoint), `endpoint_states` as stop criterion vs observation; cumulative elapsed time; heat-transfer mode;
  repetition/loop markers; parallel-branch markers; link to InstructionStep id.
- Entity: entity_type must cover ingredient instance, intermediate, mixture, reserved portion, discarded portion,
  tool-bound contents; quantity_state type defined.
- State: observability flag per field (C18 rule L25217 needs to know which fields are "observable"; repo SVAR has
  `observable_in_session`), cumulative thermal history pointer, composition (water/fat/protein/sugar fractions or
  reference) for later mechanism applicability; timestamp semantics.
- Failure/recovery annotations (§257A.9) as separate cause/symptom/recovery relations if Step 36 DIAGNOSE/RECOVER
  modes are to be evaluated.

For Steps 24–36 (consumers) — ids that must be stable from the start
- model_id/model_version/forward_model_version (ClaimLedger.6–7; InverseDesignTrial.9); evidence_distance and
  OOD_flag definitions shared by C9/C14/InverseDesignTrial (L31414–31424); response_id/session ids (ClaimLedger.2).
- Experiment registry (EXP ledger) must be extended to §257A.20's 19 fields before Steps 29–34 run, otherwise
  result-to-decision rules (L28434–28451) cannot be audited.
