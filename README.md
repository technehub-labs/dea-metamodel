# OpenDEA Metamodel — Open Digital Enterprise Architecture Metamodel

> **Canonical entity definitions, relationships, and schemas for all DEA catalog repositories.**

[![Metamodel Version](https://img.shields.io/badge/version-0.3.0-blue)](./VERSION)
[![OpenDEAM Pin](https://img.shields.io/badge/OpenDEAM-v0.3.0-2DD4BF)](https://github.com/technehub-labs/dea-architecture-framework/tree/v0.3.0)
[![Metamodel Schema](https://img.shields.io/badge/schema-JSON%20Schema-blue)](./schemas/)
[![RDF Format](https://img.shields.io/badge/rdf-TTL-orange)](./ttl/)

## Overview

The DEA Metamodel is the **foundation layer** for the TechneHub Labs Enterprise Architecture space.
Every entity, relationship, and attribute used across all `dea-catalog-*` repositories is defined here
and referenced by version pin.

```
dea-metamodel (this repo)
       ↑
       │ version-pinned by all catalog repos
       │
   ┌───┴───────────────────────────────────────┐
   │  dea-catalog-principles                   │
   │  dea-catalog-patterns                     │
   │  dea-catalog-standards                    │
   │  dea-catalog-reference-models             │
   │  dea-catalog-metrics                      │
   │  dea-catalog-ontologies                   │
   │  dea-catalog-taxonomy                     │
   │  dea-catalog-glossary                     │
   └───────────────────────────────────────────┘
```

## Structure

```
dea-metamodel/
├── VERSION                     # Semantic version of the metamodel
├── metamodel.yaml             # Human-readable entity index
├── schemas/
│   ├── entities/              # Per-entity JSON Schema definitions
│   └── relationships/         # Relationship type definitions
├── ttl/                       # OWL/RDF Turtle serializations
├── sqlite/
│   └── schema.sql             # SQLite runtime schema
├── typescript/
│   └── src/                   # TypeScript interfaces
├── pydantic/                  # Python Pydantic models
└── docs/
    └── metamodel/            # Entity narrative docs
```

## Entity Hierarchy

```
Entity (abstract root)
├── Principle
├── ArchitecturePattern
├── Standard
├── ReferenceModel
│   ├── IntegrationPattern
│   ├── DataPattern
│   └── ApplicationPattern
├── Capability
├── Process
├── BusinessService
├── SolutionComponent
│   ├── ApplicationComponent
│   ├── InfrastructureComponent
│   └── IntegrationComponent
├── Technology
├── Metric
├── GlossaryTerm
├── TaxonomyNode
└── Viewpoint
```

## Relationship Types

| Relationship | Domain | Range | Description |
|---|---|---|---|
| `maps-to` | any Entity | any Entity | General-purpose cross-catalog mapping |
| `realizes` | SolutionComponent | Capability | Component implements a capability |
| `implements` | ArchitecturePattern | Standard | Pattern implements a standard |
| `influenced-by` | any Entity | Principle | Entity is governed by a principle |
| `decomposes` | Capability | Capability | Parent capability breaks into sub-capabilities |
| `orchestrates` | Process | Process | Parent process coordinates sub-processes |
| `consumes` | SolutionComponent | BusinessService | Component uses an external service |
| `provides` | SolutionComponent | BusinessService | Component exposes a service |
| `governs` | Standard | any Entity | Standard governs entity behavior |
| `measured-by` | any Entity | Metric | Entity is tracked via metric |

## Quick Start

### Validate an entity against the metamodel

```bash
# Validate a JSON entity
python3 scripts/validate_entity.py --schema schemas/entities/principle.json --entity my-principle.json

# Validate RDF serialization
python3 scripts/validate_rdf.py --schema ttl/dea-metamodel.ttl --input my-entity.ttl
```

### Query the SQLite runtime store

```bash
sqlite3 sqlite/dea-metamodel.db ".schema"
sqlite3 sqlite/dea-metamodel.db "SELECT * FROM entities WHERE type = 'ArchitecturePattern';"
```

### Generate TypeScript types

```bash
cd typescript && npm install && npm run generate
```

## Versioning Policy

- **Breaking changes** (entity removal, relationship rename) → minor version bump (0.**X**.0)
- **Additive changes** (new entity, new field) → patch bump (0.0.**X**)
- Catalog repos pin to a **specific tag** (e.g., `v0.3.0`) in their `metamodel.yaml`
- All changes go through PR → review → merge → tag workflow

## Contributing

1. Propose a change in the relevant `docs/metamodel/` narrative doc
2. Submit a PR updating the affected schema files
3. CI validates: JSON Schema valid, TTL parses, SQLite schema applies, TypeScript compiles
4. CODEOWNERS (platform-architecture team) must approve

## License

Apache 2.0 — see [LICENSE](./LICENSE).
