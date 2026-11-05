"""Step 19 blank annotation packets for one annotator (DRAFT_PENDING_H4; engineering only).

Builds the design's section 5.2 packets: one blank gold-1.0 template per recipe with a packet id of
``DGP-<letter>-nnnn`` (A = Kush, B = Parv), a per-annotator order seeded by the draw seed, and a
packet-id -> recipe-id key that the caller keeps outside git. Packet files carry the recipe text and the
packet id only (never the recipe id, no AI label, no model output). Text-free manifest rows are for git.
Only one letter is built per call: the two annotators' files must not share a filesystem.

S164 (review block J7): the order also uses a secret per-annotator salt (kept outside git; only its sha256 is
tracked), because seed and recipe ids are public and the key could otherwise be rebuilt from tracked files.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

STATUS = "DRAFT_PENDING_H4"
ANNOTATOR = {"A": "Kush", "B": "Parv"}
LOCALE = {"FOODCOM": "US", "A1_BBC_GOOD_FOOD": "UK", "WIKIBOOKS": "US"}


SALT_RE = re.compile(r"[0-9a-f]{64,}")  # generate with secrets.token_hex(32)
SALT_MIN_DISTINCT = 8


def salt_ok(salt_hex: object) -> bool:
    return isinstance(salt_hex, str) and bool(SALT_RE.fullmatch(salt_hex)) and len(set(salt_hex)) >= SALT_MIN_DISTINCT


class PacketError(ValueError):
    pass


def salt_commitment(salt_hex: str) -> str:
    return hashlib.sha256(salt_hex.encode("utf-8")).hexdigest()


def read_salt(path: Path, *, repo_root: Path) -> str:
    """Salt from a private (mode 0600) file outside the repository (one trailing newline removed).

    Symlinks are resolved and paths compared case-insensitively (macOS volumes are usually case-insensitive).
    """
    real, repo = os.path.realpath(path).casefold(), os.path.realpath(repo_root).casefold()
    if real == repo or real.startswith(repo.rstrip(os.sep) + os.sep):
        raise PacketError("the salt file must live outside the repository")
    if os.stat(path).st_mode & 0o077:
        raise PacketError("the salt file must be private (chmod 0600)")
    text = Path(path).read_text(encoding="utf-8")
    salt = text[:-1] if text.endswith("\n") else text
    if not salt_ok(salt):
        raise PacketError("salt must be at least 64 lower-case hex characters with >= 8 distinct digits")
    return salt


def independence_problems(local_root: Path, letter: str) -> list[str]:
    """The other annotator's packets or key must not exist on this filesystem."""
    out = []
    for other in sorted(set(ANNOTATOR) - {letter}):
        if (Path(local_root) / other).exists():
            out.append(f"OTHER_ANNOTATOR_FOLDER_PRESENT: {other}")
        if any(Path(local_root).glob(f"sealed_key_*_{other}.json")):
            out.append(f"OTHER_ANNOTATOR_KEY_PRESENT: {other}")
    return out


def _sha(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def content_hash(rec: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps([list(rec["ingredient_lines"]), list(rec["steps"])], ensure_ascii=False,
                                     sort_keys=True).encode("utf-8")).hexdigest()


def is_pristine(doc: Mapping[str, Any]) -> bool:
    return (not any(l["spans"] or l["entity"] != "TODO" or l["concept"] != "TODO" for l in doc["ingredient_lines"])
            and not any(s["spans"] or s["events"] or s.get("coref") for s in doc["steps"])
            and not doc["unknowns"] and not doc.get("notes"))


def build_packets(recipe_ids: Sequence[str], records: Mapping[str, Mapping[str, Any]], *, letter: str,
                  seed_hex: str, salt_hex: str) -> tuple[list[dict], dict[str, str]]:
    """(packets, key): packets in issue order; key maps packet id -> recipe id (keep outside git)."""
    if letter not in ANNOTATOR:
        raise PacketError(f"letter must be one of {tuple(ANNOTATOR)}")
    if not isinstance(seed_hex, str) or not seed_hex:
        raise PacketError("seed is required")
    if not salt_ok(salt_hex):
        raise PacketError("salt must be at least 64 lower-case hex characters with >= 8 distinct digits")
    ordered = sorted(set(recipe_ids), key=lambda rid: (_sha(seed_hex, letter, salt_hex, rid), rid))
    packets, key = [], {}
    for n, rid in enumerate(ordered, 1):
        rec = records.get(rid)
        if not rec or not (rec.get("ingredient_lines") or rec.get("steps")):
            raise PacketError("a packet recipe has no text")
        pid = f"DGP-{letter}-{n:04d}"
        doc = {"schema_version": "gold-1.0", "recipe_id": pid,
               "source_ref": f"{pid}; annotation_status=DRAFT_HUMAN_INDEPENDENT; ai_prefill=NONE",
               "annotator": ANNOTATOR[letter], "status": "DRAFT", "locale": LOCALE.get(rec.get("source_family"), "US"),
               "ingredient_lines": [{"line_index": i, "text": t, "spans": [], "entity": "TODO", "concept": "TODO"}
                                    for i, t in enumerate(rec["ingredient_lines"])],
               "steps": [{"step_index": i, "text": t, "spans": [], "events": [], "coref": []}
                         for i, t in enumerate(rec["steps"])],
               "unknowns": [], "notes": ""}
        packets.append({"packet_id": pid, "doc": doc, "content_sha256": content_hash(rec)})
        key[pid] = rid
    return packets, key


def manifest_rows(packets: Sequence[Mapping[str, Any]]) -> list[dict]:
    """Text-free rows for the tracked manifest (no recipe id, no text)."""
    return [{"packet_id": p["packet_id"],
             "file_sha256": hashlib.sha256((json.dumps(p["doc"], indent=2, ensure_ascii=False) + "\n").encode()).hexdigest(),
             "content_sha256": p["content_sha256"], "n_ingredient_lines": len(p["doc"]["ingredient_lines"]),
             "n_steps": len(p["doc"]["steps"]), "ai_prefill": "NONE", "model_outputs_embedded": "NONE",
             "status": STATUS} for p in packets]
