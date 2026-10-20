"""Simulator data-fidelity contract (S116). Every state-transition input must declare WHAT KIND of source supports it.

Permanent rule: a STRUCTURAL_RECIPE source may say that a process occurred; it may NOT by itself define the measured
physical/chemical magnitude of the transition. Magnitudes need MEASURED_TRANSITION, COMPILED_RETENTION or KINETIC support
(or are explicitly MODEL_GENERATED / SYNTHETIC and labelled so).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SourceClass(str, Enum):
    STRUCTURAL_RECIPE = "STRUCTURAL_RECIPE"
    COMPOSITION = "COMPOSITION"
    MEASURED_TRANSITION = "MEASURED_TRANSITION"
    COMPILED_RETENTION = "COMPILED_RETENTION"
    KINETIC = "KINETIC"
    MOLECULAR_PRIOR = "MOLECULAR_PRIOR"
    SENSORY_PRIOR = "SENSORY_PRIOR"
    MODEL_GENERATED = "MODEL_GENERATED"
    SYNTHETIC = "SYNTHETIC"


MAGNITUDE_CLASSES = {SourceClass.MEASURED_TRANSITION, SourceClass.COMPILED_RETENTION, SourceClass.KINETIC,
                     SourceClass.MODEL_GENERATED, SourceClass.SYNTHETIC}


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class TransitionInput:
    source_class: SourceClass
    source_id: str
    source_record_id: str
    evidence_tier: str
    process: str
    conditions: dict = field(default_factory=dict)
    initial_state_support: str = "UNKNOWN"
    final_state_support: str = "UNKNOWN"
    uncertainty: str | None = None
    licence: str = "UNVERIFIED"
    provenance: str = ""
    magnitude: float | None = None            # measured/predicted size of the change (e.g. retention fraction), if any

    def __post_init__(self):
        if not isinstance(self.source_class, SourceClass):
            raise ContractError(f"source_class must be a SourceClass, got {self.source_class!r}")
        for name in ("source_id", "source_record_id", "process", "provenance"):
            if not getattr(self, name):
                raise ContractError(f"{name} is required")
        if self.magnitude is not None and self.source_class not in MAGNITUDE_CLASSES:
            raise ContractError(f"{self.source_class.value} cannot define a transition magnitude")
        if self.source_class in (SourceClass.MODEL_GENERATED, SourceClass.SYNTHETIC) and self.uncertainty is None:
            raise ContractError("MODEL_GENERATED/SYNTHETIC inputs must state their uncertainty")
