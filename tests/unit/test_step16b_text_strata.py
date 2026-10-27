"""Step 16b text strata: deterministic, id-exact, Y/N only, text-free, inputs untouched, regexes behave."""
import csv
import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("ts16b", ROOT / "tools/step16b_text_strata.py")
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)

INPUTS = [ts.FRAME, ts.BASE, ts.FOODCOM, ts.WIKI, ts.A1_RAW, ts.A1_PROC]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    d = tmp_path_factory.mktemp("o")
    before = {p: sha(ROOT / p) for p in INPUTS}
    a, b = d / "a.csv", d / "b.csv"
    assert ts.main(["--out", str(a)]) == 0
    assert ts.main(["--out", str(b)]) == 0
    return a, b, before


def test_deterministic_byte_identical(run):
    a, b, _ = run
    assert a.read_bytes() == b.read_bytes()


def test_committed_output_matches_rerun(run):
    assert (ROOT / ts.OUT).read_bytes() == run[0].read_bytes()


def test_ids_equal_frame_exactly(run):
    with open(run[0]) as fh:
        ids = [r["recipe_id"] for r in csv.DictReader(fh)]
    with open(ROOT / ts.FRAME) as fh:
        fids = [r["recipe_id"] for r in csv.DictReader(fh)]
    assert ids == fids and len(set(ids)) == len(ids)


def test_only_yn_na_and_no_text_columns(run):
    with open(run[0]) as fh:
        rd = csv.DictReader(fh)
        assert rd.fieldnames == ["recipe_id", "baking", "drain_discard", "reserve_split", "reserve_split_v2", "multi_component"]
        for r in rd:
            assert all(r[k] in {"Y", "N", "NA"} for k in ts.FLAGS)


def test_inputs_unchanged(run):
    assert {p: sha(ROOT / p) for p in INPUTS} == run[2]


def test_regexes_fire_and_not():
    f = ts.flags_for(["Preheat the OVEN.", "Drain well, then discard the water."],
                     ["1 cup flour", "Divide the dough"])
    assert f == {"baking": "Y", "drain_discard": "Y", "reserve_split": "Y", "reserve_split_v2": "Y", "multi_component": "N"}
    g = ts.flags_for(["Make the sauce for the sauce base."], ["2 eggs"])
    assert g["multi_component"] == "Y" and g["baking"] == "N"
    n = ts.flags_for(["Stir gently.", "Serve with a baked potato? no: bakery"], ["1 onion", "salt"])
    assert n == {k: "N" for k in ts.FLAGS}      # 'baked' / 'bakery' / 'ovens' do not match \b(bake|oven)\b
    assert ts.flags_for(["Cover the oven"], [])["baking"] == "Y"
    assert ts.flags_for(["strainer"], [])["drain_discard"] == "N"
    assert ts.flags_for(["Set aside."], [])["reserve_split"] == "Y"
    assert ts.flags_for(["for the marinade, mix"], [])["multi_component"] == "Y"


def test_reserv_quirk_kept_verbatim():
    # \b(reserv|...)\b needs a boundary right after "reserv": "reserve"/"reserved" do NOT match (verbatim from make_gold_batch.py)
    assert ts.flags_for(["Reserve half."], [])["reserve_split"] == "N"
    assert ts.flags_for(["Keep the remaining sauce."], [])["reserve_split"] == "Y"


def test_missing_text_is_na_not_n():
    assert ts.flags_for([], []) == {k: "NA" for k in ts.FLAGS}
    assert ts.flags_for(None, None) == {k: "NA" for k in ts.FLAGS}


def test_reserve_split_v2_fixes_the_boundary_quirk_and_keeps_v1():
    # D-038: v1 column stays verbatim (comparability); v2 also matches reserve/reserved/reserving.
    for text in ("Reserve half.", "Add the reserved liquid.", "Reserving 1 cup of water."):
        f = ts.flags_for([text], [])
        assert f["reserve_split"] == "N" and f["reserve_split_v2"] == "Y"
    assert ts.flags_for(["Keep the remaining sauce."], [])["reserve_split_v2"] == "Y"
    assert ts.flags_for(["Stir well."], [])["reserve_split_v2"] == "N"
    assert ts.flags_for([], [])["reserve_split_v2"] == "NA"
