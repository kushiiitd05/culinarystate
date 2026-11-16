# AA pilot: frozen Model A identifiability diagnostic

Date: 2026-11-11. Board item: T5-C12-R2.

**DIAGNOSTIC / NON_CITABLE / AI_PRECHECKED / NO_HUMAN_SIGNOFF_D085.**
Model A remains **NOT_VALIDATED / RESEARCH_ONLY**. Reviewer: author-only review (AI-delegated).
This report profiles the already frozen estimates; it neither refits Model A nor opens SIM-VAL.
No parameter-precision gate is passed by this report.

## Inputs and reproducibility

- Frozen fit: `reports/step10/aa_pilot_model_a_fit_D085.json`, SHA-256
  `b9247db03e98423f8866fa50b24e2ecd33831d907f3aace00b1f7e4f2ea9543f` (D-091).
- Frozen model: unweighted OLS on ln k, separate paper intercepts and shared Ea,
  `src/culinarystate/simulation/aa_pilot_fit.py`, version `aa-pilot-fit-0.1.0-draft`.
- New tool: `tools/s179_aa_profile_summary.py`; new output:
  `reports/step10/aa_identifiability_profile_summary_S179.json`. The tool checks both code hashes
  recorded by the frozen fit, refuses an existing output path and records the fit/tool SHA-256 values.
- Command: `python tools/s179_aa_profile_summary.py --fit reports/step10/aa_pilot_model_a_fit_D085.json
  --out reports/step10/aa_identifiability_profile_summary_S179.json`.
- Source rows are AI_PRECHECKED under D-085, not human verified. There are **7 included rows from 2 papers,
  3 regression coefficients and 4 residual degrees of freedom**. Original CAL verification sheets and
  paper texts are absent from this checkout; the diagnostic uses the frozen sufficient summaries only.

All numerical results below have the four diagnostic labels above. No bootstrap was performed.

## Method and why the summaries are sufficient

Let beta be the three regression coefficients, C the frozen OLS covariance, s the frozen residual SD,
n = 7 and nu = 4. The frozen fitter uses C = s²(X'X)^-1 and SSR_min = nu s². For coefficient j fixed
at b, minimising over all nuisance coefficients gives the exact quadratic profile

`SSR_profile(b) = SSR_min + s² (b - beta_j)² / C_jj`.

Profiling the unknown common Gaussian variance gives

`LR(b) = n log[SSR_profile(b) / SSR_min]`.

This algebra reconstructs the unconstrained profile from the committed summary without raw observations,
refitting, a scan-width choice or a new optimiser. The 95% **asymptotic** likelihood interval uses
`LR <= chi²_1(.95) = 3.841458820694124`; its half-width is
`sqrt(C_jj * nu * expm1(chi²_1(.95) / n))`.
The confidence level is a disclosed diagnostic choice, not a new acceptance threshold.

Because only four residual degrees of freedom remain, the table separately includes the Student-t interval
`beta_j +/- t_4(.975) sqrt(C_jj)`. This is finite-sample conditional inference under the fixed-design,
independent, homoscedastic Gaussian-error model; it does not account for paper dependence, verification error,
assay mismatch, model misspecification or extrapolation to another matrix. The t interval is wider here.
The likelihood profile is exact algebraically; its chi-square confidence calibration is asymptotic.

Method references: the [NIST likelihood-ratio test description](https://www.itl.nist.gov/div898/handbook/apr/section2/apr233.htm)
gives the chi-square calibration, while [NIST's linear-regression uncertainty example](https://pages.nist.gov/ml_uncertainty_py/toy_regression.html)
uses residual degrees of freedom for Student-t inference. The displayed profile identity is derived above from
the frozen fitter's OLS equations, rather than inferred from an unscaled covariance condition number.

## Per-parameter results

Reference temperature is 363.15 K. The ln k_ref intercepts use k in min^-1 as in the frozen AA fitter.
Ea is displayed in kJ/mol; the JSON retains J/mol.

| Parameter | Estimate | Asymptotic profile 95% interval | Conditional Student-t 95% interval | Profile status | Practical gate status |
|---|---:|---|---|---|---|
| ln k_ref, AAK-01 | -4.3152 | [-4.5445, -4.0859] | [-4.6875, -3.9429] | BOUNDED_CONDITIONAL_ON_OLS_MODEL | NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION |
| ln k_ref, AAK-06 | -3.1251 | [-3.4142, -2.8360] | [-3.5944, -2.6558] | BOUNDED_CONDITIONAL_ON_OLS_MODEL | NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION |
| Shared Ea, kJ/mol | 64.3978 | [46.6419, 82.1536] | [35.5707, 93.2249] | BOUNDED_CONDITIONAL_ON_OLS_MODEL | NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION |

The recorded covariance is positive definite; within the fitted linear model there is no flat coefficient
profile. This establishes bounded model-conditional intervals, not sufficient scientific precision for a use
case. No locked precision or relative-width criterion was found in the AA pilot preregistration. Proposed
G26-CAL settings must not silently become signed rules. A raw covariance condition number would mix units of
dimensionless ln k and J/mol; no such number is presented as an identifiability test.

## Checks and limits

`tests/unit/test_s179_aa_profile_summary.py`: **10 passed** under Python 3.11.9. A failing collection first
confirmed the new tool was absent. Synthetic constrained OLS refits at both endpoints for every coefficient
reproduce the likelihood-ratio cutoff. Tests distinguish profile and t intervals, preserve the caller's input,
and refuse invalid degrees of freedom, residual SD, covariance or paper identities.

The new tool reads no recipe text, CAL sheets or SIM-VAL material. It checks existing hashes rather than
replacing the fit or its code. Existing failed gates and frozen outputs remain unchanged.

- Two papers provide very little information about between-paper heterogeneity. The fitted between-paper SD
  is not a random-effects variance estimate with a profiled confidence interval here.
- No residual checks, leverage analysis, per-temperature checks, raw-unit revalidation or per-paper Model B
  sensitivity can be reconstructed reliably from the summary. They remain open pending the CAL packet.
- The likelihood profile assumes a common Gaussian residual variance and no within-paper dependence.
  Bounded intervals under that model are not evidence of robust practical identifiability under alternatives.
- The report supplies parameter profiles and explicit parameter statuses for T5-C12-R2. Its practical gate
  remains unassessed; a reviewer may accept the report artifact without approving a scientific gate.
- PARAM minting, SIMULATE calibration, domain/basis checks, SIM-VAL extraction and prediction, and the T5 G15
  scorecard retain their own requirements. This report changes none of them.
