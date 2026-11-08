"""Assemble the two L-SRC deliverables (S176) from the sub-lane JSONL files plus lane-lead additions.

Run: <venv python> -I build_lsrc.py <repo_root> <lsrc_scratch_dir>
Writes ONLY:
  <repo>/registry/scenario_defaults_source_review_S176.csv
  <repo>/registry/mechanism_condition_windows_draft_v1.csv
No third-party verbatim text is written (audit snippets are dropped; quote marks removed / paraphrased).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
SCR = Path(sys.argv[2])

# ----------------------------------------------------------------------------------------------
# Citation strings (bibliographic fields only as seen on fetched pages; '?' where not seen)
# ----------------------------------------------------------------------------------------------
C = {
    "TAJIMA2001": "Tajima M et al. (2001) Heat-induced changes of myosin and sarcoplasmic proteins in beef during simmering. J Food Sci. doi:10.1111/j.1365-2621.2001.tb11323.x",
    "KIMINDU2025": "Kimindu VA et al. (2025) Lethality of beef cooking methods against Pediococcus species surrogates of Shiga toxin-producing Escherichia coli. J Food Saf (DOI not in record)",
    "FLANNERY2014": "Flannery J et al. (2014) Effectiveness of cooking to reduce norovirus and infectious F-specific RNA bacteriophage concentrations in Mytilus edulis. J Appl Microbiol. doi:10.1111/jam.12534",
    "CANO2026": "Cano PW et al. (2026) Salmonella inactivation during the preparation of omelets, poached eggs, and scrambled eggs. J Food Saf (DOI not in record)",
    "NCHFP_BLANCH": "National Center for Home Food Preservation (USDA-NIFA funded, Univ. of Georgia), 'Blanching Vegetables', from So Easy to Preserve 6th ed. 2014, UGA Coop. Ext. Bulletin 989. https://nchfp.uga.edu/how/freeze/freeze-general-information/blanching-vegetables/",
    "NIST_SAT": "NIST Chemistry WebBook SRD 69, Thermophysical Properties of Fluid Systems: water, saturation table. https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C7732185&Type=SatP&Digits=5&PLow=14.696&PHigh=29.696&PInc=5&RefState=DEF&TUnit=C&PUnit=psia",
    "NIST_SAT_H": "NIST Chemistry WebBook SRD 69: water saturation table with enthalpies (kJ/kg). https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID=C7732185&Type=SatT&Digits=5&THigh=100&TLow=20&TInc=40&RefState=DEF&TUnit=C&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm",
    "NIST_ISOBAR": "NIST Chemistry WebBook SRD 69: water isobaric data at 0.101325 MPa, 1-99 C (k, rho, cp). https://webbook.nist.gov/cgi/fluid.cgi?P=0.101325&TLow=1&THigh=99&TInc=7&Digits=4&ID=C7732185&Action=Load&Type=IsoBar",
    "NCHFP_G1": "USDA / NCHFP, Complete Guide to Home Canning, Guide 1 'Principles of Home Canning' (rev. 2015). https://nchfp.uga.edu/papers/guide/GUIDE01_HomeCan_rev0715.pdf",
    "EU2017_2158": "Commission Regulation (EU) 2017/2158 establishing mitigation measures and benchmark levels for the reduction of the presence of acrylamide in food. https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R2158",
    "SAHIN1999": "Sahin S, Sastry SK, Bayindirli L (1999) The determination of convective heat transfer coefficient during frying. J Food Eng 39(3):307-311. doi:10.1016/s0260-8774(98)00171-x",
    "COSTA1999": "Costa RM, Oliveira FAR, Delaney O, Gekas V (1999) Analysis of the heat transfer coefficient during potato frying. J Food Eng 39(3):293-299. doi:10.1016/s0260-8774(98)00169-1",
    "FARINU2007": "Farinu A, Baik OD (2007) Heat transfer coefficients during deep fat frying of sweetpotato: effects of product size and oil temperature. Food Res Int 40(8):989-994. doi:10.1016/j.foodres.2007.05.006",
    "SERUGA2005": "Seruga B et al. (2005) Determination of thermal conductivity and convective heat transfer coefficient during deep fat frying of Krostula dough. Eur Food Res Technol. doi:10.1007/s00217-005-1176-6",
    "SOSA2006": "Sosa-Morales ME, Orzuna-Espiritu R, Velez-Ruiz JF (2006) Mass, thermal and quality aspects of deep-fat frying of pork meat. J Food Eng 77(3):731-738. doi:10.1016/j.jfoodeng.2005.07.033",
    "MIRBEL2012": "Mir-Bel J, Oria R, Salvador ML (2012) Influence of temperature on heat transfer coefficient during moderate vacuum deep-fat frying. J Food Eng 113(2):167-176. doi:10.1016/j.jfoodeng.2012.06.009",
    "HAKANSSON2019": "Hakansson A (2019) An investigation of uncertainties in determining convective heat transfer during immersion frying using the general uncertainty management framework. J Food Eng 263:424-436. doi:10.1016/j.jfoodeng.2019.07.024",
    "NUGRAHEDI2017": "Nugrahedi PY et al. (2017) Stir-frying of Chinese cabbage and pakchoi retains health-promoting glucosinolates. Plant Foods Hum Nutr. doi:10.1007/s11130-017-0646-x",
    "OU2006": "Ou D et al. (2006) Double-sided pan-frying of unfrozen/frozen hamburgers for microbial safety using modelling and simulation. Food Res Int. doi:10.1016/j.foodres.2005.06.009",
    "IKEDIALA1996": "Ikediala JN et al. (1996) Finite element modeling of heat transfer in meat patties during single-sided pan-frying. J Food Sci. doi:10.1111/j.1365-2621.1996.tb12205.x",
    "ROCCA2019": "Rocca-Polimeni R, Zarate Vilet N, Roux S, Bailleul JL, Broyart B (2019) Continuous measurement of contact heat flux during minced meat grilling. J Food Eng 242:163-171. doi:10.1016/j.jfoodeng.2018.08.032",
    "VINE": "Vine T, Flick D, Bernuau E, Broyart B. Experimental and numerical study of heat and mass transfer during contact heating of sliced potatoes. J Food Eng 275 (year 2020 or 2021: check; HAL hal-02959920)",
    "FSIS_DZ": "USDA FSIS, Food Safety Information fact sheet 'Danger Zone (40 F - 140 F)' (GPO govinfo copy). https://www.govinfo.gov/content/pkg/GOVPUB-A110-PURL-gpo11877/pdf/GOVPUB-A110-PURL-gpo11877.pdf",
    "INCROPERA_MTU": "Incropera FP et al., Fundamentals of Heat and Mass Transfer, 6th ed. (Wiley 2007), table of typical convection coefficients, as reproduced in F. Morrison, CM3120 handout, Michigan Tech. https://pages.mtu.edu/~fmorriso/cm3120/typical_values_heat_transfer_coefficient.pdf",
    "CARSON2006": "Carson JK, Willix J, North MF (2006) Measurements of heat transfer coefficients within convection ovens. J Food Eng 72(3):293-301. doi:10.1016/j.jfoodeng.2004.12.010",
    "SAKIN2009": "Sakin M, Kaymak-Ertekin F, Ilicali C (2009) Convection and radiation combined surface heat transfer coefficient in baking ovens. J Food Eng 94(3-4):344-349. doi:10.1016/j.jfoodeng.2009.03.027",
    "GOUYO2021": "Gouyo T, Goujot D, Bohuon P, Courtois F (2021) Multi-compartment model for heat and mass transfer during the frying of frozen pre-fried french fries. J Food Eng 305:110587. doi:10.1016/j.jfoodeng.2021.110587",
    "MUNIANDY2021": "Muniandy A et al. (2021) Dynamic thermal properties estimation using sensitivity coefficients for rapid heating process. Foods 10:1954. doi:10.3390/foods10081954",
    "NDISYA2022": "Ndisya J, Gitau A, Roman F, Mbuge D, Sturm B, Hensel O (2022) Simulation of transient heat transfer during forced convection cooling of cocoyam tubers. Heliyon 8(12):e12360. doi:10.1016/j.heliyon.2022.e12360 (PMC9793272)",
    "CUESTA2021": "Cuesta F, Sanchez-Alonso I, Navas A, Careche M (2021) Calculation of full process freezing time in minced fish muscle. MethodsX 8:101292. doi:10.1016/j.mex.2021.101292 (PMC8374274)",
    "USDA_AMS_CARROT": "USDA AMS, United States Standards for Grades of Frozen Carrots (39 FR 2096; effective 28 Feb 1974; corrected and reprinted 26 Nov 2025). https://ams-prod.azureedge.us/sites/default/files/media/Frozen_Carrots_Standard%5B1%5D.pdf",
    "FDA_CU": "US FDA Consumer Update 'Are You Storing Food Safely?' (content current as of 18 Jan 2023). https://www.fda.gov/consumers/consumer-updates/are-you-storing-food-safely",
    "FOODCODE": "US FDA Food Code 2022 (Jan 18 2023 version). https://www.fda.gov/media/164194/download",
    "FSA_UK": "UK Food Standards Agency, How to chill, freeze and defrost food safely (GOV.UK, 18 Dec 2017). https://www.gov.uk/government/publications/how-to-chill-freeze-and-defrost-food-safely/how-to-chill-freeze-and-defrost-food-safely",
    "OVCA2021": "Ovca A, Skufca T, Jevsnik M (2021) Temperatures and storage conditions in domestic refrigerators - Slovenian scenario. Food Control 123:107715. doi:10.1016/j.foodcont.2020.107715 (PMC7571380)",
    "STEFANOU2023": "Stefanou C-R, Szosland-Faltyn A, Bartodziejska B (2023) Survey of domestic refrigerator storage temperatures in Poland for use as a QMRA tool for exposure assessment. Int J Environ Res Public Health 20:2924. doi:10.3390/ijerph20042924 (PMC9957224)",
    "EU89_108": "Council Directive 89/108/EEC on quick-frozen foodstuffs for human consumption. https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:31989L0108",
    "NWS_PA": "US National Weather Service (El Paso), wxcalc sheet 'Pressure Altitude'. https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf",
    "FSIS_HA": "USDA FSIS fact sheet 'High Altitude Cooking and Food Safety' (2011 PDF, GPO copy). https://www.govinfo.gov/content/pkg/GOVPUB-A110-PURL-gpo62705/pdf/GOVPUB-A110-PURL-gpo62705.pdf",
    "NMSU_E215": "Flores NC, Schlenker Davies C (rev.) High-Altitude Cooking, Guide E-215, New Mexico State Univ. College of ACES (rev. Nov 2015). https://pubs.nmsu.edu/_e/E215/",
    "FDA_ITG7": "US FDA Inspection Technical Guide No. 7 'Sterilizing Symbols (D, z, F)' (1/9/72). https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-guides/sterilizing-symbols-d-z-f",
    "BABU2022": "Babu PS, Pulissery SK, Jaganath B, Obaiah MC (2022) Effect of thermal processing on quality of tender jackfruit in tin-free-steel cans. J Food Sci Technol 59(5):2035-2046. doi:10.1007/s13197-021-05218-x (PMC9046495)",
    "HB66": "USDA ARS Agriculture Handbook 66, The Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks (rev. Feb 2016). https://www.ars.usda.gov/arsuserfiles/oc/np/commercialstorage/commercialstorage.pdf",
    "SINGH_HO": "Singh RP, lecture handout 'Problems Involving Phase Change - Freezing' (PDF title '94 Lecture Freezing', 2013; author of Singh & Heldman). https://mail.rpaulsingh.com/lectures/freezing_handout.pdf",
    "FAO_FISH": "FAO, Freezing and refrigerated storage in fisheries, Section 5 'Freezing time'. https://www.fao.org/4/V3630E/V3630E06.htm",
    "JIMENEZ2013": "Jimenez-Avalos HA, Chaires-Martinez L, Perez-Vargas MA (2013) Prediction of freezing time and evaluation of the effect of frozen storage on textural properties of white trout fillets. Food Sci Technol Res 19(3):375-. doi:10.3136/fstr.19.375",
    "MERAI2019": "Merai M et al. (2019) Experimental characterization and modelling of refrigeration of pork carcasses during transport in field conditions. 25th IIR Int. Congress of Refrigeration. doi:10.18462/iir.icr.2019.0179",
    "BENAMARA2005": "Ben Amara S (2005) Natural convection flows and heat transfers in macroporous food media: application to household refrigerators. PhD thesis (HAL tel-02586567)",
    "TB1292": "Bennett AH (1963) Thermal Characteristics of Peaches as Related to Hydrocooling. USDA Technical Bulletin 1292. https://hortscans.ces.ncsu.edu/uploads/t/h/thermal__51bf41b2198df.pdf",
    "OZUNA2013": "Ozuna C, Puig A, Garcia-Perez JV, Mulet A, Carcel JA (2013) Influence of high intensity ultrasound application on mass transport, microstructure and textural properties of pork meat (Longissimus dorsi) brined at different NaCl concentrations. J Food Eng 119(1):84-93. doi:10.1016/j.jfoodeng.2013.05.016 (author version: https://riunet.upv.es/bitstream/10251/72942/3/author%20version.pdf)",
    "WANG2000": "Wang D, Tang J, Correia LR (2000) Salt diffusivities and salt diffusion in farmed Atlantic salmon muscle as influenced by rigor mortis. J Food Eng 43:115-123 (PDF: https://wpcdn.web.wsu.edu/wp-labs/uploads/sites/1254/2016/05/tang45.pdf)",
    "KHOMIAKOVA2023": "Khomiakova M (2023) Mathematical model and dependence of fish salting process duration to a given salt concentration. Braz J Food Technol 26:e2023049. doi:10.1590/1981-6723.04923",
    "CASALES2009": "Casales MR, Capaccioni ME, Yeannes MI (2009) [equilibrium times and acid and salt diffusion coefficients for marinating Engraulis anchoita fillets]. Cienc Tecnol Aliment 29(4). doi:10.1590/S0101-20612009000400035",
    "CHO1988": "Cho H-Y, Kim J-B, Pyun Y-R (1988) Diffusion of sodium chloride in Chinese cabbage during salting. Korean J Food Sci Technol 20(5):711-717. https://koreascience.or.kr/article/JAKO198803041936417.page",
    "PASSOS2005": "Passos FV, Felder RM, Fleming HP, McFeeters RF, Ollis DF (2005) Dynamic model for mass transfer of solutes in cucumber fermentation. J Food Eng 68:297-302. doi:10.1016/j.jfoodeng.2004.06.002",
    "LEBERT2014": "Lebert A, Daudin J-D (2014) Modelling the distribution of aw, pH and ions in marinated beef meat. Meat Sci 97(3):347-357. doi:10.1016/j.meatsci.2013.10.017",
    "ARROQUI2002": "Arroqui C, Rumsey TR, Lopez A, Virseda P (2002) Losses by diffusion of ascorbic acid during recycled water blanching of potato tissue. J Food Eng 52(1):25-30. doi:10.1016/S0260-8774(01)00081-4",
    "LEE2018": "Lee S, Choi Y, Jeong HS, Lee J, Sung J (2018) Effect of different cooking methods on the content of vitamins and true retention in selected vegetables. Food Sci Biotechnol 27(2):333-342. doi:10.1007/s10068-017-0281-1 (PMC6049644)",
    "GIL1999": "Gil MI, Ferreres F, Tomas-Barberan FA (1999) Effect of postharvest storage and processing on the antioxidant constituents (flavonoids and vitamin C) of fresh-cut spinach. J Agric Food Chem 47(6):2213-. doi:10.1021/jf981200l (PMID 10794612)",
    "PINHEIRO2023": "Coelho Pinheiro MN, Castro LMMN (2023) Effective moisture diffusivity prediction in two Portuguese fruit cultivars (Bravo de Esmolfe apple and Madeira banana) using drying kinetics data. Heliyon 9(7):e17741. doi:10.1016/j.heliyon.2023.e17741 (PMC10336512)",
    "BOTELHO2011": "Botelho FM et al. (2011) Periods of constant and falling-rate for infrared drying of carrot slices. Rev Bras Eng Agric Ambient 15(8). doi:10.1590/S1415-43662011000800012",
    "NCHFP_PICKLE": "NCHFP, 'General Information on Pickling'. https://nchfp.uga.edu/how/pickle/general-information-pickling/general-information-on-pickling/",
    "NCHFP_KRAUT": "NCHFP, Sauerkraut recipe (adapted from USDA Complete Guide to Home Canning, AIB 539, rev. 2015). https://nchfp.uga.edu/how/ferment/recipes/sauerkraut/",
    "NCHFP_DILL": "NCHFP, Fermented Dill Pickles (adapted from USDA AIB 539, rev. 2015). https://nchfp.uga.edu/how/ferment/recipes/dill-pickles/",
    "NCHFP_DEHYD": "NCHFP, 'Food Dehydrators', from So Easy to Preserve 6th ed. 2014 (UGA Bulletin 989). https://nchfp.uga.edu/how/dry/drying-general/food-dehydrators/",
    "NCHFP_JERKY": "NCHFP, 'Jerky', from So Easy to Preserve 6th ed. 2014 (UGA Bulletin 989). https://nchfp.uga.edu/how/dry/recipes/jerky/",
    "CERNELA2015": "Cernela J et al. (2015) Experimental study of heat and mass transfer phenomena during the contact heating of solid food models. J Food Eng. doi:10.1016/j.jfoodeng.2014.09.007",
}

H = ["key", "quantity", "current_value_or_range", "proposed_range", "unit", "matrix_scope", "source_citation",
     "locator", "source_type", "verification", "notes"]

V, U = "VERIFIED_OPENED", "UNVERIFIED_CANDIDATE"
AI = "[AI_DRAFTED, PROPOSED] "


def row(key, q, cur, prop, unit, scope, cites, loc, stype, ver, notes):
    return dict(key=key, quantity=q, current_value_or_range=cur, proposed_range=prop, unit=unit, matrix_scope=scope,
                source_citation=" || ".join(C[c] if c in C else c for c in cites), locator=loc, source_type=stype,
                verification=ver, notes=AI + notes)


R = []
# ------------------------------------------------- heat rows (keys from registry/scenario_defaults_v1.csv) ----
R += [
    row("SD-001", "bath_temperature (simmer, PROC-000020)", "85 / 90 / 95", "85 / 90 / 95 (unchanged)", "degC",
        "liquid around food during simmering; sea level", ["KIMINDU2025", "TAJIMA2001", "FLANNERY2014"],
        "Kimindu 2025 abstract (simmering defined as 85 C for 1 h); Tajima 2001 abstract (simmering in sub-boiling water at 95 C for 3 h, beef); Flannery 2014 abstract (simmering water about 70 C, mussels). All abstracts read via Europe PMC REST.",
        "PRIMARY", V,
        "Operational definitions used in three primary studies, not a standard definition: 85 and 95 C bracket the registry triple; 90 is the midpoint (arithmetic). Flannery used about 70 C, so a GENTLE sensitivity case near 70 C is defensible. A US Navy cook-training glossary (NAVEDTRA 14163) giving roughly 190-210 F was seen only in a search summary: UNVERIFIED. Simmer can never exceed the local boiling point (see LSRC-ALT-BOIL)."),
    row("SD-002", "bath_temperature (poach, PROC-000021)", "70 / 80 / 90", "70 / 80 / 90 (unchanged; UNVERIFIED); eggs: high bound up to 100", "degC",
        "poaching liquid; fish, poultry, fruit, eggs", ["CANO2026"],
        "Cano 2026 abstract (poached eggs prepared in boiling water for up to 8 min), via Europe PMC REST",
        "PRIMARY", U,
        "No opened source gives the 70-90 C convention for poaching (culinary texts are the candidates: CIA The Professional Chef; McGee On Food and Cooking; not opened). The one verified primary study poached eggs in boiling water, so an egg-specific INTENSE bound of 100 C has support; a Europe PMC search for poaching temperatures returned no other usable abstract."),
    row("SD-003", "bath_temperature (blanch, PROC-000023)", "95 / 98 / 100", "100 / 100 / 100 at sea level (boiling water); at altitude use the local boiling point (LSRC-ALT-BOIL, e.g. 93.3 at 2000 m)", "degC",
        "water blanching of vegetables (home freezing practice)", ["NCHFP_BLANCH", "NIST_SAT", "NWS_PA"],
        "NCHFP Blanching Vegetables page: water blanching in boiling water, about one gallon of water per pound of vegetables, water must return to the boil within 1 min, timing starts at the return to boil; steam blanching takes about 1.5 times longer; cool in water at 60 F or below. Altitude value derived (see LSRC-ALT-BOIL).",
        "GOV", V,
        "Physical definition: boiling water is 100 C at 1 atm (Layer 1). The registry's 95-98 C lower values have no source; the only real downward uncertainty is altitude and the short dip after the load goes in (NCHFP limits it to 1 min, not quantified in C). Same page states that under-blanching stimulates enzyme activity and is worse than no blanching (used in the mechanism-window file). Water ratio: LSRC-WATER-RATIO-BLANCH."),
    row("SD-004", "bath_temperature (braise, PROC-000024)", "85 / 90 / 95", "85 / 90 / 95 (unchanged; by analogy with SD-001, UNVERIFIED for braising)", "degC",
        "braising liquid (stove-top or oven)", ["candidate: culinary texts (The Professional Chef; On Food and Cooking); USDA cooking-yield tables name 'Braised' as a method but give no temperature"],
        "not opened", "HANDBOOK", U,
        "No opened source states a braising-liquid temperature. The local USDA meat and poultry cooking-yields table (data/external/usda_yields) lists Braised and Poached/Simmered/Stewed methods without temperatures. A 2025 LWT ultrasound-assisted braising study used 90 C (Europe PMC abstract), but the link to braising practice is inferred, so it is not cited as support."),
    row("SD-005", "bath_temperature (stew, PROC-000025)", "85 / 90 / 95", "85 / 90 / 95 (unchanged; by analogy with SD-001, UNVERIFIED for stewing)", "degC",
        "stewing liquid", ["candidate: culinary texts; see SD-001 primary sources for simmering"],
        "not opened", "HANDBOOK", U,
        "Same situation as SD-004. Stewing at a simmer is a convention; the simmer sources (SD-001) can be adopted only if the humans accept stewing = simmering."),
    row("SD-006", "bath_temperature (pressure-cook, PROC-000027)", "110 / 118 / 121", "108 / 115 / 121 (5 / 10 / 15 psig at sea level)", "degC",
        "saturated steam, air vented, sea-level atmosphere", ["NIST_SAT", "NCHFP_G1"],
        "NIST saturation table rows (19.736 psia -> 108.45 C; 24.784 psia -> 115.31 C; 29.661 psia -> 120.92 C; 30.248 psia -> 121.54 C); NCHFP Guide 1: low-acid foods processed at 240-250 F, reached at 10-15 psig; 10.5 psig gives 240 F at sea level",
        "GOV", V,
        "DERIVED by linear interpolation at 14.696 + gauge psia: 5 psig 108.4 C, 10 psig 115.2 C, 15 psig 121.0 C. The registry's 110 and 118 C correspond to about 6.1 and 12.3 psig, i.e. no standard gauge setting. At altitude the same gauge reading gives less (15 psig at 2000 m about 117.4 C, derived). Operating pressure of electric multicookers vs stove-top cookers: not sourced."),
    row("SD-007", "bath_temperature (scald, PROC-000150)", "80 / 83 / 85", "80 / 83 / 85 (unchanged; UNVERIFIED)", "degC",
        "milk heated to just below the boil", ["candidate: culinary texts; no GOV or primary source located"],
        "not opened", "HANDBOOK", U,
        "Recipe 'scald' is ambiguous: heating milk to just below the boil vs pouring boiling water over produce (peeling). Propose splitting by object before any number is used. No source opened for either meaning."),
    row("SD-008", "bath_temperature (deep-fry oil, PROC-000011)", "160 / 175 / 190", "160 / 175 / 190 (unchanged); potato products: 160-175", "degC",
        "frying oil; French fries and cut potato products (EU text); other foods in the frying literature", ["EU2017_2158", "SAHIN1999", "SERUGA2005"],
        "EU 2017/2158 Annex I Part I(b), information to end users (keep 160-175 C when frying; 180-220 C in an oven); Annex II Part A point 1 (food-service frying of French fries below 175 C); Sahin 1999 abstract (oil 150-190 C); Seruga 2005 abstract (oil 160-190 C)",
        "STANDARD", V,
        "The EU text is an acrylamide mitigation instruction for potato products, not a description of all frying; the 190 C INTENSE value is supported only by experimental oil temperatures in frying studies (150-190 C). For starchy potato products the humans may cap INTENSE at 175 C."),
    row("SD-009", "bath_temperature (shallow-fry oil, PROC-000012)", "150 / 170 / 190", "150 / 170 / 190 (unchanged; UNVERIFIED for shallow frying)", "degC",
        "shallow frying oil", ["EU2017_2158", "IKEDIALA1996", "OU2006"],
        "related anchors only: EU 2017/2158 Annex I Part I(b) (frying 160-175 C, potato products); pan-frying studies at 140-180 C pan temperature (Ikediala 1996; Ou 2006 abstracts)",
        "STANDARD", U,
        "No opened source gives a shallow-fry oil temperature as such; the anchors concern deep frying of potato products or pan (contact) temperatures."),
    row("SD-010", "bath_temperature = pan contact temperature (pan-fry, fry, stir-fry, saute, sear, brown)", "140 / 170 / 200", "140 / 180 / 250 (merged row); or split: pan-fry/saute/brown 140 / 160 / 180 and stir-fry/sear 160 / 200 / 250", "degC",
        "heated pan or plate surface; meat patties, brassica vegetables", ["IKEDIALA1996", "OU2006", "NUGRAHEDI2017", "ROCCA2019"],
        "Ikediala 1996 abstract (single-sided pan-frying at 140 and 180 C); Ou 2006 abstract (double-sided pan-frying, 160 C pan recommended); Nugrahedi 2017 abstract (stir-frying at set pan temperatures 160-250 C for 1-8 min); Rocca-Polimeni 2019 abstract (heating surface 128, 215, 255 C)",
        "PRIMARY", V,
        "These are experimental set-points, not surveys of home practice. The registry high of 200 C is below the stir-frying and grilling set-points (250-255 C). The 200 C mid of the stir-fry split is a pick inside the 160-250 C stated range. Surface vs contact temperature: the food surface stays near 100 C while wet (LSRC-SURFACE-WET-CAP)."),
    row("SD-011", "bath_temperature (sweat, PROC-000017)", "100 / 120 / 140", "100 / 120 / 140 (unchanged; UNVERIFIED)", "degC",
        "gentle pan heat without browning", ["no source located"], "not opened", "HANDBOOK", U,
        "No source states a sweating temperature; the definition (no browning) is qualitative. Recommend keeping it QUALITATIVE (a no-browning flag) rather than a number."),
    row("SD-012", "bath_temperature (bake, roast, blind-bake: oven set-point)", "160 / 180 / 220", "163 / 180 / 220", "degC",
        "oven set-point (not oven air temperature); meat and poultry roasting (FSIS); oven-cooked potato products (EU)", ["FSIS_DZ", "EU2017_2158"],
        "FSIS Danger Zone fact sheet, Cooking paragraph (when roasting meat and poultry use an oven temperature no lower than 325 F); EU 2017/2158 Annex I Part I(b) (180-220 C when using an oven; preheat oven or air fryer to 180-220 C)",
        "GOV", V,
        "163 C = 325 F (conversion). Baking (cakes, bread) and low-oven drying are not covered by these sources. Set-point is not the air temperature: oven calibration error is UNKNOWN (LSRC-OVEN-ERR)."),
    row("SD-013", "bath_temperature (air-fry set-point, PROC-000008)", "180 / 190 / 200", "180 / 200 / 220", "degC",
        "air fryer set-point; potato products", ["EU2017_2158"],
        "EU 2017/2158 Annex I Part I(b), end-user information: preheat the cooking device (oven, air fryer) to 180-220 C",
        "STANDARD", V,
        "Scope is French fries and cut potato products; 200 C is the midpoint (arithmetic). Gouyo 2021 (air-fryer h) does not state the air temperature in its abstract."),
    row("SD-020", "gas_mark -> degC (GAS_1..GAS_9)", "140|150|170|180|190|200|220|230|240", "unchanged (UNVERIFIED); carry a set-point uncertainty band once LSRC-OVEN-ERR is sourced", "degC",
        "UK gas-oven thermostat marks", ["candidates: oven manufacturer manuals; UK cookery references (e.g. Oxford Companion to Food 'gas mark'); BBC Good Food is excluded under D-003"],
        "not opened", "HANDBOOK", U,
        "A targeted search found no official (gov.uk, standards body) conversion table; only commercial converter pages, which disagree by about 5 C at some marks. Not citable as is."),
    row("SD-030", "h, water / liquid around food (natural convection to boiling)", "200 / 600 / 1500", "200 / 500 / 1000 (1500 only as a rolling-boil sensitivity case)", "W/m2K",
        "generic engineering band; not food-specific", ["INCROPERA_MTU"],
        "Handout table: free convection of liquids 50-1000; forced convection of liquids 100-20,000; boiling/condensing 2500-100,000 W/m2K (textbook table number not printed on the handout)",
        "HANDBOOK", V,
        "Textbook seen only as reproduced in a university course handout. 200 and 500 are picks inside the stated free-convection band (agent judgement). An MSc thesis abstract (Lund 2022) says the fluid-to-particle h is higher in boiling than in simmering water (direction only). DERIVED Biot check: with k about 0.5 W/mK and 1 cm half-thickness, Bi = h/50, so for h above about 300 the centre trajectory hardly depends on h. No measured h for food in boiling water was opened (lead: CFD + experiment study of eggs in a water bath, J Food Sci, not opened)."),
    row("SD-031", "h, condensing steam / pressurised water", "1000 / 3000 / 8000", "1000 / 3000 / 8000 (unchanged; low end UNVERIFIED)", "W/m2K",
        "steam around food; generic band", ["INCROPERA_MTU", "candidates: Ling, Lund & Lightfoot 1976 J Food Sci doi:10.1111/j.1365-2621.1976.tb01167.x (non-condensable gases); Tung, Ramaswamy et al. 1984 J Food Sci (steam/air retorts)"],
        "Handout table, phase-change row (boiling/condensing): 2500-100,000 W/m2K",
        "HANDBOOK", U,
        "3000 and 8000 sit inside the opened band; 1000 is below it and would need the steam/air (non-condensable) literature, not opened. Because Bi >> 1 at all three values, the choice barely changes the trajectory."),
    row("SD-032", "h, frying oil (immersion, with bubbling)", "250 / 450 / 700", "200 / 500 / 850", "W/m2K",
        "deep-fat frying of potato, sweet potato, dough, pork; oil 90-190 C", ["SAHIN1999", "SOSA2006", "FARINU2007", "COSTA1999", "SERUGA2005", "MIRBEL2012", "HAKANSSON2019"],
        "Abstracts (Europe PMC REST): Sahin 1999 90-200 (model sample, oil 150-190 C); Sosa-Morales 2006 187.7-226.1 (pork, oil 90-110 C); Farinu 2007 peak 710-850, later stage 450-550 (sweet potato, 150-180 C); Costa 1999 peak 443-750 (potato); Seruga 2005 579-658 (dough, 160-190 C); Mir-Bel 2012 atmospheric peak 800-2000; Hakansson 2019 literature spread 4-7000",
        "PRIMARY", V,
        "500 is a pick inside the Farinu late-stage band 450-550; 850 is the Farinu peak maximum. h is strongly time-dependent (peak while the surface boils, then falls), so a single h is a simplification. The often-quoted 300-1100 range (Farkas & Hubbard 2000, Drying Technology) was seen only in a search summary: UNVERIFIED."),
    row("SD-033", "h, still-air oven (convection + radiation)", "15 / 25 / 40", "10 / 20 / 30 (PROVISIONAL; UNVERIFIED)", "W/m2K",
        "static (no fan) domestic oven", ["INCROPERA_MTU", "SAKIN2009"],
        "Handout table: free convection of gases 2-25 W/m2K (convection only); Sakin 2009 abstract opened but its static/fan values are only in the full text",
        "HANDBOOK", U,
        "No opened source gives a static-oven apparent h. Radiation adds roughly as much as free convection in an oven (agent estimate, not sourced). Sakin 2009 full-text tables would settle SD-033 and SD-034. Ovens give Bi of about 0.3-1.5, so this row matters most for the trajectories: verify it first."),
    row("SD-034", "h, forced-air (fan) oven / air fryer", "30 / 50 / 80", "fan oven 15 / 25 / 40; air fryer 66 / 71 / 76 (split the row)", "W/m2K",
        "domestic fan oven and commercial batch oven (Carson); hot-air frying of frozen pre-fried French fries (Gouyo)", ["CARSON2006", "GOUYO2021"],
        "Carson 2006 abstract (majority of measured data 15-40 W/m2K; about twice the laminar flat-plate prediction, partly due to radiation); Gouyo 2021 abstract (h 66-76 W/m2K identified by model fitting)",
        "PRIMARY", V,
        "Registry triple fits air fryers only. Carson values are apparent (convection + radiation), which is what a single-h centre model needs. Gouyo values are fitted, not measured, and come from one study. 25 and 71 are picks/midpoints inside the stated ranges."),
    row("SD-035", "h, effective pan contact with fat film", "200 / 500 / 1000", "100 / 300 / 512", "W/m2K",
        "contact heating of potato slices (with/without oil) and minced meat", ["VINE", "ROCCA2019"],
        "Vine abstract (contact h 512.2 +/- 12.4 with an oil layer, 197.5 +/- 5.8 without); Rocca-Polimeni 2019 abstract (h falls from 500 to 100 W/m2K between start and end of grilling)",
        "PRIMARY", V,
        "The registry high (1000) is about twice any opened value. 300 is a pick between the stated values. Older pan-frying contact-coefficient papers (Dagerskog & Sorenfors 1978; Ateba & Mittal) were not opened."),
    row("SD-040", "k, high-moisture food", "0.45 / 0.5 / 0.6", "0.41 / 0.50 / 0.60", "W/mK",
        "high-moisture plant foods above freezing; water as the upper bound", ["NIST_ISOBAR", "MUNIANDY2021", "NDISYA2022", "CUESTA2021"],
        "NIST isobaric rows: water k 0.55818 (1 C) to 0.67683 W/mK (99 C); Muniandy 2021 abstract: potato puree 0.463 (25 C) to 0.450 (140 C); Ndisya 2022 Table 2: cocoyam k_eff 0.414 (composition model); Cuesta 2021 Table 2 reproduces the Choi-Okos component equations",
        "GOV", V,
        "0.50 is a pick inside the opened values. Choi & Okos (1986) itself was not opened; its equations are verified only as reproduced (ASHRAE 2010 ch. 19 via Cuesta 2021). Composition-based k (SR Legacy water/protein/fat/carb) would replace this default."),
    row("SD-041", "alpha, high-moisture food", "1.2e-7 / 1.4e-7 / 1.6e-7", "1.10e-7 / 1.35e-7 / 1.60e-7", "m2/s",
        "high-moisture plant foods; water as the upper bound", ["NIST_ISOBAR", "NDISYA2022"],
        "NIST isobaric rows (k, rho, cp); Ndisya 2022 Table 2 (cocoyam alpha 1.099e-7 at 10 C, 1.098e-7 at 30 C)",
        "GOV", V,
        "DERIVED water alpha = k/(rho cp) from the NIST rows: 1.32e-7 (1 C), 1.44e-7 (22 C), 1.55e-7 (50 C), 1.67e-7 (99 C). 1.35e-7 is a pick inside this range."),
    row("SD-050", "half_thickness (minced, grated, shredded)", "0.0005 / 0.001 / 0.0015", "unchanged (UNVERIFIED)", "m",
        "home cut classes", ["candidates: culinary knife-cut tables (CIA The Professional Chef); no GOV size definition found for these classes"],
        "not opened", "HANDBOOK", U,
        "The USDA frozen-carrot standard defines chips (longest edge about 1/2 inch or less) but not grated or minced pieces."),
    row("SD-051", "half_thickness (sliced)", "0.0015 / 0.0025 / 0.004", "unchanged (UNVERIFIED); USDA Grade A frozen sliced carrots allow up to about 3/4 inch (19 mm) slice thickness, i.e. half-thickness <= 0.0095", "m",
        "home slicing vs commercial frozen carrot slices", ["USDA_AMS_CARROT"],
        "USDA AMS standard, Section 52.702(d) (slices cut transversely) and Table I, A classification (sliced: about 3/4-inch maximum thickness, 2-inch maximum diameter)",
        "GOV", U,
        "The commercial upper limit is much thicker than home slices; the 3-8 mm home convention is not sourced."),
    row("SD-052", "half_thickness (diced)", "0.003 / 0.005 / 0.008", "GOV anchor: Grade A diced carrots are cubes of 1/2 inch (12.7 mm) or less, i.e. half-thickness <= 0.00635; low and mid UNVERIFIED", "m",
        "commercial frozen diced carrots (USDA grade standard); home dicing", ["USDA_AMS_CARROT"],
        "USDA AMS standard, Section 52.702(e) (diced = approximate cube-shaped units) and Table I, A classification (approximate cube shapes 1/2 inch or less)",
        "GOV", U,
        "The registry high of 0.008 m (16 mm cube) exceeds the Grade A diced limit; home 'large dice' sizes would need a culinary source. Cubes are not slabs: the shape factor matters (packet Q4)."),
    row("SD-053", "half_thickness (chopped)", "0.003 / 0.006 / 0.012", "unchanged (UNVERIFIED)", "m",
        "home chopping (irregular pieces)", ["no source located"], "not opened", "HANDBOOK", U,
        "'Chopped' has no size definition in any opened source; keep as a wide UNVERIFIED class or treat size as UNKNOWN."),
    row("SD-060", "initial_temperature (all)", "4 / 20 / 25", "split by start state: FRIDGE 3 / 5 / 8 (sourced, see NH-001); ROOM unchanged 20 / 25 (UNVERIFIED); FROZEN -18 (see NH-002)", "degC",
        "food start temperature before a heat step", ["OVCA2021", "STEFANOU2023", "FOODCODE", "FDA_CU"],
        "see NH-001 (fridge surveys and limits)",
        "PRIMARY", U,
        "The fridge component is VERIFIED_OPENED (NH-001); the room component has no opened source (ISO 554 and IUPAC SATP not opened), so the row as a whole stays UNVERIFIED_CANDIDATE. A single T0 that mixes fridge and room starts hides a real input: the recipe text often says which (Layer 1)."),
]

# ------------------------------------------------- non-heat rows -------------------------------------------
R += [
    row("NH-001", "medium_temperature FRIDGE (domestic refrigerator air)", "2 / 5 / 8", "3 / 5 / 8", "degC",
        "household refrigerators (US/UK guidance; Slovenian and Polish surveys)", ["FDA_CU", "FOODCODE", "FSA_UK", "OVCA2021", "STEFANOU2023"],
        "FDA consumer update (fridge kept at 40 F (4 C) or colder); Food Code 2022 section 3-501.16(A)(2) p. 3-28 (cold holding 5 C / 41 F or less, food temperature); FSA guidance chilling section (fridge set between 0 and 5 C); Ovca 2021 Abstract + Results (24-h mean below 4 C in 20 %, 4-6 C in 30 %, above 6 C in 50 % of fridges; overall mean about 5.9, SD about 2.2); Stefanou 2023 Results (mean 5.1 C, SD 2.8; per-fridge means -1.2 to 15.2 C)",
        "PRIMARY", V,
        "DERIVED: low = survey mean - 1 SD (2.3 Poland, 3.7 Slovenia), high = mean + 1 SD (7.9, 8.1), rounded; mid 5 = the Food Code / FSA ceiling and near both survey means. Guidance values are ceilings, surveys are operating values. Which Slovenian mean is air vs test product should be re-checked in the Results."),
    row("NH-011", "medium_temperature ROLE_CHILL (unqualified chill = refrigerator)", "2 / 5 / 8", "3 / 5 / 8 (as NH-001)", "degC",
        "recipe 'chill' with no stated temperature", ["FSA_UK", "OVCA2021", "STEFANOU2023"],
        "as NH-001; FSA guidance (cool cooked food and put it in the fridge within 1-2 h)",
        "GOV", V,
        "Reading 'chill' as refrigeration is a modelling assumption (Layer 2), not a source statement; the numbers are NH-001's."),
    row("NH-002", "medium_temperature FREEZER", "-24 / -18 / -12", "TYPICAL -18; INTENSE (warm) -15; GENTLE: no opened source", "degC",
        "household freezers; commercial quick-frozen food", ["FDA_CU", "EU89_108", "FSA_UK"],
        "FDA consumer update (freezer 0 F / -18 C); Directive 89/108/EEC Art 5(1) (product kept at -18 C or lower) and Art 5(2)(a) (brief rises of no more than 3 C in transport, and in local distribution and retail display); FSA guidance (freezer around -18 C)",
        "STANDARD", V,
        "-15 = -18 + 3 C EU tolerance (arithmetic). A colder GENTLE value (around -22 C, chest freezers) appeared only in search summaries of two PMC papers (PMC9602642, PMC13264023): UNVERIFIED. The registry's -12 C has no source. FSIS freezing page returned 403."),
    row("NH-003", "medium_temperature ROOM", "18 / 21 / 25", "unchanged (UNVERIFIED)", "degC",
        "indoor kitchen air", ["candidates: ISO 554 (standard atmospheres 20 / 23 / 27 C); IUPAC standard ambient temperature 25 C (Gold Book)"],
        "not opened (ISO paywalled; IUPAC Gold Book returned 403)", "STANDARD", U,
        "Context (VERIFIED, FSIS Danger Zone sheet): guidance treats rooms above 90 F (32 C) as a separate case (1 h instead of 2 h), so hot kitchens exist; no opened source gives a room-temperature distribution."),
    row("NH-012", "medium_temperature ROLE_COOL (unqualified cool = room air)", "18 / 21 / 25", "unchanged (UNVERIFIED; as NH-003)", "degC",
        "recipe 'cool' with no stated medium", ["FSA_UK", "FSIS_DZ"], "FSA guidance (cool at room temperature, refrigerate within 1-2 h); FSIS sheet (2 h rule)",
        "GOV", U, "The guidance sources fix the time limit, not the room temperature; see LSRC-COOL-TIME."),
    row("NH-004", "medium_temperature ICE_BATH", "0 / 1 / 4", "unchanged (UNVERIFIED); partial anchor: blanch-cooling water must be 60 F (15.6 C) or below, about 1 lb ice per lb vegetables", "degC",
        "ice-water bath for cooling", ["NCHFP_BLANCH"],
        "NCHFP Blanching Vegetables page, cooling paragraph", "GOV", U,
        "Ice-water equilibrium at 0 C (1 atm) is a physical definition, but the bath temperature reached in practice (stirred vs still, ice fraction) is not sourced."),
    row("NH-005", "medium_temperature COLD_WATER", "5 / 12 / 20", "unchanged (UNVERIFIED); partial anchor: running-water thawing must use water at 21 C (70 F) or below", "degC",
        "cold tap / running water", ["FOODCODE", "NCHFP_BLANCH"],
        "Food Code 2022 section 3-501.13(B) (completely submerged under running water at 21 C or below, with enough velocity to agitate); NCHFP cooling water 60 F or below",
        "GOV", U, "Tap-water temperature by season and region: no source opened."),
    row("NH-006", "medium_temperature COOL_DARK (pantry / cellar)", "8 / 12 / 16", "unchanged (UNVERIFIED)", "degC",
        "pantry, cellar storage", ["candidate: USDA ARS Agriculture Handbook 66 storage chapters (commodity-specific storage temperatures, e.g. potatoes, onions)"],
        "not opened for this item", "GOV", U, "No generic 'cool dark place' definition exists in the opened sources."),
    row("NH-007", "medium_temperature WARM_PLACE (proving, culturing)", "24 / 30 / 38", "unchanged (UNVERIFIED)", "degC",
        "dough proving; yoghurt or ferment culturing", ["no source located"], "not opened", "HANDBOOK", U,
        "NCHFP fermentation temperatures (21-24 C kraut, see LSRC-FERMENT-T) are for vegetable fermentation, not dough proving."),
    row("NH-008", "medium_temperature DEHYDRATOR", "40 / 55 / 70", "29 / 60 / 71", "degC",
        "electric home dehydrators", ["NCHFP_DEHYD"],
        "NCHFP Food Dehydrators page (dehydrators dry efficiently at 140 F; look for an enclosed thermostat from 85 to 160 F)",
        "GOV", V,
        "60 C = 140 F; 29 and 71 C = 85 and 160 F thermostat range ends (conversion). 29 C is a thermostat floor, not a drying recommendation."),
    row("NH-009", "medium_temperature OVEN_LOW (oven drying)", "50 / 80 / 110", "unchanged (UNVERIFIED); partial anchor: jerky dried in a dehydrator or oven preheated to 140 F (60 C)", "degC",
        "low oven used for drying", ["NCHFP_JERKY"], "NCHFP Jerky page", "GOV", U,
        "Only the jerky case is sourced; the 80-110 C values are not."),
    row("NH-010", "medium_temperature PRESSURE_CANNER", "110 / 116 / 121", "115.6 / 118.3 / 121.1", "degC",
        "home pressure canning of low-acid foods, sea level", ["NCHFP_G1", "NIST_SAT"],
        "NCHFP Guide 1 (240-250 F at 10-15 psig); NIST saturation rows (see SD-006)",
        "GOV", V, "240 / 245 / 250 F converted; 245 F is the midpoint. Equals SD-006's 10-15 psig band; altitude lowers it."),
    row("NH-013", "medium_temperature ROLE_DEFROST", "4 / 12 / 22", "GENTLE and TYPICAL: refrigerator thawing (food kept at 5 C or below); INTENSE: running water at 21 C or below; microwave thawing only if cooked at once", "degC",
        "thawing of frozen food", ["FOODCODE", "FSA_UK"],
        "Food Code 2022 section 3-501.13(A)-(C) pp. 3-26/3-27; FSA defrosting section (defrost in the fridge, use within 24 h; microwave defrost only directly before cooking)",
        "GOV", V,
        "The medium changes with the bracket (air vs water), so h must switch with it (NH-027 vs NH-023). Cold-water thawing with water changed every 30 min (FSIS Big Thaw page) returned 403: UNVERIFIED."),
    row("NH-014", "post_heat_temperature (start of a cool/chill step after cooking)", "60 / 80 / 95", "unchanged (UNVERIFIED); anchors: cooling limits start at 57 C (135 F); hot holding at 57 C (Food Code) or 60 C / 140 F (FSIS)", "degC",
        "cooked food entering a cooling step", ["FOODCODE", "FSIS_DZ"],
        "Food Code sections 3-501.14 and 3-501.16; FSIS sheet (keep hot food at or above 140 F)", "GOV", U,
        "Better: take the start temperature from the previous step's Layer 2 end state (core_end_c), not a default."),
    row("NH-020", "h FRIDGE (still or weakly forced cold air, convection + radiation)", "5 / 10 / 20", "3 / 6 / 10", "W/m2K",
        "food in a domestic refrigerator or freezer cabinet", ["CUESTA2021", "MERAI2019", "BENAMARA2005", "INCROPERA_MTU"],
        "Cuesta 2021 Example 1 (h estimated indirectly as 5.67 W/m2K for a freezer cabinet with unknown air speed); Merai 2019 abstract (7.7 W/m2K used as model input, refrigerated transport); Ben Amara 2005 abstract (air velocity below 0.2 m/s; radiation and conduction of the same order as convection); handout free convection of gases 2-25",
        "PRIMARY", V,
        "3 and 10 are picks inside the generic free-convection band; 6 is close to the 5.67 estimate. Laguerre et al. 2008 (J Food Eng, HAL hal-02589659) abstract supports the low air velocity. The registry high of 20 is plausible only with a fan."),
    row("NH-021", "h FREEZER (still or weak forced air)", "5 / 12 / 25", "3 / 6 / 10 (still); forced-air freezers: see LSRC-H-FORCED-AIR", "W/m2K",
        "household freezer cabinet", ["CUESTA2021", "INCROPERA_MTU"], "as NH-020", "PRIMARY", V,
        "Same evidence as NH-020; the only freezer-specific value is the 5.67 indirect estimate."),
    row("NH-022", "h ROOM (still room air, convection + radiation); also NH-026 ROLE_COOL and NH-027 ROLE_DEFROST", "5 / 10 / 15", "unchanged (UNVERIFIED)", "W/m2K",
        "food cooling or resting in room air", ["INCROPERA_MTU", "BENAMARA2005"],
        "generic band only (free convection of gases 2-25, convection alone)", "HANDBOOK", U,
        "No food-in-room-air measurement opened. Radiation to room walls adds a few W/m2K for hot food (agent estimate, not sourced)."),
    row("NH-023", "h COLD_WATER (still to gently stirred)", "100 / 300 / 600", "100 / 300 / 600 (generic band only)", "W/m2K",
        "food immersed in cold water", ["INCROPERA_MTU"], "handout: free convection of liquids 50-1000 W/m2K", "HANDBOOK", V,
        "All three values are picks inside the generic band; no food-specific still-water measurement opened."),
    row("NH-024", "h ICE_BATH (stirred) / hydrocooling", "200 / 500 / 1000", "200 / 500 / 900", "W/m2K",
        "agitated ice water; flood-type hydrocooling of fruit", ["TB1292", "INCROPERA_MTU"],
        "USDA Technical Bulletin 1292 summary (film coefficient peaches-to-water 125-165 Btu per h per sq ft per F in flood-type hydrocoolers); handout free convection of liquids 50-1000",
        "GOV", V,
        "DERIVED conversion: 125-165 Btu/(h ft2 F) x 5.678 = 710-937 W/m2K (scanned 1963 bulletin, OCR text). 200 and 500 are picks inside the generic band. Poultry immersion-chilling paper (Carciofi & Laurindo 2010) gives no h value (negative result)."),
    row("NH-025", "h ROLE_CHILL (companion of NH-011, refrigerator air)", "5 / 10 / 20", "3 / 6 / 10 (as NH-020)", "W/m2K",
        "food chilled in a domestic refrigerator", ["CUESTA2021", "MERAI2019", "BENAMARA2005", "INCROPERA_MTU"],
        "as NH-020", "PRIMARY", V, "Same evidence and picks as NH-020; reading an unqualified chill as refrigerator air is a modelling assumption."),
    row("LSRC-H-FORCED-AIR", "h, forced-air (air-blast) chilling or freezing", "(no registry row)", "10 / 25 / 50", "W/m2K",
        "forced-air cooling of produce and foods at about 0.5-5 m/s", ["NDISYA2022", "INCROPERA_MTU"],
        "Ndisya 2022 Table 3 (h_overall 7.65-12.40 W/m2K at 0.5-0.9 m/s, from Re-Pr correlations, cocoyam); handout forced convection of gases 25-250",
        "PRIMARY", V,
        "Only the low end has a food-specific anchor (correlation-based). Becker & Fricke 2004 (Int J Refrig 27:540-551; h database behind the ASHRAE cooling-time chapter) not opened: the best source for this row."),
    row("NH-030", "density_food (high moisture)", "950 / 1050 / 1100", "unchanged (UNVERIFIED); anchor: water 999.9 (1 C) to 959.1 kg/m3 (99 C)", "kg/m3",
        "high-moisture foods", ["NIST_ISOBAR"], "NIST isobaric rows (density column)", "GOV", U,
        "Food density from composition (Choi-Okos component densities, as reproduced in Cuesta 2021 Table 1) would replace this default."),
    row("LSRC-LATENT-WATER", "latent heat of fusion of water L0", "(no registry row)", "333.6", "kJ/kg",
        "pure water (ice Ih -> liquid at 0 C)", ["CUESTA2021"],
        "Cuesta 2021 Symbols table and text after Eq. (30) (L0 = 333.6 kJ/kg, latent heat of fusion of water)",
        "PRIMARY", V,
        "Verified only as used in an open-access methods paper that follows the ASHRAE formulas; IAPWS R10-06 and the CRC Handbook (primary physical-property sources) were not opened."),
    row("NH-031", "latent_heat_freezing of a high-moisture food", "200000 / 250000 / 300000", "per food: (x_w0 - x_b) x 333.6 kJ/kg; with x_w0 0.60 / 0.75 / 0.90 and x_b = 0: 200 / 250 / 300 kJ/kg", "kJ/kg (registry uses J/kg)",
        "foods with 60-90 % water; x_b = bound (unfreezable) water fraction", ["CUESTA2021"],
        "Cuesta 2021 Eq. (30) (latent term scales L0 by initial water minus bound water); Eqs. (23)-(24) (ice fraction from unfrozen water and temperature)",
        "PRIMARY", V,
        "DERIVED: the 200/250/300 kJ/kg triple is arithmetic on assumed water fractions; the water fraction should come from composition (SR Legacy) per food, and x_b is not sourced here (it lowers L)."),
    row("NH-032", "freezing_point (initial / highest freezing temperature), class overview", "-2.0 / -1.0 / -0.5", "-3.0 to -0.2 across produce classes (see NH-032:* rows); hake mince -1.3", "degC",
        "fresh produce (HB66); minced fish (Cuesta)", ["HB66", "CUESTA2021"],
        "HB66 commodity chapters (see class rows); Cuesta 2021 Example 1 (estimated initial freezing temperature of hake mince about -1.3 C)",
        "GOV", V, "Freezing point falls as soluble solids rise (HB66). Class values below; use the class row, not this overview."),
    row("NH-032:LEAFY_STEM", "freezing_point class LEAFY_STEM", "(new)", "-0.5 / -0.35 / -0.2", "degC",
        "lettuce, bok choy, celery, chicory", ["HB66"],
        "HB66 commodity chapters, PDF pages (printed page = PDF page - 10): lettuce 397 (-0.2 C), bok choy 253 (-0.5), celery 288 (-0.5), chicory 297 (-0.5)",
        "GOV", V, "Mid = midpoint (arithmetic). Celery value attributed by HB66 to Whiteman 1957."),
    row("NH-032:BRASSICA", "freezing_point class BRASSICA", "(new)", "-1.0 / -0.9 / -0.8", "degC",
        "cabbage, Brussels sprouts, broccoli", ["HB66"],
        "HB66: cabbage PDF p. 266 (-0.9 to -0.83 C); Brussels sprouts (-0.8 C, chapter inferred from page context); broccoli freezing injury below -1 C",
        "GOV", V, "Brussels sprouts chapter assignment was inferred by the sub-lane: re-check."),
    row("NH-032:ROOT_TUBER_BULB", "freezing_point class ROOT_TUBER_BULB", "(new)", "-1.2 / -1.0 / -0.8", "degC",
        "carrot, parsnip, potato, onion, kohlrabi", ["HB66"],
        "HB66 PDF pages: carrot 275 (-1.2 C), parsnip 468 (-0.9), potato 517 (about -1), onion 448 (-0.8; the printed F value looks like a typo), kohlrabi 388 (-1)",
        "GOV", V, ""),
    row("NH-032:FRUIT_LOW_SSC", "freezing_point class FRUIT_LOW_SSC", "(new)", "-1.1 / -0.85 / -0.6", "degC",
        "tomato, apricot", ["HB66"],
        "HB66 general chapter PDF pp. 75-76 (tomatoes and parsnips freeze at -1.1 to -0.6 C); apricot chapter PDF p. 205 (-1.0 C)",
        "GOV", V, "Apple: no explicit value found in the HB66 apple chapter (UNVERIFIED)."),
    row("NH-032:FRUIT_HIGH_SSC", "freezing_point class FRUIT_HIGH_SSC", "(new)", "-3.0 / -2.0 / -1.5", "degC",
        "stone fruit, grapes, persimmon, Asian pear", ["HB66"],
        "HB66: peach and nectarine (-3 to -1.5 C, soluble-solids dependent); table grape berries (-3.0 C); persimmon (-2 C); Asian pear (-1.5 C)",
        "GOV", V, "Some chapter assignments were inferred from page context by the sub-lane (Asian pear p. 216, grape p. 355): re-check."),
    row("NH-032:MEAT_FISH_DAIRY_EGG", "freezing_point class MEAT / FISH / POULTRY / EGG / DAIRY", "(new)", "UNVERIFIED (hake mince -1.3 is the only opened value)", "degC",
        "animal foods", ["CUESTA2021", "candidate: ASHRAE Handbook - Refrigeration, Thermal Properties of Foods (table of initial freezing points); Whiteman 1957 (USDA)"],
        "Cuesta 2021 Example 1 (fish mince only)", "HANDBOOK", U,
        "Kim et al. 2020 (Food Sci Anim Resour 40:444; PMC7207096) give the -1 to -6 C maximum ice-crystal zone for meat, which is NOT an initial freezing point."),
    row("NH-033", "k_frozen (frozen high-moisture food)", "1.2 / 1.6 / 2.2", "unchanged (UNVERIFIED); anchor: ice k = 2.2196 - 6.2489e-3 T + 1.0154e-4 T^2 (T in C), i.e. 2.22 at 0 C and 2.39 at -20 C", "W/mK",
        "frozen foods; ice", ["CUESTA2021"],
        "Cuesta 2021 Table 2 (Choi-Okos ice equation as tabulated in ASHRAE 2010 ch. 19)", "PRIMARY", U,
        "Frozen-food k needs the ice fraction and a mixing model (perpendicular model in Cuesta 2021); the registry triple is not sourced."),
    row("NH-040:MEAT", "D_eff NaCl in meat (brining)", "1e-10 / 2.5e-10 / 6e-10 (NH-040, all tissues)", "1.24e-10 / 2.0e-10 / 4.0e-10", "m2/s",
        "lean pork (Longissimus dorsi), frozen-thawed, 10 mm slabs, 5 C, brine 50-280 kg/m3", ["OZUNA2013", "WANG2000"],
        "Ozuna 2013 Table 1 (control Ds 1.24-2.11e-10 m2/s) and Section 3 (literature range 2-4e-10 m2/s, citing Graiver 2006 and Vestergaard 2007); Wang 2000 Section 4.1 (pork lean 1.9-2.2e-10 at 4-5 C, back fat 0.28e-10, citing Fox 1980)",
        "PRIMARY", V,
        "4.0e-10 is AS_CITED by Ozuna (originals not opened). Fat slows uptake about 8-fold (as cited). Temperature dependence 2-25 C and beef values: gap. Ozuna assumed negligible external resistance, so Bi -> infinity is consistent for meat slabs."),
    row("NH-040:FISH", "D_eff NaCl in fish muscle", "(NH-040)", "0.88e-10 / 2.44e-10 / 1.45e-9", "m2/s",
        "Atlantic salmon (never frozen, 10 C) to thawed lean fish at 20-33 C", ["WANG2000", "KHOMIAKOVA2023"],
        "Wang 2000 Abstract and Section 4.1 (salmon 0.878-3.40e-10 by rigor state) and Table 2 (literature 1.14e-10 to 1.45e-9, incl. Baltic herring 2.44e-10 at 10 C); Khomiakova 2023 Section 3.2 (herring, saturated brine, 10 C: mean 0.73e-9)",
        "PRIMARY", V,
        "Table 2 values are AS_CITED (originals not opened); cod values in Wang Table 2 look inconsistent with temperature: re-check. Khomiakova's D varies with depth and time (not a constant-D Fick parameter)."),
    row("NH-040:VEGETABLE", "D_eff NaCl in vegetable tissue (salting)", "(NH-040)", "1.7e-11 (uptake; single verified value)", "m2/s",
        "Chinese cabbage stalk, salting", ["CHO1988", "PASSOS2005"],
        "Cho 1988 Abstract (absorption diffusivity 1.7e-11 m2/s; Ea 66 kJ/mol); Passos 2005 Abstract and Section 3 (whole cucumbers: stomata are the rate-determining step)",
        "PRIMARY", V,
        "Single value: widen before use. Desorption about 1.16e-10 came from a fetch summary, not a verbatim line: UNVERIFIED. For whole unpeeled cucumbers (and probably olives) a Bi -> infinity slab is wrong: skin/stomata resistance controls exchange. Olive flesh vs skin values: UNVERIFIED (Grasas y Aceites 2008 not reachable)."),
    row("NH-041:FISH", "D_eff acetic acid in fish (marinating)", "3e-10 / 8e-10 / 1.5e-9 (NH-041, all tissues)", "3.39e-10 / 3.44e-10 / 3.49e-10 (single study)", "m2/s",
        "anchovy (Engraulis anchoita) fillets 6.1 mm, 3 % acetic acid + 10 % NaCl, 20 C, 10:1 solution:fish", ["CASALES2009"],
        "Casales 2009 Abstract and Section 3 (acetic acid D 3.39e-6 and 3.49e-6 cm2/s at 20 C)",
        "PRIMARY", V,
        "Single study; widen before use. In the same runs NaCl was 2.39e-11 m2/s and not Fickian (pre-salted fillets). A grass-carp value near 6e-9 was seen only in a search summary (host unreachable): UNVERIFIED."),
    row("NH-041:VEGETABLE_MEAT", "D_eff acetic acid in vegetables and meat", "(NH-041)", "UNVERIFIED", "m2/s",
        "pickled cucumber, onion; marinated beef", ["PASSOS2005", "LEBERT2014"],
        "Passos 2005 Table 3 (whole cucumber: overall coefficients only, skin-limited, units ambiguous); Lebert & Daudin 2014 Abstract (apparent diffusivities used, no numbers)",
        "PRIMARY", U, "No opened source gives an internal acetic-acid diffusivity for vegetable or meat tissue."),
    row("NH-042", "D_eff WATER (soaking legumes, grains)", "1e-10 / 3e-10 / 1e-9", "unchanged (UNVERIFIED)", "m2/s",
        "soaking of legumes and grains", ["not searched (budget)"], "not opened", "PRIMARY", U,
        "Only meat moisture diffusivity during brining was opened (Ozuna 2013 Table 2: 0.17-1.83e-10 m2/s at 5 C), which is a different process."),
    row("NH-043", "D_eff MARINADE_OTHER", "5e-11 / 2e-10 / 6e-10", "unchanged (UNVERIFIED)", "m2/s",
        "soy, dairy, alcohol, oil-borne flavour", ["no source located"], "not opened", "PRIMARY", U,
        "Mixed marinade components have no common diffusivity; recommend QUALITATIVE (uptake flag) only."),
    row("NH-045", "overnight_duration", "480 / 600 / 720", "unchanged (UNVERIFIED)", "min",
        "meaning of 'overnight' in recipes", ["no source located"], "not opened", "HANDBOOK", U,
        "A language convention; the FSA advises defrosting in the fridge overnight but gives no duration. Corpus statistics (KGE quantiles) would be a better basis than a default."),
    row("NH-050", "wet_bulb_temperature of drying air", "25 / 32 / 40", "unchanged (UNVERIFIED)", "degC",
        "home oven or dehydrator air", ["no source located"], "not opened", "HANDBOOK", U,
        "Wet-bulb follows from air temperature and RH by psychrometrics; neither RH nor the psychrometric source was opened."),
    row("NH-051", "latent_heat_vaporisation of water", "2260000 / 2360000 / 2450000", "2.250e6 / 2.279e6 / 2.323e6 (at 102.5 / 91.5 / 74.2 C)", "J/kg",
        "water, saturation", ["NIST_SAT_H"],
        "NIST saturation rows (vapour minus liquid enthalpy): 74.240 C 2322.5; 91.457 C 2278.7; 102.53 C 2249.7 kJ/kg",
        "GOV", V,
        "DERIVED differences of printed enthalpies. The 20 C end of the registry range (about 2.45e6) was not in the fetched rows: UNVERIFIED."),
    row("NH-052", "water_content_db_initial", "3 / 6 / 9", "per food from composition: X = w / (1 - w); 75 / 86 / 90 % wet basis gives 3 / 6 / 9 kg/kg db", "kg/kg dry basis",
        "fresh fruit, vegetable or meat pieces", ["no source for the default; composition (SR Legacy water) is the right input"], "n/a", "GOV", U,
        "The conversion is arithmetic; the 75-90 % wet-basis range is an assumption, not sourced."),
    row("NH-053", "water_content_db_critical (end of constant-rate drying)", "1 / 2.5 / 4", "UNVERIFIED; recommend a falling-rate-only default (see LSRC-DRY-RATE-CLASS)", "kg/kg dry basis",
        "fruit and vegetable drying", ["BOTELHO2011"],
        "Botelho 2011 Results (critical moisture about 4.2 kg/kg db for infrared-dried carrot: from a fetch summary, not a verbatim line)", "PRIMARY", U,
        "If a constant-rate stage is absent (banana) or lasts minutes (carrot), a critical moisture content is not needed."),
    row("NH-054", "water_content_db_equilibrium", "0.05 / 0.1 / 0.2", "unchanged (UNVERIFIED)", "kg/kg dry basis",
        "warm low-humidity drying air", ["candidate: sorption-isotherm studies per food"], "not opened", "PRIMARY", U, ""),
    row("LSRC-DRY-DEFF", "effective moisture diffusivity in drying", "(no registry row)", "1e-10 / 4e-10 / 3.6e-9; Ea 28-66 kJ/mol", "m2/s",
        "apple and banana slices (35-50 C air, 1.6 m/s); carrot slices (infrared, 50-100 C)", ["PINHEIRO2023", "BOTELHO2011"],
        "Pinheiro & Castro 2023 Table 1 (apple 0.957-4.013e-10; banana 1.572-2.627e-10; Ea apple 36.40 and 65.93, banana 27.95 kJ/mol); Botelho 2011 Conclusions item 4 (carrot 8.94e-10 to 3.57e-9) and Results (Ea 29.092 kJ/mol)",
        "PRIMARY", V,
        "1e-10 rounds 0.957e-10. Hot-air data at 60-80 C, meat (jerky) diffusivity and the Zogzas et al. 1996 compilation span (abstract opened, no number) are gaps."),
    row("LSRC-DRY-RATE-CLASS", "drying-rate class (constant vs falling rate)", "(no registry row)", "FALLING_RATE_ONLY default; optional short constant-rate stage (4-14 min) for very wet produce", "class",
        "fruit and vegetable slices", ["PINHEIRO2023", "BOTELHO2011"],
        "Pinheiro & Castro 2023 Sections 2.3 and 3 (banana: no constant drying-rate period; apple: two falling-rate periods); Botelho 2011 Results (constant rate lasted 14 min at 50 C to 4 min at 90 C, infrared)",
        "PRIMARY", V, "Thin-layer model families (Lewis, Page, Henderson-Pabis) were not sourced (context only)."),
    row("NH-060", "lethality_z (F0 convention)", "10 / 10 / 10", "8.9 / 10 / 11.1", "degC",
        "C. botulinum / mesophilic spores, low-acid canned foods", ["FDA_ITG7"],
        "FDA ITG No. 7 (F without subscript means 250 F with z = 18 F; spore z typically 16-20 F)",
        "GOV", V, "C conversions of 16 / 18 / 20 F. 21 CFR 113 and Codex CXC 23-1979 were not opened."),
    row("NH-061", "lethality_t_ref (F0 convention)", "121.1", "121.1", "degC", "low-acid canned foods", ["FDA_ITG7"],
        "FDA ITG No. 7 (reference exposure temperature 250 F)", "GOV", V, "250 F = 121.1 C (conversion)."),
    row("LSRC-COOK-VALUE", "cook value convention (scenario_layer.py: T_ref 100 C, z 33 C)", "T_ref 100, z 33 (code constants)", "T_ref 100, z 33 (keep)", "degC",
        "quality (cook) value of thermally processed foods", ["BABU2022"],
        "Babu 2022 Methods (cook value C0 at T_ref 100 C and z 33.1 C; lethality at 121.1 C or 85 C with z 10 C)",
        "PRIMARY", V,
        "This verifies the convention in current use, not its origin (Mansfield 1962; Ohlsson 1980 J Food Sci): UNVERIFIED. Quality z values vary widely by attribute; a single z = 33 C cook value is a dose index, not a nutrient model."),
    row("NH-070", "half_thickness JULIENNE", "0.001 / 0.0015 / 0.002", "unchanged (UNVERIFIED)", "m",
        "julienne strips", ["USDA_AMS_CARROT"],
        "USDA AMS standard Table I (strips: french-cut shapes 1/2 inch or more in length; cross-section not specified)", "GOV", U,
        "The USDA standard defines strip length, not the 2-4 mm cross-section."),
    row("NH-080", "liquid_removed_fraction DRAIN / STRAIN", "0.7 / 0.9 / 0.98", "unchanged (UNVERIFIED)", "fraction",
        "draining or straining cooked food", ["no source located"], "not opened", "HANDBOOK", U,
        "Retained surface film depends on piece size and surface area; no source opened."),
    row("LSRC-PLANK-SLAB", "Plank shape constants, infinite slab (P, R)", "(no registry row)", "P = 1/2 (0.5); R = 1/8 (0.125); a = full thickness", "dimensionless",
        "Plank equation t = rho L / (Tf - Ta) x (P a / h + R a^2 / k)", ["SINGH_HO", "FAO_FISH"],
        "Singh handout pp. 2-3 (general form and P/R table; slab derivation integrates from 0 to a/2); re-checked by the lane lead",
        "HANDBOOK", V,
        "Do NOT use FAO Table 8 for P and R: as published online it prints slab R = 0.25 and cylinder = sphere (cite FAO only for the assumptions: product pre-chilled, all heat removed at the initial freezing point, rough guide for irregular shapes)."),
    row("LSRC-PLANK-CYL", "Plank shape constants, infinite cylinder (P, R)", "(no registry row)", "P = 1/4 (0.25); R = 1/16 (0.0625); a = diameter", "dimensionless",
        "as LSRC-PLANK-SLAB", ["SINGH_HO"], "Singh handout p. 3 (P/R table)", "HANDBOOK", V, ""),
    row("LSRC-PLANK-SPHERE", "Plank shape constants, sphere (P, R)", "(no registry row)", "P = 1/6 (0.167); R = 1/24 (0.0417); a = diameter", "dimensionless",
        "as LSRC-PLANK-SLAB", ["SINGH_HO"], "Singh handout p. 3 (P/R table)", "HANDBOOK", V, ""),
    row("LSRC-PLANK-ACCURACY", "Plank freezing-time accuracy", "(no registry row)", "Plank under-predicts: mean error 25.11 % vs 5.7 % for the Nagaoka modification", "percent",
        "white trout fillets", ["JIMENEZ2013", "CUESTA2021"],
        "Jimenez-Avalos 2013 Abstract; Cuesta 2021 Eqs. 25-32 (ASHRAE Plank form extended by Cleland, with Stefan-number terms)",
        "PRIMARY", V,
        "Plank ignores sensible heat above and below the freezing point, so it gives a short (GENTLE-side) freezing time; Cleland/Pham-type corrections exist (Cuesta 2021)."),
    row("LSRC-ALT-BOIL", "boiling point of water vs altitude", "(no registry row; Layer 1 uses 100 C at 1 atm)", "0 m 99.97; 1000 m 96.65; 1500 m 94.98; 2000 m 93.31; 3000 m 89.97", "degC",
        "open vessel, standard-atmosphere pressure altitude", ["NIST_SAT", "NWS_PA", "FSIS_HA", "NMSU_E215"],
        "NIST saturation rows; NWS pressure-altitude formula; FSIS sheet p. 1 (boiling point drops just under 1 F per 500 ft; 208 F at 2,000 ft; about 198 F at 7,500 ft; high altitude = above 3,000 ft); NMSU E-215 Table 1 (212 / 208 / 202 / 198 F at 0 / 2,000 / 5,000 / 7,500 ft)",
        "GOV", V,
        "DERIVED: NWS formula -> pressure, NIST interpolation -> boiling point; matches FSIS within 0.3 F at 2,000 and 7,500 ft. Altitude is an input the recipe rarely states: treat as a Layer 2 uncertainty (packet Q6), never silently."),
    row("LSRC-OVEN-ERR", "oven set-point calibration error and thermostat cycling", "(no registry row)", "UNKNOWN (no citable value found)", "degC",
        "household ovens", ["candidates: IEC 60350-1 (household cooking appliances, performance test methods; paywalled); US DOE test procedure 10 CFR 430 Subpart B Appendix I (not opened)"],
        "not opened", "STANDARD", U,
        "Searches returned only blogs, forums and vendor pages (not citable). Recommendation: keep oven error out of the numbers until a measurement study or standard tolerance is opened; flag oven steps as SETPOINT_NOT_AIR_TEMPERATURE."),
    row("LSRC-COOL-TIME", "time limits for cooling cooked food", "(no registry row)", "into the fridge within 1-2 h (TYPICAL); Food Code limit: 57 -> 21 C within 2 h and to 5 C within 6 h total (INTENSE = slowest allowed)", "h",
        "cooked food cooled at home or in food service", ["FOODCODE", "FSA_UK", "FSIS_DZ"],
        "Food Code 2022 section 3-501.14(A) p. 3-27 (and cooling methods 3-501.15); FSA guidance (refrigerate within 1-2 h); FSIS sheet (refrigerate leftovers at 40 F or below within two hours; 1 h if the room is above 90 F)",
        "GOV", V, "These are safety limits, not measured practice; GENTLE (fast) cooling time is not sourced."),
    row("LSRC-WATER-RATIO-BLANCH", "water-to-food ratio, water blanching (sim_aa_1 r)", "(no registry row)", "8.35 L water per kg vegetables (8.35e-3 m3/kg)", "L/kg",
        "home water blanching of vegetables", ["NCHFP_BLANCH"],
        "NCHFP Blanching Vegetables page (one gallon water per pound of prepared vegetables)", "GOV", V,
        "DERIVED: 3.785 L / 0.4536 kg = 8.35 L/kg. sim_aa_1 takes r = V_w/m_t in m3/kg; this is a scenario value for blanching only."),
    row("LSRC-WATER-RATIO-BOIL", "water-to-food ratio, boiling vegetables (sim_aa_1 r)", "(no registry row)", "5 L water per kg food (1:5 by mass, single study)", "L/kg",
        "boiling of 10 vegetables in a retention study", ["LEE2018"],
        "Lee 2018 Materials and methods (vegetables added to just-boiling distilled water, 1:5 food:water) and Table 2 (vitamin C true retention 0-73.86 %)",
        "PRIMARY", V,
        "DERIVED: 1:5 by mass taken as about 5 L/kg (water density about 1 kg/L). The effect of the ratio on vitamin C was not measured in any opened source (gap); together with LSRC-WATER-RATIO-BLANCH this brackets 5-8.35 L/kg."),
    row("LSRC-D-AA-LEACH", "apparent diffusivity of ascorbic acid leaching into blanching water (sim_aa_1 k_L basis)", "(no registry row)", "1.23e-9 / 1.80e-9 / 2.43e-9 (at 65 / 80 / 93 C, distilled water)", "m2/s",
        "potato cylinders blanched in water at 65-93 C", ["ARROQUI2002"],
        "Arroqui 2002 Abstract (Arrhenius D0 8.63e-6 m2/s and Ea 24.89 kJ/mol in distilled water; D0 5.14e-7 m2/s and Ea 17.09 kJ/mol in recycled water)",
        "PRIMARY", V,
        "DERIVED from the stated Arrhenius parameters (100 C would be 2.83e-9 by extrapolation, not used). 'Apparent' D may fold in some degradation: check the full text. One matrix (potato) only. Converting D to the lumped k_L of sim_aa_1 needs the piece geometry (k_L ~ D x shape factor / L^2): a modelling step, not a source value."),
    row("LSRC-AA-LEACH-SHARE", "share of vitamin C found in the cooking water after boiling", "(no registry row)", "60 % of spinach vitamin C in the cooking water (single study)", "percent",
        "fresh-cut spinach, boiled", ["GIL1999"],
        "Gil 1999 Abstract (after boiling, 60 % of the vitamin C and 50 % of total flavonoids were found in the cooking water); re-checked by the lane lead",
        "PRIMARY", V,
        "Evidence that leaching (not only degradation) is a major route for leafy vegetables; it is an outcome, not a parameter. A broccoli study measuring vitamin C eluted into cooking water (Nakashima 2014, J-STAGE) gives numbers only in the Japanese full text (not opened)."),
    row("LSRC-VINEGAR-ACIDITY", "vinegar acidity for pickling", "(no registry row)", "5 % acidity (50 grain)", "percent acetic acid",
        "US home pickling", ["NCHFP_PICKLE"], "NCHFP General Information on Pickling page", "GOV", V,
        "The page also says not to change vinegar/food/water proportions or use vinegar of unknown acidity."),
    row("LSRC-FERMENT-T", "vegetable fermentation temperature and time", "(no registry row)", "15.6-18.3 C for 5-6 weeks; 21.1-23.9 C for 3-4 weeks", "degC",
        "sauerkraut; fermented dill pickles", ["NCHFP_KRAUT", "NCHFP_DILL"],
        "NCHFP sauerkraut recipe (70-75 F: 3-4 weeks; 60-65 F: 5-6 weeks); NCHFP fermented dill pickles (70-75 F for about 3-4 weeks; 55-65 F acceptable but 5-6 weeks)",
        "GOV", V, "F to C conversions."),
    row("LSRC-KRAUT-SALT", "salt level in sauerkraut", "(no registry row)", "UNVERIFIED as % w/w; recipe proportions verified (3 Tbsp salt per 5 lb cabbage; 3/4 cup per 25 lb)", "percent w/w",
        "home sauerkraut", ["NCHFP_KRAUT"], "NCHFP sauerkraut recipe (ingredients)", "GOV", U,
        "Converting tablespoons to grams needs a salt bulk density (about 18 g/Tbsp assumed by the sub-lane: not sourced), giving about 1.9-2.4 % w/w. The two NCHFP proportions disagree (15 vs 12 Tbsp per 25 lb)."),
    row("LSRC-PICKLE-BRINE", "NaCl in fermentation brine for cucumbers", "(no registry row)", "lab brine 8.6 wt % NaCl (Passos 2005); home recipe value UNVERIFIED", "percent w/w",
        "cucumber fermentation", ["PASSOS2005", "NCHFP_DILL"],
        "Passos 2005 Materials and methods (8.6 wt % NaCl brine); NCHFP dill pickles (1/2 cup salt + 1/4 cup 5 % vinegar + 8 cups water per gallon)", "PRIMARY", U,
        "The home recipe needs a salt-volume conversion (not sourced) to give a % (about 6.9 % by the sub-lane's assumption)."),
    row("LSRC-JERKY", "jerky drying and lethality conditions", "(no registry row)", "strips <= 6.4 mm; air 60 C; meat internal 71 C; 10-24 h", "mixed",
        "home meat jerky", ["NCHFP_JERKY"],
        "NCHFP Jerky page (slices no thicker than 1/4 inch; dehydrator or oven at 140 F; internal 160 F before or after drying; 10-24 h)", "GOV", V,
        "Poultry 165 F and the FSIS jerky page were not opened."),
    row("LSRC-SURFACE-WET-CAP", "surface temperature of a wet food surface on a hot plate", "(no registry row)", "surface capped near the boiling point while wet; rises above 100 C only after a crust forms", "degC",
        "gel emulsion and cereal batter models on a heated plate", ["CERNELA2015"],
        "Cernela 2015 Abstract (gel emulsion never exceeded 100 C regardless of plate temperature; batter exceeded 100 C only after crust formation)",
        "PRIMARY", V, "Supports a two-zone surface rule for packet Q3 (QUALITATIVE until a drying-front model exists)."),
    row("LSRC-DANGER-ZONE", "temperature band of rapid bacterial growth (context for rest/store)", "(no registry row)", "4.4-60 C (40-140 F); 2 h limit, 1 h above 32 C (90 F)", "degC",
        "perishable food out of refrigeration (US consumer guidance)", ["FSIS_DZ", "FOODCODE"],
        "FSIS Danger Zone sheet (40-140 F; never leave food out over 2 h; 1 h above 90 F); Food Code 2022 section 3-501.16 (cold holding 5 C or less, hot holding 57 C or more)", "GOV", V,
        "Context for STORAGE/RESTING scenario flags only; no microbial number is emitted."),
]

# ------------------------------------------------- write deliverable 1 -------------------------------------
keys = [r["key"] for r in R]
assert len(keys) == len(set(keys)), "duplicate keys"
out1 = REPO / "registry/scenario_defaults_source_review_S176.csv"
with open(out1, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=H, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    w.writeheader()
    for r in R:
        w.writerow(r)

# ================================================ deliverable 2 ============================================
rows = [json.loads(l) for f in ("S4.jsonl", "S5.jsonl") for l in open(SCR / f, encoding="utf-8")]

PARA = {  # paraphrase short source phrases that appeared in quote marks
    "'significantly inhibited'": "strongly inhibited", "'achieved'": "reached", "'almost complete'": "nearly complete",
    "'(almost) complete'": "(nearly) complete", "'short times'": "short (unquantified) times",
    "'only a few minutes'": "a few minutes", "'strongly pH dependent'": "strongly pH-dependent",
    "'gradually diminishes'": "diminishes progressively", "'much lower than'": "well below",
    "'consistent with inactivation of alliinase'": "consistent with alliinase inactivation",
    "'Total chewing work'": "total chewing work", "'rate increases with pH'": "rate rises with pH",
    "'~140 °C Maillard onset'": "~140 °C Maillard onset (folk claim)", "'Colorants'": "Colorants",
    "'Chlorophyll o'": "Chlorophyll o", "'dissociated form'": "dissociated form", "'no O2'": "no O2",
    "'is AA->DHA reversible?'": "whether AA->DHA is reversible", "'none'": "none", "'complete'": "complete",
    "'>80 °C, 10 min'": ">80 °C, 10 min", "'excess water'": "excess water",
    "'decreases with water content'": "decreases with water content",
}


def clean(s: str) -> str:
    s = s or ""
    for k, v in PARA.items():
        s = s.replace(k, v)
    s = s.replace("“", "").replace("”", "").replace("‘", "").replace("’", "'")
    s = s.replace('"', "")
    return re.sub(r"\s+", " ", s).strip()


def axis_norm(a: str) -> str:
    x = a.lower()
    if x.startswith("start condition"):
        return "START_MODE"
    if "heating rate" in x:
        return "HEATING_RATE"
    if "cell disruption" in x:
        return "CELL_DISRUPTION"
    if "microwave" in x:
        return "MICROWAVE_EXPOSURE"
    if x.startswith("time") or "heating time" in x or "time between" in x:
        return "STORAGE_TIME" if "storage" in x else "TIME"
    if "aqueous medium contact" in x:
        return "WATER_CONTACT"
    if x.startswith("water (co-substrate)") or "enzyme + water" in x:
        return "WATER_PRESENCE"
    if "water_activity" in x:
        return "WATER_ACTIVITY"
    if x.startswith("water_content") or "water content" in x:
        return "WATER_CONTENT"
    if x.startswith("oxygen"):
        return "OXYGEN"
    if "ca2+" in x:
        return "CALCIUM_IONS"
    if "metal" in x or "fe3+" in x or "zn2+" in x:
        return "METAL_IONS"
    if "bicarbonate" in x:
        return "BICARBONATE"
    if "cysteine" in x or "thiol" in x or "ascorbic acid (quinone" in x:
        return "REDUCTANT"
    if x.startswith("enzyme"):
        return "ENZYME_STATE"
    if x.startswith("salt_content"):
        return "SALT_CONTENT"
    if x.startswith("sugar_content"):
        return "SUGAR_CONTENT"
    if x.startswith("ph") or x.startswith("pH".lower()):
        return "PH"
    if x.startswith("temperature") or x.startswith("heat"):
        return "TEMPERATURE"
    return "OTHER"


MEDIUM_LOC = ("aqueous", "bulk solution", "model solvent", "bulk suspension", "bulk extract", "enzyme preparation",
              "enzyme extract", "broccoli juice", "tissue / cooking-water interface")


def loc_kind(raw: str) -> str:
    r = (raw or "").lower()
    if any(k in r for k in MEDIUM_LOC):
        return "MEDIUM"
    if r in ("n/a", "?", ""):
        return "UNKNOWN"
    if "headspace" in r:
        return "HEADSPACE"
    if r.startswith("bulk") or "whole sample" in r:
        return "WHOLE_ENTITY"
    return "TISSUE"


def cv_and_location(axis: str, raw_loc: str) -> tuple[str, str]:
    k = loc_kind(raw_loc)
    if axis == "TEMPERATURE":
        return ("CV-006" if k == "MEDIUM" else "CV-008"), "NOT_APPLICABLE"
    m = {"PH": "CV-013", "WATER_ACTIVITY": "CV-015", "WATER_CONTENT": "CV-016", "OXYGEN": "CV-021",
         "SALT_CONTENT": "CV-018", "SUGAR_CONTENT": "CV-019", "TIME": "CV-001", "STORAGE_TIME": "CV-040",
         "HEATING_RATE": "CV-011", "START_MODE": "CV-012", "WATER_CONTACT": "CV-022", "WATER_PRESENCE": "CV-022",
         "MICROWAVE_EXPOSURE": "CV-001|CV-029"}
    if axis in ("METAL_IONS", "CALCIUM_IONS", "BICARBONATE", "REDUCTANT", "ENZYME_STATE"):
        return "CV-023", ("TISSUE" if k in ("TISSUE", "WHOLE_ENTITY") else "MEDIUM")
    if axis == "CELL_DISRUPTION":
        return "NONE (history item cell_integrity, owner 16a)", "NOT_APPLICABLE"
    if axis == "OXYGEN":
        return "CV-021", "HEADSPACE"
    if axis in ("TIME", "STORAGE_TIME", "HEATING_RATE", "START_MODE", "MICROWAVE_EXPOSURE"):
        return m[axis], "NOT_APPLICABLE"
    if axis in m:
        return m[axis], ("TISSUE" if k in ("TISSUE", "WHOLE_ENTITY") else k)
    return "UNMAPPED", "UNKNOWN"


def canon(unit: str, v):
    if v in (None, ""):
        return "", ""
    u = (unit or "").strip()
    try:
        x = float(v)
    except (TypeError, ValueError):
        return "", ""
    if u.startswith("°C"):
        return "K", f"{x + 273.15:.2f}"
    if u.startswith("pH"):
        return "pH", f"{x:g}"
    if u.startswith("aw"):
        return "aw", f"{x:g}"
    if u.startswith("min"):
        return "s", f"{x * 60:g}"
    if u.startswith("h "):
        return "s", f"{x * 3600:g}"
    if u.startswith("s "):
        return "s", f"{x:g}"
    if u.startswith("% water") or u.startswith("% moisture") or u.startswith("% (w/w) water") or \
            u.startswith("% NaCl") or u.startswith("% sucrose") or u.startswith("% mol/mol O2") or \
            u.startswith("g NaCl per 100 g"):
        return "fraction", f"{x / 100:g}"
    return "", ""


PEAK_TYPE = {"S5-SG-01", "S5-SG-10", "S5-SG-11", "S5-PM-01", "S5-PM-04", "S5-PM-08", "S5-PM-09", "S5-PE-01"}

W = []
for r in rows:
    iid = r["item_id"]
    if iid == "S4-35":  # replaced by the lane-lead verified Ryan-Stoneham & Tong row below
        continue
    mk = "LEACHING" if r["mechanism_key"] == "LEACHING_VITAMIN_C" else r["mechanism_key"]
    axis = axis_norm(r["condition_axis"])
    cv, loc = cv_and_location(axis, r["location"])
    wtype = r["window_type"]
    basis = clean(r["window_type_justification"])
    notes = clean(r["notes"])
    mn, mns, mx, mxs = r["min_value"], r["min_status"], r["max_value"], r["max_status"]
    if iid == "S4-01":  # metal catalysts: schema rule M-1 encodes catalysts as MODULATING gates
        wtype = "MODULATING"
        basis = ("Evidence: in catalytic-metal-free, air-saturated pH 7 buffer ascorbate did not autoxidise (loss below "
                 "detection), i.e. NECESSARY in that model system. Encoded MODULATING: the MECH schema treats metal ions as "
                 "CATALYST modifiers (MODULATING gate, rule M-1), and a metal-free medium is not a cooking condition; a "
                 "NECESSARY gate would turn the usual UNKNOWN metal input into UNKNOWN for every AA oxidation (H4, D21-20).")
    if iid in PEAK_TYPE and mns == "STATED":  # a peak (or undefined Tgel) is not an onset: no NECESSARY lower bound
        notes = (f"Peak-type or undefined transition temperature {mn} °C moved from min to notes: a peak is not an "
                 f"onset, so it must not become a NECESSARY lower bound (values just below it would wrongly screen "
                 f"NOT_POSSIBLE). " + notes)
        mn, mns = None, "NOT_REPORTED"
    cu, cmin = canon(r["unit"], mn)
    cu2, cmax = canon(r["unit"], mx)
    stype = r["source_type"]
    if stype == "DATABASE":
        stype = "DATABASE (curated enzyme nomenclature, ExPASy ENZYME; not PRIMARY)"
    W.append(dict(
        mechanism_key=mk, condition_axis=axis, axis_detail=clean(r["condition_axis"]), cv_id_proposed=cv,
        location=loc, window_type=wtype, window_type_basis=basis, direction_of_effect=clean(r["direction_of_effect"]),
        matrix_scope=clean(r["matrix_scope"]),
        min_value="" if mn in (None, "") else mn, min_status=mns, max_value="" if mx in (None, "") else mx,
        max_status=mxs, unit=clean(r["unit"]), canonical_unit=cu or cu2, min_canonical=cmin, max_canonical=cmax,
        time_qualifier=clean(r["time_qualifier"]), source_citation=clean(r["source_citation"]),
        doi_or_url=clean(r["doi_or_url"]), source_type=stype, evidence_locator=clean(r["locator"]),
        verification=r["verification"], usable_for="QUALITATIVE_ONLY", status="AI_DRAFTED_CANDIDATE_PENDING_H4",
        notes=(f"Evidence location as reported: {clean(r['location'])}. " + notes).strip(), _src=iid))

# ---- lane-lead additions (opened in this session) ----
ADD = [
    dict(mechanism_key="CHLOROPHYLL_TO_PHEOPHYTIN", condition_axis="PH", axis_detail="pH (explicit rate direction)",
         cv_id_proposed="CV-013", location="TISSUE", window_type="MODULATING",
         window_type_basis="The degradation rate constant fell log-linearly as pH rose: a continuous rate effect with no "
                           "cut-off, so pH cannot be a NECESSARY gate for this chemical reaction (answers EQ21-07a in "
                           "direction; the studied pH range is not in the abstract).",
         direction_of_effect="higher pH -> slower chlorophyll degradation (log-linear)", matrix_scope="peas (pH held within +/-0.1 of target)",
         min_value="", min_status="NOT_REPORTED", max_value="", max_status="NOT_REPORTED", unit="pH",
         canonical_unit="", min_canonical="", max_canonical="", time_qualifier="heating conditions in full text",
         source_citation="Ryan-Stoneham T, Tong CH (2000) Degradation kinetics of chlorophyll in peas as a function of pH. J Food Sci",
         doi_or_url="doi:10.1111/j.1365-2621.2000.tb10600.x | fetched: Europe PMC REST search (DOI/title query)",
         source_type="PRIMARY", evidence_locator="Abstract (Europe PMC REST record)", verification="VERIFIED_OPENED",
         usable_for="QUALITATIVE_ONLY", status="AI_DRAFTED_CANDIDATE_PENDING_H4",
         notes="Opened by the lane lead. Koca et al. 2007 (same mechanism, pH 5.5-7.5) gives pH-specific activation energies "
               "but no direction in its abstract. Schwartz & von Elbe 1983 and LaBorde & von Elbe 1990 remain unopened."),
    dict(mechanism_key="LEACHING", condition_axis="TEMPERATURE", axis_detail="blanching water temperature (ascorbic acid leaching)",
         cv_id_proposed="CV-006", location="NOT_APPLICABLE", window_type="MODULATING",
         window_type_basis="Apparent AA diffusivity followed an Arrhenius law over 65-93 °C (Ea 24.89 kJ/mol in distilled "
                           "water): leaching speeds up with T, no threshold.",
         direction_of_effect="higher water T -> faster AA leaching", matrix_scope="potato cylinders, water blanching (distilled vs recycled water)",
         min_value=65, min_status="OPEN_STATED", max_value=93, max_status="OPEN_STATED", unit="°C",
         canonical_unit="K", min_canonical="338.15", max_canonical="366.15", time_qualifier="blanching kinetics",
         source_citation=C["ARROQUI2002"], doi_or_url="doi:10.1016/S0260-8774(01)00081-4", source_type="PRIMARY",
         evidence_locator="Abstract", verification="VERIFIED_OPENED", usable_for="QUALITATIVE_ONLY",
         status="AI_DRAFTED_CANDIDATE_PENDING_H4",
         notes="Opened by sub-lane S3 (abstract). Apparent D may fold in degradation; see scenario review row LSRC-D-AA-LEACH."),
    dict(mechanism_key="ENZYME_THERMAL_INACTIVATION", condition_axis="TIME", axis_detail="blanching dose (under-blanching)",
         cv_id_proposed="CV-001", location="NOT_APPLICABLE", window_type="MODULATING",
         window_type_basis="Extension guidance states that under-blanching stimulates enzyme activity and is worse than no "
                           "blanching: an insufficient heat dose leaves enzymes active (supports EQ21-09 qualitatively; not a measurement).",
         direction_of_effect="insufficient blanch -> enzyme activity stimulated", matrix_scope="vegetables blanched for home freezing",
         min_value="", min_status="NOT_REPORTED", max_value="", max_status="NOT_REPORTED", unit="n/a",
         canonical_unit="", min_canonical="", max_canonical="", time_qualifier="timing starts when the water returns to the boil (within 1 min)",
         source_citation=C["NCHFP_BLANCH"], doi_or_url="https://nchfp.uga.edu/how/freeze/freeze-general-information/blanching-vegetables/",
         source_type="GOV (extension guidance; not PRIMARY)", evidence_locator="Web page, reasons for blanching", verification="VERIFIED_OPENED",
         usable_for="QUALITATIVE_ONLY", status="AI_DRAFTED_CANDIDATE_PENDING_H4",
         notes="Opened by the lane lead. Same page: microwave blanching may not inactivate some enzymes (heat-transfer mode matters)."),
]
W += ADD

CATEGORICAL = ("CV-023", "CV-022", "CV-012")
for d in W:
    has_b = d["min_status"] != "NOT_REPORTED" or d["max_status"] != "NOT_REPORTED"
    # a numeric degC window belongs on a temperature axis, whatever the driver (enzyme activation, Ca pre-treatment)
    if has_b and d["unit"].startswith("°C") and d["condition_axis"] not in ("TEMPERATURE",):
        d["notes"] = (f"Axis re-assigned from {d['condition_axis']} to TEMPERATURE because the bounds are temperatures "
                      f"(the enzyme or ion is the driver named in axis_detail). " + d["notes"])
        d["condition_axis"] = "TEMPERATURE"
        d["cv_id_proposed"] = "CV-006" if d["location"] == "MEDIUM" else "CV-008"
        d["location"] = "NOT_APPLICABLE"
    # no numeric window on a categorical CV (schema semantic check): keep the studied levels in notes
    if has_b and d["cv_id_proposed"] in CATEGORICAL:
        lv = f"studied levels: min {d['min_value'] or '-'} ({d['min_status']}), max {d['max_value'] or '-'} ({d['max_status']}) {d['unit']}"
        d["notes"] = f"Numeric levels moved to notes because {d['cv_id_proposed']} is categorical ({lv}). " + d["notes"]
        d["min_value"] = d["max_value"] = d["min_canonical"] = d["max_canonical"] = d["canonical_unit"] = ""
        d["min_status"] = d["max_status"] = "NOT_REPORTED"
    if d["condition_axis"] == "OXYGEN":
        d["notes"] = ("CV-021 is headspace O2; the evidence concerns O2 available to the aqueous phase, and dissolved O2 has "
                      "no CV axis (gap G-8). " + d["notes"])

REWORD = [
    ("Real foods always carry trace Fe/Cu, so in practice this window is always satisfied:", "Trace Fe/Cu are normally present in foods and cooking water (general chemistry, not sourced here), so a metal-free condition is not expected in cooking:"),
    ("chlorophyll a was retained at pH >= 8.0", "chlorophyll a persisted when pH was 8.0 or above"),
    ("can occur at 55–60 °C in slow heating (slow roast, sous vide)", "may start as low as 55–60 °C when heating is slow (slow roasting, sous vide)"),
    ("Ca2+ did not inhibit acid hydrolysis of pectin", "Ca2+ had no inhibitory effect on acid hydrolysis of pectin"),
    ("near neutrality browning followed pseudo-zero-order kinetics after a lag", "around neutral pH, browning was pseudo-zero-order once a lag phase had passed"),
    ("storage at 45 °C for two months at aw 0.05–0.79", "two months of storage at 45 °C across aw 0.05–0.79"),
    ("rate constants at aw 0.52 were higher than at aw 0.33 (at 37 and 50 °C)", "at 37 and 50 °C the rate constants at aw 0.52 exceeded those at aw 0.33"),
    ("antiplatelet activity was lost after 30, 20 and 10 min of oven heating for whole, quartered and crushed onion", "oven heating abolished antiplatelet activity after 30 min (whole), 20 min (quartered) and 10 min (crushed onion)"),
    ("collagen solubility after 77 °C for 1 h was high (75.3 ± 8.1 %)", "1 h at 77 °C left collagen highly soluble (75.3 ± 8.1 %)"),
    ("higher cooking T increased collagen solubility (P < 0.001) in both muscles", "collagen solubility rose with cooking temperature in both muscles (P < 0.001)"),
    ("low-temperature long-time cooking up to 24 h at 60 °C", "low-temperature long-time cooking at 60 °C for as long as 24 h"),
    ("at 10 °C/min and pH 9, ovalbumin denatures at 84.5 °C and S-ovalbumin at 92.5 °C (intermediate 88.5 °C)", "DSC at pH 9 and 10 °C/min: ovalbumin 84.5 °C, S-ovalbumin 92.5 °C, an intermediate form 88.5 °C"),
    ("moved from 72.55 ± 0.07 °C to 70.43 ± 0.06 °C with oleuropein", "shifted with oleuropein between 72.55 (±0.07) and 70.43 (±0.06) °C"),
]
for d in W:
    for k in ("window_type_basis", "direction_of_effect", "time_qualifier", "notes"):
        v = d.get(k, "") or ""
        for a, b in REWORD:
            v = v.replace(a, b)
        if k == "time_qualifier" and v == "up to 24 h at 60 °C":
            v = "60 °C, holds to 24 h"
        d[k] = v

# order by mechanism priority
ORDER = ["ASCORBATE_TO_DHA_OXIDATION", "DHA_HYDROLYSIS_TO_DKG", "ASCORBATE_OXIDASE_AA_OXIDATION", "LEACHING",
         "CHLOROPHYLL_TO_PHEOPHYTIN", "CHLOROPHYLLASE_DEPHYTYLATION", "METALLO_CHLOROPHYLL_COMPLEX_FORMATION",
         "STARCH_GELATINISATION", "PROTEIN_DENATURATION_AGGREGATION", "COLLAGEN_SOLUBILISATION", "CELL_WALL_SOFTENING",
         "PPO_ENZYMATIC_BROWNING", "ALLIINASE_ALLIIN_CLEAVAGE", "MYROSINASE_GLUCOSINOLATE_HYDROLYSIS",
         "ENZYME_THERMAL_INACTIVATION", "MAILLARD_STRECKER_LUMPED", "STARCH_RETROGRADATION"]
W.sort(key=lambda d: ORDER.index(d["mechanism_key"]))
for i, d in enumerate(W, 1):
    d["window_id"] = f"MCW-{i:04d}"
SRC2W = {d.get("_src"): d["window_id"] for d in W if d.get("_src")}
for d in W:
    for k in ("window_type_basis", "notes", "direction_of_effect"):
        d[k] = re.sub(r"\bS[45]-[A-Z]*-?[0-9]+\b", lambda m: SRC2W.get(m.group(0), "another row"), d.get(k, "") or "")

H2 = ["window_id", "mechanism_key", "condition_axis", "axis_detail", "cv_id_proposed", "location", "window_type",
      "window_type_basis", "direction_of_effect", "matrix_scope", "min_value", "min_status", "max_value", "max_status",
      "unit", "canonical_unit", "min_canonical", "max_canonical", "time_qualifier", "source_citation", "doi_or_url",
      "source_type", "evidence_locator", "verification", "usable_for", "status", "notes"]
out2 = REPO / "registry/mechanism_condition_windows_draft_v1.csv"
with open(out2, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=H2, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    w.writeheader()
    for d in W:
        w.writerow({k: d.get(k, "") for k in H2})

for p in (out1, out2):
    print(p, hashlib.sha256(p.read_bytes()).hexdigest())
print("review rows", len(R), "window rows", len(W))
