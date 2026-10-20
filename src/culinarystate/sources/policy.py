"""Source ingest policy (S116): which registry rows may enter canonical (persistent, releasable) ledgers or datasets."""
from __future__ import annotations

BLOCKING_STATUS = ("LIVE_ONLY", "DO_NOT_STORE", "DO_NOT_USE", "LICENCE_BLOCKED")
BLOCKING_FLAGS = {"NO", "PERMISSION_REQUIRED", "RESEARCH_ONLY", "LICENCE_REQUIRED"}


def can_ingest_canonical(row: dict) -> tuple[bool, str]:
    """Return (allowed, reason). A row is allowed only when nothing in the registry blocks persistence/redistribution."""
    status = (row.get("status") or "").upper()
    if any(tag in status for tag in BLOCKING_STATUS):
        return False, f"status {row.get('status')!r} forbids persistence"
    roles = (row.get("roles") or "").upper()
    if "LIVE_ONLY" in roles or "DO_NOT_USE" in roles:
        return False, "role LIVE_ONLY/DO_NOT_USE"
    for col in ("redistribution", "bulk_training_allowed"):
        v = (row.get(col) or "UNVERIFIED").split()[0].upper().strip("_")
        if v in BLOCKING_FLAGS:
            return False, f"{col}={row.get(col)}"
        if v.startswith("UNVERIFIED") or v == "UNKNOWN":
            return False, f"{col} unresolved: resolve licence before ingest"
    lic = (row.get("licence") or "").upper()
    if not lic or "UNVERIFIED" in lic and "CC0" not in lic:
        return False, "licence unresolved"
    return True, "ok"
