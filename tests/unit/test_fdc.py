import pandas as pd

from culinarystate.vocab.fdc import _variants, candidates_for, parse_portion_modifier, score_candidate, token_index

FOOD = pd.DataFrame([
    (1, "Butter, salted", "Dairy"), (2, "Fruit butters, apple", "Fruits"), (3, "Oil, olive, salad or cooking", "Fats"),
    (4, "Oil, corn, peanut, and olive", "Fats"), (5, "Spices, cinnamon, ground", "Spices"),
    (6, "Bread, cinnamon", "Baked"), (7, "Wheat flour, white, all-purpose, enriched, bleached", "Cereal"),
    (8, "Milk, whole, 3.25% milkfat", "Dairy"), (9, "Milk, dry, whole, with added vitamin D", "Dairy"),
    (10, "KRAFT, butter spread", "Dairy"),
], columns=["fdc_id", "description", "category"])
IDX = token_index(FOOD)


def top(name):
    c = candidates_for(name, FOOD, IDX)
    return c[0] if c else None


def test_exact_head_beats_partial():
    assert top("butter").fdc_id == 1
    assert top("olive oil").fdc_id == 3                     # inverted SR naming "Oil, olive"
    assert top("cinnamon").fdc_id == 5                      # category prefix "Spices," skipped
    assert top("milk").fdc_id == 8                          # 'dry' is not neutral


def test_uk_synonym_used_and_recorded():
    c = top("plain flour")
    assert c.fdc_id == 7 and c.via == "all-purpose flour"


def test_brand_penalty_and_no_match():
    assert score_candidate("butter", "KRAFT, butter spread")[0] < score_candidate("butter", "Butter, salted")[0]
    assert top("paneer") is None


def test_variants():
    assert "turmeric ground" in _variants("turmeric powder")
    assert "without salt butter" in _variants("unsalted butter")


def test_parse_portion_modifier():
    assert parse_portion_modifier("cup, chopped").unit_key == "cup"
    assert parse_portion_modifier("large").size == "large"
    assert parse_portion_modifier("cloves").unit_key == "clove"
    assert parse_portion_modifier('medium (2-1/2" dia)').size == "medium"
