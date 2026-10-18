"""Segment public-domain cookbook text into recipe candidates (X4).

Paragraphs are split on blank lines and unwrapped. A heading is a short paragraph (≤ 10 words, ≤ 80 chars) that is
mostly upper-case or title-like; a recipe candidate = heading + following paragraphs until the next heading.
Beeton-style fields ("INGREDIENTS.--", "Mode.--", "Time.--", "Sufficient for") are split out when present.
Candidates are filtered later (ingredient + process evidence); nothing here decides what is a recipe.
"""
from __future__ import annotations

import re

NUM_PREFIX = re.compile(r"^\s*(?:No\.\s*)?\d+[.)]?\s+")
FIELD = re.compile(r"_?\b((?:INGREDIENTS|Mode|Time|Average [Cc]ost)_?\s*\.?\s*[-—–]+|(?:Sufficient|Seasonable)_?)\s*")
STOP_HEADINGS = re.compile(r"^(chapter|contents|index|preface|introduction|footnotes?|illustration|note|table of)\b", re.I)


def paragraphs(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if p.strip()]


def is_heading(p: str) -> bool:
    core = NUM_PREFIX.sub("", p).strip(" .:_*")
    words = core.split()
    if not words or len(words) > 10 or len(core) > 80 or STOP_HEADINGS.match(core) or core[-1:] in ",;":
        return False
    letters = [c for c in core if c.isalpha()]
    if len(letters) < 3 or re.search(r"[.!?]\s+\S", core):
        return False
    upper = sum(c.isupper() for c in letters) / len(letters)
    titled = sum(w[0].isupper() for w in words if w[0].isalpha()) / max(1, sum(w[0].isalpha() for w in words))
    return upper > 0.6 or (titled >= 0.75 and len(words) <= 7)


def fields(body: str) -> dict:
    parts = FIELD.split(body)
    if len(parts) < 3:
        return {}
    out, k = {}, 1
    while k < len(parts) - 1:
        key = re.sub(r"[^a-z].*$", "", parts[k].lower())
        out[{"ingredients": "ingredients", "mode": "method", "time": "time", "average": "cost",
             "sufficient": "servings", "seasonable": "season"}[key]] = parts[k + 1].strip(" .")
        k += 2
    return out


def segment(text: str) -> list[dict]:
    paras = paragraphs(text)
    out, cur = [], None
    for p in paras:
        if is_heading(p):
            if cur and cur["body"]:
                out.append(cur)
            cur = {"title": NUM_PREFIX.sub("", p).strip(" .:_*"), "body": []}
        elif cur is not None:
            cur["body"].append(p)
    if cur and cur["body"]:
        out.append(cur)
    res = []
    for c in out:
        body = " ".join(c["body"])
        res.append({"title": c["title"], "body": body, **fields(body)})
    return res
