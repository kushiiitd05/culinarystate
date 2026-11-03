"""DRAFT_PENDING_15aR_15b -- tests for evaluation leakage checks.

Synthetic rows and a synthetic 15a.R-style commitment built with the seal module's own
functions in tmp memory; the real seal is never run and no reserved id is written to git.
"""
from __future__ import annotations

from fractions import Fraction

import pytest

from culinarystate.evaluation import leakage as lk
from culinarystate.evaluation import splits as sp
from culinarystate.lineage import reserved_seal as rs

COLS = ("lineage_group",)


def _evd(i: int, ig: str, matrix: str, step: str) -> dict:
    return {"id": f"EVD-{i:04d}", "status": "ACTIVE", "source_family_id": "SYN-FAM",
            "independence_group": ig, "matrix": {"raw_name": matrix},
            "process": {"steps": [step], "modifiers": {}}, "study_ids": [], "study_id_status": "NOT_IDENTIFIABLE",
            "lineage_group": f"LG-{i:04d}", "near_dup": matrix.lower().strip() + "/" + step}


def _rows() -> list[dict]:
    out, i = [], 0
    for m in range(8):
        for step in ("boil", "bake"):
            i += 1
            out.append(_evd(i, "SYN-IG", f"Matrix{m}", step))
    return out


def _seal(rows: list[dict], reserve: int = 2) -> tuple[dict, bytes, list[str]]:
    groups = rs.build_groups(rows, "CELL")
    reserved = sorted(groups)[:reserve]
    sealed = rs.sealed_list_bytes(reserved, groups)
    ruling = rs.Ruling("D-999", Fraction(1, 8), "CELL", "NONE", "0" * 64)
    commitment = rs.build_commitment(ruling=ruling, groups=groups, reserved=reserved, sealed_bytes=sealed,
                                     snapshot={"evd_sha256": "synthetic"})
    return commitment, sealed, reserved


def _codes(exc) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


def _split(rows, seed="s"):
    return sp.group_aware_split(rows, id_column="id", group_columns=COLS,
                                role_fractions={"train": Fraction(1, 2), "test": Fraction(1, 2)},
                                seed=seed, remainder_role="train")


# ---------------------------------------------------------------- overlap checks

def test_clean_split_has_no_leakage():
    rows = _rows()
    s = _split(rows)
    assert lk.check_leakage(s, rows, id_column="id", group_columns=COLS,
                            near_dup_key=lambda r: [r["near_dup"]]) == []


def test_group_overlap_is_reported_when_rows_change_after_the_split():
    rows = _rows()
    s = _split(rows)
    test_id, train_id = s.rows("test")[0], s.rows("train")[0]
    lg = next(r["lineage_group"] for r in rows if r["id"] == test_id)
    edited = [dict(r, lineage_group=lg) if r["id"] == train_id else r for r in rows]
    blockers = lk.check_leakage(s, edited, id_column="id", group_columns=COLS)
    assert any(b.startswith("GROUP_OVERLAP: lineage_group") for b in blockers)
    assert not any(lg in b for b in blockers)  # values are counted, not echoed
    with pytest.raises(lk.LeakageRefused):
        lk.assert_no_leakage(s, edited, id_column="id", group_columns=COLS)


def test_rows_missing_from_the_split_are_reported():
    rows = _rows()
    s = _split(rows[:-1])
    assert any(b.startswith("ROW_NOT_IN_SPLIT") for b in lk.check_leakage(s, rows, id_column="id", group_columns=COLS))


def test_near_duplicate_key_overlap_is_reported():
    rows = _rows()
    # same near-duplicate key under two different lineage groups: grouping alone misses it
    rows[0] = {**rows[0], "near_dup": "shared-key", "lineage_group": "LG-A"}
    rows[1] = {**rows[1], "near_dup": "shared-key", "lineage_group": "LG-B"}
    for seed in (f"s{i}" for i in range(50)):
        s = _split(rows, seed)
        if s.assignment[rows[0]["id"]] != s.assignment[rows[1]["id"]]:
            break
    else:
        pytest.skip("no seed separated the pair")
    blockers = lk.check_leakage(s, rows, id_column="id", group_columns=COLS, near_dup_key=lambda r: [r["near_dup"]])
    assert any(b.startswith("NEAR_DUPLICATE_OVERLAP") for b in blockers)
    assert not any("shared-key" in b for b in blockers)  # values are counted, not echoed


def test_near_duplicate_keys_can_be_merged_into_groups_before_splitting():
    rows = _rows()
    rows[0] = {**rows[0], "near_dup": "shared-key", "lineage_group": "LG-A"}
    rows[1] = {**rows[1], "near_dup": "shared-key", "lineage_group": "LG-B"}
    s = sp.group_aware_split(rows, id_column="id", group_columns=("lineage_group", "near_dup"),
                             role_fractions={"train": Fraction(1, 2), "test": Fraction(1, 2)},
                             seed="s", remainder_role="train")
    assert s.assignment[rows[0]["id"]] == s.assignment[rows[1]["id"]]


# ---------------------------------------------------------------- reserved-group exclusion

def test_sealed_list_is_verified_against_its_commitment():
    rows = _rows()
    commitment, sealed, reserved = _seal(rows)
    assert lk.load_sealed_reserved(commitment, sealed) == frozenset(reserved)
    with pytest.raises(lk.LeakageRefused) as exc:
        lk.load_sealed_reserved(commitment, sealed + b"{}\n")
    assert "SEAL_COMMITMENT_MISMATCH" in _codes(exc)
    with pytest.raises(lk.LeakageRefused) as exc:
        lk.load_sealed_reserved({**commitment, "n_reserved": 99}, sealed)
    assert "SEAL_COMMITMENT_MISMATCH" in _codes(exc)


def test_seal_group_id_matches_the_seal_module():
    rows = _rows()
    groups = rs.build_groups(rows, "CELL")
    assert {lk.seal_group_id(r, "CELL") for r in rows} == set(groups)


def test_reserved_groups_and_their_components_are_excluded():
    rows = _rows()
    commitment, sealed, reserved = _seal(rows)
    reserved_set = lk.load_sealed_reserved(commitment, sealed)
    seal_of = {r["id"]: lk.seal_group_id(r, commitment["unit"]) for r in rows}
    # link one DEV row to a reserved row through a shared lineage group: the component is burned
    res_row = next(r for r in rows if seal_of[r["id"]] in reserved_set)
    dev_row = next(r for r in rows if seal_of[r["id"]] not in reserved_set)
    rows = [dict(r, lineage_group=res_row["lineage_group"]) if r["id"] == dev_row["id"] else r for r in rows]
    out = lk.exclude_reserved(rows, id_column="id", group_columns=COLS, row_seal_group=seal_of,
                              reserved=reserved_set)
    kept = {r["id"] for r in out.kept_rows}
    assert dev_row["id"] not in kept
    assert not any(seal_of[i] in reserved_set for i in kept)
    assert out.n_burned_components == 1 and out.n_excluded_rows == len(rows) - len(kept)
    assert not any(g in repr(out.report()) for g in reserved_set)


def test_using_a_reserved_row_is_refused():
    rows = _rows()
    commitment, sealed, _ = _seal(rows)
    reserved_set = lk.load_sealed_reserved(commitment, sealed)
    seal_of = {r["id"]: lk.seal_group_id(r, commitment["unit"]) for r in rows}
    with pytest.raises(lk.LeakageRefused) as exc:
        lk.assert_reserved_excluded([r["id"] for r in rows], row_seal_group=seal_of, reserved=reserved_set)
    assert "RESERVED_GROUP_USED" in _codes(exc)
    assert not any(g in str(exc.value) for g in reserved_set)


def test_row_without_seal_group_is_refused():
    with pytest.raises(lk.LeakageRefused) as exc:
        lk.assert_reserved_excluded(["x"], row_seal_group={}, reserved=frozenset({"RG-1"}))
    assert "SEAL_GROUP_UNKNOWN" in _codes(exc)


# ---------------------------------------------------------------- modes

def test_headline_mode_is_refused_while_15b_is_not_frozen(tmp_path):
    with pytest.raises(lk.LeakageRefused) as exc:
        lk.require_mode("HEADLINE", root=tmp_path)
    assert "HEADLINE_REQUIRES_15B" in _codes(exc)
    frozen, reason = lk.freeze_15b_status(tmp_path)
    assert frozen is False and "15b" in reason


def test_headline_mode_is_refused_even_if_a_record_file_appears(tmp_path):
    (tmp_path / "reports/step15").mkdir(parents=True)
    (tmp_path / "reports/step15/15b_freeze_record.SIGNED.json").write_text('{"status": "SIGNED"}')
    with pytest.raises(lk.LeakageRefused):
        lk.require_mode("HEADLINE", root=tmp_path)


def test_diagnostic_mode_is_allowed_and_unknown_mode_refused(tmp_path):
    assert lk.require_mode("DIAGNOSTIC", root=tmp_path) == lk.DIAGNOSTIC_LABELS
    with pytest.raises(lk.LeakageRefused) as exc:
        lk.require_mode("PAPER", root=tmp_path)
    assert "MODE_UNKNOWN" in _codes(exc)
