import random

from culinarystate.lineage.unionfind import check_nesting, components, derive_group

NODES = ["d", "a", "c", "b", "e", "f"]
EDGES = [("a", "b"), ("c", "b"), ("e", "f")]


def test_components_min_member_key():
    comp, dropped = components(NODES, EDGES)
    assert comp == {"a": "a", "b": "a", "c": "a", "d": "d", "e": "e", "f": "e"}
    assert dropped == ()


def test_order_independence_shuffle_50():
    ref, _ = components(NODES, EDGES)
    rng = random.Random(0)
    for _ in range(50):
        n, e = list(NODES), [tuple(x) if rng.random() < .5 else (x[1], x[0]) for x in EDGES]
        rng.shuffle(n)
        rng.shuffle(e)
        got, _ = components(n, e)
        assert got == ref


def test_unknown_edge_node_is_error_free_and_added():
    comp, _ = components(["a"], [("a", "z")])
    assert comp == {"a": "a", "z": "a"}


def test_hub_never_links_two_primaries():
    nodes = ["p1", "p2", "p3", "hub", "agg"]
    edges = [("p1", "hub"), ("hub", "p2"), ("p3", "agg"), ("agg", "hub")]
    for _ in range(20):
        random.shuffle(edges)
        comp, dropped = components(nodes, edges, hubs={"hub"}, primaries={"p1", "p2", "p3"})
        assert len({comp["p1"], comp["p2"], comp["p3"]}) == 3
        assert comp["hub"] != comp["p1"] or comp["hub"] != comp["p2"]
        assert ("hub", "p1") in dropped and ("hub", "p2") in dropped


def test_hub_with_single_primary_is_kept():
    comp, dropped = components(["p1", "hub"], [("p1", "hub")], hubs={"hub"}, primaries={"p1"})
    assert comp["hub"] == comp["p1"] and dropped == ()


def test_hub_dropped_report_is_deterministic():
    nodes = ["p1", "p2", "hub"]
    a = components(nodes, [("p1", "hub"), ("p2", "hub")], hubs={"hub"}, primaries={"p1", "p2"})[1]
    b = components(nodes[::-1], [("hub", "p2"), ("hub", "p1")], hubs={"hub"}, primaries={"p1", "p2"})[1]
    assert a == b


def test_nesting_ok():
    assert check_nesting({"r1": "STUDY-1", "r2": "STUDY-1"}, {"r1": "LROOT-1", "r2": "LROOT-1"},
                         {"r1": "SPLITGRP-EVD-1", "r2": "SPLITGRP-EVD-1"}) == []


def test_nesting_study_in_two_roots():
    v = check_nesting({"r1": "S1", "r2": "S1"}, {"r1": "L1", "r2": "L2"}, {"r1": "G1", "r2": "G1"})
    assert any("study" in x and "S1" in x for x in v)


def test_nesting_root_in_two_groups():
    v = check_nesting({"r1": "S1", "r2": "S2"}, {"r1": "L1", "r2": "L1"}, {"r1": "G1", "r2": "G2"})
    assert any("lineage_root" in x and "L1" in x for x in v)


def test_aliasing_detected():
    v = check_nesting({"r1": "X"}, {"r1": "X"}, {"r1": "G"})
    assert any("alias" in x for x in v)
    v = check_nesting({"r1": "S"}, {"r1": "L"}, {"r1": "L"})
    assert any("alias" in x for x in v)


def test_null_study_allowed_missing_root_flagged():
    assert check_nesting({"r1": None}, {"r1": "L"}, {"r1": "G"}) == []
    assert check_nesting({"r1": "S"}, {}, {"r1": "G"}) != []


def test_derive_group_merges_parents():
    mapping, n = derive_group({"drv1": ["G2", "G1"], "drv2": ["G3"], "drv3": ["G1", "G1"]})
    assert n == 1
    assert mapping["G1"] == mapping["G2"] == "G1"
    assert mapping["G3"] == "G3"


def test_derive_group_chain_and_order_independence():
    pg = {"d1": ["G1", "G2"], "d2": ["G2", "G3"], "d3": ["G9"]}
    ref = derive_group(pg)
    items = list(pg.items())
    for _ in range(20):
        random.shuffle(items)
        assert derive_group({k: list(reversed(v)) for k, v in items}) == ref
    assert ref[1] == 2 and ref[0]["G3"] == "G1"
