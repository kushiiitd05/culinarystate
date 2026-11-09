"""Shared text normalisation for the ING -> SR Legacy matcher (deterministic, no model)."""
from __future__ import annotations

import re
import unicodedata

STOP = frozenset({"of", "the", "and", "in", "with", "a", "an", "or", "for", "to", "from", "by", "style", "type", "no",
                  "added", "nfs", "ns", "as", "per", "s", "than", "less", "more", "other", "not", "all", "purpose"})
_PAREN = re.compile(r"\([^)]*\)")


def singular(w: str) -> str:
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith(("oes", "ches", "shes", "xes", "sses")):
        return w[:-2]
    if w.endswith("s") and not w.endswith(("ss", "us", "is")) and len(w) > 3:
        return w[:-1]
    return w


def strip_marks(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text or "") if not unicodedata.combining(c))


def tokens(text: str, *, drop_stop: bool = False) -> list[str]:
    """Lower-case ASCII word tokens, singularised; parentheticals removed."""
    t = _PAREN.sub(" ", strip_marks(text).lower())
    out = [singular(w) for w in re.findall(r"[a-z]+", t)]
    return [w for w in out if w not in STOP] if drop_stop else out
