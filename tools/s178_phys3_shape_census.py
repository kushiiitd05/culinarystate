#!/usr/bin/env python
"""Shape-class diagnostic for the physical layers (S178 PHYS3, T4-C08-R1). DRAFT, AI_DRAFTED, counts only.

Shapes are NOT wired into Layer 2 in this round. This tool reads the Layer 1 records (cut class = piece_size_class, ingredient class
= the single food group of the consumed lot) and the Layer 2 records of the same events, maps each heat event to a shape with
``registry/shape_map_v1.csv`` (``shape_series.shape_for``), and counts:

- heat events by mapped shape and by (cut class, shape); events whose shape class would change (shape not SLAB and not
  SLAB_BOUND_UNRESOLVED);
- Layer 2 events with a computed core (a size class and a film coefficient exist), and among them the ones whose shape would change;
- for those, the change of the end-of-step centre temperature per bracket if the mapped shape replaced the slab, in buckets
  (|dT| <= 0.1, 0.1-1, 1-5, 5-20, > 20 degC), recomputed from the record's own scenario inputs (h, half-thickness, initial and boundary
  temperature, duration; k and alpha = the SD-040 / SD-041 mid values Layer 2 uses), plus a consistency count (the recomputed slab
  centre equals the record's core_end_c to 0.01 degC) and a bound count (the shape centre is never farther from the bath than the slab).

No ids, values or text leave the run: the JSON holds integers and codes only.

    nice -n 10 python tools/s178_phys3_shape_census.py --l1 data/derived/physical_L1_1000_S178v04 \
        --l2 data/derived/physical_L2_1000_S178v04 --out reports/s178/phys3/shape_census_1000_S178v04.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.simulation import shape_series as S  # noqa: E402

TOOL_VERSION = "s178-phys3-shape-census-0.1.0-draft"
BRACKETS = ("GENTLE", "TYPICAL", "INTENSE")  # = scenario_layer.BRACKETS; aspect index 2 - i (GENTLE = least exposure)
BUCKETS = ((0.1, "DT_LE_0_1"), (1.0, "DT_0_1_TO_1"), (5.0, "DT_1_TO_5"), (20.0, "DT_5_TO_20"))
CODE_FILES = ("src/culinarystate/simulation/shape_series.py", "registry/shape_map_v1.csv", "registry/scenario_defaults_v1.csv",
              "tools/s178_phys3_shape_census.py")
_CTX: dict = {}


def _bucket(dt: float) -> str:
    return next((name for lim, name in BUCKETS if dt <= lim), "DT_GT_20")


def _files(dirs) -> list[str]:
    out = []
    for d in dirs:
        p = Path(d)
        out += [str(f) for f in sorted(p.rglob("*.jsonl"))] if p.is_dir() else [str(p)]
    return out


def mids(path: Path) -> tuple[float, float]:
    """(k, alpha) mid values of SD-040 / SD-041 (FOOD_HIGH_MOISTURE), the values Layer 2 uses for every bracket."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = {r["default_id"]: r for r in csv.DictReader(fh)}
    return float(rows["SD-040"]["mid"]), float(rows["SD-041"]["mid"])


def _l1_part(path: str) -> tuple[dict, Counter]:
    rows = _CTX["rows"]
    idx = {r.map_id: i for i, r in enumerate(rows)}
    keys, c = {}, Counter()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            inp = rec.get("inputs") or {}
            cut = (inp.get("piece_size_class") or {}).get("value")
            mx = inp.get("matrix_class") or {}
            cls = mx.get("value") if mx.get("status", "UNKNOWN") != "UNKNOWN" else None
            row = S.shape_for(rows, cut, cls)
            keys[f"{rec['recipe_id']}#{rec['event_id']}"] = idx[row.map_id]
            c[("events",)] += 1
            c[("by_row", D_code(row.map_id))] += 1
            c[("by_shape", row.shape)] += 1
            c[("by_cut_and_shape", D_code(cut), row.shape)] += 1
            if row.shape not in S.UNCHANGED:
                c[("shape_changed",)] += 1
            if rec.get("version"):
                c[("l1_version", D_code(rec["version"]))] += 1
    return keys, c


def D_code(v) -> str:
    return "NONE" if v is None else str(v).replace("-", "_").replace(".", "_").upper()


def _l2_part(path: str) -> Counter:
    rows, keys, (k, alpha) = _CTX["rows"], _CTX["keys"], _CTX["k_alpha"]
    c = Counter()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            c[("records",)] += 1
            ri = keys.get(f"{rec.get('recipe_id')}#{rec.get('event_id')}")
            if ri is None:
                c[("not_joined_to_l1",)] += 1
                continue
            row = rows[ri]
            c[("status", D_code(rec.get("status")))] += 1
            sc = rec.get("scenarios") or {}
            typ = sc.get("TYPICAL") or {}
            if typ.get("core_end_c") is None:
                continue
            c[("core_computed",)] += 1
            c[("core_computed_by_shape", row.shape)] += 1
            if row.shape in S.UNCHANGED:
                continue
            c[("core_computed_shape_changed",)] += 1
            c[("core_computed_shape_changed_by_row", D_code(row.map_id))] += 1
            for i, name in enumerate(BRACKETS):
                s = sc.get(name) or {}
                need = ("h", "half_thickness_m", "initial_c", "duration_min", "core_end_c")
                if any(s.get(x) is None for x in need):
                    c[("l2_fields_missing", name)] += 1
                    continue
                bound = s.get("boundary_c", s.get("bath_c"))
                props = dict(time_s=60.0 * s["duration_min"], alpha_m2_s=alpha, h_w_m2k=s["h"], k_w_mk=k)
                slab = S.core_and_mean_temperature(S.Geometry("SLAB", (s["half_thickness_m"],)), t0_c=s["initial_c"], bath_c=bound,
                                                   **props)[0]
                c[("slab_recompute_matches_record" if abs(slab - s["core_end_c"]) <= 0.01 else "slab_recompute_differs", name)] += 1
                geom = S.geometry_for(row, s["half_thickness_m"], bracket=2 - i)
                shp = S.core_and_mean_temperature(geom, t0_c=s["initial_c"], bath_c=bound, **props)[0]
                c[("core_end_change_bucket", name, _bucket(abs(shp - slab)))] += 1
                # slab bound: the shape centre is never farther from the boundary than the slab centre
                if abs(shp - bound) > abs(slab - bound) + 1e-9:
                    c[("slab_bound_violated", name)] += 1
                else:
                    c[("slab_bound_holds", name)] += 1
    return c


def _nest(c: Counter, name: str) -> dict | int:
    out: dict = {}
    for key, v in sorted(c.items(), key=lambda kv: tuple(map(str, kv[0]))):
        if key[0] != name:
            continue
        if len(key) == 1:
            return v
        d = out
        for part in key[1:-1]:
            d = d.setdefault(str(part), {})
        d[str(key[-1])] = d.get(str(key[-1]), 0) + v
    return out


def run(l1_dirs, l2_dirs, *, workers: int = 1, root: Path = ROOT) -> dict:
    rows = S.load_shape_map(root / "registry/shape_map_v1.csv")
    _CTX.clear()
    _CTX.update(rows=rows, k_alpha=mids(root / "registry/scenario_defaults_v1.csv"))
    f1, f2 = _files(l1_dirs), _files(l2_dirs)

    def pmap(fn, items):
        if workers == 1:
            return [fn(x) for x in items]
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            return pool.map(fn, items, chunksize=1)

    c1, keys = Counter(), {}
    for kk, cc in pmap(_l1_part, f1):
        dup = len(keys.keys() & kk.keys())
        c1[("duplicate_event_keys",)] += dup
        keys.update(kk)
        c1.update(cc)
    _CTX["keys"] = keys
    c2 = Counter()
    for cc in pmap(_l2_part, f2):
        c2.update(cc)
    _CTX.clear()
    rep = {"record": "SHAPE_CLASS_DIAGNOSTIC", "tool_version": TOOL_VERSION, "shape_series_version": S.VERSION,
           "status": "AI_ENGINEERING_DIAGNOSTIC_COUNTS_ONLY", "wired_into_layer2": False, "basis": "ASSUMED_DEFAULT",
           "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
           "l1_files": len(f1), "l2_files": len(f2),
           "l1_heat_events": c1[("events",)], "l1_duplicate_event_keys": c1[("duplicate_event_keys",)],
           "l1_versions": _nest(c1, "l1_version"),
           "events_by_map_row": _nest(c1, "by_row"), "events_by_shape": _nest(c1, "by_shape"),
           "events_by_cut_class_and_shape": _nest(c1, "by_cut_and_shape"),
           "events_shape_class_would_change": c1[("shape_changed",)],
           "l2_records": c2[("records",)], "l2_not_joined_to_l1": c2[("not_joined_to_l1",)],
           "l2_status": _nest(c2, "status"), "l2_core_computed": c2[("core_computed",)],
           "l2_core_computed_by_shape": _nest(c2, "core_computed_by_shape"),
           "l2_core_computed_shape_would_change": c2[("core_computed_shape_changed",)],
           "l2_core_computed_shape_would_change_by_row": _nest(c2, "core_computed_shape_changed_by_row"),
           "core_end_change_if_shape_replaced_slab_by_bracket": _nest(c2, "core_end_change_bucket"),
           "slab_recompute_matches_record_by_bracket": _nest(c2, "slab_recompute_matches_record"),
           "slab_recompute_differs_by_bracket": _nest(c2, "slab_recompute_differs"),
           "slab_bound_holds_by_bracket": _nest(c2, "slab_bound_holds"),
           "slab_bound_violated_by_bracket": _nest(c2, "slab_bound_violated"),
           "l2_fields_missing_by_bracket": _nest(c2, "l2_fields_missing")}
    D.assert_counts_only(rep)
    return rep


def provenance(root: Path = ROOT) -> dict:
    return {"code_sha256": [{"path": f, "sha256": hashlib.sha256((root / f).read_bytes()).hexdigest()} for f in CODE_FILES]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--l1", nargs="+", required=True, help="Layer 1 record directories (recursive *.jsonl)")
    ap.add_argument("--l2", nargs="+", required=True, help="Layer 2 record directories of the same events")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", required=True, help="new counts-only JSON (refuses overwrite and protected places)")
    a = ap.parse_args(argv)
    if not 1 <= a.workers <= 24:
        ap.error("--workers must be between 1 and 24 (shared server)")
    out = Path(a.out)
    if out.exists():
        ap.error("refusing to overwrite an existing report")
    prov = provenance()
    rep = run(a.l1, a.l2, workers=a.workers)
    rep.update(code_provenance=prov, code_unchanged_during_run=provenance() == prov)
    try:
        D.write_report(out, rep, root=ROOT)
    except D.DryRunError as exc:
        ap.error(str(exc))
    print(json.dumps({k: rep[k] for k in ("l1_heat_events", "events_shape_class_would_change", "l2_core_computed",
                                           "l2_core_computed_shape_would_change")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
