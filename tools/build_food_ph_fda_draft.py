#!/usr/bin/env python
"""S176 lane L-PH: parse the FDA/CFSAN "Approximate pH of Foods and Food Products" (April 2007)
into a DRAFT registry and a DRAFT lexical crosswalk to the ING ledger.

Inputs (read-only):
  data/raw/fda_ph/wayback_20080223_lacf-phs.html   (web.archive.org capture of the fda.gov page)
  ledgers/data/ING.jsonl, ledgers/data/ALIAS.jsonl  (append-only; latest version per id is used)
Outputs:
  registry/food_ph_fda_draft_v1.csv
  registry/food_ph_fda_ing_crosswalk_draft_v1.csv
  (optional) --summary-json PATH : counts used by the S176_L-PH report

Rules kept (project laws): raw strings are kept verbatim; normalisation lives in new columns; a bound is
NEVER invented (single printed value -> POINT with low=high; a printed "5.00 -" keeps ph_high empty);
character-substitution typos (e.g. "5.2l") are NOT silently repaired; nothing here edits a ledger.
Deterministic: no randomness, no network, stable sort orders.

Run:  python -I tools/build_food_ph_fda_draft.py   (from the worktree root)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/fda_ph/wayback_20080223_lacf-phs.html"
RAW_SHA256 = "f5b8faad71a83ff5b98ef1e7073e6405ac34730557903a89a70a8c058083d59f"
ORIG_URL = "http://www.cfsan.fda.gov/~comm/lacf-phs.html"
SOURCE_URL = "https://web.archive.org/web/20080223184205id_/" + ORIG_URL
RETRIEVED_AT = "2026-11-08T12:54:19Z"  # Date header of the download response
SOURCE_ID = "SRC-PROPOSED-FDA-CFSAN-PH-2007"  # proposal only; NOT a ledger edit

OUT_DRAFT = ROOT / "registry/food_ph_fda_draft_v1.csv"
OUT_XWALK = ROOT / "registry/food_ph_fda_ing_crosswalk_draft_v1.csv"

DRAFT_COLS = [
    "ph_id", "item_raw", "item_norm", "ph_low", "ph_high", "ph_value_type", "page", "source_id",
    "source_url", "retrieved_at", "parse_status", "notes",
    # extra columns (appended after the requested ones)
    "ph_raw", "row_index", "indent_level", "parent_item_raw", "item_context_norm",
]
XWALK_COLS = [
    "xwalk_id", "ph_id", "item_norm", "query_used", "match_basis", "ing_id", "ing_canonical_name",
    "ing_status", "match_via", "alias_id", "matched_surface", "score", "confidence_band", "rank",
    "form_qualifiers", "ph_applies_to", "status", "notes",
]

# ----------------------------------------------------------------------------- HTML table parsing


class TableParser(HTMLParser):
    """Collect (cells, has_dent) per <tr> of the single data table. Entities are decoded."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict] = []
        self._row: dict | None = None
        self._cell: list[str] | None = None
        self._in_data_table = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table" and a.get("class") == "data":
            self._in_data_table = True
        if not self._in_data_table:
            return
        if tag == "tr":
            self._row = {"cells": [], "dent": False, "th": False}
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
            if tag == "th":
                self._row["th"] = True
        elif tag == "div" and a.get("class") == "dent" and self._row is not None:
            self._row["dent"] = True

    def handle_endtag(self, tag):
        if tag == "table":
            self._in_data_table = False
        if not self._in_data_table:
            return
        if tag in ("td", "th") and self._row is not None and self._cell is not None:
            self._row["cells"].append("".join(self._cell))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


NUM = r"\d+(?:\.\d+)?"
RE_POINT = re.compile(rf"^({NUM})$")
RE_RANGE = re.compile(rf"^({NUM})\s*-\s*({NUM})$")
RE_OPEN = re.compile(rf"^({NUM})\s*-$")


def parse_ph(raw: str):
    """Return (low, high, type, status, note). Never invents a bound."""
    s = raw.replace("\xa0", " ").strip()
    if s == "":
        return None, None, "NONE", "NO_PH_PRINTED", ""
    repaired = False
    t = s
    if re.search(r"\d\.\s+\d", t):  # '4. 10' -> '4.10' (whitespace only; deterministic)
        t = re.sub(r"(\d)\.\s+(\d)", r"\1.\2", t)
        repaired = True
    m = RE_POINT.match(t)
    if m:
        v = float(m.group(1))
        return v, v, "POINT", "PARSED_REPAIRED_WS" if repaired else "PARSED", (
            f"printed '{s}': whitespace inside a number removed" if repaired else "")
    m = RE_RANGE.match(t)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        note = ""
        status = "PARSED_REPAIRED_WS" if repaired else "PARSED"
        if repaired:
            note = f"printed '{s}': whitespace inside a number removed"
        if lo > hi:
            status, note = "UNPARSED_REVIEW", f"printed '{s}': low > high"
            return None, None, "RANGE", status, note
        if lo == hi:
            note = (note + "; " if note else "") + "printed as a range with equal ends"
        return lo, hi, "RANGE", status, note
    m = RE_OPEN.match(t)
    if m:
        lo = float(m.group(1))
        return lo, None, "RANGE", "PARSED_OPEN_ENDED", (
            f"printed '{s}' with no upper value: lower bound only; ph_high left empty (NOT a POINT)"
        )
    # character-substitution typo candidates are reported, never applied
    cand = re.sub(r"(?<=\d)l(?=\s|$)", "1", s)
    note = f"printed '{s}' is not a valid number/range"
    if cand != s:
        note += f"; possible intended '{cand}' (letter ell for digit one) NOT applied - human check"
    m = re.match(rf"^({NUM})\s*-\s*\S+$", s)
    if m:  # the lower bound itself is validly printed; the upper token is not
        note += "; valid lower bound kept, ph_high left empty"
        return float(m.group(1)), None, "RANGE", "UNPARSED_REVIEW", note
    return None, None, "RANGE" if "-" in s else "NONE", "UNPARSED_REVIEW", note


# ----------------------------------------------------------------------------- normalisation

STATE_WORDS = {
    "cooked", "canned", "frozen", "fresh", "dried", "boiled", "broiled", "stewed", "strained",
    "pureed", "chopped", "sauted", "acidified", "condensed", "rts", "raw", "ripe", "baked",
    "pickled", "preserved", "smoked", "fermented", "unstrained", "freshly", "ground", "mashed",
}
STOP = {"of", "and", "w", "with", "in", "the", "a", "an", "no", "type"}
GENERIC = {"sauce", "soup", "juice", "paste", "cream", "syrup", "jam", "jelly", "puree", "drink",
           "powder", "oil", "salad", "nectar", "dessert", "flake", "cracker", "milk", "bread",
           "filet", "fillet", "shell", "broth", "stock"}
# processing words that move pH substantially (an acid/fermentation step): identity match is capped at MEDIUM
ACID_PROC = {"acidified", "pickled", "fermented", "preserved"}
# modifier words that may remain on the item without changing what the ingredient is
QUAL = STATE_WORDS | {"red", "green", "yellow", "white", "black", "brown", "purple", "wild", "sweet",
                      "light", "dark", "whole", "young", "new"}

# Possible source typos, reported only (printed text is untouched). AI-suggested, unverified.
TYPO_HINTS = {
    "cruel": "gruel", "eell": "eel", "escarolle": "escarole", "enchalada": "enchilada",
    "edem": "Edam", "calamyrna": "Calimyrna", "kubbard": "Hubbard", "suop": "soup", "saoup": "soup",
    "minestronen": "minestrone", "krispice": "Krispies", "wheatnena": "Wheatena",
    "yangsberries": "Youngberries", "mirliton": None, "sauted": "sauteed",
}
# layout anomalies: indented rows whose parent context should NOT be prepended
NO_CONTEXT = {
    "Prunes, dried, stewed": "indented under 'Potatoes' in the source; probable layout error; parent context not applied",
    "Herring, Pickled": "indented under 'Kippered, Herring, Marshall'; parent context not applied",
}


def norm_text(s: str) -> str:
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*,\s*", ", ", s)
    s = re.sub(r"\s+[+?]$", "", s)  # footnote-like markers
    s = re.sub(r"[.,:;]+$", "", s).strip()
    return s.lower()


def singular(tok: str) -> str:
    if len(tok) <= 3:
        return tok
    if tok.endswith("ies") and len(tok) > 4:
        return tok[:-3] + "y"
    if tok.endswith(("ches", "shes", "xes", "sses", "zes")):
        return tok[:-2]
    if tok.endswith("oes"):
        return tok[:-2]
    if tok.endswith("ss") or tok.endswith("us") or tok.endswith("is"):
        return tok
    if tok.endswith("s"):
        return tok[:-1]
    return tok


def tokens(s: str, drop_states: bool = False) -> list[str]:
    s = re.sub(r"\(.*?\)", " ", s.lower())  # parentheticals are not part of the name proper
    toks = [singular(t) for t in re.findall(r"[a-z0-9]+", s)]
    out = []
    for t in toks:
        if t in STOP:
            continue
        if drop_states and t in STATE_WORDS:
            continue
        out.append(t)
    return out


def ph_applies_to(s: str) -> str:
    toks = {singular(t) for t in re.findall(r"[a-z]+", s.lower())}
    if toks & ACID_PROC:
        return "ACID_PROCESSED_FORM"
    if toks & (STATE_WORDS | {"juice", "nectar", "jam", "jelly", "marmalade", "sauce", "soup", "syrup"}):
        return "PROCESSED_FORM"
    return "ITEM_AS_PRINTED"


def form_qualifiers(s: str) -> str:
    toks = [singular(t) for t in re.findall(r"[a-z]+", s.lower())]
    q = sorted({t for t in toks if t in STATE_WORDS or t in {"juice", "nectar", "jam", "jelly", "marmalade", "sauce", "soup"}})
    return ";".join(q)


# ----------------------------------------------------------------------------- build draft


def build_draft():
    raw_bytes = RAW.read_bytes()
    sha = hashlib.sha256(raw_bytes).hexdigest()
    if sha != RAW_SHA256:
        sys.exit(f"raw sha256 mismatch: {sha}")
    text = raw_bytes.decode("iso-8859-1")  # page declares iso-8859-1; it is pure ASCII anyway
    p = TableParser()
    p.feed(text)
    trs = [r for r in p.rows if not r["th"]]
    n_header = sum(1 for r in p.rows if r["th"])
    # independent completeness count straight from the markup (different method: regex on raw text)
    tbl = re.search(r'<table class="data">(.*?)</table>', text, re.S).group(1)
    n_tr_open = len(re.findall(r"<tr[ >]", tbl))
    n_tr_close = len(re.findall(r"</tr>", tbl))
    n_th_rows = len(re.findall(r"<tr><th>", tbl))
    expected_items = n_tr_open - n_th_rows

    rows = []
    parent_raw = ""
    parent_head = ""
    for i, r in enumerate(trs, 1):
        cells = r["cells"]
        item_raw = cells[0] if cells else ""
        ph_raw = cells[1] if len(cells) > 1 else ""
        indent = 1 if r["dent"] else 0
        if not indent:
            parent_raw = item_raw
            head = re.sub(r"\(.*?\)", "", norm_text(item_raw).split(",")[0]).strip()
            parent_head = head
        low, high, vtype, status, pnote = parse_ph(ph_raw)
        notes = []
        if pnote:
            notes.append(pnote)
        if len(cells) == 1:
            notes.append("source row has no pH cell")
        if len(cells) > 2:
            notes.append(f"source row has {len(cells)} cells; extra cell(s) empty" if not any(c.strip() for c in cells[2:]) else f"source row has {len(cells)} cells")
        inorm = norm_text(item_raw)
        if re.search(r"\s[+?]\s*$", item_raw.replace("\xa0", " ")):
            notes.append("item carries a trailing marker (+ or ?) in the source with no printed explanation")
        m = re.search(r"\((.*?pH.*?)\)", item_raw)
        if m:
            notes.append(f"item name contains a pH figure in parentheses ('{m.group(1)}'); that is NOT the item's pH value")
        if re.search(r"[A-Za-z]\d[A-Za-z]", item_raw):
            notes.append("digit inside a word in item name (probable OCR-style typo); printed text kept")
        for tok in re.findall(r"[A-Za-z]+", item_raw):
            h = TYPO_HINTS.get(tok.lower())
            if h:
                notes.append(f"possible source typo '{tok}' (AI-suggested: '{h}'); printed text kept")
        # context for indented children
        ctx = inorm
        if indent:
            if item_raw.strip() in NO_CONTEXT:
                notes.append(NO_CONTEXT[item_raw.strip()])
            elif parent_head == "soup":
                pass  # children of the 'Soup' group are complete product names; no prefix needed
            elif parent_head:
                ctx = f"{parent_head}, {inorm}"
        rows.append({
            "item_raw": item_raw, "item_norm": inorm, "ph_low": low, "ph_high": high,
            "ph_value_type": vtype, "parse_status": status, "notes": notes,
            "ph_raw": ph_raw, "row_index": i, "indent_level": indent,
            "parent_item_raw": parent_raw if indent else "", "item_context_norm": ctx,
        })
    # group headers: no pH printed and followed by indented children
    for j, r in enumerate(rows):
        if r["parse_status"] == "NO_PH_PRINTED" and r["indent_level"] == 0:
            if j + 1 < len(rows) and rows[j + 1]["indent_level"] == 1:
                r["parse_status"] = "NO_PH_PRINTED_GROUP_HEADER"
                r["notes"].append("group header: no pH printed; values are on the indented rows that follow")
            else:
                r["notes"].append("no pH printed and no indented children")
    # duplicate item_norm
    cnt = Counter(r["item_context_norm"] for r in rows)
    for r in rows:
        if cnt[r["item_context_norm"]] > 1:
            r["notes"].append("duplicate item_context_norm within the document")
    for k, r in enumerate(rows, 1):
        r["ph_id"] = f"FDAPH-{k:04d}"
    meta = {
        "n_tr_open": n_tr_open, "n_tr_close": n_tr_close, "n_th_rows": n_th_rows,
        "expected_items": expected_items, "parsed_rows": len(rows), "header_rows": n_header,
        "raw_sha256": sha,
    }
    return rows, meta


def write_draft(rows):
    with open(OUT_DRAFT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=DRAFT_COLS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({
                "ph_id": r["ph_id"], "item_raw": r["item_raw"], "item_norm": r["item_norm"],
                "ph_low": "" if r["ph_low"] is None else f"{r['ph_low']:.2f}",
                "ph_high": "" if r["ph_high"] is None else f"{r['ph_high']:.2f}",
                "ph_value_type": r["ph_value_type"], "page": 1, "source_id": SOURCE_ID,
                "source_url": SOURCE_URL, "retrieved_at": RETRIEVED_AT,
                "parse_status": r["parse_status"], "notes": " | ".join(r["notes"]),
                "ph_raw": r["ph_raw"], "row_index": r["row_index"], "indent_level": r["indent_level"],
                "parent_item_raw": r["parent_item_raw"], "item_context_norm": r["item_context_norm"],
            })


# ----------------------------------------------------------------------------- crosswalk


def load_latest(name: str) -> list[dict]:
    latest: dict[str, dict] = {}
    with open(ROOT / f"ledgers/data/{name}.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] not in latest or r["version"] > latest[r["id"]]["version"]:
                latest[r["id"]] = r
    return [latest[k] for k in sorted(latest)]


def band(score: float) -> str:
    if score >= 1.0:
        return "EXACT"
    if score >= 0.85:
        return "HIGH"
    if score >= 0.5:
        return "MEDIUM"
    return "LOW"


def build_crosswalk(rows):
    ing = [r for r in load_latest("ING") if r["status"] == "ACTIVE"]
    ali = [r for r in load_latest("ALIAS") if r["status"] == "ACTIVE" and r.get("ingredient_id")]
    ing_by_id = {r["id"]: r for r in ing}
    # name pool: (surface, ing_id, via, alias_id)
    pool = []
    for r in ing:
        pool.append((r["canonical_name"], r["id"], "ING_CANONICAL", ""))
    for a in ali:
        if a["ingredient_id"] in ing_by_id:
            pool.append((a["normalized"] or a["surface"], a["ingredient_id"], "ALIAS", a["id"]))
    index: dict[str, list[int]] = defaultdict(list)
    ptoks = []
    for n, (surf, iid, via, aid) in enumerate(pool):
        t = frozenset(tokens(surf))
        ptoks.append(t)
        for tok in t:
            index[tok].append(n)

    def score_one(q_full: frozenset, q_core: frozenset, c: frozenset):
        """Deterministic lexical relation between the item (q) and a candidate ING/alias name (c)."""
        if not c or not q_full:
            return 0.0, ""
        if c == q_full:
            return 1.0, "FULL"
        if q_core and c == q_core:
            if (q_full - q_core) & ACID_PROC:  # identity matches, but pH of an acidified/pickled form != base item
                return 0.70, "CORE_ACID_PROCESS"
            return 0.90, "CORE"  # equal once processing-state words are dropped
        base = q_core or q_full
        inter = c & base
        if not inter or not (inter - GENERIC):
            return 0.0, ""
        if c < base:  # candidate is a generalisation (item is more specific)
            extras = base - c
            return (0.70, "GENERALISATION") if extras <= QUAL else (0.45, "GENERALISATION")
        if base < c:  # candidate is more specific than the item
            return 0.40, "SPECIALISATION"
        dice = 2 * len(inter) / (len(base) + len(c))
        return round(min(0.8 * dice, 0.39), 4), "OVERLAP"

    out = []
    stats = Counter()
    k = 0
    for r in rows:
        qs = [("CONTEXT", r["item_context_norm"])]
        best: dict[str, dict] = {}
        for label, text in qs:
            q_full = frozenset(tokens(text))
            q_core = frozenset(tokens(text, drop_states=True))
            cand_idx = set()
            for tok in (q_core or q_full):
                cand_idx.update(index.get(tok, ()))
            for n in cand_idx:
                sc, basis = score_one(q_full, q_core, ptoks[n])
                if sc <= 0:
                    continue
                if sc < 0.3:
                    continue
                surf, iid, via, aid = pool[n]
                key = iid
                rec = {"score": sc, "basis": basis, "query": text,
                       "ing_id": iid, "via": via, "alias_id": aid, "surface": surf}
                cur = best.get(key)
                pref = (rec["score"], rec["via"] == "ING_CANONICAL")
                if cur is None or pref > (cur["score"], cur["via"] == "ING_CANONICAL"):
                    best[key] = rec
        ranked = sorted(
            best.values(),
            key=lambda x: (-x["score"], x["via"] != "ING_CANONICAL", -(ing_by_id[x["ing_id"]].get("corpus_frequency") or 0), x["ing_id"]),
        )[:5]
        fq = form_qualifiers(r["item_raw"])
        if not ranked:
            k += 1
            out.append({
                "xwalk_id": f"FDAPH-X-{k:05d}", "ph_id": r["ph_id"], "item_norm": r["item_norm"],
                "query_used": "", "match_basis": "", "ing_id": "", "ing_canonical_name": "",
                "ing_status": "", "match_via": "", "alias_id": "", "matched_surface": "", "score": "",
                "confidence_band": "NONE", "rank": 0, "form_qualifiers": fq,
                "ph_applies_to": ph_applies_to(r["item_raw"]), "status": "AI_DRAFTED",
                "notes": "no candidate with score >= 0.30",
            })
            stats["none"] += 1
            r["_best_band"] = "NONE"
            continue
        r["_best_band"] = band(ranked[0]["score"])
        for rank, c in enumerate(ranked, 1):
            k += 1
            i = ing_by_id[c["ing_id"]]
            nts = []
            if fq:
                nts.append("item is a processed/other form (" + fq + "); the pH applies to that form, not necessarily to the base ING")
            if c["basis"] == "CORE_ACID_PROCESS":
                nts.append("identity matches the base ingredient, but the item is an acidified/pickled/fermented form: its pH must not be applied to the base ING")
            if c["basis"] == "GENERALISATION":
                nts.append("candidate is a more general ingredient than the item (item adds words the candidate lacks)")
            elif c["basis"] == "SPECIALISATION":
                nts.append("candidate is more specific than the item")
            elif c["basis"] == "OVERLAP":
                nts.append("partial word overlap only")
            out.append({
                "xwalk_id": f"FDAPH-X-{k:05d}", "ph_id": r["ph_id"], "item_norm": r["item_norm"],
                "query_used": c["query"], "match_basis": c["basis"], "ing_id": c["ing_id"],
                "ing_canonical_name": i["canonical_name"], "ing_status": i["status"],
                "match_via": c["via"], "alias_id": c["alias_id"], "matched_surface": c["surface"],
                "score": f"{c['score']:.2f}", "confidence_band": band(c["score"]), "rank": rank,
                "form_qualifiers": fq, "ph_applies_to": ph_applies_to(r["item_raw"]),
                "status": "AI_DRAFTED", "notes": " | ".join(nts),
            })
    with open(OUT_XWALK, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=XWALK_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    return out, {"ing_active_latest": len(ing), "alias_active_latest": len(ali), "pool_size": len(pool)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary-json", default=None)
    args = ap.parse_args()
    rows, meta = build_draft()
    write_draft(rows)
    xw, xmeta = build_crosswalk(rows)
    types = Counter(r["ph_value_type"] for r in rows)
    status = Counter(r["parse_status"] for r in rows)
    with_val = [r for r in rows if r["parse_status"] in ("PARSED", "PARSED_REPAIRED_WS", "PARSED_OPEN_ENDED")]
    best = Counter(r["_best_band"] for r in with_val)
    best_all = Counter(r["_best_band"] for r in rows)
    summary = {
        **meta, **xmeta, "types": dict(types), "status": dict(status),
        "rows_with_numeric_ph": len(with_val), "best_band_numeric_rows": dict(best),
        "best_band_all_rows": dict(best_all), "crosswalk_rows": len(xw),
        "draft_sha256": hashlib.sha256(OUT_DRAFT.read_bytes()).hexdigest(),
        "xwalk_sha256": hashlib.sha256(OUT_XWALK.read_bytes()).hexdigest(),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.summary_json:
        Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
