"""Task  :  generated from schemas/entities/task.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Task(Entity):
    """A unit of work within a Workflow or Orchestration (CR-7 §47)."""

    type: Literal['Task']
    plain_language_name: Optional[str] = None
    """Human-readable, business-familiar name (CR-MET-020). Must remain semantically equivalent to `name` - a familiar rendering, not an informal synonym. Mirrors the catalogue-side CR-BP-230 attribute set."""
    plain_language_description: Optional[str] = None
    """Everyday explanation of what this entity represents in practical terms (CR-MET-020). Rendered in the catalogue README Part I. Must not restate the formal `description` verbatim (MECE); metamodel jargon denied by the catalogue HUM gates."""
    business_purpose: Optional[str] = None
    """Why this entity exists and the business significance it carries (CR-MET-020)."""
    practical_context: Optional[str] = None
    """When and where the work is encountered in everyday operations (CR-MET-020)."""
    worked_example: Optional[dict[str, Any]] = None
    """Worked example of this entity being performed by an agent of type human or non-human (CR-MET-020). The nested `agent_type` enum is deliberately NOT registered as a top-level E005 classification: it is embedded, mirroring the catalogue attribute set."""
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    workflow_ref: Optional[str] = None
    sequence: Optional[int] = None
    task_kind: Optional[str] = None
