"""08a.6 component-feasibility (G08-7; THR-08A-08/09/15/20). Synthetic data only."""
import importlib.util
import json
import random
from pathlib import Path

import pytest

from culinarystate.lineage import feasibility as fz

REPO = Path(__file__).resolve().parents[2]


def mk(i, grp, fam="PE", res="PUBLICATION_ONLY", tf="CHEMICAL", an="A1", mx="veg", pr="boil", tier="E3", ver="UNVERIFIED"):
    return {"evd_id": f"EVD-{i:06d}", "source_family": fam, "target_family": tf, "analyte": an, "matrix_family": mx,
            "process_family": pr, "split_group_id": f"G{grp}", "independence_resolution": res, "tier": tier,
            "verification_status": ver}


def test_kish_formula():
    assert fz.kish_neff([5, 5]) == pytest.approx(2.0)
    assert fz.kish_neff([1] * 10) == pytest.approx(10.0)
    assert fz.kish_neff([90, 10]) == pytest.approx(100 ** 2 / (8100 + 100))
    assert fz.kish_neff([]) is None


def test_giant_stats_and_forty_percent_is_strict():
    s = fz.giant_stats({"a": 40, "b": 60})
    assert s["largest_share"] == 0.6 and s["groups"] == 2 and s["rows"] == 100
    assert fz.exceeds_share({"a": 40, "b": 60}) is True
    assert fz.exceeds_share({"a": 40, "b": 30, "c": 30}) is False  # exactly 0.40 does not exceed
    assert fz.exceeds_share({}) is None


def test_refined_pass_needs_neff_and_share():
    rows = [mk(i, i % 12) for i in range(120)]  # 12 equal groups: n_eff 12, share 1/12
    ev = fz.evaluate_family(rows)
    assert ev["A_tier_only"]["refined_pass"] is True
    assert ev["A_tier_only"]["label"] == "publication-component CV"  # no STUDY rows: never study-disjoint (L-06)
    rows = [mk(i, i % 5) for i in range(50)]  # 5 groups: n_eff 5 < 10
    assert fz.evaluate_family(rows)["A_tier_only"]["refined_pass"] is False


def test_study_disjoint_only_when_all_pool_rows_study_and_both_rules_pass():
    rows = [mk(i, i % 12, res="STUDY") for i in range(120)]
    assert fz.evaluate_family(rows)["A_tier_only"]["label"] == "study-disjoint"
    rows[0] = mk(0, 0, res="PUBLICATION_ONLY")
    assert fz.evaluate_family(rows)["A_tier_only"]["label"] == "publication-component CV"


def test_card_rule_on_all_rows_forces_weaker_label_with_fallback_pair():
    big = [mk(i, 0, fam="USDA", res="SOURCE_FAMILY_ONLY") for i in range(500)]
    pe = [mk(1000 + i, 1 + i % 12) for i in range(120)]
    ev = fz.evaluate_family(big + pe)["A_tier_only"]
    assert ev["card_exceeds"] is True and ev["refined_pass"] is True
    assert ev["label"] == "publication-component CV"
    assert ev["fallback_pair"] == ["publication-component CV", "leave-one-source-family-out"]


def test_empty_pool_gives_source_family_label_and_unknown_refinement():
    rows = [mk(i, i, fam="USDA", res="SOURCE_FAMILY_ONLY") for i in range(30)]
    ev = fz.evaluate_family(rows)["A_tier_only"]
    assert ev["pool_rows"] == 0 and ev["n_eff"] is None and ev["refined_pass"] is None
    assert ev["label"] == "leave-one-source-family-out"


def test_strict_reading_requires_human_verified_and_empties_pool():
    rows = [mk(i, i % 12) for i in range(120)]
    ev = fz.evaluate_family(rows)
    assert ev["B_tier_and_human_verified"]["pool_rows"] == 0
    rows = [mk(i, i % 12, ver="HUMAN_VERIFIED") for i in range(120)]
    assert fz.evaluate_family(rows)["B_tier_and_human_verified"]["pool_rows"] == 120


def test_tier_exclusion_per_l08():
    rows = [mk(i, i % 12, tier="E5") for i in range(60)] + [mk(100 + i, i % 12) for i in range(60)]
    assert fz.evaluate_family(rows)["A_tier_only"]["pool_rows"] == 60


def test_unknown_resolution_never_in_pool():
    rows = [mk(i, i % 12, res="UNKNOWN") for i in range(60)]
    assert fz.evaluate_family(rows)["A_tier_only"]["pool_rows"] == 0


def test_losfo_structural_and_cross_family_group():
    rows = [mk(1, 1, fam="X"), mk(2, 2, fam="X"), mk(3, 3, fam="Y"), mk(4, 3, fam="Z")]
    out = fz.losfo_feasibility(rows)
    assert out["groups_spanning_families"] == 1
    assert out["structurally_feasible"] is False
    ok = fz.losfo_feasibility([mk(1, 1, fam="X"), mk(2, 2, fam="Y")])
    assert ok["structurally_feasible"] is True
    assert ok["per_family"]["X"]["heldout_rows"] == 1 and ok["per_family"]["X"]["remaining_rows"] == 1
    assert ok["per_family"]["X"]["remaining_groups"] == 1
    assert fz.losfo_feasibility([mk(1, 1, fam="X")])["structurally_feasible"] is False


def test_cell_survival_k5():
    rows = [mk(i, i, an="A", mx="m", pr="p") for i in range(5)] + [mk(10 + i, i % 4, an="B", mx="m", pr="p") for i in range(8)]
    out = fz.cell_survival(rows, k=5)
    assert out["cells"] == 2 and out["cells_with_ge_k_groups"] == 1
    assert out["surviving_rows"] == 5 and out["k"] == 5


def test_cell_survival_pool_only_option():
    rows = [mk(i, i, res="SOURCE_FAMILY_ONLY") for i in range(6)]
    assert fz.cell_survival(rows, k=5)["cells_with_ge_k_groups"] == 1
    assert fz.cell_survival(rows, k=5, pool_only=True)["cells_with_ge_k_groups"] == 0


def test_build_report_deterministic_under_shuffle():
    rows = [mk(i, i % 7, fam=("A", "B")[i % 2], an=f"AN{i % 3}") for i in range(80)]
    a = json.dumps(fz.build_report(rows), sort_keys=True)
    sh = rows[:]
    random.Random(3).shuffle(sh)
    assert json.dumps(fz.build_report(sh), sort_keys=True) == a


def test_build_report_has_required_sections_and_unknowns():
    rep = fz.build_report([mk(i, i % 12) for i in range(60)])
    for k in ("overall", "by_target_family", "by_source_family", "losfo", "cells_k5", "label_verdict",
              "unknowns", "lab_disjoint", "formulas"):
        assert k in rep
    assert rep["lab_disjoint"] == "NEED_DATA"
    assert any("TEST-eligible" in u for u in rep["unknowns"])


def test_join_rows_maps_fields_and_rejects_missing_keys():
    evd = [{"id": "EVD-000001", "source_family_id": "F", "tier": "E3", "verification": {"status": "UNVERIFIED"},
            "target": {"state_variable_id": "SVAR-1", "raw_name": "x"}, "matrix": {"food_group": "veg"},
            "process": {"steps": ["boil", "drain"]}}]
    keys = [{"evd_id": "EVD-000001", "split_group_id": "S1", "independence_resolution": "UNKNOWN"}]
    svar = {"SVAR-1": {"canonical_name": "Cal", "family": "CHEMICAL"}}
    r = fz.join_rows(evd, keys, svar)[0]
    assert (r["analyte"], r["target_family"], r["matrix_family"], r["process_family"]) == ("Cal", "CHEMICAL", "veg", "boil+drain")
    with pytest.raises(ValueError):
        fz.join_rows(evd, [], svar)


def _tool():
    spec = importlib.util.spec_from_file_location("step08a_feasibility", REPO / "tools" / "step08a_feasibility.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_tool_refuses_repo_output(tmp_path):
    t = _tool()
    with pytest.raises(t.RefusedPathError):
        t._check_out(REPO / "reports" / "x", REPO, t.ALLOWED_OUT_ROOT)


def test_tool_run_end_to_end_deterministic(tmp_path):
    t = _tool()
    root = tmp_path / "scratch_root"
    (root / "data").mkdir(parents=True)
    evd = [{"id": f"EVD-{i:06d}", "version": 1, "status": "ACTIVE", "source_family_id": "AB"[i % 2], "tier": "E3",
            "verification": {"status": "UNVERIFIED"}, "target": {"state_variable_id": "SVAR-1", "raw_name": "x"},
            "matrix": {"food_group": "veg"}, "process": {"steps": ["boil"]}} for i in range(1, 25)]
    (root / "data" / "EVD.jsonl").write_text("\n".join(json.dumps(e) for e in evd) + "\n")
    (root / "data" / "SVAR.jsonl").write_text(json.dumps({"id": "SVAR-1", "version": 1, "canonical_name": "Cal", "family": "CHEMICAL"}) + "\n")
    keys = tmp_path / "keys.jsonl"
    keys.write_text("\n".join(json.dumps({"evd_id": e["id"], "split_group_id": f"S{int(e['id'][4:]) % 6}",
                                          "independence_resolution": "PUBLICATION_ONLY"}) for e in evd) + "\n")
    out = tmp_path / "out"
    r1 = t.run(root, keys, out, repo_root=REPO, allowed=tmp_path)
    b1 = (out / "feasibility.json").read_bytes()
    t.run(root, keys, out, repo_root=REPO, allowed=tmp_path)
    assert (out / "feasibility.json").read_bytes() == b1
    assert r1["rows"] == 24 and (out / "feasibility_report.txt").read_text().startswith("08a.6")
