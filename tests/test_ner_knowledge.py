"""S119 Part VII: knowledge contexts are train-only, deterministic, and grow K0 < K1 < K2 < K3."""
from culinarystate.ner.knowledge import build_context

TRAIN = [("2 cups flour , sifted", [(0, 1, "QUANTITY"), (2, 6, "UNIT"), (7, 12, "FOOD"), (15, 21, "PROCESS")])] * 8
LAB = ["FOOD", "QUANTITY", "UNIT", "PROCESS"]


def test_ladder_and_determinism():
    c = [build_context(TRAIN, LAB, k) for k in ("K0", "K1", "K2", "K3")]
    assert c[0] == "" and "food: ingredient" in c[1] and "flour" in c[2] and len(c[1]) < len(c[2]) <= len(c[3])
    assert c == [build_context(TRAIN, LAB, k) for k in ("K0", "K1", "K2", "K3")]


def test_no_test_text_leaks_into_context():
    other = TRAIN + [("9 tbsp zzzunseenword", [(2, 6, "UNIT"), (7, 20, "FOOD")])]
    assert "zzzunseenword" not in build_context(TRAIN, LAB, "K3") and "zzzunseenword" in build_context(other, LAB, "K2")
