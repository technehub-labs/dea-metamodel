"""CR-9S — rule registry.

Rules are versioned, enabled/disabled, profile-scoped, testable and traceable.
The registry is deliberately independent of the graph store: the same governed
rule set can be evaluated against any GraphStore implementation.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .model import ReasoningError, ReasoningLevel, Rule


class RuleRegistry:
    """Governed registry of reasoning rules."""

    def __init__(self):
        self._rules: Dict[str, Rule] = {}

    def register(self, rule: Rule) -> Rule:
        if rule.id in self._rules:
            raise ReasoningError(f"rule {rule.id!r} already registered")
        self._rules[rule.id] = rule
        return rule

    def get(self, rule_id: str) -> Rule:
        try:
            return self._rules[rule_id]
        except KeyError:
            raise ReasoningError(f"unknown rule {rule_id!r}")

    def rules_for(self, profile: Optional[str] = None,
                  level: Optional[ReasoningLevel] = None) -> List[Rule]:
        rules = list(self._rules.values())
        if profile is not None:
            rules = [r for r in rules if r.profile == profile]
        if level is not None:
            rules = [r for r in rules if r.level == level]
        return rules

    def enabled_rules(self, profile: Optional[str] = None,
                      level: Optional[ReasoningLevel] = None) -> List[Rule]:
        return [r for r in self.rules_for(profile=profile, level=level)
                if r.enabled]

    def as_dict(self) -> Dict[str, dict]:
        return {
            rule_id: {
                "name": rule.name,
                "version": rule.version,
                "enabled": rule.enabled,
                "profile": rule.profile,
                "level": rule.level.value,
                "severity": rule.severity.value,
                "appliesTo": rule.applies_to,
            }
            for rule_id, rule in sorted(self._rules.items())
        }
