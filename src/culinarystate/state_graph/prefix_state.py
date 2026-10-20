"""Base-ingredient ancestry, processes, reserved set and prior events along an event prefix (used by H_STATE tooling)."""
from collections import defaultdict

from .engine import Add


def prefix_state(ev, k, concept):
    """Alive entities, base-ingredient ancestry and processes applied along the prefix ev[:k]."""
    adds = {e.label for e in ev if isinstance(e, Add)}
    anc = {a: {a} for a in adds}
    procs, reserved, prior = defaultdict(set), set(), defaultdict(list)
    for e in ev[:k]:
        nm = type(e).__name__
        if nm == "Merge":
            anc[e.output] = set().union(*[anc.get(x, {x}) for x in e.inputs])
            for x in e.inputs:
                procs[e.output] |= procs.get(x, set())
                prior[e.output] += prior.get(x, [])
            procs[e.output].add(e.process)
            prior[e.output].append("Merge")
        elif nm in ("Split", "Reserve"):
            outs = [o for o, _ in e.outputs] if nm == "Split" else [e.output]
            src = e.source
            for o in outs:
                anc[o] = set(anc.get(src, {src}))
                procs[o] = set(procs.get(src, set()))
                prior[o] = list(prior.get(src, [])) + [nm]
                if nm == "Reserve":
                    reserved.add(o)
        elif nm == "Transform":
            procs[e.target].add(e.process)
            prior[e.target].append("Transform")
    return anc, procs, reserved, prior
