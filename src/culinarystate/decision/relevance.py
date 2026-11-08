"""Process relevance gate + query intent cues (SSOT §7 Project A, C13; DEL-5).

The gate decides whether process-effect reasoning is needed at all. Initial implementation is rule-based (§7);
a learned gate needs annotated query categories (benchmark, D-008). No cue -> relevant=None (explicit UNKNOWN);
callers decide how to treat UNKNOWN, the gate does not guess.
"""
from __future__ import annotations

import re
import unicodedata

from culinarystate.decision import safety as SF

VERSION = "relevance_rules@0.2"      # S176: inflected process forms ("fried", "seared", ...) and the SAFETY intent
# process stems. "fried" is its own stem (fry-ing / fry but fri-ed); "\b" before it also matches "deep-fried",
# "pan-fried", "stir-fried", "air fried". Short ambiguous stems carry an explicit ending ("sear" is not "search",
# "char" is not "charcoal"). "fries" (noun) and "smok*" (cigarettes) are deliberately absent.
_P = (r"(?:boil|fry|fried|roast|bake|steam|grill|microwav|simmer|brown|saut|blanch|poach|stew|braise|toast|cook|broil|"
      r"sear(?:ed|ing)?\b|charred\b|charring\b|barbecu|bbq|scrambl|parboil|caramel|reheat|sous[- ]vide|"
      r"freez|froze|thaw|defrost|ferment|pickl|dehydrat|dried\b|drying\b|canned\b|canning\b)\w*")
HIGH = (("SUBSTITUTION", r"\binstead of\b|\bsubstitut\w*|\bswap\b|\breplace\b"),
        ("WHY_PROCESS", rf"\bwhy (?:do|does|should|must|would) (?:i|we|you) (?:need to |have to )?{_P}"),
        ("RECOVERY", r"\baccident\w*|\brecover\w*|\brescue\b|\bsalvage\b|\bfix (?:it|this)\b|\bruin\w*"),
        ("WHAT_IF", r"\bwhat (?:changes|happens|would happen) if\b"),
        ("OUTCOME", rf"\bwill {_P}.*\b(?:same|produce|change|affect|keep|lose)\b"),
        ("PROCESS_EFFECT", r"\b(?:retention|retain|lose|loss|destroy\w*|keep)\b.*\b(?:vitamin|nutrient|mineral|"
                           r"colour|color|texture|flavou?r)\w*"),
        ("FAILURE", r"\b(?:burnt|burned|overcooked|undercooked|soggy|curdled|split|too (?:salty|dry|thick|thin|bitter))\b"))
LOW = (("NAVIGATION", r"\bnext (?:step|instruction)\b|\bprevious step\b|\bwhat is step\b"),
       ("COUNT", r"\bhow many\b(?!.*\b(?:lose|retain|keep)\b)"),
       ("TRANSFER", r"^\s*(?:move|transfer|put|place|set aside)\b"),
       ("OUT_OF_SCOPE", r"\b(?:joke|poem|story|song|riddle|limerick)s?\b"))
INTENT = (("SAFETY", None),   # decided by safety.is_safety (strong / weak cue tiers), checked first
          ("RECOVER", r"\baccident\w*|\brecover\w*|\brescue\b|\bsalvage\b|\bfix (?:it|this)\b|\bsave (?:it|this)\b"),
          ("DIAGNOSE", r"\bwhy (?:did|is|are|has|have|does)\b.*\b(?:split|curdle\w*|soggy|dry|tough|bitter|burn\w*|"
                       r"sink|sank|collapse\w*|turn\w*|become|go|went)\b|\bwhat went wrong\b"),
          ("COMPARE", r"\binstead of\b|\bvs\.?\b|\bversus\b|\bcompared? (?:to|with)\b|\bdifference between\b|"
                      r"\bwhich is better\b|\bor\b.*\b(?:more|less|better|worse)\b|"
                      r"\b(?:more|less|better|worse)\b.*\bor\b"),
          ("RECOMMEND", r"\bwhat should i\b|\bhow (?:should|can|do) i\b|\bbest way\b|\brecommend\w*|\bsuggest\w*"))


def fold_accents(q: str) -> str:
    """Accent-folded copy for process matching ("sautéed" -> "sauteed"); callers keep the original for linking foods."""
    return "".join(c for c in unicodedata.normalize("NFKD", q) if not unicodedata.combining(c))


def relevance_gate(query: str) -> dict:
    if not query or not query.strip():
        return {"relevant": None, "reason": "MALFORMED_EMPTY", "cue": None, "version": VERSION, "raw": query}
    q = re.sub(r"\s+", " ", query.lower())             # surface variation: spacing never changes the gate
    for name, pat in HIGH:
        if re.search(pat, q):
            return {"relevant": True, "reason": name, "cue": re.search(pat, q).group(0), "version": VERSION, "raw": query}
    for name, pat in LOW:
        if re.search(pat, q):
            return {"relevant": False, "reason": name, "cue": re.search(pat, q).group(0), "version": VERSION, "raw": query}
    return {"relevant": None, "reason": "NO_CUE", "cue": None, "version": VERSION, "raw": query}


def intent(query: str) -> str:
    q = re.sub(r"\s+", " ", (query or "").lower())
    if SF.is_safety(q):
        return "SAFETY"
    return next((name for name, pat in INTENT if pat and re.search(pat, q)), "ANSWER")
