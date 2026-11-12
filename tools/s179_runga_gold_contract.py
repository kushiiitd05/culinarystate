#!/usr/bin/env python3
"""Inspect the actual Rung A / historical Gold comparison contract, without tuning.

Never relabel generic ACTION as Transform or invent a semantic alignment to score.
Public output contains counts/hashes only; no third-party recipe text.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tools'))
MAPPING={s.upper():s for s in ('Merge','Transform','Transfer','Split','Discard','Reserve','Recombine')}


def gold_kind(kind):return MAPPING.get(kind)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out.exists():parser.error('Refusing overwrite')
    import s179_compiler_vs_gold_pooled as original
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.quantity.rc2_dryrun import load_schema
    from culinarystate.annotation.gold import to_events
    rung=RungA();schema=load_schema();start=datetime.now(timezone.utc).isoformat();sets={}
    for name,folder,pattern,basis in original.SETS:
        paths=sorted(folder.glob(pattern));docs=original.load_docs(paths)
        pred,gold,adapted=Counter(),Counter(),Counter();missing_kind=0
        for i,doc in enumerate(docs):
            raw='\n'.join(s['text'] for s in doc['steps'])
            parsed=rung.run(SourceText.from_raw('GOLD_CONTRACT_'+str(i),raw),rung.config(),schema=schema)
            for e in parsed.graph.events:
                kind=next((a.value for a in e.attributes if a.field=='event_kind'),'UNSPECIFIED')
                pred[str(kind)]+=1;label=gold_kind(kind)
                if label:adapted[label]+=1
                else:missing_kind+=1
            gold.update(type(e).__name__ for e in to_events(doc) if type(e).__name__!='Add')
        sets[name]={'n_recipes':len(docs),'label_basis':basis,'input_set_sha256':original.set_digest(paths) if paths else None,
                    'status':'INPUT_MISSING' if not paths else 'COUNTS_COMPLETE_SEMANTIC_ALIGNMENT_REQUIRED',
                    'raw_candidate_kinds':dict(pred),'explicitly_compatible_types':dict(adapted),'unmapped_candidate_events':missing_kind,
                    'gold_event_types_excluding_adds':dict(gold),'event_or_state_precision':None,
                    'null_metric_reason':'P1 packets unavailable' if not paths else 'Generic ACTION/UNSPECIFIED and gold Merge/Transform/state labels are not an established shared annotation contract.'}
    code=['tools/s179_runga_gold_contract.py','src/culinarystate/extraction/rung_a.py','src/culinarystate/state_graph/event_adapter.py','src/culinarystate/annotation/gold.py']
    report={'record':'RUNGA_VS_GOLD_REPRESENTATION_CONTRACT_AUDIT','started_at_utc':start,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'labels':['DIAGNOSTIC','NOT_INDEPENDENT','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],'sets':sets,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in code},'declared_exact_type_mapping':MAPPING,
            'scientific_gate_pass':False,'limitations':['The older rule compiler evaluation remains unchanged; this uses actual Rung A candidates, not a substituted compiler.',
                        'P1 accepted-A Gold is not present locally; blank packets are not accepted Gold.',
                        'No semantic typing/alignment is invented to manufacture per-field precision or a state confusion matrix.',
                        'Existing compiler-vs-Gold Wilson/bootstrap outputs retain their original model and non-independent label basis.']}
    with args.out.open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(sets))


if __name__=='__main__':main()
