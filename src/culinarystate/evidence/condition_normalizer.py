"""Step 07: deterministic condition and measurement normalisation.

Rules: nothing is inferred. Qualitative stays qualitative, UNKNOWN stays UNKNOWN, boiling is never 100 C, pH is never defaulted, moisture/aw/pressure/O2 absent is never 0,
ambiguous values keep their raw form and receive a reason code. Every call returns status VALID / INVALID / AMBIGUOUS / UNKNOWN with reason codes.
Registries: registry/condition_variable_registry_v1.csv etc. (stable ids authoritative; raw source strings always kept).
"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG = ROOT / "registry"
VALID, INVALID, AMBIGUOUS, UNKNOWN = "VALID", "INVALID", "AMBIGUOUS", "UNKNOWN"
VALUE_TYPES = ("POINT", "INTERVAL", "TRAJECTORY", "QUALITATIVE", "UNKNOWN")

# reason codes
R_UNKNOWN_VAR, R_NOT_STATED, R_QUALITATIVE, R_NO_NUMERIC_MAPPING = "UNKNOWN_VARIABLE", "NOT_STATED", "QUALITATIVE_NOT_NUMERIC", "NO_SOURCED_NUMERIC_MAPPING"
R_UNIT_MISSING, R_UNIT_UNKNOWN, R_UNIT_DIM = "UNIT_MISSING", "UNIT_NOT_ALLOWED_FOR_VARIABLE", "UNIT_DIMENSION_MISMATCH"
R_RANGE, R_REVERSED, R_NONFINITE = "OUT_OF_PHYSICAL_RANGE", "INTERVAL_REVERSED", "NON_FINITE_VALUE"
R_PRESSURE_REF, R_PERCENT_FRACTION, R_BASIS_MISSING, R_LOCATION_MISSING = "PRESSURE_REFERENCE_UNSPECIFIED", "PERCENT_OR_FRACTION_AMBIGUOUS", "MEASUREMENT_BASIS_MISSING", "MEASUREMENT_LOCATION_MISSING"
R_TRAJ_ORDER, R_TRAJ_SHORT, R_TEMP_HIGH, R_DELTA_ABS = "TRAJECTORY_TIME_NOT_INCREASING", "TRAJECTORY_NEEDS_2_POINTS", "TEMPERATURE_IMPLAUSIBLY_HIGH", "TEMPERATURE_DIFFERENCE_VS_ABSOLUTE"
R_BOILING = "BOILING_POINT_NOT_ASSUMED"

_T = {"s": 1.0, "sec": 1.0, "secs": 1.0, "second": 1.0, "seconds": 1.0, "min": 60.0, "mins": 60.0, "minute": 60.0, "minutes": 60.0, "h": 3600.0, "hr": 3600.0, "hrs": 3600.0, "hour": 3600.0, "hours": 3600.0,
      "d": 86400.0, "day": 86400.0, "days": 86400.0, "week": 604800.0, "weeks": 604800.0, "month": 2629746.0, "months": 2629746.0, "year": 31556952.0, "years": 31556952.0}  # month/year: repo convention
_P = {"pa": 1.0, "kpa": 1e3, "mpa": 1e6, "bar": 1e5, "atm": 101325.0, "psi": 6894.757293168, "mmhg": 133.322387415, "torr": 133.322368421}
_L = {"um": 1e-6, "mm": 1e-3, "cm": 1e-2, "m": 1.0}
_W = {"w": 1.0, "kw": 1e3}
_F = {"hz": 1.0, "mhz": 1e6, "ghz": 1e9}
_RATIO = {"percent": 0.01, "%": 0.01, "fraction": 1.0, "g/100g": 0.01, "aw": 1.0}
_PH = {"ph": 1.0}
_DIMS = {"time": ("s", _T), "pressure": ("Pa", _P), "length": ("m", _L), "power": ("W", _W), "frequency": ("Hz", _F), "mass_fraction": ("fraction", _RATIO), "ratio": ("fraction", _RATIO), "dimensionless": ("as stated", _RATIO | _PH),
         "volume_fraction": ("fraction", _RATIO)}
_PREF = re.compile(r"^(pa|kpa|mpa|bar|atm|psi|mmhg|torr)\s*[\(\[]?\s*(a|abs|absolute|g|gauge|ga)?[\)\]]?$", re.I)
_PREF_SUFFIX = re.compile(r"^(psi|bar|kpa|mpa|pa)(a|g)$", re.I)


def _load_registry():
    out = {}
    with open(REG / "condition_variable_registry_v1.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["name"]] = r
    return out


VARS = _load_registry()


def _f(x):
    return None if x is None else float(x)


def _result(var, vtype, status, reasons, raw, **kw):
    d = {"variable": var, "variable_id": VARS[var]["condition_variable_id"] if var in VARS else None, "value_type": vtype, "status": status, "reasons": list(dict.fromkeys(reasons)), "raw": raw}
    d.update(kw)
    return d


def convert_temperature(value: float, unit: str, kind: str = "absolute") -> float:
    """-> Kelvin (absolute) or kelvin-difference. degC/degF/K; differences are scaled, never offset."""
    u = unit.strip().lower().replace("°", "deg").replace("º", "deg")
    u = {"c": "degc", "celsius": "degc", "f": "degf", "fahrenheit": "degf", "k": "k", "kelvin": "k"}.get(u, u)
    if u not in ("degc", "degf", "k"):
        raise ValueError(f"unknown temperature unit {unit!r}")
    if kind == "difference":
        return value * (5.0 / 9.0 if u == "degf" else 1.0)
    return {"degc": value + 273.15, "degf": (value - 32.0) * 5.0 / 9.0 + 273.15, "k": value}[u]


def _unit_factor(var, unit):
    meta = VARS[var]
    dim = meta["dimension"]
    if dim in ("temperature",):
        return "temperature", None
    if dim == "temperature_rate":
        return "temperature_rate", None
    if dim not in _DIMS:
        return dim, None
    canon, table = _DIMS[dim]
    key = (unit or "").strip().lower()
    return dim, (canon, table.get(key), key)


def normalize_value(var: str, *, value=None, low=None, high=None, unit=None, raw=None, qualitative=None, trajectory=None, location=None, basis=None, kind="absolute",
                    open_low=False, open_high=False, pressure_reference=None, sourced_mapping=None) -> dict:
    """Return a normalised condition value. Never fills absent values. `basis` in {'WET','DRY'} for moisture. `trajectory` = [(t_value, v_value), ...] with times in `unit` pairs (t_unit, v_unit)."""
    if var not in VARS:
        return _result(var, "UNKNOWN", INVALID, [R_UNKNOWN_VAR], raw)
    meta = VARS[var]
    res = []
    # --- qualitative / unknown ---
    if qualitative is not None and value is None and low is None and high is None and trajectory is None:
        if sourced_mapping and qualitative in sourced_mapping:
            m = sourced_mapping[qualitative]
            return _result(var, "POINT", VALID, ["NUMERIC_FROM_EXPLICIT_SOURCED_MAPPING"], raw or qualitative, qualitative=qualitative, mapping_source=m.get("source"), canonical_value=m["value"], canonical_unit=meta["canonical_unit"])
        reasons = [R_QUALITATIVE, R_NO_NUMERIC_MAPPING]
        if re.search(r"\bboil", str(qualitative), re.I) and meta["dimension"] == "temperature":
            reasons.append(R_BOILING)
        return _result(var, "QUALITATIVE", VALID, reasons, raw or qualitative, qualitative=qualitative)
    if value is None and low is None and high is None and trajectory is None:
        return _result(var, "UNKNOWN", UNKNOWN, [R_NOT_STATED], raw)
    dim = meta["dimension"]
    # --- trajectory ---
    if trajectory is not None:
        ts = [p[0] for p in trajectory]
        if len(trajectory) < 2:
            return _result(var, "TRAJECTORY", INVALID, [R_TRAJ_SHORT], raw)
        if any(b <= a for a, b in zip(ts, ts[1:])):
            return _result(var, "TRAJECTORY", INVALID, [R_TRAJ_ORDER], raw)
        status = VALID
        if dim == "temperature" and not location:
            status, res = AMBIGUOUS, [R_LOCATION_MISSING]
        return _result(var, "TRAJECTORY", status, res, raw, points=[list(p) for p in trajectory], location=location, unit_canonical=meta["canonical_unit"], note="point units must be normalised by the caller per axis")
    # --- numeric point / interval ---
    vals = [x for x in (value, low, high) if x is not None]
    if any((isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)) for x in vals):
        return _result(var, "UNKNOWN", INVALID, [R_NONFINITE], raw)
    is_interval = value is None and (low is not None or high is not None)
    lo_, hi_ = (low, high) if is_interval else (value, value)
    if is_interval and low is not None and high is not None and low > high:
        return _result(var, "INTERVAL", INVALID, [R_REVERSED], raw)
    vt = "INTERVAL" if is_interval else "POINT"
    status = VALID
    canon = None
    unit_c = meta["canonical_unit"]
    # temperature
    if dim in ("temperature", "temperature_rate"):
        if not unit:
            return _result(var, vt, AMBIGUOUS, [R_UNIT_MISSING], raw, low=low, high=high, value=value)
        try:
            if dim == "temperature":
                conv = lambda x: None if x is None else convert_temperature(x, unit, kind)
                k = "difference" if kind == "difference" else "absolute"
                if k == "absolute" and meta["absolute_or_difference"] == "difference":
                    res.append(R_DELTA_ABS)
                    status = AMBIGUOUS
            else:
                m = re.match(r"^(k|degc|°c|degf|°f)\s*/\s*(s|min|h)$", unit.strip().lower().replace("°", "deg"))
                if not m:
                    return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw)
                conv = lambda x: None if x is None else convert_temperature(x, m.group(1), "difference") / _T[m.group(2)]
        except ValueError:
            return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw)
        cv, cl, ch = conv(value), conv(low), conv(high)
        if dim == "temperature" and kind != "difference":
            if any(x is not None and x < 0 for x in (cv, cl, ch)):
                return _result(var, vt, INVALID, [R_RANGE], raw, value=value, low=low, high=high)
            if any(x is not None and x > 1773.15 for x in (cv, cl, ch)):
                status = AMBIGUOUS
                res.append(R_TEMP_HIGH)
        if var in ("temp_unspecified",):
            res.append(R_LOCATION_MISSING)
            status = AMBIGUOUS if status == VALID else status
        return _result(var, vt, status, res, raw, canonical_value=cv, canonical_low=cl, canonical_high=ch, canonical_unit=unit_c, open_low=bool(open_low), open_high=bool(open_high), location=location,
                       temperature_kind=kind if dim == "temperature" else "rate")
    # pressure
    if dim == "pressure":
        u = (unit or "").strip()
        if not u:
            return _result(var, vt, AMBIGUOUS, [R_UNIT_MISSING], raw, value=value, low=low, high=high)
        ref = pressure_reference
        base = u
        mm = _PREF.match(u) or None
        sm = _PREF_SUFFIX.match(u)
        if sm:
            base, ref = sm.group(1), {"a": "ABSOLUTE", "g": "GAUGE"}[sm.group(2).lower()]
        elif mm:
            base = mm.group(1)
            if mm.group(2):
                ref = "ABSOLUTE" if mm.group(2).lower().startswith("a") else "GAUGE"
        f = _P.get(base.lower())
        if f is None:
            return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw)
        if ref is None:
            res.append(R_PRESSURE_REF)
            status = AMBIGUOUS
            ref = "UNSPECIFIED"
        if any(x is not None and x < 0 for x in vals) and ref != "GAUGE":
            return _result(var, vt, INVALID, [R_RANGE], raw)
        c = lambda x: None if x is None else x * f
        return _result(var, vt, status, res, raw, canonical_value=c(value), canonical_low=c(low), canonical_high=c(high), canonical_unit="Pa", pressure_reference=ref, open_low=bool(open_low), open_high=bool(open_high))
    # generic dimensions
    d, info = _unit_factor(var, unit)
    if info is None:  # categorical or 'as stated'
        return _result(var, vt, AMBIGUOUS, ["NO_UNIT_TABLE_FOR_VARIABLE"], raw, value=value, low=low, high=high, unit=unit)
    canon_unit, factor, key = info
    if var == "ph":
        factor, key = 1.0, "ph"
    if not unit and var not in ("ph",):
        if dim in ("mass_fraction", "ratio", "volume_fraction", "dimensionless"):
            return _result(var, vt, AMBIGUOUS, [R_PERCENT_FRACTION, R_UNIT_MISSING], raw, value=value, low=low, high=high)
        return _result(var, vt, AMBIGUOUS, [R_UNIT_MISSING], raw, value=value, low=low, high=high)
    if factor is None:
        return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw, unit=unit)
    if var == "water_activity":
        factor = 1.0
    c = lambda x: None if x is None else x * factor
    cv, cl, ch = c(value), c(low), c(high)
    vmin, vmax = meta["valid_min"], meta["valid_max"]
    chk = [x for x in (cv, cl, ch) if x is not None]
    if var == "ph":
        bad = any(x < 0 or x > 14 for x in chk)
    elif var == "water_activity":
        bad = any(x < 0 or x > 1 for x in chk)
    else:
        bad = any((vmin != "" and x < float(vmin)) or (vmax != "" and x > float(vmax)) for x in chk)
    if bad:
        return _result(var, vt, INVALID, [R_RANGE], raw, value=value, low=low, high=high, unit=unit)
    if var == "moisture_content":
        if basis not in ("WET", "DRY"):
            return _result(var, vt, AMBIGUOUS, [R_BASIS_MISSING], raw, canonical_value=cv, canonical_low=cl, canonical_high=ch, canonical_unit=canon_unit)
        if basis == "WET" and any(x > 1 for x in chk):
            return _result(var, vt, INVALID, [R_RANGE], raw)
    if dim in ("mass_fraction", "ratio", "volume_fraction") and key == "fraction" and any(x > 1 for x in chk) and var != "moisture_content":
        return _result(var, vt, INVALID, [R_RANGE, R_PERCENT_FRACTION], raw)
    return _result(var, vt, status, res, raw, canonical_value=cv, canonical_low=cl, canonical_high=ch, canonical_unit=canon_unit, open_low=bool(open_low), open_high=bool(open_high), basis=basis)


# ---------- adapter for the repo QVALUE dicts (COND ledger) ----------
_TEMP_LOC = {"SETPOINT": "temp_equipment_setpoint", "MEDIUM": "temp_medium", "SURFACE": "temp_surface", "CORE": "temp_core", "UNSPECIFIED": "temp_unspecified"}


def from_qvalue(var: str, qv: dict | None, *, location: str | None = None, **kw) -> dict:
    """QVALUE statuses: MEASURED -> POINT; RANGE -> INTERVAL; CENSORED -> INTERVAL with an open end; QUALITATIVE -> QUALITATIVE; anything else/None -> UNKNOWN."""
    if not qv or qv.get("status") in (None, "UNKNOWN", "NOT_APPLICABLE"):
        return normalize_value(var, raw=(qv or {}).get("raw"), **kw)
    st, raw, unit = qv["status"], qv.get("raw"), qv.get("unit")
    if st == "MEASURED":
        return normalize_value(var, value=qv.get("value"), unit=unit, raw=raw, location=location, **kw)
    if st == "RANGE":
        return normalize_value(var, low=qv.get("low"), high=qv.get("high"), unit=unit, raw=raw, location=location, **kw)
    if st == "CENSORED":
        cz = qv.get("censor") or {}
        lim = cz.get("limit", qv.get("value"))
        kind = str(cz.get("kind", ""))
        if kind.startswith("GT") or kind == "ABOVE_CAP":
            return normalize_value(var, low=lim, unit=unit, raw=raw, open_high=True, location=location, **kw)
        return normalize_value(var, high=lim, unit=unit, raw=raw, open_low=True, location=location, **kw)
    if st == "QUALITATIVE":
        return normalize_value(var, qualitative=qv.get("qualitative") or raw, raw=raw, **kw)
    return _result(var, "UNKNOWN", AMBIGUOUS, [f"UNRECOGNISED_QVALUE_STATUS:{st}"], raw)


def temperature_variable_for(location: str | None) -> str:
    return _TEMP_LOC.get((location or "UNSPECIFIED").upper(), "temp_unspecified")


# ---------- measurement fields ----------
_BASIS = {"FRESH_WEIGHT": "MB-001", "DRY": "MB-002", "PER_VOLUME": "MB-005", "RETENTION_TR_OR_AR": "MB-007", "TRUE_RETENTION": "MB-007"}
_RET = {("USDA-RETN-R6", "RETENTION_TR_OR_AR"): ("RT-004", "SOURCE_STATES_MIXED_UNMARKED"), ("BOGNAR-2002", "TRUE_RETENTION"): ("RT-001", "NAMED_BY_SOURCE"),
        ("PHENOL-EXPLORER-3.6", None): ("RT-003", "SOURCE_DESCRIPTION_SECONDARY_SNIPPET_UNVERIFIED")}


def classify_basis(target_basis: str | None) -> dict:
    if target_basis in _BASIS:
        return {"basis_id": _BASIS[target_basis], "status": VALID, "raw": target_basis, "reasons": []}
    return {"basis_id": "MB-008", "status": UNKNOWN, "raw": target_basis, "reasons": [R_BASIS_MISSING]}


def classify_retention_type(source_family: str | None, target_basis: str | None, has_retention: bool) -> dict:
    if not has_retention:
        return {"retention_type_id": "RT-006", "status": VALID, "evidence": "row carries no retention value", "reasons": []}
    key = (source_family, target_basis)
    if key in _RET:
        return {"retention_type_id": _RET[key][0], "status": VALID if _RET[key][1] != "SOURCE_DESCRIPTION_SECONDARY_SNIPPET_UNVERIFIED" else AMBIGUOUS, "evidence": _RET[key][1], "reasons": [] if _RET[key][1] != "SOURCE_DESCRIPTION_SECONDARY_SNIPPET_UNVERIFIED" else ["RETENTION_TYPE_PENDING_PRIMARY_SOURCE_CHECK"]}
    if source_family == "PHENOL-EXPLORER-3.6":
        return {"retention_type_id": _RET[("PHENOL-EXPLORER-3.6", None)][0], "status": AMBIGUOUS, "evidence": _RET[("PHENOL-EXPLORER-3.6", None)][1], "reasons": ["RETENTION_TYPE_PENDING_PRIMARY_SOURCE_CHECK"]}
    return {"retention_type_id": "RT-005", "status": UNKNOWN, "evidence": "no source description", "reasons": ["RETENTION_BASIS_UNKNOWN"]}


def classify_censoring(qv: dict | None) -> dict:
    """UNKNOWN != NON_DETECT; NON_DETECT != 0. Only caps present in the ledger (GT_CAP) map to ABOVE_CAP."""
    if not qv or qv.get("status") in (None, "UNKNOWN", "ABSENT"):
        return {"censoring_id": "CS-007", "name": "NOT_REPORTED", "limit": None}
    cz = qv.get("censor") or {}
    kind = str(cz.get("kind", ""))
    if qv.get("status") == "CENSORED" or kind:
        if kind in ("GT_CAP", "GT_STATED"):
            return {"censoring_id": "CS-005", "name": "ABOVE_CAP", "limit": cz.get("limit")}
        if kind == "LT_LOD":
            return {"censoring_id": "CS-003", "name": "BELOW_LOD", "limit": cz.get("limit")}
        if kind == "LT_LOQ":
            return {"censoring_id": "CS-004", "name": "BELOW_LOQ", "limit": cz.get("limit")}
        if kind in ("ND", "NON_DETECT"):
            return {"censoring_id": "CS-002", "name": "NON_DETECT", "limit": cz.get("limit")}
        return {"censoring_id": "CS-006", "name": "CENSORED_UNKNOWN", "limit": cz.get("limit")}
    return {"censoring_id": "CS-001", "name": "DETECTED", "limit": None}


def classify_method(raw_text: str | None, meas_family: str | None = None) -> dict:
    t = (raw_text or "").lower()
    if t:
        with open(REG / "measurement_method_registry_v1.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if any(k and k in t for k in r["keywords_for_raw_text_matching"].split(";")):
                    return {"method_id": r["measurement_method_id"], "name": r["name"], "raw": raw_text}
        return {"method_id": "AM-010", "name": "OTHER", "raw": raw_text}
    if (meas_family or "").upper() == "CALCULATION":
        return {"method_id": "AM-009", "name": "CALCULATION", "raw": raw_text}
    return {"method_id": "AM-011", "name": "UNKNOWN", "raw": raw_text}


def can_combine_basis(a: str, b: str) -> tuple[bool, str]:
    """True only if both bases are identical and informative; wet/dry/volume/serving are never mixed; UNKNOWN/PER_MASS_UNSPECIFIED never combine."""
    if a != b:
        return False, "INCOMPATIBLE_BASES"
    if a in ("MB-004", "MB-008"):
        return False, "BASIS_NOT_INFORMATIVE"
    return True, ""


def can_combine_retention(a: str, b: str) -> tuple[bool, str]:
    if a in ("RT-005", "RT-004") or b in ("RT-005", "RT-004"):
        return False, "RETENTION_TYPE_UNDISCLOSED_OR_UNKNOWN"
    return (a == b, "" if a == b else "RETENTION_TYPES_DIFFER")
