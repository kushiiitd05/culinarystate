"""Evaporation / phase-change cap and qualitative surface state for the Layer 2 conduction drivers (S176 L-PHYS).

Why (REV-A V2, SSOT v16 DRAFT 284.3): the slab driver used the medium temperature as the boundary for every medium, so
a moist core in a 200 C oven, in oil or in a pan reached 160-220 C and the thermal doses were about 100 times too high.
While free water remains, a moist zone cannot exceed the local boiling point T_boil(P). This module supplies:

- ``PhaseChange.cap``: the cap for one event and bracket (matrix regime, medium, pressure, altitude) with its flags and
  registry id. The effective boundary temperature for conduction into a moist interior is min(T_medium, T_cap).
- ``surface_state``: QUALITATIVE flags only (SURFACE_WET_AT_TBOIL, then SURFACE_DRYING_POSSIBLE). No crust
  temperature or crust-onset time is produced; no sourced model exists for them.

T_boil: 100 C at 1 atm is a PROCESS_DEFINITION (PC-001, flag PRESSURE_ASSUMED_1ATM, sea level by default with flag
ALTITUDE_ASSUMED_SEA_LEVEL). A pressure process (medium WATER_PRESSURIZED) uses the saturation temperature at the stated or
scenario gauge pressure; with no pressure stated the scenario bracket is 108.4 / 115.2 / 121.0 C (5 / 10 / 15 psig) as
proposed by the L-SRC review (PC-002). Altitude is an optional parameter (rows PC-010..PC-014, valid 0-3000 m).
Every number in registry/phase_change_v1.csv carries its source status; none is human verified. The cap is an upper
bound, not a validated model, and it is never lifted here because no drying model exists (flag CAP_NOT_LIFTED_NO_DRYING_MODEL).

Matrix regimes (registry/matrix_moisture_regime_v1.csv): MOIST and MIXED_AMBIGUOUS (and an unknown matrix class) are
capped; DRY_LOW_MOISTURE (NUT_SEED, SWEETENER, FAT_OIL) is not. Ambiguous and unknown classes are capped because the
heat layer already assumes high-moisture properties for every matrix.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[3]
VERSION = "evaporation-cap-0.1.0-draft"
REGISTRY = "registry/phase_change_v1.csv"
REGIME_REGISTRY = "registry/matrix_moisture_regime_v1.csv"
PRESSURE_MEDIA = ("WATER_PRESSURIZED",)
ATM_ID, PRESSURE_ID = "PC-001", "PC-002"
MOIST, AMBIGUOUS, DRY, UNKNOWN_CLASS = "MOIST", "MIXED_AMBIGUOUS", "DRY_LOW_MOISTURE", "UNKNOWN_ASSUMED_MOIST"
# surface states (qualitative)
WET_AT_TBOIL, DRYING_POSSIBLE = "SURFACE_WET_AT_TBOIL", "SURFACE_DRYING_POSSIBLE"
WET_BELOW_TBOIL, IMMERSED_WET = "SURFACE_WET_BELOW_TBOIL_CAP_NOT_BINDING", "SURFACE_IMMERSED_WET"
NOT_APPLICABLE_DRY, STATE_UNKNOWN = "SURFACE_STATE_NOT_APPLICABLE_DRY_MATRIX", "SURFACE_STATE_UNKNOWN_CORE_NOT_COMPUTED"


@dataclass(frozen=True)
class CapPolicy:
    """Caller choices. ``altitude_m`` None means sea level at 1 atm (flagged); ``pressure_psig`` None means the bracket."""
    enabled: bool = True
    altitude_m: float | None = None
    pressure_psig: float | None = None


@dataclass(frozen=True)
class Cap:
    t_c: float | None  # None: no cap (dry matrix or cap disabled)
    regime: str
    basis: str | None
    flags: tuple = field(default_factory=tuple)

    @property
    def active(self) -> bool:
        return self.t_c is not None

    def boundary(self, medium_c: float) -> float:
        """Effective boundary temperature for conduction into the interior: min(T_medium, T_cap)."""
        return medium_c if self.t_c is None else min(medium_c, self.t_c)

    def binding(self, medium_c: float) -> bool:
        return self.t_c is not None and medium_c > self.t_c


def _interp(rows: Sequence[tuple[float, float]], x: float, what: str) -> float:
    xs = [r[0] for r in rows]
    if not xs[0] <= x <= xs[-1]:
        raise ValueError(f"{what} {x} outside the tabulated range {xs[0]}..{xs[-1]}")
    for (x0, y0), (x1, y1) in zip(rows, rows[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return rows[-1][1]


class PhaseChange:
    def __init__(self, *, nums: Mapping[str, Mapping[str, tuple]], regimes: Mapping[str, str]) -> None:
        self.nums, self.regimes = nums, dict(regimes)
        self._alt = sorted((float(k[4:]), v[1]) for k, v in nums["boiling_point_altitude"].items())
        self._psig = sorted((float(k[5:]), v[1]) for k, v in nums["saturation_temperature_gauge_psi"].items())
        self.drying_tol_c = nums["drying_criterion_core_within"]["ALL"][1]
        self.invariant_tol_c = nums["cap_invariant_tolerance"]["ALL"][1]

    @classmethod
    def load(cls, root: Path = ROOT) -> "PhaseChange":
        nums: dict[str, dict[str, tuple]] = {}
        with open(root / REGISTRY, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                nums.setdefault(r["quantity"], {})[r["applies_to"]] = (float(r["low"]), float(r["mid"]), float(r["high"]),
                                                                       r["default_id"])
        with open(root / REGIME_REGISTRY, newline="", encoding="utf-8") as fh:
            regimes = {r["matrix_class"]: r["regime"] for r in csv.DictReader(fh)}
        return cls(nums=nums, regimes=regimes)

    # ------------------------------------------------------------------------------------------ regimes
    def regime(self, matrix_class: str | None) -> str:
        if matrix_class is None:
            return UNKNOWN_CLASS
        return self.regimes.get(matrix_class, UNKNOWN_CLASS)

    @property
    def dry_classes(self) -> tuple[str, ...]:
        return tuple(sorted(k for k, v in self.regimes.items() if v == DRY))

    # ------------------------------------------------------------------------------------------ boiling points
    def t_boil_atmospheric_c(self, altitude_m: float | None = None) -> tuple[float, str, tuple]:
        """(T_boil, basis id, flags). No altitude: 100 C at 1 atm (PROCESS_DEFINITION), sea level assumed, flagged."""
        if altitude_m is None:
            return self.nums["boiling_point"]["ATM_1"][1], ATM_ID, ("PRESSURE_ASSUMED_1ATM", "ALTITUDE_ASSUMED_SEA_LEVEL")
        t = _interp(self._alt, float(altitude_m), "altitude_m")
        return t, "PC-010..PC-014", ("ALTITUDE_USER_SUPPLIED",)

    def t_sat_gauge_c(self, psig: float) -> float:
        """Saturation temperature at a gauge pressure (sea level), linear in the tabulated NIST-derived rows."""
        return _interp(self._psig, float(psig), "psig")

    # ------------------------------------------------------------------------------------------ the cap
    def cap(self, *, medium: str | None, matrix_class: str | None, bracket: int = 1,
            policy: CapPolicy | None = None) -> Cap:
        """Cap for one event and bracket (0 GENTLE, 1 TYPICAL, 2 INTENSE). ``policy.enabled`` False gives no cap."""
        policy = policy or CapPolicy()
        regime = self.regime(matrix_class)
        if not policy.enabled:
            return Cap(None, regime, None, ("EVAPORATION_CAP_DISABLED_BY_CALLER",))
        if regime == DRY:
            return Cap(None, regime, None, ("MATRIX_DRY_CLASS_UNCAPPED",))
        flags = {UNKNOWN_CLASS: ("MATRIX_UNKNOWN_MOIST_ASSUMED",), AMBIGUOUS: ("MATRIX_AMBIGUOUS_MOIST_ASSUMED",)}.get(regime, ())
        if medium in PRESSURE_MEDIA:
            if policy.pressure_psig is not None:
                t, basis = self.t_sat_gauge_c(policy.pressure_psig), "PC-030..PC-034"
                flags += ("PRESSURE_PROCESS_STATED_OR_SCENARIO_PSIG",)
            else:
                row = self.nums["boiling_point_pressure_process"]["WATER_PRESSURIZED"]
                t, basis = row[bracket], row[3]
                flags += ("PRESSURE_PROCESS_BRACKET_FROM_SATURATION_TEMPERATURE",)
            if policy.altitude_m is not None:
                flags += ("ALTITUDE_NOT_APPLIED_TO_PRESSURE_PROCESS",)
            return Cap(t, regime, basis, flags + ("CAP_NOT_LIFTED_NO_DRYING_MODEL", "CAP_IS_UPPER_BOUND_NOT_VALIDATED"))
        t, basis, f = self.t_boil_atmospheric_c(policy.altitude_m)
        return Cap(t, regime, basis, flags + f + ("CAP_NOT_LIFTED_NO_DRYING_MODEL", "CAP_IS_UPPER_BOUND_NOT_VALIDATED"))

    # ------------------------------------------------------------------------------------------ surface state
    def surface_state(self, *, cap: Cap, medium_c: float, immersion: bool, core_end_c: float | None) -> str:
        """QUALITATIVE surface regime at the end of the step; never a temperature.

        While the cap binds (the medium is hotter than T_cap) a moist surface sits at T_boil: SURFACE_WET_AT_TBOIL. Once the
        capped model's core is within ``drying_tol_c`` of T_cap the piece no longer absorbs sensible heat, all excess flux
        must go into evaporating water or into raising a dried surface: SURFACE_DRYING_POSSIBLE. Drying can start earlier
        (the onset time is not modelled), so WET_AT_TBOIL means "not yet forced to dry by the energy balance".
        """
        if cap.t_c is None:
            return NOT_APPLICABLE_DRY if cap.regime == DRY else STATE_UNKNOWN
        if not cap.binding(medium_c):
            return IMMERSED_WET if immersion else WET_BELOW_TBOIL
        if core_end_c is None:
            return STATE_UNKNOWN
        return DRYING_POSSIBLE if core_end_c >= cap.t_c - self.drying_tol_c else WET_AT_TBOIL
