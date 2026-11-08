import csv
import json

import pytest

from culinarystate.lotstate import ing_match as M
from culinarystate.lotstate import mention_freq as MF
from culinarystate.lotstate.sr_legacy import parse_portion
from tests.unit._lotstate_fx import make_sr

SR = make_sr()
MATCHER = M.Matcher(SR, phrases={})


def top(name, cat=None):
    c = MATCHER.match(name, cat)
    return c[0] if c else None


def test_head_noun_identity_and_raw_default():
    c = top("onion")
    assert c["description"] == "Onions, raw" and c["band"] in ("HIGH", "MEDIUM")
    # a processed SR entry is not preferred when the ING names no processing facet
    assert top("onion")["fdc_id"] == 1


def test_form_words_are_facets_not_identity():
    # "dried onion" keeps identity onion and the dried facet: the dehydrated entry wins over raw
    c = top("dried onion")
    assert c["fdc_id"] == 6
    assert "facet_match" in c["reason"]
    # "frozen onion" prefers the frozen entry
    assert top("frozen onion")["fdc_id"] == 16


def test_head_noun_beats_modifier_word():
    # "red pepper" must not pick black pepper; "black pepper" must not pick sweet peppers
    assert top("red pepper")["fdc_id"] == 15
    assert top("black pepper")["fdc_id"] == 14


def test_generic_head_is_never_high():
    cands = MATCHER.match("cheese")
    assert cands[0]["band"] != "HIGH"
    assert [c["rank"] for c in cands] == [1, 2, 3]
    # deterministic
    assert MATCHER.match("cheese") == cands


def test_unknown_ingredient_has_no_high_candidate():
    c = MATCHER.match("zorblax")
    assert c == []


def test_category_penalty_for_baby_foods():
    c = MATCHER.match("applesauce")
    assert not c or c[0]["category"] != "Baby Foods" or c[0]["band"] != "HIGH"


def test_draft_rows_are_ai_drafted_never_accepted():
    rows = M.match_ing_rows(MATCHER, [{"id": "ING-1", "canonical_name": "onion", "status": "ACTIVE", "category": "VEGETABLE",
                                       "corpus_frequency": 5},
                                      {"id": "ING-2", "canonical_name": "zorblax", "status": "ACTIVE"}])
    assert {r["status"] for r in rows} == {"AI_DRAFTED"}
    assert {r["human_decision"] for r in rows} == {""}
    assert all(r["confidence_band"] in ("HIGH", "MEDIUM", "LOW", "NONE") for r in rows)
    top1 = M.top1_table(rows)
    assert top1["ING-1"]["fdc_id"] == 1 and "ING-2" not in top1


def test_phrase_variant_can_reach_an_sr_entry():
    m = M.Matcher(SR, phrases={"caster sugar": ["sugars granulated"]})
    c = m.match("caster sugar")[0]
    assert c["fdc_id"] == 3 and c["via"].startswith("phrase:")


@pytest.mark.parametrize("mod,kind,unit,size,desc", [
    ("cup, chopped", "VOLUME", "cup", None, "chopped"),
    ("tbsp", "VOLUME", "tbsp", None, ""),
    ("fl oz", "VOLUME", "fl_oz", None, ""),
    ("medium (2-1/2\" dia)", "COUNT", "item", "medium", ""),
    ("large", "COUNT", "item", "large", ""),
    ("slice, medium (1/8\" thick)", "COUNT", "slice", "medium", "medium"),
    ("clove", "COUNT", "clove", None, ""),
    ("oz", "MASS", None, None, ""),
    ("package (10 oz)", "PACKAGE", None, None, ""),
    ("piece, cooked, excluding refuse (yield from 1 lb raw meat with refuse)", "OTHER", None, None, "cooked, excluding refuse"),
])
def test_portion_parser(mod, kind, unit, size, desc):
    p = parse_portion(1, 1, "1", mod, "10")
    assert (p.kind, p.unit_key, p.size) == (kind, unit, size)
    assert p.descriptor == desc


def test_portion_density_and_grams_per_unit():
    p = parse_portion(1, 1, "2", "cup", "480")
    assert p.grams_per_unit == 240
    assert abs(float(p.g_per_ml) - 240 / 236.5882365) < 1e-9


def test_cumulative_coverage_and_80pct_cut():
    rows, need = MF.cumulative([("a", 50), ("b", 30), ("c", 15), ("d", 5)], 0.8)
    assert need == 2 and [round(r[2], 2) for r in rows] == [0.5, 0.8, 0.95, 1.0]
