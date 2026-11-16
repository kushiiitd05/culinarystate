# S178 lane EVD: evidence, benchmark U/X draft, 29-diag text (W1-W2)

Status: **AI_DRAFTED / PROPOSED. Nothing here is a human gate, signature, approval or nonce (D-071).** Worktree `max/s176-orchestration` at HEAD `4a95380` plus uncommitted files, host manjot-server, 2026-11-09.
Protected ledgers `ledgers/data/{EVD,COND,SRC,MEAS,SNAP}.jsonl` are byte-identical before and after every run (EVD `5b3b1939...`, COND `e9a1827a...`, SRC `6fddc14b...`, MEAS `bdb7b4210...`, SNAP `8834094f...`); no `ledgers/data/*.jsonl` was written, no git write, no existing file edited.
Every output is counts, hashes or our own text; no third-party text. Board file not edited.

## 1. Item statuses

| item_id | status | evidence | what is left |
|---|---|---|---|
| T2-C01-R1 | **PARTIAL** (built, asserted, unreviewed) | `reports/s178/evd/evd_field_conformance_203_2_v1.{md,csv,json}`; `tools/s178_evd_conformance.py`; `tests/unit/test_s178_evd_conformance.py` | Kush review (board acceptance); copy the table to `reports/step15/` (not my path). 55 fields over the 45 lines of 203.2; every row sums to 17,978 (asserted); `--selfcheck` byte-identical |
| T2-C01-R2 | **DONE, with a finding** | `reports/s178/evd/evd_export_repro_check_v1.{md,json}`; `tools/s178_evd_export_repro.py`; `tests/unit/test_s178_evd_export_repro.py` | the cross-platform finding in section 2.1 needs a human decision; orchestrator logs run row EVD-001 |
| T2-C03-R3 | **DONE** (table); 4 stale quotes left for the orchestrator | `reports/s178/evd/svar_reconciliation_v1.{md,json}`; `tools/s178_evd_svar_reconcile.py`; `tests/unit/test_s178_evd_svar_reconcile.py` | the packet (`handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md:123`) and 3 other lines still say 355 SVAR (listed with path:line in the report) |
| T2-C13-R1 | **DONE** | `reports/s178/evd/evd_coverage_vs_corpus_demand_v1.{md,csv,json}` + `fig_evd_coverage_by_family_v1.svg`; `tools/s178_evd_coverage.py`; `tests/unit/test_s178_evd_coverage.py` | one command reproduces it; EVD vitamin-C pairs 115 / 25 ING equal both router censuses; the sample reproduces the committed S177 1,000-recipe census on 7 fields. Not human-reviewed |
| T2-C15-R4 (the other W2 evd-card-d1 row for manjot-agent) | **DONE** | `reports/s178/evd/evd_reproducibility_record_v1.{md,json}`; `tools/s178_evd_repro_record.py` | the dataset-card rerun reproduces both committed hashes; orchestrator logs the run rows. (T2-C14-R1 is mac-agent only; T2-C06-R1 is BLOCKED_HUMAN; T2-C16-R1 and T2-C21-R1 are W3: not touched) |
| T8-C20-R4 | **PARTIAL** (drafted, AI_DRAFTED, unreviewed) | `annotation/d5_review/d5_UX_blocks_S178_DRAFT.{csv,md}` (git-ignored) and byte-identical committed copies in `reports/s178/evd/`; `tools/s178_evd_d5_ux_draft.py`; `tests/unit/test_s178_evd_d5_ux_draft.py` | Kush + Parv review (Mon 16); five U and five X rows, 3 X safety rows with gold REFUSE; status stays `DRAFT_FOR_REVIEW`; open decisions in the md (no reserves, U5 branch ambiguity, drafter disclosure) |
| T6-C08-R3 | **PARTIAL** (drafted, unreviewed) | `reports/step29/29diag_memo_MNAR_claim_boundary_S178_DRAFT.md` | Kush reads (0.3 h); then verbatim into H2 / D2 slides. The paragraph says only what exists today (DEL-2 diagnostic, no sweep, no overlap report) |
| T6-C09-R2 | **PARTIAL**: imputation tests DONE, 3 gaps reported | `tests/unit/test_s178_evd_no_imputation.py` (77 pass, 1 skipped, 3 xfail; see 2.3), `tools/s178_evd_transition_audit.py`, `reports/s178/evd/transition_no_imputation_audit_v1.json` | no zero / mean / half-minimum imputation reaches a real cell table (0 violations). The tier-I-in-test/cal and E5-E7 / Layer-2 refusal parts of the board text are not satisfied by the builder (xfail test); builder unchanged as instructed |

## 2. Findings that matter (negative results stay visible)

### 2.1 The EVD export is NOT byte-reproducible across platforms (T2-C01-R2)

- On this Linux (glibc) host two fresh v2 builds are byte-identical (`e8908eba...`), the ledgers are unchanged, `keys.jsonl` and the keys' input ledgers (DOC, STUDY, _ids, SRC_08A_YIELD) match the freeze manifest, the matrix and prior-state tables match.
- But the rebuilt v1 sha256 is `1801607c...`, not the recorded Mac value `e61d7db4...`, and v2 is `e8908eba...`, not `ffeefef9...`. **Cause (proven):** glibc `math.log` differs from the correctly rounded value in the last digit for 4 of the 15,290 log evaluations; the 4 cells are all `log_fold_change` (EVD-007201, EVD-007924, EVD-009784, EVD-010626). A build with a correctly rounded `log` equals the recorded v1 **and** v2 sha256 exactly.
- Verdict string: `REPRODUCIBLE_ON_THIS_HOST__CROSS_PLATFORM_DIFFERS_IN_4_LOG_FOLD_CHANGE_CELLS_EXPLAINED` (10 of 12 checks pass; the two failures are the as-built equality with the Mac hash).
- Proposed (a human decides; `src/culinarystate/evidence/evd_export.py` is not edited): make the log columns platform-neutral in the next builder version (correctly rounded log, or 12 significant digits), record the new sha256, keep the old one as the Mac-libm reference. Until then any claim "byte-reproducible" must say "on one libm".
- Not done: `keys.jsonl` is verified by hash, not rebuilt (`tools/step08a_build_keys.py` refuses repo roots and a non-Mac output root). The committed v1 / v2 jsonl files are git-ignored and absent here; the comparison is against the recorded manifest sha256.

### 2.2 Statements in other documents that the conformance table corrects (T2-C01-R1)

- The dataset card's temperature `RANGE 3,585` mixes 3,369 one-sided "above X" bounds (`GT_STATED`, Bognar core temperature) with only **216** true two-sided ranges: the completeness mask labels both RANGE. (Card file `reports/s178/analysis/evd_dataset_card_v1.*`, ANALYSIS lane.)
- The card says water activity is `NOT_IN_COND_SCHEMA`; the COND schema does have `water_activity` (also `ph_initial`, `ph_final`, `moisture`, `oxygen`, `agitation`, `tool_ids`, `geometry`); none is populated on any ACTIVE row. Only the completeness mask lacks an a_w key.
- Of the 55 fields: **10** carried with a value on every row, **19** on some rows, **18** in the schema but never populated, **8** with no field at all (ingredient_state_out, t_type, moisture / water-activity / pressure type, ordinal_band, platform, split_id in v1; export v2 adds `split_group_id` on every row, SCRATCH_PROVISIONAL). `doi_or_citation` is exact only for 3,678 Phenol-Explorer rows (DOI); USDA and Bognar cite one database record each. 0 rows have a human verifier.

### 2.3 Transition builders (T6-C09-R2)

- Real tables (`transition_no_imputation_audit_v1.json`, unmodified `cells_from_rows`): 17,458 cells from 17,978 ACTIVE rows (520 dropped, not filled: 496 Bognar mass-yield rows without a retention factor, 24 USDA UNKNOWN). **0** cells with a missing y that is not censored, **0** censored cells with y filled, **0** y_lower = 0, **0** y_train NaN. 5,894 cells are censored GT_CAP (33.76 %: Bognar 3,274 = 49.65 %, USDA 2,620 = 37.46 %); `y_train` enters them at their stated bound (the only substitution, documented in the code).
- 61 cells have y = 0; all are Phenol-Explorer rows whose ledger value is MEASURED 0 (not a builder fill). Whether those mean a true zero or a not-detected value is not stated in the ledger; `LogTarget` floors y at 0.001, so it acts on exactly those 61 cells. A source check is advisable before the 29-diag log-scale reading.
- Three latent gaps, pinned as `xfail(strict=True)` so they flip when fixed; **builder unchanged**: (1) `dataset._rf` reads `censor.limit` with default 0, so a censored row whose censor object has no `limit` key would become `y_lower = 0.0` (not reachable from the real ledger: all 5,894 carry a limit); (2) `_rf` ignores `censor.kind`, so a left-censored (LT_*) value would be stored as a lower bound (real ledger: GT_CAP only); (3) `cells_from_rows` filters on source family and ACTIVE only, not on evidence tier, so an E5-E7 row would enter a cell table (the board's "refuses any E7 or Layer-2 row" is not met by the builder).
- Observation (no test, verified by a one-line run): `splits.study_components` (L61-L66) sends every row with `study = None` to the single component `s:None`, although its docstring says such rows get their own group. Effect is conservative (study_disjoint refuses), but for a mixed family it creates one giant component.
- `fillna` occurs only as prediction-time backoff (`D2ProcessMean.predict`, `D5Boosting._X`) and in the propensity diagnostic (`propensity_weights.feats`); the test pins that set, so a new `fillna` in a fit path fails the suite.
- `tests/unit/test_transition.py::test_baselines_run_and_beat_persistence_on_toy` fails here with `ModuleNotFoundError` at `transition/evaluate.py:42` (sklearn is not installed in `.venv312`). Pre-existing and independent of this lane; the D5 fit test in my file is skipped for the same reason.

### 2.4 SVAR counts (T2-C03-R3)

SVAR.jsonl has **355 version lines = 224 distinct ids** (223 CHEMICAL + 1 PHYSICAL at the latest version; by line 354 + 1; 93 ids with one version, 131 with two; all ACTIVE). The registry CSV has **254 rows = those 224 ids + 30 FUTURE ids** (12 PHYSICAL, 7 CHEMICAL, 5 PROCEDURAL, 3 SENSORY, 3 SAFETY); non-FUTURE registry ids equal the ledger ids exactly (59 ACTIVE, 73 PROVISIONAL, 81 MISSING_EVIDENCE, 11 DUPLICATE). All 224 ids are used by the 17,978 ACTIVE EVD rows (213 canonical after the 11 DUPLICATE_SAME_ANALYTE mappings). The v16 corrections register's C-02 (355 records = 224 ids, 254 = 224 + 30) is correct; the board row's own phrase "224 distinct ids; 354 CHEMICAL, 1 PHYSICAL" mixes a distinct count with a line-level split. Lines still quoting 355 as a count: `handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md:123`, `registry/component_ledger_v1.csv:436`, `reports/orchestration/ssot_consensus/CONSENSUS_PLAN_2026-11-08.md:53` and `:60` (orchestrator-owned).

### 2.5 Coverage (T2-C13-R1), counts only, tagged COND_UNAUDITED

EVD holds 338 routable (ingredient, process) pairs over 98 ingredients and 36 processes (115 pairs / 25 ING for vitamin C, equal to both committed router censuses). A seeded 1,000-recipe non-BBC sample (seed 20261104) asks about 12,501 distinct pairs; 111 (0.89 %) have any EVD pair; 112 of its 618 ingredients have any EVD row. At process level 63.47 % of 4,724,493 corpus process events (non-BBC, full) are for a process that has some EVD row: an upper bound that ignores the ingredient (DRY_HEAT 97.6 %, WET_HEAT 78.4 %, COOLING 42.8 %, MECHANICAL_CUT 0 %, RESTING 0 %). Per-family pair hit rates in the sample range from 0 % (FERMENT_LEAVEN, SEPARATION, MECHANICAL_CUT, RESTING) to 6.5 % (WET_HEAT). Full-corpus vitamin C: 102 of 115 EVD pairs seen among 125,172 distinct pairs (0.08 %). The pair layer is a 1,000-recipe sample, not the corpus (a full-corpus per-family pair scan needs the 25-minute, 32-worker route census and was not run: server load average 60-90).
Dependency: the sample is reconciled to `reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json`, which is **untracked** in the worktree; commit it with this lane or the coverage tool will not run on a clean checkout.

## 3. Files (all new)

- Tools: `tools/s178_evd_common.py`, `s178_evd_conformance.py`, `s178_evd_export_repro.py`, `s178_evd_svar_reconcile.py`, `s178_evd_coverage.py`, `s178_evd_transition_audit.py`, `s178_evd_d5_ux_draft.py`, `s178_evd_repro_record.py`.
- Tests: `tests/unit/test_s178_evd_{conformance,export_repro,svar_reconcile,coverage,d5_ux_draft,no_imputation}.py`.
- Outputs `reports/s178/evd/`: the conformance, repro check, SVAR, coverage (+ figure), transition audit and reproducibility record files named above, plus `d5_UX_blocks_S178_DRAFT.{csv,md}` (committed copy).
- Drafts: `annotation/d5_review/d5_UX_blocks_S178_DRAFT.{csv,md}` (git-ignored: not carried by a commit), `reports/step29/29diag_memo_MNAR_claim_boundary_S178_DRAFT.md`.

## 4. Tests run

`pytest -q tests/unit/test_s178_evd_*.py`: **105 passed, 1 skipped (D5 fit needs sklearn), 3 xfailed (strict, the gaps in 2.3)** (per file: conformance 7, coverage 5, d5_ux_draft 9, export_repro 4, svar_reconcile 3, no_imputation 77 + 1 skipped + 3 xfailed). With `test_transition.py`, `test_cross_source.py`, `test_evd_export.py`, `test_lineage_export_v2.py`, `test_del2.py`: 134 passed, 1 skipped, 3 xfailed, 1 failed (the sklearn failure above, pre-existing). `--selfcheck` (two runs, byte-identical output) passed for the conformance, SVAR, transition-audit and coverage tools; the repro check showed two identical v2 builds; the repro record re-ran twice with the same hash.

## 5. Runs (rows for `registry/compute_runs_v1.csv`; the orchestrator inserts them)

Header: `run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes`. `git_commit` is the real HEAD (`4a95380`); the brief's `07fc0d2` is outdated.

```csv
RUN-S178-EVD-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),4a95380+uncommitted,EVD (USDA-RETN-R6 BOGNAR-2002 PHENOL-EXPLORER-3.6),1,"nice -n 10 python tools/s178_evd_export_repro.py --scratch <scratchpad>",reports/s178/evd/evd_export_repro_check_v1.json,39e2aac673120317b60536d784b24bf626bc8b95a246615afbcb3836a8c23792,2026-11-09T10:18:17Z,2026-11-09T10:19:54Z,DONE,"T2-C01-R2; wall 97 s; 2 fresh v2 builds + v1 + correctly-rounded-log variant; v2 sha e8908eba... identical twice but != recorded ffeefef9... (4 log_fold_change cells, glibc libm); correctly rounded log equals recorded; ledgers unchanged. A first run at 10:12:33Z (before the libm variant was added) gave MISMATCH and is superseded"
RUN-S178-EVD-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),4a95380+uncommitted,EVD (USDA-RETN-R6 BOGNAR-2002 PHENOL-EXPLORER-3.6),1,nice -n 10 python tools/s178_evd_conformance.py,reports/s178/evd/evd_field_conformance_203_2_v1.json,55e71b5325de01977b1ba897c0c3dbbed182288da2aa750787726f58053473d3,2026-11-09T10:40:11Z,2026-11-09T10:40:28Z,DONE,"T2-C01-R1; wall 17 s; 55 fields x 17,978 rows asserted; --selfcheck (2 runs) IDENTICAL earlier the same session; ledgers unchanged"
RUN-S178-EVD-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),4a95380+uncommitted,EVD (SVAR ledger + registry),1,nice -n 10 python tools/s178_evd_svar_reconcile.py,reports/s178/evd/svar_reconciliation_v1.json,36af7dfaa65ec2c1152b70c492e9b080bc79e240fdcd70c6cfcf5691c9afa10f,2026-11-09T10:40:56Z,2026-11-09T10:41:01Z,DONE,"T2-C03-R3; wall 5 s; --selfcheck IDENTICAL"
RUN-S178-EVD-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),4a95380+uncommitted,WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET (1000-recipe sample) + EVD,4,"nice -n 10 python tools/s178_evd_coverage.py --sample-size 1000 --workers 4",reports/s178/evd/evd_coverage_vs_corpus_demand_v1.json,e7f86f3704cf6e04295d15e7df01e176758049627d87d893b157a65675d2dd9d,2026-11-09T10:31:27Z,2026-11-09T10:33:55Z,DONE,"T2-C13-R1; wall 148 s; seed 20261104 (sha256 1037f2ed...); sample reproduces the committed S177 1000-sample census on items 57511 events 15326 pairs 12501 ING 618 vit-C pairs seen 51; --selfcheck 10:34:17Z-10:38:04Z (2 runs) IDENTICAL; 0 exceptions"
RUN-S178-EVD-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),4a95380+uncommitted,EVD (USDA-RETN-R6 BOGNAR-2002 PHENOL-EXPLORER-3.6),1,nice -n 10 python tools/s178_evd_transition_audit.py,reports/s178/evd/transition_no_imputation_audit_v1.json,f63daf3bc47fae63f704dc83efd7ed2acce8bdb94e4757527f8bfbc10dafbbc1,2026-11-09T10:41:01Z,2026-11-09T10:41:06Z,DONE,"T6-C09-R2; wall 5 s; 17,458 cells; 0 imputation violations; --selfcheck IDENTICAL"
RUN-S178-EVD-006,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),4a95380+uncommitted,EVD + KGE + ING ledgers (read),1,nice -n 10 python tools/s178_evd_d5_ux_draft.py,reports/s178/evd/d5_UX_blocks_S178_DRAFT.csv,d3b924826cd90ddb2b5c065bad16bf7e1cbc5cb91206cd309b9cf9baf6afd459,2026-11-09T10:41:06Z,2026-11-09T10:41:15Z,DONE,"T8-C20-R4; wall 8 s; 10 rows (U 5, X 5) DRAFT_FOR_REVIEW; facts asserted against ledgers before writing"
RUN-S178-EVD-007,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),4a95380+uncommitted,EVD,1,nice -n 10 python tools/s178_evd_repro_record.py,reports/s178/evd/evd_reproducibility_record_v1.json,c1861bdcbb5c437cfd63cbf442aff015cae79f555f0508f966a964123b0e13be,2026-11-09T10:41:57Z,2026-11-09T10:42:06Z,DONE,"T2-C15-R4; wall 9 s; reruns tools/s178_analysis_evd_card.py and the rerun reproduces both committed card hashes (json d97d1af7..., md e4e33bc0...)"
```

## 6. What a human must decide

1. The export builder's platform-dependent `log` (section 2.1): fix in a new builder version and re-record, or keep "byte-identical on one libm" as the stated guarantee.
2. Kush: review the conformance table (T2-C01-R1), the MNAR paragraph (T6-C08-R3); Kush and Parv: the ten U / X rows (T8-C20-R4, Mon 16; decide on reserves and the U5 branch).
3. Whether to fix the three latent builder gaps and the `study_components` fallback before the 29-diag run (Sat 14); this lane did not touch them.
4. Whether the 61 Phenol-Explorer zero retention factors are true zeros or not-detected values (source check).
5. The orchestrator: copy the conformance table to `reports/step15/`, fix the four stale "355 SVAR" lines, ask the ANALYSIS lane to correct the card's `RANGE 3,585` and a_w wording, commit the untracked S177 router census JSON with this lane.

## S178 correction (FIX-GOV, 2026-11-09)

Appended by the S178 FIX-GOV lane (GOV review findings GOV-1, GOV-10; SCI-B B1; this report's section 6 item 5). Nothing above was rewritten. Status: AI_DRAFTED / PROPOSED.

**1. Coverage table (T2-C13-R1, GOV-1).** The tool read the superseded S176 full router census. It now reads `reports/step23/router_demo_census_vitc_nonBBC_full_S177.json` (router census 0.3.0) and refuses any input listed in `registry/superseded_outputs_S176.csv`. Re-run with seed 20261104 and 4 workers: the sample still reproduces the committed S177 1,000-sample census, and the EVD pair counts still equal the router census. The statement in section 2.5 is unchanged (338 pairs, 12,501 sample pairs, 111 with EVD, 63.47 % of 4,724,493 events, 102 of 115 vitamin-C pairs). Only the last column (vitamin-C DIRECT items, gated) changes:

| family | old (S176) | new (S177) |
|---|---:|---:|
| DRY_HEAT | 10,792 | 11,925 |
| FAT_HEAT | 4,871 | 8,237 |
| WET_HEAT | 6,345 | 7,117 |
| HEAT_GENERAL | 5,060 | 7,795 |
| COOLING | 98 | 83 |
| PRESERVATION | 1,075 | 854 |
| MECHANICAL_MIX | 6,296 | 4,297 |
| **all** | **34,537** | **40,308** |

(For example, PROC-000002 roast: 668 → 2,315; PROC-000016 brown: 2,365 → 5,135.) Files: json `2c8d9661d416f89c…`, md `3db9af0d064f4126…`, csv `951a210fa83db1fa…`. The SVG `<desc>` now says AI_DRAFTED.

**2. Latent builder gaps of section 2.3 (GOV-10, board T6-C09-R2): fixed.** `transition/dataset.py` now does the following:
- treats a CENSORED row with no usable limit as UNKNOWN (no cell; never a zero bound);
- treats a `GT_*` limit as a lower bound;
- treats an `LT_*` limit as an upper bound, which is never stored as `y_lower` (the v0 table holds only lower bounds, so the row is left out and counted); any other censor kind is UNKNOWN;
- admits only tiers E1-E4 (TB-V0) and refuses Layer-2 / scenario / simulated rows;
- keeps an imputed-target class-I row (SSOT 222.9) out of any table that feeds test, validation or calibration; only `role="train"` admits it;
- counts every refusal in `CellTable.excluded`.

The three strict xfails in `tests/unit/test_s178_evd_no_imputation.py` are now ordinary passing tests, and `tests/unit/test_transition_firewall.py` (the board's acceptance test) passes with 40 tests. On the real ledger nothing changes: 17,458 cells (BOGNAR 6,594, PHENOL-EXPLORER 3,870, USDA 6,994), equal to `transition_no_imputation_audit_v1.json`. The only exclusions are the 520 rows with no retention value, which were skipped before as well.

**3. Item 5 of section 6.**
- The conformance table and the dataset card were copied byte-identical to `reports/step15/` (`evd_field_conformance_203_2_v1.{csv,md,json}`, `dataset_card_15a_v1.{md,json}`), with `reports/step15/README_S178_copies.md` and a test that checks each copy against its source.
- The card's "RANGE 3,585" and a_w wording are corrected (card 0.2.0: 216 two-sided + 3,369 one-sided censored; a_w is in the COND schema but never populated). Pressure "not recorded" (10,831 rows) is now shown and counted as missing.
- RUN-S178-EVD-007 was re-run (`tools/s178_evd_repro_record.py` 0.1.1, whose input list now names the S177 full census). It reproduces the new card hash: record json `714a1b4f…`, md `19665ad7…`.

## S178 correction (FIX-EVAL), 2026-11-09

AI_DRAFTED (D-071). Appended by lane FIX-EVAL after the SCI-B review finding B5; the sections above are kept as written.

- **B5, `tools/s178_evd_transition_audit.py` 0.2.0.** The `violations` block of v1 omitted two invariants (cells =
  MEASURED + CENSORED rows per family; y_train = y or y_lower everywhere) and checked y = 0 by comparing totals, so one
  imputed 0 and one dropped measured 0 would cancel. The block now carries every invariant as a count that must be 0;
  the two booleans enter as counts of failing families, and the y = 0 check is per row (each cell joined to its EVD row
  by id: cells with y = 0 whose row is not MEASURED 0; MEASURED-0 rows whose cell is missing or not 0; duplicate ids).
  Test with the reviewer's cancelling pair: `tests/unit/test_s178_fixeval_evd.py`.
- **Re-run on the real ledger** (`reports/s178/evd/transition_no_imputation_audit_v2.json`, sha256
  `7368111b454b7154135cbb8c74fc6cfa8d19ca0e0db39641ebca759f9da7df16`; uses the FIX-GOV builder of section 2 above):
  every violation field is 0. 17,458 cells; the 61 y = 0 cells are exactly the 61 MEASURED-0 rows, matched row by row;
  cells = MEASURED + CENSORED rows in all three families; y_train = y or y_lower everywhere. The totals equal v1.
  The builder's exclusion counts are now in the output per family (520 rows, all NO_RETENTION_VALUE).
- v1 (`transition_no_imputation_audit_v1.json`, sha256 `f63daf3b…`) is kept as history and superseded by v2.

## S179 correction (router census 0.4.1, 2026-11-10)

**Coverage table (T2-C13-R1).** `tools/s178_evd_coverage.py` 0.3.0 reads `corpus_can_say_v2.json` (physics v06) and the
router census 0.4.1 (`router_demo_census_vitc_nonBBC_{full,1000}_S179b.json`); the S177 0.3.0 census and can-say v1 are
superseded. Re-run on manjot, seed 20261104, 4 workers (RUN-S179-ANA6-003): the sample reproduces the committed S179b
1,000-sample census (items 57,511; events 15,326; pairs 12,501), and the EVD pair counts equal the router census. The
statement is unchanged (338 pairs, 12,501 sample pairs, 111 with EVD, 63.47 % of 4,724,493 events, 102 of 115 vitamin-C
pairs). Only the last column (vitamin-C DIRECT items, gated) changes, from the 0.4.x router gates:

| family | S177 (0.3.0) | S179b (0.4.1) |
|---|---:|---:|
| DRY_HEAT | 11,925 | 8,234 |
| FAT_HEAT | 8,237 | 7,518 |
| WET_HEAT | 7,117 | 6,557 |
| HEAT_GENERAL | 7,795 | 6,811 |
| COOLING | 83 | 68 |
| PRESERVATION | 854 | 255 |
| MECHANICAL_MIX | 4,297 | 777 |
| all | 40,308 | 30,220 |

New files `evd_coverage_vs_corpus_demand_v2.{json,csv,md}`, `fig_evd_coverage_by_family_v2.svg`; v1 kept on record.
`tools/s178_evd_repro_record.py` 0.2.0 (inputs S179b census, can-say v2, coverage v2) re-run (RUN-S179-ANA6-004): the
dataset card rerun reproduces the committed hash; record `evd_reproducibility_record_v2.{json,md}`.
