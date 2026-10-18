from culinarystate.evidence.conditions import extract_conditions, total_duration


def test_duration_and_power():
    c = extract_conditions("Red cabbage, microwaved by steam vapour for 2 min at 800 W")
    assert c["durations"] == [{"status": "MEASURED", "value": 2.0, "unit": "min", "raw": "2 min"}]
    assert c["power"][0]["value"] == 800.0


def test_ranges_and_hours():
    c = extract_conditions("boiled 15-20 min; soaked for 12 h")
    assert c["durations"][0] == {"status": "RANGE", "low": 15.0, "high": 20.0, "unit": "min", "raw": "15-20 min"}
    assert c["durations"][1]["value"] == 720.0


def test_seconds():
    assert extract_conditions("blanched 90 s")["durations"][0]["value"] == 1.5


def test_temperature_location_never_assumed_core():
    t = extract_conditions("baked at 180 °C for 30 min")["temperatures"][0]
    assert t["location"] == "UNSPECIFIED" and t["value"]["value"] == 180.0 and t["value"]["unit"] == "degC"
    assert extract_conditions("oven at 200°C")["temperatures"][0]["location"] == "SETPOINT"
    assert extract_conditions("until core temperature 72 °C")["temperatures"][0]["location"] == "CORE"
    assert extract_conditions("fried in oil at 170-180 ºC")["temperatures"][0]["location"] == "MEDIUM"


def test_location_words_match_whole_words_only():
    # regression: "boiled" contains "oil" and was labelled MEDIUM (oil temperature)
    assert extract_conditions("Red onion, boiled 100 °C")["temperatures"][0]["location"] == "UNSPECIFIED"


def test_fahrenheit_and_decimal_comma():
    c = extract_conditions("roast at 350 °F for 1,5 h")
    assert c["temperatures"][0]["value"]["unit"] == "degF"
    assert c["durations"][0]["value"] == 90.0


def test_qualitative_heat_stays_qualitative():
    c = extract_conditions("cook over medium heat until soft")
    assert c["temperatures"] == [] and c["qualitative"][0]["status"] == "QUALITATIVE"


def test_pressure():
    assert extract_conditions("high-pressure processed at 600 MPa for 5 min")["pressure"][0]["unit"] == "MPa"


def test_no_numbers_no_conditions():
    c = extract_conditions("Red cabbage, raw")
    assert all(v == [] for v in c.values())


def test_total_duration():
    assert total_duration([])["status"] == "UNKNOWN"
    one = {"status": "MEASURED", "value": 2.0, "unit": "min", "raw": "2 min"}
    assert total_duration([one]) == one
    assert total_duration([one, one])["status"] == "UNKNOWN"


def test_months_and_years():
    d = extract_conditions("Stored 6 months at room temperature")["durations"][0]
    assert d["raw"] == "6 months" and round(d["value"] / 1440) == 183
    assert extract_conditions("aged 2 years")["durations"][0]["unit"] == "min"


def test_negative_temperatures_keep_sign():
    t = lambda s: [x["value"] for x in extract_conditions(s)["temperatures"]]  # noqa: E731
    assert t("stored, -20°C 6 months")[0]["value"] == -20.0
    assert t("frozen at −18 °C")[0]["value"] == -18.0
    r = t("stored at -18 to -20°C")[0]
    assert (r["low"], r["high"]) == (-20.0, -18.0)
    r = t("chilled at 4-6°C")[0]
    assert (r["low"], r["high"]) == (4.0, 6.0)                 # a range, not -6
    assert t("blanched at 95°C")[0]["value"] == 95.0


def test_stated_bounds_and_approximations_keep_qualifier():
    gt = extract_conditions("Pork, core temperature > 75 °C")["temperatures"][0]["value"]
    assert gt == {"status": "CENSORED", "censor": {"kind": "GT_STATED", "limit": 75.0}, "unit": "degC", "raw": "> 75 °C"}
    lt = extract_conditions("stored below 4 °C")["temperatures"][0]["value"]
    assert lt["censor"] == {"kind": "LT_STATED", "limit": 4.0} and lt["raw"] == "below 4 °C"
    ap = extract_conditions("core temperature ~ 66 °C")["temperatures"][0]["value"]
    assert ap == {"status": "MEASURED", "value": 66.0, "unit": "degC", "raw": "~ 66 °C"}
    assert extract_conditions("a temperature of around 100°C")["temperatures"][0]["value"]["raw"] == "around 100°C"
    assert extract_conditions("heated to -18 °C")["temperatures"][0]["value"]["raw"] == "-18 °C"
    assert extract_conditions("boiled 10 min 100 °C")["temperatures"][0]["value"]["status"] == "MEASURED"   # "min" = minutes
