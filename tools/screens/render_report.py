"""Render the current submission report using the pinned Markdown version."""
import argparse
import html
import json
from pathlib import Path
import subprocess

import markdown

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "reports/final"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """
@page { size: A4; margin: 15mm 17mm 15mm; }
html { color:#231e19; background:white; }
body { font: 10.5pt/1.43 "Helvetica Neue", Arial, sans-serif; }
h1,h2,h3 { font-family: Georgia, serif; color:#231e19; break-after:avoid; line-height:1.18; }
h1 { font-size:30pt; margin:0 0 10pt; }
h2 { font-size:19pt; margin:19pt 0 6pt; border-top:1px solid #c5c2bb; padding-top:10pt; }
h3 { font-size:13pt; margin:13pt 0 4pt; }
p { margin:0 0 8pt; orphans:3; widows:3; }
table { border-collapse:collapse; width:100%; font-size:9.3pt; margin:8pt 0 12pt; }
th,td { text-align:left; padding:4pt 6pt; border-bottom:1px solid #dcd9d3; vertical-align:top; }
th { color:#1b36c4; }
tr, img, .story, .business { break-inside:avoid; }
img { max-width:100%; max-height:95mm; object-fit:contain; }
code { font: 8.3pt Menlo, monospace; overflow-wrap:anywhere; }
a { color:#1b36c4; overflow-wrap:anywhere; }
.story { margin:9pt 0 12pt; border:1px solid #c5c2bb; padding:9pt; }
.answers { display:grid; grid-template-columns:1fr 1fr; gap:9pt; }
.answers section { padding:7pt; background:#f7f6f2; white-space:pre-wrap; }
.story small { display:block; margin-top:6pt; overflow-wrap:anywhere; }
.business { break-before:page; }
"""


def story_html(data):
    parts = []
    for row in data["stories"]:
        title = {"tomato-a-d": "Tomato A–D", "carrots": "Carrots came out mushy",
                 "tomatoes": "Tomatoes · vitamin C", "safety": "Chicken · is it safe?"}[row["id"]]
        if row["status"] == "SIGNED_SNAPSHOT":
            # Full A–D text remains in the saved story sheet. Show one paired case here.
            selected = json.loads((ROOT / row["source_run"]).read_text())["rows"][0]
            plain, system = selected["plain_model"], selected["culinarystate"]
            why = row["why"] + " The saved story sheet includes all four verbatim pairs."
        else:
            plain, system, why = row["plain_model"], row["culinarystate"], row["why"]
        esc = html.escape
        values = ", ".join(str(v) + " [no source]" for v in row["unsourced_values"])
        citation = f'{row["source_run"]} · {row["model"]} · {row["date"]}' if row["source_run"] else "Live answer capture pending."
        parts.append(f'<div class="story"><h3>{esc(title)}</h3><p><b>Question.</b> {esc(row["question"])}</p>'
                     f'<div class="answers"><section><b>Plain model</b>\n{esc(plain)}</section>'
                     f'<section><b>CulinaryState</b>\n{esc(system)}</section></div>'
                     f'<p><b>Why.</b> {esc(why)} {esc(row["limit"])}</p>'
                     + (f'<p>Verifier annotation: {esc(values)}</p>' if values else "")
                     + f'<small>{esc(citation)}</small></div>')
    return "\n".join(parts)


def build(out):
    if markdown.__version__ != "3.4.1":
        raise RuntimeError("Markdown 3.4.1 is required for this export.")
    md = (FINAL / "FINAL_REPORT_DRAFT_S179_2026-11-11.md").read_text()
    story = story_html(json.loads((FINAL / "screens/answer_panels.json").read_text()))
    business = (FINAL / "deck/BUSINESS_PROPOSAL_OPTIONAL_2026-11-20.md").read_text()
    business = business.split("\n", 1)[1]
    deployment = FINAL / "DEPLOYMENT_2026-11-20.json"
    url = json.loads(deployment.read_text()).get("url") if deployment.exists() else None
    public = f'<a href="{html.escape(url, quote=True)}">{html.escape(url)}</a>' if url else "Production deployment pending."
    content = markdown.markdown(md, extensions=["tables", "fenced_code"])
    content = content.replace("<!-- STORY_PANELS -->", story).replace("<!-- PUBLIC_URL -->", public)
    content = content.replace("<!-- BUSINESS_PROPOSAL -->", markdown.markdown(business))
    content = content.replace("<h2>Appendix. Business proposal</h2>", '<h2 class="business">Appendix. Business proposal</h2>')
    tmp = out.with_suffix(".html")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><title>CulinaryState report</title>'
                   f'<base href="{FINAL.as_uri()}/"><style>{CSS}</style><body>{content}</body></html>', encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", tmp.as_uri()], check=True)
    tmp.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=FINAL / "CulinaryState_final_report.pdf")
    build(parser.parse_args().out.resolve())
