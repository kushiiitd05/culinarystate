"""08a.1: DOC records for every SRC actually read (local files, sha256; no downloads).

Mint key (D-029 D-11): `<src_id>|sha256:<hex>`. DOC.sha256 must equal SNAP.sha256 where a SNAP exists
(JSON Schema cannot say so; `validate_doc_snap` does). Output goes only to a ledgers root that passes
`assert_safe_write_target`, i.e. never the repo's real `ledgers/data`.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from ..evidence.doi_resolve import _key as crossref_key  # noqa: F401  (same cache-file naming)
from ..evidence.doi_resolve import accept, title_match
from ..ledgers.registry import R
from ..ledgers.store import IdMinter, LedgerStore, _append_jsonl, _read_jsonl
from .guard import assert_safe_write_target

FIXED_CREATED_AT = "2026-10-27T00:00:00+00:00"
CREATED_BY = "Kush+Claude"
AGENT = "rule:step08a_docs@0.1"
_CHUNK = 1 << 20
_MEDIA = {".pdf": "application/pdf", ".txt": "text/plain", ".html": "text/html", ".htm": "text/html",
          ".json": "application/json", ".csv": "text/csv"}


class DocSnapMismatch(ValueError):
    """DOC.sha256 (or src) disagrees with the SNAP it claims to be."""


class DeterministicIdMinter(IdMinter):
    """IdMinter with a caller-supplied `minted_at`, so two rebuilds give byte-identical `_ids.jsonl`."""

    def __init__(self, root: Path, minted_at: str):
        super().__init__(root)
        self.minted_at = minted_at

    def mint(self, prefix: str, key: str | None = None) -> str:
        if prefix not in R:
            raise KeyError(f"unknown prefix {prefix}")
        if key is not None and (prefix, key) in self._by_key:
            return self._by_key[(prefix, key)]
        new_id = f"{prefix}-{self._max.get(prefix, 0) + 1:06d}"
        row = {"id": new_id, "prefix": prefix, "key": key, "minted_at": self.minted_at}
        _append_jsonl(self.path, row)
        self._index(row)
        return new_id


def sha256_file(path: Path) -> tuple[str, int]:
    h, n = hashlib.sha256(), 0
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(_CHUNK), b""):
            h.update(block)
            n += len(block)
    return h.hexdigest(), n


def doc_mint_key(src_id: str, sha256_hex: str) -> str:
    return f"{src_id}|sha256:{sha256_hex}"


def iter_source_files(directory: Path) -> list[Path]:
    """Files under directory, sorted by posix path; `*.snap.json` bookkeeping sidecars are skipped."""
    files = [p for p in Path(directory).rglob("*") if p.is_file() and not p.name.endswith(".snap.json")]
    return sorted(files, key=lambda p: p.as_posix())


def validate_doc_snap(doc: dict, snaps: dict[str, dict]) -> None:
    sid = doc.get("snapshot_id")
    if sid is None:
        return
    snap = snaps.get(sid)
    if snap is None:
        raise DocSnapMismatch(f"{sid}: SNAP not found")
    if snap["source_id"] != doc["src_id"]:
        raise DocSnapMismatch(f"{sid}: SNAP source {snap['source_id']} != DOC src {doc['src_id']}")
    if snap["sha256"] != doc["sha256"]:
        raise DocSnapMismatch(f"{sid}: SNAP sha256 != DOC sha256")


def _latest(rows: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in rows:
        out[r["id"]] = r
    return out


def _norm_path(p: str | None, repo: Path) -> str | None:
    if not p:
        return None
    path = Path(p)
    if path.is_absolute():
        try:
            path = path.relative_to(repo)
        except ValueError:
            return path.as_posix()
    return path.as_posix()


def _classify(src: dict) -> tuple[str, str]:
    """(report_kind, is_compilation_hub) from the SRC's own primary_or_secondary; never guessed."""
    nature = src.get("primary_or_secondary", "UNKNOWN")
    if nature in ("SECONDARY", "TERTIARY"):
        return "COMPILATION_DATABASE", "YES"
    if nature == "PRIMARY":
        return "PRIMARY_REPORT", "NO"
    return "UNKNOWN", "UNKNOWN"


_AUTHORSHIP_UNKNOWN = {"status": "UNKNOWN", "authors_raw": [], "affiliations_raw": [],
                       "corresponding_author_raw": None, "year_published": None}


def _doc_record(*, src: dict, sha: str, size: int, rel: str, created_at: str, created_by: str,
                snap: dict | None, doc_kind: str, content_access: str, report_kind: str, hub: str,
                version_label: str, identifiers: dict, notes: str) -> dict:
    prov = {"method": "IMPORT", "source_ids": [src["id"]], "agent": AGENT, "locator": rel, "notes": None}
    if snap:
        prov["snapshot_ids"] = [snap["id"]]
    return {
        "record_type": "DOC", "version": 1, "status": "ACTIVE", "created_at": created_at,
        "created_by": created_by, "provenance": prov, "verification": {"status": "UNVERIFIED"},
        "notes": notes, "src_id": src["id"], "snapshot_id": snap["id"] if snap else None,
        "sha256": sha, "bytes": size, "media_type": _MEDIA.get(Path(rel).suffix.lower()),
        "doc_kind": doc_kind, "content_access": content_access, "report_kind": report_kind,
        "is_compilation_hub": hub, "authorship": dict(_AUTHORSHIP_UNKNOWN), "version_label": version_label,
        "edition_version": snap.get("source_version") if snap else None, "identifiers": identifiers,
        "retrieved_at": snap.get("retrieved_at") if snap else None, "local_path": rel,
        "licence_status": src["licence_status"], "storage_rule": src["storage_rule"],
    }


def _doc_kind(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "FULL_TEXT_PDF", "FULL_TEXT"
    if ext in (".html", ".htm"):
        return "WEB_PAGE_SNAPSHOT", "UNKNOWN"
    if ext == ".txt":
        return "OTHER", "FULL_TEXT"
    if ext == ".csv":
        return "TABLE_FILE", "UNKNOWN"
    return "UNKNOWN", "UNKNOWN"


def _open_store(root: Path, minted_at: str) -> LedgerStore:
    root = Path(root)
    for name in ("DOC.jsonl", "_ids.jsonl"):
        assert_safe_write_target(root / name)
    store = LedgerStore(root)
    store.ids = DeterministicIdMinter(root, minted_at)
    return store


def _write(store: LedgerStore, records: list[dict], minted_at: str) -> Counter:
    """Mint (sorted order) and upsert; returns Counter of created/unchanged/revised."""
    res: Counter = Counter()
    for rec in sorted(records, key=lambda r: (r["src_id"], r["local_path"])):
        rec = {**rec, "id": store.ids.mint("DOC", doc_mint_key(rec["src_id"], rec["sha256"]))}
        status, _ = store.upsert(rec)
        res[status] += 1
    return res


def build_file_docs(ledgers_data: Path, repo_root: Path, srcmap: dict[str, str], *, created_at: str,
                    created_by: str = CREATED_BY, raw_subdir: str = "data/raw") -> dict:
    """Hash every file of data/raw/<dir> and write one DOC per distinct (src_id, sha256)."""
    repo_root = Path(repo_root)
    store = _open_store(ledgers_data, created_at)
    srcs = {}
    for d, sid in srcmap.items():
        src = store.latest(sid)
        if src is None or src.get("status") != "ACTIVE":
            raise KeyError(f"{sid}: SRC missing or not ACTIVE")
        srcs[sid] = src
    snaps = _latest(_read_jsonl(Path(ledgers_data) / "SNAP.jsonl"))
    groups: dict[tuple[str, str], list[tuple[str, int]]] = {}
    n_files = 0
    for d in sorted(srcmap):
        sid = srcmap[d]
        for p in iter_source_files(repo_root / raw_subdir / d):
            sha, size = sha256_file(p)
            rel = p.relative_to(repo_root).as_posix()
            groups.setdefault((sid, sha), []).append((rel, size))
            n_files += 1
    records, dup = [], 0
    for (sid, sha), members in sorted(groups.items()):
        members.sort()
        rel, size = members[0]
        dup += len(members) - 1
        snap = _find_snap(snaps, sid, [m[0] for m in members], sha, repo_root)
        src = srcs[sid]
        kind, access = _doc_kind(Path(rel))
        rk, hub = _classify(src)
        notes = (f"08a.1: local file hashed (sha256). Same bytes also at: {', '.join(m[0] for m in members[1:])}."
                 if len(members) > 1 else "08a.1: local file hashed (sha256).")
        rec = _doc_record(src=src, sha=sha, size=size, rel=rel, created_at=created_at, created_by=created_by,
                          snap=snap, doc_kind=kind, content_access=access, report_kind=rk, hub=hub,
                          version_label="DATABASE_RELEASE" if src.get("kind") == "DATABASE" else "UNKNOWN",
                          identifiers={}, notes=notes)
        validate_doc_snap(rec, snaps)
        records.append(rec)
    res = _write(store, records, created_at)       # nothing is written above this line
    by_src = Counter(r["src_id"] for r in records)
    return {"files_hashed": n_files, "docs_created": res["created"], "docs_unchanged": res["unchanged"],
            "docs_revised": res["revised"], "duplicate_byte_files": dup, "docs_by_src": dict(by_src),
            "files_by_src": dict(Counter(k[0] for k, v in groups.items() for _ in v))}


def _find_snap(snaps: dict[str, dict], src_id: str, rels: list[str], sha: str, repo: Path) -> dict | None:
    mine = [s for s in sorted(snaps.values(), key=lambda s: s["id"]) if s["source_id"] == src_id]
    for s in mine:
        if s["sha256"] == sha:
            return s
    for s in mine:                                   # same file path, different bytes: hard stop
        if _norm_path(s.get("local_path"), repo) in rels:
            raise DocSnapMismatch(f"{s['id']}: file {s.get('local_path')} sha256 differs from SNAP")
    return None


def build_pe_metadata_docs(ledgers_data: Path, repo_root: Path, pe_src_id: str, cache_dir: Path, *,
                           created_at: str, created_by: str = CREATED_BY) -> dict:
    """METADATA_RECORD DOCs for PE publications from the existing doi_resolve cache (read-only).

    A DOC is written only when Crossref's cached response contains an item that passes the same
    `accept` test the resolver used; an unresolved cache file is a search response with no match, so
    it is not a manifestation of the paper. Never touches the network.
    """
    repo_root, cache_dir = Path(repo_root), Path(cache_dir)
    store = _open_store(ledgers_data, created_at)
    papers = sorted((s for s in store.all_latest("SRC") if s["kind"] == "PAPER" and s["status"] == "ACTIVE"
                     and pe_src_id in s["provenance"]["source_ids"]), key=lambda s: s["id"])
    import json
    c: Counter = Counter()
    c.update({k: 0 for k in ("cache_missing", "crossref_files_found", "openalex_files_found", "resolved",
                             "unresolved")})
    c["pe_publications"] = len(papers)
    records, links = [], {}
    for src in papers:
        q = re.sub(r"PubMed \(\d+\)", "", src["title"]).strip()
        cr = cache_dir / "crossref" / f"{crossref_key(q)}.json"
        if not cr.is_file():
            c["cache_missing"] += 1
            continue
        c["crossref_files_found"] += 1
        items = ((json.loads(cr.read_text()).get("message") or {}).get("items")) or []
        best = next((it for it in items if accept(it, q)), None)
        if best is None:
            c["unresolved"] += 1
            continue
        c["resolved"] += 1
        doi = best["DOI"].lower()
        files = [(cr, f"Crossref bibliographic search response (top 3 items) cached by evidence.doi_resolve; "
                      f"item accepted: DOI {doi}, title match {title_match(best['title'][0], q)}. "
                      "The file is a search response, not the paper.")]
        oa = cache_dir / "openalex_doi" / f"{crossref_key(doi)}.json"
        if oa.is_file():
            c["openalex_files_found"] += 1
            files.append((oa, f"OpenAlex open-access lookup by DOI {doi} cached by evidence.doi_resolve; "
                              "metadata only."))
        for path, note in files:
            sha, size = sha256_file(path)
            rec = _doc_record(src=src, sha=sha, size=size, rel=path.relative_to(repo_root).as_posix(),
                              created_at=created_at, created_by=created_by, snap=None,
                              doc_kind="METADATA_RECORD", content_access="METADATA_ONLY",
                              report_kind="OTHER", hub="NO", version_label="UNKNOWN",
                              identifiers={"doi": doi}, notes="08a.1: " + note)
            records.append(rec)
    res = _write(store, records, created_at)
    ids = {}
    for r in records:
        ids.setdefault(r["src_id"], []).append(
            store.ids.lookup("DOC", doc_mint_key(r["src_id"], r["sha256"])))
    return {**dict(c), "docs_created": res["created"], "docs_unchanged": res["unchanged"],
            "doc_ids_by_src": {k: sorted(v) for k, v in ids.items()}}
