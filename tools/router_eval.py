#!/usr/bin/env python3
"""S127: router with explicit baselines. Thresholds on CALIBRATION only (eps = 0.02 finite-sample risk control, per-label strata), evaluated on DEV; TEST untouched.
 R1 raw span threshold | R2 calibrated span | R3 calibrated span + M6 | R4 R3 + label-stratified thresholds + linker/NIL gate (ACCEPT/REVIEW/NOVEL) | R5 final = R4 + REJECT bar.
Span correctness is the only observable truth on the benchmarks (no gold canonical IDs), so link quality is validated on the linker-v2 held-out NIL sets, not on spans."""
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import e1_e2_calibration as E  # noqa: E402
import e2_signal_calibration as M  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402
from culinarystate.ner import spans as S  # noqa: E402

EPS = 0.02
RAWV2 = ROOT / "reports/ner/_raw_v2"
COSTS = {"c_err": 10.0, "c_review": 1.0, "c_lost": 3.0}      # accepted wrong span / each REVIEW or NOVEL / correct span REJECTED


def calibration_rows(ds):
    sp, docs, labels = E.load(ds)
    tr_docs = docs(sp["train"])
    full = S.Gazetteer.build(tr_docs, labels)
    pa = json.load(open(E.RAW / f"{ds}__deberta-base_crf__seed1.pred.json"))
    ca = json.load(open(E.RAW / f"{ds}__deberta-base_crf__seed1.conf.json"))
    return M.rows(docs(sp["calibration"]), pa["calibration"], ca["calibration"], full, labels, list(range(len(sp["calibration"]))), "cal")


def link_gate():
    """p_link model + thresholds from the linker-v2 DEV sets only (dev_alias vs dev NIL)."""
    t = json.load(open(RAWV2 / "linker__bge-large-en-v1.5_v2x__seed1.tables.json"))

    def f(rows):
        v = np.array([[s for _, s in r["top"]] for r in rows])
        p = np.exp((v - v.max(1, keepdims=True)) / 0.05)
        p /= p.sum(1, keepdims=True)
        return np.stack([v[:, 0], v[:, 0] - v[:, 1], -(p * np.log(p + 1e-12)).sum(1) / np.log(5)], 1)
    da, dn = t["dev_alias"], t["dev"]
    X = np.vstack([f(da), f(dn)])
    y = np.concatenate([[r["top"][0][0] == r["gold"] for r in da], np.zeros(len(dn), bool)]).astype(int)
    m = LogisticRegression(max_iter=1000).fit(X, y)
    p = m.predict_proba(X)[:, 1]
    grid = np.linspace(0.02, 0.98, 97)
    tau_l = max(grid, key=lambda c: 0.5 * ((p[y == 1] >= c).mean() + (p[y == 0] < c).mean()))
    pp = m.predict_proba(f(da))[:, 1]
    tl90 = float(np.percentile(pp, 10))                             # 90% of known dev aliases pass
    c0 = float(np.percentile(f(da)[:, 0], 5))                      # 95% of known aliases have top-1 cosine above c0 -> "has candidate"
    return m, float(tau_l), c0, f, t, tl90


def span_link(rows, ds, ex, m, f):
    pl, cand = np.ones(len(rows)), np.ones(len(rows), bool)
    for i, r in enumerate(rows):
        if r["lab_s"] == M.FOOD[ds] and r["norm"] in ex:
            v = np.array([s for _, s in ex[r["norm"]]][:5])
            p = np.exp((v - v.max()) / 0.05)
            p /= p.sum()
            pl[i] = m.predict_proba(np.array([[v[0], v[0] - v[1], -(p * np.log(p + 1e-12)).sum() / np.log(5)]]))[0, 1]
            cand[i] = v[0] >= LG[2]
    return pl, cand


def reject_bar(score, y, min_n=30, wrong=0.8):
    o = np.argsort(score)
    cw = np.cumsum(1 - y[o]) / np.arange(1, len(y) + 1)
    ok = np.where((cw >= wrong) & (np.arange(1, len(y) + 1) >= min_n))[0]
    return float(score[o][ok.max()]) if len(ok) else -np.inf


def evaluate(routes, y, groups, unseen, nb=300):
    r = np.asarray(routes)
    acc, rev, nov, rej = (r == "ACCEPT"), (r == "REVIEW"), (r == "NOVEL"), (r == "REJECT")
    wrong = 1 - y
    out = {"coverage": float(acc.mean()), "accept_error": float(wrong[acc].mean()) if acc.any() else None, "review_rate": float(rev.mean()), "novel_rate": float(nov.mean()), "reject_rate": float(rej.mean()),
           "error_capture_nonaccept": float(wrong[~acc].sum() / max(wrong.sum(), 1)), "reject_error_rate": float(wrong[rej].mean()) if rej.any() else None,
           "novel_correct_span_share": float(y[nov].mean()) if nov.any() else None,
           "accept_error_unseen": float(wrong[acc & unseen].mean()) if (acc & unseen).any() else None, "n_accept_unseen": int((acc & unseen).sum())}
    for ce in (5.0, 10.0, 20.0):
        out[f"cost_per_100_ce{int(ce)}"] = float(100 * (ce * wrong[acc].sum() + COSTS["c_review"] * (rev.sum() + nov.sum()) + COSTS["c_lost"] * y[rej].sum()) / len(y))
    g = np.asarray(groups)
    ug = np.unique(g)
    idx = {k: np.where(g == k)[0] for k in ug}
    rng = np.random.RandomState(0)
    be = []
    for _ in range(nb):
        s = np.concatenate([idx[ug[i]] for i in rng.randint(0, len(ug), len(ug))])
        a = acc[s]
        if a.any():
            be.append(wrong[s][a].mean())
    out["accept_error_ci95"] = [float(np.percentile(be, 2.5)), float(np.percentile(be, 97.5))] if be else None
    return out


def run(ds):
    global LG
    oof, dev, labels = M.collect(ds)
    cal = calibration_rows(ds)
    for r in oof + dev + cal:
        r.setdefault("lf", {}), r.setdefault("pf", "NA")
    spec = {"nlab": len(labels), "cats": [], "fams": []}
    yo = np.array([r["y"] for r in oof])
    yc, yd = np.array([r["y"] for r in cal]), np.array([r["y"] for r in dev])
    P = {}
    for k in ("P0", "P0+M6"):
        Xo = M.design(oof, k, spec)
        sc = M.scaler(Xo)
        mo, iso, _ = R.fit_calibrator(sc(Xo), yo)
        P[k] = {nm: R.calibrated(mo, iso, sc(M.design(rs, k, spec))) for nm, rs in (("cal", cal), ("dev", dev))}
    raw = {"cal": np.array([r["conf"] for r in cal]), "dev": np.array([r["conf"] for r in dev])}
    LG = link_gate()
    m, tau_l, c0, f, _, _t90 = LG
    ex = json.loads((RAWV2 / "linker_export__bge-large-en-v1.5_v2x__seed1.json").read_text())["scores"]
    pl_c, cand_c = span_link(cal, ds, ex, m, f)
    pl_d, cand_d = span_link(dev, ds, ex, m, f)
    lab_c, lab_d = np.array([r["lab_s"] for r in cal]), np.array([r["lab_s"] for r in dev])
    gd = [r["group"] for r in dev]
    unseen = np.array([r["n"] == 0 for r in dev])
    res = {"dataset": ds, "eps": EPS, "n_cal": len(cal), "n_dev": len(dev), "link_gate": {"tau_l": tau_l, "cos_candidate": c0}, "routers": {}}
    # R1-R3 : global threshold
    for nm, sc_c, sc_d in (("R1_raw_span", raw["cal"], raw["dev"]), ("R2_calibrated_span", P["P0"]["cal"], P["P0"]["dev"]), ("R3_calibrated_span+M6", P["P0+M6"]["cal"], P["P0+M6"]["dev"])):
        tau = R.risk_control_threshold(sc_c, yc, EPS)
        res["routers"][nm] = {"tau": tau, **evaluate(np.where(sc_d >= tau, "ACCEPT", "REVIEW"), yd, gd, unseen)}
    sc_c, sc_d = P["P0+M6"]["cal"], P["P0+M6"]["dev"]
    un_c = np.array([r["n"] == 0 for r in cal])
    strat = {"label": (lab_c, lab_d), "label_x_unseen": (np.array([f"{l}|{'U' if u else 'S'}" for l, u in zip(lab_c, un_c)]), np.array([f"{l}|{'U' if u else 'S'}" for l, u in zip(lab_d, unseen)]))}
    tau_by = {}
    for nm, (sc_s, sd_s) in strat.items():
        taus = R.stratified_thresholds(sc_c, yc, sc_s, EPS)
        tau_by[nm] = np.array([taus.get(l, taus["__pooled__"]) for l in sd_s])
        res["routers"][f"R3s_M6_strata[{nm}]"] = {"taus": {k: (None if np.isinf(v) else round(v, 4)) for k, v in taus.items()}, **evaluate(np.where(sc_d >= tau_by[nm], "ACCEPT", "REVIEW"), yd, gd, unseen)}
    tau_d = tau_by["label_x_unseen"]
    # R4 : + linker/NIL gate (ACCEPT / REVIEW / NOVEL); two operating points of tau_l (dev-balanced, and 90% of known aliases kept)
    def gate(sc, tau, pl, cand, bar, tl):
        return [R.route(float(a), float(b), float(t), tl, bar, bool(c)) for a, t, b, c in zip(sc, tau, pl, cand)]
    tl90 = LG[5]
    for nm, tl in (("balanced", tau_l), ("keep90", tl90)):
        res["routers"][f"R4_M6+strata+linker_NIL[{nm} tau_l={tl:.2f}]"] = evaluate(gate(sc_d, tau_d, pl_d, cand_d, -np.inf, tl), yd, gd, unseen)
    bar = COSTS["c_review"] / COSTS["c_lost"]                      # reject iff P(correct) < c_review / c_lost (cost-derived, not tuned)
    res["reject_bar_check_on_calibration"] = {"bar": bar, "n_cal_below": int((sc_c < bar).sum()), "wrong_rate_below": float((1 - yc[sc_c < bar]).mean()) if (sc_c < bar).any() else None}
    res["routers"][f"R5_final(+REJECT<{bar:.2f}, tau_l={tau_l:.2f})"] = {"review_bar": bar, **evaluate(gate(sc_d, tau_d, pl_d, cand_d, bar, tau_l), yd, gd, unseen)}
    res["routers"]["R6_FINAL(strata label x unseen, REJECT bar, linker advisory only)"] = {"review_bar": bar, **evaluate(gate(sc_d, tau_d, pl_d, cand_d, bar, 0.0), yd, gd, unseen)}
    tau_l_final = 0.0
    # per-label accept error of the final router
    fr = np.array(gate(sc_d, tau_d, pl_d, cand_d, bar, tau_l_final))
    res["final_per_label"] = {l: {"n": int((lab_d == l).sum()), "accept_rate": float((fr[lab_d == l] == "ACCEPT").mean()), "accept_error": (float((1 - yd[(lab_d == l) & (fr == "ACCEPT")]).mean()) if ((lab_d == l) & (fr == "ACCEPT")).any() else None)}
                              for l in sorted(set(lab_d))}
    tg = res["routers"]["R3_calibrated_span+M6"]["tau"]
    ga = sc_d >= tg
    res["R3_global_per_label"] = {l: {"n": int((lab_d == l).sum()), "accept_rate": float(ga[lab_d == l].mean()), "accept_error": (float((1 - yd[(lab_d == l) & ga]).mean()) if ((lab_d == l) & ga).any() else None)} for l in sorted(set(lab_d))}
    isfood = np.array([r["lab_s"] == M.FOOD[ds] for r in dev])
    nov = isfood & (sc_d >= bar) & (~cand_d)                      # advisory NOVEL tag: plausible span, no ledger candidate above cos_candidate
    led = M.ledger_maps()[0]
    res["novel_advisory"] = {"n": int(nov.sum()), "share_of_food_spans": float(nov.sum() / max(isfood.sum(), 1)), "correct_span_share": float(yd[nov].mean()) if nov.any() else None,
                             "ledger_exact_hit_share": float(np.mean([dev[i]["norm"] in led for i in np.where(nov)[0]])) if nov.any() else None,
                             "share_routed_accept": float((np.array(fr)[nov] == "ACCEPT").mean()) if nov.any() else None}
    # risk-coverage AURC of the continuous scores on DEV
    res["aurc_dev"] = {"raw": M.aurc(raw["dev"], yd), "calibrated": M.aurc(P["P0"]["dev"], yd), "calibrated+M6": M.aurc(P["P0+M6"]["dev"], yd)}
    # latency of the Mac-side components (per 1000 spans)
    t0 = time.perf_counter()
    for r in dev[:1000]:
        pass
    t_route = time.perf_counter()
    gate(sc_d[:1000], tau_d[:1000], pl_d[:1000], cand_d[:1000], bar, tau_l_final)
    res["router_ms_per_1000_spans"] = round(1000 * (time.perf_counter() - t_route), 2)
    (ROOT / f"reports/ner/_router_{ds}.json").write_text(json.dumps(res, indent=1, default=float))
    print("==", ds, "tau_l", round(tau_l, 3), "cos_cand", round(c0, 3), "reject_bar", round(res["reject_bar_check_on_calibration"]["bar"], 3), res["reject_bar_check_on_calibration"])
    for nm, r in res["routers"].items():
        ci = r["accept_error_ci95"]
        print(f"{nm[:44]:44s} cov {r['coverage']:.3f} acc_err {r['accept_error'] if r['accept_error'] is None else round(r['accept_error'], 4)} ci {None if ci is None else [round(x, 4) for x in ci]} "
              f"rev {r['review_rate']:.3f} nov {r['novel_rate']:.3f} rej {r['reject_rate']:.3f} errcap {r['error_capture_nonaccept']:.3f} unseenAccErr {r['accept_error_unseen']} n_u {r['n_accept_unseen']} "
              f"cost10 {r['cost_per_100_ce10']:.1f}")
    print("per-label final:", {k: (v["n"], round(v["accept_rate"], 3), None if v["accept_error"] is None else round(v["accept_error"], 4)) for k, v in res["final_per_label"].items()})
    print("R3 global per-label:", {k: (v["n"], round(v["accept_rate"], 3), None if v["accept_error"] is None else round(v["accept_error"], 4)) for k, v in res["R3_global_per_label"].items()})
    print("novel advisory:", res["novel_advisory"])
    print("AURC", {k: round(v, 5) for k, v in res["aurc_dev"].items()})


if __name__ == "__main__":
    for ds in ("tasteset", "recipedb3"):
        run(ds)
