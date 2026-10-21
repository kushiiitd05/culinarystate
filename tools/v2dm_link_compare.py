#!/usr/bin/env python3
"""V2-DM Track C: same-candidate comparison (K ablation). Methods: BGE top-1, conventional cross-encoder (zero-shot bge-reranker-large), decision models (forced choice over candidates; NONE probability for NIL).
Viewed sets only (dev_alias selection, unseen_alias report-only); fresh set is scored separately once labelled.  python tools/v2dm_link_compare.py"""
import json
import string
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "reports/ner_v2/_dm_raw"
T = {}
for l in open(ROOT / "features/v2dm/linker_tasks_k10.jsonl"):
    r = json.loads(l)
    T[r["id"]] = r


def dm_results(path, k):
    keys = list(string.ascii_uppercase[:k])
    out = {}
    for l in open(path):
        r = json.loads(l)
        if not r["resp"]:
            continue
        a = r["resp"]["answers"]["link"]
        p = a["probabilities"]
        best = max(keys, key=lambda x: p.get(x, 0))
        out[r["id"]] = {"pick": T[r["id"]]["cands"][keys.index(best)]["id"], "pnone": p.get("NONE", 0.0), "ms": r["ms"], "default_none": a["choice"] == "NONE"}
    return out


def ce_results(k):
    out = {}
    for l in open(RAW / "ce_k10.jsonl"):
        r = json.loads(l)
        s = r["scores"][:k]
        out[r["id"]] = {"pick": T[r["id"]]["cands"][int(np.argmax(s))]["id"], "max": float(max(s))}
    return out


def report(name, res, k, nilscore):
    row = {"method": name, "K": k}
    for pos, neg, tag in (("dev_alias", "dev", "dev"), ("unseen_alias", "unseen_concept", "heldout")):
        ids = [i for i, t in T.items() if t["set"] == pos and i in res]
        acc = np.mean([res[i]["pick"] == T[i]["gold"] for i in ids])
        top1 = np.mean([T[i]["cands"][0]["id"] == T[i]["gold"] for i in ids])
        orc = np.mean([any(c["id"] == T[i]["gold"] for c in T[i]["cands"][:k]) for i in ids])
        nid = [i for i, t in T.items() if t["set"] == neg and i in res]
        y = [0] * len(ids) + [1] * len(nid)
        au = roc_auc_score(y, [nilscore(res, i) for i in ids + nid])
        row[tag] = {"acc": round(float(acc), 3), "top1": round(float(top1), 3), f"oracle@{k}": round(float(orc), 3), "efficiency": round(float((acc - top1) / max(orc - top1, 1e-9)), 3), "NIL_AUROC": round(float(au), 3)}
    if "ms" in next(iter(res.values())):
        row["median_ms"] = round(float(np.median([v["ms"] for v in res.values()])), 1)
    return row


rows = []
for k in (3, 5, 10):
    rows.append(report("Tev1-4B", dm_results(RAW / f"dm_link_tev4b_k{k}.jsonl", k), k, k_none := (lambda res, i: res[i]["pnone"])))
    rows.append(report("cross-encoder (zero-shot)", ce_results(k), k, lambda res, i: -res[i]["max"]))
base = {i: {"pick": T[i]["cands"][0]["id"]} for i in T}
rows.append(report("BGE top-1 (cosine NIL)", base, 1, lambda res, i: -T[i]["cands"][0]["score"]))
for nm in ("nimble",):
    for k in (3, 5, 10):
        p = RAW / f"dm_link_{nm}_k{k}.jsonl"
        if p.exists():
            rows.append(report("Nimble", dm_results(p, k), k, lambda res, i: res[i]["pnone"]))
(ROOT / "reports/ner_v2/_v2dm_link_compare.json").write_text(json.dumps(rows, indent=1))
for r in rows:
    print(f"{r['method']:28s} K={r['K']:2d} dev acc {r['dev']['acc']:.3f} (top1 {r['dev']['top1']:.3f}, oracle {r['dev'][[k for k in r['dev'] if k.startswith('oracle')][0]]:.3f}, eff {r['dev']['efficiency']:.2f}, NIL AUROC {r['dev']['NIL_AUROC']:.3f}) | heldout acc {r['heldout']['acc']:.3f} (eff {r['heldout']['efficiency']:.2f}, NIL AUROC {r['heldout']['NIL_AUROC']:.3f}) {r.get('median_ms', '')}ms")
