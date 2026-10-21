# Fresh linker set -- human agreement BEFORE adjudication (final Parv file)

Files (hashes in `fresh_linker_annotation_manifest.json`): `Kush_ALL_441items_BLINDED.csv`, **`Parv_ALL_441items_BLINDED_FINAL.csv`** (16:26, declared final by the annotators; earlier Parv versions -- byte-identical, cell-identical, and a low-agreement 15:58 version -- are superseded and not used), `RUBRIC_AND_INSTRUCTIONS.md`. No model was scored, no pool key or model provenance opened, no label repaired, nothing adjudicated by a model.

## Validity
441 rows each, identical id set and order, 0 duplicates, 0 malformed rows (valid decisions, MATCH/PARENT indices exist, NONE has a name, AMBIGUOUS has readings, confidences 1-3, no blanks), candidate columns identical.

## Agreement (raw counts; MATCH and PARENT kept separate)
- Exact judgment agreement (same class and same concept for MATCH/PARENT): **276 / 441 (62.6%)**. Class agreement: **284 / 441 (64.4%)**. **Cohen's kappa (class) = 0.500.**
- Class counts: Kush MATCH 174, PARENT 57, NONE 72, AMBIGUOUS 138; Parv MATCH 207, PARENT 25, NONE 157, AMBIGUOUS 52.
- Confusion (Kush -> Parv): MATCH->MATCH 153, NONE->NONE 65, AMBIGUOUS->NONE 57, AMBIGUOUS->AMBIGUOUS 50, AMBIGUOUS->MATCH 29, PARENT->MATCH 23, MATCH->NONE 18, PARENT->NONE 17, PARENT->PARENT 16, NONE->PARENT 4, MATCH->PARENT 3, AMBIGUOUS->PARENT 2, NONE->MATCH 2, NONE->AMBIGUOUS 1, PARENT->AMBIGUOUS 1.
- Concept-level agreement when both gave MATCH/PARENT: **180 / 195**; both MATCH: 145 / 153; both PARENT: 16 / 16.
- MATCH vs PARENT boundary disagreements: **26** (19 on the same concept = pure MATCH/PARENT strictness disagreement; 7 on different concepts). PARENT is Parv-rare (25 vs Kush 57).
- Among the 65 NONE-NONE pairs, typed ingredient names differ textually in 52 (descriptive; not auto-compared).

## By stratum (exact / class agreement, kappa)
S1 60/60, 60/60, 1.00 | S2 88/160, 93/160, 0.44 | S3 77/120, 78/120, 0.47 | S4 26/60, 26/60, 0.26 | S5 0/1 | S6 25/40, 27/40, 0.52.
## By confidence
both 3: 77 rows, 72 exact agree (93.5%). at least one 2 (none 1): 194 rows, 122 exact (62.9%). at least one 1: 170 rows, 82 exact (48.2%). Confidence-1 counts: Kush 78, Parv 118; either <= 2: 364.

## Disagreement categories (descriptive only; 165 rows to adjudicate)
AMBIGUOUS vs NONE 58 | AMBIGUOUS vs MATCH 29 | NONE vs PARENT 21 | MATCH vs NONE 20 | MATCH vs PARENT same concept 19 | MATCH vs a different MATCH 8 | MATCH vs PARENT different concepts 7 | AMBIGUOUS vs PARENT 3.

## Reading (descriptive, no adjudication)
Moderate class agreement (kappa 0.50); near-perfect on known surfaces (S1) and when both are certain; weakest on the ambiguous-generic stratum S4 (kappa 0.26). The main fault lines are the NONE / AMBIGUOUS boundary (58) and MATCH vs PARENT strictness (26), i.e. rubric interpretation, not concept identification (concept agreement 180/195 when both commit). Ambiguity rows should be kept as a separate stratum in the final gold rather than forced.

## Files
`fresh_linker_adjudication.csv` (165 rows, annotators randomly mapped to A/B, no model provenance; local-only because it contains recipe context lines, git-ignored; copy in `~/Downloads/fresh_linker_annotation/`), `fresh_linker_labels_normalised_PRE_ADJUDICATION.csv` (raw + canonical concept IDs), `_fresh_linker_agreement.json`, `fresh_linker_annotation_manifest.json`.
