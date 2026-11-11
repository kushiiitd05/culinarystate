# 29-diag D2 versus B2 contrast

Status: AI_DRAFTED, 2026-11-11. **Every number in this memo carries DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / PRIOR_EXPOSURE_REANALYSIS / COND_UNAUDITED / PROVISIONAL_08A / NO_HUMAN_SIGNOFF_D085.**

Source: `reports/step29/diag/diag_results_S179.json`, RUN-S179-DIAG29-001 (D-085; WORKLOG S191).
This is a read-only transcription/interpretation of committed output, not a new model run or a new gate.
No human skim of this newly separated memo is recorded. Existing combined memo remains unchanged.

## Process-versus-ingredient contrast

The estimate is mean cluster loss(D2) minus loss(B2). Positive values mean lower B2 loss.
Source: `result.families.<family>.contrast_d2_vs_b2.splits.<split>`.

| Family | Split | Rows | Clusters | Cluster key | Estimate | Lower95 | Upper95 | Persisted label |
|---|---|---:|---:|---|---:|---:|---:|---|
| BOGNAR-2002 | matrix_disjoint | 894 | 18 | ONE_LINEAGE_CLUSTER | -0.0077 | -0.0142 | -0.0015 | DIAGNOSTIC |
| BOGNAR-2002 | process_disjoint | 139 | 4 | ONE_LINEAGE_CLUSTER | 0.006 | -0.0039 | 0.0121 | DIAGNOSTIC_ONLY |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | 286 | 25 | independence_group | 0.2892 | 0.0399 | 0.6582 | DIAGNOSTIC |
| PHENOL-EXPLORER-3.6 | process_disjoint | 1135 | 34 | independence_group | -0.0119 | -0.074 | 0.0428 | DIAGNOSTIC |
| PHENOL-EXPLORER-3.6 | study_disjoint | 362 | 20 | independence_group | 0.0992 | -0.0446 | 0.2401 | DIAGNOSTIC |
| USDA-RETN-R6 | matrix_disjoint | 1015 | 35 | ONE_LINEAGE_CLUSTER | 0.013 | 0.003 | 0.0231 | DIAGNOSTIC |
| USDA-RETN-R6 | process_disjoint | 988 | 33 | ONE_LINEAGE_CLUSTER | 0.022 | 0.0138 | 0.03 | DIAGNOSTIC |

The JSON's persisted label is supplemented by the memo-wide limitations, never upgraded.
S-3 favours D2 because B2's test ingredients are unseen. S-4 favours B2 because D2's test processes are unseen.
Only Phenol-Explorer S-6 compares on equal terms; its interval crosses zero. USDA and Bognár use
ONE_LINEAGE_CLUSTER fallback matrix×process clusters; they are not independent studies. Bognár S-4 has
4 clusters, below the preregistered proposed K_min=10, so no direction is interpreted.
