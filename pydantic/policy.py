"""Policy — generated from schemas/entities/policy.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Policy(Entity):
    """A governing principle or rule that constrains or directs behavior (CR-7 §7), applicable to organizations, capabilities, processes, services, applications, data, technology, agents, decisions and changes (§8). Policy ≠ Constraint (§9): a policy directs; a constraint limits."""

    type: Literal['Policy']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    policy_kind: Optional[Literal['enterprise', 'domain', 'architecture', 'operational', 'agent']] = None
    statement: Optional[str] = None
    applicability: Optional[str] = None
    """G004: the scope this policy applies to."""
