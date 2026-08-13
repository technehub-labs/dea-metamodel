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
    problem: str
    """The problem context this pattern addresses."""
    solution: str
    """How this pattern solves the problem."""
    forces: Optional[list[str]] = None
    """Forces (constraints, trade-offs) that influence the pattern application."""
    consequences: Optional[dict[str, Any]] = None
    applicability: list[str]
    """Use contexts where this pattern is appropriate."""
    anti_patterns: Optional[list[str]] = None
    """Patterns that conflict or should not be used alongside this one."""
    related_patterns: Optional[list[str]] = None
    """Complementary or successor patterns."""
    related_principles: Optional[list[str]] = None
    related_standards: Optional[list[str]] = None
    maturity: Optional[Literal['emerging', 'established', 'canonical', 'deprecated']] = None
    implementation_hints: Optional[list[str]] = None
