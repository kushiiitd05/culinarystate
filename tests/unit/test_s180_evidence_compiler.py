"""S180 freeze steps 3-4: query-specific evidence compiler and Claim Packet.

RAG packet v2 hardcoded five compatibility keys (ingredient, process, salt, acid, lipid).
The freeze requires the canonical schema to carry *all* SSOT compatibility axes, with
unavailable fields staying UNKNOWN, and the axes relevant to the target/question selected
*before* retrieval and applicability checking.

The axis list is never duplicated in code: it is read from
``registry/rag/compatibility_axes_v1.csv``, the single source of truth created on 15 Nov.
"""
from __future__ import annotations

import pytest

from culinarystate.composition import claim_packet as CP
from culinarystate.composition import evidence_compiler as EC
from culinarystate.composition.state_full import StateBuilder

TOMATO_A = "Boil the tomatoes in water for 20 minutes."
TOMATO_D = "Mix the tomatoes, water, salt, vinegar and oil.\nBoil the mixture for 20 minutes."


@pytest.fixture(scope="module")
def B():
    return StateBuilder()


def _state(B, text, step):
    return next(x for x in B.build(text) if x["food"] == "tomato" and x["step"] == step)


# --- the axis registry is the single source of truth ------------------------------

def test_axes_load_from_the_registry_csv():
    axes = EC.load_axes()
    assert len(axes) == 13
    assert [a.axis_no for a in axes] == list(range(1, 14))


def test_registry_marks_two_axes_schema_only():
    """Axes 7 and 9 left this set on 15 Nov.

    7: the FDA/CFSAN 2003 pH table was already in the repo. 9: ``Q.piece_size_class`` was already
    derived from cut history and only needed wiring. 8 (a_w / moisture) has no producer and 12
    (measurement method) has no data, so both stay SCHEMA_ONLY.
    """
    schema_only = {a.axis_no for a in axes_by_status("SCHEMA_ONLY")}
    assert schema_only == {8, 12}


def axes_by_status(status):
    return [a for a in EC.load_axes() if a.status == status]


def test_schema_only_axes_carry_an_unknown_reason():
    for a in axes_by_status("SCHEMA_ONLY"):
        assert a.unknown_reason, f"axis {a.axis_no} must say why it is absent"


def test_implemented_axis_names_match_the_compatibility_module():
    from culinarystate.retrieval import compatibility as C
    names = {a.code_axis_name for a in EC.load_axes() if a.code_axis_name}
    assert names == set(C.AXES)


def test_hard_exclusion_axes_are_1_3_10_11():
    assert {a.axis_no for a in EC.load_axes() if a.hard_exclusion} == {1, 3, 10, 11}


# --- axis selection happens before retrieval --------------------------------------

def test_question_kinds_are_a_closed_vocabulary():
    assert "RETENTION_NUMERIC" in EC.QUESTION_AXES
    with pytest.raises(EC.CompilerError):
        EC.select_axes("vitc", "NOT_A_QUESTION_KIND")


def test_selection_is_a_subset_of_the_thirteen():
    for kind in EC.QUESTION_AXES:
        chosen = EC.select_axes("vitc", kind)
        assert chosen, f"{kind} selected no axes"
        assert set(chosen) <= set(range(1, 14))


def test_retention_question_selects_the_hard_exclusion_axes():
    chosen = set(EC.select_axes("vitc", "RETENTION_NUMERIC"))
    assert {1, 3, 10, 11} <= chosen, "a numeric retention claim cannot skip a hard-exclusion axis"


def test_composition_question_does_not_pull_in_process_conditions():
    chosen = set(EC.select_axes("vitc", "COMPOSITION"))
    assert 4 not in chosen and 5 not in chosen


def test_flavour_question_is_selectable_but_unserviceable():
    """The molecule set exists (313 ING) but is not wired; the answer is UNKNOWN, not silence."""
    chosen = EC.select_axes("vitc", "FLAVOUR")
    assert chosen


# --- compiled evidence ------------------------------------------------------------

def test_every_selected_axis_appears_in_the_output(B):
    s = _state(B, TOMATO_A, 1)
    out = EC.compile_evidence(s, "vitc", "RETENTION_NUMERIC")
    chosen = EC.select_axes("vitc", "RETENTION_NUMERIC")
    assert set(out["compatibility"]) == {EC.axis_key(n) for n in chosen}


def test_schema_only_axes_are_unknown_with_their_registry_reason(B):
    s = _state(B, TOMATO_A, 1)
    out = EC.compile_evidence(s, "vitc", "RETENTION_NUMERIC")
    method = out["compatibility"].get(EC.axis_key(12))
    assert method is not None, "an unavailable axis must still be present in the schema"
    assert method["status"] == "UNKNOWN"
    assert method["reason"] == "MEAS_HAS_3_ROWS_PE_METHOD_NULL"


def test_ph_axis_is_filled_for_tomato_with_its_source(B):
    """Axis 7 is no longer schema-only: the FDA/CFSAN 2003 table resolves tomato EXACTly."""
    s = _state(B, TOMATO_A, 1)
    ph = EC.compile_evidence(s, "vitc", "RETENTION_NUMERIC")["compatibility"][EC.axis_key(7)]
    assert ph["status"] == "EVALUABLE"
    assert (ph["ph_low"], ph["ph_high"]) == (4.3, 4.9)
    assert ph["acidity"] == "INCONCLUSIVE_SPANS_THRESHOLD"
    assert "FDA" in ph["source"] and len(ph["source_sha256"]) == 64
    assert ph["verify_status"] == "UNVERIFIED_CROSSWALK_AI_DRAFTED"


def test_compiler_never_reports_a_schema_only_axis_as_match(B):
    s = _state(B, TOMATO_A, 1)
    out = EC.compile_evidence(s, "vitc", "RETENTION_NUMERIC")
    for n in (7, 8, 9, 12):
        cell = out["compatibility"].get(EC.axis_key(n))
        if cell is not None:
            assert cell["status"] != "MATCH"


def test_tomato_a_keeps_its_direct_route_and_evidence(B):
    s = _state(B, TOMATO_A, 1)
    out = EC.compile_evidence(s, "vitc", "RETENTION_NUMERIC")
    assert out["route"] == "DIRECT"
    assert out["evidence_ids"] == ["EVD-002765"]


def test_tomato_d_unknown_route_lists_near_evidence_only(B):
    s = _state(B, TOMATO_D, 2)
    out = EC.compile_evidence(s, "vitc", "RETENTION_NUMERIC")
    assert out["route"] == "UNKNOWN"
    assert out["evidence_ids"] == []
    assert out["near_evidence_ids"] == ["EVD-002765"]


def test_unknown_axes_are_listed_not_dropped(B):
    s = _state(B, TOMATO_D, 2)
    out = EC.compile_evidence(s, "vitc", "RETENTION_NUMERIC")
    assert out["unknown_axes"], "UNKNOWN is neutral but never silent"
    for key in out["unknown_axes"]:
        assert out["compatibility"][key]["status"] == "UNKNOWN"


# --- Claim Packet -----------------------------------------------------------------

REQUIRED_FIELDS = ("allowed_claims", "required_caveats", "forbidden_claims", "evidence_ids",
                   "compatibility", "max_allowed_precision", "unknown_reasons")


def test_claim_packet_has_every_required_field(B):
    s = _state(B, TOMATO_A, 1)
    p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
    for f in REQUIRED_FIELDS:
        assert f in p, f"Claim Packet must carry {f}"


def test_direct_route_allows_a_cited_number(B):
    s = _state(B, TOMATO_A, 1)
    p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
    assert "NUMERIC_FROM_CITED_EVIDENCE" in p["allowed_claims"]
    assert p["evidence_ids"] == ["EVD-002765"]


def test_unknown_route_forbids_numeric_transfer(B):
    s = _state(B, TOMATO_D, 2)
    p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
    assert "NUMERIC_FROM_CITED_EVIDENCE" not in p["allowed_claims"]
    assert "NUMERIC_TRANSFER_FROM_NEAR_EVIDENCE" in p["forbidden_claims"]


def test_max_allowed_precision_never_exceeds_the_source(B):
    """EVD-002765 reports 95.0%, one decimal, so one decimal is the cap."""
    s = _state(B, TOMATO_A, 1)
    p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
    assert p["max_allowed_precision"] == 1


def test_no_evidence_means_no_precision_budget(B):
    s = _state(B, TOMATO_D, 2)
    p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
    assert p["max_allowed_precision"] is None


def test_unknown_reasons_are_plain_and_non_empty(B):
    s = _state(B, TOMATO_D, 2)
    p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
    assert p["unknown_reasons"]
    for key, reason in p["unknown_reasons"].items():
        assert reason and isinstance(reason, str)


def test_abstain_is_always_allowed(B):
    for text, step in ((TOMATO_A, 1), (TOMATO_D, 2)):
        s = _state(B, text, step)
        p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
        assert "ABSTAIN" in p["allowed_claims"], "abstaining is never forbidden"


def test_packet_is_a_new_object_and_does_not_mutate_the_state(B):
    s = _state(B, TOMATO_A, 1)
    before = repr(s)
    CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
    assert repr(s) == before


def test_claim_packet_agrees_with_the_legacy_allowed_claim(B):
    """Step 4 extends allowed_claim; it must not contradict rag_packet v2."""
    from culinarystate.composition import rag_packet as RP
    for text, step in ((TOMATO_A, 1), (TOMATO_D, 2)):
        s = _state(B, text, step)
        legacy = RP.packet(s, "vitc")["allowed_claim"]
        p = CP.claim_packet(s, "vitc", "RETENTION_NUMERIC")
        if legacy == "NUMERIC_FROM_CITED_EVIDENCE_ONLY":
            assert "NUMERIC_FROM_CITED_EVIDENCE" in p["allowed_claims"]
        if legacy == "QUALITATIVE_ONLY_NO_NUMERIC_TRANSFER":
            assert "NUMERIC_FROM_CITED_EVIDENCE" not in p["allowed_claims"]
