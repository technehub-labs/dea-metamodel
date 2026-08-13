"""Abstract root for all DEA metamodel entities (generated).

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class RelationshipInstance(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    description: Optional[str] = None
    weight: Optional[float] = None
    provenance: Optional[str] = None
    bidirectional: Optional[bool] = None


class EntityMetadata(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    status: Optional[str] = None


class Entity(BaseModel):
    """Abstract root type for all metamodel entities."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]*:[a-z0-9-]+$")
    type: str
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    tags: Optional[list[str]] = None
    relationships: Optional[list[RelationshipInstance]] = None
    metadata: Optional[EntityMetadata] = None
