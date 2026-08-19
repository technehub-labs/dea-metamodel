"""CR-9.8 — agent runtime (CR-9AH…AR).

Provides the policy decision point (ALLOW / DENY / ESCALATE), the tool
registry with provides -> capability mapping, and the audit trail.

The runtime is the governance surface; it does not run an automated agent
loop. Inbound decisions are recorded as audit entries on the runtime graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from ..api import RuntimeService
from ..graph import EntityNotFoundError, GraphStore, Node


@dataclass(frozen=True)
class AuthorizationDecision:
    """CR-9AK: the result of a policy decision point."""

    agent_id: str
    action: str
    target: str
    effect: str  # ALLOW | DENY | ESCALATE
    policy_id: str = ""
    reason: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "agentId": self.agent_id,
            "action": self.action,
            "target": self.target,
            "effect": self.effect,
            "policyId": self.policy_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AuditEntry:
    """CR-9AM: one recorded decision."""

    id: str
    agent_id: str
    action: str
    target: str
    decision: AuthorizationDecision
    at: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "at": self.at,
            "agentId": self.agent_id,
            "action": self.action,
            "target": self.target,
            "decision": self.decision.as_dict(),
        }


@dataclass(frozen=True)
class ToolCapability:
    """CR-9AN: a capability a tool provides."""

    id: str
    description: str = ""


class AgentError(Exception):
    """Agent runtime invariant violated."""


class ToolRegistry:
    """CR-9AN: a semantic tool registry with provides -> capability mapping."""

    def __init__(self, service: RuntimeService):
        self.service = service
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._bindings: Dict[str, List[str]] = {}

    def register_tool(self, id: str, name: str,
                       provides_capabilities: Iterable[ToolCapability]):
        if id in self._tools:
            raise AgentError(f"tool {id!r} already registered")
        self._tools[id] = {
            "id": id, "name": name,
            "capabilities": {c.id: c for c in provides_capabilities},
        }

    def bind(self, agent_id: str, tool_id: str) -> None:
        self._bindings.setdefault(agent_id, []).append(tool_id)

    def tools_for_capability(self, capability_id: str) -> List[Dict[str, Any]]:
        return [tool for tool in self._tools.values()
                if capability_id in tool['capabilities']]

    def tools_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        return [self._tools[tid] for tid in self._bindings.get(agent_id, [])]


class AgentRuntime:
    """CR-9AH…AR — runtime governance surface for agents."""

    def __init__(self, service: RuntimeService,
                 tool_registry: Optional[ToolRegistry] = None):
        self.service = service
        self.tool_registry = tool_registry or ToolRegistry(service)
        self._audit: List[AuditEntry] = []

    def request_authorization(self, agent_id: str, action: str,
                             target: str) -> AuthorizationDecision:
        store = self.service.store
        if not store.has_entity(agent_id):
            raise AgentError(f"unknown agent {agent_id!r}")
        if not store.has_entity(target):
            decision = AuthorizationDecision(
                agent_id=agent_id, action=action, target=target,
                effect="DENY",
                reason=f"unknown target {target!r} — refusing to authorise "
                       "writes to missing entities")
            self._record(decision)
            return decision
        policy = self._find_policy(agent_id, action)
        if policy is None:
            decision = AuthorizationDecision(
                agent_id=agent_id, action=action, target=target,
                effect="DENY",
                reason="no matching policy — agents are read-only by default")
            self._record(decision)
            return decision
        effect = policy.properties.get("effect", "DENY")
        reason = self._reason(policy, agent_id, action)
        decision = AuthorizationDecision(
            agent_id=agent_id, action=action, target=target,
            effect=effect, policy_id=policy.id, reason=reason)
        self._record(decision)
        return decision

    def audit_log(self) -> List[AuditEntry]:
        return list(self._audit)

    def _find_policy(self, agent_id: str, action: str) -> Optional[Node]:
        agent = self.service.get_entity(agent_id)
        agent_role = agent.properties.get("role")
        for node in self.service.query(type="Policy"):
            if node.properties.get("action") != action:
                continue
            required_role = node.properties.get("actor_role")
            if required_role and required_role != agent_role:
                continue
            return node
        return None

    def _reason(self, policy: Node, agent_id: str, action: str) -> str:
        return (f"policy {policy.id!r} {policy.properties.get('effect', '')}"
                f" {action} for agent {agent_id}")

    def _record(self, decision: AuthorizationDecision) -> None:
        entry_id = f"audit.{len(self._audit) + 1}.{decision.agent_id}"
        entry = AuditEntry(
            id=entry_id,
            agent_id=decision.agent_id,
            action=decision.action,
            target=decision.target,
            decision=decision,
            at=datetime.now(timezone.utc).isoformat(),
        )
        self._audit.append(entry)
