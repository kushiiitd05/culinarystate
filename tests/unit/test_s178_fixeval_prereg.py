"""S178 FIX-EVAL: SCI-B P1 and P2 on the 07.A-R1 amendment draft, as synthetic demonstrations with the project's own scorer code.

P1 (i): reviewer 2 copies reviewer 1's 10 judgement columns and blanks the reasons. The old rule (IDENTICAL_JUDGEMENTS) gives
NOT_COUNTED; Option A's three new copy checks all pass. No check on the judgement columns can separate that copy from an
honest perfect agreement, because the judgement columns are identical in both cases.
P1 (ii): reviewer 1 all CORRECT, reviewer 2 SHOULD_BE_AMBIGUOUS on 5 conditions in 5 fields, adjudicated to 0 defects. The
signed R-06 (pooled kappa >= 0.80) FAILS (kappa = 0.0); Option A (bootstrap AC1 lower bound >= 0.95, critical-field rule,
co-gate) PASSES. Option A is therefore a loosening of R-06 in this region.
P2: the co-gate counts "at most 1 of 100" / "at most 4 of 100" hold for n = 100 only.
"""
from __future__ import annotations

import re

import pytest
from scipy.stats import beta

from culinarystate.evidence import condition_agreement as CA
from tests.unit.test_s178_analysis_helpers import ROOT

AMEND = ROOT / "reports/step07/07A_R1_preregistration_AMENDMENT_S178_DRAFT.md"
CRIT_A = (*CA.CRITICAL, "duration_judgement", "temperature_value_judgement")          # Option A item 4 critical set


def _norm(t: str) -> str:
    return re.sub(r"[\W_]+", " ", (t or "").lower()).strip()


def option_a_copy_checks(A: dict, B: dict, *, receipts, signatures, detected: dict[str, int]) -> list[str]:
    """Option A item 2 as written in the amendment (reference implementation for this demonstration)."""
    probs = []
    if not all(t > max(signatures) for t in receipts):
        probs.append("RECEIPT_BEFORE_SIGNATURE")
    same = sum(1 for i in A if len(_norm(A[i]["reason_if_not_correct"])) >= 15
               and _norm(A[i]["reason_if_not_correct"]) == _norm(B[i]["reason_if_not_correct"]))
    if same >= 3:
        probs.append("REASON_OVERLAP")
    probs += [f"PLANTED_{w}" for w, k in detected.items() if k < 8]
    return probs


def _reviewer(seed: int) -> dict:
    out = {}
    for n in range(1, 101):
        row = {f: "CORRECT" for f in CA.FIELDS}
        if n % 9 == seed:
            row["duration_judgement"] = "WRONG_VALUE"
        row.update(overall_judgement="ACCEPT", reason_if_not_correct=f"reviewer {seed} wrote this reason for row {n}" if n % 9 == seed else "")
        out[f"CA-{n:03d}"] = row
    return out


def _judgement_view(P: dict) -> list:
    return [[P[i][c] for c in (*CA.FIELDS, "overall_judgement")] for i in sorted(P)]


def test_judgement_only_copy_passes_the_three_new_checks_and_only_identical_judgements_catches_it():
    A = _reviewer(1)
    B = {i: {**r, "reason_if_not_correct": ""} for i, r in A.items()}                  # judgement-only copy
    issued = {i: {"audit_id": i} for i in A}
    A = {i: {**r, "audit_id": i} for i, r in A.items()}
    B = {i: {**r, "audit_id": i} for i, r in B.items()}
    old = CA._provenance(issued, A, B, sorted(A))
    assert old == ["IDENTICAL_JUDGEMENTS"]                                             # old rule: NOT_COUNTED
    new = option_a_copy_checks(A, B, receipts=[3, 4], signatures=[1, 2], detected={"A": 9, "B": 9})
    assert new == []                                                                   # all three new checks pass the copy
    honest = {i: {**r, "reason_if_not_correct": ("independent wording, row " + i) if r["reason_if_not_correct"] else ""}
              for i, r in A.items()}                                                   # an honest pair that agrees everywhere
    assert CA._provenance(issued, A, honest, sorted(A)) == ["IDENTICAL_JUDGEMENTS"]   # the F-05 cost of the old rule
    assert _judgement_view(B) == _judgement_view(honest)                               # indistinguishable on judgements


def _paradox():
    ids = [f"CA-{i:03d}" for i in range(1, 101)]
    A = {i: {f: "CORRECT" for f in CA.FIELDS} for i in ids}
    B = {i: {f: "CORRECT" for f in CA.FIELDS} for i in ids}
    for k, f in enumerate(CA.FIELDS[:5]):                                              # 5 conditions, 5 fields
        B[ids[k * 7]][f] = "SHOULD_BE_AMBIGUOUS"
    return ids, A, B


def cp_lower_defect_free(x: int, n: int) -> float:
    return float(beta.ppf(0.05, n - x, x + 1))


def test_option_a_passes_a_pattern_the_signed_r06_fails():
    ids, A, B = _paradox()
    a, b = CA._codes(A, ids), CA._codes(B, ids)
    kappa = CA.cohen_kappa(a, b)
    assert kappa == pytest.approx(0.0, abs=1e-12)                                      # R-06: pooled kappa >= 0.80 -> FAIL
    lo, _ = CA._bootstrap(A, B, ids)
    assert lo >= 0.95 and round(lo, 3) == 0.990                                         # Option A item 3 passes
    for f in CRIT_A:                                                                   # Option A item 4 passes
        st, dis = CA._field([A[i][f] for i in ids], [B[i][f] for i in ids])
        assert st["ac1"] >= 0.80 and st["exact_agreement"] >= 0.90 and max(dis.values(), default=0) < 3
    assert cp_lower_defect_free(0, 100) >= 0.95                                        # co-gate with 0 adjudicated defects
    issued = {i: {"audit_id": i} for i in ids}
    A2 = {i: {**A[i], "audit_id": i, "overall_judgement": "ACCEPT"} for i in ids}
    B2 = {i: {**B[i], "audit_id": i, "overall_judgement": "ACCEPT"} for i in ids}
    assert CA._provenance(issued, A2, B2, ids) == []                                   # A-keep's copy rule does not fire: A-keep PASSES too


@pytest.mark.parametrize("n,crit,anyf", [(100, 1, 4), (120, 1, 6)])
def test_co_gate_counts_depend_on_n(n, crit, anyf):
    assert max(x for x in range(n) if cp_lower_defect_free(x, n) >= 0.95) == crit
    assert max(x for x in range(n) if cp_lower_defect_free(x, n) >= 0.90) == anyf


def test_amendment_text_carries_the_corrections():
    t = AMEND.read_text(encoding="utf-8")
    head = t[:t.index("## 0.")]
    assert "Revision S178-FIX-EVAL" in head
    assert "three stronger copy" not in t
    assert "does not catch a judgement-only copy" in t
    assert "LOOSENING" in t and "kappa 0.0" in t
    row = next(line for line in t.splitlines() if line.startswith("| D-07A-1 |"))
    assert row.rstrip().endswith("| **B** |")                                          # the non-loosening AI recommendation
    assert "A-keep also PASSES" in t
    assert "at most 1 of 100)" not in t and "at most 4 of 100)" not in t               # P2: counts stated per n
    assert "n = 120" in t and "6 of 120" in t
