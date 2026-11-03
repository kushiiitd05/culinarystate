"""Step 17b Rung A deterministic baseline on synthetic text (DRAFT_PENDING_16c).

Rung A (Plan 17-M, B0): longest-match lexicon tagging; verb -> PROC lookup with
modifier cues; nearest-noun / recency argument binding; recency + lexical coref;
sentence templates; claim_route = INFERRED_RULE; uncertainty = rule-fired flags and
an ambiguity count only. Logic tests use a small synthetic lexicon so expectations
are exact; smoke tests use the read-only repository lexicons. Nothing here is gold.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.extraction import rung_a as ra
from culinarystate.extraction import rung_a_lexicon as lx
from culinarystate.extraction.auditor import audit_outputs
from culinarystate.extraction.interfaces import (
    FailureCode, InterfaceError, RungInterface, SourceText, StageConfig, TraceKind, ValueKind,
)
from culinarystate.extraction.invariants import run_validators
from culinarystate.quantity.rc2_grounding import GroundingContext, ground_quantity_rc2

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text())
LEDGERS = ("ING", "ALIAS", "PROC", "TOOL", "UNIT")
CATALOG = ROOT / "annotation/hard_case_catalog_v2_DRAFT.jsonl"

SYN = dict(
    foods={"onion": ["ING-000010"], "garlic": ["ING-000011"], "water": ["ING-000012"], "oil": ["ING-000014"],
           "olive oil": ["ING-000013"], "paste": ["ING-000015"], "syrup": ["ING-000016"], "grain": ["ING-000017"],
           "liquid": ["ING-000018"], "dough": ["ING-000019"], "leaf": ["ING-000020"],
           "clove": ["ING-000021", "ING-000022"]},
    procs={"heat": ["PROC-000032"], "add": ["PROC-000088"], "fry": ["PROC-000050"], "stir": ["PROC-000064"],
           "pour": ["PROC-000089"], "bake": ["PROC-000001"], "mix": ["PROC-000065"], "place": ["PROC-000102"],
           "divide": ["PROC-000120"], "reserve": ["PROC-000121"], "discard": ["PROC-000122"],
           "rest": ["PROC-000123"], "hold": ["PROC-000124"]},
    proc_info={"PROC-000032": ("heat", "HEAT_GENERAL", "ACTION"), "PROC-000088": ("add", "COMBINATION", "ACTION"),
               "PROC-000050": ("fry", "FAT_HEAT", "ACTION"), "PROC-000064": ("stir", "MECHANICAL_MIX", "ACTION"),
               "PROC-000089": ("pour", "TRANSFER", "ACTION"), "PROC-000001": ("bake", "DRY_HEAT", "ACTION"),
               "PROC-000065": ("mix", "MECHANICAL_MIX", "ACTION"), "PROC-000102": ("place", "TRANSFER", "ACTION"),
               "PROC-000120": ("divide", "SHAPING", "ACTION"), "PROC-000121": ("reserve", "RESERVATION", "ACTION"),
               "PROC-000122": ("discard", "SEPARATION", "ACTION"), "PROC-000123": ("rest", "RESTING", "ACTION"),
               "PROC-000124": ("hold", "RESTING", "ACTION")},
    tools={"frying pan": ["TOOL-000019"], "pan": ["TOOL-000099"], "oven": ["TOOL-000001"]},
    tool_classes={"TOOL-000019": "COOKWARE", "TOOL-000001": "HEATING_APPLIANCE"},
    units=["g", "grams", "tbsp", "tsp", "ml", "cup", "cups"],
)
TEXT = ("Heat the oil in a frying pan over medium heat. Add 200 g onion and fry for 5-6 minutes until golden. "
        "Stir in the garlic, then pour in 2 tbsp water. Bake at 180°C for 20 minutes.")


@pytest.fixture(scope="module")
def rung() -> ra.RungA:
    return ra.RungA(lx.build_lexicon(**SYN))


@pytest.fixture(scope="module")
def real() -> ra.RungA:
    return ra.RungA(lx.load_lexicon(ROOT))


def run(rung: ra.RungA, raw: str, locale: str | None = None):
    s = SourceText.from_raw("SYN-17B", raw)
    cfg = rung.config(locale=locale)
    return s, cfg, rung.run(s, cfg, schema=SCHEMA)


def surfaces(out, label: str) -> list[str]:
    return [m.span.surface for m in out.mentions.mentions if m.label == label]


def event_attr(event, name: str):
    return next((a for a in event.attributes if a.field == name), None)


def check_clean(rung: ra.RungA, s: SourceText, out) -> None:
    reports = run_validators(s, out.all(), qnt_schema=SCHEMA, mention_labels=ra.RUNG_A_LABELS,
                             id_sets=rung.lexicon.id_sets())
    assert {k: r.issues for k, r in reports.items()} == {"V1": (), "V2": (), "V3": (), "V4": ()}
    assert audit_outputs(s, out.all(), recomputers=rung.recomputers()).invented_count == 0


# ---------------------------------------------------------------- module / config
def test_modules_are_draft_pending_16c_and_versioned():
    for mod in (ra, lx):
        assert "DRAFT_PENDING_16c" in mod.__doc__.splitlines()[0]
    assert ra.RULES_VERSION.endswith("_DRAFT") and lx.LEXICON_VERSION.endswith("_DRAFT")


def test_rung_a_implements_the_common_interface_with_inferred_rule_route(rung):
    assert isinstance(rung, RungInterface)
    cfg = rung.config()
    assert cfg.rung_id == "A" and cfg.claim_route == "INFERRED_RULE"
    assert cfg.annotated_labels == ra.RUNG_A_LABELS and "MEDIUM" not in ra.RUNG_A_LABELS
    assert cfg.params["lexicon_fingerprint"] == rung.lexicon.fingerprint
    assert rung.config(locale="UK").config_hash != cfg.config_hash
    with pytest.raises(InterfaceError):
        rung.extract_mentions(SourceText.from_raw("X", "Stir."), replace(cfg, claim_route="INFERRED_LLM"))
    with pytest.raises(InterfaceError):
        rung.extract_mentions(SourceText.from_raw("X", "Stir."), replace(cfg, params={"lexicon_fingerprint": "x"}))


def test_lexicon_fingerprint_depends_on_content_only():
    a, b = lx.build_lexicon(**SYN), lx.build_lexicon(**SYN)
    assert a.fingerprint == b.fingerprint and len(a.fingerprint) == 64
    other = dict(SYN, foods=dict(SYN["foods"], salt=["ING-000099"]))
    assert lx.build_lexicon(**other).fingerprint != a.fingerprint


# ---------------------------------------------------------------- mentions
def test_mentions_are_typed_longest_match_spans_that_round_trip(rung):
    s, _, out = run(rung, TEXT)
    assert surfaces(out, "ACTION") == ["Heat", "Add", "fry", "Stir", "pour", "Bake"]
    assert surfaces(out, "FOOD_MENTION") == ["oil", "onion", "garlic", "water"]
    assert surfaces(out, "TOOL") == ["frying pan"]
    assert surfaces(out, "QUANTITY_IN_STEP") == ["200 g", "2 tbsp"]
    assert surfaces(out, "DURATION") == ["5-6 minutes", "20 minutes"]
    assert surfaces(out, "TEMPERATURE") == ["180°C"]
    assert surfaces(out, "ENDPOINT") == ["until golden"]
    assert surfaces(out, "CONDITION_CUE") == ["medium heat"]
    for m in out.mentions.mentions:
        assert s.raw[m.span.char_start:m.span.char_end] == m.span.surface
    assert out.mentions.provenance.claim_route == "INFERRED_RULE"
    assert out.mentions.provenance.label_status("MEDIUM") == "MISSING"
    check_clean(rung, s, out)


def test_duration_and_temperature_values_are_literal_or_registered_rules(rung):
    _, _, out = run(rung, TEXT)
    dur = [m for m in out.mentions.mentions if m.label == "DURATION"][0]
    lit = event_attr(dur, "duration")
    assert lit.value == (5, 6) and lit.unit == "minutes" and lit.trace.kind is TraceKind.SPAN_LITERAL
    norm = event_attr(dur, "duration_min")
    assert norm.value == (5, 6) and norm.unit == "min" and norm.trace.rule_id == "RA_DURATION_TO_MIN_V1"
    temp = [m for m in out.mentions.mentions if m.label == "TEMPERATURE"][0]
    t = event_attr(temp, "temperature")
    assert t.kind is ValueKind.TEMPERATURE and t.value == 180 and t.unit == "C"


def test_bare_c_after_a_number_is_flagged_not_read_as_a_temperature(rung):
    s, _, out = run(rung, "Hold at 20 C for 2 min.")
    assert "BARE_TEMPERATURE_UNIT_AMBIGUOUS" in out.mentions.diagnostics
    assert surfaces(out, "TEMPERATURE") == [] and surfaces(out, "DURATION") == ["2 min"]
    check_clean(rung, s, out)


def test_duration_after_a_mixed_number_is_flagged_not_read_as_its_last_digit(rung):
    s, _, out = run(rung, "Bake for 1 1/2 hours.")
    assert "DURATION_COMPLEX_NUMBER" in out.mentions.diagnostics
    assert surfaces(out, "DURATION") == []
    check_clean(rung, s, out)


def test_decimal_comma_duration_stays_unknown(rung):
    s, _, out = run(rung, "Rest for 1,5 hours.")
    dur = [m for m in out.mentions.mentions if m.label == "DURATION"][0]
    claim = event_attr(dur, "duration")
    assert claim.status == "UNKNOWN" and claim.value is None
    assert "DECIMAL_COMMA_UNKNOWN" in out.mentions.diagnostics
    check_clean(rung, s, out)


def test_noun_like_verbs_need_a_verb_slot(rung):
    _, _, out = run(rung, "Add oil to the heat.")
    assert surfaces(out, "ACTION") == ["Add"]


# ---------------------------------------------------------------- link
def test_link_selects_only_a_unique_lexicon_candidate(rung):
    s, cfg, out = run(rung, "Add one clove and the onion and the zavu.")
    by = {lr.span.surface: lr for lr in out.links}
    assert by["onion"].selected_id == "ING-000010" and by["onion"].failure is None
    assert by["clove"].failure.code is FailureCode.UNRESOLVED and by["clove"].candidate_ids == (
        "ING-000021", "ING-000022")
    assert by["Add"].selected_id == "PROC-000088"
    assert "zavu" not in by
    check_clean(rung, s, out)


def test_link_of_a_non_linkable_label_is_an_explicit_failure(rung):
    s, cfg, out = run(rung, "Bake for 20 minutes.")
    dur = [m for m in out.mentions.mentions if m.label == "DURATION"][0]
    r = rung.link(s, dur, cfg)
    assert r.failure.code is FailureCode.NO_VALID_CANDIDATE and r.selected_id is None


# ---------------------------------------------------------------- quantities
def test_quantities_delegate_to_rc2_grounding_and_only_q0_grams_appear(rung):
    s, _, out = run(rung, TEXT)
    q200, q2 = out.quantities
    ctx = GroundingContext(source_metadata=ra.QUANTITY_SOURCE_META, quantity_scope="INSTRUCTION_ALLOCATION")
    assert q200.record == ground_quantity_rc2("200 g", ctx, schema=SCHEMA).record
    assert q200.failure is None and q2.failure.code is FailureCode.UNRESOLVED
    add = next(e for e in out.graph.events if event_attr(e, "proc_id").value == "PROC-000088")
    amount = event_attr(add, "amount_g_0")
    assert amount.kind is ValueKind.MASS_G and amount.value == 200 and amount.trace.kind is TraceKind.QNT_RECORD
    assert not any(a.kind is ValueKind.MASS_G for e in out.graph.events for a in e.attributes if a is not amount)


# ---------------------------------------------------------------- events / binding
def test_events_follow_text_order_with_recency_binding_and_combine_templates(rung):
    s, _, out = run(rung, TEXT)
    g = out.graph
    assert [e.order for e in g.events] == [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0)]
    ents = {n.entity_id: n for n in g.entities}
    fry = g.events[2]
    assert fry.consumes == g.events[1].produces and "IMPLICIT_ARG_BOUND" in g.diagnostics
    stir, pour = g.events[3], g.events[4]
    assert ents[stir.produces[0]].entity_type == "MIXTURE" and len(stir.consumes) == 2
    assert stir.produces[0] in pour.consumes
    assert event_attr(fry, "temporal_relation").value == "UNTIL"
    assert event_attr(g.events[0], "tool_id_0").value == "TOOL-000019"
    assert event_attr(g.events[0], "event_kind").value == "ACTION"
    assert set(g.lot_accounting.values()) == {"USED"} and len(g.lot_accounting) == 4
    assert all(e.claim_route == "INFERRED_RULE" for e in g.events)
    check_clean(rung, s, out)


def test_many_to_one_into_names_the_product(rung):
    s, _, out = run(rung, "Mix the grains with the liquid into a paste. Stir it.")
    g = out.graph
    mix = g.events[0]
    product = next(n for n in g.entities if n.entity_id == mix.produces[0])
    assert len(mix.consumes) == 2 and product.span.surface == "paste"
    ref = out.refs[0]
    assert ref.antecedent_ids == (product.entity_id,)
    check_clean(rung, s, out)


def test_ambiguous_singular_pronoun_is_unresolved_and_plural_takes_the_tier(rung):
    s, _, out = run(rung, "Place the paste beside the syrup. Stir it. Place them in the pan.")
    first, second = out.refs
    assert first.failure.code is FailureCode.UNRESOLVED and first.failure.reason == "AMBIGUOUS_ANTECEDENT"
    assert len(first.candidates) == 2
    assert len(second.antecedent_ids) == 2 and second.failure is None
    assert "REF_ARG_UNRESOLVED" in out.graph.diagnostics
    check_clean(rung, s, out)


def test_divide_into_a_number_word_makes_split_children_without_fractions(rung):
    s, _, out = run(rung, "Divide the dough into four portions.")
    g = out.graph
    assert [a.kind for a in g.allocations] == ["SPLIT"] * 4
    assert all(a.fraction is None and a.basis == "UNSPECIFIED" for a in g.allocations)
    count = event_attr(g.events[0], "split_count")
    assert count.value == 4 and count.trace.rule_id == "RA_NUMBER_WORD_V1"
    check_clean(rung, s, out)


def test_reserve_half_gives_a_rule_traced_fraction_and_a_remainder(rung):
    s, _, out = run(rung, "Reserve half of the liquid.")
    kinds = Counter(a.kind for a in out.graph.allocations)
    assert kinds == {"RESERVE": 1, "REMAINDER": 1}
    frac = next(a.fraction for a in out.graph.allocations if a.kind == "RESERVE")
    assert frac.value == Fraction(1, 2) and frac.trace.rule_id == "RA_HALF_V1"
    remainder = next(a for a in out.graph.allocations if a.kind == "REMAINDER")
    assert remainder.fraction is None
    check_clean(rung, s, out)


def test_optional_cue_and_discard_update_modality_and_lot_accounting(rung):
    s, _, out = run(rung, "Add the leaf if desired. Discard the liquid.")
    g = out.graph
    assert event_attr(g.events[0], "modality").value == "OPTIONAL"
    assert sorted(g.lot_accounting.values()) == ["DISCARDED", "OPTIONAL"]
    assert g.events[1].discards and not g.events[1].consumes
    check_clean(rung, s, out)


def test_lexical_coref_reuses_a_live_entity(rung):
    s, _, out = run(rung, "Heat the oil. Discard the oil.")
    g = out.graph
    assert len([n for n in g.entities if n.entity_type == "INGREDIENT_LOT"]) == 1
    assert g.events[1].discards == g.events[0].produces
    assert "LEXICAL_COREF_DESCENDANT" in g.diagnostics
    check_clean(rung, s, out)


def test_resolve_refs_refuses_a_graph_it_cannot_reproduce(rung):
    s, cfg, out = run(rung, "Place the paste. Stir it.")
    foreign = replace(out.graph, entities=out.graph.entities[:-1])
    refs = rung.resolve_refs(s, out.mentions, foreign, cfg)
    assert refs and all(r.failure.reason == "GRAPH_NOT_REPRODUCED" for r in refs)


# ---------------------------------------------------------------- auditor / determinism
def test_rule_traced_values_need_the_registered_recomputers(rung):
    s, _, out = run(rung, TEXT)
    assert audit_outputs(s, out.all(), recomputers=rung.recomputers()).invented_count == 0
    bare = audit_outputs(s, out.all())
    assert bare.invented_count > 0 and set(bare.invented_by_code) == {"RULE_NOT_REPRODUCIBLE"}
    ev = out.graph.events[0]
    bad = replace(ev, attributes=tuple(replace(a, value="PROC-000001") if a.field == "proc_id" else a
                                       for a in ev.attributes))
    tampered = replace(out.graph, events=(bad, *out.graph.events[1:]))
    r = audit_outputs(s, [*out.quantities, tampered], recomputers=rung.recomputers())
    assert r.invented_by_code == {"RULE_MISMATCH": 1}


def test_runs_are_deterministic(rung):
    _, _, a = run(rung, TEXT)
    _, _, b = run(rung, TEXT)
    assert a.all() == b.all()


def test_empty_text_gives_empty_but_valid_outputs(rung):
    s, _, out = run(rung, "")
    assert out.mentions.mentions == () and out.graph.events == () and out.refs == ()
    check_clean(rung, s, out)


# ---------------------------------------------------------------- real lexicons (read-only)
def _ledger_hashes() -> dict[str, str]:
    return {n: hashlib.sha256((ROOT / f"ledgers/data/{n}.jsonl").read_bytes()).hexdigest() for n in LEDGERS}


def test_real_lexicon_loads_read_only_active_latest_records():
    before = _ledger_hashes()
    lex = lx.load_lexicon(ROOT, cache=False)
    assert _ledger_hashes() == before
    ids = lex.id_sets()
    assert {"ING", "PROC", "TOOL"} <= set(ids) and all(ids.values())
    assert all(i.startswith("ING-") for i in ids["ING"])
    assert len(lex.sources) == 7 and all(len(h) == 64 for h in lex.sources.values())


def test_hard_case_prompts_run_without_invented_values_and_catalog_stays_blank(real):
    before = CATALOG.read_bytes()
    rows = [json.loads(line) for line in before.decode("utf-8").splitlines() if line.strip()]
    assert len(rows) == 17
    for row in rows:
        s, _, out = run(real, row["prompt"])
        assert audit_outputs(s, out.all(), recomputers=real.recomputers()).invented_count == 0
        reports = run_validators(s, out.all(), qnt_schema=SCHEMA, mention_labels=ra.RUNG_A_LABELS,
                                 id_sets=real.lexicon.id_sets())
        assert reports["V1"].issues == () and reports["V2"].issues == () and reports["V3"].issues == ()
    assert CATALOG.read_bytes() == before
    assert all(r["observed_output"] is None and r["expert_decision"] is None for r in rows)


def test_a_word_after_a_determiner_or_number_is_not_a_verb(rung):
    _, _, out = run(rung, "Divide the dough into four portions. Add two stir sticks.")
    assert surfaces(out, "ACTION") == ["Divide", "Add"]


def test_unresolved_mixture_word_opens_a_new_flagged_entity_and_feeds_the_template(rung):
    s, _, out = run(rung, "Divide the batter into 2 parts.")
    g = out.graph
    assert out.refs[0].failure.code is FailureCode.NO_VALID_CANDIDATE
    assert "INTERMEDIATE_NEW_ENTITY" in g.diagnostics
    assert [a.kind for a in g.allocations] == ["SPLIT", "SPLIT"]
    assert event_attr(g.events[0], "split_count").trace.kind is TraceKind.SPAN_LITERAL
    check_clean(rung, s, out)
