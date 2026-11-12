#!/usr/bin/env python3
"""Select/prehash a bound-heat review sample before AI labels; publish counts/IDs only."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
REVIEW_FIELDS=('temperature','unit','duration','medium','event_attribution')
CODES={'MATCH','MISMATCH','UNASSESSABLE','NOT_BOUND','NON_TEXT_BASIS'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select(rows,seed,n):
    groups=defaultdict(list)
    for row in rows:groups[row['family']].append(row)
    for family in groups:
        groups[family].sort(key=lambda r:(hashlib.sha256((seed+'|'+family+'|'+r['recipe_id']+'|'+r['event_id']).encode()).hexdigest(),r['recipe_id'],r['event_id']))
    result=[];index=0
    while len(result)<n:
        progressed=False
        for family in sorted(groups):
            if index<len(groups[family]) and len(result)<n:result.append(groups[family][index]);progressed=True
        if not progressed:break
        index+=1
    return result


def wilson(k,n):
    if n==0:return [None,None]
    z=1.959963984540054;p=k/n;den=1+z*z/n
    centre=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [0. if k==0 else max(0.,centre-half),1. if k==n else min(1.,centre+half)]


def review_summary(manifest,labels):
    expected={r['case_id'] for r in manifest['selected']}
    if len(labels)!=len(expected) or {r['case_id'] for r in labels}!=expected:raise ValueError('Review case IDs incomplete/duplicated')
    result={}
    for field in REVIEW_FIELDS:
        counts=Counter()
        for row in labels:
            code=row.get('fields',{}).get(field)
            if code not in CODES:raise ValueError('Invalid/missing field review code')
            counts[code]+=1
        n=counts['MATCH']+counts['MISMATCH']
        result[field]={'codes':dict(counts),'matches':counts['MATCH'],'mismatches':counts['MISMATCH'],
                       'adjudicated_denominator':n,'conditional_precision':counts['MATCH']/n if n else None,
                       'wilson_95':wilson(counts['MATCH'],n),'all_selected_cases':len(labels)}
    return result


def make_packet(args):
    if args.manifest.exists() or args.packet.exists():raise ValueError('Refusing to overwrite')
    if subprocess.run(['git','check-ignore','-q','--',str(args.packet)],cwd=ROOT).returncode:raise ValueError('Private packet must be git-ignored')
    files=sorted(args.records_dir.glob('*.jsonl'));rows=[]
    for path in files:
        rows.extend(json.loads(line) for line in path.read_text().splitlines() if line.strip())
    chosen=select(rows,args.seed,args.size)
    if len(chosen)!=args.size:raise ValueError('Insufficient sample')
    record_hashes={str(path):sha(path) for path in files}
    selected=[{'case_id':f'BINDREV-{index+1:03d}','recipe_id':row['recipe_id'],'event_id':row['event_id'],
               'process_id':row['process_id'],'family':row['family'],'source_family':row['source_family'],
               'producer_row_sha256':digest(row)} for index,row in enumerate(chosen)]
    manifest={'record':'BINDER_AI_REVIEW_PREHASH_MANIFEST','created_at_utc':datetime.now(timezone.utc).isoformat(),
              'seed':args.seed,'size':args.size,'selected':selected,'record_file_sha256':record_hashes,
              'selection':'Round-robin process family; within family SHA256(seed|family|recipe_id|event_id) ascending',
              'source_scope':'WIKIBOOKS_ONLY; source-family generalization is not assessed',
              'rubric':{'MATCH':'Bound TEXT_STATED value/unit and event attribution agree with the cited text under manual AI source reading.',
                        'MISMATCH':'Text contradicts bound value/unit or wrong event ownership.',
                        'UNASSESSABLE':'Text/context insufficient to decide; excluded from precision denominator, coverage disclosed.',
                        'NOT_BOUND':'Producer axis is UNKNOWN; no positive prediction to score.',
                        'NON_TEXT_BASIS':'Physical/process definition or carried/default basis; not scored as literal text extraction precision.'},
              'review_fields':list(REVIEW_FIELDS),'labels':['AI_CHECKED','NON_CITABLE','NO_HUMAN_SIGNOFF_D085']}
    with args.manifest.open('x') as handle:handle.write(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('Prehash before source review:',sha(args.manifest),flush=True)
    from culinarystate.recipes.corpus import iter_rec_corpora
    from culinarystate.simulation.condition_binding import Binder
    from culinarystate.extraction.interfaces import SourceText
    need={row['recipe_id'] for row in chosen};recipes={r['recipe_id']:r for r in iter_rec_corpora(families=('WIKIBOOKS',)) if r['recipe_id'] in need}
    binder=Binder.load();graphs={};packets=[]
    for selected_row,row in zip(selected,chosen):
        recipe=recipes[row['recipe_id']];raw='\n'.join(recipe['steps'])
        if row['recipe_id'] not in graphs:
            graphs[row['recipe_id']]=binder.rung.run(SourceText.from_raw('BIND',raw),binder.rung.config(locale=None),schema=binder.schema).graph
        event=next(e for e in graphs[row['recipe_id']].events if e.event_id==row['event_id'])
        start,end=event.span.char_start,event.span.char_end
        sentence=binder._sentence(raw,start)
        contexts=[]
        for field,axis in row['inputs'].items():
            if axis['status']=='UNKNOWN':continue
            span=axis.get('span')
            contexts.append({'field':field,**axis,'source_fragment':raw[span[0]:span[1]] if span else None,
                             'context':raw[max(0,span[0]-65):min(len(raw),span[1]+80)] if span else None})
        packets.append({**selected_row,'action':event.span.surface,'action_span':[start,end],
                        'sentence':raw[sentence[0]:sentence[1]],'raw_recipe_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                        'source_axes':contexts,'all_inputs':row['inputs']})
    args.packet.parent.mkdir(parents=True,exist_ok=True)
    with args.packet.open('x') as handle:
        for packet in packets:handle.write(json.dumps(packet,sort_keys=True)+'\n')
    print('Private source packet created:',len(packets),'cases; no text in public manifest')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    prepare=sub.add_parser('prepare');prepare.add_argument('--records-dir',type=Path,required=True)
    prepare.add_argument('--manifest',type=Path,required=True);prepare.add_argument('--packet',type=Path,required=True)
    prepare.add_argument('--seed',default='20261104');prepare.add_argument('--size',type=int,default=100)
    summarize=sub.add_parser('summarize');summarize.add_argument('--manifest',type=Path,required=True)
    summarize.add_argument('--labels',type=Path,required=True);summarize.add_argument('--packet',type=Path,required=True)
    summarize.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='prepare':make_packet(args);return
    if args.out.exists():parser.error('Refusing to overwrite')
    manifest=json.loads(args.manifest.read_text());review=json.loads(args.labels.read_text())
    if review['manifest_sha256']!=sha(args.manifest) or review['packet_sha256']!=sha(args.packet):parser.error('Review source hash mismatch')
    result={'record':'BINDER_100_CASE_AI_FIELD_REVIEW','completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'manifest_sha256':sha(args.manifest),'private_review_sha256':sha(args.labels),'private_packet_sha256':sha(args.packet),
            'selected':len(manifest['selected']),'source_family':'WIKIBOOKS','seed':manifest['seed'],
            'process_family_counts':dict(Counter(r['family'] for r in manifest['selected'])),
            'field_results':review_summary(manifest,review['labels']),'labels':['AI_CHECKED','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],
            'scientific_gate_pass':False,'rubric':manifest['rubric'],
            'limitations':['AI source reading is not human gold or inter-rater agreement.',
                           'Source family is Wikibooks only; process-family balanced sample is not corpus prevalence.',
                           'Conditional precision denominator excludes unknown/unassessable/non-text axes; counts remain explicit.',
                           'Wilson intervals describe these AI decisions; systematic bias/within-recipe dependence are not corrected.',
                           'No binder rule or frozen scientific output is changed or tuned after review.']}
    with args.out.open('x') as handle:handle.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result['field_results']))


if __name__=='__main__':main()
