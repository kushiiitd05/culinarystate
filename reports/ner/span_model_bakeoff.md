# Span-model bake-off (DEV evidence only; TEST unopened except the disclosed TASTEset E0 exposure)

## TASTEset DEV, 5 seeds (exact micro F1; unseen-surface F1; boundary-error rate; train minutes; GPU GB)
| model | micro | unseen | boundary err | min | GB |
|---|---|---|---|---|---|
| DeBERTa-v3-large+CRF | 0.9443 ± 0.0037 | 0.744 | 0.0261 | 3.7 | 10.5 |
| DeBERTa-v3-large | 0.9435 ± 0.0025 | 0.736 | 0.0253 | 2.4 | 10.5 |
| DeBERTa-base+CRF | 0.9396 ± 0.0015 | 0.707 | 0.0313 | 2.4 | 3.6 |
| DeBERTa-base | 0.9390 ± 0.0027 | 0.706 | 0.0310 | 1.0 | 3.6 |
| RoBERTa-base | 0.9346 ± 0.0029 | 0.684 | 0.0320 | 0.8 | 2.5 |
| BERT-base-cased | 0.9269 ± 0.0017 | 0.650 | 0.0382 | 0.7 | 2.3 |
Paired tests (documents resampled, Holm over the ladder): CRF vs softmax on base +0.0006 CI [−0.0015, 0.0026] (3/5 seeds) INCONCLUSIVE; v3-large+CRF vs base+CRF +0.0047 CI [−0.0016, 0.0105], 5/5 seeds, unseen F1 +0.038, not significant; base vs BERT +0.0121 PROMOTED; base vs RoBERTa +0.0044 CI [0.0001, 0.0093], not significant after Holm.
Note: TASTEset DEV has only 106 recipes.

## RecipeDB3 DEV, seed 1 elimination (best dev micro F1)
| model | dev micro | minutes | GB |
|---|---|---|---|
| DeBERTa-v3-large+CRF | 0.9695 | 61 | 9.3 |
| DeBERTa-base+CRF | 0.9670 | 30 | 3.0 |
| DeBERTa-base | 0.9659 | 26 | 3.0 |
Single seed: direction agrees with TASTEset (large > base+CRF > base) but is INCONCLUSIVE. Seeds 2-3 for base, base+CRF (lane A) and v3-large+CRF (queued, jobs_v.txt) are running.

## Decision (provisional)
SPAN_PARETO_SET = { DeBERTa-base+CRF (efficiency: 1/2 time, 1/3 memory), DeBERTa-v3-large+CRF (accuracy and unseen-surface F1) }. SPAN_CHAMPION is not declared: the large model's advantage is consistent in direction on both datasets (5/5 seeds on TASTEset) but not significant, and costs 2x time / 3x memory. Resolve with RecipeDB3 seeds 2-3 for large+CRF (minimum experiment). Out-of-fold calibrator tables currently exist for base+CRF; if large is chosen they must be regenerated (cheap on TASTEset, ~5 h on RecipeDB3).
RoBERTa and BERT are dominated: REJECT from mainline.
