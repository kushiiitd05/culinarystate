"""Audit export preserves UNKNOWN mass and source-data provenance; no guessed grams."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS

spec = importlib.util.spec_from_file_location("composition_audit", Path(__file__).parents[2] / "tools/s179_composition_sample_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def member(low, high, basis="TEXT_STATED_MASS"):
    return NS(mass=NS(low_g=low, high_g=high, basis=basis))


def test_unknown_member_mass_is_not_exported_as_zero_or_an_interval():
    assert audit.mass_export([member(100.,100.),member(None,None)]) == {
        "status":"UNKNOWN","low_g":None,"high_g":None,"basis":"MEMBER_MASS_UNKNOWN"}


def test_known_member_intervals_sum_without_midpoints():
    assert audit.mass_export([member(90.,110.),member(10.,20.)]) == {
        "status":"INTERVAL","low_g":100.,"high_g":130.,"basis":"SUM_OF_DECLARED_MEMBER_GRAM_INTERVALS"}


def test_empty_members_have_no_invented_lot_mass():
    assert audit.mass_export([])["status"] == "UNKNOWN"


def test_mapping_serialization_is_canonical_and_does_not_mutate():
    from types import MappingProxyType
    source={"z":MappingProxyType({"b":2,"a":1}),"tuple":(3,4)}
    assert audit.digest(source)==audit.digest({"tuple":[3,4],"z":{"a":1,"b":2}})
    assert isinstance(source["z"],type(MappingProxyType({})))
