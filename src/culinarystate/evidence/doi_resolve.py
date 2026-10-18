"""Resolve free-text citations (Phenol-Explorer style) to DOIs + open-access links.

citation -> Crossref `query.bibliographic` (top 3) -> accept only if year matches (±1) AND ≥ 85% of the Crossref
title's content tokens occur in the citation text -> OpenAlex lookup by DOI for OA status / best PDF URL.
Unaccepted citations stay UNRESOLVED (no guessed DOIs). All HTTP responses cached on disk.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from .literature import MAILTO

CROSSREF = "https://api.crossref.org/works"
OPENALEX = "https://api.openalex.org/works/doi:"
STOP = {"a", "an", "and", "the", "of", "in", "on", "for", "to", "with", "by", "at", "from", "during", "after", "l"}
YEAR = re.compile(r"\((\d{4})\)")


def tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (s or "").lower()) if t not in STOP and len(t) > 1}


def citation_year(cit: str) -> int | None:
    m = YEAR.search(cit or "")
    return int(m.group(1)) if m else None


def title_match(candidate_title: str, citation: str) -> float:
    """Share of the candidate's content tokens present in the citation (1.0 = all)."""
    ct = tokens(candidate_title)
    return round(len(ct & tokens(citation)) / len(ct), 3) if ct else 0.0


def accept(item: dict, citation: str, min_match: float = 0.85) -> bool:
    title = (item.get("title") or [""])[0]
    year = ((item.get("issued") or {}).get("date-parts") or [[None]])[0][0]
    cy = citation_year(citation)
    year_ok = cy is None or (year is not None and abs(int(year) - cy) <= 1)
    return year_ok and len(tokens(title)) >= 3 and title_match(title, citation) >= min_match


@dataclass(frozen=True)
class Resolution:
    citation: str
    status: str                  # RESOLVED | UNRESOLVED | ERROR
    doi: str | None = None
    crossref_title: str | None = None
    match: float = 0.0
    is_oa: bool | None = None
    oa_url: str | None = None
    oa_status: str | None = None


def _cached_get(url: str, params: dict | None, path: Path) -> dict | None:
    if path.exists():
        return json.loads(path.read_text())
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, timeout=40)
            if r.status_code == 404:
                data: dict = {}
                break
            r.raise_for_status()
            data = r.json()
            break
        except requests.RequestException:
            time.sleep(2 ** attempt)
    else:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    time.sleep(0.25)
    return data


def _key(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower())[:150]


def resolve(citation: str, cache: Path) -> Resolution:
    q = re.sub(r"PubMed \(\d+\)", "", citation).strip()
    data = _cached_get(CROSSREF, {"query.bibliographic": q[:400], "rows": 3, "select": "DOI,title,issued",
                                  "mailto": MAILTO}, cache / "crossref" / f"{_key(q)}.json")
    if data is None:
        return Resolution(citation, "ERROR")
    items = (data.get("message") or {}).get("items") or []
    best = next((it for it in items if accept(it, q)), None)
    if not best:
        return Resolution(citation, "UNRESOLVED")
    doi = best["DOI"].lower()
    title = best["title"][0]
    oa = _cached_get(OPENALEX + doi, {"select": "doi,open_access,best_oa_location", "mailto": MAILTO},
                     cache / "openalex_doi" / f"{_key(doi)}.json") or {}
    o = oa.get("open_access") or {}
    loc = oa.get("best_oa_location") or {}
    url = loc.get("pdf_url") or loc.get("landing_page_url") or o.get("oa_url")
    return Resolution(citation, "RESOLVED", doi, title, title_match(title, q), o.get("is_oa"), url, o.get("oa_status"))
