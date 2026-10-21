"""Metric  :  generated from schemas/entities/metric.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Metric(Entity):
    """A formally defined, reusable semantic specification that describes a measurable property, characteristic, condition, quantity, rate, ratio, index, or other observable aspect of a subject, including the semantic rules necessary to determine and interpret its value. A Metric is foundational: reified across the measurement-dimension orthogonal allocator (ADR-0002 D1) and referenceable from any OpenDEAM profile. (CR-MET-001 binding CR-MET-000 reconciliation and ADR-MET-001.)"""

    type: Literal['Metric']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired', 'under_review', 'approved', 'published', 'under_revision', 'suspended']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml. The five CR-MET-010 refinement states (under_review, approved, published, under_revision, suspended) are declared for Metric governance per Q15a."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    subject_concept: str
    """The type of phenomenon or property measured (CR-MET-001 binding). Normative: required, distinguishes a Metric by what it measures rather than by its MECE label."""
    measurement_nature: Literal['numeric', 'ordinal', 'nominal', 'boolean', 'composite']
    """The data nature of the value produced by applying this Metric. Normative: required. CR-MET-001 binding."""
    subject_classification: Optional[list[str]] = None
    """Measurement subject axis (CR-MET-002 binding ADR-MET-003). A Metric MAY have multiple subject classifications; a non-empty value is recommended for catalog discoverability."""
    purpose_classification: Optional[list[str]] = None
    """Measurement purpose axis (CR-MET-002 binding ADR-MET-003). A Metric MAY have multiple purpose classifications."""
    orientation_classification: Optional[list[str]] = None
    """Measurement orientation axis (CR-MET-002 binding ADR-MET-003). Mirrors Indicator.kind. A Metric MAY have multiple orientation classifications only where the definitions genuinely support them."""
    scope_classification: Optional[list[str]] = None
    """Measurement scope axis (CR-MET-002 binding ADR-MET-003). A Metric MAY have multiple scope classifications. process refers to dea:BusinessProcess (line 592; L3); there is no dea:Activity (per user reminder 2026-10-18)."""
    formula_definition: Optional[dict[str, Any]] = None
    """The structured calculation definition (CR-MET-005 binding). 8-field object per user-supplied section 5."""
    composite_definition: Optional[dict[str, Any]] = None
    """The structured Composite Metric definition (CR-MET-005 binding). 6-field object per user-supplied section 7. Required iff measurement_nature: composite."""
    precision: Optional[int] = None
    """Significant figures for the result (CR-MET-005 binding)."""
    decimal_scale: Optional[int] = None
    """Decimal places for the result (CR-MET-005 binding)."""
    rounding_rule: Optional[Literal['half_up', 'half_even', 'half_down', 'truncate']] = None
    """Rounding rule for the result (CR-MET-005 binding). 4-value enum."""
    null_value_semantics: Optional[str] = None
    """How null/missing values are interpreted (CR-MET-005 binding). Examples: 'excluded_from_aggregation', 'treated_as_zero', 'propagates_null'."""
    management_significance: Optional[list[str]] = None
    """Management significance axis (CR-MET-002 binding ADR-MET-003). Designations, not specializations. Full IndicatorDesignation entity in CR-MET-008."""
    directionality: Optional[Literal['higher_is_better', 'lower_is_better', 'target_is_better', 'nominal']] = None
    """Desired interpretation of increasing or decreasing values. CR-MET-001 binding."""
    calculation_definition: Optional[str] = None
    """Formula or computational definition. Required when measurement_nature is numeric and the value is computed; for ordinal/nominal/boolean values a textual rule suffices."""
    unit: Optional[str] = None
    """Measurement unit (cross-reference to the unit registry per CR-MET-005). Optional: required only when measurement_nature is numeric. Examples: %, count, days, USD, ms."""
    measurement_method: Optional[str] = None
    """How this metric is collected or calculated."""
    baseline_value: Optional[Any] = None
    target_value: Optional[Any] = None
    thresholds: Optional[dict[str, Any]] = None
    frequency: Optional[Literal['realtime', 'hourly', 'daily', 'weekly', 'monthly', 'quarterly']] = None
    scope_layers: Optional[list[str]] = None
    """Architecture layers this metric may evaluate (OpenDEAM v0.2.0 measurement-dimension scope)."""
    legacy_metric_type: Optional[Literal['kpi', 'health', 'maturity', 'performance', 'adoption', 'compliance', 'risk']] = None
    """DEPRECATED. The pre-CR-MET-001 MECE taxonomy value. Preserved for one release cycle to allow migration of existing catalog records. New records MUST use the binding six-axis classification per CR-MET-002 / ADR-MET-003."""
    governance: Optional[dict[str, Any]] = None
    """CR-MET-010 section 4 governance role accountability. One individual may fulfil multiple roles, but accountability MUST remain explicit."""
    quality_dimensions: Optional[list[str]] = None
    """CR-MET-010 section 6: the ten reusable quality dimensions evaluated for this Metric definition. Definition quality MUST be distinguished from individual Observation quality."""
    conformance: Optional[dict[str, Any]] = None
    """CR-MET-010 section 7: three conformance levels. Level 1 structural (schema, required attributes, identity, references, data types). Level 2 semantic (unambiguous definition, valid classification, appropriate unit or scale, valid formula semantics, subject concept, relationships). Level 3 governance (owner, steward, approval status, lifecycle compliance, source documentation, evidence, versioning, change traceability)."""
