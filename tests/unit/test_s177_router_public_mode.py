"""S177 / SCIFIX-ROUTER: FINAL-GOV #2 public mode for the hosted demo (BBC-derived edges and carbon figures left out).

Synthetic ledger store and fake context only; one structural check reads the repo's KGE ledger (read only) to prove that
nothing BBC-derived survives the filter. ``lxml`` is not installed in the project venv: tests that import the lexicon
loader use a test-only stand-in module placed in ``sys.modules`` (nothing installed, undone after each test).
"""
from __future__ import annotations

import json
import sys
import threading
import types
import urllib.request
from pathlib import Path

import pytest

from culinarystate.decision import public_mode as PM

ROOT = Path(__file__).resolve().parents[2]
BBC = "BBCGF-A1"


@pytest.fixture
def lxml_shim(monkeypatch):
    try:
        import lxml  # noqa: F401
    except ImportError:
        pkg = types.ModuleType("lxml")
        pkg.etree = types.ModuleType("lxml.etree")
        monkeypatch.setitem(sys.modules, "lxml", pkg)
        monkeypatch.setitem(sys.modules, "lxml.etree", pkg.etree)


def _edge(eid, pred, subj, obj=None, *, corpus=None, fam=None, srcs=None, **kw):
    e = {"id": eid, "version": 1, "status": "ACTIVE", "predicate": pred, "subject_id": subj, "object_id": obj,
         "confidence": 0.3, "confidence_band": "HIGH"}
    if corpus is not None:
        e["corpus_ids"] = corpus
    if fam is not None:
        e["support"] = {"by_source_family": fam}
    if srcs is not None:
        e["provenance"] = {"source_ids": srcs}
    return {**e, **kw}


# =================================================================== the switch
def test_parse_flag_values():
    assert [PM.parse_flag(v) for v in ("1", "TRUE", " on ", "public", "yes")] == [True] * 5
    assert [PM.parse_flag(v) for v in ("0", "false", "off", "local", "No")] == [False] * 5
    assert PM.parse_flag(None) is None and PM.parse_flag("  ") is None
    with pytest.raises(ValueError):
        PM.parse_flag("maybe")


def test_resolve_precedence_and_defaults():
    # local use on the Mac: nothing set, loopback host -> OFF
    assert PM.resolve(env={}, host="127.0.0.1") == PM.Mode(False, "DEFAULT_LOCAL")
    assert PM.resolve(env={}, host=None) == PM.Mode(False, "DEFAULT_LOCAL")
    assert PM.resolve(env={}, host="localhost").public is False
    # a hosted build: markers or a non-loopback bind -> ON
    for marker in ("CS_DEMO_HOSTED", "PORT", "SPACE_ID", "K_SERVICE"):
        assert PM.resolve(env={marker: "1"}, host="127.0.0.1") == PM.Mode(True, "HOSTED_MARKER")
    assert PM.resolve(env={}, host="0.0.0.0") == PM.Mode(True, "NON_LOOPBACK_HOST")
    assert PM.resolve(env={}, host="192.0.2.7").public is True
    # the env switch overrides the automatic default in both directions
    assert PM.resolve(env={PM.ENV_PUBLIC: "1"}, host="127.0.0.1") == PM.Mode(True, "ENV")
    assert PM.resolve(env={PM.ENV_PUBLIC: "0", "PORT": "8080"}, host="0.0.0.0") == PM.Mode(False, "ENV")
    # an explicit argument beats the env
    assert PM.resolve(True, env={PM.ENV_PUBLIC: "0"}) == PM.Mode(True, "ARGUMENT")
    assert PM.resolve(False, env={PM.ENV_PUBLIC: "1"}) == PM.Mode(False, "ARGUMENT")
    # an unreadable switch fails CLOSED (public)
    assert PM.resolve(env={PM.ENV_PUBLIC: "banana"}, host="127.0.0.1") == PM.Mode(True, "ENV_INVALID_FAIL_CLOSED")
    assert PM.Mode(True, "ENV").name == "public" and PM.Mode(False, "ENV").name == "local"


def test_resolve_reads_the_process_environment_by_default(monkeypatch):
    for k in (PM.ENV_PUBLIC, *PM.HOSTED_MARKERS):
        monkeypatch.delenv(k, raising=False)
    assert PM.resolve().public is False
    monkeypatch.setenv(PM.ENV_PUBLIC, "1")
    assert PM.resolve().public is True


# =================================================================== the edge filter
def test_is_bbc_derived_uses_corpus_ids_family_support_and_the_source_record():
    assert PM.is_bbc_derived(_edge("a", "X", "S", corpus=[BBC, "WIKIBOOKS-COOKBOOK"]))
    assert PM.is_bbc_derived(_edge("b", "X", "S", fam={BBC: 103, "WIKIBOOKS-COOKBOOK": 7}))
    assert PM.is_bbc_derived(_edge("c", "X", "S", fam={BBC: 0}))                      # present with a zero count still counts
    assert PM.is_bbc_derived(_edge("d", "X", "S", corpus=["WIKIBOOKS-COOKBOOK"], fam={BBC: 2}))    # either signal
    # no corpus / family field at all (PROC_TYPICAL_DURATION): the BBC source record decides
    assert PM.is_bbc_derived(_edge("e", "X", "S", srcs=["SRC-000002", "SRC-000140"]))
    assert not PM.is_bbc_derived(_edge("f", "X", "S", srcs=["SRC-000140"]))
    # edges that name only other corpora stay
    assert not PM.is_bbc_derived(_edge("g", "X", "S", corpus=["WIKIBOOKS-COOKBOOK"], fam={"WIKIBOOKS-COOKBOOK": 4}))
    assert not PM.is_bbc_derived(_edge("h", "X", "S", corpus=["GUTENBERG-PD"], srcs=["SRC-000002"]))   # corpus field decides
    assert not PM.is_bbc_derived({"id": "i", "predicate": "X"})


def test_filter_edges_local_keeps_everything_public_drops_bbc_and_carbon():
    edges = [_edge("1", "ING_ALTERNATIVE_TO", "ING-1", "ING-2", corpus=[BBC], fam={BBC: 5}),
             _edge("2", "ING_ALTERNATIVE_TO", "ING-3", "ING-4", corpus=["WIKIBOOKS-COOKBOOK"], fam={"WIKIBOOKS-COOKBOOK": 4}),
             _edge("3", "PROC_FOLLOWED_BY", "PROC-1", "PROC-2", corpus=[BBC]),
             _edge("4", "PROC_TYPICAL_DURATION", "PROC-1", srcs=["SRC-000002"], quantiles={"p10": 1, "p50": 2, "p90": 3}),
             _edge("5", "ING_CARBON_FOOTPRINT", "ING-1", corpus=["SUEATABLE"], quantiles={"p50": 8.5}),
             _edge("6", "ING_PROCESSED_BY", "ING-3", "PROC-9", corpus=["GUTENBERG-PD"])]
    kept, dropped = PM.filter_edges(edges, public=False)
    assert [e["id"] for e in kept] == ["1", "2", "3", "4", "5", "6"] and not dropped
    kept, dropped = PM.filter_edges(edges, public=True)
    assert [e["id"] for e in kept] == ["2", "6"]
    assert dropped == {"ING_ALTERNATIVE_TO": 1, "PROC_FOLLOWED_BY": 1, "PROC_TYPICAL_DURATION": 1, "ING_CARBON_FOOTPRINT": 1}
    assert not any(PM.is_bbc_derived(e) for e in kept)


def test_describe_is_codes_and_counts_only():
    d = PM.describe(PM.Mode(True, "ENV"), {"ING_ALTERNATIVE_TO": 3})
    assert d == {"mode": "public", "public": True, "source": "ENV", "bbc_derived_edges": "EXCLUDED",
                 "carbon_figures": "EXCLUDED", "dropped_edges_by_predicate": {"ING_ALTERNATIVE_TO": 3}}
    loc = PM.describe(PM.Mode(False, "DEFAULT_LOCAL"))
    assert loc["mode"] == "local" and loc["bbc_derived_edges"] == "INCLUDED_LOCAL_ONLY" and loc["dropped_edges_by_predicate"] == {}


def test_the_repo_kge_ledger_has_no_bbc_derived_edge_left_in_public_mode():
    latest = {}
    with (ROOT / "ledgers" / "data" / "KGE.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["id"] not in latest or r["version"] > latest[r["id"]]["version"]:
                latest[r["id"]] = r
    active = [e for e in latest.values() if e["status"] == "ACTIVE"]
    kept, dropped = PM.filter_edges(active, public=True)
    assert not any(PM.is_bbc_derived(e) or e["predicate"] == PM.CARBON_PREDICATE for e in kept)
    assert dropped["ING_CARBON_FOOTPRINT"] > 0 and dropped["ING_ALTERNATIVE_TO"] > 0 and dropped["PROC_FOLLOWED_BY"] > 0
    assert dropped["PROC_TYPICAL_DURATION"] > 0                                       # found through the source record
    # the demo's own substitution and sequence edges: what is left is only Wikibooks / Gutenberg-supported
    for e in kept:
        if e["predicate"] in ("ING_ALTERNATIVE_TO", "PROC_FOLLOWED_BY"):
            assert not (set(e.get("corpus_ids") or ()) & {BBC})
    assert len(kept) + sum(dropped.values()) == len(active)


# =================================================================== the lexicon / requirements loaders
class FakeStore:
    def __init__(self, tables):
        self.t = tables

    def all_latest(self, prefix):
        return [dict(r) for r in self.t.get(prefix, [])]


def _store():
    ing = lambda i, n, **k: {"id": i, "status": "ACTIVE", "canonical_name": n, "parent_ids": [], **k}  # noqa: E731
    proc = lambda i, n, fam: {"id": i, "status": "ACTIVE", "canonical_name": n, "family": fam}  # noqa: E731
    kge = [
        _edge("K1", "ING_ALTERNATIVE_TO", "ING-1", "ING-2", corpus=[BBC], fam={BBC: 50}, confidence=0.4),      # BBC
        _edge("K2", "ING_ALTERNATIVE_TO", "ING-3", "ING-4", corpus=["WIKIBOOKS-COOKBOOK"],
              fam={"WIKIBOOKS-COOKBOOK": 4}, confidence=0.2),                                                 # not BBC
        _edge("K3", "PROC_FOLLOWED_BY", "PROC-1", "PROC-2", corpus=[BBC, "GUTENBERG-PD"],
              fam={BBC: 9, "GUTENBERG-PD": 1}, confidence=0.5),
        _edge("K4", "PROC_FOLLOWED_BY", "PROC-2", "PROC-1", corpus=["GUTENBERG-PD"], fam={"GUTENBERG-PD": 3}),
        _edge("K5", "PROC_TYPICAL_DURATION", "PROC-1", srcs=["SRC-000002", "SRC-000140"],
              quantiles={"p10": 2.0, "p50": 9.0, "p90": 60.0}),
        _edge("K6", "ING_CARBON_FOOTPRINT", "ING-1", corpus=["SUEATABLE"], quantiles={"p50": 8.48}),
        _edge("K7", "ING_PROCESSED_BY", "ING-1", "PROC-1", corpus=[BBC], fam={BBC: 20}, confidence=0.6),
        _edge("K8", "ING_PROCESSED_BY", "ING-3", "PROC-2", corpus=["GUTENBERG-PD"], fam={"GUTENBERG-PD": 2}, confidence=0.1),
        _edge("K9", "PROC_USES_TOOL", "PROC-1", "TOOL-1", corpus=[BBC], association={"p_object_given_subject": 0.9}),
        _edge("K10", "PROC_USES_TOOL", "PROC-2", "TOOL-2", corpus=["WIKIBOOKS-COOKBOOK"],
              association={"p_object_given_subject": 0.9}),
    ]
    return FakeStore({"ING": [ing("ING-1", "butter"), ing("ING-2", "margarine"), ing("ING-3", "ricotta"),
                              ing("ING-4", "cottage cheese")],
                      "ALIAS": [], "PROC": [proc("PROC-1", "boil", "WET_HEAT"), proc("PROC-2", "drain", "SEPARATION")],
                      "KGE": kge, "EVD": [], "ALLERGEN": []})


def test_load_lexicon_local_keeps_everything(lxml_shim):
    from culinarystate.decision.pipeline import load_lexicon
    lex, _ = load_lexicon(_store(), off_path=None)
    assert set(lex.alternatives) == {"ING-1", "ING-3"} and set(lex.followed_by) == {"PROC-1", "PROC-2"}
    assert lex.carbon == {"ING-1": 8.48} and lex.durations == {"PROC-1": 9.0}
    assert set(lex.processed_by) == {"ING-1", "ING-3"}
    assert lex.public_mode["mode"] == "local" and lex.public_mode["dropped_edges_by_predicate"] == {}


def test_load_lexicon_public_drops_bbc_edges_before_candidates_and_empties_carbon(lxml_shim):
    from culinarystate.decision.candidates import sequence_candidates, substitution_candidates
    from culinarystate.decision.pipeline import load_lexicon
    lex, _ = load_lexicon(_store(), off_path=None, public=True)
    assert set(lex.alternatives) == {"ING-3"}                      # the BBC-supported butter -> margarine edge is gone
    assert [c.id for c in substitution_candidates("ING-1", lex.alternatives, lex.ing_names)] == []
    assert [c.id for c in substitution_candidates("ING-3", lex.alternatives, lex.ing_names)] == ["ING-4"]   # Wikibooks-only stays
    names = {"PROC-1": "boil", "PROC-2": "drain"}
    assert sequence_candidates("PROC-1", lex.followed_by, names) == []                                    # BBC-supported edge gone
    assert [c.id for c in sequence_candidates("PROC-2", lex.followed_by, names)] == ["PROC-1"]
    assert lex.carbon == {} and lex.durations == {}                # carbon emptied; the duration edge was BBC-sourced
    assert set(lex.processed_by) == {"ING-3"}
    assert lex.public_mode["mode"] == "public" and lex.public_mode["dropped_edges_by_predicate"] == {
        "ING_ALTERNATIVE_TO": 1, "PROC_FOLLOWED_BY": 1, "PROC_TYPICAL_DURATION": 1, "ING_CARBON_FOOTPRINT": 1,
        "ING_PROCESSED_BY": 1, "PROC_USES_TOOL": 1}


def test_extra_candidates_carry_no_carbon_text_in_public_mode(lxml_shim):
    from culinarystate.decision.pipeline import Slots, extra_candidates, load_lexicon
    store = _store()
    store.t["KGE"].append(_edge("K11", "ING_CARBON_FOOTPRINT", "ING-2", corpus=["SUEATABLE"], quantiles={"p50": 2.0}))
    store.t["KGE"].append(_edge("K12", "ING_ALTERNATIVE_TO", "ING-1", "ING-2", corpus=["WIKIBOOKS-COOKBOOK"],
                                fam={"WIKIBOOKS-COOKBOOK": 3}, confidence=0.3))
    slots = Slots("ING-1", "butter", (), (), None, ())
    local, _ = load_lexicon(store, off_path=None)
    pub, _ = load_lexicon(store, off_path=None, public=True)
    q = "What can I use instead of butter?"
    assert any("carbon" in c.reason for c in extra_candidates(q, slots, local).candidates)      # local still adds the figure
    cs = extra_candidates(q, slots, pub)
    assert cs is not None and cs.candidates and not any("carbon" in c.reason or "kgCO2e" in c.reason for c in cs.candidates)


def test_load_requirements_public_drops_bbc_tool_and_duration_edges(lxml_shim):
    from culinarystate.decision.feasibility import load_requirements
    local = load_requirements(_store())
    pub = load_requirements(_store(), public=True)
    assert set(local.required_tools) == {"PROC-1", "PROC-2"} and "PROC-1" in local.typical_minutes
    assert set(pub.required_tools) == {"PROC-2"} and pub.typical_minutes == {}


# =================================================================== the context and the page
def _ctx(lxml_shim_used, public: bool):
    from culinarystate.decision.demo_context import DemoContext
    from culinarystate.decision.pipeline import load_lexicon
    store = _store()
    lex, _ = load_lexicon(store, off_path=None, public=public)
    mode = PM.describe(PM.Mode(public, "ARGUMENT"), lex.public_mode["dropped_edges_by_predicate"])
    return DemoContext(lex=lex, mode=mode, gates=None)


def test_context_answers_a_substitution_in_local_mode_and_abstains_in_public_mode(lxml_shim):
    local = _ctx(lxml_shim, False).respond("What can I use instead of butter?")
    assert local["demo_mode"]["mode"] == "local" and local["mode"] == "ANSWER_CORPUS_PATTERN"
    pub_ctx = _ctx(lxml_shim, True)
    pub = pub_ctx.respond("What can I use instead of butter?")
    assert pub["mode"] == "ABSTAIN_NO_EDGES" and "margarine" not in json.dumps(pub)          # nothing BBC-derived is served
    assert "public build" in pub["answer"] and pub["demo_mode"]["public"] is True
    assert pub["demo_mode"]["bbc_derived_edges"] == "EXCLUDED" and pub["demo_mode"]["carbon_figures"] == "EXCLUDED"
    wiki = pub_ctx.respond("What can I use instead of ricotta?")                             # the Wikibooks-only edge still works
    assert wiki["mode"] == "ANSWER_CORPUS_PATTERN" and "cottage cheese" in wiki["answer"]


def test_every_response_names_the_mode_even_an_abstention(lxml_shim):
    ctx = _ctx(lxml_shim, True)
    for q in ("Is chicken safe to eat if it is still pink inside?", "", "Here is a photo of my bread, is it proofed?"):
        out = ctx.respond(q)
        assert out["demo_mode"]["mode"] == "public", q
    from culinarystate.decision.demo_context import DemoContext
    assert DemoContext().mode_info() == {"mode": "local", "public": False, "source": "DEFAULT_LOCAL"}   # no mode given: local


class _FakeCtx:
    def __init__(self, mode):
        self._m = mode

    def mode_info(self):
        return self._m

    def respond(self, q, recipe_text=None):
        return {"mode": "ASK", "answer": "x", "demo_mode": self._m}


@pytest.mark.parametrize("name", ["public", "local"])
def test_health_endpoint_reports_the_active_mode(name):
    from culinarystate.app import server as S
    srv = S.make_server(("127.0.0.1", 0), _FakeCtx({"mode": name, "public": name == "public"}), per_minute=100)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{srv.server_address[1]}/api/health", timeout=5) as r:
            body = json.loads(r.read())
    finally:
        srv.shutdown()
    assert body["status"] == "ok" and body["mode"]["mode"] == name


def test_server_main_passes_the_flags_and_host_to_the_context(monkeypatch):
    from culinarystate.app import server as S
    from culinarystate.decision import demo_context as DC
    seen = {}

    def fake_load(public=None, host=None):
        seen.update(public=public, host=host)
        return _FakeCtx({"mode": "public" if public else "local", "source": "ARGUMENT"})

    monkeypatch.setattr(DC.DemoContext, "load", staticmethod(fake_load))
    monkeypatch.setattr(S, "make_server", lambda addr, ctx, per_minute=30: types.SimpleNamespace(serve_forever=lambda: None))
    assert S.main(["--public", "--host", "0.0.0.0"]) == 0 and seen == {"public": True, "host": "0.0.0.0"}
    assert S.main(["--local"]) == 0 and seen == {"public": False, "host": "127.0.0.1"}
    assert S.main([]) == 0 and seen == {"public": None, "host": "127.0.0.1"}              # None: env, then automatic
    with pytest.raises(SystemExit):
        S.main(["--public", "--local"])


def test_page_states_the_mode_and_explains_the_new_reason():
    html = (ROOT / "src/culinarystate/app/static/index.html").read_text(encoding="utf-8")
    assert 'id="mode"' in html and 'fetch("/api/health")' in html
    assert "Public mode" in html and "Local mode" in html and "Mode unknown" in html
    assert "PRIOR_PROCESS_CONTEXT" in html                                                   # the step reason has text
    assert "textContent" in html and "innerHTML" not in html                                 # the page still renders by textContent
