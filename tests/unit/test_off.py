from culinarystate.vocab.off import parse_block

BLOCK = """< en: herbs
# a comment
en: coriander leaf, coriander leaves, cilantro
hi: धनिया पत्ती
wikidata:en: Q65523167
usda_fdc_code:en: 169997""".splitlines()


def test_parse_block():
    e = parse_block(BLOCK)
    assert e.id == "en:coriander leaf" and e.parents == ["en:herbs"]
    assert e.names["en"] == ["coriander leaf", "coriander leaves", "cilantro"] and e.names["hi"] == ["धनिया पत्ती"]
    assert e.props == {"wikidata": "Q65523167", "usda_fdc_code": "169997"}


def test_skips_synonym_blocks():
    assert parse_block(["synonyms:en: colour, color"]) is None
