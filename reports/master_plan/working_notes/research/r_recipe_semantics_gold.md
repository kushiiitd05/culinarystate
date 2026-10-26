# r_recipe_semantics_gold — Recipe procedure semantics, state tracking, ontologies, CQPO, Gold/Silver design

Researcher role: external researcher for spine steps 03, 16, 17, 18, 19, 20 (+ brief §14–16 ingredient/CQPO/process/tool, §31–32 Silver/Gold).
Date 2026-10-22. Read-only on the repo. Nothing implemented. The 36-step plan cards are MISSING (ctx.md). Step contents below are reconstructed from SSOT v15, Master Plan v4.0 and repo artifacts, and are labelled as reconstructions. No text is attributed to the missing plan.
Tags: [V] = I opened the primary page or abstract. [S] = secondary source only. [U] = unverified (my background knowledge, not checked this session).

---------------------------------------------------------------------
## 0. Internal context (what the repo actually says and holds)

SSOT anchors (line numbers in `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`):
- §233 event-sourced state graph, intermediates, merge/split relations, quantity propagation, five memory classes: L25323–25399.
- §234 vocabulary/ontology programme. Canonical concept vs surface string L25424–25440; 10k+ ingredients is "a target, not a quota" (§234.3); compact canonical processes plus modifiers (§234.5 L25459–25462); external ontologies are alignments only (§234.6 L25463–25466).
- §235 CQPO: three-problem separation, Q0–Q6 portion ladder, qualitative quantities, raw+normalized preservation, quantity encoder with masks: L25500–25586.
- §236 data tiers: Deep Gold ~750–1,000; Gold-Light ~3–5k; Silver 60–100k; weak corpus 1M+; synthetic. Also sampling dimensions, stages 0–10 and batch checkpoints: L25587–25658.
- §237 Gold handbook (independence, no anchoring "when avoidable", agreement per task, hard-case list): L25659–25744.
- §240 validation stack V1–V6, validator rules, active-learning priority: L26260–26319.
- §257C field dictionary for Quantity (L30068–30289, 22 fields), PortionProfile (L30290–30471, 18 fields) and Event (L30472–30673, 20 fields). §257D Gold test catalog: L31465–33895. §257P pre-scale checklist: L42705–42743.
- Master Plan v4.0 (`docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md`): B05 process ontology (L329–347, gate ≥95% of Gold-seed process mentions mapped or explicit UNMAPPED); B07 corpus factory (L370–386); B09 vocabulary (L412–427); B10 quantity (L428–446); B11 event/state graph (L447–462); Part J quantity pipeline (L649–689); X1 TOOL ledger (L1923–1945); DEL-3 "≥40 gold recipes + 30 scripted sessions" (L1250).

Repo reality (verified by reading files):
- `ledgers/data/PROC.jsonl` has 552 rows: 534 ACTION and 18 ENDPOINT, in 18 families. **0 rows have a parent**. Mechanism families are "AI-drafted (verify vs R3)".
- `TOOL.jsonl` has 297 rows in 7 categories. `max_safe_temperature_c` is UNKNOWN, which is correct.
- `UNIT.jsonl` has 74 rows: 12 PHYSICAL, 11 CULINARY_VOLUME, 21 COUNT_PORTION, 15 PACKAGE, 15 VERBAL_QUALITATIVE.
- `ING.jsonl` has 5,387 concepts. FoodOn crosswalk: LINKED 1,147 (21%), CANDIDATE 572, NO_MATCH 1,540, UNRESOLVED 2,128. Facets are populated on 616 rows and parent_ids on 854.
- There is no POR/portion ledger file in `ledgers/data/`. WORKLOG L789 (S115) says FNDDS, the FAO Density DB and USDA Cooking Yields R2 were downloaded.
- **Gold status. There is no valid independent human annotation anywhere in the project.**
  - The BBC pilot-20 Gold-v1/v1.1 is AI-drafted. Kush reviewed and approved it, and "Parv = AI-assisted set". Agreement is labelled NOT_INDEPENDENT (WORKLOG S106–S110, L712–757).
  - The Food.com 20 is `AI_ASSISTED_HUMAN_REVIEWED`. It was batch-approved in chat, has empty row decisions, and "agreement trivially 1.0, non-informative" (`reports/gold/foodcom_ai_assisted_human_review.md`).
  - The 7-recipe blind calibration round is `BLOCKED_HUMAN` (`reports/del3/gold_pilot_7_calibration.md`).
  - The Step-07H condition audit is `NOT_COUNTED_PROVENANCE_INVALID`: two files written 11 s apart, pooled kappa 0.998. Three fields are flagged for kappa-paradox risk at prevalence 1.00 (`reports/step07/step07h_human_gate_result.json`).
  - S134 has a 400-pair identity blind packet, UNLABELED.
  - Consequence: SSOT law "Silver ≠ Gold; Gold protected from model anchoring" (SSOT L70, §236.2) is not yet met by any existing artifact. All 40 existing "Gold" recipes should be re-tiered as Gold-Light / MODEL_ASSISTED.

---------------------------------------------------------------------
## 1. Questions

Q1. What is the established representation for recipe procedure semantics and state? Options: flow graph, action graph, state-change tuples. Which elements must the CulinaryState event/state schema keep?
Q2. How good are LLMs (2023–2026) at extracting procedures and graphs, compared with supervised parsers? What should the Step-17 baseline ladder be?
Q3. How should entity/state tracking be evaluated, given what ProPara/NPN/OpenPI/OpenPI2.0 teach?
Q4. Ingredient identity vs state/form/cut: which external ontology pattern should we use, and what mapping strategy?
Q5. Process and tool hierarchy: does a standard ontology exist, and what depth is right?
Q6. Which authoritative portion/density sources exist, and how do we represent uncertainty without fake grams?
Q7. Which annotation reliability conventions apply (alpha/kappa thresholds, kappa paradox), and what sample sizes give useful CIs?
Q8. What is the evidence on LLM pre-annotation anchoring and automation bias, and what Gold protocol follows from it?
Q9. Active learning and Silver QA: what works, and what is the risk?
Q10. What Gold sizes per task, and how should the 612k corpus be tiered and sampled?

---------------------------------------------------------------------
## 2. Findings

### Q1 — Procedure representation (confidence HIGH)
- **Mori et al. 2014, LREC [V].** Japanese r-FG: 266 recipes (200 random plus 66 of one dish). Recipe flow graphs are DAGs whose root node is the final dish. Vertices are recipe named entities (food, tool, action, ...) and arcs are labelled relations.
- **Yamakata, Mori & Carroll 2020, LREC [V].** English Recipe Flow Graph corpus: 300 recipes written by members of the public, with r-NE plus flow graph. IAA is 82.3–90.5 F1. Baseline NER plus dependency-style parser reaches 71.1–87.5 F1. The exact node/edge tag inventory was not shown on the abstract page [U for tag list].
- **Kiddon et al. 2015, EMNLP [V metadata; S content].** Unsupervised hard-EM mapping of recipes to action graphs. Nodes are actions and edges are argument flow, including elided/implicit arguments ("Bake for 50 minutes").
- **RISeC, Jiang et al. 2020, AACL [S content; V metadata via anthology search].** Entities (ingredients, tools, actions), relations, and zero-anaphora resolution linking actions to implicit arguments such as earlier outputs. It deliberately avoids domain-specific predicates.
- **Bhatt et al. 2024, LREC-COLING [V].** End-to-end multitask flow-graph parsing with compact encoders. Pretraining on automatically generated *silver* flow graphs from unlabelled recipes gives a large improvement. This directly supports our weak-corpus → Silver → Gold design.
- **Toyooka, Aizawa & Yamakata 2025, ACM MM 2025 [V].** Japanese recipe dataset with ingredient-state annotations and state-probing tasks for LLMs. Training on state knowledge improves open LLMs.
- **Consensus.** The field has converged on (a) typed entities (food/tool/action/quantity/duration/state), (b) a DAG with intermediates and a final-dish root, (c) explicit implicit-argument links, and (d) per-step state-change tuples. SSOT §233 already contains a superset of (a)–(c): intermediates, MERGES_INTO, SPLITS_INTO, RESERVED_AS, and so on.
- **Gaps in the SSOT Event dictionary (§257C.Event L30472–30673)** against the literature and our own Gold audit:
  - no explicit `implicit_argument` / zero-anaphora flag (RISeC);
  - no alternative/disjunction group (S109 found "or" lines mis-modelled as ALTERNATIVE);
  - no conditional/until/optional/negation marker;
  - no parallel/concurrency relation;
  - no action-vs-endpoint-vs-observation event kind (PROC currently mixes 18 ENDPOINT rows into the process vocabulary).

### Q2 — LLM vs supervised extraction (confidence MEDIUM-HIGH)
- **PAGED, Du et al., ACL 2024 [V].** LLMs (with self-refine) are good at identifying textual elements but "show gaps in building logical structures" (non-sequential logic). [S: the search summary says gateway/flow F1 < 0.5 and fine-tuned Llama2 beats ChatGPT. I did not verify this in the paper.]
- **Gajo, Rosati, Sajjad & Barrón-Cedeño, ACL 2026 main (arXiv 2604.08752) [V abstract].** Across 6 RE datasets, a graph-based parser increasingly outperforms 4 LLMs as the number of relations per input grows. It concludes that lighter parsers are better for complex linguistic graphs. Whether a recipe dataset is among the six: [U].
- **text2flow / multi-agent procedural graph extraction, EACL 2026 Findings [S only].** Refinement rounds are needed because LLM outputs are often ill-formed.
- **OpenPI2.0, Zhang et al., EACL 2024 [V].** Under canonicalized, fairer evaluation, SOTA LLMs are "far from competent" at entity state tracking.
- **Kim & Schuster 2023, ACL [S content, V metadata].** Entity tracking emerges mainly in code-pretrained LLMs. Text-only pretraining does not reliably surface it.
- **Consequence.** LLM extraction is a credible *Silver generator* for spans and attributes, but it is not trustworthy for edges or state structure without validators. A supervised graph parser trained on Silver plus Gold-Light (Bhatt 2024 pattern) is a mandatory strong baseline and a likely winner on edges. This matches the SSOT law "complexity must beat simple baselines" and SSOT L9202: "local LLM not assumed to beat a domain NER model".

### Q3 — State tracking evaluation (confidence HIGH)
- **ProPara, Dalvi et al., NAACL 2018 [V].** ~81k datapoints. It tracks only *existence* and *location* of entities per step, and it shows that implicit effects are the hard part.
- **NPN, Bosselut et al., ICLR 2018 [V venue/abstract].** Actions are state transformers over entity state. [U: six state-change types and the 65k-recipe training subset, from a secondary source.]
- **OpenPI, Tandon et al., EMNLP 2020 [V].** 810 wikiHow paragraphs, 4,050 sentences, 29,928 open-vocabulary (entity, attribute, before, after) tuples. Best model 16.1% BLEU-based F1. OpenPI2.0 fixed this by **canonicalizing entities/attributes and adding salience**, because free-form attributes made evaluation unfair.
- **Consequence for Steps 18/19.**
  - Evaluate state with a **closed, canonical attribute vocabulary** (our `registry/state_variable_registry_v1.csv` / SVAR, 355 rows) plus an explicit OTHER/UNMAPPED bucket.
  - Score three layers separately: (i) existence/creation/consumption (ProPara-style), (ii) location/containment, (iii) attribute before→after with UNKNOWN allowed.
  - Add salience weighting so trivial entities do not dominate.
  - Report exact-match per attribute, not BLEU.

### Q4 — Ingredient identity vs state/form/cut (confidence HIGH on pattern, MEDIUM on mapping yield)
- **FoodOn [V via foodon.org].** OBO Foundry ontology. "over 9,600 generic food product categories". It separates *food products* from *food sources* (organisms or organism parts, reusing NCBITaxon/PO/UBERON). Products link to facets such as harvest state, maturity and food process, and it carries "an extensive list of food processes". It is based on LanguaL's 14 facets and is described as LanguaL's successor [V langual.org]. The FoodOn paper (Dooley et al. 2018, npj Sci Food, DOI 10.1038/s41538-018-0032-6) is behind an auth redirect, so its content is [U].
- **LanguaL [V langual.org, partial].** Faceted thesaurus. A = Product Type, B = Food Source. [S: other letters C part, E physical state, F heat-treatment extent, G cooking method, H treatment applied, from an EFSA slide example.] More than 40,000 foods indexed.
- **FoodEx2, EFSA [V EFSA data-standardisation page; V MCRA docs].** A base term plus facets syntax, e.g. `A01CE#F28.A07LC` (clementine, process facet F28 = peeled), with facets joined by `$`. The current version has nine hierarchies. There is maintenance through 2025. [S: F28 Process is the comprehensive process facet, and F01 Source / F27 Source-commodities / F04 Ingredient distinguish raw vs composite.]
- **Open Food Facts [V GitHub taxonomies folder].** Separate DAG taxonomies, including `ingredients_processing.txt`, `states.txt`, `preservation.txt`, `units.txt`, `sizes.txt`, `brands.txt` and `food_groups.txt`. This is independent evidence that mature systems keep processing/state/size outside the ingredient identity. Licence of the taxonomy files: [U]; the OFF database is commonly ODbL [U].
- **FoodKG, Haussmann et al., ISWC 2019 [S].** Recipe1M + USDA + FoodOn KG with provenance. [S, unverified: linkage gains, e.g. FoodOn linkage ~30% → >90%.]
- **Consensus pattern.** *Identity (base term) × orthogonal facets* (part, physical state, process/treatment, cut/geometry, maturity, preservation, packing, brand). This is the same decomposition as SSOT §234.2 ("2 large ripe tomatoes, roughly chopped" → food, quantity, size, state, form).
- **Our ledger.** Only 21% of concepts are FoodOn-LINKED. Facets exist on 11% of concepts (616/5,387), and there is no explicit cut/geometry or maturity axis yet.

### Q5 — Process and tool hierarchies (confidence MEDIUM)
- **No widely adopted standard cooking-action or kitchen-tool ontology was found.** I found only academic designs: an ISCTE cooking ontology with actions/food/recipes/utensils modules, and an action-graph DSL (arXiv 2509.04159, preprint) [S]. FoodOn's process terms and the FoodEx2 F28 / LanguaL G/H facets cover industrial and nutritional processing and cooking-method *as food descriptors*, not as procedural actions with arguments [S].
- **Consequence.** The internal PROC/TOOL vocabularies remain authoritative (SSOT §234.6). External mappings are SKOS-style crosswalks (exact/broad/narrow/related) to FoodOn process terms, FoodEx2 F28 and LanguaL G/H. Wikidata QIDs are optional for multilingual tool aliases.

### Q6 — Portion/density sources and uncertainty (confidence MEDIUM-HIGH)
- **FAO/INFOODS Density Database [V fao.org page].** Version 2 (and v1) PDF and Excel exist for volume↔weight conversion. Data come from the literature, national food composition tables and the authors' own measurements. Entry count is [U] here because the PDF did not render.
- **FNDDS (USDA ARS) [S snippets of the official ARS PDFs].** Its purpose is to convert WWEIA/NHANES reported portions into grams. FoodWeights (food code, seq, portion code, gram weight) + FoodPortionDesc. [S: 2021–2023 release has 22,046 portion weights.]
- **FoodData Central FAQ [V].** "FoodData Central does not contain a way to automatically modify portion sizes". Serving sizes differ by data type (Branded = label; FNDDS = survey portions; Foundation mostly 100-unit measures).
- **Not found.** No authoritative source exists for Indian household measures (katori, glass) or for verbal quantities (pinch, handful). SSOT §235.5 is right to keep these qualitative.
- **Uncertainty representation.** Store intervals or empirical quantiles with source count and source diversity (SSOT §235.8), keep the Q-level, and propagate intervals through allocations (§233.6). Never use midpoints in Gold (§237.1). This is consistent with how FNDDS/FDC present multiple measure-specific gram weights rather than one density.

### Q7 — Reliability conventions and sample sizes (confidence HIGH on conventions, MEDIUM on applying them to graphs)
- **Krippendorff thresholds [S via Wikipedia, citing Krippendorff 2004 *Content Analysis* 2nd ed. pp. 241–243].** α ≥ 0.800 is relied on. 0.667 ≤ α < 0.800 supports only tentative conclusions. α < 0.667 is discarded. Bootstrapped CIs are preferred (Hayes & Krippendorff 2007, CMM 1(1):77–89 [S]). Krippendorff 2004 HCR 30(3):411–433 [S] covers common misconceptions.
- **Artstein & Poesio 2008, CL 34(4):555–596 [V metadata only].** The standard CL survey of agreement coefficients. Content recalled [U]: prefer chance-corrected coefficients with a single expected-agreement model (α/π family); thresholds are task-dependent; 0.8 is a common bar for reliable data; weighted coefficients give lower values.
- **Feinstein & Cicchetti 1990, J Clin Epidemiol 43(6):543–549 [V via EuropePMC].** Kappa paradoxes: high agreement with low kappa under marginal imbalance, and higher kappa under asymmetric imbalance. Part II (Cicchetti & Feinstein, pp. 551–558) resolves this with positive/negative specific agreement [S]. **This applies directly:** the 07H gate flagged fields with prevalence 1.00.
- **Sample-size arithmetic (my computation, normal approximation).**
  - Accuracy/F1 near 0.85–0.90: n = 500 independent units gives a 95% CI half-width of about ±0.03; n = 1,000 gives about ±0.02.
  - Recipe-clustered units: with 10 events per recipe and ICC 0.1–0.3, 200 recipes give an effective n of about 540–1,050 events.
  - Kappa ±0.05 at observed agreement 0.9: n ≈ 550 when chance agreement is 0.5, but ≈ 3,460 when chance agreement is 0.8 (high prevalence). So rare categories must be **oversampled** and reported with stratum or specific agreement.
  - Zero-failure upper bounds (rule of three): proving a critical-error rate < 1% needs 300 clean audited items; < 0.5% needs 600.
  - Walter, Eliasziw & Donner 1998, Stat Med 17:101–110 [S] gives ICC-based sample sizes. It is useful for continuous fields such as quantity mass.

### Q8 — LLM pre-annotation anchoring (confidence MEDIUM-HIGH)
- **Schroeder, Roy & Kabbara, ACL Findings 2025 [V].** Pre-registered study: 350 annotators, 7,000 annotations. LLM suggestions did not speed annotators up but raised confidence. Annotators largely adopted the suggestions, which shifted label distributions. **Using LLM-assisted labels as the benchmark significantly inflated the LLM's measured performance.**
- **Choi et al., EMNLP 2024, "The LLM Effect" [V].** LLM suggestions speed work but introduce anchoring bias. [S: one annotator's agreement with the LLM rose from 36.6% to 70.7% when suggestions were shown.]
- **Fort & Sagot 2010, LAW IV [V metadata; S content].** Pre-annotation improves speed and quality, but biases appear and must be accounted for.
- **Mikulová et al. 2022, LREC [V].** For dependency syntax with a high-accuracy parser, pre-annotation increased speed and consistency "without reducing quality". This is the counter-evidence. But higher consistency means **IAA under shared pre-annotation is inflated and is not evidence of independent reliability**.
- **"Bias in the Loop", HDSR 2026 / arXiv 2509.08514 [S].** Annotators under-correct LLM pre-annotations.
- **Consequence.**
  - Deep Gold must be annotated **blank (no model output)**, with model output revealed only after the independent pass (if at all) and logged.
  - Model-assisted human review is legitimate only for Gold-Light/Silver QA, carries provenance `MODEL_ASSISTED`, and is **never used to score the model family that produced the suggestions**.
  - All 40 existing project "Gold" recipes fall under this rule.

### Q9 — Active learning and Silver QA (confidence MEDIUM)
- **Lowell, Lipton & Wallace 2019, EMNLP [V].** AL gains over random are inconsistent across models and tasks. Actively acquired sets transfer poorly to successor models.
- **Zhang, Strubell & Hovy 2022, EMNLP [V].** Survey covering AL for structured prediction, cost, and stopping.
- **Consequence.** Use AL/uncertainty selection only for **Gold-Light training/QA queues**, with a fixed random component. Deep Gold (the evaluation set) must be a **probability sample** frozen before models are run. Otherwise evaluation is biased toward the selecting model.
- **Confident learning, Northcutt, Jiang & Chuang 2021, JAIR 70 [V].** Label-error detection via the estimated noise joint. It is a cheap Silver QA signal (cleanlab), alongside SSOT V1–V6 validators and multi-model disagreement.

### Q10 — Gold sizes and tiering: synthesis in §3.

---------------------------------------------------------------------
## 3. Architecture recommendations (and rejected alternatives)

### 3.1 Event/state schema (Steps 03/16/18)
**Adopt:** SSOT §233 + §257C.Event as the core. Add the fields below. Keep an **r-FG export adapter** so the English r-FG corpus (300 recipes, Yamakata 2020) can serve as an external OOD check, subject to licence (licence [U]; check before use).

Event additions:
- `event_kind ∈ {ACTION, ENDPOINT_CHECK, OBSERVATION, CONDITIONAL, WAIT/REST}`. Move the 18 PROC ENDPOINT rows into a separate V_ENDPOINT/V_STATE vocabulary.
- `implicit_args[]`, each with a `resolution_ref` to a prior entity/intermediate (zero anaphora, as in RISeC).
- `alternative_group_id` (for "or" lines and alternative steps).
- `modality ∈ {REQUIRED, OPTIONAL, NEGATED, CONDITIONAL}` plus raw cue.
- `temporal_relation` (SEQUENTIAL/PARALLEL/OVERLAPS/UNTIL) to support the concurrency failures LLMs show.
- `condition_profile_id`, pointing to a Step-07 COND profile rather than flat temperature/duration only.
- `allocation` with a fraction basis (for "half of the reserved sauce").
- `heat_transfer_mode` / `transformation_mode` (mechanical / thermal / chemical / biochemical / transfer / temporal).
- `tool_roles` (instrument vs container vs heat source).

State layer: per entity-version, give existence/creation/consumption, location/container, and attribute tuples (SVAR attribute, before, after, value-or-UNKNOWN, provenance). Mark salience.

Rejected:
- (a) Free-form OpenPI-style attributes: unscoreable, as OpenPI2.0 showed.
- (b) A latent-only state (NPN-style) as the stored truth: violates "static representation ≠ transition" and SSOT §233.3 replayability. A latent model may be a *model* on top.
- (c) A pure linear step list: loses merge/split/intermediates.

### 3.2 Ingredient hierarchy and mapping (Step 16 look-back to the B09 vocab)
**Adopt the FoodEx2/FoodOn pattern.** `ING` = identity base term (food source + part where identity-defining, e.g. egg yolk vs egg). Orthogonal facet axes:
`V_VARIETY · V_PART · V_FORM (whole/ground/paste/juice) · V_CUT_GEOMETRY (diced/sliced/julienne + size class) · V_STATE (raw/cooked/ripe/frozen/dried) · V_MATURITY · V_PRESERVATION · V_PACKING · V_BRAND→PRODUCT layer · V_LOCALE_SENSE`.
- Shallow is-a hierarchy (≤4 levels, e.g. produce › allium › onion › red onion) plus `COMPOUND_FOOD` kind, with optional decomposition links (never forced).
- Crosswalks are 1:n with SKOS relation + confidence + status. Order: FoodOn (primary, open, OBO) → FDC/FNDDS (nutrition/portion) → FoodEx2 (EU exposure, optional) → LanguaL via FoodOn. Keep NO_MATCH as a valid state (SSOT §234.6).
- Measure mention-weighted coverage, with separate long-tail and regional coverage (SSOT §234.3), not concept counts.

Rejected:
- Whole-string canonical concepts ("chopped red onion"), which explode concept counts.
- Forcing FoodOn IDs as identity: only 21% linked today, and wrong links are worse than NO_MATCH.
- LanguaL as primary: superseded by FoodOn.

### 3.3 Process / tool hierarchy depth (Step 16)
**Process (3 levels + modifiers):**
1. **family**, ~15–20 heat/transfer-mode families, keeping the current 18 minus ENDPOINT/SERVING housekeeping;
2. **canonical process**, ~150–300, each with definition, required condition axes and typical medium/tool (B05 fields);
3. **surface alias**, unbounded and language-tagged.

Orthogonal modifiers: intensity, granularity/geometry, endpoint (as a separate ENDPOINT/STATE vocabulary), medium, tool, duration class.
- `transformation_mode` is a separate axis (manual/mechanical vs thermal vs biochemical/fermentation vs chemical/curing vs transfer vs rest). Do not merge it with family.
- Every PROC row needs `parent_id`; today 0/552 have one.
- Mechanism families are a *candidate-effects* link for Step 22, marked AI_DRAFTED until evidenced.

**Tool:** category (heat source / cookware / vessel / utensil / appliance / measure) → tool → alias. Attribute axes: material/coating, heat-transfer mode, pressure capability, capacity. Safety limits stay UNKNOWN unless there is manufacturer/authority evidence (Master Plan X1 L1923–1945).

Rejected:
- A deep (>4 level) process taxonomy: no external standard to anchor it, and LLM mapping error grows with depth.
- A flat 10k process list (SSOT §234.5 forbids it).

### 3.4 CQPO fields (Step 16/17; B10)
Keep §235 and the §257C Quantity/PortionProfile fields. Add or clarify:
- `quantity_scope ∈ {INGREDIENT_LINE, INSTRUCTION_ALLOCATION, YIELD/SERVING}`;
- `basis_ref` for allocations;
- `multiplier` (e.g. "2 × 400 g");
- `dual_expression` consistency check for strings like "1 cup (240 ml)", with a flag on conflict;
- `measured_state` (raw/cooked/drained/packed/sifted: "1 cup cooked rice" ≠ raw rice);
- `as_purchased_vs_edible` + `edible_fraction_ref` (refuse);
- `density_record_ref` with temperature/condition where known;
- `interval_semantics ∈ {SOURCE_RANGE, CONVERSION_UNCERTAINTY, EMPIRICAL_QUANTILES}`, so a source range "1½–2 cups" is never confused with conversion uncertainty;
- `locale_evidence` (where the locale assumption came from).

Grounding order: Q0 exact → Q1 FNDDS/FDC portion → Q2 FAO/INFOODS density → Q3 multi-source → Q4 corpus empirical (flagged) → Q5 model → Q6 UNKNOWN.
Gold annotators never convert units. Gold for grounding = *which portion record applies*, or UNKNOWN.

Rejected:
- A single density per ingredient.
- Midpoint imputation.
- LLM "common-sense grams" (SSOT §235.5 / Part J SX-10-02 "invented grams must be 0").

### 3.5 Tiering of the 612,782-recipe corpus (Step 20) and sampling
Unit of independence = provisional duplicate/dish family from 07I-R (605,476 families). **Assign families to tiers and splits before any sampling.** Over-merging is acceptable for leakage control.

| Tier | Size | Processing | Selection | Use |
|---|---|---|---|---|
| T0 weak corpus | all 611,714 exact reps | deterministic only (07H-R parser, lexicons, frozen NER/linker); no LLM | all | vocab/alias statistics, long-tail discovery, silver pretraining of parsers (Bhatt 2024) |
| T1 Silver | 10k pilot → 25k → 60k; 100k only if utility curve still rising | LLM structured extraction + V1–V6 validators + 2-model disagreement + confident-learning flags | stratified probability sample, **1 recipe per family**, SSOT §236.3 strata; **source cap** (Food.com is 522,517/612,782 ≈ 85% of the base; cap its share, e.g. ≤50% [suggested, not SSOT]); BBC restricted stays local-only | parser training/distillation, statistics, state graphs |
| T2 Gold-Light | 3–5k *units* (lines/mentions/events), not 3–5k recipes | single human review, model-assisted allowed, ≥15–20% double-blind for IAA | ≥70% uncertainty/disagreement/frequency-impact queue + ≥30% random | linker/quantity/process tuning, validator calibration, AL; **not final test; never scores the suggesting model** |
| T3 Deep Gold | staged: DG-0 30 → DG-1 200 → DG-2 ~500 → 750–1,000 only if CI analysis requires | 2 independent blank annotations + adjudication + validators; model output hidden | stratified random from families **held out of T1/T2 entirely**, frozen sampling frame with inclusion probabilities; hard strata (§237.5) oversampled but weighted | dev/calibration/test (locked), confidence calibration (§242), RAG state cases |

Sampling: disproportionate stratified sampling, with inclusion weights recorded so population-level metrics can be Horvitz-Thompson weighted. Report weighted metrics and per-stratum metrics with cluster (recipe-family) bootstrap CIs.

### 3.6 Gold sizes per task (justification in Q7 arithmetic)
| Task | Unit | Recommended Gold | Rationale |
|---|---|---|---|
| Ingredient-line structure (food head/qty/size/state/form) | line | 1,500 lines dual (≈ DG-1 recipes' lines + §257D catalog) | exact-match ±2% |
| Quantity parse | line | §257D catalog (deterministic tests) + 1,000 stratified real lines incl. ranges/packages/qualitative | ±2–3%, rare types oversampled |
| Portion-record selection | line | 300–500 Gold-Light (single + 20% double) | decision accuracy ±4% |
| Ingredient entity linking | mention | 2,000–3,000 Gold-Light by frequency bucket (head/torso/tail/regional) | per-bucket ±4–5% |
| Process/tool mapping | mention | 1,000 process + 500 tool mentions | supports the B05 gate "≥95% mapped or UNMAPPED" with CI ±1.4% |
| Events/edges/coref/merge-split | recipe | DG-1 = 200 recipes dual-blind (≈2k events; eff. n ≈ 540–1,050) | F1 ±0.02–0.04; ≥ public r-FG scale (300) by DG-2 |
| State trajectories (Step 19) | recipe×cut | 60 recipes dual-blind + 30 scripted sessions (DEL-3 asks ≥40 + 30, L1250) | pilot; widen to DG-1 later |
| Duplicate identity | pair | existing 400-pair blind packet, stratified by similarity band (~100 per band) | threshold calibration ±5–10% per band; extend bands near threshold |
| Condition audit (07H) | condition | 100 rows blind ×2 (existing packet) + oversample rare codes | report raw + specific agreement (kappa paradox) |

Agreement gates: α ≥ 0.80 (or span/edge F1 ≥ 0.80, which is near the r-FG human range of 82.3–90.5) for fields used in final claims. 0.667–0.80 means revise the handbook and re-calibrate. < 0.667 means redesign or drop the category. These are conventions, not laws, so they are pre-registered. Never gate on pooled kappa alone. Report raw agreement, prevalence and per-class specific agreement.

Hours (UNVERIFIED estimate; measure in DG-0): deep annotation is perhaps 30–60 min per recipe per annotator. DG-1 (200 recipes × 2 + 25% adjudication) would then be roughly 250–500 h. **This is the dominant bottleneck.** DG-0 must time it, and DG-1 should be resized from the measured rate.

Rejected:
- (a) Making SSOT's 750–1,000 Deep Gold a precondition for Steps 17–20: blocks the path, and a CI analysis shows 200 already supports ±0.03–0.04.
- (b) Upgrading Silver or model-assisted labels to Gold.
- (c) AL-selected Deep Gold.

---------------------------------------------------------------------
## 4. Per-step changes (reconstructed step identity; the cards are missing)

**Step 03 Freeze state semantics.** Status: MP-1 contract `reports/h_state/state_representation_contract_v1.md` is DRAFT FOR REVIEW.
Add and freeze:
- the identity separation ING ≠ ENTITY/version ≠ STATE ≠ PROC ≠ COND (already in the contract);
- a closed attribute vocabulary for state = SVAR plus OTHER;
- event_kind and modality enums;
- tier definitions T0–T3 and provenance enum values `MODEL_ASSISTED_HUMAN_REVIEWED` vs `INDEPENDENT_HUMAN` vs `ADJUDICATED`;
- metric definitions per task (span F1, typed edge F1, coref accuracy, state-attribute exact match with UNKNOWN as a class, quantity structure exact match);
- the agreement-reporting protocol (α + raw + specific agreement + bootstrap CI).
Gate: humans approve the contract. Fail action: no Step-16 schema freeze.

**Step 16 Instruction semantic schema.**
- Outputs: Event/State/Quantity schema v1 (fields in §3.1/§3.4); PROC with parent_id and the 3-level hierarchy, with ENDPOINT moved out; TOOL hierarchy; facet vocabularies (§3.2); handbook v2 with decision trees (SSOT §257A); r-FG export adapter; **Deep Gold sampling frame + family hold-out frozen and pre-registered here**.
- Experiment DG-0: 30 recipes, 2 annotators, blank, timed. It measures α per field and minutes per recipe.
- Gate: α ≥ 0.80 (or F1 ≥ 0.80) on core fields; mapping coverage ≥95% mapped-or-explicit-UNMAPPED (B05).
- Fail: revise the schema/handbook and repeat DG-0 on 30 *new* recipes. Do not re-score the same ones as independent.

**Step 17 Instruction-level extraction.**
- Baseline ladder, all scored on DG dev only (test locked):
  - B0 deterministic rules/lexicon + 07H-R quantity parser;
  - B1 frozen NER (DeBERTa+CRF, S128) + BGE linker + heuristic recency coref;
  - B2 supervised graph parser (biaffine/dependency-style, as in r-FG) trained on T0 silver + Gold-Light;
  - B3 LLM constrained-JSON extraction + validators;
  - B4 LLM + self-refine / verifier;
  - B5 cascade/distilled small parser.
- Metrics: per-label span F1, link accuracy@1/@k, quantity structure exact match, event F1, typed edge F1, implicit-arg resolution accuracy, merge/split F1, validator-failure rate, cost per recipe. CIs are cluster-bootstrapped by family.
- Hypothesis to test: B2 ≥ B3 on edges (PAGED; Gajo 2026).
- Leakage: train families ∩ DG families = ∅.

**Step 18 Event-sourcing engine.**
- Replay invariants (SSOT §240.2 V4): no use before creation; every intermediate has a producer; merge/split consistency; interval quantity propagation with correlated splits.
- Outputs:
  - prefix state packets;
  - a **transition-tuple export** (entity_state_before, event/process, condition_profile_id, entity_state_after, provenance) for Steps 22/29;
  - planned vs observed state.
- Metrics:
  - replay determinism 100%;
  - invariant violations 0 on Gold;
  - existence/location/attribute accuracy vs DG (ProPara/OpenPI2.0 style, canonical attributes, salience-weighted).

**Step 19 Gold state-trajectory pilot.**
- Re-tier the existing 40 recipes (BBC 20 + Food.com 20) to Gold-Light/MODEL_ASSISTED.
- Build 60 new recipes dual-blind + adjudication, plus 30 scripted sessions (DEL-3).
- Gate: α/F1 ≥ 0.80 on state attributes, using raw + specific agreement for high-prevalence attributes.
- Compare compiler-predicted vs Gold states (B3/B4 cascade from S107).

**Step 20 Scale procedural semantic corpus.**
- Tiering and sampling as in §3.5. Stage 10k → 25k → 60k with per-batch acceptance audit: stratified n ≈ 300 per 5–10k batch gives a zero-failure upper bound of 1% on critical errors (fabricated temperature/grams/pH). Error-rate estimates ±2% need about 460.
- Silver-utility curve (RQ16-09): scale beyond 25k only if a B2/B5 parser trained on more Silver improves DG-dev by a pre-registered margin. Otherwise stop.
- §257P checklist before 60k.
- Dataset card + source/region distribution (§236.7).

---------------------------------------------------------------------
## 5. Look-ahead requirements for earlier steps
- **Step 07 (COND):**
  - Events must reference a `condition_profile_id` with per-axis MEASURED/RANGE/UNKNOWN status.
  - Fix the calendar-month→seconds ingest bug flagged in `step07h_human_gate_result.json` before Step 16 links events to COND.
  - Redo the 07H human audit blind (it currently does not count).
  - Oversample rare codes, because 3 fields have prevalence 1.0 and kappa is uninformative there.
- **Step 07I (identity):** label the 400-pair packet blind *before* the Deep Gold frame is frozen. Families must be fixed before tier/split assignment (SSOT §240.2 "duplicate-group members remain in the same final split").
- **Step 04 (provenance/similarity contracts):** add the `MODEL_ASSISTED_HUMAN_REVIEWED` provenance class distinct from independent human, and the rule "never evaluate a model on labels it suggested".
- **Steps 21–23 (mechanism):** need entity facets (cut geometry/size class, moisture-relevant state, medium, container/lid). Step 16 must capture them as facets/modifiers, not text.
- **Step 29 (transition bootstrap):** needs the Step-18 transition-tuple export, with UNKNOWN masks and no imputed conditions.
- **Step 36 (RAG):** needs prefix state packets, state history and Deep Gold calibration cases (§242). DG-2 (~500) should be in place before Step 36 calibration.
- **Step 35 (representation):** the quantity encoder needs masks for missing mass/volume/count (§235.7). Silver must keep raw + normalized + Q-level.

---------------------------------------------------------------------
## 6. Residual uncertainty and pilot vs reading
- Human minutes per Deep-Gold recipe: unknown. **Measure in DG-0 (30 recipes, timed).** This is far cheaper than more reading and decides DG-1 size.
- Achievable α for implicit-argument and state-attribute fields on our schema: unknown. r-FG gives 82–90 F1 for its simpler schema. Measure in DG-0.
- LLM vs supervised parser on *our* edges: the literature direction is MEDIUM-HIGH (parsers win on complex graphs), but it is untested on recipes with our schema. Steps 17 B2 vs B3 decide it empirically.
- Licences: English r-FG corpus [U], OFF taxonomies [U], FNDDS/FDC (US government; commonly public domain [U]).
- Portion coverage for Indian/regional measures: no authoritative source exists, so expect Q4/Q6.
- Further literature search is unlikely to change these recommendations (§8 stop rules 1, 2 and 5 are met). **An empirical pilot (DG-0 + a B0–B3 bake-off on 30 recipes) is now cheaper and more informative than more reading.**
