"""CR-9.10b — interoperability end-to-end suite (CR-9CM)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List

from ..api import RuntimeService
from ..graph import Edge, InMemoryGraphStore, Node
from ..interoperability import (ExternalIdentifier, ExternalSystem,
                                InteropRegistry, SemanticMapping)
from ..model import load_model
from ..provenance import AssertionStatus, ProvenanceService

#: Repository root for fixture locations (interop scenarios resolve paths here).
REPO_ROOT = Path(__file__).resolve().parents[2]
from ..scenario import ScenarioEngine, ScenarioStatus, load_scenario
from ..scenario.impact import ImpactEngine
from .model import ConformanceClass, ConformanceSuite


@dataclass(frozen=True)
class InteropScenario:
    """A reusable cross-runtime interoperability scenario."""

    name: str
    description: str
    classes: List[ConformanceClass]
    run: Callable[["InteropRunContext"], Dict[str, Any]]


@dataclass
class InteropRunContext:
    """Shared fixtures available to every interop scenario."""

    store: InMemoryGraphStore
    service: RuntimeService
    provenance: ProvenanceService
    registry: InteropRegistry


def _canonical_registry() -> InteropRegistry:
    registry = InteropRegistry()
    registry.register_system(ExternalSystem(
        id="system.servicenow", name="ServiceNow CMDB", type="CMDB"))
    registry.register_system(ExternalSystem(
        id="system.leanix", name="LeanIX", type="EA_REPOSITORY"))
    registry.register_mapping(SemanticMapping(
        source_concept="external:archimate.ApplicationComponent",
        target_concept="opendea:ApplicationComponent"))
    return registry


def _new_context() -> InteropRunContext:
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    provenance = ProvenanceService(store)
    return InteropRunContext(
        store=store, service=service, provenance=provenance,
        registry=_canonical_registry())


def _scenario_external_id_correlation(ctx: InteropRunContext) -> Dict[str, Any]:
    ctx.service.create_entity("app.customer-platform",
                              "ApplicationComponent", "CS Platform")
    ctx.registry.link_external_identifier(ExternalIdentifier(
        system="system.servicenow", identifier="CI-001",
        entity="app.customer-platform"))
    resolved = ctx.registry.resolve("system.servicenow", "CI-001")
    return {
        "assertions": {"external_id_correlated": resolved == "app.customer-platform"},
        "metrics": {"external_id_count": 1},
    }


def _scenario_reasoning_materialization(ctx: InteropRunContext) -> Dict[str, Any]:
    ctx.service.create_entity("cap.cs", "BusinessCapability", "Capability")
    ctx.service.create_entity("obj.cs", "StrategicObjective", "Objective")
    ctx.service.create_relationship("cap.cs", "enables", "obj.cs", status="active")

    rule = Rule(
        id="DEA-INF-007", name="StrategicCapability",
        level=ReasoningLevel.DETERMINISTIC,
        applies_to=["BusinessCapability"],
        condition=lambda store: [
            RuleMatch(subject="cap.cs", claim={"classification": "strategic"},
                      derived_from=["cap.cs", "obj.cs"], confidence=0.96)])
    inference = ReasoningEngine().infer(rule, ctx.store)[0]
    assertion_id = ReasoningEngine().materialize(inference, ctx.provenance)
    assertion = ctx.provenance.assertions_for("cap.cs")[0]
    return {
        "assertions": {
            "inference_recorded": assertion.status == AssertionStatus.PROPOSED,
            "derived_from_present": assertion.derivation_rule == "DEA-INF-007",
        },
        "metrics": {"assertion_id": assertion_id},
    }


def _scenario_scenario_pipeline(ctx: InteropRunContext) -> Dict[str, Any]:
    load_model(REPO_ROOT / "models" / "scenarios" / "customer-service-baseline.yaml",
               ctx.store)
    engine = ScenarioEngine()
    baseline = engine.create_baseline(ctx.store, "baseline.interop", "Baseline")
    scenario = load_scenario(str(
        REPO_ROOT / "models" / "scenarios" / "customer-platform-replacement.yaml"))
    scenario.baseline = "baseline.interop"
    scenario.transition(ScenarioStatus.DEFINED)
    report = ImpactEngine().evaluate(scenario, baseline)
    return {
        "assertions": {
            "changed_application_a": "app.customer-platform" in report.delta.removed_entities,
            "added_platform_b": "platform.customer-v2" in report.delta.added_entities,
        },
        "metrics": {
            "delta_added_entities": len(report.delta.added_entities),
            "delta_removed_entities": len(report.delta.removed_entities),
        },
    }


INTEROP_SCENARIOS: List[InteropScenario] = [
    InteropScenario(
        name="external-id-correlation",
        description="Round-trip an external identifier through ExternalIdentifier "
                    "without adopting it as canonical identity (CR-11I).",
        classes=[ConformanceClass.PROVENANCE, ConformanceClass.SECURITY],
        run=_scenario_external_id_correlation),
    InteropScenario(
        name="reasoning-materialization",
        description="Reasoning engine explicit materialization lands as a "
                    "PROPOSED assertion via the provenance layer (CR-9Q/CQ).",
        classes=[ConformanceClass.VALIDATION, ConformanceClass.PROVENANCE],
        run=_scenario_reasoning_materialization),
    InteropScenario(
        name="scenario-impact-pipeline",
        description="End-to-end scenario pipeline: load baseline, simulate "
                    "delta, evaluate impact + architecture delta (CR-10G/H).",
        classes=[ConformanceClass.API, ConformanceClass.QUERY],
        run=_scenario_scenario_pipeline),
]


def run_interop_scenario(scenario: InteropScenario) -> Dict[str, Any]:
    """Run one named scenario against the canonical reference runtime."""
    context = _new_context()
    try:
        result = scenario.run(context)
    except Exception as exc:
        return {
            "scenario": scenario.name,
            "classes": [c.value for c in scenario.classes],
            "passed": False,
            "error": str(exc),
        }
    assertions = result.get("assertions", {})
    metrics = result.get("metrics", {})
    return {
        "scenario": scenario.name,
        "classes": [c.value for c in scenario.classes],
        "passed": all(assertions.values()) if assertions else False,
        "assertions": assertions,
        "metrics": metrics,
    }


def run_all_interop_scenarios() -> List[Dict[str, Any]]:
    return [run_interop_scenario(scenario) for scenario in INTEROP_SCENARIOS]


# ---- imports needed by the scenario bodies (avoids top-level cycles) ----
from ..reasoning import (ReasoningEngine, ReasoningLevel, Rule, RuleMatch)
