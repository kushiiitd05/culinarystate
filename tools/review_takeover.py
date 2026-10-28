#!/usr/bin/env python3
"""Read-only AI evidence audit; no scientific evaluation, human labels or recipe text.

Writes tracked aggregate/ID evidence to reports/review/machine_evidence.json and
local-only FlavorGraph review worksheets beneath ignored features/step35/.
Never invokes ingestion scripts or writes ledgers. All verdict columns stay blank.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.vocab.foodon import norm

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def latest_records(records):
    latest = {}
    versions = {}
    for r in records:
        key = (r["id"], r["version"])
        if key in versions and versions[key] != r:
            raise ValueError(f"conflicting equal versions for {r['id']}")
        versions[key] = r
        old = latest.get(r["id"])
        if old is None or r["version"] > old["version"]:
            latest[r["id"]] = r
    return latest


def ledger(name):
    with (ROOT / f"ledgers/data/{name}.jsonl").open() as f:
        return latest_records(json.loads(line) for line in f if line.strip())


def read_source_sheet(path):
    """Read cached values of this source's sheet1, preserving sparse cell positions.

    This is a source-specific OOXML reader, not a general Excel implementation.
    It does not evaluate formulas; the reviewed source contains cached cells.
    """
    with ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(t.text or "" for t in si.findall(".//s:t", NS))
                       for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("s:si", NS)]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        parsed = []
        for row in sheet.findall("s:sheetData/s:row", NS):
            cells = {}
            for c in row.findall("s:c", NS):
                col = re.sub(r"\d", "", c.attrib["r"])
                v = c.find("s:v", NS)
                text = v.text if v is not None and v.text is not None else ""
                if c.get("t") == "s":
                    text = strings[int(text)]
                elif c.get("t") == "inlineStr":
                    text = "".join(t.text or "" for t in c.findall(".//s:t", NS))
                cells[col] = text
            parsed.append(cells)
    if not parsed:
        raise ValueError("source worksheet is empty")
    header = parsed[0]
    return [{name: row.get(col, "") for col, name in header.items() if name}
            for row in parsed[1:] if any(row.values())]


def audit_taste_migrations(records, source_rows, molecules):
    latest = latest_records(records)
    by_source_id = defaultdict(list)
    for r in source_rows:
        if r.get("ID"):
            by_source_id[str(r["ID"])].append(r)
    active = defaultdict(list)
    for r in latest.values():
        if r["status"] == "ACTIVE" and r.get("provenance", {}).get("agent") == "chemtastesdb@0.1":
            active[(r["subject_id"], r["provenance"].get("locator"))].append(r)
    pairs = []
    for r in sorted(latest.values(), key=lambda r: r["id"]):
        if r["status"] != "DEPRECATED" or r.get("provenance", {}).get("agent") != "chemtastesdb@0.1":
            continue
        locator = r["provenance"].get("locator", "")
        match = re.match(r"ChemTastesDB ID (\S+) ", locator)
        source_id = match[1] if match else None
        source = by_source_id.get(source_id, [])
        replacements = active[(r["subject_id"], locator)]
        one_source, one_replacement = len(source) == 1, len(replacements) == 1
        s = source[0] if one_source else {}
        a = replacements[0] if one_replacement else {}
        cid = molecules.get(r["subject_id"], {}).get("pubchem_cid")
        try:
            cid_match = cid is not None and float(cid) == float(s.get("PubChem CID", ""))
        except (ValueError, TypeError):
            cid_match = False
        pair = {
            "deprecated_edge_id": r["id"], "deprecated_version": r["version"],
            "molecule_id": r["subject_id"], "source_tastant_id": source_id,
            "replacement_count": len(replacements), "source_row_count": len(source),
            "replacement_edge_id": a.get("id"), "replacement_version": a.get("version"),
            "source_cid_match": cid_match,
            "source_free_text_match": one_source and str(r.get("object_value", "")).strip() == s.get("Taste", "").strip(),
            "source_class_match": one_source and one_replacement and str(a.get("object_value", "")).strip() == s.get("Class taste", "").strip(),
        }
        pair["migration_explained"] = one_source and one_replacement and all(
            pair[k] for k in ("source_cid_match", "source_free_text_match", "source_class_match"))
        pairs.append(pair)
    return {"deprecated": len(pairs), "fully_explained": sum(p["migration_explained"] for p in pairs),
            "interpretation": "AI_PRECHECK_ONLY: free-text to curated-class migration; not proof of taste validity",
            "pairs": pairs}


def crosswalk_candidates():
    ingredients, aliases = ledger("ING"), ledger("ALIAS")
    names, candidates = {}, defaultdict(set)
    for i in ingredients.values():
        if i["status"] == "ACTIVE":
            key = norm(i["canonical_name"])
            names[key] = i["id"]
            candidates[key].add(i["id"])
    for a in aliases.values():
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en" and a["alias_type"] != "AMBIGUOUS":
            key = norm(a["normalized"])
            names.setdefault(key, a["ingredient_id"])
            candidates[key].add(a["ingredient_id"])
    with (ROOT / "data/raw/flavorgraph/nodes_191120.csv").open(newline="") as f:
        nodes = {r["node_id"]: r for r in csv.DictReader(f)}
    linked = set()
    with (ROOT / "data/raw/flavorgraph/edges_191120.csv").open(newline="") as f:
        for e in csv.DictReader(f):
            if e["edge_type"] != "ingr-ingr":
                for key in ("id_1", "id_2"):
                    if nodes[e[key]]["node_type"] == "ingredient":
                        linked.add(e[key])
    rows = []
    for node_id in sorted(linked, key=int):
        n = nodes[node_id]
        key = norm(n["name"].replace("_", " "))
        iid = names.get(key)
        if not iid:
            continue
        flags = []
        if len(candidates[key]) > 1:
            flags.append("NORMALISED_NAME_COLLISION")
        target = ingredients.get(iid, {})
        if target.get("status") != "ACTIVE":
            flags.append("TARGET_NOT_ACTIVE")
        if n["name"].replace("_", " ").casefold() != target.get("canonical_name", "").casefold():
            flags.append("ALIAS_OR_NORMALISATION_MATCH")
        rows.append({"source_node_id": node_id, "source_name": n["name"], "normalised_key": key,
                     "proposed_ingredient_id": iid, "ingredient_name": target.get("canonical_name", ""),
                     "candidate_ingredient_ids": ";".join(sorted(candidates[key])),
                     "ai_flags": ";".join(flags), "ai_status": "AUTOMATED_MATCH_ONLY",
                     "human_verdict": "", "human_reviewer": "", "human_notes": ""})
    return rows, {"compound_linked_source_nodes": len(linked), "mapped_crosswalks": len(rows),
                  "distinct_ingredient_ids": len({r["proposed_ingredient_id"] for r in rows}),
                  "name_collision_rows": sum("NORMALISED_NAME_COLLISION" in r["ai_flags"] for r in rows),
                  "inactive_target_rows": sum("TARGET_NOT_ACTIVE" in r["ai_flags"] for r in rows)}


def write_review_csv(path, rows):
    if path.exists():
        with path.open(newline="") as f:
            if any(any(r.get(k, "").strip() for k in ("human_verdict", "human_reviewer", "human_notes"))
                   for r in csv.DictReader(f)):
                raise ValueError(f"refusing to overwrite human review in {path}")
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    source = ROOT / "data/raw/chemtastesdb/ChemTastesDB_database.xlsx"
    source_rows = read_source_sheet(source)
    with (ROOT / "ledgers/data/KGE.jsonl").open() as f:
        taste = [r for line in f if (r := json.loads(line)).get("predicate") == "MOL_HAS_TASTE"]
    migration = audit_taste_migrations(taste, source_rows, ledger("MOL"))
    crosswalks, crosswalk_summary = crosswalk_candidates()
    local = ROOT / "features/step35/ai_review"
    local.mkdir(parents=True, exist_ok=True)
    packet = sorted(crosswalks, key=lambda r: hashlib.sha256(
        f"crosswalk-review-v1|20261028|{r['source_node_id']}|{r['proposed_ingredient_id']}".encode()).hexdigest())[:50]
    for name, rows in [("crosswalk_all_candidates.csv", crosswalks), ("crosswalk_50_human_review.csv", packet)]:
        write_review_csv(local / name, rows)
    priority = [r for r in crosswalks if any(flag in r["ai_flags"] for flag in
                ("NORMALISED_NAME_COLLISION", "TARGET_NOT_ACTIVE"))]
    if priority:
        write_review_csv(local / "crosswalk_priority_review.csv", priority)
    active_imap = [r for r in ledger("IMAP").values() if r["status"] == "ACTIVE"
                   and r["relation"] == "PRESENCE" and r.get("provenance", {}).get("agent") == "flavorgraph@0.1"]
    reconstructed_ids = {r["proposed_ingredient_id"] for r in crosswalks}
    profile_ids = {r["ingredient_id"] for r in active_imap}
    crosswalk_summary.update(active_presence_rows=len(active_imap),
                             active_profile_ingredient_ids=len(profile_ids),
                             reconstruction_profile_id_difference=sorted(reconstructed_ids ^ profile_ids),
                             priority_review_rows=len(priority))
    inputs = [source, ROOT / "data/raw/flavorgraph/nodes_191120.csv", ROOT / "data/raw/flavorgraph/edges_191120.csv"]
    inputs += [ROOT / f"ledgers/data/{n}.jsonl" for n in ("KGE", "MOL", "ING", "ALIAS", "IMAP")]
    inputs += [ROOT / p for p in ("tools/review_takeover.py", "tools/ingest_chemtastesdb.py", "tools/ingest_flavorgraph.py",
                                "src/culinarystate/vocab/foodon.py")]
    evidence = {"status": "AI_PRECHECK_ONLY_PENDING_EXPERT", "review_date": "2026-10-28",
                "input_sha256": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
                "source_xlsx_md5": digest(source, "md5"),
                "source_nonempty_rows": len(source_rows),
                "source_rows_with_id": sum(bool(r.get("ID")) for r in source_rows),
                "source_distinct_ids": len({r["ID"] for r in source_rows if r.get("ID")}),
                "taste_migrations": migration, "crosswalk_structure": crosswalk_summary,
                "crosswalk_packet": {"rows": len(packet), "path": str((local / "crosswalk_50_human_review.csv").relative_to(ROOT)),
                                     "selection": "lowest SHA256(crosswalk-review-v1|20261028|source_node_id|ING), mapped compound-linked nodes only; review worksheet, not pilot draw or performance sample",
                                     "sha256": digest(local / "crosswalk_50_human_review.csv"),
                                     "all_candidates_sha256": digest(local / "crosswalk_all_candidates.csv")},
                "human_verification": "PENDING; no human verdict assigned; all ledgers untouched"}
    out = ROOT / "reports/review/machine_evidence.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"source_nonempty_rows": len(source_rows), "source_rows_with_id": evidence["source_rows_with_id"],
                      "deprecated": migration["deprecated"], "source_explained": migration["fully_explained"],
                      "crosswalk_structure": crosswalk_summary, "packet_rows": len(packet),
                      "evidence": str(out.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
