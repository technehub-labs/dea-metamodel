# Contract Publication — OpenDEA Assessment Contract Suite

CR-AM-11 Phase 2. Governs how the six canonical contract families (CR-AM-11 §16)
are published from `technehub-labs/dea-metamodel` and consumed by the
Assessment-Models ecosystem.

## The suite

`assessment-models/contracts/contract-suite.yaml` is the machine-readable
publication surface. It maps each contract family to its landed artifacts
(schemas, governance docs, canonical data) and is CI-validated on every PR
(`validate-contract-suite` in `ci-assessment-models.yml`): every path must
resolve, every schema must be Draft 2020-12, and every file under
`assessment-models/schemas/` must be claimed by exactly one family
(completeness guard — an unmapped schema fails CI).

| Family | Scope | Key artifacts |
|---|---|---|
| `assessment-contract` | Instruments, executions, results, views, result-side analytics | 16 schemas + 6 governance docs |
| `maturity-model-contract` | Maturity structure & composition (CR-AM-10 components/references) | 5 schemas + component registry |
| `maturity-scale-contract` | Model-owned scales, progression, resolution, baselines (CR-AM-09) | 5 schemas + v2 bands + legacy-name map |
| `scoring-contract` | Scoring, evaluation, aggregation | 3 schemas |
| `conformance-contract` | Shared `$defs`, compatibility axes, relationships, vocabularies | 3 schemas + `vocabulary/` + versioning/compatibility policy |
| `benchmark-contract` | Eligibility, cohorts, comparative benchmarking (CR-AM-06/07) | 2 schemas + 2 governance docs + `benchmark/` |

## Consuming a contract (the handshake, CR-AM-11 §15)

A model repository declares its dependency in its root `model.yaml`:

```yaml
conformance:
  contract:
    id: maturity-scale-contract        # a family id from contract-suite.yaml
  source:
    organization: technehub-labs
    repository: dea-metamodel
  version: "1.0"                        # the contract family version
```

Rules:

1. **Immutable pins only.** Conformance validation resolves the handshake
   against a tagged dea-metamodel release (or commit SHA) — never `main`,
   `master`, `latest` (CR-AM-11 §12).
2. **Known family ids only.** `Assessment-Models/assessment-ci`
   (`validate_handshake.py`) rejects handshake ids outside the §16/Annex A
   inventory — a typo in the contract id fails CI.
3. **Canonical source only.** The handshake source must be
   `technehub-labs/dea-metamodel`. Contracts are not re-published from
   ecosystem repositories.

## Compatibility declarations (CR-AM-11 §17)

A model may declare a supported range:

```yaml
compatibility:
  metamodel:
    minimum: 1.0.0
    maximum: "<2.0.0"
```

or per contract family:

```yaml
compatibility:
  contracts:
    - id: maturity-model-contract
      version: "^1.0"
```

Syntax follows the existing schema conventions
(`schemas/compatibility.schema.json` + `governance/compatibility.md`).

## Versioning

Families are independently identifiable but currently versioned together with
the suite (`version: 1.0.0`, matching spec/metamodel 1.0.0 — the publication is
additive, no canonical version bump). Independent per-family versioning is a
deliberate Phase 2 decision to be recorded in a contract-publication ADR when
the first family needs to move at its own cadence (CR-AM-11 Annex A note).

## Extraction boundary

This publication maps families to artifacts at their **current** locations
inside `assessment-models/`. The physical relocation of contract artifacts to
the §5 target layout (`contracts/`, `schemas/`, `vocabularies/`, `validation/`
at repo root) is the contract-extraction & sub-tree-reduction pre-step, landing
as separate PRs; each such PR updates this manifest's paths, and the
`validate-contract-suite` CI job fails if any path stops resolving — the
manifest is the anti-drift guard for the extraction itself.
