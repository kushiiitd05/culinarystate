"""Step 13a-0 offline seed corpus (S157). Status: PROVISIONAL_PENDING_13A.

Every DOI, title and work below is SYNTHETIC (self-authored fixture strings, ``10.9999/...`` style
prefixes); none names a real paper. The tests prove that the seed corpus is built offline from local
artifacts only, deduplicates on the exact normalised DOI and nothing else, keeps per-record
provenance, keeps abstracts and other free text out of its outputs, and never states a licence the
inputs do not state.
"""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.evidence import seed_corpus as S

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "SENTINELABSTRACTWORD"

QUEUE_COLS = ["queue_rank", "route", "class", "score", "doi", "title", "year", "evd_rows", "process", "target",
              "matrix", "evd_ids", "reasons", "open_access", "url", "human_status", "verifier", "verified_at",
              "notes", "ai_suggested_decision", "ai_notes"]
REJ_COLS = [c for c in QUEUE_COLS if c not in ("queue_rank", "ai_suggested_decision", "ai_notes")]
PRE_COLS = ["src_id", "citation", "doi", "is_oa", "oa_url", "rows", "ai_paper_suggestion"]
PACK_COLS = ["pack", "evd_id", "paper_doi", "paper_link", "citation", "food", "human_decision", "verifier"]


def write_csv(path: Path, cols: list[str], rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    return path


def write_jsonl(path: Path, recs: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
    return path


def synthetic_root(tmp_path: Path, *, openalex: bool = True) -> Path:
    root = tmp_path / "repo"
    ev = root / "registry" / "evidence"
    write_csv(ev / "verification_queue_ranked_v1.csv", QUEUE_COLS, [
        {"queue_rank": "1", "route": "A_phenol_explorer", "class": "VERIFY_NOW", "doi": "10.9999/SYNTH.A1",
         "title": "Author A. (2001) Synthetic paper one. Synthetic Journal 1:1-2", "year": "2001",
         "open_access": "False", "reasons": "free text reason", "ai_notes": "free text ai note"},
        {"queue_rank": "2", "route": "A_phenol_explorer", "class": "STRONG_CANDIDATE", "doi": "",
         "title": "Author B. (2002) Synthetic paper without doi. Synthetic Journal 2:3-4", "year": "2002"},
        {"queue_rank": "3", "route": "B_openalex_gap", "class": "NEEDS_SOURCE", "doi": "10.9999/synth.b1",
         "title": "Synthetic gap paper one", "year": "2020", "process": "boil", "target": "vitamin c",
         "matrix": "vegetables", "open_access": "True", "url": "https://example.org/synthetic-b1.pdf"},
        {"queue_rank": "4", "route": "B_openalex_gap", "class": "NEEDS_SOURCE", "doi": "10.9999/synth.b2",
         "title": "Synthetic shared title", "year": "2021", "open_access": "False",
         "url": "https://doi.org/10.9999/synth.b2"},
        {"queue_rank": "5", "route": "B_openalex_gap", "class": "NEEDS_SOURCE", "doi": "not-a-doi",
         "title": "Synthetic broken doi", "year": "2022"},
    ])
    write_csv(ev / "rejected_candidates.csv", REJ_COLS, [
        {"route": "B_openalex_gap", "class": "REJECT", "doi": "10.9999/synth.r1", "title": "Synthetic shared title",
         "year": "2019", "open_access": "True"},
    ])
    write_csv(ev / "route_a_paper_precheck.csv", PRE_COLS, [
        {"src_id": "SRC-900001", "citation": "Author A. (2001) Synthetic paper one. Synthetic Journal 1:1-2",
         "doi": "https://doi.org/10.9999/synth.a1", "is_oa": "True", "oa_url": "https://example.org/a1.pdf",
         "ai_paper_suggestion": "free text"},
        {"src_id": "SRC-900002", "citation": "Author B. (2002) Synthetic paper without doi. Synthetic Journal 2:3-4",
         "doi": ""},
    ])
    write_csv(ev / "human_review_pack_v1.csv", PACK_COLS, [
        {"pack": "MAIN", "evd_id": "EVD-900001", "paper_doi": "doi:10.9999/Synth.A1",
         "citation": "Author A. (2001) Synthetic paper one. Synthetic Journal 1:1-2", "food": "synthetic food"},
    ])
    write_csv(root / "registry" / "evidence_query_matrix_v1.csv", ["query_id", "europepmc_query_titleabs",
                                                                   "hits_all"],
              [{"query_id": "Q01", "europepmc_query_titleabs": "TITLE_ABS:(synthetic)", "hits_all": "5"}])
    src = root / "ledgers" / "data" / "SRC.jsonl"
    write_jsonl(src, [
        {"id": "SRC-900001", "version": 1, "status": "ACTIVE", "kind": "PAPER", "source_family_id": "pe_pub:aaaa",
         "title": "Author A. (2001) Synthetic paper one. Synthetic Journal 1:1-2", "year": 2001,
         "licence_status": "UNKNOWN", "licence": "Publisher copyright (synthetic)"},
        {"id": "SRC-900001", "version": 2, "status": "ACTIVE", "kind": "PAPER", "source_family_id": "pe_pub:aaaa",
         "title": "Author A. (2001) Synthetic paper one. Synthetic Journal 1:1-2", "year": 2001,
         "doi": "10.9999/synth.a1", "licence_status": "UNKNOWN", "licence": "Publisher copyright (synthetic)"},
        {"id": "SRC-900002", "version": 1, "status": "ACTIVE", "kind": "PAPER", "source_family_id": "pe_pub:bbbb",
         "title": "Author B. (2002) Synthetic paper without doi. Synthetic Journal 2:3-4", "year": 2002,
         "licence_status": "UNKNOWN"},
        {"id": "SRC-900003", "version": 1, "status": "ACTIVE", "kind": "DATABASE", "source_family_id": "SYNTH-DB",
         "title": "Synthetic database", "doi": "10.9999/synth.db"},
    ])
    write_jsonl(root / "ledgers" / "data" / "DOC.jsonl", [
        {"id": "DOC-900001", "version": 1, "status": "ACTIVE", "doc_kind": "METADATA_RECORD", "src_id": "SRC-900001",
         "identifiers": {"doi": "10.9999/synth.a1"}},
        {"id": "DOC-900002", "version": 1, "status": "ACTIVE", "doc_kind": "WEB_PAGE_SNAPSHOT", "identifiers": {}},
    ])
    if openalex:
        oa = root / "data" / "raw" / "openalex"
        oa.mkdir(parents=True)
        (oa / "synthetic_query_one.json").write_text(json.dumps([
            {"id": "https://openalex.org/W9000000001", "doi": "https://doi.org/10.9999/SYNTH.B1",
             "title": "Synthetic gap paper one", "publication_year": 2020, "type": "article",
             "primary_location": {"source": {"display_name": "Synthetic Venue"}, "license": "cc-by"},
             "open_access": {"is_oa": True, "oa_url": "https://example.org/synthetic-b1.pdf", "oa_status": "gold"},
             "cited_by_count": 3, "abstract_inverted_index": {SENTINEL: [0], "boiled": [1]},
             "authorships": [{"author": {"display_name": "Synthetic Author"}}]},
            {"id": "https://openalex.org/W9000000002", "doi": None, "title": "Synthetic work without doi",
             "publication_year": 2018, "abstract_inverted_index": None},
            {"id": "https://openalex.org/W9000000003", "doi": "https://doi.org/10.9999/synth.new",
             "title": "Synthetic new paper", "publication_year": 2023, "open_access": {"is_oa": False},
             "primary_location": None},
        ]), encoding="utf-8")
        (oa / "broken_page.json").write_text("{not json", encoding="utf-8")
    return root


def build(root: Path, **kw) -> S.SeedCorpus:
    return S.build_seed_corpus(S.default_inputs(root, **kw), root=root)


def seed(corpus: S.SeedCorpus, key: str) -> dict:
    return next(s for s in corpus.seeds if s["seed_key"] == key)


# ---------------------------------------------------------------- DOI normalisation
@pytest.mark.parametrize("raw,norm,transforms", [
    ("10.9999/ABC.Def", "10.9999/abc.def", ("CASE_FOLD_ASCII",)),
    ("https://doi.org/10.9999/x", "10.9999/x", ("STRIP_RESOLVER_URL",)),
    ("HTTP://DX.DOI.ORG/10.9999/X", "10.9999/x", ("STRIP_RESOLVER_URL", "CASE_FOLD_ASCII")),
    ("doi.org/10.9999/x", "10.9999/x", ("STRIP_RESOLVER_URL",)),
    ("doi:10.9999/x", "10.9999/x", ("STRIP_DOI_SCHEME",)),
    ("DOI: 10.9999/x", "10.9999/x", ("STRIP_DOI_SCHEME",)),
    ("info:doi/10.9999/x", "10.9999/x", ("STRIP_DOI_SCHEME",)),
    ("  10.9999/x\t", "10.9999/x", ("STRIP_WHITESPACE",)),
    ("https://doi.org/10.9999/a%2Fb%28c%29", "10.9999/a/b(c)", ("STRIP_RESOLVER_URL", "PERCENT_DECODE_URL_FORM")),
    ("10.9999/a%2Fb", "10.9999/a%2fb", ("CASE_FOLD_ASCII",)),      # bare form: '%' is a DOI character
    ("10.9999/x.", "10.9999/x.", ()),                               # trailing punctuation is never trimmed
    ("10.9999/ÉtudeX", "10.9999/Étudex", ("CASE_FOLD_ASCII",)),     # ASCII only; no Unicode case mapping
    ("10.9999.12/x", "10.9999.12/x", ()),
])
def test_normalise_doi_valid(raw: str, norm: str, transforms: tuple[str, ...]) -> None:
    r = S.normalise_doi(raw)
    assert r.status == "VALID" and r.doi == norm and r.transforms == transforms and r.raw == raw


@pytest.mark.parametrize("raw,status", [("", "ABSENT"), ("   ", "ABSENT"), (None, "ABSENT"),
                                        ("not-a-doi", "INVALID_SYNTAX"), ("10.9999/a b", "INVALID_SYNTAX"),
                                        ("11.9999/x", "INVALID_SYNTAX"), ("10.abc/x", "INVALID_SYNTAX"),
                                        ("10.9999/", "INVALID_SYNTAX"), ("https://doi.org/", "INVALID_SYNTAX"),
                                        ("https://doi.org/10.9999/%ZZ%FF", "INVALID_SYNTAX")])
def test_normalise_doi_absent_or_invalid_is_never_guessed(raw: str | None, status: str) -> None:
    r = S.normalise_doi(raw)
    assert r.status == status and r.doi is None


def test_transform_vocabulary_is_documented() -> None:
    assert S.STATUS == "PROVISIONAL_PENDING_13A"
    assert set(S.DOI_TRANSFORMS) == {"STRIP_WHITESPACE", "STRIP_RESOLVER_URL", "STRIP_DOI_SCHEME",
                                     "PERCENT_DECODE_URL_FORM", "CASE_FOLD_ASCII"}
    assert S.DEDUP_RULE == "EXACT_NORMALISED_DOI_ONLY"


# ---------------------------------------------------------------- reading and dedup
def test_exact_doi_dedup_keeps_provenance(tmp_path: Path) -> None:
    c = build(synthetic_root(tmp_path))
    a1 = seed(c, "doi:10.9999/synth.a1")
    assert sorted(s["artifact"] for s in a1["sources"]) == [
        "doc_ledger_doi", "human_review_pack_v1", "queue_v1", "route_a_precheck_v1", "src_ledger_pe_pub"]
    assert {"artifact": "queue_v1", "ref": "queue_rank=1"} in [{k: s[k] for k in ("artifact", "ref")}
                                                               for s in a1["sources"]]
    assert a1["doi_raw_forms"] == sorted({"10.9999/SYNTH.A1", "https://doi.org/10.9999/synth.a1",
                                          "doi:10.9999/Synth.A1", "10.9999/synth.a1"})
    assert a1["src_ids"] == ["SRC-900001"] and a1["doc_ids"] == ["DOC-900001"]
    assert a1["n_source_records"] == 5
    b1 = seed(c, "doi:10.9999/synth.b1")
    assert sorted(s["artifact"] for s in b1["sources"]) == ["openalex_pages", "queue_v1"]
    assert b1["openalex_ids"] == ["W9000000001"] and b1["venue"] == "Synthetic Venue"
    assert b1["query_cells"] == ["boil|vitamin c|vegetables"]


def test_same_title_different_doi_is_not_merged_but_counted(tmp_path: Path) -> None:
    c = build(synthetic_root(tmp_path))
    keys = {s["seed_key"] for s in c.seeds}
    assert {"doi:10.9999/synth.b2", "doi:10.9999/synth.r1"} <= keys
    assert c.counts["fuzzy_report_only"]["doi_seed_groups_sharing_normalised_title"] == 1


def test_records_without_valid_doi_are_never_merged(tmp_path: Path) -> None:
    c = build(synthetic_root(tmp_path))
    nodoi = [s for s in c.seeds if s["doi"] is None]
    assert all(s["n_source_records"] == 1 for s in nodoi)
    assert {s["doi_status"] for s in nodoi} == {"ABSENT", "INVALID_SYNTAX"}
    assert "nodoi:queue_v1:queue_rank=2" in {s["seed_key"] for s in nodoi}
    assert "invalid:queue_v1:queue_rank=5" in {s["seed_key"] for s in nodoi}
    # Author B appears in 3 artifacts without a DOI: exact-DOI-only dedup keeps 3 seeds; the title link is counted
    assert c.counts["fuzzy_report_only"]["no_doi_seeds_sharing_normalised_title_with_another_seed"] >= 2


def test_src_ledger_latest_paper_versions_only(tmp_path: Path) -> None:
    c = build(synthetic_root(tmp_path))
    assert "doi:10.9999/synth.db" not in {s["seed_key"] for s in c.seeds}       # not a pe_pub PAPER
    src = [r for r in c.records if r["artifact"] == "src_ledger_pe_pub"]
    assert sorted(r["ref"] for r in src) == ["src_id=SRC-900001", "src_id=SRC-900002"]


def test_query_matrix_contributes_no_records(tmp_path: Path) -> None:
    c = build(synthetic_root(tmp_path))
    qm = c.counts["inputs"]["query_matrix_v1"]
    assert qm["records_read"] == 0 and qm["present"] is True
    assert qm["reason"] == "NO_RECORD_LEVEL_IDENTIFIERS"


def test_openalex_pages_optional_and_unreadable_page_counted(tmp_path: Path) -> None:
    root = synthetic_root(tmp_path)
    c = build(root)
    oa = c.counts["inputs"]["openalex_pages"]
    assert oa["files_read"] == 1 and oa["files_unreadable"] == 1 and oa["records_read"] == 3
    assert oa["works_with_abstract_dropped"] == 1
    assert "doi:10.9999/synth.new" in {s["seed_key"] for s in c.seeds}
    off = build(synthetic_root(tmp_path / "x", openalex=False))
    assert off.counts["inputs"]["openalex_pages"]["present"] is False
    assert "doi:10.9999/synth.new" not in {s["seed_key"] for s in off.seeds}


# ---------------------------------------------------------------- licence / access
def test_licence_unknown_unless_stated(tmp_path: Path) -> None:
    c = build(synthetic_root(tmp_path))
    a1 = seed(c, "doi:10.9999/synth.a1")
    assert a1["licence_status"] == "UNKNOWN" and a1["licence_stated"] == [] and a1["tdm_status"] == "UNKNOWN"
    b1 = seed(c, "doi:10.9999/synth.b1")
    assert b1["licence_status"] == "STATED_BY_INPUT_UNVERIFIED"
    assert b1["licence_stated"] == [{"artifact": "openalex_pages", "value": "cc-by"}]
    assert {s["licence_status"] for s in c.seeds} <= {"UNKNOWN", "STATED_BY_INPUT_UNVERIFIED",
                                                      "CONFLICTING_STATEMENTS_UNVERIFIED"}
    assert "VERIFIED" not in {s["licence_status"] for s in c.seeds}


def test_oa_flag_conflict_is_reported_not_resolved(tmp_path: Path) -> None:
    c = build(synthetic_root(tmp_path))
    a1 = seed(c, "doi:10.9999/synth.a1")              # queue says False, precheck says True
    assert a1["oa_flag"] == "CONFLICT"
    assert a1["oa_flag_statements"] == [{"artifact": "queue_v1", "value": "FALSE"},
                                        {"artifact": "route_a_precheck_v1", "value": "TRUE"}]
    assert seed(c, "doi:10.9999/synth.b1")["oa_flag"] == "TRUE"
    assert seed(c, "nodoi:queue_v1:queue_rank=2")["oa_flag"] == "UNKNOWN"


# ---------------------------------------------------------------- no free text / abstracts
def test_outputs_carry_no_abstract_or_free_text(tmp_path: Path) -> None:
    root = synthetic_root(tmp_path)
    c = build(root)
    out = S.write_seed_corpus(c, root / "registry" / "evidence" / "seed.jsonl", root=root)
    text = out.read_text(encoding="utf-8")
    for banned in (SENTINEL, "free text reason", "free text ai note", "Synthetic Author", "synthetic food",
                   "abstract_inverted_index", "authorships"):
        assert banned not in text
    head = json.loads(text.splitlines()[0])
    assert head["record"] == "SEED_CORPUS_HEADER" and head["status"] == "PROVISIONAL_PENDING_13A"
    assert head["abstracts_included"] is False and head["dedup_rule"] == "EXACT_NORMALISED_DOI_ONLY"
    seeds = [json.loads(x) for x in text.splitlines()[1:]]
    assert all(set(s) <= set(S.SEED_FIELDS) for s in seeds)
    assert [s["seed_key"] for s in seeds] == sorted(s["seed_key"] for s in seeds)


def test_build_is_deterministic(tmp_path: Path) -> None:
    root = synthetic_root(tmp_path)
    a = S.write_seed_corpus(build(root), root / "a.jsonl", root=root).read_bytes()
    b = S.write_seed_corpus(build(root), root / "b.jsonl", root=root).read_bytes()
    assert a == b


@pytest.mark.parametrize("rel", ["ledgers/data/x.jsonl", "ledgers/other.jsonl", "exports/evd/x.jsonl",
                                 "annotation/gold/x.jsonl", "data/interim/x.jsonl", "registry/evidence/EVD.jsonl"])
def test_writer_refuses_protected_targets(tmp_path: Path, rel: str) -> None:
    root = synthetic_root(tmp_path)
    with pytest.raises(S.SeedCorpusError):
        S.write_seed_corpus(build(root), root / rel, root=root)


def test_writer_refuses_overwrite(tmp_path: Path) -> None:
    root = synthetic_root(tmp_path)
    p = S.write_seed_corpus(build(root), root / "seed.jsonl", root=root)
    with pytest.raises(S.SeedCorpusError):
        S.write_seed_corpus(build(root), p, root=root)


def test_counts_report_is_counts_only(tmp_path: Path) -> None:
    root = synthetic_root(tmp_path)
    c = build(root)
    S.assert_counts_only(c.counts)
    with pytest.raises(S.SeedCorpusError):
        S.assert_counts_only({"seeds": {"title": "Synthetic paper one"}})
    s = c.counts["seeds"]
    assert s["total"] == len(c.seeds)
    assert s["with_valid_doi"] + s["without_valid_doi"] == s["total"]
    assert c.counts["abstracts_included"] is False and c.counts["ledger_rows_appended"] == 0
    assert c.counts["doi_transform_counts"]["CASE_FOLD_ASCII"] >= 2
    md = S.render_report_md(c.counts)
    assert md.startswith("# ") and "PROVISIONAL_PENDING_13A" in md.splitlines()[2]
    assert "Synthetic" not in md


def test_missing_required_input_is_refused(tmp_path: Path) -> None:
    root = synthetic_root(tmp_path)
    (root / "registry" / "evidence" / "verification_queue_ranked_v1.csv").unlink()
    with pytest.raises(S.SeedCorpusError):
        build(root)


# ---------------------------------------------------------------- tool
def load_tool():
    spec = importlib.util.spec_from_file_location("seed_tool", ROOT / "tools" / "step13a0_seed_corpus.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_tool_end_to_end_on_synthetic_root(tmp_path: Path) -> None:
    T = load_tool()
    root = synthetic_root(tmp_path)
    assert T.main(["--root", str(root)]) == 0
    full = root / T.DEFAULT_OUT["full"]
    assert full.is_file() and (root / T.DEFAULT_REPORT_JSON["full"]).is_file()
    assert (root / T.DEFAULT_REPORT_MD["full"]).is_file()
    assert T.main(["--root", str(root)]) == 2                         # refuses overwrite
    assert T.main(["--root", str(root), "--no-openalex"]) == 0
    assert (root / T.DEFAULT_OUT["tracked"]).is_file()


def test_real_tracked_artifacts_build_read_only() -> None:
    before = {p: p.stat().st_mtime_ns for p in (ROOT / "ledgers" / "data").glob("*.jsonl")}
    c = S.build_seed_corpus(S.default_inputs(ROOT, openalex=False), root=ROOT)
    keys = [s["seed_key"] for s in c.seeds]
    assert len(keys) == len(set(keys)) and c.counts["seeds"]["with_valid_doi"] > 0
    dois = [s["doi"] for s in c.seeds if s["doi"]]
    assert len(dois) == len(set(dois))
    assert {p: p.stat().st_mtime_ns for p in (ROOT / "ledgers" / "data").glob("*.jsonl")} == before
