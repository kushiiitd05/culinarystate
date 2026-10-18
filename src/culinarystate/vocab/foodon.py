"""FoodOn (CC BY 4.0) RDF/XML -> term table + name index for ING crosswalks.

Only FOODON_* classes that are not deprecated/obsolete. Names: rdfs:label (score 1.0), exact synonyms and IAO
alternative terms (0.9), the label with its parenthetical qualifier removed — "tomato (whole, raw)" -> "tomato"
(0.85), related/broad synonyms (0.7). A name shared by several terms is ambiguous: all are returned, none is LINKED.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

NS = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
      "owl": "http://www.w3.org/2002/07/owl#", "obo": "http://purl.obolibrary.org/obo/",
      "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#"}
OBO = "http://purl.obolibrary.org/obo/"
RDF_ABOUT = f"{{{NS['rdf']}}}about"
RDF_RES = f"{{{NS['rdf']}}}resource"
SYN_TAGS = {"oboInOwl:hasExactSynonym": 0.9, "obo:IAO_0000118": 0.9, "oboInOwl:hasRelatedSynonym": 0.7,
            "oboInOwl:hasBroadSynonym": 0.6, "oboInOwl:hasNarrowSynonym": 0.6}


@dataclass
class Term:
    id: str
    label: str
    synonyms: dict[str, float] = field(default_factory=dict)
    parents: list[str] = field(default_factory=list)


def norm(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())
    words = [w[:-3] + "y" if w.endswith("ies") and len(w) > 4 else
             (w[:-2] if re.search(r"(oes|ches|shes|sses|xes)$", w) else
              (w[:-1] if w.endswith("s") and not w.endswith("ss") and len(w) > 3 else w)) for w in s.split()]
    return " ".join(words)


def strip_qualifier(label: str) -> str:
    return re.sub(r"\s*\([^)]*\)", "", label).strip()


def parse(path: Path) -> dict[str, Term]:
    terms: dict[str, Term] = {}
    for _, el in etree.iterparse(str(path), events=("end",), tag=f"{{{NS['owl']}}}Class", huge_tree=True):
        about = el.get(RDF_ABOUT) or ""
        if about.startswith(OBO + "FOODON_"):
            dep = el.findtext("owl:deprecated", namespaces=NS)
            label = el.findtext("rdfs:label", namespaces=NS)
            if label and dep != "true" and not label.lower().startswith("obsolete"):
                t = Term(about[len(OBO):], label.strip())
                for tag, sc in SYN_TAGS.items():
                    for s in el.findall(tag, namespaces=NS):
                        if s.text and s.text.strip():
                            t.synonyms[s.text.strip()] = max(sc, t.synonyms.get(s.text.strip(), 0))
                t.parents = [p.get(RDF_RES)[len(OBO):] for p in el.findall("rdfs:subClassOf", namespaces=NS)
                             if (p.get(RDF_RES) or "").startswith(OBO)]
                terms[t.id] = t
        el.clear()
    return terms


def name_index(terms: dict[str, Term]) -> dict[str, dict[str, float]]:
    """normalised name -> {term_id: best score}."""
    idx: dict[str, dict[str, float]] = {}

    def add(name: str, tid: str, sc: float) -> None:
        k = norm(name)
        if k:
            d = idx.setdefault(k, {})
            d[tid] = max(sc, d.get(tid, 0))
    for t in terms.values():
        add(t.label, t.id, 1.0)
        if strip_qualifier(t.label) != t.label:
            add(strip_qualifier(t.label), t.id, 0.85)
        for s, sc in t.synonyms.items():
            add(s, t.id, sc)
    return idx


def ancestors(tid: str, terms: dict[str, Term], limit: int = 40) -> list[str]:
    out, stack, seen = [], list(terms[tid].parents) if tid in terms else [], set()
    while stack and len(out) < limit:
        p = stack.pop(0)
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
        stack.extend(terms[p].parents if p in terms else [])
    return out
