"""Food-safety questions are out of scope: explicit ABSTAIN that points to official guidance (S176, L-ROUTER).

CulinaryState has no validated food-safety model and its evidence rows are nutrient / quality retention values from
food-composition tables. A question about doneness, pathogens, a safe temperature or how long food keeps must never
be answered with a number or a yes / no. The rule baseline below only decides WHEN to refuse; it is a recall-oriented
heuristic (a false refusal costs a referral, a missed refusal could cost a person's health), tested on a labelled set
of examples in ``tests/unit/test_s176_safety.py``, not a calibrated classifier.

Two cue tiers (all patterns lower-case, whitespace-normalised):
- STRONG: explicit safety words (safe / unsafe / food poisoning / named pathogens / safe or internal temperature /
  storage and spoilage phrases). A STRONG cue refuses even when the question also names a nutrient.
- WEAK: doneness, raw-food and "how long does it keep / last" phrases ("is it done", "cooked through", "still pink",
  "eat raw", "can I eat"). These refuse only when the question carries no nutrient / quality target, so "how much
  vitamin C is left when the potatoes are done" and "how long can I boil it and still keep the vitamin C" stay
  retention questions.

The referral names are agent-recalled (SOURCE_UNVERIFIED_AGENT_RECALLED): Kush must check each name and address
before the page goes public. The message contains no number.
"""
from __future__ import annotations

import re

VERSION = "food_safety_cues@0.1"
REASON = "FOOD_SAFETY_REFER_OFFICIAL"
# the nutrient / quality cue shared with the query router (same pattern string as before S176)
NUTRIENT_CUE = (r"\b(?:vitamin\w*|nutrient\w*|mineral\w*|folate|carotene\w*|polyphenol\w*|antioxidant\w*|protein|"
                r"colou?r|texture|flavou?r|taste|aroma|crisp\w*|tender\w*|moist\w*|acrylamide)\b")

STRONG = (
    r"\b(?:un)?safe(?:ly|ty)?\b|\b(?:dangerous|hazard\w*|harmful)\b",
    r"\bfood[- ]?(?:borne|poison\w*)\b|\bpoison\w*|\bmake (?:me|us|you|them) (?:sick|ill)\b|\bget(?:ting)? (?:sick|ill)\b",
    r"\b(?:salmonella|listeria|campylobacter|e\.? ?coli|botulis\w*|clostridi\w*|norovirus|staphylococc\w*|"
    r"pathogen\w*|trichin\w*|toxin\w*)\b",
    r"\bkill\w*\b[^.?!]{0,25}\b(?:bacteria|germs|pathogens|salmonella|parasites)\b",
    r"\b(?:internal|core|minimum|safe|doneness) (?:cooking )?temp\w*|\bwhat temp\w* (?:should|do|to|is|must)\b"
    r"[^.?!]{0,30}\b(?:cook|reach|chicken|pork|turkey|burgers?|beef|egg|eggs|poultry|mince|sausages?)\b",
    r"\bhow long (?:can|could|does|do|will|should|is|are|would)\b[^.?!]{0,40}\b(?:sit|leave|left|fridge|"
    r"refrigerat\w*|freezer|counter|room temperature)\b",
    r"\b(?:leave|left|sit|sitting|sat)\b[^.?!]{0,25}\b(?:out|overnight|on the counter|at room temperature)\b",
    r"\b(?:spoil\w*|go(?:es)? (?:off|bad)|gone (?:off|bad)|expir\w*|best before|use[- ]by|shelf[- ]life|"
    r"danger zone|refreez\w*|reheat\w* (?:safely|twice))\b",
    r"\bdoneness\b",
)
WEAK = (
    r"\b(?:is|are|it'?s|they'?re|when|until|if|whether)\b[^.?!]{0,40}\bdone\b",
    r"\bcooked (?:through|enough|properly|fully|all the way)\b|\b(?:fully|completely|thoroughly|properly) cooked\b",
    r"\bundercooked (?:chicken|pork|turkey|poultry|beef|burgers?|sausages?|meat|eggs?|fish|seafood|shellfish|mince)\b",
    r"\bstill (?:pink|raw)\b|\bpink (?:in the middle|inside|centre|center)\b",
    r"\bmedium[- ]rare\b|\brare (?:steak|beef|burgers?|meat|lamb)\b",
    r"\b(?:eat|eating|drink|drinking) (?:it |them |this |that )?raw\b|\braw (?:chicken|pork|eggs?|meat|fish|beef|flour|dough)\b",
    r"\bcan (?:i|we|you) (?:still )?eat\b",
    r"\bhow long (?:can|could|does|do|will|should|is|are|would)\b[^.?!]{0,40}\b(?:keep|last|stay|store|good|fresh|out)\b",
)
_STRONG = tuple(re.compile(p) for p in STRONG)
_WEAK = tuple(re.compile(p) for p in WEAK)
_NUTRIENT = re.compile(NUTRIENT_CUE)

MESSAGE = ("I can't answer food-safety questions (safe temperatures, doneness, bacteria, or how long food keeps), "
           "so I won't give a number or a yes or no. Please use official food-safety guidance for your country, "
           "for example FSSAI in India, USDA FSIS and FoodSafety.gov in the US, the Food Standards Agency in the UK, "
           "or the WHO guide Five Keys to Safer Food. When you are unsure about a food, don't eat it.")
REFERRAL = ("FSSAI (India)", "USDA FSIS / FoodSafety.gov (US)", "Food Standards Agency (UK)", "WHO Five Keys to Safer Food")


def _norm(q: str | None) -> str:
    return re.sub(r"\s+", " ", (q or "").lower()).strip()


def is_safety(query: str | None) -> bool:
    """True when the question is a food-safety question (refuse and refer; never answer)."""
    q = _norm(query)
    if not q:
        return False
    if any(p.search(q) for p in _STRONG):
        return True
    return any(p.search(q) for p in _WEAK) and not _NUTRIENT.search(q)
