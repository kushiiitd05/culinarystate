"""Synthetic evidence controls for the read-only review audit."""
import importlib.util
from pathlib import Path
from zipfile import ZipFile

import pytest

SPEC = importlib.util.spec_from_file_location("takeover_review", Path(__file__).resolve().parents[2] / "tools/review_takeover.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def test_xlsx_reader_keeps_sparse_cells_and_decodes_shared_strings(tmp_path):
    p = tmp_path / "source.xlsx"
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    with ZipFile(p, "w") as z:
        z.writestr("xl/sharedStrings.xml", f'<sst {ns}><si><t>ID</t></si><si><t>Class taste</t></si><si><t>Bitterness</t></si></sst>')
        z.writestr("xl/worksheets/sheet1.xml", f'''<worksheet {ns}><sheetData>
          <row><c r="A1" t="s"><v>0</v></c><c r="C1" t="s"><v>1</v></c></row>
          <row><c r="A2" t="inlineStr"><is><t>CT1</t></is></c><c r="C2" t="s"><v>2</v></c></row>
          </sheetData></worksheet>''')
    assert audit.read_source_sheet(p) == [{"ID": "CT1", "Class taste": "Bitterness"}]


def fixture_records():
    def edge(eid, version, status, label):
        return {"id": eid, "version": version, "status": status, "predicate": "MOL_HAS_TASTE",
                "subject_id": "MOL-000001", "object_value": label,
                "provenance": {"agent": "chemtastesdb@0.1", "locator": "ChemTastesDB ID CT1 (fixture); refs test"}}
    return [edge("OLD", 1, "ACTIVE", "very bitter"), edge("OLD", 2, "DEPRECATED", "very bitter"),
            edge("NEW", 1, "ACTIVE", "Bitterness")]


def test_source_backed_replacement_requires_all_three_identity_label_checks():
    source = [{"ID": "CT1", "PubChem CID": "10", "Taste": "very bitter", "Class taste": "Bitterness"}]
    result = audit.audit_taste_migrations(fixture_records(), source, {"MOL-000001": {"pubchem_cid": 10}})
    assert result["fully_explained"] == 1 and result["deprecated"] == 1
    assert result["pairs"][0]["source_class_match"] is True
    source[0]["Class taste"] = "Sweetness"
    result = audit.audit_taste_migrations(fixture_records(), source, {"MOL-000001": {"pubchem_cid": 10}})
    assert result["fully_explained"] == 0


def test_missing_replacement_is_unresolved_not_inferred():
    result = audit.audit_taste_migrations(fixture_records()[:2], [], {})
    assert result["fully_explained"] == 0
    assert result["pairs"][0]["replacement_count"] == 0


def test_conflicting_equal_versions_cannot_be_hidden_by_file_order():
    rows = fixture_records()
    rows.append({**rows[0], "object_value": "contradiction"})
    with pytest.raises(ValueError, match="conflicting"):
        audit.latest_records(rows)


def test_reproduction_never_overwrites_a_completed_human_review(tmp_path):
    p = tmp_path / "review.csv"
    p.write_text("source_node_id,human_verdict,human_reviewer,human_notes\n1,ACCEPT,Reviewer,checked\n")
    before = p.read_bytes()
    with pytest.raises(ValueError, match="human"):
        audit.write_review_csv(p, [{"source_node_id": "1", "human_verdict": "", "human_reviewer": "", "human_notes": ""}])
    assert p.read_bytes() == before
