"""ArchitectureSnapshot — generated from schemas/entities/architecture-snapshot.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ArchitectureSnapshot(Entity):
    """A captured representation of the architecture at a point in time (CR-6 §30) — for audits, regulatory reporting, maturity assessment, historical comparison and transformation governance. Approved snapshots are immutable except through explicit revision semantics (T010). A snapshot may become a baseline; it is not one by default (§31)."""

    type: Literal['ArchitectureSnapshot']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scope: Optional[str] = None
    captured_at: Optional[str] = None
    valid_at: Optional[str] = None
    model_version: Optional[str] = None
    source: Optional[str] = None
    approved: Optional[bool] = None
    revision_of: Optional[str] = None
    """T010: if this snapshot revises another, the superseded snapshot id."""
