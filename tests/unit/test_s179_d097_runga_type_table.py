"""D-097: structural Rung A -> Gold event-type mapping and count-match type table (T3-C11-R1, T3-C17-R2)."""
from __future__ import annotations

from collections import Counter
from types import SimpleNamespace as NS

import pytest

from culinarystate.evaluation import runga_typed_vs_gold as R


def ev(consumes=(), produces=(), discards=()):
    return NS(consumes=tuple(consumes), produces=tuple(produces), discards=tuple(discards))


@pytest.mark.parametrize("e,want", [
    (ev(["a"], [], ["b"]), "Discard"),             # discards wins first
    (ev(["a", "b"], ["c"]), "Merge"),
    (ev(["a"], ["b", "c"]), "Split"),
    (ev(["a"], ["b"]), "Transform"),
    (ev([], []), None),                            # 0 consumes -> abstain
    (ev(["a", "b"], ["c", "d"]), None),           # many -> many -> abstain
    (ev(["a", "b"], []), None),
])
def test_structural_mapping(e, want):
    assert R.map_event(e) == want


def test_mapping_never_predicts_unsignalled_types():
    assert not {"Transfer", "Reserve", "Recombine"} & set(R.PREDICTABLE)


def test_type_table_count_match_and_zero_recall_for_unpredicted():
    per = [(Counter(Merge=2, Transform=1, Transfer=1), Counter(Merge=1, Transform=2)),
           (Counter(Merge=1), Counter(Merge=1, Split=1))]
    t = R.type_table_from_counts(per, n_boot=200, seed="t", unmapped=3)
    rows = t["types"]
    assert rows["Merge"] == pytest.approx({**rows["Merge"], "gold": 3, "pred": 2, "matched": 2})
    assert rows["Merge"]["precision"] == 1.0 and rows["Merge"]["recall"] == pytest.approx(0.6667, abs=1e-4)
    assert rows["Transfer"]["pred"] == 0 and rows["Transfer"]["recall"] == 0.0
    assert rows["Transfer"]["precision"] is None
    assert rows["Split"]["gold"] == 0 and rows["Split"]["precision"] == 0.0
    assert t["unmapped_candidate_events"] == 3
    # recipe 1: Merge min(2,1)=1, Transform min(1,2)=1; recipe 2: Merge 1 -> tp 3; pred 5, gold 5
    assert t["pooled"]["tp"] == 3 and t["pooled"]["fp"] == 2 and t["pooled"]["fn"] == 2
    lo, hi = t["pooled"]["precision_ci95"]
    assert 0 <= lo <= t["pooled"]["precision"] <= hi <= 1


def test_bootstrap_is_deterministic():
    per = [(Counter(Merge=2), Counter(Merge=1)), (Counter(Merge=1), Counter(Merge=2))]
    a = R.type_table_from_counts(per, n_boot=100, seed="x", unmapped=0)
    b = R.type_table_from_counts(per, n_boot=100, seed="x", unmapped=0)
    assert a == b


def test_empty_set_refused():
    with pytest.raises(ValueError):
        R.type_table_from_counts([], n_boot=10, seed="x", unmapped=0)
