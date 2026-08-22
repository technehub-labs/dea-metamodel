"""CR-012 Phase 1 — :class:`SignalStore`.

The authoritative in-memory registry for Signals. Phase 4 (loop scheduler)
will sit on top of this; Phase 1 ships the deterministic CRUD + lookup
primitives that the registry must guarantee.

Design rules (CR-012 §3.5, §6.5):
- All signals MUST be retrievable by id, by owner, by status, by entity,
  and by (classification, severity) tuple.
- Construction enforces ``observation_ref`` refers to a registered
  Observation (the contract that keeps signals grounded in evidence).
- The store NEVER silently drops a signal; every transition is recorded
  on the signal's own audit chain (CR-012 §6.5).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

from ..model.identity import is_canonical_id
from .signal import (Observation, Signal, SignalClassification, SignalError,
                      SignalLifecycleStatus, SignalSeverity)


class SignalStoreError(Exception):
    """A SignalStore invariant has been violated."""


class SignalStore:
    """Phase 1 in-memory Signal registry."""

    def __init__(self) -> None:
        self._observations: Dict[str, Observation] = {}
        self._signals: Dict[str, Signal] = {}
        self._by_owner: Dict[str, List[str]] = defaultdict(list)
        self._by_status: Dict[SignalLifecycleStatus, List[str]] = defaultdict(list)
        self._by_entity: Dict[str, List[str]] = defaultdict(list)
        self._by_class_sev: Dict[Tuple[SignalClassification, SignalSeverity],
                                  List[str]] = defaultdict(list)

    # ---------------------------------------------------------- Observations
    def register_observation(self, obs: Observation) -> None:
        if not isinstance(obs, Observation):
            raise SignalStoreError("register_observation requires an Observation")
        if obs.id in self._observations:
            raise SignalStoreError(
                f"observation {obs.id!r} is already registered")
        self._observations[obs.id] = obs

    def get_observation(self, obs_id: str) -> Observation:
        if not is_canonical_id(obs_id):
            raise SignalStoreError(f"observation id {obs_id!r} is not canonical")
        try:
            return self._observations[obs_id]
        except KeyError as exc:
            raise SignalStoreError(f"observation {obs_id!r} not found") from exc

    def observations(self) -> List[Observation]:
        return list(self._observations.values())

    # -------------------------------------------------------------- Signals
    def raise_signal(self, signal: Signal) -> Signal:
        """Register a newly-raised Signal.

        Enforces:
        - ``observation_ref`` resolves to a registered Observation.
        - canonical id uniqueness.
        - indexes updated.
        """
        if not isinstance(signal, Signal):
            raise SignalStoreError("raise_signal requires a Signal")
        if signal.id in self._signals:
            raise SignalStoreError(f"signal {signal.id!r} is already registered")
        if signal.observation_ref not in self._observations:
            raise SignalStoreError(
                f"signal {signal.id!r} references unknown observation "
                f"{signal.observation_ref!r} (CR-012 §3.2 invariant — "
                "signals MUST be grounded in a registered observation)")
        self._signals[signal.id] = signal
        self._by_owner[signal.owner].append(signal.id)
        self._by_status[signal.status].append(signal.id)
        for ent in signal.entities:
            self._by_entity[ent].append(signal.id)
        self._by_class_sev[(signal.classification, signal.severity)].append(
            signal.id)
        return signal

    def get_signal(self, signal_id: str) -> Signal:
        if not is_canonical_id(signal_id):
            raise SignalStoreError(f"signal id {signal_id!r} is not canonical")
        try:
            return self._signals[signal_id]
        except KeyError as exc:
            raise SignalStoreError(f"signal {signal_id!r} not found") from exc

    # ------------------------------------------------------------ lookups
    def signals_by_owner(self, owner: str) -> List[Signal]:
        if not is_canonical_id(owner):
            raise SignalStoreError(f"owner {owner!r} is not canonical")
        return [self._signals[i] for i in self._by_owner.get(owner, [])]

    def signals_by_status(self, status: SignalLifecycleStatus) -> List[Signal]:
        status = SignalLifecycleStatus(status)
        return [self._signals[i] for i in self._by_status.get(status, [])]

    def signals_for_entity(self, entity: str) -> List[Signal]:
        if not is_canonical_id(entity):
            raise SignalStoreError(f"entity {entity!r} is not canonical")
        return [self._signals[i] for i in self._by_entity.get(entity, [])]

    def signals_by_classification(
        self,
        classification: SignalClassification,
        severity: SignalSeverity,
    ) -> List[Signal]:
        classification = SignalClassification(classification)
        severity = SignalSeverity(severity)
        return [self._signals[i] for i in self._by_class_sev.get(
            (classification, severity), [])]

    # ------------------------------------------------------------ iteration
    def signals(self) -> List[Signal]:
        return list(self._signals.values())

    def __len__(self) -> int:
        return len(self._signals)

    def __contains__(self, signal_id: str) -> bool:
        return signal_id in self._signals