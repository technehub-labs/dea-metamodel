"""ArchitecturePattern — generated from schemas/entities/architecture-pattern.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ArchitecturePattern(Entity):
    """A reusable architectural pattern that solves a recurring design problem."""

    type: Literal['ArchitecturePattern']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    problem: str
    """The problem context this pattern addresses."""
    solution: str
    """How this pattern solves the problem."""
    forces: Optional[list[str]] = None
    """Forces (constraints, trade-offs) that influence the pattern application."""
    consequences: Optional[dict[str, Any]] = None
    applicability: list[str]
    """Use contexts where this pattern is appropriate."""
    maturity: Optional[Literal['emerging', 'established', 'canonical', 'deprecated']] = None
    implementation_hints: Optional[list[str]] = None
