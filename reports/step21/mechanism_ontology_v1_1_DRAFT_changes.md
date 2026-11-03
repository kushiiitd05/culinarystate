# Step 21a: MECH schema v1.1 draft, changes against v1

**Status: DRAFT_PENDING_H4.** Written 2026-11-03 in session S158 by the AI worker "ksh" (an agent, not Kush). This is an AI draft under D-045 W1: Kush and Parv review it. Nothing is approved, frozen, minted, signed or entered into a ledger. No v1 file was edited: `registry/schemas/MECH.draft_v1.schema.json`, `reports/step21/{README.md, mechanism_effect_ontology_v1_draft.md, FIX_LOG_round3.md}` and the three vocabulary CSVs stay byte-identical. v1 still holds the ontology, the R-15 / R-14 / R-20 rules, the D21-1..D21-23 checklist and the plan deviations. This file lists only what v1.1 changes.

**Inputs:** round-3 reviews (`reports/master_plan/review_queue/round3_review_{A_governance,B_science}.md`) and the fixer's record `FIX_LOG_round3.md`. The fix log closed 40 items as FIXED. It left three items as OPEN_QUESTION only (21-12, 21-17, 21-19), and eight FIXED items with a chemistry OPEN_QUESTION attached. v1.1 applies the *structural* part of the remaining items. The chemistry goes to the expert (`S158_expert_questions.md`, EQ21-01..14). No chemistry is asserted.

## 1. New files

| Path | What |
|---|---|
| `registry/schemas/MECH.draft_v1_1.schema.json` | MECH v1.1 draft (`schema_version 1.1.0-draft`) |
| `src/culinarystate/mechanism/__init__.py`, `mech_contract.py` | pure semantic validator and read API for Steps 22a / 23a |
| `tests/fixtures/mech_v1_1_fixtures.py` | SYNTHETIC SCHEMA FIXTURES, ported from README §5 |
| `tests/unit/test_step21_mech_v1_1_schema.py` | the README §5 contract test, now a real `tests/unit` file on v1.1: 33 accepted variants (V-1..V-33), 106 negative controls (N-1..N-104 plus N-12b and N-12c; the v1 N-1..N-85 carried over, N-86..N-104 new), structure, vocabulary and diff tests |
| `tests/unit/test_step21_mech_v1_1_semantics.py` | semantic checks, link checks, the read API, and the test-local three-valued reference evaluator with a property test (2,000 random entries, seed 158) |
| `reports/step21/S158_expert_questions.md` | expert questions EQ21-01..14 with current draft wording and source status |

The tests were written and committed while they still failed (RED), before the schema and the module existed. This closes README D21-17's "no `tests/` file" for the draft. The card's `tests/unit/test_mech_schema.py` for the frozen schema still waits for H4.

## 2. Changes against v1 (complete; the diff test fails on any other difference)

| # | Subtree | Change | Round-3 item / reason |
|---|---|---|---|
| MC-1 | `$id`, `title`, `description`, `$comment` | v1.1 id and title; `schema_version 1.1.0-draft`; the comment names the additions and states that the R-15 reading is unchanged | versioned file |
| MC-2 | `$defs.affected_target.properties.analyte_form` | new required `token` (pattern `^[A-Z][A-Z0-9_]{1,63}$`, never `UNKNOWN`, or null) and `token_status` (NO_APPROVED_REGISTRY / REGISTRY_TOKEN / NOT_APPLICABLE). STATED takes NO_APPROVED_REGISTRY or REGISTRY_TOKEN; NOT_REPORTED and UNKNOWN take NOT_APPLICABLE; the token is non-null only for REGISTRY_TOKEN | **21-12 / D21-22.** The slot is structural. **No token list is in the schema** (a test checks that `token` has no `enum`); the list is EQ21-06. The convention matches KIN v1.1 `target.analyte_form` |
| MC-3 | `$defs.affected_target.required`, `.properties.target_class`, `.allOf` | new required `target_class` ∈ {SPECIES, TRANSFERRED_AMOUNT, OBSERVABLE, STATE, UNKNOWN}. New rule: a MONOTONIC `trajectory_shape` on an OBSERVABLE or UNKNOWN-class target needs ≥ 1 evidence id | **21-17.** v1 encoded nothing, and the ontology §3.2 table existed only as an effect-CSV reviewer column. The rule asserts nothing about colour or any other observable. It treats "monotone" as a claim that needs evidence; without evidence the drafter writes UNKNOWN. This deviates from ontology §3.2 ("target_class ... not a schema field"): H4 item H-1 |
| MC-4 | `$defs.marker.required`, `.properties.sharing_status`, `.properties.shared_with_mechanism_keys`, `.allOf`, `.description` | `sharing_status` ∈ {SHARED_DECLARED (≥ 1 key), NOT_ASSESSED (no key)}; keys use the `mechanism_key` pattern | **21-19.** A marker can declare the other entries that produce it. There is deliberately **no** "not shared" value, because not knowing of a second source never makes a marker unique. `marker_unique` stays const false |
| MC-5 | `$defs.open_question` (new), `properties.open_questions` (new, required), `required`, root `allOf` (one rule) | `open_questions[] = {question_ref ^EQ21-\d{2}$, topic_raw, status OPEN / EXPERT_ANSWER_RECORDED_PENDING_HUMAN_REVIEW / CLOSED_BY_HUMAN_DECISION, answer_locator, decision_ref ^D-\d{3}$}`. An ACCEPTED entry may carry only CLOSED_BY_HUMAN_DECISION questions. An expert answer needs its locator, and closing needs a DECISIONS id | **D21-23** ("21b keeps a row only if a PRIMARY source supports it"). v1 kept open chemistry in CSV free text, so an entry could be ACCEPTED while its chemistry was still open. An expert answer alone does not close a question (D-045: humans decide), and an AI review never does |

**Unchanged:** every v1 field, enum, constant and rule: R-15 constants, bound statuses with no optimum, E-7 (still a semantic check), ACCEPTED rules on all eight item types, the xref namespaces, the R-14 neutrality (the schema text still names neither candidate system; tested) and the absence of any kinetic field (G21.8; tested).

## 3. Round-3 items: where each remaining one now stands

| Item | v1 fix-log status | v1.1 |
|---|---|---|
| 21-12 analyte-form free text | OPEN_QUESTION | structure applied (MC-2); token list → EQ21-06 |
| 21-17 non-monotone colour | OPEN_QUESTION | evidence burden applied (MC-3); chemistry → EQ21-08 |
| 21-19 anaerobic markers non-unique | OPEN_QUESTION | sharing declaration applied (MC-4); which markers are shared → EQ21-10 |
| 21-1 DHA step | FIXED structure; chemistry OPEN | → EQ21-01, EQ21-02; guard MC-5 |
| 21-2 ascorbate-oxidase EC / node | FIXED structure; EC OPEN | → EQ21-03 |
| 21-3 SBO:0000459 PROMOTER id | FIXED; id OPEN (D21-19) | → EQ21-05 |
| 21-4 enzyme come-up window | FIXED structure; claim OPEN | → EQ21-09 (MECH entry versus Step-18 operator stays human, D21-14) |
| 21-6 chlorophyllase branch | FIXED structure; science OPEN | → EQ21-04 |
| 21-7 E-7 / pH NECESSARY | FIXED default rule; chemistry OPEN | → EQ21-07 |
| 21-13 dissolved O2 | FIXED schema; chemistry OPEN | → EQ21-11 (a new CV axis would be Step 07 v1.1, D21-10) |
| 21-14 coupled-redox pairs | FIXED relation; pairs OPEN | → EQ21-12 |
| 21-16 metallo-chlorophyll | FIXED structure; science OPEN | → EQ21-13 |
| optional pyropheophytin row | secondary source only | → EQ21-14 |
| A#17 evidence-id prefixes | FIXED in text (D21-1) | unchanged; the pattern still depends on the 04.9-min reservations (human) |
| A#36 log the step | NOT_APPLICABLE | not done here (the build note and WORKLOG are written by the integrating session) |

## 4. Read API for Steps 22a / 23a (`culinarystate.mechanism.mech_contract`)

- `schema_errors(entry) -> list[str]`: v1.1 record check.
- `semantic_problems(entry, cv_rows, *, effect_rows=None, analyte_form_tokens=None) -> list[str]`: v1 design, ported (duplicate keys, evidence ids ⊆ refs, CV exists / canonical unit / min ≤ max / numeric window on a categorical CV, category overlap, modifier gate type, `acts_on_modifier_key`, E-7). After the S158 AI cross-review (R4, R5) it also reports a CATEGORICAL_SET gate on a CV whose dimension is not categorical, and it orders OPEN_STATED bounds as well as STATED ones in the min ≤ max check. v1.1 adds: duplicate `question_ref`; `target_class` admitted for the effect type by the effect CSV `target_class` column (UNKNOWN always admitted); a marker shared with its own entry; REGISTRY_TOKEN without an approved token set.
- `asymmetric_links(entries)`, `unresolved_links(entries)`: competition and consecutive symmetry; links (including marker sharing) to keys outside the set.
- `required_condition_axes(entry) -> tuple[AxisRequirement]`: one per gate (cv_id, location, basis, clock, gate_key, gate_type, via GATE | MODIFIER_GATE). Under rule M-1 a modifier's axis is required even though its MODULATING gate never changes G4.
- `required_state_inputs(entry) -> tuple[StateInput]`: preconditions, then history items, then inline STATE_PREDICATE modifiers.
- `candidate_effects(entry) -> tuple[CandidateEffect]`: target key / SVAR or state key, target class and role, compartment, effect type, allowed sign set, trajectory shape, analyte token and status. It has no magnitude field (tested).
- `consumable_for_applicability(entry) -> (bool, reasons)`: false for NOT_ACTIVE (record status DEPRECATED / SUPERSEDED / RETRACTED; added after the S158 AI cross-review R3), NOT_ACCEPTED, NOT_HUMAN_VERIFIED, GATES_UNKNOWN, OPEN_QUESTIONS or UNRESOLVED_SINK. False means the entry contributes UNKNOWN, never NOT_APPLICABLE or APPLICABLE.
- Constants `APPLICABLE / NOT_APPLICABLE / UNKNOWN` (R-15 tokens). The module computes no verdict and no route. The three-valued evaluator stays test-local, as in v1. The Step 23 engine is a separate deliverable.

## 5. Observations for the humans (not changed here)

- **H-1** MC-3 makes `target_class` a schema field. Ontology §3.2 called it a reviewer guide only. Accept the field, or drop it and keep 21-17 open.
- **H-2** The effect CSV marks STRUCTURE_ALTERED, DENATURED, AGGREGATED and GELATINIZED as `OBSERVABLE_OR_STATE`. The ontology §3.2 table lists them under OBSERVABLE only. The validator follows the CSV, because the CSV is the vocabulary file. One of the two should be corrected in a new version.
- **H-3** MC-5's question ids are local (`EQ21-nn`, not a ledger prefix). Confirm that they do not collide with any reserved id family (04.9-min).
- **H-4** Every D21-n item of README §4 remains open as written there.
