"""Rule-based ingredient-line NER baseline in TASTEset's label set (X10 / P5).

QUANTITY + UNIT from the quantity grammar; PROCESS from the prep-form vocabulary; closed lists for
PHYSICAL_QUALITY, COLOR, TASTE, PART; PURPOSE phrases ("for garnish", "to taste"); FOOD = the maximal run of
non-modifier tokens in the head region (before the first comma/parenthesis) that contains the ING n-gram match.
A transparent floor for the encoder NER (X8, A100); never a gold source.
"""
from __future__ import annotations

import re

from culinarystate.kg.mine import FORM_RE
from culinarystate.quantity.grammar import parse_line

QUALITY = {"fresh", "large", "medium", "small", "frozen", "dried", "boneless", "skinless", "instant", "whole", "powdered",
           "condensed", "cold", "canned", "mini", "granulated", "warm", "hot", "ripe", "raw", "lean", "thick", "thin",
           "firm", "soft", "extra-large", "jumbo", "baby", "plain", "self-raising", "self-rising", "all-purpose",
           "unbleached", "light", "low-fat", "fat-free", "reduced-fat", "full-fat", "skimmed", "heavy", "liquid",
           "smoked", "free-range", "organic", "coarse", "fine", "flaked", "virgin", "extra", "room", "temperature"}
COLOR = {"white", "black", "green", "brown", "red", "yellow", "dark", "purple", "golden", "gold", "silver", "pink"}
TASTE = {"sweet", "sweetened", "unsalted", "unsweetened", "semi-sweet", "semisweet", "salted", "mild", "sharp",
         "bittersweet", "spicy", "spiced", "sour", "dry", "bitter", "tangy", "savory", "savoury"}
PART = {"breast", "breasts", "whites", "white", "thighs", "thigh", "yolks", "yolk", "leg", "legs", "drumsticks",
        "wings", "ribs", "tenderloin", "cutlets", "fillets", "fillet", "zest", "leaves", "stems", "florets", "skins",
        "hearts", "loin", "shoulder", "shank"}
PURPOSE = re.compile(r"\b(?:for|to|as) (?:garnish(?:ing)?|serving|serve|topping|frying|dusting|dipping|decorat(?:ing|ion)|"
                     r"coating|greasing|brushing|cooking)\b|\bto taste\b", re.I)
STOP = {"of", "a", "an", "the", "and", "or", "about", "plus", "more", "each", "into", "in", "with", "cut", "very",
        "finely", "roughly", "thinly", "freshly", "lightly", "well", "packed", "loosely", "firmly", "at", "such", "as"}
NUMBER = re.compile(r"\s*([\d½¼¾⅓⅔⅛⅜⅝⅞]+(?:[\s./–-]+[\d½¼¾⅓⅔⅛⅜⅝⅞]+)*|a|an|one|two|three|four|five|six|seven|eight|"
                    r"nine|ten|eleven|twelve|half|dozen)\b", re.I)
PAREN_QTY = re.compile(r"\(\s*(\d+(?:[.,/]\d+)?(?:\s*-\s*\d+(?:[.,/]\d+)?)?)\s*-?\s*(fluid ounces?|fl\.? oz|ounces?|oz|"
                       r"grams?|g|kg|ml|millilit(?:re|er)s?|lbs?|pounds?|inch(?:es)?|cm)\b", re.I)
CONTAINER = re.compile(r"\b(packages?|packets?|containers?|boxe?s|box|jars?|bags?|envelopes?|cans?|bottles?|tins?|"
                       r"cartons?|heads?|bunch(?:es)?|sprigs?|pinch(?:es)?|dash(?:es)?|cloves?|slices?|sticks?|pieces?)\b",
                       re.I)
TOKEN = re.compile(r"[A-Za-z][A-Za-z'®&-]*")


def tag_line(line: str, offset: int, food_match) -> list[tuple[int, int, str]]:
    """Spans (start, end, label) with document offsets. food_match(text) -> True if text is a known ingredient."""
    spans: list[tuple[int, int, str]] = []
    q = parse_line(line)
    head_start = 0
    if q.span:
        a, b = q.span
        num = NUMBER.match(line, a)
        if num and num.group(1):
            spans.append((offset + num.start(1), offset + num.end(1), "QUANTITY"))
            head_start = num.end(1)
        if q.unit_raw:
            u = line.lower().find(q.unit_raw.lower(), head_start)
            if u >= 0:
                spans.append((offset + u, offset + u + len(q.unit_raw), "UNIT"))
                head_start = u + len(q.unit_raw)
    for m in PAREN_QTY.finditer(line):                     # "(14 oz)", "(8 ounce)" second quantity
        spans += [(offset + m.start(1), offset + m.end(1), "QUANTITY"), (offset + m.start(2), offset + m.end(2), "UNIT")]
        head_start = max(head_start, m.end())
        c = CONTAINER.match(line, m.end() + (len(line[m.end():]) - len(line[m.end():].lstrip(") "))))
        if c:
            spans.append((offset + c.start(), offset + c.end(), "UNIT"))
            head_start = max(head_start, c.end())
    for m in PURPOSE.finditer(line):
        spans.append((offset + m.start(), offset + m.end(), "PURPOSE"))
    taken = {i for s, e, _ in spans for i in range(s - offset, e - offset)}
    for m in FORM_RE.finditer(line):
        if m.start() >= head_start and m.start() not in taken:
            spans.append((offset + m.start(), offset + m.end(), "PROCESS"))
            taken |= set(range(m.start(), m.end()))
    cut = re.search(r"[,(;]", line[head_start:])
    head_end = head_start + cut.start() if cut else len(line)
    toks = [(m.start(), m.end(), m.group(0)) for m in TOKEN.finditer(line) if m.start() not in taken]
    run, runs = [], []
    for s, e, w in toks:
        lw = w.lower()
        label = ("COLOR" if lw in COLOR else "TASTE" if lw in TASTE else "PHYSICAL_QUALITY" if lw in QUALITY
                 else "PART" if lw in PART and run else None)
        if label and head_start <= s < head_end:
            spans.append((offset + s, offset + e, label))
        if label or lw in STOP or not (head_start <= s < head_end):
            if run:
                runs.append(run)
            run = []
            continue
        run.append((s, e))
    if run:
        runs.append(run)
    if runs:
        best = next((r for r in reversed(runs) if food_match(line[r[0][0]:r[-1][1]])), runs[-1])
        spans.append((offset + best[0][0], offset + best[-1][1], "FOOD"))
    return sorted(spans)


def tag_text(text: str, food_match) -> list[tuple[int, int, str]]:
    out, pos = [], 0
    for line in text.split("\n"):
        out += tag_line(line, pos, food_match) if line.strip() else []
        pos += len(line) + 1
    return out
