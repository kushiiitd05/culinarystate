# Step 10 (reduced, D-076): ascorbic-acid kinetics pilot — pre-registration (DRAFT)

Status: **DRAFT_PENDING_SIGNATURES** (Kush, Parv). Written S171, 2026-11-08, by the coding agent from D-076, before
any full text was opened (`registry/evidence/aa_kinetics_source_candidates_v1.csv`, column `full_text_opened` = NO
for every row). This is a reduced version of the Step 10 card, not the full card: no 100-abstract double triage, no
dual human extraction. It is labelled MODEL_ASSISTED (D-045); every row is verified by both Kush and Parv.
Amended before any signature with the S178 options
(`reports/step10/aa_pilot_preregistration_AMENDMENT_S178_DRAFT.md`) as chosen in D-080 / D-081 / D-082 (ksh and prv, AI under D-071; not a human sitting). Until both humans sign it is a dated AI
draft. **Step 27 (SIM-VAL) is pre-announced RESEARCH_ONLY** (§5): this pilot shows the SIMULATE pathway on one
narrow domain; it cannot show that SIMULATE works for recipes.

## 1. Sources

CC-BY open-access papers found by Europe PMC and OpenAlex searches (S171), screened by the agent on title and
abstract only: 8 INCLUDE, 4 MAYBE, 4 EXCLUDE (storage-only, 150–190 °C model system, review). Each paper's licence is
confirmed on its landing page before use; a paper that is not CC-BY or CC0 is dropped and recorded, never stored.
Full texts are stored under `data/raw/aa_pilot/` (git-ignored) with SHA-256 in the extraction file.
Licence status at the lock (`registry/evidence/aa_kinetics_source_candidates_v1.csv`): CC-BY stated in the PDF only
for AAK-06 and AAK-09; every other paper reads UNKNOWN, **including AAK-01 and AAK-11, from which CAL rows were
already extracted**. Kush confirms each licence on the publisher page (AAK-01, 02, 04, 05, 08, 09, 10, 11 before
verification; the SIM-VAL papers AAK-03, 07, 12 from the landing-page badge only, without opening the text). If
AAK-01 or AAK-11 is not CC-BY or CC0, its rows are dropped before verification and the report says so. AAK-09: the
publisher version (CC-BY) is the one used; its repository copy is labelled CC-BY-NC-ND.

## 2. What a row is

One row = one first-order (or stated-order) **rate constant at one temperature, in one matrix, under one stated
condition set**, as the paper reports it (`fit_by=AUTHOR`), or one **(time, retained fraction) series** at one
temperature when the paper gives the points (`fit_by=NONE`, to be fitted by us). Paper-level Arrhenius parameters
(Ea, k_ref, T_ref) are kept as separate AUTHOR_FIT rows and are **not** used to fit anything; we fit only from
per-temperature k or raw points (SSOT §211.48: no Arrhenius from aggregates).

Required fields per row, each with a verbatim **source span** (quote, plus table/figure/page locator): analyte
basis (AA only, or AA + DHA), matrix, heating medium, temperature and where it was measured, time range, number of
time points, order, k and unit, dispersion type and value or NOT_REPORTED, n, assay method, and (AA leaching) whether
cooking water or syrup was assayed. A field the paper does not state is `NOT_REPORTED_BY_SOURCE`, never guessed.

## 3. Split (fixed now, before extraction and before any fit)

Unit = paper (lab group unknown at screening; paper is the proxy). Rank INCLUDE + MAYBE papers by
sha256(`aa-pilot-split-2026-11-08` ‖ DOI) ascending; the first 4 are **SIM-VAL** (held out for Step 27), the rest
**SIM-CAL**. Resulting assignment:

| Partition | Papers |
|---|---|
| SIM-VAL | AAK-12, AAK-07, AAK-03, AAK-05 |
| SIM-CAL | AAK-02, AAK-04, AAK-10, AAK-11, AAK-09, AAK-01, AAK-08, AAK-06 |

A paper dropped later (licence, no kinetic data) leaves the others in place, with no re-draw. If two papers share a
corresponding author or lab, both go to the partition of the lower-ranked one, and the move is logged. SIM-VAL rows are
extracted and verified like the others, but **only after** the SIM-CAL fit is frozen (hash committed): the agent is both
extractor and fitter, so it does not open a SIM-VAL full text before the freeze (Step 11.L firewall). The firewall is
made physical, not only behavioural (REV-B B2.3, F-09):
(a) Kush moves the SIM-VAL PDFs (AAK-03, 07, 12, and AAK-05 when downloaded: "save it, do not read it") out of
`data/raw/aa_pilot/` to a folder the agent session does not use, records their sha256, and puts them back only after
the Model A fit JSON and its sha256 are committed.
and (b) SIM-VAL rows are extracted by a separate agent session that did not run the fit, after the fit hash is
committed; it is given the frozen fit JSON's hash, never its estimates, before extraction ends.

Acquisition (S171): 7 of 12 PDFs fetched from their OA locations (AAK-01, 03, 06, 07, 09, 11, 12; SHA-256 recorded
at extraction). AAK-02, 04, 05, 08 and 10 refuse scripted downloads; a human downloads them in a browser, and the agent
does not work around the sites' checks. AAK-09's repository copy is labelled CC-BY-NC-ND; the publisher's version is
CC-BY. The licence is confirmed on the publisher's page.

## 4. Verification (human only)

Kush and Parv each check every row against its span: `VERIFIED`, `CORRECTED` (with the corrected value and span) or
`REJECTED`. A row becomes a PARAM row only if **both** mark it VERIFIED, or CORRECTED to the same value; anything else
stays out. Disagreements are adjudicated jointly and logged. Unverified rows never reach SIMULATE. Target: about 20
verified rows, of which at least 3 temperatures in at least 2 SIM-CAL matrices (so an Arrhenius fit is identifiable).

## 5. Then

Fit `sim_aa_1` (first-order, Arrhenius in T) on verified SIM-CAL rows only, and freeze and hash the fit. The §4
target becomes a minimum: if the verified, included rows (§6) do not give at least 3 temperatures in each of at
least 2 SIM-CAL papers, or the fitter refuses (`simulation/aa_pilot_fit.fit_model_a`: at least 2 papers, and the
design identifies Ea), Model A is **NEED_DATA**: no PARAM row, no SIMULATE route. Predict SIM-VAL retention and report the
error with no threshold (pilot, descriptive). **Step 27 is RESEARCH_ONLY from the start:** SIM-VAL holds 4 papers
(3 if AAK-05 is missing), below the plan's minimum of 5 groups (Step 15 G15-f), so no outcome of this pilot moves
`sim_aa_1` beyond NOT_VALIDATED / RESEARCH_ONLY. Report everything, including rows lost at each step.

## 6. Fit specification (added S171 after CAL extraction, before any verification or fit)

The agent has seen the extracted CAL values (16 rows, 4 papers), so this section is **not blind to the data**. It
is fixed before verification and before any fit, and the report must say so.

- **Inclusion:** `K_AT_T` rows with both verdicts VERIFIED (or the same CORRECTED value), first order, and
  60 °C ≤ T ≤ 100 °C (cooking range). Rows below 60 °C are reported but not fitted. `AUTHOR_FIT_EA` rows are never
  fitted; they are compared with our estimate afterwards.
- **Model A (primary):** ln k_ij = a_i − (Ea/R)(1/T_ij − 1/T_ref), with a separate intercept a_i per paper (matrix),
  one shared Ea, T_ref = 363.15 K (90 °C), unweighted least squares on ln k (dispersion is missing for most rows).
  Report Ea with SE, each a_i, the residual SD, and the between-paper SD of the a_i (σ_b).
- **Model B (sensitivity):** a separate Ea per paper wherever the paper has ≥ 3 included temperatures. Also an
  all-rows sensitivity fit, including the < 60 °C rows and the AI-flagged AAK-11.
- **Prediction for an unseen matrix (SIM-VAL, Step 27):** ln k(T) = mean(a_i) − (Ea/R)(1/T − 1/T_ref), with a
  95 % interval from σ_b, the residual SD and the parameter covariance. For each SIM-VAL row, record whether its
  verified k lies inside the interval and its ln-k error. Descriptive only: no threshold, no tuning after SIM-VAL is
  opened.
- **Freeze:** the Model A fit JSON (inputs, row ids, estimates, code hash) is committed and its SHA-256 recorded
  before any SIM-VAL full text is opened.
- **What sim_aa_1 may use:** only Model A estimates, labelled `PILOT_MODEL_ASSISTED`, n = (papers, rows); leaching
  (k_L, K_p) stays UNKNOWN (no included CAL paper identifies it), so WATER_IMMERSION runs return UNKNOWN for the
  leaching part.

## 7. Where a SIMULATE number may be used (added S178, before any verification or fit)

- **Domain gate.** A `sim_aa_1` output may be emitted only for an event that passes all of: (i) the matrix is on a
  matrix-class list of liquid or pulpy acidic fruit matrices (juices, nectars, pulps, purées, fruit in syrup),
  written as ING ids by the agent from the CAL matrices and committed with the lock; (ii) the pH condition below;
  (iii) temperature within 60-100 °C (the fit range, §6); (iv) NO_WATER_CONTACT, by a medium-to-contact map
  committed with the lock (`simulation/systems.py` requires the caller to supply it; unmapped media are refused).
  Any event outside the gate, or with any gate input UNKNOWN, gets no SIMULATE output (UNKNOWN never routes to
  SIMULATE). Leaching stays UNKNOWN (no CAL paper identifies k_L or K_p), so vegetables boiled in water stay UNKNOWN.
- **pH condition:** "matrix pH as stated in the paper, else NOT_REPORTED_BY_SOURCE" is added to the
  extracted fields of §2 for the CAL papers and verified with the other fields. The gate range is the minimum to
  maximum stated pH over the verified CAL papers. An event passes only if its food's pH interval in
  `registry/food_ph_fda2003_v1.csv` lies inside that range; a lower-bound-only entry or no entry is UNKNOWN. If fewer
  than 2 CAL papers state pH, the gate falls back to: no pH gate; the matrix-class list carries the acidity restriction and the
  report says "pH not gated".
- **Analyte basis.** `sim_aa_1` models reduced L-ascorbic acid with no DHA compartment, while the target SVAR-000009
  is total vitamin C (USDA 401). Every SIMULATE output is labelled "reduced ascorbic acid retention" and carries
  `BASIS_MISMATCH_TOTAL_VITC` wherever it is shown beside a total-vitamin-C value. SIM-VAL comparisons use only rows
  with the same analyte basis as the CAL rows; rows on another basis are reported separately.
- **Pre-declared sensitivities (D-AA-4; the primary Model A is unchanged):** Model A refitted (a) without CAL papers
  whose process has water contact (AAK-09, mango blanching, if its verified rows say so) and (b) without rows whose
  assay is not AA-specific (the AI flag on AAK-06, iodine titration, if verification confirms it). Both are reported
  beside the primary fit, never instead of it.

## Signatures (human only; D-071)

This file is signed only by `reports/step10/aa_pilot_prereg_signature_Kush.json` and
`reports/step10/aa_pilot_prereg_signature_Parv.json` (final names: the lock note), each typed and committed by its
signer before any verdict is read: `{"prereg_sha256": "<sha256 of this file>", "signed_by": "Kush Tokas" | "Parv
Goyal", "signed_date": "YYYY-MM-DD"}`. Nobody types a name into this file.
