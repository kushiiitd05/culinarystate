#!/usr/bin/env python
"""Run the shape eigen-series verification pack and write the reproducible report (S178 PHYS3, T4-C08-R1). DRAFT, AI_DRAFTED.

    python tools/s178_phys3_shape_verification.py --out-json reports/s178/phys3/shape_verification_S178.json \
        --out-md reports/s178/phys3/shape_verification_S178.md

Compares the cylinder, sphere and product-shape series of ``shape_series`` with independent references (analytic limits,
finite-volume solves in 1-D and 2-D, root and coefficient identities, the slab bound, the Layer 2 slab driver). The report holds
errors and tolerances only; ``results_sha256`` hashes the check results rounded to 6 significant digits. Never overwrites. A numerical
verification of the series, not a validation against food.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.simulation import phys_verification_shapes as V  # noqa: E402
from culinarystate.simulation import shape_series as S  # noqa: E402

CODE = ("src/culinarystate/simulation/shape_series.py", "src/culinarystate/simulation/phys_verification_shapes.py",
        "src/culinarystate/simulation/physics_drivers.py", "tools/s178_phys3_shape_verification.py")
CMD = ("python tools/s178_phys3_shape_verification.py --out-json reports/s178/phys3/shape_verification_S178.json "
       "--out-md reports/s178/phys3/shape_verification_S178.md")


def _round(x, sig: int = 6):
    if isinstance(x, float):
        return float(f"{x:.{sig}g}")
    if isinstance(x, dict):
        return {k: _round(v, sig) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_round(v, sig) for v in x]
    return x


def markdown(rep: dict) -> str:
    by = {c["id"]: c for c in rep["checks"]}
    n_ok = sum(c["passed"] for c in rep["checks"])
    lines = ["# Shape eigen-series verification pack (S178 PHYS3, T4-C08-R1)", "",
             "Status: DRAFT / AI_DRAFTED. A numerical verification of `shape_series` (infinite cylinder, sphere, finite cylinder, "
             "cube / brick) against independent references; not a validation against food and not a human signature. Shapes are NOT "
             "wired into Layer 2 in this round: the slab stays the stated slow-side bound.", "",
             f"Reproduce: `{rep['command']}`; `results_sha256` = `{rep['results_sha256']}` (results rounded to 6 significant digits).",
             "", f"**Result: {n_ok} of {len(rep['checks'])} checks pass.**", "",
             "| id | check | cases | max abs error | max rel error | tolerance | pass |", "|---|---|---:|---:|---:|---|---|"]
    for c in rep["checks"]:
        lines.append(f"| {c['id']} | {c['what']} | {c['n_cases']} | {c['max_abs_error']:.3g} | {c['max_rel_error']:.3g} | "
                     f"{c['tolerance']:g} ({c['tolerance_on']}) | {'yes' if c['passed'] else 'NO'} |")
    sv06, sv07, sv11 = by["SV06"], by["SV07"], by["SV11"]
    lines += ["", "## Reading", "",
              f"- Finite-volume references: 1-D (200 cells, exact in time) max abs error in theta by shape "
              f"{json.dumps(sv06['max_abs_error_by_shape'])}; 2-D Crank-Nicolson (60 cells per radius) of the finite cylinder and "
              f"the square bar {json.dumps(sv07['max_abs_error_by_case'])}. The 2-D check is the product rule (Heisler products) "
              "against a solve that does not separate variables.",
              f"- Slab bound (SV11): {sv11['comparisons']} comparisons on the grid Bi 0.01-100, Fo 1e-3-5; violations "
              f"{sv11['violations']}, ordering violations (sphere <= cylinder <= slab) {sv11['ordering_violations']}. This is numerical "
              "evidence for the bound on that grid, not a proof.",
              f"- Long-cylinder limit (SV04): centre and mean error by half-height / radius "
              f"{json.dumps(by['SV04']['error_by_half_height_over_radius'])} ([centre abs, mean rel]); the centre reaches the "
              "infinite cylinder at Lz >= 10 R, the mean converges like R / Lz.",
              f"- Short times (SV05): sphere surface against the semi-infinite solid, observed order in Fo "
              f"{json.dumps(by['SV05']['sphere_surface_observed_order_in_fo'])} (1 while Bi sqrt(Fo) << 1).",
              f"- Truncation (SV14): the term count is chosen from Fo (tail < {S.EPS_TAIL:g}); the largest count used in the grid is "
              f"{by['SV14']['largest_n_terms']}; Fo below {by['SV14']['fo_min']:.3g} is refused (semi-infinite regime).",
              "- SV09 compares with first-term constants recalled from the heat-transfer textbook tables and SV13 relies on the recalled "
              "statement that one term is within about 2 % at Fo >= 0.2: both tagged `SOURCE_UNVERIFIED_AGENT_RECALLED`, both also "
              "covered by exact checks (SV01, SV08) that do not depend on recall.",
              "- Not covered: property variation with temperature, irregular shapes, food data. The map from cut / ingredient class to "
              "shape (`registry/shape_map_v1.csv`) is ASSUMED_DEFAULT and is not verified by this pack.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--quick", action="store_true", help="coarser finite-volume grids (tests)")
    a = ap.parse_args(argv)
    for p in (a.out_json, a.out_md):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    t0 = time.time()
    checks = [_round(c) for c in V.run_all(quick=a.quick)]
    rep = {"record": "SHAPE_SERIES_VERIFICATION_PACK", "status": "AI_DRAFTED_NUMERICAL_VERIFICATION_NOT_A_VALIDATION",
           "version": V.VERSION, "shape_series_version": S.VERSION, "contains_text": False, "counts_as_human_gate": False,
           "wired_into_layer2": False, "command": CMD + (" --quick" if a.quick else ""),
           "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                           "platform": platform.system()},
           "code_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE},
           "recalled_constants_source_status": V.RECALLED, "checks": checks,
           "checks_passed": sum(c["passed"] for c in checks), "all_passed": all(c["passed"] for c in checks),
           "results_sha256": hashlib.sha256(json.dumps(checks, sort_keys=True).encode()).hexdigest(),
           "wall_seconds": round(time.time() - t0, 1)}
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    a.out_md.write_text(markdown(rep), encoding="utf-8")
    print(json.dumps({"checks_passed": rep["checks_passed"], "checks": len(checks), "results_sha256": rep["results_sha256"],
                      "wall_seconds": rep["wall_seconds"]}))
    return 0 if rep["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
