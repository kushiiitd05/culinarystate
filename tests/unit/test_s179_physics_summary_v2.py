"""Synthetic per-number provenance checks, independent of scientific model accuracy."""
from copy import deepcopy
from fractions import Fraction

from culinarystate.decision.demo_context import physics_summary
from culinarystate.decision.physics_summary_v2 import physics_summary_v2


def fixture():
    inputs = {
        "duration": {"value": Fraction(5, 2), "status": "MEASURED", "basis": "TEXT_STATED",
                     "unit": "min", "span_id": "C:0-4", "row": "CB_RULE:DURATION"},
        "temperature_profile": {"value": (Fraction(90), Fraction(100)), "status": "RANGE",
                                "basis": "PHYSICAL_DEFINITION", "span_id": "E:SYN-E1", "row": "PROC_MAP:SYN"},
        "medium": {"value": "WATER", "status": "MEASURED", "basis": "PROCESS_DEFINITION"},
        "lid_state": {"value": "COVERED", "status": "MEASURED", "basis": "CUE"},
        "piece_size_class": {"value": "DICED", "status": "MEASURED", "basis": "CUT_HISTORY"},
    }
    event = {"event_id": "SYN-E1", "action": "synthetic heat", "process_id": "PROC-990001",
             "family": "WET_HEAT", "heat": True, "oven_setpoint_code": None, "inputs": inputs}
    bases = {"bath_c": "L1:PHYSICAL_DEFINITION", "duration_min": "L1:TEXT_STATED", "initial_c": "SD-011",
             "k": "SD-012", "alpha": "SD-013", "h": "SD-014", "half_thickness_m": "SD-015"}
    scenarios = {name: {"bath_c": 95., "duration_min": 2.5, "core_end_c": core,
                        "bases": deepcopy(bases), "flags": ["SOURCE_UNVERIFIED"]}
                 for name, core in [("GENTLE", 40.), ("TYPICAL", 50.), ("INTENSE", 60.)]}
    result = {"status": "SCENARIO_COMPUTED", "version": "SYN-LAYER", "scenarios": scenarios,
              "l1_provenance": {k: {a: v[a] for a in ["basis", "span_id", "row"] if a in v}
                                for k, v in inputs.items()}}
    return {"events": [event]}, result


class Binder:
    def __init__(self, result):
        self.result, self.calls = result, 0

    def bind_text(self, text):
        self.calls += 1
        return self.result


class Layer:
    def __init__(self, result):
        self.result, self.records = result, []

    def run(self, record):
        self.records.append(record)
        return self.result


def run(binding=None, scenario=None):
    a, b = fixture()
    binder, layer = Binder(a if binding is None else binding), Layer(b if scenario is None else scenario)
    return physics_summary_v2("synthetic input", binder, layer), binder, layer


def test_legacy_display_fields_unchanged_and_dependencies_called_once():
    a, b = fixture()
    old = physics_summary("synthetic input", Binder(deepcopy(a)), Layer(deepcopy(b)))
    out, binder, layer = run(a, b)
    assert binder.calls == 1 and len(layer.records) == 1
    for key in ("event_id", "action", "process_id", "stated", "scenario"):
        assert out["steps"][0][key] == old["steps"][0][key]


def test_stated_values_preserve_actual_basis_status_unit_and_source_refs():
    out, _, _ = run()
    p = out["steps"][0]["numeric_provenance"]
    duration = p["stated.duration_min"]
    assert duration["basis"] == "TEXT_STATED" and duration["status"] == "MEASURED"
    assert duration["unit"] == "min" and duration["source_unit"] == "min"
    assert "C:0-4" in duration["span_ids"] and "CB_RULE:DURATION" in duration["registry_refs"]
    for endpoint in (0, 1):
        temp = p[f"stated.temperature_c.{endpoint}"]
        assert temp["basis"] == "PHYSICAL_DEFINITION" and temp["status"] == "RANGE"
        assert temp["unit"] == "degC" and temp["unit_source"] == "BINDER_AXIS_CONTRACT"
        assert any("temperature_profile" in ref for ref in temp["source_field_refs"])


def test_scenario_is_not_relabelled_text_stated_and_core_keeps_dependencies():
    out, _, _ = run()
    p = out["steps"][0]["numeric_provenance"]
    assert p["scenario.typical_bath_c"]["basis"] == "SCENARIO"
    assert p["scenario.typical_bath_c"]["source_basis"] == "L1:PHYSICAL_DEFINITION"
    core = p["scenario.typical_core_end_c"]
    assert core["basis"] == "MODEL_DERIVED" and core["status"] == "MODEL_DERIVED"
    assert core["assumed_default_refs"] == ["SD-011", "SD-012", "SD-013", "SD-014", "SD-015"]
    assert "scenario.range_core_end_c.0" in p and "scenario.range_core_end_c.1" in p
    assert out["numeric_provenance_complete"] is True


def test_unknown_source_basis_remains_unknown_and_blocks_complete_coverage():
    a, b = fixture()
    a["events"][0]["inputs"]["duration"]["basis"] = "UNREGISTERED_GUESS"
    out, _, _ = run(a, b)
    p = out["steps"][0]["numeric_provenance"]["stated.duration_min"]
    assert p["basis"] == p["status"] == "UNKNOWN"
    assert p["source_basis"] == "UNREGISTERED_GUESS"
    assert out["numeric_provenance_complete"] is False


def test_missing_core_dependency_cannot_claim_model_provenance_complete():
    a, b = fixture()
    del b["scenarios"]["TYPICAL"]["bases"]["h"]
    out, _, _ = run(a, b)
    p = out["steps"][0]["numeric_provenance"]["scenario.typical_core_end_c"]
    assert p["status"] == "UNKNOWN" and out["numeric_provenance_complete"] is False


def test_default_and_corpus_refs_are_preserved_without_claiming_observation():
    a, b = fixture()
    b["scenarios"]["TYPICAL"]["bases"].update(bath_c="SD-001", duration_min="KGE-990001")
    out, _, _ = run(a, b)
    p = out["steps"][0]["numeric_provenance"]
    assert p["scenario.typical_bath_c"]["assumed_default_refs"] == ["SD-001"]
    assert p["scenario.typical_duration_min"]["source_basis"] == "KGE-990001"
    assert p["scenario.typical_duration_min"]["basis"] == "SCENARIO"


def test_null_numbers_are_not_filled_or_given_numeric_provenance():
    a, b = fixture()
    b["scenarios"]["GENTLE"]["core_end_c"] = None
    b["scenarios"]["TYPICAL"]["core_end_c"] = None
    out, _, _ = run(a, b)
    step = out["steps"][0]
    assert step["scenario"]["typical_core_end_c"] is None
    assert step["scenario"]["range_core_end_c"] == [None, 60.]
    assert "scenario.typical_core_end_c" not in step["numeric_provenance"]
    assert "scenario.range_core_end_c.0" not in step["numeric_provenance"]


def test_inputs_are_immutable_even_if_layer_mutates_its_argument():
    a, b = fixture()
    before = deepcopy((a, b))

    class MutatingLayer(Layer):
        def run(self, record):
            record["inputs"]["duration"]["basis"] = "MUTATED"
            return self.result

    out = physics_summary_v2("synthetic input", Binder(a), MutatingLayer(b))
    assert (a, b) == before
    assert out["steps"][0]["numeric_provenance"]["stated.duration_min"]["basis"] == "TEXT_STATED"


def test_non_heat_event_does_not_call_scenario_layer():
    a, b = fixture()
    a["events"][0]["heat"] = False
    out, binder, layer = run(a, b)
    assert binder.calls == 1 and not layer.records and not out["steps"]
