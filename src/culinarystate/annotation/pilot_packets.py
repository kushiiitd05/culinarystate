"""Step 19 blank annotation packets for one annotator (DRAFT_PENDING_H4; engineering only).

Builds the design's section 5.2 packets: one blank gold-1.0 template per recipe with a packet id of
``DGP-<letter>-nnnn`` (A = Kush, B = Parv), a per-annotator order seeded by the draw seed, and a
packet-id -> recipe-id key that the caller keeps outside git. Packet files carry the recipe text and the
packet id only (never the recipe id, no AI label, no model output). Text-free manifest rows are for git.
Only one letter is built per call: the two annotators' files must not share a filesystem.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

STATUS = "DRAFT_PENDING_H4"
ANNOTATOR = {"A": "Kush", "B": "Parv"}
LOCALE = {"FOODCOM": "US", "A1_BBC_GOOD_FOOD": "UK", "WIKIBOOKS": "US"}


class PacketError(ValueError):
    pass


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
                  seed_hex: str) -> tuple[list[dict], dict[str, str]]:
    """(packets, key): packets in issue order; key maps packet id -> recipe id (keep outside git)."""
    if letter not in ANNOTATOR:
        raise PacketError(f"letter must be one of {tuple(ANNOTATOR)}")
    if not isinstance(seed_hex, str) or not seed_hex:
        raise PacketError("seed is required")
    ordered = sorted(set(recipe_ids), key=lambda rid: (_sha(seed_hex, letter, rid), rid))
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
