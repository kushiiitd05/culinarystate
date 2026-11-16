"""S180: wire compatibility axis 9 (geometry / size) into the evidence compiler.

The registry lists axis 9 as `SCHEMA_ONLY` with reason `NOT_WIRED_TO_COMPATIBILITY`, although State
v2 already computes ``Q.piece_size_class`` from cut history. Wiring is the whole task: nothing new is
produced and nothing is estimated.

The one thing this must not do is report a **match**. Evidence rows carry no geometry field, so the
row side of axis 9 is UNKNOWN, and the freeze invariant "evidence-context UNKNOWN cannot be treated as
MATCH" forbids calling a one-sided axis EVALUABLE. A known query size with an unknown row size is
``QUERY_ONLY``, which is a third thing, not a pass and not a missing value.
"""
from __future__ import annotations

import pytest

from culinarystate.composition import evidence_compiler as EC
from culinarystate.composition.state_full import StateBuilder

DICED = "Dice the onion. Fry the diced onion in oil for 5 minutes."
PLAIN = "Boil the whole potatoes in water for 20 minutes."


def _state(text: str, *, want_size: bool):
    for state in StateBuilder().build(text):
        cell = state["Q"].get("piece_size_class") or {}
        if bool(cell.get("v")) is want_size:
            return state
    pytest.skip(f"no step with want_size={want_size}")


def test_registry_now_marks_axis_9_wired():
    axis = EC.axes_by_no()[9]
    assert axis.status == "IMPLEMENTED_IN_COMPILER"
    assert axis.code_axis_name in (None, "")


def test_known_cut_history_is_query_only_never_a_match():
    cell = EC.geometry_axis_cell(_state(DICED, want_size=True))
    assert cell["status"] == "QUERY_ONLY"
    assert cell["reason"] == "NO_ROW_GEOMETRY_FIELD"
    assert cell["status"] not in ("EVALUABLE", "MATCH", "EXACT")


def test_query_only_cell_carries_the_value_and_its_basis():
    cell = EC.geometry_axis_cell(_state(DICED, want_size=True))
    assert cell["piece_size_class"] == "DICED"
    assert cell["basis"] == "CUT_HISTORY"


def test_absent_cut_history_is_unknown_with_the_state_reason():
    cell = EC.geometry_axis_cell(_state(PLAIN, want_size=False))
    assert cell["status"] == "UNKNOWN"
    assert cell["reason"]
    assert "piece_size_class" not in cell


def test_every_cell_names_its_axis_and_owner_step():
    for text, want in ((DICED, True), (PLAIN, False)):
        cell = EC.geometry_axis_cell(_state(text, want_size=want))
        assert cell["axis"] == EC.axes_by_no()[9].axis
        assert cell["owner_step"]
        assert cell["hard_exclusion"] is False


def test_compile_evidence_routes_axis_9_through_the_new_cell():
    state = _state(DICED, want_size=True)
    out = EC.compile_evidence(state, "vitc", "PROCESS_EFFECT")
    key = EC.axis_key(9)
    assert key in out["compatibility"]
    assert out["compatibility"][key]["status"] == "QUERY_ONLY"


def test_query_only_is_not_counted_as_an_unknown_axis():
    """QUERY_ONLY is information. It must not be swept into unknown_axes as if nothing were known."""
    state = _state(DICED, want_size=True)
    out = EC.compile_evidence(state, "vitc", "PROCESS_EFFECT")
    assert EC.axis_key(9) not in out["unknown_axes"]


def test_unwired_axes_still_report_their_registry_reason():
    """Wiring 9 must not silently mark 8 or 12 as done."""
    state = _state(DICED, want_size=True)
    for n in (8, 12):
        assert EC.axes_by_no()[n].status == "SCHEMA_ONLY"
