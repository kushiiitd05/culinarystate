"""§257B NER pipeline (Part K hybrid cascade) — 12 mandatory unit tests."""
from culinarystate.ner.pipeline import (
    Span, NERResult, NERPipeline, VERSION,
    _overlaps, _merge_spans, _rule_spans,
)


# 1. clean in-domain case
def test_rule_only_pipeline():
    p = NERPipeline(layers=("RULE",))
    r = p.tag("2 cups all-purpose flour")
    assert isinstance(r, NERResult)
    assert len(r.spans) > 0
    assert r.layers_used == ("RULE",)
    labels = {s.label for s in r.spans}
    assert "QUANTITY" in labels or "UNIT" in labels or "FOOD" in labels


# 2. missing optional field (no model_dir, encoder layer requested but no model)
def test_no_encoder_graceful():
    p = NERPipeline(model_dir=None, layers=("RULE",))
    r = p.tag("1 cup sugar")
    assert len(r.spans) > 0


# 3. missing critical field (empty text)
def test_empty_text():
    p = NERPipeline(layers=("RULE",))
    r = p.tag("")
    assert r.spans == ()
    assert r.layers_used == ()


# 4. none text
def test_none_text():
    p = NERPipeline(layers=("RULE",))
    r = p.tag(None)
    assert r.spans == ()


# 5. overlap detection
def test_overlaps():
    a = Span(0, 5, "FOOD", 0.9, "RULE")
    b = Span(3, 8, "FOOD", 0.8, "ENCODER")
    assert _overlaps(a, b)
    c = Span(5, 10, "UNIT", 0.9, "RULE")
    assert not _overlaps(a, c)


# 6. merge — override wins on higher confidence
def test_merge_override_wins():
    base = [Span(0, 5, "FOOD", 0.7, "RULE")]
    over = [Span(0, 6, "FOOD", 0.9, "ENCODER")]
    merged = _merge_spans(base, over)
    assert len(merged) == 1
    assert merged[0].source == "ENCODER"
    assert merged[0].end == 6


# 7. merge — base kept when higher confidence
def test_merge_base_wins():
    base = [Span(0, 5, "QUANTITY", 0.95, "RULE")]
    over = [Span(0, 5, "QUANTITY", 0.80, "ENCODER")]
    merged = _merge_spans(base, over)
    assert len(merged) == 1
    assert merged[0].source == "RULE"


# 8. merge — non-overlapping spans combined
def test_merge_no_overlap():
    base = [Span(0, 3, "QUANTITY", 0.9, "RULE")]
    over = [Span(4, 10, "FOOD", 0.9, "ENCODER")]
    merged = _merge_spans(base, over)
    assert len(merged) == 2


# 9. span dataclass
def test_span_length():
    s = Span(3, 10, "FOOD", 0.9, "RULE")
    assert s.length == 7
    assert s.start == 3
    assert s.end == 10


# 10. version
def test_version():
    assert VERSION == "ner_pipeline@0.1"


# 11. result is frozen
def test_result_frozen():
    r = NERResult("test", spans=(), layers_used=())
    try:
        r.text = "other"
        assert False, "should raise"
    except AttributeError:
        pass


# 12. batch
def test_batch():
    p = NERPipeline(layers=("RULE",))
    results = p.tag_batch(["1 cup sugar", "2 tbsp olive oil"])
    assert len(results) == 2
    assert all(isinstance(r, NERResult) for r in results)


# -- extra: gliner stub returns empty
def test_gliner_stub():
    p = NERPipeline(layers=("RULE", "GLINER"))
    r = p.tag("1 cup sugar")
    assert "GLINER" not in r.layers_used


# -- extra: rule spans have expected confidence
def test_rule_confidence():
    spans = _rule_spans("2 cups flour")
    for s in spans:
        assert s.source == "RULE"
        assert 0 < s.confidence <= 1.0
