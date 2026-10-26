> **STATUS (2026-10-26): ADVISORY ONLY.** Built on SSOT v14. The working plan is `CulinaryState_36_Step_Execution_Plan_v2.md` (D-027). Hierarchy: `docs/plan/CONSOLIDATED_VERDICT_2026-10-26.md` section 3.

# CulinaryState Recipe Semantic Compiler — Detailed R&D and Execution Plan

**Research consensus · Execution plan · Experiments and sub-experiments · Affected deliverable plan · JEPA scope**

| Field | Value |
|---|---|
| Version | **2.0 — 3 October 2026.** Research review conducted 2–3 October. Expands MERGED-1.2 with reviewed claims, implementation contracts, annotation decisions, replay semantics, controlled experiments, capacity estimates, release gates, and the requested RAG/Google model extension. Repository audit measurements remain provisional. |
| Merges | **Report A:** "CulinaryState recipe semantics: research consensus and execution proposal" (companion report, 2 Oct 2026). **Report B:** "CulinaryState-RAG: A Layered Recipe Semantic-Parsing and Canonicalisation Pipeline" (Claude research report). **New verification pass:** ReciFine, knowledge-augmented recipe NER, GLiNER2.5, JFC-Recipe, JEPA family, and **TypeSafe Jev** (official docs: pricing, limits, language support). |
| Project baseline | `computational_gastronomy_master_ssot_v14_0` — esp. §§230–242, 245, 249, 252, 257A, 259 (numbering identical in the CLEAN edition) |
| Team | Group 17 (MDMA): Kush Tokas (2023296), Parv Goyal (2023374). This plan is deliberately **owner-agnostic** (Track A / Track B). |
| Status | Plan only. **No model result, agreement score, cost measurement or superiority claim has been produced yet.** |

---


## Review note — authority, corrections, and execution scope

This version expands the supplied MERGED-1.2 plan into a buildable R&D program. The conceptual core and the E0–E14 / J1–J5 experiment identifiers are retained. The appendices are part of the plan, not optional commentary: they define record contracts, annotation decisions, replay semantics, statistical protocols, work budgets, and release gates.

**Authority order:** immutable source and measured evidence → adjudicated annotation contract → versioned compiler contracts → experiment results. A confident model prediction never moves itself up that chain. This document proposes changes to v14; it does not silently edit its D0–D11 transition ladder or declare its execution gates passed.

**Research status:** current primary documentation was checked for Jev and GLiNER2.5; official 2026 recipe-paper records were checked for knowledge-augmented token classification, ReciFine, and JFC-Recipe. Relevant earlier work and the existing research report are carried forward with their access limits. No new recipe corpus was downloaded, no model was trained, and the RecipeDB3 notebooks were not independently executed. Direct retrieval of the cited RecipeDB3 GitHub page failed during this review. Repository-specific scores, code findings, and overlap percentages remain attachment-reported audit leads until an artifact-backed rerun.

| Correction | Revised operational decision | Where implemented |
|---|---|---|
| Reported code audit presented as our completed work | Preserve the reported values, label them attachment-reported, and require commit/data/split/scorer artifacts | §1.2; Appendix F |
| One universal sample-size formula for F1 | Use task-specific, recipe-clustered intervals and pilot-based power simulations | §7.4; Appendix F |
| RecipeDB2 coverage compared with a different pool | Match pair definitions, eligibility, weighting, and accepted-risk denominator before comparing percentages | E6.7; Appendix F |
| Fixed score bands interpreted as safety guarantees | Thresholds are fitted policies, evaluated with uncertainty; risk budgets remain targets until supported | §14; Appendix F |
| A reserved lot requires an explicit retrieve sentence | A supported later reference can consume its compatible portion; record state access without inventing source text | §11.2; Appendix D |
| Ingredient mentioned means ingredient consumed | Account for each lot and branch; garnish, alternative, optional, and unresolved uses have distinct dispositions | §8; Appendix D |
| Choice confidence formula applied to all Jev primitives | Choice, Score, and Noul have different response semantics; calibrate each decision family | §17; Appendix E |
| Fan-out decisions assumed mutually dependent | Questions in one call are independent; dependent choices require code-mediated staging and joint consistency checks | Appendix E |
| Source value lists treated as character-span Gold | Re-annotate raw spans independently; keep projected labels as a distinct weak-label view | Appendix C; E1.10 |
| Two annotators can do every experiment in 12 weeks | Measure throughput, publish a capacity budget, and preserve a smaller credible core if necessary | Appendix H |
| Scientific completion implicitly fixes measurement sparsity | Study-disjoint evaluation and explicit missingness assumptions; imputation is never observed chemistry | Appendix G |

**Recommended core contribution:** evidence-preserving food/product normalization plus a symbolic quantity-and-entity lineage compiler, evaluated under sparse annotations and selective routing. Ingredient NER is a necessary baseline. Jev is an optional selector behind a provider-neutral interface. JEPA is a bounded research branch after the core works.

**Reading route:** use §§1–15 for semantics, §17 for Jev, §18 for the research matrix, §§19–22 for alignment with the original proposal, and Appendices B–K for the detailed execution contract. All numeric targets are proposed unless explicitly marked as published-source results or measured locally.

| Need | Detailed section |
|---|---|
| Record schemas, modules, and bounded compile loop | [Appendix B](#appendix-b-implementation-contract-records-services-and-replay) |
| Label manual, Gold chain, and picker decisions | [Appendix C](#appendix-c-annotation-manual-v1-decisions-the-label-picker-must-support) |
| Worked quantity/entity ledger cases | [Appendix D](#appendix-d-quantity-and-entity-lineage-worked-cases-and-transaction-semantics) |
| Jev and open selector interfaces | [Appendix E](#appendix-e-jev-and-open-selectors-precise-integration-and-adoption-protocol) |
| Splits, metrics, calibration, and fair SOTA claims | [Appendix F](#appendix-f-rigorous-evaluation-split-design-metrics-claims-and-comparison-artifacts) |
| Scientific evidence and sparsity boundaries | [Appendix G](#appendix-g-scientific-evidence-missingness-and-the-completion-boundary) |
| Capacity, first ten days, and weekly gates | [Appendix H](#appendix-h-capacity-aware-work-plan-and-synchronized-execution) |
| Fixtures and release/migration gates | [Appendix I](#appendix-i-acceptance-fixtures-release-gates-and-reviewable-outputs) |
| Current primary sources and pending audits | [Appendix J](#appendix-j-current-primary-source-review-and-audit-status) |
| **Jev versus JEPA; Google work; vectors/metadata; RAG/chunks/prompts** | [Appendix K](#appendix-k-retrieval-embeddings-chunking-prompts-and-learning-from-gaps) |

## 0. How to read this document

### 0.1 Naming conventions (fixes collisions between the two reports and v14)

| Prefix | Meaning | Note |
|---|---|---|
| **P0–P10** | Compiler stages | Report A's stages are canonical. Report B's L0–L6 map onto them (§4.2). |
| **A0–A5** | Annotation **depth** | Renamed from Report A's "D0–D5" to avoid clashing with deliverables and v14's D-ladder. |
| **DEL-1…DEL-5** | Mini-project deliverables | As submitted in the Group 17 proposal. |
| **D0–D11** | v14 Level-15 transition ladder | Unchanged; not used for anything else here. |
| **B0–B5** | RAG baseline ladder | As in the proposal / v14 §245. |
| **S1–S6** | Recipe **complexity flags** | Overlapping diagnostic strata, not six mutually exclusive bins. |
| **E0–E13** | Main experiments | E1–E12 from Report A, E0 and E13 added. Sub-experiments are `E#.#`. |
| **E14 / E14.x** | Jev decision-layer experiments | New (§17, §18). |
| **J1–J5** | JEPA experiments | Appendix A (optional). |
| **W0–W10** | Work packages with exit gates | Report A, extended. |
| **G-*** | Gates | Hard gates and promotion gates. |
| **[S#]** | Source registry IDs | §23. S1–S34 keep Report A's numbering; S35+ are added. |

### 0.2 Evidence markers

**Additional v2 marker:** `[A-code]` means a code audit asserted in the supplied attachment and awaiting independent reproduction. `[R]` in Appendix J means a primary page checked in this review; it does not mean its code or model was executed.


| Marker | Meaning |
|---|---|
| **[V]** | Verification marker carried from the supplied reports; check Appendix J for what was independently rechecked in this review. It does not mean model/code reproduction. |
| **[C]** | Reported by Report A from its own inspection; not re-checked here |
| **[P]** | Project hypothesis — must be tested |
| **[U]** | Unverified; do not cite until checked |

---

## 1. The decision

**Build a selective recipe semantic compiler with entity and quantity lineage, and use it as the shared substrate for CulinaryState-RAG (and later FlavorTwin).**

The compiler has these properties:
- It links ingredient mentions to stable food concepts **without losing meaningful products and forms**.
- It reconstructs **entity flow** (merge, split, reserve, discard, recombine) across steps.
- It accounts for quantities **symbolically first**, converting only with evidence.
- It separates **explicit / inferred / unknown** information everywhere.
- It **withholds** unsupported state or scientific claims.

NER is the entry task. Linking (NEL), event arguments, cross-step references, intermediate entities, allocation and provenance are **separate tasks with separate labels and separate metrics**.

**Where the research contribution is.** The contribution is the *reliable combination* of these components under sparse evidence, with calibrated abstention. It is not a bigger corpus or a newer model. Both reports agree on this independently.

### 1.1 What "beat Bagler" means — merged position

| Track | What is compared | Rule |
|---|---|---|
| **Legacy reproduction** | Ingredient-phrase NER on CoSyLab's 6,611 / 2,187 manual split, 7 tags, the lab's own macro-F1 scorer [S1][V] | Reproduce the CRF (95.52) and spaCy-transformer (95.90) first. Claim a win only with matched splits/scorers, a predeclared comparison, and uncertainty that covers recipe families and training seeds. Seed variation must be measured; no fixed ±0.3–0.5 pp noise band is assumed. |
| **Legitimate win areas** | Tasks the cited work leaves weak or incompletely evaluated | (a) Instruction-level process/utensil extraction (2020: F1 0.88 / 0.90) [S35]. (b) Calibrated ingredient linking beyond the top-200 (RecipeDB2: 79.50% accuracy, raw cosine ≥ 0.70) [S2]. (c) Unit/quantity normalization on a matched pair universe [S2]. (d) Cross-step quantity/entity lineage and provenance under our explicit benchmark contract; this is not a claim that no lab work has considered relations. |
| **Our expanded ontology** | Forms, products, references, ledgers | A **different benchmark**. Never compare it numerically to 95.90 / 96.04 as if the tasks were identical. |
| **Current external SOTA** | RecipeBERT-KA / RecipeRoBERTa-KA, reported SOTA on 5 of 7 recipe NER benchmarks (EACL 2026) [S31][V] | A required challenger, not something we assume we beat. |

**Proposed superiority claim (merged):** lower unsupported-link and unsupported-quantity rates, better source-held-out entity-flow accuracy, and better state-aware answers **at matched useful coverage and cost**. Superiority on the original NER/NEL benchmarks is claimed only after a matched reproduction succeeds.


### 1.2 Beating CoSyLab's *current* pipeline — attachment-reported code audit; independent reproduction pending

**What the supplied attachment reports.** It identifies `cosylabiiit/RecipeDB3_NER_Research_Paper` as a July 2026 code release and provides the notebook findings below [S64][A-code]. These are reproduction leads, not a code audit completed in this review. The culinary-laws paper describes using NER [S69], but does not alone establish that this repository is its precise checkpoint or the lab's current best system. Obtain an explicit paper-to-artifact mapping before describing it that way.

| Component (theirs) | What the code does | Reported result (notebook output) | Our observation (measured or read from code) |
|---|---|---|---|
| Ingredient NER | `microsoft/deberta-base`, 15 epochs, **random 80/20 split** (`random_state=48`) over **26,444 phrases** (the augmented set) | Test macro-F1 **0.9557** (micro 0.9603); per tag: QUANTITY 0.988, UNIT 0.976, DF 0.967, STATE 0.949, NAME 0.931, TEMP 0.924 | (a) The checkpoint is kept by **best test-set macro-F1 each epoch** (model selection on test). (b) **SIZE is absent** from the label dictionary and the report, although the data has 1,476 SIZE tokens. (c) Re-running their split, the supplied plan reports measuring **5.1% of test phrases with an exact duplicate in train** and **13.6% identical to a train phrase once numbers are masked** (augmentation families leak across the split). (d) **70.4%** of test phrases have a NAME string seen in train, so the test is head-heavy. |
| Instruction NER | spaCy blank-`en` model; **10,000 single instructions** (9,879 recipes); 12 labels; random 80/20 (`random_state=42`) | micro-F1 **0.9258**, macro **0.8698**. Weak spots: **QUANTITY 0.638**, **PREPROCESS 0.500** (support 17), DRYFRESH 0.831 (29), TEMPERATURE 0.880, ACTION 0.904 | Gold is stored as **pipe-separated value lists per column** (no character spans). BIO tags are produced by **exact token matching**, so every occurrence of a value is tagged, punctuation is stripped and temperatures are rewritten to digits. There are **no relations**: instruction mentions are not linked to ingredient-list lines, to each other, or to states. |
| Linking (RecipeDB2) | BERT embedding → USDA, cosine ≥ 0.70 | F1 87.90 / accuracy 79.50 on the top-200 ingredients | No calibration, no tail evaluation [S2] |
| Units (RecipeDB2) | Conversion tables | 43.90% of frequent ingredient–unit pairs converted | Coverage gap [S2] |

**Proposed matched-comparison strategy.** These moves are labeled M1–M7 to avoid colliding with the v14 B0–B7 RAG baselines. Exact-data comparisons are conditional on artifact access.

| # | Move | Metric | Target |
|---|---|---|---|
| M1 | **Reproduce** both notebooks exactly (same data, seeds, scorer) | their macro/micro F1 | a predeclared reproduction tolerance, interpreted with scorer equivalence and seed variation |
| M2 | **Re-evaluate under hygiene**: separate dev set for checkpoint selection; **augmentation-family-grouped split** (and number-masked dedup); SIZE included | same metrics | Honest numbers for *both* their model and ours. The direction and size of any change are unknown until both systems are rerun; report them neutrally. |
| M3 | **Instruction weak labels**: quantity grammar + kNN/GLiNER2.5 + Jev label verification on QUANTITY / PREPROCESS / DRYFRESH / TEMPERATURE | per-label F1 on their 80/20 split **and** on our span-level re-annotation (200 instructions) | QUANTITY ≥ 0.85 (vs 0.638); PREPROCESS and DRYFRESH significantly up (small support → report CIs) |
| M4 | **New capability 1 — mention→ledger alignment**: link each instruction mention to its ingredient-list line or an intermediate (Jev Choice over ledger rows) | alignment accuracy | not available in their pipeline |
| M5 | **New capability 2 — canonical form + facets** with calibrated accept/review/unresolved | Acc@1, ACCEPT precision, tail coverage | beat 79.50% on the top-200 *and* report the tail |
| M6 | **New capability 3 — quantity ledger** with portion-record selection + deterministic conversion | grounded-quantity coverage at ≤ 1% wrong-route rate | an improvement on a matched denominator if available; otherwise report our coverage without a direct numerical superiority claim, with zero unsupported accepted conversions |
| M7 | **New capability 4 — events, references, entity flow** | §18 E4–E6 | not available in their pipeline |

**Presentation rule.** M2 findings are reported as *evaluation-protocol differences* with the code and numbers attached, never as accusations. Prepare a reproducible protocol and a neutral artifact-backed account. Any external contact or sharing is a separate action, undertaken only when authorized; do not treat this plan as permission to send messages.

---

## 2. What is supported and what is still a hypothesis (merged)

| Statement | Status | Consequence |
|---|---|---|
| Ingredient tagging, food linking and procedural comprehension are different tasks | Supported across recipe NER, food NEL and flow-graph work [S1–S10] [C/V] | Separate labels, outputs, metrics |
| Ingredient-line NER on RecipeDB is near ceiling (CRF 95.52 vs spaCy-trf 95.90) | [V] [S1] | Not the headline contribution |
| Unverified machine-annotated (silver) training data slightly *hurt* on RecipeDB | [V] [S1] (95.71 vs 95.90) | Tiered gold chain; ablate silver |
| Recipe procedures need entity/action relations and omitted-argument resolution | RISeC, r-FG, Kiddon 2015 [S6][S7][S39] | Event arguments plus explicit unresolved references |
| Pipelined errors compound (r-FG edges drop sharply with predicted entities) | [V] [S8] | Oracle-upstream studies are mandatory |
| Food links degrade under ontology version change | FoodOntoRAG [S4] [C] | Version external mappings separately from internal IDs |
| Long context alone does not ensure reliable use of earlier facts | Lost in the Middle [S16] [C] | Compile entity-specific state packets |
| Artificial-data NEL scores overstate natural-text linking | FoodBench-QA ranges [S5] [C] | Report natural and artificial separately |
| Untuned LLMs are weak at recipe NER (RecipeDB few-shot macro-F1 5.88–32.90; Claude Sonnet 4 averaged 0.497 F1 vs 0.741 human IAA on UNER v2) | [V] [S1][S44] | Claude pre-annotates and verifies; never Gold on its own |
| Retrieval augmentation helps the long tail (kNN-NER; RENER up to +11 F on CrossNER) | [V] [S41][S42] | Test structural/exemplar retrieval |
| Order-as-supervision pretraining improves recipe entity tracking (+1.6% NPN-Cooking) | [V] [S46] | Closest published cousin of the JEPA idea (Appendix A) |
| Schema-based extractors can cut pipeline cost (GLiNER2.5: zero-shot macro-F1 56.17 vs 56.09 for GLiNER2 Multi over 16 sets) | [V] [S12] | Benchmark; small average gains are not domain evidence |
| A quantity/lineage compiler improves downstream RAG | [P] | E10 at matched model, evidence and token budget |
| Structural similarity beats recency for recipe references | [P] | E4/E5 |
| 100k Silver beats a smaller curated set | [P] — unproven | E8 scale ablation before expanding |
| A calibrated closed-set decision model (Jev) can replace LLM selectors/verifiers at much lower cost without accuracy loss | [P] — speed/cost figures are vendor-reported (40–200×, up to 444.6× cheaper) | E14 against open baselines |
| JEPA objectives help recipe parsing, linking or state tracking | [P] — no peer-reviewed recipe-domain JEPA found | J1–J4, gated (Appendix A) |
| Recipe text alone identifies process chemistry or sensory effects | Unsupported in general | Scientific evidence stays in a separate plane |

---

## 3. Frontier map (merged and re-verified)

### 3.1 CoSyLab / Bagler line (the comparison you will be judged against)

| Work | Task / data | Best reported | Open gap we target |
|---|---|---|---|
| Diwan, Batra & Bagler 2020 [S35][V] | RecipeDB ingredient NER (CRF), 7 tags; instruction processes/utensils | Ingredient F1 0.9611; cross-site 0.8672; processes 0.88, utensils 0.90 | Instruction NER, cross-source generalisation |
| Goel et al., LREC-COLING 2024 [S1][V] | 6,611 manual / 26,445 augmented / 88,526 machine-annotated phrases; 2,187 test | spaCy-trf macro-F1 95.90 / 96.04 / 95.71; Stanford NER 95.52; few-shot LLMs 5.88–32.90 | Ingredient-only; TEMP tag weakest; non-standard macro-F1 → reproduce their scorer |
| RecipeDB2 (arXiv 2609.22099, preprint) [S2][V] | 128,942 recipes; 35,474 ingredient entries; USDA mapping; 34-category classifier | Linking F1 87.90 / accuracy 79.50 on top-200; 73.01% of entries mapped at cosine ≥ 0.70; 43.90% of frequent unit pairs converted; classifier accuracy 89.12% [V] / weighted F1 89.16% [C] | Tail linking, calibrated thresholds, quantity coverage, ontology integration listed as future work |
| Bagler, generative grammar of cooking [S36][V] | "Cubits": ingredient / process / utensil phrases | 268 processes, 69 utensils | Seed vocabulary for P5 |
| **RecipeDB3 NER code + data** (GitHub, Jul 2026) [S64][A-code] | 26,444 ingredient phrases (7 tags); 10,000 annotated instructions (12 labels) | DeBERTa ingredient macro-F1 0.9557; spaCy instruction micro-F1 0.9258 / macro 0.8698 | The current comparison target: see §1.2 |
| Bansal … Bagler, *Universal statistical laws governing culinary design* (arXiv 2604.28021, 2026) [S69][V] | Corpus annotated with "state-of-the-art" NER (ingredients, techniques, utensils, attributes); Zipf/Heaps/Menzerath-type laws | — | Provides culinary-distribution context; does not, by itself, identify a current best NER checkpoint. Frequency-bucket evaluation remains appropriate |
| CocktailDB NER (GitHub, Apr 2026) [S65][V] | Sister NER code and annotations for cocktails | — | Cross-domain transfer test |
| Nutritional Profile Estimation (arXiv 2004.12286 + repo) [S66][V] | NER + Jaccard similarity + unit mapping → USDA | Documents errors such as "500 g or 1 cup" parsed as "500 cups" | Baseline for E6 quantity grounding |

RecipeDB2 has date-header inconsistencies: cite the title and identifier, not a release day [C]. It is a preprint, so it is not peer-reviewed.

### 3.2 External comparison set

| Work | Contribution | Our use |
|---|---|---|
| TASTEset v1 / v2 [S27][S37][V] | 9 → 15 food entity types; best F1 0.935 (v1) / 0.943 (v2); rare v2 types weak | Independent ingredient-attribute benchmark; extensible-label template |
| ReciFine / ReciFineGold, Findings EACL 2026 [S29][S30][V] | Extends RecipeNLG: 97M+ entity mentions, 10 types, 2.2M recipes; human-annotated benchmark | Acquisition priority: external instruction-NER test and permitted Silver reuse |
| Knowledge-augmented token classification (RecipeBERT-KA / RecipeRoBERTa-KA), EACL 2026 [S31][V] | Entity-type-specific, knowledge-prefix token classification; SOTA on 5/7 recipe benchmarks; merged 7-dataset corpus | **Required current challenger**; count multi-pass cost |
| English r-FG 2020 + Fan & Hunter 2023 [S7][S8][V] | 300 recipes, r-NE tags and flow edges; NER F1 up to 94.1; labelled graph F1 92.2 | Graph benchmark and schema crosswalk |
| RISeC 2020 [S6][C] | Entities, relations, zero anaphora in instructions | Omitted-argument baseline |
| ARA 2021 / REAL 2021 [S9][S10][C] | Action alignment across recipes; entity-action-location graph reasoning | Structural exemplar retrieval; state-tracking baseline family |
| Kiddon et al. 2015 "Mise en Place" [S39][V] | Unsupervised action graphs with implicit arguments | Deterministic implicit-argument default |
| OpenPI / OpenPI2.0 / OpenPI-C [S40][V] | Open-vocabulary state changes; canonicalisation; documented hallucinated changes | Closed, versioned state vocabulary |
| FoodSEM 2025 [S3][C] | Fine-tuned food NEL (FoodOn, Hansard, SNOMED CT) | Domain-linking baseline; audit memorised IDs |
| FoodOntoRAG (IEEE BigData 2025 / arXiv 2026) [S4][C] | Retrieve → grounded select → separate scorer → retry; ontology drift | Retrieval-first NEL baseline |
| FoodBench-QA 2026 [S5][C] | Shared-task food NER/NEL; natural 60.71–80.89 vs artificial 87.75–95.75 macro-F1 | External target if task-compatible |
| GLiNER / GLiNER2 / GLiNER2.5 [S43][S11][S12][V] | Zero-shot schema extraction; 2.5 adds boundary prediction, joint relations, span attributes; 74M / 194M / 287M, Apache-2.0 | Cheap flexible baseline and Silver cascade |
| GLiNER2.5-Decide [S13][C] | Typed decision outputs | Review-routing candidate; calibrate locally |
| kNN-NER [S41], RENER [S42], RA-IT open NER [S17] | Retrieval-augmented NER | Structural-similarity experiments |
| SINERA 2024 [S14][V] | Position-shortcut bias in food NER; augmentation | Position-shuffle robustness test |
| Ingredient Parser (strangetom) [S21–S23][V] | CRF parser, 94.94% sentence accuracy; FDC "foundation foods" matcher | Strong P2/P4 baseline; **defaults to water density** and adds `raw` hints → adapter required |
| JFC-Recipe, LREC 2026 [S47][V] | Japanese recipes: food-item links to a composition DB plus amount/unit → grams via a weight table, with IAA | Direct precedent for the quantity ledger's evidence route |
| Nandy et al., NAACL 2024 [S46][V] | Order-as-supervision pretraining (incl. embedding regression) for recipe entity tracking | Self-supervised baseline for J-experiments |
| INDoRI [S45][V] | 5,187 Indian recipes, 18 regions | Source for the S4 Indian/Hinglish stratum (check licence) |
| ReGraph 2026 [S26][C] | Image-to-recipe-graph (abstract only) | Watch list |
| Actionable cooking KGs for robots, 2025 [S34][C] | Overlapping action/prerequisite representation | Must appear in the novelty audit |

**Neither report found published GLiNER, Claude or retrieval-augmented results on TASTEset or RecipeDB NER.** A well-controlled comparison could be useful, but it rests on a limited search, so run a final novelty audit before writing "first".


### 3.3 GitHub and Kaggle resource map (new in v1.2)

| Resource | Where | What it gives us | Use | Check |
|---|---|---|---|---|
| `RecipeDB3_NER_Research_Paper` | github.com/cosylabiiit [S64] | 26,444 ingredient phrases; 10k instructions with 12 value-list columns; DeBERTa + spaCy notebooks | Reproduction (M1–M2); instruction re-annotation seed | Licence not stated in the README; ask the lab |
| `Recipedb-companion-data` | github.com/cosylabiiit [S67] | 2020 manual train/test (the 6,611 / 2,188 split) | Legacy E1.1 | — |
| `Recipe_NER_DL` | github.com/cosylabiiit | 2023 DL NER notebooks (likely the Goel et al. 2024 line) | E1.1 reproduction | Confirm against the paper |
| `CocktailDB_NER_Research_Paper` | github.com/cosylabiiit [S65] | Cocktail ingredient + instruction annotations | Domain-shift test | — |
| `Nutritional-Estimation-In-Recipes` | github.com/cosylabiiit [S66] | NER → Jaccard → USDA + unit mapping | Quantity/linking baseline | — |
| CulinaryDB | cosylab.iiitd.edu.in/culinarydb [S68] | Original→aliased ingredient mappings, synonyms, **compound ingredients with components**, 22 regions | Seed alias table + product (compound) concepts for §5 | Licence |
| RecipeDB2 repo | github.com/cosylabiiit | Code behind the RecipeDB2 framework [S2] | Linking reproduction (E3.3) | — |
| Ingredient Parser | github.com/strangetom [S21] | CRF parser + FDC matcher | P2/P4 baseline (with adapter) | MIT-style licence; check |
| NYT ingredient-phrase-tagger data | GitHub [S38] | ~180k labelled ingredient lines (noisy) | Pretraining / Silver only | Label noise documented |
| TASTEset v1/v2 | GitHub / IEEE DataPort [S27][S37] | 700 / 1,000 annotated recipes | External benchmark | Folds |
| **6000+ Indian Food Recipes** (Archana's Kitchen) | Mendeley Data, DOI 10.17632/xsphgmmh7b.1; Kaggle mirrors [S70] | Original **Hindi/Hinglish** ingredients and instructions **paired with machine translations** | Ready-made **S4 stratum** and a translation-robustness test (original vs translated) | Scraped source, so check terms; translations are noisy |
| Kaggle "What's Cooking?" (Yummly) | kaggle.com [S71] | ~40k ingredient lists with cuisine labels | Alias mining; cuisine-shift (S6) sampling | Competition terms |
| Food.com recipes and interactions | Kaggle [S72] | ~180k recipes + reviews | Raw pool (overlaps with RecipeDB's Food.com sources, so dedupe) | Terms; duplicates with RecipeDB |
| RecipeNLG / ReciFine | [S29][S32] | Large raw pool / Silver | Silver, Gold benchmark | Overlap audit |
| HF community recipe-NER models (e.g., `fastyBOOM/recipe-ner`, F1 0.877 on its own split) | huggingface.co | Weak baselines | Sanity check only | Unknown provenance |

**Kaggle scope.** The supplied plan did not identify a directly comparable stronger recipe-NER or quantity-grounding result; this is a limited search result, not an exhaustive leaderboard claim. Kaggle's value is **raw and regional data** (especially Indian/Hinglish pairs), not a stronger baseline. GitHub's value is CoSyLab's own code, which defines the comparison.

---

## 4. Reconciliation: where the two reports differed and what is final

| Topic | Report A | Report B | **Final decision** |
|---|---|---|---|
| Pipeline granularity | P0–P10 compiler stages | L0–L6 layers | **P0–P10 canonical**; L-layers mapped (§4.2) |
| Verification tiers | Deep Gold / Gold-Light / Silver / Bronze (v14 names) | Bronze / Silver / Gold / Platinum | **v14 names**, plus a **Sealed** status for the test partition. Platinum = Deep Gold + Sealed + no-LLM initial passes. |
| Annotation depth | "D0–D5" | — | Renamed **A0–A5** |
| Gold size (mini-project) | 20 design + 100–200 seed; measure throughput first | 300 recipes (200 test / 100 dev) over 6 strata | **Phased:** 20-recipe design pilot → measure minutes/recipe → 100-recipe seed at A2 (40 of them to A4) → sealed test of 100 at A2 (40 at A4). 300 is the stretch target. v14's 750–1,000 Deep Gold remains the long-term target. |
| Thresholds | Risk budgets chosen on a calibration partition; no fixed cut-offs | Numeric starting bands (e.g., accept p ≥ 0.90) | **Risk budgets are the policy**; Report B's bands are only **initialisation priors** before calibration |
| Label names | Layered annotation (FOOD_MENTION …) | Label schema v1 mapped to RecipeDB / TASTEset / r-FG | **Layered canonical schema** (§6) plus **legacy adapters** to RecipeDB's 7 tags, TASTEset and r-FG |
| Structural similarity | Three mechanisms; graph-aware antecedent selection | kNN-NER datastore plus SEFS-signature exemplar retrieval | **Both**: exemplar retrieval (incl. kNN-NER and SEFS signatures), ontology retrieval, antecedent retrieval (§11) |
| Inferred steps | Proposals only, outside the observed graph | Rule library + ≥ 1 retrieved precedent, separate tier | **OMITTED_STEP_CANDIDATE** outside the observed graph; produced by rule + precedent; never source fact |
| Existing large corpora | Inspect ReciFine before making Silver | Not covered | **Inspect ReciFine first** (permissions, crosswalk, overlap) |
| Claude Max | Operational packets; measure first | Pre-annotation + critic pass; per-label precision rule | **Merged protocol** (§7.6) |
| Agreement targets | Report per task; investigate low agreement | Numeric targets per label family | Report B's numbers are **targets to check**, and low agreement triggers a schema review (Report A) |

### 4.1 The compiler stages (canonical)

| Stage | Transformation | Retained output | Promotion gate |
|---|---|---|---|
| **P0** Source contract | Source, rights, locale, checksums, duplicate family | Immutable recipe and manifest | Source and split lineage known |
| **P1** Text preparation | Unicode, fractions, ranges, whitespace; reversible parsing view; transliteration kept alongside the original | Raw text plus offset map | Every annotation maps back to raw text |
| **P2** Mention recognition | Food, amount, unit, form, state, action, tool, condition, endpoint | Typed spans and attributes | Gold span/attribute performance |
| **P3** Food/product linking | Candidates → internal concept or unresolved set | Food IDs, modifiers, link type, candidates | Precision and coverage on held-out Gold |
| **P4** Quantity structure | Ranges, fractions, packaging, qualifiers, multipliers | Symbolic typed quantity expressions | Structure exact match; unit validity |
| **P5** Event parsing | Actions; participants, conditions, endpoints, branches; process-ontology mapping | Event records, typed relations | Argument/condition/ordering accuracy |
| **P6** Referential grounding | it/them/mixture/remaining/reserved; omitted arguments | Entity IDs or unresolved candidate sets | Cross-step and implicit reference accuracy |
| **P7** Entity-flow replay | Intermediates; merge, split, transfer, reserve, discard, recombine | Versioned entity graph, state snapshots | Replay and temporal integrity |
| **P8** Quantity grounding/accounting | Sourced portion/density; event allocations | Quantity ledger, uncertainty, residuals | Evidence routes; accounting consistency |
| **P9** Task sufficiency | Can this question be answered? | Capability vector and route | Calibrated selective risk |
| **P10** Scientific enrichment | Join compatible experimental evidence (DEL-1 registry) | Evidence packet, claim ledger | Scientific provenance, domain support |

P3–P6 exchange information: this is not a waterfall. Corrections are new annotation **versions**. P4 parsing precedes food-specific grounding, and P8 may wait while quantities stay symbolic.

### 4.2 Mapping Report B's layers onto the stages

| Report B layer | Canonical stage |
|---|---|
| L0 text cleanup | P1 |
| L1 span extraction (hybrid NER) | P2 |
| L2 lexical normalisation (lemma, brand → attribute, modifier peeling) | end of P2 / start of P3 |
| L3 canonical linking | P3 |
| L4 quantity ledger (CQPO) | P4 + P8 |
| L5 process/condition normalisation | P5 |
| L6 state/event graph | P6 + P7 |

### 4.3 Architecture

```mermaid
flowchart TD
    A["P0 Immutable recipe + source manifest"] --> B["P1 Reversible text view + offsets"]
    B --> C["P2 Spans + attributes (hybrid NER)"]
    C --> D["P3 Canonical foods / products"]
    C --> E["P4 Symbolic quantities"]
    C --> F["P5 Events + process ontology"]
    D --> F
    F --> G["P6 References + omitted arguments"]
    D --> G
    G --> H["P7 Entity and state lineage (versioned graph)"]
    E --> I["P8 Quantity accounting with evidence routes"]
    H --> I
    H --> J["P9 Task-sufficiency gate"]
    I --> J
    K["P10 Scientific evidence registry (DEL-1)"] --> J
    J --> L["Grounded answer / ask one question"]
    J --> M["Review or abstain"]
```

**P2 hybrid NER (Report B), feeding the stages above:**
- gazetteer and rules (numerals, closed unit lexicon);
- a fine-tuned encoder (+CRF);
- kNN-NER interpolation from a training-only datastore;
- GLiNER2.5 for labels missing from training;
- a Claude verifier on low-confidence spans only, using structure-retrieved training exemplars.

The verifier may **relabel or abstain** within proposed spans. It may never invent spans or text.

**Global rules (merged):**
1. Prediction precision never exceeds evidence precision.
2. Unknown is not a mismatch. It is first-class and neutral in retrieval.
3. Every stage is replayable from raw text plus a versioned config (event-sourced).
4. An LLM may *propose*. Decisions are made by rules, or by calibrated decision models — Jev or an open alternative — and those count only after **our own** recalibration. Only humans commit Gold.
5. Hard validity gates come before any confidence score (§14.1).
6. Recipe text never becomes scientific evidence (separate evidence planes).
7. Use relational/JSON tables first. Entity-version and typed-edge tables express the graph without a graph database or GNN until benchmarks justify one.

---

## 5. Canonical ingredients without losing meaningful products

### 5.1 Three identities (from Report A — adopted)

1. **Food concept:** a reusable vocabulary entry (garlic; garlic paste).
2. **Recipe entity (lot):** a particular ingredient lot, mixture or reserved portion in one recipe.
3. **Entity state version:** that entity at a particular event/time, with its form, location, thermal status and quantity references.

"Garlic" in two recipes shares a *concept*, not a physical entity. Two garlic additions in one recipe may be different *lots*. Dicing does not create a new concept, but the later state must never overwrite the original mention.

### 5.2 Identity-preserving versus product-forming (merged; Hinglish rows added)

| Phrase | Representation | Mistake to avoid |
|---|---|---|
| large red onion, finely diced | onion; variety red; size large; form diced; granularity fine | a new concept per descriptor combination |
| 3 cloves garlic | garlic; count 3; portion unit = clove | linking "clove" to the spice |
| ground cloves | clove (spice); form ground | linking to garlic |
| sour cream / cream cheese | lexicalised **product** concept (+ dairy relation) | stripping "sour"; splitting into two foods |
| tomato paste vs tomato, chopped | distinct product DERIVED_FROM tomato vs tomato with form chopped | treating concentration as a cut modifier |
| corn flour / coriander | **locale-conditioned candidate sets** (corn flour vs cornstarch; coriander leaf vs seed) | one global alias |
| jeera / haldi / dhaniya | alias → cumin seed / turmeric / coriander (**leaf or seed resolved by FORM/PART context**); surface form kept | dropping the original Hinglish token |
| chicken stock | compound product; chicken origin if supported | chicken meat + state flag |
| garlic powder | product/form distinction at declared granularity | reusing fresh-garlic portion/density evidence |
| frozen spinach, thawed and drained | spinach; initial state + preparation order | treating drained mass as packaged mass |
| brand sauce | brand/product record; formulation only if sourced | inventing a standard composition |
| half the reserved sauce | recipe portion reference + fraction | creating a new global concept |

**Rule.** A product earns a distinct concept when its composition, processing or culinary meaning cannot be faithfully represented by the base food plus declared modifiers. Keep `DERIVED_FROM`, `HAS_INGREDIENT` and `IS_VARIANT_OF` relations, each with its own evidence. Never decompose a purchased compound food into assumed ingredients.

### 5.3 Linking cascade (P3) with calibration

1. Exact curated alias (bypasses ranking **only if** unambiguous in the locale/context).
2. Normalised alias (lemma, plural, spelling).
3. Fuzzy match (character n-gram / token-set).
4. Dense bi-encoder top-20 over internal names + RecipeDB/FlavorDB IDs + FoodOn labels/synonyms/definitions.
5. Cross-encoder rerank (trained on gold link pairs + hard negatives: milk ↔ milk chocolate ↔ coconut milk).
6. LLM selector (Claude) over top-5 **with definitions**, only in the review band.
7. A calibration model over (rank, score margin, alias type, frequency bucket, type/form compatibility, "no valid candidate" signal) → P(correct).
8. Route: **accept / review / unresolved**. Always offer `NO_VALID_CANDIDATE`.

**ID policy.**
- Internal stable IDs are primary.
- RecipeDB/FlavorDB IDs are the course-aligned cross-references and the evaluation target.
- FoodOn is the semantic and interoperability layer, versioned per snapshot.
- USDA FDC IDs are used **only** for composition/portion evidence, chosen by data type (Foundation / SR Legacy / FNDDS / Branded) [S20].

### 5.4 Vocabulary lifecycle (Report A — adopted)

`PROPOSED → {ALIAS | MODIFIER_COMPOSITION | PRODUCT_CONCEPT | AMBIGUOUS | NON_FOOD} → REVIEWED → ACTIVE`

**Record per entry:** approver, source examples, locale, external crosswalk version and negative examples.

**Monitor:** mention-weighted and unique-alias coverage, rare/regional coverage, mistaken merges, fragmentation and review backlog. v14's 10k-concept figure is a *scale hypothesis*, not a quota.

---

## 6. Label system: layered schema, legacy adapters, manual, picker

### 6.1 Annotation layers (Report A structure, with Report B's label inventory)

| Layer | Labels / fields | Example |
|---|---|---|
| **Spans (ingredient lines)** | FOOD_MENTION · AMOUNT · UNIT · SIZE · FORM · PREP_STATE · TEMP · DRY_FRESH · VARIETY · PART · BRAND · PURPOSE · ALTERNATIVE · OPTIONAL · QUALITATIVE_AMOUNT · DIET | "1 cup finely chopped red onion" |
| **Spans (instructions)** | ACTION · FOOD_MENTION · INTERMEDIATE_MENTION · TOOL · DURATION · HEAT/TEMPERATURE · ENDPOINT · FOOD_ACTION · TOOL_STATE · QUANTITY_IN_STEP | "simmer the sauce on low flame until thick" |
| **Mention qualifiers** | optional · divided · reserved · approximate · additional · to_taste · as_needed · negated · hypothetical | "plus more", "if too thick" |
| **Reference relations** | REFERS_TO · PART_OF · DERIVED_FROM · SAME_LOT_AS · F-EQ (coref) | "it" → sauce entity |
| **Event roles** | INPUT · OUTPUT · TOOL · DESTINATION · MEDIUM · CONDITION · ENDPOINT | sauce → simmer |
| **Flow operations** | TRANSFORM · MERGE · SPLIT · TRANSFER · RESERVE · DISCARD · RECOMBINE · SERVE · WAIT | "reserve half the sauce" |
| **Temporal/control** | BEFORE · DEPENDS_ON · PARALLEL_WITH · OPTIONAL_BRANCH · ALTERNATIVE_BRANCH · REPEAT_UNTIL | "bake until golden" |
| **Quantity relations** | AMOUNT_OF · FRACTION_OF · REMAINDER_OF · PACKAGE_CONTENT · ALLOCATED_TO | "half of reserved sauce" |
| **State fields** | form · phase · location · qualitative thermal/texture/visual · numeric only when supported | "browned"; temperature unknown |
| **Annotation status** | task mask · disagreements · adjudication · unresolved candidates · guideline version · assistance visible? | "links verified; chemistry unannotated" |

**Storage.**
- Raw character offsets (declare code-point vs byte), relations and attributes.
- BIO/BILOU only inside models.
- Nested and discontinuous spans need an explicit representation or a declared exclusion. A flat tagger must never silently erase them.

### 6.2 Legacy adapters (so we can be scored on others' benchmarks)

| Ours | RecipeDB (7) [S1] | TASTEset [S27] | r-FG [S7] |
|---|---|---|---|
| FOOD_MENTION | NAME | FOOD | F |
| AMOUNT | QUANTITY | QUANTITY | Q (in steps) |
| UNIT | UNIT | UNIT | — |
| SIZE | SIZE | PHYSICAL QUALITY (part) | — |
| FORM / PREP_STATE | STATE | PROCESS / PHYSICAL QUALITY | — |
| TEMP | TEMP | — | — |
| DRY_FRESH | DF | — | — |
| ACTION | — | — | Ac / Ac2 |
| TOOL | — | — | T |
| DURATION | — | — | D |
| ENDPOINT | — | — | Sf |
| FOOD_ACTION / TOOL_STATE | — | — | Af / At, St |

Ambiguous boundary cases (e.g., "sour cream" NAME vs STATE) follow **the benchmark's own convention** when scoring on that benchmark, and ours internally. Record every adapter decision in the decision log.

### 6.3 Minimum manual per label

1. Definition and purpose.
2. Positive and negative examples, plus hard cases.
3. Boundary, punctuation and overlap rules.
4. Allowed attributes and relation endpoints.
5. Cross-step scope and temporal rule.
6. Policy for omission, ambiguity, contradiction and not-applicable.
7. Evidence requirement and Gold-verification requirement.
8. Adjudication examples and a versioned decision log.
9. Hinglish/transliteration conventions (keep the surface form; canonical goes in P3).

### 6.4 Schema evolution (Report B — adopted)

**Versioning:** `LM-vMAJOR.MINOR.PATCH`.
- **MAJOR** = a label split or merge → migration script + re-adjudication.
- **MINOR** = a new child label; old Gold stays valid at parent granularity.
- **PATCH** = clarification only.

Each document stores `labels_annotated_for = [...]`. A label that was never annotated is scored as **missing annotation**, never as `O`. Evaluate every model only on the label set its Gold was annotated under. This is how new labels can arrive without corrupting old Gold.

### 6.5 Annotation tool and "label picker"

**Pilot.** Run INCEpTION (relations, coreference, curation) against Label Studio (simpler NER and relations) on the **same 20 difficult recipes**, then choose [S18][S19].

**Picker requirements.**
- Raw text, plus the current entity's timeline.
- Food candidates with aliases and definitions.
- Relation-compatible options only.
- Mandatory `UNRESOLVED`, `NOT_STATED` and `NO_VALID_CANDIDATE` choices. The annotator is never forced onto the nearest wrong food.

**Panes.** Source · current event/entities · span/attribute editor · canonical search · quantity expression + evidence route · contradiction/review queue.

**Assistance rules.**
- **Deep Gold:** model predictions are hidden during the initial passes; registry browsing is allowed.
- **Gold-Light / Silver review:** predictions are shown and `assistance_visible = true` is recorded.

A custom UI is deferred until the pilot shows the tools block real operations.

---

## 7. Gold: verification tier × annotation depth × complexity stratum

### 7.1 Annotation depth (A0–A5)

| Depth | Annotated | Supports |
|---|---|---|
| A0 | Immutable source + manifest | Inventory, deduplication |
| A1 | Ingredient and quantity spans | NER, quantity structure |
| A2 | Canonical links, forms, states, locale | NEL, food representation |
| A3 | Actions, arguments, conditions, endpoints | Event extraction |
| A4 | References, intermediates, allocations, branches, state replay | Procedural understanding, ledgers |
| A5 | Independently verified external measurements for compatible cases | Process-effect science (DEL-1 joins) |

A5 never means "ask the LLM to add chemistry". A recipe can be Deep Gold at A2 and unannotated at A4, and unannotated relations are **not negatives**.

### 7.2 Verification tiers (v14 names, with Sealed status)

| Tier | Required process | Use |
|---|---|---|
| **Deep Gold (Sealed)** | Two independent humans, **no LLM pre-fill on the initial passes**, adjudicated, validators passed, source-locked, hashed | Final test only |
| **Deep Gold** | Independent A/B + adjudication + validators | Calibration, dev |
| **Gold-Light** | Human verification of specified fields; assistance logged | Training, dev, active learning |
| **Silver** | Model extraction + validators + sampled audits (incl. permitted ReciFine reuse) | Training at scale, vocabulary mining |
| **Bronze / synthetic** | Rules, auto-parsers, generated examples (tagged `synthetic`) | Pretraining, stress tests; never dev or test |

**Two rules.**
- A validator pass proves only the constraints it checks. Two models agreeing is not Gold.
- Correction after seeing model output is Gold-Light, never "independent".

### 7.3 Complexity strata (Report B), applied to every tier

| Stratum | Definition |
|---|---|
| S1 Simple | ≤ 8 ingredients, linear steps |
| S2 Multi-component | ≥ 2 sub-preparations, merges/splits |
| S3 Implicit-heavy | ≥ 3 null-argument steps or "the mixture" references |
| S4 Indian / Hinglish | Regional Indian, code-mixed terms (jeera, tadka, katori) |
| S5 Unit-heavy | Ranges, household/Indian measures, "to taste", multipliers |
| S6 Cold-region | Cuisines/regions held out of training |

### 7.4 Sizes (merged phasing)

| Phase | Content | Exit condition |
|---|---|---|
| G-0 Design pilot | 20 hard recipes, both annotators, all layers | Manual v1.1; minutes/recipe measured per depth |
| G-1 Seed (dev/calibration) | 100 recipes at A2; **40 of them to A4**; stratified S1–S6 | Disagreement understood; key labels stable |
| G-2 Sealed test | 100 recipes at A2 (40 at A4); double-annotated, no LLM pre-fill | Hashed; never tuned on |
| Stretch | 300 recipes (Report B's 200 test + 100 dev) | Only if G-0 throughput allows |
| v14 long-term | 750–1,000 Deep Gold (≈ 300 train/dev · 300 calibration · 400 sealed), 3–5k Gold-Light, 60–100k Silver | After the mini-project; scale gated by E8 |

**Precision arithmetic.**
- The familiar ≈384 calculation applies to an independent Bernoulli accuracy/proportion near 0.90 at ±3 pp, not directly to F1. F1 requires task-specific uncertainty estimation. Core labels may have many mentions at 100 recipes, but the recipe-cluster count still limits uncertainty estimation; rare labels (TEMP, DRY_FRESH, ENDPOINT, PURPOSE) will not. Report those with recipe-level bootstrap CIs and oversample them by targeted retrieval.
- Per-stratum results (about 15–20 recipes each) are **diagnostic**, not headline claims.
- Keep natural-distribution and challenge samples identifiable. A 70/30 natural/challenge mix is the starting proposal, and natural performance is reported separately.

### 7.5 Agreement (targets to check, not promises)

| Item | Metric | Target |
|---|---|---|
| Core ingredient spans | exact span-F1 | ≥ 0.90 |
| ACTION / TOOL / DURATION | exact span-F1 | ≥ 0.85 |
| ENDPOINT / FORM / INTERMEDIATE | exact (+ partial) span-F1 | ≥ 0.80 |
| Relations / coreference | edge-F1 | ≥ 0.75 |
| Link decisions | Cohen's κ | ≥ 0.80 |
| Implicit arguments / omitted steps | κ or F1 | ≥ 0.65 (contested; report honestly) |

Token-level κ is inflated by `O`, so use span-F1 for spans and Krippendorff's α if a third rater joins. Agreement **below target triggers a schema/evidence review before any Silver expansion**.

### 7.6 Claude Max protocol (merged)

**Facts.** Claude and Claude Code share subscription usage limits, and API usage is billed separately [S25][C]. The plan therefore does **not** guarantee any number of accepted recipes. Measure it.

**Work packets.** Never paste the 42k-line SSOT into a request:
1. **Contract:** relevant v14 sections + schema version + definitions + acceptance criteria.
2. **Vocabulary:** mention, locale, curated candidates, negatives → chosen ID or unresolved set.
3. **Event:** raw current step + active-entity packet + relevant prior spans → atomic events and references.
4. **Quantity:** parsed expressions + approved conversion records. **Code** executes the arithmetic.
5. **Reviewer:** source + annotations + validator flags → flagged fields with reasons (the "critic pass").
6. **Migration:** old/new schema + explicit rule. The source and sealed test are protected.

**Operating rules.**
- Pilot on 50–100 recipes. Batch 10–25 ordinary recipes or 1–5 hard flow recipes, then adjust from measurements.
- Log `model_id`, prompt hash, timestamp, tokens, retries, accepted records, failure types and review minutes.
- **One extraction → deterministic validation → one targeted repair → review/unresolved.** No open-ended rewriting loops.
- Per-label rule: if Claude's pilot precision for a label is < 0.85, that label becomes **human-first**.
- Claude is never the sole source of a Deep Gold label, and never touches the sealed test's initial passes.
- The best value of the subscription is Claude Code for converters, validators, scorers and adapters.

### 7.7 Splits, leakage and source roles

**Leakage rules.**
- Form duplicate, source and likely derivative families **before** splitting (MinHash Jaccard ≥ 0.8 is an initial duplicate-candidate rule, not an automatic proof that two dishes are identical).
- Augmentation, translations, teacher outputs, kNN datastores, retrieval exemplars and prompt examples all obey the split.
- A public corpus may already be in a frontier model's pretraining. Add **new-source/private held-out** recipes where possible and disclose the limitation.

| Resource | Role | Acquisition check |
|---|---|---|
| CoSyLab ingredient phrases (+ 2020 instruction set, on request) [S1][S35] | Legacy reproduction | Exact release, teacher lineage, derivative duplicates, scorer |
| RecipeDB / RecipeDB2 / Foodoscope APIs [S2] | Statistics, IDs, linking comparison | API access (requested), schemas, redistribution |
| ReciFine / ReciFineGold [S29][S30] | Instruction-entity Silver + external human benchmark | Crosswalk, official splits, protocol, permissions, overlap with RecipeNLG |
| TASTEset v1/v2 [S27][S37] | Independent ingredient-attribute benchmark | Version labels and folds |
| RISeC / r-FG / ARA [S6–S9] | Relations, implicit arguments, actions | Exhaustiveness of links; semantic compatibility |
| FoodSEM / FoodOntoRAG resources [S3][S4] | External NEL checks | Ontology snapshot; natural vs artificial |
| JFC-Recipe [S47] | Quantity-to-grams annotation precedent | Licence; Japanese-language scope |
| INDoRI [S45], RecipeDB2 Indian content | S4 stratum source | Licence before storing raw text |
| RecipeNLG [S32] / Recipe1M+ [S33] | Raw pools | Original sources, duplicates, text rights |

**Never mix copies of the same recipe from RecipeNLG, ReciFine and other pools into nominally independent splits. Keep scientific study families disjoint separately from recipe families.**

---

## 8. Three connected ledgers plus a separate evidence registry

| Ledger | Key fields (merged) | Prevents |
|---|---|---|
| **Ingredient / entity** | `concept_id`, `canonical_source`, `xrefs{}`, `lot/entity_id`, `version`, `raw_mention`, `char_span`, `surface_name`, `head_lemma`, `lang`, product/form/state facets, `parents[]`, `location`, `lifecycle_status`, `link_band`, `link_p`, `candidates[]`, `provenance`, `verification`, `guideline_version`, `model_versions{}` | Wrong aliases, merged lots, lost parentage |
| **Quantity** | `quantity_id`, `entity_version_id`, `raw_qty_text`, symbolic `expression`, `value_min/max` (exact rationals), `is_range`, `multiplier`, `approximate`, `unit_raw`, `unit_canonical`, `unit_system`, `unit_variant`, `dimension`, `basis`, `kind`, `allocation{fraction, parent_qty}`, `conversion_path[{from,to,factor,source,evidence_id}]`, `uncertainty{source_var, interval}`, `unresolved_reason` | Fabricated grams, double counting, quantity loss |
| **Event / state** | `event_id`, `step_id`, `text_order`, `depends_on[]`, `event_type`, `action_raw`, `process_id`, `process_band`, `effect_class`, `inputs[]`, `outputs[]`, `tool_id`, `conditions{heat, temp_value/range, duration_min/max}`, `endpoint_text`, `trajectory`, `provenance`, `inference_rule_id`, `precedent_ids[]`, before/after entity versions | Forgotten steps, impossible references, invented conditions |
| **Scientific evidence (DEL-1)** | `study_id`, food/matrix/state/process, measurement basis, conditions, method, source table/span, evidence tier, verification | Recipe instructions masquerading as chemistry |

**Entity lifecycle.**
- States: `ACTIVE`, `RESERVED`, `INCORPORATED`, `DISCARDED`, `SERVED`, `UNRESOLVED`.
- Incorporation ≠ the material vanished. Discarding broth ≠ molecular destruction. Heating ≠ a numeric composition change.

**DAG rules.**
- Text order and execution dependencies are stored separately ("meanwhile" ≠ sequential).
- "Repeat until smooth" is a **control construct**, so no iteration count is invented.
- A live session logs actual iterations as new events, keeping the execution history acyclic.

**Invariants checked in CI.**
1. Every explicit span round-trips to raw offsets.
2. Every ingredient-list lot is accounted for as used, optional, alternative, garnish, explicitly discarded, unresolved, or apparently unused; not every mention is itself a consumption event.
3. Nothing is consumed after DISCARD or before it is produced.
4. Split fractions sum to ≤ 1 per compatible basis.
5. Mass balance is checked **only** where every term is known; otherwise the result is `unknown`, not `fail`.
6. Inferred events never feed explicit-only queries.
7. Grams invented without an evidence route = 0.

---

## 9. Quantity normalisation and allocation

### 9.1 Three problems, three evidence requirements

1. **Same-dimension conversion** (g ↔ kg, °C ↔ °F): deterministic code, raw value retained.
2. **Culinary-unit interpretation** (cup, tbsp, katori): convention from source locale; an unresolved convention stays ambiguous, with `unit_variant` and an interval.
3. **Food-specific grounding** (volume/count/container → mass): needs food, product, form, packing, size and basis, plus compatible portion/density evidence (USDA FDC by data type [S20]; JFC-style weight tables [S47]).

**Ingredient Parser adapter (mandatory).**
- Disable the implicit water-density default.
- Never copy its `raw` retrieval hint into source-state fields.
- Treat BM25 scores as rankings, not probabilities [S21–S23].

### 9.2 Structural cases (illustrative manual cases, not Gold)

| Expression | Structure | Numeric policy |
|---|---|---|
| 2 × 200 g chicken breasts | 2 items × stated mass | 400 g total stated |
| 1 (400 g) can tomatoes, drained | package count + contents mass + drained qualifier | drained mass unknown unless supplied |
| 1½–2 cups water | exact rational range; culinary unit | keep interval; resolve cup convention separately |
| 3 cloves garlic | count + clove portion | grams need a portion record |
| 1 packed cup brown sugar | volume + packing | packed-sugar evidence, or mass unknown |
| 1 cup flour, sifted vs 1 cup sifted flour | measurement-vs-preparation order | keep scope; adjudicate |
| 1 katori dal | Indian household unit; variant size | interval, `unit_variant=katori(regional)` |
| salt to taste / a pinch | qualitative amount | no invented number; optional conventional range tagged `provenance=convention`, never in totals |
| oil for frying | purpose-linked open amount | used ≠ absorbed oil |
| 2 cups broth plus more as needed | fixed term + open term | open term stays symbolic |
| remaining batter | residual reference | compute only if prior allocations are supported |

### 9.3 Symbolic accounting

\[
Q_{after}=Q_{before}+Q_{added}-Q_{allocated}-Q_{discarded}+\Delta Q_{process}
\]

This is an accounting **contract**, not a claim that every term is known.
- Mass, volume, count, dry basis, edible basis and source-origin allocation are separate channels, never added without an evidenced conversion.
- **Worked example.** 200 g sauce → reserve half → use half of the reserve gives 100 g kept, 50 g used, 50 g still reserved. With **unknown** initial mass the ledger still answers "¼ of the original sauce" without inventing grams.

### 9.4 Conservation boundary and correlated uncertainty

- Conserve **known allocations** under split/merge. Do **not** require edible-mass conservation across evaporation, absorption, draining, peeling, frying or fermentation. An unknown $\Delta Q_{process}$ is a legitimate residual.
- Oil uptake, water uptake, retention and homogeneity need evidence or declared assumptions (DEL-1). Parent fractions in heterogeneous mixtures are not always proportional to mass.
- Keep `SOURCE_ORIGIN_ALLOCATION` distinct from measured final composition.
- Store uncertainty **once**, at the source variable. A split of Q gives children `0.5Q` that are **correlated**, so propagate with a dependency-aware interval or Monte Carlo. Parser, density and link uncertainty are separate terms.

---

## 10. Hidden processes, omitted arguments and earlier context

### 10.1 The prefix state packet

For every step *t*, the parser receives a compiled packet; it is not left to rely on raw long context, which is unreliable at depth [S16]. The packet contains:
- active entities and their producing events;
- location, product/form, reservation status and symbolic quantities of each entity;
- relevant prior spans;
- unresolved alternatives.

The current step is parsed against the packet, replayed into P7, and the whole graph is validated afterwards.

### 10.2 Four kinds of "implicit" (Report A), plus omitted-step rules (Report B)

| Case | Example | Policy |
|---|---|---|
| Linguistically omitted participant | "Simmer 10 minutes" after a single sauce exists | Resolve from the packet. Use most-recent compatible output as a baseline hypothesis informed by action-graph work [S39], not an unconditional semantic rule. Then a classifier over candidate nodes; Claude tiebreak only in the review band. Keep `provenance=inferred` with uncertainty. |
| Source-described prior preparation | Ingredient list "onion, chopped"; steps start with frying | Annotate the initial prepared form. **Do not** create an explicit chop event. |
| Structural intermediate | "Mix flour and water … knead it" | Create a mixture entity. Distinguish a structural output from an explicitly *named* "dough". |
| Unstated customary action/condition | Preheat, rinse, drain; a "standard" simmer temperature | **Remains unknown in the observed graph.** A rule may emit an `OMITTED_STEP_CANDIDATE` only when the prerequisite is absent **and** ≥ 1 retrieved training recipe states it explicitly. Store `rule_id` and `precedent_ids`. Never copy time, temperature, quantity or chemistry into source ledgers. |

### 10.3 Planned versus observed

Keep **PLANNED** (parsed procedure and intended endpoints) separate from **OBSERVED_SESSION** (user or sensor reports). For example, "it is still pale" updates the observed trajectory and leaves the expectation intact. "Bake until golden" is a *target* endpoint, not proof the dish became golden.

### 10.4 Offline and online tracks

- **Offline full-document:** later text may resolve earlier ambiguity, with the evidence span recorded.
- **Online prefix at step *t*:** only the prefix plus observations are available. Score it separately, and never let future-step evidence leak into it.

### 10.5 Missingness is not one null (four orthogonal axes)

| Axis | Values |
|---|---|
| Availability | PRESENT · NOT_STATED · NOT_MEASURED · BELOW_LOD · UNRESOLVED · NOT_APPLICABLE · CONFLICTING |
| Epistemic provenance | EXPLICIT_SOURCE · EXTERNAL_VERIFIED · DERIVED_DETERMINISTIC · INFERRED_LLM · MODEL_ESTIMATED · IMPUTED · SIMULATED · CONVENTION |
| Verification | UNREVIEWED · HUMAN_VERIFIED · DUAL_ADJUDICATED |
| Trajectory | PLANNED · OBSERVED_SESSION · PREDICTED |

A human can verify that an inference is *reasonable* without turning it into an explicit fact. A numeric zero requires evidence, and an absent concentration is not zero.

---

## 11. Referential structural similarity — the testable design

### 11.1 Three mechanisms (merged)

| Mechanism | Retrieved object | Use | Restriction |
|---|---|---|---|
| **Exemplar retrieval** | Labelled training phrases/steps, selected by (i) **SEFS entity-composition signature** [S1], (ii) BM25, (iii) dense similarity; plus a **kNN-NER token datastore** [S41] | P2 boundaries/attributes; event parsing; Claude-verifier demonstrations [S42] | Training/approved Gold-Light index only; no evaluated dev/calibration/test or derivative items |
| **Ontology retrieval** | Concept cards: labels, aliases, definitions, relations | P3 candidates and rerank | Valid IDs and compatible product/form only |
| **Antecedent retrieval** | Active entities plus their local graph history | P6: it/them/mixture/remaining/omitted arguments | Candidate must exist in this recipe/session and satisfy temporal constraints |

**Why signatures matter.** In RecipeDB, about 90% of 1.15M ingredient phrases fall into 91 entity-frequency vectors, while the remaining 10% need 1,976 [S1][V]. Structure therefore predicts head patterns well, and retrieval should matter most in the tail. **Always report gains per signature-frequency bucket.**

At inference, retrieval signatures must come from raw observable features or the current model's predictions. Gold entity-composition signatures are allowed for diagnostic bucket reporting or an explicitly labeled oracle, not for production retrieval or development/test exemplars. The datastore contains only approved training examples.

### 11.2 Antecedent scoring

\[
s(r,e)=f(\text{lexical},\ \text{contextual},\ \text{food compatibility},\ \text{role},\ \text{location},\ \text{state},\ \text{recency},\ \text{graph path},\ \text{allocation})
\]

Start with rules and a **small learned reranker**; no hand-set weights.

**Hard rejections:** entity not yet produced on the chosen branch, or material already discarded; reserved portion used without a supported reference or compatible allocation; double-spending a quantity.

**Soft scores:** food/form compatibility, role acceptance by the action, location match.

Source inconsistencies are recorded as **conflicts**, not "fixed".

### 11.3 Cross-recipe similarity is a proposal source only

ARA-style alignment [S9] can suggest missing rinse/rest/preheat steps. These become `OMITTED_STEP_CANDIDATE` items with exemplar IDs. Ask the user only when the answer would materially change the decision. **Counterfactual tests** independently swap verbs, forms, locations, fractions and recency; a resolver that just copies the nearest entity or template must fail them.

---

## 12. Is a recipe "good enough"? Task sufficiency (P9)

A recipe has no universal completeness score. Use a capability vector:

\[
c_r=(\text{food coverage},\ \text{quantity structure},\ \text{grounding},\ \text{event coverage},\ \text{reference closure},\ \text{condition support},\ \text{scientific support})
\]

| Requested task | Needs | Missing info that is acceptable |
|---|---|---|
| Ingredient/process retrieval | Reliable identity + source spans | Mass, chemistry |
| Follow procedure | Events + resolvable key participants | Exact grams |
| Scale a fixed stated amount | Valid quantity structure + unit meaning | Count→mass evidence |
| Portion fractions | Supported references + allocations | Absolute initial mass |
| Nutrients of the served dish | Composition links, amount basis, retained/discarded material, serving basis | Missing parts flagged or interval-bounded |
| Process-specific chemical change | Compatible measurements/models + conditions (DEL-1) | Generic steps are insufficient for numbers |
| Next-action advice | Planned vs observed state, goal, constraints, evidence | Qualitative advice or one clarification |

**Return value:** `READY` · `READY_WITH_LIMITS` · `NEEDS_CLARIFICATION` · `UNSUPPORTED` · `CONFLICTING`, plus the missing critical fields. This is the operational form of v14's sufficiency/abstention program and of DEL-4.

---

## 13. Sparsity: three different problems

| Sparsity | What is sparse | Response |
|---|---|---|
| **Annotation** | Rare labels, roles, regional aliases, flow patterns | Targeted Gold-Light, hierarchical metrics, task masks, active learning, valid augmentation |
| **Procedural omission** | Arguments, intermediate names, quantities, conditions | Candidate references, symbolic quantities, explicit unknowns, clarification |
| **Scientific measurement** | Food × form × process × condition × target | DEL-1 evidence acquisition; Level-15 completion under its own gates (DEL-2) |

**Rules.**
- Never fill a scientific gap by generating more recipe labels.
- Never use a scientific imputation model to decide whether a sentence stated a temperature.

**Per field, report:** source-present rate, attempted extraction rate, verified accuracy on present fields, unresolved rate and grounded rate.
- Report everything in **frequency buckets** (head / torso / tail / unseen, defined on training counts).
- Low grounding may reflect missing portion evidence, not poor NER.
- An unobserved intersection (ingredient × form × process × region) is not an invalid one.

**Silver** carries task masks and field weights. Unannotated spans or edges are never negatives without an exhaustive-annotation contract.

**Active learning** combines:
- uncertainty;
- model disagreement (CRF / encoder / GLiNER / Claude);
- rare SEFS signatures;
- UNKNOWN links;
- source/region diversity;
- expensive downstream errors.

A separate **random audit stream** keeps quality estimates unbiased. Active-learning picks never enter the sealed test.

**Synthetic data:** tagged, capped at ≤ 20% of training lines, never in dev/test/calibration, always ablated (Silver noise hurt in [S1]).

**Gazetteer expansion** draws on RecipeDB2 ingredient names, FlavorDB, FoodOn labels/synonyms, and reviewed Hinglish aliases, each with source and reviewer.

---

## 14. Thresholds and gates

### 14.1 Hard gates (always before confidence)

Route to review/reject when:
- an ID is invalid;
- a source span cannot be found;
- dimensions are incompatible;
- no portion/density route exists;
- an entity is used before it is produced;
- an allocation over-spends the known amount;
- an unsupported scientific value appears.

High confidence cannot bypass these, and schema validity does not prove correctness.

### 14.2 Calibrated selective policy

**Do not adopt RecipeDB2's raw cosine ≥ 0.70 as a correctness cutoff.** Cosine, token probability, reviewer agreement and P(correct link) are different quantities.

\[
\text{Coverage}_j(t)=\frac{N_{accepted}}{N_{eligible}},\qquad \text{Risk}_j(t)=\frac{N_{incorrect,\,accepted}}{N_{accepted}}
\]

Choose *t* on a **dedicated calibration partition**, with the error budget and minimum useful coverage fixed **before** looking. Test once on sealed data.

| Route | Initial error budget [P] | Initialisation prior (Report B), before calibration |
|---|---|---|
| Automatic food linking | accepted-link error ≤ 2% | accept band P ≥ 0.90; review 0.50–0.90 |
| Food-specific quantity grounding | wrong/unsupported route ≤ 1% | ingredient-specific density → accept; category density → review; none → mass = null |
| Cross-step reference/flow | wrong-link ≤ 5% | provenance stays `inferred` even when accepted |
| Span labels | report per label | p ≥ 0.90 and ≥ 2 sources agree → accept; 0.60–0.90 → review |
| Process mapping | report | exact/alias or P ≥ 0.85 → accept; else `UNMAPPED` with raw verb kept |
| Unseen concept / no candidate / conflict | review/unresolved by default | — |
| Scientific quantitative claims | evidence compatibility + Level-15 gates | no universal threshold |

### 14.3 How much calibration evidence is enough

- **Zero-error upper bound:** with zero observed errors the exact one-sided 95% bound is $p_{upper}=1-0.05^{1/n}$. That needs **n = 149** for < 2%, **299** for < 1% and **598** for < 0.5%. Decisions inside one recipe are **not independent**, so use recipe/source-clustered intervals.
- **Threshold search:** searching thresholds on the same data needs a simultaneous bound or a separate validation sample.
- **F1 uncertainty:** there is no universal instance count for an F1 interval. Estimate uncertainty from recipe/family-clustered resampling or a task-specific simulation; precision, recall, support, and clustering all matter.
- **Formal guarantees:** conformal risk control [S24] is an option only under matched assumptions, so start with the simple calibrate/validate route.

**Report:** risk–coverage curves, Brier/reliability, unsupported-conversion rate, erroneous-merge rate and review cost. Switch to conservative behaviour when drift is detected.

---

## 15. Models and tools to benchmark (merged roster)

| Candidate | Role | Limitation to measure |
|---|---|---|
| Deterministic quantity grammar + curated aliases | Fractions, ranges, units, known aliases, integrity | Ambiguous grammar; registry coverage |
| Stanford NER / CRF (reproduce 95.52) | Legacy baseline | Cross-source drop |
| spaCy-transformer (reproduce 95.90) | Legacy SOTA reproduction | No relations/coreference |
| Ingredient Parser + adapter | Ingredient-line and quantity baseline | Water-density default, `raw` hints |
| DeBERTa-v3 + CRF | Strong trained encoder | Data hunger on rare labels |
| **RecipeBERT-KA / RecipeRoBERTa-KA** [S31] | Current recipe-NER challenger | Ontology crosswalk; multi-pass cost |
| GLiNER2 / **GLiNER2.5** small·base·multi [S11][S12] | Zero-shot + fine-tuned schema extraction; joint relations and span attributes | Domain accuracy; cross-step references; product distinctions |
| GLiNER2.5-Decide [S13] | Review routing, label decisions | Local calibration |
| kNN-NER layer [S41] | Tail boost by retrieval | Datastore leakage control |
| FoodSEM [S3] | Food NEL baseline | Memorised IDs; ontology version |
| FoodOntoRAG-style linker [S4] | Retrieval-first NEL baseline | Retrieval recall; scorer calibration |
| One pinned frontier LLM (Claude via Max) | Silver teacher, hard-case comparator, verifier | Cost, fabrication, model drift, Gold anchoring |
| One local instruction model | Reproducible extraction / distillation comparator | VRAM, latency, valid-output rate |
| **Jev 1.13 (`jev-1.13.0`, TypeSafe AI)** [S59] | Closed-set **decision layer**: span-label verification, link selection, process/event typing, antecedent choice, routing, evidence reranking, answer guards | Domain calibration; English-first; literal-reading / counting / multi-hop / noisy-state weaknesses; proprietary early-access API |
| JEPA variants (Appendix A) | Auxiliary objectives / latent predictors | Only under J-gates |

**Pin** checkpoints, library versions, prompts, label descriptions and decoding settings. Test **label-description paraphrases**, because zero-shot wording changes extraction. Measure hardware on the machine you actually use, with no assumed GPU.

---

## 16. (reserved) — consistency index

Sections 1–15 define the semantic design; Appendices B–J provide the implementation, annotation, and evaluation contracts. §17 adds the Jev decision layer, §18 defines *how to test*, and §19–§20 define *when* and *what changes in the deliverables*. Appendix A keeps JEPA as an optional research track.

---


---

## 17. Jev (TypeSafe AI "System One" model) — scope in this project

### 17.1 What Jev is (verified)

| Property | Value | Source |
|---|---|---|
| Release | 15 September 2026, early access; TypeSafe AI's first "System One" model | [S61][S62] |
| Contract | Send a text **state** plus typed **questions** → get a typed answer per question, with a probability distribution, in one non-autoregressive pass. **No text generation.** | [S59][S61] |
| Primitives | **Choice** (unordered, up to 255 options); **Score** (ordered rubric of 2–10 levels; score = expectation over levels); **Noul** (probability that a statement is true) | [S61] |
| Guarantee | Cannot return a label outside the answer space, so no malformed JSON or invented labels. **It can still be confidently wrong.** | [S61] |
| Training | "RLCD" (Reinforcement Learning for Calibrated Decisions). **No customer fine-tuning or LoRA; the same weights serve every account.** You adapt it only through `state`, `instructions` and `criteria`. | [S59] |
| Price | **$0.042 per million input tokens; output tokens free** (not $0.0042) | [S59][V] |
| Limits | 64k tokens per request (32k for state + longest question). Rate limits currently 100K tokens/s and 40 requests/s, **"adjusting dynamically … can change without notice"** | [S59][V] |
| Language | English is primary; other languages are "handled but not equally well" | [S59][V] |
| Latency / cost claims | 70–500 ms; typically 40–200× faster; one upper-end example of 193.6× faster and 444.6× cheaper. **All vendor-reported.** | [S61] |
| Confidence | **Choice** confidence = $(n\,p_{max}-1)/(n-1)$. **Score has a different formula; Noul has no separate confidence field.** It ignores how the remaining probability is spread, so the vendor recommends using margin or entropy from the full distribution when that matters | [S61] |
| Documented failure modes (v1.13) | Literal reading of scope words and negation; counting and arithmetic; dates; indirection and multi-hop reasoning; accuracy drop with large, noisy state; steerable by adversarial text in the state | [S60][S61] |
| Data | Not trained on customer requests; zero data retention only for enterprise | [S59][V] |

### 17.2 Why it matters here

Most of what the compiler does after P1 is a **closed-answer-space decision**:
- which label this span has;
- which of 20 candidate foods it is;
- whether it is a product or a modifier;
- which process family applies;
- which active entity "it" refers to;
- whether this evidence row is relevant and condition-compatible;
- whether this answer claim is supported.

Today, Report A and Report B both route the hard cases of these decisions to an LLM (Claude) that must *generate* a choice as text. Jev is built for exactly this shape of problem. It does not generate arbitrary span boundaries, compute quantities reliably, or write free-text answers; it can select a pre-enumerated span candidate, so it **complements** rather than replaces the other components.

**Three-tier stack (adopted as a hypothesis):**
1. **Deterministic code:** offsets, quantity grammar, conversions, allocations, invariants, numeric checks.
2. **System One decisions (Jev, or an open alternative):** closed-set choices with distributions → **our calibrator** → risk-budget routing (§14).
3. **LLM (Claude):** generation only — structured extraction of hard steps, review-band adjudication, explanations and final answer verbalisation.

### 17.3 Fit by pipeline stage

| Stage | Decision | Primitive | Fit | Notes |
|---|---|---|---|---|
| P2 | Verify the label of a **candidate** span proposed by gazetteer/encoder (incl. `NOT_A_SPAN`) | Choice | **Med–High** | Replaces the Claude verifier on low-confidence spans; Jev cannot produce offsets itself |
| P2 | Attribute disambiguation (FORM vs PREP_STATE vs TEMP; "hot" = temperature or pungency) | Choice | **High** | Put boundary cases in `criteria` |
| P3 | Select among top-K concept cards (+ `NO_VALID_CANDIDATE`, `AMBIGUOUS`) | Choice (two-stage Noul → Choice for large K) | **High** | Structured criteria: label, aliases, definition, relations |
| P3 | Vocabulary lifecycle: ALIAS / MODIFIER_COMPOSITION / PRODUCT_CONCEPT / AMBIGUOUS / NON_FOOD | Choice | **High** | Feeds §5.4 review queue |
| P3 | Locale-conditioned aliases (corn flour, coriander leaf vs seed, jeera/dhaniya) | Choice | **Medium** | English-first: pass transliteration plus an English gloss; evaluate S4 separately |
| P4 | Quantity *kind* (exact / range / count / package / qualitative / open) and unit convention (US cup / metric cup / regional katori) | Choice | **Low–Med** | **Never** arithmetic, counting or conversion (documented weakness) |
| P5 | Process mapping: family Choice, then specific Choice (RecipeDB's 268 processes exceed the 255-option limit, so split by family) | Choice ×2 | **High** | |
| P5 | Heat level (low / medium / high), endpoint type, event type (TRANSFORM / MERGE / SPLIT / RESERVE / …) | Score / Choice | **High** | |
| P6 | Antecedent selection over active entities in the prefix packet (+ `NEW_ENTITY`, `UNRESOLVED`) | Choice | **Medium** | Indirection and multi-hop weaknesses, so test long-distance references (E4.4) |
| P7 | Flow operation type; "this step retrieves a reserved portion" | Choice / Noul | **Med–High** | |
| §10 | Score an omitted-step **candidate** ("step presupposes a preheated oven not stated") | Noul | **Medium** | Candidates only, precedent still required |
| P9 / DEL-4 | Relevance gate (process-sensitive?), task-type router (8 types), evidence-row relevance and condition compatibility, contradiction, injection | Noul / Choice | **High** | Matches the vendor's passage-classification and re-ranking patterns |
| DEL-5 | Per-claim grounding guard ("claim supported by packet row X?") | Noul | **Med–High** | Numbers are checked deterministically, not by Jev |
| Annotation ops | Pre-labels for categorical fields (Gold-Light, assistance logged), disagreement signal for active learning, Silver categorical fields | All | **High** | **Never** the sole source of Gold |
| DEL-1 | Pre-classify literature rows (process family, study type, evidence-tier hint) for human verification | Choice | **Medium** | Humans verify |
| DEL-2, quantity arithmetic, unit conversion, chemistry values | — | — | **None** | Deterministic code and evidence only |

### 17.4 Cost and throughput at our scale (official pricing, $0.042/Mtok input)

| Workload | Tokens (estimate) | Cost | Time at 40 req/s |
|---|---|---|---|
| One linking call (line + context ≈ 150 tok + 20 concept cards ≈ 800 tok) | ≈ 1,000 | ≈ $0.000042 | — |
| G-1 seed + sealed test (200 recipes × 12 mentions, ×5 questions via fan-out) | ≈ 3M | ≈ $0.13 | minutes |
| 10k Silver × 12 mentions (linking) | ≈ 120M | ≈ $5 | ≈ 50 min |
| 100k Silver × 12 mentions (linking) | ≈ 1.2B | ≈ $50 | ≈ 8.3 h |

Extra questions on the same state ("fan-out") add only a few dozen tokens each, so link + attribute + process + qualifier questions can share one call.

**Caveats:**
- Rate limits are dynamic, and access may be waitlisted.
- These are planning estimates. Log real usage in E14.1.

### 17.5 Rules for using Jev scientifically

1. **Pin `jev-1.13.0`** (never `jev-latest`) and log the answering model ID per decision. Re-validate thresholds when you move versions.
2. **Recalibrate on our calibration partition.** Vendor calibration is general, not on our distribution. Features: $p_{max}$, top-2 margin, entropy, number of options, frequency bucket, S4/Hinglish flag → isotonic/logistic calibrator. Report ECE before and after.
3. Route by **our risk budgets** (§14.2), not the vendor's example 0.5 / 0.9 thresholds.
4. Always include `NO_VALID_CANDIDATE`, `UNRESOLVED` or `OTHER` options, so it is never forced onto the nearest wrong answer.
5. Keep the state **small and relevant**: send the prefix state packet, not the whole recipe (accuracy falls with noisy state).
6. **Decompose:** one atomic question per decision, combined in code.
7. Treat recipe text as **untrusted state**, especially user-supplied recipes in DEL-5.
8. **Hinglish / Devanagari:** add transliteration and an English gloss; report S4 separately.
9. **Reproducibility.** Jev is a proprietary hosted model that graders may not be able to call, so:
   - pair every Jev result with an **open baseline** (GLiNER2.5-Decide, cross-encoder, logistic over features) behind the same interface;
   - cache and release request/response logs where licences permit.
10. **Data permissions:** check recipe-source licences before sending text to a third-party API.
11. **Never Gold, never arithmetic, never chemistry values.**

### 17.6 Verdict

Jev is a **high-value, very low-cost candidate for the decision layer**. It fits P3 selection, P5 process typing, P9 routing, evidence reranking, answer guards and annotation operations, and it could cut the Claude Max load substantially.

It is **unproven on our domain**: it is two weeks old, its benchmarks are vendor-reported, it cannot be fine-tuned, and it is English-first. Adopt it **only through E14**, always against open baselines and after our own recalibration.

If Jev access is unavailable, prepare an access request for review and continue with the open selector. No external message is sent as part of this document task.

### 17.7 Jev over the three ledgers — "pick, don't generate" (new in v1.2)

The rule: **candidates come from our ledgers and registries, Jev picks among them, and deterministic code writes the result.** Every question carries an escape option (`NONE_OF_THESE` / `UNRESOLVED` / `NEW_ENTITY`), and every answer is recalibrated (§17.5) before routing.

#### 17.7.1 Ingredient / entity ledger

| Decision | State sent | Question (type → answer space) |
|---|---|---|
| **Instruction mention → ingredient-list line** (missing from RecipeDB3) | Current step + the active-lot table (line id, surface name, canonical id, status) | Choice over active lot IDs + `INTERMEDIATE` + `NOT_IN_LIST` + `UNRESOLVED` |
| Same lot or a second addition ("2 tbsp butter … remaining butter") | Both mentions + allocation history | Noul "same physical lot" |
| Mention refers to an intermediate ("the batter") | Packet of intermediates (id, producing event, parents) | Choice over intermediate IDs + `NEW_INTERMEDIATE` |
| Lifecycle after the step | Step + entity row | Choice {ACTIVE, RESERVED, INCORPORATED, DISCARDED, SERVED} |

#### 17.7.2 Canonical-form ledger (concept + facets)

| Decision | State sent | Question |
|---|---|---|
| Concept choice | Mention in context + top-K concept cards (label, aliases, definition, locale) | Choice over K + `NO_VALID_CANDIDATE` + `AMBIGUOUS` |
| Product vs modifier ("tomato paste" vs "tomato, chopped") | Mention + base-concept card | Choice {ALIAS, MODIFIER_COMPOSITION, PRODUCT_CONCEPT, AMBIGUOUS, NON_FOOD} |
| Facet: form | Mention | Choice over a closed form vocabulary (whole, sliced, diced, minced, ground, grated, paste, purée, powder, juice, zest, … `UNSTATED`) |
| Facet: size / dry-fresh / temperature-state / packing | Mention | Choice per facet with `UNSTATED` |
| Locale sense (coriander leaf/seed; corn flour = maize flour or cornstarch) | Mention + recipe region + co-ingredients | Choice over senses + `AMBIGUOUS` |

Facets are separate questions in **one fan-out call**, so all of them cost about one state read.

#### 17.7.3 Quantity ledger

| Decision | State sent | Question | Arithmetic |
|---|---|---|---|
| Quantity **kind** | Raw quantity text | Choice {EXACT, RANGE, COUNT, PACKAGE, QUALITATIVE, OPEN_PLUS, UNSTATED} | none |
| Unit convention | Unit token + recipe locale/source | Choice {US_CUP, METRIC_CUP, IMPERIAL, KATORI_REGIONAL, UNKNOWN} | none |
| **Pick a portion/density record** (closing the RecipeDB2 coverage gap) | Mention (food, form, size, packing) + candidate records retrieved from FDC portion descriptions / our portion table (e.g., "1 cup, chopped", "1 medium", "1 cup, packed") | Choice over records + `NO_COMPATIBLE_RECORD`; plus Noul per record "compatible with form and packing" | **Code** computes grams with the record's interval |
| Instruction quantity → ledger row ("add half of the butter") | Step + quantity rows of active lots | Choice over quantity rows + `UNRESOLVED` | **Code** computes 0.5·Q symbolically |
| Fraction basis ("half" by mass, volume or count?) | Step + row dimensions | Choice {MASS, VOLUME, COUNT, PORTION_FRACTION_ONLY} | code |
| "Remaining" / "reserved" resolution | Allocation history | Choice over open allocations + `UNRESOLVED` | code |

**Hard boundary (vendor-documented weakness).** Jev never counts, sums, converts or compares numbers. It only **picks which record or row applies**, and the ledger arithmetic is deterministic and replayable.

#### 17.7.4 Example request (illustrative)

```json
{
  "model": "jev-1.13.0",
  "state": {
    "step": "Stir in half of the butter and cook until the onions soften.",
    "active_lots": [
      {"id": "L3", "surface": "4 tbsp unsalted butter, divided", "canonical": "butter"},
      {"id": "L5", "surface": "2 large onions, thinly sliced", "canonical": "onion"}
    ]
  },
  "questions": {
    "butter_ref": {"type": "choice", "instructions": "Which ingredient-list lot does 'butter' in the step refer to?",
                   "criteria": {"L3": "4 tbsp unsalted butter, divided", "NOT_IN_LIST": "not in the ingredient list", "UNRESOLVED": "cannot tell"}},
    "fraction_basis": {"type": "choice", "instructions": "What does 'half' measure?",
                       "criteria": {"VOLUME": "half of the stated tablespoon volume", "PORTION_FRACTION_ONLY": "half of whatever amount, basis unclear"}},
    "onion_state_goal": {"type": "choice", "instructions": "Target state for the onions in this step",
                         "criteria": {"SOFTENED": "soft", "BROWNED": "browned", "UNSTATED": "no target stated"}}
  }
}
```

Code then writes: `allocation(L3, 0.5, basis=VOLUME) → 2 tbsp`, `event(STIR_IN, inputs=[L3@0.5])`, `PLANNED endpoint(onion = SOFTENED)`. Each written value carries Jev's distribution, our calibrated probability, and the route (accept / review / unresolved).

---

## 18. Experiment program — main experiments and sub-experiments

**Format.** Every sub-experiment states its comparison, data and metric. "Win" criteria are pre-registered **before** running anything.

**Shared rules for every experiment:**
- Recipe/family-clustered paired bootstrap.
- Multiple seeds where training is involved.
- Assistance disclosed.
- No tuning on the sealed test.

### E0 — Annotation reliability (prerequisite)

| Sub | Comparison | Data | Metric | Exit |
|---|---|---|---|---|
| E0.1 | Two annotators, all layers, no LLM | G-0 pilot (20) | span-F1, edge-F1, κ per layer; minutes/recipe per depth | Throughput known; manual v1.1 |
| E0.2 | INCEpTION vs Label Studio | same 20 | time/recipe, supported operations, error rate | Tool chosen |
| E0.3 | Claude pre-fill vs none (Gold-Light only) | 20 seed recipes | per-label Claude precision/recall; time saved; anchoring check | Per-label human-first list (precision < 0.85) |

### E1 — Legacy NER reproduction and extension

| Sub | Comparison | Data | Metric | Win criterion |
|---|---|---|---|---|
| E1.1 | Reproduce CRF (95.52) and spaCy-trf (95.90) | CoSyLab 6,611/2,187 split | lab macro-F1 + standard strict span micro/macro F1 | matched scorer behavior and a predeclared reproduction tolerance; published CIs may be unavailable |
| E1.2 | Cross-source (AllRecipes ↔ Food.com) | version-matched source partitions where available | strict F1 | compare with a rerun baseline; 0.8672 is historical context unless scorer/data match |
| E1.3 | DeBERTa-CRF; RecipeBERT-KA/RoBERTa-KA; GLiNER2.5 zero-shot + fine-tuned | same + TASTEset v1/v2 (5-fold, seed 42) | per-label F1 (TEMP, DF focus) | rare-label gain with CI |
| E1.4 | + kNN-NER; + SEFS-exemplar Claude verifier on p < 0.9 | same | F1 per **signature-frequency bucket**; cost/1k lines | tail-bucket gain |
| E1.5 | Unverified Silver vs verified Silver vs none | same | macro-F1 | determine whether verified Silver helps (unverified hurt in [S1]) |
| E1.6 | Teacher-lineage/contamination audit | released data | duplicate/derivative overlap | documented before any claim |
| E1.7 | Instruction NER (process/tool/duration/endpoint) | 2020 instruction set (requested) else our sealed A3; ReciFineGold; r-FG | strict span-F1 | beat 0.88/0.90 on a matched set, else report on our set and say so |
| E1.8 | Robustness: position shuffle (SINERA), Hinglish/Devanagari, unit-format variants | challenge sets | F1 drop | report degradation |
| E1.9 | **Reproduce RecipeDB3** ingredient DeBERTa (0.9557) and instruction spaCy (0.9258 / 0.8698), then re-evaluate under hygiene: dev-set checkpointing, augmentation-family-grouped and number-masked-dedup splits, SIZE included (§1.2 M1–M2) | RecipeDB3 repo [S64] | macro/micro seqeval F1, per label | reproduction within a predeclared tolerance, interpreted with scorer equivalence and seed variation; grouped-split numbers for both systems |
| E1.10 | **Instruction weak labels** (QUANTITY 0.638, PREPROCESS 0.50, DRYFRESH 0.83, TEMPERATURE 0.88): quantity grammar + kNN/GLiNER2.5 + Jev verification | their split + our 200-instruction span re-annotation | per-label F1 with CIs | QUANTITY ≥ 0.85; significant gains elsewhere |

### E2 — Canonical factorisation

| Sub | Comparison | Metric |
|---|---|---|
| E2.1 | Whole-string linking vs concept + facets | Acc@1, fragmentation, wrong merges |
| E2.2 | Product-boundary challenge set (sour cream, tomato paste, coriander leaf/seed, corn flour locale, garlic powder) | boundary accuracy |
| E2.3 | Hinglish alias coverage (S4) | coverage, precision of alias resolution |

### E3 — Food linking (NEL)

| Sub | Comparison | Metric | Note |
|---|---|---|---|
| E3.1 | Lexical / dense / hybrid candidate generators | **Recall@K** (separate from selector accuracy) | No selector can fix a missing candidate |
| E3.2 | Cross-encoder vs FoodSEM vs FoodOntoRAG-style vs Claude selector | Acc@1, ACCEPT-band precision, coverage | |
| E3.3 | Reproduce RecipeDB2 top-200 (79.50% acc, Jaccard 25.50) → calibrated policy | accuracy; risk–coverage vs raw cosine 0.70 | Same candidate universe |
| E3.4 | Tail / unseen / regional / source-held-out | per-bucket precision and coverage | the cited top-200 result does not establish tail performance |

### E4 — Reference resolution with state packets

| Sub | Comparison | Metric |
|---|---|---|
| E4.1 | Recency + lexical resolver | explicit and implicit coreference accuracy |
| E4.2 | Contextual encoder / LLM, same candidates | same |
| E4.3 | + prefix state packet + temporal/type constraints | same; long-distance stratified |
| E4.4 | Long-distance references (> 3 steps back) | accuracy by distance bin |
| E4.5 | Online-prefix vs offline-full-document tracks | accuracy; leakage check |

### E5 — Structural similarity

| Sub | Comparison | Metric |
|---|---|---|
| E5.1 | E4.3 + role/path/allocation features | wrong-antecedent rate; merge/split edge F1 |
| E5.2 | + training-only structural exemplars (ARA-style) | same + cost |
| E5.3 | Counterfactual swaps (verb/form/location/fraction/recency) | pass rate — a template-copier must fail |
| E5.4 | Rule signatures vs graph kernel vs learned graph encoder | added only if E5.1 shows remaining structural errors |

### E6 — Quantity ledger

| Sub | Comparison | Metric | Win criterion |
|---|---|---|---|
| E6.1 | Grammar vs Ingredient Parser (+adapter) vs LLM on the structural challenge set (§9.2) | structure exact match; unit validity | |
| E6.2 | Conversion-route correctness (USDA portions; JFC-style weight table) | correct route %; near machine-precision tolerance for exact conversions; empirical error and interval coverage for food-specific estimates; interval coverage | |
| E6.3 | Allocation (reserve/split/remaining/recombine) | allocation accuracy; residual correctness | |
| E6.4 | Invented-grams audit (parser default vs adapter) | count of unsupported grams | **must be 0 for adapter** |
| E6.5 | Indian measures (katori, regional cup/tbsp) | interval coverage; variant tagging | |
| E6.6 | Correlated vs independent uncertainty propagation | interval calibration on synthetic splits | |
| E6.7 | **Grounded-quantity coverage, with a matched RecipeDB2 comparison only if its pair set is available (reported 43.90%)** and vs the Nutritional-Estimation baseline (NER + Jaccard + unit mapping) [S66] | same frequent ingredient–unit pairs | coverage at ≤ 1% wrong-route rate; invented grams | coverage > 43.90% with zero invented grams |

### E7 — Silver pipeline economics

| Sub | Comparison | Metric |
|---|---|---|
| E7.1 | One-pass LLM extraction | Gold accuracy; accepted-record cost; review minutes |
| E7.2 | Staged packets (§7.6) | same |
| E7.3 | Small-model cascade (GLiNER2.5-small/base → LLM only on low confidence) | same + latency |
| E7.4 | Rule-hybrid | same |
| E7.5 | ReciFine Silver reuse vs own Silver | same; overlap audit |

### E8 — How much Silver helps

1k → 10k → 25k → 60k, and 100k only if the marginal Gold gain justifies it. Measure on the same fixed Gold, plus rare-label and source-shift performance and marginal cost.

### E9 — Confidence routes

| Sub | Comparison | Metric |
|---|---|---|
| E9.1 | Raw scores (cosine, token p) vs calibrated policy | risk–coverage, ECE/Brier |
| E9.2 | Achievable coverage at budgets 2% / 1% / 5% | coverage at fixed risk |
| E9.3 | Clustered vs naive intervals | interval width honesty |
| E9.4 | Drift-triggered conservative mode | error under source shift |

### E10 — Does the compiler improve RAG? (links to the proposal's B0–B5)

| Sub | Comparison | Metric |
|---|---|---|
| E10.1 | Strong hybrid RAG vs the **same** retriever/generator + state/ledger packet | supported-answer rate; quantity errors; reference errors |
| E10.2 | B0 LLM-only → B5 state plus evidence compatibility/conflict packet | task utility at matched coverage |
| E10.3 | One-at-a-time ablations (−state, −ledger, −linking, −abstention) | Δ utility |
| E10.4 | Oracle cascade: gold state → retrieval | upper bound |

### E11 — Provenance gates versus invented science

| Sub | Comparison | Metric |
|---|---|---|
| E11.1 | Missing/conflicting-condition challenge set, with and without gates | unsupported numeric claims |
| E11.2 | Correct unknowns | precision of `UNSUPPORTED/CONFLICTING` |
| E11.3 | Justified abstention | risk–coverage at fixed utility |

### E12 — Ontology drift

| Sub | Comparison | Metric |
|---|---|---|
| E12.1 | Frozen vs updated FoodOn snapshot, internal IDs pinned | obsolete-ID errors; correct new links |
| E12.2 | New aliases/products injected | re-annotation cost |

### E13 — Omitted steps (new; pairs with J3)

| Sub | Comparison | Metric |
|---|---|---|
| E13.1 | Rule + precedent vs LLM-only proposals | candidate precision/recall vs gold "missing prerequisite" |
| E13.2 | + JEPA surprise (J3) or perplexity | precision@k at matched recall |
| E13.3 | Hallucinated-step audit | % judged wrong (target precision ≥ 0.90 at achievable recall) |

### E14 — Jev decision layer (TypeSafe System One)

**Gate.** E14 runs only after:
- E3.1 exists (so every selector sees the **same candidates**);
- the calibration partition is frozen;
- the Jev API key is granted.

Every row is compared with at least one **open** baseline behind the same interface.

| Sub | Comparison | Data | Metric | Win criterion |
|---|---|---|---|---|
| E14.1 | Harness: pinned `jev-1.13.0`, request/response cache, token & cost meter, latency log; open baseline (GLiNER2.5-Decide / cross-encoder / logistic) on the same interface | pilot | valid-response rate, cost/1k decisions, p50/p95 latency | harness reproducible from the cache |
| E14.2 | **P3 link selector**: Jev Choice vs cross-encoder vs FoodSEM vs FoodOntoRAG-style vs Claude selector, same top-K | G-1 links, tail buckets | Acc@1; ACCEPT-band precision at the 2% risk budget; coverage; cost; latency | ≥ cross-encoder coverage at equal risk and lower cost |
| E14.3 | **Calibration**: raw Jev distribution vs vendor confidence vs margin/entropy vs our recalibrator | calibration partition | ECE, Brier, risk–coverage per frequency bucket and S4 | recalibrated ECE ≤ open baseline |
| E14.4 | **P2 span-label verifier** on low-confidence spans: Jev vs Claude verifier vs none | E1.4 setting | per-label F1 gain, cost per corrected span | gain ≥ Claude verifier at lower cost |
| E14.5 | **Product/modifier/vocabulary lifecycle** classification | E2.2 challenge set | boundary accuracy; wrong-merge rate | ≥ open baseline |
| E14.6 | **P5 process mapping** (two-stage family → specific) and heat/endpoint/event typing | G-1 A3 events | accuracy; UNMAPPED precision | ≥ embedding + cross-encoder |
| E14.7 | **P6 antecedent choice** over prefix-packet entities vs E4.3 resolver | G-1 A4 | accuracy by distance bin; negation/indirection subset | non-inferior overall; report long-distance |
| E14.8 | **Silver cascade economics**: encoder → Jev verify → Claude only in the review band, vs E7.2 staged LLM | 1k → 10k Silver | Gold accuracy on audit; cost per accepted record; review minutes | lower cost at equal audited accuracy |
| E14.9 | **RAG decision layer**: relevance gate, task router, evidence relevance/compatibility reranker, contradiction and injection Nouls | DEL-4/5 benchmark | Recall@K after rerank; unsupported-claim rate; added latency | better supported-answer rate at matched coverage |
| E14.10 | **Answer grounding guard** (per-claim Noul) vs LLM-judge vs none | E11 challenge set | unsupported-claim catch rate; false-alarm rate | higher catch rate at ≤ equal false alarms |
| E14.11 | **Robustness (vendor-documented jaggedness)**: negation ("do not drain"), scope words, Hinglish/Devanagari, long/noisy state, adversarial recipe text | challenge sets | accuracy drop vs clean | documented; drives the routing rules |
| E14.12 | **Reproducibility and drift**: repeated identical calls; version-pin vs alias; re-run on a new release | fixed probe set | answer agreement; threshold stability | thresholds re-validated before any version move |
| E14.13 | **Instruction mention → ingredient-ledger alignment** (§17.7.1) vs string match vs embedding nearest vs E4.3 resolver | G-1 A4 recipes + RecipeDB3 instructions (re-annotated subset) | alignment accuracy; `NOT_IN_LIST` precision | new capability; ≥ embedding baseline |
| E14.14 | **Portion/density record selection** (§17.7.3) vs lexical match of FDC portion descriptions | quantity challenge set + frequent pairs | correct-record rate; coverage at ≤ 1% wrong-route | feeds E6.7 |
| E14.15 | **Facet fan-out** (form/size/dry-fresh/temperature/packing + product-vs-modifier in one call) vs separate classifiers | G-1 A2 | per-facet accuracy; tokens per mention | equal accuracy at lower cost |

### Oracle studies (run before adding complexity)

- Gold spans → predicted links.
- Gold links → predicted references.
- Gold events → predicted ledger.
- Gold state → retrieval/answers.

Report the **oracle-vs-predicted gap per stage**. It shows the real bottleneck.

### Evaluation rules (merged)

- Group splits by recipe/source/dish/near-duplicate family **before** augmentation and indexing.
- Offline and online tracks are separate.
- Natural and challenge results are reported separately.
- Report full support counts, per label / source / region / frequency bucket.
- For links, report candidate Recall@K separately from selector accuracy.
- For graphs, align nodes under a declared policy before scoring typed edges. Canonical IDs alone cannot tell two onion lots apart.
- For quantities, report structure / route / tolerance / interval coverage separately.
- Compare selective systems at **matched useful coverage**. Abstaining on everything is not a result.
- Use the strongest relevant baseline, not a weak generic RAG.
- If sealed labels influence a fix, version a new evaluation set.

### Novelty boundary

Ingredient NER, food linking, recipe graphs, RAG and abstention each have prior work [S34 included]. The contribution must come from a specific dataset, the quantity-lineage representation, the sparse-evidence policy, a validated integration, or a measured improvement. **Run the final novelty audit before writing "first".**

---

## 19. Execution — work packages and a 12-week mapping (owner-agnostic)

### 19.1 Work packages and exit gates

| Package | Deliverable | Exit gate |
|---|---|---|
| **W0** | Source/rights manifest, duplicate families, task definitions, API audit (CoSyLab/Foodoscope, once granted) | Every pilot record has a source and a split family |
| **W1** | Manual v0; span/offset conventions; concept/product rules; three-ledger schemas; legacy adapters | 20 hard recipes representable with no ad-hoc fields |
| **W2** | G-0 pilot + E0; then G-1 seed (100 at A2, 40 at A4) | Disagreements understood; throughput measured |
| **W3** | Quantity grammar; curated alias/link baseline; Ingredient Parser adapter | §9.2 cases keep unknowns and evidence routes; E6.4 = 0 |
| **W4** | Baseline harness: CRF / spaCy-trf / DeBERTa / KA / GLiNER2.5 / pinned LLM; common scorer | E1.1 reproduced; costs logged |
| **W5** | Event/reference parser, prefix packets, entity versioning, symbolic ledger, replay | Reserve/split/discard and unresolved cases pass CI invariants |
| **W6** | Sealed test G-2 + calibration policy | Risk–coverage and subgroup support documented |
| **W7** | 10k Silver pilot + random and targeted audits (incl. ReciFine reuse decision) | Quality, concept growth and review cost acceptable |
| **W8** | 25k → 60k (100k optional) with Gold-Light active learning | E8 marginal gain > cost; no evidence fabrication |
| **W9** | State/quantity/evidence packet into RAG; B0–B5; demo | E10 better at matched coverage/cost |
| **W10** | Process-effect service (DEL-1 join) and FlavorTwin conditioning | Requires passed Level-12–15 execution gates |
| **WV** | Jev decision layer E14 (parallel; needs API access) | E14 gate satisfied; open baseline on the same interface |
| **WJ** | JEPA track J1–J3 (Appendix A; parallel, ≤ 10%) | J-gate satisfied |

### 19.2 Twelve-week mapping for the mini-project (two parallel tracks)

| Week | Track A — data, annotation, ledgers | Track B — models, evaluation, RAG |
|---|---|---|
| 1 | W0 manifest + families; manual v0; tool pilot setup; **apply for Jev early access** | E1.1 reproduction; common scorer; legacy adapters |
| 2 | G-0 pilot (20) + E0.1–E0.3 | E1.2–E1.3 baselines; GLiNER2.5 zero-shot |
| 3 | Manual v1.1; G-1 seed annotation begins | Quantity grammar + Ingredient Parser adapter (W3); E6.1, E6.4 |
| 4 | G-1 seed (A2) continues; alias tables incl. Hinglish | Linking cascade (E3.1–E3.3); **E14.1 Jev harness + open baseline** |
| 5 | G-1: 40 recipes to A4 (events, references, allocations) | kNN-NER + exemplar verifier (E1.4); calibration (E9.1); **E14.2–E14.4** |
| 6 | G-2 sealed test annotation (double, no LLM) | Event parser + prefix packets (E4.1–E4.3); **E14.5–E14.6** |
| 7 | G-2 continues; adjudication | Entity versioning + symbolic ledger + replay (W5); E6.2–E6.3 |
| 8 | Silver 10k pilot + audits (E7, ReciFine decision); **E14.8 Jev Silver cascade** | E5 structural similarity; E13 omitted steps; **E14.7** |
| 9 | Ledger release v1 (hash); data card | Task-sufficiency vector (P9); E9.2–E9.4 |
| 10 | Robustness challenge sets (S4/S5, Hinglish); **E14.11** | RAG integration B0–B5 (E10.1–E10.3); E11; **E14.9–E14.10** |
| 11 | Error analysis; oracle studies; **E14.12** | Ablations; optional J2/J3 (Appendix A) if the J-gate passed |
| 12 | Report + data card + release | Demo (8 scenarios) + report |

**Overlap guard (Assignment 1 = scraping + NLP/NER).** Keep P2 NER at about 15% of effort and frame it as "reproduced baseline + retrieval-augmented hybrid". The headline work is P3–P9: canonicalisation with an UNKNOWN band, quantity ledger, events/references, entity flow, sufficiency and gates. State this boundary in the report.

---

## 20. Affected plan — what changes in the mini-project deliverables, and their sub-experiments

| Deliverable (as submitted) | What changes | Sub-experiments | Minimum viable | Stretch |
|---|---|---|---|---|
| **DEL-1 Process-Effect Evidence Ledger** | Becomes the **P10 scientific evidence registry**, a separate plane. Rows join the compiler through canonical food/process IDs (P3/P5), never through recipe text. A5 depth is defined by it. | DEL-1.a coverage/sparsity audit; DEL-1.b canonical-ID join accuracy using the E3 linker; DEL-1.c E11.1 challenge (conditions missing/conflicting) | ≥ 1,000 public rows + ≥ 40 verified; joins via IDs | A5 links for anchor ingredients |
| **DEL-2 Sparsity-aware completion + cold-split benchmark** | Scope is the **scientific-measurement sparsity** only (§13). Annotation sparsity and procedural omission are handled elsewhere. No recipe-label generation for science gaps. | DEL-2.a density/MNAR profile; DEL-2.b pair-holdout / study-disjoint baselines; DEL-2.c completion vs LightGBM with propensity weighting; DEL-2.d conformal coverage | Baselines + one completion model + CIs | Var-T-JEPA / T-JEPA comparison (research only) |
| **DEL-3 State-tracking engine** | Now = **compiler core P4–P8** on top of P2–P3: three identities, event parser, prefix packets, references, entity versions, symbolic quantity accounting, planned vs observed | E4.1–E4.5, E5.1–E5.3, E6.1–E6.6, E13.1–E13.3, oracle studies; optional J3 | 40 A4 recipes + 30 scripted sessions; replay + allocation pass; invented grams = 0 | J3 surprise detector; E5.4 graph encoder |
| **DEL-4 Evidence-aware retrieval + calibrated abstention** | Adds the **task-sufficiency vector (P9)** and empirically evaluated risk-budget targets; retrieval keys use canonical IDs, process IDs and state fields; unknown = neutral | E3.2–E3.4 (keys), E9.1–E9.4, E11.2–E11.3 | Risk–coverage curves; 2%/5% target budgets, observed risk, uncertainty, and achieved coverage; no guarantee when support is inadequate | GLiNER2.5-Decide routing comparison |
| **DEL-5 End-to-end CulinaryState-RAG + benchmark + demo** | Uses compiler packets; B0–B5 ladder fixed; planned/observed trajectories in sessions; online-prefix track for live advice | E10.1–E10.4, E11.1, E1.8 robustness; human/chef review | ~80 questions × 8 task types; matched-coverage comparison; demo | J2 event-parsing gain feeding the demo; Level-17 J5 noted as future |

**Jev's effect on the deliverables (if access is granted and E14 passes):**
- **DEL-3:** P5 process typing, P6 antecedent choice and P7 operation typing run as Jev decisions plus our calibrator. The open baseline stays as fallback (E14.6–E14.7).
- **DEL-4:** relevance gate, evidence reranker, condition-compatibility and contradiction checks become Jev decisions feeding the risk–coverage router (E14.2, E14.3, E14.9).
- **DEL-5:** task router and per-claim grounding guard (E14.9–E14.10), with latency inside an interactive loop.
- **Annotation ops:** Jev pre-labels categorical fields and supplies disagreement signals for active learning. The Silver cascade (E14.8) should cut Claude Max load.
- **DEL-1:** pre-classifies literature rows for human verification.
- **DEL-2:** unchanged.

If access is **not** granted, the same decision interface runs on GLiNER2.5-Decide / cross-encoder / logistic baselines and nothing else in the plan changes.

**What gets cut first if time runs short:**
1. E8 beyond 10k Silver.
2. E5.4.
3. All J-experiments (Appendix A).
4. E12 and E14.12.
5. The stretch annotation to 300 recipes.

**Protect the core:** E0, one accessible matched NER baseline, E3.1, E4.3, E6.4, E9.1, E10.1, E11.1. E1.1 and E3.3 are reproduction priorities when their exact artifacts are accessible; blocked external access does not stop the compiler. These carry the credibility of the compiler claims. Optional model breadth does not substitute for them.

**Effect on FlavorTwin.** It consumes P3 canonical products/forms and P7 state versions. "Process-conditioned flavour" is allowed only through DEL-1 evidence. FlavorTwin work stays at W10, after the gates.

---

## 21. Additive schema changes recommended for v14 (versioned adoption)

1. Food concept / physical entity (lot) / entity version as three distinct identities.
2. Planned endpoint versus observed session state.
3. Quantity basis, symbolic expression, fraction scope, correlated-source reference, `unit_variant`.
4. Four orthogonal axes: availability, epistemic provenance (adds `CONVENTION`), verification, trajectory.
5. Field/task annotation masks plus `labels_annotated_for`.
6. External ontology snapshot/version and mapping relation, separate from internal IDs.
7. Text order versus execution dependencies versus control constructs.
8. Unresolved candidate sets and an explicit `NO_VALID_CANDIDATE`.
9. Library adapter contracts: no implicit density, no retrieval prior as observed state, no nearest-ID fallback.
10. Online-prefix versus offline-full-document evaluation modes.
11. `OMITTED_STEP_CANDIDATE` record type (rule ID + precedent IDs), outside the observed graph.
12. Annotation depth A0–A5 and the Sealed flag on Deep Gold.
13. A legacy-adapter table (RecipeDB 7 / TASTEset / r-FG) as a versioned artefact.

Map existing v14 enums through an explicit **migration table**, with no silent reinterpretation.

**Illustrative record (not Gold):**
```json
{
  "schema_version": "PROPOSED-1",
  "entity_id": "example:garlic_lot_1",
  "entity_version_id": "example:garlic_lot_1:v0",
  "canonical_food_id": "example:garlic",
  "raw_mention": "3 cloves garlic",
  "char_span": [0, 15],
  "quantity": {
    "kind": "COUNT",
    "value": {"numerator": 3, "denominator": 1},
    "unit": "example:garlic_clove_portion",
    "mass_g": null,
    "mass_status": "UNRESOLVED",
    "conversion_evidence_id": null
  },
  "availability": "PRESENT",
  "provenance": "EXPLICIT_SOURCE",
  "verification": "UNREVIEWED",
  "trajectory": "PLANNED",
  "annotation_task_mask": ["MENTION", "QUANTITY_STRUCTURE"],
  "labels_annotated_for": ["FOOD_MENTION", "AMOUNT", "UNIT"],
  "validation_flags": ["PORTION_MASS_EVIDENCE_REQUIRED"]
}
```

---

## 22. Risks, mitigations and next actions

| Risk | Mitigation |
|---|---|
| Lab test sets / APIs unavailable or late | Request now (access email sent); fall back to TASTEset, ReciFineGold, our sealed set; say so |
| Annotation throughput below plan | Measure in G-0; shrink A4 subset before shrinking the sealed test |
| Claude usage limits | Front-load Silver in weeks 7–8; cache; GLiNER2.5 cascade (E7.3) |
| Licences of scraped text | Store offsets and derived annotations; redistribute raw text only where permitted |
| Over-claiming SOTA | Matched reproduction; paired bootstrap; publish negative results |
| Inferred-step hallucination | Candidates only; precedent required; E13.3 audit |
| JEPA becomes a time sink | J-gate; ≤ 10% effort; kill criterion |
| Jev access waitlisted / rate limits change | Open-baseline interface from day one; cache responses; Jev optional per decision |
| Jev confidently wrong or miscalibrated on our domain | Our own recalibrator + risk budgets (E14.3); hard gates first; never Gold |
| Jev English-first weakness on Hinglish (S4) | Transliteration + gloss; S4 reported separately; human-first labels where it fails |
| Proprietary model harms reproducibility for graders | Pin `jev-1.13.0`; release cached logs where licences permit; every claim paired with an open baseline |
| Sending licensed recipe text to a third-party API | Check source licences; send derived packets or permitted text only |
| Silver noise propagates | Task masks, verified-Silver ablation (E1.5), random audit stream |
| Benchmark contamination in frontier LLMs | New-source held-out set; disclose |

### First ten working days

Appendix H.4 is the runnable order and H.2 supplies the capacity gate. Start with source/family manifests, a 20-recipe independent pilot, the manual and offset contract, quantity ASTs, the no-default-density adapter, an accessible baseline/scorer, three replay examples, and the shared selector interface. Freeze the initial splits before indexing examples. Draft access requests if necessary, but this plan does not send them. Exact CoSyLab reproduction, a larger regional pool, and Jev access run as conditional branches rather than blocking the pilot.

---

## 23. Source registry (merged)

S1–S34 keep Report A's numbering. Markers: [V] verified in this or the previous pass; [C] from Report A.

| ID | Source | Marker |
|---|---|---|
| S1 | Goel et al., *Deep Learning Based Named Entity Recognition Models for Recipes*, LREC-COLING 2024 (arXiv 2402.17447; aclanthology 2024.lrec-main.406) | [V] |
| S2 | Goel et al., *A framework for recipe data structure with applications for culinary and nutritional insights* (RecipeDB2), arXiv 2609.22099 (preprint) | [V] |
| S3 | FoodSEM: LLM specialised in food named-entity linking, arXiv 2509.22125 | [C] |
| S4 | Drole et al., FoodOntoRAG, arXiv 2603.09758 (IEEE BigData 2025 work) | [C] |
| S5 | Eftimov et al., FoodBench-QA 2026 overview | [C] |
| S6 | RISeC: Resolving Semantic Structure and Zero Anaphora in Recipes, 2020 | [C] |
| S7 | Yamakata, Mori & Carroll, *English Recipe Flow Graph Corpus*, LREC 2020 (aclanthology 2020.lrec-1.638) | [V] |
| S8 | Fan & Hunter, *Understanding the Cooking Process with English Recipe Text*, Findings ACL 2023 (2023.findings-acl.261) | [V] |
| S9 | Aligning Actions Across Recipe Graphs (ARA), 2021 | [C] |
| S10 | REAL: Entity-Action-Location graph reasoning for procedural text, 2021 | [C] |
| S11 | GLiNER2, EMNLP 2025 | [C] |
| S12 | Fastino, GLiNER2.5 (24 Aug 2026), Hugging Face cards `fastino/gliner2.5-{small,base,multi}-v1` | [V] |
| S13 | Fastino, GLiNER2.5-Decide (24 Sep 2026) | [C] |
| S14 | Akujuobi, Liu & Besold, *Revisiting NER in food computing* (SINERA), AI Review 2024 | [V] |
| S15 | FoodOn ontology and facets (Dooley et al., npj Sci Food 2018) | [V] |
| S16 | Liu et al., *Lost in the Middle*, TACL 2024 | [C] |
| S17 | Retrieval-Augmented Instruction Tuning for Open NER, COLING 2025 | [C] |
| S18 | INCEpTION user guide | [C] |
| S19 | Label Studio relation-extraction template | [C] |
| S20 | USDA FoodData Central data-type documentation | [C] |
| S21–S23 | Ingredient Parser (strangetom): docs, unit conversion, foundation-foods matcher | [V] |
| S24 | Conformal Risk Control, ICLR 2024 | [C] |
| S25 | Anthropic support: Using Claude Code with Pro or Max | [C] |
| S26 | ReGraph: Learning to Generate Recipe Graphs from Food Images, 2026 (abstract only) | [C] |
| S27 | Wróblewska et al., TASTEset, 2022 (arXiv 2204.07775) | [V] |
| S28 | Dalvi et al., ProPara, 2018 | [C] |
| S29 | Ibrahim et al., *ReciFine*, Findings EACL 2026, pp. 4058–4074 (2026.findings-eacl.210) | [V] |
| S30 | ReciFine dataset and evaluation documentation | [C] |
| S31 | *Knowledge Augmentation Enhances Token Classification for Recipe Understanding*, EACL 2026 | [V] |
| S32 | RecipeNLG, INLG 2020 | [C] |
| S33 | Recipe1M+, TPAMI | [C] |
| S34 | *Everything robots need to know about cooking actions* (actionable cooking KGs), 2025 | [C] |
| S35 | Diwan, Batra & Bagler, *A named entity based approach to model recipes*, ICDE-W 2020 (arXiv 2004.12184) | [V] |
| S36 | Bagler, *A generative grammar of cooking*, arXiv 2211.09059 | [V] |
| S37 | TASTEset 2.0 repository (github.com/taisti/TASTEset-2.0) | [V] |
| S38 | NYT ingredient-phrase-tagger (CRF) | [V] |
| S39 | Kiddon et al., *Mise en Place: Unsupervised Interpretation of Instructional Recipes*, EMNLP 2015 | [V] |
| S40 | OpenPI (arXiv 2011.08092), OpenPI2.0 (2305.14603), OpenPI-C (2306.00887) | [V] |
| S41 | Wang et al., kNN-NER, arXiv 2203.17103 | [V] |
| S42 | Shiraishi et al., RENER, arXiv 2410.13118 | [V] |
| S43 | Zaratiana et al., GLiNER, arXiv 2311.08526 | [V] |
| S44 | Blevins et al., Universal NER v2, LREC 2026 | [V] |
| S45 | INDoRI: Indian Dataset of Recipes and Ingredients, arXiv 2309.10403 | [V] |
| S46 | Nandy, Kulkarni, Goyal & Ganguly, *Order-Based Pre-training Strategies for Procedural Text Understanding*, NAACL 2024 | [V] |
| S47 | Shirai et al., *JFC-Recipe: A Dataset for Nutrient Estimation from Japanese User-Generated Cooking Recipes*, LREC 2026 (2026.lrec-1.504) | [V] |
| S48 | Assran et al., I-JEPA, CVPR 2023 | [V] |
| S49 | Assran et al., *V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning*, Meta, June 2025 (arXiv 2506.09985) | [V] |
| S50 | Huang, LeCun & Balestriero, *LLM-JEPA*, arXiv 2509.14252 (ICLR 2026) | [V] |
| S51 | VL-JEPA, arXiv 2512.10942 | [V] |
| S52 | Balestriero & LeCun, LeJEPA (SIGReg), 2025 | [V] (via S54) |
| S53 | T-JEPA: augmentation-free SSL for tabular data, ICLR 2025 | [V] (citation) |
| S54 | Var-JEPA, arXiv 2603.20111 (PMLR 306, 2026) | [V] |
| S55 | DLLM-JEPA, arXiv 2606.00091 (ICML 2026 workshop) | [V] |
| S56 | Ogrinc et al., zero-shot ChatGPT for food NER/NEL, Front. Nutr. 2024 | [V] (headline only) |
| S57 | Highly clean recipe dataset with ingredient-state annotation (NHK), arXiv 2507.17232 | [V] |
| S58 | TypeSafe AI, "Introducing System One Models and Jev" (blog, 15 Sep 2026), typesafe.ai/blog/introducing-system-one-models-and-jev | [C] (cited by S61) |
| S59 | TypeSafe docs — Models (Jev 1.13: price, limits, language, data handling), docs.typesafe.ai/models | [V] |
| S60 | TypeSafe docs — Jev 1.13 jaggedness (failure modes), docs.typesafe.ai/model-jaggedness/jev-1.13 | [C] (summarised in S61) |
| S61 | Saha, "What Is Jev? Inside TypeSafe AI's System One Model", Maxim, 21 Sep 2026 | [V] (secondary) |
| S62 | LangChain, "Building a harness with Jev" (TypeSafeClassifier integration), 2026 | [V] (secondary) |
| S63 | Calibrated decision models for autonomous pentest harnesses (surveys the Jev family and an open-source System One project), arXiv 2609.28940 | [U] |
| S64 | CoSyLab, `RecipeDB3_NER_Research_Paper` (GitHub; annotation data + DeBERTa ingredient / spaCy instruction notebooks; updated 7 Jul 2026), github.com/cosylabiiit/RecipeDB3_NER_Research_Paper | [A-code] (audit reported by the supplied MERGED-1.2 attachment; not independently reproduced in this review) |
| S65 | CoSyLab, `CocktailDB_NER_Research_Paper` (GitHub, Apr 2026) | [V] (listing) |
| S66 | *Nutritional Profile Estimation in Cooking Recipes*, arXiv 2004.12286; repo `cosylabiiit/Nutritional-Estimation-In-Recipes` | [V] |
| S67 | CoSyLab, `Recipedb-companion-data` (2020 manual train/test) | [V] (listing) |
| S68 | CulinaryDB, cosylab.iiitd.edu.in/culinarydb (aliases, synonyms, compound ingredients, 22 regions) | [V] |
| S69 | Bansal, Dargar, Goel, Sinha, Bagler et al., *Universal statistical laws governing culinary design*, arXiv 2604.28021 (2026; IIIT-Delhi and Foodoscope) | [V] |
| S70 | Jain, *6000+ Indian Food Recipes Dataset* (Archana's Kitchen; original + googletrans), Mendeley Data, DOI 10.17632/xsphgmmh7b.1 (Kaggle mirrors exist) | [V] |
| S71 | Kaggle, *What's Cooking?* / Recipe Ingredients Dataset (Yummly ingredient lists + cuisine labels) | [V] (listing) |
| S72 | Food.com recipes and interactions (Kaggle) | [U] (not re-checked in this pass) |

### Still genuinely open

- The professor's API/bulk access and permissions (requested).
- Real annotation throughput and Claude Max capacity (measure in G-0 / E0.3).
- Actual agreement per label/source.
- Whether structural features beat strong contextual baselines (E4/E5).
- Whether GLiNER2.5 or the knowledge-augmented models meet risk budgets at useful coverage.
- Whether Jev's decisions beat open baselines on our domain after recalibration, and whether access is granted (E14).
- Licence and permission for reusing the RecipeDB3 annotation data, and the lab's view of the grouped-split re-evaluation (§1.2).
- Whether any JEPA objective helps on recipe tasks (J1–J3, Appendix A).
- The final novelty audit.

*None of these blocks W0–W2. Together they block claims about throughput, SOTA, universal coverage and chemistry.*

---

## Appendix A. JEPA — optional research track (originally assumed to be "JEV")

*Correction:* "JEV" turned out to mean **Jev**, TypeSafe AI's System One model (§17). JEPA remains a valid but **optional** research direction and is kept here unchanged.

### A.1 What JEPA is (consensus)

A JEPA has an **encoder** that embeds a context view *x* and a target view *y*, and a **predictor** that predicts the *embedding* of *y* from the embedding of *x* (optionally conditioned on an action). Learning therefore happens in latent space rather than by reconstructing raw pixels or tokens. LeCun proposed it as a step toward world models [S54][V]. Collapse is prevented by EMA/stop-gradient or explicit regularisers such as LeJEPA's SIGReg [S52][S54][V].

| Work | What it shows | Relevance |
|---|---|---|
| I-JEPA (CVPR 2023) [S48] | Masked latent prediction for images | Origin |
| **V-JEPA 2** (Meta, June 2025) [S49][V] | Pretrained on 1M+ hours of video; **SOTA human action anticipation on Epic-Kitchens-100, 39.7 recall@5**. **V-JEPA 2-AC**: an action-conditioned latent world model post-trained on < 62 h of robot video, planning zero-shot on Franka arms | Kitchen-domain perception; action-conditioned latent transitions = the Level-15 shape |
| **LLM-JEPA** (Huang, LeCun, Balestriero; arXiv 2509.14252, ICLR 2026) [S50][V] | Adds a JEPA embedding-prediction loss between **paired views** (e.g., natural language ↔ code) to next-token training; gains on NL-RX, GSM8K, Spider across Llama3/Gemma2; more robust to overfitting. **Main limitation: needs naturally paired multi-view data.** | Our step text ↔ structured event record is a proposed paired-view application, requiring a matched baseline |
| VL-JEPA (arXiv 2512.10942) [S51][V] | Predicts text embeddings from vision instead of generating tokens | Future multimodal |
| T-JEPA (ICLR 2025) [S53], Var-JEPA (PMLR 2026, tabular variant) [S54][V] | JEPA for heterogeneous tabular data | Possible for the DEL-2 evidence matrix (research only) |
| DLLM-JEPA (2026 workshop) [S55][V] | Ablations: **asymmetric views and the predictor are both load-bearing**; removing either collapses gains | Any J-experiment must keep both |
| Nandy et al., NAACL 2024 [S46][V] | Order-as-supervision pretraining (incl. **embedding regression**) improves recipe entity tracking (+1.6% over the best baseline on NPN-Cooking) | Closest published recipe-domain evidence; a required baseline |
| Recipe-domain JEPA | **No peer-reviewed recipe-domain result identified in the supplied limited search** (search limited). A non-peer-reviewed tutorial trains a toy "ingredients + actions → dish" text JEPA without evaluation. | Novel space, but with no evidence it works |

### A.2 Fit matrix

| Component | JEPA fit | Reason |
|---|---|---|
| P2 span NER | **Low** | Token classification with supervised encoders dominates; JEPA could only be an auxiliary pretraining loss |
| P3 food linking | **Medium** | Mention-in-context ↔ concept card is a natural paired view, but contrastive bi-encoders are the established baseline to beat |
| P5 text → structured event | **Medium–High** | Exactly LLM-JEPA's NL→code setting (regex, SQL). Gold pairs are scarce; Silver pairs (ReciFine/ours) are abundant but noisy |
| P6/P7 omitted-step / inconsistency detection | **Medium** | A latent next-state predictor's error ("surprise") can flag missing steps or contradictions, as candidates only |
| Level-15 planned-state transition prior | **Speculative** | Shaped like V-JEPA 2-AC, but text-only states learn procedural regularities, **not chemistry**; it cannot replace ledgers |
| Level-17 multimodal session observation | **Highest readiness, out of mini-project scope** | Frozen V-JEPA 2 features on kitchen video → OBSERVED_SESSION state updates |
| Quantity arithmetic, unit conversion, evidence claims, provenance, Gold labels | **None** | Deterministic code and human verification only |

### A.3 JEPA experiments (all gated)

**J-gate.** No J-experiment starts until E1.1, E3.1 and E4.1–E4.3 baselines exist and frozen splits are in place. Total JEPA effort ≤ 10% of project time. Kill criterion: no gain over the matched non-JEPA baseline outside the paired-bootstrap CI on dev after one tuning round.

| ID | Question | Design | Baselines | Metric / success |
|---|---|---|---|---|
| **J1** | Does a JEPA objective improve the P3 linking encoder under low labels? | Mention-in-context encoder predicts the concept-card embedding (predictor + EMA target); compare at 10/25/50/100% of link-gold | Contrastive bi-encoder (InfoNCE); MLM continued pretraining | Recall@20, Acc@1, ACCEPT-band precision, tail bucket; win = significant tail gain |
| **J2** | Does LLM-JEPA-style fine-tuning improve step → event-JSON parsing? | Small instruction model; loss = next-token + λ·JEPA(step-text view ↔ gold event-JSON view); Silver-only vs Gold-Light pairs | Same model, standard SFT; same token budget | Event argument F1, valid-JSON rate, held-out-source F1; win = gain at ≤ 1k gold pairs |
| **J3** | Does latent "surprise" detect omitted steps/inconsistencies better than LM perplexity or rules? | Latent transition predictor $\hat z_{t+1}=g(z_t, a_t)$ over step embeddings; flag steps with high prediction error | Rule + precedent library (§10.2); LM perplexity; Nandy-style order model | Omitted-step candidate precision@k vs gold "missing prerequisite"; hallucination rate; win = higher precision at matched recall, candidates only |
| **J4** (stretch) | Can an action-conditioned latent model act as a planned-state prior for the state tracker? | V-JEPA-2-AC-style predictor on (entity-state packet, action) → next packet embedding; probe for state fields | Symbolic replay only; GRU baseline | State-field probe accuracy, replay consistency; **never overrides symbolic replay** |
| **J5** (future, Level 17) | Can frozen V-JEPA 2 video features update observed cooking state? | Linear probes on kitchen video for doneness/colour/phase | Image CLIP features | Out of mini-project scope |

**Verdict.** JEPA is a credible **research add-on**: J2 or J3 could each be a paper-worthy sub-experiment. It is **not** a core dependency and **not** a promised deliverable. Mention it in reports as an exploratory track gated by baselines.

## Appendix B. Implementation contract: records, services, and replay

### B.1 The smallest coherent build

Build one vertical slice that accepts a recipe, preserves its text, extracts mentions and quantity expressions, resolves food concepts, records events and entity versions, and answers five constrained questions with evidence. The first release should answer: what food is mentioned; what amount is stated; which lot is used now; what fraction remains; and what information is missing for a requested task. A service that cannot answer these reproducibly should not yet generate richer process-science explanations.

The slice consists of a corpus manifest, a concept registry, a quantity parser, one baseline extractor, one candidate generator/selector, an event/reference parser, a replay engine, validators, and a common evaluator. Keep provider integrations behind adapters. SQLite plus JSONL is adequate for the pilot; Parquet snapshots can support batch analysis. Neither a graph database nor a graph neural network is a prerequisite for having a typed graph.

Treat a compile run as immutable. Its outputs are selected proposals with versioned provenance. Corrections produce a new annotation revision and a new compiled snapshot. The application may show the latest accepted view, but evaluation always points to an explicit snapshot. This makes an answer reproducible after an alias, ontology, prompt, or model changes.

### B.2 Record families and their keys

| Record | Primary key | Required references | Purpose |
|---|---|---|---|
| Source asset | `source_asset_id` | source URL or supplied-file identity, content hash | Immutable bytes and source terms |
| Recipe | `recipe_id` | source asset, family, locale assertions | Document-level boundary |
| Text view | `view_id` | recipe, raw hash, transformation version | Normalized model input with offset provenance |
| Mention | `mention_id` | recipe, raw segment list, label contract | Lexical evidence |
| Field assertion | `assertion_id` | owner record, evidence references | Value plus epistemic status |
| Food concept | `concept_id` | registry revision | Reusable identity |
| External mapping | `mapping_id` | internal ID, external snapshot, relation | Versioned crosswalk |
| Lot/entity | `entity_id` | recipe or session | Physical ingredient lot or intermediate |
| Entity version | `entity_version_id` | entity, prior version, producing event | State at a logical boundary |
| Quantity expression | `quantity_id` | AST, basis, source variable | Stated or derived amount |
| Conversion evidence | `conversion_record_id` | food/form/basis, source record | Approved grounding route |
| Allocation | `allocation_id` | parent quantity, child/entity, branch | Transfer or fraction accounting |
| Event | `event_id` | step span, roles, dependencies | Procedure semantics |
| Reference decision | `reference_id` | mention/omitted role, candidates, cutoff | Antecedent grounding |
| Control construct | `control_id` | branch/loop expressions, body events | Execution structure |
| Observation | `observation_id` | session, reported time, target entity | Actual-session evidence |
| Model decision | `decision_id` | request hash, options, distribution | Auditable selection |
| Review issue | `issue_id` | record/field, reason, resolution | Human workflow |
| Scientific row | `evidence_id` | study family, table/span, conditions | Independent measurements |
| Answer claim | `claim_id` | supporting assertions and derivation | User-facing grounding |

Canonical-form information is a versioned view over concept identity and entity facets. It is not a fourth physical ledger with an independent copy of the same quantity. This answers the request for ingredient, canonical-form, and quantity ledgers without creating competing sources of truth: ingredient/entity records own identity and lineage; the canonical-form view exposes concept plus facets; quantities own amounts; event/state records own change history.

### B.3 Field-level evidence wrapper

Whole-record provenance is insufficient. In one event, the verb may be explicit, its object inferred, its duration not stated, and its planned endpoint explicit. Each answer-critical field therefore needs an assertion wrapper, or a normalized assertion table with equivalent fields:

```json
{
  "assertion_id": "example:assertion:17",
  "owner_record_id": "example:event:3",
  "field": "input_entity_id",
  "value": "example:entity:sauce",
  "availability": "PRESENT",
  "epistemic_provenance": "INFERRED_LLM",
  "verification": "UNREVIEWED",
  "trajectory": "PLANNED",
  "evidence_refs": ["example:mention:8", "example:event:2"],
  "inference_rule_id": "example:compatible-active-output-v1",
  "decision_id": "example:decision:42",
  "calibrated_probability": null,
  "guideline_version": "LM-1.0.0"
}
```

This is a synthetic contract example. A human can later mark the inference as verified while its provenance remains inferred. If the source only says “cook until soft,” `duration` is `NOT_STATED`; the source has provided a stopping condition, not a numeric elapsed time. If a user says “I cooked it for four minutes,” create an observed-session assertion rather than rewriting the planned recipe.

Store a separate `evidence_origin` for inferred fields: rule, learned resolver, external precedent, or human interpretation. If v14 lacks a rule-inference enum, propose `INFERRED_RULE` through migration; do not mislabel a deterministic rule's semantic guess as `DERIVED_DETERMINISTIC`. Exact arithmetic on a stated fraction is deterministic. Choosing what “it” means is an interpretation even when software executes the rule deterministically.

### B.4 Offset and text-view contract

Declare raw offsets as half-open Python/Unicode code-point intervals, `[start, end)`, within an immutable UTF-8-decoded raw section. Store the section ID as well as the interval; ingredient line 2 and instruction step 2 are different coordinate spaces. Frontend JavaScript uses UTF-16 positions, so the adapter must translate offsets rather than assuming they match Python for emoji or supplementary characters.

Every mention stores one or more ordered, non-overlapping raw segments. A contiguous mention has one segment. A discontinuous mention stores several and an explicit segment-join policy for display. The evaluator never invents a contiguous span that covers unrelated intervening text merely to accommodate a flat tagger.

Each normalization operation records a transformation kind and an interval mapping. Normalizing `½` to `1/2` is one raw character to three view characters. A model span that lands inside that expansion is mapped to the containing raw segment and checked. Transliterated or translated views require an alignment confidence; a gloss without reliable alignment can help linking but cannot create raw character-span Gold. Keep the source and gloss available together.

Offset acceptance fixtures must cover: vulgar fractions; mixed numbers; en-dash ranges; accented food names; Devanagari; Hindi/English code mixing; nonbreaking spaces; line breaks; repeated food names; and an emoji before a labeled span. A passed fixture proves mapping integrity, not that the model chose the correct label.

### B.5 Interface contracts

| Interface | Input | Output | Failure result |
|---|---|---|---|
| `prepare_text` | raw asset + normalization configuration | views + reversible maps | `INVALID_ENCODING` or unsupported transform |
| `extract_mentions` | bounded text view + label descriptions | candidate spans + attributes | no candidates; malformed proposals retained in diagnostics |
| `generate_concepts` | mention + context + registry snapshot | candidates with retrieval components | `CANDIDATE_SET_EMPTY` |
| `select_option` | decision family + state + ordered option cards | distribution + selected ID + model metadata | timeout/invalid output, never nearest-ID fallback |
| `parse_quantity` | raw amount expression + surrounding scope | typed AST + ambiguities | `UNPARSED_EXPRESSION` |
| `parse_events` | current step + prefix packet | atomic event/role proposals | unresolved event boundaries or roles |
| `resolve_reference` | role/mention + candidate versions + cutoff | candidate decision or unresolved set | `NO_COMPATIBLE_ANTECEDENT` |
| `replay_event` | validated event + prior snapshot | transaction + next snapshot + issues | proposed transaction rejected atomically |
| `ground_quantity` | AST + compatible conversion candidates | mass/volume expression + evidence route | retain original symbolic amount |
| `assess_sufficiency` | task + accepted snapshot + evidence packet | capability route + missing fields | unsupported/conflicting |
| `render_answer` | approved claim packet | concise answer linked to claims | abstention template |

The replay engine and quantity arithmetic do not call a model. A model may supply a proposed event or select an existing conversion record; code checks it before execution. This separation lets model comparisons use identical downstream logic.

### B.6 Compile loop and bounded revisions

1. Validate P0/P1, create immutable mentions and quantity AST proposals.
2. Generate concept candidates, select links, and initialize ingredient-list lots.
3. For each step, build the prefix packet from accepted prior events and branch state.
4. Propose atomic events; resolve explicit and omitted roles against compatible versions.
5. Validate temporal, type, quantity, and branch constraints.
6. Commit a transaction and produce a new planned snapshot, or preserve alternatives and an issue.
7. Attempt food-specific grounding only after its semantic dependencies are available.
8. Run a full-document audit; offline revisions may cite later evidence, but online snapshots remain unchanged.
9. Build a sufficiency packet for the requested task and render supported claims.

Allow one targeted automatic repair of invalid model structure and at most two semantic proposal rounds for a step during the pilot. Additional unresolved issues go to review. These are operational caps, not scientific assertions. Log why a repair was attempted and whether it changed boundaries, candidates, or decisions. Never let a validator repeatedly force a plausible source contradiction into a clean graph.

### B.7 Event sourcing and idempotency

The event log is append-only. A transaction includes its input snapshot hash, event revision, output versions, quantity changes, issues, and compiler configuration hash. Replaying identical accepted events under the same configuration must reproduce the same canonical snapshot hash. IDs derived from normalized immutable keys must be stable within a release; human corrections have explicit revision IDs.

For API-derived proposals, cache by the full request contract: model version, state, question descriptions, candidate IDs/order, prompt version, schema version, and registry snapshot. A cache hit is a replay mode, not a fresh model latency measurement. Store network timing separately from inference/pipeline timing where available. Do not cache a model answer as if it were an independently verified fact.

On a change to a concept mapping, invalidate dependent link decisions, food-specific conversions, and evidence joins. On a corrected span, invalidate all decisions that consumed that span. A quantity-only correction need not retrain the NER model, but its downstream allocations must be replayed. Document the dependency graph so invalidation is explicit rather than a full, opaque rerun.

### B.8 Candidate implementation layout

| Module / artifact | Responsibility | Required release artifact |
|---|---|---|
| `contracts/` | JSON schemas, enums, field masks, migrations | schema version and changelog |
| `sources/` | ingestion adapters, rights manifest, hashes, families | corpus/source manifest |
| `text/` | reversible views, offset conversion, language helpers | offset fixture report |
| `vocabulary/` | concept cards, aliases, product relations, xrefs | frozen registry snapshot |
| `mentions/` | NER adapters and legacy output adapters | extractor configurations |
| `quantities/` | grammar, AST, unit registry, evidence adapters | quantity fixture report |
| `decisions/` | common selector API, Jev/open/Claude adapters | decision cache and probe results |
| `events/` | atomic events, roles, control constructs | parsing error taxonomy |
| `replay/` | entity versions, allocations, snapshots | replay integrity report |
| `evidence/` | scientific rows and compatible joins | evidence card and study hashes |
| `evaluation/` | matched scorers, clustered intervals, cost reports | frozen metric definitions |
| `annotation/` | manual, decision log, tool import/export | adjudication and assistance log |
| `application/` | task sufficiency, retrieval, claims, demo | benchmark and scenario outputs |

These are suggested project-relative paths, not files already implemented. Use the existing repository structure if it has equivalent responsibilities. Start with ordinary modules and command-line batch runs; create a web UI only after the annotation-tool pilot establishes a concrete unmet need.

## Appendix C. Annotation manual v1: decisions the label picker must support

### C.1 Separate detection, classification, identity, and change

Annotators first identify source spans, then assign lexical labels and qualifiers, then resolve food identity, then bind physical lots, then annotate event roles and changes. A single dropdown cannot represent all five decisions. “Tomato paste” may be one food mention with a product concept; “tomato, finely chopped” may be a food mention plus form/preparation facets. Both can be valid NER outputs while requiring different canonical representations.

Use staged visibility: ingredient-line annotators see source lines and relevant locale metadata; link annotators see registry cards; flow annotators see earlier accepted states and the current raw step. During independent Deep Gold passes, no model predictions, model confidence, or other annotator's answers appear. Registry descriptions and the written manual are available to both annotators. Record the registry version they saw.

### C.2 Boundary rules for the initial core labels

| Label | Inclusion rule | Exclusion / hard case |
|---|---|---|
| `FOOD_MENTION` | Smallest span naming the food/product under the internal lexical convention | “Sour cream” remains one mention; a benchmark adapter may use different tags |
| `AMOUNT` | Numeric or fractional expression, including explicit range endpoints | Unit is separate; a package multiplier has scope, not one flattened number |
| `UNIT` | Measure token/phrase with declared unit semantics | “Clove” is a portion unit in “3 cloves garlic,” a food in “ground cloves” |
| `FORM` | Physical presentation: diced, sliced, grated, minced | Does not imply a new event occurred in the written instructions |
| `PREP_STATE` | Source-stated preparation/state such as cooked, thawed, drained | Distinguish initial state from an instruction's intended result |
| `DRY_FRESH` | Explicit dry/fresh qualifier | Absence is unstated, not fresh by default |
| `TEMP` | Explicit temperature-related expression | “Hot pepper” may mean pungency; “hot pan” refers to equipment |
| `PART` | Edible/anatomical part when expressed: leaf, seed, breast, zest | Part may be concept-defining; do not force it to be a disposable modifier |
| `VARIETY` | Explicit food cultivar/type descriptor | Locale ambiguity can remain an unresolved sense |
| `SIZE` | Explicit size descriptor: small, medium, large | Size class is not a measured gram weight |
| `BRAND` | Source-stated brand/product designation | Do not infer manufacturer from packaging style |
| `PACKING` | Stated packed, loosely filled, heaped, level convention | Do not infer packing from the ingredient alone |
| `ACTION` | Predicate expressing a culinary or material-flow instruction | “Do not drain” has a negated action; the material is not drained |
| `TOOL` | Equipment/container named in a role-compatible context | A “cup” used as a container differs from a measured cup amount |
| `DURATION` | Explicit time interval or amount | “Until tender” is an endpoint, not a numeric duration |
| `ENDPOINT` | Explicit target/stop condition | Planned golden color is not observed golden color |
| `INTERMEDIATE_MENTION` | Source name/reference to a preparation: sauce, batter, mixture | Its composition and identity are resolved separately |
| `CONDITION` | Explicit branch or operating condition | “If needed” does not assert that the branch ran |

`PACKING` is a proposed additive child/facet absent from some legacy tagsets. If introduced, version the manual and annotate its task mask. Additional new labels should pass the same lifecycle; schema-based models being able to name a label does not make old records annotated for it.

For punctuation, exclude commas, parentheses, and sentence-final punctuation unless semantically part of a lexical food/product name. Include hyphens internal to a lexical mention. In `1 (400 g) can tomatoes`, parentheses delimit package-content structure; numeric and unit spans remain raw subspans. A benchmark-specific tokenizer may yield a different token boundary; scoring uses its own frozen adapter, not a global rewrite.

### C.3 Qualifiers and non-events

| Source expression | Annotation | Accounting consequence |
|---|---|---|
| “optional” | optional lot/use qualifier | Absence from an executed branch is valid |
| “or coconut milk” | alternative food branch | Never add both alternatives to default totals |
| “plus more for dusting” | additional/open amount and purpose | Fixed amount does not cover the open use |
| “divided” | future allocation expected | Does not determine fractions by itself |
| “reserve half” | reserve operation plus fraction scope | Creates an allocated reserved portion |
| “do not drain” | negated drain predicate | No drain transaction |
| “if the sauce is thick, add water” | condition plus optional event | Two possible planned branches; executed branch unknown |
| “chopped onion” in ingredients | initial form/preparation | No source-explicit chopping event |
| “preheated oven” | equipment initial condition | Does not prove a separate preheat sentence exists |
| “serve with rice” | serving relation to an external/optional entity | Do not invent the rice's cooking procedure |

Annotate a negated action as a lexical action mention with a negation attribute so the span task can learn it. The event replay adapter rejects its execution as a positive material operation. This prevents NER evaluation and procedure evaluation from disagreeing merely because an action word is present.

### C.4 Relation endpoints and equivalence

`SAME_LOT_AS` joins mentions that denote the same recipe lot. `REFERS_TO` binds a reference mention or omitted event role to an entity version. `PART_OF` records containment or component membership with a declared basis. `DERIVED_FROM` at concept level describes product lineage; at entity level it describes material lineage. Namespace these relation types or record their level so a food-ontology relation cannot accidentally become a recipe transaction.

Do not make all references an equivalence class. The onion mention before frying and the onion-containing sauce after a merge can share material lineage without being identical physical entities. “Half the sauce” refers to an allocation, not the whole sauce as an interchangeable amount. Two “butter” lines with different quantities may be two lots even if they share a canonical concept.

When a pronoun admits two compatible antecedents, annotate `UNRESOLVED` with the candidate set and reason. If later text disambiguates it, the offline annotation records that later evidence; the prefix annotation remains ambiguous at that cutoff. Gold need not force one interpretation where the source does not determine one.

### C.5 Unlabeled versus absent

Store task masks at recipe, section, and field family as needed. A recipe may have ingredient spans exhaustively annotated but only selected instruction relations checked. In that case, `O` is valid for the ingredient-span scope; it is not valid for arbitrary instruction relations. A negative edge is supervised only under an exhaustive eligible-pair contract, or when explicitly rejected by annotation.

For every task, define its eligible universe. For coreference it may be food/intermediate references plus omitted input roles, excluding unrelated pronouns about the cook. For quantity grounding it may be source-stated quantities with a parseable dimension; qualitative “to taste” is recorded, but does not count as an automatically mass-groundable item. Evaluators read the masks rather than guessing missingness from null values.

### C.6 Gold chain and disagreement workflow

1. Sample and family-lock the recipe before annotation.
2. Annotator A and B complete the specified depth independently.
3. Compute agreement against both original passes before adjudication.
4. Open a disagreement item with both values, source spans, and manual rule.
5. Adjudicate with a written reason; keep both original annotations.
6. If the manual changes, identify all affected prior records and re-review them.
7. Validate offsets, IDs, roles, branches, allocations, and field evidence.
8. Assign verification status per task/field; seal eligible test snapshots and hashes.

Gold-Light follows a different route: predictions may be visible, one person verifies specified fields, and assistance is logged. For a contested case, a second independent source-first annotation can improve reliability; it does not erase the fact that one original pass was assisted. Promotion to independent Deep Gold requires a new independent protocol, not merely relabeling the record after a critic agrees.

Agreement should include strict span-F1, attribute agreement conditional on matched spans, canonical-link agreement including unresolved categories, and edge agreement under a declared node alignment. Cohen's κ is appropriate only for paired categorical decisions with a well-defined common item universe. It should not be applied to arbitrary free-form edge lists without constructing that universe. Report prevalence and category counts alongside κ.

### C.7 Assistance experiment without contaminating Gold

Run E0.3 on an explicitly Gold-Light pilot pool. Randomize recipes between source-first and assisted annotation, balancing complexity and source. A person should not see the same recipe's assisted answer and then act as its independent source-first annotator. Use different recipes or a counterbalanced design with a documented memory/washout limitation; do not claim blinding was perfect if it was not.

Measure total review time, errors remaining after review, corrections per field, and disagreement with a source-first reference. An 0.85 teacher-precision threshold is a triage proposal; with small support, use its uncertainty and error severity, not the point estimate alone. A high-confidence wrong product merge can matter more than several harmless boundary corrections.

### C.8 Picker behavior and review reasons

The picker shows source evidence first, then candidates with short definitions, facets, and compatibility flags. It allows search beyond the initial top-K, creation of a proposed vocabulary item, and unresolved reasons. Candidate order can be randomized during an anchoring study; ordinary annotation should preserve a logged sort order.

| Picker result | Meaning | Next queue |
|---|---|---|
| `ACCEPT_EXISTING` | Existing concept/record is supported | Normal validation |
| `ALIAS_PROPOSAL` | New surface form for an existing sense | Alias review |
| `PRODUCT_PROPOSAL` | Distinct product needed at declared granularity | Concept review |
| `AMBIGUOUS_LOCALE` | Multiple regional senses remain | Locale/context review |
| `NO_VALID_CANDIDATE` | Registry/shortlist lacks the correct target | Candidate-recall audit |
| `NOT_STATED` | Source provides no value | Missingness retained |
| `UNRESOLVED_REFERENCE` | Several recipe entities fit | Flow review |
| `CONFLICTING_SOURCE` | Source assertions cannot both hold | Conflict review |
| `NOT_APPLICABLE` | Field does not apply to this object/task | Mask/contract check |

Do not use a generic `OTHER` to collapse all these outcomes. They have different actions and different evaluation meanings. For a small closed-set model, the options can remain compact, but the application retains the distinct reason codes.

### C.9 New-label lifecycle and regression pack

For a proposed new label, write its definition, parent, purpose, boundaries, exclusions, required evidence, and downstream use. Search a development pool for examples and near misses. Annotate a small source-diverse pilot independently; review whether the distinction is observable and useful. Add a task mask and migration rule before expanding annotation. Benchmark zero-shot descriptions on development data, then freeze the selected descriptions for test.

Each manual revision adds a regression pack of adjudicated examples. Gold test cases never become prompt demonstrations. A development-only pack may contain synthetic edge cases clearly labeled as fixtures. Keep the label-description probe separate from the sealed benchmark; choosing the best paraphrase on test is model tuning.

### C.10 Weak value-list annotations

If the RecipeDB3 source release uses value lists rather than raw offsets, retain them as `VALUE_LIST_SOURCE`. A projection algorithm produces a separate `PROJECTED_SPAN_VIEW` with tokenization, matching, punctuation, occurrence-selection, and rewrite rules recorded. A repeated value appearing twice must not become two Gold spans merely because a string match found both.

A re-annotation sample is drawn before examining our predictions, covers repeated values and ambiguous boundaries, and receives raw-span independent annotation. Report agreement between value-list projection and the new span reference separately from model accuracy. Performance on projected labels and performance on human raw spans answer different questions. This is especially important for low-support PREPROCESS, DRYFRESH, and quantities.

## Appendix D. Quantity and entity lineage: worked cases and transaction semantics

### D.1 Typed quantity expressions

Use an AST rather than a string formula that an LLM later interprets. Initial node types are `RATIONAL`, `RANGE`, `ADD`, `MULTIPLY`, `FRACTION_OF`, `REMAINDER_OF`, `PACKAGE_CONTENT`, `ALTERNATIVE`, `QUALITATIVE`, `OPEN_AMOUNT`, and `UNKNOWN`. A numeric leaf includes its unit and basis. A symbolic leaf references a source variable or another quantity record. Range endpoints remain exact rationals until an evidenced floating-point conversion requires a numeric approximation.

Separate `quantity_kind` from `dimension`: a range may measure mass, volume, count, or duration. A package expression includes item count and content mass. A source may state alternative equivalent-looking expressions such as “500 g or 1 cup”; that is an alternative assertion with a potential conflict, never a multiplication of 500 by cups.

| Raw expression | AST interpretation | Important preserved field |
|---|---|---|
| `1 1/2 cups` | `MULTIPLY(3/2, cup_variant)` | mixed-number scope |
| `1-2 tbsp` | `RANGE(1, 2, tbsp_variant)` | bounded uncertainty, not mean 1.5 by default |
| `2 x 200 g` | `MULTIPLY(2, 200 g)` | whether mass is each-item content |
| `1 lb 2 oz` | `ADD(1 lb, 2 oz)` | compatible mass dimension |
| `half the reserved sauce` | `FRACTION_OF(1/2, reserved_quantity)` | exact parent/allocation identity |
| `remaining flour` | `REMAINDER_OF(flour_source, supported_prior_allocations)` | unknown if allocations are incomplete |
| `salt to taste` | `QUALITATIVE(to_taste)` | no number inferred |
| `2 cups plus more` | `ADD(2 cups, OPEN_AMOUNT)` | lower fixed term and open additional term |
| `500 g or 1 cup` | `ALTERNATIVE(500 g, 1 cup)` | equivalence/conflict not automatically assumed |

### D.2 Unit conventions and evidence hierarchy

Resolve a measure convention from explicit source definitions first, then a documented source-level convention, then supported locale metadata. Region is a prior, not a universal proof of cup size. A source using imported US recipes may retain US cups in an Indian collection. When convention is unresolved, keep candidate variants; an interval over those variants is a scenario envelope, not a calibrated probability interval unless probabilities are actually estimated.

For food-specific mass grounding, prefer an exact compatible portion record, then a reviewed ingredient/product/form-specific density or weight record, then a clearly labeled category-level estimate if the requested task permits it. The strict automatic route does not accept a category approximation as if it were measured for that food. `UNKNOWN` is a useful output when form, packing, edible basis, or size is absent.

Temperature conversion is affine: convert absolute temperature using scale and offset, and temperature differences using scale alone. Quantity scaling must never multiply an oven temperature by the serving multiplier. A household container called a “cup” may have no calibrated volume; store `CONTAINER_COUNT` rather than silently using a culinary measuring cup.

### D.3 Core transaction operations

| Operation | Material effect | Quantity policy |
|---|---|---|
| `TRANSFORM` | New state version of a lot/entity | Preserve stated amount unless a supported amount change exists; final mass may be unknown |
| `MERGE` | Inputs become components of a new intermediate | Preserve parent source contributions; final mixture amount depends on compatible known totals/process losses |
| `SPLIT` | Parent amount allocated to children | Fractions/amounts tracked on one declared compatible basis |
| `TRANSFER` | Location/container changes | No quantity loss assumed solely from transfer |
| `RESERVE` | Portion held out of current use | Creates reserved allocation; remaining parent available amount is updated |
| `DISCARD` | Portion exits edible/available path | Removed from available amount; source-origin history retained |
| `RECOMBINE` | Previously separated portions merge | Same accounting rules as merge; avoid duplicate parent contribution |
| `SERVE` | Amount allocated to served output | Serving count and serving mass are distinct |
| `WAIT` | Time/condition transition | No chemical or mass delta without evidence |

A material operation is committed only when all necessary role references and allocation semantics are accepted. For ambiguous operations, create alternatives or an unresolved transaction. Do not execute both sides of an ambiguity and then use whichever ledger balance looks cleaner.

### D.4 Example 1: nested reservation with known and unknown mass

Synthetic source: “Make 200 g sauce. Reserve half. Use half of the reserved sauce in the filling. Keep the rest for serving.” Assume no process loss is stated between these allocation events.

| Boundary | Entity / allocation | Expression | Available role |
|---|---|---|---|
| Initial | sauce source `Q0` | `200 g` | parent |
| Reserve | reserved portion `Qr` | `1/2 Q0 = 100 g` | reserved |
| After reserve | non-reserved portion `Qa` | `1/2 Q0 = 100 g` | active |
| Fill | portion from reserve `Qf` | `1/2 Qr = 1/4 Q0 = 50 g` | incorporated in filling |
| Remaining reserve | `Qrs` | `Qr - Qf = 50 g` | reserved for serving |

The final material-origin accounting is `100 g active + 50 g in filling + 50 g reserved = 200 g`. This describes allocations, not a measured final mass after later cooking. If initial mass is unknown, replace `200 g` with `Q0`; the fractions remain valid and the compiler can answer that one quarter of the original sauce was allocated to the filling. It cannot answer grams.

The words “Use half of the reserved sauce” directly support access to that reserved portion. No separate “retrieve the sauce” sentence is required. Code can record a state/access transition tied to the use event, with interpretation provenance; it must not add a source-explicit retrieve action.

### D.5 Example 2: two butter lots and a mixture

Synthetic ingredients: “4 tbsp butter, divided”; “2 tbsp butter for topping”; “2 onions, sliced.” Instructions: “Cook the onions in half the divided butter. Add the remaining divided butter. Melt the topping butter separately.”

Create butter lot `B1` for the divided 4 tbsp and `B2` for the topping 2 tbsp. Both have the same concept, but their purposes and quantities differ. “Half the divided butter” allocates 2 tbsp from `B1`; “remaining divided butter” resolves to the residual 2 tbsp of `B1`; topping butter resolves to `B2`. A canonical-ID-only resolver would confuse the lots.

The onion/butter pan mixture is a new intermediate with material parents. Its total mass is not known merely because butter volume and onion count are known. Its parent butter allocation remains 4 tbsp; its final retained butter amount after cooking is unknown unless evidence states losses/retention. The ingredient ledger can trace butter into the mixture while the quantity ledger refuses unsupported final grams.

If the source only says “add remaining butter,” both lots may be compatible. Purpose, location, and prior allocations are useful features, but absence of disambiguating text can require `UNRESOLVED`. A resolver should be evaluated for correct unresolved decisions, not rewarded for always picking the most recent butter.

### D.6 Example 3: packaged mass, draining, and separate liquid

Synthetic source: “One 400 g can tomatoes, drained. Reserve the liquid. Simmer the tomatoes.” The phrase “drained” describes a prepared ingredient state; the package-content mass does not specify the drained-solid mass. “Reserve the liquid” implies a separate liquid entity, but its amount is unknown unless provided.

Represent package contents, drained tomato solids, and reserved liquid with related lineage. A structural separation may be inferred from the source preparation and instruction, but do not fabricate a full draining event with an invented duration. Store package mass 400 g on its correct basis; store drained solids and liquid amounts as unknown. A conservation relation can be retained as a symbolic hypothesis only when the relevant contents/basis and losses are compatible. It is not a measured equality for the final simmered solids.

A serving-nutrient calculation using 400 g of undrained tomatoes would be unsupported for these solids. A retrieval task about using drained tomatoes can still be ready. Sufficiency therefore depends on the task, not on whether every entity has grams.

### D.7 Example 4: heterogeneous mixture and source allocation

Synthetic source: “Mix beans and broth. Reserve half the mixture.” Half by volume does not necessarily contain half the beans by mass. Even half by total mass does not guarantee equal component fractions unless mixing/homogeneity assumptions are supported. Preserve the mixture fraction and its basis; component-specific allocation stays unknown or scenario-based.

Distinguish three possible questions: how much mixture was reserved; what share of source material was intended to be reserved; and what measured nutrient/chemical composition is in the reserved portion. Only the first may be source-supported. An optional homogeneous-allocation scenario must carry its assumption ID, and it cannot be displayed as measured component mass.

### D.8 Example 5: planned and observed branches

Synthetic source: “Simmer until thick. If it becomes too thick, add water.” Planned state includes a thickness endpoint and a conditional water-addition branch. There is no stated simmer duration, evaporation amount, or water quantity. A live user says, “It is still thin after five minutes.” The session now has an observed duration and observed qualitative state. The endpoint remains a plan target.

Online advice may use current state plus supported procedure/evidence to suggest continuing or clarifying, but it cannot assert that the water branch ran. A later report, “I added half a cup of water,” creates a session addition with its own unit convention. Session changes invalidate affected totals and evidence compatibility checks. They do not overwrite the immutable source recipe.

### D.9 Conflict handling and partial execution

Use issue codes such as `ALLOCATION_EXCEEDS_AVAILABLE`, `UNKNOWN_FRACTION_BASIS`, `AMBIGUOUS_LOT`, `UNPRODUCED_REFERENCE`, `DISCARDED_MATERIAL_REFERENCE`, `BRANCH_STATE_UNRESOLVED`, `SOURCE_AMOUNT_CONFLICT`, and `INCOMPATIBLE_CONVERSION_EVIDENCE`. Each stores severity, affected fields, source evidence, and suggested resolution.

Some conflicts block only one task. An unresolved onion mass blocks a complete nutrient total but not an onion identity answer. A duplicated butter allocation blocks “how much butter remains” until repaired. A conflict never licenses code to silently clamp the fraction, drop a source assertion, or select the quantity that makes conservation pass.

On partial failure, keep the accepted prefix snapshot and the unresolved step proposals. The application may continue answering unaffected questions. The evaluator records the blocked task and accepted coverage, so failing gracefully is visible without counting unsupported answers as correct.

### D.10 Uncertainty and dependency checks

Represent shared source variables explicitly. If `Q0` has a mass interval, both `0.5Q0` children depend on the same variable; recombination must recover `Q0`, not a wider interval created by independent sampling. A density record can also be shared across several uses, while portion-size uncertainty may be independent or correlated depending on the evidence.

Separate semantic uncertainty from numeric variability. An unresolved garlic-versus-clove-spice link is a discrete interpretation alternative; it is not a gram error bar around one chosen food. An unknown cup convention is a discrete unit scenario. Report interval coverage only where a reference value and a defined interval meaning exist. For source ambiguity, report whether the correct scenario/candidate is retained.

## Appendix E. Jev and open selectors: precise integration and adoption protocol

### E.1 Verified public contract, with limited conclusions

TypeSafe's current model page lists `jev-1.13.0`, text/JSON state, $0.042 per million input tokens with free output tokens, and dynamic rate limits. It describes a 64k total request budget and a 32k state-plus-longest-question budget, English-first performance, and request-based customization rather than customer fine-tuning. These are provider documentation facts checked on 2 October 2026, not tested throughput or recipe accuracy. See [R1].

The API exposes Choice, Score, and Noul [R2–R4]. Choice selects from supplied options; Score uses an ordered rubric; Noul returns a yes-probability. Questions in a call see the same state independently. Structured answer spaces constrain output types; they do not ensure the selected fact is correct. We do not adopt the provider's speed, cost, or “zero hallucinations” marketing claims as domain results.

### E.2 Provider-neutral decision request

Define our own request envelope before writing a Jev-specific adapter:

```json
{
  "decision_family": "FOOD_LINK_SELECTION",
  "schema_version": "decision-1.0",
  "state_snapshot_id": "example:prefix:5",
  "evidence_cutoff": {"mode": "ONLINE_PREFIX", "step_index": 5},
  "source_refs": ["example:mention:31"],
  "question": "Which candidate food sense is supported by this mention and context?",
  "options": [
    {"id": "example:coriander_leaf", "description": "Leaves used as an herb"},
    {"id": "example:coriander_seed", "description": "Seeds used as a spice"},
    {"id": "NO_VALID_CANDIDATE", "description": "The correct sense is absent"},
    {"id": "UNRESOLVED", "description": "Available evidence does not distinguish the senses"}
  ],
  "state": {"raw_mention": "dhaniya", "local_context": "example context", "locale_status": "UNRESOLVED"},
  "registry_snapshot": "example:registry:1",
  "criteria_version": "food-link-1.0"
}
```

The adapter translates this envelope to each provider's request. The response stores selected option, complete probabilities when available, raw provider confidence, model/version, token usage, time, validity flags, and cache mode. A logistic baseline may return calibrated probabilities over candidates; a cross-encoder may need score calibration; Jev exposes a distribution. Their differences remain explicit.

### E.3 Candidate constraints before and after selection

Filter candidates using indisputable structural constraints: valid ID, available version at the prefix, allowed role type, correct source scope, and quantity dimensions. Preserve rejected candidates with reason codes for candidate-recall analysis. Soft food/form/process compatibility can help rank candidates, but it should not remove a plausible unusual recipe solely because it is uncommon.

After selection, validate cross-question consistency. If a link selects garlic powder while a facet decision claims fresh cloves and no compatible evidence supports that combination, raise a conflict. Do not multiply marginal probabilities and call the result a calibrated joint confidence. Joint consistency and downstream correctness are evaluated separately.

### E.4 Fan-out versus sequential decisions

Independent decisions over an unchanged state can share a call: initial form, explicitly stated size, packing, dry/fresh qualifier, and product/modifier hypothesis. Each question still includes its own `UNSTATED` or unresolved option. Extra questions have token cost; broad batching should be measured against smaller packets rather than assumed optimal.

Dependent decisions require stages. Select a concept before retrieving its compatible portion records; select a process family before supplying family-specific process candidates; resolve an antecedent before querying that entity's allocation. In one fan-out call, a “portion compatibility” question cannot see the answer to the simultaneous “food concept” question. Code must either send all clearly scoped alternatives and reconcile them, or make the second call using the first accepted result.

For large taxonomies, retain a small beam of plausible family paths rather than greedily committing to one family with no escape route. Evaluate total leaf accuracy and unresolved coverage, including family-pruning failures. The 255-option Choice limit [R2] includes escape options; never create a 255-leaf list and then add two more.

### E.5 Supported uses and prohibited shortcuts

| Decision | Jev trial | Open comparator | Required hard boundary |
|---|---|---|---|
| Candidate span label | Choose label or reject candidate | trained span classifier / GLiNER | No new raw boundary created by label selection |
| Food concept | Choose among identical top-K | cross-encoder | Candidate recall reported separately |
| Product/modifier | Choose observable relation type | logistic / encoder | Human review before registry promotion |
| Process mapping | Choose family/specific process | lexical + cross-encoder | Raw verb kept when unmapped |
| Lot/intermediate reference | Choose compatible entity version | recency + learned reranker | Prefix-only and branch constraints |
| Portion-record choice | Choose compatible evidence row | lexical + reranker | Arithmetic and dimensional checks in code |
| Task route | Choose task/category or unresolved | rules / small classifier | Sufficiency evaluated against actual required fields |
| Evidence relevance | Rank supplied rows | hybrid retrieval + cross-encoder | Condition compatibility independently checked |
| Claim support | Flag support/contradiction | deterministic numeric checks + human benchmark | A passed guard is not proof of scientific validity |

Use Choice for unordered event types and nominal heat categories unless the annotation contract genuinely defines an ordered rubric. A Score's expected level is not a stove temperature or duration. A Noul score about whether a step is missing remains a proposal score; it never writes an event into the source graph.

### E.6 Calibrating each decision family

Start with an interpretable logistic correctness model using a small, predeclared feature set: top probability, margin, normalized entropy, candidate count, retrieval rank/score, exact-alias indicator, and a few compatibility/source flags. With very little data, a flexible isotonic model may overfit; compare it only when support permits. Separate correctness calibration from multiclass distribution calibration and state which target is being estimated.

For Choice, the documented confidence statistic is a transformation of top probability and option count. Score uses a different dispersion measure, and Noul does not return a separate confidence field [R3]. The raw distributions and option count are retained, so a changing answer space can be audited. A threshold learned for four candidates is not assumed stable for twenty.

Use a calibration-fit pool for fitting and a separate policy-validation pool for selecting/validating the route. If resources permit only one small calibration pool, use grouped cross-fitting for development diagnostics and refrain from claiming a strong risk guarantee. Test the frozen policy once on sealed recipes. Recalibrate after model, prompt, candidate-generator, registry, or language-view changes.

### E.7 Economic calculation and measurement

The planning equation is `input_tokens / 1,000,000 × current_input_price`, plus upstream retrieval, local compute, network/retry cost, and human review. At the currently documented rate, a hypothetical 1,000-input-token call costs $0.000042; 120 million tokens cost $5.04, and 1.2 billion cost $50.40. These are arithmetic scenarios, not an invoice or an estimate of total system cost.

Question text, concept definitions, and option descriptions contribute to input tokens. A five-question batch is not automatically five times the state size, but neither is it free. Log actual `usage`, request count, accepted decision count, and review minutes. Measure decisions per accepted recipe rather than only API dollars per raw recipe.

Theoretical time is bounded by both request and token rates, and can be worsened by latency, concurrency, backoff, access limits, and retries. The original 50-minute/8.3-hour estimates describe an idealized request-count lower bound at a published rate. They should not be committed as a delivery schedule. Small benchmark sweeps can estimate achieved throughput before any 10k/100k run.

### E.8 Robustness and adoption gate

The provider documents weaknesses in numbers, counting, negation/scope, indirection, and noisy state [R5]. Build probes for “do not drain”; “only the reserved half”; “remaining butter” with two lots; Hindi/transliterated aliases; a long recipe with irrelevant containers; and recipe text that attempts to alter the decision instructions. Numeric parsing, sums, comparisons, and conversions remain code operations.

Release a fixed development probe pack, plus a held-out probe pack. Evaluate clean and perturbed examples paired by recipe family. Report false acceptance of a wrong option, unresolved rate, and coverage; a robustness improvement achieved by abstaining everywhere is not sufficient.

Jev is adopted per decision family, not for the whole compiler at once. Require a useful risk–coverage tradeoff against the open baseline, reproducible request/response logging, acceptable latency, and no unresolved contract violation. If it fails reference resolution but helps concept selection, use it only for concept selection. A timeout or unavailable account falls back to the open selector or unresolved route with the reason visible in logs.

## Appendix F. Rigorous evaluation: split design, metrics, claims, and comparison artifacts

### F.1 Three evaluation tracks

Keep legacy reproduction, the new compiler benchmark, and downstream RAG evaluation separate. Legacy reproduction asks whether a published experiment can be matched. The compiler benchmark asks whether food concepts, entity lineage, and symbolic quantities are represented correctly under the new contract. RAG evaluation asks whether that representation improves answers. A model can improve one and harm another, so there is no single combined “SOTA score.”

For every experiment record: hypothesis; primary metric; practical minimum effect; data/split hashes; eligible universe; baselines; fixed and tuned components; tuning budget; seed list; uncertainty method; cost definition; and a claim template. Choose the metric and tuning scope before final test. Exploratory comparisons remain useful, but are labeled exploratory and do not receive the same confirmatory claim.

### F.2 Split hierarchy and calibration partitions

| Partition | Purpose | Allowed changes after viewing outputs |
|---|---|---|
| Design pilot | Manual/schema/tool development | Broad changes; never a final test |
| Train / Gold-Light | Supervised fitting and exemplar datastore | Training changes logged |
| Development | Architecture, prompts, hyperparameters, error analysis | Bounded model selection |
| Calibration-fit | Correctness-probability fitting | Only predeclared calibration fitting |
| Policy-validation | Threshold/policy assessment | Select among predeclared policies; protect a fresh validation if repeated |
| Sealed natural test | Confirmatory performance under target sampling | No tuning |
| Sealed challenge test | Diagnostic rare/ambiguous behaviors | No tuning; separate headline |
| External benchmark | Transfer under its published contract | Own splits/scorer preserved |

The original 100 seed recipes cannot simultaneously be a full supervised training set, unconstrained development set, calibration fit set, and policy-validation set. A proposed resource-limited allocation is 60 development/training-support, 20 calibration-fit, and 20 policy-validation recipes, all family-disjoint. This is a pilot allocation, not enough evidence for a 1% risk guarantee across subgroups. Use external training corpora and Gold-Light to conserve Deep Gold. A larger long-term calibration pool is needed for stronger claims.

The 100 sealed recipes at A2 and 40 of them at A4 remain the target if throughput permits. Sealed A2 does not imply A4 edges are annotated on the remaining 60. If the minimum path uses smaller sets, publish the actual supports and narrow the claims. Do not tune on the sealed set to rescue a missed target.

### F.3 Families, source shift, and conflicting holdouts

Build a derivative-family graph using raw hashes, normalized hashes, ingredient/instruction signatures, and near-duplicate candidates. Review borderline matches. Numbers may be masked for a derivative audit, but two recipes with the same verbs and different foods are not automatically duplicates. Family-level grouping should be defensible, with manual sampled precision of the grouping rule.

Distinguish derivative holdout, source holdout, dish-family holdout, ingredient-concept holdout, and region holdout. They test different generalization problems. Do not enforce all simultaneously without checking whether the remaining train/test distributions are meaningful. Publish the held-out dimension and support. S1–S6 are overlapping flags: a simple Indian recipe can also be unit-heavy. Report multi-flag intersections only with adequate support.

Translations, augmentations, teacher labels, and retrieval examples inherit the original family's partition. Ontology cards may be shared across partitions as external knowledge under a frozen snapshot, but recipe-specific Gold test examples cannot enter the retrieval datastore. Scientific studies use a separate study-family split; a recipe-family split does not prevent duplicate experimental measurements.

### F.4 Metric definitions

| Task | Primary metric | Essential companion measures |
|---|---|---|
| NER | strict raw-span micro-F1 and per-label F1 | benchmark-native score; macro definition; support; discontinuous policy |
| Facets | accuracy/F1 on eligible matched mentions | all-pipeline facet correctness and unstated precision |
| Concept candidates | Recall@K including allowed target IDs | empty/invalid candidate rate; head/tail/source support |
| Concept selection | Acc@1 on complete eligible set | conditional-on-candidate accuracy; risk–coverage; no-candidate precision |
| Product factorization | boundary/relation correctness | wrong merges; unnecessary concept fragmentation |
| Lot alignment | exact lot/entity binding | unresolved accuracy; two-lot challenge; intermediate accuracy |
| Event extraction | predicate + typed-role F1 | explicit/implicit roles; condition/negation/branch accuracy |
| Flow graph | typed-edge F1 under fixed node alignment | Gold-node and predicted-node tracks; node failures |
| Quantity structure | AST exact match after canonical equivalence | range, package, open, alternative, qualitative supports |
| Conversion route | correct compatible evidence-route rate | unsupported accepted routes; grounded coverage |
| Numeric conversion | dimension-aware exact tolerance | food-specific error, interval coverage, interval width |
| Allocation | parent/fraction/basis correctness | double-spend; remainder correctness; unknown correctness |
| Replay | snapshot field accuracy plus invariant pass rate | invalid transaction count; abstained/blocked steps |
| Sufficiency | route accuracy on task-specific reference | false-ready, unnecessary-clarification, supported coverage |
| Retrieval | graded nDCG and supporting-evidence Recall@K | wrong-basis/process evidence; citation diversity; stale-version rate |
| Answers | supported task-success rate | numeric/reference errors; justified abstention; useful coverage; cost |

AST equivalence should tolerate representationally equivalent exact expressions, such as `1/2 × 200 g` and `100 g`, when they retain the required parent lineage. It must not treat a rounded estimate as equivalent to an exact source amount. Node alignment should use mentions, event anchors, lot distinctions, and permitted structural intermediates; matching solely by canonical food IDs would merge distinct onion lots.

### F.5 Risk budgets and zero-error evidence

For a fixed accepted-decision policy, report observed accepted error `errors / accepted`, coverage `accepted / eligible`, and an uncertainty interval. The error event is defined per task: wrong food identity, wrong portion record, wrong antecedent, or unsupported numeric claim. A schema-valid but semantically wrong answer is an error.

Under independent Bernoulli decisions and a fixed policy, zero errors in n accepted decisions gives a one-sided 95% upper bound `1 - 0.05^(1/n)`. The familiar counts are 149 for below 2%, 299 for below 1%, and 598 for below 0.5%. These are illustrative independent-decision requirements. Multiple decisions in one recipe/source can be correlated, and threshold search can invalidate a simple fixed-policy interpretation. Do not plug the raw mention count into the formula and claim a recipe-distribution guarantee.

A recipe-cluster bootstrap is useful for ordinary uncertainty, but with zero observed errors it cannot invent an unseen-error upper tail: every resample still contains zero errors. For rare-error assurance, obtain enough independent evaluation units and use an explicit clustered/hierarchical risk model or a conservative unit-level loss with justified assumptions. State the unit and assumptions. When evidence is insufficient, report the risk target as unvalidated and keep human review for the strict route.

The 1% quantity budget is a wrong/unsupported accepted-route target, not a requirement that estimates be within 1% of measured mass. Numeric measurement error and evidence-route error are different. Compare systems at matched coverage or report a risk–coverage frontier; a system that grounds only obvious gram quantities cannot claim to solve household measures solely because its error is low.

### F.6 F1 uncertainty, seeds, and multiplicity

The binomial approximation `n ≈ z² p(1-p) / margin²` gives about 384 independent observations for a proportion near 0.90 with ±0.03 at 95%. F1 combines precision and recall, depends on predicted and true support, and changes with the error pattern. Plan F1 support through a pilot-based simulation or resampling study; report achieved intervals rather than asserting a universal required count.

For model differences, resample recipe/derivative-family clusters with both systems' predictions kept paired. Preserve the target sampling design, including source strata where appropriate. Training seeds are another uncertainty source; report per-seed results and a predeclared aggregation. With limited compute, use three seeds for the main trained comparison and fewer diagnostic runs only when labeled as such. No fixed seed-noise band is assumed.

Designate one or a small number of primary comparisons. Use an appropriate multiplicity adjustment or clearly mark secondary p-values exploratory. Report effect size and interval; statistical significance without a useful effect is not a compelling compiler contribution. Equivalence/non-inferiority requires a predeclared margin and adequate power; “not significant” does not demonstrate equivalence.

### F.7 RecipeDB3 reproduction and audit checklist

The supplied attachment reports ingredient macro/micro scores, instruction scores, test-selected checkpoints, omitted SIZE evaluation, and exact/number-masked overlaps. These remain [A-code] leads. Reproduction requires a commit hash, complete raw-file hashes, row counts, label inventory, tokenization, split indices, augmentation-parent mapping, environment lock, training configuration, checkpoint selection, metric implementation, and predictions.

Reproduce the original protocol first as an artifact-level reproduction, clearly stating if the test was used for checkpoint selection. Then run a clean protocol for both the released baseline and our system: group derivatives before splitting; use train/dev/test; select checkpoints on dev; score all declared labels; keep the same allowed text information; report original and standard metrics. Differences are protocol findings, not allegations about authors.

| Reported lead | Independent verification artifact | Permitted claim before rerun |
|---|---|---|
| 26,444 ingredient phrases | raw-file count and checksum | attachment-reported count |
| macro 0.9557 / micro 0.9603 | prediction file plus scorer output | notebook result reported by attachment |
| SIZE absent from score table | label supports and scorer/config audit | issue to investigate |
| test checkpoint selection | training/evaluation code path plus logs | potential protocol issue, not established here |
| exact overlap 5.1% | split IDs plus exact-normalization implementation | provisional percentage |
| number-masked overlap 13.6% | masked canonical text + pair examples | provisional derivative indicator, not proof every pair leaks |
| NAME overlap 70.4% | extracted name rules, train vocabulary, test denominator | provisional head-coverage statistic |
| 10k instruction value lists | files, columns, raw-to-span projection | annotation-format lead |

There is no requirement to get the lab's model score to fall. A grouped split can change difficulty in either direction. The useful output is an honest matched comparison with error analysis and reproducible artifacts. If the exact release cannot be accessed, keep this experiment pending and continue the compiler on accessible data.

### F.8 Matching RecipeDB2 linking and quantity coverage

The cited RecipeDB2 manuscript's linking result concerns a top-200 ingredient evaluation and its unit-coverage result concerns a particular frequent ingredient–unit-pair universe [S2]. A direct numerical comparison requires the same target ontology/data release, allowed candidates, gold mapping policy, item universe, unit conventions, and evaluation weighting. A higher percentage on our smaller, easier pair set is not a win over the published percentage.

Report three coverage denominators: source-present quantity expressions; eligible expressions requiring food-specific grounding; and expressions with an accepted compatible route. Also report distinct pair coverage versus mention-weighted coverage. Directly stated grams should be separated from household volume/count measures. “To taste” is not a failed mass conversion if the task contract excludes qualitative amounts from numeric grounding.

The manuscript states that its generated/analyzed datasets are not publicly available due to institutional copyright restrictions [R14]. Access-dependent reproduction is therefore conditional. If its exact evaluation pairs are unavailable, publish our task specification and baseline results, cite the reported context, and avoid “we beat 43.90%” or “we beat 79.50%” language. The core contribution remains testable on our independently defined benchmark.

### F.9 Oracle cascade and error attribution

Run each key downstream stage with Gold upstream inputs and with predicted inputs. The difference identifies whether errors come from span detection, concept selection, lot binding, event parsing, or quantity grounding. A quantity-ledger failure may originate in an incorrect food link; report both the proximal failure and root-cause annotation.

For RAG, compare predicted compiler state, Gold compiler state, and a no-compiler retriever with the same answer model/evidence budget. Gold-state performance is an upper bound for this pipeline under the benchmark, not a deployable result. Likewise, graph-edge F1 on Gold entities is not full predicted-pipeline graph F1; the r-FG published score must be matched to its exact track before comparing [R13].

### F.10 Experiment ordering and stop rules

| Gate | Run now | Promote only if | Stop / redesign if |
|---|---|---|---|
| Annotation | E0 | label decisions observable; throughput known | disagreements show an incoherent schema |
| Baselines | accessible E1 + E3.1 + E6.1/E6.4 | scorer/offset adapters pass | reproduction mismatch is unexplained |
| Core flow | E4 + E6.3 | state packet adds useful value or exposes fixable failures | ledger depends on invented values |
| Structure | E5 | errors remain that role/path features could address | no gain over strong contextual baseline |
| Selective policy | E9 | useful coverage and documented uncertainty | rare errors unsupported by calibration sample |
| Jev | E14.1–E14.3 first | equal-risk utility/cost justifies adoption | confidently wrong on key domain cases |
| RAG | E10/E11 | same-model comparison shows supported utility | extra tokens alone explain the gain |
| Silver scale | E7 then E8 | audited accuracy and marginal dev gain | noise/coverage drift or review cost overwhelms gain |
| JEPA | one J experiment | core gates passed; matched budget baseline exists | no meaningful dev gain after one bounded round |

## Appendix G. Scientific evidence, missingness, and the completion boundary

### G.1 Evidence-row granularity

A scientific row is one measurement or a clearly defined aggregate from one study, with food/matrix, initial form/state, process, conditions, analyte/target, measurement unit, basis, method, uncertainty where reported, and source table/span. It is not one sentence mentioning a food chemical. Several rows from the same table remain one study family for splitting and uncertainty; a thousand extracted rows may contain far fewer independent experiments.

DEL-1's proposed 1,000 public rows and 40 verified rows are acquisition targets. The first scientific pilot should favor fewer fully traceable anchor studies over a large noisy extraction pool. Record whether a “verified” row means source transcription checked, food/process alignment checked, or scientific comparability assessed. These are different verification tasks.

### G.2 Compatibility is a conjunction of required fields

Numeric evidence joins require compatible food/product, part, form, edible/dry/wet basis, process family, relevant conditions, and measurement target. Some fields can be task-irrelevant; define that contract explicitly. A frying study does not automatically support boiling. Fresh garlic and garlic powder do not share a portion-density record merely because both map to garlic lineage.

Unknown metadata is neutral for candidate discovery, but it cannot satisfy an evidence requirement for a quantitative claim. Retrieval can surface a study with an unknown cooking temperature; the claim gate can still reject using it for an exact temperature-conditioned effect. A high vector score cannot make the missing condition present.

### G.3 Missingness taxonomy and completion experiments

Scientific gaps can arise because a measurement was not performed, not reported, below detection, not extractable, incompatible with our basis, or outside the study domain. An observation mask alone does not identify MCAR/MAR/MNAR. Profile availability by study, food, process, target, and conditions; describe likely selection mechanisms as hypotheses unless supported.

DEL-2 completion is tested on study-disjoint holdouts and explicit cold dimensions: held-out food/product, process, food×process pair, region/source where relevant, and target conditions. Split before normalization/imputation. Features must exclude held-out target values and leakage through duplicate study tables. Randomly masking observed cells is an easier benchmark and does not establish performance on genuinely unmeasured intersections.

Compare simple means/hierarchical priors, nearest compatible evidence, regularized regression/LightGBM where appropriate, and one completion model. Propensity weighting requires a justified observation-probability model and overlap; it does not automatically remove MNAR bias. Report sensitivity to plausible missingness scenarios and model assumptions. Uncertainty from a predictive model is not evidence that an absent measurement occurred.

### G.4 Scientific answer classes

| Class | Allowed output | Required grounding |
|---|---|---|
| Observed study result | Report measurement under its stated conditions | verified row and source |
| Deterministic derived result | Unit/basis calculation from compatible measured inputs | complete derivation and inputs |
| Model estimate | Clearly labeled prediction with applicable-domain limits | trained model card and evaluated uncertainty |
| Scenario / assumption | Conditional result if declared assumptions hold | assumption IDs and sensitivity |
| Qualitative procedural statement | Source/evidence-supported direction or instruction | relevant text/evidence, no invented number |
| Unsupported / conflicting | State missing critical evidence or conflict | explicit reason and affected task |

Level-15 or FlavorTwin estimates consume the scientific registry under their own gates; they never write source recipe temperatures, Gold labels, or observed-session chemistry. A recipe compiler improves evidence matching and applicability, but does not by itself solve causal process effects.

### G.5 Claim ledger and numeric check

Before final verbalization, construct claims with `claim_type`, statement, supporting assertion/evidence IDs, calculation ID, applicability status, provenance, and limitations. Numeric claims are checked against stored values and deterministic derivations, including units/basis and rounding. Citation support and condition compatibility are separate checks: a citation can mention the topic while failing to support the number.

A Jev/LLM support guard can flag semantic mismatch but cannot replace a verified numeric route. Test it on missing conditions, contradictory units, wrong food forms, measurement-basis changes, and a correct citation attached to an unsupported extrapolation. Evaluate false alarms as well as missed unsupported claims.

## Appendix H. Capacity-aware work plan and synchronized execution

### H.1 Scope levels

| Level | Annotation/data scope | Model scope | Defensible output |
|---|---|---|---|
| Core minimum | 20 design recipes; smaller family-disjoint seed/calibration and sealed pools; 20 A4 sealed cases if feasible | one accessible NER baseline, lexical/hybrid linker, recency + state resolver, quantity grammar | working compiler with honest support counts and diagnostic uncertainty |
| Target | original 100 seed + 100 sealed at A2; 40 A4 in each; external benchmarks | strong trained NER challenger, cross-encoder, one frontier teacher, optional Jev | matched compiler/RAG comparison with source/complexity diagnostics |
| Stretch | 300 recipes or added Gold-Light; 10k audited Silver | kNN/exemplar layer, broader Jev families, one structural ablation | tail/cost studies and scale evidence |
| Long-term | 750–1,000 Deep Gold, 3–5k Gold-Light, staged 60–100k Silver | broader sources, better calibration, scientific completion if justified | stronger risk evidence and deployment-oriented coverage |

The core minimum is not an automatic approval for tiny, overstated experiments. Choose its actual sample sizes from the pilot and publish them. A small sealed set can support a useful case study, but cannot carry universal rare-error or regional generalization claims.

### H.2 Annotation capacity arithmetic

For the original target, suppose 200 recipes receive independent A2 annotation by two people, 80 of them receive an additional A4 pass by both, and 20 separate design-pilot recipes receive both depths. Let `t2` be A2 minutes per annotator, `t4` additional A4 minutes, `a2/a4` adjudication minutes. Estimated annotation hours are:

`[400 t2 + 160 t4 + 200 a2 + 80 a4 + 40(t2+t4) + 20(a2+a4)] / 60`.

| Hypothetical throughput | A2 min | additional A4 min | A2 / A4 adjudication min | Target annotation hours |
|---|---:|---:|---:|---:|
| Fast | 15 | 35 | 5 / 10 | about 262 |
| Central | 25 | 60 | 10 / 20 | about 453 |
| Slow | 40 | 90 | 15 / 30 | about 698 |

These are planning scenarios, not observed annotation times. They exclude literature acquisition, implementation, model training oversight, review-tool setup, and the scientific ledger. Two people at 15 hours/week each for 12 weeks have 360 total person-hours; at 20 hours/week each they have 480. The central annotation scenario would consume almost all of that. The original plan is therefore a target gated by measured throughput, not a promise.

Options are to reduce A4 depth on development recipes, use Gold-Light for training-support fields, reuse permitted external benchmarks, narrow model breadth, or extend the schedule. Preserve independent sealed annotation and the common evaluator before spending effort on 100k Silver or several JEPA variants. Track active annotation time separately from tool/model waiting time.

### H.3 Ownership without assigning people prematurely

Track A owns source manifests, annotation contracts, vocabulary review, and data cards. Track B owns adapters, compiler/replay implementation, evaluation, and RAG. Both annotate independently for Deep Gold. Each work package has one implementation owner, one reviewer, dependencies, output hashes, and an exit decision. Assign the named team members when actual availability is known; the plan does not assume one person can annotate while simultaneously reviewing the other person's code at full capacity.

Use a shared issue format: issue ID, source/record, task, source evidence, expected behavior, actual behavior, root-cause stage, severity, reviewer, fix revision, and regression fixture. Link an issue to a task or experiment rather than losing it in chat. This gives Claude Code bounded implementation packets and keeps the team synchronized around the same schema.

### H.4 Revised first ten working days

| Day | Concrete work | Exit artifact |
|---|---|---|
| 1 | Freeze goals, task families, evidence policy, source manifest, and core schema proposal | decision register + manifest template |
| 2 | Choose source-diverse pilot; create derivative-family candidates; define offset conventions | 20 pilot IDs + family audit sample |
| 3 | Import into one annotation tool; test critical relations and export; try second tool only on a representative subset | tool capability/time record |
| 4 | Independently annotate initial pilot cases; write first boundary/product/quantity decisions | manual v0.1 + disagreement log |
| 5 | Implement reversible views, quantity AST parser, alias baseline, strict no-density adapter | offset/quantity fixtures |
| 6 | Finish pilot annotation and adjudication; compute agreement and capacity | E0 report + scope decision |
| 7 | Freeze initial splits and accessible benchmark adapters; establish common scorers | split hashes + baseline contract |
| 8 | Compile three hand-checked flow recipes; implement entity versions and allocations | deterministic replay demo |
| 9 | Build identical concept candidate sets for open selector/Jev adapter; define calibration-fit/policy pools | candidate snapshot + decision contract |
| 10 | Run development smoke benchmark; classify failures; freeze next two-week backlog | error taxonomy + W3/W5 plan |

Access requests may be drafted, but sending them is a separately authorized action. Late APIs do not block source-first pilot work. If exact CoSyLab artifacts are accessible, start reproduction in parallel within the team's capacity; otherwise mark that branch blocked, not the entire project.

### H.5 Twelve-week target with explicit critical path

| Weeks | Critical-path work | Optional parallel work | Gate |
|---|---|---|---|
| 1–2 | W0/W1, E0, offset/AST/alias slice | accessible legacy reproduction | G-DESIGN: schema representable, throughput measured |
| 3–4 | seed annotation; concept candidates; quantity adapter; common scorer | RecipeBERT-KA or GLiNER challenger | G-BASE: shared data/scorer and no unsupported conversion |
| 5–6 | events, references, entity versions, allocations; calibration pools | E14.1–E14.3 if access exists | G-FLOW: replay and unresolved cases correct |
| 7–8 | sealed annotation/adjudication; RAG index/chunk pilot; retrieval labels | 1k Silver economics pilot | G-EVAL: splits frozen, models/policies selected on dev |
| 9–10 | E10/E11, controlled retrieval/prompt ablations; subgroup diagnostics | expand audited Silver to 10k if justified | G-UTILITY: supported task utility measured |
| 11 | final predeclared runs, oracle gaps, cost/latency, confidence intervals | one JEPA development pilot only if core complete | G-RESULTS: claims match evidence |
| 12 | report, data/model/evidence cards, reproducible demo and release bundle | presentation polish | G-RELEASE: artifacts traceable and rerunnable |

Moving the sealed annotation earlier reduces the risk of running out of time to create an honest final test. Its contents stay hidden from model/prompt development. A person who annotates test labels should not use those recipes as examples in a model-selection conversation. Log access to the sealed artifacts.

### H.6 Claude Max work packets and synchronization

Every coding packet has: objective, relevant schema/manual extracts, accepted input/output examples, affected modules, protected artifacts, validation criteria, and a stopping condition. It should not contain the entire 42k-line SSOT. Claude Code is particularly useful for adapters, converters, scorers, migrations, and fixtures; model-produced annotations still follow their verification tier.

Every annotation packet records source IDs, label masks, candidate registry version, prompt/model ID, assistance visibility, validator flags, and review outcome. Use one extraction and one targeted repair, then stop for review/unresolved. Subscription capacity is measured, not treated as a fixed recipe allowance. Keep API billing and subscription usage separate in cost reports.

At each weekly checkpoint, publish accepted artifacts, unresolved decisions, measured time, benchmark status, and the next critical-path package. Changes to a shared contract are merged before downstream teams generate more data. This prevents one track from using a new quantity basis while another still evaluates the old fields.

### H.7 What to cut and what to protect

Cut optional model breadth, Silver beyond the audited pilot, graph encoders, full JEPA experiments, broad ontology drift studies, and multimodal deployment first. Protect raw/source preservation, offset integrity, independent final labels, quantity evidence routes, prefix evaluation, common scorers, and one controlled compiler-to-RAG comparison. These are the foundations of the claim.

If annotation throughput forces a smaller dataset, adjust experiment power and headline scope before final runs. If the compiler does not improve RAG, release the error analysis and useful semantic/quantity benchmark rather than manufacturing an end-to-end win. Negative results about Silver, Jev, or structural retrieval can still inform the final architecture.

## Appendix I. Acceptance fixtures, release gates, and reviewable outputs

### I.1 Required deterministic fixtures

| Fixture family | Expected behavior | Failure it catches |
|---|---|---|
| Unicode/view offsets | source round-trip for fractions, Hindi, emoji | shifted labels and false evidence spans |
| Product identity | sour cream/cream cheese/stock/paste remain meaningful | destructive modifier stripping |
| Alias ambiguity | dhaniya/corn flour can remain unresolved | global nearest-alias coercion |
| Two same-food lots | distinct butter/onion lots retained | canonical-ID-only coreference |
| Quantity alternatives | “500 g or 1 cup” remains alternative/conflict | accidental 500 cups |
| Package/drained basis | package grams do not become drained grams | basis fabrication |
| No density evidence | flour cup mass remains unknown | water-density default |
| Nested split | half of reserved half = quarter of source | wrong parent scope |
| Correlated split | recombined children recover shared source uncertainty | independent-source double variance |
| Negated action | “do not drain” makes no discard transaction | positive verb replay |
| Conditional branch | optional water added only in executed branch | both alternatives counted |
| Reserved reference | supported later use can access reserved portion | unnecessary retrieve requirement |
| Used-after-discard | rejected transaction or source conflict | impossible lineage |
| Initial chopped form | no invented explicit chop event | source history fabrication |
| Planned endpoint | “until golden” remains planned | false observed doneness |
| Unknown quantity | symbolic lineage retained | null-to-zero conversion |
| Evidence incompatibility | wrong form/process/basis cannot support numeric claim | high-similarity evidence misuse |
| Snapshot change | dependent answers invalidated after quantity correction | stale retrieval/state cache |

These fixtures are synthetic/manual cases for software validation, not a replacement for natural Gold evaluation. The implementation can use ordinary unit/property tests for arithmetic and replay invariants; the document itself does not claim those tests have been written or passed.

### I.2 Eight end-to-end demonstration scenarios

1. Ingredient-line parsing with a product and preparation facets.
2. Hinglish alias ambiguity resolved or preserved with a reason.
3. Nested reserve/split and a symbolic remaining fraction.
4. Two lots of the same food, including an unresolved reference.
5. Packaged drained ingredient with unknown edible mass.
6. Planned endpoint versus a contrary live-session observation.
7. Scientific evidence retrieved but rejected for incompatible conditions.
8. A correct abstention/clarification that enables a supported answer after new evidence.

Each demo includes raw text, accepted claims, graph/ledger view, evidence IDs, unresolved fields, and a replay hash. Add a hidden evaluation variant for each scenario so the demo is not the only evidence of robustness.

### I.3 Release gate checklist

The release bundle contains: schema/manual versions; source and split manifests; concept and unit snapshots; legacy adapters; actual annotation counts and masks; independent agreement before adjudication; assistance log; model/prompt/index manifests; predictions and decision caches where permitted; metric code/configuration; cost/time definitions; oracle gaps; error taxonomy; risk–coverage results with uncertainty; and claim limitations.

No “first,” “SOTA,” “guaranteed ≤1%,” or “chemistry predicted from recipe text” claim is included unless the corresponding novelty/comparison/statistical/evidence gate is supported. A useful release can state that the target was not met. Unsupported numeric conversions accepted by the deterministic adapter must be zero on its exhaustive software fixtures and audited benchmark; any observed violation blocks that route until fixed.

### I.4 v14 adoption and migration

Prepare an additive migration table: old field/enum, new field/enum, mapping rule, information loss, affected records, re-adjudication requirement, and validation query. Internal concept IDs remain stable where meaning is unchanged. A split/merge creates explicit replacement relations rather than reusing an old ID with a new meaning. External ontology updates create new mapping revisions.

Adopt the compiler schemas only after a pilot round-trip and a representative migration sample. Do not mark Level-12–15 execution gates complete merely because fields exist. FlavorTwin consumes accepted canonical products/forms and entity states; scientific condition-dependent outputs remain tied to DEL-1/DEL-2 evidence gates.

## Appendix J. Current primary-source review and audit status

This registry supplements S1–S72 without pretending every inherited item was re-executed. `[R]` means a primary/official page was checked during this review. A paper abstract verifies its described task and headline claim; it does not verify the released code or reproduce the score. Proposed design decisions in Appendices B–K are our hypotheses/contracts unless explicitly described as source facts.

| ID | Primary source | Checked fact / limit |
|---|---|---|
| R1 | [TypeSafe model documentation](https://docs.typesafe.ai/models) | Current Jev version, price, input/limits, customization, language; no recipe benchmark |
| R2 | [TypeSafe Choice](https://docs.typesafe.ai/primitives/choice) | Supplied options, distribution, 255-option limit, independent fan-out |
| R3 | [TypeSafe confidence](https://docs.typesafe.ai/confidence) | Choice and Score differ; Noul has no separate confidence |
| R4 | [TypeSafe API](https://docs.typesafe.ai/api) | State/question/answer contract; no calls made here |
| R5 | [Jev 1.13 documented weaknesses](https://docs.typesafe.ai/model-jaggedness/jev-1.13) | Numbers/counting and other robustness concerns |
| R6 | [Knowledge-augmented recipe token classification, EACL 2026](https://aclanthology.org/2026.eacl-long.127/) | Reported best results on five of seven recipe datasets; required matched challenger |
| R7 | [ReciFine, Findings EACL 2026](https://aclanthology.org/2026.findings-eacl.210/) | Large automatically extracted corpus plus human evaluation benchmark; not millions of human Gold recipes |
| R8 | [JFC-Recipe, LREC 2026](https://aclanthology.org/2026.lrec-1.504/) | Japanese food-item linking and amount/weight annotation precedent; corrected Anthology URL |
| R9 | [GLiNER2.5 provider description](https://fastino.ai/blog/gliner2-5-span-free-information-extraction) | Schema extraction/boundary approach; domain accuracy untested here |
| R10 | [GLiNER2.5-Decide provider description](https://fastino.ai/blog/gliner-2-5-decide-open-weight-decision-model) | Open-weight decision comparator; pin actual card/checkpoint/license |
| R11 | [kNN-NER](https://arxiv.org/abs/2203.17103) | Training-example retrieval for NER; no automatic recipe-domain gain |
| R12 | [RENER](https://arxiv.org/abs/2410.13118) | Retrieval-enhanced demonstrations; CrossNER results do not transfer numerically to recipes |
| R13 | [Fan and Hunter, recipe flow graphs](https://aclanthology.org/2023.findings-acl.261/) | Graph/edge result; exact upstream-input/scoring track must be audited |
| R14 | [RecipeDB2 manuscript](https://arxiv.org/html/2609.22099v1) | Linking/coverage context and restricted data-availability statement; preprint |
| R15 | [Ingredient Parser conversion documentation](https://ingredient-parser.readthedocs.io/en/latest/how-to/convert-units.html) | Default water density for mass/volume conversion; wrapper must require explicit evidence |
| R16 | [Indian recipes dataset, Mendeley](https://data.mendeley.com/datasets/xsphgmmh7b/1) | Hindi entries and googletrans fields; repository lists CC BY 4.0; original source lineage retained |
| R17 | [Order-based pretraining, NAACL 2024](https://aclanthology.org/2024.naacl-short.74/) | Procedural/entity-tracking objectives, including embedding regression; recipe baseline for J studies |
| R18 | [Universal NER v2, LREC 2026](https://aclanthology.org/2026.lrec-1.525/) | Multilingual NER context; not a recipe-specific Claude result |
| R19 | [LLM-JEPA](https://arxiv.org/abs/2509.14252) | Latent-prediction language-training research; not a Jev product or recipe result |
| R20 | [Var-JEPA / Var-T-JEPA](https://arxiv.org/abs/2603.20111) | Tabular representation research; scientific-gap completion remains unproven here |
| R21 | [V-JEPA 2](https://arxiv.org/abs/2506.09985) | Video prediction/planning research; future observation track |
| R22 | [Gemini Embedding 2 model page](https://deepmind.google/models/gemini/embedding/) | Current multimodal embedding offering; availability and model details checked 3 October |
| R23 | [Gemini embedding API documentation](https://ai.google.dev/gemini-api/docs/embeddings) | Model-specific task instructions, dimensionality, and aggregation behavior |
| R24 | [Gemini Embedding 2 technical report](https://arxiv.org/abs/2605.27295) | Unified multimodal representation/retrieval results; no CulinaryState test |
| R25 | [Gemini 4 Argon announcement](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/) | 30 September announcement and restricted initial rollout; no assumed project access |
| R26 | [Google Research, Titans + MIRAS](https://research.google/blog/titans-miras-helping-ai-have-long-term-memory/) | Neural memory research; no replacement for external evidence records |
| R27 | [Google Research, Nested Learning / Hope](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/) | Continual-learning/memory architecture research; not a turnkey RAG component |
| R28 | [Google DeepMind, AlphaEvolve impact](https://deepmind.google/blog/alphaevolve-impact/) | Evaluator-driven algorithm/code optimization; no recipe-label Gold authority |
| R29 | [M3-Embedding / BGE-M3 paper](https://arxiv.org/abs/2402.03216) | Dense/sparse/multivector retrieval baseline family |
| R30 | [Late Chunking](https://arxiv.org/abs/2409.04701) | Contextual token encoding before chunk pooling; requires suitable model access |
| R31 | [ColBERT](https://arxiv.org/abs/2004.12832) | Fine-grained late interaction; distinct from late chunking |
| R32 | [Anthropic Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | Chunk-specific context for embedding/BM25; source-grounding and cost must be evaluated |

**Pending source audits:** RecipeDB3 commit/data/notebooks; exact original CoSyLab scorers/splits; ReciFine/TASTEset current downloadable release licenses and split artifacts; RecipeDB2 evaluation-pair access; and any precise DeepMind release the user had in mind beyond the candidates covered here. Missing access narrows claims; it does not stop the core compiler.

## Appendix K. Retrieval, embeddings, chunking, prompts, and learning from gaps

*Added in response to the 3 October follow-up. This appendix is the detailed RAG implementation and experiment contract. It distinguishes a structured source of truth from its searchable representations and directly answers what belongs in vectors versus metadata.*

### K.1 Jev, JEPA, and the Google work are different things

| Name | What it is | Useful role here | What it does not establish |
|---|---|---|---|
| **Jev** | TypeSafe's hosted typed-decision model | Candidate concept/label/record selection, optional routing and guards | Correctness on recipes; arithmetic; independent Gold |
| **JEPA** | Joint Embedding Predictive Architecture: a latent-prediction training approach and research family | Optional representation-learning or transition-surprise experiments | A ready recipe parser, database, or RAG service |
| **Gemini Embedding 2** | Google's multimodal embedding model | A retrieval challenger for text and later image/video/document evidence | Exact quantities, food identity, causal chemistry, or measured session state |
| **Gemini 4 Argon** | Newly announced frontier generative/reasoning model | Potential future generator/extractor comparator if accessible | Public project access or a recipe-specific advantage |
| **Titans / MIRAS** | Google Research neural-memory work | Inspiration/research baseline for long-context memory | Auditable external facts or ledger replay |
| **Nested Learning / Hope** | Google Research continual-learning/memory research | A later study of memory/update mechanisms | Safe automatic promotion of new labels or evidence |
| **AlphaEvolve** | DeepMind's evaluator-driven algorithm/code optimization approach | Optional search over measurable retrieval/code configurations | Human annotation authority or discovery of measured food chemistry |

Because no exact Google model was named, this review covers the directly relevant retrieval model, the newest official flagship announcement located, and the related memory/optimization work. These are alternatives to investigate at different layers, not components that must all be combined.

The current Gemini Embedding 2 model page lists general availability, multimodal inputs, an 8,192-token input limit, and flexible dimensions; its technical report evaluates broad retrieval tasks [R22,R24]. The March launch article described public preview, so use current model/API documentation when implementing. The API now documents `gemini-embedding-2`; do not freeze an old `-preview` identifier solely because it appears in a launch example.

Google announced Gemini 4 Argon on 30 September 2026 with an initial rollout to selected cyber defenders [R25]. It is a watch-list comparator until actual access, model ID, cost, and reproducibility are established. The existence of a stronger general model does not remove the need for source/quantity/evidence contracts. Titans/MIRAS and Hope concern memory/learning mechanisms [R26,R27]; keep those as bounded research ideas rather than rebuilding the core around them now.

### K.2 The source of truth is structured; vectors are derived indexes

There are three authoritative planes: immutable source assets; accepted recipe/session records and ledgers; and independently verified scientific evidence. The project SSOT/manual specifies how those planes are interpreted. An embedding is a derived search representation of one versioned view. It is never the sole record of a quantity, citation, food ID, annotation, or state transition.

Maintain distinct index namespaces for concepts, recipe text/events, training exemplars, scientific evidence, and project documentation. A planning document that says “target QUANTITY F1 ≥0.85” must not be retrieved as evidence that the model attained 0.85. A teacher-generated explanation must not be retrieved as a study measurement. Keeping namespaces and epistemic type in the retrieval contract prevents those mistakes.

```mermaid
flowchart TD
    A["Immutable sources"] --> B["Compiler and verification"]
    B --> C["Accepted ledgers"]
    B --> D["Search cards and metadata"]
    E["Verified study evidence"] --> D
    D --> F["Lexical and vector indexes"]
    C --> G["Task and state query"]
    G --> H["Retrieve and check compatibility"]
    F --> H
    H --> I["Evidence and calculation packet"]
    I --> J["Supported claims and answer"]
```

Every chunk/vector points to its source record and revision. The system can resolve a result back to raw text, accepted assertions, or a study table. A deleted/replaced record is excluded through its snapshot/tombstone policy. Retrieval quality and data correctness are separate: a perfect vector search can retrieve an incorrect annotation if the underlying record is wrong.

### K.3 What belongs in embeddings, metadata, and ledgers

| Information | Embedding/search text | Metadata / structured records | Why |
|---|---|---|---|
| Food name, aliases, definitions | Yes, in a concept card | Stable concept ID, alias locale/source, registry revision | Semantic search plus exact identity |
| Product/form/part descriptions | Short meaningful descriptions when relevant | Typed facets with availability/provenance | Similar wording helps discovery; exact compatibility remains inspectable |
| Raw recipe step | Yes, unchanged source text | Recipe/step IDs, raw offsets, source/family | Search result retains evidence |
| Resolved antecedent summary | Optional versioned context prefix | Entity-version ID, evidence cutoff, inferred status | Improves search without disguising the inference as source text |
| Numeric amounts and units | Can appear in source/card text | AST, exact values, dimensions, basis, unit variant | Vectors are unreliable for exact arithmetic/range matching |
| Reserve/split/material lineage | Short event/state summary may be searchable | Typed edges, parent allocations, branch and snapshot | Graph queries/replay supply exact reference history |
| Temperature/duration ranges | Source wording may be embedded | Numeric ranges, missingness, planned/observed | Compatibility and filtering need exact fields |
| Scientific findings | Source-grounded textual description | Value/unit/basis, conditions, study IDs, measurement status | Retrieve meaning; compute/validate from structured evidence |
| Confidence/review status | Usually omit from semantic text | Distribution, calibration revision, verification tier | Numeric confidence is a routing feature, not document meaning |
| Model failures or research findings | Separate project/error-analysis index | Experiment ID, measured/proposed status, split/model hashes | Improves development workflow without polluting food evidence |
| Missing fields | A concise explicit “duration not stated” can be useful | Required availability enum and task mask | Querying gaps is useful; absence must remain exact |
| User's current cooking state | Optional temporary state card | Session observations and entity snapshot | Exact live state is read directly, not approximated by nearest vector |
| Labels used for training | Short label descriptions in training cards | Label/manual version and split/task masks | No sealed-label leakage |

The answer is therefore **both**, with different responsibilities. Embed meaningful language for discovery. Keep facts, IDs, quantities, constraints, uncertainty, and evidence status as structured fields. Supply exact current state and calculations directly from ledgers. Do not concatenate all metadata into one long string and hope cosine similarity preserves every distinction.

For a finding such as “this source's QUANTITY label is weak,” store the measured experiment result in the development registry, and optionally index its explanation for the coding/annotation assistant. For “a study measured a process effect,” create a scientific row and a searchable evidence card. For “this step uses the reserved butter,” create a reference/ledger assertion and optionally a short retrieval card. These three findings have different authority and cannot share an undifferentiated vector collection.

### K.4 Similarity is task-specific, not one universal number

| Similarity | Example | Retrieval/ranking mechanism | Important non-equivalence |
|---|---|---|---|
| Lexical | spelling variants and rare names | BM25, exact alias, character n-gram | Same word can have different food senses |
| Food-concept | fresh tomato versus a described tomato variety | concept cards + dense/cross-encoder | Tomato paste is not interchangeable with chopped tomato |
| Form/product compatibility | packed sugar, chopped spinach | typed metadata plus reranker | Same base ingredient does not imply same density |
| Procedural role | food heated in a medium, then reserved | event signature/path features | Similar procedure does not prove a missing step occurred |
| Referential | “the remaining sauce” to a current lot | active-state candidates + learned resolver | A similar sauce from another recipe is never the antecedent |
| Scientific applicability | same matrix/process/conditions/target | structured compatibility + relevance reranker | Topic similarity does not establish causal transfer |
| Whole-recipe/dish | related cuisine/ingredient composition | coarse recipe embedding + structured overlap | Dish similarity is too coarse for exact quantity evidence |
| Cross-modal | cooking image to relevant state/example | multimodal embedding candidate search | Visually similar food does not prove temperature/doneness |

Define retrieval labels separately for each task. Food linking needs a valid concept target. Evidence retrieval needs support/applicability judgments. Recipe-exemplar retrieval needs helpful training examples. Reference resolution needs a local entity version. A high-performing general embedding can still fail one of these contracts.

Begin with hybrid candidate retrieval and rank fusion, then a cross-encoder or calibrated selector with explicit compatibility features. Raw cosine, BM25, graph scores, and probability are on different scales. Use rank fusion as a simple baseline, or learn a ranker on development relevance labels. Do not select arbitrary hand weights for an impressive-looking global “similarity” score and present it as calibrated correctness.

### K.5 Index types and card schemas

| Index | Retrieval unit | Search card | Hard scope |
|---|---|---|---|
| Concept | one concept/sense | canonical name, aliases, definition, distinguishing product/form facts | frozen registry snapshot |
| Ingredient line | one source line | raw line plus bounded locale/context | source/family/split |
| Event | one atomic event or short dependent event group | raw step plus accepted roles and initial state summary | recipe/version/cutoff |
| Recipe parent | one recipe or component | title, components, coarse procedure | parent for expansion, not sole detailed evidence |
| Exemplar | one labeled training case | input, labels, explanation under manual | training partition only |
| Scientific evidence | one compatible result row with local context | measurement plus food/process/basis/method | verified study/snapshot |
| Study parent | one study section/table | methods, table headers, footnotes | source family and evidence type |
| Development docs | one contract/experiment/issue section | objective, status, findings, linked artifacts | unavailable to scientific-answer retrieval |

Each card has `chunk_id`, `record_id`, `record_revision`, `namespace`, `parent_id`, `raw_source_refs`, `view_text`, `view_hash`, `epistemic_type`, `verification`, `task_mask`, `split/family`, and any exact task fields. The vector record additionally stores model/version, dimension, task instruction, normalization, embedding timestamp, and index snapshot. Keep raw text and generated context in separate fields.

### K.6 Chunking policy by source type

Recipes should be chunked around semantic units: ingredient lines, steps/events, and component boundaries. Never split an amount from its food name or an action from its negation/condition merely to hit a fixed token target. Use small event/line children for retrieval and a bounded parent expansion for coherent context. Whole-recipe embeddings can help coarse discovery but should not replace step-level evidence.

Scientific papers need section-aware text chunks and table-aware evidence units. A measurement row must retain headers, units, footnotes, matrix/process conditions, and its study ID. If a PDF row is OCR-corrupted or a table header is missing, flag extraction uncertainty; no embedding model repairs the measurement's authority. Parent expansion brings methods/context only when needed and under a token budget.

For project SSOT/manual retrieval, chunk by headings and contract boundaries, retaining version and section ID. Do not split enum definitions from their invariants or a migration rule from its affected fields. That index helps the coding workflow; it stays separate from food scientific evidence.

Initial development sweeps can compare 128/256/512-token text children, 0/32/64-token overlaps, and event-boundary chunks with bounded parent context. These are candidate settings, not recommended universal optima. Evaluate retrieval and answer quality under the same final context budget. Overlap creates redundant hits; deduplicate by source span/parent before generation.

### K.7 Contextual prefixes, late chunking, and late interaction

Three different approaches deserve separate ablations:

1. **Structured contextual prefix:** prepend a short compiler-generated context card to the raw step, such as the recipe component, active intermediate, and explicitly marked unresolved/reference information. Prefer deterministic serialization of accepted fields before LLM-generated context.
2. **Contextual Retrieval:** add source-grounded chunk-specific context for embedding and lexical retrieval, as described by Anthropic [R32]. Generated context is stored separately and audited; it never becomes source evidence.
3. **Late chunking:** encode a longer text context at token level, then pool chunk representations, following the research method [R30]. This requires access to suitable token embeddings/pooling behavior, not just a hosted API that returns one pooled vector.

ColBERT-style late interaction is another mechanism: independently encoded query/document token representations interact during ranking [R31]. It is not the same as late chunking. BGE-M3 supplies a useful dense/sparse/multivector baseline family [R29]; model-specific interfaces and licenses must be pinned before implementation.

Online-prefix evaluation imposes a strict cutoff. A step-t embedding produced from the full recipe with late chunking can contain future-step context even if its displayed chunk contains only step t. Build prefix-safe embeddings/cards or use a model/view that cannot ingest future text for that track. Offline full-document indexing is a separate allowed mode. Apply the same distinction to generated contextual prefixes and retrieved state summaries.

### K.8 Embedding model selection and storage

Use at least one reproducible open text-embedding baseline and one stronger hosted challenger if available. BGE-M3 is a relevant open baseline family; Gemini Embedding 2 is the directly relevant Google challenger. Their public benchmark results do not select the winner for recipe linking or sparse scientific applicability. Test raw-text, concept-card, event-card, and evidence-card tasks separately.

Pin checkpoint/API model, tokenizer/task instruction, dimension, normalization, text-view revision, and card template. Queries and documents must use compatible model/task conventions. Vectors from different model spaces cannot be mixed in one cosine index merely because they have the same dimension. A model/card-template change requires re-embedding affected records or a versioned dual-index comparison.

Gemini's current API documentation uses prompt-based task instructions for Embedding 2 rather than Embedding 1's `task_type` parameter, and distinguishes multi-input aggregation from separately embedded inputs [R23]. The adapter must explicitly create one vector per intended retrieval unit; accidentally aggregating several recipe chunks into one vector defeats the chunk contract. Unit tests should assert input count, vector count, and record-to-vector mapping.

Dense float32 storage before index/metadata overhead is `N × dimension × 4 bytes`. For 2 million vectors at 768 dimensions that is 6.144 GB in decimal units; at 3,072 dimensions it is 24.576 GB. Multivector indexes can be much larger. Estimate actual chunk counts from the pilot before scaling. Quantization and dimensionality reduction are candidates to test for recall/latency/storage; do not assume memory savings are accuracy-neutral.

### K.9 Query planning and exact ledger reads

The query planner identifies task type, target food/entity, relevant state cutoff, required quantities/conditions, and acceptable evidence class. It resolves pronouns against the current session/recipe state before external search. It does not search across recipes to determine which local butter “the remaining butter” refers to.

For “how much of the reserved sauce remains,” read the exact allocation ledger and calculate deterministically. External retrieval is unnecessary unless unit/portion evidence is required. For “what does simmer mean in this step,” retrieve relevant process definitions and procedure context. For a process-effect question, build a query from canonical food/product, form, process, conditions, target, and missingness; retrieve evidence broadly, then assess applicability strictly.

Maintain the raw user query and structured query plan. Query expansion may add reviewed aliases/process synonyms, but must not invent missing temperatures or amounts. Multi-query retrieval can improve recall; all expanded terms and their provenance are logged. A synthetic hypothetical answer/query is a retrieval aid, never evidence of the requested finding.

### K.10 Retrieval pipeline and compatibility routing

1. Resolve exact local state/quantity targets and determine which namespaces are needed.
2. Read ledger facts/calculations directly for exact questions.
3. Retrieve lexical and dense candidates from the permitted index snapshots.
4. Fuse and deduplicate candidates; retain source/study diversity.
5. Apply immutable scope/permission/cutoff constraints and explicit semantic incompatibility checks.
6. Rerank with query/card text plus structured compatibility features.
7. Expand only needed parents, headers, footnotes, and state lineage.
8. Assemble an evidence packet with support, conflicts, unknown conditions, and calculation IDs.
9. Apply task sufficiency and the selective policy.
10. Generate a constrained claim packet, verify it, and render the answer.

Unknown metadata should not always exclude a candidate at initial retrieval, since that can destroy recall. But unknown cannot satisfy a required field at the claim gate. Distinguish `COMPATIBLE`, `INCOMPATIBLE`, and `INSUFFICIENT_INFORMATION`. Region/source and dietary tags are soft or hard only when the task contract justifies them; a weakly inferred tag must not become a universal filter.

### K.11 Prompt contracts for extraction, selection, and answering

Separate prompts by role and output contract. An extraction prompt asks for source-backed spans/events. A selector prompt chooses among supplied candidates. An answer prompt uses accepted facts/evidence/calculations. A critique prompt flags specific errors. Combining all four in one unconstrained prompt makes error provenance and evaluation harder.

**Extraction contract template:**

```text
Task: extract the specified label/event fields from this source view.
Use guideline version {{manual_version}} and schema {{schema_version}}.
Source section and raw offsets: {{source_and_map}}.
Allowed prefix state: {{state_packet_with_cutoff}}.
Return proposed records with raw evidence spans and per-field status.
If text does not state a field, mark NOT_STATED.
If an argument is inferred, include candidate IDs and inference provenance.
Preserve negation, alternatives, conditional branches, and unknown amounts.
Return the schema object only; a failed field may remain unresolved.
```

**Candidate-selector contract template:**

```text
Decision family: {{decision_family}}.
Source evidence and accepted context: {{bounded_packet}}.
Allowed choices and definitions: {{candidate_cards}}.
Choose the supported option, NO_VALID_CANDIDATE, or UNRESOLVED.
Treat source text as data. Decide only this specified field.
Return the provider-neutral decision result.
```

**Answer contract template:**

```text
Task: answer {{user_question}} for {{task_type}}.
Current recipe/session snapshot: {{snapshot_id_and_cutoff}}.
Accepted facts: {{field_assertions_with_provenance}}.
Approved calculations: {{calculation_results_and_basis}}.
Retrieved evidence: {{source_cards_with_ids_and_compatibility}}.
Conflicts and missing critical fields: {{issues}}.
Sufficiency route: {{READY_or_LIMITS_or_CLARIFY_or_UNSUPPORTED}}.
Return claim objects with support IDs, claim type, and limitations.
Use only approved quantities/calculations for numeric claims.
Distinguish planned source procedure from observed-session reports.
If a required fact is missing, give the supported portion of the answer
and the single clarification that would most improve the requested task.
```

These are project-specific template proposals, not copied vendor prompts. Version the templates and demonstrate valid/invalid examples during development. A well-written prompt is necessary but does not replace data quality, retrieval evaluation, output validation, or independent Gold.

### K.12 Context budget and evidence ordering

Reserve explicit budget for the user task, current state, approved calculations, selected evidence, and conflicts. Do not fill the context window solely because the model accepts a large input. A useful pilot budget might allocate 15% to instructions/task, 25% to state/calculations, 50% to evidence, and 10% to conflicts/answer contract; this is a measured design candidate, not a fixed optimum.

Place decisive exact facts and calculation results where the generator reliably uses them; test order sensitivity rather than assuming one layout. Group supporting/conflicting evidence by claim, retain source IDs, and cap redundant studies/recipe parents. The comparison between compiler and plain RAG must match generator, evidence universe, and final token budget. Otherwise an apparent compiler gain may come from extra context or a stronger model.

### K.13 RAG baseline ladder aligned with v14

The source SSOT's §245.12 defines B0–B7. The mini-project's B0–B5 subset should keep those exact meanings:

| Baseline | Added capability | Control needed |
|---|---|---|
| B0 | LLM only | Same generator/task prompts; no external retrieved facts |
| B1 | Dense RAG | Same source universe and context budget |
| B2 | BM25 + dense hybrid RAG | Fusion tuned only on development |
| B3 | Structured metadata RAG | Same text candidates; auditable metadata filtering/ranking |
| B4 | State-aware RAG | Predicted compiler packet; prefix mode declared |
| B5 | State + evidence compatibility/conflict packet | Scientific applicability and conflicts explicit |
| B6 | Level-15 transition fallback | Future/stretch only after transition gates |
| B7 | Calibrated recommend/ask/abstain decision layer | Policy targets, useful coverage, and uncertainty |

Apply shared integrity checks to all baselines so a baseline is not deliberately allowed malformed quantities while the proposed system gets deterministic validation. Evaluate the added selective decision layer separately from representational gains. If the mini-project implements B7 behavior in its application, disclose that extension rather than redefining B5 to mean everything.

### K.14 Retrieval relevance Gold and rigorous experiments

Build a query set across ingredient identity, product/form, symbolic quantity, antecedent/remaining allocation, procedure, process evidence, observed-session advice, and sufficiency/clarification. The original ~80-question target is a pilot: several questions from one recipe are correlated. Increase independent recipe/study families before claiming narrow confidence intervals.

Pool candidates from lexical, dense, structured, and state-aware retrievers for human relevance annotation, without revealing which system supplied each. Grade relevance separately from applicability/support: a row can be topically relevant but incompatible with the question's form or measurement basis. Retain unjudged status; absence from a shallow judging pool is not necessarily irrelevance. Double-annotate a representative subset and adjudicate support disagreements.

| ID | Research question | Controlled comparison | Main outputs |
|---|---|---|---|
| E10.5 | Does semantic chunking help? | fixed-token vs line/event/table-aware chunks, same embedding | Recall@K, nDCG, answer support, token cost |
| E10.6 | Do typed metadata fields help beyond text? | raw text vs card text vs metadata vs both | compatible-evidence recall and wrong-basis retrieval |
| E10.7 | Which embedding fits each task? | open baseline vs Gemini Embedding 2, same cards/splits | task-specific retrieval, latency/storage/cost |
| E10.8 | Is parent expansion useful? | no expansion vs bounded source/state parent | supported-answer rate at matched tokens |
| E10.9 | Do contextual prefixes help? | none vs deterministic compiler prefix vs audited LLM prefix | retrieval gain and prefix factual-error rate |
| E10.10 | Does late chunking help? | suitable open model early/late pooling, same boundaries | retrieval gain; prefix-leakage check |
| E10.11 | Is fine-grained interaction worth its cost? | dense/hybrid vs multivector/ColBERT-style rerank | nDCG, answer utility, memory, p95 latency |
| E10.12 | Does prompt structure matter? | identical facts/evidence with different frozen layouts | support/citation/calculation errors; order sensitivity |
| E10.13 | Do semantic compatibility features help? | text-only reranker vs text + exact state/basis fields | false compatible acceptance and useful coverage |
| E10.14 | Does query expansion invent assumptions? | raw vs reviewed alias expansion vs generated expansion | recall, unsupported-condition insertion rate |
| E10.15 | What breaks after index updates? | old/new embedding/card/registry snapshots | stale-ID rate, retrieval drift, replay consistency |

Run a small staged design rather than all combinations. First establish B2 and event/table chunks. Then test metadata, state packets, and one embedding challenger. Add contextual prefixes or multivectors only if the error analysis suggests a bottleneck they can address. Choose on development, freeze, and evaluate once on sealed data. Retrieval wins must ultimately show useful supported answers or a clear task-specific improvement.

### K.15 Learning what is missing after model training

The model does not automatically know every gap in the corpus. Detect gaps through task masks, source-presence checks, unresolved reasons, candidate-recall failures, disagreement, deterministic conflicts, and independent error audits. Compare source-present fields with extracted fields; distinguish an omission in the recipe from a model miss in the text.

| Gap type | Observable signal | Next action |
|---|---|---|
| Span missed | source-first Gold span absent in prediction | improve extractor/description or add targeted labels |
| Correct concept absent | Gold target missing from top-K | registry/candidate generator work |
| Selector error | correct candidate present but wrong choice | hard negatives, calibration, selector training |
| Regional alias gap | unresolved alias with reviewed source sense | alias/locale review and Gold-Light examples |
| Flow ambiguity | multiple compatible local entities | retain candidates; source clarification if needed |
| Unstated step/condition | source has no relevant assertion | omitted-step proposal or unknown, never fabricated Gold |
| Quantity evidence gap | no compatible portion/density record | evidence acquisition; retain symbolic quantity |
| Scientific measurement gap | missing compatible study result | DEL-1 acquisition or separately labeled DEL-2 estimate |
| Retrieval failure | supporting evidence exists but absent from result | chunk/query/index/reranker experiment |
| Generation failure | support is in packet but answer misuses it | prompt/claim-check/calculation integration |

Create a gap queue scored by downstream impact, uncertainty/disagreement, rarity, source diversity, and acquisition/review cost. Keep a separate random audit stream to estimate unbiased error rates. Active-learning examples enter train/Gold-Light, never the sealed test. Similarity finds candidate examples for review; it cannot certify the new labels by itself.

### K.16 Continual improvement without evidence laundering

Use a controlled loop: observed development error → issue/root-cause label → targeted source retrieval → human/manual decision → versioned training/example update → retrain or recalibrate → frozen development check → new release. Log every transition. A model-generated explanation of its mistake is a hypothesis for the issue, not a verified diagnosis.

New aliases can update a registry after review; new labels require the lifecycle in Appendix C; new measurements require evidence verification. Do not enable unrestricted online self-training from final answers or user agreement. A user saying “looks good” is feedback on utility, not independent proof of source chemistry or quantity grounding.

Titans/Hope-style memory experiments may later test whether a learned memory complements compiled packets, using the same prefix/no-leakage and state-accuracy controls. They must preserve external evidence and the deterministic ledger as authoritative. Latent surprise from JEPA can prioritize anomalies, but a high surprise score can reflect rare valid procedures, noise, or source style; it does not prove a missing process.

### K.17 Final RAG adoption decision

Adopt the simplest configuration that improves supported task utility at useful coverage within the measured latency/cost/storage budget. The initial recommended candidate is: structured accepted records, event/table-aware chunks, lexical+dense retrieval, exact ledger reads, metadata compatibility, a strong reranker, bounded state/evidence packets, a versioned answer contract, deterministic numeric checks, and calibrated routing. Gemini Embedding 2 and Jev enter as independently evaluated alternatives at their respective layers. JEPA and neural-memory architectures remain experiments after the core is stable.

The final report should answer: which errors the compiler fixed; which retrieval view/metadata fields helped; which embedding won per task; whether stronger prompts helped once evidence was held constant; what remains missing in source versus annotation versus science; and what additional review/data would reduce the most costly errors. That is the practical meaning of using the models and similarity methods to improve the workflow.

---

**Completion boundary:** this deliverable is the expanded research and execution plan. It includes verified source context, corrected assumptions, schemas, annotation policy, experiments, and acceptance gates. It does not claim completed training, a reproduced RecipeDB3 audit, measured SOTA superiority, or passed implementation tests. The next execution starts with the capacity-aware pilot and the smallest coherent compiler slice.
