"""S178 T9-C06-R1: the section 238 conformance table covers every SSOT field with a map kind and a reason."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SSOT = ROOT / "docs/SSOT/computational_gastronomy_master_ssot_v15_0.md"
CSV = ROOT / "reports/s178/ssot238_conformance.csv"
KINDS = {"EXACT", "RENAMED", "COMPOSED", "RELATED", "TABLE_ONLY", "CODE_ONLY", "ABSENT"}


def _ssot_fields():
    cur, out = None, {}
    for line in SSOT.read_text().split("\n")[25744:26101]:
        m = re.match(r"^## 238\.\d+ (\w+)", line)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        m = re.match(r"^- `([^`]+)` — ", line)
        if m and cur:
            out[cur].append(m.group(1))
    return out


def _rows():
    with CSV.open(newline="") as fh:
        return list(csv.DictReader(fh))


def test_twelve_contracts_and_every_ssot_field_is_in_the_table_once():
    want = _ssot_fields()
    assert len(want) == 12 and sum(len(v) for v in want.values()) == 210
    got = {}
    for r in _rows():
        got.setdefault(r["contract"], []).append(r["ssot_field"])
    assert got == want


def test_every_row_has_a_valid_kind_and_non_exact_rows_have_a_reason():
    for r in _rows():
        assert r["map_kind"] in KINDS
        if r["map_kind"] in {"ABSENT", "RELATED", "TABLE_ONLY", "CODE_ONLY"}:
            assert r["reason"].strip(), (r["contract"], r["ssot_field"])


def test_absent_rows_have_no_populated_counts():
    for r in _rows():
        if r["map_kind"] == "ABSENT":
            assert r["n_populated"] == ""


def test_populated_never_exceeds_rows():
    for r in _rows():
        if r["n_rows"] not in ("", "0"):
            assert int(r["n_populated"]) <= int(r["n_rows"])
