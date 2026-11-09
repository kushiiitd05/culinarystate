"""S178 INGCAT: the proposal engine (tools/s178_ingcat_propose.py) on single ingredient names.

Pure rule tests, no ledger or SR file. Ingredient names are registry-style names; nothing here is third-party text.
Every proposal is AI_DRAFTED: these tests pin the rules, they do not assert any value is right.
"""
from __future__ import annotations

import pytest

from tests.unit.test_s178_analysis_helpers import load_tool

T = load_tool("s178_ingcat_propose")
VOCAB = ("BEVERAGE", "CEREAL", "CONDIMENT", "DAIRY", "EGG", "FAT_OIL", "FRUIT", "HERB_SPICE", "LEGUME", "MEAT", "NUT_SEED",
         "SEAFOOD", "SWEETENER", "VEGETABLE")


def prop(name, **kw):
    return T.propose(T.Evidence(name=name, **kw), VOCAB)


def reg(name, kind, group, desc=""):
    return prop(name, registry_kind=kind, registry_group=group, registry_description=desc or name)


# ------------------------------------------------------------------ names, tokens, SR groups
def test_fold_strips_accents_and_singularises():
    assert T.fold("Gruyère") == ("gruyere",)
    assert T.fold("jalapeño peppers") == ("jalapeno", "pepper")
    assert T.fold("saké") == ("sake",)


def test_sr_group_maps_only_to_existing_vocabulary_items():
    assert set(T.GROUP_TO_CATEGORY.values()) <= set(VOCAB)
    assert T.sr_category("Spices and Herbs") == "HERB_SPICE"
    assert T.sr_category("Snacks") is None and T.sr_category("Baby Foods") is None and T.sr_category(None) is None
    assert T.sr_category("Dairy and Egg Products", "Egg, whole, raw, fresh") == "EGG"
    assert T.sr_category("Dairy and Egg Products", "Cheese, parmesan") == "DAIRY"
    assert T.sr_category("Fruits and Fruit Juices", "Lemon juice, raw") == "BEVERAGE"


def test_group_map_agrees_with_the_s177_crosswalk():
    from culinarystate.mechanism import evidence_gates as EG
    for group, cat in T.GROUP_TO_CATEGORY.items():
        assert EG.category_matches(cat, group), (cat, group)


def test_every_lexicon_category_exists_in_the_ingredient_vocabulary():
    assert set(T.CATEGORY_WORDS) <= set(VOCAB)
    assert {p[1] for p in T.PHRASES if p[1]} <= set(VOCAB)
    assert {v[0] for v in T.WORD_CAT.values()} <= set(VOCAB)


# ------------------------------------------------------------------ the cases the brief names
def test_salt_has_no_exact_fit_and_suggests_a_new_value_without_adding_it():
    p = reg("salt", "DIRECT", "Spices and Herbs", "Salt, table")
    assert p.category == "HERB_SPICE" and p.alt_category == "CONDIMENT"      # closest existing values, in order
    assert p.confidence == T.MEDIUM                                          # never HIGH: the fit is approximate
    assert "NO_EXACT_FIT" in p.conflicts and p.new_category_suggestion == "SALT_MINERAL"
    assert "SALT_MINERAL" not in VOCAB and p.category in VOCAB


def test_water_and_ice_are_flagged_not_silently_a_beverage():
    for name in ("water", "ice", "ice cube", "hot water"):
        p = reg(name, "DIRECT", "Beverages", "Beverages, water, tap")
        assert p.category == "BEVERAGE" and p.confidence == T.MEDIUM
        assert p.new_category_suggestion == "WATER" and "NO_EXACT_FIT" in p.conflicts
    mineral = reg("sparkling water", "APPROX", "Beverages")
    assert mineral.category == "BEVERAGE" and mineral.confidence == T.HIGH and not mineral.new_category_suggestion


def test_seasoned_salts_are_ordinary_seasonings():
    p = prop("garlic salt")
    assert p.category == "HERB_SPICE" and not p.new_category_suggestion
    assert prop("salt cod").category == "SEAFOOD" and prop("salt beef").category == "MEAT"


def test_leavening_agents_get_no_category_and_say_why():
    for name in ("baking powder", "bicarbonate of soda", "cream of tartar", "dried yeast"):
        p = reg(name, "DIRECT", "Baked Products")
        assert p.category == "" and p.confidence == T.LOW
        assert p.new_category_suggestion == "LEAVENING_AGENT" and "NO_VOCABULARY_FIT" in p.conflicts
        assert "SR_GROUP_WOULD_MAP_TO(CEREAL)" in p.conflicts            # the SR group would have said CEREAL


def test_culinary_class_beats_a_leaky_sr_group_and_the_conflict_is_recorded():
    soy = reg("soy sauce", "DEFAULT_FORM", "Legumes and Legume Products")
    assert soy.category == "CONDIMENT" and soy.alt_category == "LEGUME" and soy.confidence == T.MEDIUM
    assert "SR_GROUP_DISAGREES" in soy.conflicts
    mayo = reg("mayonnaise", "DIRECT", "Fats and Oils")
    assert mayo.category == "CONDIMENT" and "SR_GROUP_DISAGREES" in mayo.conflicts
    ketchup = reg("ketchup", "UK_US", "Vegetables and Vegetable Products")
    assert ketchup.category == "CONDIMENT" and ketchup.alt_category == "VEGETABLE"


def test_stock_is_the_closest_value_but_flagged():
    p = reg("chicken stock", "DEFAULT_FORM", "Soups, Sauces, and Gravies")
    assert p.category == "CONDIMENT" and p.confidence == T.MEDIUM
    assert p.new_category_suggestion == "STOCK_BROTH" and "NO_EXACT_FIT" in p.conflicts


def test_two_agreeing_bases_with_an_exact_fit_are_high():
    for name, group, cat in (("egg yolk", "Dairy and Egg Products", "EGG"), ("cornflour", "Cereal Grains and Pasta", "CEREAL"),
                             ("honey", "Sweets", "SWEETENER"), ("parmesan", "Dairy and Egg Products", "DAIRY"),
                             ("carrot", "Vegetables and Vegetable Products", "VEGETABLE"), ("paprika", "Spices and Herbs", "HERB_SPICE")):
        p = reg(name, "DIRECT", group, "Egg, yolk" if cat == "EGG" else name)
        assert (p.category, p.confidence) == (cat, T.HIGH), name
        assert "LEXICAL" in p.basis and "REGISTRY_SR" in p.basis


def test_dual_use_words_are_never_high():
    ginger = reg("ginger", "DEFAULT_FORM", "Vegetables and Vegetable Products")
    assert ginger.confidence == T.LOW and ginger.alt_category == "VEGETABLE" and "DUAL_USE" in ginger.conflicts + "DUAL_USE_NOTE"
    chilli = reg("chilli", "UK_US", "Vegetables and Vegetable Products")
    assert chilli.category == "VEGETABLE" and chilli.confidence == T.MEDIUM and chilli.alt_category == "HERB_SPICE"


def test_sr_alone_gives_high_only_for_a_curated_identity_in_a_clean_group():
    clean = reg("zzfood", "DIRECT", "Finfish and Shellfish Products")
    assert (clean.category, clean.confidence) == ("SEAFOOD", T.HIGH)
    approx = reg("zzfood", "APPROX", "Finfish and Shellfish Products")
    assert approx.confidence == T.MEDIUM
    leaky = reg("zzfood", "DIRECT", "Sweets")
    assert leaky.confidence == T.MEDIUM and "LEAKY_SR_GROUP" in leaky.conflicts


def test_legacy_match_alone_is_never_better_than_low_and_a_low_band_proposes_nothing():
    p = prop("zzfood", legacy_group="Beef Products", legacy_description="Beef, raw", legacy_band="HIGH")
    assert p.category == "MEAT" and p.confidence == T.LOW and "LEGACY_MATCH_ONLY" in p.conflicts
    assert prop("zzfood", legacy_group="Beef Products", legacy_band="LOW").category == ""
    assert prop("zzfood").category == "" and "NO_BASIS" in prop("zzfood").conflicts


def test_registry_unmappable_kinds_give_no_sr_basis():
    p = prop("cake", registry_kind="NOT_A_FOOD", legacy_group="Baked Products", legacy_band="HIGH")
    assert "REGISTRY_UNMAPPABLE(NOT_A_FOOD)" in p.conflicts and "LEGACY_SR" not in p.basis     # the registry says no identity
    assert p.category == "CEREAL" and p.confidence == T.MEDIUM                                  # the culinary rule still speaks


def test_utensils_and_generic_nouns_get_no_category():
    for name in ("saucepan", "colander", "wooden spoon", "sharp knife", "muslin", "pastry brush"):
        p = prop(name)
        assert p.category == "" and "NO_VOCABULARY_FIT" in p.conflicts and "NOT_A_FOOD_CONSIDER_DEPRECATING" in p.conflicts, name
    assert prop("silver").category == "" and prop("outer").category == ""
    assert prop("taco shell").category == "CEREAL"                                              # an edible shell is not a utensil


# ------------------------------------------------------------------ rule details that were wrong once
@pytest.mark.parametrize("name,cat", [
    ("tuna steak", "SEAFOOD"), ("salmon fillet", "SEAFOOD"), ("lamb chop", "MEAT"), ("chicken breast fillet", "MEAT"),
    ("peanut butter", "NUT_SEED"), ("butter", "DAIRY"), ("butter bean", "LEGUME"), ("coffee bean", "BEVERAGE"),
    ("green pepper", "VEGETABLE"), ("black pepper", "HERB_SPICE"), ("white pepper", "HERB_SPICE"), ("cayenne pepper", "HERB_SPICE"),
    ("celery seed", "HERB_SPICE"), ("sesame seed", "NUT_SEED"), ("allspice berry", "HERB_SPICE"), ("blueberry", "FRUIT"),
    ("garlic powder", "HERB_SPICE"), ("garlic", "VEGETABLE"), ("onion granule", "HERB_SPICE"), ("tomato paste", "VEGETABLE"),
    ("lemon juice", "BEVERAGE"), ("lemon zest", "FRUIT"), ("olive oil", "FAT_OIL"), ("vegan butter", "FAT_OIL"),
    ("ice cream", "DAIRY"), ("cream cheese", "DAIRY"), ("egg noodles", "CEREAL"), ("water chestnut", "VEGETABLE"),
    ("gruyère", "DAIRY"), ("tortilla chips", "CEREAL"), ("mince pie", "CEREAL"), ("rose water", "HERB_SPICE"),
    ("soy milk", "DAIRY"), ("coconut cream", "NUT_SEED"), ("sweet potato", "VEGETABLE"), ("curry paste", "HERB_SPICE")])
def test_lexical_rule_cases(name, cat):
    lex = T.lexical(T.fold(name))
    assert lex is not None and lex.category == cat, (name, lex)


def test_lexical_returns_none_for_unknown_words():
    assert T.lexical(T.fold("zzzzfood")) is None and T.lexical(()) is None


# ------------------------------------------------------------------ guards
def test_a_proposed_category_is_always_in_the_vocabulary_or_empty():
    names = ["salt", "water", "egg", "baking powder", "soy sauce", "ginger", "saucepan", "tofu", "kombucha", "zzfood",
             "fish sauce", "olive", "mushroom", "gin", "chocolate", "yeast", "tapioca starch", "gelatine"]
    for n in names:
        p = prop(n)
        assert p.category == "" or p.category in VOCAB, (n, p.category)
        assert p.alt_category == "" or p.alt_category in VOCAB
        assert p.confidence in (T.HIGH, T.MEDIUM, T.LOW)


def test_the_vocabulary_guard_refuses_a_value_that_is_not_in_the_ledger_vocabulary():
    small = tuple(c for c in VOCAB if c != "EGG")                  # a ledger vocabulary without EGG
    p = T.propose(T.Evidence(name="egg", registry_kind="DIRECT", registry_group="Dairy and Egg Products",
                             registry_description="Egg, whole"), small)
    assert p.category == "" and p.confidence == T.LOW and "VALUE_NOT_IN_VOCABULARY(EGG)" in p.conflicts


def test_precedent_disagreement_is_flagged_but_does_not_change_the_proposal():
    p = prop("white pepper", registry_kind="DIRECT", registry_group="Spices and Herbs", registry_description="Pepper, white",
             precedent={"VEGETABLE": 9, "HERB_SPICE": 3})
    assert p.category == "HERB_SPICE" and "PRECEDENT_DISAGREES" in p.conflicts
    q = prop("white pepper", registry_kind="DIRECT", registry_group="Spices and Herbs", precedent={"HERB_SPICE": 3})
    assert "PRECEDENT_DISAGREES" not in q.conflicts


def test_propose_is_deterministic():
    ev = T.Evidence(name="soy sauce", registry_kind="DEFAULT_FORM", registry_group="Legumes and Legume Products")
    assert T.propose(ev, VOCAB) == T.propose(ev, VOCAB)
