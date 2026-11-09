# EVD export v1 / v2 (08a.7) reproducibility check (S178, T2-C01-R2)

Status: AI_DRAFTED / PROPOSED, hashes and counts only, nothing written under `ledgers/` or `exports/`. `tools/s178_evd_export_repro.py` (s178-evd-export-repro-0.1.0-draft); deterministic.

**Verdict: REPRODUCIBLE_ON_THIS_HOST__CROSS_PLATFORM_DIFFERS_IN_4_LOG_FOLD_CHANGE_CELLS_EXPLAINED** (10 of 12 checks pass).

| check | result |
|---|---|
| v1_export_sha256_equals_recorded_as_built_here | FAIL |
| v1_export_sha256_equals_recorded_under_correctly_rounded_log | PASS |
| v1_matrix_and_prior_state_tables_equal_recorded | PASS |
| v2_two_fresh_runs_identical | PASS |
| v2_equals_recorded_sha256_as_built_here | FAIL |
| v2_equals_recorded_sha256_under_correctly_rounded_log | PASS |
| only_log_fold_change_cells_differ_between_libm_variants | PASS |
| keys_file_hash_matches_recorded_and_freeze | PASS |
| ledger_inputs_of_keys_unchanged_since_freeze | PASS |
| protected_ledgers_unchanged_during_run | PASS |
| protected_ledgers_equal_recorded | PASS |
| evd_ledger_hash_in_v2_manifest_is_current | PASS |

## Cross-platform finding

- The rebuilt v1 and v2 bytes differ from the recorded (Mac) sha256 in **4 cells**, all in column(s) ['log_fold_change']: the host `math.log` (glibc) differs from the correctly rounded value in the last digit. A build with a correctly rounded `log` equals the recorded v1 and v2 sha256 exactly (v1 True, v2 True).
- Two fresh builds on this host are byte-identical to each other. The recorded hash is therefore reproducible on the Mac libm and, up to those cells, here. Proposed (a human decides; the builder is not changed here): make the log columns platform-neutral (correctly rounded log, or round to 12 significant digits) in the next builder version, record the new sha256, and keep the old one as `evd_export_v1@mac-libm`.

## Hashes (rebuilt in scratch vs recorded)

| artifact | rebuilt / current sha256 | recorded sha256 |
|---|---|---|
| v1 export (evd_export_v1.jsonl) | 1801607c915bf9fc12255eb2f366f505545efe97b240e7a4a08ba8954aefc3e5 | e61d7db4dc709ff3a4cb95ec6889a63d491e7f10d30222b421761f428aedd457 |
| v1 matrix table | 80f6a4fd7e8b5ddbb17b1b79560d3f6b437b5813dcb51dc703efa5ee200fbab7 | 80f6a4fd7e8b5ddbb17b1b79560d3f6b437b5813dcb51dc703efa5ee200fbab7 |
| v1 prior-state table | 1a8036632ff533bba29176a54a72d65d2326548c783bad973b06cce1db9f39ff | 1a8036632ff533bba29176a54a72d65d2326548c783bad973b06cce1db9f39ff |
| v2 export run A | e8908eba15118f7a87d2ec086097d766b2617f00120cf2c4ff67211dc5d91d79 | ffeefef915ba1ae9c048e055ba298a2ef1c6f9562a3327743c2b1e7856512203 |
| v2 export run B | e8908eba15118f7a87d2ec086097d766b2617f00120cf2c4ff67211dc5d91d79 | ffeefef915ba1ae9c048e055ba298a2ef1c6f9562a3327743c2b1e7856512203 |
| v1 export, correctly rounded log | e61d7db4dc709ff3a4cb95ec6889a63d491e7f10d30222b421761f428aedd457 | e61d7db4dc709ff3a4cb95ec6889a63d491e7f10d30222b421761f428aedd457 |
| v2 export, correctly rounded log | ffeefef915ba1ae9c048e055ba298a2ef1c6f9562a3327743c2b1e7856512203 | ffeefef915ba1ae9c048e055ba298a2ef1c6f9562a3327743c2b1e7856512203 |
| keys.jsonl (verified, not rebuilt) | f8da2fe7eb32dc1934686d8a6f35e36dce0ee4c9005da1f487e9c896956bfe90 | f8da2fe7eb32dc1934686d8a6f35e36dce0ee4c9005da1f487e9c896956bfe90 |

## Protected ledgers (before and after the run)

| ledger | before | after | unchanged | equals recorded baseline |
|---|---|---|---|---|
| EVD | 5b3b1939c7993283... | 5b3b1939c7993283... | yes | yes |
| COND | e9a1827a4a648a87... | e9a1827a4a648a87... | yes | yes |
| SRC | 6fddc14bac6d8cc8... | 6fddc14bac6d8cc8... | yes | yes |
| MEAS | bdb7b4210af4fd9b... | bdb7b4210af4fd9b... | yes | yes |
| SNAP | 8834094ff2034427... | 8834094ff2034427... | yes | yes |
| SVAR | d617f17bb8fb6c39... | d617f17bb8fb6c39... | yes | yes |
| PROC | b9248bf2b4069572... | b9248bf2b4069572... | yes | yes |
| ING | ef439951982b98ef... | ef439951982b98ef... | yes | yes |

## Not done

- keys.jsonl was verified by hash, not rebuilt (tools/step08a_build_keys.py refuses repo roots and a non-Mac output root)
- the committed v1 jsonl and v2 jsonl are git-ignored and not in this tree: comparison is against the recorded manifest sha256
