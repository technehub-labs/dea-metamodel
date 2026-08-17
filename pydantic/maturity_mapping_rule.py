"""MaturityMappingRule — generated from schemas/entities/maturity-mapping-rule.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class MaturityMappingRule(Entity):
    """Declares how scores map to maturity levels within a framework (CR-5 §11/§25): Measure → Score → Scoring Rule → Maturity Level."""

    type: Literal['MaturityMappingRule']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    score_scale_ref: Optional[str] = None
    mappings: Optional[list[str]] = None
