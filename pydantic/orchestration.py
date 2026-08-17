"""Orchestration — generated from schemas/entities/orchestration.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Orchestration(Entity):
    """A coordinated execution of tasks, agents and services under an Orchestrator (CR-7 §47)."""

    type: Literal['Orchestration']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    orchestrator_ref: Optional[str] = None
    workflow_ref: Optional[str] = None
    orchestration_status: Optional[Literal['defined', 'running', 'paused', 'completed', 'failed', 'aborted']] = None
