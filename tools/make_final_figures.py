#!/usr/bin/env python
"""Slide figures for the final report (S168) from committed, counts-only result files. Static PNGs, light surface.

    python tools/make_final_figures.py   # writes reports/final/figures/*.png (refuses to overwrite)
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/final/figures"
SURFACE, INK, INK2, SERIES, REF = "#fcfcfb", "#0b0b0b", "#52514e", "#2a78d6", "#8a8984"


def _style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(REF)
    ax.tick_params(colors=INK2, length=0)
    ax.xaxis.grid(True, color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)


def _hbar(ax, labels, values, fmt):
    y = range(len(labels))[::-1]
    ax.barh(list(y), values, height=0.5, color=SERIES, edgecolor=SURFACE, linewidth=2)
    ax.set_yticks(list(y), labels, color=INK, fontsize=10)
    top = max(values) or 1
    for yi, v in zip(y, values):
        ax.text(v + top * 0.01, yi, fmt(v), va="center", ha="left", color=INK, fontsize=10)
    ax.set_xlim(0, top * 1.28)


def _save(fig, name):
    path = OUT / name
    if path.exists():
        sys.exit(f"refusing to overwrite {path}")
    fig.savefig(path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(path.relative_to(ROOT))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rc2 = json.loads((ROOT / "reports/step16/rc2_grounding_dryrun_counts.json").read_text())
    lines = sum(f["lines_total"] for f in rc2["by_family"].values())
    q0 = sum(f["q_level"].get("Q0", 0) for f in rc2["by_family"].values())
    u2044 = 1_275_782  # S168 counts-only corpus scan (D-069); not in a committed JSON
    fig, ax = plt.subplots(figsize=(8, 2.6), facecolor=SURFACE)
    _style(ax)
    _hbar(ax, ["Ingredient lines", "Lines with U+2044 fraction slash\n(mis-parsed, SP-002)", "rc2 exact mass (Q0)"],
          [lines, u2044, q0], lambda v: f"{v:,}  ({v / lines:.2%})" if v != lines else f"{v:,}")
    ax.set_title("Step 16 quantity grounding: under 1 % of ingredient lines reach an exact mass",
                 loc="left", color=INK, fontsize=12)
    ax.text(0, -0.32, "Sources: rc2_grounding_dryrun_counts.json (S161); U+2044 count from the S168 corpus scan. "
            "Q0 is expected to change once SP-002 is fixed.", transform=ax.transAxes, color=INK2, fontsize=8)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1e6:g}M"))
    _save(fig, "fig1_quantity_funnel.png")

    cen = json.loads((ROOT / "reports/step26/simulability_census_full_corpus_S166.json").read_text())
    sysc = cen["census"]["systems"]["sim_aa_1"]
    ev, nce, sim = cen["engine_events"], sysc["reasons"]["NO_CONSUMED_ENTITY"], sysc["route"]["SIMULATE"]
    fig, ax = plt.subplots(figsize=(8, 2.6), facecolor=SURFACE)
    _style(ax)
    _hbar(ax, ["Engine events", "No consumed entity\n(extraction/linking gap)", "Routed to SIMULATE"], [ev, nce, sim],
          lambda v: f"{v:,}  ({v / ev:.0%})" if v not in (ev, 0) else (f"{v:,}" if v else "0  (no condition bindings yet)"))
    ax.set_title("Step 26g simulability census (sim_aa_1): nothing is simulable yet", loc="left", color=INK, fontsize=12)
    ax.text(0, -0.32, "Source: simulability_census_full_corpus_S166.json (612,782 recipes). SIMULATE = 0 by construction; "
            "42 % of events would still lack a consumed entity.", transform=ax.transAxes, color=INK2, fontsize=8)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1e6:g}M"))
    _save(fig, "fig2_census_funnel.png")

    p1 = json.loads((ROOT / "reports/step19/p1_agreement_counts_S166.json").read_text())
    m, rate = p1["mean"], p1["handbook_gate"]["per_pair_rate"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.6), facecolor=SURFACE, gridspec_kw={"wspace": 0.55})
    for ax in (a1, a2):
        _style(ax)
    names = [("Concept", "concept_agreement"), ("Spans (exact)", "spans_exact_f1"), ("Coref B³", "coref_b_cubed_f1"),
             ("Process", "process_link_f1"), ("Alive entities", "alive_entity_f1"), ("Events (strict)", "event_f1_strict"),
             ("Final-state fields", "state_field_agreement")]
    _hbar(a1, [n for n, _ in names], [m[k] for _, k in names], lambda v: f"{v:.2f}")
    a1.set_xlim(0, 1.15)
    a1.set_ylim(-1.1, 6.6)
    for x, lab in ((0.80, "0.80"), (0.667, "0.667")):
        a1.axvline(x, color=REF, linestyle="--", linewidth=1)
        a1.text(x, -0.85, lab, color=INK2, fontsize=8, ha="center")
    a1.set_title("P1 agreement (mean over 7 pairs)", loc="left", color=INK, fontsize=11)
    cats = sorted(rate, key=lambda c: -(rate[c] or 0))[:6]
    _hbar(a2, [c.replace("_", " ") for c in cats], [rate[c] or 0 for c in cats], lambda v: f"{v:.2f}")
    a2.set_xlim(0, 1.15)
    a2.set_ylim(-1.1, 5.6)
    a2.axvline(0.20, color=REF, linestyle="--", linewidth=1)
    a2.text(0.20, -0.85, "gate 0.20", color=INK2, fontsize=8, ha="center")
    a2.set_title("Handbook gate: disagreement rate per category", loc="left", color=INK, fontsize=11)
    fig.text(0.01, -0.04, "Labels are human-accepted AI drafts from one model family on one machine (D-045 W2, D-060, D-064): "
             "an engineering score, not inter-annotator agreement. Source: p1_agreement_counts_S166.json "
             "(per-pair rate, THR-19P-31); verdict HANDBOOK_REVISION_REQUIRED.", color=INK2, fontsize=8)
    _save(fig, "fig3_p1_panel.png")


if __name__ == "__main__":
    main()
