"""Rule-based recipe -> events baseline (DEL-3 system baseline "B-rules").

Deterministic and transparent so failures are inspectable against Gold:
  * ingredient lines -> Add (entity label = cleaned food phrase; concept = longest registry name inside it)
  * per step: processes in text order (phrases first, then verb lemmas via a light inflection matcher)
      reserve phrase            -> Reserve(current target, portion parsed from the sentence if any)
      drain / strain            -> Split(target -> drained, liquid) + Discard(liquid) or Reserve if "reserving"
      divide … into N (equal)   -> Split into N (fractions only if "equal"/"equally")
      combination verbs         -> Merge(current mixture + mentioned unmerged entities) -> new mixture
      transfer verb + tool word -> Transfer(current, tool)
      other actions             -> Transform(each mentioned entity, or current mixture)
No quantities are invented: amounts come from the quantity grammar only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from fractions import Fraction

from culinarystate.process.vocab import BY_CANON, LEMMA_TO_PROC, phrase_processes
from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.normalize import normalize

from .engine import Add, Discard, Merge, Recombine, Reserve, Split, Transfer, Transform
from .symqty import Base

COMBINE = {"add", "stir", "mix", "whisk", "fold", "toss", "pour", "beat", "blend", "combine", "season", "dress",
           "rub-in", "coat", "spoon", "drizzle", "sprinkle", "top", "fill", "spread", "dissolve"}
TRANSFER_PROCS = {"put", "transfer", "tip", "return", "arrange", "spoon", "pour"}
TOOLS = ("baking tray", "roasting tin", "frying pan", "saucepan", "casserole", "oven", "tin", "tray", "dish", "bowl",
         "pan", "wok", "jug", "blender", "food processor", "plate", "fridge", "freezer", "griddle", "slow cooker")
MIXTURE_WORDS = ("mixture", "batter", "dough", "sauce", "paste", "filling", "dressing", "marinade", "mix")
NUM_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "eight": 8, "ten": 10, "twelve": 12}
_INFL = re.compile(r"\b[A-Za-z]+(?:-[A-Za-z]+)?\b")


def _lemma_guess(word: str) -> str | None:
    w = word.lower()
    for cand in (w, w[:-1] if w.endswith("s") else None, w[:-2] if w.endswith("es") else None,
                 w[:-3] if w.endswith("ing") else None, w[:-3] + "e" if w.endswith("ing") else None,
                 w[:-4] if w.endswith("ing") and len(w) > 5 and w[-4] == w[-5] else None,
                 w[:-2] if w.endswith("ed") else None, w[:-1] if w.endswith("ed") else None,
                 w[:-3] if w.endswith("ed") and len(w) > 4 and w[-3] == w[-4] else None,
                 w[:-3] + "y" if w.endswith("ied") else None):
        if cand and cand in LEMMA_TO_PROC:
            return LEMMA_TO_PROC[cand]
    return None


# aliases that are usually nouns in recipe text: count only in imperative/verb position
NOUNY = {"butter", "oil", "salt", "top", "dust", "pick", "juice", "stone", "core", "cube", "skin", "press", "set",
         "pot", "spoon", "season", "zest", "dot", "quarter", "process", "build", "pack", "mill", "golden", "tender",
         "colour", "color", "rise", "firm", "turn", "rest", "stand", "sit", "keep", "save", "take", "move", "empty",
         "heat", "cook"}
_VERB_SLOT = re.compile(r"(?:^|[.;:,!]\s*|\b(?:then|and|or|to|until|before|after|gently|carefully|quickly|"
                        r"lightly|well|briefly)\s+)$", re.IGNORECASE)


def step_processes(text: str) -> list[tuple[int, str]]:
    """(char position, canonical process) in order; phrases override their verbs."""
    out = []
    for m in _INFL.finditer(text):
        w = m.group(0).lower()
        p = LEMMA_TO_PROC.get(w) or _lemma_guess(w)
        if not p:
            continue
        base = w if w in LEMMA_TO_PROC else None
        if (base in NOUNY or w in NOUNY) and not _VERB_SLOT.search(text[:m.start()]):
            continue
        if w.endswith("ed") and re.search(r"\bthe\s+$", text[:m.start()], re.IGNORECASE):
            continue                                            # "the reserved water" is an adjective
        out.append((m.start(), p))
    out = [(i, p) for i, p in out if p and BY_CANON[p].kind == "ACTION"]
    for p in phrase_processes(text):
        out.append((0, p))
    seen, ordered = set(), []
    for i, p in sorted(out):
        if p not in seen:
            seen.add(p)
            ordered.append((i, p))
    return ordered


def _clean_food(rest: str) -> str:
    rest = re.split(r",|\(| or | to serve| for ", rest)[0]
    rest = re.sub(r"\b(finely|roughly|thinly|freshly|chopped|sliced|grated|diced|crushed|peeled|halved|minced|"
                  r"softened|melted|beaten|large|small|medium)\b", " ", rest.lower())
    return re.sub(r"\s+", " ", rest).strip() or "ingredient"


@dataclass
class _Ctx:
    entities: dict[str, str] = field(default_factory=dict)      # label -> concept (or "")
    alive: list[str] = field(default_factory=list)
    current: str | None = None
    last: str | None = None                                     # last entity acted on (drain fallback)
    n_mix: int = 0


def _mentions(text: str, ctx: _Ctx) -> list[str]:
    t = text.lower()
    found = []
    for label in ctx.alive:
        concept = ctx.entities.get(label) or ""
        heads = {label, label.split()[-1]} | ({concept, concept.split()[-1]} if concept else set())
        heads = {h for h in heads if len(h) > 2 and not h.startswith(("mixture", "reserved", "liquid"))}
        if label.startswith("reserved ") and "reserv" not in t:
            continue                                            # reserved portions need an explicit mention
        if any(re.search(rf"\b{re.escape(h)}(e?s)?\b", t) for h in heads):
            found.append(label)
    if ctx.current and ctx.current in ctx.alive and any(re.search(rf"\b{w}\b", t) for w in MIXTURE_WORDS):
        if ctx.current not in found:
            found.append(ctx.current)
    return found


def compile_recipe(ingredient_lines: list[str], steps: list[str], concept_names: set[str] | None = None,
                   locale: str = "UK") -> list:
    concept_names = concept_names or set()
    ctx = _Ctx()
    events: list = []
    for line in ingredient_lines:
        p = parse_line(line)
        z = normalize(p, locale=locale)
        label = _clean_food(p.rest or line)
        base_label = label
        k = 2
        while label in ctx.entities:
            label = f"{base_label} {k}"
            k += 1
        concept = max((c for c in concept_names if re.search(rf"\b{re.escape(c)}\b", label)), key=len, default="")
        ctx.entities[label] = concept
        ctx.alive.append(label)
        events.append(Add(label, concept or None, Base.from_channels(z.mass_g, z.volume_ml, z.count, line.strip())))
    for k, step in enumerate(steps):
        for sent in re.split(r"(?<=[.!?])\s+", step):
            events += _compile_sentence(sent, ctx, k, locale)
    return events


def _new_mix(ctx: _Ctx) -> str:
    ctx.n_mix += 1
    return f"mixture {ctx.n_mix}"


def _compile_sentence(sent: str, ctx: _Ctx, k: int, locale: str) -> list:  # noqa: C901
    evs: list = []
    procs = [p for _, p in step_processes(sent)]
    if not procs:
        return evs
    ment = _mentions(sent, ctx)
    low = sent.lower()
    target = ment[0] if ment else (ctx.current or ctx.last)
    if "reserve" in procs and target in ctx.alive and "drain" not in procs:
        q = re.search(r"\d+(?:\.\d+)?\s*(?:tbsp|tsp|ml|g|cup)s?", low)
        portion = None
        if q:
            z = normalize(parse_line(q.group(0)), locale=locale)
            portion = Base.from_channels(z.mass_g, z.volume_ml, z.count, q.group(0))
        out = f"reserved {target}"
        if out not in ctx.entities:
            evs.append(Reserve(target, out, portion=portion, fraction=None if portion else Fraction(1, 2)
                               if "half" in low else None, step=k))
            ctx.entities[out] = ctx.entities.get(target, "")
            ctx.alive.append(out)
        return evs
    if ("drain" in procs or "strain" in procs) and target in ctx.alive:
        kept, liquid = f"{target} drained", f"liquid from {target}"
        evs.append(Split(target, ((kept, None), (liquid, None)), step=k))
        ctx.alive = [a for a in ctx.alive if a != target] + [kept, liquid]
        ctx.entities[kept] = ctx.entities.get(target, "")
        ctx.entities[liquid] = ""
        if "reserv" in low:
            evs.append(Reserve(liquid, f"reserved {liquid}", step=k))
            ctx.alive.append(f"reserved {liquid}")
            ctx.entities[f"reserved {liquid}"] = ""
        evs.append(Discard(liquid, step=k))
        ctx.alive.remove(liquid)
        if ctx.current == target:
            ctx.current = kept
        return evs
    if "divide" in procs and target in ctx.alive:
        m = re.search(r"into (\d+|" + "|".join(NUM_WORDS) + r")\b", low)
        n = (int(m.group(1)) if m.group(1).isdigit() else NUM_WORDS[m.group(1)]) if m else 2
        frac = Fraction(1, n) if re.search(r"\bequal(ly)?\b", low) else None
        outs = tuple((f"{target} part {i + 1}", frac) for i in range(n))
        evs.append(Split(target, outs, step=k))
        ctx.alive = [a for a in ctx.alive if a != target] + [o for o, _ in outs]
        for o, _ in outs:
            ctx.entities[o] = ctx.entities.get(target, "")
        return evs
    reserved = [m for m in ment if m.startswith("reserved ")]
    ment = [m for m in ment if not m.startswith("reserved ")]
    cooks_in = bool(re.search(r"\b(in|with)\b", low)) and len(ment) >= 2      # "fry the garlic in the oil"
    if any(p in COMBINE for p in procs) or cooks_in:
        inputs = [m for m in ment if m in ctx.alive]
        if ctx.current and ctx.current in ctx.alive and ctx.current not in inputs and inputs:
            inputs = [ctx.current] + inputs
        if len(inputs) >= 2:
            out = _new_mix(ctx)
            proc = next((p for p in procs if p in COMBINE), procs[0])
            evs.append(Merge(tuple(inputs), out, proc, step=k))
            ctx.alive = [a for a in ctx.alive if a not in inputs] + [out]
            ctx.entities[out] = ""
            ctx.current = out
            target = out
            ment = [out]
    for r in reserved:
        if r in ctx.alive and target in ctx.alive and r != target:
            evs.append(Recombine(r, target, step=k))
            ctx.alive.remove(r)
    tool = next((t for t in TOOLS if re.search(rf"\b{t}\b", low)), None)
    if tool and any(p in TRANSFER_PROCS for p in procs) and target in ctx.alive:
        evs.append(Transfer(target, tool, step=k))
    for p in procs:
        if p in COMBINE or p in TRANSFER_PROCS or p in {"reserve", "serve", "preheat", "adjust-heat"}:
            continue
        for tgt in (ment or ([ctx.current] if ctx.current else [])):
            if tgt in ctx.alive:
                evs.append(Transform(tgt, p, step=k))
                ctx.last = tgt
    return evs
