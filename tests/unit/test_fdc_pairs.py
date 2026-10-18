import pandas as pd

from culinarystate.evidence.fdc_pairs import dry_basis_ratio, pair_foods, split_state


def test_split_state():
    assert split_state("Broccoli, raw") == ("broccoli", "RAW", None, None)
    assert split_state("Broccoli, cooked, boiled, drained, without salt") == ("broccoli", "COOKED", "boil", False)
    assert split_state("Broccoli, frozen, chopped, cooked, boiled, drained, with salt") == \
        ("broccoli|frozen|chopped", "COOKED", "boil", True)
    assert split_state("Beef, ground, 80% lean meat / 20% fat, cooked, pan-browned") == \
        ("beef|ground|80% lean meat / 20% fat", "COOKED", "fry", None)
    assert split_state("Broccoli, chinese, cooked") == ("broccoli|chinese", "COOKED", None, None)
    assert split_state("Pillsbury, Cinnamon Rolls with Icing, refrigerated dough")[1] is None


def test_pair_foods_prefers_unsalted():
    df = pd.DataFrame({"fdc_id": [1, 2, 3, 4], "description": [
        "Broccoli, raw", "Broccoli, cooked, boiled, drained, with salt",
        "Broccoli, cooked, boiled, drained, without salt", "Kale, cooked, boiled"]})
    p = pair_foods(df)
    assert p[["raw_id", "cooked_id", "method"]].values.tolist() == [[1, 3, "boil"]]   # kale has no raw partner


def test_dry_basis_ratio():
    # 10 mg/100 g raw at 90% water -> 100 mg/100 g solids; cooked 12 mg at 92% water -> 150 mg/100 g solids
    assert dry_basis_ratio(10, 90, 12, 92) == 1.5
    assert dry_basis_ratio(0, 90, 1, 92) is None and dry_basis_ratio(1, 100, 1, 92) is None
