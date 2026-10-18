"""Deterministic normalization of a QuantityParse into mass / volume / count channels.

* exact physical units -> EXACT_PHYSICAL (Q0 for mass)
* culinary volume      -> LOCALE_CONVENTION; unknown locale or locale not covered -> RANGE over conventions
* package / parenthetical mass written in the line -> SOURCE_STATED (Q0)
* count / volume -> grams: only with a POR- record (none supplied yet) -> UNKNOWN (Q6)
* verbal (pinch, handful, to taste) -> QUALITATIVE on every channel (SSOT §235.5)
q_level describes the evidence behind mass_g (SSOT §235.3).
"""
from __future__ import annotations

from dataclasses import dataclass

from .grammar import QuantityParse
from .units import BY_KEY, SOURCES

UNK = {"status": "UNKNOWN"}


@dataclass(frozen=True)
class Normalized:
    mass_g: dict
    volume_ml: dict
    count: dict
    conversion_method: str
    q_level: str
    path: tuple[str, ...]
    flags: tuple[str, ...] = ()


def _scaled(lo: float, hi: float | None, factor: float, unit: str, raw: str) -> dict:
    if hi is None:
        return {"status": "MEASURED", "value": round(lo * factor, 6), "unit": unit, "raw": raw}
    return {"status": "RANGE", "low": round(lo * factor, 6), "high": round(hi * factor, 6), "unit": unit, "raw": raw}


def _amount(p: QuantityParse) -> tuple[float, float | None] | None:
    if p.value is not None:
        return p.value, None
    if p.low is not None and p.high is not None:
        return p.low, p.high
    return None


def _volume_factor(unit_key: str, locale: str | None) -> tuple[float, float | None, str]:
    u = BY_KEY[unit_key]
    if locale and locale in u.conventions:
        ml, src = u.conventions[locale]
        return ml, None, f"{unit_key}@{locale}={ml}mL [{src}:{SOURCES[src][2]}]"
    vals = sorted({ml for ml, _ in u.conventions.values()})
    return vals[0], vals[-1], f"{unit_key}@AMBIGUOUS_LOCALE={vals[0]}-{vals[-1]}mL"


def normalize(p: QuantityParse, locale: str | None = None) -> Normalized:
    raw = p.raw
    if p.kind == "QUALITATIVE":
        q = {"status": "QUALITATIVE", "qualitative": p.unit_raw or ",".join(p.qualifiers) or "qualitative",
             "raw": raw}
        return Normalized(q, q, q, "NONE", "Q6", ("qualitative",))
    amt = _amount(p)
    mass, vol, cnt = dict(UNK), dict(UNK), dict(UNK)
    path: list[str] = []
    method, q = "NONE", "Q6"
    flags: list[str] = []
    unit = BY_KEY.get(p.unit_key) if p.unit_key else None
    mult = p.multiplier or 1.0

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
    return Normalized(mass, vol, cnt, method, q, tuple(path), tuple(flags + list(p.flags)))
