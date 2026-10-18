from culinarystate.annotation.examples import ALL, pasta_reserved_water, white_sauce
from culinarystate.annotation.gold import to_events
from culinarystate.scoring.state_metrics import align_entities, aligned_state_scores, relabel
from culinarystate.state_graph.engine import Merge, Recombine, Reserve, Split, replay
from culinarystate.state_graph.rule_compiler import compile_recipe, step_processes

NAMES = {"butter", "unsalted butter", "plain flour", "milk", "nutmeg", "spaghetti", "garlic", "olive oil", "salt",
         "carrot", "red onion"}


def _run(doc):
    lines = [x["text"] for x in doc["ingredient_lines"]]
    steps = [x["text"] for x in doc["steps"]]
    return compile_recipe(lines, steps, NAMES)


def test_verbs_capitalised_and_nouns_not_verbs():
    assert step_processes("Stir the flour into the butter.")[0][1] == "stir"
    assert all(p != "brush" for _, p in step_processes("Melt the butter in a pan."))
    assert all(p != "reserve" for _, p in step_processes("Add the reserved water."))
    assert ("heat" not in [p for _, p in step_processes("Fry over a low heat.")])


def test_white_sauce_structure():
    ev = _run(white_sauce())
    g = replay(ev)
    assert g.issues == ()
    assert [type(e).__name__ for e in ev if isinstance(e, (Merge, Reserve))] == ["Reserve", "Merge", "Merge", "Merge"]
    s = aligned_state_scores(to_events(white_sauce()), ev)
    assert s["merge_split_f1"]["f1"] == 1.0 and s["alignment"]["mixture 1"] == "roux"


def test_drain_reserve_discard_pattern():
    ev = _run(pasta_reserved_water())
    kinds = [type(e).__name__ for e in ev]
    assert "Split" in kinds and "Discard" in kinds
    assert not any(isinstance(e, Reserve) and e.source.startswith("mixture") for e in ev)


def test_all_examples_replay_clean():
    for fn in ALL:
        assert replay(_run(fn())).issues == ()


def test_alignment_relabel_identity():
    ev = to_events(white_sauce())
    m = align_entities(ev, ev)
    assert all(k == v for k, v in m.items())
    assert replay(relabel(ev, m)).sha256() == replay(ev).sha256()
