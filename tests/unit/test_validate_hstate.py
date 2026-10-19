import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS

spec = importlib.util.spec_from_file_location("vh", Path(__file__).resolve().parents[2] / "tools" / "validate_hstate_questions.py")
vh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vh)


import hashlib


def _text(i, q):
    h = hashlib.sha256(f"{i}{q}".encode()).hexdigest()
    return " ".join(h[k:k + 6] for k in range(0, 36, 6))


def _rows():
    r = []
    for i in range(20):
        for q, cls in (("Q1", "STATE_DEPENDENT"), ("Q2", "STATE_DEPENDENT"), ("Q3", "STATE_DEPENDENT"), ("Q4", "CONTROL")):
            r.append({"question_id": f"R{i}-{q}", "recipe_id": f"R{i}", "question_class": cls, "question_text": _text(i, q),
                      "author": "Kush", "gold_mode": "ANSWER", "gold_evidence_cell": "UNSUPPORTED",
                      "state_information_required": "ENTITY;PROCESS" if cls == "STATE_DEPENDENT" else "", "why_state_is_required": "x"})
    return r


def test_complete_set_passes_and_flags_work():
    assert vh.check(_rows()) == []
    r = _rows()
    r[0]["author"] = "claude"
    r[1]["gold_mode"] = "MAYBE"
    r[2]["question_text"] = ""
    e = vh.check(r)
    assert any("author must be Kush" in x for x in e) and any("gold_mode" in x for x in e) and any("empty" in x for x in e)


def test_parser_based_state_dependence_and_control():
    r = _rows()
    both = lambda q: NS(ingredient_id="ING-1", processes=(("boil", "P"),))
    none = lambda q: NS(ingredient_id=None, processes=())
    assert any("state not required" in x for x in vh.check(r, both))
    assert any("control must state" in x for x in vh.check(r, none))
