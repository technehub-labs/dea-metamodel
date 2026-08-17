# Conformance Specification (CR-8 §25-§29, §56-§58)

## 1. Conformance levels (§27)

| Level | Name | Meaning | Enforcement here |
|---|---|---|---|
| 0 | Syntax | document parses | `opendea validate` stage 0 |
| 1 | Structural | envelope + element schemas valid | validator + JSON Schema |
| 2 | Semantic | types, relationships, endpoints valid against the registry | validator (registry-driven) |
| 3 | Profile | declared profile rules hold (A/T/G families) | validator + profile rule sets |
| 4 | Governance | authority, ownership, policy, accountability present where required | G001–G016 |
| 5 | Operational | lifecycle, temporal, assessment semantics valid | T001–T010, A001–A013 |

**No organization may claim "OpenDEA compliant" without specifying level + profiles (§27).**

## 2. Semantic invariants (§56) — the mathematical contract

| Invariant | Rule |
|---|---|
| INV-IDENTITY | every concrete entity instance has a unique stable id |
| INV-TYPE | every instance has exactly one canonical primary type |
| INV-REL | every relationship instance references a declared relationship type |
| INV-LIFECYCLE | lifecycle-managed instances carry a valid lifecycle state |
| INV-GOV | every autonomous production Agent has authority AND accountability |
| INV-ASSESS | every AssessmentResult references its Assessment context |

## 3. Error taxonomy (§29)

| Code | Meaning |
|---|---|
| DEA-E001 | invalid type |
| DEA-E002 | unknown relationship |
| DEA-E003 | cardinality violation |
| DEA-E004 | missing required property |
| DEA-E005 | invalid relationship target |
| DEA-E006 | invalid relationship source |
| DEA-E007 | circular dependency |
| DEA-E008 | governance violation |
| DEA-E009 | authority violation |
| DEA-E010 | profile violation |
| DEA-W0xx | warnings (same numbering space) |

Profile rule violations carry their native ids (O/R/E/A/T/G + DMM-xxxx) with severity.

## 4. Conformance report (§28)

The validator emits a structured report — see `tools/opendea_validate.py`:

```yaml
conformance:
  status: failed
summary: {errors: 3, warnings: 5}
levels: {syntax: pass, structural: pass, semantic: fail, profile: fail}
violations:
  - {rule: G006, code: DEA-E009, severity: error, element: agent.customer-service,
     message: "Missing delegated authority"}
```

## 5. Open-world vs closed-world (§57)

Core validation is **open-world**: absence of a relationship is not proof of absence.
Profiles may impose **closed-world** requirements within their scope: a production Agent
without a declared policy is *unknown* to Core but **non-conformant** under the agentic
profile (G008). The validator reports which world each violation comes from.

## 6. Known / unknown / not-applicable (§58)

`null` never carries multiple meanings. Property values distinguish:
`known` · `unknown` · `not-applicable` · `not-assessed` · `not-disclosed` · `derived`
(declare via the value vocabulary in instance data; essential for DMM and enterprise data).

## 7. Assertion lifecycle & provenance (§39-§41)

Assertions move Proposed → Validated → Approved → Active → Superseded (CR-6 machinery).
Every derived or AI-generated fact carries provenance: `derivedFrom`, `derivationRule`,
`assertedBy`, `observedAt`, `confidence`. Assertion status values:
`declared · observed · imported · inferred · generated · validated · approved` —
an LLM-generated assertion is never equivalent to a human-approved architectural fact (§40).
