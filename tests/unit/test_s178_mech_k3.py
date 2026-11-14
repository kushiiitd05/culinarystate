"""Kleene K3 core of the mechanism screen (S178 lane MECH): exhaustive truth tables and verdict properties.

Synthetic inputs only; passing says the logic is the strong Kleene logic the acceptance asks for, nothing about food."""
from __future__ import annotations

import itertools

import pytest

from culinarystate.mechanism import mech_k3 as K
from culinarystate.mechanism.mech_k3 import FALSE, TRUE, UNKNOWN

ORDER = {FALSE: 0, UNKNOWN: 1, TRUE: 2}           # strong Kleene: AND = min, OR = max over F < U < T
INV = {v: k for k, v in ORDER.items()}


def ref_and(vs):
    return INV[min(ORDER[v] for v in vs)] if vs else TRUE


def ref_or(vs):
    return INV[max(ORDER[v] for v in vs)] if vs else FALSE


def c(value, key="PRE01", basis=None, reason="R"):
    if basis is None:
        basis = K.NO_BASIS if value == UNKNOWN else "REFERENCE_SR"
    return K.Conjunct(key, "PRECONDITION", value, reason, basis)


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_and_or_match_strong_kleene_exhaustively(n):
    for vs in itertools.product(K.VALUES, repeat=n):
        assert K.k_and(vs) == ref_and(vs)
        assert K.k_or(vs) == ref_or(vs)
        assert K.k_not(K.k_and(vs)) == K.k_or([K.k_not(v) for v in vs])       # De Morgan holds in K3


def test_named_cases_of_the_acceptance():
    assert K.k_and([FALSE, UNKNOWN]) == FALSE        # false AND unknown = false
    assert K.k_and([TRUE, UNKNOWN]) == UNKNOWN       # true AND unknown = unknown
    assert K.k_or([TRUE, UNKNOWN]) == TRUE
    assert K.k_or([FALSE, UNKNOWN]) == UNKNOWN
    assert K.k_not(UNKNOWN) == UNKNOWN
    assert K.k_or_or_unknown([]) == UNKNOWN          # no evidence for a disjunction is UNKNOWN, never FALSE


def test_bad_values_are_errors_not_verdicts():
    for bad in ("true", None, "", "MAYBE"):
        with pytest.raises(K.K3Error):
            K.k_and([bad])
    with pytest.raises(K.K3Error):
        K.Conjunct("PRE01", "PRECONDITION", TRUE, "R", K.NO_BASIS)     # a decided conjunct needs a basis
    with pytest.raises(K.K3Error):
        K.Conjunct("PRE01", "PRECONDITION", UNKNOWN, "", K.NO_BASIS)    # an UNKNOWN conjunct needs a reason


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_combine_exhaustive_l1(n):
    for vs in itertools.product(K.VALUES, repeat=n):
        cs = [c(v, f"PRE{i:02d}", reason=f"R{i}") for i, v in enumerate(vs)]
        v = K.combine(cs, "L1")
        expect = {TRUE: K.POSSIBLE, FALSE: K.NOT_POSSIBLE, UNKNOWN: K.UNDECIDED}[ref_and(vs)]
        assert v.verdict == expect
        if UNKNOWN in vs:
            assert v.verdict != K.POSSIBLE                       # an UNKNOWN conjunct never yields POSSIBLE ...
            if v.verdict == K.NOT_POSSIBLE:
                assert FALSE in vs                               # ... nor NOT_POSSIBLE unless another conjunct decides
        if v.verdict == K.NOT_POSSIBLE:
            first_false = next(i for i, x in enumerate(vs) if x == FALSE)
            assert v.item_key == f"PRE{first_false:02d}" and v.reason == f"R{first_false}"
        if v.verdict == K.UNDECIDED:
            first_unknown = next(i for i, x in enumerate(vs) if x == UNKNOWN)
            assert v.item_key == f"PRE{first_unknown:02d}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_refining_an_unknown_never_flips_a_decided_verdict(n):
    for vs in itertools.product(K.VALUES, repeat=n):
        base = K.combine([c(v, f"PRE{i:02d}") for i, v in enumerate(vs)], "L1").verdict
        for i, v in enumerate(vs):
            if v != UNKNOWN:
                continue
            for r in (TRUE, FALSE):
                ws = list(vs)
                ws[i] = r
                ref = K.combine([c(w, f"PRE{j:02d}") for j, w in enumerate(ws)], "L1").verdict
                if base != K.UNDECIDED:
                    assert ref == base


def test_l2_false_never_excludes_and_l2_never_enters_l1():
    l2_false = c(FALSE, "CG01", basis="SCENARIO", reason="BELOW_WINDOW")
    v = K.combine([c(TRUE), l2_false], "L2:TYPICAL")
    assert v.verdict == K.UNDECIDED and v.reason == "L2_CANNOT_EXCLUDE__BELOW_WINDOW"
    v = K.combine([c(FALSE, "PRE01"), l2_false], "L2:INTENSE")          # an L1 FALSE still decides in an L2 view
    assert v.verdict == K.NOT_POSSIBLE and v.item_key == "PRE01" and v.support_layer == "L1"
    for basis in K.L2_BASES:
        with pytest.raises(K.K3Error):
            K.combine([c(TRUE, basis=basis)], "L1")
    v = K.combine([c(TRUE), c(TRUE, "CG01", basis="SCENARIO")], "L2:GENTLE")
    assert v.verdict == K.POSSIBLE and v.support_layer == "L2"
    assert K.combine([c(TRUE)], "L2:GENTLE").support_layer == "L1"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_combine_exhaustive_with_l2_bases(n):
    """Over every value x basis-class assignment: NOT_POSSIBLE iff some L1-basis conjunct is FALSE."""
    for vs in itertools.product(K.VALUES, repeat=n):
        for l2 in itertools.product((False, True), repeat=n):
            cs = [c(v, f"PRE{i:02d}", basis=(K.NO_BASIS if v == UNKNOWN else ("SCENARIO" if l2[i] else "TEXT_STATED")))
                  for i, v in enumerate(vs)]
            v = K.combine(cs, "L2:TYPICAL")
            l1_false = any(x == FALSE and not l2[i] for i, x in enumerate(vs))
            assert (v.verdict == K.NOT_POSSIBLE) == l1_false
            assert (v.verdict == K.POSSIBLE) == all(x == TRUE for x in vs)


def test_flags_are_carried_and_sorted():
    v = K.combine([K.Conjunct("PRE01", "PRECONDITION", TRUE, "R", "REFERENCE_SR", ("B",))], "L1", ["A"])
    assert v.flags == ("A", "B")


def test_or_over_members():
    P = K.combine([c(TRUE)], "L1")
    N = K.combine([c(FALSE)], "L1")
    U = K.combine([c(UNKNOWN)], "L1")
    for combo in itertools.product((P, N, U), repeat=3):
        got = K.k_or_verdicts(list(combo), "L1").verdict
        verdicts = [x.verdict for x in combo]
        if K.POSSIBLE in verdicts:
            assert got == K.POSSIBLE
        elif all(x == K.NOT_POSSIBLE for x in verdicts):
            assert got == K.NOT_POSSIBLE
        else:
            assert got == K.UNDECIDED
    with pytest.raises(K.K3Error):
        K.k_or_verdicts([], "L1")


def test_unknown_view_is_an_error():
    with pytest.raises(K.K3Error):
        K.combine([c(TRUE)], "L3")
