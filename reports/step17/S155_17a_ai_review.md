# S155 — Step 17a AI cross-review (DRAFT_PENDING_16c)

## AI verdict — pending Kush/Parv review

This is an **AI verdict, not an approval and not a human verification**. It was
produced by the AI worker "prv" (a worker label; not Parv) on branch
`cloud/s155-step17ab`. Kush and Parv review it afterwards; nothing here closes a
human gate, H4 item or 16c.

**Scope.** The five Step 17a modules written by the AI worker "ksh" —
`src/culinarystate/extraction/{interfaces,quantity_stages,validators,invariants,auditor}.py` —
and their tests `tests/unit/test_step17a_*.py` (152 tests at review start). The
review looked for correctness bugs, contract holes and over-claiming. Synthetic
text only; no real recipe was read.

**Verdict.** The interface and the delegation to the S154 rc2 pipeline look sound.
Quantity stages reimplement nothing, and failures are explicit. Seven real
defects were found. Four were in the invented-value auditor and V3/V4 contract
coverage, where values or references passed although they should not have; three
were in the interface contract. All seven are **FIXED**. Each fix has a RED test
first, in `tests/unit/test_step17a_review_fixes.py`, followed by a separate fix
commit. Nine further items are **OPEN** for human decision. Most are draft
semantics that the sources do not settle.

## Findings

| id | severity | evidence (synthetic reproduction) | disposition |
|---|---|---|---|
| R1 | HIGH | `auditor.audit_claim` SPAN_LITERAL checked number membership and a unit substring separately. On the span `"Bake 20 minutes at 180C"`, DURATION = 180 with unit `minutes` passed with `invented_count` 0, even though the 180 was a temperature. The unit was also matched inside words: `"C"` matched in `"Cook"`. | **FIXED** in `38cecf0`: a literal span may hold no number other than the claim's (`SPAN_HAS_OTHER_NUMBERS`), and the unit must be a whole token. RED test: `2d4fdee`, test-fixture follow-up `c49733d`. |
| R2 | HIGH | `numbers_in_text("-18°C")` returned {18}. A TEMPERATURE claim of +18 on `"-18°C"` therefore passed as literal, and the correct value −18 was flagged as invented. | **FIXED** in `38cecf0`: a minus sign (`-` or U+2212) attached to a number is read as a sign unless it follows another number, so range dashes such as `20-25` and `1 - 2` keep both numbers positive. |
| R3 | MEDIUM | `StageConfig.config_hash` covered only rung, params, model and schema. Configurations with different `claim_route`, `annotated_labels` or `annotation_mode` had identical hashes, although their outputs differ (origin, MISSING vs ANNOTATED). | **FIXED** in `03f2d7b`: all three are hashed, with labels sorted. |
| R4 | MEDIUM | "All referenced IDs exist" was checked only inside one EventGraph. A ReferenceResult naming a ghost mention or ghost entity, or a LinkResult for a ghost mention, passed V1–V4 and the audit. | **FIXED** in `6582614`: `run_validators` V4 checks mention ids and entity ids across outputs (`REFERENCED_ID_MISSING`). A missing target output is reported in `not_checked`. |
| R5 | MEDIUM | V3 skipped categorical claims whose field has no vocabulary, and did not list them in `not_checked`, so for example `process_family = "MADE_UP"` passed silently. Identifier claims outside LinkResult were never compared with the supplied id sets. | **FIXED** in `15c5c68`: `CATEGORICAL_FIELD_NO_VOCAB:<field>` is listed in `not_checked`, and identifiers are checked by prefix (`IDENTIFIER_NOT_IN_ID_SET`, or `ID_SET:<ns>` when no id set is supplied). |
| R6 | LOW | `Span.of(s, 1.7, 3)` and `Span.of(s, True, 3)` were silently truncated to `(1, 3)` by `int()`, producing a span that round-trips but was not what the caller requested. | **FIXED** in `a44000b`: non-int offsets are refused (`SPAN_SEGMENT_TYPE`). RED test: `fd31efe`. |
| R7 | LOW | `EventCandidate.order` was not type-checked. An order of `(0, "x")` made `v4_invariants` raise `TypeError` instead of reporting an issue. | **FIXED** in `a44000b`: the order must be a tuple of two ints. |
| O1 | MEDIUM | `ValidationReport.status` is `PASS` when nothing was checked. For example, V2 without a QNT schema returns PASS with `not_checked=("QNT_SCHEMA_NOT_SUPPLIED",)`. A consumer that reads only `status` over-reads this. | OPEN: does a "NOT_CHECKED" status replace PASS? Changing it alters the report semantics that the 17a tests pin. Meanwhile the Rung A reports count `not_checked` separately and always supply the QNT schema. |
| O2 | MEDIUM | A SPAN_LITERAL TEMPERATURE or DURATION without a unit is accepted (the 17a test `bake_time (20, 25)` has no unit). The number is literal, but its unit is not stated. | OPEN: is a unit required for literal magnitudes? Rung A always emits the raw unit token. |
| O3 | LOW | `invariants._consumption_order` checks only `consumes` for "nothing consumed after DISCARD". A later DISCARD, or an allocation whose parent was already discarded, is not flagged. | OPEN: does splitting or discarding count as consumption? The sources do not say. |
| O4 | LOW | Split fractions are summed per (parent, event, basis), so two RESERVE events of 3/4 each on the same parent are not summed. | OPEN: are fractions relative to the current entity version? Grouping by event is defensible under event sourcing. |
| O5 | LOW | `ground_quantity` returns `failure` (for example UNRESOLVED for `NO_INGREDIENT_LINK`) while the record still carries a known count or volume channel that `claims()` exposes. "Failure" therefore means "no grams", not "stage failed". | OPEN: H4 needs to rule on the failure semantics for partial QNT records. |
| O6 | INFO | `REGISTRY_LABEL` categorical values are not compared with anything by the auditor; membership is V3's job only, and only for vocabulary fields. Since R5 this gap is at least visible in `not_checked`. | OPEN for an H4 vocabulary list per field. |
| O7 | INFO | The draft tables `ROUTE_TO_ORIGIN`, `ALLOWED_FAILURES`, `GROUNDING_FAILURE_MAP` and `MENTION_LABELS_*`, and the Plan-vs-SSOT V1–V4 numbering, are AI choices or discrepancies that ksh already marks for H4. | OPEN (H4 / 16c). |
| O8 | INFO | `StageConfig` holds a mutable `params` dict in a frozen dataclass, so it is unhashable and `config_hash` can change if a caller mutates `params` after outputs were produced (outputs keep their own copy of the hash). | OPEN: freeze `params` (for example as a MappingProxy) at 16c. |
| O9 | INFO | Unused imports: `dataclasses.field` in `interfaces.py` and `EntityCandidate` in `test_step17a_auditor.py`. These are cosmetic and not defects. | OPEN (cosmetic). |

## What was checked and found sound (AI reading, not a proof)

- `quantity_stages` passes the raw span surface to `parse_quantity_v2` and
  `ground_quantity_rc2` unchanged and reimplements no arithmetic, units, locale
  or POR choice. `ContractError` propagates as caller misuse.
- `interfaces` rejects silent guesses structurally: a link's `selected_id` must be
  among its candidates, and a reference has antecedents or a failure, never both.
  A failed MentionSet carries no partial mentions.
- V1 checks the raw hash, text id, segment bounds and order, the texts and
  explicit-without-span claims. V2 enforces the exact declared `schema_version`
  and strict JSON (NaN/inf rejected).
- The auditor accepts grams and millilitres only through QNT records that pass
  the S154 `audit_invented_values`. It re-parses the AST from the raw span and
  re-derives the volume and count channels by Q0. An unregistered rule counts as
  invented.

## Evidence of the fixes

- RED tests: `tests/unit/test_step17a_review_fixes.py`, 12 tests (R1–R7 plus
  controls showing that tight literals and range dashes still pass).
- Full 17a + 17b targeted run after the fixes: 203 passed. All 152 original 17a
  tests still pass unchanged.
- Full unit suite (CPU thread caps): 2000 passed, 17 skipped, 1 deselected, with
  1 failed and 11 errors. The failure and errors are the same missing data-bundle
  files as before S155, so there is no new failure.
- No pre-S155 file was edited. The fixes touch only ksh's S155 files.

## Items left for humans

R1–R7 are fixed but need human confirmation that the fixes are wanted. O1–O9 are
open and listed above. Nothing in this review is human-verified.
