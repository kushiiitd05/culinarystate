"""08a.7 EVD export v2 (= plan 05.1, additive). v1 columns are carried through unchanged; lineage columns are added.

Pure functions plus one writer. Never writes under ledgers/data or any `exports` directory (v1 stays untouched).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from culinarystate.evidence.evd_export import canon_json
from culinarystate.lineage.guard import ProtectedPathError, assert_safe_write_target

EXPORT_V2_VERSION = "evd_export@2.0.0"
# CONTRACT-AMBIGUITY: v1 already has `study_id_status` (ledger value, kept unchanged for byte-identity) and `study_ids`.
# The lineage key's status is therefore exported as `lineage_study_id_status`; the plan's `study_id_status` name collides.
# CONTRACT-AMBIGUITY: v1 `export_version` must stay "evd_export@1.0.0" (unchanged values), so the v2 bump is carried by
# the new column `export_schema_version` and by the manifest `export_version`.
# CONTRACT-AMBIGUITY: pointer columns of lineage_contract_v1_1 Appendix A (evidence_level, parent_ids, obs_ids, sexp_id,
# series_link, doc_id, ...) need OBS/AGG/DRV/DOC data not produced here; they are NOT exported (not invented, not null-filled).
ADDED_COLUMNS = ("study_id", "lineage_study_id_status", "independence_resolution", "lineage_root_id", "split_group_id",
                 "lineage_rule_version", "lineage_assignment_status", "export_schema_version")
_KEY_MAP = {"study_id": "study_id", "lineage_study_id_status": "study_id_status", "independence_resolution": "independence_resolution",
            "lineage_root_id": "lineage_root_id", "split_group_id": "split_group_id", "lineage_rule_version": "rule_version",
            "lineage_assignment_status": "assignment_status"}
_REQUIRED_NONNULL = ("lineage_study_id_status", "independence_resolution", "lineage_root_id", "split_group_id")  # study_id may be null (NOT_IDENTIFIABLE)


class ExportV2Error(RuntimeError):
    pass


def load_keys(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r["evd_id"] in out:
                raise ExportV2Error(f"duplicate key record for {r['evd_id']}")
            out[r["evd_id"]] = r
    return out


def build_v2_rows(v1_rows: Sequence[Mapping], keys: Mapping[str, Mapping]) -> list[dict]:
    """Return new rows = v1 row + added columns, same order. Fails on any missing/extra/null key record."""
    clash = set(ADDED_COLUMNS) & {c for r in v1_rows for c in r}
    if clash:
        raise ExportV2Error(f"added columns collide with v1 columns: {sorted(clash)}")
    ids = [r["evd_id"] for r in v1_rows]
    extra = sorted(set(keys) - set(ids))
    if extra:
        raise ExportV2Error(f"key records without v1 row: {extra[:3]}")
    out = []
    for r in v1_rows:
        k = keys.get(r["evd_id"])
        if k is None:
            raise ExportV2Error(f"no key record for {r['evd_id']}")
        add = {c: k.get(src) for c, src in _KEY_MAP.items()}
        bad = [c for c in _REQUIRED_NONNULL if add[c] is None]
        if bad:
            raise ExportV2Error(f"{r['evd_id']}: null {bad}")
        add["export_schema_version"] = EXPORT_V2_VERSION
        out.append({**r, **add})
    return out


def check_v1_identical(v2_rows: Sequence[Mapping], v1_lines: Sequence[str]) -> int:
    """v2 minus added columns, canonically serialised, must equal each v1 line; same count and order."""
    if len(v2_rows) != len(v1_lines):
        raise ExportV2Error(f"row count {len(v2_rows)} != v1 {len(v1_lines)}")
    drop = set(ADDED_COLUMNS)
    for i, (r, line) in enumerate(zip(v2_rows, v1_lines)):
        if canon_json({k: v for k, v in r.items() if k not in drop}) != line:
            raise ExportV2Error(f"v1 columns differ at row {i} ({r.get('evd_id')})")
    return len(v2_rows)


def _assert_out_dir(out_dir: Path) -> None:
    assert_safe_write_target(out_dir)
    if "exports" in Path(os.path.abspath(out_dir)).parts:
        raise ProtectedPathError(f"refusing to write inside an exports directory: {out_dir}")


def write_export_v2(rows: Iterable[Mapping], out_dir: Path, extra_meta: Mapping) -> dict:
    """Write evd_export_v2.jsonl (canonical JSON, one row per line) and a manifest with sha256s. Returns the manifest."""
    out_dir = Path(out_dir)
    _assert_out_dir(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    body = "".join(canon_json(r) + "\n" for r in rows).encode("utf-8")
    (out_dir / "evd_export_v2.jsonl").write_bytes(body)
    manifest = {**extra_meta, "export_version": EXPORT_V2_VERSION, "export_file": "evd_export_v2.jsonl", "export_rows": len(rows),
                "export_sha256": hashlib.sha256(body).hexdigest(), "added_columns": list(ADDED_COLUMNS),
                "v1_columns_policy": "all v1 columns unchanged in value; v1 export_version column kept at evd_export@1.0.0"}
    (out_dir / "evd_export_v2.manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    return manifest
