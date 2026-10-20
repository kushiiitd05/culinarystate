# Fusion decision (F0-F3), DEV only, TASTEset

Metadata set frozen first (`metadata_calibration_crossdataset.md`): only M6 (gazetteer exact + fuzzy agreement) is promoted.

| Arm | Definition | DEV micro-F1 (5 seeds) | vs F0 |
|---|---|---|---|
| F0 | DeBERTa-base+CRF | 0.9396 | - |
| F2a | + M6-only concat fusion | 0.9369 | -0.0027, 1/5 seeds |
| F2b | + M6-only gated fusion | 0.9368 | -0.0028, 1/5 seeds |
| F1 | F0 + M6 outside the encoder, through the calibrator | NLL 0.1539 -> 0.1450, ECE 0.0265 -> 0.0232 (TASTEset); neutral on RecipeDB3 | F1 is a calibration-stage change: span F1 unchanged by construction |

Earlier all-feature fusion also failed (concat +0.0002, gated -0.0017, metadata ON vs OFF -0.0007). **Neural fusion: REJECT.** Keeping metadata outside the encoder is the supported design. F3 (fusion + final calibration) is moot. F2 not run on RecipeDB3 (no evidence of benefit on the cheaper dataset; no compute spent).
