#!/usr/bin/env python3
"""EXP-000006: generic cross-encoder scores for every (query, candidate) pair in data/interim/rq1603/pairs.jsonl.

  python tools/score_pairs_ce.py --model BAAI/bge-reranker-large      # A100 (mh-copilot venv, read-only)
Writes data/interim/rq1603/ce_<model>.json ({qid: {evd_id: logit}}).
"""
import argparse
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

D = Path(__file__).resolve().parents[1] / "data" / "interim" / "rq1603"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="BAAI/bge-reranker-large")
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForSequenceClassification.from_pretrained(a.model).to(dev).eval()
    out, t0 = {}, time.time()
    for line in (D / "pairs.jsonl").open():
        q = json.loads(line)
        with torch.no_grad():
            b = tok([q["question"]] * len(q["candidates"]), [c["text"] for c in q["candidates"]], padding=True,
                    truncation=True, max_length=192, return_tensors="pt").to(dev)
            s = model(**b).logits.view(-1).float().cpu().tolist()
        out[q["qid"]] = {c["evd_id"]: v for c, v in zip(q["candidates"], s)}
    (D / f"ce_{a.model.replace('/', '__')}.json").write_text(json.dumps(out))
    print(a.model, dev, f"{len(out)} queries in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
