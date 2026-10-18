"""Troubleshooting statements mined from recipe/technique text -> CANDIDATE cause / prevention / recovery relations
(SSOT §243.6–243.7, RQ16-18/19: proposer evidence; cause and recovery kept separate).

Closed failure vocabulary; three surface patterns:
  RECOVERY    "If/Should <x> <fail>, <action>"           -> action after the conditional clause
  CAUSE       "<x> will <fail> if <condition>"           -> condition
  PREVENTION  "<action> to prevent/avoid <fail>" | "<action>, or <x> will <fail>"
Statements are source-cited candidates, never verified causal facts (cause language stays qualified).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

FAILURES = {  # surface stem -> failure key
    "curdl": "CURDLE", "split": "SPLIT", "separat": "SPLIT", "lump": "LUMPY", "burn": "BURN", "scorch": "BURN",
    "catch": "BURN", "stick": "STICK", "sink": "SINK", "sank": "SINK", "fall": "SINK", "crack": "CRACK",
    "boil over": "BOIL_OVER", "seize": "SEIZE", "grainy": "GRAINY", "toughen": "TOUGH", "too thick": "TOO_THICK",
    "too thin": "TOO_THIN", "too salt": "TOO_SALTY", "soggy": "SOGGY", "oily": "OILY",
    "too dry": "TOO_DRY", "dry out": "TOO_DRY", "become tough": "TOUGH", "be tough": "TOUGH", "turn": "TURN",
    "turns out heavy": "HEAVY", "turn out heavy": "HEAVY", "be heavy": "HEAVY", "become heavy": "HEAVY", "is heavy": "HEAVY",
}
_F = "|".join(sorted((re.escape(k) for k in FAILURES), key=len, reverse=True))
FAIL = rf"(?P<fail>(?:{_F})\w*)"
SUBJ = r"(?:(?:the|your|it|they|this|its|mixture|sauce|custard|cake|eggs?|cream|milk|batter|dough|butter|fat|it all)\s*){0,4}?"
AUX = r"(?:(?:begins?|starts?|seems?|appears?|is about|threatens?|happens?|be|is|are|does|do|should)\s+(?:to\s+)?){0,2}"
RECOVERY_RE = re.compile(rf"^\s*(?:if|should)\s+{SUBJ}{AUX}{FAIL}\b[^,;:]*[,;:]\s*(?:then\s+)?(?P<act>[^.;]{{4,160}})", re.I)
CAUSE_RE = re.compile(rf"\b(?:will|would|may|might|is apt to|are apt to|is likely to|are likely to)\s+{FAIL}\b[^,;]*?"
                      rf"\b(?:if|when|unless)\s+(?P<cond>[^.;]{{4,160}})", re.I)
CAUSE_PLAIN_RE = re.compile(rf"\b{FAIL}\s+(?:if|when)\s+(?P<cond>[^.;]{{4,160}})", re.I)
PREVENT_RE = re.compile(rf"^\s*(?P<act>[^.;]{{4,160}}?)\s*,?\s+(?:to (?:prevent|avoid)|to keep\b[^.;]*?\bfrom|so as not to|lest)\b"
                        rf"[^.;]*?\b{FAIL}", re.I)                    # "keep it burning" (wanted) is not prevention
NOT_ACTION = re.compile(r"\b(?:difficult|impossible|hard|easy)\b|\bweather\b", re.I)
PREVENT_OR_RE = re.compile(rf"^\s*(?P<act>[^.;]{{4,160}}?)\s*,\s*(?:or|otherwise)\s+{SUBJ}(?:will|would|may)\s+{FAIL}", re.I)
SENT = re.compile(r"(?<!\b[A-Z])(?<!\bmin)(?<!\bmins)(?<!\boz)(?<!\blb)(?<!\btsp)(?<!\btbsp)(?<!\bNo)(?<=[.!?])\s+(?=[A-Z])")


@dataclass(frozen=True)
class Statement:
    relation: str       # CAUSE / PREVENTION / RECOVERY
    failure: str        # closed vocabulary key
    text: str           # condition (CAUSE) or action (PREVENTION / RECOVERY)
    sentence: str


def _key(surface: str) -> str:
    s = surface.lower()
    return next(v for k, v in sorted(FAILURES.items(), key=lambda kv: -len(kv[0])) if s.startswith(k))


def sentences(text: str) -> list[str]:
    """Sentence split that does not break after common recipe abbreviations (min., oz., lb., tsp.)."""
    return [s.strip() for s in SENT.split(text or "") if s.strip()]


def mine_sentence(s: str) -> list[Statement]:
    out = []
    if m := RECOVERY_RE.search(s):
        out.append(Statement("RECOVERY", _key(m["fail"]), m["act"].strip(" ,"), s))
    elif m := (CAUSE_RE.search(s) or CAUSE_PLAIN_RE.search(s)):
        out.append(Statement("CAUSE", _key(m["fail"]), m["cond"].strip(" ,"), s))
    elif (m := (PREVENT_RE.search(s) or PREVENT_OR_RE.search(s))) and not NOT_ACTION.search(m["act"]):
        out.append(Statement("PREVENTION", _key(m["fail"]), m["act"].strip(" ,"), s))
    return [x for x in out if x.failure != "TURN" or re.search(r"\bturn\w*\s+(?:sour|bitter|rancid)", s, re.I)]
