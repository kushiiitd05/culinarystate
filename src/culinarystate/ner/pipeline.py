"""Part K hybrid NER pipeline: cascade rules -> encoder ± CRF -> (GLiNER stub) -> verifier.

Layers are tried in order. Each returns spans + confidence. Higher layers can override
lower layers on the same region if they have higher confidence.

Design (SSOT Part K, §245 E16-A):
  1. Rules/gazetteer — fast, high precision on known vocabulary
  2. Encoder ± CRF — DeBERTa fine-tuned on TASTEset (0.927 base+CRF, 0.933 large+CRF)
  3. kNN-NER — NEGATIVE RESULT (Δ=0 across 5 seeds); excluded from cascade
  4. GLiNER — zero-shot for unseen labels; stub until eval completes
  5. Verifier — confidence filter + conflict resolution

Current: rules + encoder cascade. GLiNER and verifier are stubs returning empty.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

VERSION = "ner_pipeline@0.1"

LayerName = Literal["RULE", "ENCODER", "GLINER", "VERIFIER"]


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    label: str
    confidence: float  # 0-1
    source: LayerName

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class NERResult:
    text: str
    spans: tuple[Span, ...]
    layers_used: tuple[LayerName, ...]
    version: str = VERSION


def _overlaps(a: Span, b: Span) -> bool:
    return a.start < b.end and b.start < a.end


def _merge_spans(base: list[Span], override: list[Span]) -> list[Span]:
    """Merge override spans into base. Override wins on overlap if higher confidence."""
    merged = []
    used_base = set()

    for ov in override:
        conflicts = [i for i, b in enumerate(base) if _overlaps(b, ov)]
        if conflicts:
            for ci in conflicts:
                if base[ci].confidence < ov.confidence:
                    used_base.add(ci)
            if all(ci in used_base for ci in conflicts):
                merged.append(ov)
            else:
                for ci in conflicts:
                    used_base.discard(ci)
        else:
            merged.append(ov)

    for i, b in enumerate(base):
        if i not in used_base:
            conflict = any(_overlaps(b, m) for m in merged)
            if not conflict:
                merged.append(b)

    merged.sort(key=lambda s: (s.start, -s.length))
    return merged


def _default_food_match(text: str) -> bool:
    return len(text.split()) <= 4 and text[0].islower() if text else False


def _rule_spans(text: str, food_match=None) -> list[Span]:
    """Layer 1: rule-based NER. Returns spans with confidence based on match type."""
    from .rule_ner import tag_text

    raw = tag_text(text, food_match or _default_food_match)
    spans = []
    for start, end, label in raw:
        conf = 0.95 if label in ("QUANTITY", "UNIT") else 0.80
        spans.append(Span(start, end, label, conf, "RULE"))
    return spans


def _encoder_spans(text: str, tagger) -> list[Span]:
    """Layer 2: encoder tagger. Confidence from logit margin (proxy)."""
    raw = tagger.tag(text)
    spans = []
    for start, end, label in raw:
        conf = 0.90
        spans.append(Span(start, end, label, conf, "ENCODER"))
    return spans


def _gliner_spans(text: str) -> list[Span]:
    """Layer 4: GLiNER zero-shot — STUB. Returns empty until A100 eval completes."""
    return []


def _verify(spans: list[Span]) -> list[Span]:
    """Layer 5: confidence verifier — STUB. Currently passes all spans through."""
    return spans


class NERPipeline:
    def __init__(self, model_dir: str | Path | None = None, device: str | None = None,
                 layers: tuple[LayerName, ...] = ("RULE", "ENCODER")):
        self.layers = layers
        self._tagger = None
        self._model_dir = model_dir
        self._device = device

    def _get_tagger(self):
        if self._tagger is None and "ENCODER" in self.layers:
            from .encoder_tagger import EncoderTagger
            self._tagger = EncoderTagger(self._model_dir, self._device)
        return self._tagger

    def tag(self, text: str) -> NERResult:
        if not text or not text.strip():
            return NERResult(text=text, spans=(), layers_used=())

        all_spans: list[Span] = []
        used: list[LayerName] = []

        if "RULE" in self.layers:
            rule_out = _rule_spans(text)
            all_spans = rule_out
            used.append("RULE")

        if "ENCODER" in self.layers:
            tagger = self._get_tagger()
            if tagger:
                enc_out = _encoder_spans(text, tagger)
                all_spans = _merge_spans(all_spans, enc_out)
                used.append("ENCODER")

        if "GLINER" in self.layers:
            gli_out = _gliner_spans(text)
            if gli_out:
                all_spans = _merge_spans(all_spans, gli_out)
                used.append("GLINER")

        all_spans = _verify(all_spans)

        return NERResult(
            text=text,
            spans=tuple(all_spans),
            layers_used=tuple(used),
        )

    def tag_batch(self, texts: list[str]) -> list[NERResult]:
        return [self.tag(t) for t in texts]
