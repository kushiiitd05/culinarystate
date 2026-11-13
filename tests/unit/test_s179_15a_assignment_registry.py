"""T9-C09-R1: counts-only 15a.R reserved/dev assignment registry (no group ids, no seed)."""
from __future__ import annotations

import pytest

from culinarystate.lineage import assignment_registry as AR
from culinarystate.lineage.reserved_seal import GroupInfo


def _g(gid: str, stratum: str, n: int, matrix: str = "m", process: str = "p", ig: str = "IG") -> GroupInfo:
    return GroupInfo(gid, "CELL", f"{ig}-{stratum}", matrix, process, stratum, n)


GROUPS = {
    "RG-1": _g("RG-1", "A", 3, matrix="spinach"),
    "RG-2": _g("RG-2", "A", 2, matrix="kale"),
    "RG-3": _g("RG-3", "B", 4, matrix="spinach"),
    "RG-4": _g("RG-4", "B", 1, matrix="pea"),
}


def test_partition_counts_and_zero_crossing():
    s = AR.partition_summary(GROUPS, reserved=["RG-1", "RG-4"])
    assert s["n_groups"] == 4 and s["n_reserved_groups"] == 2 and s["n_dev_groups"] == 2
    assert s["n_reserved_rows"] == 4 and s["n_dev_rows"] == 6
    assert s["groups_in_both"] == 0 and s["groups_in_neither"] == 0
    assert s["strata"]["A"] == {"n_groups": 2, "n_reserved": 1, "n_reserved_rows": 3, "n_dev_rows": 2}
    assert s["strata"]["B"] == {"n_groups": 2, "n_reserved": 1, "n_reserved_rows": 1, "n_dev_rows": 4}


def test_cross_source_matrix_process_overlap_is_disclosed_not_hidden():
    s = AR.partition_summary(GROUPS, reserved=["RG-1", "RG-4"])
    # spinach/p is reserved via RG-1 (stratum A) and dev via RG-3 (stratum B)
    assert s["matrix_process_keys_in_both_splits"] == 1


def test_unknown_reserved_id_is_refused():
    with pytest.raises(ValueError, match="not in the group universe"):
        AR.partition_summary(GROUPS, reserved=["RG-9"])


def test_duplicate_reserved_id_is_refused():
    with pytest.raises(ValueError, match="duplicate"):
        AR.partition_summary(GROUPS, reserved=["RG-1", "RG-1"])


def test_summary_carries_no_group_ids_or_seed():
    s = AR.partition_summary(GROUPS, reserved=["RG-1"])
    flat = repr(s)
    assert "RG-" not in flat
    assert s["contains_group_ids"] is False and s["contains_seed"] is False


def test_registry_rows_match_split_registry_columns():
    s = AR.partition_summary(GROUPS, reserved=["RG-1", "RG-4"])
    rows = AR.registry_rows(s, commitment={"seed_sha256": "ab" * 32, "rule_id": "R", "group_key_rule": "G",
                                           "reserved_list_sha256": "cd" * 32, "universe_sha256": "ef" * 32,
                                           "snapshot": {"evd_sha256": "12" * 32}},
                            source_artifact="reports/step15/x.json", source_sha256="34" * 32,
                            code_artifact="tools/t.py", code_sha256="56" * 32)
    assert [r["registry_id"] for r in rows] == ["SPL-15A-RESERVED", "SPL-15A-DEV"]
    assert set(rows[0]) == set(AR.REGISTRY_FIELDS)
    assert rows[0]["n_units"] == 2 and rows[1]["n_units"] == 2
    assert rows[0]["seed"] == "sha256:" + "ab" * 32
    assert "groups_in_both=0" in rows[0]["checks"]
