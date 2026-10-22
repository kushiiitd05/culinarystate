#!/usr/bin/env python3
"""Step 07: controlled vocabularies (stable internal ids are authoritative; raw source strings are always kept alongside).
  python tools/build_step07_registries.py"""
import csv
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "registry"


def w(name, hdr, rows):
    with open(R / name, "w", newline="", encoding="utf-8") as f:
        c = csv.writer(f)
        c.writerow(hdr)
        c.writerows(rows)
    print(name, len(rows))


# ---- condition variables: id, name, group, dimension, canonical_unit, allowed_units, valid_min, valid_max, absolute_or_difference, notes
INF = ""
CV = [
    ("time_duration", "TIME", "time", "s", "s;min;h;d;week;month;year", 0, INF, "n/a", "month/year use the repo convention (mean Gregorian); raw text kept"),
    ("time_start_end", "TIME", "time", "s", "s;min;h;d", 0, INF, "n/a", "start/end offsets within a process"),
    ("time_hold_rest", "TIME", "time", "s", "s;min;h;d", 0, INF, "n/a", "hold/rest periods between steps"),
    ("time_trajectory", "TIME", "time", "s", "s;min;h", 0, INF, "n/a", "time axis of a trajectory"),
    ("temp_equipment_setpoint", "TEMPERATURE", "temperature", "K", "degC;degF;K", 0, INF, "absolute", "oven/hob/fryer setpoint; never food temperature"),
    ("temp_medium", "TEMPERATURE", "temperature", "K", "degC;degF;K", 0, INF, "absolute", "water/oil/steam/air temperature"),
    ("temp_surface", "TEMPERATURE", "temperature", "K", "degC;degF;K", 0, INF, "absolute", "food surface"),
    ("temp_core", "TEMPERATURE", "temperature", "K", "degC;degF;K", 0, INF, "absolute", "food core / internal"),
    ("temp_unspecified", "TEMPERATURE", "temperature", "K", "degC;degF;K", 0, INF, "absolute", "location not stated in source (never promoted to core/surface)"),
    ("temp_trajectory", "TEMPERATURE", "temperature", "K", "degC;degF;K", 0, INF, "absolute", "T(t) series; location must be stated"),
    ("temp_rate", "TEMPERATURE", "temperature_rate", "K/s", "K/s;K/min;degC/min;degF/min", INF, INF, "difference", "heating/cooling rate (a temperature DIFFERENCE per time)"),
    ("preheat_status", "TEMPERATURE", "categorical", "category", "category", INF, INF, "n/a", "preheated / not / unknown"),
    ("ph", "CHEMICAL", "dimensionless", "pH", "pH", 0, 14, "n/a", "0-14 bounds; never defaulted to 7; mixture pH never averaged"),
    ("titratable_acidity", "CHEMICAL", "mass_fraction_or_conc", "as stated", "g/100g;g/L;percent;mmol/L", 0, INF, "n/a", "expressed as an acid equivalent; acid must be named"),
    ("water_activity", "CHEMICAL", "dimensionless", "aw", "aw", 0, 1, "n/a", "0-1; absent is UNKNOWN not 0"),
    ("moisture_content", "CHEMICAL", "mass_fraction", "fraction", "percent;fraction;g/100g", 0, INF, "n/a", "basis (wet/dry) mandatory; wet-basis <=1, dry-basis may exceed 1"),
    ("dry_matter", "CHEMICAL", "mass_fraction", "fraction", "percent;fraction;g/100g", 0, 1, "n/a", "wet-basis fraction"),
    ("salt_content", "CHEMICAL", "mass_fraction", "fraction", "percent;fraction;g/100g;g/L", 0, INF, "n/a", ""),
    ("sugar_content", "CHEMICAL", "mass_fraction", "fraction", "percent;fraction;g/100g;g/L;Brix", 0, INF, "n/a", ""),
    ("fat_oil_content", "CHEMICAL", "mass_fraction", "fraction", "percent;fraction;g/100g", 0, INF, "n/a", ""),
    ("oxygen_headspace", "CHEMICAL", "volume_fraction", "fraction", "percent;fraction;kPa", 0, INF, "n/a", "absent is UNKNOWN not 0; atmosphere composition may be qualitative"),
    ("solvent_medium", "CHEMICAL", "categorical", "category", "category", INF, INF, "n/a", "water / oil / steam / air / brine ..."),
    ("additive_catalyst_enzyme", "CHEMICAL", "categorical", "category", "category", INF, INF, "n/a", "name + amount held separately"),
    ("pressure", "PHYSICAL", "pressure", "Pa", "Pa;kPa;MPa;bar;atm;psi;mmHg;torr", 0, INF, "absolute", "gauge vs absolute must be stated; bare psi/bar is AMBIGUOUS"),
    ("relative_humidity", "PHYSICAL", "ratio", "fraction", "percent;fraction", 0, 1, "n/a", ""),
    ("heat_transfer_mode", "PHYSICAL", "categorical", "category", "category", INF, INF, "n/a", "see heat_transfer_mode_registry_v1.csv"),
    ("agitation_mixing", "PHYSICAL", "categorical_or_rate", "as stated", "rpm;category", 0, INF, "n/a", ""),
    ("flow_rate", "PHYSICAL", "flow", "as stated", "as stated", 0, INF, "n/a", ""),
    ("microwave_power", "PHYSICAL", "power", "W", "W;kW", 0, INF, "n/a", "nominal oven power, not absorbed power"),
    ("microwave_frequency", "PHYSICAL", "frequency", "Hz", "Hz;MHz;GHz", 0, INF, "n/a", ""),
    ("geometry_shape", "PHYSICAL", "categorical", "category", "category", INF, INF, "n/a", "slab / cylinder / sphere / irregular"),
    ("thickness", "PHYSICAL", "length", "m", "mm;cm;m", 0, INF, "n/a", ""),
    ("particle_size", "PHYSICAL", "length", "m", "um;mm;cm", 0, INF, "n/a", ""),
    ("surface_area_volume_proxy", "PHYSICAL", "ratio", "1/m", "1/m;1/cm;1/mm", 0, INF, "n/a", "only if stated or computable from stated geometry"),
    ("batch_size", "PHYSICAL", "mass_or_volume", "g", "g;kg;mL;L;count", 0, INF, "n/a", ""),
    ("container_tool_material", "PHYSICAL", "categorical", "category", "category", INF, INF, "n/a", "TOOL ledger ids when available"),
    ("organism_strain", "BIOLOGICAL", "categorical", "category", "category", INF, INF, "n/a", ""),
    ("starter_inoculum", "BIOLOGICAL", "categorical_or_conc", "as stated", "CFU/g;CFU/mL;percent;category", 0, INF, "n/a", ""),
    ("maturity_ripeness", "BIOLOGICAL", "categorical", "category", "category", INF, INF, "n/a", ""),
    ("storage_age", "BIOLOGICAL", "time", "s", "h;d;week;month", 0, INF, "n/a", "storage time before processing"),
]
w("condition_variable_registry_v1.csv", ["condition_variable_id", "name", "group", "dimension", "canonical_unit", "allowed_units", "valid_min", "valid_max", "absolute_or_difference", "notes"],
  [[f"CV-{i:03d}", n, g, d, cu, au, lo, hi, ad, nt] for i, (n, g, d, cu, au, lo, hi, ad, nt) in enumerate(CV, 1)])
w("value_type_registry_v1.csv", ["value_type_id", "name", "definition", "rule"],
  [["VT-001", "POINT", "single stated value", "e.g. 180 C"], ["VT-002", "INTERVAL", "stated lower/upper bounds (either may be open)", "e.g. 170-190 C; '>100 C' is an interval with an open upper bound"],
   ["VT-003", "TRAJECTORY", "ordered (time, value) pairs", "time strictly increasing; location stated"], ["VT-004", "QUALITATIVE", "descriptive term", "never converted to a number without an explicit sourced mapping"],
   ["VT-005", "UNKNOWN", "not stated", "never defaulted"]])
w("measurement_basis_registry_v1.csv", ["measurement_basis_id", "name", "definition", "ledger_target_basis_aliases", "combinable_with"],
  [["MB-001", "WET_FRESH_WEIGHT", "per mass of fresh/as-sampled (wet) material", "FRESH_WEIGHT", "MB-001 only"], ["MB-002", "DRY_WEIGHT", "per mass of dry matter", "DRY", "MB-002 only"],
   ["MB-003", "AS_FED_AS_PREPARED", "per mass of food as eaten/prepared", "", "MB-003 only"], ["MB-004", "PER_MASS_UNSPECIFIED", "per mass, wet/dry not stated", "", "none (ambiguous; cannot be combined with MB-001/002)"],
   ["MB-005", "PER_VOLUME", "per volume of liquid/sample", "PER_VOLUME", "MB-005 only"], ["MB-006", "PER_SERVING", "per defined serving", "", "MB-006 only"],
   ["MB-007", "RATIO_NO_BASIS", "dimensionless ratio (e.g. retention fraction); basis is carried by the retention type", "RETENTION_TR_OR_AR; TRUE_RETENTION", "see retention type"], ["MB-008", "UNKNOWN", "basis not stated", "", "none"]])
w("quantity_form_registry_v1.csv", ["quantity_form_id", "name", "definition"],
  [["QF-001", "CONCENTRATION", "amount per mass/volume of matrix"], ["QF-002", "ABSOLUTE_AMOUNT", "total amount in a sample/portion"], ["QF-003", "RELATIVE_ABUNDANCE", "fraction of a reference/total"], ["QF-004", "PEAK_AREA_INTENSITY", "instrument response, not a concentration"], ["QF-005", "RATIO", "dimensionless ratio of two amounts"], ["QF-006", "UNKNOWN", ""]])
w("retention_type_registry_v1.csv", ["retention_type_id", "name", "definition", "assigned_when"],
  [["RT-001", "TRUE_RETENTION", "fraction of the nutrient/compound in the whole food retained after processing, accounting for weight change", "source names it true retention (Bognar TRUE_RETENTION)"],
   ["RT-002", "APPARENT_RETENTION", "ratio of concentrations (per unit weight) after/before, no yield correction", "source states apparent / concentration ratio"],
   ["RT-003", "YIELD_ADJUSTED_RETENTION", "retention including a yield/water-change correction as stated by the source", "source description says so (Phenol-Explorer: description reported by a secondary snippet, UNVERIFIED against the primary page)"],
   ["RT-004", "TR_OR_AR_UNDISCLOSED", "source mixes true and apparent retention and does not mark which per row", "USDA R6"], ["RT-005", "UNKNOWN_RETENTION_BASIS", "no information", "default"], ["RT-006", "NOT_APPLICABLE", "row carries no retention value", ""]])
w("censoring_registry_v1.csv", ["censoring_id", "name", "definition", "numeric_use"],
  [["CS-001", "DETECTED", "a quantified value is reported", "value usable"], ["CS-002", "NON_DETECT", "analyte reported as not detected (limit may be unknown)", "NOT zero; left-censored"],
   ["CS-003", "BELOW_LOD", "below the stated limit of detection", "left-censored at LOD (LOD must be stated)"], ["CS-004", "BELOW_LOQ", "below the stated limit of quantification", "left-censored at LOQ (LOQ must be stated)"],
   ["CS-005", "ABOVE_CAP", "reported value is a cap/upper bound (e.g. >100% retention capped)", "right-censored at the cap"], ["CS-006", "CENSORED_UNKNOWN", "censored but type/limit unknown", "no numeric use"], ["CS-007", "NOT_REPORTED", "no value or censoring information (UNKNOWN is not NON_DETECT)", "none"]])
w("value_origin_registry_v1.csv", ["value_origin_id", "name", "definition"],
  [["VO-001", "MEASURED", "measured by the source authors (primary study)"], ["VO-002", "REPORTED", "reported by a database/compilation without per-row measurement detail"], ["VO-003", "DERIVED_DETERMINISTIC", "computed by a documented deterministic rule from stated values"],
   ["VO-004", "SOURCE_IMPUTED", "imputed by the source (stated)"], ["VO-005", "SOURCE_IMPUTATION_POSSIBLE", "source says imputation occurs but does not mark rows (USDA R6)"], ["VO-006", "UNKNOWN", ""]])
w("measurement_location_registry_v1.csv", ["measurement_location_id", "name", "definition", "maps_to_temperature_variable"],
  [["ML-001", "EQUIPMENT_SETPOINT", "oven/hob/fryer dial or controller setpoint", "temp_equipment_setpoint"], ["ML-002", "MEDIUM", "cooking medium (water, oil, steam, air)", "temp_medium"], ["ML-003", "SURFACE", "food surface", "temp_surface"],
   ["ML-004", "CORE", "food core / internal", "temp_core"], ["ML-005", "UNSPECIFIED", "source does not say", "temp_unspecified"], ["ML-006", "AMBIENT", "environment/room", "temp_unspecified"]])
w("measurement_method_registry_v1.csv", ["measurement_method_id", "name", "keywords_for_raw_text_matching", "class", "note"],
  [["AM-001", "HPLC", "hplc;high performance liquid chromatography;uplc", "chromatography", ""], ["AM-002", "GC-MS", "gc-ms;gc/ms;gas chromatography", "chromatography", ""], ["AM-003", "LC-MS", "lc-ms;lc/ms;uhplc-ms;ms/ms", "chromatography", ""],
   ["AM-004", "SPECTROPHOTOMETRY", "spectrophotom;uv-vis;absorbance", "spectroscopy", ""], ["AM-005", "GRAVIMETRIC", "gravimetric;weighed;weight loss;drying oven", "mass", ""], ["AM-006", "TEXTURE_ANALYSIS", "texture analy;instron;warner-bratzler;shear force", "mechanical", ""],
   ["AM-007", "COLORIMETRY", "colorimet;l*a*b*;hunter", "optical", ""], ["AM-008", "SENSOR_PROBE", "thermocouple;probe;sensor;data logger", "sensor", ""], ["AM-009", "CALCULATION", "calculated;calculation;derived", "computed", "e.g. USDA R6 retention (MEAS-000001)"],
   ["AM-010", "OTHER", "", "other", "raw text kept"], ["AM-011", "UNKNOWN", "", "unknown", "default"]])
w("heat_transfer_mode_registry_v1.csv", ["heat_transfer_mode_id", "name", "definition"],
  [["HT-001", "CONDUCTION", "contact with a hot surface or within the food"], ["HT-002", "CONVECTION_NATURAL", "natural convection in air/liquid"], ["HT-003", "CONVECTION_FORCED", "fan/stirring/agitation-driven"], ["HT-004", "RADIATION", "infrared/grill/oven wall radiation"],
   ["HT-005", "CONDENSATION_STEAM", "latent heat from condensing steam"], ["HT-006", "DIELECTRIC_MICROWAVE", "microwave volumetric heating"], ["HT-007", "MIXED", "several modes stated"], ["HT-008", "UNKNOWN", "not stated"]])
