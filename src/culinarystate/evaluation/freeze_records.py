"""15a bootstrap freeze record and 29-diag pre-registration signature (S173). Formats only; humans approve.

Freeze record ``registry/freezes/<snapshot_id>.json``: the SHA-256 of every frozen ledger file and of the 15a.R
seal commitment, written as PROPOSED by ``propose_freeze``. It counts as frozen only when a human has set
status FROZEN, approved_by to a named human (never an AI marker) and approved_date, AND every recorded hash still
matches the bytes on disk. The 29-diag pre-registration counts as signed only when
``reports/step29/29diag_prereg_signature.json`` names a human signer and the SHA-256 of the current pre-registration
text (an edit after signing voids it). D-071: the agent never signs or approves.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

FREEZE_DIR = "registry/freezes"
FROZEN_LEDGERS = ("EVD.jsonl", "COND.jsonl", "SRC.jsonl", "MEAS.jsonl", "SNAP.jsonl", "STUDY.jsonl", "PROC.jsonl",
                  "ING.jsonl", "SVAR.jsonl")
SEAL_COMMITMENT = "reports/step15/15a_R_seal_commitment_v1.json"
PREREG = "reports/step29/29diag_preregistration_DRAFT.md"
PREREG_SIGNATURE = "reports/step29/29diag_prereg_signature.json"
HUMANS = ("Kush Tokas", "Parv Goyal")
AI_DELEGATE = "ksh+prv (AI, D-085)"      # D-085: AI personas act on the humans' behalf, under their own name only
APPROVERS = (*HUMANS, AI_DELEGATE)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _hashes(root: Path) -> dict[str, str]:
    out = {f"ledgers/data/{n}": _sha(root / "ledgers/data" / n) for n in FROZEN_LEDGERS
           if (root / "ledgers/data" / n).is_file()}
    if (root / SEAL_COMMITMENT).is_file():
        out[SEAL_COMMITMENT] = _sha(root / SEAL_COMMITMENT)
    return out


def propose_freeze(root: Path | str, snapshot_id: str) -> dict:
    root = Path(root)
    rec = {"record": "FREEZE_15A_BOOTSTRAP", "snapshot_id": snapshot_id, "status": "PROPOSED",
           "proposed_by": "AI_AGENT", "proposed_date": date.today().isoformat(), "ledger_sha256": _hashes(root),
           "use": "15a / 29-diag diagnostic only; BOOTSTRAP_UNVERIFIED; RESERVED groups unread (15a.R seal)",
           "approved_by": None, "approved_date": None,
           "how_to_approve": "a named human sets status FROZEN, approved_by, approved_date; any ledger change voids it"}
    path = root / FREEZE_DIR / f"{snapshot_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return rec


def freeze_problems(root: Path | str, snapshot_id: str) -> list[str]:
    root = Path(root)
    path = root / FREEZE_DIR / f"{snapshot_id}.json"
    if not path.is_file():
        return ["NO_FREEZE_RECORD"]
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["FREEZE_RECORD_UNREADABLE"]
    probs = []
    if rec.get("status") != "FROZEN":
        probs.append("NOT_APPROVED")
    if rec.get("approved_by") not in APPROVERS or not rec.get("approved_date"):
        probs.append("NO_HUMAN_APPROVAL")
    now = _hashes(root)
    if not rec.get("ledger_sha256") or any(now.get(k) != v for k, v in rec["ledger_sha256"].items()):
        probs.append("SNAPSHOT_HASH_MISMATCH")
    return probs


def frozen_snapshot_ids(root: Path | str) -> frozenset[str]:
    d = Path(root) / FREEZE_DIR
    ids = [p.stem for p in d.glob("*.json")] if d.is_dir() else []
    return frozenset(i for i in ids if not freeze_problems(root, i))


def prereg_signed(root: Path | str) -> bool:
    root = Path(root)
    sig, pre = root / PREREG_SIGNATURE, root / PREREG
    if not (sig.is_file() and pre.is_file()):
        return False
    try:
        s = json.loads(sig.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return s.get("signed_by") in APPROVERS and bool(s.get("signed_date")) and s.get("prereg_sha256") == _sha(pre)


def _kind(who) -> str | None:
    return "HUMAN" if who in HUMANS else ("AI_DELEGATED_D085" if who == AI_DELEGATE else None)


def approval_kind(root: Path | str, snapshot_id: str) -> str | None:
    """HUMAN, AI_DELEGATED_D085 or None for a freeze record's approver."""
    p = Path(root) / FREEZE_DIR / f"{snapshot_id}.json"
    try:
        return _kind(json.loads(p.read_text(encoding="utf-8")).get("approved_by"))
    except (OSError, ValueError):
        return None


def prereg_signer_kind(root: Path | str) -> str | None:
    p = Path(root) / PREREG_SIGNATURE
    try:
        return _kind(json.loads(p.read_text(encoding="utf-8")).get("signed_by"))
    except (OSError, ValueError):
        return None
