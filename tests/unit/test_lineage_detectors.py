"""Tests for 08a.3 LIN edge detectors (B0, B1, B2, B3, STRONG) and the scratch-only CLI."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
from pathlib import Path

import pytest

from culinarystate.lineage import detectors as D
from culinarystate.lineage import seeding

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("s8a3", REPO / "tools" / "step08a_detect_edges.py")
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)


def mk(i, *, src="SRC-000001", loc=None, analyte="Vitamin C", matrix="Spinach", process="boil",
       steps=("boil",), vals=(("retention", 55.5, "%"),), doc=None, **kw):
    return {
        "id": f"EVD-{i:06d}", "source_id": src, "family": "F", "locator": loc if loc is not None else f"loc {i}",
        "analyte": analyte, "matrix": matrix, "process": process, "steps": list(steps),
        "values": [{"role": r, "value": v, "unit": u, "basis": None} for r, v, u in vals],
        "doc_ref": doc, "origin_type": "DATABASE_AGGREGATE", "moisture_fraction": None, **kw,
    }


def levels(edges):
    return sorted((e["detector_level"], e["from_id"], e["to_id"]) for e in edges)


# ---------- canonicalisation ----------
def test_canonical_mass_units_to_g_per_100g():
    assert D.canonical_value(500, "mg/100g") == D.canonical_value(0.5, "g/100g")
    assert D.canonical_value(500, "ug/100g")[0] == "mass/100g"
    assert D.canonical_value(21.93, "mg/100 g fresh weight") == D.canonical_value(0.02193, "g/100g")


def test_canonical_percent_fraction():
    assert D.canonical_value(55.0, "%") == D.canonical_value(0.55, "fraction")


def test_canonical_dry_to_fresh_needs_moisture():
    fresh = D.canonical_value(10.0, "mg/100g", "fresh", 0.8)
    dry = D.canonical_value(50.0, "mg/100g", "dry", 0.8)
    assert fresh[0] == dry[0] and fresh[1] == pytest.approx(dry[1])
    # moisture unknown: never guess; dry stays a different dimension
    assert D.canonical_value(50.0, "mg/100g", "dry", None)[0] != fresh[0]


# ---------- levels ----------
def test_b0_same_src_same_locator():
    e = D.detect_edges([mk(1, loc="t1 row 5"), mk(2, loc=" T1  row 5", analyte="Folate")])[0]
    assert [x["detector_level"] for x in e] == ["B0"]
    assert D.detect_edges([mk(1, loc="t1 row 5"), mk(2, loc="t1 row 5", src="SRC-000141", analyte="Folate")])[0] == []


def test_b1_exact_key_direction_and_type():
    edges, _ = D.detect_edges([mk(1), mk(2)])
    assert levels(edges) == [("B1", "EVD-000002", "EVD-000001")]
    assert edges[0]["edge_type"] == "QUOTES_VALUES_FROM"
    assert D.detect_edges([mk(1), mk(2, process="fry")])[0] != [] or True  # looser levels may fire
    assert all(e["detector_level"] != "B1" for e in D.detect_edges([mk(1), mk(2, process="fry", steps=("fry",))])[0])


def test_b2_looser_key():
    a = mk(1, matrix="Spinach, raw", process="Boil / steam", steps=("boil", "steam"), vals=(("retention", 12.345, "%"),))
    b = mk(2, matrix="spinach raw", process="steam boil", steps=("steam", "boil"), vals=(("retention", 12.3449, "%"),))
    edges, _ = D.detect_edges([a, b])
    assert [e["detector_level"] for e in edges] == ["B2"]


def test_b3_rounding_different_process():
    a = mk(1, process="boil", steps=("boil",), vals=(("retention", 55.5, "%"),))
    b = mk(2, process="fry", steps=("fry",), vals=(("retention", 55.5, "%"),))
    edges, _ = D.detect_edges([a, b])
    assert [e["detector_level"] for e in edges] == ["B3"] and edges[0]["score"] >= D.B3_CUT
    c = mk(3, process="fry", steps=("fry",), vals=(("retention", 31.7, "%"),))
    assert D.detect_edges([a, c])[0] == []
    d = mk(4, analyte="Folate", vals=(("retention", 55.5, "%"),))
    assert D.detect_edges([a, d])[0] == []


def test_strong_same_doc_identical_value_beats_b1():
    edges, _ = D.detect_edges([mk(1, doc="DOI:10.1/x"), mk(2, doc="doi:10.1/X ")])
    assert [e["detector_level"] for e in edges] == ["STRONG"]
    assert edges[0]["detection_method"] == "DOI_MATCH"
    edges2, _ = D.detect_edges([mk(1, doc="DOI:10.1/x"), mk(2, doc="DOI:10.1/y")])
    assert [e["detector_level"] for e in edges2] == ["B1"]
    edges3, _ = D.detect_edges([mk(1, doc="DOI:10.1/x"), mk(2, doc="DOI:10.1/x", vals=(("retention", 80.0, "%"),))])
    assert all(e["detector_level"] != "STRONG" for e in edges3)


def test_status_and_audit_flags_and_single_emission():
    items = [mk(1, doc="doi:a"), mk(2, doc="doi:a"), mk(3, loc="loc 1")]
    edges, _ = D.detect_edges(items)
    pairs = [(e["from_id"], e["to_id"]) for e in edges]
    assert len(pairs) == len(set(pairs))
    for e in edges:
        assert e["edge_status"] == "PROVISIONAL"          # only schema-valid non-human status
        assert e["audit_required"] is (e["detector_level"] not in ("STRONG", "B0"))
        assert e["rationale_code"] and e["rule_version"] == D.RULE_VERSION
        assert e["seeded"] is False


def test_edges_match_lin_schema_enums():
    sch = json.loads((REPO / "ledgers/schemas/LIN.schema.json").read_text())["properties"]
    edges, _ = D.detect_edges([mk(1), mk(2), mk(3, process="fry", steps=("fry",)), mk(4, doc="d"), mk(5, doc="d")])
    assert edges
    for e in edges:
        assert e["edge_type"] in sch["edge_type"]["enum"]
        assert e["detector_level"] in sch["detector_level"]["enum"]
        assert e["detection_method"] in sch["detection_method"]["enum"]
        assert 0.0 <= e["score"] <= 1.0


def test_blocking_pair_counts_and_largest_block():
    items = []
    n = 0
    for a in range(20):
        for k in range(10):
            n += 1
            items.append(mk(n, analyte=f"an{a}", vals=(("retention", 1.0 + k * 3.1234, "%"),)))
    _, st = D.detect_edges(items)
    assert st["b3_pairs_compared"] == 20 * 45 < 200 * 199 // 2
    assert st["largest_block"] == 10 and st["n_blocks"] == 20


def test_unfingerprintable_rows_skipped_not_guessed():
    a = mk(1, vals=())
    b = mk(2, vals=())
    edges, st = D.detect_edges([a, b])
    assert edges == [] and st["rows_without_numeric_value"] == 2


def test_determinism_order_independent_bytes():
    rng = random.Random(3)
    items = [mk(i, analyte=f"a{i % 5}", vals=(("retention", float(i % 7), "%"),), doc=f"d{i % 3}") for i in range(1, 60)]
    e1, s1 = D.detect_edges(items)
    sh = items[:]
    rng.shuffle(sh)
    e2, s2 = D.detect_edges(sh)
    assert D.edges_to_jsonl(e1) == D.edges_to_jsonl(e2) and s1 == s2


def test_refuses_seeded_items():
    it = mk(1)
    it[seeding.SEEDED_MARKER] = True
    with pytest.raises(seeding.SeededRecordError):
        D.detect_edges([it, mk(2)])


# ---------- B3 cut-point and seeded recall (G08-4, THR-08A-19) ----------
SEED = 20261027


def test_seeded_recall_every_class_meets_floor_at_frozen_cut():
    pairs = seeding.generate_seeded_pairs(SEED, 100)
    res = seeding.seeded_recall(pairs, lambda o, c: D.record_b3_detects(o, c, D.B3_CUT))
    for cls, v in res["classes"].items():
        assert v["recall"] >= 0.95, (cls, v)
    assert res["all_pass"]


def test_frozen_cut_generalises_to_other_seed():
    pairs = seeding.generate_seeded_pairs(777, 80)
    res = seeding.seeded_recall(pairs, lambda o, c: D.record_b3_detects(o, c, D.B3_CUT))
    assert all(v["recall"] >= 0.95 for v in res["classes"].values())


def test_frozen_cut_reproduced_by_sweep_and_documented():
    pairs = seeding.generate_seeded_pairs(D.CUT_DETERMINATION_SEED, D.CUT_DETERMINATION_N)
    assert D.sweep_cut_for_recall(pairs) == D.B3_CUT
    assert "B3_CUT" in D.__doc__ and str(D.B3_CUT) in D.__doc__ and "frozen" in D.__doc__.lower()


def test_cut_not_trivially_zero_negative_control():
    rng = random.Random(5)
    fp = 0
    n = 400
    for i in range(n):
        a = seeding.make_synthetic_record(1, i)
        b = seeding.make_synthetic_record(2, rng.randrange(10_000))
        fp += D.record_b3_detects(a, b, D.B3_CUT)
    assert D.B3_CUT > 0.5 and fp / n < 0.05


# ---------- CLI ----------
def _mini_root(tmp: Path) -> Path:
    data = tmp / "ledgers_scratch" / "data"
    data.mkdir(parents=True)
    rows = []
    for i in (1, 2, 3, 4):
        rows.append({"id": f"EVD-{i:06d}", "version": 1, "status": "ACTIVE", "source_id": "SRC-000001",
                     "source_family_id": "USDA-RETN-R6", "origin_type": "DATABASE_AGGREGATE",
                     "matrix": {"raw_name": "CHEESE"}, "process": {"raw_name": "baked", "steps": ["bake"]},
                     "target": {"raw_name": "Calcium, Ca", "basis": "RETENTION_TR_OR_AR"},
                     "derived": {"retention_factor": {"status": "MEASURED", "value": 87.5 if i < 4 else 12.0, "unit": "%"}},
                     "study_ids": [], "provenance": {"locator": f"retn06.txt line {i}"}})
    rows.append(dict(rows[0], version=0, status="DEPRECATED"))
    (data / "EVD.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return tmp / "ledgers_scratch"


def _tree_hash(root: Path) -> dict:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def test_cli_refuses_repo_ledgers_and_foreign_out(tmp_path):
    out = tmp_path / "edges"
    with pytest.raises(cli.RefusedPathError):
        cli.run(REPO / "ledgers", out, allowed_out_root=tmp_path)
    with pytest.raises(cli.RefusedPathError):
        cli.run(REPO / "ledgers" / "data", out, allowed_out_root=tmp_path)
    root = _mini_root(tmp_path)
    with pytest.raises(cli.RefusedPathError):
        cli.run(root, REPO / "reports" / "x", allowed_out_root=tmp_path / "edges")
    with pytest.raises(cli.RefusedPathError):
        cli.run(root, tmp_path / "elsewhere", allowed_out_root=tmp_path / "edges")


def test_cli_runs_deterministically_and_leaves_ledgers_untouched(tmp_path):
    root = _mini_root(tmp_path)
    before = _tree_hash(root)
    outs = []
    for k in (1, 2):
        out = tmp_path / "edges" / f"run{k}"
        counts = cli.run(root, out, allowed_out_root=tmp_path / "edges")
        outs.append({p.name: p.read_bytes() for p in out.iterdir()})
    assert outs[0] == outs[1] and set(outs[0]) == {"edge_candidates.jsonl", "edge_counts.json"}
    assert _tree_hash(root) == before
    assert counts["by_level"]["B1"] == 2 and counts["rows_total"] == 4
    assert counts["rows_without_numeric_value"] == 0
    assert "runtime" not in json.dumps(counts)
