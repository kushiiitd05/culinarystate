#!/usr/bin/env python3
"""Dense embeddings for DEL-4 retrieval (B1/B2 rungs). Runs in recsys_env (torch + transformers), CPU or GPU.

  /opt/anaconda3/envs/recsys_env/bin/python tools/embed_texts.py --model BAAI/bge-small-en-v1.5
Embeds data/interim/retrieval/evd_texts.jsonl (passages) and silver_queries.jsonl (queries) with the pooling and
prefixes from each model card; L2-normalised float32 .npy in data/interim/embeddings/<model>/ plus ids + meta.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
RET = ROOT / "data" / "interim" / "retrieval"
CARDS = {  # pooling, query prefix, passage prefix (model cards)
    "BAAI/bge-small-en-v1.5": ("cls", "Represent this sentence for searching relevant passages: ", ""),
    "BAAI/bge-base-en-v1.5": ("cls", "Represent this sentence for searching relevant passages: ", ""),
    "intfloat/e5-base-v2": ("mean", "query: ", "passage: "),
    "intfloat/e5-small-v2": ("mean", "query: ", "passage: "),
    "BAAI/bge-large-en-v1.5": ("cls", "Represent this sentence for searching relevant passages: ", ""),
    "intfloat/e5-large-v2": ("mean", "query: ", "passage: "),
    "thenlper/gte-large": ("mean", "", ""),
}


@torch.no_grad()
def embed(texts, tok, model, pooling, bs, dev):
    out = []
    for i in range(0, len(texts), bs):
        b = tok(texts[i:i + bs], padding=True, truncation=True, max_length=128, return_tensors="pt").to(dev)
        h = model(**b).last_hidden_state
        v = h[:, 0] if pooling == "cls" else (h * b["attention_mask"][..., None]).sum(1) / b["attention_mask"].sum(1, keepdim=True)
        out.append(torch.nn.functional.normalize(v, dim=-1).float().cpu().numpy())
    return np.concatenate(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(CARDS))
    ap.add_argument("--bs", type=int, default=128)
    a = ap.parse_args()
    pooling, qp, pp = CARDS[a.model]
    dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    tok, model = AutoTokenizer.from_pretrained(a.model), AutoModel.from_pretrained(a.model).to(dev).eval()
    passages = [json.loads(l) for l in (RET / "evd_texts.jsonl").open()]
    queries = [json.loads(l) for l in (RET / "silver_queries.jsonl").open()]
    out = ROOT / "data" / "interim" / "embeddings" / a.model.replace("/", "__")
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    np.save(out / "passages.npy", embed([pp + p["text"] for p in passages], tok, model, pooling, a.bs, dev))
    np.save(out / "queries.npy", embed([qp + q["question"] for q in queries], tok, model, pooling, a.bs, dev))
    (out / "ids.json").write_text(json.dumps({"passages": [p["id"] for p in passages], "queries": [q["qid"] for q in queries]}))
    (out / "meta.json").write_text(json.dumps({"model": a.model, "pooling": pooling, "device": dev,
                                               "seconds": round(time.time() - t0, 1), "torch": torch.__version__}))
    print(a.model, dev, f"{len(passages)} passages + {len(queries)} queries in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
