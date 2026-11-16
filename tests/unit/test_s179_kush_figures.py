"""T3-C17-R2 / T6-C02-R3 figure series come only from the committed JSON."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("kf", ROOT / "tools" / "s179_kush_figures.py")
kf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kf)


def test_type_series_skips_types_without_gold_or_pred():
    d = {"sets": {"S": {"n_recipes": 2, "label_basis": "B", "types": {
        "Merge": {"gold": 3, "pred": 2, "precision": 1.0, "precision_ci95": [0.9, 1.0], "recall": 0.6,
                  "recall_ci95": [0.4, 0.8]},
        "Reserve": {"gold": 0, "pred": 0, "precision": None, "precision_ci95": None, "recall": None,
                    "recall_ci95": None}}}}}
    s = kf.type_series(d)
    assert list(s["S"]["types"]) == ["Merge"]
    assert s["S"]["types"]["Merge"]["recall_ci95"] == [0.4, 0.8]


def test_paired_grid_marks_ci_sign_and_low_cluster():
    d = {"result": {"families": {"F": {"splits": {
        "random": {"D1": {"estimate": 0.1, "lower95": 0.05, "upper95": 0.2, "label": "DIAGNOSTIC;X"},
                   "D2": {"estimate": -0.1, "lower95": -0.2, "upper95": -0.01, "label": "DIAGNOSTIC_ONLY;X"},
                   "D3": {"estimate": 0.0, "lower95": -0.1, "upper95": 0.1, "label": "DIAGNOSTIC;X"}},
        "empty": {"refused": ["EMPTY_FOLD"]}}}}}}
    g = kf.paired_grid(d)
    cells = g["F"]["random"]
    assert cells["D1"]["sign"] == "+" and cells["D2"]["sign"] == "-" and cells["D3"]["sign"] == "0"
    assert cells["D2"]["low_clusters"] is True and cells["D1"]["low_clusters"] is False
    assert "empty" not in g["F"]
