"""S116: evidence-first matching, independence counting, ingest policy, simulator contract, secret hygiene."""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import evidence_first_candidates as efc  # noqa: E402
from culinarystate.sources.policy import can_ingest_canonical  # noqa: E402
from culinarystate.state_graph.source_class import ContractError, SourceClass, TransitionInput  # noqa: E402


@pytest.fixture()
def ctx():
    efc.G.clear()
    efc.G.update({"ing": {"broccoli": "ING-1", "onion": "ING-2"}, "proc": {"boil": "PROC-1", "fry": "PROC-2"},
                  "cells": defaultdict(list, {("ING-1", "PROC-1"): ["EVD-1"]}), "names": {"broccoli", "onion"}})


def _rows(lines, steps):
    return efc._one(("wikibooks", "R1", "Test", lines, steps))[4]


def test_ingredient_list_alone_does_not_match(ctx):
    assert _rows(["200g broccoli", "1 onion"], ["Mix everything together and serve."]) == []


def test_process_must_act_on_the_ingredient(ctx):
    assert _rows(["200g broccoli", "1 onion"], ["Fry the onion until soft.", "Serve with the broccoli."]) == []


def test_instruction_level_match(ctx):
    rows = _rows(["200g broccoli"], ["Boil the broccoli for 5 minutes."])
    assert [(r["ingredient_id"], r["process"]) for r in rows] == [("ING-1", "PROC-1")]
    assert "broccoli" in rows[0]["instruction_span"].lower()


def test_duplicate_families_not_independent():
    rows = [{"pool": "p", "recipe_family": "FAM-a"}, {"pool": "p", "recipe_family": "FAM-a"}, {"pool": "p", "recipe_family": "FAM-b"}]
    assert efc.independent_families(rows) == 2


def test_policy_blocks_live_only_and_unresolved():
    assert not can_ingest_canonical({"status": "LIVE_ONLY / DO_NOT_STORE", "redistribution": "Y", "bulk_training_allowed": "Y", "licence": "CC0"})[0]
    assert not can_ingest_canonical({"status": "DOWNLOADED", "redistribution": "NO", "bulk_training_allowed": "Y", "licence": "CC0"})[0]
    assert not can_ingest_canonical({"status": "DOWNLOADED", "redistribution": "UNVERIFIED", "bulk_training_allowed": "Y", "licence": "CC0"})[0]
    assert not can_ingest_canonical({"status": "DOWNLOADED", "redistribution": "Y", "bulk_training_allowed": "PERMISSION_REQUIRED", "licence": "x"})[0]
    assert can_ingest_canonical({"status": "DOWNLOADED", "redistribution": "Y", "bulk_training_allowed": "Y", "licence": "CC0 1.0"})[0]


def test_registry_rows_obey_policy():
    rows = list(csv.DictReader((ROOT / "registry/sources/external_data_source_registry.csv").open()))
    by = {r["name"]: r for r in rows}
    spoon = next(r for n, r in by.items() if n == "Spoonacular")
    assert not can_ingest_canonical(spoon)[0]
    for r in rows:
        if "LIVE_ONLY" in r["status"] or "DO_NOT_USE" in r["roles"]:
            assert not can_ingest_canonical(r)[0], r["name"]
    assert not can_ingest_canonical(next(r for r in rows if r["source_id"] == "XS-A02"))[0]        # RecipeNLG: non-commercial
    assert not can_ingest_canonical(next(r for r in rows if r["source_id"] == "XS-A01"))[0]        # Food.com: authority unverified


def _ti(**kw):
    base = dict(source_class=SourceClass.COMPILED_RETENTION, source_id="SRC-1", source_record_id="EVD-1", evidence_tier="E3", process="boil",
                provenance="usda r6")
    base.update(kw)
    return TransitionInput(**base)


def test_contract_structural_recipe_cannot_carry_magnitude():
    _ti(source_class=SourceClass.STRUCTURAL_RECIPE)
    with pytest.raises(ContractError):
        _ti(source_class=SourceClass.STRUCTURAL_RECIPE, magnitude=0.8)
    assert _ti(magnitude=0.8).magnitude == 0.8


def test_contract_requires_provenance_and_model_uncertainty():
    with pytest.raises(ContractError):
        _ti(provenance="")
    with pytest.raises(ContractError):
        _ti(source_class=SourceClass.MODEL_GENERATED, magnitude=0.5)
    _ti(source_class=SourceClass.MODEL_GENERATED, magnitude=0.5, uncertainty="0.2 sd")
    with pytest.raises(ContractError):
        _ti(source_class="KINETIC")


SECRET_RX = re.compile(r"sk_live_[A-Za-z0-9]{12,}|\brd_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|KGAT_[A-Za-z0-9]{10,}")


def test_no_credentials_in_repository_files():
    bad = []
    for d in ("src", "tools", "tests", "registry", "reports", "docs", "handoff", "benchmark", "experiments", "annotation"):
        for f in (ROOT / d).rglob("*"):
            if f.is_file() and f.suffix in {".py", ".md", ".csv", ".json", ".jsonl", ".txt", ".yaml", ".yml", ".sh"} and f.stat().st_size < 5_000_000:
                if "pilot_20" in str(f) or "ai_review" in str(f) or "parv_pack" in str(f):
                    continue
                try:
                    if SECRET_RX.search(f.read_text(errors="ignore")):
                        bad.append(str(f.relative_to(ROOT)))
                except OSError:
                    pass
    assert not bad, f"credential-like strings in: {bad}"   # paths only; values are never printed


def test_missing_evidence_classification():
    import hstate_missing_evidence_ranked as m
    r = {"ingredient": "carrot", "process_family": "DRY_HEAT"}
    assert m.classify(r, None) == ("VEGETABLE", "")                                      # category-less ingredient resolved by the allow-map
    assert m.classify({"ingredient": "carrot", "process_family": "HEAT_GENERAL"}, None)[1] == "GENERIC_PROCESS_UNRESOLVED"
    assert m.classify({"ingredient": "carrot", "process_family": "MECHANICAL_MIX"}, None)[1] == "NON_THERMAL_STRUCTURAL_ONLY"
    assert m.classify({"ingredient": "avocado oil", "process_family": "WET_HEAT"}, "FRUIT")[1] == "INGREDIENT_NOT_RETENTION_MEANINGFUL"
    assert m.classify({"ingredient": "plain flour", "process_family": "DRY_HEAT"}, None)[1] == "INGREDIENT_UNCATEGORISED"


def test_infoods_classes_never_claim_matched_experiment():
    import infoods_transition_candidates as t
    assert t.classify_ufish_row("calc. from 091001", {"fi002"})[0] == "COMPILED_REFERENCE"
    assert t.classify_ufish_row("fi002", {"fi002"})[0] == "SAME_STUDY_UNMATCHED"
    assert t.classify_ufish_row("fi999", {"fi002"})[0] == "CROSS_STUDY_COMPARISON"
    assert t.classify_ufish_row("", {"fi002"})[0] == "QUALITATIVE_ONLY"
