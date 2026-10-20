#!/usr/bin/env python3
"""S128 FINAL TEST (run once). Frozen system: reports/ner/test_freeze_manifest.json. No threshold / calibrator / strata / feature changes after reading TEST.
  python tools/final_test_eval.py surfaces      # test FOOD-span surfaces (+ previous) for the frozen linker export
  python tools/final_test_eval.py eval          # the single TEST evaluation -> reports/ner/_final_test.json"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import e1_e2_calibration as E  # noqa: E402
import e2_signal_calibration as M  # noqa: E402
import router_eval as RT  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402
from culinarystate.ner import spans as S  # noqa: E402

DS = ("tasteset", "recipedb3")


def test_rows(ds):
    sp, docs, labels = E.load(ds)
    full = S.Gazetteer.build(docs(sp["train"]), labels)
    pa = json.load(open(E.RAW / f"{ds}__deberta-base_crf__seed1.pred.json"))
    ca = json.load(open(E.RAW / f"{ds}__deberta-base_crf__seed1.conf.json"))
    return M.rows(docs(sp["test"]), pa["test"], ca["test"], full, labels, list(range(len(sp["test"]))), "test")


def surfaces():
    allv = set(json.load(open(ROOT / "features/span_surfaces_all.json")))
    new = set()
    for ds in DS:
        new |= {r["norm"] for r in test_rows(ds) if r["lab_s"] == M.FOOD[ds] and r["norm"]}
    out = sorted(allv | new)
    (ROOT / "features/span_surfaces_final.json").write_text(json.dumps(out))
    print(len(allv), "+", len(new - allv), "->", len(out))


if __name__ == "__main__":
    surfaces() if sys.argv[1] == "surfaces" else None


# ---------------------------------------------------------------------------------- the single TEST evaluation
def span_quality(ds, stem):
    import glob
    import statistics as st
    runs = [json.load(open(f)) for f in sorted(glob.glob(str(ROOT / f"reports/ner/_raw_all/{ds}__{stem}__seed?.json")))]
    T = [r["test"] for r in runs]
    ms = lambda xs: [round(float(np.mean(xs)), 4), round(float(np.std(xs, ddof=1)), 4) if len(xs) > 1 else None]
    out = {"seeds": [r["seed"] for r in runs], "exact_micro_f1": ms([t["exact"]["micro"]["f1"] for t in T]), "exact_macro_f1": ms([t["exact"]["macro_f1"] for t in T]),
           "relaxed_micro_f1": ms([t["relaxed"]["micro"]["f1"] for t in T]), "boundary_error": ms([t["boundary_error_rate"] for t in T]), "type_error": ms([t["type_error_rate"] for t in T]),
           "seed1": {"exact_micro_f1": round(T[0]["exact"]["micro"]["f1"], 4), "exact_macro_f1": round(T[0]["exact"]["macro_f1"], 4)},
           "strata_f1": {k: ms([t["strata"][k]["f1"] for t in T]) for k in T[0]["strata"]}, "strata_n": {k: T[0]["strata"][k].get("n") for k in T[0]["strata"]},
           "per_label_f1": {k: ms([t["exact"]["per_label"][k]["f1"] for t in T]) for k in T[0]["exact"]["per_label"]},
           "train_minutes": ms([r["minutes"] for r in runs]), "peak_gpu_gb": ms([r["peak_gpu_gb"] for r in runs])}
    return out


def cal_metrics(p, y):
    p = np.asarray(p, float)
    m = M.fm(p, p, y)
    return {k: m[k] for k in ("nll", "brier", "ece", "n")}


def run_eval():
    res = {}
    RT.LG = RT.link_gate()
    m_link, tau_l, c0, f_link, _, _ = RT.LG
    ex = json.loads((ROOT / "reports/ner/_raw_v2/linker_export__bge-large-en-v1.5_v2final__seed1.json").read_text())["scores"]
    for ds in DS:
        oof, dev, labels = M.collect(ds)
        cal, tst = RT.calibration_rows(ds), test_rows(ds)
        for r in oof + cal + tst:
            r.setdefault("lf", {}), r.setdefault("pf", "NA")
        spec = {"nlab": len(labels), "cats": [], "fams": []}
        yo, yc, yt = (np.array([r["y"] for r in rs]) for rs in (oof, cal, tst))
        P = {}
        for k in ("P0", "P0+M6"):
            Xo = M.design(oof, k, spec)
            sc = M.scaler(Xo)
            mo, iso, _ = R.fit_calibrator(sc(Xo), yo)
            P[k] = {nm: R.calibrated(mo, iso, sc(M.design(rs, k, spec))) for nm, rs in (("cal", cal), ("test", tst))}
        raw = {"cal": np.array([r["conf"] for r in cal]), "test": np.array([r["conf"] for r in tst])}
        lab_c, lab_t = np.array([r["lab_s"] for r in cal]), np.array([r["lab_s"] for r in tst])
        un_c, un_t = np.array([r["n"] == 0 for r in cal]), np.array([r["n"] == 0 for r in tst])
        tail_t = np.array([1 <= r["n"] <= 2 for r in tst])
        gt = [r["group"] for r in tst]
        isfood = np.array([r["lab_s"] == M.FOOD[ds] for r in tst])
        o = {"n_test_spans": len(tst), "n_test_docs": len(set(gt)), "span_acc": float(yt.mean())}
        # calibration
        o["calibration"] = {nm: {"all": cal_metrics(p, yt), "food": cal_metrics(p[isfood], yt[isfood]), "unseen_mention": cal_metrics(p[un_t], yt[un_t]), "seen_mention": cal_metrics(p[~un_t], yt[~un_t]),
                                 "tail_mention": cal_metrics(p[tail_t], yt[tail_t])}
                            for nm, p in (("raw_conf", raw["test"]), ("calibrated", P["P0"]["test"]), ("calibrated+M6", P["P0+M6"]["test"]))}
        o["risk_discrimination_aurc"] = {"raw": M.aurc(raw["test"], yt), "calibrated": M.aurc(P["P0"]["test"], yt), "calibrated+M6": M.aurc(P["P0+M6"]["test"], yt)}
        # routers (thresholds from CALIBRATION only)
        routers = {}
        for nm, a, b in (("R1_raw_span", raw["cal"], raw["test"]), ("R2_calibrated_span", P["P0"]["cal"], P["P0"]["test"]), ("R3_calibrated_span+M6", P["P0+M6"]["cal"], P["P0+M6"]["test"])):
            tau = R.risk_control_threshold(a, yc, RT.EPS)
            routers[nm] = {"tau": tau, **RT.evaluate(np.where(b >= tau, "ACCEPT", "REVIEW"), yt, gt, un_t)}
        sc_c, sc_t = P["P0+M6"]["cal"], P["P0+M6"]["test"]
        for nm, kc, kt in (("R3s_label_strata", lab_c, lab_t), ("R6_FINAL_label_x_unseen", np.array([f"{l}|{'U' if u else 'S'}" for l, u in zip(lab_c, un_c)]), np.array([f"{l}|{'U' if u else 'S'}" for l, u in zip(lab_t, un_t)]))):
            taus = R.stratified_thresholds(sc_c, yc, kc, RT.EPS)
            tau_t = np.array([taus.get(l, taus["__pooled__"]) for l in kt])
            bar = RT.COSTS["c_review"] / RT.COSTS["c_lost"]
            rt = np.array([R.route(float(s), 1.0, float(t), 0.0, bar if nm.startswith("R6") else -np.inf, True) for s, t in zip(sc_t, tau_t)])
            routers[nm] = {"taus": {k: (None if np.isinf(v) else round(v, 4)) for k, v in taus.items()}, **RT.evaluate(rt, yt, gt, un_t)}
            if nm.startswith("R6"):
                stored = json.load(open(ROOT / f"reports/ner/_router_{ds}.json"))
                key = [k for k in stored["routers"] if k.startswith("R3s_M6_strata[label_x_unseen]")][0]
                routers[nm]["frozen_thresholds_match_S127"] = all((stored["routers"][key]["taus"][k] is None and v is None) or (stored["routers"][key]["taus"][k] is not None and v is not None and abs(stored["routers"][key]["taus"][k] - v) < 1e-4)
                                                                 for k, v in routers[nm]["taus"].items())
                wrong = 1 - yt
                routers[nm]["error_capture_review_only"] = float(wrong[rt == "REVIEW"].sum() / max(wrong.sum(), 1))
                routers[nm]["per_label"] = {l: {"n": int((lab_t == l).sum()), "accept_rate": float((rt[lab_t == l] == "ACCEPT").mean()), "accept_error": (float(wrong[(lab_t == l) & (rt == "ACCEPT")].mean()) if ((lab_t == l) & (rt == "ACCEPT")).any() else None),
                                                "span_error_rate": float(wrong[lab_t == l].mean()), "review_rate": float((rt[lab_t == l] == "REVIEW").mean()), "reject_rate": float((rt[lab_t == l] == "REJECT").mean())} for l in sorted(set(lab_t))}
                routers[nm]["seen_unseen"] = {nm_: {"n": int(mk.sum()), "accept_rate": float((rt[mk] == "ACCEPT").mean()), "accept_error": (float(wrong[mk & (rt == "ACCEPT")].mean()) if (mk & (rt == "ACCEPT")).any() else None), "span_error_rate": float(wrong[mk].mean())}
                                              for nm_, mk in (("seen", ~un_t), ("unseen", un_t))}
                routers[nm]["always_review_labels(never ACCEPT at eps=0.02)"] = [l for l, v in routers[nm]["per_label"].items() if v["accept_rate"] == 0.0]
                final_route = rt
        o["routers"] = routers
        # linker advisory NOVEL on TEST spans (never an action)
        pl, cand = RT.span_link(tst, ds, ex, m_link, f_link)
        bar = RT.COSTS["c_review"] / RT.COSTS["c_lost"]
        nov = isfood & (sc_t >= bar) & (~cand)
        led = M.ledger_maps()[0]
        o["novel_advisory"] = {"n": int(nov.sum()), "share_of_food_spans": float(nov.sum() / max(isfood.sum(), 1)), "correct_span_share": (float(yt[nov].mean()) if nov.any() else None),
                               "ledger_exact_hit_share": (float(np.mean([tst[i]["norm"] in led for i in np.where(nov)[0]])) if nov.any() else None), "auto_accepted": int((final_route[nov] == "ACCEPT").sum())}
        res[ds] = o
    # span quality (primary, challenger) and challenger paired test come from the same frozen run files
    for ds in DS:
        res[ds]["span_quality"] = {"PRIMARY deberta-base+CRF": span_quality(ds, "deberta-base_crf"), "FROZEN ACCURACY/COMPUTE CHALLENGER deberta-v3-large+CRF": span_quality(ds, "deberta-v3-large_crf")}
    res["linker"] = json.load(open(ROOT / "reports/ner/_linker_v2_eval.json"))
    res["latency"] = json.load(open(ROOT / "reports/ner/_latency_bench.json"))
    (ROOT / "reports/ner/_final_test.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__" and sys.argv[1] == "eval":
    r = run_eval()
    for ds in DS:
        o = r[ds]
        print("=====", ds, "test spans", o["n_test_spans"], "docs", o["n_test_docs"], "span acc", round(o["span_acc"], 4))
        for nm, c in o["calibration"].items():
            print(f"  cal {nm:14s} ALL nll {c['all']['nll']:.4f} brier {c['all']['brier']:.4f} ece {c['all']['ece']:.4f} | FOOD nll {c['food']['nll']:.4f} ece {c['food']['ece']:.4f} | unseen nll {c['unseen_mention']['nll']:.4f} ece {c['unseen_mention']['ece']:.4f}")
        print("  AURC", {k: round(v, 5) for k, v in o["risk_discrimination_aurc"].items()})
        for nm, c in o["routers"].items():
            ci = c["accept_error_ci95"]
            print(f"  {nm:26s} cov {c['coverage']:.3f} acc_err {c['accept_error'] if c['accept_error'] is None else round(c['accept_error'], 4)} ci {None if ci is None else [round(x, 4) for x in ci]} rev {c['review_rate']:.3f} rej {c['reject_rate']:.3f} errcap {c['error_capture_nonaccept']:.3f} cost10 {c['cost_per_100_ce10']:.1f}")
        f = o["routers"]["R6_FINAL_label_x_unseen"]
        print("  R6 thresholds match S127:", f["frozen_thresholds_match_S127"], "| never-ACCEPT labels:", f["always_review_labels(never ACCEPT at eps=0.02)"], "| review-only capture", round(f["error_capture_review_only"], 3))
        print("  R6 per label:", {k: (v["n"], round(v["accept_rate"], 3), None if v["accept_error"] is None else round(v["accept_error"], 4), round(v["span_error_rate"], 3)) for k, v in f["per_label"].items()})
        print("  R6 seen/unseen:", {k: {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()} for k, v in f["seen_unseen"].items()})
        print("  NOVEL advisory:", o["novel_advisory"])
        for nm, q in o["span_quality"].items():
            print(f"  SPAN {nm}: micro {q['exact_micro_f1']} macro {q['exact_macro_f1']} relaxed {q['relaxed_micro_f1']} boundary {q['boundary_error']} type {q['type_error']} seeds {q['seeds']} min {q['train_minutes']} gb {q['peak_gpu_gb']}")
            print("     strata", q["strata_f1"])
