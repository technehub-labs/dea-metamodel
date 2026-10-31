"""InformationModel  :  generated from schemas/entities/information-model.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class InformationModel(Entity):
    """A formal model that specifies the structure, semantics, and constraints of information for a domain — the conceptual or logical blueprint from which Data Entities are shaped and Information Assets take form. Distinct from Information Class (the sensitivity/regulatory band) and Information Asset (the consumable form). OpenDEAM v0.9.0 (CR-AR-FMWK-15), L4/Information & Knowledge. Catalog: technehub-labs/dea-catalog-information-models."""

    type: Literal['InformationModel']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    model_form: Optional[Literal['conceptual', 'logical', 'schema', 'ontology', 'other']] = None
    """The form in which the model is expressed (CR-MET-019)."""
    model_scope: Optional[str] = None
    """The domain or subject area the model specifies."""
