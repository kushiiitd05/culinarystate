"""Number listing cannot silently grant scientific claim approval."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("number_lint", Path(__file__).parents[2] / "tools/s179_number_class_lint.py")
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)


def test_lists_signed_decimal_fraction_percent_and_metadata_without_dropping_any():
    out = lint.inspect_text("DIAGNOSTIC\nValues -1.5, 1e-5, 95%, 2/9 and EVD-000001.")
    assert [r["token"] for r in out["numbers"]] == ["-1.5", "1e-5", "95%", "2/9", "000001"]
    assert out["numbers"][-1]["class"] == "IDENTIFIER_METADATA"
    assert all(r["class"] == "DIAGNOSTIC/PRIOR_EXPOSURE" for r in out["numbers"][:-1])


def test_unknown_numbers_are_visible_review_gaps():
    out = lint.inspect_text("The value is 42.")
    assert out["numbers"][0]["class"] == "UNCLASSIFIED_REVIEW_REQUIRED"
    assert out["unclassified"] == 1


def test_positive_claim_requires_a_real_supplied_passed_gate():
    assert len(lint.inspect_text("The model is validated [G15].")["claim_flags"]) == 1
    assert len(lint.inspect_text("The model is validated [G15].", passed_gates={"G15"})["claim_flags"]) == 0
    assert lint.inspect_text("NOT_VALIDATED / uncalibrated; no validated simulator.")["claim_flags"] == []


def test_nearby_result_does_not_inherit_class_from_a_distant_section():
    out = lint.inspect_text("## DIAGNOSTIC\n\n- Count 4.\n\n## New section\n\nValue 7.")
    assert out["numbers"][0]["class"] == "DIAGNOSTIC/PRIOR_EXPOSURE"
    assert out["numbers"][-1]["class"] == "UNCLASSIFIED_REVIEW_REQUIRED"


def test_review_is_bound_to_exact_line_and_numeric_position():
    import hashlib
    text = "The value is 42."
    out = lint.inspect_text(text)
    entry = {"line": 1, "column": 14, "token": "42", "class": "DIAGNOSTIC/PRIOR_EXPOSURE",
             "line_sha256": hashlib.sha256(text.encode()).hexdigest(), "reason": "AI review of the diagnostic section"}
    revised = lint.apply_review(out, text, [entry])
    assert revised["unclassified"] == 0
    import pytest
    with pytest.raises(ValueError):
        lint.apply_review(lint.inspect_text(text), text + " changed", [entry])
