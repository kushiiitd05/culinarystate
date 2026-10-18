"""Wikibooks Cookbook (CC BY-SA 4.0) via the official MediaWiki API — X3, D-009.

Polite: one request at a time, ≥ 1 s apart, batches of 50 titles, every response cached on disk.
Parsing keeps wiki links to Cookbook pages as character spans over the plain text, so each ingredient line
and step carries free entity links ([[Cookbook:Onion|onions]] -> span "onions" -> target "Onion").
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

from .acquire import USER_AGENT

API = "https://en.wikibooks.org/w/api.php"
LINK = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")
TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
INGREDIENT_SECTIONS = ("ingredient",)
STEP_SECTIONS = ("procedure", "method", "directions", "preparation", "instructions", "steps")


class WikiClient:
    def __init__(self, cache: Path, pause_s: float = 1.0):
        self.cache, self.pause_s, self._last = cache, pause_s, 0.0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def get(self, params: dict) -> dict:
        params = {**params, "format": "json", "formatversion": 2}
        key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:24]
        path = self.cache / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text())
        for attempt in range(6):
            wait = self.pause_s - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                r = self.session.get(API, params=params, timeout=60)
                if r.status_code == 429 or r.status_code >= 500:
                    raise requests.HTTPError(str(r.status_code))
                r.raise_for_status()
                data = r.json()
                break
            except (requests.RequestException, ValueError):
                time.sleep(2 ** attempt)
        else:
            raise RuntimeError(f"Wikibooks API failed for {params}")
        self.cache.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return data

    def members(self, category: str, ns: int = 102) -> list[str]:
        out, cont = [], {}
        while True:
            d = self.get({"action": "query", "list": "categorymembers", "cmtitle": category, "cmlimit": 500,
                          "cmnamespace": ns, **cont})
            out += [m["title"] for m in d["query"]["categorymembers"]]
            if "continue" not in d:
                return out
            cont = {"cmcontinue": d["continue"]["cmcontinue"]}

    def pages(self, titles: list[str]) -> list[dict]:
        out = []
        for i in range(0, len(titles), 50):
            d = self.get({"action": "query", "prop": "revisions|categories", "rvprop": "content|ids|timestamp",
                          "rvslots": "main", "cllimit": "max", "titles": "|".join(titles[i:i + 50])})
            for p in d["query"]["pages"]:
                if p.get("missing") or not p.get("revisions"):
                    continue
                rv = p["revisions"][0]
                out.append({"title": p["title"], "pageid": p["pageid"], "revid": rv["revid"],
                            "timestamp": rv["timestamp"], "content": rv["slots"]["main"]["content"],
                            "categories": [c["title"].removeprefix("Category:") for c in p.get("categories", [])]})
        return out


@dataclass
class Line:
    text: str
    links: list[tuple[int, int, str]] = field(default_factory=list)   # (start, end, target page) over text


def to_plain(wikitext: str) -> Line:
    """Strip markup; keep [[Cookbook:X|shown]] as spans (target X). Other links keep their shown text."""
    s = TEMPLATE.sub("", wikitext)
    s = re.sub(r"'{2,}", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>|<[^>]+>", "", s, flags=re.S)
    out, links, pos = [], [], 0
    for m in LINK.finditer(s):
        out.append(s[pos:m.start()])
        target, shown = m.group(1).strip(), m.group(2)
        if target.lower().startswith(("file:", "image:", "category:")):
            pos = m.end()
            continue
        shown = (shown if shown is not None else target.split(":", 1)[-1]).strip()
        start = sum(map(len, out))
        out.append(shown)
        if target.lower().startswith("cookbook:"):
            links.append((start, start + len(shown), target.split(":", 1)[1].split("#")[0].strip()))
        pos = m.end()
    out.append(s[pos:])
    text = "".join(out)
    lead = len(text) - len(text.lstrip())
    text = text.strip()
    return Line(re.sub(r"\s+", " ", text) if not links else text,
                [(a - lead, b - lead, t) for a, b, t in links if b - lead <= len(text)])


def _summary(wikitext: str) -> dict:
    m = re.search(r"\{\{\s*recipe\s*summary\s*\|(.*?)\}\}", wikitext, re.I | re.S)
    if not m:
        return {}
    out = {}
    for part in re.split(r"\|(?![^\[]*\]\])", m.group(1)):
        k, _, v = part.partition("=")
        if v.strip() and k.strip().lower() in ("category", "servings", "time", "difficulty"):
            out[k.strip().lower()] = v.strip()
    return out


def sections(wikitext: str) -> list[tuple[int, str, str]]:
    """[(level, heading, own body)] in document order (body excludes sub-sections)."""
    heads = list(re.finditer(r"^(=+)\s*([^=]+?)\s*\1\s*$", wikitext, re.M))
    return [(len(h.group(1)), h.group(2).strip().lower(),
             wikitext[h.end():heads[i + 1].start() if i + 1 < len(heads) else len(wikitext)])
            for i, h in enumerate(heads)]


def grouped_items(wikitext: str, names: tuple[str, ...]) -> list[tuple[str | None, Line]]:
    """Items under a matching section and its sub-sections; sub-heading kept as component group."""
    out, active, group = [], None, None
    for level, head, body in sections(wikitext):
        if active is not None and level <= active:
            active = None
        if active is None and any(w in head for w in names):
            active, group = level, None
        elif active is not None:
            group = head
        if active is not None:
            out += [(group, x) for x in _items(body)]
    return out


def _items(body: str) -> list[Line]:
    out = []
    for ln in body.splitlines():
        if ln.strip().startswith(("*", "#")):
            x = to_plain(ln.strip().lstrip("*#: "))
            if x.text:
                out.append(x)
    return out


def parse_recipe(page: dict) -> dict:
    ingredients = grouped_items(page["content"], INGREDIENT_SECTIONS)
    steps = grouped_items(page["content"], STEP_SECTIONS)
    equipment = grouped_items(page["content"], ("equipment",))
    return {"title": page["title"].removeprefix("Cookbook:"), "pageid": page["pageid"], "revid": page["revid"],
            "timestamp": page["timestamp"], "summary": _summary(page["content"]),
            "ingredients": [{"group": g, "text": x.text, "links": x.links} for g, x in ingredients],
            "steps": [{"group": g, "text": x.text, "links": x.links} for g, x in steps],
            "equipment": [{"text": x.text, "links": x.links} for _, x in equipment],
            "categories": page["categories"],
            "url": "https://en.wikibooks.org/wiki/" + page["title"].replace(" ", "_")}
