# Interoperability, Federation & Ecosystem Conformance — Overview

> **KB note — CR-11 is the consolidation change request, not a
> conceptual expansion.** It exists to let enterprise knowledge
> *already living in other systems* participate in OpenDEA reasoning
> and decisions, without those systems adopting the OpenDEA metamodel.
> Source: CR-11 §1–2 and §66. Companion notes: [architecture.md](architecture.md),
> [identity.md](identity.md), [mappings.md](mappings.md),
> [federation.md](federation.md), [events.md](events.md),
> [security.md](security.md).

## 1. Why interop is the next phase (CR-11 §1)

OpenDEA's runtime (CR-9) and scenario engine (CR-10) work because the
canonical metamodel is stable, but **the data those engines reason
over does not live in OpenDEA**. It lives — in fragments — across the
systems the enterprise already runs:

| Domain | Typical sources |
|---|---|
| Architecture | EA repositories (Archi, Avolution, BiZZdesign, LeanIX) |
| Operations | CMDBs (ServiceNow CMDB, BMC, i-doit) |
| Discovery | Data catalogs (Collibra, Alation, Informatica) |
| Service | ITSM (ServiceNow, Jira SM, Cherwell) |
| Risk & compliance | GRC (Archer, ServiceNow GRC, SAP GRC) |
| Capability maturity | DMM, CMMI, OBMM assessments |
| Portfolio | LeanIX, Planview, Apptio |
| Cloud | AWS Config, Azure Resource Graph, GCP Asset Inventory |
| People | HR / IAM (Workday, SAP SuccessFactors, Okta) |
| Agents | Agent registries, MCP tool catalogs, internal agent platforms |

CR-9J (adapters) and CR-10.4 (assessments) already let the runtime
*ingest* snapshots, but they do not yet give OpenDEA a stable
*semantic contract* with those systems, and they do not yet let
OpenDEA reason over **federated** knowledge it does not own.

## 2. The critical design principle (CR-11 §2)

> **OpenDEA should be the semantic contract; adapters should absorb
> external complexity.**

The wrong pattern is to make OpenDEA imitate every external system, or
to demand external systems adopt the OpenDEA metamodel. The right
pattern is to keep OpenDEA small, canonical, and stable — and to
push all heterogeneity into adapters. The CR §2 diagram pair:

```
         WRONG: hub pattern                         RIGHT: adapter pattern
                                                              
   EA Repo ─┐                                        EA Repo ──► [Adapter] ─┐
   CMDB ─────┤                                   CMDB ────► [Adapter] ─┤
   GRC ──────┼───►  OpenDEA-shaped  ────► All     GRC ─────► [Adapter] ─┤
   DMM ──────┤         Hub                              │             │
   Cloud ────┘                                   OpenDEA ◄──────────────┘
                                                  (canonical, stable)
   (hub grows; every new                              (adapters grow; OpenDEA
    source rewrites the core)                          stays canonical)
```

## 3. The strategic outcome (CR-11 §66)

The end-state claim is precise and falsifiable: CR-11 delivers
**a canonical semantic layer through which heterogeneous enterprise
knowledge interoperates — without external systems adopting the
OpenDEA metamodel.** Every CR-11 concept (Sources, Adapters, Mappings,
Federation, Events, Security) is a load-bearing piece of that claim.

## 4. Scope of CR-11

CR-11 covers the full interop surface: source modelling, connector vs
adapter distinction, semantic mapping, identity reconciliation,
property-specific authority, federated query, event integration,
governed mapping lifecycle, and interop security. The rest of this
directory unpacks each.
