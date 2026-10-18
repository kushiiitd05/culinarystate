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
