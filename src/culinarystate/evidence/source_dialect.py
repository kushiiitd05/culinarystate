"""Step 07H layer D3: SOURCE DIALECT adapter. Source-specific labels/abbreviations live ONLY in registry/source_dialect_mapping_registry_v1.csv
(mapping_id, source_family, field, raw_pattern, canonical_target, status VERIFIED|CANDIDATE|UNVERIFIED|DEPRECATED, evidence, verified_by, version).
The semantic normalizer never imports source names; unresolved abbreviations stay UNVERIFIED and are annotated, never expanded."""
from __future__ import annotations

import csv
import re
from pathlib import Path

REG = Path(__file__).resolve().parents[3] / "registry"
STATUSES = ("VERIFIED", "CANDIDATE", "UNVERIFIED", "DEPRECATED")


def _load() -> list[dict]:
    with open(REG / "source_dialect_mapping_registry_v1.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        assert r["status"] in STATUSES, r
    return rows


MAPPINGS = _load()


def lookup(field: str, raw: str | None, source_family: str | None = None) -> dict | None:
    """exact (case-sensitive) raw_pattern match; a source-specific row beats a '*' row; '*' as raw_pattern matches any raw for that source. DEPRECATED rows are skipped."""
    best = None
    for r in MAPPINGS:
        if r["field"] != field or r["status"] == "DEPRECATED" or r["source_family"] not in ("*", source_family):
            continue
        if r["raw_pattern"] not in (raw, "*"):
            continue
        spec = (r["source_family"] != "*") + (r["raw_pattern"] != "*")
        if best is None or spec > best[0]:
            best = (spec, r)
    return best[1] if best else None


def annotate_abbreviations(raw: str | None, source_family: str | None) -> list[dict]:
    """tokens in a raw string that the registry knows as source abbreviations -> [{token, status, mapping_id}] (annotation only; never changes a value)."""
    out = []
    for r in MAPPINGS:
        if r["field"] == "source_abbreviation" and r["source_family"] in ("*", source_family) and raw and r["status"] != "DEPRECATED":
            pat = re.escape(r["raw_pattern"])
            if re.search(rf"(?<![A-Za-z]){pat}(?![A-Za-z])" if r["raw_pattern"].isalpha() else pat, str(raw)):
                out.append({"token": r["raw_pattern"], "status": r["status"], "mapping_id": r["mapping_id"], "canonical_target": r["canonical_target"] or None})
    return out
