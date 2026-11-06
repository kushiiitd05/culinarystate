# Step 19 pilot schema-problem log (text-free)

Entries use packet ids and field families only; no recipe text. Created S166 (D-063) from prv's re-check of annotator A's AI pass.

| SP id | Wave | Packet | Field family | Problem | Category | Rating effect | Status |
|---|---|---|---|---|---|---|---|
| SP-001 | P1 | DGP-A-0007 | steps.events / coref | The engine creates entities only from ingredient lines, so an ingredient named in the steps but absent from the ingredient lines cannot be an entity or an event target; it is kept as UNKNOWN coref plus an `unknowns` entry. The dish state loses a stated main component. | coreference/entity (tooling) | WORKAROUND (Kush, D-063; strict reading would be IMPOSSIBLE) | OPEN: needs a schema/engine decision (e.g. allow step-introduced entities) before P2 |
| SP-002 | P1 | DGP-B-0004, 0005, 0007 (and, by the same recipes, the committed A labels) | ingredient_lines quantity parse | Quantities written with U+2044 FRACTION SLASH ("1⁄4", "1 1⁄2") parse as a count of 1 and bare numbers become a `count` channel, so replay carries unsupported quantities. B pass 2 adds quantity overrides with an ASCII slash; A's labels were committed before this was found (D-063) and keep the defect. | quantity (tooling/source) | WORKAROUND for B; A's affected quantities must be treated as unreliable in scoring | OPEN: fix the quantity parser (normalise U+2044) before P2 |
| SP-003 | P1 | DGP-B-0001, 0002, 0006 | steps.events Merge/Split | Per-unit, repeated or partial use of an entity with an unstated share ("a slice", "a little", "a few", "repeat with the other"). Whole-entity Merge over-asserts consumption; Split with null fractions is the permitted workaround. | quantity/events | WORKAROUND | OPEN: handbook guidance for unstated shares |
| SP-004 | P1 | DGP-B-0003, 0006, 0007 | steps.events fields | Alternative or conditional values in one field (two cooking methods or times; a modal storage clause) are only representable as free text. | events/values | WORKAROUND | OPEN: schema decision on alternatives/conditionals |

## AI triage of SP-001..SP-004 (ksh SP-001/002, prv SP-003/004; 2026-11-06; AI verdicts pending human stamp, D-067 M5)

Design classes: BLOCKING / WORKAROUND / COSMETIC (design s9). THR-19P-25 needs every item triaged; this section supplies the AI triage, the human stamp is still needed.

| SP | AI severity | Root cause | Recommended route | Schema impact |
|---|---|---|---|---|
| SP-001 | WORKAROUND now; candidate BLOCKING (main component lost from final state) | `to_events` makes an `Add` only from `ingredient_lines` (src/culinarystate/annotation/gold.py:144-147); the engine creates entities only from `Add` (src/culinarystate/state_graph/engine.py:220-227); Addendum A.2 forbids hand-written `Add` | Short term: UNKNOWN coref + `unknowns` entry (Addendum B.1/B.2), TRIAGED_TO_16A. Long term: a step-sourced `Introduce` event (source span, quantity UNKNOWN) as a gold-1.1 proposal decided in Step 16 after more evidence | gold-1.x bump if adopted; H4 matter; never applied to the committed P1 labels |
| SP-002 | WORKAROUND (B overrides); A's affected cells quantity-unreliable for scoring | `UNICODE_FRAC` (src/culinarystate/quantity/grammar.py:16) lacks U+2044 and `normalize_text` (grammar.py:56-62) maps only precomposed fractions; `1⁄4 tsp` → NUMBER 1.0, `1 1⁄2 cups` → NUMBER 1.0, `1 ½ tbsp` → MIXED 1.5 | Test-first fix in `normalize_text` (map `(\d)\s*⁄\s*(\d)` → `\1/\2`) after human approval; `parse_line` has other callers (step12_local, line_link, ledgers/common, recipes/ledgers, ner/rule_ner, ingest/usda_yields_r2, bognar_remaining), so run a before/after diff of parsed ledgers first. A's P1 labels are not edited; a corrected-parse sensitivity column may sit beside the raw score | None (parser only); ledgers built from U+2044 recipes change on rerun |
| SP-003 | WORKAROUND | HANDBOOK_GAP: Split/Reserve already take a null portion/fraction; v1 has no rule for partial use | Addendum B (Split with null share, then act on the output; "repeat with the other" = a second event set) | None |
| SP-004 | WORKAROUND with a BLOCKING risk (a conditional that changes the cooking path is lost in free text) | SCHEMA_GAP: an ALTERNATIVE span exists but event fields hold one value | Addendum B (first-stated value in the field, the other as ALTERNATIVE span + note); TRIAGED_TO_16B for an optional `alternatives[]` field | Deferred to Step 16 |

STOP-SCHEMA (THR-19P-26/32) is not triggered: no item is adjudicated BLOCKING, and SP-001 is logged in one recipe per annotator. ksh notes the coref (0.96 per-pair) and event_type (0.76) rates are mostly not explained by SP-001/002; a separate adjudication is needed for the true causes.

## Human stamp (D-070, 2026-11-06)

All four items are triaged; THR-19P-25 is satisfied. Status for every row above: TRIAGED (route as stamped).

| SP | Severity | Adjudication class | Route |
|---|---|---|---|
| SP-001 | WORKAROUND | SCHEMA_GAP | TRIAGED_TO_16A |
| SP-002 | WORKAROUND | TOOLING | TOOLING_BACKLOG (parser fix after the presentation, D-070 O1) |
| SP-003 | WORKAROUND | HANDBOOK_GAP | ADDENDUM_B (B.4) |
| SP-004 | WORKAROUND (BLOCKING risk) | SCHEMA_GAP | TRIAGED_TO_16B (Addendum B.5 meanwhile) |
