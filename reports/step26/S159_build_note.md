# S159 build note — formula registry 24a and simulator core 26a–c (data-free)

2026-11-03. Branch `cloud/s159-simulator-core`, stacked on `cloud/s158-mechanism-stack`.
All new code is **DRAFT_PENDING_H4 / DRAFT_PENDING_26_0_H4**. **No fitted or literature parameter value is
entered anywhere.** Every parameter is a required, provenance-carrying input. Decisions recorded this
session: D-050 (block G accepted, scipy approved as optional extra `step26`) and D-051 (THR-04K-01..04 signed).

Workflow (D-045): AI worker "ksh" built 24a and 26a; AI worker "prv" built 26b, 26c and the 26.0 template and
cross-reviewed 24a/26a; the coordinator verified both.

## What was built

| Part | Files | Content |
|---|---|---|
| 24a | `registry/schemas/{FORM,PARAM,VAL}.draft_v1.schema.json`, `src/culinarystate/mechanism/form_param_val.py` | Formula, parameter and validation schemas sharing fields with KIN v1.1. A parameter without provenance is rejected. The FORM- vs MODEL- prefix is a required argument and is not decided. |
| 26a | `src/culinarystate/simulation/kinetics/{units,models,fitting,identifiability}.py` | Zero-order, first-order, Weibull and reference-T Arrhenius forms, plus a one-step global fit and an exact piecewise-temperature solution. Least squares (numpy, with scipy optional), profile likelihood, local sensitivity, identifiability verdicts (criteria have no defaults) and a dimension checker. |
| 26b | `src/culinarystate/simulation/{sim_core,sim_aa_1,sim_chl_1,systems,choi_okos}.py` | `sim_aa_1`: tissue, water and degraded compartments; Arrhenius degradation; lumped leaching; optional k_dw; optional product-temperature lag. `sim_chl_1`: Chl a/b to pheophytin with a caller-supplied g(pH). One interface. A run happens **only** with a valid APPDEC record that says SIMULATE; UNKNOWN never simulates. Deterministic, full provenance, `sim_run_id` null, NOT_VALIDATED. Choi–Okos is structure only: coefficients are caller PARAMs and the mixing rules are marked as AI recollection (OPEN). |
| 26c | `src/culinarystate/simulation/verification.py` + tests | Analytic vs numeric ≤ 1e-6 for all 6 solvers; convergence order within ±0.2 of nominal; mass balance ≤ 1e-9; unit dimensions; stiff case refused for fixed-step methods and matched by BDF/Radau/LSODA; synthetic recovery through 26a, with the negative controls behaving as expected. |
| 26.0 | `reports/step26/system_selection_record_TEMPLATE.{md,UNSIGNED.json}` | Template only. AA leading candidate vs chlorophyll fallback (D-027). **Nothing chosen.** |

Synthetic recovery examples: noise-free fits recover the parameters to ≤ 1e-6; noisy first-order Arrhenius fits
land within 3% (k_ref) and 5% (Ea); 90% profile CIs covered the truth in 94 of 100 datasets; a single-temperature
design gives NOT_IDENTIFIABLE.

## AI cross-review of 24a/26a (`reports/step26/S159_ai_review.md`)

| ID | Severity | Fix |
|---|---|---|
| R1 | medium | A zero-order mass-ratio unit passed as first order |
| R2 | high | n ≤ p with unknown sigma came out IDENTIFIABLE with a machine-precision CI |
| R3 | low | NaN covariance instead of None |
| R4 | medium | An unknown-unit PARAM was eligible for calibration |
| R5 | low | `validate_param` crashed on a non-numeric value |

Open items O1–O7 are in block H. O6 is the important one: in the card's equations k_L does not depend on
temperature, so a "no-water-assay" design can still identify k_L. The 26.0 pre-registration must define that
design exactly.

## Verification

| Check | Result |
|---|---|
| Full unit suite (thread caps) | **2994 passed**, 17 skipped, 1 deselected. The 1 failed + 11 errors are missing bundle files, unchanged. |
| Ledger guard | 7/7 |
| Attribution lines | 0 |
| Float literals in simulator modules | 0, apart from exact constants (a test checks this) |
| Memory-sourced items | KiSAO ids and Choi–Okos mixing rules, both tagged `AI_RECALLED_UNVERIFIED` / OPEN |

## Needs human

The open items are listed as block H on the review sheet.
