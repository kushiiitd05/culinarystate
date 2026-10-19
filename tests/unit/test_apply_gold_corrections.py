import csv
import importlib.util
import json
from pathlib import Path

from culinarystate.annotation.examples import white_sauce

spec = importlib.util.spec_from_file_location("agc", Path(__file__).resolve().parents[2] / "tools" / "apply_gold_corrections.py")
agc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agc)


def _mk(tmp_path, decision):
    gd = tmp_path / "v1"
    gd.mkdir()
    d = white_sauce()
    d["recipe_id"] = "R9"
    (gd / "R9.ADJUDICATED.json").write_text(json.dumps(d))
    new_events = d["steps"][0]["events"][:1]
    q = tmp_path / "q.csv"
    with q.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item_id", "decision", "patch_json"])
        w.writeheader()
        w.writerow({"item_id": "GC-001", "decision": decision,
                    "patch_json": json.dumps({"op": "replace_events", "recipe": "R9", "step": 0, "events": new_events})})
    return gd, q, d


def test_empty_decision_applies_nothing(tmp_path):
    gd, q, _ = _mk(tmp_path, "")
    n, errs = agc.apply(gd, q, tmp_path / "out")
    assert (n, errs) == (0, []) and not (tmp_path / "out").exists()


def test_rejected_is_not_applied(tmp_path):
    gd, q, _ = _mk(tmp_path, "reject")
    assert agc.apply(gd, q, tmp_path / "out")[0] == 0
    assert not (tmp_path / "out").exists()


def test_valid_approved_patch_is_written_with_provenance_and_v1_untouched(tmp_path):
    gd, q, d = _mk(tmp_path, "Approve")
    rows = list(csv.DictReader(q.open()))
    same = {"op": "replace_events", "recipe": "R9", "step": 0, "events": d["steps"][0]["events"]}   # identical events: must validate
    rows[0]["patch_json"] = json.dumps(same)
    with q.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    before = (gd / "R9.ADJUDICATED.json").read_text()
    n, errs = agc.apply(gd, q, tmp_path / "out")
    assert (n, errs) == (1, [])
    out = json.loads((tmp_path / "out" / "R9.ADJUDICATED.json").read_text())
    assert "GC-001 approved by Kush" in out["notes"] and "not independent" in out["notes"]
    assert (gd / "R9.ADJUDICATED.json").read_text() == before


def test_approval_that_breaks_replay_writes_nothing(tmp_path):
    gd, q, d = _mk(tmp_path, "approve")
    rows = list(csv.DictReader(q.open()))
    rows[0]["patch_json"] = json.dumps({"op": "replace_events", "recipe": "R9", "step": 0,
                                        "events": [{"type": "Transform", "target": "no such entity", "process": "stir"}]})
    with q.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    n, errs = agc.apply(gd, q, tmp_path / "out")
    assert n == 0 and errs and not (tmp_path / "out").exists()


def _queue(tmp_path, patches):
    q = tmp_path / "q2.csv"
    with q.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item_id", "decision", "patch_json"])
        w.writeheader()
        for i, p in enumerate(patches):
            w.writerow({"item_id": f"GC-{i + 1:03d}", "decision": "approve", "patch_json": json.dumps(p)})
    return q


def test_coref_and_alternative_ops(tmp_path):
    gd = tmp_path / "v1"
    gd.mkdir()
    d = white_sauce()
    d["recipe_id"] = "R9"
    t = d["steps"][0]["text"]
    d["steps"][0]["coref"] = [{"mention": t[1:3], "start": 1, "end": 3, "entity": "UNKNOWN"},
                              {"mention": t[9:11], "start": 9, "end": 11, "entity": "UNKNOWN"}]
    line = d["ingredient_lines"][0]
    (gd / "R9.ADJUDICATED.json").write_text(json.dumps(d))
    q = _queue(tmp_path, [{"op": "drop_coref", "recipe": "R9", "step": 0, "starts": [1]},
                          {"op": "set_coref", "recipe": "R9", "step": 0, "start": 9, "entity": line["entity"]},
                          {"op": "set_line_alt", "recipe": "R9", "line": 0, "alternatives": ["x"],
                           "spans": [{"start": 0, "end": 1, "label": "ALTERNATIVE", "text": line["text"][0]}]}])
    n, errs = agc.apply(gd, q, tmp_path / "out")
    assert (n, errs) == (1, [])
    out = json.loads((tmp_path / "out" / "R9.ADJUDICATED.json").read_text())
    assert [c["start"] for c in out["steps"][0]["coref"]] == [9] and out["steps"][0]["coref"][0]["entity"] == line["entity"]
    assert out["ingredient_lines"][0]["alternatives"] == ["x"]
    assert any(s["label"] == "ALTERNATIVE" for s in out["ingredient_lines"][0]["spans"])
