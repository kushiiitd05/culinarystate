import csv
from pathlib import Path

import pytest

from culinarystate.lineage.wilson import wilson_interval, wilson_lower

REPO = Path(__file__).resolve().parents[2]
THR = REPO / "registry" / "preregistered_thresholds_v1.csv"


@pytest.mark.parametrize("k,n,lb", [(143, 150, 0.9068), (142, 150, 0.8983), (59, 60, 0.9114), (58, 60, 0.8864), (57, 60, 0.8630)])
def test_prereg_figures(k, n, lb):
    assert round(wilson_lower(k, n), 4) == lb


def test_figures_present_in_csv_text():
    rows = {r["threshold_id"] if "threshold_id" in r else list(r.values())[0]: r for r in csv.DictReader(THR.open())}
    t4 = " ".join(rows["THR-08A-04"].values())
    t17 = " ".join(rows["THR-08A-17"].values())
    for s in ("0.9068", "0.8983"):
        assert s in t4
    for s in ("0.9114", "0.8864", "0.8630"):
        assert s in t17


def test_interval_contains_point_and_bounds():
    lo, hi = wilson_interval(59, 60)
    assert 0 <= lo < 59 / 60 <= hi <= 1
    assert lo == wilson_lower(59, 60)


def test_edge_cases():
    assert wilson_interval(0, 0) == (0.0, 1.0)
    assert wilson_lower(10, 10) < 1.0
    with pytest.raises(ValueError):
        wilson_lower(5, 4)
    with pytest.raises(ValueError):
        wilson_lower(-1, 4)
