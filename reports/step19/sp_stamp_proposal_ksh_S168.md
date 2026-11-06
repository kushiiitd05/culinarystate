# SP-001..SP-004 stamp proposal (ksh, AI verdict; human stamp pending, D-045 / D-067 M5)

Basis: `reports/step19/pilot_schema_problem_log.md` incl. the AI triage section; design s9; THR-19P-24/25/26/32/33. Text-free. Not a human stamp; Kush decides.

| SP | Final severity | Adjudication class | Route | One-line justification |
|---|---|---|---|---|
| SP-001 | WORKAROUND | SCHEMA_GAP | TRIAGED_TO_16A | The step-named food is kept in the label (UNKNOWN coref + `unknowns` entry), so nothing is invented or dropped from the annotation; the loss is only in the replayed dish state, which is why it is schema debt and a Step 16a proposal (step-sourced `Introduce`). |
| SP-002 | WORKAROUND | TOOLING | PARSER_FIX | U+2044 is not normalised in `quantity/grammar.py`; text stays exact, B overrides in ASCII, A's affected quantities are scored as unreliable; fix test-first with a before/after ledger diff. |
| SP-003 | WORKAROUND | HANDBOOK_GAP | ADDENDUM_B | Split/Reserve already accept null shares; v1 only lacks a rule for partial use (Addendum B.4). |
| SP-004 | WORKAROUND (BLOCKING risk noted) | SCHEMA_GAP | TRIAGED_TO_16B | Event fields hold one value; the ALTERNATIVE span plus note (Addendum B.5) preserves the content, an optional `alternatives[]` field is a Step 16b decision. |

## SP-001: WORKAROUND vs BLOCKING (explicit decision)

Proposed: **WORKAROUND**, consistent with Kush's D-063 rating.

Reason: THR-19P-26/32 define BLOCKING as "cannot annotate faithfully without inventing or dropping content". The annotator can record the food (UNKNOWN coref + `unknowns`); the schema cannot make it an entity, so the replayed state is incomplete. That is a representability limit of the derived state, not an annotation that had to invent or drop content. Under THR-19P-33 it is counted as silent schema debt (WORKAROUND) and reported next to any BLOCKING count; it is not hidden.

Consequence if WORKAROUND: THR-19P-26 (>= 3 distinct BLOCKING categories logged by both) not triggered; THR-19P-32 (>= 2 recipes with adjudicated BLOCKING on one field family) not triggered; no STOP-SCHEMA from SP-001.

Consequence if Kush instead stamps BLOCKING: THR-19P-26 still not triggered (one category). THR-19P-32 depends on whether the recipe SP-001 was logged in for A and for B is the same recipe (the log says one recipe per annotator; the A/B pairing is behind the sealed keys and was not opened). Same recipe = 1 recipe, no trigger. Two different recipes = 2 recipes on the field family `steps.events/coref` = STOP-SCHEMA for that family, escalate to Step 16. If SP-004 were also stamped BLOCKING on `steps.events` it would add recipes to the same family, so the family grouping must be decided at the same sitting.

Residual risk to state: SP-001 and the final_state disagreement rate (0.82 per-pair) are both about state; the 16a proposal should be decided on more evidence than 2 packets.

## THR-19P-25 (100 % triage)

After the human stamp, all four items carry a route and none is OPEN, so THR-19P-25 is satisfied (4/4). Until then it is not: the log Status column still reads OPEN for all four, and OPEN counts as not triaged. The AI triage alone does not count (D-067 M5). Two housekeeping points for the stamp: (a) the design triage vocabulary has TOOLING_BACKLOG where this request uses PARSER_FIX; record PARSER_FIX as the SP-002 value of TOOLING_BACKLOG or add it to the vocabulary; (b) the log columns `field_family`, `adjudication_class`, `convergent` are still unfilled; THR-19P-32 needs `field_family` (all four are `steps.events` / coref / quantity families as logged).

## Not decided here
Whether SP-001 and SP-004 share a field family for THR-19P-32; whether the A/B SP-001 recipes coincide (needs the key reveal, a human call); THR-19P-33 per-recipe checklist sheets were not inspected.
