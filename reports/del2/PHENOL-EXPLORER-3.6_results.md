# DEL-2 baselines — PHENOL-EXPLORER-3.6 (seed 7)

rows 3,870 (censored 0); matrices 146, process signatures 33, targets 161; grid density 0.00267, propensity AUC 0.9118

- D6 TabPFN: SKIPPED (not installed; GPU)
- censored rows trained at lower bound 0.975 (assumption)
- conformal coverage is empirical (AH4)

| split | model | MAE (censor-aware) | 95% CI (grouped) | median AE | MAE log (obs) | MAE IPW | conformal-90 cov / width |
|---|---|---|---|---|---|---|---|
| random | D0_persistence | 0.8616 | [0.4681, 1.4549] | 0.32 | 0.7469 | 0.8543 | 0.8941 / 1.96 |
| random | D1_global_mean | 0.9622 | [0.5743, 1.5422] | 0.4664 | 0.8391 | 0.9301 | 0.9005 / 2.2728 |
| random | D2_process_mean | 0.9034 | [0.5478, 1.462] | 0.3481 | 0.7518 | 0.9032 | 0.916 / 2.6039 |
| random | D3_hierarchical_shrinkage | 0.7833 | [0.4828, 1.1638] | 0.2662 | 0.6489 | 0.8872 | 0.9044 / 2.2924 |
| random | D4_nearest_compatible_evidence | 0.7338 | [0.436, 1.1012] | 0.1645 | 0.5418 | 1.0939 | 0.8941 / 2.0761 |
| random | D5_gradient_boosting | 0.7435 | [0.4434, 1.0921] | 0.1788 | 0.7045 | 0.9312 | 0.9096 / 2.6838 |
| random | D7_biased_mf_side_info | 0.9622 | [0.5743, 1.5422] | 0.4664 | 0.8391 | 0.9301 | 0.9005 / 2.2728 |
| pair_holdout | D0_persistence | 0.7298 | [0.43, 0.9535] | 0.3 | 0.6362 | 1.2266 | 0.9166 / 3.5 |
| pair_holdout | D1_global_mean | 0.7263 | [0.4122, 0.9667] | 0.2814 | 0.6329 | 1.2218 | 0.9166 / 3.6973 |
| pair_holdout | D2_process_mean | 0.7951 | [0.5532, 0.9782] | 0.4023 | 0.7308 | 1.2901 | 0.8917 / 3.0247 |
| pair_holdout | D3_hierarchical_shrinkage | 0.7725 | [0.5262, 0.9724] | 0.368 | 0.7226 | 1.2670 | 0.8909 / 2.8919 |
| pair_holdout | D4_nearest_compatible_evidence | 0.7652 | [0.436, 0.9393] | 0.3035 | 0.6911 | 1.1979 | 0.8971 / 3.4006 |
| pair_holdout | D5_gradient_boosting | 0.7901 | [0.5831, 0.9592] | 0.3711 | 0.839 | 1.2736 | 0.929 / 3.8159 |
| pair_holdout | D7_biased_mf_side_info | 0.7263 | [0.4122, 0.9667] | 0.2814 | 0.6329 | 1.2218 | 0.9166 / 3.6973 |
| matrix_disjoint | D0_persistence | 0.7670 | [0.4163, 1.0564] | 0.38 | 0.7439 | 0.8063 | 0.7872 / 1.7 |
| matrix_disjoint | D1_global_mean | 0.8468 | [0.5023, 1.081] | 0.5157 | 0.8162 | 0.8631 | 0.8014 / 2.0485 |
| matrix_disjoint | D2_process_mean | 0.9881 | [0.6068, 1.3063] | 0.4005 | 0.7907 | 1.2552 | 0.8312 / 2.6397 |
| matrix_disjoint | D3_hierarchical_shrinkage | 0.9554 | [0.5956, 1.2422] | 0.3531 | 0.7655 | 1.2165 | 0.7858 / 2.0403 |
| matrix_disjoint | D4_nearest_compatible_evidence | 0.7988 | [0.4877, 1.0382] | 0.326 | 0.751 | 0.9528 | 0.8085 / 2.2704 |
| matrix_disjoint | D5_gradient_boosting | 0.9088 | [0.5223, 1.271] | 0.4024 | 1.1985 | 1.0625 | 0.7702 / 2.2171 |
| matrix_disjoint | D7_biased_mf_side_info | 0.8468 | [0.5023, 1.081] | 0.5157 | 0.8162 | 0.8631 | 0.8014 / 2.0485 |
| process_disjoint | D0_persistence | 0.3676 | [0.2211, 0.4289] | 0.22 | 0.3896 | 0.4225 | 0.9826 / 3.5 |
| process_disjoint | D1_global_mean | 0.5016 | [0.3725, 0.612] | 0.3696 | 0.5091 | 0.5905 | 0.9826 / 3.0409 |
| process_disjoint | D2_process_mean | 0.5016 | [0.3725, 0.612] | 0.3696 | 0.5091 | 0.5905 | 0.9826 / 3.0409 |
| process_disjoint | D3_hierarchical_shrinkage | 0.5677 | [0.5042, 0.9211] | 0.3077 | 0.5263 | 0.7876 | 0.9585 / 4.0472 |
| process_disjoint | D4_nearest_compatible_evidence | 0.7334 | [0.4686, 2.6361] | 0.3295 | 0.6071 | 0.9056 | 0.9381 / 4.495 |
| process_disjoint | D5_gradient_boosting | 0.6004 | [0.3626, 2.1343] | 0.2949 | 0.5441 | 0.6299 | 0.9464 / 3.8412 |
| process_disjoint | D7_biased_mf_side_info | 0.5016 | [0.3725, 0.612] | 0.3696 | 0.5091 | 0.5905 | 0.9826 / 3.0409 |
| study_disjoint | D0_persistence | 0.5577 | [0.3473, 0.7583] | 0.39 | 0.6299 | 0.9737 | 0.9078 / 1.88 |
| study_disjoint | D1_global_mean | 0.6978 | [0.5272, 0.8646] | 0.5822 | 0.756 | 1.0710 | 0.9078 / 2.0844 |
| study_disjoint | D2_process_mean | 0.9647 | [0.5507, 1.3563] | 0.5561 | 0.8268 | 1.6594 | 0.851 / 2.949 |
| study_disjoint | D3_hierarchical_shrinkage | 0.7922 | [0.408, 1.1481] | 0.3938 | 0.7241 | 1.5880 | 0.8765 / 2.918 |
| study_disjoint | D4_nearest_compatible_evidence | 0.9880 | [0.4365, 1.5469] | 0.34 | 0.6968 | 2.3658 | 0.8765 / 2.336 |
| study_disjoint | D5_gradient_boosting | 0.7551 | [0.4977, 0.9877] | 0.446 | 1.2742 | 1.2082 | 0.8275 / 2.3936 |
| study_disjoint | D7_biased_mf_side_info | 0.6978 | [0.5272, 0.8646] | 0.5822 | 0.756 | 1.0710 | 0.9078 / 2.0844 |
