#!/usr/bin/env python3
"""Question-only AI branch Gold handoff; original Gold/router remain frozen."""
import argparse,csv,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from culinarystate.evaluation import d5_scoring as DS
LABELS=['AI_DELEGATED_D085','NOT_INDEPENDENT','NOT_HUMAN_VERIFIED_UNTIL_REVIEW','NO_HUMAN_SIGNOFF_D085','AI_ASSISTED_GOLD_NOT_INDEPENDENT']
BRANCHES={'METADATA','RELATIONSHIP','SEMANTIC','TRANSFORMATION','MULTIMODAL','SAFETY','UNKNOWN','MALFORMED'}
BENCH=['benchmark/d5/d5_benchmark_v1_D085_'+s+'.csv' for s in ['S','PC','UX']]
PRIVATE=Path('data/derived/prv_branch_review_2026-11-13')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,x):
    with open(p,'x') as f:f.write(json.dumps(x,indent=2,sort_keys=True)+'\n')
def blind_packet(rows):return [{'audit_id':f'PBR-{i:03d}','question':r.get('question',''),'gold_branch':'','reviewer_note':''} for i,r in enumerate(rows,1)]
def validate(issued,labels):
    ids=[x['audit_id'] for x in labels]
    if len(ids)!=len(set(ids)) or set(ids)!={r['audit_id'] for r in issued}:raise ValueError('Exact unique IDs required')
    by={x['audit_id']:x for x in labels}
    for r in issued:
        x=by[r['audit_id']]
        if x['question']!=r['question'] or x.get('gold_branch') not in BRANCHES or not x.get('reviewer_note'):raise ValueError('Invalid return')
def prepare():
    rows=DS.load_benchmark(BENCH)
    # Order is hash-based to hide block and qid; key is inaccessible to the judge.
    rows=sorted(rows,key=lambda r:hashlib.sha256(('prv-branch-20261113|'+r['qid']).encode()).hexdigest())
    packet=blind_packet(rows);PRIVATE.mkdir(parents=True,exist_ok=True)
    p=PRIVATE/'blind_branch_packet.csv'
    with open(p,'x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(packet[0]));w.writeheader();w.writerows(packet)
    key=PRIVATE/'key_SEALED.json';write(key,{p['audit_id']:r['qid'] for p,r in zip(packet,rows)})
    write('reports/s179/prv_branch_review_prelabel_2026-11-13.json',{'record':'PRV_BRANCH_GOLD_PRELABEL','created_at_utc':datetime.now(timezone.utc).isoformat(),'labels':LABELS,'n':len(packet),'inputs':{p:sha(p) for p in BENCH},'tool_sha256':sha(__file__),'packet':str(p),'packet_sha256':sha(p),'key_sha256':sha(key),'selection':'All74 frozen questions, hash-shuffled; no prior Gold/answer/route field supplied','judge':'Separate fresh context; no system branch outputs opened. Branch intent only, no answers, not independent Gold.','scoring':'After returned labels frozen, run unchanged local rule router on exact frozen question strings; full accuracy and per-branch confusion via existing d5_scoring. Original frozen Gold unchanged.'})
    print('Prepared',len(packet),'packet SHA',sha(p))
def finish(returned):
    m=json.loads(Path('reports/s179/prv_branch_review_prelabel_2026-11-13.json').read_text())
    p=Path(m['packet']);key=PRIVATE/'key_SEALED.json'
    assert sha(p)==m['packet_sha256'] and sha(key)==m['key_sha256']
    issued=read(p);labels=read(returned);validate(issued,labels);by={x['audit_id']:x for x in labels};k=json.loads(key.read_text())
    rows=DS.load_benchmark(BENCH)
    assert all(sha(p)==h for p,h in m['inputs'].items())
    new={k[id]:x['gold_branch'] for id,x in by.items()}
    supplemental=[{**r,'gold_branch':new[r['qid']]} for r in rows]
    pred=DS.live_router_branches(rows)
    result=DS.router_branch_accuracy(supplemental,pred)
    write('reports/s179/prv_branch_review_2026-11-13.json',{'record':'PRV_AI_BRANCH_GOLD_DIAGNOSTIC','completed_at_utc':datetime.now(timezone.utc).isoformat(),'labels':LABELS,'review_status':'AI_VERDICT_PENDING_HUMAN_REVIEW','prelabel_manifest_sha256':sha('reports/s179/prv_branch_review_prelabel_2026-11-13.json'),'returned_sha256':sha(returned),'router_source_sha256':sha('src/culinarystate/decision/query_router.py'),'result':result,'scientific_gate_pass':False,'limitations':['AI labels, not independent Gold or human verification.','Only question intent judged; no recipe context or system branch outputs supplied. Style/semantic clues remain.','Question-level accuracy/interval conditional on this existing benchmark and AI labels; no population generalization.','Live unchanged rule router evaluated, not LLM answer quality; original benchmark/Gold/scoring outputs not modified.']})
    print(json.dumps(result['accuracy']))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','finish']);ap.add_argument('--returned',type=Path);a=ap.parse_args()
    if a.mode=='prepare':prepare()
    elif a.returned:finish(a.returned)
    else:ap.error('--returned required')
