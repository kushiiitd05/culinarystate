"""Physical display compatible with v1 plus explicit per-number provenance.

No model, binding or scientific rule is changed. Metadata describes only exported
numeric leaves. UNKNOWN provenance never becomes TEXT_STATED by field-name inference.
"""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from fractions import Fraction
import math
import re

VERSION = "physics-summary-provenance-v2.0.0"
L1_BASES = {"TEXT_STATED", "CARRIED_SETPOINT", "PHYSICAL_DEFINITION", "PROCESS_DEFINITION",
            "CUE", "CUT_HISTORY", "FOOD_GROUP"}
CORE_INPUTS = {"bath_c", "duration_min", "initial_c", "k", "alpha", "h", "half_thickness_m"}
AXES = {"bath_c": "temperature_profile", "duration_min": "duration", "t_cap_c": "temperature_profile"}


def _obj(value):
    return value if isinstance(value, Mapping) else {}


def _str(value):
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, tuple):
        return [_str(child) for child in value]
    return str(value)


def _numeric(value):
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, Fraction)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, str):
        try:
            Fraction(value)
            return True
        except (ValueError, ZeroDivisionError):
            pass
    return False


def _leaves(value, suffix=""):
    if isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            yield from _leaves(child, f"{suffix}.{i}")
    elif value is not None:
        yield suffix, value


def _l1_record(axis, inputs, event_index):
    source = _obj(inputs.get(axis))
    unit = "min" if axis == "duration" else "degC"
    native_unit = source.get("unit")
    actual_basis = source.get("basis")
    known = actual_basis in L1_BASES and source.get("status") in ("MEASURED", "RANGE")
    if native_unit is not None and native_unit != unit:
        known = False
    return {"basis": actual_basis if known else "UNKNOWN", "status": source.get("status") if known else "UNKNOWN",
            "source_basis": actual_basis, "source_status": source.get("status", "UNKNOWN"),
            "unit": native_unit if native_unit is not None else unit, "source_unit": native_unit,
            "unit_source": "SOURCE_FIELD" if native_unit is not None else "BINDER_AXIS_CONTRACT",
            "source_field_refs": [f"/binder/events/{event_index}/inputs/{axis}/value"],
            "span_ids": [source["span_id"]] if isinstance(source.get("span_id"), str) else [],
            "registry_refs": [source["row"]] if isinstance(source.get("row"), str) else [],
            "assumed_default_refs": [], "layer": 1, "provenance_scope": "DECLARED_SOURCE_FIELDS_ONLY"}


def _basis(token, inputs, axis, event_index):
    """Map declared basis tokens; this does not validate registry source quality."""
    refs, spans, defaults, fields = [], [], [], []
    if not isinstance(token, str) or not token:
        return False, refs, spans, defaults, fields
    for component in token.split("|"):
        if component.startswith("L1:"):
            if axis not in ("duration", "temperature_profile"):
                return False, refs, spans, defaults, fields
            rec = _l1_record(axis, inputs, event_index)
            if rec["basis"] == "UNKNOWN" or component != "L1:" + str(rec["source_basis"]):
                return False, refs, spans, defaults, fields
            refs += rec["registry_refs"]
            spans += rec["span_ids"]
            fields += rec["source_field_refs"]
        elif re.fullmatch(r"SD-\d{3}|KGE-\d{6}", component):
            refs.append(component)
            defaults.append(component)
        elif re.fullmatch(r"PC-\d{3}(?:\.\.PC-\d{3})?", component):
            refs.append(component)
        elif component.startswith("ASSUMED_DEFAULT:"):
            ref = component.split(":", 1)[1]
            if not re.fullmatch(r"SD-\d{3}|KGE-\d{6}|PC-\d{3}", ref):
                return False, refs, spans, defaults, fields
            refs.append(ref)
            defaults.append(ref)
        elif component != "MODEL_DERIVED":
            return False, refs, spans, defaults, fields
    return True, refs, spans, defaults, fields


def _scenario_record(field, bracket, scenario, inputs, event_index, *, core=False):
    point = _obj(_obj(scenario.get("scenarios")).get(bracket))
    bases = _obj(point.get("bases"))
    selected = dict(bases) if core else {field: bases.get(field)}
    known = scenario.get("status") == "SCENARIO_COMPUTED"
    if core:
        known = known and CORE_INPUTS <= bases.keys()
        if point.get("t_cap_c") is not None and "t_cap_c" not in bases:
            known = False
    refs, spans, defaults, fields = [], [], [], [f"/scenario/scenarios/{bracket}/{field}"]
    for name, token in selected.items():
        good, rs, ss, ds, fs = _basis(token, inputs, AXES.get(name), event_index)
        known = known and good
        refs += rs
        spans += ss
        defaults += ds
        fields += fs + [f"/scenario/scenarios/{bracket}/bases/{name}"]
    return {"basis": ("MODEL_DERIVED" if core else "SCENARIO") if known else "UNKNOWN",
            "status": ("MODEL_DERIVED" if core else "SCENARIO") if known else "UNKNOWN",
            "source_basis": deepcopy(bases) if core else bases.get(field),
            "source_status": scenario.get("status", "UNKNOWN"), "unit": "min" if field == "duration_min" else "degC",
            "source_unit": None, "unit_source": "SCENARIO_OUTPUT_CONTRACT", "layer": 2,
            "source_field_refs": sorted(set(fields)), "span_ids": sorted(set(spans)),
            "registry_refs": sorted(set(refs)), "assumed_default_refs": sorted(set(defaults)),
            "model_version": scenario.get("version"), "cap_model_version": scenario.get("cap_model"),
            "provenance_scope": "DECLARED_SOURCE_FIELDS_ONLY"}


def physics_summary_v2(recipe_text, binder, layer):
    """Bind once, run the original scenario contract, annotate exported numeric leaves."""
    bound = binder.bind_text(recipe_text)
    steps, gaps = [], []
    numeric_count = 0
    for index, ev in enumerate(bound["events"]):
        if not ev["heat"]:
            continue
        inputs = ev["inputs"]
        rec = {"process_id": ev["process_id"], "family": ev["family"], "oven_setpoint_code": ev["oven_setpoint_code"],
               "inputs": {key: {**deepcopy(value), "value": _str(value["value"])} for key, value in inputs.items()}}
        scenario = layer.run(rec)
        scenarios = _obj(scenario.get("scenarios"))
        typical = _obj(scenarios.get("TYPICAL"))
        temp = inputs["temperature_profile"]
        step = {"event_id": ev["event_id"], "action": ev["action"], "process_id": ev["process_id"],
                "stated": {"duration_min": _str(inputs["duration"]["value"]), "temperature_c": _str(temp["value"]),
                           "temperature_basis": temp.get("basis"), "medium": inputs["medium"]["value"],
                           "lid": inputs["lid_state"]["value"], "piece_size": inputs["piece_size_class"]["value"]},
                "scenario": {"status": scenario["status"], "typical_bath_c": typical.get("bath_c"),
                             "typical_duration_min": typical.get("duration_min"),
                             "typical_core_end_c": typical.get("core_end_c"),
                             "range_core_end_c": [scenarios.get(b, {}).get("core_end_c") for b in ("GENTLE", "INTENSE")]
                             if scenarios else None, "bases": deepcopy(typical.get("bases")),
                             "flags": deepcopy(typical.get("flags"))}, "numeric_provenance": {}}

        def annotate(path, value, record):
            nonlocal numeric_count
            for suffix, leaf in _leaves(value):
                metadata = deepcopy(record)
                if not _numeric(leaf):
                    metadata["basis"] = metadata["status"] = "UNKNOWN"
                metadata["path"] = path + suffix
                step["numeric_provenance"][path + suffix] = metadata
                numeric_count += 1
                if metadata["status"] == "UNKNOWN":
                    gaps.append({"event_id": ev["event_id"], "path": path + suffix,
                                 "reason": "SOURCE_PROVENANCE_UNMAPPED_OR_UNKNOWN"})

        for field, axis in (("duration_min", "duration"), ("temperature_c", "temperature_profile")):
            annotate("stated." + field, step["stated"][field], _l1_record(axis, inputs, index))
        for display, source in (("typical_bath_c", "bath_c"), ("typical_duration_min", "duration_min"),
                                ("typical_core_end_c", "core_end_c")):
            annotate("scenario." + display, step["scenario"][display],
                     _scenario_record(source, "TYPICAL", scenario, inputs, index, core=source == "core_end_c"))
        if step["scenario"]["range_core_end_c"] is not None:
            for endpoint, bracket in enumerate(("GENTLE", "INTENSE")):
                annotate(f"scenario.range_core_end_c.{endpoint}", step["scenario"]["range_core_end_c"][endpoint],
                         _scenario_record("core_end_c", bracket, scenario, inputs, index, core=True))
        steps.append(step)
    labels = ["SCENARIO", "MODEL_DERIVED", "NON_CITABLE"]
    if any(v["basis"] == "TEXT_STATED" for step in steps for v in step["numeric_provenance"].values()):
        labels.insert(0, "TEXT_STATED")
    return {"version": VERSION, "labels": labels, "steps": steps, "numeric_provenance_complete": not gaps,
            "numeric_provenance_scope": "EXPORTED_NON_NULL_NUMERIC_LEAVES_ONLY", "numeric_fields": numeric_count,
            "numeric_provenance_gaps": gaps, "citable": False}
