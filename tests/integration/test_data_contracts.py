"""SSOT §257I.6 data-contract / release audit over the real ledgers.

A release fails if provenance, checksums, references, split/seed registry or schema versions are missing — whatever
the model metrics say. Also the DEL-1 clause: 100% of EVD rows carry source, tier, condition status, censoring flag.
"""
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from culinarystate.ledgers.validate import errors

pytestmark = pytest.mark.ledgers
ROOT = Path(__file__).resolve().parents[2]
CORE = ["SRC", "SNAP", "EVD", "COND", "SVAR", "MEAS", "ING", "ALIAS", "PROC", "TOOL", "UNIT", "MOL", "IMAP", "KGE",
        "ALLERGEN"]
ID = re.compile(r"^([A-Z]+)-\d{6}$")


def test_every_latest_record_validates_and_has_schema_version(latest):
    bad = Counter()
    for t in CORE:
        for r in latest(t):
            if errors(r) or not r.get("schema_version"):
                bad[t] += 1
    assert not bad, f"invalid records: {dict(bad)}"


def test_ids_are_unique_and_never_reused(store):
    seen = Counter()
    for line in (ROOT / "ledgers" / "data" / "_ids.jsonl").open():
        seen[json.loads(line)["id"]] += 1
    assert not [i for i, n in seen.items() if n > 1]


def test_sources_have_licence_and_storage_rule(latest):
    missing = [s["id"] for s in latest("SRC") if not s.get("licence") or not s.get("storage_rule")]
    assert not missing, missing[:10]


def test_snapshots_have_checksum_and_resolve(latest):
    src = {s["id"] for s in latest("SRC")}
    bad = [s["id"] for s in latest("SNAP") if not re.fullmatch(r"[0-9a-f]{64}", s.get("sha256") or "")
           or s.get("source_id") not in src]
    assert not bad, bad[:10]


def test_del1_clause_every_evd_row_has_source_tier_condition_status_censoring(latest):
    src = {s["id"] for s in latest("SRC")}
    cond = {c["id"]: c for c in latest("COND")}
    bad = []
    for e in latest("EVD"):
        if e["status"] != "ACTIVE":
            continue
        cid = e["process"].get("condition_id")
        ok = (e["source_id"] in src and e.get("tier") and isinstance(e.get("censored"), bool)
              and (cid is None or (cid in cond and cond[cid].get("completeness_mask"))))
        if not ok:
            bad.append(e["id"])
    assert not bad, f"{len(bad)} EVD rows break the DEL-1 clause, e.g. {bad[:5]}"


def test_no_dangling_references(latest):
    ids = {t: {r["id"] for r in latest(t)} for t in ("ING", "PROC", "COND", "SVAR", "MEAS", "MOL", "TOOL", "SRC")}
    dangling = Counter()
    for e in latest("EVD"):
        refs = [e["matrix"].get("ingredient_id"), e["process"].get("process_id"), e["process"].get("condition_id"),
                e["target"].get("state_variable_id"), e.get("measurement_method_id"),
                *(e["process"].get("step_process_ids") or [])]
        for r in filter(None, refs):
            if r.split("-")[0] in ids and r not in ids[r.split("-")[0]]:
                dangling[("EVD", r.split("-")[0])] += 1
    for k in latest("KGE"):
        for r in (k["subject_id"], k.get("object_id")):
            m = ID.match(r or "")
            if m and m.group(1) in ids and r not in ids[m.group(1)]:
                dangling[("KGE", m.group(1))] += 1
    for m in latest("IMAP"):
        if m["ingredient_id"] not in ids["ING"] or m["molecule_id"] not in ids["MOL"]:
            dangling[("IMAP", "ING/MOL")] += 1
    assert not dangling, dict(dangling)


def test_third_party_recipe_text_is_not_in_ledgers(latest):
    """D-003: REC carries hashes/metadata; raw text stays in data/raw or data/interim (git-ignored)."""
    allowed = {"content_sha256", "created_at", "created_by", "cuisine", "external_refs", "family_id", "id",
               "n_ingredient_lines", "n_steps", "provenance", "raw_location", "record_type", "schema_version",
               "source_url", "status", "title", "verification", "version", "notes"}
    extra = Counter(k for r in latest("REC") for k in r if k not in allowed)
    assert not extra, dict(extra)


def test_experiment_cards_record_command_seed_and_split(latest):
    cards = sorted((ROOT / "experiments").glob("EXP-*/card.md"))
    assert cards
    for c in cards:
        t = c.read_text()
        assert "**Command:**" in t and re.search(r"seed \d+", t) and "split" in t.lower(), c


def test_deprecated_records_are_not_reused_as_active_targets(latest):
    dep_ing = {i["id"] for i in latest("ING") if i["status"] != "ACTIVE"}
    used = Counter(e["matrix"]["ingredient_id"] for e in latest("EVD")
                   if e["status"] == "ACTIVE" and e["matrix"].get("ingredient_id") in dep_ing)
    assert not used, f"ACTIVE EVD linked to non-active ING: {dict(used.most_common(5))}"
