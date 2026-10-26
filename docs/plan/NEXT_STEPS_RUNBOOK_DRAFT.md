# CulinaryState — next-steps runbook (DRAFT, ordered; each step needs its named go-ahead)

Principle: original 36-step spine governs; adapted plan in `CulinaryState_Master_Plan_v2_ADAPTED_DRAFT.md`. STEP 08 NOT STARTED.

| # | Action | Owner | Gate / output | Blocks |
|---|---|---|---|---|
| 1 | Review and sign (or edit) `D-028_DRAFT_residual_rulings.md`, `condition_audit_protocol_amendment_v4_1_DRAFT.md`, `registry/preregistered_thresholds_v1.csv` | Kush + Parv (~1 h) | signed copies; D-027 entry in DECISIONS.md | 3, 5 |
| 2 | Condition audit on UNCHANGED packet v4: each reviewer alone and blind; each records the sha256 of the returned file | Kush, Parv (3-5 h each, UNVERIFIED) | two completed files | 3 |
| 3 | `step07_provenance_precheck.py` -> `step07_agreement.py` -> report every disagreement; no automatic adjudication | agent runs, humans adjudicate | PASS / FAIL_REVIEWER_DISAGREEMENT / INVALID_AUDIT | Step 15 condition fields, Steps 23, 29-33 (not Step 08 if D-027 item 1 is approved) |
| 4 | 400-pair identity labels (07I-C), blind and independent | Kush, Parv (4-6 h each, UNVERIFIED) | labelled packet; sealed v2 test packet built after | recipe-level test splits |
| 5 | Step 08a on the existing 17,978 EVD rows (CPU, Mac): DOC/LIN/SEXP/SMP/OBS schemas, STUDY append versions, detector B0-B3, USDA<->Bognar overlap verdict, independence registry, feasibility report | agent, after 1 and a separate go-ahead | G08-1..6 and 150-edge human audit | Steps 09-15 |
| 6 | Step 09 machinery incl. trajectory table (golden fixtures only) | agent | no real documents until Step 10 | Step 10 |
| 7 | 19A pilot design (20-50 recipes) and Step 16 schema work | Kush, Parv + agent | timings + IAA | 19B |
| 8 | Step 35 explicit baselines (parallel CPU lane); 36B benchmark protocol draft | agent + humans | pre-registration (35.0) | |

Do not: edit packet v4; change the condition gate; merge near-duplicates; pick duplicate thresholds for a target corpus size; push any licence-restricted data; run Step 08 before items 1 and 5's go-ahead.
Deadline reality: presentation 25-26 Nov 2026. Items 6-8 beyond design are likely out of scope and are reported NEED_DATA / DEFER.
