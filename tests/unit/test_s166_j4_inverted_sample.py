"""S166: J4 sample of V2 INVERTED_INTERVAL cases for human reading (block J4; D-059).

Finds Rung A quantity groundings whose rc2 record V2 flags INVERTED_INTERVAL, gives each a shape mask (digits -> 9,
letter runs -> a), and draws the agreed stratified sample: every case in the seeded 1,000 sample, all A1 and
Wikibooks cases, up to 30 Food.com and 30 Gutenberg, with every P1 manifest recipe excluded. Synthetic text only.
"""
import hashlib

from culinarystate.extraction import j4_inverted_sample as J

MIXED = "Add 1-1/2 cups flour and bake 20 minutes."
RANGE = "Bake 20-25 minutes."


def test_a_mixed_number_read_as_a_range_is_found_with_its_span():
    hits = J.inverted_spans(MIXED, locale="US")
    assert len(hits) == 1
    start, end = hits[0]
    assert MIXED[start:end].startswith("1-1/2")


def test_an_ordinary_range_is_not_flagged():
    assert J.inverted_spans(RANGE, locale="US") == []


def test_shape_mask_hides_digits_and_words():
    assert J.shape("1-1/2 cups") == "9-9/9 a"
    assert J.shape("10 - 12 Tbsp.") == "9 - 9 a."


def _cands():
    out = []
    for fam, n in (("FOODCOM", 50), ("GUTENBERG_SEGMENT", 40), ("A1_BBC_GOOD_FOOD", 2), ("WIKIBOOKS", 2)):
        out += [{"recipe_id": f"{fam}-{i}", "source_family": fam, "start": 3, "end": 9} for i in range(n)]
    return out


def test_stratified_sample_follows_the_agreed_quotas_and_exclusions():
    in_1000 = {"FOODCOM-7", "GUTENBERG_SEGMENT-3"}
    excluded = {"FOODCOM-0", "WIKIBOOKS-1"}
    rows = J.stratified_sample(_cands(), seed="s", in_1000=in_1000, excluded=excluded)
    ids = [r["recipe_id"] for r in rows]
    assert not set(ids) & excluded and len(ids) == len(set((r["recipe_id"], r["start"]) for r in rows))
    by = {}
    for r in rows:
        by.setdefault(r["stratum"], []).append(r)
    assert {r["recipe_id"] for r in by["S1_IN_1000_SAMPLE"]} == in_1000
    assert len(by["S2_A1_ALL"]) == 2 and len(by["S3_WIKIBOOKS_ALL"]) == 1
    assert len(by["S4_FOODCOM_30"]) == 30 and len(by["S5_GUTENBERG_30"]) == 30
    assert J.stratified_sample(_cands(), seed="s", in_1000=in_1000, excluded=excluded) == rows
    assert J.stratified_sample(_cands(), seed="t", in_1000=in_1000, excluded=excluded) != rows


def test_manifest_rows_are_text_free():
    rows = J.stratified_sample(_cands(), seed="s", in_1000=set(), excluded=set())
    man = J.manifest_rows(rows)
    assert set(man[0]) == {"case_id", "recipe_id_sha256", "source_family", "stratum", "shape"}
    assert man[0]["recipe_id_sha256"] == hashlib.sha256(rows[0]["recipe_id"].encode()).hexdigest()
    assert not any(r["recipe_id"] in str(man) for r in rows)
