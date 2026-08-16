# Versioning Policy — OpenDEA Metamodel (CR-1.7)

The metamodel uses **semantic versioning** (`MAJOR.MINOR.PATCH`) with the rules below.
The single declared version lives in `metamodel/manifest.yaml` and `VERSION`; both must
always agree (enforced by CI).

## Component versions are separate (CR-1.3)

Four concepts version independently and MUST NOT be conflated:

| Component | Example | Changes when |
|---|---|---|
| **Metamodel version** | 0.6.0 | The normative semantics change (entities, relationships, layers, meanings) |
| **JSON Schema version** | 0.6.0 | The generated/validated schema surface changes |
| **SQLite projection version** | 0.6.0 | The database projection changes |
| **Viewer version** | 0.1.0 (in `dea-web-viewer`) | The viewer app evolves — independent of ontology |

A database implementation can change without changing the metamodel; the viewer can
evolve without changing the ontology.

## MAJOR — breaking semantic changes

- Removing an entity or relationship
- Changing the *meaning* of an entity or relationship
- Changing inheritance / abstraction hierarchy
- Incompatible cardinality changes
- Renaming a semantic ID (`dea:*`) without a declared alias

## MINOR — backward-compatible additions

- New entity or relationship
- New optional attribute
- New extension or profile

## PATCH — non-semantic corrections

- Documentation, descriptions, examples, formatting
- Regenerated derived artifacts with no semantic change

## The relationship-redefinition rule

**Changing the definition of an existing relationship is a semantic change, even if the
JSON schema remains technically compatible.** It triggers at least a MINOR review and
potentially a MAJOR version bump. Schema compatibility is not semantic compatibility.

## Change control (CR-1.8)

Every metamodel modification requires a Change Request record in `change-requests/`:

```
CR-NNN
Title: <short title>
Status: Proposed | Accepted | Implemented | Closed
Version: <metamodel version it targets>
Depends on: <prior CRs, if any>
```

CRs are numbered sequentially and processed in dependency order. The active programme
(CR-1 … CR-10) is tracked in `change-requests/README.md`.

## Semantic expansion freeze (CR-1.6)

Until CR-3 closes: **no new entity types** may be introduced to solve modelling gaps —
no additional AI, governance, DMM, data, or technology entities. Every new concept added
before the semantics stabilize compounds existing ambiguity.
