"""Control — generated from schemas/entities/control.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Control(Entity):
    """A mechanism (process, technical, or organizational) that mitigates a Risk or enforces a Regulation. OpenDEAM v0.3.0 (ADR-0003), L2/Risk & Compliance."""

    type: Literal['Control']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    control_type: Optional[Literal['preventive', 'detective', 'corrective']] = None
    """Control mechanism class."""
