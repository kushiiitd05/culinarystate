from culinarystate.evidence.precheck import check_row, rf_interval


def _e(b=3.36, a=3.14, rf=0.93, yf=1.0, txt="storage 2 Months at 20°C", ing="ING-000001"):
    qv = lambda v, u="mg/100 ml": {"status": "MEASURED", "value": v, "unit": u}  # noqa: E731
    return {"before": qv(b), "after": qv(a),
            "derived": {"retention_factor": qv(rf, "fraction"), "yield_factor": qv(yf, "fraction")},
            "process": {"modifiers": {"food_after_raw": txt}}, "matrix": {"ingredient_id": ing}}


FULL = {"completeness_mask": {"temperature": "MEASURED", "duration": "MEASURED"}}


def test_rounding_tolerant_interval():
    lo, hi = rf_interval(0.01, 0.02, 1.0)
    assert lo <= 2.62 <= hi                               # 0.01 -> 0.02 rounded values allow RF 2.62


def test_pass_and_flags():
    assert check_row(_e(), FULL)["suggestion"] == "LIKELY_CONFIRM"
    assert check_row(_e(rf=0.5), FULL)["suggestion"] == "CHECK_VALUES"
    r = check_row(_e(), {"completeness_mask": {"temperature": "UNKNOWN", "duration": "MEASURED"}})
    assert r["suggestion"] == "CHECK_CONDITIONS"
    assert check_row(_e(txt="boiled"), {"completeness_mask": {}})["suggestion"] == "LIKELY_CONFIRM"  # none stated
    assert "not linked" in " ".join(check_row(_e(ing=None), FULL)["flags"])


def test_multi_step_duration_is_captured_raw():
    c = {"completeness_mask": {"temperature": "MEASURED", "duration": "UNKNOWN"}, "duration": {"raw": "2 min; 5months"}}
    r = check_row(_e(txt="blanched at 95°C for 2 min, stored at 23°C, 5months"), c)
    assert r["suggestion"] == "LIKELY_CONFIRM" and "by design" in r["flags"][0]
