# 29-diag cap-stratified losses

Status: AI_DRAFTED, 2026-11-11. **Every number in this memo carries DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / PRIOR_EXPOSURE_REANALYSIS / COND_UNAUDITED / PROVISIONAL_08A / NO_HUMAN_SIGNOFF_D085.**

Source: `reports/step29/diag/diag_results_S179.json`, RUN-S179-DIAG29-001 (D-085; WORKLOG S191).
This is a read-only transcription/interpretation of committed output, not a new model run or a new gate.
No human skim of this newly separated memo is recorded. Existing combined memo remains unchanged.

## Cap-stratified MAE (all available rungs and splits)

Each row comes from `result.families.<family>.splits.<split>.<rung>`.
The last MAE drops cap rows **from training**, then evaluates the original test set; it is not the
below-cap test-only MAE. NA means JSON null (no cap test rows), never zero.

| Family | Split | Rung | Test n | Test at cap | MAE all | MAE below cap | MAE at cap | MAE with cap training rows dropped |
|---|---|---|---:|---:|---:|---:|---:|---:|
| BOGNAR-2002 | food_group_disjoint | B2 | 1093 | 488 | 0.1058 | 0.1232 | 0.0842 | 0.1286 |
| BOGNAR-2002 | food_group_disjoint | D0 | 1093 | 488 | 0.1111 | 0.2006 | 0.0 | 0.1111 |
| BOGNAR-2002 | food_group_disjoint | D1 | 1093 | 488 | 0.1058 | 0.1232 | 0.0842 | 0.1286 |
| BOGNAR-2002 | food_group_disjoint | D2 | 1093 | 488 | 0.1044 | 0.1243 | 0.0797 | 0.1237 |
| BOGNAR-2002 | food_group_disjoint | D3 | 1093 | 488 | 0.0724 | 0.099 | 0.0394 | 0.111 |
| BOGNAR-2002 | food_group_disjoint | D4 | 1093 | 488 | 0.0662 | 0.0876 | 0.0397 | 0.1098 |
| BOGNAR-2002 | food_group_disjoint | D5 | 1093 | 488 | 0.0726 | 0.1171 | 0.0174 | 0.1002 |
| BOGNAR-2002 | food_group_disjoint | D7 | 1093 | 488 | 0.0709 | 0.0999 | 0.0349 | 0.108 |
| BOGNAR-2002 | matrix_disjoint | B2 | 894 | 506 | 0.0853 | 0.0681 | 0.0985 | 0.1302 |
| BOGNAR-2002 | matrix_disjoint | D0 | 894 | 506 | 0.0588 | 0.1356 | 0.0 | 0.0588 |
| BOGNAR-2002 | matrix_disjoint | D1 | 894 | 506 | 0.0804 | 0.0563 | 0.0989 | 0.1368 |
| BOGNAR-2002 | matrix_disjoint | D2 | 894 | 506 | 0.0782 | 0.062 | 0.0906 | 0.123 |
| BOGNAR-2002 | matrix_disjoint | D3 | 894 | 506 | 0.0522 | 0.0547 | 0.0503 | 0.112 |
| BOGNAR-2002 | matrix_disjoint | D4 | 894 | 506 | 0.0592 | 0.0763 | 0.046 | 0.1135 |
| BOGNAR-2002 | matrix_disjoint | D5 | 894 | 506 | 0.0396 | 0.0527 | 0.0296 | 0.0951 |
| BOGNAR-2002 | matrix_disjoint | D7 | 894 | 506 | 0.05 | 0.0609 | 0.0417 | 0.1078 |
| BOGNAR-2002 | pair_holdout | B2 | 1058 | 501 | 0.0972 | 0.1002 | 0.0939 | 0.1306 |
| BOGNAR-2002 | pair_holdout | D0 | 1058 | 501 | 0.0991 | 0.1883 | 0.0 | 0.0991 |
| BOGNAR-2002 | pair_holdout | D1 | 1058 | 501 | 0.0993 | 0.1126 | 0.0845 | 0.1322 |
| BOGNAR-2002 | pair_holdout | D2 | 1058 | 501 | 0.0997 | 0.1123 | 0.0857 | 0.1312 |
| BOGNAR-2002 | pair_holdout | D3 | 1058 | 501 | 0.0705 | 0.0913 | 0.0474 | 0.1177 |
| BOGNAR-2002 | pair_holdout | D4 | 1058 | 501 | 0.0658 | 0.0794 | 0.0506 | 0.1162 |
| BOGNAR-2002 | pair_holdout | D5 | 1058 | 501 | 0.0492 | 0.0616 | 0.0353 | 0.0921 |
| BOGNAR-2002 | pair_holdout | D7 | 1058 | 501 | 0.0677 | 0.0764 | 0.0581 | 0.109 |
| BOGNAR-2002 | process_disjoint | B2 | 139 | 101 | 0.0722 | 0.0758 | 0.0708 | 0.1525 |
| BOGNAR-2002 | process_disjoint | D0 | 139 | 101 | 0.0385 | 0.1408 | 0.0 | 0.0385 |
| BOGNAR-2002 | process_disjoint | D1 | 139 | 101 | 0.0782 | 0.0697 | 0.0814 | 0.1454 |
| BOGNAR-2002 | process_disjoint | D2 | 139 | 101 | 0.0782 | 0.0697 | 0.0814 | 0.1454 |
| BOGNAR-2002 | process_disjoint | D3 | 139 | 101 | 0.0523 | 0.0743 | 0.044 | 0.1317 |
| BOGNAR-2002 | process_disjoint | D4 | 139 | 101 | 0.0398 | 0.0517 | 0.0353 | 0.1318 |
| BOGNAR-2002 | process_disjoint | D5 | 139 | 101 | 0.0103 | 0.0191 | 0.0069 | 0.0775 |
| BOGNAR-2002 | process_disjoint | D7 | 139 | 101 | 0.0558 | 0.0666 | 0.0518 | 0.1175 |
| BOGNAR-2002 | random | B2 | 1036 | 537 | 0.0861 | 0.0923 | 0.0804 | 0.1243 |
| BOGNAR-2002 | random | D0 | 1036 | 537 | 0.0833 | 0.173 | 0.0 | 0.0833 |
| BOGNAR-2002 | random | D1 | 1036 | 537 | 0.0917 | 0.0968 | 0.0869 | 0.1342 |
| BOGNAR-2002 | random | D2 | 1036 | 537 | 0.0904 | 0.0972 | 0.0841 | 0.129 |
| BOGNAR-2002 | random | D3 | 1036 | 537 | 0.0642 | 0.0824 | 0.0472 | 0.1155 |
| BOGNAR-2002 | random | D4 | 1036 | 537 | 0.0623 | 0.0821 | 0.044 | 0.1097 |
| BOGNAR-2002 | random | D5 | 1036 | 537 | 0.0499 | 0.066 | 0.0349 | 0.0858 |
| BOGNAR-2002 | random | D7 | 1036 | 537 | 0.0572 | 0.0809 | 0.0353 | 0.0906 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | B2 | 612 | 0 | 0.5611 | 0.5611 | NA | 0.5611 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | D0 | 612 | 0 | 0.4063 | 0.4063 | NA | 0.4063 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | D1 | 612 | 0 | 0.4669 | 0.4669 | NA | 0.4669 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | D2 | 612 | 0 | 0.7587 | 0.7587 | NA | 0.7587 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | D3 | 612 | 0 | 0.6918 | 0.6918 | NA | 0.6918 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | D4 | 612 | 0 | 0.4349 | 0.4349 | NA | 0.4349 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | D5 | 612 | 0 | 0.7184 | 0.7184 | NA | 0.7184 |
| PHENOL-EXPLORER-3.6 | food_group_disjoint | D7 | 612 | 0 | 0.4669 | 0.4669 | NA | 0.4669 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | B2 | 286 | 0 | 0.5148 | 0.5148 | NA | 0.5148 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D0 | 286 | 0 | 0.4889 | 0.4889 | NA | 0.4889 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D1 | 286 | 0 | 0.6557 | 0.6557 | NA | 0.6557 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D2 | 286 | 0 | 0.753 | 0.753 | NA | 0.753 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D3 | 286 | 0 | 0.7556 | 0.7556 | NA | 0.7556 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D4 | 286 | 0 | 0.4498 | 0.4498 | NA | 0.4498 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D5 | 286 | 0 | 0.5487 | 0.5487 | NA | 0.5487 |
| PHENOL-EXPLORER-3.6 | matrix_disjoint | D7 | 286 | 0 | 0.6557 | 0.6557 | NA | 0.6557 |
| PHENOL-EXPLORER-3.6 | pair_holdout | B2 | 757 | 0 | 1.0046 | 1.0046 | NA | 1.0046 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D0 | 757 | 0 | 1.0834 | 1.0834 | NA | 1.0834 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D1 | 757 | 0 | 1.0975 | 1.0975 | NA | 1.0975 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D2 | 757 | 0 | 1.1351 | 1.1351 | NA | 1.1351 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D3 | 757 | 0 | 1.0982 | 1.0982 | NA | 1.0982 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D4 | 757 | 0 | 1.0772 | 1.0772 | NA | 1.0772 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D5 | 757 | 0 | 1.0357 | 1.0357 | NA | 1.0357 |
| PHENOL-EXPLORER-3.6 | pair_holdout | D7 | 757 | 0 | 1.0975 | 1.0975 | NA | 1.0975 |
| PHENOL-EXPLORER-3.6 | process_disjoint | B2 | 1135 | 0 | 0.4171 | 0.4171 | NA | 0.4171 |
| PHENOL-EXPLORER-3.6 | process_disjoint | D0 | 1135 | 0 | 0.3896 | 0.3896 | NA | 0.3896 |
| PHENOL-EXPLORER-3.6 | process_disjoint | D1 | 1135 | 0 | 0.3714 | 0.3714 | NA | 0.3714 |
| PHENOL-EXPLORER-3.6 | process_disjoint | D2 | 1135 | 0 | 0.3714 | 0.3714 | NA | 0.3714 |
| PHENOL-EXPLORER-3.6 | process_disjoint | D3 | 1135 | 0 | 0.4542 | 0.4542 | NA | 0.4542 |
| PHENOL-EXPLORER-3.6 | process_disjoint | D4 | 1135 | 0 | 0.5903 | 0.5903 | NA | 0.5903 |
| PHENOL-EXPLORER-3.6 | process_disjoint | D5 | 1135 | 0 | 0.5004 | 0.5004 | NA | 0.5004 |
| PHENOL-EXPLORER-3.6 | process_disjoint | D7 | 1135 | 0 | 0.3714 | 0.3714 | NA | 0.3714 |
| PHENOL-EXPLORER-3.6 | random | B2 | 635 | 0 | 0.7737 | 0.7737 | NA | 0.7737 |
| PHENOL-EXPLORER-3.6 | random | D0 | 635 | 0 | 0.7139 | 0.7139 | NA | 0.7139 |
| PHENOL-EXPLORER-3.6 | random | D1 | 635 | 0 | 0.8087 | 0.8087 | NA | 0.8087 |
| PHENOL-EXPLORER-3.6 | random | D2 | 635 | 0 | 0.7605 | 0.7605 | NA | 0.7605 |
| PHENOL-EXPLORER-3.6 | random | D3 | 635 | 0 | 0.573 | 0.573 | NA | 0.573 |
| PHENOL-EXPLORER-3.6 | random | D4 | 635 | 0 | 0.5635 | 0.5635 | NA | 0.5635 |
| PHENOL-EXPLORER-3.6 | random | D5 | 635 | 0 | 0.5468 | 0.5468 | NA | 0.5468 |
| PHENOL-EXPLORER-3.6 | random | D7 | 635 | 0 | 0.8087 | 0.8087 | NA | 0.8087 |
| PHENOL-EXPLORER-3.6 | study_disjoint | B2 | 362 | 0 | 0.4035 | 0.4035 | NA | 0.4035 |
| PHENOL-EXPLORER-3.6 | study_disjoint | D0 | 362 | 0 | 0.3622 | 0.3622 | NA | 0.3622 |
| PHENOL-EXPLORER-3.6 | study_disjoint | D1 | 362 | 0 | 0.5529 | 0.5529 | NA | 0.5529 |
| PHENOL-EXPLORER-3.6 | study_disjoint | D2 | 362 | 0 | 0.5274 | 0.5274 | NA | 0.5274 |
| PHENOL-EXPLORER-3.6 | study_disjoint | D3 | 362 | 0 | 0.5501 | 0.5501 | NA | 0.5501 |
| PHENOL-EXPLORER-3.6 | study_disjoint | D4 | 362 | 0 | 0.5619 | 0.5619 | NA | 0.5619 |
| PHENOL-EXPLORER-3.6 | study_disjoint | D5 | 362 | 0 | 0.3497 | 0.3497 | NA | 0.3497 |
| PHENOL-EXPLORER-3.6 | study_disjoint | D7 | 362 | 0 | 0.5529 | 0.5529 | NA | 0.5529 |
| USDA-RETN-R6 | food_group_disjoint | B2 | 1144 | 302 | 0.1357 | 0.154 | 0.0847 | 0.1303 |
| USDA-RETN-R6 | food_group_disjoint | D0 | 1144 | 302 | 0.1838 | 0.2497 | 0.0 | 0.1838 |
| USDA-RETN-R6 | food_group_disjoint | D1 | 1144 | 302 | 0.1357 | 0.154 | 0.0847 | 0.1303 |
| USDA-RETN-R6 | food_group_disjoint | D2 | 1144 | 302 | 0.1217 | 0.1351 | 0.0844 | 0.1178 |
| USDA-RETN-R6 | food_group_disjoint | D3 | 1144 | 302 | 0.0943 | 0.113 | 0.0423 | 0.1085 |
| USDA-RETN-R6 | food_group_disjoint | D4 | 1144 | 302 | 0.0756 | 0.0992 | 0.0099 | 0.1224 |
| USDA-RETN-R6 | food_group_disjoint | D5 | 1144 | 302 | 0.0983 | 0.1254 | 0.0229 | 0.1064 |
| USDA-RETN-R6 | food_group_disjoint | D7 | 1144 | 302 | 0.0869 | 0.1095 | 0.0238 | 0.1046 |
| USDA-RETN-R6 | matrix_disjoint | B2 | 1015 | 565 | 0.0798 | 0.069 | 0.0883 | 0.1066 |
| USDA-RETN-R6 | matrix_disjoint | D0 | 1015 | 565 | 0.0602 | 0.1358 | 0.0 | 0.0602 |
| USDA-RETN-R6 | matrix_disjoint | D1 | 1015 | 565 | 0.1011 | 0.0725 | 0.124 | 0.1479 |
| USDA-RETN-R6 | matrix_disjoint | D2 | 1015 | 565 | 0.0914 | 0.0677 | 0.1103 | 0.1319 |
| USDA-RETN-R6 | matrix_disjoint | D3 | 1015 | 565 | 0.0834 | 0.0762 | 0.0891 | 0.1236 |
| USDA-RETN-R6 | matrix_disjoint | D4 | 1015 | 565 | 0.0499 | 0.0607 | 0.0414 | 0.0933 |
| USDA-RETN-R6 | matrix_disjoint | D5 | 1015 | 565 | 0.0601 | 0.0706 | 0.0517 | 0.1385 |
| USDA-RETN-R6 | matrix_disjoint | D7 | 1015 | 565 | 0.0794 | 0.0717 | 0.0855 | 0.1023 |
| USDA-RETN-R6 | pair_holdout | B2 | 962 | 388 | 0.0875 | 0.0851 | 0.0911 | 0.1206 |
| USDA-RETN-R6 | pair_holdout | D0 | 962 | 388 | 0.1028 | 0.1723 | 0.0 | 0.1028 |
| USDA-RETN-R6 | pair_holdout | D1 | 962 | 388 | 0.0974 | 0.0876 | 0.112 | 0.1303 |
| USDA-RETN-R6 | pair_holdout | D2 | 962 | 388 | 0.0795 | 0.0863 | 0.0694 | 0.0987 |
| USDA-RETN-R6 | pair_holdout | D3 | 962 | 388 | 0.0664 | 0.0805 | 0.0456 | 0.0962 |
| USDA-RETN-R6 | pair_holdout | D4 | 962 | 388 | 0.0391 | 0.0542 | 0.0167 | 0.0948 |
| USDA-RETN-R6 | pair_holdout | D5 | 962 | 388 | 0.0437 | 0.0614 | 0.0177 | 0.0805 |
| USDA-RETN-R6 | pair_holdout | D7 | 962 | 388 | 0.0572 | 0.0715 | 0.0359 | 0.0835 |
| USDA-RETN-R6 | process_disjoint | B2 | 988 | 351 | 0.0894 | 0.0965 | 0.0766 | 0.1298 |
| USDA-RETN-R6 | process_disjoint | D0 | 988 | 351 | 0.1316 | 0.2042 | 0.0 | 0.1316 |
| USDA-RETN-R6 | process_disjoint | D1 | 988 | 351 | 0.1102 | 0.1117 | 0.1074 | 0.131 |
| USDA-RETN-R6 | process_disjoint | D2 | 988 | 351 | 0.1102 | 0.1117 | 0.1074 | 0.131 |
| USDA-RETN-R6 | process_disjoint | D3 | 988 | 351 | 0.0871 | 0.0992 | 0.0653 | 0.1239 |
| USDA-RETN-R6 | process_disjoint | D4 | 988 | 351 | 0.0347 | 0.0474 | 0.0116 | 0.0937 |
| USDA-RETN-R6 | process_disjoint | D5 | 988 | 351 | 0.0459 | 0.0594 | 0.0214 | 0.0846 |
| USDA-RETN-R6 | process_disjoint | D7 | 988 | 351 | 0.0728 | 0.0807 | 0.0586 | 0.1043 |
| USDA-RETN-R6 | random | B2 | 1128 | 396 | 0.0893 | 0.0943 | 0.0802 | 0.1182 |
| USDA-RETN-R6 | random | D0 | 1128 | 396 | 0.1298 | 0.2001 | 0.0 | 0.1298 |
| USDA-RETN-R6 | random | D1 | 1128 | 396 | 0.1118 | 0.1155 | 0.1049 | 0.1308 |
| USDA-RETN-R6 | random | D2 | 1128 | 396 | 0.0825 | 0.0889 | 0.0706 | 0.1101 |
| USDA-RETN-R6 | random | D3 | 1128 | 396 | 0.0647 | 0.0726 | 0.0501 | 0.096 |
| USDA-RETN-R6 | random | D4 | 1128 | 396 | 0.0384 | 0.0502 | 0.0164 | 0.0874 |
| USDA-RETN-R6 | random | D5 | 1128 | 396 | 0.0251 | 0.0329 | 0.0107 | 0.0595 |
| USDA-RETN-R6 | random | D7 | 1128 | 396 | 0.0498 | 0.0599 | 0.0312 | 0.081 |

## Cap-artefact conclusion

The lower D5 pair-holdout loss is not confined to cap test rows in these source-key splits. USDA D5 below-cap
MAE is 0.0614 versus D2 0.0863 and D1 0.0876; Bognár D5 is 0.0616 versus D2 0.1123 and D1 0.1126.
Dropping cap training rows changes D5 all-test MAE from 0.0437 to 0.0805 (USDA), and 0.0492 to 0.0921
(Bognár). Thus cap handling materially affects the numerical result; the cap alone does not explain all of
the observed pair-holdout difference. Repeated source values and shared lineage remain competing explanations.
This is not evidence of generalisation to independent studies. The duplicate-safe results are reported
separately, and the cap sensitivity is descriptive; no post-hoc cap choice is selected.
