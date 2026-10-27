# Step 08b: authorisation package and pre-registration (v1 DRAFT, UNSIGNED, written 2026-10-27, before any 08b code or test is written)

Status: DRAFT for Kush to sign. Nothing here is in force. Authority it would rest on: D-029 (04.1 approved), D-030/D-032 (08a signed and authorised), D-034 (G08-3 FAIL recorded), the Plan v2 Step 08 card (08b / 08b-v0 / 08b v1), CHG-08-4 ("needs human approval"). Companion files: `registry/preregistered_thresholds_08b_v1_DRAFT.csv` (THR-08B-01..05), `docs/plan/D-035_DRAFT_08b_authorisation.md`, `reports/step08/step08b_questions_for_kush.md`. Where this text and the CSV differ, the CSV wins. D-032 listed "Step 08b" as not authorised; that stays true until D-035 is signed.

## 1. Scope
Two releases of the same reusable lineage / dedup library `src/culinarystate/lineage/` with tests `tests/unit/test_lineage_*.py`. Goal (card): package the same detector and registry as 08a so Steps 11-14 link duplicates at discovery time. Extract no new scientific values.

| | 08b-v0 (library packaging) | 08b v1 (release) |
|---|---|---|
| What it is | library API plus a seeded fixture; no precision/recall claim | the release, once 08a has produced detector precision/recall evidence |
| Hard dependency | 04.1 (approved, D-029) | 04.1 and 08a release evidence |
| May run in parallel with | 08a, 09 | nothing until 08a evidence is accepted |
| Downstream that waits on it | Step 10 document intake; 13a-1..5 | Steps 11 and 14 |
| Authorised by this package | YES, if D-035 is signed | NO, until Kush decides (section 7) |

API (card): `register_document`, `propose_edges`, `assign_keys`, `check_disjointness`. Properties (card): hashed `rule_version` on every output; offline; deterministic; bounded memory. Same detector code as 08a (detectors B0-B3 and STRONG, `detectors.py`).

**May write (proposed reading):** NEW files only: new library modules under `src/culinarystate/lineage/`, new `tests/unit/test_lineage_*.py`, scratch / configured output paths, and (at the end of a work package) a `reports/step08/` 08b report and the log entry via `tools/log_step.py`.
**Must not touch:** `ledgers/data/*` (EVD, COND, SRC, MEAS byte-identical, STUDY, SNAP, `_ids.jsonl`, DOC, LIN), the signed rows of `registry/preregistered_thresholds_v1.csv`, `registry/baseline_ledger_hashes_08a_v1.csv`, `exports/evd/evd_export_v1.*` and v2, the 08a reports and audit JSONs, the existing 08a modules' detector logic and the B3 cut 0.75 (D-034), any push to GitHub (H7).

## 2. Gates (card G08b-1..4; values in the CSV; all unsigned)
| Gate | Rule in one line | Row |
|---|---|---|
| G08b-1 | unit tests incl. determinism, idempotence and the seeded fixture pass | THR-08B-01 |
| G08b-2 | `rule_version` on every output | THR-08B-02 |
| G08b-3 | 100% of seeded copies detected on the library fixture at the 08a-registered threshold | THR-08B-03 |
| G08b-4 | no network access; no writes outside the configured scratch / output paths | THR-08B-04 |
| (release) | 08b v1 released only after 08a has produced detector precision/recall evidence; no numeric bar in the plan | THR-08B-05 |
SSOT floor from the card (never weaker): Split 6 (L16886-16891), G14-6 (L17083), G15-1 (L22382), 232.6 (L25307-25310). Card gives no fail action specific to 08b; the generic rule stands: a failed gate stops the run and is reported, no gate is loosened (D-027 R-20).

## 3. Work packages (from the card; the card does not number 08b substeps, so these are the card's listed items)
1. Library API: `register_document`, `propose_edges`, `assign_keys`, `check_disjointness`, reusing the 08a detector and key code without changing it.
2. `rule_version`: a hash stamped on every output.
3. Seeded fixture (scratch / test fixtures only) and `tests/unit/test_lineage_*.py` covering determinism and idempotence.
4. Offline / bounded-memory / write-path guard check (G08b-4).
5. (08b v1 only, NOT authorised) release against 08a precision/recall evidence; consumer wiring for Steps 11-14 and later 24-27 (`lineage_root_id` on every parameter / calibration source).

## 4. Run policy
All 08b-v0 work is CPU, stdlib or pandas, seconds to minutes (card Compute: "no GPU; A100 not needed"). It runs on the Mac. Nothing in 08b is flagged heavy or GPU by the card, so the unreachable A100 (VPN down) blocks nothing. D-031's "vinayak only if a run proves heavy" is inherited, not needed. Tests: `/opt/anaconda3/bin/python -m pytest -q`. Seeded copies live in scratch only. The 08a guard (`guard.py` verify_baseline / assert_safe_write_target) is the natural write-path control; whether to reuse it unchanged is an implementation choice, not a plan item.

## 5. What needs people
- Authorisation: Kush (D-035 signature). CHG-08-4 says 08b-v0 "needs human approval".
- The card lists no separate human audit for 08b (the 08a human hours are 08a's). Parv's sign-off: the 08a card asks for both reviewers; for 08b the card says nothing, so it is UNKNOWN whether Parv must sign. Asked as a question, not assumed.
- 08b v1: Kush's decision on whether 08a's evidence counts as "release evidence" (section 7).

## 6. Ambiguities decided conservatively (flagged)
1. Gate split: the card does not say which of G08b-1..4 apply to v0 vs v1. Decided: v0 must pass G08b-1, 2, 4 and G08b-3 as a fixture unit test; v1 must pass all four again plus the release condition.
2. G08b-3 vs "no precision/recall claim" for v0: decided that the 100% seeded-fixture check is a unit test of the code path and is reported as such, never as recall of the detector on real data.
3. "the 08a-registered threshold": THR-08A-19 registers a rule (loosest B3 score with seeded recall >= 0.95), and D-034 records the B3 cut as 0.75. Decided: use the frozen 0.75 unchanged, no retune; the exact register line is to be confirmed by Kush (question 4).
4. "Same detector code as 08a": decided that the library imports / wraps the existing 08a detector modules without edits; any needed change to them is a separate request.
5. Write permission: the card does not state it; decided as "new files only" (section 1), mirroring D-032. No edit to `registry.py`, ledgers, or 08a modules.
6. Numbers the card does not give, left UNKNOWN: fixture size and perturbation classes, test-count or coverage floor, `rule_version` hash algorithm, the "bounded memory" bound, the numeric bar for "precision/recall evidence". Not invented; THR-08B-01..05 say "NOT GIVEN IN PLAN - needs Kush" where applicable. (The 80% coverage figure is a global project rule, not an 08b card value.)
7. Dependencies on other steps: the card says 08b-v0 is HARD on 04.1 only. 04.2-min, 04.6-min, 04.9-min are not listed as 08b-v0 dependencies and were approved in D-029 anyway.

## 7. What 08a's G08-3 FAIL (D-034) means for 08b v1
Facts only, from D-034 and `reports/step08/step08a_audit_result_v2.json`:
- G08-3 is recorded as FAIL. Kush's edge precision: B3 13/50, B2 49/50 (Wilson lower 0.895), STRONG 50/50; Parv's: B3 0/50, B2 0/50 correct (49 UNCERTAIN), STRONG 50/50. Pooled Wilson lower bound (Kush) 0.6715. Both reviewers' per-reviewer pass = false. Unlinked-pair recall (report only): Kush 2 of 200, Parv 0 of 200.
- The B3 cut stays 0.75; no retune; THR-08A-03/04/16 are unchanged. B3 and B2 edges stay PROVISIONAL and merge conservatively (THR-08A-14); keys stay `SCRATCH_PROVISIONAL`.
- No claim that depends on G08-3 passing (08a "PASS", study-disjoint labels) may be made. This draft makes none.
- The card's 08b v1 trigger is that 08a "has produced detector precision/recall evidence". 08a has produced audit evidence, and that evidence is a FAIL for B2 / B3. The plan does not say whether a failed gate satisfies the trigger. This draft does not decide it: 08b v1 stays NOT authorised (question 1).
- Any 08b v1 report must carry B2 / B3 as PROVISIONAL and quote D-034 beside any precision or recall figure. A library fixture result (G08b-3) must never be cited as detector quality on real data.

## 8. Sign-off
Kush: _______ (unsigned). Parv: not required by the card text; UNKNOWN. Date: _______
