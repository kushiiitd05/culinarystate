import copy

import pytest

from culinarystate.annotation.agreement import adjudication_rows, agreement, char_kappa
from culinarystate.annotation.examples import ALL, pasta_reserved_water, white_sauce
from culinarystate.annotation.gold import to_events, validate_gold
from culinarystate.state_graph.engine import replay


@pytest.mark.parametrize("fn", ALL)
def test_examples_valid_and_replay_clean(fn):
    doc = fn()
    assert validate_gold(doc) == []
    g = replay(to_events(doc))
    assert g.issues == ()


def test_white_sauce_state():
    g = replay(to_events(white_sauce()))
    assert g.alive() == ["greasing butter", "seasoned sauce"]
    assert g.current("greasing butter").qty.render() == "1 tbsp"
    assert g.current("seasoned sauce").qty.evaluate()["status"] == "UNKNOWN"    # g + mL + qualitative pinch


def test_pasta_reserve_and_recombine():
    g = replay(to_events(pasta_reserved_water()))
    rels = {e.relation for e in g.edges}
    assert {"SPLITS_INTO", "RESERVED_AS", "DISCARDED_FROM", "RECOMBINED_WITH"} <= rels
    assert g.alive() == ["dish"]


def test_validator_catches_offset_and_missing_fields():
    doc = white_sauce()
    doc["ingredient_lines"][0]["spans"][0]["end"] = 3
    doc["steps"][1]["events"][0].pop("output")
    errs = validate_gold(doc)
    assert any("span text" in e for e in errs) and any("missing" in e for e in errs)


def test_validator_rejects_ai_annotator():
    doc = white_sauce()
    doc["annotator"] = "claude"
    assert validate_gold(doc)


def test_agreement_identical_is_perfect():
    a, b = white_sauce("Kush"), white_sauce("Parv")
    r = agreement(a, b)
    assert r["spans_exact"]["micro"]["f1"] == 1.0 and r["char_kappa_mean"] == 1.0
    assert r["concept_agreement"] == 1.0 and r["state"]["merge_split_f1"]["f1"] == 1.0
    assert adjudication_rows(a, b) == []


def test_agreement_detects_disagreement():
    a, b = white_sauce("Kush"), white_sauce("Parv")
    b = copy.deepcopy(b)
    b["ingredient_lines"][0]["concept"] = "butter"                    # concept disagreement
    b["steps"][0]["events"] = b["steps"][0]["events"][:2]             # Parv missed the reserve
    r = agreement(a, b)
    assert r["concept_agreement"] == 0.75 and r["state"]["merge_split_f1"]["recall"] < 1.0
    rows = adjudication_rows(a, b)
    assert {row["field"] for row in rows} >= {"concept", "event"}
    assert all(row["adjudicated"] == "" for row in rows)


def test_char_kappa():
    t = "50g butter"
    a = [{"start": 0, "end": 2, "label": "QUANTITY"}, {"start": 4, "end": 10, "label": "FOOD"}]
    b = [{"start": 0, "end": 2, "label": "QUANTITY"}]
    assert char_kappa(t, a, a) == 1.0 and char_kappa(t, a, b) < 1.0
