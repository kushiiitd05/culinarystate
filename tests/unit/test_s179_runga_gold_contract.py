import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('runga_gold',Path(__file__).parents[2]/'tools/s179_runga_gold_contract.py')
tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)


def test_generic_action_cannot_be_promoted_into_a_gold_transformation_label():
    assert tool.gold_kind('ACTION') is None
    assert tool.gold_kind('UNSPECIFIED') is None
    assert tool.gold_kind('TRANSFORM')=='Transform'
    assert tool.gold_kind('MERGE')=='Merge'
