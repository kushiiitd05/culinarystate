# Gate provenance: human and AI decisions (S179, T9-C07-R3)

Status: **AI_DRAFTED, generated** by `tools/s179_gate_provenance_report.py` from `DECISIONS.md`. Each decision is classed from its Approver line or explicit recorded title/instruction.

**What D-085 changed.** From D-085 (2026-11-10) the AI personas ksh and prv (one model) act on Kush and Parv's behalf for every remaining human gate, always under the name `ksh+prv (AI, D-085)` and never a human's. Every output that rests on such an act carries `NO_HUMAN_SIGNOFF_D085`. Agreement between the two personas is not inter-rater evidence, so 07.A-R1 was not attempted and its v4 FAIL stays on record; AI-written gold is labelled AI (`AI_DRAFTED_GOLD`), never HUMAN_BLIND.

## Counts

| Class | Decisions |
|---|---|
| HUMAN | 71 |
| AI_DELEGATED_D085 | 16 |
| AI_PERSONA_D071 | 6 |
| MIXED_PERSONA_AND_HUMAN | 1 |
| AI_AGENT_PROVISIONAL | 7 |
| NO_APPROVER_LINE | 0 |
| **all** | 101 |

Of the HUMAN decisions, 19 record Parv's view as relayed by Kush, and 18 name the human in the title or instruction line instead of an Approver line.

## Decisions not made by a human

| Decision | Date | Title | Class |
|---|---|---|---|
| D-002 | 2026-10-18 | Ledger schemas are JSON Schema (draft 2020-12) + Python semantic validators, not pydantic | AI_AGENT_PROVISIONAL |
| D-006 | 2026-10-18 | FDC crosswalk is CANDIDATE-only; FDC portions become POR- records only after human verification | AI_AGENT_PROVISIONAL |
| D-007 | 2026-10-18 | Gold files and adjudication sheets stay out of git (they contain BBC recipe text) | AI_AGENT_PROVISIONAL |
| D-010 | 2026-10-18 | Ledger version timestamps | AI_AGENT_PROVISIONAL |
| D-011 | 2026-10-18 | KGE ledger: typed concept-level edges with support + confidence (Kush: "link confidence, usage support, categories, timers") | AI_AGENT_PROVISIONAL |
| D-012 | 2026-10-18 | Gutenberg recipes are silver; ledger file size watch | AI_AGENT_PROVISIONAL |
| D-013 | 2026-10-18 | Stated temperature bounds are CENSORED, not exact | AI_AGENT_PROVISIONAL |
| D-072 | 2026-11-06 | J4 read; hyphenated mixed numbers fixed in the versioned rc2 change (decided by prv and ksh (AI) under D-071; entered by the coding agent as scribe) | AI_PERSONA_D071 |
| D-073 | 2026-11-07 | Census reason fix: lot introductions are not a binding gap; Rung A implicit-object fixes need a precision check first (decided by ksh (AI) under D-071; entered by the coding agent as scribe) | AI_PERSONA_D071 |
| D-074 | 2026-11-07 | D-073 implicit-object rules: R2 withdrawn, R1 not landed (decided by ksh (AI) under D-071; entered by the coding agent as scribe) | AI_PERSONA_D071 |
| D-080 | 2026-11-10 | The choice items of the 9 Nov operations pack, D-008 task merge, Route B host (choice items decided by ksh and prv (AI) under D-071; D-008 and Route B decided by Kush; entered by the coding agent as scribe) | MIXED_PERSONA_AND_HUMAN |
| D-081 | 2026-11-10 | D5 pre-registration amendment options (decided by ksh and prv (AI) under D-071; entered by the coding agent as scribe) | AI_PERSONA_D071 |
| D-082 | 2026-11-10 | 29-diag and AA pre-registration amendment options; amendments applied in place (decided by ksh and prv (AI) under D-071; entered by the coding agent as scribe) | AI_PERSONA_D071 |
| D-083 | 2026-11-10 | D5 H3 sign test is two-sided (D-D5-6) (decided by ksh and prv (AI) under D-071; entered by the coding agent as scribe) | AI_PERSONA_D071 |
| D-086 | 2026-11-10 | Freeze the mode-to-§141 crosswalk (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-087 | 2026-11-10 | Formula id prefix FORM-; FORM, PARAM and VAL schemas frozen (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-088 | 2026-11-10 | D-071 addendum: the AI-persona line, as amended by D-085 (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-089 | 2026-11-10 | H8 scope-cut register signed (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-090 | 2026-11-10 | D5 benchmark v1 reviewed and frozen (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-091 | 2026-11-10 | AA pilot: licence checks, CAL pre-check and Model A fit (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-092 | 2026-11-11 | D5 ladder run and scored; H1 and H3 rules not met (recorded by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-093 | 2026-11-12 | Separate strict-v2 local engineering policy (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-095 | 2026-11-12 | Strict-v3 display and supplemental technical diagnostics (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-096 | 2026-11-13 | Conservative technical dispositions and MECH reference freeze (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-097 | 2026-11-13 | Structural Rung A → Gold event-type mapping, pre-declared before scoring (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-100 | 2026-11-13 | Full-corpus column map, formula census and transition-type map, pre-declared before any number (decided by ksh+prv (AI, D-085) on Kush's instruction "this is MUST … all columns … all of the flow"; entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-099 | 2026-11-13 | Predeclare prv supplemental blinded AI claim review before selection/labelling (decided by ksh+prv (AI, D-085); entered by coding agent as scribe) | AI_DELEGATED_D085 |
| D-102 | 2026-11-13 | Process-aware type mapping v2, post-hoc amendment of D-097 (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-104 | 2026-11-13 | Operational AA SIMULATE domain gate for the D-100 Lane S formula census, fixed before computing (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
| D-106 | 2026-11-13 | D-104 gate amendment: require a liquid medium (decided by ksh+prv (AI, D-085); entered by the coding agent as scribe) | AI_DELEGATED_D085 |
