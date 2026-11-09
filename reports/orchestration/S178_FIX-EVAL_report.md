# S178 lane FIX-EVAL: report (finished S179 on the Mac + manjot)

Status: AI_DRAFTED (D-071). Nothing here is a decision, signature, approval or freeze. Code: branch
`kush/s179-finish-fixes` (snapshot `max/s178-wip` 6f8d1bc + Mac composition fixes, merge 1c21191). The fixer agent wrote
the code, the `_v2` outputs and the correction sections; it stopped before the replay re-run, the two regenerations and
this report. They were finished in S179.

## 1. Findings and where each is corrected

| Finding | Fix | Correction section |
|---|---|---|
| E1 gold origin | `h1_independence@0.2`: HUMAN_BLIND needs `gold_source` BLIND_HUMAN, a filled blind column and seen false; KEEP / EDIT of an engine draft = HUMAN_AFTER_SEEING_ENGINE; conflicts refused. H1 counts unchanged (40 / 40 ENGINE_DRAFT) | `S178_EVAL_report.md` |
| E2 sign-test floor | one-sided floor 5, both floors returned | `S178_EVAL_report.md` |
| E3 name matching | token boundaries ("pea" ≠ "peanut") | `S178_EVAL_report.md` |
| E4 cell=None | CELL_NOT_CHECKED, never SUPPORTED; DEV ladder: 0 value mismatches, not "UCR 0" | `S178_EVAL_report.md` |
| E5 split verifier | one hash convention per row, `unit_ids_sha256` recomputed, DIAG29 NOT_VERIFIABLE_FROM_LISTING unless recomputed | `S178_EVAL_report.md` |
| E6 `h1_rungs` docstring / leaky defaults | docstring fixed; `context()` refuses the leaky legacy settings for a D5 qid | `S178_EVAL_report.md` |
| E7 MDE wording | power monotone in the gap; ranges per n separated; values unchanged | `S178_EVAL_report.md`, `S178_PREREG_report.md` |
| E8 id scan | scans `reports/s178/` with an explicit allow-list | `S178_EVAL_report.md` |
| P1 07.A-R1 amendment | "stronger" withdrawn; Option A stated as a LOOSENING of signed R-06 with counterexample; AI recommendation now B + U1 + P1 + T2; A / A-keep / C / E are human choices needing Kush's signed D-0NN | `S178_PREREG_report.md` |
| P2 co-gate counts | counts per n stated (n = 100: ≤1 / ≤4; n = 120: ≤1 / ≤6) | `S178_PREREG_report.md` |
| B5 transition audit | full violations block, y = 0 checked per row; all 0 on the real ledger | `S178_EVD_report.md` |
| CORP-4/5/6 | independent replay, by-construction labels, two-pool determinism, verb-census denominator | `S178_CORPUS_report.md` |

## 2. Finished in S179

- `reports/s178/d5_harness/SYNTHETIC_FIXTURE_d5_scoring_result.json` regenerated (RUN-S179-EVAL-001). The JSON diff
  holds only the new version strings and new fields (refusal block; cell-check fields); no existing metric changed.
- `registry/prompt_registry_v1.csv` re-hashed (RUN-S179-EVAL-002): PR-H1-CONTEXT and CK-H3-INDEPENDENT source hashes
  changed with E1 / E4 / E6. The registry is not frozen (the D5 freeze is human, pending).
- Replay invariants re-run: smoke (RUN-S179-CORP-001) then full families (RUN-S179-CORP-002); 0 unexplained.

## 3. Tests

- Lane suites on the manjot worktree: 796 passed (all S176-S178 lane tests) before the two regenerations, with the two
  known failures (`test_s178_d5_fixture_run`, `test_s178_prompt_registry`) outside that selection; after the
  regenerations both pass (25 passed).
- Full suite: manjot 4,968 passed; its 6 failures and 53 errors are environment gaps (sklearn, requests, lxml,
  hypothesis; BBC data off the server, D-003) plus one real failure fixed in S179 (superseded-registry re-pin of
  `ing_sr_defaults_v1.csv`). The 48 affected modules were re-run on the Mac: 2,881 passed, 0 failed.

## 4. Superseded by this lane (rows for `registry/superseded_outputs_S176.csv`, appended by the orchestrator)

- `reports/s178/corpus/replay_invariants_corpus_v1.{json,md}` → `replay_invariants_corpus_v2.{json,md}`
- `reports/s178/h1_gold_independence_d5_draft.json` → `_v2.json`; `reports/s178/h3_independent_rescore_ladder.json` → `_v2.json`
- `reports/s178/mcnemar_power_n30_n60.json` → `_v2.json`; `reports/s178/leakage_audit_d5.json` → `_v2.json`
- `reports/s178/evd/transition_no_imputation_audit_v1.json` → `_v2.json`; `reports/s178/corpus/verb_coverage_census_v1.*` → `_v2.*`
