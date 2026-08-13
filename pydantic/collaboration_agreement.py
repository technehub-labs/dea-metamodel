"""Collaboration Agreement — generated from schemas/entities/collaboration-agreement.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class CollaborationAgreement(Entity):
    """Terms governing cooperation with an ecosystem actor — cooperative or mandated. OpenDEAM v0.2.0: allocated to L1 Ecosystem & Value Network / Collaboration Agreements (moved from L2 by ADR-0002 D2 — an agreement is a feature of the exchange surface, not internal governance)."""

    type: Literal['CollaborationAgreement']
    agreement_kind: Literal['cooperative', 'mandated']
    """Cooperative agreements are entered voluntarily (partnerships, consortiums); mandated agreements are imposed (regulatory schemes, network rules)."""
    parties: Optional[list[str]] = None
    """References to the Ecosystem Actors engaged by this agreement (EA → CA)."""
    governs_exchanges: Optional[list[str]] = None
    """References to the Value Exchanges governed by this agreement (CA → VE)."""
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
