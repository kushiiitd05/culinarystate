"""Controls for a supplemental blinded AI review, not scientific scorer changes."""
import importlib.util
from pathlib import Path
import pytest
P=Path(__file__).resolve().parents[2]/'tools/s179_prv_claim_review.py'
spec=importlib.util.spec_from_file_location('prv_claim_review',P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_agreement_excludes_unclear_and_reports_mismatch():
    key=[{'audit_id':'a','checker_flags_answer':'True','rung':'B7'},
         {'audit_id':'b','checker_flags_answer':'False','rung':'B2'},
         {'audit_id':'c','checker_flags_answer':'False','rung':'B2'}]
    labels=[{'audit_id':'a','claim_supported_by_cited_row':'NO','cited_row_matches_question':'RIGHT_CELL'},
            {'audit_id':'b','claim_supported_by_cited_row':'NO','cited_row_matches_question':'RIGHT_CELL'},
            {'audit_id':'c','claim_supported_by_cited_row':'CANNOT_TELL','cited_row_matches_question':'SIMILAR'}]
    x=m.agreement(key,labels)
    assert (x['agreed'],x['judged'],x['unclear'])==(1,2,1)
    assert x['agreement']==.5

def test_review_requires_exact_complete_unique_ids():
    with pytest.raises(ValueError):m.agreement([{'audit_id':'a'}],[])
    with pytest.raises(ValueError):m.agreement([{'audit_id':'a'}],[{'audit_id':'a'},{'audit_id':'a'}])

def test_blind_columns_exclude_rung_checker_qid():
    assert not {'rung','qid','checker_flags_answer','independent_verdict','stratum'} & set(m.BLIND_COLUMNS)

def test_judgment_cannot_change_issued_fields():
    a={'audit_id':'a','question':'original','answer_sentence':'x','claim_text':'x','claim_kind':'NUMERIC','cited_rows':'z'}
    with pytest.raises(ValueError):m.validate_return([a],[{**a,'question':'changed'}])
