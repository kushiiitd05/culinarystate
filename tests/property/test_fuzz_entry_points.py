"""Adversarial fuzzing of every free-text entry point (seeded; reproducible).

Invariants: never crash; spans stay inside the text and well-ordered; MEASURED values only when a digit or number word
is present; explicit UNKNOWN/None instead of guesses; outputs are deterministic for identical input.
"""
import random
import re

import pytest

from culinarystate.decision.relevance import intent, relevance_gate
from culinarystate.evidence.conditions import extract_conditions
from culinarystate.evidence.fdc_pairs import split_state
from culinarystate.ingest.bognar_yield import parse_yields
from culinarystate.kg.mine import alternatives, endpoints, forms, is_optional, media
from culinarystate.ner.rule_ner import tag_text
from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.normalize import normalize
from culinarystate.state_graph.rule_compiler import step_processes
from culinarystate.vocab.line_link import LineLinker

RNG = random.Random(4242)
ALPHABET = ("abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 ½¼¾⅓⅔ .,;:-/()[]'\"!?%&*+=<>~°ºé"
            "ñüçøß 日本語 हिन्दी 🍅🔥 \t\n\r\x00​‮")
SEEDS = ["2 cups flour", "1½ kg potatoes, peeled", "bake at 180°C for 20-25 min", "salt or pepper (optional)",
         "fry until golden brown", "-18 °C", "3/4 l stock", "1 tsp", "a pinch", "Beef, ground, raw"]
LINKER = LineLinker({"flour": "ING-1", "potato": "ING-2", "salt": "ING-3", "pepper": "ING-4", "stock": "ING-5"}, set())


def _garbage(n: int) -> list[str]:
    out = ["", " ", "\n\n\n", "0", "-", "½", "°C", "°F", "∞ kg", "1e309 g", "999999999999999999999 kg",
           "NaN ml", "1/0 cup", "0/0 kg", "--5 kg", "5 kg kg kg", "((((((", "'; DROP TABLE ING; --",
           "<script>alert(1)</script>", "x" * 20000, "1 " * 3000, "🍅" * 500]
    for _ in range(n):
        k = RNG.randint(1, 80)
        s = "".join(RNG.choice(ALPHABET) for _ in range(k))
        if RNG.random() < 0.5:                       # mutate a realistic seed
            seed = list(RNG.choice(SEEDS))
            for _ in range(RNG.randint(1, 4)):
                seed.insert(RNG.randint(0, len(seed)), RNG.choice(ALPHABET))
            s = "".join(seed)
        out.append(s)
    return out


GARBAGE = _garbage(400)
HAS_NUMBER = re.compile(r"[0-9½¼¾⅓⅔⅛⅜⅝⅞]|\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|half|dozen)\b",
                        re.I)


@pytest.mark.parametrize("s", GARBAGE)
def test_quantity_never_crashes_or_invents(s):
    z = normalize(parse_line(s), locale="UK")
    for ch in (z.mass_g, z.volume_ml, z.count):
        if ch["status"] == "MEASURED":
            assert HAS_NUMBER.search(s), f"MEASURED without any number in {s!r}"
            assert ch["value"] == ch["value"], "NaN leaked"                      # NaN != NaN


@pytest.mark.parametrize("s", GARBAGE)
def test_conditions_never_crash_and_values_are_finite(s):
    c = extract_conditions(s)
    for t in c["temperatures"]:
        v = t["value"]
        for k in ("value", "low", "high"):
            if v.get(k) is not None:
                assert v[k] == v[k] and abs(v[k]) != float("inf")
        assert v["raw"] is None or v["raw"] in s


@pytest.mark.parametrize("s", GARBAGE)
def test_rule_ner_spans_in_bounds_ordered_and_deterministic(s):
    spans = tag_text(s, lambda t: t.lower() in {"flour", "potatoes", "salt"})
    for a, b, lab in spans:
        assert 0 <= a < b <= len(s) and lab
    assert spans == sorted(spans) and spans == tag_text(s, lambda t: t.lower() in {"flour", "potatoes", "salt"})


@pytest.mark.parametrize("s", GARBAGE)
def test_linkers_miners_and_gates_never_crash(s):
    assert isinstance(LINKER.mentions(s), list)
    LINKER.match_phrase(LINKER.phrase(s))
    is_optional(s), forms(s), media(s), endpoints(s, [(0, "fry")])
    alternatives(s, lambda t: LINKER.match_phrase(LINKER.phrase(t)))
    step_processes(s)
    split_state(s)
    g = relevance_gate(s)
    assert g["relevant"] in (True, False, None) and g["raw"] == s
    assert intent(s) in ("ANSWER", "COMPARE", "DIAGNOSE", "RECOVER", "RECOMMEND")


def test_yield_parser_ignores_garbage_and_truncated_tables():
    text = "\n".join(GARBAGE[:200]) + "\nTable 9: Weight yield factors by cooking of x\n Carrot, boiled   FR m.S   a\n"
    assert parse_yields(text) == []                    # truncated row: not parsed, not guessed
