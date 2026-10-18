import pytest

from culinarystate.scoring.calibration import aurc, brier, ece, error_detection_auroc, risk_coverage, unsupported_claim_rate


def test_brier_and_ece():
    assert brier([1.0, 0.0], [1, 0]) == 0.0 and brier([0.5, 0.5], [1, 0]) == 0.25
    r = ece([0.9, 0.9, 0.1, 0.1], [1, 0, 0, 0], n_bins=10)
    # bin 0.9: acc 0.5, conf 0.9 (gap 0.4); bin 0.1: acc 0, conf 0.1 (gap 0.1) -> (2*0.4 + 2*0.1)/4
    assert r["ece"] == pytest.approx(0.25) and len(r["bins"]) == 2 and r["bins"][0]["n"] == 2


def test_risk_coverage_and_aurc():
    rc = risk_coverage([0.9, 0.8, 0.3], [1, 1, 0])
    assert [(p["coverage"], p["risk"]) for p in rc] == [(1 / 3, 0.0), (2 / 3, 0.0), (1.0, 1 / 3)]
    assert aurc([0.9, 0.8, 0.3], [1, 1, 0]) == pytest.approx(1 / 9)
    assert aurc([0.3, 0.8, 0.9], [1, 1, 0]) > aurc([0.9, 0.8, 0.3], [1, 1, 0])     # worse ranking -> larger area


def test_error_detection_auroc():
    assert error_detection_auroc([0.9, 0.8, 0.3], [1, 1, 0]) == 1.0
    assert error_detection_auroc([0.9, 0.8], [1, 1]) is None                        # needs both classes


def test_unsupported_claim_rate():
    claims = [{"supported": True}, {"supported": False}, {"supported": None}]
    assert unsupported_claim_rate(claims) == {"ucr": 0.5, "claims": 3, "judged": 2, "unjudged": 1}
