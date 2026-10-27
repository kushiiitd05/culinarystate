import json

from culinarystate.lineage import gates


def _inputs(**over):
    base = dict(
        keys_counts={"gates": {"G08-1": {"pass": True}, "G08-2": {"pass": True}, "G08-8": {"pass": True},
                               "G08-10": {"pass": True}}},
        seeded={"all_pass": True, "classes": {}},
        feasibility={"label_verdict": {"overall_A": "publication-component CV"}, "overall": {}},
        largest_share=0.39,
        overlap={"verdict": "NO_OVERLAP_FOUND_IN_BIBLIOGRAPHY"},
        baseline_after={"EVD": "IDENTICAL", "STUDY": "PREFIX_IDENTICAL"},
        export_v1_identical=True,
        rebuild={"pass": True, "differences": []},
    )
    base.update(over)
    return base


def test_human_gates_block_overall_pass():
    r = gates.build_gate_report(**_inputs())
    assert r["gates"]["G08-3"]["status"] == "PENDING_HUMAN"
    assert r["gates"]["G08-H"]["status"] == "PENDING_HUMAN"
    assert r["overall"] == "BLOCKED_PENDING_HUMAN"


def test_any_failed_machine_gate_is_fail():
    k = _inputs()["keys_counts"]
    k["gates"]["G08-2"] = {"pass": False}
    assert gates.build_gate_report(**_inputs(keys_counts=k))["overall"] == "FAIL"
    assert gates.build_gate_report(**_inputs(rebuild={"pass": False, "differences": ["keys"]}))["overall"] == "FAIL"
    assert gates.build_gate_report(**_inputs(seeded={"all_pass": False, "classes": {}}))["gates"]["G08-4"]["status"] == "FAIL"


def test_baseline_mutation_fails_g08_5():
    r = gates.build_gate_report(**_inputs(baseline_after={"EVD": "DIFFERENT"}))
    assert r["gates"]["G08-5"]["status"] == "FAIL"
    r = gates.build_gate_report(**_inputs(export_v1_identical=False))
    assert r["gates"]["G08-5"]["status"] == "FAIL"


def test_g08_7_forces_label_not_pass():
    g = gates.build_gate_report(**_inputs(largest_share=0.41))["gates"]["G08-7"]
    assert g["status"] == "LABEL_FORCED" and g["card_rule_exceeded"] is True


def test_compare_runs_and_manifest(tmp_path):
    for d in ("a", "b"):
        (tmp_path / d).mkdir()
        (tmp_path / d / "x").write_text("same")
        (tmp_path / d / "y").write_text("same")
    (tmp_path / "b" / "y").write_text("different")
    r = gates.compare_runs({n: tmp_path / "a" / n for n in "xy"}, {n: tmp_path / "b" / n for n in "xy"})
    assert r == {"pass": False, "differences": ["y"]}
    m = gates.freeze_manifest({"x": tmp_path / "a" / "x"})
    assert m["x"]["bytes"] == 4 and len(m["x"]["sha256"]) == 64
    json.dumps(m)
