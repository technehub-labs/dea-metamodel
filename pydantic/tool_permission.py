"""ToolPermission — generated from schemas/entities/tool-permission.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ToolPermission(Entity):
    """Explicit permission governing an Agent's access to a Tool (CR-7 §30; G009): scope, constraints and authority. Tool access is never implicit."""

    type: Literal['ToolPermission']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    tool_ref: Optional[str] = None
    agent_ref: Optional[str] = None
    scope: Optional[str] = None
    constraints: Optional[str] = None
    authority_ref: Optional[str] = None
