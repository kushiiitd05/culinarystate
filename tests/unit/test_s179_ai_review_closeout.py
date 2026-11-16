"""AI-persona comparison cannot grant an independent-human gate."""
import importlib.util
from pathlib import Path
import pytest
s=importlib.util.spec_from_file_location('closeout',Path(__file__).resolve().parents[2]/'tools/s179_ai_review_closeout.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_even_numeric_rule_pass_never_becomes_human_pass():
    rows=[{'audit_id':'x','raw':'a','duration_judgement':''}]
    a=[{'audit_id':'x','raw':'a','duration_judgement':'CORRECT'}]
    x=m.paired(rows,a,a,scorer=lambda *a:{'gate':'PASS','pooled_ac1':1.0})
    assert x['gate']=='NOT_COUNTED' and x['reason']=='AI_PERSONAS_NOT_INTER_RATER'
    assert 'gate' not in x['diagnostic_statistics'] and not x['counts_as_human_gate']

def test_duplicate_ids_and_changed_issued_content_refused():
    rows=[{'audit_id':'x','raw':'a'}]
    with pytest.raises(ValueError):m.paired(rows,rows+rows,rows)
    with pytest.raises(ValueError):m.paired(rows,[{'audit_id':'x','raw':'changed'}],rows)

def test_difference_queue_preserves_unresolved_code_pair():
    a=[{'audit_id':'x','duration_judgement':'CORRECT'}]
    b=[{'audit_id':'x','duration_judgement':'N/A'}]
    x=m.differences(a,b)
    assert x==[{'audit_id':'x','field':'duration_judgement','ksh_code':'CORRECT','prv_code':'N/A','status':'UNRESOLVED_ORIGINAL_LABELS_PRESERVED'}]
