# Gold-v1 full 20-recipe source audit (S109)

Every recipe's ingredient lines, steps and events were read against the source text (handbook v1 + Addendum A). Checked: parent/intermediate lineage, merge/split sources, reserve/recombine, conditional instructions, optional/alternative ingredients, repeated lots and 'remaining' quantities, glaze/topping/dressing identity, transfers, endpoints, coreference, artificial remainders, entities that stay alive when the text consumes them. Nothing was changed because the rule compiler disagrees. Item ids refer to `annotation/gold/gold_v1_correction_queue.csv` (local); source text is not reproduced here.

| recipe | verdict | reason | queue items |
|---|---|---|---|
| R000312 | CORRECTION_REQUIRED | 3 of 4 dough balls never used (kept alive); 6 spurious coref entries ('it' inside words) | GC-089, GC-018, GC-019 |
| R000387 | CORRECTION_REQUIRED | two 'fry for a few mins' phases not recorded | GC-090 |
| R001894 | CORRECTION_REQUIRED | Merge process mis-canonicalised as 'trim' (text: spoon / top) | GC-091, GC-020, GC-021 |
| R002843 | CORRECTION_REQUIRED | wrong butter lot for the dish and the fish; cooked cod merged into the sauce and missing from the served dish | GC-092, GC-093, GC-094, GC-095, GC-022, GC-023, GC-024, GC-025 |
| R002919 | CORRECTION_REQUIRED | mayo missing from the mixing Merge; peel/chop missing; 'halve' padded with a remainder | GC-001, GC-026 |
| R003456 | CORRECTION_REQUIRED | ALTERNATIVE span/list hold the word 'or' instead of 'rapeseed oil' | GC-113 |
| R003595 | CORRECTION_REQUIRED | soak/drain/dry events unconverted; conditional flour treated as unconditional; batter omits flour+ground almonds and uses glaze milk; glaze built from batter; bakes/cool/wrap missing; alternative span | GC-002, GC-003, GC-004, GC-005, GC-006, GC-007, GC-114, GC-027, GC-028, GC-029, GC-030, GC-031, GC-032, GC-033, GC-034 |
| R004275 | CORRECTION_REQUIRED | asparagus discard and 6 tbsp Reserve missing; purée and mousse built from the reserved peas; padded remainder; serving ignores reserved peas; alternative spans | GC-008, GC-009, GC-010, GC-011, GC-115, GC-116, GC-035, GC-036, GC-037 |
| R006967 | CORRECTION_REQUIRED | spinach never squeezed/used; 12-15 min cook missing | GC-012, GC-111, GC-038, GC-039 |
| R007017 | CORRECTION_REQUIRED | guacamole Split padded with a remainder; sandwich lineage | GC-014, GC-040 |
| R007363 | CORRECTION_REQUIRED | set-aside chicken merged in step 0; chicken never returned; coriander halves not separated or served | GC-096, GC-097, GC-098, GC-041 |
| R008469 | CORRECTION_REQUIRED | roasting Merge uses the croutons' oil; soup base built by splitting 'soft onions'; croutons built from soup base; bread/oil unused; cream not split | GC-099, GC-100, GC-101, GC-102, GC-042, GC-043, GC-044, GC-045 |
| R008637 | CORRECTION_REQUIRED | carrots+grapes fused and put into the dressing; oil missing from dressing; bean water not discarded; half the feta not separated; alternative spans | GC-103, GC-104, GC-117, GC-118, GC-046, GC-047 |
| R009484 | CORRECTION_REQUIRED | optional grill step recorded as unconditional; squeezed liquid and wilting not recorded; alternative span | GC-013, GC-112, GC-119, GC-048, GC-049 |
| R009647 | CORRECTION_REQUIRED (coref noise only) | tool state (chilling the glass) is outside the schema (documented); retained ice discard is implicit (ambiguous, left) | GC-050, GC-051 |
| R009987 | CORRECTION_REQUIRED (coref noise only) | lineage, split of harissa, rest and serve all follow the text | GC-052, GC-053 |
| R010426 | CORRECTION_REQUIRED | final event is the label 'finish with'; stir-fry 3-4 mins not recorded | GC-105, GC-054 |
| R010532 | CORRECTION_REQUIRED | 'tear' and 'drain on kitchen paper' not recorded (minor) | GC-109, GC-110, GC-055, GC-056, GC-057 |
| R011207 | CORRECTION_REQUIRED | batter Split padded with a remainder; batches treated as entities; serving refers to a removed entity; alternative spans | GC-015, GC-016, GC-120, GC-121, GC-058, GC-059, GC-060 |
| R011481 | CORRECTION_REQUIRED | dough Split into 'or 10 dough portion N' entities with only portion 1 used; batches as entities | GC-106, GC-107, GC-108, GC-061, GC-062, GC-063 |

**Totals:** 20/20 audited; 18 CORRECTION_REQUIRED (substantive), 2 CORRECTION_REQUIRED (spurious coreference entries only), 0 PASS. Proposal rows needing a decision: 95 (46 are coreference-noise removals).

## What the audit found about the draft
- Most errors are **lineage** errors: the draft's chain of named intermediates sometimes merges the wrong lot (set-aside chicken, croutons built from soup, glaze built from batter).
- **78 of 113 coreference entries are not references**: the draft matched the letters 'it' inside words ('with', 'little'). They are proposed for removal. Of the 35 genuine mentions: 2 explicit, 4 structural, 1 expletive ('it's important'), 28 genuinely ambiguous (left `UNKNOWN`).
- 9 ingredient lines had the word 'or' as the ALTERNATIVE span instead of the alternative item.
- Two schema-level limits are documented, not corrected: tool states (chilling a glass) and partial portions of a lot with unstated size (represented with symbolic portions or null fractions).

## The 25 automated flags
| flag ids | recipe | verdict | handled by |
|---|---|---|---|
| 043-045 style (dough balls 2-4 alive) | R000312 | TRUE_ANNOTATION_ERROR | correction row (balls used) |
| butter never used | R002843 | TRUE_ANNOTATION_ERROR | correction rows (fish/sauce butter lots) |
| mayo never used | R002919 | CONVERTER_ISSUE (name 'mayonnaise' vs line 'mayo' not tied) | Gold row; converter limitation documented (no synonym in registry) |
| closed sandwiches remainder / mousse / guacamole / fritter remainders | R002919 R004275 R007017 R011207 | CONVERTER_ISSUE (padding) | converter fixed in S108 + Gold rows |
| almonds, ground almonds, milk never used; almonds 2 alive | R003595 | TRUE_ANNOTATION_ERROR + CONVERTER_ISSUE | correction rows |
| leaf spinach never used | R006967 | TRUE_ANNOTATION_ERROR | correction row |
| olive oil, rustic bread never used | R008469 | TRUE_ANNOTATION_ERROR | correction rows |
| olive/rapeseed oil 2 unused and alive | R008637 | TRUE_ANNOTATION_ERROR | correction row |
| 'or 10 dough portion 2-8' alive | R011481 | TRUE_ANNOTATION_ERROR (label artefact + batches) | correction rows |
No flag was classed SCHEMA_LIMITATION or VALID_AS_IS; 2 judgement items (R009647) are documented separately above.
