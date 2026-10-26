# READER ssot_l13 — SSOT v15 Level 13 §§186–194 (L13364–L15365)

Reader: ssot_l13 · 2026-10-22 · read-only · SSOT = `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (all "L" numbers are SSOT line numbers unless prefixed by a file).
I read the full bodies at L13362–L15397 (plus §195 change register L15366–L15397, §196.3 L15462–L15505), and checked cross-references at §85 (L4712–4745), §124.x (index L7603–7696, title only), §238.15 (L25764–25775), §257C Recipe.20 (L29532–29540), §257G.9 (L34854–34862), §247.13/§247.23 (L27025–27031, L27225–27232), §260.4/§262 L13E crosswalks (L42970–42985, L43280–43312), §279 (L45457, L45482).
Repo facts checked read-only: `reports/step07i/final_recipe_database_statistics.md`, `reports/step07i/preregistration_v1.md`, `reports/step07i/feature_file_integrity_report.md`, `reports/step07i/max_plan_consensus.md`, `tools/build_recipe_base.py`, `src/culinarystate/recipes/corpus.py`, `tools/step07i_consensus.py`, `registry/ssot15_similarity_registry.csv`, `registry/ssot15_state_experiment_map.csv`, `ledgers/data/REC.jsonl` (stdlib-profiled), `data/external/foodcom/PROVENANCE.json`, the Master Plan v4.0 (B14 L485–495, Part L L719, Track C L4635–4660).
Missing 36-step plan: nothing below is attributed to its step cards. Where I map to steps (§8) that is MY reconstruction from SSOT + the brief §9 titles.

---

## 0. One-paragraph verdict

Level 13 is a **conceptually complete, empirically never-run** specification (L13368–13372: "Empirical validation / code gates: NOT YET RUN"; "Default recipe encoder: NONE FROZEN"; "Default cuisine encoder: NONE FROZEN"). It is a well-built *baseline-first, confound-first* program: explicit ladders R0–R9 (L13779–13789), C0–C8 (L14337–14345), O0–O7 (L14714–14721); five gates G13-0…G13-4 (L15118, L15139, L15157, L15171, L15191); a 12-item completion checklist (L15266–15277); a permanent promotion rule (L15310–15329). In the 36-step spine its natural home is **Step 35** (representation ladder), but its **data contract (§192, L14942–15098) and split policy (§191.3, L14774–14801) are look-ahead requirements on Steps 03/04/07(07I)/16–20**. The single most decision-relevant finding is that the repo's two required L13 supervision/leakage variables are in poor shape: (a) **explicit cuisine labels cover only 9.81% of the 612,782 recipes and Food.com has 0%** (`final_recipe_database_statistics.md` CULTURE_REGION_HISTORY), and in REC 153 of the 156 cuisine-labelled sources carry exactly **one** cuisine label (source-level book labels → cuisine ≈ source; my stdlib profile of `ledgers/data/REC.jsonl`); (b) the implemented `duplicate_group_id` is **exact-copy only** (`preregistration_v1.md` §1 Level A: "No near-duplicate is auto-coalesced"; HIGH_CONFIDENCE_NEAR_DUPLICATE_GROUPS = 0), whereas SSOT §191.3 requires the split group to contain "Near duplicates / mirrored recipes / cross-source copies" (L14782–14785). Both need decisions before any Step-35 benchmark; neither blocks Step 08.

---

## 1. Definitions, entities and data contracts

### 1.1 Status and scope (§186.1, L13366–13396)
- Status block L13368–13373: learning/conceptual spec COMPLETE; research design "COMPLETE enough to execute once required Level-12 inputs are frozen" (L13369); empirical gates NOT YET RUN (L13370); no default recipe or cuisine encoder frozen (L13371–13372); next learning level L14 (L13373).
- Object chain z_m → z_i → z_R → z_C (L13377–13387); definitions L13391–13394.
- Purpose statement L13396: "not to choose a transformer because recipes are text, nor to average learned vectors and call them culinary meaning … whether the learned representation adds value beyond explicit classical statistics."

### 1.2 Fourteen frozen design rules (§186.2, L13400–13413) — quoted ids
1 composition ≠ procedure (L13400); 2 presence ≠ quantity ≠ role ≠ sensory contribution (L13401); 3 same ingredient set ≠ same recipe (L13402); 4 same cuisine ≠ same recipe (L13403); 5 cuisine ≠ average recipe (L13404); 6 recipe frequency / ingredient popularity ≠ culinary importance (L13405); 7 cuisine prevalence ≠ specificity/authenticity ≠ χ_i (L13406); 8 text similarity ≠ culinary similarity (L13407); 9 attention ≠ causal importance (L13408); 10 learned pair interaction ≠ mechanism (L13409); 11 embedding interpreted relative to its training objective (L13410); 12 **training signal and headline evaluation target must not be the same underlying quantity** (L13411); 13 **recipe size, cuisine corpus size, source, language, profile coverage and global ingredient frequency are mandatory confound audits** (L13412); 14 L13 may consume L12 representations but "cannot inherit credibility from architecture alone" (L13413).
These map 1:1 onto brief §3 permanent laws (attention ≠ causality; structural ≠ sensory; presence ≠ abundance ≠ importance; complexity must beat simple baselines).

### 1.3 Inherited classical baselines (§186.3, L13417–13431)
Incidence; prevalence/frequency; recipe-size distribution; overlap/Jaccard/cosine/IDF; pair/triplet prevalence & itemsets; N_s, null-relative effects, cross-cuisine normalization; χ_i; category composition; authenticity/relative prevalence; cuisine fingerprints (§85, L4712–4745); cross-cuisine size/coverage controls (§124.x, L7603–7696). Rule L13431: "A learned z_R or z_C is promoted only if it adds measurable information beyond the appropriate explicit baseline."

### 1.4 Notation / per-ingredient metadata (§186.4, L13435–13486)
- R = {i_1..i_nR} (L13438).
- **x_{i,R} = [quantity, role, state, position, evidence, context]** (L13444–13453) — this six-slot vector is the de facto per-mention field contract L13 expects from upstream semantics.
- R^proc = (a_1..a_T) (L13459–13462); G_R = (V_R, E_R) (L13467); C = {R_1..R_NC} (L13473); z_R = E_R(R, views) (L13479); z_C = E_C({z_R}, explicit views) (L13485).

### 1.5 Recipe views and their preconditions (§187)
- **R0 incidence** x_R ∈ {0,1}^M (L13497–13509); preserves identity, size, co-occurrence; does NOT preserve quantity, role, state, sequence, intermediates, tool/medium/condition, sensory (L13517–13525); mandatory (L13527).
- **R1 mean z_i** (L13533–13538); failure "all ingredients receive equal importance" (L13545); control role (L13548).
- **Quantity view** z_R^qty = Σ q z / Σ q (L13555–13561); requires "explicit unit conversion and serving/batch context" (L13564); frozen warning mass ≠ sensory contribution (L13570–13576).
- **Role view** r_{i,R} ∈ {base, protein, fat, aromatic, spice, acid, sweetener, thickener, garnish, starter, …} (L13583–13595); role provenance classes: explicitly annotated / extracted from procedure/context / weakly inferred / unknown (L13610–13613); "must not be hallucinated from ingredient identity alone" (L13615).
- **State view** (i,s), z_{i,s} (L13622–13628); onion / chopped / fried / caramelized are not equivalent (L13634–13640); this is the L14 bridge, but L13 must "first separate static recipe composition from process-conditioned state evolution" (L13642).
- **Set vs sequence**: set view appropriate for similarity, itemsets, some retrieval/classification, fingerprints (L13654–13659); order matters because T_p2(T_p1(S0)) ≠ T_p1(T_p2(S0)) (L13671–13675); boxed: ingredient-set embedding ≠ complete procedural representation (L13680–13684).
- **Graph view**: nodes ingredient, ingredient state, action/process, tool, medium, intermediate entity/product (L13697–13702); edges participates-in, transforms input→output state, precedes, intermediate becomes later input, tool/medium used by (L13706–13710); "consumes the semantic-parsing/state-reconstruction track (§§152–156)" (L13712); "Graph representation is a hypothesis, not a default." (L13714).
- **Text view** z_R^text = E_text(title, ingredients, instructions, …) (L13719); confounds website style, author voice, formatting, measurement conventions, duplicated prose (L13724–13728); "text requires source-disjoint and duplicate-group controls" (L13730).
- **Multi-view** Z_R = {ingredients, quantity, role, state, process, graph, text, sensory} (L13737–13747); principle "preserve factorization until the downstream task requires fusion" (L13753–13755).
- What z_R may preserve (task-dependent) L13764–13772; "No single representation is required to optimize all of these simultaneously." (L13774).

### 1.6 Cuisine-level definitions (§189)
- z_C^mean (L14077–14080), failure assumption "all recipes are equally representative" (L14088–14090).
- **Prevalence fingerprint** P(i|C) = #{R∈C: i∈R}/N_C, x_C = [P(i_1|C)…P(i_M|C)] (L14100–14116) — "strong, interpretable baseline" (L14119).
- **Specificity / relative prevalence** A_i^C = P(i|C) − (1/(K−1)) Σ_{C'≠C} P(i|C') (L14124–14129); boxed specificity/authenticity ≠ historical cause (L14141–14145). (Note: §188.2 L13870–13874 writes the same quantity with (C−1); §189.3 uses K — notation inconsistency, see §9.)
- **TF-IDF cuisine fingerprint**: TF = P(i|C), IDF_i = log(K / #{C: i occurs in C}) (L14153–14169).
- **Motifs** P(i,j|C), PMI(i,j|C) = log P(i,j|C)/(P(i|C)P(j|C)) (L14181–14194); triplets P(i,j,k|C) (L14200); "Sparse storage/support thresholds are required" (L14205).
- **Distributional cuisine** p(z_R|C) and mixture Σ π_k N(μ_k, Σ_k) "as a modeling family, not an assumption" (L14213–14225).
- **Hierarchical labels** country → region → subcuisine (L14282–14286); "geographic proximity is not assumed to equal culinary similarity" (L14289).
- **Fingerprint vs embedding** (L14293–14314): x_C = [prevalence, specificity, motifs, category composition, N_s/null effects, χ_i summaries, …]; "The embedding … does not replace the explicit fingerprint baseline" (L14314).
- Multi-view Z_C = {ingredient, pairing, recipe, process, sensory, context} (L14321–14329); context covariates (geography, agriculture, trade, economics, religion, history, technology) "do not by themselves establish causality" (L14332).

### 1.7 Data-engineering contract (§192, L14942–15098) — field level
Status note L14944: "v10 synthesis … extends the v9 identity/state/evidence rules rather than replacing them."

**§192.1 Recipe master table (L14948–14959)** — minimum fields:
`recipe_id`; `title`; `source_id/source_url`; `cuisine/subcuisine labels with provenance`; `language`; `duplicate_group_id`; `servings`; `total/prep/cook time where available`; `split_id`; `evidence/provenance flags`.

**§192.2 Recipe–ingredient edge table (L14963–14981)** — one row per canonical recipe–ingredient relation:
`recipe_id`; `ingredient_id`; `raw phrase`; `canonical ingredient`; `quantity value/range`; `unit`; `normalized quantity if derivable`; `preparation/form`; `state`; `role if explicit/inferred`; `source span/provenance`; `confidence`; `missingness flags`. Rule L14981: membership binary for set/itemset baselines unless a quantity-aware task explicitly uses weighted information.

**§192.3 Recipe event/state table (L14985–15004)** — reuses §§152–156; S_0 → a_1 → S_1 … S_T (L14988); fields `action`; `input entity/state`; `tool`; `medium`; `temperature`; `time`; `output entity/state`; `event order`; `explicit vs inferred`; `confidence`. "This table feeds R8/R9, not the first recipe-set baselines." (L15004).

**§192.4 Cuisine ontology (L15008–15017)** — explicit hierarchy cuisine / subcuisine / region / country; "Do not silently conflate geography with cuisine identity." (L15015); "Every label requires source/provenance." (L15017).

**§192.5 Source and duplicate registry (L15021–15030)** — "Required for leakage control": `source_id`; `canonical URL`; `scrape/acquisition date`; `duplicate_group_id`; `near-duplicate score/method`; `translated/parallel version identifier where known`. Directive L15030: **"Split duplicate groups before model training."**
- Elsewhere: §238.15 lists `duplicate_group_id` as a required Recipe field, "typed/versioned; nullable only according to the schema" (L25770); §257C Recipe.20 (L29532–29540) requires "one stable documented meaning per schema version" and "semantic reinterpretation requires a schema/version migration" (L29538); §257G.9 split integrity: "duplicate groups crossing splits (must be zero under policy)" (L34857); §242-area checklist "duplicate grouping runs before split assignment" (L42720); L13E: temporal copies "Build lineage/near-duplicate groups and assign them wholly to one split" (L44097).

**§192.6 Motif tables (L15034–15042)** — sparse singleton/pair/triplet prevalence; optional PMI/lift/support/confidence; category motifs; "explicit baselines and diagnostics, not necessarily learned inputs".

**§192.7 Recipe representation registry (L15046–15056)** — per z_R artifact: encoder version; ingredient representation version; aggregator; objective; dimension; normalization; data/split version; checkpoint; random seed.

**§192.8 Cuisine representation registry (L15060–15069)** — recipe representation dependency; aggregation method; corpus-size matching regime; recipe-size matching regime; source filters; explicit views fused; objective/checkpoint; seed/version.

**§192.9 Missingness policy (L15073–15082)** — separate flags: quantity missing; role missing; state missing; process conditions missing; cuisine label uncertain; text/instructions missing. "Unknown is not zero." (L15082).

**§192.10 Data-quality audits (L15086–15098)** — duplicate/near-duplicate recipes; alias collisions; cuisine-label inconsistency; source imbalance; recipe-size distribution by cuisine/source; ingredient-frequency distribution; quantity-unit consistency; role/state coverage; procedure extraction coverage; rare ingredient/motif support; missingness by source/cuisine.

### 1.8 Repo reality vs §192 contract (verified, read-only)
| §192 field | Where it lives today | Status |
|---|---|---|
| recipe_id, title, source_id | `ledgers/recipe_base/recipe_base_v1.parquet` BASE_SCHEMA (`tools/build_recipe_base.py` L40) | PRESENT |
| source_url / canonical URL | REC has `source_url` (107,760 REC rows only); Food.com rows have pointer `data/external/foodcom/recipes.parquet#RecipeId=` (`corpus.py` iter_foodcom); `MIRRORED_COPY|canonical_url` groups = 0 | PARTIAL |
| cuisine/subcuisine with provenance | `cuisine_if_explicit` (single string, no hierarchy, no provenance field, multi-labels as "American\|French") | PARTIAL; 9.81% coverage; FOODCOM 0.0%; 256 distinct REC values incl. artifacts e.g. "New" (121) |
| language | `language` = "en" for 612,782 (all) ; `locale` en-US/en-historic/en-GB/en | PRESENT but uninformative (cross-language §190.14 not testable) |
| duplicate_group_id | `ledgers/recipe_identity/recipe_identity_fk_v1.parquet` (`recipe_id -> duplicate_group_id -> recipe_family_id`, `max_plan_consensus.md` row 24) | PRESENT, **exact-only semantics** |
| near-duplicate score/method | `candidate_pairs_v1.parquet` (744,615 stored pairs; ranking score not a decision); provisional families PROVISIONAL_STAR_V1 `calibrated=false` | PROVISIONAL / UNCALIBRATED; 400-pair packet UNLABELED |
| servings | Food.com `RecipeServings`/`RecipeYield` exist in the raw parquet but are NOT read by `iter_foodcom` (columns list: RecipeId, Name, PrepTime, CookTime, TotalTime, quantities, parts, instructions, RecipeCategory) | MISSING in recipe_base (SSOT §238.15 also requires `servings_raw`, `servings_normalized`, L25764–25765) |
| total/prep/cook time | Food.com `structured_times` captured; TIME_STRUCTURED_FIELD 1,479,788 expressions (step07h report L87) | PRESENT (Food.com) |
| split_id | step07h report L57: `SPLIT | 0 | 0 | BLOCKED_FUTURE_STEP`; DECISIONS L135 "NO split frozen" | MISSING (correctly deferred) |
| scrape/acquisition date | Food.com PROVENANCE.json `downloaded_utc 2026-10-20`; per-recipe not stored | PARTIAL (source-level) |
| author / uploader id (needed for Food.com "source-entity" split, see §9) | `AuthorId` exists in raw parquet; not read by `iter_foodcom` | MISSING |
| publication date (temporal split §191.3) | `DatePublished` read ad hoc by `tools/step07i_consensus.py` era_map (L54–55) into an era string; not a recipe_base column | PARTIAL |
| Food.com `Keywords` / `RecipeCategory` (candidate cuisine/dish-type tags) | `RecipeCategory` stored in `extra.category`; `Keywords` not read | PARTIAL; whether Keywords carry cuisine tags is UNVERIFIED here (not inspected) |
| edge table: raw phrase, quantity, unit, form/state, confidence | ING_SCHEMA (`raw_span`, `candidate_ingredient_id`, `link_confidence`, `quantity_raw`, `unit_raw`, `form_state_modifiers`), QTY_SCHEMA (mass/volume/count with intervals + status) | PRESENT (quantity normalization partial) |
| role | no role column in ING_SCHEMA | MISSING (correctly — SSOT forbids hallucinating it) |
| state (separate from form) | `form_state_modifiers` only (string) | PARTIAL; no typed state |
| event/state table | PROC_SCHEMA has actions + `condition_expression_ids`; EVT/STATE/ENTITY "not built (blocked future step)" (`max_plan_consensus.md` row 24) | MISSING (Phase D) |
| motif tables | none in repo; registry note "classical A2 frequent itemsets outside repo" (`registry/ssot15_state_experiment_map.csv` SX-14-01) | MISSING |
| z_R / z_C representation registries | none | MISSING (nothing to register yet) |
| missingness flags | recipe_base `has_ingredients/has_quantities/has_instructions/has_conditions` booleans; identity features use `*_missing` flags, "never 0" (`preregistration_v1.md` §3) | PARTIAL (no role/state/cuisine-uncertain flags) |
| similarity registry | `registry/ssot15_similarity_registry.csv` SIM-20 (recipe) and SIM-21 (cuisine) rows `FROZEN` as definitions, `CURRENT_STATUS = MISSING` | DEFINED, NOT IMPLEMENTED |

---

## 2. Models and baseline ladders (simple → strong → advanced)

### 2.1 Recipe ladder R0–R9 (§187.11, L13779–13789) — quoted
```
R0 binary ingredient incidence
R1 mean pooled ingredient embeddings
R2 frequency/IDF-weighted pooling
R3 quantity/role-aware pooling
R4 Deep Sets
R5 attention pooling
R6 Set Transformer
R7 pair/higher-order interaction model
R8 process/sequence/heterogeneous-graph recipe model
R9 task-conditioned multi-view recipe encoder
```
Rule L13791: **"R0–R3 are mandatory before claims about R4–R9."**

Model bodies:
- Generic aggregation z_R = A({z_i}) — "an experimental component, not a hidden implementation detail" (L13799–13807).
- Weighted pooling family (L13813–13820) with three semantically distinct weights: quantity w = q (L13827–13829); IDF_i = log(N/(f_i+ε)) (L13834–13839), z_R^idf (L13842–13850), warning **rare ≠ important** (L13857–13862); cuisine-specific weight A_i^c (L13870–13874) is descriptive only — using it to predict the same cuisine "creates leakage/circularity" (L13877).
- Deep Sets ρ(Σ φ(z_i)) — "canonical learned permutation-invariant set baseline" (L13881–13891), research question L13895.
- Attention pooling α_i = softmax(g(z_i)) (L13899–13911); task-conditioned α_i = softmax(g(z_i, z_q)) (L13919–13921); "not causal explanations" (L13914).
- Set Transformer Z' = SelfAttention(...), z_R = Pool(Z') (L13928–13935); warning learned interaction ≠ mechanism (L13942–13950).
- Pair/higher-order: p_ij = ψ(z_i, z_j), z_R = ρ(Σφ + Σ_{i<j} p_ij) (L13956–13970); triplets (L13975–13976); link to itemset mining/pair prevalence/flavor-overlap baselines (L13979–13984); **"Higher-order terms are introduced only if pairwise models leave measurable residual value."** (L13986).

### 2.2 Cuisine ladder C0–C8 (§189.13, L14337–14345) — quoted
```
C0 ingredient prevalence vector
C1 specificity / TF-IDF / authenticity-style explicit fingerprint
C2 pair/triplet motif representation
C3 mean recipe embedding
C4 weighted recipe aggregation
C5 Deep Sets over recipes
C6 attention / Set Transformer over recipes
C7 distributional / multi-cluster cuisine representation
C8 task-conditioned multi-view cuisine representation
```
C0–C2 must exist before learned claims (completion gate L15267; Phase 0 L15115).

### 2.3 Objective ladder O0–O7 (§190.17, L14714–14721) — quoted
```
O0 no-learning explicit recipe/cuisine vectors
O1 cuisine-classification supervision
O2 masked ingredient prediction
O3 recipe reconstruction
O4 same-recipe multi-view contrastive learning
O5 hard-negative contrastive learning
O6 multi-task recipe learning
O7 hierarchical recipe/cuisine learning
```
"The preferred objective is decided empirically." (L14724).

Objective bodies:
- §190.1 principle z_R = E_R(R; 𝓛) — similarity "must always be qualified by the signal used to train it" (L14365–14368).
- O1 cross-entropy (L14379–14381); shortcut risk (signature ingredients, source, length, formatting) (L14386); boxed accuracy ≠ representation quality (L14391–14395).
- O2 masked ingredient 𝓛 = −log P(i_k|R^{−k}) (L14403–14417); extensions single/multiple mask, rank vs sampled negatives, mask by role/frequency/category strata (L14424–14427).
- O3 BCE reconstruction (L14446–14453); "information-retention objective, not … sole evidence of useful transfer: an autoencoder can memorize identity" (L14456).
- O4 InfoNCE over views of the same canonical recipe: ingredients↔instructions, ingredients↔G_R, text↔structured (L14462–14492); preferred over same-cuisine positives (L14495).
- §190.6 safe augmentations (reorder ingredient list; normalize aliases; remove formatting; drop optional low-info fields; small quantity perturbation where units permit, L14501–14505) vs **forbidden invariances** (delete core protein/base; delete key spice/aromatic; change major process; reorder meaningful process events; remove fermentation/defining transformations, L14509–14513).
- §190.7 same-cuisine positives only for cuisine-discriminative spaces (L14518–14523).
- §190.8 process positives P(R_a)≈P(R_b) → z_R^process; sensory S(R_a)≈S(R_b) → z_R^sensory; "task-specific spaces … remain labeled as such" (L14530–14541).
- §190.9 hard negatives: same cuisine/different dish type; same category/different structure; similar ingredients/different process; similar process/different composition; size-matched; frequency-matched (L14547–14554); "mined without leaking the evaluation label" (L14556).
- §190.10 frequency-aware weights w_i = log(N/f_i) or 1/f_i^α (L14565–14571); weighted mask loss (L14577–14579); "α is a hyperparameter to validate, not a law" (L14582).
- §190.11 negative samplers uniform 1/M, ∝ f_i, ∝ f_i^β (0<β<1) (L14588–14604); "must be recorded" (L14606).
- §190.12 multi-task heads cuisine/missing/process/category with λ weights (L14612–14640); "Measure negative transfer" (L14642).
- §190.13 hierarchical L = L_ingredient + L_recipe + L_cuisine; "Each level must have a distinct target and ablation" (L14649–14664).
- §190.14 cross-source / cross-language positives "If duplicate/parallel recipes are reliably identified" (L14670–14684).
- §190.15 cuisine objectives: held-out prevalence, held-out motif, recipe retrieval from z_C, cross-source matching, hierarchical prediction; same-label prediction insufficient alone (L14690–14696).

### 2.4 Non-circular objective matrix (§190.16, L14700–14709) — quoted
| Training signal | Headline evaluation | Status |
|---|---|---|
| ingredient overlap | ingredient-overlap retrieval | circular/weak |
| cuisine label | same cuisine classification only | weak as sole evidence |
| masked ingredient | held-out ingredient prediction + cross-source transfer | valid |
| recipe text ↔ ingredient view | cross-view retrieval | valid |
| recipe co-occurrence/context | held-out ingredient completion | valid |
| process supervision | process-sensitive retrieval/classification | valid |
| multi-view recipe | cross-source retrieval | strong |
| recipe/cuisine representation | held-out motif/reconstruction/transfer | strong |

### 2.5 Required explicit baseline families (§191.1, L14734–14751)
Recipe: incidence; Jaccard/cosine; IDF-weighted vector; mean z_i; quantity/role weighted pooling where data exist; **frequency-only shortcut baseline** (L14736–14741).
Cuisine: prevalence vector; specificity/authenticity/TF-IDF fingerprint; pair/triplet motif vector; classical §85 fingerprint; mean recipe embedding (L14745–14749).
"A neural result without the relevant explicit baseline is incomplete." (L14751).
Tier-0 classical learners named: "LightGBM/logistic/classical baselines" (L15206).

### 2.6 Current strongest candidate (not frozen) — §196.3 L15462–15503
Factorized task-conditioned Z_R = {ingredients, role, state, process, text, graph} and Z_C = {ingredient, pairing, recipe, process, context}; likely training family "masked ingredient prediction + same-recipe multi-view contrastive learning + carefully mined hard negatives + multi-task/hierarchical supervision where justified" (L15496–15500), "remains a hypothesis until compared against explicit incidence/frequency/IDF/mean-pooling baselines under source/size/frequency controls" (L15503). (Note §196.3 drops z_R^quantity and z_R^sensory from the §187.9 list — see §9.)

### 2.7 Master Plan v4.0 framing (for comparison, not SSOT)
Part L L719: "Recipe z_R, cuisine z_C | bag-of-ingredients TF-IDF; mean z_i | set/graph/text encoders; frequency-debiased objectives | §191 leakage-controlled evaluation". Track C L4635–4660 repeats the R-ladder and confound list (recipe size, ingredient frequency, cuisine size, source, duplicates, language). B14 L485–495 adds typed similarity separation and **fitness** (F_{i|c,t}, η, §265) which are NOT in §§186–194 (they come from §160/§264–265).

---

## 3. Experiments / hypotheses / RQs

### 3.1 Canonical experimental program (§193)
- **Phase 0 (L15104–15118)** — prerequisite "required Level-12 ingredient representations and canonical identity tables are available" (L15106). Build/freeze: recipe master/edge tables; duplicate groups; source/cuisine ontology; split manifests; R0/R1/R2; C0/C1/C2; frequency/size/source shortcut baselines (L15110–15116). Gate G13-0.
- **Phase 1 (L15120–15139)** — encoder bake-off R1, R2, R3, R4, R5, R6 "on identical inputs/splits" (L15122–15131). Questions: learned aggregation > mean/weighted? attention > parameter-matched non-attention? gains survive frequency/size/source controls? (L15135–15137). Gate G13-1.
- **Phase 2 (L15141–15157)** — objective bake-off O1–O7, "same architecture where possible to isolate the objective" (L15155). Gate G13-2.
- **Phase 3 (L15159–15171)** — "Only after recipe-set baselines are stable" (L15161): pair interaction; explicit role/state inputs; process-sequence encoder; heterogeneous graph; structured+text fusion (L15163–15167); "depends strongly on the semantic-parsing/state track" (L15169). Gate G13-3.
- **Phase 4 (L15173–15191)** — C0…C8 comparison (L15177–15187); "Always include recipe-count/size/source matched sensitivity" (L15189). Gate G13-4.

### 3.2 Recipe task families (minimum ≥2; §188.10 L14059–14066, §191.2 L14757–14763)
§188.10: cuisine classification; recipe retrieval; masked ingredient prediction; partial-recipe completion; substitution/recommendation **"where gold/evidence exists"**; cross-source retrieval/generalization. "A representation that wins only the task used to train it is not automatically a general recipe representation." (L14066).
§191.2 recipe-level: cuisine classification; recipe retrieval; masked ingredient recovery; partial-recipe completion; cross-view retrieval; **cross-source duplicate/identity retrieval**; process-sensitive retrieval when process labels exist.
§191.2 cuisine-level (L14767–14772): cuisine/subcuisine classification; cuisine→recipe retrieval; held-out prevalence reconstruction; held-out pair/triplet motif prediction; cross-source cuisine matching; similarity stability under matched resampling.

### 3.3 Research questions (verbatim ids)
- **RQ13-C1** learned cuisine representation adds value beyond explicit prevalence fingerprints? (L14350)
- **RQ13-C2** pair/triplet motifs add information beyond singles? (L14351)
- **RQ13-C3** recipe-level aggregation improves cuisine representation beyond direct ingredient statistics? (L14352)
- **RQ13-C4** distributional > centroid when internal diversity is large? (L14353)
- **RQ13-C5** how much apparent cross-cuisine similarity changes after recipe-count, recipe-size, source and annotation-coverage matching? (L14354)
- Implicit recipe-side RQs (not given ids in SSOT): Deep Sets vs fixed pooling (L13895); attention vs parameter-matched non-attention (L15136); higher-order residual value (L13986); procedure value beyond set/text (crosswalk L15293).
- Related cross-level RQs: **RQ16-23** "Does learned quantity representation add value to recipe embeddings beyond ingredient incidence and normalized grams alone?" data "Level-13 tasks with quantity-rich subset", baseline incidence; grams only (L27225–27232). **RQ16-13** duplicate leakage inflation vs group-safe splits, baseline random split, data "100k corpus duplicate groups" (L27025–27031). Master Plan SX-14-01…05 (B14 L490–494): encoder bake-off; similarity-type separation; identity/variant calibration (shared E13E-05); cuisine fingerprint robustness; substitution benchmark — all `CURRENT_STATUS=MISSING` with fields `NOT_SPECIFIED_IN_PLAN` in `registry/ssot15_state_experiment_map.csv`.

### 3.4 Mandatory diagnostics (each is an experiment arm)
- **Frequency leakage controls §188.7 (L13998–14024)**: frequency-only baseline (L14002–14004); random/shuffled consistent embeddings (L14006–14008); frequency-bin substitution i→j same bin (L14010–14018); leave-top-k-out with multiple k, "k is a sensitivity parameter, not a universal constant" (L14020–14024).
- **Recipe-size confound §188.8 (L14036–14042)**: report corr(‖z_R‖, n_R); sum vs mean normalization; size-matched subsets; size as covariate baseline; stratify by size bins.
- **Source leakage §188.9 (L14048–14053)**: group (near-)duplicates; split at source-entity level; source-disjoint eval; per-source metrics.
- **Corpus-size control §189.7 (L14244–14248)**: equal-recipe-count subsampling; bootstrap subsampling; stability vs N_C.
- **Recipe-size matching §189.8 (L14258–14264)**: matched subsampling; common-reference weighting; size-stratified; inherits §124.x.
- **Source/language §189.9 (L14271–14275)**: source-disjoint cuisine matching; per-source sensitivity; cross-language duplicates; canonicalized views separate from raw text.
- **Frequency-debiasing panel §191.7 (L14862–14872)**: (1) full model, (2) frequency-only, (3) random-embedding identity, (4) frequency-bin substitution, (5) top-k removal, (6) IDF/specificity weighting, (7) size-matched eval; "The purpose is not to remove frequency automatically; frequency is a real culinary signal." (L14872).
- **Source-leakage diagnostic §191.8 (L14876–14881)**: train A/B test C; remove source metadata; structured-only vs text-only vs fused; report whether cuisine performance collapses under source holdout.
- **Ablations §191.10 (L14896–14914)** and **required ablation matrix §193.7 (L15238–15260)**: recipe Full − {quantity, role, state, text, process, pairs, attention}; plus remove pretraining; replace learned z_i with classical explicit ingredient vectors (L14905–14906). Cuisine Full − {pair/triplet, recipe embedding, context, distributional component}; mean vs learned aggregation; size/source matched vs unmatched. Confound controls: matched recipe size; matched corpus size; source holdout; frequency-bin perturbation; top-k removal (L15256–15260).
- **Repeated runs §191.11 (L14918–14925)**: multiple seeds; CIs; paired bootstrap/permutation; seed variance; "A tiny mean gain smaller than seed/split variation does not justify added complexity." (L14925).
- **Compute tracking §191.12 (L14929–14938)**: params, train/inference time, VRAM/RAM, feature cost, artifact size.

---

## 4. Gates, promotion and stop rules (quoted exactly)

| Id | Exact text | Line |
|---|---|---|
| **G13-0** | "no learned Level-13 headline result until leakage audits and explicit baselines exist." | L15118 |
| **G13-1** | "promote a learned set aggregator only if gains exceed seed/split uncertainty on at least two task families." | L15139 |
| **G13-2** | "freeze no objective based solely on the task it directly optimizes; require transfer or non-circular secondary evaluation." | L15157 |
| **G13-3** | "procedural/graph complexity is promoted only if it improves process-sensitive or cross-source tasks beyond set/text baselines and survives extraction-error analysis." | L15171 |
| **G13-4** | "learned z_C must add value beyond explicit cuisine fingerprints on at least one non-circular held-out task and remain stable under matched resampling." | L15191 |

**Level-13 completion gate §193.8 (L15264–15277)** — "Level 13 becomes empirically frozen only when:" (12 boxes, all unchecked):
1. recipe/cuisine data contracts and duplicate/source registries are versioned (L15266);
2. R0–R3 and C0–C2 explicit baselines exist (L15267);
3. at least one leakage-safe recipe split family is frozen (L15268);
4. source leakage is quantified where source labels exist (L15269);
5. frequency-only and recipe-size shortcut baselines are reported (L15270);
6. recipe-set aggregation is selected empirically, not by preference (L15271);
7. objective choice is tested with non-circular transfer evaluation (L15272);
8. recipe and cuisine embedding gains survive required confound controls (L15273);
9. calibration/uncertainty reported where probabilistic outputs exist (L15274);
10. compute profiles and seed/split uncertainty recorded (L15275);
11. final decision record states what z_R and z_C mean, which tasks they support, and what they do **not** support (L15276);
12. procedural/process claims are deferred to L14/L15 unless supported by the structured/process evaluation (L15277).

**Permanent Level-13 promotion rule §194.3 (L15310–15329)**: boxed "added information > shortcut/confound explanation" under identical data/splits (L15312–15320); operational six: (1) beat the appropriate explicit baseline; (2) survive frequency/size/source controls; (3) demonstrate non-circular transfer/retrieval/reconstruction value; (4) remain stable across seeds/resamples; (5) justify its compute/complexity; (6) retain a clear statement of what the embedding geometry means (L15324–15329).

**Other binding rules acting as gates**
- R0–R3 mandatory before R4–R9 claims (L13791).
- Higher-order terms only if pairwise leaves measurable residual (L13986).
- Non-circular evaluation rule §191.9 (L14885–14892): "The headline evaluation target must not simply restate the training objective" with four examples (train masked → also cross-source retrieval; train cuisine classification → also retrieval/held-out motif; cross-view → cross-view + downstream; "train ingredient overlap distillation → do not headline ingredient-overlap retrieval").
- Cuisine/subcuisine holdout misuse prohibition (L14796): "do not use a cuisine-disjoint split for ordinary supervised cuisine classification and then claim impossible labels should be predicted."
- Compute escalation "conditional on a proven bottleneck and benchmark value" (L15230).
- §191.12 L14938: "A simpler explicit or Deep-Set model remains preferable if the complex model produces negligible practical gain."
- §192.5 L15030 "Split duplicate groups before model training."
- Calibration §191.5 (L14840–14845): ECE; Brier; reliability plots; selective risk/coverage if abstention implemented.

**What the gates do NOT specify (quantitatively)**: no numeric effect-size threshold, no number of seeds, no k/α/β grid, no minimum cuisine support (recipes per cuisine), no minimum number of sources for source holdout, no CI level, no definition of "stable under matched resampling" (e.g. neighbour-overlap ≥ x). See §9.

**Stop / fail paths implied (my reading, not SSOT text)**: if G13-0 cannot be met because cuisine labels/source registry are inadequate → only R-side, cuisine-free task families (masked ingredient, completion, cross-view, cross-source identity) are legal headlines; if G13-1 fails → keep R1/R2 (or Deep Sets per L14938); if G13-3 fails → procedural claims deferred to L14/L15 (L15277); if G13-4 fails → explicit C0–C2 fingerprints are the cuisine representation.

---

## 5. Data requirements and named sources (licence notes)

### 5.1 What §§186–194 actually require (no datasets are named in §§186–194)
§§186–194 name **no external dataset**; they require: canonical ingredient identity (L15106 "canonical identity tables"), Level-12 z_i (L15106), recipe master + edge tables (§192.1–192.2), cuisine labels with provenance and hierarchy (§192.1, §192.4), source + duplicate registry (§192.5), timestamps for temporal split "where timestamps permit" (L14792), process/state events for R8/R9 only (L15004), sensory supervision only for z_R^sensory (L14539) and substitution gold "where gold/evidence exists" (L14063).

### 5.2 Repo supply (verified)
- 612,782 raw recipes; 611,714 exact-dedup logical recipes; 1,039 exact groups / 2,107 records; 605,476 provisional families (598,689 singletons); 46,697 dish-family candidates (`final_recipe_database_statistics.md`).
- Source mix: FOODCOM 522,517 (85.27%); GUTENBERG_SEGMENT 73,955 (12.07%); A1_BBC_GOOD_FOOD 11,934 (1.95%); WIKIBOOKS 3,676; TASTESET 700 (ibid.).
- **Licence / model eligibility**: MODEL_ELIGIBLE (training_allowed=YES) = **73,778** — i.e. essentially Gutenberg only (PUBLIC_OPEN 73,955); training_allowed UNKNOWN 535,151 (Food.com + A1 + TASTESET), CONDITIONAL 3,676 (Wikibooks CC BY-SA). H2 items open: Food.com SRC registration + licence; TASTEset; A1/BBC training/redistribution; Wikibooks share-alike (ibid. LICENCE_USAGE). Food.com: "kaggle_declared_licence CC0-1.0 … uploader authority … NOT verified; keep DERIVED/analysis use" (`data/external/foodcom/PROVENANCE.json`). A1/BBC = LOCAL_RESEARCH_ONLY (RESTRICTED local-only per ctx).
  → **Consequence for L13**: a *learned* z_R trained on Food.com/A1 is currently not licence-cleared for training under the repo's own usage registry; explicit Tier-0 statistics (R0–R2, C0–C2) are analysis-level and lower-risk, but publication/release of derived embeddings still needs H2 decisions.
- **Cuisine supervision**: 9.81% explicit; by source A1 58.46%, Gutenberg 69.63%, Wikibooks 45.57%, Food.com 0.0%, TASTEset 0.0%. Top: American 35,516; English 7,640; British 3,411; French 3,382; Jewish 1,932; Italian 1,566; Creole 618; Indian 501; Roman 455; Mexican 422 (ibid.). My REC profile (107,760 REC rows; 73,186 with cuisine): 256 distinct label strings; 156 sources carry any cuisine label and **153 of them carry a single label**; "American" spans 111 sources; A1 (SRC-000002) is the one large multi-cuisine source (British 3,030; Italian 717; French 449; Indian 391; American 263; …). Interpretation: Gutenberg cuisine labels are book-level provenance labels, so cuisine is almost perfectly confounded with source/book/era there — exactly risk §194.2 #2 ("Website/source may be easier to learn than cuisine", L15298).
- **Language**: 100% "en" → §189.9 cross-language duplicates and §190.14 cross-language invariance are NOT testable on current data.
- **Temporal**: Food.com era from DatePublished (PUBLISHED_1999…2019; 2005–2010 dominant); Gutenberg era is AUTHOR_BORN_xxxxs (author birth decade, not recipe date); era_known 93.03% (ibid.). Temporal split §191.3 feasible within Food.com; Gutenberg dates are weak proxies (L13E §262.3 L43310 excludes undated recipes from date-sensitive claims).
- **Missingness** (ibid. MISSINGNESS; the key semantics "has_x" with values like Gutenberg has_quantities 0.9305 vs Food.com 0.0056 read as *missing fractions* — label ambiguous, UNVERIFIED which direction): quantity info is near-complete for Food.com/A1 and largely absent for Gutenberg — so R3 quantity-aware pooling is effectively a Food.com/A1 experiment, i.e. licence-UNKNOWN data.
- Gold: 40 GOLD_PENDING_INDEPENDENT_IAA (not independent), SILVER_AUTO 11,914 (A1 model/rule annotations, unverified); no role/state Gold → role view (R3 role, §187.4) has no supervision.
- Substitution: "ING_ALTERNATIVE_TO KGE (220 edges) are mined co-occurrence, not a substitution benchmark" (`registry/ssot15_state_experiment_map.csv` SX-14-05) — §188.10 task 5 has no gold.

### 5.3 External sources that could serve L13 (NOT verified in this run; for research agents)
Not named by §§186–194; listed only as research leads, all UNVERIFIED here: Recipe1M/Recipe1M+ (Marin et al.; cuisine-free, licence restricted to research), RecipeNLG (Bień et al. 2020; non-commercial), Yummly-28K / "What's Cooking" Kaggle (cuisine-labelled; licence unclear), CoSyLab RecipeDB (cuisine/region labels; D-015 permission ASSUMED/DERIVED_ONLY per ctx), Ahn et al. 2011 flavor network data (cuisine-level). Any of these would need an SRC row, licence class and duplicate-group integration *before* entering an L13 split. Do not acquire in this run.

---

## 6. Dependencies on other levels/steps

**Upstream (hard)**
- L12 ingredient representations z_i and canonical identity tables (L15106; L13413; §195.2 "Level 12 remains specification-complete but empirically open" L15385). Repo: `registry/ssot15_state_experiment_map.csv` G12-COMPLETE "0 of 12 items satisfied beyond MOL registry existing". → **R1–R7 depend on an L12 deliverable that does not exist.** R0/R2(explicit IDF vector) and C0–C2 do NOT need z_i and can run on canonical ingredient ids alone. (Note R2 in the ladder is "frequency/IDF-weighted *pooling*" of z_i, but §191.1 L14738 also lists an "IDF-weighted explicit vector" — the explicit version is z_i-free.)
- Canonical ingredient vocabulary/ALIAS (alias collisions audit L15089) — NER/linker frozen S128 (ctx); ING 5,387 rows.
- Recipe identity: duplicate groups, near-duplicate method, split manifests (§192.5; Phase 0 L15111–15113) → Step 07I outputs + a not-yet-done calibration.
- Semantic parsing / state reconstruction §§152–156 (L13712, L14985, L15169) for R8/R9, role/state views, process positives → Phase D (Steps 16–20).
- Cross-cuisine controls §124.x (L14264) and §85 fingerprint (L14748).

**Lateral / downstream**
- L14 (§194.4 L15333–15361): L13 represents composition/context/state annotations/observed procedure; L14 conditions on process; L15 predicts ΔS. L13 "does not itself prove process-conditioned dynamics" (L15354).
- L13E (§260.4 L42979; §262 L43284): may add temporal/cultural views to z_R/z_C "where task-justified", "not a mandatory view"; forbidden shortcut "calling same-cuisine pairs universally 'similar'". Shared experiment E13E-05 ↔ SX-14-03 identity/variant calibration (Master Plan L492).
- L16 / RAG: RQ16-13 duplicate leakage (L27025–27031) and RQ16-23 quantity encoder (L27225–27232) consume L13 tasks; §257G.9 split-integrity audit (L34854–34862).
- FlavorTwin: §260.4 L42982 cultural prior optional; z_R/z_C similarity must remain typed (brief §24; registry SIM-20/SIM-21).
- Master Plan DAG (L243): "B14 recipe/cuisine repr + similarity/fitness (L13) ← B04, B09, B11" (B04 = L12 molecules/ingredients; B09 vocab; B11 event/state graph). Note: B11 is only needed for R8/R9/G13-3; Phase 0–2 and Phase 4 need only B04 (and not even that for explicit baselines) + B09 + identity.

---

## 7. Risks / failure modes

SSOT list §194.2 (L15297–15306), verbatim headings:
1 "Cuisine labels are noisy and hierarchical." 2 "Website/source may be easier to learn than cuisine." 3 "Global frequency is a real signal and a confound simultaneously." 4 "Recipe quantity normalization is difficult across units/servings." 5 "Ingredient role labels may be sparse/inferred." 6 "Process/state extraction error can dominate graph/sequence models." 7 "Same-cuisine positive pairs may collapse heterogeneous dishes." 8 "Pair/triplet spaces can explode without support/sparsity control." 9 "A centroid cuisine embedding may hide legitimate internal modes." 10 "Learned z_R/z_C can appear strong while simply reproducing explicit prevalence statistics."

Repo-specific failure modes (my analysis, evidence cited):
- **R-A Cuisine ≡ source (risk 1+2 realised).** 153/156 labelled sources single-label; Food.com unlabelled. A source-disjoint cuisine classifier is nearly impossible to construct except within A1 (local-only) and Wikibooks; any "cuisine classification" headline on Gutenberg is a book classifier. §191.8 requires reporting "whether cuisine performance collapses under source holdout" (L14881) — expect collapse.
- **R-B Exact-only duplicate groups (risk to every L13 split).** `duplicate_group_id` is exact (1,039 groups); near-dup families are provisional and uncalibrated (400-pair packet unlabeled). §191.3 duplicate-group-disjoint (L14782–14785) explicitly includes near duplicates and cross-source copies. Food.com is notorious for re-posted recipes (UNVERIFIED magnitude here); RQ16-13 exists to measure inflation (L27025).
- **R-C Identity–representation circularity.** Provisional family edges require IDF-weighted ingredient-token Jaccard ≥ 0.80 and title Jaccard ≥ 0.50 and use explicit-cuisine *disagreement* as a veto (`preregistration_v1.md` §3 rule (2),(3),(5)). If L13 later (i) uses families as split groups and (ii) evaluates ingredient-overlap retrieval, it hits the §190.16 "ingredient overlap → ingredient-overlap retrieval: circular/weak" row; and cuisine-veto in the identity rule makes "cross-cuisine near-duplicates" structurally impossible to discover, biasing any cuisine-transfer evaluation. Must be recorded as a known dependency.
- **R-D Licence gate on learned models.** Only 73,778 training_allowed=YES (Gutenberg); a learned z_R on Food.com/A1 violates the repo's own usage registry until H2 resolved. Gutenberg alone is en-historic, 93% missing quantities (if the missingness reading is right), single-label-per-book → poor training substrate for R3/R4–R6.
- **R-E L12 absence.** R1–R7 require z_i; L12 empirically 0/12. Running R4–R6 over ad-hoc z_i (e.g. BGE text embeddings of ingredient names from the frozen linker) would make L13 inherit an unvalidated L12 — violates L13413 spirit; must be declared as "text-embedding z_i" variant, with "replace learned z_i with classical explicit ingredient vectors" ablation (L14906).
- **R-F Role/state not extracted.** No role column; `form_state_modifiers` string only; Gold has no role/state. R3-role and state views are blocked until Phase D; hallucinating roles from identity is forbidden (L13615).
- **R-G Frequency-bin substitution / top-k removal parameter shopping.** k, α, β are "sensitivity parameters" (L14024, L14582, L14603) with no pre-registered grid → post-hoc gate-weakening risk (brief §3 "no post-hoc gate weakening"). Needs pre-registration like 07I did.
- **R-H Seed/split variance gate with tiny cuisine classes.** G13-1 "gains exceed seed/split uncertainty" with classes like Indian 501, Mexican 422 → high variance; macro-F1 unstable; need minimum-support rule.
- **R-I Scale vs compute.** 611k recipes × M ingredients for incidence/pairs is Tier-0 feasible (sparse); triplets need support thresholds (L14205; risk 8). Learned R4–R6 Tier-1 GPU; this server's GPUs are off-limits (ctx), VPN to A100 impractical → Tier-1 means the local RTX machine.
- **R-J Text view leakage.** Food.com instructions contain author voice; no AuthorId captured → cannot do author-disjoint split inside Food.com, the only within-source analogue of "source-entity" (L14050).

---

## 8. MAPPING TO THE 36-STEP SPINE (reconstruction; the 36-step plan is missing)

Legend: REQ = what L13 material requires from that step. Nothing here is quoted from step cards.

**Step 01 Freeze project authority** — REQ: record that §§186–194 are canonical L13 (§195.1 L15370–15371) and that §196.3 "strongest candidate" is a hypothesis, not a decision (L15462). Record that L13E is a *parallel* extension, not a gate on L13 (L42927).

**Step 02 Audit implementation state** — REQ: state that L13 is NOT STARTED empirically; G13-0…4 all MISSING (`registry/ssot15_state_experiment_map.csv`); SIM-20/SIM-21 defined/MISSING (`registry/ssot15_similarity_registry.csv`); record the cuisine-coverage and licence facts in §5.2 above.

**Step 03 Freeze state semantics** — REQ: freeze the distinction ingredient identity vs ingredient state (i,s) (L13622–13642) and composition vs procedure (L13400); typed `state` field separate from `preparation/form` in the edge table (§192.2 L14974–14975 lists both). Missingness codes per §192.9 (L15073–15082), distinct from zero.

**Step 04 Freeze evidence / provenance / similarity contracts** — REQ (most direct pre-35 owner):
- Typed similarity registry entries SIM-20 (recipe) and SIM-21 (cuisine) must carry: training objective (L14365–14368, rule 11 L13410), task, baseline, confounds (size, source, era, frequency), non-circular evaluation pairing (§190.16 table).
- Freeze the semantics of `duplicate_group_id` (exact) AND add a distinct split-group concept (see §9 #1) — §257C Recipe.20 forbids silently reinterpreting it (L29538).
- Cuisine-label provenance class (explicit-in-recipe / book-level / inferred / tag) required by L15017.
- Representation registry schemas §192.7/§192.8 (fields listed in §1.7).
Gate contribution: contracts versioned = completion box 1 (L15266).

**Step 05 Normalize EVD** — no direct L13 requirement (L13 consumes recipe planes, not EVD). Only link: sensory supervision for z_R^sensory (L14539) would come from evidence planes later; keep separate.

**Step 06 Freeze source acquisition manifest** — REQ: every recipe source used by L13 needs SRC registration + licence class + training_allowed; currently Food.com and TASTEset are "UNREGISTERED:" (`corpus.py` source_id) and are H2 items. If external cuisine-labelled corpora (§5.3) are wanted, they must enter the manifest here, not ad hoc.

**Step 07 Condition & measurement normalization (incl. 07H-R, 07I-R)** — REQ:
- 07H-R recipe_base: add/capture (in a new derived column/table, not by rewriting frozen artifacts) servings_raw/normalized, AuthorId, DatePublished, Keywords, RecipeYield for Food.com (all present in the raw parquet, not read by `iter_foodcom`) — §192.1 servings and time; §191.3 temporal split; §188.9 source-entity split.
- 07I-R identity: duplicate groups exist (exact); near-dup calibration (400-pair packet) is the prerequisite for a §191.3-compliant split group; provisional families must not be treated as calibrated.
- Quantity normalization (QTY_SCHEMA mass/volume/count + intervals) feeds R3 (L13564 "requires explicit unit conversion and serving/batch context").
- §192.10 data-quality audits (duplicates, alias collisions, cuisine-label inconsistency, source imbalance, size distribution, missingness by source/cuisine) are mostly computable from 07H-R/07I-R outputs at Tier 0.

**Step 08 Scientific source lineage** — no L13 dependency (scientific evidence plane). L13 does not argue for or against Step 08 being next. (Analogy only: L13 split groups for recipes play the role that study lineage plays for EVD.)

**Step 09 Evidence extraction & verification machinery** — none direct.

**Steps 10–15 Evidence acquisition / DATA-EVIDENCE v1** — none direct. Indirect: sensory/process supervision for §190.8 task-specific spaces would only become available via evidence acquisition; L13 must not wait on it (sensory view is optional).

**Step 16 Instruction semantic schema** — REQ: event/state table fields of §192.3 (action, input entity/state, tool, medium, temperature, time, output entity/state, event order, explicit vs inferred, confidence, L14993–15002); graph node/edge types of §187.7 (L13697–13710); role variable r_{i,R} with provenance class {annotated, extracted, weakly inferred, unknown} (L13610–13613).

**Step 17 Instruction-level extraction** — REQ: produce role/state/event outputs with per-field confidence and extraction-error estimates, because G13-3 requires models to "survive extraction-error analysis" (L15171) and risk 6 (L15302).

**Step 18 Event-sourcing engine** — REQ: S_0 → a_1 → … S_T reconstruction (L14988) and intermediate-product nodes (L13702) for R8 graph view.

**Step 19 Gold state-trajectory pilot** — REQ: a held-out, duplicate-group-disjoint Gold subset usable for process-sensitive retrieval (§191.2 #7) and extraction-error analysis; role/state gold (none exists).

**Step 20 Scale procedural semantic corpus** — REQ: coverage statistics by source/cuisine (§192.10 "procedure extraction coverage", "role/state coverage", L15095–15096); without them G13-3 cannot be evaluated.

**Steps 21–34 (mechanism, simulation, transition)** — L13 has no hard dependency on them; §194.4 places process-conditioned dynamics in L14/L15 (L15359–15361). Step 29–30 tabular baselines (LightGBM etc.) share the "simple model wins" principle (L14938).

**Step 35 Molecule → ingredient → recipe / cuisine representation ladder** — PRIMARY OWNER of §§186–194. REQ:
- Inputs: canonical ingredient ids; L12 z_i (for R1, R2-pooling, R3–R7); recipe master + edge tables; split manifest with split groups; source registry; cuisine ontology with provenance; motif tables; (for R8/R9) event/state graph from Phase D.
- Sub-phases = §193 Phases 0–4 with gates G13-0…G13-4 and completion gate §193.8.
- Baselines: R0, Jaccard/cosine, IDF-explicit vector, R1 mean z_i, R3 where data exist, frequency-only; C0, C1, C2, §85 fingerprint, C3 mean (L14736–14749); classical learners "LightGBM/logistic" (L15206).
- Strong: R4 Deep Sets (and per L14938 the default winner if complex models gain negligibly); O2 masked ingredient + O4 cross-view contrastive.
- Advanced: R5/R6 attention/Set Transformer; R7 pairs; R8/R9 graph/multi-view (only after G13-1/G13-3); C5–C8.
- Metrics: macro/micro-F1, AUROC/AUPRC, balanced accuracy; Recall@K, Precision@K, MRR, MAP, NDCG; Hit@K, mean rank, frequency-stratified macro; reconstruction micro/macro F1, AUPRC, BCE; stability by bootstrap CIs, CKA/Procrustes, neighbour-overlap (L14804–14836); calibration ECE, Brier, reliability, selective risk/coverage (L14840–14845).
- Splits: recipe-disjoint; duplicate-group-disjoint; source-disjoint; temporal (Food.com DatePublished); cuisine holdout only for transfer tasks; ingredient cold-start (L14778–14801).
- Outputs: §192.7/§192.8 registry rows; final decision record (L15276).
- Ordering inside Step 35: z_m/z_i (L12) must precede learned z_R; but **explicit R0/R2-explicit/C0–C2 + all confound audits can run earlier and in parallel** (CPU, Tier 0) — they need only 07H-R/07I-R outputs.

**Step 36 Evidence compiler → CulinaryState-RAG → FlavorTwin** — REQ: z_R/z_C used only for the tasks the decision record says they support (L15276); RAG recipe retrieval must use group-safe evaluation (RQ16-13); FlavorTwin may consume a cultural prior but "final similarity stays multi-view and evidence-aware" (L42982); never treat z_R similarity as sensory/chemical similarity (rule 8, L13407; brief §24).

---

## 9. Contradictions, stale items, underspecified parts, open questions

1. **`duplicate_group_id` semantics conflict (material).** §192.5 (L15021–15030) lists `duplicate_group_id` *and* separately "near-duplicate score/method", and §191.3 (L14782–14785) defines the split unit as "Near duplicates / mirrored recipes / cross-source copies stay in one split group". The repo implements `duplicate_group_id` = exact/normalized/mirrored copies only (`preregistration_v1.md` §1 Level A), and HIGH_CONFIDENCE_NEAR_DUPLICATE_GROUPS = 0. SSOT §257C Recipe.20 (L29533–29538) requires one stable meaning per schema version. → Proposed resolution (PROPOSED_ONLY): keep `duplicate_group_id` = exact; add a separately versioned **`split_group_id`** (connected components over duplicate groups ∪ calibrated near-dup edges ∪ cross-source copies, and conservatively ∪ provisional family edges until calibration) with `split_group_method` and `calibrated` flags. Needs human calibration of the 400-pair packet; also a sensitivity analysis split-by-exact vs split-by-family (RQ16-13 design).
2. **Cuisine supervision essentially absent for the bulk corpus.** §§188.10/191.2 put cuisine classification first in both task lists, and G13-4 needs cuisine fingerprints, but Food.com (85% of recipes) has 0% explicit cuisine and Gutenberg labels are source-level. Open question (needs inspection, not done): does Food.com `Keywords` contain cuisine tags of usable quality (UNVERIFIED)? If used, they must be marked "tag-derived, uploader-assigned" provenance (L15017) and audited for inconsistency (L15090).
3. **Notation inconsistency**: relative prevalence uses (C−1) in §188.2 (L13874) but (K−1) in §189.3 (L14129); §188.2 uses lower-case c and C for count simultaneously. Cosmetic, but a code reference implementation must fix one definition. Also IDF in §188.2 is recipe-level (N recipes, f_i recipe frequency, L13836–13838) whereas §189.4 IDF is cuisine-level (K cuisines, L14161–14163) — same symbol IDF_i, different quantity; must be two named features.
4. **§196.3 vs §187.9 view lists**: §196.3 Z_R omits quantity and sensory views (L15467–15477) and Z_C omits sensory (L15481–15488) relative to §187.9 (L13737–13747) and §189.12 (L14321–14329). §196 is a "historical return point … retained for provenance only" (L15507), so §187.9/§189.12 govern; flag as stale.
5. **"R2" ambiguity**: ladder R2 is "frequency/IDF-weighted pooling" (of z_i, L13782) while Phase 0 lists "R0/R1/R2 baselines" to build *before* any learned work (L15114) and §191.1 lists an "IDF-weighted explicit vector" (L14738). Phase 0 therefore needs either an explicit (z_i-free) R2 or L12 z_i first. Recommend splitting into R2-explicit (TF-IDF incidence) and R2-pooled.
6. **Phase-0 prerequisite too strong for explicit work**: L15106 makes L12 z_i a prerequisite for Phase 0, but C0–C2, R0, explicit IDF, motifs, splits and confound audits do not need z_i. Plan should let explicit L13 baselines run in parallel with L12 (Master Plan DAG L243 `B14 ← B04` is likewise over-constrained for explicit baselines).
7. **Gates lack numeric operationalisation**: no seed count, CI level, test, minimum class support, "two task families" eligible list, definition of "stable under matched resampling", k/α/β grids, minimum number of sources for source-disjoint. These must be pre-registered at Step 35 start to avoid post-hoc weakening (brief §3). Research leads: Bouthillier et al. 2021 "Accounting for variance in ML benchmarks" (MLSys) and Dror et al. 2018/2019 on significance testing in NLP — UNVERIFIED citations here, for the research agent.
8. **Cross-language invariance (§190.14, §189.9) is untestable** on an all-English corpus; should be marked NOT_APPLICABLE_CURRENT_DATA rather than silently skipped.
9. **Source-disjoint within Food.com**: "split at source-entity level" (L14050) is undefined when one website contributes 85%; author (AuthorId) is the natural entity but is not captured. Open question: is author-disjoint a valid proxy for source-disjoint for the text view? (literature research needed on author-leakage in recipe corpora — UNVERIFIED).
10. **Cuisine ontology unspecified**: §192.4 requires hierarchy cuisine/subcuisine/region/country but names no ontology; 256 raw label strings incl. artifacts ("New", "American|French", "Roman", "Jewish" = religious/cultural not geographic). Needs a small controlled vocabulary + mapping with provenance; candidate external references (Wikidata cuisine items, FoodOn has no cuisine hierarchy to my knowledge — UNVERIFIED) are research items.
11. **Substitution task has no gold** (§188.10 #5 "where gold/evidence exists"): ING_ALTERNATIVE_TO is mined co-occurrence (SX-14-05 note) — using it as a benchmark would be circular with co-occurrence training (§190.16 row 5). Keep task deferred until a gold exists.
12. **Fitness is in the Master Plan B14 but not in §§186–194.** Fitness (F_{i|c,t}, η, §160.x/§265) belongs to L13E/§160; Step 35 card should cite §265 explicitly if it keeps fitness, or move it to the L13E lane.
13. **Licence × learning**: SSOT L13 is silent on licence; repo registry says training_allowed UNKNOWN for 535,151 recipes. Open governance question: is "derived-only analysis use" (Food.com PROVENANCE note) sufficient to train an embedding model whose weights are not released? Needs human (H2) decision, not research.
14. **Master Plan SX id collision**: SX-14-01…05 are L13 experiments (block B14) but read like Level-14 ids; risk of confusion with G14-*. Recommend renaming in the plan to SX-B14-* or SX-L13-*.
15. **Missingness-key direction**: `final_recipe_database_statistics.md` MISSINGNESS block labels values `has_quantities` etc. but numbers look like missing fractions (e.g. TASTESET has_instructions 1.0 while TASTEset has no steps; Gutenberg has_quantities 0.9305). UNVERIFIED; should be checked by whoever writes the Step 35/07 data card.

---

## 10. LOOK-AHEAD: fields earlier steps must capture so L13 is usable later

Priority A = blocks a §193.8 completion box; B = blocks a specific task/ablation; C = nice to have.

| # | Field / artifact | Needed by (SSOT) | Earliest owning step | Current state | Pri |
|---|---|---|---|---|---|
| 1 | `split_group_id` (+ `split_group_method`, `calibrated`, version) distinct from exact `duplicate_group_id` | §191.3 L14782–14785; §192.5 L15030; §257G.9 L34857; box L15268 | 04 (contract) → 07I-R (compute) | MISSING; exact groups only | A |
| 2 | Near-duplicate calibration labels (400-pair packet) | §192.5 "near-duplicate score/method" L15027 | 07I-R (human) | UNLABELED | A |
| 3 | `cuisine_label`, `cuisine_label_provenance_class` {explicit_in_recipe, book_level, site_tag, inferred}, `cuisine_label_source_span`, multi-label as list not "a\|b" | §192.1 L14953; §192.4 L15017; §192.10 L15090 | 04 (contract) + 07H-R derived table | single string, no provenance | A |
| 4 | Cuisine ontology table (cuisine/subcuisine/region/country, geography kept separate) | §192.4 L15008–15015; §189.10 | 04 | MISSING | A (for G13-4) |
| 5 | Per-recipe `source_entity_id` (site/book; for Food.com `AuthorId`) | §188.9 L14050; §191.8 L14878 | 06/07H-R | AuthorId not read | A (for source-leakage box L15269) |
| 6 | `date_published` (typed date) and `date_kind` {published, author_birth_proxy, unknown} | §191.3 temporal L14790–14793; L13E §262.3 L43310 | 07H-R derived | era string computed ad hoc | B |
| 7 | `servings_raw`, `servings_normalized`, `yield_raw` | §192.1 L14956; §187.3 L13564; §238.15 L25764–25765 | 07H-R / CQPO | not captured for Food.com | B (R3) |
| 8 | `acquisition_date` per source (and per record where scraped) | §192.5 L15025 | 06 | source-level only | C |
| 9 | `canonical_url` normalised for web sources | §192.5 L15024 | 06/07I | A1 only; MIRRORED_COPY groups 0 | C |
| 10 | Edge-table typed `state` separate from `preparation/form`; `role` + `role_provenance` {annotated, extracted, weakly_inferred, unknown} | §192.2 L14974–14976; §187.4 L13610–13615; §187.5 | 03 (semantics) → 16/17 | form_state string; no role | B (R3-role, state ablation) |
| 11 | Per-field missingness flags: quantity, role, state, process conditions, cuisine-uncertain, text-missing | §192.9 L15073–15082 | 03/04 contract; 07H-R | partial booleans | A (confound audit L14857) |
| 12 | Normalized quantity with basis (mass/volume/count) + interval + conversion status | §192.2 L14971–14973; §187.3 | 07 (CQPO) | QTY_SCHEMA present | B |
| 13 | Event/state table fields (action, input/output entity-state, tool, medium, temperature, time, order, explicit_vs_inferred, confidence) | §192.3 L14993–15002 | 16–18 | not built | B (R8/R9, G13-3) |
| 14 | Extraction-error estimates per field on held-out Gold | G13-3 L15171 | 17/19 | none | B |
| 15 | Food.com `Keywords` and `RecipeCategory` as raw tag lists (dish type for hard negatives §190.9 "same cuisine, different dish type") | §190.9 L14547–14554; §192.6 category motifs | 07H-R derived | category only, Keywords not read | B |
| 16 | Licence/usage class + `training_allowed` per recipe joined to every split manifest | (repo usage registry; not in §§186–194) | 06 | present; H2 open | A (governance) |
| 17 | Ingredient global frequency table f_i (recipe-level, over dedup view) and frequency bins | §188.7 L13993–14024 | 07H-R (`vocab_corpus_frequency_v1.parquet` exists — content not verified here) | likely present | A |
| 18 | Sparse motif tables (pair/triplet support, PMI/lift) with support thresholds | §192.6; §189.5 L14205 | Step 35 Phase 0 (Tier 0) | MISSING | A (C2) |
| 19 | Representation registries §192.7/§192.8 schemas | L15046–15069 | 04 (schema) | MISSING | A (box L15266) |
| 20 | Gold-firewall membership joined to split groups | §191.3; repo gold_firewall_v1 (2 Gold with family relatives) | 07I/19 | present (exact) | A |

**Key look-ahead message for Steps 03/04/07**: none of rows 1–11 require new acquisition; all are derivable from data already on disk (Food.com raw parquet columns AuthorId, DatePublished, Keywords, RecipeServings, RecipeYield; 07I candidate pairs; REC cuisine + SRC registry). They should be added as *new derived, versioned tables* (frozen 07H-R/07I-R artifacts must not be edited). The human-time item is the 400-pair near-duplicate calibration (row 2), which simultaneously serves L13 split groups, RQ16-13, SX-14-03/E13E-05 and Gold leakage control.
