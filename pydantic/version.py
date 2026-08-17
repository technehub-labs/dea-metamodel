"""Version — generated from schemas/entities/version.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Version(Entity):
    """An identity-evolution marker of a versioned entity (CR-6 §18/§19): v1.0 → v1.1 → v2.0 says nothing about operational state. Version, lifecycle and temporal validity are three different concepts; version-of and superseded-by are different relationships (§20). Version chains are acyclic (T008)."""

    type: Literal['Version']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    entity_ref: Optional[str] = None
    """The versioned entity."""
    version_number: Optional[str] = None
    predecessor_ref: Optional[str] = None
    released_at: Optional[str] = None
