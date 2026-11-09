"""S171 / D-075 M2: 07.A-R1 scorer (Gwet AC1 gate, reports/step07/07A_R1_preregistration_DRAFT.md). Synthetic only."""
from __future__ import annotations

import pytest

from culinarystate.evidence import condition_agreement as CA

FIELDS, CRITICAL = CA.FIELDS, CA.CRITICAL


def issued(n=100):
    return [{"audit_id": f"CA-{i:03d}", "condition_id": f"CONDZQX{i}", "stratum": "S1", "raw_duration": f"{i} ZQXSENTINEL",
             "normalizer_fingerprint_12": "e7d589136275", **{f: "" for f in FIELDS},
             "overall_judgement": "", "reason_if_not_correct": ""} for i in range(1, n + 1)]


def labelled(rows, overrides=None):
    out = []
    for r in rows:
        x = {**r, **{f: "CORRECT" for f in FIELDS}, "overall_judgement": "ACCEPT"}
        x.update((overrides or {}).get(r["audit_id"], {}))
        out.append(x)
    return out


def test_ac1_known_values():
    assert CA.gwet_ac1(["A"] * 10, ["A"] * 10, q=7) == 1.0
    assert CA.gwet_ac1(["x", "x", "y", "y"], ["x", "y", "x", "y"], q=2) == pytest.approx(0.0)
    a = ["CORRECT"] * 900
    b = ["CORRECT"] * 895 + ["SHOULD_BE_AMBIGUOUS"] * 5  # the v4 shape: kappa paradox
    assert CA.cohen_kappa(a, b) == pytest.approx(0.0)
    assert CA.gwet_ac1(a, b, q=7) == pytest.approx(0.99444, abs=1e-3)


def test_ac1_rejects_bad_q_and_lengths():
    with pytest.raises(ValueError):
        CA.gwet_ac1(["A"], ["A"], q=1)
    with pytest.raises(ValueError):
        CA.gwet_ac1(["A"], ["A", "B"], q=2)


def test_high_agreement_passes_with_kappa_diagnostic_only():
    rows = issued()
    a = labelled(rows)
    b = labelled(rows, {"CA-001": {"duration_judgement": "SHOULD_BE_AMBIGUOUS"}})
    out = CA.score(rows, a, b)
    assert out["gate"] == "PASS" and out["pooled_ac1"] > 0.99
    assert out["diagnostics"]["pooled_kappa"] == pytest.approx(0.0)
    assert out["critical_field_flags"] == []


def test_repeated_critical_pair_flags_even_when_pooled_passes():
    rows = issued()
    a = labelled(rows)
    b = labelled(rows, {f"CA-00{i}": {"basis_judgement": "INFERRED"} for i in range(1, 4)})
    out = CA.score(rows, a, b)
    assert out["pooled_ac1"] >= 0.80 and out["gate"] == "FAIL_OR_ADJUDICATE"
    assert any(f.startswith("basis_judgement") for f in out["critical_field_flags"])


def test_low_agreement_fails():
    rows = issued()
    codes = sorted(CA.CODES)
    a = labelled(rows, {r["audit_id"]: {f: codes[(i + j) % 7] for j, f in enumerate(FIELDS)}
                        for i, r in enumerate(rows)})
    b = labelled(rows, {r["audit_id"]: {f: codes[(i + 2 * j + 1) % 7] for j, f in enumerate(FIELDS)}
                        for i, r in enumerate(rows)})
    out = CA.score(rows, a, b)
    assert out["gate"] == "FAIL_OR_ADJUDICATE" and out["pooled_ac1"] < 0.80


def test_identical_files_are_not_counted():
    rows = issued()
    out = CA.score(rows, labelled(rows), labelled(rows))
    assert out["gate"] == "NOT_COUNTED" and "IDENTICAL_JUDGEMENTS" in out["problems"]


def test_edited_non_judgement_column_is_not_counted():
    rows = issued()
    b = labelled(rows)
    b[5] = {**b[5], "raw_duration": "edited"}
    b[0] = {**b[0], "duration_judgement": "INFERRED"}
    out = CA.score(rows, labelled(rows), b)
    assert out["gate"] == "NOT_COUNTED" and any("B:CA-006" in p for p in out["problems"])


def test_blank_or_invalid_codes_are_invalid_input():
    rows = issued()
    b = labelled(rows)
    b[2] = {**b[2], "pressure_judgement": ""}
    out = CA.score(rows, labelled(rows), b)
    assert out["gate"] == "INVALID_INPUT"
    b = labelled(rows)
    b[2] = {**b[2], "overall_judgement": "CORRECT"}
    assert CA.score(rows, labelled(rows), b)["gate"] == "INVALID_INPUT"


def test_missing_rows_and_fingerprint_mismatch_are_invalid_input():
    rows = issued()
    assert CA.score(rows, labelled(rows), labelled(rows)[:-1])["gate"] == "INVALID_INPUT"
    b = labelled(rows)
    b[0] = {**b[0], "normalizer_fingerprint_12": "000000000000", "duration_judgement": "INFERRED"}
    assert CA.score(rows, labelled(rows), b)["gate"] in ("INVALID_INPUT", "NOT_COUNTED")


def test_bootstrap_interval_is_deterministic_and_brackets_point():
    rows = issued()
    a = labelled(rows)
    b = labelled(rows, {f"CA-0{i:02d}": {"duration_judgement": "INFERRED"} for i in range(10, 30)})
    o1, o2 = CA.score(rows, a, b), CA.score(rows, a, b)
    lo, hi = o1["diagnostics"]["pooled_ac1_bootstrap95"]
    assert o1 == o2 and lo <= o1["pooled_ac1"] <= hi


def test_output_carries_no_condition_ids_or_raw_text():
    rows = issued()
    a = labelled(rows)
    b = labelled(rows, {"CA-001": {"duration_judgement": "INFERRED"}})
    text = repr(CA.score(rows, a, b))
    assert "CONDZQX" not in text and "ZQXSENTINEL" not in text
