"""AI/rule pre-check of imported primary-study EVD rows (Route A). Never human verification.

Checks per row (all transparent, each yields a flag string):
  values      before/after MEASURED, same unit
  rf_consistent  RF within the interval implied by the displayed (2-decimal-rounded) values × yield, ±5 %
  conditions  temperature/duration stated in the source text are present in COND
  ing_link    matrix linked to an internal ING
Suggested decision: LIKELY_CONFIRM (all core checks pass) | CHECK_VALUES | CHECK_CONDITIONS.
"""
from __future__ import annotations

import re

ROUND = 0.005
TEMP_TXT = re.compile(r"\d\s?°\s?C|\d\s?ºC|\bdegrees?\b", re.I)
DUR_TXT = re.compile(r"\d+(\.\d+)?\s?(min|minutes?|h|hours?|days?|weeks?|months?|years?|s|sec)\b", re.I)


def rf_interval(before: float, after: float, yf: float) -> tuple[float, float]:
    lo_b, hi_b = max(before - ROUND, 1e-9), before + ROUND
    lo_a, hi_a = max(after - ROUND, 0.0), after + ROUND
    return (lo_a / hi_b) * yf, (hi_a / lo_b) * yf


def check_row(e: dict, cond: dict | None) -> dict:
    b, a, d = e.get("before") or {}, e.get("after") or {}, e.get("derived") or {}
    flags, ok = [], {}
    ok["values"] = b.get("status") == a.get("status") == "MEASURED" and b.get("unit") == a.get("unit") \
        and bool(b.get("value"))
    if not ok["values"]:
        flags.append("before/after not both measured in one unit")
    rf = (d.get("retention_factor") or {}).get("value")
    yf = (d.get("yield_factor") or {}).get("value") or 1.0
    if ok["values"] and rf is not None:
        lo, hi = rf_interval(b["value"], a["value"], yf)
        ok["rf_consistent"] = lo * 0.95 <= rf <= hi * 1.05
        if not ok["rf_consistent"]:
            flags.append(f"RF {rf} outside [{lo:.3g}, {hi:.3g}] implied by values×yield — check paper")
    else:
        ok["rf_consistent"] = False
        flags.append("no RF or values to cross-check")
    txt = (e["process"].get("modifiers") or {}).get("food_after_raw") or ""
    mask = (cond or {}).get("completeness_mask") or {}
    need_t, need_d = bool(TEMP_TXT.search(txt)), bool(DUR_TXT.search(txt))
    has_t = mask.get("temperature") in ("MEASURED", "RANGE")
    has_d = mask.get("duration") in ("MEASURED", "RANGE")
    multi_d = not has_d and ";" in str(((cond or {}).get("duration") or {}).get("raw") or "")
    if multi_d:
        flags.append("several step durations kept in duration.raw; total UNKNOWN by design")
        has_d = True
    ok["conditions"] = (has_t or not need_t) and (has_d or not need_d)
    if not ok["conditions"]:
        flags.append("source text states temperature/duration not captured in COND")
    ok["ing_link"] = bool(e["matrix"].get("ingredient_id"))
    if not ok["ing_link"]:
        flags.append("matrix not linked to ING (see evd_ingredient_link_review.csv)")
    if ok["values"] and ok["rf_consistent"] and ok["conditions"]:
        suggestion = "LIKELY_CONFIRM"
    elif not (ok["values"] and ok["rf_consistent"]):
        suggestion = "CHECK_VALUES"
    else:
        suggestion = "CHECK_CONDITIONS"
    return {"ok": ok, "flags": flags, "suggestion": suggestion, "has_temperature": has_t, "has_duration": has_d}
