#!/usr/bin/env python3
"""Bind draft FDA table rows to a paginated historical consistency copy.

The primary archive/legacy edition is not replaced; no pH values are changed.
Requires PyMuPDF, used locally from the temporary PDF-inspection directory.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',type=Path,required=True);parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out_dir.exists():parser.error('New output directory required')
    import fitz
    normal=lambda s:re.sub(r'\s+',' ',s).casefold().strip()
    pages=[normal(page.get_text()) for page in fitz.open(args.pdf)];joined=' '.join(pages)
    offsets=[];offset=0
    for page in pages:offsets.append(offset);offset+=len(page)+1
    source=ROOT/'registry/food_ph_fda_draft_v1.csv';rows=list(csv.DictReader(source.open()));cursor=0;found=[]
    for row in rows:
        candidates=[]
        for separator in [' ','']:
            needle=normal(row['item_raw']+separator+row['ph_raw']);position=joined.find(needle,cursor)
            if position>=0:candidates.append((position,len(needle),separator))
        if candidates:
            position,length,separator=min(candidates)
            page=max(i+1 for i,start in enumerate(offsets) if start<=position)
            cursor=position+length;status='EXACT_NORMALIZED_FIELDS' if separator else 'EXACT_FIELDS_ADJACENT_IN_PDF'
        else:page=None;status='NOT_LOCATED'
        found.append({'ph_id':row['ph_id'],'registry_row_sha256':hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest(),
                      'matching_copy_pdf_page':page,'match_status':status,'verification_status':'AI_FIDELITY_CHECK_NOT_HUMAN_VERIFIED'})
    args.out_dir.mkdir(parents=True)
    index=args.out_dir/'draft_row_page_locators.csv'
    with index.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(found[0]));w.writeheader();w.writerows(found)
    report={'record':'FDA_DRAFT_PAGINATED_COPY_FIDELITY_INDEX','created_at_utc':datetime.now(timezone.utc).isoformat(),
            'labels':['AI_PRECHECKED','NON_CITABLE','NO_HUMAN_SIGNOFF_D085'],'scientific_gate_pass':False,
            'source_registry':str(source.relative_to(ROOT)),'source_registry_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'matching_copy_url':'https://riverstonehealth.org/wp-content/uploads/FDA-Approximate-pH-of-Foods.pdf',
            'matching_copy_pdf_sha256':hashlib.sha256(args.pdf.read_bytes()).hexdigest(),'matching_copy_pages':len(pages),
            'rows':len(found),'located':sum(r['matching_copy_pdf_page'] is not None for r in found),
            'index_sha256':hashlib.sha256(index.read_bytes()).hexdigest(),'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'original_pH_values_modified':False,'crosswalk_status':'AI_DRAFTED_UNVERIFIED; no promotion to human-reviewed',
            'limitations':['April2007 historical FDA document consistency copy hosted by a third party; not a new primary-source-of-record adoption.',
                        'Original2003 legacy479-row registry and archive references remain unchanged; edition/row-count differences are not silently merged.',
                        'Source row numbers, normalized item/raw-value strings and order are checked; no pH measurement, source methodology or food-safety advice is validated.',
                        'Primary archive was not retrievable by the web tool; no JavaScript archive challenge was solved or bypassed.',
                        'Member pH flags remain exploratory/as-listed, not mixture pH or process applicability.']}
    with (args.out_dir/'manifest.json').open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('Located',report['located'],'of',report['rows'],'draft rows in',len(pages),'pages')


if __name__=='__main__':main()
