import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('cell_audit',Path(__file__).parents[2]/'tools/s179_cell_definition_audit.py')
tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)


def row(i,duration=None):
    return {'id':f'EVD-{i:06d}','status':'ACTIVE','source_family_id':'SYNTHETIC',
            'matrix':{'raw_name':'synthetic food'},'process':{'steps':['boil'],'condition_id':duration},
            'target':{'raw_name':'synthetic target'}}


def test_cell_counts_and_hash_are_order_independent_but_condition_sensitive():
    a,b=row(1),row(2)
    first=tool.audit([a,b],{})
    assert first==tool.audit([b,a],{})
    assert first['SYNTHETIC']['canonical_cells']==1
    b['process']['condition_id']='C'
    changed=tool.audit([a,b],{'C':{'duration':{'status':'MEASURED','value':5,'unit':'min'}}})
    assert changed['SYNTHETIC']['canonical_cells']==2
    assert changed['SYNTHETIC']['cell_assignment_sha256']!=first['SYNTHETIC']['cell_assignment_sha256']
