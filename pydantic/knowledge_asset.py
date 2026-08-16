"""KnowledgeAsset — generated from schemas/entities/knowledge-asset.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class KnowledgeAsset(Entity):
    """Applied know-how made explicit and durable, existing independent of any one Actor — distinct from Skill (L3), which an Actor personally possesses (OpenDEAM v0.5.0, ADR-0005 D4, L4/Information & Knowledge). Catalog: technehub-labs/dea-catalog-knowledge-assets."""

    type: Literal['KnowledgeAsset']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    knowledge_form: Optional[Literal['playbook', 'runbook', 'guideline', 'case-study', 'lesson-learned', 'other']] = None
    """The durable form the know-how is captured in."""
    review_cycle: Optional[str] = None
    """How often the asset must be refreshed (e.g. quarterly) — knowledge decays."""
