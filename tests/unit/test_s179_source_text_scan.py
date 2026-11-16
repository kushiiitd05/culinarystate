"""Local source-text scan: hashes and locations only, never matched excerpts."""
import json

import pytest

from tools.s179_source_text_scan import scan, source_strings


def test_detects_normalized_copy_without_disclosing_source_words():
    secret = "Combine the finely diced onions with freshly ground pepper and simmer gently until translucent."
    report = scan({"private.jsonl": [secret]}, {"draft.md": secret.upper()}, window=12)
    assert report["status"] == "POTENTIAL_SOURCE_TEXT_MATCHES"
    assert report["matched_windows"] > 0
    assert "finely" not in json.dumps(report).lower()
    assert report["findings"][0]["artifact"] == "draft.md"


def test_does_not_join_separate_recipe_strings():
    report = scan({"private": ["one two three", "four five six"]},
                  {"draft": "one two three four five six"}, window=6)
    assert report["matched_windows"] == 0


def test_repeated_source_windows_keep_all_source_locations():
    text = "one two three four five six"
    report = scan({"a": [text], "b": [text]}, {"draft": text}, window=6)
    assert report["findings"][0]["source_paths"] == ["a", "b"]
    assert report["matched_windows"] == 1


def test_zero_matches_is_limited_scan_not_release_clearance():
    report = scan({"a": ["one two three four five six"]},
                  {"draft": "completely different words here today please"}, window=6)
    assert report["status"] == "NO_MATCHES_IN_SUPPLIED_SOURCES_ONLY"
    assert report["release_clearance"] is False


def test_nested_json_strings_and_non_mutation():
    doc = {"steps": ["one two", {"text": "three four"}], "n": 3}
    before = json.dumps(doc)
    assert list(source_strings(doc)) == ["one two", "three four"]
    assert json.dumps(doc) == before


@pytest.mark.parametrize("window", [0, -1, True, 1.2])
def test_invalid_window_refused(window):
    with pytest.raises(ValueError):
        scan({}, {}, window=window)
