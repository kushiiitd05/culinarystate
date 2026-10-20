#!/usr/bin/env python3
"""Server-side, DEV-only, deterministic shortlist for RecipeDB3 elimination (design contract B: no TEST). Reads TASTEset wave-2 run JSONs (history -> best dev micro F1),
applies PRE-DECLARED rules, writes jobs_rdb3_elim.txt and shortlist.json.
Rules: a variant is shortlisted only if mean DEV micro-F1 (5 seeds) beats its own control by >= 0.003:
  knowledge Kx vs base+CRF (K0); span head vs metadata-off no-span control. The best qualifying variant of each family is kept.
Fusion is NOT shortlisted here: the contract requires the calibrator to show metadata signal first. Always included: base, base+CRF (with --conf), v3-large+CRF."""
import glob
import json
import statistics as st
import time
from pathlib import Path

# K4 lane (jobs_k4.txt) is launched separately; wait for it (max 3 h) so K4 can be shortlisted on equal terms
for _ in range(90):
    q = Path("queue_k4.out")
    if not q.exists() or "cmds-done" in q.read_text():
        break
    time.sleep(120)

R = Path("runs")


def dev(pattern):
    v = []
    for f in sorted(glob.glob(str(R / pattern))):
        if f.endswith(".pred.json"):
            continue
        h = json.load(open(f))["history"]
        v.append(max(x["dev_micro_f1"] for x in h))
    return v


def mean(v):
    return st.mean(v) if v else None


M = "--dataset recipedb3 --model microsoft/deberta-base"
base = dev("tasteset__deberta-base_crf__seed*.json")
out, info = [], {"base_crf_dev": mean(base), "n_base": len(base)}
ks = {k: dev(f"tasteset__deberta-base_crf_{k}__seed*.json") for k in ("K1", "K2", "K3", "K4")}
info["knowledge_dev"] = {k: (mean(v), len(v)) for k, v in ks.items()}
cand = [(mean(v), k) for k, v in ks.items() if len(v) >= 5 and base and mean(v) - mean(base) >= 0.003]
kbest = max(cand)[1] if cand else None
zero, span = dev("tasteset__deberta-base_fusion-zero__seed*.json"), dev("tasteset__deberta-base_fusion-zero+span0.5__seed*.json")
info.update({"zero_control_dev": mean(zero), "span_dev": mean(span), "n_zero": len(zero), "n_span": len(span)})
span_ok = len(zero) >= 5 and len(span) >= 5 and mean(span) - mean(zero) >= 0.003
info.update({"knowledge_winner": kbest, "span_head_qualifies": span_ok})
out.append(f"bench_train.py {M} --seed 1 --out runs")
out.append(f"bench_train.py {M} --crf --conf --seed 1 --out runs")
out.append("bench_train.py --dataset recipedb3 --model microsoft/deberta-v3-large --crf --seed 1 --out runs")
if kbest:
    out.append(f"bench_train.py {M} --crf --knowledge {kbest} --seed 1 --out runs")
if span_ok:
    out.append(f"fusion_train.py {M} --mode gated --zero-meta --feats recipedb3_span_feats_v1.npz --seed 1 --out runs")
    out.append(f"fusion_train.py {M} --mode gated --zero-meta --span-lambda 0.5 --feats recipedb3_span_feats_v1.npz --seed 1 --out runs")
Path("jobs_rdb3_elim.txt").write_text("\n".join(out) + "\n")
Path("shortlist.json").write_text(json.dumps({"rules": "DEV mean (5 seeds) >= control + 0.003; fusion excluded until calibrator shows metadata signal", "info": info, "jobs": out}, indent=1))
print(json.dumps(info, indent=1))
