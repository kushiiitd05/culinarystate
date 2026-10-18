from culinarystate.ingest.wikibooks import _summary, parse_recipe, to_plain

PAGE = {"title": "Cookbook:Potato Curry (Aloo Masala)", "pageid": 1, "revid": 2, "timestamp": "t",
        "categories": ["Indian recipes", "Recipes using potato", "Vegan recipes", "Recipes"],
        "content": """{{recipesummary|category=Side dish recipes|servings=4-6|time=20 minutes|difficulty=3|Image=[[File:A.jpg|300px]]}}
'''Potato masala''' is a dish.
==Ingredients==
* 1 [[Cookbook:Tablespoon|tablespoon]] [[cookbook:oil|oil]]
* 4 large [[Cookbook:Potato|potatoes]], cubed
==Procedure==
# Heat oil.
# [[Cookbook:Sautéing|Sautée]] the mustard seed first.
[[Category:Indian recipes]]"""}


def test_to_plain_spans():
    ln = to_plain("4 large [[Cookbook:Potato|potatoes]], cubed and [[Cookbook:Salt]]")
    assert ln.text == "4 large potatoes, cubed and Salt"
    assert [ln.text[a:b] for a, b, _ in ln.links] == ["potatoes", "Salt"]
    assert [t for *_, t in ln.links] == ["Potato", "Salt"]


def test_parse_recipe():
    r = parse_recipe(PAGE)
    assert r["summary"] == {"category": "Side dish recipes", "servings": "4-6", "time": "20 minutes", "difficulty": "3"}
    assert [i["text"] for i in r["ingredients"]] == ["1 tablespoon oil", "4 large potatoes, cubed"]
    assert r["ingredients"][0]["links"][1][2] == "oil"
    assert [s["text"] for s in r["steps"]] == ["Heat oil.", "Sautée the mustard seed first."]
    assert r["steps"][1]["links"][0][2] == "Sautéing"


def test_subsection_groups():
    page = {**PAGE, "content": "==Ingredients==\n===Dough===\n* 2 cups flour\n===Filling===\n* 1 onion\n"
                               "==Procedure==\n# Mix.\n==Notes==\n* not an ingredient"}
    r = parse_recipe(page)
    assert [(i["group"], i["text"]) for i in r["ingredients"]] == [("dough", "2 cups flour"), ("filling", "1 onion")]
    assert [s["text"] for s in r["steps"]] == ["Mix."]


def test_summary_missing():
    assert _summary("no template") == {}
