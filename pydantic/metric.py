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
    entities_measured: Optional[list[str]] = None
    """Entity IDs this metric tracks."""
    owner: Optional[str] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    scope_layers: Optional[list[str]] = None
    """Architecture layers this metric may evaluate (OpenDEAM v0.2.0 measurement-dimension scope)."""
