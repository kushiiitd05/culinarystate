"""S178 PHYS2 T4-C01-R1: the PROC -> process-family registry (one primary family per PROC, ambiguous verbs listed)."""
from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import nonheat_binding as NB
from culinarystate.simulation import proc_family_registry as PR

ROOT = PR.ROOT


@pytest.fixture(scope="module")
def rows():
    return PR.read_registry()


def test_committed_registry_validates_against_the_ledger_and_the_binders(rows):
    assert PR.validate(rows) == []


def test_every_proc_exactly_once_with_one_primary_family(rows):
    procs = PR.latest_proc()
    ids = [r["proc_id"] for r in rows]
    assert len(ids) == len(set(ids)) == len(procs)  # the ledger has 156 PROCs, not the 93 of the board text
    assert set(ids) == set(procs)
    assert all(r["primary_family"] in PR.PRIMARY_FAMILIES for r in rows)
    assert {r["primary_family"] for r in rows} >= set(PR.NONHEAT_FAMILIES) | set(PR.HEAT_FAMILIES)


def test_primary_family_equals_the_ledger_family_except_store(rows):
    diff = {r["proc_id"]: (r["ledger_family"], r["primary_family"]) for r in rows
            if r["ledger_family"] != r["primary_family"] and r["primary_family"] != "BOOKKEEPING"}
    assert diff == {PR.STORE_PROC: ("TRANSFER", "STORAGE")}


def test_binders_agree_with_the_registry(rows):
    procs = PR.latest_proc()
    nh = NB.NonHeatBinder(type("B", (), {"family": {p: r["family"] for p, r in procs.items()}})(), {})
    for r in rows:
        want = r["primary_family"] if r["primary_family"] in PR.NONHEAT_FAMILIES else None
        assert nh.nh_family(r["proc_id"]) == want, r["proc_id"]
        assert (r["primary_family"] in PR.HEAT_FAMILIES) == (r["ledger_family"] in CB.HEAT)
        if r["primary_family"] in PR.NONHEAT_FAMILIES:
            assert r["form_candidate_class"] == NB.FORM_CANDIDATE[r["primary_family"]]
    assert {r["binder"] for r in rows} == {"condition_binding", "nonheat_binding", "endpoint_cues", "none"}


def test_ambiguous_verbs_are_listed_with_rules(rows):
    by = {r["proc_id"]: r for r in rows}
    for pid, name in (("PROC-000129", "soak"), ("PROC-000155", "brine"), ("PROC-000133", "dry"), ("PROC-000042", "rest")):
        r = by[pid]
        assert r["canonical"] == name or name in r["canonical"].split("-") or r["canonical"] in (name, "dry")
        assert r["ambiguity_flag"] == "YES" and r["ambiguity_rule"] and r["secondary_family"] not in ("", r["primary_family"])
    for r in rows:
        assert (r["ambiguity_flag"] == "YES") == bool(r["ambiguity_rule"]) == bool(r["secondary_family"])
    assert sum(r["ambiguity_flag"] == "YES" for r in rows) >= 20


def test_unsupported_media_have_no_form(rows):
    unsupported = {r["proc_id"] for r in rows if r["form_candidate_class"] == "UNSUPPORTED_MEDIUM_NO_FORM"}
    assert {"PROC-000003", "PROC-000004", "PROC-000007"} <= unsupported  # grill, toast (RADIANT), microwave


def test_validator_catches_corruption(rows):
    def broken(mutate):
        c = copy.deepcopy(rows)
        mutate(c)
        return PR.validate(c)
    assert broken(lambda c: c.append(dict(c[0])))                                   # duplicate
    assert broken(lambda c: c.pop())                                                # missing PROC
    assert broken(lambda c: c[0].update(primary_family="NOT_A_FAMILY"))
    assert broken(lambda c: next(r for r in c if r["proc_id"] == "PROC-000038").update(primary_family="RESTING"))  # nh_family disagrees
    assert broken(lambda c: next(r for r in c if r["proc_id"] == "PROC-000129").update(ambiguity_rule=""))
    assert broken(lambda c: next(r for r in c if r["proc_id"] == "PROC-000001").update(form_candidate_class=""))
    assert broken(lambda c: [r.update(primary_family="BOOKKEEPING") for r in c if r["primary_family"] == "RESTING"])  # family uninhabited


def test_build_is_deterministic_and_matches_the_committed_file(rows, tmp_path):
    built = PR.build_rows()
    out = tmp_path / "r.csv"
    PR.write_registry(out, built)
    assert out.read_bytes() == (ROOT / PR.REGISTRY).read_bytes()


def test_tool_validate_and_refuse_overwrite(capsys, tmp_path):
    spec = importlib.util.spec_from_file_location("s178_phys_proc_registry", ROOT / "tools/s178_phys_proc_registry.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.main(["--validate"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["rows"] == 156 and out["problems"] == [] and out["sha256"] == hashlib.sha256((ROOT / PR.REGISTRY).read_bytes()).hexdigest()
    with pytest.raises(SystemExit):
        mod.main(["--build"])  # the committed registry exists: refuses to overwrite


def test_registry_carries_no_third_party_text(rows):
    assert all(r["status"] == PR.STATUS for r in rows)
    header = next(csv.reader(open(ROOT / PR.REGISTRY, encoding="utf-8")))
    assert tuple(header) == PR.COLUMNS
