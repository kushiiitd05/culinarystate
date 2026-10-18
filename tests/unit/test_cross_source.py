import pandas as pd

from culinarystate.transition.cross_source import agreement, coarse_group, nutrient_key, prepare_groups


def test_keys():
    assert nutrient_key("Thiamin") == "vitamin_b1" and nutrient_key("Vitamin C, total ascorbic acid") == "vitamin_c"
    assert nutrient_key("Protein") is None
    assert coarse_group("Poultry Products") == "POULTRY" and coarse_group("vegetable based dishes") == "VEGETABLE"
    assert coarse_group("offal based dishes") == "OFFAL"


def _df(fg, step, target, y, censored=False, form=""):
    return {"evd_id": f"E{fg}{step}{target}{y}", "food_group": fg, "process_family": step, "target": target,
            "y": None if censored else y, "y_lower": y if censored else None, "censored": censored, "matrix_form": form}


def test_group_alignment_and_agreement():
    a = prepare_groups(pd.DataFrame([_df("Vegetables and Vegetable Products", "boil", "Vitamin C", 0.5),
                                     _df("Vegetables and Vegetable Products", "simmer", "Vitamin C", 0.7)]))
    b = prepare_groups(pd.DataFrame([_df("vegetable based dishes", "boil", "Vitamin C", 0.4),
                                     _df("vegetable based dishes", "pan-fry", "Vitamin C", 0.9, form="breaded")]))
    assert len(b) == 1                                                          # breaded excluded
    r = agreement(a, b)
    assert r["overlap_cells"] == 1 and abs(r["mae_same_cell"] - 0.2) < 1e-9     # A mean 0.6 vs B 0.4
