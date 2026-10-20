#!/usr/bin/env python3
"""S120 E2 (laptop): do linker-derived signals add information beyond the span model's own confidence? DEV only; TEST and CALIBRATION never read here.

  python tools/e2_linker_calibration.py tasteset surfaces            # -> features/span_surfaces_<ds>.json (FOOD-span surfaces; goes to the A100 linker export)
  python tools/e2_linker_calibration.py tasteset run <export.json>   # validates the OOF artefact, then feature-by-feature calibration -> reports/ner/_e2_linker_<ds>.json

Baseline P0 = [logit(span conf)] (calibrated); C = P0 + label one-hot + length is reported as a nuisance control; every feature block is added to P0 ALONE (no combination). Calibrator = router.fit_calibrator (logreg + isotonic)
fit on OOF train-span rows only; evaluation on DEV spans. The linker is trained on ledger surfaces only (no benchmark document), so one frozen linker scores every split;
fold-leakage is checked empirically (linker-train-surface overlap per split) rather than assumed.
Pre-declared decision rule (per feature vs P0, Holm over features on dNLL): PROMOTE = Holm-significant NLL gain AND dAURC <= 0 AND dECE <= +0.01 AND unseen-stratum NLL not worse;
REJECT = dNLL > -0.002 (no meaningful gain) or significantly worse; else INCONCLUSIVE."""
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import e1_e2_calibration as E  # noqa: E402
from build_linker_data import norm  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402
from culinarystate.ner import spans as S  # noqa: E402
from culinarystate.process.vocab import BY_CANON, map_step_name  # noqa: E402

RAW = E.RAW
TEMP = 0.05                                                        # linker training temperature, used for the top-K softmax entropy
FOOD = {"tasteset": "FOOD", "recipedb3": "NAME"}


def collect(ds, stem="deberta-base_crf"):
    """Span rows for the 5 OOF train folds and DEV, with surface text, label, gazetteer slot, doc group."""
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
    return oof, dev, labels


def rows(docs_part, preds, confs, gz, labels, groups, part):
    out = []
    for k, ((text, gold), pr, cf) in enumerate(zip(docs_part, preds, confs)):
        g = {tuple(x) for x in gold}
        for (s, e, lab, *_), c in zip(pr, cf):
            surf = text[s:e]
            f = gz.features(surf)
            li = labels.index(lab)
            out.append({"conf": c, "y": int((s, e, lab) in g), "lab": li, "lab_s": lab, "len": len(surf.split()), "norm": norm(surf), "gaz": f,
                        "n": float(np.expm1(f[4 * li + 1])), "exact": f[4 * li], "fuzzy": f[4 * li + 2], "group": groups[k], "part": part})
    return out


def surfaces(ds):
    oof, dev, _ = collect(ds)
    ss = sorted({r["norm"] for r in oof + dev if r["lab_s"] == FOOD[ds] and r["norm"]})
    Path(ROOT / "features").mkdir(exist_ok=True)
    (ROOT / "features" / f"span_surfaces_{ds}.json").write_text(json.dumps(ss))
    print(len(ss), "unique FOOD-span surfaces ->", f"features/span_surfaces_{ds}.json")


# ---------------------------------------------------------------- feature blocks
def cat_map():
    D = json.loads((ROOT / "features/linker_data_v1.json").read_text())
    m = {}
    for qs in D["queries"].values():
        for q in qs:
            if q.get("cat") and q["ing"] not in m:
                m[q["ing"]] = q["cat"]
    surf_train = {s for s, _ in D["train_gallery"]}
    return m, surf_train, {s for s, _ in D["full_gallery_seen_concepts"]}


def link_feats(r, ex, cats, ds):
    """linker features for one row; non-FOOD spans -> applicable flag 0 and zeros."""
    if r["lab_s"] != FOOD[ds] or r["norm"] not in ex:
        return {"app": 0.0, "top1": 0.0, "margin": 0.0, "ent": 0.0, "cat": "NA", "nil": 0.0, "top": []}
    sc = ex[r["norm"]]
    v = np.array([s for _, s in sc])
    p = np.exp((v - v.max()) / TEMP)
    p /= p.sum()
    return {"app": 1.0, "top1": float(v[0]), "margin": float(v[0] - v[1]), "ent": float(-(p * np.log(p + 1e-12)).sum() / np.log(len(p))),
            "cat": cats.get(sc[0][0], "UNK"), "nil": 1.0 - float(v[0]), "top": [c for c, _ in sc]}


def proc_family(r):
    if r["lab_s"] != "PROCESS":
        return "NA"
    c = map_step_name(r["norm"])
    return BY_CANON[c].family if c in BY_CANON else "UNMAPPED"


def design(rs, kind, spec):
    """spec holds fitted vocab/scaling so OOF and DEV share columns."""
    lg = E.logit([r["conf"] for r in rs])
    cols = [lg]
    if kind == "C":                                                # nuisance control: label identity + length, no semantic signal
        cols += [np.array([r["len"] for r in rs], float)] + list(np.eye(spec["nlab"])[[r["lab"] for r in rs]].T)
    f = lambda k: np.array([r["lf"][k] for r in rs], float)
    if kind == "M1":
        cols += [f("app"), f("top1"), f("nil") * f("app")]
    if kind == "M2":
        cols += [f("app"), f("margin"), f("ent")]
    if kind == "M3":
        cols += [np.array([float(r["lf"]["cat"] == c) for r in rs]) for c in spec["cats"]]
    if kind == "M4":
        cols += [np.array([float(r["pf"] == c) for r in rs]) for c in spec["fams"]]
    if kind == "M5":
        cols += [np.log1p([r["n"] for r in rs]), np.array([float(r["n"] == 0) for r in rs])]
    if kind == "M6":
        cols += [np.array([r["exact"] for r in rs], float), np.array([r["fuzzy"] for r in rs], float)]
    X = np.stack([np.asarray(c, float) for c in cols], axis=1)
    return X


def scaler(X):
    mu, sd = X.mean(0), X.std(0)
    sd[sd < 1e-9] = 1.0
    return lambda Z: (Z - mu) / sd


# ---------------------------------------------------------------- metrics
def nll(p, y):
    p = np.clip(p, 1e-3, 1 - 1e-3)                                  # isotonic outputs hit 0/1; clip so one confident error cannot dominate NLL
    return float(-np.mean(np.where(y == 1, np.log(p), np.log(1 - p))))


def aurc(p, y):
    o = np.argsort(-p)
    c = np.cumsum(1 - y[o]) / np.arange(1, len(y) + 1)
    return float(c.mean())


def full_metrics(p, y):
    m = E.metrics(p, y)
    return {"nll": round(nll(p, y), 5), "brier": round(m["brier"], 5), "ece": round(m["ece"], 5), "aurc": round(aurc(p, y), 5), "prec@80": m["prec@80"], "prec@90": m["prec@90"], "prec@95": m["prec@95"], "n": m["n"]}


def boot(pa, pb, y, groups, n=500, seed=7):
    """paired document bootstrap of (candidate - baseline) for NLL / ECE / AURC / prec@90."""
    g = np.array(groups)
    ug = np.unique(g)
    idx = {k: np.where(g == k)[0] for k in ug}
    rng = random.Random(seed)
    d = {"nll": [], "ece": [], "aurc": [], "prec@90": []}
    for _ in range(n):
        s = np.concatenate([idx[ug[rng.randrange(len(ug))]] for _ in ug])
        ma, mb = full_metrics(pa[s], y[s]), full_metrics(pb[s], y[s])
        for k in d:
            d[k].append(ma[k] - mb[k])
    pt = {k: full_metrics(pa, y)[k] - full_metrics(pb, y)[k] for k in d}
    return {k: {"delta": float(pt[k]), "lo": float(np.percentile(v, 2.5)), "hi": float(np.percentile(v, 97.5)), "p": float(max(2 * min(np.mean(np.array(v) <= 0), np.mean(np.array(v) >= 0)), 1.0 / n))} for k, v in d.items()}


# ---------------------------------------------------------------- validation of the OOF linker artefact
def validate(oof, dev, ex, surf_train, ds):
    rep = {}
    food = lambda rs: [r for r in rs if r["lab_s"] == FOOD[ds]]
    for name, rs in (("oof_train", oof), ("dev", dev)):
        fr = food(rs)
        miss = [r for r in fr if r["norm"] not in ex]
        top1 = np.array([r["lf"]["top1"] for r in fr if r["lf"]["app"]])
        rep[name] = {"n_spans": len(rs), "n_food": len(fr), "missing_predictions": len(miss),
                     "linker_train_surface_exact_overlap": round(float(np.mean([r["norm"] in surf_train for r in fr])), 4),
                     "top1_cos_quantiles": [round(float(np.quantile(top1, q)), 3) for q in (0.05, 0.25, 0.5, 0.75, 0.95)],
                     "margin_mean": round(float(np.mean([r["lf"]["margin"] for r in fr if r["lf"]["app"]])), 4),
                     "frac_top1_below_0.8 (NIL-like)": round(float(np.mean(top1 < 0.8)), 4), "frac_top1_below_0.7": round(float(np.mean(top1 < 0.7)), 4),
                     "mean_top1_when_span_correct": round(float(np.mean([r["lf"]["top1"] for r in fr if r["y"]])), 4),
                     "mean_top1_when_span_wrong": round(float(np.mean([r["lf"]["top1"] for r in fr if not r["y"]])), 4),
                     "topk_len_min": int(min(len(r["lf"]["top"]) for r in fr if r["lf"]["app"]))}
    rep["shift_exact_overlap_train_minus_dev"] = round(rep["oof_train"]["linker_train_surface_exact_overlap"] - rep["dev"]["linker_train_surface_exact_overlap"], 4)
    return rep


def run(ds, export):
    oof, dev, labels = collect(ds)
    ex = json.loads(Path(export).read_text())["scores"]
    cats, surf_train, _ = cat_map()
    for r in oof + dev:
        r["lf"], r["pf"] = link_feats(r, ex, cats, ds), proc_family(r)
    val = validate(oof, dev, ex, surf_train, ds)
    spec = {"nlab": len(labels), "cats": sorted({r["lf"]["cat"] for r in oof if r["lf"]["cat"] not in ("NA",)}),
            "fams": sorted({r["pf"] for r in oof if r["pf"] != "NA"})}
    yo, yd = np.array([r["y"] for r in oof]), np.array([r["y"] for r in dev])
    gd = [r["group"] for r in dev]
    unseen = np.array([r["n"] == 0 for r in dev])
    food_d = np.array([r["lab_s"] == FOOD[ds] for r in dev])
    preds = {}
    for kind in ("P0", "C", "M1", "M2", "M3", "M4", "M5", "M6"):
        k = "C" if kind == "C" else kind
        Xo, Xd = design(oof, k, spec), design(dev, k, spec)
        sc = scaler(Xo)
        model, iso, _ = R.fit_calibrator(sc(Xo), yo)
        preds[kind] = R.calibrated(model, iso, sc(Xd))
    res, pv = {}, []
    for kind in ("P0", "C", "M1", "M2", "M3", "M4", "M5", "M6"):
        p = preds[kind]
        res[kind] = {"all": full_metrics(p, yd), "unseen_span": full_metrics(p[unseen], yd[unseen]), "food_spans": full_metrics(p[food_d], yd[food_d]),
                     "food_unseen": full_metrics(p[unseen & food_d], yd[unseen & food_d])}
    feats = ["M1", "M2", "M3", "M4", "M5", "M6"]
    for kind in feats:
        b = boot(preds[kind], preds["P0"], yd, gd)
        res[kind]["vs_P0"] = b
        pv.append(b["nll"]["p"])
    gf = [g for g, m in zip(gd, food_d) if m]
    for kind in feats:                                              # minimum follow-up for INCONCLUSIVE: restrict to the spans the linker features are defined on (FOOD)
        res[kind]["vs_P0_food"] = boot(preds[kind][food_d], preds["P0"][food_d], yd[food_d], gf)
    rej = R.holm(pv)
    for kind, sig in zip(feats, rej):
        r = res[kind]
        d = r["vs_P0"]
        dn = d["nll"]["delta"]
        du = r["unseen_span"]["nll"] - res["P0"]["unseen_span"]["nll"]
        worse_sig = sig and dn > 0
        if sig and dn < 0 and d["aurc"]["delta"] <= 0 and d["ece"]["delta"] <= 0.01 and du <= 0.0:
            dec = "PROMOTE"
        elif dn > -0.002 or worse_sig:
            dec = "REJECT"
        else:
            dec = "INCONCLUSIVE"
        r["holm_significant_nll"], r["unseen_nll_delta"], r["decision"] = bool(sig), round(du, 5), dec
    out = {"dataset": ds, "baseline": "P0 = calibrated logit(span conf) only; C = nuisance control (label+length)", "validation": val, "spec_sizes": {k: len(v) if hasattr(v, "__len__") else v for k, v in spec.items()},
           "n_oof": len(oof), "n_dev": len(dev), "results": res}
    (ROOT / "reports" / "ner" / f"_e2_linker_{ds}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"validation": val}, indent=1))
    for kind in feats:
        v = res[kind]["vs_P0_food"]
        print(f"FOOD-only {kind}: dNLL {v['nll']['delta']:+.4f} [{v['nll']['lo']:+.4f},{v['nll']['hi']:+.4f}] dAURC {v['aurc']['delta']:+.5f} [{v['aurc']['lo']:+.5f},{v['aurc']['hi']:+.5f}] dECE {v['ece']['delta']:+.4f} dP90 {v['prec@90']['delta']:+.4f}")
    print("n food dev spans", int(food_d.sum()), "unseen", int(unseen.sum()), "food unseen", int((unseen & food_d).sum()), "dev docs", len(set(gd)))
    for kind in ("P0", "C") + tuple(feats):
        a = res[kind]["all"]
        extra = ""
        if kind in feats:
            v = res[kind]["vs_P0"]
            extra = f" dNLL {v['nll']['delta']:+.4f} [{v['nll']['lo']:+.4f},{v['nll']['hi']:+.4f}] dAURC {v['aurc']['delta']:+.5f} dECE {v['ece']['delta']:+.4f} dP90 {v['prec@90']['delta']:+.4f} unseenNLL {res[kind]['unseen_nll_delta']:+.4f} -> {res[kind]['decision']}"
        print(f"{kind}: nll {a['nll']} brier {a['brier']} ece {a['ece']} aurc {a['aurc']} p90 {a['prec@90']}{extra}")


if __name__ == "__main__":
    ds, mode = sys.argv[1], sys.argv[2]
    surfaces(ds) if mode == "surfaces" else run(ds, sys.argv[3])
