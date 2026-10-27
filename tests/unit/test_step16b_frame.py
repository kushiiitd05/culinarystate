"""Step 16b frame generator: determinism, text-free output, eligible sources, group coverage, inputs untouched."""
import hashlib
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("step16b", ROOT / "tools" / "step16b_build_frame.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

INPUTS = [mod.BASE, mod.FK, mod.FEAT, mod.GOLD, mod.POOL, mod.USAGE]
FORBIDDEN = ("title", "ingredient_text", "instruction", "steps_text", "pointer", "raw_hash", "cuisine_raw")
TEXT_EXACT = {"text", "recipe_text", "ingredients", "steps", "directions", "description"}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    before = {p: sha(p) for p in INPUTS}
    d = tmp_path_factory.mktemp("frame")
    a, b = d / "a.csv", d / "b.csv"
    for out in (a, b):
        df, _ = mod.build_frame(ROOT)
        mod.write_frame(df, out)
    after = {p: sha(p) for p in INPUTS}
    return a, b, before, after


def test_byte_identical_rerun(built):
    a, b, *_ = built
    assert a.read_bytes() == b.read_bytes()


def test_inputs_unchanged(built):
    *_, before, after = built
    assert before == after


def test_no_recipe_text_columns(built):
    df = pd.read_csv(built[0], dtype=str, keep_default_na=False)
    assert list(df.columns) == mod.COLUMNS
    for col in df.columns:
        assert not any(f in col.lower() for f in FORBIDDEN), col
        assert col.lower() not in TEXT_EXACT, col
    assert df["text_regex_strata_status"].eq("NOT_COMPUTED_TEXT_NOT_READ").all()


def test_only_eligible_sources(built):
    df = pd.read_csv(built[0], dtype=str, keep_default_na=False)
    assert set(df["source_family"]) <= set(mod.ELIGIBLE_SOURCES)
    assert df["recipe_id"].is_unique
    n = pd.to_numeric(df["n_ingredient_lines"]); s = pd.to_numeric(df["n_steps"])
    assert n.between(4, 20).all() and s.between(2, 15).all()


def test_group_id_for_every_row(built):
    df = pd.read_csv(built[0], dtype=str, keep_default_na=False)
    assert (df["group_id"] != "").all()
    assert set(df["group_basis"]) <= {"SPLIT_GROUP_07IC", "FALLBACK_COMPONENT_V1"}
    assert (df.loc[df.group_basis == "FALLBACK_COMPONENT_V1", "split_group_id"] == "").all()


def test_excluded_ids_absent(built):
    df = pd.read_csv(built[0], dtype=str, keep_default_na=False)
    gold = set(pd.read_parquet(ROOT / mod.GOLD)["recipe_id"])
    pool = set(pd.read_csv(ROOT / mod.POOL, usecols=["source_recipe_id"])["source_recipe_id"])
    assert not (set(df["recipe_id"]) & (gold | pool))


def test_fallback_components_synthetic():
    ids = pd.Series(["a", "b", "c", "d"])
    lab = mod.fallback_components(ids, {"k1": pd.Series(["x", "x", None, None]),
                                        "k2": pd.Series([None, "y", "y", None])})
    assert lab[0] == lab[1] == lab[2] and lab[3] != lab[0]


def test_is_indian():
    assert mod.is_indian("Bengali|Indian") and mod.is_indian("Indic") and mod.is_indian("South Indian")
    assert not mod.is_indian("Italian") and not mod.is_indian(None) and not mod.is_indian(float("nan"))
