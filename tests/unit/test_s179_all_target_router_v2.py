import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('target_v2',Path(__file__).parents[2]/'tools/s179_all_target_router_v2.py')
tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)


def test_partition_keeps_every_source_hit_and_presence_screen_separate():
    class Index:
        _by_key={('I','P'):({'svar_id':'A'},),('other','P'):({'svar_id':'B'},)}
    class Screen:
        def screened(self,target):return target=='C'
    class Gates:screen=Screen()
    specific,generic=tool.partition_targets(['A','B','C','D'],{('I','P')},Index(),Gates())
    assert specific==['A','C'] and generic==['B','D']


def test_metric_equivalence_does_not_confuse_target_specific_ids_with_counts():
    a={'target_svar':'A','items':[{'route':'UNKNOWN','reasons':['GAP'],'event_id':'EA'}]}
    b={'target_svar':'B','items':[{'route':'UNKNOWN','reasons':['GAP'],'event_id':'EB'}]}
    assert tool.measure(a)==tool.measure(b)
    b['items'][0]['route']='DIRECT'
    assert tool.measure(a)!=tool.measure(b)
