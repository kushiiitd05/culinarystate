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


# ------------------------------------------------ CLI (sharded, private excerpts git-ignored)
def _tool():
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("j4tool", root / "tools/j4_inverted_interval_sample.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _recs():
    out = []
    for i in range(12):
        fam = ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS")[i % 3]
        out.append({"recipe_id": f"R{i}", "source_family": fam,
                    "steps": [MIXED if i % 2 == 0 else RANGE, "Serve."]})
    return out


def test_cli_one_and_two_workers_agree_and_keep_text_private(tmp_path):
    tool = _tool()
    res = []
    for w in (1, 2):
        man, priv = tmp_path / f"m{w}.csv", tmp_path / f"p{w}.csv"
        assert tool.main(["--seed", "s", "--workers", str(w), "--out-manifest", str(man), "--out-private", str(priv),
                          "--exclude-manifest", ""], record_source=lambda fams, root: iter(_recs())) == 0
        res.append((man.read_text(), priv.read_text()))
    assert res[0] == res[1]
    man_text, priv_text = res[0]
    assert "flour" not in man_text and "R0" not in man_text and "flour" in priv_text
    assert man_text.count("\n") - 1 == 6  # six recipes carry the mixed number


def test_cli_refuses_a_private_file_that_git_would_track(tmp_path):
    import pytest as _pt
    tool = _tool()
    with _pt.raises(SystemExit):
        tool.main(["--seed", "s", "--out-manifest", str(tmp_path / "m.csv"),
                   "--out-private", str(tool.ROOT / "reports/step17/j4_private_TEST.csv"), "--exclude-manifest", ""],
                  record_source=lambda fams, root: iter(_recs()))
