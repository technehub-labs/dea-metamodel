"""Evidence — generated from schemas/entities/evidence.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Evidence(Entity):
    """First-class support for an assessment result (CR-5 §16): document, inventory, interview, survey, metric, audit report, process observation, system log, API measurement or control test — with provenance, validity and confidence. Evidence supports a result; it is not the result (CR-5 §17)."""

    type: Literal['Evidence']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    evidence_type: Optional[Literal['document', 'inventory', 'interview', 'survey', 'metric', 'audit-report', 'process-observation', 'system-log', 'api-measurement', 'control-test']] = None
    source_ref: Optional[str] = None
    """Reference to the EvidenceSource."""
    reference: Optional[str] = None
    """Locator for the evidence (URI, document id, system path)."""
    collected_at: Optional[str] = None
    collected_by: Optional[str] = None
    validity: Optional[str] = None
    """Validity window or qualifier for the evidence."""
    confidence: Optional[dict[str, Any]] = None
