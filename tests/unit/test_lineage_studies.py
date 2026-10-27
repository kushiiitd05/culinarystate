"""08a.2 STUDY appended versions + new STUDY/SRC nodes for PE yield-source publications."""
import hashlib
import json

import pytest

from culinarystate.ledgers.store import LedgerStore
from culinarystate.lineage import docs, studies
from culinarystate.lineage.guard import ProtectedPathError

T0 = "2026-10-18T00:00:00+00:00"
FIX = "2026-10-27T00:00:00+00:00"


def _rec(rtype, rid, **kw):
    r = {"id": rid, "record_type": rtype, "version": 1, "status": "ACTIVE", "created_at": T0,
         "created_by": "t", "provenance": {"method": "IMPORT", "source_ids": []},
         "verification": {"status": "UNVERIFIED"}}
    r.update(kw)
    return r


def _world(tmp_path, name="w", n_pub=2):
    root = tmp_path / name / "scratch" / "data"
    root.mkdir(parents=True)
    st = LedgerStore(root)
    st.ids = docs.DeterministicIdMinter(root, T0)
    db = st.ids.mint("SRC", "pedb")
    st.append(_rec("SRC", db, kind="DATABASE", title="PE", licence="x", licence_status="VERIFIED",
                   storage_rule="DERIVED_ONLY"))
    pubs, stds = [], []
    for i in range(n_pub):
        s = st.ids.mint("SRC", f"pub{i}")
        st.append(_rec("SRC", s, kind="PAPER", title=f"P{i}", licence="x", licence_status="UNKNOWN",
                       storage_rule="DERIVED_ONLY"))
        u = st.ids.mint("STUDY", f"pe_pub:{i}")
        st.append(_rec("STUDY", u, source_id=s, design="UNKNOWN"))
        pubs.append(s)
        stds.append(u)
    # a DOC id so report_doc_ids refs are real-looking
    d = st.ids.mint("DOC", f"{pubs[0]}|sha256:{'a' * 64}")
    evd = root.parent / "evd.jsonl"
    rows = []
    for k, (u, org) in enumerate(((stds[0], "PRIMARY_STUDY"), (stds[1], "PRIMARY_STUDY"))):
        rows.append({"id": f"EVD-{k + 1:06d}", "status": "ACTIVE", "study_ids": [u], "origin_type": org,
                     "source_id": db, "process": {"modifiers": {"yield_source": "BERGSTROM 1994_X",
                                                                "yield_food": f"food{k}"}}})
    rows.append({"id": "EVD-000003", "status": "ACTIVE", "study_ids": [stds[0]], "origin_type": "PRIMARY_STUDY",
                 "source_id": db, "process": {"modifiers": {"yield_source": "UNSPECIFIED", "yield_food": "f"}}})
    rows.append({"id": "EVD-000004", "status": "ACTIVE", "study_ids": [stds[0]], "origin_type": "PRIMARY_STUDY",
                 "source_id": db, "process": {"modifiers": {"yield_source": "GOULAS 2011", "yield_food": "f"}}})
    rows.append({"id": "EVD-000004", "status": "ACTIVE", "study_ids": [stds[0]], "origin_type": "PRIMARY_STUDY",
                 "source_id": db, "process": {"modifiers": {"yield_source": "GOULAS 2011", "yield_food": "f"}}, "version": 2})
    rows.append({"id": "EVD-000005", "status": "ACTIVE", "study_ids": [], "origin_type": "PRIMARY_STUDY",
                 "source_id": "SRC-999999", "process": {"modifiers": {"yield_source": "NOPE", "yield_food": "f"}}})
    evd.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return root, db, pubs, stds, d, evd


def test_origin_types_from_evd(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    ot = studies.origin_types_from_evd(evd)
    assert ot[stds[0]] == {"PRIMARY_STUDY"}


def test_collect_yield_sources_skips_unspecified_and_counts_latest_rows(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    ys = studies.collect_yield_sources(evd, db)
    assert set(ys) == {"BERGSTROM 1994_X", "GOULAS 2011"}          # NOPE: other source; UNSPECIFIED skipped
    assert ys["BERGSTROM 1994_X"]["rows"] == 2
    assert ys["GOULAS 2011"]["rows"] == 1                            # latest version of an id only
    assert ys["BERGSTROM 1994_X"]["yield_foods"] == ["food0", "food1"]


def test_study_schema_accepts_additive_fields_only_when_valid():
    from jsonschema import Draft202012Validator
    v = Draft202012Validator(studies.study_schema())
    base = _rec("STUDY", "STUDY-000001", source_id="SRC-000001", design="UNKNOWN", version=2)
    assert not list(v.iter_errors({**base, "origin_type": "PRIMARY_STUDY", "report_doc_ids": ["DOC-000001"]}))
    assert list(v.iter_errors({**base, "origin_type": "MADE_UP"}))
    assert list(v.iter_errors({**base, "report_doc_ids": ["X-1"]}))
    assert list(v.iter_errors({**base, "design": "NOT_IDENTIFIABLE"}))     # never a design value


def test_append_report_versions_is_append_only(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    p = root / "STUDY.jsonl"
    before = p.read_bytes()
    out = studies.append_report_versions(root, {pubs[0]: [d]}, studies.origin_types_from_evd(evd),
                                         created_at=FIX)
    after = p.read_bytes()
    assert after.startswith(before) and len(after) > len(before)
    assert out["versions_appended"] == 2
    st = LedgerStore(root)
    s0, s1 = st.latest(stds[0]), st.latest(stds[1])
    assert s0["version"] == 2 and s0["report_doc_ids"] == [d] and s0["origin_type"] == "PRIMARY_STUDY"
    assert s1["report_doc_ids"] == [] and s1["design"] == "UNKNOWN"
    assert s0["created_at"] == FIX and s0["verification"] == {"status": "UNVERIFIED"}
    assert st.history(stds[0])[0]["version"] == 1


def test_ambiguous_origin_type_is_omitted_not_guessed(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    studies.append_report_versions(root, {}, {stds[0]: {"PRIMARY_STUDY", "REVIEW_AGGREGATE"}}, created_at=FIX)
    assert "origin_type" not in LedgerStore(root).latest(stds[0])


def test_append_report_versions_idempotent(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    ot = studies.origin_types_from_evd(evd)
    studies.append_report_versions(root, {pubs[0]: [d]}, ot, created_at=FIX)
    b = (root / "STUDY.jsonl").read_bytes()
    out = studies.append_report_versions(root, {pubs[0]: [d]}, ot, created_at=FIX)
    assert out["versions_appended"] == 0 and (root / "STUDY.jsonl").read_bytes() == b


def test_yield_nodes_new_src_in_sidecar_never_in_src_ledger(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    src_before = (root / "SRC.jsonl").read_bytes()
    ys = studies.collect_yield_sources(evd, db)
    out = studies.add_yield_source_nodes(root, db, ys, created_at=FIX)
    assert (root / "SRC.jsonl").read_bytes() == src_before
    assert out["src_created"] == 2 and out["study_created"] == 2
    side = [json.loads(x) for x in (root / studies.SRC_SIDECAR).read_text().splitlines()]
    assert [r["title"] for r in side] == ["BERGSTROM 1994_X", "GOULAS 2011"]
    for r in side:
        assert r["kind"] == "PAPER" and r["licence_status"] == "UNKNOWN" and r["year"] is None
        assert r["provenance"]["source_ids"] == [db] and "doi" not in r
    st = LedgerStore(root)
    new = [s for s in st.all_latest("STUDY") if s["id"] not in stds]
    assert len(new) == 2
    for s in new:
        assert s["design"] == "UNKNOWN" and s["report_doc_ids"] == [] and "origin_type" not in s
        assert s["source_id"] in {r["id"] for r in side}
    assert "NOT_IDENTIFIABLE" not in (root / "STUDY.jsonl").read_text()


def test_yield_nodes_idempotent_and_id_stable(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    ys = studies.collect_yield_sources(evd, db)
    studies.add_yield_source_nodes(root, db, ys, created_at=FIX)
    snap = {p.name: p.read_bytes() for p in root.glob("*.jsonl")}
    out = studies.add_yield_source_nodes(root, db, ys, created_at=FIX)
    assert out["src_created"] == 0 and out["study_created"] == 0
    assert snap == {p.name: p.read_bytes() for p in root.glob("*.jsonl")}


def test_full_run_deterministic_across_fresh_roots(tmp_path):
    outs = []
    for n in ("a", "b"):
        root, db, pubs, stds, d, evd = _world(tmp_path, n)
        studies.run_08a2(root, db, {pubs[0]: [d]}, evd, created_at=FIX)
        outs.append({p.name: p.read_bytes() for p in root.glob("*.jsonl")})
    assert outs[0] == outs[1]


def test_prefix_guard_detects_rewrite(tmp_path):
    p = tmp_path / "S.jsonl"
    p.write_bytes(b"line1\nline2\n")
    sha = hashlib.sha256(b"line1\nline2\n").hexdigest()
    studies.check_prefix_unchanged(p, 12, sha)
    p.write_bytes(b"line1\nline2\nmore\n")
    studies.check_prefix_unchanged(p, 12, sha)                       # append is fine
    p.write_bytes(b"lineX\nline2\nmore\n")
    with pytest.raises(studies.AppendOnlyViolation):
        studies.check_prefix_unchanged(p, 12, sha)
    p.write_bytes(b"line1\n")
    with pytest.raises(studies.AppendOnlyViolation):                 # truncated
        studies.check_prefix_unchanged(p, 12, sha)


def test_run_aborts_if_prefix_changes(tmp_path):
    root, db, pubs, stds, d, evd = _world(tmp_path)
    good = hashlib.sha256((root / "STUDY.jsonl").read_bytes()).hexdigest()
    n = (root / "STUDY.jsonl").stat().st_size
    studies.run_08a2(root, db, {pubs[0]: [d]}, evd, created_at=FIX, expect_prefix=(n, good))
    with pytest.raises(studies.AppendOnlyViolation):
        studies.run_08a2(root, db, {}, evd, created_at=FIX, expect_prefix=(n, "0" * 64))


def test_refuses_protected_root(tmp_path):
    bad = tmp_path / "ledgers" / "data"
    bad.mkdir(parents=True)
    with pytest.raises(ProtectedPathError):
        studies.append_report_versions(bad, {}, {}, created_at=FIX)
    with pytest.raises(ProtectedPathError):
        studies.add_yield_source_nodes(bad, "SRC-000001", {}, created_at=FIX)
