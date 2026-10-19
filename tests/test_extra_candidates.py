from culinarystate.decision.pipeline import Lexicon, Slots, extra_candidates


def _lex():
    return Lexicon(None, {"boil": "PROC-1", "drain": "PROC-2"}, {}, {}, frozenset(),
                   alternatives={"ING-000001": (("ING-000002", 0.6),)},
                   followed_by={"PROC-1": (("PROC-2", 0.5),)},
                   ing_names={"ING-000001": "butter", "ING-000002": "ghee"})


def _slots(proc=None):
    return Slots("ING-000001", "butter", (), ((("boil", "PROC-1"),) if proc else ()), None, ())


def test_recommend_gives_substitutes_only():
    cs = extra_candidates("what is the best way to cook butter?", _slots(True), _lex())
    assert cs is None or all(c.type == "SUBSTITUTION" for c in cs.candidates)


def test_none_for_answer_intent():
    assert extra_candidates("how much vitamin C is in butter?", _slots(), _lex()) is None
