"""S118: repaired Food.com Gold (v1.1) is structurally valid, S117 stays unchanged, and no recipe text is tracked by git."""
import json
import subprocess
from pathlib import Path

import pytest

from culinarystate.annotation.gold import to_events, validate_gold
from culinarystate.state_graph.engine import replay

ROOT = Path(__file__).resolve().parents[1]
V0 = ROOT / "annotation" / "gold" / "foodcom_ai_assisted"
V1 = ROOT / "annotation" / "gold" / "foodcom_ai_assisted_v1_1"
have = pytest.mark.skipif(not (V1 / "Kush").exists(), reason="local-only Food.com gold not present")


@have
def test_v1_1_all_20_validate_replay_and_deterministic():
    files = sorted((V1 / "Kush").glob("*.json"))
    assert len(files) == 20
    for f in files:
        d = json.loads(f.read_text())
        assert d["status"] == "DONE" and validate_gold(d) == []
        r1, r2 = replay(to_events(d)), replay(to_events(d))
        assert list(r1.issues) == [] and r1.sha256() == r2.sha256()


@have
def test_v1_1_has_no_mechanical_lineage_names_and_kush_parv_identical_events():
    for f in (V1 / "Kush").glob("*.json"):
        d = json.loads(f.read_text())
        assert "mixture step" not in json.dumps(d)
        p = json.loads((V1 / "Parv" / f.name.replace(".Kush.", ".Parv.")).read_text())
        assert [s["events"] for s in p["steps"]] == [s["events"] for s in d["steps"]]
        assert "AI_REAUTHORED_SOURCE_GROUNDED" in d["notes"] and "HUMAN_REVIEW_PENDING" in d["notes"]
        assert "AI_ASSISTED_HUMAN_REVIEWED" not in d["notes"].split("Promote to")[0].split("PROVENANCE:")[1].split(";")[0]


@have
def test_s117_version_is_preserved():
    assert len(list((V0 / "Kush").glob("*.json"))) == 20
    assert "UNRESOLVED_REFERENCE" in (V0 / "conversion_log.csv").read_text()


def test_no_foodcom_recipe_text_is_tracked():
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    bad = [t for t in tracked if t.startswith("annotation/gold/foodcom_ai_assisted") or t.endswith("foodcom_dropped_event_audit.csv")
           or "evidence_first_expansion/Kush_all_20" in t or "evidence_first_expansion/Parv_all_20" in t]
    assert bad == []
