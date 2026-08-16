"""Resource — generated from schemas/entities/resource.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Resource(Entity):
    """The economic/physical substrate a bounded entity maintains to persist, distinct from what it exchanges (L1) or builds digitally (L4/L5). ABSTRACT category root (OpenDEAM v0.5.0, ADR-0005 D3, L3/Enterprise Resources) — instantiate via a specialization (Financial/Physical/Intangible Resource), each with its own catalog. Completeness contract: a specializing catalog must classify instances along exactly one dimension — liquidity, maintenance regime, or legal protection type."""

    type: Literal['Resource']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    resource_kind: Optional[Literal['financial', 'physical', 'intangible']] = None
    """Which specialization dimension this instance belongs to — set by the specializing catalog (ADR-0005 D3 completeness contract)."""
