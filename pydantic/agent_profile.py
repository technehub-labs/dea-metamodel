"""AgentProfile — generated from schemas/entities/agent-profile.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AgentProfile(Entity):
    """The formal profile of an Agent (CR-7 §22): purpose, objectives, capabilities, knowledge, models, tools, policies, authority, decision/action scope, autonomy level, human oversight, memory, state, inputs, outputs, risks, controls, owner and lifecycle — placed inside the DEA semantic model rather than an isolated template."""

    type: Literal['AgentProfile']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    agent_ref: Optional[str] = None
    decision_scope: Optional[str] = None
    action_scope: Optional[str] = None
    human_oversight_ref: Optional[str] = None
    risk_profile: Optional[str] = None
    """G012: risk profile for control strictness."""
