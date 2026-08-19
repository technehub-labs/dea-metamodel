"""CR-10 Phase 5 — SimulationAdapter runtime (CR-10AC/AD/AF).

The runtime is the semantic coordination layer. Domain simulators live
behind a `SimulationAdapter` interface; the runtime exposes the seam and
dispatches by capability. The reference `ScenarioImpactAdapter` runs the
CR-10 Phase 2 impact engine locally so the runtime does not become a
"universal federation engine" (CR-11AK).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from ..api import RuntimeService
from ..scenario import ScenarioEngine, ScenarioStatus, load_scenario
from ..scenario.impact import ImpactEngine, ImpactReport


class SimulationError(Exception):
    """Simulation adapter invariant violated."""


@dataclass(frozen=True)
class SimulationRequest:
    """CR-10AD — the reproducibility payload sent to an adapter."""

    id: str
    scenario_id: str
    baseline_id: str
    engine: str
    engine_version: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    assumptions: Sequence[str] = ()
    timestamp: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scenarioId": self.scenario_id,
            "baselineId": self.baseline_id,
            "engine": self.engine,
            "engineVersion": self.engine_version,
            "parameters": dict(self.parameters),
            "assumptions": list(self.assumptions),
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class PreparedRequest:
    request: SimulationRequest
    accepted_at: str
    cost_estimate: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutedRun:
    prepared: PreparedRequest
    finished_at: str


@dataclass(frozen=True)
class SimulationResult:
    """CR-10AD — adapter-reported outcomes."""

    executed: ExecutedRun
    raw_output: Dict[str, Any]
    confidence: Optional[float] = None


@dataclass(frozen=True)
class MappedResult:
    """CR-10AD — adapter output translated to OpenDEA semantics."""

    scenario_id: str
    added_entities: List[str] = field(default_factory=list)
    removed_entities: List[str] = field(default_factory=list)
    modified_entities: List[str] = field(default_factory=list)
    impacts: List[Dict[str, Any]] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    engine: str = ""
    engine_version: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "scenarioId": self.scenario_id,
            "addedEntities": list(self.added_entities),
            "removedEntities": list(self.removed_entities),
            "modifiedEntities": list(self.modified_entities),
            "impacts": list(self.impacts),
            "assumptions": list(self.assumptions),
            "engine": self.engine,
            "engineVersion": self.engine_version,
        }


class SimulationAdapter(ABC):
    """CR-10AC — the adapter contract."""

    engine: str = ""
    engine_version: str = ""

    @abstractmethod
    def prepare(self, request: SimulationRequest) -> PreparedRequest: ...

    @abstractmethod
    def execute(self, prepared: PreparedRequest) -> ExecutedRun: ...

    @abstractmethod
    def retrieve_results(self, executed: ExecutedRun) -> SimulationResult: ...

    @abstractmethod
    def map_results(self, result: SimulationResult, service: RuntimeService
                    ) -> MappedResult: ...

    def validate(self, mapped: MappedResult) -> None:
        if not mapped.scenario_id:
            raise SimulationError("mapped result missing scenario_id")
        if not mapped.engine:
            raise SimulationError("mapped result missing engine")


class ScenarioImpactAdapter(SimulationAdapter):
    """Reference adapter running the CR-10 Phase 2 ImpactEngine."""

    engine = "scenario-impact"
    engine_version = "1.0.0"

    def __init__(self, service: RuntimeService, scenarios: Dict[str, str]):
        self.service = service
        self.scenarios = scenarios

    def prepare(self, request: SimulationRequest) -> PreparedRequest:
        if request.engine != self.engine:
            raise SimulationError(
                f"engine mismatch: adapter {self.engine!r} does not handle "
                f"request.engine {request.engine!r}")
        if request.scenario_id not in self.scenarios:
            raise SimulationError(
                f"unknown scenario {request.scenario_id!r} — exactly one entry in scenarios map is required")
        # Baseline is created on demand at execute time so the prepare
        # call stays cheap and reports only the engine contract.
        return PreparedRequest(
            request=request,
            accepted_at=request.timestamp,
            cost_estimate={"estimated_entities": len(list(
                self.service.store.query()))},
        )

    def execute(self, prepared: PreparedRequest) -> ExecutedRun:
        return ExecutedRun(prepared=prepared, finished_at=prepared.request.timestamp)

    def retrieve_results(self, executed: ExecutedRun) -> SimulationResult:
        report = self._run_impact(executed.prepared.request)
        return SimulationResult(
            executed=executed,
            raw_output={"impact_report": report},
            confidence=0.9,
        )

    def map_results(self, result: SimulationResult, service: RuntimeService
                    ) -> MappedResult:
        report: ImpactReport = result.raw_output["impact_report"]
        return MappedResult(
            scenario_id=result.executed.prepared.request.scenario_id,
            added_entities=list(report.delta.added_entities),
            removed_entities=list(report.delta.removed_entities),
            modified_entities=list(report.delta.modified_entities),
            impacts=[i.as_dict() for i in report.impacts[:5]],
            assumptions=list(result.executed.prepared.request.assumptions),
            engine=self.engine,
            engine_version=self.engine_version,
        )

    def _run_impact(self, request: SimulationRequest) -> ImpactReport:
        yaml_path = self.scenarios.get(request.scenario_id)
        if not yaml_path:
            raise SimulationError(
                f"no scenario file registered for {request.scenario_id!r}")
        scenario = load_scenario(yaml_path)
        scenario.baseline = request.baseline_id
        scenario.transition(ScenarioStatus.DEFINED)
        baseline = ScenarioEngine().create_baseline(
            self.service.store, request.baseline_id, "Adapter Baseline")
        return ImpactEngine().evaluate(scenario, baseline)


class SimulationRegistry:
    """CR-10AG — registry of available adapters."""

    def __init__(self):
        self._adapters: Dict[str, SimulationAdapter] = {}

    def register(self, adapter: SimulationAdapter) -> None:
        self._adapters[adapter.engine] = adapter

    def engine_for(self, engine: str) -> SimulationAdapter:
        adapter = self._adapters.get(engine)
        if adapter is None:
            raise SimulationError(
                f"no adapter registered for engine {engine!r}")
        return adapter

    def capabilities(self) -> List[str]:
        return sorted(self._adapters.keys())
