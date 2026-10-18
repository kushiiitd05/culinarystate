"""Phenol-Explorer 3.6 polyphenol retention factors (food processing) — polite cached crawl + parse.

Terms (phenol-explorer.eu/downloads, checked 2026-10-18): freely available; commercial use/redistribution
needs permission; cite Phenol-Explorer + original publications. robots.txt: no disallow.
Retention factors are not in the bulk downloads, so pages are fetched once, cached under
data/raw/phenol_explorer/html/ (local only, git-ignored) and parsed offline.

Page levels:
  /retention-factors/polyphenols?page=N        list of (compound, process) -> /food-processing/<id>/compounds
  /food-processing/<id>/compounds              foods for that compound×process -> /retention-factors/details/<id>
  /retention-factors/details/<id>              per-publication values: RF, food before/after, contents, units
"""
from __future__ import annotations

import html as htmllib
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests

BASE = "http://phenol-explorer.eu"
USER_AGENT = "CulinaryState-research/0.1 (IIIT Delhi course project; kush23296@iiitd.ac.in)"
PAUSE_S = 1.5


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


class CachedFetcher:
    def __init__(self, cache_dir: Path, pause_s: float = PAUSE_S):
        self.cache = Path(cache_dir)
        self.pause_s = pause_s
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.fetched = 0

    def path_for(self, path: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.strip("/")) or "index"
        return self.cache / f"{safe}.html"

    def get(self, path: str) -> str:
        p = self.path_for(path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        for attempt in range(4):
            try:
                r = self.session.get(BASE + path, timeout=60)
                if r.status_code == 200:
                    break
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(10 * (attempt + 1))
                    continue
                r.raise_for_status()
            except requests.RequestException:
                if attempt == 3:
                    raise
                time.sleep(10 * (attempt + 1))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(r.text, encoding="utf-8")
        self.fetched += 1
        time.sleep(self.pause_s)
        return r.text


@dataclass(frozen=True)
class ListRow:
    compound_class: str
    compound: str
    process: str
    n_foods: int
    n_data: int
    fp_path: str


def parse_list_page(page_html: str) -> tuple[list[ListRow], int]:
    s = re.sub(r"<script.*?</script>", "", page_html, flags=re.S)
    last = max([int(x) for x in re.findall(r"polyphenols\?page=(\d+)", s)] or [1])
    rows, klass = [], ""
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S):
        th = re.search(r'<th colspan="7">(.*?)</th>', tr, re.S)
        if th:
            klass = _text(th.group(1))
            continue
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        link = re.search(r'href="(/food-processing/\d+/compounds)"', tr)
        if len(tds) >= 4 and link:
            rows.append(ListRow(klass, _text(tds[0]), _text(tds[1]), int(_text(tds[2])), int(_text(tds[3])),
                                link.group(1)))
    return rows, last


@dataclass(frozen=True)
class FoodRow:
    compound_path: str
    compound: str
    food_group: str
    food_subgroup: str
    food: str
    mean_rf: float | None
    n: int | None
    details_path: str


def parse_food_processing(page_html: str) -> list[FoodRow]:
    s = re.sub(r"<script.*?</script>", "", page_html, flags=re.S)
    out, compound, cpath, group = [], "", "", ""
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S):
        outer = re.search(r'class="outer">(.*?)</th>', tr, re.S)
        if outer:
            a = re.search(r'href="(/compounds/\d+)">(.*?)</a>', outer.group(1), re.S)
            cpath, compound = (a.group(1), _text(a.group(2))) if a else ("", _text(outer.group(1)))
            continue
        inner = re.search(r'class="inner"[^>]*>(.*?)</th>', tr, re.S)
        if inner:
            group = _text(inner.group(1))
            continue
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        det = re.search(r'href="(/retention-factors/details/\d+)"', tr)
        if len(tds) >= 7 and det:
            def num(x):
                t = _text(x)
                return float(t) if re.fullmatch(r"-?\d+(\.\d+)?", t) else None
            n = num(tds[6])
            out.append(FoodRow(cpath, compound, group, _text(tds[0]), _text(tds[1]), num(tds[2]),
                               int(n) if n is not None else None, det.group(1)))
    return out


@dataclass(frozen=True)
class PubValue:
    publication: str
    publication_path: str | None
    rf: float | None
    food_before: str
    food_after: str
    content_before: float | None
    content_after: float | None
    units: str


@dataclass(frozen=True)
class Details:
    compound: str
    food: str
    process: str
    process_definition: str
    yield_factor: float | None
    yield_food: str | None
    yield_source: str | None
    mean_rf: float | None
    values: tuple[PubValue, ...]


def _num(t: str) -> float | None:
    t = t.strip()
    return float(t) if re.fullmatch(r"-?\d+(\.\d+)?(e-?\d+)?", t) else None


def parse_details(page_html: str) -> Details:
    s = re.sub(r"<script.*?</script>", "", page_html, flags=re.S)
    h1 = re.search(r"<h1>(.*?)</h1>", s, re.S).group(1)
    ems = re.findall(r"<em>(.*?)</em>", h1, re.S)
    proc_title = re.search(r'title="([^"]*)"', ems[2]) if len(ems) > 2 else None
    yf = re.search(r"Yield factor value:\s*<strong>([^<]*)</strong>\s*\(<strong>(.*?)</strong>,\s*"
                   r"(?:<a[^>]*>(.*?)</a>)?", s, re.S)
    mean = re.search(r"Calculated Mean Retention Factor Value</h2>.*?<tbody>\s*<tr>\s*<td>([^<]*)</td>", s, re.S)
    values = []
    for block in re.findall(r'<div class="well publication-values">(.*?)</div>', s, re.S):
        bq = re.search(r'<blockquote class="publication">(.*?)</blockquote>', block, re.S)
        pub = _text(bq.group(1)) if bq else ""
        plink = re.search(r'href="(/publications/\d+)"', block)
        body = re.search(r"<tbody>(.*?)</tbody>", block, re.S)
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body.group(1) if body else "", re.S):
            tds = [_text(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            if len(tds) >= 6:
                values.append(PubValue(pub, plink.group(1) if plink else None, _num(tds[0]), tds[1], tds[2],
                                       _num(tds[3]), _num(tds[4]), tds[5]))
    return Details(
        compound=_text(re.sub(r"<i .*?</i>", "", ems[0])) if ems else "",
        food=_text(ems[1]) if len(ems) > 1 else "",
        process=_text(re.sub(r"<i .*?</i>", "", ems[2], flags=re.S)) if len(ems) > 2 else "",
        process_definition=htmllib.unescape(proc_title.group(1)).split("|", 1)[-1] if proc_title else "",
        yield_factor=_num(yf.group(1)) if yf else None,
        yield_food=_text(yf.group(2)) if yf else None,
        yield_source=_text(yf.group(3)) if yf and yf.group(3) else None,
        mean_rf=_num(mean.group(1)) if mean else None,
        values=tuple(values),
    )
