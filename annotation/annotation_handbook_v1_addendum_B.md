# Annotation handbook v1 — Addendum B (STAMPED 2026-11-06, D-070; in force from P1b/P2)

Status: AI-consolidated by ksh from the ksh/prv draft (B.1-B.23) after the P1 handbook gate returned HANDBOOK_REVISION_REQUIRED (`reports/step19/p1_agreement_counts_S166.json`; THR-19P-16/31). **Stamped by Kush (Parv relayed), D-070: the issued rules below are in force from P1b/P2; held rules are not.** Applies from P1b/P2. **P1 labels are never edited or re-scored under it** (design s5.6, D-063, D-066). Examples use invented dish words. Design rule: a rule needs recurrence >= 3 (design s8).

How recurrence was counted (counts only, no text): packets = the 14 committed P1 label files (A 7 + B 7), "pass-1 edit" = a difference between the AI pass-1 draft and the committed label (the must-fix trail), "pairs" = the 7 A/B pairs with a flagged gate category (the pair counts are category-level and cannot be attributed to one rule). "Exposure" = the pattern occurs in the committed label but the count does not say it was mis-labelled; the real per-rule disagreement class count comes only from the adjudication rows (THR-19P-24) and may move any rule across the threshold.

## Issued rules (recurrence >= 3)

- **B.1 Quantity text and override** (old B.3+B.4). Write quantity text exactly as in the source. If the replayed quantity disagrees with the text (a count of 1 for a fraction, a bare number turned into a `count`), set `quantity_override` in ASCII and log SP-002 until the parser is fixed. Ex: "1⁄3 dram of zorp" → text unchanged, override `1/3`. Retire when the SP-002 parser fix lands.
  Evidence: 6 packets (A 3, B 3) carry U+2044 quantities; 3 B packets carry overrides; source SP-002; gate category `quantity` (35 disagreements, 7/7 pairs).
- **B.2 Coreference** (old B.5+B.11+B.12). Every later mention of an alive entity that is an event argument ("the X", "the mixture", "them") is a `coref` entry pointing to the entity that holds that content at that step; pronouns are coref only, never entity spans. If two antecedents are plausible, use UNKNOWN plus a note; never pick one. Ex: "Mix kelp and salt, then rinse it" → "it" UNKNOWN.
  Evidence: 7 packets with pass-1 coref edits (A 4, B 3); 6 packets with UNKNOWN coref (A 1, B 5); 7/7 pairs flagged `coref` (per-pair rate 0.96). Source: gate category `coref`.
- **B.3 Re-mention of an intermediate** (old B.13). A later mention of an intermediate links to the `output` label of the Merge/Split that made it; no new entity and no INTERMEDIATE span. Ex: "whisk the zing-glaze … drizzle the glaze" → one output, one coref.
  Evidence: 13 packets (A 7, B 6) contain coref to an event output (exposure). Source: gate categories `coref`, `entity_type`.
- **B.4 Partial use of an entity** (old B.8+B.15, plus "repeat with the other" from old B.16). Partial use ("a slice", "a little", "a few", "half") is a Split with portion/fraction null unless stated, then the verb acts on the Split output; a whole-entity Merge is only for "all", "the rest" or a whole-count item. "Repeat with the other X" is a second event set on the other entity. Ex: "Grate a little of the quince-cheese" → Split(null) then Grate.
  Evidence: 9 packets (A 5, B 4) use Split with an unstated share; SP-003 logged in 3 B packets. Source: SP-003; gate category `event_type` (74 disagreements, 7/7 pairs).
- **B.5 Alternative or conditional values** (old B.9+B.20, alternatives part). Write the first-stated value in the event field and the other as an ALTERNATIVE span with a note (`Alternative:` first); a modal storage clause is recorded the same way. Never average or choose silently. Ex: "bake 10 or 12 mins" → TIME 10, ALTERNATIVE "12".
  Evidence: 6 packets (ALTERNATIVE spans in A 2, B 2; SP-004 also in B 3, union 6). Source: SP-004; gate category `event_argument` (22 disagreements, 7/7 pairs).
- **B.6 Implicit events** (old B.14). Write an implicit Merge/Split/Transform only if the text could not be true without it (a new named product appears, or a stated entity is added to a vessel holding a named product); otherwise write nothing. Ex: "Stir the plum paste into the oat base" → Merge with a named output only if the text names the result.
  Evidence: 12 packets (A 7, B 5) carry `implicit` events (exposure); 1 packet shows a pass-1 event-count and type edit; 7/7 pairs flagged `event_type`. Source: gate category `event_type`. Weakest-attributed issued rule; re-count at adjudication.
- **B.7 FOOD span** (old B.22). FOOD spans the head noun with its modifiers; FORM, STATE and SIZE are nested spans inside it; a food word inside a tool or intermediate name is not a FOOD span. Ex: "chopped blue vrim" → FOOD "blue vrim", FORM "chopped".
  Evidence: 5 packets with FOOD span added or removed between pass 1 and committed (A 2, B 3). Source: gate category `entity_type` (104 disagreements, 6/7 pairs).
- **B.8 UNIT versus TOOL** (old B.23). UNIT is a measure word after a QUANTITY ("2 cloves", "1 jar"); a container word with no number is a TOOL. Ex: "2 pinches of krell" → UNIT "pinches"; "a krell pot" → TOOL.
  Evidence: 3 packets with UNIT spans added at pass-1 review (A 3); at threshold. Source: gate category `entity_type`.

## Held: INSUFFICIENT_RECURRENCE (not issued)

| Held | Old ids | Proposed wording (one line) | Recurrence | Source |
|---|---|---|---|---|
| H.1 | B.1+B.2 | A food named in a step but absent from the ingredient lines gets UNKNOWN coref plus one `unknowns` entry; never add a line, an `Add` or edit `text`; the validator warning is logged as SP-001. Ex: "stir in the plonk" (no plonk line) → UNKNOWN coref + unknowns. | 2 packets (A 1, B 1) | SP-001; coref/entity |
| H.2 | B.6 | Intermediate output is labelled by the event that creates it. | 0 (`intermediate_identity` 0 disagreements) | coref/entity |
| H.3 | B.7 | Entity role follows the span's role (INGREDIENT list item, INTERMEDIATE product). | 0 attributable | entity_type |
| H.4 | B.10 | Use only REQUIRED event types; Transform over Observe. | 1 packet (Transform/Merge swap); no Observe events in P1 | event_type |
| H.5 | B.16 | Reserve for set-aside-and-reuse; Split otherwise. | 0 (no Reserve events in any committed P1 label); "repeat with the other" folded into B.4 | event_type |
| H.6 | B.17 | Check final state after `replay`; never hand-type it. | not a label rule: labels carry no state field, state is replay-derived; belongs in the checklist, not the handbook | final_state |
| H.7 | B.18 | One container/location per alive entity; "serve" ends there. | 0 `location` edits | final_state |
| H.8 | B.19 | Temperature and time belong to the event whose verb they modify; oven setpoint is a TEMPERATURE span on the heat event. | 1 packet | event_argument |
| H.9 | B.20 (rest) | Stated values only; "until golden" is an ENDPOINT, not a TIME. | 2 packets (ENDPOINT edits) | event_argument |
| H.10 | B.21 | `medium` is what the food is in, `tool` the vessel. | 1 packet | event_argument |

H.1 is the one item where holding it leaves P2 annotators with only Addendum A.2 for a known schema gap; see the decision list in the stamp proposal / report.

## Derived from the three overlaps (resolved)
B.5/B.11/B.12 → B.2; B.8/B.15 (+B.16 part) → B.4; B.9/B.20 → B.5. Two extra merges beyond those three (same evidence, same SP): B.1+B.2 → H.1, B.3+B.4 → B.1.
