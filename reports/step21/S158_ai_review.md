# AI verdict — pending Kush/Parv review

**S158 AI cross-review of worker "ksh"'s parts A + B (04.3 KIN/KINPT v1.1, Step 21 MECH v1.1).**
Reviewer: worker "prv", an AI agent and not Parv. Under D-045 this is an AI verdict. It is not an
approval, a sign-off, a human verification or a chemistry judgement. Kush and Parv review it and their
review is final. Every test cited here uses synthetic fixtures. No source was opened and no citation is
given from memory.

Scope read: `registry/schemas/{KIN,KINPT}.draft_v1_1.schema.json` (diffed against v1),
`src/culinarystate/lineage/kinetic_contract.py`, `reports/step04/kinetic_trajectory_contract_v1_1_DRAFT.md`
(against `kinetic_trajectory_contract_v1.md` R04-1..R04-16 and `04_6_min_data_plane_rules.md`),
`registry/schemas/MECH.draft_v1_1.schema.json` (diffed against v1), `src/culinarystate/mechanism/mech_contract.py`
(against README §5's semantic-validator design and the schema `$comment`),
`reports/step21/{mechanism_ontology_v1_1_DRAFT_changes.md,S158_expert_questions.md}` (against `FIX_LOG_round3.md`,
the roster CSV, README §4 and the round-3 Review B text), and the S158 tests and fixtures.
Regression tests: `tests/unit/test_s158_ai_review_regressions.py` (committed RED in `2bef136`, before the fixes).

## Findings

| id | severity | evidence | disposition |
|---|---|---|---|
| R1 | medium | `split_eligibility` never read `verification.status` or the record `status`. The clean synthetic series is UNVERIFIED and got `ELIGIBLE_UNDER_DRAFT_RULES`, and a RETRACTED series was eligible too. The KIN row of 04.6-min (approved by D-029) says a KIN may enter test / calibration "Y only if human verified". The CLAUDE.md law that AI review is not human verification points the same way. Tests: `test_r1_*`. | FIXED (`064b131`). Not ACTIVE gives NOT_ELIGIBLE `RECORD_NOT_ACTIVE`; HUMAN_REJECTED gives NOT_ELIGIBLE; any other non-HUMAN_VERIFIED status gives UNKNOWN `NOT_HUMAN_VERIFIED`. ksh's clean-series test now marks the series human-verified (`1fd3a03`). Doc §2 updated (`e3a682f`). |
| R2 | medium | `arrhenius_eligibility` returned ELIGIBLE for a series with `temperature_status = NOT_REPORTED` (so no profile) when it said PRODUCT_ISOTHERMAL_STATED or come-up EXCLUDED_FROM_TIME. With temperature status UNKNOWN it also returned ELIGIBLE, which contradicts the doc's "UNKNOWN results when temperature status … is UNKNOWN". Test: `test_r2_*`. | FIXED (`064b131`). A positive verdict needs a REPORTED temperature: NOT_REPORTED becomes NOT_ELIGIBLE and UNKNOWN becomes UNKNOWN. The non-positive paths and every existing ksh case are unchanged. Doc updated (`e3a682f`). |
| R3 | medium | `consumable_for_applicability` ignored the record `status`. An ACCEPTED entry with status RETRACTED, DEPRECATED or SUPERSEDED returned `(True, ())`, so Step 23 could evaluate it as APPLICABLE. Tests: `test_r3_*` (including the 23a engine). | FIXED (`a1ee9db`): reason `NOT_ACTIVE`. Propagated to the engine as `MECH_NOT_ACTIVE` (`0d997ba`, `cd31645`). Read-API doc updated (`b98bd73`). |
| R4 | low | The schema `$comment` assigns "dimension agrees with domain_kind" to the semantic validator. `_gate_problems` checked only one direction (a numeric window on a categorical CV). A CATEGORICAL_SET gate on CV-013 (pH) passed. The defect is inherited from README §5's v1 design. Test: `test_r4_*`. | FIXED (`a1ee9db`). |
| R5 | low | The min ≤ max check considered STATED bounds only. `min OPEN_STATED 0.9` with `max STATED 0.2` passed, although an OPEN_STATED value is the studied extreme on its side. Inherited from v1. Test: `test_r5_*`. The 23a engine could not activate such a gate in any case: no value satisfies both sides. | FIXED (`a1ee9db`). |
| R6 | low (doc) | EQ21-07 said that a pure-chemistry entry with only MODULATING gates "can never" have `gates_unknown = false`. The schema root rule admits it when the entry has a precondition. Evidence test `test_r6_*` passes on the unchanged schema. No code defect was involved, so no failing test applies. | FIXED (`88a9701`): wording corrected. |
| O-1 | low | `distinct_numeric_tau` and the companion pairing compare `(unit, value)` unless every non-zero point has an exact seconds value. In that case "60 min" and "1 h" count as two times. Raw units are kept by design (R04-5), so this is a design choice, not a clear defect. | OPEN: decide whether to compare on exact seconds per pair. |
| O-2 | low | `split_eligibility` checks the KIN-level verification (after R1). The 04.6-min OBS row also requires human verification of each OBS. | OPEN: does a human-verified KIN imply its OBS, or must each OBS be checked? |
| O-3 | info | `_gate_problems` uses `dimension.startswith("categorical")`, so a numeric window on the dual-dimension CVs CV-027 (`categorical_or_rate`) and CV-038 (`categorical_or_conc`) is flagged. Their canonical unit "as stated" fails the unit check anyway. | OPEN: decide how dual-dimension CVs take numeric gates (CV registry owner). |
| O-4 | info | The expert questions list web search results as "search leads, not opened", with titles "as returned". This review did not open or resolve any of them. No lead is presented as evidence, every Sources line says UNVERIFIED, and no numeric value is reproduced. | No over-claim found. The leads remain unverified pointers for the humans. |

## Checks with no defect found

- **v1 → v1.1 diff claims.** A recursive diff of the KIN, KINPT and MECH JSON files gives exactly the declared
  path sets (KC-1..6, PC-1..6, MC-1..5). Every v1 `allOf` / `required` item is kept. The only modified v1
  item is the KIN `censoring_summary` YES rule (KC-5 adds `contains`), as declared. The root rules are one new
  rule each where stated. Counts in the docs agree with the code: 22 accepted variants and 31 negative controls
  (KIN/KINPT); 50 cross-record tests.
- **KINPT v1.1 rules.** Probed on fixtures: a RANGE or NOT_APPLICABLE_REFERENCE tau cannot carry exact seconds,
  a DEFINITIONAL_ZERO converted exactly must be 0, and a DIGITIZED tau requires `digitized.status = YES`.
- **Kinetic validator vs doc §2.** The issue codes, severities and the two-read / censoring / C0 / companion
  rules match the doc and R04-5, -6, -7, -9, -10, -13, -14, -16. `OBS_MISSING` (UNKNOWN) in `split_eligibility`
  was undocumented; it is now listed (`e3a682f`). The THR-04K rows remain unsigned drafts (tested by ksh).
- **MECH read API vs doc §4.** `required_condition_axes`, `required_state_inputs` and `candidate_effects` match the
  doc. Candidate effects carry no magnitude. `asymmetric_links` / `unresolved_links` match the README design.
  `reviewer_ids` has `uniqueItems`, so one reviewer cannot count twice towards the dual-review rule.
- **Round-3 accounting.** `FIX_LOG_round3.md` gives 23 + 17 = 40 FIXED, three OPEN_QUESTION-only items
  (21-12, 21-17, 21-19) and eight FIXED items with a chemistry OPEN_QUESTION (21-1, 2, 4, 6, 7, 13, 14, 16), as
  `mechanism_ontology_v1_1_DRAFT_changes.md` states.
- **Expert questions (over-claiming).** Each of the 15 "current draft wording" quotes was found in the cited repo
  file (roster CSV, README, ontology). One quote differs only by bold mark-up and an ellipsis. The named chemistry
  (EC numbers, products, markers) is phrased as a question and traces to the roster or to round-3 Review B. It
  is never stated as fact. The document says that no primary source was opened.

## Not reviewed

The real-data behaviour of either validator (no reviewed KIN or MECH record exists), the chemistry itself, and
whether the 04.3 or MECH v1.1 contracts should be approved (H4, humans only).
