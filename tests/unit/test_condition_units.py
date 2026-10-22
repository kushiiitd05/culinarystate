"""Step 07H: every conversion in condition_units.py is tested; Pint (if installed) is an independent oracle, never a runtime dependency."""
import math

import pytest

from culinarystate.evidence import condition_units as U

EXACT = {("time", "min"): 60, ("time", "hr"): 3600, ("time", "day"): 86400, ("time", "week"): 604800, ("pressure", "kpa"): 1e3, ("pressure", "bar"): 1e5, ("pressure", "atm"): 101325, ("length", "cm"): 1e-2, ("power", "kw"): 1e3, ("frequency", "ghz"): 1e9}


@pytest.mark.parametrize("key,f", list(EXACT.items()))
def test_exact_factors(key, f):
    assert U.DIMS[key[0]][1][key[1]] == f


def test_every_table_entry_positive_finite():
    for dim, (_, tab) in U.DIMS.items():
        for k, f in tab.items():
            assert f > 0 and math.isfinite(f), (dim, k)


def test_calendar_units_never_convertible():
    for u in ("month", "months", "year", "years", "yr"):
        assert U.time_factor(u) == ("CALENDAR", None) and u not in U.TIME
    assert U.time_factor("fortnight") == ("UNSUPPORTED", None)


def test_temperature_roundtrip_points():
    assert U.convert_temperature(0, "degC") == pytest.approx(273.15) and U.convert_temperature(32, "degF") == pytest.approx(273.15)
    assert U.convert_temperature(9, "degF", "difference") == pytest.approx(5)
    with pytest.raises(ValueError):
        U.convert_temperature(1, "rankine")


@pytest.mark.parametrize("u,exp", [("psig", ("psi", "GAUGE")), ("psia", ("psi", "ABSOLUTE")), ("psid", ("psi", "DIFFERENTIAL")), ("bar(g)", ("bar", "GAUGE")), ("kPa (a)", ("kPa", "ABSOLUTE")), ("bar", ("bar", None)), ("kPa", ("kPa", None))])
def test_pressure_unit_split(u, exp):
    assert U.split_pressure_unit(u) == exp


def test_against_pint_if_available():
    pint = pytest.importorskip("pint")
    ur = pint.UnitRegistry()
    for k, to in (("psi", "pascal"), ("atm", "pascal"), ("bar", "pascal"), ("torr", "pascal"), ("mmhg", "pascal")):
        name = {"mmhg": "mmHg"}.get(k, k)
        assert U.PRESSURE[k] == pytest.approx((1 * ur(name)).to(to).magnitude, rel=1e-6), k
    for k, to in (("min", "second"), ("hour", "second"), ("day", "second"), ("week", "second")):
        assert U.TIME[{"hour": "hours"}.get(k, k)] == pytest.approx((1 * ur(k)).to(to).magnitude)
    assert U.POWER["kw"] == pytest.approx((1 * ur("kilowatt")).to("watt").magnitude) and U.LENGTH["cm"] == pytest.approx((1 * ur("cm")).to("m").magnitude)
    assert U.convert_temperature(180, "degC") == pytest.approx(ur.Quantity(180, ur.degC).to("kelvin").magnitude)
    assert U.convert_temperature(356, "degF") == pytest.approx(ur.Quantity(356, ur.degF).to("kelvin").magnitude)
