"""Synthetic-only checks for separate, post-freeze CAL sensitivity diagnostics."""
from copy import deepcopy
import math
from pathlib import Path
import runpy

import pytest

from culinarystate.simulation.aa_cal_sensitivity import fit_paper, model_b, sensitivity_report


def rows(paper="SYN-A", ea=60000.0, intercept=-3.0, noise=(.03, -.02, .01, -.02)):
    return [{"row_id": f"{paper}-{j}", "candidate_id": paper, "T": temp,
             "k": math.exp(intercept - ea / 8.314462618 * (1 / (temp + 273.15) - 1 / 363.15) + e)}
            for j, (temp, e) in enumerate(zip((65., 75., 85., 95.), noise))]


def test_per_paper_fit_matches_independent_ols_and_does_not_mutate():
    import numpy as np
    a = rows()
    before = deepcopy(a)
    res = fit_paper(a)
    x = np.array([[-(1 / (r["T"] + 273.15) - 1 / 363.15) / 8.314462618, 1.] for r in a])
    beta = np.linalg.lstsq(x, np.log([r["k"] for r in a]), rcond=None)[0]
    assert res["Ea_J_per_mol"] == pytest.approx(beta[0])
    assert res["ln_k_ref"] == pytest.approx(beta[1])
    assert res["dof"] == 2 and res["Ea_se"] > 0
    assert a == before


def test_separate_paper_slopes_stay_separate():
    a, b = rows(), rows("SYN-B", 90000.)
    res = model_b(a + b)
    assert set(res) == {"SYN-A", "SYN-B"}
    assert res["SYN-B"]["Ea_J_per_mol"] - res["SYN-A"]["Ea_J_per_mol"] == pytest.approx(30000.)


def test_three_distinct_temperatures_are_required():
    a = rows()[:2]
    a.append({**a[0], "row_id": "SYN-A-repeat"})
    assert fit_paper(a)["status"] == "NEED_DATA"


def test_exact_fit_does_not_report_zero_uncertainty():
    res = fit_paper(rows(noise=(0., 0., 0., 0.)))
    assert res["status"] == "NEED_DATA_FOR_UNCERTAINTY"
    assert res["Ea_se"] is None and res["ln_k_ref_se"] is None


@pytest.mark.parametrize("field,value", [("T", math.nan), ("T", -273.15), ("k", math.inf),
                                         ("k", 0), ("T", True)])
def test_invalid_numeric_inputs_refused(field, value):
    a = rows()
    a[0][field] = value
    with pytest.raises(ValueError):
        fit_paper(a)


def test_duplicate_ids_and_mixed_papers_refused():
    a = rows()
    with pytest.raises(ValueError):
        fit_paper(a + [a[0]])
    with pytest.raises(ValueError):
        fit_paper(a + rows("SYN-B"))


def test_sensitivities_never_reintroduce_rejected_papers():
    accepted = rows() + rows("SYN-B", 90000.)
    meta = {"SYN-A": {"water_contact": "NO", "aa_specific": True},
            "SYN-B": {"water_contact": "UNKNOWN", "aa_specific": False}}
    before = deepcopy(accepted)
    res = sensitivity_report(accepted, meta, rejected_papers=["SYN-REJECTED"])
    assert res["all_rows_including_rejected"]["status"] == "NOT_RUN_LICENCE_REJECTED"
    assert res["without_non_aa_specific"]["status"] == "NEED_DATA"
    assert res["without_water_contact"]["unknown_water_contact_papers"] == ["SYN-B"]
    assert res["without_water_contact"]["same_rows_as_primary"] is True
    assert accepted == before


def test_all_admissible_temperatures_arm_includes_cold_rows_without_mutating_primary():
    a = rows() + rows("SYN-B", 90000.)
    a.append({"row_id": "SYN-COLD", "candidate_id": "SYN-A", "T": 45., "k": .001})
    meta = {p: {"water_contact": "NO", "aa_specific": True} for p in ("SYN-A", "SYN-B")}
    res = sensitivity_report(a, meta, rejected_papers=[])
    assert res["primary_included_rows"] == 8
    assert res["all_admissible_temperatures"]["n_rows"] == 9
    assert res["all_admissible_temperatures"]["added_below_60C"] == 1


def test_unchanged_primary_rows_are_not_refitted(monkeypatch):
    from culinarystate.simulation import aa_cal_sensitivity as M
    def refuse(*args, **kwargs):
        raise AssertionError("the unchanged primary must not be refitted")
    monkeypatch.setattr(M.frozen, "fit_model_a", refuse)
    a = rows() + rows("SYN-B")
    meta = {p: {"water_contact": "NO", "aa_specific": True} for p in ("SYN-A", "SYN-B")}
    out = sensitivity_report(a, meta, rejected_papers=[])
    assert out["all_admissible_temperatures"]["status"] == "SAME_ROWS_AS_PRIMARY_NO_REFIT"


def test_tool_refuses_existing_output_before_reading_inputs(tmp_path):
    tool = runpy.run_path(str(Path(__file__).resolve().parents[2] / "tools/s179_aa_cal_sensitivity.py"))
    out = tmp_path / "keep.json"
    out.write_text("unchanged")
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        tool["main"](["--cal", "missing.csv", "--metadata", "missing.json", "--out", str(out)])
    assert out.read_text() == "unchanged"
