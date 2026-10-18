# DEL-2 baselines — PHENOL-EXPLORER-3.6 (seed 7)

rows 3,870 (censored 0); matrices 146, process signatures 33, targets 161; grid density 0.00267, propensity AUC 0.9118

- D6 TabPFN: SKIPPED (not installed; GPU)
- censored rows trained at lower bound 0.975 (assumption)
- conformal coverage is empirical (AH4)

| split | model | MAE (censor-aware) | 95% CI (grouped) | MAE IPW | RMSE obs | conformal-90 cov / width |
|---|---|---|---|---|---|---|
| random | D0_persistence | 0.8616 | [0.4962, 1.4549] | 0.8543 | 4.9136 | 0.8941 / 1.96 |
| random | D1_global_mean | 0.9622 | [0.6121, 1.5422] | 0.9301 | 4.9062 | 0.9005 / 2.2728 |
| random | D2_process_mean | 0.9034 | [0.561, 1.462] | 0.9032 | 4.7904 | 0.916 / 2.6039 |
| random | D3_hierarchical_shrinkage | 0.7833 | [0.4928, 1.271] | 0.8872 | 4.0998 | 0.9044 / 2.2924 |
| random | D4_nearest_compatible_evidence | 0.7338 | [0.436, 1.1847] | 1.0939 | 3.5261 | 0.8941 / 2.0761 |
| random | D5_gradient_boosting | 0.7435 | [0.4445, 1.2216] | 0.9312 | 3.67 | 0.9096 / 2.6838 |
| random | D7_biased_mf_side_info | nan | [nan, nan] | nan | nan | 0.0 / nan |
| pair_holdout | D0_persistence | 0.7298 | [0.4255, 1.0051] | 1.2266 | 1.7427 | 0.9166 / 3.5 |
| pair_holdout | D1_global_mean | 0.7263 | [0.4117, 1.0046] | 1.2218 | 1.7637 | 0.9166 / 3.6973 |
| pair_holdout | D2_process_mean | 0.7951 | [0.5058, 1.0399] | 1.2901 | 1.8004 | 0.8917 / 3.0247 |
| pair_holdout | D3_hierarchical_shrinkage | 0.7725 | [0.4654, 1.0031] | 1.2670 | 1.7969 | 0.8909 / 2.8919 |
| pair_holdout | D4_nearest_compatible_evidence | 0.7652 | [0.4304, 1.0055] | 1.1979 | 1.7895 | 0.8971 / 3.4006 |
| pair_holdout | D5_gradient_boosting | 0.7901 | [0.5452, 1.0091] | 1.2736 | 1.8021 | 0.929 / 3.8159 |
| pair_holdout | D7_biased_mf_side_info | nan | [nan, nan] | nan | nan | 0.0 / nan |
| matrix_disjoint | D0_persistence | 0.7670 | [0.4163, 1.1032] | 0.8063 | 1.6984 | 0.7872 / 1.7 |
| matrix_disjoint | D1_global_mean | 0.8468 | [0.5343, 1.1387] | 0.8631 | 1.6773 | 0.8014 / 2.0485 |
| matrix_disjoint | D2_process_mean | 0.9881 | [0.6068, 1.3211] | 1.2552 | 2.0336 | 0.8312 / 2.6397 |
| matrix_disjoint | D3_hierarchical_shrinkage | 0.9554 | [0.593, 1.275] | 1.2165 | 2.0009 | 0.7858 / 2.0403 |
| matrix_disjoint | D4_nearest_compatible_evidence | 0.7988 | [0.4682, 1.0817] | 0.9528 | 1.723 | 0.8085 / 2.2704 |
| matrix_disjoint | D5_gradient_boosting | 0.9088 | [0.5231, 1.3139] | 1.0625 | 1.8478 | 0.7702 / 2.2171 |
| matrix_disjoint | D7_biased_mf_side_info | nan | [nan, nan] | nan | nan | 0.0 / nan |
| process_disjoint | D0_persistence | 0.3676 | [0.2211, 0.4221] | 0.4225 | 1.0186 | 0.9826 / 3.5 |
| process_disjoint | D1_global_mean | 0.5016 | [0.3725, 0.5905] | 0.5905 | 1.0457 | 0.9826 / 3.0409 |
| process_disjoint | D2_process_mean | 0.5016 | [0.3725, 0.5905] | 0.5905 | 1.0457 | 0.9826 / 3.0409 |
| process_disjoint | D3_hierarchical_shrinkage | 0.5677 | [0.5067, 0.8801] | 0.7876 | 1.1922 | 0.9585 / 4.0472 |
| process_disjoint | D4_nearest_compatible_evidence | 0.7334 | [0.4996, 2.0319] | 0.9056 | 2.7739 | 0.9381 / 4.495 |
| process_disjoint | D5_gradient_boosting | 0.6004 | [0.3704, 1.5786] | 0.6299 | 1.9816 | 0.9464 / 3.8412 |
| process_disjoint | D7_biased_mf_side_info | nan | [nan, nan] | nan | nan | 0.0 / nan |
| study_disjoint | D0_persistence | 0.5577 | [0.3558, 0.747] | 0.9737 | 1.0668 | 0.9078 / 1.88 |
| study_disjoint | D1_global_mean | 0.6978 | [0.5273, 0.854] | 1.0710 | 1.098 | 0.9078 / 2.0844 |
| study_disjoint | D2_process_mean | 0.9647 | [0.5336, 1.4309] | 1.6594 | 1.6552 | 0.851 / 2.949 |
| study_disjoint | D3_hierarchical_shrinkage | 0.7922 | [0.4076, 1.1791] | 1.5880 | 1.4573 | 0.8765 / 2.918 |
| study_disjoint | D4_nearest_compatible_evidence | 0.9880 | [0.4353, 1.5469] | 2.3658 | 3.8422 | 0.8765 / 2.336 |
| study_disjoint | D5_gradient_boosting | 0.7551 | [0.5007, 0.9882] | 1.2082 | 1.2571 | 0.8275 / 2.3936 |
| study_disjoint | D7_biased_mf_side_info | nan | [nan, nan] | nan | nan | 0.0 / nan |
