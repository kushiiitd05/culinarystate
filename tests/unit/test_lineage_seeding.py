import json

import pytest

from culinarystate.lineage import seeding as S
from culinarystate.lineage.wilson import wilson_lower

CLASSES = ("EXACT_COPY", "UNIT_CONVERSION", "ROUNDING_1_2_SF", "PERCENT_FRACTION", "FRESH_DRY_WEIGHT", "SUBSET_OR_REORDERED", "ONE_CELL_ERROR")


def _orig(i=0):
    return S.make_synthetic_record(seed=1, index=i)


def test_seven_classes_in_order():
    assert S.PERTURBATION_CLASSES == CLASSES


def test_synthetic_record_deterministic_and_unmarked():
    a, b = _orig(3), _orig(3)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert not S.is_seeded(a)
    assert len(a["rows"]) >= 4


@pytest.mark.parametrize("cls", CLASSES)
def test_every_class_marks_copy_and_does_not_mutate_original(cls):
    o = S.make_synthetic_record(1, 1, kind="proportion" if cls == "PERCENT_FRACTION" else "mass")
    snap = json.dumps(o, sort_keys=True)
    c = S.perturb(o, cls, seed=5)
    assert json.dumps(o, sort_keys=True) == snap
    assert S.is_seeded(c) and c["seeded_class"] == cls and c["seeded_from"] == o["record_id"]
    assert c["record_id"] != o["record_id"]


def test_refuse_ledger_write_for_seeded():
    c = S.perturb(_orig(), "EXACT_COPY", seed=1)
    with pytest.raises(S.SeededRecordError):
        S.refuse_if_seeded(c)
    S.refuse_if_seeded(_orig())


def test_exact_copy_rows_identical():
    o = _orig()
    assert S.perturb(o, "EXACT_COPY", seed=1)["rows"] == o["rows"]


def test_unit_conversion_preserves_quantity():
    o = _orig()
    c = S.perturb(o, "UNIT_CONVERSION", seed=2)
    assert [r["unit"] for r in c["rows"]] != [r["unit"] for r in o["rows"]]
    for ro, rc in zip(o["rows"], c["rows"]):
        assert rc["value"] * S.UNIT_FACTORS[(ro["unit"], rc["unit"])] ** -1 == pytest.approx(ro["value"])


def test_rounding_one_or_two_sf():
    o = _orig()
    c = S.perturb(o, "ROUNDING_1_2_SF", seed=3)
    for ro, rc in zip(o["rows"], c["rows"]):
        assert float(f"{rc['value']:.2g}") == rc["value"]
        assert rc["value"] == pytest.approx(ro["value"], rel=0.5)


def test_percent_fraction_roundtrip():
    o = S.make_synthetic_record(seed=1, index=1, kind="proportion")
    c = S.perturb(o, "PERCENT_FRACTION", seed=4)
    for ro, rc in zip(o["rows"], c["rows"]):
        assert (ro["unit"], rc["unit"]) in (("%", "fraction"), ("fraction", "%"))
        f = 100 if ro["unit"] == "fraction" else 0.01
        assert rc["value"] == pytest.approx(ro["value"] * f)


def test_fresh_dry_uses_moisture():
    o = _orig()
    c = S.perturb(o, "FRESH_DRY_WEIGHT", seed=4)
    assert {r["basis"] for r in c["rows"]} != {r["basis"] for r in o["rows"]}
    w = o["moisture_fraction"]
    for ro, rc in zip(o["rows"], c["rows"]):
        k = 1 / (1 - w) if ro["basis"] == "fresh" else (1 - w)
        assert rc["value"] == pytest.approx(ro["value"] * k)


def test_subset_reordered():
    o = _orig()
    c = S.perturb(o, "SUBSET_OR_REORDERED", seed=6)
    ko = {json.dumps(r, sort_keys=True) for r in o["rows"]}
    kc = [json.dumps(r, sort_keys=True) for r in c["rows"]]
    assert set(kc) <= ko and 2 <= len(kc) <= len(ko)
    assert kc != [json.dumps(r, sort_keys=True) for r in o["rows"]][: len(kc)]


def test_one_cell_error_changes_exactly_one_cell():
    for s in range(30):
        o = _orig(s)
        c = S.perturb(o, "ONE_CELL_ERROR", seed=s)
        diffs = [(i, k) for i, (ro, rc) in enumerate(zip(o["rows"], c["rows"])) for k in ro if ro[k] != rc[k]]
        assert len(diffs) == 1 and diffs[0][1] == "value"


def test_generator_counts_and_determinism():
    g1 = S.generate_seeded_pairs(seed=7)
    g2 = S.generate_seeded_pairs(seed=7)
    assert json.dumps(g1, sort_keys=True) == json.dumps(g2, sort_keys=True)
    assert S.generate_seeded_pairs(seed=8) != g1
    for cls in CLASSES:
        assert sum(1 for p in g1 if p["seeded_class"] == cls) == S.MIN_SEEDS_PER_CLASS == 60
    assert len(g1) == 420
    assert all(S.is_seeded(p["copy"]) and not S.is_seeded(p["original"]) for p in g1)
    with pytest.raises(ValueError):
        S.generate_seeded_pairs(seed=1, n_per_class=59)


def test_recall_perfect_and_blind_detectors():
    pairs = S.generate_seeded_pairs(seed=7)
    full = S.seeded_recall(pairs, lambda a, b: True)
    assert set(full["classes"]) == set(CLASSES)
    for v in full["classes"].values():
        assert v["n"] == 60 and v["hits"] == 60 and v["recall"] == 1.0
        assert v["wilson_lower"] == pytest.approx(wilson_lower(60, 60))
        assert v["passes"] is True
    assert full["all_pass"] is True
    none = S.seeded_recall(pairs, lambda a, b: False)
    assert none["all_pass"] is False and none["classes"]["EXACT_COPY"]["recall"] == 0.0


def test_recall_pass_rule_needs_lb_and_point():
    pairs = S.generate_seeded_pairs(seed=7)
    miss = {id(p["copy"]) for p in pairs if p["seeded_class"] == "EXACT_COPY"}
    first_misses = set(list(miss)[:2])
    r = S.seeded_recall(pairs, lambda a, b: id(b) not in first_misses)
    e = r["classes"]["EXACT_COPY"]
    assert e["hits"] == 58 and e["passes"] is False  # LB 0.8864 < 0.90
    one = set(list(miss)[:1])
    e = S.seeded_recall(pairs, lambda a, b: id(b) not in one)["classes"]["EXACT_COPY"]
    assert e["hits"] == 59 and e["passes"] is True


def test_recall_rejects_unmarked_copy():
    with pytest.raises(S.SeededRecordError):
        S.seeded_recall([{"seeded_class": "EXACT_COPY", "original": _orig(), "copy": _orig(1)}], lambda a, b: True)
