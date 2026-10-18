"""PubChem PUG-REST client (name -> CID -> properties), cached, ≤ 4 requests/s.

Only single, well-defined molecules are resolved. Aggregate targets ("…, total", "Vitamin A, IU",
"Lutein + zeaxanthin", minerals, compound classes) are refused by `molecule_name()` and stay SVAR-only.
"""
from __future__ import annotations

import base64
import json
import re
import time
from pathlib import Path

import requests

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PROPS = ("InChIKey,CanonicalSMILES,IsomericSMILES,MolecularFormula,MolecularWeight,XLogP,TPSA,HBondDonorCount,"
         "HBondAcceptorCount,RotatableBondCount,HeavyAtomCount,Fingerprint2D,IUPACName")
UA = {"User-Agent": "CulinaryState-research/0.1 (IIIT Delhi; kush23296@iiitd.ac.in)"}

# explicit renames for USDA nutrient names (single molecules only)
RENAME = {"vitamin c, total ascorbic acid": "ascorbic acid", "thiamin": "thiamine", "riboflavin": "riboflavin",
          "niacin": "nicotinic acid", "folic acid": "folic acid", "carotene, beta": "beta-carotene",
          "carotene, alpha": "alpha-carotene", "cryptoxanthin, beta": "beta-cryptoxanthin", "lycopene": "lycopene",
          "alcohol, ethyl": "ethanol"}
AGGREGATE = re.compile(r"\b(total|iu|re|and|vitamin b-6|vitamin b-12|vitamin a|folate|choline|calcium|iron|"
                       r"magnesium|phosphorus|potassium|sodium|zinc|copper|anthocyanins|flavonoids|polyphenols|"
                       r"proanthocyanidins|tannins|lignans|phenolic acids)\b", re.IGNORECASE)


def molecule_name(target: str) -> str | None:
    t = target.strip().lower()
    if t in RENAME:
        return RENAME[t]
    if "+" in t or AGGREGATE.search(t) or ("," in t and t not in RENAME):
        return None
    return t


class PubChem:
    def __init__(self, cache_dir: Path, pause_s: float = 0.25):
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.pause_s = pause_s

    def _get(self, url: str, key: str) -> dict | None:
        p = self.cache / f"{re.sub(r'[^A-Za-z0-9_.-]+', '_', key)[:150]}.json"
        if p.exists():
            data = json.loads(p.read_text())
            return data or None
        for attempt in range(4):
            r = requests.get(url, headers=UA, timeout=30)
            if r.status_code == 200:
                data = r.json()
                break
            if r.status_code == 404:
                data = {}
                break
            time.sleep(2 * (attempt + 1))
        else:
            return None
        p.write_text(json.dumps(data))
        time.sleep(self.pause_s)
        return data or None

    def by_name(self, name: str) -> dict | None:
        q = requests.utils.quote(name)
        d = self._get(f"{BASE}/compound/name/{q}/property/{PROPS}/JSON", f"name_{name}")
        if not d:
            return None
        props = d.get("PropertyTable", {}).get("Properties", [])
        if not props:
            return None
        pr = dict(props[0])
        # PubChem renamed fields (2025): ConnectivitySMILES = no stereo, SMILES = isomeric
        pr.setdefault("CanonicalSMILES", pr.get("ConnectivitySMILES"))
        pr.setdefault("IsomericSMILES", pr.get("SMILES"))
        if pr.get("MolecularWeight") is not None:
            pr["MolecularWeight"] = float(pr["MolecularWeight"])
        return pr


def stereo_status(isomeric: str | None, canonical: str | None) -> str:
    if not isomeric:
        return "UNKNOWN"
    if "@" in isomeric or "/" in isomeric or "\\" in isomeric:
        return "DEFINED" if isomeric != canonical else "PARTIAL"
    return "UNDEFINED"


def fingerprint_hex(b64: str | None) -> str | None:
    """PubChem CACTVS 881-bit substructure fingerprint (base64, 4-byte length prefix) -> hex."""
    if not b64:
        return None
    raw = base64.b64decode(b64)
    return raw[4:].hex()


def tanimoto_hex(a: str, b: str) -> float:
    x, y = int(a, 16), int(b, 16)
    inter, union = bin(x & y).count("1"), bin(x | y).count("1")
    return inter / union if union else 0.0
