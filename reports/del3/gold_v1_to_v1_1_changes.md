# Gold-v1 → v1.1 (proposed): reference repair and clean compiler rerun (S108)

**Status: PROPOSED, NOT APPROVED.** Every correction below is `AI_PROPOSED_CORRECTION`; none is `HUMAN_VERIFIED`. Gold-v1 (`pilot_20_adjudicated`) is unchanged. The provisional set is `pilot_20_adjudicated_v1_1_proposed/` (status DRAFT). Final `pilot_20_adjudicated_v1_1/` is created only by `tools/apply_gold_corrections.py` from rows Kush marks `approve` in `annotation/gold/gold_v1_correction_queue.csv`. Provenance when approved: AI-assisted + human-reviewed development Gold (not independent, not a test set). The rule compiler was **not changed** (`git diff` on `rule_compiler.py` is empty).

## Queue (67 rows; local file with source text)
Types: {'UNCONVERTED_EVENT+PADDED_REMAINDER': 1, 'UNCONVERTED_EVENT': 4, 'ANNOTATION_ERROR_FOUND_ON_AUDIT': 2, 'ANNOTATION_ERROR_FOUND_ON_AUDIT+UNCONVERTED_EVENT': 1, 'UNCONVERTED_EVENT+DOWNSTREAM_ARTEFACT': 2, 'DOWNSTREAM_ARTEFACT': 3, 'PADDED_REMAINDER+DOWNSTREAM_ARTEFACT': 1, 'PADDED_REMAINDER': 2, 'UNSUPPORTED_BY_SCHEMA': 1, 'COREF': 25, 'AUDIT_FLAG': 25}. Problem class (non-coref): {'CONVERTER_LIMITATION (name mismatch) + ANNOTATION/REPRESENTATION (pad)': 1, 'CONVERTER_LIMITATION (ambiguous fuzzy match between two almond lines)': 1, 'ANNOTATION_ERROR (draft); downstream effect on state': 1, 'ANNOTATION_ERROR (draft)': 1, 'CONVERTER_LIMITATION (named intermediates)': 1, 'CONVERTER_LIMITATION': 2, 'ANNOTATION_ERROR (draft) + CONVERTER_LIMITATION': 1, 'CONVERTER_LIMITATION (portion phrase) causing ANNOTATION ARTEFACT': 1, 'ANNOTATION ARTEFACT from the Reserve failure': 1, 'ANNOTATION ARTEFACT + REPRESENTATION (pad)': 1, 'ANNOTATION ARTEFACT': 1, 'CONVERTER_LIMITATION + ANNOTATION ARTEFACT': 1, 'REPRESENTATION (pad)': 2, 'ANNOTATION ARTEFACT (downstream of the step 1 pad)': 1, 'SCHEMA LIMITATION (documented; no change)': 1, 'AUDIT_FLAG': 25}. Recipes with step-level proposals: 7 (R002919, R003595, R004275, R006967, R007017, R009484, R011207).
Items distinguish **annotation error** (draft contradicts the source text, found on reading) from **converter limitation** (valid content the converter could not represent) from **schema limitation** (not representable: R009647 'chill the glass', a tool state; documented, no change).

Important: reading the 8 affected recipes against the source text found annotation errors **beyond** the 13 unconvertible events (for example R003595's glaze built from the cake batter, an 'anti-curdle' event that merges all the flour although the text makes it conditional, R004275's purée made from the reserved peas). The other 12 recipes were only checked by automated flags (25 `AUDIT_FLAG` rows), not read line by line.

## Split / remainder audit (4 single-output splits)
| recipe | what the text says | class | fix |
|---|---|---|---|
| R002919 | 'then halve' (cutting) | converter problem (my padding rule) | Transform sets form=halved; converter fixed + regression test |
| R004275 | 'divide the mixture between the moulds' (6 moulds from step 0) | converter problem (count comes from equipment, not the output string) | Split into 6 outputs, fractions null (handbook H5) |
| R007017 | 'divide guacamole between rye bread' (2 slices) | converter problem (same) | Split into 2 outputs, fractions null |
| R011207 | 'drop spoonfuls ... in batches' | annotation problem (batches are not entities, handbook H16) | Transform fry, no Split |
No engine representation limitation was found. No synthetic remainder entity remains in the proposed set.

## Coreference audit (113 mentions)
RESOLVABLE_EXPLICIT 1, RESOLVABLE_STRUCTURAL 26, GENUINELY_AMBIGUOUS 86, NOT_APPLICABLE 0. 25 proposals set an entity (rows type COREF); the rest remain `UNKNOWN` by design, with no target percentage. Structural = a pronoun or generic noun ('it', 'the mixture') with exactly one alive derived entity at the start of the step and no ingredient named earlier in the sentence. Of the 108 mentions still `UNKNOWN` in Gold-v1, 87 are pronouns (86 are the word 'it'); the rest are generic nouns ('the mixture' 4, 'the rest' 3, 'everything' 3, 'the sauce' 2, 'the dough' 2, 'the soup' 2). The draft supplied no entity antecedent for any of them, and the events carry no character offsets, so an 'it' cannot be tied to one event without a human reading the sentence.

## Compiler rerun (same compiler as S107; n=20; Gold = proposed v1.1)
| metric | S107 P | S108 P | S107 O1 | S108 O1 | S108 O2 | gold sanity |
|---|---|---|---|---|---|---|
| state-field accuracy | 0.102 | 0.140 | 0.130 | 0.159 | 0.146 | 1.000 |
| alive-entity F1 | 0.312 | 0.395 | 0.342 | 0.393 | 0.395 | 1.000 |
| merge/split/reserve F1 | 0.343 | 0.368 | 0.349 | 0.353 | 0.368 | 1.000 |
| relation F1 | 0.289 | 0.327 | 0.289 | 0.313 | 0.327 | 1.000 |
| event F1 (loose) | 0.199 | 0.237 | 0.207 | 0.232 | 0.237 | 1.000 |
| event-type F1 | 0.582 | 0.629 | 0.575 | 0.614 | 0.629 | 1.000 |

Event counts, gold → predicted: Merge 85 vs 60, Transform 83 vs 169, Split 16 vs 14, Transfer 21 vs 22, Discard 10 vs 10, Reserve 1 vs 8. Raw: `compiler_vs_gold_s108_proposed.json`.

## Answers
1. **Does oracle ingredient identity still give only a small gain?** Yes: O1 vs P is +0.019 state-field accuracy and -0.002 alive-entity F1 (S107: +0.028, +0.030).
2. **Is event construction still the dominant bottleneck?** Yes. With gold Add events (O2) nothing improves, and all structural metrics stay around 0.33-0.39.
3. **Over-produced:** Transform (about 2.0x Gold) and Reserve (8 predicted vs 1 in Gold).
4. **Missed / under-produced:** Merge (60 vs 85).
5. **How much did repair change the headline?** P state-field accuracy 0.102 → 0.140, alive F1 0.312 → 0.395, merge/split 0.343 → 0.368. The conclusions did not change; the numbers moved by roughly +0.03 to +0.08. These are provisional and still against AI-proposed corrections.
6. **Is Gold-state trustworthy enough to be the oracle arm of H_STATE?** **Not yet.** (a) the corrections are unapproved; (b) 7 of the 8 recipes I read against the source text needed substantive fixes, so the other 12 (not read line by line) may carry similar errors that automated flags cannot see; (c) coreference is still mostly UNKNOWN; (d) the set is AI-assisted, not independent. It is usable as a development oracle only.

No generalisation is claimed: 20 development recipes, one source.

## Verdict
**GOLD_ORACLE_NOT_READY**

Next action (one): **Kush reviews `annotation/gold/gold_v1_correction_queue.csv` and fills the `decision` column (approve / reject) for the 41 proposal rows, then runs `tools/apply_gold_corrections.py`; read the 12 unread recipes' `AUDIT_FLAG` rows first.**
