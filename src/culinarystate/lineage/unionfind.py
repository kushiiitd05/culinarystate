"""Deterministic union-find over string node ids, hub rule, nesting checks.

Contract: reports/step04/lineage_contract_v1_1.md sections 4.1-4.2.
Component key = lexicographically smallest member id (order-independent).
"""
from __future__ import annotations

from typing import Iterable, Mapping, Optional, Sequence

Edge = tuple[str, str]


def _find(parent: dict[str, str], x: str) -> str:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def _union_all(nodes: Iterable[str], edges: Iterable[Edge]) -> dict[str, str]:
    """Return node -> smallest member id of its component (nodes of edges are added)."""
    parent: dict[str, str] = {}
    for n in nodes:
        parent.setdefault(n, n)
    for a, b in edges:
        parent.setdefault(a, a)
        parent.setdefault(b, b)
        ra, rb = _find(parent, a), _find(parent, b)
        if ra != rb:
            lo, hi = (ra, rb) if ra < rb else (rb, ra)
            parent[hi] = lo  # smaller id always becomes the root
    return {n: _find(parent, n) for n in sorted(parent)}


def components(
    nodes: Iterable[str],
    merge_edges: Iterable[Edge],
    hubs: Iterable[str] = (),
    primaries: Optional[Iterable[str]] = None,
) -> tuple[dict[str, str], tuple[Edge, ...]]:
    """Components under merge_edges with the hub rule (contract 4.2 step 2a).

    A hub never connects two primaries: first components are built from
    hub-free edges; then for each hub, if its edges reach primary-bearing
    components of >= 2 distinct hub-free components, every edge from the hub
    into a primary-bearing component is dropped. Edges between two hubs are
    dropped. Order-independent. Returns (node -> component key, dropped edges
    sorted, each normalised as (hub, other) hub-first when one endpoint is a hub).
    primaries=None means every non-hub node is a primary.
    """
    nodes_l = list(nodes)
    edges = [(a, b) for a, b in merge_edges]
    hub_set = frozenset(hubs)
    if not hub_set:
        return _union_all(nodes_l, edges), ()
    all_nodes = set(nodes_l) | {x for e in edges for x in e}
    prim = frozenset(all_nodes - hub_set) if primaries is None else frozenset(primaries) - hub_set

    free = [e for e in edges if e[0] not in hub_set and e[1] not in hub_set]
    base = _union_all(all_nodes, free)
    prim_comps = {base[p] for p in prim if p in base}

    hub_edges: dict[str, list[Edge]] = {}
    dropped: set[Edge] = set()
    for a, b in edges:
        ha, hb = a in hub_set, b in hub_set
        if ha and hb:
            dropped.add((min(a, b), max(a, b)))  # CONTRACT-AMBIGUITY: hub-hub edge, dropped conservatively
        elif ha or hb:
            hub, other = (a, b) if ha else (b, a)
            hub_edges.setdefault(hub, []).append((hub, other))

    kept = list(free)
    for hub, hes in hub_edges.items():
        touched = {base[o] for _, o in hes if base[o] in prim_comps}
        drop_primary = len(touched) >= 2
        for h, o in hes:
            if drop_primary and base[o] in prim_comps:
                dropped.add((h, o))
            else:
                kept.append((h, o))
    return _union_all(all_nodes, kept), tuple(sorted(dropped))


def check_nesting(
    study_of: Mapping[str, Optional[str]],
    root_of: Mapping[str, str],
    group_of: Mapping[str, str],
) -> list[str]:
    """Violations of study <= lineage_root <= split_group and of key aliasing (G08-10).

    Inputs map row id -> key. A null study (NOT_IDENTIFIABLE) is exempt from the
    study level. Empty list = OK.
    """
    out: list[str] = []
    rows = sorted(set(study_of) | set(root_of) | set(group_of))
    study_roots: dict[str, set[str]] = {}
    root_groups: dict[str, set[str]] = {}
    for r in rows:
        s, lr, g = study_of.get(r), root_of.get(r), group_of.get(r)
        if lr is None or g is None:
            out.append(f"row {r}: missing lineage_root_id or split_group_id")
            continue
        if s is not None:
            study_roots.setdefault(s, set()).add(lr)
            if s == lr or s == g:
                out.append(f"row {r}: alias study_id == {'lineage_root_id' if s == lr else 'split_group_id'} ({s})")
        if lr == g:
            out.append(f"row {r}: alias lineage_root_id == split_group_id ({lr})")
        root_groups.setdefault(lr, set()).add(g)
    # CONTRACT-AMBIGUITY: "derived by naming convention" is not machine-defined;
    # only string equality across levels is checked.
    for s, roots in sorted(study_roots.items()):
        if len(roots) > 1:
            out.append(f"study {s} spans lineage_roots {sorted(roots)}")
    for lr, groups in sorted(root_groups.items()):
        if len(groups) > 1:
            out.append(f"lineage_root {lr} spans split_groups {sorted(groups)}")
    return out


def derive_group(
    parents_groups: Mapping[str, Sequence[str]],
) -> tuple[dict[str, str], int]:
    """DRV parent union (G08-2): merge the split groups of each DRV's parents.

    parents_groups: drv_id -> split_group keys of its parents. Returns
    (group key -> merged key [smallest member], number of DRV rows whose
    parents lay in more than one group before merging).
    """
    needing = sum(1 for gs in parents_groups.values() if len(set(gs)) > 1)
    nodes = {g for gs in parents_groups.values() for g in gs}
    edges: list[Edge] = []
    for gs in parents_groups.values():
        u = sorted(set(gs))
        edges.extend((u[0], x) for x in u[1:])
    return _union_all(nodes, edges), needing
