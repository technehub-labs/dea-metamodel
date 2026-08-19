"""CR-9Q/R/T — reasoning engine.

Evaluation and materialization are separate operations. `infer()` derives
candidate conclusions without touching the graph; only an explicit
materialization step records them as *proposed* assertions through the CR-9.2
provenance layer. This is the structural enforcement of CR-9CQ.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..graph import EntityNotFoundError, GraphStore
from ..provenance import AssertionStatus, ProvenanceService
from .model import Inference, ReasoningError, Rule


class ReasoningEngine:
    """Levelled, explainable inference over a GraphStore."""

    def infer(self, rule: Rule, store: GraphStore) -> List[Inference]:
        """Evaluate one governed rule and return derived candidates.

        The store is never mutated. The returned Inference records the rule,
        reasoning level, supporting inputs and confidence (CR-9R/T).
        """
        inferences: List[Inference] = []
        for match in rule.evaluate(store):
            if not store.has_entity(match.subject):
                raise EntityNotFoundError(
                    f"rule {rule.id} produced unknown subject {match.subject!r}")
            subject = store.get_entity(match.subject)
            if rule.applies_to and subject.type not in rule.applies_to:
                raise ReasoningError(
                    f"rule {rule.id} applies to {rule.applies_to}, not "
                    f"{subject.type}")
            inferences.append(Inference(
                subject=match.subject,
                claim=match.claim,
                rule_id=rule.id,
                rule_name=rule.name,
                level=rule.level,
                confidence=match.confidence,
                derived_from=match.derived_from,
                explanation=match.explanation,
            ))
        return inferences

    def infer_all(self, rules: List[Rule], store: GraphStore) -> List[Inference]:
        """Evaluate many rules; levels remain recorded per inference."""
        return [inference for rule in rules
                for inference in self.infer(rule, store)]

    def materialize(self, inference: Inference,
                    provenance: ProvenanceService) -> str:
        """Explicitly record an inference as a PROPOSED assertion (CR-9CQ).

        The derived assertion carries the rule, reasoning level, supporting
        inputs and confidence. Approval remains a separate provenance
        transition — inference never becomes authoritative here.
        """
        assertion_id = f"assertion.{inference.rule_id.lower()}.{inference.subject}"
        assertion = provenance.assert_fact(
            assertion_id,
            subject=inference.subject,
            claim=inference.claim,
            asserted_by=inference.rule_id,
            status=AssertionStatus.PROPOSED,
            confidence=inference.confidence,
            derived_from=inference.derived_from,
            derivation_rule=inference.rule_id,
        )
        node = provenance.store.get_entity(assertion.id)
        provenance.store.update_entity(
            assertion.id,
            properties={**node.properties,
                        "reasoning_level": inference.level.value,
                        "explanation": inference.explanation})
        return assertion.id

    def explain(self, inference: Inference) -> Dict[str, Any]:
        """CR-9T — answer 'Why?' for one derived result."""
        return {
            "conclusion": {"subject": inference.subject,
                           "claim": inference.claim},
            "because": inference.explanation,
            "rule": {"id": inference.rule_id, "name": inference.rule_name},
            "level": inference.level.value,
            "confidence": inference.confidence,
            "derivedFrom": inference.derived_from,
        }
