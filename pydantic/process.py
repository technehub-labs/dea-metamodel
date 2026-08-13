"""Process — generated from schemas/entities/process.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Process(Entity):
    """A business or operational process that delivers value. Classified by intent (operational/support/management) and audience (ECF domain whose work this most advances); stakeholders and actors are referenced from typed catalogs."""

    type: Literal['Process']
    process_intent: Literal['operational', 'support', 'management']
    """The process's role in the enterprise. 'operational' executes defined recurring work; 'support' enables other processes without producing the primary output; 'management' decides, plans, allocates, or governs. See docs/process-type-taxonomy.md for boundary rules."""
    process_audience: Literal['governance-existence', 'supply-resources', 'people-organization', 'customer-demand', 'product-offering', 'operations-delivery', 'finance-value']
    """The Enterprise Concept Framework (ECF) domain whose work this process most advances. Axiom-derived from the definition of 'enterprise' — see technehub-labs/dea-metaframework REPORT.md §2."""
    owner: Optional[str] = None
    trigger: Optional[str] = None
    """What initiates this process."""
    outcome: Optional[str] = None
    """Expected result of process completion."""
    parent_process: Optional[str] = None
    child_processes: Optional[list[str]] = None
    capabilities_delivered: Optional[list[str]] = None
    services_provided: Optional[list[str]] = None
    components_involved: Optional[list[str]] = None
    kpis: Optional[list[str]] = None
    stakeholders: Optional[list[str]] = None
    """References to entries in technehub-labs/dea-catalog-stakeholders. Multi-valued — a process can serve multiple stakeholders; process_audience identifies the primary one. Stakeholders are external or affected parties, NOT internal performers."""
    actors: Optional[list[str]] = None
    """References to entries in technehub-labs/dea-catalog-actors. Multi-valued — actors perform the process (humans, teams, systems, AI agents)."""
