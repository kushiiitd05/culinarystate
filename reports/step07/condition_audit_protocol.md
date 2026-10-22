# Step 07 -- 100-condition human audit protocol (NOT yet conducted)

Purpose: confirm that the deterministic normaliser represents source conditions without inference. Reviewers: Kush and Parv, independently and blind to each other. Packets (git-ignored, local): `annotation/condition_audit/condition_audit_packet_100_{Kush,Parv}.csv` (sampling manifest and seed: `condition_audit_sampling_manifest.json`; strata S1-S6, deterministic seed `step07-condition-audit-v1`).
Per condition, judge each field (duration, temperature value, temperature location, pressure, power, medium) against the **raw source string shown** using exactly one code:
- `CORRECT` -- the normalised value type/status matches what the raw text says.
- `WRONG_TYPE` -- should be POINT / INTERVAL / QUALITATIVE / UNKNOWN (state which in the reason column).
- `WRONG_VALUE` -- type right, number or unit wrong.
- `WRONG_LOCATION` -- temperature assigned to a location the text does not support (setpoint vs medium vs surface vs core), or a location should have been left UNSPECIFIED.
- `INFERRED` -- the normalised output contains information not in the raw text (any assumption).
- `SHOULD_BE_AMBIGUOUS` -- the raw text is genuinely ambiguous (e.g. bare psi; "boiling"; percent vs fraction) and the normaliser should flag it.
- `N/A` -- field not present in raw or output.
`overall_judgement` = `ACCEPT` only if no field is WRONG_*/INFERRED. Do not look at the other reviewer's file. Do not use external sources; judge only against the raw string.
Agreement: Cohen's kappa over per-field codes, and over overall ACCEPT/REJECT, computed with `tools/agreement.py` conventions once both packets are returned. **Gate: kappa >= 0.8 before any condition annotation is promoted for later scientific use.** Disagreements are adjudicated by a joint session; the adjudicated file is frozen with hashes before any normaliser change. The normaliser may not be modified based on a reviewer's file until the kappa and adjudication are recorded.
Status: **PENDING_HUMAN_SUBGATE** (packets built, 0 judgements).

## Update (2026-10-22, packet v2)
Packet v1 omitted the normalised power and medium columns, so reviewers could not see them (all 5 power REJECTs in the returned v1 files were caused by this display defect, not by the normaliser). Use `condition_audit_packet_100_v2_{Kush,Parv}.csv` (same 100 conditions, same seed). The returned v1 files are not accepted as the human sub-gate: Kush "(1)" and Parv "(1)" agree on all six field columns in 100 of 100 rows and Kush_REVIEWED disagrees with both; provenance unconfirmed. Normaliser fixes made after reading the flagged cases: RAW_TEXT_PRESENT_BUT_NOT_PARSED (245 durations), SLASH_NOTATION_RANGE_OR_ALTERNATIVES (18), SPACED_DASH_SIGN_OR_RANGE_FRAGMENT (24), MULTIPLE_VALUES_SAME_LOCATION (472 temperature entries). The fresh blind v2 audit is still required for the kappa >= 0.8 gate.

## Update (07H, packet v3) -- the ONLY valid audit input
Packets v1 and v2 are **invalid** as audit inputs (the normalizer semantics changed in 07H: open-bound fix, calendar durations, plausibility-vs-hard bounds, trajectories, uncertainty, strict schema). Previously returned files are not used.
Files: `condition_audit_packet_100_v3_Kush.csv`, `condition_audit_packet_100_v3_Parv.csv` (identical content, separate files; blind). Each row carries `normalizer_fingerprint_12`; the full code/schema/registry hashes are in `reports/step07/condition_audit_sampling_manifest.json`.
Reading the normalised columns: `POINT/VALID 453.15 K` = single value in canonical units; `~` = source marked it approximate; `INTERVAL/VALID (348.15, +inf) K` = `> 75 C` (round bracket = limit excluded, square = included); `calendar:3 month` = calendar duration deliberately NOT converted to seconds (status AMBIGUOUS is correct);
`ref=ABSOLUTE|GAUGE|UNSPECIFIED` = pressure reference; `UNKNOWN/UNKNOWN` = field not stated. New judgement columns: `basis_judgement`, `retention_type_judgement`, `censoring_judgement` judge `normalised_measurement_context` against `raw_measurement_context` (same codes; N/A if no EVD row).
Same codes as above. Judge each normalised field against the raw string ONLY; do not use external sources; do not look at the other reviewer's file; do not edit the normalised columns. Fill every judgement cell (blank = invalid file); `overall_judgement` is ACCEPT or REJECT.
Gate (preregistered): pooled Cohen's kappa >= 0.80 AND no systematic disagreement on a critical field (temperature location, pressure reference, basis, retention type, censoring) -- a flagged critical field forces adjudication even if overall kappa passes. Computed by `tools/step07_agreement.py` (also reports per-field, per-status, disagreement matrix, per-stratum, raw agreement).
If the normalizer changes after reviewers start, the audit is invalid and must be rerun. Do not tune the normalizer on the labels.

## Update (07H-R, packet v4 -- the ONLY valid audit input)
Packets v1, v2 and v3 are invalid (normalizer changed in 07H-R: calendar months/years stored as fixed seconds at ingest are now AMBIGUOUS calendar durations, scale-not-stated temperatures, fractions, compound durations). Files: `condition_audit_packet_100_v4_Kush.csv`, `condition_audit_packet_100_v4_Parv.csv` (identical content; each reviewer works alone; fingerprint `e7d589136275` on every row; full hashes in `reports/step07/step07hr_freeze_manifest.json`). Same rubric, codes and gate as the v3 section above. The two files returned for v3 were NOT used (provenance: written 11 s apart; authorship unverified).
Rows such as `POINT/AMBIGUOUS calendar:6.0 month` are correct behaviour (calendar duration deliberately not converted to seconds). The reviewers must judge only against the raw string; the agent does not fill or tune on labels; if the frozen files change after review starts the audit is invalid (`python tools/step07hr_freeze.py --verify`).
