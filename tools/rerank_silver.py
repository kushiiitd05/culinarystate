#!/usr/bin/env python3
"""R5 cross-encoder reranking (SSOT §241.1; RQ16-03 generic cross-encoder baseline) over a first-stage run.

  /opt/anaconda3/envs/recsys_env/bin/python tools/rerank_silver.py --model BAAI/bge-reranker-base
First stage = reciprocal-rank fusion of BM25 (top-100 lists exported by eval_retrieval_silver.py) and a dense model; the top 50 are rescored by the cross-encoder. Writes data/interim/retrieval/rerank_<model>.json
({qid: [evd ids]}) for tools/eval_retrieval_silver.py.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
RET, EMB = ROOT / "data" / "interim" / "retrieval", ROOT / "data" / "interim" / "embeddings"
TOP = 50


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="BAAI/bge-reranker-base")
    ap.add_argument("--dense", default="BAAI__bge-small-en-v1.5")
    ap.add_argument("--bs", type=int, default=64)
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    passages = [json.loads(l) for l in (RET / "evd_texts.jsonl").open()]
    queries = [json.loads(l) for l in (RET / "silver_queries.jsonl").open()]
    bm25 = json.loads((RET / "bm25_top100.json").read_text())
    P, Q = np.load(EMB / a.dense / "passages.npy"), np.load(EMB / a.dense / "queries.npy")
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForSequenceClassification.from_pretrained(a.model).to(dev).eval()
    out, t0 = {}, time.time()
    for qi, q in enumerate(queries):
        dense = np.argsort(-(Q[qi] @ P.T))[:100].tolist()
        fused: dict = {}
        for r in (bm25[q["qid"]], dense):
            for i, x in enumerate(r):
                fused[x] = fused.get(x, 0.0) + 1 / (61 + i)
        cand = sorted(fused, key=lambda x: -fused[x])[:TOP]
        with torch.no_grad():
            b = tok([q["question"]] * len(cand), [passages[i]["text"] for i in cand], padding=True, truncation=True,
                    max_length=192, return_tensors="pt").to(dev)
            s = model(**b).logits.view(-1).float().cpu().numpy()
        out[q["qid"]] = [passages[cand[j]]["id"] for j in np.argsort(-s)]
    name = a.model.replace("/", "__")
    (RET / f"rerank_{name}.json").write_text(json.dumps(out))
    print(a.model, dev, f"{len(queries)} queries x {TOP} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
