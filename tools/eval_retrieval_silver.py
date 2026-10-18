#!/usr/bin/env python3
"""DEL-4 silver retrieval comparison: BM25 vs dense vs hybrid vs structured retriever (dev only).

  /opt/anaconda3/bin/python tools/eval_retrieval_silver.py
Inputs from tools/export_retrieval_set.py and tools/embed_texts.py. Systems:
  R0 BM25 · R1 dense (each embedded model) · R2 BM25+dense reciprocal-rank fusion (k=60)
  R3 EvidenceRetriever with oracle slots (process id + target from the query record) · R4 R3 + best dense
  R5 cross-encoder reranking of the R2 top-50 (tools/rerank_silver.py outputs, if present)
Metrics: Hit@5/10, MRR@10, nDCG@10 (binary relevance at cell level); CI = bootstrap over queries.
Writes reports/del4/retrieval_silver_v1.md/json. Silver, templated questions: a dev signal for which rung earns its
place (plan AI8/AI9), not a benchmark result.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.compatibility import Query  # noqa: E402
from culinarystate.retrieval.retriever import EvidenceRetriever  # noqa: E402
from culinarystate.scoring.metrics import grouped_bootstrap  # noqa: E402

RET, EMB, K = ROOT / "data" / "interim" / "retrieval", ROOT / "data" / "interim" / "embeddings", 10


def scores(ranked: list[str], rel: set) -> dict:
    hits = [i for i, x in enumerate(ranked[:K]) if x in rel]
    dcg = sum(1 / math.log2(i + 2) for i in hits)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(len(rel), K)))
    return {"hit@5": float(any(i < 5 for i in hits)), "hit@10": float(bool(hits)),
            "mrr@10": 1 / (hits[0] + 1) if hits else 0.0, "ndcg@10": dcg / idcg if idcg else 0.0}


def rrf(*rankings: list[str], k: int = 60) -> list[str]:
    s: dict = {}
    for r in rankings:
        for i, x in enumerate(r):
            s[x] = s.get(x, 0.0) + 1 / (k + i + 1)
    return sorted(s, key=lambda x: -s[x])


def summarise(per_q: list[dict]) -> dict:
    out = {}
    for m in ("hit@5", "hit@10", "mrr@10", "ndcg@10"):
        ci = grouped_bootstrap({i: [r[m]] for i, r in enumerate(per_q)}, lambda xs: sum(xs) / len(xs), n_boot=1000)
        out[m] = {"mean": ci["estimate"], "low": ci["low"], "high": ci["high"]}
    return out


def main() -> None:
    st = LedgerStore()
    cond = {c["id"]: c for c in st.all_latest("COND")}
    family = {p["id"]: p["family"] for p in st.all_latest("PROC")}
    passages = [json.loads(l) for l in (RET / "evd_texts.jsonl").open()]
    queries = [json.loads(l) for l in (RET / "silver_queries.jsonl").open()]
    ids = [p["id"] for p in passages]
    by_id = {e["id"]: e for e in st.all_latest("EVD")}
    retr = EvidenceRetriever([by_id[i] for i in ids], cond, family)
    assert [e["id"] for e in retr.evd] == ids, "retriever row order must match exported passages"
    bm25_idx = {q["qid"]: [i for i, _ in retr.bm25.top(q["question"], 100)] for q in queries}
    (RET / "bm25_top100.json").write_text(json.dumps(bm25_idx))           # first stage for tools/rerank_silver.py
    runs: dict[str, list[list[str]]] = {"R0 BM25": [[ids[i] for i in bm25_idx[q["qid"]]] for q in queries]}
    dense = {}
    for d in sorted(EMB.glob("*/meta.json")):
        name = json.loads(d.read_text())["model"]
        P, Q = np.load(d.parent / "passages.npy"), np.load(d.parent / "queries.npy")
        top = np.argsort(-(Q @ P.T), axis=1)[:, :100]
        dense[name] = (Q @ P.T)
        runs[f"R1 dense {name}"] = [[ids[i] for i in row] for row in top]
        runs[f"R2 RRF BM25+{name}"] = [rrf(a, b) for a, b in zip(runs["R0 BM25"], runs[f"R1 dense {name}"])]
    struct = []
    for q in queries:
        hits = retr.search(q["question"], Query(process_id=q["process_id"], process_family=family.get(q["process_id"]),
                                                target=q["target"]), k=K)
        struct.append([h.evd_id for h in hits])
    runs["R3 structured (oracle slots)"] = struct
    for f in sorted(RET.glob("rerank_*.json")):                         # R5 cross-encoder over RRF top-50
        rr = json.loads(f.read_text())
        runs[f"R5 rerank {f.stem.removeprefix('rerank_').replace('__', '/')}"] = [rr[q["qid"]] for q in queries]
    results = {name: [scores(r, set(q["relevant"])) for r, q in zip(rs, queries)] for name, rs in runs.items()}
    best = max((n for n in results if n.startswith("R1")), key=lambda n: summarise(results[n])["mrr@10"]["mean"],
               default=None)
    if best:
        sims = dense[best.removeprefix("R1 dense ")]
        r4 = []
        for qi, q in enumerate(queries):
            hits = retr.search(q["question"], Query(process_id=q["process_id"], process_family=family.get(q["process_id"]),
                                                    target=q["target"]), k=K,
                               dense_scores={int(i): float(sims[qi, i]) for i in np.argsort(-sims[qi])[:300]})
            r4.append([h.evd_id for h in hits])
        results[f"R4 structured + {best.removeprefix('R1 dense ')}"] = [scores(r, set(q["relevant"])) for r, q in zip(r4, queries)]
    summary = {n: summarise(v) for n, v in results.items()}
    fams = sorted({q["family"] for q in queries})
    by_family = {n: {f: round(float(np.mean([r["mrr@10"] for r, q in zip(v, queries) if q["family"] == f])), 4)
                     for f in fams} for n, v in results.items()}
    out = ROOT / "reports" / "del4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "retrieval_silver_v1.json").write_text(json.dumps({"summary": summary, "mrr_by_family": by_family,
                                                              "n_queries": len(queries)}, indent=1))
    lines = ["# DEL-4 silver retrieval comparison v1 (dev only)", "",
             f"{len(queries)} templated questions over {len(ids):,} evidence rows; relevance = same (matrix, process, "
             "target) cell. Silver: ranks rungs, not a benchmark result. CI = bootstrap over queries.", "",
             "| system | Hit@5 | Hit@10 | MRR@10 | nDCG@10 | " + " | ".join(f"MRR {f}" for f in fams) + " |",
             "|---|---|---|---|---|" + "---|" * len(fams)]
    for n, s in summary.items():
        cell = lambda m: f"{s[m]['mean']} [{s[m]['low']}–{s[m]['high']}]"  # noqa: E731
        lines.append(f"| {n} | {cell('hit@5')} | {cell('hit@10')} | {cell('mrr@10')} | {cell('ndcg@10')} | "
                     + " | ".join(str(by_family[n][f]) for f in fams) + " |")
    (out / "retrieval_silver_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
