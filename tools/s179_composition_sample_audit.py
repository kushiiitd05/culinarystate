#!/usr/bin/env python3
"""Read-only balanced1,000recipe RECIPE_POOL composition audit and authored worked examples.

Unknown grams remain UNKNOWN in the exported mass view; the old interval engine
is retained without promoting deferred SR portion authority or process effects.
"""
from __future__ import annotations
import argparse
from collections import Counter
from collections.abc import Mapping
from dataclasses import fields,is_dataclass
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'tools'))


def plain(value):
    if is_dataclass(value):
        return {field.name:plain(getattr(value,field.name)) for field in fields(value)}
    if isinstance(value,Mapping):
        return {key:plain(child) for key,child in value.items()}
    if isinstance(value,(tuple,list)):
        return [plain(child) for child in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(plain(value),sort_keys=True,allow_nan=False).encode()).hexdigest()


def sha(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1048576),b''):result.update(chunk)
    return result.hexdigest()


def mass_export(members):
    if not members or any(m.mass.low_g is None or m.mass.high_g is None for m in members):
        return {'status':'UNKNOWN','low_g':None,'high_g':None,'basis':'MEMBER_MASS_UNKNOWN'}
    return {'status':'INTERVAL','low_g':sum(m.mass.low_g for m in members),
            'high_g':sum(m.mass.high_g for m in members),'basis':'SUM_OF_DECLARED_MEMBER_GRAM_INTERVALS'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--seed',default='20261104')
    parser.add_argument('--per-family',type=int,default=200)
    args=parser.parse_args(argv)
    if args.out.exists() or args.manifest.exists():parser.error('Refusing to overwrite')
    if args.per_family<1:parser.error('Positive family size required')
    from culinarystate.recipes import corpus
    from culinarystate.extraction.rung_a_measure import seeded_sample
    from culinarystate.composition import line_census as LC,lot_census as LOT,food_ph as PH
    from culinarystate.composition.lot_state import Member,lot_state
    from culinarystate.composition import ing_sr_match as M,sr_legacy as SR
    from culinarystate.extraction.rung_a_lexicon import load_lexicon
    import s175_line_mass_census as original
    start=datetime.now(timezone.utc).isoformat()
    inputs=[original.SR_DIR/x for x in ['food.csv','food_nutrient.csv','food_portion.csv','measure_unit.csv']]
    inputs += [original.REGISTRY,original.PH_REGISTRY,ROOT/'ledgers/data/ING.jsonl',ROOT/'ledgers/data/REC.jsonl',
               corpus.A1_DIR/'recipes_processed.jsonl',ROOT/'data/interim/wikibooks/recipes.jsonl',
               ROOT/'data/interim/gutenberg/recipes.jsonl',corpus.FOODCOM,corpus.TASTESET]
    input_hashes={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):sha(p) for p in inputs}
    sample=[]
    for family in corpus.SOURCE_FAMILIES:
        source=corpus.iter_foodcom() if family=='FOODCOM' else corpus.iter_tasteset() if family=='TASTESET' else corpus.iter_rec_corpora(families=(family,))
        sample.extend(seeded_sample(source,args.seed,args.per_family))
    manifest={'record':'COMPOSITION_SAMPLE_BEFORE_EVALUATION','seed':args.seed,'per_family':args.per_family,
              'selection_rule':'WITHIN_SOURCE_FAMILY_SHA256_SEED_CONCAT_RECIPE_ID_ASC',
              'selected':[{'recipe_id':r['recipe_id'],'source_family':r['source_family'],
                           'source_fields_sha256':digest({'ingredient_lines':r['ingredient_lines'],'steps':r['steps']})} for r in sample],
              'input_sha256':input_hashes,'labels':['ENGINEERING_DIAGNOSTIC','NON_CITABLE','NO_HUMAN_SIGNOFF_D085']}
    with args.manifest.open('x') as handle:handle.write(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    manifest_hash=sha(args.manifest)
    print('Sample manifest written before evaluation',manifest_hash,flush=True)
    foods=SR.load_sr(original.SR_DIR);names,freq=original._ing_names()
    find=original.make_find_food(load_lexicon(),names,freq)
    resolve=original.make_resolve(foods,M.load_registry(original.REGISTRY),M.build_index(foods))
    ph=PH.PHTable(PH.load_registry_lph(original.PH_REGISTRY))
    kwargs=dict(find_food=find,resolve=resolve,foods=foods)
    lines=LC.census(sample,**kwargs)
    lots=LOT.census(sample,ph=ph,**kwargs)
    totals=Counter();mass_status=Counter();source_basis=Counter();state_hashes=[]
    def members_for(lines,family):
        result=[];metadata=[]
        for index,line in enumerate(lines):
            name=find(line) or ''
            resolved,mass=LC._line(line,family,find,resolve,foods)
            food=foods.get(resolved.fdc_id) if resolved.fdc_id is not None else None
            result.append(Member(name,food,mass,ph.lookup(name)))
            metadata.append({'member_index':index,'fdc_id':resolved.fdc_id,'link_match_status':resolved.status,
                             'link_verification':'UNVERIFIED','record_tier':'NOT_AN_EVD_RECORD',
                             'mass':plain(mass),'source':'USDA_SR_LEGACY_2018_04','source_record_id':resolved.fdc_id})
        return result,metadata
    for recipe in sample:
        members,_=members_for(recipe['ingredient_lines'],recipe['source_family'])
        totals['recipes']+=1
        if not members:
            totals['recipes_without_ingredient_lines']+=1
            continue
        first=lot_state(members);second=lot_state(members)
        first_hash,second_hash=digest(first),digest(second)
        totals['deterministic_repeats_equal']+=first_hash==second_hash
        totals['deterministic_repeats_mismatched']+=first_hash!=second_hash
        totals['lots']+=1
        state_hashes.append({'recipe_id':recipe['recipe_id'],'state_sha256':first_hash})
        view=mass_export(members);mass_status[view['status']]+=1
        for member in members:
            source_basis[member.mass.basis]+=1
            totals['unknown_grams_members']+=member.mass.low_g is None or member.mass.high_g is None
            totals['known_grams_members']+=member.mass.low_g is not None and member.mass.high_g is not None
        totals['missing_required_state_labels']+=not all(x in first.labels for x in ['MODEL_DERIVED','AS_LISTED_NO_PROCESS_EFFECTS','NON_CITABLE'])
    examples=[]
    for key,authored in [('SYNTHETIC_KNOWN_MASS',['100 g sugar','50 g water']),('SYNTHETIC_UNKNOWN_MASS',['100 g sugar','salt to taste'])]:
        members,metadata=members_for(authored,'WIKIBOOKS');state=lot_state(members)
        values=plain(state)
        # Canonical ingredient names are metadata; no corpus recipe text is exported.
        values.pop('member_ph',None)
        examples.append({'example_id':key,'origin':'AUTHORED_SYNTHETIC_NOT_GOLD','authored_inputs':authored,
                         'members':metadata,'mass_export':mass_export(members),'as_listed_state':values,
                         'state_sha256':digest(state),'scientific_applicability_certified':False})
    code_paths=['tools/s179_composition_sample_audit.py','tools/s175_line_mass_census.py']+[str(p.relative_to(ROOT)) for p in (ROOT/'src/culinarystate/composition').glob('*.py')]
    result={'record':'COMPOSITION_BALANCED_SAMPLE_AND_WORKED_EXAMPLES','started_at_utc':start,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'labels':['ENGINEERING_DIAGNOSTIC','MODEL_DERIVED','SR_LINK_UNVERIFIED','AS_LISTED_NO_PROCESS_EFFECTS','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],
            'manifest':str(args.manifest),'manifest_sha256':manifest_hash,'input_sha256':input_hashes,
            'code_sha256':{p:sha(ROOT/p) for p in sorted(code_paths)},'counts':dict(totals),'mass_export_status':dict(mass_status),
            'member_mass_basis':dict(source_basis),'line_census':lines,'lot_census':lots,
            'repeat_state_hashes_sha256':digest(state_hashes),'examples':examples,'scientific_gate_pass':False,
            'limitations':['Balanced sample is not prevalence-weighted and does not constitute a full-corpus census.',
                           'RECIPE_POOL/as-listed slice only; no event-level lot transition, evaporation, leaching or fat-loss replay.',
                           'Existing SR-derived gram intervals are exploratory/provisional; deferred portion authority is not promoted.',
                           'Unknown member grams remain UNKNOWN in exported total-mass view; original interval engine remains unchanged.',
                           'SR links are UNVERIFIED; pH member flags are not mixture-pH measurements; no food safety claims.',
                           'Authored worked examples are synthetic illustrations using sourced SR records, not independent gold or chemical validation.']}
    assert sha(args.manifest)==manifest_hash
    with args.out.open('x') as handle:handle.write(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'counts':dict(totals),'mass_status':dict(mass_status)}))


if __name__=='__main__':main()
