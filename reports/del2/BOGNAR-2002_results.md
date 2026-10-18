# DEL-2 baselines — BOGNAR-2002 (seed 7)

rows 6,594 (censored 3,274); matrices 28, process signatures 7, targets 36; grid density 0.62075, propensity AUC 0.8674

- study_disjoint: NOT POSSIBLE (single source family or one giant component) — not reported
- D6 TabPFN: SKIPPED (not installed; GPU)
- censored rows trained at lower bound 0.975 (assumption)
- conformal coverage is empirical (AH4)

| split | model | MAE (censor-aware) | 95% CI (grouped) | median AE | MAE log (obs) | MAE IPW | conformal-90 cov / width |
|---|---|---|---|---|---|---|---|
| random | D0_persistence | 0.0873 | [0.0698, 0.1054] | 0.02 | 0.2031 | 0.0817 | 0.9067 / 0.5 |
| random | D1_global_mean | 0.0926 | [0.0839, 0.1026] | 0.0871 | 0.1245 | 0.0912 | 0.9067 / 0.3159 |
| random | D2_process_mean | 0.0923 | [0.0837, 0.1016] | 0.0731 | 0.1263 | 0.0890 | 0.8983 / 0.2829 |
| random | D3_hierarchical_shrinkage | 0.0641 | [0.0554, 0.0725] | 0.0472 | 0.1049 | 0.0624 | 0.909 / 0.2965 |
| random | D4_nearest_compatible_evidence | 0.0609 | [0.0529, 0.0684] | 0.0383 | 0.1018 | 0.0538 | 0.9036 / 0.3158 |
| random | D5_gradient_boosting | 0.0483 | [0.0377, 0.0586] | 0.0231 | 0.0868 | 0.0414 | 0.9052 / 0.2788 |
| random | D7_biased_mf_side_info | 0.0607 | [0.0498, 0.0718] | 0.0439 | 0.0985 | 0.0542 | 0.8983 / 0.2925 |
| pair_holdout | D0_persistence | 0.0892 | [0.0719, 0.1117] | 0.05 | 0.2031 | 0.0771 | 0.9469 / 0.6 |
| pair_holdout | D1_global_mean | 0.0922 | [0.0816, 0.1047] | 0.0839 | 0.1265 | 0.0875 | 0.9469 / 0.4222 |
| pair_holdout | D2_process_mean | 0.0954 | [0.082, 0.1071] | 0.0827 | 0.1279 | 0.0865 | 0.9272 / 0.369 |
| pair_holdout | D3_hierarchical_shrinkage | 0.0666 | [0.0542, 0.0773] | 0.0466 | 0.1066 | 0.0591 | 0.9156 / 0.3136 |
| pair_holdout | D4_nearest_compatible_evidence | 0.0639 | [0.0459, 0.0771] | 0.0399 | 0.1036 | 0.0535 | 0.9141 / 0.349 |
| pair_holdout | D5_gradient_boosting | 0.0443 | [0.0354, 0.0524] | 0.0253 | 0.075 | 0.0369 | 0.933 / 0.2671 |
| pair_holdout | D7_biased_mf_side_info | 0.0582 | [0.0467, 0.0703] | 0.0401 | 0.0998 | 0.0499 | 0.9287 / 0.3069 |
| matrix_disjoint | D0_persistence | 0.0621 | [0.0349, 0.0825] | 0.0 | 0.1581 | 0.0562 | 0.9347 / 0.4 |
| matrix_disjoint | D1_global_mean | 0.0836 | [0.0779, 0.0861] | 0.1 | 0.074 | 0.0827 | 0.9347 / 0.2 |
| matrix_disjoint | D2_process_mean | 0.0823 | [0.0677, 0.0872] | 0.0835 | 0.077 | 0.0791 | 0.9525 / 0.2684 |
| matrix_disjoint | D3_hierarchical_shrinkage | 0.0569 | [0.0446, 0.0608] | 0.0461 | 0.0741 | 0.0554 | 0.9415 / 0.3011 |
| matrix_disjoint | D4_nearest_compatible_evidence | 0.0597 | [0.0288, 0.0791] | 0.0325 | 0.0972 | 0.0530 | 0.8898 / 0.2947 |
| matrix_disjoint | D5_gradient_boosting | 0.0463 | [0.0386, 0.0509] | 0.03 | 0.0723 | 0.0460 | 0.9373 / 0.2652 |
| matrix_disjoint | D7_biased_mf_side_info | 0.0503 | [0.0408, 0.0544] | 0.0356 | 0.0794 | 0.0510 | 0.922 / 0.2776 |
| process_disjoint | D0_persistence | 0.0385 | [0.0385, 0.0385] | 0.0 | 0.1586 | 0.0416 | 0.9928 / 0.6 |
| process_disjoint | D1_global_mean | 0.0799 | [0.0799, 0.0799] | 0.0843 | 0.0829 | 0.0820 | 0.9928 / 0.4214 |
| process_disjoint | D2_process_mean | 0.0799 | [0.0799, 0.0799] | 0.0843 | 0.0829 | 0.0820 | 0.9928 / 0.4214 |
| process_disjoint | D3_hierarchical_shrinkage | 0.0549 | [0.0549, 0.0549] | 0.0494 | 0.0951 | 0.0552 | 0.9928 / 0.3617 |
| process_disjoint | D4_nearest_compatible_evidence | 0.0398 | [0.0398, 0.0398] | 0.0341 | 0.0626 | 0.0434 | 0.9856 / 0.296 |
| process_disjoint | D5_gradient_boosting | 0.0096 | [0.0096, 0.0096] | 0.0033 | 0.0275 | 0.0111 | 1.0 / 0.3323 |
| process_disjoint | D7_biased_mf_side_info | 0.0391 | [0.0391, 0.0391] | 0.0299 | 0.0687 | 0.0407 | 0.9928 / 0.4069 |
