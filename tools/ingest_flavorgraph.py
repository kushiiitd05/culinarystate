#!/usr/bin/env python3
"""X9: FlavorGraph (Park et al. 2021, Sci Rep; repo lamypark/FlavorGraph @8d3472d) -> MOL + IMAP PRESENCE + KGE.

  /opt/anaconda3/bin/python tools/ingest_flavorgraph.py
Counts and checksums the released files first (SSOT Q-N1). Ingredient-compound links become IMAP PRESENCE
observations (qualitative, source = FlavorGraph/FlavorDB, never concentrations). Ingredient-ingredient NPMI edges
become KGE ING_CO_OCCURS with corpus FLAVORGRAPH-RECIPE1M (kept separate from our corpora by key).
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import sha256_file  # noqa: E402
from culinarystate.kg.edges import band  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.molecules.pubchem import PubChem, by_cids, fingerprint_hex, stereo_status  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

COMMIT = "8d3472d0823f4542b2ce47f83e28046c41d2f06a"
D = ROOT / "data" / "raw" / "flavorgraph"
CB, AGENT = "Kush+Claude", "flavorgraph@0.1"


def names_map(st):
    names = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en" and a["alias_type"] != "AMBIGUOUS":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    return names


def main() -> None:
    st = LedgerStore()
    nodes, edges = pd.read_csv(D / "nodes_191120.csv"), pd.read_csv(D / "edges_191120.csv")
    counts = {"nodes": len(nodes), "by_type": nodes.node_type.value_counts().to_dict(), "edges": len(edges),
              "edge_types": edges.edge_type.value_counts().to_dict()}
    linked_ingr = edges[edges.edge_type.str.startswith("ingr-") & (edges.edge_type != "ingr-ingr")].id_1.nunique()
    sid = st.ids.mint("SRC", key="flavorgraph:repo")
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "REPO", "title": "FlavorGraph (Park et al. 2021, Sci Rep 11:931) released graph files",
               "url": f"https://github.com/lamypark/FlavorGraph/tree/{COMMIT}/input", "year": 2021,
               "licence": "Apache-2.0 (repository); data derived from Recipe1M + FlavorDB (CC BY-NC-SA 3.0)",
               "licence_status": "ASSUMED", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "SECONDARY",
               "source_family_id": "FLAVORGRAPH",
               "notes": f"released-file counts: {counts}; ingredients with compound links: {linked_ingr}"})
    for f in ("nodes_191120.csv", "edges_191120.csv"):
        sha = sha256_file(D / f)
        st.upsert({"id": st.ids.mint("SNAP", key=f"sha256:{sha}"), "record_type": "SNAP", "status": "ACTIVE",
                   "created_by": CB, "provenance": {"method": "IMPORT", "source_ids": [sid]},
                   "verification": {"status": "UNVERIFIED"}, "source_id": sid, "retrieved_at": "2026-10-18T17:00:00+05:30",
                   "retrieval_url": f"https://raw.githubusercontent.com/lamypark/FlavorGraph/{COMMIT}/input/{f}",
                   "sha256": sha, "bytes": (D / f).stat().st_size, "local_path": f"data/raw/flavorgraph/{f}",
                   "http_status": 200, "source_version": f"git {COMMIT[:12]}"})
    names = names_map(st)
    ing_nodes = nodes[nodes.node_type == "ingredient"]
    node_ing = {int(r.node_id): names.get(norm(str(r.name).replace("_", " "))) for r in ing_nodes.itertuples()}
    comp = nodes[nodes.node_type == "compound"].dropna(subset=["id"])
    pc = PubChem(ROOT / "data" / "raw" / "pubchem")
    props = by_cids(pc, sorted({int(c) for c in comp.id}))
    pubchem_src = st.ids.mint("SRC", key="pubchem:pug-rest")
    w = Counter()
    node_mol = {}
    for r in comp.itertuples():
        pr = props.get(int(r.id))
        if not pr or not pr.get("InChIKey"):
            continue
        existing = st.ids.lookup("MOL", pr["InChIKey"])
        mid = st.ids.mint("MOL", key=pr["InChIKey"])
        node_mol[int(r.node_id)] = mid
        if existing and st.latest(existing):
            continue                                   # molecule already owned by build_molecule_registry
        fp = fingerprint_hex(pr.get("Fingerprint2D"))
        w[("MOL", st.upsert({
            "id": mid, "record_type": "MOL", "status": "ACTIVE", "created_by": CB,
            "provenance": {"method": "IMPORT", "source_ids": [pubchem_src, sid], "locator": f"CID {pr['CID']}",
                           "notes": f"FlavorGraph compound node {r.node_id} ({r.name})"},
            "verification": {"status": "UNVERIFIED"}, "inchikey": pr["InChIKey"], "pubchem_cid": int(pr["CID"]),
            "preferred_name": str(r.name), "synonyms": [],
            "canonical_smiles": pr.get("CanonicalSMILES"), "isomeric_smiles": pr.get("IsomericSMILES"),
            "formula": pr.get("MolecularFormula"), "molecular_weight": pr.get("MolecularWeight"),
            "stereo_status": stereo_status(pr.get("IsomericSMILES"), pr.get("CanonicalSMILES")),
            "descriptors": {k: float(pr[k]) for k in ("XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount",
                                                      "RotatableBondCount", "HeavyAtomCount") if pr.get(k) is not None},
            "fingerprints": {"pubchem_cactvs_881": fp} if fp else {}})[0])] += 1
    # several FlavorGraph nodes can map to one ING, so aggregate per ledger key first, then write once (idempotent)
    unmapped_ing, co, pres = Counter(), {}, {}
    for e in edges.itertuples():
        a, b = int(e.id_1), int(e.id_2)
        if e.edge_type == "ingr-ingr":
            ia, ib = node_ing.get(a), node_ing.get(b)
            if not ia or not ib or ia == ib:
                continue
            for s_, o_ in ((ia, ib), (ib, ia)):
                best = co.get((s_, o_))
                score = round(float(e.score), 4)
                if best is None or (score, -min(a, b)) > (best[0], -min(best[1])):
                    co[(s_, o_)] = (score, (a, b), (best[2] + 1) if best else 1)
                else:
                    co[(s_, o_)] = (best[0], best[1], best[2] + 1)
        else:
            ing_node, comp_node = (a, b) if a in node_ing else (b, a)
            ia, mid = node_ing.get(ing_node), node_mol.get(comp_node)
            if not ia:
                unmapped_ing[ing_node] += 1
                continue
            if mid:
                pres.setdefault((ia, mid), set()).add((e.edge_type, f"{a}-{b}"))
    for (s_, o_), (score, (a, b), n) in sorted(co.items()):
        w[("KGE", st.upsert({
            "id": st.ids.mint("KGE", key=f"ING_CO_OCCURS|{s_}|{o_}|FLAVORGRAPH"), "record_type": "KGE",
            "status": "ACTIVE", "created_by": CB,
            "provenance": {"method": "IMPORT", "source_ids": [sid], "agent": AGENT,
                           "locator": f"edges_191120.csv ingr-ingr {a}-{b}" + (f" (max of {n} node pairs)" if n > 1 else "")},
            "verification": {"status": "UNVERIFIED"}, "predicate": "ING_CO_OCCURS", "subject_id": s_,
            "object_id": o_, "object_value": None, "support": {"recipes": 0},
            "association": {"pmi": score}, "confidence": min(1.0, max(0.0, score)),
            "confidence_band": "MEDIUM" if score >= 0.25 else "LOW", "method": "EXTERNAL_SOURCE",
            "corpus_ids": ["FLAVORGRAPH-RECIPE1M"],
            "notes": "score = FlavorGraph NPMI over Recipe1M (recipe counts not released)"})[0])] += 1
    for (ia, mid), links in sorted(pres.items()):
        types = sorted({t for t, _ in links})
        locs = sorted(f"{t} {pair}" for t, pair in links)
        w[("IMAP", st.upsert({
            "id": st.ids.mint("IMAP", key=f"flavorgraph:{ia}:{mid}"), "record_type": "IMAP", "status": "ACTIVE",
            "created_by": CB, "provenance": {"method": "IMPORT", "source_ids": [sid], "agent": AGENT,
                                              "locator": "edges_191120.csv " + "; ".join(locs[:5]) +
                                                         (f" (+{len(locs) - 5} more)" if len(locs) > 5 else "")},
            "verification": {"status": "UNVERIFIED"}, "ingredient_id": ia, "molecule_id": mid,
            "relation": "PRESENCE",
            "concentration": {"status": "QUALITATIVE", "qualitative": "reported present (FlavorDB via FlavorGraph)",
                              "value": None, "low": None, "high": None},
            "state_id_or_form": None,
            "notes": "drug-compound link (ingr-dcomp)" if types == ["ingr-dcomp"] else
                     "food- and drug-compound links" if len(types) > 1 else None})[0])] += 1
    mapped = sum(1 for v in node_ing.values() if v)
    lines = ["# FlavorGraph ingest v1 (X9)", "", f"- released-file counts (Q-N1): {counts}",
             f"- ingredients with ≥1 compound link: {linked_ingr} of {counts['by_type'].get('ingredient')}",
             f"- FlavorGraph ingredient nodes mapped to ING: {mapped:,} / {len(ing_nodes):,}",
             f"- compounds resolved to InChIKey via PubChem: {len(node_mol):,} / {len(comp):,}",
             f"- compound-linked ingredient nodes not mapped to ING: {len(unmapped_ing)}",
             f"- ledger writes: {dict(w)}",
             "- IMAP = qualitative PRESENCE observations (SSOT §65.x); NC-licensed upstream (FlavorDB) → no public/commercial redistribution."]
    (ROOT / "reports" / "flavorgraph_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
