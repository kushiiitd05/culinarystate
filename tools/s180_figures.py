#!/usr/bin/env python3
"""Export the freeze step-10 figures for S180, beside the author-owned report, never editing it.

Every series is read from a committed source file and the sha256 of each source is written into a
manifest, so a figure can be traced to the bytes it came from. Nothing is recomputed here and nothing
is estimated: if a number is not in a source file, it is not in a figure.

Four figures:

  * **fig_s180_1_retrieval_views** - step 9. Mean Jaccard@k between the three retrieval views, V0 and
    V1 side by side, with the chance-Jaccard null drawn as a line. Without the null, a low overlap is
    uninterpretable.
  * **fig_s180_2_layer1_surface** - step 7. Accepted proposals as recorded and on the surviving
    licensed surface, with the denominators printed on the axis.
  * **fig_s180_3_axis_status** - the canonical 13 compatibility axes by registry status.
  * **fig_s180_4_ph_bands** - the 140 ING pH bands from the FDA/CFSAN 2003 table, as intervals
    against the 4.6 threshold. No midpoints and no clipping.

Every figure that rests on the sealed comparison or the retrieval diagnostic carries a
``DIAGNOSTIC_ONLY`` stamp, as step 7's pre-registration section 5 requires, and the pH figure carries
its unverified-crosswalk stamp.

  python tools/s180_figures.py --out-dir reports/final/figures_s180_2026-11-15
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DIAG = "DIAGNOSTIC_ONLY · no gold · not accuracy"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args(argv)
    out = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    if out.exists():
        ap.error(f"{out} exists; a new output directory is required so a figure set is never overwritten")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.dpi": 200, "svg.hashsalt": "s180-figures"})

    sources: dict[str, str] = {}

    def read(rel: str):
        p = ROOT / rel
        sources[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
        return json.loads(p.read_text(encoding="utf-8"))

    def stamp(fig, text: str) -> None:
        """Footer below everything. Negative y keeps it clear of tick labels; bbox_inches='tight'
        still includes it because it is an artist of the figure."""
        import textwrap as _tw
        wrapped = "\n".join(_tw.wrap(" ".join(text.split()), width=108))
        fig.text(0.01, -0.06 * (5.0 / max(2.5, fig.get_figheight())), wrapped,
                 fontsize=6.3, color="#555", ha="left", va="top")

    out.mkdir(parents=True)
    written: list[str] = []

    def save(fig, name: str) -> None:
        fig.savefig(out / f"{name}.png", bbox_inches="tight")
        plt.close(fig)
        written.append(name)

    # ---- fig 1: step 9 retrieval views, V0 vs V1, with the chance null -------------------------
    v0 = read("reports/s180/retrieval_diagnostic_2026-11-15.json")
    v1 = read("reports/s180/retrieval_diagnostic_V1_2026-11-15.json")
    pairs = ["TEXT|PROCESS", "TEXT|COMPOSITION", "PROCESS|COMPOSITION"]
    fig, ax = plt.subplots(figsize=(5.6, 3.1))
    x = range(len(pairs))
    w = 0.36
    ax.bar([i - w / 2 for i in x], [v0["mean_jaccard_overlap_at_k"][p] for p in pairs], w,
           label=f"V0 ({v0['state_vector_dims']} dims)", color="#4C78A8")
    ax.bar([i + w / 2 for i in x], [v1["mean_jaccard_overlap_at_k"][p] for p in pairs], w,
           label=f"V1 ({v1['state_vector_dims']} dims)", color="#F58518")
    ax.axhline(v0["chance_jaccard_at_k"], color="#888", ls="--", lw=1,
               label=f"chance Jaccard = {v0['chance_jaccard_at_k']}")
    ax.set_xticks(list(x))
    ax.set_xticklabels([p.replace("|", " vs ") for p in pairs], fontsize=8)
    ax.set_ylabel("mean Jaccard@k")
    ax.set_title(f"Retrieval views disagree\n{v0['corpus_states']:,} states · {v0['queries']} queries"
                 f" · k={v0['k']}", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    stamp(fig, f"{DIAG} · no relevance gold, so overlap is not precision · "
               f"nothing shared by all three on {v0['queries_with_no_shared_hit_in_all_three']}"
               f"/{v0['queries']} queries (V0)")
    save(fig, "fig_s180_1_retrieval_views")

    # ---- fig 2: step 7 Layer-1 surface, recorded vs surviving ----------------------------------
    from culinarystate.composition import layer1_proposer as LP
    a1 = read("reports/s180/step7_arm_L_qwen7b_2026-11-15.json")
    a2 = read("reports/s180/step7_arm_L_qwen7b_v2_2026-11-15.json")
    seal = read("reports/s180/hardcase_seal_2026-11-15.json")
    lic = {t for t, f in LP.TRIGGER_FIELDS.items() if f}
    n_elig = sum(1 for c in seal["cases"] if lic & set(c["triggers"]))

    def surviving(arm) -> int:
        return sum(1 for c in arm["per_case"] for a in c["accepted"]
                   if a["field"] in LP.PROPOSABLE_FIELDS)

    labels = ["7B prompt v1", "7B prompt v2"]
    rec = [a1["proposals_accepted"], a2["proposals_accepted"]]
    sur = [surviving(a1), surviving(a2)]
    fig, ax = plt.subplots(figsize=(5.2, 3.1))
    x = range(len(labels))
    ax.bar([i - w / 2 for i in x], rec, w, label="accepted as recorded", color="#B3C7E0")
    ax.bar([i + w / 2 for i in x], sur, w, label="on the surviving licensed surface", color="#4C78A8")
    for i, (r, s) in enumerate(zip(rec, sur)):
        ax.text(i - w / 2, r + 0.6, str(r), ha="center", fontsize=8)
        ax.text(i + w / 2, s + 0.6, str(s), ha="center", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("accepted proposals")
    ax.set_title("Layer-1: removing a referenceless field\n"
                 f"{seal['selected_n']} sealed cases · {n_elig} with a licensed trigger", fontsize=9)
    ax.legend(fontsize=7, frameon=False)
    stamp(fig, f"{DIAG} · the two bars are NOT comparable: 'as recorded' counted condition_profile_id,"
               f" a reference field with no referent (D-135) · re-scoring of recorded data, not a re-run")
    save(fig, "fig_s180_2_layer1_surface")

    # ---- fig 3: the 13 compatibility axes by status ---------------------------------------------
    from culinarystate.composition import evidence_compiler as EC
    axes = EC.load_axes()
    sources["registry/rag/compatibility_axes_v1.csv"] = hashlib.sha256(
        (ROOT / "registry/rag/compatibility_axes_v1.csv").read_bytes()).hexdigest()
    order = ["IMPLEMENTED", "IMPLEMENTED_IN_COMPILER", "SCHEMA_ONLY"]
    colour = {"IMPLEMENTED": "#4C78A8", "IMPLEMENTED_IN_COMPILER": "#54A24B", "SCHEMA_ONLY": "#D3D3D3"}
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    for a in axes:
        ax.barh(a.axis_no, 1, color=colour.get(a.status, "#CCC"), edgecolor="white")
    ax.set_yticks([a.axis_no for a in axes])
    ax.set_yticklabels([f"{a.axis_no}. {a.axis.split(' (')[0]}" for a in axes], fontsize=7)
    ax.invert_yaxis()
    ax.set_xticks([])
    counts = {s: sum(1 for a in axes if a.status == s) for s in order}
    ax.set_title("Canonical compatibility axes, by registry status\n"
                 + " · ".join(f"{s.replace('_', ' ').lower()} {counts[s]}" for s in order), fontsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, color=colour[s]) for s in order]
    ax.legend(handles, [s.replace("_", " ").lower() for s in order], fontsize=7, frameon=False,
              loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3)
    stamp(fig, "schema carries all 13 axes; an unavailable axis stays UNKNOWN with a reason, "
               "never dropped · axis 8 has no producer, axis 12 has no data")
    save(fig, "fig_s180_3_axis_status")

    # ---- fig 4: pH bands as intervals against 4.6 ----------------------------------------------
    from culinarystate.composition import ph_bands as PH
    for rel in ("registry/food_ph_fda2003_v1.csv", "registry/food_ph_fda_ing_crosswalk_draft_v1.csv"):
        sources[rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    # ph_high is None for the LOWER_BOUND_ONLY rows ("greater than 4.6"); they are drawn as an open
    # ray to the axis limit, never closed at an invented upper bound.
    bands = sorted(PH.load_ph_bands().values(), key=lambda b: (b.ph_low, b.ph_high or 99.0))
    x_max = max((b.ph_high or b.ph_low) for b in bands) + 0.4
    fig, ax = plt.subplots(figsize=(5.4, 4.0))
    for i, b in enumerate(bands):
        band = PH.acidity_band(b.ph_low, b.ph_high)
        c = {"ACIDIC": "#E45756", "LOW_ACID": "#4C78A8"}.get(band, "#B279A2")
        hi = b.ph_high if b.ph_high is not None else x_max
        ax.plot([b.ph_low, hi], [i, i], color=c, lw=1.1, solid_capstyle="butt",
                ls="-" if b.ph_high is not None else ":")
        if b.ph_low == hi:  # POINT value: a single measured pH, drawn as a dot not a zero-length line
            ax.plot([b.ph_low], [i], marker="o", ms=1.6, color=c)
    ax.axvline(PH.ACID_THRESHOLD, color="#333", ls="--", lw=1)
    ax.text(PH.ACID_THRESHOLD + 0.05, len(bands) * 0.02, f"pH {PH.ACID_THRESHOLD}", fontsize=7)
    ax.set_xlim(0, x_max)
    ax.set_xlabel("pH")
    ax.set_ylabel(f"{len(bands)} ingredients, ordered by band")
    ax.set_yticks([])
    kinds = {}
    for b in bands:
        kinds[PH.acidity_band(b.ph_low, b.ph_high)] = kinds.get(PH.acidity_band(b.ph_low, b.ph_high), 0) + 1
    ax.set_title("Ingredient pH bands reported as intervals\n"
                 + " · ".join(f"{k.lower().replace('_', ' ')} {v}" for k, v in sorted(kinds.items())),
                 fontsize=9)
    stamp(fig, f"{PH.BASIS} · {PH.VERIFY_STATUS} · human verification owed before any claim · "
               f"no midpoints, no clipping (D-013): an interval straddling 4.6 is inconclusive")
    save(fig, "fig_s180_4_ph_bands")

    manifest = {
        "generated": "2026-11-15",
        "generator": "tools/s180_figures.py",
        "labels": ["DIAGNOSTIC_ONLY", "NO_GOLD_SO_NOT_ACCURACY", "WIKIBOOKS_CC_BY_PUBLIC_TEXT_ONLY",
                   "PH_CROSSWALK_UNVERIFIED_AI_DRAFTED"],
        "figures": written,
        "source_sha256": sources,
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    print(f"wrote {len(written)} figures + MANIFEST.json -> {out.relative_to(ROOT)}")
    for n in written:
        print(f"  {n}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
