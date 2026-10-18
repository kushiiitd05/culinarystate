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


def test_mentions_longest_first():
    assert L.mentions("Fry the red onions in oil, then add potatoes and mustard seed.") == ["ING-2", "ING-4", "ING-1", "ING-5"]


def test_free_text_excludes_verb_homographs():
    ll = LineLinker({"fry": "ING-9", "butter": "ING-1"}, set())
    assert ll.mentions("Fry in butter") == ["ING-1"]
