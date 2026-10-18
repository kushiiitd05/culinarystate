from culinarystate.vocab.line_link import LineLinker

L = LineLinker({"potato": "ING-1", "red onion": "ING-2", "onion": "ING-3", "oil": "ING-4", "mustard seed": "ING-5"},
               {"tablespoon", "cup"})


def test_ngram_prefers_longest_and_head():
    assert L.link("2 large red onions, chopped") == ("ING-2", "ngram")
    assert L.link("1 onion (about 200 g)") == ("ING-3", "ngram")
    assert L.link("½ teaspoon mustard seeds") == ("ING-5", "ngram")
    assert L.link("a pinch of saffron") == (None, "none")


def test_wiki_links_skip_units():
    text = "1 tablespoon oil"
    assert L.link(text, [(2, 12, "Tablespoon"), (13, 16, "Oil")]) == ("ING-4", "wiki_link")
