"""Synthetic controls; the legacy parser/normaliser and recipe base stay untouched."""
import copy
from fractions import Fraction

import pytest

from culinarystate.quantity.grammar import QuantityParse, parse_line
from culinarystate.quantity.parse_adapter import parse_quantity_v2
from culinarystate.quantity.versioned_normalizer import normalize_v2

META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
        "evidence_refs": ["synthetic:pipeline"]}


@pytest.mark.parametrize("unit,channel", [("g", "mass_g"), ("ml", "volume_ml")])
def test_explicit_zero_packages_are_zero_not_one(unit, channel):
    p = parse_line(f"0 x 400{unit} cans synthetic ingredient")
    before = copy.deepcopy(p)
    result = normalize_v2(p)
    assert getattr(result, channel)["value"] == 0
    assert result.count["value"] == 0 and result.rule_version == "CQPO_NORMALIZE_V2"
    assert p == before


def test_normal_quantity_stays_source_stated_and_no_density_is_assumed():
    assert normalize_v2(parse_line("2 x 400g cans synthetic ingredient")).mass_g["value"] == 800
    cup = normalize_v2(parse_line("1 cup synthetic ingredient"), locale="US")
    assert cup.mass_g["status"] == "UNKNOWN" and cup.q_level == "Q6"


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf")])
def test_invalid_constructed_parse_is_masked_and_flagged(bad):
    p = QuantityParse("synthetic invalid", "NUMBER", value=bad, unit_key="g")
    result = normalize_v2(p)
    assert result.mass_g["status"] == "UNKNOWN" and "INVALID_NUMERIC_INPUT" in result.flags


def test_exact_fraction_bridge_and_raw_preservation():
    raw = "1/3 g synthetic ingredient"
    result = parse_quantity_v2(raw, source_metadata=META)
    assert result.raw == raw and result.parsed.raw == raw
    assert result.arithmetic.low == Fraction(1, 3)
    assert "NORMALIZATION_FLOAT_PRECISION_LIMIT" in result.flags


@pytest.mark.parametrize("count,expected", [(0, 0), (2, 800)])
def test_package_bridge_uses_explicit_operands(count, expected):
    result = parse_quantity_v2(f"{count} x 400g cans synthetic ingredient", source_metadata=META)
    assert result.ast["node_type"] == "PACKAGE_CONTENT" and result.arithmetic.low == expected


def test_or_choices_are_not_replaced_by_a_continuous_range():
    result = parse_quantity_v2("1 or 2g synthetic ingredient", source_metadata=META)
    assert result.arithmetic.status == "ALTERNATIVE"
    assert [x.low for x in result.arithmetic.alternatives] == [1, 2]


def test_cross_unit_or_is_not_silently_reduced_to_the_first_branch():
    result = parse_quantity_v2("500g or 1 cup synthetic ingredient", source_metadata=META)
    assert result.arithmetic.status == "UNKNOWN" and "UNRESOLVED_ALTERNATIVE" in result.flags


def test_range_preserved_without_a_midpoint():
    result = parse_quantity_v2("1-2g synthetic ingredient", source_metadata=META)
    assert (result.arithmetic.low, result.arithmetic.high) == (1, 2)


def test_nonterminating_range_bound_is_not_rounded_into_exact_ast():
    result = parse_quantity_v2("1/3-2/3g synthetic ingredient", source_metadata=META)
    assert result.arithmetic.status == "UNKNOWN" and "NONTERMINATING_RANGE_BOUND" in result.flags


def test_qualitative_and_unstated_never_gain_numeric_amounts():
    q = parse_quantity_v2("a pinch synthetic ingredient", source_metadata=META)
    assert q.arithmetic.low is None and q.arithmetic.status == "QUALITATIVE"
    u = parse_quantity_v2("synthetic ingredient as desired", source_metadata=META)
    assert u.arithmetic.low is None and u.arithmetic.status == "UNKNOWN"


def test_dual_expressions_and_part_yields_are_visible_as_unsupported():
    for raw, flag in [("100g/4oz synthetic ingredient", "UNSUPPORTED_DUAL_EXPRESSION"),
                      ("juice of 1 synthetic lemon", "PART_AMOUNT_UNGROUNDED")]:
        result = parse_quantity_v2(raw, source_metadata=META)
        assert flag in result.flags and result.arithmetic.status == "UNKNOWN"


def test_metadata_is_required_and_never_changed():
    before = copy.deepcopy(META)
    parse_quantity_v2("1g synthetic ingredient", source_metadata=META)
    assert META == before
    with pytest.raises(TypeError):
        parse_quantity_v2("1g synthetic ingredient")


def test_length_modifier_is_not_a_count_and_word_half_is_preserved():
    size = parse_quantity_v2("5cm piece synthetic ingredient", source_metadata=META)
    assert size.arithmetic.status == "UNKNOWN" and "SIZE_IS_NOT_QUANTITY" in size.flags
    half = parse_quantity_v2("a half cup synthetic ingredient", source_metadata=META)
    assert half.arithmetic.low == Fraction(1, 2)


@pytest.mark.parametrize("raw", ["2.5 x 400g cans synthetic ingredient", "1/2 x 400g cans synthetic ingredient",
    "2×400g cans synthetic ingredient", "1 or 2 or 3g synthetic ingredient",
    "1g plus 2g synthetic ingredient", "1g + 2g synthetic ingredient", "1g and 2g synthetic ingredient"])
def test_unsupported_operations_cannot_silently_drop_an_operand(raw):
    result = parse_quantity_v2(raw, source_metadata=META)
    assert result.arithmetic.status == "UNKNOWN" and result.requires_review


@pytest.mark.parametrize("raw", ["0.0000001g synthetic ingredient", "2 x 1/3g cans synthetic ingredient"])
def test_compatibility_normalisation_precision_is_disclosed(raw):
    result = parse_quantity_v2(raw, source_metadata=META)
    assert "NORMALIZATION_FLOAT_PRECISION_LIMIT" in result.flags


def test_long_decimal_range_is_not_rounded_into_an_exact_ast():
    result = parse_quantity_v2("0.123456789123456789-0.223456789123456789g synthetic ingredient", source_metadata=META)
    assert result.arithmetic.status == "UNKNOWN" and "BOUND_FLOAT_PRECISION_LIMIT" in result.flags


@pytest.mark.parametrize("p,flag", [
    (QuantityParse("synthetic", "NUMBER", value=2, unit_key="g", alt=(3, "not_a_unit")), "UNKNOWN_UNIT_KEY"),
    (QuantityParse("synthetic", "NUMBER", value=2, unit_key="g", alt=(float("nan"), "g")), "INVALID_NUMERIC_INPUT"),
    (QuantityParse("synthetic", "NUMBER", value=2, unit_key="not_a_unit"), "UNKNOWN_UNIT_KEY"),
    (QuantityParse("synthetic", "NUMBER", value=1e308, unit_key="kg"), "NONFINITE_NORMALIZATION"),
])
def test_invalid_units_alt_values_and_derived_overflow_are_masked(p, flag):
    result = normalize_v2(p)
    assert result.mass_g["status"] == "UNKNOWN" and flag in result.flags


def test_suffix_approximation_is_not_treated_as_an_exact_measurement():
    result = parse_quantity_v2("1g approximately synthetic ingredient", source_metadata=META)
    assert result.requires_review and "APPROXIMATE_SOURCE_AMOUNT" in result.flags


@pytest.mark.parametrize("raw", ["half a cup synthetic ingredient", "1g plus two g synthetic ingredient",
    "2 x 400g/14oz cans synthetic ingredient", "1-2-3g synthetic ingredient",
    "1 and a half g synthetic ingredient"])
def test_unconsumed_source_expression_is_masked_instead_of_truncated(raw):
    result = parse_quantity_v2(raw, source_metadata=META)
    assert result.arithmetic.status == "UNKNOWN" and result.requires_review
