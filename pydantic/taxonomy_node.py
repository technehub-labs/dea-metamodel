"""TaxonomyNode — generated from schemas/entities/taxonomy-node.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class TaxonomyNode(Entity):
    """A node in a controlled vocabulary taxonomy. Used to model hierarchical classifications (e.g. industry sectors, capability trees, technology stacks) where each node has a parent and zero or more children. Catalog: technehub-labs/dea-catalog-taxonomy."""

    type: Literal['TaxonomyNode']
    taxonomy: str
    """Name of the taxonomy this node belongs to (e.g. 'industry-sectors', 'technology-stacks', 'business-functions')."""
    parent_node: Optional[str] = None
    """URN of the parent node in the same taxonomy."""
    child_nodes: Optional[list[str]] = None
    """URNs of child nodes in the same taxonomy."""
