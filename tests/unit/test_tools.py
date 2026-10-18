from culinarystate.process.tools import TOOLS, find_tools


def names(text):
    return [t for _, t, _ in find_tools(text)]


def test_verb_vs_tool():
    assert names("Whisk the eggs.") == []
    assert names("Beat with a whisk.") == ["whisk"]
    assert names("Grill for 5 mins.") == [] and names("Put under a hot grill.") == ["grill"]


def test_multiword_and_material():
    t = find_tools("Heat oil in a large non-stick frying pan.")
    assert t[0][1] == "frying pan" and t[0][2] == "non-stick"
    assert names("Blitz in a food processor") == ["food processor"]
    assert names("Cook on a hot tawa") == ["tawa"]


def test_unique_canonicals():
    assert len({t.canonical for t in TOOLS}) == len(TOOLS)
