"""S178 FIX-GOV (GOV-1, GOV-2, GOV-6): the superseded-output registry and the guard that live tools call on their inputs.

Synthetic registries (invented paths) test the guard; the real registry is checked for chain integrity: every row's file exists
on disk (or the row declares it deleted), every recorded sha256 equals the file, and no ``superseded_by`` is itself superseded.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

from culinarystate import governance_superseded as G

ROOT = Path(__file__).resolve().parents[2]
HEADER = ["path", "sha256", "superseded_by", "superseded_by_sha256", "reason", "recorded_at", "status"]


def _write(tmp: Path, rows: list[dict]) -> Path:
    p = tmp / "registry" / "superseded_outputs_S176.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in HEADER})
    return p


def _row(path, by="reports/x/new.json", status="SUPERSEDED_KEPT_ON_RECORD"):
    return {"path": path, "superseded_by": by, "reason": "test", "recorded_at": "2026-11-09", "status": status}


def test_guard_refuses_a_registered_path_and_names_its_replacement(tmp_path):
    _write(tmp_path, [_row("reports/x/old.json")])
    with pytest.raises(G.SupersededInputError) as e:
        G.assert_not_superseded(["reports/x/new.json", "reports/x/old.json"], root=tmp_path)
    assert "reports/x/old.json" in str(e.value) and "reports/x/new.json" in str(e.value)
    G.assert_not_superseded(["reports/x/new.json"], root=tmp_path)          # a current path passes


def test_guard_normalises_absolute_and_dotted_paths(tmp_path):
    _write(tmp_path, [_row("reports/x/old.json")])
    for p in (tmp_path / "reports/x/old.json", "./reports/x/old.json", "reports/x/../x/old.json", Path("reports/x/old.json")):
        with pytest.raises(G.SupersededInputError):
            G.assert_not_superseded([p], root=tmp_path)


def test_guard_refuses_files_under_a_registered_directory(tmp_path):
    _write(tmp_path, [_row("data/derived/old_records/", by="data/derived/new_records/")])
    with pytest.raises(G.SupersededInputError):
        G.assert_not_superseded(["data/derived/old_records/FOODCOM/part-00000.jsonl"], root=tmp_path)
    with pytest.raises(G.SupersededInputError):
        G.assert_not_superseded(["data/derived/old_records"], root=tmp_path)
    G.assert_not_superseded(["data/derived/old_records_v2/part-00000.jsonl"], root=tmp_path)   # prefix of a name is not a match


def test_guard_refuses_invalid_rows_too(tmp_path):
    _write(tmp_path, [_row("reports/x/bad.json", by="composition/ lot census", status="INVALID_SUPERSEDED_KEPT_ON_RECORD")])
    with pytest.raises(G.SupersededInputError):
        G.assert_not_superseded(["reports/x/bad.json"], root=tmp_path)


def test_missing_registry_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError):
        G.assert_not_superseded(["reports/x/new.json"], root=tmp_path)


def test_registry_header_is_the_fixed_column_set():
    with open(ROOT / G.REGISTRY, newline="", encoding="utf-8") as fh:
        assert next(csv.reader(fh)) == HEADER


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def test_real_registry_rows_exist_hash_and_chain_to_a_live_replacement():
    rows = G.load_registry(ROOT)
    assert rows, "registry is empty"
    paths = [r["path"] for r in rows]
    assert len(paths) == len(set(paths)), "duplicate path rows"
    registered = set(paths)
    for r in rows:
        p = ROOT / r["path"]
        if G.declared_deleted(r):
            assert not p.exists(), r["path"]
        else:
            assert p.is_file(), f"missing on disk and not declared deleted: {r['path']}"
            assert r["sha256"] and _sha(p) == r["sha256"], f"sha256 differs: {r['path']}"
        by = r["superseded_by"]
        assert by, r["path"]
        assert by not in registered, f"{r['path']} -> {by}, which is itself superseded"
        if G.is_repo_path(by):
            assert (ROOT / by).is_file(), f"replacement missing: {by}"
            assert r["superseded_by_sha256"] and _sha(ROOT / by) == r["superseded_by_sha256"], f"replacement sha256 differs: {by}"


def test_real_registry_covers_the_s177_s178_superseded_physics_and_router_outputs():
    reg = {r["path"] for r in G.load_registry(ROOT)}
    fams = ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS", "TASTESET")
    want = [f"reports/step26/binding_census_L1_{f}_full_S176_v02.json" for f in fams]
    want += [f"reports/step26/scenario_L2_{f}_full_S177_v03.json" for f in fams]
    want += [f"reports/step26/nonheat_L1_{f}_full_S176.json" for f in fams]
    want += [f"reports/step26/nonheat_L2_{f}_full_S177_v03.json" for f in fams]
    want += [f"reports/step26/scenario_L2_{f}_full_S176_v02.json" for f in fams]
    want += [f"reports/step26/nonheat_L2_{f}_full_S176_v02.json" for f in fams]
    want += ["reports/step26/binding_census_L1_1000_S176_v02.json", "reports/step26/scenario_L2_1000_S177_v03.json",
             "reports/step26/nonheat_L1_1000_S176.json", "reports/step26/nonheat_L2_1000_S177_v03.json",
             "reports/step23/router_demo_census_vitc_nonBBC_1000_S176.json", "reports/step23/router_demo_census_vitc_nonBBC_full_S176.json",
             "reports/lotstate/lotstate_census_1000_S176_ph_provisional.json"]
    missing = [w for w in want if w not in reg]
    assert not missing, missing


def test_ph_provisional_row_is_invalid_and_row_13_reason_is_fixed():
    rows = {r["path"]: r for r in G.load_registry(ROOT)}
    prov = rows["reports/lotstate/lotstate_census_1000_S176_ph_provisional.json"]
    assert prov["status"].startswith("INVALID") and "EXACT" in prov["reason"]
    plain = rows["reports/lotstate/lotstate_census_1000_S176.json"]
    assert "pH flags invalid" not in plain["reason"] and "no pH data" in plain["reason"]
