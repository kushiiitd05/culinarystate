"""Slide content for CulinaryState_final.pptx. Every number is listed in NUMBER_SOURCES.md."""


def build(g):
    globals().update(g)
    for fn in SLIDES:
        fn()


def s01_title():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
    box(s, 0.6, 1.55, 0.09, 2.3, BLUE, BLUE)
    text(s, "CulinaryState", 0.9, 1.4, 11.5, 1.0, size=48, font=SERIF)
    text(s, "from recipe text to evidence-grounded cooking state", 0.9, 2.45, 11.5, 0.8,
         size=26, font=SERIF, color=SLATE)
    text(s, "A composition-aware cooking-state representation that measures when scientific "
            "evidence transfers to a recipe step, and abstains when it does not.",
         0.9, 3.3, 10.5, 0.9, size=16, color=INK)
    text(s, ["Group 17 · Kush Tokas · Parv Goyal",
             "Computational Gastronomy · Final project · IIIT Delhi · 25–26 Nov 2026"],
         0.9, 5.2, 11, 0.8, size=14, color=MUTED)
    text(s, "Every figure on these slides is labelled with its source file and its evidence status.",
         0.9, 6.5, 11, 0.4, size=11, color=MUTED, font=SANS)


def s02_problem():
    s = new_slide("Text RAG treats a recipe as text, so it answers without evidence", "THE PROBLEM")
    labelled_box(s, 0.6, 1.6, 5.9, 3.9, [
        R(("What a text retriever sees", {"bold": True, "size": 15})),
        "",
        "“Boil the tomatoes in water with salt, vinegar and olive oil for 15 minutes.”",
        "",
        "Nearest passage: a retention row for boiled tomato. A generator then states a number.",
        "",
        "Nothing checks whether the measured food matched this pot: water alone, or water with "
        "salt, acid and fat.",
    ], size=14)
    labelled_box(s, 6.8, 1.6, 5.9, 3.9, [
        R(("What a cooking question actually needs", {"bold": True, "size": 15, "color": BLUE})),
        "",
        "1.  The state of the food at that step: what it is mixed with, how it was cut, heated, covered.",
        "2.  Which evidence rows were measured under compatible conditions.",
        "3.  A rule for what may be said: a cited number, a range, or “not known”.",
        "4.  The right to abstain when the evidence does not transfer.",
    ], line=BLUE, size=14)
    text(s, "Our question: when does a measured retention value transfer to a specific recipe step?",
         0.6, 5.85, 12.1, 0.5, size=17, font=SERIF, color=BLUE)
    source(s, "framing from handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md; tomato sentence from "
              "reports/s181/snapshot_findings.md (tomato-d, kept phrasing).")


def s03_compliance():
    s = new_slide("Promised D1–D5 vs delivered: all five are PARTIAL", "HONEST COMPLIANCE")
    A = {"color": AMBER, "bold": True}
    rows = [
        ["", "Promised (proposal, 18 Oct)", "Delivered", "Status", "Specific gap"],
        ["D1", "Evidence ledger ≥1,000 rows + ≥40 hand-verified literature rows",
         "17,978 ACTIVE rows, each with source + tier", ("PARTIAL", A),
         "0 human-verified rows; all 17,978 are tier E3"],
        ["D2", "Cold-split completion benchmark, H2 with study-level CIs",
         "Splits, baselines, completion models; negative results reported", ("PARTIAL", A),
         "Not every prescribed treatment (propensity, conformal, bootstrap) shown"],
        ["D3", "State engine; 40 gold recipes + 30 scripted sessions",
         "Engine; 30 sessions pass; scored on 40 dev-gold: field acc 0.11–0.20, merge/split F1 0.36–0.47, 0 replay issues",
         ("PARTIAL", A), "Gold is author-accepted AI drafts, not independent or held out"],
        ["D4", "Compatibility retrieval + calibrated abstention; Recall@K, risk–coverage, UCR, ECE",
         "UNKNOWN-neutral compatibility, answer/ask/abstain; 3 of 4 metrics post hoc", ("PARTIAL", A),
         "ECE not computable; condition-aware Recall@K degenerate; no human claim audit"],
        ["D5", "~80 questions / 8 task types, B0–B5 ladder, chef/peer review, 8-scenario Streamlit demo",
         "74 questions over 8 task types; ladder + ablations; 8 backend scenarios; web Explorer",
         ("PARTIAL", A), "Chef/peer review not performed; demo is a substitution for Streamlit"],
    ]
    table(s, rows, 0.6, 1.45, [0.55, 3.2, 3.6, 1.0, 3.75], row_h=0.86, size=11)
    caveat(s, "The compliance matrix is AI_DRAFTED, not a human attestation. D3 correction of 17 Nov: "
              "the 40-recipe evaluation was performed, on non-independent dev gold.",
           0.6, 6.05, 12.1, 0.8, size=11.5)
    source(s, "reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md (D1–D5 rows, D3 correction 17 Nov); "
              "D4 metric status: reports/s181/d4_contract_metrics.md.")


def s04_pipeline():
    s = new_slide("Pipeline: the LLM may touch one field; everything after it is checked", "ARCHITECTURE")
    top = ["Recipe text", "Rule compiler", "Ambiguity trigger?", "LLM proposal\nalternative_group only",
           "Typed Event IR", "Invariant validator"]
    bot = ["S_t = (G,C,Q,Y,P)", "Evidence compiler\n(13 axes)", "Compatibility", "Claim packet",
           "Verbaliser", "Verifier → answer\nor abstain"]
    w, h, gap, x0 = 1.82, 1.0, 0.24, 0.6
    for row, labels, y in ((0, top, 1.75), (1, bot, 4.1)):
        for i, lab in enumerate(labels):
            x = x0 + i * (w + gap)
            if row == 1:
                x = x0 + (5 - i) * (w + gap)
            llm = "LLM" in lab
            fill, line = (AMBER_BG, AMBER) if llm else ((BLUE_BG, BLUE) if lab.startswith("S_t") else (SURF, BORDER))
            box(s, x, y, w, h, fill, line, 2.0 if (llm or lab.startswith("S_t")) else 1.0)
            text(s, lab, x + 0.06, y + 0.05, w - 0.12, h - 0.1, size=12.5,
                 font=MONO if lab.startswith("S_t") else SANS, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            if i < 5:
                if row == 0:
                    arrow(s, x + w, y + h / 2, x + w + gap, y + h / 2)
                else:
                    arrow(s, x, y + h / 2, x - gap, y + h / 2)
    xr = x0 + 5 * (w + gap) + w / 2
    arrow(s, xr, 1.75 + h, xr, 4.1)
    text(s, "no trigger: compiler output goes straight to the IR", 2.6, 2.85, 5.6, 0.3, size=11, color=MUTED)
    text(s, [R(("Deterministic by default. ", {"bold": True, "color": BLUE}),
               "The LLM proposes only alternative_group, on one trigger, and must quote the span that licenses it. "
               "The verbaliser cannot widen the claim packet: failure falls back to a fixed template.")],
         0.6, 5.45, 12.1, 0.8, size=14)
    source(s, "handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md §architecture (D-135 surface, 13-axis registry, claim packet + verifier).")


def s05_state():
    s = new_slide("State S_t = (G, C, Q, Y, P): what the food is at each step", "REPRESENTATION")
    blocks = [("G", "Lineage / structure", "Lot-aware graph: which pieces of food were merged, split, reserved, recombined."),
              ("C", "Composition", "What the lot is mixed with: e.g. water, salt, acid, lipid present or UNKNOWN."),
              ("Q", "Physical conditions", "Thermal dose, lid, geometry, cut history (piece size class)."),
              ("Y", "Analyte / evidence", "Per-nutrient route (DIRECT / UNKNOWN), cited rows, near rows, reasons."),
              ("P", "Provenance", "Which rule, span or proposal produced each field; replayable event log.")]
    for i, (k, name, desc) in enumerate(blocks):
        y = 1.5 + i * 0.86
        box(s, 0.6, y, 0.8, 0.72, BLUE_BG, BLUE, 1.5)
        text(s, k, 0.6, y, 0.8, 0.72, size=26, font=SERIF, color=BLUE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(s, [R((name, {"bold": True})), desc], 1.55, y + 0.02, 6.2, 0.75, size=13)
    box(s, 8.1, 1.5, 4.6, 2.35, SLATE_BG, SLATE, 1.5)
    text(s, [R(("UNKNOWN is first-class, never zero", {"bold": True, "size": 15})), "",
             "A field the text does not settle is UNKNOWN with a stated reason, e.g. "
             "lipid_present = UNKNOWN (NO_RECOGNIZED_MARKER).",
             "It is never filled with 0, a default, or a midpoint."],
         8.25, 1.6, 4.3, 2.2, size=13)
    caveat(s, "Broad even when sparse: many fields are UNKNOWN on most recipes. Known engine defects stay "
              "visible, e.g. blending leaves cell_integrity = CUT, and a diced tomato is reported SLICED in cut-mixed.",
           8.1, 4.05, 4.6, 1.9, size=12)
    source(s, "handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md (State engine); reports/s181/snapshot_findings.md "
              "(NO_RECOGNIZED_MARKER, surprises 5–6).")


def s06_compat():
    s = new_slide("Evidence compatibility: unknown is not a mismatch", "13 AXES · 4 OUTCOMES")
    outs = [("MATCH", "source and query agree on this axis", BLUE_BG, BLUE),
            ("MISMATCH", "they disagree: the row does not apply", SURF, INK),
            ("UNKNOWN_IN_SOURCE", "the row did not record this condition", SLATE_BG, SLATE),
            ("UNKNOWN_IN_QUERY", "the recipe does not state it", SLATE_BG, SLATE)]
    for i, (k, d, f, l) in enumerate(outs):
        y = 1.55 + i * 0.95
        box(s, 0.6, y, 5.3, 0.8, f, l, 1.5)
        text(s, [R((k, {"font": MONO, "bold": True, "size": 13})), d], 0.75, y + 0.05, 5.0, 0.72, size=12.5)
    text(s, "The axes are chosen before retrieval from a 13-axis registry: 9 implemented, 2 in the compiler "
            "(pH, geometry), 2 schema-only (a_w, measurement method). An unavailable axis stays UNKNOWN with a reason.",
         0.6, 5.45, 5.3, 1.3, size=12.5)
    picture(s, "fig_s180_3_axis_status.png", 6.15, 1.5, w=6.6)
    source(s, "handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md (Evidence compiler, Compatibility engine); "
              "figure reports/final/figures_s180_2026-11-16/fig_s180_3_axis_status.png.")


def s07_tomato():
    s = new_slide("Tomato A–D: one evidence row, four pots, one allowed number", "CENTRAL DEMO")
    rows = [["", "Recipe (boil tomatoes in water … for 15 minutes)", "Route (vit C, lycopene)", "Evidence", "System says"],
            ["A", "water only", ("DIRECT", {"color": BLUE, "bold": True}), "applied EVD-002765, EVD-002781",
             ("cites EVD-002765 = 95.0%", {"color": BLUE})],
            ["B", "+ salt", ("UNKNOWN", {"color": SLATE, "bold": True}), "near EVD-002765, EVD-002781", "not known; no number"],
            ["C", "+ salt, vinegar", ("UNKNOWN", {"color": SLATE, "bold": True}), "near EVD-002765, EVD-002781", "not known; no number"],
            ["D", "+ salt, vinegar, olive oil", ("UNKNOWN", {"color": SLATE, "bold": True}), "near EVD-002765, EVD-002781", "not known; no number"]]
    t = table(s, rows, 0.6, 1.5, [0.5, 4.0, 2.3, 3.0, 2.3], row_h=0.55, size=13)
    for i in range(1, 5):
        for j in (3,):
            for p in t.cell(i, j).text_frame.paragraphs:
                for r in p.runs: r.font.name = MONO; r.font.size = Pt(11.5)
    text(s, [R(("The same row is near evidence for B, C and D, but numeric transfer is forbidden: ", {"bold": True}),
               "the source does not confirm the food was measured with salt, acid or lipid present "
               "(COMPOSITION_UNCONFIRMED_IN_SOURCE:SALT+ACID+LIPID). A text retriever would return the same 95.0% for all four.")],
         0.6, 4.4, 12.1, 0.9, size=14)
    caveat(s, "On stage the template's UNKNOWN reason reads MEAS_HAS_3_ROWS_PE_METHOD_NULL, not the composition reason, "
              "which sits only in Y.vitc_route. Tomato D binds the oil only with lineage vNext on (D-134); "
              "the code default differs. Scenarios are self-written text with no gold.",
           0.6, 5.35, 12.1, 1.45, size=12)
    source(s, "reports/s181/snapshot_findings.md (route table, kept phrasing, surprises 2 and 10); EVD-002765 / EVD-002781 → SRC-000001 (USDA-RETN-R6).")


def s08_plainllm():
    s = new_slide("Plain LLM vs CulinaryState on the same 19 questions", "DIAGNOSTIC_ONLY")
    labelled_box(s, 0.6, 1.5, 5.95, 3.75, [
        R(("Where the plain model was more cautious", {"bold": True})), "",
        "On the 5 DIRECT questions (tomato-a ×3, cut-dice ×2) it gave no number and said the amount "
        "cannot be precisely determined. The system stated the cited 95.0%.", "",
        "At least 4 of its 14 FAIL verdicts are cautious in substance; they fail a wording check."],
        size=13.5)
    labelled_box(s, 6.75, 1.5, 5.95, 3.75, [
        R(("Where it invented numbers", {"bold": True})), "",
        "In 3 of 19 replies it asserted “20–30%” with no source (tomato-b vit C, tomato-c lycopene, tomato-d lycopene).", "",
        "For the same nutrient, lycopene, it said 20–30% is lost (tomato-c) and 20–30% remains (tomato-d).", "",
        "The verifier flagged each as FORBIDDEN_NUMERIC_CLAIM."], size=13.5)
    caveat(s, "One model (qwen2.5:7b-instruct), one prompt, temperature 0, no gold. 2 FORBIDDEN_NUMERIC_CLAIM verdicts are verifier "
              "false positives on durations (“15-minute”, “10–15 minutes”), and it reads only the first number of a range. "
              "This states what each side did; it does not rank them.",
           0.6, 5.4, 12.1, 1.4, size=12, head="DIAGNOSTIC_ONLY · NO GOLD")
    source(s, "reports/s181/snapshot_findings.md, “Plain-LLM baseline (arm B0_LLM_ONLY)” and “Reading the baseline table honestly”.")


def s09_d4():
    s = new_slide("D4 metrics on the 74-question benchmark", "MODEL_ASSISTED_GOLD · POST_HOC")
    rows = [["Contract metric", "Result", "Status"],
            ["Unsupported-claim rate", "B7 full system 4/34 = 0.118  ·  B2 hybrid RAG 24/43 = 0.558", "reported, machine checker"],
            ["Risk–coverage", "B7 partial AURC 0.0977 over coverage 0.45–1.0 (n = 40)", "post hoc, 4 tied levels"],
            ["Condition-compatible Recall@K", "0.20 / 0.34 / 0.375 at K = 1 / 3 / 5 (B2, n = 20)", "degenerate = plain recall"],
            ["ECE", "—", ("NOT_COMPUTABLE", {"color": SLATE, "bold": True})]]
    t = table(s, rows, 0.6, 1.5, [3.2, 5.9, 3.0], row_h=0.55, size=13)
    for p in t.cell(1, 1).text_frame.paragraphs:
        for r in p.runs: r.font.color.rgb = BLUE; r.font.bold = True
    caveat(s, "B7's low rate is partly bought by saying less: 17 of its 40 answers make no numeric claim. B5T (0.070) is lower "
              "than B7. Recall@K: no question states a condition, so nothing can mismatch. ECE: the system emits ordinal classes, "
              "not probabilities, and no calibrator was built, so abstention is rule-based and uncalibrated. No human claim audit. "
              "H3 stays RULE_NOT_MET.",
           0.6, 4.45, 12.1, 2.3, size=13)
    source(s, "reports/s181/d4_contract_metrics.md §1–4 and summary table (labels MODEL_ASSISTED_GOLD · NO_HUMAN_SIGNOFF_D085 · POST_HOC_DIAGNOSTIC).")


def s10_layer1():
    s = new_slide("Layer-1 LLM: three defects, each found by a check", "DIAGNOSTIC_ONLY · NO GOLD")
    items = [("D-135", "A reference field with no referent: condition_profile_id let any noun pass. Removed; one field on one trigger remains."),
             ("D-137", "Range-checked spans were reported as grounded: every accepted v1 proposal pointed somewhere else."),
             ("prompt v3", "Integer offsets produced plausible numbers, not locations. v3 asks for the quote and locates it in code.")]
    for i, (k, d) in enumerate(items):
        y = 1.5 + i * 1.05
        text(s, k, 0.6, y, 1.4, 0.4, size=13, font=MONO, color=BLUE, bold=True)
        text(s, d, 2.0, y, 4.6, 1.0, size=12.5)
    text(s, [R(("0 → 21 grounded proposals", {"bold": True, "color": BLUE, "size": 17})),
             "72B, prompt v3, 60 sealed cases; 0 of 63 quotes failed to locate.", "",
             R(("Scale chose better, located nothing: ", {"bold": True})),
             "under prompt v1, selection 50% (7B) → 81% (72B); grounding 0 → 0. 72B v3: 19 of 21 name a real choice."],
         0.6, 4.65, 6.0, 1.9, size=12.5)
    picture(s, "fig_s180_2_layer1_surface.png", 6.85, 1.45, w=5.85)
    caveat(s, "No gold; AI-delegated review (D-085), raters not independent; single-sample arms; 59 + 1 repaired call. No accuracy number.",
           6.85, 5.85, 5.85, 0.95, size=11)
    source(s, "reports/s180/step7_FINAL_COMPARISON_2026-11-16.md §1–5; figure fig_s180_2_layer1_surface.png.")


def s11_ph():
    s = new_slide("pH: bands from a public table, never midpoints", "AXIS 7")
    text(s, [R(("140 ingredient bands", {"bold": True, "color": BLUE, "size": 18})),
             "from the FDA/CFSAN 2003 table (479 rows, public domain): 31 acidic, 101 low-acid, 8 inconclusive.", "",
             R(("Tomato: pH 4.3–4.9", {"bold": True, "size": 16})),
             "The band straddles 4.6, so the system will not call tomato acidic. It keeps the interval; it never "
             "reports a midpoint and never clips."],
         0.6, 1.55, 5.4, 3.6, size=14)
    caveat(s, "The ingredient crosswalk is UNVERIFIED_CROSSWALK_AI_DRAFTED, and pH is deliberately not wired into C_t (D-136).",
           0.6, 5.3, 5.4, 1.3, size=12.5)
    picture(s, "fig_s180_4_ph_bands.png", 6.3, 1.45, h=5.35)
    source(s, "handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md (pH axis 7); reports/final/CLAIM_AND_SOTA_MATRIX.md (pH row); fig_s180_4_ph_bands.png.")


def s12_ner():
    s = new_slide("NER: a tie, and a leak in the standard protocol", "TIES · PROTOCOL FINDING")
    rows = [["RecipeDB3", "Micro F1", "Macro F1", "Claim"],
            ["Clean baseline (grouped split, select on dev)", "0.9594", "0.9504 ± 0.0034", ""],
            ["Ours: DeBERTa-base + CRF", "0.9581 ± 0.0012", "0.9545 ± 0.0037", ("TIES", {"bold": True})]]
    table(s, rows, 0.6, 1.5, [5.2, 2.2, 2.4, 2.3], row_h=0.5, size=13)
    labelled_box(s, 0.6, 3.25, 12.1, 1.75, [
        R(("The stronger finding: the standard RecipeDB3 protocol leaks", {"bold": True, "color": BLUE, "size": 15})),
        "Random 80/20 split with selection on test: 13.6% masked-family overlap and 5.4% exact duplicate test rows. "
        "Leaked rows score micro 0.9937 vs 0.9558."], line=BLUE, size=13.5)
    caveat(s, "The score gap from the leak is +0.0039 with Welch p = 0.067: not significant at 0.05. "
              "Ours is numerically above the clean macro but the NER report words it “no improvement”. External TASTEset and FoodBase "
              "scores were not obtained: NOT_COMPARABLE.",
           0.6, 5.2, 12.1, 1.55, size=12.5)
    source(s, "reports/final/CLAIM_AND_SOTA_MATRIX.md (NER rows, citing reports/ner/culinaryner_kf_final_report.md §A).")


def s13_negative():
    s = new_slide("Negative results and limitations we keep", "RETAINED")
    items = [
        ("H1  RULE_NOT_MET", "B4 = 6/24 vs B1 = B2 = 6/24; 4 discordant pairs, exact McNemar p = 1.0. Not equivalence, not absence of an effect."),
        ("H3  RULE_NOT_MET", "Sign test favours B7 (16 vs 0), but the preregistered P3 condition fails: B7 abstains 0/10. Not reported as a win."),
        ("Lineage vNext  DIAGNOSTIC", "29.3% of recipes changed; there is no gold regression set."),
        ("Layer-1  no gold", "21 grounded proposals; recall unmeasured; no accuracy figure exists."),
        ("Reviews are not human verification", "D-085 passes were AI personas; the chef/peer review was not performed."),
        ("D1  0 hand-verified rows", "The ≥40 hand-verified literature rows are not met; this is human-only work."),
    ]
    for i, (k, d) in enumerate(items):
        col, r = i % 2, i // 2
        x, y = 0.6 + col * 6.15, 1.5 + r * 1.75
        box(s, x, y, 5.95, 1.55, AMBER_BG, AMBER, 2.0)
        text(s, k, x + 0.14, y + 0.1, 5.7, 0.35, size=13, font=MONO, color=AMBER, bold=True)
        text(s, d, x + 0.14, y + 0.48, 5.7, 1.05, size=13)
    source(s, "reports/final/CLAIM_AND_SOTA_MATRIX.md (H1, H3, lineage, Layer-1 rows); "
              "reports/s180/step7_FINAL_COMPARISON_2026-11-16.md §5; reports/s181/human_audit/REPORT_WORDING.md; "
              "DELIVERABLE_COMPLIANCE_MATRIX D1.")


def s14_app():
    s = new_slide("CulinaryState Explorer: snapshot first, live core optional", "DEMO ARCHITECTURE")
    box(s, 0.6, 1.7, 2.6, 1.3, SURF, BORDER); text(s, "Browser\n(Explorer UI)", 0.6, 1.7, 2.6, 1.3, size=14, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    box(s, 4.2, 1.5, 3.9, 1.7, BLUE_BG, BLUE, 2.0)
    text(s, [R(("Signed precomputed snapshot", {"bold": True})), "default path",
             "Ed25519 manifest · 17 data files · 1.10 MB"], 4.3, 1.6, 3.7, 1.5, size=13, align=PP_ALIGN.CENTER)
    box(s, 4.2, 3.7, 3.9, 1.5, SURF, BORDER)
    text(s, [R(("Live core (optional)", {"bold": True})), "stdlib server: /api/analyze, /api/ask, /api/compare, /api/health"],
         4.3, 3.8, 3.7, 1.3, size=12.5, align=PP_ALIGN.CENTER)
    box(s, 9.2, 3.7, 3.5, 1.5, SLATE_BG, SLATE)
    text(s, [R(("Ollama", {"bold": True})), "not on the request path; never exposed to the browser"],
         9.3, 3.8, 3.3, 1.3, size=12.5, align=PP_ALIGN.CENTER)
    arrow(s, 3.2, 2.35, 4.2, 2.35, BLUE); arrow(s, 3.2, 2.7, 4.2, 4.45)
    text(s, "The demo must survive GPU, VPN, Ollama or tunnel failure: the snapshot needs none of them.",
         0.6, 5.5, 12.1, 0.5, size=14, color=BLUE)
    caveat(s, "This web app substitutes for the proposal's 8-scenario Streamlit demo and is declared as such. "
              "None of the 8 contractual ask cases returns ANSWER; all abstain or ask.",
           0.6, 6.0, 12.1, 0.85, size=12)
    source(s, "reports/s181/snapshot_findings.md (What was built; eight ask outputs); handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md §11, §15–17; compliance matrix D5.")


def s15_close():
    s = new_slide("Contribution", "SUMMARY")
    box(s, 0.6, 1.6, 0.09, 1.9, BLUE, BLUE)
    text(s, "A composition-aware, evidence-grounded cooking-state representation that measures when "
            "scientific evidence transfers — and abstains when it does not.",
         0.9, 1.5, 11.6, 2.0, size=26, font=SERIF)
    text(s, ["Our contribution is the integration: state representation + evidence compatibility + "
             "claim-constrained answering. Recipe flow graphs are prior art; we do not claim to have invented them.",
             "", "We make no state-of-the-art claim on any component."],
         0.9, 3.8, 11.6, 1.5, size=15, color=SLATE)
    text(s, "Questions", 0.9, 5.6, 6, 0.8, size=32, font=SERIF, color=BLUE)
    source(s, "reports/final/CLAIM_AND_SOTA_MATRIX.md (“No overall SOTA claim”; SYSTEM_CONTRIBUTION_ONLY rows; flow-graph prior art).")


SLIDES = [s01_title, s02_problem, s03_compliance, s04_pipeline, s05_state, s06_compat, s07_tomato,
          s08_plainllm, s09_d4, s10_layer1, s11_ph, s12_ner, s13_negative, s14_app, s15_close]
