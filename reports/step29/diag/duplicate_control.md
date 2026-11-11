# 29-diag repeated-value control

Status: AI_DRAFTED, 2026-11-11. **Every number in this memo carries DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / PRIOR_EXPOSURE_REANALYSIS / COND_UNAUDITED / PROVISIONAL_08A / NO_HUMAN_SIGNOFF_D085.**

Source: `reports/step29/diag/diag_results_S179.json`, RUN-S179-DIAG29-001 (D-085; WORKLOG S191).
This is a read-only transcription/interpretation of committed output, not a new model run or a new gate.
No human skim of this newly separated memo is recorded. Existing combined memo remains unchanged.

## Repeated-value groups and fold controls

Source: `result.families.<family>.duplicate_control`. A group repeats one reported retention value for a
process×target across at least two matrices within a source family; this is an operational diagnostic,
not proof that every repetition is an imputation or a duplicate primary experiment.

| Family | Groups | Rows in groups | Share of diagnostic subset |
|---|---:|---:|---:|
| BOGNAR-2002 | 748 | 4916 | 0.9489 |
| PHENOL-EXPLORER-3.6 | 138 | 354 | 0.1114 |
| USDA-RETN-R6 | 750 | 3314 | 0.5874 |

| Family | Split | Rung | MAE original split | MAE with duplicate groups in one fold |
|---|---|---|---:|---:|
| BOGNAR-2002 | matrix_disjoint | B2 | 0.0853 | NOT_POSSIBLE |
| BOGNAR-2002 | matrix_disjoint | D2 | 0.0782 | NOT_POSSIBLE |
| BOGNAR-2002 | matrix_disjoint | D3 | 0.0522 | NOT_POSSIBLE |
| BOGNAR-2002 | matrix_disjoint | D5 | 0.0396 | NOT_POSSIBLE |
| BOGNAR-2002 | pair_holdout | B2 | 0.0972 | 0.078 |
| BOGNAR-2002 | pair_holdout | D2 | 0.0997 | 0.0823 |
| BOGNAR-2002 | pair_holdout | D3 | 0.0705 | 0.0559 |
| BOGNAR-2002 | pair_holdout | D5 | 0.0492 | 0.0324 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | B2 | 0.5148 | 0.8225 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D2 | 0.753 | 1.2254 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D3 | 0.7556 | 0.8092 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D5 | 0.5487 | 0.628 |
| PHENOL-EXPLORER-3.6 | pair_holdout | B2 | 1.0046 | 0.7091 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D2 | 1.1351 | 0.8587 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D3 | 1.0982 | 0.9139 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D5 | 1.0357 | 0.723 |
| USDA-RETN-R6 | matrix_disjoint | B2 | 0.0798 | 0.0832 |
| USDA-RETN-R6 | matrix_disjoint | D2 | 0.0914 | 0.0973 |
| USDA-RETN-R6 | matrix_disjoint | D3 | 0.0834 | 0.0639 |
| USDA-RETN-R6 | matrix_disjoint | D5 | 0.0601 | 0.0469 |
| USDA-RETN-R6 | pair_holdout | B2 | 0.0875 | 0.0702 |
| USDA-RETN-R6 | pair_holdout | D2 | 0.0795 | 0.1077 |
| USDA-RETN-R6 | pair_holdout | D3 | 0.0664 | 0.0875 |
| USDA-RETN-R6 | pair_holdout | D5 | 0.0437 | 0.0524 |

Bognár duplicate-safe matrix-disjoint is NOT_POSSIBLE, not a missing zero-error result. Fold grouping changes
the test composition, so column differences are not paired treatment effects. Large shares in Bognár and
USDA, each a single lineage group, preclude an independent-study reading.

Duplicate-safe contrast entries are kept under `.contrast_matrix_disjoint_dupsafe` in the source JSON.
USDA has only 2 clusters (DIAGNOSTIC_ONLY); Phenol-Explorer has 16 and an interval crossing zero.
No new split, threshold or selection is chosen from these tables.
