# READER ssot_l15b — SSOT v15 Level 15 §§213–216 (L20585–23052)

Reader: ssot_l15b · Date 2026-10-22 · Source: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (SSOT), index `docs/SSOT_INDEX.md`.
Scope I read in full: §213 (L20585–21233), §214 (L21234–21906), §215 (L21907–22730), §216 (L22731–23052). For cross-references I also read: §209.17 D0–D11 ladder (L18543–18610), §217.1 v12 change register (L23055–23082), §228.1 items 13–29 (≈L24860–24876), §226.5–226.8 (L24541–24576), §229.5 (L25021–25034). Repo spot-checks (read-only): `reports/h_state/transition_bootstrap_v0_contract.md`, `docs/simulator_data_contract.md`, `registry/ssot15_state_experiment_map.csv`, `ledgers/data/{EVD,COND}.jsonl` (stdlib counts), `DECISIONS.md`, `WORKLOG.md` (grep only), `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (Master Plan v4.0, grep + B13 L472–483, H1/H2 L540–575, W6 L1689–1715, AZ6 L4696–4721).

The 36-step plan ("Master Execution Plan v1") is NOT present. All step mappings in §8 are my reconstruction from SSOT text + brief §9 titles + repo artifacts; none is quoted from missing step cards.

---

## 1. Definitions, entities and data contracts

### 1.1 Core objects (§213)
- **Molecular graph vs reaction network** (L20587–20615): `G_m=(V_atoms,E_bonds)` describes one molecule; `G_R=(V_species,E_reaction)` describes species transformation; boxed law "molecular graph ≠ reaction network" (L20608–20612). Molecular embeddings may be *node features* of the reaction network (L20615).
- **Reaction hypergraph / bipartite graph** (L20617–20631): A+B→C+D is not a pairwise edge; use hyperedges or explicit reaction nodes.
- **Stoichiometric dynamics** (L20632–20645): boxed `dc/dt = N v` (N stoichiometric matrix, v rate vector). "Topology says who transforms; rate laws say how fast" (L20645).
- **Dynamic state vs dynamic topology** (L20647–20665): boxed preference "fixed plausible topology + dynamic concentrations/rates" before nodes/edges appear/disappear.
- **Rate gating before topology mutation** (L20667–20677): inactive pathway via `v_r≈0` preferred over creating/deleting edges on weak evidence.
- **Known pathway model** (L20679–20689): `A→k1 B→k2 C`; fit rates/condition dependence, do not rediscover topology. "Focused known systems are preferred for a semester project" (L20689).
- **Edge semantics rule** (L20775–20784): an edge must mean one of {known reaction; transport/exchange; equilibrium/interaction; validated statistical interaction explicitly labelled statistical}. Co-occurrence all-pairs graphs are not mechanistic.
- **Statistical vs reaction graph** (L20786–20802): attention weight `w_ij` = predictive interaction ≠ `i+j→k`; "Never rename learned graph edges as chemical reactions without validation" (L20802).
- **Species node features** (L20804–20819): `h_i(t)=[z_{m_i}, log c_i(t), mask_i, phase_i, evidence_i]` — identity static, concentration/evidence evolve.
- **Reaction-edge features** (L20821–20838): reaction type; reactants/products; rate family; A; Ea; order; condition scope; parameter uncertainty; source; evidence tier. "Unknown fields remain masked" (L20838).
- **Unknown sink/source channel** (L20926–20936): `A→U`, U labelled unresolved/unmeasured, not a discovered molecule.
- **Hidden species** (L20938–20946): allowed only if chemically plausible AND needed by residual structure AND supported by enough measurements.
- **Open-system conservation** (L20972–20986): `l^T c(t)=const` for a defined closed network; cooking usually open → `dc/dt = N v + u_in − u_out`.
- **Compartment models** (L20988–20994): food/water (boiling, leaching), surface/core (frying).
- **Spatial/PDE reference** (L20996–21004): e.g. `∂T/∂t=α∇²T`; "focused engineering simulators, not a universal project requirement".
- **Recipe graph ↔ reaction graph boundary** (L21012–21022): `G_recipe,t → G_reaction,t` automatic mapping "beyond current broad data; keep modular".
- **Local process modules** (L21024–21036): boiling-retention; frying/acrylamide; roasting-browning; fermentation; mechanical/merge — each with own evidence/state variables.
- **FlavorTwin bridge** (L21046–21060): `c_t→c_{t+1}` then `z_{i,t+1}=Agg(z_m,c_{m,t+1})`; FlavorTwin consumes processed chemistry "when evidence supports it".
- **Canonical dynamic reaction object** (L21215–21230): boxed `G_t=(V,E,c_t,q)` — V species, E candidate/known reactions, c_t state, q evidence/parameter metadata; conditions θ_t drive rates.

### 1.2 Core objects (§214)
- **Forward**: `S_{t+1}=T_φ(S_t,P,θ)` (L21240–21242). **Inverse**: boxed `(P*,θ*)=argmin d(T_φ(S_t,P,θ),S*)` s.t. feasibility/evidence constraints (L21244–21255); inverse is many-to-one, unique `T^{-1}` not assumed (L21257).
- **Partial target mask**: `L_target=Σ_j m_j d_j(Ŝ_j,S*_j)`; unspecified dims not forced (L21259–21269).
- **Hard constraints** (L21294–21299): equipment unavailable; unsafe/impossible condition; process incompatible with state; bounded operating range. **Soft** (L21301–21306): preferred time; energy; culinary style; approximate target. "Document which constraints are hard" (L21308).
- **Feasible process set** boxed `P_feasible(S_t,C)` defined *before* optimisation from current state, process ontology, prerequisites, tools, allowed condition ranges, evidence support (L21310–21325).
- **Evidence-distance constraint** `d_evidence(x) ≤ τ` or penalty (L21403–21411) — "ties optimization to the curated evidence ledger".
- **Conservative feasible region** `C_safe={x : d_evidence(x)<τ, UQ(x)<u_max, constraints(x)=true}`; default system optimises only inside it (L21628–21636).
- **Evidence-class labels for recommendations** (L21601–21613): `OBSERVED | INTERPOLATED | MODEL-ESTIMATED | EXTRAPOLATED | UNSUPPORTED`; "must be visible in downstream reasoning".
- **FlavorTwin inverse problem** boxed `target→ingredients→processes→conditions` or joint `(I*,P*,θ*)=argmin D(z_target,z_{I,P,θ})` (L21519–21541); multi-axis fitness `[D_chemical,D_sensory,D_process,D_culinary,D_constraint,D_evidence,D_OOD]`, not collapsed unless a downstream application supplies preferences (L21543–21559).
- **CulinaryState-RAG next-action**: `P_t*=argmax U(T(S_t,P,θ),G)`; sparse-data default pipeline `retrieve evidence → filter feasible actions → simulate only supported candidates → expose trade-offs → abstain if unsupported` (L21580–21599).
- **State ≠ quality**: boxed "food state ≠ human liking", "chemical similarity ≠ palatability" (L21745–21759).
- **Shared core** (L21841–21855): state encoder; transition model; evidence ledger; uncertainty; OOD; process ontology; recipe-state graph. Evaluation remains task-specific (L21857–21867).

### 1.3 Claim families and data regimes (§215)
- **Claims A–F** (L21909–21947): A coarse process effect `(i,P)→{↓,≈,↑}`; B quantitative endpoint `(S0,P,θ)→S_final`; C kinetic law `dS/dt=f(S,θ)`; D multi-step simulator `S0→…→ST`; E reaction network `dc/dt=Nv`; F inverse process design `S*→(P*,θ*)`. "Each claim has different data requirements and evaluation" (L21947).
- **Data regimes** (L21949–21996): D-A aggregated process effects (retention; supports direction/retention/endpoint/cold-pair; NOT detailed kinetics, L21965); D-B curated raw vs processed (log-fold change, endpoint transition, process-conditioned molecular state, platform/domain analysis); D-C focused kinetic studies (rate, order, Arrhenius, thermal dose, simulator/hybrid, condition-OOD); D-D recipe procedure/state corpora (procedure graph, merge/split, qualitative state tracking, order reasoning; "Does not directly support quantitative chemistry", L21996).
- **Shared schema, separate strata** (L21998–22009): common provenance/state/process schema preserving target type; fidelity; study; platform; matched status; trajectory availability.
- **Activation rule** boxed "dataset supervision ⇒ eligible model family" (L22017–22025); D0–D11 from §209.17 (L22013).
- **Final broad object** boxed `S_{t+1}=T_φ(S_t,P_t,θ_t,H_t; ℰ)` with ℰ = evidence/provenance regime (L22685–22703). Permanent sentence: "**A transition model is only as credible as the evidence regime under which its transition was observed.**" (L22727).

### 1.4 Level-15 data contracts (§216) — field level
**216.1 Canonical transition-event table** (L22733–22798). Minimum fields, grouped as in source:
- identity: `transition_id, ingredient_id, state_before_id, state_after_id, process_family, process_leaf`
- T/t with intervals and type: `T_value, T_lo, T_hi, T_type, t_value, t_lo, t_hi, t_type`
- context: `medium, tool, geometry, moisture_before, moisture_after, water_activity, pH, pressure, oxygen, mixing`
- target: `target_family, target_variable, target_compound, value_before, value_after, delta_value, direction_label, ordinal_band, unit`
- censoring: `censor_flag, LOD`
- provenance: `study_id, source_id, doi_or_citation, platform, matrix_description`
- evidence: `evidence_tier, verification_status, extraction_method, explicit_or_inferred`
- dynamics: `trajectory_id, timepoint, sequence_id, event_index`
- versioning: `split_id, dataset_version`
- Rule: "Not every row has every field. Missingness remains explicit." (L22798)
- Note: `T_type`/`t_type` semantics (e.g. setpoint vs core vs surface; nominal vs measured) are NOT defined in §216.1 — UNDERSPECIFIED here (may be defined in L14/§209 or COND registries; the repo has `registry/measurement_location_registry_v1.csv` and `heat_transfer_mode_registry_v1.csv` which may serve; UNVERIFIED mapping).

**216.2 Kinetic-experiment table** (L22800–22823), one row per experiment/series: `kinetic_experiment_id, target, food_matrix, process, initial_conditions, temperature_schedule, timepoints, observations, candidate_model_family, fitted_parameters, parameter_units, parameter_uncertainty, fit_diagnostics, identifiability_status, source, evidence_tier`. "Raw timepoint measurements remain available separately" (L22823).

**216.3 Reaction-ledger table** (L22825–22845): `reaction_id, species_reactants, species_products, stoichiometry, reaction_family, rate_law, A, Ea, order, condition_scope, matrix_scope, parameter_uncertainty, source, evidence_tier, verified`. "Unknown pathways remain absent/UNKNOWN rather than invented." Compare the earlier §213.42 reaction evidence ledger (L21171–21187): `reaction_id, reactants, products, reaction type, conditions, parameter values/ranges, matrix/system, source, evidence tier, measured / inferred, uncertainty` — §213.42 has `measured/inferred` which §216.3 lacks; §216.3 has `stoichiometry, rate_law, A, Ea, order, verified` which §213.42 lacks (see §9 contradictions). Master Plan v4.0 RXN- (H2 item 11, L570; W6 L1689–1708) adds InChIKeys, marker compounds, reaction SMARTS/SMILES (RDKit), confidence, and a qualitative transformation vocabulary (FORMED, DEGRADED, RETAINED, VOLATILIZED, LEACHED, OXIDIZED, REDUCED, DENATURED/AGGREGATED, GELATINIZED, ISOMERIZED, FERMENTED/CONSUMED, UNKNOWN_TRANSFORMATION).

**216.4 Rollout/sequence table** (L22847–22862): `sequence_id, event_index, entity_ids_in, entity_ids_out, process, conditions, state_observed, state_inferred, observation_quality, source`. Supports procedural and short-horizon dynamics.

**216.5 Inverse-design trial table** (L22864–22883): `trial_id, initial_state, target_state, candidate_process, candidate_conditions, constraints, optimizer, forward_model_version, predicted_state, prediction_interval, evidence_distance, OOD_flag, feasible_flag, heldout_or_real_outcome, target_error, notes`. Overlaps §214.44 inverse-design provenance (L21761–21778) which additionally lists `nearest supporting studies` and `optimization algorithm/version` (216.5 has `optimizer` only, no nearest-studies field).

**216.6 Data/version registry** (L22885–22896): every representation/model depends on dataset version; ontology version; unit normalization; split version; evidence-tier policy; target definition — "part of the model artifact".

**216.12 Minimum implementation package** (L22988–23032): `data/{transition_schema, evidence_registry, split_registry}`, `baselines/{persistence, process_mean, nearest_evidence, ridge, lightgbm_or_xgboost, tabpfn_if_applicable}`, `kinetics/{zero_order, first_order, nth_order, arrhenius, fit_and_diagnostics}`, `models/{residual_mlp, film_transition}`, `evaluation/{pair_holdout, ingredient_disjoint, process_disjoint, condition_ood, study_disjoint, calibration, uncertainty, ablation}`, `reports/{dataset_card, transition_benchmark, kinetic_fit_report, decision_record}`.

**216.13 Decision record** (L23034–23049), 10 items: supportable targets; strongest simple baseline; whether conditions add value; whether physics features add value; whether neural transitions add value; whether kinetics identifiable; whether hybrid adds OOD value; whether short rollout justified; whether inverse design allowed; what remains UNKNOWN/DEFERRED. "This decision record, not architecture preference, controls the next implementation step" (L23049).

### 1.5 Repo reality vs these contracts (read-only check, 2026-10-22)
- `ledgers/data/` contains no RXN, KINETIC, SEQ/rollout, SPLIT, inverse-trial or transition-event table. DECISIONS.md L136 records "EVT/STATE/ENTITY/INST/QNT/POR/SPLIT/RXN/KINETIC/SIM not created (BLOCKED_FUTURE_STEP)".
- EVD (latest version per id): 18,156 ids, 17,978 ACTIVE. Of ACTIVE: `process.process_id` set 17,821; `matrix.ingredient_id` set 11,569; `matrix.initial_state` set 12,442; `censored` true 5,894; `study_id_status=PRESENT` 3,870 (= Phenol-Explorer); verification UNVERIFIED 14,108 / AI_PRECHECKED 3,870 / human-verified 0. EVD fields: `applicability, censored, design, independence_group, matrix{food_group,form,ingredient_id,initial_state,raw_name}, measurement_method_id, origin_type, process{condition_id,medium,modifiers,process_id,raw_name,steps}, study_ids, target{basis,raw_name,state_variable_id}, tier, verification …`. There is NO `value_before/value_after/delta/direction_label/ordinal_band/LOD/platform/trajectory_id/timepoint/sequence_id/split_id/dataset_version/explicit_or_inferred` at top level (value fields may be nested — I did not print value sub-objects; partially UNVERIFIED).
- COND (4,746 rows) completeness_mask: temperature MEASURED 2,445 / RANGE 276 / UNKNOWN 2,025; duration MEASURED 2,580 / RANGE 28 / UNKNOWN 2,138; **moisture UNKNOWN 4,746/4,746; pH UNKNOWN 4,746/4,746**; pressure MEASURED 129 / N_A 270; power MEASURED 60. No oxygen, aw, geometry, mixing axis in the mask.
- `reports/h_state/transition_bootstrap_v0_contract.md` (MP-1, "defined, NOT run") = a reduced D-A instance of §216.1 (retention + yield only; B-0..B-5; splits S-1..S-7; censor-aware MAE; pre-registered success). Its B-ladder differs from §209.17 D-ladder labels (see §9).
- `docs/simulator_data_contract.md` (S116) source_class enum {STRUCTURAL_RECIPE, COMPOSITION, MEASURED_TRANSITION, COMPILED_RETENTION, KINETIC, MOLECULAR_PRIOR, SENSORY_PRIOR, MODEL_GENERATED, SYNTHETIC} + rule that STRUCTURAL_RECIPE cannot carry magnitude — consistent with §215.2 D-D "does not directly support quantitative chemistry" (L21996).

---

## 2. Models and baseline ladders (simple → strong → advanced)

### 2.1 Canonical transition ladder D0–D11 (§209.17, L18543–18610; invoked by §215.4 L22013)
D0 persistence → D1 global mean-delta → D2 process-conditioned mean-delta → D3 hierarchical shrinkage/partial pooling (food class, process family, compound class, study) → D4 nearest-evidence retrieval → D5 GBDT (LightGBM/XGBoost) → D6 TabPFN/small-data tabular FM "where sample size/task shape are compatible" → D7 evidence-aware low-rank/factorization completion (biased MF, BPMF/Macau-like, FM, coupled matrix/tensor) → D8 classical kinetics (zero/first/nth, Arrhenius, Weibull, formation/degradation, focused compartment) → D9 hybrid mechanistic + learned residual → D10 neural multi-output/latent-state (residual MLP, FiLM, history-aware, state-space) "not allowed to skip D0–D7" → D11 UDE/neural ODE/reaction-network "focused time-resolved systems only".

### 2.2 Reaction-model ladder (§213, implicit; data-to-model table §213.33 L21072–21082)
| data | model |
|---|---|
| process label + endpoint | tabular/endpoint transition |
| T,t + endpoint | physics features / simple kinetics |
| multiple times | rate model |
| multiple times × temperatures | Arrhenius |
| multiple species | reaction network |
| dense multi-species trajectories | reaction-network learning / CRNN |
| spatial fields | compartment / PDE hybrid |

Advanced options, each gated: known-topology rate fitting (L20679) → CRNN-style hard-coded mass-action + Arrhenius with learned parameters `v_r=k_r Π c_i^{α_ir}`, `k_r(T)=A_r e^{−Ea,r/RT}` (L20727–20745, "Requires time-resolved concentration data") → sparse system identification SINDy-style `dc/dt=Θ(c)Ξ` (L20711–20725, "focused stretch requiring dense low-noise trajectories and adequate condition excitation") → gated topology selection `v_r=g_r ṽ_r` with sparsity (L20948–20958, stretch, needs held-out interventions/trajectories). v13 patch (L21195–21213): SINDy/CRNN "belongs to simulator recovery studies or unusually dense D-C data, not broad endpoint data".

### 2.3 Hybrid ladder (§213.15–213.19, 213.43A)
- Generic GNN `h'=GNN(G,h,θ)` is statistical (L20840–20848); kinetic graph enforces balance (L20850–20856); hybrid rate `v_r=v_r^mech+Δv_r^NN` (L20858–20862).
- **Endpoint residual** `S_final=S_mech+r_NN` works with endpoint data; **rate residual** `dS/dt=f_mech+f_NN` requires trajectories; "Default broad program: endpoint residual first" (L20864–20882).
- UDE `dS/dt=f_known(S,θ)+f_unknown,φ(S,θ)` (L20884–20892).
- Multiplicative positive correction `r=r_mech(θ)·exp(g_ψ(x))` (L21203–21207) + residual-off ablation + report whether correction overwhelms mechanistic term (L21210).
- Mandatory three-way benchmark: mechanistic only / pure ML / hybrid (L20908–20912); compare `‖f_NN‖` vs `‖f_known‖` (L20894–20906). Regularisation `L=L_data+λ‖f_NN‖²` "only if validated; do not force the residual small merely to preserve a preferred mechanism story" (L20916–20924).
- Process-family experts: hard route by process family first; soft MoE optional later (L21038–21044).

### 2.4 Focused experiment comparison set (§213.36, L21106–21124)
focused food/system + T(t), moisture(t), target compound(s); compare simple regression; classical kinetics; strong tree/ML; mechanistic + neural residual; reaction-aware model only if warranted. **Headline split: condition-OOD.**

### 2.5 Inverse-design ladder I0–I6 (§214.54, L21887–21903)
I0 finite counterfactual comparison → I1 grid/random feasible search → I2 uncertainty-aware continuous search → I3 Bayesian/evolutionary mixed search → I4 short sequence beam search → I5 receding-horizon planning → I6 long-horizon MCTS/optimal control. "Higher rungs require stronger forward-model credibility" (L21903).
- Mandatory baselines (§215.20, L22192–22200): nearest known process/evidence; random feasible search; grid for low-dim. §214.10 grid = "best first baseline for low-dimensional supported ranges" (L21365); §214.11 random feasible = "Mandatory baseline for higher-dimensional/mixed spaces… must beat it under the same evaluation budget" (L21371–21375).
- Objective forms: `J=μ_L+λσ_L` (min loss), `U_safe=μ_U−βσ_U` (L21413–21427); LCB `score_safe=μ−κσ` + hard evidence-distance constraint (L21877–21881); ensemble disagreement penalty (L21638–21642); robust perturbation `T=180±δ` (L21429–21441).
- Candidate algorithms (v13 patch L21869–21885): grid/random; Bayesian multi-objective or NSGA-II-like Pareto; LCB; simulator-first optimisation for focused acrylamide/browning trade-offs before wet lab; return several diverse Pareto candidates. "These algorithm names are implementation candidates, not frozen winners" (L21885).
- Gradient search "fast, but highly vulnerable to model exploitation/OOD" (L21377–21385). MCTS "Deferred until the forward simulator is demonstrably reliable" (L21463–21467). DP/optimal control = "long-term process-engineering formulations" (L21469–21489). Temperature-schedule `T(t)` optimisation "meaningful only with validated kinetics" (L21491–21501).
- Short-horizon first: K=1 then perhaps K=2; "Do not begin with whole-recipe autonomous optimization" (L21708–21718). Receding horizon / MPC (L21720–21732).

### 2.6 Validation ladder ID0–ID5 (§214.49, L21815–21827)
ID0 recover known process/conditions; ID1 interpolation target; ID2 novel ingredient×process combination; ID3 condition extrapolation; ID4 multi-step sequence; ID5 real experimental validation. (Headings only; no per-rung pass criteria given — see §9.)

### 2.7 Ablation families (§215.56–215.58)
- Endpoint A0–A8 (L22466–22484): A0 ingredient only; A1 process only; A2 conditions only; A3 ingredient+process; A4 +conditions; A5 +physics features; A6 +initial state; A7 +history; A8 +molecule representation.
- Kinetic K0–K6 (L22486–22500): K0 mean/null; K1 time only; K2 empirical (T,t); K3 simple kinetic law; K4 Arrhenius; K5 +moisture/pH/process gating; K6 hybrid residual.
- Rollout (L22502–22511): teacher forcing; free rollout; noisy-state training; history-aware; retrieval correction; observation correction.
- Topology (L21138–21147): prior/known topology; randomized topology; fully connected; non-graph set/tabular. Structural randomisation preserving graph statistics (L21149–21153). Reaction-importance `v_r=0` = model dependence, not causal (L21155–21165).

### 2.8 Minimum code package baselines (§216.12, L22997–23015)
persistence, process_mean, nearest_evidence, ridge, lightgbm_or_xgboost, tabpfn_if_applicable; kinetics zero/first/nth/Arrhenius + diagnostics; models residual_mlp, film_transition. (Note: no D3 shrinkage and no D7 completion in the minimum package — see §9.)

### 2.9 Compute (§215.64, L22569–22593)
CPU: curation, kinetic fitting, trees/tabular, bootstrap, retrieval, grid/random inverse search. Modest GPU: MLP/FiLM, DeepSets, GRU, small molecular encoders. Larger "only if earned": large graph/sequence dynamics, large reaction learning, large multiview world models. "The main Level-15 bottleneck is data, not GPU access." (L22593) → consistent with ctx (no GPU use; 128-core CPU server suffices for D0–D9 and I0–I3).

---

## 3. Experiments / hypotheses / RQs

No RQ-IDs (RQ16/RQ13E style) are defined inside §§213–216. Experiments are implicit; I enumerate them with anchors (IDs below are my own labels, `L15b-x`, NOT SSOT IDs):
- L15b-1 **Pre-model data audit** (§215.26, L22251–22269): counts of unique ingredients; processes/families; ingredient×process pairs; rows with T; rows with t; rows with both; matched before/after pairs; time-series experiments; temperatures per kinetic series; jointly measured species; studies/platforms; complete process sequences; intermediate-state labels. "This audit selects the reachable model rung."
- L15b-2 **Data-support map per target** (§215.27, L22271–22285): endpoint / time series / temperature series / multi-species / sequence-intermediate / study count / platform count. "prevents architecture-first decisions".
- L15b-3 **Endpoint baseline + sparsity bakeoff** (15-B, L22601–22603): D0–D7 where eligible; masked-real-cell, cold food/process/compound/pair, study-disjoint, OOD.
- L15b-4 **Process-signal test** (G15-3): process-conditioned vs food-identity-only on process-disjoint split with CI/effect.
- L15b-5 **Focused kinetics** (15-C, L22605–22607): one or two targets; reaction-order/Arrhenius/uncertainty; model-family selection by held-out, AICc/BIC, residuals, identifiability, mechanistic scope, "not by training R² alone" (L22130–22140). SSOT §226.5 (L24541–24547) names "focused acrylamide/Maillard anchor simulators"; registry SX-06-04 lists candidate focused systems acrylamide/potato, Maillard glucose/glycine, vitamin C, anthocyanin, chlorophyll — all MISSING in repo.
- L15b-6 **Mechanistic vs ML vs hybrid** (15-D; §213.36; §215.30 "one of the highest-value advanced experiments", L22325) under condition-OOD; K0–K6 ablation; residual-off ablation; `‖f_NN‖/‖f_known‖` report. Related §226.6 M4 (L24549–24558): real-only mechanics / pure ML / hybrid / simulator-pretrained+real-finetuned / synthetic ratio sweep / held-out temperature. Focused hypothesis §229.5 (L25021–25033): "mechanistic simulator/kinetics + real fitting + hybrid residual or synthetic-prior pretraining may improve held-out-condition prediction in one well-characterized system" (not frozen).
- L15b-7 **Reaction-network experiment** (stretch §215.32, L22333–22342): only with multiple species, time series, plausible pathways, sufficient condition variation; compare independent/tabular alternatives and randomized topology; topology ablation §213.38; leave-one-reaction (G15-RXN item 4).
- L15b-8 **Short rollout** (15-E; §215.31): 2–3 steps, only with measured intermediates; metrics E(1..K), D(k)=E(k)/(E(1)+ε) (L22158–22164), trust horizon; rollout ablations §215.58.
- L15b-9 **Counterfactual comparison** I0 (§214.7, L21327–21339) — finite set A vs B; causal language only with controlled/mechanistic justification (L21341–21351); counterfactual sensitivity = model sensitivity (L22230–22234).
- L15b-10 **Conservative inverse design** (15-F; §215.33): start with (T,t); compare nearest evidence, random/grid, conservative model-based search; equal evaluation budget (L21786–21797); regret only in a simulator with known optimum (L21803–21813); model-exploitation audit OOD(x*), UQ(x*) vs ordinary candidates (L22202–22216). Related §226.8 M6 (L24569–24575).
- L15b-11 **Null-transition test** (§215.24, L22236–22240): persistence as real benchmark; overreactive models penalised.
- L15b-12 **Ceiling / error decomposition** (§215.54–55, L22450–22464): measurement + state uncertainty + model + domain shift; replicate noise floor; report error relative to empirical variability.
- L15b-13 **Mechanistic consistency** (§215.22, L22218–22228): non-negativity; balance; direction under controlled subset; moisture gating; prerequisite conditions; "only impose rules scientifically appropriate to that system".
- L15b-14 **RAG evaluation bridge** (§215.59, L22513–22523): evidence retrieval quality; citation/provenance correctness; state reconstruction; action feasibility; abstention; target granularity; explicit model-fallback labelling. Decision hierarchy §215.60 (L22525–22539): direct evidence → report; else close calibrated interpolation → estimate+interval+model flag; else broader qualitative evidence → broader statement; else abstain.
- L15b-15 **FlavorTwin evaluation bridge** (§215.61, L22541–22550): static retrieval; process-conditioned retrieval; inverse-process recovery; constraint satisfaction; OOD control; sensory validation only where human/sensory evidence exists; wording boundary §215.62 (L22552–22554).

Paper framing (§215.66, L22621–22637): primary "Evidence-aware process-state transition modeling for computational gastronomy under sparse heterogeneous supervision" with 9 possible contributions (dataset; FoodProc-style cold-start/study benchmark; tabular + low-rank completion; MNAR/propensity; physics/kinetic features; conformal abstention; focused mech-vs-ML-vs-hybrid; active acquisition; RAG integration). Secondary (§215.67, L22639–22645): "Hybrid mechanistic-neural modeling of a focused food transformation under condition shift".

Positive-result criterion (§215.68, L22647–22657): gain persists under cold-pair; source/study; condition-OOD; calibration; physical consistency. "Random-split improvement alone is insufficient."
Valuable negative result (§215.69, L22659–22669): LightGBM beats FiLM/GRU; simple kinetics beats neural ODE; nearest evidence matches optimisation → simpler result retained.

Existing empirical evidence in repo relevant to these hypotheses: WORKLOG L117 (DEL-2, USDA): random D5 0.025 vs D0 0.121; matrix_disjoint D0 0.059 ≈ D4 0.057 (CIs overlap) — cold gains vanish; process_disjoint D0 0.073 vs D5 0.067; conformal-90 coverage 0.72–0.87 on cold splits; study-disjoint impossible for USDA. WORKLOG L276: EXP-000001..4 — USDA supported on random only; PE not supported (study_disjoint best = global mean; D5 worse than persistence); Bognár supported but caveated (templated factors; process split degenerate). These are prior negative results that §215.69/§215.70 require be retained.

---

## 4. Gates, promotion and stop rules (exact quotes)

### 4.1 v13 revised G15 gate table (§215.38, L22376–22396) — "These supersede the v12 G15-1…G15-I naming" (L22378)
- **G15-1 Data audit** (L22382): "Every quantitative row has source/study, evidence tier, units/target definition, yield/normalization status, and censoring/missingness status."
- **G15-2 Baselines** (L22383): "Canonical D0–D6 are reported on all eligible headline splits before D7+ claims."
- **G15-3 Process signal** (L22384): "Process-conditioned modeling adds value over food-identity-only on a process-disjoint or equivalent controlled split; report CI/effect, not just point gain."
- **G15-4 Kinetic fit** (L22385): "At least one focused D-C dataset supports an identifiable/useful kinetic fit with profile/bootstrap/posterior uncertainty."
- **G15-5 Condition-OOD** (L22386): "Kinetic/hybrid/physics model adds value over the best non-kinetic tabular baseline on held-out temperature/condition."
- **G15-6 Calibration** (L22387): "Real, study-disjoint calibration is reported; intervals/sets achieve acceptable task-specific coverage/width."
- **G15-7 Abstention** (L22388): "Risk–coverage/selective prediction improves over always-answering and abstention rules are defined on REAL calibration data."
- **G15-8 Consistency** (L22389): "Relevant non-negativity, semigroup/order/balance/constraint diagnostics are reported on scientifically valid subsets."
- **G15-9 Completion** (L22390): "Evidence-aware D7 completion beats D5/D6 on masked-real-cell and cold food/process/compound/pair tests, or is rejected."
- **G15-10 Synthetic/imputed utility** (L22391): "Synthetic/imputed training rows improve REAL-only study-disjoint performance in a ratio sweep without unacceptable calibration damage; no synthetic/imputed target enters final test/calibration."
- **G15-11 Rollout** (L22392): "A trust horizon is empirically established on D-C/D-D where true intermediate states exist; no rollout claim otherwise."
- **G15-12 Inverse design** (L22393): "At least one supported inverse-design case passes an ID-level benchmark beyond nearest-evidence/random/grid and remains inside the safe support region."
- **G15-R Reproducibility** (L22394): "Seeds, versions, hashes/snapshots, splits and parameter settings permit rerun within declared tolerance."
- **G15-H Human verification** (L22395): "Every LLM-extracted row used in held-out test/calibration is human verified against the cited source span/table."
- **G15-I Integration** (L22396): "CulinaryState-RAG / FlavorTwin end-to-end evaluation logs evidence class, uncertainty, abstention and provenance."

### 4.2 Model-specific sub-gates (§215.39, L22398–22426)
- **G15-RXN** (L22402–22410): "Promote a reaction graph only if: 1. species/reactions have evidence; 2. dynamics data exist; 3. topology adds value beyond set/tabular baselines; 4. randomized-topology and leave-one-reaction controls support the graph claim; 5. learned edges are not mislabeled as chemistry."
- **G15-HYB** (L22412–22414): "Promote a mechanistic-neural hybrid only if it adds meaningful held-out/OOD/calibration value beyond both the mechanistic model and pure ML, or provides a separately demonstrated physical-consistency advantage."
- **G15-INV** (L22416–22426): boxed "inverse-design ceiling ≤ forward-model credibility"; "Inverse search is blocked when forward transition, uncertainty, support/OOD or calibration gates fail."
- Count check: 12 + R/H/I + RXN/HYB/INV = 18, matching WORKLOG L23 "18/18 G15".

### 4.3 Other promotion/precondition rules in §§213–216 (non-ID'd)
- Reaction graph justification (L21084–21095) requires enough identified species, plausible pathways, concentrations, time points, conditions, pathway literature; else set/tabular. Decorative-graph rule (L21097–21104): not justified when arbitrary-similarity edges, single final label, no dynamic concentrations, or no meaningful ablation.
- §213.38 L21147: "If topology does not add value, do not claim graph benefit."
- §213.43A L21200–21201: graph must beat **both** a non-graph set model and a randomized-topology control.
- Hidden species admission (L20942–20946) — three-way AND.
- §214.47 L21801: "A sophisticated optimizer that barely beats random/grid feasible search has not earned complexity." (no numeric margin)
- §214.35 boxed "optimization precision ≤ forward-model precision" (L21652–21658), with example ±0.15 vs 0.98/0.95 (L21650).
- §214.45 optimisation leakage: separate transition-model dev, optimiser tuning and final held-out evaluation; "Do not repeatedly optimize against the final test outcomes" (L21780–21784).
- §215.31: rollout "only where measured intermediate states exist" (L22329). §215.33 inverse start with (T,t) (L22346–22352). 15-F "only after forward gates" (L22619).
- §216.10 L22976–22978: upstream L12/13 embeddings enter only as "additional features/ablations after their own gates pass"; "Level 15 must not depend on an unvalidated upstream learned embedding to function at all."

### 4.4 Stop / escalation rule (§215.70, L22671–22683) — quote
"Stop increasing model complexity when: cold-pair collapses; study shift dominates; conditions add no value; labels are too noisy; kinetic parameters are unidentifiable; uncertainty is badly calibrated; retrieval matches advanced models. Then invest in better evidence/data."

### 4.5 Defer list (§215.34–215.37, L22356–22374) and §216.11 (L22980–22986)
Defer: general neural ODE without dense trajectories; universal reaction discovery from sparse endpoints; full-recipe chemical world model ("Procedure graph is feasible. Universal quantitative chemistry simulation across complete recipes is not currently supported", L22366–22368); autonomous long-horizon recipe optimiser. Waits for richer L15 data: neural ODE/CDE; dynamic reaction-network learning; long chemistry rollout; topology discovery; unrestricted inverse process planning.

### 4.6 Thresholds — none numeric
No gate in §§213–216 gives a numeric threshold (coverage targets, effect sizes, τ, u_max, κ, β, λ, trust-horizon tolerance, "declared tolerance", "acceptable task-specific coverage/width" are all unspecified). Only quantitative illustration is the ±0.15 precision example (L21650) and `T=180±δ` (L21435). → these must be pre-registered in step contracts before runs (no post-hoc weakening law).

### 4.7 Current repo gate status (registry/ssot15_state_experiment_map.csv)
G15-1 PARTIAL, G15-2 PARTIAL, G15-3 PARTIAL, G15-4 MISSING, G15-5 MISSING (rows seen; remaining G15 rows not printed — UNVERIFIED). SX-13-01 PARTIAL, SX-13-02/05/06/07 MISSING, SX-13-03/04 PARTIAL. G15-H is structurally unmet today: 0 human-verified EVD rows (EVD ACTIVE all UNVERIFIED/AI_PRECHECKED). G15-1 in strict reading is unmet: study_id PRESENT only on 3,870/17,978 ACTIVE rows (USDA/Bognár rows have `study_id_status=NOT_IDENTIFIABLE`; independence_group exists instead).

---

## 5. Data requirements and named sources (licence notes)

§§213–216 name **no specific external dataset or paper**. Requirements are by regime:
- D-A (aggregated retention: USDA retention factors, Bognár, Phenol-Explorer in repo) → Claims A/B only; "Does not support detailed kinetics" (L21965). Repo has these 3 (E3, unverified). Licence: USDA public domain (UNVERIFIED here); Bognár and Phenol-Explorer terms not checked by me — defer to licence reader.
- D-B curated raw vs processed (volatiles/compound log-fold change, GC-MS/GC-IMS platforms §215.12 L22103–22111) → repo has none (registry SX-06-03 MISSING: "no volatile raw-vs-cooked rows").
- D-C focused kinetic series (multiple timepoints × ≥2 temperatures for Arrhenius, L21079; T(t), moisture(t) per §213.36 L21113) → repo has none (SX-06-04 MISSING; DECISIONS L119 S130 census: "structured open sources for mechanism/kinetic/physical time series not found (SOURCE_GAP for 13 of 16 priority-cell rows; literature route available)"). So D-C must come from literature extraction (Steps 09–13) with human verification (G15-H) — the true long pole for G15-4/5, HYB, RXN, INV.
- Multi-species time series (reaction networks, L21080–21081) — none in repo; even rarer in literature (e.g. Maillard model-system studies are the classic source; specific papers NOT named in SSOT — external research needed).
- D-D recipe procedure/state corpora with measured intermediates — repo has recipe text (612,782 base recipes, S133) but D-D intermediate *state labels* do not exist yet (Gold state-trajectory pilot = Step 19). Note: recipe text supports procedural rollout only (simulator_data_contract: STRUCTURAL_RECIPE cannot carry magnitude).
- Sensory/preference data for any liking optimisation (§214.24 L21517, §214.43) — none; any "flavor" optimisation must stay chemical-target-only.
- Wet-lab: §214.36–214.38 real validation / active-learning loop "compelling future wet-lab direction" (L21686) — no lab resource documented in repo (UNVERIFIED); ID5 is therefore likely unreachable in plan horizon.
- §213.43A L21213: all literature claims motivating the v13 reaction choices "remain `[SOURCE-REPORTED]` until independently checked for publication" — i.e. SSOT itself flags its CRNN/SINDy/multiplicative-residual motivations as unverified.

Licence notes from ctx: BBC A1 RESTRICTED local-only; Food.com CC0 uploader-declared; CoSyLab ASSUMED/DERIVED_ONLY — relevant to D-D only; none of these provide D-C.

---

## 6. Dependencies on other levels/steps

From §216.7 execution DAG (L22898–22929), verbatim structure: Level-14 process/evidence table → Level-15 transition schema → D0–D4 endpoint baselines → cold-pair + study/OOD evaluation → calibration/abstention → {CulinaryState-RAG transition fallback; [focused time-series available?] kinetic fits → physics features → mechanistic vs ML vs hybrid; [measured intermediates available?] short rollout; [forward gates passed?] inverse search → FlavorTwin / action optimisation}.
- Note ordering inside the focused branch: kinetic fits **before** physics features (L22914–22918), whereas §215.71 practical order is "endpoint evidence → cold baselines → physics features → focused kinetics → hybrid → short rollout → inverse design" (L22707–22722), i.e. physics features **before** kinetics. Spine 31 (physics/condition features) before 32 (focused kinetics) follows §215.71. (Contradiction logged §9.)
- Upstream hard dependencies: Level 14 process/evidence table (§§197–205) and process ontology (process_family/process_leaf for §215.9 process-disjoint "hold out leaf process while retaining its parent family", L22079); evidence ledger with study ids (study-disjoint §215.11); COND normalisation (T/t intervals + type; moisture; pH; aw; pressure; oxygen) for condition-OOD (§215.10) and K5 gating; human verification (G15-H); split registry (§216.6); Level 13E/L12/L13 embeddings are OPTIONAL (§216.10).
- §215.63 shared core between "Project A/B" (CulinaryState-RAG / FlavorTwin) — RAG consumes calibrated transition fallback (§216.7 branch at calibration), FlavorTwin consumes inverse search only after forward gates.
- §§219–227 (L15 sparsity/MNAR/synthetic prior) is a hard co-dependency: G15-9/10 are defined there in substance (§226.4 M2 L24528–24539 "Pass target: G15-9 or reject the completion hypothesis"), and E7 synthetic prior (Step 28) feeds G15-10.
- §212 (rollout, L19857–20584) defines trust horizon, R0–R5 fidelity ladder, M0–M11 — prerequisite theory for Step 34; §212.52B trust-horizon operationalisation (L20551–20566) is referenced by G15-11 (not read in full by me).
- §210 kinetics (classical, Arrhenius, thermal dose) — prerequisite for D8/K-ladder (not in my range).

Dependency classes for spine:
- HARD: 15 (DATA-EVIDENCE v1 freeze) → 29; 07 conditions → 31/32; 08 lineage → study-disjoint everywhere; 09 verification machinery → G15-H; 12/13/14 kinetic literature → 32/33; 19/20 measured intermediates → 34; 24/25 registry/parameters → 26/32/33; 27 simulator validation → 28 and any simulator-first inverse design; 29–33 forward gates → any inverse design (G15-INV).
- SOFT/OPTIONAL: 35 representation embeddings → A8 ablation only (§216.10).
- PARALLEL (§216.9 "What can run now", L22955–22965): schema; retention/process transition baselines; study/cold splits; kinetic literature curation; simple kinetic fitting; evidence retrieval; uncertainty/abstention harness. Track L15-BROAD and L15-FOCUSED run in parallel sharing schema (L22931–22953).

---

## 7. Risks / failure modes

1. **Model exploitation** — "core Level-15 risk" (L21387–21393); optimisers find model errors; bound constraints insufficient (high-T long-t example, L21395–21401). Mitigation: multivariate evidence distance, C_safe, LCB, ensemble disagreement, exploitation audit.
2. **Decorative graphs** — all-pairs co-occurrence/similarity graphs passed off as chemistry (L20775–20784, L21097–21104); learned attention renamed as reactions (L20802).
3. **Topology non-identifiability** — different topologies fit similar trajectories; "Trajectory fit alone is insufficient for pathway discovery" (L20707–20709); hidden species non-identifiable (L20940).
4. **Hybrid becoming black-box** — "A technically hybrid model can become effectively black-box" (L20914); also the opposite: over-regularising residual to protect a preferred story (L20924).
5. **Causal over-claim** — counterfactual differences/sensitivity/reaction knock-out are model sensitivity not causal effect (L21349–21351, L21165, L22234).
6. **Preference/quality conflation** — optimising chemistry as if liking (L21503–21517, L21745–21759); "flavor similarity" wording without sensory evidence (L22554).
7. **Compounding horizon error** in multi-step optimisation (L21706).
8. **Optimisation leakage** against final test (L21780–21784).
9. **Precision illusion** — distinguishing candidates below forward-model precision (L21648–21658).
10. **Macro/micro domination** — common targets dominate rare compounds (L22053–22061).
11. **Platform domain shift** GC-MS vs GC-IMS (L22111).
12. **Matrix transfer failure** (L22113–22117) and ingredient-disjoint collapse to be stated explicitly (L22075).
13. **Noise ceiling** — high replicate variability caps achievable precision (L22460–22464); risk of over-interpreting gains below noise floor.
14. **Upstream embedding dependency** — L15 broken if it relies on unvalidated L12/13 embeddings (L22978).
15. **Data starvation for D-C** (repo: zero kinetic series; S130 SOURCE_GAP) → G15-4/5/HYB/RXN/INV/11 may all be unreachable; per §215.70 the correct response is evidence acquisition, not architecture.
16. **Strict G15-1 unmet** by aggregate DB rows lacking study ids (USDA/Bognár NOT_IDENTIFIABLE study) — need an explicit policy that `independence_group` substitutes for study_id for D-A database aggregates, or G15-1 can never pass.
17. **Repo evidence of cold-split collapse** (WORKLOG L117, L276) already triggers §215.70 "cold-pair collapses" for USDA/PE → escalation beyond D5 on those sources is currently unjustified.
18. **Moisture/pH 100% UNKNOWN in COND** → K5 gating, §213.36 moisture(t), §215.22 moisture gating, §215.10 moisture/pH OOD are impossible on current EVD.

---

## 8. MAPPING TO THE 36-STEP SPINE (reconstruction; step cards missing)

- **01 Freeze project authority** — must register that §215.38 v13 gate table supersedes v12 naming (L22378) and that §217.1 item 21 (v12 register, L23075) is historical; that §209.17 D0–D11 is canonical over Master Plan AZ6 ladder (L4696–4721 of plan) and over MP-1 B-labels. Output: authority note on L15 ladders.
- **02 Audit implementation state** — record: no RXN/KINETIC/SEQ/SPLIT/inverse tables (DECISIONS L136); DEL-2 `src/culinarystate/transition/{baselines,cross_source,dataset,evaluate,splits}.py` covers D0–D7 on D-A; G15 status per registry; cold-split negatives EXP-000001..4.
- **03 Freeze state semantics** — must fix `state_before_id/state_after_id` semantics (§216.1), species-node state `c_i(t)`, mask, phase (§213.13), and the open-system/compartment notion (food vs water vs surface/core, §213.25) as state locations. Also the "state ≠ quality" law (L21747–21757) and target masks for partial targets (§214.2).
- **04 Freeze evidence/provenance/similarity contracts** — must include: evidence_tier, verification_status, extraction_method, explicit_or_inferred (§216.1); evidence classes OBSERVED/INTERPOLATED/MODEL-ESTIMATED/EXTRAPOLATED/UNSUPPORTED (§214.30) as a contract enum; edge-semantics enum {known reaction, transport/exchange, equilibrium/interaction, statistical} (§213.11); "measured/inferred" flag for reaction parameters (§213.42); data/version registry fields (§216.6). Gate link: G15-1, G15-H.
- **05 Normalize EVD** — EVD must expose §216.1 target block (value_before/after, delta, direction_label, ordinal_band, unit, censor_flag, LOD), platform, matrix_description, and a rule for study_id vs independence_group (G15-1). Check whether value sub-objects already carry before/after (UNVERIFIED).
- **06 Freeze source acquisition manifest** — must tag each source with L15 regime D-A/D-B/D-C/D-D and capabilities: time series? temperature series? multi-species? intermediates? platform? (the §215.27 data-support map columns). S130 manifest already found D-C SOURCE_GAP.
- **07 Condition & measurement normalization** — must emit T_value/T_lo/T_hi/T_type and t_value/t_lo/t_hi/t_type, medium, tool, geometry, moisture_before/after, water_activity, pH, pressure, oxygen, mixing (§216.1); temperature_schedule T(t) (for §214.23, §216.2); platform (GC-MS/GC-IMS). Needed for condition-OOD (§215.10), K2/K4/K5 ablations, evidence distance d_evidence (§214.15) and C_safe. Current COND lacks oxygen/aw/geometry/mixing axes and has moisture/pH 100% UNKNOWN.
- **08 Scientific source lineage** — study_id, source_id, doi_or_citation, experimental campaign grouping (§215.11 "Keep each paper/experimental campaign grouped"); lineage for "nearest supporting studies" (§214.44); detection of the same measurement appearing in several sources (MP-1 leakage list). Gate: G15-1, G15-6 (study-disjoint calibration), study bootstrap (§215.53).
- **09 Evidence extraction & verification machinery** — must extract kinetic-series tables to §216.2 with raw timepoints kept separately (L22823), source span/table retained (G15-H L22395; §226.5 "source spans/tables retained"); flag LLM-extracted rows; human-verification queue for any row in test/calibration.
- **10 20-row mechanism pilot** — should include ≥ a few D-C kinetic rows (multi-time × multi-T) for the chosen focused target so the §216.2 contract is exercised early; test explicit_or_inferred, censor/LOD, parameter_units.
- **11 Wave-1 verified mechanism evidence** — target: enough verified D-C series for G15-4 (one identifiable focused fit) — choose focused system now (acrylamide/Maillard per §226.5, or vitamin C, chlorophyll, anthocyanin per SX-06-04). Also reaction-ledger rows (§216.3) with `verified` flag for the focused system's known pathway (§213.6).
- **12 Structured database evidence** — D-A/D-B growth (retention, nutrient, phenolic DBs); tag platform; supports G15-2/3/9, pair-holdout. Does not unlock D-C.
- **13 Large literature discovery corpus** — discovery for D-C kinetics and multi-species time series (G15-RXN prerequisites L22406–22407); topology-identification interventions (precursor, T, pH, moisture, oxygen, §213.23).
- **14 Coverage-driven evidence growth** — use §215.26 pre-model audit counts and §215.27 data-support map as the coverage objective; prioritise ingredient×process pair coverage for headline pair-holdout (§215.7) and temperatures per kinetic series.
- **15 Freeze DATA-EVIDENCE v1** — must produce dataset_version, split registry (pair-holdout, ingredient-disjoint, process-disjoint w/ parent family, condition-OOD, study-disjoint, platform-stratified, matrix-OOD), evidence-tier policy, target definitions (§216.6), dataset card (§216.12). Gate G15-1 (data audit) and G15-R (hashes/snapshots) belong here.
- **16 Instruction semantic schema** — D-D needs entity_ids_in/out, event_index, merge/split/reserve/discard/recombine (§215.18; §216.4), conditions per event; observed vs inferred state (`state_observed/state_inferred`, `observation_quality`).
- **17 Instruction-level extraction** — §215.18 metrics: action extraction F1, state-before/after accuracy, relation F1, intermediate-entity accuracy, merge/split… accuracy, sequence/order accuracy; "Do not merge these with chemistry metrics" (L22177).
- **18 Event-sourcing engine** — implements rollout/sequence table §216.4 and procedure-graph (R0/R1 rollout); provides `P_feasible(S_t,C)` prerequisites/tools for §214.6; append-only transition provenance.
- **19 Gold state-trajectory pilot** — the only source of "true intermediate states" for D-D (G15-11 L22392); must define observation_quality; separate qualitative state from quantitative chemistry.
- **20 Scale procedural semantic corpus** — D-D at scale for procedure graph/order reasoning; NOT a source of magnitudes (simulator_data_contract).
- **21 Effect/mechanism ontology** — local process modules (§213.29) as top-level mechanism families; qualitative transformation verbs (plan W6); unresolved sink `U` concept (§213.20) as explicit ontology term.
- **22 Event→effect signatures** — maps D-D events to candidate effects; must not create reaction edges (§213.11–12); outputs Claim-A style directional candidates only.
- **23 Mechanism applicability engine** — implements rate gating `v_r≈0` (§213.5) as applicability (prefer gating to topology mutation); prerequisites/moisture gating (§215.22); feeds P_feasible and evidence-class labels.
- **24 Formula/model registry** — must hold rate families (zero/first/nth/Arrhenius/Weibull), reaction-ledger fields (§216.3: rate_law, A, Ea, order, condition_scope, matrix_scope, parameter_uncertainty, verified), compartment model specs (§213.25), identifiability_status (§216.2).
- **25 Parameter-compatibility retrieval** — returns parameters whose condition_scope/matrix_scope cover the query; basis for d_evidence and "nearest supporting studies" (§214.44); INTERPOLATED vs EXTRAPOLATED labelling (§214.30).
- **26 One focused deterministic simulator** — the §213.6 known-pathway / §226.5 anchor simulator (acrylamide/Maillard candidate); open-system `Nv+u_in−u_out`; compartment rather than PDE (§213.27).
- **27 Validate simulator on held-out evidence** — headline condition-OOD (§213.36); report trajectory/endpoint error, non-negativity/balance, parameter uncertainty, topology sensitivity, matrix transfer (§213.37). Fail → RESEARCH_ONLY; also blocks simulator-first inverse design (§214.53A L21882).
- **28 Controlled E7 synthetic prior** — §213.43A: SINDy/CRNN discovery belongs to "simulator recovery studies" → recover known topology from simulated trajectories is the right place for any CRNN/SINDy experiment; G15-10 ratio sweep; E7 never in final test/calibration.
- **29 TRANSITION_BOOTSTRAP_V0** — = §216.1 schema + D0–D4 (D0–D6 for G15-2) on D-A; MP-1 contract exists. Gates G15-1, G15-2 (partial), G15-3 test. Decision record §216.13 items 1–2.
- **30 Strong tabular/sparsity bake-off** — D5, D6 (TabPFN where compatible), D7 completion; masked-real-cell and cold tests; G15-9; macro/micro (§215.6); decision table (§215.25); G15-6/G15-7 calibration/abstention on REAL study-disjoint data.
- **31 Physics/condition features** — A2/A4/A5 ablations; thermal dose; G15-3 & G15-5 partial (physics vs best non-kinetic tabular on held-out T). Decision record items 3–4.
- **32 Focused kinetics** — K0–K4 (K5 if moisture/pH exist); §216.2 table; AICc/BIC + held-out + identifiability; profile/bootstrap/posterior; G15-4. Decision record item 6.
- **33 Mechanistic vs ML vs hybrid** — §213.16–19, §213.43A multiplicative residual, K6; residual-off ablation; G15-HYB, G15-5; reaction-network variant only if G15-RXN prerequisites (realistically: defer). Decision record items 5, 7.
- **34 Short rollout** — 2–3 steps, D(k), trust horizon, rollout ablations §215.58; only where measured intermediates exist (D-C time series or Step 19 Gold); G15-11; G15-8 semigroup/order consistency. Decision record item 8.
- **35 Representation ladder** — §213.10 hierarchy atom graph→molecule embedding→species node→reaction network; molecule embeddings as cold-start side information (L21199); enters L15 only as A8 ablation after own gates (§216.10). FlavorTwin bridge `z_{i,t+1}=Agg(z_m,c_{m,t+1})` (§213.31) = process-conditioned ingredient representation, needs Step 33/34 outputs.
- **36 Evidence compiler → CulinaryState-RAG → FlavorTwin** — §215.60 decision hierarchy; §214.29 next-action pipeline; §214.30 evidence-class labels; §215.59 evaluation; G15-I; inverse design (I0→I1→… ID0→…) and FlavorTwin inverse (§214.25–27) gated by G15-INV and G15-12. Decision record item 9. **Inverse design has no dedicated spine step** — it lives implicitly in 36 (and possibly 34); see §9.

---

## 9. Contradictions, stale items, underspecified parts, open questions

Contradictions / inconsistencies
1. **Gate naming conflict**: §217.1 item 21 (L23075, v12 register) says "G15-1…G15-12 plus G15-R/G15-H/G15-I are frozen as the Level-15 decision gates", but §215.38 L22378 says the v13 table "supersede[s] the v12 G15-1…G15-I naming". The content of v12 G15-1…12 is not in my range (replaced in place). Resolution: v13 table authoritative (later version; §228.1 item 25–26 ≈L24871–24872 confirms revision). Mark §217.1 item 21 historical.
2. **D-ladder conflict across documents**: SSOT §209.17 (D4 nearest-evidence, D5 GBDT, D6 TabPFN, D7 completion, D8 kinetics, D9 hybrid) vs Master Plan v4.0 AZ6 (plan L4696–4712: D1 process mean, D2 nearest evidence, D3 linear/tree, D4 neural residual, D5 conditioning, D6 multi-output, D7 sparse completion, D8 kinetics, D9 hybrid, D10/11) vs MP-1 B-0..B-5 (transition_bootstrap_v0_contract.md L17) vs DEL-2 code "D0–D7". G15-2 ("D0–D6") is uninterpretable unless the SSOT §209.17 labels are fixed as canonical. The plan AZ6 ladder places neural models (D4–D6) before completion and GBDT — violates §209.17 "not allowed to skip D0–D7". → SSOT change request not needed; plan fix needed.
3. **Order of physics features vs kinetics**: §216.7 DAG (L22914–22918) kinetic fits → physics features → hybrid; §215.71 (L22707–22722) physics features → focused kinetics → hybrid. Spine follows §215.71. Probably both valid (physics features can be derived from fitted kinetics, e.g. Arrhenius-exposure, or from generic thermal dose); needs a clarifying note.
4. **G15-2 "D0–D6" vs §215.28 MVP "D0–D4 baselines"** (L22293) and §216.7 "D0–D4 endpoint baselines" (L22905) and §216.12 package (no D3 shrinkage, no D7; includes ridge which is not a named D-rung). MVP thus fails G15-2 as written. Need decision: G15-2 requires D0–D6 (with D6 "where compatible").
5. **Reaction ledger field sets differ**: §213.42 (L21173–21187) vs §216.3 (L22827–22843) vs Master Plan H2 item 11 / W6 (InChIKeys, SMARTS, marker compounds, confidence). Union needed; `measured/inferred` must survive into §216.3.
6. **Inverse provenance vs trial table**: §214.44 has "nearest supporting studies" and "optimization algorithm/version"; §216.5 lacks nearest studies. Union needed.
7. **§215 numbering gap**: §215.39 is followed by §215.53 (L22428); §215.40–215.52 absent (grep confirmed none). Probably removed v12 gate subsections; nothing lost that I can detect, but flag as stale editing artefact.
8. **G15-1 vs D-A database reality**: G15-1 requires "source/study" per row; USDA/Bognár have no study ids (13,888 of 17,978 ACTIVE rows NOT_IDENTIFIABLE study). "source/study" may be read as source OR study — ambiguous; needs explicit policy (independence_group as study surrogate, and study-disjoint impossible → source-disjoint).
9. **G15-H vs current evidence**: G15-H requires human verification only for *LLM-extracted* rows in test/calibration; current D-A rows are rule-parsed DB imports (UNVERIFIED, not LLM) — G15-H doesn't formally bind them, but project law "AI review ≠ human verification" and MP-1 "no row is called Gold" apply. Clarify whether DB-import rows need sample verification for calibration use.
10. **Inverse design has no spine home**: §214 (entire §) and G15-12/G15-INV, ID0–ID5, I0–I6, 15-F, M6 map to no explicit step among 29–34; Step 36 title mentions "later FlavorTwin". Under brief §4 rule, add as a sub-step of 36 (or 34) rather than a new step; it is deferred/stretch anyway.
11. **Reaction networks (Claim E) have no spine home** other than 33/28; realistic placement: 28 (simulator recovery study, per L21211) + 33 optional arm.

Underspecified
12. No numeric thresholds anywhere in G15-1…12/RXN/HYB/INV ("acceptable task-specific coverage/width", "declared tolerance", "meaningful", "adds value"); τ, u_max, κ, β, λ unspecified; "ID-level benchmark" pass criteria per rung undefined (ID0–ID5 are headings only, L21817–21827); trust-horizon tolerance defined in §212.52B (not checked here).
13. `T_type`, `t_type`, `ordinal_band`, `direction_label` thresholds (what counts as ≈ in Claim A), `observation_quality` scale, `evidence_distance` metric (multivariate; Mahalanobis? kNN in normalised condition space? study-weighted?) — all undefined in §§213–216.
14. `d_evidence` definition matters most (§214.14 shows marginal bounds fail): needs a defined joint support measure (e.g. convex hull / kNN / density / conformal OOD score) — external research item.
15. "Equal evaluation budget" (L21788) unit undefined (forward-model calls? wall time?).
16. Matrix-OOD and platform-disjoint splits lack definitions of matrix grouping/platform taxonomy.
17. Compartment model specification (which compartments, transfer laws) for boiling/frying — not specified.
18. §216.12 package lists TabPFN "if applicable" — licence/version and CPU feasibility not considered (TabPFN v2 runs on CPU for small n but is slower; check licence — external).

Open questions needing external research (do not answer from memory)
- Q1: Which focused D-C system has openly available multi-time × multi-temperature series with matrix detail sufficient for G15-4 and condition-OOD (acrylamide in potato/model systems; ascorbic acid thermal degradation; chlorophyll→pheophytin; anthocyanin; Maillard glucose–glycine multi-species)? SSOT names none (L21106–21124); S130 found structured sources lacking.
- Q2: Are there published food-chemistry multi-species time-series datasets suitable for reaction-network identification (Claim E), or is Claim E effectively simulator-only? Relevant literature: multiresponse kinetic modelling (van Boekel and colleagues, Maillard; to verify), CRNN (Ji & Deng 2021, J. Phys. Chem. A — to verify), SINDy (Brunton, Proctor & Kutz 2016 PNAS — to verify), UDE (Rackauckas et al. 2020 arXiv — to verify). SSOT itself marks these as `[SOURCE-REPORTED]` (L21213).
- Q3: Best practical evidence-distance / applicability-domain measure for mixed categorical+continuous process conditions (for C_safe, §214.32).
- Q4: Safe/pessimistic BO and constrained multi-objective BO methods appropriate at tiny data scale; whether NSGA-II on a cheap simulator is justified vs grid for 2-D (T,t).
- Q5: Kinetic model-family selection with AICc/BIC under censoring/LOD and identifiability (profile likelihood; Raue et al. 2009 Bioinformatics — to verify) — likely covered by L15 §210 reader.
- Q6: Conformal / selective prediction under study-grouped data (group-conditional coverage) for G15-6/7 — likely covered by §219–227 reader.

Stale items
- §213.6 "Focused known systems are preferred for a semester project" (L20689) and §226.9 "Semester compression" — semester framing may be stale relative to the 36-step multi-phase programme.
- §215.66 paper story lists "FoodProc-style cold-start/study benchmark" — "FoodProc" undefined in my range (UNVERIFIED reference; probably defined in §219–227).

---

## 10. LOOK-AHEAD: fields earlier steps must capture

Must be captured by **03/04 (state & evidence contracts)**:
- `state_before_id`, `state_after_id`, state location/compartment (food, cooking water, surface, core, drip/fat) — needed for open-system balance `u_in/u_out` (L20985) and leaching compartments (L20990).
- `explicit_or_inferred`, `extraction_method` (rule/LLM/human), `verification_status` with span/table locator (G15-H).
- Evidence class enum for outputs (OBSERVED/INTERPOLATED/MODEL-ESTIMATED/EXTRAPOLATED/UNSUPPORTED).
- Edge-type enum for any graph relation (reaction / transport / equilibrium / statistical).
- Target mask semantics (partial targets) and "UNKNOWN ≠ 0" for unmeasured species/targets.

Must be captured by **05 (EVD normalization)**:
- value_before, value_after, delta_value, direction_label, ordinal_band, unit, basis (true/apparent retention, fresh/dry), censor_flag, LOD (separately from LOQ/ND per §228.1 item 13 ≈L24860), platform, matrix_description, replicate count/SD/SE (for §215.54–55 noise floor & ceiling analysis — NOT listed in §216.1 but required by §215.54 L22458; add `n_replicates`, `dispersion_value`, `dispersion_type`).
- `matched_status` (matched before/after pair vs unpaired) and `trajectory_availability` (§215.3 L22007–22009).

Must be captured by **06 (acquisition manifest)**: per source: regime (D-A/B/C/D), has_time_series, n_temperatures, multi_species, has_intermediates, platform(s), replicates reported, raw-table availability, licence — the §215.27 support-map columns, so 14 can be coverage-driven.

Must be captured by **07 (conditions)**: T_value/T_lo/T_hi/T_type (setpoint vs medium vs surface vs core; nominal vs measured), temperature_schedule T(t) (time-indexed) and heating-come-up time; t_value/t_lo/t_hi/t_type (total vs hold time); medium; tool; geometry (cut size/thickness — affects compartments & heat transfer); moisture_before/after; water_activity; pH (initial & during); pressure; oxygen (headspace/packaging/aerobic); mixing; power (exists); precursor concentrations (initial_conditions for §216.2 — e.g. asparagine/reducing sugar for acrylamide) — the topology-identification intervention variables (initial precursor, T, pH, moisture, oxygen; L20962–20968). Current COND has no oxygen/aw/geometry/mixing axes and moisture/pH 100% UNKNOWN — a look-ahead gap.

Must be captured by **08 (lineage)**: study_id, experimental-campaign id, paper DOI, lab/author group (for publication-disjoint), shared-yield/shared-measurement links across sources (MP-1 leakage list), derived-from links (USDA imputed-from-similar-food donors), so study-disjoint, source-disjoint and study bootstrap (§215.53) are possible and G15-6 calibration is "study-disjoint".

Must be captured by **09 (extraction/verification)**: raw timepoint tables preserved separately from fitted parameters (L22823); source span/table coordinates; reported fitted parameters (k, Ea, A, order, D/z values) with units and reported uncertainty, flagged as `source_reported` vs `refit_by_us`; fit model family reported by authors; extraction confidence; human verifier id/date.

Must be captured by **10–14 (acquisition)**: for the chosen focused system — ≥ several temperatures with ≥ several timepoints each (Arrhenius needs multiple T, L21079), co-measured moisture(t) & T(t) (§213.36), jointly measured species (precursors, intermediates, products) for any reaction claim; replicate data; matrix variants (for matrix-OOD §215.13); platform for volatiles; held-out temperature ranges reserved for condition-OOD (do not consume all temperatures in development). Reaction-ledger rows for the known pathway with stoichiometry and condition/matrix scope.

Must be captured by **15 (freeze)**: dataset_version, ontology version, unit-normalisation version, split version (with all split families and group keys), evidence-tier policy, target definitions (§216.6); real-only calibration and test partitions locked; E7/imputed flag column to enforce G15-10's exclusion.

Must be captured by **16–20 (procedure/state)**: sequence_id, event_index, entity_ids_in/out, process (leaf + family), per-event conditions, state_observed vs state_inferred, observation_quality (§216.4); merge/split/reserve/discard/recombine operators; tools/equipment availability (for hard constraints, §214.5); prerequisites (for P_feasible, §214.6); measured intermediate state labels for any rollout claim (G15-11).

For **24/25 (registry/parameters)** downstream of the above: rate_law, A, Ea, order, condition_scope, matrix_scope, parameter_uncertainty, identifiability_status, calibration_source vs validation_source (keep distinct to avoid leakage into Step 27/32 held-out tests).

For **36 / inverse design**: forward_model_version, optimizer + version, constraint set (hard/soft documented), evidence_distance, nearest supporting studies, OOD_flag, prediction_interval, heldout_or_real_outcome (§216.5 + §214.44 union).
