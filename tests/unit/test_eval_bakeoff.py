"""DRAFT_PENDING_30_0 -- tests for the Step 30 bake-off scaffold (registry + paired cluster bootstrap).

Synthetic losses only. Margins, resample counts, confidence levels and seeds used here
are test inputs, not the pre-registered Step 30 values (delta_30 etc. stay PROPOSED_PILOT).
"""
from __future__ import annotations

import inspect
import statistics
from fractions import Fraction

import pytest

from culinarystate.evaluation import bakeoff as bk
from culinarystate.evaluation import splits as sp


def _codes(exc) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


def _persistence(train):
    return lambda row: 1.0


def _global_median(train):
    m = statistics.median(r["y"] for r in train)
    return lambda row: m


# ---------------------------------------------------------------- registry

def test_registry_accepts_plan_rungs_and_freezes():
    reg = bk.ModelRegistry()
    reg.register(bk.ModelSpec("m-d0", "D0", "persistence RF=1", _persistence))
    reg.register(bk.ModelSpec("m-d1", "D1", "global median", _global_median))
    manifest = reg.freeze()
    assert [m["model_id"] for m in manifest["models"]] == ["m-d0", "m-d1"]
    assert manifest["status"].startswith("DRAFT_PENDING") and len(manifest["sha256"]) == 64
    with pytest.raises(bk.BakeoffRefused) as exc:
        reg.register(bk.ModelSpec("m-d2", "D2", "late", _global_median))
    assert "REGISTRY_FROZEN" in _codes(exc)


@pytest.mark.parametrize("spec,code", [
    (bk.ModelSpec("m", "D99", "unknown rung", _persistence), "RUNG_UNKNOWN"),
    (bk.ModelSpec("", "D0", "no id", _persistence), "MODEL_ID_MISSING"),
    (bk.ModelSpec("m", "D10", "deferred neural rung", _persistence), "RUNG_UNKNOWN"),
])
def test_registry_refusals(spec, code):
    with pytest.raises(bk.BakeoffRefused) as exc:
        bk.ModelRegistry().register(spec)
    assert code in _codes(exc)


def test_duplicate_model_id_refused():
    reg = bk.ModelRegistry()
    reg.register(bk.ModelSpec("m", "D0", "a", _persistence))
    with pytest.raises(bk.BakeoffRefused) as exc:
        reg.register(bk.ModelSpec("m", "D1", "b", _global_median))
    assert "MODEL_ID_DUPLICATE" in _codes(exc)


def test_evaluate_requires_frozen_registry_and_fits_on_train_only():
    rows = [{"id": f"r{i}", "g": f"G{i // 2}", "y": float(i)} for i in range(12)]
    split = sp.group_aware_split(rows, id_column="id", group_columns=("g",),
                                 role_fractions={"train": Fraction(1, 2), "test": Fraction(1, 2)},
                                 seed="s", remainder_role="train")
    reg = bk.ModelRegistry()
    seen_train: list[set] = []

    def spy(train):
        seen_train.append({r["id"] for r in train})
        return _global_median(train)

    reg.register(bk.ModelSpec("m-d1", "D1", "global median", spy))
    with pytest.raises(bk.BakeoffRefused) as exc:
        bk.evaluate(reg, split, rows, id_column="id", target=lambda r: r["y"],
                    loss=lambda y, p: abs(y - p), train_role="train", test_role="test")
    assert "REGISTRY_NOT_FROZEN" in _codes(exc)
    reg.freeze()
    out = bk.evaluate(reg, split, rows, id_column="id", target=lambda r: r["y"],
                      loss=lambda y, p: abs(y - p), train_role="train", test_role="test")
    assert seen_train == [set(split.rows("train"))]
    assert set(out["m-d1"]) == set(split.rows("test"))


# ---------------------------------------------------------------- paired cluster bootstrap

def _losses(n_clusters: int = 12, per: int = 3, gain: float = 0.1):
    base, chal, clus = {}, {}, {}
    for c in range(n_clusters):
        for k in range(per):
            rid = f"c{c}-{k}"
            base[rid] = 1.0 + 0.01 * k + 0.02 * c
            chal[rid] = base[rid] - gain - 0.005 * ((c + k) % 3)
            clus[rid] = f"C{c}"
    return base, chal, clus


def _boot(base, chal, clus, **over):
    kw = dict(margin=0.0, n_resamples=500, confidence=0.9, seed="synthetic", weighting="CLUSTER")
    kw.update(over)
    return bk.paired_cluster_bootstrap(base, chal, clus, **kw)


def test_margin_has_no_default():
    params = inspect.signature(bk.paired_cluster_bootstrap).parameters
    for name in ("margin", "n_resamples", "confidence", "seed", "weighting"):
        assert params[name].default is inspect.Parameter.empty, name
        assert params[name].kind is inspect.Parameter.KEYWORD_ONLY, name
    base, chal, clus = _losses()
    with pytest.raises(TypeError):
        bk.paired_cluster_bootstrap(base, chal, clus, n_resamples=10, confidence=0.9, seed="s",  # type: ignore[call-arg]
                                    weighting="CLUSTER")


def test_clear_gain_beats_a_small_margin_and_not_a_large_one():
    base, chal, clus = _losses(gain=0.1)
    small = _boot(base, chal, clus, margin=0.01)
    large = _boot(base, chal, clus, margin=0.5)
    assert small.verdict == "LOWER_BOUND_ABOVE_MARGIN" and large.verdict == "NOT_ABOVE_MARGIN"
    assert small.n_clusters == 12 and small.n_rows == 36
    assert small.lower <= small.estimate <= small.upper
    assert abs(small.estimate - statistics.mean(base[r] - chal[r] for r in base)) < 1e-9


def test_no_gain_is_not_above_a_zero_margin():
    base, chal, clus = _losses(gain=0.0)
    chal = {k: v + (0.01 if int(k[1:].split("-")[0]) % 2 else -0.01) for k, v in base.items()}
    assert _boot(base, chal, clus).verdict == "NOT_ABOVE_MARGIN"


def test_bootstrap_is_deterministic_and_seeded():
    base, chal, clus = _losses()
    a, b = _boot(base, chal, clus), _boot(base, chal, clus)
    assert a == b
    assert _boot(base, chal, clus, seed="other").seed_sha256 != a.seed_sha256


def test_resampling_unit_is_the_cluster():
    base, chal, clus = _losses(n_clusters=2, per=50, gain=0.1)
    res = _boot(base, chal, clus)
    assert res.n_clusters == 2  # 2 clusters, however many rows


def test_cluster_and_row_weighting_differ_on_unbalanced_clusters():
    base = {"a1": 1.0, "a2": 1.0, "a3": 1.0, "b1": 1.0}
    chal = {"a1": 0.0, "a2": 0.0, "a3": 0.0, "b1": 1.0}
    clus = {"a1": "A", "a2": "A", "a3": "A", "b1": "B"}
    assert _boot(base, chal, clus, weighting="CLUSTER").estimate == pytest.approx(0.5)
    assert _boot(base, chal, clus, weighting="ROW").estimate == pytest.approx(0.75)


@pytest.mark.parametrize("over,code", [
    ({"margin": float("nan")}, "MARGIN_INVALID"),
    ({"margin": None}, "MARGIN_INVALID"),
    ({"confidence": 1.0}, "CONFIDENCE_INVALID"),
    ({"n_resamples": 0}, "N_RESAMPLES_INVALID"),
    ({"weighting": "AUTO"}, "WEIGHTING_INVALID"),
    ({"seed": ""}, "SEED_MISSING"),
])
def test_bootstrap_argument_refusals(over, code):
    base, chal, clus = _losses()
    with pytest.raises(bk.BakeoffRefused) as exc:
        _boot(base, chal, clus, **over)
    assert code in _codes(exc)


def test_bootstrap_data_refusals():
    base, chal, clus = _losses()
    with pytest.raises(bk.BakeoffRefused) as exc:
        _boot(base, {k: v for k, v in list(chal.items())[1:]}, clus)
    assert "ROWS_NOT_PAIRED" in _codes(exc)
    with pytest.raises(bk.BakeoffRefused) as exc:
        _boot(base, chal, {k: v for k, v in list(clus.items())[1:]})
    assert "CLUSTER_MISSING" in _codes(exc)
    one = {k: "C0" for k in clus}
    with pytest.raises(bk.BakeoffRefused) as exc:
        _boot(base, chal, one)
    assert "TOO_FEW_CLUSTERS" in _codes(exc)
    bad = dict(base, **{next(iter(base)): float("inf")})
    with pytest.raises(bk.BakeoffRefused) as exc:
        _boot(bad, chal, clus)
    assert "LOSS_NOT_FINITE" in _codes(exc)


def test_result_record_names_its_conventions():
    base, chal, clus = _losses()
    rec = _boot(base, chal, clus, margin=0.02).as_record()
    for key in ("margin", "n_resamples", "confidence", "weighting", "seed_sha256", "interval_rule",
                "n_clusters", "labels"):
        assert key in rec, key
    assert "DIAGNOSTIC_ONLY" in rec["labels"] and "synthetic" not in repr(rec)
