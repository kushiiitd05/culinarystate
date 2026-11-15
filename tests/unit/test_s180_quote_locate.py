"""S180 amendment A5: prompt v3 asks for a quote; the runner locates it deterministically.

v1/v2 asked the model for integer character offsets. The 72B arm showed the consequence: 13 of 16
values named a choice that genuinely exists in the text, and **0 of 16 spans pointed at it**. The
models read correctly and then guess the location, because nothing makes a language model compute an
offset.

v3 removes the offset from the model's job. It returns the licensing substring; ``locate_quote``
finds it. A quote that is not present is a refusal - no fuzzy matching and no nearest-match
fallback, since inventing a location would reintroduce exactly the defect this removes.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import s180_run_layer1_arms as R  # noqa: E402

RAW = "Add the lemon juice or the vinegar,\nthen simmer for 20 minutes or until thick."


def test_exact_quote_is_located():
    assert R.locate_quote(RAW, "lemon juice or the vinegar") == (8, 34)


def test_located_span_round_trips_to_the_quote():
    q = "lemon juice or the vinegar"
    a, b = R.locate_quote(RAW, q)
    assert RAW[a:b] == q


def test_absent_quote_is_refused_not_approximated():
    assert R.locate_quote(RAW, "lemon juice or the balsamic") is None
    assert R.locate_quote(RAW, "") is None


def test_whitespace_runs_are_collapsed_but_nothing_else_is():
    """A model re-wrapping a newline as a space must not cost a true match."""
    assert R.locate_quote(RAW, "the vinegar, then simmer") is not None
    assert R.locate_quote(RAW, "the  vinegar,   then simmer") is not None


def test_case_and_punctuation_are_not_normalised_away():
    assert R.locate_quote(RAW, "LEMON JUICE OR THE VINEGAR") is None
    assert R.locate_quote(RAW, "lemon juice or the vinegar!") is None


def test_a_located_quote_still_has_to_pass_the_gate():
    """v3 cannot manufacture an acceptance: grounding is applied to the located span as always."""
    from culinarystate.composition import layer1_proposer as LP
    a, b = R.locate_quote(RAW, "then simmer for 20 minutes")
    assert not LP.span_grounds_value(RAW, a, b), "no coordinator, so it must still fail"
    a, b = R.locate_quote(RAW, "lemon juice or the vinegar")
    assert LP.span_grounds_value(RAW, a, b)


def test_endpoint_quote_is_located_but_not_grounded():
    from culinarystate.composition import layer1_proposer as LP
    a, b = R.locate_quote(RAW, "simmer for 20 minutes or until thick")
    assert (a, b) != (None, None)
    assert not LP.span_grounds_value(RAW, a, b), "'or until' is an endpoint, not a branch"


def test_v3_prompt_asks_for_a_quote_and_never_for_offsets():
    case = {"raw": RAW, "triggers": ["VNEXT_ALTERNATIVE_SKIPPED"]}
    p = R.build_prompt(case, "E1, E2", version="v3")
    assert '"quote"' in p
    assert "span_start" not in p and "span_end" not in p
    assert "offset" not in p.lower()


def test_v1_prompt_is_unchanged_and_still_asks_for_offsets():
    """v1 and v2 results are kept and reported beside v3, so their prompts must not move."""
    case = {"raw": RAW, "triggers": ["VNEXT_ALTERNATIVE_SKIPPED"]}
    p = R.build_prompt(case, "E1", version="v1")
    assert "span_start" in p and "quote" not in p
