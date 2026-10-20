# S119 execution plan — CulinaryNER-KF ladder (master prompt Parts V–XV + Aprilab strategy)

Status of hypothesis: RESEARCH HYPOTHESIS. No "SOTA" claim before H6. Benchmark v1 is frozen (`benchmark/ner/`); any change = a dated amendment logged BEFORE the first candidate run.

## 1. Where each piece runs (so nothing slows down)
| Where | Does | Never does |
|---|---|---|
| **A100** (GPU0 ~28 GB free, GPU1 ~16 GB free; shared with other users; bf16, <=2 jobs/GPU) | all encoder / CRF / fusion / span-head / contrastive-linker / GLiNER training and inference | feature tables, calibrators, statistics, reports |
| **Mac M2 (8 GB, CPU, `nice -n 10`, <3 GB RAM)** | candidate spans, alias/gazetteer features, 5-fold cross-fitting, calibrator (logreg/GBM + isotonic), conformal router, bootstrap + Holm statistics, Pareto decision, reports, tests, linker data prep, TF-IDF linker baseline | any transformer training (no `transformers` locally, by design) |
Data flow: Mac builds feature tables → `scp` to A100; A100 writes predictions/marginals JSON (small) → `scp` to Mac; Mac calibrates and decides. Raw recipe text never leaves local/A100 working dirs.

## 2. Ladder and rung ownership
| Rung | Prompt part | GPU job | Mac job | Gate (frozen rule: delta micro-F1 >= 0.003, paired grouped bootstrap CI excludes 0, Holm; >=4/5 seeds) |
|---|---|---|---|---|
| E0 baselines | V, VI | BERT, RoBERTa, DeBERTa-base, DeBERTa-v3-large, each +/- CRF (+ModernBERT, GLiNER-FT if approved), 5 seeds TASTEset; 1 seed RecipeDB3 for elimination, 5 seeds for contenders | stats, SPAN_CHAMPION/PARETO table | champion or Pareto set |
| E1 | VIII first test | CRF forward-backward span marginals, save | temperature scaling, span ECE | ECE falls |
| E2 | VIII | none | cross-fitted calibrator on marginal + span metadata; AURC, precision@coverage | AURC down, CI separates |
| Part VII knowledge | VII | K0-K3 knowledge-context prefix runs | build train-only knowledge contexts | tail/unseen up, no head loss |
| E3/E4 | IX | concat then gated fusion (+metadata dropout 0.3, gate bias init ~1, warm start from E0) | candidate-span feature tables, B/I projection arrays | unseen F1 >= E0, seen >= E3; alias-swap + coverage 25/50/100% stress tests |
| Part X | X | CRF + span-boundary head (aux loss only; CRF decodes) | boundary-error analysis | exact boundaries improve consistently |
| E5 | — | kNN datastore (prior null; one cheap test) | — | tail gain, no head loss |
| Part XI/XII | XI, XII | contrastive linker (e5-large, hard negatives), then optional joint objective | positive/negative pair building, TF-IDF baseline, top-K tables | Acc@1/Recall@5/NIL beat e5 0.607 on family-grouped split |
| E6 | XIII | GLiNER fallback inference on low-confidence spans | conformal router: ACCEPT/REVIEW/NOVEL/REJECT, eps = 0.02, thresholds on CALIBRATION by stratum | accept-set error <= eps on test; review rate below E2 |
| Final | XIV, XV | — | ablation ladder B0-B9 report, Pareto champion | `semantic_pipeline_candidate.md` |

## 3. Order of work and what blocks what
1. (running) S118C: SIZE runs -> `recipedb3_matched_reproduction.md`.
2. Benchmark amendment A1 (before first candidate): mention-disjoint test subset; dataset-specific max_len (TASTEset 256, RecipeDB3 128); dev unseen-mention F1 logged as hard gate beside the frozen dev micro-F1 selection rule. Source-disjoint test: not possible on RecipeDB3 (no source field), recorded as UNKNOWN.
3. E0 TASTEset sweep (cheap, ~1.5 h on 2 GPUs) -> elimination on RecipeDB3 (1 seed each) -> 5 seeds for contenders only.
4. While E0 runs: Mac builds candidate spans + cross-fit features + calibrator + router + statistics modules, all unit-tested (Part XX).
5. E1/E2 immediately after E0 predictions exist; fusion only if E2 shows metadata carries signal (Part IX condition).

## 4. Precautions against slowdown
- One queue runner, max 2 jobs per GPU, bf16, best-state kept in CPU RAM (no checkpoint files), predictions as small JSON.
- Never launch large (v3-large) 5-seed RecipeDB3 sets blind: elimination first.
- Mac jobs capped at ~3 GB, run niced; no model downloads locally.
- Other users share the A100: check `nvidia-smi` before each wave; back off if free memory < 12 GB.

## 5. Decisions / permissions still needed from Kush
| Item | Why | Default if no answer |
|---|---|---|
| Upgrade `transformers` on the server (4.45 -> >=4.48) for ModernBERT (M7/M8) | ModernBERT unsupported in 4.45 | skip M7/M8, note as not run |
| `pip install gliner` on the server and a GLiNER-FT baseline | E0 asks for it | zero-shot GLiNER only (already measured: weak exact) |
| FoodBase download for cross-corpus transfer | Aprilab evaluation protocol | not run; RecipeDB3 + TASTEset only |
| Checkpoint rule: keep dev exact micro-F1 (frozen) vs unseen-mention F1 | plan prefers unseen-mention | frozen rule + unseen-mention F1 as hard gate |

## 6. Test requirements (Part XX), added as each module lands
family leakage, exact duplicates, alias/concept leakage, train-only + out-of-fold statistics, missing metadata, normalisation, CRF decode legality, span-head offsets, NIL behaviour, hard negatives, benchmark hashes, dev-only selection, no secrets, no committed Food.com text.
