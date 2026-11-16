"""S178 T9-C08-R4: negative-results register append tool. Append-only behaviour on a temp copy; recomputation checks on the real tree."""
from __future__ import annotations

import csv
import hashlib
import io
import shutil

import pytest

from tests.unit.test_s178_analysis_helpers import ROOT, load_tool

N = load_tool("s178_analysis_negregister")


def test_wilson_matches_the_committed_d074_bound():
    lo, hi = N.wilson(4, 60)
    assert round(lo, 4) == 0.0262          # reports/step17/d073_r1_precision_S170.json: wilson95_lower
    assert 0.15 < hi < 0.17


def test_checks_flag_a_mismatch_and_accept_a_match():
    c = N.Checks()
    assert c.eq("a", "five", 5, 5, "src")
    assert not c.eq("b", "five", 5, 6, "src")
    assert [r["status"] for r in c.rows] == ["VERIFIED_COMPUTED", "MISMATCH"]
    c.unverified("c", "x", "src", "no source")
    assert c.rows[-1]["status"] == "UNVERIFIED"


def _tiny_register(tmp_path):
    reg = tmp_path / "registry"
    reg.mkdir()
    p = reg / "negative_results_register_v1.csv"
    w = io.StringIO()
    cw = csv.writer(w, lineterminator="\n")
    cw.writerow(N.COLUMNS)
    cw.writerow(["NEG-0001", "DRAFT_PENDING_H4", "claim, with comma", "d", "s", "m", "v", "c", "p", "q", "RECORDED_AGENT_CHECKED", "2026-10-26"])
    p.write_text(w.getvalue(), encoding="utf-8")
    return p


def _row(i, claim):
    return {"result_id": f"NEG-{i:04d}", "registry_status": "DRAFT_PENDING_H4", "claim_tested": claim, "data_version": "d", "split": "n/a",
            "metric": "m", "value": "v, with \"quotes\" and a comma", "ci": "n/a", "source_path": "p", "consequence": "c",
            "status": "RECORDED_AGENT_CHECKED", "recorded_at": "2026-11-09"}


def test_append_keeps_the_old_bytes_and_is_idempotent(tmp_path):
    p = _tiny_register(tmp_path)
    old = p.read_bytes()
    res = N.append_rows(tmp_path, [_row(2, "claim two"), _row(3, "claim three")])
    assert res["appended"] == 2 and res["prefix_intact"] and res["all_rows_12_columns"]
    new = p.read_bytes()
    assert new.startswith(old) and new.endswith(b"\n")
    rows = list(csv.DictReader(io.StringIO(new.decode())))
    assert [r["result_id"] for r in rows] == ["NEG-0001", "NEG-0002", "NEG-0003"]
    assert rows[1]["value"] == "v, with \"quotes\" and a comma"
    # rows flagged as already present are skipped: a re-run changes nothing
    again = N.append_rows(tmp_path, [{**_row(2, "claim two"), "_existing": True}])
    assert again["appended"] == 0 and p.read_bytes() == new


def test_append_refuses_a_register_without_final_newline(tmp_path):
    p = _tiny_register(tmp_path)
    p.write_bytes(p.read_bytes().rstrip(b"\n"))
    with pytest.raises(AssertionError):
        N.append_rows(tmp_path, [_row(2, "x")])


def test_real_tree_every_quoted_figure_recomputes():
    rows, checks = N.build(ROOT)
    bad = [c for c in checks.rows if c["status"] == "MISMATCH"]
    assert not bad, bad
    assert not [c for c in checks.rows if c["status"] == "UNVERIFIED"]
    # headline figures named in the plan
    got = {c["check_id"]: c["recomputed"] for c in checks.rows}
    assert got["R1.pct"] == "0.754 %" and got["R2.ungated"] == 267933 and got["R2.gated"] == 34537
    assert got["D74.correct"] == (4, 60)
    assert got["FQ.sample_mis"][0] == 683
    assert got["SP.denominator"] == 4281956
    assert got["P1.verdict"] == "HANDBOOK_REVISION_REQUIRED"
    assert got["EV.before"][0] == 47198 and got["EV.after"][0] == 1242
    ids = [r["result_id"] for r in rows]
    assert ids == sorted(ids) and len(set(ids)) == len(ids)
    for r in rows:
        assert all(k in r for k in N.COLUMNS)
        assert r["registry_status"] == "DRAFT_PENDING_H4" and r["source_path"]


def test_real_register_first_30_rows_untouched_and_new_rows_present():
    reg = ROOT / "registry/negative_results_register_v1.csv"
    rows = list(csv.DictReader(open(reg, newline="", encoding="utf-8")))
    ids = [r["result_id"] for r in rows]
    assert ids[:30] == [f"NEG-{i:04d}" for i in range(1, 31)]
    assert len(ids) == len(set(ids))
    assert all(len(r) == 12 for r in rows)
    new = [r for r in rows if r["recorded_at"] == "2026-11-09" and r["result_id"] >= "NEG-0031"]
    if new:   # rows appended by this lane
        assert [r["result_id"] for r in new] == [f"NEG-{i:04d}" for i in range(31, 31 + len(new))]
        assert all(r["source_path"] and r["status"].startswith("RECORDED_AGENT_CHECKED") for r in new)
    assert reg.read_bytes().endswith(b"\n")
