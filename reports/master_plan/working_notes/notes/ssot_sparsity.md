# READER NOTES — ssot_sparsity (SSOT v15 PART XI §§219–227 + §229 return point)

Reader: `ssot_sparsity`. Scope: SSOT `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` L23317–25079 (PART XI header L23317; §219 L23319 … §227 end L24843; §228 change register L24844–24895; §229 L24896–25079). Cross-checked against the L15 sections the PART XI text depends on: §209.17 D0–D11 ladder (L18543–18613), §201.7/§201.9 evidence tiers and censoring (L16651–16712), §215.38–39 G15 gates (L22376–22424), §215.68–70 (L22647–22684), §216 data contracts (L22731–23049), §240.4–240.5 (L26311–26317), §246.6 (L26755–26765), RQ16-20/21 (L27165–27199). Repo checks: `ledgers/data/EVD.jsonl`, `ledgers/data/EXP.jsonl`, `reports/del2/*`, `reports/es1/es1_1_audit.md`, `reports/h_state/transition_bootstrap_v0_contract.md`, `reports/h_state/state_representation_contract_v1.md`, `registry/{censoring_registry_v1,value_origin_registry_v1,evidence_tier_provenance_map_v1,provenance_class_registry_v1,simulated_state_changes_schema_v1}.csv`, `docs/simulator_data_contract.md`, `src/culinarystate/transition/*`, `WORKLOG.md` S017/S029/S038–S040, and plan `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (cited "Plan v4 L…").

The 36-step Master Execution Plan v1 is MISSING (ctx.md L14). Every "spine step" requirement in §8/§10 below is my reconstruction from the SSOT, Plan v4 and repo artifacts. None of it is quoted card text.

Status labels used: **SSOT** = quoted or paraphrased from the SSOT at the cited line. **REPO** = observed in the repo. **DIAG** = my own read-only stdlib diagnostic (script at `/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad/mpa/evd_profile2.py`). **INFERENCE** = my reasoning. **UNVERIFIED** = not checked.

---

## 0. Authority / status of this material

- PART XI comes from a supplied external report ("Level 15 — Explicit State-Transition Learning: Finalized Research Report + Sparsity Deep-Dive", SSOT L23323). The SSOT says it is "not treated as an independently verified literature review" (L23325). Paper, dataset-size and performance claims carry `[SOURCE-REPORTED]` (L23328) until checked against primary sources. Design recommendations are taken in "as hypotheses/gates where they are consistent with the frozen SSOT rules" (L23333).
- §229 is labelled "v13 HISTORICAL RETURN POINT — SUPERSEDED BY §259" (L24896), and §259 "replaces §229 as the current return point" (L42782). §229's content is still the most concrete implementation order for L15 sparsity (L24922–24982). I did not check whether §259 or §279 overrides that order: UNVERIFIED (read §259/§279 to confirm).
- The SSOT header (L22) names PART XI §§219–227 the "authoritative Level-15 sparsity/MNAR/completion/synthetic-prior/active-learning extension". The status line (L5) says L15 "sparse/MNAR/completion/kinetics/hybrid/inverse-design tracks OPEN under evidence gates".
- §228.2 (L24878–24892) lists what did NOT change. Two items matter most here: "Synthetic/imputed data never become observed evidence" (L24889) and "Simple models remain valid winners" (L24891).

---

## 1. Definitions, entities and data contracts

### 1.1 Core objects (§219)
- **Thesis** (L23340): "Which food-process transitions have been measured is itself structured, learnable information." The evidence base is "a sparse, censored, biased observation of a much larger transition space" (L23342).
- **Value tensor** `Y ∈ R^{I×P×C×J}` (L23346–23357). I = ingredients/foods/matrices; P = process families/leaves; C = condition bins **or condition representations**; J = targets/compounds/properties. An observed cell holds `Y_ipcj = log RF` "or another evidence-matched delta/endpoint target" (L23362–23365).
- **Metadata/confidence tensor** `W_ipcj` (L23370–23382), with fields: evidence tier; study/source; method/platform; replicate count; censoring/LOD; yield/normalization; verification status; observation mask.
- **Observation mask** `M_ipcj ∈ {0,1}` (L23388–23392). Rule: `P(M=1|Y,X) ≠ constant` is plausible (L23409–23414), and "Do not assume unobserved cells are a random sample" (L23416).
- **MNAR mechanisms listed** (L23398–23404): popularity; health-relevant compounds; process choice depends on food type; analytical platform determines detectability; non-detects (left-censoring); publication bias; historical/year/source trends.
- **Density** (L23420–23429): `[SOURCE-REPORTED]` a Phenol-Explorer-like food×process×compound grid is "well below 1%". The SSOT requires that "The exact density must be recomputed from the versions actually acquired" (L23422). The only frozen point is qualitative: the tensor is "extremely sparse and highly structured" (L23428).
- **Source regimes** (§219.6, L23447–23463). These must not be flattened into one exchangeable dataset (L23463).
  - **D-A** aggregated retention: sparse across food/process/target, limited conditions (L23449).
  - **D-B** curated raw-vs-processed panels: dense within a few foods/studies, block-missing across sources/platforms (L23453).
  - **D-C** focused kinetics: deep in time/condition for very few systems (L23457).
  - **D-D** recipe procedure/state corpora: "Dense structurally, nearly empty for measured chemistry" (L23461).
- **Cold-start types** (§219.7, L23469–23474): cold food/ingredient; cold process; cold compound/target; cold ingredient×process pair; cold condition region; cold study/platform.
- **Canonical side information** (§219.8, L23480–23505):
  - Food: FoodOn/category, proximate composition, ingredient embeddings, molecular composition/embeddings "where valid", matrix properties.
  - Process: hierarchy/family, heat/moisture/medium descriptors, continuous `T,t,pH,a_w`, physics-derived exposure features.
  - Compound: fingerprints/descriptors/embeddings, compound class, assay/platform metadata.
  - Study: source/year/lab/platform, evidence tier, extraction/verification status.
- **Objective** (§219.9, L23511–23525): `min Σ_{Ω_obs} q_ipcj L(Y, Ŷ(X;Θ)) + R(Θ)`, where q = evidence quality/uncertainty weight. Under MNAR a propensity model may be added, but it "must be sensitivity-tested because the true observation mechanism is not known" (L23525).
  - Interacts with §201.7 (L16668–16674): tier weights are `[PROPOSED-PILOT]`, tuned on the highest-quality validation subset, and "do not treat confidence weights as probabilities unless calibrated".

### 1.2 CF analogy entities (§220.1, L23535–23544)
| CF concept | Food-process analogue |
|---|---|
| user | food/ingredient/matrix |
| item | process × condition × target |
| rating | log retention / delta / endpoint |
| confidence | tier × replication × method quality |
| user bias | food/matrix bias |
| item bias | process/target lability bias |
| exposure | P(cell studied) |
| side info | composition, molecule/process descriptors, ontology |

"Useful mathematically, not literally" (L23546). The analogy breaks on seven points (L23550–23558): continuous conditions; study/platform dependence; censoring; kinetic/physical constraints; clustering by paper; absence ≠ dislike/non-interaction; and "retention can exceed 1".

### 1.3 Propensity entities (§220.5)
- `e(x) = P(M=1|x)` (L23612–23616).
- Covariates x (L23620–23625): food popularity/frequency; target/compound class; process; study year; analytical platform; source type.

### 1.4 Value-status vocabulary (§222.3)
- **SSOT:** `TRUE_ZERO / NON_DETECT / BELOW_LOD / NOT_MEASURED / UNKNOWN`, kept distinct "wherever source information permits" (L23972–23980). §201.9 (L16696–16712) gives the earlier set `ND / <LOD / unmeasured / true zero` and says "Always retain censor_flag".
- **REPO** `registry/censoring_registry_v1.csv` covers it at this level of detail: CS-001 DETECTED, CS-002 NON_DETECT, CS-003 BELOW_LOD, CS-004 BELOW_LOQ, CS-005 ABOVE_CAP, CS-006 CENSORED_UNKNOWN, CS-007 NOT_REPORTED ("UNKNOWN is not NON_DETECT").
  - It adds BELOW_LOQ and ABOVE_CAP, which the SSOT lacks.
  - It has **no TRUE_ZERO code** (DIAG/INFERENCE: TRUE_ZERO is in SSOT L23973 but absent from the CS registry).
- **REPO** `registry/value_origin_registry_v1.csv`: VO-001 MEASURED … VO-004 SOURCE_IMPUTED, VO-005 SOURCE_IMPUTATION_POSSIBLE (USDA R6), VO-006 UNKNOWN. This supports the "source-side imputation" flag that §222/§223 implicitly need.

### 1.5 Missing covariate vs missing target (§222.1)
- Covariate: "May be imputed within the training fold with uncertainty/mask retained" (L23949).
- Target: "Do not fill for final evaluation" (L23953). A model-completed target may enter "selected training experiments as an explicit low-confidence/imputed tier, never as ground truth" (L23955).

### 1.6 Completed-cell class (§221.19)
- A completed cell is `IMPUTED / MODEL-ESTIMATED`, "not observed evidence" (L23925–23929).
- It may guide retrieval/ranking, uncertainty-aware recommendations and active acquisition (L23933–23935). It "does not become a source citation for a factual chemistry claim" (L23937).

### 1.7 Imputed-target training tier (§222.9, L24042–24048)
- Mark evidence class **`I`**.
- Assign inflated noise/lower weight.
- Retain imputer/model provenance.
- Exclude from validation/test/calibration.
- Run a real-only vs augmented ablation.

### 1.8 Synthetic data taxonomy (§223.1, L24072–24074)
Three tiers:
1. mechanistic simulation / synthetic prior (**S-MECH**);
2. structural augmentation of real observations;
3. statistical / LLM-generated rows.

Further detail:
- **S-MECH generation** samples (L24091–24097): literature-prior kinetic parameters; `T,t,pH,moisture`; schedule shapes; study offsets; measurement noise; LOD censoring; sparse observation grids.
- **Structural augmentation examples** (L24129–24133): within-study deltas/contrasts; yield normalization; dry/wet-basis normalization; matched cultivar contrasts; shared-reference bridging. "Generated pairs are dependent and require clustered uncertainty" (L24135).
- **Weak/rule labels** (L24141–24153): e.g. "boiling → likely water-soluble nutrient loss pathway". "Never treat rule labels as measured chemistry."
- **LLM extraction workflow** (L24161–24169): paper/table/span → structured extraction → exact source pointer → unit normalization → automated checks → human verification → evidence tier promotion. "Only the **verified source measurement** is real evidence" (L24171).
- **Fidelity ordering** (L24229–24243). It is "a project control hierarchy", "not a universal epistemology" (L24245). From highest to lowest:
  1. observed + human-verified
  2. observed extracted + verified
  3. observed-derived structural augmentation
  4. imputed/model-estimated
  5. mechanistic synthetic prior (domain-specific)
  6. rule weak labels
  7. statistical/LLM generated rows

### 1.9 Field-level contracts relevant to sparsity (from §216, which PART XI consumes)
- **§216.1 transition-event table** (L22737–22795):
  - identity: transition_id, ingredient_id, state_before_id, state_after_id, process_family, process_leaf;
  - temperature: T_value/T_lo/T_hi/T_type;
  - time: t_value/t_lo/t_hi/t_type;
  - conditions: medium, tool, geometry, moisture_before/after, water_activity, pH, pressure, oxygen, mixing;
  - target: target_family/variable/compound, value_before/after, delta_value, direction_label, ordinal_band, unit;
  - censoring: **censor_flag, LOD**;
  - provenance: **study_id, source_id, doi_or_citation, platform, matrix_description**, **evidence_tier, verification_status, extraction_method, explicit_or_inferred**;
  - sequence: trajectory_id, timepoint, sequence_id, event_index;
  - versioning: **split_id, dataset_version**.
  - Rule: "Not every row has every field. Missingness remains explicit" (L22798).
  - *Not in the table:* observation mask, propensity, replicate count (n), SD/range, yield/normalization status, lab, year. W_ipcj (L23375–23382) needs replicate count and yield/normalization; G15-1 (L22382) needs yield/normalization and censoring/missingness status. → GAP (§9).
- **§216.2 kinetic-experiment table** (L22804–22820). Needed for S-MECH parameter priors and §224.4 identifiability.
- **§216.6 data/version registry** (L22887–22894): dataset version, ontology version, unit normalization, split version, evidence-tier policy, target definition. These are "part of the model artifact" (L22896).
- **§216.12 minimum package** (L22992–23031): `data/{transition_schema, evidence_registry, split_registry}`; baselines; kinetics; evaluation splits; reports (dataset_card, transition_benchmark, kinetic_fit_report, decision_record).
  - It does **not** list completion models (D7), a propensity model or a mask audit. The package predates v13 PART XI (INFERENCE: §216 is v12; PART XI adds M2 completion, L24528–24539).

### 1.10 Highest-priority artifact (§229.3, L24987–25001)
`FoodProc transition tensor + observation mask + evidence ledger + cold-start split registry`. It is claimed to support transition prediction, completion, MNAR analysis, calibration, active acquisition, CulinaryState-RAG retrieval and FlavorTwin candidate generation.

### 1.11 Repo reality vs these contracts (REPO/DIAG)
- **EVD versioning:** `EVD.jsonl` has 57,280 version lines and 18,156 latest IDs. 17,978 are ACTIVE (`reports/es1/es1_1_audit.md` L6). Any profiling must take the latest ACTIVE row; a naive line count over-counts about 3.2×.
- **Active EVD by source:** USDA-RETN-R6 7,018; BOGNAR-2002 7,090; PHENOL-EXPLORER-3.6 3,870. All are tier E3.
- **Verification:** 14,108 UNVERIFIED and 3,870 AI_PRECHECKED (PE). **0 human-verified rows** (DIAG). Consistent with `registry/evidence_tier_provenance_map_v1.csv`: E1/E2/E4 current_rows = 0.
- **Censoring:** 5,894 rows are censored, all `GT_CAP` right-caps.
  - USDA raw "100" is stored as cap limit 97.5 (5,700 version lines). Bognár "1.00" is stored as limit 0.995 (13,096 version lines; WORKLOG S038 L262).
  - **No NON_DETECT / BELOW_LOD rows exist.** `lod` and `loq` are null in all 17,978 rows, `lod_loq_status = NOT_REPORTED_BY_SOURCE_ROW` (`es1_1_audit.md` L25).
- **Study identity:** study_id_status is NOT_IDENTIFIABLE for all USDA and Bognár rows and PRESENT for PE (125 distinct STUDY ids). Study-disjoint evaluation is therefore possible only on PE today.
- **Condition axis:** condition_moisture UNKNOWN 17,978/17,978; pH UNKNOWN 17,978; temperature UNKNOWN 11,963; duration UNKNOWN 14,895 (`es1_1_audit.md` L24). **The C mode of `Y^{I×P×C×J}` is practically empty for the current D-A data.** Only process labels and, for some rows, a core temperature exist.
- **Indicative density** (DIAG; food key = ingredient_id, else raw matrix name; process key = process_id, else raw name; target = SVAR id):
  - Over all three sources: F=318, P=40, T=224, 9,294 observed (F,P,T) cells, density **0.33%** of F×P×T.
  - Food×process pairs observed: 763/12,720 = 6.0%.
  - Within observed pairs, target fill: 5.4%.
  - Per source: USDA F35×P27×T26 → 3,951 cells, 16.1%; Bognár F249×P14×T37 → 4,424 cells, 3.4%; PE F82×P20×T161 → 919 cells, 0.35%.
  - DEL-2's own "grid density" uses a different cell definition: USDA 0.0755, Bognár 0.62075, PE 0.00267 (`reports/del2/*_results.md` header lines).
  - **Takeaway: density is definition-dependent.** A canonical cell definition must be frozen (Plan v4 AM1 L3560–3578) before any density number is reported, as §219.4 L23422 requires.

---

## 2. Models and baseline ladders (simple → strong → advanced)

### 2.1 Canonical ladder (SSOT §209.17, L18547–18611; order re-affirmed §227.12 L24826–24840)
- D0 persistence `Ŝ_{t+1}=S_t` → D1 global mean-delta → D2 process-conditioned mean-delta → D3 hierarchical shrinkage/partial pooling (food class, process family, compound class, study/source) → D4 nearest-evidence retrieval/kNN → D5 strong GBDT (LightGBM/XGBoost) → D6 TabPFN "where sample size/task shape are compatible" → **D7 evidence-aware low-rank/factorization completion** → D8 classical kinetics → D9 hybrid mechanistic + learned residual → D10 neural multi-output/latent-state (may "not … skip D0–D7", L18607) → D11 UDE/neural ODE/reaction networks (focused time-resolved only).
- The §227.12 order "supersedes architecture-first escalation" (L24840): `D0–D6 → D7 → D8 → D9 → D10/D11 only if data support`.

### 2.2 D3 ↔ D7 equivalence claim (§220.4, L23590–23606)
The mixed model `y = μ + a_food + b_process + c_compound + d_study + interactions + ε` serves "the same broad purpose as factorization", and "This is D3 and should be benchmarked before advanced completion" (L23606).

### 2.3 D7 sub-ladder (§221)
| ID | Model | Line | Notes |
|---|---|---|---|
| D7a | biased MF `μ+b_f+b_i+u_fᵀv_i` | L23714–23726 | item = (process family/leaf, target); conditions as side info "rather than endlessly binning" |
| — | extended bias model `μ+b_food+b_process,target+b_study+u·v` | L23575–23584 | conditions enter explicitly |
| D7b | Bayesian PMF | L23730–23738 | partial pooling, posterior uncertainty; "attractive at small sparse scale" |
| D7c | Macau-like side-info BMF | L23742–23751 | `[SOURCE-REPORTED]` chemistry precedent; "implementation availability/licensing as a practical constraint" |
| D7d | Factorization machine | L23757–23775 | food ID, process ID, condition features, compound descriptors, matrix props, source/evidence features |
| D7e | soft-impute / nuclear norm | L23779–23781 | "Do not let Bayesian/neural complexity skip it if the matrix view is well-defined" |
| tensor | CP / Tucker / coupled matrix–tensor / PARAFAC2-like | L23785–23801 | continuous conditions stay explicit features/kinetic links |
| coupled side matrices | food×composition, compound×descriptor, process×physics, food×ontology | L23805–23812 | for cold start |
| DropoutNet-like | whole-row/column masking during training | L23853–23858 | "valid cold-start training ablation" |
| GP/kernel completion | kernels over food/process-condition/target | L23862–23870 | D-B/D-C small data; calibrated; BO-ready; "Benchmark cost/scalability" |
| two-tower + ANN | retrieval layer for FlavorTwin | L23874–23884; L24404–24408 | "not automatically a calibrated transition predictor"; "ANN retrieval is a scalability layer, not scientific evidence" |
| Neural CF / LightGCN / AE | deprioritized | L23888–23894 | **rule: "well-tuned biased MF/FM/Bayesian completion are mandatory before neural CF claims"** (L23892) |

### 2.4 Covariate imputation baselines (§222.4–222.6)
- Candidates: MICE; missForest; "small-table TabPFN-like imputation for covariates", fit "**inside training folds only**" (L23986–23990).
- Left-censoring: QRILC/GSimp `[SOURCE-REPORTED]`. Prefer censored likelihoods; use censoring-aware imputation only where complete covariates are needed; retain censor flags (L23994–24000).
- §201.9: "Tobit-like likelihoods" (L16707).
- Multiple imputation with between-imputation variability when inference is affected (L24004–24008).

### 2.5 Synthetic-data generators (§223.9)
CTGAN/TVAE, CTAB-GAN, diffusion, copula/BN, LLM row generators, SMOTE/SMOGN/mixup. Priority is "**LOW** for target synthesis" (L24184); they "add no new chemistry and can reproduce source bias/memorize rare rows" (L24186).

### 2.6 Regime × technique map (§226.1, L24475–24481)
| Regime / claim | First techniques | Synthetic/imputed use | Headline evaluation |
|---|---|---|---|
| D-A × qualitative/ordinal | hierarchical shrinkage, biased MF, rules | rules train only | study/cold cell |
| D-A × quantitative endpoint | FM/Bayesian completion + propensity sensitivity | imputed training tier only | masked real + cold pair |
| D-B × multi-compound | side-info Bayesian completion, coupled tensor, strong GBDT | observed-derived deltas | cold compound/study/platform |
| D-C × dynamics | classical kinetics → hybrid residual | mechanistic simulation pretrain/prior | held-out temperature/study |
| D-D × procedure | symbolic graph + sequence baseline | recipe tuples/rules | step F1 / trust horizon |

### 2.7 Situation rules (§226.2, L24485–24517)
- Mechanism known, parameters uncertain → `mechanistic simulator + Bayesian parameter prior + real fitting`.
- Mechanism unknown, few observations → real acquisition / active experiment selection "over bulk synthetic target generation".
- Many unstructured papers → LLM extraction + exact spans + human verification.
- Only qualitative claims → rule/weak supervision + verified qualitative test set.

### 2.8 Acquisition models (§224)
- Completion-posterior acquisition (L24297–24302): uncertainty, downstream value, connectivity to cold entities, model disagreement.
- Kinetic identifiability (L24306–24313): choose T, time point, initial condition, moisture/pH to maximise information about `k, E_a`.
- D-optimal `F = JᵀWJ` (L24319–24323).
- Bayesian expected information gain (L24327–24335).
- BALD/ensemble disagreement (L24339–24341).

### 2.9 Tooling candidates (§226.10, L24595–24629)
- Data: pandas/Polars, DuckDB/Parquet, DVC.
- Tabular: scikit-learn, LightGBM/XGBoost, TabPFN.
- Completion: PyTorch/NumPy biased MF, an FM implementation, PyMC/NumPyro/SMURFF-like, tensorly.
- Kinetics: SciPy least_squares/solve_ivp, lmfit, PyMC/NumPyro.
- Design: BoTorch, pymoo, SALib.
- Retrieval: FAISS "only after representation validation".
- "Tool choice does not replace transparent baselines" (L24629).

### 2.10 Plan v4 / repo ladders (compare; see §9 contradictions)
- **Plan v4 AZ6 (L4700–4711)** uses a *different* D numbering: D0 persistence, D1 process mean, D2 nearest evidence, D3 linear/tree, D4 neural residual, D5 conditioning, D6 multi-output, D7 sparse completion, D8 kinetics, D9 hybrid. **Conflicts with SSOT §209.17.**
- **Plan v4 AI6 (L3130–3139)** matches the SSOT: D0 RF=1 … D5 LightGBM, D6 TabPFN only if practical, D7 FM/side-info factorization, plus a biased-MF comparator.
- **REPO `src/culinarystate/transition/baselines.py`** implements D0Persistence, D1GlobalMean, D2ProcessMean, D3Hierarchical, D4NearestEvidence, D5Boosting (HistGradientBoosting with categorical features + masks, WORKLOG S017 L115) and D7BiasedMF (biased MF with side-info biases), plus a LogTarget wrapper.
  - **D6 TabPFN SKIPPED** ("not installed; GPU", `reports/del2/*_results.md`).
  - No FM, BPMF, Macau, soft-impute, tensor, GP or DropoutNet (REPO; grep of class names).
- **REPO `reports/h_state/transition_bootstrap_v0_contract.md` §3** defines B-0 persistence, B-1 global mean, B-2 ingredient-conditioned mean (shrinkage to food group), B-3 process-conditioned mean, B-4 hierarchical-fallback lookup, and B-5 simple tabular "only after B-0..B-4". **"TabPFN or learned models are out of scope for V0."** Its B-numbers do not map 1:1 to D-numbers.

---

## 3. Experiments / hypotheses / RQs

### 3.1 Research questions opened by sparsity (§219.5, L23436–23441)
1. Low-rank latent transfer across foods/compounds?
2. Molecular/process side info solving cold start?
3. Does the mask reveal reporting/popularity bias?
4. Does propensity/MNAR correction change reported generalization?
5. Can mechanistic priors pretrain without contaminating real evaluation?
6. Which new observation reduces the most uncertainty?

### 3.2 Paper contributions (§227.2–227.6)
- **C1 evidence-aware sparse completion** (L24656–24668).
  - Hypothesis: "tier-aware low-rank/factorization/side-information completion improves cold-pair/compound prediction and calibration over D0–D6."
  - Controls: masked real cells; cold food/process/compound/pair; study-disjoint; frequency buckets; no imputed test targets.
- **C2 FoodProc-ColdStart benchmark** (L24670–24683).
  - Splits: random reference; masked-real-cell; cold food; cold process; cold target; cold pair; study/source; platform/matrix where possible.
  - Can be a contribution "if the data licenses permit release or if split manifests/code can be shared."
- **C3 MNAR/reporting-bias sensitivity** (L24685–24698).
  - Hypothesis: "naive evaluation over observed literature cells may overestimate generalization into unstudied regions".
  - Tests: propensity model; naive vs weighted/DR; support buckets; source/year/platform covariates.
  - Status: `[HYPOTHESIS]`.
- **C4 simulator-pretrained / real-finetuned** (L24700–24718).
  - Pipeline: simulator → domain-randomized pretraining → real fine-tuning → held-out-temperature evaluation.
  - Compare: real-only / simulator-only / mixed / pure kinetics / pure ML / hybrid.
- **C5 active experiment/evidence selection** (L24720–24728): random/factorial vs information-gain/D-optimal; count experiments needed for stable `k,E_a`; optional real validation.

### 3.3 Milestones (§226.3–226.8)
- **M1** data audit & baseline floor (L24521–24526): acquire/normalize D-A/D-B; Parquet/DuckDB versioned schema; entity resolution; **observation-mask audit**; D0–D6; random vs cold vs study-disjoint.
- **M2** evidence-aware completion (L24530–24539): hierarchical shrinkage; biased MF; FM; Bayesian side-info "if practical"; propensity sensitivity; conformal/selective abstention on real calibration cells. "**Pass target: G15-9 or reject the completion hypothesis**" (L24539).
- **M3** kinetics + verified literature expansion (L24543–24547): focused acrylamide/Maillard anchor simulators; identifiability; kinetic paper curation; spans retained.
- **M4** hybrid + synthetic-prior ablation on one real D-C target (L24551–24558), including a synthetic ratio sweep and held-out-temperature evaluation.
- **M5** procedural engine / rollout / RAG (L24562–24567).
- **M6** conservative inverse design (L24571–24575).
- **Semester compression** (L24579–24591): M1–M3 suffice ("sparse evidence benchmark + completion/MNAR analysis + calibrated abstention + focused kinetics"). "Do not sacrifice evaluation quality merely to reach M6."

### 3.4 §229.2 immediate order (L24924–24981) — the operational sequence
1. Step 1, L15 data audit: the observed tensor/mask + dataset card covering food/process/condition/target support, study/platform support, censoring, tiers, cold-start categories and missingness patterns (L24926–24933).
2. Step 2, D0–D6 floor on real grouped/cold splits (L24937–24948).
3. Step 3, D7 benchmark: biased MF, FM, Bayesian/side-info "if feasible", simple tensor/low-rank; masked-real-cell + cold-start + study-disjoint (L24952–24961).
4. Step 4, calibration/abstention/MNAR: real-only calibration, risk–coverage, support/evidence distance, propensity sensitivity, source/popularity buckets (L24965–24969).
5. Step 5, D8 focused kinetics: one or two systems, identifiability/OOD (L24973).
6. Step 6, D9 hybrid/synthetic prior: "Only after D8 is credible" (L24977).
7. Step 7, rollout/inverse: "Only where measured intermediate states or a validated focused simulator permit it" (L24981).

### 3.5 Hypotheses marked not frozen
- §229.4 broad (L25005–25019): "hierarchical/low-rank side-information completion + strong tabular baselines + study/cold evaluation + calibrated abstention may provide more real value than larger neural dynamics models … must be tested, not assumed."
- §229.5 focused (L25023–25033): "mechanistic simulator/kinetics + real fitting + hybrid residual or synthetic-prior pretraining may improve held-out-condition prediction in one well-characterized system."

### 3.6 Active-learning first experiment (§224.11, L24379–24384)
Simulate a known kinetic system → compare random/factorial vs info-gain → measure the number of experiments to stable parameters → optionally validate 1–2 real conditions.

### 3.7 Related RQs elsewhere
- RQ16-20 Transition fallback (L27165–27183): headline split cold pair/study; metrics coverage, error, UCR, calibration.
- **RQ16-21 Completion visibility** (L27185–27199): does exposing the imputed/model-estimated evidence class improve calibration vs unlabeled completion?
- Plan v4 SX-13-03 (completion vs GBDT, masked-cell/cold-pair), SX-13-04 (MNAR propensity-corrected eval), SX-13-05 (simulator pretraining, ratio sweep, TSTR) (Plan v4 L478–480).
- DEL-2 deliverable (Plan v4 L1249).

### 3.8 Experiments already run (REPO, `ledgers/data/EXP.jsonl`, `reports/del2/`)
- **EXP-000001** USDA R6: "SUPPORTED on random split only; NOT supported under cold-start".
  - random: D5 0.0251 vs D0 0.1205.
  - matrix_disjoint: D0 0.0590, D4 0.0567, D5 0.0692, D7 0.0759.
  - process_disjoint: D0 0.0728, D5 0.0672, D7 0.0891.
  - study_disjoint: NOT POSSIBLE.
- **EXP-000002/3** Phenol-Explorer raw / log-RF: "NOT SUPPORTED".
  - D0 persistence is best or tied on matrix/process/study-disjoint. E.g. study_disjoint raw: D0 0.5577 vs D7 0.6978 vs D5 0.7551.
  - With the log target: D7+log 0.5688 vs D0 0.5577 (CIs overlap).
- **EXP-000004** Bognár: "SUPPORTED incl. cold-start".
  - matrix_disjoint: D5 0.0463 vs D0 0.0621, D7 0.0503.
  - process_disjoint is degenerate: point CIs such as [0.0385,0.0385], only 7 process signatures.
- **D7 (biased MF) never beats D5 on USDA or Bognár on any split.** On PE cold splits it beats D5 but not D0 (DIAG reading of the tables). **G15-9 as written (D7 beats D5/D6) is therefore not met on any current source.** G15-2 is also unmet because D6 was skipped.
- DEL-2 reports "propensity AUC" 0.8105 (USDA), 0.8674 (Bognár), 0.9118 (PE), and an "MAE IPW" column. WORKLOG S017 L115 says the propensity is "from marginal frequencies", not the covariate model of §220.5.
- Split-conformal 90% empirical coverage on cold splits was 0.72–0.87 for USDA (WORKLOG S017 L117), i.e. **under-coverage on cold splits**. PE process_disjoint D4 coverage was 0.938 with very wide width.
- Censored rows are "trained at lower bound 0.975 (assumption)" (all DEL-2 reports).
- Cross-source USDA vs Bognár (`reports/del2/cross_source_v1.md`): only 67 overlap cells (4 ingredients, roast only); MAE 0.0751, Spearman 0.611.
- FDC raw/cooked pairs (`reports/del2/fdc_pairs_v1.md`): 867 pairs, 4,984 analytical rows. Imputed FDC values are "circular against R6". These are E6 candidates, not EVD (`evidence_tier_provenance_map_v1.csv` E6 note).

---

## 4. Gates, promotion and stop rules (exact text, line numbers)

### 4.1 G15 gate table (SSOT §215.38, L22380–22396; frozen per L23077; "revised to include completion, synthetic/imputed utility…" per L24872)
- **G15-1 Data audit** (L22382): "Every quantitative row has source/study, evidence tier, units/target definition, yield/normalization status, and censoring/missingness status."
- **G15-2 Baselines** (L22383): "Canonical D0–D6 are reported on all eligible headline splits before D7+ claims."
- **G15-3 Process signal** (L22384): "Process-conditioned modeling adds value over food-identity-only on a process-disjoint or equivalent controlled split; report CI/effect, not just point gain."
- **G15-4 Kinetic fit** (L22385): "At least one focused D-C dataset supports an identifiable/useful kinetic fit with profile/bootstrap/posterior uncertainty."
- **G15-5 Condition-OOD** (L22386): "Kinetic/hybrid/physics model adds value over the best non-kinetic tabular baseline on held-out temperature/condition."
- **G15-6 Calibration** (L22387): "Real, study-disjoint calibration is reported; intervals/sets achieve acceptable task-specific coverage/width."
- **G15-7 Abstention** (L22388): "Risk–coverage/selective prediction improves over always-answering and abstention rules are defined on REAL calibration data."
- **G15-8 Consistency** (L22389): non-negativity, semigroup/order/balance/constraint diagnostics on valid subsets.
- **G15-9 Completion** (L22390): "**Evidence-aware D7 completion beats D5/D6 on masked-real-cell and cold food/process/compound/pair tests, or is rejected.**"
- **G15-10 Synthetic/imputed utility** (L22391): "**Synthetic/imputed training rows improve REAL-only study-disjoint performance in a ratio sweep without unacceptable calibration damage; no synthetic/imputed target enters final test/calibration.**"
- **G15-11 Rollout** (L22392): "A trust horizon is empirically established on D-C/D-D where true intermediate states exist; no rollout claim otherwise."
- **G15-12 Inverse design** (L22393): "passes an ID-level benchmark beyond nearest-evidence/random/grid and remains inside the safe support region."
- **G15-R** (L22394): seeds, versions, hashes/snapshots, splits, parameters permit rerun "within declared tolerance".
- **G15-H** (L22395): "Every LLM-extracted row used in held-out test/calibration is human verified against the cited source span/table."
- **G15-I** (L22396): RAG/FlavorTwin end-to-end logs "evidence class, uncertainty, abstention and provenance".
- Sub-gates (L22402–22424):
  - G15-RXN: 5 conditions.
  - G15-HYB: "beyond both the mechanistic model and pure ML, or … separately demonstrated physical-consistency advantage".
  - G15-INV: `inverse-design ceiling ≤ forward-model credibility`.

### 4.2 PART XI hard rules / promotion rules
- **HR-SYN-1 (frozen)** §223.14 (L24249–24255): "**synthetic/imputed target rows never enter final test or calibration sets**" — "This rule is frozen in v13."
- **§221.17 conformalized completion** (L23902–23905): "calibrate on **real observed cells only**; maintain study/source grouping; report assumption violations; under MNAR, weighted/propensity adjustments are sensitivity analyses rather than automatic guarantees."
- **§221.18 completion evaluation protocol** (L23911–23919), 9 required items: (1) masked REAL cell holdout; (2) cold food row; (3) cold process column/entity; (4) cold compound/target; (5) cold ingredient×process pair; (6) study-disjoint; (7) platform/matrix stratification where relevant; (8) calibration/coverage; (9) frequency/support buckets.
- **§222.10 anti-inflation protocol** (L24052–24060). Every completion/imputation experiment reports: real-only test; masked-real-cell test; cold-start test; study-disjoint test; with/without missingness mask; with/without propensity weighting; calibration.
- **§222.2 forbidden default target values** (L23961–23964): zero; mean/median; half-minimum; LOD/2.
- **§220.8** (L23666): "Propensity weighting does not license random row splits." Study-disjoint, cluster bootstrap and source/platform covariates are mandatory (L23660–23664).
- **§220.9** (L23676): "A model that works only on popular cells has not solved sparse transfer."
- **§220.10 MNAR claim boundary** (L23682–23688). Allowed: "plausibly MNAR and we model/sensitivity-test this structure". Forbidden without external validation: "our propensity model recovers the true missing-data mechanism".
- **§220.6**: clipping/stabilization of 1/ê (L23641). The goal is robustness testing, not asserting correctness (L23643).
- **§220.7 DR evaluation**: `[HYPOTHESIS]` for food literature (L23654).
- **§223.5 forbidden claim** (L24121): "Simulator-generated success cannot establish performance outside the simulator's validated domain."
- **§223.10 ratio sweep** (L24192–24203): `0× 0.25× 0.5× 1× 2× 5×` synthetic relative to real "or an equivalent designed sweep". "Do not report only the best hand-picked ratio."
- **§223.11** (L24209–24213): TRTR / TSTR / mixed; "The headline test is always real and study-disjoint where possible."
- **§223.12 memorization/two-sample checks** (L24217–24223): train-record copies; distance to nearest real row; distribution shift; implausible units/conditions; physical-constraint violations.
- **§223.15** (L24265): "all synthetic value is conditional on real-only validation."
- **§224.11 active-learning gate** (L24377): "Do not claim acquisition efficiency from simulations only without stating the simulator assumption."
- **§227.11 final promotion rule** (L24800–24822):
  - **Sparse-data method**: `real cold/study generalization + calibration + evidence honesty > apparent gain from imputation/source bias`.
  - **Synthetic-data method**: `real-only held-out benefit survives ratio sweep and calibration checks`.
  - **Active-learning method**: "only if it reduces uncertainty/error per acquired observation relative to simpler acquisition strategies."
- **§227.10 canonical caveats** (L24790–24796). These "must accompany any paper draft":
  1. secondary-reported numbers need primary re-check;
  2. website/database counts differ from papers;
  3. some extraction-paper counts are internally inconsistent;
  4. "no transferable universal 'synthetic data multiplier'";
  5. conformal guarantees can fail under clustering/MNAR/shift.
- **§229.6 "What not to do next"** (L25037–25046):
  - bulk-generate synthetic chemistry rows;
  - impute final test targets;
  - random row splits as headline;
  - neural ODE on endpoint-only data;
  - call completion "observed chemistry";
  - LLM value into gold test without verification;
  - optimizer over unsupported conditions;
  - "skip D0–D7 because a reaction/transformer architecture sounds more novel".
- **§229.8** (L25073): "build the sparse transition/evidence benchmark before a generic RAG front-end".

### 4.3 Stop / escalation (cross-ref)
- §215.70 (L22673–22683): stop increasing complexity when cold-pair collapses, study shift dominates, conditions add no value, labels are too noisy, kinetics are unidentifiable, uncertainty is badly calibrated, or retrieval matches advanced models → "invest in better evidence/data".
- §215.69 (L22661–22669): the simpler result is retained.
- §215.68 (L22649–22657): a positive result must persist under cold-pair, source/study, condition-OOD, calibration and physical consistency; "Random-split improvement alone is insufficient."
- §216.13 decision record (L23036–23049): "This decision record, not architecture preference, controls the next implementation step."
- **Underspecified thresholds** (see §9): G15-6 "acceptable task-specific coverage/width"; G15-9 "beats" (no margin, statistic or CI rule); G15-10 "unacceptable calibration damage"; §227.11 inequalities are qualitative.
  - Plan v4 AM5 (L3628–3632) adds "improves a predeclared primary metric with uncertainty and does not catastrophically harm cold splits / calibration / coverage / error slices".
  - The bootstrap contract §6 adds "paired lower bound > 0 on S-3 or S-4" and is the only concrete threshold in the repo.

---

## 5. Data requirements and named sources (licence notes)

### 5.1 §227.8 dataset acquisition list (L24746–24757)
"Resource inclusion remains license/quality/version dependent" (L24757). For each item: repo state (REPO = checked; licence statements not marked REPO are from my knowledge and UNVERIFIED unless noted).
- **Phenol-Explorer retention data.**
  - REPO: ingested as PHENOL-EXPLORER-3.6, 3,870 active EVD rows from 125 studies.
  - Licence: UNVERIFIED here. ctx/D-? not checked. DECISIONS L24 notes retention factors are excluded from bulk downloads (they need per-publication values).
- **USDA nutrient-retention factors R6.**
  - REPO: ingested, 7,018 rows.
  - Licence: `data_source_acquisition_manifest.csv` DS-001 says "US federal work, public domain … ASSUMED_PD_CATALOG_CONFIRMS_EXISTENCE".
  - Caveats: imputed from similar foods, not row-identifiable (VO-005); %TR/%AR mixed (state contract C4, L68).
- **FoodData Central raw/cooked composition "where matchable".**
  - REPO: 867 SR-Legacy pairs analysed (`reports/del2/fdc_pairs_v1.md`). Not ingested (E6 candidates).
  - Licence: US federal / CC0 per FDC docs (UNVERIFIED in this run).
  - Circularity caveat: FDC imputed values are derived from R6 retention factors.
- **FoodAtlas**: not checked. Licence UNVERIFIED.
- **FooDB / FlavorDB / FlavorGraph** as composition/context resources:
  - FlavorDB use is permitted via Prof. Bagler (D-015, licence ASSUMED/DERIVED_ONLY per ctx L21).
  - FooDB and FlavorGraph licences: UNVERIFIED here.
- **Curated GC-MS/GC-IMS raw-vs-processed studies** (D-B regime): none in the repo (DIAG: no volatile-platform EVD). This is the source class where NON_DETECT/BELOW_LOD and platform block-missingness (§222.8) actually matter.
- **Focused acrylamide kinetics; Maillard/glucose–glycine kinetics** (D-C): no D-C data in the repo (EVD has no time series; `es1_1_audit` duration UNKNOWN 14,895/17,978).
- **Recipe1M+ / r-FG / OpenPI / NHK-state-like corpora** (D-D): licence/research-only terms UNVERIFIED. The project's D-D plane is the 612,782-recipe base (ctx L29).
- **FoodOn / process ontologies**: FoodOn is CC BY 4.0 per its OBO listing (UNVERIFIED in this run).

### 5.2 Data needed per technique (INFERENCE from the SSOT text)
- **Propensity model** (§220.5, L23620–23625) needs covariates for *observed and unobserved* cells: food popularity/frequency, target class, process, **study year**, **analytical platform**, **source type**.
  - Year and platform are not in EVD today; MEAS has 3 rows (`ssot15_state_program_inventory.md` L67).
  - The *universe* of candidate cells (the denominator) must be defined. Otherwise "propensity" is just marginal frequency, which is what DEL-2 did (WORKLOG S017 L115).
- **Cold compound/target** needs molecular fingerprints/descriptors. Per the WORKLOG S? RDKit was a blocker (handoff/API_BLOCKERS mentions rdkit, WORKLOG L157). The SSOT allows learned molecule embeddings "only after L12 gates" (L23840).
- **Cold food** needs composition (FDC/FooDB), FoodOn category and matrix properties (L23818–23821).
- **Cold process** needs process hierarchy plus heat/moisture/medium descriptors and condition features (L23829–23831). This depends on Step 07 conditions, which are largely UNKNOWN today.
- **Study effects** need study_id/lab/platform/year (L23503). Study ids are missing for USDA and Bognár.
- **Censoring** needs LOD/LOQ values plus status codes (L23972–23980; §216.1 L22775–22776). None are populated today.
- **W tensor** needs replicate count n, SD/range and yield/normalization (L23379–23380; Plan v4 AM2 L3586–3593). The ES-1.1 export has a `yield_fraction` UNKNOWN for 13,612 rows (`es1_1_audit.md` L24). Presence of n/SD: UNVERIFIED (not profiled).
- **S-MECH** needs literature-prior kinetic parameters (§216.2 table) and validated simulator scope (`registry/simulated_state_changes_schema_v1.csv` validation_scope, extrapolation_flag, `may_enter_gold_evaluation` "always false").
- **Active literature acquisition** (§224.8) needs a discovery corpus with paper-level metadata (year, matrix, process, target, platform) *before* extraction, so the "high-value missing region" can be matched to candidate papers.

### 5.3 Compute (§226.11, L24633–24642)
"Most v13 work remains CPU/small-GPU feasible." The bottleneck is "evidence acquisition; verification; harmonization; study-aware evaluation. Not model FLOPs." Consistent with §215.64 L22593 ("The main Level-15 bottleneck is data, not GPU access").
- INFERENCE: TabPFN on ≤10k rows is CPU-feasible. DEL-2's "SKIPPED (not installed; GPU)" is an environment issue, not a compute requirement (UNVERIFIED: TabPFN v2 CPU inference behaviour and weight licence).

---

## 6. Dependencies on other levels / steps

- **L14 → L15**: §216.7 graph (L22901–22928): L14 process/evidence table → L15 transition schema → D0–D4 → cold-pair + study/OOD → calibration/abstention → {RAG transition fallback; kinetics if time series; rollout if intermediates; inverse search if forward gates pass}.
- **L12/L13 representations are optional additive features only.** §216.10 (L22976–22978): "Level 15 must not depend on an unvalidated upstream learned embedding to function at all." §221.11 (L23840): molecule embeddings "only after L12 gates".
- **L16 consumers.**
  - §240.4–240.5 (L26313, L26317): recipe-plane missingness is "measured and reported; it is not filled by LLM guesses". Completion "never convert[s] missingness into observed truth".
  - §246.6 evidence classes (L26757–26765) include MODEL_ESTIMATED_MATCH and PROCESS_SIMULATED_MATCH.
  - RQ16-20/21 (L27165–27199).
  - §225.1 cascade "retrieve candidates → filter feasibility/evidence → simulate/predict → rank with uncertainty → abstain" (L24394–24400) "maps directly to FlavorTwin and CulinaryState-RAG" (L24402).
  - §27710 overview places "L15 transition / sparse completion / kinetics" between L14 and the Semantic Evidence Compiler (L27708–27712).
- **Entity resolution** (§225.5, L24430–24437): canonical food IDs, process ontology mapping, compound IDs, alias/fuzzy merges, provenance and a review queue are prerequisites. "LLM assistance … must not silently rewrite identities."
  - REPO: ingredient_id is null on 6,409/17,978 active EVD rows (`es1_1_audit.md` L24) and process_id on 157.
- **Human verification**: G15-H (L22395) plus §223.8 workflow. Today 0 rows are human-verified (`evidence_tier_provenance_map_v1.csv`), so **no eligible held-out test/calibration set exists that satisfies G15-H for E3 test rows**. The tier map E3 note says "needed for held-out test labels (G14-3, G15-H)".
- **Kinetics (D8) depends on D-C data**, which does not exist in the repo. M3/M4/C4/C5 are blocked on acquisition (Steps 11–14) and simulator validation (26–27).
- **Ordering dependency inside PART XI**: D9 hybrid / synthetic prior "Only after D8 is credible" (L24977). Rollout/inverse "only where measured intermediate states or a validated focused simulator permit" (L24981). G15-INV ceiling (L22420).

---

## 7. Risks / failure modes

1. **Popular-cell illusion**: gains only on high-support cells (§220.9 L23676). Mitigated by frequency buckets (§221.18 item 9).
2. **Platform shortcut**: the model learns `platform → target block` (L24029) instead of chemistry. Needs platform controls and platform-disjoint evaluation (L24036–24038). Repo has no platform field populated (MEAS 3 rows).
3. **Mask shortcut**: missingness indicators encode source/platform (L24020).
4. **Propensity variance and misspecification**: small ê → huge weights (L23641). The true mechanism is unknown (L23525, L23686). DEL-2's propensity from marginal frequencies may be near-degenerate; AUC 0.91 on PE suggests strong structure and possible positivity problems (INFERENCE). Plan v4 AM4 (L3619–3624) requires positivity/overlap reporting, which is not done in DEL-2 (REPO: no such column).
5. **Row dependence**: within-paper clustering; within-study derived pairs are dependent (L24135, L23658).
   - DEL-2 used grouped bootstrap.
   - Bognár process_disjoint has a single group, which gives degenerate CIs (REPO). This is a failure of the split, not a result.
6. **Censor-as-truth leakage**: training censored rows at bound 0.975 (DEL-2) is in effect single-value imputation. It conflicts with §222.5 L23998 ("prefer censored likelihoods") and `state_representation_contract_v1.md` L40 ("never imputed to a bound as truth"). The bootstrap contract §4 lists "censored rows contributing label leakage through the bound" as a risk. With 33% of active rows censored (5,894/17,978), this affects results materially (INFERENCE).
7. **Circularity**: USDA R6 factors are imputed from similar foods. FDC cooked values are computed with R6 factors, so FDC-vs-R6 agreement is circular (`fdc_pairs_v1.md`). Donor/recipient rows must stay in the same fold (bootstrap contract §4).
8. **Conformal under-coverage** on cold/clustered splits (0.72–0.87 at nominal 0.90, WORKLOG S017 L117). This is consistent with §227.10 caveat 5 (L24794).
9. **Simulator gap / confirmation bias / model collapse** (§223.15, L24261–24263).
10. **Synthetic memorization** of rare rows (L24186, L24217–24223).
11. **Over-binning conditions**: tensor bins of continuous T/t destroy physics (L23726, L23801, L23584).
12. **Regime flattening**: pooling D-A/D-B/D-C/D-D as exchangeable (L23463). Also pooling USDA %TR/%AR with Bognár true retention (state contract C4).
13. **Analogy imports**: implicit negatives, iid exposure, preference semantics, web-scale neural recommenders (§225.8, L24463–24467).
14. **Over-claiming conformal guarantees or MNAR recovery** (L23905, L23686).
15. **Cell-definition drift**: course cell `(food, process, target)` vs full cell `(matrix, S_in, process, Θ, target, measurement basis)` (Plan v4 AM1 L3567–3575). "Course results therefore do not imply universal condition-independent process effects" (L3578).
16. **Negative empirical prior**: on current data, cold-split gains vanish (USDA, PE), and D7 < D5 on USDA/Bognár. The SSOT stop rule (§215.70) and §227.11 say to invest in data rather than deepen completion architecture. Risk: the programme keeps building D7 variants on E3 aggregates that cannot pass G15-9.

---

## 8. MAPPING TO THE 36-STEP SPINE (brief §9) — reconstructed, NOT from missing plan cards

**Step 01 (authority) / 02 (implementation audit)**
- Record PART XI as authoritative (L22) and §229 as superseded by §259 (L42782).
- Record the DEL-2 results (EXP-000001…000004) as **existing negative/partial evidence** under G15-2/G15-9. Do not re-run them as if new.
- Record the D-ladder numbering conflict, Plan v4 AZ6 L4700–4711 vs SSOT L18547–18611. The SSOT wins (authority order).

**Step 03 (state semantics)**
- Freeze value-status codes: TRUE_ZERO / NON_DETECT / BELOW_LOD / BELOW_LOQ / ABOVE_CAP / NOT_MEASURED / UNKNOWN (SSOT L23972–23980 + CS registry). TRUE_ZERO must be added to the CS registry.
- Freeze a per-variable observation mask in the state object (state contract L20/L31 already has a per-variable mask).
- Distinguish missing covariate from missing target (L23947–23955).

**Step 04 (evidence/provenance/similarity contracts)**
- Freeze one **tier crosswalk**:
  - SSOT E1–E6 (L16656–16661);
  - Plan/registry E7 SIMULATED (Plan v4 L594);
  - SSOT class `I` imputed (L24044) — repo maps IMPUTED → E6 (provenance_class_registry);
  - §223.13 fidelity levels, including "observed-derived structural augmentation", which has no tier code;
  - §246.6 RAG evidence classes;
  - `IMPUTED / MODEL-ESTIMATED` (L23926).
- Contract that completed cells are never citations (L23937).
- Add W_ipcj fields (L23375–23382) to the EVD contract.

**Step 05 (normalize EVD)**
- Required outputs: censor object with kind+limit+status; LOD/LOQ + `lod_loq_status`; basis (TRUE/APPARENT retention, wet/dry); yield_fraction; n/SD/range where present; value_origin (VO-00x).
- `log_fold_change` must never be computed from censored values (state contract L41).
- Log-RF target plus the raw RF definition preserved; "Do not clip RF > 1" (Plan v4 AM2 L3584).
- Gate: G15-1 field completeness (L22382). It is a status audit: every row has *status* fields, even when the value is UNKNOWN.

**Step 06 (source acquisition manifest)**
- Tag each source with its **regime D-A/D-B/D-C/D-D** (L23447–23461) and with the cold-start types it can support.
- Licence/release rights per C2 benchmark release (L24683).
- §227.8 list as candidate rows with licence UNVERIFIED flags.

**Step 07 (condition & measurement normalization)**
- Continuous T/t/pH/aw with `_lo/_hi/_type` (§216.1), kept continuous (not binned) per L23726/L23801.
- A condition-completeness mask per axis.
- Measurement **platform/method** (MEAS) normalization, because §222.8 platform controls depend on it.
- Output feeds the C mode of Y and the cold-condition-region split (L23473).

**Step 08 (scientific source lineage)** — NOT to be executed now
- Must produce study_id, lab, year, venue, platform, publication connected components (Plan v4 AM3 L3599–3613), independence groups, and USDA donor→recipient imputation links where identifiable.
- Required by: §220.8 study-disjoint; §221.18 item 6; G15-6 "real, study-disjoint calibration"; C3 year/source covariates.

**Step 09 (extraction & verification machinery)**
- Implement the §223.8 workflow (L24161–24169) with exact source pointer + human verification + tier promotion.
- G15-H (L22395).
- The LLM extractor is "candidate real-data acquisition" (L24867), never synthetic chemistry.

**Step 10 (20-row mechanism pilot)**
- The pilot schema should exercise the hard cases: ≥1 NON_DETECT/BELOW_LOD row, ≥1 RF>1 formation row, platform, replicate n/SD, within-study contrast, so the §222 statuses are tested end to end. INFERENCE: this is a recommendation, not SSOT text.

**Step 11 (Wave-1 verified mechanism evidence)**
- Use the §224.8 active literature loop and §224.3 priorities (uncertainty, downstream value, **connectivity to cold entities**, disagreement).
- Log acquisition decisions (random vs prioritised) so §227.11's active-learning promotion rule can be evaluated later.

**Step 12 (structured database evidence)**
- D-A/D-B ingestion: FDC pairs as E6 candidates (circularity flag); FooDB/FlavorDB composition as *side information* (coupled matrices, L23805–23812), not as targets.
- Keep regimes separate (L23463).

**Step 13 (large literature discovery corpus)**
- **Critical for MNAR**: capture paper-level metadata (year, food, process, target class, platform, venue) for *all discovered* papers, extracted or not. This defines the "studied" universe vs "never studied", which is the only defensible basis for a propensity model e(x) (§220.5). Without it, C3 can only use marginal-frequency proxies.
- INFERENCE, but follows directly from L23620–23629.

**Step 14 (coverage-driven evidence growth)**
- Frequency/support buckets (L23672–23674).
- Cold-entity connectivity targets.
- VoI ranking from the D7/D3 posterior (§224.3, §224.7).
- Compare against random/coverage-only acquisition (L24822).

**Step 15 (freeze DATA-EVIDENCE v1)**
- Produce the §229.3 artifact: **observed tensor + observation mask + evidence ledger + cold-start split registry**, plus the dataset card of §229.2 Step 1 (L24926–24933): support by food/process/condition/target, study/platform, censoring, tiers, cold categories, missingness patterns.
- Freeze the cell definition (AM1), split manifests with sha256 (`splits.py` already hashes), propensity features "before outcome inspection" (Plan v4 L3109), and the empirical conformal reporting (L3110).
- Gates: G15-1, G15-R.
- Freeze a **human-verified real calibration/test subset** (G15-H). Without it G15-6/G15-7 cannot pass.

**Steps 16–20 (procedure / state, D-D regime)**
- D-D is "dense structurally, nearly empty for measured chemistry" (L23461).
- Masks on recipe-derived conditions; "not filled by LLM guesses" (L26313).
- Sequence baselines for procedure (L23894, L24481), with step F1 / trust horizon.
- G15-11 needs true intermediate states (Step 19 gold trajectories).
- Recipe ingredient frequency can serve as a **popularity covariate** for propensity (L23621). Declare it as a cross-plane covariate only (INFERENCE).

**Step 21–23 (ontology, event→effect, applicability)**
- §223.7 weak/rule labels (E6) for coarse direction tasks/pretraining/extraction prioritisation, "Never treat rule labels as measured chemistry" (L24153).
- §226.2 "Only qualitative claims → rule/weak supervision + verified qualitative test set".
- Applicability decides the D-A × qualitative vs quantitative regime (L24477–24478).

**Step 24 (formula/model registry) / 25 (parameter-compatibility retrieval)**
- S-MECH families (L24084–24087): acrylamide frying kinetics, Maillard model systems, first-order Arrhenius nutrient/pigment degradation, two-compartment leaching.
- Parameter priors for domain randomization (L24091) come from the §216.2 kinetic table.
- Process/compound side-info descriptors feed D7 cold start.

**Step 26 (one focused deterministic simulator) / 27 (validate on real held-out evidence)**
- The validated domain is mandatory: §223.5 (L24121); §223.2 "Strongest synthetic source **when a validated model exists**" (L24080).
- `simulated_state_changes_schema_v1.csv` validation_scope / extrapolation_flag.
- Fail → simulator is RESEARCH_ONLY and Step 28 is blocked.

**Step 28 (controlled E7 synthetic prior)**
- Required content:
  - domain randomization (L24101–24107);
  - sampling list (L24091–24097, including LOD censoring and sparse grids, so the synthetic data mimics the real observation process);
  - ratio sweep 0/0.25/0.5/1/2/5× (L24192–24198);
  - TRTR/TSTR/mixed (L24209–24211);
  - memorization/two-sample/physics checks (L24217–24223);
  - provenance E7 SIMULATED; `may_enter_gold_evaluation=false`.
- Gate: G15-10 + HR-SYN-1 (L24251) + §227.11 synthetic promotion rule.
- Allowed uses are limited to the §223.4 list (L24111–24117).
- PFN-style kinetic prior is a stretch (L24117, L24457).

**Step 29 (TRANSITION_BOOTSTRAP_V0)**
- = §229.2 Step 2, D0–D6 floor, with G15-2.
- The repo contract (B-0..B-5) excludes TabPFN, which means G15-2 ("D0–D6") cannot be met by V0 as written. Either add D6 "where compatible" or record D6 as not-applicable with a reason.
- Splits S-1..S-7 map to §221.18 items 1–6 (masked-real ≈ S-1/S-2, cold food = S-3, cold process = S-4, study = S-6, source = S-7).
- Missing: cold compound/target and frequency buckets.

**Step 30 (strong tabular / sparsity bake-off)**
- = §229.2 Steps 3–4 / M2.
- Required set: D3 vs D5 vs D6 vs D7a biased MF, D7d FM, D7e soft-impute (mandatory when the matrix view is well-defined, L23781), D7b/c Bayesian side-info "if feasible", and the DropoutNet ablation.
- Protocol: the 9-item §221.18 protocol plus the 7-item §222.10 anti-inflation report.
- Propensity (covariate model, clipped IPS, naive vs weighted, positivity/overlap, AM4).
- Real-only conformal with grouping; risk–coverage.
- Gate: **G15-9 (or formal rejection)**, plus G15-6/7 and §227.11.
- Existing DEL-2 is a partial run of this step: D7a only, D6 missing, marginal propensity, censored-at-bound training.

**Step 31 (physics/condition features)**: G15-3 (process signal) and G15-5. Physics-derived exposure features are process side info (L23493).

**Step 32 (focused kinetics)**
- D8; G15-4; §224.4–224.6 identifiability-driven acquisition; C5 (L24720–24728); M3.
- First experiment per §224.11 (L24379–24384).

**Step 33 (mechanistic vs ML vs hybrid)**
- D9; C4 comparison set (L24711–24718); M4 (L24551–24558); G15-HYB; G15-10 if synthetic pretraining is used.
- "Only after D8 is credible" (L24977).

**Step 34 (short rollout)**: G15-11; M5 (L24562–24567).

**Step 35 (representation ladder)**
- Supplies side info (L23480–23499) and two-tower embeddings (L23874–23884).
- Representations enter L15 only as ablations after their gates (L22976).
- FAISS only after representation validation (L24627).

**Step 36 (Evidence compiler → RAG → FlavorTwin)**
- The §225.1 cascade.
- Completed cells exposed as `IMPUTED / MODEL-ESTIMATED` (L23926), MODEL_ESTIMATED_MATCH (L26761), RQ16-21.
- G15-I logging; G15-12/G15-INV + M6 for the FlavorTwin inverse step (L24571–24575).
- §229.8: benchmark before generic RAG front-end (L25073).

---

## 9. Contradictions, stale items, underspecified parts, open research questions

**Contradictions / inconsistencies**
1. **D-ladder numbering**: Plan v4 AZ6 (L4700–4711) contradicts SSOT §209.17 (L18547–18611) and Plan v4's own AI6 (L3130–3139). SSOT governs. The plan text is stale (likely carried from the v12 neural sub-ladder that §209.17 L18613 demotes).
2. **Evidence-tier vocabularies**: SSOT §201.7 defines E1–E6 only (L16656–16661); Plan v4 L588–595 and `evidence_tier_provenance_map_v1.csv` add E7 SIMULATED; SSOT §222.9 uses class `I` (L24044); the repo maps IMPUTED → E6 (`provenance_class_registry_v1.csv`). E6 then mixes "heuristic/qualitative" with "imputed/model-estimated", although §223.13 (L24236–24240) ranks imputed *above* mechanistic synthetic and rule labels. Structural augmentation (L24234) has no tier code. A single crosswalk is required (Step 04).
3. **Censoring handling**: DEL-2 trains censored rows "at lower bound 0.975" (all `reports/del2/*_results.md`). This conflicts with §222.5 (L23998, censored likelihoods preferred), §222.2 spirit (no default substitution), and the repo's own state contract L40. Evaluation is censor-aware; training is not.
4. **Cap semantics**: USDA "100" → GT_CAP 97.5 and Bognár "1.00" → GT_CAP 0.995 (REPO). Plan v4 AM2 says "Do not clip RF > 1" (L3584). Treating exactly-100% as right-censored is a project interpretation of source rounding/capping. The justification is not found in the files I read: UNVERIFIED (check `tools/ingest_usda_r6.py`, USDA R6 documentation, and the Bognár report preface).
5. **Propensity implementation vs spec**: DEL-2 propensity is "from marginal frequencies" (WORKLOG S017 L115), but §220.5 (L23620–23625) specifies year/platform/source-type covariates and Plan v4 AM4 requires calibration/positivity/sensitivity reporting. "MAE IPW" in DEL-2 is not the C3 analysis.
6. **G15-2 vs bootstrap V0 contract**: G15-2 requires D0–D6 (L22383), while V0 excludes TabPFN (bootstrap contract §3) and DEL-2 skipped D6.
7. **§216.12 minimum package vs PART XI**: the package (L22992–23031) lacks completion/propensity/mask-audit modules. It is stale relative to §226.4 M2.
8. **"Gold" vs E3**: G15-H applies to LLM-extracted rows. For E3 database rows the tier map says human verification is "needed for held-out test labels (G14-3, G15-H)". The SSOT G15-H text covers only LLM-extracted rows (L22395). Clarify whether E3 test rows require verification. The bootstrap contract says "no row is called Gold (conflict C2)".

**Stale items**
9. §229 is superseded (L24896, L42782), but no later section seems to restate the sparsity implementation order (my grep after L25080 found only §240.4–240.5, RQ16-20/21 and a diagram, L27710). §259/§279 not read: UNVERIFIED.
10. §219.4's density figure is `[SOURCE-REPORTED]` and must be recomputed. Repo DEL-2 densities and my DIAG density use inconsistent cell definitions (see §1.11).

**Underspecified**
11. G15-9 "beats": no metric, margin, CI rule, or rule for how many of the 4 cold tests must be won; "D5/D6" when D6 is inapplicable is undefined.
12. G15-6 "acceptable task-specific coverage/width"; G15-10 "unacceptable calibration damage": no numeric tolerance.
13. "Masked-real-cell holdout" (L23911) vs pair holdout: is it random cell masking within observed pairs? The mask pattern itself (MCAR masking of observed cells) re-introduces the iid assumption the section warns against. Needs a structured-masking design.
14. Cold-condition-region and cold study/platform are listed as cold-start types (L23473–23474) but omitted from the §221.18 protocol and the C2 split list (only "study/source; platform/matrix where possible").
15. Universe definition for propensity (which unobserved cells count as "could have been studied") is not given anywhere.
16. Tier weights q (L23514) remain `[PROPOSED-PILOT]` (L16672) with no tuning protocol beyond "highest-quality validation subset".
17. The ratio sweep is defined "relative to real", but per-target, per-regime or global is not stated.
18. The active-learning gate has no metric definition beyond "uncertainty/error per acquired observation" (L24822).
19. No rule for how D-A aggregate rows with NOT_IDENTIFIABLE study ids enter "study-disjoint" headline tests. Plan v4 AM3 says report non-feasibility and use source-held-out instead (L3610–3613). Cross-source overlap is tiny (67 cells USDA–Bognár).

**Open questions needing external research** (none verified in this run; all to be traced to primary sources)
- R1 Conformalized matrix completion under non-exchangeable/MNAR/clustered missingness. Candidates: Gui, Barber & Ma, "Conformalized matrix completion", NeurIPS 2023; Barber, Candès, Ramdas & Tibshirani, "Conformal prediction beyond exchangeability", Ann. Stat. 2023; group-conditional/Mondrian conformal; weighted conformal under covariate shift (Tibshirani et al., NeurIPS 2019). UNVERIFIED. Decision impact: the G15-6 method on cold splits (current under-coverage 0.72–0.87).
- R2 MNAR-aware recommender evaluation: IPS/SNIPS/DR (Schnabel et al., ICML 2016 "Recommendations as Treatments"; Wang et al., ICML 2019 doubly robust joint learning). UNVERIFIED. Decision impact: C3 design and propensity covariates.
- R3 Censored-likelihood regression for capped retention, e.g. Tobit/censored GBDT. Check XGBoost's `survival:aft` objective as an interval-censored option (UNVERIFIED), and censored GPs. Decision impact: replaces the "train at 0.975" assumption.
- R4 TabPFN v2 (Hollmann et al., Nature 2025) CPU feasibility, row/feature limits, weight licence. UNVERIFIED. Decision impact: whether G15-2's D6 is runnable.
- R5 Macau/SMURFF (Simm et al.) availability/licence and FM libraries. UNVERIFIED. Practical constraint per L23751.
- R6 Cold-start ablation DropoutNet (Volkovs et al., NeurIPS 2017). UNVERIFIED.
- R7 Left-censored imputation QRILC/GSimp (metabolomics; Wei et al. 2018 for GSimp). UNVERIFIED. Only relevant once GC-MS D-B data arrive.
- R8 Optimal experimental design for Arrhenius/first-order kinetics (D-optimal designs for nonlinear kinetic models in food engineering). Needed for C5/Step 32.
- R9 Data licences: Phenol-Explorer, FooDB, FoodAtlas, FlavorGraph, Recipe1M+, OpenPI — release rights for the C2 benchmark split manifests.
- R10 Whether any public food-process dataset records non-detects/LOD at row level (GC-MS volatile studies). Decision impact: whether §222.3 statuses beyond GT_CAP will ever be populated.

---

## 10. LOOK-AHEAD — fields/metadata earlier steps must capture

Each item names the earliest spine step that must capture it (INFERENCE; derived from the SSOT lines cited).

| # | Field / metadata | Needed later by | Capture at step | SSOT anchor | Repo status |
|---|---|---|---|---|---|
| LA-1 | `value_status` ∈ {TRUE_ZERO, NON_DETECT, BELOW_LOD, BELOW_LOQ, ABOVE_CAP, NOT_MEASURED, UNKNOWN} | censored likelihoods, anti-inflation, S-MECH LOD simulation | 03, 05 | L23972–23980, L16696–16712 | CS registry exists, no TRUE_ZERO; only GT_CAP populated |
| LA-2 | `lod`, `loq`, `lod_unit`, `lod_loq_status` | §222.5, §223.2 LOD censoring sampling | 05, 09, 12 | L22776, L24096 | null in all 17,978 rows |
| LA-3 | censor kind + limit + **cap justification** (source text pointer) | Step 30 censored training | 05 | L23998–24000 | kind/limit present; justification UNVERIFIED |
| LA-4 | measurement `platform` / `method` / assay (GC-MS, HPLC, …) and detectable-target panel per platform | §222.8 platform controls, platform-disjoint split, propensity covariate | 07 (MEAS), 09, 12 | L23380, L23499, L23623, L24029–24038 | MEAS = 3 rows |
| LA-5 | `study_id`, `lab`, `year`, `venue`, publication-component id, independence_group | study-disjoint, cluster bootstrap, propensity year covariate | 08 | L23503, L23622, L23660–23664 | PE only; USDA/Bognár NOT_IDENTIFIABLE |
| LA-6 | replicate `n`, SD/SE/range, aggregation type (mean/median/single) | W tensor, q weights, noise model, S-MECH noise | 05, 09 | L23378, L16668–16674; Plan v4 AM2 L3591–3592 | UNVERIFIED (not profiled) |
| LA-7 | yield factor, wet/dry basis, before/after basis, normalization status | G15-1, structural augmentation | 05 | L22382, L24130–24131; AM2 L3586–3590 | basis present; yield_fraction UNKNOWN 13,612 |
| LA-8 | `value_origin` incl. SOURCE_IMPUTED / SOURCE_IMPUTATION_POSSIBLE and **donor food id** where identifiable | fold grouping (donors with recipients), circularity flags (FDC vs R6) | 05, 08, 12 | L24040–24048 (imputed tier provenance) | VO registry exists; donor links absent |
| LA-9 | `evidence_tier` + `provenance_class` + `verification_status` + `extraction_method` + `explicit_or_inferred` + exact source span/table | G15-1, G15-H, §223.8 | 04, 09 | L22784–22787, L24161–24169 | tier/verification present; 0 human-verified |
| LA-10 | continuous `T_value/T_lo/T_hi/T_type`, `t_*`, pH, aw, moisture_before/after, medium, geometry; **per-axis completeness mask** | C mode, cold-condition region, physics features, kinetics | 07 | L22745–22763, L23492, L23726, L23801 | moisture/pH UNKNOWN 100%; T UNKNOWN 66%; t UNKNOWN 83% |
| LA-11 | canonical `ingredient_id` (FoodOn/category), `process_id` + family/leaf, `compound` InChIKey | entity resolution for D7 rows/columns; cold food/process/compound | 05, 07I/ING, 12 | L24430–24437, L23482, L23490, L23497 | ingredient_id null 6,409/17,978 |
| LA-12 | food side info: proximate composition, matrix properties (link to FDC id) | coupled matrices, cold food | 12 | L23484–23486, L23807 | FDC pairs only (not ingested) |
| LA-13 | compound side info: fingerprints/descriptors, compound class | cold compound | 12 (MOL) | L23497–23498, L23839–23841 | RDKit blocker noted (WORKLOG L157) |
| LA-14 | **discovery-corpus paper metadata for unextracted papers** (food, process, target class, platform, year, venue) | propensity universe e(x), C3, active literature loop | 13 | L23620–23629, L24345–24353 | not started |
| LA-15 | entity popularity/frequency (literature count; recipe-corpus frequency as a separate-plane covariate) | propensity, frequency buckets | 13, 16–20 | L23621, L23672–23674 | recipe frequencies derivable; not registered |
| LA-16 | acquisition log: why each paper/cell was acquired (random / coverage / VoI score / model version) | §227.11 active-learning promotion, selection-bias accounting | 11, 14 | L24822, L24297–24302 | not present |
| LA-17 | regime tag D-A/D-B/D-C/D-D per row/source | no flattening, regime×technique map | 06, 15 | L23447–23463, L24475–24481 | not a field (INFERENCE: derivable from design/origin_type) |
| LA-18 | time-series ids: `trajectory_id`, `timepoint`, `kinetic_experiment_id`, initial conditions, temperature schedule | D8/D9, S-MECH priors, C4/C5 | 11–14 | L22789–22792, L22804–22820 | none (no D-C data) |
| LA-19 | split registry entries: split_id, family (masked-real, cold food/process/compound/pair/condition/study/platform, source), sha256, frozen-before-outcome flag | C2 benchmark, G15-R | 15 | L23911–23919, L24672–24681; Plan v4 L3104–3110 | `splits.py` hashes splits; no registry file found (UNVERIFIED) |
| LA-20 | `dataset_version`, ontology version, unit-normalization version, evidence-tier-policy version, target definition | G15-R, §216.6 | 05, 15 | L22887–22894 | partially (schema_version, extraction_version) |
| LA-21 | for synthetic rows: simulator_id/version, parameters + source, uncertainty, validation_scope, extrapolation_flag, ratio-sweep id, `may_enter_gold_evaluation=false` | G15-10, HR-SYN-1 | 24, 26–28 | L24089–24097, L24251 | `simulated_state_changes_schema_v1.csv` defines it (no rows) |
| LA-22 | for imputed rows: class `I` (or crosswalked tier), imputer id/version, fold id, inflated-noise weight | §222.9 | 04, 30 | L24042–24048 | no `I` code in repo |
| LA-23 | within-study contrast id / shared-reference id (pairs derived from the same study) | structural augmentation, clustered uncertainty | 05, 08 | L24129–24135 | not present |
| LA-24 | recipe-plane masks for conditions (never LLM-filled) | D-D regime, §240.4 | 16–20 | L26313 | 07H normalizer outputs (check UNKNOWN handling, UNVERIFIED) |

Highest-leverage look-ahead items: **LA-4 (platform), LA-5 (study lineage, Step 08), LA-10 (conditions), LA-14 (discovery-corpus metadata for the propensity universe), LA-16 (acquisition log).** If these are not captured in Steps 07/08/13/14, C3 (MNAR), the platform-disjoint split, cold-condition region and the active-learning promotion rule cannot be evaluated later without re-extraction.
