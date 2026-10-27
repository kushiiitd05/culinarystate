# D-035 (DRAFT, UNSIGNED): Step 08b-v0 authorisation

Not recorded in `DECISIONS.md`. Nothing here is in force until Kush signs. Companion: `reports/step08/step08b_preregistration_v1_DRAFT.md`, `registry/preregistered_thresholds_08b_v1_DRAFT.csv`.

### D-035 · 2026-__-__ · Written authorisation of Step 08b-v0 (decided by Kush)
- **Decision:** Step 08b-v0 (reusable lineage / dedup library: API `register_document`, `propose_edges`, `assign_keys`, `check_disjointness`; hashed `rule_version` on every output; offline, deterministic, bounded memory; seeded fixture; no precision/recall claim) is AUTHORISED. Basis: HARD dependency 04.1 approved in D-029; CHG-08-4. The coding agent implements it on the Mac (CPU; no GPU needed; the A100 is not used). It writes only NEW files (new modules under `src/culinarystate/lineage/`, new `tests/unit/test_lineage_*.py`, scratch / configured output paths). It reuses the 08a detector code unchanged.
- **Gates:** THR-08B-01..04 (G08b-1..4) are signed with this decision, values as in `registry/preregistered_thresholds_08b_v1_DRAFT.csv` [Kush to fill each "NOT GIVEN IN PLAN" value or leave it UNKNOWN]. The run stops and reports on any failed gate; no gate is loosened (D-027 R-20).
- **08b v1 stays NOT AUTHORISED** until Kush decides. 08a's G08-3 is FAIL (D-034); B2 / B3 edges stay PROVISIONAL. No 08b-v0 output may be described as detector precision or recall on real data, or as 08a PASS.
- **Not authorised:** 08b v1 release (THR-08B-05); any edit to `ledgers/data/*`, `_ids.jsonl`, `registry.py`, 08a detector modules, the B3 cut 0.75 or any signed THR-08A row; any change to `exports/evd/*`; wiring the library into Steps 10-14 consumers; 07.A, 07I-C, 07I-S work; any A100 / vinayak use; any push to GitHub (H7); any commit made without the human whose session did the work.
- **Approver:** (blank)
