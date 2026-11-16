#!/usr/bin/env python
"""D-100 Lane S / D-104: frozen AA Model A applied to every physics-v06 heat event in the D-104 domain.

Joins L1 (inputs) and L2 (scenarios) records by (recipe_id, event_id). For each event and scenario
(GENTLE / TYPICAL / INTENSE, never pooled): D-104 gate -> IN_DOMAIN with retention = exp(-k t) at the
frozen unseen-matrix 95 % predictive interval of ln k, or the first failing reason (no number).
Counts and quantiles only; RESEARCH_ONLY / NOT_VALIDATED / SCENARIO_DEFAULT.

    python tools/s179_formula_census.py --l1 data/derived/physical_L1_full_S179v06 \
        --l2 data/derived/physical_L2_full_S179v06 --out reports/s179/formula_census_aa_BBC_2026-11-13.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.simulation.aa_pilot_fit import predict_ln_k  # noqa: E402

FIT = "reports/step10/aa_pilot_model_a_fit_D085.json"
SCEN = ("GENTLE", "TYPICAL", "INTENSE")
ACIDIC_FRUIT_GROUPS = {"FRUIT", "SWEETENER", "BEVERAGE"}
WATER_MEDIA = {"WATER", "STEAM"}
LABELS = ["RESEARCH_ONLY", "NOT_VALIDATED", "SCENARIO_DEFAULT", "DIAGNOSTIC", "NO_HUMAN_SIGNOFF_D085"]
QS = (0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99)


def _v(inp: dict, key: str):
    x = (inp or {}).get(key)
    return x.get("value") if isinstance(x, dict) else x


LIQUID_MEDIA = {"LIQUID", "LIQUID_PARTIAL"}


def gate(r1: dict, r2: dict, scenario: str, *, liquid_required: bool = False) -> tuple[bool, str, float | None, float | None]:
    """D-104 (default) or D-106 (``liquid_required``): (in_domain, reason, food_T_C, duration_min)."""
    inp = r1.get("inputs") or {}
    mc, groups, medium = _v(inp, "matrix_class"), _v(inp, "matrix_groups") or [], _v(inp, "medium")
    groups = [g for g in (groups if isinstance(groups, list) else [groups]) if g]
    fruit = mc == "FRUIT" or (bool(groups) and set(groups) <= ACIDIC_FRUIT_GROUPS and "FRUIT" in groups)
    if not fruit:
        return False, "MATRIX_NOT_ACIDIC_FRUIT", None, None
    if medium is None:
        return False, "MEDIUM_UNKNOWN", None, None
    if medium in WATER_MEDIA:
        return False, "WATER_CONTACT", None, None
    if liquid_required and medium not in LIQUID_MEDIA:
        return False, "MEDIUM_NOT_LIQUID", None, None
    if r2.get("status") != "SCENARIO_COMPUTED":
        return False, "SCENARIO_NOT_COMPUTED", None, None
    sc = (r2.get("scenarios") or {}).get(scenario) or {}
    bath, cap, dur = sc.get("bath_c"), sc.get("t_cap_c"), sc.get("duration_min")
    if bath is None:
        return False, "SCENARIO_NOT_COMPUTED", None, None
    T = float(min(bath, cap)) if cap is not None else float(bath)
    if not 60.0 <= T <= 100.0:
        return False, "T_OUT_OF_RANGE", None, None
    if not dur or dur <= 0:
        return False, "NO_DURATION", None, None
    return True, "IN_DOMAIN", T, float(dur)


def retention(fit: dict, T: float, t_min: float) -> tuple[float, float, float]:
    mid, lo, hi = predict_ln_k(fit, T)
    # higher k -> lower retention, so the ln k upper bound gives the retention lower bound
    return math.exp(-math.exp(mid) * t_min), math.exp(-math.exp(hi) * t_min), math.exp(-math.exp(lo) * t_min)


def _quant(xs: list[float]) -> dict:
    if not xs:
        return {}
    s = sorted(xs)
    return {f"p{int(q * 100):02d}": round(s[min(len(s) - 1, int(q * (len(s) - 1)))], 4) for q in QS}


def _load(dirpath: Path) -> dict:
    out = {}
    for f in sorted(glob.glob(str(dirpath / "**" / "*.jsonl"), recursive=True)):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    out[(r["recipe_id"], r["event_id"])] = r
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--l1", required=True)
    ap.add_argument("--l2", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gate", choices=("D-104", "D-106"), default="D-106")
    a = ap.parse_args(argv)
    liquid = a.gate == "D-106"
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    fit = json.loads((ROOT / FIT).read_text())["fit"]
    L1, L2 = _load(Path(a.l1)), _load(Path(a.l2))
    reasons = {s: Counter() for s in SCEN}
    in_proc = {s: Counter() for s in SCEN}
    ret = {s: {"mid": [], "lo": [], "hi": []} for s in SCEN}
    fit_range = Counter()
    text_stated = 0
    missing_l1 = 0
    for key, r2 in L2.items():
        r1 = L1.get(key)
        if r1 is None:
            missing_l1 += 1
            continue
        inp = r1.get("inputs") or {}
        if all((inp.get(k) or {}).get("status") == "MEASURED" for k in ("temperature_profile", "duration")):
            text_stated += 1
        for s in SCEN:
            ok, why, T, t = gate(r1, r2, s, liquid_required=liquid)
            reasons[s][why] += 1
            if ok:
                m, lo, hi = retention(fit, T, t)
                ret[s]["mid"].append(m); ret[s]["lo"].append(lo); ret[s]["hi"].append(hi)
                in_proc[s][r2.get("process_id", "NO_PROC")] += 1
                fit_range[s] += 70.0 <= T <= 95.0
    res = {s: {"reasons": dict(reasons[s]), "in_domain": reasons[s]["IN_DOMAIN"], "in_fit_range_70_95": fit_range[s],
               "retention_mid_quantiles": _quant(ret[s]["mid"]), "retention_lo95_quantiles": _quant(ret[s]["lo"]),
               "retention_hi95_quantiles": _quant(ret[s]["hi"]),
               "in_domain_by_process": dict(in_proc[s].most_common(25))} for s in SCEN}
    rec = {"record": "AA_FORMULA_CENSUS", "decision": f"D-100 Lane S; gate {a.gate}", "labels": LABELS,
           "approver": "ksh+prv (AI, D-085)", "fit": FIT, "fit_sha256": hashlib.sha256((ROOT / FIT).read_bytes()).hexdigest(),
           "l1_dir": Path(a.l1).name, "l2_dir": Path(a.l2).name, "heat_events_l2": len(L2), "l2_without_l1": missing_l1,
           "text_stated_T_and_t_available": text_stated, "scenarios": res,
           "run_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
           "notes": ["Retention is the fraction of reduced ascorbic acid remaining for an unseen matrix (frozen Model A, 2 papers).",
                     "Food temperature = min(bath, moisture cap); scenario T and t are defaults, not observations.",
                     "pH not observed per event (PH_ASSUMED_FROM_FRUIT_CLASS); leaching UNKNOWN so water contact is excluded."],
           "contains_text": False, "contains_ids": False, "scientific_gate_pass": False}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as f:
        f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({s: {"in_domain": res[s]["in_domain"], "median_retention": res[s]["retention_mid_quantiles"].get("p50")}
                      for s in SCEN}), "heat events", len(L2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
