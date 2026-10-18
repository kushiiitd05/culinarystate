# RQ16-03 evidence compatibility reranker — silver dev pilot (pre-registered 2026-10-18, before running)

**Claim (falsifiable):** on scientifically close hard negatives built from the evidence ledger, a structured
compatibility scorer (compat vector + categorical match types) separates the true evidence cell from hard
negatives with higher AUROC than a generic cross-encoder (bge-reranker-large), on food-cold and process-cold splits.

**Unit:** (templated query, evidence row) pair. **Population:** ACTIVE EVD rows with linked ingredient, process and
target (USDA R6, Bognár, Phenol-Explorer), English.
**Labels:** SILVER — positive = same (ingredient, process, target) cell as the query; negatives typed per §241.4:
`WRONG_PROCESS` (same food+target, other process), `WRONG_TARGET` (same food+process, other target),
`RELATED_FOOD` (same process+target, parent/child food), `EASY` (random row). Headline RQ16-03 needs human-labelled
pairs (SSOT §247.3) -> this pilot cannot promote; it decides whether labelling effort is worth spending.
**Systems:** S0 BM25 · S1 generic cross-encoder · S2 structured compatibility score (no training) ·
S3 logistic regression on [S2 axes, S1 score] trained on the train fold only.
**Splits:** food-cold (GroupKFold by ingredient, 5 folds) and process-cold (by process); seed 7.
**Metrics:** AUROC overall and per negative type; Recall@1 among {positive + its negatives}; grouped bootstrap CI.
**Leakage audit:** query text is templated from the positive's fields, so lexical systems get an advantage on
WRONG_TARGET; reported per type, not hidden.
**Success gate:** S2 or S3 AUROC on WRONG_PROCESS ∪ RELATED_FOOD exceeds S1 with CI excluding 0 on both splits.
**Null gate:** CIs overlap -> keep the current structured retriever, no new model.
**Negative gate:** S1 beats S2/S3 -> MODIFY (structured axes miss something the CE sees; inspect errors).
**Not justified by this pilot:** any claim on free-text user questions or on human-judged relevance.

## Run record (added after running, 2026-10-18; claim and gates above unchanged)
**Command:** `tools/build_rq1603_pairs.py --n 800` (seed 7) → `tools/score_pairs_ce.py --model BAAI/bge-reranker-{large,base}`
on the A100 → `tools/eval_rq1603.py` → `reports/del4/rq1603_pilot_v1.md`.
**Data:** 800 queries; negatives WRONG_PROCESS 751, WRONG_TARGET 768, RELATED_FOOD 315, EASY 800. Splits for S3:
food-cold and process-cold GroupKFold (5 folds); S0/S1/S2 are unsupervised (split-independent).
**Added system (§257B predicted-upstream, not in the pre-registration):** S2p = S2 with slots parsed from the
question by the runtime parser. It exposed a parser defect (target slot accuracy 0.205), fixed by a closed-world
ledger target lexicon (`decision/targets.py`, accuracy 0.994 on these templated questions — optimistic, since the
template contains the ledger name).

| system | HARD AUROC | Δ HARD vs CE-large | Recall@1 |
|---|---|---|---|
| S1 CE bge-reranker-large | 0.924 [0.906, 0.940] | — | 0.905 |
| S2 structured, oracle slots | 0.995 [0.992, 0.998] | +0.071 [+0.055, +0.090] | 0.979 |
| S2p structured, predicted slots | 0.975 [0.968, 0.982] | +0.051 [+0.035, +0.070] | 0.926 |
| S3 struct + CE (food-cold / process-cold) | 0.996 | +0.072 [+0.057, +0.089] | 0.995 |

**Verdict (silver):** success gate met on both splits — structured compatibility beats the generic cross-encoder on
hard negatives, also with predicted slots. Largely expected by construction (labels are cell identity, which the
structured axes encode); S3's extra gain over S2 is Recall@1 only (+0.016). **Decision:** KEEP structured scorer as
the RQ16-03 method; no learned reranker promoted (S3 needs CE on GPU at query time for +0.016 R@1); headline result
NEED_DATA (human-labelled pairs, free-text questions).
