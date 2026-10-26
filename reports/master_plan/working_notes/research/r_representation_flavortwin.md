# r_representation_flavortwin — research notes (Steps 35, 36-FlavorTwin, L12/L13)

Researcher: r_representation_flavortwin · 2026-10-22 · PLAN-RESEARCH ONLY (no implementation, no downloads, no training).
Scope caveat: the 36-step plan's step cards are MISSING (ctx.md). "Step 35" and "Step 36" are reconstructed from the
brief §9 titles + SSOT PART VII/VIII (§§174–194), §§15–19, §96, §99–101, §132, §142, §246, §279.6 and Master Plan v4.0
B04/B14/B16/W8. Nothing below is quoted from the missing plan. No repo file refers to "Step 35"/"Step 36" (grep, 0 hits).

---------------------------------------------------------------------------------------------------
## 0. Internal context (SSOT / plan / repo, read-only)

SSOT already specifies (and the specification is largely right):
- L12 status: spec COMPLETE, empirical gates OPEN, no default architecture frozen (SSOT L10588–10594). 10 inherited
  invariants incl. circularity ban, E0–E3 mandatory, structure≠sensory≠process≠context, z_m≠z_i, confound audits
  (L10598–10609). Program principle: every component vs (a) fingerprint+tree/linear, (b) trivial prior/mean pool,
  (c) published SOTA on identical splits (L10661).
- Frozen evidence table F1–F8 (L10665–10676); data inventory and gaps (L10680–10702): no concentration-resolved
  sensory labels, little quantified composition + thresholds (OAV), little time-resolved process chemistry, licences.
- Threads T0–T9 with gates G1–G9 (L10700–10963); T7 ingredient aggregation gate G7: an aggregator is frozen only if it
  beats OAV-weighted average **on ingredient-level sensory labels, not only proxy tasks** (L10882–10910).
- Set-to-set similarity: S_mean / best-match / symmetrised / weighted / OT; "aggregation choice changes the answer more
  than the molecule kernel" (SSOT L8306–8330). §142 baseline stack: E0 n_ij; E1 Jaccard/Ochiai/IDF/null percentile;
  E2 Morgan r2 2048 chirality Tanimoto (+ count/MinMax, MACCS, FCFP); E2-ingredient kernel mean + balanced OT
  (OT marked **Unverified**) (L8852–8871). No universal Tanimoto cutoff; FlavorDB's FP2≥0.30 is historical (L8388–8450).
- Circularity trap table (L8465–8486). L12 completion gate (L13260–13278). Integrated order (L13200–13240): T8 process
  data acquisition starts at Phase 0 because data, not GPU, is the bottleneck.
- L13: 14 frozen design distinctions (L13396–13411); inherited classical baselines (L13415–13432); recipe ladder R0–R9,
  "R0–R3 mandatory before claims about R4–R9" (L13776–13794); cuisine ladder C0–C8 (L14334–14347); L13 gate
  (L15262–15280); promotion rule "added information > shortcut/confound explanation" (L15308–15330).
- FlavorTwin: §19 baseline ladder + tasks (L1710–1754); §96 B0–B6 ladder, B2 (co-occurrence) is an *evaluation*
  signal, not a representation rung (L5191–5246); §246 V2 boundary: Z* factorised, **no universal flavour-similarity
  scalar**, candidate = ingredient+state+process+conditions, 7 evidence classes, chemical≠perceived flavour
  (L26712–26782); §279.6 cultural prior P_culture may only rerank, after E13E-17 (L45591–45614). SSOT itself lists
  "Recent related work that reduces static FlavorTwin novelty" (L4276–4280).
- Master Plan v4.0: B04 molecules/ingredients (plan L312–330), B14 typed similarity framework, "never merged into one
  similarity, each has its own metric, evaluation set and null model" + SX-14-02 separation test (L485–495),
  B16 FlavorTwin static→process-conditioned (L503–520), W8 representation update contract with views + mask
  (L1768–1790).

Repo reality (verified by read-only inspection):
- `ledgers/data/MOL.jsonl` 1,726 rows (PubChem-resolved; CACTVS-881 fingerprint + 6 PubChem descriptors; **ECFP pending
  rdkit** — WORKLOG L185; `pyproject.toml` has no rdkit).
- `ledgers/data/IMAP.jsonl` 31,972 rows: 31,334 PRESENCE (all from SRC-000451 FlavorGraph, licence_status ASSUMED,
  storage DERIVED_ONLY, upstream FlavorDB CC BY-NC-SA 3.0), 219 MEASURED_CONCENTRATION + 419 PROCESS_CHANGE
  (SRC-000138 = Phenol-Explorer). Distinct: 313 ING × 1,659 MOL. SRC-000451 notes 417 FlavorGraph ingredients with
  compound links (SSOT §96.x says 416 — minor discrepancy).
- `ledgers/data/KGE.jsonl` 80,607 edges: ING_CO_OCCURS 57,496 (38,394 FlavorGraph NPMI + 19,102 corpus), ING_USED_IN_CUISINE
  6,619, ING_ALTERNATIVE_TO 462, MOL_HAS_TASTE 1,145 (ChemTastesDB), etc. All verification UNVERIFIED.
- ING↔FoodOn/FDC/FlavorDB/RecipeDB crosswalks were UNRESOLVED_EXTERNAL at WORKLOG L59; FlavorDB API needs a key
  (WORKLOG L775). `src/culinarystate/classical/` is an empty package; no representation/similarity code exists.
- Status of Step 35/36: NOT STARTED (only B04-lite molecule registry exists).

---------------------------------------------------------------------------------------------------
## 1. Questions

Q1 Molecule level: in our small-data regime, do learned/pretrained molecular encoders beat ECFP/descriptors + RF/GBM?
Q2 Odour/flavour prediction: what is established for structure→odour, and how far does it transfer to mixtures/foods?
Q3 Limits of structural vs sensory similarity (molecule and mixture).
Q4 Food pairing: what do Ahn 2011 / Jain-Rakhi-Bagler 2015 / later critiques actually license?
Q5 Ingredient = set of compounds: which aggregator (Jaccard/IDF, set kernels, Deep Sets, Set Transformer, OT)?
Q6 Presence vs abundance vs odour activity value — what data exist, and what is the minimum representation?
Q7 Recipe and cuisine embeddings: what does literature support beyond R0–R3 / C0–C2?
Q8 FlavorTwin-like work 2019–2026: what is already done, publication status, what remains novel?
Q9 Which separate similarity notions are needed, how is each operationalised, evaluated, null-modelled?
Q10 Is an empirical pilot cheaper than more reading?

---------------------------------------------------------------------------------------------------
## 2. Findings per question

### Q1 — fingerprints vs learned encoders (confidence HIGH)
- MoleculeNet (Wu et al., Chem Sci 2018; arXiv 1703.00564, opened): learnable representations are generally best but
  "struggle … under data scarcity" and with heavy class imbalance.
- Deng et al., Nat Commun 14:6395 (2023), DOI 10.1038/s41467-023-41948-6 (Europe PMC record opened): 62,820 models;
  representation-learning models perform poorly on most datasets; dataset size is essential for them to excel; activity
  cliffs matter.
- Praski, Adamczyk & Czech, arXiv 2508.06199 (v1 Aug 2025, v4 23 Feb 2026; opened): 25 pretrained models × 25 datasets
  (MoleculeNet+TDC), frozen embeddings, hierarchical Bayesian comparison: nearly all show negligible or no improvement
  over ECFP; only CLAMP (fingerprint-based) significantly better. **STATUS: arXiv preprint, no peer-reviewed venue listed.**
  SSOT F3 (L10671) treats it as [FROZEN]; the conclusion is corroborated by peer-reviewed Deng 2023 + MoleculeNet, so
  the default is safe, but the evidence label should read "preprint, corroborated by peer-reviewed work".
- Rogers & Hahn, JCIM 50:742–754 (2010), DOI 10.1021/ci100050t (Crossref record opened) — ECFP definition.
- TabPFN (Hollmann et al., Nature 637:319–326, 2025, DOI 10.1038/s41586-024-08328-6; Crossref record opened) — a credible
  small-data tabular comparator for fingerprint/descriptor features (already named in SSOT T2).
- Consequence: ECFP4 (count + bit) / Morgan + RF/LightGBM/logistic and kNN-Tanimoto are the default z_m^struct; pretrained
  GNN/transformer encoders are optional rungs only. Our molecule set is ~1.7k (MOL ledger), i.e. firmly small-data.

### Q2 — odour/flavour prediction (confidence HIGH for single molecules; MEDIUM–LOW for foods)
- Lee et al., Science 381(6661):999–1006 (2023), DOI 10.1126/science.ade4401 (Europe PMC record + bioRxiv opened): GNN
  "principal odor map"; on 400 prospective odorants, closer to panel mean than the median panelist; beats standard
  chemoinformatic models on several other odour tasks.
- Keller et al., Science 355(6327):820–826 (2017), DOI 10.1126/science.aal2014 (opened): DREAM; intensity and pleasantness
  predicted well, only 8 of 19 semantic descriptors; regularised linear models nearly as good as RF.
- Recent single-molecule benchmarks are mixed: Suh, Hong & Park, Commun Chem 8:278 (2025), DOI 10.1038/s42004-025-01651-7
  (opened): 8,681 odorants from 10 pyrfume sources; Morgan-structural + XGBoost best (AUROC 0.828, AUPRC 0.237), no GNN arm.
  Wen et al. 2025 (Molecules; GCN macro-F1 0.519 vs 0.477) — seen only via search snippet → UNVERIFIED (SSOT T2 cites it).
- Mixtures: POMMix (Tom et al., arXiv 2501.16271, Jan 2025; opened) — GNN + attention aggregation + cosine head; presented
  at the **AI4MAT-ICLR-2025 workshop** (iclr.cc page opened), not the ICLR main track. AROMMA (arXiv 2601.19561, Jan 2026,
  preprint; opened) — unified single/two-molecule embedding. Ravia et al., Nature 588:118–123 (2020) (opened): 49,788
  similarity estimates, 199 participants, 242 mixtures, 21 physicochemical features → olfactory metamers. Snitz et al.,
  PLoS Comput Biol 9:e1003184 (2013) (opened): per-component models predict mixture similarity poorly; a single structural
  vector per mixture gives r ≥ 0.49, optimised r = 0.85.
- Key-odorant reality: Dunkel et al., Angew Chem Int Ed 53:7124–7143 (2014), DOI 10.1002/anie.201309508 (opened): ~230 key
  food odorants out of ~10,000 food volatiles; each food 3–40 key odorants; odour codes for >220 foods.
- Consequence: a **molecule-level** z_m^sensory is defensible (GS-LF / pyrfume, licence-checked). An **ingredient-level**
  sensory representation is NOT supported by public data: all mixture datasets are lab mixtures, small, and do not
  cover food matrices. Treat ingredient sensory similarity as HYPOTHESIS/UNSUPPORTED until sensory labels exist (SSOT G7).

### Q3 — structural vs sensory similarity limits (confidence HIGH)
- Sell, Angew Chem Int Ed 45:6254–6261 (2006), DOI 10.1002/anie.200600782 (Crossref record opened) — odour unpredictability /
  structural near-neighbours with different odours; SSOT also cites the GraphNOSE m-cresol vs 3-methylcyclohexanol
  example (L10724; not re-verified here).
- POM (Lee 2023) beats fingerprints at reproducing perceptual structure → a fingerprint Tanimoto is a STRUCTURAL notion
  only. Snitz 2013/Ravia 2020: mixture perception is not the sum of component similarities.
- Consequence: SSOT law "structural similarity ≠ sensory similarity" is empirically grounded; Step 35 must ship a
  measured separation test (Master Plan SX-14-02), not just a statement.

### Q4 — food pairing (confidence HIGH on what the papers say; HIGH that pairing ≠ palatability)
- Ahn, Ahnert, Bagrow & Barabási, Sci Rep 1:196 (2011), DOI 10.1038/srep00196 (opened): Western cuisines combine
  compound-sharing ingredients; East Asian avoid.
- Jain, Rakhi & Bagler, **PLoS One 10(10):e0139539 (2015)**, DOI 10.1371/journal.pone.0139539 (opened; note: PLoS One, not
  Sci Rep): eight regional Indian cuisines all show negative food pairing; **ingredient usage frequency is central**;
  spices push negative, dairy positive. Matches SSOT L6720–6725.
- Spence, Food Res Int 133:109124 (2020), DOI 10.1016/j.foodres.2020.109124 (opened): critical review; shared-aroma-compound
  pairing is a limited predictor of good matches; proposes cognitive vs perceptual pairing principles.
- Consequence: pairing statistics (n_ij, N_s, ΔN_s vs null cuisines) are a CULTURAL/statistical descriptor of corpora,
  not evidence of flavour compatibility. Any FlavorTwin "pairs well" claim needs sensory/human evidence. Frequency-
  preserving null models are mandatory (already SSOT §81–82, §159).

### Q5 — compound-set aggregation (confidence MEDIUM)
- Deep Sets (Zaheer et al., NeurIPS 2017; arXiv 1703.06114, opened) and Set Transformer (Lee et al., ICML 2019; arXiv
  1810.00825, opened) are the canonical learned permutation-invariant set encoders; they need supervised targets.
- OTKE (Mialon et al., ICLR 2021; arXiv 2006.12065, opened): trainable OT embedding, related to attention.
- No food-specific study of OT/Wasserstein over ingredient compound sets was found (one targeted search) → the SSOT label
  "Unverified" for balanced OT (L8868) stands. Word Mover's Distance is the obvious analogue (not opened → UNVERIFIED).
- Consequence: v1 aggregator set = {binary Jaccard/Ochiai, IDF-weighted overlap, cardinality-normalised kernel mean,
  symmetrised best-match, top-k mean}, with OT as one ablation arm. Learned Deep Sets/Set Transformer only if a
  non-circular ingredient-level supervised target exists (currently none — see Q6). The 2×2 example in SSOT L8320 shows
  the aggregator choice matters more than the kernel; the cardinality slope (score vs |F_i|) must be reported per arm.

### Q6 — presence vs abundance vs OAV (confidence HIGH on data scarcity)
- FlavorDB (Garg et al., NAR 46:D1210–D1216, 2018, DOI 10.1093/nar/gkx957; opened): 25,595 molecules, 2,254 linked to 936
  natural ingredients, 34 categories — presence lists. **SSOT §175.3 (L10690) attributes these counts to "FlavorDB2";
  they are the FlavorDB 2018 counts.** FlavorDB2 (Grover et al., arXiv 2205.05451, 2022; opened; no journal-ref) adds
  attributes incl. taste/aroma threshold values; its counts were not stated in the abstract → UNVERIFIED.
- Thresholds are matrix-dependent (water/oil/air) and mostly in subscription (VCF) or print compilations; VCF includes
  thresholds since 2015 (vcf-online page, search-level → UNVERIFIED detail). OAV = concentration / threshold in the same
  matrix; both are needed.
- Repo: 31,334 PRESENCE edges (FlavorGraph, 313 ING) vs 219 MEASURED_CONCENTRATION (Phenol-Explorer polyphenols, not
  odorants) vs 0 thresholds. **OAV-weighted representations are currently impossible for odorants in this repo.**
- Consequence: x_ij must be a tiered record (PRESENCE / MEASURED_CONCENTRATION with basis+matrix+study / THRESHOLD with
  matrix+source / OAV derived only when both exist in compatible matrix) and every ingredient profile carries coverage
  stats; UNKNOWN concentration never becomes 0 or 1.

### Q7 — recipe/cuisine embeddings (confidence MEDIUM)
- Recipe1M / im2recipe (Salvador et al., CVPR 2017, DOI 10.1109/cvpr.2017.327; Marin et al., TPAMI 43(1) 2021, DOI
  10.1109/tpami.2019.2927476) — cross-modal image↔recipe retrieval; Crossref records opened. Licence/scope: images +
  scraped recipes; not needed for CulinaryState core.
- Reciptor (Li & Zaki, KDD 2020, DOI 10.1145/3394486.3403223; Crossref record opened) — pretrained recipe representation.
- KitcheNette (Park et al., IJCAI 2019; arXiv 1905.07261, opened): Siamese pairing-score model trained on ~300K
  recipe-derived pairing scores. RecipeMind (Gim et al., CIKM 2022, DOI 10.1145/3511808.3557092; arXiv 2210.10628
  opened): cascaded Set Transformer predicting "food affinity" from co-occurrence scores. **Both train and evaluate on
  co-occurrence-derived targets → circular under SSOT §133.2 if used as headline.**
- Cuisine: no newer primary source changed the SSOT C0–C8 ladder; the "Kissing Cuisines" WWW'17 Companion record carries
  a Crossref "Notice of Removal March 3, 2026" in its title field → do NOT cite.
- Consequence: R0–R3 (incidence, mean, IDF, quantity/role) and C0–C2 (prevalence, specificity/TF-IDF, motifs) are the
  v1 deliverable; R4–R9/C3–C8 stay gated. Recipe-family-disjoint splits using 07I families are essential because
  near-duplicates inflate recipe-completion metrics.

### Q8 — FlavorTwin-like work and novelty (confidence MEDIUM; literature moving fast)
Already done (so NOT novel for FlavorTwin):
- Static food-chemical graph embeddings for pairing: FlavorGraph (Park et al., Sci Rep 11:931, 2021, DOI
  10.1038/s41598-020-79422-8; opened); FlavorDiffusion (arXiv 2502.06871 / ACL Anthology 2025.aisd-main.7, Proc. 1st
  Workshop on AI and Scientific Discovery, pp. 70–77; workshop paper); Epicure (Radzikowski & Chen, arXiv 2604.22776,
  Apr 2026, preprint: ≥15 classifiable dimensions in FlavorGraph embeddings incl. taste, texture, geography, processing,
  culture) and Epicure multilingual (arXiv 2605.22391, May 2026, preprint: 4.14M recipes, 7 languages, chemistry-vs-context
  Metapath2Vec variants).
- Pairing/affinity prediction from co-occurrence: KitcheNette 2019, RecipeMind 2022.
- Contextual ingredient substitution: GISMo (Fatemi et al., arXiv 2302.07960, 2023; opened; no venue listed on arXiv);
  LLM SFT+DPO substitution (Senath et al., Natural Language Processing Journal vol. 12, 2025; Massey repository record
  opened; Hit@1 22.04 beats GISMo only on Hit@1).
- LLM flavour agents/benchmarks: FoodPuzzle (Huang et al., arXiv 2409.12832; published KDD 2025 Vol. 2 pp. 5493–5504 per
  ISI record opened; 978 foods, 1,766 flavour-molecule profiles, RAG agent); FlavourBench (Chen & Hayretci, arXiv
  2608.20574, Aug–Sep 2026, preprint: 27 LLM endpoints × 534 pairing/substitution/constraint tasks).
- Inverse food design with sensory test: Tac, Gardner & Kuhl, arXiv 2602.03092 (Feb 2026, preprint): generative burger
  design, blinded test n=101. NotCo patent US10957424B1 (granted 2021-03-23; opened): formula generator matching a target
  food. Review: Tac & Kuhl arXiv 2607.09529 (2026, preprint).
- Processing-aware taste prediction + inverse design: Tagkopoulos et al., arXiv 2604.20206 (Apr 2026, preprint): 70 recipes,
  209 ingredient taste references, trained panel; Reuss–Voigt/Hashin–Shtrikman bounds under-predict; 8 processing-chemistry
  proxy features (Maillard, caramelisation, evaporation, hydrolysis, nucleotide synergy) cut MAE 27–62%. **This narrows any
  generic "process-conditioned flavour" novelty claim.**
- Process-aroma ML in one food: Hu et al., Food Chem 496:146915 (2025), DOI 10.1016/j.foodchem.2025.146915 (PubMed esummary
  opened; abstract not read → details UNVERIFIED). SSOT L4283 describes it as "during thermal processing".
What still looks novel (UNVERIFIED as exhaustive; one-pass search):
  (a) candidates = ingredient+**state**+process+conditions with every match carrying an SSOT §246.6 evidence class backed by
      study-level measured evidence (EVD/STUDY), with explicit UNKNOWN/abstention — no found work does evidence-gated
      inverse search;
  (b) a typed, multi-notion similarity registry with per-notion null models and measured separation tests (structural vs
      sensory vs cultural vs process) — prior work fuses views into one embedding (Epicure, FlavorGraph);
  (c) non-circular, recipe-family-disjoint evaluation at 600k-recipe scale with identity families (07I);
  (d) Indian-cuisine frequency-aware/negative-pairing-aware search with a separable cultural prior (§279.6).
  Novelty must be re-checked immediately before any paper; FlavourBench/Epicure group is active.

### Q9 — separate similarity notions (confidence HIGH on need; MEDIUM on operationalisation)
See §3 table. Ambiguity found: brief §24 "COMPOSITIONAL" can mean ingredient→compound (chemical composition) or
recipe→ingredient composition. Recommend splitting into CHEMICAL (compound profile) and COMPOSITIONAL (recipe ingredient
incidence/quantity), and NUTRITIONAL separately (nutrient vector).

### Q10 — pilot vs reading (confidence HIGH): pilot is cheaper. See §6.

---------------------------------------------------------------------------------------------------
## 3. Architecture recommendation

### 3.1 Recommended: "Typed Similarity Registry + gated representation ladder" (CPU-first)
Every similarity is a registered, versioned function, never a free scalar:
`sim_id, notion, level(molecule|ingredient|ingredient_state|recipe|cuisine), inputs/views, formula, aggregator,
weights, evidence_class_required, coverage_fields, null_model, eval_set, split_family, valid_domain, licence_scope, status
(BASELINE|HYPOTHESIS|PROMOTED|RESEARCH_ONLY)`.

| Notion | Level | v1 operationalisation (baseline) | Null / confound control | Non-circular evaluation | Data status |
|---|---|---|---|---|---|
| STRUCTURAL | molecule | ECFP4/Morgan r2 2048 bit + count; Tanimoto / MinMax; MACCS, FCFP, atom-pair ablations | scaffold/cluster split; no global τ | odour/taste label prediction (GS-LF, ChemTastesDB) scaffold+cluster split | MOL 1.7k; rdkit missing |
| STRUCTURAL | ingredient | set aggregation of molecule kernel: kernel-mean, sym best-match, top-k; OT ablation | cardinality slope; degree-preserving null; source-count | held-out recipe completion; category prediction (proxy, flagged) | FlavorGraph presence, 313 ING |
| CHEMICAL (composition) | ingredient | n_ij, Jaccard, Ochiai, IDF overlap (E0–E1) on PRESENCE tier; concentration tier separately | profile-size, source-count, null percentile | NOT on n_ij itself; cross-check vs held-out co-occurrence | presence only |
| SENSORY | molecule | POM-style or fingerprint+GBM descriptor predictions; cosine over predicted descriptor vectors | label-frequency prior; shuffled labels | held-out sensory labels only | GS-LF licence check |
| SENSORY | ingredient | OAV-weighted aggregation of molecule sensory vectors **only where conc+threshold in same matrix** | shuffled concentrations | ingredient-level sensory labels (none) → status UNSUPPORTED | NEED_DATA |
| FUNCTIONAL (culinary role) | ingredient-in-recipe | context substitution score(i→j|recipe, role); baselines: co-occurrence-context kNN, GISMo-style, LLM zero-shot | frequency baseline | held-out curated substitution pairs (KGE ALTERNATIVE_TO 462 + human-labelled) | thin; needs labels |
| NUTRITIONAL | ingredient/recipe | standardized per-100 g nutrient vector cosine/Mahalanobis; UNKNOWN masked | basis checks | held-out nutrient-profile retrieval | FDC/INFOODS local |
| CULTURAL | ingredient/recipe/cuisine | NPMI co-occurrence, prevalence, specificity, C0–C2; N_s vs null cuisines | frequency-preserving + category nulls; source/website confound | cross-cuisine transfer; never "flavour" | KGE + recipe_base |
| COMPOSITIONAL | recipe | R0 incidence Jaccard; R2 IDF cosine; R3 quantity/role weighted (CQPO) | recipe size; family-disjoint | held-out completion, family-disjoint | recipe_base 612k |
| PROCEDURAL | recipe | Jaccard over process bag → event-sequence edit distance → graph kernel (after Steps 16–20) | step-count confound | dish-family retrieval, family-disjoint | depends Steps 16–20 |
| PROCESS-CONDITIONED | ingredient_state | Δ-profile similarity from measured EVD before/after (E1–E4) or validated transition (Steps 27/33) | evidence class + OOD flag; else UNKNOWN | process-state discrimination (raw vs cooked) on study-disjoint EVD | phenolics/vitamins only; volatiles NEED_DATA |

Ladder order for Step 35 (consistent with SSOT L13200–13240, L13776–13794): E0–E3 → R0–R3 → C0–C2 → separation tests
→ (only if a non-circular supervised target exists) learned rungs E4–E8 / R4–R9 / C3–C8.
Fusion: allowed only as a *task-conditioned* reranker that reports per-notion components; never stored as "the similarity".

### 3.2 FlavorTwin (Step 36 FlavorTwin part) recommended pipeline
SSOT §246.3 hierarchy is right. Add: (i) every candidate output lists per-notion scores + evidence class + coverage +
UNKNOWN components; (ii) mandatory baselines = SSOT §19 ladder + **LLM zero-shot/RAG baseline** (FoodPuzzle/FlavourBench
style) + **GISMo/LLM-substitution baseline** for contextual substitution; (iii) a separable cultural prior only after
E13E-17 (§279.6); (iv) sensory-equivalence claims require a human sensory gate (§246.7).

### 3.3 Rejected alternatives
- Single universal flavour embedding / similarity scalar (FlavorGraph/Epicure-style as the product) — violates §246.2 and
  laws; Epicure shows such spaces entangle taste, geography, processing and culture.
- Pretrained molecular foundation models as default z_m — Q1 evidence; keep as optional rung.
- Deep Sets / Set Transformer / OT as default ingredient aggregator — no ingredient-level supervised target; OT
  coverage-sensitive and unverified for food profiles.
- Training on co-occurrence/NPMI and evaluating on co-occurrence (KitcheNette/RecipeMind regime) — circular (§133.2).
- LLM-only pairing/substitution — ungrounded, cannot produce evidence classes; retained only as a baseline.
- Cross-modal image↔recipe (Recipe1M) encoders in core — out of scope, licence-heavy, GPU-heavy; L17 optional.
- OAV-weighted sensory ingredient similarity now — no thresholds/odorant concentrations in repo; would invent values.
- FlavorDB FP2≥0.30 threshold as a definition — historical only (SSOT L8388–8450).

---------------------------------------------------------------------------------------------------
## 4. What each affected step must change/add

### Step 35 (Representation ladder) — recommendation MODIFY (split into substeps, no new top-level step)
- 35a Molecule registry completion: InChIKey master (exists) + rdkit ECFP/FCFP/MACCS/RDKit2D (env decision needed: rdkit
  is not installed; human approval to add dependency). Output `molecule_fingerprints_v1` (pinned rdkit version).
- 35b Ingredient chemical profile: tiered `x_ij` schema {tier: PRESENCE|MEASURED_CONC|THRESHOLD|OAV_DERIVED, value/UNKNOWN,
  unit, basis, matrix, state_id/form, study_id, source_family, licence_scope, evidence_ids}; per-ingredient coverage record
  {n_compounds, n_sources, n_measured, coverage_class}. Aggregator ablation (E1/E2 arms above) with cardinality slope.
- 35c Recipe R0–R3 + cuisine C0–C2 + null lattice (frequency-preserving, category-preserving) on recipe_base; splits:
  recipe-family-disjoint (07I families), source-disjoint, cuisine holdout.
- 35d Typed similarity registry (`registry/similarity_registry_v1.csv`, fields in §3.1) + separation tests: Spearman/rank
  agreement between notions per pair (e.g. structural vs cultural vs nutritional) and kNN-overlap@k; report that they
  differ (expected), never fuse.
- 35e (optional, gated) learned rungs; promoted only per §183.3/§194.3.
- Baselines: label-prior, kNN-Tanimoto, ECFP+LightGBM/RF/logistic, TabPFN optional; E0–E3; R0–R3; C0–C2.
- Metrics: AUROC/AUPRC (molecule tasks), Recall@K/MRR/nDCG (completion), cardinality slope, null percentile, rank stability
  across fingerprint families, seed/split CIs, runtime.
- Gates: §183.4 L12 gate + §193.8 L13 gate + NEW explicit gates: G35-COV (score–profile-size slope reported and below a
  pre-registered bound or the notion is flagged coverage-confounded); G35-CIRC (no headline metric shares its signal with
  training); G35-SEP (every notion has its own eval set and null).
- Compute: CPU sufficient (128-core server or Mac); GPU unnecessary for v1; learned rungs Tier-1 GPU at most.
- Human: ~small: curate held-out substitution pairs (few hundred) and audit 50 ingredient crosswalks.
- Licence: FlavorGraph/FlavorDB NC + DERIVED_ONLY; GoodScents/Leffingwell terms; FooDB CC BY-NC; VCF subscription.

### Step 36 (FlavorTwin portion) — MODIFY + DEFER the process-conditioned claim (NEED_DATA)
- Inputs: Step 35 registry + profiles; Step 27/33 validated transitions; Step 15 DATA-EVIDENCE v1; Step 36 RAG evidence
  packets; 07I families.
- Outputs: candidate records {ingredient_id, state_id, process_id, condition_ranges, per-notion scores, evidence_class (§246.6),
  coverage, OOD flag, unknown_components, citations}.
- Baselines: random, co-occurrence/PMI, n_ij, IDF, ECFP-set, static text embedding, FlavorGraph-like embedding (released
  vectors, licence check), LLM zero-shot/RAG, GISMo/LLM substitution.
- Evaluation: held-out recipe reconstruction (family-disjoint), contextual substitution on held-out human-labelled pairs,
  process-state discrimination on study-disjoint EVD (only analytes with data), target-descriptor retrieval at molecule
  level, cross-cuisine robustness; expert rating only with blinded protocol. Metrics: Recall@K, MRR, nDCG, constraint
  satisfaction, abstention rate/coverage-risk curve, diversity.
- Gate: process conditioning earns its place only if it beats static on a held-out process-sensitive task beyond CI
  (§246.8); otherwise FlavorTwin ships static + evidence-gated and says so.

---------------------------------------------------------------------------------------------------
## 5. Look-ahead requirements for earlier steps
1. Step 04 (similarity contract): freeze the typed similarity registry schema and the "no universal scalar" rule there,
   incl. CHEMICAL vs COMPOSITIONAL vs NUTRITIONAL naming.
2. Step 05/ING (identity): ING↔FlavorDB/FooDB/FDC/FoodOn crosswalks (UNRESOLVED_EXTERNAL per WORKLOG L59) are a hard
   prerequisite for coverage; keep ingredient identity separate from state/form (state_id_or_form already in IMAP).
3. Step 07I: recipe family/dish-family IDs must be exported as a split key for 35c/36 (near-dup leakage).
4. Step 08 (lineage): every IMAP/EVD edge needs source_family + study_id for source-count confounds and study-disjoint
   evaluation.
5. Steps 11–14 (acquisition): if process-conditioned FlavorTwin is to be tested on flavour (not only nutrients/phenolics),
   acquisition must target volatile/key-odorant before/after-process studies with matrix, concentration basis, platform
   (GC-MS/GC-O/AEDA), and odour thresholds with matrix + source. Current EVD (USDA R6, Bognár, Phenol-Explorer) has no
   volatiles → mark as NEED_DATA in Step 14 coverage map.
6. Step 12 (structured DBs): per-edge licence_scope (NC, DERIVED_ONLY, subscription) so Step 35 outputs can be filtered for
   any public release.
7. Steps 16–20: quantity (CQPO) and ingredient role are required for R3 and contextual substitution; procedural events are
   required for PROCEDURAL similarity; ingredient state per event required for PROCESS-CONDITIONED lookup.
8. Steps 27/33: export validated-domain metadata so FlavorTwin can assign PROCESS_SIMULATED_MATCH vs EXTRAPOLATED.
9. Environment: decide rdkit (and optionally TabPFN) dependency before Step 35.

---------------------------------------------------------------------------------------------------
## 6. Residual uncertainty and pilot
Residual: (i) whether balanced OT beats kernel-mean/best-match on real profile-size distributions (needs ablation);
(ii) how coverage-confounded FlavorGraph presence profiles are (417 linked ingredients of 6,653); (iii) whether any public
ingredient-level sensory dataset with licence fit exists (none found); (iv) novelty landscape after Oct 2026; (v) Wen 2025,
Hu 2025 details, FlavorDB2 counts, WMD — UNVERIFIED.
Pilot is cheaper than more reading (stop rule §8.5): P35-0, CPU-only, ~1–2 days, no downloads, using local FlavorGraph
DERIVED_ONLY data + MOL ledger + recipe_base: compute E0/E1/E2-ingredient (3 aggregators + OT arm), cardinality slopes,
null percentiles, inter-notion rank agreement, and a family-disjoint held-out ingredient-completion task comparing R0/R2 vs
co-occurrence. Needs rdkit approval. Its result decides whether OT/learned aggregators stay on the plan.

SSOT change requests to file (PROPOSED_ONLY): F3 evidence label (preprint); §175.3 FlavorDB vs FlavorDB2 counts; POMMix
venue = workshop; FlavorGraph linked-ingredient count 416 vs 417; brief's "Jain, Rakhi & Bagler 2015" = PLoS One.
