# SIM-VAL source precheck — 2026-11-11

Status: **AI_PRECHECKED; NO_HUMAN_SIGNOFF_D085**.

Separate AI source/context precheck only. This is not independent human gold, human signoff, or inter-annotator agreement.

- Finalized extraction rows checked: 19.
- Decisions: PASS 6; FLAG 12; REJECT 1.
- Licensed source PDFs checked: 2. Licence-blocked sources kept excluded without opening text: 1.
- Row kinds: author rates at temperature 3; author activation-energy aggregates 8; author pre-exponential aggregates 7; licensing exclusion 1.
- Raw time/retention observations: 0. Rows computationally eligible after this precheck: 0.
- Flag categories (overlapping): unresolved assay basis 4; isothermal context/exponent serialization 7; explicitly uncertain reaction order 2.

All row decisions, source locators, exact units/scaling checks, quantities, and source detail are confined to the ignored annotation CSV. PASS records source fidelity only; it does not grant fit or validation eligibility. FLAG requires analyst exclusion/review; ambiguities were not cured or silently normalized. Author aggregates remain separate from raw kinetics. No fits or predictions were performed.

Local `pdftotext -layout` was run directly on the two licensed PDFs. Explicit raster numeric labels were additionally checked against an existing rendering of a licensed PDF page; no graph digitization was used. Publisher licence state was accepted from the finalized manifest and not independently revalidated. The licence-blocked PDF was not opened or text-extracted. Temporary layout text created for this review was removed after inspection.

The frozen fit hash was provided as an opaque preregistration token only. No Model A fit output, CAL source material, identifiability output, fit estimates, predictions, integrated reports, or prior extraction-author script was opened. Finalized extraction and manifest were not modified. No shared brief, DECISIONS, log, or commit was created.

SHA-256 provenance:

- Frozen fit token supplied: `b9247db03e98423f8866fa50b24e2ecd33831d907f3aace00b1f7e4f2ea9543f`
- Finalized extraction, verified before and after: `2ad09c578b7be970ff1fa9ae4fead545a381945c095252c5d5967ae7a3a4554f`
- Extraction manifest: `88cbc8bec37421643d9da9e8df784e2a5a5a1341357ad26c02dfd76f6ece0d36`
- AAK-03 PDF: `416081ff6c2c90500db507c1a08a4ba747d0ce02aa6213b87c983fa12de5a0a9`
- AAK-07 PDF: `d6c3d67c361fc7f2e356d8015444425b561a665d33ca8ae8e0f24f6faa4066cf`
- Ignored source precheck CSV: `c5565cac24bc6a583ae08f3dcfc87a4f88df014f1df1d37da733228ec6381aa8`

Ignored artifact: `annotation/aa_pilot/aa_pilot_SIMVAL_source_precheck_2026-11-11.csv`.
