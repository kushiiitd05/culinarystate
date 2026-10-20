# Metadata / linker signals: cross-dataset calibration confirmation (DEV only; TEST and CALIBRATION untouched)

Script `tools/e2_signal_calibration.py` (successor of the S125 script; raw `_e2b_<dataset>_<tag>.json`). Baseline **P0** = calibrated logit(span confidence) of DeBERTa-base+CRF (logreg + isotonic fit on 5-fold OOF train spans: TASTEset 8,225 / RecipeDB3 65,716; DEV: 2,067 spans, 106 docs / 9,171 spans, 2,596 docs). Each block added to P0 alone. Paired document bootstrap (500 / 300), Holm per family, scope pre-declared (M1, M2, G1 = FOOD/NAME spans; M7 = rule-covered types; M5, M6, G2 = all spans).
Control **C** = P0 + label one-hot + length (no semantic signal).

## Method correction made during this stage (affects S125 AURC statements)
P0 confidences are heavily quantised (RecipeDB3: 253 distinct values on 2,948 FOOD spans) and isotonic output has plateaus, so AURC / precision@coverage depended on arbitrary tie order. All ranking metrics now use the continuous pre-isotonic score with expected-over-random-tie-breaking AURC and precision@coverage (unit-tested on a hand case). NLL is computed on the isotonic output clipped at 1e-3. Calibration (NLL/ECE) conclusions on TASTEset are unchanged; S125 AURC deltas were tie artefacts and are superseded.

## Results vs P0 (BGE linker, seed 1; dNLL negative = better)
| Block (scope) | TASTEset dNLL [CI] | TASTEset dAURC | RecipeDB3 dNLL [CI] | RecipeDB3 dAURC | cross-dataset |
|---|---|---|---|---|---|
| M1 linker top-1 (FOOD) | -0.0196 [-0.036,-0.006] | -0.003 n.s. | **+0.0099 [+0.003,+0.017]** | -0.004 n.s. | REVERSES -> REJECT (dataset-specific) |
| M2 margin/entropy (FOOD) | -0.0155 [-0.028,-0.004] (Holm miss) | -0.001 n.s. | **+0.0060 [+0.000,+0.012]** | -0.000 n.s. | REVERSES -> REJECT |
| M5 frequency/tail (all) | -0.0050 [-0.014,+0.004] | -0.001 n.s. | -0.0007 [-0.004,+0.003] | -0.0068 [-0.009,-0.004] | direction agrees, magnitude negligible; ranking gain = label identity (see below) -> INCONCLUSIVE, left out |
| M6 gazetteer agreement (all) | **-0.0089 [-0.017,-0.003]** (Holm p=.004) | -0.000 | -0.0012 [-0.005,+0.002] | -0.0030 [-0.004,-0.002] | significant on TASTEset, neutral (no harm) on RecipeDB3 -> PROMOTE, regime-conditional |
| G1 external ledger aliases (FOOD) | -0.0159 [-0.035,-0.002] (p=.028) | +0.0024 (worse) | +0.0057 [-0.001,+0.012] | -0.0036 | REJECT as added source (below) |
| G2 = M6+G1 (all) | -0.0068 [-0.016,+0.000] | -0.001 | -0.0004 | -0.0050 | no gain over M6 -> REJECT |
| M7 rule agreement (rule-covered types) | +0.0012 [-0.004,+0.008] | -0.0007 | +0.0004 [-0.002,+0.003] | -0.0040 | REJECT |
P0 calibration is already good on RecipeDB3 (ECE 0.009 all / 0.015 FOOD vs TASTEset 0.027 / 0.052), so there is little room for calibration features there.

## Risk-ranking is label identity, not semantic signal
RecipeDB3 AURC gains of M5/M6/M7/G2 vs P0 (-0.003 to -0.007) equal what the nuisance control C gets (C vs P0 dAURC -0.0060 [-0.0078,-0.0041]). Versus C, M6 and M7 are *worse* on AURC (+0.0030 [+0.0012,+0.0047], +0.0022 [+0.0005,+0.0039]); M1 vs C also worse (+0.0021 all spans). On TASTEset no block improves AURC vs P0 or C with CI excluding 0. Conclusion: M1/M6 are calibration signals only; the one robust ranking effect is class-conditional (per-label) confidence, which the router already stratifies by.

## Safe ledger aliases (G0 = M6, G1, G2) with the provenance audit attached (`alias_leakage_audit.md`: ALLOWED, 0 benchmark-provenance records, TEST never inspected)
Beyond the train gazetteer: G1 vs M6 dNLL +0.0059 [-0.001,+0.012] (TASTEset, all), +0.0025 [+0.0001,+0.0056] (RecipeDB3, all); G2 vs M6 dNLL +0.0021 / +0.0008, no AURC or unseen gain (unseen NLL +0.014 TASTEset, +0.0002 RecipeDB3; tail -0.016 / +0.008). Ledger exact coverage of unseen DEV spans is only 37.5% (TASTEset) / 4.1% (RecipeDB3). G1 alone helps TASTEset (-0.016, Holm-inconclusive) but that information is already in the train gazetteer. **G1, G2: REJECT** (external ledger adds no information beyond the train gazetteer; no false-positive harm measured beyond the small NLL worsening above).

## M7 rule agreement (quantity form, unit/process/ledger lexicon membership, cross-lexicon conflict, quantity-unit-food adjacency; no gold types or IDs)
REJECT on both datasets (dNLL ~0, vs C no gain; vs C worse AURC on RecipeDB3).

## Redundancy (descriptive; M1 already rejected)
TASTEset: M1+M6 vs M6 on all spans dNLL +0.0003 (no gain); FOOD-only -0.0092 [-0.020,-0.0004]. RecipeDB3: M1+M6 vs M6 +0.0009 (no gain), worse than P0 on FOOD (+0.0094). Smallest set preserving the gain: **M6 alone**.

## BGE vs E5 by downstream usefulness
| | BGE | E5 |
|---|---|---|
| TASTEset M1 dNLL (FOOD) | -0.0196 | -0.0198 |
| TASTEset M2 dNLL (FOOD) | -0.0155 | -0.0152 |
| RecipeDB3 M1 / M2 dNLL | +0.0099 / +0.0060 | +0.0110 / +0.0064 |
| NIL separation AUROC (dev_alias vs unseen_concept) | 0.713 | 0.715 |
| unseen_alias vs unseen_concept AUROC | 0.648 | 0.644 |
| training time (4 ep) / size | ~0.16 min / 335M | ~0.14 min / 335M |
No downstream difference, so the **Pareto tie stands** (BGE provisional).
**Evaluation bug found:** the linker `dev` "NIL" set (252 queries) consists of surfaces that are exact members of the gallery (cosine 1.0) -- dev-concept canonical names kept in `full_gallery_seen_concepts` -- so the NIL threshold tau selected on it, and the earlier "NIL precision/recall" figures, are not valid. Retrieval metrics (Acc@1/R@5/MRR), the calibration features (raw cosines) and the unseen_concept AUROC above are unaffected. Linker data v2 with true held-out dev NIL concepts is needed before any NIL/NOVEL threshold is trusted (no new training branch started).

## Linker validation (OOF artefact)
Linker trained on ledger surfaces only; one frozen linker scores all splits. Exact overlap with linker-train surfaces: TASTEset 0.472 train-OOF / 0.466 DEV; RecipeDB3 0.315 train-OOF / 0.300 DEV. Missing predictions: 0 (TASTEset), 4 of 21,123 train-FOOD spans (RecipeDB3, empty/odd surfaces after normalisation; neutral features). Top-K length 10.

## Metadata freeze (calibration use only; nothing enters the encoder yet)
- METADATA_PROMOTED = [M6 gazetteer agreement, all spans (calibration only; significant on TASTEset, neutral on RecipeDB3)]
- METADATA_REJECTED = [M1 (FOOD; reverses on RecipeDB3), M2 (FOOD; reverses), M3, M4, G1, G2, M7]
- METADATA_INCONCLUSIVE (left out of mainline) = [M5 frequency/tail]
- Per-label (class-conditional) confidence kept as a ranking aid for the router strata, not a semantic metadata block.
