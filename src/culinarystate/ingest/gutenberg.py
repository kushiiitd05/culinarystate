"""Project Gutenberg cookbooks (public domain in the US) via the PGLAF mirror — X4, D-009.

Gutenberg's robot policy asks bulk downloads to use a mirror with a wait between requests; we fetch one
directory listing + one text file per book, ≥ 2 s apart, cached on disk, preferring UTF-8 (-0.txt).
"""
from __future__ import annotations

import io
import re
import time
import zipfile
from pathlib import Path

import requests

from .acquire import USER_AGENT

MIRROR = "https://gutenberg.pglaf.org"
START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^*]*\*\*\*", re.I)
END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK", re.I)


def book_dir(book_id: int) -> str:
    s = str(book_id)
    parts = list(s[:-1]) if len(s) > 1 else ["0"]
    return f"{MIRROR}/{'/'.join(parts)}/{s}/"


def pick_file(listing_html: str, book_id: int) -> tuple[str, str] | None:
    """(filename, encoding) — UTF-8 first, then Latin-1, then ASCII; the .zip of a text is preferred (≈3× smaller)."""
    hrefs = set(re.findall(r'href="([^"/]+)"', listing_html))
    for stem, enc in ((f"{book_id}-0", "utf-8"), (f"{book_id}-8", "latin-1"), (f"{book_id}", "utf-8")):
        for ext in (".zip", ".txt"):
            if stem + ext in hrefs:
                return stem + ext, enc
    return None


def unpack(raw: bytes, name: str) -> bytes:
    if not name.endswith(".zip"):
        return raw
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        txt = next(n for n in z.namelist() if n.endswith(".txt"))
        return z.read(txt)


def strip_boilerplate(text: str) -> str:
    s, e = START.search(text), END.search(text)
    return text[s.end() if s else 0: e.start() if e else len(text)].strip()


class Fetcher:
    def __init__(self, cache: Path, pause_s: float = 2.0):
        self.cache, self.pause_s, self._last = cache, pause_s, 0.0
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def _get(self, url: str) -> bytes | None:
        for attempt in range(5):
            wait = self.pause_s - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                r = self.session.get(url, timeout=60)
                if r.status_code == 404:
                    return None
                r.raise_for_status()
                return r.content
            except requests.RequestException:
                time.sleep(2 ** attempt)
        return None

    def book(self, book_id: int) -> tuple[str, str] | None:
        """Return (clean text, source url) or None. Raw file cached as <id>.txt (+ .url)."""
        path, meta = self.cache / f"{book_id}.txt", self.cache / f"{book_id}.url"
        if path.exists() and meta.exists():
            return strip_boilerplate(path.read_text(encoding="utf-8")), meta.read_text().strip()
        listing = self._get(book_dir(book_id))
        pick = pick_file(listing.decode("utf-8", "replace"), book_id) if listing else None
        if not pick:
            return None
        url = book_dir(book_id) + pick[0]
        raw = self._get(url)
        if raw is None:
            return None
        text = unpack(raw, pick[0]).decode(pick[1], "replace")
        self.cache.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        meta.write_text(url)
        return strip_boilerplate(text), url
