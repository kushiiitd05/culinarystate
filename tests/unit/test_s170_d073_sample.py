"""S170: D-073 R1 (RA_IMPLICIT_CURRENT_V1) precision sample and scoring (pre-registration in reports/step17)."""
import csv
import json

import pytest

from culinarystate.extraction import d073_current_sample as S

R1_TEXT = "Mix the flour and sugar in a bowl. Chop the onion and garlic. Stir."
NO_R1_TEXT = "Preheat the oven. Mix the flour and sugar. Bake."


def test_r1_fires_when_tier_ambiguous_and_current_live():
    cands = S.r1_candidates(R1_TEXT, locale=None)
    assert len(cands) == 1
    c = cands[0]
    assert R1_TEXT[c["offset"]:c["offset"] + len(c["surface"])] == c["surface"] == "Stir"
    assert c["tier_size"] >= 2
    assert sorted(c["current_leaves"]) == ["flour", "sugar"]


def test_r1_silent_when_tier_unique_or_empty():
    assert S.r1_candidates(NO_R1_TEXT, locale=None) == []


def test_candidates_do_not_change_the_binder():
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.quantity import rc2_dryrun as D
    rung, schema = RungA(), D.load_schema()
    src = SourceText.from_raw("T", R1_TEXT)
    before = rung.run(src, rung.config(locale=None), schema=schema).graph
    S.r1_candidates(R1_TEXT, locale=None, rung=rung)
    after = rung.run(src, rung.config(locale=None), schema=schema).graph
    assert before == after
    assert "IMPLICIT_ARG_AMBIGUOUS" in after.diagnostics


def _cands(n):
    return {f"r{i}": [{"offset": 5, "surface": "Stir"}, {"offset": 40, "surface": "Bake"}] for i in range(n)}


def test_pick_one_per_recipe_smallest_rank_and_excludes():
    picked = S.pick_sample(_cands(100), seed="s", n=60, excluded={"r0", "r1"})
    ids = [p["recipe_id"] for p in picked]
    assert len(ids) == 60 == len(set(ids))
    assert not {"r0", "r1"} & set(ids)
    assert ids == sorted(ids, key=lambda r: S.rank("s", r))
    assert picked == S.pick_sample(_cands(100), seed="s", n=60, excluded={"r0", "r1"})


def test_pick_returns_all_when_fewer():
    assert len(S.pick_sample(_cands(7), seed="s", n=60, excluded=set())) == 7


@pytest.mark.parametrize("correct,n,verdict", [(54, 60, "LAND"), (53, 60, "DO_NOT_LAND"), (60, 60, "LAND"),
                                               (20, 20, "LAND"), (15, 20, "DO_NOT_LAND")])
def test_score_landing_rule(correct, n, verdict):
    labels = ["CORRECT"] * correct + ["WRONG_OBJECT"] * (n - correct)
    out = S.score(labels)
    assert out["verdict"] == verdict
    assert out["label_counts"]["CORRECT"] == correct and out["n"] == n


def test_score_wilson_and_unknown_labels():
    out = S.score(["CORRECT"] * 54 + ["NO_OBJECT"] * 6)
    assert 0.798 <= out["wilson95_lower"] < 0.799  # 54/60: 0.7985 (prereg amendment)
    with pytest.raises(ValueError):
        S.score(["CORRECT", "maybe"])
    with pytest.raises(ValueError):
        S.score([])


def test_tool_refuses_tracked_private_and_writes_counts_only(tmp_path, monkeypatch):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("d073tool", Path(__file__).resolve().parents[2]
                                                  / "tools/d073_precision_sample.py")
    T = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(T)
    recs = [{"recipe_id": f"x{i}", "source_family": "WIKIBOOKS", "steps": [R1_TEXT]} for i in range(5)]
    src = lambda fams, root: iter(r for r in recs if r["source_family"] in fams)  # noqa: E731
    priv, out = tmp_path / "priv.csv", tmp_path / "counts.json"
    monkeypatch.setattr(T, "_tracked_by_git", lambda p: False)
    assert T.main(["draw", "--seed", "s", "--recipes", "5", "--exclude-seed", "e", "--exclude-size", "0",
                   "--out-private", str(priv), "--out", str(out)], record_source=src) == 0
    rows = list(csv.DictReader(priv.open()))
    assert len(rows) == 5 and all(r["label"] == "" for r in rows)
    counts = json.loads(out.read_text())
    assert counts["contains_text"] is False and counts["sample_items"] == 5
    assert "x0" not in out.read_text() and "Stir" not in out.read_text()
    with pytest.raises(SystemExit):  # refuses overwrite
        T.main(["draw", "--seed", "s", "--recipes", "5", "--exclude-seed", "e", "--exclude-size", "0",
                "--out-private", str(priv), "--out", str(out)], record_source=src)
    for r in rows:
        r["label"] = "CORRECT"
    with priv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    score_out = tmp_path / "score.json"
    assert T.main(["score", "--private", str(priv), "--out", str(score_out)]) == 0
    s = json.loads(score_out.read_text())
    assert s["n"] == 5 and s["contains_text"] is False and "x0" not in score_out.read_text()
    monkeypatch.setattr(T, "_tracked_by_git", lambda p: True)
    with pytest.raises(SystemExit):
        T.main(["draw", "--seed", "s", "--recipes", "5", "--exclude-seed", "e", "--exclude-size", "0",
                "--out-private", str(tmp_path / "p2.csv"), "--out", str(tmp_path / "c2.json")], record_source=src)
