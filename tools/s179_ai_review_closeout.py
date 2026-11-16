#!/usr/bin/env python3
"""Supplemental AI-persona comparisons. Never grants a scientific/human gate."""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from culinarystate.evidence import condition_agreement as CA
LABELS=['AI_DELEGATED_D085','NOT_INDEPENDENT','NOT_HUMAN_VERIFIED_UNTIL_REVIEW','NO_HUMAN_SIGNOFF_D085']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def unique(rows,key):
    ids=[r[key] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate IDs')
    return {r[key]:r for r in rows}
def check_issued(issued,returned):
    I,R=unique(issued,'audit_id'),unique(returned,'audit_id')
    if set(I)!=set(R):raise ValueError('Exact issued IDs required')
    for i,r in I.items():
        if any(R[i].get(k)!=v for k,v in r.items() if k not in CA.JUDGEMENT_COLS):raise ValueError('Issued content changed')
def differences(a,b):
    A,B=unique(a,'audit_id'),unique(b,'audit_id')
    if set(A)!=set(B):raise ValueError('ID mismatch')
    return [{'audit_id':i,'field':f,'ksh_code':A[i].get(f),'prv_code':B[i].get(f),'status':'UNRESOLVED_ORIGINAL_LABELS_PRESERVED'}
            for i in sorted(A) for f in (*CA.FIELDS,'overall_judgement') if A[i].get(f)!=B[i].get(f)]
def paired(issued,a,b,*,scorer=CA.score):
    check_issued(issued,a);check_issued(issued,b)
    raw=dict(scorer(issued,a,b));raw.pop('gate',None)
    raw.pop('counts_as_human_gate',None)
    return {'gate':'NOT_COUNTED','reason':'AI_PERSONAS_NOT_INTER_RATER','counts_as_human_gate':False,
            'diagnostic_statistics':raw,'disagreement_cells':differences(a,b),'scientific_gate_pass':False}
def cal_compare(a,b):
    A,B=unique(a,'row_id'),unique(b,'row_id')
    if set(A)!=set(B):raise ValueError('Exact CAL IDs required')
    pairs=[];queue=[]
    for i in sorted(A):
        x,y=A[i],B[i]
        if any(x.get(f)!=y.get(f) for f in ('candidate_id','doi','value','unit','pdf_sha256')):raise ValueError('CAL source/numeric inputs differ')
        xc=json.loads(x.get('corrected_fields_json') or '{}');yc=json.loads(y.get('corrected_fields_json') or '{}')
        numx=x.get('numeric_verdict') or x.get('numeric_span_status');numy=y.get('numeric_verdict') or y.get('numeric_span_status')
        vx=x.get('review_verdict') or x.get('verdict');vy=y.get('review_verdict') or y.get('verdict')
        fields=sorted({*xc,*yc})
        lexical=[f for f in fields if xc.get(f)!=yc.get(f)]
        pairs.append({'row_id':i,'ksh_verdict':vx,'prv_verdict':vy,'numeric_span_status_agrees':numx==numy,'numeric_ksh':numx,'numeric_prv':numy,'correction_fields_ksh':sorted(xc),'correction_fields_prv':sorted(yc),'lexical_or_additional_correction_fields':lexical})
        if lexical:queue.append({'row_id':i,'ksh_corrections':xc,'prv_corrections':yc,'status':'AI_COMPARISON_PENDING_HUMAN_SOURCE_REVIEW','note':'Exact string differences are not semantic disagreements; additional qualifiers remain visible. Original extraction and fit unchanged.'})
    return {'n':len(pairs),'numeric_span_status_agreement':sum(p['numeric_span_status_agrees'] for p in pairs),'verdict_pairs':dict(Counter(p['ksh_verdict']+'|'+p['prv_verdict'] for p in pairs)),'rows':pairs,'source_values_or_fit_changed':False},queue

def write_new(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:f.write(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['r1','cal']);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--queue',type=Path,required=True);a=ap.parse_args()
    if a.out.exists() or a.queue.exists():ap.error('Refusing overwrite')
    if not a.queue.resolve().is_relative_to((ROOT/'data/derived').resolve()):ap.error('Private queue must be in ignored data/derived')
    started=datetime.now(timezone.utc).isoformat()
    if a.mode=='r1':
        paths=['annotation/condition_audit/condition_audit_packet_100_R1_Kush.csv','annotation/condition_audit/ksh_R1_AI_review_closeout_2026-11-13.csv','annotation/condition_audit/prv_R1_AI_review_2026-11-13.csv']
        hashes={p:sha(p) for p in paths} # hash returned files before numeric scoring
        expected=json.loads(Path('reports/step07/07A_R1_packet_manifest.json').read_text())['sha256_packet_Kush']
        if hashes[paths[0]]!=expected:raise ValueError('Issued hash differs')
        out=paired(*(read(p) for p in paths));queue=out.pop('disagreement_cells')
        out['disagreement_cell_count']=len(queue);out['by_field']=dict(Counter(x['field'] for x in queue))
        out['limitations']=['Two AI personas, not independent humans; registered numeric statistic is descriptive only.','Original labels are frozen; no rescoring after proposed adjudication, no human signature supplied.','Reviewers were given raw/normalized fields; ontology code meanings not independently verified.','N/A versus CORRECT convention and source precision require source/protocol-aware adjudication; no post-hoc normalizer repair.']
    else:
        paths=['annotation/aa_pilot/ksh_CAL_source_review_closeout_2026-11-13.csv','annotation/aa_pilot/prv_CAL_source_review_2026-11-13.csv'];hashes={p:sha(p) for p in paths}
        out,queue=cal_compare(*(read(p) for p in paths))
        out.update(gate='NOT_COUNTED',reason='AI_PERSONAS_NOT_INDEPENDENT_SOURCE_VERIFIERS',counts_as_human_gate=False,scientific_gate_pass=False)
        out['limitations']=['Both reviewers verified source spans; this does not validate chemical assay specificity or simulation.','Lexical correction differences include synonymous wording and added metadata, not measured disagreement accuracy.','No updated extraction/fit/lineage or human approval inferred.']
    write_new(a.queue,queue)
    out.update(record='REDUCED_SUBMISSION_AI_'+a.mode.upper()+'_CLOSEOUT',started_at_utc=started,completed_at_utc=datetime.now(timezone.utc).isoformat(),labels=LABELS,review_status='AI_VERDICT_PENDING_HUMAN_REVIEW',input_sha256=hashes,private_queue_sha256=sha(a.queue),private_queue=str(a.queue),tool_sha256=sha(__file__))
    write_new(a.out,out)
    print(json.dumps({'mode':a.mode,'gate':out['gate'],'queue_rows':len(queue),'out':str(a.out)}))
if __name__=='__main__':main()
