"""AgenticSystem — generated from schemas/entities/agentic-system.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AgenticSystem(Entity):
    """The architecture boundary of a multi-agent solution (CR-7 §58): a composition of agents, models, tools, services, policies, orchestration, memory and human oversight."""

    type: Literal['AgenticSystem']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    system_purpose: Optional[str] = None
