#!/usr/bin/env python3
"""S127 latency / memory of the surviving model components (random token ids at realistic lengths; weights do not affect latency). python 3.8 safe.
  python latency_bench.py   -> JSON on stdout. Medians over repeats; the A100 is shared, so treat as indicative."""
import json
import time

import numpy as np
import torch
from transformers import AutoModel

from crf import CRF, marginals

dev = "cuda"


def timeit(fn, n=30, warm=5):
    for _ in range(warm):
        fn()
    torch.cuda.synchronize()
    ts = []
    for _ in range(n):
        t = time.perf_counter()
        fn()
        torch.cuda.synchronize()
        ts.append((time.perf_counter() - t) * 1000)
    return float(np.median(ts))


out = {"gpu": torch.cuda.get_device_name(0)}
for name, L in (("tasteset_len48", 48), ("recipedb3_len24", 24)):
    for mname in ("microsoft/deberta-base", "microsoft/deberta-v3-large"):
        m = AutoModel.from_pretrained(mname).to(dev).eval()
        crf = CRF(19).to(dev).eval()
        head = torch.nn.Linear(m.config.hidden_size, 19).to(dev)
        torch.cuda.reset_peak_memory_stats()
        r = {}
        for bs in (1, 32):
            ids = torch.randint(1000, 20000, (bs, L), device=dev)
            att = torch.ones_like(ids)
            def enc():
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                    return m(input_ids=ids, attention_mask=att).last_hidden_state
            def full():
                with torch.no_grad():
                    h = enc()
                    e = head(h.float())
                    return crf.decode(e, att.bool())
            def marg():
                with torch.no_grad():
                    h = enc()
                    e = head(h.float()).float()
                    return [marginals(crf, e[i]) for i in range(e.shape[0])]       # per-document forward-backward
            r[f"bs{bs}"] = {"encoder_ms": timeit(enc), "encoder+crf_decode_ms": timeit(full), "encoder+crf_decode+marginals_ms": timeit(lambda: (full(), marg()))}
        r["peak_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 2)
        out[f"{name}|{mname.split('/')[-1]}"] = r
        del m
        torch.cuda.empty_cache()
# linker: embed 256 queries and score vs 2k gallery
for mname in ("BAAI/bge-large-en-v1.5", "intfloat/e5-large-v2"):
    m = AutoModel.from_pretrained(mname).to(dev).eval()
    ids = torch.randint(1000, 20000, (256, 6), device=dev)
    G = torch.nn.functional.normalize(torch.randn(2031, m.config.hidden_size, device=dev), dim=-1)
    torch.cuda.reset_peak_memory_stats()
    def link(bs):
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            h = m(input_ids=ids[:bs], attention_mask=torch.ones_like(ids[:bs])).last_hidden_state[:, 0].float()
        return torch.topk(torch.nn.functional.normalize(h, dim=-1) @ G.T, 10, dim=1)
    out["linker|" + mname.split("/")[-1]] = {"bs1_ms": timeit(lambda: link(1)), "bs256_ms": timeit(lambda: link(256)), "peak_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2)}
    del m
    torch.cuda.empty_cache()
print(json.dumps(out, indent=1))
