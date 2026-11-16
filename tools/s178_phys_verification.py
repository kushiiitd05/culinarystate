#!/usr/bin/env python
"""Run the physical-layer verification pack and write the reproducible report (S178 PHYS2, T4-C07-R1). DRAFT, AI_DRAFTED.

    python tools/s178_phys_verification.py --out-json reports/s178/phys/verification_pack_S178_v05.json \
        --out-md reports/s178/phys/verification_pack_S178_v05.md      (S178 FIX-PHYS: 18 checks, independence classes)

Compares the slab series, the local temperature, the exact modal stepper, Plank and the Fickian slab with independent references
(analytic limits, finite-difference solves, textbook constants recalled by the agent and tagged SOURCE_UNVERIFIED_AGENT_RECALLED).
The report holds counts, errors and tolerances only; ``results_sha256`` hashes the check results rounded to 6 significant digits, so a
re-run on the same numpy reproduces it. Never overwrites. This is a numerical verification of the drivers, not a validation against food.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.simulation import phys_verification as V  # noqa: E402

CODE = ("src/culinarystate/simulation/phys_verification.py", "src/culinarystate/simulation/physics_drivers.py",
        "src/culinarystate/simulation/nonheat_drivers.py", "tools/s178_phys_verification.py")


def _round(x, sig: int = 6):
    if isinstance(x, float):
        return float(f"{x:.{sig}g}")
    if isinstance(x, dict):
        return {k: _round(v, sig) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_round(v, sig) for v in x]
    return x


def headline(checks: list[dict]) -> dict:
    by = {c["id"]: c for c in checks}
    series = ("V02", "V03", "V04", "V07", "V08")  # exact references; V01 is an approximate model (O(Bi) difference), reported apart
    return {"checks": len(checks), "checks_passed": sum(c["passed"] for c in checks), "all_passed": all(c["passed"] for c in checks),
            "slab_series_vs_independent_references": {
                "max_abs_error_theta": max(by[i]["max_abs_error"] for i in series),
                "max_rel_error_theta": max(by[i]["max_rel_error"] for i in series),
                "fd_reference_max_abs_error_theta": by["V08"]["max_abs_error"], "fd_reference_max_rel_error_theta": by["V08"]["max_rel_error"],
                "lumped_limit_difference_abs": by["V01"]["max_abs_error"]},
            "modal_stepper": {"spatial_order_observed": "2 (see V09)", "n160_max_abs_error_vs_series": by["V09"]["max_abs_error"],
                              "vs_crank_nicolson_max_abs_error_c": by["V11"]["max_abs_error"]},
            "n_terms": {"default": by["V12"]["n_terms_default"], "largest_n_needed_for_1e_10": by["V12"]["largest_needed_n"],
                        "max_abs_error_at_default": by["V12"]["max_abs_error"]},
            "plank": {"vs_ode_max_rel_error": by["V13"]["max_rel_error"],
                      "vs_enthalpy_stefan_by_ste": by["V14"]["results_by_stefan_number"]},
            "fickian": {"vs_fd_max_abs_error": by["V15"]["max_abs_error_vs_fd"], "half_uptake_tau_code": by["V15"]["half_uptake_tau_code"],
                        "half_uptake_tau_textbook": by["V15"]["half_uptake_tau_textbook"]},
            # S178 FIX-PHYS m7 / m9
            "independence": V.independence_counts(checks),
            "short_time_front_vs_fd_max_abs_error": by["V16"]["max_abs_error"] if "V16" in by else None,
            "zone_dose_vs_dense_reference_max_rel_error": by["V17"]["max_rel_error"] if "V17" in by else None,
            "dose_rule_bias": {k: by["V18"][k] for k in ("bias_by_case", "volume_avg_t_bias_sign", "zone_mean_bias_sign",
                                                         "inequality_exceeds_twice_the_bias")} if "V18" in by else None}


def markdown(rep: dict) -> str:
    h = rep["headline"]
    s = rep["headline"]["slab_series_vs_independent_references"]
    ind = h["independence"]
    lines = ["# Physical-layer verification pack (S178 PHYS2, T4-C07-R1; FIX-PHYS v05)", "",
             "Status: DRAFT / AI_DRAFTED. A numerical verification of the drivers against independent references; not a validation "
             "against food and not a human signature. Textbook constants are recalled by the agent (`SOURCE_UNVERIFIED_AGENT_RECALLED`).", "",
             f"Reproduce: `{rep['command']}`; `results_sha256` = `{rep['results_sha256']}` (check results rounded to 6 significant digits).", "",
             "**Independence (S178 FIX-PHYS m7).** " + "; ".join(f"{k}: {v['passed']} of {v['checks']} pass" for k, v in ind.items()
                                                                 if v["checks"]) +
             ". Only the INDEPENDENT checks compare the drivers with a reference that shares no formula or code path with them; IDENTITY "
             "and SELF_CONSISTENCY checks catch coding slips, not a wrong formula; LOOSE_TOLERANCE checks could pass a wrong trend "
             "(V14 is now also gated on the trend); RECALLED_CONSTANTS depend on agent-recalled table values.", "",
             f"**Result: {h['checks_passed']} of {h['checks']} checks pass.** Slab series against the exact independent references (Dirichlet "
             f"limit, semi-infinite solution, continuity, quadrature, 200-node finite-difference solve): max absolute error in theta {s['max_abs_error_theta']:.3g}, max relative "
             f"error {s['max_rel_error_theta']:.3g}; against the finite-difference solve alone {s['fd_reference_max_abs_error_theta']:.3g} "
             f"absolute / {s['fd_reference_max_rel_error_theta']:.3g} relative (theta floor 1e-3); the lumped (Bi -> 0) limit differs from the exact slab by {s['lumped_limit_difference_abs']:.2g} at Bi = 1e-3, the O(Bi) error of the lumped model itself. Exact modal stepper: observed spatial "
             f"order 2; error {h['modal_stepper']['n160_max_abs_error_vs_series']:.3g} at 160 nodes. N_TERMS = {h['n_terms']['default']}: "
             f"the series is converged to 1e-10 with {h['n_terms']['largest_n_needed_for_1e_10']} terms in the worst case at Fo >= 0.02.", "",
             "| id | independence | check | cases | max abs error | max rel error | tolerance | pass |", "|---|---|---|---:|---:|---:|---|---|"]
    for c in rep["checks"]:
        lines.append(f"| {c['id']} | {c.get('independence', '')} | {c['what']} | {c['n_cases']} | {c['max_abs_error']:.3g} | "
                     f"{c['max_rel_error']:.3g} | {c['tolerance']:g} ({c['tolerance_on']}) | {'yes' if c['passed'] else 'NO'} |")
    lines += ["", "## Plank against the enthalpy-method Stefan solve (V14)", "",
              "Plank neglects the sensible heat of the frozen layer, so it is the Stefan number -> 0 limit; the difference must fall with Ste.",
              "", "| Ste | enthalpy method (s) | Plank (s) | Plank / enthalpy |", "|---:|---:|---:|---:|"]
    for k, v in h["plank"]["vs_enthalpy_stefan_by_ste"].items():
        lines.append(f"| {k.split('_')[1]} | {v['enthalpy_s']} | {v['plank_s']} | {v['plank_over_enthalpy']} |")
    db = h.get("dose_rule_bias")
    if db:
        lines += ["", "## Dose-rule biases (V18, SCI-A m9)", "",
                  "The layer's zone-mean dose (trapezoid on the dose rate, graded 48-step node grid) and its dose at the volume-average "
                  "temperature (midpoint temperature, uniform 40 steps) against a dense reference (24 nodes, 1,200 uniform times). Signs: "
                  f"volume-average-T dose {db['volume_avg_t_bias_sign']}, zone mean {db['zone_mean_bias_sign']}; the physical "
                  f"zone / volume-average ratio exceeds twice the bias in every case: {db['inequality_exceeds_twice_the_bias']}.", "",
                  "| case | zone-mean bias | volume-average-T bias | reference zone / vol-avg - 1 |", "|---|---:|---:|---:|"]
        for k, v in db["bias_by_case"].items():
            lines.append(f"| {k} | {v['zone_mean_bias']:+.5f} | {v['volume_avg_t_bias']:+.5f} | {v['reference_ratio_minus_1']:.4f} |")
    lines += ["", "## Notes", "",
              "- V05 and V06 compare with the plane-wall table of the first-term constants (zeta_1, C_1) recalled from the heat-transfer "
              "textbook; V15 uses the recalled half-uptake time D t / L^2 = 4 x 0.04919. Both are tagged `SOURCE_UNVERIFIED_AGENT_RECALLED`: "
              "the pack does not depend on them for the analytic and finite-difference checks (V01-V04, V07-V18).",
              "- V06: the one-term (Heisler-chart) curve differs from the full series by up to 1.8 % at Fo = 0.2 and by less later, as the "
              "textbook says; the driver uses the full series.",
              "- V09 observed order: " + json.dumps(next(c for c in rep["checks"] if c["id"] == "V09")["observed_order_by_case"]) + ".",
              "- V12: the default N_TERMS has a margin of "
              f"{h['n_terms']['default'] / h['n_terms']['largest_n_needed_for_1e_10']:.0f}x over the worst case in the grid "
              "(Bi 0.1-1000, Fo 0.02-1).",
              "- Not covered: shape factors (cylinder, sphere), property variation with temperature, food data. Verification of the drivers "
              "says nothing about whether a recipe's food behaves like the model.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--quick", action="store_true", help="shorter Stefan sweep (tests)")
    a = ap.parse_args(argv)
    for p in (a.out_json, a.out_md):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    t0 = time.time()
    checks = V.run_all(quick=a.quick)
    checks = [_round(c) for c in checks]
    rep = {"record": "PHYSICAL_LAYER_VERIFICATION_PACK", "status": "AI_DRAFTED_NUMERICAL_VERIFICATION_NOT_A_VALIDATION",
           "version": V.VERSION, "contains_text": False, "counts_as_human_gate": False,
           "command": "python tools/s178_phys_verification.py --out-json reports/s178/phys/verification_pack_S178_v05.json "
                      "--out-md reports/s178/phys/verification_pack_S178_v05.md" + (" --quick" if a.quick else ""),
           "environment": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.system()},
           "code_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE},
           "recalled_constants_source_status": V.RECALLED, "checks": checks, "headline": _round(headline(checks)),
           "results_sha256": hashlib.sha256(json.dumps(checks, sort_keys=True).encode()).hexdigest(),
           "wall_seconds": round(time.time() - t0, 1)}
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    a.out_md.write_text(markdown(rep), encoding="utf-8")
    print(json.dumps({"checks_passed": rep["headline"]["checks_passed"], "checks": rep["headline"]["checks"],
                      "results_sha256": rep["results_sha256"], "wall_seconds": rep["wall_seconds"]}))
    return 0 if rep["headline"]["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
