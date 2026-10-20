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


def test_k4_is_contrastive_budgeted_and_train_only():
    docs = [("fresh basil", [(0, 5, "PHYSICAL_QUALITY"), (6, 11, "FOOD")])] * 20 + [("fresh start", [(0, 5, "PROCESS")])] * 2 + [("olive oil", [(0, 9, "FOOD")])] * 5
    labs = ["FOOD", "PHYSICAL_QUALITY", "PROCESS"]
    c = build_context(docs, labs, "K4", budget=30)
    assert "fresh is physical_quality not process" in c and "food olive oil" in c and len(c.split()) <= 30
    assert len(build_context(docs, labs, "K4", budget=8).split()) <= 8
    assert "zzzunseen" not in build_context(docs, labs, "K4") and "zzzunseen" in build_context(docs + [("zzzunseen xx", [(0, 12, "FOOD")])] * 30, labs, "K4", budget=60)


def test_type_specific_context_is_per_type_budgeted_train_only():
    from culinarystate.ner.knowledge import type_context
    docs = [("fresh basil", [(0, 5, "PHYSICAL_QUALITY"), (6, 11, "FOOD")])] * 20 + [("fresh start", [(0, 5, "PROCESS")])] * 2 + [("olive oil", [(0, 9, "FOOD")])] * 5
    labs = ["FOOD", "PHYSICAL_QUALITY", "PROCESS"]
    c = type_context(docs, "PHYSICAL_QUALITY", labs, budget=30)
    assert c.startswith("physical_quality means") and "fresh is physical_quality not process" in c and "olive oil" not in c and len(c.split()) <= 30
    assert "zzz" not in type_context(docs, "FOOD", labs) and "olive oil" in type_context(docs, "FOOD", labs)
