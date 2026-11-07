# Step 10 (reduced, D-076): ascorbic-acid kinetics pilot — pre-registration (DRAFT)

Status: **DRAFT_PENDING_SIGNATURES** (Kush, Parv). Written S171, 2026-11-08, by the coding agent from D-076, before
any full text was opened (`registry/evidence/aa_kinetics_source_candidates_v1.csv`, column `full_text_opened` = NO
for every row). This is a reduced version of the Step 10 card, not the full card: no 100-abstract double triage, no
dual human extraction. It is labelled MODEL_ASSISTED (D-045); every row is verified by both Kush and Parv.

## 1. Sources

CC-BY open-access papers found by Europe PMC and OpenAlex searches (S171), screened by the agent on title and
abstract only: 8 INCLUDE, 4 MAYBE, 4 EXCLUDE (storage-only, 150–190 °C model system, review). Each paper's licence is
confirmed on its landing page before use; a paper that is not CC-BY or CC0 is dropped and recorded, never stored.
Full texts are stored under `data/raw/aa_pilot/` (git-ignored) with SHA-256 in the extraction file.

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
extractor and fitter, so it does not open a SIM-VAL full text before the freeze (Step 11.L firewall).

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

Fit `sim_aa_1` (first-order, Arrhenius in T) on verified SIM-CAL rows only, and freeze and hash the fit. Predict SIM-VAL
retention and report the error with no threshold (pilot, descriptive). Report everything, including rows lost at each
step.

## Signatures (human only; D-071)

- Kush Tokas: ______ date ______
- Parv Goyal: ______ date ______
