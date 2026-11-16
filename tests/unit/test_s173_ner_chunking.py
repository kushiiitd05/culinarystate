"""S173: corpus NER chunking and span-to-line mapping (no torch needed)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("cni", ROOT / "gpu/ner_bench/corpus_ner_infer.py")
CNI = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CNI)


def test_chunks_follow_training_format_and_offsets():
    ch = CNI.chunk_lines(["2 carrots", "1 tbsp oil", "salt"], 2)
    assert [c[0] for c in ch] == [0, 2]
    first, text, offs = ch[0]
    assert text == "2 carrots\n1 tbsp oil\n" and [text[a:b] for a, b in offs] == ["2 carrots", "1 tbsp oil"]


def test_spans_mapped_to_lines_with_local_offsets():
    first, text, offs = CNI.chunk_lines(["2 carrots", "1 tbsp oil"], 5)[0]
    spans = [(0, 1, "QUANTITY"), (2, 9, "FOOD"), (10, 11, "QUANTITY"), (12, 16, "UNIT"), (17, 20, "FOOD")]
    rows = CNI.spans_by_line(spans, offs, text, first)
    assert rows[0] == [[0, 1, "QUANTITY", "2"], [2, 9, "FOOD", "carrots"]]
    assert rows[1] == [[0, 1, "QUANTITY", "1"], [2, 6, "UNIT", "tbsp"], [7, 10, "FOOD", "oil"]]
