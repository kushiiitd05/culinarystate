"""Step 12.0 PROPOSED SRC/SNAP registration rows (S157, PROVISIONAL_PENDING_H2_REBASELINE).

Synthetic files, manifest rows, H2 queue and id ledgers below are self-authored fixtures. The tool
mints no id, appends to no ledger and writes PROPOSED rows to a staging file only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

from culinarystate.evidence import registration as R

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_COLS = ["source_id", "source_name", "provider", "official_url", "source_type", "licence", "licence_status",
                 "redistribution_allowed", "derived_data_allowed", "raw_text_storage_allowed",
                 "human_approval_required", "blocking_issue", "existing_repo_path", "ledger_src_family",
                 "licence_verification", "current_version"]


def manifest(tmp: Path) -> Path:
    rows = [
        ["DS-901", "SYNTHETIC yields table", "Synthetic Agency", "https://example.invalid/y", "database",
         "CC0 per catalog record (synthetic)", "CC0_REPORTED_BY_CATALOG", "yes (if CC0 confirmed)", "yes", "yes",
         "no", "none", "data/external/synth_yields", "none", "CATALOG_RECORD", "R2"],
        ["DS-902", "SYNTHETIC density table", "Synthetic Org", "https://example.invalid/d", "database",
         "UNKNOWN (no licence statement found)", "UNKNOWN_CAPABILITY_LICENCE", "UNKNOWN", "UNKNOWN", "UNKNOWN",
         "yes (licence confirmation)", "licence unknown", "data/external/synth_density", "none",
         "NOT_VERIFIED_THIS_RUN", "v2"],
        ["DS-903", "SYNTHETIC report", "Synthetic Institute", "https://example.invalid/r", "report tables",
         "values cited, text not redistributed", "ASSUMED", "values only (DERIVED_ONLY)", "yes",
         "no (text not redistributed)", "no (licence re-check recommended)", "none", "data/raw/synth_report",
         "SYNTH-FAMILY", "SRC_LEDGER_AT_INGESTION", "2002"],
        ["DS-904", "SYNTHETIC blocked table", "Synthetic Press", "https://example.invalid/b", "database",
         "Copyright; no reuse licence", "BLOCKED_LICENSE (no reuse licence)", "UNKNOWN", "UNKNOWN", "UNKNOWN",
         "no", "BLOCKED_LICENSE", "data/external/synth_blocked", "none", "THIRD_PARTY_REPORT", "1"],
    ]
    import csv
    p = tmp / "manifest.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(MANIFEST_COLS)
        w.writerows(rows)
    return p


def h2_queue(tmp: Path) -> Path:
    p = tmp / "h2.md"
    p.write_text("# SYNTHETIC H2 queue (nothing here has been executed)\n\n"
                 "| # | Source / action | Planned action | Why | Concern | Recommended |\n|---|---|---|---|---|---|\n"
                 "| 9 | Synthetic density (DS-902) | Ingest | x | No licence | ASK |\n"
                 "| 12 | Something else (DS-950, DS-951) | x | x | x | x |\n", encoding="utf-8")
    return p


def ids_file(tmp: Path, extra: list[dict] | None = None) -> Path:
    rows = [{"id": "SRC-000001", "key": "synthetic:existing", "prefix": "SRC", "minted_at": "2026-10-18T00:00:00+00:00"},
            {"id": "SRC-000007", "key": "synthetic:report", "prefix": "SRC", "minted_at": "2026-10-18T00:00:00+00:00"},
            {"id": "SNAP-000001", "key": "sha256:" + "0" * 64, "prefix": "SNAP", "minted_at": "2026-10-18T00:00:00+00:00"}]
    rows += extra or []
    p = tmp / "_ids.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return p


def src_ledger(tmp: Path) -> Path:
    rows = [{"id": "SRC-000007", "record_type": "SRC", "version": 1, "status": "ACTIVE",
             "source_family_id": "SYNTH-FAMILY", "title": "SYNTHETIC report"}]
    p = tmp / "SRC.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return p


def files(tmp: Path) -> dict[str, Path]:
    y = tmp / "data" / "external" / "synth_yields"
    d = tmp / "data" / "external" / "synth_density"
    r = tmp / "data" / "raw" / "synth_report"
    for x in (y, d, r):
        x.mkdir(parents=True)
    (y / "yields.csv").write_text("NDB,Yield Description\n99001,SYNTHETIC cut\n", encoding="utf-8")
    (y / "yields_DD.csv").write_text("column,meaning\nNDB,synthetic id\n", encoding="utf-8")
    (d / "density.xlsx").write_bytes(b"PK\x03\x04SYNTHETIC")
    (d / ".hidden").write_text("skip me", encoding="utf-8")
    pdf = r / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 SYNTHETIC")
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    (r / "report.pdf.snap.json").write_text(json.dumps(
        {"url": "https://example.invalid/r.pdf", "local_path": str(pdf), "sha256": sha, "bytes": pdf.stat().st_size,
         "retrieved_at": "2026-10-18T05:00:00+00:00", "http_status": 200}), encoding="utf-8")
    return {"yields_dir": y, "density_dir": d, "report_pdf": pdf}


def build(tmp: Path, entries: list[tuple[str, Path]], ids: Path | None = None) -> list[dict]:
    return R.build_proposals(entries, manifest=R.load_manifest(manifest(tmp)), h2_open=R.load_h2_open(h2_queue(tmp)),
                             id_index=R.IdIndex.from_file(ids or ids_file(tmp)),
                             existing_src=R.existing_src_by_family(src_ledger(tmp)), root=tmp)


def by(rows: list[dict], kind: str) -> list[dict]:
    return [r for r in rows if r["record"] == kind]


# ---------------------------------------------------------------- loaders
def test_status() -> None:
    assert R.STATUS == "PROVISIONAL_PENDING_H2_REBASELINE"


def test_h2_open_parser_reads_ds_ids(tmp_path: Path) -> None:
    open_ = R.load_h2_open(h2_queue(tmp_path))
    assert open_ == {"DS-902": ("9",), "DS-950": ("12",), "DS-951": ("12",)}


def test_real_h2_queue_and_manifest_flags() -> None:
    open_ = R.load_h2_open(ROOT / "reports" / "h_state" / "es_1_2_h2_approval_queue.md")
    assert "DS-014" in open_ and "9" in open_["DS-014"]          # INFOODS: H2 #9 open
    assert "DS-006" not in open_ and "DS-007" not in open_
    man = R.load_manifest(ROOT / "registry" / "data_source_acquisition_manifest.csv")
    assert {"DS-002", "DS-006", "DS-007", "DS-014"} <= set(man)


@pytest.mark.parametrize("raw,mapped", [("ASSUMED", "ASSUMED"), ("VERIFIED", "VERIFIED"),
                                        ("BLOCKED_LICENSE (no reuse licence)", "RESTRICTED"),
                                        ("NC_RESTRICTED", "RESTRICTED"), ("CC0_REPORTED_BY_CATALOG", "UNKNOWN"),
                                        ("PD_REPORTED_BY_CATALOG", "UNKNOWN"), ("UNKNOWN_CAPABILITY_LICENCE", "UNKNOWN"),
                                        ("", "UNKNOWN"), ("UNVERIFIED", "UNKNOWN")])
def test_licence_status_mapping_is_conservative(raw: str, mapped: str) -> None:
    assert R.map_licence_status(raw) == mapped


# ---------------------------------------------------------------- proposals
def test_proposals_for_directory_and_file_entries(tmp_path: Path) -> None:
    f = files(tmp_path)
    rows = build(tmp_path, [("DS-901", f["yields_dir"]), ("DS-902", f["density_dir"]), ("DS-903", f["report_pdf"])])
    srcs, snaps = by(rows, "PROPOSED_SRC"), by(rows, "PROPOSED_SNAP")
    assert [s["manifest_source_id"] for s in srcs] == ["DS-901", "DS-902"]   # DS-903 reuses existing SRC-000007
    assert [s["file"]["locator"] for s in snaps] == ["data/external/synth_yields/yields.csv",
                                                      "data/external/synth_yields/yields_DD.csv",
                                                      "data/external/synth_density/density.xlsx",
                                                      "data/raw/synth_report/report.pdf"]
    pdf = snaps[-1]
    assert pdf["proposed_record"]["source_id"] == "SRC-000007" and pdf["src_ref_status"] == "EXISTING_SRC"
    assert pdf["proposed_record"]["retrieved_at"] == "2026-10-18T05:00:00+00:00" and "SIDECAR_USED" in pdf["flags"]
    y = snaps[0]
    data = (tmp_path / "data/external/synth_yields/yields.csv").read_bytes()
    assert y["file"]["sha256"] == hashlib.sha256(data).hexdigest() and y["file"]["bytes"] == len(data)
    assert y["proposed_record"]["sha256"] == y["file"]["sha256"] and y["proposed_record"]["source_id"] == srcs[0]["proposal_id"]
    assert "retrieved_at" in y["gaps"] and "retrieved_at" not in y["proposed_record"]   # never invented


def test_placeholder_ids_are_not_real_ids(tmp_path: Path) -> None:
    f = files(tmp_path)
    rows = build(tmp_path, [("DS-901", f["yields_dir"]), ("DS-902", f["density_dir"])])
    real = re.compile(r"^(SRC|SNAP)-\d{6}$")
    for r in by(rows, "PROPOSED_SRC") + by(rows, "PROPOSED_SNAP"):
        assert re.fullmatch(r"PROPOSED-(SRC|SNAP)-\d{4}", r["proposal_id"])
        assert not real.match(r["proposal_id"]) and r["proposed_record"]["id"] == r["proposal_id"]
        assert r["id_check"] == {"placeholder_in_ids_ledger": False, "mint_key_in_ids_ledger": False}
        assert r["proposed_record"]["verification"] == {"status": "UNVERIFIED"}
        assert r["schema_errors"] == []


def test_existing_snapshot_hash_is_not_reproposed(tmp_path: Path) -> None:
    f = files(tmp_path)
    sha = hashlib.sha256((f["yields_dir"] / "yields.csv").read_bytes()).hexdigest()
    ids = ids_file(tmp_path, [{"id": "SNAP-000042", "key": f"sha256:{sha}", "prefix": "SNAP",
                               "minted_at": "2026-10-18T00:00:00+00:00"}])
    rows = build(tmp_path, [("DS-901", f["yields_dir"])], ids=ids)
    done = by(rows, "ALREADY_REGISTERED_SNAP")
    assert len(done) == 1 and done[0]["existing_snap_id"] == "SNAP-000042"
    assert [s["file"]["locator"] for s in by(rows, "PROPOSED_SNAP")] == ["data/external/synth_yields/yields_DD.csv"]


def test_existing_src_mint_key_is_flagged(tmp_path: Path) -> None:
    f = files(tmp_path)
    ids = ids_file(tmp_path, [{"id": "SRC-000050", "key": "manifest:DS-901", "prefix": "SRC",
                               "minted_at": "2026-10-18T00:00:00+00:00"}])
    rows = build(tmp_path, [("DS-901", f["yields_dir"])], ids=ids)
    src = by(rows, "PROPOSED_SRC")[0]
    assert src["id_check"]["mint_key_in_ids_ledger"] is True and "MINT_KEY_ALREADY_USED" in src["flags"]


def test_licence_and_storage_rules(tmp_path: Path) -> None:
    f = files(tmp_path)
    (tmp_path / "data/external/synth_blocked").mkdir(parents=True)
    (tmp_path / "data/external/synth_blocked/b.csv").write_text("x\n", encoding="utf-8")
    rows = build(tmp_path, [("DS-901", f["yields_dir"]), ("DS-902", f["density_dir"]),
                            ("DS-904", tmp_path / "data/external/synth_blocked")])
    src = {s["manifest_source_id"]: s for s in by(rows, "PROPOSED_SRC")}
    y, d, b = src["DS-901"], src["DS-902"], src["DS-904"]
    assert y["proposed_record"]["licence_status"] == "UNKNOWN" and y["proposed_record"]["storage_rule"] == "DERIVED_ONLY"
    assert y["licence_raw"]["licence_status"] == "CC0_REPORTED_BY_CATALOG"
    assert d["proposed_record"]["licence"].startswith("UNKNOWN") and d["proposed_record"]["storage_rule"] == "LOCAL_ONLY"
    assert {"H2_OPEN", "LOCAL_ONLY"} <= set(d["flags"]) and d["h2_items"] == ["9"]
    assert b["proposed_record"]["licence_status"] == "RESTRICTED" and b["proposed_record"]["storage_rule"] == "LOCAL_ONLY"
    assert all(s["proposed_record"]["storage_rule"] != "COMMIT_OK" for s in src.values())   # COMMIT_OK needs a human


def test_unknown_manifest_entry_and_missing_path(tmp_path: Path) -> None:
    f = files(tmp_path)
    with pytest.raises(R.RegistrationError):
        build(tmp_path, [("DS-999", f["yields_dir"])])
    rows = build(tmp_path, [("DS-901", tmp_path / "data/external/nowhere.csv")])
    miss = by(rows, "MISSING_LOCAL_FILE")
    assert len(miss) == 1 and "sha256" not in miss[0]


def test_outside_root_locator_flag(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    other = tmp_path / "elsewhere.csv"
    other.write_text("x\n", encoding="utf-8")
    rows = R.build_proposals([("DS-901", other)], manifest=R.load_manifest(manifest(tmp_path)),
                             h2_open={}, id_index=R.IdIndex.from_file(ids_file(tmp_path)), existing_src={}, root=root)
    snap = by(rows, "PROPOSED_SNAP")[0]
    assert "OUTSIDE_REPO_ROOT" in snap["flags"] and snap["file"]["locator"] == str(other.resolve())


def test_deterministic_and_writer_guards(tmp_path: Path) -> None:
    f = files(tmp_path)
    entries = [("DS-901", f["yields_dir"]), ("DS-903", f["report_pdf"])]
    a, b = build(tmp_path, entries), build(tmp_path, entries)
    assert a == b
    out = R.write_staging(a, tmp_path / "registry" / "staging" / "p.jsonl", root=tmp_path, inputs={"manifest": "x"})
    lines = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
    head = lines[0]
    assert head["record"] == "STAGING_HEADER" and head["status"] == R.STATUS
    assert head["ids_minted"] == 0 and head["ledger_rows_appended"] == 0
    assert head["counts"] == {"PROPOSED_SNAP": 3, "PROPOSED_SRC": 1}
    assert lines[1:] == a
    with pytest.raises(R.RegistrationError):
        R.write_staging(a, out, root=tmp_path, inputs={})
    for rel in ("ledgers/data/SRC.jsonl", "ledgers/data/x.jsonl", "exports/evd/x.jsonl", "out/SNAP.jsonl",
                "Ledgers/Data/x.jsonl"):
        with pytest.raises(R.RegistrationError):
            R.write_staging(a, tmp_path / rel, root=tmp_path, inputs={})


def test_real_ids_ledger_has_no_placeholder() -> None:
    idx = R.IdIndex.from_file(ROOT / "ledgers" / "data" / "_ids.jsonl")
    assert not any(i.startswith("PROPOSED-") for i in idx.ids)
    assert idx.lookup("SRC", "bognar:bfe-r-02-03") is not None


def test_tool_writes_staging_only_and_ledgers_unchanged(tmp_path: Path) -> None:
    from culinarystate.lineage.guard import verify_baseline
    f = files(tmp_path)
    spec = importlib.util.spec_from_file_location("reg_tool", ROOT / "tools" / "step12_0_register_local_files.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    out = tmp_path / "staging.jsonl"
    rc = mod.main(["--root", str(tmp_path), "--manifest", str(manifest(tmp_path)), "--h2-queue", str(h2_queue(tmp_path)),
                   "--ids", str(ids_file(tmp_path)), "--src-ledger", str(src_ledger(tmp_path)),
                   "--entry", f"DS-901={f['yields_dir']}", "--out", str(out)])
    assert rc == 0 and out.is_file()
    head = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert set(head["inputs"]) == {"manifest", "h2_queue", "ids", "src_ledger"}
    assert verify_baseline(ROOT / "registry" / "baseline_ledger_hashes_08a_v1.csv", ROOT) == 7
    assert mod.main(["--root", str(tmp_path), "--manifest", str(manifest(tmp_path)), "--h2-queue",
                     str(h2_queue(tmp_path)), "--ids", str(ids_file(tmp_path)), "--src-ledger",
                     str(src_ledger(tmp_path)), "--entry", f"DS-901={f['yields_dir']}", "--out", str(out)]) == 2


def test_tool_default_entries_cover_plan_sources() -> None:
    spec = importlib.util.spec_from_file_location("reg_tool2", ROOT / "tools" / "step12_0_register_local_files.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    ds = {d for d, _ in mod.DEFAULT_ENTRIES}
    assert {"DS-002", "DS-006", "DS-007", "DS-014"} <= ds
    assert mod.DEFAULT_OUT == "registry/staging/step12_0_src_snap_proposed_v1.jsonl"
