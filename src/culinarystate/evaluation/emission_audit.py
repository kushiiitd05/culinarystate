"""Separate lexical/structural emission audit; never a scorer or semantic certificate.

Counts/hashes only. Numeric alignment uses half a two-decimal rounding unit;
that engineering setting is not a scientific threshold or a replacement for C17.
Unknown numeric types and missing provenance remain explicit review gaps.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

CIT = re.compile(r"EVD-\d{6}(?!\d)")
NUMBER = re.compile(r"(?<![\w.])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?\s*(?:%|percent\b)?")
SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
CHEM = re.compile(r"\b(?:retention|retain|retained|factor|fraction|nutrient|vitamin|ascorbic)\b", re.I)
COUNT = re.compile(r"\s*(?:independent\s+)?(?:rows?|sources?|steps?|papers?|studies|recipes?)\b", re.I)
UNIT = re.compile(r"\s*(?:°|degrees?|minutes?|mins?|hours?|seconds?|mg\b|ug\b|µg\b|grams?|g\b|ml\b|mol\b|kJ\b)", re.I)


def _sentences(text):
    out = []
    for fragment in SPLIT.split(text or ""):
        fragment = fragment.strip()
        if not fragment:
            continue
        if CIT.search(fragment) and not re.sub(r"[\[\](),;.\s]", "", CIT.sub("", fragment)) and out:
            out[-1] += " " + fragment
        else:
            out.append(fragment)
    return out


def _point(row):
    value = (row.get("derived") or {}).get("retention_factor") or {}
    if row.get("status") != "ACTIVE" or value.get("status") != "MEASURED":
        return None
    number = value.get("value")
    if type(number) not in (float, int):
        return None
    number = float(number) * (.01 if value.get("unit") == "%" else 1.)
    return number if math.isfinite(number) else None


def audit_text(text, evd, *, packet_ids, no_numbers=False):
    issues, gaps, counts = Counter(), Counter(), Counter()
    aligned = 0
    for sentence in _sentences(text):
        references = set(CIT.findall(sentence))
        issues["UNKNOWN_EVD_CITATION"] += sum(ref not in evd for ref in references)
        if packet_ids is not None:
            issues["CITATION_OUTSIDE_RECORDED_PACKET"] += len(references - packet_ids)
        clean = CIT.sub(lambda m: " " * len(m.group()), sentence)
        for match in NUMBER.finditer(clean):
            token = match.group().strip()
            suffix, prefix = clean[match.end():], clean[:match.start()]
            if COUNT.match(suffix):
                counts["METADATA_COUNT"] += 1
                continue
            if re.search(r"co-occurrence score\s*$", prefix, re.I):
                counts["CORPUS_PATTERN_SCORE"] += 1
                continue
            if UNIT.match(suffix):
                gaps["UNIT_BEARING_QUANTITY_NOT_CHECKED"] += 1
                continue
            percent = token.endswith("%") or token.lower().endswith("percent")
            if not percent and not CHEM.search(sentence):
                gaps["UNCLASSIFIED_NUMERIC_TOKEN"] += 1
                continue
            counts["CHEMISTRY_NUMERIC_TOKENS"] += 1
            raw = re.sub(r"\s*(?:%|percent)$", "", token, flags=re.I)
            value = float(raw) / (100 if percent else 1)
            if no_numbers:
                issues["NUMERIC_CLAIM_EXCEEDS_PRECISION_CAP"] += 1
            if not references:
                issues["UNCITED_CHEMISTRY_NUMBER"] += 1
            else:
                values = [_point(evd[r]) for r in references if r in evd]
                if any(v is not None and abs(v - value) <= .0050000001 for v in values):
                    aligned += 1
                else:
                    issues["VALUE_NOT_IN_CITED_POINT_EVIDENCE"] += 1
            if packet_ids is None:
                gaps["PACKET_PROVENANCE_UNRECORDED"] += 1
    return {"answer_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "issues": {k: v for k, v in sorted(issues.items()) if v},
            "gaps": dict(sorted(gaps.items())), "counts": dict(sorted(counts.items())),
            "aligned_retention_numbers": aligned, "semantic_entailment_verified": False}


def _unknown(value):
    if isinstance(value, dict):
        return value.get("status") == "UNKNOWN" or any(_unknown(v) for v in value.values())
    return isinstance(value, list) and any(_unknown(v) for v in value)


def audit_payload(value):
    issues = Counter()

    def visit(node):
        if isinstance(node, dict):
            basis = str(node.get("basis", node.get("layer_basis", ""))).upper()
            model_basis = any(x in basis for x in ("SCENARIO", "ASSUMED", "MODEL_DERIVED", "LAYER2", "L2:"))
            label = node.get("label", node.get("evidence_class"))
            if label == "evidence_supported" and model_basis:
                issues["MODEL_BASIS_LABELLED_EVIDENCE"] += 1
            if node.get("verdict") == "NOT_POSSIBLE" and model_basis:
                issues["NOT_POSSIBLE_FROM_LAYER2"] += 1
            if node.get("route") == "SIMULATE" and _unknown(node):
                issues["UNKNOWN_INPUT_TO_SIMULATE"] += 1
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
    visit(value)
    return dict(sorted(issues.items()))
