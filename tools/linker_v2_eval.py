#!/usr/bin/env python3
"""S127: BGE vs E5 on linker_data_v2 (true held-out NIL). Selection set = dev (dev_alias positives, dev NIL); unseen_alias / unseen_concept = held-out report only.
Retrieval, NIL separation (AUROC), tau chosen on dev, and a dev-fitted logistic confidence [top1, margin, entropy(top5)] for P(top-1 correct & concept present), reported on held-out."""
import json
import random
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.scoring.calibration import ece  # noqa: E402

RAW = ROOT / "reports/ner/_raw_v2"
MODELS = {"BGE": "bge-large-en-v1.5", "E5": "e5-large-v2"}


def feats(rows):
    out = []
    for r in rows:
        v = np.array([s for _, s in r["top"]])
        p = np.exp((v - v.max()) / 0.05)
        p /= p.sum()
        out.append([v[0], v[0] - v[1], -(p * np.log(p + 1e-12)).sum() / np.log(len(p))])
    return np.array(out)


def correct(rows):
    return np.array([r["top"][0][0] == r["gold"] for r in rows])


def rank(rows):
    return np.array([next((i + 1 for i, (c, _) in enumerate(r["top"]) if c == r["gold"]), 10**6) for r in rows])


def one(model, seed):
    t = json.load(open(RAW / f"linker__{MODELS[model]}_v2d__seed{seed}.tables.json"))
    j = json.load(open(RAW / f"linker__{MODELS[model]}_v2d__seed{seed}.json"))
    da, ua, dn, un = t["dev_alias"], t["unseen_alias"], t["dev"], t["unseen_concept"]
    out = {"minutes": j["minutes"]}
    for nm, rows in (("dev_alias", da), ("unseen_alias", ua)):
        rk = rank(rows)
        out[nm] = {"acc1": float((rk == 1).mean()), "r5": float((rk <= 5).mean()), "mrr": float((1.0 / rk).mean())}
    ft = lambda rows: np.array([r["n_surf"] <= 3 for r in rows])
    rk = rank(ua)
    out["unseen_alias_tail_acc1"] = float((rk[ft(ua)] == 1).mean())
    out["unseen_alias_head_acc1"] = float((rk[~ft(ua)] == 1).mean())
    # NIL separation by top-1 cosine
    au = lambda pos, neg: float(roc_auc_score([1] * len(pos) + [0] * len(neg), list(pos) + list(neg)))
    top = lambda rows: np.array([r["top"][0][1] for r in rows])
    out["nil_auroc_dev"] = au(top(da), top(dn))
    out["nil_auroc_heldout"] = au(top(ua), top(un))
    cand = np.linspace(0.5, 1.0, 101)
    tau = max(cand, key=lambda c: 0.5 * ((top(da) >= c).mean() + (top(dn) < c).mean()))     # tau on dev only
    out["tau_dev"] = float(tau)
    out["nil_heldout"] = {"precision": float((top(un) < tau).sum() / max((top(un) < tau).sum() + (top(ua) < tau).sum(), 1)), "recall": float((top(un) < tau).mean()),
                          "false_nil_rate_on_aliases": float((top(ua) < tau).mean())}
    # confidence: target = concept present AND top-1 correct; fit on dev, report on held-out
    Xd, yd = np.vstack([feats(da), feats(dn)]), np.concatenate([correct(da), np.zeros(len(dn), bool)]).astype(int)
    Xh, yh = np.vstack([feats(ua), feats(un)]), np.concatenate([correct(ua), np.zeros(len(un), bool)]).astype(int)
    m = LogisticRegression(max_iter=1000).fit(Xd, yd)
    p = m.predict_proba(Xh)[:, 1]
    pc = np.clip(p, 1e-3, 1 - 1e-3)
    out["conf_heldout"] = {"ece": ece(p.tolist(), yh.tolist())["ece"], "brier": float(np.mean((p - yh) ** 2)), "nll": float(-np.mean(yh * np.log(pc) + (1 - yh) * np.log(1 - pc))),
                           "auroc": float(roc_auc_score(yh, p)), "n": int(len(yh)), "pos_rate": float(yh.mean())}
    return out, (rank(da), rank(ua), p, yh)


def main():
    res, per = {}, {}
    for model in MODELS:
        runs = [one(model, s) for s in (1, 2, 3, 4, 5)]
        res[model] = {k: ({a: float(np.mean([r[0][k][a] for r in runs])) for a in runs[0][0][k]} if isinstance(runs[0][0][k], dict) else float(np.mean([r[0][k] for r in runs])))
                      for k in runs[0][0]}
        res[model]["acc1_dev_alias_sd"] = float(np.std([r[0]["dev_alias"]["acc1"] for r in runs]))
        res[model]["conf_heldout"] = {a: float(np.mean([r[0]["conf_heldout"][a] for r in runs])) for a in runs[0][0]["conf_heldout"]}
        per[model] = runs
    rng = random.Random(0)
    cmp = {}
    for nm, idx in (("dev_alias", 0), ("unseen_alias(report only)", 1)):
        a = np.mean([r[1][idx] == 1 for r in per["BGE"]], 0)
        b = np.mean([r[1][idx] == 1 for r in per["E5"]], 0)
        d = a - b
        bs = [d[[rng.randrange(len(d)) for _ in d]].mean() for _ in range(5000)]
        cmp[nm] = {"n": int(len(d)), "acc1_diff_BGE_minus_E5": float(d.mean()), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    # held-out confidence NLL paired over items (seed-averaged probabilities)
    pb, pe = np.mean([r[1][2] for r in per["BGE"]], 0), np.mean([r[1][2] for r in per["E5"]], 0)
    yh = per["BGE"][0][1][3]
    nl = lambda p: -(yh * np.log(np.clip(p, 1e-3, 1 - 1e-3)) + (1 - yh) * np.log(1 - np.clip(p, 1e-3, 1 - 1e-3)))
    d = nl(pb) - nl(pe)
    bs = [d[[rng.randrange(len(d)) for _ in d]].mean() for _ in range(2000)]
    cmp["heldout_conf_nll_BGE_minus_E5"] = {"diff": float(d.mean()), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    out = {"models": res, "paired": cmp}
    (ROOT / "reports/ner/_linker_v2_eval.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
