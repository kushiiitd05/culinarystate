"""Ingredient-line -> ING linker for the lot-state layer.

Same algorithm as ``vocab.line_link.LineLinker`` (longest n-gram of the quantity-stripped phrase that equals an
ING canonical name or an unambiguous ALIAS, right-most n-gram preferred, no fuzzy matching). It is re-implemented here
because ``vocab.line_link`` imports ``vocab.foodon`` which needs ``lxml`` (not installed in the project venv).
The name map is built from the LATEST ACTIVE ING / ALIAS ledger rows, read-only.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable

from culinarystate.quantity.grammar import parse_line

CUT = re.compile(r"\s*(\(|,|;| - | – | to taste\b| for (?:garnish|serving|frying|dusting)\b| or \b).*$", re.I)


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    words = [w[:-3] + "y" if w.endswith("ies") and len(w) > 4 else
             (w[:-2] if re.search(r"(oes|ches|shes|sses|xes)$", w) else
              (w[:-1] if w.endswith("s") and not w.endswith("ss") and len(w) > 3 else w)) for w in s.split()]
    return " ".join(words)


def latest_rows(path: Path) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                prev = latest.get(r["id"])
                if prev is None or int(r.get("version") or 0) >= int(prev.get("version") or 0):
                    latest[r["id"]] = r
    return latest


def names_map(ledger_dir: Path) -> dict[str, str]:
    """norm(surface) -> ING id from ACTIVE canonical names, then unambiguous English aliases (first wins)."""
    ing = {k: v for k, v in latest_rows(Path(ledger_dir) / "ING.jsonl").items() if v.get("status") == "ACTIVE"}
    names = {norm(r["canonical_name"]): rid for rid, r in sorted(ing.items())}
    for rid, a in sorted(latest_rows(Path(ledger_dir) / "ALIAS.jsonl").items()):
        tgt = a.get("ingredient_id")
        if (a.get("status") == "ACTIVE" and tgt in ing and a.get("language") == "en"
                and a.get("alias_type") != "AMBIGUOUS" and len(a.get("candidate_ingredient_ids") or [tgt]) == 1):
            names.setdefault(norm(a["normalized"]), tgt)
    return names


class LineLinker:
    def __init__(self, names: dict[str, str]):
        self.names: dict[str, str] = {}
        for k, v in names.items():
            self.names.setdefault(norm(k), v)
        self.max_n = max((len(k.split()) for k in self.names), default=1)

    def phrase(self, line: str) -> str:
        q = parse_line(line)
        rest = q.rest if q.rest else line
        return CUT.sub("", rest).strip()

    def match_phrase(self, phrase: str) -> str | None:
        words = norm(phrase).split()
        for n in range(min(self.max_n, len(words)), 0, -1):
            for i in range(len(words) - n, -1, -1):          # right-most (head) n-gram first
                hit = self.names.get(" ".join(words[i:i + n]))
                if hit:
                    return hit
        return None

    def link_line(self, line: str) -> str | None:
        return self.match_phrase(self.phrase(line))

    def link_part(self, part: str) -> str | None:
        """Food.com ingredient part (no quantity in the text)."""
        return self.match_phrase(CUT.sub("", part or "").strip())
