"""S159 alignment between the 26a kinetics library and the 24a FORM / PARAM schemas (DRAFT_PENDING_H4).

Synthetic only: the fitted value below comes from data generated inside the test from a SYNTHETIC truth.
The PARAM row built here is a schema exercise, never a ledger row.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from culinarystate.mechanism import form_param_val as FPV
from culinarystate.simulation.kinetics import fitting as FT
from culinarystate.simulation.kinetics import identifiability as ID
from culinarystate.simulation.kinetics import models as M
from culinarystate.simulation.kinetics import units as U
from tests.fixtures import form_param_val_v1_fixtures as F

SCHEMAS = Path(__file__).resolve().parents[2] / "registry" / "schemas"


def schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def slots_for(form: M.KineticForm) -> list[dict[str, Any]]:
    out = []
    for p in form.parameters:
        order = None
        if p.role == "RATE_CONSTANT":
            order = float(1 - U.dimension(p.dimension).as_dict().get("CONCENTRATION", Fraction(0)))
        out.append(F.slot(p.symbol, role=p.role, dimension=p.dimension, order=order, positive=p.transform == "LOG",
                          needs_t_ref=p.symbol == "k_ref"))
    return out


def test_library_vocabularies_are_inside_the_schema_vocabularies() -> None:
    form = schema("FORM.draft_v1.schema.json")
    kin_fit = schema("KIN.draft_v1_1.schema.json")["properties"]["fit"]["items"]["properties"]
    roles = set(form["$defs"]["parameter_slot"]["properties"]["role"]["enum"])
    for f in M.FORMS.values():
        assert f.kin_family in form["properties"]["model_family"]["enum"]
        assert f.kin_model_level in kin_fit["model_level"]["enum"]
        assert {p.role for p in f.parameters} <= roles
    assert set(ID.CLASSES) <= set(form["properties"]["identifiability_status"]["enum"])


@pytest.mark.parametrize("prefix", FPV.FORM_ID_PREFIX_OPTIONS)
@pytest.mark.parametrize("name", sorted(M.FORMS))
def test_a_form_record_built_from_each_library_form_validates(name: str, prefix: str) -> None:
    rec = F.form(7, prefix=prefix, family=M.FORMS[name].kin_family, slots=slots_for(M.FORMS[name]))
    issues = FPV.validate_form(rec, form_id_prefix=prefix)
    assert [i for i in issues if i.severity == "ERROR"] == []


def _obs(origin: str) -> FT.Observations:
    tau = np.array([0.0, 300.0, 900.0, 1800.0])
    y = -1.5e-3 * tau + np.random.default_rng(1).normal(0, 0.01, tau.shape)    # SYNTHETIC truth k = 1.5e-3 s^-1
    return FT.Observations(response=y, covariates={"tau_s": tau}, sigma=np.full(tau.shape, 0.01),
                           response_kind="LN_RETENTION", origin=origin,
                           kin_ids=("KIN-000001",) if origin == "KIN_SERIES" else ())


def test_project_refit_provenance_from_a_fit_validates_as_param() -> None:
    fit = FT.fit_least_squares(M.FORMS["FIRST_ORDER"], _obs("KIN_SERIES"), starts=[{"k": 1e-3}], backend="numpy")
    p = F.param(source_class="PROJECT_REFIT", unit="1/s", value=fit.estimates["k"])
    p["value_provenance"] = fit.as_param_provenance()
    form = F.form()
    issues = FPV.validate_param(p, form_id_prefix="FORM", forms_by_id={form["id"]: form})
    assert [i for i in issues if i.severity == "ERROR"] == []


def test_synthetic_fits_never_become_param_provenance() -> None:
    fit = FT.fit_least_squares(M.FORMS["FIRST_ORDER"], _obs("SYNTHETIC"), starts=[{"k": 1e-3}], backend="numpy")
    with pytest.raises(FT.FitError):
        fit.as_param_provenance()
