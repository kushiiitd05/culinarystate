# READER ssot_l14 — SSOT v15 Level 14, §§197–205 (L15516–L17741)

Reader: ssot_l14. Source: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`. I read every body line from L15514 to L17782 (PART IX header through the §206 v11 change register), plus the cross-references at §144.2–144.3 (L8987–9002), §207.2–207.7 (L17815–17930) and §216.7/§218.3–218.4 (L22890–23230).
Repo cross-checks were read-only: `ledgers/schemas/{EVD,COND,MEAS,STUDY,EVT,STATE,SPLIT,RXN,PROC}.schema.json`, `registry/evd_contract_v1.csv`, `registry/ssot15_state_experiment_map.csv` (rows SX-06-*, SX-12-*, G14-1..12), `registry/evidence_tier_provenance_map_v1.csv`, `registry/censoring_registry_v1.csv`, `registry/condition_variable_registry_v1.csv`, `registry/recipe_condition_surface_forms_v1.csv`, `registry/data_source_acquisition_manifest.csv`, `reports/h_state/state_representation_contract_v1.md` (MP-1), `reports/h_state/transition_bootstrap_v0_contract.md` (TB-V0), `reports/del2/*_results.md`, `reports/del2/cross_source_v1.md`, `DECISIONS.md` D-018, and Master Plan v4.0 (`docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md`, MP4 below) at L335–372, L460–475, L585–630, L1630–1650, L3125–3150, L3405–3420.
**The 36-step plan cards are missing** (ctx.md). Every step mapping in §8 is my reconstruction from the 36 step titles in brief §9 plus SSOT/MP4/repo artifacts. None of it is text quoted from the missing plan.
The "supplied 656-line Level-14 research-consensus report" that §206.1 item 3 (L17748) says was integrated is **not in the repo** (grep over docs/ and reports/ finds nothing). So the proposed-pilot numeric thresholds (§202.17), the example tier-weight schedule (§201.7) and the "several thousand rows" MVP figure (§203.10) cannot be recovered verbatim: UNVERIFIED / NOT AVAILABLE.

---

## 1. Definitions, entities and data contracts

### 1.1 Status (§197.1, L15518–15526)
- Learning/conceptual spec: COMPLETE. Research design: "COMPLETE enough to begin data acquisition and low-complexity MVP work" (L15521).
- Data/evidence spine: **OPEN and may run in parallel with Levels 12–13** (L15522). SSOT header L174 repeats "OPEN / ACTIVE PARALLEL TRACK" (§§203–205, §259).
- Simple process-effect MVP: OPEN "once the minimum curated table exists" (L15523).
- Full learned process dynamics: **NOT FROZEN; DATA-CONSTRAINED** (L15524). Default advanced architecture: **NONE** (L15525).
- §206.2 (L17767–17782): "No learned z_m, z_i, z_R, z_C, z_{i,t} is frozen by documentation alone."

### 1.2 Canonical interface (§197.1, L15530–15565)
- Ingredient state: `z_{i,t} = F(z_i, S_t, P_t, θ_t, H_t)` (L15533–15543), with z_i = static identity, S_t = current observed/estimated state, P_t = process identity/family, θ_t = process conditions, H_t = prior process/event history (L15548–15552).
- Recipe scale: `z_{R,t} = A({z_{i,t}}, P_{≤t}, θ_{≤t}, H_t)` (L15556–15565).
- §198.1 restates the state encoder as `z_{i,t} = E(i, S_t, P_{≤t}, θ_{≤t})` (L15699–15707). H is implicit in the ≤t indexing here; this is a minor notational inconsistency with L15533.
- Task-conditioned `z_i^task = F(z_i, q)` is kept separate from process-conditioned `z_{i,t}^process` (§198.6, L15936–15950).

### 1.3 Frozen distinctions (§197.5, L15659–15670), quoted in short form
1 molecular identity ≠ process state; 2 ingredient identity ≠ ingredient state; 3 a static molecule embedding does not "cook"; 4 composition, concentration, products, physical state and relevance can change; 5 **state encoder ≠ transition model**; 6 procedure graph ≠ chemistry supervision; 7 attention/relevance weight ≠ concentration or causal contribution; 8 **an endpoint phrase ≠ a process condition if it directly reveals the target**; 9 unknown ≠ zero, non-detect ≠ absence; 10 cross-study association ≠ controlled causal effect.

### 1.4 Permanent model-selection rule (§197.4, L15623–15657)
- `target precision ≤ evidence precision` (L15629–15631).
- If the source says only "decreases", the target is directional/ordinal. Never manufacture "23.7%" (L15635–15647).
- A process label alone ("fried") gives no condition-resolved chemistry (L15649–15655).
- An aggregate retention factor without sample-level T, t, pH, a_w can teach a method/food-level effect, not a continuous kinetic law (L15657). **This bears directly on USDA R6, Bognár and Phenol-Explorer, which make up all 17,978 current EVD rows.**

### 1.5 Epistemic labels (§197.3, L15610–15621)
`[FROZEN-DESIGN]`, `[SOURCE-REPORTED]` (not independently re-verified), `[HYPOTHESIS]`, `[OPEN]`, `[DEFER]`, `[PROPOSED-PILOT]` ("engineering threshold/weight … not literature-derived truth", L15619). "No `[SOURCE-REPORTED]` claim becomes `[FROZEN]` merely by entering this SSOT" (L15621).

### 1.6 State key `[FROZEN-DESIGN]` (§198.1, L15725–15736)
Fields: `ingredient_id`, `state_id`, `process_event_chain`, `condition_bucket / raw condition fields`. "A practical state identifier may hash the event chain + condition representation, but the raw event/condition fields must remain separately inspectable" (L15736).
- Repo: STATE schema has `entity_id, state_version, previous_state_id, produced_by_event_id, belief, overrides_state_id, variables, quantity, location, form`. It has no explicit `process_event_chain` or `condition_bucket` field; the chain is reconstructable through `previous_state_id`/`produced_by_event_id`. EVD carries `matrix.initial_state`/`prior_processing` (free text). D-018 (DECISIONS L116) makes `prior_state_id`/`matrix_id` hashes of normalised raw descriptors with reversible lookup tables, which matches the L15736 rule. STATE/EVT ledgers are not yet created (DECISIONS L136: "EVT/STATE/ENTITY/… not created (BLOCKED_FUTURE_STEP)").

### 1.7 Compound-state channels (§198.2, L15738–15807)
- Molecule identity is invariant: `E_m(m) = z_m` (L15743). What changes is `c_{m,t}, presence_{m,t}, relevance_{m,t}, M_t` (L15750–15757).
- Aggregation `z_{i,t} = Agg({z_m, c_{m,t}, mask_{m,t}, evidence_{m,t}})` (L15763–15767).
- Three channels where data permit (L15774–15778): `present / absent / unknown`; `log-concentration or interval if known`; `formed-by-process / degraded-by-process / unknown`.
- Formation head `[HYPOTHESIS]` over a **closed, evidence-supported marker set** (L15782): furans, pyrazines, Strecker aldehydes, lipid-oxidation aldehydes such as hexanal, HMF, acrylamide (L15786–15791). "Do not expand this list without evidence" (L15793).
- Measurement platform is a confound. Record GC-MS / SPME-GC-MS / GC-IMS / GC-O / other/unknown (L15797–15807).
- Repo: MEAS.family enum includes HPLC, LC_MS, GC_MS, GC_IMS, GC_O, SPECTROPHOTOMETRY, … but **no SPME-GC-MS value** (UNVERIFIED whether it is folded into GC_MS + `extraction`). EVD has no row-level `platform` column; platform is reachable only via `measurement_method_id → MEAS.family` and `STUDY.analytical_platform_ids`. evd_contract_v1 reports "USDA/Bognar 3 MEAS records; PE null", so **platform is effectively unpopulated** for the existing evidence.

### 1.8 Process ≠ conditions (§198.3, L15809–15846)
- `P_t ≠ θ_t`. θ_t = [T(t), duration, moisture, pH, pressure, O₂, medium, geometry, …] (L15828–15829).
- Candidate physics-derived exposure features `[SOURCE-REPORTED/HYPOTHESIS]` (L15836–15844): peak/mean/final T; time above thresholds; log-duration; 1/T in Kelvin; generic Arrhenius-style exposure integrals at representative activation energies; cook/F-value-like cumulative exposure; moisture-gated effective time "when justified by a specific system". These are "**features/inductive biases, not proof of mechanism**" (L15846).

### 1.9 History (§198.4, L15848–15892)
- Non-commutativity: `T_{P2}(T_{P1}(S0)) ≠ T_{P1}(T_{P2}(S0))` (L15853–15855). H_t = {(P_1, θ_1), …, (P_t, θ_t)} (L15861–15863).
- Recipe flow/state graphs represent ingredients, tools, actions, intermediates, split/merge and qualitative before/after states (L15869–15876). They are useful for procedure structure and "do **not** automatically provide quantitative chemistry" (L15880).
- Order-swap validation set `[HYPOTHESIS]`: a small, evidence-backed matched set, e.g. pre-treatment→frying vs frying without/before pre-treatment. "Only include pairs where literature or controlled data support the comparison" (L15884–15892).

### 1.10 Process ontology (§199.1–199.2, L16031–16103)
- Example hierarchy (L16037–16065): thermal-moist {boil, steam, poach, pressure-cook}; thermal-dry {roast, bake, grill, broil}; thermal-fat {sauté, shallow-fry, deep-fry}; mechanical {cut, grind, whisk, mix}; biological {ferment, enzymatic}; cooling/storage {chill, refrigerate, freeze}.
- Ontology mapping `[SOURCE-REPORTED]`: FoodOn/LanguaL plus transformation/process ontologies "cited in the supplied report" (L16069). Rule: map to external terms where stable; keep a small custom hierarchy for modelling; **store the mapping/provenance rather than replacing one with the other** (L16073–16075).
- Representation: one-hot baseline → learned; preferred small-data form `z_P = [z_family; z_leaf; physics descriptors]` (L16093–16100). Text-derived verb embeddings are an **ablation, not the default** (L16103).
- Repo: PROC schema has `family, kind, parent_id, media, tool_ids, prerequisite_ids, required_condition_axes, likely_state_variable_ids, mechanism_families, corpus_frequency, evidence_coverage`. MP-1 §10 C7 says the 93 PROC mechanism_families are AI-drafted and unverified.

### 1.11 Continuous / time-varying conditions (§199.3–199.5, L16105–16171)
- "Store raw values first" (L16107). Transforms: t, log(1+t), T °C, 1/T_K, interval lower/upper bounds, learned numerical embeddings (piecewise/periodic) for neural models, cumulative exposure features (L16109–16117). Trees get raw + explicit derived physics features. Neural models may add learned numerical embeddings (L16119–16121).
- θ(τ) = [T(τ), pH(τ), a_w(τ), O₂(τ), pressure(τ), …] (L16128–16131). `[DEFER]` dense trajectory encoders for the general dataset (L16135). Summarise with peak/mean/final T, duration, time above threshold, exposure integrals, final/initial moisture (L16139–16143). Neural ODE/CDE only on focused kinetic/simulator data (L16145).
- Event schema extras (L16151–16161): medium, tool, geometry/cut/thickness/surface-area proxy, moisture, water_activity, pH, pressure, oxygen_exposure, mixing/agitation. Every feature is the tuple **`(value, unit, type, mask, provenance)`** (L16166–16168). "Do not force dense input coverage" (L16171).
- Repo: the COND schema covers duration, temperatures[], trajectory[], ph_initial/ph_final, moisture, water_activity, pressure, oxygen, salt, sugar, fat, medium, particle_size, geometry, agitation, power, humidity, heat_transfer_mode, tool_ids, biological, completeness_mask, each value typed {status, value, low, high, unit, uncertainty, qualitative, censor, raw}. That meets the L16166 tuple except for per-axis provenance, which sits at record level (`provenance`), not per axis. Population (evd_contract_v1 and MP-1 §7): temperature known 33% (6,015), duration 17% (3,083), **moisture/pH/aw 0%**.

### 1.12 Prerequisites and missingness (§199.6–199.7, L16173–16207)
- State-action relations take one of REQUIRED, TYPICAL, OPTIONAL, INCOMPATIBLE, UNKNOWN (L16177–16179). Procedure corpora are **soft priors / sanity checks** only. "Do not train chemistry targets from simple state-action co-occurrence" (L16183).
- Condition missingness types: POINT / INTERVAL / QUALITATIVE / UNKNOWN (L16189–16194), with the examples 180 °C → POINT, 170–190 °C → INTERVAL, "medium heat" → QUALITATIVE, not stated → UNKNOWN (L16198–16203). "Qualitative-to-numeric mappings are hypotheses and must retain a flag" (L16205). Trees use NaN + indicators; neural models use masks/tokens/bounds (L16207).
- Repo: the COND/EVD status enum is {MEASURED, RANGE, QUALITATIVE, CENSORED, UNKNOWN, NOT_APPLICABLE}, a superset of the SSOT four (POINT≈MEASURED, INTERVAL≈RANGE). `registry/recipe_condition_surface_forms_v1.csv` keeps "medium heat" (count 74,048) as `QUALITATIVE` with an empty `canonical_mapping`, which conforms to L16205. No numeric heat mapping is invented.

### 1.13 Endpoint leakage (§199.8, L16209–16233)
"until golden / until tender / until reduced by half" are observed endpoint/state information, not clean causal inputs. When predicting browning, "until golden" must not be an input. Store it as weak outcome annotation, stopping criterion and provenance (L16229–16233).
- Repo: `EVT.schema.json` has an `endpoint` field, which is good. Whether Step 07/07H separate endpoint cues from conditions is UNVERIFIED by this reader (grep shows no "endpoint" handling in the step07 reports beyond an unrelated interval-endpoint fix and API endpoint notes).

### 1.14 Process views and shortcut controls (§199.9–199.10, L16235–16270)
- Potential factorisation z_P^procedure, z_P^physical, z_P^chemistry, z_P^user/feasibility. Different heads may consume different condition subsets (L16241–16257).
- **Mandatory L14 shortcuts** (L16261–16268): ingredient-only; process-only; condition-only; study-ID-only; analytical-platform-only; tool-only where relevant. "A process-conditioned representation is credible only if its gain survives these baselines under grouped/cold splits" (L16270).

### 1.15 Canonical target (§201.1–201.3, L16512–16590)
- `(S_t, P_t, θ_t) → ΔS_t` or `S_{t+1} = S_t + ΔS_t` (L16516–16532); ΔS "may be observed at different fidelity" (L16534).
- Factorised ΔS = [Δchemistry, Δaroma, Δtaste, Δtexture, Δmoisture, Δnutrition, Δappearance] (L16540–16551). These are separate heads with unequal coverage (L16554).
- **Target-type ladder T0–T7** (L16556–16590):
  - T0 identity/co-occurrence: "widely available but not process-effect supervision".
  - T1 qualitative state labels (raw/cooked, cut/form, soft/tender/browned when explicitly supported).
  - T2 direction ↓ ≈ ↑.
  - T3 ordinal/ranking (low/med/high retention; process A > B).
  - T4 retention factor / log-fold-change regression.
  - T5 condition-resolved quantitative ΔS: "Thin; mostly focused studies".
  - T6 time-resolved trajectory: focused kinetic literature/simulators.
  - T7 cross-matrix mechanistic/counterfactual dynamics: `[OPEN / NOT SUPPORTABLE AS DEFAULT]`.
  - NOTE: the "T0–T7" target ladder **collides by name** with the Level-12 thread experiments "T0–T9" (MP4 L192, L281; SSOT L13213 "T8, T9"). See §9.

### 1.16 Retention / log-ratio / direction (§201.5–201.6, L16614–16649)
- RF = after/before, "or yield-adjusted formulation as defined by the source dataset". Candidate target log(RF+ε). "**Do not merge datasets with different retention definitions without explicit harmonization**" (L16632).
- Dead band: y = −1 if Δ < −δ; 0 if |Δ| ≤ δ; +1 if Δ > δ (L16638–16645). The source report proposes **±10%** as the first engineering dead band (L16647), labelled `[PROPOSED-PILOT]`, "not a frozen universal threshold" (L16649).
- Repo: D-018 creates a separate `log_retention_factor = ln(reported MEASURED retention > 0)` that is distinct from `log_fold_change`, because 278 of 3,859 PE rows deviate from after/before × yield by > 0.02 (DECISIONS L116). This conforms to L16632. MP-1 C4: USDA R6 mixes %TR and %AR undisclosed at row level and imputes from similar foods; Bognár is true retention with ~50% censoring.

### 1.17 Evidence tiers (§201.7, L16651–16674), verbatim list
```
E1 controlled experiment with measured conditions
E2 experiment with partial conditions
E3 curated database aggregate / retention table
E4 machine/LLM extracted + human verified
E5 machine/LLM extracted, not yet verified
E6 heuristic / qualitative / weak inference
```
- "Test labels should preferentially come from E1–E4 and be human verified" (L16664).
- Weighting: the source report's example tier-weight schedule is preserved only as `[PROPOSED-PILOT]`, tuned on the highest-quality validation subset. "Do not treat confidence weights as probabilities unless calibrated" (L16670–16674). **The schedule values are not in the SSOT** (not reproduced; the source report is absent from the repo).
- Repo/MP4 extend this to E1–E7, with E6 = "mechanism-family rule/heuristic (MODEL_ESTIMATED)" and E7 = "simulator output (SIMULATED)" (MP4 L589–596, EVD `tier` enum, MP-1 §6). D-018 rules that tier, verification_status, design_strength and provenance_class are **four separate export fields** and E3 is never promoted to E1/E2.

### 1.18 Literature-extraction fields (§201.8, L16676–16690)
Required: source DOI/citation; exact span/table; extraction method; human verification status; units; conditions; target definition. "**All held-out test values should be human verified**" (L16690).

### 1.19 Censoring (§201.9, L16692–16717)
ND / <LOD / unmeasured / true zero are distinct. "Do not substitute zero or LOD/2 by default." Use censored/Tobit-like likelihoods where data suffice. Always retain `censor_flag`, `LOD`, `platform` if known (L16711–16715).
- Repo: `registry/censoring_registry_v1.csv` has CS-001 DETECTED, CS-002 NON_DETECT ("NOT zero; left-censored"), CS-003 BELOW_LOD, CS-004 BELOW_LOQ, …, which conforms. D-018 (3): "`lod`/`loq` are null everywhere (the sources record only GT_CAP caps)". 5,894 EVD rows are censored.

### 1.20 Compound / sensory / constraints (§201.10–201.12, L16719–16761)
- Compound targets: Δc_m or `LFC_m = log((c_{m,t+1}+ε)/(c_{m,t}+ε))` (L16729–16735). At current scale, focus on evidence-supported marker compounds/classes, not open-vocabulary molecular output (L16737).
- Sensory: task-specific, labelled "composition-to-sensory approximation", evaluated against sensory evidence, bounded by mixture/matrix uncertainty. "**Do not claim palatability from process-conditioned embeddings**" (L16743–16750).
- Physics-informed soft constraints: non-negativity, degradation-only monotonicity, mass/retention bounds after yield correction, known thermal-dose relationships. "Do not apply generic constraints to formed compounds or open systems where mass leaves/enters the modeled boundary" (L16754–16761).

### 1.21 Process-event table: the minimum schema (§203.2, L17127–17189), verbatim field list
```
event_id, ingredient_id, ingredient_state_in, ingredient_state_out, process_leaf, process_family,
T_value, T_lo, T_hi, T_type, t_value, t_lo, t_hi, t_type,
medium, tool, geometry, moisture_value/range/type, water_activity_value/range/type,
pH_value/range/type, pressure_value/range/type, oxygen_value/category, mixing,
target_type, target_variable/target_compound, target_value, target_lo, target_hi, unit,
direction_label, ordinal_band, censor_flag, LOD, platform, study_id, source_id, doi_or_citation,
evidence_tier, verified_by, verification_status, extraction_method, explicit_or_inferred,
notes, dataset_version, split_id
```
Plus canonical external IDs: ingredient ontology ID; PubChem/ChEBI/InChIKey for compounds; process ontology mapping (L17185–17189).

**Field-by-field mapping to the existing repo (my read of the EVD/COND/MEAS/STUDY schemas):**
| §203.2 field | Repo location | Status |
|---|---|---|
| event_id | EVD `id` | present |
| ingredient_id | EVD `matrix.ingredient_id` | 64% populated (11,569/17,978) |
| ingredient_state_in | `matrix.initial_state` + `prior_processing`; `prior_state_id` hash (D-018) | free text; controlled vocab pending |
| **ingredient_state_out** | — | **ABSENT** (no output-state field in EVD; STATE ledger not created) |
| process_leaf / process_family | `process.process_id` / `process.family` | 99% process_id |
| T_value/lo/hi/type | COND `temperatures[]` typed values | 33% known |
| t_value/lo/hi/type | COND `duration` | 17% known |
| medium, tool, geometry | COND `medium`, `tool_ids`, `geometry`; EVD `matrix.geometry` | sparse |
| moisture/aw/pH/pressure | COND typed objects | **0% populated** |
| oxygen_value/category | COND `oxygen` | UNVERIFIED population (likely 0) |
| mixing | COND `agitation` | name differs |
| target_type | implicit in `derived.*` choice / SVAR family | no explicit `target_type` column (UNVERIFIED in export) |
| target_variable/compound | `target.state_variable_id`, `target.molecule_id` | 100% SVAR |
| target_value/lo/hi, unit | `before/after/derived.*` typed objects | present |
| direction_label | `derived.direction` (INCREASE/DECREASE/NO_CHANGE/MIXED/UNKNOWN) | 100% (UNKNOWN allowed) |
| **ordinal_band** | — | **ABSENT** |
| censor_flag, LOD | `censored`, `*.censor`; MEAS `lod/loq` | censor present; LOD null |
| **platform** | only via MEAS.family / STUDY.analytical_platform_ids | **effectively absent at row level** |
| study_id, source_id | `study_ids[]` + `study_id_status`; `source_id` | study present only for PE (3,870) |
| doi_or_citation | SRC/STUDY via source_id; `external_refs` | UNVERIFIED per row |
| evidence_tier | `tier` (export alias `evidence_tier`) | all E3 |
| verified_by, verification_status | `verification.verifier`, `verification.status` | 0 HUMAN_VERIFIED |
| extraction_method | `provenance.method` + `extraction_version` | present |
| explicit_or_inferred | `provenance_class` (export view, D-018) | export only |
| dataset_version | `extraction_version`; DATASET ledger | partial |
| **split_id** | SPLIT ledger (`strategy, seed, roles, assignment_sha256, leakage_report_path`) | SPLIT ledger **not created** (DECISIONS L136) |

### 1.22 Resource-fidelity record (§203.4, L17249–17263)
Every imported resource documents: what is measured; how; matched before/after?; T/t available?; analytical platform; quantitative/ordinal/qualitative; citation; licence; what is missing. `registry/data_source_acquisition_manifest.csv` has most of these columns (time_series_available, before_after_available, measurement_method_available, condition_coverage, licence, …), but not "analytical platform" as its own column (UNVERIFIED; it may sit in notes).

### 1.23 Evidence ledger for RAG (§203.8, L17330–17353)
Key: ingredient/state; process family + leaf; condition bucket / raw condition vector; target family; evidence tier; source/study (L17336–17343). Response policy: 1 retrieve closest evidence; 2 state what is directly observed; 3 state what is inferred; 4 attach uncertainty; 5 abstain/broaden outside coverage (L17347–17353). Generation must distinguish **retrieved evidence / model estimate / inference-extrapolation / unknown** (§198.8, L16012–16017). §198.8 retrieval key: (ingredient, process family, condition bucket) plus provenance, tier, observed target, uncertainty/interval and platform (L15998–16008).

### 1.24 Dataset card mandatory outputs (§203.9, L17355–17371)
Total rows; unique ingredients; unique processes/families; ingredient×process pair counts; target-type counts; evidence-tier counts; study/source counts; analytical-platform counts; coverage of T, t, pH, a_w, moisture, pressure, …; missingness by source/process; pair-frequency distribution; condition ranges; duplicate/conflict audit. All are generated **"before model selection"** (L17357).
- Repo: `reports/DEL1_data_card.md` exists. ssot15_state_experiment_map G14-2 = PARTIAL ("per-field coverage for new W4 fields absent").

### 1.25 Recipe-procedure boundary (§203.5, L17265–17297)
Procedure data give S0 → a1 → S1 → … structure without chemistry. The hard boundary is **procedure extraction quality ≠ chemistry-effect accuracy** (L17292–17296).

---

## 2. Models and baseline ladders

### 2.1 Small-data default (§200.1, L16276–16292)
In order: linear/ridge → LightGBM or equivalent GBT → TabPFN where scale/task allows → MLP with numerical embeddings + concat → FiLM-MLP → DeepSets / Set Transformer over molecule sets *only if compound-level data exist* → cross-attention *only if it earns its value*. The purpose is "not to declare trees universally superior. It is to establish a strong credibility floor" (L16292).

### 2.2 Conditioning ablation order (§198.5, L15894–15932)
identity-only → + process one-hot → + raw conditions → concat+MLP → FiLM/gating → molecule-set conditioning / cross-attention → history-aware model → reaction/mechanistic model only where data support it (L15898–15907). The formulas are concat `MLP([z_i; z_P; z_θ])` (L15912–15915) and FiLM `h' = γ(z_P, z_θ)⊙h + β(z_P, z_θ)` (L15920–15924). Cross-attention applies when ingredients are molecule sets or history is tokenised (L15928). **Hypernetworks `[DEFER]`** (L15932).

### 2.3 Encoder ladder S0–S10 (§200.2, L16294–16369)
| Rung | Content | Status |
|---|---|---|
| S0 | static identity z_i | baseline |
| S1 | shortcut predictors F(i), F(P), F(θ) | mandatory |
| S2 | concat+MLP / tabular joint F([z_i, z_P, z_θ]) | MVP |
| S3 | gated/FiLM γ(P,θ)⊙h + β(P,θ) | MVP ablation |
| S4 | process-conditioned molecule-set aggregation A({z_m, c_m, mask_m}, P, θ) | needs compound data |
| S5 | composition-aware: predict c_{m,t}, not just attention | needs concentrations |
| S6 | history-aware GRU / small transformer over events | needs order labels |
| S7 | latent state-space h_{t+1} = f(h_t, u_t) | L15 territory |
| S8 | reaction-aware graph, "only for known species/edges" | focused |
| S9 | dynamic reaction/state graph | **[DEFER]** for general food (L16365) |
| S10 | hybrid mechanistic + neural residual | "focused stretch goal for one or two well-characterized reactions/systems" (L16369) |

**Name collision**: L14 "S0–S10" encoders vs TB-V0 split ids "S-1…S-7" (`reports/h_state/transition_bootstrap_v0_contract.md` L20). Distinct meanings, risk of confusion.

### 2.4 Molecule-set encoders (§200.3, L16371–16397)
M_i = {(m, c_m, mask_m)}. Benchmark concentration-weighted mean, Deep Sets, Set Transformer and conditioned attention. "Attention is not explanation". When attention is reported, pair it with a perturbation test (remove top-k attended → measure prediction change) and with concentration/evidence analysis (L16388–16397).

### 2.5 Reaction-aware / hybrid (§200.4, L16399–16429)
`[SOURCE-REPORTED]` reaction NNs and UDE-style hybrids need much stronger time-resolved data than general food datasets provide. For general L14: "Do **not** start here" (L16407). Focused stretch: choose one system, "e.g. a focused acrylamide/browning case", and compare mechanistic vs pure ML vs mechanistic+neural residual. "The point is a controlled scientific experiment, not a universal food simulator" (L16429).

### 2.6 History models (§200.5, L16431–16447)
Ladder: order-invariant sum/mean of events → GRU over event tokens → small transformer only if needed. Evaluate on matched order-swap examples. "Do not use a large sequence model if the labels cannot supervise sequence effects" (L16447).

### 2.7 Recipe-level/intermediate nodes (§200.6, L16449–16467)
Many-to-one: ingredients → intermediate → later state. Parent aggregation uses mass/quantity weighting where known, explicit provenance and state/condition metadata. "A DAG/GNN may be useful for CulinaryState-RAG and procedural tasks even when chemistry supervision is sparse" (L16467).

### 2.8 Multi-task (§200.7, L16469–16484)
Start with a shared backbone, separate heads, explicit missing-target masks and static normalised task weights. Add uncertainty weighting / GradNorm-like / PCGrad-like **only if measured gradient/task conflict justifies them** (L16478–16484). Loss `L = Σ_k M_k λ_k L_k` with M_k the label mask (L16606–16612). Losses per target (§201.4, L16594–16601): Huber/MAE; heteroscedastic Gaussian NLL; BCE/CE; ordinal; ranking (paired process comparisons); interval/censored likelihood.

### 2.9 Contrastive (§200.8, L16486–16495)
`[DEFER / LOW PRIORITY]` for chemistry. If used, positives must come from evidence-supported state/process/condition equivalence, not name similarity.

### 2.10 Recipe self-supervision (§201.17, L16821–16827)
Masked-ingredient / next-action objectives are useful for procedural representation. Transfer to chemistry is `[OPEN]`. Use them only as initialisation/auxiliary, and **keep them only if they improve cold-process chemistry/state prediction**.

### 2.11 Simulation pretraining / multi-fidelity (§201.13, L16763–16774)
Pipeline: mechanistic simulator → synthetic conditions/outcomes → pretraining or residual learning → real-data fine-tuning, for a focused kinetic system only. "Synthetic rows must retain a source/fidelity flag and must not be silently pooled with measurements" (L16774).

### 2.12 Hierarchical prediction (§201.14, L16776–16789)
direction → broad band/qualitative state → quantitative estimate → compound-specific detail, "only as evidence allows".

### 2.13 MVP / stretch / defer (§204)
- Do-first, in order (§204.2, L17407–17450): **A** process-event table + provenance + evidence tiers (value very high, risk low, foundational); **B** cold/grouped splits + shortcut baselines ("likely a major research contribution because random-split optimism is expected", L17419); **C** physics/condition features (raw T, t; log t; 1/T; cumulative exposure; moisture-gated exposure only with system-specific evidence); **D** strong tabular (linear/ridge, GBT, TabPFN where appropriate); **E** mixed targets (direction, ordinal band, retention/log-ratio, paired ranking); **F** calibrated abstention; **G** recipe-state graph schema.
- MVP-ablation (§204.3, L17452–17461): concat MLP with numerical embeddings; FiLM MLP; simple DeepSets if concentration data exist; GRU only if order labels support evaluation. "These are ablation candidates, not mandatory winners."
- Stretch (§204.4, L17463–17485): molecule-weighted process-conditioned ingredient state `z_{i,t} = Σ_m w_{m,i,t} z_m` ("High relevance to FlavorTwin, but data hungry"); focused hybrid kinetic + neural residual (one or two systems); hierarchy-aware/hyperbolic process embedding "only if simple hierarchy embeddings fail on process-disjoint transfer"; larger recipe-state GNN if parsing/intermediate-graph coverage becomes strong.
- **Defer list** (§204.5, L17487–17499): general neural ODE/CDE over food trajectories; universal dynamic reaction graph; hypernetwork-conditioned chemistry; large contrastive process pretraining for chemistry; large recipe-SSL-to-chemistry claims; open-vocabulary compound generation; universal learned non-commutative chemistry operators. "These may become valid if future data change the constraint."
- Semester compression (§204.6, L17501–17535): Phase A data foundation (schema, retention datasets, first volatile anchors, ontology normalisation, dataset card) → Phase B baselines + splits (null/shortcut, six split families, LightGBM/TabPFN, physics features) → Phase C neural conditioning + uncertainty (concat MLP, FiLM, ensemble/calibration/conformal wrapper, L14 gates) → Phase D RAG demo (evidence-ledger retrieval, citation, "estimated" flag, uncertainty interval, abstention). "Everything beyond this is stretch."
- Tooling (§204.7, L17537–17556): Python, pandas/Polars, scikit-learn, LightGBM/XGBoost, TabPFN where appropriate, PyTorch, PyG only if graph experiments are earned, RDKit, MLflow/W&B, DVC/versioned snapshots, pronto/Owlready2, MAPIE/crepes or a transparent custom conformal implementation. "Tool choice is secondary to dataset/version/split reproducibility."
- Strongest current candidate, not frozen (§207.5, L17863–17892): canonical identity + process hierarchy + raw/physics condition features + evidence-aware mixed targets + strong tabular baseline + concat/FiLM ablation + pair/source-disjoint evaluation + calibrated abstention. Extend with compound set + concentration/mask/evidence where compound data exist.

### 2.14 Repo baselines already run (DEL-2, EXP-000001..4)
`reports/del2/*_results.md` contains D0 persistence, D1 global mean, D2 process mean, D3 hierarchical shrinkage, D4 nearest compatible evidence, D5 gradient boosting, D7 biased MF side-info, on random / pair_holdout / matrix_disjoint / process_disjoint / study_disjoint (PE only). D6 TabPFN was "SKIPPED (not installed; GPU)". Single seed 7. Headline facts I checked:
- USDA R6 (6,994 rows, 2,620 censored), pair_holdout censor-aware MAE: D5 0.0390 vs D3 0.0659 vs D2 0.0872 vs D1 0.1057. GBT wins on pair-holdout. study_disjoint "NOT POSSIBLE (single source family)".
- Bognár (6,594 rows, 3,274 censored), pair_holdout: D5 0.0443 vs D3 0.0666 vs D1 0.0922.
- Phenol-Explorer (3,870 rows, 146 matrices, 33 process signatures, 161 targets, grid density 0.00267), pair_holdout: **D1 global mean 0.7263 = D7 0.7263 ≤ D0 0.7298 < D4 0.7652 < D3 0.7725 < D5 0.7901**. study_disjoint: **D0 persistence 0.5577 best**, D5 0.7551. process_disjoint: **D0 0.3676 best**. So on the only multi-study source, **no learned model beats persistence/global mean under cold splits**. This is a retained negative result, consistent with the §202.16 promotion rule.
- Conformal-90 coverage under shift ranged roughly 0.77–0.93 in these tables (ssot15 map SX-12-05 says "0.72–0.87 under shift"; I did not reconcile the exact range).
- DEL-2 trains "censored rows at lower bound 0.975 (assumption)". This is in tension with §201.9 (see §9).

---

## 3. Experiments / hypotheses / RQs (as stated in §§197–205)
No numbered RQ IDs exist in L14 (unlike RQ16/RQ13E). The implicit experiments, with anchors:
1. **H-L14-core** (§197.6, L15680): "whether process conditioning improves prediction of supported coarse or quantitative state changes beyond ingredient-only, process-only and tabular baselines, with calibrated abstention outside the evidence region", on a provenance-tracked process-event dataset with leakage-safe cold-pair/source splits.
2. Conditioning ablation ladder (§198.5 L15898–15907; §200.2 S0–S10).
3. Condition-vs-label test (G14-7, L17084): does adding θ beat process label only?
4. Physics features vs raw conditions (§198.3 L15836–15846; §204.2C).
5. Process-hierarchy transfer: process-disjoint with parent family retained (Split 3, L16861–16865); hyperbolic embedding only if simple hierarchy fails (L17479–17481).
6. Text-verb embedding ablation vs hierarchy/physics (L16103).
7. Order-swap matched set (§198.4 L15882–15892; §200.5 L16445): order-invariant vs GRU.
8. Molecule-set encoders with top-k perturbation test (§200.3 L16381–16397).
9. Formation head over a closed marker set (§198.2 L15780–15793).
10. Focused mechanistic vs pure ML vs hybrid residual (§200.4 L16409–16429), e.g. acrylamide/browning.
11. Simulation pretraining → real fine-tuning, with fidelity flag (§201.13).
12. Multi-task conflict measurement before GradNorm/PCGrad (§200.7).
13. Recipe-SSL initialisation transfer to cold-process chemistry (§201.17, `[OPEN]`).
14. Counterfactual/monotonicity diagnostics: vary T, t, moisture/pH holding all else fixed (§200.9 L16499–16506; §202.6 L16936–16957).
15. Representation probes on frozen z_{i,t}: identity, process, condition bin, moisture/browning (§202.13 L17038–17051). The diagnostic: "If process is perfectly decodable but outcome is not, the representation may be mostly process identity" (L17051).
16. Missingness robustness: natural subsets vs controlled masking at multiple rates; performance vs number of observed condition fields (§202.7 L16959–16968).
17. Cross-platform harmonisation: same food/process, different platform; platform-disjoint; intersection vs union vocabularies (§203.7 L17317–17328).
18. Grouped permutation/ablation of feature families: identity, process, continuous conditions, physics-derived conditions, source/study, platform, tool/medium/geometry, history (§202.5 L16921–16934).
19. Tier-weight tuning on the highest-quality validation subset (§201.7 L16670–16674).
20. Dead-band sensitivity: ±10% pilot (L16647). The SSOT does not explicitly require a sensitivity sweep. I infer one is needed (my recommendation, not SSOT text).
21. Matrix-transfer tests (§205.2 L17596–17604).
22. Literature extraction reliability (§205.5): this maps to MP4 SX-06-08 "LLM literature-extraction accuracy vs human verification" (MP4 L362). That repo row is BLOCKED_HUMAN: "634 rows; 0/40 verified".

MP4 operationalisation: B12 SX-12-01…05 (MP4 L464–471); B06 SX-06-01…08 (L355–368); B13 DEL-2 D0–D7 (L3125–3150). The registry maps these in `registry/ssot15_state_experiment_map.csv` rows 16–23 and 55–59 with status MISSING/PARTIAL.

---

## 4. Gates, promotion and stop rules (exact quotes)

### 4.1 G14 acceptance gates (§202.16, L17074–17090), verbatim
- **G14-1** (L17078) "Versioned process-event schema + provenance/evidence tier/missingness."
- **G14-2** (L17079) "Dataset card with per-field coverage, source/study/platform distribution."
- **G14-3** (L17080) "Human-verified held-out test labels."
- **G14-4** (L17081) "Shortcut/null/tabular baselines completed."
- **G14-5** (L17082) "Ingredient × process pair-holdout completed."
- **G14-6** (L17083) "Source/study-disjoint evaluation completed where study IDs exist."
- **G14-7** (L17084) "Condition contribution tested against label-only."
- **G14-8** (L17085) "Missingness robustness reported."
- **G14-9** (L17086) "Calibration / interval coverage / risk–coverage reported."
- **G14-10** (L17087) "Evidence-quality stratification reported."
- **G14-11** (L17088) "Multiple-seed / clustered uncertainty reported for learned models."
- **G14-12** (L17089) "Final decision record states what is supported, what is extrapolated, and where the system abstains."
- The SSOT labels all of them "Hard design/data gates" (L17076). **None carries a numeric threshold.** They are completion/reporting gates, not performance gates.
- Repo status (`registry/ssot15_state_experiment_map.csv` L79–90): G14-1 PARTIAL (moisture/pH/aw never populated); G14-2 PARTIAL; **G14-3 MISSING (0 human-verified EVD rows)**; G14-4 PARTIAL (DEL-2 D0–D7 retention); G14-5 PARTIAL; G14-6 PARTIAL (PE only); G14-7 MISSING; G14-8 MISSING; G14-9 PARTIAL; G14-10 MISSING (trivially: all rows are E3, so stratification is impossible); G14-11 PARTIAL (grouped CIs, single seed); G14-12 MISSING.

### 4.2 Model-promotion rule (§202.16, L17091–17103)
"A neural encoder does **not** need to beat a strong tree model for Level 14 to be scientifically successful. If `LightGBM/TabPFN > FiLM/cross-attention` under the strongest splits, ship/report the simpler model. That is a valid result."

### 4.3 Permanent L14 promotion rule (§205.10, L17683–17712)
`generalization gain + evidence fidelity + calibration + robustness > shortcut explanation + added complexity` (L17688–17700). Operationally: beat the relevant null/shortcut/tabular baseline; survive pair-holdout; survive source/study grouping where possible; quantify missingness sensitivity; quantify evidence-tier performance; calibrate uncertainty; state when the system abstains; "do not claim chemistry beyond the target fidelity" (L17705–17712).

### 4.4 Other binding rules with promotion force
- §202.4 (L16919): "A complex encoder that fails to beat these under cold/grouped splits has not earned promotion." The mandatory comparison list (L16906–16917) is global/process mean, ingredient-only, process-only, conditions-only, study-ID-only, platform-only, simple linear/ridge, LightGBM/strong tree, TabPFN where appropriate, concat neural model.
- §199.10 (L16270): gain must survive shortcuts under grouped/cold splits.
- §202.12 (L17028–17036): ≥5 seeds for neural models; study-level bootstrap rather than naive row bootstrap when rows are clustered; paired comparisons on identical folds; macro metrics across processes/targets; CIs. "Do not declare architecture superiority from one split/seed."
- §202.1 (L16845): "Headline Level-14 evidence comes from grouped/cold/OOD splits." Random is reference/sanity only (L16851).
- §202.3 (L16898–16900): headline = **pair-holdout + source/study-disjoint**, "when sample size permits".
- §202.8 (L16983): "Do not let a large weak-label set hide poor performance on controlled measurements."
- §203.6 (L17315): "No unverified extraction may enter the gold test set."
- §201.16 (L16819): "No model prediction is promoted to a causal process effect without controlled/mechanistic support."
- §201.11 (L16750): no palatability claims from process-conditioned embeddings.
- §201.13 (L16774): synthetic rows flagged, never silently pooled.

### 4.5 Proposed-pilot thresholds, NOT frozen
- §201.6 dead band **±10%** (L16647), `[PROPOSED-PILOT]`.
- §202.17 (L17105–17115): the source report proposes first-pass numeric thresholds for "direction macro-F1, source-disjoint degradation, conformal coverage, monotonicity violations and RAG abstention". They are preserved only as `[PROPOSED-PILOT]`, "must be recalibrated after the first baseline run and may not be cited as literature-derived standards". **The numeric values are not in the SSOT and the source report is not in the repo**, so they are unrecoverable here.
- §203.10 (L17373–17387): an MVP of "several thousand process-effect rows and a handful of anchor ingredients" is `[PROPOSED-PILOT]`. **True launch criterion: "enough support to create meaningful pair-holdout and study-disjoint test sets", "not an arbitrary sample count"** (L17381–17387).
- §201.7 tier weights `[PROPOSED-PILOT]` (L16672).

### 4.6 MVP definition, a de facto L14 exit gate (§204.8, L17558–17572)
All of: 1 versioned process-event/evidence table; 2 ≥2 supported target fidelities (e.g. direction + retention/log-ratio); 3 null + identity-only + process-only + strong tabular baseline; 4 ingredient×process pair-holdout; 5 study/source-disjoint test where possible; 6 concat/FiLM comparison if enough rows exist; 7 calibrated uncertainty/selective prediction; 8 RAG retrieval over ledger with citation/provenance; 9 explicit abstention for out-of-ledger queries. "No dynamic graph is required for the MVP" (L17572).

### 4.7 Stop / defer rules
- Abstention rule (§201.15, L16795–16799): `confidence < τ ⇒ abstain / retrieve evidence / return broader claim`, "a feature, not a failure" (L16801). τ is unspecified.
- §198.8 (L16019–16025): if nearest evidence is too distant or uncertainty too high → abstain/retrieve broader evidence.
- Defer list §204.5 and `[DEFER]` items: hypernetworks L15932, dense trajectory encoders L16135, S9 L16365, contrastive L16488.
- §207.7 (L17919–17926): implementation must "**not build a large L15 dynamics model yet**"; resume the L12 benchmark and, in parallel, start the L14 process-event/evidence spine.

### 4.8 Statistical/calibration reporting (§202.9–202.11)
Classification: ECE, Brier, reliability. Regression: calibrated PIs, empirical interval coverage, interval width (L16987–16997). Conformal/CQR and risk–coverage are `[SOURCE-REPORTED]`. Outputs: point/band, interval/set, evidence-distance/OOD flag, abstain. "Coverage assumptions and shift limitations must be stated" (L17010). OOD: `d_evidence = kNN-distance to curated evidence rows` in standardised structured feature space, "a retrieval-distance heuristic, not a guaranteed probabilistic OOD detector" (L17016–17024). Compute profile per model: params, preprocessing cost, train time, inference time, RAM/VRAM, artifact size. "Small-data process modeling should not become GPU-heavy by default" (L17063–17072).

---

## 5. Data requirements and named sources (licence notes)

### 5.1 Source-reported landscape (§198.7, L15961–15990)
| Resource family | Supports | Limitation (SSOT) | Repo status / licence (manifest; UNVERIFIED unless noted) |
|---|---|---|---|
| USDA nutrient-retention tables | food × method retention factors | aggregated; little/no sample conditions | DS-001 USDA R6 in EVD 7,018 rows (E3). Licence per manifest (public-domain USDA; not re-verified by me) |
| Phenol-Explorer retention | compound-level polyphenol RF | heterogeneous studies; conditions in papers | DS-003 PE 3.6, 3,870 rows / 125 papers; "polite crawl (D-005)"; licence UNKNOWN in manifest |
| FoodData Central raw/cooked | composition comparisons | often not matched samples | DS-004/005; CC0 per FDC statement (manifest says unverified this run); 867 FDC raw/cooked pairs = E6 candidates, not in EVD (ssot15 map SX-06-03) |
| FoodAtlas | food–chemical evidence graph | composition, not dynamics | DS-015; manifest: "Data CC BY-NC 4.0 since 2026-10-09"; manual download |
| FooDB / FlavorDB / FlavorGraph | presence links | weak process evidence | DS-017 FooDB CC BY-NC 4.0 per third-party mirror (UNVERIFIED); DS-024 FlavorDB no licence, use via Prof. Bagler (D-015); DS-025 FlavorGraph Apache-2.0 code, data derived from Recipe1M (CC BY-NC-SA) + FlavorDB |
| raw-vs-cooked GC-MS/GC-IMS papers | volatile changes | small n, platform/matrix-specific | no dedicated manifest entry; generic DS-040 OA journals (per-article CC BY). **0 volatile rows in EVD** (SX-06-03 MISSING) |
| focused kinetic literature | time-resolved trajectories | narrow systems | DS-045 OA kinetic literature (per-article); DS-044 ComBase (microbial, licence UNVERIFIED); DS-047 BRENDA (CC BY 4.0 "quoted by search"); DS-049 EFSA acrylamide occurrence (licence not found) |
| recipe-flow/state corpora | procedural structure | no chemistry | DS-058 RecipeNLG (non-commercial research agreement) / Recipe1M+ (CC BY-NC-SA 4.0 per manifest) / English Recipe Flow Graph (licence UNVERIFIED); project corpus 612,782 recipes (S133) |

Canonical conclusion (L15978–15990): "no single public dataset currently supplies (process + continuous conditions + before/after molecular state) at large scale", described as "the dominant Level-14 design constraint". §205.1 (L17578–17594) restates this as the single largest gap.

### 5.2 Acquisition priority (§203.3, L17191–17247)
- **A, retention tables**: 1 nutrient RFs, 2 polyphenol RFs. Why first: structured, immediately useful for T2–T4, low compute, "enough to establish the entire evaluation/data pipeline". Limitation: aggregated, conditions incomplete. Repo: done in E3 form (USDA R6, Bognár, PE). Candidates not yet in EVD: DS-006 USDA Cooking Yields R2, DS-009 FSANZ AUSNUT retention factors, DS-016 USDA Flavonoid DB (composition, not retention).
- **B, curated raw-vs-cooked volatile literature**: "Focus on a small anchor set rather than pretending broad coverage" (L17214). Candidate anchors: onion, garlic, potato, tomato, chicken, beef, coffee/cocoa (roasting/Maillard) (L17218–17226). "The exact anchor set should be chosen after coverage audit" (L17228).
- **C, focused kinetic literature**: thermal-dose features, simulators, one focused hybrid experiment (L17232–17236).
- **D, recipe/state corpora**: procedure graphs, action/state extraction, intermediates, order tests. "Do not use them as molecular outcome truth" (L17247).

### 5.3 Extraction workflow (§203.6, L17305–17315)
paper → structured extraction → unit normalisation → source-span/table pointer → automatic checks → human verification → evidence tier. "No unverified extraction may enter the gold test set." §205.5 (L17625–17627): "Human verification is part of the data pipeline, not an optional cleanup step."

### 5.4 Cross-platform (§203.7) and platform as a 4-role variable (§205.4, L17616–17621)
Platform is a covariate, a split key, a provenance field and a potential domain-shift variable.

### 5.5 Human-verification reality (repo)
0 HUMAN_VERIFIED EVD rows; 3,870 AI_PRECHECKED; 14,108 UNVERIFIED (MP-1 §6). The verification queue has 634 rows, 0/40 verified (SX-06-08). G14-3 cannot pass until held-out labels are human-verified. MP-1 C2 proposes E3 "Bootstrap benchmark labelled unverified; nothing called Gold until verified".

---

## 6. Dependencies on other levels/steps

- **Upstream SSOT**: §§104–113 (factorised state, explicit vs latent; MP-1 grounding), §106 profiles, §107 process/ΔS, §117 missing modalities, §141 frozen transition output contract, §143–145 cooking-chemistry contract and curation cells (§144.3 L8994–9002), §64 process-effect schema (cited by MP4 L341), §25 process encoder (MP4 L341). L12 molecule/ingredient representations feed z_i and z_m (§207.2: "The two tracks meet when stable Level-12/13 representations are available as additional Level-14 inputs", L17838). Track B "starts now" and must **not wait for** a perfect molecule encoder, full recipe-graph automation, a universal chemistry dataset or professor APIs (§207.3, L17842–17851).
- **Downstream**: L15 (§§208–216). §205.11 (L17714–17738): L14 makes a credible process-conditioned state representation and defines trustworthy targets/evidence. L15 adds transition learning, multi-step rollout, error accumulation, kinetic/ODE, reaction networks, mechanistic residuals and counterfactual simulation. "The lack of data discovered in Level 14 becomes a central Level-15 constraint rather than disappearing" (L17738). §218.4 (L23214–23226): the highest-priority L15 artifact is a versioned transition/evidence table connected "to the existing Level-14 process-event ledger". §216.7 (L22890–22910) dependency: L14 process/evidence table → L15 transition schema → D0–D4 endpoint baselines → cold-pair + study/OOD → calibration/abstention → RAG transition fallback.
- **L15 sparsity (§§219–227)**: MNAR/propensity (DEL-2 already reports propensity AUC 0.81–0.91) and synthetic-prior tiers (E7). L14's E1–E6 has no E7, so the synthetic tier is defined only in L15/MP4.
- **L16 CulinaryState-RAG / FlavorTwin V2**: §198.8 and §203.8 define the evidence-ledger key and response policy. FlavorTwin V2 "process-conditioned flavour similarity" anchors include §198 and §204 (SSOT L8536). The molecule-weighted state stretch goal (L17465–17473) is "High relevance to FlavorTwin".
- **L13E**: SSOT L43285/L43328 separate historical time `t` from within-recipe process time `tau` (Level 14/15 "separate clock"). L14's θ(τ) uses τ (L16128), so it must never be mixed with L13E historical t.
- **MP4 blocks**: B05 process vocabulary (L335–345; G16-VOCAB ≥95% of process mentions mapped or explicit UNMAPPED); B06 state-change KB (L347–368; gate G14-1…12 + G15 data gates; target ≥100k evidence-bearing rows across tiers); B11 graph; B12 L14 (L464–471); B13 L15 + sparsity (L473+).

---

## 7. Risks / failure modes

From §205 and §207.6 (L17896–17907, the "long-pole risks"):
1. **Insufficient matched process-effect data** (§207.6 #1; §205.1). Consequence: no universal dynamics model. Fallback: retrieval-first, abstention.
2. **Retention-definition/unit heterogeneity** (§207.6 #2; §201.5 L16632). Repo: USDA %TR/%AR mixing (C4), PE yield coupling (C5).
3. **No continuous conditions** (§207.6 #3). Repo: pH/aw/moisture 0%, T 33%, t 17%. So G14-7 (condition vs label) may be untestable on E3 data. **This is a real gate-feasibility risk.**
4. **Study/platform domain shift** (§207.6 #4; §205.4; §203.7 L17328): "Do not interpret platform-induced profile differences as food-state differences."
5. **Human-verification burden** (§207.6 #5; §205.5). Repo: 0 verified rows, so G14-3 is blocked.
6. **Sparse molecular concentrations** (§207.6 #6). S4/S5 and the formation head are blocked.
7. **No controlled order/trajectory data** (§207.6 #7). S6/order-swap is blocked.
8. **Matrix transfer** (§207.6 #8; §205.2 L17596–17604): a model-system kinetic law may not transfer to a real food matrix. Matrix identity "is not nuisance metadata".
9. Mixture perception (§205.3 L17606–17610): volatile prediction is useful without claiming perceived flavour.
10. **Procedural split/recombine reasoning** (§205.6 L17629–17643): recipe-state reconstruction must explicitly evaluate split, merge, discard, reserve, recombine, pronoun/coreference and implicit intermediates.
11. **Shortcut learning**: study-ID/platform/tool leakage (§199.10, §202.4). Endpoint-phrase leakage (§199.8). Random-split memorisation (§202.1).
12. Correlated-feature permutation importance misleading (§202.5 L16934).
13. Representation that only encodes process identity (§202.13 L17051).
14. Synthetic/real pooling (§201.13).
15. Qualitative heat mappings mistaken for measurements (§199.7 L16205; §205.9 #4).
16. Contrastive positive contamination (§200.8 L16490–16495).
17. Generic physics constraints applied to formed compounds / open systems (§201.12 L16761).
18. Reference caveats (§205.9 L17670–17681): bibliographic details to be checked before submission; cross-domain generalisation drops are motivation only; gate thresholds are engineering starting points; qualitative heat mappings are hypotheses; tier weights are tunable; "no cited model architecture is accepted as default without this project's own benchmark".
19. Speculative components kept `[HYPOTHESIS/OPEN]` (§205.7 L17645–17654): learned non-commutative operators; general process-conditioned molecule weights; universal end-to-end T(S_t, P_t, θ_t); chemistry contrastive process embeddings; general dynamic reaction graphs; cross-matrix causal counterfactuals.
20. Established/lower-risk components (§205.8 L17656–17668): state dependence; explicit process/condition representation; retention-factor supervision; qualitative/ordinal tracking; process-event/procedural graphs; physics-derived exposure features where definitions are clear; cold/grouped evaluation; uncertainty/abstention; evidence provenance.
21. **Empirical risk already realised (repo)**: on PE (the only multi-study source) learned baselines do not beat persistence/global mean under pair/process/study-disjoint splits (DEL-2 tables above). L14's conditioning hypothesis currently has **no positive evidence**. Under the promotion rules this is a valid negative result, but it means further architecture work before new data would violate §204.1 ("data quality + evaluation design > architecture novelty", L17399–17403).

---

## 8. Mapping to the 36-step spine (brief §9)
(Reconstruction: the step cards are missing. Each entry says what L14 requires of that step.)

- **01 Freeze project authority**: register PART IX epistemic labels (§197.3) so `[PROPOSED-PILOT]` values (±10% dead band, §202.17 thresholds, tier weights, row-count MVP) are never cited as frozen. Record that the L14 source report is absent (§206.1 #3), so pilot values are unavailable.
- **02 Audit implementation state**: G14-1…12 status table (already in `registry/ssot15_state_experiment_map.csv` L79–90); DEL-2 negative cold-split results recorded as retained negative evidence.
- **03 Freeze state semantics**: inputs §197.5 distinctions 1–10, §198.1 state key (ingredient_id, state_id, process_event_chain, condition_bucket + raw fields), §198.2 three compound channels, §201.2 factorised ΔS heads, §201.3 target ladder T0–T7, §201.14 hierarchical granularity. Output: a frozen state contract (MP-1 is the DRAFT, `reports/h_state/state_representation_contract_v1.md`). Gate: every state variable has a target-type eligibility (which T-rungs) and a "target precision ≤ evidence precision" rule (§197.4). Missing: `ingredient_state_out` and `ordinal_band` semantics. Disambiguate the T0–T7 label vs L12 T0–T9.
- **04 Freeze evidence/provenance/similarity contracts**: tiers §201.7. Reconcile E1–E6 (SSOT) vs E1–E7 (MP4/EVD); D-018 already separates tier/verification/design/provenance_class. Literature-extraction fields §201.8; censoring semantics §201.9; platform as a 4-role variable §205.4; synthetic flag §201.13; RAG distinction retrieved/estimated/inferred/unknown §198.8. Similarity: the L14 "process-conditioned change" similarity must stay separate from structural (registry has 21 types; consistent).
- **05 Normalize EVD**: implement the §203.2 export view in full. Add `ordinal_band`, `ingredient_state_out`, row-level `platform`, `split_id`, `dataset_version`, explicit `target_type`, `explicit_or_inferred` (= provenance_class), external IDs (InChIKey/ChEBI/PubChem, ingredient ontology, process ontology mapping). Separate `log_retention_factor` vs `log_fold_change` (D-018 done). Retention definition flag (TR/AR/yield-adjusted) is mandatory (§201.5). Gate: G14-1. ES-1.1 PASS covers most of it; the gaps listed above remain.
- **06 Freeze source acquisition manifest**: priority A→D (§203.3) and resource-fidelity record per source (§203.4: measured what/how, matched?, T/t?, platform, value type, citation, licence, missing). The manifest lacks an explicit platform column and a "matched before/after within study" flag distinct from `before_after_available` (UNVERIFIED). Volatile anchors: no dedicated sources listed. The anchor set must be chosen "after coverage audit" (L17228).
- **07 Condition & measurement normalization**: §199.3 raw-first storage + transforms (log(1+t), 1/T_K, bounds); §199.5 tuple (value, unit, type, mask, provenance); §199.7 POINT/INTERVAL/QUALITATIVE/UNKNOWN with a flag on any qualitative→numeric mapping; §199.8 endpoint phrases as outcome/stopping criterion, **never as condition inputs**; units for T in K for 1/T and Arrhenius features; MEAS platform vocabulary incl. SPME-GC-MS (§198.2 L15797–15805). The Step-07 human audit is NOT_COUNTED_PROVENANCE_INVALID (ctx), so condition normalisation is not human-validated. G14-1 "missingness" depends on this.
- **08 Scientific source lineage** (not to be started now): study_id/source_id/campaign grouping is mandatory for Split 6 (§202.2 L16886–16890: "Keep all rows from a paper/study/experimental campaign together … mandatory for literature-mined quantitative process data"). Study-level bootstrap (§202.12) needs cluster ids. Platform per study (STUDY.analytical_platform_ids). Cultivar, geography, storage, lab protocol are needed as confounders (§201.16 L16809–16815). USDA "imputed from similar foods" donor links must keep donors in the same fold (TB-V0 L20). Gate support: G14-6, G14-11.
- **09 Evidence extraction & verification machinery**: §203.6 workflow; §201.8 required fields; §205.5 "human verification is part of the pipeline". Output: E5→E4 promotion only via human span/table check (MP-1 §6). Metric: SX-06-08 extraction accuracy vs human. Gate: no unverified extraction enters the test set (L17315), which serves G14-3.
- **10 20-row mechanism pilot**: should exercise the full §203.2 schema end to end, including platform, censor/LOD, T/t types, endpoint vs condition, direction with dead band, and verification fields. It is a schema-stress pilot, not a modelling run.
- **11 Wave-1 verified mechanism evidence**: produce E1/E2/E4 rows (human-verified) to satisfy G14-3 and G14-10 (stratification needs ≥2 tiers with counts). Choose rows to create **pair-holdout and study-disjoint test support** (the §203.10 launch criterion).
- **12 Structured database evidence**: Priority A (§203.3): more retention tables (USDA Cooking Yields, AUSNUT retention, etc.), with retention definition and basis harmonisation (§201.5). Output T2–T4 targets.
- **13 Large literature discovery corpus**: Priority B volatile anchors (onion, garlic, potato, tomato, chicken, beef, coffee/cocoa, to be reconciled with §144.3 cells) and Priority C kinetic literature. Capture the platform for every volatile study. Formation-marker families limited to the closed list (L15786–15791).
- **14 Coverage-driven evidence growth**: drive acquisition by dataset-card metrics (§203.9): pair-frequency distribution, per-condition coverage, study counts per pair, platform counts. Target: "enough support to create meaningful pair-holdout and study-disjoint test sets" (L17383). Priority cells: pairs with ≥2 independent studies (my operationalisation, not SSOT).
- **15 Freeze DATA-EVIDENCE v1**: gates G14-1, G14-2, G14-3 (hard data gates). Dataset card before model selection (L17357). Duplicate/conflict audit. SPLIT ledger with frozen assignments (split_id, assignment_sha256, leakage report) for the six split families (§202.2). Test labels human-verified.
- **16 Instruction semantic schema**: §199.6 state-action relations (REQUIRED/TYPICAL/OPTIONAL/INCOMPATIBLE/UNKNOWN); §199.8 endpoint fields; §199.5 medium/tool/geometry/agitation fields; §205.6 split/merge/discard/reserve/recombine/coreference/implicit intermediates; §200.6 many-to-one intermediates with quantity weighting.
- **17 Instruction-level extraction**: endpoint cues extracted as outcome/stopping, not condition; qualitative heat kept QUALITATIVE (repo conforms); evaluation per §205.6 operations.
- **18 Event-sourcing engine**: state key (§198.1) with event-chain hash + inspectable raw fields; H_t as an explicit ordered list; τ process clock separate from historical t (L43328).
- **19 Gold state-trajectory pilot**: T1 qualitative state labels; order-swap candidates (§198.4) only where literature supports them; "procedure extraction quality ≠ chemistry-effect accuracy" (L17292–17296), so Gold trajectories never count as chemistry evidence.
- **20 Scale procedural semantic corpus**: Priority D (§203.3) for procedure graphs and RAG S0→a1→S1 chains (§203.5); recipe self-supervision only as an auxiliary (§201.17); soft priors only (§199.6 L16183).
- **21 Effect/mechanism ontology**: formation-marker families (§198.2) and the factorised ΔS heads (§201.2). Mechanism families on PROC are AI-drafted (C7) and must be verified before use.
- **22 Event→effect signatures**: direction/ordinal targets with dead band (§201.6); "do not train chemistry targets from simple state-action co-occurrence" (L16183).
- **23 Mechanism applicability engine**: needs θ coverage (pH, aw, moisture, O₂). L14 shows these are 0% in EVD, so applicability will often return UNKNOWN → retrieve/abstain (§198.8). Matrix identity is a core variable (§205.2).
- **24 Formula/model registry**: Arrhenius exposure integrals "at representative activation-energy values" (L15842) and F-value-like features need Ea/z-value sources per system (Priority C). Physics constraints apply only for defined subsets (§201.12).
- **25 Parameter-compatibility retrieval**: the condition bucket + raw vector is the retrieval key (§203.8); evidence-distance kNN (§202.11).
- **26–28 Simulator / validation / E7 prior**: §201.13 (focused system only; fidelity flag; never pooled); §200.4 focused acrylamide/browning example; §199.4 neural ODE/CDE only on focused kinetic/simulator data. MP-1 §8: E7 `may_enter_gold_evaluation=false`.
- **29 TRANSITION_BOOTSTRAP_V0**: canonical target (§201.1); T2–T4 rungs only on E3 data (§197.4 L15657: method/food-level effect, not kinetic law); D0–D5 baselines; splits incl. pair-holdout + study-disjoint (headline per §202.3, but TB-V0 differs, see §9). Reports per G14-4/5/6/9/11. Already partly executed in DEL-2.
- **30 Strong tabular / sparsity bake-off**: §200.1 ladder; §202.4 mandatory list incl. study-ID-only, platform-only, conditions-only (not yet run); TabPFN "where appropriate" (skipped so far; CPU feasibility is an open question); ≥5 seeds for neural, study-level bootstrap (§202.12); evidence-tier stratification (§202.8, G14-10); missingness robustness (§202.7, G14-8); risk–coverage (G14-9).
- **31 Physics/condition features**: §198.3, §199.3, §204.2C; gate G14-7 "condition contribution tested against label-only"; grouped ablation (§202.5); counterfactual/monotonicity checks where the direction is scientifically justified (§202.6). Feasibility is constrained by T 33% / t 17%.
- **32 Focused kinetics**: Priority C; T6 trajectories; one system.
- **33 Mechanistic vs ML vs hybrid**: §200.4 three-way comparison; S10; §204.4 stretch.
- **34 Short rollout**: L14 hands off to L15 (§205.11). History-aware S6/order-invariant vs GRU only with order labels (§200.5).
- **35 Representation ladder**: S0–S10 (§200.2); molecule-set encoders with perturbation tests (§200.3); z_P = [family; leaf; physics] (§199.2); process-disjoint transfer + hyperbolic only if simple fails; probes (§202.13); NN inspection diagnostic only (§202.14); molecule-weighted z_{i,t} stretch for FlavorTwin (§204.4); concat/FiLM ablations (§204.3); promotion per §205.10.
- **36 Evidence compiler → RAG → FlavorTwin**: §198.8 retrieval key + four-way distinction; §203.8 response policy; §202.10 interval/set + OOD flag + abstain; §202.11 kNN evidence distance; §201.15 τ abstention; §201.11 no palatability claims; §204.6 Phase D demo (citation, "estimated" flag, interval, abstention); G14-12 decision record; MVP items 8–9 (§204.8).

---

## 9. Contradictions, stale items, underspecified parts, open questions

**Contradictions / tensions**
1. **Tier ladder E1–E6 vs E1–E7.** SSOT L14 §201.7 (L16655–16662) defines E6 = "heuristic / qualitative / weak inference" and no E7. MP4 L589–596, the EVD `tier` enum and MP-1 §6 define E6 = "mechanism-family rule/heuristic (MODEL_ESTIMATED)" and E7 = SIMULATED. E6 semantics differ: "qualitative" evidence (a literature statement "vitamin C decreases") is SSOT E6 but could be E1/E2 design with qualitative values. D-018 separates design_strength from tier, which partly resolves this, but an SSOT change request is warranted to make E7 explicit, or to state that L14's E-tiers are design-of-evidence only.
2. **E1–E4 "test labels" vs human verification.** §201.7 L16664 says test labels "preferentially" come from E1–E4 *and* are human-verified. §201.8 L16690 says *all* held-out test values should be human-verified. §203.6 L17315 says no unverified extraction in the gold test set. E3 database aggregates are not "extractions", so is an unverified E3 row allowed in test? MP-1 C2 proposes "Bootstrap benchmark labelled unverified". This needs a ruling; G14-3 as worded ("Human-verified held-out test labels") excludes it.
3. **Headline split.** SSOT §202.3 (L16898–16900) = pair-holdout + source/study-disjoint, and calls pair-holdout "the canonical compositional-generalization test" (L16878). TB-V0 (`reports/h_state/transition_bootstrap_v0_contract.md` L20, L27–28) sets headline = min(S-2..S-5), counts support only on S-3/S-4 (matrix-/process-disjoint) and treats gains on S-2 (pair holdout) as "non-cold". The repo contract is stricter than the SSOT and inconsistent with it. Pick one rule and record it before Step 29/30 results are re-read (no post-hoc gate change).
4. **Split taxonomy.** SSOT has 6 families + optional sequence-OOD (§202.2). TB-V0 has 7 (adds food-group-disjoint S-5 and source-disjoint S-7; calls ingredient-disjoint "matrix-disjoint"). Condition-OOD (SSOT Split 5) is **absent** from TB-V0 and DEL-2. Platform-disjoint (§203.7) is optional and absent.
5. **Anchor ingredients.** §203.3 Priority B (onion, garlic, potato, tomato, chicken, beef, coffee/cocoa; L17218–17226) vs §144.3 first curation cells (rice, potato, broccoli, garlic, beef, wheat dough, cabbage; L8996–8998). MP4 SX-06-03 uses §144.3 (MP4 L360). The overlap is only potato, garlic and beef. §203.3 says to choose after a coverage audit, so both lists are candidates. ES-1.2 `reports/h_state/es_1_2_priority_cell_source_coverage.csv` may already encode a choice (UNVERIFIED by me).
6. **Censoring practice.** DEL-2 trained "censored rows at lower bound 0.975 (assumption)" (all three DEL-2 reports). §201.9 L16705 forbids default substitution (zero or LOD/2) and prefers censored likelihoods. Bound substitution is a default substitution in training. It is not prohibited verbatim but conflicts in spirit and should be flagged; evaluation is censor-aware, which is fine.
7. **Seeds.** §202.12 requires ≥5 seeds for neural models. DEL-2 is single-seed (seed 7) but non-neural, so this is acceptable for trees. G14-11 requires multiple seeds/clustered uncertainty "for learned models", which includes GBT. PARTIAL.
8. **Shortcut list incomplete in repo.** §199.10 and §202.4 require study-ID-only, platform-only, conditions-only and tool-only. DEL-2 has none of these. G14-4 is marked PARTIAL, correctly.
9. **Kinetic focus system.** §200.4 suggests acrylamide/browning. MP4 SX-06-04 lists acrylamide/potato, Maillard glucose/glycine, vitamin C, anthocyanin, chlorophyll. The brief §22 asks for a comparison (ascorbic acid, chlorophyll, enzyme inactivation, gelatinisation, Maillard, acrylamide). The SSOT gives no selection criterion beyond "sufficient literature" (L16411).
10. **Notation clashes.** T0–T7 targets (L14) vs L12 thread experiments T0–T9; S0–S10 encoders vs TB-V0 S-1..S-7 splits; E0–E8 ingredient-encoder ladder in L12 (SSOT L8490–8501) vs evidence tiers E1–E7. These are high-risk for agent confusion and need a namespace prefix (e.g. L14-T*, L14-S*, EVD-E*).
11. **H_t in E(·).** L15699–15707 omits H_t while L15533 includes it. Cosmetic.

**Stale / unavailable**
12. The "supplied 656-line Level-14 report" (§206.1 #3) is not in the repo. So the §202.17 pilot thresholds, the §201.7 tier weights, the §203.10 MVP row count, the transformation/process ontologies cited at L16069, and the reaction-NN/UDE citations at L16401 are **unrecoverable**. §205.9 says citations were not independently re-verified.
13. §207 is a "historical return point — superseded by §218" (index L1310). The §207.2 Track B ordering is superseded in form by §216.7/§218, but the content is compatible.

**Underspecified**
14. **G14 gates are completion gates with no pass thresholds.** "Completed/reported" items cannot fail on performance. The scientific pass/fail lives only in §205.10's qualitative inequality and §202.4's "beat under cold/grouped splits". A pre-registered operational rule is needed (e.g. paired grouped-bootstrap lower bound > 0 vs best shortcut on the headline split, as TB-V0 L27 does), frozen before the test run.
15. **"Recalibrate pilot thresholds after the first baseline run"** (L17115) vs the project law "no post-hoc gate weakening". A procedure is needed: recalibrate only on train/validation folds, freeze before any locked-test evaluation, and log the change in DECISIONS.
16. τ for abstention (§201.15) and the d_evidence cut-off (§202.11) have no calibration protocol (which validation set, which target risk level).
17. The **condition bucket** definition (§198.1, §198.8, §203.8) is never specified: bin edges, per process family, how intervals/qualitative values are bucketed.
18. **ordinal_band** definitions (low/medium/high retention) are unspecified: cut-points per target? per nutrient?
19. Dead-band δ: relative (±10% of before) or absolute on RF (|RF−1| ≤ 0.10)? L16638–16647 writes Δ with ±10%, which is ambiguous for log-ratio vs fraction.
20. Representative activation energies for "generic Arrhenius exposure integrals" (L15842): which Ea values, and from what source? F-value reference temperature and z-value are unspecified.
21. "Study/experimental campaign" grouping for USDA/Bognár (single source family) makes G14-6 impossible on Priority-A data. The SSOT's "where study IDs exist" escape clause (L17083) means G14-6 can pass vacuously. A minimum number of independent study groups should be required.
22. Minimum support for a "meaningful" pair-holdout/study-disjoint test set (L17383) is undefined: how many test pairs, how many independent studies per pair?
23. The process-ontology choice (FoodOn vs LanguaL vs a custom one) and mapping storage format are not fixed (L16069–16075).
24. How to handle yield-adjusted vs true vs apparent retention in one model (basis as covariate? separate heads?). §201.5 only forbids un-harmonised merging.
25. Platform vocabulary lacks SPME-GC-MS in MEAS.family (UNVERIFIED whether it is folded in).

**Open questions needing external research** (not done by this reader)
- R1: TabPFN (v2, Hollmann et al., *Nature* 2025, UNVERIFIED citation details): CPU feasibility at ≤10k rows, licence of the weights, and whether it handles censored targets. DEL-2 skipped it as "GPU" without testing CPU.
- R2: Established food-process ontologies for process hierarchy (FoodOn processes, LanguaL facet F "extent of heat treatment"/H "treatment applied", FoodEx2 process facets): which is stable and licensable.
- R3: Censored-regression options for retention with GT caps: Tobit or censored GBT (e.g. XGBoost survival:aft), and conformal under censoring.
- R4: Conformal prediction under group/covariate shift (weighted/Mondrian/group-conditional conformal) for study-disjoint coverage. DEL-2 shows coverage dropping below nominal under shift.
- R5: Volatile raw-vs-cooked literature availability per anchor (onion, garlic, potato, tomato, chicken, beef, coffee/cocoa vs §144.3 cells): count of matched-design studies with platform reported.
- R6: Kinetic-parameter availability (Ea, k_ref, z) per candidate focused system, to choose Step 32's system and supply §198.3 Arrhenius features.
- R7: USDA R6 %TR vs %AR identifiability; whether the R6 documentation allows row-level recovery.
- R8: Platform harmonisation literature (GC-MS vs GC-IMS vs SPME) for compound-vocabulary intersection.
- R9: Minimum sample-size guidance for grouped CV / study-level bootstrap with few clusters (PE has 125 papers).
- R10: Process-time-temperature history recovery from recipes: is there any evidence that recipe text supports F-value-like features? Probably not, which supports §197.4.

---

## 10. LOOK-AHEAD: fields earlier steps must capture

**Steps 03/04 (semantics & contracts)**: freeze `target_type` (T0–T7 rung) per row; `ordinal_band` definition; dead-band δ definition (relative vs absolute) as `[PROPOSED-PILOT]`; a tier ladder reconciled to E1–E7 with SSOT-text mapping; `design_strength`, `verification_status` and `provenance_class` separate (D-018); synthetic `fidelity_flag`; the RAG output class {RETRIEVED, MODEL_ESTIMATE, INFERRED/EXTRAPOLATED, UNKNOWN}; `ingredient_state_in`/`ingredient_state_out` semantics; τ process clock vs historical t.

**Step 05 (EVD normalise)**: row-level `platform` (from MEAS/STUDY, explicit UNKNOWN); `retention_definition` {TRUE, APPARENT, YIELD_ADJUSTED, UNKNOWN} + basis; `log_retention_factor` vs `log_fold_change` (done); `ordinal_band`; `direction_label` with δ version; `target_type`; `split_id` placeholder; `dataset_version`; external IDs (InChIKey/ChEBI/PubChem; ingredient ontology; process ontology mapping + mapping provenance); `censor_flag` + LOD/LOQ (or explicit "not reported"); `imputed_from_similar_food` donor link (USDA) for fold grouping.

**Step 06 (manifest)**: per source, the §203.4 fidelity fields: matched within-study before/after (Y/N), T/t availability, analytical platform(s), value type, retention definition, licence (verified/unverified), study-lineage availability; priority class A/B/C/D.

**Step 07 (conditions/measurement)**: every axis as (value, unit, type ∈ POINT/INTERVAL/QUALITATIVE/UNKNOWN [+CENSORED/NA], mask, provenance), with **per-axis provenance** (currently record-level only); T kept in °C plus a derivable K; T-type semantics (oven set-point vs medium vs surface vs core; MEAS location registry exists, `measurement_location_registry_v1.csv`); time semantics (total vs holding vs time above threshold); a time–temperature trajectory array when reported (COND.trajectory exists); medium, tool, geometry/thickness/surface-area proxy, agitation, oxygen exposure, pressure; heat_transfer_mode; **qualitative→numeric mapping flag**; endpoint/stopping-criterion cues stored separately and marked as potential outcome leakage; platform vocabulary incl. SPME-GC-MS, GC-O, GC-IMS.

**Step 08 (lineage)**: study_id, publication_id, experimental campaign/batch id, lab/group, `independence_group`, cultivar/variety, geography/origin, storage/ripeness, sample prep, analytical platform per study, replicates n, whether rows are within-study matched (the §201.16 causality boundary), donor links for imputed values, conflict_cluster. These feed Split 6, study-level bootstrap and G14-6/G14-11.

**Step 09 (extraction/verification)**: DOI/citation, exact span/table/figure/page pointer, extraction method/model/version, automatic-check results, human verifier id/time, units as reported + normalised, conditions as reported, target definition as reported (§201.8). E5→E4 promotion log.

**Steps 10–15 (acquisition)**: aim acquisition at **pair-holdout and study-disjoint support** (≥2 independent studies per ingredient×process pair for test cells); include within-study matched before/after; capture platform; capture continuous T/t (and pH/aw/moisture where any exist) because G14-7 needs condition variance; capture ND/LOD; capture order-swap evidence (pre-treatment→fry vs not) for §198.4; capture formation markers only from the closed list; record matrix identity in detail (§205.2: not nuisance). Dataset card (§203.9) metrics are generated at Step 15 before any model selection. SPLIT ledger frozen with assignment hash and leakage report.

**Steps 16–20 (procedure/state)**: state-action relation labels (REQUIRED/TYPICAL/OPTIONAL/INCOMPATIBLE/UNKNOWN); endpoint cue fields (EVT.endpoint exists); split/merge/discard/reserve/recombine/coreference/implicit-intermediate operations (§205.6) with Gold evaluation; quantity/mass per intermediate for parent weighting (§200.6); event order with confidence for order-sensitive tests; medium/tool/geometry per event; raw condition spans with POINT/INTERVAL/QUALITATIVE/UNKNOWN; an explicit flag that these rows are RECIPE_TEXT plane, never chemistry evidence (§203.5).

---
Word count is approximately 7,000.
