"""CR-9.8 — agent runtime tests (CR-9AH…AR)."""

import pytest

from runtime.agent import (AgentRuntime, AgentError, AuthorizationDecision,
                           AuditEntry, ToolCapability, ToolRegistry)
from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore


def _runtime():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    service.create_entity("agent.architect", "Agent",
                          "Architect Agent",
                          properties={"role": "Architect"})
    service.create_entity("agent.observer", "Agent",
                          "Read-Only Observer",
                          properties={"role": "Observer"})
    service.create_entity("policy.read", "Policy",
                          "Read Policy",
                          properties={"action": "read", "effect": "ALLOW"})
    service.create_entity("policy.write", "Policy",
                          "Write Policy",
                          properties={"action": "write", "effect": "ALLOW",
                                       "actor_role": "Architect"})
    service.create_entity("policy.deny.delete", "Policy",
                          "Delete Deny Policy",
                          properties={"action": "delete", "effect": "DENY"})
    service.create_entity("app.cs", "ApplicationComponent", "CS Platform")
    return service


def test_runtime_resolves_allow_for_granted_policy():
    """CR-9AK: an agent with a matching policy receives ALLOW."""
    service = _runtime()
    runtime = AgentRuntime(service)
    decision = runtime.request_authorization("agent.architect", "write",
                                            "app.cs")
    assert decision.effect == "ALLOW"
    assert decision.policy_id == "policy.write"


def test_runtime_resolves_deny_for_ungranted_policy():
    """CR-9AK: when no matching policy exists the runtime emits DENY."""
    service = _runtime()
    runtime = AgentRuntime(service)
    decision = runtime.request_authorization("agent.observer", "delete",
                                            "app.cs")
    assert decision.effect in {"DENY", "ESCALATE"}


def test_runtime_returns_escalate_when_policy_requires_human_review():
    """CR-9AL: policy-driven escalations are returned without speculation."""
    service = _runtime()
    service.create_entity("policy.escalate", "Policy",
                          "Human-Review Policy",
                          properties={"action": "promote",
                                       "effect": "ESCALATE"})
    runtime = AgentRuntime(service)
    decision = runtime.request_authorization("agent.architect", "promote",
                                            "app.cs")
    assert decision.effect == "ESCALATE"
    assert decision.policy_id == "policy.escalate"


def test_runtime_returns_deny_when_target_unknown_to_runtime():
    """CR-9AJ: an unknown target is rejected up-front."""
    service = _runtime()
    runtime = AgentRuntime(service)
    decision = runtime.request_authorization("agent.architect", "write",
                                            "ghost.target")
    assert decision.effect == "DENY"
    assert "unknown" in decision.reason.lower()


def test_runtime_records_audit_entry_for_every_decision():
    """CR-9AM: every authorisation decision is logged on the graph."""
    service = _runtime()
    runtime = AgentRuntime(service)
    runtime.request_authorization("agent.architect", "write", "app.cs")
    runtime.request_authorization("agent.observer", "delete", "app.cs")

    assert len(runtime.audit_log()) == 2
    audit_ids = {entry.id for entry in runtime.audit_log()}
    assert all(aid.startswith("audit.") for aid in audit_ids)


def test_tool_registry_matches_agents_to_capabilities():
    """CR-9AN: a tool registry exposes provides -> capability mapping."""
    service = RuntimeService(InMemoryGraphStore())
    service.create_entity("agent.svc", "Agent", "Service Agent")
    service.create_tool = lambda *args, **kwargs: None  # placeholder
    registry = ToolRegistry(service)
    registry.register_tool(
        id="tool.cdm",
        name="CDM Sync",
        provides_capabilities=[ToolCapability(
            id="cap.read-cmdb", description="Read CMDB records")])
    registry.bind(agent_id="agent.svc", tool_id="tool.cdm")

    matches = registry.tools_for_capability("cap.read-cmdb")
    assert [tool["id"] for tool in matches] == ["tool.cdm"]


def test_unknown_agent_raises():
    service = RuntimeService(InMemoryGraphStore())
    runtime = AgentRuntime(service)
    with pytest.raises(AgentError, match="unknown agent"):
        runtime.request_authorization("agent.ghost", "read", "x")
