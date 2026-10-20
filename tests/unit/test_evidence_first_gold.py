"""S116: evidence-first Gold selection determinism, family dedupe, reserve rules, pack equality/blankness, no leakage."""
import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import select_evidence_first_gold as sel  # noqa: E402
import make_independent_gold_packs as packs  # noqa: E402

PFAM = {"PROC-1": "WET_HEAT", "PROC-2": "FAT_HEAT", "PROC-3": "DRY_HEAT"}
SRC = {("ING-1", "PROC-1"): {"S1"}, ("ING-2", "PROC-2"): {"S2"}, ("ING-3", "PROC-3"): {"S3"}, ("ING-4", "PROC-1"): {"S1"}}


def _cands():
    return {"FC1": {"cells": [("ING-1", "PROC-1")], "fam": "FAM-a", "parts": {"a", "b", "c"}},
            "FC2": {"cells": [("ING-2", "PROC-2")], "fam": "FAM-b", "parts": {"d", "e", "f"}},
            "FC3": {"cells": [("ING-3", "PROC-3")], "fam": "FAM-c", "parts": {"g", "h", "i"}},
            "FC4": {"cells": [("ING-4", "PROC-1")], "fam": "FAM-a", "parts": {"j", "k", "l"}}}   # same family as FC1


CAPS = {"ingredient": 3, "cell": 4}


def test_selection_is_deterministic():
    a = sel.greedy(_cands(), 3, CAPS, PFAM, SRC)
    b = sel.greedy(dict(reversed(list(_cands().items()))), 3, CAPS, PFAM, SRC)
    assert [r for r, _, _ in a] == [r for r, _, _ in b]


def test_family_dedupe_one_recipe_per_family():
    out = sel.greedy(_cands(), 4, CAPS, PFAM, SRC)
    assert len(out) == 3 and not ({"FC1", "FC4"} <= {r for r, _, _ in out})


def test_near_duplicate_ingredient_sets_rejected():
    c = _cands()
    c["FC3"]["parts"] = set(c["FC2"]["parts"])
    out = [r for r, _, _ in sel.greedy(c, 4, CAPS, PFAM, SRC)]
    assert not ({"FC2", "FC3"} <= set(out))


def test_ingredient_in_sentence_is_required_text_level():
    assert sel.ingredient_in_text("broccoli", "Steam broccoli and cauliflower until tender.")
    assert not sel.ingredient_in_text("broccoli", "Mix the pasta with the sauce.")


def _manifest():
    rows = []
    for k in range(1, 4):
        rows.append({"selection_id": f"EFG-{k:03d}", "source_recipe_id": f"FC{k}", "selection_role": "PRIMARY" if k < 3 else "RESERVE"})
    rows.append({"selection_id": "EFG-004", "source_recipe_id": "FC4", "selection_role": "RESERVE"})
    return rows


def test_reserve_replacement_only_for_prespecified_reasons():
    with pytest.raises(ValueError):
        sel.replace_primary(_manifest(), "FC1", "ANNOTATION_TOO_HARD")
    with pytest.raises(ValueError):
        sel.replace_primary(_manifest(), "FC1", "MODEL_PERFORMS_POORLY")
    out = sel.replace_primary(_manifest(), "FC1", "SOURCE_CORRUPTION")
    roles = {r["source_recipe_id"]: r["selection_role"] for r in out}
    assert roles["FC1"] == "REPLACED" and roles["FC3"] == "PRIMARY" and roles["FC4"] == "RESERVE"


def test_packs_blank_equal_and_leak_free():
    d = packs.D
    man = d / "selection_manifest_v1.csv"
    if not man.exists():
        pytest.skip("selection not generated on this machine")
    prim = sorted({r["source_recipe_id"] for r in csv.DictReader(man.open()) if r["selection_role"] == "PRIMARY"})
    assert len(prim) == 20
    for rid in prim:
        k, p = json.loads((d / "_split" / "Kush" / f"{rid}.Kush.json").read_text()), json.loads((d / "_split" / "Parv" / f"{rid}.Parv.json").read_text())
        assert packs.pristine(k) and packs.pristine(p)                                    # no spans, events, coref, concepts, notes
        assert packs.raw_hash(k) == packs.raw_hash(p)                                     # identical recipe text
        assert k["annotator"] == "Kush" and p["annotator"] == "Parv" and k["status"] == p["status"] == "DRAFT"
        assert "DRAFT_HUMAN_INDEPENDENT" in k["source_ref"]
        for doc in (k, p):
            assert all(l["entity"] == "TODO" and l["concept"] == "TODO" and not l["spans"] for l in doc["ingredient_lines"])
            assert all(not s["events"] and not s["coref"] and not s["spans"] for s in doc["steps"])


def test_committed_manifests_contain_no_recipe_text():
    for name in ("selection_manifest_v1.csv", "screening_log.csv", "preannotation_manifest.csv"):
        f = packs.D / name
        if not f.exists():
            continue
        header = next(csv.reader(f.open()))
        assert not {"title", "matched_step", "instruction_span", "ingredient_line", "steps", "text"} & set(header), name
        for row in csv.DictReader(f.open()):
            assert all(len(v) < 400 for v in row.values()), f"{name}: suspiciously long cell"


def test_recipedb3_summary_handles_partial_and_complete(tmp_path, monkeypatch):
    import summarise_recipedb3_repro as s
    def run(protocol, seed, best, last):
        sc = lambda f: {"macro_f1": f, "micro_f1": f + 0.01, "n_entities": 10, "per_label": {"NAME": {"f1": f, "precision": f, "recall": f, "support": 5}}}
        return {"protocol": protocol, "seed": seed, "model": "m", "test_at_best": sc(best), "test_at_last": sc(last), "selection_split": "TEST" if protocol == "theirs" else "DEV",
                "leaked_frac_of_test": 0.13, "exact_duplicate_frac_of_test": 0.05, "test_at_best_leaked": sc(best + 0.01), "test_at_best_non_leaked": sc(best - 0.02),
                "gpu": "A100", "code_revision": "abc", "torch": "2", "runtime_s": 60, "skipped_len_mismatch": 0}
    monkeypatch.setattr(s, "RUNS", tmp_path)
    monkeypatch.setattr(s, "OUT", tmp_path / "out.md")
    for i in range(5):
        (tmp_path / f"theirs_seed{i}.json").write_text(json.dumps(run("theirs", i, 0.953, 0.95)))
        (tmp_path / f"clean_seed{i}.json").write_text(json.dumps(run("clean", i, 0.94, 0.93)))
    s.main()
    txt = (tmp_path / "out.md").read_text()
    assert "COMPLETE" in txt and "0.953" in txt and "Leaked vs non-leaked" in txt and "NOT our final NER model" in txt


def test_bundles_match_split_and_roundtrip(tmp_path):
    import bundle_gold_packs as b
    d = packs.D
    if not (d / "Kush_all_20.json").exists():
        pytest.skip("packs not generated on this machine")
    for who in ("Kush", "Parv"):
        bundle = json.loads((d / f"{who}_all_20.json").read_text())
        assert bundle["n_recipes"] == len(bundle["recipes"]) == 20 and all(packs.pristine(r) for r in bundle["recipes"])
        per = {r["recipe_id"]: r for r in bundle["recipes"]}
        for f in (d / "_split" / who).glob("*.json"):
            assert json.loads(f.read_text()) == per[f.name.split(".")[0]]
    k, p = json.loads((d / "Kush_all_20.json").read_text()), json.loads((d / "Parv_all_20.json").read_text())
    assert [packs.raw_hash(r) for r in k["recipes"]] == [packs.raw_hash(r) for r in p["recipes"]]
    assert b.D == d
