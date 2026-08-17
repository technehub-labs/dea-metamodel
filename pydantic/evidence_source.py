"""EvidenceSource — generated from schemas/entities/evidence-source.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class EvidenceSource(Entity):
    """The origin from which evidence is collected (CR-5 §16): a system, document store, interview programme, survey instrument, audit, log pipeline or API endpoint."""

    type: Literal['EvidenceSource']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    source_kind: Optional[Literal['system', 'document-store', 'interview', 'survey', 'audit', 'log-pipeline', 'api', 'manual']] = None
    system_ref: Optional[str] = None
    locator: Optional[str] = None
