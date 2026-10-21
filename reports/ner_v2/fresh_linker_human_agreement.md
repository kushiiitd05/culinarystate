# Fresh linker set -- human annotation QC (stage 1)

**Result: STOPPED at validation.** `Kush_ALL_441items_BLINDED.csv` and `Parv_ALL_441items_BLINDED_.csv` (note the trailing underscore in Parv's filename) are **byte-identical** (same SHA-256), so every one of the 441 decisions agrees by construction: they are the same file, not two independent annotations. Agreement, kappa, stratum breakdown and the adjudication file were **not computed or generated**, because any such number would be meaningless and would mislead.
No model was scored, `pool_key_DO_NOT_SHARE.json` was not opened, no model provenance was inspected. Hashes in `fresh_linker_annotation_manifest.json`.
Format validation of the (single distinct) file is reported in the session summary; no label was repaired.
Action needed from the annotators: Parv's independently filled sheet (from the blank `Parv_*` CSVs) or an explanation of how the two files came to be identical (e.g. a copy/export error), before the agreement analysis can run.
