# 35h decision record v1, Level 12 (molecule and ingredient representation) (S179)

Status: **AI_DRAFTED, v1** (board T7-C22-R1, T7-C20-R1). It states what the record shows at
`kush/s179-finish-fixes`. It is not a gate pass or a signature. Step 35 for the course is **DESIGNED,
pre-registered, NOT RUN** (D-080 #3): the 35.0 v2 package is unsigned and no rung has run on real data.

**Status vocabulary.** The 35.0 completion rule (`preregistration_35_0_v1_draft.md` §12) names three statuses:
PROMOTED, FAILED and DATA-BLOCKED. A rung that was decided not to run is neither, so it is written as **NOT_RUN
(D-080 #3)**. A box whose input does not exist is DATA-BLOCKED.

**Learned rungs deferred; entry rule LR-1..LR-5** (35.0 §14, `THR-35P-29`). No learned rung (35g) is run, scheduled
or pre-registered. LR-1 needs the explicit rungs evaluated under a signed 35.0. That has not happened, so LR-1 is not
met and none of LR-2..LR-5 is reached. This statement goes on the talk's limitation slide verbatim.

## Rungs

| Rung | Status | Evidence |
|---|---|---|
| 35a molecule features and leaderboard (E0-E3) | NOT_RUN (D-080 #3) | prereg §4; `registry/molecules/target_molecule_map.csv` (target map only, no feature matrix); rdkit only on the Mac (`reports/s179/env_inputs_three_hosts_S179.md`) |
| 35b ingredient chemical profile x_ij and aggregator ablation | NOT_RUN (D-080 #3); DATA-BLOCKED for abundance (EVD has no volatiles, §13) | prereg §5 |
| 35g learned rungs | DEFERRED (LR-1 not met) | prereg §14 |

## SSOT §183.4 Level-12 completion boxes

| # | Box | Status | Evidence / reason |
|---|---|---|---|
| 1 | v9 molecule registry and source / licence / evidence ledger versioned | PARTIAL | `registry/molecules/*` (target map; unresolved targets listed), SRC ledger; no versioned molecule registry release |
| 2 | split manifests frozen and leakage-audited | NOT_MET | `registry/split_registry_v1.csv` exists, but G08-3 FAILED (NEG-0047) and no 35a/35b split is frozen |
| 3 | classical E0-E3 baselines on real data | NOT_RUN (D-080 #3) | prereg §4.4 |
| 4 | default z_m justified against ECFP / descriptors under two leakage-safe splits | NOT_RUN | depends on boxes 2 and 3 |
| 5 | positive-pair semantics and circularity explicit for every learned objective | MET as specification only | prereg §5.3 (non-circular tasks, SSOT §133.2); no learned objective exists |
| 6 | aggregation chosen through the mean ... interaction-graph ladder | NOT_RUN | prereg §5.2 |
| 7 | frequency / profile-size / source-count confounds audited | NOT_RUN | prereg §5.4 (designed) |
| 8 | missing-view and missing-concentration behaviour quantified | DATA-BLOCKED | no concentration data for most targets (§5.1 tiers: presence != abundance) |
| 9 | calibration and OOD reported | NOT_RUN | — |
| 10 | compute / VRAM / time profiles recorded | PARTIAL | environment locks `reports/s179/env_lock/*` (RUN-S179-ENV-003..005); no training run to profile |
| 11 | process-conditioned claims supported by G8/G9 evidence or left open | LEFT OPEN | no process-conditioned Level-12 claim is made |
| 12 | final Level-12 decision record | THIS FILE (v1) | — |

## What this record does not support

- There is no z_m, no ingredient embedding and no molecule leaderboard; no representation claim of any kind.
- "Similar molecules" or "similar ingredients" means only the explicit, typed notions of 35e
  (`reports/step35/35e_similarity_registry_build_note.md`, synthetic only), never a learned similarity.

## 25 Nov claim boundary

Level 12 is designed and pre-registered, and its explicit-rung code exists and is tested on synthetic fixtures. No
Level-12 result exists.
