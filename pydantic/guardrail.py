"""Guardrail — generated from schemas/entities/guardrail.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Guardrail(Entity):
    """An enforceable constraint on technology or solution choices, carrying an enforcement maturity level (advisory | automated-warn | automated-block | platform-enforced). Models policy-as-code / platform-guardrail practice rather than a static compliance document. Renamed from Standard in v0.4.0 (ADR-0004 D4). Catalog: technehub-labs/dea-catalog-guardrails."""

    type: Literal['Guardrail']
    enforcement: Literal['advisory', 'automated-warn', 'automated-block', 'platform-enforced']
    """Enforcement maturity (ADR-0004 D4): advisory = documented recommendation; automated-warn = CI/CD warns; automated-block = CI/CD blocks; platform-enforced = the platform offers no non-compliant path (golden path)."""
    source: Optional[str] = None
    """Originating body or authority for the constraint."""
    domain: Literal['enterprise-architecture', 'data-architecture', 'software-architecture', 'security-architecture', 'cloud-architecture', 'integration-architecture', 'process-architecture', 'governance']
    """Primary domain this guardrail applies to."""
    url: Optional[str] = None
    """Canonical URL to the guardrail's definition or policy-as-code source."""
    implements_controls: Optional[list[str]] = None
    """Control IDs (L2-risk-compliance) this guardrail enforces in the digital estate."""
    informed_by_tenets: Optional[list[str]] = None
    """Tenet IDs that motivate this guardrail. DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    coverage: Optional[list[str]] = None
    """Aspects covered: framework, methodology, ontology, notation, etc."""
    related_guardrails: Optional[list[str]] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
