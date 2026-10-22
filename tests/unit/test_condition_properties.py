"""Step 07H property-based tests (Hypothesis). Run counts are set explicitly so the gate report can quote them."""
import json
import math

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from culinarystate.evidence import condition_normalizer as N
from culinarystate.evidence import condition_parser as P
from culinarystate.evidence import condition_units as U

SET = settings(max_examples=300, deadline=None, suppress_health_check=[HealthCheck.too_slow])
finite = st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
pos = st.floats(min_value=1e-6, max_value=1e6, allow_nan=False, allow_infinity=False)
VARS = ["temp_medium", "time_duration", "pressure", "microwave_power", "ph", "water_activity", "salt_content", "thickness"]
UNIT = {"temp_medium": "degC", "time_duration": "min", "pressure": "kPa(a)", "microwave_power": "W", "ph": "pH", "water_activity": "aw", "salt_content": "percent", "thickness": "mm"}
NUMKEYS = ("canonical_value", "canonical_low", "canonical_high")


@SET
@given(finite, st.sampled_from(["degC", "degF", "K"]))
def test_temperature_roundtrip(x, u):
    k = U.convert_temperature(x, u)
    back = {"degC": k - 273.15, "degF": (k - 273.15) * 9 / 5 + 32, "K": k}[u]
    assert back == pytest.approx(x, rel=1e-9, abs=1e-7)


@SET
@given(finite, finite, st.sampled_from(VARS))
def test_interval_order_never_silently_changed(a, b, var):
    r = N.normalize_value(var, low=a, high=b, unit=UNIT[var], location="MEDIUM", basis="WET")
    if a > b:
        assert r["status"] == N.INVALID and N.R_REVERSED in r["reasons"]
    elif r["value_type"] == "INTERVAL" and r.get("canonical_low") is not None and r.get("canonical_high") is not None:
        assert r["canonical_low"] <= r["canonical_high"]


@SET
@given(st.text(max_size=30), st.sampled_from(VARS))
def test_unknown_inputs_never_acquire_values(txt, var):
    r = N.normalize_value(var, raw=txt)
    assert r["value_type"] == "UNKNOWN" and all(r.get(k) is None for k in NUMKEYS)


@SET
@given(st.text(alphabet=st.characters(categories=("L", "Zs")), min_size=1, max_size=30), st.sampled_from(VARS))
def test_qualitative_never_acquires_numbers(txt, var):
    r = N.normalize_value(var, qualitative=txt)
    assert r["value_type"] == "QUALITATIVE" and all(r.get(k) is None for k in NUMKEYS)


@SET
@given(pos, st.sampled_from(sorted(U.TIME)))
def test_time_conversion_preserves_dimension_and_ratio(x, unit):
    one = N.normalize_value("time_duration", value=x, unit=unit)["canonical_value"]
    two = N.normalize_value("time_duration", value=2 * x, unit=unit)["canonical_value"]
    assert two == pytest.approx(2 * one) and one == pytest.approx(x * U.TIME[unit])


@SET
@given(st.text(max_size=40), st.sampled_from(VARS))
def test_determinism_byte_equivalent(txt, var):
    a = json.dumps(N.normalize_text(var, txt, location="MEDIUM"), sort_keys=True, default=str)
    b = json.dumps(N.normalize_text(var, txt, location="MEDIUM"), sort_keys=True, default=str)
    assert a == b and json.dumps(P.parse_raw(txt), sort_keys=True) == json.dumps(P.parse_raw(txt), sort_keys=True)


@SET
@given(st.one_of(finite, st.just(float("nan")), st.just(float("inf")), st.just(float("-inf"))), st.sampled_from(VARS))
def test_no_nan_inf_in_valid_output(x, var):
    r = N.normalize_value(var, value=x, unit=UNIT[var], location="MEDIUM", basis="WET")
    if not math.isfinite(x):
        assert r["status"] == N.INVALID
    if r["status"] == N.VALID:
        assert all(r.get(k) is None or math.isfinite(r[k]) for k in NUMKEYS)


@SET
@given(finite, st.sampled_from([">", ">=", "<", "<="]), st.sampled_from(["temp_medium", "time_duration", "microwave_power", "thickness"]))
def test_open_bound_semantics(x, op, var):
    r = N.normalize_bound(var, op, x, unit=UNIT[var], location="MEDIUM")
    if r["status"] == N.INVALID:
        return
    side = "low" if op in (">", ">=") else "high"
    other = "high" if side == "low" else "low"
    assert r[f"canonical_{side}"] is not None and r[f"canonical_{other}"] is None
    assert r[f"open_{side}"] is (op in (">", "<")) and r[f"open_{other}"] is False


@SET
@given(st.text(max_size=60))
def test_normalize_text_never_raises_and_keeps_raw(txt):
    r = N.normalize_text("temp_medium", txt, location="CORE")
    assert r["raw"] == txt and r["status"] in (N.VALID, N.INVALID, N.AMBIGUOUS, N.UNKNOWN)


@SET
@given(st.floats(min_value=0, max_value=1000, allow_nan=False), st.floats(min_value=0, max_value=100, allow_nan=False))
def test_uncertainty_is_not_a_range(v, e):
    r = N.normalize_value("temp_medium", value=v, unit="degC", location="MEDIUM", uncertainty={"value": e, "unit_text": "degC", "type": "REPORTED_UNSPECIFIED"})
    assert r["value_type"] == "POINT" and r.get("canonical_low") is None and r["uncertainty"]["canonical_value"] == pytest.approx(e)
