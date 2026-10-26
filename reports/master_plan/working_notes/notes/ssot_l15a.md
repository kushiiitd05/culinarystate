# READER ssot_l15a — SSOT Level 15 §§208–212 (L17934–20584)

Reader: ssot_l15a · Date 2026-10-22 · Mode: read-only plan research.
Source: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (cited as "SSOT Lnnnnn"). I read every body line in L17930–20587. To pin down terms that §§208–212 use but do not define, I also briefly read SSOT §215.2 data regimes (L21949–21997), §215.38–215.39 G15 gates (L22376–22427) and §216.1–216.11 data contracts/dependency graph (L22733–22987). Those sections belong to another reader's assignment. I cite them only where my sections depend on them.
Repo cross-checks are read-only: `reports/h_state/transition_bootstrap_v0_contract.md`, `reports/h_state/ssot15_state_program_inventory.md`, `reports/del2/*_results.md`, `src/culinarystate/transition/baselines.py`, `ledgers/data/{EVD,COND,EXP,UNIT}.jsonl` (stdlib key profiling only), `registry/evd_contract_v1.csv`, `registry/condition_variable_registry_v1.csv`, `registry/retention_type_registry_v1.csv`, `reports/step07/step07_report.md`, `reports/h_state/es_1_2_source_census.md`, `docs/simulator_data_contract.md`, `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (cited "MPv4 Lnnn").
The 36-step plan with step cards is MISSING (ctx.md). I have only the step titles (brief §9). Every step mapping in §8 is my reconstruction from SSOT, MPv4 and repo artifacts. None of it is quoted card text.

**Headline finding:** §§208–212 hold **no gate IDs and almost no numeric thresholds**. They are a conceptual specification: laws, ladders, equations, fitting protocol, rollout semantics. The binding Level-15 gates (G15-1…12, G15-R/H/I, G15-RXN/HYB/INV) live in §215.38–215.39 (SSOT L22376–22427) and are declared frozen at SSOT L23077. The only numbers in my range are labelled `[SOURCE-REPORTED / PILOT]`, i.e. explicitly not frozen (SSOT L19162, L19841). Trust-horizon thresholds are deliberately left task-specific (SSOT L20565).

---

## 1. Definitions, entities and data contracts

### 1.1 Core objects (§208)
- **Level-15 transition operator** (SSOT L17947–17975): `T_φ: (S_t, P_t, θ_t, H_t) → S_{t+1}`, or the delta form `→ ΔS_t` with `S_{t+1} = S_t + ΔS_t` "when the state representation supports additive deltas" (L17975).
  - S_t = state. P_t = process. θ_t = process conditions. H_t = history.
  - Implication: each state variable needs a declared **delta-compatibility type**: additive, ratio/retention, categorical, or non-additive. That flag does not yet exist anywhere (see §10).
- **Representation ≠ transition** (L17989–18013): Level-14 `z_{i,t} = E(S_t,P_t,θ_t,H_t)` represents the current state, while Level-15 `Ŝ_{t+1} = T_φ(...)` predicts a future one; boxed `E ≠ T` (L18010). "A useful embedding does not automatically imply a trustworthy dynamics model" (L18013). This matches project law "static representation ≠ transition" (brief §3).
- **Status block** (L17936–17945):
  - Conceptual spec: COMPLETE.
  - Broad endpoint transition modelling: "DATA-CONSTRAINED but feasible with curated before/after and retention data" (L17940).
  - Focused kinetics: "feasible where time/temperature series exist" (L17941).
  - Multi-step quantitative chemistry rollout: "LIMITED / BLOCKED by missing measured intermediates" (L17942).
  - Reaction-network learning: "focused stretch only" (L17943).
  - Inverse design: gated by forward credibility (L17944).
  - Next level: L16A CulinaryState-RAG (L17945).

### 1.2 Permanent Level-15 rules (L18015–18031), quoted by number
1 Data rung limits model rung · 2 Endpoint data do not identify continuous-time dynamics · 3 One-step prediction does not establish rollout stability · 4 Good curve fit does not establish a mechanism · 5 Parameter estimate ≠ parameter knowledge without uncertainty/identifiability · 6 Model counterfactual ≠ causal counterfactual · 7 Learned interaction ≠ reaction pathway · 8 Reaction graph = species/reaction structure, not all-pairs molecule similarity · 9 Inverse-design credibility ≤ forward-model credibility · 10 Optimisation precision ≤ model/evidence precision · 11 OOD/model uncertainty must constrain optimisation · 12 Unknown pathways/states remain UNKNOWN · 13 Synthetic/simulator data remain a separate fidelity source · 14 Procedure/state graphs can supervise structural transitions without becoming chemistry truth · 15 "The project may stop at retrieval/tabular/kinetic models if added complexity is not earned" (L18031).

### 1.3 Data-to-claim ladder (§208.4, L18033–18056)
Ten evidence → claim rows:

| Evidence | Defensible claim |
|---|---|
| qualitative outcome | direction/category |
| matched before/after | endpoint ΔS, retention, fold-change |
| before/after + T,t | condition-aware endpoint |
| multiple times at one condition | rate k, simple kinetic family |
| times × temperatures | Arrhenius |
| multiple simultaneously measured species | reaction-network fitting |
| dense multi-species trajectories | learned dynamics / rate residuals |
| measured intermediates across steps | quantitative rollout evaluation |
| controlled alternative conditions | stronger counterfactual |
| real validation of optimised candidate | inverse-design evidence |

Boxed law (L18050–18055): **model ambition ≤ highest evidence rung actually present.**

### 1.4 Transition-fidelity ladder L15-A…F (L18058–18110)
- A: qualitative {↓, ≈, ↑} (L18060–18066)
- B: ordinal, none<low<medium<high (L18068–18074)
- C: scalar quantitative endpoint, e.g. moisture, nutrient retention, browning index, one compound (L18076–18083)
- D: multi-output ΔS vector (L18085–18096)
- E: molecular composition transition c_t→c_{t+1} (L18098–18102)
- F: continuous-time dS/dt = f(S,P,θ) (L18104–18108)
- "Each rung needs stronger evidence" (L18110).

### 1.5 Kinetic data hierarchy K0–K4 (§210.28, L19089–19109)
- K0: one before/after endpoint. Supports retention/direction, "not detailed kinetics".
- K1: multiple times at one T. Supports k and reaction order.
- K2: times × temperatures. Supports Arrhenius.
- K3: multiple state variables/species. Supports multiresponse/network fitting.
- K4: multiple matrices/process histories. Supports transfer/generalisation.

The related data regimes D-A (aggregated process effects), D-B (curated raw vs processed), D-C (focused kinetic studies) and D-D (recipe procedure/state corpora) are defined at SSOT L21949–21997, not in my range. §210.29A (L19139) and §211.50A (L19834) use "D-C" without defining it in §§208–212.

### 1.6 Rollout-fidelity ladder R0–R5 (§212.44, L20400–20424)
- R0 procedural graph rollout: "Most feasible"
- R1 qualitative state rollout: "Feasible with state labels"
- R2 scalar physical/nutrient: "Selected variables"
- R3 multi-output quantitative: "Limited"
- R4 molecular trajectory: "Focused systems"
- R5 full reaction-network: "Stretch only"

### 1.7 State factorisation (L18159–18177; L19973–19984; L20383–20398)
- S_t = [physical, chemical, sensory, nutrition, visual, procedure] (L18166–18174). Views "can have different evidence coverage and different transition models" (L18177).
- Rollout views keep procedure/physical/chemical/sensory distinct (L19976–19982). "A recipe can have high-confidence procedure state and low-confidence chemical state simultaneously" (L19984).
- **State coverage vector** q_t = [q_physical, q_chemical, q_sensory, q_nutrition, q_procedure] (L20388–20395). Note: it omits "visual", which §208.8 includes (minor inconsistency, §9).
- Repo: `reports/h_state/state_representation_contract_v1.md` factorises S = {C, P^phys, Y^sens, N, V, A} (+ procedural, safety), according to `ssot15_state_program_inventory.md` L108. The view sets broadly agree but the names differ ("A" vs procedure; "safety" is extra). Steps 03 and 18 need an explicit crosswalk.

### 1.8 Field-level contracts inside §§208–212
**(a) Kinetic evidence schema §210.29 (L19111–19135).** Exactly these fields: `kinetic_family, reaction_order, k_value, k_unit, A, Ea, Ea_unit, temperature_points, time_points, initial_conditions, fit_metric, parameter_CI, matrix, process, target, mechanistic_scope, effective_or_mechanistic, source, verified`.

**(b) Censored observation (§211.8, L19291–19316).** Store `censor_flag, LOD, platform` with the observation. "do not impute zero by default". Use censored likelihood P(c<LOD|φ).

**(c) Minimal kinetic report §211.50 (L19806–19826).** Every fitted model records: `target, food/matrix, process, conditions, equation, parameter estimates, units, confidence/posterior intervals, number of time points, number of temperatures, residual diagnostics, held-out evaluation, identifiability note, effective vs mechanistic interpretation, source/provenance`.

**(d) Transition provenance graph §212.53 (L20567–20581).** Every predicted transition retains: `source, evidence tier, distance to evidence, model version, predicted delta, uncertainty, interpolated / extrapolated flag`.

**(e) Rate-constant units §210.30 (L19164–19184).**
- Zero order: [k] = concentration/time.
- First order: [k] = time⁻¹.
- Second order: [k] = concentration⁻¹·time⁻¹.
- "Never harmonize k values across incompatible orders/units" (L19184).
- Arrhenius needs Kelvin, `T_K = T_°C + 273.15` (L18759–18763).

**(f) Merge/split/reserve semantics (L20262–20304).**
- Merge A+B→C needs many-to-one aggregation, with mass/quantity weighting where quantities exist (L20268–20270).
- Split C→A+B needs one-to-many allocation: "Track how quantities/state are partitioned" (L20280).
- Explicit handling of `reserve, discard, remove, split, recombine` (L20284–20292).
- Graph transition operator `G_{t+1} = 𝒯(G_t, a_t, θ_t)` (L20298–20302).

**(g) Constraint-violation categories (L20224–20234).** Track separately: negative concentration, impossible moisture, invalid allocation, incompatible process/state, balance violations.

**(h) Open-system conservation (L20244–20260).** No naive mass_in = mass_out. Explicit source/sink terms for evaporation, drainage, leaching, discard, ingredient addition.

**(i) Related contracts outside my range** (cited for completeness, other reader):
- §216.1 canonical transition-event table (L22733–22799): includes `T_type, t_type, T_lo/hi, moisture_before/after, water_activity, pH, pressure, oxygen, mixing, censor_flag, LOD, platform, matrix_description, trajectory_id, timepoint, sequence_id, event_index, split_id, dataset_version`.
- §216.2 kinetic-experiment table (L22800–22823): adds `temperature_schedule, observations, candidate_model_family, fitted_parameters, parameter_uncertainty, fit_diagnostics, identifiability_status, evidence_tier`. "Raw timepoint measurements remain available separately" (L22823).
- §216.4 rollout/sequence table (L22847–22863).

### 1.9 Repo reality vs these contracts (verified read-only)
- **No KINETIC, RXN, transition-event, sequence or trajectory ledger exists.**
  - `ledgers/data/` holds ALIAS, ALLERGEN, COND, DATASET, EVD, EXP, IMAP, ING, KGE, MEAS, MOL, PROC, REC, SNAP, SRC, STUDY, SVAR, TOOL, UNIT. No KINETIC/RXN/SIM/SEQ.
  - The inventory confirms: "No physical/chemical simulation or kinetic table exists" (`ssot15_state_program_inventory.md` L82) and "G15: 0 of 15 passed" (L47).
- **EVD.jsonl** has 57,280 lines: ACTIVE E3 DATABASE_AGGREGATE 42,940; ACTIVE E3 UNKNOWN-design 13,888; DEPRECATED 452 (my stdlib count).
  - Nested fields present: `derived.{direction, percent_change, retention_factor{raw,value,status,unit,uncertainty,censor}, yield_factor}`, `matrix.{food_group, form, ingredient_id, initial_state, raw_name}`, `process.{condition_id, medium, modifiers, process_id, raw_name, steps, step_process_ids}`, `target.{basis, raw_name, state_variable_id}`, `censored` (bool), `independence_group`, `study_ids`, `measurement_method_id`.
  - Absent: any `trajectory_id / timepoint / sequence_id / event_index / replicate n / SD-as-separate field`. `uncertainty` appears on only 9,431 retention_factor objects.
  - Reconcile: ctx.md quotes "ES-1.1 EVD export PASS (17,978 EVD rows)" and the bootstrap contract says "today: E3 = 17,978 rows". The ledger holds 56,828 ACTIVE lines. The export is presumably a filtered subset (UNVERIFIED which filter).
- **COND.jsonl:** 4,746 rows.
  - completeness_mask: temperature MEASURED 2,445 / RANGE 276 / UNKNOWN 2,025; duration MEASURED 2,580 / RANGE 28 / UNKNOWN 2,138; moisture UNKNOWN 4,746; pH UNKNOWN 4,746.
  - The Step-07 normalizer report classes temperature validity "UNKNOWN 2,025; AMBIGUOUS 2,417; VALID 213", top reason `temperature:MEASUREMENT_LOCATION_MISSING` (`reports/step07/step07_report.md` L16, L23).
  - Therefore **existing evidence is K0/D-A almost entirely, with zero rows that have a stated pH/moisture and ~213 location-valid temperatures.**
- **Step-07 registries already anticipate parts of §210/§216.**
  - `registry/condition_variable_registry_v1.csv` has CV-004 `time_trajectory`, CV-010 `temp_trajectory` ("T(t) series; location must be stated") and CV-011 `temp_rate`.
  - The value_type registry has TRAJECTORY.
  - The censoring registry has DETECTED/NON_DETECT/BELOW_LOD/BELOW_LOQ/ABOVE_CAP/CENSORED_UNKNOWN/NOT_REPORTED (step07_report L6, L9).
  - Good look-ahead coverage, but no ledger stores trajectories yet.
- **UNIT.jsonl has no kinetic units.** 0 matches for kJ, kcal/mol, min⁻¹, s⁻¹ (grep). §210.30 units are unsupported today.
- `registry/evd_contract_v1.csv` maps `lod / loq` to "NONE as columns (censor.kind/limit inside derived)" and `provenance_class` to "NONE". It has no timepoint/trajectory field.

---

## 2. Models and baseline ladders

### 2.1 Canonical v13 D0–D11 ladder (§209.17, L18543–18613): the binding benchmark ladder
- D0 persistence `Ŝ_{t+1} = S_t` (L18547–18551)
- D1 global mean-delta (L18553–18557)
- D2 process-conditioned mean-delta (L18559–18563)
- D3 hierarchical shrinkage / partial pooling across food class, process family, compound/target class, study/source (L18565–18572)
- D4 nearest-evidence retrieval: "Evidence-backed lookup/kNN over ingredient/process/condition/target context" (L18574–18576)
- D5 strong GBDT, LightGBM/XGBoost (L18578–18580)
- D6 TabPFN / small-data tabular foundation "where sample size/task shape are compatible" (L18582–18584)
- D7 evidence-aware low-rank/factorisation completion: biased MF, Bayesian PMF/Macau-like side-info, factorisation machines, coupled matrix/tensor completion (L18586–18593). "especially important for cold food/process/compound prediction under sparse evidence" (L18595).
- D8 classical kinetics: zero/first/nth-order, Arrhenius, Weibull, formation/degradation, focused compartment (L18597–18599)
- D9 hybrid mechanistic + learned residual, "only where evidence supports it" (L18601–18603)
- D10 neural multi-output / latent-state dynamics. Includes residual MLP, FiLM/gating, history-aware and state-space models as ablations. "**not allowed to skip D0–D7**" (L18605–18607).
- D11 UDE / neural ODE / reaction-network: "Focused time-resolved systems only" (L18609–18611)
- L18613: the old v12 neural sub-ladder survives only as an architectural ablation inside D10/D11. "low-rank/side-information completion is a first-class competitor rather than a preprocessing step."
- Activation rule (outside range, L22022–22026): "dataset supervision ⇒ eligible model family". Not every dataset runs every rung.

### 2.2 Earlier §209 baselines (v12 text, folded into D-ladder)
- Persistence is "mandatory". "Any claimed transition model must beat it on the dimensions it claims to transform" (L18292–18296).
- Mean-delta: global, E[ΔS|P], E[ΔS|i,P], "strong sanity baselines for sparse data" (L18298–18318).
- Nearest-evidence `x* = argmin d(x,q)`, especially relevant because RAG is evidence-first (L18320–18336).
- Tabular features `x = [z_i, P, θ, S_t, source/platform controls, physics features]`. Ridge, LightGBM/XGBoost and TabPFN "define the credibility floor for neural transitions" (L18338–18360).
- Neural residual `Ŝ_{t+1} = S_t + MLP([S_t, z_i, z_P, z_θ])` (L18362–18377). FiLM `h' = γ(P,θ)⊙h + β(P,θ)` is "an ablation, not an assumed winner" (L18379–18391).
- State dependence: T(raw onion, fry) ≠ T(preboiled onion, fry). "A process-only model is a shortcut baseline" (L18393–18405).
- Matrix dependence, conceptually T = T(S_t,P,θ,matrix): sugar/protein precursors, fat, aw, pH, geometry, microstructure (L18407–18424).
- Multi-output heads with **target masks for missing outputs**; "Do not assume all outputs follow identical transition laws" (L18426–18454).
- Coupled outcomes: use shared latent representations rather than hard-coded causal ordering unless a mechanism is evidenced (L18456–18470).
- Probabilistic outputs (μ̂, σ̂), calibrated intervals, p(y|x) (L18472–18488).
- Four separate uncertainty types: aleatoric, epistemic, evidence-distance/OOD, kinetic-parameter (L18490–18499).
- Counterfactual: Ŝ^A − Ŝ^B is a **model** counterfactual, ≠ Y(P_A) − Y(P_B) (L18501–18523).
- Partial observability O_t = g(S_t) + noise. Explicit measured variables preferred first (L18525–18541).

### 2.3 Kinetic model library (§210, L18617–19187)
- General order `−dc/dt = k cⁿ`; n is effective, not stoichiometric (L18645–18658).
- Zero-order `c = c0 − kt` (L18660–18674). First-order `c = c0 e^{−kt}`, `t½ = ln2/k` (L18676–18698). Second-order `1/c = 1/c0 + kt` (L18700–18718). nth-order `c^{1−n} = c0^{1−n} + (n−1)kt`, "Use only if data support extra flexibility" (L18720–18730).
- **Direct nonlinear fitting preferred** over linearisation (L18732–18742).
- Arrhenius `k = A exp(−Ea/RT)` (L18744–18763). Linearised diagnostic ln k vs 1/T (L18765–18785). Relative rate k2/k1 (L18787–18802). Q10, "Useful locally; less mechanistically grounded" (L18804–18814).
- Variable temperature: `c(t) = c0 exp[−∫k(T(τ))dτ]` (L18816–18836). **Thermal dose** `Ω(t) = ∫0^t k(T(τ))dτ` (L18838–18854). Physics features using "multiple representative Ea values" are "features/priors rather than proof of the true reaction mechanism" (L18856).
- Condition features log(1+t) and 1/T_K alongside raw T, t (L18858–18876). This is a stated hypothesis: such features help small-data ML.
- Moisture-gated kinetics `Ω = ∫ g(M(τ)) k(T(τ)) dτ`, "Use only for systems where moisture gating has evidence" (L18878–18896).
- Formation A→B (L18898–18914). Consecutive A→B→C with intermediate peak, relevant to aroma (L18916–18936). Parallel/competing with dA/dt = −(k1+k2)A; conditions change selectivity (L18938–18954).
- Multiresponse `dc/dt = N v(c,T,θ)`, with N the stoichiometric matrix (L18956–18972).
- Lumped/effective parameters: k_fitted ≠ elementary constant (L18974–18985).
- Degradation vs leaching `dc/dt = −k_deg c − k_leach c` with a water compartment. "A single fitted k can hide several mechanisms" (L18987–19000).
- Volatilisation `dB/dt = k_f A − k_v B − k_d B`. "Endpoint concentration cannot necessarily identify which mechanism dominated" (L19002–19020).
- Relaxation/softening `X = X∞ + (X0 − X∞) e^{−kt}` (L19022–19030). Weibull `c/c0 = exp[−(kt)^β]`, "Use only if simpler models fail" (L19032–19042). Logistic/Gompertz, "process-specific candidates" (L19044–19054). Monod `μ = μmax S/(Ks+S)` (L19056–19070).
- Process-family library list (L19074–19087). "Select using evidence, fit diagnostics and generalization."
- §210.29A [SOURCE-REPORTED] anchors (L19137–19162):
  - (1) potato/frying/acrylamide models with coupled moisture/temperature/time and formation/loss
  - (2) glucose/glycine Maillard multiresponse models with pH-dependent kinetics
  - These are "simulator/reimplementation anchors, not as universal food kinetics" (L19144).
  - **Reference-temperature Arrhenius** `k = k_ref exp[−Ea/R (1/T − 1/T_ref)]` reduces k-scale/Ea correlation (L19146–19160).

### 2.4 Fitting/estimation protocol (§211, L19188–19853)
- NLS default (L19216–19230). WLS with σ_i² (L19232–19240). Log/relative error matched to the noise process "rather than convenience" (L19242–19250). MLE (L19252–19271). Heteroscedastic σ_i = g(x_i) (L19273–19283). Robust Huber/MAE, which "does not replace source-quality auditing" (L19285–19289). Censored likelihood (L19291–19316).
- Arrhenius: two-stage (interpretable, but first-stage uncertainty must be propagated; L19318–19329) vs global (L19331–19341). A/Ea correlation, "good interpolation can coexist with poor parameter/extrapolation certainty" (L19343–19355).
- Structural identifiability (L19357–19365) vs practical identifiability (L19367–19376). Parameter-count caution, "12 observations / 9 parameters is not strong evidence" (L19378–19389).
- Diagnostics: loss surface (L19391–19397); Hessian Cov ∝ H⁻¹ (L19399–19415); **study/experiment-level bootstrap** preferred (L19417–19433); profile likelihood (L19435–19443); Bayesian with transparent, sensitivity-checked priors (L19445–19458); positive reparameterisation k = e^η (L19460–19474).
- Hierarchical: `log k_i ~ N(μ_k, σ_k²)` (L19476–19486) and `log k_{i,p} = μ + α_i + β_p + γ_{i,p}` (L19488–19496). The latter mirrors ingredient×process generalisation.
- Multi-start (L19498–19508). Residual diagnostics vs time, T, concentration, matrix, study, platform (L19510–19527).
- CV modes: held-out time, temperature, ingredient/matrix, study. "Condition-OOD is especially important" (L19529–19538).
- AIC/AICc/BIC used "alongside held-out prediction/residuals rather than as the sole selection criterion" (L19540–19566). "Do not select by R² alone." Boxed criterion: prediction + uncertainty + residual diagnostics + identifiability + mechanistic plausibility (L19568–19576).
- Parameter plausibility checks: sign, units, magnitude, condition range, meaning (L19578–19588). Parameter vs predictive uncertainty must not be conflated (L19590–19604). Propagate via draws; "Extrapolation uncertainty should generally widen" (L19606–19616).
- Experimental design (L19618–19643). Confounded historical designs (process↔T, T↔duration, study↔platform, ingredient↔process): "No architecture fixes a structurally confounded dataset" (L19644–19657).
- **Within-study fitting first**, then pool/meta-analyse (L19659–19667). Random effects log k_s = μ + u_s, "Only pool parameters with comparable definitions and units" (L19669–19683). Study nuisance b_s (L19685–19693). Effective vs mechanistic naming (L19695–19699).
- Sensitivity matrix J and Fisher F = JᵀWJ (L19701–19719). Multimodality (L19721–19731). "Prediction can be identifiable when parameters are not" (L19733–19743).
- **Sequential hybrid**: fit mechanistic model → freeze/record → residuals → ML residual on held-out/grouped data (L19745–19754). Residual model ŷ_hybrid = ŷ_mech + r̂ (L19756–19770).
- Dataset-size regimes: tiny N → kinetics/Bayesian/regularised linear; hundreds–low thousands → trees; large condition-resolved trajectories → neural. These are "heuristics, not hard thresholds" (L19772–19780).
- **Aggregate-database limitation**: food+process+RF without T/t → "do not estimate true Arrhenius parameters from them" (L19782–19792).
- **Multi-fidelity bridge**: dense focused studies yield mechanisms, parameters and physics features, then test those on broad endpoint data; no universal transfer (L19794–19804).
- Core rule (L19843–19853): parameter estimate ≠ parameter knowledge without uncertainty and identifiability.

### 2.5 Multi-step ladder M0–M11 (§212.50, L20481–20507)
- M0 one-step persistence · M1 one-step process mean/lookup · M2 one-step tabular · M3 autoregressive neural · M4 teacher-forced sequence · M5 free-rollout event model · M6 history-aware GRU/state-space · M7 uncertainty-aware rollout · M8 graph split/merge · M9 hybrid event + local kinetics · M10 continuous latent dynamics · M11 broad reaction-network/world model.
- "Upper rungs require real trajectory supervision" (L20507).
- Strong sparse baseline (L20509–20523): deterministic procedure-state updater + process ontology + explicit merge/split rules + retrieved process-effect tables. "Do not assume a recurrent neural model will beat it."
- Retrieval-augmented transition loop (L20525–20535): retrieve → estimate/apply delta → update state → propagate uncertainty → stop when unsupported. "likely highly competitive for CulinaryState-RAG".
- Architecture direction:
  - Event-based dynamics first (L20447–20451).
  - Hybrid event graph + process-family local transition + kinetic operator for supported thermal/biological events (L20453–20465).
  - Hard-routed process-family experts: thermal-moist, thermal-dry, thermal-fat, mechanical, biological, cooling/storage, merge/split (L20467–20479).
- State-space machinery:
  - Markov assumption caveat (L19986–19996). History encoders GRU/LSTM/small transformer/SSM, "Use only if order/history data support evaluation" (L19998–20011).
  - Latent SSM (L20013–20033). Classical linear SSM baseline (L20035–20045). Filtering predict→observe→correct (L20047–20055). Open-loop vs corrected rollout (L20057–20071).
  - Scheduled sampling as an ablation (L20073–20077). Denoising with plausible perturbation scale (L20079–20091).
  - Jacobian stability δ_{t+1} ≈ J_T δ_t (L20093–20107). No universal contraction (L20109–20117).

### 2.6 Already-implemented ladder in repo (verified)
- `src/culinarystate/transition/baselines.py` L1–7 implements "DEL-2 baselines D0–D7":
  - D0 persistence (RF = 1)
  - D1 global mean
  - D2 process mean (backoff)
  - D3 hierarchical shrinkage target×process → process → global (empirical-Bayes pseudo-counts)
  - D4 nearest compatible evidence
  - D5 gradient boosting
  - **D6 TabPFN "not run (not installed; GPU) → recorded as SKIPPED"**
  - D7 biased MF with side-info biases
  - Naming matches SSOT D0–D7.
- `TRANSITION_BOOTSTRAP_V0` (`reports/h_state/transition_bootstrap_v0_contract.md` §3) re-labels the ladder as **B-0…B-5**: B-4 is a hierarchical-fallback lookup; B-5 is "simple tabular… only after B-0..B-4 are reported". It excludes TabPFN and learned models. This naming conflicts with the SSOT D-ladder and with the brief's "B0–B5 integrated ladder" (MPv4 L3456), which is a different (RAG) ladder. See §9.
- Empirical DEL-2 results (`reports/del2/*_results.md`, seed 7):
  - **USDA-RETN-R6:** 6,994 rows (2,620 censored); 38 matrices; 77 process signatures; 26 targets; grid density 0.0755. Matrix-disjoint MAE: D0 0.0590 [0.0407, 0.0711] vs D5 0.0692, D4 0.0567, D7 0.0759. On cold splits **persistence is at or near the best**. study_disjoint "NOT POSSIBLE".
  - **BOGNAR-2002:** 6,594 rows (3,274 censored); 28 matrices; **7 process signatures**; 36 targets; density 0.621.
    - Matrix-disjoint: D5 0.0463 [0.0386, 0.0509] beats D0 0.0621 [0.0349, 0.0825].
    - Process-disjoint CIs are **degenerate** (e.g. D5 0.0096 [0.0096, 0.0096]), consistent with a single held-out group. The cold "supported" claim on the process split is therefore not statistically meaningful (see §9).
  - **PHENOL-EXPLORER-3.6:** 3,870 rows; 146 matrices; 33 processes; 161 targets; density 0.00267.
    - D7 numbers are **identical to D1** on every split shown, so MF degenerated to the global mean.
    - Process-disjoint: D0 0.3676 is best.
    - study_disjoint present: D0 0.5577 vs D1 0.6978.
  - All three: "censored rows trained at lower bound 0.975 (assumption)". "D6 TabPFN: SKIPPED".

---

## 3. Experiments / hypotheses / RQs

### 3.1 RQ15-1…5 (§208.10, L18203–18224), verbatim essence
- **RQ15-1** (L18207): Does explicit transition modelling beat persistence, process-average, nearest-evidence and strong tabular baselines under **ingredient×process pair-holdout and study-disjoint** evaluation?
- **RQ15-2** (L18211): Do explicit continuous conditions and physics-derived exposure features improve **condition-OOD** generalisation over process labels and raw T,t alone?
- **RQ15-3** (L18215): For a focused kinetic system, does mechanistic + learned residual add value beyond pure kinetics and pure ML under condition extrapolation?
- **RQ15-4** (L18219): When intermediate measurements exist, do history-aware models improve short-horizon rollout **without becoming overconfident**?
- **RQ15-5** (L18223): Can conservative inverse search recover supported process conditions without exploiting OOD model error?

### 3.2 Embedded hypotheses / experiments in §§209–212 (no IDs assigned)
- H-persist: transition models must beat D0 on claimed dimensions (L18296).
- H-shortcut: process-only and food-identity-only models are shortcut baselines (L18405). This is G15-3's comparison (L22384).
- H-FiLM: FiLM/gating vs concat is an ablation (L18391).
- H-physfeat: log(1+t), 1/T_K and Ω with representative Ea values beat raw T,t in small-data ML (L18856, L18876). This is RQ15-2.
- H-two-scale: broad endpoint program + one or two focused kinetic systems (L18179–18201), "the canonical v12 plan".
- Kinetic model-family selection via AICc/BIC + held-out + identifiability + plausibility (L19540–19588).
- Kinetic CV: leave-one-temperature-out and leave-one-study-out as defaults (L19836).
- Multi-fidelity bridge: kinetic features from D-C tested on D-A/D-B (L19794–19804).
- Sequential hybrid residual (L19745–19770). This is RQ15-3 and G15-HYB.
- Rollout experiments:
  - teacher-forced vs free rollout (L19907–19939)
  - multi-step loss L_K (L19941–19949)
  - scheduled sampling ablation (L20073–20077)
  - denoising training (L20079–20091)
  - open-loop vs corrected (L20057–20071)
  - MC and ensemble rollout (L20170–20190)
  - horizon-wise coverage (L20192–20208)
  - integrated trajectory error (L20210–20222)
  - constraint-violation tracking (L20224–20234)
- **Semigroup test** (§212.52A, L20537–20549): T(t1+t2) ≈ T(t2)∘T(t1) under constant conditions. Report violation magnitude "only on process/target subsets where the assumption is scientifically reasonable". D8 satisfies it by construction; learned endpoint models may not. Feeds G15-8 (L22389).
- Repeated-process consistency, "dry 10+10 ≈ dry 20" (L20342–20358). Non-commutativity T_B∘T_A vs T_A∘T_B only "where order-effect evidence exists" (L20324–20340). Operator composition on unseen sequences (L20312–20322).
- Synthetic rollout benchmark from mechanistic simulators for method development, kept separate from real evaluation (L20441–20445).
- Controlled staged experiment, raw → pretreatment → dry → fry with intermediate measurements (L20426–20439). "A small staged experiment can be more valuable than a huge unstructured recipe corpus."

### 3.3 Repo experiment status
- EXP-000001..4 DONE: DEL-2 D0–D7 on USDA, PE raw, PE log, Bognár.
- EXP-000007 PLANNED: H_STATE explicit state vs none (B4 vs B3). It appears **twice with the same id** in EXP.jsonl, which looks like an ID-reuse or append-version anomaly worth checking (UNVERIFIED cause).
- No kinetic, physics-feature, hybrid or rollout experiment exists.

---

## 4. Gates, promotion and stop rules

### 4.1 Inside §§208–212: no gate IDs. Binding rules and the only numeric items, quoted with lines
- Boxed: **model ambition ≤ highest evidence rung actually present** (L18050–18055).
- D10 "not allowed to skip D0–D7" (L18607). D11 "Focused time-resolved systems only" (L18611).
- Persistence "is mandatory… Any claimed transition model must beat it on the dimensions it claims to transform" (L18292–18296).
- "The project may stop at retrieval/tabular/kinetic models if added complexity is not earned" (L18031). This is the **legitimate stop exit** for Steps 30–34.
- Aggregate DB without T/t gives no Arrhenius (L19790). Weibull/nth-order only if simpler models fail (L18730, L19042). Moisture-gated only with evidence (L18896).
- `[SOURCE-REPORTED / PILOT]` Arrhenius design target: "roughly **≥3, preferably ≥4 temperatures with ≥4–5 time points each** … a planning rule, not a universal literature standard" (L19162).
- `[SOURCE-REPORTED / PILOT]` "**≥5 observations per fitted parameter** and a **condition-number warning around 10⁶**. These are engineering diagnostics, **not frozen scientific thresholds**" (L19841). Condition number is "an identifiability warning rather than a pass/fail proof" (L19837).
- Rollout abstention triggers (L20149–20158): evidence distance too large, uncertainty too high, constraint violations, calibrated coverage no longer holds. Action: "stop quantitative rollout or downgrade to a broader qualitative statement".
- "A rollout must not silently continue indefinitely" (L20125).
- Trust horizon (L20556–20565): `H_trust = max k s.t. Coverage(k) ≥ c_min, E(k) ≤ ε_max, OOD(k) ≤ τ`. "values c_min, ε_max, τ are task-specific and must be calibrated on real held-out sequences." There is **no universal number**; "state/process-specific, not a universal number of steps" (L20147).
- One-step conformal ≠ trajectory coverage (L20194). Evaluate coverage by horizon.
- "Partial culinary world model… Do not describe it as a universal kitchen simulator" (L20379–20381). This is a claim-boundary gate on publications and the UI.

### 4.2 Binding G15 gates these sections feed (outside my range; quoted for mapping only; SSOT L22380–22427, frozen per L23077)

| Gate | Pass criterion (quoted, SSOT line) | Fed by |
|---|---|---|
| G15-1 Data audit | "Every quantitative row has source/study, evidence tier, units/target definition, yield/normalization status, and censoring/missingness status." (L22382) | §208.4, §211.8 |
| G15-2 Baselines | "Canonical D0–D6 are reported on all eligible headline splits before D7+ claims." (L22383) | §209.17 |
| G15-3 Process signal | "Process-conditioned modeling adds value over food-identity-only on a process-disjoint or equivalent controlled split; report CI/effect, not just point gain." (L22384) | §209.9 |
| G15-4 Kinetic fit | "At least one focused D-C dataset supports an identifiable/useful kinetic fit with profile/bootstrap/posterior uncertainty." (L22385) | §§210–211 |
| G15-5 Condition-OOD | "Kinetic/hybrid/physics model adds value over the best non-kinetic tabular baseline on held-out temperature/condition." (L22386) | RQ15-2/3, §210.13–14 |
| G15-6 Calibration | "Real, study-disjoint calibration…" (L22387) | §209.13–14 |
| G15-7 Abstention | "…abstention rules are defined on REAL calibration data." (L22388) | §212.22 |
| G15-8 Consistency | "Relevant non-negativity, semigroup/order/balance/constraint diagnostics are reported on scientifically valid subsets." (L22389) | §212.29–31, 212.38–39, 212.52A |
| G15-9 Completion | "Evidence-aware D7 completion beats D5/D6 on masked-real-cell and cold food/process/compound/pair tests, or is rejected." (L22390) | D7 |
| G15-10 Synthetic/imputed | "…no synthetic/imputed target enters final test/calibration." (L22391) | rule 13, §212.46 |
| G15-11 Rollout | "A trust horizon is empirically established on D-C/D-D where true intermediate states exist; no rollout claim otherwise." (L22392) | §212.21, 212.52B |
| G15-12 Inverse design | "…beyond nearest-evidence/random/grid and remains inside the safe support region." (L22393) | RQ15-5, §212.41 |
| G15-R / G15-H / G15-I | reproducibility / human verification of LLM-extracted test rows / integration logging (L22394–22396) | §212.53 |
| G15-HYB | hybrid only if it adds held-out/OOD/calibration value beyond both mechanistic and pure ML, or a demonstrated physical-consistency advantage (L22412–22414) | §211.45–46 |
| G15-INV | "inverse-design ceiling ≤ forward-model credibility" (L22418–22424) | rule 9 |

Note on G15-11: "D-C/D-D". D-D recipe corpora "Does not directly support quantitative chemistry" (L21994–21996). So a G15-11 pass on D-D can only license R0/R1 procedural/qualitative rollout, never R2+. The gate text does not say this explicitly. Flagged in §9.

### 4.3 Current gate status (repo)
- "G15: 0 of 15 passed" (`ssot15_state_program_inventory.md` L47).
- G15-2 is **unpassable as currently run**, because D6 is SKIPPED in all DEL-2 runs. Either run TabPFN on CPU (for small N it may be feasible; UNVERIFIED in this run, needs research) or document D6 as "ineligible" under the activation rule (L22022–22026) with a justification.
- G15-1 is partially blocked: yield/normalisation status is mixed (RT-004 TR_OR_AR_UNDISCLOSED for USDA R6, `registry/retention_type_registry_v1.csv`).

---

## 5. Data requirements and named sources (licence notes)

### 5.1 Data requirements implied by §§208–212
- **L15-BROAD (D-A/D-B):** matched before/after, retention or fold-change, with basis (true/apparent/yield-adjusted), censoring and LOD, platform, study_id, and T/t where available (L18033–18046, L19291–19316, L19782–19792).
- **L15-FOCUSED (D-C), at K1/K2 minimum:**
  - same matrix/target measured at multiple times (K1), and at multiple temperatures for Arrhenius (K2): pilot target ≥3–4 T × ≥4–5 t (L19162)
  - replicates and SD (needed for WLS/heteroscedastic/MLE; L19232–19283)
  - the **temperature schedule T(τ)** with measurement location for Ω (L18816–18854)
  - moisture trajectory M(τ) if moisture gating is claimed (L18878–18896)
  - multiple species (K3) for network/multiresponse fitting (L18956–18972)
  - leaching water-compartment measurements to separate degradation from leaching (L18987–19000)
  - headspace/volatile loss to separate volatilisation (L19002–19020)
- **Rollout (R2+):** measured intermediate states after each stage (L19951–19971, L20426–20439). Recipe text provides sequence only: "procedural rollout ≠ quantitative chemistry rollout" (L19966–19970).
- **Calibration/trust horizon:** real held-out sequences (L20565).
- **Independence:** study/experiment grouping for bootstrap (L19433) and for leave-one-study-out (L19836). Within-study fitting needs a study_id on every timepoint row (L19659–19667).

### 5.2 Named sources in my range
- §210.29A names model families, not datasets: "potato/frying/acrylamide" and "glucose/glycine Maillard multiresponse" (L19141–19142). It cites no paper IDs, DOIs or licences. **The specific source papers are UNVERIFIED in SSOT text**; they must be located in Steps 13/14 (per-article licence).
- No other dataset is named in §§208–212.

### 5.3 Repo source reality (verified)
- Held: USDA R6 retention, Bognár 2002, Phenol-Explorer 3.6. All are E3 aggregate, i.e. D-A/K0. Phenol-Explorer can be D-B-like where per-paper.
- ES-1.2 census: "no structured open source was found for mechanism, kinetic or physical time-series evidence… SOURCE_GAP for 13 of 16 priority-cell rows; the discovery route is open-access primary literature" (`reports/h_state/es_1_2_source_census.md` L7). Kinetic routes are DS-043/044/045 (literature, ComBase) with PER_ARTICLE_LICENCE (L57, L75). Rhea/BRENDA give "reference reactions and in-vitro parameters, not in-food kinetics" (L76).
- The potato×frying acrylamide cell is "SOURCE_GAP (structured kinetics); literature rich", with 840 local EVD rows on the potato matrix (endpoint only) (L86).
- MPv4 SX-06-04 (L363) proposes a kinetic parameter table for acrylamide/potato, Maillard glucose/glycine, vitamin C, anthocyanin and chlorophyll. Its literature queue item 5 (L917) asks for "Kinetic parameters (Ea, k, order) for vitamins, pigments, acrylamide, HMF, browning — reviews and databases".
- Licence: kinetic literature is per-article (CC-BY OA vs closed). Fitted parameters re-derived from closed-access figures/tables are derived data. The licence posture for storing digitised timepoints from closed papers is **unresolved** and needs Step 08/06 policy. Digitising plots (e.g. WebPlotDigitizer-style) also introduces extraction uncertainty that needs its own field.

### 5.4 Literature I would cite for these sections (from my own knowledge; NOT re-verified in this run, so treat as UNVERIFIED until the bibliography agent checks)
- van Boekel, M.A.J.S. (2008/2009) *Kinetic Modeling of Reactions in Foods*, CRC Press: multiresponse modelling, glucose/glycine Maillard, Arrhenius reparameterisation.
- Raue, A. et al. (2009) Bioinformatics 25(15):1923–1929: profile-likelihood structural/practical identifiability.
- Peleg, M. & Cole, M.B. (1998) on Weibull inactivation: Weibull kinetics.
- Hollmann, N. et al. (2025) Nature 637: TabPFN v2: D6 feasibility for N ≤ ~10k (CPU feasibility and licence UNVERIFIED).
- Rackauckas, C. et al. (2020) arXiv:2001.04385: Universal Differential Equations, i.e. D11.
- Acrylamide frying kinetics: e.g. Knol et al. (2005/2009, J. Agric. Food Chem.) multiresponse acrylamide models. UNVERIFIED exact refs.
- Kinetics review: Corradini & Peleg (2006/2007) on non-isothermal Weibull/Arrhenius. UNVERIFIED.

---

## 6. Dependencies on other levels/steps

- **Level 14 (§§197–205):** E ≠ T (L18010). Level-14 process/evidence table feeds the Level-15 transition schema (§216.7 L22900–22904). Physics features appear in both MPv4 B12 SX-12-02 (L467) and Level-15 §210.13–14, so ownership must be decided (Step 31 vs B12).
- **Level 12/13 embeddings z_i, z_m, z_R:** used as optional features only after their own gates pass. "Level 15 must not depend on an unvalidated upstream learned embedding to function at all" (§216.10, L22967–22979). The §209.6 tabular feature vector lists z_i (L18345), but in practice a simple hand-crafted/categorical ingredient encoding must be the default.
- **PART XI sparsity/MNAR/synthetic prior (§§219–227):** D7 and G15-9/G15-10. Synthetic rollouts (L20441–20445) depend on the E7 prior design (Step 28).
- **Level 16 / CulinaryState-RAG:**
  - D4 nearest-evidence (L18320–18336) and the retrieval-augmented transition loop (L20525–20535) are the RAG transition fallback (§216.7 L22912).
  - The transition provenance graph (L20567–20581) feeds evidence packet fields "MODEL ESTIMATES", "KNOWN UNKNOWNS" and "interpolated/extrapolated".
  - Rollout abstention (L20149–20158) feeds the DIRECT → INTERPOLATE → MODEL → QUALITATIVE → ASK → ABSTAIN cascade (brief §28).
- **Level 13E:** no direct dependency.
- **Recipe event/state graph (Phase D, Steps 16–20):**
  - Merge/split/reserve/discard semantics (L20262–20304), graph operator (L20296–20304), R0/R1 rollout (L20402–20409) and the symbolic baseline (L20509–20523) all require the Step-18 event-sourcing engine and the Step-19 gold trajectory pilot.
  - Procedure graph ≠ chemistry graph (L20306–20310).
- **Formula/model registry (Step 24) and applicability (Step 23):** the §210 library and §210.29 schema are registry content. Moisture gating, pH dependence and matrix scope are applicability conditions.
- **Simulator (Steps 26–28):** §210.29A anchors are "simulator/reimplementation anchors" (L19144). §211 is the calibration/identifiability protocol any simulator validation needs. So Step 26/27 depends on §211 machinery that the spine places at Step 32.

---

## 7. Risks / failure modes (with SSOT anchors)

1. **Data-rung inflation.** Fitting kinetics or Arrhenius to K0 aggregate data violates rule 2 (L18018) and L19790. Repo evidence is ~all K0 (COND: 213 temperature entries VALID with location; zero pH/moisture).
2. **Persistence dominance on cold splits.** Already observed: USDA matrix-disjoint D0 is among the best; PE process-disjoint D0 is best. The risk is complexity escalation in place of acquisition. SSOT L18031 permits stopping, and the bootstrap contract §6 forbids escalation.
3. **Hidden-mechanism lumping.** A single k hides degradation + leaching + volatilisation (L18987–19020). An endpoint cannot identify the dominant mechanism (L19020).
4. **A/Ea compensation.** Narrow T range gives a precise-looking fit and wrong extrapolation (L19343–19355, L19638–19642).
5. **Over-parameterisation** with 12 obs / 9 params (L19378–19389).
6. **Confounded literature designs** (L19644–19657), e.g. process ↔ T ↔ duration ↔ study ↔ platform. In USDA/Bognár, process signatures equal source-family protocols.
7. **Naive row bootstrap** overstates certainty (L19433). The repo uses grouped CIs (good), but the degenerate Bognár CIs reveal too few groups.
8. **Censoring mishandled.** DEL-2 trains censored rows "at lower bound 0.975 (assumption)", which is a form of single-value imputation. SSOT prefers a censored likelihood (L19300–19305).
9. **Pooling incomparable parameters** across orders/units (L19184, L19683). There are no kinetic units in UNIT.jsonl yet.
10. **Exposure bias and rollout drift** (L19917–19931, L20119–20125). Rollout continuing past support breaks L20125.
11. **One-step conformal misused for trajectories** (L20192–20196).
12. **Forced contraction/stability** hides real threshold amplification (L20109–20117).
13. **Naive mass balance** in open systems (L20244–20260). The retention-capped-at-1 constraint can be wrong (L20242).
14. **Procedure accuracy mistaken for chemistry accuracy** (L20306–20310, L19966–19970).
15. **Model counterfactuals reported as causal** (L18501–18523).
16. **Planner exploits model error** (L20366–20375).
17. **"World model" overclaim** (L20377–20381).
18. **Synthetic-to-real leakage** in rollout benchmarks (L20441–20445, G15-10).
19. **Temperature semantics:** Ω needs product (core/surface) temperature, but most sources report setpoint/medium. Using setpoint inside Ω silently changes meaning. SSOT §210.12–13 does not state which temperature; the Step-07 registry distinguishes them (step07_report L9).
20. **Retention basis mixing** (true/apparent/yield-adjusted). RT-004 USDA undisclosed. Mixed bases cannot be pooled (step07_report L9).

---

## 8. MAPPING TO THE 36-STEP SPINE (reconstruction; the 36-step cards are MISSING)

For each step: what §§208–212 require. "Gate" names cite G15 IDs from §215.38 (L22380–22396) where relevant.

**Step 03 Freeze state semantics**
- Inputs: §208.8 view factorisation (L18166–18174); delta form (L17972–17975); L15-A…F ladder (L18058–18110); q_t coverage vector (L20388–20395).
- Outputs: per-SVAR `value_type` and **delta_semantics** (additive / multiplicative-retention / categorical / non-transitionable); a view assignment; observability (O_t vs S_t, L18525–18541).
- Gate: crosswalk of the SSOT views ↔ `state_representation_contract_v1` (C, P^phys, Y^sens, N, V, A).

**Step 04 Freeze evidence/provenance/similarity contracts**
- Must include the §212.53 transition provenance fields (L20571–20579) and the `interpolated/extrapolated` flag.
- Must include the §210.29 / §211.50 / §216.2 kinetic contracts as one unified schema (currently three lists; §9).
- Must include the "effective_or_mechanistic" parameter flag (L19133, L19697).
- Must include "evidence tier" for SIM vs real (rule 13, L18029).

**Step 05 Normalize EVD**
- G15-1 fields (L22382): basis, yield/normalisation status, censor + LOD + platform (L19311–19314), units.
- Add `matrix x process signature` independence units (already in bootstrap contract §1).
- Do not impute censored to a constant in the canonical row; store the bound.

**Step 06 Source acquisition manifest**
- Rank sources by **K-rung** (K0–K4, L19089–19109) and D-regime.
- Explicit targets for K1/K2 focused systems meeting the pilot design (L19162).
- Include staged-experiment sources with intermediates (L20426–20439) and a leaching/water-phase measurement flag.

**Step 07 Condition & measurement normalisation (done/frozen except the human audit)**
- Already supports trajectories (CV-004, CV-010 with stated location, CV-011 rate), separate setpoint/medium/surface/core temperatures, and censoring kinds. This satisfies the §210.12 prerequisites in schema.
- Still required for §210:
  - Kelvin conversion stored as a derived column (L18759–18763)
  - kinetic unit types in UNIT (k by order, Ea in kJ·mol⁻¹)
  - moisture with wet/dry basis (present) as a trajectory
  - pH/aw trajectories
- The human audit (kappa ≥ 0.8; step07_report L26) gates any scientific use of conditions, and therefore G15-5.

**Step 08 Scientific source lineage (NOT to execute; plan only)**
- §211.37–211.39 within-study fitting and study-level random effects need `study_id`, `experiment_id`, `series_id` and `replicate_id`.
- Leave-one-study-out (L19836) and study bootstrap (L19433) need publication-connected-component grouping (MPv4 DEL-2, L3105–3106).
- Lineage must also record **figure-digitised vs table-reported** origin of timepoints.

**Step 09 Extraction & verification machinery**
- Must extract **series** (time × T × value × SD × n), not just endpoints.
- Must capture the temperature schedule and its location; censoring (ND/<LOD); platform; reported fitted parameters with CI; and the stated model family.
- G15-H (L22395) requires human verification for any LLM-extracted test/calibration row.

**Step 10 20-row mechanism pilot**
- Include ≥1 K1/K2 kinetic series row (e.g. potato acrylamide or ascorbic acid) to test series extraction end-to-end.
- Record K-rung per row.

**Steps 11–14 Evidence acquisition / growth**
- Coverage must be measured on **K-rung and condition axes** (T, t, T-location, moisture, pH, aw), not row count.
- Step 14 coverage-driven growth should use the Fisher-information/design logic (L19701–19719) and time/temperature placement criteria (L19630–19642) to prioritise series spanning the transformation range and several temperatures.
- Kinetic families per MPv4 SX-06-04 (L363).

**Step 15 Freeze DATA-EVIDENCE v1**
- Freeze **separate strata** D-A/D-B/D-C/D-D with trajectory availability (L21998–22010).
- Freeze study-disjoint split feasibility per source (currently impossible for USDA/Bognár).
- Gate: G15-1 audit.

**Steps 16–20 Recipe procedure/state**
- Merge/split/reserve/discard/recombine (L20284–20292); graph operator (L20298–20302); explicit source/sink terms (L20260).
- Event-based segmentation (L20447–20451); process-family expert routing classes (L20471–20477).
- The Step-19 gold trajectory pilot supplies R0/R1 supervision, i.e. G15-11 on D-D procedural only.
- Order/history labels are needed for history-aware models (L20011).

**Step 21 Effect/mechanism ontology**
- Distinguish degradation / leaching / volatilisation / formation / consecutive / parallel (L18898–19020).
- Map process families to transition semantics (L20465).

**Step 22 Event → effect signatures**
- Direction labels (L15-A) and ordinal bands (L15-B) per event × target.
- Provide the "process-effect tables" of the symbolic baseline (L20514–20520).

**Step 23 Mechanism applicability engine**
- Activation conditions: moisture gating (L18880–18896), pH dependence (L19142), matrix precursors (L18409–18416), T regime (L19642).
- Output UNKNOWN when there is no evidence (rule 12).

**Step 24 Formula/model registry**
- Rows for every §210 family (L19074–19085), with units per order (L19164–19184), reference-T Arrhenius (L19148–19158), effective vs mechanistic flag (L18985), and parameter positivity (L19460–19474).
- Required fields: equation, state vars, parameters+units, assumptions, IC/BC, matrix/condition scope, identifiability status, source, verified (union of §210.29 + §211.50 + §216.2).

**Step 25 Parameter-compatibility retrieval**
- Retrieve parameters only when order/units/target definition/matrix/T-range are comparable (L19184, L19683).
- Return parameter CI, not a point (L19843–19853).
- Flag extrapolation beyond the fitted T-range (L19616).

**Step 26 Focused deterministic simulator**
- Choose from the §210.29A anchors or a simpler first-order/Arrhenius system. The simulator implements D8 with the variable-temperature solution (L18832–18836) and Ω (L18844).
- It needs §211 fitting (NLS/MLE, positive params, multi-start, profile, study bootstrap) to calibrate.
- **Recommendation (reconstruction):** factor §211 machinery into a shared module created at Step 24/26, not first at Step 32.

**Step 27 Validate simulator on held-out evidence**
- CV modes leave-one-temperature-out and leave-one-study-out (L19836); residual diagnostics (L19510–19527); plausibility (L19578–19588).
- Parameter vs predictive uncertainty kept separate (L19590–19616).
- Gate: G15-4 (one identifiable kinetic fit with profile/bootstrap/posterior; L22385).
- Fail → RESEARCH_ONLY simulator (brief §40).

**Step 28 E7 synthetic prior**
- Synthetic trajectories for method development only (L20441–20445). Separate fidelity tier (rule 13).
- Gate: G15-10 ratio sweep, with no synthetic target in test/calibration (L22391).

**Step 29 TRANSITION_BOOTSTRAP_V0**
- Contract exists (`reports/h_state/transition_bootstrap_v0_contract.md`).
- Required by SSOT: D0 mandatory (L18292); D1/D2/D3/D4 (L18547–18576); evaluation on pair-holdout + study-disjoint (RQ15-1, L18207); censor-aware loss (L19291–19316); grouped/cluster bootstrap (L19433).
- Outputs: per-split tables with n_independent_groups.
- Gate: subset of G15-2 (D0–D4) and G15-3.
- **Fix:** align naming to D0–D4 (not B-0..B-5), and replace "lower bound 0.975" censor handling with a censored/Tobit likelihood or interval loss, at least as a sensitivity arm.

**Step 30 Strong tabular / sparsity bake-off**
- D5 LightGBM/XGBoost; D6 TabPFN (or a documented ineligibility); D7 MF/FM/BPMF with side information (L18578–18595).
- Masked-real-cell and cold food/process/compound/pair tests. Gate: G15-9 (L22390).
- G15-2 requires D0–D6 before D7+ claims (L22383).
- Current evidence: D7 degenerates on PE (=D1) and loses to D5 on USDA/Bognár, so the D7 hypothesis is presently weak.

**Step 31 Physics / condition features**
- log(1+t), 1/T_K, Ω with a grid of representative Ea values (L18856–18876), moisture-gated Ω only with evidence (L18896).
- Test RQ15-2 on condition-OOD (held-out temperature).
- Gate: G15-5 (L22386) partially; full G15-5 also needs Step 32/33.
- **Ordering caveat:** the multi-fidelity bridge (L19794–19804) and §216.7 (kinetic fits → physics features, L22914–22920) imply fitted-Ea features come after Step 32. Recommend 31a (generic features, literature Ea grid) before 32 and 31b (fitted-parameter features) after 32.
- Also needs location-valid temperatures (only 213 VALID today), so this step is NEED_DATA for a meaningful condition-OOD test.

**Step 32 Focused kinetics**
- Inputs: ≥1 D-C dataset at K1/K2 (pilot ≥3–4 T × ≥4–5 t, L19162).
- Methods: NLS/MLE, WLS/heteroscedastic, censored likelihood (L19216–19316); reference-T global Arrhenius + two-stage diagnostic (L19833); log-space positive params; profile all key parameters; cluster/study bootstrap; LOTO/LOSO CV (L19832–19839); AICc/BIC + held-out + plausibility (L19540–19588); identifiability notes (L19357–19377).
- Outputs: the §211.50 minimal kinetic report per fit (L19808–19826) and kinetic-experiment rows (§216.2).
- Gate: G15-4 (L22385).
- Stop: if no identifiable fit exists, record a negative result and do not proceed to D9/D11.

**Step 33 Mechanistic vs ML vs hybrid**
- Sequential hybrid protocol (L19745–19770); RQ15-3 (L18215).
- Gates: G15-HYB (L22412–22414) and G15-5 (L22386).
- Compare against the best non-kinetic tabular (D5/D6) on held-out temperature.
- Semigroup consistency test for D8 vs learned (L20537–20549), i.e. G15-8.
- Stop exit: "may stop at retrieval/tabular/kinetic" (L18031).

**Step 34 Short rollout**
- Prerequisites: measured intermediates (L19951–19971, L20426–20439) or Step-19 procedural gold for R0/R1 only.
- Ladder M0–M2 first (L20483–20488); symbolic/retrieval baseline (L20509–20523); retrieval-augmented loop (L20525–20535).
- Metrics: E(k), interval width and coverage vs horizon (L20198–20208); E_traj (L20210–20222); constraint violations (L20224–20234).
- H_trust with c_min/ε_max/τ calibrated on real held-out sequences (L20556–20565). Rollout abstention (L20149–20158).
- Gate: G15-11 (L22392).
- **Status reconstruction: NEED_DATA for R2+**. ES-1.2 found no structured time-series sources. Only R0/R1 is feasible within the plan horizon.

**Step 35 Representation ladder**
- E ≠ T (L18010). Embeddings enter transitions only as ablation features after their own gates (L22967–22979).

**Step 36 Evidence compiler → CulinaryState-RAG → FlavorTwin**
- Consumes D4/retrieval-augmented transition (L20525–20535), the provenance graph (L20567–20581), H_trust and rollout abstention (L20137–20158), and counterfactual wording limits (L18501–18523).
- Inverse design is gated by G15-INV / G15-12 (L22393, L22418–22424) and rules 9–11 (L18025–18027).
- "Partial culinary world model" wording boundary (L20379–20381).

---

## 9. Contradictions, stale items, underspecified parts, open questions

**C1. Three overlapping ladders with no crosswalk.**
- D0–D11 (L18543–18613) is canonical v13. M0–M11 (L20481–20507) is the multi-step ladder. The repo bootstrap ladder is B-0…B-5. MPv4 also uses "B0–B5" for the integrated RAG ladder (L3456). Steps 29/34/36 need a crosswalk: M0 = D0, M1 ≈ D2/D4, M2 ≈ D5, M9 ≈ D9, M10 ≈ D10/D11.
- L18613's "old v12 neural sub-ladder" is not enumerated in my range (UNVERIFIED which list it refers to; possibly §209.6–209.8 text).

**C2. Spine order 31 (physics features) → 32 (focused kinetics) vs SSOT §216.7**, which runs "kinetic fits → physics features → mechanistic vs ML vs hybrid" (L22914–22920), and vs §211.49 multi-fidelity bridge (L19794–19804). §210.13 permits representative-Ea features without fitting (L18856), so the conflict is resolvable by splitting Step 31 (see §8). This needs a decision.

**C3. Simulator (26–27) before focused kinetics (32).**
- §210.29A anchors are simulator anchors (L19144), and §211 is the calibration protocol. Steps 26/27 and 32 risk duplicating kinetic-fitting work, or 26 running without the §211 protocol.
- Proposed: either one shared "kinetic fitting & identifiability module" owned by Step 24/26 and reused by 32, or merge 32 into the 26/27 focused system with 32 extended to a second system.
- Also unresolved: are the simulator's focused system and Step 32's focused system the same? SSOT §208.9 says "one or two kinetic systems" (L18193).

**C4. G15-11 "D-C/D-D" ambiguity.** D-D cannot support quantitative chemistry (L21994–21996; L19966–19970). The gate text should say that a pass on D-D licenses only R0/R1. Propose an SSOT change request (PROPOSED_ONLY).

**C5. G15-2 vs repo D6 SKIPPED.** G15-2 requires D0–D6 (L22383). D6 has never run ("not installed; GPU"). An open question needing research: can TabPFN v2 run CPU-only at these sizes (≈4–7k rows)? What is its licence (Prior Labs licence terms)? UNVERIFIED. Otherwise apply the activation rule (L22022–22026) to declare D6 ineligible, with the reason recorded before results.

**C6. Censoring handling.** DEL-2 uses "lower bound 0.975 (assumption)" vs SSOT censored likelihood (L19300–19305). The bootstrap contract says "CENSORED kept censored" with censor-aware MAE, which is consistent for evaluation but not for training. Needs a Tobit/interval-censored training arm.

**C7. Bognár "supported incl. cold".** The inventory (L47) claims this, but the process-disjoint CIs are degenerate (7 process signatures; D5 0.0096 [0.0096, 0.0096]). Matrix-disjoint D5 0.0463 vs D0 0.0621 has overlapping CIs [0.0386, 0.0509] vs [0.0349, 0.0825], and no paired test is reported in the .md. The claim of cold support should be re-checked with paired bootstrap per the bootstrap contract §6. UNVERIFIED whether the JSON has paired results.

**C8. Phenol-Explorer D7 = D1 exactly.** The factorisation is degenerate at density 0.00267, so G15-9 is effectively "reject" on this source. The cause may be implementation (side-info biases not learned) or data sparsity. Needs diagnosis before Step 30 claims.

**C9. Retention > 1.** SSOT warns retention can legitimately exceed 1 (L20242). The Step-07 normaliser marks "fraction > 1 INVALID" (step07_report L9). This likely applies to bare fraction parsing, not to retention metrics, but it must be verified so true retention >1 (formation, yield correction) is not discarded. Formation reactions (L18898–18914) make >1 normal for formed species.

**C10. Three kinetic schemas** (§210.29 L19115–19135; §211.50 L19808–19826; §216.2 L22800–22823). There is no single canonical field list; for example `verified` exists only in §210.29 and `identifiability_status` only in §216.2. Step 04/24 must unify them.

**C11. Underspecified temperature semantics for Ω and Arrhenius.**
- Which temperature (product core / surface / medium / setpoint) is unspecified (L18816–18854).
- Non-isothermal heat penetration is not modelled at all (no heat-transfer PDE). The Ω features will be setpoint-based for nearly all literature rows.
- Open research: when is setpoint-based Ω a usable proxy (thin samples, liquid media) vs misleading (frying, roasting large items)?

**C12. Coverage-vector inconsistency.** §208.8 includes "visual" (L18172); q_t omits it (L20388–20395). Minor.

**C13. Stale status text.** §208.1 status (L17936–17945) predates repo results. It does not record that broad endpoint baselines exist and show negative cold results (EXP-000001..4). Not a contradiction, but the "feasible" wording should be read as conditional.

**C14. No numeric gates for kinetic adequacy.** By design the thresholds are pilot only (L19162, L19841). Steps 27/32 must **pre-register** task-specific thresholds before seeing results (law: no post-hoc gate weakening). Open: what minimum held-out improvement and coverage define G15-5 pass? The SSOT leaves this unspecified.

**C15. History H_t.** It is in the core signature (L17952) but undefined: which history fields (previous processes, cumulative Ω, previous moisture)? Step 18 must define the H_t payload.

**C16. Data-to-claim ladder "controlled alternative conditions → stronger counterfactual"** (L18045). There is no field marking a study as controlled (same lot, varied factor). Step 08/09 need a `design_controlled_factor` field.

**Open questions requiring external research (for the research agents):**
- Q1. Best first focused kinetic system given open data: ascorbic acid thermal degradation, chlorophyll→pheophytin, anthocyanin, acrylamide in potato, or glucose/glycine Maillard. What open K2 datasets with ≥3–4 temperatures exist, with what licences?
- Q2. Is TabPFN v2 runnable on CPU at N≈4–7k, and is its licence compatible?
- Q3. Censored regression for GBDT: is a Tobit/interval-censored objective (e.g. XGBoost survival:aft) appropriate for retention capped at 97.5–100%?
- Q4. Standard practice for reporting kinetic identifiability in food science (profile likelihood; collinearity indices).
- Q5. Do published staged-cooking datasets with intermediate measurements exist (moisture/colour/compounds per stage)? If not, R2+ rollout is out of scope.
- Q6. Setpoint vs product temperature: literature on the error of using oven/oil setpoint in kinetic models of fried/roasted foods.

---

## 10. LOOK-AHEAD: fields earlier steps must capture

So that §§208–212 (and the §216 contracts they feed) are usable at Steps 24–34 and 36:

**Steps 03/04 (schemas)**
- Per state variable:
  - `delta_semantics` (ADDITIVE / RATIO_RETENTION / LOG_FOLD / CATEGORICAL / ORDINAL / NOT_TRANSITIONABLE) (L17975)
  - `view` (physical/chemical/sensory/nutrition/visual/procedure) (L18166)
  - `fidelity_rung` (L15-A..F) (L18058–18110)
  - `bounds_type` (hard / soft / may-exceed-1) (L20236–20242)
- Per evidence row: `K_rung` (K0–K4) and `data_regime` (D-A..D-D) (L19089–19109; L21949–21997).
- Transition provenance: `evidence_distance`, `interpolated_or_extrapolated`, `model_version`, `predicted_delta`, `uncertainty_type{aleatoric, epistemic, ood, parameter}` (L18490–18499, L20571–20579).
- Kinetic parameter object:
  - `effective_or_mechanistic`, `reaction_order`, `k_unit` typed by order, `Ea_unit`
  - `T_ref` (for reference-T Arrhenius, L19148–19158)
  - `fit_T_range_lo/hi`, `fit_t_range` (for extrapolation flags, L19616)
  - `identifiability_status{structural, practical, profile_flat}`
  - `parameter_CI_method{hessian, bootstrap_cluster, profile, posterior}`
  - `n_timepoints`, `n_temperatures`, `n_replicates`
  - `cv_mode`, `heldout_metric`
  - `prior_spec` (if Bayesian, L19458)

**Step 05 (EVD)**
- `censor_flag` + `censor_kind` + `limit` (LOD/LOQ/cap) + `platform` (L19311–19314). Some exist in `derived.*.censor`; LOD is not a column (evd_contract_v1).
- `retention_basis` (true / apparent / yield-adjusted / undisclosed).
- `matched_before_after` flag; `before_value`/`after_value` separately (contract fields exist; populated?).
- `measurement_sd`, `n_replicates` as separate fields. `uncertainty` exists on only 9,431 retention objects.

**Step 07 (conditions; frozen, but extend additively)**
- `temperature_location` mandatory for kinetics; `T_K` derived column; `temperature_schedule` (CV-010) with stated location; heating rate (CV-011); preheat.
- `moisture_trajectory` with basis; `pH` and `aw` start/end; oxygen/headspace; `medium` and medium-to-food ratio (needed for leaching compartments, L18987–19000); `lid/open` (volatilisation, L19002–19020); sample geometry/size (L18414; heat penetration).
- UNIT additions: `min⁻¹`, `s⁻¹`, `h⁻¹`, `mol·L⁻¹·min⁻¹`, `L·mol⁻¹·min⁻¹`, `kJ·mol⁻¹`, `kcal·mol⁻¹`. All absent today.

**Step 08 (lineage; plan only)**
- `study_id`, `experiment_id`, `series_id` (one kinetic series = one matrix × target × condition schedule), `replicate_id`, `lot/batch_id` (same-lot controlled comparisons; L18045).
- `publication_component_id` (study-disjoint feasibility).
- `data_origin{table, text, figure_digitised, supplementary, author_fit_only}` and `digitisation_uncertainty`.
- `analytical_platform` (L19524, L19652).
- `design_controlled_factor` (which factor varied with others held fixed; L18045, L19644–19657).

**Step 09 (extraction)**
- Long-format timepoint extraction: (series_id, t, T(t) or schedule ref, value, SD, n, unit, censor).
- Extraction of **author-reported fitted parameters** (k, Ea, A, order, model family, CI, R², fit method), kept separate from project re-fits (L19806–19826; never conflate author fit with project fit).
- Multi-species simultaneous measurement linkage (same sample, multiple targets) for K3 (L18956–18972).
- Water/medium-phase concentrations (leaching) and headspace (volatiles) as linked targets.

**Steps 10–15 (acquisition)**
- Record per acquired series: K-rung, number of temperatures, number of timepoints, whether the series spans the transformation range (L19630–19636), and whether temperatures stay in one mechanistic regime (L19642).
- Prefer studies with ≥3–4 T × ≥4–5 t (pilot rule L19162).
- Staged-process datasets with intermediates (L20426–20439) should be flagged as rare high-value Step 34 enablers.
- Step 15 freeze: per-stratum split manifests (pair-holdout, study-disjoint, leave-one-temperature-out, leave-one-study-out, condition-OOD), with n_independent_groups.

**Steps 16–20 (procedure/state)**
- `event_index`, `sequence_id`, `entity_ids_in/out` (merge/split), `operation_type ∈ {reserve, discard, remove, split, recombine}` (L20284–20292), quantity partition fractions or UNKNOWN (L20280).
- Process-family expert class per event (thermal-moist/dry/fat, mechanical, biological, cooling/storage, merge/split; L20471–20477).
- `H_t` payload: previous process families, cumulative heating time, last known moisture state (L18001–18002, L19998–20011).
- Per-view state confidence q_t (L20388–20395).
- `state_observed` vs `state_inferred` + `observation_quality` (§216.4 L22847–22863).
- Order-effect evidence flags (non-commutativity, L20338).
- Time-additivity validity flag per process/target (semigroup test eligibility, L20549).
