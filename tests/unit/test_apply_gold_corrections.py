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
