# Serialization & Versioning (CR-8 §18-§22)

## 1. Reference serializations (§22)

- **YAML** — human authoring (reference serialization, used by `models/golden/`).
- **JSON** — machine interchange.
- **RDF/OWL (Turtle)** — interoperability representation (`ttl/`), evaluated per CR-8 §2 and
  adopted as a **derived** serialization, not a mandatory one. JSON-LD context is a roadmap
  candidate under `schema/contexts/`.

The canonical semantic specification remains `metamodel/dea-metamodel.yaml`; **no
serialization ever becomes the accidental ontology** (§21).

## 2. Document shape

Every model uses the standard envelope (`schemas/model-envelope.json`):
`opendea.version` + `model{id,name,version}` + `profiles[]` + `context` + `metadata` +
`elements[]`. Elements carry `id` (stable), `type` (canonical), `name` (display),
`properties{}`, `relationships[]` (typed, directed, optionally temporal).

## 3. Semantic versioning (§18)

`MAJOR.MINOR.PATCH`:
- **MAJOR** — breaking semantic changes (removed concepts, inverted relationship semantics,
  narrowed endpoint types).
- **MINOR** — backward-compatible additions (new concepts, new profiles, widened endpoints).
- **PATCH** — corrections without semantic change (definition clarifications, typos).

## 4. Two-level compatibility (§19)

Compatibility is evaluated twice:
1. **Syntax compatibility** — schemas still validate.
2. **Semantic compatibility** — meanings unchanged. E.g. flipping `supports` from
   "Capability enables Service" to "Service enables Capability" is a **semantic breaking
   change (MAJOR)** even if every JSON schema still passes.

## 5. Deprecation (§20)

Concepts/relationships carry `status: stable | experimental | deprecated | retired`.
Deprecated entries MUST declare: `replacement`, `deprecated_since`, `removal_target`,
`migration_guidance` (see `docs/versioning.md` and `metamodel/migration/`).

## 6. Migration (§64-§65)

Every breaking change ships a migration rule in `metamodel/migration/`:
legacy concept → canonical concept → transformation. Consumers should never need to
hand-rewrite models for a MINOR/PATCH release; MAJOR releases provide migration tooling
guidance (schema migration + semantic migration + profile migration).
