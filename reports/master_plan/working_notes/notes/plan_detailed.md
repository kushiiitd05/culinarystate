# READER NOTES — plan_detailed

Scope read in full (bodies, not headings): `docs/plan/CulinaryState_Detailed_RnD_Execution_Plan_v2.md` (2,559 lines; cited **RD Lnnnn**), `docs/plan/S093_dataset_ledger_status_and_model_plan.md` (81 lines; **S093 Ln**), `docs/BACKLOG_NONBLOCKING.md` (12; **BL Ln**), `docs/RESOURCE_GAP_MAP.md` (49; **RGM Ln**), `docs/BUILD_TRACKER.md` (93; **BT Ln**), `docs/DONE_FROM_SSOT.md` (62; **DFS Ln**), `docs/simulator_data_contract.md` (8; **SDC Ln**).
Spot-verifications against SSOT v15 (**SSOT Lnnnnn**), WORKLOG, DECISIONS, Master Plan v4.0 (**MP Lnnnn**), registry/reports, cited where used. Nothing in the repo was modified.

**Status of this material in the authority stack.** `registry/plan_authority_map_v1.csv` row 7 classifies RD as "APPROVED_PLAN (implementation detail) … rank 5 (written against SSOT v14)", scope "recipe semantics NER/canonicalisation/quantity/state graph/leakage", steps "07I;B07;B08". S093 is row 8: "INFORMATIVE (stale counts)", rank 8. **Contradiction:** Master Plan v4.0 Part AG4 (MP L2742–2750) ranks "Detailed compiler/R&D plan" as #4, *above* "This master prompt / final execution plan" (#5). The authority map and the brief §2 put the master plan above it. Needs a human ruling (see §9).

RD self-description: v2.0, 3 Oct 2026; "Plan only. No model result, agreement score, cost measurement or superiority claim has been produced yet" (RD L7, L11). Baseline = SSOT v14 §§230–242, 245, 249, 252, 257A, 259 (RD L9). **Verified:** these section numbers still exist with the same titles in v15 (SSOT_INDEX: §230 at SSOT L25082, §236 L25587, §245 L26604, §245.12 L26667–26679, §249 L27442–27521, §252 L27585, §259 L42796). v15 adds §§260–279 (L13E, SSOT L42915–45655), which RD does not cover at all.

---

## 1. Definitions, entities and data contracts (field-level where given)

### 1.1 Naming conventions (RD L57–72)
- P0–P10 compiler stages; A0–A5 annotation *depth* (renamed from "D0–D5" to avoid v14 D-ladder clash); DEL-1…DEL-5 course deliverables; D0–D11 = v14 L15 transition ladder (untouched); B0–B5 RAG ladder (v14 §245); S1–S6 complexity *flags* (overlapping, not bins); E0–E13 main experiments; E14.x Jev experiments; J1–J5 JEPA; W0–W10 work packages; G-* gates; [S#] sources (S1–S72); R1–R32 primary-source checks (Appendix J).
- Evidence markers: [V] carried verification, [C] Report-A claim not rechecked, [P] project hypothesis, [U] unverified, [A-code] attachment-reported code audit awaiting reproduction, [R] primary page checked (RD L74–84).

### 1.2 Compiler stages P0–P10 (RD L253–269) — the canonical pipeline
| Stage | Retained output | Promotion gate (verbatim essence) |
|---|---|---|
| P0 Source contract | immutable recipe + manifest (source, rights, locale, checksums, duplicate family) | "Source and split lineage known" |
| P1 Text preparation | raw text + offset map; transliteration kept alongside original | "Every annotation maps back to raw text" |
| P2 Mention recognition | typed spans + attributes (food, amount, unit, form, state, action, tool, condition, endpoint) | Gold span/attribute performance |
| P3 Food/product linking | food IDs, modifiers, link type, candidates, or unresolved set | precision & coverage on held-out Gold |
| P4 Quantity structure | symbolic typed quantity expressions | structure exact match; unit validity |
| P5 Event parsing | event records, typed relations, process-ontology mapping | argument/condition/ordering accuracy |
| P6 Referential grounding | entity IDs or unresolved candidate sets | cross-step & implicit reference accuracy |
| P7 Entity-flow replay | versioned entity graph, state snapshots | replay & temporal integrity |
| P8 Quantity grounding/accounting | quantity ledger, uncertainty, residuals | evidence routes; accounting consistency |
| P9 Task sufficiency | capability vector + route | calibrated selective risk |
| P10 Scientific enrichment | evidence packet, claim ledger (joins DEL-1 registry) | scientific provenance, domain support |
"P3–P6 exchange information: this is not a waterfall. Corrections are new annotation **versions**" (RD L269). Report B's L0–L6 map onto P (RD L271–281).

Global rules (RD L314–321): (1) prediction precision never exceeds evidence precision; (2) Unknown ≠ mismatch, neutral in retrieval; (3) every stage replayable from raw text + versioned config (event-sourced); (4) LLM proposes; rules or *recalibrated* decision models decide; only humans commit Gold; (5) hard validity gates before confidence; (6) recipe text never becomes scientific evidence; (7) relational/JSON tables first; no graph DB/GNN until benchmarks justify.

### 1.3 Three identities (RD L327–333) — directly relevant to Step 03
1. **Food concept** (reusable vocabulary entry: garlic; garlic paste). 2. **Recipe entity / lot** (one ingredient lot, mixture, reserved portion in one recipe). 3. **Entity state version** (that entity at an event/time: form, location, thermal status, quantity refs). "Dicing does not create a new concept, but the later state must never overwrite the original mention."
Product rule (RD L352): a product earns a distinct concept when composition/processing/culinary meaning cannot be represented by base food + declared modifiers; relations `DERIVED_FROM`, `HAS_INGREDIENT`, `IS_VARIANT_OF`, each with own evidence; "Never decompose a purchased compound food into assumed ingredients." Worked boundary table RD L337–350 (onion facets; clove portion vs clove spice; sour cream/cream cheese as lexicalised product; tomato paste DERIVED_FROM tomato; corn flour/coriander locale-conditioned candidate sets; jeera/haldi/dhaniya aliases with FORM/PART resolving leaf vs seed; chicken stock compound; garlic powder ≠ fresh-garlic density; frozen spinach thawed+drained ≠ packaged mass; brand sauce formulation only if sourced; "half the reserved sauce" = portion reference, not new concept).

### 1.4 Vocabulary lifecycle (RD L371–377)
`PROPOSED → {ALIAS | MODIFIER_COMPOSITION | PRODUCT_CONCEPT | AMBIGUOUS | NON_FOOD} → REVIEWED → ACTIVE`. Per-entry record: approver, source examples, locale, external crosswalk version, negative examples. Monitor mention-weighted and unique-alias coverage, rare/regional coverage, mistaken merges, fragmentation, backlog. "v14's 10k-concept figure is a *scale hypothesis*, not a quota."
ID policy (RD L365–369): internal stable IDs primary; RecipeDB/FlavorDB IDs = course cross-reference + evaluation target; FoodOn = semantic/interoperability layer, versioned per snapshot; USDA FDC IDs **only** for composition/portion evidence, chosen by data type (Foundation / SR Legacy / FNDDS / Branded).

### 1.5 Annotation layers (RD L383–401)
- Ingredient-line spans: FOOD_MENTION · AMOUNT · UNIT · SIZE · FORM · PREP_STATE · TEMP · DRY_FRESH · VARIETY · PART · BRAND · PURPOSE · ALTERNATIVE · OPTIONAL · QUALITATIVE_AMOUNT · DIET (+ proposed PACKING, RD L1657, L1665).
- Instruction spans: ACTION · FOOD_MENTION · INTERMEDIATE_MENTION · TOOL · DURATION · HEAT/TEMPERATURE · ENDPOINT · FOOD_ACTION · TOOL_STATE · QUANTITY_IN_STEP (+ CONDITION, RD L1663).
- Mention qualifiers: optional · divided · reserved · approximate · additional · to_taste · as_needed · negated · hypothetical.
- Reference relations: REFERS_TO · PART_OF · DERIVED_FROM · SAME_LOT_AS · F-EQ.
- Event roles: INPUT · OUTPUT · TOOL · DESTINATION · MEDIUM · CONDITION · ENDPOINT.
- Flow ops: TRANSFORM · MERGE · SPLIT · TRANSFER · RESERVE · DISCARD · RECOMBINE · SERVE · WAIT (semantics RD L1781–1791).
- Temporal/control: BEFORE · DEPENDS_ON · PARALLEL_WITH · OPTIONAL_BRANCH · ALTERNATIVE_BRANCH · REPEAT_UNTIL.
- Quantity relations: AMOUNT_OF · FRACTION_OF · REMAINDER_OF · PACKAGE_CONTENT · ALLOCATED_TO.
- State fields: form · phase · location · qualitative thermal/texture/visual · "numeric only when supported".
- Annotation status: task mask · disagreements · adjudication · unresolved candidates · guideline version · assistance visible?
- Storage: raw char offsets (declare code-point vs byte); BIO/BILOU only inside models; nested/discontinuous spans explicit or declared exclusion (RD L398–401).
- Boundary rules per label RD L1644–1667 (e.g. DRY_FRESH "Absence is unstated, not fresh by default"; DURATION "'Until tender' is an endpoint, not a numeric duration"; ENDPOINT "Planned golden color is not observed golden color"; negated action annotated with negation attribute, replay rejects it RD L1684). Relation namespacing: concept-level DERIVED_FROM vs entity-level material lineage must be distinguished (RD L1688). Qualifiers & non-events table RD L1671–1682.
- Legacy adapters to RecipeDB 7 tags / TASTEset / r-FG (RD L405–418); adapter decisions logged.
- Schema versioning `LM-vMAJOR.MINOR.PATCH` (MAJOR = split/merge + migration + re-adjudication; MINOR = new child label; PATCH clarification). Each doc stores `labels_annotated_for = [...]`; never-annotated label scored as **missing annotation**, never `O` (RD L436–441).

### 1.6 Ledgers (RD §8, L574–599) — field-level
- **Ingredient/entity:** `concept_id, canonical_source, xrefs{}, lot/entity_id, version, raw_mention, char_span, surface_name, head_lemma, lang`, product/form/state facets, `parents[], location, lifecycle_status, link_band, link_p, candidates[], provenance, verification, guideline_version, model_versions{}`.
- **Quantity:** `quantity_id, entity_version_id, raw_qty_text`, symbolic `expression`, `value_min/max` (exact rationals), `is_range, multiplier, approximate, unit_raw, unit_canonical, unit_system, unit_variant, dimension, basis, kind, allocation{fraction,parent_qty}, conversion_path[{from,to,factor,source,evidence_id}], uncertainty{source_var,interval}, unresolved_reason`.
- **Event/state:** `event_id, step_id, text_order, depends_on[], event_type, action_raw, process_id, process_band, effect_class, inputs[], outputs[], tool_id, conditions{heat,temp_value/range,duration_min/max}, endpoint_text, trajectory, provenance, inference_rule_id, precedent_ids[]`, before/after entity versions.
- **Scientific evidence (DEL-1):** `study_id`, food/matrix/state/process, measurement basis, conditions, method, source table/span, evidence tier, verification.
- Entity lifecycle states: ACTIVE, RESERVED, INCORPORATED, DISCARDED, SERVED, UNRESOLVED. "Incorporation ≠ the material vanished… Heating ≠ a numeric composition change" (RD L584–585).
- DAG rules: text order and execution dependencies stored separately; "Repeat until smooth" is a control construct (no invented iteration count) (RD L587–590).
- **CI invariants (RD L592–599):** (1) explicit spans round-trip; (2) every ingredient-list lot accounted as used/optional/alternative/garnish/explicitly discarded/unresolved/apparently unused; (3) nothing consumed after DISCARD or before produced; (4) split fractions ≤1 per compatible basis; (5) mass balance only where every term known, else `unknown` not `fail`; (6) inferred events never feed explicit-only queries; (7) "Grams invented without an evidence route = 0".

### 1.7 Record families (Appendix B.2, RD L1511–1536)
source_asset (`source_asset_id`; URL/file identity, content hash), recipe (`recipe_id`; family, locale assertions), text view (`view_id`; raw hash, transformation version), mention, field assertion, food concept (registry revision), external mapping (internal ID, external snapshot, relation), lot/entity, entity version (prior version, producing event), quantity expression (AST, basis, source variable), conversion evidence (`conversion_record_id`), allocation, event, reference decision (candidates, cutoff), control construct, observation (session, reported time, target entity), model decision (`decision_id`; request hash, options, distribution), review issue, scientific row (`evidence_id`; study family, table/span, conditions), answer claim (`claim_id`). Canonical-form = versioned *view*, not a fourth physical ledger (RD L1536).

### 1.8 Field-level evidence wrapper (B.3, RD L1538–1562)
`assertion_id, owner_record_id, field, value, availability, epistemic_provenance, verification, trajectory, evidence_refs[], inference_rule_id, decision_id, calibrated_probability, guideline_version` + separate `evidence_origin` (rule / learned resolver / external precedent / human interpretation). Proposes new enum `INFERRED_RULE` "do not mislabel a deterministic rule's semantic guess as DERIVED_DETERMINISTIC" (RD L1562).

### 1.9 Missingness — four orthogonal axes (RD L681–690)
- Availability: PRESENT · NOT_STATED · NOT_MEASURED · BELOW_LOD · UNRESOLVED · NOT_APPLICABLE · CONFLICTING
- Epistemic provenance: EXPLICIT_SOURCE · EXTERNAL_VERIFIED · DERIVED_DETERMINISTIC · INFERRED_LLM · MODEL_ESTIMATED · IMPUTED · SIMULATED · CONVENTION
- Verification: UNREVIEWED · HUMAN_VERIFIED · DUAL_ADJUDICATED
- Trajectory: PLANNED · OBSERVED_SESSION · PREDICTED (implemented: `src/culinarystate/state_graph/engine.py:23`, `ledgers/registry.py:270`).
"A numeric zero requires evidence, and an absent concentration is not zero."

### 1.10 Offset/text-view contract (B.4, RD L1564–1572)
Half-open Python code-point intervals `[start,end)` within immutable UTF-8-decoded raw *section*; section ID stored (ingredient line 2 ≠ step 2); UTF-16 frontend translation; ordered non-overlapping multi-segment mentions; every normalization op records transformation kind + interval map (`½`→`1/2`); transliterated/translated views need alignment confidence; gloss cannot create raw-span Gold. Required fixtures: vulgar fractions, mixed numbers, en-dash ranges, accents, Devanagari, Hindi/English code mixing, NBSP, line breaks, repeated food names, emoji before a span.

### 1.11 Quantity AST & unit conventions (D.1–D.2, RD L1753–1777; §9 RD L603–647)
Node types: `RATIONAL, RANGE, ADD, MULTIPLY, FRACTION_OF, REMAINDER_OF, PACKAGE_CONTENT, ALTERNATIVE, QUALITATIVE, OPEN_AMOUNT, UNKNOWN`. `quantity_kind` separate from `dimension`. "500 g or 1 cup" = ALTERNATIVE (never multiply). Convention resolution order: explicit source definition → documented source-level convention → supported locale metadata; "Region is a prior, not a universal proof of cup size"; scenario envelope ≠ calibrated interval. Mass grounding preference: exact compatible portion record → reviewed ingredient/product/form-specific density/weight → clearly labelled category-level estimate *only if task permits*; strict route never accepts category approximation. **Temperature conversion is affine** (absolute: scale+offset; differences: scale only); scaling never multiplies oven temperature; household "cup" container → `CONTAINER_COUNT`. Three problems/evidence requirements (RD L605–609): same-dimension conversion (deterministic), culinary-unit interpretation (locale convention, `unit_variant` + interval), food-specific grounding (food, product, form, packing, size, basis + portion/density evidence: FDC by data type; JFC-style weight tables). Symbolic accounting `Q_after = Q_before + Q_added − Q_allocated − Q_discarded + ΔQ_process` is a contract, channels (mass, volume, count, dry basis, edible basis, source-origin allocation) never added without evidenced conversion (RD L634–640). Uncertainty stored once at source variable; split children correlated; parser, density, link uncertainty separate terms (RD L647; D.10 RD L1851–1853). Ingredient Parser adapter: disable water-density default; never copy `raw` hint into state; BM25 scores = rankings (RD L611–614).

### 1.12 Planned vs observed; offline vs online (RD L672–679; D.8 RD L1837–1839)
PLANNED (parsed procedure, intended endpoints) vs OBSERVED_SESSION; "Bake until golden" is a target. Offline full-document (later text may resolve earlier ambiguity, evidence span recorded) vs online prefix at step t (no future leakage; scored separately). Prefix state packet contents (RD L655–661): active entities + producing events; location, product/form, reservation status, symbolic quantities; relevant prior spans; unresolved alternatives.

### 1.13 Implicit/omitted (RD L663–670)
Four kinds: linguistically omitted participant (resolve from packet; most-recent compatible output only as baseline hypothesis; `provenance=inferred`), source-described prior preparation (annotate initial form; **no** explicit chop event), structural intermediate (mixture entity; distinguish from named "dough"), unstated customary action/condition (stays unknown; rule may emit `OMITTED_STEP_CANDIDATE` only if prerequisite absent **and** ≥1 retrieved training recipe states it explicitly; store `rule_id`, `precedent_ids`; never copy time/temp/quantity/chemistry into source ledgers).

### 1.14 Task sufficiency (P9, RD L728–746)
Capability vector `c_r = (food coverage, quantity structure, grounding, event coverage, reference closure, condition support, scientific support)`; return `READY · READY_WITH_LIMITS · NEEDS_CLARIFICATION · UNSUPPORTED · CONFLICTING` + missing critical fields; task→needs table (RD L736–744).

### 1.15 Issue codes (D.9, RD L1843)
`ALLOCATION_EXCEEDS_AVAILABLE, UNKNOWN_FRACTION_BASIS, AMBIGUOUS_LOT, UNPRODUCED_REFERENCE, DISCARDED_MATERIAL_REFERENCE, BRANCH_STATE_UNRESOLVED, SOURCE_AMOUNT_CONFLICT, INCOMPATIBLE_CONVERSION_EVIDENCE`, each with severity, affected fields, source evidence, suggested resolution. "A conflict never licenses code to silently clamp the fraction…" (RD L1845).

### 1.16 Picker reason codes (C.8, RD L1725–1737)
ACCEPT_EXISTING · ALIAS_PROPOSAL · PRODUCT_PROPOSAL · AMBIGUOUS_LOCALE · NO_VALID_CANDIDATE · NOT_STATED · UNRESOLVED_REFERENCE · CONFLICTING_SOURCE · NOT_APPLICABLE; "Do not use a generic OTHER to collapse all these outcomes."

### 1.17 Scientific evidence row (Appendix G, RD L2066–2103)
Row = one measurement or clearly defined aggregate from one study with food/matrix, initial form/state, process, conditions, analyte/target, unit, basis, method, uncertainty where reported, source table/span (RD L2068). Rows from one table = one study family for splits. "Verified" must say which of three tasks: transcription checked / food-process alignment checked / scientific comparability assessed (RD L2070). Compatibility = conjunction of food/product, part, form, edible/dry/wet basis, process family, conditions, target (RD L2074); "Unknown metadata is neutral for candidate discovery, but it cannot satisfy an evidence requirement for a quantitative claim" (RD L2076). Answer classes (RD L2088–2095): Observed study result · Deterministic derived result · Model estimate · Scenario/assumption · Qualitative procedural statement · Unsupported/conflicting. Claim ledger fields: `claim_type`, statement, supporting assertion/evidence IDs, calculation ID, applicability status, provenance, limitations (RD L2101).

### 1.18 Retrieval card contract (K.5, RD L2374)
Card: `chunk_id, record_id, record_revision, namespace, parent_id, raw_source_refs, view_text, view_hash, epistemic_type, verification, task_mask, split/family` + exact task fields; vector record adds model/version, dimension, task instruction, normalization, embedding timestamp, index snapshot. Distinct namespaces: concepts, recipe text/events, training exemplars, scientific evidence, project docs (RD L2304). Compatibility tri-state `COMPATIBLE / INCOMPATIBLE / INSUFFICIENT_INFORMATION` (RD L2429).

### 1.19 Provider-neutral decision envelope (E.2, RD L1865–1887)
`decision_family, schema_version, state_snapshot_id, evidence_cutoff{mode,step_index}, source_refs, question, options[{id,description}]` incl. `NO_VALID_CANDIDATE` and `UNRESOLVED`, `state`, `registry_snapshot`, `criteria_version`. Response stores selected option, full probabilities, raw provider confidence, model/version, tokens, time, validity flags, cache mode. Interfaces `prepare_text, extract_mentions, generate_concepts, select_option, parse_quantity, parse_events, resolve_reference, replay_event, ground_quantity, assess_sufficiency, render_answer` with failure results (RD L1576–1588); "never nearest-ID fallback".

### 1.20 Simulator data contract (SDC L1–8) — repo-implemented
Every transition input carries `source_class` ∈ {STRUCTURAL_RECIPE, COMPOSITION, MEASURED_TRANSITION, COMPILED_RETENTION, KINETIC, MOLECULAR_PRIOR, SENSORY_PRIOR, MODEL_GENERATED, SYNTHETIC} + `source_id, source_record_id, evidence_tier, process, conditions, initial/final_state_support, uncertainty, licence, provenance`. **Permanent rule:** STRUCTURAL_RECIPE may define that a process occurred, not its magnitude; only MEASURED_TRANSITION, COMPILED_RETENTION, KINETIC (or labelled MODEL_GENERATED/SYNTHETIC with stated uncertainty) carry magnitude; enforced by `TransitionInput` (tests/unit/test_external_data_policy.py). Ingest policy: LIVE_ONLY / DO_NOT_STORE / licence-unresolved / research-only rows cannot enter canonical ledgers (`sources/policy.py`). File `src/culinarystate/state_graph/source_class.py` verified present.

---

## 2. Models and baseline ladders (simple → strong → advanced)

### 2.1 SSOT promotion order (verified SSOT L27503–27519, §249.3)
Rules/lookup → strong simple baseline → structured model → learned model → agentic/optimization layer; "No stage is skipped merely because the later stage sounds more novel." BT L9–10 and S093 L4–5 restate the §257B promotion rule "keep only if it earns its place against the strongest simpler baseline".

### 2.2 NER (P2) roster (RD §15 L831–851; P2 hybrid RD L305–312)
Simple: deterministic quantity grammar + curated aliases; Stanford NER/CRF (reproduce 95.52); Ingredient Parser + adapter. Strong: spaCy-trf (95.90); DeBERTa-v3+CRF; RecipeBERT-KA/RecipeRoBERTa-KA (EACL 2026, "required current challenger"). Advanced/optional: GLiNER2/2.5 (zero-shot + fine-tuned), GLiNER2.5-Decide, kNN-NER layer, pinned frontier LLM verifier (only relabel/abstain within proposed spans; "may never invent spans", RD L312), local instruction model, Jev 1.13, JEPA variants.
**Repo reality (supersedes RD plan for NER):** TASTEset exact F1 rules 0.774 → BERT 0.919 / RoBERTa 0.925 / DeBERTa 0.922 → base+CRF 0.927, large+CRF 0.933 (S093 L43; BT L71; DFS L43); kNN-NER Δ=0 (null); GLiNER zero-shot 0.232 exact / 0.643 relaxed → fallback only (DFS L44); WORKLOG S125–S128: DeBERTa-base+CRF kept, router R6 frozen, BGE linker frozen, final TEST run once (ACCEPT err 2.13%/2.09%, coverage 0.59/0.72). NER block closed (ctx; S128 "no more model development"). Prospective V2-DM lane uses open System-One models (Tev1, Nimble) locally, not Jev (reports/ner_v2/systemone_decision_model_review.md L20–22).

### 2.3 Linking (P3) cascade (RD L354–363)
1 exact curated alias (only if unambiguous in locale) → 2 normalised alias → 3 fuzzy (char n-gram/token-set) → 4 dense bi-encoder top-20 (internal names + RecipeDB/FlavorDB IDs + FoodOn labels/synonyms/defs) → 5 cross-encoder rerank (gold pairs + hard negatives milk↔milk chocolate↔coconut milk) → 6 LLM selector top-5 with definitions, review band only → 7 calibration model over (rank, margin, alias type, frequency bucket, type/form compatibility, no-candidate signal) → 8 route accept/review/unresolved, always `NO_VALID_CANDIDATE`. Baselines to compare: FoodSEM, FoodOntoRAG-style, RecipeDB2 cosine ≥0.70 (E3.2–E3.3).
Repo: S094 leave-one-alias-out zero-shot: char TF-IDF Acc@1 0.555 / R@5 0.783; e5-large-v2 0.607 / 0.820; RRF 0.586 (S093 L73–79), paired +0.051 CI [0.014, 0.090]; S124 contrastive linker +0.035 Acc@1 over zero-shot e5 (WORKLOG S124). "Baseline to beat: current LineLinker… keep the bi-encoder only if it improves R@5 on rare/unseen foods without lowering Acc@1 on head" (S093 L57).

### 2.4 Reference resolution (P6) ladder (E4/E5, RD L1076–1093; §11.2 RD L708–720)
E4.1 recency+lexical → E4.2 contextual encoder/LLM same candidates → E4.3 + prefix packet + temporal/type constraints → E5.1 + role/path/allocation features → E5.2 + training-only structural exemplars (ARA) → E5.4 graph kernel/learned graph encoder **only if E5.1 shows remaining structural errors**. Antecedent score `s(r,e)=f(lexical, contextual, food compatibility, role, location, state, recency, graph path, allocation)`: "Start with rules and a small learned reranker; no hand-set weights" (RD L714). Hard rejections: not-yet-produced on branch, discarded, reserved without supported reference, double-spend.

### 2.5 Quantity (P4/P8) ladder (E6, RD L1095–1105)
Grammar vs Ingredient Parser (+adapter) vs LLM; conversion via USDA portions / JFC-style table; baseline Nutritional-Estimation (NER+Jaccard+unit mapping) [S66]. Repo: 74 units with cited authority (NIST, UK WMA, 21 CFR), grammar covers ~90% lines, symbolic qty, POR evidence partial (DFS L12; BT L43); FDC crosswalk CANDIDATE-only, FDC portions become POR only after human verification (DECISIONS D-006).

### 2.6 Silver/teacher economics (E7, RD L1107–1115)
One-pass LLM → staged packets (§7.6) → small-model cascade (GLiNER2.5 → LLM on low confidence) → rule-hybrid → ReciFine Silver reuse. E8 scale 1k→10k→25k→60k (100k only if marginal Gold gain justifies) (RD L1117–1119).

### 2.7 Calibration
Interpretable logistic correctness model first (top p, margin, normalized entropy, candidate count, retrieval rank/score, exact-alias, compatibility/source flags); isotonic only when support permits (RD L1921); separate calibration-fit and policy-validation pools; recalibrate after model/prompt/candidate-generator/registry/language-view change (RD L1925). Conformal risk control "only under matched assumptions" (RD L825). Repo: calibrator = logistic+isotonic on conf+M6 (S127).

### 2.8 RAG ladder (verified identical to SSOT §245.12, SSOT L26667–26679; RD L2487–2498)
B0 LLM only · B1 dense RAG · B2 BM25+dense hybrid · B3 structured metadata RAG · B4 state-aware RAG · B5 state + evidence compatibility/conflict packet · B6 + Level-15 transition fallback · B7 + calibrated recommend/ask/abstain. RD: shared integrity checks on all baselines; evaluate B7 separately from representational gains (RD L2500). Retrieval sub-ladder (K.14 staged): establish B2 + event/table chunks → metadata, state packets, one embedding challenger → contextual prefixes / multivectors only if error analysis indicates (RD L2522). Final recommended candidate K.17 (RD L2553): structured accepted records, event/table-aware chunks, lexical+dense, exact ledger reads, metadata compatibility, "a strong reranker", bounded packets, versioned answer contract, deterministic numeric checks, calibrated routing. Embeddings: open BGE-M3 baseline + Gemini Embedding 2 challenger (RD L2400).
**Repo reality:** structured retrieval MRR 0.856 > RRF hybrid 0.704 > BM25 0.597; free-text fallback RRF(BM25+e5-large-v2) 0.762; **cross-encoders negative**; dense blend on structured +0.005 n.s. (S093 L53; BT L20; DFS L35). "So bi-encoders do not go into evidence retrieval again" (S093 L54). RQ16-03 pilot: structured compatibility beats CE-large on hard negatives (BT L39). → RD K.17's "strong reranker" default conflicts with measured evidence (silver-only; see §9).

### 2.9 Scientific completion (DEL-2) ladder (G.3, RD L2084)
Simple means/hierarchical priors → nearest compatible evidence → regularized regression/LightGBM → one completion model; propensity weighting needs justified observation model and overlap; conformal coverage (DEL-2.d, RD L1263); Var-T-JEPA/T-JEPA research-only stretch. **Repo:** D0–D7 baselines, log-RF + median AE; "learned models win on random splits; gains vanish on cold splits; conformal coverage 0.72–0.87 under shift" (DFS L32); C9 transition fallback not routed, G16-TRANS not passed (BT L23).

### 2.10 Representation / autoencoder (S093 §4.3, L60–65)
No AE on critical path (SSOT §190.4: reconstruction ≠ useful transfer). Bounded: denoising/masked-ingredient AE over REC ingredient sets (mask 10–20%) as substitution/anomaly prior; **baselines first: PMI/SVD co-occurrence, then masked-set kNN**; ships only if beats PMI/SVD on masked-ingredient recovery R@10 on family-grouped splits, replicated on second source (SustainableFoodDB 118k). VAE/graph AE/FlavorTwin deferred.

### 2.11 Jev / System-One decision layer (RD §17, L864–1022; App. E L1855–1941)
Three-tier stack (hypothesis): deterministic code → closed-set decisions (Jev or open alternative) + **our** calibrator → LLM generation only (RD L896–899). Fit table by stage RD L903–920 ("None" for DEL-2, arithmetic, conversion, chemistry). Rules RD L939–951: pin `jev-1.13.0`, recalibrate (ECE before/after), route by our budgets, always escape options, small state, atomic questions, recipe text untrusted, Hinglish gloss, pair with open baseline, check licences before sending text to third-party API, "Never Gold, never arithmetic, never chemistry values". Adoption per decision family (RD L1941).

### 2.12 JEPA (Appendix A, RD L1456–1499) — optional ≤10%
J1 linking encoder (vs InfoNCE bi-encoder, MLM), J2 LLM-JEPA step→event JSON (vs SFT), J3 latent surprise for omitted steps (vs rule+precedent, LM perplexity, Nandy order model), J4 action-conditioned planned-state prior (never overrides symbolic replay), J5 V-JEPA 2 video (Level 17, out of scope).

---

## 3. Experiments / hypotheses / RQs

Shared rules (RD L1030–1034): recipe/family-clustered paired bootstrap; multiple seeds; assistance disclosed; no tuning on sealed test. Every experiment records hypothesis, primary metric, practical minimum effect, data/split hashes, eligible universe, baselines, fixed/tuned components, tuning budget, seed list, uncertainty method, cost definition, claim template (RD L1949). Three tracks kept separate: legacy reproduction, compiler benchmark, downstream RAG — "no single combined SOTA score" (RD L1947).

Hypotheses explicitly [P] (RD L158–163): compiler improves RAG (E10); structural similarity beats recency (E4/E5); 100k Silver beats smaller curated set (E8, "unproven"); Jev replaces LLM selectors at lower cost (E14); JEPA helps (J1–J4); "Recipe text alone identifies process chemistry or sensory effects — Unsupported in general".

| ID | Question / comparison | Key metric / win criterion | Repo status |
|---|---|---|---|
| E0.1–0.3 (RD L1038–1042) | IAA, tool choice (INCEpTION vs Label Studio on same 20), Claude pre-fill vs none (Gold-Light) | span-F1/edge-F1/κ per layer; minutes/recipe; per-label human-first list if Claude precision <0.85 | pilot_20 frozen as AI-assisted human-reviewed dev Gold (D-016/D-017); Food.com v1.1 20 recipes AI_ASSISTED_HUMAN_REVIEWED (reports/gold/foodcom_ai_assisted_v1_to_v1_1.md L3). Tool pilot: no repo evidence (UNVERIFIED). |
| E1.1–E1.10 (RD L1046–1057) | legacy NER reproduction, cross-source, challengers, kNN, Silver ablation, contamination audit, instruction NER, robustness, RecipeDB3 reproduction+hygiene, instruction weak labels | e.g. E1.10 QUANTITY ≥0.85 vs 0.638 | E1.9 **done**: reports/ner/recipedb3_matched_reproduction.md: theirs 0.9543±0.0020 vs clean grouped 0.9504±0.0034, Δ +0.0039 (Welch p 0.0674); leaked rows micro 0.9937 vs non-leaked 0.9558. Instruction NER (E1.7/E1.10): no repo result found (UNVERIFIED). |
| E2.1–2.3 | whole-string vs concept+facets; product-boundary challenge; Hinglish alias coverage | Acc@1, fragmentation, wrong merges | not found |
| E3.1–3.4 | candidate Recall@K separately; selectors; RecipeDB2 top-200 reproduction; tail/unseen | Recall@K; ACCEPT precision; risk-coverage vs cosine 0.70 | partial (S094, S124–S127 linker) |
| E4.1–4.5 | reference resolution; long-distance >3 steps; online vs offline | accuracy by distance bin; leakage check | not found |
| E5.1–5.4 | structural similarity; counterfactual swaps ("a template-copier must fail") | wrong-antecedent rate; merge/split edge F1 | not found |
| E6.1–6.7 | quantity structure, routes, allocation, invented-grams audit (**must be 0**), katori, correlated uncertainty, coverage vs 43.90% | "coverage > 43.90% with zero invented grams" only on matched pair set | partial (quantity_coverage_v0) |
| E7.1–7.5, E8 | Silver economics & scale | Gold accuracy, cost per accepted record, review minutes | ⬜ (BT L45 RQ16-09 Silver utility ⬜) |
| E9.1–9.4 | raw vs calibrated; coverage at 2/1/5%; clustered vs naive intervals; drift mode | risk–coverage, ECE/Brier | NER router done; RAG calibration "needs verified labels" (BT L41) |
| E10.1–10.15 | compiler→RAG; B0–B5; ablations (−state,−ledger,−linking,−abstention); oracle; chunking, metadata, embeddings, parent expansion, contextual prefix, late chunking, ColBERT, prompt layout, compatibility features, query expansion, index drift | supported-answer rate at matched coverage/tokens | B0/B2/B5/B5F/B5F+E/B5T on 20 AI-authored dev questions; benchmark ≥80 human questions (D-008) open (DFS L40) |
| E11.1–11.3 | provenance gates vs invented science | unsupported numeric claims; precision of UNSUPPORTED/CONFLICTING | C16 template verbaliser 0 unsupported (BT L30) on dev only |
| E12 | ontology drift (FoodOn snapshot) | obsolete-ID errors | not found |
| E13.1–13.3 | omitted steps rule+precedent vs LLM; hallucinated-step audit | "target precision ≥ 0.90 at achievable recall" | not found |
| E14.1–14.15 | Jev decision layer per family | e.g. E14.2 "≥ cross-encoder coverage at equal risk and lower cost"; E14.3 "recalibrated ECE ≤ open baseline" | not run; superseded by V2-DM open-model lane |
| Oracle studies (RD L1189–1196; F.9 L2044–2048) | gold spans→links, gold links→refs, gold events→ledger, gold state→answers | oracle-vs-predicted gap per stage | — |
| J1–J5 | see §2.12 | kill criterion RD L1489 | not started |
| DEL-1.a–c, DEL-2.a–d (RD L1262–1263) | coverage audit; canonical-ID join accuracy; E11.1 challenge; MNAR profile; pair-holdout/study-disjoint; completion vs LightGBM+propensity; conformal | — | DEL-2 negative result exists (DFS L32) |

SSOT RQ/E16 status (BT L34–84): RQ16-01 semantic state value ⬜; 02 structured retrieval 🟡; 03 compatibility reranker 🟡 NEED_DATA; 07 quantity ontology 🟡; 09 Silver ⬜; 10 active learning ⬜; 11 Claude multi-pass ⛔; 13 duplicate leakage 🟡; 20 transition fallback 🟡 (negative); 21 completion visibility ⬜; 23 quantity encoder downstream ⬜; 24 recipe graph downstream ⬜; 25–27 FlavorTwin ➖; 28 source generalization 🟡; 29 long-tail ⬜; 30 system contribution ⬜. Gates G16-* all ⬜ "to be scored when matching E16 runs exist" (BT L84). (BT is dated 2026-10-18 after S056 — partially stale.)

---

## 4. Gates, promotion and stop rules — exact ids and thresholds

### 4.1 Hard gates (RD §14.1, L787–798)
Route to review/reject when: ID invalid; source span not found; dimensions incompatible; no portion/density route; entity used before produced; allocation over-spends known amount; unsupported scientific value appears. "High confidence cannot bypass these, and schema validity does not prove correctness."

### 4.2 Selective policy (RD §14.2, L800–818)
`Coverage_j(t)=N_accepted/N_eligible`, `Risk_j(t)=N_incorrect,accepted/N_accepted`; t chosen on dedicated calibration partition with error budget and minimum useful coverage fixed **before** looking; test once sealed. "Do not adopt RecipeDB2's raw cosine ≥ 0.70 as a correctness cutoff" (RD L802).
| Route | Initial error budget [P] | Init prior (Report B) |
|---|---|---|
| Automatic food linking | accepted-link error ≤ 2% | accept P ≥ 0.90; review 0.50–0.90 |
| Food-specific quantity grounding | wrong/unsupported route ≤ 1% | ingredient-specific density → accept; category → review; none → mass = null |
| Cross-step reference/flow | wrong-link ≤ 5% | provenance stays `inferred` even if accepted |
| Span labels | report per label | p ≥ 0.90 and ≥2 sources agree → accept; 0.60–0.90 → review |
| Process mapping | report | exact/alias or P ≥ 0.85 → accept; else `UNMAPPED` with raw verb kept |
| Unseen concept / no candidate / conflict | review/unresolved by default | — |
| Scientific quantitative claims | evidence compatibility + Level-15 gates | no universal threshold |
Note "The 1% quantity budget is a wrong/unsupported accepted-route target, not … within 1% of measured mass" (RD L2007).

### 4.3 Calibration-evidence arithmetic (RD L820–827; F.5 L2001–2007; F.6 L2011)
Zero-error one-sided 95% bound `p_upper = 1 − 0.05^(1/n)`: **n = 149 for <2%, 299 for <1%, 598 for <0.5%**; decisions within a recipe not independent → clustered intervals; cluster bootstrap with zero errors "cannot invent an unseen-error upper tail" (RD L2005); ≈384 for proportion ≈0.90 ±3pp applies to Bernoulli, not F1 (RD L514, L2011); 3 seeds for main trained comparisons (RD L2013); predeclared non-inferiority margin required (RD L2015).

### 4.4 Agreement targets — "targets to check, not promises" (RD L518–529)
Core ingredient spans exact span-F1 ≥ 0.90; ACTION/TOOL/DURATION ≥ 0.85; ENDPOINT/FORM/INTERMEDIATE exact(+partial) ≥ 0.80; relations/coreference edge-F1 ≥ 0.75; link decisions Cohen's κ ≥ 0.80; implicit arguments/omitted steps κ or F1 ≥ 0.65 ("contested"). "Agreement below target triggers a schema/evidence review before any Silver expansion." κ only for paired categorical decisions with defined item universe (RD L1713).

### 4.5 Claude protocol thresholds (RD L544–549; C.7 L1719)
Pilot 50–100 recipes; batches 10–25 ordinary or 1–5 hard; "One extraction → deterministic validation → one targeted repair → review/unresolved"; per-label precision < 0.85 → human-first (a triage proposal; use uncertainty and severity); Claude never sole source of Deep Gold label; never touches sealed test initial passes. Compile loop caps: one automatic structural repair, ≤2 semantic proposal rounds per step in pilot (RD L1604).

### 4.6 Verification tiers (RD L478–490) and Gold phases (RD L503–516)
Deep Gold (Sealed): two independent humans, **no LLM pre-fill on initial passes**, adjudicated, validators, source-locked, hashed → final test only. Deep Gold: independent A/B + adjudication → calibration/dev. Gold-Light: human verification of specified fields, assistance logged → training/dev/AL. Silver: model extraction + validators + sampled audits. Bronze/synthetic: never dev/test. "Correction after seeing model output is Gold-Light, never 'independent'" (RD L490).
Phases: **G-0** 20 hard recipes, both annotators, all layers → exit "Manual v1.1; minutes/recipe measured per depth"; **G-1** 100 at A2, 40 to A4, stratified S1–S6 → "Disagreement understood; key labels stable"; **G-2** sealed 100 at A2 (40 at A4), double, no LLM → "Hashed; never tuned on"; Stretch 300; v14 long-term 750–1,000 Deep Gold (≈300 train/dev · 300 calibration · 400 sealed), 3–5k Gold-Light, 60–100k Silver (matches SSOT §236.1 L25593+). Pilot allocation of 100 seed: 60 dev/training-support, 20 calibration-fit, 20 policy-validation, family-disjoint — "not enough evidence for a 1% risk guarantee" (RD L1964). Natural/challenge 70/30 (RD L516). Synthetic ≤20% of training lines, never dev/test/calibration (RD L779).

### 4.7 Work-package exit gates (RD §19.1, L1221–1235)
W0 "Every pilot record has a source and a split family"; W1 "20 hard recipes representable with no ad-hoc fields"; W2 "Disagreements understood; throughput measured"; W3 "§9.2 cases keep unknowns and evidence routes; E6.4 = 0"; W4 "E1.1 reproduced; costs logged"; W5 "Reserve/split/discard and unresolved cases pass CI invariants"; W6 "Risk–coverage and subgroup support documented"; W7 "Quality, concept growth and review cost acceptable"; W8 "E8 marginal gain > cost; no evidence fabrication"; W9 "E10 better at matched coverage/cost"; W10 "Requires passed Level-12–15 execution gates"; WV "E14 gate satisfied; open baseline on same interface"; WJ "J-gate satisfied".

### 4.8 Twelve-week gates (H.5, RD L2159–2167)
G-DESIGN (schema representable, throughput measured) · G-BASE (shared data/scorer and no unsupported conversion) · G-FLOW (replay and unresolved cases correct) · G-EVAL (splits frozen, models/policies selected on dev) · G-UTILITY (supported task utility measured) · G-RESULTS (claims match evidence) · G-RELEASE (artifacts traceable and rerunnable).

### 4.9 Experiment stop rules (F.10, RD L2052–2062)
Annotation E0: promote if decisions observable + throughput known; stop if "disagreements show an incoherent schema". Baselines: stop if "reproduction mismatch is unexplained". Core flow: stop if "ledger depends on invented values". Structure E5: stop if "no gain over strong contextual baseline". Selective policy: stop if "rare errors unsupported by calibration sample". Jev: stop if "confidently wrong on key domain cases". RAG E10/E11: stop if "extra tokens alone explain the gain". Silver: stop if "noise/coverage drift or review cost overwhelms gain". JEPA: "no meaningful dev gain after one bounded round".
Special gates: **E14 gate** (RD L1164–1167) only after E3.1 exists (same candidates), calibration partition frozen, API key granted. **J-gate** (RD L1489): no J until E1.1, E3.1, E4.1–E4.3 and frozen splits; ≤10% effort; kill = no gain outside paired-bootstrap CI on dev after one tuning round.

### 4.10 Release gate (I.3, RD L2227–2229)
No "first", "SOTA", "guaranteed ≤1%", or "chemistry predicted from recipe text" claim unless the corresponding gate is supported; "Unsupported numeric conversions accepted by the deterministic adapter must be zero on its exhaustive software fixtures and audited benchmark; any observed violation blocks that route". v14 adoption: "Do not mark Level-12–15 execution gates complete merely because fields exist" (RD L2235). 18 deterministic fixture families (RD L2189–2208), 8 demo scenarios each with a hidden evaluation variant (RD L2214–2223).

### 4.11 SSOT G16 gates and stop rules (verified SSOT L27446–27501)
G16-DATA, -VOCAB, -QTY, -SEM, -GRAPH, -EVID, -CONFLICT, -CAL, -TRANS ("No Level-15 fallback… until the relevant G15 gates pass"), -DEC, -REC, -PROV, -OOD, -FT. §249.2 stop rules (complexity → data/evidence) include "Silver does not improve held-out Gold", "canonicalization errors dominate parser errors", "quantity conversions are mostly unsupported", "structured retrieval does not beat strong hybrid RAG", "confidence is uncalibrated under source shift", "human verification cost exceeds the value". RD's G-*/W-gates are *finer-grained operationalisations* of these; RD never names G16 IDs explicitly (it references §249 only as baseline, RD L9) — mapping needed.

### 4.12 Repo gate statuses touching this material
NER claims gated on H6 ("No 'beats CoSyLab / SOTA' statement before H6 approval, a matched reproduction and a paired significant difference", S093 L68). DEL-1 0/40 human-verified (S093 L10; DFS L21). DEL-3 30 sessions 0/30 human-reviewed (DFS L29). D-008 benchmark ≥80 human questions open. Step-07 condition human audit κ ≥ 0.8 pending (WORKLOG S131); `reports/step07/step07h_human_gate_result.json` = NOT_COUNTED_PROVENANCE_INVALID (ctx). Identity 400-pair blind packet unlabeled (S134).

---

## 5. Data requirements and named sources (licence notes)

### 5.1 RD source registry essentials (RD §3, §7.7, §23; App. J)
| Source | Role in RD | Licence/access note (as stated) | Repo status |
|---|---|---|---|
| CoSyLab 6,611/2,187 manual split; RecipeDB companion data [S1][S67] | E1.1 legacy reproduction | ask lab | cosylab_companion downloaded (S093 L23); D-015 use permitted, licence ASSUMED / DERIVED_ONLY |
| RecipeDB3_NER_Research_Paper [S64] (26,444 phrases; 10k instructions value-lists) | M1–M7, E1.9, E1.10 | "Licence not stated in the README; ask the lab" (RD L217) | downloaded (S093 L21); reproduction run |
| Recipe_NER_DL | E1.1 | confirm vs paper | downloaded (S093 L22) |
| CocktailDB NER [S65] | domain shift | — | — |
| Nutritional-Estimation [S66] | E6.7 baseline | — | — |
| CulinaryDB [S68] | alias seed, compound ingredients, 22 regions | "Licence" to check | not found in ledgers (UNVERIFIED) |
| RecipeDB2 [S2] | E3.3, E6.7 comparison | **datasets not publicly available due to institutional copyright** (RD L2042, R14); preprint | categories ingested (DFS L50) |
| RecipeDB / Foodoscope API, FlavorDB2 | IDs, eval target | CC BY-NC-SA 3.0, API via Prof. Bagler (RGM L17) | ⏳ H1 email; FlavorDB missing (S093 L14) |
| Ingredient Parser (strangetom) [S21–S23] | P2/P4 baseline | "MIT-style licence; check" | — |
| NYT ingredient-phrase-tagger [S38] | Silver/pretraining only, noisy | — | — |
| TASTEset v1/v2 [S27][S37] | external benchmark | MIT (RGM L20) | ✅ used; ctx says "TASTEset unverified" — **contradiction** with RGM "MIT" (verify which TASTEset version/licence) |
| ReciFine/ReciFineGold [S29][S30] | instruction-NER test + Silver | permissions, crosswalk, overlap with RecipeNLG | not acquired |
| RISeC / r-FG / ARA [S6–S9] | relations, implicit args | — | **r-FG repo not found** (RGM L21) |
| OpenPI / OpenPI2.0 / OpenPI-C [S40] | closed state vocabulary | OpenPI MIT (RGM L21) | food subset 197 procedures / 7,629 state changes (RGM L21) |
| FoodSEM / FoodOntoRAG / FoodBench-QA [S3–S5] | NEL baselines | [C] only | — |
| JFC-Recipe [S47] | quantity→grams precedent | licence; Japanese | — |
| INDoRI [S45] (5,187 Indian recipes) | S4 stratum | "Licence before storing raw text" | — |
| 6000+ Indian Food Recipes (Archana's Kitchen) Mendeley DOI 10.17632/xsphgmmh7b.1 [S70] | S4 stratum + translation robustness | "repository lists CC BY 4.0" (RD L2258); scraped source → check terms | not found (UNVERIFIED) |
| Kaggle What's Cooking (Yummly) [S71] | alias mining, cuisine shift | competition terms | — |
| Food.com recipes+interactions [S72] (~180k) | raw pool, dedupe vs RecipeDB | [U] | repo has **522,517 Food.com** recipes in recipe_base (WORKLOG S133) — different size from RD's ~180k → which Kaggle release? UNVERIFIED; ctx: "Food.com CC0 only uploader-declared" |
| RecipeNLG [S32] / Recipe1M+ [S33] | raw pools | Recipe1M+ "research access, no open licence" (RGM L22) | ⛔ |
| USDA FDC by data type [S20] | portion/density evidence | public domain / CC0 (RGM L13; DFS L14) | FDC crosswalk CANDIDATE only (D-006) |
| FoodOn [S15] | ontology layer | CC BY 4.0 (RGM L25) | crosswalk ✅ |
| GLiNER family | baselines | Apache-2.0 (RD L199) | zero-shot run |
| Jev 1.13 [S59–S62] | decision layer | proprietary; **sending recipe text to third-party API needs licence check** (RD L950, L1353) | not used |
| Gemini Embedding 2, BGE-M3, ColBERT, Late Chunking, Contextual Retrieval [R22–R32] | RAG challengers | hosted model = external service | not used; hard rule: never send project data externally |

### 5.2 Additional sources from the smaller docs
- Evidence (RGM L10–26): USDA retention R6 (public domain, EVD 7,018); Phenol-Explorer (DB terms, EVD 3,870; D-005 scrape approved for this one target); Bognár 2002 (open-access report, EVD 6,594 retention + 496 weight-yield = 7,090 matches ctx); FDC raw/cooked 867 pairs, 16,365 dry-basis ratios (4,984 analytical) = candidates not EVD; FoodAtlas 2026 (code MIT, **data CC BY-NC 4.0 since 2026-10-09**; manual download only, bot checkpoint not circumvented); FlavorGraph (Apache-2.0 repo, NC upstream → no redistribution); FooDB (CC BY-NC 4.0; 403 to scripts); ChemTastesDB (CC BY 4.0, Zenodo 15051366); BitterDB/Pyrfume/GS-LF/Keller-DREAM (later, FlavorTwin); BioModels BIOMD0000000052 Maillard ODE (open; "later (P9 reaction substrate)"); Maillard/acrylamide kinetic literature via verification queue Route B.
- Downloaded-not-ledgered (S093 L18–28): sustainablefooddb 118k recipes (carbon footprint) — **possible un-indexed recipe corpus** (authority map row 8); NOVA 2,970×103 nutrients; AllerStack 4,316 proteins; recipe_knowledge_mining; companion; NER_DL. All under D-015 ASSUMED / DERIVED_ONLY.
- Route rule D-009 (S093 L30): one source → SRC record → derived rows via `LedgerStore` → validators → rebuild exports → test → WORKLOG.
- Backlog (BL L10–12): closed-world inventory of raw terms across all ledgers vs normaliser after Step-07 human gate; USDA abbreviation expansions (CKD, BKD, BLD, DRND, BKD/SIMMRD, `+`) = H2 approval item, UNVERIFIED until then; "No scraping/acquisition for new terms before Step 08+ approval".

### 5.3 Data requirements implied by RD
- Recipe-level: source/rights/locale/checksum/family per recipe (P0); raw text preserved with section IDs; family graph before splits (F.3).
- Gold: 20 + 100 + 100 (target) with A2/A4 depth, S1–S6 flags; 750–1,000 Deep Gold long-term; capacity scenarios 262 / 453 / 698 annotation hours vs 360–480 available person-hours (RD L2124–2130) — "the original plan is therefore a target gated by measured throughput".
- Science: DEL-1 "≥ 1,000 public rows + ≥ 40 verified; joins via IDs" (RD L1262); "favor fewer fully traceable anchor studies over a large noisy extraction pool" (RD L2070).
- Retrieval Gold: ~80 questions × 8 task types (pilot; correlated within recipe) (RD L1266, L2504); pooled blind relevance judging, graded relevance separate from applicability (RD L2506).
- Storage arithmetic: dense float32 `N × dim × 4 B`; 2M × 768 = 6.144 GB; × 3,072 = 24.576 GB (RD L2406).

---

## 6. Dependencies on other levels/steps

- P10/DEL-1 scientific registry is a **separate plane**; joins only via canonical food/process IDs (P3/P5), never recipe text (RD L1262, L321 rule 6, K.2 L2302).
- W10 process-effect service and FlavorTwin conditioning "Requires passed Level-12–15 execution gates" (RD L1233); FlavorTwin consumes P3 products/forms and P7 state versions; "process-conditioned flavour" only through DEL-1 evidence (RD L1287, L2235).
- B6 (Level-15 transition fallback) "Future/stretch only after transition gates" (RD L2497); SSOT G16-TRANS.
- Level-15/FlavorTwin estimates consume the scientific registry; "never write source recipe temperatures, Gold labels, or observed-session chemistry" (RD L2097).
- E14 depends on E3.1, frozen calibration partition, API access (RD L1164). J depends on E1.1, E3.1, E4.1–4.3 (RD L1489).
- Oracle cascade dependencies P2→P3→P6→P7/P8→P9 (F.9).
- Invalidation graph (B.7, RD L1612): concept-mapping change invalidates link decisions, food-specific conversions, evidence joins; corrected span invalidates consumers; quantity-only correction requires downstream allocation replay.
- Split dependencies: families formed before split; augmentations/translations/teacher labels/exemplars inherit family partition; scientific study-family split separate from recipe-family split (RD L554–570, L1974).
- Annotation contract precedes Silver: agreement below target blocks Silver expansion (RD L529); shared contract changes merged before downstream data generation (RD L2177).
- Simulator inputs depend on SDC `source_class` (SDC L2–7).
- S093 sequence (S093 L33–38): E16-A closing → mention→ING linking → DEL-5 ladder B0–B5 → SustainableFoodDB carbon → AllerStack/NOVA after allergen sign-off; human gates throughout. RGM order (RGM L48–49): X14 → X9 → X10 → X11 → X12 → X13 → X15 → X7 → X8. Both are *course-era* sequences, superseded by the 36-step spine.
- L13E (SSOT §§260–279): RD has no dependency on it; but RD's derivative-family graph (F.3) and recipe identity overlaps with SSOT §264 "Recipe identity, variants, distance, and novelty" — the 07I implementation already consolidated these (authority inventory L25–32).

---

## 7. Risks / failure modes

From RD §22 (L1340–1355): lab test sets/APIs unavailable (fallback TASTEset/ReciFineGold/sealed set); annotation throughput below plan (shrink A4 before sealed test); Claude usage limits; **licences of scraped text** (store offsets/derived annotations; redistribute raw only where permitted); over-claiming SOTA; inferred-step hallucination; JEPA time sink; Jev waitlist/rate-limit change; Jev confidently wrong; Jev English-first on Hinglish; proprietary reproducibility; **sending licensed recipe text to third-party API**; Silver noise propagation; frontier-LLM benchmark contamination (new-source held-out set).
Additional failure modes stated in the body:
- Pipelined error compounding (r-FG edges drop sharply with predicted entities) → oracle studies mandatory (RD L150).
- Untuned LLMs weak at recipe NER (few-shot macro-F1 5.88–32.90; Claude Sonnet 4 0.497 vs 0.741 human IAA on UNER v2) → Claude never Gold alone (RD L154).
- Unverified Silver *hurt* on RecipeDB (95.71 vs 95.90) (RD L148).
- Food links degrade under ontology version change (RD L151).
- Lost-in-the-middle: long context unreliable → state packets (RD L152, L655).
- Artificial-data NEL overstates natural (RD L153; FoodBench natural 60.71–80.89 vs artificial 87.75–95.75).
- Ingredient Parser water-density default and `raw` hints → fabricated grams (RD L203, L611–614; R15).
- "500 g or 1 cup" parsed as 500 cups in Nutritional Estimation (RD L180).
- Canonical-ID-only coreference confuses lots (D.5, RD L1815).
- Test-set checkpoint selection, augmentation-family leakage (RecipeDB3) → hygiene; repo confirms 5.4%/13.5% leakage (S093 L68) but effect small (+0.0039, ns).
- Late chunking leaks future context into online-prefix track (RD L2396).
- Mixing vectors from different model spaces; accidental multi-input aggregation in Gemini API (RD L2402–2404).
- Planning documents retrieved as evidence ("target QUANTITY F1 ≥0.85" retrieved as attained) → namespace separation (RD L2304).
- Evidence laundering via online self-training from user agreement (RD L2547).
- Assisted annotation mislabelled as independent; anchoring (RD L490, C.7).
- Zero-error cluster bootstrap misread as guarantee (RD L2005).
- Capacity: central annotation scenario consumes nearly all 360–480 person-hours (RD L2130).
- Repo-observed: DEL-2 cold-split collapse; conformal undercoverage 0.72–0.87 (DFS L32); kNN-NER null; cross-encoders negative; GLiNER zero-shot weak; memory pressure in identity run (S134); ledger size watch REC 94 MB / KGE ~60 MB (DFS L60); allergen table awaiting human sign-off (S093 L16).

---

## 8. MAPPING TO THE 36-STEP SPINE (brief §9)

Caveat: the 36-step plan's step cards are MISSING (ctx). Below, "requires" = what *this* material requires/implies for that step; it is reconstruction, not quoted card text.

**01 Freeze project authority.** Input: RD authority order (RD L20: immutable source & measured evidence → adjudicated annotation contract → versioned compiler contracts → experiment results). Must resolve: RD rank (#4 per MP AG4 L2742–2750 vs rank 5 per authority map). Output: ruling on whether RD §21 additive schema changes (RD L1291–1307) are adopted — they are **not** in SSOT v15 (grep: `OMITTED_STEP_CANDIDATE`, `labels_annotated_for`, `NO_VALID_CANDIDATE`, `unit_variant`, `entity_version`, `INFERRED_RULE`, "Sealed" all 0 hits in SSOT v15; MP v4.0 has OMITTED_STEP_CANDIDATE ×3, OBSERVED_SESSION ×2, Sealed ×1, katori ×4). Gate: explicit adopt/defer per item via migration table (RD L1307, L2233).

**02 Audit implementation state.** Inputs: BT, DFS, S093 — all **stale** (BT 2026-10-18 after S056; DFS through S096; S093 2026-10-19). Required corrections: RecipeDB3 matched reproduction is DONE (reports/ner/recipedb3_matched_reproduction.md) though DFS L45/L57 and S093 L33 say not run; NER closed S128; REC 89,565 → recipe base 612,782 (S133); EVD Bognár 6,594+496; GLiNER zero-shot done (BT L71 says "pending"). Output: refreshed tracker keyed to steps, not DEL-1…5.

**03 Freeze state semantics.** Requires: three identities (concept / lot / entity version, RD L327–333); lifecycle ACTIVE/RESERVED/INCORPORATED/DISCARDED/SERVED/UNRESOLVED (RD L584); flow ops semantics D.3 (RD L1781–1791); trajectory PLANNED/OBSERVED_SESSION/PREDICTED (already in engine.py:23); planned endpoint vs observed; text order vs execution deps vs control constructs (RD L587–590); four missingness axes (RD L681–690) incl. `CONVENTION` and proposed `INFERRED_RULE`; field-level assertion wrapper (B.3). Gate: 18 fixture families pass (RD L2189–2208); W1 "20 hard recipes representable with no ad-hoc fields". Cross-check with `reports/h_state/state_representation_contract_v1.md` (not in my assignment; UNVERIFIED alignment).

**04 Freeze evidence/provenance/similarity contracts.** Requires: evidence row granularity (G.1) and three meanings of "verified" (RD L2070); compatibility as conjunction (G.2) with tri-state COMPATIBLE/INCOMPATIBLE/INSUFFICIENT_INFORMATION (RD L2429); answer classes (G.4); claim ledger (G.5); similarity taxonomy K.4 (lexical, food-concept, form/product, procedural role, referential, scientific applicability, whole-recipe, cross-modal — "Similarity is task-specific, not one universal number"); index namespaces + `epistemic_type` (K.2, K.5); SDC `source_class` and magnitude rule. Gate: no claim class without required grounding; similarity never used as calibrated correctness (RD L2359).

**05 Normalize EVD.** (Done S129.) RD contributes: row = one measurement/aggregate with basis, method, uncertainty, source table/span (RD L2068); BELOW_LOD/NOT_MEASURED availability; study family as split unit. Check that ES-1.1 export fields (matrix_id, prior_state_id, LOD/LOQ=null, tier, verification, design strength) cover RD G.1 — appear to (WORKLOG S129).

**06 Freeze source acquisition manifest.** (Done S130, 64 sources.) RD/RGM/S093 licence notes to reconcile with `registry/data_source_acquisition_manifest.csv`: FoodAtlas CC BY-NC since 2026-10-09; FlavorDB2/RecipeDB CC BY-NC-SA 3.0; FooDB CC BY-NC; ChemTastesDB CC BY 4.0; RecipeDB2 data not public; RecipeDB3 licence unstated; Mendeley Indian CC BY 4.0; Recipe1M+ no open licence; D-015 ASSUMED/DERIVED_ONLY; sustainablefooddb 118k recipes not indexed. Also P0: rights, locale, checksum per asset; ingest policy LIVE_ONLY/DO_NOT_STORE (SDC L8).

**07 Condition & measurement normalization.** (Automated infra done; 07H/07H-R frozen; human audit not validly passed.) RD requires: quantity AST node set (D.1), `quantity_kind` ≠ `dimension`, exact rationals, ALTERNATIVE not multiplication, unit-convention resolution order and scenario envelopes (D.2), affine temperature, CONTAINER_COUNT, conversion route preference with no category approximation in strict route, `unit_variant` (katori regional). Gate: E6.4 invented grams = 0; fixtures "No density evidence", "Quantity alternatives", "Package/drained basis" (RD L2195–2197). Conditions: `conditions{heat, temp_value/range, duration_min/max}`, endpoint text separate from duration (RD L580, L1660). Human audit protocol: κ ≥ 0.8 (S131) consistent with RD link κ target 0.80. **07I identity:** RD §7.7 MinHash ≥0.8 = initial candidate rule only; F.3 derivative-family graph (raw hash, normalized hash, ingredient/instruction signatures, near-dup candidates), borderline review, sampled grouping precision; "same verbs and different foods are not automatically duplicates"; distinguish derivative / source / dish-family / ingredient-concept / region holdouts (RD L1972). 07I-R produced exactly this structure; 400-pair blind packet = the RD-required sampled precision check, still unlabeled.

**08 Scientific source lineage.** RD requires: study-family split separate from recipe-family split (RD L570, L1974); "a thousand extracted rows may contain far fewer independent experiments" (RD L2068); duplicate study tables are a leakage path (RD L2082); source/table/span pointers; publication-level identity for E1.6-like contamination audits on scientific sources. Output must support DEL-2 study-disjoint holdouts and Step 15 freeze.

**09 Evidence extraction & verification machinery.** RD requires: provider-neutral decision envelope (E.2) and `select_option` interface with no nearest-ID fallback; one extraction → validation → one repair → review (RD L546); prompt contracts by role (K.11 extraction / selector / answer / critique); table-aware chunking keeping headers/units/footnotes/study ID, OCR uncertainty flags (RD L2380); "verified" meaning recorded (RD L2070); AI pre-classification of literature rows only as hint (RD L919); request/response caching keyed by full contract (RD L1610); never send licensed text externally (RD L950; hard rule). Gate: per-label/field AI precision < 0.85 → human-first.

**10 20-row mechanism pilot.** RD G.1: "first scientific pilot should favor fewer fully traceable anchor studies over a large noisy extraction pool" (RD L2070). Metrics: transcription accuracy, alignment accuracy, comparability assessment — separately. Related repo: DEL-1 40 verified rows gate 0/40.

**11 Wave-1 verified mechanism evidence.** Requires E11 challenge set (missing/conflicting conditions) as acceptance probe (RD L1141–1145); DEL-1.c; verification tier per row.

**12 Structured database evidence.** Sources (RGM): USDA R6, Bognár, Phenol-Explorer (done), FDC raw/cooked (candidates), FoodAtlas (NC, manual), FooDB (NC, manual), BioModels Maillard ODE, NOVA (S093 L25). Requirement: compatibility fields per G.2 captured per row (form, part, basis, process family, conditions, target).

**13 Large literature discovery corpus.** RD: literature harvest → verification queue (634 rows, DFS L18); OpenAlex/Crossref; section-aware chunking; Route B kinetics (RGM L24). No licence-violating full-text redistribution.

**14 Coverage-driven evidence growth.** RD §13: per-field present/attempted/verified/unresolved/grounded rates, head/torso/tail/unseen buckets; "An unobserved intersection … is not an invalid one" (RD L765); gap queue scored by impact/uncertainty/rarity/diversity/cost with a separate random audit stream (K.15, RD L2541).

**15 Freeze DATA-EVIDENCE v1.** Requires study-disjoint split manifests, hashes, evidence cards, claim limitations (I.3), DEL-1 ≥1,000 public rows + ≥40 verified (RD L1262; EVD already 17,978).

**16 Instruction semantic schema.** RD is the most detailed source: §6.1 layers, C.2 boundary rules, C.3 qualifiers/non-events, C.4 relation namespacing, C.5 task masks + eligible universes, `labels_annotated_for`, LM versioning, legacy adapters, PACKING/CONDITION additions, closed form vocabulary (RD L980), quantity kinds and unit conventions (RD L990–991), process mapping two-stage family→specific (RecipeDB 268 processes, RD L911; repo PROC 156 in 18 families, DFS L13). Gate: W1; G-DESIGN.

**17 Instruction-level extraction.** P2–P6 with E1.7 (instruction NER vs 0.88/0.90 [S35]), E1.10 (QUANTITY ≥0.85), E4.1–4.5, E14.13 mention→ingredient-list alignment (M4 "not available in their pipeline"); online vs offline tracks; prefix packets; Silver cascade. Baselines: RecipeDB3 spaCy instruction model micro 0.9258/macro 0.8698 (RD L122); r-FG (repo not found). Metric definitions F.4 (predicate + typed-role F1; explicit/implicit roles; negation/branch accuracy).

**18 Event-sourcing engine.** B.6 compile loop (9 steps), B.7 append-only, transaction includes input snapshot hash/event revision/output versions/quantity changes/issues/config hash, identical replay ⇒ identical snapshot hash; invalidation graph; D.3 operations; D.9 issue codes; CI invariants §8. Repo: C3 state reconstructor ✅, merge/split/reserve fixtures (DFS L29). Gate: W5 / G-FLOW.

**19 Gold state-trajectory pilot.** RD G-0/G-1/G-2, A0–A5, S1–S6, Deep Gold (Sealed) no LLM pre-fill, C.6 Gold chain (8 steps), IAA targets §7.5, capacity H.2. **Conflict with repo:** existing state Gold (pilot_20, Food.com v1.1) is AI-assisted/AI-reauthored + human-reviewed → by RD L490 it is Gold-Light, not Deep Gold; 30 sessions AI-drafted 0/30 reviewed. Step 19 must therefore create the first *independent* source-first Deep Gold set, or explicitly downgrade claims.

**20 Scale procedural semantic corpus.** E7/E8 Silver economics/scale (1k→10k→25k→60k; 100k conditional), task masks/field weights, active learning (uncertainty, disagreement, rare SEFS signatures, UNKNOWN links, source/region diversity, expensive downstream errors) + random audit stream, synthetic ≤20%. With 612,782 recipes (S133) and 605,476 provisional families (S134), RD's tiering (Silver 60–100k selected, not all 612k) applies; SSOT §236.1 adds "Large weak corpus 1M+ when permitted". Gate: W7/W8; SSOT §249.2 "Silver does not improve held-out Gold" stop.

**21 Effect/mechanism ontology.** RD minimal: `effect_class` field on events (RD L580); "Recipe text alone identifies process chemistry… Unsupported" (RD L163); WAIT has no chemical delta without evidence (RD L1791). Mostly outside RD scope.

**22 Event → effect signatures.** Requires P5 process IDs + conditions + initial form/state on entity versions (inputs), SDC rule (STRUCTURAL_RECIPE defines occurrence only).

**23 Mechanism applicability engine.** G.2 conjunction + INSUFFICIENT_INFORMATION tri-state; "A frying study does not automatically support boiling"; unknown cannot satisfy required field at claim gate; repo C7 compatibility layer 9 axes, UNKNOWN neutral (BT L21).

**24 Formula/model registry.** RD G.4 "Model estimate — trained model card and evaluated uncertainty"; scenario/assumption IDs; RGM BioModels BIOMD0000000052. No registry schema in RD (gap).

**25 Parameter-compatibility retrieval.** E14.14/§17.7.3 portion/density record selection pattern ("pick, don't generate"; Choice over records + `NO_COMPATIBLE_RECORD`; code computes) generalises to parameter records; K.10 pipeline with structured compatibility rerank.

**26–28 Simulation.** SDC is the binding contract (source_class, magnitude rule, licence, uncertainty). RD answer class "Scenario/assumption" + "Model estimate"; E6.6 interval calibration only on synthetic splits for software validation; synthetic never in dev/test/calibration (RD L779) ⇒ E7 synthetic prior (Step 28) must be tagged and excluded from final real evaluation. RGM: Maillard ODE (BioModels) is the only named simulator substrate.

**29–34 Transition science.** RD G.3 (DEL-2): study-disjoint + cold dimensions (food/product, process, food×process pair, region/source, conditions); split before normalization/imputation; baselines mean/hierarchical → nearest compatible → regularized/LightGBM → one model; propensity weighting caveats; sensitivity to missingness scenarios; "Randomly masking observed cells is an easier benchmark". Repo DEL-2 verdict negative on cold splits; conformal 0.72–0.87 (DFS L32) — Step 29/30 must start from this negative result, not re-promise it. RD keeps D0–D11 ladder untouched (RD L20, L64).

**35 Representation ladder.** RD K.4 similarity taxonomy; S093 §4.3 masked-ingredient AE with PMI/SVD and masked-set kNN baselines, R@10 family-grouped, second-source replication; mention→ING bi-encoder (S093 §4.2: Acc@1/R@5 by frequency bucket, ING-grouped splits, leakage guard against lexicon-building corpora); SEFS signature buckets (90% of 1.15M phrases in 91 vectors; RD L704); J1 JEPA linking (optional). Molecule level not covered (FlavorGraph/IMAP PRESENCE only; RGM L44: ingredient→compound qualitative; FoodAtlas quantitative NC).

**36 Evidence compiler → selective CulinaryState-RAG → FlavorTwin.** RD Appendix K is the primary contract: K.2 structured truth/derived vectors; K.3 embed-vs-metadata table; K.5 cards; K.6 chunking; K.7 prefix-safe embeddings; K.9 query planning (exact ledger reads first); K.10 10-step pipeline; K.11 prompt contracts; K.12 context budget (15/25/50/10 candidate); K.13 B0–B7; K.14 relevance Gold & E10.5–E10.15; K.15 gap queue; K.16 no evidence laundering; K.17 adoption. P9 sufficiency routes; G.5 claim ledger; E11 provenance gates; E14.9/14.10 relevance/grounding guards (open-model equivalents). Metrics: graded nDCG, supporting-evidence Recall@K, wrong-basis/process evidence rate, stale-version rate, supported task-success rate, justified abstention, useful coverage, cost (F.4). Gate: G16-DEC/PROV/CAL; E10 "extra tokens alone explain the gain" stop. FlavorTwin: W10 only after L12–15 gates; consumes P3 products/forms + P7 state versions (RD L1287).

---

## 9. Contradictions, stale items, underspecified parts, open questions

### 9.1 Contradictions
1. **Authority rank of RD:** MP v4.0 AG4 (MP L2742–2750) ranks it #4 above the master plan; authority map row 7 ranks it 5 (written against v14); brief §2 order puts MAX/implementation plans at 6. Needs ruling.
2. **Choice option limit:** RD says Jev Choice "up to 255 options" (RD L872, L1901, R2); repo's later review of the Ollama System-One API says `choice` 2–26 options (reports/ner_v2/systemone_decision_model_review.md L9). Different API surfaces (TypeSafe hosted vs Ollama local) — UNVERIFIED which applies; affects the two-stage process mapping design (RD L911).
3. **Reranker default:** RD K.17 recommends "a strong reranker" and E3.2 cross-encoder; repo measured cross-encoders negative for evidence retrieval and structured retrieval superior (S093 L53; BT L20). Silver-label evidence only (headline NEED_DATA, BT L39).
4. **kNN-NER/exemplar retrieval** expected to help tail (RD L155, E1.4); repo null (Δ=0).
5. **Gold tier naming:** repo "Gold-v1 pilot_20 frozen as AI-assisted, human-reviewed development Gold" (D-017) and Food.com v1.1 "AI_ASSISTED_HUMAN_REVIEWED" vs RD L490 "Correction after seeing model output is Gold-Light, never 'independent'" and L482 Deep Gold Sealed "no LLM pre-fill". Not a contradiction if labelled Gold-Light; it is one if used as Deep Gold for calibration/test claims.
6. **TASTEset licence:** RGM L20 "MIT" vs ctx "TASTEset unverified".
7. **Food.com size:** RD ~180k (S72, [U]) vs repo 522,517 Food.com recipes (S133). Different releases → licence/provenance must be pinned.
8. **SSOT line count:** RD says "42k-line SSOT" (RD L535, L2173); v15 is 45,697 lines (stale, harmless).
9. **RecipeDB3 reproduction status:** DFS L45/L57 and S093 L33 "NOT yet run (VPN down)" vs `reports/ner/recipedb3_matched_reproduction.md` showing completed 5-seed results. DFS/S093 stale.
10. **BT RQ16-11 "Claude multi-pass ⛔"** vs RD's Claude Max protocol as central Silver engine; also hard rule here forbids sending project data to external services, while RD envisions Jev/Gemini hosted APIs (RD §17, K.8). For licence-restricted data (BBC A1 RESTRICTED local-only; D-015 DERIVED_ONLY) hosted APIs are effectively excluded.

### 9.2 Stale items (still-valid vs stale)
STALE: 12-week mini-project schedule and DEL-1…5 framing (RD §19–20, App. H; S093 "T-37 days" L4); Jev-centred decision layer (RD §17, E14, App. E) — superseded by open System-One lane, and Jev "two weeks old" (RD L957); RD §1.2 M1–M2 RecipeDB3 tasks (done); E1 legacy NER program (closed S128); S093 ledger counts (REC 89,565 → 612,782 recipe base); BT/DFS statuses; RGM order X14…X8 (completed or superseded); "apply for Jev early access" (RD L1241); INCEpTION vs Label Studio pilot (no evidence done — status UNVERIFIED); Google model watch-list (Gemini 4 Argon etc., RD K.1) — irrelevant under no-external-service rule.
STILL VALID (consistent with SSOT laws and v15 numbering): three identities; lifecycle & flow ops; quantity AST and evidence-route hierarchy; affine temperature; invariants; missingness axes; offset contract; task masks/`labels_annotated_for`; verification tiers; Gold chain; IAA reporting rules; calibration arithmetic; selective risk budgets as [P] targets; split hierarchy & family/study separation; oracle cascades; F.10 stop rules; Appendix G evidence granularity/compatibility/answer classes; Appendix K retrieval contracts (namespaces, cards, prefix-safe embeddings, exact ledger reads, query planning, no evidence laundering); B0–B7 ladder (matches SSOT L26667–26679); release gate wording; SDC.

### 9.3 Underspecified
- No formula/model registry schema, parameter registry, mechanism ontology, kinetic data contract (Steps 21–25 have almost no RD support).
- Effect_class vocabulary undefined (RD L580).
- No explicit mapping of RD G-*/W-gates to SSOT G16-* IDs or to G15-*.
- Silver tier sampling for a 612k corpus with 605k families: how to choose the 60–100k (strata, families, sources) — not specified beyond S1–S6 and active learning.
- Process ontology depth/aliases: only "two-stage family → specific" and 268 Bagler processes; repo has 156 PROC in 18 families. No external standard chosen (e.g., FoodOn process branch, LanguaL facet) — research needed.
- Ingredient facets list (form vocabulary RD L980) is closed but not versioned against FoodOn/LanguaL/FoodEx2 facets.
- Portion/density table schema (POR) beyond `conversion_record_id`; edible fraction, state-dependent density not modelled explicitly (only "edible basis" channel).
- Retrieval Gold size (~80 questions) is acknowledged as pilot; no power analysis.
- Scientific "verification" three-task distinction (RD L2070) not mapped to EVD `verification` enum.
- Risk budgets (2%/1%/5%) are [P]; minimum useful coverage values never set.
- Cultural/historical (L13E) entirely absent.

### 9.4 Open questions needing external research (do NOT send project data)
1. Food ontology facet standards for form/part/processing (FoodOn, LanguaL, FoodEx2) — which to crosswalk for the closed form vocabulary.
2. Authoritative portion/density sources beyond FDC (e.g., FAO/INFOODS density database; Indian household measures like katori) — availability and licence.
3. Current licence status of TASTEset v2, ReciFine/ReciFineGold, RecipeNLG, r-FG (repo location), INDoRI, Mendeley Indian dataset; which Food.com release has 522k recipes.
4. Annotation reliability standards for procedural graphs/coreference (beyond RD targets) and minimum Deep Gold sizes for clustered risk claims.
5. Whether open System-One decision models (Tev1, Nimble) have documented calibration on extraction tasks; weights licences (review notes Tev1 weights licence unstated).
6. Study-disjoint benchmark design for sparse food-process data (MNAR identification limits; propensity methods) — RD flags but does not resolve.
7. Formula/model registry conventions (SBML/BioModels, model cards) — not covered by RD.

---

## 10. LOOK-AHEAD: fields/metadata earlier steps must capture

**Step 03 (state semantics)** must freeze: `entity_id` vs `entity_version_id` vs `concept_id`; `prior_version_id`, `producing_event_id`; lifecycle enum incl. UNRESOLVED; `location`, `phase`, form/product facets, qualitative thermal/texture/visual with provenance; `trajectory` (PLANNED/OBSERVED_SESSION/PREDICTED); `evidence_cutoff{mode: ONLINE_PREFIX|OFFLINE_FULL, step_index}`; control constructs (`control_id`, branch/loop expressions) separate from events; `text_order` vs `depends_on[]`; allocation records (`allocation_id`, parent quantity, basis, branch); planned endpoint objects. Without these, Steps 18/19/22/29/34/36 cannot do prefix-safe or branch-aware reasoning.

**Step 04 (evidence/provenance/similarity)** must add: the four missingness axes per *field* (assertion wrapper), `evidence_origin`, `INFERRED_RULE` (or explicit decision to reject), `CONVENTION` provenance, `calibrated_probability` + `decision_id` + calibration revision; compatibility tri-state; claim types; index `namespace` + `epistemic_type`; similarity-type tag on any similarity output (K.4) so Step 35 never emits a universal scalar; `source_class` per SDC.

**Step 05/07 (EVD and conditions)** must capture for Steps 23–27/29–33: food/product, `part`, initial form/state (`prior_state_id`), process family + specific process ID, temperature as value/range/censored bound with affine-correct units, duration min/max with censoring, medium, heat level, endpoint text, pH/aw/moisture/oxygen if reported (not in RD — flagged as gap for Step 23), analyte/target, unit, **basis (edible/dry/wet/as-served)**, method/platform, replicate count & uncertainty type, LOD/LOQ flags (BELOW_LOD), trajectory vs endpoint designation, table/span pointer. Unit layer must keep `unit_variant`, `unit_system`, `dimension`, `kind` separately and never collapse ranges to midpoints.

**Step 06/08 (manifest, lineage)** must capture: `source_asset_id`, content hash, rights/licence verification level, storage policy (LIVE_ONLY/DO_NOT_STORE/DERIVED_ONLY), external-service permission flag (whether text may leave the machine — needed by any hosted model), locale; for science: `study_id`, `study_family_id`, publication ID/DOI, table ID, experiment/sample IDs, derived-from (e.g., Bognár compiled from primary studies → shared-origin flag), duplicate-table detection, for study-disjoint and publication-disjoint splits (RD L1974, L2082).

**Step 07I (identity)** must preserve: exact-hash group, normalized-hash group, signature group, near-dup candidate pair scores, reviewed family label + sampled precision, dish-family candidate, source family; family IDs propagate to augmentations, translations, teacher labels, retrieval exemplars, prompt demos (RD L555, L1974). The 400-pair labeled precision must exist before any split is frozen.

**Steps 09–15 (extraction/acquisition)** must record: per-row "verified" type (transcription / alignment / comparability); extraction model/prompt hash, assistance visible flag, repair attempts; OCR/table uncertainty; condition completeness vs required-field contract per claim type (G.2) so Step 23 can return INSUFFICIENT_INFORMATION rather than guess; parameter-bearing rows (rate constants, activation energies, D/z values) tagged with model form and validity ranges for Steps 24–27 (RD silent — gap); independence group IDs for Step 27 held-out validation.

**Steps 16–20 (procedure semantics)** must capture for Steps 22, 29, 36: `labels_annotated_for` + task masks + eligible universe per task; raw-section offsets; `process_id` + `process_band` + raw verb kept when UNMAPPED; `effect_class` placeholder; event roles incl. MEDIUM, DESTINATION, CONDITION, ENDPOINT; negation/hypothetical/conditional attributes; OMITTED_STEP_CANDIDATE with `rule_id`/`precedent_ids` outside the observed graph; quantity AST with `source_var` for correlated uncertainty; allocation basis (MASS/VOLUME/COUNT/PORTION_FRACTION_ONLY); `assistance_visible`, annotator IDs, guideline version, adjudication reasons; S1–S6 complexity flags and natural vs challenge membership; frequency-bucket (head/torso/tail/unseen) defined on training counts; recipe family ID on every Gold/Silver record; Silver tier, teacher model ID, audit-sample membership (random vs active-learning; AL picks never sealed).

**For Step 35/36 specifically:** concept cards need registry revision, aliases with locale/source, definitions, negative examples; ingredient-line and event cards need family/split, view hash, prefix-safe flag; evidence cards need study ID, basis, conditions, verification; all vectors need model/version/dimension/template revision; session observations need reported time and target entity.

*End of notes.*
