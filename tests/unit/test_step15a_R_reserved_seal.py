"""15a.R RESERVED-group seal: synthetic groups only; the real seal is never run here.

The only real-repository checks are refusals: no signed 15.0 decision exists in
DECISIONS.md, so the tool must refuse before reading any EVD row.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.lineage import reserved_seal as rs

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "step15a_R_seal.py"
SEED = "synthetic-seed-for-tests-only"
SEED_SHA = hashlib.sha256(SEED.encode("utf-8")).hexdigest()


def _row(i: int, fam: str, ig: str, matrix: str, steps: list[str], *, version: int = 1,
         status: str = "ACTIVE", study: bool = False) -> dict:
    return {"id": f"EVD-{i:06d}", "version": version, "status": status, "source_family_id": fam,
            "independence_group": ig, "matrix": {"raw_name": matrix},
            "process": {"steps": steps, "modifiers": {}},
            "study_ids": [f"STUDY-{ig}"] if study else [],
            "study_id_status": "PRESENT" if study else "NOT_IDENTIFIABLE"}


def _synthetic_rows() -> list[dict]:
    rows, i = [], 0
    for m in range(12):  # database family A: one independence group, 12 x 2 cells
        for p in ("boil", "bake"):
            i += 1
            rows.append(_row(i, "SYN-DB-A", "SYN-DB-A", f"MATRIX{m}", [p]))
    for pub in range(8):  # literature family B: 8 publications, 3 cells each
        for m in range(3):
            i += 1
            rows.append(_row(i, "SYN-LIT-B", f"SYN-PUB-{pub}", f"FOOD{m}", ["fry"], study=True))
    return rows


def _decision(did: str = "D-901", *, heading: str = "15.0 pre-freeze rulings (synthetic)",
              fraction: str = "1/4", unit: str = "STUDY_THEN_CELL", stratify: str = "SOURCE_FAMILY",
              seed_sha: str = SEED_SHA, approver: str = "Kush (synthetic test entry)", extra: str = "") -> str:
    return (f"# DECISIONS\n\n### D-900 · 2026-01-01 · unrelated\n- **Approver:** Kush.\n\n"
            f"### {did} · 2026-01-02 · {heading}\n"
            f"- **15.0 RESERVED_FRACTION:** {fraction}\n- **15.0 RESERVED_UNIT:** {unit}\n"
            f"- **15.0 RESERVED_STRATIFY:** {stratify}\n- **15a.R SEED_SHA256:** {seed_sha}\n"
            f"{extra}- **Approver:** {approver}\n\n### D-902 · 2026-01-03 · later\n- **Approver:** Parv.\n")


@pytest.fixture
def world(tmp_path):
    root = tmp_path / "repo"
    (root / "ledgers/data").mkdir(parents=True)
    (root / "exports/evd").mkdir(parents=True)
    rows = _synthetic_rows()
    rows.append(_row(9999, "SYN-DB-A", "SYN-DB-A", "MATRIX0", ["boil"], status="DEPRECATED"))
    evd = root / "ledgers/data/EVD.jsonl"
    evd.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    digest = hashlib.sha256(evd.read_bytes()).hexdigest()
    (root / "exports/evd/evd_export_v1.manifest.json").write_text(
        json.dumps({"ledger_sha256": digest, "active_rows": len(rows) - 1}), encoding="utf-8")
    (root / "DECISIONS.md").write_text(_decision(), encoding="utf-8")
    private = tmp_path / "private"
    private.mkdir()
    (private / "seed.txt").write_text(SEED + "\n", encoding="utf-8")
    return {"root": root, "private": private, "evd_sha": digest}


def _seal(world, **over):
    kw = dict(root=world["root"], decision_id="D-901", seed_file=world["private"] / "seed.txt",
              sealed_out=world["private"] / "reserved.jsonl",
              commitment_out=world["root"] / "reports/step15/commit.json", execute=True)
    kw.update(over)
    return rs.run_seal(**kw)


def _codes(exc: pytest.ExceptionInfo) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


# ---------------------------------------------------------------- pure parts

@pytest.mark.parametrize("text,value", [("1/4", Fraction(1, 4)), ("0.25", Fraction(1, 4)), (" 3/10 ", Fraction(3, 10))])
def test_parse_fraction_exact(text, value):
    assert rs.parse_fraction(text) == value


@pytest.mark.parametrize("text", ["0", "1", "1/1", "-0.1", "1.5", "", "abc", "<fraction>", "nan", "inf"])
def test_parse_fraction_rejects(text):
    with pytest.raises(ValueError):
        rs.parse_fraction(text)


def test_latest_active_keeps_last_version_and_drops_inactive():
    rows = [_row(1, "F", "F", "a", ["x"]), _row(1, "F", "F", "b", ["x"], version=2),
            _row(2, "F", "F", "c", ["x"]), _row(2, "F", "F", "c", ["x"], version=2, status="DEPRECATED")]
    out = rs.latest_active(rows)
    assert [r["matrix"]["raw_name"] for r in out] == ["b"]


def test_cell_unit_splits_publication_but_study_unit_keeps_it_whole():
    rows = rs.latest_active(_synthetic_rows())
    cell = rs.build_groups(rows, "CELL")
    study = rs.build_groups(rows, "STUDY_THEN_CELL")
    assert len(cell) == 24 + 24 and len(study) == 24 + 8
    assert sum(g.n_rows for g in study.values()) == len(rows)
    pubs = [g for g in study.values() if g.kind == "STUDY"]
    assert all(g.n_rows == 3 and g.stratum == "SYN-LIT-B" for g in pubs)


def test_matrix_key_is_casefolded_raw_name_and_process_signature():
    a = _row(1, "F", "F", "Onion", ["boil"])
    b = _row(2, "F", "F", "onion", ["boil"])
    c = _row(3, "F", "F", "onion", ["boil", "fry"])
    groups = rs.build_groups([a, b, c], "CELL")
    assert sorted(g.n_rows for g in groups.values()) == [1, 2]


def test_group_spanning_two_strata_is_refused():
    rows = [_row(1, "FAM1", "SHARED", "a", ["x"], study=True), _row(2, "FAM2", "SHARED", "b", ["y"], study=True)]
    with pytest.raises(ValueError, match="stratum"):
        rs.build_groups(rows, "STUDY_THEN_CELL")


def test_unknown_unit_or_stratify_refused():
    rows = rs.latest_active(_synthetic_rows())
    with pytest.raises(ValueError):
        rs.build_groups(rows, "ROW")
    groups = rs.build_groups(rows, "CELL")
    with pytest.raises(ValueError):
        rs.select_reserved(groups, snapshot_sha256="0" * 64, seed=SEED, fraction=Fraction(1, 4), stratify="LAB")


def test_selection_is_deterministic_and_floor_per_stratum():
    groups = rs.build_groups(rs.latest_active(_synthetic_rows()), "STUDY_THEN_CELL")
    kw = dict(snapshot_sha256="a" * 64, seed=SEED, fraction=Fraction(1, 4), stratify="SOURCE_FAMILY")
    first = rs.select_reserved(groups, **kw)
    assert first == rs.select_reserved(dict(reversed(list(groups.items()))), **kw)
    by = {}
    for gid in first:
        by[groups[gid].stratum] = by.get(groups[gid].stratum, 0) + 1
    assert by == {"SYN-DB-A": 6, "SYN-LIT-B": 2}  # floor(24/4), floor(8/4)
    assert first == sorted(first)


def test_selection_depends_on_seed_and_snapshot():
    groups = rs.build_groups(rs.latest_active(_synthetic_rows()), "CELL")
    base = dict(snapshot_sha256="a" * 64, seed=SEED, fraction=Fraction(1, 2), stratify="NONE")
    one = rs.select_reserved(groups, **base)
    assert len(one) == 24
    assert one != rs.select_reserved(groups, **{**base, "seed": SEED + "x"})
    assert one != rs.select_reserved(groups, **{**base, "snapshot_sha256": "b" * 64})


def test_small_stratum_reserves_none_under_floor():
    rows = [_row(1, "TINY", "TINY", "a", ["x"]), _row(2, "TINY", "TINY", "b", ["x"])]
    groups = rs.build_groups(rows, "CELL")
    assert rs.select_reserved(groups, snapshot_sha256="c" * 64, seed=SEED, fraction=Fraction(1, 4),
                              stratify="SOURCE_FAMILY") == []


# ---------------------------------------------------------------- decision parsing

def test_find_ruling_reads_markers():
    r = rs.find_ruling(_decision(), "D-901")
    assert (r.decision_id, r.fraction, r.unit, r.stratify, r.seed_sha256) == (
        "D-901", Fraction(1, 4), "STUDY_THEN_CELL", "SOURCE_FAMILY", SEED_SHA)


def test_find_ruling_unknown_id():
    with pytest.raises(rs.SealRefused) as exc:
        rs.find_ruling(_decision(), "D-903")
    assert _codes(exc) == {"DECISION_NOT_FOUND"}


@pytest.mark.parametrize("over,code", [
    ({"heading": "pre-freeze rulings without the step number"}, "DECISION_NOT_15_0"),
    ({"heading": "15.0 rulings DRAFT"}, "DECISION_NOT_SIGNED"),
    ({"heading": "15.0 rulings (UNSIGNED)"}, "DECISION_NOT_SIGNED"),
    ({"approver": "Parv"}, "APPROVER_NOT_KUSH"),
    ({"fraction": "<fraction in (0,1)>"}, "FRACTION_INVALID"),
    ({"fraction": "1"}, "FRACTION_INVALID"),
    ({"unit": "ROW"}, "UNIT_INVALID"),
    ({"stratify": "<SOURCE_FAMILY | NONE>"}, "STRATIFY_INVALID"),
    ({"seed_sha": "abc"}, "SEED_COMMITMENT_INVALID"),
    ({"extra": "- **15.0 RESERVED_FRACTION:** 1/3\n"}, "FRACTION_DUPLICATE"),
])
def test_find_ruling_refusals(over, code):
    with pytest.raises(rs.SealRefused) as exc:
        rs.find_ruling(_decision(**over), "D-901")
    assert code in _codes(exc)


def test_missing_marker_is_named():
    text = _decision().replace("- **15.0 RESERVED_UNIT:** STUDY_THEN_CELL\n", "")
    with pytest.raises(rs.SealRefused) as exc:
        rs.find_ruling(text, "D-901")
    assert "UNIT_MISSING" in _codes(exc)


def test_markers_of_a_later_entry_are_not_borrowed():
    text = _decision(did="D-901").replace("### D-902 · 2026-01-03 · later", "### D-904 · 2026-01-03 · 15.0 other")
    no_markers = "### D-905 · 2026-01-04 · 15.0 empty\n- **Approver:** Kush\n\n" + text
    with pytest.raises(rs.SealRefused) as exc:
        rs.find_ruling(no_markers, "D-905")
    assert "FRACTION_MISSING" in _codes(exc)


# ---------------------------------------------------------------- end-to-end on a synthetic root

def test_synthetic_seal_writes_commitment_and_sealed_list(world):
    out = _seal(world)
    sealed = (world["private"] / "reserved.jsonl").read_bytes()
    commit_text = (world["root"] / "reports/step15/commit.json").read_text(encoding="utf-8")
    commit = json.loads(commit_text)
    assert commit == out
    assert commit["reserved_list_sha256"] == hashlib.sha256(sealed).hexdigest()
    assert commit["snapshot"]["evd_sha256"] == world["evd_sha"]
    assert (commit["fraction"], commit["unit"], commit["stratify"]) == ("1/4", "STUDY_THEN_CELL", "SOURCE_FAMILY")
    assert commit["n_groups"] == 32 and commit["n_reserved"] == 8
    assert SEED not in commit_text and "RG-" not in commit_text and "MATRIX" not in commit_text
    assert rs.verify_sealed_list(sealed, commit) is True
    assert rs.verify_sealed_list(sealed + b"\n", commit) is False
    payload = {k: v for k, v in commit.items() if k not in rs.NON_PAYLOAD_KEYS}
    assert commit["payload_sha256"] == rs.canonical_sha256(payload)


def test_synthetic_seal_is_reproducible(world, tmp_path):
    first = _seal(world)
    again = _seal(world, sealed_out=tmp_path / "private" / "again.jsonl",
                  commitment_out=world["root"] / "reports/step15/commit2.json")
    assert (world["private"] / "reserved.jsonl").read_bytes() == (tmp_path / "private" / "again.jsonl").read_bytes()
    assert first["payload_sha256"] == again["payload_sha256"]


def test_refuses_without_execute_and_writes_nothing(world):
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world, execute=False)
    assert _codes(exc) == {"EXECUTE_FLAG_MISSING"}
    assert not (world["private"] / "reserved.jsonl").exists()
    assert not (world["root"] / "reports/step15/commit.json").exists()


def test_refuses_without_decision_and_lists_every_blocker(world):
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world, decision_id=None, execute=False, seed_file=None, sealed_out=None)
    assert {"EXECUTE_FLAG_MISSING", "NO_15_0_DECISION_ID", "SEED_FILE_MISSING", "SEALED_OUT_MISSING"} <= _codes(exc)


def test_refuses_seed_mismatch(world):
    (world["private"] / "seed.txt").write_text("another seed\n", encoding="utf-8")
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world)
    assert "SEED_COMMITMENT_MISMATCH" in _codes(exc)


def test_refuses_sealed_out_inside_repository(world):
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world, sealed_out=world["root"] / "reports/step15/reserved.jsonl")
    assert "SEALED_OUT_TRACKABLE" in _codes(exc)


def test_refuses_sealed_out_inside_git_tracked_path(world):
    root = world["root"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text("private_ignored/\n", encoding="utf-8")
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world, sealed_out=root / "reports/reserved.jsonl")
    assert "SEALED_OUT_TRACKABLE" in _codes(exc)
    out = _seal(world, sealed_out=root / "private_ignored/reserved.jsonl")
    assert out["n_reserved"] == 8


def test_refuses_existing_outputs(world):
    (world["private"] / "reserved.jsonl").write_text("x", encoding="utf-8")
    (world["root"] / "reports/step15").mkdir(parents=True)
    (world["root"] / "reports/step15/commit.json").write_text("{}", encoding="utf-8")
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world)
    assert {"SEALED_OUT_EXISTS", "COMMITMENT_EXISTS"} <= _codes(exc)


def test_refuses_protected_commitment_path(world):
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world, commitment_out=world["root"] / "ledgers/data/commit.json")
    assert "COMMITMENT_PROTECTED" in _codes(exc)


def test_refuses_snapshot_hash_mismatch(world):
    with (world["root"] / "ledgers/data/EVD.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(_row(5000, "SYN-DB-A", "SYN-DB-A", "NEW", ["boil"])) + "\n")
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world)
    assert "SNAPSHOT_HASH_MISMATCH" in _codes(exc)


def test_refuses_snapshot_rowcount_mismatch(world):
    man = world["root"] / "exports/evd/evd_export_v1.manifest.json"
    rec = json.loads(man.read_text(encoding="utf-8"))
    rec["active_rows"] += 1
    man.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(rs.SealRefused) as exc:
        _seal(world)
    assert "SNAPSHOT_ROWCOUNT_MISMATCH" in _codes(exc)
    assert not (world["private"] / "reserved.jsonl").exists()


# ---------------------------------------------------------------- the real repository: refusal only

def test_real_decisions_contain_no_15_0_ruling():
    text = (REPO / "DECISIONS.md").read_text(encoding="utf-8")
    assert rs.find_15_0_rulings(text) == []


def test_real_repository_refuses_before_reading_rows(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("EVD rows must not be read when the seal is refused")
    monkeypatch.setattr(rs, "read_jsonl", boom)
    with pytest.raises(rs.SealRefused) as exc:
        rs.run_seal(root=REPO, decision_id=None, seed_file=None, sealed_out=tmp_path / "x.jsonl",
                    commitment_out=tmp_path / "c.json", execute=True)
    assert "NO_15_0_DECISION_ID" in _codes(exc)
    assert not (tmp_path / "x.jsonl").exists()


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, cwd=REPO)


def test_cli_check_on_real_repository_refuses():
    res = _cli("check")
    assert res.returncode == 1
    report = json.loads(res.stdout)
    assert report["ready"] is False and any(b.startswith("NO_15_0_DECISION_ID") for b in report["blockers"])


def test_cli_seal_without_execute_refuses(world):
    res = _cli("seal", "--root", str(world["root"]), "--decision", "D-901",
               "--seed-file", str(world["private"] / "seed.txt"),
               "--sealed-out", str(world["private"] / "reserved.jsonl"))
    assert res.returncode == 2
    assert "EXECUTE_FLAG_MISSING" in res.stdout
    assert not (world["private"] / "reserved.jsonl").exists()


def test_cli_seal_with_execute_on_synthetic_root(world):
    res = _cli("seal", "--root", str(world["root"]), "--decision", "D-901",
               "--seed-file", str(world["private"] / "seed.txt"),
               "--sealed-out", str(world["private"] / "reserved.jsonl"),
               "--commitment-out", str(world["root"] / "reports/step15/commit.json"), "--execute")
    assert res.returncode == 0, res.stdout + res.stderr
    assert json.loads(res.stdout)["n_reserved"] == 8
