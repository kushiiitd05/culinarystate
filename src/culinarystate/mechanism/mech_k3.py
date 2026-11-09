"""Kleene strong three-valued logic (K3) for the mechanism screen (S178 lane MECH, T5-C02-R2). AI_DRAFTED, NON_CITABLE.

Values are TRUE / FALSE / UNKNOWN. ``k_and``: FALSE if any conjunct is FALSE, TRUE if all are TRUE, else UNKNOWN
(false AND unknown = false; true AND unknown = unknown). ``k_or`` is its dual. An empty conjunction is TRUE and an empty
disjunction is FALSE (the identities), so callers that have NO evidence for a disjunction must pass an explicit UNKNOWN
instead of an empty list (``k_or_or_unknown``).

A ``Conjunct`` is one evaluated precondition / gate / inhibitor of a mechanism entry, with the reason code and the basis
that decided it. ``combine`` turns a conjunct list into a verdict for ONE layer view (L1, L2:GENTLE, L2:TYPICAL,
L2:INTENSE; never mixed):

- NOT_POSSIBLE needs a FALSE conjunct whose basis may exclude (Layer 1 text, a physical or process definition, the
  lineage, or measured reference composition). A FALSE conjunct whose basis is a Layer 2 scenario value (SCENARIO,
  MODEL_DERIVED, ASSUMED_DEFAULT) is read as UNKNOWN with reason ``L2_CANNOT_EXCLUDE`` (SSOT v16 DRAFT 285.12, D-077).
- POSSIBLE needs every conjunct TRUE. An UNKNOWN conjunct therefore never yields POSSIBLE, and it yields NOT_POSSIBLE only
  when another conjunct decides (is an admissible FALSE).
- Otherwise UNKNOWN, with the reason of the first undecided conjunct (declaration order: deterministic).

``k_or_verdicts`` combines per-member verdicts of a member-scoped entry (the mechanism is possible in the lot iff it is
possible for SOME member): POSSIBLE if any member is POSSIBLE, NOT_POSSIBLE only if every member is NOT_POSSIBLE.
Nothing here holds a chemistry value.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

TRUE, FALSE, UNKNOWN = "TRUE", "FALSE", "UNKNOWN"
VALUES = (TRUE, FALSE, UNKNOWN)
POSSIBLE, NOT_POSSIBLE, UNDECIDED = "POSSIBLE", "NOT_POSSIBLE", "UNKNOWN"
VERDICTS = (POSSIBLE, NOT_POSSIBLE, UNDECIDED)
VIEWS = ("L1", "L2:GENTLE", "L2:TYPICAL", "L2:INTENSE")
BRACKETS = ("GENTLE", "TYPICAL", "INTENSE")

# bases that may decide FALSE (exclusion): Layer 1 and definitions, lineage, measured reference composition
L1_BASES = frozenset({"TEXT_STATED", "CARRIED_SETPOINT", "CUE", "TEXT_CUE", "PHYSICAL_DEFINITION", "PROCESS_DEFINITION",
                      "CUT_HISTORY", "LINEAGE", "REFERENCE_SR", "MECH_DEFINITION"})
# bases that may only ever add support (TRUE), never exclude
L2_BASES = frozenset({"SCENARIO", "MODEL_DERIVED", "ASSUMED_DEFAULT"})
NO_BASIS = "NONE"
R_L2_CANNOT_EXCLUDE = "L2_CANNOT_EXCLUDE"
R_ALL_TRUE = "ALL_CONJUNCTS_TRUE"


class K3Error(ValueError):
    """A malformed three-valued input (never a verdict)."""


def _check(v: str) -> str:
    if v not in VALUES:
        raise K3Error(f"not a K3 value: {v!r}")
    return v


def k_and(values: Iterable[str]) -> str:
    vs = [_check(v) for v in values]
    if FALSE in vs:
        return FALSE
    return TRUE if all(v == TRUE for v in vs) else UNKNOWN


def k_or(values: Iterable[str]) -> str:
    vs = [_check(v) for v in values]
    if TRUE in vs:
        return TRUE
    return FALSE if all(v == FALSE for v in vs) else UNKNOWN


def k_not(v: str) -> str:
    return {TRUE: FALSE, FALSE: TRUE, UNKNOWN: UNKNOWN}[_check(v)]


def k_or_or_unknown(values: Sequence[str]) -> str:
    """Disjunction that reads 'no evidence at all' (empty input) as UNKNOWN, not FALSE."""
    return k_or(values) if values else UNKNOWN


@dataclass(frozen=True)
class Conjunct:
    """One evaluated item of an entry. ``basis`` says what decided ``value`` (NONE when UNKNOWN)."""

    item_key: str            # PRE01 / CG01 / INH01 (entry item key)
    role: str                # PRECONDITION / GATE / INHIBITOR_ABSENT
    value: str
    reason: str
    basis: str = NO_BASIS
    flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _check(self.value)
        if self.value != UNKNOWN and self.basis not in L1_BASES | L2_BASES:
            raise K3Error(f"{self.item_key}: a decided conjunct needs a known basis, got {self.basis!r}")
        if self.value == UNKNOWN and not self.reason:
            raise K3Error(f"{self.item_key}: an UNKNOWN conjunct needs a reason code")

    @property
    def l2(self) -> bool:
        return self.basis in L2_BASES


@dataclass(frozen=True)
class Verdict:
    verdict: str
    view: str
    reason: str
    item_key: str | None                      # the deciding item (None for POSSIBLE)
    support_layer: str                        # L1 when no L2 value was needed, else L2 (POSSIBLE); L1 for NOT_POSSIBLE
    flags: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS or self.view not in VIEWS:
            raise K3Error(f"bad verdict {self.verdict!r} / view {self.view!r}")


def effective(c: Conjunct, view: str) -> Conjunct:
    """The conjunct as a view may use it: an L2 FALSE never excludes; an L2 value never enters the L1 view."""
    if c.l2 and view == "L1":
        raise K3Error(f"{c.item_key}: Layer 2 basis {c.basis} in the L1 view (layers are never mixed)")
    if c.value == FALSE and c.l2:
        return Conjunct(c.item_key, c.role, UNKNOWN, f"{R_L2_CANNOT_EXCLUDE}__{c.reason}", NO_BASIS, c.flags)
    return c


def combine(conjuncts: Sequence[Conjunct], view: str, flags: Iterable[str] = ()) -> Verdict:
    if view not in VIEWS:
        raise K3Error(f"unknown view {view!r}")
    cs = [effective(c, view) for c in conjuncts]
    extra = tuple(sorted(set(flags) | {f for c in cs for f in c.flags}))
    for c in cs:
        if c.value == FALSE:
            return Verdict(NOT_POSSIBLE, view, c.reason, c.item_key, "L1", extra)
    for c in cs:
        if c.value == UNKNOWN:
            return Verdict(UNDECIDED, view, c.reason, c.item_key, "NONE", extra)
    layer = "L2" if any(c.l2 for c in cs) else "L1"
    return Verdict(POSSIBLE, view, R_ALL_TRUE, None, layer, extra)


def k_or_verdicts(per_member: Sequence[Verdict], view: str) -> Verdict:
    """Lot verdict of a member-scoped entry: POSSIBLE if some member is POSSIBLE, NOT_POSSIBLE only if all are."""
    if not per_member:
        raise K3Error("k_or_verdicts needs at least one (possibly virtual) member")
    for v in per_member:
        if v.verdict == POSSIBLE:
            return v
    if all(v.verdict == NOT_POSSIBLE for v in per_member):
        return per_member[0]
    return next(v for v in per_member if v.verdict == UNDECIDED)
