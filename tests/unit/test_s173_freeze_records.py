"""S173: 15a bootstrap freeze record + 29-diag pre-registration signature (formats; human approval only counts)."""
from __future__ import annotations

import hashlib
import json

import pytest

from culinarystate.evaluation import freeze_records as FR


@pytest.fixture
def root(tmp_path):
    (tmp_path / "ledgers/data").mkdir(parents=True)
    for n in FR.FROZEN_LEDGERS:
        (tmp_path / "ledgers/data" / n).write_text(f"{n}\n")
    (tmp_path / "reports/step15").mkdir(parents=True)
    (tmp_path / FR.SEAL_COMMITMENT).write_text("{}")
    (tmp_path / "reports/step29").mkdir(parents=True)
    (tmp_path / FR.PREREG).write_text("# prereg v1\n")
    return tmp_path


def test_proposed_record_has_hashes_and_is_not_frozen(root):
    rec = FR.propose_freeze(root, "15A-BOOT-TEST")
    assert rec["status"] == "PROPOSED" and rec["approved_by"] is None
    assert rec["ledger_sha256"]["ledgers/data/EVD.jsonl"] == hashlib.sha256(b"EVD.jsonl\n").hexdigest()
    assert FR.frozen_snapshot_ids(root) == frozenset()


def test_only_human_approved_matching_record_counts(root):
    rec = FR.propose_freeze(root, "15A-BOOT-TEST")
    path = root / FR.FREEZE_DIR / "15A-BOOT-TEST.json"
    path.write_text(json.dumps({**rec, "status": "FROZEN", "approved_by": "Kush Tokas", "approved_date": "2026-11-09"}))
    assert FR.frozen_snapshot_ids(root) == frozenset({"15A-BOOT-TEST"})
    (root / "ledgers/data/EVD.jsonl").write_text("changed\n")
    assert FR.frozen_snapshot_ids(root) == frozenset()            # bytes moved: no longer frozen
    assert "SNAPSHOT_HASH_MISMATCH" in FR.freeze_problems(root, "15A-BOOT-TEST")


def test_agent_cannot_approve(root):
    rec = FR.propose_freeze(root, "15A-BOOT-TEST")
    path = root / FR.FREEZE_DIR / "15A-BOOT-TEST.json"
    path.write_text(json.dumps({**rec, "status": "FROZEN", "approved_by": "AI_AGENT", "approved_date": "2026-11-09"}))
    assert FR.frozen_snapshot_ids(root) == frozenset()


def test_propose_refuses_overwrite(root):
    FR.propose_freeze(root, "15A-BOOT-TEST")
    with pytest.raises(FileExistsError):
        FR.propose_freeze(root, "15A-BOOT-TEST")


def test_prereg_signature_must_match_current_text(root):
    assert FR.prereg_signed(root) is False
    sha = hashlib.sha256((root / FR.PREREG).read_bytes()).hexdigest()
    (root / FR.PREREG_SIGNATURE).write_text(json.dumps({"prereg_sha256": sha, "signed_by": "Kush Tokas",
                                                         "signed_date": "2026-11-09"}))
    assert FR.prereg_signed(root) is True
    (root / FR.PREREG).write_text("# prereg v1 edited after signing\n")
    assert FR.prereg_signed(root) is False
