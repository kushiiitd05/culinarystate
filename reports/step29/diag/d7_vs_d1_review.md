# 29-diag shortcut and D7 versus D1 review

Status: AI_DRAFTED, 2026-11-11. **Every number in this memo carries DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / PRIOR_EXPOSURE_REANALYSIS / COND_UNAUDITED / PROVISIONAL_08A / NO_HUMAN_SIGNOFF_D085.**

Source: `reports/step29/diag/diag_results_S179.json`, RUN-S179-DIAG29-001 (D-085; WORKLOG S191).
This is a read-only transcription/interpretation of committed output, not a new model run or a new gate.
No human skim of this newly separated memo is recorded. Existing combined memo remains unchanged.

## Prediction equality and basis-removal check

Sources: `result.families.<family>.d7_vs_d1_max_abs_pred_diff` and `.shortcut_basis_removed`.
The maximum prediction difference is from the random-split review; it must not be read as a persisted
per-split optimizer trace. DEL-2's original metric equality over its five splits remains NEG-0050.

| Family | Max absolute D7−D1 prediction difference | D5 random MAE | D5 random MAE with basis removed |
|---|---:|---:|---:|
| BOGNAR-2002 | 0.2761 | 0.0499 | 0.0499 |
| PHENOL-EXPLORER-3.6 | 0.0 | 0.5468 | 0.5468 |
| USDA-RETN-R6 | 0.6528 | 0.0251 | 0.0251 |

## Why equal output is possible

`src/culinarystate/transition/baselines.py`, `D7BiasedMF.predict`, explicitly replaces nonfinite raw SGD
predictions with `self.mu`, the training target mean. D1 is the training global mean. The class comment notes
that SGD can diverge on the raw RF scale. The raw-scale Phenol-Explorer range is a known numerical risk;
`LogTarget` documents the wide ratio scale and is a different analysis already kept in the DEL-2 record.
Exact equality in this diagnostic is consistent with the global-mean fallback, rather than distinct learned
predictions. The committed JSON does not include `n_fallback` or optimizer trajectories, so it does **not**
isolate numerical divergence from every other route to equality. No optimizer hyperparameter or result is
changed in this memo; a mechanistic trace would require a dated, separately labelled follow-up.

Removing basis changes no reported D5 random-split MAE. Source family is already constant within each
family-specific fit, so this is not a train-source-held-out test or evidence that all shortcuts are absent.
The Bognár and USDA D7 predictions differ from D1, which rules out an unconditional implementation identity
between the two model classes, but says nothing about scientific transfer.
