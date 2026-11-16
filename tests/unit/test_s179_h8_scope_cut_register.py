"""H8 scope-cut register (T9-C07-R4, D-089): every cut has a status, report wording and existing evidence path."""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REG = REPO / "registry" / "h8_scope_cut_register_v1.csv"
STATUSES = {"DELIVERED", "DIAGNOSTIC", "DECLARED_NOT_RUN", "NOT_DELIVERED_AT_THIS_SCALE"}
REQUIRED = ("D2", "H2", "H4", "Step 20", "Step 28", "Step 33", "Step 34", "FlavorTwin", "40 recipes",
            "8-scenario", "Levels 10-11")


def _rows() -> list[dict[str, str]]:
    with REG.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_every_listed_promise_has_a_row():
    promises = " | ".join(r["proposal_promise"] for r in _rows())
    for item in REQUIRED:
        assert item in promises, item


def test_rows_have_status_wording_and_existing_evidence():
    for r in _rows():
        assert r["status"] in STATUSES, r["cut_id"]
        assert len(r["report_wording"]) > 40, r["cut_id"]
        for part in r["evidence"].split(";"):
            path = re.split(r"[ :]", part.strip(), maxsplit=1)[0]
            assert (REPO / path).exists(), (r["cut_id"], path)


def test_no_banned_claim_words():
    text = REG.read_text(encoding="utf-8").lower()
    for word in ("supported", "beats", "validated "):
        assert word not in text, word


def test_d089_locks_this_exact_table_under_the_delegate():
    decisions = (REPO / "DECISIONS.md").read_text(encoding="utf-8")
    m = re.search(r"### D-089 .*?(?=\n### D-|\Z)", decisions, re.S)
    assert m, "D-089 missing"
    entry = m.group(0)
    assert hashlib.sha256(REG.read_bytes()).hexdigest() in entry
    assert "ksh+prv (AI, D-085)" in entry and "NO_HUMAN_SIGNOFF_D085" in entry
    assert {r["decision"] for r in _rows()} == {"D-089"}
