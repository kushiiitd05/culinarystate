"""B4 state conditioning (SSOT RQ16-01, Plan B4 = B3 + reconstructed state): fill slots the question leaves empty
from the reconstructed session state. Question slots always win; nothing is guessed when the focus entity is ambiguous.

Focus entity: an alive entity named in the question, else the only alive entity, else none (policy then asks).
Ingredient: LineLinker mention inside the entity label ("rice pot" -> rice). Process: the entity's last_process
field when the question names none. Returns (new Slots, trace) so every filled slot is auditable against the state.
"""
from __future__ import annotations

import re
from dataclasses import replace

VERSION = "state_conditioning@0.1"


def _focus(question: str, session) -> str | None:
    alive = session.alive_entities()
    named = [e for e in alive if re.search(rf"(?<!\w){re.escape(e.lower())}(?!\w)", question.lower())]
    if len(named) == 1:
        return named[0]
    return alive[0] if len(alive) == 1 and not named else None


def condition_slots(question: str, slots, session, lex):
    ent = _focus(question, session) if session else None
    if ent is None:
        return slots, {}
    trace: dict = {}
    out = slots
    if slots.ingredient_id is None:
        ments = lex.linker.mentions(ent)
        if ments:
            ing = ments[0]
            name = next((n for n, i in lex.linker.names.items() if i == ing), None)
            out = replace(out, ingredient_id=ing, ingredient_name=name, parents=tuple(lex.parents.get(ing, ())))
            trace["ingredient"] = {"entity": ent, "ing_id": ing}
    if not slots.processes:
        lp = (session.current_state(ent) or {}).get("fields", {}).get("last_process", {}).get("value")
        pid = lex.proc_ids.get(lp) if lp else None
        if pid:
            out = replace(out, processes=((lp, pid),))
            trace["process"] = {"entity": ent, "from": "last_process", "name": lp}
    return out, trace
