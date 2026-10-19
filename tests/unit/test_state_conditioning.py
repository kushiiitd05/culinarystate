from culinarystate.decision.pipeline import Lexicon, Slots
from culinarystate.decision.session_state import SessionState
from culinarystate.decision.state_conditioning import condition_slots
from culinarystate.vocab.line_link import LineLinker

LEX = Lexicon(LineLinker({"rice": "ING-000001", "broccoli": "ING-000002"}, set()),
              {"boil": "PROC-1", "simmer": "PROC-2"}, {"ING-000001": ()}, {}, frozenset())
EMPTY = Slots(None, None, (), (), None, ())


def _ss(events, ingredients):
    return SessionState.from_turns([{"events": events}], ingredients)


def _single():
    return _ss([{"type": "Transform", "target": "broccoli", "process": "boil", "sets": {}}],
               [{"entity": "broccoli", "concept": "UNKNOWN", "quantity": "200g broccoli"}])


def test_fills_missing_ingredient_and_process_from_single_alive_entity():
    s, trace = condition_slots("how much vitamin C is left?", EMPTY, _single(), LEX)
    assert s.ingredient_id == "ING-000002" and s.processes == (("boil", "PROC-1"),)
    assert trace["ingredient"]["entity"] == "broccoli" and trace["process"]["from"] == "last_process"


def test_question_slots_win_over_state():
    given = Slots("ING-000001", "rice", (), (("simmer", "PROC-2"),), None, ())
    s, trace = condition_slots("simmer the rice?", given, _single(), LEX)
    assert s == given and trace == {}


def test_ambiguous_entities_leave_slots_empty():
    ss = _ss([], [{"entity": "rice", "concept": "UNKNOWN", "quantity": "1 cup"},
                  {"entity": "broccoli", "concept": "UNKNOWN", "quantity": "1 head"}])
    s, trace = condition_slots("how much is left?", EMPTY, ss, LEX)
    assert s.ingredient_id is None and trace == {}


def test_question_names_the_entity():
    ss = _ss([], [{"entity": "rice", "concept": "UNKNOWN", "quantity": "1 cup"},
                  {"entity": "broccoli", "concept": "UNKNOWN", "quantity": "1 head"}])
    s, _ = condition_slots("what happened to the broccoli?", EMPTY, ss, LEX)
    assert s.ingredient_id == "ING-000002"
