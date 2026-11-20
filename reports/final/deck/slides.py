"""Presentation story; source/claim limits are kept in NUMBER_SOURCES.md."""
import csv
import json
import os
from collections import Counter
from pathlib import Path


def build(g):
    globals().update(g)
    for fn in selected_slides():
        fn()


def selected_slides():
    if os.environ.get("CS_DECK_VARIANT") == "business-only":
        return [s14c_business]
    ordered = [s01_title, s02_problem, s02b_data, s03_compliance, s04_pipeline,
               s05_state, s06_compat, s07_tomato, s08_plainllm, s09_d4,
               s10_layer1, s11_ph, s12_ner, s12b_models, s14_app, s14b_live]
    if os.environ.get("CS_INCLUDE_BUSINESS", "1") == "1":
        ordered.append(s14c_business)
    return ordered + [s13_negative, s15_close]


def repo():
    return HERE.parents[2]


def read_json(relative):
    path = repo() / relative
    return json.loads(path.read_text()) if path.is_file() else None


def screen(s, stem, x, y, w, h, *, top=0, bottom=0):
    path = HERE.parent / "screens" / (stem + ".png")
    if path.is_file():
        from PIL import Image
        with Image.open(path) as image:
            iw, ih = image.size
        crop_h = ih * (1 - top - bottom)
        scale = min(w / iw, h / crop_h)
        shape = picture(s, str(path), x + (w - iw * scale) / 2,
                        y + (h - crop_h * scale) / 2, w=iw * scale, h=crop_h * scale)
        shape.crop_top = top
        shape.crop_bottom = bottom
        return True
    labelled_box(s, x, y, w, h,
                 "Capture pending.",
                 fill=AMBER_BG, line=AMBER, size=17)
    return False


def s01_title():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
    box(s, 0.6, 1.55, 0.09, 2.3, BLUE, BLUE)
    text(s, "CulinaryState", 0.9, 1.4, 11.5, 1.0, size=48, font=SERIF)
    text(s, "From recipe text to evidence-grounded cooking state", 0.9, 2.55, 11.3, 0.9,
         size=26, font=SERIF, color=SLATE)
    text(s, "State is recorded. Evidence is checked. Unsupported claims remain UNKNOWN.",
         0.9, 3.8, 11, 0.7, size=20)
    text(s, ["Group 17 · Kush Tokas · Parv Goyal",
             "Computational Gastronomy · IIIT Delhi · 25–26 Nov 2026"],
         0.9, 5.35, 11.3, 0.8, size=14, color=MUTED)
    source(s, "docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf; presentation dates: handoff/PARV_LATEST_PROMPT_2026-11-19.md")


def s02_problem():
    s = new_slide("Text retrieval does not tell us what is in the pot", "THE PROBLEM")
    labelled_box(s, 0.6, 1.8, 5.8, 3.5,
                 [R(("Text-only context", {"bold": True})), "",
                  "A nearby passage mentions boiled tomato."], size=22)
    labelled_box(s, 6.8, 1.8, 5.8, 3.5,
                 [R(("State-aware question", {"bold": True})), "",
                  "Was this pot mixed with salt, acid or fat?"], line=BLUE, size=22)
    caveat(s, "A retrieved number is not proof that the measurement applies to this recipe step.",
           0.6, 5.75, 12.0, 0.85, size=16)
    source(s, "docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf §1; reports/s181/snapshot_findings.md")


def s02b_data():
    s = new_slide("Five recipe families retain distinct licence boundaries", "DATA AND SOURCES")
    counts = Counter()
    with (repo() / "registry/recipe_source_usage_registry_v1.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            counts[row["source_family"]] += int(row["recipes_in_base"])
    specs = [("FOODCOM", "Food.com", "Restricted", "No raw export"),
             ("A1_BBC_GOOD_FOOD", "BBC Good Food", "Local only", "No raw export"),
             ("TASTESET", "TASTEset", "Dataset-specific", "Counts only"),
             ("WIKIBOOKS", "Wikibooks", "CC BY-SA", "Attributed reference"),
             ("GUTENBERG_SEGMENT", "Gutenberg segments", "US public-domain basis", "Policy applies")]
    rows = [["Recipe base v1", "Records", "Licence boundary", "Demo policy"]]
    rows += [[name, f"{counts[key]:,}", licence, policy] for key, name, licence, policy in specs]
    table(s, rows, 0.6, 1.55, [3.1, 1.7, 3.3, 4.0], row_h=0.61, size=16)
    text(s, "Evidence rows: USDA retention · Bognár · Phenol-Explorer. FDA pH and SR Legacy are additional resources.",
         0.6, 5.5, 12.0, 0.7, size=15)
    source(s, "registry/recipe_source_usage_registry_v1.csv (sum=612,782). Distinct populations: compiler=611,902; similar-title index=612,903; see reports/final/REPORT_EVIDENCE_REVIEW_2026-11-20.json. Licence status is not redistribution clearance.")


def s03_compliance():
    s = new_slide("All five contractual deliverables remain PARTIAL", "HONEST COMPLIANCE")
    rows = [["", "Evidenced", "Remaining limit"],
            ["D1", "17,978 evidence rows", "0 hand-verified literature rows"],
            ["D2", "Pilot fit on 7 rows from 2 papers", "0 comparable SIM-VAL rows"],
            ["D3", "40 dev-gold recipes; 30 sessions", "Gold not independent"],
            ["D4", "Three diagnostic metric families", "ECE not computable"],
            ["D5", "74 questions; Explorer", "Chef/peer review not performed"]]
    table(s, rows, 0.6, 1.5, [0.8, 5.3, 6.0], row_h=0.67, size=19)
    caveat(s, "AI pre-checks and an interactive demonstration do not close the human requirements.",
           0.6, 5.85, 12.1, 0.75, size=15)
    source(s, "reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md (17 Nov D3 correction); reports/s181/human_audit/REPORT_WORDING.md; reports/s181/d4_contract_metrics.json; reports/step10/aa_pilot_model_a_fit_D085.json")


def s04_pipeline():
    s = new_slide("The validator decides which model proposals can propagate", "ARCHITECTURE")
    top = ["Recipe", "Compiler", "Trigger?", "LLM proposal", "Typed IR", "Validator"]
    bot = ["State", "Evidence compiler", "Compatibility", "Claim packet", "Verbaliser", "Verifier"]
    w, h, gap, x0 = 1.82, 1.05, 0.24, 0.6
    for row, labels, y in ((0, top, 1.85), (1, bot, 4.05)):
        for i, label in enumerate(labels):
            x = x0 + (i if row == 0 else 5 - i) * (w + gap)
            box(s, x, y, w, h, AMBER_BG if "LLM" in label else SURF,
                AMBER if "LLM" in label else BORDER)
            text(s, label, x + 0.06, y + 0.05, w - 0.12, h - 0.1, size=17,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            if i < 5:
                arrow(s, x + w if row == 0 else x, y + h / 2,
                      x + w + gap if row == 0 else x - gap, y + h / 2)
    xr = x0 + 5 * (w + gap) + w / 2
    arrow(s, xr, 2.9, xr, 4.05)
    caveat(s, "Layer-1 licenses only alternative_group on VNEXT_ALTERNATIVE_SKIPPED. It cannot invent numeric state.",
           0.6, 5.7, 12.1, 0.9, size=15)
    source(s, "DECISIONS.md D-135/D-137; registry/rag/compatibility_axes_v1.csv; handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md §5")


def s05_state():
    s = new_slide("Food state records lineage, composition, conditions and provenance", "S_t = (G, C, Q, Y, P)")
    rows = [["Block", "Meaning"], ["G", "Lineage and structure"], ["C", "Composition"],
            ["Q", "Physical conditions"], ["Y", "Analyte and evidence state"], ["P", "Provenance"]]
    table(s, rows, 0.6, 1.5, [1.1, 6.3], row_h=0.65, size=21)
    labelled_box(s, 8.3, 1.65, 4.25, 3.6,
                 [R(("UNKNOWN ≠ zero", {"bold": True, "size": 25})), "",
                  "Missing fields retain their reason and basis."], line=BLUE, size=20)
    caveat(s, "Lineage vNext is diagnostic; no independent gold regression set exists.", 0.6, 5.8, 12.1, 0.8, size=16)
    source(s, "docs/final/FINAL_STATE_SCHEMA.md; DECISIONS.md D-134; reports/s181/snapshot_findings.md")


def s06_compat():
    s = new_slide("Unknown evidence context never becomes a MATCH", "COMPATIBILITY")
    rows = [["Outcome", "Meaning"], ["MATCH", "Recorded conditions agree"], ["MISMATCH", "Recorded conditions disagree"],
            ["UNKNOWN_IN_SOURCE", "Measurement omitted the axis"], ["UNKNOWN_IN_QUERY", "Recipe omitted the axis"]]
    table(s, rows, 0.6, 1.65, [4.7, 7.4], row_h=0.75, size=20)
    text(s, "13 axes: 9 implemented · 2 compiler-only · 2 schema-only", 0.6, 5.7, 12.0, 0.5, size=19, color=BLUE)
    source(s, "registry/rag/compatibility_axes_v1.csv; src/culinarystate/composition/evidence_compiler.py. Geometry is QUERY_ONLY because source rows have no geometry.")


def s07_tomato():
    s = new_slide("One added ingredient changes whether a number is permitted", "TOMATO A–D · SIGNED SNAPSHOT")
    if not screen(s, "04_compare_A-D", 0.6, 1.5, 12.1, 4.65):
        # The offline table is backed by the committed snapshot, never fabricated live output.
        for shape in list(s.shapes)[-2:]:
            shape._element.getparent().remove(shape._element)
        rows = [["Pot", "Added context", "Route", "Output"], ["A", "Water", "DIRECT", "95.0% [EVD-002765]"],
                ["B", "+ salt", "UNKNOWN", "No numeric transfer"], ["C", "+ vinegar", "UNKNOWN", "No numeric transfer"],
                ["D", "+ olive oil", "UNKNOWN", "No numeric transfer"]]
        table(s, rows, 0.6, 1.75, [1.0, 3.6, 3.0, 4.5], row_h=0.75, size=20)
    caveat(s, "Self-written scenarios. DIRECT is an engine decision about cited evidence, not scientific validation.",
           0.6, 6.05, 12.1, 0.65, size=13)
    source(s, "web/public/snapshot/scenarios/tomato-{a,b,c,d}.json; reports/s181/snapshot_findings.md; EVD-002765 (USDA-RETN-R6)")


def s08_plainllm():
    s = new_slide("The plain model was cautious in some replies and unsourced in others", "FROZEN SNAPSHOT BASELINE")
    rows = [["Observed reply behaviour", "Count"], ["Uncited 20–30% nutrient claims", "3 / 19"],
            ["Cautious replies failing wording checks", "At least 4"], ["Gold accuracy comparison", "Not available"]]
    table(s, rows, 0.6, 1.8, [8.9, 3.2], row_h=0.86, size=22)
    caveat(s, "One qwen2.5:7b-instruct prompt; no gold. Duration false positives and range parsing limit the verifier.",
           0.6, 5.65, 12.1, 1.0, size=16)
    source(s, "reports/s181/snapshot_findings.md: Plain-LLM baseline and Reading the baseline table honestly. This is not the later NIM live comparison.")


def s09_d4():
    s = new_slide("D4 is rule-based and uncalibrated, with post-hoc diagnostics", "MODEL_ASSISTED_GOLD · POST_HOC")
    rows = [["Metric", "Observed diagnostic"], ["Numeric-claim UCR", "B7 4/34; B2 24/43"],
            ["B7 partial AURC", "0.0977 over coverage 0.45–1.0"],
            ["B2 Recall@1 / 3 / 5", "0.20 / 0.3417 / 0.375; n=20"], ["ECE", "NOT_COMPUTABLE"]]
    table(s, rows, 0.6, 1.55, [4.7, 7.4], row_h=0.75, size=20)
    caveat(s, "Recall is condition-degenerate; confidence probabilities do not exist. B5T UCR is lower than B7.",
           0.6, 5.8, 12.1, 0.85, size=15)
    source(s, "reports/s181/d4_contract_metrics.json and .md; machine checkers, not human claim audit. H3 remains RULE_NOT_MET.")


def s10_layer1():
    s = new_slide("Quote-first prompting enabled grounded proposals", "LAYER-1 · DIAGNOSTIC_ONLY")
    picture(s, "fig_s180_2_layer1_surface.png", 1.05, 1.42, h=4.1)
    text(s, ["0 → 21 grounded proposals", "Quote-first prompting", "60 sealed cases", "No correctness gold"],
         7.2, 2.1, 5.4, 2.8, size=22, color=BLUE)
    caveat(s, "The 72B v3 run used 59 calls plus one repaired call. The 7B v3 run was sensitive to an abstention clause.",
           0.6, 5.85, 12.1, 0.8, size=14)
    source(s, "reports/s180/step7_FINAL_COMPARISON_2026-11-16.md; reports/s180/step7_arm_L72b_v3prompt_2026-11-15.json; figure MANIFEST.json")


def s11_ph():
    s = new_slide("Tomato spans the pH threshold, so no acidic label is inferred", "INGREDIENT BANDS, NOT LOT pH")
    picture(s, "fig_s180_4_ph_bands.png", 5.8, 1.4, h=5.35)
    text(s, ["Tomato: 4.3–4.9", "Threshold: 4.6", "Keep the interval.", "Lot pH stays UNKNOWN."],
         0.6, 2.0, 5.0, 3.3, size=25)
    caveat(s, "Ingredient crosswalk AI-drafted and unverified; C_t deliberately unwired under D-136.",
           0.6, 5.85, 5.0, 0.95, size=13)
    source(s, "FDA/CFSAN 2003 table, 479 rows; 140 ING bands (31 acidic,101 low-acid,8 inconclusive). DECISIONS.md D-136; fig_s180_4_ph_bands.png")


def s12_ner():
    s = new_slide("The NER protocol leaked families and duplicate rows", "GROUPED RECIPE SPLIT")
    rows = [["Grouped split", "Macro F1"], ["Clean baseline", "0.9504 ± 0.0034"],
            ["DeBERTa-base + CRF", "0.9545 ± 0.0037"]]
    table(s, rows, 0.6, 1.7, [7.6, 4.5], row_h=0.8, size=23)
    text(s, "Standard protocol: 13.6% masked-family overlap; 5.4% duplicate test rows.",
         0.6, 4.65, 12.0, 0.75, size=22, color=BLUE)
    caveat(s, "The grouped test showed no meaningful gain over the reproduced baseline.", 0.6, 5.85, 12.1, 0.8, size=15)
    source(s, "reports/ner/culinaryner_kf_final_report.md §A")


def s12b_models():
    s = new_slide("Models have separate roles and separate evidence limits", "MODEL COMPARISONS")
    rows = [["Model", "Role", "What was compared", "Limit"],
            ["DeBERTa-base+CRF", "NER", "Grouped baseline", "No improvement claim"],
            ["e5-large-v2", "Dense retrieval", "D5 retrieval ladder", "Model-assisted gold"],
            ["qwen2.5:7B / 72B", "Layer-1 proposer", "Prompt v1 / v3", "No correctness gold"],
            ["Nemotron-3-Ultra", "Live verbaliser", "Same model, two contexts", "No accuracy claim"]]
    table(s, rows, 0.6, 1.65, [3.2, 2.2, 3.7, 3.0], row_h=0.78, size=16)
    caveat(s, "NIM model: nvidia/nemotron-3-ultra-550b-a55b. New live observations require a saved, dated run.",
           0.6, 5.95, 12.1, 0.7, size=13)
    source(s, "tools/s179_d5_run_rungs.py MODEL/E5; tools/s182_live_rag.py; reports/s180/step7_FINAL_COMPARISON_2026-11-16.md; reports/ner/culinaryner_kf_final_report.md")


def s14_app():
    s = new_slide("The signed snapshot survives a missing live backend", "CULINARYSTATE EXPLORER")
    screen(s, "01_landing", 0.6, 1.45, 8.0, 4.8)
    text(s, ["Snapshot: no API key", "Live: local engine + own key", "Signature checked in browser"],
         9.0, 2.1, 3.4, 2.6, size=20, color=BLUE)
    caveat(s, "The proposal named Streamlit; Explorer is the declared interactive web-app substitution.",
           0.6, 6.0, 12.1, 0.65, size=14)
    source(s, "web/public/snapshot/manifest.json; deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md; tools/live_demo.sh. Public deployment hides /live.")


def s14b_live():
    s = new_slide("Same model, different context", "LIVE COMPARISON · NO GOLD")
    screen(s, "06_live_pipeline_ticking", 0.6, 1.45, 12.1, 1.55, top=0.65, bottom=0.10)
    screen(s, "08_live_compare_plain_carrots", 0.6, 3.03, 12.1, 2.9, top=0.615)
    run = read_json("reports/final/screens/runs/carrots.json")
    if run:
        verify = next(stage for stage in run["pipeline"] if stage["id"] == "verify")
        limit = f'Verifier: {verify["detail"]}. The advice remains unverified.'
    else:
        limit = "State citations are checked against the trace. The advice remains unverified."
    caveat(s, limit, 0.6, 6.0, 12.1, 0.65, size=14)
    source(s, "reports/final/screens/MANIFEST.json and runs/carrots.json; tools/s182_live_rag.py")


def s14c_business():
    s = new_slide("A state-and-evidence API could help recipe platforms abstain responsibly", "BUSINESS PROPOSAL")
    rows = [["User / buyer", "Recipe platforms · appliance makers · meal-kit apps"],
            ["Product", "State + evidence + claim constraints"],
            ["Proof today", "Explorer stories; D1–D5 PARTIAL"],
            ["Next", "Human gold · chef review · licensed partner"]]
    table(s, rows, 0.6, 1.75, [3.1, 9.0], row_h=0.9, size=20)
    caveat(s, "The proposed pilot needs an authorised recipe partner, human reference labels and cook feedback.",
           0.6, 5.9, 12.1, 0.8, size=14)
    source(s, "handoff/PARV_LATEST_PROMPT_2026-11-19.md §7; reports/final/deck/BUSINESS_PROPOSAL_OPTIONAL_2026-11-20.md; compliance matrix")


def s13_negative():
    s = new_slide("The remaining human and scientific gaps stay visible", "HONEST LIMITS")
    rows = [["Result", "Limit retained"], ["H1 / H3", "RULE_NOT_MET"],
            ["Lineage vNext", "Diagnostic; no regression gold"], ["Layer-1", "No correctness or recall measurement"],
            ["D1 literature", "0 human-verified rows"], ["D5 review", "Chef/peer review not performed"],
            ["Gold and proposal review", "D3 spot-audit and proposal disagreements pending"],
            ["Mixture composition", "pH and salt/fat fractions UNKNOWN"]]
    table(s, rows, 0.6, 1.55, [4.7, 7.4], row_h=0.59, size=18)
    source(s, "reports/s181/human_audit/REPORT_WORDING.md; reports/del5/d5_score_v1_D085/d5_scoring_result.json; D-134–D-139.")


def s15_close():
    s = new_slide("Our contribution is the integration, with explicit limits", "QUESTIONS")
    text(s, "Cooking state + evidence compatibility + claim-constrained answering",
         0.9, 1.8, 11.5, 1.9, size=33, font=SERIF, color=BLUE)
    text(s, "The system cites evidence or gives a reason for UNKNOWN.", 0.9, 4.1, 11.3, 0.7, size=23)
    deployment = read_json("reports/final/DEPLOYMENT_2026-11-20.json")
    url = (deployment or {}).get("url") or "Public URL: deployment pending"
    links = text(s, [url, "Local live: ./tools/live_demo.sh", "Fallback: see submission README"],
                 0.9, 5.2, 11.3, 1.2, size=14, font=MONO)
    if deployment:
        links.text_frame.paragraphs[0].runs[0].hyperlink.address = url
    source(s, "reports/final/REPORT_EVIDENCE_REVIEW_2026-11-20.json; submission/README_SUBMISSION.md")


# Preserve the original fifteen slide identities; selected_slides inserts the requested additions.
SLIDES = [s01_title, s02_problem, s03_compliance, s04_pipeline, s05_state, s06_compat,
          s07_tomato, s08_plainllm, s09_d4, s10_layer1, s11_ph, s12_ner,
          s13_negative, s14_app, s15_close]
