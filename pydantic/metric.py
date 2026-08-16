"""Metric — generated from schemas/entities/metric.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Metric(Entity):
    """A measured quantity used to evaluate outcomes against targets. OpenDEAM v0.2.0 (ADR-0002 D1): Metrics belong to the cross-cutting Measurement Dimension, not an architecture layer. scope_layers declares which layers the metric is permitted to evaluate; measurable entities reference metrics via measured_by."""

    type: Literal['Metric']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    metric_type: Literal['kpi', 'health', 'maturity', 'performance', 'adoption', 'compliance', 'risk']
    """Category of metric."""
    unit: str
    """Measurement unit."""
    measurement_method: Optional[str] = None
    """How this metric is collected or calculated."""
    baseline_value: Optional[Any] = None
    target_value: Optional[Any] = None
    thresholds: Optional[dict[str, Any]] = None
    frequency: Optional[Literal['realtime', 'hourly', 'daily', 'weekly', 'monthly', 'quarterly']] = None
    scope_layers: Optional[list[str]] = None
    """Architecture layers this metric may evaluate (OpenDEAM v0.2.0 measurement-dimension scope)."""
