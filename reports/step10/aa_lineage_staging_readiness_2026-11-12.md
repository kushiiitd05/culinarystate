# AA source-bound staging and remaining scientific dependencies — 12 November 2026

**AI_PRECHECKED / DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.** Reviewer: author-only review (AI-delegated). Model A remains NOT_VALIDATED / RESEARCH_ONLY. This post-hoc technical/source assessment does not repeat the original held-out extraction firewall or claim independent human verification.

The new staging tool completes a source-bound candidate packet for all 35 existing extraction rows: 16 SIM-CAL and 19 SIM-VAL. Full rows remain in an ignored private JSON; the public JSON contains only identifiers, source hashes, dependency states and counts. Original extraction, source precheck, frozen Model A, input scientific values, protected ledgers and eligibility rules are unchanged. Eight synthetic contract tests pass after the initial missing-module failure.

## Completed reconciliation and correction

- Every PDF hash matches its extraction row. CAL matches the return bound by frozen Model A. SIM-VAL matches its finalized manifest and the exact published precheck hash. Licence status is taken from the existing D-085 publisher-page record, not inferred from PDF filenames.
- Exact normalized DOI matching finds no existing SRC, DOC or STUDY link for any of the 35 rows. There are 488 SRC, 1,967 DOC and 132 STUDY latest records. SEXP, OBS, KIN, KINPT, PARAM and FORM latest-record counts are all zero. No ledger ID is invented or borrowed from a loosely matching paper.
- Seven AAK-03 author pre-exponential aggregate rows carry a pH value from the non-isothermal composition table. The new staging view sets the corresponding isothermal pH metadata to NOT_REPORTED_BY_SOURCE and retains the original non-isothermal value separately. The original row is copied intact. This closes the context annotation inconsistency without rewriting the finalized extraction or creating a measurement. Exponent normalization is explicitly not performed; the author aggregates remain excluded from first-order validation.
- The two licensed SIM-VAL texts were re-examined by this AI context. AAK-07 describes a UV265 absorbance assay without demonstrating analyte separation/AA specificity in that text. The three author rate rows therefore retain the assay-basis exclusion; the source does not supply a defensible new AA-specific eligibility fact. AAK-03 describes an oxidase-blanked assay consistent with reduced-AA measurement, but its retained outputs are zero-order/uncertain-order author aggregates rather than comparable first-order per-temperature rates or raw trajectories. This distinction is preserved. No blocked PDF text or publisher bot check was bypassed.

## Counts and scientific disposition

The source set comprises 16 per-temperature rate summaries, 11 author activation-energy aggregates, seven author pre-exponential aggregates and one source exclusion. All 35 are staging candidates, never production PARAM records. Eight rows have unconfirmed publisher licences; seven CAL rows retain rejecting verdicts; all 19 SIM-VAL rows retain their precheck/comparison exclusions. There are zero production-eligible rows and zero minted IDs.

Author rate summaries can enter the declared narrow pilot fitter when its inclusion rules permit. They cannot generate missing source time/concentration observations, KINPT/OBS rows or an experimental lineage chain. A schema-complete KIN/PARAM chain therefore cannot be created truthfully from these files alone. Staging schema validity would not satisfy the separate production requirement for HUMAN_VERIFIED source data, FORM, held-out VAL and domain lineage.

The actionable packet for a later source/subject expert is the private staging JSON whose path/hash is bound by the public report. Its original rows, prechecks and separately corrected metadata can be checked against the source PDFs and exact IDs. Resolving absent observations or assay specificity requires additional source evidence. Until then, real scientific simulation and validation remain refused. This is a completed staging/reconciliation artifact, not a claim that those scientific prerequisites are complete.

## Reproduction

Run `python tools/s179_aa_lineage_readiness.py --out <new-public-json> --private-out annotation/aa_pilot/<new-ignored-json>`. Existing output paths are refused. Public report: `aa_lineage_staging_readiness_2026-11-12.json`; code/input/private-packet SHA256 and actual UTC timestamps are included. Private output must be ignored and inside `annotation/aa_pilot`; quantities and source quotes never appear in the public result. The CLI hashes PDFs as bytes without opening their text.
