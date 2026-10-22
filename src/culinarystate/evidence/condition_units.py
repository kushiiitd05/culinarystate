"""Step 07H: centralised unit tables for the condition normalizer (one place, every entry tested in tests/unit/test_condition_units.py).

Scope (v1): exact factors for ordinary dimensions; NO dimensional-analysis engine. Pint was considered and not adopted: it would add a dependency for ~40 unit
factors, and all semantic distinctions (gauge/absolute, basis, pH, aw, censoring, location) must stay in project code anyway.
Unsupported units are reported as UNSUPPORTED (never guessed). Calendar durations (month, year) are NOT convertible to seconds: no fixed day count is defined.
"""
from __future__ import annotations

import re

# --- time: only fixed-length units. day = 86400 s (civil day; DST/leap seconds ignored); week = 7 d.
TIME = {"s": 1.0, "sec": 1.0, "secs": 1.0, "second": 1.0, "seconds": 1.0, "min": 60.0, "mins": 60.0, "minute": 60.0, "minutes": 60.0, "h": 3600.0, "hr": 3600.0, "hrs": 3600.0, "hour": 3600.0, "hours": 3600.0,
        "d": 86400.0, "day": 86400.0, "days": 86400.0, "week": 604800.0, "weeks": 604800.0}
CALENDAR = {"month": "month", "months": "month", "year": "year", "years": "year", "yr": "year", "yrs": "year"}  # kept as calendar durations, never seconds

# --- pressure (to Pa). psi = lbf/in^2 exactly; torr = atm/760 exactly; mmHg = conventional 133.322387415.
PRESSURE = {"pa": 1.0, "hpa": 100.0, "kpa": 1e3, "mpa": 1e6, "bar": 1e5, "mbar": 100.0, "atm": 101325.0, "psi": 0.45359237 * 9.80665 / (0.0254 ** 2), "mmhg": 133.322387415, "torr": 101325.0 / 760.0}
LENGTH = {"um": 1e-6, "mm": 1e-3, "cm": 1e-2, "m": 1.0, "inch": 0.0254, "inches": 0.0254, '"': 0.0254}  # bare "in" is not accepted (ambiguous with the preposition)
POWER = {"w": 1.0, "watt": 1.0, "watts": 1.0, "kw": 1e3, "kilowatt": 1e3, "kilowatts": 1e3}
FREQUENCY = {"hz": 1.0, "mhz": 1e6, "ghz": 1e9}
RATIO = {"percent": 0.01, "%": 0.01, "fraction": 1.0, "g/100g": 0.01, "aw": 1.0}
PH = {"ph": 1.0}
DIMS = {"time": ("s", TIME), "pressure": ("Pa", PRESSURE), "length": ("m", LENGTH), "power": ("W", POWER), "frequency": ("Hz", FREQUENCY), "mass_fraction": ("fraction", RATIO), "ratio": ("fraction", RATIO),
        "dimensionless": ("as stated", RATIO | PH), "volume_fraction": ("fraction", RATIO)}

_TEMP_ALIASES = {"c": "degc", "celsius": "degc", "centigrade": "degc", "f": "degf", "fahrenheit": "degf", "k": "k", "kelvin": "k"}


def temperature_unit(unit: str) -> str | None:
    """canonical token degc / degf / k, else None. Accepts °C, ºC, 'deg C', 'degrees Fahrenheit', 'C', 'K', 'celsius'. A bare degree sign / 'degrees' carries NO scale -> None."""
    u = re.sub(r"\s+", "", str(unit).strip().lower())
    u = re.sub(r"^(?:degrees|degree|degs|deg|\u00b0|\u00ba)", "", u)
    return _TEMP_ALIASES.get(u)


def convert_temperature(value: float, unit: str, kind: str = "absolute") -> float:
    """-> Kelvin (absolute) or kelvin-difference. Differences are scaled, never offset."""
    u = temperature_unit(unit)
    if u is None:
        raise ValueError(f"unknown temperature unit {unit!r}")
    if kind == "difference":
        return value * (5.0 / 9.0 if u == "degf" else 1.0)
    return {"degc": value + 273.15, "degf": (value - 32.0) * 5.0 / 9.0 + 273.15, "k": value}[u]


_PREF = re.compile(r"^(pa|hpa|kpa|mpa|bar|mbar|atm|psi|mmhg|torr)\s*[\(\[]?\s*(a|abs|absolute|g|gauge|ga|d|diff|differential)?[\)\]]?$", re.I)
_PREF_SUFFIX = re.compile(r"^(psi|bar|kpa|mpa|pa)(a|g|d)$", re.I)
_REF = {"a": "ABSOLUTE", "g": "GAUGE", "d": "DIFFERENTIAL"}


def split_pressure_unit(unit: str) -> tuple[str, str | None]:
    """'psig' -> ('psi','GAUGE'); 'kPa(a)' -> ('kPa','ABSOLUTE'); 'bar' -> ('bar', None). The reference is read only when the unit text states it."""
    u = (unit or "").strip()
    sm = _PREF_SUFFIX.match(u)
    if sm:
        return sm.group(1), _REF[sm.group(2).lower()]
    mm = _PREF.match(u)
    if mm:
        return mm.group(1), (_REF[mm.group(2).lower()[0]] if mm.group(2) else None)
    return u, None


def time_factor(unit: str | None) -> tuple[str, float | None]:
    """-> ('FIXED', seconds) | ('CALENDAR', None) | ('UNSUPPORTED', None)"""
    k = (unit or "").strip().lower()
    if k in TIME:
        return "FIXED", TIME[k]
    if k in CALENDAR:
        return "CALENDAR", None
    return "UNSUPPORTED", None


def calendar_unit(unit: str | None) -> str | None:
    return CALENDAR.get((unit or "").strip().lower())
