# 35h decision record v1, Level 13 (recipe and cuisine representation) (S179)

Status: **AI_DRAFTED, v1** (board T7-C22-R1, T7-C20-R1). Step 35 for the course is **DESIGNED,
pre-registered, NOT RUN** (D-080 #3). Statuses are as in the Level-12 record: PROMOTED, FAILED or DATA-BLOCKED, plus
NOT_RUN (D-080 #3).

**Learned rungs deferred; entry rule LR-1..LR-5** (35.0 §14, `THR-35P-29`). LR-1 is not met, because the explicit
recipe and cuisine rungs have not run under a signed 35.0. No z_R or z_C exists or is planned before 25 Nov.

## Rungs

| Rung | Status | Evidence |
|---|---|---|
| 35c recipe explicit rungs R0-R3 | NOT_RUN (D-080 #3); code built and tested on synthetic data | `reports/step35/35c_recipe_rungs_build_note.md`; `src/culinarystate/representation/recipe_rungs.py` |
| 35d cuisine explicit rungs C0-C2 | NOT_RUN (D-080 #3); code built (12 synthetic tests) | `reports/step35/35d_cuisine_rungs_build_note.md`; `representation/cuisine_rungs.py` |
| 35e typed similarity registry v2, nine notions | NOT_RUN; lint built (20 synthetic tests) | `reports/step35/35e_similarity_registry_build_note.md` |
| 35f process-response similarity | DATA-BLOCKED (needs Steps 15, 27, 30, 33) | prereg §13 |
| 35g learned rungs | DEFERRED (LR-1 not met) | prereg §14 |

## SSOT §193.8 Level-13 completion boxes

| # | Box | Status | Evidence / reason |
|---|---|---|---|
| 1 | recipe / cuisine data contracts and duplicate / source registries versioned | PARTIAL | recipe base v1 frozen (`reports/step07/step07hr_freeze_manifest.json`); `registry/recipe_source_usage_registry_v1.csv`; identity ledger provisional (07I-C kappas 0.571 / 0.588) |
| 2 | R0-R3 and C0-C2 explicit baselines exist | PARTIAL | code exists (35c, 35d); not run on real data |
| 3 | at least one leakage-safe recipe split family frozen | NOT_MET | no recipe-level split is source-family-disjoint (`reports/final/sections/S179_licence_and_split_labels_DRAFT.md` §2) |
| 4 | source leakage quantified where source labels exist | PARTIAL | D5 leakage audit (`reports/s178/leakage_audit_d5_findings.md`); none for 35c/35d |
| 5 | frequency-only and recipe-size shortcut baselines reported | NOT_RUN | prereg §6.4 (designed) |
| 6 | recipe-set aggregation chosen empirically | NOT_RUN | — |
| 7 | objective choice tested with non-circular transfer evaluation | NOT_RUN | prereg §6.3 |
| 8 | embedding gains survive confound controls | NOT_APPLICABLE before 25 Nov | no embedding (35g deferred) |
| 9 | calibration / uncertainty where outputs are probabilistic | NOT_RUN | — |
| 10 | compute profiles and seed / split uncertainty recorded | PARTIAL | `reports/s179/env_lock/*`; no run |
| 11 | final record states what z_R and z_C mean and do not support | THIS FILE: neither exists | — |
| 12 | procedural / process claims deferred to L14 / L15 unless supported | DEFERRED | process claims go through the evidence router and physics layers, not Level 13 |

## What this record does not support

- "Recipes alike", "cuisine signature" and "authentic for a cuisine" are not supported. Cuisine labels are
  confounded with source (35.0 §7.2).
- No recipe or cuisine embedding is offered or compared.

## 25 Nov claim boundary

Level 13 is designed, pre-registered and coded for its explicit rungs on synthetic fixtures. No Level-13 result
exists, and learned rungs are deferred under LR-1..LR-5.
