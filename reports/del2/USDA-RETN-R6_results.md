# DEL-2 baselines — USDA-RETN-R6 (seed 7)

rows 6,994 (censored 2,620); matrices 38, process signatures 77, targets 26; grid density 0.07552, propensity AUC 0.8105

- study_disjoint: NOT POSSIBLE (single source family or one giant component) — not reported
- D6 TabPFN: SKIPPED (not installed; GPU)
- censored rows trained at lower bound 0.975 (assumption)
- conformal coverage is empirical (AH4)

| split | model | MAE (censor-aware) | 95% CI (grouped) | MAE IPW | RMSE obs | conformal-90 cov / width |
|---|---|---|---|---|---|---|
| random | D0_persistence | 0.1205 | [0.091, 0.1412] | 0.0936 | 0.2399 | 0.9313 / 0.7 |
| random | D1_global_mean | 0.1087 | [0.0962, 0.1172] | 0.1004 | 0.1544 | 0.9313 / 0.4411 |
| random | D2_process_mean | 0.0854 | [0.0736, 0.095] | 0.0819 | 0.1334 | 0.9113 / 0.3951 |
| random | D3_hierarchical_shrinkage | 0.0632 | [0.0549, 0.0707] | 0.0764 | 0.1061 | 0.9084 / 0.2852 |
| random | D4_nearest_compatible_evidence | 0.0394 | [0.0327, 0.0466] | 0.0431 | 0.0843 | 0.8913 / 0.2108 |
| random | D5_gradient_boosting | 0.0251 | [0.0207, 0.0299] | 0.0291 | 0.0523 | 0.8991 / 0.1289 |
| random | D7_biased_mf_side_info | 0.0466 | [0.0386, 0.0542] | 0.0547 | 0.0825 | 0.9092 / 0.2454 |
| pair_holdout | D0_persistence | 0.1093 | [0.0794, 0.143] | 0.1196 | 0.2284 | 0.8823 / 0.5 |
| pair_holdout | D1_global_mean | 0.1057 | [0.0962, 0.1153] | 0.1088 | 0.1392 | 0.8823 / 0.2275 |
| pair_holdout | D2_process_mean | 0.0872 | [0.0742, 0.0976] | 0.1049 | 0.1337 | 0.887 / 0.3223 |
| pair_holdout | D3_hierarchical_shrinkage | 0.0659 | [0.0553, 0.0778] | 0.0855 | 0.1116 | 0.9121 / 0.3163 |
| pair_holdout | D4_nearest_compatible_evidence | 0.0413 | [0.0325, 0.0525] | 0.0637 | 0.0949 | 0.9011 / 0.25 |
| pair_holdout | D5_gradient_boosting | 0.0390 | [0.0296, 0.0518] | 0.0654 | 0.0887 | 0.9113 / 0.2244 |
| pair_holdout | D7_biased_mf_side_info | 0.0514 | [0.0405, 0.0675] | 0.0744 | 0.1021 | 0.9097 / 0.2655 |
| matrix_disjoint | D0_persistence | 0.0590 | [0.0407, 0.0711] | 0.0602 | 0.1639 | 0.9703 / 0.5 |
| matrix_disjoint | D1_global_mean | 0.0998 | [0.0838, 0.1209] | 0.1004 | 0.1005 | 0.9703 / 0.2488 |
| matrix_disjoint | D2_process_mean | 0.0903 | [0.0698, 0.1128] | 0.1023 | 0.1086 | 0.9301 / 0.3012 |
| matrix_disjoint | D3_hierarchical_shrinkage | 0.0816 | [0.0526, 0.1115] | 0.0900 | 0.1211 | 0.8716 / 0.2939 |
| matrix_disjoint | D4_nearest_compatible_evidence | 0.0567 | [0.0338, 0.084] | 0.0601 | 0.1241 | 0.855 / 0.2436 |
| matrix_disjoint | D5_gradient_boosting | 0.0692 | [0.044, 0.0911] | 0.0672 | 0.1259 | 0.8716 / 0.296 |
| matrix_disjoint | D7_biased_mf_side_info | 0.0759 | [0.0468, 0.1097] | 0.0829 | 0.1241 | 0.8332 / 0.2507 |
| process_disjoint | D0_persistence | 0.0728 | [0.0329, 0.1469] | 0.1357 | 0.1918 | 0.9517 / 0.6 |
| process_disjoint | D1_global_mean | 0.1096 | [0.0937, 0.1204] | 0.1130 | 0.1228 | 0.9517 / 0.3027 |
| process_disjoint | D2_process_mean | 0.1096 | [0.0937, 0.1204] | 0.1130 | 0.1228 | 0.9517 / 0.3027 |
| process_disjoint | D3_hierarchical_shrinkage | 0.0994 | [0.0754, 0.112] | 0.0948 | 0.1406 | 0.8885 / 0.4179 |
| process_disjoint | D4_nearest_compatible_evidence | 0.0725 | [0.0349, 0.0967] | 0.0608 | 0.1397 | 0.7182 / 0.1969 |
| process_disjoint | D5_gradient_boosting | 0.0672 | [0.0347, 0.086] | 0.0703 | 0.1309 | 0.7808 / 0.2186 |
| process_disjoint | D7_biased_mf_side_info | 0.0891 | [0.0565, 0.1075] | 0.0852 | 0.1236 | 0.8082 / 0.2924 |
