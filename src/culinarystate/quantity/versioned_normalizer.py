"""Versioned quantity normaliser; legacy normalize.py remains untouched.

Reuses the frozen v0 unit catalogue/helpers, retains its documented conversion
semantics, fixes an explicit zero multiplier, and masks invalid constructed
numeric input. Culinary conventions are not promoted to authoritative evidence.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from .grammar import QuantityParse
from .normalize import Normalized, UNK, _amount, _scaled, _volume_factor
from .units import BY_KEY

NORMALIZER_VERSION = "CQPO_NORMALIZE_V2"


@dataclass(frozen=True)
class NormalizedV2(Normalized):
    rule_version: str = NORMALIZER_VERSION


def normalize_v2(p: QuantityParse, locale: str | None = None) -> NormalizedV2:
    raw = p.raw
    values = [p.value, p.low, p.high, p.multiplier]
    if p.package_size:
        values.append(p.package_size[0])
    if p.stated:
        values.append(p.stated[0])
    if p.alt:
        values.append(p.alt[0])
    invalid = any(v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))
                  or isinstance(v, float) and not math.isfinite(v) or v < 0) for v in values)
    invalid = invalid or p.low is not None and p.high is not None and p.low > p.high
    if invalid:
        return NormalizedV2(dict(UNK), dict(UNK), dict(UNK), "NONE", "Q6", (),
                            tuple(p.flags) + ("INVALID_NUMERIC_INPUT",))
    if p.kind == "MULTIPLIER" and (p.multiplier is None or p.value != p.multiplier):
        return NormalizedV2(dict(UNK), dict(UNK), dict(UNK), "NONE", "Q6", (),
                            tuple(p.flags) + ("INVALID_MULTIPLIER",))
    if (p.unit_key is not None and p.unit_key not in BY_KEY
            or p.package_size and p.package_size[1] not in BY_KEY
            or p.stated and p.stated[1] not in BY_KEY or p.alt and p.alt[1] not in BY_KEY):
        return NormalizedV2(dict(UNK), dict(UNK), dict(UNK), "NONE", "Q6", (),
                            tuple(p.flags) + ("UNKNOWN_UNIT_KEY",))
    if p.kind == "QUALITATIVE":
        q = {"status": "QUALITATIVE", "qualitative": p.unit_raw or ",".join(p.qualifiers) or "qualitative",
             "raw": raw}
        return NormalizedV2(q, q, q, "NONE", "Q6", ("qualitative",))
    amt = _amount(p)
    mass, vol, cnt = dict(UNK), dict(UNK), dict(UNK)
    path: list[str] = []
    method, q = "NONE", "Q6"
    flags: list[str] = []
    unit = BY_KEY.get(p.unit_key) if p.unit_key else None
    mult = p.multiplier if p.multiplier is not None else 1.0

    if p.package_size and amt:                                   # "2 x 400g cans", "200g can"
        n_lo, n_hi = (mult, None) if p.kind == "MULTIPLIER" else amt
        cnt = _scaled(n_lo, n_hi, 1.0, "package", raw)
        size_v, size_u = p.package_size
        su = BY_KEY[size_u]
        if su.dimension == "MASS":
            mass = _scaled(n_lo, n_hi, size_v * su.si, "g", raw)
            method, q = "SOURCE_STATED", "Q0"
            path.append(f"{n_lo} x {size_v}{size_u} package (source-stated)")
        elif su.dimension == "VOLUME" and su.si:
            vol = _scaled(n_lo, n_hi, size_v * su.si, "mL", raw)
            method = "SOURCE_STATED"
            path.append(f"{n_lo} x {size_v}{size_u} package volume (source-stated)")
    elif unit and amt:
        lo, hi = amt
        if unit.dimension == "MASS":
            mass = _scaled(lo, hi, unit.si * mult, "g", raw)
            method, q = "EXACT_PHYSICAL", "Q0"
            path.append(f"{unit.key}->g x{unit.si} [{unit.si_source}]")
        elif unit.dimension == "VOLUME" and unit.si:
            vol = _scaled(lo, hi, unit.si * mult, "mL", raw)
            method = "EXACT_PHYSICAL"
            path.append(f"{unit.key}->mL x{unit.si} [{unit.si_source}]")
        elif unit.dimension == "VOLUME" and unit.conventions:
            f_lo, f_hi, note = _volume_factor(unit.key, locale)
            if f_hi is None:
                vol = _scaled(lo, hi, f_lo * mult, "mL", raw)
            else:
                vol = {"status": "RANGE", "low": round(lo * f_lo * mult, 6),
                       "high": round((hi if hi is not None else lo) * f_hi * mult, 6), "unit": "mL", "raw": raw}
                flags.append("locale_ambiguous")
            method = "LOCALE_CONVENTION"
            path.append(note)
        elif unit.unit_type == "REGIONAL":
            cnt = _scaled(lo, hi, mult, unit.key, raw)
            flags.append(f"non_standard_vessel:{unit.key}")
            path.append(f"{unit.key}: no standard volume -> volume UNKNOWN")
        elif unit.dimension == "COUNT":
            cnt = _scaled(lo, hi, mult, unit.key, raw)
            path.append(f"count of {unit.key}; grams need POR-")
    elif amt and unit is None:                                    # "3 eggs", "2 carrots", "juice of 1 lemon"
        lo, hi = amt
        cnt = _scaled(lo, hi, mult, "item" if not p.part else f"item ({p.part} of)", raw)
        path.append("bare count; grams need POR-")

    if p.stated and mass.get("status") == "UNKNOWN":
        v, u, sraw = p.stated
        su = BY_KEY[u]
        if su.dimension == "MASS":
            mass = {"status": "MEASURED", "value": round(v * su.si, 6), "unit": "g", "raw": sraw}
            method, q = "SOURCE_STATED", "Q0"
            path.append(f"parenthetical mass {sraw} (source-stated)")
        elif su.dimension == "VOLUME" and vol.get("status") == "UNKNOWN":
            vol = {"status": "MEASURED", "value": round(v * su.si, 6), "unit": "mL", "raw": sraw}
            path.append(f"parenthetical volume {sraw} (source-stated)")
    elif p.stated and mass.get("status") == "MEASURED":
        v, u, _ = p.stated
        su = BY_KEY[u]
        if su.dimension == "MASS" and abs(v * su.si - mass["value"]) > 0.25 * mass["value"]:
            flags.append("contradictory_stated_mass")               # SSOT §235.9: flag, never rewrite

    if p.alt and mass.get("status") == "MEASURED":
        av, au = p.alt
        aunit = BY_KEY[au]
        if aunit.dimension == "MASS" and abs(av * aunit.si - mass["value"]) > 0.15 * mass["value"]:
            flags.append("alt_unit_disagrees")
    if any(isinstance(v, float) and not math.isfinite(v)
           for channel in (mass, vol, cnt) for key, v in channel.items() if key in {"value", "low", "high"}):
        return NormalizedV2(dict(UNK), dict(UNK), dict(UNK), "NONE", "Q6", tuple(path),
                            tuple(flags + list(p.flags) + ["NONFINITE_NORMALIZATION"]))
    return NormalizedV2(mass, vol, cnt, method, q, tuple(path), tuple(flags + list(p.flags)))
