# Metamodel Semantics (CR-1)

## Semantic IDs (CR-1.4)

Every normative entity and relationship has a stable, machine-readable identifier in the
`dea:` namespace. Display names are labels, never identifiers.

```yaml
entity:
  id: dea:BusinessCapability
  name: Business Capability        # display label only

relationship:
  id: dea:realizes
  name: realizes
```

- Entity IDs: `dea:` + PascalCase name (`dea:BusinessCapability`, `dea:AIMLModel`).
- Relationship IDs: `dea:` + kebab-case (`dea:realizes`, `dea:maps-to`).
- IDs are immutable once published. A rename is a MAJOR semantic change
  (see `docs/versioning.md`); the old ID is kept as a `legacy_ids` alias.
- Legacy identifiers from earlier representations (e.g. `dea:entity-capability` in the
  viewer graph, `Capability` in v0.3.x docs) are recorded in each entity's
  `legacy_ids` for migration mapping (CR-10 will consume these).

## Registries (CR-1.5)

`metamodel/registry/entities.yaml` and `metamodel/registry/relationships.yaml` are the
authoritative machine-readable inventory, generated from the normative source.
Consumers (viewer, CLI, catalog tooling) MUST read the registry rather than maintaining
their own conceptual graph.

## Two relationship vocabularies — known divergence

The repository currently carries **two** relationship vocabularies, both registered in
the normative source with `cr2_note` markers:

| Vocabulary | Source | Types | Status |
|---|---|---|---|
| **Structural** | OpenDEAM root model rendering vocabulary (viewer graph `rel_type`) | 7: aggregation, association, composition, dependency, flow, governance, realization | normative |
| **Instance** | `schemas/relationships/relationship-instance.json` enum | 10: maps-to, realizes, implements, influenced-by, decomposes, orchestrates, consumes, provides, governs, measured-by | normative |

This duality is **acknowledged technical debt, not a resolved design**. CR-2
(Relationship Semantics) replaces both with a single authoritative, typed relationship
ontology expressing direction, semantics, cardinality, provenance and temporal validity.
Until CR-2 closes, new model content should prefer the instance vocabulary for
machine-readable instances and the structural vocabulary for rendering.

## Entity status vs lifecycle

- `status: normative` — the entity is part of the governed normative inventory.
- `lifecycle: existing | scaffold | proposed | planned` — maturity of the entity's
  catalog realization, inherited from the OpenDEAM root model. `planned` entities have
  no hosting catalog yet and no JSON schema; they exist in the normative model so the
  inventory is complete and versioned.

## Layers and dimensions

Layers (L1–L5) and cross-cutting dimensions (ECF matrix, measurement,
AI & automation governance, semantic) are governed by the upstream root model
(`dea-architecture-framework`, pin declared in the normative source). This repository
references that allocation; it does not redefine it. "Layer" means architecture layer
only — see the root model's terminology block (ADR-0001).
