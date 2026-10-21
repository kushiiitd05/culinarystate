# CulinarySpanDecision-v1 -- S0-S3 numeric choosers on TASTEset (gate applied exactly as pre-registered)

Code `tools/csd_choose.py`; numbers `_csd_s0_s3.json`. Data: 5-fold TRAIN-OOF top-5 CRF paths (424 docs, 8,047 gold spans) and DEV (106 docs, 2,055 spans; full-TRAIN model). TEST untouched; no text features; no human data; RecipeDB3 not run.
Decision unit: cluster of overlapping spans across the 5 paths (884 of 8,267 OOF clusters have more than one option); options = each path restricted to the cluster; chooser picks one option per cluster, default = path-1 option. Features: path-probability mass of the option (normalised CRF path scores, aggregated over paths), mass ratio to path 1, best-path rank and score gap, span count/length/label composition, boundary-identity with path 1, cluster entropy. Headline system selected by TRAIN-OOF CV only.
Oracles: top-5 per-document 0.9474 (OOF) / 0.9558 (DEV); cluster-level 0.9490 / 0.9582.

| | BASE PATH F1 | CHOOSER F1 | DELTA vs PATH1 [95% CI] | RECOVERED | DAMAGED | NET | DAMAGE/RECOVERY | EFFICIENCY (vs doc oracle) | CLASS |
|---|---|---|---|---|---|---|---|---|---|
| OOF-CV S0 | 0.9308 | 0.9308 | 0 | 0 | 0 | 0 | - | 0 | - |
| OOF-CV S1 (mass) | 0.9308 | 0.9311 | +0.0003 [0.0000, 0.0007] | 3 | 0 | +3 | 0.00 | 0.018 | C |
| OOF-CV S2 (rule, grid by CV) | 0.9308 | 0.9309 | +0.0001 [-0.0005, 0.0006] | 3 | 1 | +2 | 0.33 | 0.006 | C |
| OOF-CV S3 (GBM) | 0.9308 | 0.9306 | -0.0002 [-0.0014, 0.0010] | 3 | 28 | -25 | 9.33 | -0.012 | C |
| DEV S0 | 0.9403 | 0.9403 | 0 | 0 | 0 | 0 | - | 0 | - |
| DEV S1 | 0.9403 | 0.9403 | 0 | 0 | 0 | 0 | - | 0 | C |
| DEV S2 | 0.9403 | 0.9403 | 0 | 0 | 0 | 0 | - | 0 | C |
| DEV S3 | 0.9403 | 0.9411 | +0.0008 [-0.0006, +0.0025] | 0 | 3 | -3 | - | 0.052 | C |

S1 at path level is identical to S0 by construction (path 1 has the highest score), which is why S1 is defined at cluster level.

**Recovered / damaged breakdown (OOF-CV).** S1: recovered FOOD 2, other 1 (same-label boundary 2, boundary+label 1); damaged 0. S2: same recoveries; damaged 1 (FOOD, same-label boundary). S3: recovered FOOD 3 (same-label boundary 3); damaged FOOD 12, PHYSICAL_QUALITY 6, PROCESS 1, other 9 (fully missed span 15, same-label boundary 10, boundary+label 3). DEV: S1/S2 change nothing; S3 recovers 0 and damages 3 (FOOD 1, PHYSICAL_QUALITY 1, other 1). Recovered/damaged in the PHYSICAL_QUALITY and PROCESS classes: 0 recovered by any system.

## Gate
Headline system (best OOF-CV delta): S1. OOF class C, DEV class C -> **RESULT: CSD-C**. The numeric chooser cannot turn the 131 recoverable spans (of 8,047) into gains: the best system recovers 3 of them with efficiency 0.018 (OOF) and 0 on DEV; the one learned model that moves many decisions (S3) is net-harmful (28 damaged vs 3 recovered). Path-probability mass and CRF-score features do not identify the alternatives that are correct: those alternatives sit at low path probability, so confidence-based selection leaves path 1 unchanged, and a learned chooser on the same numbers adds noise.

## Reading and limits
- Stop per protocol and the user's rule: **span lane stopped at CSD-C; RecipeDB3 OOF, text-aware chooser, Tev teacher, and human annotation are not started.** No sweep or retuning.
- Caveats that the CSD-C label does not remove: only TASTEset seed 1; only 131 recoverable OOF spans; alternative-span CRF marginals were not available (features are path-mass approximations); a text-aware chooser was not tested (the protocol allowed it only if S2/S3 left meaningful recoverable headroom, and the lane rule stops at CSD-C). Unrecovered ceiling remains +1.7 pp (cluster oracle), so this result says "numeric features cannot reach it", not "no signal exists".
