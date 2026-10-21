# CulinarySpanDecision-v1 -- protocol (written before any chooser is trained or scored)

## Question
Can a chooser over CRF top-K sequence/span alternatives recover part of the errors already present in the top-K distribution, without damaging correct 1-best spans? Separate hypothesis from CulinaryLinkDecision (closed, D3); link-selection models (Tev, Nimble, CD-L2) are not reused automatically. Not an LLM-first project.

## Existing evidence (TASTEset DEV, seed 1, 106 docs, 2,055 gold spans; `crf_topk_segmentation_diagnostic.md`)
1-best exact micro-F1 0.9403; per-document best-of-5 oracle 0.9558 (+1.55 pp); 1-best span recall 94.3%, top-5 96.0%; 117 missed by 1-best, 35 (30%) present in an alternative path, 82 absent. Power warning: only ~35 DEV spans are recoverable, so DEV confidence intervals will be wide; a GO therefore also needs the TRAIN-OOF cross-validated estimate (below), not DEV alone.

## Data and leakage rules
- Decision examples come from **OOF** NER predictions (concept-/document-grouped K-fold over TRAIN); no example is built from a model trained on that example.
- TRAIN (chooser training), DEV (selection / GO-NO-GO), fresh final evaluation (later, only on GO) stay separate. **TASTEset TEST, RecipeDB3 TEST and the 850/441 link sets are not used.** v1 NER scripts/checkpoints are not edited (use `bench_train_v2.py`, `crf_nbest.py`).
- First step is an inventory of existing OOF/seed checkpoints and n-best availability before generating anything new.

## Examples
Per document: top-5 paths with CRF path score, normalised path probability, span marginals, path-to-path differences, affected spans, token/context representations, label sequences, boundary disagreements. Targets: (a) document-level: the alternative with best gold agreement (ties -> path 1); (b) span-local: competing candidate spans (boundary and label) -> correct one, or keep path 1.

## Systems (simple first)
S0 always path 1. S1 normalised CRF path probability / best-by-score. S2 rule or feature reranker (path score, marginals, span length, boundary and label confidence). S3 small MLP / gradient model on the same features. **CSD-T (text-aware small chooser) is trained only if S2/S3 leave useful headroom on DEV.** Tev as teacher only after showing signal on TRAIN-OOF (bounded A-E segmentation question); no assumption of usefulness.

## Metrics
Exact micro-F1; macro-F1; boundary-error and label-error counts; **recovered** (previously wrong, now right), **damaged** (previously right, now wrong), net recovered, **damage/recovery ratio**; top-K oracle headroom; **recovery efficiency = (F1_chooser - F1_path1) / (F1_oracle - F1_path1)**; latency; memory. Error taxonomy: A = gold absent from top-K (unrecoverable); B = gold present but chooser wrong (decision error). Paired bootstrap over documents vs S0.

## Pre-registered classes (fixed now)
- **CSD-A:** paired lower bound of F1 gain vs S0 > 0 on DEV **and** on TRAIN-OOF CV; recovery efficiency >= 0.30; damage/recovery <= 0.33.
- **CSD-B:** positive point gain but CI includes 0, or efficiency 0.10-0.30, or damage/recovery 0.33-0.67.
- **CSD-C:** otherwise (no DEV gain, efficiency < 0.10, or damage/recovery > 0.67). On CSD-C stop: no sweep, no human-data collection.

## First experiment only
Answer, on existing TRAIN-OOF + DEV: (1) how many decisions differ among top-5 paths; (2) how many have a gold-recoverable alternative; (3) which labels/boundaries account for them; (4) does a numeric reranker beat path 1; (5) does a small text-aware model add anything beyond numeric CRF information. No new human dataset before a GO.

## Execution order
decision record -> this protocol (commit) -> inventory OOF -> build top-5 OOF dataset -> quantify oracle/recoverable by label and error type -> S0/S1 -> S2/S3 -> (only if headroom) CSD-T -> DEV evaluation -> GO/NO-GO -> (only on GO) design a new sealed final evaluation.
