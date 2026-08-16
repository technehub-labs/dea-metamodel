# Repository Architecture — Canonical Metamodel (CR-1)

## The foundational principle

```
                 ┌───────────────────────┐
                 │  CANONICAL METAMODEL  │
                 │       v0.6.x          │
                 └───────────┬───────────┘
                             │
               ┌─────────────┼──────────────┐
               │             │              │
               ↓             ↓              ↓
          JSON Schema       SQL          Viewer
               │             │              │
               └─────────────┼──────────────┘
                             ↓
                       DEA Instances
```

**Never the reverse.**

There is one normative semantic model: **`metamodel/dea-metamodel.yaml`**.
Everything else is a representation, projection, serialization, implementation,
or visualization of that model.

## Required rule (CR-1.1)

> The canonical DEA metamodel is defined by the normative metamodel specification.
> All schemas, database structures, viewer graphs, documentation diagrams and other
> representations MUST be generated from or validated against the normative specification.

The following MUST NOT independently define the metamodel — they are derived artifacts:

- `viewer/entity-graph.json`
- `sqlite/schema.sql`
- `README.md`
- `schemas/**`, `typescript/**`, `pydantic/**`, `ttl/**`

## Authority chain (D1 ruling, CR-001)

```
technehub-labs/dea-architecture-framework   model/opendeam-model.yaml  (ENTERPRISE MODEL root)
        │  governs: layer/building-block/dimension allocation, entity lifecycle
        ↓  one-way sync (opendeam-sync.yml), tag-pinned
technehub-labs/dea-metamodel                metamodel/dea-metamodel.yaml  (METAMODEL normative source)
        │  governs: semantic definitions, IDs, relationships, artifact projections
        ↓  generated / validated artifacts
schemas · sqlite · typescript · pydantic · ttl · viewer
        ↓  version pin
dea-catalog-* repos · dea-web-viewer · dea-cli
```

The upstream root model governs *enterprise-model allocation*; this repository governs
*metamodel semantics*. Neither redefines the other's domain. Both directions of drift
are CI-checked.

## Layout

```
dea-metamodel/
├── metamodel/                      # NORMATIVE
│   ├── dea-metamodel.yaml          #   ← the single source of truth
│   ├── manifest.yaml               #   machine-readable declaration (CR-1.2)
│   └── registry/                   #   authoritative inventory (CR-1.5)
│       ├── entities.yaml
│       └── relationships.yaml
├── change-requests/                # change control (CR-1.8)
├── docs/
│   ├── architecture.md             # this file
│   ├── semantics.md                # semantic conventions, IDs, vocabularies
│   └── versioning.md               # versioning + change-control policy (CR-1.7)
├── tests/conformance/              # conformance suite (CR-1.9)
├── schemas/  sqlite/  typescript/  pydantic/  ttl/  viewer/   # DERIVED
├── examples/                       # INFORMATIVE
├── CHANGELOG.md
└── VERSION                         # == metamodel version (CI-enforced)
```

## Generation direction (CR-1.10)

Target end-state (completed by CR-10):

```
Canonical Metamodel
        ├── generate → JSON Schema
        ├── generate → SQLite
        ├── generate → Viewer Graph
        ├── generate → TypeScript types
        ├── generate → Documentation
        └── generate → Validation rules
```

CR-1 lands the normative source, manifest, registries, versioning, change control,
conformance tests, and CI drift enforcement. Artifacts that already have generators
(viewer graph, SVG, pydantic) are wired to the normative source; the rest are
*validated against* it until their generators exist (CR-10 scope).
