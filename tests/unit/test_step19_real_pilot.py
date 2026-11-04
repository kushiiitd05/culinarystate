"""Synthetic controls for the real-pilot gate and P1 draw tool (S154).

The tool must refuse to draw unless every human prerequisite is recorded:
signatures of both annotators, H5 start authorisation, a Kush-supplied
pre-frame nonce with matching commitment, capacity and budget, signed
THR-19P rows, instrument and pilot-column confirmation, resolved method
amendments and the bound draw specification. Everything here is synthetic;
the real start record in the repository is only read.
"""
import copy
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

from culinarystate.annotation import pilot_real as R

ROOT = Path(__file__).resolve().parents[2]
REAL_RECORD = ROOT / "reports/step19/pilot_start_record.UNSIGNED.json"
NONCE = "synthetic-nonce-not-a-real-pilot-value"
FRAME_COLS = ["recipe_id", "source_family", "source_id", "usage_class", "n_ingredient_lines", "n_steps",
              "complexity_c", "complexity_tier", "stratum_simple", "stratum_indian", "stratum_random",
              "text_regex_strata_status", "split_group_id", "group_id", "group_basis", "group_size",
              "duplicate_group_id", "recipe_family_id", "dish_family_candidate_id"]
STRATA_COLS = ["recipe_id", "baking", "drain_discard", "reserve_split", "reserve_split_v2", "multi_component"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def make_root(tmp_path, *, n_per_cell=35):
    root = tmp_path / "repo"
    rdir = root / "reports/step19"
    rdir.mkdir(parents=True)
    (rdir / "design.md").write_text("synthetic design\n")
    (rdir / "bound.md").write_text("synthetic bound file\n")
    (root / "registry").mkdir()
    rows = [{"threshold_id": f"THR-19P-{i:02d}", "registry_status": "PREREGISTERED_2026-11-03",
             "signed_by": "Kush Tokas; Parv Goyal", "signed_at": "2026-11-03"} for i in range(1, 36)]
    write_csv(root / "registry/preregistered_thresholds_v1.csv",
              ["threshold_id", "registry_status", "signed_by", "signed_at"], rows)
    (root / "DECISIONS.md").write_text("### D-901 · 2026-11-03 · synthetic H5\n### D-902 · synthetic methods\n")
    record = {
        "status": "SIGNED", "document": "design.md", "sha256": sha(rdir / "design.md"),
        "signers": ["Kush", "Parv"], "date": "2026-11-03",
        "bound_files": [{"path": "bound.md", "sha256": sha(rdir / "bound.md")}],
        "purpose": "REAL_PILOT_START", "selected_instrument": "CURRENT_V0_PLUS_HANDBOOK_V1_ADDENDUM_A",
        "pre_frame_nonce": NONCE, "nonce_supplier": "Kush",
        "nonce_commitment": hashlib.sha256(NONCE.encode()).hexdigest(),
        "nonce_committed_at": "2026-11-03T00:00:00+00:00",
        "weekly_capacity_hours": {"Kush": 6, "Parv": 6}, "per_annotator_budget_B_h": {"Kush": 40, "Parv": 40},
        "pilot_column_parv_choice": "reserve_split_v2", "pilot_column_confirmation": "CONFIRMED_BY_KUSH",
        "methodological_amendments": {"status": "RESOLVED", "decision_id": "D-902"},
        "human_start_authorization": {"decision_id": "D-901", "decided_by": "Kush", "waves": ["P1"]},
        "draw_algorithm": R.DRAW_ALGORITHM_ID, "real_draw_performed": False,
    }
    (rdir / "start.json").write_text(json.dumps(record))
    frame, strata = [], []
    n = 0
    for cell, stratum, source, tier in R.P1_CELLS:
        for k in range(n_per_cell):
            n += 1
            rid = f"SYNREC-{n:05d}"
            frame.append({c: "" for c in FRAME_COLS} | {
                "recipe_id": rid, "source_family": source, "complexity_tier": tier,
                "stratum_simple": "Y" if stratum == "simple" else "N",
                "stratum_indian": "Y" if stratum == "indian" else "N", "stratum_random": "Y",
                "group_id": f"SYNGRP-{n // 2:05d}"})
            strata.append({"recipe_id": rid, **{c: ("Y" if c == stratum or (stratum == "reserve_split" and c == "reserve_split_v2") else "N")
                                                for c in STRATA_COLS[1:]}})
    write_csv(root / "frame/frame.csv", FRAME_COLS, frame)
    write_csv(root / "frame/strata.csv", STRATA_COLS, strata)
    return root


def record_path(root):
    return root / "reports/step19/start.json"


def mutate(root, fn):
    p = record_path(root)
    rec = json.loads(p.read_text())
    fn(rec)
    p.write_text(json.dumps(rec))


def codes(root, **kw):
    return {b.code for b in R.check_prerequisites(record_path(root), root=root, **kw)}


def test_real_unsigned_record_is_refused_for_every_missing_human_fact():
    before = REAL_RECORD.read_bytes()
    found = {b.code for b in R.check_prerequisites(REAL_RECORD, root=ROOT)}
    assert {"START_RECORD_UNSIGNED", "H5_START_AUTHORIZATION_MISSING", "NONCE_MISSING", "CAPACITY_MISSING",
            "BUDGET_MISSING", "INSTRUMENT_NOT_SELECTED", "PILOT_COLUMN_NOT_CONFIRMED",
            "METHOD_AMENDMENTS_UNRESOLVED", "DRAW_SPEC_NOT_BOUND"} <= found
    # D-046 (2026-11-03): THR-19P-01..35 were signed in the registry; the unsigned record itself is unchanged.
    assert "THRESHOLDS_NOT_SIGNED" not in found
    assert REAL_RECORD.read_bytes() == before
    assert all(b.owner for b in R.check_prerequisites(REAL_RECORD, root=ROOT))


def test_complete_synthetic_record_has_no_blockers(tmp_path):
    root = make_root(tmp_path)
    assert codes(root) == set()


MUTATIONS = {
    "START_RECORD_UNSIGNED": lambda r: r.update(signers=[], status="UNSIGNED_TEMPLATE"),
    "BOTH_ANNOTATOR_SIGNATURES_REQUIRED": lambda r: r.update(signers=["Kush"], single_signer_override={"reason": "x", "by": "Kush"}),
    "H5_START_AUTHORIZATION_MISSING": lambda r: r.update(human_start_authorization=None),
    "H5_DECISION_NOT_RECORDED": lambda r: r["human_start_authorization"].update(decision_id="D-999"),
    "H5_WAVE_NOT_AUTHORISED": lambda r: r["human_start_authorization"].update(waves=["P2"]),
    "NONCE_MISSING": lambda r: r.update(pre_frame_nonce=None),
    "NONCE_SUPPLIER_NOT_KUSH": lambda r: r.update(nonce_supplier="agent"),
    "NONCE_COMMITMENT_MISMATCH": lambda r: r.update(nonce_commitment="0" * 64),
    "NONCE_COMMITTED_AT_MISSING": lambda r: r.update(nonce_committed_at=None),
    "CAPACITY_MISSING": lambda r: r["weekly_capacity_hours"].update(Parv=None),
    "BUDGET_MISSING": lambda r: r["per_annotator_budget_B_h"].update(Kush=0),
    "INSTRUMENT_NOT_SELECTED": lambda r: r.update(selected_instrument=None),
    "PILOT_COLUMN_NOT_CONFIRMED": lambda r: r.update(pilot_column_confirmation="PENDING_KUSH"),
    "METHOD_AMENDMENTS_UNRESOLVED": lambda r: r.update(methodological_amendments="AI_DRAFT_PENDING_EXPERT_VERIFICATION"),
    "DRAW_SPEC_NOT_BOUND": lambda r: r.update(draw_algorithm=None),
    "ALREADY_DRAWN": lambda r: r.update(real_draw_performed=True),
    "DESIGN_HASH_MISMATCH": lambda r: r.update(sha256="f" * 64),
    "BOUND_FILE_HASH_MISMATCH": lambda r: r["bound_files"][0].update(sha256="e" * 64),
}


@pytest.mark.parametrize("code", sorted(MUTATIONS))
def test_each_missing_prerequisite_blocks_and_draw_refuses(tmp_path, code):
    root = make_root(tmp_path)
    mutate(root, MUTATIONS[code])
    assert code in codes(root)
    with pytest.raises(R.PilotGateError) as err:
        R.draw_p1(record_path(root), root / "frame/frame.csv", root / "frame/strata.csv",
                  out_dir=root / "registry/recipe_semantics/deep_gold_pilot_v1", root=root)
    assert code in str(err.value)
    assert not (root / "registry/recipe_semantics/deep_gold_pilot_v1").exists()


def test_unsigned_threshold_rows_block(tmp_path):
    root = make_root(tmp_path)
    p = root / "registry/preregistered_thresholds_v1.csv"
    rows = list(csv.DictReader(open(p)))
    rows[4]["signed_by"] = ""
    write_csv(p, list(rows[0]), rows[:-1])
    assert "THRESHOLDS_NOT_SIGNED" in codes(root)


def test_p2_wave_is_refused_until_its_spec_exists(tmp_path):
    root = make_root(tmp_path)
    assert "WAVE_P2_NOT_SUPPORTED" in codes(root, wave="P2")


def draw(root, **kw):
    return R.draw_p1(record_path(root), root / "frame/frame.csv", root / "frame/strata.csv",
                     out_dir=root / "registry/recipe_semantics/deep_gold_pilot_v1", root=root, **kw)


def test_draw_is_deterministic_one_per_group_with_two_reserves(tmp_path):
    root = make_root(tmp_path)
    result = draw(root)
    rows = result["rows"]
    assert len(rows) == 21 and {r["role"] for r in rows} == {"PRIMARY", "RESERVE_1", "RESERVE_2"}
    assert len({r["group_key"] for r in rows}) == 21
    assert [r["cell_id"] for r in rows if r["role"] == "PRIMARY"] == [c[0] for c in R.P1_CELLS]
    manifest = root / "registry/recipe_semantics/deep_gold_pilot_v1/manifest_P1.csv"
    assert manifest.read_text().splitlines()[0].split(",") == list(R.MANIFEST_COLUMNS)
    assert (manifest.parent / "manifest_P1.csv.sha256").read_text().split()[0] == sha(manifest)
    other = make_root(tmp_path / "again")
    assert [r["recipe_id"] for r in draw(other)["rows"]] == [r["recipe_id"] for r in rows]
    seed = hashlib.sha256(result["frame_sha256"].encode() + b"P1" + NONCE.encode()).digest()[:8].hex()
    assert {r["seed_hex"] for r in rows} == {seed}


def test_selected_rows_match_their_cell(tmp_path):
    root = make_root(tmp_path)
    frame = {r["recipe_id"]: r for r in csv.DictReader(open(root / "frame/frame.csv"))}
    for row in draw(root)["rows"]:
        f = frame[row["recipe_id"]]
        assert f["source_family"] == row["source_family"] and f["complexity_tier"] == row["tier"]


def test_nonce_changes_the_draw(tmp_path):
    root = make_root(tmp_path)
    a = [r["recipe_id"] for r in draw(root)["rows"]]
    root2 = make_root(tmp_path / "b")
    new = "another-synthetic-nonce"
    mutate(root2, lambda r: r.update(pre_frame_nonce=new, nonce_commitment=hashlib.sha256(new.encode()).hexdigest()))
    assert [r["recipe_id"] for r in draw(root2)["rows"]] != a


def test_draw_refuses_second_run_and_never_edits_the_record(tmp_path):
    root = make_root(tmp_path)
    before = record_path(root).read_bytes()
    draw(root)
    with pytest.raises(R.PilotGateError, match="MANIFEST_EXISTS"):
        draw(root)
    assert record_path(root).read_bytes() == before


def test_underfilled_cell_stops_for_a_human_decision(tmp_path):
    root = make_root(tmp_path, n_per_cell=29)
    with pytest.raises(R.PilotGateError, match="CELL_UNDERFILLED"):
        draw(root)


def test_frame_with_text_like_column_is_refused(tmp_path):
    root = make_root(tmp_path)
    p = root / "frame/frame.csv"
    rows = list(csv.DictReader(open(p)))
    write_csv(p, FRAME_COLS + ["title_raw"], [r | {"title_raw": "x"} for r in rows])
    with pytest.raises(R.PilotGateError, match="FRAME_COLUMNS_NOT_ALLOWED"):
        draw(root)


def test_frame_older_than_nonce_commitment_is_refused(tmp_path):
    root = make_root(tmp_path)
    mutate(root, lambda r: r.update(nonce_committed_at="2999-01-01T00:00:00+00:00"))
    with pytest.raises(R.PilotGateError, match="FRAME_PREDATES_NONCE_COMMITMENT"):
        draw(root)


def test_protected_output_location_is_refused(tmp_path):
    root = make_root(tmp_path)
    with pytest.raises(R.PilotGateError, match="PROTECTED_OUTPUT"):
        R.draw_p1(record_path(root), root / "frame/frame.csv", root / "frame/strata.csv",
                  out_dir=root / "ledgers/data", root=root)


def _tool():
    spec = importlib.util.spec_from_file_location("pilot_tool", ROOT / "tools/step19_real_pilot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cli_check_on_real_record_exits_nonzero_and_lists_owners(capsys):
    assert _tool().main(["check", "--record", str(REAL_RECORD)]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["ready"] is False and out["blockers"] and all(b["owner"] for b in out["blockers"])


def test_cli_draw_requires_execute_flag_even_when_ready(tmp_path, capsys):
    root = make_root(tmp_path)
    tool = _tool()
    args = ["draw", "--root", str(root), "--record", str(record_path(root)), "--frame", str(root / "frame/frame.csv"),
            "--strata", str(root / "frame/strata.csv")]
    assert tool.main(args) == 1
    assert "EXECUTE_FLAG_REQUIRED" in capsys.readouterr().out
    assert tool.main(args + ["--execute"]) == 0
    assert (root / "registry/recipe_semantics/deep_gold_pilot_v1/manifest_P1.csv").exists()
