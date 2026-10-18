"""Mine SSOT core relations from recipe text into concept-level signals (X14).

ALTERNATIVE_TO  "butter or margarine"            -> (ING a, ING b)
OPTIONAL_IF     "(optional)", "to taste", "if desired", "for garnish" -> ingredient line marked optional
HAS_FORM        "2 onions, finely chopped"        -> prep form tokens (closed vocabulary)
USES_MEDIUM     "fry in oil", "boil in salted water" -> medium for processes in the same sentence
ENDPOINT        "cook until golden brown"         -> endpoint state for the nearest preceding process
Closed vocabularies keep this auditable; anything outside them is ignored (UNKNOWN), never guessed.
"""
from __future__ import annotations

import re

OPTIONAL = re.compile(r"\(optional\)|\boptional\b|\bto taste\b|\bif (?:desired|liked|you like|preferred)\b|"
                      r"\bfor (?:garnish|garnishing|decoration|serving)\b", re.I)
FORMS = ("finely chopped", "roughly chopped", "chopped", "diced", "minced", "thinly sliced", "sliced", "grated",
         "crushed", "ground", "shredded", "peeled", "halved", "quartered", "julienned", "beaten", "melted", "softened",
         "cubed", "mashed", "toasted", "sifted", "zested", "juiced", "deseeded", "seeded", "trimmed", "torn",
         "crumbled", "pitted", "cored", "drained", "rinsed", "soaked", "cooked", "boiled", "roasted", "frozen",
         "thawed", "whisked", "squeezed")
FORM_RE = re.compile(r"\b(" + "|".join(re.escape(f) for f in sorted(FORMS, key=len, reverse=True)) + r")\b", re.I)
MEDIA = {"water": "water", "salted water": "water", "oil": "oil", "olive oil": "oil", "vegetable oil": "oil",
         "butter": "butter", "ghee": "ghee", "lard": "lard", "dripping": "fat", "fat": "fat", "stock": "stock",
         "broth": "stock", "milk": "milk", "wine": "wine", "steam": "steam", "syrup": "syrup", "cream": "cream"}
MEDIUM_RE = re.compile(r"\b(?:in|with|into)\s+(?:a\s+little\s+|some\s+|hot\s+|boiling\s+|the\s+|plenty of\s+)*"
                       r"(salted water|olive oil|vegetable oil|water|oil|butter|ghee|lard|dripping|fat|stock|broth|milk|"
                       r"wine|steam|syrup|cream)\b", re.I)
ENDPOINTS = ("golden brown", "golden", "browned", "brown", "tender", "soft", "softened", "translucent", "thick",
             "thickened", "smooth", "crisp", "crispy", "bubbling", "reduced", "set", "firm", "cooked through",
             "wilted", "fragrant", "melted", "doubled in size", "doubled", "light and fluffy", "fluffy", "pale",
             "caramelised", "caramelized", "opaque", "done", "dissolved", "combined", "stiff", "glossy", "puffed",
             "al dente", "hot", "warm", "cool", "cold", "evaporated", "absorbed", "charred", "sticky", "creamy")
ENDPOINT_RE = re.compile(r"\buntil\s+(?:it\s+is\s+|they\s+are\s+|it\s+has\s+|they\s+have\s+|just\s+|very\s+|nicely\s+|"
                         r"lightly\s+|well\s+|completely\s+|thoroughly\s+)*("
                         + "|".join(re.escape(e) for e in sorted(ENDPOINTS, key=len, reverse=True)) + r")\b", re.I)
ALT_SPLIT = re.compile(r"\s+or\s+", re.I)


def is_optional(line: str) -> bool:
    return bool(OPTIONAL.search(line))


def forms(line: str) -> set[str]:
    return {m.group(1).lower() for m in FORM_RE.finditer(line)}


def alternatives(line: str, link_phrase) -> tuple[str, str] | None:
    """`link_phrase(text) -> ING id | None`; both sides of a single ' or ' must link to different concepts."""
    parts = ALT_SPLIT.split(re.sub(r"\(.*?\)", " ", line))
    if len(parts) != 2:
        return None
    a, b = link_phrase(parts[0]), link_phrase(parts[1])
    right = parts[1].split()
    if len(right) >= 2:                                    # "chicken or vegetable stock": share the head noun
        d = link_phrase(f"{parts[0]} {right[-1]}")
        if d and d != link_phrase(right[-1]):              # only if the pair names a more specific concept
            a = d
    return (a, b) if a and b and a != b else None


def media(sentence: str) -> set[str]:
    return {MEDIA[m.group(1).lower()] for m in MEDIUM_RE.finditer(sentence)}


def endpoints(sentence: str, procs: list[tuple[int, str]]) -> list[tuple[str, str]]:
    """(process, endpoint) pairs: each 'until X' attaches to the nearest process mentioned before it."""
    out = []
    for m in ENDPOINT_RE.finditer(sentence):
        before = [p for pos, p in procs if pos < m.start()]
        if before:
            e = m.group(1).lower().replace("caramelized", "caramelised").replace("crispy", "crisp")
            out.append((before[-1], e))
    return out
