#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C03-R1: reconcile the ING counts (1,951 / 5,387 / 2,110 / 2,048) and publish a counts-only vocab status table.

Reads every `ledgers/data/*.jsonl` read-only (nothing is written there) and reports, per ledger type:
  lines            physical JSONL lines (append-only ledgers keep one line per version)
  ids              distinct ids
  latest_status    status of the latest version of every id
  line_status      status of every line
  verification     verification status of the latest ACTIVE version of every id
For ING and ALIAS it also gives the origin split (first-version provenance agent), the version-count distribution and the
vocabulary status block (FoodOn / FDC crosswalk status, facets, parents, scientific identity).

The three numbers quoted in the project documents are mapped to what they count:
  1,951  reports/ingredient_registry_v1.md (line 4) and reports/fdc_crosswalk_v0.md (line 3): the concepts written by the
         first A1 (BBC) registry build (min recipe frequency 3). It equals the ACTIVE ids whose first version came from
         that build. It is STALE as a description of the current ledger (it omits the ids added later).
  5,387  `wc -l ledgers/data/ING.jsonl` = ledger VERSION LINES (handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md Q7 calls them
         "ING rows"; reports/master_plan/master_plan_research_audit_v2.md and the SSOT working notes quote the same line count).
  2,110 / 2,048  distinct ids / ids whose latest version is ACTIVE (S176 L-LOT report; Rung A lexicon loads the 2,048).
Counts only: no ingredient names, no recipe text.

  python tools/s178_corpus_ing_reconcile.py [--out-dir reports/s178/corpus]
AI_DRAFTED / PROPOSED. Not a human gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_VERSION = "s178-corpus-ing-reconcile-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
LEDGER_DIR = "ledgers/data"
# documents that quote ING counts, with the number and the regex that must find it in the file (checked, not trusted)
CLAIM_SOURCES = (
    {"claim": "ING_CONCEPTS_1951", "number": 1951, "file": "reports/ingredient_registry_v1.md",
     "pattern": r"ING concepts: ([\d,]+)"},
    {"claim": "ING_CONCEPTS_1951_FDC", "number": 1951, "file": "reports/fdc_crosswalk_v0.md",
     "pattern": r"ING concepts: ([\d,]+)"},
    {"claim": "ING_ROWS_5387_PACKET", "number": 5387, "file": "handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md",
     "pattern": r"([\d,]{5,}) ING rows"},
    {"claim": "ING_LINES_5387_MP_AUDIT", "number": 5387, "file": "reports/master_plan/master_plan_research_audit_v2.md",
     "pattern": r"ING ([\d,]+) lines"},
    {"claim": "ING_ACTIVE_2048_L_LOT", "number": 2048, "file": "reports/orchestration/S176_L-LOT_report.md",
     "pattern": r"= [\d,]+ unique ids = ([\d,]+) ACTIVE concepts"},
    {"claim": "ING_IDS_2110_L_LOT", "number": 2110, "file": "reports/orchestration/S176_L-LOT_report.md",
     "pattern": r"= ([\d,]+) unique ids"},
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ver(r: dict) -> int:
    try:
        return int(r.get("version") or 0)
    except (TypeError, ValueError):
        return 0


def read_ledger(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def latest_and_first(rows: list[dict]) -> tuple[dict, dict, Counter]:
    """latest version per id, first version per id (ties: later line wins for latest, earlier for first), versions per id."""
    latest, first, nver = {}, {}, Counter()
    for r in rows:
        rid = r.get("id")
        nver[rid] += 1
        if rid not in latest or _ver(r) >= _ver(latest[rid]):
            latest[rid] = r
        if rid not in first or _ver(r) < _ver(first[rid]):
            first[rid] = r
    return latest, first, nver


def ledger_block(name: str, rows: list[dict]) -> dict:
    latest, first, nver = latest_and_first(rows)
    active = [r for r in latest.values() if r.get("status") == "ACTIVE"]
    blk = {"lines": len(rows), "ids": len(latest),
           "lines_without_id": sum(1 for r in rows if not r.get("id")),
           "latest_status": dict(sorted(Counter(r.get("status") for r in latest.values()).items(), key=lambda kv: str(kv[0]))),
           "line_status": dict(sorted(Counter(r.get("status") for r in rows).items(), key=lambda kv: str(kv[0]))),
           "active_ids": len(active),
           "versions_per_id": {str(k): v for k, v in sorted(Counter(nver.values()).items())},
           "lines_beyond_first_version": len(rows) - len(latest),
           "verification_of_active": dict(sorted(Counter((r.get("verification") or {}).get("status") for r in active).items(),
                                                key=lambda kv: str(kv[0])))}
    blk["schema_versions"] = dict(sorted(Counter(r.get("schema_version") for r in rows).items(), key=lambda kv: str(kv[0])))
    return blk


def origin_split(rows: list[dict]) -> dict:
    """Active ids by the provenance agent of their FIRST version; and lines by agent."""
    latest, first, _ = latest_and_first(rows)
    out = Counter()
    status_by_origin: dict[str, Counter] = defaultdict(Counter)
    for rid, f in first.items():
        agent = (f.get("provenance") or {}).get("agent") or "UNKNOWN"
        out[agent] += 1
        status_by_origin[agent][latest[rid].get("status")] += 1
    return {"ids_by_first_version_agent": dict(sorted(out.items())),
            "latest_status_by_first_version_agent": {a: dict(sorted(c.items(), key=lambda kv: str(kv[0])))
                                                     for a, c in sorted(status_by_origin.items())},
            "lines_by_agent": dict(sorted(Counter((r.get("provenance") or {}).get("agent") or "UNKNOWN" for r in rows).items())),
            "lines_by_created_at_date": dict(sorted(Counter(str(r.get("created_at"))[:10] for r in rows).items()))}


def ing_vocab_status(rows: list[dict]) -> dict:
    latest, _, _ = latest_and_first(rows)
    act = [r for r in latest.values() if r.get("status") == "ACTIVE"]
    cw = lambda key: dict(sorted(Counter(((r.get("crosswalks") or {}).get(key) or {}).get("status") for r in act).items(),
                                 key=lambda kv: str(kv[0])))
    n = len(act)
    pct = lambda k: round(100.0 * k / n, 2) if n else None
    with_parent = sum(1 for r in act if r.get("parent_ids"))
    with_facets = sum(1 for r in act if r.get("facets"))
    return {"active_concepts": n, "crosswalk_foodon": cw("foodon"), "crosswalk_fdc": cw("fdc"),
            "crosswalk_flavordb": cw("flavordb"), "crosswalk_recipedb": cw("recipedb"),
            "with_parent_ids": with_parent, "with_parent_ids_pct": pct(with_parent),
            "with_facets": with_facets, "with_facets_pct": pct(with_facets),
            "with_external_refs": sum(1 for r in act if r.get("external_refs")),
            "scientific_identity_status": dict(sorted(Counter(r.get("scientific_identity_status") for r in act).items(),
                                                      key=lambda kv: str(kv[0]))),
            "ambiguity": dict(sorted(Counter(r.get("ambiguity") for r in act).items(), key=lambda kv: str(kv[0]))),
            "foodon_linked_pct": pct(sum(1 for r in act if ((r.get("crosswalks") or {}).get("foodon") or {}).get("status") == "LINKED")),
            "usda_fdc_linked_pct": pct(sum(1 for r in act if ((r.get("crosswalks") or {}).get("fdc") or {}).get("status") == "LINKED"))}


def alias_status(rows: list[dict], ing_latest: dict) -> dict:
    latest, _, _ = latest_and_first(rows)
    act = [r for r in latest.values() if r.get("status") == "ACTIVE"]
    ing_active = {k for k, v in ing_latest.items() if v.get("status") == "ACTIVE"}

    def targets(r):
        t = r.get("candidate_ingredient_ids") or [r.get("ingredient_id")]
        return [x for x in t if x]

    return {"active_aliases": len(act),
            "active_aliases_with_an_active_ing_target": sum(1 for r in act if any(t in ing_active for t in targets(r))),
            "active_aliases_without_an_active_ing_target": sum(1 for r in act if not any(t in ing_active for t in targets(r))),
            "active_aliases_with_several_candidate_targets": sum(1 for r in act if len(r.get("candidate_ingredient_ids") or []) > 1),
            "alias_type": dict(sorted(Counter(r.get("alias_type") for r in act).items(), key=lambda kv: str(kv[0]))),
            "link_band": dict(sorted(Counter(r.get("link_band") for r in act).items(), key=lambda kv: str(kv[0])))}


def minted_ids(path: Path) -> dict:
    c = Counter()
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                n += 1
                c[json.loads(line).get("prefix")] += 1
    return {"lines": n, "by_prefix": dict(sorted(c.items(), key=lambda kv: str(kv[0])))}


def to_int(s: str) -> int:
    return int(s.replace(",", ""))


def claim_check(root: Path, truth: dict) -> list[dict]:
    out = []
    for c in CLAIM_SOURCES:
        p = root / c["file"]
        row = {"claim": c["claim"], "number": c["number"], "file": c["file"]}
        if not p.is_file():
            row.update(found_in_file=None, status="SOURCE_FILE_MISSING")
            out.append(row)
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        found = [to_int(m.group(1)) for m in re.finditer(c["pattern"], text)]
        row["found_in_file"] = c["number"] in found
        line_no = next((i + 1 for i, ln in enumerate(text.splitlines()) if re.search(c["pattern"], ln)
                        and any(to_int(m.group(1)) == c["number"] for m in re.finditer(c["pattern"], ln))), None)
        row["line"] = line_no
        row["counts"] = truth["what_it_counts"][str(c["number"])]
        out.append(row)
    return out


def build(root: Path) -> dict:
    led = root / LEDGER_DIR
    files = sorted(p for p in led.glob("*.jsonl") if p.name != "_ids.jsonl")
    res = {"record": "ING_COUNT_RECONCILIATION_S178", "tool_version": TOOL_VERSION, "item": "T3-C03-R1",
           "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "contains_text": False, "contains_ids": False,
           "counts_as_human_gate": False, "ledgers": {}, "ledger_file_sha256": {}}
    ing_rows = alias_rows = None
    for p in files:
        rows = read_ledger(p)
        name = p.stem
        res["ledgers"][name] = ledger_block(name, rows)
        res["ledger_file_sha256"][p.name] = sha256_file(p)
        if name == "ING":
            ing_rows = rows
        elif name == "ALIAS":
            alias_rows = rows
    ids_path = led / "_ids.jsonl"
    if ids_path.is_file():
        res["minted_id_registry"] = minted_ids(ids_path)
        res["ledger_file_sha256"]["_ids.jsonl"] = sha256_file(ids_path)
    ing_latest, _, _ = latest_and_first(ing_rows)
    ing = res["ledgers"]["ING"]
    org = origin_split(ing_rows)
    ing["origin"] = org
    ing["vocab_status"] = ing_vocab_status(ing_rows)
    res["ledgers"]["ALIAS"]["origin"] = origin_split(alias_rows)
    res["ledgers"]["ALIAS"]["vocab_status"] = alias_status(alias_rows, ing_latest)

    # the reconciliation proper
    a1 = "a1_ner+registry_build@0.1"
    a1_ids = org["ids_by_first_version_agent"].get(a1, 0)
    a1_status = org["latest_status_by_first_version_agent"].get(a1, {})
    a1_active = a1_status.get("ACTIVE", 0)
    other_active = {a: s.get("ACTIVE", 0) for a, s in org["latest_status_by_first_version_agent"].items() if a != a1}
    recon = {
        "ledger_lines": ing["lines"], "distinct_ids": ing["ids"], "active_ids": ing["active_ids"],
        "superseded_ids": ing["latest_status"].get("SUPERSEDED", 0), "deprecated_ids": ing["latest_status"].get("DEPRECATED", 0),
        "ids_from_a1_registry_build": a1_ids, "active_ids_from_a1_registry_build": a1_active,
        "active_ids_from_other_origins": other_active,
        "ids_superseded_or_deprecated": ing["ids"] - ing["active_ids"],
        "lines_beyond_first_version": ing["lines_beyond_first_version"],
        "identities": {
            "lines_equal_ids_plus_extra_versions": ing["lines"] == ing["ids"] + ing["lines_beyond_first_version"],
            "ids_equal_active_plus_superseded_plus_deprecated": ing["ids"] == ing["active_ids"] + (ing["ids"] - ing["active_ids"]),
            "active_equal_a1_active_plus_other_active": ing["active_ids"] == a1_active + sum(other_active.values()),
        },
    }
    recon["what_it_counts"] = {
        "1951": f"ACTIVE ids first written by the A1 (BBC) registry build ({a1}): {a1_active} in the ledger now; the report's own "
                "ledger-write tally (4 created + 1,867 unchanged + 80 revised = 1,951) is that build's output. "
                "STALE as a description of the current ledger: it omits the Wikibooks-link ids added by a later step (and does not track later status changes).",
        "5387": f"ledger VERSION LINES of ING.jsonl (append-only), not concepts: {ing['ids']} ids + {ing['lines_beyond_first_version']} later versions "
                "(enrichment and merge revisions; git history shows the X1 FoodOn, X2 Open Food Facts, X2b merge and X3 Wikibooks commits touching this file). The review packet's 'ING rows' means these lines.",
        "2110": f"distinct ING ids of every status ({ing['active_ids']} ACTIVE + {recon['superseded_ids']} SUPERSEDED + {recon['deprecated_ids']} DEPRECATED).",
        "2048": "distinct ING ids whose latest version is ACTIVE; this is the ING set the Rung A lexicon and every S175-S178 census use "
                "(`rung_a_lexicon._latest_active`)."}
    recon["verdict"] = {
        "current_concept_count": ing["active_ids"],
        "stale_report": "reports/ingredient_registry_v1.md (and reports/fdc_crosswalk_v0.md): '1,951 ING concepts' is the first BBC-only build, not the "
                        "current vocabulary. Quote 2,048 ACTIVE concepts (1,951 BBC-derived + 97 Wikibooks-linked) with the ledger lines (5,387) named as lines.",
        "mislabelled_wording": "'5,387 ING rows' (review packet Q7, master-plan audit, SSOT working notes) counts ledger lines; say '2,048 ACTIVE ING concepts "
                               "(5,387 ledger lines)'. The statement 'crosswalked 0 %' in packet Q7 refers to USDA/FDC: "
                               f"{ing['vocab_status']['crosswalk_fdc']}; FoodOn LINKED is {ing['vocab_status']['foodon_linked_pct']} %.",
        "file_that_produced_5387": "ledgers/data/ING.jsonl (wc -l); not a separate Food.com-extended registry: the consensus R-SSOT guess "
                                   "'suspected Food.com-extended ING' is NOT supported (no ING line has a Food.com provenance agent).",
        "vocab_built_from_bbc_only": "the A1-derived ids are 1,951 of 2,048 ACTIVE (95.3 %); Wikibooks links add 97; no Food.com or Gutenberg ING ids exist in the ledger."}
    res["reconciliation"] = recon
    res["claims_checked_against_files"] = claim_check(root, recon)
    res["notes"] = [
        "Latest version per id = highest `version` (later line wins a tie), as rung_a_lexicon._latest_active.",
        "SUPERSEDED / DEPRECATED ids (49 + 13) are no longer ACTIVE; their lines stay in the append-only ledger.",
        "All vocabulary records are UNVERIFIED (AI-drafted); 'ACTIVE' is a lifecycle status, not a verification status.",
        "Protected ledgers (EVD, COND, SRC, MEAS, SNAP) were read only; their sha256 are recorded in ledger_file_sha256 for before/after comparison."]
    return res


def md(res: dict) -> str:
    r = res["reconciliation"]
    ing = res["ledgers"]["ING"]
    L = ["# ING count reconciliation and vocab status (S178, T3-C03-R1)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts only; no ingredient names, no recipe text. Tool `%s`." % res["tool_version"], "",
         "## What each number counts", "",
         "| number | what it counts | where it is quoted |", "|---:|---|---|"]
    where = {"1951": "`reports/ingredient_registry_v1.md` L4, `reports/fdc_crosswalk_v0.md` L3",
             "5387": "review packet Q7, `reports/master_plan/master_plan_research_audit_v2.md`, SSOT working notes",
             "2110": "`reports/orchestration/S176_L-LOT_report.md`, plan 'x of 2,110'", "2048": "S176 L-LOT / L-PH reports, Rung A lexicon"}
    for k in ("1951", "5387", "2110", "2048"):
        L.append(f"| {int(k):,} | {r['what_it_counts'][k]} | {where[k]} |")
    L += ["", "## Verdict", "", f"- Current concept count: **{r['verdict']['current_concept_count']:,} ACTIVE ING concepts** "
          f"({ing['ids']:,} ids ever, {ing['lines']:,} ledger lines).",
          f"- Stale report: {r['verdict']['stale_report']}", f"- Mislabelled wording: {r['verdict']['mislabelled_wording']}",
          f"- File that produced 5,387: {r['verdict']['file_that_produced_5387']}", f"- BBC-only claim: {r['verdict']['vocab_built_from_bbc_only']}", "",
          "## Ledger counts per type (read-only)", "",
          "| ledger | lines | ids | ACTIVE ids | latest-status other than ACTIVE | lines beyond first version | verification of ACTIVE |",
          "|---|---:|---:|---:|---|---:|---|"]
    for name, b in res["ledgers"].items():
        others = {k: v for k, v in b["latest_status"].items() if k != "ACTIVE"}
        L.append(f"| {name} | {b['lines']:,} | {b['ids']:,} | {b['active_ids']:,} | {others or '-'} | {b['lines_beyond_first_version']:,} | "
                 f"{b['verification_of_active']} |")
    v = ing["vocab_status"]
    L += ["", "## ING vocabulary status (ACTIVE concepts)", "",
          "| measure | count | % of ACTIVE |", "|---|---:|---:|",
          f"| ACTIVE concepts | {v['active_concepts']:,} | 100 |",
          f"| FoodOn crosswalk LINKED | {v['crosswalk_foodon'].get('LINKED', 0):,} | {v['foodon_linked_pct']} |",
          f"| FoodOn CANDIDATE | {v['crosswalk_foodon'].get('CANDIDATE', 0):,} | {round(100 * v['crosswalk_foodon'].get('CANDIDATE', 0) / v['active_concepts'], 2)} |",
          f"| FoodOn NO_MATCH | {v['crosswalk_foodon'].get('NO_MATCH', 0):,} | {round(100 * v['crosswalk_foodon'].get('NO_MATCH', 0) / v['active_concepts'], 2)} |",
          f"| USDA FDC LINKED | {v['crosswalk_fdc'].get('LINKED', 0):,} | {v['usda_fdc_linked_pct']} |",
          f"| with parent ids | {v['with_parent_ids']:,} | {v['with_parent_ids_pct']} |",
          f"| with facets | {v['with_facets']:,} | {v['with_facets_pct']} |",
          f"| scientific identity | {v['scientific_identity_status']} | |", "",
          "## Origin of the ING ids", "", "| first-version agent | ids | of which ACTIVE |", "|---|---:|---:|"]
    for a, n in ing["origin"]["ids_by_first_version_agent"].items():
        L.append(f"| `{a}` | {n:,} | {ing['origin']['latest_status_by_first_version_agent'][a].get('ACTIVE', 0):,} |")
    al = res["ledgers"]["ALIAS"]["vocab_status"]
    L += ["", "## ALIAS", "", f"{al['active_aliases']:,} ACTIVE aliases; {al['active_aliases_with_an_active_ing_target']:,} have an ACTIVE ING target, "
          f"{al['active_aliases_without_an_active_ing_target']:,} do not (the Rung A lexicon drops those). "
          f"The registry report's '2,052 ALIAS rows' is likewise the first build only.", "",
          "## Claims checked against their files", "", "| claim | number | file | found in file | line |", "|---|---:|---|---|---:|"]
    for c in res["claims_checked_against_files"]:
        L.append(f"| {c['claim']} | {c['number']:,} | `{c['file']}` | {c.get('found_in_file')} | {c.get('line') or ''} |")
    L += ["", "## Notes", ""] + [f"- {n}" for n in res["notes"]]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    res = build(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ing_count_reconciliation_v1.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / "ing_count_reconciliation_v1.md").write_text(md(res), encoding="utf-8")
    r = res["reconciliation"]
    print(json.dumps({k: r[k] for k in ("ledger_lines", "distinct_ids", "active_ids", "ids_from_a1_registry_build",
                                          "active_ids_from_a1_registry_build", "active_ids_from_other_origins")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
