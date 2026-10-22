"""Step 07H: source dialect (D3) stays in registries; unverified USDA abbreviations are never promoted or expanded; semantic layers know no source names."""
import csv
from pathlib import Path

from culinarystate.evidence import condition_normalizer as N
from culinarystate.evidence import source_dialect as D

ROOT = Path(__file__).resolve().parents[2]
USDA = ["CKD", "BLD", "BKD", "DRND", "DRAIND", "FRIED", "BRLD", "STMD", "BKD/SIMMRD", "+"]


def test_usda_abbreviations_unverified_and_unexpanded():
    rows = {r["raw_pattern"]: r for r in D.MAPPINGS if r["field"] == "source_abbreviation"}
    for a in USDA:
        assert rows[a]["status"] == "UNVERIFIED" and rows[a]["canonical_target"] == ""


def test_no_unverified_mapping_ever_marked_verified_or_with_target():
    for r in D.MAPPINGS:
        if r["status"] in ("UNVERIFIED", "DEPRECATED"):
            assert r["canonical_target"] == "" or r["field"] != "source_abbreviation"
    assert all(r["status"] in D.STATUSES for r in D.MAPPINGS)


def test_semantic_and_parser_code_have_no_source_names():
    for n in ("condition_parser.py", "condition_units.py"):
        src = (ROOT / "src/culinarystate/evidence" / n).read_text()
        for tok in ("USDA", "BOGNAR", "PHENOL", "CKD", "BKD", "BLD"):
            assert tok not in src, (n, tok)
    core = (ROOT / "src/culinarystate/evidence/condition_normalizer.py").read_text()
    import re
    assert not re.search(r"if source\b|source_family ==|== ['\"](?:USDA|BOGNAR|PHENOL)", core)
    assert "CKD" not in core and "BOGNAR" not in core and "PHENOL" not in core


def test_annotation_only_does_not_change_status():
    q = {"status": "MEASURED", "value": 25, "unit": "min", "raw": "ALC BEV,STIRRED,BKD 25 MIN"}
    plain, annotated = N.from_qvalue("time_duration", q), N.from_qvalue("time_duration", q, source_family="USDA-RETN-R6")
    assert annotated.get("dialect_notes") and annotated["dialect_notes"][0]["status"] == "UNVERIFIED" and annotated["dialect_notes"][0]["canonical_target"] is None
    assert {k: v for k, v in annotated.items() if k != "dialect_notes"} == plain


def test_mapping_registry_schema_and_lookup_specificity():
    cols = next(csv.reader(open(ROOT / "registry/source_dialect_mapping_registry_v1.csv")))
    assert cols == ["mapping_id", "source_family", "field", "raw_pattern", "canonical_target", "status", "evidence", "verified_by", "version"]
    assert D.lookup("retention_type", "RETENTION_TR_OR_AR", "USDA-RETN-R6")["canonical_target"] == "RT-004"
    assert D.lookup("retention_type", "RETENTION_TR_OR_AR", "OTHER-SRC") is None
    assert N.classify_retention_type("PHENOL-EXPLORER-3.6", "X", True)["status"] == N.AMBIGUOUS


def test_bounds_hard_and_plausibility_are_separate_columns():
    rows = {r["variable"]: r for r in csv.DictReader(open(ROOT / "registry/condition_variable_bounds_registry_v1.csv"))}
    assert rows["ph"]["hard_min"] == "" and rows["ph"]["plaus_min"] == "0" and rows["water_activity"]["hard_max"] == "1"
    assert N.normalize_value("ph", value=16, unit="pH")["status"] == N.AMBIGUOUS
    assert N.normalize_value("water_activity", value=1.01, unit="aw")["status"] == N.INVALID
    assert N.normalize_value("temp_medium", value=2000, unit="degC")["status"] == N.AMBIGUOUS
    assert N.normalize_value("temp_medium", value=-300, unit="degC")["status"] == N.INVALID
