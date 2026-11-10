"""S179 D-085: the exact AI delegate string may approve a freeze and lock a prereg; any other AI marker still may not;
the approver kind is reported so outputs carry NO_HUMAN_SIGNOFF_D085."""
import hashlib
import json

import pytest

from culinarystate.evaluation import freeze_records as FR


@pytest.fixture
def root(tmp_path):
    (tmp_path / "ledgers/data").mkdir(parents=True)
    for n in FR.FROZEN_LEDGERS:
        (tmp_path / "ledgers/data" / n).write_text("{}\n")
    (tmp_path / "reports/step29").mkdir(parents=True)
    (tmp_path / FR.PREREG).write_text("prereg text\n")
    return tmp_path


def _approve(root, who):
    rec = FR.propose_freeze(root, "15A-BOOT-T")
    (root / FR.FREEZE_DIR / "15A-BOOT-T.json").write_text(
        json.dumps({**rec, "status": "FROZEN", "approved_by": who, "approved_date": "2026-11-10"}))


def test_delegate_can_approve_and_is_reported(root):
    _approve(root, FR.AI_DELEGATE)
    assert "15A-BOOT-T" in FR.frozen_snapshot_ids(root)
    assert FR.approval_kind(root, "15A-BOOT-T") == "AI_DELEGATED_D085"


@pytest.mark.parametrize("who", ["AI_AGENT", "ksh", "prv", "ksh+prv", "Claude"])
def test_other_ai_markers_still_refused(root, who):
    _approve(root, who)
    assert FR.frozen_snapshot_ids(root) == frozenset()


def test_prereg_lock_by_delegate(root):
    sha = hashlib.sha256((root / FR.PREREG).read_bytes()).hexdigest()
    (root / FR.PREREG_SIGNATURE).write_text(json.dumps({"prereg_sha256": sha, "signed_by": FR.AI_DELEGATE,
                                                        "signed_date": "2026-11-10"}))
    assert FR.prereg_signed(root) and FR.prereg_signer_kind(root) == "AI_DELEGATED_D085"
    _approve(root, "Kush Tokas")
    assert FR.approval_kind(root, "15A-BOOT-T") == "HUMAN"
