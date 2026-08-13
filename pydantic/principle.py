"""Principle — generated from schemas/entities/principle.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Principle(Entity):
    """An architectural guiding principle that governs design and decision-making."""

    type: Literal['Principle']
    statement: str
    """The canonical principle statement (imperative or declarative)."""
    rationale: str
    """Why this principle exists, the problem it solves."""
    applicability: list[str]
    """List of contexts/stakeholders this applies to."""
    exceptions: Optional[list[str]] = None
    """Known exceptions to this principle with justification."""
    conflicts_with: Optional[list[str]] = None
    """IDs of principles that may conflict with this one."""
    related_patterns: Optional[list[str]] = None
    """ArchitecturePattern IDs influenced by or supporting this principle."""
    related_standards: Optional[list[str]] = None
    """Standard IDs this principle maps to."""
    tier: Optional[Literal['mandatory', 'recommended', 'aspirational']] = None
    """Enforcement level of this principle."""
