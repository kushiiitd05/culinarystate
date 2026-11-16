"""Step 21 gate checkers G21.2 / G21.3 / G21.4 / G21.8 over the draft MECH entries (S178 lane MECH). AI_DRAFTED.

Reads ``registry/mech_entries_draft_v1.jsonl`` (envelope + MECH v1.1 entry per line, see ``mech_entries``) and reports:

- schema / semantic validity of every ``mech`` object (``mech_contract.schema_errors`` / ``semantic_problems``) and the
  registry-level link checks (``asymmetric_links``, ``unresolved_links``);
- envelope rules of this lane: ``provenance_class`` AI_DRAFTED; ``evidence_status`` is UNSOURCED exactly when the entry has
  no evidence ref; an UNSOURCED entry never counts toward G21.4; window refs exist in the windows registry; a screen entry
  binds every precondition, every NECESSARY gate and every inhibitor to an evaluator the screen knows;
- **G21.2** every SSOT 144.1 family plus the leaching, volatilisation and moisture-loss keys has >= 1 entry;
- **G21.3** 100 % of entries have >= 1 precondition or NECESSARY gate, or ``gates_unknown`` true;
- **G21.4** 100 % have >= 1 evidence id with document type, counting only SOURCED entries (an opened source with a
  locator); with no opened source the gate is honestly NOT met;
- **G21.8** zero numeric kinetic fields: no kinetic key anywhere and no numeric leaf other than the record ``version``.

A gate result is a check of this draft file, not H4 approval and not a human review (G21.1, G21.5-G21.7 are human gates).
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.mechanism import mech_contract as MC
from culinarystate.mechanism import mech_entries as ME

CHECK_VERSION = "mech-registry-check-0.1.0-draft"
# SSOT 144.1 families as the v1.1 family enum spells them (MICRONUTRIENT_DEGRADATION and UNRESOLVED are not 144.1 families)
SSOT_144_1_FAMILIES = ("MAILLARD_GLYCATION", "SUGAR_THERMAL_DEGRADATION", "LIPID_OXIDATION_DECOMPOSITION",
                       "PROTEIN_STRUCTURAL", "COLLAGEN_TRANSITION", "STARCH_TRANSITION", "CUTTING_TRIGGERED_ENZYMATIC",
                       "FERMENTATION", "VOLATILE_MATERIAL_TRANSFER", "PIGMENT_CELLWALL_TRANSITION")
G21_2_KEYS = ("LEACHING", "VOLATILISATION", "MOISTURE_LOSS")
# key names that would carry a kinetic number (G21.8); matched case-insensitively against every dict key
KINETIC_KEYS = frozenset({"k", "k_ref", "k_d", "rate", "rate_constant", "ea", "activation_energy", "a", "pre_exponential",
                          "half_life", "t_half", "q10", "z", "z_value", "d_value", "order", "reaction_order", "t_ref",
                          "optimum", "opt", "default", "typical", "midpoint", "value_default"})
ALLOWED_NUMERIC_PATHS = frozenset({("version",)})


def _walk(node: Any, path: tuple = ()) -> Iterable[tuple[tuple, Any]]:
    if isinstance(node, Mapping):
        for k, v in node.items():
            yield from _walk(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, path + (i,))
    else:
        yield path, node


def numeric_leaves(entry: Mapping[str, Any]) -> list[str]:
    """Paths of numeric leaves (bool excluded) other than the record version."""
    return ["/".join(map(str, p)) for p, v in _walk(entry)
            if isinstance(v, (int, float)) and not isinstance(v, bool) and p not in ALLOWED_NUMERIC_PATHS]


def _has_number(v: Any) -> bool:
    return any(isinstance(x, (int, float)) and not isinstance(x, bool) for _, x in _walk({"_": v}))


def kinetic_keys(entry: Mapping[str, Any]) -> list[str]:
    """Kinetic-named keys that carry a number anywhere below them (a schema key such as ``consecutive_with.order``,
    an enum THIS_PRECEDES_OTHER, is not a kinetic field)."""
    out = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for k, v in node.items():
                if str(k).lower() in KINETIC_KEYS and _has_number(v):
                    out.append(f"{path}/{k}")
                walk(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}/{i}")
    walk(entry, "")
    return out


def g21_3_ok(e: Mapping[str, Any]) -> bool:
    return bool(e["preconditions"]) or any(g["gate_type"] == "NECESSARY" for g in e["condition_gates"]) \
        or bool(e["gates_unknown"])


def sourced(x: Mapping[str, Any]) -> bool:
    """An entry counts toward G21.4 only when the lane opened its source(s): SOURCED envelope + >= 1 ref with a locator."""
    refs = x["mech"]["evidence_refs"]
    return x.get("evidence_status") == "SOURCED" and bool(refs) and all(r.get("doc_type") and r.get("locator")
                                                                         for r in refs)


def envelope_problems(x: Mapping[str, Any], known_windows: set[str], evaluators: set[str]) -> list[str]:
    e, out = x["mech"], []
    k = e["mechanism_key"]
    if x.get("provenance_class") != "AI_DRAFTED":
        out.append(f"{k}: envelope provenance_class must be AI_DRAFTED")
    if not e.get("ai_drafted") or e.get("review_status") != "CANDIDATE":
        out.append(f"{k}: an AI-drafted entry stays ai_drafted true and CANDIDATE")
    has_refs = bool(e["evidence_refs"])
    if x.get("evidence_status") == "UNSOURCED" and has_refs:
        out.append(f"{k}: UNSOURCED but evidence_refs present")
    if x.get("evidence_status") not in ("UNSOURCED", "SOURCED"):
        out.append(f"{k}: evidence_status must be UNSOURCED or SOURCED")
    if x.get("evidence_status") == "SOURCED" and not sourced(x):
        out.append(f"{k}: SOURCED needs evidence refs with doc_type and locator")
    if x.get("counts_toward_g21_4") != sourced(x):
        out.append(f"{k}: counts_toward_g21_4 must equal the sourced test")
    bad = set(x.get("window_refs") or []) - known_windows
    if bad:
        out.append(f"{k}: unknown window refs {sorted(bad)}")
    b = x.get("screen_binding")
    if x.get("screen_subset"):
        if not b:
            out.append(f"{k}: screen entry without binding")
            return out
        need = [p["precondition_key"] for p in e["preconditions"]] \
            + [g["gate_key"] for g in e["condition_gates"] if g["gate_type"] == "NECESSARY"] \
            + [i["inhibitor_key"] for i in e["inhibitors_mitigators"] if i["role"] in ("INHIBITOR", "MITIGATOR")]
        if sorted(need) != sorted(b["items"]):
            out.append(f"{k}: binding items {sorted(b['items'])} != evaluable items {sorted(need)}")
        if b.get("evaluation_order") and sorted(b["evaluation_order"]) != sorted(b["items"]):
            out.append(f"{k}: evaluation_order does not list exactly the bound items")
        for ik, it in b["items"].items():
            if it["evaluator"] not in evaluators:
                out.append(f"{k}: {ik} names unknown evaluator {it['evaluator']}")
        if e["gates_unknown"]:
            out.append(f"{k}: a screen entry must not be gates_unknown")
    elif b:
        out.append(f"{k}: binding on a non-screen entry")
    return out


def check(entries: Sequence[Mapping[str, Any]], *, known_windows: set[str] | None = None,
          evaluators: set[str] | None = None) -> dict[str, Any]:
    """Counts-only gate report over the draft entries."""
    if evaluators is None:
        from culinarystate.mechanism import mech_inputs as MI
        evaluators = set(MI.EVALUATORS)
    known = known_windows if known_windows is not None else ME.window_ids()
    cv, eff = MC.read_cv_rows(), MC.read_effect_rows()
    mech = [x["mech"] for x in entries]
    schema_bad = {m["mechanism_key"]: MC.schema_errors(m) for m in mech}
    sem_bad = {m["mechanism_key"]: MC.semantic_problems(m, cv, effect_rows=eff) for m in mech}
    env = [p for x in entries for p in envelope_problems(x, known, evaluators)]
    keys = Counter(m["mechanism_key"] for m in mech)
    fams = Counter(m["family"] for m in mech)
    g2_missing = [f for f in SSOT_144_1_FAMILIES if not fams[f]] + [k for k in G21_2_KEYS if not keys[k]]
    g3_fail = [m["mechanism_key"] for m in mech if not g21_3_ok(m)]
    g4_counted = sum(1 for x in entries if sourced(x))
    g8_numeric = {m["mechanism_key"]: numeric_leaves(m) for m in mech}
    g8_kinetic = {m["mechanism_key"]: kinetic_keys(m) for m in mech}
    n = len(mech)
    return {
        "record": "MECH_DRAFT_GATE_CHECK", "check_version": CHECK_VERSION, "status": "AI_DRAFTED_CHECK_NOT_A_HUMAN_GATE",
        "entries": n, "screen_subset_entries": sum(1 for x in entries if x.get("screen_subset")),
        "duplicate_keys": sorted(k for k, c in keys.items() if c > 1),
        "schema_invalid_entries": sorted(k for k, v in schema_bad.items() if v),
        "semantic_problem_entries": sorted(k for k, v in sem_bad.items() if v),
        "asymmetric_links": len(MC.asymmetric_links(mech)), "unresolved_links": len(MC.unresolved_links(mech)),
        "envelope_problems": env,
        "evidence_status": dict(sorted(Counter(x.get("evidence_status") for x in entries).items())),
        "provenance_class": dict(sorted(Counter(x.get("provenance_class") for x in entries).items())),
        "gates_unknown_entries": sum(1 for m in mech if m["gates_unknown"]),
        "kinds": dict(sorted(Counter(m["kind"] for m in mech).items())),
        "families": dict(sorted(fams.items())),
        "G21_2": {"pass": not g2_missing, "missing": g2_missing},
        "G21_3": {"pass": not g3_fail, "entries_ok": n - len(g3_fail), "entries": n, "failing": g3_fail},
        "G21_4": {"pass": n > 0 and g4_counted == n, "entries_counted": g4_counted, "entries": n,
                  "rule": "ONLY_SOURCED_ENTRIES_COUNT_UNSOURCED_NEVER"},
        "G21_8": {"pass": not any(g8_numeric.values()) and not any(g8_kinetic.values()),
                  "entries_with_numeric_leaf": sorted(k for k, v in g8_numeric.items() if v),
                  "entries_with_kinetic_key": sorted(k for k, v in g8_kinetic.items() if v)},
        "xrefs_accepted": sum(1 for m in mech for x in m["xrefs"] if x["xref_status"] == "ACCEPTED")
        + sum(1 for m in mech if m["enzyme"] for x in (m["enzyme"]["ec"], m["enzyme"]["go_mf"], m["enzyme"]["rhea"])
              if x and x["xref_status"] == "ACCEPTED"),
        "consumable_for_applicability": sum(1 for m in mech if MC.consumable_for_applicability(m)[0]),
    }
