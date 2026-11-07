"""DRAFT_PENDING_29diag_PREREG -- tests for the 29-diag TRANSITION_BOOTSTRAP_V0 runner.

On the real repository the runner must refuse. Since the 15a.R seal (S165-S170) the signed 15.0
ruling and the seal commitment exist, so the remaining blockers are no frozen bootstrap snapshot, no
signed 29-diag pre-registration and, when the private sealed list is not supplied, SEALED_LIST_MISSING. The success path is
exercised only on a synthetic root with the freeze/pre-registration hooks monkeypatched
inside the test; nothing here reads EVD.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.evaluation import bootstrap_diag as bd
from culinarystate.lineage import reserved_seal as rs

REPO = Path(__file__).resolve().parents[2]
SEED = "synthetic-seed"
SEED_SHA = hashlib.sha256(SEED.encode()).hexdigest()


def _codes(exc) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


def test_no_frozen_bootstrap_snapshot_exists():
    assert bd.frozen_bootstrap_snapshot_ids(REPO) == frozenset()
    assert bd.diag_preregistration_signed(REPO) is False


@pytest.mark.parametrize("snap", ["ES-1.1", "ledgers/data/EVD.jsonl", "LIVE", "", "15a"])
def test_real_repository_refuses_every_snapshot(snap):
    calls = []
    with pytest.raises(bd.DiagRefused) as exc:
        bd.run_bootstrap_diag(snap, calls.append, root=REPO)
    codes = _codes(exc)
    assert {"SNAPSHOT_NOT_FROZEN", "DIAG_PREREG_UNSIGNED", "SEALED_LIST_MISSING"} <= codes
    assert calls == []


def test_blockers_are_all_collected_not_first_only():
    blockers = bd.collect_diag_blockers(root=REPO, snapshot_id="x", commitment_path=None, sealed_list_path=None)
    assert len(blockers) >= 3


# ---------------------------------------------------------------- synthetic root

def _decision() -> str:
    return ("# DECISIONS\n\n### D-901 · 2026-01-02 · 15.0 pre-freeze rulings (synthetic)\n"
            "- **15.0 RESERVED_FRACTION:** 1/4\n- **15.0 RESERVED_UNIT:** CELL\n"
            "- **15.0 RESERVED_STRATIFY:** NONE\n"
            f"- **15a.R SEED_SHA256:** {SEED_SHA}\n- **Approver:** Kush (synthetic test entry)\n")


@pytest.fixture
def world(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "reports/step15").mkdir(parents=True)
    (root / "DECISIONS.md").write_text(_decision(), encoding="utf-8")
    rows = [{"id": f"EVD-{i}", "status": "ACTIVE", "source_family_id": "F", "independence_group": "F",
             "matrix": {"raw_name": f"M{i}"}, "process": {"steps": ["boil"], "modifiers": {}},
             "study_ids": [], "study_id_status": "NOT_IDENTIFIABLE"} for i in range(8)]
    groups = rs.build_groups(rows, "CELL")
    reserved = rs.select_reserved(groups, snapshot_sha256="syn", seed=SEED, fraction=Fraction(1, 4), stratify="NONE")
    sealed = rs.sealed_list_bytes(reserved, groups)
    ruling = rs.find_ruling(_decision(), "D-901")
    commitment = rs.build_commitment(ruling=ruling, groups=groups, reserved=reserved, sealed_bytes=sealed,
                                     snapshot={"evd_sha256": "syn"})
    (root / rs.COMMITMENT_PATH).write_text(json.dumps(commitment), encoding="utf-8")
    private = tmp_path / "private"
    private.mkdir()
    (private / "sealed.jsonl").write_bytes(sealed)
    monkeypatch.setattr(bd, "frozen_bootstrap_snapshot_ids", lambda root: frozenset({"SYN-15A-SNAPSHOT"}))
    monkeypatch.setattr(bd, "diag_preregistration_signed", lambda root: True)
    return {"root": root, "sealed": private / "sealed.jsonl", "rows": rows, "reserved": set(reserved)}


def test_synthetic_world_runs_and_output_is_non_citable(world):
    seen = []

    def runner(ctx):
        kept = ctx.filter_dev_rows(world["rows"], id_column="id", group_columns=("id",))
        seen.append(len(kept))
        return {"n_dev_rows": len(kept)}

    out = bd.run_bootstrap_diag("SYN-15A-SNAPSHOT", runner, root=world["root"], sealed_list_path=world["sealed"])
    assert out["citable"] is False
    assert set(bd.DIAG_LABELS) <= set(out["labels"]) and "NON_CITABLE" in out["labels"]
    assert out["result"] == {"n_dev_rows": 6} and seen == [6]
    assert not any(g in json.dumps(out) for g in world["reserved"])
    with pytest.raises(bd.DiagRefused) as exc:
        bd.assert_citable(out)
    assert "NON_CITABLE" in _codes(exc)


def test_synthetic_world_refuses_other_snapshot_and_tampered_seal(world):
    with pytest.raises(bd.DiagRefused) as exc:
        bd.run_bootstrap_diag("ES-1.1", lambda c: None, root=world["root"], sealed_list_path=world["sealed"])
    assert _codes(exc) == {"SNAPSHOT_NOT_FROZEN"}
    world["sealed"].write_bytes(world["sealed"].read_bytes() + b"\n")
    with pytest.raises(bd.DiagRefused) as exc:
        bd.run_bootstrap_diag("SYN-15A-SNAPSHOT", lambda c: None, root=world["root"], sealed_list_path=world["sealed"])
    assert "SEAL_VERIFY_FAILED" in _codes(exc)


def test_synthetic_world_requires_sealed_list(world):
    with pytest.raises(bd.DiagRefused) as exc:
        bd.run_bootstrap_diag("SYN-15A-SNAPSHOT", lambda c: None, root=world["root"])
    assert "SEALED_LIST_MISSING" in _codes(exc)


def test_runner_cannot_relabel_output_as_citable(world):
    out = bd.run_bootstrap_diag("SYN-15A-SNAPSHOT", lambda c: {"citable": True, "labels": []},
                                root=world["root"], sealed_list_path=world["sealed"])
    assert out["citable"] is False and "NON_CITABLE" in out["labels"]


def test_headline_cannot_be_requested_from_the_diag_context(world):
    def runner(ctx):
        ctx.require_mode("HEADLINE")

    with pytest.raises(Exception) as exc:
        bd.run_bootstrap_diag("SYN-15A-SNAPSHOT", runner, root=world["root"], sealed_list_path=world["sealed"])
    assert "HEADLINE_REQUIRES_15B" in str(exc.value)
