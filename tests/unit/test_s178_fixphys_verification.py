"""S178 FIX-PHYS: SCI-A m7 / m9 on the verification pack (independence classes, V14 gated on the Stefan trend, V16 short-time FD,
V17 zone-node dose against a dense reference, V18 dose-rule biases)."""
from __future__ import annotations

import pytest

from culinarystate.simulation import phys_verification as V


def test_every_check_has_an_independence_class_and_the_reviewer_split_holds():
    assert set(V.INDEPENDENCE) == {f"V{i:02d}" for i in range(1, 19)}
    assert set(V.INDEPENDENCE.values()) <= set(V.INDEPENDENCE_CLASSES)
    independent = {k for k, v in V.INDEPENDENCE.items() if v == "INDEPENDENT"}
    assert {"V01", "V02", "V04", "V07", "V08", "V09", "V10", "V15"} <= independent  # SCI-A's independent eight
    assert not {"V03", "V05", "V06", "V11", "V12", "V13", "V14"} & independent         # identities, self-consistency, loose, recalled
    assert V.check_lumped_limit()["independence"] == "INDEPENDENT" and V.check_plank_identities()["independence"] == "IDENTITY"


def test_counts_are_reported_by_class():
    checks = [{"id": "V01", "passed": True, "independence": "INDEPENDENT"}, {"id": "V03", "passed": True, "independence": "IDENTITY"},
              {"id": "V14", "passed": False, "independence": "LOOSE_TOLERANCE"}]
    c = V.independence_counts(checks)
    assert c["INDEPENDENT"] == {"checks": 1, "passed": 1} and c["LOOSE_TOLERANCE"] == {"checks": 1, "passed": 0}


def test_v14_fails_when_the_stefan_trend_is_reversed(monkeypatch):
    table = {0.4: (100.0, 99.0), 0.2: (100.0, 90.0)}  # error grows as Ste falls: the wrong trend, both within 25 %
    monkeypatch.setattr(V, "stefan_enthalpy_time", lambda ste: table[ste])
    r = V.check_plank_vs_stefan_enthalpy(stes=(0.4, 0.2))
    assert r["max_rel_error"] <= r["tolerance"] and not r["error_decreases_with_stefan_number"] and not r["passed"]


def test_v13_says_identity_not_mirror():
    what = V.check_plank_identities()["what"]
    assert "reduces to Plank's form" in what and "mirror" not in what


def test_v16_short_time_front_against_fd_passes_and_can_fail(monkeypatch):
    r = V.check_short_time_front_vs_fd(n=200, steps_per_unit=50000.0)
    assert r["passed"] and r["independence"] == "INDEPENDENT" and r["n_cases"] == 12
    real = V.PD.slab_theta
    monkeypatch.setattr(V.PD, "slab_theta", lambda xi, fo, bi, **kw: real(xi, fo=fo, bi=bi, **kw) * (1.01 if fo < 0.02 else 1.0))
    assert not V.check_short_time_front_vs_fd(n=200, steps_per_unit=50000.0)["passed"]


def test_v17_v18_dose_rules_against_the_dense_reference():
    v17, v18 = V.check_zone_dose_vs_dense_reference(), V.check_dose_rule_biases()
    assert v17["passed"] and v17["max_rel_error"] < 5e-3
    assert v18["passed"] and v18["volume_avg_t_bias_sign"] == "NEGATIVE" and v18["inequality_exceeds_twice_the_bias"]
    assert all(abs(c["zone_mean_bias"]) < 5e-3 and c["volume_avg_t_bias"] < 0 for c in v18["bias_by_case"].values())


def test_version_bumped():
    assert V.VERSION == "phys-verification-1.1.0-draft" and V.VERSION_V10 == "phys-verification-1.0.0-draft"
