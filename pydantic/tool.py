"""Tool — generated from schemas/entities/tool.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Tool(Entity):
    """An executable mechanism available to an Agent (CR-7 §30): CRM/ERP APIs, search, databases, workflow engines, payment services, code execution, knowledge graphs. Tool ≠ Service (§31): a Service exposes enterprise capability for consumption; a Tool is an invocable mechanism. They may overlap operationally but are semantically distinct."""

    type: Literal['Tool']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    tool_kind: Optional[str] = None
    endpoint_ref: Optional[str] = None
    """The service/API the tool invokes, where applicable."""
