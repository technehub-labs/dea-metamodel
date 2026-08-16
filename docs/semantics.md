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

## One canonical relationship ontology (CR-002)

As of v0.7.0 the repository has a **single** relationship vocabulary: the canonical
registry in `metamodel/dea-metamodel.yaml` (inventory projection:
`metamodel/registry/relationships.yaml`). It replaces the pre-0.7.0 split between the
viewer graph's 7 structural rel_types and the 10-type instance enum.

Key semantics:

- **Categories** (controlled, CR-2 §4): structural, realization, dependency, flow,
  serving, execution, governance, information, assessment, transformation, traceability.
- **Direction is canonical**: always source-to-target. Inverse views (e.g.
  `dea:realized-by`) are declared via the `inverse` property and generated — never
  stored as independent relationships (CR-2 §8).
- **Endpoints are typed**: `source.types` / `target.types` constrain valid connections
  (CR-2 §12); cardinality is explicit at both ends (§13).
- **Lifecycle** (§20): `proposed | active | deprecated | retired`. Deprecated types
  remain readable via the crosswalk but are rejected for new instances (R011).
- **Provenance** (§21/§22): instances can carry structured provenance; AI-asserted
  relationships are distinguishable via `agent_id` + `verification_status` + `confidence`.
- **maps-to is narrowed** (§9) to crosswalk/classification/traceability/equivalence with
  a mandatory `mapping.kind`.
- **Viewer is a projection** (§10): `viewer/entity-graph.json` edges resolve to canonical
  `rel_ids` via `metamodel/migration/relationship-crosswalk.yaml`; visual attributes
  (`rel_type` style) are presentation-only.
- **Entity schemas do not hold relationship state** (§11): duplicated convenience
  properties are `deprecated: true` as of v0.7.0 and will be removed in CR-003.

The pre-0.7.0 vocabularies are preserved as migration history in the crosswalk.

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
