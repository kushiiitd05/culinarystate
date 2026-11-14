"""tools/d085_delegate.py freeze-d5 (S179, D-085): the record passes the D5 guard and says AI_DELEGATED_D085."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from culinarystate.evaluation import frozen_guard as FG

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("d085", ROOT / "tools/d085_delegate.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
BENCH = ["benchmark/d5/d5_benchmark_v1_D085_S.csv", "benchmark/d5/d5_benchmark_v1_D085_PC.csv",
         "benchmark/d5/d5_benchmark_v1_D085_UX.csv"]


@pytest.fixture
def root(tmp_path):
    for rel in (*BENCH, FG.PREREG, *FG.SCORER_CODE):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, tmp_path / rel)
    return tmp_path


def test_freeze_d5_record_passes_the_guard(root):
    p = T.freeze_d5(root, "D5-BENCH-2026-11-10", BENCH, "2026-11-10")
    rec = json.loads(p.read_text())
    assert rec["record"] == "FREEZE_D5_BENCHMARK" and rec["status"] == "FROZEN"
    assert rec["approvals"] == [{"approved_by": T.AI_DELEGATE, "approved_date": "2026-11-10", "decision": "D-085",
                                 "label": "NO_HUMAN_SIGNOFF_D085"}]
    res = FG.check_real_inputs(root, p, BENCH)
    assert res["ok"], res["problems"]
    assert res["signoff"] == "AI_DELEGATED_D085" and res["label"] == "NO_HUMAN_SIGNOFF_D085"


def test_freeze_d5_refuses_overwrite_and_detects_later_edits(root):
    p = T.freeze_d5(root, "D5-BENCH-2026-11-10", BENCH, "2026-11-10")
    with pytest.raises(SystemExit):
        T.freeze_d5(root, "D5-BENCH-2026-11-10", BENCH, "2026-11-10")
    (root / BENCH[0]).write_text((root / BENCH[0]).read_text() + "\n")
    assert any(x.startswith("HASH_MISMATCH") for x in FG.check_real_inputs(root, p, BENCH)["problems"])
