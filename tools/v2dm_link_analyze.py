#!/usr/bin/env python3
"""V2-DM Track C analysis on a frozen task file: retrieval vs reranking failure, reranker efficiency, NIL as its own sub-problem (N0 cosine, N1 raw NONE prob, N2 calibrated NONE, N3 calibrated NONE + retrieval evidence).
Calibration / thresholds use the DEV sets only (dev_alias positives, dev NIL); held-out sets are report-only and are no longer tuned on.
  python tools/v2dm_link_analyze.py <tag> <dm_results.jsonl> [--score-key choice]"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

ROOT = Path(__file__).resolve().parents[1]
K = ["A", "B", "C", "D", "E"]
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4)))


def main(tag, path):
    T = {}
    for l in open(ROOT / "features/v2dm/linker_tasks.jsonl"):
        r = json.loads(l)
        T[r["id"]] = r
    D = json.load(open(ROOT / "features/linker_data_v2.json"))["queries"]
    meta = {f"{p}-{k}": q for p, qs in D.items() if p in ("dev_alias", "unseen_alias", "dev", "unseen_concept") for k, q in enumerate(qs)}
    R = {}
    for l in open(path):
        r = json.loads(l)
        if r["resp"]:
            R[r["id"]] = r["resp"]["answers"]["link"]
    prob = lambda i: R[i]["probabilities"]
    forced = lambda i: T[i]["cands"][K.index(max(K, key=lambda k: prob(i).get(k, 0)))]["id"]
    default = lambda i: (T[i]["cands"][K.index(R[i]["choice"])]["id"] if R[i]["choice"] in K else "NONE")
    out = {"tag": tag, "sets": {}}
    for pos, neg, nm in (("dev_alias", "dev", "dev (selection/calibration)"), ("unseen_alias", "unseen_concept", "held-out (viewed; report only)")):
        ids = [i for i, t in T.items() if t["set"] == pos and i in R]
        top1 = np.mean([T[i]["cands"][0]["id"] == T[i]["gold"] for i in ids])
        oracle = np.mean([any(c["id"] == T[i]["gold"] for c in T[i]["cands"]) for i in ids])
        acc = np.mean([forced(i) == T[i]["gold"] for i in ids])
        dec = {"retrieval_failure(gold not in top5)": 0, "reranking_failure(gold in top5, wrong pick)": 0, "default_NONE_on_alias": 0, "correct": 0}
        by = {"head(n_surf>=6)": [0, 0], "tail(n_surf<=3)": [0, 0]}
        for i in ids:
            t = T[i]
            inc = any(c["id"] == t["gold"] for c in t["cands"])
            ok = forced(i) == t["gold"]
            dec["correct"] += ok
            dec["retrieval_failure(gold not in top5)"] += not inc
            dec["reranking_failure(gold in top5, wrong pick)"] += inc and not ok
            dec["default_NONE_on_alias"] += default(i) == "NONE"
            ns = meta[i]["n_surf"]
            for k_, c in (("head(n_surf>=6)", ns >= 6), ("tail(n_surf<=3)", ns <= 3)):
                if c:
                    by[k_][0] += ok
                    by[k_][1] += 1
        out["sets"][nm] = {"n": len(ids), "top1_acc": round(float(top1), 3), "model_forced_acc": round(float(acc), 3), "top5_oracle": round(float(oracle), 3),
                           "reranker_efficiency": round(float((acc - top1) / max(oracle - top1, 1e-9)), 3), "decomposition_counts": {k: int(v) for k, v in dec.items()},
                           "by_frequency_acc": {k: (round(a / n, 3) if n else None, n) for k, (a, n) in by.items()}}
    # NIL sub-problem: features per query
    def feat(i):
        c = T[i]["cands"]
        return [lg(prob(i).get("NONE", 0.0)), c[0]["score"], c[0]["score"] - c[1]["score"]]
    sets = {}
    for pos, neg, nm in (("dev_alias", "dev", "dev"), ("unseen_alias", "unseen_concept", "held-out")):
        ids = [i for i, t in T.items() if t["set"] in (pos, neg) and i in R]
        sets[nm] = (ids, np.array([T[i]["set"] == neg for i in ids], int), np.array([feat(i) for i in ids]))
    ids, y, X = sets["dev"]
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    nil = {}
    for name, cols in (("N0_cosine", [1]), ("N1_raw_NONE_prob", [0]), ("N2_calibrated_NONE", [0]), ("N3_calibrated_NONE+retrieval", [0, 1, 2])):
        if name in ("N0_cosine", "N1_raw_NONE_prob"):
            s_dev = -X[:, 1] if name == "N0_cosine" else X[:, 0]
            m = None
        else:
            s_dev = cross_val_predict(LogisticRegression(max_iter=1000), X[:, cols], y, cv=cv, method="predict_proba")[:, 1]
            m = LogisticRegression(max_iter=1000).fit(X[:, cols], y)
        ths = np.quantile(s_dev, np.linspace(0.05, 0.95, 91))
        bal = lambda th, s, yy: 0.5 * ((s[yy == 1] >= th).mean() + (s[yy == 0] < th).mean())
        th = max(ths, key=lambda t_: bal(t_, s_dev, y))
        row = {"dev_AUROC": round(float(roc_auc_score(y, s_dev)), 3), "dev_AUPRC": round(float(average_precision_score(y, s_dev)), 3), "dev_balanced_acc_at_dev_threshold": round(float(bal(th, s_dev, y)), 3)}
        _, yh, Xh = sets["held-out"]
        s_h = (-Xh[:, 1] if name == "N0_cosine" else Xh[:, 0]) if m is None else m.predict_proba(Xh[:, cols])[:, 1]
        row.update({"heldout_AUROC": round(float(roc_auc_score(yh, s_h)), 3), "heldout_AUPRC": round(float(average_precision_score(yh, s_h)), 3), "heldout_NIL_recall": round(float((s_h[yh == 1] >= th).mean()), 3),
                    "heldout_false_NONE_on_known_aliases": round(float((s_h[yh == 0] >= th).mean()), 3), "heldout_balanced_acc": round(float(bal(th, s_h, yh)), 3)})
        nil[name] = row
    out["NIL"] = nil
    (ROOT / "reports/ner_v2" / f"_v2dm_link_analysis_{tag}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
