"""Step 17a end-to-end contract check with a toy fixture rung (DRAFT_PENDING_16c).

The toy rung below is NOT Rung A (17b): it hard-codes spans for one synthetic
instruction so the interface, validators V1-V4 and the auditor can be exercised
together. It shows the call pattern a real rung is expected to follow.
"""
from __future__ import annotations

import json
from pathlib import Path

from culinarystate.extraction import quantity_stages as qs
from culinarystate.extraction.auditor import audit_outputs
from culinarystate.extraction.interfaces import (
    EntityCandidate, EventCandidate, EventGraph, Failure, FailureCode, LinkCandidate, LinkResult, Mention,
    MentionSet, ReferenceResult, RungInterface, SourceText, Span, StageConfig, Trace, TraceKind, ValueClaim,
    ValueKind,
)
from culinarystate.extraction.invariants import run_validators
from culinarystate.quantity.rc2_grounding import GroundingContext

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text())
META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT",
        "evidence_refs": ["synthetic:17a-e2e"]}
RAW = "Add 200 g lentils to the pan and simmer them for 10 minutes."
LABELS = frozenset({"ACTION", "FOOD_MENTION", "QUANTITY_IN_STEP", "DURATION"})


def at(s, needle):
    i = s.raw.index(needle)
    return Span.of(s, i, i + len(needle))


class ToyRung:
    """Fixture-only rung over RAW; every value is traced, nothing is guessed."""

    def extract_mentions(self, source, config):
        dur = ValueClaim("duration", ValueKind.DURATION, 10, origin="EXPLICIT_SOURCE", claim_route="EXPLICIT",
                         span=at(source, "10"), trace=Trace(TraceKind.SPAN_LITERAL))
        ms = (Mention("M1", "ACTION", at(source, "Add")), Mention("M2", "QUANTITY_IN_STEP", at(source, "200 g")),
              Mention("M3", "FOOD_MENTION", at(source, "lentils")), Mention("M4", "ACTION", at(source, "simmer")),
              Mention("M5", "FOOD_MENTION", at(source, "them")),
              Mention("M6", "DURATION", at(source, "10 minutes"), attributes=(dur,)))
        return MentionSet(source.text_id, source.sha256, ms, config.provenance("extract_mentions"))

    def link(self, source, mention, config):
        cands = (LinkCandidate("ING-000001", 0.7),) if mention.span.surface == "lentils" else ()
        if not cands:
            return LinkResult(mention.mention_id, mention.span, (), config.provenance("link"),
                              failure=Failure(FailureCode.NO_VALID_CANDIDATE, "CANDIDATE_SET_EMPTY"))
        return LinkResult(mention.mention_id, mention.span, cands, config.provenance("link"), selected_id="ING-000001")

    def parse_quantity(self, source, span, config, *, source_metadata, locale=None):
        return qs.parse_quantity(source, span, config, source_metadata=source_metadata, locale=locale)

    def ground_quantity(self, source, span, context, config, *, schema, result_id):
        return qs.ground_quantity(source, span, context, config, schema=schema, result_id=result_id)

    def build_events(self, source, mentions, links, quantities, config):
        kind = ValueClaim("event_kind", ValueKind.CATEGORICAL, "ACTION", origin="DERIVED_DETERMINISTIC",
                          span=at(source, "Add"), trace=Trace(TraceKind.REGISTRY_LABEL))
        amount = ValueClaim("amount_g", ValueKind.MASS_G, 200, origin="DERIVED_DETERMINISTIC", unit="g",
                            span=quantities[0].span, trace=Trace(TraceKind.QNT_RECORD, ref_ids=("Q1",)))
        events = (EventCandidate("E1", (0, 0), at(source, "Add"), consumes=("N1",), produces=("N2",),
                                 attributes=(kind, amount)),
                  EventCandidate("E2", (0, 1), at(source, "simmer"), consumes=("N2",), produces=("N3",),
                                 depends_on=("E1",)))
        entities = (EntityCandidate("N1", "INGREDIENT_LOT", "INCORPORATED", span=at(source, "lentils")),
                    EntityCandidate("N2", "MIXTURE", "INCORPORATED", ("N1",), "E1"),
                    EntityCandidate("N3", "INTERMEDIATE", "ACTIVE", ("N2",), "E2"))
        return EventGraph(source.text_id, source.sha256, events, entities, (), {"N1": "USED"},
                          config.provenance("build_events"))

    def resolve_refs(self, source, mentions, graph, config):
        m = next(x for x in mentions.mentions if x.span.surface == "them")
        return (ReferenceResult(m.mention_id, m.span, ("N1", "N2"), config.provenance("resolve_refs"),
                                antecedent_ids=("N2",)),)


def test_toy_rung_outputs_pass_v1_to_v4_and_have_zero_invented_values():
    s = SourceText.from_raw("SYN-E2E", RAW)
    cfg = StageConfig(rung_id="TOY", params={"fixture": True}, claim_route="INFERRED_RULE", annotated_labels=LABELS)
    rung = ToyRung()
    assert isinstance(rung, RungInterface)
    mentions = rung.extract_mentions(s, cfg)
    links = [rung.link(s, m, cfg) for m in mentions.mentions if m.label == "FOOD_MENTION"]
    q = rung.ground_quantity(s, at(s, "200 g"), GroundingContext(source_metadata=META), cfg, schema=SCHEMA,
                             result_id="Q1")
    p = rung.parse_quantity(s, at(s, "200 g"), cfg, source_metadata=META)
    graph = rung.build_events(s, mentions, links, [q], cfg)
    refs = rung.resolve_refs(s, mentions, graph, cfg)
    outputs = [mentions, *links, p, q, graph, *refs]
    reports = run_validators(s, outputs, qnt_schema=SCHEMA, mention_labels=LABELS,
                             id_sets={"ING": frozenset({"ING-000001"})})
    assert {k: r.status for k, r in reports.items()} == {"V1": "PASS", "V2": "PASS", "V3": "PASS", "V4": "PASS"}
    audit = audit_outputs(s, outputs)
    assert audit.invented_count == 0 and audit.status == "PASS"
    assert links[1].failure.code is FailureCode.NO_VALID_CANDIDATE
    assert {o.provenance.config_hash for o in outputs} == {cfg.config_hash}
