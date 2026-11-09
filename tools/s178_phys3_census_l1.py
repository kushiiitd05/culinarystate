#!/usr/bin/env python
"""Step 26g simulability census WITH Layer 1 bindings (S178 PHYS3, T4-C21-R1). DRAFT, AI_DRAFTED, counts only.

The S166 census (``tools/step26g_census.py`` + ``simulation/census_chain.py``) passes no bindings, so every event is MISSING every
input by construction. ``build_simulation_inputs`` already takes caller ``ConditionBinding``s; the census tool has no hook for them.
This tool adds one WITHOUT editing the S166 files (their output stays byte-identical): it runs the same chain per sampled recipe
(Rung A -> event adapter -> replay, same seeded sample and corpus reader) and builds the contract records twice:

- ``baseline_no_bindings``: no bindings (= the S166 census of the same sample; tested equal, census_sha256 identical);
- ``with_layer1_bindings``: the Layer 1 (TEXT_STATED) records of the sampled recipes, read from ``--layer1-records`` directories
  (``data/derived/physical_L1_*``; joined on recipe id and event id), turned into contract bindings by the Layer 1 binder's own
  rule (``condition_binding.Binder._bindings``: duration, medium, lid, start mode, size class, matrix class; a temperature profile
  only with a point duration). Source class STRUCTURAL_RECIPE. No applicability record is supplied (23a has none).

SIMULATE gate (asserted): no PARAM row is human-verified (``ledgers/data/PARAM.jsonl`` is read if present) and no 23a applicability
record is supplied, so SIMULATE must be 0 in both arms; if it is not, the tool writes nothing and exits 5. Paired per-event counts
show which MISSING_* reasons the Layer 1 bindings remove. The report holds integer counts and codes only (no id, value or text).

    nice -n 10 python tools/s178_phys3_census_l1.py --seed 20261104 --sample-size 1000 \
        --layer1-records data/derived/physical_L1_1000_S178v04 --workers 8 --out reports/step26/<new>_S178_26g.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.extraction.interfaces import SourceText  # noqa: E402
from culinarystate.extraction.rung_a import RungA  # noqa: E402
from culinarystate.extraction.rung_a_measure import code, seeded_sample  # noqa: E402
from culinarystate.lineage.guard import LedgerBaselineMismatch  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.recipes.ledgers import LOCALE  # noqa: E402
from culinarystate.simulation import census_chain as C  # noqa: E402
from culinarystate.simulation import condition_binding as CB  # noqa: E402
from culinarystate.simulation import recipe_adapter as RA  # noqa: E402
from culinarystate.state_graph.event_adapter import adapt_event_graph  # noqa: E402

_spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)

TOOL_VERSION = "s178-phys3-26g-l1-census-0.1.0-draft"
CODE_FILES = ("src/culinarystate/simulation/census_chain.py", "src/culinarystate/simulation/recipe_adapter.py",
              "src/culinarystate/simulation/condition_binding.py", "tools/step26g_census.py", "tools/s178_phys3_census_l1.py")
NUMERIC_AXES = frozenset({"duration", "temperature_profile", "water_ratio", "medium_ph", "ambient_temperature"})
NEVER_BOUND_BY_L1 = frozenset({"MISSING_WATER_RATIO", "MISSING_MEDIUM_PH"})  # L1 v0 binds neither (NOT_BOUND_V0)
FLUSH_EVERY = 256
_RID = re.compile(r'^\{"recipe_id":\s*"((?:[^"\\]|\\.)*)"')
_CTX: dict = {}


# ------------------------------------------------------------------------------------------------ Layer 1 records
def l1_files(dirs: Iterable[str | Path]) -> list[Path]:
    out: list[Path] = []
    for d in dirs:
        p = Path(d)
        if not p.is_dir():
            raise FileNotFoundError(f"Layer 1 records directory not found: {p}")
        out += sorted(p.rglob("*.jsonl"))
    return out


def l1_index(files: list[Path], wanted: set[str]) -> tuple[dict[str, list[tuple[int, int, int]]], Counter]:
    """recipe id -> [(file index, start offset, end offset)] of its contiguous record lines, for wanted recipes only."""
    idx: dict[str, list[tuple[int, int, int]]] = {}
    c = Counter()
    for fi, path in enumerate(files):
        with open(path, "rb") as fh:
            pos = 0
            for raw in fh:
                start, pos = pos, pos + len(raw)
                if not raw.strip():
                    continue
                c["lines"] += 1
                m = _RID.match(raw.decode("utf-8"))
                rid = json.loads(m.group(0) + "}")["recipe_id"] if m else json.loads(raw)["recipe_id"]
                if rid not in wanted:
                    continue
                c["lines_for_sampled_recipes"] += 1
                runs = idx.setdefault(rid, [])
                if runs and runs[-1][0] == fi and runs[-1][2] == start:
                    runs[-1] = (fi, runs[-1][1], pos)
                else:
                    runs.append((fi, start, pos))
    c["sampled_recipes_with_records"] = len(idx)
    return idx, c


def read_l1(rid: str) -> list[dict]:
    files, idx, handles = _CTX["l1_files"], _CTX["l1_index"], _CTX.setdefault("handles", {})
    out = []
    for fi, a, b in idx.get(rid, ()):
        fh = handles.get(fi)
        if fh is None:
            fh = handles[fi] = open(files[fi], "rb")
        fh.seek(a)
        out += [json.loads(line) for line in fh.read(b - a).splitlines() if line.strip()]
    return out


def _num(v):
    if v is None or isinstance(v, (int, float)) and not isinstance(v, bool):
        return None if v is None else Fraction(str(v))
    if isinstance(v, str):
        return Fraction(v)
    if isinstance(v, list):
        return tuple(Fraction(str(x)) for x in v)
    raise ValueError("unexpected numeric value shape")


def decode_inputs(inputs: Mapping[str, Mapping]) -> dict[str, dict]:
    """A Layer 1 record's inputs with numeric values back as exact Fractions (records hold them as strings)."""
    out = {}
    for name, x in inputs.items():
        x = dict(x)
        if name in NUMERIC_AXES and x.get("value") is not None:
            x["value"] = _num(x["value"])
        out[name] = x
    return out


def bindings_from_records(recs: Iterable[Mapping]) -> list[RA.ConditionBinding]:
    """Contract bindings of Layer 1 records, by the binder's own rule (``Binder._bindings``)."""
    out: list[RA.ConditionBinding] = []
    for r in recs:
        out += CB.Binder._bindings(r["event_id"], decode_inputs(r["inputs"]))
    return out


def human_verified_param_rows(root: Path) -> tuple[str, int]:
    """(PRESENT / ABSENT, rows human-verified by Kush or Parv with a date) of ledgers/data/PARAM.jsonl (read only)."""
    p = Path(root) / "ledgers" / "data" / "PARAM.jsonl"
    if not p.exists():
        return "ABSENT", 0
    n = 0
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                v = (json.loads(line).get("verification") or {})
                n += int(v.get("status") == "HUMAN_VERIFIED" and v.get("verifier") in ("Kush", "Parv") and bool(v.get("verified_at")))
    return "PRESENT", n


# ------------------------------------------------------------------------------------------------ per-recipe chain
def _pair_counts(base: RA.SimulationInputSet, bound: RA.SimulationInputSet, recs: Mapping[str, Mapping], pc: Counter) -> None:
    sysid = base.system_id
    for b, w in zip(base.records, bound.records, strict=True):
        assert b.event_id == w.event_id
        rec = recs.get(b.event_id)
        fam = code(rec["family"]) if rec is not None else "NO_L1_RECORD"
        pc[(sysid, "events")] += 1
        pc[(sysid, "reasons_per_event_before", str(len(b.reasons)))] += 1
        pc[(sysid, "reasons_per_event_after", str(len(w.reasons)))] += 1
        for r in w.reasons:
            pc[(sysid, "reasons_by_event_family_after", fam, r)] += 1
        before, after = set(b.reasons), set(w.reasons)
        dropped = {r for r in before - after if r.startswith("MISSING_")}
        for r in before:
            if r.startswith("MISSING_"):
                pc[(sysid, "missing", r, "before")] += 1
        for r in after:
            if r.startswith(("MISSING_", "CONFLICTING_", "SOURCE_NOT_PERMITTED_")):
                pc[(sysid, "missing", r, "after")] += 1
        for r in dropped:
            pc[(sysid, "missing", r, "dropped")] += 1
        if dropped:
            pc[(sysid, "events_with_a_missing_reason_dropped")] += 1
        if rec is None:
            continue
        pc[(sysid, "events_with_l1_record")] += 1
        pc[(sysid, "l1_events_reason_sets_after", "|".join(sorted(after)))] += 1
        if not ({r for r in after if r.startswith(("MISSING_", "CONFLICTING_", "SOURCE_NOT_PERMITTED_"))} - NEVER_BOUND_BY_L1):
            pc[(sysid, "l1_events_only_never_l1_bound_inputs_missing")] += 1
        for i in w.inputs:
            x = rec["inputs"].get(i.name) or {}
            if x.get("status", "UNKNOWN") != "UNKNOWN" and i.status == "UNKNOWN":
                pc[(sysid, "l1_bound_but_contract_unknown", i.name, i.reason or "NONE")] += 1
            if x:
                pc[(sysid, "l1_status_to_contract_status", i.name, f"{x.get('status', 'UNKNOWN')}_TO_{i.status}")] += 1


def _chunk(args: tuple[int, list[Mapping]]) -> dict:
    _, recs = args
    rung, schema, systems = _CTX["rung"], _CTX["schema"], _CTX["systems"]
    tot, issues, exc, l1c, pc = Counter(), Counter(), Counter(), Counter(), Counter()
    base_sets: list = []
    bound_sets: list = []
    acc: dict = {}

    def flush() -> None:  # bounded memory: fold the contract records into the census every FLUSH_EVERY recipes
        for arm, sets in (("base", base_sets), ("bound", bound_sets)):
            c = RA.simulability_census(sets)
            acc[arm] = c if arm not in acc else merge_census(acc[arm], c)
            sets.clear()

    try:
        for n_done, rec in enumerate(recs, 1):
            if n_done % FLUSH_EVERY == 0:
                flush()
            steps = C._steps(rec)
            if not steps:
                continue
            tot["texts_with_steps"] += 1
            try:
                source = SourceText.from_raw("COUNTS", "\n".join(steps))
                res = rung.run(source, rung.config(locale=LOCALE.get(rec.get("source_family"))), schema=schema)
                adapted = adapt_event_graph(source, res.graph, groundings=res.quantities, recomputers=rung.recomputers())
                replay = adapted.replay()
                base = {s: RA.build_simulation_inputs(replay, recipe_id=rec["recipe_id"], system_id=s) for s in systems}
            except Exception as e:  # noqa: BLE001 - counted by class name; the message may contain text
                exc[code(type(e).__name__)] += 1
                continue
            tot["engine_events"] += len(adapted.events)
            tot["adapter_invented_excluded"] += adapted.invented_count
            issues.update(code(i.code) for i in adapted.issues)
            l1 = read_l1(rec["recipe_id"]) if _CTX["l1_index"] else []
            l1c["records_for_sampled_recipes"] += len(l1)
            by_ev: dict[str, Mapping] = {}
            for r in l1:
                l1c[("version", code(r.get("version")))] += 1
                if r["event_id"] in by_ev:
                    l1c["duplicate_event_rows"] += 1
                by_ev[r["event_id"]] = r
            replay_ids = {t.event_id for t in replay.transactions}
            l1c["records_event_in_replay"] += sum(1 for e in by_ev if e in replay_ids)
            l1c["records_event_not_in_replay"] += sum(1 for e in by_ev if e not in replay_ids)
            if not l1:
                l1c["recipes_with_steps_without_records"] += 1
            bnd: list[RA.ConditionBinding] = []
            for r in by_ev.values():
                for name, x in r["inputs"].items():
                    l1c[("input_status", name, x.get("status", "UNKNOWN"))] += 1
                try:
                    bnd += bindings_from_records([r])
                except Exception as e:  # noqa: BLE001
                    l1c[("decode_exception", code(type(e).__name__))] += 1
            for x in bnd:
                l1c[("contract_bindings_by_input", x.input_name)] += 1
            l1c["bindings_supplied"] += len(bnd)
            for s in systems:
                bound = RA.build_simulation_inputs(replay, recipe_id=rec["recipe_id"], system_id=s, bindings=bnd)
                base_sets.append(base[s])
                bound_sets.append(bound)
                _pair_counts(base[s], bound, by_ev, pc)
        flush()
    finally:
        for fh in _CTX.get("handles", {}).values():
            fh.close()
        _CTX["handles"] = {}
    return {"tot": tot, "issues": issues, "exc": exc, "l1": l1c, "pc": pc, "base": acc["base"], "bound": acc["bound"]}


# ------------------------------------------------------------------------------------------------ merging
def merge_census(a: Mapping, b: Mapping) -> dict:
    """Sum of two census dicts (ints add, equal constants stay, nested dicts merge); raises on a constant mismatch."""
    out = dict(a)
    for k, v in b.items():
        if k not in out:
            out[k] = v
        elif isinstance(v, Mapping):
            out[k] = merge_census(out[k], v)
        elif isinstance(v, bool) or not isinstance(v, int):
            if out[k] != v:
                raise ValueError(f"census constant {k!r} differs between chunks")
        else:
            out[k] = out[k] + v
    return out


def _nest(c: Counter, *prefix) -> dict:
    out: dict = {}
    n = len(prefix)
    for key, v in sorted(c.items(), key=lambda kv: tuple(map(str, kv[0])) if isinstance(kv[0], tuple) else (kv[0],)):
        if not isinstance(key, tuple) or key[:n] != prefix or len(key) == n:
            continue
        d = out
        for part in key[n:-1]:
            d = d.setdefault(str(part), {})
        d[str(key[-1])] = d.get(str(key[-1]), 0) + v
    return out


def _reason_sets(pc: Counter, s: str) -> list[dict]:
    """[{reasons: [codes], events: n}] of the Layer 1 events after binding, most frequent first."""
    rows = [{"reasons": k[2].split("|") if k[2] else [], "events": v} for k, v in pc.items()
            if isinstance(k, tuple) and len(k) == 3 and k[:2] == (s, "l1_events_reason_sets_after")]
    return sorted(rows, key=lambda d: (-d["events"], d["reasons"]))


def census_from_records(records: Iterable[Mapping], *, seed: str, size: int, systems: tuple[str, ...] = ("sim_aa_1",),
                        layer1_dirs: Iterable[str | Path] = (), workers: int = 1, rung: RungA | None = None,
                        schema: Mapping | None = None) -> dict:
    for s in systems:
        if s not in RA.SYSTEM_REQUIREMENTS:
            raise ValueError(f"system_id must be one of {tuple(RA.SYSTEM_REQUIREMENTS)}")
    if workers < 1:
        raise ValueError("workers must be positive")
    seen = 0

    def counted(it: Iterable[Mapping]) -> Iterator[Mapping]:
        nonlocal seen
        for rec in it:
            seen += 1
            yield rec

    sample = seeded_sample(counted(records), seed, size)
    ids = [r["recipe_id"] for r in sample]
    if len(set(ids)) != len(ids):  # the S166 census refuses the same (recipe, system) twice; chunks cannot see each other
        raise RA.SimInputError("the same recipe and system are counted twice")
    layer1_dirs = list(layer1_dirs)
    files = l1_files(layer1_dirs)
    idx, idx_c = l1_index(files, {r["recipe_id"] for r in sample}) if files else ({}, Counter())
    _CTX.clear()
    _CTX.update(rung=rung or RungA(), schema=schema or D.load_schema(ROOT), systems=tuple(systems), l1_files=files, l1_index=idx,
                handles={})
    n = workers * 8 if workers > 1 else 1
    chunks = [(i, sample[i::n]) for i in range(n)]
    try:
        if workers == 1:
            parts = [_chunk(c) for c in chunks]
        else:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(workers) as pool:
                parts = pool.map(_chunk, chunks, chunksize=1)
    finally:
        _CTX.clear()
    acc = {k: Counter() for k in ("tot", "issues", "exc", "l1", "pc")}
    base, bound = parts[0]["base"], parts[0]["bound"]
    for i, p in enumerate(parts):
        for k in acc:
            acc[k].update(p[k])
        if i:
            base, bound = merge_census(base, p["base"]), merge_census(bound, p["bound"])
    tot, l1, pc = acc["tot"], acc["l1"], acc["pc"]
    sims = {s: {"baseline": base["systems"].get(s, {}).get("route", {}).get("SIMULATE", 0),
                "with_layer1": bound["systems"].get(s, {}).get("route", {}).get("SIMULATE", 0)} for s in systems}
    paired = {}
    for s in systems:
        miss = _nest(pc, s, "missing")
        paired[s] = {
            "events": pc[(s, "events")], "events_with_l1_record": pc[(s, "events_with_l1_record")],
            "events_with_a_missing_reason_dropped": pc[(s, "events_with_a_missing_reason_dropped")],
            "input_reasons_before_after_dropped": {r: {k: v.get(k, 0) for k in ("before", "after", "dropped")} for r, v in miss.items()},
            "reasons_per_event_before": _nest(pc, s, "reasons_per_event_before"),
            "reasons_per_event_after": _nest(pc, s, "reasons_per_event_after"),
            "reasons_by_event_family_after": _nest(pc, s, "reasons_by_event_family_after"),
            "l1_events_reason_sets_after": _reason_sets(pc, s),
            "l1_events_only_inputs_never_bound_by_l1_missing": pc[(s, "l1_events_only_never_l1_bound_inputs_missing")],
            "l1_bound_but_contract_unknown": _nest(pc, s, "l1_bound_but_contract_unknown"),
            "l1_status_to_contract_status": _nest(pc, s, "l1_status_to_contract_status")}
    report = {
        "record": "STEP26G_CENSUS_WITH_LAYER1_BINDINGS", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
        "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD", "tool_version": TOOL_VERSION,
        "chain": "RUNG_A|EVENT_ADAPTER|REPLAY|LAYER1_RECORDS|STEP26G", "chain_version": C.CHAIN_VERSION,
        "census_version": RA.CENSUS_VERSION, "contract_version": RA.CONTRACT_VERSION, "systems": list(systems),
        "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
        "seed_sha256": hashlib.sha256(seed.encode("utf-8")).hexdigest(), "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC",
        "sample_size_requested": int(size), "recipes_seen": seen, "recipes_sampled": len(sample),
        "texts_with_steps": tot["texts_with_steps"], "engine_events": tot["engine_events"],
        "adapter_invented_excluded": tot["adapter_invented_excluded"], "adapter_issue_codes": dict(sorted(acc["issues"].items())),
        "exceptions_by_class": dict(sorted(acc["exc"].items())),
        "layer1": {"source_class": "STRUCTURAL_RECIPE", "binding_rule": "CONDITION_BINDING_BINDER_BINDINGS",
                   "records_dirs": len(layer1_dirs),
                   "files": len(files), "lines_indexed": idx_c["lines"],
                   "lines_for_sampled_recipes": idx_c["lines_for_sampled_recipes"],
                   "sampled_recipes_with_records": idx_c["sampled_recipes_with_records"],
                   "records_for_sampled_recipes": l1["records_for_sampled_recipes"],
                   "record_versions": _nest(l1, "version"), "duplicate_event_rows": l1["duplicate_event_rows"],
                   "records_event_in_replay": l1["records_event_in_replay"],
                   "records_event_not_in_replay": l1["records_event_not_in_replay"],
                   "recipes_with_steps_without_records": l1["recipes_with_steps_without_records"],
                   "record_input_status": _nest(l1, "input_status"), "decode_exceptions_by_class": _nest(l1, "decode_exception"),
                   "bindings_supplied": l1["bindings_supplied"],
                   "contract_bindings_by_input": _nest(l1, "contract_bindings_by_input")},
        "applicability_supplied": 0,
        "baseline_no_bindings": {"reading": "S166_CENSUS_OF_THE_SAME_SAMPLE_NO_BINDINGS_ALL_EVENTS_SIM_PROHIBITED_BY_CONSTRUCTION",
                                 "census": base, "census_sha256": RA.census_sha256(base)},
        "with_layer1_bindings": {"reading": "LAYER1_TEXT_STATED_BINDINGS_NO_APPLICABILITY_RECORD_SO_STILL_SIM_PROHIBITED",
                                 "census": bound, "census_sha256": RA.census_sha256(bound)},
        "paired_by_event": paired, "simulate_by_system": sims,
    }
    D.assert_counts_only(report)
    return report


# ------------------------------------------------------------------------------------------------ CLI
def provenance() -> dict:
    p = T17.code_provenance()
    return {**p, "code_sha256": p["code_sha256"] + [{"path": f, "sha256": hashlib.sha256((ROOT / f).read_bytes()).hexdigest()}
                                                       for f in CODE_FILES]}


def _ok(root: Path) -> bool:
    try:
        T17._baseline(root)
        return True
    except (LedgerBaselineMismatch, OSError, KeyError, ValueError):
        return False


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True, help="sampling seed (only its SHA-256 is reported)")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--systems", nargs="+", default=["sim_aa_1"], choices=sorted(RA.SYSTEM_REQUIREMENTS))
    ap.add_argument("--layer1-records", nargs="+", required=True, help="Layer 1 record directories (recursive *.jsonl)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", required=True, help="new counts-only JSON (refuses overwrite and protected places)")
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    ap.add_argument("--no-baseline-check", action="store_true", help="skip the protected-ledger hash check (tests only)")
    a = ap.parse_args(argv)
    if a.sample_size < 1:
        ap.error("--sample-size must be positive")
    if not 1 <= a.workers <= 24:
        ap.error("--workers must be between 1 and 24 (shared server)")
    root, out = Path(a.root), Path(a.out)
    if out.exists():
        ap.error("refusing to overwrite an existing report")
    for d in a.layer1_records:
        if not Path(d).is_dir():
            ap.error(f"--layer1-records directory not found: {d}")
    param_ledger, param_hv = human_verified_param_rows(root)
    prov = provenance()
    if a.no_baseline_check:
        baseline = "SKIPPED_BY_FLAG"
    elif not _ok(root):
        print(json.dumps({"status": "REFUSED", "reason": "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN"}))
        return 2
    else:
        baseline = "PENDING_AFTER_RUN"
    status: dict = {}
    rep = census_from_records(T17._stream(a.families, root, record_source or T17.corpus_records, status), seed=a.seed,
                              size=a.sample_size, systems=tuple(a.systems), layer1_dirs=a.layer1_records, workers=a.workers,
                              schema=D.load_schema(ROOT))
    if baseline == "PENDING_AFTER_RUN":
        baseline = "PASS_BEFORE_AND_AFTER" if _ok(root) else "FAILED_AFTER_RUN"
    sim_total = sum(v["baseline"] + v["with_layer1"] for v in rep["simulate_by_system"].values())
    gate = {"assertion": "SIMULATE_EQ_0_BOTH_ARMS", "param_ledger": param_ledger, "param_rows_human_verified": param_hv,
            "applicability_records_supplied": 0, "simulate_total": sim_total,
            "result": "PASS" if sim_total == 0 else "FAIL"}
    rep.update(simulate_gate=gate, family_status=dict(sorted(status.items())), baseline_check=baseline,
               families_requested=list(a.families), code_provenance=prov, code_unchanged_during_run=provenance() == prov)
    if sim_total != 0:
        print(json.dumps({"status": "REFUSED", "reason": "SIMULATE_ROUTE_WITHOUT_HUMAN_VERIFIED_PARAM", "simulate_total": sim_total}))
        return 5
    try:
        D.write_report(out, rep, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    s0 = a.systems[0]
    print(json.dumps({"output": str(out), "recipes_sampled": rep["recipes_sampled"], "engine_events": rep["engine_events"],
                      "bindings_supplied": rep["layer1"]["bindings_supplied"],
                      "events_with_a_missing_reason_dropped": rep["paired_by_event"][s0]["events_with_a_missing_reason_dropped"],
                      "simulate_gate": gate["result"], "baseline_check": baseline,
                      "baseline_census_sha256": rep["baseline_no_bindings"]["census_sha256"],
                      "exceptions": sum(rep["exceptions_by_class"].values()), "family_status": rep["family_status"]}))
    if baseline == "FAILED_AFTER_RUN":
        return 4
    return 3 if any(v != "READ" for v in status.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
