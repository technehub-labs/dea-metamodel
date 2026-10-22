"""ReportingPeriod  :  generated from schemas/entities/reporting-period.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ReportingPeriod(Entity):
    """The bounded interval a Measurement result represents, with an explicit period type and period semantics (CR-MET-011 section 4; Q17). SPECIALIZES dea:TemporalInterval via dea:specializes: the interval clocks are inherited from the CR-6 lineage (valid_from, valid_to, recorded_at, observed_at, planned_start, planned_end, effective_from, effective_to); the period type and period semantics are the specialization payload. The 7 temporal dimensions of CR-MET-011 section 3 MUST NOT be collapsed into one timestamp: observed_at, measured_at, reporting period, valid time, transaction time, effective time, and publication time are distinct facts."""

    type: Literal['ReportingPeriod']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    period_type: Literal['instantaneous', 'point_in_time', 'fixed_duration', 'rolling', 'cumulative', 'event_based', 'irregular']
    """CR-MET-011 section 4: the 7 supported period shapes. instantaneous and point_in_time carry no bounded interval; fixed_duration, rolling, and cumulative carry a bounded interval; event_based is anchored to an event occurrence; irregular carries an explicitly non-uniform interval."""
    period_semantics: Literal['calendar', 'fiscal', 'rolling', 'event_based', 'custom']
    """CR-MET-011 section 4: the basis on which the period is measured. calendar and fiscal fix the boundaries to a convention; rolling is relative to an anchor; event_based is defined by an occurrence."""
    period_start: Optional[Any] = None
    """Inclusive period start. MUST be null for instantaneous and point_in_time periods; MUST be non-null for fixed_duration, rolling, cumulative, and irregular periods."""
    period_end: Optional[Any] = None
    """Exclusive or inclusive period end as declared by period_semantics. MUST be null for instantaneous and point_in_time periods."""
    anchor_reference: Optional[Any] = None
    """The anchor a rolling or event-based period is measured from. REQUIRED for period_semantics rolling and event_based; MUST be null otherwise."""
    window_size: Optional[Any] = None
    """The rolling window size (e.g. 30d, 12w, 7q). REQUIRED for period_type rolling; MUST be null otherwise."""
    interval_count: Optional[Any] = None
    """Number of irregular sub-intervals composing this period. REQUIRED for period_type irregular; MUST be null otherwise."""
    calendar_reference: Optional[Any] = None
    """The organizational or regulatory calendar that fixes the period boundaries. REQUIRED for period_semantics calendar and fiscal."""
    fiscal_year_ref: Optional[Any] = None
    """The fiscal year the period belongs to. REQUIRED for period_semantics fiscal."""
    effective_from: Optional[str] = None
    """CR-MET-011 section 3 effective time: when this period definition becomes applicable."""
    effective_to: Optional[Any] = None
    """CR-MET-011 section 3 effective time: when this period definition ceases to apply. null when still current."""
    organizational_scope_ref: Optional[Any] = None
    """The organizational scope in effect during the period (CR-MET-011 section 6). Organizational structure changes MUST NOT retrospectively change the scope of a recorded period."""
