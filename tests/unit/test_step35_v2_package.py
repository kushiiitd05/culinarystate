"""Step 35.0 v2 package and the explicit-baseline runner entry (G35-PRE).

Real-repository checks only prove refusal and byte binding; every signed record in
these tests is synthetic and lives in tmp_path. Nothing here evaluates anything.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

from culinarystate.representation import explicit_runner as er
from culinarystate.representation.prereg_guard import PreregNotSigned, require_signed_prereg

REPO = Path(__file__).resolve().parents[2]
V1 = REPO / "reports/step35/preregistration_35_0_v1_draft.md"
V1_SHA = "47c6ba6e6c567a3861c72625de28b78e0fa67c8a1462396fb1e18b421a03d933"
V2 = REPO / er.PACKAGE_DOCUMENT
UNSIGNED = REPO / er.UNSIGNED_RECORD
SHEET = REPO / "reports/step35/35_0_v2_signature_sheet.md"
ROWS = REPO / "reports/step35/35_0_v2_threshold_rows.csv"
OPEN_IDS = ("P-1", "P-2", "P-3", "P-4", "P-5")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _rel_to_root(record_path: str) -> str:
    return (V2.parent / record_path).resolve().relative_to(REPO.resolve()).as_posix()


# ---------------------------------------------------------------- runner definition

def test_tasks_and_required_inputs():
    assert er.TASKS == ("35a", "35b", "35c", "35d", "35e")
    for task in er.TASKS:
        req = er.required_inputs(task)
        assert set(er.COMMON_INPUTS) <= set(req) and len(req) == len(set(req))
    assert "ledgers/data/MOL.jsonl" in er.required_inputs("35a")
    assert "registry/cuisine/cuisine_lookup_v1_DRAFT.csv" in er.required_inputs("35d")
    assert "src/culinarystate/representation/explicit_runner.py" in er.COMMON_INPUTS
    assert set(er.MAC_ONLY_INPUTS) <= set(er.package_inputs())
    with pytest.raises(ValueError):
        er.required_inputs("35g")


def test_runner_entry_cannot_be_pointed_at_another_document():
    with pytest.raises(TypeError):
        er.run_explicit_baseline("35a", lambda a: a, root=REPO, prereg_path=V1)  # type: ignore[call-arg]


@pytest.mark.parametrize("task", ["35a", "35b", "35c", "35d", "35e"])
def test_real_repository_refuses_every_task_now(task):
    calls = []
    with pytest.raises(PreregNotSigned):
        er.run_explicit_baseline(task, calls.append, root=REPO)
    assert calls == []


# ---------------------------------------------------------------- the real unsigned package

def test_v1_protocol_bytes_unchanged():
    assert _sha(V1) == V1_SHA


def test_unsigned_record_matches_current_bytes_and_is_refused():
    rec = json.loads(UNSIGNED.read_text(encoding="utf-8"))
    assert rec["status"] == "UNSIGNED_TEMPLATE" and rec["signers"] == [] and rec["date"] == ""
    assert rec["document"] == V2.name and rec["sha256"] == _sha(V2)
    bound = {_rel_to_root(b["path"]): b["sha256"] for b in rec["bound_files"]}
    for rel, digest in bound.items():
        assert _sha(REPO / rel) == digest, rel
    # Self-consistency of the committed record, independent of which machine runs the test
    # (the Mac holds MAC_ONLY_INPUTS; the cloud container does not).
    absent = set(rec["not_bound_absent_here"])
    assert not set(bound) & absent
    assert set(bound) | absent == set(er.package_inputs())
    assert absent <= set(er.MAC_ONLY_INPUTS)
    with pytest.raises(PreregNotSigned, match="no valid signer"):
        require_signed_prereg(V2, UNSIGNED, required_files=[REPO / p for p in bound])


def test_unsigned_record_is_reproducible_from_the_builder():
    committed = json.loads(UNSIGNED.read_text(encoding="utf-8"))
    rebuilt = er.build_unsigned_record(REPO)
    if set(rebuilt["not_bound_absent_here"]) == set(committed["not_bound_absent_here"]):
        assert rebuilt == committed
        return
    # Machine with the Mac-only recipe files present (Route B): the rebuilt record keeps every
    # committed hash unchanged and additionally binds only Mac-only inputs.
    cb = {_rel_to_root(b["path"]): b["sha256"] for b in committed["bound_files"]}
    rb = {_rel_to_root(b["path"]): b["sha256"] for b in rebuilt["bound_files"]}
    assert {k: rb.get(k) for k in cb} == cb
    assert set(rb) - set(cb) <= set(er.MAC_ONLY_INPUTS)
    assert set(rebuilt["not_bound_absent_here"]) <= set(committed["not_bound_absent_here"])
    same = {k: v for k, v in committed.items() if k not in {"bound_files", "not_bound_absent_here"}}
    assert {k: rebuilt[k] for k in same} == same


def test_signed_record_absent():
    assert not (REPO / er.SIGNED_RECORD).exists()


def test_threshold_rows_are_byte_identical_to_v1_appendix_a():
    text = V1.read_text(encoding="utf-8")
    block = text.split("## Appendix A.", 1)[1].split("```csv\n", 1)[1].split("\n```", 1)[0] + "\n"
    assert ROWS.read_text(encoding="utf-8") == block
    ids = [line.split(",", 1)[0] for line in block.splitlines()[1:]]
    assert ids == [f"THR-35P-{i:02d}" for i in range(1, 44)]


def test_v2_document_binds_inputs_it_lists():
    text = V2.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 800
    listed = dict(re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|", text, re.M))
    rec = json.loads(UNSIGNED.read_text(encoding="utf-8"))
    assert listed == {_rel_to_root(b["path"]): b["sha256"] for b in rec["bound_files"]}
    assert V1_SHA in text


def test_v2_document_quotes_recorded_answers_and_keeps_amendments_open():
    text = V2.read_text(encoding="utf-8")
    parv = "D2 Approved D3 yes D4 yes d5 Go. Dont wait, but record the decision D6 Yes to both rules D7 yes to all D8 Yes"
    assert parv in text
    for d in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"):
        assert re.search(rf"^\| {d} \|", text, re.M), d
    for ruling in ("Tex Mex, Cajun, Pennsylvania Dutch and Native American -> REGION/Americas",
                   "Cantonese, Szechuan and Hunan -> REGION/Asia",
                   "Creole, Hawaiian and Jewish -> REGION/MIXED",
                   "American -> CUISINE/American/Americas",
                   "Georgian, Southern, Roman and Oriental -> UNKNOWN for cuisine, continent and level"):
        assert ruling in text, ruling
    appendix = text.split("## Appendix P", 1)[1]
    assert "NOT ADOPTED" in appendix
    for pid in OPEN_IDS:
        assert re.search(rf"^### {pid} .*OPEN", appendix, re.M), pid
    assert "## Appendix P" not in text.split("## Appendix P", 1)[0]


def test_signature_sheet_lists_hashes_and_open_questions():
    text = SHEET.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 120
    assert _sha(V2) in text and _sha(UNSIGNED) in text and V1_SHA in text
    for pid in OPEN_IDS:
        assert pid in text
    assert "Kush" in text and "Parv" in text


# ---------------------------------------------------------------- synthetic signed package

def _synthetic_root(tmp_path: Path) -> Path:
    root = tmp_path / "pkg"
    for rel in set(er.package_inputs()) | {er.PACKAGE_DOCUMENT}:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"synthetic bytes for {rel}\n", encoding="utf-8")
    return root


def _sign(root: Path, rec: dict, signers=("Kush Tokas (synthetic)", "Parv Goyal (synthetic)")) -> Path:
    rec = dict(rec, signers=list(signers), date="2026-11-03", status="SIGNED")
    out = root / er.SIGNED_RECORD
    out.write_text(json.dumps(rec), encoding="utf-8")
    return out


def test_synthetic_unsigned_copy_is_refused(tmp_path):
    root = _synthetic_root(tmp_path)
    rec = er.build_unsigned_record(root)
    assert rec["not_bound_absent_here"] == []
    (root / er.SIGNED_RECORD).write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(PreregNotSigned, match="no valid signer"):
        er.authorise_explicit_run("35a", root=root)


def test_synthetic_signed_package_authorises_and_runs_once(tmp_path):
    root = _synthetic_root(tmp_path)
    _sign(root, er.build_unsigned_record(root))
    calls = []
    out = er.run_explicit_baseline("35d", lambda auth: calls.append(auth) or "done", root=root)
    assert out == "done" and len(calls) == 1
    auth = calls[0]
    assert auth.task == "35d" and auth.prereg_sha256 == _sha(root / er.PACKAGE_DOCUMENT)
    assert set(auth.required_files) == set(er.required_inputs("35d"))


def test_synthetic_tampered_input_is_refused(tmp_path):
    root = _synthetic_root(tmp_path)
    _sign(root, er.build_unsigned_record(root))
    (root / "registry/cuisine/cuisine_lookup_v1_DRAFT.csv").write_text("edited\n", encoding="utf-8")
    with pytest.raises(PreregNotSigned, match="sha256 differs"):
        er.authorise_explicit_run("35d", root=root)


def test_synthetic_record_missing_a_required_input_is_refused(tmp_path):
    root = _synthetic_root(tmp_path)
    (root / "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet").unlink()
    rec = er.build_unsigned_record(root)
    assert rec["not_bound_absent_here"] == ["ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet"]
    _sign(root, rec)
    assert er.authorise_explicit_run("35a", root=root).task == "35a"
    for task in ("35b", "35c", "35d"):
        with pytest.raises(PreregNotSigned, match="required bound file absent"):
            er.authorise_explicit_run(task, root=root)


def test_synthetic_single_signer_and_edited_document_are_refused(tmp_path):
    root = _synthetic_root(tmp_path)
    _sign(root, er.build_unsigned_record(root), signers=("Kush Tokas (synthetic)",))
    with pytest.raises(PreregNotSigned, match="distinct signers"):
        er.authorise_explicit_run("35e", root=root)
    _sign(root, er.build_unsigned_record(root))
    with (root / er.PACKAGE_DOCUMENT).open("a", encoding="utf-8") as fh:
        fh.write("one more line\n")
    with pytest.raises(PreregNotSigned, match="document sha256 differs"):
        er.authorise_explicit_run("35e", root=root)


def test_synthetic_record_for_another_document_is_refused(tmp_path):
    root = _synthetic_root(tmp_path)
    rec = er.build_unsigned_record(root)
    other = root / "reports/step35/preregistration_35_0_v1_draft.md"
    rec["sha256"] = _sha(other)
    _sign(root, rec)
    with pytest.raises(PreregNotSigned, match="document sha256 differs"):
        er.authorise_explicit_run("35a", root=root)


def test_unsigned_record_copied_from_repo_is_refused(tmp_path):
    root = tmp_path / "copy"
    (root / "reports/step35").mkdir(parents=True)
    shutil.copy(UNSIGNED, root / er.SIGNED_RECORD)
    shutil.copy(V2, root / er.PACKAGE_DOCUMENT)
    with pytest.raises(PreregNotSigned):
        er.authorise_explicit_run("35a", root=root)
