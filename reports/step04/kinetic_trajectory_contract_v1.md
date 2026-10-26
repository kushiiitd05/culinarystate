# Step 04.3 — Kinetic / trajectory contract v1 (KIN, KINPT)

**Status: DRAFT_PENDING_H4.** Written 2026-10-26 under D-027 / Plan v2 §7: contract and documentation only. Not approved, not frozen, no ledger created, no data touched. Numeric values are PROPOSED_PILOT (`registry/preregistered_thresholds_v1.csv`, unsigned).

**Revision r1 (2026-10-26, still DRAFT_PENDING_H4):** governance review A and scientific review B applied. Main changes: raw time units week / month / year are preserved (normalised seconds are a separate field with a conversion status); unknown read uncertainties are spelled UNKNOWN instead of forced to a number; the KIN mandate moves from ≥ 3 to ≥ 2 distinct numeric times (PROPOSED_PILOT edit, THR-04K-01; ≥ 3 stays the K1 label, THR-04K-02); value scale / C0 semantics, temperature profiles with clock tags and isothermality, companion series and mass-balance sets, replicate run ids, τ status / range, richer fit records and a mandatory lab group are added; the record-level R-04 guard `OBS.series_link` is added. Every change is PROPOSED with an H4 item in §14.

Authority: **R-04** — the kinetic/trajectory schema exists before Steps 09 and 11, and time series are never flattened into endpoint-only EVD rows. Owner: Step 04.3 (X2: 04.3 owns the single field list; Step 09 implements extraction; Steps 24/25 reference it). 04.3 is HARD for the Step-09 schema freeze and for Steps 10/11; it is **not** a precondition of 08a. Clock vocabulary comes from 03.3 (pending); until 03.3 is approved only `PROCESS_TAU` is admitted (Step 03 card, fail action).

Drafts: `registry/schemas/KIN.draft_v1.schema.json`, `registry/schemas/KINPT.draft_v1.schema.json` (draft 2020-12, same envelope and style as `ledgers/schemas/*`). Companion: `lineage_contract_v1_1.md` (entity chain, keys, leakage rules), `04_2_min_value_documentation.md` (OBS value block), `04_6_min_data_plane_rules.md` (FW-15).

Research basis: `reports/master_plan/working_notes/research/r_simulator_vv.md` (RV), `r_acquisition.md` (RA), `r_evidence_model.md` (RE); SSOT §210.28–29, §211.48, §211.50, §216.2.

---

## 1. Why this exists, and what it guarantees

The ledger is endpoint-only: EVD holds before / after / delta / retention / yield and no time-series or kinetic-experiment table (RA §2.0, §5). Without a series table Step 11 would flatten series into endpoints and Steps 24, 26, 27 and 32 would lose their inputs (RA: "the single most important look-ahead finding"). Today the repo holds **no** trajectory evidence able to calibrate or validate a cooking simulator: USDA R6 / Bognár vitamin rows are K0 aggregates with duration and temperature almost always UNKNOWN, and Phenol-Explorer has K1 series mostly for storage (RV §0, Q2). Every candidate simulator therefore needs K1/K2 series acquired in Steps 10–14.

The contract guarantees:

1. a time series is stored as **one KIN header + one KINPT per (time, replicate)**, each KINPT pointing to exactly one OBS that holds the measured value with its unit, basis, censoring, dispersion and n;
2. raw time points are **never discarded** (SSOT §216.2 last line) and never replaced by a fitted parameter or an endpoint;
3. an endpoint or retention value derived from a series is a **DRV with the series as parent** (§5), never a stand-alone endpoint row;
4. no kinetic or Arrhenius parameter is derived from `food + process + RF` aggregates lacking time/temperature (SSOT §211.48, FW-15);
5. fits stored here are **AUTHOR_REPORTED** only; project fits live in the model plane (FW-14);
6. raw is preserved and normalisation is a new field: a time keeps its printed unit (week / month / year included; calendar durations are never converted in this record, 07H-R) and its normalised seconds live in a separate field with a conversion status; an unknown digitisation uncertainty is UNKNOWN, never a number and never 0.

---

## 2. Objects and cardinalities

```
SEXP 1──* KIN 1──* KINPT 1──1 OBS ──* (via SMP) …
KIN.condition_profile.condition_grid_id  groups the KIN of one T x t grid (K2)
KIN ──(parent)──> DRV (ENDPOINT_FROM_SERIES)    EVD export-v2 row ──(series_link)──> KIN/KINPT
```

- `kinetic_experiment_id` of SSOT §216.2 **is the `sexp_id`** (Step 04 card). One SEXP may own several KIN (one per target × compartment × temperature schedule); the series id is the `KIN-` id. (Ambiguity A-1 in §14: SSOT calls the table row an "experiment/series row".)
- A KIN needs **≥ 2 distinct numeric times** (`n_timepoints ≥ 2`, schema) and is **mandatory** whenever the source reports **≥ 2 distinct numeric times** (the reference point counts when it has a numeric τ) for one (SEXP, target, compartment, matrix, temperature profile) — PROPOSED_PILOT THR-04K-01, an edit of the first agent draft (which said ≥ 3; the card fixes no number). Reason (review B #10): a ≥ 3 mandate would leave multi-temperature × single-time designs (C0 + C(t) at ≥ 2 T) as endpoint pairs although they are informative for Arrhenius and are valid blind-prediction targets for Step 27 HV-1 / HV-2 and Step 32, would skew the pool toward long time-course labs, and was enforced on the extractor's own count. Such designs are stored as **n_timepoints = 2 KIN sharing one `condition_grid_id`**. **≥ 3 distinct times at one temperature remains only the K1 classifier label** (THR-04K-02, §8). Legacy rows without any time (USDA R6, Bognár) stay endpoint AGG: no numeric τ, no KIN. The rule depends only on source structure, never on outcomes. R04-1 is verified by the second extractor / adjudicator on the Step-09 dual-extraction sample (THR-04K-04), not by extractor self-report.
- One KINPT = one (series, τ, replicate). If the source reports only a mean ± dispersion at a time, the KINPT is `AGGREGATED_OVER_REPLICATES`; if it reports individual replicate values, each is its own KINPT with `INDIVIDUAL_REPLICATE` and an index.

---

## 3. KIN header (`KIN.draft_v1.schema.json`)

| Field | Content / rule |
|---|---|
| envelope | `id` (`KIN-######`), `record_type`, `version`, `status`, `provenance`, `verification` … identical to every ledger |
| `sexp_id` | the experiment (= SSOT `kinetic_experiment_id`) |
| `series_label_raw`, `series_origin_form` | verbatim label; TABLE / FIGURE_DIGITIZED / MIXED_TABLE_AND_FIGURE / TEXT / SUPPLEMENT_FILE / DATABASE / UNKNOWN. FIGURE and MIXED require `provenance.locator` |
| `target` | `state_variable_id` (SVAR), `analyte_raw_name`, `molecule_id`, **`analyte_form`** (STATED / NOT_REPORTED / UNKNOWN, e.g. AA vs AA + DHA, RV §5.3), **`compartment`** (TISSUE / COOKING_MEDIUM / WHOLE_SYSTEM / NOT_APPLICABLE / UNKNOWN — needed to separate leaching from degradation, RV Q1), `basis_id` (MB-), `basis_raw`, **`value_scale`** (ABSOLUTE / RELATIVE_TO_C0 / PERCENT_OF_C0 / LN_RELATIVE / LOG10_RELATIVE / OTHER / UNKNOWN), **`c0_reference`** (T0_SAMPLE / RAW_REFERENCE_SAMPLE / AUTHOR_FITTED_C0 / NOT_REPORTED / UNKNOWN), **`c0_obs_id`** (the OBS that holds C0; required for the first two, null otherwise) |
| `matrix`, `process`, `reference_sample_id` | same facets as EVD.matrix / EVD.process; the t = 0 / untreated sample |
| `condition_profile` | `condition_grid_id` (`CGRID-######`, groups the series of one grid; `grid_role`), `condition_ids` + `condition_status`, `normalizer_fingerprint_12` (frozen 07H-R normaliser, so a later 07H.v2 can re-normalise from raw), `temperature_status` + `temperature_profiles[]`, `isothermality`, `initial_conditions` |
| `temperature_profiles[]` | ONE curve per element: **`location`** (SETPOINT / MEDIUM / SURFACE / CORE / AMBIENT / UNSPECIFIED — UNSPECIFIED is never promoted to a real location), **`clock`** (PROCESS_TAU), `schedule_type` (ISOTHERMAL / NON_ISOTHERMAL_PROGRAM / UNKNOWN), `derivation` (AS_REPORTED / DIGITIZED / ESTIMATED_FROM_SUMMARY / UNKNOWN), `uncertainty` (typed dispersion), `isothermal_value` (raw value + unit, required if ISOTHERMAL), `points[]` (≥ 2 if a programme; each point has `tau`, `tau_unit`, `tau_unit_raw`, `tau_seconds` and `T`), `raw_text`, `condition_id` (normalised value lives in COND). A medium profile and a core profile are **two elements**, never one curve with mixed per-point locations. `temperature_status` REPORTED needs ≥ 1 profile; NOT_REPORTED / UNKNOWN keep the list empty (no fake UNSPECIFIED profile) |
| `isothermality` | PRODUCT_ISOTHERMAL_STATED / SETPOINT_ONLY / COME_UP_SIGNIFICANT / NON_ISOTHERMAL / UNKNOWN. A SETPOINT is not product isothermality; Arrhenius on a setpoint with a significant come-up time biases Ea. **Arrhenius-eligible** (Steps 24 / 26 / 32) only with a MEDIUM / CORE / SURFACE profile, or PRODUCT_ISOTHERMAL_STATED, or the come-up time EXCLUDED and stated |
| `initial_conditions` | `status` (REPORTED / PARTIAL / NOT_REPORTED / UNKNOWN) + initial concentration, pH, moisture (each an UNKNOWN-aware value). `initial_concentration` must equal the value of `target.c0_obs_id` or be null (semantic check: C0 is stored once) |
| `time_base` | `clock` (PROCESS_TAU only for now), `unit` (s / min / h / d / **week / month / year / OTHER** / UNKNOWN; month and year are calendar durations, stored raw) + `unit_raw` (printed label; mandatory for OTHER), `t0_definition` (START_OF_HEATING / TARGET_TEMPERATURE_REACHED / START_OF_STORAGE / START_OF_CONTACT_WITH_MEDIUM / NOT_REPORTED / UNKNOWN), `come_up_time` (INCLUDED_IN_TIME / EXCLUDED_FROM_TIME / NOT_REPORTED / UNKNOWN) |
| `n_timepoints` | integer ≥ 2; must equal the number of distinct numeric τ over the KIN's KINPT (semantic check) |
| `replicate_structure` | design (INDEPENDENT_UNITS_PER_TIMEPOINT / REPEATED_MEASURES_SAME_UNITS / POOLED_SAMPLE_PER_TIMEPOINT / UNKNOWN), `n_biological_per_timepoint`, `n_technical_per_unit` (counts with status, never 0 or a default 1), `reporting` (PER_REPLICATE_VALUES / MEAN_WITH_DISPERSION / MEAN_ONLY / UNKNOWN) |
| `companion_status`, `companion_series[]`, `mass_balance_set_id` | Leaching and degradation cannot be separated without the other half of the run. `companion_series[]` = {`kin_id`, `role` ∈ COOKING_MEDIUM_CONC / FOOD_MASS_OR_YIELD / MEDIUM_VOLUME / MOISTURE / PRODUCT_TEMPERATURE / DEGRADATION_PRODUCT / OTHER_ANALYTE_FORM / OTHER}; `mass_balance_set_id` (`MBSET-######`, proposed prefix) groups the series of one run for the Step 26c mass-balance check and k_L identifiability. Pairing rule: KINPT of companion series at the same τ point to OBS on the **same SMP** (cooking medium is SMP role COOKING_MEDIUM) or carry `paired_kinpt_ids`. Water / food mass and volume time courses matter because evaporation changes concentration |
| `context_override` | optional per-series override of `SEXP.context` (water:food ratio, lid, start mode … can differ between the series of one experiment); absent key = inherits the SEXP value |
| `censoring_summary` | `any_censored` YES / NO / UNKNOWN, `kinds_present[]`, method-level `lod` / `loq`. The per-point truth is `OBS.censoring` (TRACE_BETWEEN_LOD_LOQ is a valid kind) |
| `method` | method / platform reference (MEAS- + raw wording) |
| `k_level` | `value` K0–K4 / UNKNOWN, `scope` (SERIES_ONLY / CONDITION_GRID / SEXP_ALL_SERIES / UNKNOWN), `classifier_version` (§8) |
| `fit[]` | author-reported fits (§9) |
| `evidence_tier` | E1–E5 only (E6/E7 are model/simulation planes). E1, E2, E4 require `verification.status = HUMAN_VERIFIED` (schema); LLM-extracted unverified = E5 |
| `locator` | DOC + table / figure / span of the series, with verbatim `raw_text` |
| `lineage` | cached keys `study_id`, `lineage_root_id`, `split_group_id` (SPLITGRP-EVD- only), `independence_resolution`, `assignment_status`, `rule_version` (see `lineage_contract_v1_1.md` §4) and, **mandatory on the kinetic plane**, `lab_group_id` (`LABGRP-######`) + `lab_group_status` (ASSIGNED / PENDING / UNKNOWN) + `lab_group_basis`; nesting `split_group` ⊆ `lab_group`. UNKNOWN (authorship not read) makes the series not SIM-VAL / DS-TEST eligible |
| `licence_status`, `storage_rule`, `extraction_version`, `extraction_record_ids` | per-row licence status; Step-09 XTR links |
| mint key | `<sexp_id>\|<state_variable_id>\|<compartment>\|<temperature profile key>\|<locator key>` — idempotent: re-extraction of the same series does not mint a duplicate (review B #30) |

## 4. KINPT (`KINPT.draft_v1.schema.json`)

| Field | Content / rule |
|---|---|
| envelope | `id` (`KINPT-######`) … |
| `kin_id`, `sequence_index` | parent series; order as printed in the source (stable, ≥ 0) |
| `tau` | `clock` (**required**; PROCESS_TAU), `status` (REPORTED / RANGE / DEFINITIONAL_ZERO / NOT_APPLICABLE_REFERENCE), `value` (null unless REPORTED or DEFINITIONAL_ZERO, which is exactly 0), `low` / `high` (RANGE: "10–12 min" is stored as an interval), `unit` (s / min / h / d / week / month / year / OTHER / UNKNOWN) + `unit_raw` (printed label; mandatory for OTHER), `derivation` (AS_REPORTED / DIGITIZED / ESTIMATED_FROM_SUMMARY), `uncertainty` (number > 0 or null), `uncertainty_unit`, `uncertainty_type` (HALF_WIDTH / SD / AXIS_RESOLUTION / UNKNOWN), `uncertainty_status` (READ_FROM_TOOL / ESTIMATED_BY_READER / UNKNOWN; **required when DIGITIZED**; UNKNOWN is a valid answer and keeps the number null — never forced to a number, never 0), `normalised_seconds` {`status` NOT_CONVERTED / CONVERTED_EXACT / CONVERTED_BY_STATED_CONVENTION / NOT_CONVERTIBLE / UNKNOWN, `value`, `convention`}. Raw value + raw unit are never rewritten; seconds are a SEPARATE field. week = 7 d converts exactly; **month and year are calendar durations and are never CONVERTED_EXACT** (convention text mandatory if converted at all, e.g. "1 month = 30 d"). An untreated reference sample with no defined τ is NOT_APPLICABLE_REFERENCE, not a fabricated 0. Rule: a time field without a clock tag is rejected (03.3) |
| `point_role` | INITIAL / INTERMEDIATE / FINAL / UNKNOWN (used when an endpoint is derived, §5) |
| `replicate` | `status` INDIVIDUAL_REPLICATE (+ index ≥ 1) / AGGREGATED_OVER_REPLICATES / UNKNOWN; **`unit_label`** (label of the experimental unit, stable across τ; required by the semantic validator when the series design is REPEATED_MEASURES_SAME_UNITS — within-unit correlation cannot be modelled otherwise); **`run_status`** (SINGLE_RUN / REPLICATE_RUNS / NOT_REPORTED / UNKNOWN) + **`run_id`** (separates independent replicate RUNS of the whole series from replicate samples at one time point; the hierarchical fits of Steps 26 / 32 need both). Mint key `<kin_id>\|<sequence_index>\|<run_id or SINGLE>\|<unit_label or AGG>` |
| `obs_id` | **exactly one OBS**: value, unit, basis, censoring (+ LOD/LOQ), dispersion type and value, n, method, locator, `value_origin` (DIGITIZED requires tool / version / uncertainty status and axis scale on the OBS; DEFINITIONAL_NORMALISATION marks a t0 = 1 point of a relative-scale series, which fitting code excludes as an observation) |
| `paired_kinpt_ids` | KINPT of companion series (tissue vs cooking medium, mass / yield) at the same τ of the same run, when the two OBS do not sit on the same SMP |
| `temperature_at_point` | SAME_AS_PROFILE / MEASURED_AT_POINT (value + location) / NOT_REPORTED / UNKNOWN — product temperature when the source measured it |
| `digitized` | YES (tool + version required) / NO / UNKNOWN; must mirror `OBS.value_origin = DIGITIZED` or a digitised τ (semantic check) |

---

## 5. How an endpoint EVD row links to its series

| Situation | Storage | `series_link.status` on the EVD export-v2 row |
|---|---|---|
| Source reports a series (≥ 2 distinct numeric τ, THR-04K-01) | KIN + KINPT + OBS are created **first**. An endpoint / retention value is a **DRV** with `derived_quantity = ENDPOINT_FROM_SERIES`, `parent_ids ⊇ {KIN, the chosen KINPT ids}` (schema: at least one KIN/KINPT parent), `parent_roles` SERIES / SERIES_POINT, a `formula_id` stating which point is the endpoint (INITIAL / FINAL / at τ*). | `LINKED`, `kin_id`, `kinpt_ids[]` |
| Source reports one time per cell (a before/after pair without a numeric duration, or a single endpoint) | two OBS (REFERENCE_BEFORE, TREATED_AFTER); derived retention as DRV if computed by us. The extractor asserts that the source has no second numeric time for this cell; the assertion is checked by the second extractor / adjudicator (THR-04K-04), not self-certified. | `ENDPOINT_ONLY_SOURCE` |
| Source has a series that was not extracted (triage, E5 candidate) | candidate row only; flagged. Excluded from kinetic uses **and** from any statement that the source shows no time dependence. No code path promotes it to E4. `UNKNOWN` is treated exactly like `SERIES_NOT_EXTRACTED` for these exclusions. | `SERIES_NOT_EXTRACTED` |
| Legacy rows (17,978) | USDA R6 and Bognár are K0 aggregates by construction (retention only, no T/t): `ENDPOINT_ONLY_SOURCE`. Phenol-Explorer rows: the underlying papers may contain series; this is not knowable without the papers: `UNKNOWN`. | as listed |

The record-level guard is now on **OBS**: `OBS.series_link{status ∈ LINKED_KINPT, ENDPOINT_ONLY_SOURCE, SERIES_NOT_EXTRACTED, UNKNOWN; kinpt_id}` (mirror of `KINPT.obs_id`, semantic check) — so a series stored only as SMP/OBS pairs without a KIN is no longer undetectable by the schema (review A F12). The richer `series_link{status, kin_id, kinpt_ids[]}` stays a proposed addition to the EVD export-v2 row (lineage contract, Appendix A); no export-v2 schema is drafted in this step.

Later extraction (review B #32): when a KIN is minted for a STUDY / cell whose legacy endpoint row has `series_link = UNKNOWN` or SERIES_NOT_EXTRACTED, the legacy OBS gets a new version with `LINKED_KINPT`, or is superseded by the ENDPOINT_FROM_SERIES DRV; a validator never lets both be active as independent rows.

Consequences: the endpoint never replaces the series; the series is retrievable from any endpoint row by `kin_id`; deprecating a KIN requires new versions of every dependent DRV (append-only); one endpoint DRV is unique per (KIN, endpoint definition) by its mint key. Lineage: a DRV and its KIN parent are one split group (L-07), so the endpoint and the series can never straddle train and test.

---

## 6. Rules R04-1 … R04-16 and where each is enforced

| # | Rule | Source | Enforced by |
|---|---|---|---|
| R04-1 | A source reporting ≥ 2 distinct numeric times for one cell must produce a KIN; an endpoint-only row for such a cell is rejected. Verified by the second extractor / adjudicator, not by extractor self-report. | R-04; THR-04K-01, THR-04K-04 | Step-09 validator + dual-extraction sample; G09-6; record-level hint `OBS.series_link` |
| R04-2 | Raw KINPT are never deleted, merged or replaced by fits or endpoints. | SSOT §216.2; FW-15 | append-only ledger; validator |
| R04-3 | Endpoint rows derived from a series are DRV with the KIN as parent. | R-04 | `DRV.draft` rule (`ENDPOINT_FROM_SERIES` needs KIN/KINPT parent) |
| R04-4 | No kinetic / Arrhenius parameter from AGG rows or any `food + process + RF` without time / temperature. | SSOT §211.48; FW-15 | KIN has no AGG parent; Step-24 PARAM validator ("Arrhenius fit on USDA RF rows → reject") |
| R04-5 | Every τ — **including every temperature-profile point** — carries a clock tag and a unit; the unit is kept raw (week / month / year / OTHER admitted; month and year are calendar durations, never converted in this record, 07H-R); unit UNKNOWN is allowed and makes the series unusable for fitting, not invisible. | 03.3; 07H-R | `KINPT.tau`, `KIN.time_base`, `temperature_profile` (clock) and its points (`tau_unit`, `tau_unit_raw`, `tau_seconds`) |
| R04-6 | Temperature has a location tag; UNSPECIFIED is never promoted; medium vs core is not merged (two profiles). A setpoint is not product isothermality. | COND (ML-001..006); RV U3 | `temperature_profiles[].location`, `isothermality` |
| R04-7 | DIGITIZED values carry tool, version, an uncertainty status (a number > 0 or explicitly UNKNOWN), axis scale and calibration points on the OBS, and the read uncertainty status on τ; an unknown uncertainty is never forced to a number or to 0; never silently merged with tabular values. Two independent reads are required for TEST / SIM-VAL eligibility (THR-04K-03). | SSOT §257A.5; FW-15 | OBS `digitization` / KINPT `tau` rules; series flagged MIXED |
| R04-8 | Analyte form / basis (AA vs AA + DHA; chlorophyll a/b vs −a\*; wet / dry / initial basis; yield) and compartment are recorded. | RV §5.3 | `target.analyte_form`, `compartment`, `basis_id` |
| R04-9 | Censored points stay censored (kind, limit, LOD / LOQ); no substitution by a bound. | SSOT L19291; EFSA / Hwang (RE Q4) | `OBS.censoring` |
| R04-10 | Replicate design is stated, never assumed; the experimental unit label is stable across τ and independent runs have a run id. | RE Q4 | `replicate_structure`, `KINPT.replicate` |
| R04-11 | Optional experiment context (water:food ratio, cooking-water assay, lid, start mode, O2 / headspace, pH tissue vs medium, open vs sealed) is held on the SEXP, overridable per series (`KIN.context_override`); an absent key means UNKNOWN (not assessed) and NOT_REPORTED must be written explicitly by an extractor that read the source (the plan card says "default NOT_REPORTED": H4 item A-12). | Step 09 card; RV §5 | `SEXP.context`, `KIN.context_override` |
| R04-12 | Fits stored in KIN are AUTHOR_REPORTED; PROJECT_FIT is excluded from the evidence plane. | FW-14 | `KIN.fit[].fit_origin` enum |
| R04-13 | Series printed on a relative scale (C/C0, % of initial, ln or log10 of C/C0) declare `target.value_scale` and the C0 source; their t0 = 1 point is DEFINITIONAL_NORMALISATION and is excluded as an observation by fitting code (fitting it as data with zero error biases k and the intercept); log-axis digitisation errors are multiplicative. | review B #11 | `KIN.target`, `OBS.value_origin`, `OBS.digitization.axis_scale_*` |
| R04-14 | Tissue and cooking-medium series, food mass / yield, medium volume and moisture of one run are linked (`companion_series[]`, `mass_balance_set_id`) so the mass-balance check and k_L identifiability are possible. | review B #13; Plan Step 26c | `KIN`, `KINPT.paired_kinpt_ids` |
| R04-15 | A series is Arrhenius-eligible only with a MEDIUM / CORE / SURFACE temperature profile, or PRODUCT_ISOTHERMAL_STATED, or the come-up time EXCLUDED and stated. | review B #12 | `condition_profile.isothermality`, `time_base.come_up_time` (Steps 24 / 26 / 32) |
| R04-16 | A series-level fit or Arrhenius parameter states the series it used (`input_kin_ids`, covering the whole condition grid for grid-level fits), its model level, fitting method, number of points, temperature basis and parameter covariance, so that Step 24 can check it against SIM-VAL. | review B #17 | `KIN.fit[]` |

---

## 7. Crosswalk: the SSOT field lists this contract unifies

| SSOT §210.29 | §211.50 minimal kinetic report | §216.2 kinetic-experiment table | Here |
|---|---|---|---|
| kinetic_family | equation | candidate_model_family | `fit[].candidate_model_family`, `equation_raw` |
| reaction_order | — | — | `candidate_model_family` (ZERO / FIRST / SECOND_ORDER …) + parameter `name` |
| k_value, k_unit, A, Ea, Ea_unit | parameter estimates, units | fitted_parameters, parameter_units | `fit[].parameters[]` (value object carries unit) |
| parameter_CI | confidence intervals | parameter_uncertainty | `fit[].parameters[].uncertainty` (typed dispersion) |
| fit_metric | residual diagnostics | fit_diagnostics | `fit[].fit_diagnostics[]` |
| temperature_points, time_points | number of time points, number of temperatures | temperature_schedule, timepoints | `temperature_profiles[]`, `n_timepoints`, KINPT; number of temperatures = distinct isothermal values over a `condition_grid_id` (derived) |
| initial_conditions | conditions | initial_conditions | `condition_profile.initial_conditions` |
| matrix, process, target | food/matrix, process, target | food_matrix, process, target | same names |
| mechanistic_scope, effective_or_mechanistic | effective vs mechanistic | — | `fit[].effective_or_mechanistic` |
| — | identifiability note | identifiability_status | `fit[].identifiability_status` |
| — | held-out evaluation | — | **not stored here**: model-plane result (Steps 26/27) |
| source, verified | source / provenance | source, evidence_tier | `locator`, envelope `provenance` / `verification`, `evidence_tier`, lineage |
| — | — | kinetic_experiment_id | `sexp_id` |
| — | — | observations | the OBS behind each KINPT |

---

## 8. K-level (SSOT §210.28) and the classifier

K0 one before/after endpoint (retention / direction only) · K1 multiple times at one temperature (k / order) · K2 multiple times × multiple temperatures (Arrhenius) · K3 multiple state variables / species (multiresponse) · K4 multiple matrices / process histories (transfer). K2 and above are properties of a **set** of series, hence `k_level.scope` and the `condition_grid_id`. "Multiple times at one temperature" is labelled K1 at **≥ 3 distinct times** (THR-04K-02, an agent reading: SSOT 210.28 gives no number); that label does not decide whether a series is stored, which is THR-04K-01 (≥ 2). The classifier is a Step-09 deliverable (K-level distribution and series yield per 100 screened abstracts are Step-10 metrics, RA §4); this contract fixes the field and the vocabulary, and stamps `classifier_version`. SSOT §210.29A's planning rule (≈ ≥ 3, preferably ≥ 4 temperatures with ≥ 4–5 time points) is a pilot target, not a threshold of this contract.

## 9. Fits, parameters, and the plane boundary

`KIN.fit[]` holds what the authors reported: model family, equation (raw), **model level** (PRIMARY_RATE / SECONDARY_ARRHENIUS / ONE_STEP_GLOBAL), **scope** (SERIES / CONDITION_GRID), **input series** (`input_kin_status` + `input_kin_ids`; a secondary or global fit spans a condition grid and must name all members), **fitting method** (linearised ln vs nonlinear LS, weighting), **number of points used**, **temperature basis** (setpoint vs measured product temperature), **parameter covariance** as printed (k_ref–Ea correlation), parameters with units and uncertainty, diagnostics, effective vs mechanistic, identifiability as reported, valid domain, locator. `fit_origin` admits `AUTHOR_REPORTED` only. A fit computed by the project (Step 26a) is a model-plane object (FW-14: PROJECT_FIT lives in P-MOD) and cites KIN / KINPT as inputs; widening the enum is an H4 decision (A-3). Parameter-only reports with no recoverable raw points are **not** KIN rows (a KIN needs ≥ 2 KINPT); they belong to the Step 09.5 / 24 parameter capture with `AUTHOR_REPORTED` and can never support a K ≥ 1 claim on their own (gap A-2).

## 10. Lineage and splits for series

Each KIN carries the cached `lineage` block. Series are atomic for splitting: all KINPT of a KIN, all KIN of one `condition_grid_id`, all KIN of a SEXP stay in one partition (L-10). For kinetic validation the unit of independence is the research group / lab (RV §4 Step 27; CHG-11-3): `lab_group_id` is a **mandatory key** on KIN (and on DRV with a KIN parent), computed from `DOC.authorship` by the recall-oriented `SAME_LAB_AS` rule (shared corresponding / senior author OR the same affiliation unit within ±N years, N: THR-08A-22, value OPEN); where authorship was not read it is UNKNOWN and the series is not SIM-VAL / DS-TEST eligible. Nesting `split_group` ⊆ `lab_group`. Atomicity binds partitions only; internal CV folds inside one partition (leave-one-temperature-out in SIM-CAL) may split a grid and are labelled "within-study extrapolation" (L-10). PARAM / fit disjointness proofs use `split_group_id` and `lab_group_id`, never `lineage_root_id` (L-11); the endpoint DRVs of SIM-VAL / DS-TEST series are held out of every comparator's TRAIN (L-11b). Simulator calibration groups are a subset of downstream TRAIN groups and the locked validation groups are fixed before any fit (L-11, Step 15).

## 11. What each downstream step receives

| Step | Needs from this contract |
|---|---|
| 09 | the single field list; schema freeze only after 04.3 approval; G09-6 round-trip of a multi-T × multi-t fixture and a figure-only fixture without collapsing to endpoints; K-level classifier; digitisation provenance |
| 10 / 11 | K-level and series yield per 100 screened abstracts; ≥ 5 AA and ≥ 3 chlorophyll series in the 20-row pilot (RV §5.4); full T/t per row; analyte form and compartment; cooking-water assay flag |
| 12 | structured sources keep aggregation level and dispersion; no kinetics derived from them (R04-4) |
| 24 / 25 | `parameter_source_rows` point at KIN; parameter K-level; no model without K ≥ 1 support is promoted beyond QUALITATIVE_ONLY (RA §4) |
| 26 / 27 | CALIBRATION series only for fitting; locked validation series from independent groups; held-out by `split_group_id`, never by row |
| 32 | K0–K6 ablation inputs; identifiability reporting |

## 12. Conformance tests to write (design only; synthetic fixtures; Mac)

| ID | Test | Expected |
|---|---|---|
| K-1 | 3 temperatures × 4 times synthetic fixture → 3 KIN sharing one `condition_grid_id`, 12 KINPT, 12 OBS; derive FINAL endpoint DRVs | series intact after export; each DRV has a KIN parent |
| K-2 | figure-only fixture | every point DIGITIZED with tool / version / uncertainty on OBS and τ; series flagged FIGURE_DIGITIZED |
| K-3 | document asserting ≥ 2 distinct numeric τ for a cell but only one endpoint extracted (including a 2-time design C0 + C(t) at ≥ 2 T) | rejected (R04-1) |
| K-4 | kinetic parameter whose parent is an AGG row | rejected (R04-4) |
| K-5 | KINPT without clock tag; clock other than PROCESS_TAU | rejected |
| K-6 | `fit_origin = PROJECT_FIT` in KIN | rejected |
| K-7 | censored points in a series | kept censored; no substituted value; `censoring_summary` consistent |
| K-8 | `SERIES_NOT_EXTRACTED` row promoted to E4 | rejected |
| K-9 | KIN E4 without HUMAN_VERIFIED; KIN with `SPLITGRP-REC-` | rejected |
| K-10 | printed time axis in weeks / months / years | raw unit kept; `normalised_seconds` NOT_CONVERTED or convention-based, never CONVERTED_EXACT for month / year |
| K-11 | digitised point with unknown read uncertainty | `uncertainty_status` UNKNOWN, number null accepted; uncertainty 0 rejected |
| K-12 | relative-scale series (C/C0) | t0 point is DEFINITIONAL_NORMALISATION and excluded by fitting code; `c0_obs_id` consistent with `initial_concentration` |
| K-13 | medium and core temperature curves | two `temperature_profiles` elements, each with a clock tag |
| K-14 | tissue + cooking-medium + yield series of one run | `companion_series` + `mass_balance_set_id`; KINPT pairs at the same τ |
| K-15 | repeated-measures design | stable `replicate.unit_label`; replicate runs distinguished by `run_id` |
| K-16 | grid-level secondary Arrhenius fit | `input_kin_ids` ⊇ all grid members |

K-5, K-6, K-9, K-10, K-11, K-13 and K-14 (record-level parts) are enforced by the drafts and were exercised with the scratch checker (see `README.md`); the others need the Step-09 validator.

## 13. Not decided here

The algorithm that fills `normalised_seconds` (the field and its status vocabulary exist; month / year conventions are not chosen here), fitting method and identifiability protocol (Step 26a, SSOT §211.50A), the K-level counting rule, the PARAM / FORM registry (Step 24), event-sourced clocks of the recipe plane (EVENT_INDEX, TEXT_ORDER, OBSERVED_AT: 03.3 / recipe plane), and the first-simulator choice (R-14: AA leading candidate, chlorophyll fallback; decided from Step 10/11 series evidence).

## 14. Open decisions and ambiguities for H4

| # | Item | Draft default |
|---|---|---|
| A-1 | SSOT §216.2's "kinetic_experiment_id" names a series row; the plan equates it with `sexp_id` (one experiment may have several series). | `sexp_id` = experiment; `KIN-` = series |
| A-2 | Parameter-only reports (k, Ea reported, raw points absent) have no KIN home. | route to Step 09.5 / 24; not a KIN |
| A-3 | `fit_origin` set: card lists AUTHOR_REPORTED and PROJECT_FIT in the header; FW-14 puts PROJECT_FIT in the model plane. | AUTHOR_REPORTED only here |
| A-4 | Minimum distinct numeric τ that makes a KIN mandatory (THR-04K-01): **2** (edited from the first draft's 3 on review B #10, PROPOSED_PILOT, unsigned); ≥ 3 at one temperature = K1 label (THR-04K-02). | sign or change before Step 09 freeze |
| A-5 | K-level is a set property; the card puts it in the header. | field kept, `scope` added |
| A-6 | New prefix `CGRID-` for `condition_grid_id` (not in the 01.3-min list). | reserve |
| A-7 | `HISTORICAL_T` and recipe clocks are excluded from KIN until 03.3 is approved. | PROCESS_TAU only |
| A-8 | D-024 mentions a `KINETIC` ledger as BLOCKED_FUTURE_STEP; this contract uses KIN / KINPT instead. | confirm no `KINETIC-` prefix is intended |
| A-9 | Raw time units week / month / year / OTHER are admitted; seconds are a separate field with a conversion status; month / year never exact. | as stated |
| A-10 | Unknown digitisation uncertainty is UNKNOWN (status field + nullable number), never a number. | as stated |
| A-11 | New prefixes `LABGRP-` (lab group, mandatory on the kinetic plane) and `MBSET-` (mass-balance set); `PARAM-` referenced by LIN only. | reserve LABGRP-, MBSET- |
| A-12 | `SEXP.context` absent key = UNKNOWN (draft) vs NOT_REPORTED (plan card). | UNKNOWN |
| A-13 | Value scale / C0 semantics, temperature profiles with isothermality, companion series, richer fit records (review B #11–#17) are part of the 04.3 field list. | as stated |
| A-14 | Digitised series: two independent reads for TEST / SIM-VAL eligibility (THR-04K-03). | as stated |
