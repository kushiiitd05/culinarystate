"""Build D1 precheck CSV. AI_DELEGATED_D085 / AI_PRECHECKED / NOT_HUMAN_VERIFIED. Seed 181."""
import csv, json, random, re, sys
SEED = 181
PAPER_TXT = sys.argv[1]
OUT = 'reports/s181/human_audit/D1_literature_rows_precheck.csv'
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
LABEL = 'AI_DELEGATED_D085 · AI_PRECHECKED · NOT_HUMAN_VERIFIED'
rows = []

def base(**k):
    d = dict(audit_no='', selected_40='', row_origin='', evidence_id='', ingredient='', process='', conditions_as_recorded='',
             target='', value_as_recorded='', unit_as_recorded='', source_citation='', doi='', url='', local_copy='',
             source_locator='', what_ai_checked='', ksh_AI_precheck='', prv_AI_precheck='', chef_AI_precheck='',
             resolved_AI_precheck='', resolution_rule='KSH_GOVERNS_AI_DELEGATED_D085_D139', chef_differs_from_ksh='NO',
             ksh_prv_differ='NO', label=LABEL, kush_HUMAN_verdict='', parv_HUMAN_verdict='', chef_HUMAN_verdict='',
             human_locator='', human_note='')
    d.update(k); return d

# ---- 1. AA kinetics CAL rows (local PDFs + text) ----
CIT = {'AAK-01': 'Food Science and Technology (Campinas) 2017, rosehip nectar thermal degradation kinetics',
       'AAK-06': 'African Journal of Food Science 2014/15, watermelon juice vitamin C/lycopene kinetics',
       'AAK-09': 'Innovative Food Science & Emerging Technologies 2018, mango blanching kinetics',
       'AAK-11': 'Jurnal Natural 2023, fig fruit juice ascorbic acid kinetics'}
txt = {}
for r in csv.DictReader(open('annotation/aa_pilot/aa_pilot_verify_CAL_v1_Kush.csv', encoding='utf-8-sig')):
    c = r['candidate_id']
    t = txt.setdefault(c, norm(open(f'data/raw/aa_pilot/{c}.txt', errors='ignore').read()))
    q = norm(r['span_quote']); found = q in t
    val = r['value']
    nums = re.findall(r'\d+\.?\d*', q.replace(',', '.'))
    if c == 'AAK-01' and r['row_type'] == 'K_AT_T':
        num_ok = len(nums) > 1 and abs(float(nums[1]) * 1e-3 - float(val)) < 1e-9
        how = f"quote '{q}' found verbatim in local text; table header k x10^3 (1/min), so {nums[1]}e-3 = {val}"
    else:
        num_ok = any(abs(float(n) - float(val)) < 1e-9 for n in nums) if r['row_type'] == 'K_AT_T' or c != 'AAK-01' else None
        how = f"quote '{q[:70]}' found verbatim in local text; recorded value {val} appears in the quote" if num_ok else \
              f"quote '{q[:70]}' found verbatim in local text; the quote itself does not contain the number {val} - value sits later in the same sentence, not machine-compared"
    if not found:
        ksh = prv = 'AMBIGUOUS: recorded span not found verbatim in local text extraction'
    elif num_ok:
        ksh = prv = 'MATCHES_SOURCE'
    else:
        ksh = prv = 'AMBIGUOUS: span located, number not machine-compared (read the sentence)'
    chef = 'NOT_APPLICABLE'
    if c == 'AAK-06' and found:
        prv = 'AMBIGUOUS: number matches, but assay is iodine titration (not ascorbic-acid specific), so the target identity is weaker than the row implies'
    if c == 'AAK-11' and found:
        prv = 'AMBIGUOUS: number matches (source prints the slope as negative; row stores magnitude), but k barely changes 30-90 C, which is implausible for thermal AA loss'
    if c == 'AAK-09' and found and r['row_type'] == 'K_AT_T':
        how += '; column identity (2nd number = L-AA, 1st = AAO enzyme) rests on the earlier AI note, table header order not re-read here'
        ksh = 'AMBIGUOUS: number present in source row; which column is L-ascorbic acid must be read off the table header'
    if r['row_id'] == 'AAP-014':
        chef = 'CONDITION_NOT_COOKING: 30 C holding is storage/room temperature, not a cooking step'
    rows.append(base(row_origin='AA_PILOT_CAL_v1 (annotation/aa_pilot/aa_pilot_verify_CAL_v1_Kush.csv); NOT an EVD ledger row',
        evidence_id=r['row_id'], ingredient=r['matrix'], process=f"heat ({r['medium_container']})",
        conditions_as_recorded=f"T={r['T_C']} C; {r['T_location_comeup']}; time {r['time_range']}; order {r['order']}; assay {r['assay']}",
        target=f"{r['analyte_basis']} - {r['row_type']}", value_as_recorded=val, unit_as_recorded=r['unit'],
        source_citation=CIT[c], doi=r['doi'], url='https://doi.org/' + r['doi'], local_copy=f'data/raw/aa_pilot/{c}.pdf',
        source_locator=r['span_locator'], what_ai_checked=how, ksh_AI_precheck=ksh, prv_AI_precheck=prv, chef_AI_precheck=chef,
        resolved_AI_precheck=ksh, _grp='AA', _paper=c))

# ---- 2. Andlauer 2003 rows (open author's version fetched, tables parsed) ----
lines = open(PAPER_TXT).read().split('\n')
def table(n):
    i = next(k for k, l in enumerate(lines) if l.strip().startswith(f'Table {n}:'))
    out = []
    for l in lines[i + 1:i + 40]:
        f = re.findall(r'\d+[.,]?\d*', l)
        if l.strip().startswith(('MW', 'SD')): break
        f = [float(x.replace(',', '.')) for x in f]
        if n == 6 and len(f) == 7: out.append((f[0], f[1], f[4]))           # raw, cooked small, cooked large (rows unnumbered)
        elif n != 6 and len(f) >= 13 and f[0] in (1, 2, 3, 4, 5): out.append((f[1], f[2], f[8]))
    return out
T = {('zucchini', 'rutin'): (2, 300), ('carrot', 'caffeoylquinic'): (3, 300), ('bean', 'rutinoside'): (4, 300),
     ('bean', 'rhamnoside'): (5, 300), ('potato', 'caffeic'): (6, 500)}
tabs = {n: table(n) for n in (2, 3, 4, 5, 6)}
and_rows = []
and_map = {}
for l in open('ledgers/data/EVD.jsonl'):
    if 'pe_pub:c38ce3d35fd6a54b' not in l: continue
    d = json.loads(l)
    if d.get('status') != 'ACTIVE': continue
    and_map[d['id']] = d
and_rows = list(and_map.values())
close = lambda a, b: abs(a - b) <= 0.0101
for d in sorted(and_rows, key=lambda x: x['id']):
    food = d['matrix']['raw_name']; tgt = d['target']['raw_name']; after_s = d['process']['modifiers'].get('food_after_raw', '')
    b = d.get('before', {}).get('value'); a = d.get('after', {}).get('value')
    key = next((k for k in T if k[0] in food.lower() and (k[1] in tgt.lower() or (k[1] == 'rutin' and 'rutinoside' in tgt.lower()))), None)
    m = re.search(r'Sample (\d)', after_s)
    pdef = d['process']['modifiers'].get('process_definition', '')
    common = dict(row_origin='EVD ledger (Phenol-Explorer 3.6 import)', evidence_id=d['id'], ingredient=food, process=d['process']['raw_name'],
        conditions_as_recorded=f"{after_s}; {pdef}", target=tgt, value_as_recorded=f"before {b} -> after {a}; RF {d['derived']['retention_factor'].get('value')}; yield {d['derived'].get('yield_factor', {}).get('value')}",
        unit_as_recorded=d.get('after', {}).get('unit', ''),
        source_citation='Andlauer W. et al. (2003) Influence of cooking process on phenolic marker compounds of vegetables. Int J Vitam Nutr Res 73(2):152-159',
        doi='10.1024/0300-9831.73.2.152', url="https://arodes.hes-so.ch/record/8584/files/Author%27s%20version.pdf (author's version, openly served)",
        local_copy='not stored in repo (fetched to session scratch only)', _grp='AND', _paper=food)
    if key is None or m is None or b is None or a is None:
        rows.append(base(**common, source_locator='Tables 2-6', what_ai_checked='row not mapped to a parsed table (Tables 2-6 parsed; e.g. potato chlorogenic acid is in a table not parsed in this pass)',
            ksh_AI_precheck='AMBIGUOUS: could not map row to a table cell by rule', prv_AI_precheck='AMBIGUOUS: could not map row to a table cell by rule',
            chef_AI_precheck='NOT_APPLICABLE', resolved_AI_precheck='AMBIGUOUS: could not map row to a table cell by rule')); continue
    n, grams = T[key]; s = int(m.group(1)); raw, small, large = tabs[n][s - 1]
    f = 100.0 / grams
    arm = 'small water volume' if close(a, small * f) or (not close(a, large * f) and close(a, small / 3)) else ('large water volume' if close(a, large * f) or close(a, large / 3) else None)
    cooked = small if arm == 'small water volume' else large
    ok = close(b, raw * f) and arm is not None and close(a, cooked * f)
    ok300 = n == 6 and close(b, raw / 3) and arm is not None and close(a, cooked / 3)
    how = (f"Table {n}, sample {s}: raw {raw} mg / {grams} g = {raw*f:.3f} mg/100 g; cooked ({arm}) {cooked} mg / {grams} g = {cooked*f:.3f} mg/100 g; "
           f"ledger {b} -> {a}")
    if n == 6: how += '; Table 6 rows are unnumbered in the source - sample order assumed top-to-bottom; source notes different whole tubers were used raw vs cooked'
    if ok:
        ksh = prv = 'MATCHES_SOURCE'
    elif ok300:
        ksh = (f"DIFFERS_FROM_SOURCE: source table is 'mg in 500 g fresh weight' -> raw {raw/5:.2f}, cooked {cooked/5:.2f} mg/100 g; "
               f"ledger has {b} and {a}, which equal the table figures divided by 300 g. Ratio after/before is unchanged")
        prv = 'AMBIGUOUS: absolute concentrations are on the wrong mass basis, but the retention ratio (the quantity the system uses) agrees with the source'
    else:
        ksh = prv = f"DIFFERS_FROM_SOURCE: expected before {raw*f:.2f}, after {small*f:.2f} (small) or {large*f:.2f} (large) mg/100 g; ledger {b} -> {a}"
    chef = 'NOT_APPLICABLE'
    if arm == 'small water volume':
        chef = (f"PROCESS_LABEL_QUESTIONED: {int(30 if n in (2,3) else 40 if n in (4,5) else 50)} mL water for {grams} g vegetable in a pot is sweating/steam-cooking, "
                "not boiling; ledger label says 'boiled' / 'cooked in boiling water'")
    rows.append(base(**common, source_locator=f'Table {n} (end of author version), sample row {s}', what_ai_checked=how,
        ksh_AI_precheck=ksh, prv_AI_precheck=prv, chef_AI_precheck=chef, resolved_AI_precheck=ksh))

# ---- 3. Other open-access-listed papers: primary source not opened by the agent ----
REASON = {'mdpi.com': 'publisher returned HTTP 403 to a plain scripted request; not retried or worked around',
          'tudublin': 'repository returned HTTP 403 to a plain scripted request; not retried or worked around',
          'sciencedirect': 'publisher PDF link; scripted download not attempted (handoff records refusals); needs a human browser',
          'wur.nl': 'link is a repository landing page, no direct PDF resolved; needs a human browser',
          'utad.pt': 'link returned an HTML application page, not the PDF; needs a human browser',
          'hdl.handle.net': 'handle resolves to a repository landing page, no PDF link found in the page; needs a human browser',
          'wiley': 'publisher PDF link; scripted download not attempted; needs a human browser',
          'doi.org': 'DOI resolves to a publisher landing page; full text not fetched; needs a human browser'}
for x in csv.DictReader(open('registry/evidence/human_review_pack_v1.csv')):
    if 'arodes' in x['paper_link']: continue
    why = next((v for k, v in REASON.items() if k in x['paper_link']), 'not opened')
    v = f'SOURCE_NOT_ACCESSIBLE: {why}'
    rows.append(base(row_origin=f"EVD ledger (Phenol-Explorer 3.6 import); registry/evidence/human_review_pack_v1.csv {x['pack']}",
        evidence_id=x['evd_id'], ingredient=x['food'], process=x['process'], conditions_as_recorded=x['sample_after_processing'],
        target=x['compound'], value_as_recorded=f"before {x['before_value']} -> after {x['after_value']}; RF {x['retention_factor']}; yield {x['yield_factor']}",
        unit_as_recorded=x['unit'], source_citation=x['citation'], doi=x['paper_doi'], url=x['paper_link'], local_copy='none',
        source_locator='not determined (source not opened)', what_ai_checked='nothing against the primary paper; earlier rule check only (RF = after/before x yield) per human_review_pack_v1 ai_suggestion=' + x['ai_suggestion'],
        ksh_AI_precheck=v, prv_AI_precheck=v, chef_AI_precheck='NOT_APPLICABLE', resolved_AI_precheck=v, _grp='PE', _paper=x['paper_doi']))

# ---- deterministic selection of the 40 ----
rng = random.Random(SEED)
sel = [r for r in rows if r['_grp'] == 'AA']                       # 16, all locally held kinetics rows
byfood = {}
for r in rows:
    if r['_grp'] == 'AND': byfood.setdefault(r['_paper'], []).append(r)
for food in sorted(byfood):                                          # 3 per food, seeded
    c = sorted(byfood[food], key=lambda r: r['evidence_id']); rng.shuffle(c); sel += c[:3]
need = 40 - len(sel)
bypaper = {}
for r in rows:
    if r['_grp'] == 'PE': bypaper.setdefault(r['_paper'], []).append(r)
papers = sorted(bypaper); rng.shuffle(papers)
i = 0
while need > 0:
    p = papers[i % len(papers)]; c = [r for r in sorted(bypaper[p], key=lambda r: r['evidence_id']) if r not in sel]
    if c: sel.append(rng.choice(c)); need -= 1
    i += 1
ids = {id(r) for r in sel}
rows.sort(key=lambda r: (id(r) not in ids, {'AA': 0, 'AND': 1, 'PE': 2}[r['_grp']], r['evidence_id']))
for n, r in enumerate(rows, 1):
    r['audit_no'] = n; r['selected_40'] = 'YES' if id(r) in ids else 'RESERVE'
    r['ksh_prv_differ'] = 'YES' if r['ksh_AI_precheck'] != r['prv_AI_precheck'] else 'NO'
    r['chef_differs_from_ksh'] = 'YES' if r['chef_AI_precheck'] != 'NOT_APPLICABLE' and r['ksh_AI_precheck'] == 'MATCHES_SOURCE' else 'NO'
cols = [k for k in rows[0] if not k.startswith('_')]
with open(OUT, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
import collections
for name, part in (('SELECTED_40', [r for r in rows if r['selected_40'] == 'YES']), ('ALL', rows)):
    print(name, len(part))
    for col in ('ksh_AI_precheck', 'prv_AI_precheck', 'chef_AI_precheck', 'resolved_AI_precheck'):
        print(' ', col, dict(collections.Counter(r[col].split(':')[0] for r in part)))
    print('  ksh_prv_differ', sum(r['ksh_prv_differ'] == 'YES' for r in part), 'chef_differs', sum(r['chef_differs_from_ksh'] == 'YES' for r in part),
          'by group', dict(collections.Counter(r['_grp'] for r in part)), 'papers', len({r['doi'] for r in part}))
