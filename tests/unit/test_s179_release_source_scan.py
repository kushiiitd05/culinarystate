"""Bounded-memory scanner detects local source overlap without exporting source text."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("release_scan", Path(__file__).parents[2] / "tools/s179_release_source_scan.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


def test_unicode_case_normalization_and_counts_only_findings():
    index = scan.artifact_index({"draft": "one two THREE four five"}, window=3)
    out = scan.match_text("ONE two three four", index, window=3)
    assert len(out) == 2 and all(len(digest) == 64 for _, digest in out)
    assert {name for name, _ in out} == {"draft"}


def test_short_and_different_text_do_not_match():
    index = scan.artifact_index({"draft": "one two three four"}, window=3)
    assert scan.match_text("one two", index, window=3) == set()
    assert scan.match_text("one two different four", index, window=3) == set()


def test_html_visible_text_excludes_style_and_script():
    assert scan.visible_html('<style>hidden</style><h1>one &amp; two</h1><script>secret</script>') == 'one & two'
