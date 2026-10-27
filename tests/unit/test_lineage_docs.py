"""08a.1 DOC records: hashing local files, SNAP agreement, determinism, guard."""
import hashlib
import json
import re
from pathlib import Path

import pytest

from culinarystate.ledgers.store import LedgerStore
from culinarystate.lineage import docs
from culinarystate.lineage.guard import ProtectedPathError

CIT = ("Lombard K., Peffley E., Geoffriau E., Thompson L., Herring A. (2005) Quercetin in onion "
       "(Allium cepa L.) after heat-treatment simulating home preparation. Journal of Food "
       "Composition and Analysis 18 :571-581 PubMed (123)")
BARE = re.sub(r"PubMed \(\d+\)", "", CIT).strip()
T0 = "2026-10-18T00:00:00+00:00"


def _src(store, key, **kw):
    sid = store.ids.mint("SRC", key)
    rec = {"id": sid, "record_type": "SRC", "version": 1, "status": "ACTIVE", "created_at": T0,
           "created_by": "t", "provenance": {"method": "IMPORT", "source_ids": []},
           "verification": {"status": "UNVERIFIED"}, "kind": "DATABASE", "title": key,
           "licence": "x", "licence_status": "ASSUMED", "storage_rule": "COMMIT_OK",
           "primary_or_secondary": "SECONDARY"}
    rec.update(kw)
    store.append(rec)
    return sid


def _snap(store, src, rel, sha, size):
    sid = store.ids.mint("SNAP", f"sha256:{sha}")
    store.append({"id": sid, "record_type": "SNAP", "version": 1, "status": "ACTIVE",
                  "created_at": T0, "created_by": "t",
                  "provenance": {"method": "IMPORT", "source_ids": [src]},
                  "verification": {"status": "UNVERIFIED"}, "source_id": src,
                  "retrieved_at": T0, "sha256": sha, "bytes": size, "local_path": rel,
                  "source_version": "R1"})
    return sid


def _world(tmp_path, name="w"):
    """repo with data/raw + a scratch ledgers root holding synthetic SRC/SNAP."""
    repo = tmp_path / name / "repo"
    root = tmp_path / name / "scratch"
    (root / "data").mkdir(parents=True)
    raw = repo / "data" / "raw"
    (raw / "dirA").mkdir(parents=True)
    (raw / "dirA" / "a.pdf").write_bytes(b"PDFBYTES")
    (raw / "dirA" / "a.txt").write_bytes(b"TEXT")
    (raw / "dirA" / "a.pdf.snap.json").write_text("{}")          # sidecar: never a DOC
    (raw / "dirB" / "html").mkdir(parents=True)
    (raw / "dirB" / "html" / "p1.html").write_bytes(b"<html>1</html>")
    (raw / "dirB" / "html" / "p2.html").write_bytes(b"<html>2</html>")
    (raw / "dirB" / "html" / "p2_copy.html").write_bytes(b"<html>2</html>")   # same bytes
    store = LedgerStore(root / "data")
    store.ids = docs.DeterministicIdMinter(root / "data", T0)
    a = _src(store, "srcA")
    b = _src(store, "srcB", title="B")
    sha = hashlib.sha256(b"PDFBYTES").hexdigest()
    snap = _snap(store, a, "data/raw/dirA/a.pdf", sha, 8)
    return repo, root, {"dirA": a, "dirB": b}, snap, sha


def _run(repo, root, srcmap, **kw):
    return docs.build_file_docs(root / "data", repo, srcmap, created_at=docs.FIXED_CREATED_AT, **kw)


def test_sha256_file_matches_hashlib(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"abc" * 100000)
    assert docs.sha256_file(p) == (hashlib.sha256(b"abc" * 100000).hexdigest(), 300000)


def test_doc_mint_key_format():
    assert docs.doc_mint_key("SRC-000001", "ab" * 32) == "SRC-000001|sha256:" + "ab" * 32


def test_iter_source_files_skips_sidecars_and_is_sorted(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    names = [p.name for p in docs.iter_source_files(repo / "data" / "raw" / "dirA")]
    assert names == ["a.pdf", "a.txt"]


def test_builds_docs_and_mints_by_src_and_sha(tmp_path):
    repo, root, srcmap, snap, sha = _world(tmp_path)
    out = _run(repo, root, srcmap)
    store = LedgerStore(root / "data")
    assert out["files_hashed"] == 5 and out["docs_created"] == 4      # duplicate bytes -> one DOC
    assert out["duplicate_byte_files"] == 1
    for d in store.all_latest("DOC"):
        key = docs.doc_mint_key(d["src_id"], d["sha256"])
        assert store.ids.lookup("DOC", key) == d["id"]
        assert d["verification"] == {"status": "UNVERIFIED"}
    assert out["docs_by_src"] == {srcmap["dirA"]: 2, srcmap["dirB"]: 2}


def test_same_bytes_under_two_src_mint_two_docs(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    (repo / "data" / "raw" / "dirB" / "html" / "p3.html").write_bytes(b"TEXT")   # = dirA/a.txt bytes
    _run(repo, root, srcmap)
    store = LedgerStore(root / "data")
    h = hashlib.sha256(b"TEXT").hexdigest()
    ids = {d["id"] for d in store.all_latest("DOC") if d["sha256"] == h}
    assert len(ids) == 2


def test_snap_linked_and_sha_equal(tmp_path):
    repo, root, srcmap, snap, sha = _world(tmp_path)
    _run(repo, root, srcmap)
    store = LedgerStore(root / "data")
    pdf = next(d for d in store.all_latest("DOC") if d["sha256"] == sha)
    assert pdf["snapshot_id"] == snap
    assert pdf["provenance"]["snapshot_ids"] == [snap]
    assert pdf["retrieved_at"] == T0
    txt = next(d for d in store.all_latest("DOC") if d["local_path"].endswith("a.txt"))
    assert txt["snapshot_id"] is None


def test_snap_linked_when_snap_path_is_absolute(tmp_path):
    repo, root, srcmap, snap, sha = _world(tmp_path)
    # rewrite SNAP with an absolute path, as SNAP-000006 (Bognar) has
    store = LedgerStore(root / "data")
    s = store.latest(snap)
    store.append({**s, "version": 2, "local_path": str(repo / "data/raw/dirA/a.pdf")})
    _run(repo, root, srcmap)
    pdf = next(d for d in LedgerStore(root / "data").all_latest("DOC") if d["sha256"] == sha)
    assert pdf["snapshot_id"] == snap


def test_snap_sha_mismatch_aborts(tmp_path):
    repo, root, srcmap, snap, sha = _world(tmp_path)
    (repo / "data/raw/dirA/a.pdf").write_bytes(b"CHANGED!")
    with pytest.raises(docs.DocSnapMismatch):
        _run(repo, root, srcmap)
    assert not (root / "data" / "DOC.jsonl").exists()      # nothing written on failure


def test_validate_doc_snap_rejects_different_src(tmp_path):
    snaps = {"SNAP-000001": {"id": "SNAP-000001", "source_id": "SRC-000009", "sha256": "a" * 64}}
    doc = {"snapshot_id": "SNAP-000001", "sha256": "a" * 64, "src_id": "SRC-000001"}
    with pytest.raises(docs.DocSnapMismatch):
        docs.validate_doc_snap(doc, snaps)
    docs.validate_doc_snap({**doc, "src_id": "SRC-000009"}, snaps)
    with pytest.raises(docs.DocSnapMismatch):
        docs.validate_doc_snap({**doc, "src_id": "SRC-000009", "sha256": "b" * 64}, snaps)


def test_report_kind_follows_src_not_guessed(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    _run(repo, root, srcmap)
    for d in LedgerStore(root / "data").all_latest("DOC"):
        assert d["report_kind"] == "COMPILATION_DATABASE" and d["is_compilation_hub"] == "YES"
        assert d["authorship"]["status"] == "UNKNOWN" and d["authorship"]["authors_raw"] == []


def test_unknown_src_nature_stays_unknown(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    store = LedgerStore(root / "data")
    s = store.latest(srcmap["dirB"])
    store.append({**s, "version": 2, "primary_or_secondary": "UNKNOWN"})
    _run(repo, root, srcmap)
    for d in LedgerStore(root / "data").all_latest("DOC"):
        if d["src_id"] == srcmap["dirB"]:
            assert d["report_kind"] == "UNKNOWN" and d["is_compilation_hub"] == "UNKNOWN"


def test_rerun_is_idempotent_no_growth(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    _run(repo, root, srcmap)
    before = {p.name: p.read_bytes() for p in (root / "data").glob("*.jsonl")}
    out = _run(repo, root, srcmap)
    assert out["docs_created"] == 0 and out["docs_unchanged"] == 4
    assert before == {p.name: p.read_bytes() for p in (root / "data").glob("*.jsonl")}


def test_two_fresh_roots_are_byte_identical(tmp_path):
    outs = []
    for n in ("one", "two"):
        repo, root, srcmap, *_ = _world(tmp_path, n)
        _run(repo, root, srcmap)
        # same local_path text across worlds: repo-relative only
        outs.append(((root / "data" / "DOC.jsonl").read_bytes(), (root / "data" / "_ids.jsonl").read_bytes()))
    assert outs[0] == outs[1]
    assert b"minted_at" in outs[0][1] and docs.FIXED_CREATED_AT.encode() in outs[0][1]


def test_local_path_is_repo_relative(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    _run(repo, root, srcmap)
    for d in LedgerStore(root / "data").all_latest("DOC"):
        assert d["local_path"].startswith("data/raw/")


def test_refuses_protected_ledger_root(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    bad = tmp_path / "x" / "ledgers" / "data"
    bad.mkdir(parents=True)
    with pytest.raises(ProtectedPathError):
        docs.build_file_docs(bad, repo, srcmap, created_at=docs.FIXED_CREATED_AT)


def test_missing_or_inactive_src_aborts(tmp_path):
    repo, root, srcmap, *_ = _world(tmp_path)
    with pytest.raises(KeyError):
        _run(repo, root, {"dirA": "SRC-999999"})


# ---------- PE publication metadata DOCs ----------
def _pe_world(tmp_path, name="pe", resolved=True):
    repo, root, srcmap, *_ = _world(tmp_path, name)
    store = LedgerStore(root / "data")
    store.ids = docs.DeterministicIdMinter(root / "data", T0)
    pe_db = _src(store, "pedb", kind="DATABASE")
    pub = _src(store, "pub1", kind="PAPER", title=CIT, primary_or_secondary="PRIMARY",
               licence_status="UNKNOWN", storage_rule="DERIVED_ONLY",
               provenance={"method": "IMPORT", "source_ids": [pe_db]})
    other = _src(store, "pub2", kind="PAPER", title="Unrelated paper (1999) x", licence_status="UNKNOWN",
                 storage_rule="DERIVED_ONLY", provenance={"method": "IMPORT", "source_ids": []})
    cache = repo / "data" / "raw" / "doi_resolve"
    (cache / "crossref").mkdir(parents=True)
    (cache / "openalex_doi").mkdir(parents=True)
    title = ("Quercetin in onion (Allium cepa L.) after heat-treatment simulating home preparation"
             if resolved else "Something else entirely different words here")
    items = [{"DOI": "10.1016/J.JFCA.2004.10.0", "title": [title], "issued": {"date-parts": [[2005, 9]]}}]
    (cache / "crossref" / f"{docs.crossref_key(BARE)}.json").write_text(
        json.dumps({"message": {"items": items}}))
    (cache / "openalex_doi" / f"{docs.crossref_key('10.1016/j.jfca.2004.10.0')}.json").write_text(
        json.dumps({"open_access": {"is_oa": False}}))
    return repo, root, pe_db, pub, other, cache


def test_pe_metadata_docs_resolved(tmp_path):
    repo, root, pe_db, pub, other, cache = _pe_world(tmp_path)
    out = docs.build_pe_metadata_docs(root / "data", repo, pe_db, cache,
                                      created_at=docs.FIXED_CREATED_AT)
    assert out["pe_publications"] == 1 and out["crossref_files_found"] == 1
    assert out["resolved"] == 1 and out["unresolved"] == 0 and out["openalex_files_found"] == 1
    ds = [d for d in LedgerStore(root / "data").all_latest("DOC") if d["src_id"] == pub]
    assert len(ds) == 2
    for d in ds:
        assert d["doc_kind"] == "METADATA_RECORD" and d["content_access"] == "METADATA_ONLY"
        assert d["identifiers"]["doi"] == "10.1016/j.jfca.2004.10.0"
        assert d["licence_status"] == "UNKNOWN" and d["storage_rule"] == "DERIVED_ONLY"
        assert d["authorship"]["status"] == "UNKNOWN"
    assert out["doc_ids_by_src"][pub] == sorted(d["id"] for d in ds)
    # the non-PE paper (provenance does not name the PE database) is untouched
    assert other not in out["doc_ids_by_src"]


def test_pe_metadata_unresolved_makes_no_doc(tmp_path):
    repo, root, pe_db, pub, other, cache = _pe_world(tmp_path, "pe2", resolved=False)
    out = docs.build_pe_metadata_docs(root / "data", repo, pe_db, cache,
                                      created_at=docs.FIXED_CREATED_AT)
    assert out["resolved"] == 0 and out["unresolved"] == 1 and out["docs_created"] == 0
    assert "DOC" not in {p.stem for p in (root / "data").glob("*.jsonl")}


def test_pe_metadata_never_downloads(tmp_path, monkeypatch):
    import socket
    def boom(*a, **k):
        raise AssertionError("network used")
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket.socket, "connect", boom)
    repo, root, pe_db, pub, other, cache = _pe_world(tmp_path, "pe3")
    (cache / "crossref" / f"{docs.crossref_key(BARE)}.json").unlink()      # cache miss
    out = docs.build_pe_metadata_docs(root / "data", repo, pe_db, cache, created_at=docs.FIXED_CREATED_AT)
    assert out["crossref_files_found"] == 0 and out["cache_missing"] == 1


def test_pe_metadata_deterministic(tmp_path):
    res = []
    for n in ("a", "b"):
        repo, root, pe_db, pub, other, cache = _pe_world(tmp_path, n)
        docs.build_pe_metadata_docs(root / "data", repo, pe_db, cache, created_at=docs.FIXED_CREATED_AT)
        res.append(((root / "data" / "DOC.jsonl").read_bytes(), (root / "data" / "_ids.jsonl").read_bytes()))
    assert res[0] == res[1]
