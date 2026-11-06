"""S168: P1b draw (P1b amendment proposal; D-069/D-070). Synthetic repository only.

P1b uses the same signed algorithm with wave "P1b" in the seed, a human-chosen subset of P1's cells, and every
recipe and group of earlier waves excluded. It is refused unless the signed record authorises the wave; P2 stays
refused. P1 behaviour is unchanged.
"""
import csv

import pytest

from culinarystate.annotation import pilot_real as R
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_t19rp", Path(__file__).with_name("test_step19_real_pilot.py"))
_T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_T)
codes, draw, make_root, mutate, record_path = _T.codes, _T.draw, _T.make_root, _T.mutate, _T.record_path

OUT = "registry/recipe_semantics/deep_gold_pilot_v1"


def _draw_p1b(root, cells=("P1-1", "P1-3", "P1-5"), prior=None):
    out = root / OUT
    return R.draw_wave(record_path(root), root / "frame/frame.csv", root / "frame/strata.csv", out_dir=out,
                       root=root, wave="P1b", cells=list(cells), exclude_manifests=[prior or out / "manifest_P1.csv"])


def test_p1b_is_refused_until_the_record_authorises_it(tmp_path):
    root = make_root(tmp_path)
    assert "H5_WAVE_NOT_AUTHORISED" in codes(root, wave="P1b")
    assert "WAVE_P2_NOT_SUPPORTED" not in codes(root, wave="P1b")
    assert "WAVE_P2_NOT_SUPPORTED" in codes(root, wave="P2")


def test_p1b_excludes_every_p1_recipe_and_group_and_uses_its_own_seed(tmp_path):
    root = make_root(tmp_path, n_per_cell=40)
    p1 = draw(root)
    mutate(root, lambda r: r["human_start_authorization"].update(waves=["P1", "P1b"]))
    res = _draw_p1b(root)
    p1_ids = {r["recipe_id"] for r in p1["rows"]}
    p1_groups = {r["group_key"] for r in p1["rows"]}
    rows = res["rows"]
    assert not {r["recipe_id"] for r in rows} & p1_ids and not {r["group_key"] for r in rows} & p1_groups
    assert {r["cell_id"] for r in rows} == {"P1-1", "P1-3", "P1-5"} and all(r["wave"] == "P1b" for r in rows)
    assert sum(r["role"] == "PRIMARY" for r in rows) == 3 and res["seed_hex"] != p1["seed_hex"]
    man = root / OUT / "manifest_P1b.csv"
    assert man.exists() and (root / OUT / "manifest_P1b.csv.sha256").exists()
    assert [r["wave"] for r in csv.DictReader(man.open())] == ["P1b"] * len(rows)


def test_p1b_needs_the_prior_manifest_and_valid_cells(tmp_path):
    root = make_root(tmp_path, n_per_cell=40)
    draw(root)
    mutate(root, lambda r: r["human_start_authorization"].update(waves=["P1", "P1b"]))
    with pytest.raises(R.PilotGateError, match="PRIOR_MANIFEST"):
        _draw_p1b(root, prior=root / OUT / "missing.csv")
    with pytest.raises(R.PilotGateError, match="CELLS"):
        _draw_p1b(root, cells=("P1-9",))
    with pytest.raises(R.PilotGateError, match="CELLS"):
        _draw_p1b(root, cells=())


def test_p1_draw_is_unchanged(tmp_path):
    a, b = make_root(tmp_path / "a"), make_root(tmp_path / "b")
    ra = draw(a)
    rb = R.draw_wave(record_path(b), b / "frame/frame.csv", b / "frame/strata.csv", out_dir=b / OUT, root=b, wave="P1")
    assert [(r["recipe_id"], r["role"]) for r in ra["rows"]] == [(r["recipe_id"], r["role"]) for r in rb["rows"]]
    assert ra["seed_hex"] == rb["seed_hex"]
