"""S178 H1H3H: end-to-end harness run on the committed SYNTHETIC fixture: stamped, deterministic, guarded, and the
key numbers equal hand computation from tools/s178_d5_fixture.py. The committed output under reports/s178/d5_harness
must equal a fresh run byte for byte."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from culinarystate.evaluation import frozen_guard as FG

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCORE, FIX = load("s178_d5_score"), load("s178_d5_fixture")


def test_fixture_files_are_what_the_builder_writes():
    assert FIX.main(["--check"]) == 0


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    out = tmp_path_factory.mktemp("d5h")
    assert SCORE.main(["--fixture", "--out-dir", str(out), "--n-boot", "200"]) == 0
    return out, json.loads((out / "SYNTHETIC_FIXTURE_d5_scoring_result.json").read_text())


def test_every_section_is_stamped(result):
    out, d = result
    FG.assert_stamped(d)
    assert d["meta"]["mode"] == "FIXTURE" and d["meta"]["guard"]["ok"]
    md = (out / "SYNTHETIC_FIXTURE_d5_scoring_result.md").read_text()
    assert md.startswith(f"# {FG.STAMP}") and md.count(FG.STAMP) >= 2


def test_key_numbers_hand_computed(result):
    _, d = result
    assert (d["router"]["accuracy"]["x"], d["router"]["accuracy"]["n"]) == (14, 16)
    h1 = d["h1"]["comparisons"]
    assert (h1["B4_vs_B1"]["pooled"]["b_treatment_only"], h1["B4_vs_B1"]["pooled"]["c_control_only"]) == (5, 0)
    assert d["h1"]["verdict"]["code"] == "RULE_NOT_MET" and d["h1"]["accuracy"]["B0"]["unresolved"] == 1
    st = d["h3_verdicts"]["options"]["H3-B|one-sided"]["sign_test"]
    assert (st["b_worse_only_unsupported"], st["c_better_only_unsupported"], st["p"]) == (4, 1, 0.1875)
    assert d["h3_summaries"]["rungs"]["B7"]["all"]["ucr"] == 0.2 and d["h3_summaries"]["rungs"]["B2"]["all"]["ucr"] == round(4 / 7, 4)
    pts = d["d4_m2_risk_coverage"]["decision_layer_rungs"]["B7"]["primary_precision_class"]["points"]
    assert [(p["threshold"], p["risk"]["x"], p["risk"]["n"]) for p in pts] == [
        ("QUANTITATIVE", 1, 3), ("INTERVAL", 1, 4), ("QUALITATIVE", 1, 5), ("ABSTAIN", 1, 7)]
    pool = d["retrieval_d4_m1"]["rungs"]["B2"]["blocks"]["pooled_P1_P2_C"]
    assert pool["K=1"]["recall"]["mean"] == 0.45 and pool["K=5"]["recall"]["mean"] == 0.8
    assert pool["K=5"]["compat_recall"]["mean"] == 0.7 and pool["mrr"]["mean"] == 0.65
    assert d["retrieval_d4_m1"]["rungs"]["B0"]["status"] == "NA_NO_RETRIEVAL_LIST" and "B1" not in d["retrieval_d4_m1"]["rungs"]
    c7 = d["c_block"]["rungs"]["B7"]
    assert (c7["agreement_with_gold"]["x"], c7["cannot_separate_rate"]["x"], c7["wrong_order"]) == (2, 1, 0)
    o = d["ood_abstention"]["rungs"]
    assert o["B7"]["abstain_recall_P3"]["x"] == 2 and o["B2"]["abstain_recall_P3"]["x"] == 1
    e = d["enforcement_cost"]["rungs"]["B7"]
    assert (e["sentences_removed"], e["template_fallback"]["x"], e["template_fallback"]["n"]) == (2, 2, 7)
    s = d["slots"]["B7"]["slots"]
    assert [(s[k]["all"]["x"], s[k]["all"]["n"]) for k in ("ingredient", "process", "target")] == [(7, 8), (5, 7), (5, 7)]
    ab = {r["toggle"]: r for r in d["ablation"]["table"] if r["status"] == "RUN"}
    assert {k: v["paired_E1"]["errors_added"] for k, v in ab.items()} == {
        "state_conditioning": 0, "evidence_compatibility": 1, "claim_enforcement": 1, "ood_gate": 1}
    assert d["h3_verdicts"]["options"]["H3-A|one-sided"]["meets_rule"] is False
    assert d["audit"]["status"].startswith("PENDING_HUMAN_LABELS")
    assert d["audit_sample"]["n_sampled"] == d["audit_sample"]["sheets"]["n_items"] > 0
    assert set(d["d4_m2_risk_coverage"]["not_reported_by_design"]) >= {"ECE", "Brier score"}


def test_rerun_is_byte_identical(result, tmp_path):
    out, _ = result
    assert SCORE.main(["--fixture", "--out-dir", str(tmp_path), "--n-boot", "200"]) == 0
    for f in ("SYNTHETIC_FIXTURE_d5_scoring_result.json", "SYNTHETIC_FIXTURE_d5_scoring_result.md"):
        assert (tmp_path / f).read_bytes() == (out / f).read_bytes()
    (tmp_path / "SYNTHETIC_FIXTURE_d5_scoring_result.md").write_text("changed")
    with pytest.raises(SystemExit):                                   # never silently overwrites a different output
        SCORE.main(["--fixture", "--out-dir", str(tmp_path), "--n-boot", "200"])


def test_committed_fixture_output_matches_fresh_run(tmp_path):
    committed = ROOT / SCORE.FIXTURE_OUT / "SYNTHETIC_FIXTURE_d5_scoring_result.json"
    if not committed.is_file():
        pytest.skip("committed fixture output not written yet")
    assert SCORE.main(["--fixture", "--out-dir", str(tmp_path)]) == 0       # pre-registered 10,000 resamples
    assert (tmp_path / committed.name).read_bytes() == committed.read_bytes()


def test_fixture_mode_refuses_input_paths_and_real_mode_refuses(tmp_path, capsys):
    with pytest.raises(SystemExit):
        SCORE.main(["--fixture", "--benchmark", "benchmark/d5/anything.csv"])
    with pytest.raises(SystemExit):                                   # real mode: the lock must fix the H3 option
        SCORE.main(["--freeze-record", "x.json"])
    fdir = ROOT / FG.FIXTURE_DIR
    args = ["--freeze-record", str(tmp_path / "missing.json"), "--benchmark", str(fdir / "benchmark_synthetic.csv"),
            "--runs", str(fdir / "runs_synthetic.jsonl"), "--evd", str(fdir / "evd_synthetic.jsonl"),
            "--relatives", str(fdir / "relatives_synthetic.json"), "--h3-option", "H3-A", "--sidedness", "one-sided",
            "--out-dir", str(tmp_path / "out")]
    assert SCORE.main(args) == 2                                      # guard: no freeze record, fixture inputs
    err = capsys.readouterr().err
    assert "NO_FREEZE_RECORD" in err and "FIXTURE_INPUT_IN_REAL_MODE" in err
    assert not (tmp_path / "out").exists()
    with pytest.raises(SystemExit):
        SCORE.main(args[:-1] + [str(ROOT / SCORE.FIXTURE_OUT)])       # real outputs never go to the synthetic folder
    with pytest.raises(SystemExit):
        SCORE.main(["--n-boot", "5"] + args)


def test_tampered_fixture_refuses(tmp_path, monkeypatch):
    src = ROOT / FG.FIXTURE_DIR
    dst = tmp_path / "tests/fixtures/d5_synthetic"
    shutil.copytree(src, dst)
    bench = dst / "benchmark_synthetic.csv"
    bench.write_text(bench.read_text().replace("SYN-P1-001", "D5-P1-001"))
    monkeypatch.setattr(SCORE, "ROOT", tmp_path)
    assert SCORE.main(["--fixture", "--out-dir", str(tmp_path / "o")]) == 2          # hash no longer matches manifest
    man = json.loads((dst / "manifest.json").read_text())
    man["files"]["benchmark_synthetic.csv"] = FG.sha256_file(bench)                  # re-hash: the row check must still refuse
    (dst / "manifest.json").write_text(json.dumps(man))
    with pytest.raises(FG.GuardRefused) as e:
        SCORE.run_fixture(tmp_path / "o")
    assert e.value.problems == ["NON_SYNTHETIC_ROW: D5-P1-001"]
    assert not (tmp_path / "o").exists()
