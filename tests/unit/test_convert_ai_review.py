import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("car", Path(__file__).resolve().parents[2] / "tools" / "convert_ai_review.py")
car = importlib.util.module_from_spec(spec)
spec.loader.exec_module(car)


def _draft(split_output):
    return {"recipe_id": "R9", "source_ref": "x", "locale": "UK", "unknowns": [],
            "ingredient_lines": [{"line_index": 0, "text": "1 loaf", "entity": "R9_ING_00_loaf", "concept_candidate": "bread",
                                  "reason": "", "spans": [{"start": 2, "end": 6, "label": "FOOD_MENTION", "text": "loaf"}]}],
            "steps": [{"step_index": 0, "text": "Halve the loaf.", "spans": [], "coref": [],
                       "events": [{"operation": "SPLIT", "action": "halve", "inputs": ["loaf"], "output": split_output,
                                   "conditions": {}, "endpoint": None, "reason": "", "event_id": "R9_S00_EV00"}]}]}


def test_single_output_split_has_no_synthetic_remainder():
    doc, _, _ = car.convert(_draft("halved loaf"), {"bread": "bread"})
    evs = doc["steps"][0]["events"]
    assert [e["type"] for e in evs] == ["Transform"] and evs[0]["target"] == "loaf"
    assert not any("remainder" in str(e) for e in evs)


def test_two_named_outputs_still_split():
    doc, _, _ = car.convert(_draft("half a + half b"), {"bread": "bread"})
    e = doc["steps"][0]["events"][0]
    assert e["type"] == "Split" and [o["label"] for o in e["outputs"]] == ["half a", "half b"]
