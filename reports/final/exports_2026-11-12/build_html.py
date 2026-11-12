import sys,json,hashlib,re,html
from pathlib import Path
sys.path.insert(0,'/private/tmp/culinarystate-export-deps')
import markdown
out=Path('reports/final/exports_2026-11-12');out.mkdir(exist_ok=True)
report=Path('reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md');deck=Path('reports/final/SLIDES_DRAFT_S179_2026-11-11.md')
base='''body{font:11pt/1.45 Arial,sans-serif;color:#17283b;margin:0;background:#eef2f6} main{max-width:1000px;margin:auto;background:white;padding:44px}h1,h2,h3{color:#163c5b;line-height:1.2} h1{font-size:27pt}h2{margin-top:28px;font-size:19pt}h3{font-size:14pt}a{color:#235e8b}table{border-collapse:collapse;width:100%;font-size:9pt;margin:16px 0}td,th{border:1px solid #bdc9d4;padding:7px;vertical-align:top}th{background:#e4edf4;text-align:left}code{font-size:8.7pt;overflow-wrap:anywhere}pre{white-space:pre-wrap}li{margin:6px 0}.banner{background:#fff0cc;border-left:5px solid #ac7d00;padding:12px 16px;font-size:10pt}.footer{font-size:9pt;color:#526275} @media print{body{background:white}main{max-width:none;padding:0}a{color:inherit;text-decoration:none} h1,h2,h3{break-after:avoid}tr{break-inside:avoid}.banner{print-color-adjust:exact} @page{size:A4;margin:18mm}}'''
exports=[]
for source,name,slides in [(report,'CulinaryState_report_DRAFT',False),(deck,'CulinaryState_slides_DRAFT',True)]:
 text=source.read_text();parts=re.split(r'^---\s*$',text,flags=re.M) if slides else [text]
 content=[]
 for i,part in enumerate(parts):
  body=markdown.markdown(part,extensions=['tables','fenced_code'])
  content.append(f'<section class="slide">{body}<p class="footer">Draft · 12 November 2026 · {i+1}/{len(parts)}</p></section>' if slides else body)
 css=base
 if slides:css+=''' .slide{box-sizing:border-box;min-height:650px;padding:40px 46px;margin-bottom:30px;border-top:8px solid #275a7a;background:white}.slide h1{font-size:29pt}.slide p,.slide li{font-size:15pt}.slide code{font-size:11pt}.slide .footer{font-size:10pt}.slide table{font-size:12pt}main{padding:0;background:transparent} @media print{@page{size:320mm 200mm;margin:0}main{padding:0}.slide{height:200mm;min-height:0;margin:0;padding:14mm 18mm;break-after:page;overflow:visible}.slide:last-child{break-after:auto}.slide p,.slide li{font-size:15pt}.slide h1{font-size:27pt}}'''
 banner='<div class="banner">DRAFT FOR AUTHOR REVIEW · NON_CITABLE · NO_HUMAN_SIGNOFF_D085 · Contributions and presentation details pending.</div>'
 doc='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+name+'</title><style>'+css+'</style><main>'+(banner if not slides else '')+''.join(content)+'</main></html>'
 target=out/(name+'.html');target.write_text(doc)
 exports.append({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'html':str(target),'html_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'slides':len(parts) if slides else None})
print(json.dumps(exports))
