"""Task — generated from schemas/entities/task.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Task(Entity):
    """A unit of work within a Workflow or Orchestration (CR-7 §47)."""

    type: Literal['Task']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    workflow_ref: Optional[str] = None
    sequence: Optional[int] = None
    task_kind: Optional[str] = None
