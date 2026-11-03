"""Synthetic controls for the rc2 history-variable contract (S154; DRAFT_PENDING_H4).

The inherited rc1 rule says history-dependent variables are never filled from
recipe text. These cases check that the explicit rc2 check enforces it on both
inline and sidecar metadata, and that externally measured history stays a
pending human policy question instead of being silently accepted or rejected.
"""
import copy

import pytest

from culinarystate.quantity.rc2_history import (
    HISTORY_KEYS, HISTORY_POLICY_ID, check_history, validate_state_rc2,
)
from tests.unit.test_step16_quantity_contract import meta, record, schema


def state_with(key, value, mapped=None):
    r = record("STATE")
    r["variables"] = {key: value}
    r["field_metadata"] = {k: v for k, v in r["field_metadata"].items() if not k.startswith("/variables/")}
    pointer = f"/variables/{key}"
    if mapped is not None:
        r["field_metadata"][pointer] = mapped
    elif "meta" not in value:
        r["field_metadata"][pointer] = meta("UNKNOWN", "UNKNOWN")
    return r


def measured(origin, route):
    return {"status": "MEASURED", "value": 1, "unit": "1", "meta": meta(origin=origin, route=route)}


def codes(r):
    return {i.code for i in check_history(r)}


def test_history_keys_are_the_five_rc1_keys_and_policy_is_marked_pending():
    assert HISTORY_KEYS == ("cell_integrity", "enzyme_activity_state", "time_since_disruption",
                            "thermal_dose", "oxygen_exposure")
    assert HISTORY_POLICY_ID.endswith("PENDING_H4")


@pytest.mark.parametrize("key", HISTORY_KEYS)
def test_unknown_history_is_always_allowed(key):
    r = state_with(key, {"status": "UNKNOWN"})
    assert check_history(r) == []
    assert validate_state_rc2(r, schema("STATE")) == []


@pytest.mark.parametrize("origin,route", [("MODEL_ESTIMATED", "MODEL"), ("SIMULATED", "SIMULATED")])
def test_model_and_simulated_history_with_matching_origin_pass(origin, route):
    r = state_with("thermal_dose", measured(origin, route))
    assert check_history(r) == []
    assert validate_state_rc2(r, schema("STATE")) == []


def test_source_text_origin_cannot_hide_behind_a_model_route():
    # Passes the rc1/rc2 JSON Schema rule (route MODEL) but the origin says source text.
    r = state_with("cell_integrity", measured("EXPLICIT_SOURCE", "MODEL"))
    assert "HISTORY_FROM_RECIPE_TEXT_FORBIDDEN" in codes(r)
    assert any(i.code == "HISTORY_FROM_RECIPE_TEXT_FORBIDDEN" for i in validate_state_rc2(r, schema("STATE")))


@pytest.mark.parametrize("route", ["EXPLICIT", "INFERRED_RULE", "INFERRED_LLM"])
def test_text_routes_are_forbidden_even_without_inline_meta(route):
    value = {"status": "QUALITATIVE", "qualitative": "synthetic"}
    r = state_with("enzyme_activity_state", value, mapped=meta(origin="DERIVED_DETERMINISTIC", route=route))
    assert "HISTORY_FROM_RECIPE_TEXT_FORBIDDEN" in codes(r)


def test_externally_measured_history_is_pending_not_accepted_or_called_recipe_text():
    r = state_with("oxygen_exposure", measured("EXTERNAL_VERIFIED", "MODEL"))
    found = codes(r)
    assert "HISTORY_EXTERNAL_POLICY_PENDING_H4" in found
    assert "HISTORY_FROM_RECIPE_TEXT_FORBIDDEN" not in found


def test_route_origin_mismatch_is_reported_as_pending():
    r = state_with("time_since_disruption", measured("DERIVED_DETERMINISTIC", "SIMULATED"))
    assert codes(r) == {"HISTORY_ORIGIN_ROUTE_PENDING_H4"}


def test_populated_history_without_any_metadata_is_reported():
    r = record("STATE")
    r["variables"] = {"thermal_dose": {"status": "MEASURED", "value": 3, "unit": "1"}}
    r["field_metadata"].pop("/variables/thermal_dose", None)
    assert "HISTORY_METADATA_MISSING" in codes(r)


def test_both_inline_and_sidecar_copies_are_checked():
    value = measured("MODEL_ESTIMATED", "MODEL")
    r = state_with("thermal_dose", value, mapped=meta(origin="EXPLICIT_SOURCE", route="EXPLICIT"))
    assert "HISTORY_FROM_RECIPE_TEXT_FORBIDDEN" in codes(r)


def test_non_history_variables_and_inputs_are_untouched():
    r = record("STATE")
    r["variables"] = {"temperature": {"status": "MEASURED", "value": 180, "unit": "C",
                                      "meta": meta()}}
    r["field_metadata"].pop("/variables/temperature", None)
    before = copy.deepcopy(r)
    assert check_history(r) == []
    assert r == before


def test_non_state_records_are_refused():
    with pytest.raises(ValueError):
        check_history(record("QNT"))
