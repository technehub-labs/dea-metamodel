# Logical Layout — CR-AM-11 §5 Contract Architecture

**Decision (CR-AM-11 Phase 2 slice 2, Option C):** the repository layout in
CR-AM-11 §5 is the **logical** contract architecture of the OpenDEA assessment
domain. It is carried by the machine-readable manifest
(`contracts/contract-suite.yaml`) and this map — **not** by physical file
relocation. Zero files move.

Rationale: the contract artifacts (notably `schemas/common.schema.json`) are
referenced by 21 schemas with sibling-relative `$ref`s and by hardcoded lists
in the test suite; physical relocation would require rewriting every reference
across all six contract families for no behavioural gain. The logical layout
gives consumers a stable mental and contractual model; the physical layout
stays where it is and remains CI-green.

## Logical → physical map

| §5 logical location | Physical location (current) | Contents |
|---|---|---|
| `metamodel/` | repo root: `metamodel/dea-metamodel.yaml` | Canonical OpenDEA metamodel |
| `contracts/` | `assessment-models/contracts/` | Contract suite manifest (the six §16 families) |
| `schemas/` | `assessment-models/schemas/` | 34 Draft 2020-12 JSON Schemas, family-assigned by the manifest |
| `vocabularies/` | `assessment-models/vocabulary/` | Controlled vocabularies (conformance-contract family) |
| `validation/` | `assessment-models/tests/` + `.github/workflows/ci-assessment-models.yml` | Conformance suites + CI validators |
| `assessment-models/opendea-enterprise-architecture/` | `assessment-models/` (Phase 3 reduces the sub-tree toward the single reference instance) | OpenDEA EA assessment model instance (in authoring) |
| `examples/` | `assessment-models/examples/` | Canonical worked examples |
| `docs/` | repo-root `docs/` + `assessment-models/governance/` | Canonical architecture docs + assessment governance policy |

## Rules

1. **The manifest is authoritative.** Family membership and artifact paths are
   read from `contracts/contract-suite.yaml`, guarded by the
   `validate-contract-suite` CI job (paths must resolve; schemas/ coverage must
   be complete). This document is the human-readable companion.
2. **Consumers pin the release, not the layout.** Model repositories declare
   conformance to a contract family id + version (the §15 handshake) against an
   immutable dea-metamodel release. Physical paths are internal to this repo.
3. **If physical extraction is ever revisited**, it is a new CR with its own
   blast-radius analysis (reference-rewrite counts, test-list guards), not an
   implicit continuation of CR-AM-11 Phase 2.
