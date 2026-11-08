"""Deterministic verbaliser (C16 template baseline, SSOT §257B.16: "verbalize; do not invent second analysis").

Turns a decision + its evidence packets into fact lines and a plain answer. Every number it prints is a packet
row's retention factor with that row's id, so the C17 checker passes by construction; the precision cap decides
whether numbers appear at all (QUALITATIVE -> direction only, REPORT_CONFLICT -> disagreement only). NEAR rows are
labelled as similar foods/processes and named. Diagnosis/recovery routes verbalise candidates, never evidence rows.
This is the strongest simpler baseline an LLM generator must beat.
"""
from __future__ import annotations

import re
from collections import Counter

from culinarystate.generation.claims import row_value
from culinarystate.retrieval.retriever import EvidencePacket

VERSION = "verbalize@0.2"  # S173: names other-process rows
NO_NUMBERS = {"QUALITATIVE", "REPORT_CONFLICT", "ABSTAIN"}
ABSTAIN_TEXT = {
    "NO_CORROBORATED_CAUSE": "No cause for this is stated by at least two independent sources in the corpus.",
    "NO_CORROBORATED_RECOVERY": "No recovery step for this is stated by at least two independent sources in the corpus.",
    "NO_EVIDENCE_FOR_ANY_TARGET": "There is not enough evidence about this food to answer.",
    "OUT_OF_SCOPE": "That is outside what CulinaryState answers: cooking processes, their effects and recipe state.",
}
VERDICT = {"OVERLAPPING": "The ranges overlap, so the evidence does not show that one method keeps more.",
           "SEPARATED": "The ranges do not overlap.",
           "INSUFFICIENT": "Too few independent sources to compare the options."}
CHECK = {"CONSISTENT": "consistent with your steps", "INCONSISTENT": "not in your steps",
         "UNVERIFIABLE": "cannot be checked from your steps"}


def _cite(rows: list[dict]) -> str:
    return "".join(f"[{r['id']}]" for r in rows)


def _food(name: str) -> str:
    """Short food label: drop the "such as …" tail of group names, lower-case ALL-CAPS FDC names."""
    s = re.split(r",?\s+such as\b", name)[0].strip(" -,")
    return s.lower() if s.isupper() else s


def _other_processes(p: EvidencePacket, key: str) -> str:
    """S173: name the processes of near rows that were not measured under the asked process."""
    other = list(dict.fromkeys(h.row["process"].get("raw_name") for h in p.near
                               if (h.compat.get("match") or {}).get("process") not in (None, "EXACT", "STEP")
                               and h.row["process"].get("raw_name")))
    return f"; measured for other processes ({', '.join(other[:3])}), not {key}" if other else ""


def _label(p: EvidencePacket, key: str) -> str:
    if p.direct:
        return key
    foods = list(dict.fromkeys(_food(h.row["matrix"]["raw_name"]) for h in p.near if h.row["matrix"].get("raw_name")))
    procs = _other_processes(p, key)
    if p.near and all((h.compat.get("match") or {}).get("matrix") == "UNKNOWN" for h in p.near):
        return f"{key} (other foods, relation to yours unknown: {', '.join(foods[:3])}{procs})"
    return f"{key} (similar foods only: {', '.join(foods[:3])}{procs})"


def _measured(r: dict) -> bool:                           # censored limits are bounds, not values
    return ((r.get("derived") or {}).get("retention_factor") or {}).get("status") == "MEASURED"


def _line(key: str, p: EvidencePacket, precision: str | None) -> str:
    rows = [h.row for h in (p.direct or p.near)]
    if not rows:
        return f"{key}: UNKNOWN — no evidence rows."
    target, label = rows[0]["target"].get("raw_name", "the nutrient"), _label(p, key)
    groups = len({r["independence_group"] for r in rows if r.get("independence_group")})
    if precision == "REPORT_CONFLICT" or p.evidence_class == "CONFLICT":
        dirs = sorted({(r.get("derived") or {}).get("direction", "UNKNOWN") for r in rows} - {"UNKNOWN"})
        return f"{label}: sources disagree on {target} ({' vs '.join(dirs).lower() or 'mixed'}) {_cite(rows[:3])}."
    vals = sorted(((v, r) for r in rows if _measured(r) and (v := row_value(r)) is not None), key=lambda x: x[0])
    if precision in NO_NUMBERS or not vals:
        d = Counter((r.get("derived") or {}).get("direction", "UNKNOWN") for r in rows).most_common(1)[0][0]
        return f"{label}: mostly a {d.lower()} in {target} across {len(rows)} rows {_cite(rows[:3])}."
    (lo, rlo), (hi, rhi) = vals[0], vals[-1]
    if rlo is rhi or abs(hi - lo) < 0.005:
        return f"{label}: {target} retention factor {lo:.2f} {_cite([rlo])}."
    src = f" from {groups} independent source{'s' * (groups != 1)}" if groups else ""
    return f"{label}: {target} retention factor from {lo:.2f} {_cite([rlo])} to {hi:.2f} {_cite([rhi])} across {len(rows)} rows{src}."


def _diagnosis(d: dict) -> list[str]:
    dg = d.get("diagnosis") or {}
    if d["mode"] == "RECOVER":
        sup = {r["action"]: r["support_sources"] for r in dg.get("recovery", [])}
        return ["Recovery steps stated in cookbooks (not controlled tests):"] + [
            f"- {a} ({sup.get(a, 1)} sources)" for a in d.get("recovery_options", [])]
    out = ["This may happen when (cookbook statements, not controlled tests):"]
    out += [f"- {c['cause']} ({c['support_sources']} sources; {CHECK[c['verdict']]})" for c in dg.get("causes", [])]
    if dg.get("prevention"):
        short = sorted((r["action"] for r in dg["prevention"]), key=len)[:3]      # long Gutenberg sentences last
        out.append("To prevent it: " + "; ".join(a for a in short if len(a) <= 100 or a == short[0]) + ".")
    return out


def facts(d: dict, packets: dict[str, EvidencePacket]) -> dict:
    """Fact lines the answer may contain — the only content an LLM generator is allowed to rephrase."""
    mode, route, per = d.get("mode"), d.get("route"), d.get("per_option") or {}
    if not mode:
        raise ValueError("MISSING_MODE: a decision without a mode cannot be verbalised")
    if mode == "ASK":
        opts = d.get("ask_options") or []
        lines = [f"Which {' and '.join(d.get('ask_for') or ['detail'])} do you mean?"
                 + (f" For example: {', '.join(opts)}." if opts else "")]
    elif mode == "ABSTAIN":
        lines = [ABSTAIN_TEXT.get(d.get("reason"), "There is not enough evidence to answer this reliably.")]
    elif route == "RECIPE_STATE":
        lines = ["No active recipe session is loaded, so the next step is unknown. Start a recipe session first."]
    elif route == "DIAGNOSIS":
        lines = _diagnosis(d)
    elif mode == "RECOVER":
        lines = ["No recovery evidence was found for this. What the cooking step does here:"] + [
            _line(k, p, "REPORT_CONFLICT" if (per.get(k) or d.get("cause_evidence", {}).get(k) or {}).get("precision")
                  == "REPORT_CONFLICT" else "QUALITATIVE") for k, p in packets.items()]
    elif mode in ("COMPARE", "RECOMMEND"):
        keys = d.get("alternatives") or list(per) or list(packets)
        lines = [_line(k, packets[k], (per.get(k) or {}).get("precision")) for k in keys if k in packets]
        if mode == "COMPARE":
            lines.append(VERDICT.get((d.get("comparison") or {}).get("verdict"), VERDICT["INSUFFICIENT"]))
        else:
            lines.insert(0, "Options that fit your constraints (not ranked):")
    else:
        k, p = next(iter(packets.items()), ("answer", EvidencePacket("", None, "UNSUPPORTED")))
        lines = ([] if p.direct or not p.near else ["No measurement for this exact food and process."]) + \
            [_line(k, p, d.get("precision"))]
    return {"version": VERSION, "mode": mode, "route": route, "lines": lines}


def verbalize(q: str, d: dict, packets: dict[str, EvidencePacket]) -> str:
    return "\n".join(facts(d, packets)["lines"])
