#!/usr/bin/env python3
"""Aggregate CD-L1 / CD-L2 student runs (DEV only): mean +- sd over seeds, paired comparison on dev_alias items (seed-averaged correctness)."""
import glob
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
R = defaultdict(list)
for f in sorted(glob.glob(str(ROOT / "reports/ner_v2/_stu/stu/*.json"))):
    d = json.load(open(f))
    R[(d["k"], d["lam"])].append(d)
T = {}
for l in open(ROOT / "features/v2dm/linker_tasks_k10.jsonl"):
    r = json.loads(l)
    if r["set"] == "dev_alias":
        T[r["id"]] = r
ids = sorted(T)
bge = np.array([float(T[i]["cands"][0]["id"] == T[i]["gold"]) for i in ids])
ms = lambda x: f"{np.mean(x):.3f}±{np.std(x):.3f}"
vec, rows = {}, []
for (k, lam), L in sorted(R.items()):
    vec[(k, lam)] = np.mean([[float(i in set(d["forced_correct_ids"])) for i in ids] for d in L], 0)
    rows.append((k, lam, len(L), ms([d["dev_alias_forced_acc"] for d in L]), ms([d["NIL_AUROC"] for d in L]), ms([d["NIL_AUPRC"] for d in L]), ms([d["false_NONE_on_aliases"] for d in L]), round(float(np.mean([d["latency_ms_median_gpu_bs1"] for d in L])), 1), L[0]["params_M"]))
    print(f"K={k} lam={lam} (seeds={len(L)}): forced acc {rows[-1][3]} | NIL AUROC {rows[-1][4]} AUPRC {rows[-1][5]} | false-NONE {rows[-1][6]} | {rows[-1][7]} ms | {rows[-1][8]}M params")
rng = random.Random(0)
def paired(a, b):
    d = a - b
    bs = [d[[rng.randrange(len(d)) for _ in d]].mean() for _ in range(5000)]
    return round(float(d.mean()), 3), [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)]
out = {"rows": rows, "paired": {}}
for (k, lam), v in vec.items():
    out["paired"][f"K={k} lam={lam} - BGE top-1"] = paired(v, bge)
for k in (5, 10):
    for lam in (0.3, 1.0):
        if (k, lam) in vec and (k, 0.0) in vec:
            out["paired"][f"K={k} CD-L2(lam={lam}) - CD-L1"] = paired(vec[(k, lam)], vec[(k, 0.0)])
if (10, 0.0) in vec and (5, 0.0) in vec:
    out["paired"]["CD-L1 K=10 - K=5"] = paired(vec[(10, 0.0)], vec[(5, 0.0)])
for k_, v_ in out["paired"].items():
    print(k_, v_)
print("DEV references: BGE top-1 0.721; Tev1-4B K=5 0.820, K=10 0.836; oracle K=5 0.852, K=10 0.869; zero-shot cross-encoder 0.705")
(ROOT / "reports/ner_v2/_cd_l1_l2_dev.json").write_text(json.dumps(out, indent=1))
