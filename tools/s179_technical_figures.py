#!/usr/bin/env python3
"""Export technical figures beside the author-owned report, never editing it.

Every numerical series comes from source JSON. Authored diagrams are explicitly
schematic and carry no scientific measurements or minted ledger identifiers.
Requires matplotlib (the local run uses temporary export-only dependencies).
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out_dir.exists():parser.error('New output directory required')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'s179-technical-figures'})
    sources={}
    def read(path):
        p=ROOT/path;sources[path]=hashlib.sha256(p.read_bytes()).hexdigest()
        return json.loads(p.read_text())
    evd=read('reports/s178/analysis/evd_dataset_card_v1.json')
    router=read('reports/step23/router_demo_census_vitc_nonBBC_1000_S179b.json')
    score=read('reports/del5/d5_score_v1_D085/d5_scoring_result.json')
    h1=read('reports/del5/d5_score_v1_D085/d5_h1_after_rung_blind_check_D085.json')['h1']
    mpu=read('reports/s179/MPU_current_evidence_preview_2026-11-12.json')
    p1=read('reports/step19/p1_agreement_counts_S166.json')
    args.out_dir.mkdir(parents=True)
    figures=[]
    def save(fig,name,title,scope,series=None):
        fig.suptitle(title,fontsize=14,color='#173d59',ha='left',x=.08)
        fig.text(.08,.02,'NON_CITABLE · NO_HUMAN_SIGNOFF_D085\n'+scope,fontsize=8,color='#4a5968',wrap=True)
        fig.tight_layout(rect=(.02,.12,.98,.92))
        paths=[]
        for suffix in ['svg','png']:
            p=args.out_dir/(name+'.'+suffix);fig.savefig(p,dpi=160,metadata={'Date':None} if suffix=='svg' else None);paths.append(str(p))
        plt.close(fig);figures.append({'name':name,'title':title,'scope':scope,'series':series,'paths':paths})
    fig,ax=plt.subplots(figsize=(10,4));ax.axis('off')
    nodes={'Local source':(.1,.6),'Rung A':(.34,.8),'Adapter / replay':(.68,.8),'Router parse':(.34,.3),'Evidence packet':(.62,.3),'Strict view':(.88,.3)}
    for label,(x,y) in nodes.items():ax.text(x,y,label,ha='center',bbox={'boxstyle':'round,pad=.6','fc':'#e7eff6','ec':'#38627e'})
    for a,b in [('Local source','Rung A'),('Rung A','Adapter / replay'),('Local source','Router parse'),('Router parse','Evidence packet'),('Evidence packet','Strict view')]:
        ax.annotate('',xy=nodes[b],xytext=nodes[a],arrowprops={'arrowstyle':'->','color':'#52748b','shrinkA':40,'shrinkB':45})
    save(fig,'fig1_architecture','Source-to-replay and source-to-answer engineering paths','Authored architecture schematic. Replay state is not passed into the current router API.')
    values=evd['s203_9_1_total_rows']['rows_per_source_family'];fig,ax=plt.subplots(figsize=(9,4));ax.barh(list(values),list(values.values()),color='#346c91');ax.set_xlabel('Imported ACTIVE EVD rows')
    save(fig,'fig2_evidence_provenance','Imported evidence by source family','E3_UNVERIFIED / COND_UNAUDITED. Imported row counts are not independent experiments.',values)
    fig,ax=plt.subplots(figsize=(9,4));ax.axis('off')
    for x,label in [(.15,'Input lot'),(.5,'Process event'),(.85,'Output lot')]:ax.text(x,.55,label,ha='center',bbox={'boxstyle':'round,pad=.8','fc':'#edf3ed','ec':'#466d4e'})
    for x,y,label in [(.2,.44,'consumes'),(.56,.8,'produces')]:ax.annotate(label,xy=(y,.55),xytext=(x,.55),arrowprops={'arrowstyle':'->'},ha='center')
    save(fig,'fig3_state_graph','A lot/event relationship','Authored schema illustration, not a measured recipe trajectory or gold event annotation.')
    routes=router['route'];fig,ax=plt.subplots(figsize=(9,4));ax.bar(list(routes),list(routes.values()),color='#346c91');ax.set_ylabel('Routed event–ingredient items')
    save(fig,'fig4_router_routes','Vitamin-C router: recorded 1,000-recipe non-BBC sample','ENGINEERING_DIAGNOSTIC. Source-row routing does not certify condition applicability.',routes)
    fig,ax=plt.subplots(figsize=(9,4));series={}
    for rung in ['B5','B7']:
        points=score['d4_m2_risk_coverage']['decision_layer_rungs'][rung]['primary_precision_class']['points']
        xs=[p['coverage'] for p in points];ys=[p['risk']['rate'] for p in points]
        errors=[[p['risk']['rate']-p['risk']['cp95'][0] for p in points],[p['risk']['cp95'][1]-p['risk']['rate'] for p in points]]
        ax.errorbar(xs,ys,yerr=errors,marker='o',capsize=3,label=rung);series[rung]=points
    ax.set(xlabel='Recorded coverage',ylabel='Recorded E1 error rate',ylim=(0,1.05));ax.legend()
    save(fig,'fig5_risk_coverage','Frozen P/C risk–coverage diagnostic','MODEL_ASSISTED_GOLD. Ordinal thresholds are uncalibrated; CP95 intervals transcribed, no rescore.',series)
    values={r:v['all'] for r,v in h1['accuracy'].items()};fig,ax=plt.subplots(figsize=(9,4));rates=[v['rate'] for v in values.values()]
    errors=[[v['rate']-v['cp95'][0] for v in values.values()],[v['cp95'][1]-v['rate'] for v in values.values()]]
    ax.bar(list(values),rates,color='#346c91');ax.errorbar(list(values),rates,yerr=errors,fmt='none',capsize=4,color='#173d59');ax.set(ylabel='Accuracy on AI-drafted S questions',ylim=(0,1))
    save(fig,'fig6_h1_ladder','H1: recorded rule not met','Rung-blind resolution supplement; 24 questions per rung. CIRCULAR_SELF_CONSISTENCY_ONLY.',values)
    counts=Counter(g['status'] for g in mpu['gates']);fig,ax=plt.subplots(figsize=(11,5));ax.barh(list(counts),list(counts.values()),color='#7e678b');ax.set_xlabel('Recorded MPU evidence-preview gates')
    save(fig,'fig7_gate_register','Current evidence-preview dispositions','Preview dated 12 November; not the required post-19-Nov MPU event. No scientific pass supplied.',dict(counts))
    conditions={axis:evd['s203_9_9_condition_coverage'][axis]['rows_by_status'] for axis in ['temperature','duration']}
    fig,ax=plt.subplots(figsize=(10,4));left=[0,0]
    for status in sorted({s for v in conditions.values() for s in v}):
        values=[conditions[axis].get(status,0) for axis in conditions]
        ax.barh(list(conditions),values,left=left,label=status);left=[a+b for a,b in zip(left,values)]
    ax.set_xlabel('Imported EVD rows by condition status');ax.legend(fontsize=7,loc='upper center',bbox_to_anchor=(.5,-.15),ncol=4)
    save(fig,'fig8_condition_missingness','Imported condition-field availability','E3_UNVERIFIED / COND_UNAUDITED. A status named MEASURED does not establish independent source verification.',conditions)
    fields=['concept_agreement','event_f1_strict','state_field_agreement'];values={k:p1['mean'][k] for k in fields}
    fig,ax=plt.subplots(figsize=(10,4));ax.barh([k.replace('_',' ') for k in values],list(values.values()),color='#426e73');ax.set_xlim(0,1);ax.set_xlabel('Recorded pair-summary agreement')
    save(fig,'fig9_p1_agreement','Accepted AI-draft P1 pair summaries','HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND. Not independent inter-rater evidence or predicted-engine accuracy.',values)
    report={'record':'TECHNICAL_FIGURE_EXPORT','labels':['ENGINEERING_DIAGNOSTIC','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],'scientific_gate_pass':False,'matplotlib':matplotlib.__version__,'sources_sha256':sources,'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'figures':figures,'file_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for f in figures for p in f['paths']},'limitations':['Authored architecture/state diagrams are labelled schematics, not data-derived experimental graphs.','No author report/deck edits or final submission approval.','Original frozen results and unsuccessful hypotheses remain unchanged.']}
    with (args.out_dir/'manifest.json').open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('Exported',len(figures),'technical figures')


if __name__=='__main__':main()
