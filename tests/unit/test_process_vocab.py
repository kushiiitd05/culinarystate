from culinarystate.process.vocab import BY_CANON, LEMMA_TO_PROC, PROCESSES, map_step_name, phrase_processes


def test_unique_canonicals_and_aliases_resolve():
    assert len({p.canonical for p in PROCESSES}) == len(PROCESSES)
    assert LEMMA_TO_PROC["whizz"] == "blend" and LEMMA_TO_PROC["break"] == "crack"


def test_phrases():
    assert "boil" in phrase_processes("Bring a large pan of water to the boil.")
    assert "reserve" in phrase_processes("Set the chicken aside.")
    assert "cool" in phrase_processes("Leave to cool completely.")
    assert "adjust-heat" in phrase_processes("Turn down the heat and simmer.")


def test_endpoints_are_marked():
    assert BY_CANON["soften"].kind == "ENDPOINT" and BY_CANON["fry"].kind == "ACTION"


def test_evidence_step_mapping():
    assert map_step_name("pressure-boil") == "pressure-cook"
    assert map_step_name("store-frozen") == "freeze"
    assert map_step_name("broil") == "grill"
    assert map_step_name("teleport") is None
