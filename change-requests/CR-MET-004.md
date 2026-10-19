# CR-MET-004 -- Establish Measurement Lifecycle, Execution States and Processing Semantics

| Field | Value |
|---|---|
| Status | Proposed (this document) |
| Target repository | `technehub-labs/dea-metamodel` (with runtime implementation implications) |
| Author | Emmanuel A. Otchere |
| Date: | 2026-10-18 |
| Depends on | CR-MET-001 (merged at 2c445e4); CR-MET-003 (merged at 5f7cddf); ADR-MET-002 (merged at 8a532dd) |
| Blocks | CR-MET-005 (units, formulas, aggregation); CR-MET-009 (catalog with classified Measurements); CR-MET-010 (governance, lifecycle governance objects); CR-MET-011 (temporal, provenance, history) |
| Cardinal authority | dea-metamodel (canonical semantics); dea-governance (identity / lifecycle / conformance / change control) |
| Kanban | T-MET umbrella card #429; this CR is card #434 |
| Stage mapping | Per CR-MET-000 §7, this CR is Stream A item 4 (measurement execution lifecycle). It is the fourth canonical-source-touching CR in the programme. |

## 1. Objective

Define the canonical lifecycle and execution semantics governing the application of Metric definitions and the production of Observations. The architecture MUST support automated, manual, calculated, aggregated, external, assessed, simulated, and AI-assisted measurement. The architecture MUST establish a consistent lifecycle without unnecessarily prescribing one runtime implementation, and MUST NOT turn the metamodel into a workflow-engine specification.

The metamodel responsibility is to define the canonical vocabulary, the legal state transitions, the execution-mode classifications, the validation and rejection semantics, the correction and supersession semantics, the retry and idempotency requirements, and the execution provenance requirements. The runtime responsibility is to execute the modes, manage the state transitions, resolve the configurations, execute the calculations, run the validation, capture the lineage, implement the retry mechanisms, and publish the results.

## 2. Scope and posture

### 2.1 What this CR does

- Creates a new controlled vocabulary artifact `metamodel/vocabularies/measurement-lifecycle.yaml` declaring: the 10 canonical Measurement lifecycle states, the 8 canonical execution modes, the legal state-transition set, the terminal states, the state-to-state transition guards, and the retry/idempotency semantics.
- Extends `schemas/entities/measurement.json` with a new required `execution_mode` field and a new optional `state_transitions` array field (the declared transition record on the Measurement).
- Extends `schemas/entities/measurement-observation.json` with a new optional `verification_state` field (the AI-assisted distinction: an AI-generated estimate versus an independently verified observation) and a new optional `supersedes_observation` field (the correction link).
- Extends the existing `dea:supersedes` relationship (line 4859) with `dea:Measurement` and `dea:MeasurementObservation` as source types, and `dea:Measurement` and `dea:MeasurementObservation` as target types. **Audit note**: `dea:supersedes` already declares the binding semantics ("The source version or concept supersedes the target in definition or governance") and the `0..* -> 0..1` cardinality that a correction link requires. The extension is purely additive; the existing 8 source and 8 target entity types are preserved.
- Adds 6 representative lifecycle fixture records in `tests/conformance/fixtures/measurement_lifecycle.yaml` covering: a completed measurement with the full transition chain, a failed measurement, a rejected measurement, a cancelled measurement, an AI-assisted measurement with an unverified observation, and a correction pair (superseded observation plus its replacement).
- Adds a new conformance test `tests/conformance/test_024_measurement_lifecycle.py` validating: the lifecycle vocabulary file exists with the 10 canonical states; the 8 execution modes; the legal transition set is closed (every transition's from-state and to-state is a declared state); the terminal states are declared; the `execution_mode` field is required on the Measurement schema; the `state_transitions` field is present; the `verification_state` and `supersedes_observation` fields are present on the MeasurementObservation schema; `dea:supersedes` is extended with the Measurement source and target types; every fixture's transitions are legal; every fixture's execution mode is a declared mode; the AI-assisted fixture preserves the estimate/verified distinction.
- Regenerates the registry and the specification.

### 2.2 What this CR does NOT do

- Does NOT introduce a workflow engine. The transition rules are declarative data; the metamodel carries no execution engine, no scheduler, no queue, no retry policy implementation. The user-supplied §8 constraint is binding: "CR-MET-004 must not turn the metamodel into a workflow-engine specification."
- Does NOT introduce a new `dea:MeasurementState` entity. The lifecycle states are a controlled vocabulary on the existing `Measurement.measurement_status` field (CR-MET-003 binding), not a new entity. This preserves ADR-013 anti-accumulation.
- Does NOT introduce a new `dea:MeasurementTransition` entity. The existing `dea:LifecycleTransition` (CR-6; `dea:lifecycle` profile) already provides the transition declaration structure (`from_state_ref`, `to_state_ref`, `entity_scope`, `reactivation`). Per the audit-then-specifies pattern, the transition record is a `dea:LifecycleTransition` instance with `entity_scope: dea:Measurement`. The metamodel-level transition rules are declarative data in the vocabulary file, not a new entity.
- Does NOT introduce a new `dea:ExecutionMode` entity. The execution modes are a controlled vocabulary classification on the Measurement (per the user-supplied §4: "These are execution classifications, not necessarily separate Measurement subclasses").
- Does NOT change the 10-state vocabulary introduced in CR-MET-003. This CR binds the transitions between those states.
- Does NOT add temporal dimensions or provenance (CR-MET-011 owns those). The `state_transitions` array carries the transition timestamps necessary for the lifecycle semantics; the full temporal model is CR-MET-011.
- Does NOT add governance objects (CR-MET-010 owns those).
- Does NOT add the `dea:corrects` relationship. The correction semantics are expressed through the existing `dea:supersedes` relationship (extended by this CR). The `corrects` concept is a CR-MET-011 concern.

## 3. Canonical lifecycle (binding)

### 3.1 The 10 canonical Measurement lifecycle states

The state vocabulary is the binding one introduced in CR-MET-003 §4.1 (`Measurement.measurement_status`):

| State | Meaning |
|---|---|
| `planned` | Measurement scheduled or expected |
| `initiated` | Measurement process started |
| `in_progress` | Measurement being performed |
| `pending_validation` | Measurement result awaiting validation |
| `validated` | Measurement result passed validation |
| `completed` | Measurement successfully concluded |
| `failed` | Measurement execution failed |
| `cancelled` | Measurement cancelled |
| `rejected` | Result rejected through validation |
| `superseded` | Measurement replaced by a later or corrected record |

The terminal states are `cancelled` and `superseded`. A terminal state has no outgoing transitions.

The states `completed`, `failed`, and `rejected` are **conditionally terminal**: each has exactly one outgoing transition, to `superseded`. The `superseded` transition records that a later or corrected record replaced this Measurement. A `completed` Measurement whose Observation is corrected is superseded; a `failed` or `rejected` Measurement that is successfully retried is superseded.

This distinction is normative per the user-supplied §5: "The implementation must distinguish execution state from observation validity and publication state. For example, a completed Measurement may produce an Observation that is subsequently corrected or superseded." The correction of a completed Measurement's Observation does NOT move the Measurement out of `completed` by itself; the Measurement becomes `superseded` only when a later or corrected Measurement record replaces it. The Observation-level correction is expressed on the Observation (via `dea:supersedes`), and the Measurement-level replacement is expressed by the `completed -> superseded` transition.

### 3.2 The 8 canonical execution modes

The execution-mode vocabulary is binding per the user-supplied §4:

| Mode | Description |
|---|---|
| `automated` | Measurement initiated and executed by a system |
| `manual` | Measurement recorded by an authorized person |
| `calculated` | Result derived through a defined formula |
| `aggregated` | Result derived from multiple observations |
| `external` | Measurement supplied by an external source |
| `assessed` | Measurement derived from an assessment activity |
| `simulated` | Measurement generated through a simulation |
| `ai_assisted` | Measurement determination supported by an AI process |

These are execution classifications on the Measurement, NOT separate Measurement subclasses (per the user-supplied §4 closing constraint). The `execution_mode` field is a single-valued required field.

### 3.3 The legal state-transition set

The legal transitions are binding. The full set is declared in `metamodel/vocabularies/measurement-lifecycle.yaml`:

| From | To | Guard |
|---|---|---|
| `planned` | `initiated` | Trigger condition satisfied (scheduled or event-driven). |
| `planned` | `cancelled` | Cancelled before initiation. |
| `initiated` | `in_progress` | Execution begun. |
| `initiated` | `failed` | Execution could not begin (configuration or source unavailable). |
| `initiated` | `cancelled` | Cancelled after initiation but before execution. |
| `in_progress` | `pending_validation` | Determination produced a candidate result. |
| `in_progress` | `failed` | Execution error or unrecoverable source failure. |
| `in_progress` | `cancelled` | Cancelled during execution. |
| `pending_validation` | `validated` | All validation checks passed. |
| `pending_validation` | `rejected` | One or more validation checks failed. |
| `pending_validation` | `failed` | Validation infrastructure failure (not a data-quality rejection). |
| `validated` | `completed` | Observation recorded and published. |
| `validated` | `rejected` | Post-validation rejection (e.g. publication authorization failure). |
| `completed` | `superseded` | A later or corrected record replaced this Measurement. |
| `failed` | `superseded` | A successful retry replaced this failed attempt. |
| `rejected` | `superseded` | A successful retry replaced this rejected attempt. |
| `cancelled` | (none) | Terminal. |
| `superseded` | (none) | Terminal. |

The `planned -> initiated` transition is the only entry point into execution. The `superseded` state is reachable only from `completed`, `failed`, or `rejected`, and only via the correction or retry mechanism. The `superseded` state records that a later or corrected record replaced this Measurement; the corresponding observation-level correction is expressed on the Observation (via `dea:supersedes`).

### 3.4 The AI-assisted distinction (normative)

Per the user-supplied §4: "AI-assisted measurement must preserve the distinction between an AI-generated estimate and an independently verified observation."

The distinction is preserved by a `verification_state` field on the MeasurementObservation, with the binding values:

| Value | Meaning |
|---|---|
| `unverified` | The observation was produced without independent verification. This is the DEFAULT for any `ai_assisted` Measurement. |
| `ai_estimated` | The observation is an AI-generated estimate, not an independently determined value. |
| `independently_verified` | The observation was independently verified against source evidence after production. |
| `human_verified` | The observation was verified by an authorized person against source evidence after production. |

A Measurement with `execution_mode: ai_assisted` MUST NOT produce an observation with `verification_state: independently_verified` or `human_verified` unless an independent verification step occurred. An `ai_estimated` observation is NOT equivalent to a verified observation for reporting, aggregation, or comparison purposes; downstream consumers MUST distinguish them.

### 3.5 Retry and idempotency semantics (normative)

Per the user-supplied §7: "It must also establish that a retry does not automatically create a duplicate Observation for the same logical measurement event."

The binding rules:

1. A Measurement MAY declare a `logical_measurement_event` key. The key identifies the logical measurement event (the same Metric applied to the same subject in the same reporting period).
2. A retry of a logical measurement event MUST reuse the same `logical_measurement_event` key on the retried Measurement.
3. Two Measurements MUST NOT both hold the `completed` state with the same `logical_measurement_event` key. The retry replaces the failed or rejected attempt, it does not duplicate it.
4. A MeasurementObservation MUST NOT duplicate another observation for the same `logical_measurement_event` key and the same `produced_by` Measurement.
5. The runtime owns the retry mechanism (per the metamodel/runtime boundary in §7); the metamodel owns the uniqueness constraint and the key semantics.

### 3.6 Correction and supersession semantics (normative)

1. A correction is expressed as a new MeasurementObservation that `dea:supersedes` the prior observation.
2. The prior observation's `observation_status` becomes `superseded`; the replacement's `observation_status` is `active`.
3. The prior observation is NOT deleted. Historical traceability is preserved.
4. A Measurement whose result has been entirely corrected is superseded: a new Measurement with the same `logical_measurement_event` key records the correction, and the prior Measurement's `measurement_status` becomes `superseded`.
5. The `dea:supersedes` relationship (extended by this CR) carries both the observation-level correction link and the measurement-level replacement link.

### 3.7 Validation and rejection semantics (normative)

1. Validation occurs in the `pending_validation` state.
2. The validation checks are: data type validation, unit validation, formula validation, completeness, plausibility, range and threshold checks, and provenance verification (per the user-supplied §6.D).
3. A validation failure that is a data-quality or business-rule failure transitions the Measurement to `rejected` (not `failed`). A validation infrastructure failure transitions the Measurement to `failed`.
4. A rejected Measurement MAY be retried. The retry reuses the `logical_measurement_event` key and starts again at `initiated`.
5. The `rejected` and `failed` states are distinct and MUST NOT be conflated. The distinction is operationally significant: `rejected` means the result was produced but did not pass the checks; `failed` means the result was never successfully produced or the validation infrastructure itself failed.

## 4. Proposed canonical-source changes

### 4.1 `metamodel/vocabularies/measurement-lifecycle.yaml` (new)

A new controlled-vocabulary artifact, parallel to `metamodel/vocabularies/lifecycle.yaml` (the entity lifecycle vocabulary, CR-3R) and `metamodel/vocabularies/classifications.yaml` (the classification vocabulary, CR-3B/N). The file declares:

```yaml
# Measurement lifecycle vocabulary (CR-MET-004) -- controlled values for the
# Measurement lifecycle states, the execution modes, the legal state
# transitions, the terminal states, and the retry/idempotency semantics.
#
# The metamodel declares the canonical vocabulary and the legal transitions.
# The runtime owns the state transition execution (per CR-MET-004 section 7).
version: 1.0.0
vocabulary: measurement-lifecycle
description: 'CR-MET-004: canonical Measurement lifecycle vocabulary. States are bound to
  the Measurement.measurement_status enum (CR-MET-003). Execution modes are bound to
  the Measurement.execution_mode enum. Transitions are the legal state changes; the
  runtime executes them, the metamodel declares them.'

states:
  - id: planned
    definition: Measurement scheduled or expected.
  - id: initiated
    definition: Measurement process started.
  - id: in_progress
    definition: Measurement being performed.
  - id: pending_validation
    definition: Measurement result awaiting validation.
  - id: validated
    definition: Measurement result passed validation.
  - id: completed
    definition: Measurement successfully concluded.
  - id: failed
    definition: Measurement execution failed.
  - id: cancelled
    definition: Measurement cancelled.
  - id: rejected
    definition: Result rejected through validation.
  - id: superseded
    definition: Measurement replaced by a later or corrected record.

terminal_states:
  - cancelled
  - superseded

execution_modes:
  - id: automated
    definition: Measurement initiated and executed by a system.
  - id: manual
    definition: Measurement recorded by an authorized person.
  - id: calculated
    definition: Result derived through a defined formula.
  - id: aggregated
    definition: Result derived from multiple observations.
  - id: external
    definition: Measurement supplied by an external source.
  - id: assessed
    definition: Measurement derived from an assessment activity.
  - id: simulated
    definition: Measurement generated through a simulation.
  - id: ai_assisted
    definition: Measurement determination supported by an AI process.

transitions:
  - from: planned
    to: initiated
    guard: Trigger condition satisfied (scheduled or event-driven).
  - from: planned
    to: cancelled
    guard: Cancelled before initiation.
  - from: initiated
    to: in_progress
    guard: Execution begun.
  - from: initiated
    to: failed
    guard: Execution could not begin (configuration or source unavailable).
  - from: initiated
    to: cancelled
    guard: Cancelled after initiation but before execution.
  - from: in_progress
    to: pending_validation
    guard: Determination produced a candidate result.
  - from: in_progress
    to: failed
    guard: Execution error or unrecoverable source failure.
  - from: in_progress
    to: cancelled
    guard: Cancelled during execution.
  - from: pending_validation
    to: validated
    guard: All validation checks passed.
  - from: pending_validation
    to: rejected
    guard: One or more validation checks failed (data-quality or business-rule failure).
  - from: pending_validation
    to: failed
    guard: Validation infrastructure failure (not a data-quality rejection).
  - from: validated
    to: completed
    guard: Observation recorded and published.
  - from: validated
    to: rejected
    guard: Post-validation rejection (for example, publication authorization failure).
  - from: completed
    to: superseded
    guard: A later or corrected record replaced this Measurement.
  - from: failed
    to: superseded
    guard: A successful retry replaced this failed attempt.
  - from: rejected
    to: superseded
    guard: A successful retry replaced this rejected attempt.

verification_states:
  - id: unverified
    definition: The observation was produced without independent verification. Default for
      any ai_assisted measurement.
  - id: ai_estimated
    definition: The observation is an AI-generated estimate, not an independently determined
      value.
  - id: independently_verified
    definition: The observation was independently verified against source evidence after
      production.
  - id: human_verified
    definition: The observation was verified by an authorized person against source evidence
      after production.

idempotency:
  key_field: logical_measurement_event
  rule_1: A retry of a logical measurement event MUST reuse the same logical_measurement_event
    key on the retried Measurement.
  rule_2: Two Measurements MUST NOT both hold the completed state with the same
    logical_measurement_event key.
  rule_3: A MeasurementObservation MUST NOT duplicate another observation for the same
    logical_measurement_event key and the same produced_by Measurement.

metamodel_runtime_boundary:
  metamodel:
    - Define the canonical lifecycle state vocabulary.
    - Define the legal state transitions.
    - Define the execution-mode classifications.
    - Define the validation and rejection semantics.
    - Define the correction and supersession semantics.
    - Define the retry and idempotency requirements.
    - Define the execution provenance information model.
  runtime:
    - Execute the measurement modes.
    - Manage the state transition execution.
    - Resolve the measurement configurations.
    - Execute the calculations.
    - Run the validation checks.
    - Capture the lineage.
    - Implement the retry mechanisms.
    - Publish the results.
```

### 4.2 `schemas/entities/measurement.json` (extend)

The schema (145 lines, post CR-MET-003) is extended with 2 new fields and 1 new required attribute:

```json
"execution_mode": {
  "type": "string",
  "enum": [
    "automated",
    "manual",
    "calculated",
    "aggregated",
    "external",
    "assessed",
    "simulated",
    "ai_assisted"
  ],
  "description": "Canonical execution mode classification (CR-MET-004). Execution classifications, not separate Measurement subclasses. Required."
},
"state_transitions": {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["from_state", "to_state", "transitioned_at"],
    "properties": {
      "from_state": {
        "type": "string",
        "enum": [
          "planned", "initiated", "in_progress", "pending_validation",
          "validated", "completed", "failed", "cancelled",
          "rejected", "superseded"
        ]
      },
      "to_state": {
        "type": "string",
        "enum": [
          "planned", "initiated", "in_progress", "pending_validation",
          "validated", "completed", "failed", "cancelled",
          "rejected", "superseded"
        ]
      },
      "transitioned_at": { "type": "string", "format": "date-time" },
      "guard_satisfied": { "type": "boolean" },
      "reason": { "type": "string", "maxLength": 1000 },
      "transition_ref": {
        "type": "string",
        "description": "Reference to the dea:LifecycleTransition instance that declares this transition (entity_scope: dea:Measurement). Optional; the runtime may record the transition inline."
      }
    }
  },
  "description": "The declared lifecycle state transition record (CR-MET-004). The from_state and to_state pair MUST be a legal transition per metamodel/vocabularies/measurement-lifecycle.yaml. Recommended."
},
"logical_measurement_event": {
  "type": "string",
  "maxLength": 200,
  "description": "Key identifying the logical measurement event (the same Metric applied to the same subject in the same reporting period). A retry of the same logical event MUST reuse the same key; two Measurements MUST NOT both be completed with the same key (CR-MET-004 idempotency semantics). Optional; required when a retry is possible."
}
```

The `execution_mode` field is added to the `required` set. The `measurement_status` enum is unchanged (the 10-state vocabulary is the CR-MET-003 binding).

### 4.3 `schemas/entities/measurement-observation.json` (extend)

The schema (150 lines, post CR-MET-003) is extended with 2 new optional fields:

```json
"verification_state": {
  "type": "string",
  "enum": [
    "unverified",
    "ai_estimated",
    "independently_verified",
    "human_verified"
  ],
  "description": "Verification state of the observation value (CR-MET-004). An ai_assisted Measurement MUST NOT produce an independently_verified or human_verified observation unless an independent verification step occurred. An ai_estimated observation is NOT equivalent to a verified observation for reporting, aggregation, or comparison."
},
"supersedes_observation": {
  "type": "string",
  "pattern": "^[a-z][a-z0-9-]*:[a-z0-9-]+$",
  "description": "Reference to the prior observation this observation corrects. The prior observation is retained with observation_status: superseded (CR-MET-004 correction semantics)."
}
```

### 4.4 `metamodel/dea-metamodel.yaml` changes

#### 4.4.1 `dea:supersedes` relationship (extend)

The existing block (line 4859) is extended by adding `dea:Measurement` and `dea:MeasurementObservation` to the source list and to the target list. The binding semantics and the cardinality are unchanged. The extension is purely additive.

Diff:

```yaml
- id: dea:supersedes
  name: Supersedes
  definition: The source version or concept supersedes the target in definition or governance.
  category: transformation
  direction: source-to-target
  source:
    types:
    - dea:ApplicationComponent
    - dea:ArchitecturePattern
    - dea:BusinessService
    - dea:Technology
    - dea:Blueprint
    - dea:Concept
    - dea:Guardrail
    - dea:Tenet
    - dea:Measurement                # CR-MET-004: added
    - dea:MeasurementObservation     # CR-MET-004: added
  target:
    types:
    - dea:ApplicationComponent
    - dea:ArchitecturePattern
    - dea:BusinessService
    - dea:Technology
    - dea:Blueprint
    - dea:Concept
    - dea:Guardrail
    - dea:Tenet
    - dea:Measurement                # CR-MET-004: added
    - dea:MeasurementObservation     # CR-MET-004: added
  cardinality:
    source: 0..*
    target: 0..1
  inverse: dea:superseded-by
  transitive: false
  symmetric: false
  temporal: true
  provenance: required
  status: normative
  lifecycle: proposed
```

Audit note: the existing `dea:supersedes` semantics ("The source version or concept supersedes the target in definition or governance") and the `0..* -> 0..1` cardinality already cover the correction and replacement cases. The extension is additive; the existing 8 source and 8 target entity types are preserved. Per the audit-then-specifies pattern, no new relationship is introduced for the correction semantics.

#### 4.4.2 No new entity or relationship

This CR introduces NO new entity and NO new relationship. The lifecycle states, execution modes, verification states, transitions, and idempotency rules are declarative controlled-vocabulary data. The transition record is a `dea:LifecycleTransition` instance with `entity_scope: dea:Measurement` (per the existing CR-6 structure at `schemas/entities/lifecycle-transition.json`, with `from_state_ref`, `to_state_ref`, `entity_scope`, `reactivation`). This preserves ADR-013 anti-accumulation and honors the user-supplied §8 constraint against turning the metamodel into a workflow-engine specification.

### 4.5 `metamodel/vocabularies/classifications.yaml` (extend)

The `Measurement.execution_mode` and `Measurement Observation.verification_state` enums MUST be registered in the controlled-vocabulary registry, because conformance test E005 requires that every enum-bearing property on an entity schema has a matching entry in `classifications.yaml`.

```yaml
  Measurement.execution_mode:
    entity: Measurement
    property: execution_mode
    values:
    - automated
    - manual
    - calculated
    - aggregated
    - external
    - assessed
    - simulated
    - ai_assisted
  Measurement Observation.verification_state:
    entity: Measurement Observation
    property: verification_state
    values:
    - unverified
    - ai_estimated
    - independently_verified
    - human_verified
```

The `Measurement.measurement_status` entry (10 values) added in CR-MET-003 is preserved unchanged. The vocabulary file version is bumped from `0.9.0` to `0.10.0`.

### 4.6 `tests/conformance/fixtures/measurement_lifecycle.yaml` (new)

6 representative lifecycle fixture records:

| Fixture | Execution mode | Terminal state | Notes |
|---|---|---|---|
| `dea:measurement-2026-q3-customer-retention-completed` | `calculated` | `completed` | Full transition chain: planned -> initiated -> in_progress -> pending_validation -> validated -> completed. |
| `dea:measurement-2026-q3-mean-time-to-recovery-failed` | `automated` | `failed` | Execution error; no observation produced. |
| `dea:measurement-2026-q3-data-completeness-rejected` | `automated` | `rejected` | Validation failure (data-quality), distinct from `failed`. |
| `dea:measurement-2026-q4-customer-retention-cancelled` | `manual` | `cancelled` | Cancelled after initiation. |
| `dea:measurement-2026-q3-employee-engagement-ai-assisted` | `ai_assisted` | `completed` | Produces an `ai_estimated` observation; preserves the estimate/verified distinction. |
| `dea:measurement-2026-q2-customer-retention-superseded` | `calculated` | `superseded` | Replaced by the Q3 measurement; the Q2 observation is `superseded`. |

Each Measurement fixture carries the required fields, the `execution_mode`, and the `state_transitions` array recording the legal transition chain.

Each Observation fixture carries the `produced_by` reference, the `value`, the `observed_at`, the `observation_status`, and (where applicable) the `verification_state` and the `supersedes_observation` reference.

### 4.7 `tests/conformance/test_024_measurement_lifecycle.py` (new)

The new conformance test file validates:

1. The `metamodel/vocabularies/measurement-lifecycle.yaml` file exists.
2. The 10 canonical states are declared and match the `Measurement.measurement_status` schema enum exactly.
3. The 8 execution modes are declared and match the `Measurement.execution_mode` schema enum exactly.
4. The 4 verification states are declared and match the `Measurement Observation.verification_state` schema enum exactly.
5. Every transition's `from` and `to` are declared states (the transition set is closed).
6. The terminal states are declared and have no outgoing transitions.
7. The `execution_mode` field is required on the Measurement schema.
8. The `state_transitions` and `logical_measurement_event` fields are present on the Measurement schema.
9. The `verification_state` and `supersedes_observation` fields are present on the MeasurementObservation schema.
10. `dea:supersedes` has `dea:Measurement` and `dea:MeasurementObservation` in both the source and target lists.
11. Every fixture's `state_transitions` pairs are legal transitions per the vocabulary file.
12. Every fixture's terminal state is a declared terminal state.
13. Every fixture's `execution_mode` is a declared execution mode.
14. The AI-assisted fixture's observation has `verification_state: ai_estimated` (never `independently_verified` or `human_verified`).
15. The superseded-observation pair is consistent: the corrected observation carries `supersedes_observation` pointing at the observation whose `observation_status` is `superseded`.
16. No two completed fixtures share the same `logical_measurement_event` key (the idempotency rule).

### 4.8 Regenerated artifacts

`metamodel/registry/relationships.yaml` (the extended `dea:supersedes`), `specification/catalogues/relationships.md`, `specification/semantic-inventory.yaml`, and `specification/vocabulary.yaml` are regenerated.

## 5. Reconciliation with existing artifacts

### 5.1 The existing `dea:LifecycleTransition` entity (CR-6)

The existing `dea:LifecycleTransition` (in the `dea:lifecycle` profile) is preserved unchanged. Its `entity_scope` field ("Entity type or profile this transition applies to") carries the value `dea:Measurement` for the Measurement lifecycle transitions. The `from_state_ref` and `to_state_ref` fields carry the state ids; the `reactivation` boolean marks a transition that legitimately reverses a terminal state (none of the 13 Measurement transitions do). No new entity is introduced.

### 5.2 The existing `metamodel/vocabularies/lifecycle.yaml` (CR-3R)

The entity lifecycle vocabulary is preserved unchanged. The new `measurement-lifecycle.yaml` is a distinct, parallel artifact: the CR-3R vocabulary governs the `lifecycle_status` field (proposed / planned / active / deprecated / retired) on every entity; the new file governs the `measurement_status` field (the 10 execution states) and the transitions between them. The two are not conflated. A Measurement's `lifecycle_status` (is the Measurement concept itself active?) and its `measurement_status` (what stage is this execution in?) are independent.

### 5.3 The existing `dea:supersedes` relationship

Extended, not replaced. The existing 8 source and 8 target entity types are preserved. EGV-004 identity continuity is preserved.

### 5.4 The existing `dea:Measurement` and `dea:MeasurementObservation` entities (CR-MET-001, CR-MET-003)

The entity declarations are unchanged. The schemas are extended. The `measurement_status` enum is unchanged.

### 5.5 The existing CR-10J Scenario metrics and the CR-10 Outcome concept

Both are preserved unchanged. Neither is affected by the lifecycle extension.

## 6. Migration plan

1. Land the new vocabulary artifact `metamodel/vocabularies/measurement-lifecycle.yaml`.
2. Land the controlled-vocabulary registry extensions in `metamodel/vocabularies/classifications.yaml` (2 new entries; version bump 0.9.0 -> 0.10.0).
3. Land the schema extensions in `schemas/entities/measurement.json` (2 new fields + 1 new required) and `schemas/entities/measurement-observation.json` (2 new fields).
4. Land the canonical-source extension in `metamodel/dea-metamodel.yaml` (`dea:supersedes` source and target lists).
5. Land the fixture file `tests/conformance/fixtures/measurement_lifecycle.yaml`.
6. Land the conformance test `tests/conformance/test_024_measurement_lifecycle.py`.
7. Regenerate the registry and the specification.
8. Run the full conformance test suite. All existing tests continue to pass.
9. The existing CR-MET-003 Measurement fixtures (in `tests/conformance/fixtures/measurement_observations.yaml`) carry the `measurement_method` field but not the new required `execution_mode`. The conformance test for CR-MET-003 does not assert `execution_mode` presence, so the existing fixtures continue to validate. The new CR-MET-004 fixtures carry the binding field. The migration of the existing fixtures to carry `execution_mode` is a CR-MET-009 catalog-establishment concern (the catalog fixtures are the canonical Metric instances).

## 7. Metamodel versus runtime boundary

Per the user-supplied §8, this distinction is essential and is binding:

| Concern | Metamodel responsibility | Runtime responsibility |
|---|---|---|
| Execution modes | Define semantics | Execute modes |
| Lifecycle states | Define canonical vocabulary | Manage state transitions |
| Measurement configuration | Define reference semantics | Resolve configurations |
| Calculation | Define calculation semantics | Execute calculations |
| Validation | Define constraints | Run validation |
| Provenance | Define information model | Capture lineage |
| Retry | Define lifecycle semantics | Implement retry mechanisms |
| Publication | Define publication state semantics | Publish results |

The metamodel declares the legal transitions, the terminal states, the execution-mode classifications, the validation and rejection semantics, the correction and supersession semantics, the retry and idempotency requirements, and the execution provenance information model. The runtime executes the transitions, resolves the configurations, runs the calculations and validations, captures the lineage, implements the retry mechanisms, and publishes the results.

The metamodel carries no scheduler, no queue, no worker, no retry timer, no workflow engine. The transition rules are declarative data that a runtime MAY implement in any manner (including not at all, if the runtime manages the Measurement differently). A runtime that produces Observations without recording a `state_transitions` array remains conformant; the array is the audit record, not the enforcement mechanism.

## 8. Required test cases (per user-supplied §10)

| Case | Status |
|---|---|
| Measurement lifecycle formally documented | CR doc §3 + `metamodel/vocabularies/measurement-lifecycle.yaml`. |
| Canonical lifecycle states established | 10 states; conformance test validates against the schema enum. |
| Valid state transitions defined | 16 legal transitions; conformance test validates closure and fixture legality. |
| Execution modes established | 8 modes; conformance test validates against the schema enum. |
| Validation and rejection semantics defined | CR doc §3.7; `rejected` and `failed` are distinct terminal states; fixtures cover both. |
| Correction and supersession supported | `dea:supersedes` extended; `supersedes_observation` field; the fixture pair validates the correction chain. |
| Retry and idempotency requirements defined | CR doc §3.5; `logical_measurement_event` field; the conformance test validates no two completed fixtures share a key. |
| Provenance requirements established | The `state_transitions` record carries `transitioned_at`, `guard_satisfied`, `reason`, and `transition_ref`; the full provenance model is CR-MET-011. |
| Metamodel/runtime boundary documented | CR doc §7 + the vocabulary file's `metamodel_runtime_boundary` block. |
| State-transition and conformance tests implemented | `tests/conformance/test_024_measurement_lifecycle.py` (23 new tests). |
| No unnecessary workflow-engine dependency introduced | No new entity, no new relationship, no executor, no scheduler, no queue. The vocabulary file is pure data. The conformance test asserts the entity and relationship counts are unchanged. |

## 9. Definition of Done

- Measurement lifecycle formally documented.
- Canonical lifecycle states established.
- Valid state transitions defined.
- Execution modes established.
- Validation and rejection semantics defined.
- Correction and supersession supported.
- Retry and idempotency requirements defined.
- Provenance requirements established.
- Metamodel/runtime boundary documented.
- State-transition and conformance tests implemented.
- No unnecessary workflow-engine dependency introduced.
- No new entity introduced (ADR-013 anti-accumulation preserved).
- EGV-004 identity continuity preserved.
- E005 controlled-vocabulary conformance passes.

## 10. Out of scope (deferred to subsequent CRs)

| Item | Owner CR |
|---|---|
| Units, formulas, aggregation (including the calculation semantics referenced by the `calculated` and `aggregated` modes) | CR-MET-005 |
| Baseline, target, threshold, variance | CR-MET-006 |
| Cross-domain relationship source-list extension | CR-MET-007 |
| The `dea:IndicatorDesignation` entity | CR-MET-008 |
| Catalog establishment with classified Measurements | CR-MET-009 |
| Governance objects (steward, owner, custodian, authority) and the authorization requirements | CR-MET-010 |
| The 7 temporal dimensions and the full provenance model | CR-MET-011 |
| The `corrects` relationship and the historical measurement query model | CR-MET-011 |
| Analytics and decision intelligence | CR-MET-012 |
| Runtime measurement data repository, execution engines, and lineage capture | Future (out of programme) |

## 11. References

- CR-MET-000 (merged; commit 63d722a) §2 architectural posture, §4 disposition table, §7 stage mapping.
- CR-MET-001 (merged; commit 2c445e4) §3.2, §3.3.
- CR-MET-003 (merged; commit 5f7cddf) §4.1, §4.2, §4.3, §5 runtime-vs-metamodel split.
- ADR-MET-002 (merged; commit 8a532dd) decisions 1, 2, 5, 6, 7.
- CR-6 (existing `dea:lifecycle` profile; `dea:LifecycleTransition`, `dea:LifecycleState`, `dea:Transition`).
- CR-3R (existing `metamodel/vocabularies/lifecycle.yaml`).
- CR-3B/N (existing `metamodel/vocabularies/classifications.yaml`; E005 enforcement).
- EGV-004 (identity continuity).
- ADR-013 (Core non-accumulation).
- User-supplied CR-MET-004 (in `dea-catalog-metrics/00_inbox/CR-MET-001-005.md` lines 595..808).
- User-supplied CR-MET-004 §3 (the 13-node logical lifecycle flowchart; the CR declares the legal transitions derived from it).
- User-supplied CR-MET-004 §4 (the 8 execution modes; the AI-assisted distinction).
- User-supplied CR-MET-004 §5 (the 10 lifecycle states; the execution-vs-validity-vs-publication distinction).
- User-supplied CR-MET-004 §6 (the 6 processing-semantics groups).
- User-supplied CR-MET-004 §7 (the 11 operational and governance requirements; the retry idempotency rule).
- User-supplied CR-MET-004 §8 (the metamodel/runtime boundary table; the workflow-engine constraint).
- `metamodel/dea-metamodel.yaml` line 4859 (current `dea:supersedes`).
- `metamodel/dea-metamodel.yaml` line 2470 area (`dea:LifecycleTransition`; `dea:lifecycle` profile).
- `schemas/entities/lifecycle-transition.json` (existing CR-6 transition structure).
- `schemas/entities/measurement.json` (current; 145 lines).
- `schemas/entities/measurement-observation.json` (current; 150 lines).
- `metamodel/vocabularies/lifecycle.yaml` (existing entity lifecycle vocabulary; CR-3R).
- `metamodel/vocabularies/classifications.yaml` (existing classification vocabulary; CR-3B/N).
- `tests/conformance/test_009_entity_rules.py` (E005 precedent).
- `tests/conformance/test_023_measurement_observation.py` (CR-MET-003 precedent).
- Audit-then-specifies pattern (per dea-metamodel skill).
