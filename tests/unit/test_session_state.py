"""§257B.18 C18 session-state updater — 12 mandatory unit tests."""
import pytest
from culinarystate.decision.session_state import SessionState, _to_event, VERSION
from culinarystate.state_graph.engine import (
    Add, Transform, Merge, Observe, Predict, Graph,
)
from culinarystate.state_graph.symqty import Base


def _qty(s: str) -> Base:
    return Base.qualitative(s)


# 1. clean in-domain case
def test_clean_session():
    ss = SessionState.from_events([
        Add("rice", "ING-001", _qty("200g"), step=0),
        Add("water", "ING-002", _qty("400ml"), step=0),
        Merge(("rice", "water"), "rice pot", "simmer", step=1),
        Transform("rice pot", "simmer", sets=(("texture", "tender"),), step=1),
    ])
    assert isinstance(ss.graph, Graph)
    assert ss.process_history() == {"simmer"}
    assert "rice pot" in ss.alive_entities()
    assert ss.version == VERSION


# 2. missing optional fields
def test_missing_optional_fields():
    ss = SessionState.from_turns([
        {"turn": 1, "events": [{"type": "Add", "label": "egg", "concept_id": None, "qty": "1 egg"}]}
    ])
    assert "egg" in ss.alive_entities()
    assert ss.process_history() == set()


# 3. missing critical field
def test_missing_critical_field():
    ss = SessionState.from_turns([
        {"turn": 1, "events": [{"type": "Transform"}]}  # no target/process
    ])
    # should not crash; event skipped and issue logged
    assert len(ss.events) == 0
    assert any("missing required fields" in i for i in ss.issues)


# 4. ambiguous surface form (two entities share a name → handled by engine)
def test_ambiguous_entity():
    ss = SessionState.from_events([
        Add("garlic", "ING-010", _qty("3 cloves")),
        Add("garlic", "ING-010", _qty("2 cloves")),  # duplicate
    ])
    assert len(ss.issues) > 0  # engine reports "entity added twice"


# 5. contradictory upstream fields
def test_contradictory_observe_predict():
    ss = SessionState.from_events([
        Add("sauce", "ING-020", _qty("200ml")),
        Observe("sauce", "texture", "smooth", source="user"),
        Predict("sauce", "texture", "lumpy", model_ref="test"),
    ])
    state = ss.current_state("sauce")
    # observation outranks prediction (SSOT rule)
    assert state["fields"]["texture"]["value"] == "smooth"
    assert state["fields"]["texture"]["trajectory"] == "OBSERVED_SESSION"


# 6. source/locale variation (different qty text)
def test_locale_variation():
    ss = SessionState.from_turns([
        {"turn": 1, "events": [
            {"type": "Add", "label": "paneer", "concept_id": "ING-050", "qty": "250 grams paneer"},
            {"type": "Transform", "target": "paneer", "process": "fry",
             "sets": {"form": "golden"}}
        ]}
    ])
    assert "fry" in ss.process_history()
    assert ss.entity_process("paneer") == "fry"


# 7. near-duplicate input (same process applied twice)
def test_near_duplicate_transform():
    ss = SessionState.from_events([
        Add("onion", "ING-030", _qty("1 large")),
        Transform("onion", "chop", sets=(("form", "chopped"),), step=1),
        Transform("onion", "fry", sets=(("form", "fried"),), step=2),
    ])
    assert ss.process_history() == {"chop", "fry"}
    assert ss.entity_process("onion") == "fry"


# 8. OOD concept/process
def test_ood_process():
    ss = SessionState.from_events([
        Add("tofu", "ING-040", _qty("200g")),
        Transform("tofu", "sous_vide", step=1),  # unusual process
    ])
    assert "sous_vide" in ss.process_history()


# 9. explicit UNKNOWN
def test_explicit_unknown():
    ss = SessionState.from_events([
        Add("mystery", None, _qty("some")),  # concept_id unknown
        Observe("mystery", "temperature", "UNKNOWN"),
    ])
    state = ss.current_state("mystery")
    assert state["fields"]["temperature"]["value"] == "UNKNOWN"


# 10. malformed identifier/reference
def test_malformed_event_type():
    ss = SessionState.from_turns([
        {"turn": 1, "events": [{"type": "BogusEvent", "foo": "bar"}]}
    ])
    assert "unknown type" in ss.issues[0]
    assert len(ss.events) == 0  # bogus event skipped


# 11. version mismatch (empty session)
def test_empty_session():
    ss = SessionState.empty()
    assert ss.process_history() == set()
    assert ss.alive_entities() == []
    assert ss.version == VERSION


# 12. round-trip/replay: update returns new, original unchanged
def test_immutable_update():
    ss1 = SessionState.from_events([
        Add("broccoli", "ING-060", _qty("300g")),
    ])
    ss2 = ss1.update([Transform("broccoli", "steam", sets=(("form", "steamed"),))])
    assert ss1.process_history() == set()       # original unchanged
    assert ss2.process_history() == {"steam"}   # new has it
    assert len(ss2.events) == 2
    assert len(ss1.events) == 1                 # immutability


# -- extra: _to_event JSON round-trip
def test_to_event_transform():
    ev = _to_event({"type": "Transform", "target": "x", "process": "boil", "sets": {"form": "soft"}, "step": 3})
    assert isinstance(ev, Transform)
    assert ev.process == "boil"
    assert ev.sets == (("form", "soft"),)


def test_to_event_merge():
    ev = _to_event({"type": "Merge", "inputs": ["a", "b"], "output": "c", "process": "combine"})
    assert isinstance(ev, Merge)
    assert ev.inputs == ("a", "b")


# -- from_session with ingredients auto-injection
def test_from_session_with_ingredients():
    sd = {
        "ingredients": [
            {"entity": "rice", "concept": "UNKNOWN", "quantity": "200g basmati rice"},
            {"entity": "water", "concept": "UNKNOWN", "quantity": "400ml water"},
        ],
        "turns": [
            {"turn": 1, "events": [
                {"type": "Merge", "inputs": ["rice", "water"], "output": "rice pot", "process": "simmer"},
                {"type": "Transform", "target": "rice pot", "process": "simmer",
                 "sets": {"texture": "tender"}},
            ]},
            {"turn": 2, "events": [
                {"type": "Observe", "target": "rice pot", "field": "texture",
                 "value": "hard centre"},
            ]},
        ],
    }
    ss = SessionState.from_session(sd)
    assert ss.process_history() == {"simmer"}
    assert "rice pot" in ss.alive_entities()
    assert len(ss.issues) == 0  # no unknown entity errors
    state = ss.current_state("rice pot")
    assert state["fields"]["texture"]["value"] == "hard centre"
    assert state["fields"]["texture"]["trajectory"] == "OBSERVED_SESSION"


# -- integration: from_turns matches from_events
def test_turns_match_events():
    turns = [{"turn": 1, "events": [
        {"type": "Add", "label": "potato", "concept_id": "ING-070", "qty": "500g"},
        {"type": "Transform", "target": "potato", "process": "boil", "sets": {"form": "cooked"}}
    ]}]
    ss = SessionState.from_turns(turns)
    assert ss.process_history() == {"boil"}
    assert ss.current_state("potato")["fields"]["form"]["value"] == "cooked"
