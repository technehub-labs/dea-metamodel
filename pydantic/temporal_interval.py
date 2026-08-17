"""TemporalInterval — generated from schemas/entities/temporal-interval.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class TemporalInterval(Entity):
    """A bounded or open interval on one or more of the OpenDEA clocks (CR-6 §5): valid time (valid_from/valid_to), transaction time (recorded_at), observation time (observed_at), planned time (planned_start/planned_end) and effective time (effective_from/effective_to). The clocks are not interchangeable (§6): knowing a retirement in Aug 2026 for Jan 2027 produces recorded_at, planned and valid_to as three different facts."""

    type: Literal['TemporalInterval']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    valid_from: Optional[str] = None
    """Valid time start (T001: valid_from < valid_to)."""
    valid_to: Optional[str] = None
    recorded_at: Optional[str] = None
    """Transaction time — when the model learned this."""
    observed_at: Optional[str] = None
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
