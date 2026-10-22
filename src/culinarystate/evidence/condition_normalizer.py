"""Step 07: deterministic condition and measurement normalisation.

Rules: nothing is inferred. Qualitative stays qualitative, UNKNOWN stays UNKNOWN, boiling is never 100 C, pH is never defaulted, moisture/aw/pressure/O2 absent is never 0,
ambiguous values keep their raw form and receive a reason code. Every call returns status VALID / INVALID / AMBIGUOUS / UNKNOWN with reason codes.
Registries: registry/condition_variable_registry_v1.csv etc. (stable ids authoritative; raw source strings always kept).
"""
from __future__ import annotations

import csv
import json
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
R_RANGE, R_REVERSED, R_NONFINITE = "PHYSICALLY_IMPOSSIBLE", "INTERVAL_REVERSED", "NON_FINITE_VALUE"
R_PRESSURE_REF, R_PERCENT_FRACTION, R_BASIS_MISSING, R_LOCATION_MISSING = "PRESSURE_REFERENCE_UNSPECIFIED", "PERCENT_OR_FRACTION_AMBIGUOUS", "MEASUREMENT_BASIS_MISSING", "MEASUREMENT_LOCATION_MISSING"
R_TRAJ_ORDER, R_TRAJ_SHORT, R_TEMP_HIGH, R_DELTA_ABS = "TRAJECTORY_TIME_NOT_INCREASING", "TRAJECTORY_NEEDS_2_POINTS", "OUTSIDE_TYPICAL_CULINARY_RANGE", "TEMPERATURE_DIFFERENCE_VS_ABSOLUTE"
R_BOILING = "BOILING_POINT_NOT_ASSUMED"

from . import condition_units as U
from . import source_dialect as D
from .condition_parser import parse_raw

_T, _P, _L, _W, _F, _RATIO, _PH, _DIMS = U.TIME, U.PRESSURE, U.LENGTH, U.POWER, U.FREQUENCY, U.RATIO, U.PH, U.DIMS  # back-compat aliases; tables live in condition_units.py
R_CALENDAR, R_PLAUS, R_UNIT_UNSUPPORTED = "CALENDAR_DURATION_NOT_CONVERTED", "OUTSIDE_TYPICAL_CULINARY_RANGE", "UNIT_CONVERSION_NOT_SUPPORTED"
R_CENSOR_LIMIT = "CENSORED_LIMIT_NOT_STATED"


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


def _load_bounds():
    out = {}
    with open(REG / "condition_variable_bounds_registry_v1.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["variable"]] = {k: (float(r[k]) if r[k] != "" else None) for k in ("hard_min", "hard_max", "plaus_min", "plaus_max")}
    return out


BOUNDS = _load_bounds()  # hard (physically impossible -> INVALID) and plausibility (warning -> AMBIGUOUS) bounds are separate, in canonical units
convert_temperature = U.convert_temperature
BOUND_OPS = {">": ("low", True), ">=": ("low", False), "<": ("high", True), "<=": ("high", False)}


def _nv(var, vt, status, reasons, raw, cv=None, cl=None, ch=None, unit_c=None, open_low=False, open_high=False, **kw):
    """numeric result: open flags are only meaningful on an existing endpoint (open_low <=> low endpoint excluded; open_high <=> high endpoint excluded)"""
    d = dict(canonical_value=cv, canonical_low=cl, canonical_high=ch, canonical_unit=unit_c, open_low=bool(open_low and cl is not None), open_high=bool(open_high and ch is not None))
    d.update(kw)
    return _result(var, vt, status, reasons, raw, **d)


def _bounds_check(var, vals, res, status, *, absolute=True):
    """-> (status, reasons) ; hard bound violation -> INVALID, plausibility violation -> AMBIGUOUS + OUTSIDE_TYPICAL_CULINARY_RANGE"""
    b = BOUNDS.get(var)
    if not b or not absolute:
        return status, res
    xs = [x for x in vals if x is not None]
    if any((b["hard_min"] is not None and x < b["hard_min"]) or (b["hard_max"] is not None and x > b["hard_max"]) for x in xs):
        return INVALID, res + [R_RANGE]
    if any((b["plaus_min"] is not None and x < b["plaus_min"]) or (b["plaus_max"] is not None and x > b["plaus_max"]) for x in xs):
        return (AMBIGUOUS if status == VALID else status), res + [R_PLAUS]
    return status, res


def _uncertainty(var, dim, unit, unc, kind="absolute"):
    """measurement uncertainty is kept SEPARATE from the range; magnitude converted with the same factor (temperature: difference scaling)"""
    if not unc:
        return None
    u = unc.get("unit_text") or unit
    out = {"value": unc["value"], "unit": u, "type": unc.get("type") or "UNKNOWN", "canonical_value": None, "canonical_unit": None}
    try:
        if dim == "temperature":
            out["canonical_value"], out["canonical_unit"] = convert_temperature(unc["value"], u, "difference"), "K"
        elif dim in U.DIMS and u and (u.strip().lower() in U.DIMS[dim][1]):
            out["canonical_value"], out["canonical_unit"] = unc["value"] * U.DIMS[dim][1][u.strip().lower()], U.DIMS[dim][0]
    except ValueError:
        pass
    return out


def normalize_value(var: str, *, value=None, low=None, high=None, unit=None, raw=None, qualitative=None, trajectory=None, location=None, basis=None, kind="absolute",
                    open_low=False, open_high=False, pressure_reference=None, sourced_mapping=None, approximate=False, uncertainty=None, time_unit=None, censor_kind=None) -> dict:
    """Return a normalised condition value. Never fills absent values. `basis` in {'WET','DRY'} for moisture.
    Interval endpoints: `open_low=True` excludes `low` (> x), `open_high=True` excludes `high` (< x); `>= x`/`<= x` are closed. `uncertainty` = {value, unit_text, type}.
    `trajectory` = list of {time, time_unit, value, unit[, location, uncertainty]} (or (t, v) pairs with `time_unit` and `unit` given); every point is normalised here."""
    res = _normalize_core(var, value=value, low=low, high=high, unit=unit, raw=raw, qualitative=qualitative, trajectory=trajectory, location=location, basis=basis, kind=kind, open_low=open_low,
                          open_high=open_high, pressure_reference=pressure_reference, sourced_mapping=sourced_mapping, uncertainty=uncertainty, time_unit=time_unit, censor_kind=censor_kind)
    if approximate and res["value_type"] in ("POINT", "INTERVAL"):
        res["approximate"] = True
    return res


def _normalize_core(var, *, value, low, high, unit, raw, qualitative, trajectory, location, basis, kind, open_low, open_high, pressure_reference, sourced_mapping, uncertainty, time_unit, censor_kind) -> dict:
    if var not in VARS:
        return _result(var, "UNKNOWN", INVALID, [R_UNKNOWN_VAR], raw)
    meta = VARS[var]
    res = []
    dim = meta["dimension"]
    if qualitative is not None and value is None and low is None and high is None and trajectory is None:
        if sourced_mapping and qualitative in sourced_mapping:
            m = sourced_mapping[qualitative]
            return _result(var, "POINT", VALID, ["NUMERIC_FROM_EXPLICIT_SOURCED_MAPPING"], raw or qualitative, qualitative=qualitative, mapping_source=m.get("source"), canonical_value=m["value"], canonical_unit=meta["canonical_unit"])
        reasons = [R_QUALITATIVE, R_NO_NUMERIC_MAPPING]
        if re.search(r"\bboil", str(qualitative), re.I) and dim == "temperature":
            reasons.append(R_BOILING)
        return _result(var, "QUALITATIVE", VALID, reasons, raw or qualitative, qualitative=qualitative)
    if trajectory is not None:
        return _normalize_trajectory(var, trajectory, raw=raw, location=location, unit=unit, time_unit=time_unit, basis=basis)
    if value is None and low is None and high is None:
        if censor_kind:
            return _result(var, "UNKNOWN", UNKNOWN, [R_CENSOR_LIMIT], raw, censoring={"kind": censor_kind, "limit": None})
        return _result(var, "UNKNOWN", UNKNOWN, [R_NOT_STATED], raw)
    vals = [x for x in (value, low, high) if x is not None]
    if any((isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)) for x in vals):
        return _result(var, "UNKNOWN", INVALID, [R_NONFINITE], raw)
    is_interval = value is None and (low is not None or high is not None)
    if is_interval and low is not None and high is not None and low > high:
        return _result(var, "INTERVAL", INVALID, [R_REVERSED], raw)
    vt = "INTERVAL" if is_interval else "POINT"
    status, canon_u = VALID, meta["canonical_unit"]
    extra = {"censoring": {"kind": censor_kind, "limit": (low if low is not None else high)}} if censor_kind else {}
    if open_low or open_high:
        extra["bound_semantics"] = "OPEN_ENDS_EXCLUDE_THE_STATED_LIMIT"
    if uncertainty and uncertainty.get("value", 0) < 0:
        return _result(var, vt, INVALID, ["UNCERTAINTY_NEGATIVE"], raw)
    # ---- temperature ----
    if dim in ("temperature", "temperature_rate"):
        if not unit:
            return _result(var, vt, AMBIGUOUS, [R_UNIT_MISSING], raw, low=low, high=high, value=value)
        try:
            if dim == "temperature":
                conv = lambda x: None if x is None else convert_temperature(x, unit, kind)
                if kind != "difference" and meta["absolute_or_difference"] == "difference":
                    res.append(R_DELTA_ABS)
                    status = AMBIGUOUS
            else:
                m = re.match(r"^(k|degc|degf)\s*/\s*(s|min|h)$", unit.strip().lower().replace("°", "deg"))
                if not m:
                    return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw)
                conv = lambda x: None if x is None else convert_temperature(x, m.group(1), "difference") / U.TIME[m.group(2)]
            cv, cl, ch = conv(value), conv(low), conv(high)  # evaluated inside the try: an unknown unit token raises here
        except ValueError:
            return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw)
        status, res = _bounds_check(var, (cv, cl, ch), res, status, absolute=(dim == "temperature" and kind != "difference"))
        if var == "temp_unspecified":
            res.append(R_LOCATION_MISSING)
            status = AMBIGUOUS if status == VALID else status
        return _nv(var, vt, status, res, raw, cv, cl, ch, canon_u, open_low, open_high, location=location, temperature_kind=kind if dim == "temperature" else "rate",
                   uncertainty=_uncertainty(var, dim, unit, uncertainty, kind), **extra)
    # ---- time (calendar durations are never converted) ----
    if dim == "time":
        tk, tf = U.time_factor(unit)
        if not unit:
            return _result(var, vt, AMBIGUOUS, [R_UNIT_MISSING], raw, value=value, low=low, high=high)
        if tk == "CALENDAR":
            return _nv(var, vt, AMBIGUOUS, [R_CALENDAR], raw, unit_c=canon_u, calendar_value=value, calendar_low=low, calendar_high=high, calendar_unit=U.calendar_unit(unit), open_low=open_low, open_high=open_high, **extra)
        if tk == "UNSUPPORTED":
            return _result(var, vt, INVALID if unit and unit.strip().lower() not in meta["allowed_units"].lower().split(";") else AMBIGUOUS, [R_UNIT_UNKNOWN], raw, unit=unit)
        cv, cl, ch = (None if x is None else x * tf for x in (value, low, high))
        status, res = _bounds_check(var, (cv, cl, ch), res, status)
        return _nv(var, vt, status, res, raw, cv, cl, ch, canon_u, open_low, open_high, uncertainty=_uncertainty(var, dim, unit, uncertainty), **extra)
    # ---- pressure ----
    if dim == "pressure":
        if not (unit or "").strip():
            return _result(var, vt, AMBIGUOUS, [R_UNIT_MISSING], raw, value=value, low=low, high=high)
        base, ref = U.split_pressure_unit(unit)
        ref = ref or pressure_reference
        f = U.PRESSURE.get(base.lower())
        if f is None:
            return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw)
        if ref is None or ref == "UNSPECIFIED":
            res.append(R_PRESSURE_REF)
            status, ref = AMBIGUOUS, "UNSPECIFIED"
        cv, cl, ch = (None if x is None else x * f for x in (value, low, high))
        if any(x is not None and x < 0 for x in (cv, cl, ch)):
            if ref == "ABSOLUTE":
                return _result(var, vt, INVALID, [R_RANGE], raw)
            if ref == "UNSPECIFIED":
                res.append("NEGATIVE_PRESSURE_REQUIRES_GAUGE_OR_DIFFERENTIAL")
        return _nv(var, vt, status, res, raw, cv, cl, ch, "Pa", open_low, open_high, pressure_reference=ref, uncertainty=_uncertainty(var, dim, base, uncertainty), **extra)
    # ---- generic dimensions ----
    if dim not in U.DIMS:
        return _result(var, vt, AMBIGUOUS, ["NO_UNIT_TABLE_FOR_VARIABLE"], raw, value=value, low=low, high=high, unit=unit)
    canon_unit, table = U.DIMS[dim]
    key = (unit or "").strip().lower()
    if var == "ph":
        key = "ph"
    if not key:
        return _result(var, vt, AMBIGUOUS, ([R_PERCENT_FRACTION] if dim in ("mass_fraction", "ratio", "volume_fraction", "dimensionless") else []) + [R_UNIT_MISSING], raw, value=value, low=low, high=high)
    factor = table.get(key)
    if var == "water_activity":
        factor = 1.0
    if factor is None:
        allowed = [a.strip().lower() for a in meta["allowed_units"].split(";")]
        if key in allowed:
            return _result(var, vt, AMBIGUOUS, [R_UNIT_UNSUPPORTED], raw, unit=unit, value=value, low=low, high=high)
        return _result(var, vt, INVALID, [R_UNIT_UNKNOWN], raw, unit=unit)
    cv, cl, ch = (None if x is None else x * factor for x in (value, low, high))
    chk = (cv, cl, ch)
    status, res = _bounds_check(var, chk, res, status)
    if var == "moisture_content":
        if basis not in ("WET", "DRY"):
            return _nv(var, vt, AMBIGUOUS if status != INVALID else status, res + [R_BASIS_MISSING], raw, cv, cl, ch, canon_unit, open_low, open_high)
        if basis == "WET" and any(x is not None and x > 1 for x in chk):
            return _result(var, vt, INVALID, [R_RANGE], raw)
    return _nv(var, vt, status, res, raw, cv, cl, ch, canon_unit, open_low, open_high, basis=basis, uncertainty=_uncertainty(var, dim, unit, uncertainty), **extra)


def _normalize_trajectory(var, traj, *, raw, location, unit, time_unit, basis) -> dict:
    meta = VARS[var]
    pts_in = []
    for p in traj:
        if isinstance(p, dict):
            pts_in.append(p)
        elif isinstance(p, (tuple, list)) and len(p) == 2:
            pts_in.append({"time": p[0], "time_unit": time_unit, "value": p[1], "unit": unit})
        else:
            return _result(var, "TRAJECTORY", INVALID, ["TRAJECTORY_POINT_MALFORMED"], raw)
    if len(pts_in) < 2:
        return _result(var, "TRAJECTORY", INVALID, [R_TRAJ_SHORT], raw)
    pts, reasons, status = [], [], VALID
    for p in pts_in:
        t = normalize_value("time_trajectory", value=p.get("time"), unit=p.get("time_unit"), raw=p.get("time"))
        loc = p.get("location") or location
        v = normalize_value(var, value=p.get("value"), unit=p.get("unit"), raw=p.get("value"), location=loc, basis=basis, uncertainty=p.get("uncertainty"))
        prs = list(dict.fromkeys(t["reasons"] + v["reasons"]))
        pts.append({"raw_time": p.get("time"), "raw_time_unit": p.get("time_unit"), "canonical_time": t.get("canonical_value"), "raw_value": p.get("value"), "raw_value_unit": p.get("unit"),
                    "canonical_value": v.get("canonical_value"), "location": loc, "uncertainty": v.get("uncertainty"), "status": INVALID if INVALID in (t["status"], v["status"]) else AMBIGUOUS if AMBIGUOUS in (t["status"], v["status"]) or UNKNOWN in (t["status"], v["status"]) else VALID,
                    "reasons": prs})
    if any(q["status"] == INVALID for q in pts):
        status, reasons = INVALID, ["TRAJECTORY_POINT_INVALID"]
    else:
        ts = [q["canonical_time"] for q in pts]
        if all(x is not None for x in ts):
            if any(b <= a for a, b in zip(ts, ts[1:])):
                return _result(var, "TRAJECTORY", INVALID, [R_TRAJ_ORDER], raw, points=pts)
        else:
            status, reasons = AMBIGUOUS, ["TRAJECTORY_TIME_AXIS_NOT_COMMON"]
        if any(q["status"] != VALID for q in pts):
            status, reasons = AMBIGUOUS, reasons + ["TRAJECTORY_POINT_AMBIGUOUS"]
    if meta["dimension"] == "temperature" and any((q["location"] or "UNSPECIFIED").upper() == "UNSPECIFIED" for q in pts) and status != INVALID:
        status, reasons = AMBIGUOUS, reasons + [R_LOCATION_MISSING]
    return _result(var, "TRAJECTORY", status, reasons, raw, points=pts, location=location, canonical_unit=meta["canonical_unit"], canonical_time_unit="s")


# ---------- adapter for the repo QVALUE dicts (COND ledger) ----------


R_RAW_UNPARSED, R_MULTI_SAME_LOC = "RAW_TEXT_PRESENT_BUT_NOT_PARSED", "MULTIPLE_VALUES_SAME_LOCATION"
R_SLASH, R_SPACED_DASH = "SLASH_NOTATION_RANGE_OR_ALTERNATIVES", "SPACED_DASH_SIGN_OR_RANGE_FRAGMENT"  # kept for importers; rules live in registry/notation_rule_registry_v1.csv


def _load_notation_rules():
    """Executable notation rules (action FLAG / QUALIFY / SPLIT) from the data-derived registry; INFO rows are documentation only."""
    out = []
    with open(REG / "notation_rule_registry_v1.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["action"] in ("FLAG", "QUALIFY", "SPLIT"):
                r["_rx"] = re.compile(r["pattern"], re.I)
                out.append(r)
    return out


NOTATION_RULES = _load_notation_rules()
_COMPONENT = re.compile(r"(\d+(?:[.,]\d+)?)\s*([A-Za-z]+)")


def _split_components(var: str, raw: str) -> list[dict]:
    """';'-separated list -> one normalised component per part (roles unknown); a part without number+unit stays raw-unparsed."""
    comps = []
    for part in str(raw).split(";"):
        m = _COMPONENT.search(part)
        if m:
            comps.append(normalize_value(var, value=float(m.group(1).replace(",", ".")), unit=m.group(2).lower(), raw=part.strip()))
        else:
            comps.append(_result(var, "UNKNOWN", AMBIGUOUS, [R_RAW_UNPARSED], part.strip()))
    return comps


def _flag(res: dict, code: str) -> dict:
    res["reasons"] = list(dict.fromkeys(res["reasons"] + [code]))
    if res["status"] in (VALID, UNKNOWN):
        res["status"] = AMBIGUOUS
    return res


_CAL_RAW = re.compile(r"(\d+(?:[.,]\d+)?)\s*(months?|years?|yrs?)\b", re.I)


def _field_of(var: str) -> str:
    return "duration" if var.startswith("time_") else "temperature" if var.startswith("temp_") else "pressure" if var == "pressure" else "power" if "power" in var else var


def from_qvalue(var: str, qv: dict | None, *, location: str | None = None, source_family: str | None = None, **kw) -> dict:
    """Adapter with raw-text guards (Step 07 fix): a value is never reported as NOT_STATED when raw text exists; slash notation and spaced dashes are flagged, never silently read."""
    res = _from_qvalue(var, qv, location=location, **kw)
    raw = (qv or {}).get("raw")
    if raw and res["value_type"] == "UNKNOWN" and res["reasons"] == [R_NOT_STATED]:
        res["reasons"] = [R_RAW_UNPARSED]
        res["status"] = AMBIGUOUS
        res["raw"] = raw
    if raw and VARS.get(var, {}).get("dimension") == "time" and res["value_type"] == "POINT" and res.get("canonical_unit") == "s":
        cm = _CAL_RAW.search(str(raw))
        if cm and not res.get("calendar_unit"):  # the ledger stored a fixed-seconds value for a calendar duration at ingest: no fake precision
            unit = U.calendar_unit(cm.group(2))
            res = _result(var, "POINT", AMBIGUOUS, [R_CALENDAR, "CALENDAR_DURATION_CONVERTED_AT_SOURCE_INGEST"], raw, calendar_value=float(cm.group(1).replace(",", ".")), calendar_unit=unit, canonical_value=None, canonical_low=None, canonical_high=None,
                          canonical_unit=res.get("canonical_unit"), open_low=False, open_high=False)
    for rule in NOTATION_RULES:
        if not raw or rule["field"] not in ("any", _field_of(var)) or not rule["_rx"].search(str(raw)):
            continue
        if rule["requires_value_type"] and res["value_type"] != rule["requires_value_type"]:
            continue
        if rule["var_prefix"] and not var.startswith(rule["var_prefix"]):
            continue
        if rule["action"] == "FLAG":
            _flag(res, rule["reason_code"])
        elif rule["action"] == "QUALIFY":
            res["approximate"] = True
        elif rule["action"] == "SPLIT":
            res["components"] = _split_components(var, raw)
            _flag(res, rule["reason_code"])
    ab = D.annotate_abbreviations(raw, source_family) if source_family else []
    if ab:
        res["dialect_notes"] = ab  # annotation only: unresolved source abbreviations never change a value or status
    return res


def normalize_temperatures(temps: list[dict]) -> list[dict]:
    """Normalise a COND `temperatures` list; repeated values at one location are flagged (could be a split range or alternatives)."""
    out = []
    seen: dict[str, int] = {}
    for t in temps or []:
        loc = (t.get("location") or "UNSPECIFIED").upper()
        seen[loc] = seen.get(loc, 0) + 1
    for t in temps or []:
        loc = (t.get("location") or "UNSPECIFIED").upper()
        r = from_qvalue(temperature_variable_for(loc), t.get("value"), location=loc)
        if seen[loc] > 1:
            _flag(r, R_MULTI_SAME_LOC)
        out.append(r)
    return out


def _from_qvalue(var: str, qv: dict | None, *, location: str | None = None, **kw) -> dict:
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
        op = CENSOR_KIND_OP.get(kind)
        if op is None:
            return _result(var, "UNKNOWN", AMBIGUOUS, [f"UNRECOGNISED_CENSOR_KIND:{kind or 'NONE'}"], raw, censoring={"kind": kind or None, "limit": lim})
        if lim is None:
            return normalize_value(var, raw=raw, censor_kind=kind, **kw)
        return normalize_bound(var, op, lim, unit=unit, raw=raw, location=location, censor_kind=kind, **kw)
    if st == "QUALITATIVE":
        return normalize_value(var, qualitative=qv.get("qualitative") or raw, raw=raw, **kw)
    return _result(var, "UNKNOWN", AMBIGUOUS, [f"UNRECOGNISED_QVALUE_STATUS:{st}"], raw)


CENSOR_KIND_OP = {"GT_STATED": ">", "GT": ">", "GE_STATED": ">=", "GE": ">=", "GT_CAP": "CAP", "ABOVE_CAP": "CAP", "LT_STATED": "<", "LT": "<", "LE_STATED": "<=", "LE": "<=",
                  "LT_LOD": "<", "LT_LOQ": "<", "BELOW_LOD": "<", "BELOW_LOQ": "<", "ND": "<", "NON_DETECT": "<"}


def normalize_bound(var: str, op: str, limit: float, **kw) -> dict:
    """`> x` -> (x, +inf): low=x, open_low=True ; `>= x` closed ; `< x` -> (-inf, x): high=x, open_high=True ; `<= x` closed. CAP (right-censored at a cap) -> [cap, +inf)."""
    if op == "CAP":
        return normalize_value(var, low=limit, open_low=False, **kw)
    side, strict = BOUND_OPS[op]
    return normalize_value(var, **{side: limit, "open_" + side: strict}, **kw)


def temperature_variable_for(location: str | None) -> str:
    m = D.lookup("temperature_location", (location or "UNSPECIFIED").upper())
    return m["canonical_target"] if m else "temp_unspecified"


# ---------- measurement fields ----------
def classify_basis(target_basis: str | None) -> dict:
    m = D.lookup("basis", target_basis)
    if m and m["status"] == "VERIFIED":
        return {"basis_id": m["canonical_target"], "status": VALID, "raw": target_basis, "reasons": [], "mapping_id": m["mapping_id"]}
    return {"basis_id": "MB-008", "status": UNKNOWN, "raw": target_basis, "reasons": [R_BASIS_MISSING]}


def classify_retention_type(source_family: str | None, target_basis: str | None, has_retention: bool) -> dict:
    if not has_retention:
        return {"retention_type_id": "RT-006", "status": VALID, "evidence": "row carries no retention value", "reasons": []}
    m = D.lookup("retention_type", target_basis, source_family)
    if m and m["source_family"] != "*":
        ok = m["status"] == "VERIFIED"
        return {"retention_type_id": m["canonical_target"], "status": VALID if ok else AMBIGUOUS, "evidence": m["evidence"].split(";")[0], "mapping_id": m["mapping_id"], "reasons": [] if ok else ["RETENTION_TYPE_PENDING_PRIMARY_SOURCE_CHECK"]}
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


# ---------- raw text -> parser (D1) -> semantic normalizer (D2) ----------
_AMB_CODES = {"SPACED_DASH_SIGN_OR_RANGE_FRAGMENT": R_SPACED_DASH, "SLASH_NOTATION_RANGE_OR_ALTERNATIVES": R_SLASH, "DECIMAL_COMMA_OR_THOUSANDS": "DECIMAL_COMMA_OR_THOUSANDS", "RANGE_UNIT_CONFLICT": "RANGE_UNIT_CONFLICT",
              "UNCERTAINTY_UNIT_CONFLICT": "UNCERTAINTY_UNIT_CONFLICT", "OPERATOR_WITH_RANGE": "OPERATOR_WITH_RANGE"}
_LABEL_UNIT = {"ph": "pH", "water_activity": "aw"}


def normalize_text(var: str, raw, *, location=None, basis=None, kind="absolute", pressure_reference=None, sourced_mapping=None) -> dict:
    """Parse raw text (syntax only) then normalise semantically. Anything the parser cannot type stays UNKNOWN/AMBIGUOUS with the raw text; nothing is guessed."""
    p = parse_raw(raw)
    k = p["kind"]
    if k == "NOT_REPORTED":
        return normalize_value(var, raw=raw)
    if k == "CENSOR_TOKEN":
        return normalize_value(var, raw=raw, censor_kind=p["censor_kind"])
    if k == "QUALITATIVE":
        return normalize_value(var, qualitative=p["qualitative"], raw=raw, sourced_mapping=sourced_mapping)
    if k == "UNPARSED":
        r = _result(var, "UNKNOWN", AMBIGUOUS, [R_RAW_UNPARSED], raw, residual=p["residual"])
        for a in p["ambiguities"]:
            _flag(r, _AMB_CODES.get(a, a))
        return r
    if k == "LIST":
        r = _result(var, "UNKNOWN", AMBIGUOUS, ["MULTI_VALUE_LIST_ROLES_UNKNOWN"], raw, components=[normalize_text(var, q["raw"], location=location, basis=basis, kind=kind, pressure_reference=pressure_reference) for q in p["parts"]])
        return r
    if k == "COMPOUND":
        return _normalize_compound(var, raw, p["parts"])
    if p["unit_text"] and p["unit_text"].strip().lower() in ("degrees", "degree", "deg", "degs", "\u00b0") and VARS.get(var, {}).get("dimension") == "temperature":
        p = dict(p, unit_text=None, _scale_missing=True)  # scale not stated -> AMBIGUOUS (TEMPERATURE_SCALE_NOT_STATED), never INVALID
    unit = p["unit_text"] or (_LABEL_UNIT.get(p["variable_hint"]) if p["variable_hint"] == var else None)
    bs = basis or p["basis_hint"]
    kw = dict(unit=unit, raw=raw, location=location, basis=bs, kind=kind, pressure_reference=p["pressure_reference"] or pressure_reference, approximate=p["approximate"], uncertainty=p["uncertainty"])
    if k == "NUMBER":
        r = normalize_value(var, value=p["value"], **kw)
    elif k in ("RANGE", "SLASH_PAIR"):
        r = normalize_value(var, low=p["low"], high=p["high"], **kw)
    else:  # BOUND
        r = normalize_bound(var, p["op"], p["low"] if p["low"] is not None else p["high"], censor_kind=p["censor_kind"], **kw)
    if p.get("_scale_missing"):
        r["reasons"] = ["TEMPERATURE_SCALE_NOT_STATED" if x == R_UNIT_MISSING else x for x in r["reasons"]]
    for a in p["ambiguities"]:
        _flag(r, _AMB_CODES.get(a, a))
    if p["variable_hint"] and p["variable_hint"] != var:
        _flag(r, "VARIABLE_HINT_MISMATCH")
    if basis and p["basis_hint"] and basis != p["basis_hint"]:
        _flag(r, "BASIS_CONFLICT")
    return r


def _normalize_compound(var: str, raw, parts) -> dict:
    """'1 hr 30 mins' -> sum of fixed-length parts in seconds (time variables only). A calendar part (month/year) or a non-time unit -> AMBIGUOUS, no sum."""
    if VARS.get(var, {}).get("dimension") != "time":
        return _result(var, "UNKNOWN", AMBIGUOUS, ["COMPOUND_AMOUNT_NOT_SUPPORTED_FOR_VARIABLE"], raw, components=[])
    total = 0.0
    for q in parts:
        kind, f = U.time_factor(q["unit_text"])
        if kind != "FIXED":
            return _result(var, "UNKNOWN", AMBIGUOUS, [R_CALENDAR if kind == "CALENDAR" else R_UNIT_UNKNOWN], raw, residual=str(raw))
        total += q["value"] * f
    r = normalize_value(var, value=total, unit="s", raw=raw)
    r["reasons"] = list(dict.fromkeys(r["reasons"] + ["COMPOUND_DURATION_SUMMED"]))
    return r


# ---------- reproducibility: version + hashes ----------
NORMALIZER_VERSION = "condition_normalizer@2.0.0-07H"
_CODE = ("condition_normalizer.py", "condition_parser.py", "condition_units.py", "source_dialect.py")
_REGISTRIES = ("condition_variable_registry_v1.csv", "condition_variable_bounds_registry_v1.csv", "notation_rule_registry_v1.csv", "source_dialect_mapping_registry_v1.csv", "measurement_basis_registry_v1.csv",
               "measurement_location_registry_v1.csv", "measurement_method_registry_v1.csv", "censoring_registry_v1.csv", "retention_type_registry_v1.csv", "value_type_registry_v1.csv", "quantity_form_registry_v1.csv",
               "value_origin_registry_v1.csv", "heat_transfer_mode_registry_v1.csv")


def fingerprint() -> dict:
    """exact code, schema and registry hashes + one combined hash; recorded in every human-audit packet and regression report"""
    import hashlib

    def h(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    here = Path(__file__).resolve().parent
    code = {n: h(here / n) for n in _CODE}
    schema = h(REG / "schemas" / "condition_value_v1.schema.json")
    regs = {n: h(REG / n) for n in _REGISTRIES}
    combined = hashlib.sha256(json.dumps([NORMALIZER_VERSION, code, schema, regs], sort_keys=True).encode()).hexdigest()
    return {"normalizer_version": NORMALIZER_VERSION, "code_sha256": code, "schema_sha256": schema, "registry_sha256": regs, "combined_sha256": combined}
