from culinarystate.molecules.pubchem import molecule_name, stereo_status, tanimoto_hex


def test_molecule_name_refuses_aggregates():
    assert molecule_name("Vitamin C, total ascorbic acid") == "ascorbic acid"
    for t in ("Folate, total", "Calcium, Ca", "Lutein + zeaxanthin", "Anthocyanins, total", "Vitamin B-6", "Polyphenols, total"):
        assert molecule_name(t) is None, t
    assert molecule_name("Quercetin") == "quercetin"


def test_stereo_and_tanimoto():
    assert stereo_status("C[C@H](N)O", "CC(N)O") == "DEFINED"
    assert stereo_status("CCO", "CCO") == "UNDEFINED"
    assert tanimoto_hex("f0", "f0") == 1.0 and tanimoto_hex("f0", "0f") == 0.0
