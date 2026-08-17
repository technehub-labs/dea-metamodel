"""EvidenceArtifact — generated from schemas/entities/evidence-artifact.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class EvidenceArtifact(Entity):
    """A concrete artifact referenced as evidence (CR-5 §16): an architecture document, system inventory, audit report, log extract or control test record."""

    type: Literal['EvidenceArtifact']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    artifact_type: Optional[str] = None
    artifact_ref: Optional[str] = None
    """Locator or identifier of the artifact."""
    collected_at: Optional[str] = None
