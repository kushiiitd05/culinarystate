# Evidence-plane reproducibility record (S178, T2-C15-R4)

Status: AI_DRAFTED / PROPOSED. `tools/s178_evd_repro_record.py` (s178-evd-repro-record-0.2.0-draft). Hashes, versions and commands only.

**Dataset card: rerun reproduces the committed hash: True.**

| card file | committed sha256 | rerun sha256 | equal |
|---|---|---|---|
| evd_dataset_card_v1.json | 1e7af6e25a8ffc1a72316f75028619709a1fd797edc2bb7d500e4efe6fe7ebfd | 1e7af6e25a8ffc1a72316f75028619709a1fd797edc2bb7d500e4efe6fe7ebfd | yes |
| evd_dataset_card_v1.md | 2cca6ed8c8c645b9cfbbd6238b9744d42eefe1b48695e852fda23daa1c373b21 | 2cca6ed8c8c645b9cfbbd6238b9744d42eefe1b48695e852fda23daa1c373b21 | yes |

## Environment

- python 3.12.3 (CPython), Linux-6.8.0-134-generic-x86_64-with-glibc2.39; packages {'numpy': '1.26.4', 'pandas': '2.1.4', 'scipy': '1.17.1', 'pytest': '9.2.0', 'pyarrow': '14.0.2'}; git HEAD c2d57b7 (+ uncommitted worktree changes).
- math.log on this glibc differs from the correctly rounded value in the last digit for 4 log_fold_change cells of the export (see evd_export_repro_check_v1).

## Seeds and splits

- Coverage sample: seed sha256 `1037f2edb4912104fc759949aacecbc2133a73a1a2b17bde5210cdad7ee901dc`, rule SHA256_SEED_CONCAT_RECIPE_ID_ASC, n = 1,000, non-BBC families; same sample as the committed S179b router census.
- none: the other evidence-plane runs are deterministic functions of the ledgers (no random draw).
- property tests use random.Random(seed) for seeds 0..39 (fixed in the test file).
- Splits: no train / test split is built or read here; split registry: registry/split_registry_v1.csv (EVAL lane).

## Runs

| run | item | command | outputs |
|---|---|---|---|
| RUN-S178-EVD-1 | T2-C01-R2 | `python tools/s178_evd_export_repro.py` | evd_export_repro_check_v1.{json,md} |
| RUN-S178-EVD-2 | T2-C01-R1 | `python tools/s178_evd_conformance.py [--selfcheck]` | evd_field_conformance_203_2_v1.{json,csv,md} |
| RUN-S178-EVD-3 | T2-C03-R3 | `python tools/s178_evd_svar_reconcile.py [--selfcheck]` | svar_reconciliation_v1.{json,md} |
| RUN-S178-EVD-4 | T2-C13-R1 | `python tools/s178_evd_coverage.py --sample-size 1000 --workers 4 [--selfcheck]` | evd_coverage_vs_corpus_demand_v2.{json,csv,md}, fig_evd_coverage_by_family_v2.svg |
| RUN-S178-EVD-5 | T6-C09-R2 | `python tools/s178_evd_transition_audit.py [--selfcheck]` | transition_no_imputation_audit_v1.json |
| RUN-S178-EVD-6 | T8-C20-R4 | `python tools/s178_evd_d5_ux_draft.py` | d5_UX_blocks_S178_DRAFT.{csv,md} |
| RUN-S178-EVD-7 | T2-C15-R4 | `python tools/s178_evd_repro_record.py` | evd_reproducibility_record_v2.{json,md} |

## Hashes

Code, input and output sha256 are in `evd_reproducibility_record_v2.json` (`code_sha256`, `input_sha256`, `output_sha256`). The record does not hash itself.
