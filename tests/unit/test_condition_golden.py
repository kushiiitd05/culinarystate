"""Step 07H golden syntax suite (frozen: tests/golden/condition_syntax_golden_v1.json). Expectations were written by hand from the contract, not copied from output."""
import json
from pathlib import Path

import pytest

from culinarystate.evidence import condition_normalizer as N

GOLD = json.loads((Path(__file__).resolve().parents[1] / "golden" / "condition_syntax_golden_v1.json").read_text(encoding="utf-8"))


def _ck(res, e):
    for k in ("value_type", "status", "approximate", "pressure_reference", "open_low", "open_high"):
        if k in e:
            assert res.get(k, False if k == "approximate" else None) == e[k], (k, res)
    for k in ("canonical_value", "canonical_low", "canonical_high"):
        if k in e:
            if e[k] is None:
                assert res.get(k) is None, (k, res)
            else:
                assert res.get(k) == pytest.approx(e[k], rel=1e-9, abs=1e-9), (k, res)
    if e.get("absent_canonical"):
        assert res.get("canonical_value") is None and res.get("canonical_low") is None
    for r in e.get("reasons_include", []):
        assert r in res["reasons"], (r, res)
    if "uncertainty_canonical" in e:
        assert res["uncertainty"]["canonical_value"] == pytest.approx(e["uncertainty_canonical"])
        assert res.get("canonical_low") is None and res.get("canonical_high") is None  # uncertainty is NOT turned into a range
    if "uncertainty_type" in e:
        assert res["uncertainty"]["type"] == e["uncertainty_type"]
    if "censor_kind" in e:
        assert res["censoring"]["kind"] == e["censor_kind"]


@pytest.mark.parametrize("case", GOLD, ids=[c["id"] + ":" + c["raw"] for c in GOLD])
def test_golden(case):
    res = N.normalize_text(case["var"], case["raw"], location=case["location"], basis=case["basis"])
    assert res["raw"] == case["raw"]  # raw text always retained
    _ck(res, case["expect"])


def test_golden_size_and_variants():
    assert len(GOLD) >= 120
