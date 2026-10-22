"""Agreement tool sanity (synthetic packets only; the tool never invents labels)."""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import step07_agreement as A  # noqa: E402


def test_kappa_basic():
    assert A.kappa(list("aabb"), list("aabb")) == 1.0
    assert abs(A.kappa(list("aabb"), list("abab"))) < 1e-9


def test_input_validation_rejects_blank(tmp_path, monkeypatch):
    src = ROOT / "annotation/condition_audit/condition_audit_packet_100_v3_Kush.csv"
    if not src.exists():
        return
    monkeypatch.setattr(A, "ROOT", tmp_path)
    (tmp_path / "reports/step07").mkdir(parents=True)
    assert A.main(str(src), str(src)) == 2  # blank judgements -> INVALID_INPUT
