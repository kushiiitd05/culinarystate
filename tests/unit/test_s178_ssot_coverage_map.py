"""S178 T0-C19-R1: every unanchored top-level SSOT section has a class; the anchor parser handles the notations."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import s178_ssot_coverage_map as M  # noqa: E402


def test_anchor_parser_handles_ranges_letters_and_plain_numbers():
    assert M.anchor_sections("§51; §61-§64; §143") == {"51", "61", "62", "63", "64", "143"}
    assert M.anchor_sections("§257G-§257K") == {"257G", "257H", "257I", "257J", "257K"}
    assert M.anchor_sections("§§174–183") == {str(n) for n in range(174, 184)}
    assert "12" in M.anchor_sections("§12.4.10 L11694-11726")
    assert M.line_ranges("§203.1 L17121-17190; L22382") == [(17121, 17190), (22382, 22382)]


def test_every_unanchored_section_has_a_valid_class_and_nothing_extra():
    assert M.problems() == []


def test_t0_c19_is_excluded_from_the_anchor_set():
    assert "T0-C19" in M.EXCLUDE
    by = M.anchored()
    assert all("T0-C19" not in v for v in by.values())


def test_map_rows_cover_all_sections_and_class_values_are_valid():
    rows = M.build()
    assert len(rows) == len(M.sections())
    for r in rows:
        if r["status"] == "UNANCHORED":
            assert r["class"] in M.VALID
        else:
            assert r["class"] == ""


def test_the_four_named_merge_registers_are_owned_by_t0_c01_r2():
    cls = M.read_classes()
    for s in ("184", "195", "206", "217"):
        assert cls[s]["class"] == "OWNER" and cls[s]["owner_or_superseded_by"] == "T0-C01-R2"


def test_committed_map_csv_matches_a_rebuild():
    with M.OUT.open(newline="") as fh:
        have = list(csv.DictReader(fh))
    want = M.build()
    assert [r["section"] for r in have] == [r["section"] for r in want]
    assert [r["class"] for r in have] == [r["class"] for r in want]
