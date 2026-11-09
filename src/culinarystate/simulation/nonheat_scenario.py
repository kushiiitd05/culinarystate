"""Layer 2 SCENARIO for the non-heat families (S176 L-NH, D-077 extension). MODEL_DERIVED, NON_CITABLE, ASSUMED_DEFAULT.

Input: one Layer 1 record from ``nonheat_binding``. Every Layer 1 value is kept (basis "L1:<basis>"); only gaps are
filled, from registry/scenario_defaults_nonheat_v1.csv (NH ids), the heat registry for shared properties (SD ids: k,
alpha, cut half-thickness, ambient start) and the corpus PROC_TYPICAL_DURATION quantiles (KGE ids). All registry rows
are SOURCE_UNVERIFIED_AGENT_RECALLED with ranges; none is presented as sourced.

Three coherent brackets, GENTLE / TYPICAL / INTENSE = low / mid / high of the PROCESS EFFECT (the least to the most
change the step can cause), so each parameter is read from the registry row in the direction that increases the
effect: faster heat transfer, colder cold medium, thinner piece, larger diffusivity, longer time, ...
(``_p(row, i, +1)`` reads the row low-to-high, ``-1`` high-to-low). Sizes are never invented: a missing cut class
leaves the geometry-dependent drivers UNKNOWN, exactly as in the heat layer.

Families and drivers (FORM candidate classes in nonheat_binding.FORM_CANDIDATE):
- COOLING: cool / chill: slab-centre trajectory with a cold medium (physics_drivers.core_trajectory) plus the time to a
  stated food target; freeze: Plank freezing time; defrost: Plank thawing time.
- SEPARATION: leaching hand-off code (which phase leaves the food system) and a liquid-removed fraction for drain/strain.
- FERMENT_LEAVEN: soak / marinate: Fickian slab uptake fraction (Bi -> infinity) for a salt, sugar or water medium; an
  ACID medium (vinegar, citrus juice) is reaction-diffusion: QUALITATIVE only (PH_FALLS), no Fickian number (S177);
  prove / ferment / germinate: qualitative state flags only (VOLUME_RISES, PH_FALLS), no number.
- PRESERVATION: dry: two-stage drying (constant rate then falling rate); pickle / brine: Fickian uptake; can: F0 upper bound
  at the medium temperature ONLY for pressure canning (PROC-000132 with a pressure canner, S177: F0 is the low-acid
  canning / retort reference, never cooking safety); pasteurise / sterilise / boiling-water-bath / oven canning: QUALITATIVE,
  F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY.
- MECHANICAL_CUT: characteristic half-thickness and surface/volume from the cut class, disruption level, enzyme-system
  flag and the stated lower bound of the time until the next heat step.
- MECHANICAL_MIX: qualitative flags AERATED / EMULSIFIED / DEVELOPED only.
- RESTING: carry-over after a linked heat step (finite-difference slab, heat stage then still-air stage). From 0.2.0
  (S176 L-PHYS) both stages carry the evaporation cap of ``phase_change`` for a moist matrix (boundary min(T_medium, T_boil)),
  so the core, peak and volume average never exceed T_boil unless the prior heat was a pressure process.
- STORAGE: storage temperature and the stated time bound; kinetics stay UNKNOWN pending PARAM rows (no model).

Under SSOT §141 every output is a temperature, a time, a geometry value or a dimensionless transport fraction, with
transition status `physically_possible`; no nutrient, compound, yield or safety number is produced.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping

from culinarystate.simulation import nonheat_binding as NB
from culinarystate.simulation import nonheat_drivers as ND
from culinarystate.simulation import phase_change as PC
from culinarystate.simulation import physics_drivers as PD
from culinarystate.simulation import scenario_layer as SL

ROOT = Path(__file__).resolve().parents[3]
VERSION = "nonheat-scenario-L2-0.4.0-draft"
VERSION_V03 = "nonheat-scenario-L2-0.3.0-draft"  # SUPERSEDED by 0.4.0 (Layer 1 temperature ownership; no per-axis provenance)
VERSION_V02 = "nonheat-scenario-L2-0.2.0-draft"  # SUPERSEDED by 0.3.0 (F0 scope, acid uptake, cap wording)
VERSION_UNCAPPED = "nonheat-scenario-L2-0.1.0-draft"  # SUPERSEDED RESTING model (no evaporation cap)
LABELS = list(SL.LABELS)
BRACKETS = SL.BRACKETS
REGISTRY = "registry/scenario_defaults_nonheat_v1.csv"
THRESHOLDS_C = (60.0, 5.0)  # reporting thresholds for cooling trajectories; not a food-safety assessment
HORIZON_MIN = 48 * 60.0
MEDIUM_TO_D = {"BRINE": "BRINE", "VINEGAR": "ACID", "CITRUS_JUICE": "ACID", "WATER": "WATER",
               "MARINADE_OTHER": "MARINADE_OTHER", "LIQUID_UNSPECIFIED": "WATER"}
ROLE_ROW = {"PROC-000038": "ROLE_COOL", "PROC-000039": "ROLE_CHILL", "PROC-000041": "ROLE_DEFROST"}
DRY_H = {"DEHYDRATOR": "OVEN_AIR_FORCED", "OVEN": "OVEN_AIR"}
DRY_T = {"DEHYDRATOR": "DEHYDRATOR", "OVEN": "OVEN_LOW"}
CAN_PID, CANNER_ENV = "PROC-000132", "PRESSURE_CANNER"  # F0 scope (SSOT v16 DRAFT 284.6): pressure canning only
STATE_FLAGS = {"PROC-000127": ["VOLUME_RISES"], "PROC-000128": ["PH_FALLS"], "PROC-000135": ["GERMINATION_ACTIVE"]}


def load_registry(path: Path) -> dict[str, dict[str, tuple]]:
    out: dict[str, dict[str, tuple]] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["source_status"].startswith("RETIRED"):  # kept in the file for the audit trail (IDs are never reused), never read
                continue
            for k in r["applies_to"].split("|"):
                out.setdefault(r["quantity"], {})[k] = (float(r["low"]), float(r["mid"]), float(r["high"]),
                                                        r["default_id"])
    return out


def _norm(o):
    """Copy with tuples as lists, so in-memory L1 records and L1 records read from JSON behave the same."""
    if isinstance(o, dict):
        return {k: _norm(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_norm(x) for x in o]
    return o


def _num(x: Mapping):
    """A numeric L1 value as float(s), or the class string for a qualitative one."""
    v = x["value"]
    if x["status"] in ("QUALITATIVE", "UNKNOWN") or isinstance(v, bool):
        return v
    return [SL._f(e) for e in v] if isinstance(v, list) else SL._f(v)


def _p(row: tuple, i: int, sign: int) -> float:
    """Registry value for bracket i; sign +1 reads low-to-high, -1 high-to-low (more effect = index 2)."""
    return row[i] if sign > 0 else row[2 - i]


def _t(tr: tuple, i: int, sign: int) -> float:
    return tr[i] if sign > 0 else tr[2 - i]



def l1_provenance(inputs: Mapping[str, Any]) -> dict:
    """{axis: {basis, span_id, row}} of the bound Layer 1 inputs of a non-heat record (S178 T4-C02; UNKNOWN axes are absent)."""
    return {k: {"basis": x.get("basis"), "span_id": x.get("span_id"), "row": x.get("row")}
            for k, x in sorted(inputs.items()) if isinstance(x, Mapping) and x.get("status", "UNKNOWN") != "UNKNOWN"}


class NonHeatScenario:
    def __init__(self, *, heat: SL.ScenarioLayer, nh: Mapping[str, Mapping[str, tuple]]) -> None:
        self.heat, self.nh = heat, nh

    @classmethod
    def load(cls, root: Path = ROOT, policy: PC.CapPolicy | None = None) -> "NonHeatScenario":
        return cls(heat=SL.ScenarioLayer.load(root, policy=policy), nh=load_registry(root / REGISTRY))

    @property
    def capped(self) -> bool:
        return self.heat.capped

    # ------------------------------------------------------------------------------------------ lookups
    def row(self, quantity: str, key: str | None) -> tuple | None:
        if key is None:
            return None
        return self.nh.get(quantity, {}).get(key) or self.heat.d.get(quantity, {}).get(key)

    def _size(self, rec) -> tuple[tuple | None, str | None]:
        x = rec["inputs"].get("piece_size_class") or {"status": "UNKNOWN"}
        if x["status"] == "UNKNOWN":
            return None, None
        r = self.row("half_thickness", x["value"])
        return (r, f"L1:{x['basis']}") if r else (None, None)

    def _duration(self, rec, name: str = "duration") -> tuple[tuple | None, str | None, list[str]]:
        x = rec["inputs"].get(name) or {"status": "UNKNOWN"}
        flags: list[str] = []
        kge = self.heat.durations.get(rec["process_id"])
        kge_t = (kge[0], kge[1], kge[2]) if kge else None
        if x["status"] in ("MEASURED", "RANGE"):
            return SL._triple(x["value"]), f"L1:{x['basis']}", flags
        if x["status"] == "QUALITATIVE" and x["value"] == "OVERNIGHT":
            r = self.row("overnight_duration", "ALL")
            return (r[:3], r[3], ["DURATION_FROM_OVERNIGHT_WORD"]) if r else (None, None, flags)
        if x["status"] in ("BOUND_UPPER", "BOUND_LOWER") and kge_t:
            b = SL._f(x["value"])
            clip = (lambda v: min(v, b)) if x["status"] == "BOUND_UPPER" else (lambda v: max(v, b))
            return tuple(clip(v) for v in kge_t), f"{kge[3]}+L1:{x['basis']}_BOUND", ["DURATION_CLIPPED_TO_STATED_BOUND"]
        if kge_t:
            return kge_t, kge[3], flags
        return None, None, flags

    def _out(self, status: str, transition: str, scenarios: dict, **extra) -> dict:
        return {"status": status, "transition_status": transition, "scenarios": scenarios, **extra}

    def _unknown(self, missing: list[str]) -> dict:
        return self._out("SCENARIO_UNKNOWN", "unsupported", {}, missing=missing)

    # ------------------------------------------------------------------------------------------ main
    def _base(self, rec: Mapping[str, Any]) -> dict:
        return {"recipe_id": rec.get("recipe_id"), "event_id": rec.get("event_id"), "process_id": rec["process_id"],
                "nh_family": rec["nh_family"], "process_role": rec["process_role"],
                "form_candidate": rec["form_candidate"], "layer": "SCENARIO",
                "version": VERSION if self.capped else VERSION_UNCAPPED, "labels": list(LABELS),
                "l1_provenance": l1_provenance(rec.get("inputs") or {})}

    def run(self, rec: Mapping[str, Any]) -> dict:
        rec = _norm(rec)  # a copy: the Layer 1 record is never written to
        fam, base = rec["nh_family"], self._base(rec)
        if any(c["name"] == "NON_VERB_SURFACE" for c in rec["cues"]):
            return {**base, **self._out("UNSUPPORTED_NON_VERB_SURFACE", "unsupported", {})}
        fn = {"COOLING": self._cooling, "SEPARATION": self._separation, "FERMENT_LEAVEN": self._ferment,
              "PRESERVATION": self._preservation, "MECHANICAL_CUT": self._cut, "MECHANICAL_MIX": self._mix,
              "RESTING": self._rest, "STORAGE": self._storage}[fam]
        return {**base, **fn(rec)}

    # ------------------------------------------------------------------------------------------ cooling
    def _cooling(self, rec) -> dict:
        inp, pid = rec["inputs"], rec["process_id"]
        env = inp["environment"]
        if env["status"] != "UNKNOWN" and env["value"] == "MICROWAVE":
            return self._out("UNSUPPORTED_MEDIUM", "unsupported", {})
        env_key, env_basis = (env["value"], f"L1:{env['basis']}") if env["status"] != "UNKNOWN" else (None, None)
        stated_t = inp["medium_temperature"]
        h_row = self.row("h", env_key or ROLE_ROW.get(pid))
        t_row = self.row("medium_temperature", env_key or ROLE_ROW.get(pid))
        t_basis = f"L1:{stated_t['basis']}" if stated_t["status"] != "UNKNOWN" else (
            t_row[3] if t_row else None)
        t_tr = SL._triple(stated_t["value"]) if stated_t["status"] != "UNKNOWN" else (t_row[:3] if t_row else None)
        size, size_basis = self._size(rec)
        k, a = self.row("k", "FOOD_HIGH_MOISTURE"), self.row("alpha", "FOOD_HIGH_MOISTURE")
        miss = [n for n, v in (("medium_temperature", t_tr), ("h", h_row), ("half_thickness", size)) if v is None]
        if miss:
            return self._unknown(miss)
        h_basis = h_row[3]
        if pid == "PROC-000040":
            return self._freeze(rec, t_tr, t_basis, h_row, size, size_basis)
        if pid == "PROC-000041":
            return self._thaw(rec, t_tr, t_basis, h_row, size, size_basis, k)
        dur, d_basis, dflags = self._duration(rec)
        if dur is None:
            return self._unknown(["duration_min"])
        start = inp["start_state"]
        if start["status"] != "UNKNOWN" and start["value"] == "POST_HEAT":
            t0_row, t0_sign, t0_basis, sflag = self.row("post_heat_temperature", "POST_HEAT"), -1, None, "START_POST_HEAT"
        else:
            t0_row, t0_sign, t0_basis, sflag = self.row("initial_temperature", "ALL"), -1, None, "START_UNKNOWN_AMBIENT_ASSUMED"
        tgt = inp["target_food_temperature"]
        out = {}
        for i, name in enumerate(BRACKETS):
            bath, h, L = _t(t_tr, i, -1), h_row[i], size[2 - i]
            t0 = _p(t0_row, i, t0_sign)
            traj = PD.core_trajectory(t0_c=t0, bath_c=bath, duration_min=dur[i], half_thickness_m=L, alpha_m2_s=a[1],
                                      h_w_m2k=h, k_w_mk=k[1], steps=40)
            rec_out = {"medium_c": bath, "duration_min": dur[i], "initial_c": t0, "h": h, "half_thickness_m": L,
                       "core_end_c": round(traj[-1][1], 3),
                       "bases": {"medium_c": t_basis, "environment": env_basis or h_basis, "duration_min": d_basis,
                                 "initial_c": t0_row[3], "h": h_basis,
                                 "half_thickness_m": size_basis + "|" + size[3], "k": k[3], "alpha": a[3]},
                       "flags": ["HIGH_MOISTURE_PROPERTIES_ASSUMED", "SLAB_GEOMETRY_ASSUMED", "REPORT_THRESHOLDS_NOT_SAFETY",
                                 sflag, *dflags]}
            for th in THRESHOLDS_C:
                rec_out[f"core_minutes_above_{int(th)}c"] = round(PD.minutes_above(traj, th), 3)
            if tgt["status"] != "UNKNOWN":
                tv = tgt["value"]
                rec_out["minutes_to_target_food_c"] = self._time_to(
                    SL._f(tv[1] if isinstance(tv, list) else tv), t0, bath, L, a[1], h, k[1])
                rec_out["bases"]["target_food_c"] = f"L1:{tgt['basis']}"
            out[name] = rec_out
        return self._out("SCENARIO_COMPUTED", "physically_possible", out)

    @staticmethod
    def _time_to(target_c: float, t0: float, bath: float, L: float, alpha: float, h: float, k: float):
        """Minutes until the slab centre reaches the target (None if the medium cannot bring it there)."""
        if (t0 - target_c) * (bath - target_c) >= 0:  # target is not between start and medium
            return None
        f = lambda m: PD.core_temperature(t0_c=t0, bath_c=bath, time_s=60 * m, half_thickness_m=L, alpha_m2_s=alpha,  # noqa: E731
                                          h_w_m2k=h, k_w_mk=k) - target_c
        lo, hi = 0.0, HORIZON_MIN
        if f(hi) * f(lo) > 0:
            return None
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if f(mid) * f(lo) > 0 else (lo, mid)
        return round(0.5 * (lo + hi), 3)

    def _phase_rows(self):
        return {q: self.row(q, "FOOD_HIGH_MOISTURE") for q in ("density_food", "latent_heat_freezing", "freezing_point",
                                                                  "k_frozen", "k")}

    def _freeze(self, rec, t_tr, t_basis, h_row, size, size_basis) -> dict:
        r = self._phase_rows()
        out, dur_known = {}, rec["inputs"]["duration"]
        for i, name in enumerate(BRACKETS):
            t_air, tf = _t(t_tr, i, -1), _p(r["freezing_point"], i, +1)
            if not t_air < tf:
                return self._unknown(["MEDIUM_NOT_BELOW_FREEZING_POINT"])
            thick = 2 * size[2 - i]
            secs = PD.plank_freezing_time_s(rho=_p(r["density_food"], i, -1), latent_j_kg=_p(r["latent_heat_freezing"], i, -1),
                                            t_freeze_c=tf, t_air_c=t_air, thickness_m=thick, h_w_m2k=h_row[i],
                                            k_frozen_w_mk=_p(r["k_frozen"], i, +1))
            rec_out = {"medium_c": t_air, "freezing_time_min": round(secs / 60, 3), "thickness_m": thick, "h": h_row[i],
                       "freezing_point_c": tf,
                       "bases": {"medium_c": t_basis, "h": h_row[3], "half_thickness_m": size_basis + "|" + size[3],
                                 **{q: v[3] for q, v in r.items() if q != "k"}},
                       "flags": ["PLANK_SLAB_P_HALF_R_EIGHTH", "START_AT_FREEZING_POINT_SENSIBLE_HEAT_NOT_INCLUDED",
                                 "HIGH_MOISTURE_PROPERTIES_ASSUMED"]}
            if dur_known["status"] in ("MEASURED", "RANGE"):
                d = SL._triple(dur_known["value"])[1]
                rec_out["frozen_within_stated_duration"] = bool(secs / 60 <= d)
                rec_out["bases"]["stated_duration_min"] = f"L1:{dur_known['basis']}"
            out[name] = rec_out
        return self._out("SCENARIO_COMPUTED", "physically_possible", out)

    def _thaw(self, rec, t_tr, t_basis, h_row, size, size_basis, k) -> dict:
        r = self._phase_rows()
        out, dur_known = {}, rec["inputs"]["duration"]
        for i, name in enumerate(BRACKETS):
            t_med, tf = _t(t_tr, i, +1), _p(r["freezing_point"], i, -1)
            if not t_med > tf:
                return self._unknown(["MEDIUM_NOT_ABOVE_FREEZING_POINT"])
            thick = 2 * size[2 - i]
            secs = ND.thaw_time_s(rho=_p(r["density_food"], i, -1), latent_j_kg=_p(r["latent_heat_freezing"], i, -1),
                                  t_freeze_c=tf, t_medium_c=t_med, thickness_m=thick, h_w_m2k=h_row[i],
                                  k_unfrozen_w_mk=k[i])
            rec_out = {"medium_c": t_med, "thaw_time_min": round(secs / 60, 3), "thickness_m": thick, "h": h_row[i],
                       "freezing_point_c": tf,
                       "bases": {"medium_c": t_basis, "h": h_row[3], "half_thickness_m": size_basis + "|" + size[3],
                                 "k_unfrozen": k[3], **{q: v[3] for q, v in r.items() if q not in ("k", "k_frozen")}},
                       "flags": ["THAW_AS_REVERSE_PLANK", "SUBCOOLING_OF_FROZEN_CORE_NOT_INCLUDED",
                                 "HIGH_MOISTURE_PROPERTIES_ASSUMED"]}
            if dur_known["status"] in ("MEASURED", "RANGE"):
                rec_out["thawed_within_stated_duration"] = bool(secs / 60 <= SL._triple(dur_known["value"])[1])
                rec_out["bases"]["stated_duration_min"] = f"L1:{dur_known['basis']}"
            out[name] = rec_out
        return self._out("SCENARIO_COMPUTED", "physically_possible", out)

    # ------------------------------------------------------------------------------------------ separation
    def _separation(self, rec) -> dict:
        inp = rec["inputs"]
        removed, fate = inp["removed_phase"], inp["liquid_fate"]
        if removed["status"] == "UNKNOWN":
            return self._unknown(["removed_phase"])
        rp = removed["value"]
        fv = fate["value"] if fate["status"] != "UNKNOWN" else None
        if rp == "LIQUID":
            handoff = {"DISCARDED": "AQUEOUS_PHASE_REMOVED_AND_DISCARDED",
                       "RETAINED": "AQUEOUS_PHASE_REMOVED_RETAINED_AS_SEPARATE_LOT"}.get(fv, "AQUEOUS_PHASE_REMOVED_FATE_UNKNOWN")
        elif rp == "SOLID":
            handoff = "SOLID_PHASE_REMOVED"
        elif rp == "SURFACE_FILM":
            handoff = "SURFACE_SOLUTES_WASHED_AWAY_PULSE"
        elif rp == "SURFACE_WATER":
            handoff = "SURFACE_WATER_REMOVED"
        else:
            handoff = "PHASE_SPLIT_UNSPECIFIED"
        flags = ["NO_COMPOUND_NUMBER"]
        if inp["follows_soak_or_brine"]["status"] != "UNKNOWN":
            flags.append("SOAK_DISCARD_CHAIN_CANDIDATE" if fv == "DISCARDED" else "FOLLOWS_SOAK_OR_BRINE")
        row = self.row("liquid_removed_fraction", {"PROC-000078": "DRAIN", "PROC-000079": "STRAIN"}.get(rec["process_id"]))
        out = {}
        for i, name in enumerate(BRACKETS):
            sc = {"handoff": handoff, "bases": {"removed_phase": f"L1:{removed['basis']}"}, "flags": list(flags)}
            if fate["status"] != "UNKNOWN":
                sc["bases"]["liquid_fate"] = f"L1:{fate['basis']}"
            if row and rp in ("LIQUID", "SOLID_LIQUID_SPLIT"):
                sc["liquid_removed_fraction"] = _p(row, i, +1)
                sc["bases"]["liquid_removed_fraction"] = row[3]
            out[name] = sc
        computed = bool(row and rp in ("LIQUID", "SOLID_LIQUID_SPLIT"))
        return self._out("SCENARIO_COMPUTED" if computed else "QUALITATIVE_FLAGS_ONLY", "physically_possible", out)

    # ------------------------------------------------------------------------------------------ uptake (ferment, pickle)
    def _uptake(self, rec) -> dict:
        inp = rec["inputs"]
        med = inp["medium"]
        if med["status"] == "UNKNOWN":
            return self._unknown(["medium"])
        dkey = MEDIUM_TO_D.get(med["value"])
        if dkey == "ACID":  # S177 (FINAL-SCI row 5): tissue buffering consumes the acid, so no Fickian bound exists for it
            return self._acid_marinade(rec, med)
        d_row = self.row("D_eff", dkey)
        size, size_basis = self._size(rec)
        dur, d_basis, dflags = self._duration(rec)
        miss = [n for n, v in (("D_eff", d_row), ("half_thickness", size), ("duration_min", dur)) if v is None]
        if miss:
            return self._unknown(miss)
        out = {}
        for i, name in enumerate(BRACKETS):
            D, L, t = _p(d_row, i, +1), size[2 - i], dur[i]
            flags = ["UPTAKE_FRACTION_OF_EQUILIBRIUM_NOT_A_CONCENTRATION", "FICKIAN_SLAB_BI_INFINITY",
                     "D_NOT_TEMPERATURE_ADJUSTED", "SLAB_GEOMETRY_ASSUMED", *dflags]
            if med["value"] == "LIQUID_UNSPECIFIED":
                flags.append("SOAK_LIQUID_ASSUMED_WATER")
            if any(inp[n]["status"] != "UNKNOWN" for n in ("salt_concentration_pct", "acid_concentration_pct")):
                flags.append("STATED_CONCENTRATION_NOT_USED_FOR_FRACTION")
            out[name] = {"D_eff_m2_s": D, "half_thickness_m": L, "duration_min": t,
                         "fourier_number": round(D * 60 * t / L ** 2, 6),
                         "uptake_fraction": round(PD.slab_uptake_fraction(d_m2_s=D, half_thickness_m=L, time_s=60 * t), 6),
                         "bases": {"D_eff_m2_s": d_row[3], "half_thickness_m": size_basis + "|" + size[3],
                                   "duration_min": d_basis, "medium": f"L1:{med['basis']}"}, "flags": flags}
        return self._out("SCENARIO_COMPUTED", "physically_possible", out)

    def _acid_marinade(self, rec, med) -> dict:
        """Vinegar or citrus-juice medium: QUALITATIVE only (the pH of the surface layer falls); no uptake number, no D."""
        dur, d_basis, dflags = self._duration(rec)
        out = {}
        for i, name in enumerate(BRACKETS):
            sc = {"state_flags": ["PH_FALLS"], "bases": {"medium": f"L1:{med['basis']}"},
                  "flags": ["ACID_UPTAKE_REACTION_DIFFUSION_QUALITATIVE_ONLY", "QUALITATIVE_ONLY_NO_NUMBER_FOR_STATE",
                            "NO_FICKIAN_UPTAKE_FOR_ACID_BUFFERED_BY_TISSUE", *dflags]}
            if dur:
                sc["duration_min"], sc["bases"]["duration_min"] = dur[i], d_basis
            out[name] = sc
        return self._out("QUALITATIVE_FLAGS_ONLY", "physically_possible", out)

    def _ferment(self, rec) -> dict:
        pid = rec["process_id"]
        if pid in ("PROC-000129", "PROC-000100"):
            return self._uptake(rec)
        flags = STATE_FLAGS.get(pid, [])
        dur, d_basis, dflags = self._duration(rec)
        out = {}
        for i, name in enumerate(BRACKETS):
            # S178: the flags come from the verb itself (STATE_FLAGS by process id): say so in the basis (T4-C02)
            sc = {"state_flags": list(flags), "flags": ["QUALITATIVE_ONLY_NO_NUMBER_FOR_STATE", *dflags],
                  "bases": {"state_flags": "L1:PROCESS_DEFINITION"}}
            if dur:
                sc["duration_min"], sc["bases"]["duration_min"] = dur[i], d_basis
            out[name] = sc
        return self._out("QUALITATIVE_FLAGS_ONLY", "physically_possible", out) if flags else self._unknown(["state_flag"])

    # ------------------------------------------------------------------------------------------ preservation
    def _preservation(self, rec) -> dict:
        pid, inp = rec["process_id"], rec["inputs"]
        if pid in ("PROC-000130", "PROC-000155"):
            return self._uptake(rec)
        if pid == "PROC-000133":
            return self._dry(rec)
        if any(c["name"] == "EQUIPMENT_LIKELY" for c in rec["cues"]):
            return self._out("UNSUPPORTED_TARGET_EQUIPMENT", "unsupported", {})
        stated = inp["medium_temperature"]
        env = inp["environment"]
        in_canner = env["status"] != "UNKNOWN" and env["value"] == CANNER_ENV
        canner = pid == CAN_PID and in_canner
        if stated["status"] != "UNKNOWN":
            t_tr, t_basis = SL._triple(stated["value"]), f"L1:{stated['basis']}"
        elif in_canner:  # canner steam temperature from the saturation rows PC-002 / PC-030..034 (not the retired NH-010)
            row = self.heat.pc.nums["boiling_point_pressure_process"]["WATER_PRESSURIZED"]
            t_tr, t_basis = row[:3], row[3]
        else:
            return self._unknown(["medium_temperature"])
        dur, d_basis, dflags = self._duration(rec)
        if dur is None:
            return self._unknown(["duration_min"])
        if not canner:  # S177 (FINAL-SCI row 4): F0 is the low-acid pressure-canning reference, never for anything else
            return self._f0_not_applicable(rec, t_tr, t_basis, dur, d_basis, dflags)
        z, tref = self.row("lethality_z", "F0"), self.row("lethality_t_ref", "F0")
        out = {}
        for i, name in enumerate(BRACKETS):
            T = _t(t_tr, i, +1)
            out[name] = {"medium_c": T, "duration_min": dur[i],
                         "f0_upper_bound_at_medium_t_min": round(ND.f0_minutes(minutes=dur[i], t_c=T, t_ref_c=tref[1],
                                                                              z_c=z[1]), 6),
                         "bases": {"medium_c": t_basis, "duration_min": d_basis, "lethality_z": z[3], "lethality_t_ref": tref[3]},
                         "flags": ["F0_UPPER_BOUND_AT_MEDIUM_T_NO_COMEUP_NO_COLD_SPOT_LAG", "F0_AT_MEDIUM_TEMPERATURE_NOT_COLD_SPOT",
                                   "LOW_ACID_FOOD_ASSUMED_NOT_CHECKED", "EQUIVALENT_MINUTES_ONLY_NO_ORGANISM_CLAIM", *dflags]}
        return self._out("SCENARIO_COMPUTED", "physically_possible", out)

    def _f0_not_applicable(self, rec, t_tr, t_basis, dur, d_basis, dflags) -> dict:
        """Pasteurise, sterilise, boiling-water-bath or oven 'canning': the stated conditions only, no F0 number."""
        env = rec["inputs"]["environment"]
        oven = env["status"] != "UNKNOWN" and env["value"] == "OVEN"
        out = {}
        for i, name in enumerate(BRACKETS):
            out[name] = {"medium_c": _t(t_tr, i, +1), "duration_min": dur[i],
                         "bases": {"medium_c": t_basis, "duration_min": d_basis},
                         "flags": ["F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY", "NO_NUMBER_EMITTED_OUTSIDE_F0_SCOPE",
                                   *(["OVEN_CANNING_NOT_A_VALID_PROCESS"] if oven else []), *dflags]}
        return self._out("QUALITATIVE_FLAGS_ONLY", "physically_possible", out)

    def _dry(self, rec) -> dict:
        inp = rec["inputs"]
        env = inp["environment"]
        if env["status"] == "UNKNOWN":
            return self._unknown(["environment"])
        if env["value"] == "MICROWAVE":
            return self._out("UNSUPPORTED_MEDIUM", "unsupported", {})
        if env["value"] not in DRY_H:
            return self._unknown(["environment_not_dehydrator_or_oven"])
        stated = inp["medium_temperature"]
        t_row = self.row("medium_temperature", DRY_T[env["value"]])
        if stated["status"] != "UNKNOWN":
            t_tr, t_basis = SL._triple(stated["value"]), f"L1:{stated['basis']}"
        else:
            t_tr, t_basis = t_row[:3], t_row[3]
        h_row = self.row("h", DRY_H[env["value"]])
        size, size_basis = self._size(rec)
        dur, d_basis, dflags = self._duration(rec)
        rows = {q: self.row(q, key) for q, key in (("wet_bulb_temperature", "DRYING_AIR"), ("latent_heat_vaporisation", "WATER"),
                                                    ("density_food", "FOOD_HIGH_MOISTURE"),
                                                    ("water_content_db_initial", "FOOD_HIGH_MOISTURE"),
                                                    ("water_content_db_critical", "FOOD_HIGH_MOISTURE"),
                                                    ("water_content_db_equilibrium", "DRYING_AIR"))}
        miss = [n for n, v in (("half_thickness", size), ("duration_min", dur)) if v is None]
        if miss:
            return self._unknown(miss)
        out = {}
        for i, name in enumerate(BRACKETS):
            T, wb = _t(t_tr, i, +1), _p(rows["wet_bulb_temperature"], i, -1)
            if not T > wb:
                return self._unknown(["AIR_NOT_WARMER_THAN_WET_BULB"])
            st = ND.drying_state(t_min=dur[i], h_w_m2k=h_row[i], t_air_c=T, t_wet_bulb_c=wb,
                                 latent_j_kg=_p(rows["latent_heat_vaporisation"], i, -1),
                                 rho_kg_m3=_p(rows["density_food"], i, -1), half_thickness_m=size[2 - i],
                                 x0_db=_p(rows["water_content_db_initial"], i, -1),
                                 xc_db=_p(rows["water_content_db_critical"], i, -1),
                                 xe_db=_p(rows["water_content_db_equilibrium"], i, -1))
            x0 = _p(rows["water_content_db_initial"], i, -1)
            out[name] = {"air_c": T, "wet_bulb_c": wb, "duration_min": dur[i], "half_thickness_m": size[2 - i],
                         "constant_rate_end_min": round(st["constant_rate_end_min"], 3),
                         "falling_rate_tau_min": round(st["falling_rate_tau_min"], 3),
                         "water_removed_fraction": round((x0 - st["x_end_db"]) / x0, 6),
                         "moisture_ratio": round(st["moisture_ratio"], 6), "time_class": st["time_class"],
                         "bases": {"air_c": t_basis, "duration_min": d_basis, "h": h_row[3],
                                   "half_thickness_m": size_basis + "|" + size[3],
                                   **{q: v[3] for q, v in rows.items()}},
                         "flags": ["TWO_STAGE_DRYING_SLAB_BOTH_FACES", "WATER_CONTENT_IS_A_DRYING_STATE_NOT_A_NUTRIENT",
                                   "RH_NOT_STATED_WET_BULB_ASSUMED", "SLAB_GEOMETRY_ASSUMED", *dflags]}
        return self._out("SCENARIO_COMPUTED", "physically_possible", out)

    # ------------------------------------------------------------------------------------------ cut, mix
    def _cut(self, rec) -> dict:
        inp = rec["inputs"]
        cls = inp["cut_class"]
        if cls["status"] == "UNKNOWN" or cls["value"] == "CUT_UNSPECIFIED":
            return self._unknown(["cut_class"])
        row = self.row("half_thickness", cls["value"])
        enz, nxt = inp["enzyme_system"], inp["time_until_next_heat"]
        out = {}
        for i, name in enumerate(BRACKETS):
            sc = {"cut_class": cls["value"], "disruption_level": inp["disruption_level"]["value"],
                  "bases": {"cut_class": f"L1:{cls['basis']}"}, "flags": ["ENZYME_RELEASE_IS_A_FLAG_NOT_A_NUMBER"]}
            if enz["status"] != "UNKNOWN":
                sc["enzyme_system_candidate"] = enz["value"]
                sc["bases"]["enzyme_system_candidate"] = f"L1:{enz['basis']}"
            if nxt["status"] != "UNKNOWN":
                sc["time_until_next_heat"] = _num(nxt)
                sc["time_until_next_heat_status"] = nxt["status"]
                sc["bases"]["time_until_next_heat"] = f"L1:{nxt['basis']}"
            if row:
                L = _p(row, i, -1)  # thinnest = most surface exposure = INTENSE
                sc.update({"half_thickness_m": L, "surface_to_volume_slab_per_m": round(ND.slab_av(L), 3),
                           "surface_to_volume_cube_per_m": round(ND.cube_av(L), 3)})
                sc["bases"]["half_thickness_m"] = row[3]
                sc["flags"].append("SLAB_OR_CUBE_BOUNDS_NOT_A_SHAPE_CLAIM")
            out[name] = sc
        return self._out("SCENARIO_COMPUTED" if row else "QUALITATIVE_FLAGS_ONLY", "physically_possible", out)

    def _mix(self, rec) -> dict:
        inp = rec["inputs"]
        flags = [n.upper() for n in ("aerated", "emulsified", "developed") if inp[n]["status"] != "UNKNOWN"]
        bases = {n.upper(): f"L1:{inp[n]['basis']}" for n in ("aerated", "emulsified", "developed")
                 if inp[n]["status"] != "UNKNOWN"}
        if not flags:
            return self._out("NO_FLAG_APPLICABLE", "unsupported", {})
        sc = {"state_flags": flags, "bases": bases, "flags": ["QUALITATIVE_ONLY_NO_NUMBER"]}
        return self._out("QUALITATIVE_FLAGS_ONLY", "physically_possible", {n: dict(sc) for n in BRACKETS})

    # ------------------------------------------------------------------------------------------ rest
    def _rest(self, rec) -> dict:
        ph = rec["history"].get("prior_heat")
        if not ph:
            return self._unknown(["prior_heat_link"])
        hrec = {"process_id": ph["process_id"], "inputs": ph["inputs"], "oven_setpoint_code": ph["oven_setpoint_code"]}
        medium = ph["inputs"]["medium"]["value"]
        if medium in SL.UNSUPPORTED:
            return self._out("UNSUPPORTED_MEDIUM", "unsupported", {})
        bath, b_basis = self.heat._bath(hrec)
        hdur, hd_basis = self.heat._duration(hrec)
        h_heat = self.heat.d.get("h", {}).get(medium)
        size, size_basis = self._size(rec)
        if size is None:
            psz = ph["inputs"]["piece_size_class"]
            r = self.row("half_thickness", psz["value"]) if psz["status"] != "UNKNOWN" else None
            size, size_basis = (r, f"HEAT_L1:{psz['basis']}") if r else (None, None)
        env = rec["inputs"]["environment"]
        env_key = env["value"] if env["status"] != "UNKNOWN" else "ROOM"
        h_air, t_air = self.row("h", env_key), self.row("medium_temperature", env_key)
        rdur, rd_basis, dflags = self._duration(rec)
        k, a, t0 = self.row("k", "FOOD_HIGH_MOISTURE"), self.row("alpha", "FOOD_HIGH_MOISTURE"), self.row("initial_temperature", "ALL")
        miss = [n for n, v in (("prior_heat_bath_c", bath), ("prior_heat_duration_min", hdur), ("prior_heat_h", h_heat),
                               ("half_thickness", size), ("rest_duration_min", rdur), ("rest_air", h_air and t_air)) if not v]
        if miss:
            return self._unknown(miss)
        hm = ph["inputs"].get("matrix_class") or {}
        matrix = hm.get("value") if hm.get("status", "UNKNOWN") != "UNKNOWN" else None
        groups = SL.member_groups(ph["inputs"])
        out = {}
        for i, name in enumerate(BRACKETS):
            L = size[2 - i]  # as in the heat layer: the thickest piece is the least exposed (GENTLE)
            stages = [(hdur[i], bath[i], h_heat[i]), (rdur[i], _p(t_air, i, +1), _p(h_air, i, -1))]
            cap_flags: list[str] = []
            caps = None
            t_cap = None
            if self.capped:
                pol = self.heat.policy
                c1 = self.heat.pc.cap(medium=medium, matrix_class=matrix, bracket=i, policy=pol, member_groups=groups,
                                      stated_liquid_c=bath[i] if b_basis in PC.STATED_BASES else None, stated_basis=b_basis)
                c2 = self.heat.pc.cap(medium=env_key, matrix_class=matrix, bracket=i, policy=pol)  # rest: atmospheric
                caps, t_cap = [c1.t_c, c2.t_c], c1.t_c
                cap_flags = list(c1.flags)
                if c1.active:
                    cap_flags.append("EVAPORATION_CAP_APPLIED" if c1.binding(bath[i]) else "EVAPORATION_CAP_NOT_BINDING")
                if c1.regime == PC.DRY:
                    cap_flags.append("DRY_MATRIX_CONDUCTION_PROPERTIES_NOT_IN_REGISTRY")
                if c2.active and c1.active and c1.t_c > c2.t_c:
                    cap_flags.append("PRESSURE_RELEASE_PROFILE_CLIPPED_TO_ATMOSPHERIC_TBOIL" if medium in PC.PRESSURE_MEDIA
                                     else "REST_PROFILE_CLIPPED_TO_ATMOSPHERIC_TBOIL_AFTER_STATED_LIQUID_T")
                if b_basis == "L1:PHYSICAL_DEFINITION" and "PRESSURE_ASSUMED_1ATM" not in cap_flags:
                    cap_flags.append("PRESSURE_ASSUMED_1ATM")
            res = ND.slab_two_stage(t0_c=t0[i], half_thickness_m=L, alpha_m2_s=a[1], k_w_mk=k[1], stages=stages, caps=caps)
            e1, e2 = res["stage_end"]
            rec_out = {"core_end_of_heat_c": round(e1["centre_c"], 3), "core_peak_c": round(res["centre_peak_last_stage_c"], 3),
                       "carryover_rise_c": round(max(0.0, res["centre_peak_last_stage_c"] - e1["centre_c"]), 3),
                       "core_end_c": round(e2["centre_c"], 3), "surface_end_c": round(e2["surface_c"], 3),
                       "rest_duration_min": rdur[i], "heat_duration_min": hdur[i], "heat_bath_c": bath[i],
                       "half_thickness_m": L,
                       "bases": {"heat_bath_c": b_basis, "heat_duration_min": hd_basis, "heat_h": h_heat[3],
                                 "half_thickness_m": size_basis + "|" + size[3], "rest_duration_min": rd_basis,
                                 "rest_air_c": t_air[3], "rest_h": h_air[3], "k": k[3], "alpha": a[3],
                                 "initial_c": t0[3], "prior_heat_link": f"L1:{ph['basis']}"},
                       "flags": ["FINITE_DIFFERENCE_SLAB_HEAT_THEN_STILL_AIR", "HIGH_MOISTURE_PROPERTIES_ASSUMED",
                                 "SLAB_GEOMETRY_ASSUMED", "UNIFORM_START_ASSUMED",
                                 *(cap_flags if self.capped else ["NO_EVAPORATION_CAP_AT_100C"]),
                                 "BRACKETS_ORDERED_BY_HEAT_DOSE_CARRYOVER_RISE_NOT_MONOTONE", *dflags]}
            if self.capped:
                rec_out.update(volume_avg_end_c=round(e2["volume_avg_c"], 3),
                               volume_avg_end_of_heat_c=round(e1["volume_avg_c"], 3), t_cap_c=t_cap,
                               boundary_c=bath[i] if t_cap is None else min(bath[i], t_cap))
                if t_cap is not None:
                    rec_out["bases"]["t_cap_c"] = c1.basis
            out[name] = rec_out
        return self._out("SCENARIO_COMPUTED", "physically_possible", out)

    # ------------------------------------------------------------------------------------------ storage
    def _storage(self, rec) -> dict:
        inp = rec["inputs"]
        env, stated, dur = inp["environment"], inp["medium_temperature"], inp["duration"]
        row = self.row("medium_temperature", env["value"]) if env["status"] != "UNKNOWN" else None
        if stated["status"] != "UNKNOWN":
            t_tr, t_basis = SL._triple(stated["value"]), f"L1:{stated['basis']}"
        elif row:
            t_tr, t_basis = row[:3], row[3]
        else:
            return self._unknown(["storage_temperature"])
        out = {}
        for i, name in enumerate(BRACKETS):
            sc = {"storage_c": _t(t_tr, i, +1), "kinetics": "UNKNOWN_PENDING_PARAM",
                  "bases": {"storage_c": t_basis}, "flags": ["NO_KINETICS_MODEL_PARAM_ROWS_PENDING"]}
            if dur["status"] != "UNKNOWN":
                sc["duration_bound_min"], sc["duration_bound_status"] = _num(dur), dur["status"]
                sc["bases"]["duration_bound_min"] = f"L1:{dur['basis']}"
            out[name] = sc
        return self._out("CONDITIONS_ONLY_KINETICS_UNKNOWN", "unsupported", out)


# ---------------------------------------------------------------------------------------------------- counts
# Per family: (main output key, direction GENTLE -> INTENSE). The census reports how many computed events violate the
# order, so a monotonicity failure stays visible (negative results are kept). The carry-over rise itself is NOT checked:
# it is physically non-monotone in the heat dose (a long heat equilibrates the piece and leaves less to carry over).
ORDER_CHECKS = {"COOLING": (("core_end_c", -1), ("freezing_time_min", -1), ("thaw_time_min", -1)),
                "FERMENT_LEAVEN": (("uptake_fraction", +1),), "PRESERVATION": (("uptake_fraction", +1),
                                   ("water_removed_fraction", +1), ("f0_upper_bound_at_medium_t_min", +1)),
                "MECHANICAL_CUT": (("half_thickness_m", -1),),
                "RESTING": (("core_end_of_heat_c", +1), ("core_peak_c", +1)),
                "STORAGE": (("storage_c", +1),), "SEPARATION": (("liquid_removed_fraction", +1),)}


def _basis_class(v: str) -> str:
    head = str(v).split("|")[0].split("+")[0]
    return head.split(":")[0] if head.startswith(("L1:", "HEAT_L1:")) else head.split("-")[0]


def count_row(out: Mapping[str, Any], c) -> None:
    """Add one L2 record to a Counter of tuple keys (counts only: no ids, no values)."""
    fam = out["nh_family"]
    c[("n", fam)] += 1
    c[("status", fam, out["status"])] += 1
    c[("transition", fam, out["transition_status"])] += 1
    for m in out.get("missing", ()):
        c[("missing", fam, m)] += 1
    sc = out["scenarios"]
    if not sc:
        return
    typ = sc["TYPICAL"]
    for k, v in typ.get("bases", {}).items():
        c[("basis", fam, k, _basis_class(v))] += 1
    for f in typ.get("flags", ()):
        c[("flag", fam, f)] += 1
    for key, sign in ORDER_CHECKS.get(fam, ()):
        vals = [sc[b].get(key) for b in BRACKETS]
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
            ok = all(sign * (vals[j + 1] - vals[j]) >= -1e-9 for j in range(2))
            c[("order", fam, key, "OK" if ok else "VIOLATION")] += 1
    if fam == "COOLING" and typ.get("minutes_to_target_food_c") is not None:
        c[("target_reached", fam, "TYPICAL")] += 1
