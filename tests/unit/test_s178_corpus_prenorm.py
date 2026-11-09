"""S178 T3-C07-R1: SP-002 opt-in pre-normaliser. Synthetic strings only (invented foods); no corpus text."""
from __future__ import annotations

import dataclasses
import json
import random
from fractions import Fraction

import pytest

from culinarystate.quantity import parse_adapter, prenormalize as P, rc2_grounding
from culinarystate.quantity.grammar import normalize_text, parse_line
from culinarystate.quantity.parse_adapter import parse_quantity_v2
from culinarystate.quantity.rc2_dryrun import LOCALE_META, SOURCE_META, load_schema
from culinarystate.quantity.rc2_grounding import GroundingContext, ground_quantity_rc2

META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT", "evidence_refs": ["synthetic:prenorm"]}
FS = "⁄"
SCHEMA = load_schema()


def _strip_raw(p):
    return dataclasses.replace(p, raw="")


# ------------------------------------------------------------------ rule behaviour
@pytest.mark.parametrize("raw,expect", [
    (f"1{FS}4 tsp synthetic", "1/4 tsp synthetic"),
    (f"1 1{FS}2 cups synthetic", "1 1/2 cups synthetic"),
    (f"1{FS}2", "1/2"),
    (f"1 {FS} 2 cup synthetic", "1/2 cup synthetic"),
    (f"1∕2 cup synthetic", "1/2 cup synthetic"),
    (f"1／2 cup synthetic", "1/2 cup synthetic"),
    (f"1{FS}2 - 3{FS}4 cup synthetic", "1/2 - 3/4 cup synthetic"),
    (f"1 1{FS}2 - 2 1{FS}2 cups synthetic", "1 1/2 - 2 1/2 cups synthetic"),
    (f"1{FS}10 tsp synthetic", "1/10 tsp synthetic"),
    ("1-1/2 cups synthetic", "1 1/2 cups synthetic"),
    ("2-3/4 cups synthetic", "2 3/4 cups synthetic"),
    (f"1-1{FS}2 cups synthetic", "1 1/2 cups synthetic"),                      # both rules in sequence
])
def test_prenormalise_rewrites(raw, expect):
    pn = P.prenormalise(raw)
    assert pn.text == expect and pn.original == raw and pn.changed and not pn.refused
    assert P.prenormalise(pn.text).text == pn.text                 # idempotent


@pytest.mark.parametrize("raw", [
    "1/2-3/4 cup synthetic", "0-1/2 tsp synthetic", "1-3/2 cups synthetic", "1 - 1/2 cups synthetic",
    "11/2 cups synthetic", "1/2 cup synthetic", "2-3 cups synthetic", "350-1/2/3", "1.5-1/2 cups synthetic",
    "", "plain words only", f"{FS}2 cup synthetic", f"1{FS} cup synthetic",
])
def test_prenormalise_leaves_alone(raw):
    pn = P.prenormalise(raw)
    assert pn.text == raw and not pn.changed and pn.rules_fired == ()


@pytest.mark.parametrize("raw", [f"11{FS}2 cups synthetic", f"12{FS}3 tsp synthetic", f"1 11{FS}2 cups synthetic",
                                 f"100∕2 g synthetic"])
def test_glued_is_refused_not_guessed(raw):
    pn = P.prenormalise(raw)
    assert pn.refused and pn.text == raw and pn.rules_fired == (P.RULE_GLUED,)
    p = P.parse_line_prenorm(raw)
    assert p.kind == "NONE" and P.GLUED_FLAG in p.flags and p.raw == raw
    got = P.parse_quantity_v2_prenorm(raw, source_metadata=META)
    assert got.ast["node_type"] == "UNKNOWN" and P.GLUED_FLAG in got.flags and got.raw == raw
    assert got.arithmetic.status not in {"KNOWN", "RANGE"} and got.requires_review
    assert got.normalized.mass_g["status"] == "UNKNOWN" and got.normalized.count["status"] == "UNKNOWN"


def test_glued_only_when_the_rule_is_enabled():
    raw = f"11{FS}2 cups synthetic"
    pn = P.prenormalise(raw, rules=(P.RULE_U2044,))
    assert not pn.refused and pn.text == "11/2 cups synthetic"       # without the refuse rule it is plain 11/2
    assert P.prenormalise(raw, rules=()).changed is False


def test_rule_subsets_are_independent():
    both = f"1{FS}2 cup and 1-1/2 cups synthetic"
    assert P.prenormalise(both, rules=(P.RULE_U2044,)).text == "1/2 cup and 1-1/2 cups synthetic"
    assert P.prenormalise(both, rules=(P.RULE_HYPHEN,)).text == f"1{FS}2 cup and 1 1/2 cups synthetic"
    assert P.prenormalise(both).text == "1/2 cup and 1 1/2 cups synthetic"
    assert P.prenormalise(both).rules_fired == (P.RULE_U2044, P.RULE_HYPHEN)
    with pytest.raises(ValueError):
        P.prenormalise("1 cup", rules=("NOPE",))


# ------------------------------------------------------------------ legacy parse level
def test_legacy_defect_is_documented_not_fixed():
    """The frozen parser still misreads U+2044 (this test fails the day someone 'fixes' grammar.py silently)."""
    p = parse_line(f"1{FS}4 tsp synthetic")
    assert p.kind == "NUMBER" and p.value == 1.0 and p.unit_key is None
    p = parse_line("1-1/2 cups synthetic")
    assert p.kind == "RANGE" and (p.low, p.high) == (1.0, 0.5)
    assert FS in normalize_text(f"1{FS}2")


def test_parse_line_prenorm_matches_ascii_twin():
    cases = [f"1{FS}4 tsp synthetic", f"1 1{FS}2 cups synthetic", f"1{FS}2 synthetic", f"1{FS}2 - 3{FS}4 cup synthetic",
             f"2 1{FS}2 - 3 cups synthetic", f"1 {FS} 3 cup synthetic"]
    for raw in cases:
        got = P.parse_line_prenorm(raw)
        twin = parse_line(raw.replace(" " + FS + " ", "/").replace(FS, "/"))
        assert got.raw == raw
        assert _strip_raw(got) == _strip_raw(twin), raw
    q = P.parse_line_prenorm(f"1 1{FS}2 cups synthetic")
    assert (q.kind, q.value, q.unit_key) == ("MIXED", 1.5, "cup")
    q = P.parse_line_prenorm(f"1{FS}4 tsp synthetic")
    assert (q.kind, q.value, q.unit_key) == ("FRACTION", 0.25, "tsp")
    q = P.parse_line_prenorm("1-1/2 cups synthetic")
    assert (q.kind, q.value, q.unit_key) == ("MIXED", 1.5, "cup")


# ------------------------------------------------------------------ rc2 adapter level
def test_rc2_parse_exact_value_and_raw_preserved():
    raw = f"1 1{FS}2 cups synthetic"
    got = P.parse_quantity_v2_prenorm(raw, source_metadata=META)
    assert got.arithmetic.status == "KNOWN" and got.arithmetic.low == got.arithmetic.high == Fraction(3, 2)
    assert got.arithmetic.unit == "cup"
    assert got.raw == raw and got.ast["raw"] == raw and got.parsed.raw == raw
    assert got.normalized.volume_ml["raw"] == raw if got.normalized.volume_ml.get("raw") else True
    assert "PRENORM_SP002_U2044" in got.flags and got.rule_version == f"{parse_adapter.ADAPTER_VERSION}+{P.PRENORM_VERSION}"
    assert got.prenorm.original == raw and got.prenorm.rules_fired == (P.RULE_U2044,)
    twin = parse_quantity_v2("1 1/2 cups synthetic", source_metadata=META)
    assert (got.arithmetic.low, got.arithmetic.high, got.arithmetic.unit) == (twin.arithmetic.low, twin.arithmetic.high,
                                                                              twin.arithmetic.unit)


def test_rc2_parse_mass_unit_gets_q0_after_prenorm():
    raw = f"1{FS}4 kg synthetic"
    before = parse_quantity_v2(raw, source_metadata=META)
    after = P.parse_quantity_v2_prenorm(raw, source_metadata=META)
    assert before.arithmetic.unit == "item" and before.arithmetic.low == 1          # the SP-002 defect
    assert after.arithmetic.unit == "kg" and after.arithmetic.low == Fraction(1, 4)
    assert after.normalized.mass_g["value"] == 250.0


def test_rc2_hyphen_mixed():
    after = P.parse_quantity_v2_prenorm("2-1/2 cups synthetic", source_metadata=META)
    before = parse_quantity_v2("2-1/2 cups synthetic", source_metadata=META)
    assert after.arithmetic.low == after.arithmetic.high == Fraction(5, 2)
    assert before.arithmetic.status != "KNOWN" or before.arithmetic.low != Fraction(5, 2)


def test_invalid_metadata_still_raises():
    from culinarystate.quantity.draft_contract import ContractError
    for raw in (f"1{FS}2 cup", f"11{FS}2 cup", "1 cup"):
        with pytest.raises(ContractError):
            P.parse_quantity_v2_prenorm(raw, source_metadata={"origin": "NOPE"})


# ------------------------------------------------------------------ rc2 grounding
def _ctx(locale="US"):
    return GroundingContext(source_metadata=SOURCE_META, locale=locale, locale_metadata=LOCALE_META if locale else None)


def _dump(res):
    return json.dumps([res.record, res.unit_resolution, res.mass_route, res.ast_root, res.arithmetic_status,
                       list(res.flags), [(i.code, i.path) for i in res.issues], res.compatibility_mass_status,
                       res.pipeline_version], sort_keys=True, default=str)


def test_grounding_affected_line_changes_and_stays_contract_valid():
    raw = f"1{FS}4 kg synthetic"
    before = ground_quantity_rc2(raw, _ctx(), schema=SCHEMA)
    after = P.ground_quantity_rc2_prenorm(raw, _ctx(), schema=SCHEMA)
    assert before.mass_route != "AST_EXACT_PHYSICAL" and after.mass_route == "AST_EXACT_PHYSICAL"
    assert after.record["mass_g"]["value"] == 250 and after.record["q_level"] == "Q0"
    assert after.record["raw"] == raw and not after.issues and not before.issues
    assert after.pipeline_version.endswith("+" + P.PRENORM_VERSION)
    assert rc2_grounding.parse_quantity_v2 is parse_adapter.parse_quantity_v2        # swap undone


def test_grounding_glued_is_refused():
    res = P.ground_quantity_rc2_prenorm(f"11{FS}2 kg synthetic", _ctx(), schema=SCHEMA)
    assert res.mass_route == "UNSUPPORTED_EXPRESSION" and res.exact_mass is None
    assert res.record["mass_g"]["status"] == "UNKNOWN" and not res.issues


def test_swap_is_undone_on_error():
    with pytest.raises(Exception):
        P.ground_quantity_rc2_prenorm(f"1{FS}2 cup", _ctx(), schema={"properties": {}})      # non-rc2 schema -> ContractError
    assert rc2_grounding.parse_quantity_v2 is parse_adapter.parse_quantity_v2


# ------------------------------------------------------------------ byte-identical for unaffected input
UNAFFECTED = [
    "1 cup synthetic flour", "1/2 tsp synthetic salt", "1 1/2 cups synthetic milk", "2 x 400g cans synthetic tomatoes",
    "250ml/9fl oz synthetic cream", "1½ tbsp synthetic oil", "½ cup synthetic", "1¼ cups synthetic",
    "3 synthetic eggs", "a pinch of synthetic", "juice of 1 synthetic lemon", "1-2 cups synthetic", "1/2-3/4 cup synthetic",
    "1 to 2 synthetic", "175g synthetic", "5cm piece synthetic", "1/0 cup synthetic", "salt to taste", "11/2 cups synthetic",
    "0-1/2 tsp synthetic", "1.5 cups synthetic", "2 – 3 cups synthetic", "synthetic only", "", "   ", "1 -2 synthetic",
    "1-3/2 cups synthetic",
]   # S178 CORP-2: "1 - 1/2 cups synthetic" (an inverted RANGE) moved to the INVERTED_RANGE tests


@pytest.mark.parametrize("raw", UNAFFECTED)
def test_unaffected_lines_are_byte_identical(raw):
    assert P.prenormalise(raw).text == raw and not P.prenormalise(raw).changed
    assert P.parse_line_prenorm(raw) == parse_line(raw)
    if raw.strip():
        a = P.parse_quantity_v2_prenorm(raw, source_metadata=META)
        b = parse_quantity_v2(raw, source_metadata=META)
        assert type(a) is type(b) and repr(a) == repr(b) and a.rule_version == b.rule_version
        assert _dump(P.ground_quantity_rc2_prenorm(raw, _ctx(), schema=SCHEMA)) == _dump(
            ground_quantity_rc2(raw, _ctx(), schema=SCHEMA))


def _random_line(rng: random.Random) -> str:
    atoms = ["1", "2", "3", "10", "12", "250", "1/2", "3/4", "1/10", "1 1/2", "2 1/4", "0.5", "1.25", "½", "-", " - ",
             "to", "or", "x", "g", "kg", "ml", "cup", "cups", "tsp", "tbsp", "oz", "can", "large", "small", "(", ")", ",",
             "about", "plus", "and", "synthetic", "flour", "/", "1-2", "a", "an", "half", "juice of", "–", "  "]
    return " ".join(rng.choice(atoms) for _ in range(rng.randint(1, 7)))


def test_random_unaffected_lines_are_byte_identical():
    rng = random.Random(20261109)
    checked = 0
    ctx = _ctx()
    while checked < 400:
        s = _random_line(rng).strip()
        if not s or P.prenormalise(s).changed or P.inverted_range(parse_line(s)):     # S178: inverted ranges are flagged
            continue
        checked += 1
        assert P.parse_line_prenorm(s) == parse_line(s)
        a = P.parse_quantity_v2_prenorm(s, source_metadata=META)
        b = parse_quantity_v2(s, source_metadata=META)
        assert repr(a) == repr(b), s
        if checked % 8 == 0:
            assert _dump(P.ground_quantity_rc2_prenorm(s, ctx, schema=SCHEMA)) == _dump(ground_quantity_rc2(s, ctx, schema=SCHEMA)), s


def test_random_affected_lines_equal_their_ascii_twin():
    """Any line whose only trigger is U+2044 between single digits parses like its ASCII twin (raw aside)."""
    rng = random.Random(7)
    seen = 0
    for _ in range(300):
        a, b = rng.randint(1, 9), rng.randint(2, 9)
        whole = rng.choice(["", f"{rng.randint(1, 9)} "])
        unit = rng.choice(["cup", "cups", "tsp", "g", "kg", "ml", "", "can"])
        raw = f"{whole}{a}{FS}{b} {unit} synthetic".replace("  ", " ")
        pn = P.prenormalise(raw)
        assert pn.changed and not pn.refused
        twin = raw.replace(FS, "/")
        got = P.parse_quantity_v2_prenorm(raw, source_metadata=META)
        want = parse_quantity_v2(twin, source_metadata=META)
        assert (got.arithmetic.status, got.arithmetic.low, got.arithmetic.high, got.arithmetic.unit) == \
               (want.arithmetic.status, want.arithmetic.low, want.arithmetic.high, want.arithmetic.unit)
        assert got.raw == raw
        seen += 1
    assert seen == 300
