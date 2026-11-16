import importlib.util
from pathlib import Path
import hashlib
spec=importlib.util.spec_from_file_location('compute_reconcile',Path(__file__).parents[2]/'tools/s179_compute_reconciliation.py')
tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)


def test_a_new_hash_cannot_replace_the_recorded_run_hash(tmp_path):
    p=tmp_path/'result.json';p.write_text('{}')
    row={'run_id':'TEST','output_path':'result.json','output_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    assert tool.inspect(tmp_path,row)['status']=='CURRENT_BYTES_MATCH_RECORDED_HASH'
    p.write_text('{"changed":true}')
    assert tool.inspect(tmp_path,row)['status']=='CURRENT_BYTES_DIFFER_FROM_RECORDED_HASH'


def test_missing_original_hash_is_explicit_even_when_current_file_exists(tmp_path):
    (tmp_path/'result.json').write_text('{}')
    row={'run_id':'TEST','output_path':'result.json','output_sha256':''}
    assert tool.inspect(tmp_path,row)['status']=='CURRENT_HASH_AVAILABLE_ORIGINAL_NOT_RECORDED'
    row['output_path']=''
    assert tool.inspect(tmp_path,row)['status']=='NO_OUTPUT_FILE_DECLARED'


def test_stdout_declarations_and_multi_file_outputs_are_not_claimed_as_missing_files(tmp_path):
    row={'run_id':'TEST','output_path':'no output file (pytest stdout)','output_sha256':''}
    assert tool.inspect(tmp_path,row)['status']=='DECLARED_STDOUT_OR_EPHEMERAL_OUTPUT'
    (tmp_path/'a.json').write_text('{}');(tmp_path/'b.json').write_text('[]')
    row['output_path']='a.json; b.json'
    result=tool.inspect(tmp_path,row)
    assert result['status']=='MULTIPLE_ARTIFACTS_CURRENT_COMPONENT_HASHES_ONLY'
    assert len(result['component_sha256'])==2
