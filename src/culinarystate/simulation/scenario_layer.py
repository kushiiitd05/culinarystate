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

S177 SCIFIX-PHYS (version 0.3.0, FINAL-SCI rows 2 and 3; SSOT v16 DRAFT 284.3 / 284.4, PROPOSED):
- Row 2. The 0.2.0 field ``quality_cook_value_min`` was the dose of the VOLUME-AVERAGE TEMPERATURE, not the volume average of
  the local dose; by convexity of 10^(T/z) it is never larger than the zone-mean dose (about 2x low early, 1.1x low at 2 min
  for 1 cm dice at 98 C, worse for smaller z). It is renamed ``cook_value_at_volume_avg_t_min`` (flag ``NOT_A_ZONE_MEAN_DOSE``;
  ``volume_avg_dose`` still reads the legacy name from old records). Per bracket the layer now also emits the local temperature
  histories at 8 Gauss-Legendre nodes of the half slab (``zone_nodes``: xi, weights, times, temps) plus the node doses and
  their volume mean ``zone_mean_cook_value_min`` at the registry convention (T_ref 100 C, z 33 C). A kinetic model with its
  own Ea / z (M3) computes mean_i w_i exp(-int k(T_i) dt) from the stored histories (``physics_drivers.zone_mean_survival``).
  ``core_cook_value_min`` stays the CORE dose (the lower bound, unchanged).
- Row 3. The cap never goes below a temperature the text states for an aqueous liquid (``STATED_LIQUID_T_ABOVE_TBOIL``);
  boiling-point elevation is not modelled and a solute-rich member makes the cap a lower estimate; the regime is DRY when
  every member is a dry class; ``CAP_IS_UPPER_BOUND_NOT_VALIDATED`` is replaced by ``TBOIL_CEILING_DILUTE_AQUEOUS_ONLY``.
  Member groups are read from the optional Layer 1 input ``matrix_groups`` (a list of food groups); records that carry only
  ``matrix_class`` (single-group lots) behave as before.

S178 PHYS2 (version 0.4.0, T4-C02): no numerical change in the drivers. The record carries ``l1_provenance`` (basis, ``span_id`` and
``row`` of every Layer 1 axis the run used) so every L2 input traces to its Layer 1 evidence; ``OVEN_OR_AMBIENT_TEMPERATURE_STATED_
NOT_USED_AS_LIQUID_T`` marks an aqueous step whose Layer 1 record keeps an oven-cued ``ambient_temperature`` (0.2.0 Layer 1 never
binds it as the liquid temperature). The L1 input that feeds the stated-liquid cap is now the owned temperature of the step, not
the nearest temperature of the sentence (the 0.3.0 population of events lifted above 150 C came from that mis-association).

S178 FIX-PHYS (version 0.5.0, SCI-A M4 / M5 / m3 / m9 / m10; SSOT v16 DRAFT 284.3 / 284.4, PROPOSED, AI_DRAFTED):
- M4 the stated-liquid lift goes through ``PhaseChange.stated_liquid_lift`` (owned temperature + a sugar-phase member, a syrup /
  stage cue or a pressure cue up to PC-002 INTENSE + PC-041); otherwise the cap stays at T_boil, flagged
  STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_<why>.
- M5 a lifted value is the LIQUID's temperature. When a core is computed for a cut piece (CUT_HISTORY size) the conduction boundary
  is min(bath, T_boil of the piece) (flag STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE); ``boundary_c`` is that piece boundary, the
  surface dose of the immersion medium stays at the liquid's (lifted) boundary, ``t_cap_c`` is the liquid's cap. A pressure lift
  applies to the piece too (its water phase is pressurised as well).
- m3 an oven step with a Layer 1 ``water_bath_cue`` is run as a WATER medium (water h, boundary min(oven T, T_boil); flag
  WATER_BATH_IN_OVEN; record ``medium`` WATER, ``medium_rule`` WATER_BATH_IN_OVEN): an upper bound, the bath sits at or below T_boil.
- m9 numerics stated (``zone_nodes.numerical_rules``): ``zone_mean_cook_value_min`` integrates the dose rate by the trapezoid rule on
  the graded 48-step node grid; ``cook_value_at_volume_avg_t_min`` uses the midpoint temperature of a uniform 40-step grid. Measured
  against a dense reference (verification pack V18): the midpoint rule is biased LOW (-0.05 to -0.11 %), the graded trapezoid has
  either sign (-0.02 to +0.11 %); in every case tested the physical zone / volume-average ratio (1.06 to 24) is far above twice the
  bias, so "zone mean >= dose at the volume-average temperature" is not a numerical artefact there; it could be one only where the
  two agree to about 0.2 %.
- Layer 1 temperature flags (FAN_VS_CONVENTIONAL_UNRESOLVED, HEAT_LEVEL_OR_APPLIANCE_SETTING_AT_OR_BELOW_TBOIL) are carried to the
  bracket flags.
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
VERSION = "scenario-layer-L2-0.5.0-draft"
VERSION_V04 = "scenario-layer-L2-0.4.0-draft"  # SUPERSEDED by 0.5.0 (unconditional stated-liquid lift, lifted moist-piece cores)
VERSION_V03 = "scenario-layer-L2-0.3.0-draft"  # SUPERSEDED by 0.4.0 (L1 0.1.0 temperature association, no per-axis provenance)
VERSION_V02 = "scenario-layer-L2-0.2.0-draft"  # SUPERSEDED by 0.3.0 (quality_cook_value_min, upper-bound cap wording)
VERSION_UNCAPPED = "scenario-layer-L2-0.1.0-draft"  # SUPERSEDED model, kept for the before/after comparison
LABELS = ["SCENARIO", "MODEL_DERIVED", "NON_CITABLE", "ASSUMED_DEFAULT"]
BRACKETS = ("GENTLE", "TYPICAL", "INTENSE")
IMMERSION = ("WATER", "LIQUID", "LIQUID_PARTIAL", "STEAM", "WATER_PRESSURIZED", "WATER_BATH_SEALED", "OIL_IMMERSION",
             "OIL_SHALLOW")
UNSUPPORTED = ("MICROWAVE", "RADIANT")
CORE_THRESHOLD_C = 70.0
T_REF_C, Z_C = 100.0, 33.0
LEGACY_VOLUME_AVG_DOSE = "quality_cook_value_min"  # 0.2.0 name of cook_value_at_volume_avg_t_min


def volume_avg_dose(sc: Mapping[str, Any]) -> float | None:
    """Cook value at the volume-average temperature of one bracket record: the 0.3.0 name, else the 0.2.0 name of old records."""
    v = sc.get("cook_value_at_volume_avg_t_min")
    return v if v is not None else sc.get(LEGACY_VOLUME_AVG_DOSE)


def member_groups(inputs: Mapping[str, Any]) -> tuple[str, ...]:
    """Food groups of all lot members when the Layer 1 record carries them (``matrix_groups``), else an empty tuple."""
    x = inputs.get("matrix_groups") or {}
    v = x.get("value") if x.get("status", "UNKNOWN") != "UNKNOWN" else None
    return tuple(sorted({str(g) for g in v})) if isinstance(v, (list, tuple)) else ()


L1_PROVENANCE_AXES = ("temperature_profile", "duration", "medium", "piece_size_class", "matrix_class", "matrix_groups",
                      "ambient_temperature", "syrup_stage_cue", "pressure_cue", "water_bath_cue")
WATER_BATH_MEDIA = ("OVEN_AIR", "OVEN_AIR_FORCED")


def _bound(inputs: Mapping[str, Any], axis: str) -> bool:
    return (inputs.get(axis) or {}).get("status", "UNKNOWN") != "UNKNOWN"


def l1_provenance(inputs: Mapping[str, Any]) -> dict:
    """{axis: {basis, span_id, row}} of the bound Layer 1 axes a run read (UNKNOWN axes are absent: nothing was used)."""
    out = {}
    for axis in L1_PROVENANCE_AXES:
        x = inputs.get(axis) or {}
        if x.get("status", "UNKNOWN") != "UNKNOWN":
            out[axis] = {"basis": x.get("basis"), "span_id": x.get("span_id"), "row": x.get("row")}
    return out


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
                 policy: PC.CapPolicy | None = None, n_nodes: int = PD.N_ZONE_NODES) -> None:
        if not PD.ZONE_NODE_RANGE[0] <= n_nodes <= PD.ZONE_NODE_RANGE[1]:
            raise ValueError(f"n_nodes must be {PD.ZONE_NODE_RANGE[0]}..{PD.ZONE_NODE_RANGE[1]} Gauss-Legendre nodes")
        self.n_nodes = n_nodes
        self.d, self.gas, self.durations = defaults, gas, durations
        self.pc, self.policy = pc, policy or PC.CapPolicy()
        self.public, self.dropped_bbc_duration_edges = False, 0  # set by load(public=True) (SCI-B R1)
        if self.policy.enabled and pc is None:
            raise ValueError("an enabled evaporation cap needs a PhaseChange registry")

    @property
    def capped(self) -> bool:
        return self.policy.enabled

    @classmethod
    def load(cls, root: Path = ROOT, policy: PC.CapPolicy | None = None, n_nodes: int = PD.N_ZONE_NODES,
             public: bool = False) -> "ScenarioLayer":
        """``public`` (S178 FIX-PHYS, SCI-B R1, D-003): drop every corpus duration edge that ``public_mode.is_bbc_derived``
        names (all 39 ACTIVE PROC_TYPICAL_DURATION edges today), so an unstated duration is SCENARIO_UNKNOWN in public mode
        instead of a BBC aggregate. The default (False) reads exactly what it read before (the census tools use it)."""
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
        bbc = None
        if public:  # read-only import (public_mode belongs to the governance lane); lazy so the default path is unchanged
            from culinarystate.decision.public_mode import is_bbc_derived as bbc
        dropped: set[str] = set()
        with open(root / "ledgers/data/KGE.jsonl", encoding="utf-8") as fh:
            for line in fh:
                if '"PROC_TYPICAL_DURATION"' not in line:
                    continue
                e = json.loads(line)
                q = e.get("quantiles") or {}
                if e.get("status") == "ACTIVE" and q.get("p50") is not None and q.get("unit") == "min":
                    if bbc is not None and bbc(e):
                        dropped.add(e["id"])  # distinct edge ids (the ledger holds several versions of an edge)
                        continue
                    durations[e["subject_id"]] = (q["p10"], q["p50"], q["p90"], e["id"])
        layer = cls(defaults=d, gas=gas, durations=durations, pc=PC.PhaseChange.load(root), policy=policy,
                    n_nodes=n_nodes)
        layer.public, layer.dropped_bbc_duration_edges = bool(public), len(dropped)
        return layer

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
        inputs = rec["inputs"]
        medium = inputs["medium"]["value"]
        water_bath = medium in WATER_BATH_MEDIA and _bound(inputs, "water_bath_cue")
        if water_bath:  # m3: the food sits in water inside the oven, at or below T_boil
            medium = "WATER"
        base = {"recipe_id": rec.get("recipe_id"), "event_id": rec.get("event_id"), "process_id": rec["process_id"],
                "layer": "SCENARIO", "version": VERSION if self.capped else VERSION_UNCAPPED, "labels": list(LABELS),
                "medium": medium, "l1_provenance": l1_provenance(inputs)}
        if water_bath:
            base["medium_rule"] = "WATER_BATH_IN_OVEN"
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
        groups = member_groups(inputs)
        tp = inputs["temperature_profile"]
        l1_tflags = list(tp.get("flags") or []) if tp.get("status", "UNKNOWN") != "UNKNOWN" else []
        syrup, pressure = _bound(inputs, "syrup_stage_cue"), _bound(inputs, "pressure_cue")
        out = {}
        for i, name in enumerate(BRACKETS):
            j = i  # GENTLE uses low exposure values, INTENSE high
            flags = ["HIGH_MOISTURE_PROPERTIES_ASSUMED", "SLAB_GEOMETRY_ASSUMED"]
            if _bound(inputs, "ambient_temperature"):
                flags.append("OVEN_OR_AMBIENT_TEMPERATURE_STATED_NOT_USED_AS_LIQUID_T")
            if water_bath:
                flags += ["WATER_BATH_IN_OVEN", "WATER_BATH_TEMPERATURE_BOUNDED_BY_TBOIL_UPPER_BOUND"]
            flags += l1_tflags
            sc = {"bath_c": bath[j], "duration_min": dur[j], "initial_c": t0[j],
                  "bases": {"bath_c": b_basis, "duration_min": d_basis, "initial_c": t0[3], "k": k[3], "alpha": a[3]}}
            stated = bath[j] if (b_basis in PC.STATED_BASES and not water_bath) else None
            lift_reason = None
            if self.capped and stated is not None:  # M4: the Q1 gate decides whether the stated value may lift the cap
                stated, lift_reason, lflags = self.pc.stated_liquid_lift(
                    medium=medium, stated_c=stated, stated_row=tp.get("row"), matrix_class=matrix, member_groups=groups,
                    syrup_cue=syrup, pressure_cue=pressure, bracket=i, policy=self.policy)
                flags += list(lflags)
            cap = self.pc.cap(medium=medium, matrix_class=matrix, bracket=i, policy=self.policy, member_groups=groups,
                              stated_liquid_c=stated, stated_basis=b_basis, syrup_cue=syrup) if self.capped else None
            boundary = cap.boundary(bath[j]) if cap else bath[j]
            liquid_boundary = boundary
            piece_cap = cap
            if cap is not None and lift_reason in ("SUGAR_PHASE_MEMBER", "SYRUP_STAGE_CUE"):
                # M5: the lifted value is the liquid's; a moist piece in it is bounded by its own T_boil
                piece_cap = self.pc.cap(medium=medium, matrix_class=matrix, bracket=i, policy=self.policy, member_groups=groups,
                                        syrup_cue=syrup)
            core = {"core_end_c": None, "core_minutes_above_70": None, "core_cook_value_min": None}
            core_end = None
            if self.capped:
                core.update(volume_avg_end_c=None, cook_value_at_volume_avg_t_min=None, zone_mean_cook_value_min=None)
            if h and L and dur[j] > 0:
                if piece_cap is not cap:
                    boundary = piece_cap.boundary(bath[j])
                    flags.append("STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE")
                sc["h"], sc["half_thickness_m"] = h[j], L[2 - j]  # thick piece = least exposure
                sc["bases"].update(h=h[3], half_thickness_m=L[3])
                props = dict(half_thickness_m=L[2 - j], alpha_m2_s=a[1], h_w_m2k=h[j], k_w_mk=k[1])
                if self.capped:
                    zt = PD.zone_trajectory(t0_c=t0[j], bath_c=boundary, duration_min=dur[j], steps=40, **props)
                    traj = [(m, c) for m, c, _ in zt]
                    core.update(volume_avg_end_c=round(zt[-1][2], 3),
                                cook_value_at_volume_avg_t_min=round(PD.trajectory_dose([(m, v) for m, _, v in zt],
                                                                                        t_ref_c=T_REF_C, z_c=Z_C), 4))
                    flags.append("NOT_A_ZONE_MEAN_DOSE")
                    hist = PD.zone_node_histories(t0_c=t0[j], bath_c=boundary, duration_min=dur[j], n_nodes=self.n_nodes,
                                                  **{k_: v_ for k_, v_ in props.items()})
                    nd = PD.node_doses(hist, t_ref_c=T_REF_C, z_c=Z_C)
                    core["zone_mean_cook_value_min"] = round(sum(w * f for w, f in zip(hist["weights"], nd)), 4)
                    sc["zone_nodes"] = {"scheme": f"GAUSS_LEGENDRE_HALF_SLAB_{self.n_nodes}", "n_nodes": self.n_nodes,
                                        "xi": [round(x, 6) for x in hist["xi"]], "weights": [round(w, 8) for w in hist["weights"]],
                                        "times_min": [round(t, 5) for t in hist["times_min"]],
                                        "temps_c": [[round(t, 2) for t in row] for row in hist["temps_c"]],
                                        "node_cook_value_min": [round(f, 4) for f in nd],
                                        "t_ref_c": T_REF_C, "z_c": Z_C, "dose_rule": "TRAPEZOID_ON_DOSE_RATE",
                                        "volume_mean": "SUM_W_I_F_I_OVER_HALF_SLAB",
                                        "numerical_rules": {  # m9: the two doses do not use the same rule (V18 sizes the biases)
                                            "zone_mean_cook_value_min": "TRAPEZOID_ON_DOSE_RATE_GRADED_GRID_BIAS_EITHER_SIGN_V18",
                                            "cook_value_at_volume_avg_t_min": "MIDPOINT_T_UNIFORM_40_STEPS_BIASED_LOW_V18"}}
                    flags.append("ZONE_NODE_HISTORIES_EMITTED_FOR_OWN_KINETICS")
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
            surface = round(PD.equivalent_minutes([(dur[j], liquid_boundary)], t_ref_c=T_REF_C, z_c=Z_C), 4) \
                if medium in IMMERSION else None
            if cap is not None:
                state_cap = piece_cap if boundary != liquid_boundary else cap
                binding = state_cap.binding(bath[j])
                sc.update(boundary_c=boundary, t_cap_c=cap.t_c,
                          surface_state=self.pc.surface_state(cap=state_cap, medium_c=bath[j], immersion=medium in IMMERSION,
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
