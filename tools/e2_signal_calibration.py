#!/usr/bin/env python3
"""S126 E2b (laptop): do linker / lexical / rule signals add information beyond the span model's own confidence? DEV only; TEST and CALIBRATION never read.
Successor of e2_linker_calibration.py (S125, kept for reproducibility): adds RecipeDB3, G1 ledger aliases, M7 rule agreement, combos, per-linker tags.

  python tools/e2_signal_calibration.py <ds> surfaces                                           # FOOD-span surfaces -> features/span_surfaces_<ds>.json
  python tools/e2_signal_calibration.py <ds> run <export.json> <tag> <kinds> <nboot> [<pairs>]   # kinds "P0,C,M1,..."; pairs "G1:M6,M1+M6:M6" = cand:base extra comparisons

Baseline P0 = calibrated logit(span confidence). Every feature block is added to P0 alone ("+" joins blocks for the redundancy stage). Calibrator = router.fit_calibrator (logreg + isotonic)
fit on OOF train-span rows only. Blocks: M1 linker top-1 cosine (FOOD) | M2 margin+entropy (FOOD) | M5 log count + unseen flag | M6 train-gazetteer exact+fuzzy (=G0) |
G1 external-ledger alias agreement (FOOD) | G2 = M6+G1 | M7 rule agreement (lexicon / form / neighbour compatibility, inference-time only) | M3, M4 rejected (reference).
Pre-declared scope: M1, M2, G1 = FOOD spans; M7 = rule-covered types; M5, M6, G2 = all spans. Rule: PROMOTE = Holm-significant NLL gain in scope AND dAURC <= 0 AND dECE <= +0.01 AND
unseen-stratum NLL not worse; REJECT = dNLL > -0.002 or significantly worse; else INCONCLUSIVE. Ledger/rule lexicons use no benchmark labels and no gold types."""
import json
import pickle
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import e1_e2_calibration as E  # noqa: E402
from build_linker_data import norm  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402
from culinarystate.ner import spans as S  # noqa: E402
from culinarystate.process.vocab import BY_CANON, map_step_name  # noqa: E402
from culinarystate.quantity.units import UNITS  # noqa: E402

RAW = E.RAW
TEMP = 0.05                                                        # linker training temperature, used for the top-K softmax entropy
FOOD = {"tasteset": "FOOD", "recipedb3": "NAME"}
NUM = re.compile(r"^(?:\d+(?:[./]\d+)?|\d+\s+\d+/\d+|\d+\s*(?:-|to)\s*\d+(?:/\d+)?|[¼½¾⅓⅔⅛]|a|an|one|two|three|four|five|six|half|few|several|some|dozen)$")
TEMPRE = re.compile(r"\d+\s*(?:°|º|degrees?|deg|f\b|c\b)|\bgas mark\b|\bdegrees?\b")
SCOPE = {"M1": "food", "M2": "food", "G1": "food", "M7": "r7", "M5": "all", "M6": "all", "G2": "all"}


def collect(ds, stem="deberta-base_crf"):
    """Span rows for the 5 OOF train folds and DEV (cached; external-knowledge features are added afterwards)."""
    cache = ROOT / "features" / f"rowcache_{ds}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    sp, docs, labels = E.load(ds)
    tr_idx = sp["train"]
    tr_docs = docs(tr_idx)
    fold = np.random.RandomState(0).permutation(len(tr_idx)) % 5
    oof = []
    for k in range(5):
        pred = json.load(open(RAW / f"{ds}__{stem}_oof{k}__seed1.pred.json"))["oof"]
        conf = json.load(open(RAW / f"{ds}__{stem}_oof{k}__seed1.conf.json"))["oof"]
        held = [i for i in range(len(tr_idx)) if fold[i] == k]
        gz = S.Gazetteer.build((tr_docs[i] for i in range(len(tr_idx)) if fold[i] != k), labels)
        oof += rows([tr_docs[i] for i in held], pred, conf, gz, labels, held, f"oof{k}")
    full = S.Gazetteer.build(tr_docs, labels)
    pred_all = json.load(open(RAW / f"{ds}__{stem}__seed1.pred.json"))
    conf_all = json.load(open(RAW / f"{ds}__{stem}__seed1.conf.json"))
    dev = rows(docs(sp["dev"]), pred_all["dev"], conf_all["dev"], full, labels, list(range(len(sp["dev"]))), "dev")
    out = (oof, dev, labels)
    cache.parent.mkdir(exist_ok=True)
    cache.write_bytes(pickle.dumps(out))
    return out


def rows(docs_part, preds, confs, gz, labels, groups, part):
    out, memo = [], {}
    for k, ((text, gold), pr, cf) in enumerate(zip(docs_part, preds, confs)):
        g = {tuple(x) for x in gold}
        order = sorted(range(len(pr)), key=lambda j: pr[j][0])
        pos = {j: i for i, j in enumerate(order)}
        for j, ((s, e, lab, *_), c) in enumerate(zip(pr, cf)):
            surf = text[s:e]
            if surf.lower() not in memo:
                memo[surf.lower()] = gz.features(surf)
            f = memo[surf.lower()]
            li = labels.index(lab)
            i = pos[j]
            nx = pr[order[i + 1]] if i + 1 < len(order) else None
            pv = pr[order[i - 1]] if i > 0 else None
            out.append({"conf": c, "y": int((s, e, lab) in g), "lab": li, "lab_s": lab, "len": len(surf.split()), "norm": norm(surf), "n": float(np.expm1(f[4 * li + 1])),
                        "exact": float(f[4 * li]), "fuzzy": float(f[4 * li + 2]), "group": groups[k], "part": part,
                        "nxt": (nx[2], len(text[e:nx[0]].split())) if nx else None, "prv": (pv[2], len(text[pv[1]:s].split())) if pv else None})
    return out


def surfaces(ds):
    oof, dev, _ = collect(ds)
    ss = sorted({r["norm"] for r in oof + dev if r["lab_s"] == FOOD[ds] and r["norm"]})
    (ROOT / "features").mkdir(exist_ok=True)
    (ROOT / "features" / f"span_surfaces_{ds}.json").write_text(json.dumps(ss))
    print(len(ss), "unique FOOD-span surfaces ->", f"features/span_surfaces_{ds}.json")


# ---------------------------------------------------------------- external knowledge (no benchmark labels, no gold types)
def ledger_maps():
    st = LedgerStore()
    ings = {i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    led = {}
    for i in st.all_latest("ING"):
        if i["status"] == "ACTIVE":
            led.setdefault(norm(i["canonical_name"]), set()).add(i["id"])
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") in ings and norm(a["normalized"]):
            led.setdefault(norm(a["normalized"]), set()).add(a["ingredient_id"])
    toks = {t for s in led for t in s.split()}
    heads = {s.split()[-1] for s in led if s}
    units = {norm(a) for u in UNITS for a in u.aliases if norm(a)}
    return led, toks, heads, units


def cat_map():
    D = json.loads((ROOT / "features/linker_data_v1.json").read_text())
    m = {}
    for qs in D["queries"].values():
        for q in qs:
            if q.get("cat") and q["ing"] not in m:
                m[q["ing"]] = q["cat"]
    return m, {s for s, _ in D["train_gallery"]}


def add_features(rs, ds, ex, cats, K):
    led, toks, heads, units = K
    fl = FOOD[ds]
    for r in rs:
        s, lab = r["norm"], r["lab_s"]
        t = s.split()
        if lab == fl and s in ex:                                                       # M1/M2/M3: linker
            sc = ex[s]
            v = np.array([x for _, x in sc])
            p = np.exp((v - v.max()) / TEMP)
            p /= p.sum()
            r["lf"] = {"app": 1.0, "top1": float(v[0]), "margin": float(v[0] - v[1]), "ent": float(-(p * np.log(p + 1e-12)).sum() / np.log(len(p))), "cat": cats.get(sc[0][0], "UNK")}
        else:
            r["lf"] = {"app": 0.0, "top1": 0.0, "margin": 0.0, "ent": 0.0, "cat": "NA"}
        pc = map_step_name(s) if lab == "PROCESS" else None
        r["pf"] = "NA" if lab != "PROCESS" else (BY_CANON[pc].family if pc in BY_CANON else "UNMAPPED")
        if lab == fl and t:                                                             # G1: external ledger alias agreement (FOOD spans)
            r["lg"] = {"app": 1.0, "exact": float(s in led), "amb": float(len(led.get(s, ())) > 1), "head": float(t[-1] in heads), "tokfrac": float(np.mean([w in toks for w in t]))}
        else:
            r["lg"] = {"app": 0.0, "exact": 0.0, "amb": 0.0, "head": 0.0, "tokfrac": 0.0}
        in_food, in_unit, in_proc = (s in led or (bool(t) and t[-1] in heads)), (s in units or any(w in units for w in t)), map_step_name(s) is not None   # M7
        app = 1.0
        if lab == fl:
            m, oth = in_food, in_unit or in_proc
        elif lab == "QUANTITY":
            m, oth = bool(NUM.match(s)), in_food
        elif lab == "UNIT":
            m, oth = in_unit, in_food
        elif lab == "PROCESS":
            m, oth = in_proc, in_food or in_unit
        elif lab == "TEMP":
            m, oth = bool(TEMPRE.search(s)), False
        else:
            app, m, oth = 0.0, False, False
        nl, pl = r["nxt"], r["prv"]
        comp = 0.0
        if lab == "QUANTITY" and nl and nl[0] in ("UNIT", fl) and nl[1] <= 2:
            comp = 1.0
        if lab == "UNIT" and ((pl and pl[0] == "QUANTITY" and pl[1] <= 2) or (nl and nl[0] == fl and nl[1] <= 2)):
            comp = 1.0
        if lab == fl and ((pl and pl[0] in ("UNIT", "QUANTITY") and pl[1] <= 2) or (nl and nl[0] in ("PROCESS", "STATE", "DF") and nl[1] <= 1)):
            comp = 1.0
        r["r7"] = {"app": app, "match": float(m) * app, "conflict": float(oth and not m) * app, "compat": comp * app}


def blocks(rs, b, spec):
    f = lambda d, k: np.array([r[d][k] for r in rs], float)
    if b == "C":
        return [np.array([r["len"] for r in rs], float)] + list(np.eye(spec["nlab"])[[r["lab"] for r in rs]].T)
    if b == "M1":
        return [f("lf", "app"), f("lf", "top1")]
    if b == "M2":
        return [f("lf", "app"), f("lf", "margin"), f("lf", "ent")]
    if b == "M3":
        return [np.array([float(r["lf"]["cat"] == c) for r in rs]) for c in spec["cats"]]
    if b == "M4":
        return [np.array([float(r["pf"] == c) for r in rs]) for c in spec["fams"]]
    if b == "M5":
        return [np.log1p([r["n"] for r in rs]), np.array([float(r["n"] == 0) for r in rs])]
    if b == "M6":
        return [np.array([r["exact"] for r in rs]), np.array([r["fuzzy"] for r in rs])]
    if b == "G1":
        return [f("lg", k) for k in ("app", "exact", "amb", "head", "tokfrac")]
    if b == "M7":
        return [f("r7", k) for k in ("app", "match", "conflict", "compat")]
    if b == "P0":
        return []
    raise ValueError(b)


def design(rs, kind, spec):
    cols = [E.logit([r["conf"] for r in rs])]
    for b in kind.split("+"):
        cols += blocks(rs, b, spec)
    return np.stack([np.asarray(c, float) for c in cols], axis=1)


def scaler(X):
    mu, sd = X.mean(0), X.std(0)
    sd[sd < 1e-9] = 1.0
    return lambda Z: (Z - mu) / sd


def nll(p, y):
    p = np.clip(p, 1e-3, 1 - 1e-3)                                  # isotonic outputs hit 0/1; clip so one confident error cannot dominate NLL
    return float(-np.mean(np.where(y == 1, np.log(p), np.log(1 - p))))


def _tie_curve(s, y):
    """expected cumulative errors at each rank under RANDOM tie-breaking (span-confidence scores are heavily quantised: P0 has ~250 distinct values on 3k spans)."""
    u, inv = np.unique(-s, return_inverse=True)                      # ascending of -s = descending score
    m = np.bincount(inv).astype(float)
    e = np.bincount(inv, weights=1.0 - y)
    prev_n, prev_e = np.concatenate([[0.0], np.cumsum(m)[:-1]]), np.concatenate([[0.0], np.cumsum(e)[:-1]])
    j = np.arange(len(s)) - np.repeat(prev_n, m.astype(int)) + 1.0         # 1-based rank inside the tie group
    gm = np.repeat(np.arange(len(m)), m.astype(int))
    return np.repeat(prev_n, m.astype(int)) + j, prev_e[gm] + e[gm] * j / m[gm]


def aurc(s, y):
    pos, cum = _tie_curve(s, y)
    return float((cum / pos).mean())


def pcov(s, y, c):
    pos, cum = _tie_curve(s, y)
    k = max(1, int(round(c * len(s))))
    return float(1.0 - cum[k - 1] / k)


def fm(p, s, y):
    """p = calibrated probability (NLL / Brier / ECE); s = continuous pre-isotonic score (AURC / precision@coverage: isotonic plateaus make ranking metrics tie-order dependent)."""
    if len(y) == 0:
        return {"n": 0}
    m = E.metrics(p, y)
    return {"nll": round(nll(p, y), 5), "brier": round(m["brier"], 5), "ece": round(m["ece"], 5), "aurc": round(aurc(s, y), 5), "prec@80": round(pcov(s, y, 0.8), 4),
            "prec@90": round(pcov(s, y, 0.9), 4), "prec@95": round(pcov(s, y, 0.95), 4), "n": int(len(y))}


def fast(p, s, y):
    return {"nll": nll(p, y), "aurc": aurc(s, y), "ece": E.metrics(p, y)["ece"], "prec@90": pcov(s, y, 0.9)}


def boot(pa, sa, pb, sb, y, groups, n, seed=7):
    g = np.asarray(groups)
    ug = np.unique(g)
    idx = {k: np.where(g == k)[0] for k in ug}
    rng = random.Random(seed)
    d = {"nll": [], "ece": [], "aurc": [], "prec@90": []}
    for _ in range(n):
        s = np.concatenate([idx[ug[rng.randrange(len(ug))]] for _ in ug])
        ma, mb = fast(pa[s], sa[s], y[s]), fast(pb[s], sb[s], y[s])
        for k in d:
            d[k].append(ma[k] - mb[k])
    A, B = fast(pa, sa, y), fast(pb, sb, y)
    return {k: {"delta": float(A[k] - B[k]), "lo": float(np.percentile(v, 2.5)), "hi": float(np.percentile(v, 97.5)), "p": float(max(2 * min(np.mean(np.array(v) <= 0), np.mean(np.array(v) >= 0)), 1.0 / n))}
            for k, v in d.items()}


def validate(oof, dev, ex, surf_train, ds):
    rep = {}
    for name, rs in (("oof_train", oof), ("dev", dev)):
        fr = [r for r in rs if r["lab_s"] == FOOD[ds]]
        top1 = np.array([r["lf"]["top1"] for r in fr if r["lf"]["app"]])
        rep[name] = {"n_spans": len(rs), "n_food": len(fr), "missing_predictions": sum(r["norm"] not in ex for r in fr),
                     "linker_train_surface_exact_overlap": round(float(np.mean([r["norm"] in surf_train for r in fr])), 4),
                     "top1_cos_quantiles": [round(float(np.quantile(top1, q)), 3) for q in (0.05, 0.25, 0.5, 0.75, 0.95)],
                     "frac_top1_below_0.8": round(float(np.mean(top1 < 0.8)), 4),
                     "mean_top1_span_correct": round(float(np.mean([r["lf"]["top1"] for r in fr if r["y"]])), 4),
                     "mean_top1_span_wrong": round(float(np.mean([r["lf"]["top1"] for r in fr if not r["y"]])), 4)}
    return rep


def run(ds, export, tag, kinds, pairs, nb):
    from culinarystate.ner.router import holm
    oof, dev, labels = collect(ds)
    ex = json.loads(Path(export).read_text())["scores"]
    cats, surf_train = cat_map()
    K = ledger_maps()
    add_features(oof, ds, ex, cats, K)
    add_features(dev, ds, ex, cats, K)
    val = validate(oof, dev, ex, surf_train, ds)
    spec = {"nlab": len(labels), "cats": sorted({r["lf"]["cat"] for r in oof if r["lf"]["cat"] != "NA"}), "fams": sorted({r["pf"] for r in oof if r["pf"] != "NA"})}
    yo, yd = np.array([r["y"] for r in oof]), np.array([r["y"] for r in dev])
    gd = np.array([r["group"] for r in dev])
    mask = {"all": np.ones(len(dev), bool), "food": np.array([r["lab_s"] == FOOD[ds] for r in dev]), "r7": np.array([r["r7"]["app"] > 0 for r in dev])}
    unseen = np.array([r["n"] == 0 for r in dev])
    tail = np.array([1 <= r["n"] <= 2 for r in dev])
    preds, scores = {}, {}
    for kind in sorted(set(kinds) | {c for pr in pairs for c in pr}):
        kk = "M6+G1" if kind == "G2" else kind
        Xo, Xd = design(oof, kk, spec), design(dev, kk, spec)
        sc = scaler(Xo)
        model, iso, _ = R.fit_calibrator(sc(Xo), yo)
        preds[kind] = R.calibrated(model, iso, sc(Xd))
        scores[kind] = model.predict_proba(sc(Xd))[:, 1]
    res = {}
    for k in preds:
        res[k] = {s_: fm(preds[k][m], scores[k][m], yd[m]) for s_, m in mask.items()}
        for nm, m in (("unseen_all", unseen), ("tail_all", tail), ("unseen_food", unseen & mask["food"]), ("tail_food", tail & mask["food"])):
            res[k][nm] = fm(preds[k][m], scores[k][m], yd[m])
    cmps, prim = {}, []
    todo = [(k, "P0", SCOPE.get(k, "all")) for k in kinds if k not in ("P0", "C") and "+" not in k] + [(c, b, s_) for c, b in pairs for s_ in ("all", "food")]
    for c, b, s_ in todo:
        m = mask[s_]
        d = boot(preds[c][m], scores[c][m], preds[b][m], scores[b][m], yd[m], gd[m], nb)
        su, st = m & unseen, m & tail
        key = f"{c}|vs|{b}|{s_}"
        cmps[key] = {**d, "unseen_nll_delta": (nll(preds[c][su], yd[su]) - nll(preds[b][su], yd[su])) if su.sum() > 20 else None,
                     "tail_nll_delta": (nll(preds[c][st], yd[st]) - nll(preds[b][st], yd[st])) if st.sum() > 20 else None, "n": int(m.sum()), "n_unseen": int(su.sum()), "n_tail": int(st.sum())}
        if b == "P0" and (c, b, s_) in todo[:len([k for k in kinds if k not in ("P0", "C") and "+" not in k])]:
            prim.append(key)
    for k, sig in zip(prim, holm([cmps[k]["nll"]["p"] for k in prim])):
        c = cmps[k]
        dn, du = c["nll"]["delta"], c["unseen_nll_delta"]
        c["holm_sig"] = bool(sig)
        c["decision"] = ("PROMOTE" if sig and dn < 0 and c["aurc"]["delta"] <= 0 and c["ece"]["delta"] <= 0.01 and (du is None or du <= 0)
                         else "REJECT" if dn > -0.002 or (sig and dn > 0) else "INCONCLUSIVE")
    out = {"dataset": ds, "tag": tag, "baseline": "P0 = calibrated logit(span conf)", "validation": val, "n_oof": len(oof), "n_dev": len(dev), "n_dev_docs": int(len(set(gd))),
           "n_food_dev": int(mask["food"].sum()), "n_unseen_dev": int(unseen.sum()), "n_tail_dev": int(tail.sum()), "results": res, "comparisons": cmps}
    (ROOT / "reports" / "ner" / f"_e2b_{ds}_{tag}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(val))
    print("dev docs", out["n_dev_docs"], "food", out["n_food_dev"], "unseen", out["n_unseen_dev"], "tail", out["n_tail_dev"])
    for k in ("P0", "C"):
        if k in res:
            print(k, "ALL", res[k]["all"], "FOOD", res[k]["food"])
    for k, c in cmps.items():
        f4 = lambda x: "NA" if x is None else f"{x:+.4f}"
        print(f"{k}: dNLL {c['nll']['delta']:+.4f} [{c['nll']['lo']:+.4f},{c['nll']['hi']:+.4f}] p={c['nll']['p']:.3f} dAURC {c['aurc']['delta']:+.5f} [{c['aurc']['lo']:+.5f},{c['aurc']['hi']:+.5f}] "
              f"dECE {c['ece']['delta']:+.4f} dP90 {c['prec@90']['delta']:+.4f} unseen {f4(c['unseen_nll_delta'])} tail {f4(c['tail_nll_delta'])} n={c['n']} {c.get('decision', '')}")


if __name__ == "__main__":
    ds, mode = sys.argv[1], sys.argv[2]
    if mode == "surfaces":
        surfaces(ds)
    else:
        pr = [tuple(p.split(":")) for p in sys.argv[7].split(",")] if len(sys.argv) > 7 and sys.argv[7] else []
        run(ds, sys.argv[3], sys.argv[4], sys.argv[5].split(","), pr, int(sys.argv[6]))
