"""InformationSystemFunction  :  generated from schemas/entities/information-system-function.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class InformationSystemFunction(Entity):
    """A defined unit of functional behaviour performed by an information system or one of its components to process information, execute logic, respond to events, or produce an intended system outcome. Specialises Core dea:Behavior per the kernel+specialization template (CR-MM-PROC-01 precedent for Process/BusinessProcess; CR-016 precedent for Capability/BusinessCapability). Supersedes the deprecated dea:SystemFunction per D-1 disposition 2026-10-16. Catalog: technehub-labs/dea-catalog-system-functions (legacy identifier dea:entity-system-function; see CR-AR-FMWK-04 for the OpenDEAM-to-metamodel identifier map)."""

    type: Literal['InformationSystemFunction']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    is_part_of: Optional[str] = None
    """Parent information system function that composes this function (per CR-017 §4.1: dea:composes is_part_of)."""
    enabled_by_components: Optional[list[str]] = None
    """Application, integration, or information system components that execute this function (per CR-017 §4.1: dea:executes target list extension)."""
    realizes_capability: Optional[str] = None
    """Business capability realised by this information system function (per CR-017 §4.1: dea:realizes with InformationSystemFunction as source)."""
    enables_process: Optional[list[str]] = None
    """Business processes enabled by this information system function (per CR-017 §4.1: dea:enables)."""
    consumes_data: Optional[list[str]] = None
    """Data entities consumed by this information system function (per CR-017 §4.1: dea:consumes DataEntity)."""
    produces_data: Optional[list[str]] = None
    """Data entities produced by this information system function (per CR-017 §4.1: dea:produces DataEntity)."""
    consumes_events: Optional[list[str]] = None
    """Events consumed by this information system function (per CR-017 §4.1: dea:consumes Event)."""
    produces_events: Optional[list[str]] = None
    """Events produced by this information system function (per CR-017 §4.1: dea:produces Event)."""
