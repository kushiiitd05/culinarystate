#!/usr/bin/env python3
"""Eight authored backend demonstration scenarios, not a human rehearsal/benchmark."""
import argparse,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tools'))
from s179_strict_runtime_audit_v3 import inspect_payload
CASES=[
 {'id':'DEMO-SAFETY','query':'Is chicken safe after two days on the counter?','expected_branch':'SAFETY'},
 {'id':'DEMO-UNKNOWN','query':'What should I do?','expected_branch':'UNKNOWN'},
 {'id':'DEMO-VISION','query':'Look at this photo and identify the dish.','expected_branch':'MULTIMODAL'},
 {'id':'DEMO-METADATA','query':'How many calories are in carrots?','expected_branch':'METADATA'},
 {'id':'DEMO-RECIPE-SEARCH','query':'Find me recipes similar to tomato soup.','expected_branch':'SEMANTIC'},
 {'id':'DEMO-SUBSTITUTION','query':'What can I substitute for butter?','expected_branch':'RELATIONSHIP'},
 {'id':'DEMO-RETENTION','query':'How much vitamin C remains in carrots after boiling?','expected_branch':'TRANSFORMATION'},
 {'id':'DEMO-PHYSICS','query':'How much vitamin C remains in carrots after boiling?','recipe_text':'Boil carrots in water at 90 C for 5 minutes.','expected_branch':'TRANSFORMATION'}]
def assess(case,payload):
    counts=inspect_payload(payload);issues=[]
    if (payload.get('route') or {}).get('branch',payload.get('branch'))!=case['expected_branch']:issues.append('BRANCH_MISMATCH')
    if counts['handler_errors']:issues.append('HANDLER_ERROR')
    if counts['citability_violations']:issues.append('CITABILITY_ERROR')
    if counts['display_provenance_violations'] or counts['missing_numeric_provenance'] or counts['unknown_numeric_fields']:issues.append('NUMERIC_PROVENANCE_ERROR')
    if counts['unexpected_simulate'] or counts['table_numbers']:issues.append('UNAUTHORIZED_DEFAULT_NUMERIC_RETENTION')
    return issues

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():ap.error('Refusing overwrite')
    from culinarystate.decision.demo_context_v3 import StrictDemoContext
    start=datetime.now(timezone.utc).isoformat();ctx=StrictDemoContext.load(public=True,host='127.0.0.1');rows=[]
    for c in CASES:
        p=ctx.respond(c['query'],recipe_text=c.get('recipe_text'));issues=assess(c,p)
        rows.append({**c,'branch':(p.get('route') or {}).get('branch',p.get('branch')),'mode':p.get('mode'),'checks':inspect_payload(p),'issues':issues,'answer':p.get('answer'),'status':'PASS' if not issues else 'FAIL'})
    files=['tools/s179_submission_demo.py','src/culinarystate/decision/demo_context_v3.py','src/culinarystate/generation/strict_v3.py','src/culinarystate/decision/strict_display_v3.py']
    report={'record':'EIGHT_AUTHORED_BACKEND_DEMO_CASES','started_at_utc':start,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'labels':['ENGINEERING_DIAGNOSTIC','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],'scientific_gate_pass':False,'actual_human_rehearsal':False,'case_origin':'SYNTHETIC_AUTHORED_DEMONSTRATION','records':rows,'passed':sum(r['status']=='PASS' for r in rows),'total':len(rows),'code_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},'limitations':['Backend smoke cases only; prior four-case real-browser screenshot is separate evidence.','METADATA/SEMANTIC/MULTIMODAL may honestly abstain; no missing handler represented as implemented capability.','No model inference/hosting or simulation validation; authored examples are not benchmark performance.']}
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'passed':report['passed'],'total':len(rows),'branches':[(r['id'],r['branch'],r['mode'],r['issues']) for r in rows]}))
    return 0 if report['passed']==len(rows) else 1
if __name__=='__main__':raise SystemExit(main())
