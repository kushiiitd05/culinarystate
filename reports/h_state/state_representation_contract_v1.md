# State representation, variable, provenance, EVD, simulation and similarity contract v1 (MP-1)

Status: DRAFT FOR REVIEW. Contracts only: no training, scraping, simulation or ledger rewrite. Grounding read from the SSOT v15 file: 104-108, 113, 117 (profiles, factorised state, explicit vs latent, missing modalities), 141-144 (frozen transition architecture, mechanism families, cooking-chemistry data contract), 142 (similarity stack), 215.38 (gate system), 249, 279. Companion files: `registry/state_variable_registry_v1.csv`, `registry/evidence_tier_provenance_map_v1.csv`, `registry/provenance_class_registry_v1.csv`, `registry/evd_contract_v1.csv`, `registry/simulated_state_changes_schema_v1.csv`, `registry/ssot15_similarity_registry.csv`, `registry/human_verification_queue.csv`; `reports/h_state/transition_bootstrap_v0_contract.md`.
Correction to MP-0 (factual): the live EVD JSON Schema already contains nested `before`, `after`, `derived.{delta, percent_change, retention_factor, log_fold_change, yield_factor, direction}` and `matrix.{initial_state, prior_processing, geometry, storage_ripeness}`. The MP-0 "schema conflicts" are therefore mostly about **population** (delta and log_fold_change are empty in all rows) and about missing `provenance_class`, `matrix_id`, `prior_state_id`, explicit `lod/loq`, not missing nested structures.

## 1. Identities (never collapsed; SSOT AN1)
- **A. Ingredient identity** `ING-` : the canonical concept ("onion"). Immutable meaning; aliases in `ALIAS-`.
- **B. Entity / lot / version** `ENTITY-` / `STATE-` : this onion portion in this pan, and its version after each event. Append-only; a process creates a new version when appropriate; no old state is overwritten.
- **C. State** : the factorised S_{i,t} below, attached to an entity version.
- **D. Process** `PROC-` : canonical action family. A process name is not a chemical cause (SSOT 107.x, 141).
- **E. Conditions** `COND-` : full condition profile theta (time, temperature, pH, moisture, aw, pressure, oxygen, medium, geometry, agitation ...), each axis MEASURED / RANGE / UNKNOWN / NOT_APPLICABLE.
- **F. History** H_t : ordered prior events on the entity; explicit event list, not a latent summary.
- **G. Evidence** `EVD-`/`RXN-`/`SIM-` : every supported change references evidence ids with tier and provenance class.
- **H. Learned representations** z_m -> z_i -> z_R -> z_C and z_{i,t} : optional, derived, never a replacement for the explicit state (SSOT 106, 113).

## 2. Factorised explicit state (frozen; SSOT 106)
S_{i,t} = { C chemical/composition, P^phys physical, Y^sens sensory, N nutrition, Q quantity/mass, R procedural, X safety, U uncertainty/missingness/evidence metadata }
- SSOT 106 also lists V (visual), A (acoustic) observations and K (culinary context). Per SSOT 108 observations O_t are **evidence about** S_t, not part of it; V/A are Level-17 (optional) and are out of MP-1 scope. K is context carried by the recipe/event record, not a state variable.
- **Q (quantity/mass)** and **R (procedural form/cut/location/identity)** and **X (safety)** come from the master plan (B10, W3, AN); they are extensions beyond the SSOT 106 literal list and are marked as such in the registry.
- Never one embedding. Each profile keeps explicit variables with units, per-variable mask, evidence references, uncertainty. A fused latent z^state may exist later alongside, never instead (SSOT 113).

| Profile | Contents (registry families) | Current evidence in ledger |
|---|---|---|
| C chemical | named compound / nutrient content, precursor/product, pH/acidity, volatiles, oxidation markers, kinetic parameters | 223 SVARs (nutrient and phenolic content), E3 retention only; mechanism rows 0 |
| P^phys | moisture, aw, mass/yield, volume, density, phase, viscosity, texture, colour L*a*b*, particle size, microstructure, temperature profile | 1 SVAR (food mass/yield, 496 Bognar rows) |
| Y^sens | descriptors, intensity, threshold/OAV | none (sensory only when evidenced; never LLM-filled) |
| N nutrition | nutrient content per serving/100 g | overlaps C nutrient SVARs (USDA/Bognar) |
| Q quantity/mass | mass/volume/count intervals with Q-level | engine symbolic quantities; QNT/POR ledgers 0 rows |
| R procedural | form, cut, location, intermediate identity, cooked/raw/fermented | Gold events (20 recipes) and engine |
| X safety | pathogen-control, allergen/cross-contact, hazard marker | ALLERGEN 8 records; authority sources only |
| U | per-variable mask, uncertainty, tier, provenance, extrapolation flag | EVD fields exist |

## 3. State variable record (every variable in `registry/state_variable_registry_v1.csv`)
state_variable_id, name, family, subfamily, definition, datatype, unit, before_allowed, after_allowed, delta_allowed, direction_allowed, retention_allowed, logfold_allowed, measurement_family, gold_eligible, simulation_eligible, evidence_required, current_row_count, current_evidence_tiers, current_coverage_status, SSOT_source, status (+ canonical_variable_id, n_distinct_process_signatures, source_families, notes).
Registry result (254 rows): ACTIVE 59, PROVISIONAL 73, MISSING_EVIDENCE 81, DUPLICATE 11, FUTURE 30, DEPRECATED 0, SIMULATION_ONLY 0. Rules (fixed before looking at benchmark needs): ACTIVE = >=50 active EVD rows, >=3 process signatures, single analyte; PROVISIONAL = 10-49 rows or aggregate; MISSING_EVIDENCE = <10 rows; DUPLICATE = same normalised analyte as a lower-id variable (11 pairs, e.g. Calcium content vs Calcium, Ca content; EVD is **not** rewritten until the MP-5A migration); FUTURE = SSOT/W3-defined variables with no ledger record. Folate/Vitamin C/Naringenin variants with different definitions are **not** merged; they carry an "equivalent-candidate" note for human/analytical review.
FUTURE rows come only from SSOT 105-107 profile lists and the master-plan W3 registry (30 variables across physical, chemical, sensory, procedural, safety). Their ids (`SVAR-FUT-###`) are provisional.

## 4. UNKNOWN, missingness and before/after/delta semantics
- UNKNOWN is a first-class value for every variable, condition axis and evidence field; it is never 0, never an LLM guess labelled data (SSOT 117).
- Censoring: non-detects and capped values are censored observations (`censor` object / `censoring_flag`), carried through every metric; never imputed to a bound as truth.
- A row may legitimately carry only `retention_fraction`; `before/after/delta` stay UNKNOWN. `delta` and `log_fold_change` are derived (provenance DERIVED_DETERMINISTIC) only where inputs are MEASURED and eligible; `log_fold_change` requires strictly positive values and is never computed from censored retention.
- Basis (fresh weight, dry weight, per volume, true vs apparent retention) is part of the value; no silent cross-basis pooling.
- Yield is a mass-profile target of its own (SVAR food mass); a yield factor attached to a concentration row (Phenol-Explorer) is a covariate from a separate yield source, not an independent observation.

## 5. Frozen representation levels
OUTER: cuisine/culture -> recipe -> process/event -> ingredient entity -> ingredient state -> state profiles -> ingredient molecule-set -> molecule -> scaffold/functional group -> atom environment -> atom/bond/reaction center :INNER. Reaction-center level is DATA-MISSING / RESEARCH-REQUIRED (RXN 0 rows).
Learned path (separate): z_m -> z_i -> z_R -> z_C. Dynamic mapping (separate): (S_t, P_t, theta_t, H_t) -> Delta S -> S_t+1, with Delta S = [Delta C, Delta P^phys, Delta Y^sens, Delta N, ...] per profile (SSOT 107); only supported variables are updated; the rest stay UNKNOWN. Frozen output contract (SSOT 141): each proposed transition is `unsupported`, `physically_possible`, or `evidence_supported`; numeric yield only from measured change or a calibrated model with initial conditions.

## 6. Evidence tier vs provenance class (kept separate)
- **Tier** answers "how strong is the scientific evidence": E1 controlled experiment with measured conditions; E2 experiment with partial conditions; E3 database aggregate; E4 structured/LLM extraction **human verified**; E5 extraction unverified; E6 mechanism rule / MODEL_ESTIMATED; E7 SIMULATED.
- **Provenance class** answers "where did this value come from": EXPLICIT_SOURCE, EXTERNAL_VERIFIED, DERIVED_DETERMINISTIC, INFERRED_LLM, MODEL_ESTIMATED, IMPUTED, SIMULATED, UNKNOWN (`registry/provenance_class_registry_v1.csv`).
- Primary evaluation eligibility: **E1-E4 only**. E5-E7 never become Gold truth. Held-out test and calibration labels additionally need human verification (G14-3, G15-H), so no E3 row is Gold until verified. E5 -> E4 promotion requires human verification against the cited source span/table; an LLM output that looks plausible is never promoted.
- Current state: all 17,978 rows are E3 / EXPLICIT_SOURCE (with derived fields DERIVED_DETERMINISTIC); verification: 14,108 UNVERIFIED, 3,870 AI_PRECHECKED, 0 human-verified.

## 7. EVD contract (`registry/evd_contract_v1.csv`)
Conceptual fields as requested map to existing ledger fields; additions in an **export view** (no ledger rewrite): `provenance_class`, `matrix_id` (hash of normalised matrix object), `prior_state_id` (controlled vocabulary, MP-5A), explicit `lod/loq`, deterministic `delta`/`log_fold_change` where legitimate. Not every row populates every representation; absent stays absent. Population today: ingredient_id 64%, process_id 99%, condition_id 100%, temperature known 33%, duration known 17%, moisture/pH/aw 0%.

## 8. Simulation contract (schema only: `registry/simulated_state_changes_schema_v1.csv`)
Simulated rows: provenance_class = SIMULATED, tier = E7, `may_enter_gold_evaluation` = false, simulator id/version/parameters/uncertainty/validation scope mandatory, `extrapolation_flag` outside the validated scope. **Eligibility is per validated simulator, not per variable family:** physical variables (temperature profile, moisture/mass transfer, geometry) are *potentially* simulation-eligible; chemical, sensory, nutrition, safety variables are NOT_BY_DEFAULT; a simulator may populate only variables listed in its declared validation scope; it never invents chemical products, sensory outcomes, nutrient changes or reaction mechanisms outside that scope. Simulation data are treated as MISSING (no `simulated_state_changes.csv` exists; no path confirmed). Reconciliation with `docs/simulator_data_contract.md` (`source_class`): STRUCTURAL_RECIPE -> R (procedural) only, never a magnitude; COMPOSITION -> C/N composition, E3; MEASURED_TRANSITION -> E1/E2/E4; COMPILED_RETENTION -> E3; KINETIC -> E1/E2/E4 if fitted to measured data with uncertainty; MOLECULAR_PRIOR / SENSORY_PRIOR / MODEL_GENERATED -> E6; SYNTHETIC -> E7.

## 9. Similarity (`registry/ssot15_similarity_registry.csv`, FROZEN v1, 21 types)
Structural chain: exact identity -> shared-compound overlap -> normalised overlap -> ECFP radius 0 / 1 / 2 (frozen baseline fingerprint: Morgan r2, 2048-bit, chirality on, binary Tanimoto, Dice excluded) / 3 -> fingerprint-family sensitivity -> scaffold/functional-group/class -> ingredient molecule-set -> state-dependent composition -> process-conditioned change -> reaction-center similarity (DATA-MISSING / RESEARCH-REQUIRED). Separate spaces, never derived from the chain: learned chemical, sensory, nutritional, functional/culinary-role, substitution fitness, cultural/co-occurrence, recipe, cuisine. Each type records OBJECT_A, OBJECT_B, REPRESENTATION, METRIC, REQUIRED_DATA, CONFOUNDS, BASELINE, GOLD_REQUIREMENT, CURRENT_STATUS.

## 10. Open contract conflicts (need a ruling)
- **C1 Tier ladder mixes two axes.** E1/E2 are design strengths; E4/E5 are verification states. A human-verified controlled experiment fits both E1 and E4. Proposed rule: E1/E2 are assigned only to human-verified extractions (or database rows with documented design) whose design supports it; E4 = human-verified extraction whose design/conditions are insufficient for E1/E2; E5 = any unverified extraction regardless of design; `design` and `verification.status` stay separate fields. Needs your decision.
- **C2 Gold eligibility of E3.** Tiers E1-E4 may enter evaluation sets, but G14-3/G15-H require human-verified held-out labels. Proposal: E3 rows may train and form a *Bootstrap* benchmark labelled "unverified"; nothing is called Gold until verified.
- **C3 Duplicate SVARs.** 11 duplicate pairs affect EVD references; resolved only in the MP-5A migration (mapping table, no overwrite).
- **C4 Retention semantics.** USDA R6 mixes %TR and %AR (not disclosed at row level) and imputes from similar foods; Bognar is true retention with ~50% censoring. Basis must be a covariate; do not pool as one target without a flag.
- **C5 PE yield.** 3,870 PE rows carry an attached yield factor from separate yield sources (103 distinct yield records); not independent of the retention rows.
- **C6 Naming.** `tier` vs `evidence_tier` (alias in export), `origin_type` vs `provenance_class` (new field).
- **C7 AI-drafted fields.** PROC mechanism families (93) and some link decisions are AI-drafted and unverified; they may not gate any claim until HV-010.
- **C8 Profiles beyond SSOT 106.** Q, R, X profiles are extensions from W3/AN/B10, flagged in the registry.
