"""Link an ingredient line (any recipe source) to an ING concept.

Order: (1) editor wiki-link targets / shown text (Wikibooks), skipping unit pages; (2) longest n-gram of the
ingredient phrase (quantity removed, text after comma/paren/"to taste" dropped) matching an ING canonical name or
an ALIAS that points to one ING. Returns (ing_id | None, method). No fuzzy matching: unmatched stays None.
"""
from __future__ import annotations

import re

from culinarystate.quantity.grammar import parse_line

from .foodon import norm

CUT = re.compile(r"\s*(\(|,|;| - | – | to taste\b| for (?:garnish|serving|frying|dusting)\b| or \b).*$", re.I)


class LineLinker:
    def __init__(self, names: dict[str, str], unit_words: set[str]):
        """names: normalised surface -> ING id (canonical names + unambiguous aliases)."""
        self.names = names
        self.unit_words = {norm(u) for u in unit_words}
        self.max_n = max((len(k.split()) for k in names), default=1)

    def phrase(self, line: str) -> str:
        q = parse_line(line)
        rest = q.rest if q.rest else line
        return CUT.sub("", rest).strip()

    def match_phrase(self, phrase: str) -> str | None:
        words = norm(phrase).split()
        for n in range(min(self.max_n, len(words)), 0, -1):
            for i in range(len(words) - n, -1, -1):           # prefer the right-most (head) n-gram
                hit = self.names.get(" ".join(words[i:i + n]))
                if hit:
                    return hit
        return None

    def link(self, text: str, links: list | None = None) -> tuple[str | None, str]:
        for a, b, target in links or []:
            for cand in (text[a:b], target):                  # shown text first: editors link lumped pages
                k = norm(cand)
                if k in self.unit_words:
                    break
                if k in self.names:
                    return self.names[k], "wiki_link"
        hit = self.match_phrase(self.phrase(text))
        return (hit, "ngram") if hit else (None, "none")
