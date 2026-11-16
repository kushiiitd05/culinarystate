# SSOT section 238 conformance table (T9-C06-R1)

Status: **AI_DRAFTED / PROPOSED** (S178 GOVDOC lane, 9 Nov 2026, manjot-server, HEAD `4a95380` plus uncommitted work). The mapping of each SSOT field to a schema property is the agent's reading and is **not human-verified**; every row that is not an exact name match carries a reason. Counts are counts only (no recipe text, no values). Machine-readable twin: `reports/s178/ssot238_conformance.csv` (210 rows, one per SSOT field).

**What was compared.** SSOT v15 section 238 "Exact data contracts / field dictionary" (L25745-26101): 12 contracts, 210 fields (field lists parsed from the SSOT text; each field's description in the SSOT is the same generic sentence, so the field *names* are the contract). Against: the JSON Schemas in `ledgers/schemas/` (REC, ING, ALIAS, QNT, POR, EVT, ENTITY, STATE, EVD, CLM, plus COND, IMAP, GRAPH where a field lives on a linked record), the committed tables `ledgers/recipe_base/recipe_base_v1.parquet` and `ledgers/recipe_identity/recipe_identity_fk_v1.parquet` (612,782 rows each), and the code-level interfaces `extraction/interfaces.py`, `state_graph/event_log.py`, `generation/claims.py`.

**Map kinds.** EXACT = same name in the schema. RENAMED = the equivalent property under another name. COMPOSED = covered by several properties or a provenance block. RELATED = nearest property, semantics differ or the link is held on another record (reason given). TABLE_ONLY / CODE_ONLY = the field exists only as a column of a committed table / only as a code interface field, not in a JSON Schema. ABSENT = no counterpart anywhere (reason given).

**Counts.** Populated = ACTIVE rows, latest version per id, with a non-null, non-empty value at that property (ledgers), or non-null non-empty column values (tables). The REC ledger holds 89,565 recipes while `recipe_base_v1` holds 612,782, so Recipe rows quote two different denominators; the column `count_artifact` names which. "0 rows" means the schema exists and no `ledgers/data/<NAME>.jsonl` exists.

## 1. Result

- 210 fields: **25 EXACT + 58 RENAMED + 9 COMPOSED = 92** map to a schema property; 65 RELATED; 5 TABLE_ONLY and 7 CODE_ONLY; **41 ABSENT**.
- **0 rows are unmapped without a stated reason** (the script asserts it; every ABSENT, RELATED, TABLE_ONLY and CODE_ONLY row has a reason).
- Contracts with no JSON Schema at all: **IngredientMention** (19 fields; only the 17a code interface exists, the MENTION ledger is a draft, and `recipe_ingredient_mentions_v1.parquet` is not visible on manjot, see T7-C01-R5) and **InverseDesignTrial** (16 fields, all ABSENT; belongs to FlavorTwin, out of the course scope).
- Schemas that exist but have **0 production rows**: QNT (Quantity), POR (PortionProfile), EVT (Event), ENTITY, STATE, CLM (ClaimLedger). The Rung A event log and the rc2 quantity results live in derived files and counts-only reports, not in these ledgers.
- Populated ledgers: REC 89,565, ING 2,048 ACTIVE, ALIAS 4,103 ACTIVE, EVD 17,978 ACTIVE.

## 2. Concrete conformance gaps found (for the report and for the Mac/manjot tickets)

1. **PortionProfile.** `POR.basis` enum is MEASURED / DATABASE / CONVENTION / RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION. The composition/ plan for SR Legacy portions names basis `SR_PORTION` (board T3-C08-R1), which is not in the enum, and POR has no `sample_count`, `source_diversity` or `size_class`. A POR export from `composition/` would fail schema validation as it stands. Decision needed on the schema (v1.1) before the Mac exports POR records.
2. **ClaimLedger.** CLM is a research-claim ledger (`statement`, `approval`, `gate_ids`, `experiment_ids`). The SSOT contract is an answer-level claim ledger (`response_id`, `model_id`, `model_version`, `confidence_class`, `citation_required`, `citation_refs`). `claim_type` is the same name with a different vocabulary (DESCRIPTIVE/COMPARATIVE/CAUSAL/SOTA/NEGATIVE_RESULT vs answer-claim kinds). Six of eleven fields are ABSENT. This is what T8-C17-R1 (claim_ledger schema for D5 answers) and T9-C06-R2 (runtime-only or materialise) have to settle; it is not a rename.
3. **Recipe.** Five fields exist only as columns of `recipe_base_v1` / `recipe_identity_fk_v1`, not in `REC.schema.json` (`dataset_version`, `license_class`, `language`, `locale`, `duplicate_group_id`); three more are approximated by table columns (`source_domain`, `dish_categories`, `annotation_tier`) and `annotation_model` is spread over four version columns. Five are ABSENT: `title_normalized`, `servings_raw`, `servings_normalized`, `prompt_version`, `validation_flags`. The statement "recipe contract implemented" is true only of the table, not of the schema.
4. **State.** Eight of 18 State fields (temperature, moisture, water activity, pH, physical/visual/thermal/texture state) can only live in `STATE.variables[SVAR id]`, and the matching registry rows (SVAR-FUT-001 moisture, -002 water activity, -005 phase, -007 texture, -008 colour, -012 surface/core temperature, -013 pH) are all `SVAR-FUT` with 0 rows in `registry/state_variable_registry_v1.csv` (30 of its 254 rows are FUT). No populated variable exists for them today.
5. **Event.** The condition fields (temperature, duration, pressure, pH, moisture, medium) are not on EVT; they are reached through `EVT.condition_id -> COND`. Any consumer of the contract has to join.
6. **Alias.** `source_domains` is ABSENT; `source_count` is approximated by `corpus_frequency` (populated on 2,207 of 4,103 ACTIVE aliases, 53.8 %).
7. **CanonicalIngredient.** `scientific_name` and `fdc_ids` are mapped but 0 of 2,048 ACTIVE ingredients populate them; `food_category` 631 (30.8 %), `parent_id` 315 (15.4 %), `known_forms` 235 (11.5 %), `known_states` 0.
8. **Entity.** Lineage (`parent_entity_ids`, `created_by_event`, `destroyed_or_consumed_by_event`) lives in event allocations (code) and on STATE, not on ENTITY.

## 3. Per-contract tables


### Recipe  (schema: REC; 26 fields; ABSENT 5, COMPOSED 2, EXACT 2, RELATED 7, RENAMED 5, TABLE_ONLY 5)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `recipe_id` | RENAMED | REC.id | recipe_base_v1.parquet:recipe_id | 89565/89565 (100.0%) |  |
| `dataset_version` | TABLE_ONLY | (none) | recipe_base_v1.parquet:source_version | 612782/612782 (100.0%) | REC has no dataset-version property; the table column is the source's version |
| `source_id` | COMPOSED | REC.provenance.source_ids | recipe_base_v1.parquet:source_id | 89565/89565 (100.0%) |  |
| `source_url` | EXACT | REC.source_url | (table has raw_recipe_pointer only) | 89565/89565 (100.0%) | table omits the URL by design (licence) |
| `source_domain` | RELATED | (none) | recipe_base_v1.parquet:source_family | 612782/612782 (100.0%) | table column is the corpus family, not a URL domain; the domain is derivable only from REC.source_url |
| `license_class` | TABLE_ONLY | (none) | recipe_base_v1.parquet:licence_status | 612782/612782 (100.0%) | REC has no licence property |
| `source_checksum` | RENAMED | REC.content_sha256 | recipe_base_v1.parquet:raw_hash | 89565/89565 (100.0%) |  |
| `title_raw` | RENAMED | REC.title | recipe_base_v1.parquet:title_raw | 89565/89565 (100.0%) |  |
| `title_normalized` | ABSENT | (none) | (none) | n/a | no normalised-title column was ever written (project law: normalisation is a new column; none built) |
| `language` | TABLE_ONLY | (none) | recipe_base_v1.parquet:language | 612782/612782 (100.0%) | REC has no language property |
| `locale` | TABLE_ONLY | (none) | recipe_base_v1.parquet:locale | 612782/612782 (100.0%) | REC has no locale property |
| `cuisine_labels` | RENAMED | REC.cuisine | recipe_base_v1.parquet:cuisine_if_explicit | 60144/89565 (67.2%) |  |
| `dish_categories` | RELATED | (none) | recipe_identity_fk_v1.parquet:dish_family_candidate_id | 198273/612782 (32.4%) | candidate dish-family id, not category labels |
| `servings_raw` | ABSENT | (none) | (none) | n/a | no step extracts servings; no REC property or table column |
| `servings_normalized` | ABSENT | (none) | (none) | n/a | as servings_raw |
| `ingredient_mention_ids` | RELATED | REC.n_ingredient_lines | (none) | 89565/89565 (100.0%) | only the count of ingredient lines is carried; the mention ledger is not materialised (see IngredientMention) |
| `event_ids` | RELATED | (none; GRAPH.event_ids) | (none) | 0 rows | the link is held on the GRAPH record (0 ledger rows), not on REC |
| `entity_ids` | RELATED | (none; ENTITY.recipe_id) | (none) | 0 rows | reverse link only: ENTITY.recipe_id (0 ledger rows) |
| `recipe_graph_id` | RELATED | (none; GRAPH.recipe_id) | (none) | 0 rows | reverse link only: GRAPH.recipe_id (0 ledger rows) |
| `duplicate_group_id` | TABLE_ONLY | (none) | recipe_identity_fk_v1.parquet:duplicate_group_id | 612782/612782 (100.0%) | identity tables, not REC |
| `annotation_tier` | RELATED | (none) | recipe_base_v1.parquet:quality_tier | 612782/612782 (100.0%) | quality tier registry label, not the SSOT annotation tier vocabulary |
| `annotation_model` | COMPOSED | (none) | recipe_base_v1.parquet:ner_version + linker_version + parser_version + normalizer_version | 612782/612782 (100.0%) | four version columns instead of one model field; rule/NER stages |
| `prompt_version` | ABSENT | (none) | (none) | n/a | no LLM prompt version is recorded for recipe annotation; production stages are rules/NER (parser_version, ner_version) |
| `schema_version` | EXACT | REC.schema_version | (none) | 89565/89565 (100.0%) |  |
| `validation_status` | RENAMED | REC.verification.status | recipe_base_v1.parquet:human_verification_status | 89565/89565 (100.0%) |  |
| `validation_flags` | ABSENT | (none) | (none) | n/a | no per-recipe flag list; validator issue codes exist only in counts-only reports |

### IngredientMention  (schema: none; 19 fields; ABSENT 3, CODE_ONLY 6, RELATED 10)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `mention_id` | CODE_ONLY | (no schema) | extraction/interfaces.py Mention.mention_id | n/a | code-level interface only |
| `recipe_id` | RELATED | QNT.recipe_id (line-level record) | interfaces SourceText.text_id | n/a | QNT is a line record, not a mention record |
| `raw_text` | RELATED | QNT.raw | interfaces SourceText.raw | n/a | nearest property; semantics differ or the link is held on another record |
| `source_span` | RELATED | QNT.span | interfaces Mention.span (Span) | n/a | nearest property; semantics differ or the link is held on another record |
| `canonical_ingredient_id` | RELATED | QNT.ingredient_id | interfaces LinkResult.selected_id | n/a | nearest property; semantics differ or the link is held on another record |
| `candidate_ids` | CODE_ONLY | (no schema; ALIAS.candidate_ingredient_ids is alias-level) | interfaces LinkResult.candidates (concept_id) | n/a | code-level interface only |
| `variety` | CODE_ONLY | (no schema; ING.facets.variety is canonical-level) | interfaces Mention.attributes (ValueClaim.field) | n/a | attribute claims, not a fixed field |
| `form` | CODE_ONLY | (no schema; ING.facets.form is canonical-level) | interfaces Mention.attributes | n/a | code-level interface only |
| `state` | CODE_ONLY | (no schema; ING.facets.prep_state is canonical-level) | interfaces Mention.attributes | n/a | code-level interface only |
| `size` | RELATED | QNT.parsed.size | interfaces Mention.attributes | n/a | nearest property; semantics differ or the link is held on another record |
| `quantity_id` | RELATED | QNT.id | interfaces QuantityParseResult.result_id | n/a | nearest property; semantics differ or the link is held on another record |
| `role` | ABSENT | (none) | (none) | n/a | no extractor for ingredient role (main/garnish) exists |
| `optional` | RELATED | QNT.qualifiers (string list) | (none) | n/a | carried as a qualifier string, not a boolean |
| `divided` | RELATED | QNT.qualifiers (string list) | (none) | n/a | as optional |
| `reserved` | RELATED | QNT.qualifiers (string list) | (none) | n/a | as optional; reserved portions are never implicit by design (D-074) |
| `brand` | ABSENT | (none) | (none) | n/a | no extractor for brand |
| `canonicalization_status` | RELATED | ALIAS.link_band | interfaces LinkResult.failure / selected_id is None | n/a | alias link band is per alias, not per mention |
| `provenance` | CODE_ONLY | (no schema; QNT.provenance is the nearest) | interfaces Provenance | n/a | code-level interface only |
| `annotation_confidence_features` | ABSENT | (none) | (none) | n/a | the confidence vector (decision/confidence.py) is answer-level; no per-mention features recorded |

### CanonicalIngredient  (schema: ING; 17 fields; EXACT 2, RELATED 5, RENAMED 10)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `ingredient_id` | RENAMED | ING.id |  | 2048/2048 (100.0%) |  |
| `preferred_name` | RENAMED | ING.canonical_name |  | 2048/2048 (100.0%) |  |
| `food_category` | RENAMED | ING.category |  | 631/2048 (30.8%) |  |
| `parent_id` | RENAMED | ING.parent_ids (list) |  | 315/2048 (15.4%) | single id in SSOT, list in the schema |
| `scientific_name` | EXACT | ING.scientific_name |  | 0/2048 (0.0%) |  |
| `foodon_id` | RENAMED | ING.crosswalks.foodon.external_id |  | 849/2048 (41.5%) |  |
| `fdc_ids` | RENAMED | ING.crosswalks.fdc.external_id |  | 0/2048 (0.0%) | single external id in the schema (list in SSOT) |
| `aliases` | RELATED | (reverse: ALIAS.ingredient_id) |  | 4103/4103 (100.0%) | held in the ALIAS ledger, not on ING |
| `regional_aliases` | RELATED | (reverse: ALIAS.region) |  | 3515/4103 (85.7%) | as aliases |
| `languages` | RELATED | (reverse: ALIAS.language) |  | 4103/4103 (100.0%) | as aliases |
| `known_forms` | RENAMED | ING.facets.form |  | 235/2048 (11.5%) |  |
| `known_states` | RENAMED | ING.facets.prep_state |  | 0/2048 (0.0%) |  |
| `portion_profile_ids` | RELATED | (reverse: POR.ingredient_id) |  | 0 rows | POR has 0 ledger rows |
| `chemistry_link_ids` | RELATED | (reverse: IMAP.ingredient_id) |  | 30294/30294 (100.0%) | held in the IMAP ledger (rows counted are IMAP rows with an ingredient id) |
| `status` | EXACT | ING.status |  | 2048/2048 (100.0%) |  |
| `version_created` | RENAMED | ING.created_at (and ING.version) |  | 2048/2048 (100.0%) |  |
| `human_verified` | RENAMED | ING.verification.status |  | 2048/2048 (100.0%) | status enum, not boolean |

### Alias  (schema: ALIAS; 10 fields; ABSENT 1, EXACT 4, RELATED 3, RENAMED 2)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `alias_id` | RENAMED | ALIAS.id |  | 4103/4103 (100.0%) |  |
| `surface` | EXACT | ALIAS.surface |  | 4103/4103 (100.0%) |  |
| `canonical_ingredient_id` | RENAMED | ALIAS.ingredient_id |  | 4103/4103 (100.0%) | null when the alias is ambiguous (candidate_ingredient_ids holds the options) |
| `language` | EXACT | ALIAS.language |  | 4103/4103 (100.0%) |  |
| `locale` | RELATED | ALIAS.region |  | 3515/4103 (85.7%) | region, not a locale code |
| `alias_type` | EXACT | ALIAS.alias_type |  | 4103/4103 (100.0%) |  |
| `source_count` | RELATED | ALIAS.corpus_frequency |  | 2207/4103 (53.8%) | corpus frequency, not a count of sources |
| `source_domains` | ABSENT | (none) | (none) | n/a | ALIAS carries corpus_frequency only; no domain list |
| `verification` | EXACT | ALIAS.verification |  | 4103/4103 (100.0%) |  |
| `first_seen_version` | RELATED | ALIAS.created_at (and ALIAS.version) |  | 4103/4103 (100.0%) | creation time/version of the record, not first corpus version |

### Quantity  (schema: QNT; 22 fields; ABSENT 1, EXACT 2, RELATED 6, RENAMED 13)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `quantity_id` | RENAMED | QNT.id |  | 0 rows |  |
| `raw_text` | RENAMED | QNT.raw |  | 0 rows |  |
| `quantity_type` | RENAMED | QNT.parsed.kind |  | 0 rows | enum NUMBER/RANGE/FRACTION/MIXED/MULTIPLIER/PACKAGE/QUALITATIVE/NONE |
| `value` | RENAMED | QNT.parsed.value |  | 0 rows |  |
| `lower` | RENAMED | QNT.parsed.low |  | 0 rows |  |
| `upper` | RENAMED | QNT.parsed.high |  | 0 rows |  |
| `fraction` | RELATED | QNT.parsed.value (kind FRACTION / MIXED) |  | 0 rows | no separate fraction field; fractions are kinds of value |
| `count` | EXACT | QNT.count |  | 0 rows |  |
| `unit_id` | RENAMED | QNT.parsed.unit_id |  | 0 rows |  |
| `unit_locale` | RENAMED | QNT.locale |  | 0 rows |  |
| `size` | RENAMED | QNT.parsed.size |  | 0 rows |  |
| `packing` | RELATED | QNT.parsed.package_size |  | 0 rows | package size, not packing (POR.packing exists on the portion record) |
| `container` | ABSENT | (none) | (none) | n/a | no container property in QNT |
| `approximate` | RELATED | QNT.parsed.qualifier |  | 0 rows | qualifier string, not a boolean |
| `qualitative_term` | RENAMED | QNT.parsed.qualifier / normalized.qualitative |  | 0 rows |  |
| `optional` | RELATED | QNT.qualifiers (string list) |  | 0 rows | nearest property; semantics differ or the link is held on another record |
| `divided` | RELATED | QNT.qualifiers (string list) |  | 0 rows | nearest property; semantics differ or the link is held on another record |
| `reserved` | RELATED | QNT.qualifiers (string list) |  | 0 rows | nearest property; semantics differ or the link is held on another record |
| `normalized_mass_g` | RENAMED | QNT.mass_g |  | 0 rows |  |
| `normalized_volume_ml` | RENAMED | QNT.volume_ml |  | 0 rows |  |
| `conversion_record_id` | RENAMED | QNT.portion_id (+ conversion_method, conversion_path) |  | 0 rows |  |
| `provenance` | EXACT | QNT.provenance |  | 0 rows |  |

### PortionProfile  (schema: POR; 18 fields; ABSENT 3, COMPOSED 1, EXACT 4, RELATED 3, RENAMED 7)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `portion_profile_id` | RENAMED | POR.id |  | 0 rows |  |
| `ingredient_id` | EXACT | POR.ingredient_id |  | 0 rows |  |
| `state` | RELATED | POR.form |  | 0 rows | no separate prep-state property |
| `form` | EXACT | POR.form |  | 0 rows |  |
| `size_class` | ABSENT | (none) | (none) | n/a | POR has no size property; SR portion size words are not modelled (Mac ticket A5 concerns size words) |
| `packing` | EXACT | POR.packing |  | 0 rows |  |
| `portion_value` | RELATED | POR.from_unit_id |  | 0 rows | value is implicit 1 per from_unit_id |
| `portion_unit` | RENAMED | POR.from_unit_id |  | 0 rows |  |
| `unit_locale` | RENAMED | POR.locale |  | 0 rows |  |
| `mass_g` | RENAMED | POR.grams_per_unit.value |  | 0 rows |  |
| `mass_low_g` | RENAMED | POR.grams_per_unit.low |  | 0 rows |  |
| `mass_high_g` | RENAMED | POR.grams_per_unit.high |  | 0 rows |  |
| `conversion_class` | RELATED | QNT.conversion_method (on the quantity record) |  | 0 rows | not on POR |
| `source_type` | RENAMED | POR.basis |  | 0 rows | POR.basis enum is MEASURED / DATABASE / CONVENTION / RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION; the composition/ plan names basis SR_PORTION, which is NOT in the enum (conformance gap) |
| `source_record` | COMPOSED | POR.provenance.source_ids / provenance.locator |  | 0 rows |  |
| `sample_count` | ABSENT | (none) | (none) | n/a | no sample_count property; the composition/ POR candidates need one (board T3-C08-R1) |
| `source_diversity` | ABSENT | (none) | (none) | n/a | no property |
| `verification` | EXACT | POR.verification |  | 0 rows |  |

### Event  (schema: EVT; 20 fields; ABSENT 1, CODE_ONLY 1, COMPOSED 1, EXACT 4, RELATED 10, RENAMED 3)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `event_id` | RENAMED | EVT.id | state_graph/event_log.py EngineEvent.event_id | 0 rows |  |
| `recipe_id` | EXACT | EVT.recipe_id |  | 0 rows |  |
| `event_index` | COMPOSED | EVT.step_index + EVT.ordinal | EngineEvent.order | 0 rows |  |
| `process_id` | EXACT | EVT.process_id |  | 0 rows |  |
| `process_modifiers` | CODE_ONLY | (none) | EngineEvent.attributes | 0 rows | EVT has no modifiers property (EVD.process.modifiers is evidence-side) |
| `input_entity_ids` | RELATED | EVT.input_state_ids | EngineEvent.consumes | 0 rows | state ids, not entity ids |
| `output_entity_ids` | RELATED | EVT.output_state_ids | EngineEvent.produces | 0 rows | state ids, not entity ids |
| `tool_ids` | EXACT | EVT.tool_ids |  | 0 rows |  |
| `medium` | RELATED | EVT.condition_id -> COND.medium |  | 0 rows | held on the condition record |
| `temperature_C` | RELATED | EVT.condition_id -> COND.temperatures |  | 0 rows | held on the condition record |
| `temperature_raw` | RELATED | EVT.condition_id -> COND.temperatures (raw) |  | 0 rows | held on the condition record |
| `duration_s` | RELATED | EVT.condition_id -> COND.duration |  | 0 rows | held on the condition record |
| `duration_raw` | RELATED | EVT.condition_id -> COND.duration (raw) |  | 0 rows | held on the condition record |
| `pressure` | RELATED | EVT.condition_id -> COND.pressure |  | 0 rows | held on the condition record |
| `pH` | RELATED | EVT.condition_id -> COND.ph_initial / ph_final |  | 0 rows | held on the condition record |
| `moisture_condition` | RELATED | EVT.condition_id -> COND.moisture |  | 0 rows | held on the condition record |
| `endpoint_states` | RENAMED | EVT.endpoint |  | 0 rows | single string in the schema |
| `source_span` | RENAMED | EVT.span |  | 0 rows |  |
| `provenance` | EXACT | EVT.provenance |  | 0 rows |  |
| `validation_flags` | ABSENT | (none) | (none) | n/a | no flags property; replay/validator issue codes appear in counts-only reports |

### Entity  (schema: ENTITY; 10 fields; ABSENT 4, EXACT 1, RELATED 1, RENAMED 4)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `entity_id` | RENAMED | ENTITY.id |  | 0 rows |  |
| `recipe_id` | EXACT | ENTITY.recipe_id |  | 0 rows |  |
| `entity_type` | RENAMED | ENTITY.kind |  | 0 rows | enum INGREDIENT_LOT/INTERMEDIATE/TOOL_CONTENTS/FINAL_DISH/DISCARD/UNKNOWN |
| `canonical_food_id` | RENAMED | ENTITY.ingredient_id |  | 0 rows |  |
| `name` | RENAMED | ENTITY.label |  | 0 rows |  |
| `parent_entity_ids` | ABSENT | (none) | state_graph/event_log.py Allocation.parent / child | n/a | lineage lives in event allocations (code), not on the entity record |
| `created_by_event` | RELATED | (reverse: STATE.produced_by_event_id) |  | 0 rows | held on the state record |
| `destroyed_or_consumed_by_event` | ABSENT | (none) | EngineEvent.consumes / discards | n/a | no property on ENTITY |
| `quantity_state_id` | ABSENT | (none; reverse STATE.entity_id) |  | n/a | link is by STATE.entity_id |
| `current_state_id` | ABSENT | (none; reverse STATE.entity_id, max state_version) |  | n/a | derived by query, not stored |

### State  (schema: STATE; 18 fields; ABSENT 1, COMPOSED 1, EXACT 2, RELATED 11, RENAMED 3)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `state_id` | RENAMED | STATE.id |  | 0 rows |  |
| `entity_id` | EXACT | STATE.entity_id |  | 0 rows |  |
| `event_index` | RELATED | STATE.produced_by_event_id (+ state_version) |  | 0 rows | event id, not index |
| `timestamp` | ABSENT | (none) | (none) | n/a | no clock; ordering by state_version only |
| `form` | EXACT | STATE.form |  | 0 rows |  |
| `physical_state` | RELATED | STATE.variables[SVAR id] |  | 0 rows | state variables are keyed by SVAR id; the nearest registry row is SVAR-FUT-005 phase (future, 0 rows) |
| `visual_state` | RELATED | STATE.variables[SVAR id] |  | 0 rows | SVAR-FUT-008 colour (future, 0 rows) |
| `thermal_state` | RELATED | STATE.variables[SVAR id] |  | 0 rows | nearest registry row is SVAR-FUT-012 surface/core temperature (future, 0 rows) |
| `texture_state` | RELATED | STATE.variables[SVAR id] |  | 0 rows | SVAR-FUT-007 texture (future, 0 rows) |
| `temperature_C` | RELATED | STATE.variables[SVAR id] |  | 0 rows | SVAR-FUT-012 surface/core temperature (future, 0 rows); no ACTIVE temperature SVAR |
| `moisture` | RELATED | STATE.variables[SVAR id] |  | 0 rows | SVAR-FUT-001 moisture content (future, 0 rows) |
| `water_activity` | RELATED | STATE.variables[SVAR id] |  | 0 rows | SVAR-FUT-002 water activity (future, 0 rows) |
| `pH` | RELATED | STATE.variables[SVAR id] |  | 0 rows | SVAR-FUT-013 pH / acidity (future, 0 rows) |
| `quantity_mass_g` | RENAMED | STATE.quantity |  | 0 rows |  |
| `chemical_state_ref` | COMPOSED | STATE.variables[SVAR id] (chemical SVARs) |  | 0 rows |  |
| `field_provenance` | RELATED | STATE.provenance |  | 0 rows | record-level only, not per field |
| `uncertainty` | RENAMED | STATE.variables.*.uncertainty |  | 0 rows |  |
| `observation_source` | RELATED | STATE.belief |  | 0 rows | enum PREDICTED/OBSERVED/PLANNED |

### EvidenceAtom  (schema: EVD; 23 fields; COMPOSED 4, EXACT 3, RELATED 7, RENAMED 9)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `evidence_id` | RENAMED | EVD.id |  | 17978/17978 (100.0%) |  |
| `subject_type` | RELATED | (implicit: EVD.matrix is an ingredient matrix) |  | n/a | EVD is a fixed matrix/process/target triple; no subject_type property |
| `subject_id` | RELATED | EVD.matrix.ingredient_id |  | 11569/17978 (64.4%) | nearest property; EVD fixes the subject as an ingredient matrix |
| `relation` | RELATED | EVD.derived.direction |  | 17978/17978 (100.0%) | direction enum, not a free relation |
| `object_type` | RELATED | (implicit: EVD.target) |  | n/a | no object_type property |
| `object_id` | RELATED | EVD.target.state_variable_id |  | 17978/17978 (100.0%) | the object is always a state variable |
| `process_id` | RENAMED | EVD.process.process_id |  | 17821/17978 (99.1%) |  |
| `conditions` | RENAMED | EVD.process.condition_id |  | 17978/17978 (100.0%) |  |
| `measurement_target` | RENAMED | EVD.target.state_variable_id / target.raw_name |  | 17978/17978 (100.0%) |  |
| `measurement_value` | COMPOSED | EVD.before / after / derived |  | 17978/17978 (100.0%) | counted: any of after.value or a derived value is populated |
| `measurement_unit` | RENAMED | EVD.after.unit |  | 3870/17978 (21.5%) |  |
| `metric` | COMPOSED | EVD.derived.{delta, percent_change, retention_factor, log_fold_change, yield_factor} |  | 17482/17978 (97.2%) |  |
| `matrix_description` | RENAMED | EVD.matrix.raw_name (+ food_group, form, ...) |  | 17978/17978 (100.0%) |  |
| `analytical_method` | RENAMED | EVD.measurement_method_id |  | 14108/17978 (78.5%) |  |
| `study_id` | RENAMED | EVD.study_ids |  | 3870/17978 (21.5%) |  |
| `source_id` | EXACT | EVD.source_id |  | 17978/17978 (100.0%) |  |
| `doi` | RELATED | (via SRC / STUDY records) |  | n/a | no DOI property on EVD |
| `table_or_figure` | COMPOSED | EVD.provenance.locator |  | 17978/17978 (100.0%) |  |
| `source_span` | RELATED | EVD.provenance.locator |  | 17978/17978 (100.0%) | locator string, not a character span |
| `evidence_class` | RENAMED | EVD.tier |  | 17978/17978 (100.0%) | E1-E7 |
| `verification` | EXACT | EVD.verification |  | 17978/17978 (100.0%) |  |
| `independence_group` | EXACT | EVD.independence_group |  | 17978/17978 (100.0%) |  |
| `quality_features` | COMPOSED | EVD.applicability / design / censored / n_replicates |  | 17978/17978 (100.0%) |  |

### ClaimLedger  (schema: CLM; 11 fields; ABSENT 6, EXACT 1, RELATED 2, RENAMED 2)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `claim_id` | RENAMED | CLM.id |  | 0 rows |  |
| `response_id` | ABSENT | (none) | (none) | n/a | CLM is a research-claim ledger (statement, approval, gate_ids); it has no answer/response link |
| `claim_text` | RENAMED | CLM.statement |  | 0 rows |  |
| `claim_type` | RELATED | CLM.claim_type |  | 0 rows | same name, different vocabulary: CLM enum is DESCRIPTIVE/COMPARATIVE/CAUSAL/SOTA/NEGATIVE_RESULT (a research claim kind), not an answer-claim kind (numeric, directional, ...) |
| `evidence_ids` | EXACT | CLM.evidence_ids |  | 0 rows |  |
| `model_id` | ABSENT | (none) | (none) | n/a | no model id on CLM |
| `model_version` | ABSENT | (none) | (none) | n/a | no model version on CLM |
| `confidence_class` | ABSENT | (none) | decision/confidence.py (runtime confidence vector, ordinal) | n/a | not a ledger field |
| `citation_required` | ABSENT | (none) | (none) | n/a | claim checking is runtime (generation/claims.py check_claims); nothing persisted |
| `citation_refs` | ABSENT | (none) | generation/claims.py CIT regex output (runtime) | n/a | runtime only |
| `verification_status` | RELATED | CLM.approval (DRAFT/HUMAN_APPROVED/REJECTED) and CLM.verification.status |  | 0 rows | nearest property; semantics differ or the link is held on another record |

### InverseDesignTrial  (schema: none; 16 fields; ABSENT 16)

| SSOT field | kind | schema property | table / code counterpart | populated | reason |
|---|---|---|---|---|---|
| `trial_id` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `initial_state_id` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `target_state` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `candidate_ingredient_ids` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `candidate_process` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `candidate_conditions` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `constraints` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `optimizer` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `forward_model_version` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `predicted_state` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `prediction_interval` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `evidence_distance` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `OOD_flag` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `feasible_flag` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `heldout_or_real_outcome` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |
| `target_error` | ABSENT | (no schema) | (none) | n/a | no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor) |

## 4. Limits

The mapping is an AI reading of names and schema descriptions; two readers could place some RELATED rows differently. The SSOT gives no per-field semantics beyond the field name, so "conforms" here means "a property with the same job exists", not "values agree". No schema validation of the populated rows was run in this lane (the ledger rules in `src/culinarystate/ledgers/rules.py` are the existing validators). Populated counts use ACTIVE latest versions only; DEPRECATED and SUPERSEDED records are excluded.
