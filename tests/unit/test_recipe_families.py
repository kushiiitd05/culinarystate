from culinarystate.ingest.recipe_families import families, shingles


def test_near_duplicates_grouped_distinct_kept_apart():
    base = "Heat the oil in a large pan and fry the onions until soft and golden, then add the garlic and cook for one minute more."
    docs = {"A": base, "B": base + " Season well.", "C": "Whisk the eggs with the sugar until pale, fold in the flour and bake for twenty minutes."}
    fam, pairs = families(docs)
    assert fam["A"] == fam["B"] != fam["C"]
    assert pairs and pairs[0][2] >= 0.8


def test_shingles_short_text():
    assert len(shingles("two words")) == 1 and shingles("") == set()
