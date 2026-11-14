# SIM-VAL extraction precheck — 2026-11-11

Status: FINAL_EXTRACTION, AI_DRAFTED / AI_PRECHECKED, NO_HUMAN_SIGNOFF_D085.

A separate extraction agent received only the frozen Model A fit SHA-256 before extraction completed: `b9247db03e98423f8866fa50b24e2ecd33831d907f3aace00b1f7e4f2ea9543f`. It did not open the fit JSON, its estimates, CAL source text or sheets, identifiability outputs, integrated report, D091, or earlier chat context. This is process/context separation, not independent human validation. No model was fitted and no prediction was made.

Frozen private extraction: `annotation/aa_pilot/aa_pilot_SIMVAL_extraction_2026-11-11.csv`.

SHA-256: `2ad09c578b7be970ff1fa9ae4fead545a381945c095252c5d5967ae7a3a4554f`.

Ignored completion manifest: `data/raw/aa_pilot_simval_quarantine/aa_pilot_SIMVAL_extraction_2026-11-11.manifest.json`.

Manifest SHA-256: `88cbc8bec37421643d9da9e8df784e2a5a5a1341357ad26c02dfd76f6ece0d36`.

Observed extraction completion UTC: `2026-11-11T17:16:50.122898+00:00`.

| Row class | Count |
|---|---:|
| K_AT_T | 3 |
| AUTHOR_FIT_EA | 8 |
| AUTHOR_FIT_K0 | 7 |
| SOURCE_EXCLUSION | 1 |
| Total | 19 |
| Raw time/retention points | 0 |

AAK-03 and AAK-07 were used under existing publisher-page CC-BY confirmation records. AAK-12 was excluded: the DOI could not be opened and the publisher landing page returned HTTP 403; institutional metadata did not satisfy the required publisher-page confirmation. Its PDF text was not opened. AAK-05 was not supplied in this acquisition.

AAK-03 provides only separate author Arrhenius aggregates in this extraction, with stated order outside the primary first-order comparison. Explicit printed figure labels were transcribed visually; no bar heights, coordinates, error-bar bounds, or time-series graph points were digitized. AUTHOR_FIT_K0 rows are pre-exponential factors and must never be interpreted as K_AT_T or used to fit an Arrhenius relation. No exact per-temperature k/raw-point table was located.

AAK-07 extraction includes only the table's AA component, excluding monomeric anthocyanins. The stated AA assay does not establish total AA+DHA; assay specificity and comparison basis need review. Fitting errors are not represented as parameter dispersion. Unstated fields use NOT_REPORTED_BY_SOURCE. Numeric observed kinetics and source spans remain in ignored private files.

Local structural checks confirmed row counts and status labels, no K values on aggregate/exclusion rows, and consistency of the table's rate-unit scaling with its printed half-lives. PDF table/figure-label renderings were inspected locally. Every row remains unverified by humans.
