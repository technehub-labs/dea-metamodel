"""Baseline  :  generated from schemas/entities/baseline.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Baseline(Entity):
    """A reference measurement or established starting condition against which change, improvement, or deterioration can be evaluated (CR-MET-006)."""

    type: Literal['Baseline']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    kind: Literal['historical', 'initial', 'strategic', 'operational', 'regulatory', 'scenario_derived']
    """CR-MET-006 binding (Baseline.kind controlled vocabulary; 6 values)."""
    approval_status: Literal['draft', 'proposed', 'approved', 'retired']
    """CR-MET-006 binding (Baseline.approval_status controlled vocabulary; 4 values)."""
    reference_metric_ref: str
    """The PerformanceMetric id this Baseline is a reference for (relationship dea:references)."""
    subject_ref: str
    """The subject the Baseline concerns (relationship dea:applies-to; target is Entity or AssessmentSubject)."""
    reference_value: Any
    """The reference value or observation summary. Numeric for ratio/interval Metrics; ordinal for ordinal Metrics; categorical for categorical Metrics."""
    establishment_date: str
    applicable_period: str
    """Reference to a TemporalInterval; CR-MET-006 binding."""
    organizational_scope: Any
    """The organizational scope (enterprise, business_domain, business_unit, capability, process, product_or_service, system). String or array of strings."""
    measurement_methodology: Optional[str] = None
    source_evidence: Optional[Any] = None
    """Source and evidence supporting the Baseline. String or array of strings/references."""
    supersedes_baselines: Optional[list[str]] = None
    """Previous Baseline ids this Baseline supersedes (relationship dea:supersedes, extended in CR-MET-004)."""
