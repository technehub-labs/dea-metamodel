"""Measurement  :  generated from schemas/entities/measurement.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Measurement(Entity):
    """The execution or application of a Metric to a particular subject, within a defined context, using an identified measurement method and applicable configuration. A Measurement is distinct from the Metric it applies and from the MeasurementObservation it produces. (CR-MET-001 binding ADR-MET-002; full attribute set in CR-MET-003.)"""

    type: Literal['Measurement']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired', 'under_review', 'approved', 'published', 'under_revision', 'suspended']] = None
    applies_metric: str
    """Reference to the dea:PerformanceMetric definition version applied. Cardinality 1:1 (every Measurement applies exactly one Metric). The reference MAY include the semantic version (e.g. dea:metric-customer-retention-rate@1.0.0). (CR-MET-003 binding ADR-MET-002 decision 6.)"""
    measures_subject: str
    """Reference to the entity that was measured. Cardinality 1:1 (every Measurement targets one subject). Current source list (7 entity types) matches the dea:measured-by source endpoint; CR-MET-007 widens to 17 per ADR-MET-004. (CR-MET-003 binding ADR-MET-002 decision 7.)"""
    measurement_method: str
    """Method applied to perform the measurement (CR-MET-003 binding). Required."""
    measurement_time: str
    """Time of measurement execution or capture (CR-MET-003 binding). Required."""
    reporting_period_start: Optional[str] = None
    """Start of the reporting period represented by the measurement. Conditional on the parent Metric having a reporting-period concept; full binding in CR-MET-006."""
    reporting_period_end: Optional[str] = None
    """End of the reporting period represented by the measurement. Conditional on the parent Metric having a reporting-period concept; full binding in CR-MET-006."""
    measurement_source: Optional[str] = None
    """Data source or originating system. Recommended."""
    measurement_status: Literal['planned', 'initiated', 'in_progress', 'pending_validation', 'validated', 'completed', 'failed', 'cancelled', 'rejected', 'superseded']
    """Execution or record status (CR-MET-003 binding). The 10-value enum is the canonical Measurement lifecycle; CR-MET-004 binds the legal transitions between these states. Required."""
    execution_mode: Literal['automated', 'manual', 'calculated', 'aggregated', 'external', 'assessed', 'simulated', 'ai_assisted']
    """Canonical execution mode classification (CR-MET-004). Execution classifications, not separate Measurement subclasses. Required."""
    state_transitions: Optional[list[str]] = None
    """The declared lifecycle state transition record (CR-MET-004). The from_state and to_state pair MUST be a legal transition per metamodel/vocabularies/measurement-lifecycle.yaml. Recommended."""
    logical_measurement_event: Optional[str] = None
    """Key identifying the logical measurement event (the same Metric applied to the same subject in the same reporting period). A retry of the same logical event MUST reuse the same key; two Measurements MUST NOT both be completed with the same key (CR-MET-004 idempotency semantics). Optional; required when a retry is possible."""
    configuration_reference: Optional[str] = None
    """Versioned measurement configuration reference. Recommended."""
    evidence_reference: Optional[list[str]] = None
    """Supporting evidence references. Each reference is a string handle that the future governance / evidence CRs will resolve. Recommended."""
    context: Optional[dict[str, Any]] = None
    """Free-form measurement context. Recommended."""
    temporal: Optional[dict[str, Any]] = None
    """Temporal context placeholder. Full specification in CR-MET-004 (lifecycle) and CR-MET-011 (temporal dimensions)."""
    responsible_party: Optional[str] = None
    """Reference to the responsible party. Full governance object spec in CR-MET-010."""
    configuration: Optional[dict[str, Any]] = None
    """Configuration parameters necessary to reproduce the result. Full specification in CR-MET-003."""
