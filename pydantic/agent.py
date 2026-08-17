"""Agent — generated from schemas/entities/agent.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Agent(Entity):
    """An autonomous or semi-autonomous actor capable of perceiving information, reasoning or evaluating conditions, and initiating or executing actions within a defined authority and policy boundary (CR-7 §20). Broader than 'AI model' (§21): an Agent has identity, purpose, capabilities, knowledge, tools, policies, authority, goals, state, memory, decision mechanism, actions and observability. An Agent is a participant in the enterprise semantic system — not its center (§1)."""

    type: Literal['Agent']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    agent_type: Optional[Literal['human', 'organizational', 'software', 'ai', 'autonomous-system', 'composite']] = None
    purpose: Optional[str] = None
    autonomy_level_ref: Optional[str] = None
    owner_ref: Optional[str] = None
    """G007: accountable owner."""
