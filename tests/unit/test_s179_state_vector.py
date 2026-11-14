"""T6: named, masked state vector; UNKNOWN is mask 0, Δ only on dims known in both."""
from culinarystate.composition import state_vector as SV


def _ctx(salt, phase="AQUEOUS"):
    return {"salt_present": {"v": salt}, "acid_present": {"v": "NO_RECOGNIZED_MARKER"},
            "lipid_present": {"v": "NO_RECOGNIZED_MARKER"}, "aqueous_present": {"v": True},
            "contact_phase": {"v": phase}, "member_composition": {"v": {}}}


def _enc(salt, family="WET_HEAT"):
    return SV.encode(family=family, step_position=0.5, n_inputs=2, n_members=3, history={"CUT"}, ctx=_ctx(salt))


def test_lengths_and_names_align():
    v, m = _enc(True)
    assert len(v) == len(m) == len(SV.dims())


def test_unknown_is_masked_not_zero():
    names = [n for _, n in SV.dims()]
    v, m = _enc(None)
    i = names.index("salt_present")
    assert m[i] == 0 and v[i] == 0.0
    v2, m2 = _enc("NO_RECOGNIZED_MARKER")
    assert m2[i] == 1 and v2[i] == 0.0


def test_delta_names_the_change_and_skips_unknown():
    assert SV.delta(_enc("NO_RECOGNIZED_MARKER"), _enc(True)) == {"salt_present": 1.0}
    assert SV.delta(_enc(None), _enc(True)) == {}


def test_similarity_identical_is_one():
    assert SV.similarity(_enc(True), _enc(True)) == 1.0
