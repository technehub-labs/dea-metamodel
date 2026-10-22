"""PerformanceTarget  :  generated from schemas/entities/performance-target.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class PerformanceTarget(Entity):
    """A value-level desired measurement result (CR-MET-006). Sibling of AssessmentTarget (maturity-level, CR-5 section 21); the two target types coexist."""

    type: Literal['PerformanceTarget']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    target_metric_ref: str
    """The PerformanceMetric id being targeted (relationship dea:specifies-target)."""
    target_subject_ref: str
    """The subject being targeted (relationship dea:applies-to)."""
    target_scope: Any
    """The scope (enterprise, business_domain, business_unit, capability, process, product_or_service, system). Aligns with Metric.scope_classification (CR-MET-002). String or array of strings."""
    target_value: Optional[float] = None
    """The desired value (numeric). Mutually exclusive with target_range."""
    target_range: Optional[dict[str, Any]] = None
    """The desired range {min, max}. Mutually exclusive with target_value."""
    target_direction: Literal['increase', 'decrease', 'maintain', 'bounded', 'exact_match']
    """CR-MET-006 binding (PerformanceTarget.direction controlled vocabulary; 5 values)."""
    effective_period: str
    """Reference to a TemporalInterval."""
    owner_ref: str
    """Responsible owner (Actor ref)."""
    associated_objective_ref: Optional[str] = None
    """The StrategicObjective or Outcome this Target supports. Relationship dea:has-target (StrategicObjective -> PerformanceTarget)."""
    approval_status: Literal['draft', 'proposed', 'approved', 'retired']
    """CR-MET-006 binding (PerformanceTarget.approval_status controlled vocabulary; 4 values)."""
    supporting_rationale: Optional[str] = None
