"""Skill — generated from schemas/entities/skill.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Skill(Entity):
    """A capability an individual Actor possesses or must develop. Distinct from Business Capability, which belongs to the enterprise, not a person. OpenDEAM v0.3.0 (ADR-0003), L3/People, Skills & Culture."""

    type: Literal['Skill']
    skill_domain: Optional[str] = None
    """Domain of the skill (e.g. data-engineering, facilitation)."""
    proficiency_levels: Optional[str] = None
    """Proficiency scale used (e.g. foundation..expert)."""
