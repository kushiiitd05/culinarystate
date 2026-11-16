"""S175 guard: nothing under data/ may be tracked by git (D-003 BBC stays on the Mac; the repo is public)."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_tracked_files_under_data():
    out = subprocess.run(["git", "ls-files", "data"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert out.strip() == "", f"tracked files under data/: {out.splitlines()[:5]}"


def test_gitignore_lists_derived_records():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/derived/" in text
