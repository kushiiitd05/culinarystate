"""08a.7 export v2: additive lineage columns on top of EVD export v1 (strict TDD, synthetic fixtures)."""
import json
from pathlib import Path

import pytest

from culinarystate.evidence.evd_export import canon_json
from culinarystate.lineage.export_v2 import (ADDED_COLUMNS, EXPORT_V2_VERSION, ExportV2Error, build_v2_rows,
                                             check_v1_identical, load_keys, write_export_v2)
from culinarystate.lineage.guard import ProtectedPathError


def _v1(i, **kw):
    r = {"evd_id": f"EVD-{i:06d}", "study_id_status": "UNKNOWN", "study_ids": [], "export_version": "evd_export@1.0.0", "x": i}
    r.update(kw)
    return r


def _key(i, **kw):
    k = {"evd_id": f"EVD-{i:06d}", "study_id": None, "study_id_status": "NOT_IDENTIFIABLE", "independence_resolution": "UNKNOWN",
         "lineage_root_id": f"LROOT-{i:06d}", "split_group_id": f"SPLITGRP-EVD-{i:06d}", "rule_version": "keys-v1",
         "assignment_status": "SCRATCH_PROVISIONAL"}
    k.update(kw)
    return k


def test_v1_columns_preserved_and_new_added():
    rows = build_v2_rows([_v1(1), _v1(2)], {k["evd_id"]: k for k in (_key(1), _key(2, study_id="STUDY-9", study_id_status="PRESENT"))})
    assert [r["evd_id"] for r in rows] == ["EVD-000001", "EVD-000002"]
    for r in rows:
        assert set(ADDED_COLUMNS) <= set(r)
    assert rows[0]["study_id_status"] == "UNKNOWN"  # v1 value untouched
    assert rows[1]["study_id"] == "STUDY-9" and rows[1]["lineage_study_id_status"] == "PRESENT"
    assert rows[0]["split_group_id"] == "SPLITGRP-EVD-000001"


def test_added_columns_never_collide_with_v1():
    assert not set(ADDED_COLUMNS) & set(_v1(1))


def test_input_not_mutated():
    v1 = [_v1(1)]
    before = canon_json(v1[0])
    build_v2_rows(v1, {"EVD-000001": _key(1)})
    assert canon_json(v1[0]) == before


def test_missing_key_fails():
    with pytest.raises(ExportV2Error, match="EVD-000002"):
        build_v2_rows([_v1(1), _v1(2)], {"EVD-000001": _key(1)})


def test_null_key_field_fails():
    with pytest.raises(ExportV2Error):
        build_v2_rows([_v1(1)], {"EVD-000001": _key(1, split_group_id=None)})


def test_extra_keys_fail():
    with pytest.raises(ExportV2Error, match="EVD-000007"):
        build_v2_rows([_v1(1)], {"EVD-000001": _key(1), "EVD-000007": _key(7)})


def test_v1_identity_check_passes_and_detects_change():
    v1 = [_v1(1), _v1(2)]
    v1_lines = [canon_json(r) for r in v1]
    rows = build_v2_rows(v1, {k["evd_id"]: k for k in (_key(1), _key(2))})
    assert check_v1_identical(rows, v1_lines) == 2
    rows[1] = {**rows[1], "x": 99}
    with pytest.raises(ExportV2Error):
        check_v1_identical(rows, v1_lines)
    with pytest.raises(ExportV2Error):
        check_v1_identical(rows[:1], v1_lines)  # row lost


def test_load_keys_duplicate_fails(tmp_path):
    p = tmp_path / "k.jsonl"
    p.write_text(canon_json(_key(1)) + "\n" + canon_json(_key(1)) + "\n")
    with pytest.raises(ExportV2Error):
        load_keys(p)


def test_write_deterministic_manifest_and_guard(tmp_path):
    v1 = [_v1(1), _v1(2)]
    rows = build_v2_rows(v1, {k["evd_id"]: k for k in (_key(1), _key(2))})
    a, b = tmp_path / "a", tmp_path / "b"
    ma = write_export_v2(rows, a, {"note": "t"})
    mb = write_export_v2(rows, b, {"note": "t"})
    assert (a / "evd_export_v2.jsonl").read_bytes() == (b / "evd_export_v2.jsonl").read_bytes()
    assert (a / "evd_export_v2.manifest.json").read_bytes() == (b / "evd_export_v2.manifest.json").read_bytes()
    man = json.loads((a / "evd_export_v2.manifest.json").read_text())
    assert man["export_version"] == EXPORT_V2_VERSION == "evd_export@2.0.0"
    assert man["export_rows"] == 2 and len(man["export_sha256"]) == 64
    assert man["added_columns"] == list(ADDED_COLUMNS) and man["export_sha256"] == ma["export_sha256"] == mb["export_sha256"]
    lines = (a / "evd_export_v2.jsonl").read_text().splitlines()
    assert len(lines) == 2 and json.loads(lines[0])["export_schema_version"] == EXPORT_V2_VERSION


def test_refuses_repo_exports_and_ledgers(tmp_path):
    rows = build_v2_rows([_v1(1)], {"EVD-000001": _key(1)})
    for bad in (tmp_path / "exports" / "evd", tmp_path / "ledgers" / "data" / "x", tmp_path / "exports" / "evd_v2"):
        with pytest.raises(ProtectedPathError):
            write_export_v2(rows, bad, {})
