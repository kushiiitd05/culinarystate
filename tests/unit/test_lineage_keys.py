"""08a.5: three keys + independence registry (synthetic data only; real ledgers are never read)."""
import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.lineage import keys

REPO = Path(__file__).resolve().parents[2]


def row(i, study=None, src="SRC-A", fam="FAM-A", **kw):
    r = {"id": f"EVD-{i:06d}", "study_ids": [study] if study else [],
         "study_id_status": "PRESENT" if study else "NOT_IDENTIFIABLE",
         "source_id": src, "source_family_id": fam}
    r.update(kw)
    return r


def edge(a, b, level="B3", etype="QUOTES_VALUES_FROM", status="PROVISIONAL"):
    return {"edge_type": etype, "from_id": f"EVD-{a:06d}", "to_id": f"EVD-{b:06d}",
            "detector_level": level, "edge_status": status}


STUDIES = {f"STUDY-{n:06d}": {"id": f"STUDY-{n:06d}", "report_doc_ids": [f"DOC-{n:06d}"]} for n in (1, 2, 3)}
STUDIES["STUDY-000009"] = {"id": "STUDY-000009", "report_doc_ids": []}
DOCS = {f"DOC-{n:06d}": {"id": f"DOC-{n:06d}", "src_id": f"SRC-P{n}", "is_compilation_hub": "NO",
                         "report_kind": "OTHER", "authorship": {"status": "UNKNOWN"}} for n in (1, 2, 3)}
SRCS = {"SRC-A": {"id": "SRC-A", "kind": "DATABASE"}, "SRC-B": {"id": "SRC-B", "kind": "DATABASE"},
        "SRC-P1": {"id": "SRC-P1", "kind": "PAPER"}}


def run(rows, edges=(), **kw):
    return keys.assign_keys(rows, STUDIES, DOCS, SRCS, list(edges), **kw)


def by_id(res):
    return {r["evd_id"]: r for r in res["records"]}


def test_same_study_same_root_and_different_studies_apart():
    res = by_id(run([row(1, "STUDY-000001"), row(2, "STUDY-000001"), row(3, "STUDY-000002")]))
    assert res["EVD-000001"]["lineage_root_id"] == res["EVD-000002"]["lineage_root_id"]
    assert res["EVD-000001"]["lineage_root_id"] != res["EVD-000003"]["lineage_root_id"]
    assert res["EVD-000001"]["split_group_id"] != res["EVD-000003"]["split_group_id"]


def test_prefixes_and_no_alias():
    res = by_id(run([row(1, "STUDY-000001")]))["EVD-000001"]
    assert res["lineage_root_id"].startswith("LROOT-")
    assert res["split_group_id"].startswith("SPLITGRP-EVD-")
    assert len({res["study_id"], res["lineage_root_id"], res["split_group_id"]}) == 3


def test_not_identifiable_family_is_one_root_source_family_only():
    res = by_id(run([row(1), row(2), row(3, src="SRC-B", fam="FAM-B")]))
    assert res["EVD-000001"]["lineage_root_id"] == res["EVD-000002"]["lineage_root_id"]
    assert res["EVD-000001"]["lineage_root_id"] != res["EVD-000003"]["lineage_root_id"]
    r = res["EVD-000001"]
    assert r["study_id"] is None and r["study_id_status"] == "NOT_IDENTIFIABLE"
    assert r["independence_resolution"] == "SOURCE_FAMILY_ONLY" and r["is_compilation_hub"] is True


def test_provisional_edge_merges_rejected_does_not():
    rows = [row(1, "STUDY-000001"), row(2, "STUDY-000002")]
    merged = by_id(run(rows, [edge(1, 2)]))
    assert merged["EVD-000001"]["lineage_root_id"] == merged["EVD-000002"]["lineage_root_id"]
    assert merged["EVD-000001"]["provisional_edges_in_component"] == 1
    apart = by_id(run(rows, [edge(1, 2, status="REJECTED")]))
    assert apart["EVD-000001"]["lineage_root_id"] != apart["EVD-000002"]["lineage_root_id"]


def test_non_merging_and_unknown_membership_edges_do_not_merge_roots():
    rows = [row(1, "STUDY-000001"), row(2, "STUDY-000002")]
    res = by_id(run(rows, [edge(1, 2, etype="CITES"), edge(1, 2, etype="PRIMARY_SOURCE")]))
    assert res["EVD-000001"]["lineage_root_id"] != res["EVD-000002"]["lineage_root_id"]


def test_grouping_default_edge_merges_split_not_root():
    rows = [row(1, "STUDY-000001"), row(2, "STUDY-000002")]
    res = by_id(run(rows, [edge(1, 2, etype="SHARES_REFERENCE_SAMPLE")]))
    assert res["EVD-000001"]["lineage_root_id"] != res["EVD-000002"]["lineage_root_id"]
    assert res["EVD-000001"]["split_group_id"] == res["EVD-000002"]["split_group_id"]


def test_hub_hub_edge_dropped_and_counted():
    out = run([row(1), row(2, src="SRC-B", fam="FAM-B")], [edge(1, 2), edge(1, 2, level="B2")])
    r = by_id(out)
    assert r["EVD-000001"]["split_group_id"] != r["EVD-000002"]["split_group_id"]
    assert out["stats"]["edges_dropped_by_hub_rule"] == 2


def test_hub_never_joins_two_studies():
    rows = [row(1), row(2, "STUDY-000001"), row(3, "STUDY-000002")]
    out = run(rows, [edge(1, 2), edge(1, 3)])
    r = by_id(out)
    assert r["EVD-000002"]["lineage_root_id"] != r["EVD-000003"]["lineage_root_id"]
    assert r["EVD-000001"]["lineage_root_id"] not in (r["EVD-000002"]["lineage_root_id"], r["EVD-000003"]["lineage_root_id"])
    assert out["stats"]["edges_dropped_by_hub_rule"] == 2


def test_hub_with_single_study_link_is_kept():
    r = by_id(run([row(1), row(2, "STUDY-000001")], [edge(1, 2)]))
    assert r["EVD-000001"]["lineage_root_id"] == r["EVD-000002"]["lineage_root_id"]


def test_edge_order_independence():
    rows = [row(1), row(2, "STUDY-000001"), row(3, "STUDY-000002"), row(4, "STUDY-000003")]
    es = [edge(2, 3), edge(3, 4), edge(1, 2)]
    a = run(rows, es)["records"]
    b = run(list(reversed(rows)), list(reversed(es)))["records"]
    assert a == b


def test_study_without_doc_locator_is_withheld_not_fabricated():
    r = by_id(run([row(1, "STUDY-000009")]))["EVD-000001"]
    assert r["study_id"] is None and r["study_id_status"] == "NOT_IDENTIFIABLE"
    assert r["independence_resolution"] == "UNKNOWN" and r["study_id_withheld_reason"] == "NO_DOC_LOCATOR"


def test_study_pointing_at_hub_doc_has_no_locator():
    docs = {**DOCS, "DOC-000001": {**DOCS["DOC-000001"], "is_compilation_hub": "YES"}}
    out = keys.assign_keys([row(1, "STUDY-000001")], STUDIES, docs, SRCS, [])
    assert out["records"][0]["study_id"] is None


def test_publication_only_by_default_study_only_when_confirmed():
    rows = [row(1, "STUDY-000001")]
    assert by_id(run(rows))["EVD-000001"]["independence_resolution"] == "PUBLICATION_ONLY"
    conf = by_id(run(rows, study_level_confirmed=frozenset({"STUDY-000001"})))
    assert conf["EVD-000001"]["independence_resolution"] == "STUDY"


def test_gates_pass_on_clean_data():
    out = run([row(1), row(2, "STUDY-000001"), row(3, "STUDY-000002")], [edge(2, 3)])
    g = keys.check_gates(out["records"], 3, STUDIES, DOCS)
    assert g["G08-1"]["pass"] and g["G08-1"]["covered"] == 3
    assert g["G08-8"]["pass"] and g["G08-8"]["fabricated"] == 0
    assert g["G08-10"]["pass"] and g["G08-10"]["violations"] == 0


def test_gates_fail_on_bad_records():
    out = run([row(1, "STUDY-000001"), row(2, "STUDY-000002")])
    recs = [dict(r) for r in out["records"]]
    recs[0]["lineage_root_id"] = None
    recs[1]["study_id"] = "STUDY-000009"  # no locator
    g = keys.check_gates(recs, 2, STUDIES, DOCS)
    assert not g["G08-1"]["pass"] and g["G08-1"]["covered"] == 1
    assert not g["G08-8"]["pass"] and g["G08-8"]["fabricated"] == 1
    alias = [dict(r) for r in out["records"]]
    alias[0]["split_group_id"] = alias[0]["lineage_root_id"]
    assert not keys.check_gates(alias, 2, STUDIES, DOCS)["G08-10"]["pass"]


def test_drv_parent_union_merges_split_groups_and_gate_g08_2():
    rows = [row(1, "STUDY-000001"), row(2, "STUDY-000002"), row(3, "STUDY-000003"),
            row(4, "STUDY-000003", parent_ids=["EVD-000001", "EVD-000002"])]
    out = run(rows)
    r = by_id(out)
    assert r["EVD-000001"]["split_group_id"] == r["EVD-000002"]["split_group_id"] == r["EVD-000004"]["split_group_id"] == r["EVD-000003"]["split_group_id"]
    assert r["EVD-000001"]["lineage_root_id"] != r["EVD-000002"]["lineage_root_id"]
    assert out["stats"]["drv_rows"] == 1 and out["stats"]["drv_parents_in_different_groups_before_union"] == 1
    assert out["stats"]["drv_parents_in_different_groups_after_union"] == 0
    assert keys.check_drv_gate(out["records"], {"EVD-000004": ["EVD-000001", "EVD-000002"]})["violations"] == 0
    assert set(r["EVD-000004"]["parent_union_split_group_ids"]) == {r["EVD-000004"]["split_group_id"]}


def test_drv_gate_detects_split_parents():
    out = run([row(1, "STUDY-000001"), row(2, "STUDY-000002"), row(3, "STUDY-000003")])
    assert keys.check_drv_gate(out["records"], {"EVD-000003": ["EVD-000001", "EVD-000002"]})["violations"] == 1


def test_no_drv_reported_as_none():
    assert run([row(1, "STUDY-000001")])["stats"]["drv_rows"] == 0


def test_level_filter_and_sensitivity():
    rows = [row(1, "STUDY-000001"), row(2, "STUDY-000002"), row(3, "STUDY-000003"), row(4, "STUDY-000003")]
    es = [edge(1, 2, level="STRONG"), edge(2, 3, level="B3")]
    sens = keys.level_sensitivity(rows, STUDIES, DOCS, SRCS, es)
    assert sens["STRONG+B1"]["largest_group_rows"] == 2
    assert sens["STRONG+B1+B2"]["largest_group_rows"] == 2
    assert sens["ALL"]["largest_group_rows"] == 4
    assert sens["ALL"]["largest_group_share"] == 1.0
    assert sens["NONE"]["largest_group_rows"] == 2


def test_lab_unknown_when_authorship_unread():
    r = by_id(run([row(1, "STUDY-000001"), row(2)]))
    assert r["EVD-000001"]["lab_group_status"] == "UNKNOWN" and r["EVD-000001"]["lab_group_id"] is None


def test_same_lab_window_three_years():
    def d(auth, aff, yr, st="READ_FROM_DOCUMENT"):
        return {"authorship": {"status": st, "corresponding_author_raw": auth, "affiliations_raw": aff, "year_published": yr}}
    assert keys.same_lab(d("A. Smith", ["Uni X"], 2000), d("A. Smith", ["Uni Y"], 2020)) is True      # shared corresponding author
    assert keys.same_lab(d("A", ["Uni X"], 2000), d("B", ["Uni X"], 2003)) is True                   # same affil, 3y
    assert keys.same_lab(d("A", ["Uni X"], 2000), d("B", ["Uni X"], 2004)) is False                  # 4y > N
    assert keys.same_lab(d("A", ["Uni X"], 2000), d("B", ["Uni X"], None)) is None                   # year unknown
    assert keys.same_lab(d("A", [], 2000, st="UNKNOWN"), d("B", ["Uni X"], 2001)) is None            # authorship unread


def _write(p, recs):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in recs))


def _tool():
    spec = importlib.util.spec_from_file_location("step08a_build_keys", REPO / "tools" / "step08a_build_keys.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _mini_root(tmp):
    root = tmp / "ledgers_scratch"
    full = lambda r: {**r, "status": "ACTIVE", "version": 1}
    rows = [full({**row(1), "origin_type": "DATABASE_AGGREGATE"}), full(row(2, "STUDY-000001")), full(row(3, "STUDY-000002"))]
    _write(root / "data" / "EVD.jsonl", rows)
    _write(root / "data" / "STUDY.jsonl", [{**s, "status": "ACTIVE", "version": 1} for s in STUDIES.values()])
    _write(root / "data" / "DOC.jsonl", [{**d, "status": "ACTIVE", "version": 1} for d in DOCS.values()])
    _write(root / "data" / "SRC.jsonl", [{**s, "status": "ACTIVE", "version": 1} for s in SRCS.values()])
    edges = tmp / "edges.jsonl"
    _write(edges, [edge(2, 3)])
    return root, edges


def test_tool_deterministic_and_outputs(tmp_path):
    t = _tool()
    root, edges = _mini_root(tmp_path)
    allowed = tmp_path / "keys"
    outs = []
    for n in ("a", "b"):
        counts = t.run(root, edges, allowed / n, repo_root=REPO, allowed_out_root=allowed)
        outs.append(((allowed / n / "keys.jsonl").read_bytes(), (allowed / n / "counts.json").read_bytes()))
    assert outs[0] == outs[1]
    assert counts["gates"]["G08-1"]["pass"] and counts["rows_total"] == 3
    assert len((allowed / "a" / "keys.jsonl").read_text().splitlines()) == 3


def test_tool_refuses_repo_ledgers_and_bad_out(tmp_path):
    t = _tool()
    root, edges = _mini_root(tmp_path)
    with pytest.raises(t.RefusedPathError):
        t.run(REPO / "ledgers", edges, tmp_path / "k", repo_root=REPO, allowed_out_root=tmp_path / "k")
    with pytest.raises(t.RefusedPathError):
        t.run(root, edges, REPO / "x_out", repo_root=REPO, allowed_out_root=REPO)
    with pytest.raises(t.RefusedPathError):
        t.run(root, edges, tmp_path / "elsewhere", repo_root=REPO, allowed_out_root=tmp_path / "k")
