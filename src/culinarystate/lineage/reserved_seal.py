"""15a.R: seeded, group-level, hash-committed RESERVED-group seal on the ES-1.1 snapshot.

Spine row 15a.R (``registry/execution_spine_v2.csv``) and Plan Step 15 card: a seeded
group-level hold-out over the existing ES-1.1 EVD rows, fraction pre-registered in 15.0,
hash-committed, 0 reads before 15b; needs no 08a.

Refusal conditions (all collected, none skipped): no explicit ``execute``; no decision id;
the decision is not a signed 15.0 entry in DECISIONS.md naming Kush as approver with exactly
one of each marker line below; the seed file is missing or its sha256 differs from the
committed one; the sealed-list path is missing, exists, is protected or could be tracked by
git (inside the repository and not git-ignored, or tracked); the commitment path exists or is
protected; the EVD ledger sha256 differs from the ES-1.1 manifest; the latest-ACTIVE row count
differs from the manifest. No EVD row is read until every other check passes.

Marker lines read from the decision entry (values are human-supplied; none is built in)::

    - **15.0 RESERVED_FRACTION:** a/b or a decimal in (0, 1)
    - **15.0 RESERVED_UNIT:** CELL | STUDY_THEN_CELL
    - **15.0 RESERVED_STRATIFY:** SOURCE_FAMILY | NONE
    - **15a.R SEED_SHA256:** sha256 hex of the UTF-8 seed (one trailing newline removed)

Group key (``GROUP_KEY_RULE``): CELL = (independence_group or source_family_id, casefolded
``matrix.raw_name``, ``transition.dataset.process_signature``); STUDY_THEN_CELL = rows with
``study_id_status == PRESENT`` grouped by independence_group alone, other rows by CELL.
Stratum = ``source_family_id``. Selection (``RULE_ID``): within each stratum rank groups by
sha256(rule id, snapshot sha256, seed, group id) and reserve floor(fraction x n_groups).
The commitment file holds parameters, counts and hashes only (no seed, no group id); the
sealed list must live outside git.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Optional

from culinarystate.lineage.guard import ProtectedPathError, assert_safe_write_target
from culinarystate.transition.dataset import process_signature

RULE_ID = "15aR-sha256-rank-v1"
GROUP_KEY_RULE = "15aR-group-v1"
TOOL_VERSION = "0.1.0"
UNITS = ("CELL", "STUDY_THEN_CELL")
STRATIFY = ("SOURCE_FAMILY", "NONE")
EVD_PATH = "ledgers/data/EVD.jsonl"
MANIFEST_PATH = "exports/evd/evd_export_v1.manifest.json"
COMMITMENT_PATH = "reports/step15/15a_R_seal_commitment_v1.json"
NON_PAYLOAD_KEYS = frozenset({"payload_sha256", "sealed_at_utc", "sealed_list_location"})
_MARKERS = {
    "FRACTION": r"15\.0 RESERVED_FRACTION",
    "UNIT": r"15\.0 RESERVED_UNIT",
    "STRATIFY": r"15\.0 RESERVED_STRATIFY",
    "SEED_COMMITMENT": r"15a\.R SEED_SHA256",
}
_HEADING = re.compile(r"^#{1,3} ", re.M)
_NOT_SIGNED = re.compile(r"\b(DRAFT|PROPOSED|UNSIGNED)\b", re.I)


class SealRefused(RuntimeError):
    """The seal may not run; ``blockers`` lists every reason as ``CODE: detail``."""

    def __init__(self, blockers: Iterable[str]):
        self.blockers = list(blockers)
        super().__init__("15a.R seal refused: " + "; ".join(self.blockers))


@dataclass(frozen=True)
class Ruling:
    decision_id: str
    fraction: Fraction
    unit: str
    stratify: str
    seed_sha256: str


@dataclass(frozen=True)
class GroupInfo:
    group_id: str
    kind: str
    independence_group: str
    matrix: str
    process: str
    stratum: str
    n_rows: int


def parse_fraction(text: str) -> Fraction:
    """Exact fraction strictly between 0 and 1 from 'a/b' or a decimal string."""
    s = str(text).strip()
    if not re.fullmatch(r"\d+/\d+|\d*\.\d+|\d+", s):
        raise ValueError(f"not a fraction: {text!r}")
    value = Fraction(s)
    if not 0 < value < 1:
        raise ValueError(f"fraction must lie strictly between 0 and 1: {text!r}")
    return value


def canonical_sha256(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> Iterator[dict]:
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


# ---------------------------------------------------------------- decision entry

def _entries(text: str) -> dict[str, tuple[str, str]]:
    """decision id -> (heading line, entry body) for every '## D-NNN' / '### D-NNN' heading."""
    out: dict[str, tuple[str, str]] = {}
    starts = [m.start() for m in _HEADING.finditer(text)] + [len(text)]
    for a, b in zip(starts, starts[1:]):
        block = text[a:b]
        heading, _, body = block.partition("\n")
        m = re.match(r"^#{2,3} (D-\d{3})\b", heading)
        if m and m.group(1) not in out:
            out[m.group(1)] = (heading, body)
    return out


def _marker_values(body: str, pattern: str) -> list[str]:
    return re.findall(rf"^- \*\*{pattern}:\*\*[ \t]*(.*?)[ \t]*$", body, re.M)


def find_ruling(decisions_text: str, decision_id: str) -> Ruling:
    """Parse the signed 15.0 entry ``decision_id`` or raise SealRefused naming every defect."""
    entry = _entries(decisions_text).get(decision_id)
    if entry is None:
        raise SealRefused([f"DECISION_NOT_FOUND: {decision_id} has no heading in DECISIONS.md"])
    heading, body = entry
    blockers: list[str] = []
    if "15.0" not in heading:
        blockers.append(f"DECISION_NOT_15_0: {decision_id} heading does not name step 15.0")
    if _NOT_SIGNED.search(heading):
        blockers.append(f"DECISION_NOT_SIGNED: {decision_id} heading is marked draft/proposed/unsigned")
    approvers = _marker_values(body, "Approver")
    if len(approvers) != 1 or "kush" not in approvers[0].lower():
        blockers.append(f"APPROVER_NOT_KUSH: {decision_id} needs exactly one Approver line naming Kush")
    values: dict[str, Optional[str]] = {}
    for name, pattern in _MARKERS.items():
        found = _marker_values(body, pattern)
        if not found:
            blockers.append(f"{name}_MISSING: no '{pattern.replace(chr(92), '')}' line in {decision_id}")
        elif len(found) > 1:
            blockers.append(f"{name}_DUPLICATE: {len(found)} '{pattern.replace(chr(92), '')}' lines in {decision_id}")
        values[name] = found[0] if len(found) == 1 else None
    fraction: Optional[Fraction] = None
    if values["FRACTION"] is not None:
        try:
            fraction = parse_fraction(values["FRACTION"])
        except ValueError as exc:
            blockers.append(f"FRACTION_INVALID: {exc}")
    if values["UNIT"] is not None and values["UNIT"] not in UNITS:
        blockers.append(f"UNIT_INVALID: {values['UNIT']!r} not in {UNITS}")
    if values["STRATIFY"] is not None and values["STRATIFY"] not in STRATIFY:
        blockers.append(f"STRATIFY_INVALID: {values['STRATIFY']!r} not in {STRATIFY}")
    seed = values["SEED_COMMITMENT"]
    if seed is not None and not re.fullmatch(r"[0-9a-f]{64}", seed):
        blockers.append("SEED_COMMITMENT_INVALID: expected 64 lower-case hex characters")
    if blockers:
        raise SealRefused(blockers)
    assert fraction is not None and seed is not None
    return Ruling(decision_id, fraction, str(values["UNIT"]), str(values["STRATIFY"]), seed)


def find_15_0_rulings(decisions_text: str) -> list[str]:
    """Decision ids whose entry parses as a complete signed 15.0 ruling."""
    found = []
    for did in _entries(decisions_text):
        try:
            find_ruling(decisions_text, did)
        except SealRefused:
            continue
        found.append(did)
    return found


# ---------------------------------------------------------------- groups and selection

def latest_active(rows: Iterable[Mapping]) -> list[dict]:
    """Last version of every id (append order), kept only if its status is ACTIVE."""
    last: dict[str, dict] = {}
    for r in rows:
        last[str(r["id"])] = dict(r)
    return [r for r in last.values() if r.get("status") == "ACTIVE"]


def _group_fields(row: Mapping, unit: str) -> tuple[str, str, str, str]:
    ig = str(row.get("independence_group") or row.get("source_family_id") or "")
    if not ig:
        raise ValueError(f"{row.get('id')}: no independence_group or source_family_id")
    if unit == "STUDY_THEN_CELL" and row.get("study_id_status") == "PRESENT" and row.get("study_ids"):
        return "STUDY", ig, "", ""
    matrix = str((row.get("matrix") or {}).get("raw_name") or "").lower()
    return "CELL", ig, matrix, process_signature(dict(row))


def build_groups(rows: Iterable[Mapping], unit: str) -> dict[str, GroupInfo]:
    """Group rows by ``unit``; a group whose rows span two source families is refused."""
    if unit not in UNITS:
        raise ValueError(f"unknown unit {unit!r}; expected one of {UNITS}")
    acc: dict[str, list] = {}
    for r in rows:
        kind, ig, matrix, process = _group_fields(r, unit)
        gid = "RG-" + canonical_sha256([kind, ig, matrix, process])
        stratum = str(r.get("source_family_id") or "")
        cur = acc.setdefault(gid, [kind, ig, matrix, process, stratum, 0])
        if cur[4] != stratum:
            raise ValueError(f"group {ig!r} spans more than one stratum ({cur[4]!r}, {stratum!r})")
        cur[5] += 1
    return {gid: GroupInfo(gid, *vals) for gid, vals in acc.items()}


def select_reserved(groups: Mapping[str, GroupInfo], *, snapshot_sha256: str, seed: str,
                    fraction: Fraction, stratify: str) -> list[str]:
    """Deterministic reserved group ids (sorted) for (snapshot, seed, fraction, stratify)."""
    if stratify not in STRATIFY:
        raise ValueError(f"unknown stratify {stratify!r}; expected one of {STRATIFY}")
    fraction = Fraction(fraction)
    if not 0 < fraction < 1:
        raise ValueError("fraction must lie strictly between 0 and 1")
    strata: dict[str, list[str]] = {}
    for gid, g in groups.items():
        strata.setdefault(g.stratum if stratify == "SOURCE_FAMILY" else "ALL", []).append(gid)
    chosen: list[str] = []
    for ids in strata.values():
        ranked = sorted(ids, key=lambda gid: (hashlib.sha256(
            f"{RULE_ID}\n{snapshot_sha256}\n{seed}\n{gid}".encode("utf-8")).hexdigest(), gid))
        chosen.extend(ranked[:math.floor(fraction * len(ranked))])
    return sorted(chosen)


def sealed_list_bytes(reserved: Iterable[str], groups: Mapping[str, GroupInfo]) -> bytes:
    lines = []
    for gid in sorted(reserved):
        g = groups[gid]
        lines.append(json.dumps({"group_id": g.group_id, "kind": g.kind, "independence_group": g.independence_group,
                                 "matrix": g.matrix, "process": g.process, "stratum": g.stratum,
                                 "n_rows": g.n_rows}, sort_keys=True, ensure_ascii=False) + "\n")
    return "".join(lines).encode("utf-8")


def universe_sha256(groups: Mapping[str, GroupInfo]) -> str:
    return hashlib.sha256("".join(f"{gid}\n" for gid in sorted(groups)).encode("utf-8")).hexdigest()


def build_commitment(*, ruling: Ruling, groups: Mapping[str, GroupInfo], reserved: Iterable[str],
                     sealed_bytes: bytes, snapshot: Mapping[str, Any]) -> dict:
    reserved = set(reserved)
    strata: dict[str, dict[str, int]] = {}
    for gid, g in groups.items():
        s = strata.setdefault(g.stratum, {"n_groups": 0, "n_reserved": 0, "n_rows": 0, "n_reserved_rows": 0})
        s["n_groups"] += 1
        s["n_rows"] += g.n_rows
        if gid in reserved:
            s["n_reserved"] += 1
            s["n_reserved_rows"] += g.n_rows
    payload = {
        "record_type": "RESERVED_SEAL_COMMITMENT_15A_R", "rule_id": RULE_ID, "group_key_rule": GROUP_KEY_RULE,
        "tool_version": TOOL_VERSION, "decision_id": ruling.decision_id, "fraction": str(ruling.fraction),
        "unit": ruling.unit, "stratify": ruling.stratify, "seed_sha256": ruling.seed_sha256,
        "snapshot": dict(snapshot), "n_groups": len(groups), "n_reserved": len(reserved),
        "n_reserved_rows": sum(groups[g].n_rows for g in reserved), "strata": strata,
        "universe_sha256": universe_sha256(groups),
        "reserved_list_sha256": hashlib.sha256(sealed_bytes).hexdigest(),
    }
    return {**payload, "payload_sha256": canonical_sha256(payload),
            "sealed_list_location": "NOT_RECORDED (kept outside git)",
            "sealed_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat()}


def verify_sealed_list(sealed_bytes: bytes, commitment: Mapping[str, Any]) -> bool:
    payload = {k: v for k, v in commitment.items() if k not in NON_PAYLOAD_KEYS}
    return (hashlib.sha256(sealed_bytes).hexdigest() == commitment.get("reserved_list_sha256")
            and canonical_sha256(payload) == commitment.get("payload_sha256"))


# ---------------------------------------------------------------- guards and run

def read_seed(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8")
    return text[:-1] if text.endswith("\n") else text


def _git_ok(args: list[str], root: Path) -> Optional[bool]:
    try:
        res = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    except OSError:
        return None
    return {0: True, 1: False}.get(res.returncode)


def trackable_reason(path: Path, root: Path) -> Optional[str]:
    """Why ``path`` could end up in git (inside root and not ignored, or tracked); None if safe."""
    target, base = Path(path).resolve(), Path(root).resolve()
    try:
        rel = target.relative_to(base).as_posix()
    except ValueError:
        return None
    if _git_ok(["check-ignore", "-q", "--", rel], base) is not True:
        return f"{rel} is inside the repository and not git-ignored"
    if _git_ok(["ls-files", "--error-unmatch", "--", rel], base) is not False:
        return f"{rel} is tracked or its git status is unknown"
    return None


def _protected(path: Path) -> bool:
    try:
        assert_safe_write_target(path)
    except ProtectedPathError:
        return True
    return False


def collect_blockers(*, root: Path, decision_id: Optional[str], seed_file: Optional[Path],
                     sealed_out: Optional[Path], commitment_out: Optional[Path], require_execute: bool,
                     execute: bool) -> tuple[list[str], Optional[Ruling], Optional[str]]:
    """Every refusal reason, the parsed ruling (or None) and the verified snapshot sha256 (or None)."""
    root = Path(root)
    blockers: list[str] = []
    if require_execute and not execute:
        blockers.append("EXECUTE_FLAG_MISSING: pass --execute explicitly")
    ruling: Optional[Ruling] = None
    if not decision_id:
        blockers.append("NO_15_0_DECISION_ID: no signed 15.0 decision named (none exists in DECISIONS.md yet)")
    else:
        try:
            ruling = find_ruling((root / "DECISIONS.md").read_text(encoding="utf-8"), decision_id)
        except OSError:
            blockers.append("DECISIONS_UNREADABLE: DECISIONS.md missing")
        except SealRefused as exc:
            blockers.extend(exc.blockers)
    if seed_file is None:
        blockers.append("SEED_FILE_MISSING: pass --seed-file (kept outside git)")
    elif not Path(seed_file).is_file():
        blockers.append(f"SEED_FILE_MISSING: {seed_file} not found")
    else:
        reason = trackable_reason(Path(seed_file), root)
        if reason:
            blockers.append(f"SEED_FILE_TRACKABLE: {reason}")
        if ruling and hashlib.sha256(read_seed(Path(seed_file)).encode("utf-8")).hexdigest() != ruling.seed_sha256:
            blockers.append("SEED_COMMITMENT_MISMATCH: seed sha256 differs from the decision's SEED_SHA256")
    if sealed_out is None:
        blockers.append("SEALED_OUT_MISSING: pass --sealed-out outside git")
    else:
        if Path(sealed_out).exists():
            blockers.append(f"SEALED_OUT_EXISTS: {sealed_out} (a seal is never overwritten)")
        if _protected(Path(sealed_out)):
            blockers.append(f"SEALED_OUT_PROTECTED: {sealed_out}")
        reason = trackable_reason(Path(sealed_out), root)
        if reason:
            blockers.append(f"SEALED_OUT_TRACKABLE: {reason}")
    if commitment_out is not None:
        if Path(commitment_out).exists():
            blockers.append(f"COMMITMENT_EXISTS: {commitment_out}")
        if _protected(Path(commitment_out)):
            blockers.append(f"COMMITMENT_PROTECTED: {commitment_out}")
    snapshot_sha: Optional[str] = None
    evd, manifest = root / EVD_PATH, root / MANIFEST_PATH
    try:
        expected = json.loads(manifest.read_text(encoding="utf-8"))["ledger_sha256"]
        snapshot_sha = sha256_file(evd)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        blockers.append(f"SNAPSHOT_MISSING: {exc}")
    else:
        if snapshot_sha != expected:
            blockers.append("SNAPSHOT_HASH_MISMATCH: EVD ledger sha256 differs from the ES-1.1 manifest")
            snapshot_sha = None
    return blockers, ruling, snapshot_sha


def run_seal(*, root: Path, decision_id: Optional[str], seed_file: Optional[Path],
             sealed_out: Optional[Path], commitment_out: Optional[Path] = None, execute: bool = False) -> dict:
    """Seal the RESERVED groups or raise SealRefused; returns the commitment written."""
    root = Path(root)
    commitment_out = Path(commitment_out) if commitment_out else root / COMMITMENT_PATH
    blockers, ruling, snapshot_sha = collect_blockers(
        root=root, decision_id=decision_id, seed_file=seed_file, sealed_out=sealed_out,
        commitment_out=commitment_out, require_execute=True, execute=execute)
    if blockers:
        raise SealRefused(blockers)
    assert ruling is not None and snapshot_sha is not None and seed_file is not None and sealed_out is not None
    manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
    rows = latest_active(read_jsonl(root / EVD_PATH))
    if len(rows) != manifest.get("active_rows"):
        raise SealRefused([f"SNAPSHOT_ROWCOUNT_MISMATCH: {len(rows)} latest ACTIVE rows, "
                           f"manifest says {manifest.get('active_rows')}"])
    groups = build_groups(rows, ruling.unit)
    reserved = select_reserved(groups, snapshot_sha256=snapshot_sha, seed=read_seed(Path(seed_file)),
                               fraction=ruling.fraction, stratify=ruling.stratify)
    sealed = sealed_list_bytes(reserved, groups)
    commitment = build_commitment(ruling=ruling, groups=groups, reserved=reserved, sealed_bytes=sealed,
                                  snapshot={"evd_path": EVD_PATH, "evd_sha256": snapshot_sha,
                                            "manifest_path": MANIFEST_PATH, "active_rows": len(rows)})
    Path(sealed_out).parent.mkdir(parents=True, exist_ok=True)
    with Path(sealed_out).open("xb") as fh:
        fh.write(sealed)
    commitment_out.parent.mkdir(parents=True, exist_ok=True)
    with commitment_out.open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(commitment, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return commitment
