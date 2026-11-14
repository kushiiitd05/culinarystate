#!/usr/bin/env python3
"""Hash the existing canonical cell definition and count source-specific density.

Pre-seal resource description only: no reserved assignment read or model rerun.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def audit(rows,cond):
    from culinarystate.eda.report import cell_key
    groups=defaultdict(list)
    for r in rows:
        if r.get('status')=='ACTIVE':groups[r['source_family_id']].append(r)
    result={}
    for family,rs in sorted(groups.items()):
        cells=[(r['id'],cell_key(r,cond)) for r in rs]
        matrices={key[0] for _,key in cells};processes={key[2] for _,key in cells};targets={key[3] for _,key in cells}
        triples={(key[0],key[2],key[3]) for _,key in cells}
        denominator=len(matrices)*len(processes)*len(targets)
        result[family]={'active_rows':len(rs),'canonical_cells':len({key for _,key in cells}),
                        'matrix_labels':len(matrices),'step_sequences':len(processes),'target_labels':len(targets),
                        'observed_matrix_process_target_triples':len(triples),'cartesian_triple_denominator':denominator,
                        'triple_density':len(triples)/denominator if denominator else None,
                        'cell_assignment_sha256':digest(sorted(cells))}
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out.exists():parser.error('Refusing overwrite')
    from culinarystate.ledgers.store import LedgerStore
    store=LedgerStore();rows=store.all_latest('EVD');cond={r['id']:r for r in store.all_latest('COND')}
    start=datetime.now(timezone.utc).isoformat();first=audit(rows,cond);second=audit(list(reversed(rows)),cond)
    assert first==second
    paths=['src/culinarystate/eda/report.py','src/culinarystate/transition/dataset.py','tools/s179_cell_definition_audit.py','ledgers/data/EVD.jsonl','ledgers/data/COND.jsonl']
    report={'record':'CANONICAL_CELL_DEFINITION_AND_DENSITY','started_at_utc':start,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'labels':['RESOURCE_DIAGNOSTIC','PRE_SEAL_NO_HOLDOUT','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],
            'definition':'Existing eda.report.cell_key: lowercase matrix raw name, form, exact step sequence, lowercase target raw name, structural modifiers and reported duration signature.',
            'temperature_not_in_existing_key':True,'condition_completeness_not_equivalence':True,
            'source_and_input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
            'families':first,'core_sha256':digest(first),'reversed_input_repeat_identical':True,'scientific_gate_pass':False,
            'limitations':['Describes all ACTIVE resource rows before seal filtering; no private assignment or model output touched.',
                           'Existing key omits temperature; shared keys are candidates for replicate/duplicate review, not proof of same experimental conditions.',
                           'Density is observed raw-label matrix/step/target triples over their source-specific Cartesian product; basis/form/duration subdivisions belong to canonical_cells separately.',
                           'Source families and provisional groups are not independent experiment units.']}
    with args.out.open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(first))


if __name__=='__main__':main()
