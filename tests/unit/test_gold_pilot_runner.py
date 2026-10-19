import copy
import csv
import importlib.util
import json
from pathlib import Path

from culinarystate.annotation.examples import white_sauce

spec = importlib.util.spec_from_file_location("gpa", Path(__file__).resolve().parents[2] / "tools" / "gold_pilot_agreement.py")
gpa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gpa)


def _setup(tmp_path, ids, done):
    g = tmp_path / "gold"
    (g / "pilot_20" / "Kush").mkdir(parents=True)
    (g / "pilot_20" / "Parv").mkdir(parents=True)
    with (g / "pilot_20_manifest.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["recipe_id"])
        w.writerows([[i] for i in ids])
    with (g / "pilot_7_calibration_manifest.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["recipe_id"])
        w.writerows([[i] for i in ids[:2]])
    for i in ids:
        for who in ("Kush", "Parv"):
            d = copy.deepcopy(white_sauce())
            d.update(recipe_id=i, annotator=who, status="DONE" if i in done else "DRAFT")
            (g / "pilot_20" / who / f"{i}.{who}.json").write_text(json.dumps(d))
    return g


def test_only_ignores_unfinished_nonselected(tmp_path):
    g = _setup(tmp_path, ["R1", "R2", "R3"], done={"R1", "R2"})
    assert gpa.main(["--only", "R1,R2"], gold=g) == 0
    out = json.loads((g / "pilot_20_partial_agreement.json").read_text())
    assert out["pooled"]["recipes"] == ["R1", "R2"]
    m = out["pooled"]["macro_over_recipes"]
    assert m["event_f1_strict"] == m["relation_f1_all_macro"] == m["coref_b_cubed_f1_macro"] == 1.0
    assert m["state_field_agreement_macro"] == m["replay_consistent_fraction"] == 1.0
    assert out["pooled"]["handbook_gate"]["flagged_categories"] == []


def test_selected_unfinished_blocks_and_default_is_all(tmp_path):
    g = _setup(tmp_path, ["R1", "R2", "R3"], done={"R1", "R2"})
    assert gpa.main(["--only", "R1,R3"], gold=g) == 2
    assert gpa.main([], gold=g) == 2


def test_calibration_flag_uses_frozen_list(tmp_path):
    g = _setup(tmp_path, ["R1", "R2", "R3"], done={"R1", "R2"})
    assert gpa.main(["--calibration"], gold=g) == 0
    assert (g / "pilot_20_calibration7_agreement.json").exists()


def test_unknown_only_id_is_rejected(tmp_path):
    g = _setup(tmp_path, ["R1"], done={"R1"})
    try:
        gpa.main(["--only", "R9"], gold=g)
    except SystemExit as e:
        assert "not in the frozen manifest" in str(e)
    else:
        raise AssertionError
