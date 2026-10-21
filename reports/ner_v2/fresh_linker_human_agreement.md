# Fresh linker set -- human agreement BEFORE adjudication

Files (hashes in `fresh_linker_annotation_manifest.json`): `Kush_ALL_441items_BLINDED.csv`, `Parv_ALL_441items_BLINDED_FILLED.csv` (third version, 15:58; two earlier Parv versions were byte- or cell-identical to Kush's and were rejected: see commit 5e91d38), `RUBRIC_AND_INSTRUCTIONS.md`. No model was scored, no pool key or model provenance was opened, no label was repaired or adjudicated by a model.

## Validity
441 rows each, identical id set and order, 0 duplicates, 0 malformed rows (all decisions syntactically valid, MATCH/PARENT indices exist, NONE has a name, AMBIGUOUS has readings, confidences 1-3, no blanks), candidate columns identical.

## Agreement (raw counts; MATCH and PARENT kept separate)
- Exact judgment agreement (same class and same concept for MATCH/PARENT): **137 / 441 (31.1%)**. Class agreement: **138 / 441 (31.3%)**. **Cohen's kappa (class) = 0.130.**
- Class counts: Kush MATCH 174, PARENT 57, NONE 72, AMBIGUOUS 138; Parv MATCH 71, PARENT 0, NONE 341, AMBIGUOUS 29.
- Confusion (Kush -> Parv): AMBIGUOUS->NONE 130, MATCH->NONE 93, PARENT->NONE 54, MATCH->MATCH 67, NONE->NONE 64, MATCH->AMBIGUOUS 14, AMBIGUOUS->AMBIGUOUS 7, NONE->AMBIGUOUS 5, PARENT->AMBIGUOUS 3, NONE->MATCH 3, AMBIGUOUS->MATCH 1.
- Concept-level agreement when both gave MATCH/PARENT: **66 / 67** (both MATCH: 66 / 67; both PARENT: 0 / 0 -- Parv never used PARENT).
- MATCH vs PARENT boundary disagreements: MATCH vs PARENT same concept 0, different concepts 0 (Parv has no PARENT labels; Kush's 57 PARENT all fall under NONE 54 or AMBIGUOUS 3).
- Typed NONE names differ between the 64 NONE-NONE pairs in 50 cases (descriptive; not auto-compared).

## By stratum (exact / class agreement, kappa)
S1 58/60, 58/60, 0.49 | S2 24/160, 25/160, -0.03 | S3 38/120, 38/120, 0.06 | S4 10/60, 10/60, -0.03 | S5 0/1 | S6 7/40, 7/40, -0.01.
## By confidence
both 3: 58 rows, all agree (58/58). at least one 2 (none 1): 283 rows, 62 exact. at least one 1: 100 rows, 17 exact. Confidence-1 counts: Kush 78, Parv 29; either <= 2: 383.

## Disagreement categories (descriptive only; 304 rows)
AMBIGUOUS vs NONE 135 | MATCH vs NONE 96 | NONE vs PARENT 54 | AMBIGUOUS vs MATCH 15 | AMBIGUOUS vs PARENT 3 | MATCH vs a different MATCH 1.

## Reading (descriptive, no adjudication)
Concept choice is reliable when both commit to a concept (66/67), and agreement is perfect on the 58 rows where both were certain. The disagreement is almost entirely **class**: Parv used NONE for 341 items (77%) and never PARENT, Kush used MATCH/PARENT/AMBIGUOUS far more. That pattern looks like a systematic difference in applying the rubric (when a candidate counts as "the same or a broader ingredient", and what counts as ambiguous), not random noise. It matters for scoring: the final gold depends on how those rules are settled, so a short joint calibration of the rubric rules before adjudication is advisable (a human decision; nothing here was resolved automatically).

## Files
`fresh_linker_adjudication.csv` (304 rows, annotators randomly mapped to A/B, no model provenance; local-only, contains recipe context lines, git-ignored), `fresh_linker_labels_normalised_PRE_ADJUDICATION.csv` (raw + canonical concept IDs for both annotators), `_fresh_linker_agreement.json`, `fresh_linker_annotation_manifest.json`; copy of the adjudication CSV in `~/Downloads/fresh_linker_annotation/`.
