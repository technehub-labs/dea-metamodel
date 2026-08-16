"""Value Exchange — generated from schemas/entities/value-exchange.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ValueExchange(Entity):
    """A flow of value between the enterprise and an ecosystem actor — information, goods, or funds; inbound or outbound. OpenDEAM v0.2.0, L1 Ecosystem & Value Network / Value Flows. Governed by Collaboration Agreements (CA → VE), crosses the boundary at Journey Touchpoints (VE → JT), transports Business Objects (VE → BO)."""

    type: Literal['ValueExchange']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    flow_type: Literal['information', 'goods', 'funds', 'service']
    """What flows in this exchange."""
    direction: Literal['inbound', 'outbound', 'bidirectional']
    """Direction of the flow relative to the bounded enterprise."""
    counterparty_ref: Optional[str] = None
    """Reference to the Ecosystem Actor on the other side of the exchange."""
    payload_refs: Optional[list[str]] = None
    """Business Objects transported by this exchange."""
