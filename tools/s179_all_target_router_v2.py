#!/usr/bin/env python3
"""Run the unchanged recipe router for every raw target ID in ACTIVE EVD.

Reuse the prehashed balanced composition sample and memoize only target-independent
parsing within one recipe. No new parameter, gate threshold or interpolation rule. For unscreened no-hit targets, aggregate-count equivalence is derived from the unchanged router and checked on additional targets during the run.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from itertools import chain
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))


class CachedRung:
    def __init__(self, base):
        self.base, self.cache = base, {}

    def __getattr__(self, name):
        return getattr(self.base, name)

    def _call(self, name, source, config, extra=(), **kwargs):
        key = name, source.text_id, source.sha256, repr(config), extra, tuple((k, repr(v)) for k, v in sorted(kwargs.items()))
        if key not in self.cache:
            function = getattr(self.base, name)
            self.cache[key] = function(source, config, **kwargs) if name != 'link' else function(source, extra[0], config)
        return self.cache[key]

    def run(self, source, config, **kwargs):
        return self._call('run', source, config, **kwargs)

    def extract_mentions(self, source, config):
        return self._call('extract_mentions', source, config)

    def link(self, source, mention, config):
        # Mention objects are immutable, but their nested attributes need not be hashable.
        key = 'link', source.text_id, source.sha256, repr(config), repr(mention)
        if key not in self.cache:
            self.cache[key] = self.base.link(source, mention, config)
        return self.cache[key]


def partition_targets(targets, pairs, index, gates):
    hits={r['svar_id'] for pair in pairs for r in index._by_key.get(pair, ())}
    specific=[target for target in targets if target in hits or gates.screen.screened(target)]
    return specific,[target for target in targets if target not in set(specific)]


def measure(out):
    items=out['items']
    return {'route':Counter(item['route'] for item in items),
            'reason':Counter(reason for item in items for reason in item['reasons']),
            'items':len(items),'recipes_with_direct':int(any(item['route']=='DIRECT' for item in items))}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1048576), b''): h.update(part)
    return h.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists(): parser.error('Refusing overwrite')
    from culinarystate.recipes import corpus
    from culinarystate.recipes.ledgers import LOCALE
    from culinarystate.ledgers.store import LedgerStore
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.mechanism import router_demo as RD, evidence_gates as EG, process_signatures as PS
    from culinarystate.quantity import rc2_dryrun as D
    from s179_composition_sample_audit import digest
    manifest = json.loads(args.manifest.read_text()); wanted = {r['recipe_id']: r for r in manifest['selected']}
    source_hashes = {p: sha(Path(p) if Path(p).is_absolute() else ROOT / p) for p in manifest['input_sha256']}
    if source_hashes != manifest['input_sha256']: raise ValueError('Manifest input hash mismatch')
    records = chain(corpus.iter_rec_corpora(), corpus.iter_foodcom(), corpus.iter_tasteset())
    sample = []
    for rec in records:
        expected = wanted.get(rec['recipe_id'])
        if expected:
            if digest({'ingredient_lines': rec['ingredient_lines'], 'steps': rec['steps']}) != expected['source_fields_sha256']:
                raise ValueError('Selected source fields changed')
            sample.append(rec)
    if len(sample) != len(wanted): raise ValueError('Selected recipe missing')
    started = datetime.now(timezone.utc).isoformat()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    code = {str(p.relative_to(ROOT)): sha(p) for p in ROOT.glob('src/**/*.py')}
    code['tools/s179_all_target_router_v2.py'] = sha(__file__)
    evd = LedgerStore().all_latest('EVD')
    targets = sorted({r['target']['state_variable_id'] for r in evd if r['status']=='ACTIVE' and r.get('target',{}).get('state_variable_id')})
    index, gates, hierarchy, schema, rung = RD.EvidenceIndex.from_rows(evd), EG.EvidenceGates.load(), PS.read_process_hierarchy(), D.load_schema(), RungA()
    totals = {target: {'route': Counter(), 'reason': Counter(), 'recipes_with_direct': 0, 'items': 0, 'exceptions': Counter()} for target in targets}
    source_counts, no_steps = Counter(), Counter()
    parity_checks=grouped_target_evaluations=0
    for i, rec in enumerate(sorted(sample, key=lambda r: r['recipe_id'])):
        family = rec['source_family']; source_counts[family] += 1
        raw = '\n'.join(rec.get('steps') or [])
        if not raw.strip(): no_steps[family] += 1; continue
        cached = CachedRung(rung)
        def route(target):
            return RD.route_text(raw,index=index,target_svar=target,locale=LOCALE.get(family),rung=cached,
                                 hierarchy=hierarchy,schema=schema,gates=gates,ingredient_lines=rec.get('ingredient_lines'))
        first=route(targets[0])
        pairs={(item['ingredient_id'],item['process_id']) for item in first['items']}
        specific,generic=partition_targets(targets,pairs,index,gates)
        computed={targets[0]:measure(first)}
        if generic:
            representative=generic[0]
            if representative not in computed:computed[representative]=measure(route(representative))
            shared=computed[representative]
            if len(generic)>1 and i%50==0:
                assert measure(route(generic[-1]))==shared,'Unscreened/no-hit target metric equivalence failed'
                parity_checks+=1
            for target in generic:computed[target]=shared
            grouped_target_evaluations+=len(generic)-1
        for target in specific:
            if target not in computed:computed[target]=measure(route(target))
        for target in targets:
            acc=totals[target];m=computed[target]
            acc['items']+=m['items'];acc['recipes_with_direct']+=m['recipes_with_direct']
            acc['route'].update(m['route']);acc['reason'].update(m['reason'])
        if (i+1)%25 == 0: print(f'All-target sample {i+1}/{len(sample)}; targets={len(targets)}', flush=True)
    if code != {p: sha(ROOT/p) for p in code}: raise RuntimeError('Source changed during run')
    report = {'record':'ALL_ACTIVE_EVD_TARGET_ROUTER_SAMPLE_V2','started_at_utc':started,'completed_at_utc':datetime.now(timezone.utc).isoformat(),
              'base_commit':head,'code_sha256':code,'input_sha256':source_hashes,
              'manifest_sha256':sha(args.manifest),'selected_recipes':len(sample),'recipes_by_family':dict(source_counts),
              'no_instruction_channel':dict(no_steps),'raw_target_ids':len(targets),'targets':totals,'generic_metric_parity_checks':parity_checks,'equivalent_target_calls_grouped':grouped_target_evaluations,
              'labels':['ENGINEERING_DIAGNOSTIC','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],'scientific_gate_pass':False,
              'interpolate_definition':'Would require BRACKETING source precheck; unchanged router precheck supplies DIRECT or NONE only. Zero INTERPOLATE is structural, not evidence of no interpolatable effects.',
              'limitations':['1000 balanced selected recipes, not a full-corpus target census or prevalence estimate.',
                             'Raw target IDs retained separately; duplicate canonical variables are not silently pooled.',
                             'No PARAM integration or real SIMULATE; no missing presence floor or chemistry inferred.',
                             'Cached parse reuse is target-independent and parity-tested; no routing rule changed.',
                             'Only count/reason aggregates are shared for targets with no matching ING/PROC source rows and no presence screen; no per-target IDs or claims are synthesized. Every source-hit or screened target runs unchanged routing separately.',
                             'Existing composition sample was already exposed; not fresh gold or confirmatory evaluation.']}
    with args.out.open('x') as f: f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('All targets written',len(targets))


if __name__=='__main__': main()
