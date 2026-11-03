"""Step 13a-0 offline seed corpus from existing local artifacts (S157). Status: PROVISIONAL_PENDING_13A.

Offline only: no network call, no API key, no crawl. The corpus is a DOI-keyed interim table (spine
row 13a-0: "may use an interim DOI table until the 04.1 DOC schema exists"); it mints no ledger id and
writes no ledger. Ledgers are read only.

Inputs (artifact id -> local file)
- ``queue_v1``            registry/evidence/verification_queue_ranked_v1.csv (Route A PE + Route B OpenAlex)
- ``rejected_v1``         registry/evidence/rejected_candidates.csv (Route B rows the heuristic rejected)
- ``route_a_precheck_v1`` registry/evidence/route_a_paper_precheck.csv (PE citations, resolved DOIs)
- ``human_review_pack_v1`` registry/evidence/human_review_pack_v1.csv (paper_doi of the 55 pack rows)
- ``src_ledger_pe_pub``   ledgers/data/SRC.jsonl, latest version of each ACTIVE ``kind = PAPER``
                          record of a ``pe_pub:*`` family (the PE cited papers)
- ``doc_ledger_doi``      ledgers/data/DOC.jsonl, latest ACTIVE records with ``identifiers.doi``
- ``query_matrix_v1``     registry/evidence_query_matrix_v1.csv: read and counted; it holds query
                          templates and hit counts only, so it contributes NO record
- ``openalex_pages``      data/raw/openalex/*.json (git-ignored first-page caches written by
                          ``evidence.literature.harvest``); used only when present locally

DOI normalisation (``normalise_doi``), applied in this order; each applied step is recorded
1. STRIP_WHITESPACE: surrounding whitespace removed (``str.strip``).
2. STRIP_RESOLVER_URL: one leading resolver prefix removed, any case: ``[http[s]://][www.|dx.]doi.org/``.
   STRIP_DOI_SCHEME: or one leading ``doi:`` (optional spaces after it) or ``info:doi/``.
   These are presentation / resolution forms, not part of the DOI name.
3. PERCENT_DECODE_URL_FORM: only when a resolver URL was stripped, ``%XX`` escapes are decoded as
   UTF-8 (URI encoding). A malformed escape or invalid UTF-8 makes the DOI INVALID_SYNTAX. In the bare
   form ``%`` is an ordinary DOI character and is left alone.
4. CASE_FOLD_ASCII: ASCII A-Z -> a-z only (DOI names are case-insensitive). Non-ASCII characters are
   left unchanged: no Unicode case mapping and no NFC/NFKC normalisation (conservative choice).
5. Syntax check ``10.<digits>[.<digits>]*/<suffix without whitespace>``; failure -> INVALID_SYNTAX.
NOT applied: trailing-punctuation trimming, internal-whitespace removal, SICI / legacy escapes,
prefix repair, any lookup. A blank DOI is ABSENT. Nothing is guessed. The rules follow the DOI
Handbook's syntax and case-insensitivity statements as recalled offline; section numbers were not
re-checked in this session (UNVERIFIED).

Dedup: EXACT_NORMALISED_DOI_ONLY. Records with an ABSENT or INVALID_SYNTAX DOI are never merged
(one seed each). Titles are compared only for a report-only count (exact equality after casefold and
non-alphanumeric collapsing); no fuzzy match is applied to the corpus (08b detector, later).

What a seed carries: ids, DOI raw forms, title / year / venue metadata, provenance (artifact + row
ref per input record), the OA flag statements of the inputs, and licence statements only when an
input states one (OpenAlex ``license`` fields, a non-UNKNOWN SRC ``licence_status``). Otherwise
``licence_status = UNKNOWN``; ``tdm_status`` is always UNKNOWN. An OA flag is not a reuse licence.
Never carried: abstracts (``abstract_inverted_index``), authorships, AI notes, reasons, food /
compound values, human-review cells. Seeds are built from a field whitelist (``SEED_FIELDS``).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from culinarystate.lineage.guard import ProtectedPathError, assert_safe_write_target

STATUS = "PROVISIONAL_PENDING_13A"
VERSION = "seed_corpus_13a0@0.1-provisional"
DEDUP_RULE = "EXACT_NORMALISED_DOI_ONLY"
DOI_TRANSFORMS = ("STRIP_WHITESPACE", "STRIP_RESOLVER_URL", "STRIP_DOI_SCHEME", "PERCENT_DECODE_URL_FORM",
                  "CASE_FOLD_ASCII")
NOT_APPLIED = ("TRAILING_PUNCTUATION_TRIM", "INTERNAL_WHITESPACE_REMOVAL", "UNICODE_CASE_MAPPING",
               "UNICODE_NORMALISATION", "PREFIX_REPAIR", "NETWORK_LOOKUP", "FUZZY_TITLE_MERGE")
EXCLUDED_INPUT_FIELDS = ("abstract_inverted_index", "abstract", "authorships", "reasons", "notes", "ai_notes",
                         "ai_suggested_decision", "ai_paper_suggestion", "food", "compound", "before_value",
                         "after_value", "evd_ids", "human_status", "human_decision", "verifier", "verified_at")
LICENCE_STATUSES = ("UNKNOWN", "STATED_BY_INPUT_UNVERIFIED", "CONFLICTING_STATEMENTS_UNVERIFIED")
ROOT = Path(__file__).resolve().parents[3]

# title / year / venue are taken from the first artifact in this order that gives one
ARTIFACT_ORDER = ("openalex_pages", "src_ledger_pe_pub", "route_a_precheck_v1", "queue_v1", "rejected_v1",
                  "human_review_pack_v1", "doc_ledger_doi")
INPUT_PATHS: Mapping[str, str] = {
    "queue_v1": "registry/evidence/verification_queue_ranked_v1.csv",
    "rejected_v1": "registry/evidence/rejected_candidates.csv",
    "route_a_precheck_v1": "registry/evidence/route_a_paper_precheck.csv",
    "human_review_pack_v1": "registry/evidence/human_review_pack_v1.csv",
    "src_ledger_pe_pub": "ledgers/data/SRC.jsonl",
    "doc_ledger_doi": "ledgers/data/DOC.jsonl",
    "query_matrix_v1": "registry/evidence_query_matrix_v1.csv",
    "openalex_pages": "data/raw/openalex",
}
SEED_FIELDS = ("record", "seed_key", "doi", "doi_status", "doi_raw_forms", "doi_transforms", "title",
               "title_artifact", "titles_distinct", "year", "years_seen", "venue", "work_types", "openalex_ids",
               "src_ids", "doc_ids", "routes", "queue_classes", "query_cells", "oa_flag", "oa_flag_statements",
               "oa_urls", "licence_status", "licence_stated", "tdm_status", "n_source_records", "sources")

_RESOLVER = re.compile(r"^(?:https?://)?(?:www\.|dx\.)?doi\.org/", re.IGNORECASE)
_SCHEME = re.compile(r"^(?:doi:\s*|info:doi/)", re.IGNORECASE)
_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")
_SYNTAX = re.compile(r"^10\.[0-9]+(?:\.[0-9]+)*/\S+$")
_YEAR = re.compile(r"^\s*(\d{4})(?:\.0+)?\s*$")
_ASCII_UPPER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


class SeedCorpusError(ValueError):
    """Missing required input, refused write or a report that is not counts-only."""


# ---------------------------------------------------------------- DOI normalisation
@dataclass(frozen=True)
class DoiNorm:
    raw: str | None
    status: str                   # VALID | INVALID_SYNTAX | ABSENT
    doi: str | None
    transforms: tuple[str, ...]


def normalise_doi(raw: str | None) -> DoiNorm:
    if raw is None or not str(raw).strip():
        return DoiNorm(raw, "ABSENT", None, ())
    s, applied = str(raw), []
    if s.strip() != s:
        s = s.strip()
        applied.append("STRIP_WHITESPACE")
    url_form = False
    if _RESOLVER.match(s):
        s, url_form = _RESOLVER.sub("", s, count=1), True
        applied.append("STRIP_RESOLVER_URL")
    elif _SCHEME.match(s):
        s = _SCHEME.sub("", s, count=1)
        applied.append("STRIP_DOI_SCHEME")
    if url_form and "%" in s:
        if _ESCAPE.search(s):
            return DoiNorm(raw, "INVALID_SYNTAX", None, tuple(applied))
        try:
            decoded = unquote(s, encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            return DoiNorm(raw, "INVALID_SYNTAX", None, tuple(applied))
        if decoded != s:
            s = decoded
            applied.append("PERCENT_DECODE_URL_FORM")
    folded = s.translate(_ASCII_UPPER)
    if folded != s:
        s = folded
        applied.append("CASE_FOLD_ASCII")
    if not _SYNTAX.match(s):
        return DoiNorm(raw, "INVALID_SYNTAX", None, tuple(applied))
    return DoiNorm(raw, "VALID", s, tuple(applied))


def normalise_title(t: str | None) -> str:
    return " ".join(re.sub(r"[^0-9a-z]+", " ", str(t or "").casefold()).split())


# ---------------------------------------------------------------- inputs
@dataclass(frozen=True)
class InputSpec:
    artifact: str
    path: Path | None
    required: bool


def default_inputs(root: Path | str, *, openalex: bool = True, openalex_dir: Path | str | None = None
                   ) -> list[InputSpec]:
    root = Path(root)
    out = [InputSpec(a, root / p, True) for a, p in INPUT_PATHS.items() if a != "openalex_pages"]
    oa = Path(openalex_dir) if openalex_dir is not None else root / INPUT_PATHS["openalex_pages"]
    out.append(InputSpec("openalex_pages", oa if openalex else None, False))
    return out


def _blank(v: Any) -> str | None:
    s = "" if v is None else str(v)
    return s if s.strip() else None


def _year(v: Any) -> int | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    m = _YEAR.match(str(v or ""))
    return int(m.group(1)) if m else None


def _flag(v: Any) -> str | None:
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    s = str(v or "").strip().lower()
    return {"true": "TRUE", "false": "FALSE"}.get(s)


def _rec(artifact: str, ref: str, doi_raw: Any, **kw: Any) -> dict:
    base = {"artifact": artifact, "ref": ref, "doi_raw": _blank(doi_raw), "title": None, "year": None,
            "oa_flag": None, "oa_url": None, "licence_stated": (), "openalex_id": None, "venue": None,
            "work_type": None, "route": None, "queue_class": None, "query_cell": None, "src_id": None,
            "doc_id": None}
    base.update(kw)
    return base


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _human_filled(row: Mapping[str, str], cols: Iterable[str]) -> bool:
    return any((row.get(c) or "").strip() for c in cols)


def _unique_ref(ref: str, n: int, seen: set[str]) -> str:
    out = ref if ref not in seen else f"{ref};row={n}"
    seen.add(out)
    return out


def _queue_like(path: Path, artifact: str) -> tuple[list[dict], dict]:
    recs, seen, human = [], set(), 0
    for n, r in enumerate(_csv_rows(path), start=1):
        human += _human_filled(r, ("human_status", "verifier", "verified_at"))
        rank = (r.get("queue_rank") or "").strip()
        ref = _unique_ref(f"queue_rank={rank}" if rank else f"row={n}", n, seen)
        route = _blank(r.get("route"))
        cell = None
        if route and route.startswith("B_"):
            parts = [(r.get(k) or "").strip() for k in ("process", "target", "matrix")]
            cell = "|".join(parts) if any(parts) else None
        url = _blank(r.get("url"))
        oa_url = url.strip() if url and not _RESOLVER.match(url.strip()) else None
        recs.append(_rec(artifact, ref, r.get("doi"), title=_blank(r.get("title")), year=_year(r.get("year")),
                         oa_flag=_flag(r.get("open_access")), oa_url=oa_url, route=route,
                         queue_class=_blank(r.get("class")), query_cell=cell))
    return recs, {"rows_with_human_fields_filled": human}


def _precheck(path: Path, artifact: str) -> tuple[list[dict], dict]:
    recs, seen = [], set()
    for n, r in enumerate(_csv_rows(path), start=1):
        sid = _blank(r.get("src_id"))
        ref = _unique_ref(f"src_id={sid.strip()}" if sid else f"row={n}", n, seen)
        recs.append(_rec(artifact, ref, r.get("doi"), title=_blank(r.get("citation")), oa_flag=_flag(r.get("is_oa")),
                         oa_url=_blank(r.get("oa_url")), src_id=sid.strip() if sid else None))
    return recs, {}


def _review_pack(path: Path, artifact: str) -> tuple[list[dict], dict]:
    recs, seen, human = [], set(), 0
    for n, r in enumerate(_csv_rows(path), start=1):
        human += _human_filled(r, ("human_decision", "verifier", "verified_at"))
        eid = _blank(r.get("evd_id"))
        ref = _unique_ref(f"evd_id={eid.strip()}" if eid else f"row={n}", n, seen)
        recs.append(_rec(artifact, ref, r.get("paper_doi"), title=_blank(r.get("citation"))))
    return recs, {"rows_with_human_fields_filled": human}


def _latest(path: Path) -> list[dict]:
    latest: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                latest[r["id"]] = r
    return [latest[k] for k in sorted(latest)]


def _src_ledger(path: Path, artifact: str) -> tuple[list[dict], dict]:
    recs = []
    for r in _latest(path):
        if (r.get("status") != "ACTIVE" or r.get("kind") != "PAPER"
                or not str(r.get("source_family_id") or "").startswith("pe_pub:")):
            continue
        ls = str(r.get("licence_status") or "").strip()
        stated = (ls,) if ls and ls.upper() != "UNKNOWN" else ()
        recs.append(_rec(artifact, f"src_id={r['id']}", r.get("doi"), title=_blank(r.get("title")),
                         year=_year(r.get("year")), licence_stated=stated, src_id=r["id"]))
    return recs, {}


def _doc_ledger(path: Path, artifact: str) -> tuple[list[dict], dict]:
    recs = []
    for r in _latest(path):
        doi = (r.get("identifiers") or {}).get("doi")
        if r.get("status") != "ACTIVE" or not _blank(doi):
            continue
        recs.append(_rec(artifact, f"doc_id={r['id']}", doi, doc_id=r["id"], src_id=_blank(r.get("src_id"))))
    return recs, {}


def _query_matrix(path: Path, artifact: str) -> tuple[list[dict], dict]:
    return [], {"template_rows": len(_csv_rows(path)), "reason": "NO_RECORD_LEVEL_IDENTIFIERS"}


def _openalex_licences(w: Mapping[str, Any]) -> tuple[str, ...]:
    out = []
    for k in ("primary_location", "best_oa_location"):
        lic = (w.get(k) or {}).get("license") if isinstance(w.get(k), Mapping) else None
        if _blank(lic):
            out.append(str(lic).strip())
    return tuple(dict.fromkeys(out))


def _openalex(path: Path, artifact: str) -> tuple[list[dict], dict]:
    recs, files_read, unreadable, abstracts = [], 0, 0, 0
    for f in sorted(p for p in path.glob("*.json") if p.is_file()):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            unreadable += 1
            continue
        works = data.get("results") if isinstance(data, Mapping) else data
        if not isinstance(works, list):
            unreadable += 1
            continue
        files_read += 1
        for i, w in enumerate(works):
            if not isinstance(w, Mapping):
                continue
            abstracts += bool(w.get("abstract_inverted_index") or w.get("abstract"))
            loc = w.get("primary_location") if isinstance(w.get("primary_location"), Mapping) else {}
            src = loc.get("source") if isinstance(loc.get("source"), Mapping) else {}
            oa = w.get("open_access") if isinstance(w.get("open_access"), Mapping) else {}
            wid = _blank(w.get("id"))
            recs.append(_rec(artifact, f"{f.name}#{i}", w.get("doi"), title=_blank(w.get("title")),
                             year=_year(w.get("publication_year")), oa_flag=_flag(oa.get("is_oa")),
                             oa_url=_blank(oa.get("oa_url")), licence_stated=_openalex_licences(w),
                             openalex_id=wid.rsplit("/", 1)[-1] if wid else None,
                             venue=_blank(src.get("display_name")), work_type=_blank(w.get("type"))))
    return recs, {"files_read": files_read, "files_unreadable": unreadable, "works_with_abstract_dropped": abstracts}


READERS = {"queue_v1": _queue_like, "rejected_v1": _queue_like, "route_a_precheck_v1": _precheck,
           "human_review_pack_v1": _review_pack, "src_ledger_pe_pub": _src_ledger, "doc_ledger_doi": _doc_ledger,
           "query_matrix_v1": _query_matrix, "openalex_pages": _openalex}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _locator(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return "OUTSIDE_REPO_ROOT"


def _input_fact(spec: InputSpec, root: Path) -> dict:
    if spec.path is None:
        return {"present": False, "reason": "DISABLED", "records_read": 0}
    p = spec.path
    if spec.artifact == "openalex_pages":
        if not p.is_dir():
            return {"present": False, "reason": "NOT_PRESENT_LOCALLY", "records_read": 0}
        h = hashlib.sha256()
        for f in sorted(x for x in p.glob("*.json") if x.is_file()):
            h.update(f"{f.name}\0{_sha256(f)}\n".encode())
        return {"present": True, "locator": _locator(p, root), "sha256_of_file_digests": h.hexdigest()}
    if not p.is_file():
        if spec.required:
            raise SeedCorpusError(f"required input missing: {spec.artifact}")
        return {"present": False, "reason": "NOT_PRESENT_LOCALLY", "records_read": 0}
    return {"present": True, "locator": _locator(p, root), "sha256": _sha256(p), "bytes": p.stat().st_size}


# ---------------------------------------------------------------- build
@dataclass(frozen=True)
class SeedCorpus:
    seeds: list[dict] = field(default_factory=list)
    records: list[dict] = field(default_factory=list)
    counts: dict = field(default_factory=dict)
    inputs: dict = field(default_factory=dict)


def _order(artifact: str) -> int:
    return ARTIFACT_ORDER.index(artifact) if artifact in ARTIFACT_ORDER else len(ARTIFACT_ORDER)


def _first(recs: list[dict], key: str) -> tuple[Any, str | None]:
    for r in sorted(recs, key=lambda r: (_order(r["artifact"]), r["ref"])):
        if r[key] not in (None, ""):
            return r[key], r["artifact"]
    return None, None


def _statements(recs: list[dict], key: str) -> list[dict]:
    pairs = set()
    for r in recs:
        vals = r[key] if isinstance(r[key], tuple) else (r[key],)
        pairs |= {(r["artifact"], v) for v in vals if v is not None}
    return [{"artifact": a, "value": v} for a, v in sorted(pairs)]


def _seed(key: str, norm: DoiNorm, recs: list[dict]) -> dict:
    title, title_art = _first(recs, "title")
    year, _ = _first(recs, "year")
    venue, _ = _first(recs, "venue")
    oa = _statements(recs, "oa_flag")
    oa_vals = {s["value"] for s in oa}
    lic = _statements(recs, "licence_stated")
    lic_vals = {s["value"] for s in lic}

    def distinct(k: str) -> list:
        return sorted({r[k] for r in recs if r[k] not in (None, "")})
    seed = {
        "record": "SEED", "seed_key": key, "doi": norm.doi, "doi_status": norm.status,
        "doi_raw_forms": distinct("doi_raw"),
        "doi_transforms": sorted({t for r in recs for t in r["_doi"].transforms}),
        "title": title, "title_artifact": title_art, "titles_distinct": len(distinct("title")),
        "year": year, "years_seen": distinct("year"), "venue": venue, "work_types": distinct("work_type"),
        "openalex_ids": distinct("openalex_id"), "src_ids": distinct("src_id"), "doc_ids": distinct("doc_id"),
        "routes": distinct("route"), "queue_classes": distinct("queue_class"), "query_cells": distinct("query_cell"),
        "oa_flag": "UNKNOWN" if not oa_vals else (oa_vals.pop() if len(oa_vals) == 1 else "CONFLICT"),
        "oa_flag_statements": oa, "oa_urls": distinct("oa_url"),
        "licence_status": ("UNKNOWN" if not lic_vals else "STATED_BY_INPUT_UNVERIFIED" if len(lic_vals) == 1
                           else "CONFLICTING_STATEMENTS_UNVERIFIED"),
        "licence_stated": lic, "tdm_status": "UNKNOWN", "n_source_records": len(recs),
        "sources": [{"artifact": r["artifact"], "ref": r["ref"], "doi_status": r["_doi"].status}
                    for r in sorted(recs, key=lambda r: (r["artifact"], r["ref"]))],
    }
    return {k: seed[k] for k in SEED_FIELDS}


def build_seed_corpus(inputs: Iterable[InputSpec], *, root: Path | str = ROOT) -> SeedCorpus:
    root = Path(root)
    records: list[dict] = []
    facts: dict[str, dict] = {}
    for spec in inputs:
        fact = _input_fact(spec, root)
        if fact.get("present"):
            recs, extra = READERS[spec.artifact](spec.path, spec.artifact)
            fact.update(extra)
            for r in recs:
                r["_doi"] = normalise_doi(r["doi_raw"])
            st = Counter(r["_doi"].status for r in recs)
            fact.update(records_read=len(recs), doi_valid=st.get("VALID", 0),
                        doi_invalid_syntax=st.get("INVALID_SYNTAX", 0), doi_absent=st.get("ABSENT", 0))
            records += recs
        facts[spec.artifact] = fact
    groups: dict[str, list[dict]] = defaultdict(list)
    norms: dict[str, DoiNorm] = {}
    for r in records:
        n = r["_doi"]
        key = {"VALID": f"doi:{n.doi}", "INVALID_SYNTAX": f"invalid:{r['artifact']}:{r['ref']}",
               "ABSENT": f"nodoi:{r['artifact']}:{r['ref']}"}[n.status]
        groups[key].append(r)
        norms.setdefault(key, n)
    seeds = [_seed(k, norms[k], groups[k]) for k in sorted(groups)]
    counts = _counts(seeds, records, facts, groups)
    return SeedCorpus(seeds=seeds, records=records, counts=counts, inputs=facts)


def _counts(seeds: list[dict], records: list[dict], facts: dict, groups: Mapping[str, list[dict]]) -> dict:
    doi_seeds = [s for s in seeds if s["doi"]]
    by_art: dict[str, set[str]] = defaultdict(set)
    for s in doi_seeds:
        for src in s["sources"]:
            by_art[src["artifact"]].add(s["seed_key"])
    arts = sorted(by_art)
    overlap = {f"{a}__{b}": len(by_art[a] & by_art[b]) for a, b in combinations(arts, 2)}
    n_hist = Counter(min(s["n_source_records"], 5) for s in seeds)
    title_seeds: dict[str, set[str]] = defaultdict(set)
    for key, recs in groups.items():
        for r in recs:
            t = normalise_title(r["title"])
            if t:
                title_seeds[t].add(key)
    doi_keys = {s["seed_key"] for s in doi_seeds}
    shared = [ks for ks in title_seeds.values() if len(ks & doi_keys) > 1]
    nodoi_shared = {k for ks in title_seeds.values() if len(ks) > 1 for k in ks if k not in doi_keys}
    transforms = Counter(t for r in records for t in r["_doi"].transforms)
    return {
        "status": STATUS, "versions": {"seed_corpus": VERSION}, "dedup_rule": DEDUP_RULE,
        "abstracts_included": False, "network_calls": 0, "ledger_rows_appended": 0, "ids_minted": 0,
        "inputs": facts, "records_read_total": len(records),
        "doi_transform_counts": {t: transforms.get(t, 0) for t in DOI_TRANSFORMS},
        "seeds": {"total": len(seeds), "with_valid_doi": len(doi_seeds),
                  "without_valid_doi": len(seeds) - len(doi_seeds),
                  "invalid_syntax": sum(s["doi_status"] == "INVALID_SYNTAX" for s in seeds),
                  "absent": sum(s["doi_status"] == "ABSENT" for s in seeds),
                  "doi_records_merged_into_an_earlier_record": sum(len(groups[k]) - 1 for k in doi_keys),
                  "doi_seeds_multi_source_record": sum(s["n_source_records"] > 1 for s in doi_seeds),
                  "doi_seeds_multi_artifact": sum(len({x["artifact"] for x in s["sources"]}) > 1 for s in doi_seeds),
                  "doi_seeds_with_several_raw_forms": sum(len(s["doi_raw_forms"]) > 1 for s in doi_seeds),
                  "doi_seeds_with_conflicting_years": sum(len(s["years_seen"]) > 1 for s in doi_seeds),
                  "by_n_source_records": {("n_5_plus" if k == 5 else f"n_{k}"): v for k, v in sorted(n_hist.items())}},
        "doi_seeds_by_artifact": {a: len(by_art[a]) for a in arts},
        "doi_seed_overlap_by_artifact_pair": overlap,
        "oa_flag_counts": dict(sorted(Counter(s["oa_flag"] for s in seeds).items())),
        "licence_status_counts": dict(sorted(Counter(s["licence_status"] for s in seeds).items())),
        "tdm_status_counts": dict(sorted(Counter(s["tdm_status"] for s in seeds).items())),
        "fuzzy_report_only": {"method": "EXACT_EQUALITY_OF_NORMALISED_TITLE", "applied_to_dedup": False,
                              "doi_seed_groups_sharing_normalised_title": len(shared),
                              "doi_seeds_in_those_groups": len({k for ks in shared for k in ks & doi_keys}),
                              "no_doi_seeds_sharing_normalised_title_with_another_seed": len(nodoi_shared)},
    }


# ---------------------------------------------------------------- counts-only check, writers
_KEY = re.compile(r"^[A-Za-z0-9_]+$")
_CODE = re.compile(r"^[A-Z0-9_.:\-]+$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
_PATH = re.compile(r"^[A-Za-z0-9_./@\-]+$")
_FREE = ("versions", "inputs")


def assert_counts_only(obj: Any, _free: bool = False) -> None:
    """Integers, booleans, None, upper-case codes and sha256; paths / versions only under inputs / versions."""
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            if not isinstance(k, str) or not _KEY.match(k):
                raise SeedCorpusError(f"report key is not a code token: {k!r}")
            assert_counts_only(v, _free or k in _FREE)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            assert_counts_only(v, _free)
    elif isinstance(obj, str):
        if not (_CODE.match(obj) or _HEX.match(obj) or (_free and _PATH.match(obj) and len(obj) <= 300)):
            raise SeedCorpusError("report string is not a code, hash or input locator")
    elif obj is not None and not isinstance(obj, (bool, int)):
        raise SeedCorpusError(f"report value of type {type(obj).__name__} is not a count")


_PROTECTED = (("ledgers",), ("exports",), ("annotation", "gold"), ("data",))
_LEDGER_NAMES = frozenset(f"{n}.JSONL" for n in ("EVD", "SRC", "SNAP", "COND", "MEAS", "STUDY", "_IDS", "DOC",
                                                 "LIN", "XTR", "ADJ", "KIN", "KINPT", "OBS", "SEXP", "SMP"))


def guard_output_path(path: Path | str, *, root: Path | str = ROOT) -> Path:
    target = Path(path).resolve()
    if target.name.upper() in _LEDGER_NAMES:
        raise SeedCorpusError("refusing a file named like a ledger")
    try:
        parts = tuple(x.casefold() for x in target.relative_to(Path(root).resolve()).parts)
    except ValueError:
        parts = ()
    if any(parts[:len(p)] == p for p in _PROTECTED):
        raise SeedCorpusError("refusing to write inside ledgers/, exports/, annotation/gold/ or data/")
    try:
        assert_safe_write_target(target)
    except ProtectedPathError as e:
        raise SeedCorpusError(str(e)) from e
    if target.exists():
        raise SeedCorpusError("refusing to overwrite an existing file")
    return target


def _write(target: Path, text: str) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return target


def header_record(corpus: SeedCorpus) -> dict:
    head = {"record": "SEED_CORPUS_HEADER", "status": STATUS, "version": VERSION, "dedup_rule": DEDUP_RULE,
            "doi_transforms": list(DOI_TRANSFORMS), "not_applied": list(NOT_APPLIED),
            "field_rule": "SEED_FIELDS_WHITELIST", "abstracts_included": False,
            "licence_rule": "UNKNOWN_UNLESS_STATED_BY_INPUT_NEVER_VERIFIED_BY_CODE", "tdm_rule": "UNKNOWN",
            "ledger_rows_appended": 0, "ids_minted": 0, "inputs": corpus.inputs,
            "seed_count": len(corpus.seeds)}
    assert_counts_only({"inputs": corpus.inputs})                  # the rest are module constants
    return head


def write_seed_corpus(corpus: SeedCorpus, path: Path | str, *, root: Path | str = ROOT) -> Path:
    target = guard_output_path(path, root=root)
    lines = [header_record(corpus), *({k: s[k] for k in SEED_FIELDS} for s in corpus.seeds)]
    return _write(target, "".join(json.dumps(x, sort_keys=True, ensure_ascii=False) + "\n" for x in lines))


def write_counts(counts: Mapping[str, Any], path: Path | str, *, root: Path | str = ROOT) -> Path:
    assert_counts_only(counts)
    target = guard_output_path(path, root=root)
    return _write(target, json.dumps(counts, indent=2, sort_keys=True) + "\n")


def _table(d: Mapping[str, Any]) -> list[str]:
    return ["| key | count |", "|---|---|", *(f"| {k} | {v} |" for k, v in d.items())]


def render_report_md(counts: Mapping[str, Any]) -> str:
    assert_counts_only(counts)
    s = counts["seeds"]
    lines = [
        "# S157 13a-0 offline seed corpus: counts", "",
        f"**Status: {STATUS}.** AI-built (worker prv) and counts only; Kush and Parv review it (D-045). "
        "No network call, no ledger row, no id minted, no abstract or full text.", "",
        f"Dedup rule: `{counts['dedup_rule']}`. DOI transforms applied in order: "
        + ", ".join(f"`{t}`" for t in DOI_TRANSFORMS) + ". Not applied: "
        + ", ".join(f"`{t}`" for t in NOT_APPLIED) + " (see `src/culinarystate/evidence/seed_corpus.py`).", "",
        "## Inputs", "", "| artifact | present | records | DOI valid | invalid | absent |", "|---|---|---|---|---|---|",
    ]
    for a, f in counts["inputs"].items():
        lines.append(f"| {a} | {f.get('present')} | {f.get('records_read', 0)} | {f.get('doi_valid', 0)} | "
                     f"{f.get('doi_invalid_syntax', 0)} | {f.get('doi_absent', 0)} |")
    lines += ["", "## Seeds", "", *_table({k: v for k, v in s.items() if k != "by_n_source_records"}), "",
              "Seeds by number of source records: " + ", ".join(f"{k} = {v}" for k, v in
                                                                 s["by_n_source_records"].items()) + ".", "",
              "## DOI transforms applied (records)", "", *_table(counts["doi_transform_counts"]), "",
              "## DOI seeds per artifact and pairwise overlap", "", *_table(counts["doi_seeds_by_artifact"]), "",
              *_table(counts["doi_seed_overlap_by_artifact_pair"]), "",
              "## Access and licence (as stated by the inputs; nothing verified)", "",
              *_table({f"oa_flag {k}": v for k, v in counts["oa_flag_counts"].items()}), "",
              *_table({f"licence_status {k}": v for k, v in counts["licence_status_counts"].items()}), "",
              "An OA flag is not a reuse licence; `tdm_status` is UNKNOWN for every seed.", "",
              "## Fuzzy duplicates (report only, not applied)", "",
              *_table({k: v for k, v in counts["fuzzy_report_only"].items() if k not in ("method",)}), "",
              "Method: exact equality of casefolded, punctuation-collapsed titles. Route A titles are full "
              "citations, so this under-counts; the 08b detector does real linkage later.", ""]
    return "\n".join(lines)


def write_report_md(counts: Mapping[str, Any], path: Path | str, *, root: Path | str = ROOT) -> Path:
    target = guard_output_path(path, root=root)
    return _write(target, render_report_md(counts))
