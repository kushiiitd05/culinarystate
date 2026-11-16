"""S178 T3-C03-R2: ING/ALIAS coverage census. Synthetic lexicon (invented surfaces, test only); real-data checks read the committed JSON."""
from __future__ import annotations

import json

import pytest

from culinarystate.extraction.rung_a_lexicon import build_lexicon, key_of, tokens
from culinarystate.quantity.grammar import parse_line
from tests.unit.test_s178_analysis_helpers import ROOT, load_tool

C = load_tool("s178_analysis_coverage_census")


@pytest.fixture(scope="module")
def matcher():
    lex = build_lexicon(foods={"salt": ["ING-1"], "sea salt": ["ING-2"], "table salt": ["ING-1"], "oil": ["ING-3"]},
                        procs={}, proc_info={}, tools={}, tool_classes={}, units=[])
    return C.Matcher(lex, {key_of("salt"), key_of("sea salt"), key_of("oil")})


def test_classes(matcher):
    assert matcher.classify(["salt"])[0] == "EXACT_ING"
    assert matcher.classify(["salts"])[0] == "EXACT_ING"                 # plural strip
    assert matcher.classify(["table", "salt"])[0] == "EXACT_ALIAS"       # alias surface, not a canonical name
    assert matcher.classify(["fine", "sea", "salt"]) == ("PARTIAL", 2, 3)
    assert matcher.classify(["mystery", "herb"]) == ("MISS", 0, 2)
    assert matcher.classify([]) == ("MISS", 0, 0)
    assert matcher.any_hit(["a", "oil"]) and not matcher.any_hit(["a", "b"])


def test_mention_rule():
    assert C.mention_words("2 cups of salt, sifted", "WIKIBOOKS", tokens, parse_line) == ["salt"]
    assert C.mention_words("Sea Salt (fine)", "FOODCOM", tokens, parse_line) == ["sea", "salt"]
    assert C.mention_words("", "FOODCOM", tokens, parse_line) == []
    # a leading parenthetical conversion must not swallow the food (S178 bug found on Wikibooks lines)
    assert C.mention_words("200 ml (3/4 cup) boiling water", "WIKIBOOKS", tokens, parse_line) == ["boiling", "water"]
    assert C.mention_words("1 can () condensed soup (figures vary), drained", "WIKIBOOKS", tokens, parse_line) == ["condensed", "soup"]
    assert C.mention_words("1/2 tsp", "WIKIBOOKS", tokens, parse_line) == []


ROWS = [("salt", 50, "EXACT_ING"), ("oil", 30, "EXACT_ING"), ("sea salt", 10, "EXACT_ING"), ("fine sea salt", 6, "PARTIAL"),
        ("herb x", 3, "MISS"), ("pinch salt", 1, "PARTIAL")]


def test_deciles_partition_mentions_and_types():
    total = sum(c for _, c, _ in ROWS)
    for fn in (C.deciles_by_mass, C.deciles_by_rank):
        d = fn(ROWS)
        assert len(d) == 10
        assert sum(x["mentions"] for x in d) == total
        assert sum(x["types"] for x in d) == len(ROWS)
    d = C.deciles_by_mass(ROWS)
    assert d[0]["types"] == 1 and d[0]["pct_exact"] == 100.0          # the most frequent phrase opens decile 1
    many = [(f"p{i}", 100 - i, "EXACT_ING" if i < 12 else "MISS") for i in range(20)]
    r = C.deciles_by_rank(many)
    assert [x["types"] for x in r] == [2] * 10 and r[0]["max_count"] == 100 and r[9]["min_count"] == 81
    assert r[0]["pct_exact"] == 100.0 and r[9]["pct_exact"] == 0.0


def test_curve_and_family_block_have_no_phrase_text():
    cls_of = {tuple(p.split()): (k, 1, len(p.split())) for p, _, k in ROWS}
    from collections import Counter
    blk, rows = C.family_block(Counter({tuple(p.split()): c for p, c, _ in ROWS}), cls_of)
    assert blk["mentions"] == 100 and blk["types"] == 6 and blk["pct_exact"] == 90.0
    assert blk["types_needed_for_pct_of_mentions"]["50"] == 1 and blk["types_needed_for_pct_of_mentions"]["80"] == 2
    assert blk["nonexact_types"] == 3
    text = json.dumps(blk)
    assert "fine sea salt" not in text and "herb" not in text           # counts only: no phrase leaves the block
    assert rows[0][0] == "salt"


def test_committed_census_is_counts_only_and_reconciles_with_s177():
    p = ROOT / "reports/s178/analysis/ing_alias_coverage_census_v1.json"
    if not p.is_file():
        pytest.skip("census not generated in this tree")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["contains_text"] is False and d["lexicon"]["lexicon_fingerprint"]
    for fam, rec in d["reconciliation_with_s177_line_census"].items():
        assert rec["delta"] == 0 and rec["lines_equal"], fam
    for fam in ("FOODCOM", "WIKIBOOKS", "TASTESET"):
        b = d["families"][fam]
        assert sum(b["mentions_by_class"].values()) == b["mentions"]
        assert sum(x["mentions"] for x in b["deciles_by_mention_mass"]) == b["mentions"]
        assert sum(x["types"] for x in b["deciles_by_type_rank"]) == b["types"]
    assert d["families"]["FOODCOM"]["lines_with_u2044_fraction_slash"] == 1275153
    assert d["families"]["GUTENBERG_SEGMENT"]["status"] == "NOT_AVAILABLE"
    assert d["unmapped_lists"]["FOODCOM"]["git_ignored"] is True
