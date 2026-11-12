#!/usr/bin/env python3
"""Extend the existing phrase-coverage adapter to local BBC lines; no NER inference."""
from collections import Counter
from datetime import datetime,timezone
import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tools'))


def main():
    import s178_analysis_coverage_census as old
    from culinarystate.recipes import corpus
    from culinarystate.extraction.rung_a_lexicon import tokens
    from culinarystate.quantity.grammar import parse_line
    out=ROOT/'reports/s179/coverage_BBC_GUT_2026-11-13.json'
    private=ROOT/'data/derived/coverage_refresh_2026-11-13/unmapped_top500_BBC.csv'
    if out.exists() or private.exists():raise SystemExit('Refusing overwrite')
    matcher,lexicon=old.load_matcher(ROOT);start=datetime.now(timezone.utc).isoformat()
    mentions=Counter();classes={};recipes=lines=0
    for rec in corpus.iter_rec_corpora(families=('A1_BBC_GOOD_FOOD',)):
        recipes+=1
        for line in rec['ingredient_lines']:
            lines+=1;words=old.mention_words(line,'A1_BBC_GOOD_FOOD',tokens,parse_line);key=tuple(words)
            if key:mentions[key]+=1
            if key not in classes:classes[key]=matcher.classify(words)
    block,ranked=old.family_block(mentions,classes)
    block.update(recipes=recipes,ingredient_lines=lines)
    nonexact=[r for r in ranked if r[2] not in ('EXACT_ING','EXACT_ALIAS')][:500]
    private.parent.mkdir(parents=True,exist_ok=True)
    with private.open('x',newline='') as f:
        w=csv.writer(f);w.writerow(['rank','phrase','count','class'])
        for i,(phrase,count,kind) in enumerate(nonexact,1):w.writerow([i,phrase,count,kind])
    import subprocess
    if subprocess.run(['git','check-ignore','-q','--',str(private)],cwd=ROOT).returncode:raise RuntimeError('Private list not ignored')
    gut_total=gut_lines=0
    for rec in corpus.iter_rec_corpora(families=('GUTENBERG_SEGMENT',)):
        gut_total+=1;gut_lines+=len(rec['ingredient_lines'])
    report={'record':'BBC_GUT_PHRASE_COVERAGE_ADAPTER','started_at_utc':start,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'labels':['LEXICON_PROXY_NOT_NER','ENGINEERING_DIAGNOSTIC','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],'scientific_gate_pass':False,
            'BBC':block,'GUTENBERG_SEGMENT':{'recipes':gut_total,'ingredient_lines':gut_lines,'coverage':None,'reason':'No separate ingredient-line channel; no zero-coverage or negative NER outcome inferred.'},
            'private_unmapped_list':{'path':str(private.relative_to(ROOT)),'rows':len(nonexact),'sha256':hashlib.sha256(private.read_bytes()).hexdigest()},
            'lexicon':lexicon,'source_sha256':{str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'tools/s178_analysis_coverage_census.py',corpus.A1_DIR/'recipes_processed.jsonl',ROOT/'data/interim/gutenberg/recipes.jsonl']},
            'limitations':['Existing MENTION_RULE_V1, matcher and family_block calculations reused unchanged.','Full BBC corpus processed locally under D003; raw phrases remain ignored.','This completes corpus-channel coverage curves/queues, not learned model span agreement, accuracy or independent gold.']}
    with out.open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('BBC',recipes,'recipes;',block['mentions'],'proxy mentions; GUT ingredient channel',gut_lines)


if __name__=='__main__':main()
