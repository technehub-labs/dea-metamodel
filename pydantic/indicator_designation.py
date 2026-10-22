"""IndicatorDesignation  :  generated from schemas/entities/indicator-designation.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class IndicatorDesignation(Entity):
    """A governed management designation applied to a PerformanceMetric (CR-MET-008 binding). The Metric identity is preserved across designations (EGV-004); one Metric may carry multiple designations (KPI Lagging, KRI Leading, etc.) for different management purposes."""

    type: Literal['IndicatorDesignation']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired', 'under_review', 'approved', 'published', 'under_revision', 'suspended']
    """CR-MET-010 Q15a-prime: the five governance refinement states are declared for this entity by the metric-governance lifecycle specialization."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    designation_type: Literal['KPI', 'KRI', 'KCI', 'SLI', 'Operational']
    """CR-MET-008 binding (IndicatorDesignation.designation_type controlled vocabulary; 5 values)."""
    associated_metric_ref: str
    """The PerformanceMetric id being designated (relationship dea:has-designation, inverse dea:designates)."""
    management_purpose: str
    """Why the designation exists. For KPI: 'evaluating performance against objective X'. For KRI: 'monitoring risk exposure of risk Y'. For KCI: 'evaluating control effectiveness of control Z'."""
    associated_objective_ref: Optional[str] = None
    """The StrategicObjective, Outcome, Risk, or Control this designation supports. KPI points to business objective; KRI points to risk-objective; KCI points to control objective. The user-supplied sections 6-8 requirement."""
    organizational_scope: Any
    """Scope of application (enterprise, business_domain, business_unit, capability, process, product_or_service, system). Aligns with Metric.scope_classification (CR-MET-002). String or array of strings."""
    accountable_owner_ref: str
    """Responsible management authority (Actor ref)."""
    reporting_frequency: Literal['real_time', 'hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'semi_annual', 'annual']
    """CR-MET-008 binding (IndicatorDesignation.reporting_frequency controlled vocabulary; 8 values)."""
    target_reference: Optional[str] = None
    """Reference to a PerformanceTarget (CR-MET-006) applicable to this designation."""
    threshold_reference: Optional[str] = None
    """Reference to a Threshold (CR-MET-006) applicable to this designation."""
    escalation_rules: Optional[Any] = None
    """Required management response (e.g., notification policy, runbook, escalation chain). String or array of strings/references."""
    measurement_orientation: Literal['leading', 'lagging', 'neutral']
    """CR-MET-008 binding (IndicatorDesignation.measurement_orientation controlled vocabulary; 3 values). Cross-cutting attribute: the same Metric may be designated as KPI Leading for one purpose and KPI Lagging for another."""
    effective_period: str
    """Reference to a TemporalInterval; CR-MET-006 binding (also applies to designation)."""
    approval_status: Literal['draft', 'proposed', 'approved', 'retired']
    """CR-MET-008 binding (IndicatorDesignation.approval_status controlled vocabulary; 4 values)."""
