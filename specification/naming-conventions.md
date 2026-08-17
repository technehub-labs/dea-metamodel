# Naming Conventions & Concept Identity (CR-8 §6-§7)

## Canonical rules

| Construct | Rule | Examples |
|---|---|---|
| Class names | PascalCase | `BusinessCapability`, `Decision`, `ArchitectureState`, `AgentProfile`, `AssessmentResult` |
| Relationship ids | `dea:` + kebab-case | `dea:depends-on`, `dea:informed-by`, `dea:authorized-by` |
| RDF/OWL properties | camelCase serialization | `dea:dependsOn`, `dea:informedBy` (see `ttl/`) |
| Enumeration values | lowercase-kebab (repository convention — see reconciliation below) | `proposed`, `under-evaluation`, `active`, `retired` |
| Concept ids | `dea:` + PascalCase, stable forever | `dea:Decision`, `dea:BusinessCapability`, `dea:Agent` |
| Instance ids | `prefix:type-slug` | `cap.customer-service`, `agent.customer-service` |
| Namespace | `https://technehub-labs.github.io/dea-metamodel/` prefix `dea` — never casually changed (§6) | |
| Profile namespaces (§54) | `dea:<profile>:` for profile-owned content; `ext:<name>:` reserved for third-party profiles | `dmm:dimension/strategy`, `ext:financial:…` |

## Reconciled divergences from the CR-8 text (CR-8.2)

1. **Enumeration case.** CR-8 §6 suggests PascalCase enum values. The repository has used
   lowercase-kebab values since CR-1 across 100+ schemas and all catalog repos. Per CR-8 §22
   itself ("follow whatever schema CR-1–CR-7 established rather than introducing an
   incompatible format"), lowercase-kebab is **canonical**. PascalCase display labels are a
   presentation concern.
2. **Relationship naming.** CR-8 §10 lists camelCase relationship names. The canonical idiom
   here is kebab-case ids (`dea:depends-on`) with camelCase RDF properties (`dea:dependsOn`)
   — established CR-2 and serialized in `ttl/`. Both halves of §6 are therefore satisfied,
   each in its own layer.

## Concept identity (§7)

**Names are not identities.** "Customer Service" can be a capability, function, service,
department or process. Every modeled object carries a stable `id` + canonical `type`;
the display `name` may change freely. Instance ids remain stable across renames (CR-3 E004:
external identifiers never substitute for the OpenDEA id).
