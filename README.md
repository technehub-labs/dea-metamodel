# OpenDEA Metamodel — Open Digital Enterprise Architecture Metamodel

> **Canonical entity definitions, relationships, and schemas for all DEA catalog repositories.**

[![Metamodel Version](https://img.shields.io/badge/version-0.7.0-blue)](./VERSION)
[![OpenDEAM Pin](https://img.shields.io/badge/OpenDEAM-v0.5.0-2DD4BF)](https://github.com/technehub-labs/dea-architecture-framework/tree/v0.5.0)
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
   │  dea-catalog-tenets                       │
   │  dea-catalog-patterns                     │
   │  dea-catalog-guardrails                   │
   │  dea-catalog-blueprints                   │
   │  dea-catalog-metrics                      │
   │  dea-catalog-ontologies                   │
   │  dea-catalog-concepts                     │
   └───────────────────────────────────────────┘
```

## Normative / Derived / Informative (CR-1)

**There is one normative semantic model. Everything else is a representation,
projection, serialization, implementation, or visualization of that model.**

> The canonical DEA metamodel is defined by the normative metamodel specification
> (`metamodel/dea-metamodel.yaml`). All schemas, database structures, viewer graphs,
> documentation diagrams and other representations MUST be generated from or validated
> against the normative specification.

| Class | Content | Authority |
|---|---|---|
| **Normative** | `metamodel/dea-metamodel.yaml`, `metamodel/manifest.yaml`, `metamodel/registry/` | The semantic metamodel — the only source of truth |
| **Derived** | `schemas/`, `sqlite/`, `typescript/`, `pydantic/`, `ttl/`, `viewer/entity-graph.json`, `viewer/metamodel.svg` | Generated from or validated against the normative model — never edited to change semantics |
| **Informative** | `docs/` narratives, `examples/`, diagrams, tutorials | Illustration only — no semantic authority |

Change control: every metamodel modification requires a CR in [`change-requests/`](./change-requests/)
following [`docs/versioning.md`](./docs/versioning.md). **Semantic expansion freeze in
effect: no new entity types until CR-003 closes.**

## Structure

```
dea-metamodel/
├── metamodel/                 # NORMATIVE — dea-metamodel.yaml, manifest.yaml, registry/
├── change-requests/           # CR-based change control
├── docs/                      # architecture.md · semantics.md · versioning.md (+ narratives)
├── tests/conformance/         # Conformance suite (runs in CI)
├── VERSION                    # == metamodel version (CI-enforced)
├── CHANGELOG.md
├── metamodel.yaml             # LEGACY index (deprecated v0.6.0 — kept for compatibility)
├── schemas/                   # DERIVED — per-entity JSON Schema definitions
├── ttl/                       # DERIVED — OWL/RDF Turtle serializations
├── sqlite/                    # DERIVED — SQLite runtime projection
├── typescript/                # DERIVED — TypeScript interfaces
├── pydantic/                  # DERIVED — Python Pydantic models
└── viewer/                    # DERIVED — entity graph + rendered diagram
```

## Semantic IDs

Every normative entity and relationship carries a stable identifier
(`dea:BusinessCapability`, `dea:realizes`) — display names are labels, never identifiers.
The authoritative inventory is [`metamodel/registry/`](./metamodel/registry/). See
[`docs/semantics.md`](./docs/semantics.md) for ID conventions, the two relationship
vocabularies (structural vs instance — unification is CR-002), and lifecycle states.

## Diagram Design Tokens

The rendered metamodel diagram (`viewer/metamodel.svg`) follows a locked
design defined in **`viewer/diagram-tokens.json`** — no canvas (transparent
background inheriting the page), dark layer-colored packages, small italic
relationship labels with no outline, light-grey attribute text on dark entity
fills.

Every regeneration consumes these tokens: `generate_puml.py` (PlantUML skin
params) and `inject_svg_attributes.py` (SVG post-processing) load them via
`.github/scripts/diagram_tokens.py`. Do not hardcode design values in the
pipeline scripts.

Per-layer accent/dark colors are **not** in the token file — they cascade
from the OpenDEAM root model through `viewer/entity-graph.json`
(`layers[].color` / `layers[].dark_color`), so new layers and packages pick
up color coding automatically. Extend the token file (e.g. the `dimension`
tokens) only when adding a new cross-cutting dimension.

## Quick Start

### Validate an entity against the metamodel

```bash
# Validate a JSON entity
python3 scripts/validate_entity.py --schema schemas/entities/tenet.json --entity my-tenet.json

# Validate RDF serialization
python3 scripts/validate_rdf.py --schema ttl/dea-metamodel.ttl --input my-entity.ttl
```

### Run the conformance suite

```bash
python3 -m pytest tests/conformance/ -v
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

Full policy: [`docs/versioning.md`](./docs/versioning.md). Summary:

- **MAJOR** — breaking semantic changes (entity/relationship removal or redefinition,
  inheritance change, incompatible cardinality)
- **MINOR** — backward-compatible additions (new entity/relationship, optional attribute)
- **PATCH** — non-semantic corrections (docs, formatting, regenerated artifacts)
- **Changing a relationship's definition is a semantic change even when the JSON schema
  stays compatible.**
- Catalog repos pin to a **specific tag** (e.g., `v0.6.0`) in their `metamodel-pointer.yaml`

## Contributing

1. Open a Change Request record under `change-requests/` (see `change-requests/README.md`)
2. Submit a PR against the **normative source** (`metamodel/dea-metamodel.yaml`) — never
   against derived artifacts
3. CI validates: JSON Schema valid, TTL parses, SQLite schema applies, TypeScript compiles,
   **conformance suite passes, no version/semantic drift**
4. CODEOWNERS (platform-architecture team) must approve

## License

Apache 2.0 — see [LICENSE](./LICENSE).
