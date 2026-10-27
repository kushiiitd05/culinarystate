"""Step 08b-v0: reusable lineage / dedup library API (D-035). Thin wrappers over the unchanged 08a modules.

API: register_document, propose_edges, assign_keys, check_disjointness (+ write_jsonl, doc_key, rule_constants).
Detector logic, the B3 cut (0.75, D-034) and the key logic are NOT reimplemented: `detectors.detect_edges`,
`keys.assign_keys`, `keys.check_gates`, `keys.check_drv_gate` and `guard.assert_safe_write_target` are called as is.
This file makes no precision or recall claim; edges stay PROVISIONAL and keys stay SCRATCH_PROVISIONAL (D-034).

rule_version recipe (exact):
    constants = {
        "detectors.B3_CUT", "detectors.B1_SF", "detectors.B2_SF", "detectors._ROUND_SFS", "detectors.LEVEL_ORDER",
        "detectors.RULE_VERSION", "keys.RULE_VERSION", "keys.SAME_LAB_WINDOW_YEARS", "keys.MERGING_TYPES (sorted)",
        "keys.GROUPING_DEFAULT_TYPES (sorted)", "keys.HUB_SRC_KINDS (sorted)", "keys.HUB_REPORT_KINDS (sorted)",
        "library.LIBRARY_VERSION" }                      # = rule_constants()
    text = "\\n".join(f"{name}={value!r}" for name in sorted(constants))
    rule_version = "lib-v0-" + sha256(text.encode("utf-8")).hexdigest()      # full 64 hex digits
Changing any constant, or either 08a rule_version, changes the hash. The 08a versions are kept on each record as
`detector_rule_version` / `keys_rule_version`; `rule_version` itself is always the library hash. (Hash algorithm and
length were "NOT GIVEN IN PLAN"; this choice is flagged in reports/step08/step08b_v0_build_note.md.)

Properties:
  * Offline: imports only stdlib + 08a modules that import no network code. It deliberately does NOT import
    `lineage.docs` (imports `requests` via `evidence.doi_resolve`) nor `ledgers.store` (imports jsonschema, which loads
    urllib/socket); `doc_key` and the id minter are reproduced here; a test checks key parity with `docs.doc_mint_key`.
  * Deterministic and idempotent: sorted keys, fixed `minted_at`, no clocks, no randomness; input order is irrelevant.
  * Writes: only `register_document` (out_dir/DOC_library.jsonl, out_dir/_ids.jsonl) and `write_jsonl`, both under a
    caller-supplied directory that must pass `guard.assert_safe_write_target` (never ledgers/data or exports/evd).
    DOC ids minted here are SCRATCH library ids (sequence per out_dir), not ledger DOC ids.
  * Memory: register_document streams the bytes in 1 MiB chunks (peak independent of document size; measured in the
    build note). propose_edges/assign_keys materialise their inputs because the 08a code sorts and unions over all of
    them (O(items + edges + largest B3 block pairs)); the measured peak is in the build note, not a promised bound.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Mapping, Optional, Sequence, Union

from culinarystate.lineage import detectors, keys
from culinarystate.lineage.guard import assert_safe_write_target

LIBRARY_VERSION = "lib-v0"
B3_CUT = detectors.B3_CUT
FIXED_MINTED_AT = "2026-10-27T00:00:00+00:00"
DOC_FILE = "DOC_library.jsonl"
_CHUNK = 1 << 20


def rule_constants() -> dict[str, Any]:
    """The constants hashed into rule_version (see module docstring)."""
    return {
        "detectors.B3_CUT": detectors.B3_CUT, "detectors.B1_SF": detectors.B1_SF, "detectors.B2_SF": detectors.B2_SF,
        "detectors._ROUND_SFS": tuple(detectors._ROUND_SFS), "detectors.LEVEL_ORDER": tuple(detectors.LEVEL_ORDER),
        "detectors.RULE_VERSION": detectors.RULE_VERSION, "keys.RULE_VERSION": keys.RULE_VERSION,
        "keys.SAME_LAB_WINDOW_YEARS": keys.SAME_LAB_WINDOW_YEARS,
        "keys.MERGING_TYPES": tuple(sorted(keys.MERGING_TYPES)),
        "keys.GROUPING_DEFAULT_TYPES": tuple(sorted(keys.GROUPING_DEFAULT_TYPES)),
        "keys.HUB_SRC_KINDS": tuple(sorted(keys.HUB_SRC_KINDS)),
        "keys.HUB_REPORT_KINDS": tuple(sorted(keys.HUB_REPORT_KINDS)),
        "library.LIBRARY_VERSION": LIBRARY_VERSION,
    }


def hash_rule_constants(consts: Mapping[str, Any]) -> str:
    text = "\n".join(f"{k}={consts[k]!r}" for k in sorted(consts))
    return f"{LIBRARY_VERSION}-" + hashlib.sha256(text.encode("utf-8")).hexdigest()


RULE_VERSION = hash_rule_constants(rule_constants())


# ------------------------------------------------------------------ write helpers
def _check_out_dir(out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    assert_safe_write_target(out_dir)
    return out_dir


def _dump(obj: Mapping[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def write_jsonl(records: Iterable[Mapping[str, Any]], path: Path, out_dir: Path) -> int:
    """Stream records to `path` (must lie inside `out_dir`), sorted keys, atomic replace. Returns the line count.
    A record without rule_version gets the library one (on a copy)."""
    out_dir, path = _check_out_dir(out_dir), Path(path)
    assert_safe_write_target(path)
    root, target = Path(os.path.abspath(out_dir)), Path(os.path.abspath(path))
    if root not in target.parents:
        raise ValueError(f"{path} is not inside the supplied output directory {out_dir}")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    n = 0
    with tmp.open("w", encoding="utf-8", newline="\n") as fh:
        for rec in records:
            fh.write(_dump(rec if "rule_version" in rec else {**rec, "rule_version": RULE_VERSION}))
            n += 1
    os.replace(tmp, target)
    return n


# ------------------------------------------------------------------ register_document
def _mint_doc_id(out_dir: Path, key: str) -> str:
    """Mint/lookup `DOC-######` for `key` in out_dir/_ids.jsonl (same row shape as ledgers.store.IdMinter, fixed
    minted_at). Reproduced instead of imported: `ledgers.store` pulls in jsonschema, which loads urllib/socket."""
    path = out_dir / "_ids.jsonl"
    top = 0
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    row = json.loads(line)
                    if row["prefix"] == "DOC":
                        if row.get("key") == key:
                            return row["id"]
                        top = max(top, int(row["id"].rsplit("-", 1)[1]))
    new_id = f"DOC-{top + 1:06d}"
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(_dump({"id": new_id, "prefix": "DOC", "key": key, "minted_at": FIXED_MINTED_AT}))
    return new_id


def doc_key(src_id: str, sha256_hex: str) -> str:
    """D-029 D-11 mint key; identical to docs.doc_mint_key (tested)."""
    return f"{src_id}|sha256:{sha256_hex}"


def _hash_source(source: Union[bytes, bytearray, memoryview, os.PathLike, BinaryIO]) -> tuple[str, int]:
    h, n = hashlib.sha256(), 0
    if isinstance(source, (bytes, bytearray, memoryview)):
        mv = memoryview(source)
        for i in range(0, len(mv), _CHUNK):
            h.update(mv[i:i + _CHUNK])
        return h.hexdigest(), len(mv)
    if isinstance(source, os.PathLike):
        with Path(source).open("rb") as fh:
            return _hash_source(fh)
    if hasattr(source, "read"):
        for block in iter(lambda: source.read(_CHUNK), b""):
            h.update(block)
            n += len(block)
        return h.hexdigest(), n
    raise TypeError("source must be bytes, a Path, or a binary file-like object")


def _find_doc(path: Path, doc_id: str) -> Optional[dict]:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                if rec["doc_id"] == doc_id:
                    return rec
    return None


def register_document(src_id: str, source: Union[bytes, bytearray, memoryview, os.PathLike, BinaryIO],
                      out_dir: Path) -> dict[str, Any]:
    """Hash `source` (streamed) and register one DOC record under `out_dir`; same bytes -> same record, no second one."""
    if not isinstance(src_id, str) or not src_id.strip():
        raise ValueError("src_id must be a non-empty string")
    out_dir = _check_out_dir(out_dir)
    assert_safe_write_target(out_dir / DOC_FILE)
    sha, size = _hash_source(source)
    key = doc_key(src_id, sha)
    out_dir.mkdir(parents=True, exist_ok=True)
    doc_id = _mint_doc_id(out_dir, key)
    existing = _find_doc(out_dir / DOC_FILE, doc_id)
    if existing is not None:
        return existing
    rec = {"rule_version": RULE_VERSION, "doc_id": doc_id, "doc_key": key, "src_id": src_id, "sha256": sha,
           "bytes": size, "registration_status": "SCRATCH_LIBRARY"}
    with (out_dir / DOC_FILE).open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(_dump(rec))
    return rec


# ------------------------------------------------------------------ propose_edges / assign_keys / check_disjointness
def propose_edges(items: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """08a detectors B0-B3 + STRONG over detector items (see detectors.item_from_evd). Inputs are not mutated."""
    edges, stats = detectors.detect_edges(items)
    out = [{**e, "detector_rule_version": e["rule_version"], "rule_version": RULE_VERSION} for e in edges]
    return {"rule_version": RULE_VERSION, "edges": out, "stats": dict(stats)}


def assign_keys(rows: Sequence[Mapping], studies: Mapping, docs: Mapping, srcs: Mapping,
                edges: Iterable[Mapping], **kw: Any) -> dict[str, Any]:
    """08a keys.assign_keys (kw: levels, study_level_confirmed). Keys stay SCRATCH_PROVISIONAL."""
    res = keys.assign_keys(rows, studies, docs, srcs, edges, **kw)
    recs = [{**r, "keys_rule_version": r["rule_version"], "rule_version": RULE_VERSION} for r in res["records"]]
    return {"rule_version": RULE_VERSION, "records": recs, "stats": dict(res["stats"])}


def check_disjointness(records: Sequence[Mapping], *, expected_rows: int, studies: Mapping, docs: Mapping,
                       drv_parents: Optional[Mapping[str, Sequence[str]]] = None) -> dict[str, Any]:
    """Nesting / coverage / DRV-parent checks from keys.check_gates and keys.check_drv_gate, as data (no verdicts
    beyond each check's own boolean; a library check is not an 08a gate result)."""
    checks = dict(keys.check_gates(records, expected_rows, studies, docs))
    checks["G08-2"] = keys.check_drv_gate(records, drv_parents or {})
    return {"rule_version": RULE_VERSION, "checks": {k: {**v, "rule_version": RULE_VERSION} for k, v in sorted(checks.items())}}
