from culinarystate.retrieval.food_graph import FoodGraph

ING = [{"id": "ING-1", "parent_ids": [], "external_refs": ["OFF:en:spinach"]},
       {"id": "ING-2", "parent_ids": [], "external_refs": ["OFF:en:chard"]},
       {"id": "ING-3", "parent_ids": [], "external_refs": ["OFF:en:leaf vegetable"]},
       {"id": "ING-4", "parent_ids": ["ING-1"], "external_refs": []},                 # baby spinach (FORM_OF)
       {"id": "ING-5", "parent_ids": [], "external_refs": ["OFF:en:carrot"]},
       {"id": "ING-6", "parent_ids": [], "external_refs": ["OFF:en:vegetable"]}]
OFF = {"en:spinach": ["en:leaf vegetable"], "en:chard": ["en:leaf vegetable"], "en:leaf vegetable": ["en:vegetable"],
       "en:carrot": ["en:root vegetable"], "en:root vegetable": ["en:vegetable"], "en:vegetable": []}
G = FoodGraph(ING, OFF, max_siblings=10)


def test_relations_from_ing_hierarchy_and_off_taxonomy():
    r = G.related("ING-1", siblings=True)
    assert r["ING-4"] == "CHILD" and r["ING-2"] == "SIBLING" and r["ING-3"] == "PARENT"
    assert r["ING-6"] == "ANCESTOR" and "ING-5" not in r and "ING-1" not in r


def test_child_sees_parent_and_unknown_is_empty():
    assert G.related("ING-4")["ING-1"] == "PARENT"
    assert G.related("ING-999") == {} and G.related(None) == {}


def test_broad_parents_do_not_create_siblings():
    g = FoodGraph(ING, OFF, max_siblings=1)
    assert "ING-2" not in g.related("ING-1", siblings=True)        # leaf vegetable has 2 children > cap


def test_deterministic():
    assert G.related("ING-1", True) == FoodGraph(list(reversed(ING)), OFF, max_siblings=10).related("ING-1", True)


def test_siblings_off_by_default_after_r4_evaluation():
    assert "ING-2" not in G.related("ING-1", siblings=False) and G.related("ING-1", siblings=False)["ING-4"] == "CHILD"
