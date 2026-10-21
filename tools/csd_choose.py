#!/usr/bin/env python3
"""CulinarySpanDecision-v1: numeric choosers S0-S3 over CRF top-5 paths (TASTEset). No text features, no TEST. Protocol: reports/ner_v2/culinary_span_decision_v1_protocol.md (gate frozen).
Decision unit = cluster of overlapping spans across the 5 paths; options = the restriction of each path to the cluster; the chooser picks one option per cluster (default = path-1 option).
Selection of the headline system uses TRAIN-OOF CV only (never DEV).
  python tools/csd_choose.py [out_json]"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "features/csd"
rng = np.random.RandomState(20261022)
UA, UB = 1.07, 0.93  # local F1 utility (tp, fp) near F1 ~ 0.93: dF ~ (2-F)tp - F*fp


def load():
    df = pd.read_csv(ROOT / "data/raw/tasteset/TASTEset.csv")
    gold = {i: {(e["start"], e["end"], e["type"]) for e in json.loads(r.ingredients_entities)} for i, r in enumerate(df.itertuples())}
    oof = []
    for k in range(5):
        d = json.load(open(D / f"tasteset__deberta-base_crf_oof{k}__seed1.nbest_oof.json"))
        oof += [(i, k, p) for i, p in zip(d["doc_indices"], d["nbest"])]
    dev_idx = json.load(open(ROOT / "benchmark/ner/splits/tasteset_split_v1.json"))["indices"]["dev"]
    dev = [(i, -1, p) for i, p in zip(dev_idx, json.load(open(D / "tasteset__deberta-base_crf__seed1.nbest_dev.json")))]
    return gold, oof, dev


def clusters(paths):
    P = [{tuple(s) for s in p["spans"]} for p in paths]
    U = sorted(set().union(*P), key=lambda s: (s[0], s[1]))
    comps, cur, end = [], [], -1
    for s in U:
        if cur and s[0] >= end:
            comps.append(cur)
            cur, end = [], -1
        cur.append(s)
        end = max(end, s[1])
    if cur:
        comps.append(cur)
    return P, comps


def build(items, gold, T=1.0):
    """-> list of documents; each doc: list of clusters; each cluster: dict(options=[dict(spans, mass, best_rank, gap, ...)], p1=index)."""
    docs = []
    for i, fold, paths in items:
        sc = np.array([p["score"] for p in paths], float)
        pr = np.exp((sc - sc.max()) / T)
        pr /= pr.sum()
        P, comps = clusters(paths)
        g = gold[i]
        cl = []
        for comp in comps:
            cs = set(comp)
            opts = {}
            for r, ps in enumerate(P):
                o = frozenset(ps & cs)
                e = opts.setdefault(o, {"spans": o, "ranks": [], "mass": 0.0})
                e["ranks"].append(r)
                e["mass"] += pr[r]
            op = list(opts.values())
            p1 = next(k for k, e in enumerate(op) if 0 in e["ranks"])
            for e in op:
                tp, fp = len(e["spans"] & g), len(e["spans"] - g)
                e["tp"], e["fp"], e["u"] = tp, fp, UA * tp - UB * fp
            cl.append({"options": op, "p1": p1})
        docs.append({"i": i, "fold": fold, "gold": g, "scores": sc, "clusters": cl, "P": P})
    return docs


def feats(c, k, sc):
    op, p1 = c["options"], c["options"][c["p1"]]
    e = op[k]
    ml = lambda sp: [s[1] - s[0] for s in sp] or [0]
    masses = np.array([x["mass"] for x in op])
    ent = float(-(masses[masses > 0] * np.log(masses[masses > 0])).sum())
    lab = Counter(s[2] for s in e["spans"])
    sb = {(s[0], s[1]) for s in e["spans"]}
    pb = {(s[0], s[1]) for s in p1["spans"]}
    return [e["mass"], e["mass"] / max(p1["mass"], 1e-9), p1["mass"], min(e["ranks"]), len(e["ranks"]), len(e["spans"]), len(e["spans"]) - len(p1["spans"]), sum(ml(e["spans"])), sum(ml(e["spans"])) - sum(ml(p1["spans"])),
            float(np.mean(ml(e["spans"]))), len(lab), lab.get("FOOD", 0), len(op), ent, float(sb == pb), float(sum(ml(e["spans"])) > sum(ml(p1["spans"]))), sc[min(e["ranks"])] - sc[0], sc[0] - sc[1]]


def assemble(doc, choose):
    out = set()
    for ci, c in enumerate(doc["clusters"]):
        out |= c["options"][choose(doc, ci, c)]["spans"]
    return out


def prf(tp, fp, fn):
    return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 1.0


def kind(g, pred):
    if g in pred:
        return "present"
    ov = [p for p in pred if p[0] < g[1] and g[0] < p[1]]
    if not ov:
        return "fully missed span"
    if any(p[0] == g[0] and p[1] == g[1] for p in ov):
        return "label-only error"
    return "boundary+label error" if not any(p[2] == g[2] for p in ov) else "same-label boundary error"


def evaluate(docs, preds, name):
    n = len(docs)
    cnt = np.zeros((n, 6))  # tp,fp,fn for p1 and chosen
    rec, dam = Counter(), Counter()
    reck, damk = Counter(), Counter()
    fpn = 0
    for d_, (doc, pr) in enumerate(zip(docs, preds)):
        g, p1 = doc["gold"], doc["P"][0]
        cnt[d_] = [len(g & p1), len(p1 - g), len(g - p1), len(g & pr), len(pr - g), len(g - pr)]
        for s in (g & pr) - p1:
            rec[s[2]] += 1
            reck[kind(s, p1)] += 1
        for s in (g & p1) - pr:
            dam[s[2]] += 1
            damk[kind(s, pr)] += 1
        fpn += len(pr - g) - len(p1 - g)
    S = cnt.sum(0)
    f1_0, f1_c = prf(*S[:3]), prf(*S[3:])
    d = np.array([prf(*c[3:]) - prf(*c[:3]) for c in cnt])  # not used for CI; CI uses micro delta below

    def micro(ix):
        s = cnt[ix].sum(0)
        return prf(*s[3:]) - prf(*s[:3])
    bs = [micro(rng.randint(0, n, n)) for _ in range(3000)]
    grp = lambda c: {"FOOD": c["FOOD"], "PHYSICAL_QUALITY": c["PHYSICAL_QUALITY"], "PROCESS": c["PROCESS"], "other labels": sum(v for k, v in c.items() if k not in ("FOOD", "PHYSICAL_QUALITY", "PROCESS"))}
    R, Dm = sum(rec.values()), sum(dam.values())
    return {"system": name, "path1_F1": round(f1_0, 4), "chooser_F1": round(f1_c, 4), "delta": round(f1_c - f1_0, 4), "ci95": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
            "recovered": R, "damaged": Dm, "net_recovered": R - Dm, "damage_recovery_ratio": round(Dm / R, 3) if R else None, "extra_false_positives": int(fpn),
            "recovered_by_label": grp(rec), "damaged_by_label": grp(dam), "recovered_by_error_type": dict(reck), "damaged_by_error_type": dict(damk)}


def oracle_doc(docs):
    s = np.zeros(3)
    for doc in docs:
        g = doc["gold"]
        b = max(doc["P"], key=lambda p: (prf(len(g & p), len(p - g), len(g - p)), p == doc["P"][0]))
        s += [len(g & b), len(b - g), len(g - b)]
    return prf(*s)


def oracle_cluster(docs):
    return evaluate(docs, [assemble(doc, lambda d_, ci, c: max(range(len(c["options"])), key=lambda k: (c["options"][k]["u"], k == c["p1"]))) for doc in docs], "cluster-oracle")["chooser_F1"]


# ---- systems ----
def s0(docs, **_):
    return [assemble(d, lambda d_, ci, c: c["p1"]) for d in docs]


def mass_choice(doc, ci, c, margin):
    op = c["options"]
    best = max(range(len(op)), key=lambda k: (op[k]["mass"], k == c["p1"]))
    return best if op[best]["mass"] > op[c["p1"]]["mass"] * (1 + margin) else c["p1"]


def s1(docs, **_):
    return [assemble(d, lambda d_, ci, c: mass_choice(d_, ci, c, 0.0)) for d in docs]


GRID = [(T, m) for T in (0.5, 1.0, 2.0, 4.0) for m in (0.0, 0.25, 0.5, 1.0, 2.0)]


def s2_fit(items, gold, tr_idx):
    best, bf = None, -1
    for T, m in GRID:
        ds = build([items[j] for j in tr_idx], gold, T)
        pr = [assemble(d, lambda d_, ci, c: mass_choice(d_, ci, c, m)) for d in ds]
        f = evaluate(ds, pr, "g")["delta"]
        if f > bf:
            best, bf = (T, m), f
    return best


def s2_apply(items, gold, Tm):
    T, m = Tm
    ds = build(items, gold, T)
    return ds, [assemble(d, lambda d_, ci, c: mass_choice(d_, ci, c, m)) for d in ds]


def s3_rows(docs):
    X, y = [], []
    for doc in docs:
        for c in doc["clusters"]:
            for k, e in enumerate(c["options"]):
                if k != c["p1"]:
                    X.append(feats(c, k, doc["scores"]))
                    y.append(e["u"] - c["options"][c["p1"]]["u"])
    return np.array(X), np.array(y)


def s3_fit(docs):
    X, y = s3_rows(docs)
    return HistGradientBoostingRegressor(max_depth=3, max_iter=100, learning_rate=0.05, min_samples_leaf=20, l2_regularization=1.0, random_state=0).fit(X, y)


def s3_apply(docs, mdl):
    def ch(doc, ci, c):
        ks = [k for k in range(len(c["options"])) if k != c["p1"]]
        if not ks:
            return c["p1"]
        pr = mdl.predict(np.array([feats(c, k, doc["scores"]) for k in ks]))
        j = int(np.argmax(pr))
        return ks[j] if pr[j] > 0 else c["p1"]
    return [assemble(d, ch) for d in docs]


def grade(r, oracle_f1):
    eff = (r["chooser_F1"] - r["path1_F1"]) / (oracle_f1 - r["path1_F1"]) if oracle_f1 > r["path1_F1"] else None
    dr = r["damage_recovery_ratio"]
    lo = r["ci95"][0]
    if lo > 0 and eff is not None and eff >= 0.30 and dr is not None and dr <= 0.33:
        c = "A"
    elif r["delta"] <= 0 or eff is None or eff < 0.10 or dr is None or dr > 0.67:
        c = "C"
    else:
        c = "B"
    return c, (round(eff, 3) if eff is not None else None)


def main(outp):
    gold, oof, dev = load()
    # TRAIN-OOF CV: folds = the 5 OOF folds (doc-disjoint)
    items_all = oof
    fold = np.array([f for _, f, _ in oof])
    res = {"oof": {}, "dev": {}}
    base = build(oof, gold)
    docs_f = {k: [d for d in base if d["fold"] == k] for k in range(5)}
    res["oracle"] = {"oof_doc_top5": round(oracle_doc(base), 4), "oof_cluster": oracle_cluster(base)}
    dev_base = build(dev, gold)
    res["oracle"].update({"dev_doc_top5": round(oracle_doc(dev_base), 4), "dev_cluster": oracle_cluster(dev_base)})
    res["n"] = {"oof_docs": len(oof), "oof_gold_spans": sum(len(d["gold"]) for d in base), "dev_docs": len(dev), "dev_gold_spans": sum(len(d["gold"]) for d in dev_base),
                "clusters_with_choice(oof)": sum(len(c["options"]) > 1 for d in base for c in d["clusters"]), "clusters_total(oof)": sum(len(d["clusters"]) for d in base)}
    # ---- OOF CV (held-out folds) ----
    preds = {n: [None] * len(oof) for n in ("S0", "S1", "S2", "S3")}
    order = {id(d): j for j, d in enumerate(base)}
    chosen_grid = []
    for k in range(5):
        tr_idx = [j for j in range(len(oof)) if fold[j] != k]
        te_idx = [j for j in range(len(oof)) if fold[j] == k]
        te_items = [oof[j] for j in te_idx]
        te_docs = build(te_items, gold)
        for n, pr in (("S0", s0(te_docs)), ("S1", s1(te_docs))):
            for j, p in zip(te_idx, pr):
                preds[n][j] = p
        Tm = s2_fit(oof, gold, tr_idx)
        chosen_grid.append(Tm)
        ds2, pr2 = s2_apply(te_items, gold, Tm)
        for j, p in zip(te_idx, pr2):
            preds["S2"][j] = p
        mdl = s3_fit([base[j] for j in tr_idx])
        for j, p in zip(te_idx, s3_apply(te_docs, mdl)):
            preds["S3"][j] = p
    res["S2_selected_grid_per_fold"] = chosen_grid
    for n in ("S0", "S1", "S2", "S3"):
        r = evaluate(base, preds[n], n)
        r["class"], r["recovery_efficiency_vs_doc_top5_oracle"] = grade(r, res["oracle"]["oof_doc_top5"]) if n != "S0" else ("-", 0.0)
        r["recovery_efficiency_vs_cluster_oracle"] = round((r["chooser_F1"] - r["path1_F1"]) / (res["oracle"]["oof_cluster"] - r["path1_F1"]), 3)
        res["oof"][n] = r
    # ---- DEV (chooser fit on all OOF) ----
    Tm = s2_fit(oof, gold, list(range(len(oof))))
    res["S2_selected_grid_all_oof"] = Tm
    mdl = s3_fit(base)
    dev_preds = {"S0": s0(dev_base), "S1": s1(dev_base), "S2": s2_apply(dev, gold, Tm)[1], "S3": s3_apply(dev_base, mdl)}
    for n, pr in dev_preds.items():
        r = evaluate(dev_base, pr, n)
        r["class"], r["recovery_efficiency_vs_doc_top5_oracle"] = grade(r, res["oracle"]["dev_doc_top5"]) if n != "S0" else ("-", 0.0)
        r["recovery_efficiency_vs_cluster_oracle"] = round((r["chooser_F1"] - r["path1_F1"]) / (res["oracle"]["dev_cluster"] - r["path1_F1"]), 3)
        res["dev"][n] = r
    # headline = best OOF-CV delta (DEV never used for selection)
    head = max(("S1", "S2", "S3"), key=lambda n: res["oof"][n]["delta"])
    cs = {"A": 3, "B": 2, "C": 1}
    final = min((res["oof"][head]["class"], res["dev"][head]["class"]), key=lambda c: cs[c])
    res["headline"] = {"system": head, "selected_on": "TRAIN-OOF CV delta only", "oof_class": res["oof"][head]["class"], "dev_class": res["dev"][head]["class"], "RESULT": "CSD-" + final,
                       "rule": "class = lower of OOF-CV and DEV class; efficiency vs pre-registered top-5 per-document oracle"}
    Path(outp).write_text(json.dumps(res, indent=1, default=str))
    for part in ("oof", "dev"):
        for n, r in res[part].items():
            print(part, n, {k: r[k] for k in ("path1_F1", "chooser_F1", "delta", "ci95", "recovered", "damaged", "net_recovered", "damage_recovery_ratio", "extra_false_positives", "recovery_efficiency_vs_doc_top5_oracle", "class")})
    print(json.dumps({k: res[k] for k in ("oracle", "n", "headline", "S2_selected_grid_all_oof")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "reports/ner_v2/_csd_s0_s3.json"))
