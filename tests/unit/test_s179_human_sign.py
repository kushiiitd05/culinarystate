"""S179: the human-run signing helper writes only the signer's own file, binds the current text, never overwrites,
refuses non-human names (D-071), and approving a freeze edits only the three approval fields."""
import json
import runpy
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
M = runpy.run_path(str(ROOT / "tools/human_sign.py"), run_name="lib")


def _repo(tmp_path):
    for rel in ("reports/del5/d5_benchmark_preregistration_DRAFT.md", "reports/step29/29diag_preregistration_DRAFT.md",
                "reports/step10/aa_pilot_preregistration_DRAFT.md", "registry/freezes/15A-BOOT-2026-11-08.json"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, tmp_path / rel)
    return tmp_path


def test_sign_writes_the_signers_file_bound_to_the_text(tmp_path):
    r = _repo(tmp_path)
    p = M["sign"](r, "D5", "Kush Tokas", "2026-11-10")
    s = json.loads(p.read_text())
    assert p.name == "d5_prereg_signature_Kush.json" and s["signed_by"] == "Kush Tokas"
    assert s["prereg_sha256"] == M["sha"](r / "reports/del5/d5_benchmark_preregistration_DRAFT.md")
    assert set(s) == {"prereg_sha256", "signed_by", "signed_date"}
    with pytest.raises(SystemExit):
        M["sign"](r, "D5", "Kush Tokas", "2026-11-10")          # never overwrites


def test_29diag_signature_satisfies_the_checker(tmp_path):
    from culinarystate.evaluation.freeze_records import prereg_signed
    r = _repo(tmp_path)
    M["sign"](r, "D29", "Kush Tokas", "2026-11-10")
    assert prereg_signed(r)


@pytest.mark.parametrize("who", ["ksh", "prv", "AI_AGENT", "Claude", "kush", ""])
def test_refuses_anyone_but_the_two_humans(tmp_path, who):
    with pytest.raises(SystemExit):
        M["sign"](_repo(tmp_path), "D5", who, "2026-11-10")


def test_29diag_has_one_signer_only(tmp_path):
    with pytest.raises(SystemExit):
        M["sign"](_repo(tmp_path), "D29", "Parv Goyal", "2026-11-10")


def test_approve_freeze_sets_only_approval_fields(tmp_path):
    r = _repo(tmp_path)
    f = r / "registry/freezes/15A-BOOT-2026-11-08.json"
    before = json.loads(f.read_text())
    M["approve_freeze"](r, "15A-BOOT-2026-11-08", "Kush Tokas", "2026-11-10")
    after = json.loads(f.read_text())
    assert {k for k in after if after[k] != before.get(k)} == {"status", "approved_by", "approved_date"}
    assert after["status"] == "FROZEN" and after["approved_by"] == "Kush Tokas"
    with pytest.raises(SystemExit):
        M["approve_freeze"](r, "15A-BOOT-2026-11-08", "Kush Tokas", "2026-11-10")
