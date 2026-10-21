#!/usr/bin/env python3
"""Fresh linker gold: the single frozen scoring run (plan: reports/ner_v2/fresh_linker_scoring_plan.md). Reads ONLY stored system outputs + the sealed gold; nothing is tuned.
  python tools/v2dm_fresh_score.py <FRESH_LINKER_GOLD_FINAL.csv> [out_json]"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "reports/ner_v2/_dm_raw"
KEYS = list("ABCDE")
rng = np.random.RandomState(20261021)


def load_systems(gold):
    tasks = {r["mention"]: r for r in (json.loads(l) for l in open(ROOT / "features/v2dm/fresh_tasks_k10.jsonl"))}
    tid = {r["id"]: r for r in tasks.values()}
    ev = json.load(open(ROOT / "reports/ner/_linker_v2_eval.json"))["models"]
    tau = {"BGE": ev["BGE"]["tau_dev"], "E5": ev["E5"]["tau_dev"]}
    e5 = json.load(open(RAW / "fresh_export_e5-large-v2.json"))["scores"]
    ce = {r["id"]: r["scores"] for r in map(json.loads, open(RAW / "ce_fresh_k10.jsonl"))}
    dm = {}
    for nm, f in (("Tev1-4B", "dm_fresh_tev4b_k5.jsonl"), ("Nimble", "dm_fresh_nimble_k5.jsonl")):
        dm[nm] = {r["id"]: r for r in map(json.loads, open(RAW / f))}
    S = {k: {} for k in ("BGE", "E5", "CE", "Tev1-4B", "Nimble")}
    for _, g in gold.iterrows():
        t = tasks[g["mention"]]
        i = t["id"]
        c = t["cands"]
        S["BGE"][i] = {"pick": c[0]["id"], "nil": -c[0]["score"], "none": c[0]["score"] < tau["BGE"], "pool": [x["id"] for x in c[:5]], "ms": None, "failed": False}
        e = e5[g["mention"]]
        S["E5"][i] = {"pick": e[0][0], "nil": -e[0][1], "none": e[0][1] < tau["E5"], "pool": [x[0] for x in e[:5]], "ms": None, "failed": False}
        sc = ce[i]
        S["CE"][i] = {"pick": c[int(np.argmax(sc))]["id"], "nil": -max(sc), "none": None, "pool": [x["id"] for x in c[:10]], "ms": None, "failed": False}
        for nm in ("Tev1-4B", "Nimble"):
            r = dm[nm].get(i)
            if not r or not r["resp"]:
                S[nm][i] = {"pick": None, "nil": np.nan, "none": None, "pool": [x["id"] for x in c[:5]], "ms": None, "failed": True}
                continue
            a = r["resp"]["answers"]["link"]
            p = a["probabilities"]
            best = max(KEYS, key=lambda k: p.get(k, 0))
            S[nm][i] = {"pick": c[KEYS.index(best)]["id"], "nil": p.get("NONE", 0.0), "none": a["choice"] == "NONE", "pool": [x["id"] for x in c[:5]], "ms": r["ms"], "failed": False,
                        "default_pick": (c[KEYS.index(a["choice"])]["id"] if a["choice"] in KEYS else "NONE")}
    return S


def gold_sets(g):
    cls, con = g["final_class"], g["final_concept"]
    amb = set(re.findall(r"ING-\d{6}", str(g["final_readings"]))) if cls == "AMBIGUOUS" else set()
    return cls, con, amb


def ci(x, B=5000):
    x = np.asarray(x, float)
    b = [x[rng.randint(0, len(x), len(x))].mean() for _ in range(B)]
    return [round(float(np.percentile(b, 2.5)), 3), round(float(np.percentile(b, 97.5)), 3)]


def paired(a, b, B=5000):
    d = np.asarray(a, float) - np.asarray(b, float)
    bs = [d[rng.randint(0, len(d), len(d))].mean() for _ in range(B)]
    n10, n01 = int(((np.asarray(a) == 1) & (np.asarray(b) == 0)).sum()), int(((np.asarray(a) == 0) & (np.asarray(b) == 1)).sum())
    from scipy.stats import binomtest
    p = binomtest(n10, n10 + n01, 0.5).pvalue if n10 + n01 else 1.0
    return {"diff": round(float(d.mean()), 3), "ci95": [round(float(np.percentile(bs, 2.5)), 3), round(float(np.percentile(bs, 97.5)), 3)], "mcnemar_exact_p": round(float(p), 4), "n": int(len(d))}


def main(gp, outp):
    G = pd.read_csv(gp, dtype=str, keep_default_na=False)
    assert len(G) == 441 and G.item_id.is_unique
    S = load_systems(G)
    rows = []
    for _, g in G.iterrows():
        cls, con, amb = gold_sets(g)
        rows.append({"id": g["item_id"], "cls": cls, "con": con, "amb": amb, "stratum": g["stratum"].split("_")[0], "mention": g["mention"], "kconf": int(g["kush_conf"]), "pconf": int(g["parv_conf"]),
                     "npool": sum(1 for c in G.columns if c.startswith("cand_") and g[c] != "")})
    ids = [r["id"] for r in rows]
    R = {r["id"]: r for r in rows}
    n_amb_set = sum(1 for r in rows if r["cls"] == "AMBIGUOUS" and r["amb"])
    out = {"n": len(rows), "gold_counts": pd.Series([r["cls"] for r in rows]).value_counts().to_dict(), "ambiguous_with_explicit_answer_set": n_amb_set, "systems": {}, "paired": {}}
    # correctness vectors
    def viewA(sys_, policy):
        idx, corr = [], []
        for i in ids:
            r = R[i]
            ok_cls = ("MATCH",) if policy == "strict" else ("MATCH", "PARENT")
            if r["cls"] in ok_cls:
                idx.append(i)
                corr.append(int(S[sys_][i]["pick"] == r["con"]) if S[sys_][i]["pick"] else 0)
            elif r["cls"] == "AMBIGUOUS" and r["amb"]:
                idx.append(i)
                corr.append(int(S[sys_][i]["pick"] in r["amb"]) if S[sys_][i]["pick"] else 0)
        return idx, np.array(corr)

    def viewB(sys_, policy):
        idx, corr = [], []
        for i in ids:
            r = R[i]
            s = S[sys_][i]
            if s["none"] is None or s["failed"]:
                continue
            if r["cls"] == "NONE":
                idx.append(i)
                corr.append(int(bool(s["none"])))
            elif r["cls"] == "MATCH" or (policy == "lenient" and r["cls"] == "PARENT"):
                pk = s.get("default_pick", s["pick"]) if sys_ in ("Tev1-4B", "Nimble") else (s["pick"] if not s["none"] else "NONE")
                idx.append(i)
                corr.append(int(pk == r["con"]))
        return idx, np.array(corr)

    for sys_ in S:
        o = {}
        for pol in ("strict", "lenient"):
            ia, ca = viewA(sys_, pol)
            o[f"viewA_{pol}"] = {"n": len(ia), "acc": round(float(ca.mean()), 3), "ci95": ci(ca)}
            ib, cb = viewB(sys_, pol)
            if len(ib):
                o[f"viewB_{pol}"] = {"n": len(ib), "acc": round(float(cb.mean()), 3), "ci95": ci(cb)}
        pk = [S[sys_][i]["pick"] for i in ids]
        o["PARENT_items"] = {"n": sum(R[i]["cls"] == "PARENT" for i in ids), "picked_the_parent_concept": sum(1 for i in ids if R[i]["cls"] == "PARENT" and S[sys_][i]["pick"] == R[i]["con"])}
        o["ambiguous_total"] = sum(R[i]["cls"] == "AMBIGUOUS" for i in ids)
        # NIL view C
        known = [i for i in ids if R[i]["cls"] in ("MATCH", "PARENT")]
        nil = [i for i in ids if R[i]["cls"] == "NONE"]
        sc = np.array([S[sys_][i]["nil"] for i in nil + known], float)
        y = np.array([1] * len(nil) + [0] * len(known))
        ok = ~np.isnan(sc)
        if ok.sum() and len(set(y[ok])) == 2:
            o["NIL"] = {"AUROC": round(float(roc_auc_score(y[ok], sc[ok])), 3), "AUPRC": round(float(average_precision_score(y[ok], sc[ok])), 3), "n_NONE": len(nil), "n_known": len(known)}
            if S[sys_][ids[0]]["none"] is not None:
                dn = np.array([S[sys_][i]["none"] for i in nil + known], float)
                rec, fn = float(dn[y == 1].mean()), float(dn[y == 0].mean())
                o["NIL"].update({"operating_point": "frozen (BGE/E5 dev tau; Tev/Nimble default NONE choice)", "NIL_recall": round(rec, 3), "false_NONE_rate_on_known": round(fn, 3), "specificity": round(1 - fn, 3), "balanced_acc": round(0.5 * (rec + 1 - fn), 3)})
        # retrieval vs reranking
        pool_ok = {}
        for pol in ("strict", "lenient"):
            tot = inpool = right = 0
            for i in ids:
                r = R[i]
                gold = {r["con"]} if r["cls"] == "MATCH" or (pol == "lenient" and r["cls"] == "PARENT") else None
                if gold is None:
                    continue
                tot += 1
                p = set(S[sys_][i]["pool"])
                inpool += bool(gold & p)
                right += S[sys_][i]["pick"] in gold
            o[f"pool_{pol}"] = {"n": tot, "oracle": round(inpool / tot, 3), "acc": round(right / tot, 3), "retrieval_failures": tot - inpool, "reranking_failures": inpool - right}
        ms = [S[sys_][i]["ms"] for i in ids if S[sys_][i]["ms"] is not None]
        o["latency_median_ms"] = round(float(np.median(ms)), 1) if ms else None
        o["failed_calls"] = int(sum(S[sys_][i]["failed"] for i in ids))
        # strata (view A strict)
        ia, ca = viewA(sys_, "strict")
        cm = dict(zip(ia, ca))
        o["viewA_strict_by_stratum"] = {s: {"n": sum(1 for i in ia if R[i]["stratum"] == s), "acc": (round(float(np.mean([cm[i] for i in ia if R[i]["stratum"] == s])), 3) if any(R[i]["stratum"] == s for i in ia) else None)} for s in sorted({r["stratum"] for r in rows})}
        o["viewA_strict_by_human_conf"] = {g: {"n": sum(1 for i in ia if (R[i]["kconf"] == 3 and R[i]["pconf"] == 3) == (g == "both_3")), "acc": (round(float(np.mean([cm[i] for i in ia if (R[i]["kconf"] == 3 and R[i]["pconf"] == 3) == (g == "both_3")])), 3) if any((R[i]["kconf"] == 3 and R[i]["pconf"] == 3) == (g == "both_3") for i in ia) else None)} for g in ("both_3", "lower")}
        o["viewA_strict_by_mention_len"] = {g: {"n": sum(1 for i in ia if (len(R[i]["mention"].split()) <= 2) == (g == "<=2 tokens")), "acc": (round(float(np.mean([cm[i] for i in ia if (len(R[i]["mention"].split()) <= 2) == (g == "<=2 tokens")])), 3) if any((len(R[i]["mention"].split()) <= 2) == (g == "<=2 tokens") for i in ia) else None)} for g in ("<=2 tokens", ">=3 tokens")}
        out["systems"][sys_] = o
    # paired differences on View A
    for pol in ("strict", "lenient"):
        va = {s: dict(zip(*viewA(s, pol))) for s in S}
        common = sorted(set.intersection(*[set(v) for v in va.values()]))
        for a_, b_ in (("Tev1-4B", "BGE"), ("Tev1-4B", "CE"), ("Tev1-4B", "E5"), ("Nimble", "BGE"), ("Nimble", "CE"), ("Nimble", "Tev1-4B"), ("CE", "BGE")):
            out["paired"][f"viewA_{pol}: {a_} - {b_}"] = paired([va[a_][i] for i in common], [va[b_][i] for i in common])
    # reranker efficiency
    out["reranker_efficiency"] = {}
    for pol in ("strict", "lenient"):
        b = out["systems"]["BGE"][f"pool_{pol}"]
        for nm in ("Tev1-4B", "Nimble"):
            s = out["systems"][nm][f"pool_{pol}"]
            den = s["oracle"] - b["acc"]
            out["reranker_efficiency"][f"{nm} ({pol})"] = round((s["acc"] - b["acc"]) / den, 3) if den > 0 else None
    # NIL paired AUROC difference (Tev vs BGE) by bootstrap
    nil_ids = [i for i in ids if R[i]["cls"] == "NONE"]
    kn_ids = [i for i in ids if R[i]["cls"] in ("MATCH", "PARENT")]
    if nil_ids and kn_ids:
        yy = np.array([1] * len(nil_ids) + [0] * len(kn_ids))
        allid = nil_ids + kn_ids
        def auc(sys_, idx):
            s = np.array([S[sys_][allid[j]]["nil"] for j in idx])
            return roc_auc_score(yy[idx], s) if len(set(yy[idx])) == 2 and not np.isnan(s).any() else np.nan
        for a_, b_ in (("Tev1-4B", "BGE"), ("Nimble", "BGE"), ("Tev1-4B", "CE")):
            d = []
            for _ in range(2000):
                idx = rng.randint(0, len(allid), len(allid))
                v = auc(a_, idx) - auc(b_, idx)
                if not np.isnan(v):
                    d.append(v)
            out["paired"][f"NIL AUROC: {a_} - {b_}"] = {"diff": round(float(np.mean(d)), 3), "ci95": [round(float(np.percentile(d, 2.5)), 3), round(float(np.percentile(d, 97.5)), 3)]} if d else None
    Path(outp).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ("n", "gold_counts", "ambiguous_with_explicit_answer_set", "reranker_efficiency")}, indent=1))
    for k, v in out["systems"].items():
        print(k, "A_strict", v["viewA_strict"], "A_lenient", v["viewA_lenient"], "NIL", v.get("NIL", {}).get("AUROC"))
    for k, v in out["paired"].items():
        print(k, v)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "reports/ner_v2/_fresh_linker_scores.json"))
