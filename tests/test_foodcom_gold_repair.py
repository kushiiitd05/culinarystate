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
J = V1 / "foodcom_v1_1_joint.json"
have = pytest.mark.skipif(not J.exists(), reason="local-only Food.com gold not present")


@have
def test_v1_1_all_20_validate_replay_and_deterministic():
    recipes = json.loads(J.read_text())["recipes"]
    assert len(recipes) == 20 and not (V1 / "Kush").exists()
    for d in recipes:
        assert d["annotator"] == "JOINT" and d["status"] == "DONE" and validate_gold(d) == []
        r1, r2 = replay(to_events(d)), replay(to_events(d))
        assert list(r1.issues) == [] and r1.sha256() == r2.sha256()


@have
def test_v1_1_is_one_joint_bundle_with_pending_review_provenance():
    b = json.loads(J.read_text())
    assert b["annotator"] == "JOINT" and b["n_recipes"] == 20
    assert "AI_REAUTHORED_SOURCE_GROUNDED" in b["provenance"] and "HUMAN_REVIEW_PENDING" in b["provenance"]
    for d in b["recipes"]:
        assert "mixture step" not in json.dumps(d)
        assert "HUMAN_REVIEW_PENDING" in d["notes"]


@have
def test_s117_version_is_preserved():
    assert len(list((V0 / "Kush").glob("*.json"))) == 20
    assert "UNRESOLVED_REFERENCE" in (V0 / "conversion_log.csv").read_text()


def test_no_foodcom_recipe_text_is_tracked():
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    bad = [t for t in tracked if t.startswith("annotation/gold/foodcom_ai_assisted") or t.endswith("foodcom_dropped_event_audit.csv")
           or "evidence_first_expansion/Kush_all_20" in t or "evidence_first_expansion/Parv_all_20" in t]
    assert bad == []
