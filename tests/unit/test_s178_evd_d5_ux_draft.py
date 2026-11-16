"""S178 EVD lane, T8-C20-R4: the U / X draft rows keep the pre-registered shape and never claim a review."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
_spec = importlib.util.spec_from_file_location("s178_evd_d5_ux_draft", ROOT / "tools/s178_evd_d5_ux_draft.py")
UX = importlib.util.module_from_spec(_spec)
sys.modules["s178_evd_d5_ux_draft"] = UX
_spec.loader.exec_module(UX)


def facts():
    ing = {"ING-000166": "ricotta", "ING-000771": "cottage cheese", "ING-000058": "cornflour", "ING-001568": "potato starch", "ING-000319": "saffron",
           "ING-000212": "tahini", "ING-000017": "carrot"}
    proc = {"PROC-000022": "steam", "PROC-000007": "microwave"}
    edge = lambda s, o: {"s": s, "o": o, "corpora": ["WIKIBOOKS-COOKBOOK"], "method": "CO_OCCURRENCE", "band": "LOW"}   # noqa: E731
    alt = {"KGE-016693": edge("ING-000166", "ING-000771"), "KGE-016692": edge("ING-000771", "ING-000166"),
           "KGE-046037": edge("ING-000058", "ING-001568"), "KGE-046036": edge("ING-001568", "ING-000058")}
    return {"ing": ing, "proc": proc, "alt": alt, "alt_degree": {"ING-000166": 2, "ING-000771": 2, "ING-000058": 2, "ING-001568": 2}, "evd_rows": {}}


def test_rows_have_the_preregistered_shape_and_pass_validation():
    rows = UX.rows_with_ids()
    assert [r["qid"] for r in rows] == [f"D5-U-00{i}" for i in range(1, 6)] + [f"D5-X-00{i}" for i in range(1, 6)]
    assert UX.validate(rows, facts()) == []
    assert sum(1 for r in rows if r["gold_mode"] == "REFUSE") == 3
    assert all(r["status"] == "DRAFT_FOR_REVIEW" and r["drafted_by"] == "AI_AGENT_S178_EVD" for r in rows)
    assert not any("REVIEWED" in r["status"].upper().replace("UNREVIEWED", "") for r in rows)


@pytest.mark.parametrize("mutate,expect", [
    (lambda r: r[0].update(status="REVIEWED"), "status"),
    (lambda r: r[5].update(gold_mode="ANSWER"), "3 safety"),
    (lambda r: r[2].update(ingredient_id="ING-000166", food="ricotta"), "ALTERNATIVE edges"),          # 'no edge' claim made false
    (lambda r: r[0].update(gold_graph_edge_ids="KGE-000001|KGE-016692"), "not an ACTIVE"),
    (lambda r: r[1].update(question="Can I swap cornflour for potato starch for 5 g?"), "digit"),
    (lambda r: r[3].update(question="What replaces tahini for more vitamin C?"), "nutrient"),
    (lambda r: r[0].update(food="cheese"), "name"),
])
def test_validation_catches_stale_or_unsafe_rows(mutate, expect):
    rows = UX.rows_with_ids()
    mutate(rows)
    assert any(expect in p for p in UX.validate(rows, facts()))


def test_committed_copy_matches_the_generator_when_present():
    p = ROOT / "reports/s178/evd/d5_UX_blocks_S178_DRAFT.csv"
    if not p.is_file():
        pytest.skip("draft not generated in this tree")
    assert p.read_text(encoding="utf-8") == UX.to_csv(UX.rows_with_ids())
    got = list(csv.DictReader(p.open(encoding="utf-8", newline="")))
    assert list(got[0].keys()) == UX.COLS and len(got) == 10
