"""S178 FIX-EVAL: SCI-B E5 (split registry verifier). Uses copies of the committed registry in tmp_path; nothing is edited in place.

Failure scenario (review): editing one S1 recipe id to REC-999999 in split_registry_units_v1.csv gives verify_registry -> []; the
verifier accepted either hash convention, never checked unit_ids_sha256, and skipped the 16 DIAG29 rows silently.
"""
from __future__ import annotations

import csv
import shutil

import pytest

from culinarystate.evaluation import split_registry as SR
from tests.unit.test_s178_analysis_helpers import ROOT

REG, UNITS = ROOT / "registry/split_registry_v1.csv", ROOT / "reports/s178/split_registry_units_v1.csv"


@pytest.fixture()
def copies(tmp_path):
    r, u = tmp_path / "r.csv", tmp_path / "u.csv"
    shutil.copy(REG, r)
    shutil.copy(UNITS, u)
    return r, u


def _rewrite(path, fn):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    cols = list(rows[0])
    rows = [fn(dict(x)) for x in rows]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def errors(findings):
    return [f for f in findings if not f.startswith("NOT_VERIFIABLE_FROM_LISTING")]


def test_committed_registry_has_no_errors_and_names_the_unverifiable_rows(copies):
    r, u = copies
    f = SR.verify_registry(r, u)
    assert errors(f) == []
    nv = [x for x in f if x.startswith("NOT_VERIFIABLE_FROM_LISTING")]
    rows = list(csv.DictReader(open(REG, newline="", encoding="utf-8")))
    diag_with_units = [x["registry_id"] for x in rows if x["evaluation"] == "DIAG29" and x["n_units"] != "0"]
    assert len(nv) == len(diag_with_units) == 13 and all(any(d in x for x in nv) for d in diag_with_units)


def test_swapped_recipe_id_in_the_attributes_is_detected(copies):
    r, u = copies
    first = next(x for x in csv.DictReader(open(u, newline="", encoding="utf-8")) if x["registry_id"] == "SPL-D5-S1")
    rid = SR._attrs(first["attributes"])["recipe_id"]                                 # read, not hard-coded (leakage scan)
    _rewrite(u, lambda x: {**x, "attributes": x["attributes"].replace(f"recipe_id={rid};", "recipe_id=REC-999999;")})
    assert "UNIT_IDS_SHA256_MISMATCH: SPL-D5-S1" in SR.verify_registry(r, u)


def test_swapped_cell_in_the_attributes_is_detected(copies):
    r, u = copies
    done = []

    def swap(x):
        if x["registry_id"] == "SPL-D5-P1" and not done:
            done.append(1)
            return {**x, "attributes": x["attributes"].replace("|folate;", "|vitamin C;", 1)}
        return x
    _rewrite(u, swap)
    assert done and "UNIT_IDS_SHA256_MISMATCH: SPL-D5-P1" in SR.verify_registry(r, u)


def test_one_hash_convention_per_row(copies):
    r, u = copies
    units = [x for x in csv.DictReader(open(u, newline="", encoding="utf-8")) if x["registry_id"] == "SPL-D5-S2"]
    wrong = SR.assignment_sha256((x["unit_id"], x["role"]) for x in units)          # the other convention
    _rewrite(r, lambda x: {**x, "ids_sha256": wrong} if x["registry_id"] == "SPL-D5-S2" else x)
    assert "IDS_SHA256_MISMATCH: SPL-D5-S2" in SR.verify_registry(r, u)
    assert SR.hash_convention({"evaluation": "D5_BENCHMARK"}) == "IDS_SORTED_NEWLINE"
    assert SR.hash_convention({"evaluation": "DIAG29"}) == "UNIT_ROLE_ASSIGNMENT"


def test_diag29_rows_verified_from_a_recomputed_assignment(copies):
    r, u = copies
    rows = {x["registry_id"]: x for x in csv.DictReader(open(r, newline="", encoding="utf-8"))}
    rid = "SPL-29D-BOGNAR-2002-S-1-random"
    # a synthetic recomputation that does not match the registered hash must be an error, not a pass
    bad = {rid: [("EVD-000001", "train")]}
    f = SR.verify_registry(r, u, recomputed=bad)
    assert f"IDS_SHA256_MISMATCH: {rid}" in f and f"N_UNITS_MISMATCH: {rid} (1 listed, {rows[rid]['n_units']} registered)" in f
    assert not any(rid in x and x.startswith("NOT_VERIFIABLE") for x in f)


def test_unit_id_rule_per_split_unit():
    assert SR.unit_ids_from_listing({"split_unit": "RECIPE"}, [{"unit_id": "q1", "attributes": "recipe_id=REC-1;family=W"}]) == ["REC-1"]
    assert SR.unit_ids_from_listing({"split_unit": "CELL"}, [{"unit_id": "q1", "attributes": "cell=I|P||vitamin C;stratum=D"}]) == ["I|P||vitamin C"]
    assert SR.unit_ids_from_listing({"split_unit": "CONDITION"}, [{"unit_id": "COND-1", "attributes": ""}]) == ["COND-1"]
    assert SR.unit_ids_from_listing({"split_unit": "RECIPE"}, [{"unit_id": "q1", "attributes": "family=W"}]) is None   # attribute missing
