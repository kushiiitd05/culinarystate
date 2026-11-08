"""Layer 2 SCENARIO for the physical-state dataset (S172, D-077). MODEL_DERIVED, NON_CITABLE, ASSUMED_DEFAULT.

Input: one Layer 1 event record (condition_binding / binding_census). Every Layer 1 value is kept (basis "L1:<b>");
only gaps are filled, from registry/scenario_defaults_v1.csv (SD ids, sources still to verify) or, for durations,
the corpus PROC_TYPICAL_DURATION quantiles (KGE ids). Three coherent brackets: GENTLE (least heat exposure: low bath
T, short time, low h, thick piece, cold start), TYPICAL (mid), INTENSE (most). Per bracket, physics_drivers gives the
slab-centre trajectory (when h and a size class exist): end temperature, minutes above 70 °C and the cook value
(T_ref 100 °C, z 33 °C); immersion media also get the surface cook value at bath temperature. Under SSOT §141 the
output is a driver trajectory with transition status `physically_possible`: no nutrient or yield number, ever.

S176 L-PHYS (version 0.2.0, default ON; ``CapPolicy(enabled=False)`` reproduces 0.1.0 exactly): the evaporation cap of
``phase_change``. For a matrix with free water the boundary temperature of the conduction problem is min(T_medium, T_boil)
(100 C at 1 atm, altitude optional, pressure processes at the saturation temperature of the bracket), so a moist core and
the volume average never exceed T_boil in dry heat, oil or pan. Additions per bracket: ``boundary_c``, ``t_cap_c``,
``volume_avg_end_c``, ``quality_cook_value_min`` (dose of the volume-average trajectory: quality doses use the volume
average, ``core_cook_value_min`` stays the core dose, the lower bound), ``surface_state`` (qualitative flags only, no
crust temperature) and the surface dose of immersion media at the capped temperature. The 0.1.0 core and dose fields of
oven, oil and pan events are SUPERSEDED (REV-A V2, SSOT v16 DRAFT 284.3).
"""
from __future__ import annotations

import csv
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from culinarystate.simulation import phase_change as PC
from culinarystate.simulation import physics_drivers as PD

ROOT = Path(__file__).resolve().parents[3]
VERSION = "scenario-layer-L2-0.2.0-draft"
VERSION_UNCAPPED = "scenario-layer-L2-0.1.0-draft"  # SUPERSEDED model, kept for the before/after comparison
LABELS = ["SCENARIO", "MODEL_DERIVED", "NON_CITABLE", "ASSUMED_DEFAULT"]
BRACKETS = ("GENTLE", "TYPICAL", "INTENSE")
IMMERSION = ("WATER", "LIQUID", "LIQUID_PARTIAL", "STEAM", "WATER_PRESSURIZED", "WATER_BATH_SEALED", "OIL_IMMERSION",
             "OIL_SHALLOW")
UNSUPPORTED = ("MICROWAVE", "RADIANT")
CORE_THRESHOLD_C = 70.0
T_REF_C, Z_C = 100.0, 33.0


def _f(v) -> float:
    return float(Fraction(str(v)))


def _triple(v) -> tuple[float, float, float]:
    if isinstance(v, list):
        lo, hi = _f(v[0]), _f(v[1])
        return lo, (lo + hi) / 2, hi
    x = _f(v)
    return x, x, x


class ScenarioLayer:
    def __init__(self, *, defaults: Mapping[str, Mapping[str, tuple]], gas: Mapping[str, tuple],
                 durations: Mapping[str, tuple], pc: PC.PhaseChange | None = None,
                 policy: PC.CapPolicy | None = None) -> None:
        self.d, self.gas, self.durations = defaults, gas, durations
        self.pc, self.policy = pc, policy or PC.CapPolicy()
        if self.policy.enabled and pc is None:
            raise ValueError("an enabled evaporation cap needs a PhaseChange registry")

    @property
    def capped(self) -> bool:
        return self.policy.enabled

    @classmethod
    def load(cls, root: Path = ROOT, policy: PC.CapPolicy | None = None) -> "ScenarioLayer":
        d: dict[str, dict[str, tuple]] = {}
        gas: dict[str, tuple] = {}
        with open(root / "registry/scenario_defaults_v1.csv", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                keys = r["applies_to"].split("|")
                if r["quantity"] == "gas_mark":
                    for k, v in zip(keys, r["low"].split("|")):
                        gas[k] = (float(v), r["default_id"])
                    continue
                for k in keys:
                    d.setdefault(r["quantity"], {})[k] = (float(r["low"]), float(r["mid"]), float(r["high"]),
                                                          r["default_id"])
        durations: dict[str, tuple] = {}
        with open(root / "ledgers/data/KGE.jsonl", encoding="utf-8") as fh:
            for line in fh:
                if '"PROC_TYPICAL_DURATION"' not in line:
                    continue
                e = json.loads(line)
                q = e.get("quantiles") or {}
                if e.get("status") == "ACTIVE" and q.get("p50") is not None and q.get("unit") == "min":
                    durations[e["subject_id"]] = (q["p10"], q["p50"], q["p90"], e["id"])
        return cls(defaults=d, gas=gas, durations=durations, pc=PC.PhaseChange.load(root), policy=policy)

    def _bath(self, rec) -> tuple[tuple | None, str | None]:
        t = rec["inputs"]["temperature_profile"]
        if t["status"] != "UNKNOWN":
            return _triple(t["value"]), f"L1:{t['basis']}"
        code = rec.get("oven_setpoint_code")
        if code and code in self.gas:
            v, sid = self.gas[code]
            return (v, v, v), sid
        row = self.d.get("bath_temperature", {}).get(rec["process_id"])
        return (row[:3], row[3]) if row else (None, None)

    def _duration(self, rec) -> tuple[tuple | None, str | None]:
        x = rec["inputs"]["duration"]
        if x["status"] != "UNKNOWN":
            return _triple(x["value"]), f"L1:{x['basis']}"
        q = self.durations.get(rec["process_id"])
        return ((q[0], q[1], q[2]), q[3]) if q else (None, None)

    def run(self, rec: Mapping[str, Any]) -> dict:
        medium = rec["inputs"]["medium"]["value"]
        base = {"recipe_id": rec.get("recipe_id"), "event_id": rec.get("event_id"), "process_id": rec["process_id"],
                "layer": "SCENARIO", "version": VERSION if self.capped else VERSION_UNCAPPED, "labels": list(LABELS),
                "medium": medium}
        if self.capped:
            base["cap_model"] = PC.VERSION
        if medium in UNSUPPORTED:
            return {**base, "status": "UNSUPPORTED_MEDIUM", "transition_status": "unsupported", "scenarios": {}}
        bath, b_basis = self._bath(rec)
        dur, d_basis = self._duration(rec)
        if bath is None or dur is None or medium is None:
            return {**base, "status": "SCENARIO_UNKNOWN", "transition_status": "unsupported", "scenarios": {},
                    "missing": [n for n, v in (("bath_c", bath), ("duration_min", dur), ("medium", medium)) if v is None]}
        h = self.d.get("h", {}).get(medium)
        size = rec["inputs"]["piece_size_class"]["value"]
        L = self.d.get("half_thickness", {}).get(size) if size else None
        k = self.d["k"]["FOOD_HIGH_MOISTURE"]
        a = self.d["alpha"]["FOOD_HIGH_MOISTURE"]
        t0 = self.d["initial_temperature"]["ALL"]
        mx = rec["inputs"].get("matrix_class") or {}
        matrix = mx.get("value") if mx.get("status", "UNKNOWN") != "UNKNOWN" else None
        out = {}
        for i, name in enumerate(BRACKETS):
            j = i  # GENTLE uses low exposure values, INTENSE high
            flags = ["HIGH_MOISTURE_PROPERTIES_ASSUMED", "SLAB_GEOMETRY_ASSUMED"]
            sc = {"bath_c": bath[j], "duration_min": dur[j], "initial_c": t0[j],
                  "bases": {"bath_c": b_basis, "duration_min": d_basis, "initial_c": t0[3], "k": k[3], "alpha": a[3]}}
            cap = self.pc.cap(medium=medium, matrix_class=matrix, bracket=i, policy=self.policy) if self.capped else None
            boundary = cap.boundary(bath[j]) if cap else bath[j]
            core = {"core_end_c": None, "core_minutes_above_70": None, "core_cook_value_min": None}
            core_end = None
            if self.capped:
                core.update(volume_avg_end_c=None, quality_cook_value_min=None)
            if h and L and dur[j] > 0:
                sc["h"], sc["half_thickness_m"] = h[j], L[2 - j]  # thick piece = least exposure
                sc["bases"].update(h=h[3], half_thickness_m=L[3])
                props = dict(half_thickness_m=L[2 - j], alpha_m2_s=a[1], h_w_m2k=h[j], k_w_mk=k[1])
                if self.capped:
                    zt = PD.zone_trajectory(t0_c=t0[j], bath_c=boundary, duration_min=dur[j], steps=40, **props)
                    traj = [(m, c) for m, c, _ in zt]
                    core.update(volume_avg_end_c=round(zt[-1][2], 3),
                                quality_cook_value_min=round(PD.trajectory_dose([(m, v) for m, _, v in zt],
                                                                                t_ref_c=T_REF_C, z_c=Z_C), 4))
                else:
                    traj = PD.core_trajectory(t0_c=t0[j], bath_c=bath[j], duration_min=dur[j], steps=40, **props)
                core_end = traj[-1][1]
                core.update(core_end_c=round(core_end, 3),
                            core_minutes_above_70=round(PD.minutes_above(traj, CORE_THRESHOLD_C), 3),
                            core_cook_value_min=round(PD.trajectory_dose(traj, t_ref_c=T_REF_C, z_c=Z_C), 4))
            else:
                flags.append("CORE_UNKNOWN_NO_SIZE" if not L else "CORE_UNKNOWN_NO_H")
            if medium not in IMMERSION:
                flags.append("SURFACE_NOT_AT_BATH_TEMPERATURE")
            surface = round(PD.equivalent_minutes([(dur[j], boundary)], t_ref_c=T_REF_C, z_c=Z_C), 4) \
                if medium in IMMERSION else None
            if cap is not None:
                binding = cap.binding(bath[j])
                sc.update(boundary_c=boundary, t_cap_c=cap.t_c,
                          surface_state=self.pc.surface_state(cap=cap, medium_c=bath[j], immersion=medium in IMMERSION,
                                                              core_end_c=core_end))
                if cap.basis:
                    sc["bases"]["t_cap_c"] = cap.basis
                flags += list(cap.flags)
                if cap.regime == PC.DRY:
                    flags.append("DRY_MATRIX_CONDUCTION_PROPERTIES_NOT_IN_REGISTRY")
                if cap.active:
                    flags.append("EVAPORATION_CAP_APPLIED" if binding else "EVAPORATION_CAP_NOT_BINDING")
                    if binding:
                        flags.append("CAPPED_BOUNDARY_ROBIN_SAME_H_NO_FLUX_LIMIT")
                        if surface is not None:
                            flags.append("SURFACE_DOSE_AT_TBOIL_WET_PERIOD_ONLY")
                if b_basis == "L1:PHYSICAL_DEFINITION" and "PRESSURE_ASSUMED_1ATM" not in flags:
                    flags.append("PRESSURE_ASSUMED_1ATM")
            out[name] = {**sc, **core, "surface_cook_value_min": surface, "flags": flags}
        return {**base, "status": "SCENARIO_COMPUTED", "transition_status": "physically_possible", "scenarios": out}
