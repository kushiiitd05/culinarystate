# r_mechanism_registry — research notes for spine Steps 21–25 (Mechanism intelligence)

Researcher: r_mechanism_registry · Date: 2026-10-22 · Mode: PLAN-RESEARCH ONLY (no implementation, nothing in the repo changed).
Internal sources were read only. External sources were opened through Europe PMC REST, Crossref, EBI OLS4, GitHub raw/API, SBML.org and JRC/QSARDB PDFs. No project data went into any query.
Caveat: the 36-step plan's step cards are MISSING (ctx.md). The scope given below for Steps 21–25 is *reconstructed* from the step titles (brief §9), brief §§20–21, SSOT v15 and Master Plan v4.0. It is not card text.

---

## 0. Internal baseline (what exists today) — verified in repo

| Item | Finding | Evidence |
|---|---|---|
| Mechanism / RXN ledger | **Does not exist.** There is no `RXN.jsonl`, `MECH-`, `MODEL-`/formula or `PARAM-` registry. | `ls ledgers/data` (19 ledgers, no RXN); `registry/` listing |
| Mechanism links on processes | `PROC.jsonl` has 552 rows, each with a `mechanism_families` list (23 distinct labels, e.g. maillard 76, lipid_oxidation 76, acrylamide_formation_starchy 41). **All 552 are `verification.status=UNVERIFIED`**, with the note "mechanism families AI-drafted (verify vs R3)". | `ledgers/data/PROC.jsonl`; `reports/h_state/state_representation_contract_v1.md` L71 (C7: "may not gate any claim until HV-010") |
| Mechanism evidence rows | "mechanism rows 0" | `state_representation_contract_v1.md` L24 |
| Condition coverage of current EVD | 4,414 conditions referenced by 17,978 EVD rows. **pH, moisture and aw are UNKNOWN in all 4,414.** Only 213 temperatures are VALID with a stated location (2,409 UNSPECIFIED → AMBIGUOUS). **No trajectories.** No platform is recorded. LOD/LOQ are UNKNOWN everywhere. | `reports/step07/step07_report.md` L12–23; `reports/step07/step07_condition_coverage_audit.json` |
| Condition vocabulary (ready for future rows) | 40 condition variables, incl. CV `ph`, `water_activity`, `oxygen_headspace`, `additive_catalyst_enzyme`, `maturity_ripeness`, `temp_core/surface/medium/setpoint`, `temp_trajectory` | `registry/condition_variable_registry_v1.csv` |
| State variables needed by mechanisms | `SVAR-FUT-002` aw and `SVAR-FUT-014` precursor concentration are both `not_applicable_yet`. There is no enzyme-activity-state variable. | `registry/state_variable_registry_v1.csv` |
| Simulator output contract | `validation_scope`, `extrapolation_flag`, `parameters (source or SIMULATED_PARAMETER)`, `simulator_id → registry entry with equations/assumptions`, E7 only, `may_enter_gold_evaluation=false` | `registry/simulated_state_changes_schema_v1.csv` |
| Step-07 human gate | `step07h_human_gate_result.json` = NOT_COUNTED_PROVENANCE_INVALID (per ctx.md). Condition annotations are therefore not promoted for scientific use. | ctx.md; `step07_report.md` L3 |

SSOT/plan anchors used throughout:
- SSOT §144.1 mechanism families + frozen cautions (L8976–8986)
- §144.2 sparse evidence, censoring, leaching vs destruction (L8987–8993)
- §64 v4 update listing candidate causal drivers (L3885–3893)
- §199.6 REQUIRED/TYPICAL/OPTIONAL/INCOMPATIBLE/UNKNOWN state–action relations (L16173–16180)
- §208.5 L15-A…F fidelity ladder (L18058–18111)
- §210.15 moisture-gated kinetics (L18878)
- §210.18 parallel/competing pathways (L18938–18955)
- §210.20 lumped parameters (L18974–18986)
- §210.27 process-family model library (L19072–19088)
- §210.28 K0–K4 kinetic data hierarchy (L19089–19110)
- §210.29 kinetic evidence schema (L19111–19136)
- §210.29A Tref-Arrhenius (L19137–19163)
- §210.30 "never harmonize k across orders/units" (L19164–19187)
- §211.38 cross-study pooling (L19669)
- §211.40 effective vs mechanistic (L19695–19700)
- §211.50 minimal kinetic report (L19806–19827)
- §215.22 mechanistic consistency (L22218–22229)
- G15-RXN (L22402–22411)
- §223.2 S-MECH (L24078–24098) and §223.5 forbidden claim (L24119–24121)
- §241.3 categorical compatibility vector (L26339–26347)
- §257O.4 mechanism lookup ≠ quantity (L42670–42673)
- §263.1 parameter-name compatibility rule (L43361–43364)
- SSOT L10690 BioModels BIOMD0000000052 row
- Master Plan v4.0:
  - ID table RXN (L549)
  - reaction ledger (L570)
  - E6/E7 tiers (L590–596)
  - mechanism families (L601)
  - W4 `applicability:` block (L1646–1654)
  - W6 RXN representation (L1689–1725)
  - W7 state compiler (L1727–1767)
  - X6 MODEL registry (L2028–2046)
  - cascade DIRECT/INTERPOLATED/MODEL/QUALITATIVE/ABSTAIN (L4751)

---

## 1. Research questions

- **Q1** Which existing model-exchange/registry standards (SBML + units/SBO/Constraints, SED-ML, KiSAO, CellML, MIRIAM/identifiers.org, BioModels curation, FSK-ML/FSKX, PMF-ML/PMM-Lab, ComBase) should the formula/model registry adopt, borrow from, or only export to?
- **Q2** How do these standards and the QSAR/AD literature represent the *validity/applicability domain* of a model? Is per-parameter min/max (a box) enough?
- **Q3** How should model *quality* be recorded so that calibration (fit) is not confused with validation (held-out predictivity)?
- **Q4** Which ontologies can anchor mechanisms, participants, enzymes, processes and rate laws, and where are the gaps?
- **Q5** How should mechanism activation conditions, competing mechanisms, inhibitors, matrix dependence, T/pH/aw/O2 ranges, substrate availability, enzyme state and history be represented?
- **Q6** Is EVENT → direct change → candidate effects → mechanism applicability → formula applicability → parameter compatibility → validated domain → SIMULATE/RETRIEVE/QUALITATIVE/UNKNOWN sound?
- **Q7** Do curated food-chemistry kinetic-parameter repositories exist that the parameter registry could draw on?
- **Q8** How should parameter-compatibility retrieval work (Step 25)?
- **Q9** Which brief §21 fields are essential now, and which can be deferred?

---

## 2. Findings

### Q1 — Standards to adopt / borrow / export

**F1.1 (HIGH).** FSK-ML/FSKX is the closest food-domain precedent. It is an SBML-derived, COMBINE-archive-based exchange format for food-safety models (QMRA and predictive microbiology), produced by the BfR/RAKIP initiative.
- I opened the RAKIP JSON/YAML schema (`SiLeBAT/fskml_schemas/model.yaml`, "RAKIP Generic model" v1.0.4, last pushed 2021-02-16).
  - Top-level sections are generalInformation / scope / dataBackground / modelMath, plus model-type subclasses (GenericModel, PredictiveModel, ProcessModel, DoseResponseModel, …).
  - `scope.product` holds name, description, unit, method, packaging, **treatment**, origin, dates.
  - `Parameter` holds id (SBML-SId compatible), `classification` ∈ {CONSTANT, INPUT, OUTPUT}, name, description, unit, unitCategory, dataType, source, subject, distribution, value, reference, variabilitySubject, **minValue / maxValue** and error.
  - `minValue`/`maxValue` are documented as "the range of applicability for which the model applies".
  - `QualityMeasures` = sse, mse, rmse, rsquared, aic, bic and sensitivityAnalysis. **These are all goodness-of-fit. There is no external-validation field.**
  - `ModelEquation` holds name, class, reference, a pointer to the script, and modelHypothesis.
  - Related papers: Haberbeck et al. 2018 (metadata schema), de Alba Aparicio et al. 2018 (FSK-Lab), Plaza-Rodríguez et al. 2015 (model repository strategy). The BfR website was unreachable from this server, so the FSK-ML guidance v3.1 PDF was NOT opened.
- Consequence: borrow the parameter fields and the INPUT/OUTPUT/CONSTANT classification. Do not adopt the domain or quality semantics as they stand (see Q2/Q3).

**F1.2 (HIGH).** PMF-ML (BfR, `SiLeBAT/pmfml`, "Predictive Modelling in Food Markup Language", last pushed 2021-05-11) is SBML-based. It types models as:
- EXPERIMENTAL_DATA
- PRIMARY_MODEL_W(O)DATA
- ONE/TWO_STEP/MANUAL SECONDARY
- ONE/TWO_STEP/MANUAL TERTIARY

ModelClass includes T, pH, aw and their combinations. It encodes variable limits **as SBML Constraints**: `LimitsConstraint` generates `(var >= min) && (var <= max)`. It also stores parameter `Correlation` objects.
- The **primary / secondary / tertiary** split maps directly onto food kinetics:
  - primary = time course at fixed conditions (zero-, first-order or Weibull law)
  - secondary = parameter as a function of conditions (Arrhenius in T; pH/aw terms)
  - tertiary = composed, executable model
- I opened the repo listing and the `ModelType`, `ModelClass`, `Limits` and `LimitsConstraint` sources.

**F1.3 (HIGH).** SBML Level 3 (Keating et al. 2020 MSB; spec L3V2 Hucka et al. 2019 JIB) supplies:
- units on all quantities
- SBO terms for the mathematical semantics of each element
- the `distrib` package for uncertainty and distributions
- Events: "instantaneous, discontinuous state changes", triggered by a condition
- **Constraints**: "a mechanism for stating the assumptions under which a model is designed to operate … if a dynamical analysis … reaches a state in which a constraint is no longer satisfied, the results of the analysis are deemed invalid beginning with that point in time" (spec §4.10, opened).

SBML core assumes well-mixed compartments. Spatial/transport models (heat/mass transfer in a potato slab) need the `spatial` package or another format (CellML/FEM). BioModels holds a curated SBML Maillard model from a food model system: **BIOMD0000000052** (Brands & van Boekel 2002 JAFC 50:6725, monosaccharide–casein, multiresponse-estimated rate constants; page opened, status "Curated", SBML L2V1).
- Consequence:
  - Adopt **SBML Constraint semantics** as the runtime "validated-domain guard" along trajectories.
  - Treat SBML/FSKX as an **export target** for the single Step-26 simulator, not the internal storage format.

**F1.4 (HIGH).** The other standards, and what to take from each:
- **SED-ML** (Waltemath et al. 2011, BMC Syst Biol) describes the simulation experiment (model, modifications, simulation algorithm, outputs) independently of the model.
- **KiSAO** (Courtot et al. 2011 MSB) identifies algorithms. OLS confirms KISAO:0000019 = CVODE.
- **SBO** (same paper) provides participant roles and rate-law terms (see Q4).
- **MIRIAM** (Le Novère et al. 2005 Nat Biotechnol) sets curation rules: reference correspondence, attribution, external-resource annotation. BioModels curation verifies that a model **reproduces the simulation results of the reference publication** (Malik-Sheriff et al. 2020 NAR).
- **identifiers.org** compact identifiers (prefix:accession; Wimalaratne et al. 2018 Sci Data) are the right xref syntax.
- **CellML 2.0** (Clerx et al. 2020 JIB) is component/variable/equation based. It is an alternative abstraction to SBML and adds nothing CulinaryState needs beyond SBML + an equation AST.
- Consequence:
  - Registry status lifecycle gets a **REPRODUCED** state, meaning the reimplementation reproduces a figure or table of the source paper (the BioModels-curation analogue). It sits before CALIBRATED and VALIDATED.
  - Solver is recorded as a KiSAO CURIE.
  - All xrefs are identifiers.org-style CURIEs.

### Q2 — Applicability/validity domain representation

**F2.1 (HIGH).** OECD (Q)SAR Principle 3 calls for "a defined domain of applicability". The JRC QSAR Model Reporting Format v1.2 (26/05/2008, opened) defines the AD as "the response and chemical structure space in which the model makes predictions with a given reliability". It asks for:
- fixed *or probabilistic* boundaries
- the AD method and software
- inclusion/exclusion rules on descriptor ranges *and response ranges*

The full OECD 2007 guidance (ENV/JM/MONO(2007)2) could not be opened (OECD server refused); its principle wording is taken from QMRF.

**F2.2 (HIGH).** Sahigara et al. 2012 (Molecules 17:4791, full text opened) group AD methods into four families:
- range-based (bounding box, PCA box)
- geometric (convex hull)
- distance-based (Euclidean, Mahalanobis/leverage, kNN)
- probability-density

**A bounding box "cannot identify empty regions … and the correlation between descriptors"**, and the convex hull also misses internal empty regions. Schultz, Wang, Jacobs & Morgan (npj Comput Mater 11:95, 2025; arXiv 2406.05143 abstract opened; publication confirmed via Crossref) show that KDE-based feature-space dissimilarity tracks larger residuals and unreliable uncertainty estimates.

**F2.3 (HIGH).** Predictive microbiology hit this exact problem for T × pH × aw models:
- Baranyi, Ross, McMeekin & Roberts 1996 (Food Microbiol 13:83, Crossref-verified) introduced the **Minimum Convex Polyhedron (MCP)** of the design points as the interpolation region.
- Le Marc, Pin & Baranyi 2005 (IJFM 100:3, abstract opened) combine MCP and logistic regression to handle "extrapolation of predictive models at the growth limits", using ComBase data.
- Consequence: **FSK-ML/PMF-ML per-parameter min/max (a box) is not an adequate validated domain.** Kinetic studies sample sparse factorial or one-factor-at-a-time grids, so the box corners are often unsupported.

**F2.4 (HIGH).** Three different things are routinely conflated in "domain":
- (a) **calibration domain**: the convex hull of the design points the parameters were fitted on
- (b) **validated domain**: the points where predictions were checked against *held-out, study-disjoint* measurements
- (c) **structural assumption domain**: isothermal, well-mixed, constant moisture, first-order, no competing pathway (SBML Constraint-type boolean conditions)

FSK-ML only has min/max. QMRF only has "AD". SSOT §223.5 already forbids claims outside the "validated domain", so (b) must be a first-class field distinct from (a).

### Q3 — Fit vs predictivity

**F3.1 (HIGH).** QMRF splits OECD Principle 4 into goodness-of-fit and robustness (§6: r², LOO, LMO, Y-scrambling) versus predictivity on an external set (§7). FSK-ML QualityMeasures only covers the first.
- Ross 1996 (J Appl Bacteriol 81:501, abstract opened) proposed the **bias factor and accuracy factor** as the predictive-microbiology performance indices, aimed at "an objective … definition of the term 'validated model'". He warns that published data can be inappropriate for validation.
- Pin et al. 2004 (AEM 70:3925, abstract opened) found that a model developed in laboratory media and validated on seafood and ComBase showed **bias "when applied to food environments"** plus higher variability in food. Their statistical method was also used to *extend* the interpolation region.
- Consequence: the registry needs a separate `VAL-` record type (dataset ids, study-disjointness, matrix relation, Bf/Af + RMSE in natural units + interval coverage). Calibration statistics go on the parameter set and never count as validation.

### Q4 — Ontologies (EBI OLS4 probes, 2026-10-22)

**F4.1 (MEDIUM-HIGH; absence-of-evidence from probes).** No OBO ontology provides a food-chemistry mechanism hierarchy.
- "Maillard reaction" appears only in MeSH (D015416) and OMIT. ChEBI has the role CHEBI:77523 "Maillard reaction product".
- **RXNO** (named reactions) has 0 hits for Maillard but does contain:
  - RXNO:0000224 **Strecker degradation**, with a food-aroma definition
  - RXNO:0000207 **Strecker reaction**, the amino-acid synthesis, which is a different reaction. **This is a label-collision hazard for automated mapping.**
- "Acrylamide formation" returned nothing. "Starch gelatinization" exists only as a trait (TO:0000462).
- **GO** has enzyme activities for the cutting-triggered families:
  - GO:0047654 alliin lyase activity
  - GO:0004097 catechol oxidase activity (PPO)
  - GO:0019137 thioglucosidase activity (myrosinase)
  - lipoxygenase activities
  - GO:0030164 protein denaturation
- **SBO** provides participant roles: SBO:0000010 reactant, 0000011 product, 0000019 modifier, 0000020 inhibitor, 0000013 catalyst, 0000459 stimulator, 0000461 essential activator. It also has rate-law and kinetic-constant terms (SBO:0000001, 0000009, 0000046). It has **no Arrhenius term**.
- **FoodOn** (Dooley et al. 2018 npj Sci Food, LanguaL-derived) has *process* terms such as food blanching FOODON:03470175, roasting, grilling, pressure frying and heat drying process, but no mechanisms.
- **PO²/TransformON** (Weber et al. 2023 npj Sci Food 7:47) is a process-and-observation ontology for food/bioproduct transformation. It suits the process and observation side, not chemistry mechanisms.
- **Rhea** (Bansal et al. 2022 NAR) is the ChEBI-based curated reaction knowledgebase, for enzymatic reactions.
- Consequence: Step 21 must **author its own small mechanism vocabulary** (MECH-), seeded from SSOT §144.1 and Master Plan L601. External ontologies are used as **xrefs only**: RXNO/MeSH for mechanism, GO MF + EC/Rhea for enzyme, ChEBI for participants and roles, SBO for participant roles and rate laws, FoodOn/PO² for process alignment. Every xref needs human verification, because the Strecker collision shows that label-matching is unsafe.

### Q5 — Representing activation conditions, competition, inhibitors, matrix, history

**F5.1 (HIGH as pattern; MEDIUM as transfer).** Predictive microbiology's **cardinal-parameter / gamma** form models a rate as μ_opt × Π factor_i(x_i). Each factor is defined by cardinal values (x_min, x_opt, x_max), and rate = 0 outside [x_min, x_max]. Rosso et al. 1995 (AEM 61:610, abstract opened) use 3 cardinal T and 3 cardinal pH values and **explicitly assume independent T and pH effects**.
- This is a clean, evidence-addressable way to encode "activation window" plus "modulation".
- It also shows the trap: independence is an *assumption*, which the registry has to record, and later work adds interaction terms.
- For CulinaryState, per-axis gates should be stored as **intervals with provenance and matrix scope**, never as a universal switch (SSOT §144.1 frozen caution: "no universal temperature switch").

**F5.2 (HIGH).** Reaction-centric curated databases key every parameter set to its experimental conditions. In SABIO-RK (Wittig et al. 2018 NAR, full text opened), "a database entry … comprises kinetics data for one single reaction in one organism under specific experimental conditions", including pH/temperature, rate law and formula. STRENDA DB (Swainston et al. 2018 FEBS J) validates the completeness of reported enzymology data and conditions. This is the right pattern for `PARAM-`: a parameter is meaningless without its fitted-on conditions and matrix.

**F5.3 (HIGH).** Matrix dependence is fundamental, not a nuisance. van Boekel 2008 (CRFSFS 7:144, abstract via Crossref) states that chemical-kinetics principles "are strictly speaking only valid for simple elementary reactions, and foods are all but simple. Interactions in the food matrix and variability are 2 complicating factors." The same review points to the lumped/effective parameters already in SSOT §210.20/§211.40. Pin 2004 gives the empirical demonstration (lab-medium → food bias).

**F5.4 (reasoned from SSOT + sources; MEDIUM-HIGH).** Required representational elements:
- (i) *Necessary preconditions*: substrate/precursor present, enzyme present **and active**, compartment disruption (cutting/crushing for alliinase/myrosinase/PPO/LOX), water present.
- (ii) *Condition gates* per axis: NECESSARY / MODULATING / INHIBITING, each an interval with matrix scope and evidence.
- (iii) *Inhibitors/mitigators*: acid, chilling, blanching (enzyme inactivation), antioxidants, sulfite, exclusion of O2. These use SBO inhibitor/modifier roles.
- (iv) *Competing/parallel pathways*: SSOT §210.18. Represented as a `competes_with` relation plus a requirement that a target affected by ≥2 applicable mechanisms can only be simulated with a jointly-fitted multiresponse/composite model (§210.19). Example: ascorbate loss by leaching vs oxidation, SSOT §144.2 and §210.21.
- (v) *History dependence*: this needs **state** not conditions, carried by Step 18. Items:
  - enzyme_activity_state ∈ {ACTIVE, PARTIALLY_INACTIVATED, INACTIVATED, UNKNOWN}
  - cell_integrity ∈ {INTACT, CUT, CRUSHED/PUREED, UNKNOWN}
  - time-since-disruption (garlic crush/rest, SSOT §144.3)
  - cumulative thermal dose (§210.13)
  - precursor depletion
  - prior acid/salt exposure
  - oxygen exposure (covered/uncovered)
- (vi) *Marker caution*: HMF, colour, pyrazines and hexanal are not unique pathway identifiers (§144.1). Effect signatures must never infer a mechanism from a marker alone.

### Q6 — Is the decision chain sound?

**F6.1 (MEDIUM-HIGH).** The brief §20 chain is **sound as the gating sequence for the SIMULATE branch**. It is unsound as the whole decision procedure, for six reasons:
1. **Evidence retrieval must run first or in parallel, and it dominates.** The SSOT/Master Plan cascade is DIRECT → INTERPOLATED → MODEL → QUALITATIVE → ASK/ABSTAIN (MP L4751; brief §28; SSOT §257O.4 "why this may happen" ≠ "how much happened"). A direct, compatible E1–E4 measurement should pre-empt simulation. Simulation is a fallback or a cross-check, not the first resort.
2. **Every gate is three-valued** {PASS, FAIL, UNKNOWN} + reason code + evidence ids (UNKNOWN ≠ 0 law). UNKNOWN at any of mechanism applicability / formula applicability / parameter compatibility / validated domain **forbids SIMULATE**. It does not mean "not applicable".
3. **The unit of decision is (entity-version × event × target variable)**, not the event. One event can be SIMULATE for moisture and UNKNOWN for a volatile.
4. **Add a competing-mechanism gate** between mechanism applicability and formula applicability. If ≥2 applicable mechanisms act on the target and no jointly fitted model covers them, numeric output is prohibited. The result is QUALITATIVE (direction only, if all applicable mechanisms agree) or UNKNOWN/CONFLICT.
5. **Add an input-observability gate.** A formula needs specific inputs: core vs surface T trajectory, aw, initial concentration. If they are UNKNOWN they must not be imputed into a simulator to produce a number (law: no invented value). Today this gate would fail for essentially all EVD conditions (pH/aw UNKNOWN in 4,414/4,414).
6. **Distinguish calibration domain vs validated domain** (F2.4). Inside calibration but outside validation → result is labelled MODEL_ESTIMATED / RESEARCH_ONLY, not a validated estimate.

The terminal enum should align with the SSOT cascade: DIRECT · INTERPOLATE · SIMULATE (=MODEL, E7, with propagated uncertainty) · QUALITATIVE (L15-A direction) · ASK (missing user-observable input, e.g. "was it covered?") · UNKNOWN/ABSTAIN.

### Q7 — Do curated food-chemistry kinetic-parameter repositories exist?

**F7.1 (MEDIUM).** Two searches found **no open curated food-chemistry kinetic-parameter database** comparable to:
- ComBase (microbial responses; Baranyi & Tamplin 2004 J Food Prot)
- SABIO-RK (biochemical reactions, mostly non-food)

What exists:
- handbook compilations: Villota & Hawkes "Reaction kinetics in food systems" (Handbook of Food Engineering; NOT opened, paywalled → UNVERIFIED content)
- reviews: van Boekel 2008; van Boekel 2021 J Food Eng 306:110634 workflow proposal (Crossref-verified metadata only)
- individual papers
- one curated SBML Maillard model-system entry (BIOMD0000000052)

SSOT L10690 already says Maillard kinetics "must be digitized by hand".
- Consequence: `PARAM-` will be populated by **literature extraction in Steps 11/13**, slowly and with human verification. It must be scoped to the Step-26 system first.

### Q8 — Parameter-compatibility retrieval design

**F8.1 (HIGH as principle, from SSOT §241.3 + SABIO-RK/STRENDA + §210.30).** This is a **structured, rule-first retrieval problem, not a dense-retrieval problem.** Design:

- **Hard filters** (never relaxed):
  - same model form/equation and reaction order
  - unit-dimension consistency (§210.30)
  - same mechanism or an explicitly declared lumped scope
  - effective-vs-mechanistic flag respected (§211.40)
  - Tref present when the Tref-Arrhenius form is used (§210.29A)
  - original symbol definitions mapped through an explicit conversion table (§263.1 rule generalised: never unify symbols from memory)
- **Categorical match vector** (SSOT §241.3, kept categorical before any scalar):
  - m_matrix ∈ {EXACT, SAME_SPECIES/CULTIVAR, SAME_FOOD_GROUP, MODEL_SYSTEM, GENERIC}
  - m_composition: query moisture/aw/pH/fat/precursor inside fitted ranges? (UNKNOWN allowed)
  - m_condition: query point inside the **calibration MCP/convex hull**, plus kNN distance in normalised condition space. A per-axis box is the baseline only.
  - m_history: blanched/raw, enzyme state, cut state
  - m_measurement: platform/basis compatible (MEAS-, measurement_basis_registry)
  - m_design_level: K0–K4 (§210.28); Arrhenius extrapolation is allowed only from K2+ and only within the fitted T range
- **Multiple compatible sets:** no averaging across studies unless a hierarchical model has been fitted (§211.38). Keep them as an ensemble with source spread, or as a CONFLICT with lineage (Step 08 independence groups).
- **Outputs:** ranked candidate parameter sets with the full match vector and the reason for each exclusion. This is a replayable `APPDEC-` record (SSOT L42346 "evidence_compatibility_features — persist or log").

### Q9 — Which brief §21 fields are essential?

See §3.2 below. Essential at v1:
- model_id, mechanism_id(s), equation (machine-readable), state variables, inputs, parameters → PARAM, units
- assumptions (as Constraint expressions), initial conditions
- matrix scope, condition scope (calibration domain), parameter source, calibration source, validation source → VAL
- identifiability status, implementation reference + code hash, solver (KiSAO), uncertainty, status

Boundary conditions are essential **only for transport models** (leaching, heat/moisture transfer) and N/A otherwise. Sensitivity analysis is deferrable.

---

## 3. Architecture recommendation

### 3.1 Recommended: "small native registries + standards-borrowed semantics + export-only exchange"

Five linked, append-only registries (JSONL + JSON Schema, consistent with existing ledgers). They hold no scientific values beyond the cited source, and every row carries provenance class, tier and verification:

1. `MECH-` mechanism registry (Step 21)
2. `EFFSIG-` event→candidate-effect signatures (Step 22)
3. `MODEL-` formula/model registry, with `PARAM-` and `VAL-` (Step 24)
4. `APPDEC-` applicability decision records (output of Steps 23 + 25; replayable)
5. Reuse the existing COND/SVAR/MEAS/STUDY/EVD/PROC ledgers. Do not duplicate them.

Exchange: export the one Step-26 simulator as SBML L3 (+ distrib if used) / SED-ML / FSKX-compatible metadata **optionally**, for reproducibility credibility. The internal store stays native.

### 3.2 Minimal schemas (v1)

**MECH-** (Step 21; target ≈20–40 entries, splitting the SSOT §144.1 families)
- mechanism_id
- label + synonyms
- family (§144.1)
- kind ∈ {CHEMICAL_REACTION, ENZYMATIC, PHYSICAL_TRANSPORT (leaching, volatilisation, moisture loss, oil uptake), PHASE/STRUCTURAL_TRANSITION (gelatinisation, denaturation, melting, crystallisation), MICROBIAL, MECHANICAL_DISRUPTION}
- participants[] = {MOL/ChEBI CURIE or class, SBO role}
- enzyme = {EC, GO MF, Rhea} | null
- preconditions[] (state predicates on SVAR/entity state: substrate present, enzyme ACTIVE, cell_integrity≠INTACT, water present)
- condition_gates[] = {CV axis, gate_type NECESSARY|MODULATING|INHIBITING, interval (min/opt/max allowed, each nullable), matrix_scope, evidence_ids, status}
- inhibitors_mitigators[] (SBO:0000020/0000019, with evidence)
- competes_with[] / consecutive_with[]
- affected_targets[] = {SVAR id, allowed directions}
- markers[] + `marker_unique=false` default
- history_dependence[] (which state variables are required)
- xrefs[] (RXNO/MeSH/GO/ChEBI/FoodOn CURIEs, each with verification)
- evidence_tier, provenance_class, verification
- `ai_drafted` flag (PROC mechanism links stay AI-drafted until verified)

**EFFSIG-** (Step 22)
- signature_id
- trigger = {process family/leaf (PROC), tool/medium/modifier predicates, required condition axes}
- deterministic_changes[] (mass split/combine, geometry, cut-state change, temperature setpoint; DERIVED_DETERMINISTIC only)
- candidate_mechanisms[] → MECH
- candidate_effects[] = {SVAR, direction set}
- provenance = E6/MODEL_ESTIMATED
- `is_evidence=false`

**MODEL-** (Step 24) — brief §21 fields, with modifications:
- model_id, mechanism_ids[]
- model_tier ∈ {PRIMARY, SECONDARY, TERTIARY} (PMF-ML)
- model_family (§210.27)
- equation = {machine AST (SymPy/MathML), human LaTeX}
- state_variables[] (SVAR+unit)
- inputs[] (CV axis + **required location**, e.g. temp_core)
- parameters[] → PARAM
- assumptions[] as **Constraint expressions** (SBML semantics: violation ⇒ results invalid from that time)
- initial_conditions_required[]
- boundary_conditions (transport only)
- effective_or_mechanistic
- calibration_domain (MCP/convex hull or point set + box summary)
- validated_domain → VAL ids
- identifiability_status (§211)
- implementation = {repo path, code hash}
- solver (KiSAO CURIE)
- uncertainty_representation
- status ∈ {CANDIDATE, REIMPLEMENTED, REPRODUCED, CALIBRATED, VALIDATED_HELD_OUT, RESEARCH_ONLY, RETIRED}
- provenance/licence

Note: the existing Master Plan X6 `MODEL-` (L2028) is an **ML model registry** (training data, seed, checkpoint). **Name collision.** Recommend a prefix such as `FORM-`/`KMOD-` for scientific formula models, or a `model_kind` discriminator. Flag this as a DECISION needed.

**PARAM-** (Step 24/25)
- param_id, model_id
- symbol_source + symbol_canonical + conversion note (§263.1)
- value | interval | distribution
- unit + reaction_order
- T_ref
- estimation_method, CI/SE, correlation_with[] (PMF-ML Correlation)
- fitted_on = {study_ids, independence_group, matrix (ING/FoodOn), composition descriptors, process, design points (T list × time list), K-level (§210.28), measurement (MEAS), basis}
- effective_or_mechanistic
- source locator (table/figure/page), extraction tier, verification

**VAL-**
- val_id, model_id + param_set
- evaluation EVD ids
- study_disjoint (bool + lineage proof)
- matrix_relation
- condition points covered
- metrics: RMSE in natural units, Bf/Af, interval coverage, sign accuracy
- verdict
- `may_define_validated_domain` (bool)

**APPDEC-**
- query (entity version, event, target)
- per-gate result {PASS/FAIL/UNKNOWN/N_A} + reason codes + evidence ids + missing inputs
- final route ∈ {DIRECT, INTERPOLATE, SIMULATE, QUALITATIVE, ASK, UNKNOWN}
- versions of all registries used

### 3.3 Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Use SBML/FSKX as the *internal* registry format | SBML core assumes well-mixed compartments and has no matrix/condition-applicability semantics beyond Constraints. FSKX domain = per-parameter box (F2.3) and quality = fit-only (F3.1). Heavy tooling (Java/KNIME) for a 2-person team. Keep as export only. |
| Per-parameter min/max box as the validated domain (FSK-ML/PMF-ML default) | Cannot detect empty regions or correlations (Sahigara 2012). MCP was introduced precisely for this (Baranyi 1996; Le Marc 2005). The box stays only as a baseline and a summary. |
| One scalar "applicability/confidence score" | Violates SSOT §241.3 (categorical before scalar) and brief §28 (no arbitrary confidence scalar). |
| Full OWL mechanism ontology with reasoner | No existing ontology covers food mechanisms (F4.1). Building one is scope creep. A flat registry + xrefs suffices for ≤40 mechanisms. |
| Adopt RXNO/GO as the mechanism backbone | Coverage gaps (no Maillard, acrylamide or gelatinisation process) and a label collision (Strecker reaction vs Strecker degradation). Use as xrefs only. |
| Atomically complete reaction network (RXN graph) as the Step 21–24 deliverable | SSOT G15-RXN (L22402) and MP W6 (L1689–1725, "never manufacture a balanced reaction"). Data are K0 endpoints only (step07_report: no trajectories). |
| LLM-judged mechanism applicability as authority | Permitted only as a CANDIDATE generator (E5/E6) feeding human verification. PROC mechanism links already show the AI-drafted-unverified risk. |
| Dense/semantic retrieval for parameter compatibility | Semantic similarity ≠ experimental compatibility (SSOT L25157). Structured hard filters + categorical vector first. A learned ranker only if labelled data justify it. |
| Pool/average parameters across studies to fill gaps | §211.38/§210.30. Use a hierarchical fit with uncertainty, or keep an ensemble/conflict. |

---

## 4. What each affected step must change/add (reconstructed scope; not card text)

**Step 21 — Effect/mechanism ontology → recommend KEEP + MODIFY (scope down; rename "mechanism & effect registry").**
- Inputs: SSOT §144.1/§144.3, MP L601/I3 worked examples, PROC.mechanism_families (as unverified candidates), SVAR registry, CV registry.
- Outputs: `MECH-` v1 schema + ≈20–40 entries; effect/target vocabulary (SVAR-linked, directions); xref table; `mechanism_registry_card.md`.
- Gate: every MECH has preconditions + ≥1 condition gate or an explicit "UNKNOWN gates" flag. Human domain review of ≥ all entries, recording kappa or adjudication. 0 xrefs accepted without verification.
- Metrics: coverage of §144.1 families; xref verification rate; Strecker-type collision count.
- Baseline: the current PROC mechanism_families list.
- Effort is small (days). It **can start in parallel with Phase C/D** because it needs no new data.
- Freeze the schema early (look-ahead, §5).

**Step 22 — Event → effect signatures → KEEP + MODIFY.**
- Separate deterministic changes (DERIVED_DETERMINISTIC) from candidate effects (E6, never evidence).
- Inputs: Step 16–18 event schema/state, MECH-, PROC/TOOL.
- Output: `EFFSIG-`.
- Baselines:
  - B0: process-label → mechanism_families lookup
  - B1: rule signatures with condition/precondition predicates
- Negative control: process-label permutation.
- Metric: precision/recall of candidate mechanisms vs an expert-labelled set of (event, entity) cases, built from MP I3 + SSOT §144.3 cells (alliinase on crushed garlic, PPO on cut apple, acrylamide in fried potato, chlorophyll→pheophytin with acid/heat, leaching vs degradation in boiling).

**Step 23 — Mechanism applicability engine → KEEP + MODIFY.**
- Three-valued gates + reason codes; competing-mechanism gate; input-observability gate; `APPDEC-` output.
- **Primary safety metric: false-activation rate** (APPLICABLE when the expert says not applicable or unknown). Also report UNKNOWN rate and recall on positive cases.
- Ablation: remove condition gates or preconditions → expect over-activation.
- Gate: false-activation ≤ a pre-registered threshold on human-labelled cases. The threshold is set before running. UNKNOWN never routes to SIMULATE.
- Diagnostic: on current EVD, expect ~100% UNKNOWN for pH/aw-gated mechanisms (step07_report). This is an *expected and correct* result. It is a data gap for Steps 11–14, not an engine failure.

**Step 24 — Formula/model registry → KEEP + MODIFY (substeps 24a MODEL schema, 24b PARAM, 24c VAL).**
- Populate only for the Step-26 candidate system(s) first (≈2–5 models, 10–50 PARAM rows).
- Lifecycle with REPRODUCED before CALIBRATED; MCP calibration domain; Constraint-style assumptions; KiSAO solver; Tref-Arrhenius.
- Resolve the `MODEL-` prefix collision with MP X6.
- Gate: every model that enters Step 26 has REPRODUCED status (reproduces a source figure/table within the stated tolerance), complete units/order consistency, a PARAM provenance locator, and a declared validated-domain plan (which held-out VAL data, study-disjoint via Step 08).
- Baseline models per SSOT §210.27 (zero/first-order/Weibull) before any multiresponse model.

**Step 25 — Parameter-compatibility retrieval → MODIFY; candidate MERGE-as-substep with 24** (it cannot run without PARAM). Keep the number for the spine.
- Architecture per F8.1.
- Baselines:
  - B0: exact (matrix, process, model) lookup
  - B1: rule-based categorical tiers + box domain
  - B2: B1 + MCP/kNN domain
  - B3 (optional): a learned ranker only if ≥ a few hundred labelled pairs exist
- Metrics: compatible@k precision; **harmful-mismatch rate**; coverage (queries with ≥1 compatible set); downstream error when retrieved params are used to predict held-out measurements vs a matrix-shuffled-parameter negative control.
- Leakage: a parameter set fitted on study S must not be used to "validate" on S (Step 08 lineage).

---

## 5. Look-ahead requirements for earlier steps

- **Step 03/04 (state/evidence contracts):**
  - Add state variables for history-dependent mechanisms: enzyme_activity_state, cell_integrity, time_since_disruption, cumulative thermal dose, oxygen_exposure, precursor concentration (SVAR-FUT-014 → active). All may be UNKNOWN.
  - Resolve the MODEL- prefix collision.
- **Step 07 (conditions):**
  - The vocabulary already exists (40 CVs incl. pH, aw, O2, enzyme/additive, ripeness). The *data* lack them (4,414/4,414 UNKNOWN pH/aw/moisture; 213 located temperatures; no trajectories).
  - Kinetic/applicability use requires **temperature location** (core/surface/medium) and trajectories. Steps 10–14 extraction must populate these fields.
  - The human condition audit (provenance-invalid) must pass before condition annotations gate Step 23.
- **Step 08 (lineage):**
  - Independence groups must also cover **parameter re-reporting**: reviews/handbooks re-tabulating the same k/Ea, the same lab across papers.
  - This is needed for Step 25 conflict handling and the Step 24c/27 study-disjoint validation.
- **Step 09 (extraction machinery):**
  - Must extract kinetic tables/figures to the SSOT §210.29/§211.50 fields: k, unit, order, A/Ea, Tref, CI, T list, time points, fit metric, matrix composition, measurement platform.
  - Figure digitisation is flagged DERIVED with a locator.
  - It must also capture design level K0–K4.
- **Step 10 (20-row mechanism pilot):**
  - Include ≥3–5 kinetic-parameter rows and ≥2 *negative/inhibited* cases (e.g. blanched → no PPO browning; acidified → chlorophyll conversion).
  - This exercises the MECH preconditions/inhibitors and the PARAM fields.
  - Record per-field reporting rates (how often papers give Tref, CI, aw, temperature location). These are the key unknowns for Step 24.
- **Steps 11/13/14 (acquisition):**
  - Target K1–K4 studies for the Step-26 system plus matrix-composition descriptors.
  - Hold out study-disjoint validation sets *before* any fitting.
  - ComBase (microbial) is useful only if a microbial mechanism is in scope; check its licence.
- **Step 12 (structured DBs):**
  - Candidates: BioModels BIOMD0000000052 (model-system Maillard SBML); SABIO-RK (enzyme kinetics, mostly non-food); USDA/Bognár retention (endpoints only, K0).
  - Licence of BioModels content: UNVERIFIED here.
- **Step 15 (freeze):** DATA-EVIDENCE v1 must include PARAM-bearing kinetic rows and a frozen VAL partition (study-disjoint).
- **Steps 16–18 (procedure/state):** The event schema must expose medium, covered/uncovered, cut type, rest time, acid/salt additions and setpoint vs. core temperature cues as explicit (possibly UNKNOWN) fields. Otherwise Step 22/23 inputs are always UNKNOWN.
- **Step 26–27:** consume MODEL/PARAM/VAL. Simulator outputs fill `simulated_state_changes_schema_v1` `validation_scope` from VAL- (validated domain), never from the calibration domain.

---

## 6. Residual uncertainty, and whether an empirical pilot is cheaper

Residual unknowns:
- (U1) How often food-kinetics papers report the fields the registry needs: Tref, CI, temperature location, aw/pH, matrix composition, raw time-series. **This is not answerable by more reading. A pilot is cheaper.**
- (U2) Whether MCP/kNN domains are estimable with the few design points typical of food studies (often 3–5 T × 4–6 t). MCP may collapse to a near-box. Test in the pilot.
- (U3) The FSK-ML guidance v3.1 text (BfR site unreachable). The schema YAML was opened, so the residual risk is low.
- (U4) Exact OECD 2007 guidance text (server refused). QMRF v1.2 is the authoritative proxy, so the residual risk is low.
- (U5) Licence of BioModels / ComBase content for redistribution: UNVERIFIED.
- (U6) The threshold for the Step-23 false-activation gate needs human pre-registration.

**Recommended pilot** (no data acquisition beyond Step 10/11 authorisation; ~1–2 person-days once authorised; CPU only):
- Take the Step-26 candidate system.
- Populate MECH (3–5), MODEL (2–3), PARAM (10–30) from 5–10 already-authorised papers.
- Run the compatibility rules on ~50 hand-built queries.
- Measure the field reporting rates, the box-vs-MCP difference and the UNKNOWN rate.

Further literature reading is unlikely to change the architecture (stop rule §8.1 + §8.5 met).

Confidence summary: architecture choice MEDIUM-HIGH; schema fields HIGH; ontology-gap finding MEDIUM-HIGH; data availability for PARAM MEDIUM (U1).
