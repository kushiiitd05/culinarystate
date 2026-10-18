# DEL-2 baselines — USDA-RETN-R6 (seed 7)

rows 6,994 (censored 2,620); matrices 38, process signatures 77, targets 26; grid density 0.07552, propensity AUC 0.8105

- study_disjoint: NOT POSSIBLE (single source family or one giant component) — not reported
- D6 TabPFN: SKIPPED (not installed; GPU)
- censored rows trained at lower bound 0.975 (assumption)
- conformal coverage is empirical (AH4)

| split | model | MAE (censor-aware) | 95% CI (grouped) | median AE | MAE log (obs) | MAE IPW | conformal-90 cov / width |
|---|---|---|---|---|---|---|---|
| random | D0_persistence | 0.1205 | [0.0934, 0.1412] | 0.05 | 0.2361 | 0.0936 | 0.9313 / 0.7 |
| random | D1_global_mean | 0.1087 | [0.0967, 0.1172] | 0.1044 | 0.1481 | 0.1004 | 0.9313 / 0.4411 |
| random | D2_process_mean | 0.0854 | [0.0741, 0.095] | 0.0629 | 0.1262 | 0.0819 | 0.9113 / 0.3951 |
| random | D3_hierarchical_shrinkage | 0.0632 | [0.0545, 0.0711] | 0.0443 | 0.0987 | 0.0764 | 0.9084 / 0.2852 |
| random | D4_nearest_compatible_evidence | 0.0394 | [0.0323, 0.0453] | 0.0173 | 0.0717 | 0.0431 | 0.8913 / 0.2108 |
| random | D5_gradient_boosting | 0.0251 | [0.0198, 0.0292] | 0.0108 | 0.0454 | 0.0291 | 0.8991 / 0.1289 |
| random | D7_biased_mf_side_info | 0.0466 | [0.0383, 0.0529] | 0.0286 | 0.0771 | 0.0547 | 0.9092 / 0.2454 |
| pair_holdout | D0_persistence | 0.1093 | [0.0765, 0.1427] | 0.05 | 0.2245 | 0.1196 | 0.8823 / 0.5 |
| pair_holdout | D1_global_mean | 0.1057 | [0.0969, 0.1173] | 0.1113 | 0.1332 | 0.1088 | 0.8823 / 0.2275 |
| pair_holdout | D2_process_mean | 0.0872 | [0.0751, 0.0972] | 0.084 | 0.1213 | 0.1049 | 0.887 / 0.3223 |
| pair_holdout | D3_hierarchical_shrinkage | 0.0659 | [0.0543, 0.0778] | 0.0437 | 0.0986 | 0.0855 | 0.9121 / 0.3163 |
| pair_holdout | D4_nearest_compatible_evidence | 0.0413 | [0.0305, 0.0511] | 0.0152 | 0.0807 | 0.0637 | 0.9011 / 0.25 |
| pair_holdout | D5_gradient_boosting | 0.0390 | [0.0296, 0.0518] | 0.0158 | 0.0725 | 0.0654 | 0.9113 / 0.2244 |
| pair_holdout | D7_biased_mf_side_info | 0.0514 | [0.0409, 0.0677] | 0.0318 | 0.086 | 0.0744 | 0.9097 / 0.2655 |
| matrix_disjoint | D0_persistence | 0.0590 | [0.0407, 0.0711] | 0.0 | 0.1505 | 0.0602 | 0.9703 / 0.5 |
| matrix_disjoint | D1_global_mean | 0.0998 | [0.0822, 0.1212] | 0.1244 | 0.0878 | 0.1004 | 0.9703 / 0.2488 |
| matrix_disjoint | D2_process_mean | 0.0903 | [0.0708, 0.1132] | 0.087 | 0.0958 | 0.1023 | 0.9301 / 0.3012 |
| matrix_disjoint | D3_hierarchical_shrinkage | 0.0816 | [0.0526, 0.1144] | 0.058 | 0.1026 | 0.0900 | 0.8716 / 0.2939 |
| matrix_disjoint | D4_nearest_compatible_evidence | 0.0567 | [0.0344, 0.0872] | 0.0288 | 0.0948 | 0.0601 | 0.855 / 0.2436 |
| matrix_disjoint | D5_gradient_boosting | 0.0692 | [0.0441, 0.0945] | 0.0415 | 0.1104 | 0.0672 | 0.8716 / 0.296 |
| matrix_disjoint | D7_biased_mf_side_info | 0.0759 | [0.0468, 0.1118] | 0.0571 | 0.104 | 0.0829 | 0.8332 / 0.2507 |
| process_disjoint | D0_persistence | 0.0728 | [0.0328, 0.1469] | 0.0 | 0.1726 | 0.1357 | 0.9517 / 0.6 |
| process_disjoint | D1_global_mean | 0.1096 | [0.0908, 0.1219] | 0.1237 | 0.1194 | 0.1130 | 0.9517 / 0.3027 |
| process_disjoint | D2_process_mean | 0.1096 | [0.0908, 0.1219] | 0.1237 | 0.1194 | 0.1130 | 0.9517 / 0.3027 |
| process_disjoint | D3_hierarchical_shrinkage | 0.0994 | [0.0747, 0.1115] | 0.0843 | 0.1404 | 0.0948 | 0.8885 / 0.4179 |
| process_disjoint | D4_nearest_compatible_evidence | 0.0725 | [0.0354, 0.0967] | 0.0328 | 0.1218 | 0.0608 | 0.7182 / 0.1969 |
| process_disjoint | D5_gradient_boosting | 0.0672 | [0.034, 0.0853] | 0.0315 | 0.1163 | 0.0703 | 0.7808 / 0.2186 |
| process_disjoint | D7_biased_mf_side_info | 0.0891 | [0.0563, 0.1078] | 0.0766 | 0.1195 | 0.0852 | 0.8082 / 0.2924 |
