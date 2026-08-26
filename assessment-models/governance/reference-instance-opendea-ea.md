# Reference Assessment Instance — opendea-enterprise-architecture

CR-AM-11 §6 / §24. The OpenDEA Enterprise Architecture assessment model
instance demonstrates the assessment and maturity architecture (§31 acceptance
criterion for this CR's **OpenDEA Reference Model** group) and serves as the
first ecosystem participant in the federated ecosystem.

## What this instance demonstrates

Per CR-AM-11 §31 (OpenDEA Reference Model):

- The instance **conforms** to the canonical OpenDEA contracts.
- The instance **demonstrates** maturity structure, maturity scale, evaluation
  model, scoring, conformance and benchmark baseline.
- The instance is the **first consumer** of the Phase 1 ecosystem (it is the
  first thing registered with `Assessment-Models/assessment-registry` once
  Phase 6 begins migration), and is **referred to by** the Phase 4
  first-model candidate (the Digital Transformation composite model) for
  benchmark participation.

## Architecture

| Layer | Artifact | Validation |
|---|---|---|
| Maturity structure | `assessment-models/scale-examples/opendea-enterprise-architecture.yaml` | `validate-maturity-scale-examples` CI |
| Evaluation model | `assessment-models/evaluation-examples/opendea-enterprise-architecture.yaml` | `validate-maturity-evaluation-examples` CI |
| Benchmark baseline | `assessment-models/baseline-examples/opendea-enterprise-architecture.yaml` | `validate-maturity-baseline-examples` CI |

The three artefacts are linked by id+version:

- The scale declares its own levels (L-0…L-4) and progression.
- The evaluation model references the scale (id + version) and declares its
  six criteria with per-level expectations.
- The baseline references the scale (id + version), the band set
  (canonical v2 bands), the resolution rule (id), and the evaluation model
  (id + version) — frozen for Benchmark 2026 with a sha256 content-hashed
  snapshot of the effective scale contract at lock time.

## Conformance

The instance conforms to the contract suite published in
`assessment-models/contracts/contract-suite.yaml`:

- **assessment-contract** — instruments, executions, results, views, gap /
  insight / improvement-objective analytics.
- **maturity-model-contract** — dimensions + criteria + indicators (the
  evaluation model carries the criteria; the orchestrating model can add
  dimensions and indicators as Level 3+ adoption surfaces them).
- **maturity-scale-contract** — model-owned scale (CR-AM-09) with the
  v2-band canonical instance.
- **scoring-contract** — weighted-mean over a 0–100 native domain, with
  per-level effort_multiplier producing the effort-adjusted value reported
  in AssessmentResults.
- **conformance-contract** — six-axis compatibility declaration, modelReference
  lineage, vocabulary compliance.
- **benchmark-contract** — cohort eligibility + immutable baseline for
  Benchmark 2026.

The contract handshake (§15) for this instance pins `dea-metamodel@main`
during authoring; release time switches to an immutable tag and the
handshake is published to the registry.

## Phase 3 exit criterion (§30)

> *The metamodel has a real assessment model instance demonstrating the
> architecture.*

Met on this PR: the scale + evaluation + baseline triplet exercises the
full maturity-architecture pipeline against the published schemas, with
content_hash reproducibility anchored at the baseline.