"""Plan L4: effect-map rows and merge are counts/values from EVD only."""
from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("em", ROOT / "tools" / "s179_effect_map_224.py")
em = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(em)


def test_effect_rows_value_summary_and_order():
    direct = {"S1|I1|P1": Counter({"E1": 3, "E2": 1}), "S2|I2|P2": Counter({"E3": 9})}
    evd = {"E1": {"value": 0.4, "unit": "fraction"}, "E2": {"value": 0.6, "unit": "fraction"}, "E3": {"value": None}}
    rows = em.effect_rows(direct, evd)
    assert [r["target"] for r in rows] == ["S2", "S1"]
    s1 = rows[1]
    assert s1["direct_items"] == 4 and s1["n_evd"] == 2 and s1["value_median"] == 0.5 and s1["unit"] == "fraction"
    assert rows[0]["value_median"] is None


def test_merge_adds_counts():
    a, b = em._empty(), em._empty()
    a["recipes"]["F"] += 2; b["recipes"]["F"] += 3
    a["direct"]["S|I|P"]["E1"] += 1; b["direct"]["S|I|P"]["E1"] += 2
    m = em.merge([a, b])
    assert m["recipes"]["F"] == 5 and m["direct"]["S|I|P"]["E1"] == 3
