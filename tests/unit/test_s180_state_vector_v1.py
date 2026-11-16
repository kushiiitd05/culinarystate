"""S180: STATE_VECTOR_V1 exposes the physics history State v2 already computes.

V0 carried only ``temperature_C`` and ``duration_min`` in its Q block - 2 of 51 dims - while State v2
had thermal dose, cumulative dose, hot-aqueous and hot-fat minutes, food temperature, moisture cap,
lid state and an oxygen proxy sitting unused. So V0's notion of "time" was step position plus a raw
stated duration, not accumulated dose.

V1 adds those as named dims. **V0 is left exactly as it is**, because the committed step-9 retrieval
diagnostic was measured on it.

Nothing is learned and nothing is estimated: every new dim is a cell State v2 already produces, and
an absent cell stays mask 0 (UNKNOWN), distinct from a known zero.
"""
from __future__ import annotations

from culinarystate.composition import state_vector as SV

CTX = {
    "salt_present": {"v": True}, "acid_present": {"v": None, "u": "NO_MARKER"},
    "lipid_present": {"v": False}, "aqueous_present": {"v": True},
    "contact_phase": {"v": "AQUEOUS"}, "member_composition": {"v": {}},
}
BASE = dict(family="WET_HEAT", step_position=0.5, n_inputs=2, n_members=2,
            history={"HEATED"}, ctx=CTX, temperature_c=100.0, duration_min=20.0)


def test_v0_is_unchanged_at_51_dims():
    """The step-9 diagnostic was measured on V0; it must not move under us."""
    assert len(SV.dims()) == 51


def test_v1_adds_dims_and_keeps_v0_names_as_a_prefix():
    v0 = [n for _, n in SV.dims()]
    v1 = [n for _, n in SV.dims_v1()]
    assert len(v1) > len(v0)
    assert v1[: len(v0)] == v0, "V1 must extend V0, not reorder it"


def test_v1_q_block_is_much_larger_than_v0_two_dims():
    q0 = sum(1 for b, _ in SV.dims() if b == "Q")
    q1 = sum(1 for b, _ in SV.dims_v1() if b == "Q")
    assert q0 == 2
    assert q1 >= 9


def test_every_new_dim_is_named_and_unique():
    names = [n for _, n in SV.dims_v1()]
    assert len(names) == len(set(names))
    assert all(n and not n.startswith("dim") for n in names)


def test_new_dims_are_in_known_blocks():
    assert {b for b, _ in SV.dims_v1()} <= {"G", "C", "Q", "Y"}


def test_encode_v1_length_matches_dims_v1():
    v, m = SV.encode_v1(**BASE)
    assert len(v) == len(m) == len(SV.dims_v1())


def test_physics_history_is_carried_when_given():
    v, m = SV.encode_v1(**BASE, cumulative_dose_min=30.0, hot_aqueous_minutes=20.0,
                        hot_fat_minutes=0.0, heat_steps_so_far=2)
    names = [n for _, n in SV.dims_v1()]
    for name in ("cumulative_thermal_dose_min/60", "hot_aqueous_minutes/60", "hot_fat_minutes/60"):
        assert m[names.index(name)] == 1, f"{name} should be known"
    assert v[names.index("cumulative_thermal_dose_min/60")] == 0.5
    assert v[names.index("hot_aqueous_minutes/60")] == 20.0 / 60


def test_known_zero_is_not_unknown():
    """hot_fat_minutes = 0 means no hot fat, which is a fact, not a missing value."""
    v, m = SV.encode_v1(**BASE, hot_fat_minutes=0.0)
    names = [n for _, n in SV.dims_v1()]
    i = names.index("hot_fat_minutes/60")
    assert m[i] == 1 and v[i] == 0.0


def test_absent_physics_stays_masked_unknown():
    v, m = SV.encode_v1(**BASE)
    names = [n for _, n in SV.dims_v1()]
    for name in ("cumulative_thermal_dose_min/60", "food_T_typical_C/100", "moisture_cap_C/100"):
        assert m[names.index(name)] == 0, f"{name} must be UNKNOWN when no cell gives it"


def test_lid_and_oxygen_are_booleans_not_invented_numbers():
    v, m = SV.encode_v1(**BASE, lid_covered=True, oxygen_limited=False)
    names = [n for _, n in SV.dims_v1()]
    assert (v[names.index("lid_covered")], m[names.index("lid_covered")]) == (1.0, 1)
    assert (v[names.index("oxygen_limited")], m[names.index("oxygen_limited")]) == (0.0, 1)


def test_similarity_and_delta_work_on_v1_vectors():
    a = SV.encode_v1(**BASE, cumulative_dose_min=30.0)
    b = SV.encode_v1(**BASE, cumulative_dose_min=60.0)
    assert 0.0 <= SV.similarity(a, b) <= 1.0
    d = SV.delta(a, b)
    assert "cumulative_thermal_dose_min/60" in d
    assert d["cumulative_thermal_dose_min/60"] == 0.5


def test_delta_ignores_dims_unknown_on_either_side():
    a = SV.encode_v1(**BASE, cumulative_dose_min=30.0)
    b = SV.encode_v1(**BASE)
    assert "cumulative_thermal_dose_min/60" not in SV.delta(a, b)


def test_block_weights_cover_every_v1_block():
    assert {b for b, _ in SV.dims_v1()} <= set(SV.BLOCK_WEIGHTS)


def test_v1_is_still_retrieval_only_and_unvalidated():
    assert "DIAGNOSTIC" in SV.V1_STATUS or "RETRIEVAL" in SV.V1_STATUS
