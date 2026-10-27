"""Step 08b-v0 library tests: G08b-1 (determinism, idempotence, seeded fixture as a code-path unit test),
G08b-2 (rule_version on every output), G08b-4 (offline, writes only under the supplied path).
Synthetic data and tmp dirs only; no real ledger is read. No precision/recall claim is made here."""
from __future__ import annotations

import ast
import builtins
import hashlib
import io
import json
import socket
import sys
from pathlib import Path

import pytest

from culinarystate.lineage import detectors, keys, seeding
from culinarystate.lineage import library as L
from culinarystate.lineage.guard import ProtectedPathError

REPO = Path(__file__).resolve().parents[2]
SRC = "SRC-000001"


# ------------------------------------------------------------------ fixtures
def mk(i, *, src="SRC-000001", loc=None, analyte="Vitamin C", matrix="Spinach", process="boil",
       vals=(("retention", 55.5, "%"),), doc=None):
    return {
        "id": f"EVD-{i:06d}", "source_id": src, "family": "F", "locator": loc if loc is not None else f"loc {i}",
        "analyte": analyte, "matrix": matrix, "process": process, "steps": [process],
        "values": [{"role": r, "value": v, "unit": u, "basis": None} for r, v, u in vals],
        "doc_ref": doc, "origin_type": "DATABASE_AGGREGATE", "moisture_fraction": None,
    }


def items():
    return [mk(1), mk(2, vals=(("retention", 55.5, "%"),)), mk(3, analyte="Folate", vals=(("retention", 10.0, "%"),)),
            mk(4, analyte="Folate", vals=(("retention", 10.0, "%"),), loc="loc 3")]


def row(i, study=None):
    return {"id": f"EVD-{i:06d}", "study_ids": [study] if study else [],
            "study_id_status": "PRESENT" if study else "NOT_IDENTIFIABLE",
            "source_id": "SRC-A", "source_family_id": f"FAM-{i}"}


STUDIES = {"STUDY-000001": {"id": "STUDY-000001", "report_doc_ids": ["DOC-000001"]}}
DOCS = {"DOC-000001": {"id": "DOC-000001", "src_id": "SRC-P1", "is_compilation_hub": "NO",
                       "report_kind": "OTHER", "authorship": {"status": "UNKNOWN"}}}
SRCS = {"SRC-A": {"id": "SRC-A", "kind": "DATABASE"}}


def jbytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True).encode()


# ------------------------------------------------------------------ rule_version (G08b-2)
def test_rule_version_recipe_is_reproducible_and_sensitive():
    consts = L.rule_constants()
    text = "\n".join(f"{k}={consts[k]!r}" for k in sorted(consts))
    assert L.RULE_VERSION == "lib-v0-" + hashlib.sha256(text.encode()).hexdigest()
    assert consts["detectors.RULE_VERSION"] == detectors.RULE_VERSION
    assert consts["keys.RULE_VERSION"] == keys.RULE_VERSION
    assert consts["detectors.B3_CUT"] == 0.75
    changed = dict(consts, **{"detectors.B3_CUT": 0.8})
    assert L.hash_rule_constants(changed) != L.RULE_VERSION


def test_every_output_record_carries_rule_version(tmp_path):
    outs = []
    outs.append(L.register_document(SRC, b"abc", tmp_path / "o"))
    edges = L.propose_edges(items())
    assert edges["edges"], "fixture must yield edges"
    outs += [edges] + edges["edges"]
    ks = L.assign_keys([row(1, "STUDY-000001"), row(2)], STUDIES, DOCS, SRCS, edges["edges"])
    outs += [ks] + ks["records"]
    dj = L.check_disjointness(ks["records"], expected_rows=2, studies=STUDIES, docs=DOCS)
    outs += [dj] + [v for v in dj["checks"].values()]
    assert all(o.get("rule_version") == L.RULE_VERSION for o in outs)  # 100%
    # the library hash replaces, never hides, the 08a versions
    assert edges["edges"][0]["detector_rule_version"] == detectors.RULE_VERSION
    assert ks["records"][0]["keys_rule_version"] == keys.RULE_VERSION


# ------------------------------------------------------------------ G08b-1 determinism / idempotence
def test_propose_edges_deterministic_and_order_independent():
    a = L.propose_edges(items())
    b = L.propose_edges(list(reversed(items())))
    assert jbytes(a) == jbytes(b) == jbytes(L.propose_edges(iter(items())))


def test_propose_edges_does_not_mutate_input():
    its = items()
    before = json.dumps(its, sort_keys=True)
    L.propose_edges(its)
    assert json.dumps(its, sort_keys=True) == before


def test_propose_edges_matches_08a_detector_exactly():
    raw, _ = detectors.detect_edges(items())
    lib = L.propose_edges(items())["edges"]
    strip = lambda e: {k: v for k, v in e.items() if k not in ("rule_version", "detector_rule_version")}
    assert [strip(e) for e in lib] == [strip(e) for e in raw]


def test_assign_keys_deterministic_and_matches_08a():
    edges = L.propose_edges(items())["edges"]
    rows = [row(1, "STUDY-000001"), row(2), row(3), row(4)]
    a = L.assign_keys(rows, STUDIES, DOCS, SRCS, edges)
    b = L.assign_keys(list(reversed(rows)), STUDIES, DOCS, SRCS, list(reversed(edges)))
    assert jbytes(a) == jbytes(b)
    raw = keys.assign_keys(rows, STUDIES, DOCS, SRCS, edges)
    strip = lambda r: {k: v for k, v in r.items() if k not in ("rule_version", "keys_rule_version")}
    assert [strip(r) for r in a["records"]] == [strip(r) for r in raw["records"]]
    assert a["stats"] == raw["stats"]


def test_register_document_idempotent_single_record(tmp_path):
    out = tmp_path / "o"
    r1 = L.register_document(SRC, b"hello bytes", out)
    snap = {p.name: p.read_bytes() for p in out.iterdir()}
    r2 = L.register_document(SRC, io.BytesIO(b"hello bytes"), out)   # same bytes, different carrier
    assert r1 == r2 and r1["doc_id"].startswith("DOC-")
    assert {p.name: p.read_bytes() for p in out.iterdir()} == snap       # byte-identical, no second record
    assert len((out / "DOC_library.jsonl").read_text().splitlines()) == 1
    r3 = L.register_document(SRC, b"other bytes", out)
    assert r3["doc_id"] != r1["doc_id"]
    assert len((out / "DOC_library.jsonl").read_text().splitlines()) == 2


def test_register_document_from_path_and_independent_dirs_agree(tmp_path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"x" * 5000)
    r1 = L.register_document(SRC, f, tmp_path / "o1")
    r2 = L.register_document(SRC, b"x" * 5000, tmp_path / "o2")
    assert jbytes(r1) == jbytes(r2)
    assert r1["sha256"] == hashlib.sha256(b"x" * 5000).hexdigest() and r1["bytes"] == 5000
    assert r1["doc_key"] == f"{SRC}|sha256:{r1['sha256']}"


def test_doc_key_parity_with_08a_docs_module():
    from culinarystate.lineage import docs  # test may import it; the library must not (requests)
    assert L.doc_key("SRC-9", "ab" * 32) == docs.doc_mint_key("SRC-9", "ab" * 32)


def test_register_document_rejects_bad_input(tmp_path):
    with pytest.raises(ValueError):
        L.register_document("", b"x", tmp_path)
    with pytest.raises(TypeError):
        L.register_document(SRC, "a string", tmp_path)


# ------------------------------------------------------------------ check_disjointness
def test_check_disjointness_flags_violations_and_passes_clean():
    clean = L.assign_keys([row(1), row(2)], STUDIES, DOCS, SRCS, [])
    ok = L.check_disjointness(clean["records"], expected_rows=2, studies=STUDIES, docs=DOCS)
    assert ok["checks"]["G08-10"]["pass"] and ok["checks"]["G08-2"]["pass"]
    bad = L.check_disjointness(clean["records"], expected_rows=2, studies=STUDIES, docs=DOCS,
                               drv_parents={"EVD-000001": ["EVD-000002"]})
    assert not bad["checks"]["G08-2"]["pass"]


# ------------------------------------------------------------------ seeded fixture (unit test of code path ONLY)
def _record_to_item(rec, tag):
    return {"id": f"EVD-{tag}", "source_id": "S", "family": "F", "locator": None,
            "analyte": "rec", "matrix": rec["matrix"], "process": "p", "steps": ["p"],
            "values": [{"role": r["analyte"], "value": r["value"], "unit": r["unit"], "basis": r["basis"]}
                       for r in rec["rows"]],
            "doc_ref": None, "origin_type": "OTHER", "moisture_fraction": rec["moisture_fraction"]}


def test_seeded_fixture_seven_classes_at_frozen_cut():
    assert L.B3_CUT == 0.75 == detectors.B3_CUT
    pairs = seeding.generate_seeded_pairs(20261027, seeding.MIN_SEEDS_PER_CLASS)
    assert {p["seeded_class"] for p in pairs} == set(seeding.PERTURBATION_CLASSES)
    assert len(pairs) == 7 * seeding.MIN_SEEDS_PER_CLASS
    missed = []
    for n, p in enumerate(pairs):
        o, c = _record_to_item(p["original"], f"{n:06d}"), _record_to_item(p["copy"], f"{n:06d}9")
        got = L.propose_edges([o, c])["edges"]
        if len(got) != 1:
            missed.append((p["seeded_class"], n))
    assert missed == []          # code-path check on scratch fixtures; says nothing about real-data detection


# ------------------------------------------------------------------ G08b-4 offline
def test_library_imports_no_network_modules():
    tree = ast.parse((REPO / "src/culinarystate/lineage/library.py").read_text())
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            names.add((n.module or "").split(".")[0] if n.level == 0 else "." * n.level + (n.module or ""))
    assert not names & {"socket", "urllib", "http", "requests", "httpx", "ssl", "aiohttp", "ftplib", "smtplib"}


def test_fresh_interpreter_import_loads_no_network_module():
    import subprocess
    code = ("import sys; sys.path.insert(0, %r); import culinarystate.lineage.library as L; "
            "bad={'socket','http','requests','httpx','ssl','aiohttp','urllib.request','urllib.error'}; "
            "print(sorted(m for m in sys.modules if m in bad or m.split('.')[0] in bad))" % str(REPO / "src"))
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=True).stdout
    assert out.strip() == "[]", out


def test_use_opens_no_sockets(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise AssertionError("socket used")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    L.register_document(SRC, b"z", tmp_path / "o")
    e = L.propose_edges(items())["edges"]
    ks = L.assign_keys([row(1), row(2)], STUDIES, DOCS, SRCS, e)
    L.check_disjointness(ks["records"], expected_rows=2, studies=STUDIES, docs=DOCS)
    L.write_jsonl(e, tmp_path / "o" / "edges.jsonl", tmp_path / "o")


# ------------------------------------------------------------------ G08b-4 write guard
def test_writes_only_under_supplied_path(monkeypatch, tmp_path):
    out = tmp_path / "out"
    writes = []
    real_open = builtins.open
    real_popen = Path.open

    def spy(file, mode="r", *a, **k):
        if any(c in str(mode) for c in "wax+"):
            writes.append(Path(file).resolve())
        return real_open(file, mode, *a, **k)

    def spy_path(self, mode="r", *a, **k):
        if any(c in str(mode) for c in "wax+"):
            writes.append(self.resolve())
        return real_popen(self, mode, *a, **k)

    monkeypatch.setattr(builtins, "open", spy)
    monkeypatch.setattr(Path, "open", spy_path)
    L.register_document(SRC, b"data", out)
    e = L.propose_edges(items())["edges"]
    L.write_jsonl(e, out / "edges.jsonl", out)
    assert writes and all(out.resolve() in p.parents for p in writes), writes


@pytest.mark.parametrize("sub", ["ledgers/data", "exports/evd"])
def test_protected_paths_refused_and_nothing_created(tmp_path, sub):
    bad = tmp_path / sub / "scratch"
    with pytest.raises(ProtectedPathError):
        L.register_document(SRC, b"x", bad)
    with pytest.raises(ProtectedPathError):
        L.write_jsonl([{"a": 1}], bad / "e.jsonl", bad)
    assert not (tmp_path / sub.split("/")[0]).exists()


def test_write_target_must_be_inside_out_dir(tmp_path):
    with pytest.raises(ValueError):
        L.write_jsonl([{"a": 1}], tmp_path / "elsewhere.jsonl", tmp_path / "out")
    assert not (tmp_path / "elsewhere.jsonl").exists()


def test_write_jsonl_byte_identical_and_stamps_rule_version(tmp_path):
    e = L.propose_edges(items())["edges"]
    L.write_jsonl(e, tmp_path / "a.jsonl", tmp_path)
    L.write_jsonl(iter(e), tmp_path / "b.jsonl", tmp_path)
    assert (tmp_path / "a.jsonl").read_bytes() == (tmp_path / "b.jsonl").read_bytes()
    assert all(json.loads(l)["rule_version"] == L.RULE_VERSION for l in (tmp_path / "a.jsonl").read_text().splitlines())
