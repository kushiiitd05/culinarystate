"""DEL-3 state engine fixtures: merge/split/reserve/discard/recombine/observe/replay."""
from fractions import Fraction

from culinarystate.state_graph.engine import (AcceptCandidate, Add, Discard, Merge, Observe, OmittedStepCandidate,
                                              Predict, Recombine, Reserve, Split, Transfer, Transform, replay)
from culinarystate.state_graph.symqty import Base, SymQty

G = lambda v: Base.amount("g", v, f"{v:g} g")  # noqa: E731


# ---------- symbolic quantity algebra ----------
def test_symqty_no_invented_grams():
    butter = SymQty.of(G(50))
    rest = butter.minus(SymQty.of(Base.amount("mL", 14.79, "1 tbsp")))
    assert rest.evaluate()["status"] == "UNKNOWN"            # g − mL stays symbolic
    assert rest.render() == "50 g − 1 tbsp"


def test_symqty_interval_fraction_propagation():
    q = SymQty.of(Base.interval("g", 100, 120, "100–120 g")).scale(Fraction(1, 2))
    assert q.evaluate() == {"status": "RANGE", "low": 50.0, "high": 60.0, "unit": "g", "raw": "1/2×100–120 g"}


def test_symqty_same_dim_arithmetic_and_cancel():
    a = SymQty.of(G(500))
    assert a.minus(a.scale(Fraction(1, 4))).evaluate()["value"] == 375.0
    assert a.minus(a).evaluate()["value"] == 0.0


def test_qualitative_stays_unknown():
    assert SymQty.of(Base.qualitative("a pinch")).evaluate()["status"] == "UNKNOWN"


# ---------- engine fixtures ----------
def pancakes():
    return [
        Add("flour", "ING-000007", G(100), step=1),
        Add("eggs", "ING-000004", Base.amount("count", 2, "2 eggs"), step=1),
        Add("milk", "ING-000014", Base.amount("mL", 300, "300 ml"), step=1),
        Merge(("flour", "eggs", "milk"), "batter", "whisk", step=1),
        Reserve("batter", "test batter", portion=Base.amount("mL", 30, "2 tbsp"), step=2),
        Transfer("batter", "frying pan", step=3),
        Transform("batter", "fry", {"heat": "medium (qualitative)"}, (("doneness", "golden"),), step=3),
    ]


def test_merge_creates_intermediate_and_consumes_parents():
    g = replay(pancakes())
    assert not g.current("flour").alive and not g.current("eggs").alive
    assert g.concepts["batter"] is None and g.concepts["flour"] == "ING-000007"   # concept ≠ entity
    rel = {(e.src, e.relation) for e in g.edges}
    assert ("flour@1", "MERGES_INTO") in rel
    # mixed dimensions -> symbolic, numeric UNKNOWN
    assert g.versions["batter"][0].qty.evaluate()["status"] == "UNKNOWN"
    assert "100 g" in g.versions["batter"][0].qty.render()


def test_reserve_remainder_symbolic_and_location():
    g = replay(pancakes())
    assert g.current("test batter").qty.render() == "2 tbsp"
    assert "− 2 tbsp" in g.current("batter").qty.render()
    assert g.current("batter").location == "frying pan"
    assert g.current("batter").get("doneness").value == "golden"


def test_append_only_history():
    g = replay(pancakes())
    ns = [v.n for v in g.versions["batter"]]
    assert ns == list(range(len(ns)))                      # versions only grow, never rewritten
    assert g.versions["batter"][0].location is None        # old version unchanged after transfer


def test_split_quantity_propagation():
    g = replay([Add("dough", None, G(500)), Split("dough", (("ball1", Fraction(1, 4)), ("rest", Fraction(3, 4))))])
    assert g.current("ball1").qty.evaluate()["value"] == 125.0
    assert g.current("rest").qty.evaluate()["value"] == 375.0
    assert not g.current("dough").alive


def test_split_fraction_overflow_flagged():
    g = replay([Add("dough", None, G(500)), Split("dough", (("a", Fraction(2, 3)), ("b", Fraction(2, 3))))])
    assert any("sum to" in x for x in g.issues) and g.current("dough").alive


def test_discard_and_recombine_pasta_water():
    ev = [Add("pasta", None, G(300)), Add("water", None, Base.amount("mL", 2000, "2 L")),
          Merge(("pasta", "water"), "pot"), Transform("pot", "boil"),
          Split("pot", (("pasta drained", None), ("cooking water", None))),
          Reserve("cooking water", "reserved water", portion=Base.amount("mL", 100, "100 ml")),
          Discard("cooking water", what="drained water"),
          Add("sauce", None, Base.qualitative("sauce")), Merge(("pasta drained", "sauce"), "dish"),
          Recombine("reserved water", "dish")]
    g = replay(ev)
    rels = [e.relation for e in g.edges]
    for r in ("MERGES_INTO", "SPLITS_INTO", "RESERVED_AS", "DISCARDED_FROM", "RECOMBINED_WITH", "TRANSFORMS_INTO"):
        assert r in rels
    assert not g.current("cooking water").alive and not g.current("reserved water").alive
    assert "100 ml" in g.current("dish").qty.render()
    assert g.issues == ()


def test_observation_overrides_prediction_and_keeps_audit():
    ev = [Add("onion", "ING-000005", Base.amount("count", 1, "1 onion")),
          Transform("onion", "fry"), Predict("onion", "colour", "translucent", "rule:fry_onion_8min"),
          Observe("onion", "colour", "browned", source="user"),
          Predict("onion", "colour", "translucent", "rule:fry_onion_8min")]
    g = replay(ev)
    b = g.current("onion").get("colour")
    assert (b.value, b.trajectory) == ("browned", "OBSERVED_SESSION")
    assert g.audit[0]["superseded"]["value"] == "translucent"            # prior prediction preserved
    assert g.audit[1]["reason"] == "observation outranks prediction"


def test_using_consumed_entity_flagged():
    g = replay([Add("a", None, G(1)), Add("b", None, G(1)), Merge(("a", "b"), "ab"), Transform("a", "chop")])
    assert any("already consumed" in x for x in g.issues)


def test_omitted_step_candidate_not_applied_until_accepted():
    cand = OmittedStepCandidate("C1", 2, "preheat oven", "bake step without preheat",
                                proposed=(Transfer("tray", "oven"),))
    base = [Add("tray", None, Base.qualitative("tray")), cand]
    g = replay(base)
    assert g.current("tray").location is None and g.candidates == ("C1",)
    g2 = replay(base + [AcceptCandidate("C1", by="Parv")])
    assert g2.current("tray").location == "oven" and g2.accepted == (("C1", "Parv"),)


def test_replay_deterministic():
    assert replay(pancakes()).sha256() == replay(list(pancakes())).sha256()
    assert replay(pancakes()).sha256() != replay(pancakes()[:-1]).sha256()


def test_existing_label_never_overwritten():
    ev = [Add("a", None, G(1)), Add("b", None, G(1)), Merge(("a", "b"), "ab"),
          Add("c", None, G(1)), Merge(("c",), "a"),                    # 'a' exists (consumed)
          Split("ab", (("b", Fraction(1, 2)), ("x", Fraction(1, 2))))]  # 'b' exists
    g = replay(ev)
    assert len(g.versions["a"]) == 2 and g.versions["a"][0].event_index == 0   # history intact
    assert sum("already exist" in x for x in g.issues) == 2
    assert g.current("ab").alive and g.current("c").alive
