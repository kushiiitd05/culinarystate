"""Conservative display view: quantities need their own known declared provenance.

This view does not recompute the physical model or turn source-row presence into
condition applicability. Raw source fields remain separately available in JSON.
"""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from fractions import Fraction
import math

VERSION = "strict-display-v3.0.0"
BASES = {"TEXT_STATED", "CARRIED_SETPOINT", "PHYSICAL_DEFINITION", "PROCESS_DEFINITION", "CUE",
         "CUT_HISTORY", "FOOD_GROUP", "SCENARIO", "MODEL_DERIVED"}
STATUSES = {"MEASURED", "RANGE", "SCENARIO", "MODEL_DERIVED"}
FIELDS = (("stated", "duration_min", "Recorded duration", "min"),
          ("stated", "temperature_c", "Recorded temperature", "degC"),
          ("scenario", "typical_bath_c", "Scenario medium temperature", "degC"),
          ("scenario", "typical_duration_min", "Scenario duration", "min"),
          ("scenario", "typical_core_end_c", "Scenario typical centre temperature", "degC"),
          ("scenario", "range_core_end_c", "Scenario centre temperature endpoint", "degC"))


def _obj(value):
    return value if isinstance(value, Mapping) else {}


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(Fraction(value)) if isinstance(value, str) else float(value)
        return number if math.isfinite(number) else None
    except (ValueError, TypeError, OverflowError, ZeroDivisionError):
        return None


def _leaves(value, path):
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from _leaves(child, f"{path}.{index}")
    else:
        yield path, value


def physics_display(step):
    step = _obj(step)
    provenance = _obj(step.get("numeric_provenance"))
    numbers, unavailable = [], []
    for prefix, field, label, unit in FIELDS:
        value = _obj(step.get(prefix)).get(field)
        for path, leaf in _leaves(value, prefix + "." + field):
            source = _obj(provenance.get(path))
            numeric = _number(leaf)
            if numeric is None or source.get("basis") not in BASES or source.get("status") not in STATUSES \
                    or source.get("unit") != unit:
                unavailable.append(path)
                continue
            numbers.append({"path": path, "label": label, "value": numeric, "display_value": repr(numeric),
                            "unit": unit, "basis": source["basis"], "status": source["status"],
                            "source_field_refs": deepcopy(source.get("source_field_refs", [])),
                            "span_ids": deepcopy(source.get("span_ids", [])),
                            "registry_refs": deepcopy(source.get("registry_refs", [])),
                            "assumed_default_refs": deepcopy(source.get("assumed_default_refs", [])),
                            "validated": False})
    return {"numbers": numbers, "unavailable_paths": unavailable, "citable": False,
            "provenance_scope": "DECLARED_SOURCE_FIELDS_ONLY", "applicability_certified": False}


def recipe_display(recipe):
    recipe = _obj(recipe)
    physics = _obj(recipe.get("physics")).get("steps") or []
    by_event = {step["event_id"]: step for step in physics}
    rows, seen = [], set()
    for step in recipe.get("steps") or []:
        event_id = step.get("event_id")
        seen.add(event_id)
        direct = step.get("route") == "DIRECT"
        rows.append({"event_id": event_id, "action": step.get("action"), "ingredient_id": step.get("ingredient_id"),
                     "legacy_route": step.get("route"), "evidence_ids": list(step.get("evidence") or []),
                     "badge": "Unverified source row only" if direct else "Condition applicability unknown",
                     "explanation": "A retrieved table row exists; recipe conditions and source validity are not certified."
                     if direct else "The legacy screening route is metadata, not a scientific applicability determination.",
                     "applicability_certified": False, "physics": physics_display(by_event.get(event_id))})
    for event_id, step in by_event.items():
        if event_id not in seen:
            rows.append({"event_id": event_id, "action": step.get("action"), "ingredient_id": None,
                         "legacy_route": None, "evidence_ids": [], "badge": "Condition applicability unknown",
                         "explanation": "Physical scenario display only; no source effect is applied.",
                         "applicability_certified": False, "physics": physics_display(step)})
    return {"version": VERSION, "steps": rows, "citable": False,
            "labels": ["NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"],
            "scope": "DECLARED_PROVENANCE_DISPLAY_NOT_SCIENTIFIC_VERIFICATION"}
