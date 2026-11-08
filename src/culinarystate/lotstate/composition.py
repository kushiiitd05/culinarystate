"""Step 3: lot composition with exact interval bounds, solute load, optional water activity (all MODEL_DERIVED).

A lot is described by its members: ``Member(ing_id, fdc_id, band, mass)``, ``mass`` = exact (low, high) grams or None.
Composition is that of the members AS LISTED (SR Legacy values per 100 g); process effects (evaporation, leaching,
fat loss) are NOT modelled, so a cooked lot carries its ingredients' as-introduced composition (flag
``AS_LISTED_NO_PROCESS_EFFECTS``).

Kinds (``composition.kind``):
- ``SINGLE_MEMBER_POINT``   one usable member: its SR values, independent of its mass (POINT per nutrient).
- ``INTERVAL_EXACT_BOUNDS`` >= 2 usable members, every mass an interval: exact min / max of the mass-weighted
                            fraction over the box of member masses (``intervals.ratio_bounds``) per nutrient.
- ``PRESENCE_ONLY``         some member unmatched, below the band floor or without mass: three-valued presence per
                            nutrient (PRESENT / ABSENT / UNKNOWN), QUALITATIVE type.
- ``NO_MEMBERS``            the lot has no identified member.
A nutrient missing in SR for a member that could carry mass is UNKNOWN for the lot (never 0).

Solute load = g salt-equivalent (sodium x NaCl/Na mass ratio, all sodium taken as NaCl, so an upper bound on NaCl) and
g total sugars per g water; exact interval, ``open_upper`` when the lot may contain no water at all.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Mapping, Sequence

from . import values as V
from .intervals import frac, ratio_bounds
from .sr_legacy import NUTRIENT_KEYS, NUTRIENT_UNITS, SRLegacy

BAND_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
SCOPE_FLAG = "AS_LISTED_NO_PROCESS_EFFECTS"
KINDS = ("SINGLE_MEMBER_POINT", "INTERVAL_EXACT_BOUNDS", "PRESENCE_ONLY", "NO_MEMBERS")
# NaCl / Na mass ratio from standard atomic weights (58.44 / 22.99); agent-recalled, see the constants registry
NACL_PER_NA = Fraction("2.5421")


@dataclass(frozen=True)
class Member:
    ing_id: str | None
    fdc_id: int | None
    band: str = "NONE"
    mass: tuple[Fraction, Fraction] | None = None      # grams
    mass_basis: str = V.BASIS_UNKNOWN

    def usable(self, floor: str) -> bool:
        return self.ing_id is not None and self.fdc_id is not None and BAND_RANK.get(self.band, 0) >= BAND_RANK[floor]

    def may_carry_mass(self) -> bool:
        return self.mass is None or self.mass[1] > 0


@dataclass(frozen=True)
class CompositionConfig:
    min_band: str = "MEDIUM"          # members below this band are treated as unmatched
    nutrients: tuple[str, ...] = NUTRIENT_KEYS


def _prov(method: str, members: Sequence[Member], flags: Sequence[str], **extra) -> dict:
    bases = sorted({m.mass_basis for m in members})
    return V.provenance(method, inputs=("SR_LEGACY_2018_04", *bases), source_ids=("USDA_SR_LEGACY_FDC_2018_04",),
                        flags=(SCOPE_FLAG, *flags), mass_bases=bases, **extra)


def _unit(key: str) -> str:
    return f"{NUTRIENT_UNITS[key]}/100g"


def composition(members: Sequence[Member], sr: SRLegacy, cfg: CompositionConfig = CompositionConfig()) -> dict:
    """{"kind", "members_total", "members_usable", "match_floor", "nutrients": {key: value record}, "total_mass_g"}."""
    ms = list(members)
    if not ms:
        return {"kind": "NO_MEMBERS", "members_total": 0, "members_usable": 0, "match_floor": "NONE", "nutrients": {},
                "total_mass_g": V.unknown("g", "NO_MEMBERS")}
    floor_band = min((m.band if m.ing_id is not None and m.fdc_id is not None else "NONE" for m in ms),
                     key=lambda b: BAND_RANK.get(b, 0))
    usable = [m for m in ms if m.usable(cfg.min_band)]
    all_usable = len(usable) == len(ms)
    out = {"members_total": len(ms), "members_usable": len(usable), "match_floor": floor_band}
    masses = [m.mass for m in ms]
    if len(ms) == 1 and all_usable:
        m = ms[0]
        out["kind"] = "SINGLE_MEMBER_POINT"
        prov = _prov("SR_VALUE_SINGLE_MEMBER", ms, ("MASS_INDEPENDENT",))
        out["nutrients"] = {k: _single(sr, m, k, prov) for k in cfg.nutrients}
        out["total_mass_g"] = _mass_total(masses, ms)
        return out
    if all_usable and all(x is not None for x in masses):
        out["kind"] = "INTERVAL_EXACT_BOUNDS"
        prov = _prov("MASS_WEIGHTED_EXACT_INTERVAL_BOUNDS", ms, ())
        out["nutrients"] = {k: _interval(sr, ms, k, prov) for k in cfg.nutrients}
        out["total_mass_g"] = _mass_total(masses, ms)
        return out
    out["kind"] = "PRESENCE_ONLY"
    why = []
    if not all_usable:
        why.append("MEMBER_NOT_MATCHED_OR_BELOW_BAND")
    if any(x is None for x in masses):
        why.append("MEMBER_MASS_UNKNOWN")
    prov = _prov("PRESENCE_FROM_SR", ms, tuple(why))
    out["nutrients"] = {k: _presence(sr, ms, usable, all_usable, k, prov) for k in cfg.nutrients}
    out["total_mass_g"] = _mass_total(masses, ms)
    return out


def _mass_total(masses: Sequence, ms: Sequence[Member]) -> dict:
    if any(x is None for x in masses):
        return V.unknown("g", "MEMBER_MASS_UNKNOWN")
    lo = sum((x[0] for x in masses), Fraction(0))
    hi = sum((x[1] for x in masses), Fraction(0))
    return V.numeric(lo, hi, "g", basis="+".join(sorted({m.mass_basis for m in ms})), prov=_prov("SUM_OF_MEMBER_MASSES", ms, ()))


def _single(sr: SRLegacy, m: Member, key: str, prov: Mapping) -> dict:
    v = sr.nutrient(m.fdc_id, key)
    if v is None:
        return V.unknown(_unit(key), "SR_NUTRIENT_MISSING", basis="SR_VALUE", prov=prov)
    return V.numeric(v, v, _unit(key), basis="SR_VALUE", prov=prov)


def _interval(sr: SRLegacy, ms: Sequence[Member], key: str, prov: Mapping) -> dict:
    rows = []
    for m in ms:
        if not m.may_carry_mass():
            continue
        v = sr.nutrient(m.fdc_id, key)
        if v is None:
            return V.unknown(_unit(key), "SR_NUTRIENT_MISSING_FOR_A_MEMBER", basis="SR_VALUE+MASS_INTERVAL", prov=prov)
        rows.append((m.mass[0], m.mass[1], v, Fraction(1)))
    lo, hi, status = ratio_bounds(rows)
    if lo is None:
        return V.unknown(_unit(key), "NO_MASS", basis="SR_VALUE+MASS_INTERVAL", prov=prov)
    return V.numeric(lo, hi, _unit(key), basis="SR_VALUE+MASS_INTERVAL", prov=prov)


def _presence(sr: SRLegacy, ms: Sequence[Member], usable: Sequence[Member], all_usable: bool, key: str,
              prov: Mapping) -> dict:
    vals = [sr.nutrient(m.fdc_id, key) for m in usable]
    if any(v is not None and v > 0 for v in vals):
        label = "PRESENT"
    elif all_usable and all(v is not None and v == 0 for v in vals):
        label = "ABSENT"
    else:
        label = "UNKNOWN"
    if label == "UNKNOWN":
        return V.unknown(_unit(key), "PRESENCE_UNDETERMINED", basis="SR_VALUE", prov=prov)
    return V.qualitative(label, basis="SR_VALUE", prov=prov, unit=_unit(key))


# ---------------------------------------------------------------- solute load
SOLUTES = {"salt_g_per_g_water": ("sodium", NACL_PER_NA / 1000), "sugar_g_per_g_water": ("sugars", Fraction(1, 100))}


def solute_load(members: Sequence[Member], sr: SRLegacy, cfg: CompositionConfig = CompositionConfig()) -> dict:
    """{"salt_g_per_g_water": rec, "sugar_g_per_g_water": rec} with the same eligibility rules as composition()."""
    ms = list(members)
    out = {}
    for name, (nut, scale) in SOLUTES.items():
        out[name] = _solute(ms, sr, cfg, name, nut, scale)
    return out


def _solute(ms: Sequence[Member], sr: SRLegacy, cfg: CompositionConfig, name: str, nut: str, scale: Fraction) -> dict:
    unit = "g/g_water"
    if not ms:
        return V.unknown(unit, "NO_MEMBERS")
    usable = [m for m in ms if m.usable(cfg.min_band)]
    prov = _prov("SOLUTE_PER_WATER_FROM_SR", ms, ("SODIUM_ALL_AS_NACL_UPPER_BOUND", "NACL_PER_NA_SOURCE_UNVERIFIED_AGENT_RECALLED") if nut == "sodium" else ())
    if len(usable) != len(ms):
        return V.unknown(unit, "MEMBER_NOT_MATCHED_OR_BELOW_BAND", prov=prov)
    single = len(ms) == 1
    if not single and any(m.mass is None for m in ms):
        return V.unknown(unit, "MEMBER_MASS_UNKNOWN", prov=prov)
    rows = []
    for m in ms:
        if not m.may_carry_mass():
            continue
        a, w = sr.nutrient(m.fdc_id, nut), sr.nutrient(m.fdc_id, "water")
        if a is None or w is None:
            return V.unknown(unit, "SR_NUTRIENT_MISSING_FOR_A_MEMBER", prov=prov)
        lo, hi = (Fraction(1), Fraction(1)) if single else m.mass
        rows.append((lo, hi, a * scale, w / 100))
    lo, hi, status = ratio_bounds(rows)
    if status == "UNDEFINED":
        return V.unknown(unit, "NO_WATER_OR_NO_MASS", prov=prov)
    return V.numeric(lo, hi, unit, basis="SR_VALUE" if single else "SR_VALUE+MASS_INTERVAL", prov=prov,
                     open_upper=status == "UNBOUNDED_ABOVE")


# ---------------------------------------------------------------- water activity (gated, unsourced constants)
AW_REGISTRY = "registry/lotstate_aw_constants_draft_v1.csv"


@dataclass(frozen=True)
class AwConfig:
    allow_unverified_constants: bool = False      # default OFF: constants are recalled, not sourced
    registry_path: Path | None = None


def load_aw_constants(path: Path) -> dict[str, dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return {r["constant_id"]: r for r in csv.DictReader(fh)}


def water_activity(solutes: Mapping[str, dict], cfg: AwConfig = AwConfig()) -> dict:
    """Norrish (1966) for a sugar-water system, bracketed over the sugar constants in the registry; MODEL_DERIVED.

    Returns UNKNOWN unless ``cfg.allow_unverified_constants`` (the registry rows are
    SOURCE_UNVERIFIED_AGENT_RECALLED). Lots with any salt-equivalent above 0 are UNKNOWN (Norrish treats solutes as
    non-electrolytes). Ross (1975) is not implemented: it needs per-solute binary tables that are not in the repo.
    Monotone in every input (aw falls with sugar/water, K; rises with M), so the box corners give the exact model bounds.
    """
    unit = "aw"
    base = V.provenance("NORRISH_1966_SUGAR_BINARY", flags=("SOURCE_UNVERIFIED_CONSTANTS", "ROSS_NOT_IMPLEMENTED"))
    if not cfg.allow_unverified_constants:
        return V.unknown(unit, "AW_CONSTANTS_UNSOURCED_SWITCH_OFF", basis="MODEL", prov=base)
    if cfg.registry_path is None or not Path(cfg.registry_path).exists():
        return V.unknown(unit, "AW_CONSTANT_REGISTRY_MISSING", basis="MODEL", prov=base)
    consts = load_aw_constants(Path(cfg.registry_path))
    sugar, salt = solutes.get("sugar_g_per_g_water"), solutes.get("salt_g_per_g_water")
    if not sugar or sugar["type"] not in ("POINT", "INTERVAL") or sugar.get("open_upper"):
        return V.unknown(unit, "SUGAR_LOAD_UNKNOWN_OR_UNBOUNDED", basis="MODEL", prov=base)
    if not salt or salt["type"] not in ("POINT", "INTERVAL") or salt.get("open_upper"):
        return V.unknown(unit, "SALT_LOAD_UNKNOWN_OR_UNBOUNDED", basis="MODEL", prov=base)
    if Fraction(salt["exact"][1]) > 0:
        return V.unknown(unit, "ELECTROLYTE_PRESENT_NORRISH_NOT_VALID", basis="MODEL", prov=base)
    k_lo = min(Fraction(c["value"]) for c in consts.values() if c["role"] == "K" and c["solute_class"] == "SUGAR")
    k_hi = max(Fraction(c["value"]) for c in consts.values() if c["role"] == "K" and c["solute_class"] == "SUGAR")
    m_lo = min(Fraction(c["value"]) for c in consts.values() if c["role"] == "M" and c["solute_class"] == "SUGAR")
    m_hi = max(Fraction(c["value"]) for c in consts.values() if c["role"] == "M" and c["solute_class"] == "SUGAR")
    m_w = Fraction(consts["MW_WATER"]["value"])
    r_lo, r_hi = Fraction(sugar["exact"][0]), Fraction(sugar["exact"][1])

    def aw(r: Fraction, m: Fraction, k: Fraction) -> float:
        import math
        n_s, n_w = r / m, 1 / m_w
        x = float(n_s / (n_s + n_w))
        return (1.0 - x) * math.exp(-float(k) * x * x)

    lo, hi = aw(r_hi, m_lo, k_hi), aw(r_lo, m_hi, k_lo)
    prov = V.provenance("NORRISH_1966_SUGAR_BINARY", inputs=("SOLUTE_LOAD", AW_REGISTRY),
                        flags=("SOURCE_UNVERIFIED_CONSTANTS", "ROSS_NOT_IMPLEMENTED", "OUTSIDE_RANGE_CHECK_NOT_DONE"),
                        bounds_method="MONOTONE_BOX_CORNERS", source_ids=("SOURCE_UNVERIFIED_AGENT_RECALLED",))
    return {"type": "INTERVAL" if hi > lo else "POINT", "mask": 1, "low": lo, "high": hi, "unit": unit, "basis": "MODEL",
            "provenance": prov}
