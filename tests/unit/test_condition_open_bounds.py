"""Step 07H regression: `> x` = (x, +inf) -> low=x, open_low=True ; `< x` = (-inf, x) -> high=x, open_high=True ; >=/<= closed. (Pre-07H adapter had the flags reversed.)"""
import pytest

from culinarystate.evidence import condition_normalizer as N

CASES = [("time_duration", "min", 60.0, "10 min"), ("temp_medium", "degC", 273.15, "10 °C"), ("pressure", "kPa", 1e3, "10 kPa(a)"), ("microwave_power", "W", 1.0, "10 W"), ("thickness", "mm", 1e-3, "10 mm")]


def _canon(var, v, unit):
    return N.normalize_value(var, value=v, unit=unit, pressure_reference="ABSOLUTE")["canonical_value"]


@pytest.mark.parametrize("var,unit,_f,text", CASES)
@pytest.mark.parametrize("op,side,strict", [(">", "low", True), (">=", "low", False), ("<", "high", True), ("<=", "high", False)])
def test_normalize_bound(var, unit, _f, text, op, side, strict):
    r = N.normalize_bound(var, op, 10, unit=unit, pressure_reference="ABSOLUTE", location="MEDIUM" if var.startswith("temp") else None)
    other = "high" if side == "low" else "low"
    assert r["value_type"] == "INTERVAL"
    assert r[f"canonical_{side}"] == pytest.approx(_canon(var, 10, unit))
    assert r[f"canonical_{other}"] is None
    assert r[f"open_{side}"] is strict and r[f"open_{other}"] is False


@pytest.mark.parametrize("var,unit,_f,text", CASES)
@pytest.mark.parametrize("sym,side,strict", [(">", "low", True), (">=", "low", False), ("<", "high", True), ("<=", "high", False)])
def test_text_path_matches(var, unit, _f, text, sym, side, strict):
    r = N.normalize_text(var, f"{sym}{text}", location="MEDIUM" if var.startswith("temp") else None)
    assert r["value_type"] == "INTERVAL" and r[f"open_{side}"] is strict and r[f"canonical_{side}"] is not None


@pytest.mark.parametrize("kind,side,strict", [("GT_STATED", "low", True), ("GE_STATED", "low", False), ("LT_LOD", "high", True), ("LT_LOQ", "high", True), ("LE_STATED", "high", False), ("GT_CAP", "low", False)])
def test_ledger_censor_adapter(kind, side, strict):
    r = N.from_qvalue("temp_medium", {"status": "CENSORED", "unit": "degC", "censor": {"kind": kind, "limit": 75}, "raw": "x"}, location="MEDIUM")
    assert r[f"open_{side}"] is strict and r[f"canonical_{side}"] == pytest.approx(348.15)


def test_unrecognised_censor_kind_not_guessed():
    r = N.from_qvalue("temp_medium", {"status": "CENSORED", "unit": "degC", "censor": {"kind": "WEIRD", "limit": 75}, "raw": "x"})
    assert r["status"] == N.AMBIGUOUS and "canonical_low" not in r and "canonical_value" not in r


def test_censored_without_limit_has_no_number():
    r = N.from_qvalue("time_duration", {"status": "CENSORED", "censor": {"kind": "ND"}, "raw": "ND"})
    assert r["value_type"] == "UNKNOWN" and r["censoring"]["kind"] == "ND" and "canonical_value" not in r or r.get("canonical_value") is None


def test_less_than_rule_kept_despite_zero_hits():
    assert any(True for _ in [N.normalize_text("time_duration", "<5 min")])
    assert N.normalize_text("time_duration", "<5 min")["open_high"] is True
