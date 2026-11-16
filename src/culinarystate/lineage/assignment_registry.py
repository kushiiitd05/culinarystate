"""T9-C09-R1: counts-only registry of the historical 15a.R reserved/dev assignment.

The reserved list is re-derived from the private seed (see ``seal_integrity``); this module only
summarises a partition of the group universe. It never returns group ids or the seed, so its output
can be committed. ``matrix_process_keys_in_both_splits`` discloses cross-source (matrix, process)
keys that fall in both splits: groups are keyed by source, so this is allowed by the 15a.R rule but
it is NOT source-independence evidence and is reported, not hidden.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

from culinarystate.lineage.reserved_seal import GroupInfo

REGISTRY_FIELDS = (
    "registry_id", "evaluation", "block_or_split", "source_family", "split_unit", "n_units", "roles",
    "ids_sha256", "unit_ids_sha256", "seed", "seed_rule", "source_artifact", "source_sha256", "code_artifact",
    "code_sha256", "snapshot_id", "status", "checks", "notes",
)


def _validated_reserved(groups: Mapping[str, GroupInfo], reserved: Iterable[str]) -> frozenset[str]:
    ids = list(reserved)
    dupes = sorted(k for k, n in Counter(ids).items() if n > 1)
    if dupes:
        raise ValueError(f"{len(dupes)} duplicate reserved id(s)")
    unknown = [gid for gid in ids if gid not in groups]
    if unknown:
        raise ValueError(f"{len(unknown)} reserved id(s) not in the group universe")
    return frozenset(ids)


def partition_summary(groups: Mapping[str, GroupInfo], *, reserved: Iterable[str]) -> dict[str, Any]:
    """Counts for the reserved/dev partition of ``groups``; no ids are returned."""
    res = _validated_reserved(groups, reserved)
    dev = frozenset(groups) - res
    strata: dict[str, dict[str, int]] = {}
    keys: dict[str, set[tuple[str, str]]] = {"RESERVED": set(), "DEV": set()}
    for gid, g in groups.items():
        side = "RESERVED" if gid in res else "DEV"
        st = strata.setdefault(g.stratum, {"n_groups": 0, "n_reserved": 0, "n_reserved_rows": 0, "n_dev_rows": 0})
        st["n_groups"] += 1
        if side == "RESERVED":
            st["n_reserved"] += 1
            st["n_reserved_rows"] += g.n_rows
        else:
            st["n_dev_rows"] += g.n_rows
        keys[side].add((g.matrix, g.process))
    n_res_rows = sum(s["n_reserved_rows"] for s in strata.values())
    n_dev_rows = sum(s["n_dev_rows"] for s in strata.values())
    return {
        "n_groups": len(groups), "n_reserved_groups": len(res), "n_dev_groups": len(groups) - len(res),
        "n_reserved_rows": n_res_rows, "n_dev_rows": n_dev_rows,
        # DEV is the complement of RESERVED (the 29-diag filter), so both counts are 0 by construction;
        # they are computed from the sets, not hard-coded, so a future non-complement DEV list is caught.
        "groups_in_both": len(res & dev),
        "groups_in_neither": len(set(groups) - (res | dev)),
        "matrix_process_keys_in_both_splits": len(keys["RESERVED"] & keys["DEV"]),
        "strata": {k: dict(v) for k, v in sorted(strata.items())},
        "contains_group_ids": False, "contains_seed": False,
    }


def registry_rows(summary: Mapping[str, Any], *, commitment: Mapping[str, Any], source_artifact: str,
                  source_sha256: str, code_artifact: str, code_sha256: str) -> list[dict[str, Any]]:
    """Two split_registry-compatible rows (RESERVED, DEV) carrying hashes and counts only."""
    snap = commitment.get("snapshot") or {}
    strata = summary["strata"]
    common = {
        "evaluation": "15A_R_RESERVED_SEAL", "source_family": "|".join(strata), "split_unit": "GROUP",
        "unit_ids_sha256": commitment.get("universe_sha256", ""), "seed": "sha256:" + str(commitment["seed_sha256"]),
        "seed_rule": f"{commitment.get('rule_id')}; group key {commitment.get('group_key_rule')}; "
                     "rank = sha256(rule||snapshot||seed||group_id) per source-family stratum",
        "source_artifact": source_artifact, "source_sha256": source_sha256, "code_artifact": code_artifact,
        "code_sha256": code_sha256, "snapshot_id": "evd:" + str(snap.get("evd_sha256", "")),
        "status": "REDERIVED_BYTE_IDENTICAL",
    }
    checks = (f"groups_in_both={summary['groups_in_both']}; groups_in_neither={summary['groups_in_neither']}; "
              f"matrix_process_keys_in_both_splits={summary['matrix_process_keys_in_both_splits']}")
    note = ("counts only; group ids and seed stay outside git; cross-source matrix/process overlap disclosed, "
            "not source independence; AI_PRECHECKED NON_CITABLE NO_HUMAN_SIGNOFF_D085")
    reserved_roles = "|".join(f"{k}={v['n_reserved']}" for k, v in strata.items())
    dev_roles = "|".join(f"{k}={v['n_groups'] - v['n_reserved']}" for k, v in strata.items())
    return [
        {**common, "registry_id": "SPL-15A-RESERVED", "block_or_split": "RESERVED",
         "n_units": summary["n_reserved_groups"], "roles": f"rows={summary['n_reserved_rows']}|{reserved_roles}",
         "ids_sha256": commitment.get("reserved_list_sha256", ""), "checks": checks, "notes": note},
        {**common, "registry_id": "SPL-15A-DEV", "block_or_split": "DEV",
         "n_units": summary["n_dev_groups"], "roles": f"rows={summary['n_dev_rows']}|{dev_roles}",
         "ids_sha256": "", "checks": checks, "notes": note + "; DEV = universe minus RESERVED (29-diag filter)"},
    ]
