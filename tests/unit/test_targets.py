from culinarystate.decision.targets import TargetLexicon, variants

NAMES = ["Carotene, beta", "Carotene, alpha", "Folate, total", "Folate, food", "Iron, Fe", "Lycopene",
         "Vitamin C, total ascorbic acid", "Lutein + zeaxanthin", "Polyphenols, total", "weight yield"]
LEX = TargetLexicon(NAMES)


def test_variants():
    assert {"beta-carotene", "beta carotene", "carotene, beta"} <= variants("Carotene, beta")
    assert "iron" in variants("Iron, Fe") and "folate" in variants("Folate, total") and "vitamin c" in variants(
        "Vitamin C, total ascorbic acid")
    assert "total" not in variants("Polyphenols, total")


def test_longest_match_unique_gives_canonical_name():
    assert LEX.find("How much beta-carotene does boiled carrot keep?") == "carotene, beta"
    assert LEX.find("does boiling destroy lycopene in tomato") == "lycopene"
    assert LEX.find("iron in boiled spinach") == "iron, fe"
    assert LEX.find("total polyphenols after frying") is None or LEX.find("polyphenols after frying") == "polyphenols, total"


def test_ambiguous_variant_returns_the_shared_key():
    assert LEX.find("how much folate is left") == "folate"           # covers "folate, total" and "folate, food"
    assert LEX.find("carotene in boiled carrots") == "carotene"


def test_no_target():
    assert LEX.find("how do I boil an egg") is None and TargetLexicon([]).find("lycopene") is None
