"""STEP 07H-R: ledger-integrity, Gold/Silver separation and reference tests on the BUILT recipe base (skipped if the local parquet files are absent)."""
from pathlib import Path

import pytest

pq = pytest.importorskip("pyarrow.parquet")
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "ledgers/recipe_base/recipe_base_v1.parquet"
pytestmark = pytest.mark.skipif(not BASE.exists(), reason="recipe base not built locally")


@pytest.fixture(scope="module")
def base():
    return pq.read_table(BASE).to_pandas()


@pytest.fixture(scope="module")
def gold():
    return pq.read_table(ROOT / "ledgers/recipe_base/gold_recipe_index_v1.parquet").to_pandas()


def test_unique_ids_and_rec_mapping(base):
    from culinarystate.recipes import corpus as C
    rec = C.rec_latest()
    assert base.recipe_id.is_unique
    rb = base[base.source_family.isin(["A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT"])]
    assert set(rb.recipe_id) == set(rec) and len(rb) == 89565


def test_bulk_never_promoted_to_gold(base, gold):
    assert not base.quality_tier.isin(["DEEP_GOLD", "GOLD_LIGHT"]).any()
    g = base[base.quality_tier == "GOLD_PENDING_INDEPENDENT_IAA"]
    assert 0 < len(g) <= 40 and set(g.recipe_id) <= set(gold.recipe_id) and len(g) < len(base) / 1000
    assert (base[base.source_family != "A1_BBC_GOOD_FOOD"].query("quality_tier == 'SILVER_AUTO'")).empty


def test_gold_not_eligible_for_test_or_training_until_iaa(gold):
    pend = gold[gold.gold_status == "GOLD_PENDING_INDEPENDENT_IAA"]
    assert not pend.independent_annotation.any() and not pend.iaa_available.any() and not pend.eligible_for_test.any() and not pend.eligible_for_training.any()


def test_family_and_hash_columns(base):
    assert base.recipe_family_id.notna().all() and base.raw_hash.notna().all() and base.derived_hash.notna().all()
    assert (base.source_plane == "RECIPE").all()


def test_no_scientific_ledger_contamination():
    import subprocess
    r = subprocess.run(["git", "diff", "--quiet", "--", "ledgers/data/EVD.jsonl", "ledgers/data/COND.jsonl", "ledgers/data/MEAS.jsonl", "ledgers/data/SVAR.jsonl"], cwd=ROOT)
    assert r.returncode == 0
