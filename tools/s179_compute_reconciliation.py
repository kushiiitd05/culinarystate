#!/usr/bin/env python3
"""Read-only historical run-hash reconciliation. Never invent old hashes or times."""
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()


def inspect(root,row):
    name=row.get('output_path','');expected=row.get('output_sha256','');current=None
    path=Path(name) if Path(name).is_absolute() else Path(root)/name
    try:
        if name and path.is_file():current=sha(path)
    except OSError:pass
    components={}
    if ';' in name:
        for component in name.split(';'):
            component=component.strip();candidate=Path(component) if Path(component).is_absolute() else Path(root)/component
            if candidate.is_file():components[component]=sha(candidate)
    ephemeral=any(token in name.lower() for token in ['scratchpad','stdout','(deleted)','not kept','no kept output','no output file']) or name.startswith('<')
    if not name:status='NO_OUTPUT_FILE_DECLARED'
    elif components:status='MULTIPLE_ARTIFACTS_CURRENT_COMPONENT_HASHES_ONLY'
    elif not current and ephemeral:status='DECLARED_STDOUT_OR_EPHEMERAL_OUTPUT'
    elif current and not expected:status='CURRENT_HASH_AVAILABLE_ORIGINAL_NOT_RECORDED'
    elif current==expected and current:status='CURRENT_BYTES_MATCH_RECORDED_HASH'
    elif current:status='CURRENT_BYTES_DIFFER_FROM_RECORDED_HASH'
    else:status='DECLARED_ARTIFACT_NOT_AVAILABLE_AT_RECORDED_PATH'
    return {'run_id':row['run_id'],'output_path':name,'recorded_sha256':expected or None,'current_sha256':current,
            'status':status,'component_sha256':components,'start_recorded':bool(row.get('start')),'end_recorded':bool(row.get('end'))}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out.exists():parser.error('Refusing overwrite')
    ledger=ROOT/'registry/compute_runs_v1.csv';rows=list(csv.DictReader(ledger.open(newline='')))
    results=[];started=datetime.now(timezone.utc).isoformat()
    for row in rows:
        r=inspect(ROOT,row)
        if r['output_path'] and r['recorded_sha256'] and r['status']!='CURRENT_BYTES_MATCH_RECORDED_HASH' and not Path(r['output_path']).is_absolute():
            history_path=r['output_path'].split(' (',1)[0]
            history=subprocess.run(['git','log','--all','--format=%H','--',history_path],cwd=ROOT,text=True,capture_output=True)
            r['git_history_examined']=0;r['recorded_bytes_found_in_git']=False
            for commit in history.stdout.splitlines()[:50]:
                blob=subprocess.run(['git','show',commit+':'+history_path],cwd=ROOT,capture_output=True)
                r['git_history_examined']+=1
                if blob.returncode==0 and hashlib.sha256(blob.stdout).hexdigest()==r['recorded_sha256']:
                    r['recorded_bytes_found_in_git']=True;r['matching_git_commit']=commit;break
        results.append(r)
    report={'record':'HISTORICAL_COMPUTE_RUN_RECONCILIATION','started_at_utc':started,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'ledger_sha256_at_audit':sha(ledger),'rows_in_snapshot':len(rows),'status_counts':dict(Counter(r['status'] for r in results)),
            'missing_start_timestamps':sum(not r['start_recorded'] for r in results),'missing_end_timestamps':sum(not r['end_recorded'] for r in results),
            'rows':results,'labels':['AI_PRECHECKED','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],'scientific_gate_pass':False,
            'tool_sha256':sha(__file__),'limitations':['Current hashes are never substituted for missing or different original hashes.',
                        'Missing historical times stay missing; commit dates/file modification times are not run timestamps.',
                        'Git history search is bounded to50commits perrelative artifact; absolute/remote/ignored data are not recovered from servers.',
                        'No raw historical blob or third-party source text is copied into new reports.',
                        'This ledger snapshot predates its own compute-log row and any later appended runs.']}
    with args.out.open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'rows':len(rows),'statuses':report['status_counts']}))


if __name__=='__main__':main()
