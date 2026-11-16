"""S178 FIX-EVAL: SCI-B B5 (EVD transition no-imputation audit: complete violations block, per-row y = 0 check). Synthetic only.

Failure scenario (review): one imputed 0 plus one dropped measured 0 cancel out in the totals, and "0 violations" still shows;
two invariants (cells = MEASURED + CENSORED, y_train = y or y_lower) were not in the violations block.
"""
from __future__ import annotations

import pandas as pd

from tests.unit.test_s178_analysis_helpers import load_tool

TA = load_tool("s178_evd_transition_audit")


def rf_row(i, status, value=None):
    rf = {"status": status, "unit": "fraction"}
    if value is not None:
        rf["value"] = value
    return {"id": f"EVD-{i:06d}", "derived": {"retention_factor": rf}}


def test_an_imputed_zero_and_a_dropped_measured_zero_no_longer_cancel():
    rows = [rf_row(1, "MEASURED", 0.5), rf_row(2, "MEASURED", 0)]                    # E1 not zero at source; E2 a measured 0
    df = pd.DataFrame({"evd_id": ["EVD-000001"], "y": [0.0], "y_lower": [float("nan")], "censored": [False]})   # E1 -> 0, E2 dropped
    got = TA.y0_per_row(df, rows)
    assert got["cells_y_equal_0_whose_row_is_not_measured_0"] == 1
    assert got["measured_0_rows_whose_cell_is_missing_or_not_0"] == 1
    totals_based = int((df["y"] == 0).sum()) - sum(1 for r in rows if r["derived"]["retention_factor"].get("value") == 0)
    assert totals_based == 0                                                          # the v0.1 check saw nothing


def test_violations_block_carries_the_two_booleans_and_the_per_row_counts():
    fam = {"cells_equal_measured_plus_censored": False, "y_train_equals_y_or_y_lower_everywhere": True,
           "y_zero_per_row": {"cells_y_equal_0_whose_row_is_not_measured_0": 0, "measured_0_rows_whose_cell_is_missing_or_not_0": 2,
                              "measured_0_rows_with_a_y_0_cell": 0, "cells_with_duplicate_evd_id": 0}}
    tot = {k: 0 for k in ("cells_y_lower_equal_0", "cells_missing_y_and_not_censored", "cells_censored_with_y_filled",
                          "censored_rows_without_limit", "y_train_nan")}
    v = TA.violations({"F1": fam, "F2": {**fam, "cells_equal_measured_plus_censored": True,
                                         "y_train_equals_y_or_y_lower_everywhere": False}}, tot)
    assert v["families_where_cells_differ_from_measured_plus_censored"] == 1
    assert v["families_where_y_train_is_not_y_or_y_lower"] == 1
    assert v["measured_0_rows_whose_cell_is_missing_or_not_0"] == 4
    assert TA.OUT_NAME == "transition_no_imputation_audit_v2.json"
