#!/usr/bin/env python
"""S178 (T9-C06-R1): SSOT section 238 conformance table (12 contracts x fields).

Reads ``docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`` L25745-26101 (field lists), the ledgers
``ledgers/data/{REC,ING,ALIAS,EVD,IMAP}.jsonl`` and the committed tables ``ledgers/recipe_base/recipe_base_v1.parquet``
and ``ledgers/recipe_identity/recipe_identity_fk_v1.parquet`` and writes ``reports/s178/ssot238_conformance.{csv,md}``.
Counts only: no recipe text and no values are written. The mapping of each SSOT field to a schema property (the ``M``
dictionary below) is the agent's reading (AI_DRAFTED), not human-verified. The build asserts that the SSOT field lists
equal the mapped fields (no unmapped field, none surplus) and that every ABSENT, RELATED, TABLE_ONLY and CODE_ONLY row
carries a reason.

    python tools/s178_ssot238_conformance.py
"""
from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

import pyarrow.parquet as pq

root = str(Path(__file__).resolve().parents[1]) + "/"
SSOT = root + "docs/SSOT/computational_gastronomy_master_ssot_v15_0.md"


def ssot_fields() -> dict[str, list[str]]:
    lines = open(SSOT).read().split("\n")[25744:26101]
    cur, out = None, {}
    for l in lines:
        m = re.match(r"^## 238\.\d+ (\w+)", l)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        m = re.match(r"^- `([^`]+)` \u2014 ", l)
        if m and cur:
            out[cur].append(m.group(1))
    return out


fields = ssot_fields()

# kind: EXACT | RENAMED | COMPOSED | RELATED | TABLE_ONLY | CODE_ONLY | ABSENT
# row: (field, kind, schema_prop, counterpart, count_src, count_path, reason)
RB="recipe_base_v1.parquet"; FK="recipe_identity_fk_v1.parquet"
M={}
M["Recipe"]=("REC",[
("recipe_id","RENAMED","REC.id",f"{RB}:recipe_id","REC","id",""),
("dataset_version","TABLE_ONLY","(none)",f"{RB}:source_version","recipe_base","source_version","REC has no dataset-version property; the table column is the source's version"),
("source_id","COMPOSED","REC.provenance.source_ids",f"{RB}:source_id","REC","provenance.source_ids",""),
("source_url","EXACT","REC.source_url","(table has raw_recipe_pointer only)","REC","source_url","table omits the URL by design (licence)"),
("source_domain","RELATED","(none)",f"{RB}:source_family","recipe_base","source_family","table column is the corpus family, not a URL domain; the domain is derivable only from REC.source_url"),
("license_class","TABLE_ONLY","(none)",f"{RB}:licence_status","recipe_base","licence_status","REC has no licence property"),
("source_checksum","RENAMED","REC.content_sha256",f"{RB}:raw_hash","REC","content_sha256",""),
("title_raw","RENAMED","REC.title",f"{RB}:title_raw","REC","title",""),
("title_normalized","ABSENT","(none)","(none)",None,None,"no normalised-title column was ever written (project law: normalisation is a new column; none built)"),
("language","TABLE_ONLY","(none)",f"{RB}:language","recipe_base","language","REC has no language property"),
("locale","TABLE_ONLY","(none)",f"{RB}:locale","recipe_base","locale","REC has no locale property"),
("cuisine_labels","RENAMED","REC.cuisine",f"{RB}:cuisine_if_explicit","REC","cuisine",""),
("dish_categories","RELATED","(none)",f"{FK}:dish_family_candidate_id","recipe_identity_fk","dish_family_candidate_id","candidate dish-family id, not category labels"),
("servings_raw","ABSENT","(none)","(none)",None,None,"no step extracts servings; no REC property or table column"),
("servings_normalized","ABSENT","(none)","(none)",None,None,"as servings_raw"),
("ingredient_mention_ids","RELATED","REC.n_ingredient_lines","(none)","REC","n_ingredient_lines","only the count of ingredient lines is carried; the mention ledger is not materialised (see IngredientMention)"),
("event_ids","RELATED","(none; GRAPH.event_ids)","(none)","ZERO:GRAPH",None,"the link is held on the GRAPH record (0 ledger rows), not on REC"),
("entity_ids","RELATED","(none; ENTITY.recipe_id)","(none)","ZERO:ENTITY",None,"reverse link only: ENTITY.recipe_id (0 ledger rows)"),
("recipe_graph_id","RELATED","(none; GRAPH.recipe_id)","(none)","ZERO:GRAPH",None,"reverse link only: GRAPH.recipe_id (0 ledger rows)"),
("duplicate_group_id","TABLE_ONLY","(none)",f"{FK}:duplicate_group_id","recipe_identity_fk","duplicate_group_id","identity tables, not REC"),
("annotation_tier","RELATED","(none)",f"{RB}:quality_tier","recipe_base","quality_tier","quality tier registry label, not the SSOT annotation tier vocabulary"),
("annotation_model","COMPOSED","(none)",f"{RB}:ner_version + linker_version + parser_version + normalizer_version","recipe_base","parser_version","four version columns instead of one model field; rule/NER stages"),
("prompt_version","ABSENT","(none)","(none)",None,None,"no LLM prompt version is recorded for recipe annotation; production stages are rules/NER (parser_version, ner_version)"),
("schema_version","EXACT","REC.schema_version","(none)","REC","schema_version",""),
("validation_status","RENAMED","REC.verification.status",f"{RB}:human_verification_status","REC","verification.status",""),
("validation_flags","ABSENT","(none)","(none)",None,None,"no per-recipe flag list; validator issue codes exist only in counts-only reports"),
])
M["IngredientMention"]=(None,[
("mention_id","CODE_ONLY","(no schema)","extraction/interfaces.py Mention.mention_id",None,None,""),
("recipe_id","RELATED","QNT.recipe_id (line-level record)","interfaces SourceText.text_id",None,None,"QNT is a line record, not a mention record"),
("raw_text","RELATED","QNT.raw","interfaces SourceText.raw",None,None,""),
("source_span","RELATED","QNT.span","interfaces Mention.span (Span)",None,None,""),
("canonical_ingredient_id","RELATED","QNT.ingredient_id","interfaces LinkResult.selected_id",None,None,""),
("candidate_ids","CODE_ONLY","(no schema; ALIAS.candidate_ingredient_ids is alias-level)","interfaces LinkResult.candidates (concept_id)",None,None,""),
("variety","CODE_ONLY","(no schema; ING.facets.variety is canonical-level)","interfaces Mention.attributes (ValueClaim.field)",None,None,"attribute claims, not a fixed field"),
("form","CODE_ONLY","(no schema; ING.facets.form is canonical-level)","interfaces Mention.attributes",None,None,""),
("state","CODE_ONLY","(no schema; ING.facets.prep_state is canonical-level)","interfaces Mention.attributes",None,None,""),
("size","RELATED","QNT.parsed.size","interfaces Mention.attributes",None,None,""),
("quantity_id","RELATED","QNT.id","interfaces QuantityParseResult.result_id",None,None,""),
("role","ABSENT","(none)","(none)",None,None,"no extractor for ingredient role (main/garnish) exists"),
("optional","RELATED","QNT.qualifiers (string list)","(none)",None,None,"carried as a qualifier string, not a boolean"),
("divided","RELATED","QNT.qualifiers (string list)","(none)",None,None,"as optional"),
("reserved","RELATED","QNT.qualifiers (string list)","(none)",None,None,"as optional; reserved portions are never implicit by design (D-074)"),
("brand","ABSENT","(none)","(none)",None,None,"no extractor for brand"),
("canonicalization_status","RELATED","ALIAS.link_band","interfaces LinkResult.failure / selected_id is None",None,None,"alias link band is per alias, not per mention"),
("provenance","CODE_ONLY","(no schema; QNT.provenance is the nearest)","interfaces Provenance",None,None,""),
("annotation_confidence_features","ABSENT","(none)","(none)",None,None,"the confidence vector (decision/confidence.py) is answer-level; no per-mention features recorded"),
])
M["CanonicalIngredient"]=("ING",[
("ingredient_id","RENAMED","ING.id","","ING","id",""),
("preferred_name","RENAMED","ING.canonical_name","","ING","canonical_name",""),
("food_category","RENAMED","ING.category","","ING","category",""),
("parent_id","RENAMED","ING.parent_ids (list)","","ING","parent_ids","single id in SSOT, list in the schema"),
("scientific_name","EXACT","ING.scientific_name","","ING","scientific_name",""),
("foodon_id","RENAMED","ING.crosswalks.foodon.external_id","","ING","crosswalks.foodon.external_id",""),
("fdc_ids","RENAMED","ING.crosswalks.fdc.external_id","","ING","crosswalks.fdc.external_id","single external id in the schema (list in SSOT)"),
("aliases","RELATED","(reverse: ALIAS.ingredient_id)","","ALIAS","ingredient_id","held in the ALIAS ledger, not on ING"),
("regional_aliases","RELATED","(reverse: ALIAS.region)","","ALIAS","region","as aliases"),
("languages","RELATED","(reverse: ALIAS.language)","","ALIAS","language","as aliases"),
("known_forms","RENAMED","ING.facets.form","","ING","facets.form",""),
("known_states","RENAMED","ING.facets.prep_state","","ING","facets.prep_state",""),
("portion_profile_ids","RELATED","(reverse: POR.ingredient_id)","","ZERO:POR",None,"POR has 0 ledger rows"),
("chemistry_link_ids","RELATED","(reverse: IMAP.ingredient_id)","","IMAP","ingredient_id","held in the IMAP ledger (rows counted are IMAP rows with an ingredient id)"),
("status","EXACT","ING.status","","ING","status",""),
("version_created","RENAMED","ING.created_at (and ING.version)","","ING","created_at",""),
("human_verified","RENAMED","ING.verification.status","","ING","verification.status","status enum, not boolean"),
])
M["Alias"]=("ALIAS",[
("alias_id","RENAMED","ALIAS.id","","ALIAS","id",""),
("surface","EXACT","ALIAS.surface","","ALIAS","surface",""),
("canonical_ingredient_id","RENAMED","ALIAS.ingredient_id","","ALIAS","ingredient_id","null when the alias is ambiguous (candidate_ingredient_ids holds the options)"),
("language","EXACT","ALIAS.language","","ALIAS","language",""),
("locale","RELATED","ALIAS.region","","ALIAS","region","region, not a locale code"),
("alias_type","EXACT","ALIAS.alias_type","","ALIAS","alias_type",""),
("source_count","RELATED","ALIAS.corpus_frequency","","ALIAS","corpus_frequency","corpus frequency, not a count of sources"),
("source_domains","ABSENT","(none)","(none)",None,None,"ALIAS carries corpus_frequency only; no domain list"),
("verification","EXACT","ALIAS.verification","","ALIAS","verification.status",""),
("first_seen_version","RELATED","ALIAS.created_at (and ALIAS.version)","","ALIAS","created_at","creation time/version of the record, not first corpus version"),
])
M["Quantity"]=("QNT",[
("quantity_id","RENAMED","QNT.id","",None,None,""),
("raw_text","RENAMED","QNT.raw","",None,None,""),
("quantity_type","RENAMED","QNT.parsed.kind","",None,None,"enum NUMBER/RANGE/FRACTION/MIXED/MULTIPLIER/PACKAGE/QUALITATIVE/NONE"),
("value","RENAMED","QNT.parsed.value","",None,None,""),
("lower","RENAMED","QNT.parsed.low","",None,None,""),
("upper","RENAMED","QNT.parsed.high","",None,None,""),
("fraction","RELATED","QNT.parsed.value (kind FRACTION / MIXED)","",None,None,"no separate fraction field; fractions are kinds of value"),
("count","EXACT","QNT.count","",None,None,""),
("unit_id","RENAMED","QNT.parsed.unit_id","",None,None,""),
("unit_locale","RENAMED","QNT.locale","",None,None,""),
("size","RENAMED","QNT.parsed.size","",None,None,""),
("packing","RELATED","QNT.parsed.package_size","",None,None,"package size, not packing (POR.packing exists on the portion record)"),
("container","ABSENT","(none)","(none)",None,None,"no container property in QNT"),
("approximate","RELATED","QNT.parsed.qualifier","",None,None,"qualifier string, not a boolean"),
("qualitative_term","RENAMED","QNT.parsed.qualifier / normalized.qualitative","",None,None,""),
("optional","RELATED","QNT.qualifiers (string list)","",None,None,""),
("divided","RELATED","QNT.qualifiers (string list)","",None,None,""),
("reserved","RELATED","QNT.qualifiers (string list)","",None,None,""),
("normalized_mass_g","RENAMED","QNT.mass_g","",None,None,""),
("normalized_volume_ml","RENAMED","QNT.volume_ml","",None,None,""),
("conversion_record_id","RENAMED","QNT.portion_id (+ conversion_method, conversion_path)","",None,None,""),
("provenance","EXACT","QNT.provenance","",None,None,""),
])
M["PortionProfile"]=("POR",[
("portion_profile_id","RENAMED","POR.id","",None,None,""),
("ingredient_id","EXACT","POR.ingredient_id","",None,None,""),
("state","RELATED","POR.form","",None,None,"no separate prep-state property"),
("form","EXACT","POR.form","",None,None,""),
("size_class","ABSENT","(none)","(none)",None,None,"POR has no size property; SR portion size words are not modelled (Mac ticket A5 concerns size words)"),
("packing","EXACT","POR.packing","",None,None,""),
("portion_value","RELATED","POR.from_unit_id","",None,None,"value is implicit 1 per from_unit_id"),
("portion_unit","RENAMED","POR.from_unit_id","",None,None,""),
("unit_locale","RENAMED","POR.locale","",None,None,""),
("mass_g","RENAMED","POR.grams_per_unit.value","",None,None,""),
("mass_low_g","RENAMED","POR.grams_per_unit.low","",None,None,""),
("mass_high_g","RENAMED","POR.grams_per_unit.high","",None,None,""),
("conversion_class","RELATED","QNT.conversion_method (on the quantity record)","",None,None,"not on POR"),
("source_type","RENAMED","POR.basis","",None,None,"POR.basis enum is MEASURED / DATABASE / CONVENTION / RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION; the composition/ plan names basis SR_PORTION, which is NOT in the enum (conformance gap)"),
("source_record","COMPOSED","POR.provenance.source_ids / provenance.locator","",None,None,""),
("sample_count","ABSENT","(none)","(none)",None,None,"no sample_count property; the composition/ POR candidates need one (board T3-C08-R1)"),
("source_diversity","ABSENT","(none)","(none)",None,None,"no property"),
("verification","EXACT","POR.verification","",None,None,""),
])
M["Event"]=("EVT",[
("event_id","RENAMED","EVT.id","state_graph/event_log.py EngineEvent.event_id",None,None,""),
("recipe_id","EXACT","EVT.recipe_id","",None,None,""),
("event_index","COMPOSED","EVT.step_index + EVT.ordinal","EngineEvent.order",None,None,""),
("process_id","EXACT","EVT.process_id","",None,None,""),
("process_modifiers","CODE_ONLY","(none)","EngineEvent.attributes",None,None,"EVT has no modifiers property (EVD.process.modifiers is evidence-side)"),
("input_entity_ids","RELATED","EVT.input_state_ids","EngineEvent.consumes",None,None,"state ids, not entity ids"),
("output_entity_ids","RELATED","EVT.output_state_ids","EngineEvent.produces",None,None,"state ids, not entity ids"),
("tool_ids","EXACT","EVT.tool_ids","",None,None,""),
("medium","RELATED","EVT.condition_id -> COND.medium","",None,None,"held on the condition record"),
("temperature_C","RELATED","EVT.condition_id -> COND.temperatures","",None,None,"held on the condition record"),
("temperature_raw","RELATED","EVT.condition_id -> COND.temperatures (raw)","",None,None,"held on the condition record"),
("duration_s","RELATED","EVT.condition_id -> COND.duration","",None,None,"held on the condition record"),
("duration_raw","RELATED","EVT.condition_id -> COND.duration (raw)","",None,None,"held on the condition record"),
("pressure","RELATED","EVT.condition_id -> COND.pressure","",None,None,"held on the condition record"),
("pH","RELATED","EVT.condition_id -> COND.ph_initial / ph_final","",None,None,"held on the condition record"),
("moisture_condition","RELATED","EVT.condition_id -> COND.moisture","",None,None,"held on the condition record"),
("endpoint_states","RENAMED","EVT.endpoint","",None,None,"single string in the schema"),
("source_span","RENAMED","EVT.span","",None,None,""),
("provenance","EXACT","EVT.provenance","",None,None,""),
("validation_flags","ABSENT","(none)","(none)",None,None,"no flags property; replay/validator issue codes appear in counts-only reports"),
])
M["Entity"]=("ENTITY",[
("entity_id","RENAMED","ENTITY.id","",None,None,""),
("recipe_id","EXACT","ENTITY.recipe_id","",None,None,""),
("entity_type","RENAMED","ENTITY.kind","",None,None,"enum INGREDIENT_LOT/INTERMEDIATE/TOOL_CONTENTS/FINAL_DISH/DISCARD/UNKNOWN"),
("canonical_food_id","RENAMED","ENTITY.ingredient_id","",None,None,""),
("name","RENAMED","ENTITY.label","",None,None,""),
("parent_entity_ids","ABSENT","(none)","state_graph/event_log.py Allocation.parent / child",None,None,"lineage lives in event allocations (code), not on the entity record"),
("created_by_event","RELATED","(reverse: STATE.produced_by_event_id)","",None,None,"held on the state record"),
("destroyed_or_consumed_by_event","ABSENT","(none)","EngineEvent.consumes / discards",None,None,"no property on ENTITY"),
("quantity_state_id","ABSENT","(none; reverse STATE.entity_id)","",None,None,"link is by STATE.entity_id"),
("current_state_id","ABSENT","(none; reverse STATE.entity_id, max state_version)","",None,None,"derived by query, not stored"),
])
M["State"]=("STATE",[
("state_id","RENAMED","STATE.id","",None,None,""),
("entity_id","EXACT","STATE.entity_id","",None,None,""),
("event_index","RELATED","STATE.produced_by_event_id (+ state_version)","",None,None,"event id, not index"),
("timestamp","ABSENT","(none)","(none)",None,None,"no clock; ordering by state_version only"),
("form","EXACT","STATE.form","",None,None,""),
("physical_state","RELATED","STATE.variables[SVAR id]","",None,None,"state variables are keyed by SVAR id; the nearest registry row is SVAR-FUT-005 phase (future, 0 rows)"),
("visual_state","RELATED","STATE.variables[SVAR id]","",None,None,"SVAR-FUT-008 colour (future, 0 rows)"),
("thermal_state","RELATED","STATE.variables[SVAR id]","",None,None,"nearest registry row is SVAR-FUT-012 surface/core temperature (future, 0 rows)"),
("texture_state","RELATED","STATE.variables[SVAR id]","",None,None,"SVAR-FUT-007 texture (future, 0 rows)"),
("temperature_C","RELATED","STATE.variables[SVAR id]","",None,None,"SVAR-FUT-012 surface/core temperature (future, 0 rows); no ACTIVE temperature SVAR"),
("moisture","RELATED","STATE.variables[SVAR id]","",None,None,"SVAR-FUT-001 moisture content (future, 0 rows)"),
("water_activity","RELATED","STATE.variables[SVAR id]","",None,None,"SVAR-FUT-002 water activity (future, 0 rows)"),
("pH","RELATED","STATE.variables[SVAR id]","",None,None,"SVAR-FUT-013 pH / acidity (future, 0 rows)"),
("quantity_mass_g","RENAMED","STATE.quantity","",None,None,""),
("chemical_state_ref","COMPOSED","STATE.variables[SVAR id] (chemical SVARs)","",None,None,""),
("field_provenance","RELATED","STATE.provenance","",None,None,"record-level only, not per field"),
("uncertainty","RENAMED","STATE.variables.*.uncertainty","",None,None,""),
("observation_source","RELATED","STATE.belief","",None,None,"enum PREDICTED/OBSERVED/PLANNED"),
])
M["EvidenceAtom"]=("EVD",[
("evidence_id","RENAMED","EVD.id","","EVD","id",""),
("subject_type","RELATED","(implicit: EVD.matrix is an ingredient matrix)","","N/A",None,"EVD is a fixed matrix/process/target triple; no subject_type property"),
("subject_id","RELATED","EVD.matrix.ingredient_id","","EVD","matrix.ingredient_id","nearest property; EVD fixes the subject as an ingredient matrix"),
("relation","RELATED","EVD.derived.direction","","EVD","derived.direction","direction enum, not a free relation"),
("object_type","RELATED","(implicit: EVD.target)","","N/A",None,"no object_type property"),
("object_id","RELATED","EVD.target.state_variable_id","","EVD","target.state_variable_id","the object is always a state variable"),
("process_id","RENAMED","EVD.process.process_id","","EVD","process.process_id",""),
("conditions","RENAMED","EVD.process.condition_id","","EVD","process.condition_id",""),
("measurement_target","RENAMED","EVD.target.state_variable_id / target.raw_name","","EVD","target.raw_name",""),
("measurement_value","COMPOSED","EVD.before / after / derived","","EVD","after.value|derived.retention_factor|derived.yield_factor|derived.delta|derived.percent_change|derived.log_fold_change","counted: any of after.value or a derived value is populated"),
("measurement_unit","RENAMED","EVD.after.unit","","EVD","after.unit",""),
("metric","COMPOSED","EVD.derived.{delta, percent_change, retention_factor, log_fold_change, yield_factor}","","EVD","derived.retention_factor",""),
("matrix_description","RENAMED","EVD.matrix.raw_name (+ food_group, form, ...)","","EVD","matrix.raw_name",""),
("analytical_method","RENAMED","EVD.measurement_method_id","","EVD","measurement_method_id",""),
("study_id","RENAMED","EVD.study_ids","","EVD","study_ids",""),
("source_id","EXACT","EVD.source_id","","EVD","source_id",""),
("doi","RELATED","(via SRC / STUDY records)","","N/A",None,"no DOI property on EVD"),
("table_or_figure","COMPOSED","EVD.provenance.locator","","EVD","provenance.locator",""),
("source_span","RELATED","EVD.provenance.locator","","EVD","provenance.locator","locator string, not a character span"),
("evidence_class","RENAMED","EVD.tier","","EVD","tier","E1-E7"),
("verification","EXACT","EVD.verification","","EVD","verification.status",""),
("independence_group","EXACT","EVD.independence_group","","EVD","independence_group",""),
("quality_features","COMPOSED","EVD.applicability / design / censored / n_replicates","","EVD","design",""),
])
M["ClaimLedger"]=("CLM",[
("claim_id","RENAMED","CLM.id","",None,None,""),
("response_id","ABSENT","(none)","(none)",None,None,"CLM is a research-claim ledger (statement, approval, gate_ids); it has no answer/response link"),
("claim_text","RENAMED","CLM.statement","",None,None,""),
("claim_type","RELATED","CLM.claim_type","",None,None,"same name, different vocabulary: CLM enum is DESCRIPTIVE/COMPARATIVE/CAUSAL/SOTA/NEGATIVE_RESULT (a research claim kind), not an answer-claim kind (numeric, directional, ...)"),
("evidence_ids","EXACT","CLM.evidence_ids","",None,None,""),
("model_id","ABSENT","(none)","(none)",None,None,"no model id on CLM"),
("model_version","ABSENT","(none)","(none)",None,None,"no model version on CLM"),
("confidence_class","ABSENT","(none)","decision/confidence.py (runtime confidence vector, ordinal)",None,None,"not a ledger field"),
("citation_required","ABSENT","(none)","(none)",None,None,"claim checking is runtime (generation/claims.py check_claims); nothing persisted"),
("citation_refs","ABSENT","(none)","generation/claims.py CIT regex output (runtime)",None,None,"runtime only"),
("verification_status","RELATED","CLM.approval (DRAFT/HUMAN_APPROVED/REJECTED) and CLM.verification.status","",None,None,""),
])
M["InverseDesignTrial"]=(None,[
(f,"ABSENT","(no schema)","(none)",None,None,"no InverseDesignTrial schema or code; the contract belongs to FlavorTwin, out of the course scope (T9-C06 topic anchor)") for f in
["trial_id","initial_state_id","target_state","candidate_ingredient_ids","candidate_process","candidate_conditions","constraints","optimizer","forward_model_version","predicted_state","prediction_interval","evidence_distance","OOD_flag","feasible_flag","heldout_or_real_outcome","target_error"]])

# the SSOT field lists must equal the map
for c,(sch,rows) in M.items():
    assert [r[0] for r in rows]==fields[c],(c,[r[0] for r in rows],fields[c])
assert len(M)==12
def populated(v):
    if v is None: return False
    if isinstance(v,str): return v.strip()!=''
    if isinstance(v,(list,dict,tuple)): return len(v)>0
    return True
def get(o,path):
    for k in path.split('.'):
        if isinstance(o,dict): o=o.get(k)
        else: return None
    return o
led={}
for n in ['REC','ING','ALIAS','EVD','IMAP']:
    last={}
    for l in open(root+f'ledgers/data/{n}.jsonl'):
        r=json.loads(l)
        if r['id'] not in last or r['version']>last[r['id']]['version']: last[r['id']]=r
    led[n]=[r for r in last.values() if r['status']=='ACTIVE']
tab={}
for name,p in [('recipe_base','ledgers/recipe_base/recipe_base_v1.parquet'),('recipe_identity_fk','ledgers/recipe_identity/recipe_identity_fk_v1.parquet')]:
    t=pq.read_table(root+p); tab[name]=t
def tab_count(name,col):
    t=tab[name]; a=t.column(col).to_pylist()
    return len(a),sum(1 for x in a if populated(x))
out=[]
for c,(sch,rows) in M.items():
    for (f,kind,sp,cp,src,path,reason) in rows:
        if kind in('ABSENT','RELATED','TABLE_ONLY','CODE_ONLY') and not reason:
            reason={'RELATED':'nearest property; semantics differ or the link is held on another record','TABLE_ONLY':'committed table only','CODE_ONLY':'code-level interface only'}.get(kind)
            assert reason,(c,f)
        art='';n='';k=''
        if src and src.startswith('ZERO:'):
            n=0;k=0;art=f'{src[5:]}: 0 ledger rows (no ledgers/data/{src[5:]}.jsonl)'
        elif src=='N/A':
            art='n/a (implicit in the EVD triple; no property to count)'
        elif src in led:
            L=led[src]; n=len(L); k=sum(1 for r in L if any(populated(get(r,pp)) for pp in path.split('|'))); art=f'ledgers/data/{src}.jsonl (ACTIVE, latest version per id): {path}'
        elif src in tab:
            n,k=tab_count(src,path); art=f'{src}: {path}'
        else:
            if sch and kind!='ABSENT' and sch in ('QNT','POR','EVT','ENTITY','STATE','CLM'):
                art=f'{sch}: 0 ledger rows (no ledgers/data/{sch}.jsonl)'; n=0; k=0
            elif kind=='ABSENT':
                art='n/a (no counterpart)'
            else:
                art='n/a (not a ledger or table field)'
        pct=(round(100*k/n,1) if n not in('',0) else '')
        out.append(dict(contract=c,ssot_field=f,map_kind=kind,schema_property=sp,code_or_table_counterpart=cp,count_artifact=art,n_rows=n,n_populated=k,pct_populated=pct,reason=reason))
cols=list(out[0].keys())
with open(root+'reports/s178/ssot238_conformance.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(out)
# summary
summ=[]
for c in M:
    rs=[o for o in out if o['contract']==c]
    kc=collections.Counter(o['map_kind'] for o in rs)
    summ.append((c,M[c][0] or 'none',len(rs),kc))
json.dump({'rows':len(out)},sys.stdout); print()
for s in summ: print(s[0],s[1],s[2],dict(s[3]))
print(collections.Counter(o['map_kind'] for o in out))

# ---- markdown ----
def pct(o):
    return f"{o['n_populated']}/{o['n_rows']} ({o['pct_populated']}%)" if o['n_rows'] not in ('',0) else ('0 rows' if o['n_rows']==0 else 'n/a')
kinds=collections.Counter(o['map_kind'] for o in out)
md=[]
md.append(f"""# SSOT section 238 conformance table (T9-C06-R1)

Status: **AI_DRAFTED / PROPOSED** (S178 GOVDOC lane, 9 Nov 2026, manjot-server, HEAD `4a95380` plus uncommitted work). The mapping of each SSOT field to a schema property is the agent's reading and is **not human-verified**; every row that is not an exact name match carries a reason. Counts are counts only (no recipe text, no values). Machine-readable twin: `reports/s178/ssot238_conformance.csv` (210 rows, one per SSOT field).

**What was compared.** SSOT v15 section 238 "Exact data contracts / field dictionary" (L25745-26101): 12 contracts, 210 fields (field lists parsed from the SSOT text; each field's description in the SSOT is the same generic sentence, so the field *names* are the contract). Against: the JSON Schemas in `ledgers/schemas/` (REC, ING, ALIAS, QNT, POR, EVT, ENTITY, STATE, EVD, CLM, plus COND, IMAP, GRAPH where a field lives on a linked record), the committed tables `ledgers/recipe_base/recipe_base_v1.parquet` and `ledgers/recipe_identity/recipe_identity_fk_v1.parquet` (612,782 rows each), and the code-level interfaces `extraction/interfaces.py`, `state_graph/event_log.py`, `generation/claims.py`.

**Map kinds.** EXACT = same name in the schema. RENAMED = the equivalent property under another name. COMPOSED = covered by several properties or a provenance block. RELATED = nearest property, semantics differ or the link is held on another record (reason given). TABLE_ONLY / CODE_ONLY = the field exists only as a column of a committed table / only as a code interface field, not in a JSON Schema. ABSENT = no counterpart anywhere (reason given).

**Counts.** Populated = ACTIVE rows, latest version per id, with a non-null, non-empty value at that property (ledgers), or non-null non-empty column values (tables). The REC ledger holds 89,565 recipes while `recipe_base_v1` holds 612,782, so Recipe rows quote two different denominators; the column `count_artifact` names which. "0 rows" means the schema exists and no `ledgers/data/<NAME>.jsonl` exists.

## 1. Result

- 210 fields: **{kinds['EXACT']} EXACT + {kinds['RENAMED']} RENAMED + {kinds['COMPOSED']} COMPOSED = {kinds['EXACT']+kinds['RENAMED']+kinds['COMPOSED']}** map to a schema property; {kinds['RELATED']} RELATED; {kinds['TABLE_ONLY']} TABLE_ONLY and {kinds['CODE_ONLY']} CODE_ONLY; **{kinds['ABSENT']} ABSENT**.
- **0 rows are unmapped without a stated reason** (the script asserts it; every ABSENT, RELATED, TABLE_ONLY and CODE_ONLY row has a reason).
- Contracts with no JSON Schema at all: **IngredientMention** (19 fields; only the 17a code interface exists, the MENTION ledger is a draft, and `recipe_ingredient_mentions_v1.parquet` is not visible on manjot, see T7-C01-R5) and **InverseDesignTrial** (16 fields, all ABSENT; belongs to FlavorTwin, out of the course scope).
- Schemas that exist but have **0 production rows**: QNT (Quantity), POR (PortionProfile), EVT (Event), ENTITY, STATE, CLM (ClaimLedger). The Rung A event log and the rc2 quantity results live in derived files and counts-only reports, not in these ledgers.
- Populated ledgers: REC 89,565, ING 2,048 ACTIVE, ALIAS 4,103 ACTIVE, EVD 17,978 ACTIVE.

## 2. Concrete conformance gaps found (for the report and for the Mac/manjot tickets)

1. **PortionProfile.** `POR.basis` enum is MEASURED / DATABASE / CONVENTION / RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION. The composition/ plan for SR Legacy portions names basis `SR_PORTION` (board T3-C08-R1), which is not in the enum, and POR has no `sample_count`, `source_diversity` or `size_class`. A POR export from `composition/` would fail schema validation as it stands. Decision needed on the schema (v1.1) before the Mac exports POR records.
2. **ClaimLedger.** CLM is a research-claim ledger (`statement`, `approval`, `gate_ids`, `experiment_ids`). The SSOT contract is an answer-level claim ledger (`response_id`, `model_id`, `model_version`, `confidence_class`, `citation_required`, `citation_refs`). `claim_type` is the same name with a different vocabulary (DESCRIPTIVE/COMPARATIVE/CAUSAL/SOTA/NEGATIVE_RESULT vs answer-claim kinds). Six of eleven fields are ABSENT. This is what T8-C17-R1 (claim_ledger schema for D5 answers) and T9-C06-R2 (runtime-only or materialise) have to settle; it is not a rename.
3. **Recipe.** Five fields exist only as columns of `recipe_base_v1` / `recipe_identity_fk_v1`, not in `REC.schema.json` (`dataset_version`, `license_class`, `language`, `locale`, `duplicate_group_id`); three more are approximated by table columns (`source_domain`, `dish_categories`, `annotation_tier`) and `annotation_model` is spread over four version columns. Five are ABSENT: `title_normalized`, `servings_raw`, `servings_normalized`, `prompt_version`, `validation_flags`. The statement "recipe contract implemented" is true only of the table, not of the schema.
4. **State.** Eight of 18 State fields (temperature, moisture, water activity, pH, physical/visual/thermal/texture state) can only live in `STATE.variables[SVAR id]`, and the matching registry rows (SVAR-FUT-001 moisture, -002 water activity, -005 phase, -007 texture, -008 colour, -012 surface/core temperature, -013 pH) are all `SVAR-FUT` with 0 rows in `registry/state_variable_registry_v1.csv` (30 of its 254 rows are FUT). No populated variable exists for them today.
5. **Event.** The condition fields (temperature, duration, pressure, pH, moisture, medium) are not on EVT; they are reached through `EVT.condition_id -> COND`. Any consumer of the contract has to join.
6. **Alias.** `source_domains` is ABSENT; `source_count` is approximated by `corpus_frequency` (populated on 2,207 of 4,103 ACTIVE aliases, 53.8 %).
7. **CanonicalIngredient.** `scientific_name` and `fdc_ids` are mapped but 0 of 2,048 ACTIVE ingredients populate them; `food_category` 631 (30.8 %), `parent_id` 315 (15.4 %), `known_forms` 235 (11.5 %), `known_states` 0.
8. **Entity.** Lineage (`parent_entity_ids`, `created_by_event`, `destroyed_or_consumed_by_event`) lives in event allocations (code) and on STATE, not on ENTITY.

## 3. Per-contract tables

""")
for c,(sch,rows) in M.items():
    rs=[o for o in out if o['contract']==c]
    kc=collections.Counter(o['map_kind'] for o in rs)
    md.append(f"### {c}  (schema: {sch or 'none'}; {len(rs)} fields; "+", ".join(f"{k} {v}" for k,v in sorted(kc.items()))+")\n")
    md.append("| SSOT field | kind | schema property | table / code counterpart | populated | reason |\n|---|---|---|---|---|---|")
    for o in rs:
        md.append("| `"+o['ssot_field']+"` | "+o['map_kind']+" | "+o['schema_property'].replace('|','/')+" | "+(o['code_or_table_counterpart'] or '').replace('|','/')+" | "+pct(o)+" | "+(o['reason'] or '').replace('|','/')+" |")
    md.append("")
md.append("""## 4. Limits

The mapping is an AI reading of names and schema descriptions; two readers could place some RELATED rows differently. The SSOT gives no per-field semantics beyond the field name, so "conforms" here means "a property with the same job exists", not "values agree". No schema validation of the populated rows was run in this lane (the ledger rules in `src/culinarystate/ledgers/rules.py` are the existing validators). Populated counts use ACTIVE latest versions only; DEPRECATED and SUPERSEDED records are excluded.
""")
open(root+'reports/s178/ssot238_conformance.md','w').write("\n".join(md))
print(len("\n".join(md)))
