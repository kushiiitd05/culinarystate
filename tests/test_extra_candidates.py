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


def test_substitution_reason_carries_carbon_when_both_known():
    lex = _lex()
    lex = Lexicon(None, lex.proc_ids, {}, {}, frozenset(), alternatives=lex.alternatives, followed_by=lex.followed_by,
                  ing_names=lex.ing_names, carbon={"ING-000001": 12.0, "ING-000002": 9.5})
    cs = extra_candidates("what can I use instead of butter, any substitute to recover?", _slots(), lex)
    assert cs is not None
    assert any("carbon 9.5 vs 12.0" in c.reason for c in cs.candidates if c.type == "SUBSTITUTION")
