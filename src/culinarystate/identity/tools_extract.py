"""STEP 07I: utensil/appliance mention candidates from the TOOL vocabulary (word-boundary alias match; no mechanism inference). Structural class is assigned from the existing TOOL.category only."""
from __future__ import annotations

import re

from culinarystate.recipes import ledgers as LG

_RX = None
_MAP = None


def _build():
    global _RX, _MAP
    v = LG.vocab()
    forms = {}
    for w, (tid, cat) in v.tools.items():
        if re.fullmatch(r"[a-z][a-z \-]{1,30}", w):
            forms[w] = (tid, cat)
            if " " not in w and not w.endswith("s"):
                forms.setdefault(w + "s", (tid, cat))
    _MAP = forms
    _RX = re.compile(r"\b(" + "|".join(re.escape(w) for w in sorted(forms, key=lambda x: -len(x))) + r")\b", re.I)


def tool_mentions(rec: dict) -> list[dict]:
    if _RX is None:
        _build()
    rows = []
    for si, step in enumerate(rec["steps"]):
        for m in _RX.finditer(step):
            tid, cat = _MAP[m.group(1).lower()]
            rows.append({"recipe_id": rec["recipe_id"], "step_index": si, "char_start": m.start(), "char_end": m.end(), "raw_tool": m.group(1), "tool_id": tid, "tool_category": cat, "source_plane": "RECIPE"})
    for e in (rec.get("extra") or {}).get("equipment") or []:
        k = str(e).lower().strip()
        if k in (_MAP or {}):
            tid, cat = _MAP[k]
            rows.append({"recipe_id": rec["recipe_id"], "step_index": None, "char_start": None, "char_end": None, "raw_tool": e, "tool_id": tid, "tool_category": cat, "source_plane": "RECIPE"})
    return rows
