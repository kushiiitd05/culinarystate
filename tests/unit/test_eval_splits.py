"""DRAFT_PENDING_15_0 -- tests for group-aware evaluation splits (Steps 29/30/34 harness).

Synthetic rows only; no ledger is read. Fractions and seeds below are test inputs,
not pre-registered values. Property tests check that no group value and no
connected component ever appears on two sides of a split.
"""
from __future__ import annotations

import random
from fractions import Fraction

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from culinarystate.evaluation import splits as sp

COLS = ("lineage_group", "study")
FRACS = {"train": Fraction(1, 2), "cal": Fraction(1, 4), "test": Fraction(1, 4)}


def _rows(n_groups: int = 12) -> list[dict]:
    rows = []
    for g in range(n_groups):
        for k in range(3):
            rows.append({"row_id": f"R{g:03d}-{k}", "lineage_group": f"LG{g}", "study": f"ST{g}"})
    return rows


def _split(rows, **over):
    kw = dict(id_column="row_id", group_columns=COLS, role_fractions=FRACS, seed="synthetic-seed",
              remainder_role="train")
    kw.update(over)
    return sp.group_aware_split(rows, **kw)


def _codes(exc) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


# ---------------------------------------------------------------- components

def test_rows_sharing_any_group_value_share_a_component():
    rows = [{"row_id": "a", "lineage_group": "L1", "study": "S1"},
            {"row_id": "b", "lineage_group": "L2", "study": "S1"},   # linked to a by study
            {"row_id": "c", "lineage_group": "L2", "study": "S9"},   # linked to b by lineage
            {"row_id": "d", "lineage_group": "L3", "study": "S3"}]
    comp = sp.group_components(rows, id_column="row_id", group_columns=COLS)
    assert comp["a"] == comp["b"] == comp["c"] != comp["d"]
    assert all(v.startswith("C-") for v in comp.values())


def test_component_keys_do_not_depend_on_row_order():
    rows = _rows()
    shuffled = list(rows)
    random.Random(3).shuffle(shuffled)
    assert (sp.group_components(rows, id_column="row_id", group_columns=COLS)
            == sp.group_components(shuffled, id_column="row_id", group_columns=COLS))


def test_same_value_in_different_columns_does_not_link():
    rows = [{"row_id": "a", "lineage_group": "X", "study": "S1"},
            {"row_id": "b", "lineage_group": "L2", "study": "X"}]
    comp = sp.group_components(rows, id_column="row_id", group_columns=COLS)
    assert comp["a"] != comp["b"]


@pytest.mark.parametrize("bad,code", [
    ({"lineage_group": None}, "GROUP_VALUE_MISSING"),
    ({"lineage_group": ""}, "GROUP_VALUE_MISSING"),
    ({"study": "UNKNOWN"}, "GROUP_VALUE_UNKNOWN"),
    ({"row_id": None}, "ROW_ID_MISSING"),
])
def test_unplaceable_rows_are_refused(bad, code):
    rows = _rows(3)
    rows[0] = {**rows[0], **bad}
    with pytest.raises(sp.SplitRefused) as exc:
        sp.group_components(rows, id_column="row_id", group_columns=COLS)
    assert code in _codes(exc)


def test_duplicate_row_id_and_missing_columns_are_refused():
    rows = _rows(3)
    rows.append(dict(rows[0]))
    with pytest.raises(sp.SplitRefused) as exc:
        sp.group_components(rows, id_column="row_id", group_columns=COLS)
    assert "ROW_ID_DUPLICATE" in _codes(exc)
    with pytest.raises(sp.SplitRefused) as exc:
        sp.group_components(_rows(3), id_column="row_id", group_columns=())
    assert "NO_GROUP_COLUMNS" in _codes(exc)


# ---------------------------------------------------------------- split

def test_split_assigns_every_row_once_and_is_disjoint():
    s = _split(_rows())
    ids = [r for role in s.roles for r in s.rows(role)]
    assert sorted(ids) == sorted(r["row_id"] for r in _rows()) and len(ids) == len(set(ids))
    for col in COLS:
        assert sp.values_on_multiple_roles(s, _rows(), id_column="row_id", column=col) == {}
    assert s.n_components == {"train": 6, "cal": 3, "test": 3}
    assert s.n_rows == {"train": 18, "cal": 9, "test": 9}


def test_split_is_deterministic_and_seed_dependent():
    a, b = _split(_rows()), _split(_rows())
    assert a.assignment == b.assignment and a.sha256() == b.sha256()
    c = _split(_rows(), seed="another-seed")
    assert c.sha256() != a.sha256()


def test_split_requires_explicit_fractions_seed_and_remainder():
    with pytest.raises(TypeError):
        sp.group_aware_split(_rows(), id_column="row_id", group_columns=COLS)  # type: ignore[call-arg]


@pytest.mark.parametrize("over,code", [
    ({"role_fractions": {"train": Fraction(1, 2), "test": Fraction(1, 3)}}, "FRACTIONS_NOT_ONE"),
    ({"role_fractions": {"train": Fraction(1), "test": Fraction(0)}}, "FRACTION_INVALID"),
    ({"role_fractions": {"train": "1/2", "test": "abc"}}, "FRACTION_INVALID"),
    ({"remainder_role": "dev"}, "REMAINDER_ROLE_UNKNOWN"),
    ({"seed": ""}, "SEED_MISSING"),
    ({"role_fractions": {"train": Fraction(19, 20), "test": Fraction(1, 20)}}, "ROLE_EMPTY"),
])
def test_split_refusals(over, code):
    with pytest.raises(sp.SplitRefused) as exc:
        _split(_rows(), **over)
    assert code in _codes(exc)


def test_fraction_strings_are_parsed_exactly():
    s = _split(_rows(), role_fractions={"train": "0.5", "cal": "1/4", "test": "0.25"})
    assert s.n_components == {"train": 6, "cal": 3, "test": 3}


def test_excluded_components_never_enter_any_role():
    rows = _rows()
    comp = sp.group_components(rows, id_column="row_id", group_columns=COLS)
    drop = {comp["R000-0"], comp["R001-0"]}
    s = _split(rows, exclude_components=drop)
    used = {r for role in s.roles for r in s.rows(role)}
    assert not any(comp[r] in drop for r in used)
    assert s.n_excluded_components == 2


def test_manifest_carries_no_row_values_beyond_ids():
    m = _split(_rows()).manifest()
    assert m["rule_id"] == sp.RULE_ID and m["status"].startswith("DRAFT_PENDING")
    assert set(m["n_components"]) == {"train", "cal", "test"}
    assert "LG0" not in repr(m) and "ST0" not in repr(m)


# ---------------------------------------------------------------- grouped k-fold

def test_group_kfold_folds_are_disjoint_and_cover_all_components():
    rows = _rows(10)
    folds = sp.group_kfold(rows, id_column="row_id", group_columns=COLS, n_folds=5, seed="s")
    assert len(folds) == 5
    tests = [set(f.rows("test")) for f in folds]
    assert set().union(*tests) == {r["row_id"] for r in rows}
    assert sum(len(t) for t in tests) == len(rows)
    for f in folds:
        assert sp.values_on_multiple_roles(f, rows, id_column="row_id", column="lineage_group") == {}


@pytest.mark.parametrize("n", [1, 11])
def test_group_kfold_refuses_bad_fold_counts(n):
    with pytest.raises(sp.SplitRefused) as exc:
        sp.group_kfold(_rows(10), id_column="row_id", group_columns=COLS, n_folds=n, seed="s")
    assert "N_FOLDS_INVALID" in _codes(exc)


# ---------------------------------------------------------------- properties

_row_strategy = st.lists(
    st.tuples(st.integers(0, 7), st.integers(0, 7)), min_size=4, max_size=60)


@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(pairs=_row_strategy, seed=st.text(min_size=1, max_size=8))
def test_property_no_group_value_or_component_on_two_sides(pairs, seed):
    rows = [{"row_id": f"r{i}", "lineage_group": f"L{a}", "study": f"S{b}"} for i, (a, b) in enumerate(pairs)]
    comp = sp.group_components(rows, id_column="row_id", group_columns=COLS)
    if len(set(comp.values())) < 2:
        return
    fr = {"train": Fraction(1, 2), "test": Fraction(1, 2)}
    try:
        s = _split(rows, role_fractions=fr, seed=seed)
    except sp.SplitRefused as exc:
        assert all(b.startswith("ROLE_EMPTY") for b in exc.blockers)
        return
    role_of_comp: dict[str, str] = {}
    for rid, role in s.assignment.items():
        assert role_of_comp.setdefault(comp[rid], role) == role
    for col in COLS:
        assert sp.values_on_multiple_roles(s, rows, id_column="row_id", column=col) == {}
    assert sorted(s.assignment) == sorted(r["row_id"] for r in rows)


@settings(max_examples=40, deadline=None)
@given(pairs=_row_strategy, perm_seed=st.integers(0, 10_000))
def test_property_assignment_invariant_to_row_order(pairs, perm_seed):
    rows = [{"row_id": f"r{i}", "lineage_group": f"L{a}", "study": f"S{b}"} for i, (a, b) in enumerate(pairs)]
    shuffled = list(rows)
    random.Random(perm_seed).shuffle(shuffled)
    fr = {"train": Fraction(1, 2), "test": Fraction(1, 2)}
    try:
        a = _split(rows, role_fractions=fr)
    except sp.SplitRefused:
        return
    assert _split(shuffled, role_fractions=fr).assignment == a.assignment
