"""S171 / D-075 M2: 07.A-R1 packet selection (fresh seed, disjoint from v1-v4, v4 strata and quotas). Synthetic."""
from __future__ import annotations

import hashlib

import pytest

from culinarystate.evidence import condition_audit_packet as P


def test_quota_and_seed_match_preregistration():
    assert P.QUOTA == {"S1_temperature_location_stated": 20, "S2_temperature_location_unspecified": 25,
                       "S3_interval": 15, "S4_pressure_or_power": 15, "S5_medium_only": 10, "S6_all_unknown": 15}
    assert sum(P.QUOTA.values()) == 100 and P.SEED_R1 == "step07-condition-audit-R1-2026-11-08"


@pytest.mark.parametrize("cond,expected", [
    ({"pressure": {"raw": "1 bar"}, "temperatures": [{"location": "CORE"}]}, "S4_pressure_or_power"),
    ({"temperatures": [{"location": "CORE", "value": {"status": "POINT"}}]}, "S1_temperature_location_stated"),
    ({"temperatures": [{"location": None, "value": {"status": "RANGE"}}]}, "S3_interval"),
    ({"duration": {"status": "RANGE"}}, "S3_interval"),
    ({"temperatures": [{"location": None, "value": {"status": "POINT"}}]}, "S2_temperature_location_unspecified"),
    ({"medium": "water"}, "S5_medium_only"),
    ({}, "S6_all_unknown"),
])
def test_stratum_rules_as_v4(cond, expected):
    assert P.stratum(cond) == expected


def _pool(n=40):
    return {s: [f"COND-{s[:2]}-{i:03d}" for i in range(n)] for s in P.QUOTA}


def test_select_ranks_by_seed_and_respects_quota():
    pool = _pool()
    out = P.select(pool, seed="s", exclude=frozenset())
    assert len(out) == 100
    for s, q in P.QUOTA.items():
        got = [c for st, c in out if st == s]
        want = sorted(pool[s], key=lambda c: hashlib.sha256(("s" + c).encode()).hexdigest())[:q]
        assert got == want


def test_select_excludes_before_ranking_and_is_disjoint():
    pool = _pool()
    first = P.select(pool, seed="s", exclude=frozenset())
    excl = frozenset(c for _, c in first)
    second = P.select(pool, seed="s", exclude=excl)
    assert len(second) == 100 and not excl & {c for _, c in second}


def test_select_refuses_when_a_stratum_is_too_small():
    pool = _pool(n=12)
    with pytest.raises(ValueError):
        P.select(pool, seed="s", exclude=frozenset())


def test_fmt_point_interval_and_calendar():
    assert P.fmt({"value_type": "POINT", "status": "VALID", "canonical_value": 453.15, "canonical_unit": "K"}) \
        == "POINT/VALID 453.15 K"
    assert P.fmt({"value_type": "INTERVAL", "status": "VALID", "canonical_low": 348.15, "canonical_high": None,
                  "canonical_unit": "K"}) == "INTERVAL/VALID (348.15, +inf) K"
    assert P.fmt({"value_type": "POINT", "status": "AMBIGUOUS", "calendar_unit": "month", "calendar_value": 6.0}) \
        == "POINT/AMBIGUOUS calendar:6.0 month"


def test_manifest_is_counts_only():
    m = P.manifest(rows=[{"stratum": "S1_temperature_location_stated", "source_family": "USDA"}],
                   pool={"S1_temperature_location_stated": ["a", "b"]}, excluded=frozenset({"x"}),
                   fingerprint={"combined_sha256": "f" * 64}, packet_sha={"Kush": "1" * 64, "Parv": "2" * 64})
    text = repr(m)
    assert "'a'" not in text and "'x'" not in text
    assert m["excluded_count"] == 1 and m["n"] == 1 and m["audited_by_humans"] is False
    assert m["status"] == "DRAFT_PENDING_SIGNATURES"
