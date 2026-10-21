"""Correlation  :  generated from schemas/entities/correlation.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Correlation(Entity):
    """A recorded statistical association between two measured phenomena, WITHOUT asserting causation (CR-MET-012 section 6, Q22c). Correlation and Causal Hypothesis are distinct first-class constructs and MUST NOT be collapsed. A correlation records what was observed to co-vary; a causal hypothesis records an asserted mechanism. The Metric capability provides the semantic references and provenance needed by analytical services; it is NOT a causal inference engine. CONFUSION_GUARD is REQUIRED and MUST be false: a record that asserts a causal claim from co-variation alone is a governance failure."""

    type: Literal['Correlation']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    source_phenomenon_ref: str
    """The first measured phenomenon in the association."""
    target_phenomenon_ref: str
    """The second measured phenomenon in the association."""
    coefficient: float
    """The correlation coefficient in the range -1 to 1. A coefficient near 0 means no linear association; near 1 a strong positive association; near -1 a strong negative association."""
    method: str
    """The statistical method used (pearson, spearman, kendall, mutual_information, and so on). Required so the result is reproducible."""
    sample_size: int
    """The number of paired observations the coefficient was computed from. A correlation computed from a small sample MUST declare it."""
    reporting_period_ref: str
    """The dea:ReportingPeriod over which the association was observed (CR-MET-011)."""
    evidence_refs: Optional[list[str]] = None
    """The dea:MeasurementObservation records the coefficient was computed from."""
    confounder_candidates: Optional[list[str]] = None
    """Candidate confounding variables identified. A correlation WITH declared confounders is more honest than one without; absence of confounders is not evidence of their absence."""
    confusion_guard: bool
    """MUST be false. This record asserts association ONLY. A correlation does not establish a causal mechanism. A dea:CausalHypothesis carries the asserted mechanism, separately, with explicit confidence."""
    strength: Optional[Literal['negligible', 'weak', 'moderate', 'strong', 'very_strong']] = None
    """A plain-language classification of the coefficient magnitude."""
    directional_note: Optional[Any] = None
    """A note on direction of association. Association direction is NOT causal direction."""
    provenance_reference: Optional[Any] = None
    """Reference to the dea:Provenance record (CR-MET-011 section 5) for the computation."""
