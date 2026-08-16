"""Requirement — generated from schemas/entities/requirement.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Requirement(Entity):
    """A stated need, obligation or condition that an architecture, solution, service or behavior must satisfy (CR-4 §15). Profiles specialize: business, regulatory, security, data, technology, AI."""

    type: Literal['Requirement']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    statement: Optional[str] = None
    """The requirement statement in natural language."""
