#!/usr/bin/env python3
"""CulinaryLinkDecision-v1 CD-L0: structured baseline (no text encoder): gradient boosting over per-candidate features (retrieval score/rank/margin, lexical agreement, lengths). Train: OOF TRAIN examples; eval: DEV (dev_alias + dev). K in {5, 10}."""
import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
tok = lambda s: set(re.findall(r"[a-z0-9]+", s.lower()))


def feats(e, K):
    c = e["cands"][:K]
    m = tok(e["mention"])
    sc = [x["score"] for x in c]
    rows = []
    for i, x in enumerate(c):
        names = [x["name"]] + x["aliases"]
        jac = max(len(m & tok(n)) / max(len(m | tok(n)), 1) for n in names)
        cov = max(len(m & tok(n)) / max(len(m), 1) for n in names)
        ex = float(any(e["mention"].lower() == n.lower() for n in names))
        rows.append([sc[i], i, sc[i] - sc[0], sc[i] - (sc[i + 1] if i + 1 < len(sc) else sc[i]), jac, cov, ex, len(m), len(tok(x["name"])), len(x["aliases"]), float(e["mention"].lower().split()[-1] in {t for n in names for t in n.lower().split()}), sc[0] - sc[1] if len(sc) > 1 else 0])
    return rows


def main(K):
    tr = [json.loads(l) for l in open(ROOT / "features/v2dm/link_oof.jsonl")]
    dev = [e for e in (json.loads(l) for l in open(ROOT / "features/v2dm/linker_tasks_k10.jsonl")) if e["set"] in ("dev_alias", "dev")]
    X, y = [], []
    for e in tr:
        f = feats(e, K)
        X += f
        y += [int(c["id"] == e["gold"]) for c in e["cands"][:K]]
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=0).fit(np.array(X), np.array(y))
    pos, nil = [e for e in dev if e["set"] == "dev_alias"], [e for e in dev if e["set"] == "dev"]
    pr = lambda e: m.predict_proba(np.array(feats(e, K)))[:, 1]
    forced = [e["cands"][int(np.argmax(pr(e)))]["id"] == e["gold"] for e in pos]
    s = [-pr(e).max() for e in pos] + [-pr(e).max() for e in nil]
    yy = [0] * len(pos) + [1] * len(nil)
    bge = np.mean([e["cands"][0]["id"] == e["gold"] for e in pos])
    out = {"K": K, "CD-L0_dev_alias_forced_acc": round(float(np.mean(forced)), 3), "BGE_top1_dev_alias": round(float(bge), 3), "oracle": round(float(np.mean([any(c["id"] == e["gold"] for c in e["cands"][:K]) for e in pos])), 3),
           "NIL_AUROC(-max cand prob)": round(float(roc_auc_score(yy, s)), 3), "NIL_AUPRC": round(float(average_precision_score(yy, s)), 3), "n_train_rows": len(X), "n_pos_train": int(sum(1 for e in tr if e["gold"] != "NIL"))}
    (ROOT / "reports/ner_v2" / f"_cd_l0_k{K}.json").write_text(json.dumps(out, indent=1))
    print(out)


if __name__ == "__main__":
    for k in (5, 10):
        main(k)
