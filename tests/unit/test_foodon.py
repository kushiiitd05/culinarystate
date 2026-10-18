from pathlib import Path

from culinarystate.vocab.foodon import ancestors, name_index, norm, parse, strip_qualifier

OWL = Path(__file__).resolve().parents[1] / "fixtures" / "mini_foodon.owl"


def test_parse_skips_obsolete_deprecated_and_non_foodon():
    t = parse(OWL)
    assert set(t) == {"FOODON_1", "FOODON_2", "FOODON_3"}
    assert ancestors("FOODON_3", t) == ["FOODON_2", "FOODON_1"]


def test_index_scores():
    idx = name_index(parse(OWL))
    assert idx["tomato"] == {"FOODON_2": 1.0, "FOODON_3": 0.85}     # qualifier-stripped label scores lower
    assert idx["love apple"] == {"FOODON_2": 0.9}
    assert norm("Tomatoes") == "tomato" and norm("berries") == "berry" and strip_qualifier("a (b, c)") == "a"
