# TASTEset encoder NER v1 (X8)

Same recipe split as the rule floor (test 105 recipes). Selected on DEV: **deberta-v3-large_crf**. Rule floor test exact F1 0.7738 (95% CI 0.7392–0.8076). Verdict: **BEATS_FLOOR**.

| model | seeds | dev F1 | test exact F1 (mean ± sd) | test relaxed F1 | min/run |
|---|---|---|---|---|---|
| bert-base-cased | 5 | 0.9296 | 0.919 ± 0.0031 | 0.9501 | 0.6 |
| deberta-v3-base | 5 | 0.9345 | 0.922 ± 0.0013 | 0.9529 | 0.8 |
| deberta-v3-base_crf | 5 | 0.9405 | 0.9291 ± 0.0027 | 0.9567 | 1.3 |
| deberta-v3-base_knn | 5 | 0.9371 | 0.924 ± 0.0014 | 0.9537 | 1.0 |
| deberta-v3-large | 5 | 0.9408 | 0.9282 ± 0.0034 | 0.9543 | 2.0 |
| deberta-v3-large_crf | 5 | 0.9441 | 0.9332 ± 0.003 | 0.957 | 2.5 |
| roberta-base | 5 | 0.9328 | 0.9252 ± 0.002 | 0.9538 | 0.6 |

| label | bert-base-cased | deberta-v3-base | deberta-v3-base_crf | deberta-v3-base_knn | deberta-v3-large | deberta-v3-large_crf | roberta-base | rule floor (all 700) |
|---|---|---|---|---|---|---|---|---|
| COLOR | 0.8591 | 0.8368 | 0.8495 | 0.837 | 0.8565 | 0.8488 | 0.8437 | 0.8373 |
| FOOD | 0.8762 | 0.8859 | 0.8949 | 0.8881 | 0.8997 | 0.9076 | 0.8918 | 0.7534 |
| PART | 0.5455 | 0.4131 | 0.4893 | 0.5411 | 0.5095 | 0.5091 | 0.4783 | 0.6383 |
| PHYSICAL_QUALITY | 0.7686 | 0.7868 | 0.8099 | 0.7876 | 0.7895 | 0.8073 | 0.7743 | 0.5544 |
| PROCESS | 0.908 | 0.9069 | 0.9248 | 0.912 | 0.9129 | 0.9254 | 0.9078 | 0.7515 |
| PURPOSE | 0.7505 | 0.7421 | 0.7766 | 0.7316 | 0.7539 | 0.7644 | 0.75 | 0.6 |
| QUANTITY | 0.9743 | 0.9771 | 0.9776 | 0.9776 | 0.9769 | 0.9772 | 0.9798 | 0.8396 |
| TASTE | 0.7353 | 0.5088 | 0.5274 | 0.5427 | 0.6492 | 0.662 | 0.7248 | 0.6534 |
| UNIT | 0.9789 | 0.9782 | 0.9791 | 0.9797 | 0.9791 | 0.9793 | 0.9802 | 0.863 |
