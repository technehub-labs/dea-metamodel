# Type System (CR-8 §8-§9, §14-§15)

## 1. Shape (§8)

OpenDEA deliberately uses a **shallow** type system:

```
Entity
 ├── abstract anchors (Entity, ArchitectureElement, Behavior, Service, Information, Organization)
 ├── Core concretes (18 anchors — see core-freeze.yaml)
 └── profile concepts (124 across 10 profiles), classified by membership, NOT by deep inheritance
```

**Type + composition + typed relationships** is preferred over deep class hierarchies (§8).
Inheritance depth never exceeds two levels below `Entity` except documented specialization
chains (e.g. `Agent ⊑ Actor`, `BaselineState ⊑ ArchitectureState`).

## 2. Concept kinds (§9)

Every class declares exactly one kind:

| Kind | Meaning | Instantiable? |
|---|---|---|
| `abstract: true` | Semantic anchor — no direct instances | no |
| `abstract: false` | Concrete concept | yes |
| profile-defined | Declared in a profile, not Core | yes, within the profile |
| derived | Computed from authoritative data (AssessmentGap, ArchitectureDelta, AgentOpportunity) | never hand-authored |
| deprecated | Scheduled for removal (see versioning.md) | no new usage |

## 3. Composition vs reference (§14)

- **Composition** (`dea:composes`): the child has no independent lifecycle from the parent
  (Decision → DecisionOption, AutonomyPolicy → AutonomyLevel, AgenticSystem → its parts).
- **Reference** (typed relationships): both sides keep independent identities and lifecycles
  (Agent `governed-by` Policy, Agent `authorized-by` Authority).

Never express both as generic nesting.

## 4. isA vs specializes vs implements (§15)

| Relationship | Meaning | Example |
|---|---|---|
| `isA` (RDF `subClassOf` in `ttl/`) | ontological class membership | AI Agent isA Agent |
| `dea:specializes` | semantic narrowing within the model | Agent specializes Actor; BaselineState specializes ArchitectureState |
| `dea:realizes`/`implements` | fulfillment of an abstraction | ApplicationComponent realizes BusinessCapability |

These are not interchangeable; using one for another is a semantic error (DEA-E-class).
