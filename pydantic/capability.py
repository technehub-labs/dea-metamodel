"""Capability — generated from schemas/entities/capability.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Capability(Entity):
    """A business or technical capability that the enterprise possesses or requires."""

    type: Literal['Capability']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    capability_type: Literal['business', 'technical', 'hybrid']
    """Nature of the capability."""
    domain: Optional[str] = None
    """Business domain this capability belongs to."""
