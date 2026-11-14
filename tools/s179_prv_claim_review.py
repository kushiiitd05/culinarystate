#!/usr/bin/env python3
"""Supplemental D-099 AI claim review; no frozen scorer or result is changed."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from culinarystate.evaluation import d5_scoring as DS,claim_audit as CA
BLIND_COLUMNS=('audit_id','question','answer_sentence','claim_text','claim_kind','cited_rows')
LABELS=['AI_DELEGATED_D085','NOT_INDEPENDENT','NOT_HUMAN_VERIFIED_UNTIL_REVIEW','NO_HUMAN_SIGNOFF_D085','AI_JUDGE_NOT_HUMAN']
SEED='s179-prv-d099-20261113'
BENCH=['benchmark/d5/d5_benchmark_v1_D085_'+s+'.csv' for s in ['S','PC','UX']]
RUNS='reports/del5/d5_runs_v1_D085.jsonl'
PRIVATE=Path('data/derived/prv_claim_review_2026-11-13')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_csv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_json(p,x):
    with open(p,'x') as f:f.write(json.dumps(x,indent=2,sort_keys=True)+'\n')
def validate_return(issued,returned):
    ids=[r['audit_id'] for r in returned]
    if len(ids)!=len(set(ids)) or set(ids)!={r['audit_id'] for r in issued}:raise ValueError('Return must cover exact unique issued IDs')
    by={r['audit_id']:r for r in returned}
    for r in issued:
        if any(by[r['audit_id']].get(k)!=r.get(k) for k in BLIND_COLUMNS):raise ValueError('Issued content changed')
def interval(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h) if k else 0,min(1,c+h) if k<n else 1]
def agreement(key,labels):
    ids=[r['audit_id'] for r in labels]
    if len(ids)!=len(set(ids)) or set(ids)!={r['audit_id'] for r in key}:raise ValueError('Exact unique IDs required')
    by={r['audit_id']:r for r in labels};n=k=unclear=0;conf={};byrung={}
    for r in key:
        label=by[r['audit_id']];s=label.get('claim_supported_by_cited_row','');m=label.get('cited_row_matches_question','')
        if s not in CA.SUPPORTED_CODES or m not in CA.MATCH_CODES:raise ValueError('Invalid judgment code')
        gold=CA.human_unsupported(s,m)
        if gold is None:unclear+=1;continue
        flag=str(r['checker_flags_answer']).lower()=='true';n+=1;k+=gold==flag
        cell=f"AI_{'UNSUPPORTED' if gold else 'SUPPORTED'}|CHECKER_{'FLAGGED' if flag else 'CLEAN'}"
        conf[cell]=conf.get(cell,0)+1
        rg=byrung.setdefault(r['rung'],{'agreed':0,'judged':0});rg['judged']+=1;rg['agreed']+=gold==flag
    return {'agreed':k,'judged':n,'unclear':unclear,'agreement':k/n if n else None,'wilson95':interval(k,n),'confusion':conf,'by_rung_after_unblinding':byrung}

def prepare():
    if '### D-099 ' not in Path('DECISIONS.md').read_text():raise ValueError('Commit D-099 before preparation')
    rows=DS.load_benchmark(BENCH);records=DS.load_runs(RUNS);evd=DS.load_evd('ledgers/data/EVD.jsonl')
    relatives=json.loads(Path('benchmark/d5/d5_relatives_v1_D085.json').read_text())
    scored=DS.score_all(rows,records,evd,relatives)
    smp=DS.audit_sample(rows,records,scored,per_rung=10,seed=SEED,rungs=('B2','B5T','B7'))
    if len(smp['sample'])<30:raise ValueError('Predeclared >=30 not available')
    result=CA.write_audit_files(smp['sample'],evd,PRIVATE,seed=SEED,reviewers=('prv_AI',))
    # Supplement cited displays with only the cited ledger rows, never checker/rung metadata.
    packet=PRIVATE/'claim_audit_sheet_prv_AI.csv';issued=read_csv(packet)
    for r in issued:
        import re
        ids=re.findall(r'EVD-\d{6}',r['cited_rows'])
        r['cited_rows']='\n'.join(json.dumps(evd.get(i,{'id':i,'status':'NOT_IN_LEDGER'}),sort_keys=True) for i in dict.fromkeys(ids))
    # Initial generated sheet was not committed or issued; final enriched sheet uses a new path.
    enriched=PRIVATE/'blind_claim_packet_prv_AI.csv'
    with open(enriched,'x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=CA.SHEET_COLS);w.writeheader();w.writerows(issued)
    inputs={p:sha(p) for p in [*BENCH,RUNS,'ledgers/data/EVD.jsonl','benchmark/d5/d5_relatives_v1_D085.json','tools/s179_prv_claim_review.py']}
    out={'record':'D099_AI_CLAIM_REVIEW_PRELABEL_MANIFEST','created_at_utc':datetime.now(timezone.utc).isoformat(),'decision':'D-099','seed':SEED,'n':len(issued),'design':smp['design'],'shortfalls':smp['shortfalls'],'packet':str(enriched),'packet_sha256':sha(enriched),'key_sha256':sha(PRIVATE/'claim_audit_key_SEALED.csv'),'input_sha256':inputs,'labels':LABELS,'selection':'Existing stratified audit sampler:10 each B2/B5T/B7; deterministic seed; scorer strata deliberately enriched, not simple population random sample','blinding':'Reviewer gets only six blind content columns plus empty judgment fields. Preparing root has seen system outputs; judging fresh agent must not open key/checker/results.'}
    write_json('reports/s179/prv_claim_review_prelabel_2026-11-13.json',out)
    print(json.dumps({'n':len(issued),'packet_sha256':out['packet_sha256']}))
def finish(path):
    manifest=json.loads(Path('reports/s179/prv_claim_review_prelabel_2026-11-13.json').read_text())
    packet=Path(manifest['packet'])
    if sha(packet)!=manifest['packet_sha256']:raise ValueError('Issued packet hash mismatch')
    issued=read_csv(packet);labels=read_csv(path);validate_return(issued,labels)
    key=read_csv(PRIVATE/'claim_audit_key_SEALED.csv')
    if sha(PRIVATE/'claim_audit_key_SEALED.csv')!=manifest['key_sha256']:raise ValueError('Key hash mismatch')
    x={'record':'D099_AI_BLIND_CLAIM_REVIEW','completed_at_utc':datetime.now(timezone.utc).isoformat(),'labels':LABELS,'review_status':'AI_VERDICT_PENDING_HUMAN_REVIEW','n_sampled':len(issued),'prelabel_manifest_sha256':sha('reports/s179/prv_claim_review_prelabel_2026-11-13.json'),'returned_sha256':sha(path),'agreement':agreement(key,labels),'scientific_gate_pass':False,'limitations':['Single fresh AI judge, not independent human review; H1/H3 frozen verdicts unchanged.','Existing automatic claim extractor defines universe; omitted claims/recall not audited.','Strata deliberately enriched; simple agreement is sample-descriptive, not population-weighted accuracy.','Checker flag is answer-level, compared to individual claim judgment; correlated claims and AI systematic bias not captured by Wilson interval.','Evidence consistency review does not verify imported source measurements, applicability or full narrative entailment.','Reviewer cannot be guaranteed blind to style clues in the answer text. Root preparer was exposed to system outputs; judge is a separate fresh-context agent.']}
    write_json('reports/s179/prv_claim_review_2026-11-13.json',x);print(json.dumps(x['agreement']))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','finish']);ap.add_argument('--returned',type=Path);a=ap.parse_args()
    if a.mode=='prepare':prepare()
    elif a.returned:finish(a.returned)
    else:ap.error('--returned required')
if __name__=='__main__':main()
