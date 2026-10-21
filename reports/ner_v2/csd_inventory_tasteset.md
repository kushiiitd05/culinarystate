# CulinarySpanDecision-v1 -- inventory (TASTEset; before any chooser; no TEST)

Code: `gpu/ner_bench/bench_train_v2.py` (+`--nbest-parts`), `gpu/ner_bench/csd_inventory.py`; numbers `_csd_inventory_tasteset.json`.

- **Checkpoints/seeds:** only seed 1 (DeBERTa-base+CRF). v1 OOF runs stored 1-best + confidences only (no OOF checkpoints, no n-best), so the 5 TRAIN folds were retrained with the v1 recipe and `--nbest 5 --nbest-parts oof,dev --no-test` (~3 min each). Full-TRAIN seed-1 DEV model from the earlier diagnostic is used for DEV.
- **Deterministic reproduction:** path 1 equals the stored v1 OOF 1-best on **424/424** OOF docs; DEV path-1 micro-F1 0.9403 reproduces the v1 DEV value.
- **TRAIN-OOF size:** 424 docs, 8,047 gold spans (5 concept-agnostic doc folds, same permutation as v1). DEV: 106 docs, 2,055 spans.
- **Paths:** 5 distinct tag paths per doc. Docs whose paths 2-5 differ from path 1 (span-set): 424/424 OOF, 106/106 DEV (differences per doc: mostly 3-4 of 4 alternatives).
- **Headroom (OOF):** path-1 micro-F1 0.9308; top-5 per-doc oracle 0.9474 (**+1.66 pp**). 474 gold spans missed by path 1; **131 (27.6%)** present in the top-5 union (unrecoverable 343). DEV: 117 missed, 35 recoverable (29.9%), oracle 0.9558 (+1.55 pp).
- **Recoverable by label (OOF):** FOOD 58, PHYSICAL_QUALITY 25, PROCESS 16, COLOR 8, QUANTITY 7, UNIT 7, TASTE 5, PART 4, PURPOSE 1.
- **Recoverable by error type (OOF, of 131):** boundary same-label 72 (of 250 missed), label-only 34 (of 89), boundary diff-label 12 (of 69), missing 13 (of 66). Most recoverable cases are boundary decisions, not label decisions.
- **Leakage status:** OOF paths come from fold models that never saw those docs; DEV from the full-TRAIN model; TEST was not decoded (`--no-test`, nbest parts limited to dev/oof/calibration); calibration unused; no link sets used. Caveat: fold models (80% of TRAIN) are slightly weaker than the full model (OOF path-1 F1 0.931 vs DEV 0.940), so chooser features trained on OOF paths see a mild distribution shift at DEV.
- **Not yet done:** RecipeDB3 (18,700 TRAIN docs; ~30 min/fold = ~2.5 h GPU), seeds 2-3.

**Inventory gate: PASS** (deterministic, leakage clean, headroom > the +0.3 pp kill rule). Next: build the OOF decision dataset, S0/S1, then S2/S3.
