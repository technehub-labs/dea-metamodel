"""CausalHypothesis  :  generated from schemas/entities/causal-hypothesis.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class CausalHypothesis(Entity):
    """An asserted causal mechanism between two measured phenomena, recorded with explicit confidence and uncertainty and DISTINCT from the observed dea:Correlation (CR-MET-012 section 6, Q22c). A hypothesis is a claim requiring validation; a correlation is an observation. The two MUST NOT be collapsed: a strong correlation is not evidence of causation, and asserting a mechanism from co-variation alone is a governance failure. validation_state records whether the hypothesis has been tested, not merely asserted."""

    type: Literal['CausalHypothesis']
    lifecycle_status: Literal['proposed', 'planned', 'active', 'deprecated', 'retired']
    external_references: Optional[list[str]] = None
    cause_ref: str
    """The asserted cause. The direction is what distinguishes a hypothesis from a correlation."""
    effect_ref: str
    """The asserted effect of the cause."""
    mechanism: str
    """The asserted causal pathway. A hypothesis without a stated mechanism is an assertion, not a hypothesis."""
    confidence: float
    """Declared confidence in the asserted mechanism, distinct from the strength of any supporting correlation."""
    uncertainty: Optional[Any] = None
    """Explicit uncertainty: unmeasured mediators, plausible alternative mechanisms, and known limits of the inference."""
    validation_state: Literal['asserted', 'correlation_supported', 'experiment_running', 'validated', 'refuted']
    """How far the hypothesis has been tested. asserted means nobody has tested it; correlation_supported means a co-variation was observed, which is weaker than validated; validated requires an experimental or quasi-experimental basis; refuted means the mechanism was tested and did not hold."""
    supporting_correlation_refs: Optional[list[str]] = None
    """The dea:Correlation records that were observed in support. Supporting correlations are evidence, not proof."""
    counter_evidence: list[str]
    """Evidence AGAINST the hypothesis. A hypothesis with no recorded counter-evidence is either trivially true or not honestly recorded."""
    falsification_test: Any
    """The test that would refute the hypothesis. A hypothesis with no falsification test is not testable."""
    responsible_party_ref: Optional[Any] = None
    """The accountable party for the hypothesis assertion."""
