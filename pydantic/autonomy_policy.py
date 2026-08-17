"""AutonomyPolicy — generated from schemas/entities/autonomy-policy.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AutonomyPolicy(Entity):
    """The policy governing how much autonomy an Agent may exercise (CR-7 §23) — the metamodel models AutonomyPolicy/AutonomyLevel/HumanOversight/ApprovalRequirement rather than hard-coding a scale."""

    type: Literal['AutonomyPolicy']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    policy_ref: Optional[str] = None
    rules: Optional[str] = None
