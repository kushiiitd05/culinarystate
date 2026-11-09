"""S178 FIX-PHYS: SCI-A M7 (Q2 PROPOSED), m5 and m6 on the ascorbic-acid SIMULATE branch. SYNTHETIC TEST_ONLY fixtures only.

M7 / Q2: a Layer 2 scenario default never counts as observed: an event whose temperature or duration came from ``with_scenario``
gets G7 UNKNOWN (INPUT_UNOBSERVED_SCENARIO_ONLY) and never SIMULATE. m5: a known cut piece size is UNKNOWN
(SOLID_PIECE_NEEDS_ZONE_MODEL) until the zone model is wired. m6: no query overrides in REAL mode; TEST_ONLY fixtures only in pytest.
"""
from __future__ import annotations

import random
import sys

import pytest

from culinarystate.mechanism import simulate_branch as SB
from tests.unit.test_s178_aasim_branch import (ING, _mut, _set, event, item, make_artifacts, make_branch, make_config,
                                               make_gate, run)

SCEN = {"scenarios": {b: {"bath_c": t, "duration_min": d, "bases": {"bath_c": "SD-001", "duration_min": "KGE-1"}}
                      for b, t, d in (("GENTLE", 85.0, 10.0), ("TYPICAL", 90.0, 20.0), ("INTENSE", 98.0, 40.0))}}


def test_m7_reviewer_case_a_scenario_filled_temperature_never_simulates():
    br = make_branch()
    ev = SB.AAEvent.with_scenario(event(t=None, t_basis=None), SCEN)
    assert ev.temperature_C.value == (85.0, 98.0) and ev.temperature_C.basis == "ASSUMED_DEFAULT:SD-001"
    assert ev.scenario_only_inputs() == ("temperature",)
    out = run(br, ev)
    assert not out.simulated and out.engine_route in ("UNKNOWN", "QUALITATIVE")
    assert SB.UNOBSERVED_SCENARIO in out.reasons and "SCENARIO_ONLY_INPUT:temperature" in out.reasons
    assert "retention_interval" not in out.as_item()
    # the same event with the temperature stated in the text simulates (the fixture branch is complete)
    assert run(br, event(t=95.0)).simulated


def test_m7_any_non_layer1_basis_is_unobserved():
    for basis in ("ASSUMED_DEFAULT:SD-001", "SD-001", "KGE-007576", "MODEL_DERIVED", None):
        ev = event(t=95.0, t_basis=basis)
        if basis is None:
            assert ev.temperature_C.basis is None or ev.scenario_only_inputs() == ("temperature",)
        else:
            assert ev.scenario_only_inputs() == ("temperature",), basis
    assert event(t=95.0, t_basis="PHYSICAL_DEFINITION").scenario_only_inputs() == ()
    assert event(t=95.0, d=20.0, t_basis="TEXT_STATED", d_basis="TEXT_STATED").scenario_only_inputs() == ()


def test_m7_property_unknown_or_scenario_filled_never_routes_to_simulate():
    """The S178 AASIM 400-case property test extended to the with_scenario path: each of nine inputs known or UNKNOWN, and an
    UNKNOWN temperature / duration is (at random) filled from a Layer 2 scenario. SIMULATE iff every input is known from Layer 1."""
    rng = random.Random(20261109)
    base = make_artifacts()
    branches = {True: make_branch(arts=base),
                False: make_branch(arts=_mut(base, _set("params.0.verification", {"status": "UNVERIFIED"})))}
    sims = filled = 0
    for _ in range(400):
        known = {k: rng.random() < 0.8 for k in ("t", "d", "medium", "ing", "gates", "lot", "presence", "prior", "param")}
        fill = rng.random() < 0.5
        br = branches[known["param"]]
        ev = event(t=95.0 if known["t"] else None, d=25.0 if known["d"] else None,
                   medium="STEAM" if known["medium"] else None, ing=ING if known["ing"] else None)
        if fill and not (known["t"] and known["d"]):
            ev = SB.AAEvent.with_scenario(ev, SCEN)
            filled += 1
        gates = ({"presence": "PRESENT" if known["presence"] else "UNKNOWN",
                  "lot_context": "SINGLE_MEMBER" if known["lot"] else "NO_LOT"} if known["gates"] else None)
        it = item(ingredient_id=ev.ingredient_id, gates=gates, prior_process=[] if known["prior"] else ["HEAT"])
        out = run(br, ev, it)
        expect = all(known.values())  # a scenario fill never makes an event simulatable
        assert out.simulated == expect, (known, fill, out.reasons)
        if not expect:
            assert out.engine_route != "SIMULATE" and out.status == "NOT_SIMULATED"
        if ev.scenario_only_inputs():
            assert not out.simulated
        sims += out.simulated
    assert 0 < sims < 400 and filled > 50


def test_m5_a_known_piece_size_needs_the_zone_model():
    br = make_branch()
    out = run(br, event(piece_size_class="DICED"))
    assert not out.simulated and SB.SOLID_PIECE in out.reasons and out.gate.verdict == "UNKNOWN"
    l1 = {"temperature_profile": {"value": "95", "status": "MEASURED", "basis": "TEXT_STATED", "span_id": "C:0-4"},
          "duration": {"value": "30", "status": "MEASURED", "basis": "TEXT_STATED", "span_id": "C:5-9"},
          "medium": {"value": "STEAM", "status": "MEASURED", "basis": "PROCESS_DEFINITION"},
          "piece_size_class": {"value": "SLICED", "status": "MEASURED", "basis": "CUT_HISTORY"}}
    ev = SB.AAEvent.from_layer1("E1", "PROC-000022", ING, l1)
    assert ev.piece_size_class == "SLICED"
    assert SB.AAEvent.with_scenario(ev, SCEN).piece_size_class == "SLICED"
    assert not run(br, ev).simulated


def test_m6_query_overrides_are_refused_in_real_mode():
    with pytest.raises(SB.SimulateBranchError):
        SB.SimulateBranch(make_artifacts(test_only=False), make_gate(), make_config())
    SB.SimulateBranch.from_repo()  # the REAL branch without overrides still builds (and refuses everything)


def test_m6_test_only_fixtures_need_a_pytest_process(monkeypatch):
    SB.TestOnlyFixtures("inside pytest")
    monkeypatch.delitem(sys.modules, "pytest")
    with pytest.raises(SB.SimulateBranchError):
        SB.TestOnlyFixtures("outside a test run")


def test_branch_version_is_bumped():
    assert SB.VERSION == "simulate-branch-0.2.0-draft" and SB.VERSION_V01 == "simulate-branch-0.1.0-draft"
