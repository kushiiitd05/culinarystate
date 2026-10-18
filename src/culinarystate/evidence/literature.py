"""Literature candidate harvest (OpenAlex, free API, polite pool) + pre-check ranking for human verification.

Queries come from a small gap-driven generator (plan W10, I3 worked examples, zero-evidence processes).
Candidates are PAPERS, not verified cells: classification is a triage for humans —
VERIFY_NOW / STRONG_CANDIDATE / NEEDS_SOURCE / CONFLICT / REJECT. AI pre-check is never human verification.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests

API = "https://api.openalex.org/works"
MAILTO = "kush23296@iiitd.ac.in"

GAP_QUERIES: tuple[tuple[str, str, str, str], ...] = (  # (query, process, target, matrix) — I3 + gap processes
    ("onion cutting alliinase lachrymatory factor synthase thiosulfinates", "cut", "thiosulfinates", "onion"),
    ("garlic crushing allicin formation heating stability", "crush", "allicin", "garlic"),
    ("enzymatic browning polyphenol oxidase cut apple banana avocado potato", "cut", "browning", "fruit"),
    ("acrylamide formation frying potato temperature time", "fry", "acrylamide", "potato"),
    ("vitamin C retention boiling steaming microwaving vegetables", "boil", "vitamin c", "vegetables"),
    ("folate losses boiling leaching vegetables cooking water", "boil", "folate", "vegetables"),
    ("chlorophyll pheophytin conversion heating green vegetables colour", "boil", "chlorophyll", "green vegetables"),
    ("glucosinolate degradation broccoli cooking methods", "steam", "glucosinolates", "broccoli"),
    ("carotenoid retention cooking carrot frying boiling", "fry", "carotenoids", "carrot"),
    ("lycopene isomerization thermal processing tomato", "heat", "lycopene", "tomato"),
    ("anthocyanin degradation kinetics heating temperature", "heat", "anthocyanins", "fruit"),
    ("pressure cooking effect nutrients legumes", "pressure-cook", "nutrients", "legumes"),
    ("microwave cooking effect phenolic compounds vegetables", "microwave", "polyphenols", "vegetables"),
    ("stir-frying effect vitamin retention vegetables", "stir-fry", "vitamins", "vegetables"),
    ("deep frying oil degradation polar compounds smoke point", "deep-fry", "polar compounds", "oil"),
    ("lipid oxidation grilling meat heterocyclic amines", "grill", "heterocyclic amines", "meat"),
    ("Maillard reaction browning roasting volatile compounds", "roast", "maillard volatiles", "various"),
    ("starch gelatinization rice cooking water ratio temperature", "boil", "starch gelatinisation", "rice"),
    ("protein denaturation egg cooking temperature texture", "boil", "protein denaturation", "egg"),
    ("sous vide cooking vitamin retention", "sous-vide", "vitamins", "vegetables"),
    ("blanching effect vitamin C vegetables before freezing", "blanch", "vitamin c", "vegetables"),
    ("tempering spices oil Indian cooking volatile compounds", "temper-spices", "volatiles", "spices"),
    ("turmeric curcumin stability cooking heat", "heat", "curcumin", "turmeric"),
    ("soaking germination phytate legumes reduction", "soak", "phytate", "legumes"),
    ("fermentation idli dosa batter nutritional changes", "ferment", "nutrients", "cereal-legume batter"),
)
PRIMARY_HINT = re.compile(r"\b(effect of|effects of|influence of|impact of|changes? in|retention|kinetics|degradation|"
                          r"formation|measured|determined|was evaluated|were analy[sz]ed)\b", re.I)
REVIEW_HINT = re.compile(r"\b(review|overview|meta-analysis|systematic|perspective|state of the art)\b", re.I)
NUMERIC_HINT = re.compile(r"(\d+(\.\d+)?\s?%|mg\s?/\s?100\s?g|µg|mg/kg|retained|retention of|decreased by|increased by|"
                          r"\b\d+\s?°C)", re.I)


def abstract_text(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def harvest(query: str, cache: Path, per_page: int = 25) -> list[dict]:
    p = cache / (re.sub(r"[^a-z0-9]+", "_", query.lower())[:120] + ".json")
    if p.exists():
        return json.loads(p.read_text())
    params = {"search": query, "filter": "type:article,has_doi:true", "per_page": per_page, "mailto": MAILTO,
              "select": "id,doi,title,publication_year,primary_location,open_access,type,cited_by_count,"
                        "abstract_inverted_index,authorships"}
    r = requests.get(API, params=params, timeout=60)
    r.raise_for_status()
    works = r.json().get("results", [])
    cache.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(works))
    time.sleep(0.3)
    return works


@dataclass(frozen=True)
class Candidate:
    doi: str
    title: str
    year: int | None
    venue: str
    open_access: bool
    oa_url: str | None
    cited_by: int
    abstract: str
    query: str
    process: str
    target: str
    matrix: str


def precheck(c: Candidate) -> tuple[str, float, list[str]]:
    """Triage class + score + reasons. Heuristic, transparent, for humans to override."""
    text = f"{c.title} {c.abstract}"
    reasons, score = [], 0.0
    proc_hit = any(w in text.lower() for w in c.process.replace("-", " ").split())
    tgt_hit = any(w in text.lower() for w in c.target.lower().split() if len(w) > 3)
    if REVIEW_HINT.search(c.title):
        return "NEEDS_SOURCE", 0.2, ["review/secondary — trace primary studies"]
    if not c.abstract:
        reasons.append("no abstract in OpenAlex")
    if proc_hit:
        score += 0.3
        reasons.append("process mentioned")
    if tgt_hit:
        score += 0.3
        reasons.append("target mentioned")
    if NUMERIC_HINT.search(c.abstract):
        score += 0.2
        reasons.append("numeric before/after or conditions in abstract")
    if PRIMARY_HINT.search(text):
        score += 0.1
        reasons.append("primary-study language")
    if c.open_access:
        score += 0.1
        reasons.append("open access (full text checkable)")
    if not (proc_hit or tgt_hit):
        return "REJECT", round(score, 2), reasons + ["off-topic for query cell"]
    score = round(score, 2)                                  # avoid 0.7999… float misclassification
    cls = "VERIFY_NOW" if score >= 0.8 else ("STRONG_CANDIDATE" if score >= 0.5 else "NEEDS_SOURCE")
    return cls, round(score, 2), reasons


def to_candidate(w: dict, q: tuple[str, str, str, str]) -> Candidate | None:
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    if not doi:
        return None
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {}).get("display_name") or ""
    oa = w.get("open_access") or {}
    return Candidate(doi, w.get("title") or "", w.get("publication_year"), src, bool(oa.get("is_oa")),
                     oa.get("oa_url"), int(w.get("cited_by_count") or 0), abstract_text(w.get("abstract_inverted_index")),
                     q[0], q[1], q[2], q[3])
