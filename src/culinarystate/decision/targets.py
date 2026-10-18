"""Closed-world target lexicon from the evidence ledger's target names (C2 slot parsing for targets).

Variants of a ledger name: the full name; the head before ", total|food|dfe|iu|re|rae|<element symbol>|total ascorbic
acid"; "<alpha|beta|…>-<head>" for "head, beta"; each side of "a + b". find(question) -> longest variant present
(word-bounded): its ledger name when the variant belongs to exactly one name, else the variant itself (a key that
covers several names, e.g. "folate"). Found by EXP-000006: the regex nutrient list parsed 20.5% of targets.
"""
from __future__ import annotations

import re
from collections import defaultdict

VERSION = "targets@0.1"
QUALIFIER = re.compile(r"^(?:total|food|dfe|iu|re|rae|[a-z]{1,2}|total ascorbic acid|ethyl)$")
GREEK = ("alpha", "beta", "gamma", "delta")
GENERIC = {"total", "acid", "food", "yield", "weight", "alcohol", "fat", "water"}   # "fry in fat" is not a target


def variants(name: str) -> set:
    n = re.sub(r"\s+", " ", name.lower()).strip()
    out = {n}
    head, _, rest = n.partition(", ")
    if rest and QUALIFIER.match(rest):
        out.add(head)
    if rest in GREEK:
        out |= {head, f"{rest}-{head}", f"{rest} {head}", f"{rest}{head}"}
    if " + " in n:
        out |= {s.strip() for s in n.split(" + ")}
    return {v for v in out if len(v) >= 3 and v not in GENERIC}


class TargetLexicon:
    def __init__(self, names):
        self.by_variant: dict[str, set] = defaultdict(set)
        for name in names:
            for v in variants(name):
                self.by_variant[v].add(name.lower())
        alts = sorted(self.by_variant, key=len, reverse=True)
        self.rx = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, alts)) + r")(?!\w)") if alts else None

    def find(self, question: str) -> str | None:
        if not self.rx:
            return None
        m = self.rx.search(re.sub(r"\s+", " ", (question or "").lower()))
        if not m:
            return None
        names = self.by_variant[m.group(1)]
        return next(iter(names)) if len(names) == 1 else m.group(1)
