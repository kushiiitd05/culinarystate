"""15a.R seal integrity check (S179, T2-C14-R1): read-only, counts only.

Before any 15a / 29-diag read, confirm that the sealed RESERVED list on the Mac is the one the commitment names, that
the seed is the committed seed, that the EVD snapshot has not moved, and that re-running the seal rule on that
snapshot reproduces the sealed list byte for byte. It reuses ``reserved_seal`` unchanged, writes nothing, and its
output holds no group id, no seed and no row.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from culinarystate.lineage import reserved_seal as rs


def _flag(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def check(*, root: Path, commitment: Mapping[str, Any], sealed_bytes: bytes, seed_text: str) -> dict:
    root = Path(root)
    seed = seed_text[:-1] if seed_text.endswith("\n") else seed_text
    checks: dict[str, str] = {}
    checks["sealed_list_matches_commitment"] = _flag(rs.verify_sealed_list(sealed_bytes, commitment))
    checks["seed_matches_commitment"] = _flag(
        hashlib.sha256(seed.encode("utf-8")).hexdigest() == commitment.get("seed_sha256"))
    snap = commitment.get("snapshot") or {}
    evd = root / snap.get("evd_path", rs.EVD_PATH)
    evd_sha = rs.sha256_file(evd) if evd.is_file() else None
    checks["evd_snapshot_unchanged"] = _flag(evd_sha is not None and evd_sha == snap.get("evd_sha256"))
    rederived = "FAIL"
    universe = "FAIL"
    if checks["evd_snapshot_unchanged"] == "PASS" and checks["seed_matches_commitment"] == "PASS":
        groups = rs.build_groups(rs.latest_active(rs.read_jsonl(evd)), str(commitment["unit"]))
        reserved = rs.select_reserved(groups, snapshot_sha256=evd_sha, seed=seed,
                                      fraction=Fraction(str(commitment["fraction"])),
                                      stratify=str(commitment["stratify"]))
        rederived = _flag(rs.sealed_list_bytes(reserved, groups) == sealed_bytes)
        universe = _flag(rs.universe_sha256(groups) == commitment.get("universe_sha256")
                         and len(groups) == commitment.get("n_groups"))
    checks["reserved_list_rederived_byte_identical"] = rederived
    checks["group_universe_matches_commitment"] = universe
    n_lines = sum(1 for line in sealed_bytes.decode("utf-8", "replace").splitlines() if line.strip())
    checks["reserved_count_matches_commitment"] = _flag(n_lines == commitment.get("n_reserved"))
    return {"record": "SEAL_INTEGRITY_CHECK_15A_R", "decision_id": commitment.get("decision_id"),
            "commitment_payload_sha256": commitment.get("payload_sha256"), "n_groups": commitment.get("n_groups"),
            "n_reserved": commitment.get("n_reserved"), "checks": checks,
            "verdict": "PASS" if all(v == "PASS" for v in checks.values()) else "FAIL",
            "contains_group_ids": False, "contains_seed": False}
