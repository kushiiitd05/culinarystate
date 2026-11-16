#!/usr/bin/env python3
"""e5 vectors for the D5 S-block retrieval rungs (S179), for hosts where torch and the project venv differ.

Python 3.8-compatible and free of project imports. For every S row it embeds the question ("query: ") and each pre-cut
chunk "Step i: <text>" ("passage: ") with intfloat/e5-large-v2 at revision f169b11e..., mean pooling, L2 norm, the
same as ``tools/s179_d5_run_rungs.e5_embedder``. Output: {sha256(prefix + text): vector}, read by the runner with
``--embed-cache``. Contains no recipe text (keys are hashes).

    /usr/bin/python3 tools/s179_d5_embed_cache.py --bench benchmark/d5/d5_benchmark_v1_D085_S.csv \\
        --s-context <d5_S_context_v1.jsonl> --out <cache.json>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

E5, E5_REV = "intfloat/e5-large-v2", "f169b11e22de13617baa190a028a32f3493550b6"


def key(prefix: str, text: str) -> str:
    return hashlib.sha256((prefix + text).encode("utf-8")).hexdigest()


def texts_for(rows, steps):
    out = set()
    for r in rows:
        cut = int(r["cut_after_step"])
        out.add(("query: ", r["question"]))
        out |= {("passage: ", "Step %d: %s" % (i + 1, s)) for i, s in enumerate(steps[r["qid"]][:cut])}
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True)
    ap.add_argument("--s-context", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    import torch
    from transformers import AutoModel, AutoTokenizer
    with open(a.bench, encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if r["block"] in ("S1", "S2")]
    steps = {}
    for line in Path(a.s_context).read_text(encoding="utf-8").splitlines():
        if line:
            d = json.loads(line)
            steps[d["qid"]] = d["steps"]
    items = texts_for(rows, steps)
    tok = AutoTokenizer.from_pretrained(E5, revision=E5_REV)
    model = AutoModel.from_pretrained(E5, revision=E5_REV).to(a.device).eval()
    cache = {}
    with torch.no_grad():
        for i in range(0, len(items), 32):
            batch = items[i:i + 32]
            b = tok([p + t for p, t in batch], padding=True, truncation=True, max_length=512,
                    return_tensors="pt").to(a.device)
            h = model(**b).last_hidden_state
            v = (h * b["attention_mask"][..., None]).sum(1) / b["attention_mask"].sum(1, keepdim=True)
            for (p, t), vec in zip(batch, torch.nn.functional.normalize(v, dim=-1).float().cpu().tolist()):
                cache[key(p, t)] = vec
    Path(a.out).write_text(json.dumps({"model": E5, "revision": E5_REV, "vectors": cache}), encoding="utf-8")
    print(json.dumps({"out": a.out, "n": len(cache)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
