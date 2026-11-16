"""S180 freeze step 2: typed Event IR fields and the "alternatives are not conjunctions" invariant.

Two CR-25 event fields had no typed home on ``EventCandidate``: ``alternative_group``
(which binds mutually exclusive events) and ``condition_profile_id``. Without the first,
"A or B" could be committed as "A and B" and nothing in V4 would say so; lineage vNext
only raises the diagnostic flag ``VNEXT_ALTERNATIVE_SKIPPED`` at parse time.

The invariant is a conjunction check, not an exclusivity repair: two events that declare
the same ``alternative_group`` must not both produce committed state. V4 never repairs a
graph, so a violation is reported and the graph is left alone.

Synthetic graphs only.
"""
from __future__ import annotations

from culinarystate.extraction import invariants as inv
from culinarystate.extraction.interfaces import (
    EntityCandidate, EventCandidate, EventGraph, SourceText, StageConfig,
)

RAW = "Add the lemon juice or the vinegar, then simmer."
CFG = StageConfig(rung_id="A", params={"v": 0}, claim_route="INFERRED_RULE",
                  annotated_labels=frozenset({"FOOD_MENTION"}))
SRC = SourceText.from_raw("SYN-ALT", RAW)


def ev(eid, order, **kw):
    return EventCandidate(eid, order, **kw)


def ent(nid, etype="INTERMEDIATE", lifecycle="ACTIVE", parents=(), by=None):
    return EntityCandidate(nid, etype, lifecycle, tuple(parents), by)


def graph(events, entities):
    return EventGraph(SRC.text_id, SRC.sha256, tuple(events), tuple(entities), (), {},
                      CFG.provenance("build_events"))


# --- typed fields exist and default to None (backward compatible) ------------------

def test_event_candidate_carries_alternative_group_and_condition_profile():
    e = ev("E1", (0, 0), alternative_group="ALT-1", condition_profile_id="CP-7")
    assert e.alternative_group == "ALT-1"
    assert e.condition_profile_id == "CP-7"


def test_both_new_fields_default_to_none():
    e = ev("E1", (0, 0))
    assert e.alternative_group is None
    assert e.condition_profile_id is None


def test_event_candidate_stays_frozen():
    e = ev("E1", (0, 0), alternative_group="ALT-1")
    try:
        e.alternative_group = "ALT-2"
    except Exception:
        return
    raise AssertionError("EventCandidate must stay immutable")


def test_blank_alternative_group_is_rejected():
    for bad in ("", "   "):
        try:
            ev("E1", (0, 0), alternative_group=bad)
        except Exception:
            continue
        raise AssertionError(f"blank alternative_group {bad!r} must be rejected")


# --- the invariant ----------------------------------------------------------------

def _codes(report):
    return {i.code for i in report.issues}


def test_two_committed_members_of_one_alternative_group_fail():
    """"A or B" committed as "A and B" is a conjunction error."""
    g = graph(
        [ev("E1", (0, 0), produces=("N1",), alternative_group="ALT-1"),
         ev("E2", (0, 1), produces=("N2",), alternative_group="ALT-1")],
        [ent("N1", by="E1"), ent("N2", by="E2")],
    )
    r = inv.v4_invariants(g)
    assert "ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION" in _codes(r)


def test_one_committed_member_passes():
    g = graph(
        [ev("E1", (0, 0), produces=("N1",), alternative_group="ALT-1")],
        [ent("N1", by="E1")],
    )
    r = inv.v4_invariants(g)
    assert "ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION" not in _codes(r)


def test_events_in_different_groups_do_not_interact():
    g = graph(
        [ev("E1", (0, 0), produces=("N1",), alternative_group="ALT-1"),
         ev("E2", (0, 1), produces=("N2",), alternative_group="ALT-2")],
        [ent("N1", by="E1"), ent("N2", by="E2")],
    )
    r = inv.v4_invariants(g)
    assert "ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION" not in _codes(r)


def test_ungrouped_events_are_never_flagged():
    g = graph(
        [ev("E1", (0, 0), produces=("N1",)), ev("E2", (0, 1), produces=("N2",))],
        [ent("N1", by="E1"), ent("N2", by="E2")],
    )
    r = inv.v4_invariants(g)
    assert "ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION" not in _codes(r)


def test_group_member_that_commits_nothing_is_not_a_conjunction():
    """A member with no produces/consumes/discards is declared but not committed."""
    g = graph(
        [ev("E1", (0, 0), produces=("N1",), alternative_group="ALT-1"),
         ev("E2", (0, 1), alternative_group="ALT-1")],
        [ent("N1", by="E1")],
    )
    r = inv.v4_invariants(g)
    assert "ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION" not in _codes(r)


def test_three_members_report_once_per_group_and_name_the_members():
    g = graph(
        [ev("E1", (0, 0), produces=("N1",), alternative_group="ALT-1"),
         ev("E2", (0, 1), produces=("N2",), alternative_group="ALT-1"),
         ev("E3", (0, 2), produces=("N3",), alternative_group="ALT-1")],
        [ent("N1", by="E1"), ent("N2", by="E2"), ent("N3", by="E3")],
    )
    r = inv.v4_invariants(g)
    hits = [i for i in r.issues if i.code == "ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION"]
    assert len(hits) == 1, "one issue per group, not per pair"
    assert hits[0].path == "ALT-1"
    for eid in ("E1", "E2", "E3"):
        assert eid in hits[0].message


def test_consuming_members_also_count_as_committed():
    g = graph(
        [ev("E0", (0, 0), produces=("N1", "N2")),
         ev("E1", (0, 1), consumes=("N1",), alternative_group="ALT-1"),
         ev("E2", (0, 2), consumes=("N2",), alternative_group="ALT-1")],
        [ent("N1", by="E0"), ent("N2", by="E0")],
    )
    r = inv.v4_invariants(g)
    assert "ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION" in _codes(r)


# --- the invariant is no longer listed as open ------------------------------------

def test_alternatives_invariant_is_not_in_open_invariants():
    assert not any("ALTERNATIVE" in name for name in inv.OPEN_INVARIANTS)
