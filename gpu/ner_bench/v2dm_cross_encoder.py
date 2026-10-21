#!/usr/bin/env python3
"""Conventional cross-encoder on the SAME candidate lists as the decision-model tasks (python 3.8). Zero-shot BAAI/bge-reranker-large scores (mention, candidate text) for the first K candidates.
  python v2dm_cross_encoder.py tasks.jsonl out.jsonl K"""
import json
import sys

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tasks, out, K = sys.argv[1], sys.argv[2], int(sys.argv[3])
tok = AutoTokenizer.from_pretrained("BAAI/bge-reranker-large")
m = AutoModelForSequenceClassification.from_pretrained("BAAI/bge-reranker-large").cuda().eval()
with open(out, "w") as f:
    for l in open(tasks):
        r = json.loads(l)
        c = r["cands"][:K]
        pairs = [(r["mention"], x["name"] + (" (" + ", ".join(x["aliases"]) + ")" if x["aliases"] else "")) for x in c]
        b = tok([p[0] for p in pairs], [p[1] for p in pairs], padding=True, truncation=True, max_length=64, return_tensors="pt").to("cuda")
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            s = m(**b).logits.squeeze(-1).float().cpu().tolist()
        f.write(json.dumps({"id": r["id"], "scores": s}) + "\n")
