"""Versioned, conservative table-report renderer; old generation/scoring stays frozen.

Ranking compatibility is never an applicability grant. Only exact explicit source
context permits a table-point report, always EVD_REPORTED_UNVERIFIED. Arbitrary
generated prose and fallback text cannot expand the canonical authorization set.
This module supplies no scientific validation, model output or SIMULATE route.
"""
from __future__ import annotations

import math
import re
from collections.abc import Mapping

VERSION = "strict-emission-v2.0.0"
REFUSAL = "I cannot give a numeric result for those conditions from the available evidence."
UNKNOWN = {"", "UNKNOWN", "UNSPECIFIED", "NOT_REPORTED", "NOT_REPORTED_BY_SOURCE", "NOT_APPLICABLE"}


def _obj(value):
    return value if isinstance(value, Mapping) else {}


def _known(value):
    return isinstance(value, str) and value.strip().upper() not in UNKNOWN


def _number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def _pair(value):
    if not isinstance(value, (tuple, list)) or len(value) != 2 or not all(_number(x) for x in value):
        return None
    return tuple(value) if value[0] <= value[1] else None


def _bounds(value, unit):
    value = _obj(value)
    if value.get("unit") != unit:
        return None
    if value.get("status") == "MEASURED" and _number(value.get("value")):
        return value["value"], value["value"]
    if value.get("status") == "RANGE":
        return _pair((value.get("low"), value.get("high")))
    return None


def _retention(row):
    point = _obj(_obj(row.get("derived")).get("retention_factor"))
    if point.get("status") != "MEASURED" or not _number(point.get("value")) or point["value"] < 0:
        return None
    if point.get("unit") not in ("fraction", "1", "%"):
        return None
    return point["value"] * (.01 if point["unit"] == "%" else 1.)


def row_reasons(row, condition, context):
    """Exact declared-field checks, not scientific applicability or source verification."""
    row, condition, context = _obj(row), _obj(condition), _obj(context)
    matrix, process, target = (_obj(row.get(k)) for k in ("matrix", "process", "target"))
    reasons = []
    if row.get("status") != "ACTIVE" or not re.fullmatch(r"EVD-\d{6}", str(row.get("id", ""))):
        reasons.append("SOURCE_NOT_ACTIVE_OR_IDENTIFIED")
    if row.get("tier") != "E3":
        reasons.append("SOURCE_TIER_NOT_IN_V2_SCOPE")
    if _obj(row.get("verification")).get("status") == "HUMAN_REJECTED":
        reasons.append("SOURCE_REJECTED")
    for key, source, code in [("ingredient_id", matrix.get("ingredient_id"), "INGREDIENT_ID"),
                              ("process_id", process.get("process_id"), "PROCESS_ID"),
                              ("target_id", target.get("state_variable_id"), "TARGET_ID"),
                              ("state", matrix.get("initial_state"), "STATE"),
                              ("basis", target.get("basis"), "BASIS")]:
        if not _known(context.get(key)) or not _known(source):
            reasons.append(code + "_UNKNOWN")
        elif context[key] != source:
            reasons.append(code + "_MISMATCH")
    if condition.get("status") != "ACTIVE" or not process.get("condition_id") \
            or condition.get("id") != process.get("condition_id"):
        reasons.append("COND_MISSING_OR_NOT_ACTIVE")
    medium = condition.get("medium") or process.get("medium")
    if _known(condition.get("medium")) and _known(process.get("medium")) \
            and condition["medium"] != process["medium"]:
        reasons.append("CONFLICTING_SOURCE_MEDIUM")
    if not _known(context.get("medium")) or not _known(medium):
        reasons.append("MEDIUM_UNKNOWN")
    elif context["medium"] != medium:
        reasons.append("MEDIUM_MISMATCH")
    duration = _bounds(condition.get("duration"), "min")
    requested_time = _pair(context.get("time_min"))
    if duration is None or requested_time is None or duration != requested_time:
        reasons.append("TIME_NOT_EXACT_AND_KNOWN")
    location = context.get("temperature_location")
    temperatures_raw = condition.get("temperatures")
    temperatures_raw = temperatures_raw if isinstance(temperatures_raw, (list, tuple)) else []
    temperatures = [v for v in temperatures_raw
                    if isinstance(v, Mapping) and _known(v.get("location")) and v["location"] == location]
    if not _known(location) or len(temperatures) != 1:
        reasons.append("TEMPERATURE_LOCATION_UNKNOWN_OR_AMBIGUOUS")
    else:
        value = _bounds(temperatures[0].get("value"), "degC")
        requested_temperature = _pair(context.get("temperature_c"))
        if value is None or requested_temperature is None or value != requested_temperature:
            reasons.append("TEMPERATURE_NOT_EXACT_AND_KNOWN")
    if _retention(row) is None:
        reasons.append("NO_MEASURED_POINT_WITH_KNOWN_UNIT")
    return sorted(set(reasons))


def _refuse(reason, excluded=None, mode="ABSTAIN"):
    return {"policy": VERSION, "mode": mode, "text": REFUSAL, "reason": reason, "numbers": [],
            "excluded": excluded or {}, "citable": False, "applicability_certified": False,
            "labels": ["NON_CITABLE", "EVIDENCE_E3_UNVERIFIED", "NO_HUMAN_SIGNOFF_D085"]}


def render(decision, packets, contexts, conditions, *, renderer=None, fallback=None):
    """Render only canonical per-option reports; recheck the final fallback exactly.

    Callables are optional adapters for testing/integration. Only an exact authorized
    canonical result survives either callable. No old verbalizer is a fallback here.
    """
    decision = _obj(decision)
    if not all(isinstance(v, Mapping) for v in (packets, contexts, conditions)):
        return _refuse("INVALID_PACKET_OR_CONTEXT_CONTAINER")
    if decision.get("mode") not in ("ANSWER", "COMPARE"):
        return _refuse("MODE_NOT_AUTHORIZED_FOR_TABLE_NUMBERS", mode="ASK" if decision.get("mode") == "ASK" else "ABSTAIN")
    per = _obj(decision.get("per_option"))
    lines, numbers, excluded = [], [], {}
    for key, packet in packets.items():
        precision = _obj(per.get(key)).get("precision") if per else decision.get("precision")
        if precision not in ("QUANTITATIVE", "INTERVAL"):
            excluded[key] = ["PRECISION_MISSING_OR_NONNUMERIC"]
            continue
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z _-]{0,59}", key):
            excluded[str(key)] = ["OPTION_LABEL_NOT_CANONICAL"]
            continue
        seen = set()
        for hit in list(getattr(packet, "direct", [])) + list(getattr(packet, "near", [])):
            row = _obj(getattr(hit, "row", None))
            rid = row.get("id")
            if not isinstance(rid, str) or not re.fullmatch(r"EVD-\d{6}", rid):
                excluded[f"{key}:INVALID_SOURCE_ID"] = ["SOURCE_NOT_ACTIVE_OR_IDENTIFIED"]
                continue
            if rid in seen:
                continue
            seen.add(rid)
            condition_id = _obj(row.get("process")).get("condition_id")
            condition = conditions.get(condition_id) if isinstance(condition_id, str) else None
            why = row_reasons(row, condition, contexts.get(key))
            if getattr(hit, "evd_id", None) != rid:
                why.append("PACKET_ROW_ID_MISMATCH")
            if why:
                excluded[f"{key}:{rid}"] = sorted(set(why))
                continue
            value = _retention(row)
            lines.append(f"An unverified table row reports retention factor {value:.2f} [{rid}].")
            process_id = row["process"]["process_id"]
            numbers.append({"option": process_id, "process_id": process_id,
                            "ingredient_id": row["matrix"]["ingredient_id"],
                            "target_id": row["target"]["state_variable_id"],
                            "evd_id": rid, "value": value, "unit": "fraction",
                            "basis": "EVD_REPORTED_UNVERIFIED", "condition_id": condition_id,
                            "context_check": "EXACT_DECLARED_FIELDS_ONLY", "validated": False})
    if not lines:
        return _refuse("NO_CONTEXT_MATCHED_AUTHORIZED_POINT", excluded)
    lines.append("These are source reports, not validated predictions for your food.")
    canonical = "\n".join(lines)

    def attempt(function):
        try:
            return function(tuple(lines)) if function else canonical
        except Exception:
            return None
    text = attempt(renderer)
    if text != canonical:
        text = attempt(fallback) if fallback else None
    if text != canonical:
        return _refuse("FINAL_RENDER_NOT_AUTHORIZED", excluded)
    return {"policy": VERSION, "mode": decision["mode"], "text": text, "reason": "TABLE_REPORT_ONLY",
            "numbers": numbers, "excluded": excluded, "citable": False, "applicability_certified": False,
            "labels": ["NON_CITABLE", "EVIDENCE_E3_UNVERIFIED", "NO_HUMAN_SIGNOFF_D085"]}
