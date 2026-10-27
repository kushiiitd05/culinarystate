"""08a.5: study_id / lineage_root_id / split_group_id and independence_resolution per ACTIVE EVD row.

Contract: reports/step04/lineage_contract_v1_1.md 3.1, 4.1-4.4. Thresholds: THR-08A-01, 02, 10, 12, 14, 21, 22.
Pure functions, no I/O, no mutation of inputs. Ids are scratch ordinals over sorted component keys.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Iterable, Mapping, Optional, Sequence

from .unionfind import _union_all, check_nesting, components, derive_group

RULE_VERSION = "keys-v1"
SAME_LAB_WINDOW_YEARS = 3  # THR-08A-22
MERGING_TYPES = frozenset({"SAME_STUDY_AS", "QUOTES_VALUES_FROM", "ALTERNATE_OF", "REVISION_OF", "SHARES_SAMPLES_WITH"})
GROUPING_DEFAULT_TYPES = frozenset({"SHARES_REFERENCE_SAMPLE"})
HUB_SRC_KINDS = frozenset({"DATABASE", "REVIEW"})
HUB_REPORT_KINDS = frozenset({"COMPILATION_DATABASE", "REVIEW", "SECONDARY_COPY"})
READ_AUTHORSHIP = frozenset({"READ_FROM_DOCUMENT", "FROM_METADATA_RECORD"})
LEVEL_SETS: dict[str, Optional[frozenset]] = {
    "NONE": frozenset(),
    "STRONG+B1": frozenset({"STRONG", "B1"}),
    "STRONG+B1+B2": frozenset({"STRONG", "B1", "B2"}),
    "ALL": None,
}
_KEY_FIELDS = ("study_id_status", "independence_resolution", "lineage_root_id", "split_group_id")


def _is_hub_doc(d: Mapping) -> bool:
    return d.get("is_compilation_hub") == "YES" or d.get("report_kind") in HUB_REPORT_KINDS


def study_locator_docs(study_id: str, studies: Mapping, docs: Mapping) -> list[str]:
    """DOC ids that are a valid locator for a study: listed in report_doc_ids, present, non-hub."""
    s = studies.get(study_id)
    if not s:
        return []
    return sorted(d for d in s.get("report_doc_ids") or [] if d in docs and not _is_hub_doc(docs[d]))


def same_lab(a: Mapping, b: Mapping, window: int = SAME_LAB_WINDOW_YEARS) -> Optional[bool]:
    """SAME_LAB_AS (THR-08A-22): shared corresponding author OR same affiliation within +-window years.

    None = cannot be assessed (authorship unread, or year unknown for the affiliation test). Never guessed.
    """
    A, B = a.get("authorship") or {}, b.get("authorship") or {}
    if A.get("status") not in READ_AUTHORSHIP or B.get("status") not in READ_AUTHORSHIP:
        return None
    norm = lambda x: (x or "").strip().casefold()
    ca, cb = norm(A.get("corresponding_author_raw")), norm(B.get("corresponding_author_raw"))
    if ca and ca == cb:
        return True
    shared = {norm(x) for x in A.get("affiliations_raw") or []} & {norm(x) for x in B.get("affiliations_raw") or []}
    shared.discard("")
    if not shared:
        return False
    ya, yb = A.get("year_published"), B.get("year_published")
    if ya is None or yb is None:
        return None
    return abs(int(ya) - int(yb)) <= window


def _row_unit(r: Mapping, studies, docs, srcs, hub_nodes: set) -> dict[str, Any]:
    """Grouping node, reported study_id/status and independence for one row."""
    ids = sorted(set(r.get("study_ids") or []))
    status = r.get("study_id_status")
    if ids and status == "PRESENT":
        ok = bool(study_locator_docs(ids[0], studies, docs))
        return {"node": ids[0], "extra": ids[1:], "study_id": ids[0] if ok else None,
                "study_id_status": "PRESENT" if ok else "NOT_IDENTIFIABLE",
                "withheld": None if ok else "NO_DOC_LOCATOR", "family": False}
    fam = r.get("source_family_id") or r.get("source_id")
    if status == "NOT_IDENTIFIABLE" and fam:
        node = "FAMILY:" + fam
        if (srcs.get(r.get("source_id")) or {}).get("kind") in HUB_SRC_KINDS:
            hub_nodes.add(node)
        return {"node": node, "extra": [], "study_id": None, "study_id_status": "NOT_IDENTIFIABLE",
                "withheld": None, "family": True}
    return {"node": "ROW:" + r["id"], "extra": [], "study_id": None,
            "study_id_status": status if status in ("NOT_IDENTIFIABLE", "NOT_APPLICABLE") else "NOT_IDENTIFIABLE",
            "withheld": None, "family": False}


def _resolution(u: Mapping, confirmed: frozenset) -> str:
    if u["study_id"] is not None:
        # CONTRACT-AMBIGUITY: STUDY needs confirmed experiment boundaries (D-10); nothing in the ledgers states that,
        # so PUBLICATION_ONLY unless the caller names the study as confirmed.
        return "STUDY" if u["study_id"] in confirmed else "PUBLICATION_ONLY"
    return "SOURCE_FAMILY_ONLY" if u["family"] else "UNKNOWN"


def _edge_class(e: Mapping) -> Optional[str]:
    t, st = e.get("edge_type"), e.get("edge_status")
    if st == "REJECTED":
        return None
    if t in MERGING_TYPES:
        return "MERGE"
    if t == "PRIMARY_SOURCE":
        return "MERGE" if e.get("membership_status") == "KNOWN" else "GROUP"
    if t in GROUPING_DEFAULT_TYPES:
        return "GROUP"
    return None


def _norm_hub(a: str, b: str, hubs: set) -> tuple[str, str]:
    ha, hb = a in hubs, b in hubs
    if ha and hb:
        return (min(a, b), max(a, b))
    return (a, b) if ha or not hb else (b, a)


def assign_keys(rows: Sequence[Mapping], studies: Mapping, docs: Mapping, srcs: Mapping,
                edges: Iterable[Mapping], *, levels: Optional[frozenset] = None,
                study_level_confirmed: frozenset = frozenset()) -> dict[str, Any]:
    rows = sorted(rows, key=lambda r: r["id"])
    hubs: set[str] = set()
    unit = {r["id"]: _row_unit(r, studies, docs, srcs, hubs) for r in rows}
    nodes: set[str] = set()
    struct: list[tuple[str, str]] = []
    study_nodes: set[str] = set()
    for u in unit.values():
        nodes.add(u["node"])
        if u["node"].startswith("STUDY-"):
            study_nodes.add(u["node"])
        for x in u["extra"]:  # CONTRACT-AMBIGUITY: a row naming several studies joins them (conservative)
            struct.append((u["node"], x))
            study_nodes.add(x)
    for s in sorted(study_nodes):
        for d in study_locator_docs(s, studies, docs):  # STUDY - report DOC, primary manifestations only
            struct.append((s, d))
            nodes.add(d)
    merge_e, group_e, kept_info = [], [], []
    unmatched = 0
    for e in edges:
        c = _edge_class(e)
        if c is None or (levels is not None and e.get("detector_level") not in levels):
            continue
        a, b = unit.get(e["from_id"]), unit.get(e["to_id"])
        if a is None or b is None:
            unmatched += 1
            continue
        pair = (a["node"], b["node"])
        (merge_e if c == "MERGE" else group_e).append((pair, e))
    free_pairs = [p for p, _ in merge_e if p[0] != p[1]]
    comp, dropped = components(nodes, struct + free_pairs, hubs=hubs, primaries=study_nodes)
    dropped_set = set(dropped)
    dropped_edges = [e for p, e in merge_e if p[0] != p[1] and _norm_hub(p[0], p[1], hubs) in dropped_set]
    kept_edges = [(p, e) for p, e in merge_e if not (p[0] != p[1] and _norm_hub(p[0], p[1], hubs) in dropped_set)]
    # CONTRACT-AMBIGUITY: GROUPING_DEFAULT edges are unioned at split level without the hub filter
    # (none exist in the 08a.3 output; the contract gives no hub treatment for them).
    root_of_node = {n: comp[n] for n in nodes}
    drv = {r["id"]: list(r["parent_ids"]) for r in rows if r.get("parent_ids")}
    split_edges = [(root_of_node[p[0]], root_of_node[p[1]]) for p, _ in group_e if p[0] != p[1]]
    root_keys = sorted(set(root_of_node.values()))
    split_of_root = _union_all(root_keys, split_edges)
    row_root = {r["id"]: root_of_node[unit[r["id"]]["node"]] for r in rows}
    before = after = 0
    if drv:
        pg = {d: sorted({split_of_root[row_root[p]] for p in ps if p in row_root}) for d, ps in drv.items()}
        before = sum(1 for gs in pg.values() if len(gs) > 1)
        merged, _ = derive_group({d: gs + [split_of_root[row_root[d]]] for d, gs in pg.items()})
        split_of_root = {k: merged.get(v, v) for k, v in split_of_root.items()}
        after = sum(1 for d, ps in drv.items()
                    if len({split_of_root[row_root[x]] for x in ps if x in row_root} | {split_of_root[row_root[d]]}) > 1)
    root_id = {k: f"LROOT-{i:06d}" for i, k in enumerate(root_keys, 1)}
    split_keys = sorted(set(split_of_root.values()))
    split_id = {k: f"SPLITGRP-EVD-{i:06d}" for i, k in enumerate(split_keys, 1)}
    prov_by_root = Counter(root_of_node[p[0]] for p, e in kept_edges if e.get("edge_status") == "PROVISIONAL")
    records = []
    for r in rows:
        u, rk = unit[r["id"]], row_root[r["id"]]
        read = any((docs[d].get("authorship") or {}).get("status") in READ_AUTHORSHIP
                   for d in study_locator_docs(u["node"], studies, docs)) if u["node"].startswith("STUDY-") else False
        sg = split_id[split_of_root[rk]]
        records.append({
            "rule_version": RULE_VERSION, "evd_id": r["id"], "study_id": u["study_id"],
            "study_id_status": u["study_id_status"], "study_id_withheld_reason": u["withheld"],
            "lineage_root_id": root_id[rk], "split_group_id": sg,
            "independence_resolution": _resolution(u, study_level_confirmed),
            "source_family_id": r.get("source_family_id"), "is_compilation_hub": u["node"] in hubs,
            "provisional_edges_in_component": prov_by_root.get(rk, 0),
            "parent_union_split_group_ids": sorted({split_id[split_of_root[row_root[p]]] for p in drv.get(r["id"], []) if p in row_root} | ({sg} if r["id"] in drv else set())),
            "lab_group_id": None, "lab_group_status": "NOT_COMPUTED" if read else "UNKNOWN",
            "assignment_status": "SCRATCH_PROVISIONAL",
        })
    sizes = Counter(rec["split_group_id"] for rec in records)
    top = sizes.most_common(1)[0][1] if sizes else 0
    stats = {
        "rows": len(records), "edges_dropped_by_hub_rule": len(dropped_edges),
        "edges_dropped_by_hub_rule_by_level": dict(sorted(Counter(e.get("detector_level") for e in dropped_edges).items())),
        "hub_node_pairs_dropped": len(dropped), "edges_kept_merging": len(kept_edges),
        "edges_grouping_default": len(group_e), "edges_unmatched_endpoint": unmatched,
        "drv_rows": len(drv), "drv_parents_in_different_groups_before_union": before,
        "drv_parents_in_different_groups_after_union": after,
        "study_ids_withheld_no_locator": sum(1 for u in unit.values() if u["withheld"]),
        "lineage_roots": len({x["lineage_root_id"] for x in records}),
        "split_groups": len(sizes), "largest_group_rows": top,
        "largest_group_share": (top / len(records)) if records else 0.0,
    }
    return {"records": records, "stats": stats}


def level_sensitivity(rows, studies, docs, srcs, edges, **kw) -> dict[str, dict]:
    """Largest-split-group share when only STRONG+B1, STRONG+B1+B2, or all edge levels merge (B3 effect)."""
    edges = list(edges)
    out = {}
    for name, lv in LEVEL_SETS.items():
        s = assign_keys(rows, studies, docs, srcs, edges, levels=lv, **kw)["stats"]
        out[name] = {k: s[k] for k in ("largest_group_rows", "largest_group_share", "lineage_roots", "split_groups",
                                       "edges_kept_merging", "edges_dropped_by_hub_rule")}
    return out


def check_gates(records: Sequence[Mapping], expected_rows: int, studies: Mapping, docs: Mapping) -> dict[str, dict]:
    covered = sum(1 for r in records if all(r.get(k) is not None for k in _KEY_FIELDS))
    g1 = {"pass": covered == expected_rows == len(records), "covered": covered, "expected": expected_rows}
    fab = [r["evd_id"] for r in records
           if r.get("study_id") is not None and not study_locator_docs(r["study_id"], studies, docs)]
    g8 = {"pass": not fab, "fabricated": len(fab), "checked": sum(1 for r in records if r.get("study_id") is not None)}
    viol = check_nesting({r["evd_id"]: r.get("study_id") for r in records},
                         {r["evd_id"]: r.get("lineage_root_id") for r in records},
                         {r["evd_id"]: r.get("split_group_id") for r in records})
    g10 = {"pass": not viol, "violations": len(viol), "examples": viol[:5]}
    return {"G08-1": g1, "G08-8": g8, "G08-10": g10}


def check_drv_gate(records: Sequence[Mapping], drv_parents: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    """G08-2 (THR-08A-02): DRV rows whose parents (or the DRV itself) sit in more than one split group."""
    grp = {r["evd_id"]: r["split_group_id"] for r in records}
    bad = [d for d, ps in sorted(drv_parents.items())
           if len({grp[p] for p in ps if p in grp} | ({grp[d]} if d in grp else set())) > 1]
    return {"pass": not bad, "violations": len(bad), "drv_rows": len(drv_parents)}


def content_key(member_ids: Iterable[str]) -> str:
    """sha256 over sorted member ids (contract 4.3 content key); stored for the future idempotent minter."""
    return hashlib.sha256("\n".join(sorted(member_ids)).encode()).hexdigest()
