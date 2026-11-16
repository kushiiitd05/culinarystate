#!/usr/bin/env python
"""Run Layer 2 SCENARIO over Layer 1 records (S172, D-077). Data-plane in, data-plane out, counts-only summary.

    python tools/scenario_layer_run.py --l1 data/derived/physical_L1/ --l2 data/derived/physical_L2/ \
        --out reports/step26/<new>.json [--workers 64]

S176 L-PHYS: the evaporation cap (phase_change) is ON by default (layer 0.2.0). ``--compare-uncapped`` also runs the
SUPERSEDED 0.1.0 model on the same records and adds a counts-only before/after block (share of events whose core exceeds
100 C, dose quantiles, coverage); the per-event records written are always those of the main (capped) model.
``--no-evaporation-cap`` reproduces 0.1.0 (for regression only); ``--altitude-m`` and ``--pressure-psig`` are the optional
cap parameters (default sea level at 1 atm, bracket pressure; both flagged in every record).

S177 SCIFIX-PHYS (layer 0.3.0): zone-resolved doses (8 Gauss-Legendre node histories per bracket, ``zone_mean_cook_value_min``),
``quality_cook_value_min`` renamed ``cook_value_at_volume_avg_t_min`` (old records are still read), the cap never below a
text-stated aqueous liquid temperature. ``--compare-prev-l2 DIR`` reads the previous (0.2.0) per-event L2 records of the same
L1 files and adds a counts-only ``v02_to_v03`` block (status changes, flags added / removed, cap and dose changes, quantiles
of the zone-mean dose over the dose of the volume-average temperature).

S178 PHYS2 (layer 0.4.0): ``--prev-tag`` / ``--tag`` name the comparison block (default ``v02`` / ``v03``, the S177 behaviour; the
S178 re-run passes ``v03`` / ``v04``) and ``--prev-layer-version`` its previous version string. The comparison also counts the
events whose bath temperature or its basis changed (the Layer 1 temperature-ownership fix).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")  # many fork workers: no BLAS oversubscription

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.extraction.rung_a_measure import code  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.simulation import phase_change as PC  # noqa: E402
from culinarystate.simulation import scenario_layer as SL  # noqa: E402

_LAYER: list = []  # [main layer, SUPERSEDED uncapped layer or None]
BR = ("GENTLE", "TYPICAL", "INTENSE")
QUANTILES = (0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0)
DOSE_FIELDS = ("core_cook_value_min", "cook_value_at_volume_avg_t_min", "zone_mean_cook_value_min", "surface_cook_value_min")
STATED_T_BUCKETS = ((100.0, 105.0, "100_TO_105"), (105.0, 120.0, "105_TO_120"), (120.0, 150.0, "120_TO_150"),
                    (150.0, 1e9, "ABOVE_150"))
_PREV: list = [None]  # directory of the previous (0.2.0) per-event L2 records, or None
_TAG: list = ["v02_to_v03"]  # name of the previous -> current comparison block
CODE_FILES = ("src/culinarystate/simulation/scenario_layer.py", "src/culinarystate/simulation/phase_change.py",
              "src/culinarystate/simulation/physics_drivers.py", "src/culinarystate/simulation/condition_binding.py",
              "src/culinarystate/simulation/endpoint_cues.py", "registry/scenario_defaults_v1.csv",
              "registry/phase_change_v1.csv", "registry/matrix_moisture_regime_v1.csv", "tools/scenario_layer_run.py")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def provenance() -> dict:
    return {"code_sha256": [{"path": f, "sha256": hashlib.sha256((ROOT / f).read_bytes()).hexdigest()} for f in CODE_FILES]}


def dir_manifest_sha256(d: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(d.glob("*.jsonl")):
        h.update(f"{f.name}\0{hashlib.sha256(f.read_bytes()).hexdigest()}\n".encode())
    return h.hexdigest()


def _dose(s: dict, f: str):
    """A dose field of one bracket record; the 0.2.0 name of the volume-average dose is still read from old records."""
    return SL.volume_avg_dose(s) if f == "cook_value_at_volume_avg_t_min" else s.get(f)


def _count_main(c: Counter, out: dict) -> None:
    c[("status", code(out["status"]))] += 1
    c[("transition", code(out["transition_status"]))] += 1
    for b, s in out["scenarios"].items():
        c[("core_known", b, s["core_end_c"] is not None)] += 1
        for k, v in s["bases"].items():
            c[("basis", k, code(str(v).split(":")[0] if str(v).startswith("L1:") else
                                ("SD" if str(v).startswith("SD-") else
                                 "KGE" if str(v).startswith("KGE-") else
                                 "PC" if str(v).startswith("PC-") else str(v))))] += 1
        if b == "TYPICAL" and s["core_end_c"] is not None:
            c[("typical_core_reaches_70", s["core_minutes_above_70"] > 0)] += 1
        if "STATED_LIQUID_T_ABOVE_TBOIL" in s.get("flags", ()):
            c[("stated_liquid_above_tboil", b)] += 1
            c[("stated_liquid_above_tboil_by_stated_c", b, next(n for lo, hi, n in STATED_T_BUCKETS if lo < s["bath_c"] <= hi))] += 1
            if b == "TYPICAL":  # S178: split the stated-liquid population by solute-rich member and by core computed
                bucket = next(n for lo, hi, n in STATED_T_BUCKETS if lo < s["bath_c"] <= hi)
                solute = any(f in s["flags"] for f in ("TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER", "SUGAR_PHASE_TBOIL_LOWER_ESTIMATE"))
                c[("stated_liquid_typical_by_stated_c_and_member", bucket, "SOLUTE_RICH_MEMBER" if solute else "NO_SOLUTE_RICH_MEMBER")] += 1
                if s["core_end_c"] is not None:
                    c[("stated_liquid_typical_core_computed_by_stated_c", bucket)] += 1
        if b == "TYPICAL":  # S178 FIX-PHYS: the Q1 lift gate (M4), the moist-piece boundary (M5), water bath (m3)
            for f in s.get("flags", ()):
                if f.startswith(("STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED", "STATED_LIQUID_LIFT_")) or f in (
                        "STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE", "WATER_BATH_IN_OVEN", "FAN_VS_CONVENTIONAL_UNRESOLVED",
                        "HEAT_LEVEL_OR_APPLIANCE_SETTING_AT_OR_BELOW_TBOIL"):
                    c[("fixphys_flag_typical", code(f))] += 1
        if "OVEN_OR_AMBIENT_TEMPERATURE_STATED_NOT_USED_AS_LIQUID_T" in s.get("flags", ()) and b == "TYPICAL":
            c[("ambient_temperature_not_used_as_liquid_t_typical",)] += 1
        if s.get("zone_nodes"):
            c[("zone_nodes_emitted", b)] += 1
    t = out["scenarios"].get("TYPICAL")
    if t is not None and "surface_state" in t:
        for b, s in out["scenarios"].items():
            c[("surface_state", b, code(s["surface_state"]))] += 1
        for f in t["flags"]:
            if f.startswith(("MATRIX_", "EVAPORATION_", "PRESSURE_", "ALTITUDE_", "DRY_MATRIX", "STATED_LIQUID", "BOILING_POINT",
                             "TBOIL_", "ALL_MEMBERS", "NOT_A_ZONE", "CAP_", "SUGAR_PHASE", "SALT_MEMBER", "WATER_BATH")):
                c[("cap_flag_typical", code(f))] += 1


def _compare(c: Counter, vals: dict, tag: str, out: dict, pressure: bool, capped: bool, dry: bool) -> None:
    """Counts and dose values of one variant ('before' = SUPERSEDED 0.1.0, 'after' = capped 0.2.0).

    ``dry`` is the matrix regime of the event as classified by the capped model (DRY_LOW_MOISTURE: never capped), so both
    variants are split the same way: tags ``<tag>_moist`` (capped class, unknown or ambiguous) and ``<tag>_dry`` carry the dose
    values; the all-events tag carries everything."""
    c[("cmp", tag, "heat_events")] += 1
    c[("cmp", tag, "status", code(out["status"]))] += 1
    sc = out["scenarios"]
    over_any = over_np_any = over_moist_np = viol_any = False
    sub = f"{tag}_dry" if dry else f"{tag}_moist"
    for b in BR:
        s = sc.get(b)
        if not s or s["core_end_c"] is None:
            continue
        c[("cmp", tag, "core_computed", b)] += 1
        core, avg = s["core_end_c"], s.get("volume_avg_end_c")
        if core > 100.0:
            c[("cmp", tag, "core_gt_100", b)] += 1
            over_any = True
            if not pressure:
                c[("cmp", tag, "core_gt_100_nonpressure", b)] += 1
                over_np_any = True
                c[("cmp", tag, "core_gt_100_nonpressure_dry_class" if dry else "core_gt_100_nonpressure_moist_class", b)] += 1
                over_moist_np = over_moist_np or not dry
        if capped and s["t_cap_c"] is not None:
            tol = _TOL
            if core > s["t_cap_c"] + tol or (avg is not None and avg > s["t_cap_c"] + tol):
                c[("cmp", tag, "violations_above_cap_plus_tol", b)] += 1
                viol_any = True
        for f in DOSE_FIELDS:
            v = _dose(s, f)
            if v is not None:
                vals.setdefault((tag, f, b), []).append(v)
                vals.setdefault((sub, f, b), []).append(v)
    if over_any:
        c[("cmp", tag, "events_core_gt_100_any_bracket")] += 1
    if over_np_any:
        c[("cmp", tag, "events_core_gt_100_nonpressure_any_bracket")] += 1
    if over_moist_np:
        c[("cmp", tag, "events_core_gt_100_nonpressure_moist_class_any_bracket")] += 1
    if viol_any:
        c[("cmp", tag, "events_violating_cap_any_bracket")] += 1
    if sc.get("TYPICAL") and sc["TYPICAL"]["core_end_c"] is not None:
        c[("cmp", tag, "typical_core_computed")] += 1
        c[("cmp", tag, "typical_core_computed_dry_class" if dry else "typical_core_computed_moist_class")] += 1


_TOL = 0.5
CHANGE_EPS = 5e-4  # outputs are rounded to 0.001 (temperatures) and 0.0001 (doses)


def _cmp_prev(c: Counter, vals: dict, old: dict, new: dict) -> None:
    """Counts-only 0.2.0 -> 0.3.0 comparison of one event (same L1 record, same order in the files)."""
    c[("cmp_prev", "events")] += 1
    if old.get("event_id") != new.get("event_id") or old.get("recipe_id") != new.get("recipe_id"):
        c[("cmp_prev", "ALIGNMENT_ERROR")] += 1
        return
    c[("cmp_prev", "status", code(old["status"]), code(new["status"]))] += 1
    for b in BR:
        so, sn = old["scenarios"].get(b), new["scenarios"].get(b)
        if not so or not sn:
            continue
        fo, fn = set(so.get("flags", ())), set(sn.get("flags", ()))
        for f in sorted(fn - fo):
            c[("cmp_prev", "flag_added", b, code(f))] += 1
        for f in sorted(fo - fn):
            c[("cmp_prev", "flag_removed", b, code(f))] += 1
        if so.get("t_cap_c") != sn.get("t_cap_c"):
            c[("cmp_prev", "t_cap_changed", b)] += 1
            if sn.get("t_cap_c") is not None and so.get("t_cap_c") is not None and sn["t_cap_c"] > so["t_cap_c"]:
                c[("cmp_prev", "t_cap_raised", b)] += 1
        if so.get("bath_c") != sn.get("bath_c"):
            c[("cmp_prev", "bath_c_changed", b)] += 1
        if (so.get("bases") or {}).get("bath_c") != (sn.get("bases") or {}).get("bath_c"):
            c[("cmp_prev", "bath_basis_changed", b, code(f"{(so.get('bases') or {}).get('bath_c')}>{(sn.get('bases') or {}).get('bath_c')}"))] += 1
        for f in ("core_end_c", "volume_avg_end_c", "core_cook_value_min", "surface_cook_value_min"):
            if so.get(f) is not None and sn.get(f) is not None and abs(so[f] - sn[f]) > CHANGE_EPS * max(1.0, abs(so[f])):
                c[("cmp_prev", "changed", b, f)] += 1
        vo, vn = SL.volume_avg_dose(so), SL.volume_avg_dose(sn)
        if vo is not None and vn is not None:
            c[("cmp_prev", "volume_avg_dose_equal_to_0_2_0_name", b, abs(vo - vn) <= CHANGE_EPS * max(1.0, abs(vo)))] += 1
        z, core = sn.get("zone_mean_cook_value_min"), sn.get("core_cook_value_min")
        if z is not None and vn:
            vals.setdefault((_TAG[0], "zone_mean_over_dose_at_volume_avg_t", b), []).append(z / vn)
            c[("cmp_prev", "zone_mean_dose_gt_dose_at_volume_avg_t", b, z >= vn)] += 1
        if z is not None and core:
            vals.setdefault((_TAG[0], "zone_mean_over_core_dose", b), []).append(z / core)


def _one(paths: tuple[str, str]) -> dict:
    src, dst = paths
    layer, old = _LAYER
    c: Counter = Counter()
    vals: dict = {}
    prev = None
    if _PREV[0] is not None:
        pf = Path(_PREV[0]) / Path(src).name
        prev = open(pf, encoding="utf-8") if pf.exists() else None
        if prev is None:
            c[("cmp_prev", "PREV_FILE_MISSING")] += 1
    with open(src, encoding="utf-8") as fi, open(dst, "x", encoding="utf-8") as fo:
        for line in fi:
            rec = json.loads(line)
            out = layer.run(rec)
            fo.write(json.dumps(out, separators=(",", ":")) + "\n")
            _count_main(c, out)
            if prev is not None:
                pline = prev.readline()
                if pline:
                    _cmp_prev(c, vals, json.loads(pline), out)
                else:
                    c[("cmp_prev", "PREV_FILE_SHORTER")] += 1
            if old is not None:
                pressure = out.get("medium") in PC.PRESSURE_MEDIA
                typ = out["scenarios"].get("TYPICAL")
                dry = bool(typ) and typ.get("t_cap_c", 1) is None
                _compare(c, vals, "after", out, pressure, layer.capped, dry)
                _compare(c, vals, "before", old.run(rec), pressure, False, dry)
            if out["status"] == "SCENARIO_COMPUTED":
                for b, sb in out["scenarios"].items():
                    z, v = sb.get("zone_mean_cook_value_min"), sb.get("cook_value_at_volume_avg_t_min")
                    if z is not None and v:
                        vals.setdefault(("main", "zone_mean_over_dose_at_volume_avg_t", b), []).append(z / v)
    if prev is not None:
        extra = prev.readline()
        prev.close()
        if extra:
            c[("cmp_prev", "PREV_FILE_LONGER")] += 1
    return {"c": dict(c), "vals": vals}


def _nest(items, extra: tuple = ()) -> dict:
    nest: dict = {}
    for key, v in sorted(items, key=lambda kv: str(kv[0])):
        d = nest
        for k in key[:-1]:
            d = d.setdefault(code(k), {})
        d[code(key[-1])] = v
    return nest


def _quantiles(vals: dict) -> dict:
    out: dict = {}
    for (tag, field, b), xs in sorted(vals.items()):
        a = np.asarray(xs, dtype=float)
        q = np.quantile(a, QUANTILES)
        out.setdefault(tag, {}).setdefault(field, {})[b] = {
            "n": int(a.size), **{("max" if p == 1.0 else f"p{int(round(p * 100)):02d}"): round(float(x), 4)
                                 for p, x in zip(QUANTILES, q)}}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--l1", required=True, type=Path)
    ap.add_argument("--l2", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--compare-uncapped", action="store_true",
                    help="also run the SUPERSEDED 0.1.0 model and report a before/after block")
    ap.add_argument("--no-evaporation-cap", action="store_true",
                    help="run the SUPERSEDED 0.1.0 model as the main model (regression only)")
    ap.add_argument("--compare-prev-l2", type=Path, default=None,
                    help="directory of the previous (0.2.0) per-event L2 records of the same L1 files: adds a v02_to_v03 block")
    ap.add_argument("--prev-tag", default="v02", help="label of the previous layer in the comparison block (default v02)")
    ap.add_argument("--tag", default="v03", help="label of this layer in the comparison block (default v03)")
    ap.add_argument("--prev-layer-version", default=SL.VERSION_V02, help="previous layer version string")
    ap.add_argument("--altitude-m", type=float, default=None, help="optional altitude (default sea level, flagged)")
    ap.add_argument("--pressure-psig", type=float, default=None, help="optional stated gauge pressure of a pressure process")
    a = ap.parse_args(argv)
    if a.out.exists():
        ap.error("refusing to overwrite an existing report")
    if a.no_evaporation_cap and a.compare_uncapped:
        ap.error("--compare-uncapped needs the capped model as the main model")
    for p in (a.l1, a.l2):
        try:
            parts = p.resolve().relative_to(ROOT.resolve()).parts
        except ValueError:
            parts = ("data",)
        if parts[:1] != ("data",):
            ap.error("--l1/--l2 must be under data/ (git-ignored) or outside the repository")
    if a.compare_prev_l2 is not None and not a.compare_prev_l2.is_dir():
        ap.error("--compare-prev-l2 must be an existing directory")
    _PREV[0] = str(a.compare_prev_l2) if a.compare_prev_l2 else None
    _TAG[0] = f"{a.prev_tag}_to_{a.tag}"
    a.l2.mkdir(parents=True, exist_ok=True)
    if any(a.l2.iterdir()):
        ap.error("--l2 must be empty or new")
    policy = PC.CapPolicy(enabled=not a.no_evaporation_cap, altitude_m=a.altitude_m, pressure_psig=a.pressure_psig)
    prov = provenance()
    started, t0 = _now(), time.time()
    main_layer = SL.ScenarioLayer.load(policy=policy)
    global _TOL
    _TOL = main_layer.pc.invariant_tol_c if main_layer.pc else 0.5
    _LAYER.clear()
    _LAYER.extend([main_layer, SL.ScenarioLayer.load(policy=PC.CapPolicy(enabled=False)) if a.compare_uncapped else None])
    jobs = [(str(f), str(a.l2 / f.name)) for f in sorted(a.l1.glob("*.jsonl"))]
    if a.workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.workers) as pool:
            parts = pool.map(_one, jobs, chunksize=1)
    else:
        parts = [_one(j) for j in jobs]
    tot: Counter = Counter()
    vals: dict = {}
    for p in parts:
        tot.update(p["c"])
        for k, v in p["vals"].items():
            vals.setdefault(k, []).extend(v)
    plain = [(k, v) for k, v in tot.items() if k[0] not in ("cmp", "cmp_prev")]
    cmp_items = [(k[1:], v) for k, v in tot.items() if k[0] == "cmp"]
    prev_items = [(k[1:], v) for k, v in tot.items() if k[0] == "cmp_prev"]
    ratio_vals = {k: v for k, v in vals.items() if k[0] in ("main", _TAG[0])}
    vals = {k: v for k, v in vals.items() if k[0] not in ("main", _TAG[0])}
    reg = (ROOT / "registry/scenario_defaults_v1.csv").read_bytes()
    rep = {"record": "SCENARIO_L2_SUMMARY", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY", "layer_version": SL.VERSION
           if main_layer.capped else SL.VERSION_UNCAPPED, "labels": SL.LABELS, "contains_ids": False,
           "contains_text": False, "citable": False, "counts_as_human_gate": False,
           "scenario_registry_sha256": hashlib.sha256(reg).hexdigest(), "l1_files": len(jobs), "counts": _nest(plain),
           "zone_field": {"n_nodes": main_layer.n_nodes, "scheme": "GAUSS_LEGENDRE_HALF_SLAB", "t_ref_c": SL.T_REF_C,
                          "z_c": SL.Z_C, "zone_mean_over_dose_at_volume_avg_t_quantiles":
                          _quantiles({k: v for k, v in ratio_vals.items() if k[0] == "main"}).get("main", {})}}
    if main_layer.capped:
        rep.update(cap_model=PC.VERSION, cap_policy={"enabled": True, "altitude_m": a.altitude_m, "pressure_psig": a.pressure_psig},
                   phase_change_registry_sha256=hashlib.sha256((ROOT / PC.REGISTRY).read_bytes()).hexdigest(),
                   matrix_regime_registry_sha256=hashlib.sha256((ROOT / PC.REGIME_REGISTRY).read_bytes()).hexdigest(),
                   dry_low_moisture_classes=list(main_layer.pc.dry_classes),
                   supersedes="SCENARIO_L2_0_1_0_CORE_AND_DOSE_FIELDS_OF_DRY_AND_FAT_EVENTS")
    else:
        rep.update(superseded_model=True)
    if a.compare_uncapped:
        rep["before_after"] = {"before_layer_version": SL.VERSION_UNCAPPED, "after_layer_version": SL.VERSION,
                               "counts": _nest(cmp_items), "dose_quantiles": _quantiles(vals)}
    if a.compare_prev_l2 is not None:
        rep[_TAG[0]] = {"previous_layer_version": a.prev_layer_version, "layer_version": SL.VERSION, "counts": _nest(prev_items),
                        "ratio_quantiles": _quantiles({k: v for k, v in ratio_vals.items() if k[0] == _TAG[0]}).get(_TAG[0], {})}
    rep.update(code_provenance=prov, code_unchanged_during_run=provenance() == prov, started_at_utc=started,
               ended_at_utc=_now(), wall_seconds=round(time.time() - t0, 1), workers=a.workers,
               records_manifest_sha256=dir_manifest_sha256(a.l2))
    D.write_report(a.out, rep, root=ROOT)
    print(json.dumps({"files": len(jobs), "status": rep["counts"].get("status"), "wall_seconds": rep["wall_seconds"],
                      "report_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
