# DEL-2 baselines — PHENOL-EXPLORER-3.6 (seed 7) — log-RF target

rows 3,870 (censored 0); matrices 146, process signatures 33, targets 161; grid density 0.00267, propensity AUC 0.9118

- D6 TabPFN: SKIPPED (not installed; GPU)
- censored rows trained at lower bound 0.975 (assumption)
- conformal coverage is empirical (AH4)

| split | model | MAE (censor-aware) | 95% CI (grouped) | median AE | MAE log (obs) | MAE IPW | conformal-90 cov / width |
|---|---|---|---|---|---|---|---|
| random | D0_persistence | 0.8616 | [0.4681, 1.4549] | 0.32 | 0.7469 | 0.8543 | 0.8941 / 1.96 |
| random | D1_global_mean+log | 0.8389 | [0.4301, 1.4473] | 0.2781 | 0.7273 | 0.8334 | 0.8889 / 1.7362 |
| random | D2_process_mean+log | 0.8150 | [0.4107, 1.39] | 0.2965 | 0.6934 | 0.7742 | 0.8798 / 1.7702 |
| random | D3_hierarchical_shrinkage+log | 0.7245 | [0.3453, 1.2517] | 0.1932 | 0.5703 | 0.7538 | 0.8876 / 1.7685 |
| random | D4_nearest_compatible_evidence+log | 0.6688 | [0.326, 1.1262] | 0.1455 | 0.5203 | 0.8852 | 0.8941 / 1.77 |
| random | D5_gradient_boosting+log | 0.5664 | [0.285, 0.939] | 0.1416 | 0.4788 | 0.6554 | 0.9005 / 1.4602 |
| random | D7_biased_mf_side_info+log | 0.5816 | [0.3451, 0.8774] | 0.2154 | 0.5333 | 0.7307 | 0.8941 / 1.6067 |
| pair_holdout | D0_persistence | 0.7298 | [0.43, 0.9535] | 0.3 | 0.6362 | 1.2266 | 0.9166 / 3.5 |
| pair_holdout | D1_global_mean+log | 0.8902 | [0.5865, 1.1433] | 0.421 | 0.8782 | 1.3230 | 0.9166 / 4.4419 |
| pair_holdout | D2_process_mean+log | 0.8854 | [0.6099, 1.1339] | 0.4337 | 0.9984 | 1.2422 | 0.9059 / 4.3213 |
| pair_holdout | D3_hierarchical_shrinkage+log | 0.8545 | [0.5855, 1.1167] | 0.3608 | 0.9585 | 1.2404 | 0.9068 / 4.3879 |
| pair_holdout | D4_nearest_compatible_evidence+log | 0.7855 | [0.4627, 0.9648] | 0.363 | 0.795 | 1.2108 | 0.8971 / 3.4615 |
| pair_holdout | D5_gradient_boosting+log | 0.8305 | [0.5287, 1.0697] | 0.3615 | 0.8207 | 1.2551 | 0.8971 / 3.8534 |
| pair_holdout | D7_biased_mf_side_info+log | 0.8103 | [0.4653, 1.0375] | 0.3363 | 0.7873 | 1.1796 | 0.9095 / 4.2789 |
| matrix_disjoint | D0_persistence | 0.7670 | [0.4163, 1.0564] | 0.38 | 0.7439 | 0.8063 | 0.7872 / 1.7 |
| matrix_disjoint | D1_global_mean+log | 0.8080 | [0.4868, 1.1677] | 0.348 | 0.8025 | 0.8561 | 0.7887 / 1.496 |
| matrix_disjoint | D2_process_mean+log | 0.8567 | [0.5151, 1.1815] | 0.3611 | 0.8354 | 0.9078 | 0.7489 / 1.6882 |
| matrix_disjoint | D3_hierarchical_shrinkage+log | 0.8253 | [0.4889, 1.0985] | 0.3939 | 0.8272 | 0.8797 | 0.7376 / 1.6413 |
| matrix_disjoint | D4_nearest_compatible_evidence+log | 0.7875 | [0.4502, 1.0743] | 0.338 | 0.8221 | 0.8823 | 0.7631 / 1.7784 |
| matrix_disjoint | D5_gradient_boosting+log | 0.8332 | [0.4773, 1.2281] | 0.362 | 0.8309 | 0.9312 | 0.8227 / 2.2581 |
| matrix_disjoint | D7_biased_mf_side_info+log | 0.7383 | [0.4648, 0.9422] | 0.3639 | 0.7521 | 0.8486 | 0.7986 / 1.7496 |
| process_disjoint | D0_persistence | 0.3676 | [0.2211, 0.4289] | 0.22 | 0.3896 | 0.4225 | 0.9826 / 3.5 |
| process_disjoint | D1_global_mean+log | 0.4740 | [0.264, 0.5229] | 0.3301 | 0.5557 | 0.3887 | 0.9826 / 4.3603 |
| process_disjoint | D2_process_mean+log | 0.4740 | [0.264, 0.5229] | 0.3301 | 0.5557 | 0.3887 | 0.9826 / 4.3603 |
| process_disjoint | D3_hierarchical_shrinkage+log | 0.5047 | [0.3722, 0.5402] | 0.3364 | 0.7498 | 0.4285 | 0.9781 / 3.9495 |
| process_disjoint | D4_nearest_compatible_evidence+log | 0.6338 | [0.4227, 1.9126] | 0.3201 | 0.6603 | 0.7237 | 0.9449 / 3.8015 |
| process_disjoint | D5_gradient_boosting+log | 0.4483 | [0.2869, 0.8131] | 0.2563 | 0.5422 | 0.4200 | 0.9743 / 4.095 |
| process_disjoint | D7_biased_mf_side_info+log | 0.4776 | [0.303, 0.5231] | 0.32 | 0.5945 | 0.3917 | 0.9819 / 4.0724 |
| study_disjoint | D0_persistence | 0.5577 | [0.3473, 0.7583] | 0.39 | 0.6299 | 0.9737 | 0.9078 / 1.88 |
| study_disjoint | D1_global_mean+log | 0.4871 | [0.2376, 0.7278] | 0.2058 | 0.5553 | 0.9460 | 0.9157 / 2.3917 |
| study_disjoint | D2_process_mean+log | 0.5825 | [0.3124, 0.8374] | 0.2731 | 0.6456 | 1.1735 | 0.8804 / 2.6255 |
| study_disjoint | D3_hierarchical_shrinkage+log | 0.5516 | [0.2909, 0.807] | 0.2498 | 0.621 | 1.1128 | 0.9 / 2.5825 |
| study_disjoint | D4_nearest_compatible_evidence+log | 0.6995 | [0.381, 0.9978] | 0.2612 | 0.6596 | 1.6891 | 0.8843 / 2.3705 |
| study_disjoint | D5_gradient_boosting+log | 0.6118 | [0.3433, 0.8618] | 0.3589 | 0.8597 | 1.1256 | 0.9 / 2.4511 |
| study_disjoint | D7_biased_mf_side_info+log | 0.5688 | [0.3419, 0.8022] | 0.3013 | 0.7142 | 0.9725 | 0.9059 / 2.3721 |
