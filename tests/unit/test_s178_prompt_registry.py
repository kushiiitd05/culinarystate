"""S178 T8-C17-R1 / T8-C15-R3: prompt registry matches the code; the D5 claim record schema validates.

No model is called and no network is used. The Ollama digest lookup is tested against a local stub server.
"""
from __future__ import annotations

import csv
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import s178_prompt_registry as R  # noqa: E402


def _rows():
    with R.REGISTRY.open(newline="") as fh:
        return list(csv.DictReader(fh))


def test_header_and_unique_ids():
    rows = _rows()
    assert list(rows[0].keys()) == R.COLS
    ids = [r["prompt_id"] for r in rows]
    assert len(ids) == len(set(ids))


def test_committed_registry_matches_the_code():
    assert R.check() == []


def test_every_llm_row_carries_a_placeholder_digest_not_an_invented_one():
    for r in _rows():
        if r["llm_required"] == "yes":
            assert r["model_digest"] == R.PENDING
            assert r["digest_status"].startswith("NOT_PINNED")
    ref = [r for r in _rows() if r["kind"] == "MODEL_REFERENCE"]
    assert len(ref) == 1 and ref[0]["digest_status"] == "REFERENCE_ONLY"


def test_prompt_hashes_are_64_hex_where_present():
    for r in _rows():
        for col in ("template_sha256", "source_sha256"):
            if r[col]:
                assert len(r[col]) == 64 and set(r[col]) <= set("0123456789abcdef")


def test_changed_prompt_text_is_detected(monkeypatch):
    from culinarystate.generation import prompts as P
    monkeypatch.setattr(P, "b0_prompt", lambda q: "changed " + q)
    assert any(p.startswith("PR-B0") for p in R.check())


def test_run_note_has_registry_hash_and_pending_digest():
    note = R.run_note(None)
    assert "digest=PENDING_PIN_ON_RUN_HOST" in note
    assert R.registry_sha() in note
    assert "digest=abc123" in R.run_note("abc123")


class _Tags(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = json.dumps({"models": [{"name": "qwen2.5:7b-instruct", "digest": "f" * 64}]}).encode()
        self.send_response(200 if self.path == "/api/tags" else 404)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def test_ollama_digest_reads_tags_only():
    srv = HTTPServer(("127.0.0.1", 0), _Tags)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        url = f"http://127.0.0.1:{srv.server_port}"
        assert R.ollama_digest(url, "qwen2.5:7b-instruct") == "f" * 64
        assert R.ollama_digest(url, "not-there") is None
    finally:
        srv.shutdown()


# ---------------------------------------------------------------- D5CLM schema
jsonschema = pytest.importorskip("jsonschema")
SCHEMA = ROOT / "registry/schemas/D5CLM.draft_v1.schema.json"


def _good():
    return {"record_type": "D5CLM", "schema_version": "0.1.0-draft", "claim_id": "D5CLM-DRAFT-0123456789abcdef",
            "status": "DRAFT_PENDING_SIGNATURES", "is_evidence": False, "run_id": "RUN-S178-GOV-001",
            "qid": "D5-P1-001", "rung": "B7", "response_id": "D5-P1-001|B7|RUN-S178-GOV-001",
            "claim_text": "0.8", "claim_type": "NUMERIC", "value": 0.8, "semantics": "RETENTION",
            "binding": "FOLLOWING", "evidence_ids": ["EVD-000014"], "citation_required": True,
            "citation_refs": [{"evd_id": "EVD-000014", "exists_in_ledger": True, "in_packet": True}],
            "model_id": "qwen2.5:7b-instruct", "model_version": "PENDING_PIN_ON_RUN_HOST",
            "prompt_id": "PR-B5-ANSWER", "confidence_class": "QUANTITATIVE",
            "scorer": {"name": "h3_independent", "version": "h3_independent@0.1"}, "verdict": "SUPPORTED",
            "relevance": "EXACT", "supporting_ids": ["EVD-000014"], "verification_status": "UNVERIFIED_AI_SCORED"}


def test_schema_is_valid_and_accepts_a_good_record():
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(_good())


@pytest.mark.parametrize("field,bad", [("is_evidence", True), ("confidence_class", "0.93"), ("rung", "B3"),
                                       ("claim_type", "CAUSAL"), ("model_version", "latest"),
                                       ("evidence_ids", ["EVD-1"]), ("status", "SIGNED")])
def test_schema_rejects_bad_values(field, bad):
    schema = json.loads(SCHEMA.read_text())
    rec = {**_good(), field: bad}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(rec)


def test_schema_has_all_eleven_ssot_238_claim_ledger_fields():
    schema = json.loads(SCHEMA.read_text())
    ssot = ["claim_id", "response_id", "claim_text", "claim_type", "evidence_ids", "model_id", "model_version",
            "confidence_class", "citation_required", "citation_refs", "verification_status"]
    assert all(f in schema["properties"] for f in ssot)


def test_example_prompt_id_exists_in_the_registry():
    ids = {r["prompt_id"] for r in _rows()}
    assert _good()["prompt_id"] in ids


def test_scorer_enum_is_h3_independent_or_c17():
    schema = json.loads(SCHEMA.read_text())
    assert set(schema["properties"]["scorer"]["properties"]["name"]["enum"]) == {"h3_independent", "claims_c17"}
