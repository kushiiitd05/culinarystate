"""Human-signed ingredient-link decisions for MEDIUM/NONE-band EVD matrices (RUNBOOK §4; AI review ≠ human sign-off).

A review row becomes a decision only when human_decision is filled, the reviewer is a named human (Kush, Parv) and
the date is ISO. ACCEPT / CORRECT -> LINK to the recommended concept (canonical name or English alias); HOLD_* and
UNRESOLVED -> NO_LINK (category, multi-matrix or composite rows must not pretend to be one ingredient). A LINK whose
concept is not in the ING registry is CONCEPT_MISSING: recorded, never linked, never minted here.
"""
from __future__ import annotations

import re

from culinarystate.ledgers.common import HUMANS
from culinarystate.vocab.foodon import norm

VERSION = "link_review@0.1"
LINK = {"ACCEPT", "CORRECT"}
NO_LINK = {"HOLD_CATEGORY_SCOPE", "HOLD_MULTI_MATRIX", "HOLD_COMPOSITE_DISH", "UNRESOLVED", "REJECT"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def decide(row: dict, names: dict) -> dict:
    """row: one review CSV record; names: normalised ING name/alias -> ING id. Returns a decision record."""
    hd = str(row.get("human_decision") or "").strip().upper()
    who, when = str(row.get("human_reviewer") or "").strip(), str(row.get("human_review_date") or "").strip()
    base = {"version": VERSION, "matrix_raw": row["matrix_raw"], "source_family": row["source_family"],
            "human_decision": hd, "reviewer": who, "review_date": when, "concept": None, "ingredient_id": None}
    if not hd:
        return {**base, "status": "UNSIGNED"}
    if who not in HUMANS or not DATE.match(when):
        return {**base, "status": "INVALID_SIGNOFF"}
    if hd in NO_LINK:
        return {**base, "status": "HELD"}
    if hd not in LINK:
        return {**base, "status": "INVALID_DECISION"}
    concept = str(row.get("ai_recommended_link") or row.get("suggested") or "").strip()
    ing = names.get(norm(concept)) if concept else None
    return {**base, "concept": concept or None, "ingredient_id": ing, "status": "LINKED" if ing else "CONCEPT_MISSING"}
