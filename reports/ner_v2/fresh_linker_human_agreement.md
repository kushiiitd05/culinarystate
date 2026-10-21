# Fresh linker set -- human annotation QC (stage 1)

**Result: STOPPED; independence not established.** Both files validate syntactically (441 rows, same ids and order, 0 malformed rows, identical candidate columns), but:
1. `Parv_ALL_441items_BLINDED_.csv` is byte-identical to `Kush_ALL_441items_BLINDED.csv` (same SHA-256).
2. The replacement `Parv_ALL_441items_BLINDED_FILLED.csv` differs in bytes (formatting only) but **every parsed cell in every column is identical to Kush's**: decisions, confidences, notes, typed NONE names and AMBIGUOUS readings (0 cell differences). Computed on that pair: exact agreement 441/441, class agreement 441/441, Cohen's kappa 1.0, identical confidence profile (78 rows with confidence 1, 138 AMBIGUOUS, 57 PARENT, 72 NONE, 174 MATCH), identical free-text.
Perfect agreement with identical free-text and confidence on 441 hard items (138 ambiguous) is not what two independent human annotations produce, so these numbers are **not reported as agreement** and no adjudication file was generated (it would be empty and misleading).
No model was scored, `pool_key_DO_NOT_SHARE.json` was not opened, and no model provenance was inspected. Hashes: `fresh_linker_annotation_manifest.json`. Tooling: `tools/v2dm_fresh_agreement.py` (ready to run unchanged on a genuinely independent pair).
