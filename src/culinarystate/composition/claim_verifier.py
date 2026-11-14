"""Lightweight claim verifier and deterministic template fallback (freeze step 5).

Runs *after* LLM generation. It checks the text against the Claim Packet and, when verification
fails, the caller uses a deterministic template instead of letting an unsupported answer through.
The verifier reads only the packet: it never consults the model, never repairs the text and never
upgrades anything.

What counts as a claim
----------------------
Only numbers that assert something about the target are checked. A number followed by a context
unit (minutes, hours, °C, g, ml, …) is the recipe's own condition, not a retention claim, so
"boiled for 20 minutes" is not treated as an evidence number. Evidence ids are stripped before
scanning so that the digits inside ``EVD-002765`` are never read as a value.

When a caveat must appear in the text
-------------------------------------
Only when the route cannot support a numeric claim (UNKNOWN, CONTEXT_MISMATCH) or when near
evidence is named. A DIRECT answer whose number is cited is already supported, so it is not forced
to recite unrelated UNKNOWNs. ``FROZEN_ROUTER_REASONS`` stays recorded in the packet for audit and
is deliberately not text-required: it is provenance, not a caveat a reader needs.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from culinarystate.composition.claim_packet import NUMERIC

#: A number followed by one of these is a condition, not a claim about the target.
CONTEXT_UNITS = ("minute", "minutes", "min", "mins", "hour", "hours", "hr", "hrs", "second", "seconds",
                 "sec", "secs", "day", "days", "°c", "c", "°f", "f", "degree", "degrees",
                 "g", "kg", "mg", "ml", "l", "litre", "litres", "cup", "cups", "tsp", "tbsp", "step")
#: A number *preceded* by one of these is an index, not a value ("at step 1").
CONTEXT_PREFIXES = ("step", "steps", "stage", "no", "number", "item", "row", "axis", "rung")
_EVD_ID = re.compile(r"\b[A-Z]{3,}-\d{4,}\b")
_NUMBER = re.compile(r"(?<![\w.-])(\d+(?:\.(\d+))?)\s*(%|percent)?\s*([A-Za-z°]+)?")
_EVD_VALUE = re.compile(r"=\s*(-?\d+(?:\.\d+)?)")
_ROUTE_UPGRADE = re.compile(r"\bDIRECT\b|\bdirect(?:ly)?\s+(?:measurement|measured|measures)\b"
                            r"|\bis\s+a\s+direct\b", re.IGNORECASE)
_NOT_KNOWN = re.compile(r"not\s+known|unknown|cannot\s+be\s+determined|no\s+evidence", re.IGNORECASE)
_NO_TRANSFER = re.compile(r"cannot\s+(?:be\s+transferred|have\s+its\s+number\s+transferred)"
                          r"|not\s+transferable|number\s+cannot\s+be\s+(?:used|applied)", re.IGNORECASE)
#: Routes that cannot support a numeric claim, so an answer must say why.
_MUST_EXPLAIN = ("UNKNOWN", "CONTEXT_MISMATCH")


@dataclass(frozen=True)
class Violation:
    code: str
    detail: str


@dataclass(frozen=True)
class VerificationReport:
    violations: tuple[Violation, ...] = field(default=())

    @property
    def ok(self) -> bool:
        return not self.violations

    @property
    def codes(self) -> frozenset[str]:
        return frozenset(v.code for v in self.violations)


def _evidence_numbers(packet: Mapping[str, Any]) -> set[str]:
    out: set[str] = set()
    for v in packet.get("evidence_values") or ():
        for m in _EVD_VALUE.finditer(str(v)):
            out.add(_canon(m.group(1)))
    return out


def _canon(number: str) -> str:
    """Compare numerically, so 95 and 95.0 are the same value."""
    return repr(float(number))


def claimed_numbers(text: str) -> list[tuple[str, int]]:
    """(number, decimals) for every number that asserts something about the target."""
    stripped = _EVD_ID.sub(" ", text)
    out: list[tuple[str, int]] = []
    for m in _NUMBER.finditer(stripped):
        unit = (m.group(4) or "").lower().strip(".,;:")
        if not m.group(3) and unit in CONTEXT_UNITS:
            continue
        prefix = re.search(r"([A-Za-z.]+)\s*$", stripped[:m.start()])
        if not m.group(3) and prefix and prefix.group(1).lower().strip(".") in CONTEXT_PREFIXES:
            continue
        out.append((m.group(1), len(m.group(2) or "")))
    return out


def _axis_words(packet: Mapping[str, Any]) -> list[str]:
    """Readable words for each UNKNOWN axis, used to check a reason was actually stated."""
    words: list[str] = []
    for key in packet.get("unknown_reasons") or {}:
        short = key.split("_", 1)[1] if "_" in key else key
        words.append(short.replace("_", " "))
    compat = packet.get("compatibility") or {}
    for cell in compat.values():
        status = str(cell.get("status", ""))
        if status in ("UNCONFIRMED", "MISMATCH", "UNKNOWN"):
            words.append(cell.get("axis", "").split(" (")[0].lower())
    return [w for w in words if w]


def _states_a_reason(text: str, packet: Mapping[str, Any]) -> bool:
    low = text.lower()
    if any(eid.lower() in low for eid in packet.get("near_evidence_ids") or ()):
        return True
    for word in _axis_words(packet):
        head = word.split("/")[0].split()[0].strip()
        if head and re.search(rf"\b{re.escape(head)}\b", low):
            return True
    return False


def verify(text: str, packet: Mapping[str, Any]) -> VerificationReport:
    """Check one generated answer against its Claim Packet. Never mutates either."""
    bad: list[Violation] = []
    route = packet.get("route", "UNKNOWN")
    allowed = set(packet.get("allowed_claims") or ())
    forbidden = set(packet.get("forbidden_claims") or ())
    evidence_numbers = _evidence_numbers(packet)
    cited = bool(_EVD_ID.search(text))
    numbers = claimed_numbers(text)
    cap = packet.get("max_allowed_precision")

    if numbers and NUMERIC not in allowed:
        bad.append(Violation("FORBIDDEN_NUMERIC_CLAIM",
                             f"route {route} does not allow a number; found "
                             f"{[n for n, _ in numbers]}"))
        if any(_canon(n) == _canon("0") for n, _ in numbers) and _NOT_KNOWN.search(text) is None:
            bad.append(Violation("UNKNOWN_STATED_AS_ZERO", "UNKNOWN is not zero"))

    for number, decimals in numbers:
        if NUMERIC in allowed:
            if _canon(number) not in evidence_numbers:
                bad.append(Violation("NUMBER_NOT_IN_EVIDENCE",
                                     f"{number} is not a value in {sorted(evidence_numbers)}"))
            if cap is not None and decimals > cap:
                bad.append(Violation("PRECISION_EXCEEDS_SOURCE",
                                     f"{number} carries {decimals} decimals, the source reports {cap}"))
            if not cited:
                bad.append(Violation("NUMBER_WITHOUT_EVIDENCE_ID",
                                     f"{number} is stated without an evidence id"))

    if route != "DIRECT" and _ROUTE_UPGRADE.search(text):
        bad.append(Violation("ROUTE_UPGRADED", f"text claims a direct measurement but the route is {route}"))

    if "UPGRADE_ROUTE_OR_COMPATIBILITY" in forbidden and route in _MUST_EXPLAIN:
        if not _NOT_KNOWN.search(text):
            bad.append(Violation("REQUIRED_CAVEAT_MISSING", "an unsupported answer must say it is not known"))
        elif not _states_a_reason(text, packet):
            bad.append(Violation("REQUIRED_CAVEAT_MISSING", "the reason for UNKNOWN must be stated"))

    named_near = [e for e in packet.get("near_evidence_ids") or () if e in text]
    if named_near and not _NO_TRANSFER.search(text):
        bad.append(Violation("REQUIRED_CAVEAT_MISSING",
                             f"near evidence {named_near} is named without saying its number "
                             "cannot be transferred"))
    return VerificationReport(tuple(bad))


def template_answer(packet: Mapping[str, Any]) -> str:
    """The deterministic answer used when verification fails. Built only from packet values."""
    target, food = packet.get("target"), packet.get("food")
    route = packet.get("route", "UNKNOWN")
    reasons = packet.get("unknown_reasons") or {}

    if route == "DIRECT" and packet.get("evidence_values"):
        values = "; ".join(str(v) for v in packet["evidence_values"])
        ids = ", ".join(packet.get("evidence_ids") or ())
        return (f"For {food} at step {packet.get('step')}, the measured {target} value is {values} "
                f"[{ids}]. This is taken from the cited evidence and nothing is inferred beyond it.")

    if route == "SCENARIO":
        return (f"For {food} at step {packet.get('step')}, {target} is available only as a labelled "
                f"scenario, not a measurement, so no measured number is given.")

    head = (f"For {food} at step {packet.get('step')}, {target} is not known from the evidence "
            f"available for this context.")
    if reasons:
        named = "; ".join(f"{k.split('_', 1)[-1].replace('_', ' ')}: {v}" for k, v in reasons.items())
        head += f" Reasons: {named}."
    near = packet.get("near_evidence_ids") or ()
    if near:
        head += (f" A nearby row exists ({', '.join(near)}) but its number cannot be transferred to "
                 f"this context.")
    return head


def answer_or_template(text: str, packet: Mapping[str, Any]) -> tuple[str, bool, VerificationReport]:
    """(answer, used_template, report). A failing answer is replaced, never patched."""
    report = verify(text, packet)
    if report.ok:
        return text, False, report
    return template_answer(packet), True, report
