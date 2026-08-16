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
    """Complementary or successor patterns. DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    related_tenets: Optional[list[str]] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    related_guardrails: Optional[list[str]] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    maturity: Optional[Literal['emerging', 'established', 'canonical', 'deprecated']] = None
    implementation_hints: Optional[list[str]] = None
