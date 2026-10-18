"""Extract explicit processing conditions from free text into QVALUE dicts.

Only numbers that are literally written are extracted. Nothing is inferred:
"medium heat" stays QUALITATIVE, and an oven/appliance temperature is never a core
temperature (location stays UNSPECIFIED unless the text says core/internal/surface).
"""
from __future__ import annotations

import re

_NUM = r"(\d+(?:[.,]\d+)?)"
_RANGE = rf"{_NUM}(?:\s*(?:-|–|to)\s*{_NUM})?"
DUR_RE = re.compile(rf"{_RANGE}\s*(seconds?|secs?|s|minutes?|mins?|min|hours?|hrs?|h|days?|d|weeks?|months?|years?)\b",
                    re.IGNORECASE)
# signed only when the minus is attached to the number and preceded by start/space/punctuation ("-20°C", "-18 to -20°C");
# "4-6°C" stays a 4..6 range
_SNUM = r"((?:(?<=[\s,(:;/])|^)[-−–]\s?\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"
TEMP_RE = re.compile(rf"{_SNUM}(?:\s*(?:-|–|to)\s*{_SNUM})?\s*(?:°|º|deg(?:rees?)?\.?\s*)\s*([CF])\b", re.IGNORECASE)
POWER_RE = re.compile(rf"{_RANGE}\s*(W|watts?|kW)\b", re.IGNORECASE)
PRESSURE_RE = re.compile(rf"{_RANGE}\s*(MPa|kPa|bar|atm|psi)\b", re.IGNORECASE)
QUAL_HEAT_RE = re.compile(r"\b(low|medium|moderate|high|gentle|full)[- ](?:high[- ])?(heat|flame|power|setting)\b",
                          re.IGNORECASE)
LOCATION_WORDS = (("core", "CORE"), ("internal", "CORE"), ("centre", "CORE"), ("center", "CORE"),
                  ("surface", "SURFACE"), ("oil", "MEDIUM"), ("water", "MEDIUM"), ("oven", "SETPOINT"))

_TO_MIN = {"s": 1 / 60, "sec": 1 / 60, "secs": 1 / 60, "second": 1 / 60, "seconds": 1 / 60, "min": 1, "mins": 1,
           "minute": 1, "minutes": 1, "h": 60, "hr": 60, "hrs": 60, "hour": 60, "hours": 60, "d": 1440,
           "day": 1440, "days": 1440, "week": 10080, "weeks": 10080,
           # convention: mean Gregorian month/year (30.436875 d / 365.2425 d); raw text always kept
           "month": 43829.1, "months": 43829.1, "year": 525949.2, "years": 525949.2}


def _f(x: str) -> float:
    return float(re.sub(r"[−–]\s?|-\s", "-", x).replace(",", "."))


def _qv(lo: float, hi: float | None, unit: str, raw: str) -> dict:
    if hi is None or hi == lo:
        return {"status": "MEASURED", "value": lo, "unit": unit, "raw": raw}
    lo, hi = min(lo, hi), max(lo, hi)
    return {"status": "RANGE", "low": lo, "high": hi, "unit": unit, "raw": raw}


def _location(text: str, start: int) -> str:
    window = text[max(0, start - 40):start].lower()
    for word, loc in LOCATION_WORDS:
        if re.search(rf"\b{word}\b", window):
            return loc
    return "UNSPECIFIED"


def extract_conditions(text: str) -> dict:
    """Return {"durations": [...], "temperatures": [...], "power": [...], "pressure": [...], "qualitative": [...]}."""
    out: dict = {"durations": [], "temperatures": [], "power": [], "pressure": [], "qualitative": []}
    if not text:
        return out
    for m in TEMP_RE.finditer(text):
        lo, hi = _f(m.group(1)), (_f(m.group(2)) if m.group(2) else None)
        unit = "degC" if m.group(3).upper() == "C" else "degF"
        out["temperatures"].append({"location": _location(text, m.start()),
                                    "value": _qv(lo, hi, unit, m.group(0))})
    for m in DUR_RE.finditer(text):
        k = _TO_MIN[m.group(3).lower()]
        lo = _f(m.group(1)) * k
        hi = _f(m.group(2)) * k if m.group(2) else None
        out["durations"].append(_qv(round(lo, 4), round(hi, 4) if hi is not None else None, "min", m.group(0)))
    for m in POWER_RE.finditer(text):
        k = 1000 if m.group(3).lower() == "kw" else 1
        out["power"].append(_qv(_f(m.group(1)) * k, _f(m.group(2)) * k if m.group(2) else None, "W", m.group(0)))
    for m in PRESSURE_RE.finditer(text):
        out["pressure"].append(_qv(_f(m.group(1)), _f(m.group(2)) if m.group(2) else None, m.group(3), m.group(0)))
    for m in QUAL_HEAT_RE.finditer(text):
        out["qualitative"].append({"status": "QUALITATIVE", "qualitative": m.group(0).lower(), "raw": m.group(0)})
    return out


def total_duration(durations: list[dict]) -> dict:
    """Single duration if exactly one is stated; several stated -> UNKNOWN (steps may overlap)."""
    if len(durations) == 1:
        return durations[0]
    return {"status": "UNKNOWN", "raw": "; ".join(d["raw"] for d in durations) or None}
