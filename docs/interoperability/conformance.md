# Conformance (CR-11AM / AN / AO + CR-11BF / BG / BH)

> **KB note — what a conformant OpenDEA product, runtime or integration
> looks like in CR-11, the six classes the conformance suite tests, and
> the reference integration strategy that orders how OpenDEA reaches
> the ecosystem.** Companion to [overview.md](overview.md),
> [architecture.md](architecture.md), [mappings.md](mappings.md) and
> the four-level model in [`docs/conformance-model.md`](../conformance-model.md).

## 1. Why a separate suite for CR-11 (CR-11AM)

The four-level conformance model in [`docs/conformance-model.md`](../conformance-model.md)
covers semantic (L1), runtime (L2), interoperability (L3) and agentic
(L4) conformance. CR-11AM recasts those four into six **classes** that
test surfaces can implement independently and combine:

| Class       | Question answered                                                                                  | Maps to | Artefact(s)                                                  | Status |
|-------------|----------------------------------------------------------------------------------------------------|---------|--------------------------------------------------------------|--------|
| **Core**    | Can this product represent canonical Entities / Relationships / Assertions / Evidence / Profiles? | L1      | Schemas, golden & negative models in `models/`               | Implemented (CR-8) |
| **Exchange**| Can this product import and export exchange documents that survive CR-11AP round-trip?            | L3      | `schemas/model-envelope.json`, exchange fixtures, round-trip tests | Partial (seed CR-9.1; full release CR-11) |
| **Mapping** | Can this product declare, validate and execute a mapping declared in the `mappings/` registry?     | L3      | `mappings/archimate/`, `mappings/bpmn/`, `mappings/dmn/`     | Partial (ArchiMate v1.0.0; DMN evaluated; BPMN candidate) |
| **Runtime** | Does this product expose the vendor-independent runtime APIs defined in CR-9CL?                    | L2      | `runtime/GraphStore`, `tests/runtime/test_graphstore_contract.py` | Implemented (CR-9.1) |
| **Federation** | Can this product interact with external authoritative sources (live pull, not just import)?     | L3/L4   | `runtime/` federation adapters, Federation tests             | Partial (CR-9.1; full release CR-11) |
| **Agentic** | Can this product expose governed semantic context to agents per CR-9AH…CR-9AR / CR-10 §M?         | L4      | Agent Runtime Interface, audit-log schema, policy tests      | Proposed (CR-9.8 + CR-10 §M) |

The classes are independently testable; a Core-conformant product
that is not yet Exchange-conformant is meaningful as a stage of growth,
not a failure (cf. [conformance-model.md](../conformance-model.md) §5
— "conformance is not a single level").

## 2. The /conformance/ suite layout (CR-11AN)

CR-11AN defines a single tree that other repo areas feed. The `opendea
conformance test` CLI is the entry point; the result is a
test-report document comparable in shape to the canonical
`tests/conformance/` artefacts already used by the runtime tests:

```
conformance/
  schemas/                   — the canonical schemas under test
  fixtures/                  — golden interoperability datasets (CR-11AO)
  mapping-tests/             — one directory per mapping registry
    archimate/
    bpmn/
    dmn/
    rdf/
  validation-tests/          — golden + negative models (L1)
  exchange-tests/            — envelope round-trip tests (L3)
  identity-tests/            — canonical-id, aliasing, legacy-id tests
  provenance-tests/          — chain preservation, transformation record
```

`opendea conformance test`:

- walks the registered test surface per class,
- runs exchange-tests, mapping-tests, validation-tests,
  identity-tests and provenance-tests against fixtures,
- emits a human-readable report *and* a machine-readable artefact
  suitable for CI gating (CR-9CP).

## 3. Golden interoperability datasets (CR-11AO)

A conformance regime without regression fixtures is just prose.
CR-11AO specifies six golden interoperability datasets, each
exercising a different Source → Mapping → OpenDEA representation →
Expected result pipeline:

| Dataset               | Source representation         | Mapping                | OpenDEA expectations                                  |
|-----------------------|-------------------------------|------------------------|-------------------------------------------------------|
| `basic-enterprise`    | CSV (HR + ITSM extract)       | `csv-to-opendea@1.0.0` | Golden entity count, evidence chain, no Source loss   |
| `architecture`        | ArchiMate 3.2 Open Exchange    | `archimate@1.0.0`      | Matrix lossiness terms hold; Source preserved         |
| `dmm`                 | DMM v5 Assessment JSON        | `dmm-to-opendea@1.0.0` | Assessment → AssessmentResult → Evidence (golden)     |
| `agentic`             | Agent execution trace         | `agent-run-trace@1.x`  | Decision Evaluation logged; ALLOW/DENY/ESCALATE match  |
| `scenario`            | CR-10 canonical scenario      | `scenario@1.0.0`       | Scenario baseline + ScenarioState differ as expected  |
| `federated`           | Live federation pull sample   | `federation@1.x`       | Soft-state, conflict log, no auto-overwrite of asserted facts |

Each dataset lives at `conformance/fixtures/<dataset>/` with the same
four files: source, mapping, expected OpenDEA representation
(golden graph), expected result declaration (counts, traversals,
named queries).

## 4. Reference integration strategy (CR-11BF / BG / BH)

The CR-11 release order is deliberate. Adopting it as written is the
fastest path to ecosystem trust:

```
CR-11BF — OpenDEA ↔ OpenAPI / JSON ↔ Reference Dataset  (FIRST)
                ↓
CR-11BG — ArchiMate import / export                  (SECOND)
                ↓
CR-11BH — DMM Assessment → OpenDEA → Gap → Scenario  (THIRD)
                ↓
          Conformance release gated by all three
```

**Why this order.** (1) The OpenAPI ↔ OpenDEA bridge proves the
semantic contract without first solving vendor auth, rate-limit and
pagination conventions; the reference dataset is small, deterministic
and reused by every later test (CR-11AO `basic-enterprise`).
(2) The EA-to-EA semantic mapping proves OpenDEA can speak a peer
standard losslessly (or with a typed lossiness record — CR-11X).
(3) Assessment feeds Scenarios (`Assessment → OpenDEA → Gap → Scenario`);
this is the canonical demo story CR-11BI records, and it exercises
both the agentic layer (gap recommendation) and the scenario layer
(impact evaluation) — i.e. it requires L4-ish machinery to be at least
specified before the conformance regime can test it.

In practice: a new vendor integration starts with a JSON conformance
run; if that fails, the OpenAPI adapter is wrong, not the semantic
core. An EA-tool integration graduates to ArchiMate conformance once
it has passed `tests/conformance/mapping-tests/archimate/`. An
assessment/decision integration graduates to DMM conformance once L4
(Agentic) class status is at least partial.

## 5. Canonical demo story (CR-11BI — verbatim)

```
   Enterprise (OpenDEA semantic foundation)
      │
      ├── Enterprise model (entities, relationships, assertions,
      │   evidence, profiles, state, events, scenarios, decisions)
      │
      ├── DMM Assessment ──► AssessmentResult ──► Gap
      │                                    │
      │                                    ▼
      │                              Scenario
      │                                    │
      │                                    ▼
      │                             Recommendation
      │                                    │
      │              ┌─────────────────────┼─────────────────────┐
      │              ▼                     ▼                     ▼
      │        Architecture        Transformation          Governed
      │        Decision            Decision                Decision
      │              │                     │                     │
      │              └─────────────────────┼─────────────────────┘
      │                                    │
      │                                    ▼
      │                              Change Initiative
      │                                    │
      │                                    ▼
      └── Continuous Enterprise (CR-13 horizon)
```

This is the diagram CR-11BI pins as the canonical demo story; it is
the single picture that the conformance demonstration invokes end-to-end
across all six conformance classes.

## 6. See also

- [`docs/conformance-model.md`](../conformance-model.md) — the four levels this
  file reorganises into six classes
- [`docs/specification-and-conformance.md`](../specification-and-conformance.md)
  — semantic-conformance levels 0–5
- [overview.md](overview.md), [mappings.md](mappings.md) — framing and
  the registries the Mapping class consults
- [provenance.md](provenance.md), [identity.md](identity.md) — Federation
  and Agentic class inputs
