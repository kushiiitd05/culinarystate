from collections import Counter

import pytest

from culinarystate.ingest.acquire import Snapshot
from culinarystate.ingest.usda_r6 import R6Row, factor_qvalue, parse_desc
from culinarystate.ingest.usda_r6_build import build
from culinarystate.ledgers.store import LedgerStore
from culinarystate.ledgers.validate import errors


@pytest.mark.parametrize("desc,matrix,steps,mods", [
    ("CHEESE,BAKED", "CHEESE", ("bake",), {}),
    ("VEG,GREENS,BOILD,LITTLE WATER DRAIN", "VEG,GREENS", ("boil", "drain"), {"cooking_water": "LITTLE_DRAINED"}),
    ("POTATOES,BOILED(PARED) WATER USED", "POTATOES", ("boil",), {"cooking_water": "CONSUMED", "skin": "PARED"}),
    ("ORGAN MEATS(NOTLIVER)SIMMRD,WO/DRIP", "ORGAN MEATS NOTLIVER", ("simmer",), {"drippings_included": False}),
    ("SHELLFISH,WO/SHELL,FRIED,W/COATING", "SHELLFISH", ("fry",), {"coating": True, "shell": "OFF"}),
    ("LEGUMES,CKD 45/75MIN,BOILED+BAKED", "LEGUMES", ("boil", "bake"), {}),
    ("FRUITS,CANNED", "FRUITS", ("can",), {}),
    ("CHEESE,COOKED W/LIQUID", "CHEESE", ("cook",), {"medium": "liquid"}),
    ("PASTA,BOILED,NOT DRAINED", "PASTA", ("boil",), {"cooking_water": "NOT_DRAINED"}),
])
def test_parse_desc(desc, matrix, steps, mods):
    p = parse_desc(desc)
    assert p.matrix_raw == matrix
    assert p.steps == steps
    for k, v in mods.items():
        assert p.modifiers[k] == v
    assert p.raw == desc and p.unparsed == ()


def test_durations():
    assert parse_desc("LEGUMES,CKD 2/2.5HRS,BLD,WATER USED").duration_min == (120.0, 150.0)
    assert parse_desc("MILK,HEATED APPROX 10MIN").duration_min == (10.0, 10.0)
    assert parse_desc("ALC BEV,STIRRED,BKD/SIMMRD 1.5 HR").duration_min == (90.0, 90.0)
    assert parse_desc("CHEESE,BAKED").duration_min is None


def test_cook_dropped_when_specific_step_present():
    assert "cook" not in parse_desc("LEGUMES,CKD 15/20MIN,BOILED,DRAINED").steps


def test_factor_qvalue():
    assert factor_qvalue("")["status"] == "UNKNOWN"
    capped = factor_qvalue("100")
    assert capped["status"] == "CENSORED" and capped["censor"] == {"kind": "GT_CAP", "limit": 97.5}
    assert "value" not in capped                       # never claim exactly 100
    m = factor_qvalue("85")
    assert m == {"status": "MEASURED", "value": 85.0, "unit": "%", "uncertainty": 2.5, "raw": "85"}


def _rows():
    return [R6Row(1, "0001", "01", "CHEESE,BAKED", "401", "Vitamin C, total ascorbic acid", "65", "09/1975"),
            R6Row(2, "0001", "01", "CHEESE,BAKED", "301", "Calcium, Ca", "100", "09/1975"),
            R6Row(3, "5005", "14", "ALC BEV,STIRRED,BKD/SIMMRD 30 MIN", "301", "Calcium, Ca", "", "09/1975")]


def _snap():
    return [Snapshot("http://x/retn06.txt", "data/raw/usda_r6/retn06.txt", "c" * 64, 10,
                     "2026-10-18T05:00:00+00:00", 200)]


def test_build_end_to_end_and_idempotent(tmp_path):
    st = LedgerStore(tmp_path)
    c1 = build(st, _rows(), _snap())
    assert c1[("EVD", "created")] == 3 and c1[("COND", "created")] == 2 and c1[("SVAR", "created")] == 2
    evd = {e["target"]["raw_name"] + e["process"]["raw_name"]: e for e in st.all_latest("EVD")}
    vc = evd["Vitamin C, total ascorbic acidCHEESE,BAKED"]
    assert vc["tier"] == "E3" and vc["derived"]["direction"] == "DECREASE" and not vc["censored"]
    ca = evd["Calcium, CaCHEESE,BAKED"]
    assert ca["censored"] and ca["derived"]["direction"] == "UNKNOWN"
    alc = evd["Calcium, CaALC BEV,STIRRED,BKD/SIMMRD 30 MIN"]
    assert alc["derived"]["retention_factor"]["status"] == "UNKNOWN"
    cond = st.latest(alc["process"]["condition_id"])
    assert cond["duration"]["value"] == 30.0 and cond["completeness_mask"]["temperature"] == "UNKNOWN"
    assert all(errors(e) == [] for e in st.all_latest("EVD"))
    c2 = build(LedgerStore(tmp_path), _rows(), _snap())
    assert set(a for _, a in c2) == {"unchanged"}


def test_build_revision_keeps_history(tmp_path):
    build(LedgerStore(tmp_path), _rows(), _snap())
    rows = _rows()
    rows[0] = R6Row(1, "0001", "01", "CHEESE,BAKED", "401", "Vitamin C, total ascorbic acid", "70", "09/1975")
    c = build(LedgerStore(tmp_path), rows, _snap())
    assert c[("EVD", "revised")] == 1
    st = LedgerStore(tmp_path)
    vc = [e for e in st.all_latest("EVD") if e["target"]["raw_name"].startswith("Vitamin C")][0]
    hist = st.history(vc["id"])
    assert [h["derived"]["retention_factor"]["value"] for h in hist] == [65.0, 70.0]
    assert Counter(h["version"] for h in hist) == Counter({1: 1, 2: 1})
