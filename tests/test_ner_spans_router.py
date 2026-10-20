"""S119 Part XX: candidate spans, train-only / out-of-fold features, B/I projection, metadata dropout, calibrator, router, statistics."""
import numpy as np

from culinarystate.ner import router as R
from culinarystate.ner import spans as S


def test_candidates_cover_all_ngrams_up_to_6_and_ignore_labels():
    toks = S.tokens("2 cups red chilli powder , finely chopped extra")
    c = S.candidate_spans(toks)
    assert all(1 <= j - i <= 6 for i, j in c) and (2, 5) in c and len(c) == sum(min(6, len(toks) - i) for i in range(len(toks)))


def test_crossfit_never_uses_own_fold_and_test_uses_full_train():
    docs = [(f"1 cup item{i}", [(6, 11 + len(str(i)), "FOOD")]) for i in range(20)]
    feats, fold = S.crossfit_features(docs, ["FOOD"], k=5, seed=1)
    for i in range(20):
        cands, X = feats[i]
        toks = S.tokens(docs[i][0])
        k = next(n for n, (a, b) in enumerate(cands) if (a, b) == (2, 3))             # the item token's own span
        assert X[k][0] == 0.0                                                         # exact flag OFF: its own surface lives only in its fold
    full = S.Gazetteer.build(docs, ["FOOD"])
    assert full.features("item3")[0] == 1.0                                           # test-time (full-train) build knows it


def test_gazetteer_fuzzy_and_ext_alias_and_unseen():
    g = S.Gazetteer.build([("x flour", [(2, 7, "FOOD")])], ["FOOD"], {"FOOD": {"kosher salt"}})
    assert g.features("flour")[0] == 1.0 and 0.0 < g.features("flours")[2] < 1.0 and g.features("kosher salt")[3] == 1.0
    assert g.features("zzz")[0] == 0.0 and np.isfinite(g.features("zzz")).all()


def test_projection_has_separate_B_and_I_slots_and_metadata_dropout():
    cands, X = [(0, 3)], np.array([[1.0, 2.0]], np.float32)
    m = S.project_to_tokens(4, cands, X)
    assert m.shape == (4, 4) and list(m[0]) == [1, 2, 0, 0] and list(m[1]) == [0, 0, 1, 2] and list(m[2]) == [0, 0, 1, 2] and not m[3].any()
    assert not S.mask_metadata(m, np.random.RandomState(0), p=1.0).any() and (S.mask_metadata(m, np.random.RandomState(0), p=0.0) == m).all()


def test_risk_control_threshold_bounds_accept_error_and_handles_empty():
    rng = np.random.RandomState(0)
    s = rng.rand(4000)
    c = (rng.rand(4000) < s).astype(int)                                              # calibrated by construction
    tau = R.risk_control_threshold(s, c, 0.05)
    keep = s >= tau
    assert keep.any() and (1 - c[keep]).mean() <= 0.06
    assert R.risk_control_threshold(np.array([0.5, 0.4]), np.array([0, 0]), 0.02) == float("inf")


def test_router_four_outcomes_and_nil_behaviour():
    f = lambda pe, pl, cand: R.route(pe, pl, 0.9, 0.8, 0.3, cand)
    assert f(0.95, 0.9, True) == R.ACCEPT and f(0.95, 0.2, False) == R.NOVEL and f(0.95, 0.2, True) == R.REVIEW
    assert f(0.5, 0.9, True) == R.REVIEW and f(0.1, 0.9, True) == R.REJECT


def test_calibrator_is_cross_fitted_and_outputs_probabilities():
    rng = np.random.RandomState(1)
    X = rng.randn(600, 3)
    y = (X[:, 0] + 0.5 * rng.randn(600) > 0).astype(int)
    model, iso, oof = R.fit_calibrator(X, y)
    p = R.calibrated(model, iso, X)
    assert ((p >= 0) & (p <= 1)).all() and np.corrcoef(oof, y)[0, 1] > 0.5


def test_holm_and_paired_bootstrap_and_promotion_rule():
    assert R.holm([0.001, 0.04, 0.2]) == [True, False, False]
    groups = [i // 2 for i in range(100)]
    d = R.paired_grouped_bootstrap([0.91] * 100, [0.90] * 100, groups)
    assert abs(d["delta"] - 0.01) < 1e-9 and d["low"] > 0 and R.promote(d, True)
    assert not R.promote(d, False) and not R.promote({"delta": 0.001, "low": 0.0005}, True)
