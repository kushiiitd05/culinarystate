from pathlib import Path

from culinarystate.ner.encoder_tagger import bio_to_spans

ROOT = Path(__file__).resolve().parents[2]


def test_bio_to_spans_matches_training_decode():
    offs = [(0, 1), (2, 6), (7, 12), (13, 17), (17, 18)]
    tags = ["B-QUANTITY", "B-UNIT", "B-FOOD", "I-FOOD", "O"]
    assert bio_to_spans(tags, offs) == [(0, 1, "QUANTITY"), (2, 6, "UNIT"), (7, 17, "FOOD")]
    assert bio_to_spans(["I-FOOD", "I-UNIT"], offs[:2]) == [(0, 1, "FOOD"), (2, 6, "UNIT")]   # lenient I- start
    assert bio_to_spans([], []) == []


def test_runtime_crf_is_the_trained_crf():
    assert (ROOT / "src/culinarystate/ner/crf.py").read_text() == (ROOT / "gpu/ner_tasteset/crf.py").read_text()
