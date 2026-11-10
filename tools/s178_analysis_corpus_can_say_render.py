"""S178 T4-C04-R1 renderer: tables (markdown + JSON), CSVs and three dependency-free SVG figures.

Imported by tools/s178_analysis_corpus_can_say.py --build. matplotlib is absent from the server venv, so the
figures are written as plain SVG (light surface, explicit background, thin marks, 2 px gaps, direct labels) and the
numbers behind every figure are written to a CSV next to it.

Status marker (GOV-8): a CSV cannot carry a status line safely, so the status of every CSV written here
(fig1..3 .csv) is the one stated at the top of the sibling ``corpus_can_say_v2.md`` (``_v1`` before S179) (AI_DRAFTED / PROPOSED, counts only,
NON_CITABLE). Every SVG carries ``AI_DRAFTED`` in its ``<desc>`` element; the JSON carries a top-level ``status`` key.
"""
from __future__ import annotations

import csv
import html
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s178_analysis_corpus_can_say as T  # noqa: E402

OUT = "reports/s178/analysis"
# S179: v2 names (physics v06 inputs); the v1 files stay on record, so a re-run never overwrites them.
OUT_JSON, OUT_MD = "corpus_can_say_v2.json", "corpus_can_say_v2.md"
FIG_NAMES = ("fig1_heat_time_temperature_joint_v2", "fig2_foodcom_heat_inputs_by_family_v2", "fig3_foodcom_top_unknown_reasons_v2")
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE_RAMP = ["#184a8c", "#2a78d6", "#7fb0ea", "#c4dcf6"]   # sequential, one hue, dark -> light
NEUTRAL = "#cfcec9"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]          # categorical slots 1-4 (adjacent pairs validated in the palette reference)
PROC_FAMILY_ORDER = T.HEAT_FAMILIES
SVG_STATUS = " Status: AI_DRAFTED / PROPOSED, counts only, NON_CITABLE (the sibling .md states the full status)."
SRC_LABEL = {"FOODCOM": "Food.com", "WIKIBOOKS": "Wikibooks", "GUTENBERG_SEGMENT": "Gutenberg", "TASTESET": "TASTEset",
             "A1_BBC_GOOD_FOOD": "BBC (S173 file)"}


# ----------------------------------------------------------------------------- tiny SVG toolkit
def _t(x, y, s, size=12, anchor="start", fill=INK, weight="400"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Inter,Helvetica,Arial,sans-serif" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{html.escape(str(s))}</text>')


def _svg(w, h, body, title, desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-labelledby="t d"><title id="t">{html.escape(title)}</title><desc id="d">{html.escape(desc + SVG_STATUS)}</desc>'
            f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>{body}</svg>\n')


def _legend(items, x, y, gap=18):
    out, cx = [], x
    for color, label in items:
        out.append(f'<rect x="{cx}" y="{y - 10}" width="12" height="12" rx="2" fill="{color}"/>')
        out.append(_t(cx + 17, y, label, 11, fill=INK2))
        cx += 17 + 6.2 * len(label) + gap
    return "".join(out)


def stacked_bars(title, subtitle, rows, classes, colors, width=860):
    """rows: [(label, [pct per class], n_label)] - horizontal 100 % stacked bars with 2 px gaps and direct labels."""
    left, top, bh, gap = 150, 78, 34, 22
    h = top + len(rows) * (bh + gap) + 60
    plot_w = width - left - 40
    b = [_t(24, 28, title, 16, weight="600"), _t(24, 48, subtitle, 12, fill=INK2),
         _legend(list(zip(colors, classes)), 24, 68)]
    for i, (lab, vals, nlab) in enumerate(rows):
        y = top + 14 + i * (bh + gap)
        b.append(_t(left - 10, y + bh / 2 + 4, lab, 12, "end"))
        b.append(_t(left - 10, y + bh / 2 + 18, nlab, 10, "end", INK2))
        x = left
        for v, c in zip(vals, colors):
            w = plot_w * v / 100.0
            if w > 0.4:
                b.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w - 2, 0.5):.1f}" height="{bh}" rx="3" fill="{c}"/>')
                if w >= 40:
                    dark = c in (BLUE_RAMP[0], BLUE_RAMP[1])
                    b.append(_t(x + (w - 2) / 2, y + bh / 2 + 4, f"{v:.1f}", 11, "middle", "#ffffff" if dark else INK))
            x += w
        x, last_x = left, -99.0
        for v, c in zip(vals, colors):
            w = plot_w * v / 100.0
            if 0.4 < w < 40 and (x + w / 2) - last_x >= 26:
                b.append(_t(x + w / 2, y - 4, f"{v:.1f}", 9, "middle", INK2))
                last_x = x + w / 2
            x += w
    b.append(_t(24, h - 18, "Share of heat events (%). Counts only; NON_CITABLE; REAL_BASE_SAMPLE_COUNTS_NOT_GOLD.", 10, fill=INK2))
    return _svg(width, h, "".join(b), title, subtitle)


def grouped_bars(title, subtitle, groups, series, colors, width=900, vmax=100.0):
    """groups: [(label, [value per series])]: horizontal grouped bars (one group per measure)."""
    left, top, bh, sg, gg = 280, 78, 14, 3, 16
    gh = len(series) * (bh + sg)
    h = top + len(groups) * (gh + gg) + 50
    plot_w = width - left - 70
    b = [_t(24, 28, title, 16, weight="600"), _t(24, 48, subtitle, 12, fill=INK2),
         _legend(list(zip(colors, series)), 24, 68)]
    for i in range(0, 101, 25):
        gx = left + plot_w * i / vmax
        b.append(f'<line x1="{gx:.1f}" y1="{top}" x2="{gx:.1f}" y2="{h - 36}" stroke="{GRID}" stroke-width="1"/>')
        b.append(_t(gx, h - 22, f"{i}", 10, "middle", INK2))
    for gi, (lab, vals) in enumerate(groups):
        y0 = top + 8 + gi * (gh + gg)
        b.append(_t(left - 10, y0 + gh / 2 + 3, lab, 12, "end"))
        for si, v in enumerate(vals):
            y = y0 + si * (bh + sg)
            w = plot_w * v / vmax
            b.append(f'<rect x="{left}" y="{y}" width="{max(w, 1):.1f}" height="{bh}" rx="3" fill="{colors[si]}"/>')
            b.append(_t(left + w + 6, y + bh - 3, f"{v:.1f}", 10, fill=INK2))
    return _svg(width, h, "".join(b), title, subtitle)


def hbars(title, subtitle, items, width=860, unit="% of events", color=BLUE_RAMP[1]):
    """items: [(group, label, pct)] rendered as one thin horizontal bar each, grouped with a header."""
    left, top, bh, gap = 330, 62, 13, 6
    n_groups = len({g for g, _, _ in items})
    h = top + len(items) * (bh + gap) + n_groups * 22 + 44
    vmax = max([p for _, _, p in items] + [1.0])
    vmax = 100.0 if vmax > 50 else (50.0 if vmax > 25 else (25.0 if vmax > 10 else 10.0))
    plot_w = width - left - 70
    b = [_t(24, 28, title, 16, weight="600"), _t(24, 48, subtitle, 12, fill=INK2)]
    y, last = top, None
    for g, lab, p in items:
        if g != last:
            y += 14
            b.append(_t(24, y + 4, g, 12, fill=INK, weight="600"))
            y += 8
            last = g
        w = plot_w * p / vmax
        b.append(_t(left - 10, y + bh - 2, lab, 11, "end", INK2))
        b.append(f'<rect x="{left}" y="{y}" width="{max(w, 1):.1f}" height="{bh}" rx="3" fill="{color}"/>')
        b.append(_t(left + w + 6, y + bh - 2, f"{p:.1f}", 10, fill=INK2))
        y += bh + gap
    b.append(_t(24, h - 14, f"{unit}; bar scale 0 to {vmax:g}. Counts only; NON_CITABLE.", 10, fill=INK2))
    return _svg(width, h, "".join(b), title, subtitle)


# ----------------------------------------------------------------------------- numbers
def P(a, b):
    return T.pct(a, b)


def joint_classes(c: Counter) -> dict:
    """Exclusive classes over heat events from the derived (reconciled) joint table."""
    g = lambda t, tt: c[("joint", t, "T:" + tt)]  # noqa: E731
    n = c[("n", "-")]
    A = g("tS", "TEXT_STATED")
    B = g("tS", "CARRIED_SETPOINT") + g("tS", "PHYSICAL_DEFINITION")
    C = g("tS", "UNKNOWN")
    D = sum(g("tU", x) for x in ("TEXT_STATED", "CARRIED_SETPOINT", "PHYSICAL_DEFINITION"))
    E = g("tU", "UNKNOWN")
    assert A + B + C + D + E == n, (A, B, C, D, E, n)
    return {"n": n, "t_and_T_text": A, "t_and_T_carried_or_definition_only": B, "t_only_T_unknown": C,
            "T_known_t_unknown": D, "neither": E}


def cov_row(c: Counter) -> dict:
    n = c[("n", "-")]
    t_s = c[("dur", "MEASURED")] + c[("dur", "RANGE")]
    tt = sum(v for k, v in c.items() if k[0] == "temp" and k[2] == "TEXT_STATED")
    ta = sum(v for k, v in c.items() if k[0] == "temp" and k[1] != "UNKNOWN")
    both = c[("joint", "tS", "T:TEXT_STATED")]
    bnd = sum(v for k, v in c.items() if k[0] == "joint" and k[1] == "tS" and k[2] != "T:UNKNOWN")
    inp = lambda name: sum(v for k, v in c.items() if k[0] == "in:" + name and k[1] != "UNKNOWN")  # noqa: E731
    return {"events": n, "t_stated": t_s, "t_range": c[("dur_range", "-")], "T_text_stated": tt, "T_any_bound": ta,
            "T_range": c[("temp_range", "-")], "both_t_and_T_text_stated": both, "t_stated_and_T_any": bnd,
            "gas_mark_only": sum(v for k, v in c.items() if k[0] == "gas_mark"),
            "medium_known": inp("medium"), "piece_size_known": inp("piece_size_class"), "lid_known": inp("lid_state"),
            "start_mode_known": inp("start_mode"), "matrix_class_known": inp("matrix_class"),
            "pct": {k: P(v, n) for k, v in {"t_stated": t_s, "T_text_stated": tt, "T_any_bound": ta, "both_text": both,
                                            "t_and_T_any": bnd, "medium": inp("medium"), "size": inp("piece_size_class"),
                                            "lid": inp("lid_state"), "start": inp("start_mode")}.items()}}


def nh_row(c: Counter) -> dict:
    n = c[("n", "-")]
    dur = sum(c[("dur", s)] for s in T.NH_DUR_STATED)
    dur_exact = c[("dur", "MEASURED")] + c[("dur", "RANGE")]
    ta = c[("temp_applicable", "-")]
    ts = c[("temp", "STATED")]
    both = c[("joint", "tS", "T:S")]
    size = c[("in:piece_size_class", "QUALITATIVE")] + c[("in:piece_size_class", "MEASURED")]
    size_applicable = sum(v for k, v in c.items() if k[0] == "in:piece_size_class")
    return {"events": n, "t_stated_incl_bounds": dur, "t_measured_or_range": dur_exact,
            "temperature_applicable_events": ta, "T_stated": ts, "both_t_and_T_stated": both,
            "size_class_applicable": size_applicable, "size_class_known": size,
            "pct": {"t_stated_incl_bounds": P(dur, n), "t_measured_or_range": P(dur_exact, n),
                    "T_stated_of_applicable": P(ts, ta) if ta else None, "both_of_applicable": P(both, ta) if ta else None,
                    "size_known_of_applicable": P(size, size_applicable) if size_applicable else None}}


def top_reasons(counter: Counter, n: int) -> list:
    tot = sum(counter.values())
    return [{"reason": k, "events": v} for k, v in counter.most_common(n)] if tot else []


# ----------------------------------------------------------------------------- build the report
def render(root: Path, agg_path: Path) -> int:
    B = T.build(root, agg_path)
    out = B["out"]
    heat_flat, nh_flat = B["heat_flat"], B["nh_flat"]
    h_src, h_fam = T.rollup(heat_flat, "src"), T.rollup(heat_flat, "fam")
    n_src, n_fam = T.rollup(nh_flat, "src"), T.rollup(nh_flat, "fam")
    proc = B["proc_name"]
    out_dir = root / OUT
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- heat: source level (committed JSON values, with path)
    out["heat"] = {"source_level_from_committed_census": B["heat_rows"]}
    # ---- heat: derived cross-tabs
    heat_src = {s: cov_row(h_src[(s,)]) for s in T.SOURCES if (s,) in h_src}
    heat_joint = {s: joint_classes(h_src[(s,)]) for s in T.SOURCES if (s,) in h_src}
    heat_fam = {f"{s}|{f}": cov_row(c) for (s, f), c in sorted(h_fam.items())}
    # by process
    by_proc: dict[str, dict] = {}
    for (s, f, pid), _ in T.split_keys(heat_flat).items():
        pass
    procs: dict[tuple, Counter] = {}
    for k, v in heat_flat.items():
        s, f, pid, *rest = k.split("|")
        procs.setdefault((s, f, pid), Counter())[tuple(rest)] += v
    for (s, f, pid), c in sorted(procs.items()):
        r = cov_row(c)
        r["proc_canonical_name"], r["proc_registry_family"] = proc.get(pid, ("UNKNOWN", ""))
        r["l1_family"] = f
        by_proc[f"{s}|{pid}"] = r
    # L2 unknown reasons per source x family
    l2 = {}
    for (s, f), c in sorted(h_fam.items()):
        st = Counter({k[1]: v for k, v in c.items() if k[0] == "l2status"})
        miss = Counter({k[1]: v for k, v in c.items() if k[0] == "l2missing"})
        sets = Counter({k[1]: v for k, v in c.items() if k[0] == "l2missing_set"})
        n = c[("n", "-")]
        l2[f"{s}|{f}"] = {"events": n, "status": dict(st), "pct_scenario_computed": P(st["SCENARIO_COMPUTED"], n),
                          "pct_scenario_unknown": P(st["SCENARIO_UNKNOWN"], n),
                          "top_missing_inputs": [{"input": k, "events": v, "pct_of_events": P(v, n)} for k, v in miss.most_common(5)],
                          "top_missing_sets": [{"set": k, "events": v, "pct_of_events": P(v, n)} for k, v in sets.most_common(4)]}
    out["heat"].update({"derived_by_source": heat_src, "joint_exclusive_classes_by_source": heat_joint,
                        "derived_by_source_and_family": heat_fam, "derived_by_process": by_proc,
                        "l2_unknown_reasons_by_source_and_family": l2,
                        "derivation": f"per-event L1 and L2 ({T.LAYER_TAG}) records under data/derived, aggregated by this tool; "
                                      "totals reconciled to the committed census JSONs (see reconciliation block)"})

    # ---- non-heat
    nh_src = {s: nh_row(n_src[(s,)]) for s in T.SOURCES if (s,) in n_src}
    nh_fam = {f"{s}|{f}": nh_row(c) for (s, f), c in sorted(n_fam.items())}
    nh_role: dict[str, dict] = {}
    roles: dict[tuple, Counter] = {}
    for k, v in nh_flat.items():
        s, f, role, *rest = k.split("|")
        roles.setdefault((s, f, role), Counter())[tuple(rest)] += v
    for (s, f, role), c in sorted(roles.items()):
        nh_role[f"{s}|{f}|{role}"] = nh_row(c)
    # committed JSON: unknown reasons (L1) and L2 missing reasons
    nh_l1_reasons, nh_l2_reasons = {}, {}
    for s, d in B["nh_census"].items():
        nh_l1_reasons[s] = {"source": T.nh_l1_paths()[s], "events_by_family": d.get("events_by_family"),
                            "unknown_reasons": d.get("unknown_reasons"), "missing_core_inputs": d.get("missing_core_inputs"),
                            "events": d.get("nonheat_events")}
    for s, d in B["n2_census"].items():
        c = d.get("counts") or {}
        nh_l2_reasons[s] = {"source": T.nh_l2_paths()[s], "missing_reasons": c.get("missing_reasons"),
                            "events_by_family": c.get("events_by_family"), "status": c.get("status"),
                            "l2_driver_computed_by_family": c.get("l2_driver_computed_by_family"),
                            "l2_qualitative_or_conditions_by_family": c.get("l2_qualitative_or_conditions_by_family")}
    h2 = {s: {"source": T.heat_l2_paths()[s], "status": (d.get("counts") or {}).get("status"),
              "transition": (d.get("counts") or {}).get("transition"), "labels": d.get("labels"),
              "layer_version": d.get("layer_version")} for s, d in B["h2_census"].items()}
    out["nonheat"] = {"derived_by_source": nh_src, "derived_by_source_and_family": nh_fam, "derived_by_role": nh_role,
                      "l1_unknown_reasons_from_committed_census": nh_l1_reasons,
                      "l2_missing_reasons_from_committed_census": nh_l2_reasons,
                      "temperature_applicable_note": "temperature coverage counts only events whose family carries a medium or target temperature "
                                                     "input (COOLING, FERMENT_LEAVEN, PRESERVATION, STORAGE); cut, mix, separate and rest have none"}
    out["heat_l2_status_from_committed_census"] = h2

    # ---- figures
    figs = []
    # F1 joint classes by source
    srcs = [s for s in ("FOODCOM", "WIKIBOOKS", "GUTENBERG_SEGMENT") if s in heat_joint]
    cl_names = ["t and T in text", "t in text, T carried/defined", "t in text only", "T known, t unknown", "neither"]
    cl_keys = ["t_and_T_text", "t_and_T_carried_or_definition_only", "t_only_T_unknown", "T_known_t_unknown", "neither"]
    rows = []
    csv1 = [["source", "heat_events"] + cl_keys + [k + "_pct" for k in cl_keys]]
    for s in srcs:
        j = heat_joint[s]
        vals = [P(j[k], j["n"]) for k in cl_keys]
        rows.append((SRC_LABEL[s], vals, f"{j['n']:,} heat events"))
        csv1.append([s, j["n"]] + [j[k] for k in cl_keys] + vals)
    f1 = stacked_bars("What the recipe text gives a heat event: time t and temperature T",
                      f"Exclusive classes, share of heat events per source (L1 TEXT_STATED, {T.LAYER_TAG} records, reconciled to the census JSONs)",
                      rows, cl_names, BLUE_RAMP + [NEUTRAL])
    figs.append((FIG_NAMES[0], f1, csv1))
    # F2 FOODCOM heat families x measures
    measures = [("t stated (value or range)", "t_stated"), ("T stated in the recipe text", "T_text_stated"), ("T bound (text, carried, definition)", "T_any_bound"),
                ("t and T both in the text", "both_text"), ("medium known (process definition)", "medium"),
                ("piece size class known (cut history)", "size")]
    groups, csv2 = [], [["measure"] + [f"FOODCOM|{f}" for f in T.HEAT_FAMILIES]]
    for lab, key in measures:
        vals = [heat_fam[f"FOODCOM|{f}"]["pct"][key] for f in T.HEAT_FAMILIES]
        groups.append((lab, vals))
        csv2.append([lab] + vals)
    fam_n = "; ".join(f"{f} {heat_fam[f'FOODCOM|{f}']['events']:,}" for f in T.HEAT_FAMILIES)
    f2 = grouped_bars("Food.com heat events: which inputs the text binds, by process family",
                      f"Share of events in each L1 process family ({T.LAYER_TAG}; {fam_n})",
                      groups, list(T.HEAT_FAMILIES), CAT)
    figs.append((FIG_NAMES[1], f2, csv2))
    # F3 top UNKNOWN reasons per family (heat: L2 missing inputs; non-heat: L1 reasons) Food.com
    items, csv3 = [], [["layer", "family", "reason", "events", "pct_of_family_events"]]
    for f in T.HEAT_FAMILIES:
        e = l2[f"FOODCOM|{f}"]
        n = e["events"]
        for m in e["top_missing_inputs"][:3]:
            items.append((f"Heat {f} (L2 {T.LAYER_TAG} SCENARIO_UNKNOWN missing input)", m["input"], m["pct_of_events"]))
            csv3.append(["heat_L2", f, m["input"], m["events"], m["pct_of_events"]])
    d = B["nh_census"].get("FOODCOM") or {}
    evf = d.get("events_by_family") or {}
    for f in T.NH_FAMILIES:
        reasons = Counter()
        for inp, rr in ((d.get("unknown_reasons") or {}).get(f) or {}).items():
            for code, c in rr.items():
                reasons[f"{inp}: {code}"] += c
        for k, v in reasons.most_common(2):
            items.append((f"Non-heat {f} (L1 UNKNOWN reason)", k, P(v, evf.get(f, 0))))
            csv3.append(["nonheat_L1", f, k, v, P(v, evf.get(f, 0))])
    f3 = hbars("Food.com: top UNKNOWN reasons per process family",
               f"Heat: inputs missing on SCENARIO_UNKNOWN events (L2 {T.LAYER_TAG}). Non-heat: L1 UNKNOWN reason codes. % of that family's events.", items)
    figs.append((FIG_NAMES[2], f3, csv3))
    out["figures"] = []
    for name, svg, rows_ in figs:
        (out_dir / f"{name}.svg").write_text(svg, encoding="utf-8")
        with open(out_dir / f"{name}.csv", "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerows(rows_)
        out["figures"].append({"svg": f"{OUT}/{name}.svg", "csv": f"{OUT}/{name}.csv"})

    out["notes"] = [
        "t = stated time (duration MEASURED or RANGE, basis TEXT_STATED). T = temperature; 'text-stated' means basis TEXT_STATED; CARRIED_SETPOINT is an oven setting stated earlier and carried to the event; PHYSICAL_DEFINITION is a physical definition (water boils at 100 C at 1 atm).",
        "Gas mark: an event whose L1 record keeps an oven_setpoint_code with no converted temperature (the L1 layer does not convert a gas mark; every such event has T UNKNOWN).",
        "Medium is bound mostly from the process definition (basis PROCESS_DEFINITION: a verb such as fry or simmer implies it), not from a medium named in the recipe text; see the input_basis block of each census file.",
        "Piece size class comes from the cut history of the food (CUT_HISTORY), not from a size stated at the heat step.",
        "TASTEset has no step lists (0 heat events). BBC is not in these tables: its v06 censuses (binding_census_L1_A1_full_S179_v06.json and siblings) and records exist only on the Mac (D-003); this tool runs where the non-BBC records are.",
        f"Inputs: every census file is {T.LAYER_TAG} (FIX-GOV repoint; the first build of this table read the superseded S176 v02 / S176 / S177 v03 files) and no input is listed in registry/superseded_outputs_S176.csv (checked before reading).",
        "The Layer-2 columns are SCENARIO values (ASSUMED_DEFAULT, MODEL_DERIVED, NON_CITABLE); they are shown only for their UNKNOWN reasons.",
        "Reconciliation: derived totals equal the committed census totals for every source (heat events, duration, temperature, medium, size, lid, start mode, water ratio, matrix class, gas mark, driver-bounded, L2 status; non-heat events).",
    ]
    (out_dir / OUT_JSON).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / OUT_MD).write_text(markdown(out, B, heat_src, heat_joint, heat_fam, by_proc, l2, nh_src, nh_fam), encoding="utf-8")
    print(json.dumps({"reconciliation": out["reconciliation"]["status"], "errors": out["reconciliation"]["errors"][:5]}))
    return 0 if not B["errors"] else 3


# ----------------------------------------------------------------------------- markdown
def markdown(out, B, heat_src, heat_joint, heat_fam, by_proc, l2, nh_src, nh_fam) -> str:
    rows = B["heat_rows"]
    L = ["# What the corpus can say: stated time, temperature, size, medium (S178, T4-C04-R1)", "",
         "Status: AI_DRAFTED / PROPOSED, counts only, NON_CITABLE, REAL_BASE_SAMPLE_COUNTS_NOT_GOLD. Layer 1 TEXT_STATED unless a table says L2.",
         "Every number below is either a field of a committed census JSON (path given) or a cross-tab of the per-event records those censuses wrote (reconciled to the same JSONs: "
         f"**{out['reconciliation']['status']}**, alignment errors heat L1/L2 {out['reconciliation']['alignment_errors_heat_l1_l2']}).", "",
         "t = stated time (value or range). T = temperature; **text** = stated in the recipe sentence, **bound** = text + a carried oven setting + a physical definition (boil = 100 C).", "",
         "## 1. Heat events by source (committed census JSON fields)", "",
         "| source | census file | heat events | t stated | T text-stated | T bound | t and T both text | t stated and T bound | ranges (t / T) | gas-mark only | medium | size class |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in ("FOODCOM", "WIKIBOOKS", "GUTENBERG_SEGMENT", "A1_BBC_GOOD_FOOD"):
        r = rows.get(s)
        if not r or not r["heat_events"]:
            continue
        n = r["heat_events"]
        d = heat_src.get(s)
        both = f"{d['pct']['both_text']} %" if d else "n/a (no records on this server)"
        L.append(f"| {SRC_LABEL[s]} | `{r['census_path'].split('/')[-1]}` | {n:,} | {P(r['duration_stated'], n)} % | {P(r['temperature_text_stated'], n)} % | "
                 f"{P(r['temperature_any'], n)} % | {both} | {P(r['driver_bounded_events'], n)} % | {P(r['duration_range'], n)} / {P(r['temperature_range'], n)} % | "
                 f"{r['gas_mark_only_events']:,} | {P(r['medium_known'], n)} % | {P(r['piece_size_known'], n)} % |")
    L += ["", "TASTEset: 0 heat events (no step lists). BBC: v06 censuses exist only on the Mac (D-003), not on this server. Medium is bound on most events only through the process definition; size class only through the cut history.", "",
          "## 2. Joint time and temperature (exclusive classes, % of heat events; figure 1)", "",
          "| source | t and T in text | t in text, T carried or defined | t only | T known, t unknown | neither |", "|---|---:|---:|---:|---:|---:|"]
    for s, j in heat_joint.items():
        n = j["n"]
        L.append(f"| {SRC_LABEL[s]} ({n:,}) | {P(j['t_and_T_text'], n)} | {P(j['t_and_T_carried_or_definition_only'], n)} | {P(j['t_only_T_unknown'], n)} | {P(j['T_known_t_unknown'], n)} | {P(j['neither'], n)} |")
    L += ["", f"![fig1]({FIG_NAMES[0]}.svg)", "",
          "## 3. Heat events by source and process family (L1 families; % of the family's events)", "",
          "| source | family | events | t stated | T text | T bound | t and T text | medium | size class | lid | start mode |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k, r in heat_fam.items():
        s, f = k.split("|")
        p = r["pct"]
        L.append(f"| {SRC_LABEL[s]} | {f} | {r['events']:,} | {p['t_stated']} | {p['T_text_stated']} | {p['T_any_bound']} | {p['both_text']} | {p['medium']} | {p['size']} | {p['lid']} | {p['start']} |")
    L += ["", f"![fig2]({FIG_NAMES[1]}.svg)", "",
          "## 4. Food.com heat events by process (top 15 PROC by events)", "",
          "| PROC | name | L1 family | events | t stated | T text | T bound | t and T text | gas mark | size class |", "|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    fc = sorted(((k, r) for k, r in by_proc.items() if k.startswith("FOODCOM|")), key=lambda kv: -kv[1]["events"])[:15]
    for k, r in fc:
        p = r["pct"]
        L.append(f"| {k.split('|')[1]} | {r['proc_canonical_name']} | {r['l1_family']} | {r['events']:,} | {p['t_stated']} | {p['T_text_stated']} | {p['T_any_bound']} | {p['both_text']} | {r['gas_mark_only']} | {p['size']} |")
    L += ["", f"All sources and all processes are in `{OUT_JSON}` under `heat.derived_by_process`.", "",
          f"## 5. Non-heat families (Food.com, {T.LAYER_TAG} L1 records; % of the family's events)", "",
          "| family | events | t stated (value, range, bound) | t value or range | events with a temperature input | T stated (of those) | t and T both (of those) | size class known (of applicable) |",
          "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for f in T.NH_FAMILIES:
        r = nh_fam.get(f"FOODCOM|{f}")
        if not r:
            continue
        p = r["pct"]
        nz = lambda v: "n/a" if v is None else v  # noqa: E731
        L.append(f"| {f} | {r['events']:,} | {p['t_stated_incl_bounds']} | {p['t_measured_or_range']} | {r['temperature_applicable_events']:,} | {nz(p['T_stated_of_applicable'])} | {nz(p['both_of_applicable'])} | {nz(p['size_known_of_applicable'])} |")
    L += ["", f"Other sources are in `{OUT_JSON}` under `nonheat.derived_by_source_and_family`. n/a = the family has no such input (cut, mix, separate, rest carry no medium temperature; size class is not defined for mixing, separating or storing).", "",
          "## 6. Per-family top UNKNOWN reasons (Food.com; figure 3)", "",
          f"Heat families, Layer 2 {T.LAYER_TAG} (`{T.DERIVED}/{T.HEAT_L2_DIR}`, status counts equal `{T.heat_l2_paths()['FOODCOM'].split('/')[-1]}`): the inputs missing on SCENARIO_UNKNOWN events.", "",
          "| family | events | SCENARIO_COMPUTED | SCENARIO_UNKNOWN | UNSUPPORTED_MEDIUM | top missing inputs (events, % of family events) |", "|---|---:|---:|---:|---:|---|"]
    for f in T.HEAT_FAMILIES:
        e = l2[f"FOODCOM|{f}"]
        st = e["status"]
        tm = "; ".join(f"{m['input']} {m['events']:,} ({m['pct_of_events']} %)" for m in e["top_missing_inputs"][:3])
        L.append(f"| {f} | {e['events']:,} | {st.get('SCENARIO_COMPUTED', 0):,} | {st.get('SCENARIO_UNKNOWN', 0):,} | {st.get('UNSUPPORTED_MEDIUM', 0):,} | {tm} |")
    L += ["", f"Non-heat families, Layer 1 UNKNOWN reason codes (`{T.nh_l1_paths()['FOODCOM']}`, key `unknown_reasons`):", "",
          "| family | events | top UNKNOWN reasons (input: code, events, % of family events) |", "|---|---:|---|"]
    d = B["nh_census"].get("FOODCOM") or {}
    evf = d.get("events_by_family") or {}
    for f in T.NH_FAMILIES:
        reasons = Counter()
        for inp, rr in ((d.get("unknown_reasons") or {}).get(f) or {}).items():
            for code, c in rr.items():
                reasons[f"{inp}: {code}"] += c
        if not reasons:
            L.append(f"| {f} | {evf.get(f, 0):,} | (no UNKNOWN reason code in the L1 file; see the L2 missing reasons below) |")
            continue
        L.append(f"| {f} | {evf.get(f, 0):,} | " + "; ".join(f"{k} {v:,} ({P(v, evf.get(f, 0))} %)" for k, v in reasons.most_common(3)) + " |")
    L += ["", f"![fig3]({FIG_NAMES[2]}.svg)", "",
          f"Non-heat Layer 2 {T.LAYER_TAG} missing reasons (committed `{T.nh_l2_paths()['FOODCOM'].split('/')[-1]}`, `counts.missing_reasons`):", ""]
    mr = ((B["n2_census"].get("FOODCOM") or {}).get("counts") or {}).get("missing_reasons") or {}
    for f in sorted(mr):
        L.append(f"- {f}: " + ", ".join(f"{k} {v:,}" for k, v in sorted(mr[f].items(), key=lambda kv: -kv[1])[:4]))
    L += ["", "## 7. What the corpus can say, in one paragraph per layer", ""]
    fcs = heat_src.get("FOODCOM")
    j = heat_joint.get("FOODCOM")
    if fcs and j:
        L.append(f"- **Heat, Food.com ({fcs['events']:,} events).** The text states a time on {fcs['pct']['t_stated']} % of heat events and a temperature on {fcs['pct']['T_text_stated']} %; "
                 f"both in the text on {fcs['pct']['both_text']} %. Counting a carried oven setting and the physical definition of boiling, a temperature is bound on {fcs['pct']['T_any_bound']} % and "
                 f"time and temperature together on {fcs['pct']['t_and_T_any']} %. {P(j['neither'], j['n'])} % of heat events have neither.")
    hg = heat_fam.get("FOODCOM|HEAT_GENERAL")
    lg = l2.get("FOODCOM|HEAT_GENERAL")
    if hg and lg:
        L.append(f"- **Layer 2** (scenario defaults) turns a bound event into a physically_possible trajectory only; it adds no stated value. In Food.com the largest block of UNKNOWN is the generic verbs (HEAT_GENERAL, {hg['events']:,} events: cook, heat, melt and the like): "
                 f"{hg['pct']['medium']} % of them have a medium and {lg['status'].get('SCENARIO_COMPUTED', 0):,} reach SCENARIO_COMPUTED; {lg['pct_scenario_unknown']} % are SCENARIO_UNKNOWN, missing "
                 + ", ".join(f"{m['input']} ({m['pct_of_events']} %)" for m in lg["top_missing_inputs"][:2]) + ".")
    ndur = {f: r["pct"]["t_stated_incl_bounds"] for f in T.NH_FAMILIES if (r := nh_fam.get(f"FOODCOM|{f}"))}
    nT = {f: r["pct"]["T_stated_of_applicable"] for f in T.NH_FAMILIES if (r := nh_fam.get(f"FOODCOM|{f}")) and r["pct"]["T_stated_of_applicable"] is not None}
    if ndur and nT:
        lo_f, hi_f = min(ndur, key=ndur.get), max(ndur, key=ndur.get)
        L.append(f"- **Non-heat (Food.com).** A duration (value, range or bound) is stated on {ndur[lo_f]} % ({lo_f}) to {ndur[hi_f]} % ({hi_f}) of events by family; where a family has a medium or "
                 f"target temperature input, it is stated on at most {max(nT.values())} % of events. So these families can carry duration-keyed flags and qualitative states; the text gives almost no temperature to key a number on.")
    L += ["", "## 8. Notes", ""] + [f"- {n}" for n in out["notes"]]
    L += ["", "## 9. Provenance", "", f"- Tool `{out['tool_version']}`; derived aggregate sha256 `{out['inputs']['derived_aggregate_sha256']}`.",
          "- Committed census inputs (sha256):"] + [f"  - `{p}` `{h[:16]}`" for p, h in out["inputs"]["committed_census_files"].items()]
    return "\n".join(L) + "\n"
