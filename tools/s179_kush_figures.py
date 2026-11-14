#!/usr/bin/env python
"""T3-C17-R2 / T6-C02-R3: two technical figures from the 13 Nov committed JSON (no other source):
  fig_d097_type_pr  — D-097 per-type precision/recall with recipe-cluster bootstrap 95% CIs, per gold set.
  fig_paired_vs_d0  — 29-diag rung-vs-D0 paired estimates per family x split; + / - when the 95% CI excludes 0.
Writes PNG+SVG and a hash manifest into a NEW folder; refuses an existing one. Labels: DIAGNOSTIC, NOT_INDEPENDENT.

    /opt/anaconda3/bin/python tools/s179_kush_figures.py --out-dir reports/s179/kush_figures_2026-11-13
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D097 = "reports/s179/d097_runga_type_table_2026-11-13.json"
PAIRED = "reports/step29/diag/paired_vs_d0_S179_2026-11-13.json"
LABEL = "DIAGNOSTIC · NOT_INDEPENDENT · NON_CITABLE · NO_HUMAN_SIGNOFF_D085 (Kush review ok, D-097a)"


def type_series(d: dict) -> dict:
    out = {}
    for name, s in d["sets"].items():
        types = {t: {k: r[k] for k in ("gold", "pred", "precision", "precision_ci95", "recall", "recall_ci95")}
                 for t, r in s["types"].items() if r["gold"] or r["pred"]}
        out[name] = {"n": s["n_recipes"], "basis": s["label_basis"], "types": types}
    return out


def paired_grid(d: dict) -> dict:
    out = {}
    for fam, f in d["result"]["families"].items():
        out[fam] = {}
        for sp, per in f["splits"].items():
            if "refused" in per:
                continue
            out[fam][sp] = {k: {"estimate": v["estimate"],
                                "sign": "+" if v["lower95"] > 0 else "-" if v["upper95"] < 0 else "0",
                                "low_clusters": v["label"].startswith("DIAGNOSTIC_ONLY")}
                            for k, v in sorted(per.items()) if "refused" not in v}
    return out


def _fig_types(plt, series):
    fig, axes = plt.subplots(1, len(series), figsize=(4.2 * len(series), 4), sharey=True)
    for ax, (name, s) in zip(axes, series.items()):
        types = list(s["types"])
        for j, (metric, off, col) in enumerate((("precision", -0.18, "#1f5f8b"), ("recall", 0.18, "#c0661e"))):
            for i, t in enumerate(types):
                r = s["types"][t]
                v, ci = r[metric], r[f"{metric}_ci95"]
                if v is None:
                    continue
                yerr = [[v - ci[0]], [ci[1] - v]] if ci else None
                ax.errorbar(i + off, v, yerr=yerr, fmt="o", color=col, capsize=3, label=metric if i == 0 else None)
        ax.set_xticks(range(len(types)), types, rotation=35, ha="right")
        ax.set_ylim(-0.05, 1.05)
        ax.set_title(f"{name} (n={s['n']})", fontsize=9)
    axes[0].set_ylabel("count-match P / R (95% cluster bootstrap)")
    axes[0].legend(loc="lower left", fontsize=8)
    fig.suptitle("D-097 Rung A structural types vs gold — " + LABEL, fontsize=8, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    return fig


def _fig_paired(plt, grid):
    fams = list(grid)
    fig, axes = plt.subplots(1, len(fams), figsize=(4.6 * len(fams), 3.8))
    for ax, fam in zip(axes, fams):
        splits = list(grid[fam])
        rungs = sorted({k for sp in splits for k in grid[fam][sp]})
        m = [[grid[fam][sp].get(k, {}).get("estimate") or 0.0 for k in rungs] for sp in splits]
        lim = max(0.05, max(abs(x) for row in m for x in row))
        im = ax.imshow(m, cmap="RdBu", vmin=-lim, vmax=lim, aspect="auto")
        for i, sp in enumerate(splits):
            for j, k in enumerate(rungs):
                c = grid[fam][sp].get(k)
                if c:
                    ax.text(j, i, c["sign"] + ("*" if c["low_clusters"] else ""), ha="center", va="center", fontsize=8)
        ax.set_xticks(range(len(rungs)), rungs)
        ax.set_yticks(range(len(splits)), splits, fontsize=8)
        ax.set_title(fam, fontsize=9)
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("29-diag loss(D0) − loss(rung): blue = rung better; +/− CI excludes 0; * < K_MIN clusters; "
                 "PRIOR_EXPOSURE_REANALYSIS — " + LABEL, fontsize=7, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    return fig


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out_dir.exists():
        ap.error("new output directory required")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "s179-kush-figures", "svg.fonttype": "none"})
    src = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (D097, PAIRED)}
    figs = {"fig_d097_type_pr": _fig_types(plt, type_series(json.loads((ROOT / D097).read_text()))),
            "fig_paired_vs_d0": _fig_paired(plt, paired_grid(json.loads((ROOT / PAIRED).read_text())))}
    a.out_dir.mkdir(parents=True)
    files = {}
    for name, fig in figs.items():
        for ext in ("png", "svg"):
            p = a.out_dir / f"{name}.{ext}"
            fig.savefig(p, dpi=160, metadata={"Date": None} if ext == "svg" else None)
            files[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    (a.out_dir / "manifest.json").write_text(json.dumps({"sources": src, "files": files, "label": LABEL,
                                                         "items": ["T3-C17-R2", "T6-C02-R3"]}, indent=1) + "\n")
    print(json.dumps(files, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
