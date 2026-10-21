"""Threshold  :  generated from schemas/entities/threshold.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Threshold(Entity):
    """A directional boundary used to classify or trigger an evaluation (CR-MET-006). 4 directional models (higher_is_better, lower_is_better, bounded_optimum, exact_match) and 4 levels (critical, warning, acceptable, optimal) per user-supplied section 6."""

    type: Literal['Threshold']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    threshold_metric_ref: str
    """The PerformanceMetric id being constrained (relationship dea:constrains, extended in CR-MET-006)."""
    threshold_value: Any
    """The boundary value(s). A number for single-direction thresholds (higher_is_better, lower_is_better, exact_match); an object {min, max} for bounded_optimum."""
    threshold_level: Literal['critical', 'warning', 'acceptable', 'optimal']
    """CR-MET-006 binding (Threshold.level controlled vocabulary; 4 values). A Metric MAY have multiple Thresholds (one per level)."""
    direction: Literal['higher_is_better', 'lower_is_better', 'bounded_optimum', 'exact_match']
    """CR-MET-006 binding (Threshold.direction controlled vocabulary; 4 values)."""
    effective_period: str
    """Reference to a TemporalInterval."""
    owner_ref: Optional[str] = None
    """Responsible owner (Actor ref)."""
    escalation_rule_ref: Optional[str] = None
    """Reference to an escalation rule (e.g. notification policy, runbook)."""
