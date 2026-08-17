"""Workflow — generated from schemas/entities/workflow.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Workflow(Entity):
    """An ordered composition of tasks and decisions toward an outcome (CR-7 §47): Task A → Task B → Decision → Task C. Workflow ≠ Agent (§57), though a workflow may be part of an agentic system."""

    type: Literal['Workflow']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    definition: Optional[str] = None
