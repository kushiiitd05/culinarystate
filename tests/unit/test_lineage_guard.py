import shutil
from pathlib import Path

import pytest

from culinarystate.lineage.guard import (LedgerBaselineMismatch, ProtectedPathError,
                                         assert_safe_write_target, verify_baseline)

REPO = Path(__file__).resolve().parents[2]
CSV = REPO / "registry" / "baseline_ledger_hashes_08a_v1.csv"


def _mini(tmp_path):
    """Tiny fake root + CSV with 2 files (full-size ledgers are not copied)."""
    import csv, hashlib
    root = tmp_path / "root"
    (root / "ledgers" / "data").mkdir(parents=True)
    rows = []
    for name, body in (("STUDY.jsonl", b'{"a":1}\n{"b":2}\n'), ("SRC.jsonl", b'{"c":3}\n')):
        p = root / "ledgers" / "data" / name
        p.write_bytes(body)
        rows.append({"path": f"ledgers/data/{name}", "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
    c = tmp_path / "b.csv"
    with c.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "bytes", "sha256"])
        w.writeheader(); w.writerows(rows)
    return root, c


def test_real_repo_matches_real_csv():
    assert verify_baseline(CSV, REPO) == 7


def test_ok_on_mini(tmp_path):
    root, c = _mini(tmp_path)
    assert verify_baseline(c, root) == 2


def test_one_byte_changed_raises_with_name(tmp_path):
    root, c = _mini(tmp_path)
    p = root / "ledgers" / "data" / "SRC.jsonl"
    p.write_bytes(b'{"c":4}\n')
    with pytest.raises(LedgerBaselineMismatch, match="SRC.jsonl"):
        verify_baseline(c, root)


def test_study_prefix_change_detected(tmp_path):
    root, c = _mini(tmp_path)
    p = root / "ledgers" / "data" / "STUDY.jsonl"
    p.write_bytes(b'{"z":1}\n' + p.read_bytes()[8:])  # same size, changed prefix
    with pytest.raises(LedgerBaselineMismatch, match="STUDY.jsonl"):
        verify_baseline(c, root)


def test_size_change_and_missing_file(tmp_path):
    root, c = _mini(tmp_path)
    q = root / "ledgers" / "data" / "SRC.jsonl"
    q.write_bytes(q.read_bytes() + b"x")
    with pytest.raises(LedgerBaselineMismatch, match="SRC.jsonl"):
        verify_baseline(c, root)
    q.write_bytes(q.read_bytes()[:-1])
    p = root / "ledgers" / "data" / "STUDY.jsonl"
    p.unlink()
    with pytest.raises(LedgerBaselineMismatch, match="STUDY.jsonl"):
        verify_baseline(c, root)


@pytest.mark.parametrize("rel", ["ledgers/data/EVD.jsonl", "ledgers/data/COND.jsonl", "ledgers/data/_ids.jsonl",
                                 "ledgers/data/SNAP.jsonl", "exports/evd/v1/x.csv", "ledgers/data/new.jsonl"])
def test_protected_targets_rejected(rel):
    with pytest.raises(ProtectedPathError):
        assert_safe_write_target(REPO / rel)


def test_traversal_into_protected_rejected():
    with pytest.raises(ProtectedPathError):
        assert_safe_write_target(REPO / "scratch" / ".." / "ledgers" / "data" / "EVD.jsonl")


def test_scratch_paths_accepted(tmp_path):
    assert_safe_write_target(tmp_path / "x.jsonl")
    assert_safe_write_target(REPO / "reports" / "step08a" / "x.csv")
    assert_safe_write_target(REPO / "ledgers" / "schemas" / "x.json")


def test_append_only_files_may_grow_but_not_change(tmp_path):
    root, c = _mini(tmp_path)
    study = root / "ledgers" / "data" / "STUDY.jsonl"
    study.write_bytes(study.read_bytes() + b'{"c":3}\n')
    assert verify_baseline(c, root) == 2
    study.write_bytes(b'{"X":1}\n{"b":2}\n{"c":3}\n')
    with pytest.raises(LedgerBaselineMismatch):
        verify_baseline(c, root)


def test_other_files_must_stay_exact(tmp_path):
    root, c = _mini(tmp_path)
    src = root / "ledgers" / "data" / "SRC.jsonl"
    src.write_bytes(src.read_bytes() + b"x")
    with pytest.raises(LedgerBaselineMismatch):
        verify_baseline(c, root)
