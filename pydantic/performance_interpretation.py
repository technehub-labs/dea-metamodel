"""PerformanceInterpretation  :  generated from schemas/entities/performance-interpretation.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class PerformanceInterpretation(Entity):
    """The meaning assigned to a result under defined criteria (CR-MET-006). Carries interpretation_kind, interpretation_state, reference_used, computed variance, narrative. Sibling of AssessmentResult (which carries score); PerformanceInterpretation carries judgment. Variance itself is a derived view (no entity); PerformanceInterpretation is the auditable record of how the variance/threshold/benchmark was interpreted."""

    type: Literal['PerformanceInterpretation']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    interprets_metric_ref: str
    """The PerformanceMetric id being interpreted."""
    interprets_observation_ref: str
    """The MeasurementObservation id being interpreted (relationship dea:interprets)."""
    interpretation_kind: Literal['variance_evaluation', 'threshold_evaluation', 'benchmark_evaluation', 'composite_judgment']
    """CR-MET-006 binding (PerformanceInterpretation.kind controlled vocabulary; 4 values)."""
    interpretation_state: Literal['exceeds_target', 'meets_target', 'within_tolerance', 'warning', 'critical', 'unknown']
    """CR-MET-006 binding (PerformanceInterpretation.state controlled vocabulary; 6 values)."""
    reference_used: str
    """Which reference was used (Baseline ref, PerformanceTarget ref, Threshold ref, BenchmarkReference ref)."""
    absolute_variance: Optional[float] = None
    """Computed absolute variance (ObservedValue - ReferenceValue). Optional; populated when interpretation_kind is variance_evaluation."""
    relative_variance: Optional[float] = None
    """Computed relative variance percentage ((ObservedValue - ReferenceValue) / ReferenceValue * 100). Optional; populated when interpretation_kind is variance_evaluation."""
    narrative: Optional[str] = None
    evaluator_ref: Optional[str] = None
    """Who/what performed the interpretation (Actor or system ref)."""
    evaluated_at: str
