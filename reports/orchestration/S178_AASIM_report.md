# S178 lane AASIM (W2 aa-fit-sim): FORM rows, kinetic units, router SIMULATE branch

Status: **AI_DRAFTED / PROPOSED / NON_CITABLE.** Not a human gate, signature, approval or nonce (D-071). Worktree
`~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, base `07fc0d2+uncommitted`). No git write, no ledger
write, no edit of the board, `DECISIONS.md`, `WORKLOG.md`, `docs/*`, `handoff/*`, `registry/compute_runs_v1.csv` or any
file of another lane. Counts only; no recipe text.

## 0. Item statuses

| item_id | new status | what is done | what is left | evidence |
|---|---|---|---|---|
| T5-C07-R2 | **PARTIAL** | 6 draft FORM records (zero-order stub, first-order fixed T, reference-T Arrhenius, first-order Arrhenius one-step, Weibull stub, sim_aa_1 three-compartment composite): equation (LaTeX + evaluable AST), slots with dimension / order / positivity, 7 assumption constraints, validity-domain fields (`ms_limits`, 333.15-373.15 K from the pre-registration), units, implementation hash, model cards. **No parameter value anywhere** (tested: every numeric leaf is in {0, 1, 333.15, 373.15}). Lifecycle `REIMPLEMENTED`, verification `UNVERIFIED`, ids in the draft block `FORM-900001..6` (not minted). AST equals `models.py` to 1e-12; sim_aa_1 with NO_WATER_CONTACT equals the analytic piecewise first-order Arrhenius solution to 1e-9 (EXPM) / 1e-6 (RK4, trapezoid) (G24.2 second half, synthetic inputs). | **Not REPRODUCED**: G24.2 first half needs one source figure or table reproduced within 0.02 (a human-opened source and digitised points; none exist). So `reports/step24/reproduction_report.md` and REPRODUCED rows do not exist. Ledger mint of `FORM.jsonl` and the 24f FORM-/MODEL- decision (orchestrator / humans). Model-card review by Kush and Parv. | `registry/form_registry_aa_v1_DRAFT{.jsonl,_index.csv,_model_cards.md}`; `src/culinarystate/mechanism/aa_form_registry.py`; `tests/unit/test_s178_aasim_forms.py` (28 tests) |
| T5-C07-R5 | **PARTIAL** | 11 draft kinetic unit rows (s^-1, min^-1, h^-1, d^-1, J/mol, kJ/mol, kcal_th/mol, kcal_IT/mol, kcal/mol (ambiguous), K, degC) with exact `Fraction` factors; resolver; `to_si` / `to_kelvin`; `param_unit_issues` (every PARAM unit and `T_ref` unit must resolve with the slot dimension; `mg/g/min` is refused as a rate unit; degC refused as T_ref); cross-check with `units.py` wherever it can parse; UNIT-schema projection function. | Mint into `ledgers/data/UNIT.jsonl` (orchestrator). The UNIT schema v1.0.0 **cannot hold** these rows (see finding F3): an additive enum change is needed (H4). `units.py` has no `kcal` token and is not mine; `form_param_val._slot_checks` is not wired to the registry (not my file). | `registry/kinetic_units_v1_DRAFT.csv`; `src/culinarystate/mechanism/kinetic_unit_registry.py`; `tests/unit/test_s178_aasim_units.py` (37 tests) |
| T5-C11-R4 | **PARTIAL = "code-tested only"** (the board's own fallback wording) | SIMULATE branch end to end: guard -> domain gate -> unchanged 23a engine -> `sim_core` / `sim_aa_1` -> retention INTERVAL with PARAM ids and basis; minimal tested `simulate=` hook in `router_demo.route_text` (byte-identical when absent); property test that UNKNOWN never routes to SIMULATE; one end-to-end demo with the full provenance chain; **on real data SIMULATE is unreachable** (four independent locks, section 2: guard, domain-gate files, reviewed MECH entry, safety declaration). | Real PARAM rows, frozen fit, Step 27 VAL (M3, T5-C10-R5, humans); the lock's three domain-gate files; a reviewed MECH entry; a safety-criticality declaration; the route-rule decision F1. | `src/culinarystate/mechanism/simulate_branch.py`; hook in `router_demo.py`; `tests/unit/test_s178_aasim_branch.py` (79) + `..._router_hook.py` (16) |

Tests: 160 new tests, all pass; related existing suites re-run (see section 6).

## 1. What was built (files)

New:
- `src/culinarystate/mechanism/simulate_branch.py` (owned). Classes `Q`, `AAEvent`, `DomainGate`, `GateEval`, `Artifacts`,
  `GuardVerdict`, `TestOnlyFixtures`, `BranchConfig`, `Outcome`, `SimulateBranch`; functions `check_guard`, `evaluate_gate`,
  `load_artifacts`, `summarize` (counts only).
- `src/culinarystate/mechanism/aa_form_registry.py` and `src/culinarystate/mechanism/kinetic_unit_registry.py`: **two new
  helper modules beyond the file list in the brief.** Both are new files that nothing else imports; they hold the deterministic
  builders / resolvers behind the registry files so the files are reproducible and tested. Move or fold them as you prefer.
- `registry/form_registry_aa_v1_DRAFT.jsonl`, `registry/form_registry_aa_v1_DRAFT_index.csv`,
  `registry/form_registry_aa_v1_DRAFT_model_cards.md`, `registry/kinetic_units_v1_DRAFT.csv`.
- `tests/unit/test_s178_aasim_{branch,forms,units,router_hook}.py`.

Modified (minimal, tested): `src/culinarystate/mechanism/router_demo.py` — optional `simulate=None` argument of `route_text`
(duck-typed, nothing imported), a per-item `simulate` block, and an envelope `simulate` block only when enabled. With
`simulate=None` the output is byte-identical (tested on three texts, with and without gates). The route becomes SIMULATE
only when the branch completed a run; it is never downgraded and never replaced by a weaker route.

## 2. How SIMULATE is gated (the chain; every link can only refuse)

1. **Guard** (`check_guard`, 29 fixed refusal codes plus three validator-error families, each fixed code exercised by a test (the test counts them)): FORM present, lifecycle >= REPRODUCED (G24.2) and
   human-reviewed; frozen fit present, record `AA_PILOT_MODEL_A_FIT`, `FROZEN_BEFORE_SIM_VAL`, `sim_val_opened == false`, its
   sha256 recorded in `registry/compute_runs_v1.csv`, both humans' returned-file hashes present (D-076 dual verification),
   n_papers >= 2; PARAM rows `ACTIVE`, `HUMAN_VERIFIED` by Kush or Parv, partition `SIM_CALIBRATION` (never
   `SIM_VALIDATION_LOCKED` / `PENDING_15B`), `validate_param` clean, `fit_run_id == FITRUN-<fit sha[:16]>` (AI proposal),
   and the PARAM values equal the frozen fit's Ea and per-paper intercepts to 1e-9; a Step 27 VAL record that is evaluated,
   study-disjoint, plan-hashed, human-verified and not FAILS. REAL mode refuses any artifact containing the string `TEST_ONLY`;
   TEST_ONLY mode refuses any unmarked artifact. `from_repo()` can only build REAL mode (tested: `TestOnlyFixtures(` is
   never instantiated in `src/`).
2. **Domain gate** (v16 draft 286.3, amendment section 7): matrix class on the lock's list (ING id -> class), NO_WATER_CONTACT
   via the lock's medium map (`WATER_IMMERSION` -> UNKNOWN `LEACHING_UNIDENTIFIED_WATER_IMMERSION`; unmapped -> UNKNOWN),
   bath temperature inside 60-100 degC (the pre-registered inclusion rule; a bracket that straddles a bound is UNKNOWN, fully
   outside is SIM_PROHIBITED), pH inside the CAL range (pH-A) or declared not gated (pH-C), sole-member lot, no earlier heat
   or leach, target present (needs the router's `gates=`; without it the lot context is unconfirmed -> UNKNOWN). Out beats
   unknown beats in (Kleene, as in the engine).
3. **Unchanged Step 23a engine** (`applicability.evaluate`) with G6 / G7 / G8 stated from 1 and 2, `domain_flag`
   IN_VALIDATION_DOMAIN only when a VAL with `may_define_validated_domain` passed the guard, `safety_critical` from the config.
   `sim_core.run` re-checks the APPDEC (route SIMULATE, id intact, same event).
4. **`systems.simulate("sim_aa_1")`**: BATH_EQUALS_PRODUCT, `medium_contact = NO_WATER_CONTACT`, `k_dw` OFF, so A_t is the
   first-order Arrhenius solution. Parameters are the frozen Model A unseen-matrix prediction (`aa_pilot_fit.predict_ln_k`,
   mean intercept, between-paper SD, residual SD, covariance), run at the corners of the input box (T and duration brackets) for
   the lower and upper 95 % bound; ParamValues are `MODEL_DERIVED` (`DERIVED-<hash>`); the real PARAM ids are carried separately.
   The output is `retention_interval {low, high}` = the outer envelope; `coverage_claimed: false`; there is no point value.

**Real data today** (`SimulateBranch.from_repo()`; tested as a tripwire): the guard refuses with `FORM_NOT_REPRODUCED`,
`FORM_NOT_HUMAN_REVIEWED`, `FROZEN_FIT_ABSENT`, `PARAM_ROWS_ABSENT`, `STEP27_HELDOUT_ABSENT`; the domain gate registry is absent
(`DOMAIN_GATE_REGISTRY_ABSENT`); the engine has no reviewed MECH entry (`NO_CANDIDATE_MECHANISM`); safety is `SAFETY_UNKNOWN`.
Every router item gets a `simulate` block saying so, none routes SIMULATE, `summarize()` gives SIMULATE count 0.

## 3. Output contract (paste-ready for `docs/simulator_data_contract.md`, which is orchestrator-only)

A router item that reaches SIMULATE carries `simulate` with:
`record AA_SIMULATE_BRANCH`, `version`, `mode` (REAL | TEST_ONLY), `status COMPLETED`, `engine_route SIMULATE`,
`section141_class physically_possible`, `labels` = NOT_VALIDATED + RESEARCH_ONLY + NON_CITABLE (+ SCENARIO if any input is
Layer 2, + TEST_ONLY for fixtures), `analyte_basis REDUCED_L_ASCORBIC_ACID`, `basis_flags [BASIS_MISMATCH_TOTAL_VITC]`,
`retention_interval {low, high, unit FRACTION_OF_INITIAL_REDUCED_AA, kind OUTER_ENVELOPE_OF_95PCT_PREDICTION_BOUNDS_OVER_INPUT_BOX,
coverage_claimed false}`, `inputs[]` (name, value, unit, **basis**, **layer 1|2**, ref = Layer 1 span id), `domain_gate`
(verdict, reasons, matrix_class, medium_contact, flags), `form_id`, `param_ids` (the human-verified PARAM rows), `derived_param_ids`,
`frozen_fit_sha256`, `val_ids`, `appdec_id`, `run_sha256[]`, `flags` (T_P_BATH_EQUALS_PRODUCT_ASSUMED, COME_UP_TIME_NOT_MODELLED,
INTERVAL_COVERAGE_NOT_CLAIMED, MODEL_DERIVED_PARAMETERS, BASIS_MISMATCH_TOTAL_VITC, PH_NOT_GATED). The router item's `route` becomes
SIMULATE with reasons `["SIMULATE_RESEARCH_ONLY_PILOT"]` and the demo engine's earlier reasons kept as `reasons_demo_engine`.
Any refusal carries `status NOT_SIMULATED`, `section141_class unsupported`, reason codes, and **no number**. Any Layer 2 input
(`basis ASSUMED_DEFAULT:<id>`, including a pH range taken from the FDA table for the gate) adds the SCENARIO label and the bracket
is the GENTLE-INTENSE range, never a TYPICAL point.

## 4. Findings and decisions this lane cannot make (for humans)

- **F1 (route rule vs pilot design; needs a human decision).** The adopted engine rule routes SIMULATE only when the domain is
  IN_VALIDATION_DOMAIN, i.e. a VAL with `may_define_validated_domain`, which the VAL schema allows only for verdict
  `MEETS_PREREGISTERED_CRITERIA`, study-disjoint, tier not V3. The pilot is pre-announced RESEARCH_ONLY and descriptive with **no
  threshold** (amendment C4), and SIM-VAL is mostly other matrices (V3). So even after M3 lands, the adopted rule routes
  IN_CALIBRATION_ONLY events **QUALITATIVE + RESEARCH_ONLY, never SIMULATE**; the board acceptance ("SIMULATE fires inside the
  calibration domain, interval labelled RESEARCH_ONLY") cannot be met under the engine as written. This lane does not fake the
  domain flag (tested: a VAL that cannot define a domain gives `ENGINE_ROUTE_QUALITATIVE`, no number). Options: (a) pre-register a
  threshold so a V1/V2 VAL can define the domain; (b) amend the route rule (applicability.py, not this lane) with a "pilot
  research-only SIMULATE" line for IN_CALIBRATION_ONLY; (c) accept QUALITATIVE-only for the talk.
- **F2 (medium map semantics).** The generic `process_medium_map` gives WATER to simmer / boil. A juice simmered in its own pot has
  no separate cooking water, but a medium code cannot express "the lot is the liquid", so the lock's map must decide per matrix
  class; as written, boiled or simmered events are UNKNOWN (leaching unidentified). Likely eligible events are steam and sealed
  sous-vide of pulpy fruit: few. Expect a tiny simulability census (T5-C11-R6).
- **F3 (UNIT ledger).** `UNIT.schema.json` v1.0.0 `dimension` enum has no rate or energy-per-amount value and `unit_type` has no
  KINETIC. The additive change is exactly `unit_type += KINETIC`, `dimension += RATE_PER_TIME, ENERGY_PER_AMOUNT` (tested: the 11
  rows validate with it and fail without it). `units.py` has no `kcal` token (not edited). The calorie must be declared: `kcal/mol`
  resolves to UNKNOWN until `TH` (4184 J) or `IT` (4186.8 J); both factors are SOURCE_UNVERIFIED_AGENT_RECALLED.
- **F4 (fitted T range).** The frozen fit JSON stores no observed temperature range, so the gate uses the pre-registered inclusion
  rule 60-100 degC. If the included rows span only 70-95, the gate would extend beyond the data. Recommend `tools/aa_pilot_fit.py`
  also writes the min / max T of the included rows and the gate reads that (file not mine).
- **F5 (frozen-fit path).** `tools/aa_pilot_fit.py` writes `reports/step10/aa_pilot_model_a_fit_FROZEN.json`; the board names
  `reports/step10/aa_pilot_fit_frozen.json`. The loader accepts both. Pick one.
- **F6 (extra locks that need human input).** `safety_critical` stays UNKNOWN until a human declares it (`BranchConfig`); the
  lock's three files `registry/aa_simulate_{matrix_class_list,medium_contact_map}_v1.csv` and `aa_simulate_domain_gate_v1.json`
  (written from the VERIFIED CAL papers' matrices at the lock, never before; I wrote none); the PARAM `fit_run_id` convention
  `FITRUN-<fit sha256[:16]>` is my proposal.
- **F7 (interval meaning).** The interval is an outer envelope of per-segment-bound 95 % prediction intervals of an unseen matrix
  (between-paper SD included) over the input box; coverage is not claimed. Product temperature = bath temperature, no come-up
  (flagged); `LUMPED_LAG` is refused because no tau_h PARAM exists. Output is reduced AA; comparing it with total vitamin C
  (SVAR-000009) carries `BASIS_MISMATCH_TOTAL_VITC`.
- **F8 (tripwires).** Two tests assert today's state on purpose (`test_real_branch_refuses_on_real_data_today`, and the router
  hook's real-branch test): when the real artifacts exist they will fail so that a human re-reads them.

## 5. Not done / out of scope

No REPRODUCED row; no `reports/step24/*`; no ledger mint (FORM, UNIT); no edit of `units.py`, `form_param_val.py`,
`applicability.py`, `router_census.py`, `tools/aa_pilot_fit.py`, the board or docs; no real-data run (none possible); the router
census does not yet call `simulate_branch.summarize` (T5-C10-R5 asks the census to report a SIMULATE count, 0 acceptable).

## 6. Tests run (venv312, `nice -n 10`)

- New: `tests/unit/test_s178_aasim_{branch (79), forms (28), units (37), router_hook (16)}.py` = 160 passed; with the related suites below 500 passed in one run (taken before the 3 last guard cases were added; the branch file re-run alone afterwards: 79 passed).
- Related existing suites re-run, all passed: `test_s170_router_demo`, `test_s171_query_router`, `test_s171_router_census`,
  `test_s177_router_gates`, `test_s177_router_public_mode`, `test_step24a_form_param_val_{contract,schema}`,
  `test_step26a_kinetics_{units,models}`, `test_step26b_simulator_interface`, `test_s171_aa_pilot_fit`,
  `test_s159_kinetics_registry_alignment`, `test_s178_evd_conformance`.
- Property tests: 400 random input / guard states, SIMULATE iff every one of nine inputs is known and in range (oracle), and a
  3x2x3x5 grid of case gates x domain flags on the real engine (SIMULATE iff all APPLICABLE and IN_VALIDATION_DOMAIN).

## 7. Runs (rows for `registry/compute_runs_v1.csv`; deterministic builds, no data processed)

```
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S178-AASIM-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE,1,python -m culinarystate.mechanism.aa_form_registry,registry/form_registry_aa_v1_DRAFT.jsonl,35f8ab0454f14ef5119cc52b741deab88d03a0530d3cdc2017d5ea4c870866c0,2026-11-09T11:14:05Z,2026-11-09T11:14:07Z,DONE,AI_DRAFTED 6 FORM rows; no parameter value
RUN-S178-AASIM-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE,1,python -m culinarystate.mechanism.aa_form_registry,registry/form_registry_aa_v1_DRAFT_index.csv,43595f7eb2e5913fe0535f7f512d54f53b5b82adc507b63c317b0cecfc2bf12c,2026-11-09T11:14:05Z,2026-11-09T11:14:07Z,DONE,flat index of RUN-001
RUN-S178-AASIM-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE,1,python -m culinarystate.mechanism.aa_form_registry,registry/form_registry_aa_v1_DRAFT_model_cards.md,cdb7d45d1f4de5ee90c4aa1e91f91f6889944c5044f9a19e6d31b58bd3de8228,2026-11-09T11:14:05Z,2026-11-09T11:14:07Z,DONE,model cards of RUN-001
RUN-S178-AASIM-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE,1,"python -c 'kinetic_unit_registry.write_csv()'",registry/kinetic_units_v1_DRAFT.csv,aa9b0b1275f67665c9401362966659f86347792964decde99d2a9982a35eda27,2026-11-09T11:14:05Z,2026-11-09T11:14:07Z,DONE,11 draft kinetic unit rows; not in UNIT ledger
```
(`git_commit` as the brief states; the FORM implementation hashes inside the JSONL are of `models.py` and `sim_aa_1.py` as they stand;
regenerate the registry if either file changes: a test fails on drift on purpose.)
