import copy

from culinarystate.annotation.examples import pasta_reserved_water, white_sauce
from culinarystate.annotation.pilot_agreement import disagreements, recipe_metrics


def _cats(rows):
    return {r["category"] for r in rows}


def test_identical_docs_agree_everywhere():
    d = white_sauce()
    m = recipe_metrics(d, copy.deepcopy(d))
    assert m["event_f1_strict"]["f1"] == 1.0 and m["spans_exact"]["micro"]["f1"] == 1.0
    assert m["replay_consistent"]["ok"] and m["state_field_agreement"]["agree"] == 1.0
    from culinarystate.annotation.pilot_agreement import _align
    assert disagreements(d, copy.deepcopy(d), _align(d, d)) == []


def test_intermediate_label_choice_alone_is_not_a_disagreement():
    a = white_sauce()
    b = copy.deepcopy(a)
    old = next(e["output"] for s in b["steps"] for e in s["events"] if e["type"] == "Merge")
    for s in b["steps"]:
        for e in s["events"]:
            for k in ("target", "output"):
                if e.get(k) == old:
                    e[k] = old + " base"
            if "inputs" in e:
                e["inputs"] = [old + " base" if x == old else x for x in e["inputs"]]
        for c in s.get("coref", []):
            if c["entity"] == old:
                c["entity"] = old + " base"
    m = recipe_metrics(a, b)
    assert m["event_f1_strict"]["f1"] == 1.0 and m["alive_entity_f1"]["f1"] == 1.0


def test_boundary_concept_and_event_type_are_categorised():
    a = pasta_reserved_water()
    b = copy.deepcopy(a)
    sp = next(s for li in b["ingredient_lines"] for s in li["spans"] if s["label"] == "FOOD")
    sp["end"] -= 1
    b["ingredient_lines"][0]["concept"] = "UNKNOWN"
    b["steps"][0]["events"] = b["steps"][0]["events"][:-1]
    m = recipe_metrics(a, b)
    from culinarystate.annotation.pilot_agreement import _align
    cats = _cats(disagreements(a, b, _align(a, b)))
    assert {"boundary", "canonical_identity", "event_type"} <= cats
    assert m["unknown_disagreement_rate"] > 0 and m["event_f1_strict"]["f1"] < 1.0
