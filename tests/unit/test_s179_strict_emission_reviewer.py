"""Independent malformed-source and false-tier regression probes for strict v2."""
from types import SimpleNamespace

import pytest

from culinarystate.generation.strict_v2 import render


def _case():
    context = {"ingredient_id": "ING-990001", "process_id": "PROC-990001", "target_id": "SVAR-990001",
               "state": "RAW", "basis": "TRUE_RETENTION", "medium": "WATER", "time_min": (5, 5),
               "temperature_c": (90, 90), "temperature_location": "CORE"}
    condition = {"id": "COND-990001", "status": "ACTIVE", "medium": "WATER",
                 "duration": {"status": "MEASURED", "value": 5, "unit": "min"},
                 "temperatures": [{"location": "CORE", "value": {"status": "MEASURED", "value": 90,
                                                                            "unit": "degC"}}]}
    row = {"id": "EVD-990001", "status": "ACTIVE", "tier": "E3",
           "matrix": {"ingredient_id": "ING-990001", "initial_state": "RAW"},
           "process": {"process_id": "PROC-990001", "condition_id": "COND-990001", "medium": "WATER"},
           "target": {"state_variable_id": "SVAR-990001", "basis": "TRUE_RETENTION"},
           "derived": {"retention_factor": {"status": "MEASURED", "value": .55, "unit": "fraction"}}}
    return context, condition, row


def _render(context, condition, row):
    packet = SimpleNamespace(direct=[SimpleNamespace(evd_id=row["id"], row=row)], near=[], evidence_class="DIRECT")
    return render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"boil": packet},
                  {"boil": context}, {"COND-990001": condition})


@pytest.mark.parametrize("tier", [None, "E5", "E6", "E7"])
def test_non_e3_source_cannot_acquire_e3_numeric_label(tier):
    context, condition, row = _case()
    row["tier"] = tier
    out = _render(context, condition, row)
    assert out["numbers"] == [] and out["mode"] == "ABSTAIN"


@pytest.mark.parametrize("temperatures", [None, 42, [None]])
def test_malformed_source_temperatures_refuse_without_exception(temperatures):
    context, condition, row = _case()
    condition["temperatures"] = temperatures
    out = _render(context, condition, row)
    assert out["numbers"] == [] and out["mode"] == "ABSTAIN"


def test_unhashable_source_id_refuses_without_exception():
    context, condition, row = _case()
    row["id"] = []
    out = _render(context, condition, row)
    assert out["numbers"] == [] and out["mode"] == "ABSTAIN"


def test_unhashable_condition_reference_refuses_without_exception():
    context, condition, row = _case()
    row["process"]["condition_id"] = []
    out = _render(context, condition, row)
    assert out["numbers"] == [] and out["mode"] == "ABSTAIN"


@pytest.mark.parametrize("field", ["source_rate", "source_duration", "requested_duration"])
def test_unrepresentable_numeric_input_refuses_without_exception(field):
    context, condition, row = _case()
    huge = 10 ** 1000
    if field == "source_rate":
        row["derived"]["retention_factor"]["value"] = huge
    elif field == "source_duration":
        condition["duration"]["value"] = huge
    else:
        context["time_min"] = (huge, huge)
    out = _render(context, condition, row)
    assert out["numbers"] == [] and out["mode"] == "ABSTAIN"
