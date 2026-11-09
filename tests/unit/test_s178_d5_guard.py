"""S178 H1H3H: frozen-input guard. Every refusal path (missing record, hash mismatch, AI-signed or single-human
approval, unpinned / changed code, changed prereg, fixture paths in a real run) and the one accepting path, on
SYNTHETIC files in a temporary directory. The real benchmark is never touched."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from culinarystate.evaluation import frozen_guard as FG

ROOT = Path(__file__).resolve().parents[2]
CODE = ("src/fake_scorer.py",)
PREREG = "reports/del5/prereg.md"
BENCH = "benchmark/d5/bench_synthetic.csv"
EVD = "ledgers/data/EVD_synthetic.jsonl"
HUMANS = [{"approved_by": "Kush Tokas", "approved_date": "2026-11-16"},
          {"approved_by": "Parv Goyal", "approved_date": "2026-11-16"}]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture
def tree(tmp_path):
    for rel, text in ((BENCH, "qid,block\nSYN-P1-001,P1\n"), (EVD, '{"id": "EVD-990001"}\n'),
                      (CODE[0], "x = 1\n"), (PREREG, "prereg text\n")):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    return tmp_path


def record(root: Path, **over) -> dict:
    rec = {"record": FG.FREEZE_RECORD_TYPE, "freeze_id": "D5-BENCH-SYNTHETIC", "status": "FROZEN",
           "files": {BENCH: sha(root / BENCH), EVD: sha(root / EVD)},
           "code_sha256": {CODE[0]: sha(root / CODE[0])}, "prereg_sha256": sha(root / PREREG), "approvals": HUMANS}
    rec.update(over)
    return rec


def put(root: Path, rec: dict) -> Path:
    p = root / "registry/freezes/D5-BENCH-SYNTHETIC.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec))
    return p


def check(root, fr, inputs=(BENCH, EVD), **kw):
    return FG.check_real_inputs(root, fr, list(inputs), code_paths=CODE, prereg_path=PREREG, **kw)


def test_valid_record_passes(tree):
    res = check(tree, put(tree, record(tree)))
    assert res["ok"], res["problems"]
    assert res["files_sha256"] == {BENCH: sha(tree / BENCH), EVD: sha(tree / EVD)}
    assert res["freeze_id"] == "D5-BENCH-SYNTHETIC"


def test_missing_record_refuses(tree):
    res = check(tree, tree / "registry/freezes/none.json")
    assert not res["ok"] and res["problems"] == ["NO_FREEZE_RECORD"]
    with pytest.raises(FG.GuardRefused) as e:
        FG.require_real_inputs(tree, tree / "registry/freezes/none.json", [BENCH], code_paths=CODE, prereg_path=PREREG)
    assert "NO_FREEZE_RECORD" in e.value.problems


def test_unreadable_and_wrong_type(tree):
    p = tree / "registry/freezes/bad.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{not json")
    assert check(tree, p)["problems"] == ["FREEZE_RECORD_UNREADABLE"]
    res = check(tree, put(tree, record(tree, record="FREEZE_15A_BOOTSTRAP")))
    assert any(x.startswith("WRONG_RECORD_TYPE") for x in res["problems"])


def test_hash_mismatch_refuses(tree):
    fr = put(tree, record(tree))
    (tree / BENCH).write_text("qid,block\nSYN-P1-001,P2\n")          # edited after the freeze
    res = check(tree, fr)
    assert not res["ok"] and f"HASH_MISMATCH: {BENCH}" in res["problems"]


def test_listed_file_missing_and_unlisted_input(tree):
    fr = put(tree, record(tree))
    (tree / EVD).unlink()
    res = check(tree, fr, inputs=(BENCH, "benchmark/d5/other.csv"))
    assert f"FILE_MISSING: {EVD}" in res["problems"]
    assert "FILE_NOT_IN_FREEZE: benchmark/d5/other.csv" in res["problems"]


@pytest.mark.parametrize("who", ["AI_AGENT", "Claude", "claude-opus", "ksh", "prv", "Kush Tokas (via agent)",
                                 "assistant", "GPT-4", "qwen2.5"])
def test_ai_signed_approval_refuses(tree, who):
    rec = record(tree, approvals=[{"approved_by": who, "approved_date": "2026-11-16"}, HUMANS[1]])
    res = check(tree, put(tree, rec))
    assert not res["ok"]
    assert any(x.startswith("AI_APPROVAL") for x in res["problems"]), res["problems"]
    assert "MISSING_APPROVER: Kush Tokas" in res["problems"]


def test_ai_marker_in_other_approval_field_refuses(tree):
    rec = record(tree, approvals=[{**HUMANS[0], "entered_by": "AI_AGENT_S178"}, HUMANS[1]])
    res = check(tree, put(tree, rec))
    assert any(x.startswith("AI_APPROVAL") for x in res["problems"])


def test_non_human_names_and_dates(tree):
    rec = record(tree, approvals=[{"approved_by": "Kush", "approved_date": "2026-11-16"},
                                  {"approved_by": "Parv Goyal", "approved_date": "16 Nov"}])
    res = check(tree, put(tree, rec))
    assert any(x.startswith("APPROVER_NOT_HUMAN") for x in res["problems"])
    assert "APPROVAL_DATE_INVALID: Parv Goyal" in res["problems"]


def test_single_human_refused_by_default_allowed_if_policy_says(tree):
    rec = record(tree, approvals=None, approved_by="Kush Tokas", approved_date="2026-11-16")
    fr = put(tree, rec)
    assert "MISSING_APPROVER: Parv Goyal" in check(tree, fr)["problems"]
    assert check(tree, fr, required_approvers=("Kush Tokas",))["ok"]


def test_not_frozen_and_no_approval(tree):
    res = check(tree, put(tree, record(tree, status="PROPOSED", approvals=[])))
    assert "NOT_FROZEN: status 'PROPOSED'" in res["problems"] and "NO_HUMAN_APPROVAL" in res["problems"]


def test_code_and_prereg_pins(tree):
    fr = put(tree, record(tree, code_sha256={}))
    assert f"CODE_NOT_PINNED: {CODE[0]}" in check(tree, fr)["problems"]
    fr = put(tree, record(tree))
    (tree / CODE[0]).write_text("x = 2\n")                          # scorer edited after the freeze
    (tree / PREREG).write_text("edited prereg\n")
    res = check(tree, fr)
    assert f"CODE_CHANGED_AFTER_FREEZE: {CODE[0]}" in res["problems"] and "PREREG_CHANGED_AFTER_FREEZE" in res["problems"]
    assert "PREREG_NOT_PINNED" in check(tree, put(tree, record(tree, prereg_sha256=None)))["problems"]


def test_commit_check_and_fixture_inputs_in_real_mode(tree):
    fr = put(tree, record(tree))
    assert "FREEZE_RECORD_NOT_COMMITTED" in check(tree, fr, committed_check=lambda p: False)["problems"]
    assert check(tree, fr, committed_check=lambda p: True)["ok"]
    res = check(tree, fr, inputs=(BENCH, f"{FG.FIXTURE_DIR}/benchmark_synthetic.csv"))
    assert f"FIXTURE_INPUT_IN_REAL_MODE: {FG.FIXTURE_DIR}/benchmark_synthetic.csv" in res["problems"]


def test_guard_never_writes(tree):
    before = sorted(p.relative_to(tree).as_posix() for p in tree.rglob("*"))
    check(tree, tree / "registry/freezes/none.json")
    check(tree, put(tree, record(tree, status="PROPOSED")))
    after = sorted(p.relative_to(tree).as_posix() for p in tree.rglob("*"))
    assert set(after) - set(before) == {"registry", "registry/freezes", "registry/freezes/D5-BENCH-SYNTHETIC.json"}
    src = (ROOT / "src/culinarystate/evaluation/frozen_guard.py").read_text()
    tree_ = ast.parse(src)
    calls = {n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "") for n in ast.walk(tree_)
             if isinstance(n, ast.Call)}
    assert not calls & {"write_text", "write_bytes", "mkdir", "dump", "touch", "unlink", "rename", "replace_file"}
    assert "open" not in calls                                    # reads go through read_text / read_bytes only


def test_scorer_code_list_exists_in_repo():
    missing = [p for p in FG.scorer_code_paths() if not (ROOT / p).is_file()]
    assert not missing, missing


# ------------------------------------------------------------------ fixture mode

def fixture_dir(tmp_path, files: dict[str, str], *, synthetic=True, sub="tests/fixtures/syn") -> Path:
    d = tmp_path / sub
    d.mkdir(parents=True, exist_ok=True)
    for k, v in files.items():
        (d / k).write_text(v)
    man = {"stamp": FG.STAMP if synthetic else "X", "synthetic": synthetic,
           "files": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in files.items()}}
    (d / "manifest.json").write_text(json.dumps(man))
    return d


def test_fixture_guard_paths(tmp_path):
    d = fixture_dir(tmp_path, {"a.csv": "qid\n"})
    assert FG.check_fixture_inputs(d, [d / "a.csv"], root=tmp_path)["ok"]
    outside = tmp_path / "b.csv"
    outside.write_text("qid\n")
    res = FG.check_fixture_inputs(d, [outside], root=tmp_path)
    assert any(x.startswith("INPUT_OUTSIDE_FIXTURE_DIR") for x in res["problems"])
    (d / "a.csv").write_text("qid\nchanged\n")
    assert "FIXTURE_HASH_MISMATCH: a.csv" in FG.check_fixture_inputs(d, [d / "a.csv"], root=tmp_path)["problems"]
    (d / "c.csv").write_text("x")
    assert "INPUT_NOT_IN_MANIFEST: c.csv" in FG.check_fixture_inputs(d, [d / "c.csv"], root=tmp_path)["problems"]


def test_fixture_guard_refuses_non_synthetic_manifest_and_benchmark_dirs(tmp_path):
    d = fixture_dir(tmp_path, {"a.csv": "qid\n"}, synthetic=False)
    assert "MANIFEST_NOT_SYNTHETIC" in FG.check_fixture_inputs(d, [d / "a.csv"], root=tmp_path)["problems"]
    d2 = fixture_dir(tmp_path, {"a.csv": "qid\n"}, sub="benchmark/d5")
    res = FG.check_fixture_inputs(d2, [d2 / "a.csv"], root=tmp_path)
    assert any(x.startswith("FIXTURE_DIR_IN_FORBIDDEN_PATH") for x in res["problems"])
    assert FG.check_fixture_inputs(tmp_path / "nowhere", [], root=tmp_path)["problems"] == ["NO_FIXTURE_MANIFEST"]


def test_row_and_evd_checks():
    ok = [{"qid": "SYN-P1-001", "drafted_by": "SYNTHETIC_FIXTURE"}]
    FG.assert_synthetic_rows(ok)
    for bad in ({"qid": "D5-P1-001", "drafted_by": "SYNTHETIC_FIXTURE"}, {"qid": "SYN-P1-001", "drafted_by": "AI_AGENT_S171"}):
        with pytest.raises(FG.GuardRefused):
            FG.assert_synthetic_rows([bad])
    FG.assert_synthetic_evd({"EVD-990001": {}})
    with pytest.raises(FG.GuardRefused):
        FG.assert_synthetic_evd({"EVD-000123": {}})
    FG.assert_real_rows([{"qid": "D5-P1-001", "drafted_by": "AI_AGENT_S171"}])
    with pytest.raises(FG.GuardRefused):
        FG.assert_real_rows(ok)


def test_stamp():
    out = FG.stamp({"a": {"x": 1}, "b": [1]})
    FG.assert_stamped(out)
    assert out["a"]["stamp"] == FG.STAMP and out["stamp"] == FG.STAMP
    with pytest.raises(FG.GuardRefused):
        FG.assert_stamped({"stamp": FG.STAMP, "a": {"x": 1}})


def test_committed_fixture_manifest_is_consistent():
    d = ROOT / FG.FIXTURE_DIR
    man = json.loads((d / "manifest.json").read_text())
    res = FG.check_fixture_inputs(d, [d / f for f in man["files"]])
    assert res["ok"], res["problems"]
