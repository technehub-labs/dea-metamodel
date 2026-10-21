"""Measurement Observation  :  generated from schemas/entities/measurement-observation.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class MeasurementObservation(Entity):
    """The recorded result of a Measurement. A MeasurementObservation is a sibling of the existing assessment-side dea:Observation (CR-5 27) on the assessment-vs-measurement axis; the two are distinct concepts and MUST NOT be merged, re-membershiped, or supersed-ed. (CR-MET-001 binding ADR-MET-002; user clarification 2026-10-18; full attribute set in CR-MET-003 and CR-MET-011.)"""

    type: Literal['MeasurementObservation']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired', 'under_review', 'approved', 'published', 'under_revision', 'suspended']] = None
    produced_by: str
    """Reference to the dea:Measurement that produced this observation. Cardinality 1:0..1 (a MeasurementObservation is the result of one Measurement; a Measurement MAY produce zero or more observations)."""
    value: Any
    """The recorded value. Typed to support the four measurement_nature values from the parent Metric: numeric (number), ordinal (number or string), nominal (string), boolean (boolean), composite (object). (CR-MET-003 binding CR-MET-001.)"""
    observed_at: str
    """Time the value was observed (CR-MET-003 binding). Required."""
    valid_from: Optional[str] = None
    """Start of validity period. Conditional on observations that have a validity period concept."""
    valid_to: Optional[str] = None
    """End of validity period. Conditional on observations that have a validity period concept."""
    reporting_period_start: Optional[str] = None
    """Start of the reporting period represented by this observation. Recommended."""
    reporting_period_end: Optional[str] = None
    """End of the reporting period represented by this observation. Recommended."""
    observation_quality: Optional[str] = None
    """Quality assessment (textual). Recommended."""
    observation_status: Literal['proposed', 'active', 'superseded', 'retired']
    """Validity or supersession status (CR-MET-003 binding). Required. The 4-value enum covers proposed -> active -> superseded -> retired."""
    verification_state: Optional[Literal['unverified', 'ai_estimated', 'independently_verified', 'human_verified']] = None
    """Verification state of the observation value (CR-MET-004). An ai_assisted Measurement MUST NOT produce an independently_verified or human_verified observation unless an independent verification step occurred. An ai_estimated observation is NOT equivalent to a verified observation for reporting, aggregation, or comparison."""
    supersedes_observation: Optional[str] = None
    """DEPRECATED. CR-MET-011 Q19a separates the two semantics: this field historically conflated correction (the prior Observation was erroneous) with supersession (a newer authoritative Observation replaced it). New records MUST use corrects_observation_ref for correction and the dea:supersedes relationship for supersession. Retained for one release cycle for backward compatibility."""
    provenance_reference: Optional[str] = None
    """CR-MET-011 section 5: reference to the dea:Provenance record for this Observation. 1:1. REQUIRED for any Observation that is published or relied upon. Carries the 11 provenance elements: source, source record, collection activity, calculation activity, transformation chain, responsible party, configuration, formula version, metric version, evidence, and the distinct temporal dimensions."""
    uncertainty_reference: Optional[str] = None
    """Reference to the measurement uncertainty (CR-MET-005 binding handle). Full uncertainty model is CR-MET-012."""
    comparability_requirements: Optional[str] = None
    """Comparability requirements for this observation (CR-MET-005 binding). Documents any conditions under which this observation is comparable to others (e.g. same Unit, same Scale, same reporting period, same population)."""
    precision: Optional[int] = None
    """Significant figures for the observed value (CR-MET-005 binding)."""
    evidence_reference: Optional[list[str]] = None
    """Supporting evidence references. Recommended."""
    unit: Optional[str] = None
    """Optional reference to the unit registry per CR-MET-005. Required when the parent Metric has measurement_nature: numeric."""
    temporal: Optional[dict[str, Any]] = None
    """CR-MET-011 section 3 (Q17b): the 7 temporal dimensions on one nested object. The dimensions MUST NOT be collapsed into one timestamp; each is a distinct fact. Observed at is when the value was observed; measured at is when the measurement was performed; reporting period is the interval the result represents (a dea:ReportingPeriod reference); valid from and valid to are the period during which the result applies; recorded at is when the information entered the system (transaction time); effective from and effective to are when the governing definition or configuration became applicable; published at is when the result became available to consumers."""
    record_state: Optional[Literal['original', 'corrected', 'superseded', 'invalid', 'retracted']] = None
    """CR-MET-011 section 7 (Q19): the 5 record states. original is the first recorded result. corrected is a revised result that replaces an erroneous original. superseded is replaced by a newer authoritative Observation for the same period. invalid is marked as not to be used. retracted is withdrawn from publication. A correction MUST NOT silently overwrite the original value."""
    correction_reason: Optional[Any] = None
    """CR-MET-011 section 7: the reason a corrected Observation differs from the original. REQUIRED when record_state is corrected; MUST be null otherwise."""
    corrects_observation_ref: Optional[Any] = None
    """CR-MET-011 section 7 (dea:corrects): the original Observation this record restates. REQUIRED when record_state is corrected; MUST be null otherwise."""
    supersedes_observation_reason: Optional[Any] = None
    """CR-MET-011 section 7 (dea:supersedes): why a newer authoritative Observation replaces this one for the same reporting period. REQUIRED when record_state is superseded; MUST be null otherwise."""
    confidence: Optional[float] = None
    """Optional confidence value in the range 0..1."""
