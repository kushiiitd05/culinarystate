"""Step 19 commit step (design section 5.4; PV-6, PV-9, PV-10). DRAFT_PENDING_H4; engineering only.

Each annotator, on their own machine:
- records an interim ``snapshot`` of a label file at its first ``validate`` run and again at ``DONE``;
- then builds one text-free commitment per wave (``commitments_<letter>_<wave>.json``), committed to git from
  their own session before the sealed key is opened.

The commitment holds packet ids, hashes, sizes and UTC times only (the shape of design appendix C), never label
or recipe text. Building refuses a file that is not ``DONE``, does not validate and replay cleanly, names another
annotator or letter, or lacks a FIRST_VALIDATE and a DONE snapshot whose last hash equals the committed file.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from culinarystate.annotation.gold import to_events, validate_gold
from culinarystate.annotation.pilot_packets import ANNOTATOR
from culinarystate.state_graph.engine import replay

EVENTS = ("FIRST_VALIDATE", "DONE")
WAVE_RE = re.compile(r"P[0-9]+[a-z]?")  # S168: P1b (P1b amendment)


def valid_wave(wave: str) -> bool:
    return isinstance(wave, str) and WAVE_RE.fullmatch(wave) is not None


def valid_packet_id(packet_id: str, letter: str) -> bool:
    return isinstance(packet_id, str) and re.fullmatch(rf"DGP-{re.escape(letter)}-[0-9]{{4}}", packet_id) is not None


class CommitError(ValueError):
    pass


def _sha_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def snapshot_entry(path: Path, event: str, utc: str) -> dict:
    if event not in EVENTS:
        raise CommitError(f"SNAPSHOT_EVENT_INVALID: {event!r} not in {EVENTS}")
    return {"sha256": _sha_file(path), "utc": utc, "event": event}


def label_problems(doc: dict, *, letter: str, packet_id: str) -> list[str]:
    """Reasons a finished label file cannot be committed (codes only, no label text)."""
    out = []
    if not packet_id.startswith(f"DGP-{letter}-"):
        out.append(f"PACKET_LETTER: {packet_id} is not a {letter} packet")
    if doc.get("recipe_id") != packet_id:
        out.append(f"PACKET_ID_MISMATCH: {packet_id}")
    if doc.get("annotator") != ANNOTATOR[letter]:
        out.append(f"ANNOTATOR_MISMATCH: {packet_id}")
    if doc.get("status") != "DONE":
        out.append(f"NOT_DONE: {packet_id}")
    errs = validate_gold(doc)
    if not errs:
        errs = list(replay(to_events(doc)).issues)
    if errs:
        out.append(f"INVALID: {packet_id} ({len(errs)} validate/replay issues)")
    return out


def _snapshot_problems(packet_id: str, file_sha: str, snapshots: Sequence[dict]) -> list[str]:
    """Snapshots in append-only log order: a FIRST_VALIDATE, later a DONE that is last and equals the file."""
    events = [s.get("event") for s in snapshots]
    if "FIRST_VALIDATE" not in events or "DONE" not in events:
        return [f"SNAPSHOTS: {packet_id} needs a FIRST_VALIDATE and a DONE snapshot (PV-10)"]
    if events[-1] != "DONE" or events.index("FIRST_VALIDATE") > len(events) - 2:
        return [f"SNAPSHOT_ORDER: {packet_id} must log FIRST_VALIDATE before a final DONE (PV-10)"]
    if snapshots[-1].get("sha256") != file_sha:
        return [f"LAST_SNAPSHOT_MISMATCH: {packet_id} changed after its last snapshot (PV-10)"]
    return []


def _nonempty_file_problem(path: Path, code: str) -> list[str]:
    p = Path(path)
    return [] if p.is_file() and p.stat().st_size > 0 else [f"{code}: must be a non-empty regular file"]


def build_commitment(files: Iterable[tuple[str, Path, Sequence[dict]]], *, letter: str, wave: str,
                     handbook_version: str, question_log: Path, representability: Path, now: str,
                     expected_ids: Sequence[str]) -> dict:
    """The commitment dict for one annotator and wave, or CommitError listing every problem.

    ``expected_ids`` (the issued packet ids of this letter and wave) must equal the committed file set (PV-6).
    """
    if letter not in ANNOTATOR:
        raise CommitError(f"letter must be one of {tuple(ANNOTATOR)}")
    if not valid_wave(wave):
        raise CommitError(f"WAVE_INVALID: {wave!r}")
    problems = _nonempty_file_problem(question_log, "QUESTION_LOG") + \
        _nonempty_file_problem(representability, "REPRESENTABILITY")
    rows = []
    for packet_id, path, snapshots in sorted(files, key=lambda f: f[0]):
        path = Path(path)
        try:
            data = path.read_bytes()
            doc = json.loads(data.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            problems.append(f"LABEL_UNREADABLE: {packet_id}")
            continue
        file_sha = hashlib.sha256(data).hexdigest()
        problems += label_problems(doc, letter=letter, packet_id=packet_id)
        problems += _snapshot_problems(packet_id, file_sha, snapshots)
        st = path.stat()
        rows.append({"packet_id": packet_id, "sha256": file_sha, "size_bytes": len(data),
                     "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "committed_utc": now, "snapshots": [dict(s) for s in snapshots]})
    have, want = {pid for pid, _, _ in files}, set(expected_ids)  # required since S166 (prv P5)
    if want - have:
        problems.append(f"MISSING_PACKETS: {len(want - have)} issued packet(s) not committed")
    if have - want:
        problems.append(f"EXTRA_PACKETS: {len(have - want)} file(s) not in the issued packet list")
    if not rows and not problems:
        problems.append("NO_FILES")
    if problems:
        raise CommitError("; ".join(problems))
    return {"annotator_letter": letter, "wave": wave, "handbook_version": handbook_version, "created_utc": now,
            "question_log_sha256": _sha_file(question_log), "representability_sha256": _sha_file(representability),
            "files": rows}
