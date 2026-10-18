"""Worked gold examples (synthetic recipes written for the handbook — no third-party text).

`sp(text, sub, label, nth)` computes offsets so examples stay correct when edited.
Run `python -m culinarystate.annotation.examples` to write annotation/examples/*.json.
"""
from __future__ import annotations

import json
from pathlib import Path


def sp(text: str, sub: str, label: str, nth: int = 1) -> dict:
    start = -1
    for _ in range(nth):
        start = text.index(sub, start + 1)
    return {"start": start, "end": start + len(sub), "label": label, "text": sub}


def cr(text: str, mention: str, entity: str, nth: int = 1) -> dict:
    s = sp(text, mention, "FOOD", nth)
    return {"mention": mention, "start": s["start"], "end": s["end"], "entity": entity}


def line(i: int, text: str, entity: str, concept: str, spans: list, **kw) -> dict:
    return {"line_index": i, "text": text, "spans": spans, "entity": entity, "concept": concept, **kw}


def white_sauce(annotator: str = "Kush") -> dict:
    L = ["50g unsalted butter", "50g plain flour", "500ml whole milk", "pinch of grated nutmeg (optional)"]
    S = ["Melt the butter in a saucepan over a low heat, then spoon out 1 tbsp and set aside for greasing.",
         "Stir the flour into the remaining butter and cook for 2 mins to make a roux.",
         "Gradually whisk in the milk and simmer for 5 mins until thick enough to coat the back of a spoon.",
         "Season with the nutmeg, if using."]
    return {
        "schema_version": "gold-1.0", "recipe_id": "GOLD-EX-001", "source_ref": "synthetic handbook example",
        "annotator": annotator, "status": "DONE", "locale": "UK",
        "ingredient_lines": [
            line(0, L[0], "butter", "unsalted butter", [sp(L[0], "50", "QUANTITY"), sp(L[0], "g", "UNIT"),
                                                         sp(L[0], "unsalted butter", "FOOD")]),
            line(1, L[1], "flour", "plain flour", [sp(L[1], "50", "QUANTITY"), sp(L[1], "g", "UNIT"),
                                                   sp(L[1], "plain flour", "FOOD")]),
            line(2, L[2], "milk", "milk", [sp(L[2], "500", "QUANTITY"), sp(L[2], "ml", "UNIT"),
                                          sp(L[2], "whole milk", "FOOD")]),
            line(3, L[3], "nutmeg", "nutmeg", [sp(L[3], "pinch", "UNIT"), sp(L[3], "grated", "FORM"),
                                              sp(L[3], "nutmeg", "FOOD"), sp(L[3], "optional", "OPTIONAL")],
                 optional=True),
        ],
        "steps": [
            {"step_index": 0, "text": S[0],
             "spans": [sp(S[0], "Melt", "ACTION"), sp(S[0], "saucepan", "TOOL"), sp(S[0], "low heat", "TEMPERATURE"),
                       sp(S[0], "spoon out", "ACTION"), sp(S[0], "1 tbsp", "QUANTITY")],
             "events": [{"type": "Transfer", "target": "butter", "location": "saucepan"},
                        {"type": "Transform", "target": "butter", "process": "melt", "temperature": "low heat (qualitative)",
                         "sets": {"phase": "melted"}},
                        {"type": "Reserve", "target": "butter", "output": "greasing butter", "portion": "1 tbsp"}],
             "coref": [cr(S[0], "the butter", "butter")]},
            {"step_index": 1, "text": S[1],
             "spans": [sp(S[1], "Stir", "ACTION"), sp(S[1], "cook", "ACTION"), sp(S[1], "2 mins", "TIME"),
                       sp(S[1], "roux", "INTERMEDIATE")],
             "events": [{"type": "Merge", "inputs": ["flour", "butter"], "output": "roux", "process": "stir"},
                        {"type": "Transform", "target": "roux", "process": "cook", "time": "2 min"}],
             "coref": [cr(S[1], "the remaining butter", "butter")]},
            {"step_index": 2, "text": S[2],
             "spans": [sp(S[2], "whisk in", "ACTION"), sp(S[2], "simmer", "ACTION"), sp(S[2], "5 mins", "TIME"),
                       sp(S[2], "thick enough to coat the back of a spoon", "ENDPOINT")],
             "events": [{"type": "Merge", "inputs": ["roux", "milk"], "output": "sauce", "process": "whisk"},
                        {"type": "Transform", "target": "sauce", "process": "simmer", "time": "5 min",
                         "endpoint": "coats back of spoon", "sets": {"texture": "thick"}}],
             "coref": [cr(S[2], "the milk", "milk")]},
            {"step_index": 3, "text": S[3], "spans": [sp(S[3], "Season", "ACTION")],
             "events": [{"type": "Merge", "inputs": ["sauce", "nutmeg"], "output": "seasoned sauce", "process": "season"}],
             "coref": [cr(S[3], "the nutmeg", "nutmeg")]},
        ],
        "unknowns": [{"what": "mass of the reserved 1 tbsp butter", "why": "volume only; no POR record -> symbolic"}],
    }


def pasta_reserved_water(annotator: str = "Kush") -> dict:
    L = ["300g spaghetti", "2 garlic cloves, sliced", "3 tbsp olive oil", "salt, to taste"]
    S = ["Cook the spaghetti in a large pan of salted boiling water for 10 mins.",
         "Drain, reserving a mugful of the cooking water.",
         "Meanwhile, gently fry the garlic in the oil until just golden.",
         "Toss the pasta with the garlic oil, adding a splash of the reserved water to loosen."]
    return {
        "schema_version": "gold-1.0", "recipe_id": "GOLD-EX-002", "source_ref": "synthetic handbook example",
        "annotator": annotator, "status": "DONE", "locale": "UK",
        "ingredient_lines": [
            line(0, L[0], "spaghetti", "spaghetti", [sp(L[0], "300", "QUANTITY"), sp(L[0], "g", "UNIT"),
                                                     sp(L[0], "spaghetti", "FOOD")]),
            line(1, L[1], "garlic", "garlic", [sp(L[1], "2", "QUANTITY"), sp(L[1], "garlic", "FOOD"),
                                              sp(L[1], "cloves", "UNIT"), sp(L[1], "sliced", "FORM")]),
            line(2, L[2], "oil", "olive oil", [sp(L[2], "3", "QUANTITY"), sp(L[2], "tbsp", "UNIT"),
                                               sp(L[2], "olive oil", "FOOD")]),
            line(3, L[3], "salt", "salt", [sp(L[3], "salt", "FOOD")]),
        ],
        "steps": [
            {"step_index": 0, "text": S[0],
             "spans": [sp(S[0], "Cook", "ACTION"), sp(S[0], "large pan", "TOOL"), sp(S[0], "salted boiling water", "MEDIUM"),
                       sp(S[0], "10 mins", "TIME")],
             "events": [{"type": "Merge", "inputs": ["spaghetti", "salt"], "output": "pasta pot", "process": "boil",
                         "medium": "salted boiling water", "implicit": True},
                        {"type": "Transform", "target": "pasta pot", "process": "boil", "time": "10 min",
                         "tool": "large pan"}]},
            {"step_index": 1, "text": S[1],
             "spans": [sp(S[1], "Drain", "ACTION"), sp(S[1], "reserving", "ACTION"), sp(S[1], "mugful", "UNIT")],
             "events": [{"type": "Split", "target": "pasta pot",
                         "outputs": [{"label": "pasta", "fraction": None}, {"label": "cooking water", "fraction": None}]},
                        {"type": "Reserve", "target": "cooking water", "output": "reserved water", "portion": "1 mug"},
                        {"type": "Discard", "target": "cooking water", "value": "drained water"}],
             "coref": [cr(S[1], "the cooking water", "cooking water")]},
            {"step_index": 2, "text": S[2],
             "spans": [sp(S[2], "fry", "ACTION"), sp(S[2], "just golden", "ENDPOINT")],
             "events": [{"type": "Merge", "inputs": ["garlic", "oil"], "output": "garlic oil", "process": "fry"},
                        {"type": "Transform", "target": "garlic oil", "process": "fry", "endpoint": "just golden",
                         "sets": {"garlic_colour": "golden"}}],
             "coref": [cr(S[2], "the garlic", "garlic"), cr(S[2], "the oil", "oil")]},
            {"step_index": 3, "text": S[3],
             "spans": [sp(S[3], "Toss", "ACTION"), sp(S[3], "garlic oil", "INTERMEDIATE"), sp(S[3], "splash", "UNIT")],
             "events": [{"type": "Merge", "inputs": ["pasta", "garlic oil"], "output": "dish", "process": "toss"},
                        {"type": "Recombine", "target": "reserved water", "output": "dish"}],
             "coref": [cr(S[3], "the pasta", "pasta"), cr(S[3], "the reserved water", "reserved water")]},
        ],
        "unknowns": [{"what": "volume of a mugful", "why": "mug is a non-standard vessel"},
                     {"what": "how much reserved water is used ('a splash')", "why": "qualitative; whole reserve recombined"}],
    }


def roast_veg(annotator: str = "Kush") -> dict:
    L = ["2 large carrots", "1 red onion, cut into wedges", "2 tbsp olive oil"]
    S = ["Heat oven to 200C/180C fan/gas 6.", "Cut the carrots into chunks.",
         "Toss the carrots and onion with the oil on a baking tray.",
         "Roast for 35-40 mins until tender and golden at the edges."]
    return {
        "schema_version": "gold-1.0", "recipe_id": "GOLD-EX-003", "source_ref": "synthetic handbook example",
        "annotator": annotator, "status": "DONE", "locale": "UK",
        "ingredient_lines": [
            line(0, L[0], "carrots", "carrot", [sp(L[0], "2", "QUANTITY"), sp(L[0], "large", "SIZE"),
                                               sp(L[0], "carrots", "FOOD")]),
            line(1, L[1], "onion", "red onion", [sp(L[1], "1", "QUANTITY"), sp(L[1], "red onion", "FOOD"),
                                                 sp(L[1], "cut into wedges", "FORM")]),
            line(2, L[2], "oil", "olive oil", [sp(L[2], "2", "QUANTITY"), sp(L[2], "tbsp", "UNIT"),
                                               sp(L[2], "olive oil", "FOOD")]),
        ],
        "steps": [
            {"step_index": 0, "text": S[0],
             "spans": [sp(S[0], "Heat", "ACTION"), sp(S[0], "oven", "TOOL"), sp(S[0], "200C/180C fan/gas 6", "TEMPERATURE")],
             "events": []},
            {"step_index": 1, "text": S[1], "spans": [sp(S[1], "Cut", "ACTION"), sp(S[1], "chunks", "FORM")],
             "events": [{"type": "Transform", "target": "carrots", "process": "cut", "sets": {"form": "chunks"}}],
             "coref": [cr(S[1], "the carrots", "carrots")]},
            {"step_index": 2, "text": S[2],
             "spans": [sp(S[2], "Toss", "ACTION"), sp(S[2], "baking tray", "TOOL")],
             "events": [{"type": "Merge", "inputs": ["carrots", "onion", "oil"], "output": "tray veg", "process": "toss"},
                        {"type": "Transfer", "target": "tray veg", "location": "baking tray"}],
             "coref": [cr(S[2], "the carrots", "carrots"), cr(S[2], "onion", "onion"), cr(S[2], "the oil", "oil")]},
            {"step_index": 3, "text": S[3],
             "spans": [sp(S[3], "Roast", "ACTION"), sp(S[3], "35-40 mins", "TIME"),
                       sp(S[3], "tender and golden at the edges", "ENDPOINT")],
             "events": [{"type": "Transfer", "target": "tray veg", "location": "oven", "implicit": True},
                        {"type": "Transform", "target": "tray veg", "process": "roast", "time": "35-40 min",
                         "temperature": "200C conventional / 180C fan setpoint", "endpoint": "tender, golden edges",
                         "sets": {"doneness": "tender", "colour": "golden edges"}}]},
        ],
        "unknowns": [{"what": "food core temperature", "why": "only oven setpoint given (never treat as core temp)"},
                     {"what": "carrot mass", "why": "count + size only; no verified POR"}],
    }


ALL = (white_sauce, pasta_reserved_water, roast_veg)


def write_examples(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fn in ALL:
        doc = fn()
        p = out_dir / f"{doc['recipe_id']}.{doc['annotator']}.json"
        p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        paths.append(p)
    return paths


if __name__ == "__main__":
    for p in write_examples(Path(__file__).resolve().parents[3] / "annotation" / "examples"):
        print(p)
