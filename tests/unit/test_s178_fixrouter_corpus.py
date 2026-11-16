"""S178 FIX-ROUTER: SCI-B CORP-2 (inverted ranges after pre-normalisation) and CORP-3 (``pair_lines`` keeps the status).

Synthetic strings only (invented foods); no corpus text. Both scenario tests FAIL on the pre-fix code (fc4c004).
"""
from __future__ import annotations

import pytest

from culinarystate.quantity import foodcom_pairing as FP
from culinarystate.quantity import prenormalize as P
from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.parse_adapter import parse_quantity_v2
from culinarystate.quantity.rc2_dryrun import LOCALE_META, SOURCE_META, load_schema
from culinarystate.quantity.rc2_grounding import GroundingContext, ground_quantity_rc2

META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT", "evidence_refs": ["synthetic:prenorm"]}
SCHEMA = load_schema()
CTX = GroundingContext(source_metadata=SOURCE_META, locale="US", locale_metadata=LOCALE_META)
INVERTED = ["1-½ cups synthetic", "1–1/2 cups synthetic", "2 - 1/2 cups synthetic", "1 - 1/2 cups synthetic",
            "3-2 cups synthetic", "1 -½ cup synthetic"]


# ------------------------------------------------------------------ CORP-2
@pytest.mark.parametrize("raw", INVERTED)
def test_corp2_inverted_range_is_unknown_with_a_flag_at_every_opt_in_entry_point(raw):
    frozen = parse_line(raw)
    assert frozen.kind == "RANGE" and frozen.low > frozen.high                    # the frozen defect is still there
    p = P.parse_line_prenorm(raw)
    assert p.kind == "NONE" and p.flags == (P.INVERTED_FLAG,) and p.raw == raw and p.low is None and p.high is None
    v = P.parse_quantity_v2_prenorm(raw, source_metadata=META)
    assert v.ast["node_type"] == "UNKNOWN" and P.INVERTED_FLAG in v.flags and v.raw == raw
    assert v.arithmetic.status not in {"KNOWN", "RANGE"} and v.rule_version.endswith("+" + P.PRENORM_VERSION)
    g = P.ground_quantity_rc2_prenorm(raw, CTX, schema=SCHEMA)
    assert g.arithmetic_status == "UNKNOWN" and P.INVERTED_FLAG in g.flags and g.record["raw"] == raw
    assert g.pipeline_version.endswith("+" + P.PRENORM_VERSION)


@pytest.mark.parametrize("raw", ["1-2 cups synthetic", "1/2-3/4 cup synthetic", "0-1/2 tsp synthetic", "2 – 3 cups synthetic",
                                 "1-3/2 cups synthetic", "1-1/2 cups synthetic"])
def test_corp2_forward_ranges_and_mixed_numbers_are_not_flagged(raw):
    p = P.parse_line_prenorm(raw)
    assert P.INVERTED_FLAG not in p.flags and p.kind != "NONE"
    assert P.INVERTED_FLAG not in P.parse_quantity_v2_prenorm(raw, source_metadata=META).flags


def test_corp2_rule_can_be_switched_off_and_is_in_the_default_set():
    assert P.RULE_INVERTED in P.DEFAULT_RULES and P.RULE_INVERTED in P.RULE_IDS
    rules = tuple(r for r in P.DEFAULT_RULES if r != P.RULE_INVERTED)
    assert P.parse_line_prenorm("1-½ cups synthetic", rules=rules) == parse_line("1-½ cups synthetic")
    a = P.parse_quantity_v2_prenorm("2 - 1/2 cups synthetic", source_metadata=META, rules=rules)
    assert repr(a) == repr(parse_quantity_v2("2 - 1/2 cups synthetic", source_metadata=META))
    assert P.prenormalise("1-½ cups synthetic").changed is False                # the text itself is never rewritten


def test_corp2_unaffected_grounding_is_byte_identical():
    for raw in ("1 cup synthetic", "1-2 cups synthetic", "2 x 400g cans synthetic"):
        a, b = P.ground_quantity_rc2_prenorm(raw, CTX, schema=SCHEMA), ground_quantity_rc2(raw, CTX, schema=SCHEMA)
        assert a.pipeline_version == b.pipeline_version and a.record == b.record and a.flags == b.flags


# ------------------------------------------------------------------ CORP-3
def test_corp3_pair_lines_keeps_the_length_mismatch_status():
    out = FP.pair_lines(["1", "2", "3"], ["synthfruit", "quibbleroot"])
    assert out == ["synthfruit", "quibbleroot"]                                     # still a drop-in list of lines
    assert out.length_mismatch is True and out.statuses == (FP.STATUS_UNKNOWN, FP.STATUS_UNKNOWN)
    assert out.with_status() == [("synthfruit", FP.STATUS_UNKNOWN), ("quibbleroot", FP.STATUS_UNKNOWN)]
    eq = FP.pair_lines(["1", None], ["synthfruit", "quibbleroot"])
    assert eq == ["1 synthfruit", "quibbleroot"] and eq.length_mismatch is False
    assert eq.statuses == (FP.STATUS_PAIRED, FP.STATUS_PAIRED)                     # null quantity: the source says nothing
    pos = FP.pair_lines(["1"], ["a", "b"], "POSITIONAL")
    assert pos.statuses == ("POSITIONAL", "POSITIONAL") and pos.length_mismatch is True and pos.rule == "POSITIONAL"
    assert FP.pair_lines_with_status(["1", "2"], ["a"]) == [("a", FP.STATUS_UNKNOWN)]
    with pytest.raises(ValueError):
        FP.PairedLines(["a"], [], length_mismatch=False, rule="X")
