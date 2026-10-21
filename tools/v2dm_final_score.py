#!/usr/bin/env python3
"""CulinaryLinkDecision FINAL: the single frozen scoring run on the 850-item human gold (protocol: reports/ner_v2/culinary_link_decision_final_eval_protocol.md).
Reads ONLY stored system outputs + the frozen gold. Nothing tuned. AMBIGUOUS = set-valued (NONE may be a member of the set).
  python tools/v2dm_final_score.py [out_json]"""
import json
import string
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
V, RAW = ROOT / "reports/ner_v2/_final_sys", ROOT / "reports/ner_v2/_dm_raw"
GOLD = ROOT / "annotation/gold/final_link_set/FINAL_LINK_GOLD.csv"
KEYS = list(string.ascii_uppercase[:5])
rng = np.random.RandomState(20261021)
SEEDS = (1, 2, 3)
STU = {f"CD-L{n}": [f"CD-L{n}_s{s}" for s in SEEDS] for n in (2, 1)}


def load(G):
    tasks = {r["id"]: r for r in map(json.loads, open(ROOT / "features/v2dm/final_tasks_k10.jsonl"))}
    ev = json.load(open(ROOT / "reports/ner/_linker_v2_eval.json"))["models"]
    tau = {"BGE": ev["BGE"]["tau_dev"], "E5": ev["E5"]["tau_dev"]}
    e5 = json.load(open(RAW / "final_export_e5-large-v2.json"))["scores"]
    ce = {r["id"]: r["scores"] for r in map(json.loads, open(V / "final_ce_k10.jsonl"))}
    dm = {nm: {r["id"]: r for r in map(json.loads, open(V / f))} for nm, f in (("Tev1-4B", "final_tev4b_k5.jsonl"), ("Nimble", "final_nimble_k5.jsonl"))}
    stu = {}
    for n, lam in ((2, "1.0"), (1, "0")):
        for s in SEEDS:
            stu[f"CD-L{n}_s{s}"] = {r["id"]: r for r in json.load(open(V / f"final_stu_lam{lam}_s{s}.json"))["results"]}
    S = {k: {} for k in ["BGE", "E5", "CE", "Tev1-4B", "Nimble", *stu]}
    for i in G.item_id:
        t = tasks[i]
        c = t["cands"]
        S["BGE"][i] = {"pick": c[0]["id"], "nil": -c[0]["score"], "ans": "NONE" if c[0]["score"] < tau["BGE"] else c[0]["id"], "pool": [x["id"] for x in c[:5]], "ms": None}
        e = e5[t["mention"]]
        S["E5"][i] = {"pick": e[0][0], "nil": -e[0][1], "ans": "NONE" if e[0][1] < tau["E5"] else e[0][0], "pool": [x[0] for x in e[:5]], "ms": None}
        sc = ce[i]
        S["CE"][i] = {"pick": c[int(np.argmax(sc))]["id"], "nil": -max(sc), "ans": None, "pool": [x["id"] for x in c[:10]], "ms": None}
        for nm in ("Tev1-4B", "Nimble"):
            r = dm[nm].get(i)
            if not r or not r["resp"]:
                S[nm][i] = {"pick": None, "nil": np.nan, "ans": None, "pool": [x["id"] for x in c[:5]], "ms": None, "failed": True}
                continue
            a = r["resp"]["answers"]["link"]
            p = a["probabilities"]
            best = max(KEYS, key=lambda k: p.get(k, 0))
            S[nm][i] = {"pick": c[KEYS.index(best)]["id"], "nil": p.get("NONE", 0.0), "ans": c[KEYS.index(a["choice"])]["id"] if a["choice"] in KEYS else "NONE", "pool": [x["id"] for x in c[:5]], "ms": r["ms"]}
        for k, d in stu.items():
            r = d[i]
            S[k][i] = {"pick": r["forced"], "nil": r["pnone"], "ans": r["default"], "pool": [x["id"] for x in c[:10]], "ms": r["ms"]}
    return S


def ci(x, B=5000):
    x = np.asarray(x, float)
    b = [x[rng.randint(0, len(x), len(x))].mean() for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]


def paired(a, b, B=5000):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    bs = [d[rng.randint(0, len(d), len(d))].mean() for _ in range(B)]
    n10, n01 = int(((a > b)).sum()), int(((a < b)).sum())
    p = binomtest(n10, n10 + n01, 0.5).pvalue if n10 + n01 else 1.0
    return {"diff": round(float(d.mean()), 3), "ci95": [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)], "sign_test_p": round(float(p), 4), "n": int(len(d))}


def main(outp):
    G = pd.read_csv(GOLD, dtype=str, keep_default_na=False)
    assert len(G) == 850 and G.item_id.is_unique
    S = load(G)
    R = {}
    for _, g in G.iterrows():
        st = set(x for x in g.final_acceptable_set.split(";") if x)
        R[g.item_id] = {"cls": g.final_class, "con": g.final_concept, "set": st, "ids": st - {"NONE"}, "stratum": g.stratum, "mention": g.mention}
    ids = list(G.item_id)

    def va_items(pol):  # forced choice: concept-bearing items only
        return [i for i in ids if R[i]["cls"] == "MATCH" or (pol == "lenient" and R[i]["cls"] == "PARENT") or (R[i]["cls"] == "AMBIGUOUS" and R[i]["ids"])]

    def ok_pick(sys_, i, pol):
        r, p = R[i], S[sys_][i]["pick"]
        if p is None:
            return 0
        if r["cls"] == "AMBIGUOUS":
            return int(p in r["ids"])
        return int(p == r["con"])

    def vb_items(pol):
        return [i for i in ids if R[i]["cls"] in ("NONE", "MATCH", "AMBIGUOUS") or (pol == "lenient" and R[i]["cls"] == "PARENT")]

    def ok_ans(sys_, i):
        r, a = R[i], S[sys_][i]["ans"]
        if a is None:
            return None
        if r["cls"] == "NONE":
            return int(a == "NONE")
        if r["cls"] == "AMBIGUOUS":
            return int(a in r["set"])
        return int(a == r["con"])

    # per-item correctness vectors; students = mean over 3 seeds (the expected single-seed correctness)
    def vecA(name, pol):
        its = va_items(pol)
        ms = STU.get(name, [name])
        return its, np.mean([[ok_pick(m, i, pol) for i in its] for m in ms], axis=0)

    def vecB(name, pol):
        its = [i for i in vb_items(pol)]
        ms = STU.get(name, [name])
        if ok_ans(ms[0], its[0]) is None:
            return its, None
        return its, np.mean([[ok_ans(m, i) for i in its] for m in ms], axis=0)

    systems = ["BGE", "E5", "CE", "Tev1-4B", "Nimble", "CD-L2", "CD-L1"]
    out = {"n": 850, "gold_counts": G.final_class.value_counts().to_dict(), "systems": {}, "per_seed": {}, "paired": {}}
    for nm in systems:
        o = {}
        for pol in ("strict", "lenient"):
            its, v = vecA(nm, pol)
            o[f"viewA_{pol}"] = {"n": len(its), "acc": round(float(v.mean()), 3), "ci95": ci(v)}
            its, v = vecB(nm, pol)
            if v is not None:
                o[f"viewB_{pol}"] = {"n": len(its), "acc": round(float(v.mean()), 3), "ci95": ci(v)}
        its, v = vecA(nm, "strict")
        o["viewA_strict_unambiguous_only(MATCH)"] = round(float(np.mean([x for i, x in zip(its, v) if R[i]["cls"] == "MATCH"])), 3)
        o["viewA_strict_by_stratum"] = {s: {"n": sum(R[i]["stratum"] == s for i in its), "acc": round(float(np.mean([x for i, x in zip(its, v) if R[i]["stratum"] == s])), 3)} for s in sorted({R[i]["stratum"] for i in ids})}
        # NIL (view C): NONE vs known (MATCH/PARENT); seeds averaged by per-seed AUROC
        nil = [i for i in ids if R[i]["cls"] == "NONE"]
        kn = [i for i in ids if R[i]["cls"] in ("MATCH", "PARENT")]
        y = np.array([1] * len(nil) + [0] * len(kn))
        aucs, aps, recs, fns = [], [], [], []
        for m in STU.get(nm, [nm]):
            sc = np.array([S[m][i]["nil"] for i in nil + kn], float)
            if np.isnan(sc).any():
                continue
            aucs.append(roc_auc_score(y, sc))
            aps.append(average_precision_score(y, sc))
            if S[m][ids[0]]["ans"] is not None:
                dn = np.array([S[m][i]["ans"] == "NONE" for i in nil + kn], float)
                recs.append(dn[y == 1].mean())
                fns.append(dn[y == 0].mean())
        if aucs:
            o["NIL"] = {"AUROC": round(float(np.mean(aucs)), 3), "AUPRC": round(float(np.mean(aps)), 3), "n_NONE": len(nil), "n_known": len(kn)}
            if recs:
                o["NIL"].update({"NIL_recall": round(float(np.mean(recs)), 3), "false_NONE_on_known": round(float(np.mean(fns)), 3), "balanced_acc": round(float(0.5 * (np.mean(recs) + 1 - np.mean(fns))), 3)})
        # retrieval vs reranking (MATCH items)
        ms_ = STU.get(nm, [nm])
        mt = [i for i in ids if R[i]["cls"] == "MATCH"]
        inpool = sum(R[i]["con"] in set(S[ms_[0]][i]["pool"]) for i in mt)
        o["pool_strict_MATCH"] = {"n": len(mt), "oracle": round(inpool / len(mt), 3), "acc": round(float(np.mean([[S[m][i]["pick"] == R[i]["con"] for i in mt] for m in ms_])), 3)}
        msl = [S[m][i]["ms"] for m in ms_ for i in ids if S[m][i]["ms"] is not None]
        o["latency_median_ms"] = round(float(np.median(msl)), 1) if msl else None
        o["failed_calls"] = int(sum(1 for i in ids if S[ms_[0]][i].get("failed")))
        out["systems"][nm] = o
    for m in [k for k in S if "_s" in k]:
        its, _ = vecA("BGE", "strict")
        out["per_seed"][m] = {"viewA_strict": round(float(np.mean([ok_pick(m, i, "strict") for i in va_items("strict")])), 3), "viewA_lenient": round(float(np.mean([ok_pick(m, i, "lenient") for i in va_items("lenient")])), 3)}
    # paired comparisons (view A)
    for pol in ("strict", "lenient"):
        va = {nm: dict(zip(*vecA(nm, pol))) for nm in systems}
        com = sorted(va["BGE"])
        for a_, b_ in (("CD-L2", "BGE"), ("CD-L2", "E5"), ("CD-L2", "CE"), ("CD-L2", "CD-L1"), ("CD-L2", "Tev1-4B"), ("CD-L2", "Nimble"), ("Tev1-4B", "BGE"), ("Tev1-4B", "E5"), ("Nimble", "BGE"), ("CD-L1", "BGE"), ("CE", "BGE")):
            out["paired"][f"viewA_{pol}: {a_} - {b_}"] = paired([va[a_][i] for i in com], [va[b_][i] for i in com])
        # Q2 retention with bootstrap
        a, t, b = (np.array([va[k][i] for i in com]) for k in ("CD-L2", "Tev1-4B", "BGE"))
        ret = []
        for _ in range(5000):
            ix = rng.randint(0, len(com), len(com))
            den = t[ix].mean() - b[ix].mean()
            if abs(den) > 1e-6:
                ret.append((a[ix].mean() - b[ix].mean()) / den)
        out["paired"][f"Q2 retention {pol}: (CD-L2-BGE)/(Tev-BGE)"] = {"point": round(float((a.mean() - b.mean()) / (t.mean() - b.mean())), 3), "ci95": [round(float(np.percentile(ret, 2.5)), 3), round(float(np.percentile(ret, 97.5)), 3)]}
        # per-stratum paired CD-L2 - BGE
        for s in sorted({R[i]["stratum"] for i in ids}):
            sub = [i for i in com if R[i]["stratum"] == s]
            out["paired"][f"viewA_{pol} stratum {s}: CD-L2 - BGE"] = paired([va["CD-L2"][i] for i in sub], [va["BGE"][i] for i in sub], B=2000)
    # NIL paired AUROC CD-L2 vs BGE / Tev vs BGE (bootstrap, seed-mean score)
    nil = [i for i in ids if R[i]["cls"] == "NONE"]
    kn = [i for i in ids if R[i]["cls"] in ("MATCH", "PARENT")]
    allid = nil + kn
    yy = np.array([1] * len(nil) + [0] * len(kn))
    sc = {nm: np.mean([[S[m][i]["nil"] for i in allid] for m in STU.get(nm, [nm])], axis=0) for nm in ("BGE", "Tev1-4B", "CD-L2", "CD-L1")}
    for a_, b_ in (("CD-L2", "BGE"), ("CD-L2", "CD-L1"), ("Tev1-4B", "BGE"), ("CD-L2", "Tev1-4B")):
        d = []
        for _ in range(2000):
            ix = rng.randint(0, len(allid), len(allid))
            if len(set(yy[ix])) == 2:
                d.append(roc_auc_score(yy[ix], sc[a_][ix]) - roc_auc_score(yy[ix], sc[b_][ix]))
        out["paired"][f"NIL AUROC: {a_} - {b_}"] = {"diff": round(float(np.mean(d)), 3), "ci95": [round(float(np.percentile(d, 2.5)), 3), round(float(np.percentile(d, 97.5)), 3)]}
    Path(outp).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ("n", "gold_counts")}))
    for k, v in out["systems"].items():
        print(f"{k:8s} A_strict {v['viewA_strict']['acc']} {v['viewA_strict']['ci95']} | A_len {v['viewA_lenient']['acc']} | B_strict {v.get('viewB_strict', {}).get('acc')} | NIL AUROC {v.get('NIL', {}).get('AUROC')} | pool {v['pool_strict_MATCH']} | ms {v['latency_median_ms']}")
    for k, v in out["per_seed"].items():
        print(k, v)
    for k, v in out["paired"].items():
        print(k, v)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "reports/ner_v2/_final_link_scores.json"))
