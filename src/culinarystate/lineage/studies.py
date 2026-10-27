"""08a.2: STUDY appended versions (origin_type, report_doc_ids) and new STUDY/SRC nodes for the
Phenol-Explorer yield-source publications.

Append-only: STUDY.jsonl only grows. `design` stays UNKNOWN; `NOT_IDENTIFIABLE` is never written here.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from ..ledgers.common import ref, refs
from ..ledgers.registry import ORIGIN_TYPES, R
from ..ledgers.store import LedgerStore, _append_jsonl
from .docs import AGENT, CREATED_BY, DeterministicIdMinter
from .guard import assert_safe_write_target

STUDY_AGENT = "rule:step08a_studies@0.1"
SRC_SIDECAR = "SRC_08A_YIELD.jsonl"
UNSPECIFIED = "UNSPECIFIED"


class AppendOnlyViolation(RuntimeError):
    """The registered prefix of an append-only file changed."""


def study_schema() -> dict:
    """Registry STUDY schema plus the additive Appendix-A fields.

    # CONTRACT-AMBIGUITY: registry.py's STUDY schema (additionalProperties false) has no origin_type /
    # report_doc_ids yet and this work package may not edit registry.py, so records are validated here
    # against an extended copy and written directly (not through LedgerStore.append).
    """
    s = copy.deepcopy(R["STUDY"])
    s["properties"]["origin_type"] = {"type": "string", "enum": list(ORIGIN_TYPES)}
    s["properties"]["report_doc_ids"] = refs("DOC")
    s["properties"]["lab_group_note"] = {"anyOf": [{"type": "string"}, {"type": "null"}]}
    return s


def _validator() -> Draft202012Validator:
    return Draft202012Validator(study_schema(), format_checker=FormatChecker())


def _check(v: Draft202012Validator, rec: dict) -> None:
    errs = [e.message for e in v.iter_errors(rec)]
    if errs:
        raise ValueError(f"{rec.get('id')}: " + " | ".join(errs))


def check_prefix_unchanged(path: Path, nbytes: int, sha256_hex: str) -> None:
    data = Path(path).read_bytes() if Path(path).exists() else b""
    if len(data) < nbytes or hashlib.sha256(data[:nbytes]).hexdigest() != sha256_hex:
        raise AppendOnlyViolation(f"{path}: first {nbytes} bytes differ from the registered baseline")


def _ndjson(path: Path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def _latest_active_evd(evd_path: Path) -> dict[str, dict]:
    last: dict[str, dict] = {}
    for r in _ndjson(evd_path):
        last[r["id"]] = r
    return {k: v for k, v in last.items() if v.get("status") == "ACTIVE"}


def origin_types_from_evd(evd_path: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for r in _latest_active_evd(evd_path).values():
        for sid in r.get("study_ids") or []:
            out.setdefault(sid, set()).add(r["origin_type"])
    return out


def collect_yield_sources(evd_path: Path, pe_src_id: str) -> dict[str, dict]:
    """label as printed -> {rows, yield_foods[sorted distinct]} over latest ACTIVE PE rows; UNSPECIFIED skipped."""
    out: dict[str, dict] = {}
    for r in _latest_active_evd(evd_path).values():
        if r.get("source_id") != pe_src_id:
            continue
        mod = (r.get("process") or {}).get("modifiers") or {}
        label = mod.get("yield_source")
        if not label or label == UNSPECIFIED:
            continue
        e = out.setdefault(label, {"rows": 0, "_foods": set()})
        e["rows"] += 1
        if mod.get("yield_food"):
            e["_foods"].add(mod["yield_food"])
    return {k: {"rows": v["rows"], "yield_foods": sorted(v["_foods"])} for k, v in sorted(out.items())}


def _open(root: Path, created_at: str, files: tuple[str, ...]) -> LedgerStore:
    root = Path(root)
    for name in files:
        assert_safe_write_target(root / name)
    store = LedgerStore(root)
    store.ids = DeterministicIdMinter(root, created_at)
    return store


def append_report_versions(root: Path, doc_ids_by_src: dict[str, list[str]],
                           origin_types: dict[str, set[str]], *, created_at: str,
                           created_by: str = CREATED_BY) -> dict:
    """Append version n+1 to every latest ACTIVE STUDY lacking `report_doc_ids` (idempotent)."""
    root = Path(root)
    store = _open(root, created_at, ("STUDY.jsonl", "_ids.jsonl"))
    v, appended, with_docs = _validator(), 0, 0
    for prev in sorted(store.all_latest("STUDY"), key=lambda r: r["id"]):
        if prev["status"] != "ACTIVE" or "report_doc_ids" in prev:
            continue
        new = {**prev, "version": prev["version"] + 1, "created_at": created_at, "created_by": created_by,
               "report_doc_ids": sorted(doc_ids_by_src.get(prev["source_id"], [])),
               "provenance": {"method": "RULE", "source_ids": prev["provenance"]["source_ids"],
                              "agent": STUDY_AGENT, "locator": None,
                              "notes": "08a.2 additive version: origin_type from the study's ACTIVE EVD rows "
                                       "(omitted if not unique); report_doc_ids = 08a.1 DOCs of the paper SRC."}}
        ot = origin_types.get(prev["id"], set())
        if len(ot) == 1:
            new["origin_type"] = next(iter(ot))
        _check(v, new)
        _append_jsonl(root / "STUDY.jsonl", new)
        appended += 1
        with_docs += bool(new["report_doc_ids"])
    return {"versions_appended": appended, "versions_with_report_docs": with_docs}


def add_yield_source_nodes(root: Path, pe_src_id: str, yield_sources: dict[str, dict], *, created_at: str,
                           created_by: str = CREATED_BY) -> dict:
    """One new SRC (sidecar file) + one new STUDY per distinct stated yield-source label.

    # CONTRACT-AMBIGUITY: the card asks for new SRC nodes while G08-5/D-032 require SRC.jsonl to stay
    # byte-identical; new SRC rows therefore go to the sidecar `SRC_08A_YIELD.jsonl` (ids are minted in
    # `_ids.jsonl` as usual). Kush must decide whether they are later merged into SRC.jsonl.
    # CONTRACT-AMBIGUITY: kind=PAPER and origin_type (omitted = unknown) are not determinable from a label.
    """
    root = Path(root)
    store = _open(root, created_at, ("STUDY.jsonl", "_ids.jsonl", SRC_SIDECAR))
    v = _validator()
    src_validator = Draft202012Validator(R["SRC"], format_checker=FormatChecker())
    sidecar = root / SRC_SIDECAR
    have_src = {r["id"] for r in _ndjson(sidecar)} if sidecar.exists() else set()
    n_src = n_study = 0
    for label, info in sorted(yield_sources.items()):
        sid = store.ids.mint("SRC", f"pe_yield_src:{label}")
        if sid not in have_src:
            rec = {
                "id": sid, "record_type": "SRC", "schema_version": "1.0.0", "version": 1, "status": "ACTIVE",
                "created_at": created_at, "created_by": created_by,
                "provenance": {"method": "RULE", "source_ids": [pe_src_id], "agent": AGENT, "locator": None,
                               "notes": None},
                "verification": {"status": "UNVERIFIED"}, "kind": "PAPER", "title": label, "authors": [],
                "year": None, "licence": "UNKNOWN (cited as yield source by Phenol-Explorer; not held)",
                "licence_status": "UNKNOWN", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "UNKNOWN",
                "notes": (f"08a.2 node from EVD process.modifiers.yield_source label {label!r}: {info['rows']} "
                          f"ACTIVE EVD rows, {len(info['yield_foods'])} distinct yield_food strings. The "
                          "publication is not held and its identity beyond the printed label is UNKNOWN."),
            }
            errs = [e.message for e in src_validator.iter_errors(rec)]
            if errs:
                raise ValueError(f"{sid}: " + " | ".join(errs))
            _append_jsonl(sidecar, rec)
            have_src.add(sid)
            n_src += 1
        uid = store.ids.mint("STUDY", f"pe_yield_src:{label}")
        if store.latest(uid) is None:
            rec = {"id": uid, "record_type": "STUDY", "schema_version": "1.0.0", "version": 1,
                   "status": "ACTIVE", "created_at": created_at, "created_by": created_by,
                   "provenance": {"method": "RULE", "source_ids": [pe_src_id, sid], "agent": STUDY_AGENT,
                                  "locator": None, "notes": "08a.2 new node for a Phenol-Explorer yield-source label."},
                   "verification": {"status": "UNVERIFIED"}, "source_id": sid, "design": "UNKNOWN",
                   "report_doc_ids": []}
            _check(v, rec)
            _append_jsonl(root / "STUDY.jsonl", rec)
            n_study += 1
    return {"src_created": n_src, "study_created": n_study, "labels": len(yield_sources)}


def run_08a2(root: Path, pe_src_id: str, doc_ids_by_src: dict[str, list[str]], evd_path: Path, *,
             created_at: str, expect_prefix: tuple[int, str] | None = None) -> dict:
    """Both parts, with the append-only prefix of STUDY.jsonl checked before and after."""
    root = Path(root)
    study = root / "STUDY.jsonl"
    if expect_prefix:
        check_prefix_unchanged(study, *expect_prefix)
    out = append_report_versions(root, doc_ids_by_src, origin_types_from_evd(evd_path), created_at=created_at)
    ys = collect_yield_sources(evd_path, pe_src_id)
    out.update(add_yield_source_nodes(root, pe_src_id, ys, created_at=created_at))
    if expect_prefix:
        check_prefix_unchanged(study, *expect_prefix)
    out["yield_labels"] = {k: v["rows"] for k, v in ys.items()}
    return out
