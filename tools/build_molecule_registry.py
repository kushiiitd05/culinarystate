#!/usr/bin/env python3
"""MOL- (PubChem) + IMAP- (ingredient↔molecule, typed) from evidence targets.

  /opt/anaconda3/bin/python tools/build_molecule_registry.py
MOL: every EVD target that is a single molecule (aggregates refused) -> PubChem identity, descriptors,
CACTVS 881-bit fingerprint (ECFP pending rdkit). SVAR gets the MOL link in external_refs.
IMAP (linked ING only): MEASURED_CONCENTRATION from 'before processing' contents (raw food, basis kept);
PROCESS_CHANGE pointing to the EVD rows. Nothing numeric is created that was not measured.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.molecules.pubchem import PubChem, fingerprint_hex, molecule_name, stereo_status  # noqa: E402

st = LedgerStore()
pc = PubChem(ROOT / "data" / "raw" / "pubchem")
pubchem_src = st.ids.mint("SRC", key="pubchem:pug-rest")
counts = Counter()
counts[("SRC", st.upsert({
    "id": pubchem_src, "record_type": "SRC", "status": "ACTIVE", "created_by": "Kush+Claude",
    "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
    "kind": "API", "title": "PubChem PUG-REST (NCBI)", "url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug",
    "licence": "Public domain data (NCBI); cite PubChem", "licence_status": "ASSUMED", "storage_rule": "COMMIT_OK",
    "primary_or_secondary": "SECONDARY", "source_family_id": "PUBCHEM"})[0])] += 1

evd = st.all_latest("EVD")
targets = Counter(e["target"]["raw_name"] for e in evd)
mol_of_target, unresolved, refused = {}, [], []
for t in sorted(targets):
    name = molecule_name(t)
    if name is None:
        refused.append(t)
        continue
    pr = pc.by_name(name)
    if not pr or not pr.get("InChIKey"):
        unresolved.append(t)
        continue
    mid = st.ids.mint("MOL", key=pr["InChIKey"])
    fp = fingerprint_hex(pr.get("Fingerprint2D"))
    rec = {"id": mid, "record_type": "MOL", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "IMPORT", "source_ids": [pubchem_src], "locator": f"CID {pr['CID']}",
                          "notes": f"resolved from evidence target name '{t}' via '{name}'"},
           "verification": {"status": "UNVERIFIED"}, "inchikey": pr["InChIKey"], "pubchem_cid": int(pr["CID"]),
           "preferred_name": name, "synonyms": [t] if t.lower() != name else [],
           "canonical_smiles": pr.get("CanonicalSMILES"), "isomeric_smiles": pr.get("IsomericSMILES"),
           "formula": pr.get("MolecularFormula"), "molecular_weight": pr.get("MolecularWeight"),
           "stereo_status": stereo_status(pr.get("IsomericSMILES"), pr.get("CanonicalSMILES")),
           "descriptors": {k: float(pr[k]) for k in ("XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount",
                                                     "RotatableBondCount", "HeavyAtomCount") if pr.get(k) is not None},
           "fingerprints": {"pubchem_cactvs_881": fp} if fp else {}}
    counts[("MOL", st.upsert(rec)[0])] += 1
    mol_of_target[t] = mid

# SVAR -> MOL link
for sv in st.all_latest("SVAR"):
    t = sv["canonical_name"].removesuffix(" content")
    mid = mol_of_target.get(t)
    if mid and f"MOL:{mid}" not in sv.get("external_refs", []):
        counts[("SVAR", st.upsert({**sv, "external_refs": sv.get("external_refs", []) + [f"MOL:{mid}"]})[0])] += 1

# IMAP: only rows whose matrix is linked to an ING concept and target is a molecule
conc = {}
change = defaultdict(list)
for e in evd:
    ing, mid = e["matrix"].get("ingredient_id"), mol_of_target.get(e["target"]["raw_name"])
    if not ing or not mid:
        continue
    change[(ing, mid)].append(e["id"])
    b = e.get("before") or {}
    if b.get("status") == "MEASURED" and (ing, mid, e["target"]["basis"]) not in conc:
        conc[(ing, mid, e["target"]["basis"])] = (b, e["id"], e["matrix"].get("initial_state"))
for (ing, mid, basis), (b, eid, state) in sorted(conc.items()):
    rid = st.ids.mint("IMAP", key=f"conc:{ing}:{mid}:{basis}")
    counts[("IMAP", st.upsert({
        "id": rid, "record_type": "IMAP", "status": "ACTIVE", "created_by": "Kush+Claude",
        "provenance": {"method": "DERIVED", "source_ids": [pubchem_src], "locator": f"EVD {eid} before value",
                       "notes": "first measured before-processing content; other studies remain in EVD"},
        "verification": {"status": "UNVERIFIED"}, "ingredient_id": ing, "molecule_id": mid,
        "relation": "MEASURED_CONCENTRATION", "concentration": {**b, "raw": b.get("raw")}, "basis": basis,
        "state_id_or_form": state or "before processing", "evidence_ids": [eid]})[0])] += 1
for (ing, mid), eids in sorted(change.items()):
    rid = st.ids.mint("IMAP", key=f"change:{ing}:{mid}")
    counts[("IMAP", st.upsert({
        "id": rid, "record_type": "IMAP", "status": "ACTIVE", "created_by": "Kush+Claude",
        "provenance": {"method": "DERIVED", "source_ids": [pubchem_src], "locator": f"{len(eids)} EVD rows"},
        "verification": {"status": "UNVERIFIED"}, "ingredient_id": ing, "molecule_id": mid,
        "relation": "PROCESS_CHANGE", "evidence_ids": sorted(eids)[:200]})[0])] += 1

out = ROOT / "registry" / "molecules"
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame([{"target": t, "mol_id": m} for t, m in mol_of_target.items()]).to_csv(out / "target_molecule_map.csv",
                                                                                   index=False)
pd.DataFrame({"target": unresolved}).to_csv(out / "unresolved_targets.csv", index=False)
pd.DataFrame({"target": refused}).to_csv(out / "aggregate_targets_svar_only.csv", index=False)
print(dict(counts))
print(f"targets {len(targets)}: molecules {len(mol_of_target)}, aggregates (SVAR only) {len(refused)}, "
      f"unresolved {len(unresolved)}: {unresolved[:15]}")
