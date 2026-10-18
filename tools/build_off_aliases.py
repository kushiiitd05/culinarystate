#!/usr/bin/env python3
"""X2: Open Food Facts ingredient taxonomy -> ING external refs + new ALIAS records (D-009).

  /opt/anaconda3/bin/python tools/build_off_aliases.py
ING canonical (or UK->US variant) must equal an OFF English name of exactly one OFF entry. Then:
  - ING.external_refs += OFF:<id>, WIKIDATA:<Q>   (OFF's USDA FDC codes -> CSV candidates only, D-006)
  - ALIAS (key off:<lang>:<surface>): other English names (SYNONYM) + Indian-language names (TRANSLATION);
    a surface already aliased to a different ING is a collision -> skipped and listed, never overwritten.
Writes registry/ingredients/off_crosswalk_v1.csv, off_alias_collisions.csv, reports/off_taxonomy_v1.md.
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import fetch  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.fdc import UK_US  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402
from culinarystate.vocab.off import INDIAN_LANGS, parse  # noqa: E402

COMMIT = "a1ce1d36214b8426548f18849f25c7b4baffe08c"
URL = f"https://raw.githubusercontent.com/openfoodfacts/openfoodfacts-server/{COMMIT}/taxonomies/food/ingredients.txt"
RAW = ROOT / "data" / "raw" / "off" / f"ingredients_{COMMIT[:8]}.txt"
CB = "Kush+Claude"


def merge_hint(a: str, b: str) -> str:
    """Duplicate-concept hint for a collision: same word modulo plural, or X vs 'X cheese'/'X leaf' -> MERGE."""
    na, nb = norm(a), norm(b)
    if na == nb or {na, nb} & {f"{nb} cheese", f"{na} cheese", f"{nb} leaf", f"{na} leaf"}:
        return "SAME_CONCEPT_MERGE"
    return "KEEP_SEPARATE_OFF_LUMPS" if na and nb else "CHECK"


def source_records(st: LedgerStore) -> str:
    snap = fetch(URL, RAW)
    sid = st.ids.mint("SRC", key="off:ingredients-taxonomy")
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "DATASET", "title": "Open Food Facts ingredients taxonomy (taxonomies/food/ingredients.txt)",
               "url": URL, "publisher": "Open Food Facts", "licence": "ODbL 1.0 (database) / DbCL (contents)",
               "licence_status": "VERIFIED", "storage_rule": "COMMIT_OK", "primary_or_secondary": "SECONDARY",
               "source_family_id": "OFF-TAXONOMY", "notes": f"pinned commit {COMMIT}; attribution required (ODbL)"})
    st.upsert({"id": st.ids.mint("SNAP", key=f"sha256:{snap.sha256}"), "record_type": "SNAP", "status": "ACTIVE",
               "created_by": CB, "provenance": {"method": "IMPORT", "source_ids": [sid]},
               "verification": {"status": "UNVERIFIED"}, "source_id": sid, "retrieved_at": snap.retrieved_at,
               "retrieval_url": snap.url, "sha256": snap.sha256, "bytes": snap.bytes, "local_path": snap.local_path,
               "http_status": snap.http_status, "source_version": f"git {COMMIT[:12]}"})
    return sid


def main() -> None:
    st = LedgerStore()
    sid = source_records(st)
    off = parse(RAW)
    en_index: dict[str, set[str]] = {}
    for e in off.values():
        for n in e.names.get("en", []):
            en_index.setdefault(norm(n), set()).add(e.id)
    for a in st.all_latest("ALIAS"):                   # migrate OFF aliases if norm() changed (e.g. accent folding)
        if a["status"] == "ACTIVE" and sid in a["provenance"]["source_ids"] and a["language"] == "en" \
                and a["normalized"] != norm(a["surface"]):
            st.upsert({**a, "normalized": norm(a["surface"])})
    alias_owner = {a["normalized"]: a["ingredient_id"] for a in st.all_latest("ALIAS") if a["status"] == "ACTIVE"}
    ings = [i for i in st.all_latest("ING") if i["status"] == "ACTIVE"]
    canon_owner = {norm(i["canonical_name"]): i["id"] for i in ings}
    rows, coll, w_ing, w_al, langs = [], [], Counter(), Counter(), Counter()
    for ing in ings:
        name = ing["canonical_name"]
        hits = set().union(*[en_index.get(norm(n), set()) for n in [name, *UK_US.get(name, [])]])
        status = "LINKED" if len(hits) == 1 else ("AMBIGUOUS" if hits else "NO_MATCH")
        rows.append({"ing_id": ing["id"], "canonical_name": name, "corpus_frequency": ing.get("corpus_frequency"),
                     "status": status, "off_ids": " | ".join(sorted(hits))})
        if status != "LINKED":
            continue
        e = off[next(iter(hits))]
        rows[-1].update({"wikidata": e.props.get("wikidata"), "off_fdc_code": e.props.get("usda_fdc_code"),
                         "density_g_per_ml_ecobalyse": e.props.get("ecobalyse_density_g_per_ml"),
                         "raw_to_cooked_ratio_ecobalyse": e.props.get("ecobalyse_raw_to_cooked_ratio"),
                         "off_parents": " | ".join(e.parents)})
        refs = [r for r in (ing.get("external_refs") or []) if not r.startswith(("OFF:", "WIKIDATA:"))]
        refs.append(f"OFF:{e.id}")
        if e.props.get("wikidata"):
            refs.append(f"WIKIDATA:{e.props['wikidata']}")
        w_ing[st.upsert({**ing, "external_refs": sorted(refs)})[0]] += 1
        for lang, names in e.names.items():
            if lang != "en" and lang not in INDIAN_LANGS:
                continue
            for surface in names:
                key = norm(surface) if lang == "en" else surface.strip().lower()
                if not key:
                    continue
                owner = alias_owner.get(key) or (canon_owner.get(key) if lang == "en" else None)
                if owner == ing["id"]:
                    continue
                if owner:
                    coll.append({"surface": surface, "lang": lang, "off_entry": e.id, "wanted_ing": ing["id"],
                                 "existing_ing": owner})
                    continue
                rec = {"id": st.ids.mint("ALIAS", key=f"off:{lang}:{key}"), "record_type": "ALIAS", "status": "ACTIVE",
                       "created_by": CB, "provenance": {"method": "IMPORT", "source_ids": [sid],
                                                        "agent": "off_taxonomy@0.1", "locator": f"OFF entry {e.id}"},
                       "verification": {"status": "UNVERIFIED"}, "surface": surface, "normalized": key,
                       "ingredient_id": ing["id"], "candidate_ingredient_ids": [ing["id"]], "language": lang,
                       "region": "IN" if lang in INDIAN_LANGS else None,
                       "alias_type": "SYNONYM" if lang == "en" else "TRANSLATION", "link_band": "HIGH",
                       "corpus_frequency": None, "external_refs": [f"OFF:{e.id}"]}
                w_al[st.upsert(rec)[0]] += 1
                alias_owner[key] = ing["id"]
                langs[lang] += 1
    out = ROOT / "registry" / "ingredients"
    df = pd.DataFrame(rows).sort_values("corpus_frequency", ascending=False)
    df.to_csv(out / "off_crosswalk_v1.csv", index=False)
    names = {i["id"]: i["canonical_name"] for i in ings}
    cdf = pd.DataFrame(coll, columns=["surface", "lang", "off_entry", "wanted_ing", "existing_ing"])
    cdf["wanted_name"], cdf["existing_name"] = cdf.wanted_ing.map(names), cdf.existing_ing.map(names)
    cdf["ai_suggestion"] = [merge_hint(a, b) for a, b in zip(cdf.wanted_name.fillna(""), cdf.existing_name.fillna(""))]
    cdf["human_decision"] = ""
    cdf.to_csv(out / "off_alias_collisions.csv", index=False)
    st_c = df.status.value_counts()
    mentions = df.corpus_frequency.sum()
    lines = ["# Open Food Facts taxonomy crosswalk v1 (X2, D-009)", "",
             f"OFF entries parsed: {len(off):,} (pinned {COMMIT[:12]}, ODbL). ING concepts: {len(df):,}.", "",
             "| status | concepts | % corpus mentions |", "|---|---|---|"]
    for s in ("LINKED", "AMBIGUOUS", "NO_MATCH"):
        lines.append(f"| {s} | {st_c.get(s, 0):,} | {100 * df[df.status == s].corpus_frequency.sum() / mentions:.1f}% |")
    lines += ["", f"New aliases: {sum(langs.values()):,} — " + ", ".join(f"{k} {v}" for k, v in langs.most_common()),
              f"Alias collisions skipped (see off_alias_collisions.csv): {len(coll):,} — AI hint: "
              + ", ".join(f"{k} {v}" for k, v in cdf.ai_suggestion.value_counts().items()),
              f"Linked with Wikidata QID: {df.wikidata.notna().sum():,}; with OFF→FDC code: {df.off_fdc_code.notna().sum():,}"
              f"; with Ecobalyse density: {df.density_g_per_ml_ecobalyse.notna().sum():,}",
              "Densities / raw-to-cooked ratios are listed for the quantity ladder (Q-density path) as source-stated "
              "candidates; they are not yet ledger values."]
    (ROOT / "reports" / "off_taxonomy_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:]), "\nING writes:", dict(w_ing), "ALIAS writes:", dict(w_al))


if __name__ == "__main__":
    main()
