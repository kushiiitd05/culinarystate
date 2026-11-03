# Step 21: open chemistry questions for the chemistry expert (S158)

**Status: DRAFT_PENDING_H4. AI-prepared question list, not answers.** Written 2026-11-03 in session S158 by the AI worker "ksh" (an agent, not Kush). Nothing here settles a question, asserts a pathway, an enzyme, a rate or a condition, or claims human or expert review. The expert answers. Kush and Parv then decide each item and record it in DECISIONS.md (D-045). Until a question is closed by such a decision, every MECH entry that names it in `open_questions` cannot be ACCEPTED (MECH v1.1 schema rule), so Step 23 can only read it as UNKNOWN.

The questions come from the OPEN_QUESTION marks in `registry/mechanism_seed_roster_draft_v1.csv` (`open_issue` column), `reports/step21/mechanism_effect_ontology_v1_draft.md`, README §4 (D21-14, D21-19, D21-20, D21-22, D21-23) and `FIX_LOG_round3.md` (round-3 Review B items 21-1, 21-2, 21-3, 21-4, 21-6, 21-7, 21-12, 21-13, 21-14, 21-16, 21-17, 21-19). The ids `EQ21-nn` are the values that `MECH.open_questions[].question_ref` takes.

## Source status (read this first)

**No primary source was opened in this session.** Every source line below is **UNVERIFIED**.

- `WebFetch` of `https://www.enzyme-database.org/query.php?ec=1.10.3.3`, of `…?ec=3.1.1.14` and of the EBI OLS SBO term API (`www.ebi.ac.uk`) failed: the session's network policy does not allow those hosts. Under the session rules no further hosts were tried. To allow them, add the hosts under Allowed domains in the cloud environment's Network access settings.
- `WebSearch` did work. It returns result links and a tool-written summary, **not** the documents. The links it returned are listed under "Search leads": what to open, not what a source says. The search-tool summaries were not checked against any document and are **not** quoted as evidence. No numeric value from them is reproduced.
- No citation is given from memory. The reviewer-B statements quoted as "current draft wording" are the round-3 reviewer's text as recorded in the repo. They are not sources.

What the expert is asked for, per question: the answer, plus at least one PRIMARY source (DOI or stable URL, with page, table or figure) that the humans can check. REVIEW_CONTEXT sources may give background only; numeric claims need a PRIMARY source (MECH `evidence_refs.doc_type`).

---

### EQ21-01 The first step of the aerobic chain: is the reduced form to oxidised form step reversible, and what does it need?

- **Entries:** `ASCORBATE_TO_DHA_OXIDATION`; also touches `ASCORBIC_ACID_APPARENT_LOSS_LUMPED`.
- **Question:** (a) Is the oxidation of the reduced vitamin to its dehydro form reversible in plant tissue and cooking water? If so, which reductants (for example thiols) reverse it, and under which conditions? (b) Does the step need molecular oxygen? (c) Is it catalysed by metal ions, and which ones? (d) Does the oxidised form keep vitamin activity?
- **Why it matters:** the answers decide `edge_semantics` (REACTION versus EQUILIBRIUM), which condition axes are NECESSARY or MODULATING (oxygen, metal; gaps G-2 and G-8), and whether "reduced form decreases while total vitamin C is unchanged" is a valid effect (analyte basis, SVAR-000009). Step-10 ranking names that basis as a confounder.
- **Current draft wording (roster `open_issue`):** "OPEN_QUESTION (Review B 21-1, not in the repo, needs a PRIMARY source in 21b): that the step is reversible, needs O2, is catalysed by metal ions, and that thiols can reduce DHA back."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://hal.inrae.fr/hal-02629343v1/file/GomezRuiz_2018_AA_DHA_models_preprint.pdf` (a preprint, so not a peer-reviewed primary source as such); `https://avesis.hacettepe.edu.tr/yayin/b19653e5-970f-4b30-9621-097db2973c27/reversible-degradation-kinetics-of-ascorbic-acid-under-reducing-and-oxidizing-conditions`.

### EQ21-02 The second step: hydrolysis of the dehydro form

- **Entries:** `DHA_HYDROLYSIS_TO_DKG`.
- **Question:** Is the ring-opening of the dehydro form to 2,3-diketogulonic acid irreversible and independent of oxygen? Does it depend on pH and temperature? Over which pH range does it act in cooking-relevant conditions (a qualitative answer is enough; no rate is requested)? Does it end vitamin activity?
- **Why it matters:** the step's order relative to EQ21-01 (`consecutive_with`), whether an oxygen axis may gate it, and how "total vitamin C" targets are signed.
- **Current draft wording:** "OPEN_QUESTION (Review B 21-1; not in the repo): that this step is irreversible, a hydrolytic ring opening, independent of O2, strongly dependent on pH and T, and destroys vitamin activity."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://www.pubmed.gov/25212325/`; `https://www.research.ed.ac.uk/en/publications/characterisation-of-the-non-oxidative-degradation-pathway-of-dehy/`; `https://pubs.rsc.org/en/Content/ArticleLanding/2000/AN/B007299K`.

### EQ21-03 Ascorbate oxidase: EC number, product, and the node it acts on

- **Entries:** `ASCORBATE_OXIDASE_AA_OXIDATION`.
- **Question:** Is the enzyme EC 1.10.3.3 (L-ascorbate oxidase)? Is its direct product the monodehydroascorbate radical or the dehydro form? Does it therefore act on the **same** node as EQ21-01 (a parallel route to the same product, so the hydrolysis step is not counted twice)?
- **Why it matters:** the enzyme xref (`enzyme.ec`, PROPOSED) and the competition structure (PARALLEL_PATHWAY on the reduced form plus `consecutive_with` the hydrolysis). It also decides the plan's Step-26 prohibition "ascorbate-oxidase loss in raw / cut tissue".
- **Current draft wording:** "OPEN_QUESTION (not in the repo): that the enzyme (EC 1.10.3.3) catalyses exactly the AA -> DHA step; source the EC and the product in 21b (enzyme xref stays PROPOSED)."
- **Sources:** UNVERIFIED. Not opened (host blocked): `https://www.enzyme-database.org/query.php?ec=1.10.3.3`. Search leads, not opened: `https://enzyme.expasy.org/EC/1.10.3.3`.

### EQ21-04 Chlorophyllase branch: does it exist in cooking-relevant conditions, and what follows it?

- **Entries:** `CHLOROPHYLLASE_DEPHYTYLATION`, `CHLOROPHYLLIDE_TO_PHEOPHORBIDE`.
- **Question:** (a) Is chlorophyllase EC 3.1.1.14, with chlorophyllide and phytol as products? (b) Is the enzyme active in intact or cut vegetable tissue during the temperature range of blanching or cooking, and at which temperatures is it inactivated (qualitatively)? (c) Does chlorophyllide lose Mg to form pheophorbide under acid, so that this branch converges on Mg-free products? (d) Should the registry keep both rows, or record the branch as excluded for the processes Step 10 targets?
- **Why it matters:** the chlorophyll candidate model (SIM-CHL-1) assumes the branch away. By the UNKNOWN ≠ 0 rule, the registry must represent the branch and then evidence or exclude it. If no PRIMARY source supports it, both rows are dropped (recorded as dropped, R-19).
- **Current draft wording:** "OPEN_QUESTION (Review B 21-6, not in the repo): existence of the pathway, its enzyme (EC 3.1.1.14), product (chlorophyllide) and temperature behaviour must come from a PRIMARY source in 21b, or the entry is dropped; no xref is asserted." / "the chemistry and the convergence on Mg-free products need a PRIMARY source in 21b or the entry is dropped."
- **Sources:** UNVERIFIED. Not opened (host blocked): `https://www.enzyme-database.org/query.php?ec=3.1.1.14`. Search leads, not opened: `https://enzyme.expasy.org/EC/3.1.1.14`; `https://www.kegg.jp/entry/3.1.1.14`; `https://pubmed.ncbi.nlm.nih.gov/6819291`; `https://shizuoka.repo.nii.ac.jp/record/3010/files/K0360.pdf`.

### EQ21-05 SBO term ids for modifier roles (PROMOTER in particular)

- **Entries:** schema `$defs.inhibitor.sbo_role` (all modifier items); D21-19.
- **Question:** Are these the right Systems Biology Ontology terms: SBO:0000020 (inhibitor), SBO:0000019 (modifier), SBO:0000013 (catalyst) and SBO:0000459 (stimulator, used for PROMOTER)? Is "stimulator" the right term for a promoter such as a sensitising light, or is another SBO term closer?
- **Why it matters:** these ids are schema constants coupled to `role`. A wrong id would propagate to every entry. The xref policy treats every CURIE as unverified until a human checks it.
- **Current draft wording (README D21-19):** "Also confirm SBO:0000459 (stimulator) as the PROMOTER id; SBO:0000013 and :0000459 come from the schema's participant enum and are themselves to be human-verified."
- **Sources:** UNVERIFIED. Not opened (host blocked): `https://www.ebi.ac.uk/ols4/api/ontologies/sbo/terms?iri=http://biomodels.net/SBO/SBO_0000459`. Search leads, not opened (secondary tooling pages): `https://minerva.pages.uni.lu/manuals/v15.0/user/SBML-SBOTerms/`; `https://bmcsystbiol.biomedcentral.com/articles/10.1186/s12918-015-0212-9/tables/2`. Primary would be the SBO release itself (EBI).

### EQ21-06 Analyte-form token list

- **Entries:** every `affected_targets[].analyte_form` (MECH v1.1) and `KIN.target.analyte_form` (KIN v1.1); D21-22.
- **Question:** Which analyte forms must be told apart so that a measured value and a mechanism effect are on the same basis? Reviewer B proposed this list: REDUCED_AA, DHA, TOTAL_VITC_AA_PLUS_DHA, CHL_A, CHL_B, CHL_TOTAL, PHEO_A, PHEO_B, PYROPHEO_A, CHLIDE_A, PHEOBIDE_A, ZN_PHEO, CU_PHEO, COLOUR_NEG_A_STAR, OTHER, UNKNOWN. Is it correct and complete, are any tokens indistinguishable by the usual assay methods, and what should each token's definition and assay basis be? (UNKNOWN is a status in v1.1, not a token.)
- **Why it matters:** v1.1 has a token slot but **no list**. Every stated form stays `NO_APPROVED_REGISTRY` with a null token until the list is approved and stored in a registry file (H4). Without it, basis checks in Steps 10, 26 and 27 rely on free text.
- **Current draft wording (README D21-22):** "Reviewer B proposed a controlled token list in a new `registry/analyte_form_registry_draft_v1.csv` (REDUCED_AA, DHA, TOTAL_VITC_AA_PLUS_DHA, CHL_A, ...). **Not drafted** ... OPEN_QUESTION: approve the list and the file, then make `token` required when `status = STATED`."
- **Sources:** UNVERIFIED. No search was run for assay-method sources. The expert is asked to name the method standards they rely on.

### EQ21-07 Rule E-7: may a pH or temperature window ever be NECESSARY for a non-enzymatic reaction?

- **Entries:** `CHLOROPHYLL_TO_PHEOPHYTIN` and every CHEMICAL_REACTION entry; D21-20.
- **Question:** (a) Does Mg loss from chlorophyll on heating proceed across the whole practical tissue pH range, with acid speeding it and alkaline conditions slowing it, so that no pH makes it *absent*? (b) More generally, for non-enzymatic chemistry (hydrolysis, Maillard, lipid oxidation), is there any temperature or pH at which the reaction is absent rather than negligible on the cooking time scale?
- **Why it matters:** under the draft rule E-7, a NECESSARY pH or temperature gate on a CHEMICAL_REACTION needs PRIMARY evidence of absence. Otherwise the axis is MODULATING (a FORM input at Step 23 G7). A wrong NECESSARY gate gives false NOT_APPLICABLE results. Note too that under the current schema rule a pure-chemistry entry with only MODULATING gates can have `gates_unknown = false` only if it has at least one precondition (corrected after the S158 AI cross-review, R6).
- **Current draft wording:** "OPEN_QUESTION (Review B 21-7, not in the repo): that Mg loss proceeds across the whole practical pH range (acid speeds it, alkaline slows it), so that pH can never make the reaction absent; D21-20 asks the humans to confirm E-7 against a PRIMARY source."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://scilit.com/publications/20cc84b622de994980f985ca198a0932` (title as returned: "Kinetics of Chlorophyll Degradation to Pyropheophytin in Vegetables"); `https://www.scilit.net/publications/3c0c7adc43315a46295d046ee455139d`; `https://core.ac.uk/download/70668724.pdf`; `https://experts.umn.edu/en/publications/reaction-at-limited-water-concentration-2-chlorophyll-degradation/`.

### EQ21-08 Is colour non-monotone early in blanching for a reason outside the pigment chemistry?

- **Entries:** colour targets of `CHLOROPHYLL_TO_PHEOPHYTIN` (and any OBSERVABLE colour target); round-3 21-17.
- **Question:** Does green colour first brighten early in blanching because intercellular air is expelled (a physical-optical effect), and then dull? If so, should the registry add a physical entry (Reviewer B's optional `INTERCELLULAR_GAS_EXPULSION`) or simply never record a MONOTONIC colour trajectory?
- **Why it matters:** MECH v1.1 now requires evidence before an OBSERVABLE or UNKNOWN-class target may be MONOTONIC. Without evidence the shape is written UNKNOWN. The rule asserts nothing about colour. The answer decides whether to add a physical entry and what trajectory shape a colour target gets.
- **Current draft wording (ontology §6.2):** "Colour (a*) is an observable, not a species; whether it is monotone early in blanching (21-17) is OPEN_QUESTION and is not encoded."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://sapientia.ualg.pt/bitstreams/30caff78-bb9f-4377-b6ab-5cd99cc80eec/download`; `https://patents.google.com/patent/US4701330` (patent, not a primary scientific source).

### EQ21-09 Enzyme activity in the heating come-up window

- **Entries:** `ENZYME_THERMAL_INACTIVATION` and the enzymatic entries it gates (ascorbate oxidase, chlorophyllase, PPO, myrosinase); round-3 21-4.
- **Question:** In a cold-water start, does the activity of these enzymes rise with temperature during come-up before thermal inactivation, so that a cold start loses more of the vitamin than a boiling-water start? Is that true for each named enzyme or only some?
- **Why it matters:** this decides whether the history roles `ACTIVE_UNTIL_STATE_CHANGE` and `INPUT_REQUIRED_START_MODE` are needed on enzymatic entries, and whether start mode is a required input. Whether inactivation is a MECH entry or a Step-18 operator is a human design choice (D21-14), not this question.
- **Current draft wording:** "OPEN_QUESTION (Review B 21-4): the claim that enzyme activity first rises with temperature in the come-up window is not in the repo; source it in 21b."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://vjol.vista.gov.vn/hvnn/article/view/30228`; `https://www.protmed.uoradea.ro/facultate/publicatii/protectia_mediului/2014A/hort/02.Bei%20Mariana%202.pdf`. Non-scientific results the search returned (forums, lifestyle pages) are deliberately not listed.

### EQ21-10 Anaerobic route: markers and pH dependence

- **Entries:** `ASCORBIC_ACID_ANAEROBIC_DEGRADATION`; also `CARAMELISATION`; round-3 21-19.
- **Question:** Which products mark the anaerobic route (furfural, 2-furoic acid, 3-hydroxy-2-pyrone were named by Reviewer B)? Which of them also arise from sugar degradation or the aerobic route? Is the route acid-catalysed, so that pH is a MODULATING axis?
- **Why it matters:** MECH v1.1 lets a marker declare the other entries that produce it (`sharing_status = SHARED_DECLARED`, `shared_with_mechanism_keys`). The declaration needs the expert's list. `marker_unique` stays false in every case.
- **Current draft wording:** "OPEN_QUESTION (Review B 21-19, not in the repo): markers of this route (furfural, 2-furoic acid) may be shared with CARAMELISATION, so marker_unique stays false and no marker may identify the route; the pH dependence is to be evidenced."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://hub.hku.hk/handle/10722/68742`; `https://pmc.ncbi.nlm.nih.gov/articles/PMC4609971`; `https://katalog.lib.cas.cz/KNAV/EdsRecord/edsair,edsair.doi.dedup.....0939b6590a9f7d3d386375fbd34281f6` (title as returned: "The anaerobic decomposition of ascorbic acid in the pH range of foods and in more acid solutions").

### EQ21-11 Dissolved oxygen in the cooking water as a driver

- **Entries:** `ASCORBATE_TO_DHA_OXIDATION`, `ASCORBATE_OXIDASE_AA_OXIDATION`; gap G-8; round-3 21-13.
- **Question:** Is dissolved oxygen in the cooking medium, rather than headspace oxygen, the variable that drives aqueous oxidation and the enzyme route? Does its availability fall as water approaches boiling, so that a boiling start de-aerates the water?
- **Why it matters:** the CV registry has no dissolved-oxygen axis (CV-021 is headspace, now restricted to location HEADSPACE / UNKNOWN). If the answer is yes, the Step 07 registry v1.1 needs a new axis (D21-10), and without it these entries keep an unevaluable input.
- **Current draft wording (ontology G-8):** "whether dissolved oxygen drives aqueous oxidation and how it varies with temperature is chemistry the repo does not state (OPEN_QUESTION)".
- **Sources:** UNVERIFIED. Search leads, not opened: `https://hal.inrae.fr/hal-02739323` (title as returned: "Dissolved oxygen in aqueous solution of ascorbic acid and dissolved oxygen in apple purée at 80°C"); `https://hal.inrae.fr/hal-02755482`; `https://search.bvsalud.org/gim/resource/en/sea-25028`; `https://publish.csiro.au/BI/BI9480058`.

### EQ21-12 Coupled redox: the vitamin as a sacrificial reductant in enzymatic browning

- **Entries:** `PPO_ENZYMATIC_BROWNING` with `ASCORBATE_TO_DHA_OXIDATION`; round-3 21-14.
- **Question:** Does the reduced vitamin slow browning by reducing the o-quinones of polyphenol oxidase back to diphenols, being consumed in the process? Is that the main route, or does it also inhibit the enzyme directly? Should the two entries be linked with `COUPLED_REDOX` on the shared reduced form, with an INHIBITOR item on the browning entry?
- **Why it matters:** the relation decides whether Step 23 treats the two as competitors for the same species, and whether the anti-browning mitigation is represented.
- **Current draft wording:** "OPEN_QUESTION (Review B 21-14, not in the repo): ascorbic acid as a sacrificial reductant of the browning intermediates (consumed while it acts) would be declared with relation COUPLED_REDOX against ASCORBATE_TO_DHA_OXIDATION on reduced AA; needs a PRIMARY source."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://pmc.ncbi.nlm.nih.gov/articles/PMC4444905`; `https://www.ftb.com.hr/archives/857-control-of-enzymatic-browning-of-foods`; `https://citarea.cita-aragon.es/handle/10532/6887?mode=full`.

### EQ21-13 Metallo-chlorophyll complexes (regreening)

- **Entries:** `METALLO_CHLOROPHYLL_COMPLEX_FORMATION`; round-3 21-16.
- **Question:** Do Zn²⁺ or Cu²⁺ complexes of pheophytin or pyropheophytin form during heating of green vegetables (with metal from additives or vessels)? Under which conditions (pH, metal source)? Do they compete for pheophytin with the pyropheophytin step and reverse the colour observable?
- **Why it matters:** if they form, an EVD colour row could read MIXED against the chlorophyll entries, and the metal axis is only categorical (CV-023 / CV-036; gap G-2). MECH carries no regulatory or safety claim about copper or zinc (D21-18). The expert is not asked for one.
- **Current draft wording:** "OPEN_QUESTION (Review B 21-16, not in the repo): existence and conditions need a PRIMARY source in 21b or the entry is dropped."
- **Sources:** UNVERIFIED. Search leads, not opened: `https://pure.psu.edu/en/publications/chlorophyll-degradation-and-zinc-complex-formation-with-chlorophy/` (title as returned: "Chlorophyll Degradation and Zinc Complex Formation with Chlorophyll Derivatives in Heated Green Vegetables"); `https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_crossref_primary_10_1021_jf00041a010`; the patent pages returned (`https://patents.google.com/patent/US5482727`, `https://patents.google.com/patent/US6210729`) are not primary scientific sources.

### EQ21-14 Optional pyropheophytin entry

- **Entries:** `CHLOROPHYLL_PYROPHEOPHYTIN_FORMATION` (roster, beyond the card list).
- **Question:** Does pheophytin go on to form pyropheophytin under prolonged or high-temperature heating, so that a separate entry is justified? Or should the card list be kept verbatim and the row dropped?
- **Why it matters:** the row rests on a secondary-source statement only. It also fixes the substrate competition declared in EQ21-13.
- **Current draft wording:** "Beyond the card list; secondary-source statement only. Drop if the humans want the card list verbatim."
- **Sources:** UNVERIFIED. Search lead, not opened: `https://scilit.com/publications/20cc84b622de994980f985ca198a0932`.

---

## Not asked of the expert (human design choices; listed so they are not lost)

D21-14 (whether enzyme inactivation is a MECH entry or a Step-18 operator; named owner and date), D21-20's third branch (reviewer B's history INPUT_REQUIRED branch for `gates_unknown = false`), D21-21 (verdict fields on non-verdict items), D21-1 (evidence-id prefixes DOC- / OBS- / KIN- / LROOT- depend on 04.9-min reservations), D21-19 (re-admitting MESH / TRANSFORMON xref namespaces). Decided by Kush and Parv (H4).
