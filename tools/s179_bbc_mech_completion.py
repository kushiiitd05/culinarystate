#!/usr/bin/env python3
"""Local-only BBC physical-record reconstruction and mechanism-screen completion.

Runs existing frozen producers at new paths; raw per-event records remain ignored.
No parameter calibration, new source verification or scientific pass is supplied.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out_dir.exists():parser.error('New output directory required')
    args.out_dir.mkdir(parents=True)
    raw=Path('data/derived')/args.out_dir.name
    if raw.exists():parser.error('New ignored records directory required')
    raw.mkdir(parents=True)
    if subprocess.run(['git','check-ignore','-q','--',str(raw/'probe.jsonl')],cwd=ROOT).returncode:
        parser.error('Per-event directory must be ignored')
    started=datetime.now(timezone.utc).isoformat();jobs=[]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/**/*.py')}
    def run(name,tail,expected):
        command=[sys.executable]+tail;stamp=datetime.now(timezone.utc).isoformat();t0=time.monotonic()
        done=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
        rec={'name':name,'command':command,'started_at_utc':stamp,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
             'seconds':time.monotonic()-t0,'exit_code':done.returncode,'stdout_sha256':hashlib.sha256(done.stdout.encode()).hexdigest(),
             'stderr_sha256':hashlib.sha256(done.stderr.encode()).hexdigest(),'output_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in expected if p.is_file()}}
        jobs.append(rec);print(name,'exit',done.returncode,flush=True)
        if done.returncode:raise RuntimeError(name+' failed; retain output and review')
    error=None
    try:
        l1=args.out_dir/'binding.json'
        run('BBC_L1',['tools/binding_census.py','--seed','20261104','--sample-size','612782','--workers','2','--families','A1_BBC_GOOD_FOOD','--out',str(l1),'--records-dir',str(raw/'L1')],[l1])
        l2=args.out_dir/'scenario.json'
        run('BBC_L2',['tools/scenario_layer_run.py','--l1',str(raw/'L1'),'--l2',str(raw/'L2'),'--out',str(l2),'--workers','2','--tag','local_2026-11-13'],[l2])
        nh1,nh2=args.out_dir/'nonheat_l1.json',args.out_dir/'nonheat_l2.json'
        run('BBC_NONHEAT',['tools/nonheat_layer_run.py','--seed','20261104','--sample-size','612782','--workers','2','--families','A1_BBC_GOOD_FOOD','--l1-out',str(nh1),'--l2-out',str(nh2),'--l1-records-dir',str(raw/'NH_L1'),'--l2-records-dir',str(raw/'NH_L2')],[nh1,nh2])
        screen=args.out_dir/'mechanism_screen.json';timing=args.out_dir/'mechanism_screen_timing.json'
        run('BBC_MECH_SCREEN',['tools/s178_mech_screen_run.py','--seed','20261104','--sample-size','612782','--workers','2','--families','A1_BBC_GOOD_FOOD','--l1',str(raw/'L1'),'--l2',str(raw/'L2'),'--nh-l1',str(raw/'NH_L1'),'--nh-l2',str(raw/'NH_L2'),'--tag','BBC_local_2026-11-13','--out',str(screen),'--rows-dir',str(raw/'screen'),'--timing-out',str(timing)],[screen,timing])
    except Exception as exc:error=type(exc).__name__
    stable=hashes=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in hashes}
    stable=stable and head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report={'record':'LOCAL_BBC_MECHANISM_COMPLETION','started_at_utc':started,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'base_commit':head,'source_sha256':hashes,'source_and_commit_unchanged':stable,'jobs':jobs,'error_class':error,
            'status':'DONE_ENGINEERING' if error is None and stable else 'FAILED_REVIEW_REQUIRED',
            'labels':['ENGINEERING_DIAGNOSTIC','SOURCE_UNVERIFIED_AGENT_RECALLED','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],
            'scientific_gate_pass':False,'raw_records_directory':str(raw),
            'limitations':['BBC work ran locally under D003; no raw source/per-event records are committed.',
                           'Existing L2 scenario defaults and MECH windows remain unverified; no scientific direction/magnitude certification.',
                           'No source, calibrated PARAM, eligibility guard, frozen result or original producer is changed.']}
    with (args.out_dir/'completion.json').open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    if error or not stable:raise SystemExit(1)


if __name__=='__main__':main()
