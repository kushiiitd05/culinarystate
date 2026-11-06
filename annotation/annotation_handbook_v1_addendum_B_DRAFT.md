# Annotation handbook v1 — Addendum B (DRAFT_PENDING_HUMAN_STAMP, 2026-11-06)

Status: AI-drafted by ksh (B.1–B.10, from SP-001/SP-002 and the flagged coref/entity_type categories) and prv (B.11–B.23, from SP-003/SP-004 and the flagged coref, event_type, final_state, event_argument and entity_type categories), after the P1 handbook gate returned HANDBOOK_REVISION_REQUIRED (`reports/step19/p1_agreement_counts_S166.json`; THR-19P-16/31). Not in force until Kush and Parv stamp it. Applies from the next wave; **P1 labels are never edited or re-scored under it** (design s5.6, D-063, D-066). Examples use invented dish words.

Conditions before stamping (prv): each rule needs its P1 recurrence count (>= 3) and adjudication class confirmed; B.11–B.23 are untested on the schema; the Merge/Split boundary (B.15/B.16) is the least certain wording.

## From SP-001 / SP-002 and flagged categories (ksh)
- **B.1** A food named in a step but absent from the ingredient lines gets no ingredient entity: use UNKNOWN coref plus one `unknowns` entry naming the step; never add a line or an `Add`. (SP-001)
- **B.2** Never edit `text` or add a synthetic line to make an entity exist; a validator warning in a B.1 case is expected and logged as SP-001, not suppressed.
- **B.3** Write quantity text exactly as in the source; if the replayed quantity disagrees with the text (e.g. a count of 1 for a fraction), set `quantity_override` in ASCII (`1/4`, `1 1/2`) and log SP-002 until the parser is fixed. (SP-002)
- **B.4** Never accept a replayed `count` channel for a bare fraction or mixed number without a unit: add an override or UNKNOWN.
- **B.5** A pronoun or definite reference ("the mixture", "them") goes in `coref` with the entity that holds that content at that step, or UNKNOWN; never choose between two plausible antecedents.
- **B.6** An intermediate output gets a new label from the event that creates it and is never reused as an ingredient entity name.
- **B.7** Entity role follows the span's role in the sentence: INGREDIENT for a list item, INTERMEDIATE for any product of Merge/Split/Reserve; a later mention of the same food keeps the earlier entity.
- **B.8** An action on an unnamed share ("a little", "a slice") uses Split with null fractions; never a whole-entity Merge or Discard. (SP-003; see B.15)
- **B.9** An alternative or conditional value (two times, modal storage) is recorded with `Alternative:` first in `notes`. (SP-004; see B.20)
- **B.10** Use only the event types in the REQUIRED table; a verb that fits two types takes the type that changes the stated state (Transform over Observe).

## Coref (prv)
- **B.11** Every later mention of an alive entity that is an event argument ("the X", "the mixture", "them") appears in `coref` with its antecedent; a non-argument, non-pronoun mention is exempt. Ex: "Fold the plum paste into the oat base … stir the base" → coref "the base" → oat base.
- **B.12** Pronouns are coref only, never entity spans; two plausible antecedents → UNKNOWN + note. Ex: "Mix kelp and salt, then rinse it" → "it" UNKNOWN.
- **B.13** A re-mention of an intermediate links to the Merge/Split `output` label of the step that made it; no new entity or INTERMEDIATE span. Ex: "whisk the zing-glaze … drizzle the glaze" → one output.

## Event type (prv)
- **B.14** Write an implicit Merge/Split/Transform only if the text could not be true without it (a new named product appears, or a stated entity is added to a vessel holding a named product); otherwise write nothing.
- **B.15** Partial use ("a slice", "a little", "a few", "half") is Split with portion/fraction null unless stated, then the verb on the Split output; whole-entity Merge only for "all", "the rest" or a whole-count item. Ex: "Grate a little of the quince-cheese" → Split(null) then Grate.
- **B.16** Reserve when the text says to set aside or keep and a later step reuses it; Split for any other division, including a discard; "repeat with the other X" is a second event set on the other entity. Ex: "Set aside a splash of brine" → Reserve.

## Final state (prv)
- **B.17** Never hand-type final state: after `replay`, check that every entity the text leaves alive is alive and that no composition/qty/state field exists that the text does not state.
- **B.18** Each alive entity has at most one container/location, set by the last event that moves it; "serve" ends the entity there and does not discard it.

## Event arguments (prv)
- **B.19** Temperature and time belong to the event whose verb they modify and are not inherited; an oven setpoint is a TEMPERATURE span on the oven/heat event, never a food core temperature.
- **B.20** Stated values only (no inferred inputs, times or amounts); with two times or methods ("10 or 12 mins") write the first value and log the second as ALTERNATIVE + note; a qualitative "until golden" is an ENDPOINT, not a TIME.
- **B.21** `medium` is what the food is in (stock, hot oil); `tool` is the vessel or equipment (pan, oven); a vessel is never a medium.

## Entity type (prv)
- **B.22** FOOD spans the head noun with its modifiers; FORM, STATE and SIZE are nested spans inside it; a food word inside a tool or intermediate name is not a FOOD span.
- **B.23** UNIT is a measure word after a QUANTITY ("2 cloves", "1 jar"); a container word with no number is TOOL.

## Overlaps to resolve when stamping
B.5 ≈ B.11/B.12 (coref), B.8 ≈ B.15 (partial use), B.9 ≈ B.20 (alternatives): keep one wording each.
