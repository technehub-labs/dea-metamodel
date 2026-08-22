# Signal model (CR-012 §3.1–§3.2, Phase 1)

## What this document covers

The first-class `Signal` and `Observation` types that ship with CR-012
Phase 1. These are the foundational artifacts of the enterprise
intelligence layer; every later phase (patterns, loops, action
proposals) builds on them.

## The five-second summary

- An **Observation** is the raw, governed output of one reasoning cycle.
  Recorded evidence, never an inference (ADR-008).
- A **Signal** is the governed promotion of an Observation to
  *enterprise attention*. Carries classification, severity, confidence,
  owner, entities, rationale, status, audit chain.
- A Signal **must** be grounded in a registered Observation
  (`SignalStore` enforces the link).
- The lifecycle is a **directed graph**: `open → acknowledged → ... →
  resolved`. No skipping. Dismissed / resolved are terminal.
- A Signal of severity `critical` **must** carry an `escalation_policy_ref`.
- An `uncertain` confidence Signal is permitted only at severity `info`
  or `low`.
- The OpenDEA **core** is not extended. Signals live in their own
  profile (`metamodel/profiles/intelligence/`) and runtime package
  (`runtime/intelligence/`).

## Type reference

### Observation (CR-012 §3.1)

| Field | Type | Notes |
|---|---|---|
| `id` | `string` (canonical) | `obs.<entity>.<cycle>.kind` |
| `cycle_id` | `string` (canonical) | The IntelligenceLoop cycle that produced it |
| `subject` | `string` (canonical) | The single canonical entity observed |
| `kind` | `string` | MUST be `pattern-name@version` |
| `evidence` | `list[string]` (≥ 1) | The evidence chain |
| `confidence` | enum | `exact \| high \| medium \| low \| uncertain` |
| `scope` | `string` | The bounded scope of the reasoning cycle |
| `observed_at` | ISO 8601 | Wall-clock time the cycle completed |

An Observation is **frozen** (immutable). The reason: reasoning is the
producer; the runtime records; the Signal is the governed artifact that
moves forward. The immutability makes the audit chain deterministic.

### Signal (CR-012 §3.2)

| Field | Type | Notes |
|---|---|---|
| `id` | `string` (canonical) | `sig.<scope>.<classification>` |
| `observation_ref` | `string` (canonical) | MUST resolve in `SignalStore` |
| `classification` | enum (8) | See `classification.yaml` |
| `severity` | enum (5) | `info \| low \| medium \| high \| critical` |
| `confidence` | enum (5) | See `confidence.yaml` |
| `entities` | `list[string]` (≥ 1, canonical) | The affected canonical entities |
| `owner` | `string` (canonical Actor) | Governance owner (ADR-009) |
| `rationale` | `string` | Human-readable explanation |
| `proposed_action` | `string` (optional) | MUST NOT carry `approved: true` |
| `escalation_policy_ref` | `string` (canonical, optional) | REQUIRED when `severity == critical` |
| `status` | enum (6) | Lifecycle state (directed graph) |
| `raised_at` | ISO 8601 | Set at construction |
| `acknowledged_at` | ISO 8601 | Set on first `acknowledged` or `in_review` transition |
| `resolved_at` | ISO 8601 | Set on transition to `dismissed` or `resolved` |
| `history` | `list[{to, at, by}]` | Audit chain (append-only) |

### Lifecycle (CR-012 lifecycle.yaml)

```
open ──► acknowledged ──► in_review ──► accepted ──► dismissed / resolved
                       ╲                ╲              ▲
                        ╲────────────────────────────► ╯
                         (dismissed / resolved)
```

Terminal states reject further transitions. `dismissed` requires a
rationale. `resolved` is recorded with `resolved_at`. Every transition
appends to the signal's `history` (audit chain).

### Vocabularies (normative)

| Vocabulary | Members |
|---|---|
| Classification | `maturity_gap`, `compliance_drift`, `risk`, `capability_gap`, `federation_anomaly`, `mapping_staleness`, `agent_anomaly`, `observation_only` |
| Severity | `info`, `low`, `medium`, `high`, `critical` |
| Confidence | `exact`, `high`, `medium`, `low`, `uncertain` |
| Lifecycle | `open`, `acknowledged`, `in_review`, `accepted`, `dismissed`, `resolved` |

The `observation_only` classification is reserved for situations whose
semantics have not yet been formalised in the metamodel. Use of it
requires a follow-on CR before the signal can transition to `resolved`
(`observation_only` is a placeholder, not an end-state).

## What Phase 1 ships

- `metamodel/profiles/intelligence/profile.yaml` — profile declaration
- `metamodel/profiles/intelligence/signal.yaml` — Signal field schema
- `metamodel/profiles/intelligence/classification.yaml` — classification vocabulary
- `metamodel/profiles/intelligence/severity.yaml` — severity vocabulary
- `metamodel/profiles/intelligence/confidence.yaml` — confidence vocabulary
- `metamodel/profiles/intelligence/lifecycle.yaml` — lifecycle directed graph
- `metamodel/profiles/intelligence/observation.yaml` — Observation field schema
- `metamodel/profiles/intelligence/loop.yaml` — loop vocabulary (Phase 4 placeholder)
- `metamodel/profiles/intelligence/proposal.yaml` — proposal vocabulary (Phase 5 placeholder)
- `runtime/intelligence/__init__.py`
- `runtime/intelligence/signal.py` — Observation, Signal, vocabularies, lifecycle engine
- `runtime/intelligence/store.py` — SignalStore
- `tests/runtime/test_intelligence_phase1.py` — 31 tests
- `docs/adr/ADR-014-intelligence-loop-architecture.md`
- This document

## What Phase 1 does **not** ship (queued)

- The reasoning scheduler (Phase 4)
- The pattern library (Phase 3)
- The IntelligenceLoop runtime (Phase 4)
- ActionProposal lifecycle (Phase 5)
- Authority / routing policies (Phase 6)
- Conformance class (Phase 7)
- Golden fixtures and conformance suite (Phase 7)

## How to read the audit chain

A Signal's `history` field is append-only:

```python
from runtime.intelligence import Signal

sig = Signal(
    id="sig.x",
    observation_ref="obs.x",
    classification=SignalClassification.MATURITY_GAP,
    severity=SignalSeverity.MEDIUM,
    confidence=SignalConfidence.HIGH,
    entities=["cap.x"],
    owner="actor.ea",
)
sig.transition(SignalLifecycleStatus.ACKNOWLEDGED, by="actor.ea")
sig.transition(SignalLifecycleStatus.IN_REVIEW, by="actor.ea")

for entry in sig.history:
    print(entry)
# {'to': 'open', 'at': '...', 'by': ''}
# {'to': 'acknowledged', 'at': '...', 'by': 'actor.ea'}
# {'to': 'in_review', 'at': '...', 'by': 'actor.ea'}
```

This is the single primitive that ties Observation → Signal →
ActionProposal → execution together in CR-012 Phase 5.

## Cross-references

- CR-012 §3.1, §3.2, §3.5, §6
- `metamodel/profiles/intelligence/` — normative vocabulary source
- ADR-002 — Core vs Profiles
- ADR-007 — Runtime / API separation
- ADR-008 — Inference vs authoritative knowledge
- ADR-009 — Agent authorization model
- ADR-014 — Intelligence loop architecture