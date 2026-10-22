import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import step07_provenance_precheck as pc  # noqa: E402

HEADER = ["audit_id", "raw_duration", "normalised_duration", "duration_judgement", "temperature_location_judgement", "overall_judgement", "reason_if_not_correct"]


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)


def base():
    return [{"audit_id": f"A{i}", "raw_duration": f"{i} min", "normalised_duration": f"{i*60}", "duration_judgement": "", "temperature_location_judgement": "", "overall_judgement": "", "reason_if_not_correct": ""} for i in range(4)]


def filled(rows, code):
    return [{**r, "duration_judgement": code, "temperature_location_judgement": code, "overall_judgement": "ACCEPT"} for r in rows]


def make_case(tmp_path, a_code="CORRECT", b_code="CORRECT", gap=3600):
    blank, a, b = tmp_path / "blank.csv", tmp_path / "a.csv", tmp_path / "b.csv"
    write(blank, base())
    write(a, filled(base(), a_code))
    write(b, filled(base(), b_code))
    t = os.path.getmtime(a)
    os.utime(b, (t + gap, t + gap))
    return blank, a, b


def test_valid_pair(tmp_path):
    blank, a, b = make_case(tmp_path, "CORRECT", "WRONG_VALUE")
    r = pc.precheck(blank, a, b, 600)
    assert r["status"] == "VALID" and r["problems"] == []


def test_identical_files_flagged(tmp_path):
    blank, a, b = make_case(tmp_path)
    b.write_bytes(a.read_bytes())
    t = os.path.getmtime(a)
    os.utime(b, (t + 3600, t + 3600))
    r = pc.precheck(blank, a, b, 600)
    assert r["status"] == "INVALID_PROVENANCE" and any("byte-identical" in p for p in r["problems"])


def test_close_mtimes_flagged(tmp_path):
    blank, a, b = make_case(tmp_path, "CORRECT", "WRONG_VALUE", gap=11)
    r = pc.precheck(blank, a, b, 600)
    assert r["status"] == "INVALID_PROVENANCE" and any("mtime" in p for p in r["problems"])


def test_edited_frozen_cell_flagged(tmp_path):
    blank, a, b = make_case(tmp_path, "CORRECT", "WRONG_VALUE")
    rows = filled(base(), "WRONG_VALUE")
    rows[2]["normalised_duration"] = "tampered"
    write(b, rows)
    t = os.path.getmtime(a)
    os.utime(b, (t + 3600, t + 3600))
    r = pc.precheck(blank, a, b, 600)
    assert r["status"] == "INVALID_PROVENANCE" and any("frozen" in p for p in r["problems"])


def test_header_change_flagged(tmp_path):
    blank, a, b = make_case(tmp_path, "CORRECT", "WRONG_VALUE")
    with open(b, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADER + ["extra"])
        w.writeheader()
        w.writerows([{**r, "extra": "x"} for r in filled(base(), "WRONG_VALUE")])
    r = pc.precheck(blank, a, b, 600)
    assert r["status"] == "INVALID_PROVENANCE" and any("header" in p for p in r["problems"])


def test_never_writes_labels(tmp_path):
    blank, a, b = make_case(tmp_path, "CORRECT", "WRONG_VALUE")
    before = (a.read_bytes(), b.read_bytes(), blank.read_bytes())
    pc.precheck(blank, a, b, 600)
    assert before == (a.read_bytes(), b.read_bytes(), blank.read_bytes())
