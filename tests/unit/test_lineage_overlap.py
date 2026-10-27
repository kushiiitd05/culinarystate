"""Synthetic fixtures only; no third-party text."""
import json
import subprocess
import sys
from pathlib import Path

from culinarystate.lineage.overlap import (
    extract_references,
    match,
    normalise_key,
    verdict,
)

ROOT = Path(__file__).resolve().parents[2]

NUMBERED = """Intro text
References
 [1] Alpha, A. (1984). Synthetic study of widgets in kitchens. J. Fake Science. 3, 1-9
[2]   Beta, B., Gamma, C. (1990). Another invented title
      continued on a second line. Publisher X.
 [3] USDA Table of Nutrient Retention Factors, Release 4 (1998).
Appendix C
Unrelated Delta, D. (2001). Should not be read.
"""

PARAGRAPHS = """front matter
References

Alpha A, Beta B. 1984. Synthetic Study of Widgets in Kitchens. Journal of Fake Science.
3:1-9.

Zeta, Z, Eta, E. Widgets and ovens revisited. Journal of Fake Science. 2002; 15: 1-2.

USDA. Group. 1982. Provisional Table on Retention.
\x0c
page two Theta, T. 1999. Not a reference.
"""


def test_numbered_extraction_stops_at_appendix():
    refs = extract_references(NUMBERED)
    assert [(r.surname, r.year) for r in refs] == [("alpha", 1984), ("beta", 1990), ("usda", 1998)]


def test_paragraph_extraction_stops_at_formfeed_and_handles_year_after_title():
    refs = extract_references(PARAGRAPHS)
    assert [(r.surname, r.year) for r in refs] == [("alpha", 1984), ("zeta", 2002), ("usda", 1982)]
    assert refs[1].title_words[:2] == ("widgets", "and")


def test_no_references_heading_returns_empty():
    assert extract_references("1,2,3\n~0001~^~01~") == []


def test_normalise_key_strips_case_punctuation_and_accents():
    a = extract_references("References\n [1] Bognár, A. (1984). Das Ding, Test!\n")[0]
    b = extract_references("References\n [1] BOGNAR, a. (1984). das ding test\n")[0]
    assert normalise_key(a) == normalise_key(b) == "bognar|1984|das ding test"


def test_exact_and_fuzzy_match_counted_separately():
    a = extract_references("References\n [1] Alpha, A. (1984). Synthetic study of widgets in kitchens. J. Fake Science. 3, 1\n"
                           " [2] Kappa, K. (1990). Cooking losses in vegetables studied broadly\n")
    b = extract_references("References\n [1] Alpha, A. (1984). Synthetic study of widgets in kitchens. J. Fake Science. 3, 1\n"
                           " [2] Kappa, K. (1991). Cooking losses in vegetables studied\n"
                           " [3] Other, O. (2000). Nothing in common\n")
    m = match(a, b)
    assert m.exact_count == 1 and m.fuzzy_count == 1
    assert m.exact[0] == ("alpha", 1984, "fake science")
    assert m.fuzzy[0][:2] == ("kappa", 1990)
    assert verdict(a, b, m) == "OVERLAP_FOUND"


def test_no_overlap_verdict():
    a = extract_references("References\n [1] Alpha, A. (1984). Synthetic study of widgets\n")
    b = extract_references("References\n [1] Other, O. (2000). Nothing in common here\n")
    assert verdict(a, b, match(a, b)) == "NO_OVERLAP_FOUND_IN_BIBLIOGRAPHY"


def test_not_determinable_when_a_list_is_empty_or_unreliable():
    ok = extract_references("References\n [1] Alpha, A. (1984). Synthetic study of widgets\n")
    assert verdict([], ok, match([], ok)) == "NOT_DETERMINABLE"
    bad = extract_references("References\n [1] no year or author here at all\n")
    assert verdict(ok, bad, match(ok, bad)) == "NOT_DETERMINABLE"


def test_output_has_no_long_passages():
    refs = extract_references(NUMBERED)
    for r in refs:
        assert len(normalise_key(r)) < 80


def test_cli_deterministic_and_text_only(tmp_path):
    us = tmp_path / "usda.txt"
    bo = tmp_path / "bog.txt"
    us.write_text(PARAGRAPHS.replace("Alpha A, Beta B.", "Omega A, Beta B."))
    bo.write_text(NUMBERED)
    cs = tmp_path / "cs.json"
    cs.write_text(json.dumps({
        "L1 ingredient-level: USDA-RETN-R6 vs BOGNAR-2002": {"overlap_cells": 5},
        "L2 food-group x step-family: USDA-RETN-R6 vs BOGNAR-2002": {"overlap_cells": 9},
    }))
    outs = []
    for i in (1, 2):
        j, m = tmp_path / f"o{i}.json", tmp_path / f"o{i}.md"
        subprocess.run([sys.executable, str(ROOT / "tools" / "step08a_overlap.py"),
                        "--usda-text", str(us), "--bognar-text", str(bo), "--cross-source", str(cs),
                        "--out-json", str(j), "--out-md", str(m)], check=True)
        outs.append((j.read_bytes(), m.read_bytes()))
    assert outs[0] == outs[1]
    d = json.loads(outs[0][0])
    assert d["verdict"] == "NO_OVERLAP_FOUND_IN_BIBLIOGRAPHY"
    assert d["cells_affected_if_overlap"] == {"L1": 5, "L2": 9}
    assert "Should not be read" not in outs[0][0].decode()


def test_trailing_page_number_is_not_an_entry():
    refs = extract_references("References\n\nAlpha A. 1984. Widgets in kitchens. J. Fake. 3:1.\n\n\n   4\n\x0c")
    assert [(r.surname, r.year) for r in refs] == [("alpha", 1984)]


def test_title_before_trailing_year_is_kept_for_citation_flag():
    from culinarystate.lineage.overlap import cites_title
    refs = extract_references(NUMBERED)
    assert cites_title(refs, "Table of Nutrient Retention Factors") == [("usda", 1998)]
