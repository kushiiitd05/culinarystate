"""Hash-commitment helper for the shared Step 22c / 23 mechanism case set (S158, DRAFT_PENDING_21b_H4).

Spine row 22a: "shared case set sealed before rule coding" is a HUMAN gate. This module only computes and
checks a commitment; it seals nothing by itself, writes no file and authors no case. CASE_SET_STATUS stays
NOT_SEALED_HUMAN_GATE_OPEN until Kush and/or Parv seal a real case set and record it.

Commitment: sha256(nonce || 0x0a || canonical case lines), where the canonical lines are the cases sorted by
case_id, one compact sorted-key JSON object per line. The nonce (>= 16 random bytes, hex) is kept by the
sealing humans and disclosed only at unsealing, so the commitment does not let a rule author confirm a guessed
label. ``rules_present_at_seal`` must be false (no rule coded before the seal), and
``rules_citing_test_cases`` lists rule texts naming a TEST case id (rules may not cite test cases).
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
from typing import Any

STATUS = "DRAFT_PENDING_21b_H4"
CASE_SET_STATUS = "NOT_SEALED_HUMAN_GATE_OPEN"
MANIFEST_VERSION = "step22c-case-seal-0.1.0-draft"
HUMAN_SEALERS = ("Kush Tokas", "Parv Goyal")
SPLITS = ("DEV", "TEST")
_HEX = re.compile(r"^(?:[0-9a-f]{2}){16,}$")


class CaseSealError(ValueError):
    """The case set, nonce or manifest request does not satisfy the sealing contract."""


def canonical_case_bytes(cases: Iterable[Mapping[str, Any]]) -> bytes:
    rows = [dict(c) for c in cases]
    if not rows:
        raise CaseSealError("empty case set")
    for c in rows:
        if not isinstance(c.get("case_id"), str) or not c["case_id"].strip():
            raise CaseSealError("every case needs a non-blank case_id")
        if c.get("split") not in SPLITS:
            raise CaseSealError(f"{c['case_id']}: split must be one of {SPLITS}")
    dup = sorted(k for k, n in Counter(c["case_id"] for c in rows).items() if n > 1)
    if dup:
        raise CaseSealError(f"duplicate case_id: {dup}")
    rows.sort(key=lambda c: c["case_id"])
    return b"".join(json.dumps(c, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
                    for c in rows)


def _nonce(nonce_hex: str) -> bytes:
    if not isinstance(nonce_hex, str) or not _HEX.match(nonce_hex):
        raise CaseSealError("nonce must be lower-case hex of at least 16 bytes")
    return bytes.fromhex(nonce_hex)


def case_set_commitment(cases: Sequence[Mapping[str, Any]], *, nonce_hex: str) -> dict[str, Any]:
    body = canonical_case_bytes(cases)
    splits = Counter(c["split"] for c in cases)
    return {"algorithm": "sha256", "commitment": hashlib.sha256(_nonce(nonce_hex) + b"\n" + body).hexdigest(),
            "n_cases": len(cases), "n_by_split": {s: splits.get(s, 0) for s in SPLITS}}


def seal_manifest(cases: Sequence[Mapping[str, Any]], *, nonce_hex: str, sealed_by: Sequence[str], sealed_at: str,
                  rules_present: bool = False) -> dict[str, Any]:
    """A manifest dict for humans to record. Refuses non-human sealers and a rule set coded before the seal."""
    who = list(sealed_by)
    if not who or any(w not in HUMAN_SEALERS for w in who) or len(set(who)) != len(who):
        raise CaseSealError(f"sealed_by must name one or more of {HUMAN_SEALERS} (an AI worker never seals)")
    if rules_present:
        raise CaseSealError("a rule set exists: the case set must be sealed before any rule is coded")
    try:
        if datetime.fromisoformat(sealed_at).tzinfo is None:
            raise ValueError
    except (TypeError, ValueError) as exc:
        raise CaseSealError("sealed_at must be an ISO-8601 time with an offset") from exc
    c = case_set_commitment(cases, nonce_hex=nonce_hex)
    return {"manifest_version": MANIFEST_VERSION, "case_set_status": "SEALED_BY_HUMAN", **c, "sealed_by": who,
            "sealed_at": sealed_at, "rules_present_at_seal": False, "nonce_disclosed": False}


def verify_case_set(cases: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any], *, nonce_hex: str) -> bool:
    try:
        c = case_set_commitment(cases, nonce_hex=nonce_hex)
    except CaseSealError:
        return False
    return all(manifest.get(k) == v for k, v in c.items())


def rules_citing_test_cases(rule_texts: Mapping[str, str],
                            cases: Iterable[Mapping[str, Any]]) -> list[tuple[str, str]]:
    """(rule_key, case_id) pairs where a rule's text names a TEST case id."""
    test_ids = sorted(c["case_id"] for c in cases if c.get("split") == "TEST")
    return sorted((k, cid) for k, text in rule_texts.items() for cid in test_ids
                  if re.search(rf"(?<![\w-]){re.escape(cid)}(?![\w-])", text or ""))
