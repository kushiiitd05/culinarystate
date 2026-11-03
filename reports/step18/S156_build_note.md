# S156 build note — Step 18 event-sourcing engine and 26g simulation-input adapter

2026-11-03. Branch `cloud/s156-step18-events`, stacked on `cloud/s155-step17ab` (merge S154 → S155 → S156 in order).
Status: **DRAFT_PENDING_16c** for Step 18 and **DRAFT_PENDING_16c_23a_26b** for 26g.

Workflow (D-045): AI worker "ksh" built Step 18, AI worker "prv" built 26g and cross-reviewed Step 18,
and the coordinator verified both. Kush and Parv review afterwards, and their review is final.
There is no data bundle in this container. No ledger row was read for content or written.

## What was built

| Part | Files | Content |
|---|---|---|
| 18 audit / 18f | `reports/step18/S156_engine_audit.md` | Audit of the existing engine and its L1–L8 defects (unchanged; see Decisions). The `test_transition` hang **did not reproduce**: it passed with and without thread caps, over repeated runs and with up to 64 threads. No root cause is claimed, and the thread caps stay. A Mac diagnostic command is in §3. |
| 18b/18c event log | `src/culinarystate/state_graph/event_log.py` | Append-only event log with canonical JSON and a SHA-256 head. JSONL writers refuse protected paths (matched case-insensitively), ledger file names and any overwrite. Read-back is exact: no extra fields are accepted and lines split on newline only. |
| 18c/18d replay | `src/culinarystate/state_graph/replay.py` | Deterministic replay: one transaction per event (input snapshot hash, event revision, output entity versions, quantity changes, issues, config hash). Exact rational bounds, issue codes and no clamping. Mass balance is UNKNOWN, not FAIL, when a term is unknown, but correlated bounds that cannot be satisfied do FAIL. Reused event ids are rejected. Scope ALL or EXPLICIT_ONLY. |
| adapter | `src/culinarystate/state_graph/event_adapter.py` | Turns S155 extraction outputs into engine events. Ids only: literal recipe text is never copied (`LITERAL_TEXT_ATTRIBUTE_NOT_COPIED`). It reports an invented-value count. |
| 26g | `src/culinarystate/simulation/recipe_adapter.py` | Simulation-input contract for `sim_aa_1` and `sim_chl_1` (the input lists are PROPOSED_PENDING_26b). Each input's status is MEASURED, RANGE or UNKNOWN and comes only from bindings traced to EVT/COND/QNT/ING records. There are no defaults and no float literals in the module; conflicting bindings give UNKNOWN. The route is SIMULATE only when applicability is APPLICABLE with a 23a reference and every input is present, otherwise SIM_PROHIBITED; UNKNOWN never becomes SIMULATE (property test). The link-record writer keeps `sim_run_id` always null. A counts-only simulability census is included. |

## AI cross-review of Step 18 (`reports/step18/S156_18_ai_review.md`)

Six defects were fixed, each with a failing test first:

| ID | Severity | Fix |
|---|---|---|
| R1 | high | Recipe text no longer leaks into the event log |
| R2 | medium | Lenient read-back now refuses extra fields |
| R3 | medium | A reused event id is rejected instead of passing |
| R4 | low | Read-back no longer splits lines on Unicode separators |
| R5 | low | Protected paths are matched case-insensitively |
| R6 | medium | Correlated mass balance now fails when no bound can satisfy it |

Open items O1–O7 are listed in block E of `handoff/REVIEW_SHEET_AI_VERDICTS.md`.

## Verification

| Check | Result |
|---|---|
| New tests | Step 18: 119; review fixes: 11; 26g: 36 |
| Full unit suite (thread caps) | **2166 passed**, 17 skipped, 1 deselected. The 1 failed + 11 errors are missing bundle files, unchanged. |
| Ledger baseline | 7/7 match |
| Existing engine files edited | 0 |
| Attribution lines / files > 800 lines | 0 / 0 |

## Decisions

- **Kush, 2026-11-03:** "those bugs are not big/influential, we can leave those and continue". The old engine's L1–L8 stay unchanged; new code paths use the new replay.

## Needs human

The engine-side items below are block E on the review sheet:
1. Map the event, snapshot and transaction shapes to the 16c EVT/ENTITY/STATE/ALLOC schemas. 18a ledger persistence is not done.
2. Decide the merge/transform mass policy, who assigns the split/reserve basis (Rung A always emits UNSPECIFIED), how to read a REMAINDER with no fraction, the count-unit identity, and how to handle a rejected event.
3. Decide on prv's open review items O1–O7. O2 matters most: a replay can show PASS while the adapter excluded values.

26g items:
4. Approve the input lists, the units and the name MEASURED; decide whether SYNTHETIC inputs are allowed; human-review the census reason codes.
5. The real census needs Step 18 events from a Silver/Gold-Light sample plus 23a records.

Still open:
6. Run the Mac hang diagnostic.
7. The G18 gates are not evaluated (no adjudicated Gold events).
