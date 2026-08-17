# Profile Mechanism (CR-8 §16-§17, §53-§55)

## What a profile is

The Core is extended through profiles — the mechanism that keeps Core small and stable (§55:
the "mega-model" failure pattern is putting finance/healthcare/AI/HR/… into Core).

A profile **may**: add concepts, add relationships, add properties, add constraints,
specialize concepts, define enumerations, define assessment dimensions.

A profile **must not**: silently redefine Core semantics (CR-4 §29, enforced by O002).

## Current profiles (v1.0.0)

| Profile | From | Contents |
|---|---|---|
| business, ecosystem, digital, data, technology, ai, governance, ecf | CR-4 | domain viewpoints |
| assessment | CR-5 | the generic assessment/measurement ontology |
| dmm | CR-5 | DMMv5 as an assessment lens (independently versioned) |
| lifecycle | CR-6 | temporal, state, lifecycle, transition, version, snapshot, delta |
| governance | CR-7 | intent, objective, policy, decision-structure, authority, delegation, governance bodies |
| agentic | CR-7 | agent, skill, tool, orchestration, autonomy, oversight, agentic systems |

Profiles declare explicit `depends_on` chains; circular dependencies fail conformance (O004).

## Declaring profile usage (§17)

Models declare the profiles they use in the model envelope; the validator then knows exactly
which semantic extensions apply:

```yaml
profiles:
  - dea:core@1.0.0
  - dea:assessment@1.0.0
  - dea:dmm@5.0.0
  - dea:agentic@1.0.0
```

## Third-party extensions (§53-§54)

External organizations extend OpenDEA **without modifying Core** under their own namespace:

```
OpenDEA Core
 └── ext:financial:  (RegulatoryRequirement, FinancialProduct, RiskExposure)
 └── ext:healthcare: (PatientCapability, ClinicalService, ClinicalPolicy)
```

Rules: unique namespace (`ext:<name>:`), explicit `depends_on`, no Core redefinition,
own versioning (§18-§19 compatibility rules apply at the extension boundary).
