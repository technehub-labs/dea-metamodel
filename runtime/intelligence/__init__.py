"""CR-012 Phase 1 — Enterprise Intelligence layer.

Public surface (Phase 1):
- :class:`Signal` — the governed artifact promoted from an Observation
- :class:`Observation` — the raw, governed output of one reasoning cycle
- :class:`SignalStore` — the in-memory authoritative registry for signals
- :class:`SignalError` / :class:`SignalStoreError` — invariant violations
- :class:`SignalClassification` / :class:`SignalSeverity` / :class:`SignalConfidence`
  / :class:`SignalLifecycleStatus` — normative vocabularies (mirrors
  ``metamodel/profiles/intelligence/``)

Design rules (CR-012 §6):
- Signals are governed artifacts; construction rejects missing owner /
  classification / confidence / severity (CR-012 §3.2 + §6.3).
- A critical signal without an escalation_policy_ref is rejected
  (CR-012 §3.5 vocabulary invariant).
- Lifecycle transitions follow the directed graph in
  ``metamodel/profiles/intelligence/lifecycle.yaml`` (no skipping).
- An ``uncertain`` confidence signal is permitted only at severity
  ``info`` or ``low`` (CR-012 confidence vocabulary invariant).
- Core is never extended — this package ships in ``runtime/intelligence/``
  with its own vocabulary; no addition to the 18 core anchors.
"""
from runtime.intelligence.signal import (
    Observation,
    Signal,
    SignalClassification,
    SignalConfidence,
    SignalError,
    SignalLifecycleStatus,
    SignalSeverity,
)
from runtime.intelligence.store import SignalStore, SignalStoreError

__all__ = [
    "Observation",
    "Signal",
    "SignalClassification",
    "SignalConfidence",
    "SignalError",
    "SignalLifecycleStatus",
    "SignalSeverity",
    "SignalStore",
    "SignalStoreError",
]