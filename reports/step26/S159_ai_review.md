# S159 cross-review of ksh's 24a / 26a — AI verdict — pending Kush/Parv review

Reviewer: AI worker prv (an agent, not Parv). This is an AI verdict under D-045 W1. It is not an approval,
not a human or expert review and not a signature. Kush and Parv review it, and their review is final.

Scope: `src/culinarystate/simulation/kinetics/{units,models,fitting,identifiability}.py` (26a) and
`src/culinarystate/mechanism/form_param_val.py` with `registry/schemas/{FORM,PARAM,VAL}.draft_v1.schema.json`
(24a), as committed up to `1354c44` on `cloud/s159-simulator-core`. Questions checked: numerical correctness
(Gauss-Newton / LM, covariance, profile likelihood), identifiability verdict logic, units, unit order of rate
constants, provenance refusal for synthetic fits and over-claiming. Every defect below got a failing test
first (`tests/unit/test_s159_ai_review_regressions.py`, commits `155bd0c`, `d3a70cd`, `065b5a2`), then a fix in
a separate commit.

## Findings

| id | severity | evidence (synthetic probes) | disposition |
|---|---|---|---|
| R1 | MEDIUM | `units.check_rate_constant_unit("mg/g/min", 1)` returned CONSISTENT. Mass-per-mass cancels to TIME^-1, so a zero-order unit on a mass-ratio basis passed as first order. The same call with order 0 returned INCONSISTENT, and `"mol/L/s"` at order 0 was also INCONSISTENT, though it is a molar zero-order unit. The module docstring says concentration units are never reduced, but nothing enforced that unless the caller declared `opaque`. The 24a PARAM unit check (`_slot_checks`) had the same gap on RATE_CONSTANT slots. | FIXED. `ba3eb44` (units): any mass, amount or volume token that is not declared opaque makes a rate-constant unit UNKNOWN (`CONCENTRATION_TOKENS_UNDECLARED`). `c466ffc` (24a): such a unit on a RATE_CONSTANT slot gives `PARAM_UNIT_UNKNOWN`. |
| R2 | HIGH | With sigma unknown and n <= p, `assess_identifiability` returned IDENTIFIABLE with a CI of machine-precision width. Two observations and two parameters (FIRST_ORDER_ARRHENIUS) gave k_ref CI [1.8443961587479e-4, 1.8443961587586e-4]. One observation and one parameter gave the same pattern. SSR_min is about 0 and the profile statistic n·ln(SSR/SSR_min) explodes, so every profile "closes". This over-claims: no residual scale can be estimated. | FIXED `b29daa7`. Every parameter becomes UNKNOWN with the new reason `NO_RESIDUAL_DOF_SIGMA_UNKNOWN`, there is no CI and nothing goes into `reportable_estimates`. A known sigma with zero dof is unchanged (still a valid chi-square profile). |
| R3 | LOW | In the R2 case `FitResult.covariance_transformed()` returned a NaN matrix. Its docstring promises None when the covariance cannot be formed. | FIXED `43c7218` (returns None). |
| R4 | MEDIUM | `calibration_eligibility` returned ELIGIBLE_UNDER_DRAFT_RULES for a HUMAN_VERIFIED, SIM_CALIBRATION PARAM whose unit was `1/fortnight` (an unknown token) or `mg/g/min`. `PARAM_UNIT_UNKNOWN` is only a WARN, and eligibility counted ERRORs only. That conflicts with the module's own rule that UNKNOWN never becomes eligible. | FIXED `c466ffc`. A `PARAM_UNIT_UNKNOWN` issue now makes the verdict UNKNOWN with reason `PARAM_UNIT_UNKNOWN`. |
| R5 | LOW | `validate_param` raised TypeError / ValueError for `value_si` `{status: CONVERTED_EXACT, value: null or "x"}` instead of returning issues. | FIXED `3767cb9` (`PARAM_SI_NOT_EXACT` ERROR). |
| O1 | MEDIUM | Sigma unknown, dof > 0, noise-free synthetic data: the fit is exact to about 1e-31 SSR, and the profile CIs come out at about 1e-12 relative width with verdict IDENTIFIABLE (two close temperatures, 10 points). This is the same degenerate likelihood as R2, but n > p, so no structural rule catches it. | OPEN. The humans decide whether to add a round-off-level SSR rule (UNKNOWN). Until then, synthetic tests should use noise or a known sigma (the S159 26c tests do). |
| O2 | LOW | Overall verdict precedence: NOT_IDENTIFIABLE beats UNKNOWN. If one parameter has `PROFILE_BELOW_FIT_MINIMUM` (the fit was not at its minimum), the report can still say NOT_IDENTIFIABLE overall. | OPEN (design choice). UNKNOWN taking precedence would be the more conservative rule. |
| O3 | LOW | `KineticForm.check_inputs` treats every `fixed` input as an absolute temperature (> 0, message in K). A non-temperature fixed input, such as a held partition ratio or k_dw = 0, cannot be passed. The S159 26c harness works around this with a closure. | OPEN (API limitation, no wrong result found). |
| O4 | LOW | `_lm` reports `converged=True` when no decreasing step exists up to lambda = 1e16, with no gradient-norm test. No false convergence was reproduced in the probes. | OPEN (note only). |
| O5 | INFO | `Observations` does not check the `KIN-\d{6}` pattern of `kin_ids`. The PARAM schema catches a bad id downstream (`validate_param`: SCHEMA_INVALID). | No defect. |
| O6 | MEDIUM (design) | The card's G26-VER negative control says "the no-water-assay design flags k_L NON_IDENTIFIABLE in >= 95 % of datasets". Using sim_aa_1 with the card equations, it holds for a single-temperature, tissue-only design (S159 test). With 4 temperatures, tissue-only data and Ea free, k_L was IDENTIFIABLE: CI [2.54e-4, 3.27e-4] s^-1 around a synthetic truth of 3e-4. The cause is that k_L is temperature-independent in the card model while k_d follows Arrhenius. | OPEN for the 26.0 pre-registration. Define the "no-water-assay" design exactly, or revisit the claim. AI reading, not an expert answer. |
| O7 | INFO | `simulation/__init__.py` and `recipe_adapter.py` (S156) still say 26b is not built (`SIMULATOR_STATUS = NOT_BUILT_PENDING_26b`). | OPEN. Left unchanged as pre-existing files; the humans decide. |

## Checks that found no defect

- **Gauss-Newton / LM:** for FIRST_ORDER with known sigma (12 points), numpy LM and scipy give k equal to the
  closed-form weighted OLS to 1e-13 relative.
- **Covariance:** the Gauss-Newton SE (delta method from ln k) is 3.26006431267e-6, against an analytic
  (Σ τ²/σ²)^-1/2 of 3.26006431281e-6. With sigma unknown, s² = SSR/dof matches as well.
- **Profile likelihood:** for a model linear in k, the profile CI equals Wald k̂ ± z·se to about 1e-12. This is
  exact for linear models, so the bisection is grid-independent as claimed. The chi²₁ quantile comes from z².
- **Identifiability:** SVD rank on the sigma-weighted scaled sensitivities, condition number of the scaled Fisher
  information, PROFILE_FLAT on an open side. None of the G26-CAL numbers are encoded, and the criteria have no
  defaults.
- **Units:** dimensions [k] = C^(1-n)·T^-1 per SSOT 210.30, no cross-order harmonisation, Kelvin-only Arrhenius
  (degC refused in compounds), exact KIN time factors, month and year without a factor, R = N_A·k_B exact (2019
  SI).
- **Provenance:** `as_param_provenance` refuses SYNTHETIC fits (FitError). The S159 26c recovery tests check
  this again on simulator-generated data. `fit_id` is a content id, not a minted id.
- **Over-claiming:** status labels are DRAFT throughout. Nothing claims validation, calibration or human
  verification. The PROPOSED_PILOT gate numbers are kept out of the code.

## Verification of the fixes

`tests/unit/test_s159_ai_review_regressions.py`: 8 tests. They failed before the fixes (RED commits above) and
pass after them. The existing 26a / 24a / alignment tests still pass.
