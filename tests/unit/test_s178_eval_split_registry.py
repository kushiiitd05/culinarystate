"""S178 / T9-C09-R1: split registry helpers (hashes, schema, write-once, verification of an edited file)."""
from __future__ import annotations

import csv

import pytest

from culinarystate.evaluation import split_registry as SR


def row(rid="SPL-X", **kw):
    base = dict(registry_id=rid, evaluation="D5_BENCHMARK", block_or_split="S1", split_unit="RECIPE", n_units=3,
                ids_sha256=SR.ids_sha256(["a", "b", "c"]), seed="s", seed_rule="rule", source_artifact="f.csv",
                status="DRAFT_UNFROZEN")
    base.update(kw)
    return SR.make_row(**base)


def test_hash_conventions_are_order_free_and_match_the_07ar_manifest_rule():
    assert SR.ids_sha256(["b", "a"]) == SR.ids_sha256(["a", "b"])
    import hashlib
    assert SR.ids_sha256(["COND-2", "COND-1"]) == hashlib.sha256(b"COND-1\nCOND-2").hexdigest()
    assert SR.assignment_sha256([("a", "train"), ("b", "test")]) == SR.assignment_sha256([("b", "test"), ("a", "train")])
    assert SR.assignment_sha256([("a", "train")]) != SR.assignment_sha256([("a", "test")])        # role is part of the hash


def test_make_row_validates():
    r = row()
    assert list(r) == SR.COLUMNS and r["n_units"] == "3" and r["roles"] == ""
    with pytest.raises(ValueError):
        row(status="FROZEN")
    with pytest.raises(ValueError):
        row(evaluation="D4")
    with pytest.raises(ValueError):
        SR.make_row(registry_id="x", nonsense=1)
    with pytest.raises(ValueError):
        row(ids_sha256="")


def test_disjoint_report():
    assert SR.disjoint_report({"S1": ["r1", "r2"], "S2": ["r3"]}) == {}
    assert SR.disjoint_report({"S1": ["r1", "r2"], "S2": ["r2"], "P": ["r2"]}) == {"P&S1": 1, "P&S2": 1, "S1&S2": 1}


def test_write_once_and_verify_roundtrip(tmp_path):
    # S178 FIX-EVAL (SCI-B E5): one hash convention per row; the assignment hash belongs to a DIAG29-style row
    rows = [row("SPL-A"), row("SPL-B", evaluation="DIAG29", n_units=2, ids_sha256=SR.assignment_sha256([("u1", "train"), ("u2", "test")]))]
    units = [{"registry_id": "SPL-A", "unit_id": u, "role": "benchmark", "attributes": ""} for u in "abc"] + \
            [{"registry_id": "SPL-B", "unit_id": "u1", "role": "train", "attributes": ""},
             {"registry_id": "SPL-B", "unit_id": "u2", "role": "test", "attributes": ""}]
    rp, up = tmp_path / "r.csv", tmp_path / "u.csv"
    hashes = SR.write_registry(rows, units, rp, up)
    assert hashes["registry_sha256"] == SR.sha256_file(rp) and SR.verify_registry(rp, up) == []
    with pytest.raises(FileExistsError):
        SR.write_registry(rows, units, rp, up)
    with pytest.raises(ValueError):
        SR.write_registry([row("SPL-A"), row("SPL-A")], [], tmp_path / "r2.csv", tmp_path / "u2.csv")


def test_verify_detects_edits(tmp_path):
    rows = [row("SPL-A")]
    units = [{"registry_id": "SPL-A", "unit_id": u, "role": "benchmark", "attributes": ""} for u in "abc"]
    rp, up = tmp_path / "r.csv", tmp_path / "u.csv"
    SR.write_registry(rows, units, rp, up)
    edited = list(csv.DictReader(open(up, newline="")))
    edited[0]["unit_id"] = "z"                                             # a unit swapped after registration
    with open(up, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=SR.UNIT_COLUMNS)
        w.writeheader()
        w.writerows(edited)
    assert SR.verify_registry(rp, up) == ["IDS_SHA256_MISMATCH: SPL-A"]
    with open(up, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=SR.UNIT_COLUMNS)
        w.writeheader()
        w.writerows(edited[:2])
    assert any(f.startswith("N_UNITS_MISMATCH") for f in SR.verify_registry(rp, up))
