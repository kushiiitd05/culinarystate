"""ES-1.2 registry consistency (research-only step): ids unique, licence status explicit, capability matrix aligned, no acquisition artefacts."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
rd = lambda p: list(csv.DictReader(open(ROOT / p, newline="", encoding="utf-8")))
REQUIRED = ["source_id", "source_name", "source_family", "provider", "official_url", "documentation_url", "source_type", "evidence_plane", "access_method", "api_available", "bulk_download_available", "fulltext_available", "authentication_required",
            "api_key_required", "rate_limit_known", "licence", "licence_url", "redistribution_allowed", "derived_data_allowed", "raw_text_storage_allowed", "robots_terms_status", "current_version", "snapshot_version_date", "retrieval_date_if_existing",
            "checksum_if_existing", "expected_scale", "known_local_rows", "food_matrix_coverage", "process_coverage", "condition_coverage", "state_variable_coverage", "time_series_available", "before_after_available", "replicate_information",
            "measurement_method_available", "study_lineage_available", "candidate_evidence_tier", "candidate_design_strength", "target_ledgers", "target_state_families", "priority", "acquisition_wave", "local_copy_exists", "existing_repo_path",
            "existing_ingestion_status", "human_approval_required", "blocking_issue", "confidence", "notes"]


def test_manifest_columns_ids_and_explicit_licence_status():
    m = rd("registry/data_source_acquisition_manifest.csv")
    assert set(REQUIRED) <= set(m[0])
    ids = [r["source_id"] for r in m]
    assert len(ids) == len(set(ids))
    assert all(r["licence_status"] and r["licence_verification"] and r["priority"] in {"EXISTING", "P0", "P1", "P2", "PARK", "BLOCKED"} for r in m)
    assert all(r["acquisition_wave"] in {"A", "B", "C", "D", "E", "done", "none"} for r in m)


def test_unverified_or_conflicting_sources_are_never_p0_without_verification():
    for r in rd("registry/data_source_acquisition_manifest.csv"):
        if r["priority"] == "P0":
            assert r["licence_verification"] not in {"NOT_VERIFIED_THIS_RUN", "CHECK_FAILED_THIS_RUN"} or "CC0" in r["licence_status"] or "PER_ARTICLE" in r["licence_status"]
        if "BLOCKED" in r["licence_status"] or "BLOCKED" in r["blocking_issue"]:
            assert r["priority"] in {"BLOCKED", "PARK", "EXISTING", "P1", "P2"}


def test_capability_matrix_aligned_with_manifest_and_values_valid():
    m, c = rd("registry/data_source_acquisition_manifest.csv"), rd("registry/source_claim_capability_matrix.csv")
    assert [r["source_id"] for r in m] == [r["source_id"] for r in c]
    caps = [k for k in c[0] if k not in ("source_id", "source_name", "priority", "capability_basis", "note")]
    assert len(caps) == 20
    assert all(r[k] in {"YES", "PARTIAL", "NO", "UNKNOWN"} for r in c for k in caps)
    # recipe corpora must not claim measured transitions
    for r in c:
        if r["source_id"] in {"DS-051", "DS-052", "DS-053", "DS-054", "DS-057", "DS-058"}:
            assert r["before/after transition"] == "NO" and r["kinetic fitting"] == "NO"


def test_query_matrix_and_priority_cells():
    q = rd("registry/evidence_query_matrix_v1.csv")
    assert len(q) == 30 and all(r["europepmc_query_with_mechanism"] for r in q)
    assert not any("ERROR" in r["hits_all"] for r in q)
    pc = rd("reports/h_state/es_1_2_priority_cell_source_coverage.csv")
    cells = " ".join(r["priority_cell"] for r in pc)
    for k in ("garlic", "onion", "potato", "broccoli", "cabbage", "rice", "wheat dough", "beef"):
        assert k in cells
    qids = {r["query_id"] for r in q}
    assert all(x in qids for r in pc for x in r["literature_query_ids"].split(";"))


def test_no_acquired_data_files_added_in_es12():
    forbidden = [p for p in (ROOT / "data").rglob("*") if p.is_file() and "es12" in p.name.lower()]
    assert not forbidden
