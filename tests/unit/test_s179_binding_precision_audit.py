"""Prehash selection, label completeness and Wilson reporting controls."""
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('binding_precision',Path(__file__).parents[2]/'tools/s179_binding_precision_audit.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_selection_is_order_independent_and_stratified():
    rows=[{'recipe_id':f'R{i}','event_id':'E1','family':family} for family in ['DRY','WET'] for i in range(6)]
    first=audit.select(rows,'20261104',6)
    assert first==audit.select(list(reversed(rows)),'20261104',6)
    assert [r['family'] for r in first].count('DRY')==3


def test_wilson_uses_actual_adjudicated_denominator_and_handles_empty():
    assert audit.wilson(0,0)==[None,None]
    low,high=audit.wilson(10,10)
    assert .72<low<.73 and high==1.


def test_review_requires_each_selected_case_once_and_valid_field_codes():
    import pytest
    manifest={'selected':[{'case_id':'A'},{'case_id':'B'}]}
    fields=audit.REVIEW_FIELDS
    labels=[{'case_id':case,'fields':{field:'MATCH' for field in fields}} for case in ['A','B']]
    assert audit.review_summary(manifest,labels)['event_attribution']['matches']==2
    with pytest.raises(ValueError):audit.review_summary(manifest,labels[:1])
    labels[0]['fields']['temperature']='UNKNOWN_GUESS'
    with pytest.raises(ValueError):audit.review_summary(manifest,labels)
