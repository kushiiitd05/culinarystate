#!/usr/bin/env python
"""Sensitivity report of the GENTLE-INTENSE bracket (S178 PHYS2, T4-C05-R1): counts and quantiles only. DRAFT, AI_DRAFTED.

    python tools/s178_phys_sensitivity.py --heat-l2 data/derived/physical_L2_full_S178v04/FOODCOM [more dirs] \
        --nonheat-l2 data/derived/physical_NH_L2_FOODCOM_full_S178v04 [more dirs] \
        --out reports/s178/phys/sensitivity_S178_v04.json --out-md reports/s178/phys/sensitivity_S178_v04.md --workers 8

Per process family (the PROC family registry, ``registry/proc_family_registry_v1.csv``): the width INTENSE - GENTLE of the inputs
and of the outputs, the share of events whose qualitative conclusion changes between the three brackets, and the reasons for
SCENARIO_UNKNOWN. A conclusion of one event is ROBUST_YES / ROBUST_NO when GENTLE, TYPICAL and INTENSE agree and FRAGILE when they do
not; a conclusion of a family is flagged ROBUST when the fragile share is at most ``FRAGILE_SHARE_THRESHOLD`` (PROPOSED 0.10) and
FRAGILE otherwise. The thresholds of the conclusions (core >= 70 C, cooling to 5 or 60 C, half uptake) are reporting thresholds, not
food-safety or doneness criteria. The brackets are scenario defaults (ASSUMED_DEFAULT, MODEL_DERIVED, NON_CITABLE): a ROBUST flag
says the conclusion does not depend on where in the scenario ranges the event sits, not that it is true of food.

S178 FIX-PHYS (1.1.0, SCI-A M6 / m8; Q3 ruling PROPOSED): the report carries the CAVEAT below (JSON ``caveat``, md first section):
the bracket is a joint corner of one boundary-condition model; the boundary-model and pan-geometry uncertainty is not bracketed;
ROBUST means robust within the Robin-at-T_cap model; the stated-oven-temperature finding is a consequence of the cap. The basis
kinds are split (TEXT_STATED / CARRIED_SETPOINT / PHYSICAL_DEFINITION / DEFAULT, m8: a WET_HEAT "stated" bath was mostly the boil
by definition) and "reaches 70 C" uses one test for the core and the volume average (end value >= 70 C; for a heating slab the
end value is the maximum). The boundary-model axis (fixed-T_boil surface) is OPEN (not computed here).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

VERSION = "phys-sensitivity-1.1.0-draft"
VERSION_V10 = "phys-sensitivity-1.0.0-draft"  # SUPERSEDED: no caveat, STATED basis kind lumped L1 bases, two reach-70 tests
CAVEAT = (
    "CAVEAT (S178 FIX-PHYS, SCI-A M6; Q3 PROPOSED, for Kush): (1) GENTLE and INTENSE are JOINT corners: every scenario input moves to "
    "its low or high end together (bath, duration, film coefficient h, piece half-thickness, start temperature), so the GENTLE-INTENSE "
    "spread is a corner-to-corner range, not a sensitivity estimate of any one input and not a probability. (2) The bracket stays "
    "inside ONE boundary-condition model (Robin at T_cap with the medium's h). The boundary-model uncertainty (a fixed T_boil surface, "
    "a wet-bulb plateau) and the pan geometry (pan contact is the two-sided fast end only) are NOT bracketed; for moist pieces in dry or "
    "fat heat they can dominate (a 1 cm dice in an oven for 3 min: core about 34 C with Robin h 25 at 100 C against about 92 C with a "
    "fixed 100 C surface). (3) ROBUST therefore means robust within the Robin-at-T_cap model, not robust to the model. (4) The finding "
    "that a stated oven or oil temperature alone does not narrow 'core reaches 70 C' is a consequence of the cap: under the cap a moist "
    "core never sees the oven or oil set-point, only min(T_medium, T_boil).")
CAVEAT_CODES = ("JOINT_CORNERS_NOT_A_SENSITIVITY_ESTIMATE", "ONE_BOUNDARY_MODEL_ROBIN_AT_TCAP",
                "BOUNDARY_MODEL_UNCERTAINTY_NOT_BRACKETED", "PAN_GEOMETRY_NOT_BRACKETED_TWO_SIDED_FAST_END_ONLY",
                "ROBUST_MEANS_ROBUST_WITHIN_ROBIN_AT_TCAP_MODEL", "STATED_OVEN_OR_OIL_T_RESULT_IS_A_CONSEQUENCE_OF_THE_CAP")
BASIS_KINDS = ("TEXT_STATED", "CARRIED_SETPOINT", "PHYSICAL_DEFINITION", "DEFAULT")
FRAGILE_SHARE_THRESHOLD = 0.10
BR = ("GENTLE", "TYPICAL", "INTENSE")
QUANT = (("p10", 0.1), ("p50", 0.5), ("p90", 0.9), ("max", 1.0))
CORE_C = 70.0
CHILL_C, HOT_C = 5.0, 60.0
HEAT_CONCLUSIONS = ("core_reaches_70c", "volume_average_reaches_70c", "evaporation_cap_binds", "surface_state_unchanged")
NONHEAT_CONCLUSIONS = {
    "COOLING": ("core_end_at_or_below_5c", "core_end_at_or_below_60c", "frozen_within_stated_duration", "thawed_within_stated_duration"),
    "RESTING": ("core_end_at_or_above_60c",), "FERMENT_LEAVEN": ("uptake_at_least_half",), "PRESERVATION": ("time_class_unchanged",)}
_FAMS: dict = {}


def _family_of(pid: str) -> str:
    if not _FAMS:
        with open(ROOT / "registry/proc_family_registry_v1.csv", newline="", encoding="utf-8") as fh:
            _FAMS.update({r["proc_id"]: r["primary_family"] for r in csv.DictReader(fh)})
    return _FAMS.get(pid, "UNMAPPED_PROC")


def verdict(vals: list) -> str | None:
    """ROBUST_YES / ROBUST_NO / FRAGILE across the three brackets, or None when a bracket has no value."""
    if len(vals) != 3 or any(v is None for v in vals):
        return None
    return "ROBUST_YES" if all(vals) else "ROBUST_NO" if not any(vals) else "FRAGILE"


def _basis_kind(b) -> str:
    """m8: TEXT_STATED / CARRIED_SETPOINT / PHYSICAL_DEFINITION (or another L1 basis) / DEFAULT (any scenario row)."""
    b = str(b or "")
    if b.startswith("L1:"):
        return b[3:].split("|")[0] or "L1_OTHER"
    return "DEFAULT"


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


# ------------------------------------------------------------------------------------------------ per-file workers
def heat_file(path: str) -> dict:
    c: Counter = Counter()
    vals: dict = {}

    def put(k, v):
        vals.setdefault(k, []).append(v)

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            fam = _family_of(r["process_id"])
            c[("events", fam)] += 1
            c[("status", fam, r["status"])] += 1
            if r["status"] == "SCENARIO_UNKNOWN":
                miss = sorted(r.get("missing") or [])
                c[("missing_set", fam, "__".join(miss) or "NONE")] += 1
                for m in miss:
                    c[("missing_each", fam, m)] += 1
                continue
            if r["status"] == "UNSUPPORTED_MEDIUM":
                c[("unsupported_medium", fam, str(r.get("medium")))] += 1
                continue
            sc = r["scenarios"]
            if not all(b in sc for b in BR):
                c[("incomplete_brackets", fam)] += 1
                continue
            g, t, i = sc["GENTLE"], sc["TYPICAL"], sc["INTENSE"]
            c[("computed", fam)] += 1
            kinds = f"bath_{_basis_kind(t['bases'].get('bath_c'))}_duration_{_basis_kind(t['bases'].get('duration_min'))}"
            c[("by_basis_computed", fam, kinds)] += 1
            put((fam, "bath_c"), abs(i["bath_c"] - g["bath_c"]))
            put((fam, "duration_min"), abs(i["duration_min"] - g["duration_min"]))
            core = [s.get("core_end_c") for s in (g, t, i)]
            has_core = all(_num(x) for x in core)
            if has_core:
                c[("core_computed", fam)] += 1
                put((fam, "core_end_c"), abs(core[2] - core[0]))
                put((fam, "volume_avg_end_c"), abs(i["volume_avg_end_c"] - g["volume_avg_end_c"]))
                put((fam, "core_minutes_above_70"), abs(i["core_minutes_above_70"] - g["core_minutes_above_70"]))
                dg, di = g.get("core_cook_value_min"), i.get("core_cook_value_min")
                if _num(dg) and _num(di) and dg > 0 and di > 0:
                    put((fam, "core_dose_log10_ratio"), math.log10(di / dg))
                zg, zi = g.get("zone_mean_cook_value_min"), i.get("zone_mean_cook_value_min")
                if _num(zg) and _num(zi) and zg > 0 and zi > 0:
                    put((fam, "zone_mean_dose_log10_ratio"), math.log10(zi / zg))
                v = verdict([s["core_end_c"] >= CORE_C for s in (g, t, i)])  # m8: one test (end value) for core and volume average
                c[("conclusion", fam, "core_reaches_70c", v)] += 1
                c[("by_basis_conclusion", fam, kinds, "core_reaches_70c", v)] += 1
                put((kinds, "core_end_c_width", fam), abs(core[2] - core[0]))
                v = verdict([s["volume_avg_end_c"] >= CORE_C for s in (g, t, i)])
                c[("conclusion", fam, "volume_average_reaches_70c", v)] += 1
            else:
                for s in (g, t, i):
                    for f in s["flags"]:
                        if f.startswith("CORE_UNKNOWN"):
                            c[("core_unknown_reason", fam, f)] += 1
                            break
            c[("conclusion", fam, "evaporation_cap_binds", verdict(["EVAPORATION_CAP_APPLIED" in s["flags"] for s in (g, t, i)]))] += 1
            ss = [s.get("surface_state") for s in (g, t, i)]
            if all(x is not None for x in ss):
                c[("conclusion", fam, "surface_state_unchanged", "ROBUST_YES" if len(set(ss)) == 1 else "FRAGILE")] += 1
    return {"c": dict(c), "vals": vals}


def _nh_conclusions(fam: str, sc: dict) -> dict:
    g, t, i = (sc[b] for b in BR)
    out: dict = {}
    if fam == "COOLING":
        ce = [s.get("core_end_c") for s in (g, t, i)]
        if all(_num(x) for x in ce):
            out["core_end_at_or_below_5c"] = verdict([x <= CHILL_C for x in ce])
            out["core_end_at_or_below_60c"] = verdict([x <= HOT_C for x in ce])
        for k in ("frozen_within_stated_duration", "thawed_within_stated_duration"):
            vs = [s.get(k) for s in (g, t, i)]
            if all(isinstance(x, bool) for x in vs):
                out[k] = verdict(vs)
    elif fam == "RESTING":
        ce = [s.get("core_end_c") for s in (g, t, i)]
        if all(_num(x) for x in ce):
            out["core_end_at_or_above_60c"] = verdict([x >= HOT_C for x in ce])
    elif fam in ("FERMENT_LEAVEN", "PRESERVATION"):
        up = [s.get("uptake_fraction") for s in (g, t, i)]
        if all(_num(x) for x in up):
            out["uptake_at_least_half"] = verdict([x >= 0.5 for x in up])
        tc = [s.get("time_class") for s in (g, t, i)]
        if fam == "PRESERVATION" and all(x is not None for x in tc):
            out["time_class_unchanged"] = "ROBUST_YES" if len(set(tc)) == 1 else "FRAGILE"
    return out


def nonheat_file(path: str) -> dict:
    c: Counter = Counter()
    vals: dict = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            fam = r["nh_family"]
            c[("events", fam)] += 1
            c[("status", fam, r["status"])] += 1
            if r["status"] == "SCENARIO_UNKNOWN":
                miss = sorted(r.get("missing") or [])
                c[("missing_set", fam, "__".join(miss) or "NONE")] += 1
                for m in miss:
                    c[("missing_each", fam, m)] += 1
                continue
            sc = r["scenarios"]
            if r["status"] != "SCENARIO_COMPUTED" or not all(b in sc for b in BR):
                continue
            c[("computed", fam)] += 1
            bases = sc["TYPICAL"].get("bases") or {}
            for f, v in sc["TYPICAL"].items():
                if f in ("bases", "flags") or not _num(v):
                    continue
                lo, hi = sc["GENTLE"].get(f), sc["INTENSE"].get(f)
                if _num(lo) and _num(hi):
                    kind = "INPUT" if f in bases else "OUTPUT"
                    vals.setdefault((fam, f"{kind}_{f}"), []).append(abs(hi - lo))
            for k, v in _nh_conclusions(fam, sc).items():
                c[("conclusion", fam, k, v)] += 1
    return {"c": dict(c), "vals": vals}


# ------------------------------------------------------------------------------------------------ aggregation
def _qs(xs: list) -> dict:
    a = np.asarray(xs, dtype=float)
    out = {"n": int(a.size), "share_zero": round(float((a == 0).mean()), 4)}
    for name, q in QUANT:
        out[name] = float(f"{float(np.quantile(a, q)):.6g}")  # significant digits: widths of D_eff are ~1e-10
    return out


def _merge(parts: list[dict]) -> tuple[Counter, dict]:
    tot: Counter = Counter()
    vals: dict = {}
    for p in parts:
        tot.update(p["c"])
        for k, v in p["vals"].items():
            vals.setdefault(k, []).extend(v)
    return tot, vals


def _nest(items) -> dict:
    out: dict = {}
    for key, v in items:
        d = out
        for k in key[:-1]:
            d = d.setdefault(str(k), {})
        d[str(key[-1])] = v
    return out


def conclusion_table(tot: Counter, fam: str) -> dict:
    out: dict = {}
    names = sorted({k[2] for k in tot if k[0] == "conclusion" and k[1] == fam})
    for name in names:
        cnt = {k[3]: v for k, v in tot.items() if k[0] == "conclusion" and k[1] == fam and k[2] == name}
        none = cnt.pop("None", 0) + cnt.pop(None, 0)
        n = sum(cnt.values())
        frag = cnt.get("FRAGILE", 0)
        share = frag / n if n else None
        out[name] = {"events_evaluated": n, "events_not_evaluable": none, "robust_yes": cnt.get("ROBUST_YES", 0),
                     "robust_no": cnt.get("ROBUST_NO", 0), "fragile": frag,
                     "fragile_share": None if share is None else round(share, 4),
                     "flag": None if share is None else ("ROBUST" if share <= FRAGILE_SHARE_THRESHOLD else "FRAGILE")}
    return out


def heat_report(parts: list[dict]) -> dict:
    tot, vals = _merge(parts)
    fams = sorted({k[1] for k in tot if k[0] == "events"})
    rep: dict = {}
    for fam in fams:
        w = {name: _qs(v) for (f, name), v in sorted((k, v) for k, v in vals.items() if len(k) == 2 and k[0] == fam and v)}
        basis = {}
        for key in sorted({k[2] for k in tot if k[0] == "by_basis_computed" and k[1] == fam}):
            n = tot[("by_basis_computed", fam, key)]
            conc = {k[4]: v for k, v in tot.items() if k[0] == "by_basis_conclusion" and k[1] == fam and k[2] == key
                    and k[3] == "core_reaches_70c"}
            ev = sum(v for kk, v in conc.items() if kk not in ("None", None))
            wid = vals.get((key, "core_end_c_width", fam))
            basis[key] = {"computed": n, "core_computed": ev,
                          "core_reaches_70c_fragile_share": round(conc.get("FRAGILE", 0) / ev, 4) if ev else None,
                          "core_end_c_width": _qs(wid) if wid else None}
        rep[fam] = {
            "events": tot[("events", fam)], "status": _nest((k[2:], v) for k, v in tot.items() if k[0] == "status" and k[1] == fam),
            "computed": tot[("computed", fam)], "core_computed": tot[("core_computed", fam)],
            "scenario_unknown_missing_sets": _nest((k[2:], v) for k, v in sorted(tot.items()) if k[0] == "missing_set" and k[1] == fam),
            "scenario_unknown_missing_each_input": _nest((k[2:], v) for k, v in sorted(tot.items()) if k[0] == "missing_each" and k[1] == fam),
            "unsupported_medium": _nest((k[2:], v) for k, v in sorted(tot.items()) if k[0] == "unsupported_medium" and k[1] == fam),
            "core_unknown_reason_flag_counts": _nest((k[2:], v) for k, v in sorted(tot.items()) if k[0] == "core_unknown_reason" and k[1] == fam),
            "bracket_width": w, "conclusions": conclusion_table(tot, fam), "by_input_basis": basis}
    return rep


def nonheat_report(parts: list[dict]) -> dict:
    tot, vals = _merge(parts)
    rep: dict = {}
    for fam in sorted({k[1] for k in tot if k[0] == "events"}):
        rep[fam] = {
            "events": tot[("events", fam)], "status": _nest((k[2:], v) for k, v in tot.items() if k[0] == "status" and k[1] == fam),
            "computed": tot[("computed", fam)],
            "scenario_unknown_missing_sets": _nest((k[2:], v) for k, v in sorted(tot.items()) if k[0] == "missing_set" and k[1] == fam),
            "scenario_unknown_missing_each_input": _nest((k[2:], v) for k, v in sorted(tot.items()) if k[0] == "missing_each" and k[1] == fam),
            "bracket_width": {name: _qs(v) for (f, name), v in sorted((k, v) for k, v in vals.items() if k[0] == fam and v)},
            "conclusions": conclusion_table(tot, fam)}
    return rep


def _files(dirs: list[Path]) -> list[str]:
    return [str(f) for d in dirs for f in sorted(d.glob("*.jsonl"))]


def _run(fn, files: list[str], workers: int) -> list[dict]:
    if workers > 1 and len(files) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            return pool.map(fn, files, chunksize=1)
    return [fn(f) for f in files]


def markdown(rep: dict) -> str:
    L = ["# Sensitivity of the GENTLE-INTENSE bracket (S178 PHYS2, T4-C05-R1; FIX-PHYS v05)", "", "## Caveat", "", CAVEAT, "",
         "Caveat codes in the JSON: " + ", ".join(f"`{c}`" for c in rep["caveat"]) + ".", "",
         "Basis kinds (m8) are TEXT_STATED, CARRIED_SETPOINT, PHYSICAL_DEFINITION (the boil by definition) and DEFAULT (a scenario row); "
         "'reaches 70 C' is the end value >= 70 C for the core and for the volume average alike.", "",
         "Status: DRAFT / AI_DRAFTED, counts and quantiles only, no recipe text or ids. The brackets are scenario defaults "
         "(ASSUMED_DEFAULT, MODEL_DERIVED, NON_CITABLE). A conclusion is ROBUST for a family when at most "
         f"{FRAGILE_SHARE_THRESHOLD:.0%} of its events change the conclusion between GENTLE, TYPICAL and INTENSE (PROPOSED threshold); "
         "ROBUST says the conclusion does not depend on where in the scenario ranges the event sits, not that it is true of food.", "",
         f"Input layer versions: heat L2 `{rep['heat_layer_version']}`, non-heat L2 `{rep['nonheat_layer_version']}`.", ""]
    for part, title in (("heat", "Heat families"), ("nonheat", "Non-heat families")):
        fams = rep.get(part) or {}
        if not fams:
            continue
        L += [f"## {title}", "", "| family | events | computed | SCENARIO_UNKNOWN | conclusion | evaluated | robust yes | robust no | fragile | fragile share | flag |",
              "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|"]
        for fam, d in fams.items():
            unk = d["status"].get("SCENARIO_UNKNOWN", 0)
            conc = d["conclusions"] or {"-": None}
            for name, c in conc.items():
                if c is None:
                    L.append(f"| {fam} | {d['events']} | {d['computed']} | {unk} | - | - | - | - | - | - | - |")
                else:
                    L.append(f"| {fam} | {d['events']} | {d['computed']} | {unk} | {name} | {c['events_evaluated']} | {c['robust_yes']} | "
                             f"{c['robust_no']} | {c['fragile']} | {c['fragile_share']} | {c['flag']} |")
        L += ["", f"### {title}: width INTENSE - GENTLE (median [p10, p90], share of events with zero width)", "",
              "| family | quantity | n | p10 | p50 | p90 | max | share zero |", "|---|---|---:|---:|---:|---:|---:|---:|"]
        for fam, d in fams.items():
            for name, q in d["bracket_width"].items():
                L.append(f"| {fam} | {name} | {q['n']} | {q['p10']} | {q['p50']} | {q['p90']} | {q['max']} | {q['share_zero']} |")
        L.append("")
    L += ["## Reasons for SCENARIO_UNKNOWN (counts by missing-input set)", ""]
    for part in ("heat", "nonheat"):
        for fam, d in (rep.get(part) or {}).items():
            ms = d["scenario_unknown_missing_sets"]
            if ms:
                L.append(f"- {part} {fam}: " + "; ".join(f"{k} = {v}" for k, v in sorted(ms.items(), key=lambda kv: -kv[1])[:6]))
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--heat-l2", nargs="*", default=[], type=Path)
    ap.add_argument("--nonheat-l2", nargs="*", default=[], type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    for p in (a.out, a.out_md):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    if not a.heat_l2 and not a.nonheat_l2:
        ap.error("give --heat-l2 and/or --nonheat-l2")
    for d in (*a.heat_l2, *a.nonheat_l2):
        try:
            parts = d.resolve().relative_to(ROOT.resolve()).parts
        except ValueError:
            parts = ("data",)
        if parts[:1] != ("data",) or not d.is_dir():
            ap.error("inputs must be existing directories under data/ or outside the repository")
    hf, nf = _files(a.heat_l2), _files(a.nonheat_l2)
    heat = heat_report(_run(heat_file, hf, a.workers)) if hf else {}
    nonheat = nonheat_report(_run(nonheat_file, nf, a.workers)) if nf else {}

    def version(files):
        if not files:
            return "NONE"
        with open(files[0], encoding="utf-8") as fh:
            return json.loads(fh.readline())["version"]
    rep = {"record": "PHYSICAL_LAYER_SENSITIVITY", "status": "AI_DRAFTED_COUNTS_ONLY", "version": VERSION, "contains_ids": False,
           "contains_text": False, "citable": False, "counts_as_human_gate": False, "fragile_share_threshold_proposed": FRAGILE_SHARE_THRESHOLD,
           "thresholds_are_reporting_thresholds_not_safety_or_doneness": {"core_c": CORE_C, "chilled_c": CHILL_C, "hot_holding_c": HOT_C},
           "caveat": list(CAVEAT_CODES), "basis_kinds": list(BASIS_KINDS), "boundary_model_axis": "OPEN_NOT_COMPUTED",
           "heat_layer_version": version(hf), "nonheat_layer_version": version(nf), "heat_files": len(hf), "nonheat_files": len(nf),
           "family_source": "registry/proc_family_registry_v1.csv", "heat": heat, "nonheat": nonheat,
           "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    D.write_report(a.out, rep, root=ROOT)
    a.out_md.write_text(markdown(rep), encoding="utf-8")
    print(json.dumps({"heat_files": len(hf), "nonheat_files": len(nf), "heat_families": list(heat), "nonheat_families": list(nonheat),
                      "report_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
