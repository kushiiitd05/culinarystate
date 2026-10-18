"""SSOT §257I.3 graph replay tests over every scripted session.

1. Determinism: same events -> same sha256.
2. Prefix consistency (event sourcing): replaying the first k events reproduces exactly the full graph's versions
   whose event_index < k — later events never rewrite earlier history.
3. Correction propagation: changing an upstream annotation (reserve fraction) yields the expected revised state.
"""
import copy
import json
from pathlib import Path

import pytest

from culinarystate.annotation.sessions import check_session, to_events
from culinarystate.state_graph.engine import replay

SESSIONS = sorted((Path(__file__).resolve().parents[2] / "annotation" / "sessions").glob("SES-*.json"))
DOCS = [json.loads(p.read_text()) for p in SESSIONS]


def _history(g, k=None):
    return {e: [v for v in vs if k is None or v.event_index < k] for e, vs in g.versions.items()}


@pytest.mark.parametrize("doc", DOCS, ids=[d["session_id"] for d in DOCS])
def test_session_replay_deterministic_and_prefix_consistent(doc):
    ev = to_events(doc)
    full = replay(ev)
    assert full.sha256() == replay(list(ev)).sha256()
    for k in range(1, len(ev) + 1):
        pre = _history(replay(ev[:k]))
        trunc = {e: vs for e, vs in _history(full, k).items() if vs}
        assert {e: vs for e, vs in pre.items() if vs} == trunc, f"{doc['session_id']}: history rewritten at k={k}"


def test_annotation_correction_propagates_to_revised_state():
    doc = next(d for d in DOCS if d["session_id"] == "SES-008")              # half the tomatoes reserved
    fixed = copy.deepcopy(doc)
    fixed["turns"][1]["events"][0]["fraction"] = "1/4"                         # annotator correction
    fixed["turns"] = fixed["turns"][:2]                                        # stop before recombine
    g = replay(to_events(fixed))
    assert g.current("tomatoes for later").qty.render() == "1/4×4 tomatoes"
    assert check_session(doc)["pass"]                                          # original still consistent


def test_sessions_all_pass_as_golden_examples():
    assert all(check_session(d)["pass"] for d in DOCS) and len(DOCS) >= 30
