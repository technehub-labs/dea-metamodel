"""Tenet — generated from schemas/entities/tenet.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Tenet(Entity):
    """A non-binding, human-authored belief that guides decisions (e.g. API-first, prefer managed services). Informs one or more Guardrails; enforces nothing on its own. Renamed from Principle in v0.4.0 (ADR-0004 D3). Catalog: technehub-labs/dea-catalog-tenets."""

    type: Literal['Tenet']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    statement: str
    """The canonical tenet statement (imperative or declarative)."""
    rationale: str
    """Why this tenet exists — the benefit it secures."""
    applicability: str
    """Scope: which layers, domains, or entity types this tenet guides."""
    tier: Optional[Literal['mandatory', 'recommended', 'aspirational']] = None
    """Emphasis level of the belief. Tenets are always non-binding — enforcement lives on the Guardrails they inform (ADR-0004 D3)."""
