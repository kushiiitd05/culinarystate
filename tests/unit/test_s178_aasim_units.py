"""S178 aa-fit-sim, T5-C07-R5: kinetic unit rows (min^-1, s^-1, kJ/mol, kcal/mol) and exact conversions.

Draft registry only (``registry/kinetic_units_v1_DRAFT.csv``); nothing is appended to ``ledgers/data/UNIT.jsonl``.
Values below are arithmetic checks of definitions, not measurements.
"""
from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from culinarystate.mechanism import kinetic_unit_registry as K
from culinarystate.simulation.kinetics import units as U
from tests.fixtures import form_param_val_v1_fixtures as FX

ROWS = K.read_rows()
UNIT_SCHEMA = Path(K.ROOT) / "ledgers" / "schemas" / "UNIT.schema.json"


def test_csv_file_is_the_builders_output_and_self_consistent() -> None:
    assert K.CSV_PATH.read_text(encoding="utf-8") == K.csv_text()
    assert K.check_rows(ROWS) == []
    assert [r["proposed_key"] for r in ROWS] == [f"KU-{n:03d}" for n in range(1, 12)]


@pytest.mark.parametrize("unit, factor", [("s^-1", Fraction(1)), ("min^-1", Fraction(1, 60)),
                                          ("h^-1", Fraction(1, 3600)), ("d^-1", Fraction(1, 86400)),
                                          ("1/min", Fraction(1, 60)), ("per hour", Fraction(1, 3600)),
                                          ("J/mol", Fraction(1)), ("kJ/mol", Fraction(1000)),
                                          ("kJ mol-1", Fraction(1000))])
def test_conversion_factors_are_exact_rationals(unit: str, factor: Fraction) -> None:
    r = K.resolve(unit)
    assert r.verdict == U.CONSISTENT and r.factor_to_si == factor and not r.affine


def test_rate_constant_conversions_round_trip_exactly() -> None:
    assert K.to_si(Fraction(3, 5), "min^-1") == Fraction(1, 100)                 # 0.6 per min = 0.01 per s
    assert K.to_si(7, "h^-1") == Fraction(7, 3600)
    assert K.to_si(60, "min^-1") == K.to_si(1, "s^-1") == 1
    assert K.to_si(Fraction(1, 60), "s^-1") * 60 == Fraction(1)
    assert K.to_si(Fraction("2.5"), "kJ/mol") == 2500


def test_kcal_is_ambiguous_until_the_calorie_is_declared() -> None:
    r = K.resolve("kcal/mol")
    assert r.verdict == U.UNKNOWN and r.detail == "CALORIE_CONVENTION_UNDECLARED" and r.factor_to_si is None
    assert K.to_si(10, "kcal/mol") is None
    assert K.to_si(1, "kcal/mol", calorie="TH") == 4184
    assert K.to_si(1, "kcal/mol", calorie="IT") == Fraction(20934, 5)             # 4186.8 exactly
    assert K.to_si(1, "kcal_th/mol") == 4184 and K.to_si(1, "kcal_IT/mol") == Fraction(41868, 10)
    assert K.to_si(1, "kcal_th/mol") == K.to_si(Fraction("4.184"), "kJ/mol")      # 1 kcal_th = 4.184 kJ, no rounding
    assert K.to_si(1, "kcal_IT/mol") != K.to_si(1, "kcal_th/mol")
    with pytest.raises(ValueError):
        K.resolve("kcal/mol", calorie="LATE")


def test_unknown_or_missing_unit_is_unknown_never_a_default() -> None:
    for bad in (None, "", "   ", "UNKNOWN", "furlong/fortnight", "mg/g/min", "kcal"):
        r = K.resolve(bad)
        assert r.verdict == U.UNKNOWN and r.factor_to_si is None, bad
    assert K.to_si(5, "furlong") is None


def test_degC_is_affine_and_converts_by_the_exact_offset() -> None:
    r = K.resolve("degC")
    assert r.affine and r.factor_to_si is None and r.dimension == U.dimension("TEMPERATURE")
    assert K.to_si(90, "degC") is None                                            # no multiplicative factor
    assert K.to_kelvin(90, "degC") == Fraction(36315, 100) and K.to_kelvin(Fraction(1, 2), "K") == Fraction(1, 2)
    assert K.to_kelvin(0, "°C") == Fraction(27315, 100)
    with pytest.raises(ValueError):
        K.to_kelvin(1, "degF")


def test_aliases_are_unique_and_collisions_are_refused() -> None:
    assert K._index(ROWS)                                                          # builds without a collision
    bad = copy.deepcopy(ROWS)
    bad[1]["aliases"] += "|s^-1"
    with pytest.raises(ValueError):
        K._index(bad)
    assert any("DUPLICATE_KEY" in p for p in K.check_rows(bad[:1] + bad[:1]))


def test_registry_agrees_with_units_py_wherever_units_py_parses_the_unit() -> None:
    parsed = [r for r in ROWS if r["units_py_parses"] == "YES"]
    assert {r["canonical_name"] for r in parsed} >= {"s^-1", "min^-1", "h^-1", "d^-1", "J/mol", "kJ/mol", "K", "degC"}
    for r in parsed:
        p = U.parse_unit(r["canonical_name"])
        assert p.dimension == U.dimension(r["dimension_expr"])
        if r["si_factor_exact"]:
            n, d = r["si_factor_exact"].split("/")
            assert p.factor_to_si == Fraction(int(n), int(d)), r["canonical_name"]
    # units.py has no calorie token: the registry carries the factor instead (a finding, not edited here)
    assert [r["canonical_name"] for r in ROWS if r["units_py_parses"] == "NO"] == ["kcal_th/mol", "kcal_IT/mol", "kcal/mol"]
    for tok in ("kcal", "kcal_th"):
        with pytest.raises(U.UnitError):
            U.parse_unit(f"{tok}/mol")


def test_kcal_rows_are_flagged_as_unsourced() -> None:
    for r in ROWS:
        if "kcal" in r["canonical_name"]:
            assert r["needs_source"] == "True" and r["source_status"] == "SOURCE_UNVERIFIED_AGENT_RECALLED"


# ----------------------------------------------------------------------------- PARAM units resolve
def _param(slot: str, value: float, unit: str, *, t_unit: str | None = "K") -> dict:
    p = FX.param(1, form_id="FORM-900004", slot_symbol=slot, value=value, unit=unit)
    p["T_ref"] = None if t_unit is None else {"status": "MEASURED", "value": 360.0, "unit": t_unit, "raw": FX.Z}
    return p


@pytest.mark.parametrize("unit", ["1/s", "s^-1", "1/min", "min^-1", "1/h", "h^-1", "per day", "1/d"])
def test_every_rate_constant_unit_in_the_registry_resolves_for_a_rate_slot(unit: str) -> None:
    assert K.param_unit_issues(_param("k_ref", 1.0, unit), "TIME^-1") == []


@pytest.mark.parametrize("unit, calorie, ok", [("J/mol", None, True), ("kJ/mol", None, True), ("kcal/mol", "TH", True),
                                                ("kcal/mol", "IT", True), ("kcal/mol", None, False),
                                                ("kJ", None, False), ("1/min", None, False)])
def test_activation_energy_units_resolve_with_the_slot_dimension(unit: str, calorie: str | None, ok: bool) -> None:
    got = K.param_unit_issues(_param("Ea", 1.0, unit), "ENERGY*AMOUNT^-1", calorie=calorie)
    assert (got == []) is ok, got


def test_concentration_tokens_do_not_pass_as_a_first_order_unit_and_degc_is_not_a_t_ref() -> None:
    assert any(i.startswith("PARAM_UNIT_UNRESOLVED") for i in K.param_unit_issues(_param("k_ref", 1.0, "mg/g/min"),
                                                                                    "TIME^-1"))
    assert K.param_unit_issues(_param("k_ref", 1.0, "1/min", t_unit="degC"), "TIME^-1") == ["PARAM_T_REF_NOT_KELVIN"]
    assert K.param_unit_issues(_param("k_ref", 1.0, "1/min", t_unit=None), "TIME^-1") == []


def test_unknown_value_has_no_unit_to_resolve() -> None:
    p = _param("k_ref", 1.0, "1/min")
    p["value"] = {"status": "UNKNOWN", "value": None, "low": None, "high": None}
    assert K.param_unit_issues(p, "TIME^-1") == []


def test_wired_to_the_param_fixtures_of_the_simulate_branch() -> None:
    """Every PARAM unit the TEST_ONLY artifacts use (and the real draft FORM slots' dimensions) resolves."""
    from tests.unit import test_s178_aasim_branch as T
    arts = T.make_artifacts()
    form = arts.forms_by_id[arts.form_id]
    slots = {s["symbol"]: s["dimension"] for s in form["parameter_slots"]}
    for p in arts.params:
        assert K.param_unit_issues(p, slots[p["slot_symbol"]]) == [], p["slot_symbol"]


# ----------------------------------------------------------------------------- UNIT ledger: not touched, and why a schema change is needed
def _validator(delta: bool) -> Draft202012Validator:
    s = json.loads(UNIT_SCHEMA.read_text(encoding="utf-8"))
    s = {k: v for k, v in s.items() if k != "$id"}
    if delta:
        s["properties"]["unit_type"]["enum"] += K.SCHEMA_DELTA["unit_type"]
        s["properties"]["dimension"]["enum"] += K.SCHEMA_DELTA["dimension"]
    return Draft202012Validator(s)


def test_unit_records_validate_only_with_the_additive_enum_change() -> None:
    recs = K.unit_records(75, rows=ROWS)
    assert [r["id"] for r in recs][0] == "UNIT-000075" and len(recs) == len(ROWS)
    ok, strict = _validator(True), _validator(False)
    assert all(not list(ok.iter_errors(r)) for r in recs), [list(ok.iter_errors(r))[:1] for r in recs]
    failing = [r["canonical_name"] for r in recs if list(strict.iter_errors(r))]
    assert "kcal_th/mol" in failing and "min^-1" in failing and "J/mol" in failing
    assert "K" not in [r["canonical_name"] for r in recs if r["dimension"] != "TEMPERATURE"]
    # the schema delta is only enum additions
    assert K.SCHEMA_DELTA["unit_type"] == ["KINETIC"] and set(K.SCHEMA_DELTA["dimension"]) == {"RATE_PER_TIME",
                                                                                              "ENERGY_PER_AMOUNT"}
    cal = [r for r in recs if r["canonical_name"].startswith("kcal_")]
    assert {c["conventions"][0]["locale"] for c in cal} == {"CALORIE_TH", "CALORIE_IT"}
    assert [c["conventions"][0]["si_value"]["value"] for c in cal] == [4184.0, 4186.8]


def test_module_writes_only_its_own_registry_file() -> None:
    src = Path(K.__file__).read_text(encoding="utf-8")
    assert src.count(".write_text(") == 1 and "UNIT.jsonl" not in src.replace("``ledgers/data/UNIT.jsonl``", "")
