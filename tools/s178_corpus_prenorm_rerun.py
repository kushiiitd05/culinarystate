#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C07-R1: re-run the rc2 quantity grounding on the non-BBC families with the opt-in SP-002
pre-normaliser and report BEFORE / AFTER counts and how many lines change per family (counts only).

BEFORE = the frozen pipeline (`ground_quantity_rc2`, exactly the S154/S161 dry-run semantics, locale from the legacy family
map). AFTER = `culinarystate.quantity.prenormalize.ground_quantity_rc2_prenorm` (rules SP002_U2044, SP002_GLUED_REFUSE,
SP002_HYPHEN_MIXED). Lines are de-duplicated before grounding (the result depends only on the line text and the family
locale), then counted with their multiplicity; an unaffected line has AFTER == BEFORE by construction (the opt-in entry
point calls the frozen function), which the unit tests prove, and `--verify-unaffected N` re-checks on N such unique lines.

The BEFORE marginals use the same keys as `quantity/rc2_dryrun.py` and are compared with the committed S161 counts
(`reports/step16/rc2_grounding_dryrun_counts.json`, per family) when the full family is run.

Outputs (counts only; no line, recipe id or unit token): reports/s178/corpus/sp002_prenorm_rerun_v1.json (+ .md).
Families: FOODCOM, WIKIBOOKS, TASTESET (GUTENBERG_SEGMENT has no ingredient lines; BBC is not on this server, D-003).

  nice -n 10 python tools/s178_corpus_prenorm_rerun.py --sample 1000 --seed 20261104 --out-dir <scratch>   # smoke
  nice -n 10 python tools/s178_corpus_prenorm_rerun.py --workers 16
AI_DRAFTED / PROPOSED. Engineering coverage, not a quality estimate and not a human gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from multiprocessing import get_context
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-corpus-prenorm-rerun-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
FAMILIES = ("FOODCOM", "WIKIBOOKS", "TASTESET")
S161 = "reports/step16/rc2_grounding_dryrun_counts.json"
MARGINAL_AXES = ("mass_route", "unit_resolution", "ast_root", "arithmetic_status", "q_level", "flags", "issue_codes",
                 "legacy_vs_rc2_mass")
SCALARS = ("lines_total", "lines_blank", "lines_grounded", "lines_contract_valid", "lines_with_rc2_mass",
           "lines_with_rc2_volume", "lines_with_rc2_count", "lines_flagged")
TRANSITION_FIELDS = ("mass_route", "unit_resolution", "ast_root", "arithmetic_status", "q_level", "rc2_mass_status")

_SCHEMA = None
_CTX: dict = {}


def _init(schema):
    global _SCHEMA
    _SCHEMA = schema


def _context(family: str):
    if family not in _CTX:
        from culinarystate.quantity.rc2_dryrun import LOCALE_META, SOURCE_META
        from culinarystate.quantity.rc2_grounding import GroundingContext
        from culinarystate.recipes.ledgers import LOCALE
        loc = LOCALE.get(family)
        _CTX[family] = GroundingContext(source_metadata=SOURCE_META, locale=loc, locale_metadata=LOCALE_META if loc else None)
    return _CTX[family]


def _vclass(n: dict) -> str:
    """Coarse class of the normalised amount (the value the line carries into the grounded record)."""
    st = n.get("status")
    if st == "MEASURED":
        v = n.get("value")
        if v is None:
            return "MEASURED_NO_VALUE"
        if v < 1:
            return "LT1"
        if v == 1:
            return "E1"
        return "INT_GT1" if float(v).is_integer() else "FRACTIONAL_GT1"
    return str(st)


def _outcome(res) -> dict:
    from culinarystate.quantity.rc2_dryrun import flag_code
    rc2_mass = res.record["mass_g"]["status"]
    return {"mass_route": res.mass_route, "unit_resolution": res.unit_resolution, "ast_root": res.ast_root,
            "arithmetic_status": res.arithmetic_status, "q_level": res.record["q_level"],
            "flags": tuple(dict.fromkeys(flag_code(f) for f in res.flags)),
            "issue_codes": tuple(dict.fromkeys(flag_code(i.code) for i in res.issues)),
            "legacy_vs_rc2_mass": f"legacy_{res.compatibility_mass_status}__rc2_{rc2_mass}",
            "rc2_mass_status": rc2_mass, "valid": not res.issues, "flagged": bool(res.flags),
            "norm": json.dumps(res.record["normalized"], sort_keys=True), "vclass": _vclass(res.record["normalized"]),
            "has_volume": res.record["volume_ml"]["status"] != "UNKNOWN",
            "has_count": res.record["count"]["status"] != "UNKNOWN"}


def _empty_marginals() -> dict:
    return {**{k: 0 for k in SCALARS}, **{a: Counter() for a in MARGINAL_AXES}, "exceptions": Counter()}


def _add(m: dict, o: dict, w: int) -> None:
    m["lines_total"] += w
    m["lines_grounded"] += w
    for a in ("mass_route", "unit_resolution", "ast_root", "arithmetic_status", "q_level", "legacy_vs_rc2_mass"):
        m[a][o[a]] += w
    for c in o["flags"]:
        m["flags"][c] += w
    for c in o["issue_codes"]:
        m["issue_codes"][c] += w
    m["lines_contract_valid"] += w * o["valid"]
    m["lines_flagged"] += w * o["flagged"]
    m["lines_with_rc2_mass"] += w * (o["rc2_mass_status"] != "UNKNOWN")
    m["lines_with_rc2_volume"] += w * o["has_volume"]
    m["lines_with_rc2_count"] += w * o["has_count"]


def _empty_block() -> dict:
    return {"before": _empty_marginals(), "after": _empty_marginals(),
            "affected_lines": 0, "affected_unique": 0, "value_changed_lines": 0, "before_value_exactly_one_lines": 0, "refused_lines": 0, "rule_lines": Counter(), "rule_combo_lines": Counter(),
            "changed_record_lines": 0, "identical_record_lines": 0, "transitions": Counter(), "legacy_parse_changed_lines": 0,
            "legacy_parse_kind": Counter(), "verify_unaffected": Counter()}


def process_chunk(args):
    """args = (family, [(line, weight)], verify_unaffected_budget). Returns the partial aggregate for the chunk."""
    from culinarystate.quantity import prenormalize as P
    from culinarystate.quantity.grammar import parse_line
    from culinarystate.quantity.rc2_grounding import ground_quantity_rc2
    family, items, verify = args
    ctx = _context(family)
    blk = _empty_block()
    verified = 0
    for line, w in items:
        if not isinstance(line, str) or not line.strip():
            blk["before"]["lines_total"] += w
            blk["before"]["lines_blank"] += w
            blk["after"]["lines_total"] += w
            blk["after"]["lines_blank"] += w
            continue
        try:
            before = _outcome(ground_quantity_rc2(line, ctx, schema=_SCHEMA))
        except Exception as exc:  # counted by class name only
            blk["before"]["exceptions"][type(exc).__name__] += w
            blk["after"]["exceptions"][type(exc).__name__] += w
            continue
        pn = P.prenormalise(line)
        if not pn.changed:
            after = before
            if verified < verify:
                verified += 1
                again = _outcome(P.ground_quantity_rc2_prenorm(line, ctx, schema=_SCHEMA))
                blk["verify_unaffected"]["checked_unique"] += 1
                blk["verify_unaffected"]["identical_unique"] += int(again == before)
        else:
            try:
                after = _outcome(P.ground_quantity_rc2_prenorm(line, ctx, schema=_SCHEMA))
            except Exception as exc:
                blk["after"]["exceptions"][type(exc).__name__] += w
                after = None
            blk["affected_lines"] += w
            blk["affected_unique"] += 1
            blk["refused_lines"] += w * pn.refused
            for r in pn.rules_fired:
                blk["rule_lines"][r] += w
            blk["rule_combo_lines"]["__AND__".join(pn.rules_fired) or "NONE"] += w
            lp0, lp1 = parse_line(line), P.parse_line_prenorm(line)
            key0 = (lp0.kind, lp0.value, lp0.low, lp0.high, lp0.unit_key)
            key1 = (lp1.kind, lp1.value, lp1.low, lp1.high, lp1.unit_key)
            blk["legacy_parse_changed_lines"] += w * (key0 != key1)
            blk["legacy_parse_kind"][f"{lp0.kind}__{lp1.kind}"] += w
            if after is not None:
                fl_b = tuple(c for c in before["flags"] if not c.startswith("PRENORM_"))
                fl_a = tuple(c for c in after["flags"] if not c.startswith("PRENORM_"))
                same = all(before[k] == after[k] for k in TRANSITION_FIELDS) and fl_b == fl_a \
                    and before["issue_codes"] == after["issue_codes"] and before["norm"] == after["norm"]
                blk["changed_record_lines"] += w * (not same)
                blk["identical_record_lines"] += w * same
                blk["value_changed_lines"] += w * (before["norm"] != after["norm"])
                blk["before_value_exactly_one_lines"] += w * (before["vclass"] == "E1")
                if before["vclass"] != after["vclass"]:
                    blk["transitions"][f"valueclass__{before['vclass']}__TO__{after['vclass']}"] += w
                for f in TRANSITION_FIELDS:
                    if before[f] != after[f]:
                        blk["transitions"][f"{f}__{before[f]}__TO__{after[f]}"] += w
                for c in set(fl_a) - set(fl_b):
                    blk["transitions"][f"flag_added__{c}"] += w
                for c in set(fl_b) - set(fl_a):
                    blk["transitions"][f"flag_removed__{c}"] += w
        _add(blk["before"], before, w)
        if after is not None:
            _add(blk["after"], after, w)
    return family, blk


def merge_block(into: dict, other: dict) -> None:
    for k, v in other.items():
        if isinstance(v, dict) and k in ("before", "after"):
            for kk, vv in v.items():
                if isinstance(vv, Counter):
                    into[k][kk].update(vv)
                else:
                    into[k][kk] += vv
        elif isinstance(v, Counter):
            into[k].update(v)
        else:
            into[k] += v


def stream_unique_lines(family: str, sample: int | None, seed: str):
    """(Counter unique line -> count, recipes, recipes_without_lines). Sample = smallest sha256(seed||recipe_id)."""
    from culinarystate.extraction import rung_a_measure as M
    from culinarystate.recipes import corpus
    if family == "FOODCOM":
        it = corpus.iter_foodcom()
    elif family == "WIKIBOOKS":
        it = corpus.iter_rec_corpora(families=("WIKIBOOKS",))
    elif family == "TASTESET":
        it = corpus.iter_tasteset()
    else:
        raise ValueError(family)
    if sample:
        it = M.seeded_sample(it, seed, sample)
    uniq, recipes, empty = Counter(), 0, 0
    for rec in it:
        recipes += 1
        lines = rec["ingredient_lines"] or []
        empty += not lines
        for ln in lines:
            uniq[ln] += 1
    return uniq, recipes, empty


def chunked(uniq: Counter, family: str, n: int, verify_per_chunk: int):
    items = sorted(uniq.items(), key=lambda kv: (-kv[1], kv[0]))
    for i in range(0, len(items), n):
        yield family, items[i:i + n], verify_per_chunk


def plain(o):
    if isinstance(o, Counter):
        return {k: int(v) for k, v in sorted(o.items())}
    if isinstance(o, dict):
        return {k: plain(v) for k, v in o.items()}
    return o


def compare_s161(root: Path, family: str, before: dict, recipes: int) -> dict:
    p = root / S161
    if not p.is_file():
        return {"status": "S161_FILE_MISSING"}
    ref = json.loads(p.read_text(encoding="utf-8"))["by_family"].get(family)
    if ref is None:
        return {"status": "FAMILY_NOT_IN_S161"}
    diffs = {}
    for k in SCALARS:
        if ref.get(k) != before.get(k):
            diffs[k] = {"s161": ref.get(k), "here": before.get(k)}
    for a in MARGINAL_AXES:
        r, h = ref.get(a, {}), dict(before[a])
        for kk in set(r) | set(h):
            if r.get(kk, 0) != h.get(kk, 0):
                diffs[f"{a}:{kk}"] = {"s161": r.get(kk, 0), "here": h.get(kk, 0)}
    return {"status": "IDENTICAL" if not diffs else "DIFFERS", "recipes_match": ref.get("recipes") == recipes,
            "n_differences": len(diffs), "differences": diffs}


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def run(root: Path, families, workers: int, sample: int | None, seed: str, verify: int, out_dir: Path, name: str) -> dict:
    from culinarystate.quantity import prenormalize as P
    from culinarystate.quantity.parse_adapter import ADAPTER_VERSION
    from culinarystate.quantity.rc2_dryrun import assert_counts_only, load_schema
    from culinarystate.quantity.rc2_grounding import PIPELINE_VERSION
    schema = load_schema(root)
    t0 = time.time()
    res = {"record": "SP002_PRENORM_RERUN_S178", "tool_version": TOOL_VERSION, "item": "T3-C07-R1",
           "status": "AI_ENGINEERING_COUNTS_ONLY_DRAFT", "contains_recipe_text": False, "contains_recipe_ids": False,
           "counts_as_human_gate": False, "prenorm_version": P.PRENORM_VERSION, "rules": list(P.DEFAULT_RULES),
           "pipeline_version_before": PIPELINE_VERSION, "adapter_version_before": ADAPTER_VERSION,
           "sample_recipes_per_family": sample, "sample_seed_sha256": hashlib.sha256(seed.encode()).hexdigest() if sample else None,
           "locale_source": "LEGACY_SOURCE_FAMILY_LOCALE_MAP", "por_records_supplied": 0, "ingredient_links_supplied": False,
           "workers": workers, "families": {}}
    ctx = get_context("spawn")
    for fam in families:
        t1 = time.time()
        uniq, recipes, empty = stream_unique_lines(fam, sample, seed)
        total_lines = sum(uniq.values())
        blk = _empty_block()
        chunks = list(chunked(uniq, fam, 2000, max(0, verify // max(1, len(uniq) // 2000 + 1))))
        with ctx.Pool(workers, initializer=_init, initargs=(schema,)) as pool:
            for _f, part in pool.imap_unordered(process_chunk, chunks):
                merge_block(blk, part)
        for side in ("before", "after"):
            blk[side]["recipes"] = recipes
        b, a = blk["before"], blk["after"]
        out = {"status": "READ", "recipes": recipes, "recipes_without_ingredient_lines": empty, "lines_total": total_lines,
               "unique_lines": len(uniq), "lines_affected_by_any_rule": blk["affected_lines"],
               "pct_lines_affected": pct(blk["affected_lines"], total_lines), "unique_lines_affected": blk["affected_unique"],
               "lines_refused_glued": blk["refused_lines"], "lines_by_rule": plain(blk["rule_lines"]),
               "lines_by_rule_combination": plain(blk["rule_combo_lines"]),
               "affected_lines_whose_rc2_record_changes": blk["changed_record_lines"],
               "affected_lines_whose_normalised_amount_changes": blk["value_changed_lines"],
               "pct_lines_whose_normalised_amount_changes": pct(blk["value_changed_lines"], total_lines),
               "affected_lines_whose_before_amount_was_exactly_one": blk["before_value_exactly_one_lines"],
               "affected_lines_with_identical_rc2_record": blk["identical_record_lines"],
               "pct_lines_changing_rc2_record": pct(blk["changed_record_lines"], total_lines),
               "affected_lines_whose_legacy_parse_changes": blk["legacy_parse_changed_lines"],
               "legacy_parse_kind_transition_lines": plain(blk["legacy_parse_kind"]),
               "transitions_lines": plain(blk["transitions"]),
               "unaffected_lines_verified_identical": plain(blk["verify_unaffected"]),
               "before": plain(b), "after": plain(a),
               "delta_lines_with_rc2_mass": a["lines_with_rc2_mass"] - b["lines_with_rc2_mass"],
               "delta_lines_with_rc2_volume": a["lines_with_rc2_volume"] - b["lines_with_rc2_volume"],
               "delta_lines_flagged": a["lines_flagged"] - b["lines_flagged"],
               "delta_lines_contract_valid": a["lines_contract_valid"] - b["lines_contract_valid"]}
        if not sample:
            out["before_vs_s161"] = compare_s161(root, fam, plain(b), recipes)
        out["seconds"] = round(time.time() - t1, 1)
        res["families"][fam] = out
    res["families"]["GUTENBERG_SEGMENT"] = {"status": "NOT_AVAILABLE", "reason": "NO_INGREDIENT_LINES_S177_F6"}
    res["families"]["A1_BBC_GOOD_FOOD"] = {"status": "NOT_ON_THIS_SERVER", "reason": "D_003_BBC_DATA_NOT_PRESENT"}
    res["seconds_total"] = round(time.time() - t0, 1)
    assert_counts_only(res)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{name}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / f"{name}.md").write_text(md(res), encoding="utf-8")
    return res


def md(res: dict) -> str:
    L = ["# SP-002 pre-normalisation: rc2 grounding before / after (S178, T3-C07-R1)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts only (no line, no id, no unit token). Engineering coverage, not a quality estimate, not a gold score.",
         f"Tool `{res['tool_version']}`; pre-normaliser `{res['prenorm_version']}` rules {', '.join(res['rules'])}; BEFORE = frozen `{res['pipeline_version_before']}` "
         f"/ `{res['adapter_version_before']}`. Locale from the legacy family map (Food.com US; others ambiguous). No POR records, no ingredient links.",
         f"Sample: {res['sample_recipes_per_family'] or 'full families'}.", "",
         "## Lines changed per family", "",
         "| family | recipes | lines | lines touched by a rule | % | rc2 record changes (markers aside) | amount changes | legacy parse changes | refused (glued) | rule counts |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for f, b in res["families"].items():
        if b.get("status") != "READ":
            L.append(f"| {f} | {b['status']} | | | | | | | | {b.get('reason', '')} |")
            continue
        L.append(f"| {f} | {b['recipes']:,} | {b['lines_total']:,} | {b['lines_affected_by_any_rule']:,} | {b['pct_lines_affected']} | "
                 f"{b['affected_lines_whose_rc2_record_changes']:,} ({b['pct_lines_changing_rc2_record']} %) | "
                 f"{b['affected_lines_whose_normalised_amount_changes']:,} ({b['pct_lines_whose_normalised_amount_changes']} %) | "
                 f"{b['affected_lines_whose_legacy_parse_changes']:,} | {b['lines_refused_glued']:,} | {b['lines_by_rule']} |")
    for f, b in res["families"].items():
        if b.get("status") != "READ":
            continue
        bb, aa = b["before"], b["after"]
        L += ["", f"## {f}: before and after", "",
              "| measure | before | after | delta |", "|---|---:|---:|---:|"]
        for k in ("lines_total", "lines_grounded", "lines_with_rc2_mass", "lines_with_rc2_volume", "lines_with_rc2_count",
                  "lines_flagged", "lines_contract_valid"):
            L.append(f"| {k} | {bb[k]:,} | {aa[k]:,} | {aa[k] - bb[k]:+,} |")
        for axis in ("mass_route", "unit_resolution", "ast_root", "arithmetic_status", "q_level"):
            keys = sorted(set(bb[axis]) | set(aa[axis]))
            for k in keys:
                x, y = bb[axis].get(k, 0), aa[axis].get(k, 0)
                if x != y:
                    L.append(f"| {axis} = {k} | {x:,} | {y:,} | {y - x:+,} |")
        for k in sorted(set(bb["flags"]) | set(aa["flags"])):
            x, y = bb["flags"].get(k, 0), aa["flags"].get(k, 0)
            if x != y:
                L.append(f"| flag {k} | {x:,} | {y:,} | {y - x:+,} |")
        if bb["exceptions"] or aa["exceptions"]:
            L.append(f"| exceptions | {sum(bb['exceptions'].values())} | {sum(aa['exceptions'].values())} | |")
        v = b.get("unaffected_lines_verified_identical") or {}
        unaffected = (b.get("unique_lines") or 0) - (b.get("unique_lines_affected") or 0)
        # S178 FIX-EVAL (SCI-B CORP-6): a capped subset, not an exhaustive check; the denominator is stated
        chk, same = v.get("checked_unique", 0), v.get("identical_unique", 0)
        scope = (f"all {chk:,} unaffected unique lines (exhaustive)" if chk == unaffected else
                 f"{chk:,} sampled (capped: the first lines of each worker chunk, not a random sample) of {unaffected:,} unaffected unique lines")
        L += ["", f"Unaffected unique lines re-checked through the opt-in path: {scope}; {same:,} of the {chk:,} identical."]
        s = b.get("before_vs_s161")
        if s:
            L.append(f"BEFORE vs committed S161 counts: **{s['status']}** ({s.get('n_differences', 0)} differences).")
        L += ["", "Transitions among affected lines (lines):", ""]
        for k, v in sorted(b["transitions_lines"].items(), key=lambda kv: -kv[1])[:25]:
            L.append(f"- `{k}`: {v:,}")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sample", type=int, default=None, help="recipes per family, smallest sha256(seed||recipe_id)")
    ap.add_argument("--seed", default="20261104")
    ap.add_argument("--verify-unaffected", type=int, default=2000, help="unique unaffected lines re-checked via the opt-in path")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--name", default=None)
    a = ap.parse_args(argv)
    if a.workers > 24:
        ap.error("at most 24 workers (shared server)")
    root = Path(a.root)
    out_dir = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    name = a.name or ("sp002_prenorm_rerun_v1" if not a.sample else f"sp002_prenorm_rerun_sample{a.sample}")
    res = run(root, [f for f in a.families.split(",") if f], a.workers, a.sample, a.seed, a.verify_unaffected, out_dir, name)
    print(json.dumps({f: {k: b.get(k) for k in ("lines_total", "lines_affected_by_any_rule", "affected_lines_whose_rc2_record_changes",
                                                "lines_refused_glued", "seconds")} for f, b in res["families"].items()
                      if b.get("status") == "READ"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
