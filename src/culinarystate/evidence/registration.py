"""Step 12.0 PROPOSED SRC/SNAP registration rows for local structured-database files (S157).

Status: PROVISIONAL_PENDING_H2_REBASELINE. SRC.jsonl and SNAP.jsonl are byte-identical-protected
(registry/baseline_ledger_hashes_08a_v1.csv, lineage/guard.py), so this module never appends to
them, mints no id and never writes under ``ledgers/``. It computes sha256 / size / locator of the
given local files and emits PROPOSED rows shaped like the ledger schemas (``ledgers/schemas``) to
a staging file for Kush's review. Appending them needs an explicit human re-baseline decision.

Rules
- Placeholder ids ``PROPOSED-SRC-####`` / ``PROPOSED-SNAP-####`` can never match a real id pattern
  and are checked against ``ledgers/data/_ids.jsonl``; proposed mint keys are checked too. A file
  whose ``sha256:<hex>`` key is already minted is reported ALREADY_REGISTERED, not re-proposed.
- Licence fields are copied from ``registry/data_source_acquisition_manifest.csv``; the SRC
  ``licence_status`` mapping is conservative (only the literal tokens VERIFIED, VERIFIED_AT_INGESTION
  and ASSUMED survive, a qualified status such as "...; re-check failed" becomes UNKNOWN, BLOCKED /
  NC / RESTRICTED / RESTRICTIVE become RESTRICTED, every catalog-reported or unknown status becomes
  UNKNOWN). The raw manifest
  values are kept beside each proposal.
- A source with an open H2 item (``reports/h_state/es_1_2_h2_approval_queue.md``), a manifest
  ``human_approval_required = yes`` or a restricted licence is flagged LOCAL_ONLY. COMMIT_OK is
  never proposed by code (it needs a human licence verification).
- Values the files do not give (``created_at``, ``created_by``, a missing ``retrieved_at``) are
  listed as gaps and left out; nothing is invented. A ``.snap.json`` sidecar written by
  ``ingest/acquire.py`` supplies retrieval facts only when its sha256 matches the file.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from culinarystate.lineage.guard import ProtectedPathError, assert_safe_write_target

STATUS = "PROVISIONAL_PENDING_H2_REBASELINE"
TOOL_VERSION = "step12_0_registration@0.1-provisional"
ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "ledgers" / "schemas"
PLACEHOLDER = re.compile(r"^PROPOSED-(SRC|SNAP)-\d{4}$")
KIND_MAP = {"database": "DATABASE", "dataset": "DATASET", "api": "API", "website": "WEBSITE", "book": "BOOK"}
_CHUNK = 1 << 20


class RegistrationError(ValueError):
    """Unknown manifest entry or refused write."""


# ---------------------------------------------------------------- loaders (read-only)
def load_manifest(path: Path | str) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as fh:
        return {r["source_id"].strip(): r for r in csv.DictReader(fh) if (r.get("source_id") or "").strip()}


def load_h2_open(path: Path | str) -> dict[str, tuple[str, ...]]:
    """DS ids named in the H2 approval-queue table -> item numbers (the queue records no executed item)."""
    out: dict[str, list[str]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[0].isdigit():
            continue
        for ds in re.findall(r"DS-\d{3}", line):
            out.setdefault(ds, [])
            if cells[0] not in out[ds]:
                out[ds].append(cells[0])
    return {k: tuple(v) for k, v in sorted(out.items())}


VERIFIED_TOKENS = frozenset({"VERIFIED", "VERIFIED_AT_INGESTION"})


def map_licence_status(raw: str | None) -> str:
    """Literal tokens only: a qualified status (e.g. "VERIFIED_AT_INGESTION; re-check failed") is UNKNOWN (R3)."""
    s = (raw or "").strip().upper()
    if s in VERIFIED_TOKENS:
        return "VERIFIED"
    if s == "ASSUMED":
        return "ASSUMED"
    if s.startswith(("BLOCKED", "NC_")) or "RESTRICTED" in s or "RESTRICTIVE" in s:
        return "RESTRICTED"
    return "UNKNOWN"


@dataclass
class IdIndex:
    ids: set[str] = field(default_factory=set)
    keys: dict[tuple[str, str], str] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path | str) -> IdIndex:
        idx = cls()
        with Path(path).open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                idx.ids.add(r["id"])
                if r.get("key") is not None:
                    idx.keys.setdefault((r.get("prefix") or r["id"].split("-")[0], r["key"]), r["id"])
        return idx

    def lookup(self, prefix: str, key: str) -> str | None:
        return self.keys.get((prefix, key))


def existing_src_by_family(path: Path | str) -> dict[str, tuple[str, ...]]:
    """source_family_id -> ids of SRC records whose latest version is ACTIVE."""
    latest: dict[str, dict] = {}
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                latest[r["id"]] = r
    fam: dict[str, set[str]] = {}
    for r in latest.values():
        if r.get("status") == "ACTIVE" and r.get("source_family_id"):
            fam.setdefault(r["source_family_id"], set()).add(r["id"])
    return {k: tuple(sorted(v)) for k, v in sorted(fam.items())}


# ---------------------------------------------------------------- files
def sha256_and_size(path: Path) -> tuple[str, int]:
    h, n = hashlib.sha256(), 0
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(_CHUNK), b""):
            h.update(block)
            n += len(block)
    return h.hexdigest(), n


def expand(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.rglob("*") if p.is_file() and not p.name.startswith(".")
                      and not p.name.endswith(".snap.json")
                      and not any(part.startswith(".") for part in p.relative_to(path).parts))
    return []


def _locator(path: Path, root: Path) -> tuple[str, bool]:
    p = path.resolve()
    try:
        return p.relative_to(root.resolve()).as_posix(), True
    except ValueError:
        return str(p), False


def _sidecar(path: Path, sha: str) -> tuple[dict | None, str | None]:
    side = path.with_name(path.name + ".snap.json")
    if not side.is_file():
        return None, None
    try:
        meta = json.loads(side.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "SIDECAR_UNREADABLE"
    if meta.get("sha256") != sha:
        return None, "SIDECAR_SHA_MISMATCH"
    return meta, "SIDECAR_USED"


# ---------------------------------------------------------------- schema check
@dataclass(frozen=True)
class _Checker:
    src: Draft202012Validator
    snap: Draft202012Validator

    @classmethod
    def load(cls, schemas: Path = SCHEMAS) -> _Checker:
        def v(name: str) -> Draft202012Validator:
            s = json.loads((schemas / f"{name}.schema.json").read_text(encoding="utf-8"))
            return Draft202012Validator(s, format_checker=FormatChecker())
        return cls(v("SRC"), v("SNAP"))

    def check(self, rec: dict) -> tuple[list[str], list[str]]:
        """(missing required properties, other schema errors) with placeholders read as id-shaped."""
        def sub(x: Any) -> Any:
            if isinstance(x, str) and PLACEHOLDER.match(x):
                return x.split("-")[1] + "-000000"
            if isinstance(x, dict):
                return {k: sub(v) for k, v in x.items()}
            if isinstance(x, list):
                return [sub(v) for v in x]
            return x
        val = self.src if rec["record_type"] == "SRC" else self.snap
        gaps, errs = [], []
        for e in sorted(val.iter_errors(sub(rec)), key=lambda e: (list(e.absolute_path), e.message)):
            m = re.match(r"^'(\w+)' is a required property$", e.message)
            if m and not e.absolute_path:
                gaps.append(m.group(1))
            else:
                errs.append(f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}")
        return gaps, errs


# ---------------------------------------------------------------- proposals
def _ds_policy(row: Mapping[str, str], h2_items: Sequence[str]) -> tuple[str, list[str]]:
    flags: list[str] = []
    status = map_licence_status(row.get("licence_status"))
    approval = (row.get("human_approval_required") or "").strip().lower()
    if h2_items:
        flags.append("H2_OPEN")
    if approval.startswith("yes"):
        flags.append("HUMAN_APPROVAL_REQUIRED")
    if "re-check" in approval or "recheck" in approval:
        flags.append("LICENCE_RECHECK_RECOMMENDED")
    if status == "RESTRICTED":
        flags.append("LICENCE_RESTRICTED")
    redis = (row.get("redistribution_allowed") or "").upper()
    raw_txt = (row.get("raw_text_storage_allowed") or "").strip().lower()
    derived = (row.get("derived_data_allowed") or "").strip().lower()
    if {"H2_OPEN", "HUMAN_APPROVAL_REQUIRED", "LICENCE_RESTRICTED"} & set(flags):
        rule = "LOCAL_ONLY"
    elif "DERIVED_ONLY" in redis or raw_txt.startswith("no") or derived.startswith("yes"):
        rule = "DERIVED_ONLY"
    else:
        rule, flags = "LOCAL_ONLY", [*flags, "DERIVED_USE_UNKNOWN"]
    if rule == "LOCAL_ONLY":
        flags.append("LOCAL_ONLY")
    return rule, flags


def _licence_raw(row: Mapping[str, str]) -> dict[str, str]:
    keys = ("licence", "licence_status", "licence_verification", "redistribution_allowed", "derived_data_allowed",
            "raw_text_storage_allowed", "human_approval_required", "blocking_issue")
    return {k: row.get(k, "") for k in keys}


def build_proposals(entries: Sequence[tuple[str, Path | str]], *, manifest: Mapping[str, Mapping[str, str]],
                    h2_open: Mapping[str, Sequence[str]], id_index: IdIndex,
                    existing_src: Mapping[str, Sequence[str]], root: Path | str,
                    schemas: Path = SCHEMAS) -> list[dict]:
    """Deterministic PROPOSED SRC/SNAP rows for (manifest DS id, local file or directory) entries."""
    root = Path(root)
    checker = _Checker.load(schemas)
    rows: list[dict] = []
    n_src = n_snap = 0
    src_refs: dict[str, tuple[str, str, list[str]]] = {}
    seen_sha: dict[str, str] = {}
    for ds, raw_path in entries:
        if ds not in manifest:
            raise RegistrationError(f"{ds} is not a row of the acquisition manifest")
        m = manifest[ds]
        h2 = list(h2_open.get(ds, ()))
        rule, ds_flags = _ds_policy(m, h2)
        path = Path(raw_path) if Path(raw_path).is_absolute() else root / raw_path
        found = expand(path)
        if not found:
            rows.append({"record": "MISSING_LOCAL_FILE", "manifest_source_id": ds, "locator": _locator(path, root)[0]})
            continue
        if ds not in src_refs:
            family = (m.get("ledger_src_family") or "").strip()
            fam_ids = tuple(existing_src.get(family, ())) if family and family.lower() != "none" else ()
            if len(fam_ids) == 1:
                src_refs[ds] = (fam_ids[0], "EXISTING_SRC", [])
            else:
                n_src += 1
                pid = f"PROPOSED-SRC-{n_src:04d}"
                flags = list(ds_flags) + (["AMBIGUOUS_EXISTING_SRC"] if len(fam_ids) > 1 else [])
                kind = KIND_MAP.get((m.get("source_type") or "").strip().lower())
                rec: dict[str, Any] = {
                    "id": pid, "record_type": "SRC", "schema_version": "1.0.0", "version": 1, "status": "ACTIVE",
                    "provenance": {"method": "MANUAL", "source_ids": [], "agent": f"rule:{TOOL_VERSION}",
                                   "notes": f"PROPOSED from acquisition manifest {ds}; not appended"},
                    "verification": {"status": "UNVERIFIED"},
                    "title": (m.get("source_name") or "").strip() or "UNKNOWN",
                    "url": (m.get("official_url") or "").strip() or None,
                    "publisher": (m.get("provider") or "").strip() or None,
                    "licence": (m.get("licence") or "").strip() or "UNKNOWN",
                    "licence_status": map_licence_status(m.get("licence_status")), "storage_rule": rule,
                    "primary_or_secondary": "UNKNOWN",
                    "source_family_id": family if family and family.lower() != "none" else None,
                    "notes": f"manifest {ds}; licence fields copied from the manifest; {STATUS}"}
                if kind:
                    rec["kind"] = kind
                if rec["source_family_id"] is None:
                    flags.append("SOURCE_FAMILY_UNASSIGNED")
                key = f"manifest:{ds}"
                key_used = id_index.lookup("SRC", key) is not None
                if key_used:
                    flags.append("MINT_KEY_ALREADY_USED")
                gaps, errs = checker.check(rec)
                rows.append({"record": "PROPOSED_SRC", "proposal_id": pid, "manifest_source_id": ds,
                             "proposed_mint_key": key, "flags": sorted(set(flags)), "gaps": gaps, "schema_errors": errs,
                             "id_check": {"placeholder_in_ids_ledger": pid in id_index.ids,
                                          "mint_key_in_ids_ledger": key_used},
                             "licence_raw": _licence_raw(m), "h2_items": h2, "proposed_record": rec})
                src_refs[ds] = (pid, "PROPOSED_SRC", [])
        src_ref, ref_status, _ = src_refs[ds]
        for f in found:
            sha, size = sha256_and_size(f)
            loc, inside = _locator(f, root)
            info = {"locator": loc, "sha256": sha, "bytes": size}
            key = f"sha256:{sha}"
            existing = id_index.lookup("SNAP", key)
            if existing:
                rows.append({"record": "ALREADY_REGISTERED_SNAP", "manifest_source_id": ds, "file": info,
                             "existing_snap_id": existing})
                continue
            if sha in seen_sha:
                rows.append({"record": "DUPLICATE_CONTENT_IN_RUN", "manifest_source_id": ds, "file": info,
                             "same_as_proposal": seen_sha[sha]})
                continue
            n_snap += 1
            pid = f"PROPOSED-SNAP-{n_snap:04d}"
            seen_sha[sha] = pid
            flags = list(ds_flags) + ([] if inside else ["OUTSIDE_REPO_ROOT"])
            meta, side_flag = _sidecar(f, sha)
            if side_flag:
                flags.append(side_flag)
            snap: dict[str, Any] = {
                "id": pid, "record_type": "SNAP", "schema_version": "1.0.0", "version": 1, "status": "ACTIVE",
                "provenance": {"method": "MANUAL", "source_ids": [src_ref], "agent": f"rule:{TOOL_VERSION}",
                               "notes": f"PROPOSED local snapshot for {ds}; not appended"},
                "verification": {"status": "UNVERIFIED"}, "source_id": src_ref,
                "retrieval_url": (meta or {}).get("url"), "sha256": sha, "bytes": size, "local_path": loc,
                "source_version": (m.get("current_version") or "").strip() or None,
                "http_status": (meta or {}).get("http_status")}
            if meta and meta.get("retrieved_at"):
                snap["retrieved_at"] = meta["retrieved_at"]
            gaps, errs = checker.check(snap)
            rows.append({"record": "PROPOSED_SNAP", "proposal_id": pid, "manifest_source_id": ds, "src_ref": src_ref,
                         "src_ref_status": ref_status, "proposed_mint_key": key, "file": info,
                         "flags": sorted(set(flags)), "gaps": gaps, "schema_errors": errs,
                         "id_check": {"placeholder_in_ids_ledger": pid in id_index.ids,
                                      "mint_key_in_ids_ledger": False},
                         "h2_items": h2, "proposed_record": snap})
    return rows


# ---------------------------------------------------------------- staging writer
_PROTECTED = (("ledgers",), ("exports",), ("annotation", "gold"), ("data",))
_LEDGER_NAMES = frozenset({"SRC.JSONL", "SNAP.JSONL", "_IDS.JSONL", "EVD.JSONL", "COND.JSONL", "MEAS.JSONL",
                           "STUDY.JSONL", "DOC.JSONL"})


def guard_output_path(path: Path | str, *, root: Path | str = ROOT) -> Path:
    target = Path(path).resolve()
    if target.name.upper() in _LEDGER_NAMES:
        raise RegistrationError("refusing a file named like a ledger")
    try:
        parts = tuple(x.casefold() for x in target.relative_to(Path(root).resolve()).parts)
    except ValueError:
        parts = ()
    if any(parts[:len(p)] == p for p in _PROTECTED):
        raise RegistrationError("refusing a staging file inside ledgers/, exports/, data/ or annotation/gold/")
    try:
        assert_safe_write_target(target)
    except ProtectedPathError as e:
        raise RegistrationError(str(e)) from e
    if target.exists():
        raise RegistrationError("refusing to overwrite an existing staging file")
    return target


def write_staging(rows: Iterable[dict], path: Path | str, *, root: Path | str = ROOT,
                  inputs: Mapping[str, Any]) -> Path:
    rows = list(rows)
    target = guard_output_path(path, root=root)
    head = {"record": "STAGING_HEADER", "status": STATUS, "tool_version": TOOL_VERSION, "inputs": dict(inputs),
            "counts": dict(sorted(Counter(r["record"] for r in rows).items())), "ids_minted": 0,
            "ledger_rows_appended": 0,
            "note": "PROPOSED rows only. SRC/SNAP are byte-identical-protected: appending needs Kush's review and an "
                    "explicit human re-baseline decision; real ids are minted only then."}
    target.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in (head, *rows))
    with open(target, "x", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return target
