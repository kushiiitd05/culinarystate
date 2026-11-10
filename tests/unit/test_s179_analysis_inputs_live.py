"""S179: the corpus 'can say' -> EVD coverage -> EVD reproducibility chain reads only live inputs (physics v06,
router census 0.4.1) and writes new v2 files beside the kept v1 files (a re-run never overwrites a committed output)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from culinarystate import governance_superseded as G  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_s179_{name}", ROOT / f"tools/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_can_say_reads_the_v06_censuses_and_records():
    m = _load("s178_analysis_corpus_can_say")
    assert m.LAYER_TAG == "S179 v06"
    paths = m.all_input_paths(ROOT)
    assert paths and all("S179_v06" in p or "S179v06" in p for p in paths), paths
    G.assert_not_superseded(paths, root=ROOT)


def test_can_say_render_writes_v2_names():
    m = _load("s178_analysis_corpus_can_say_render")
    assert m.OUT_JSON == "corpus_can_say_v2.json" and m.OUT_MD == "corpus_can_say_v2.md"
    assert m.FIG_NAMES and all(n.endswith("_v2") for n in m.FIG_NAMES)


def test_evd_coverage_reads_live_inputs_and_writes_v2_names():
    m = _load("s178_evd_coverage")
    assert m.CAN_SAY == "reports/s178/analysis/corpus_can_say_v2.json"
    assert m.CENSUS_FULL.endswith("_full_S179b.json") and m.CENSUS_1000.endswith("_1000_S179b.json")
    G.assert_not_superseded([m.CAN_SAY, m.CENSUS_FULL, m.CENSUS_1000], root=ROOT)
    assert m.OUTPUT_NAMES and all("_v2." in n for n in m.OUTPUT_NAMES)


def test_evd_repro_record_lists_live_inputs_and_the_v2_coverage_outputs():
    m = _load("s178_evd_repro_record")
    G.assert_not_superseded(m.INPUTS, root=ROOT)
    assert "reports/s178/analysis/corpus_can_say_v2.json" in m.INPUTS
    cov = [o for o in m.OUTPUTS if "coverage" in o]
    assert cov and all("_v2." in o for o in cov)
    assert m.RECORD_NAMES == ("evd_reproducibility_record_v2.json", "evd_reproducibility_record_v2.md")
