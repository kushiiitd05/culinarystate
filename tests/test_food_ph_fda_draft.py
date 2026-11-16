"""S176 L-PH: invariants of the DRAFT FDA/CFSAN approximate-pH registry and its ING crosswalk."""
import csv
import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "registry/food_ph_fda_draft_v1.csv"
XWALK = ROOT / "registry/food_ph_fda_ing_crosswalk_draft_v1.csv"
RAW = ROOT / "data/raw/fda_ph/wayback_20080223_lacf-phs.html"


def _rows(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_requested_columns_in_order():
    head = list(_rows(DRAFT)[0].keys())
    assert head[:12] == ["ph_id", "item_raw", "item_norm", "ph_low", "ph_high", "ph_value_type", "page",
                         "source_id", "source_url", "retrieved_at", "parse_status", "notes"]


def test_ids_sequential_and_count():
    rows = _rows(DRAFT)
    assert len(rows) == 488
    assert [r["ph_id"] for r in rows] == [f"FDAPH-{i:04d}" for i in range(1, 489)]


def test_no_invented_bounds():
    for r in _rows(DRAFT):
        lo = float(r["ph_low"]) if r["ph_low"] else None
        hi = float(r["ph_high"]) if r["ph_high"] else None
        if r["ph_value_type"] == "POINT":
            assert lo is not None and lo == hi
        if r["parse_status"] in ("PARSED_OPEN_ENDED", "UNPARSED_REVIEW"):
            assert hi is None  # printed '5.00 -' or '5.2l' must never become a POINT or a guessed bound
        if lo is not None and hi is not None:
            assert 0 <= lo <= hi <= 14
        if r["ph_value_type"] == "NONE":
            assert lo is None and hi is None


def test_snippy_typo_not_silently_repaired():
    r = [x for x in _rows(DRAFT) if x["item_raw"] == "Cheese, Snippy"][0]
    assert r["ph_raw"] == "5.18 - 5.2l" and r["parse_status"] == "UNPARSED_REVIEW" and r["ph_high"] == ""


def test_crosswalk_covers_every_ph_id_and_is_ai_drafted():
    ph_ids = {r["ph_id"] for r in _rows(DRAFT)}
    x = _rows(XWALK)
    assert {r["ph_id"] for r in x} == ph_ids
    assert {r["status"] for r in x} == {"AI_DRAFTED"}


def test_source_id_is_a_proposal_not_a_ledger_id():
    assert {r["source_id"] for r in _rows(DRAFT)} == {"SRC-PROPOSED-FDA-CFSAN-PH-2007"}


@pytest.mark.skipif(not RAW.exists(), reason="raw capture is git-ignored / server-local")
def test_raw_capture_hash_and_row_count():
    b = RAW.read_bytes()
    assert hashlib.sha256(b).hexdigest() == "f5b8faad71a83ff5b98ef1e7073e6405ac34730557903a89a70a8c058083d59f"
    assert b.decode("iso-8859-1").count("<tr>") - 1 == 488  # minus the header row
