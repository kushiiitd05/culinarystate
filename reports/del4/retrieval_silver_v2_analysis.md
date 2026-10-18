# DEL-4 retrieval — analysis of silver v1 table with 6 dense models + 2 cross-encoders (2026-10-18)

Table and paired differences: `retrieval_silver_v1.md` (600 templated dev queries, 17,978 rows; silver, dev only).
Embeddings and reranking computed on the A100 (`gpu/`, mh-copilot venv read-only); evaluation on the Mac.

| question | result (MRR@10, paired Δ with 95% bootstrap CI) | decision |
|---|---|---|
| Better free-text embedding? (RQ16-02) | e5-large-v2 best of 6 (R1 0.700); RRF BM25+e5-large 0.762 vs bge-small RRF 0.704: **+0.057 [+0.035, +0.082]** | e5-large-v2 replaces bge-small as the free-text fallback model |
| Does a general cross-encoder help? (RQ16-03) | bge-reranker-large **−0.056 [−0.091, −0.017]**, base **−0.091 [−0.129, −0.049]** vs the RRF list they rerank | not promoted; negative result kept |
| Does dense add to the structured retriever? | R4 (structured + e5-large) vs R3: **+0.005 [−0.006, +0.015]** | not promoted; structured retriever stays primary, no dense blend at runtime |

Why the cross-encoders lose: relevance here is cell identity (same matrix × process × target). MS-MARCO-style
rerankers score topical similarity, so rows of the same food with another nutrient or process outrank the right cell.
This is the motivation for RQ16-03's compatibility reranker with scientific hard negatives (same food, wrong
process/target), which a general reranker never saw. R3 with oracle slots (0.856) bounds what slot parsing buys;
predicted-slot end-to-end evaluation needs the benchmark (D-008).
