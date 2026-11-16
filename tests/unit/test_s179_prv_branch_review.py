"""Blinded branch-Gold handoff controls; no router modifications."""
import importlib.util
from pathlib import Path
import pytest
s=importlib.util.spec_from_file_location('br',Path(__file__).resolve().parents[2]/'tools/s179_prv_branch_review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def test_return_requires_unchanged_question_and_exact_ids():
    issued=[{'audit_id':'a','question':'Q'}]
    with pytest.raises(ValueError):m.validate(issued,[])
    with pytest.raises(ValueError):m.validate(issued,[{'audit_id':'a','question':'changed','gold_branch':'UNKNOWN','reviewer_note':'x'}])
    m.validate(issued,[{'audit_id':'a','question':'Q','gold_branch':'UNKNOWN','reviewer_note':'unclear intent'}])
def test_question_only_packet_excludes_gold_outputs():
    r=m.blind_packet([{'qid':'secret','question':'Q','gold_branch':'SAFETY','answer':'system output'}])
    assert r==[{'audit_id':'PBR-001','question':'Q','gold_branch':'','reviewer_note':''}]
