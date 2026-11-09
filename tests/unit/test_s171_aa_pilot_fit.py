"""S171 / D-076 M3: AA pilot verdict rule + Model A fit (reports/step10/aa_pilot_preregistration_DRAFT.md §4, §6).

Synthetic rows only; no literature value here.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from culinarystate.simulation import aa_pilot_fit as F

R = 8.314462618


def _row(rid, paper, T, k, rtype="K_AT_T", order="first"):
    return {"row_id": rid, "candidate_id": paper, "row_type": rtype, "T_C": str(T), "value": repr(k),
            "order": order, "partition": "SIM-CAL", "verdict": "VERIFIED", "corrected_value": ""}


def _synthetic(ea=80_000.0, a=(-3.0, -3.6, -2.7), temps=(70, 80, 90, 95), noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    rows, i = [], 0
    for p, ai in enumerate(a):
        for T in temps:
            i += 1
            x = 1 / (T + 273.15) - 1 / F.T_REF_K
            rows.append(_row(f"R{i:03d}", f"P{p}", T, math.exp(ai - ea / R * x + rng.normal(0, noise))))
    return rows


def test_both_verified_or_same_correction_only():
    a = [_row("R1", "P", 80, 0.02), _row("R2", "P", 90, 0.04), _row("R3", "P", 95, 0.05), _row("R4", "P", 70, 0.01)]
    b = [dict(r) for r in a]
    b[1] = {**b[1], "verdict": "REJECTED"}
    a[2] = {**a[2], "verdict": "CORRECTED", "corrected_value": "0.06"}
    b[2] = {**b[2], "verdict": "CORRECTED", "corrected_value": "0.06"}
    b[3] = {**b[3], "verdict": "CORRECTED", "corrected_value": "0.011"}
    kept, why = F.agreed_rows(a, b)
    assert [r["row_id"] for r in kept] == ["R1", "R3"] and kept[1]["k"] == 0.06
    assert why == {"NOT_BOTH_VERIFIED": 1, "CORRECTIONS_DIFFER": 1}


def test_blank_verdict_or_mismatched_rows_refused():
    a = [_row("R1", "P", 80, 0.02)]
    with pytest.raises(F.FitRefused):
        F.agreed_rows(a, [{**a[0], "verdict": ""}])
    with pytest.raises(F.FitRefused):
        F.agreed_rows(a, [{**a[0], "row_id": "R9"}])


def test_inclusion_filter_temperature_type_order():
    rows = [{"row_id": "a", "candidate_id": "P", "row_type": "K_AT_T", "T": 55.0, "k": 0.01, "order": "first"},
            {"row_id": "b", "candidate_id": "P", "row_type": "K_AT_T", "T": 80.0, "k": 0.02, "order": "first"},
            {"row_id": "c", "candidate_id": "P", "row_type": "AUTHOR_FIT_EA", "T": None, "k": None, "order": "x"},
            {"row_id": "d", "candidate_id": "P", "row_type": "K_AT_T", "T": 90.0, "k": 0.03, "order": "second"}]
    inc, why = F.include(rows)
    assert [r["row_id"] for r in inc] == ["b"]
    assert why == {"BELOW_60C": 1, "NOT_K_AT_T": 1, "NOT_FIRST_ORDER": 1}


def test_model_a_recovers_shared_ea_and_intercepts_exactly_without_noise():
    rows, _ = F.agreed_rows(_synthetic(), _synthetic())
    fit = F.fit_model_a(rows)
    assert fit["Ea_J_per_mol"] == pytest.approx(80_000.0, rel=1e-9)
    assert [fit["intercepts"][p] for p in ("P0", "P1", "P2")] == pytest.approx([-3.0, -3.6, -2.7], abs=1e-9)
    assert fit["n_rows"] == 12 and fit["n_papers"] == 3 and fit["T_ref_K"] == F.T_REF_K


def test_model_a_refuses_unidentifiable_designs():
    one_paper = [r for r in _synthetic() if r["candidate_id"] == "P0"]
    rows, _ = F.agreed_rows(one_paper, one_paper)
    with pytest.raises(F.FitRefused):
        F.fit_model_a(rows)  # between-paper SD needs >= 2 papers
    flat = [r for r in _synthetic() if r["T_C"] == "80"]
    rows, _ = F.agreed_rows(flat, flat)
    with pytest.raises(F.FitRefused):
        F.fit_model_a(rows)  # one temperature: Ea not identifiable


def test_prediction_interval_widens_with_between_paper_spread_and_brackets_new_matrix():
    rows, _ = F.agreed_rows(_synthetic(noise=0.05, seed=1), _synthetic(noise=0.05, seed=1))
    fit = F.fit_model_a(rows)
    mid, lo, hi = F.predict_ln_k(fit, 90.0)
    assert lo < mid < hi
    assert mid == pytest.approx(np.mean([-3.0, -3.6, -2.7]), abs=0.15)
    assert lo < -3.6 and hi > -2.7  # an unseen matrix anywhere in the training spread is inside


def test_fit_is_deterministic_and_carries_its_inputs():
    rows, _ = F.agreed_rows(_synthetic(noise=0.05), _synthetic(noise=0.05))
    a, b = F.fit_model_a(rows), F.fit_model_a(rows)
    assert a == b and a["row_ids"] == sorted(r["row_id"] for r in rows)
    assert a["label"] == "PILOT_MODEL_ASSISTED" and a["model"] == "A_SHARED_EA_PAPER_INTERCEPTS"


def test_cli_freezes_once_and_reports_exclusions(tmp_path):
    import csv
    import importlib.util
    import json
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("aa_pilot_fit_tool",
                                                  Path(__file__).resolve().parents[2] / "tools/aa_pilot_fit.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    rows = _synthetic(noise=0.05) + [_row("R900", "P0", 30, 0.001)]
    paths = []
    for who in ("Kush", "Parv"):
        p = tmp_path / f"{who}.csv"
        with open(p, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        paths.append(p)
    out = tmp_path / "fit.json"
    argv = ["--kush", str(paths[0]), "--parv", str(paths[1]), "--out", str(out)]
    assert tool.main(argv) == 0
    rep = json.loads(out.read_text())
    assert rep["fit"]["n_rows"] == 12 and rep["excluded_by_inclusion"] == {"BELOW_60C": 1}
    assert rep["sim_val_opened"] is False and len(rep["returned_sha256"]["Kush"]) == 64
    with pytest.raises(SystemExit):
        tool.main(argv)
