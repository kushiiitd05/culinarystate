"""S166: the Step 17b dry-run report records which code produced it (S163 AI review, prv P2).

S163 ran three full-corpus passes with different auditor files, but every JSON carried the same
``auditor_version`` string, so the provenance lived only in prose. The report now carries a
``code_provenance`` block: the git commit and dirty flag when git is available (null otherwise, as on
vinayak-server, whose copy has no .git), the sha256 of each extraction module and of the tool, and one
hash over every tracked-shape source file. Paths and hashes only; no recipe text or id.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "ZQXSENTINEL"
HEX64 = re.compile(r"[0-9a-f]{64}")


def _tool():
    spec = importlib.util.spec_from_file_location("step17b_rung_a_dryrun", ROOT / "tools/step17b_rung_a_dryrun.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _records():
    return iter([{"recipe_id": f"SYN-{SENTINEL}-{i}", "source_family": "FOODCOM",
                  "ingredient_lines": [f"200 g {SENTINEL} onion"],
                  "steps": [f"Fry 200 g {SENTINEL}onion for 5 minutes, then bake at 180 degF for 20 minutes."]}
                 for i in range(3)])


def _run(tmp_path, tool):
    out = tmp_path / "dry.json"
    assert tool.main(["--seed", "7", "--sample-size", "3", "--out", str(out), "--no-baseline-check"],
                     record_source=lambda fams, root: _records()) == 0
    return out.read_text(encoding="utf-8")


def test_report_records_the_auditor_hash_and_every_extraction_module(tmp_path):
    text = _run(tmp_path, _tool())
    assert SENTINEL not in text and "SYN-" not in text
    prov = json.loads(text)["code_provenance"]
    files = {row["path"]: row["sha256"] for row in prov["code_sha256"]}  # list: the counts-only guard bans path keys
    auditor = "src/culinarystate/extraction/auditor.py"
    assert files[auditor] == hashlib.sha256((ROOT / auditor).read_bytes()).hexdigest()
    expected = {p.relative_to(ROOT).as_posix() for p in (ROOT / "src/culinarystate/extraction").glob("*.py")}
    expected.add("tools/step17b_rung_a_dryrun.py")
    assert set(files) == expected
    assert all(HEX64.fullmatch(v) for v in files.values())
    assert HEX64.fullmatch(prov["src_tree_sha256"])


def test_git_commit_matches_head_when_git_is_available(tmp_path):
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
    prov = json.loads(_run(tmp_path, _tool()))["code_provenance"]
    if head.returncode == 0:
        assert prov["git_commit"] == head.stdout.strip()
        assert isinstance(prov["git_dirty"], bool)
    else:
        assert prov["git_commit"] is None and prov["git_dirty"] is None


def test_without_git_the_hashes_still_pin_the_code(tmp_path, monkeypatch):
    tool = _tool()

    def no_git(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(tool.subprocess, "run", no_git)
    prov = json.loads(_run(tmp_path, tool))["code_provenance"]
    assert prov["git_commit"] is None and prov["git_dirty"] is None
    files = {row["path"]: row["sha256"] for row in prov["code_sha256"]}
    assert HEX64.fullmatch(files["src/culinarystate/extraction/auditor.py"])


def test_src_tree_hash_changes_when_any_source_file_changes(tmp_path):
    tool = _tool()
    src = tmp_path / "src/culinarystate/x"
    src.mkdir(parents=True)
    (src / "a.py").write_text("A = 1\n")
    before = tool.src_tree_sha256(tmp_path)
    (src / "a.py").write_text("A = 2\n")
    assert tool.src_tree_sha256(tmp_path) != before
