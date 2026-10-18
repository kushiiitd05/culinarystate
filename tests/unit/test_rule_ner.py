from culinarystate.ner.rule_ner import tag_line


def _lab(line):
    return [(line[s:e], lab) for s, e, lab in tag_line(line, 0, lambda t: t.lower() in {"onions", "olive oil", "rum"})]


def test_basic_line():
    assert _lab("5 ounces rum") == [("5", "QUANTITY"), ("ounces", "UNIT"), ("rum", "FOOD")]


def test_modifiers_and_process():
    got = _lab("2 large red onions, finely chopped")
    assert ("large", "PHYSICAL_QUALITY") in got and ("red", "COLOR") in got and ("onions", "FOOD") in got
    assert ("finely chopped", "PROCESS") in got


def test_purpose():
    assert ("for garnish", "PURPOSE") in _lab("fresh parsley, for garnish")


def test_parenthetical_quantity_and_container():
    got = _lab("1 (8 ounce) package cream cheese")
    assert ("8", "QUANTITY") in got and ("ounce", "UNIT") in got and ("package", "UNIT") in got
