# Do linker-derived signals add information beyond span confidence? (TASTEset, DEV only)

Baseline P0 = calibrated logit(span confidence) of DeBERTa-base+CRF (logreg+isotonic fit on 5-fold OOF train spans, 8225 spans; evaluated on DEV, 2067 spans / 106 docs, of which 622 FOOD spans, 247 unseen-surface spans). Each feature block is added to P0 ALONE. TEST and CALIBRATION not read. NLL clipped at 1e-3 (isotonic emits 0/1).
Script: `tools/e2_linker_calibration.py`; raw: `_e2_linker_tasteset*.json`. Linker = BGE-large bi-encoder (3 seeds; M1-M3 identical decisions across seeds).

## OOF linker artefact validation
- The linker is trained on **ledger surfaces only** (BBC mentions/OFF/Wikibooks; no benchmark document), so no benchmark span is a linker training example. One frozen linker scores every split. Fold-leakage therefore checked empirically: exact overlap of span surface with linker train surfaces is 0.472 (OOF-train) vs 0.466 (DEV), shift 0.006; top-1 cosine quantiles (5/25/50/75/95%) 0.650/0.826/1.0/1.0/1.0 vs 0.651/0.815/1.0/1.0/1.0.
- Missing predictions 0/2476 (train FOOD) and 0/622 (DEV); top-K length 10 everywhere. NIL-like (top-1 < 0.8): 19.3% train vs 22.2% DEV (DEV has more unseen mentions, expected). Top-1 cosine is higher when the span is correct (0.92 vs 0.83 train; 0.92 vs 0.80 DEV).
- Concept overlap: linker gallery = seen ledger concepts only; held-out ledger concepts behave as NIL.
- Caveat: a concept-grouped K-fold of the linker was NOT run (not needed for leakage as above); RecipeDB3 not exported yet.

## Results vs P0 (all DEV spans; paired document bootstrap, Holm over 6)
| Block | dNLL [95% CI] | dAURC | dECE | dPrec@90 | unseen dNLL | decision |
|---|---|---|---|---|---|---|
| M1 linker top-1 conf | -0.0035 [-0.0084,+0.0008] | -0.00007 | -0.0013 | +0.0016 | -0.031 | see FOOD follow-up |
| M2 margin/entropy | -0.0028 [-0.0067,+0.0012] | -0.00024 | -0.0018 | +0.0016 | -0.026 | see FOOD follow-up |
| M3 ING category | +0.0026 [-0.0018,+0.0072] | -0.00021 | -0.0028 | +0.0010 | +0.001 | REJECT |
| M4 process family | +0.0001 [-0.0018,+0.0028] | +0.00033 | -0.0016 | 0.0000 | +0.002 | REJECT |
| M5 frequency/tail | -0.0050 [-0.0143,+0.0038] | +0.00063 | -0.0063 | +0.0032 | -0.071 | INCONCLUSIVE |
| M6 gazetteer agreement | -0.0089 [-0.0173,-0.0031] | -0.00041 | -0.0033 | +0.0021 | -0.091 | **PROMOTE** (Holm p=0.004) |
Nuisance control C (label+length) is worse than P0 (NLL 0.1566 vs 0.1539), so gains are not label identity.

## Minimum follow-up for the INCONCLUSIVE linker blocks: restrict to FOOD spans (where the features are defined; 622 dev spans)
P0 NLL 0.2609 / ECE 0.0523. M1 dNLL -0.0199 [-0.0382,-0.0060] (Holm p=0.008 <= 0.0083, dAURC -0.0011 [-0.010,+0.007], dECE -0.0080): **PROMOTE as calibration feature, FOOD scope**. M2 dNLL -0.0154 [-0.0284,-0.0035], Holm p=0.012: fails Holm -> **INCONCLUSIVE**. M5 CI spans 0 -> INCONCLUSIVE. Risk-coverage (AURC) gain is not significant for any linker block: they improve probability quality, not ranking.

## Linker choice, BGE vs E5 (dev_alias, n=61, seed-averaged per query, paired query bootstrap)
vs e5 lr1e-5/4ep: Acc@1 +0.033 [-0.038,+0.104], R@5 +0.000, MRR +0.022 [-0.023,+0.073] (BGE-only right 4, E5-only 3). vs e5 lr2e-5/6ep: Acc@1 +0.055 [-0.027,+0.137]. Not distinguishable -> **retain both as a linker Pareto set; BGE provisional** (unseen_alias not used for the choice).
