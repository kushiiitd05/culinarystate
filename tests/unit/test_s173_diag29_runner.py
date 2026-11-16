"""S173: 29-diag runner (cap-stratified DEL-2 rerun, shortcut rerun, D7 vs D1) on synthetic EVD rows."""
from __future__ import annotations

import numpy as np

from culinarystate.evaluation import diag29_runner as R


def evd_rows(n=160, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        m, p = f"food{i % 16}", ("boil", "steam", "bake", "fry")[i % 4]
        censored = i % 7 == 0
        rf = {"status": "CENSORED", "censor": {"kind": "GT_CAP", "limit": 0.975}} if censored else \
            {"status": "MEASURED", "value": float(np.clip(0.5 + 0.1 * (i % 4) + rng.normal(0, 0.05), 0.05, 1.2)),
             "unit": "fraction"}
        out.append({"id": f"EVD-{i:06d}", "status": "ACTIVE", "source_family_id": "SYN", "tier": "E3",   # tier: schema-required (S178 GOV-10 firewall)
                    "matrix": {"raw_name": m, "form": "", "food_group": f"g{i % 4}", "ingredient_id": f"ING-{i % 16}"},
                    "process": {"steps": [p], "raw_name": p, "condition_id": None, "process_id": f"P-{p}"},
                    "target": {"raw_name": ("vitamin c", "folate")[i % 2], "basis": ("dry", "wet")[i % 2]},
                    "derived": {"retention_factor": rf}, "independence_group": f"G{i % 5}", "study_ids": []})
    return out


class PassCtx:
    def __init__(self):
        self.calls = []

    def filter_dev_rows(self, rows, *, id_column, group_columns):
        self.calls.append((id_column, tuple(group_columns)))
        return [r for r in rows if r["id"] != "EVD-000003"]   # pretend one reserved row


def test_runner_filters_at_cell_level_and_labels_output():
    ctx = PassCtx()
    out = R.run(ctx, evd_rows(), cond={}, families=["SYN"], seed=7, n_boot=20)
    assert ctx.calls == [("id", ("id",))]
    assert set(R.LABELS) <= set(out["labels"]) and out["rows_after_seal"] == 159
    fam = out["families"]["SYN"]
    assert fam["rows"] == 159 and fam["censored"] > 0 and fam["splits"]


def test_cap_strata_and_shortcut_and_d7_review_present():
    out = R.run(PassCtx(), evd_rows(), cond={}, families=["SYN"], seed=7, n_boot=20)
    any_split = next(iter(out["families"]["SYN"]["splits"].values()))
    d0 = any_split["D0"]
    assert {"mae_all", "mae_below_cap", "mae_at_cap", "mae_cap_rows_dropped_in_training"} <= set(d0)
    assert "shortcut_basis_removed" in out["families"]["SYN"]
    assert "d7_vs_d1_max_abs_pred_diff" in out["families"]["SYN"]


def test_deterministic():
    a = R.run(PassCtx(), evd_rows(), cond={}, families=["SYN"], seed=7, n_boot=20)
    b = R.run(PassCtx(), evd_rows(), cond={}, families=["SYN"], seed=7, n_boot=20)
    assert a == b
