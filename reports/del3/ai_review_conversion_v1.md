# AI-assisted pilot_20 conversion report (S105, D-016)

Source: OpenAI GPT-5.6 Sol draft (`blind_human_gold=false`), reviewed and accepted by Kush; converted to `gold-1.0` by `tools/convert_ai_review.py` under handbook v1 + Addendum A. Kush's 20 files: `DONE`, `validate` OK and replay issue-free for 20/20. Parv's 20 files: blank drafts (blind pass). Recipe text and per-event details stay local in `annotation/ai_review/pilot_20/conversion_log.csv`.

- Draft events: 189; gold events written: 183 (not 1:1, a draft multi-input TRANSFORM becomes Merge plus Transform); draft events NOT converted (no resolvable input): 13 in 5 recipes ({'R003595': 8, 'R004275': 1, 'R006967': 2, 'R009484': 1, 'R009647': 1}).
- Draft coref mentions: 113; the draft gave descriptive targets, not entity labels, so 108 are stored with entity `UNKNOWN` (handbook: unclear antecedent = UNKNOWN). **Coref is the weakest part of this set.**

| conversion decision (rule) | count |
|---|---|
| coref entity set to UNKNOWN (`COREF_TARGET_UNRESOLVED`) | 108 |
| event input matched to an entity by token overlap (`FUZZY_REFERENCE`) | 48 |
| span dropped: PURPOSE / QUALITATIVE_AMOUNT have no handbook label (`SPAN_DROPPED`) | 30 |
| free-text condition fragment not mapped to time/temperature/medium/tool (`CONDITION_NOT_MAPPED`) | 29 |
| SPLIT rewritten to handbook Split(target, outputs) (`SPLIT_REVIEW`) | 18 |
| draft RECOMBINE ('serve with', 'garnish', ...) written as Merge (`RECOMBINE_AS_MERGE`) | 18 |
| ingredient concept chosen by right-most head match in the ING registry (`CONCEPT_BY_HEAD_MATCH`) | 18 |
| Transfer location parsed from the output phrase (`TRANSFER_LOCATION_PARSED`) | 15 |
| draft TRANSFORM with 2-3 inputs written as Merge (`MULTI_INPUT_TRANSFORM_AS_MERGE`) | 14 |
| event written with only its resolvable inputs (`PARTIAL_INPUTS`) | 14 |
| event not written: no input resolvable (`UNRESOLVED_REFERENCE`) | 13 |
| water/juice input not an ingredient: kept as medium or split output (`IMPLICIT_LIQUID`) | 12 |
| event input matched by a contained entity name (`FUZZY_CONTAINMENT`) | 7 |
| draft WAIT written as Transform (`WAIT_AS_TRANSFORM`) | 6 |
| draft RESERVE of a whole item ('keep warm', 'set aside') not written as Reserve (`RESERVE_NOT_WRITTEN`) | 6 |
| draft MERGE with one input written as Transform (`SINGLE_INPUT_MERGE_AS_TRANSFORM`) | 5 |
| SPLIT naming one output got a remainder output (`SPLIT_SINGLE_OUTPUT_PADDED`) | 4 |
| concept UNKNOWN (no registry match) (`CONCEPT_UNKNOWN`) | 1 |

## How Kush's review works from here
Send corrections as one line per recipe (e.g. `R002919: event 4 should be Split+Discard`, `R008469: keep temperature qualitative`, `R003595: approve`). Each is applied by the coding agent to the local file, recorded with a one-line rationale in the correction log, and the original conversion is kept. Scientific labels are changed only on a human correction; the agent fixes schema/serialization problems only.

## Known limitations of this set
- Not blind, not independent; the draft's event model was reconciled to the handbook mechanically, so semantic choices (Merge vs Recombine, whole-item Reserve) follow the rules above, not annotator judgement.
- Coref is mostly UNKNOWN; entity labels and Split outputs were generated from the draft's phrases.
- Used for: development of the compiler evaluation and the state-replay tests. Not a test set and not publication-grade Gold.

**Biggest gap:** R003595 (baking, 8 steps) lost 8 draft events because the draft names intermediate products (e.g. the cake batter) that the engine cannot tie to an ingredient entity without a human decision; fix this one first on review.
