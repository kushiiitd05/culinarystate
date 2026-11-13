"""T3-C09-R1: NER (frozen ckpt 582c056a spans) vs Rung A lexicon mention agreement, counts-only."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("nva", ROOT / "tools" / "s179_ner_vs_runga_agreement.py")
nva = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nva)


class FakeMatch:
    def __init__(self, length: int) -> None:
        self.length = length


class FakeLex:
    """Knows 'sugar' and 'olive oil' only."""
    fingerprint = "fake"

    def food_at(self, words, i):
        if words[i] == "sugar":
            return FakeMatch(1)
        if words[i] == "olive" and i + 1 < len(words) and words[i + 1] == "oil":
            return FakeMatch(2)
        return None


def fake_tokens(text):
    out, pos = [], 0
    for w in text.split(" "):
        out.append((pos, pos + len(w), w.lower()))
        pos += len(w) + 1
    return out


def _line(text, spans, model=nva.EXPECTED_MODEL):
    return json.dumps({"recipe_id": "X", "line_index": 0, "text": text, "spans": spans, "model": model})


def _write(tmp_path: Path, lines) -> Path:
    p = tmp_path / "ner_FOODCOM_S174.jsonl"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def test_counts_overlap_missed_and_lexicon_empty_lines(tmp_path):
    p = _write(tmp_path, [
        _line("1 cup sugar", [[0, 1, "QUANTITY", "1"], [6, 11, "FOOD", "sugar"]]),
        _line("2 tbsp olive oil", [[7, 16, "FOOD", "olive oil"]]),
        _line("3 tamarind pods", [[2, 10, "FOOD", "tamarind"]]),
    ])
    res, missed, extra = nva.run_file(p, FakeLex(), fake_tokens)
    c = res["counts"]
    assert c["lines"] == 3 and c["ner_food_spans"] == 3
    assert c["ner_food_exact_boundary"] == 2 and c["ner_food_missed_no_overlap"] == 1
    assert not any(k.startswith("gold_") for k in c)
    assert c["lines_lexicon_empty_ner_food"] == 1 and c["ner_food_spans_in_lexicon_empty_lines"] == 1
    assert missed == {"tamarind": 1}
    assert res["rates_pct"]["ner_food_covered_by_a_lexicon_span"] == pytest.approx(66.667)


def test_refuses_spans_from_another_model(tmp_path):
    p = _write(tmp_path, [_line("1 cup sugar", [[6, 11, "FOOD", "sugar"]], model="deadbeef")])
    with pytest.raises(ValueError, match="model"):
        nva.run_file(p, FakeLex(), fake_tokens)


def test_record_has_no_text_or_ids(tmp_path):
    p = _write(tmp_path, [_line("3 tamarind pods", [[2, 10, "FOOD", "tamarind"]])])
    res, _, _ = nva.run_file(p, FakeLex(), fake_tokens)
    flat = json.dumps(res)
    assert "tamarind" not in flat and '"X"' not in flat


def test_family_from_filename():
    assert nva.family_of(Path("ner_GUTENBERG_SEGMENT_S174.jsonl")) == "GUTENBERG_SEGMENT"
    assert nva.family_of(Path("ner_FOODCOM_S174.jsonl")) == "FOODCOM"
