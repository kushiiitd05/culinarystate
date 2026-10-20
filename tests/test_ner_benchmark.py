"""S118 Part III: frozen semantic NER benchmark v1 — leakage, determinism, dev-only selection, metric behaviour."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from culinarystate.ner import benchmark as B

ROOT = Path(__file__).resolve().parents[1]
BM = ROOT / "benchmark" / "ner"
frozen = pytest.mark.skipif(not (BM / "semantic_benchmark_v1.json").exists(), reason="benchmark not frozen here")


def test_family_masks_numbers_and_split_is_deterministic():
    assert B.family("2 cups  Flour") == B.family("3/4 cups flour") == "# cups flour"
    s = ["2 cups flour", "1 cup flour", "salt", "3 eggs", "4 eggs"] * 40
    assert B.split_recipedb3(s) == B.split_recipedb3(s)


def test_family_never_crosses_splits():
    sents = [f"{n} cups item{m}" for m in range(300) for n in (1, 2, 3)]
    sp = B.split_recipedb3(sents)
    where = {}
    for part, idx in sp.items():
        for i in idx:
            assert where.setdefault(B.family(sents[i]), part) == part


def test_tasteset_identical_recipe_is_quarantined_and_calibration_disjoint():
    texts = [f"recipe {i % 90}\n1 cup x{i % 90}" for i in range(100)]          # ids i and i+90 are byte-identical
    sp = B.split_tasteset(texts)
    seen = set()
    for part in ("train", "calibration", "dev", "test"):
        assert not (seen & set(sp[part]))
        seen |= set(sp[part])
    held = {texts[i] for i in sp["dev"] + sp["test"]}
    assert all(texts[i] not in held for i in sp["train"] + sp["calibration"])


def test_checkpoint_selection_uses_dev_only():
    log = [{"dev_micro_f1": 0.90, "test_micro_f1": 0.99}, {"dev_micro_f1": 0.95, "test_micro_f1": 0.50}, {"dev_micro_f1": 0.95, "test_micro_f1": 0.60}]
    assert B.select_checkpoint(log) == 2                                          # tie -> earlier, test ignored
    with pytest.raises(ValueError):
        B.select_checkpoint([{"test_micro_f1": 0.9}])


def test_boundary_vs_type_errors():
    gold = [(0, 5, "FOOD"), (10, 14, "UNIT"), (20, 25, "FOOD")]
    pred = [(0, 7, "FOOD"), (10, 14, "FOOD"), (30, 35, "FOOD")]
    r = B.boundary_error_rate(gold, pred)
    assert (r["boundary_errors"], r["type_errors"], r["n_gold"]) == (1, 1, 3)


def test_strata_are_train_only_and_unseen_is_unseen_alias():
    train = [("1 cup flour", [(2, 5, "UNIT"), (6, 11, "FOOD")])] * 25 + [("rare thing", [(0, 4, "FOOD")])]
    c = B.surface_counts(train)
    assert B.stratum("FOOD", "Flour", c) == "head" and B.stratum("FOOD", "rare", c) == "tail" and B.stratum("FOOD", "kale", c) == "unseen"
    docs = [("kale flour", [(0, 4, "FOOD"), (5, 10, "FOOD")], [(5, 10, "FOOD")])]
    out = B.strata_f1(docs, c, {"FOOD"})
    assert out["unseen_alias"]["f1"] == 0.0 and out["head"]["f1"] == 1.0


def test_tags_to_bio_and_words_to_spans():
    bio = B.tags_to_bio(["QUANTITY", "UNIT", "NAME", "NAME", "O", "SIZE"], {"QUANTITY", "UNIT", "NAME"})
    assert bio == ["B-QUANTITY", "B-UNIT", "B-NAME", "I-NAME", "O", "O"]
    text, spans = B.words_to_spans("2 tbsp olive oil , x".split(), bio + ["O"][:0] + ["O"][:0] if False else bio[:5])
    assert [text[s:e] for s, e, _ in spans] == ["2", "tbsp", "olive oil"]


@frozen
def test_manifest_hashes_match_files_and_splits_are_disjoint():
    for row in csv.DictReader(open(BM / "semantic_benchmark_manifest.csv")):
        p = ROOT / row["path"]
        if p.exists():
            assert hashlib.sha256(p.read_bytes()).hexdigest() == row["sha256"], row["artifact"]
    for name in ("recipedb3", "tasteset"):
        sp = json.loads((BM / "splits" / f"{name}_split_v1.json").read_text())["indices"]
        parts = [set(sp[k]) for k in ("train", "calibration", "dev", "test")]
        assert sum(len(p) for p in parts) == len(set().union(*parts))


@frozen
def test_frozen_spec_declares_rules_before_any_candidate():
    spec = json.loads((BM / "semantic_benchmark_v1.json").read_text())
    assert spec["no_model_output_read"] and spec["seeds"] == [1, 2, 3, 4, 5]
    assert spec["statistics"]["min_effect_delta_micro_f1"] == 0.003 and "Holm" in spec["statistics"]["multiplicity"]
    assert "pareto_promotion_rule" in spec and spec["router"]["outputs"] == ["ACCEPT", "REVIEW", "NOVEL(NIL)", "REJECT"]
    for d in spec["datasets"].values():
        assert d["diagnostics"]["group_overlap_with_train"] == {"calibration": 0, "dev": 0, "test": 0}
