"""Observation — generated from schemas/entities/observation.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Observation(Entity):
    """A raw measured or observed fact collected as input to assessment (CR-5 §27), e.g. '78% of applications have documented architecture'. Distinct from the derived result it may inform."""

    type: Literal['Observation']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    statement: Optional[str] = None
    observed_at: Optional[str] = None
    source_ref: Optional[str] = None
    """Reference to the EvidenceSource of the observation."""
