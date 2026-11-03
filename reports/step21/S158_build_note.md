# S158 build note — kinetic contract 04.3, mechanism schema 21, signatures 22a, applicability 23a

2026-11-03. Branch `cloud/s158-mechanism-stack`, stacked on `cloud/s157-evidence-machinery`.
Every new file is a **DRAFT** (`DRAFT_PENDING_H4` or `_21b_22a_H4`), and 23b stays **BLOCKED** (it needs 07.A and 15b).

Workflow (D-045): AI worker "ksh" built 04.3 and 21 v1.1; AI worker "prv" built 22a and 23a and cross-reviewed
ksh's work; the coordinator verified both. Kush, Parv and the chemistry expert review afterwards. Nothing
scientific was settled by AI.

## What was built

| Part | Files | Content |
|---|---|---|
| 04.3 | `registry/schemas/{KIN,KINPT}.draft_v1_1.schema.json`, `src/culinarystate/lineage/kinetic_contract.py`, `reports/step04/kinetic_trajectory_contract_v1_1_DRAFT.md` | v1.1 beside the untouched S140 v1, with 12 tracked changes (KC-1..6, PC-1..6). Examples: no midpoint is invented for a RANGE time; digitised series declare read independence; censoring kinds are explicit. The cross-record validator checks raw units, exact seconds, clocks, a single C0, companions and lab groups. Eligibility verdicts read `ELIGIBLE_UNDER_DRAFT_RULES` because THR-04K-01..04 are unsigned; an unverified or retracted series is not eligible (R1). |
| 21 | `registry/schemas/MECH.draft_v1_1.schema.json`, `src/culinarystate/mechanism/mech_contract.py`, `reports/step21/{mechanism_ontology_v1_1_DRAFT_changes.md,S158_expert_questions.md}` | MECH v1.1 with 5 tracked changes: analyte-form token slot, target_class, shared markers, open questions. The contract test is now a unit test (33 accepted variants, 106 negative controls). There are 14 expert questions, EQ21-01..14. **No source could be opened** (the network policy blocks the enzyme-database and EBI hosts), so every citation is marked UNVERIFIED. |
| 22a | `src/culinarystate/mechanism/{process_signatures,case_seal}.py` | Sign-only signatures over PROC × modifiers × MECH. No real rule ships. A case-set sealing helper exists, but nothing has been sealed or authored. |
| 23a | `src/culinarystate/mechanism/applicability.py`, `registry/schemas/APPDEC.draft_v1.schema.json`, `registry/mechanisms/{applicability_reason_code_registry_v1_DRAFT,route_enum_v1_DRAFT}.csv`, `reports/step23/applicability_engine_23a_DRAFT.md` | Three-valued gates G0–G9. UNKNOWN never reaches SIMULATE; this is enforced by the schema and by property tests. The engine refuses 23b mode, COND-sourced values, non-consumable MECH entries and tampered signatures. 56 reason codes: 11 from the plan and 45 marked `S158_AI_DRAFT`. APPDEC maps to the S156 26g binding without any edit to 26g. |

## AI cross-review of 04.3 and 21 (`reports/step21/S158_ai_review.md`)

| ID | Severity | Fix |
|---|---|---|
| R1 | medium | Unverified or retracted series were eligible for splits |
| R2 | medium | Arrhenius verdict was ELIGIBLE with no temperature |
| R3 | medium | Retracted, deprecated and superseded MECH entries were consumable |
| R4 | low | A categorical gate on a numeric CV was not flagged |
| R5 | low | The min ≤ max check skipped OPEN_STATED bounds |
| R6 | low | Wrong statement in the EQ21-07 text (doc fix) |

Open items O-1 to O-4 are in block G.

## Verification

| Check | Result |
|---|---|
| Full unit suite (thread caps) | **2574 passed**, 17 skipped, 1 deselected. The 1 failed + 11 errors are missing bundle files, unchanged. |
| Ledger guard | 7/7 |
| Pre-S158 files modified | only append-only DECISIONS.md and the review sheet (D-049) |
| Attribution lines / .py or .md files over 800 lines | 0 / 0. The pretty-printed JSON schemas are larger, like the v1 schemas. |

## Needs human

The decisions are listed as block G on the review sheet. The chemistry expert answers EQ21-01..14.
To allow source checks, add `www.enzyme-database.org` and `www.ebi.ac.uk` to the environment's network allowlist.
