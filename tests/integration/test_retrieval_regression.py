"""SSOT §257I.4 retrieval regression suite: fixed queries, gold evidence ids, scientific hard negatives.

Hard negatives differ from the gold by exactly one axis (same food/other process, same process/other food). A
reranker or index change may move ranks, but must keep gold in the top 10 and never class a hard negative DIRECT.
Frozen 2026-10-18 against ledger HEAD b72d8a9; update only with a WORKLOG entry explaining the change.
"""
import pytest

from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidenceRetriever

pytestmark = pytest.mark.ledgers

SUITE = [  # (name, question, query kwargs, gold ids (any in top 10 / in pool), hard negatives (never DIRECT), class)
    ("onion fry quercetin", "quercetin in fried onion",
     dict(ingredient_id="ING-000005", process_id="PROC-000009", target="quercetin"),
     ["EVD-009501", "EVD-009502"], ["EVD-007019", "EVD-007020"], "DIRECT"),
    ("onion boil quercetin glucoside", "quercetin 4'-O-glucoside in boiled onion",
     dict(ingredient_id="ING-000005", process_id="PROC-000019", target="quercetin 4'-o-glucoside"),
     ["EVD-007019", "EVD-007020", "EVD-007021"], ["EVD-009501"], "DIRECT"),
    ("beef roast thiamin", "thiamin retention in roast beef",
     dict(ingredient_id="ING-000267", process_id="PROC-000002", target="thiamin"),
     ["EVD-003988"], ["EVD-003884", "EVD-003910", "EVD-001362"], "DIRECT"),
    ("pork roast thiamin", "thiamin retention in roast pork",
     dict(ingredient_id="ING-000374", process_id="PROC-000002", target="thiamin"),
     ["EVD-001362", "EVD-001648"], ["EVD-003988"], "DIRECT"),
    ("broccoli boil vitamin c (group-level only)", "vitamin C in boiled broccoli",
     dict(ingredient_id="ING-000103", ingredient_name="broccoli", process_id="PROC-000019", target="vitamin c"),
     ["EVD-016808", "EVD-016809"], [], "INTERPOLATED"),
]


@pytest.fixture(scope="module")
def retr(latest):
    cond = {c["id"]: c for c in latest("COND")}
    fam = {p["id"]: p["family"] for p in latest("PROC")}
    return EvidenceRetriever(latest("EVD"), cond, fam), fam


@pytest.mark.parametrize("name,question,qkw,gold,negatives,cls", SUITE, ids=[s[0] for s in SUITE])
def test_gold_in_top10_and_hard_negatives_never_direct(retr, name, question, qkw, gold, negatives, cls):
    r, fam = retr
    q = Query(process_family=fam.get(qkw["process_id"]), **qkw)
    hits = [h.evd_id for h in r.search(question, q, k=10)]
    p = r.packet(question, q, k=10)
    pool = [h.evd_id for h in p.direct + p.near]
    assert set(gold) & (set(hits) | set(pool)), f"{name}: no gold in top 10 {hits}"
    assert not set(negatives) & {h.evd_id for h in p.direct}, f"{name}: hard negative classed DIRECT"
    assert p.evidence_class == cls, f"{name}: class {p.evidence_class} != {cls}"


def test_unknown_ingredient_never_direct(retr):
    r, fam = retr
    p = r.packet("vitamin C in boiled romanesco", Query(ingredient_name="romanesco", process_id="PROC-000019",
                                                        target="vitamin c"), k=10)
    assert not p.direct
