"""Candidate demonstration checks reject handler errors and missing provenance."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('demo',Path(__file__).resolve().parents[2]/'tools/s179_submission_demo.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def test_handler_error_is_not_demo_success():
    p={'branch':'SAFETY','mode':'ABSTAIN_ERROR','citable':False,'labels':['NON_CITABLE'],'detail':{}}
    assert 'HANDLER_ERROR' in m.assess({'expected_branch':'SAFETY'},p)
def test_wrong_branch_rejected_even_if_safe():
    p={'branch':'UNKNOWN','mode':'ASK','citable':False,'labels':['NON_CITABLE'],'detail':{}}
    assert 'BRANCH_MISMATCH' in m.assess({'expected_branch':'SAFETY'},p)
def test_invented_numeric_display_rejected():
    p={'branch':'TRANSFORMATION','mode':'ASK','citable':False,'labels':['NON_CITABLE'],'detail':{'recipe_display':{'steps':[{'physics':{'numbers':[{'value':0}]}}]}}}
    assert 'NUMERIC_PROVENANCE_ERROR' in m.assess({'expected_branch':'TRANSFORMATION'},p)
def test_uses_actual_front_door_route_envelope():
    p={'route':{'branch':'SAFETY'},'mode':'ABSTAIN_SAFETY','citable':False,'labels':['NON_CITABLE'],'detail':{}}
    assert m.assess({'expected_branch':'SAFETY'},p)==[]
