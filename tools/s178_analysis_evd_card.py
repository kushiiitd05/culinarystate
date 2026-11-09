#!/usr/bin/env python3
"""S178 ANALYSIS lane, T2-C15-R1: counts-only dataset card for the ACTIVE E3 EVD rows (SSOT section 203.9).

Reads ledgers/data/{EVD,COND,SRC,MEAS,SVAR,PROC,ING,STUDY}.jsonl READ-ONLY (latest version per id, ACTIVE EVD only),
registry/state_variable_registry_v1.csv, registry/svar_duplicate_mapping_v1.csv and the committed 15a.R seal
commitment (counts only). Writes reports/s178/analysis/evd_dataset_card_v1.{json,md}. No timestamp, host or run id
enters the card, so two runs on the same inputs are byte-identical (`--selfcheck` runs it twice and compares).

Every SSOT 203.9 item has a key under `s203_9`. The card is DRAFT: nothing here freezes 15a, signs anything or
verifies a row. Every row is tagged E3_UNVERIFIED (tier E3, no HUMAN_VERIFIED status), BOOTSTRAP_UNVERIFIED (C2-a: E3
may train and form a bootstrap benchmark, never Gold, never headline) and COND_UNAUDITED (condition fields are carried as
imported; the 07.A condition audit did not pass).

Third-party text: the card holds counts and registry names only. Free-text food names from the source tables never enter it
(foods are reported through ING canonical names, source food-group labels of USDA / Phenol-Explorer only).

  python tools/s178_analysis_evd_card.py [--out-dir reports/s178/analysis] [--selfcheck]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-evd-card-0.1.0-draft"
LEDGERS = ("EVD", "COND", "SRC", "MEAS", "SVAR", "PROC", "ING", "STUDY")
SEAL = "reports/step15/15a_R_seal_commitment_v1.json"
SVAR_REG = "registry/state_variable_registry_v1.csv"
SVAR_MAP = "registry/svar_duplicate_mapping_v1.csv"
AXES = ("temperature", "duration", "ph", "moisture", "pressure")
STATED = ("MEASURED", "RANGE")
T_BINS = [(-1e9, 0, "<= 0 C"), (0, 60, "0-60 C"), (60, 100, "60-100 C"), (100, 140, "100-140 C"), (140, 180, "140-180 C"),
          (180, 250, "180-250 C"), (250, 1e9, "> 250 C")]
D_BINS = [(0, 1, "< 1 min"), (1, 5, "1-5 min"), (5, 15, "5-15 min"), (15, 30, "15-30 min"), (30, 60, "30-60 min"),
          (60, 180, "1-3 h"), (180, 1e9, "> 3 h")]
PAIR_BINS = [(1, 1, "1"), (2, 2, "2"), (3, 5, "3-5"), (6, 10, "6-10"), (11, 20, "11-20"), (21, 50, "21-50"), (51, 10 ** 9, "> 50")]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_latest(path: Path) -> tuple[dict[str, dict], int]:
    latest: dict[str, dict] = {}
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                n += 1
                r = json.loads(line)
                if r["id"] not in latest or r["version"] >= latest[r["id"]]["version"]:
                    latest[r["id"]] = r
    return latest, n


def pct(a: int, b: int) -> float | None:
    return round(100.0 * a / b, 2) if b else None


def bins(values, spec) -> dict:
    out = {lab: 0 for _, _, lab in spec}
    for v in values:
        for lo, hi, lab in spec:
            if (lo <= v < hi) or (lo == hi and v == lo):
                out[lab] += 1
                break
    return out


def quant(values: list[float]) -> dict:
    if not values:
        return {"n": 0}
    s = sorted(values)
    q = lambda p: s[min(len(s) - 1, int(p * (len(s) - 1) + 0.5))]  # noqa: E731
    return {"n": len(s), "min": s[0], "p05": q(0.05), "p25": q(0.25), "median": q(0.5), "p75": q(0.75), "p95": q(0.95), "max": s[-1]}


def counter_dict(c: Counter, top: int | None = None) -> dict:
    items = sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0])))
    return {str(k): v for k, v in (items[:top] if top else items)}


def build(root: Path) -> dict:
    from culinarystate.eda.report import cell_key
    data = {n: read_latest(root / "ledgers/data" / f"{n}.jsonl") for n in LEDGERS}
    evd_all, evd_lines = data["EVD"]
    evd = {k: v for k, v in evd_all.items() if v["status"] == "ACTIVE"}
    cond, src, meas, svar, proc, ing, study = (data[n][0] for n in ("COND", "SRC", "MEAS", "SVAR", "PROC", "ING", "STUDY"))
    rows = sorted(evd.values(), key=lambda e: e["id"])
    N = len(rows)
    fam_rows: dict[str, list[dict]] = defaultdict(list)
    for e in rows:
        fam_rows[e["source_family_id"]].append(e)
    fams = sorted(fam_rows)

    card: dict = {"record": "EVD_DATASET_CARD_S178", "tool_version": TOOL_VERSION, "status": "DRAFT_NOT_FROZEN_NOT_SIGNED",
                  "contains_text": False, "contains_ids": False, "counts_as_human_gate": False,
                  "scope": "ACTIVE EVD rows (latest version per id), tier E3, three source families"}
    card["inputs"] = {f"ledgers/data/{n}.jsonl": sha256_file(root / "ledgers/data" / f"{n}.jsonl") for n in LEDGERS}
    card["inputs"][SVAR_REG] = sha256_file(root / SVAR_REG)
    card["inputs"][SVAR_MAP] = sha256_file(root / SVAR_MAP)
    card["inputs"][SEAL] = sha256_file(root / SEAL)

    # --- 203.9 (1) total rows
    card["s203_9_1_total_rows"] = {"active_rows": N, "evd_ids_latest": len(evd_all), "deprecated_ids": len(evd_all) - N,
                                   "ledger_version_lines": evd_lines,
                                   "rows_per_source_family": {f: len(fam_rows[f]) for f in fams}}
    # --- labels
    ver = Counter(e["verification"]["status"] for e in rows)
    cond_ver = Counter(cond[e["process"]["condition_id"]]["verification"]["status"] for e in rows)
    human = sum(1 for e in rows if e["verification"]["status"] == "HUMAN_VERIFIED")
    card["labels"] = {
        "E3_UNVERIFIED": sum(1 for e in rows if e["tier"] == "E3" and e["verification"]["status"] != "HUMAN_VERIFIED"),
        "BOOTSTRAP_UNVERIFIED": N, "COND_UNAUDITED": sum(1 for e in rows if cond[e["process"]["condition_id"]]["verification"]["status"] != "HUMAN_VERIFIED"),
        "rows_total": N, "verification_status_rows": counter_dict(ver), "condition_verification_status_rows": counter_dict(cond_ver),
        "human_verified_rows": human, "d1_human_verified_target": 40, "d1_verified_rows_n_of_40": f"{human}/40",
        "meaning": {"E3_UNVERIFIED": "tier E3 and no HUMAN_VERIFIED status (AI_PRECHECKED is a rule check, not a human check)",
                    "BOOTSTRAP_UNVERIFIED": "C2-a (D-068/pre-freeze rulings): E3 may train and form a Bootstrap benchmark, never Gold, never headline",
                    "COND_UNAUDITED": "condition record carried as imported; 07.A condition-audit gate has not passed (NEG-0028, NEG-0029; v4 FAIL on the registered statistic)"}}

    # --- 203.9 (2) unique ingredients
    ing_ids = Counter(e["matrix"].get("ingredient_id") for e in rows if e["matrix"].get("ingredient_id"))
    raw_names = {f: len({e["matrix"]["raw_name"].lower() for e in fam_rows[f]}) for f in fams}
    allraw = len({e["matrix"]["raw_name"].lower() for e in rows})
    fg: dict[str, Counter] = {}
    for f in fams:
        c = Counter()
        for e in fam_rows[f]:
            g = e["matrix"].get("food_group")
            if g:
                c[g.split(" / ")[0] if f == "PHENOL-EXPLORER-3.6" else g] += 1
        fg[f] = c
    card["s203_9_2_unique_ingredients"] = {
        "unique_matrix_raw_names": allraw, "unique_matrix_raw_names_by_source": raw_names,
        "unique_ing_ids_linked": len(ing_ids), "rows_with_ing_link": sum(ing_ids.values()),
        "pct_rows_with_ing_link": pct(sum(ing_ids.values()), N),
        "pct_rows_with_ing_link_by_source": {f: pct(sum(1 for e in fam_rows[f] if e["matrix"].get("ingredient_id")), len(fam_rows[f])) for f in fams},
        "linked_ing_status": counter_dict(Counter(ing[i]["status"] for i in ing_ids.elements())),
        "top_20_ing_by_rows": [{"ing_id": i, "canonical_name": ing[i]["canonical_name"], "rows": c} for i, c in ing_ids.most_common(20)],
        "rows_per_ing_quantiles": quant(list(ing_ids.values())),
        "food_group_label_counts_usda_and_phenol_explorer_top15": {f: counter_dict(fg[f], 15) for f in fams if f != "BOGNAR-2002"},
        "food_group_distinct_labels_by_source": {f: len(fg[f]) for f in fams},
        "note": "source food-group labels are listed for USDA-RETN-R6 and the first level of Phenol-Explorer only; Bognar dish categories are counted, not listed (free text)"}

    # --- 203.9 (3) processes / families
    steps = Counter(s for e in rows for s in e["process"]["steps"])
    seqs = Counter(tuple(e["process"]["steps"]) for e in rows)
    pid = Counter(i for e in rows for i in (e["process"].get("step_process_ids") or []))
    pfam = Counter(proc[i]["family"] for i in pid.elements() if i in proc)
    kinds = Counter(proc[i]["kind"] for i in pid.elements() if i in proc)
    medium = Counter()
    for e in rows:
        m = e["process"].get("medium") or cond[e["process"]["condition_id"]].get("medium") or "NOT_RECORDED"
        medium[m] += 1
    card["s203_9_3_processes"] = {
        "unique_process_steps": len(steps), "unique_step_sequences": len(seqs),
        "rows_by_sequence_length": counter_dict(Counter(len(e["process"]["steps"]) for e in rows)),
        "unique_process_ids": len(pid), "rows_with_process_id": sum(1 for e in rows if e["process"].get("process_id")),
        "pct_rows_with_process_id": pct(sum(1 for e in rows if e["process"].get("process_id")), N),
        "process_family_step_counts": counter_dict(pfam), "process_kind_step_counts": counter_dict(kinds),
        "top_20_steps": counter_dict(steps, 20), "rows_by_medium": counter_dict(medium),
        "rows_by_source_and_first_step_top5": {f: counter_dict(Counter(e["process"]["steps"][0] for e in fam_rows[f] if e["process"]["steps"]), 5) for f in fams}}

    # --- 203.9 (4) ingredient x process pair counts + (10) pair frequency distribution
    pairs_raw = Counter((e["matrix"]["raw_name"].lower(), tuple(e["process"]["steps"])) for e in rows)
    pairs_ing = Counter((e["matrix"].get("ingredient_id"), tuple(e["process"]["steps"])) for e in rows if e["matrix"].get("ingredient_id"))
    n_mat = len({m for m, _ in pairs_raw})
    n_seq = len({p for _, p in pairs_raw})
    cells = Counter(cell_key(e, cond) for e in rows)
    card["s203_9_4_ingredient_process_pairs"] = {
        "distinct_matrix_raw_name_x_step_sequence": len(pairs_raw), "distinct_ing_id_x_step_sequence": len(pairs_ing),
        "pairs_by_source": {f: len({(e["matrix"]["raw_name"].lower(), tuple(e["process"]["steps"])) for e in fam_rows[f]}) for f in fams},
        "matrix_x_process_density": round(len(pairs_raw) / (n_mat * n_seq), 4) if n_mat and n_seq else None,
        "distinct_cells_matrix_steps_target_condition": len(cells)}
    card["s203_9_10_pair_frequency_distribution"] = {
        "rows_per_matrix_x_step_sequence_bins": bins(pairs_raw.values(), PAIR_BINS), "rows_per_matrix_x_step_sequence_quantiles": quant(list(pairs_raw.values())),
        "rows_per_ing_x_step_sequence_bins": bins(pairs_ing.values(), PAIR_BINS),
        "rows_per_cell_bins": bins(cells.values(), PAIR_BINS), "rows_per_cell_quantiles": quant(list(cells.values())),
        "pairs_seen_once": sum(1 for c in pairs_raw.values() if c == 1), "pairs_seen_once_pct": pct(sum(1 for c in pairs_raw.values() if c == 1), len(pairs_raw))}

    # --- 203.9 (5) target-type counts
    reg = {r["state_variable_id"]: r for r in csv.DictReader(open(root / SVAR_REG, newline="", encoding="utf-8"))}
    used = Counter(e["target"]["state_variable_id"] for e in rows)
    canon = Counter()
    for sid, c in used.items():
        canon[reg.get(sid, {}).get("canonical_variable_id") or sid] += c
    card["s203_9_5_target_types"] = {
        "unique_svar_ids": len(used), "unique_canonical_variables_after_duplicate_mapping": len(canon),
        "svar_family_rows": counter_dict(Counter(svar[s]["family"] for s in used.elements())),
        "registry_subfamily_rows": counter_dict(Counter(reg.get(s, {}).get("subfamily", "NOT_IN_REGISTRY") for s in used.elements())),
        "registry_status_of_used_svar_rows": counter_dict(Counter(reg.get(s, {}).get("status", "NOT_IN_REGISTRY") for s in used.elements())),
        "target_basis_rows": counter_dict(Counter(e["target"]["basis"] for e in rows)),
        "target_basis_rows_by_source": {f: counter_dict(Counter(e["target"]["basis"] for e in fam_rows[f])) for f in fams},
        "unique_svar_by_source": {f: len({e["target"]["state_variable_id"] for e in fam_rows[f]}) for f in fams},
        "top_20_targets": [{"svar_id": s, "canonical_name": svar[s]["canonical_name"], "rows": c} for s, c in used.most_common(20)],
        "rows_per_target_quantiles": quant(list(used.values()))}

    # --- 203.9 (6) evidence tier
    card["s203_9_6_evidence_tiers"] = {"tier_rows": counter_dict(Counter(e["tier"] for e in rows)),
                                       "origin_type_rows": counter_dict(Counter(e["origin_type"] for e in rows)),
                                       "design_rows": counter_dict(Counter(e["design"] for e in rows)),
                                       "applicability_rows": counter_dict(Counter(e["applicability"] for e in rows)),
                                       "verification_status_rows": counter_dict(ver),
                                       "rows_E1_E2_E4_E5_E6_E7": 0 if all(e["tier"] == "E3" for e in rows) else "SEE_TIER_ROWS"}

    # --- 203.9 (7) study / source counts, licence, lineage
    def licence_of(sid: str) -> dict:
        s = src.get(sid, {})
        return {"licence_status": s.get("licence_status", "NOT_IN_LEDGER"), "storage_rule": s.get("storage_rule"), "kind": s.get("kind"),
                "year": s.get("year"), "primary_or_secondary": s.get("primary_or_secondary"), "licence_text": s.get("licence")}
    prim = {f: Counter(e["source_id"] for e in fam_rows[f]) for f in fams}
    all_src = {f: Counter(s for e in fam_rows[f] for s in e["provenance"]["source_ids"]) for f in fams}
    lic = {}
    for f in fams:
        sids = sorted(all_src[f])
        lic[f] = {"primary_source_ids": counter_dict(prim[f]), "primary_source_licence": {s: licence_of(s) for s in prim[f]},
                  "source_ids_in_provenance": len(sids),
                  "provenance_source_licence_status_counts": counter_dict(Counter(src.get(s, {}).get("licence_status", "NOT_IN_LEDGER") for s in sids)),
                  "provenance_source_storage_rule_counts": counter_dict(Counter(src.get(s, {}).get("storage_rule", "NOT_IN_LEDGER") for s in sids)),
                  "rows_touching_a_source_with_licence_status_not_VERIFIED": sum(
                      1 for e in fam_rows[f] if any(src.get(s, {}).get("licence_status") != "VERIFIED" for s in e["provenance"]["source_ids"]))}
    studies = Counter(s for e in rows for s in e["study_ids"])
    groups = Counter(e["independence_group"] for e in rows)
    card["s203_9_7_study_source_counts"] = {
        "source_families": len(fams), "rows_by_source_family": {f: len(fam_rows[f]) for f in fams},
        "study_id_status_rows": counter_dict(Counter(e["study_id_status"] for e in rows)),
        "study_ids_in_evd": len(studies), "study_records_in_ledger": len(study),
        "rows_with_study_id": sum(1 for e in rows if e["study_ids"]),
        "independence_groups": len(groups), "independence_groups_by_source": {f: len({e["independence_group"] for e in fam_rows[f]}) for f in fams},
        "rows_per_independence_group_quantiles": quant(list(groups.values())),
        "rows_per_study_quantiles": quant(list(studies.values())),
        "extraction_version_rows": counter_dict(Counter(e["extraction_version"] for e in rows)),
        "created_by_rows": counter_dict(Counter(e["created_by"] for e in rows)),
        "lineage_note": "USDA-RETN-R6 and BOGNAR-2002 are one independence group each under the current key (lineage NOT_IDENTIFIABLE); study_disjoint evaluation is not possible for them (NEG-0002)"}
    card["licence_status"] = {"by_source_family": lic,
                              "reading": "licence_status VERIFIED / ASSUMED / UNKNOWN / RESTRICTED is the SRC ledger value; ASSUMED and UNKNOWN are owner-asserted or unresolved. "
                                         "Phenol-Explorer values are DERIVED_ONLY (cite Phenol-Explorer and the original publications; redistribution of the raw table needs the authors' permission); the per-publication SRC records have licence_status UNKNOWN. "
                                         "Not legal advice; a human licence review (H2) is still open."}

    # --- 203.9 (8) analytical platform
    mrows = Counter(e.get("measurement_method_id") or "NOT_RECORDED" for e in rows)
    card["s203_9_8_analytical_platform"] = {
        "rows_by_measurement_method_id": counter_dict(mrows),
        "measurement_method_family": {m: {"family": meas[m].get("family"), "basis": meas[m].get("basis")} for m in sorted(mrows) if m in meas},
        "rows_with_analytical_platform_recorded": 0, "rows_platform_not_recorded": N,
        "note": "MEAS records describe the calculation / gravimetry protocol of the database, not the analytical platform (HPLC, GC) of the primary measurement; "
                "no EVD row carries an analytical-platform field, and 3,870 Phenol-Explorer rows carry no measurement_method_id at all"}

    # --- 203.9 (9) coverage of T, t, pH, a_w, moisture, pressure ...
    def mask(e):
        return cond[e["process"]["condition_id"]]["completeness_mask"]
    cov = {}
    for ax in AXES:
        cov[ax] = {"rows_by_status": counter_dict(Counter(mask(e).get(ax, "ABSENT_FROM_MASK") for e in rows)),
                   "by_source": {f: counter_dict(Counter(mask(e).get(ax, "ABSENT_FROM_MASK") for e in fam_rows[f])) for f in fams}}
    both = sum(1 for e in rows if mask(e).get("temperature") in STATED and mask(e).get("duration") in STATED)
    cov["temperature_and_duration_both_stated"] = {"rows": both, "pct": pct(both, N),
                                                   "by_source": {f: sum(1 for e in fam_rows[f] if mask(e).get("temperature") in STATED and mask(e).get("duration") in STATED) for f in fams}}
    cov["water_activity"] = {"status": "NOT_IN_COND_SCHEMA", "rows_with_value": 0, "rows": N}
    cov["power"] = {"rows_with_value": sum(1 for e in rows if "power" in cond[e["process"]["condition_id"]]),
                    "by_source": {f: sum(1 for e in fam_rows[f] if "power" in cond[e["process"]["condition_id"]]) for f in fams}}
    cov["medium"] = {"rows_with_medium": N - medium["NOT_RECORDED"], "rows_by_medium": counter_dict(medium)}
    cov["distinct_condition_records_used"] = len({e["process"]["condition_id"] for e in rows})
    card["s203_9_9_condition_coverage"] = cov

    # --- 203.9 (11) missingness by source / process
    miss_src = {f: {ax: pct(sum(1 for e in fam_rows[f] if mask(e).get(ax) == "UNKNOWN"), len(fam_rows[f])) for ax in AXES} for f in fams}
    top_steps = [s for s, _ in steps.most_common(12)]
    miss_proc = {}
    for s in top_steps:
        sub = [e for e in rows if e["process"]["steps"] == [s]]
        miss_proc[s] = {"rows": len(sub), **{ax: pct(sum(1 for e in sub if mask(e).get(ax) == "UNKNOWN"), len(sub)) for ax in AXES}}
    card["s203_9_11_missingness"] = {"pct_UNKNOWN_by_source_and_axis": miss_src, "pct_UNKNOWN_by_single_step_process_top12": miss_proc,
                                     "reading": "UNKNOWN is a status, never 0 and never imputed; NOT_APPLICABLE (pressure for non-pressure sources) is not counted as missing",
                                     "rows_with_target_value_missing": sum(1 for e in rows if e["derived"].get("retention_factor", {}).get("status") == "UNKNOWN"),
                                     "retention_factor_status_rows": counter_dict(Counter(e["derived"].get("retention_factor", {}).get("status", "ABSENT") for e in rows))}

    # --- 203.9 (12) condition ranges
    temps, durs, press = defaultdict(list), defaultdict(list), defaultdict(lambda: defaultdict(list))
    for e in rows:
        c = cond[e["process"]["condition_id"]]
        f = e["source_family_id"]
        for t in c.get("temperatures", []):
            v = t["value"]
            if v["status"] == "MEASURED":
                temps[f].append(v["value"])
            elif v["status"] == "RANGE":
                temps[f] += [v["low"], v["high"]]
        d = c["duration"]
        if d["status"] == "MEASURED" and d.get("unit") == "min":
            durs[f].append(d["value"])
        elif d["status"] == "RANGE" and d.get("unit") == "min":
            durs[f] += [d["low"], d["high"]]
        if "pressure" in c and c["pressure"]["status"] == "MEASURED":
            press[f][c["pressure"].get("unit")].append(c["pressure"]["value"])
    all_t = [v for f in fams for v in temps[f]]
    all_d = [v for f in fams for v in durs[f]]
    card["s203_9_12_condition_ranges"] = {
        "temperature_degC_values": quant(all_t), "temperature_degC_values_by_source": {f: quant(temps[f]) for f in fams},
        "temperature_degC_bins": bins(all_t, T_BINS), "duration_min_values": quant(all_d), "duration_min_values_by_source": {f: quant(durs[f]) for f in fams},
        "duration_min_bins": bins(all_d, D_BINS), "pressure_by_source_and_unit": {f: {u: quant(v) for u, v in sorted(press[f].items(), key=lambda kv: str(kv[0]))} for f in fams if press[f]},
        "units": {"temperature": counter_dict(Counter(t["value"].get("unit") for c in cond.values() for t in c.get("temperatures", []))),
                  "duration": counter_dict(Counter(c["duration"].get("unit") for c in cond.values() if c["duration"]["status"] != "UNKNOWN")),
                  "pressure": counter_dict(Counter(c["pressure"].get("unit") for c in cond.values() if "pressure" in c))},
        "range_valued_conditions": {"temperature_range_rows": sum(1 for e in rows if mask(e).get("temperature") == "RANGE"),
                                    "duration_range_rows": sum(1 for e in rows if mask(e).get("duration") == "RANGE")},
        "note": "values are counted over the stated condition fields of the rows (a RANGE contributes both ends); two Phenol-Explorer-style conditions can share one record"}

    # --- 203.9 (13) duplicate / conflict audit (same logic as eda.report.evidence_section, restricted to ACTIVE)
    by_cell: dict[tuple, list[dict]] = defaultdict(list)
    for e in rows:
        by_cell[cell_key(e, cond)].append(e)
    dup = sum(c - 1 for c in Counter((cell_key(e, cond), e.get("independence_group")) for e in rows).values() if c > 1)
    conflicts = 0
    conflict_groups = Counter()
    for k, es in by_cell.items():
        dirs = {(x["derived"].get("direction"), x.get("independence_group")) for x in es}
        d_only = {d for d, _ in dirs if d in ("INCREASE", "DECREASE")}
        grp = {g for _, g in dirs}
        if len(d_only) == 2 and len(grp) > 1:
            conflicts += 1
            conflict_groups[len(grp)] += 1
    card["s203_9_13_duplicate_conflict_audit"] = {
        "distinct_cells": len(by_cell), "rows_in_cells_with_more_than_one_row": sum(len(v) for v in by_cell.values() if len(v) > 1),
        "replicate_rows_same_cell_same_independence_group": dup, "conflict_candidate_cells_opposite_direction_across_groups": conflicts,
        "conflict_groups_per_cell": counter_dict(conflict_groups),
        "cross_source_same_cell": sum(1 for v in by_cell.values() if len({e["source_family_id"] for e in v}) > 1),
        "deprecated_ids_excluded": len(evd_all) - N, "direction_rows": counter_dict(Counter(e["derived"].get("direction", "ABSENT") for e in rows)),
        "cell_key": "(matrix raw name, form, step sequence, target raw name, structural modifiers, duration) as in culinarystate.eda.report.cell_key",
        "note": "conflict candidates are candidates only; direction is derived from the retention factor, not a stated effect"}

    # --- censoring and units
    cens = Counter()
    cens_limit = Counter()
    for e in rows:
        rf = e["derived"].get("retention_factor", {})
        c = rf.get("censor")
        cens[(e["source_family_id"], c["kind"] if c else "NONE")] += 1
        if c:
            cens_limit[(e["source_family_id"], c["kind"], c["limit"])] += 1
    card["censoring"] = {"censored_rows": sum(1 for e in rows if e["censored"]), "pct_censored": pct(sum(1 for e in rows if e["censored"]), N),
                         "censored_rows_by_source": {f: sum(1 for e in fam_rows[f] if e["censored"]) for f in fams},
                         "pct_censored_by_source": {f: pct(sum(1 for e in fam_rows[f] if e["censored"]), len(fam_rows[f])) for f in fams},
                         "censor_kind_rows_by_source": {f"{k[0]}|{k[1]}": v for k, v in sorted(cens.items())},
                         "censor_limits": {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in sorted(cens_limit.items(), key=lambda kv: str(kv[0]))},
                         "reading": "GT_CAP = the source value sits at its cap (>= limit); not a measurement of the cap; censoring must be carried, never imputed"}
    units = {"retention_factor_unit_rows": counter_dict(Counter(e["derived"].get("retention_factor", {}).get("unit", "NO_RETENTION_FACTOR") for e in rows)),
             "before_after_unit_strings_rows": counter_dict(Counter(e["before"].get("unit") for e in rows if "before" in e)),
             "derived_fields_present_rows": counter_dict(Counter(k for e in rows for k in e["derived"])),
             "target_basis_rows": counter_dict(Counter(e["target"]["basis"] for e in rows)),
             "note": "'mg/100 ml' and 'mg/100 mL' are two spellings of one unit; they are not merged here (normalisation is a new column, raw preserved)"}
    card["units"] = units

    # --- seal commitment (counts only; the reserved list is neither read nor needed)
    seal = json.loads((root / SEAL).read_text(encoding="utf-8"))
    card["seal_15a_R_commitment_counts_only"] = {"snapshot_active_rows": seal["snapshot"]["active_rows"], "snapshot_evd_sha256": seal["snapshot"]["evd_sha256"],
                                                 "evd_sha256_matches_current": seal["snapshot"]["evd_sha256"] == card["inputs"]["ledgers/data/EVD.jsonl"],
                                                 "n_groups": seal["n_groups"], "n_reserved_groups": seal["n_reserved"], "n_reserved_rows": seal["n_reserved_rows"],
                                                 "strata": {k: {"n_rows": v["n_rows"], "n_groups": v["n_groups"], "n_reserved": v["n_reserved"], "n_reserved_rows": v["n_reserved_rows"]} for k, v in seal["strata"].items()},
                                                 "note": "the reserved group list is outside git and was not read; reserved rows are included in every count above because the card describes the snapshot, not a split"}
    card["ordering_note"] = ("G15-a asks that the card exists before any model-selection run: no 29-diag output and no 15b freeze record exists in this tree "
                             "(reports/step29 holds only the pre-registration draft); the run time of this card is in registry/compute_runs_v1.csv, not in the card (determinism).")
    card["known_limitations_computed"] = {
        "no_human_verified_row": human == 0, "all_rows_tier_E3": all(e["tier"] == "E3" for e in rows),
        "censored_share_pct": card["censoring"]["pct_censored"], "usda_and_bognar_single_independence_group_each": all(card["s203_9_7_study_source_counts"]["independence_groups_by_source"][f] == 1 for f in fams if f in ("USDA-RETN-R6", "BOGNAR-2002")),
        "rows_without_ing_link": N - sum(ing_ids.values()), "rows_without_process_id": N - sum(1 for e in rows if e["process"].get("process_id")),
        "rows_with_no_stated_temperature_or_duration_pct": pct(sum(1 for e in rows if mask(e).get("temperature") == "UNKNOWN" and mask(e).get("duration") == "UNKNOWN"), N),
        "water_activity_ph_moisture_never_recorded": all(mask(e).get("ph") == "UNKNOWN" and mask(e).get("moisture") == "UNKNOWN" for e in rows)}
    return card


def to_markdown(c: dict) -> str:
    g = c["s203_9_1_total_rows"]
    fams = list(g["rows_per_source_family"])
    L = ["# EVD dataset card: the ACTIVE E3 rows (S178, T2-C15-R1)", "",
         "Status: DRAFT, NOT FROZEN, NOT SIGNED (AI_DRAFTED / PROPOSED). Counts only; no recipe or paper text. Generated by "
         f"`tools/s178_analysis_evd_card.py` ({c['tool_version']}); deterministic (no timestamp). Every item of SSOT section 203.9 has a section below.", "",
         "## 0. Labels (all rows)", "",
         f"- **E3_UNVERIFIED**: {c['labels']['E3_UNVERIFIED']:,} of {c['labels']['rows_total']:,} rows (tier E3, no HUMAN_VERIFIED status). Verification status: {c['labels']['verification_status_rows']}.",
         f"- **BOOTSTRAP_UNVERIFIED**: {c['labels']['BOOTSTRAP_UNVERIFIED']:,} rows. {c['labels']['meaning']['BOOTSTRAP_UNVERIFIED']}.",
         f"- **COND_UNAUDITED**: {c['labels']['COND_UNAUDITED']:,} rows. Condition records: {c['labels']['condition_verification_status_rows']}. {c['labels']['meaning']['COND_UNAUDITED']}.",
         f"- Human-verified rows for D1: **{c['labels']['d1_verified_rows_n_of_40']}**.", "",
         "## 1. Total rows", "",
         f"- ACTIVE rows **{g['active_rows']:,}** ({g['evd_ids_latest']:,} ids, {g['deprecated_ids']} DEPRECATED excluded; {g['ledger_version_lines']:,} version lines).",
         "- By source family: " + "; ".join(f"{k} {v:,}" for k, v in g["rows_per_source_family"].items()) + ".",
         f"- Seal check: ledger sha256 equals the 15a.R commitment snapshot: **{c['seal_15a_R_commitment_counts_only']['evd_sha256_matches_current']}**; commitment holds {c['seal_15a_R_commitment_counts_only']['n_groups']} groups, {c['seal_15a_R_commitment_counts_only']['n_reserved_groups']} reserved ({c['seal_15a_R_commitment_counts_only']['n_reserved_rows']:,} rows).", ""]
    u = c["s203_9_2_unique_ingredients"]
    L += ["## 2. Unique ingredients (foods)", "",
          f"- {u['unique_matrix_raw_names']:,} distinct matrix names ({u['unique_matrix_raw_names_by_source']}); {u['unique_ing_ids_linked']:,} distinct ING concepts linked on {u['pct_rows_with_ing_link']} % of rows (by source {u['pct_rows_with_ing_link_by_source']}).",
          f"- Rows per ING concept: {u['rows_per_ing_quantiles']}.", "", "| top ING by rows | ING | rows |", "|---|---|---:|"]
    L += [f"| {t['canonical_name']} | {t['ing_id']} | {t['rows']:,} |" for t in u["top_20_ing_by_rows"][:12]]
    p = c["s203_9_3_processes"]
    L += ["", "## 3. Processes and process families", "",
          f"- {p['unique_process_steps']} distinct process steps, {p['unique_step_sequences']} step sequences ({p['rows_by_sequence_length']} rows by length), {p['unique_process_ids']} PROC ids on {p['pct_rows_with_process_id']} % of rows.",
          f"- PROC family (step counts): {p['process_family_step_counts']}. Medium (rows): {p['rows_by_medium']}.", f"- Top steps (rows): {p['top_20_steps']}.", ""]
    q = c["s203_9_4_ingredient_process_pairs"]
    d = c["s203_9_10_pair_frequency_distribution"]
    L += ["## 4. Ingredient x process pair counts, and 10. pair frequency distribution", "",
          f"- Distinct (matrix name, step sequence) pairs **{q['distinct_matrix_raw_name_x_step_sequence']:,}** (by source {q['pairs_by_source']}); distinct (ING, step sequence) {q['distinct_ing_id_x_step_sequence']:,}; matrix x process density {q['matrix_x_process_density']}; distinct cells {q['distinct_cells_matrix_steps_target_condition']:,}.",
          f"- Rows per pair: {d['rows_per_matrix_x_step_sequence_bins']} (median {d['rows_per_matrix_x_step_sequence_quantiles']['median']}); pairs seen once {d['pairs_seen_once']:,} ({d['pairs_seen_once_pct']} %).",
          f"- Rows per cell: {d['rows_per_cell_bins']}.", ""]
    t = c["s203_9_5_target_types"]
    L += ["## 5. Target-type counts", "",
          f"- {t['unique_svar_ids']} SVAR targets ({t['unique_canonical_variables_after_duplicate_mapping']} after the duplicate mapping). SVAR family (rows): {t['svar_family_rows']}. Subfamily (rows): {t['registry_subfamily_rows']}.",
          f"- Target basis (rows): {t['target_basis_rows']}. Registry status of the targets used (rows): {t['registry_status_of_used_svar_rows']}.", "", "| top targets | SVAR | rows |", "|---|---|---:|"]
    L += [f"| {x['canonical_name']} | {x['svar_id']} | {x['rows']:,} |" for x in t["top_20_targets"][:10]]
    tr = c["s203_9_6_evidence_tiers"]
    L += ["", "## 6. Evidence tiers", "", f"- Tier {tr['tier_rows']}; origin {tr['origin_type_rows']}; design {tr['design_rows']}; applicability {tr['applicability_rows']}; verification {tr['verification_status_rows']}.", ""]
    s = c["s203_9_7_study_source_counts"]
    L += ["## 7. Study and source counts, lineage, licence status", "",
          f"- {s['source_families']} source families; study_id_status {s['study_id_status_rows']}; {s['study_ids_in_evd']} study ids on {s['rows_with_study_id']:,} rows; {s['independence_groups']} independence groups ({s['independence_groups_by_source']}).",
          f"- {s['lineage_note']}.", "", "| source family | rows | primary SRC | licence_status | storage_rule | SRC records in provenance | rows touching a not-VERIFIED licence |", "|---|---:|---|---|---|---:|---:|"]
    for f in fams:
        l = c["licence_status"]["by_source_family"][f]
        ps = next(iter(l["primary_source_licence"].items()))
        L.append(f"| {f} | {g['rows_per_source_family'][f]:,} | {ps[0]} | {ps[1]['licence_status']} | {ps[1]['storage_rule']} | {l['source_ids_in_provenance']} | {l['rows_touching_a_source_with_licence_status_not_VERIFIED']:,} |")
    L += ["", c["licence_status"]["reading"], ""]
    a = c["s203_9_8_analytical_platform"]
    L += ["## 8. Analytical platform", "", f"- Rows by measurement method id: {a['rows_by_measurement_method_id']}. {a['note']}.", ""]
    v = c["s203_9_9_condition_coverage"]
    L += ["## 9. Coverage of T, t, pH, a_w, moisture, pressure", "", "| axis | MEASURED | RANGE | UNKNOWN | NOT_APPLICABLE |", "|---|---:|---:|---:|---:|"]
    for ax in AXES:
        r = v[ax]["rows_by_status"]
        L.append(f"| {ax} | {r.get('MEASURED', 0):,} | {r.get('RANGE', 0):,} | {r.get('UNKNOWN', 0):,} | {r.get('NOT_APPLICABLE', 0):,} |")
    L += ["", f"- Temperature and duration both stated: **{v['temperature_and_duration_both_stated']['rows']:,} rows ({v['temperature_and_duration_both_stated']['pct']} %)**, by source {v['temperature_and_duration_both_stated']['by_source']}.",
          f"- Water activity: {v['water_activity']['status']} (0 of {v['water_activity']['rows']:,}). Power stated on {v['power']['rows_with_value']} rows. Medium recorded on {v['medium']['rows_with_medium']:,} rows. {v['distinct_condition_records_used']:,} distinct COND records.", ""]
    m = c["s203_9_11_missingness"]
    L += ["## 11. Missingness by source and process", "", "| source | " + " | ".join(AXES) + " |", "|---|" + "---:|" * len(AXES)]
    for f, r in m["pct_UNKNOWN_by_source_and_axis"].items():
        L.append(f"| {f} | " + " | ".join(f"{r[ax]} %" for ax in AXES) + " |")
    L += ["", "| single-step process | rows | " + " | ".join(AXES) + " |", "|---|---:|" + "---:|" * len(AXES)]
    for st, r in m["pct_UNKNOWN_by_single_step_process_top12"].items():
        L.append(f"| {st} | {r['rows']:,} | " + " | ".join(f"{r[ax]} %" for ax in AXES) + " |")
    L += ["", f"- Retention factor status (rows): {m['retention_factor_status_rows']}. {m['reading']}.", ""]
    r = c["s203_9_12_condition_ranges"]
    L += ["## 12. Condition ranges", "", f"- Temperature (C), all stated values: {r['temperature_degC_values']}; bins {r['temperature_degC_bins']}.",
          f"- Duration (min): {r['duration_min_values']}; bins {r['duration_min_bins']}.", f"- Pressure by source and unit: {r['pressure_by_source_and_unit']}. Units in COND: {r['units']}.", ""]
    x = c["s203_9_13_duplicate_conflict_audit"]
    L += ["## 13. Duplicate and conflict audit", "",
          f"- {x['distinct_cells']:,} distinct cells; {x['rows_in_cells_with_more_than_one_row']:,} rows share a cell with another row; replicate rows in the same independence group {x['replicate_rows_same_cell_same_independence_group']:,}; "
          f"**{x['conflict_candidate_cells_opposite_direction_across_groups']} conflict-candidate cells** (opposite directions across independence groups); cells shared by two source families {x['cross_source_same_cell']}.", f"- {x['note']}.", ""]
    k = c["censoring"]
    un = c["units"]
    L += ["## Censoring and units", "", f"- Censored rows **{k['censored_rows']:,} ({k['pct_censored']} %)**; by source {k['censored_rows_by_source']} ({k['pct_censored_by_source']} %); limits {k['censor_limits']}.",
          f"- {k['reading']}.", f"- Retention-factor unit (rows): {un['retention_factor_unit_rows']}. Before/after unit strings: {un['before_after_unit_strings_rows']}. {un['note']}.", ""]
    L += ["## Computed limitations", ""] + [f"- {a_}: {b_}" for a_, b_ in c["known_limitations_computed"].items()]
    L += ["", "## Ordering (G15-a)", "", c["ordering_note"], "", "## Inputs (sha256)", ""] + [f"- `{a_}` `{b_}`" for a_, b_ in c["inputs"].items()]
    return "\n".join(L) + "\n"


def write(root: Path, out_dir: Path) -> tuple[str, str]:
    card = build(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    js = json.dumps(card, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    md = to_markdown(card)
    (out_dir / "evd_dataset_card_v1.json").write_text(js, encoding="utf-8")
    (out_dir / "evd_dataset_card_v1.md").write_text(md, encoding="utf-8")
    return hashlib.sha256(js.encode()).hexdigest(), hashlib.sha256(md.encode()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=str(ROOT / "reports/s178/analysis"))
    ap.add_argument("--selfcheck", action="store_true", help="run twice and require identical output")
    a = ap.parse_args(argv)
    root, out = Path(a.root), Path(a.out_dir)
    before = {n: sha256_file(root / "ledgers/data" / f"{n}.jsonl") for n in ("EVD", "COND", "SRC", "MEAS", "SNAP")}
    h1 = write(root, out)
    res = {"json_sha256": h1[0], "md_sha256": h1[1]}
    if a.selfcheck:
        h2 = write(root, out)
        res["selfcheck_identical"] = h1 == h2
        if h1 != h2:
            print(json.dumps(res))
            return 2
    after = {n: sha256_file(root / "ledgers/data" / f"{n}.jsonl") for n in before}
    res["protected_ledgers_unchanged"] = before == after
    print(json.dumps(res, sort_keys=True))
    return 0 if before == after else 3


if __name__ == "__main__":
    sys.exit(main())
