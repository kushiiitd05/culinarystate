#!/usr/bin/env python3
"""Run a FROZEN CulinaryLinkDecision student checkpoint on a task file (mention + candidates). python link_student_predict.py CKPT TASKS OUT [K=10]"""
import json
import sys
import time

import numpy as np
import torch
from transformers import AutoTokenizer

import link_student as L

ck, tasks, out = sys.argv[1], sys.argv[2], sys.argv[3]
K = int(sys.argv[4]) if len(sys.argv) > 4 else 10
tok = AutoTokenizer.from_pretrained(L.ENC)
m = L.Student().cuda()
m.load_state_dict(torch.load(ck))
m.eval()
torch.cuda.reset_peak_memory_stats()
res = []
with torch.no_grad():
    for l in open(tasks):
        e = json.loads(l)
        t = time.time()
        p = L.logits(m, tok, [e], K)[0].softmax(-1).cpu().numpy()
        ms = 1000 * (time.time() - t)
        c = e["cands"][:K]
        res.append({"id": e["id"], "forced": c[int(np.argmax(p[:len(c)]))]["id"], "pnone": float(p[K]), "default": "NONE" if int(np.argmax(p)) == K else c[int(np.argmax(p))]["id"], "probs": [round(float(x), 5) for x in p], "ms": round(ms, 2)})
json.dump({"results": res, "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 3)}, open(out, "w"))
