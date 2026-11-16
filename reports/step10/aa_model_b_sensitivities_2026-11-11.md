# AA CAL: Model B and predeclared sensitivity disposition

Date: 2026-11-11. Board item: T5-C10-R5.

**DIAGNOSTIC / NON_CITABLE / AI_PRECHECKED / NO_HUMAN_SIGNOFF_D085.** Every numerical result below has these
labels. The frozen primary remains **NOT_VALIDATED / RESEARCH_ONLY**. Reviewer: author-only review
(AI-delegated), not independent human verification. No SIM-VAL material was opened by this lane.

## Provenance and controls

The supplied D-085 CAL sheet has the same SHA-256 that the frozen Model A binds:
`0fff439aeb74df4edbb7cb1822ccf5aeb04d58b5427f6bf315bfa33d9e8abcd6`.
It contains 16 rows from four papers. Seven kinetic rows from the two licence-admissible papers remain in the
primary inclusion set; two admissible author-Ea rows are not fitted, and seven rows are licence/verdict-rejected.
AAK-09 and AAK-11 stay rejected under D-091; this sensitivity does not restore them.

The original fit SHA-256 remains
`b9247db03e98423f8866fa50b24e2ecd33831d907f3aace00b1f7e4f2ea9543f`.
The tool verifies the original fit, original bound CAL sheet, both frozen fitter-code hashes, licensed paper PDF
hashes, local text hashes, source span matches and minute-based rate units before any sensitivity is emitted.
The primary Model A is not refitted, replaced or retuned. No domain registry is retrospectively supplied.

New public artifact: `reports/step10/aa_model_b_sensitivities_2026-11-11.json`, SHA-256
`78b48977d69e9ca0baadd7798ab27a3a6c4df972cfc79403c97ef84ab6b5652b`.
Its code hashes bind the new library and command-line tool. Its recorded numerical-run interval is
2026-11-11T17:19:36.026560+00:00 to 2026-11-11T17:19:36.030763+00:00.
Source spans and source-located metadata are only in the ignored
`annotation/aa_pilot/aa_CAL_metadata_precheck_2026-11-11.json`, whose hash the artifact records.

Command:

```
python tools/s179_aa_cal_sensitivity.py \
  --cal annotation/aa_pilot/aa_pilot_verify_CAL_v1_D085.csv \
  --metadata annotation/aa_pilot/aa_CAL_metadata_precheck_2026-11-11.json \
  --out reports/step10/aa_model_b_sensitivities_2026-11-11.json
```

The tool refuses an existing output path. Source excerpts are not copied into the public output.

## Per-paper Model B

The locked preregistration §6 requests a separate Ea wherever at least three included temperatures exist.
Both admissible papers meet that design requirement. Each fit is unweighted OLS of ln k on reciprocal Kelvin
temperature with a paper-specific intercept and Ea; reference temperature is 363.15 K and k has units min^-1.
The numerical design scales Ea in kJ/mol, then returns J/mol. This does not change the fitted model.

| Paper | Rows / distinct temperatures | Residual dof | Ea, kJ/mol | OLS SE, kJ/mol | ln k_ref | OLS SE of ln k_ref |
|---|---:|---:|---:|---:|---:|---:|
| AAK-01 | 4 / 4 | 2 | 57.3862 | 6.1915 | -4.3576 | 0.0679 |
| AAK-06 | 3 / 3 | 1 | 76.9866 | 28.6530 | -3.0047 | 0.3550 |

These are coefficient diagnostics, not an inference that the papers have different true activation energies.
The SEs condition on independent, homoscedastic log-rate errors and ignore table rounding, shared extraction
error, assay differences and within-paper dependence. They are not 95% confidence intervals.
The second paper has only one residual degree of freedom. Reported source rate dispersions are not used as
weights because the preregistration fixes unweighted OLS. No author aggregate Ea is used as a fit input.

## Predeclared sensitivity arms

| Arm | Disposition | Reason and practical limit |
|---|---|---|
| All admissible kinetic rows, including any below 60°C | SAME_ROWS_AS_PRIMARY_NO_REFIT | No admissible row is below 60°C; the arm retains the same seven rows. This is not an additional robustness result. |
| All rows including flagged AAK-11 | NOT_RUN_LICENCE_REJECTED | AAK-11 remains rejected, as does AAK-09. The predeclared arm cannot override the source-admissibility rule. |
| Remove papers with explicitly stated water contact | SAME_ROWS_AS_PRIMARY_NO_REFIT | AAK-09 is already excluded. AAK-01 has sealed tubes; closure/contact remains UNKNOWN for AAK-06. No remaining paper is explicitly classified YES. Unknown contact is not evidence of no contact and does not pass the SIMULATE gate. |
| Remove non-AA-specific assay rows | NEED_DATA | The predeclared AAK-06 iodine-titration exclusion leaves four rows from one paper. The unchanged Model A requires at least two papers for between-paper SD. No substitute one-paper primary fit is supplied. |

## Source metadata findings

AAK-01 reports HPLC L-ascorbic acid, sealed sample tubes, and source sample pH 3.85 with reported dispersion 0.07.
The dispersion type is not declared by the checked passage, so it remains NOT_REPORTED_BY_SOURCE. Its assay
preparation uses other pH values; those are not the food matrix pH. AAK-06 reports iodine titration and juice
adjusted to pH 4.4; the natural juice pH is not substituted for the adjusted experimental value. Tube closure is
not stated in the thermal-treatment passage. pH dispersions are not converted to intervals or gate bounds.

The distinction between HPLC reduced AA and the predeclared non-AA-specific titration flag remains an assay-basis
limitation of the original pooled fit. This diagnostic does not amend that fit or certify either assay. The
comparison with SIM-VAL must preserve analyte-basis distinctions and must not silently treat total vitamin C as
reduced L-ascorbic acid. No PARAM row, domain whitelist, application approval or calibration gate is supplied here.

## Verification and remaining acceptance

TDD first reproduced the missing library, then the missing CLI. Synthetic tests cover independent OLS recovery,
separate paper slopes, distinct-temperature sufficiency, nonfinite/invalid input rejection, duplicate IDs,
input immutability, licence-exclusion handling, unknown water contact, unchanged-primary no-refit behaviour and
overwrite refusal. A numerically perfect fit returns NEED_DATA_FOR_UNCERTAINTY with null SEs instead of claiming
zero uncertainty. No practical scientific precision threshold is introduced.

The targeted AA check passed **25 tests**, including **14 new tests**. Tests ran with the pinned Python 3.11.9
environment and one-thread numeric settings. The library/tool are separate files; frozen fitter, preregistration,
primary output and SIM-VAL remain unchanged.
An additional fresh `pdftotext -layout` pass found all **16/16** admissible CAL row and metadata proof spans
directly in PDF-derived text; no paper excerpts were emitted by that check.

T5-C10-R5 now has the Model B artifact and an explicit disposition for every predeclared arm. The all-rows arm
including rejected papers remains NOT_RUN, and the assay-clean Model A sensitivity remains NEED_DATA. An expert
can verify the recorded raw spans locally; no independent human verification or scientific gate pass is claimed.
