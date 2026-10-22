"""Step 07H: strict schema contract (registry/schemas/condition_value_v1.schema.json): every normalizer output validates; contradictory objects are rejected."""
import json
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from jsonschema import Draft202012Validator

from culinarystate.evidence import condition_normalizer as N

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "registry/schemas/condition_value_v1.schema.json").read_text())
V = Draft202012Validator(SCHEMA)
GOLD = json.loads((ROOT / "tests/golden/condition_syntax_golden_v1.json").read_text(encoding="utf-8"))
BASE = {"variable": "temp_medium", "variable_id": "CV-006", "raw": "x", "reasons": []}


def test_schema_is_valid_draft2020():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("case", GOLD, ids=[c["id"] for c in GOLD])
def test_all_golden_outputs_validate(case):
    r = N.normalize_text(case["var"], case["raw"], location=case["location"], basis=case["basis"])
    errs = [e.message for e in V.iter_errors(r)]
    assert not errs, errs


@settings(max_examples=400, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.text(max_size=40), st.sampled_from(["temp_medium", "temp_unspecified", "time_duration", "pressure", "microwave_power", "ph", "water_activity", "moisture_content", "salt_content", "thickness"]))
def test_fuzz_text_outputs_always_validate(txt, var):
    r = N.normalize_text(var, txt, location="MEDIUM")
    assert not list(V.iter_errors(r)), (txt, var, [e.message for e in V.iter_errors(r)])


BAD = [
    ("POINT VALID without canonical value", dict(BASE, value_type="POINT", status="VALID")),
    ("INTERVAL VALID with no finite endpoint", dict(BASE, value_type="INTERVAL", status="VALID", canonical_low=None, canonical_high=None, canonical_unit="K", open_low=False, open_high=False)),
    ("open_low without a low endpoint", dict(BASE, value_type="INTERVAL", status="AMBIGUOUS", reasons=["X"], canonical_low=None, canonical_high=5.0, open_low=True)),
    ("INTERVAL carrying a point value", dict(BASE, value_type="INTERVAL", status="AMBIGUOUS", reasons=["X"], canonical_value=3.0)),
    ("QUALITATIVE with a number", dict(BASE, value_type="QUALITATIVE", status="VALID", qualitative="hot", canonical_value=450.0)),
    ("QUALITATIVE without text", dict(BASE, value_type="QUALITATIVE", status="VALID")),
    ("UNKNOWN with a number", dict(BASE, value_type="UNKNOWN", status="UNKNOWN", reasons=["NOT_STATED"], canonical_value=1.0)),
    ("UNKNOWN without a reason", dict(BASE, value_type="UNKNOWN", status="UNKNOWN")),
    ("AMBIGUOUS without a reason", dict(BASE, value_type="POINT", status="AMBIGUOUS", canonical_value=1.0, canonical_unit="K")),
    ("TRAJECTORY with one point", dict(BASE, value_type="TRAJECTORY", status="VALID", canonical_time_unit="s", points=[{"raw_time": 0, "raw_time_unit": "s", "canonical_time": 0.0, "raw_value": 1, "raw_value_unit": "K", "canonical_value": 1.0, "location": "CORE", "status": "VALID", "reasons": []}])),
    ("unknown extra field", dict(BASE, value_type="UNKNOWN", status="UNKNOWN", reasons=["NOT_STATED"], surprise=1)),
    ("approximate=false is not allowed (absent or true only)", dict(BASE, value_type="UNKNOWN", status="UNKNOWN", reasons=["NOT_STATED"], approximate=False)),
    ("negative uncertainty magnitude", dict(BASE, value_type="POINT", status="VALID", canonical_value=1.0, canonical_unit="K", uncertainty={"value": -1, "type": "SD"})),
]


@pytest.mark.parametrize("name,obj", BAD, ids=[b[0] for b in BAD])
def test_contradictory_objects_rejected(name, obj):
    assert list(V.iter_errors(obj)), f"schema accepted: {name}"


def test_good_minimal_objects_accepted():
    assert not list(V.iter_errors(dict(BASE, value_type="POINT", status="VALID", canonical_value=1.0, canonical_unit="K")))
    assert not list(V.iter_errors(dict(BASE, value_type="UNKNOWN", status="UNKNOWN", reasons=["NOT_STATED"])))
