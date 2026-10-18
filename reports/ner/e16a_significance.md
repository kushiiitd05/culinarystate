# E16-A Paired Bootstrap Significance

2000 bootstrap resamples over 105 recipe groups (seed 42).

| Comparison | Δ F1 | p-value | 95% CI | Significant? |
|---|---|---|---|---|
| CRF vs base | +0.0047 | 0.003 | [+0.0012, +0.0082] | YES |
| CRF vs kNN | +0.0047 | 0.003 | [+0.0012, +0.0082] | YES |
| large+CRF vs base+CRF | +0.0111 | 0.004 | [+0.0030, +0.0201] | YES |
| large+CRF vs large | +0.0049 | 0.003 | [+0.0014, +0.0088] | YES |
| base+CRF vs RoBERTa | +0.0051 | 0.126 | [-0.0035, +0.0136] | n.s. |
| base+CRF vs BERT | +0.0091 | 0.022 | [+0.0002, +0.0179] | YES |
| large+CRF vs RoBERTa | +0.0162 | 0.000 | [+0.0078, +0.0253] | YES |
| kNN vs base | +0.0000 | 1.000 | [+0.0000, +0.0000] | n.s. |

## kNN-NER: confirmed negative result

kNN-NER (Khandelwal et al., 2020 adapted) produces **zero prediction changes** across all 5 seeds
(105 test recipes each). Best dev hyperparameters: k=8, λ=0.25, τ=0.05.

The encoder logits are sufficiently peaked that even 25% kNN interpolation weight never flips any
argmax. The kNN datastore adds compute cost (neighbor search over ~9k train word states) with no
accuracy gain.

**Decision (SSOT §257B promotion rule):** kNN-NER excluded from the hybrid pipeline. Negative
result retained in the report. Layer 3 slot remains available for a method that actually helps
(e.g., retrieval-augmented verification on long-tail entities).

## Per-model variance (5 seeds)

| Model | Mean F1 | Std | Min | Max |
|---|---|---|---|---|
| bert-base-cased | 0.9190 | 0.0031 | 0.9145 | 0.9239 |
| roberta-base | 0.9252 | 0.0020 | 0.9215 | 0.9273 |
| deberta-v3-base | 0.9220 | 0.0013 | 0.9203 | 0.9244 |
| deberta-v3-base_crf | 0.9291 | 0.0027 | 0.9254 | 0.9327 |
| deberta-v3-base_knn | 0.9220 | 0.0013 | 0.9203 | 0.9244 |
| deberta-v3-large | 0.9282 | 0.0034 | 0.9239 | 0.9329 |
| deberta-v3-large_crf | 0.9332 | 0.0030 | 0.9288 | 0.9378 |
