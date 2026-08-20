The next implementation artifact should be the OpenDEA Assessment Metamodel v1: the canonical conceptual model, its PlantUML representation, and the corresponding schema structure. I would deliberately keep v1 small enough to retrofit onto the existing repositories while establishing the extension points needed for capability assessment, maturity, benchmarking, evidence, and longitudinal results.

1. Target dea-metamodel repository

I recommend creating:

dea-metamodel/
├── README.md
├── model/
│   ├── assessment-metamodel.puml
│   ├── assessment-metamodel.svg
│   └── assessment-metamodel.png
├── schemas/
│   ├── common.schema.json
│   ├── assessment-model.schema.json
│   ├── assessment-instrument.schema.json
│   ├── assessment-execution.schema.json
│   ├── assessment-result.schema.json
│   ├── capability.schema.json
│   ├── scenario.schema.json
│   ├── measure.schema.json
│   ├── evidence.schema.json
│   ├── scoring-model.schema.json
│   ├── compatibility.schema.json
│   └── relationship.schema.json
├── vocabulary/
│   ├── assessment-types.yaml
│   ├── relationship-types.yaml
│   ├── lifecycle-status.yaml
│   └── evidence-types.yaml
├── examples/
│   ├── assessment-model.yaml
│   ├── capability.yaml
│   ├── scenario.yaml
│   ├── assessment-result.yaml
│   └── benchmark-eligibility.yaml
└── governance/
    ├── versioning.md
    ├── compatibility.md
    └── lifecycle.md

The key architectural decision is that dea-metamodel becomes the stable contract, while the existing assessment repositories remain content repositories.

⸻

2. Canonical PlantUML

This is the first implementation-ready version I would use.

@startuml OpenDEA_Assessment_Metamodel
title OpenDEA Assessment Metamodel v1
skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam classAttributeIconSize 0
skinparam linetype ortho
skinparam packageStyle rectangle
skinparam class {
    BackgroundColor #F8FAFC
    BorderColor #334155
    ArrowColor #475569
    FontColor #0F172A
}
skinparam package {
    BackgroundColor #FFFFFF
    BorderColor #CBD5E1
    FontColor #0F172A
}
' ============================================================
' CORE ASSESSMENT
' ============================================================
package "Assessment Core" {
    class AssessmentModel {
        +id : Identifier
        +name : String
        +version : Version
        +purpose : AssessmentPurpose[*]
        +subjectType : SubjectType
        +status : LifecycleStatus
        +description : String
        +metamodelVersion : Version
    }
    class AssessmentInstrument {
        +id : Identifier
        +version : Version
        +name : String
        +instrumentType : InstrumentType
        +status : LifecycleStatus
    }
    class AssessmentExecution {
        +id : Identifier
        +startedAt : DateTime
        +completedAt : DateTime
        +status : ExecutionStatus
    }
    class AssessmentResult {
        +id : Identifier
        +status : ResultStatus
        +assessmentPeriod : Period
        +confidence : Confidence
        +createdAt : DateTime
    }
    class AssessmentDimension {
        +id : Identifier
        +name : String
        +description : String
        +weight : Decimal
    }
    class AssessmentQuestion {
        +id : Identifier
        +version : Version
        +text : String
        +required : Boolean
        +weight : Decimal
    }
}
' ============================================================
' CAPABILITY
' ============================================================
package "Capability Model" {
    class Capability {
        +id : Identifier
        +name : String
        +version : Version
        +description : String
        +status : LifecycleStatus
    }
    class CapabilityOutcome {
        +id : Identifier
        +name : String
        +description : String
    }
    class CapabilityDependency {
        +relationshipType : DependencyType
    }
}
' ============================================================
' SCENARIO
' ============================================================
package "Scenario Model" {
    class Scenario {
        +id : Identifier
        +name : String
        +version : Version
        +description : String
        +status : LifecycleStatus
    }
    class ScenarioContext {
        +id : Identifier
        +name : String
        +value : String
    }
    class ScenarioOutcome {
        +id : Identifier
        +name : String
        +description : String
    }
}
' ============================================================
' MEASUREMENT
' ============================================================
package "Measurement Model" {
    class Measure {
        +id : Identifier
        +name : String
        +version : Version
        +definition : String
        +unit : String
        +status : LifecycleStatus
    }
    class MeasurementRule {
        +id : Identifier
        +expression : String
        +method : String
    }
    class Observation {
        +id : Identifier
        +value : String
        +observedAt : DateTime
        +confidence : Confidence
    }
}
' ============================================================
' EVIDENCE
' ============================================================
package "Evidence Model" {
    class EvidenceRequirement {
        +id : Identifier
        +name : String
        +required : Boolean
        +description : String
    }
    class Evidence {
        +id : Identifier
        +type : EvidenceType
        +description : String
        +source : String
        +capturedAt : DateTime
        +confidence : Confidence
    }
    class EvidenceProvenance {
        +sourceType : String
        +sourceId : String
        +capturedBy : String
        +capturedAt : DateTime
    }
}
' ============================================================
' SCORING
' ============================================================
package "Scoring Model" {
    class ScoringModel {
        +id : Identifier
        +name : String
        +version : Version
        +description : String
        +status : LifecycleStatus
    }
    class ScoringRule {
        +id : Identifier
        +expression : String
        +weight : Decimal
    }
    class Score {
        +value : Decimal
        +normalizedValue : Decimal
        +scale : String
    }
}
' ============================================================
' MATURITY
' ============================================================
package "Maturity Model" {
    class MaturityModel {
        +id : Identifier
        +name : String
        +version : Version
        +description : String
        +status : LifecycleStatus
    }
    class MaturityLevel {
        +id : Identifier
        +level : Integer
        +name : String
        +description : String
    }
    class MaturityCriterion {
        +id : Identifier
        +description : String
        +threshold : Decimal
    }
}
' ============================================================
' BENCHMARK
' ============================================================
package "Benchmark Model" {
    class BenchmarkModel {
        +id : Identifier
        +name : String
        +version : Version
        +description : String
        +status : LifecycleStatus
    }
    class BenchmarkPopulation {
        +id : Identifier
        +name : String
        +description : String
    }
    class ComparabilityRule {
        +id : Identifier
        +expression : String
        +description : String
    }
    class BenchmarkResult {
        +score : Decimal
        +percentile : Decimal
        +rank : Integer
        +sampleSize : Integer
        +status : BenchmarkStatus
    }
}
' ============================================================
' MODEL GOVERNANCE
' ============================================================
package "Model Governance" {
    class ModelLineage {
        +previousVersion : Version
        +changeType : ChangeType
        +supersedes : Identifier[*]
    }
    class Compatibility {
        +backwardCompatible : Boolean
        +scoringCompatible : Boolean
        +maturityCompatible : Boolean
        +benchmarkCompatible : Boolean
        +resultCompatible : Boolean
    }
}
' ============================================================
' CORE RELATIONSHIPS
' ============================================================
AssessmentModel "1" o-- "1..*" AssessmentDimension : defines
AssessmentDimension "1" o-- "0..*" AssessmentQuestion : contains
AssessmentModel "1" --> "1..*" Capability : assesses
AssessmentModel "0..*" --> "0..*" Scenario : applicable to
AssessmentModel "1" --> "0..*" Measure : measures
AssessmentModel "1" --> "0..*" EvidenceRequirement : requires
AssessmentModel "1" --> "0..1" ScoringModel : uses
AssessmentModel "0..*" --> "0..*" MaturityModel : may interpret with
AssessmentModel "0..*" --> "0..*" BenchmarkModel : may support
AssessmentInstrument "1" --> "1" AssessmentModel : implements
AssessmentExecution "1" --> "1" AssessmentInstrument : executes
AssessmentExecution "1" --> "1" Scenario : occurs in
AssessmentExecution "1" --> "1" AssessmentResult : produces
AssessmentResult "1" --> "1" AssessmentModel : conforms to
AssessmentResult "1" --> "1..*" Observation : contains
AssessmentResult "1" --> "0..*" Evidence : supported by
AssessmentResult "1" --> "0..*" Score : produces
AssessmentResult "1" --> "0..*" MaturityLevel : interpreted as
AssessmentResult "1" --> "0..*" BenchmarkResult : produces
AssessmentResult "1" --> "0..*" Finding : identifies
Observation "1" --> "1" Measure : measures
Observation "1" --> "0..*" Evidence : supported by
Measure "1" --> "0..*" MeasurementRule : measured by
Capability "1" o-- "0..*" CapabilityOutcome : produces
Capability "0..*" --> "0..*" Capability : depends on
Scenario "1" o-- "0..*" ScenarioContext : defined by
Scenario "1" o-- "0..*" ScenarioOutcome : produces
Evidence "1" --> "0..1" EvidenceProvenance : has
ScoringModel "1" o-- "1..*" ScoringRule : defines
ScoringRule "1" --> "0..*" Score : produces
MaturityModel "1" o-- "1..*" MaturityLevel : defines
MaturityLevel "1" o-- "0..*" MaturityCriterion : evaluated by
BenchmarkModel "1" --> "1" BenchmarkPopulation : applies to
BenchmarkModel "1" o-- "1..*" ComparabilityRule : defines
BenchmarkResult "1" --> "1" BenchmarkModel : generated by
AssessmentModel "1" --> "0..1" ModelLineage : has
AssessmentModel "1" --> "0..1" Compatibility : declares
' ============================================================
' FINDINGS
' ============================================================
class Finding {
    +id : Identifier
    +type : FindingType
    +severity : Severity
    +description : String
    +recommendation : String
}
' ============================================================
' ENUMERATIONS
' ============================================================
enum AssessmentPurpose {
    enterprise-health
    capability-assessment
    maturity-assessment
    diagnostic
    baseline
    readiness
    scenario
    comparative
    benchmark
    compliance
}
enum LifecycleStatus {
    draft
    experimental
    alpha
    beta
    stable
    deprecated
    retired
}
enum ChangeType {
    major
    minor
    patch
}
enum Confidence {
    low
    medium
    high
}
enum BenchmarkStatus {
    eligible
    not-comparable
    insufficient-data
    provisional
}
enum Severity {
    informational
    low
    medium
    high
    critical
}
@enduml

⸻

3. One deliberate addition: AssessmentExecution

I would retain this concept even though it was not emphasized as strongly in the previous CR.

It provides a clean distinction between:

Assessment Model

and:

an assessment actually performed on Organization X

For example:

AssessmentModel
    API Capability Assessment v2.1
        ↓ implements
AssessmentInstrument
    Facilitated Workshop v1.0
        ↓ executes
AssessmentExecution
    EXEC-2026-00431
        ↓ produces
AssessmentResult
    RESULT-2026-00431

That distinction becomes essential once OpenDEA supports repeated assessments.

⸻

4. Assessment Model JSON Schema

The canonical schema should be deliberately conservative in v1.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://assessment-models.github.io/dea-metamodel/schemas/assessment-model.schema.json",
  "title": "OpenDEA Assessment Model",
  "type": "object",
  "required": [
    "id",
    "name",
    "version",
    "metamodel_version",
    "type",
    "purpose",
    "subject_type"
  ],
  "properties": {
    "id": {
      "$ref": "common.schema.json#/$defs/identifier"
    },
    "name": {
      "type": "string",
      "minLength": 1
    },
    "version": {
      "$ref": "common.schema.json#/$defs/version"
    },
    "metamodel_version": {
      "$ref": "common.schema.json#/$defs/version"
    },
    "type": {
      "const": "assessment-model"
    },
    "purpose": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/assessmentPurpose"
      },
      "minItems": 1,
      "uniqueItems": true
    },
    "subject_type": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "status": {
      "$ref": "common.schema.json#/$defs/lifecycleStatus"
    },
    "capabilities": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/modelReference"
      }
    },
    "scenarios": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/modelReference"
      }
    },
    "dimensions": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/dimension"
      }
    },
    "measures": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/modelReference"
      }
    },
    "evidence_requirements": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/modelReference"
      }
    },
    "scoring_model": {
      "$ref": "common.schema.json#/$defs/modelReference"
    },
    "maturity_models": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/modelReference"
      }
    },
    "benchmark_models": {
      "type": "array",
      "items": {
        "$ref": "common.schema.json#/$defs/modelReference"
      }
    },
    "lineage": {
      "$ref": "common.schema.json#/$defs/lineage"
    },
    "compatibility": {
      "$ref": "common.schema.json#/$defs/compatibility"
    }
  },
  "$defs": {
    "dimension": {
      "type": "object",
      "required": [
        "id",
        "name"
      ],
      "properties": {
        "id": {
          "$ref": "common.schema.json#/$defs/identifier"
        },
        "name": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "weight": {
          "type": "number",
          "minimum": 0
        },
        "questions": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/question"
          }
        }
      },
      "additionalProperties": false
    },
    "question": {
      "type": "object",
      "required": [
        "id",
        "text"
      ],
      "properties": {
        "id": {
          "$ref": "common.schema.json#/$defs/identifier"
        },
        "version": {
          "$ref": "common.schema.json#/$defs/version"
        },
        "text": {
          "type": "string"
        },
        "required": {
          "type": "boolean",
          "default": true
        },
        "weight": {
          "type": "number",
          "minimum": 0
        },
        "measure": {
          "$ref": "common.schema.json#/$defs/modelReference"
        },
        "evidence_requirements": {
          "type": "array",
          "items": {
            "$ref": "common.schema.json#/$defs/modelReference"
          }
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}

⸻

5. Common Schema

This is where the versioning architecture becomes important.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://assessment-models.github.io/dea-metamodel/schemas/common.schema.json",
  "$defs": {
    "identifier": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9][a-zA-Z0-9._:-]*$"
    },
    "version": {
      "type": "string",
      "pattern": "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$"
    },
    "modelReference": {
      "type": "object",
      "required": [
        "id"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/identifier"
        },
        "version": {
          "$ref": "#/$defs/version"
        }
      },
      "additionalProperties": false
    },
    "assessmentPurpose": {
      "type": "string",
      "enum": [
        "enterprise-health",
        "capability-assessment",
        "maturity-assessment",
        "diagnostic",
        "baseline",
        "readiness",
        "scenario",
        "comparative",
        "benchmark",
        "compliance"
      ]
    },
    "lifecycleStatus": {
      "type": "string",
      "enum": [
        "draft",
        "experimental",
        "alpha",
        "beta",
        "stable",
        "deprecated",
        "retired"
      ]
    },
    "changeType": {
      "type": "string",
      "enum": [
        "major",
        "minor",
        "patch"
      ]
    },
    "lineage": {
      "type": "object",
      "properties": {
        "previous_version": {
          "$ref": "#/$defs/version"
        },
        "change_type": {
          "$ref": "#/$defs/changeType"
        },
        "supersedes": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/identifier"
          }
        }
      },
      "additionalProperties": false
    },
    "compatibility": {
      "type": "object",
      "required": [
        "backward_compatible",
        "scoring_compatible",
        "maturity_compatible",
        "benchmark_compatible",
        "result_compatible"
      ],
      "properties": {
        "backward_compatible": {
          "type": "boolean"
        },
        "scoring_compatible": {
          "type": "boolean"
        },
        "maturity_compatible": {
          "type": "boolean"
        },
        "benchmark_compatible": {
          "type": "boolean"
        },
        "result_compatible": {
          "type": "boolean"
        }
      },
      "additionalProperties": false
    }
  }
}

⸻

6. Assessment Result Schema

This is arguably the most important new schema.

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://assessment-models.github.io/dea-metamodel/schemas/assessment-result.schema.json",
  "title": "OpenDEA Assessment Result",
  "type": "object",
  "required": [
    "id",
    "assessment_model",
    "subject",
    "assessment_period",
    "status"
  ],
  "properties": {
    "id": {
      "$ref": "common.schema.json#/$defs/identifier"
    },
    "assessment_model": {
      "$ref": "common.schema.json#/$defs/modelReference"
    },
    "assessment_instrument": {
      "$ref": "common.schema.json#/$defs/modelReference"
    },
    "subject": {
      "type": "object",
      "required": [
        "id",
        "type"
      ],
      "properties": {
        "id": {
          "type": "string"
        },
        "type": {
          "type": "string"
        },
        "name": {
          "type": "string"
        }
      }
    },
    "scenario": {
      "$ref": "common.schema.json#/$defs/modelReference"
    },
    "assessment_period": {
      "type": "object",
      "required": [
        "start"
      ],
      "properties": {
        "start": {
          "type": "string",
          "format": "date-time"
        },
        "end": {
          "type": "string",
          "format": "date-time"
        }
      }
    },
    "observations": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/observation"
      }
    },
    "scores": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/score"
      }
    },
    "maturity": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/maturityResult"
      }
    },
    "benchmark": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/benchmarkResult"
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/finding"
      }
    },
    "confidence": {
      "type": "string",
      "enum": [
        "low",
        "medium",
        "high"
      ]
    },
    "status": {
      "type": "string",
      "enum": [
        "draft",
        "in-progress",
        "completed",
        "validated",
        "superseded"
      ]
    }
  },
  "$defs": {
    "observation": {
      "type": "object",
      "required": [
        "id",
        "measure",
        "value"
      ],
      "properties": {
        "id": {
          "type": "string"
        },
        "measure": {
          "$ref": "common.schema.json#/$defs/modelReference"
        },
        "value": {},
        "observed_at": {
          "type": "string",
          "format": "date-time"
        },
        "evidence": {
          "type": "array",
          "items": {
            "$ref": "common.schema.json#/$defs/modelReference"
          }
        }
      }
    },
    "score": {
      "type": "object",
      "required": [
        "value"
      ],
      "properties": {
        "dimension": {
          "$ref": "common.schema.json#/$defs/identifier"
        },
        "value": {
          "type": "number"
        },
        "normalized_value": {
          "type": "number"
        },
        "scale": {
          "type": "string"
        }
      }
    },
    "maturityResult": {
      "type": "object",
      "required": [
        "model",
        "level"
      ],
      "properties": {
        "model": {
          "$ref": "common.schema.json#/$defs/modelReference"
        },
        "level": {
          "type": "integer",
          "minimum": 1
        }
      }
    },
    "benchmarkResult": {
      "type": "object",
      "required": [
        "model",
        "status"
      ],
      "properties": {
        "model": {
          "$ref": "common.schema.json#/$defs/modelReference"
        },
        "status": {
          "enum": [
            "eligible",
            "not-comparable",
            "insufficient-data",
            "provisional"
          ]
        },
        "percentile": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "rank": {
          "type": "integer",
          "minimum": 1
        },
        "sample_size": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "finding": {
      "type": "object",
      "required": [
        "id",
        "description"
      ],
      "properties": {
        "id": {
          "type": "string"
        },
        "type": {
          "type": "string"
        },
        "severity": {
          "enum": [
            "informational",
            "low",
            "medium",
            "high",
            "critical"
          ]
        },
        "description": {
          "type": "string"
        },
        "recommendation": {
          "type": "string"
        }
      }
    }
  }
}

⸻

7. Example: Existing Instrument Transformed

The important point is that an existing instrument does not need to be rewritten immediately.

A current-style instrument can continue looking conceptually like:

id: dea-assessment-technology
name: Technology Assessment
domain: technology
version: 1.0.0
metamodel_version: 0.1.0
maturity_target:
  id: dea-maturity-technology
dimensions:
  - id: architecture
    name: Architecture
    questions:
      - id: architecture-01
        text: ...

The migration layer interprets it as:

type: assessment-model
capabilities:
  - id: dea:capability-technology-architecture
maturity_models:
  - id: dea:maturity-technology
dimensions:
  - id: architecture

Nothing is lost.

⸻

8. Example: New Canonical Instrument

The same assessment can eventually become:

id: dea:assessment-technology
name: Technology Assessment
type: assessment-model
version: 2.0.0
metamodel_version: 1.0.0
purpose:
  - enterprise-health
  - capability-assessment
  - diagnostic
subject_type: enterprise
status: stable
capabilities:
  - id: dea:capability-technology-architecture
    version: 1.0.0
  - id: dea:capability-technology-platform
    version: 1.0.0
  - id: dea:capability-technology-lifecycle
    version: 1.0.0
dimensions:
  - id: architecture
    name: Architecture
    weight: 0.25
  - id: platform
    name: Platform
    weight: 0.25
  - id: lifecycle
    name: Technology Lifecycle
    weight: 0.25
  - id: technical-debt
    name: Technical Debt
    weight: 0.25
measures:
  - id: dea:measure-architecture-standardization
    version: 1.0.0
  - id: dea:measure-platform-reuse
    version: 1.0.0
scoring_model:
  id: dea:scoring-four-point
  version: 1.0.0
maturity_models:
  - id: dea:maturity-technology
    version: 1.0.0
compatibility:
  backward_compatible: true
  scoring_compatible: true
  maturity_compatible: true
  benchmark_compatible: false
  result_compatible: true

Notice the critical difference:

The assessment no longer owns the capability or maturity definition.

It references them.

⸻

9. Example: Scenario-Based Capability Assessment

This is where the model begins to unlock the benchmarking objective.

id: dea:assessment-zero-touch-operations
name: Zero Touch Operations Capability Assessment
type: assessment-model
version: 1.0.0
metamodel_version: 1.0.0
purpose:
  - capability-assessment
  - scenario
  - comparative
subject_type: enterprise
capabilities:
  - id: dea:capability-automation
    version: 1.0.0
  - id: dea:capability-self-governance
    version: 1.0.0
  - id: dea:capability-self-adaptation
    version: 1.0.0
scenarios:
  - id: dea:scenario-zero-touch-service-assurance
    version: 1.0.0
measures:
  - id: dea:measure-automation-rate
    version: 1.0.0
  - id: dea:measure-closed-loop-rate
    version: 1.0.0
  - id: dea:measure-human-intervention-rate
    version: 1.0.0
scoring_model:
  id: dea:scoring-four-point
  version: 1.0.0
maturity_models: []
benchmark_models:
  - id: dea:benchmark-zero-touch-operations
    version: 1.0.0

This assessment does not require a maturity model.

That is an important proof point for the new metamodel.

⸻

10. Example Assessment Result

id: dea:result:2026:000184
assessment_model:
  id: dea:assessment-zero-touch-operations
  version: 1.0.0
assessment_instrument:
  id: dea:instrument-zero-touch-workshop
  version: 1.0.0
subject:
  id: enterprise-001
  type: enterprise
  name: Enterprise A
scenario:
  id: dea:scenario-zero-touch-service-assurance
  version: 1.0.0
assessment_period:
  start: "2026-07-01T00:00:00Z"
  end: "2026-07-31T23:59:59Z"
status: validated
confidence: high
observations:
  - id: obs-001
    measure:
      id: dea:measure-automation-rate
      version: 1.0.0
    value: 78
    observed_at: "2026-07-31T12:00:00Z"
  - id: obs-002
    measure:
      id: dea:measure-closed-loop-rate
      version: 1.0.0
    value: 63
    observed_at: "2026-07-31T12:00:00Z"
scores:
  - dimension: automation
    value: 3.1
    normalized_value: 77.5
    scale: "0-4"
  - dimension: self-governance
    value: 2.8
    normalized_value: 70
    scale: "0-4"
benchmark:
  - model:
      id: dea:benchmark-zero-touch-operations
      version: 1.0.0
    status: eligible
    percentile: 81
    sample_size: 47

Now the result is independently useful.

It can be displayed as:

* enterprise heatmap;
* capability profile;
* scenario result;
* benchmark position;
* trend against prior assessment.

⸻

11. The Critical Versioning Pattern

This should become a hard architectural rule.

Never store:

assessment_model: dea:assessment-technology

alone in a finalized result.

Store:

assessment_model:
  id: dea:assessment-technology
  version: 2.1.0

Likewise:

capability:
  id: dea:capability-api-management
  version: 1.3.0

This makes every result reproducible.

⸻

12. Component Graph

The resulting dependency graph becomes:

                         Assessment Model
                               |
          +--------------------+-------------------+
          |                    |                   |
          ▼                    ▼                   ▼
     Capability            Scenario            Measure
       Model                 Model              Model
          |                    |                   |
          +--------------------+-------------------+
                               |
                               ▼
                         Scoring Model
                               |
                               ▼
                         Assessment
                         Instrument
                               |
                               ▼
                         Assessment
                         Execution
                               |
                               ▼
                         Assessment
                           Result
                               |
               +---------------+---------------+
               |               |               |
               ▼               ▼               ▼
          Maturity Model  Benchmark Model   Findings

This is the architectural mechanism that allows incremental change without tearing down existing content.

⸻

13. What Should Not Be in the Metamodel v1

I would explicitly resist adding these initially:

* organization ontology;
* enterprise architecture ontology;
* business process ontology;
* complex statistical benchmark algorithms;
* AI assessor ontology;
* recommendation ontology;
* remediation workflow;
* value realization model.

Those can consume Assessment Results later.

The metamodel should establish the measurement contract, not become an enterprise mega-ontology.

⸻

14. Immediate Migration Mapping

The first pilot should take the existing instrument.schema.json and map it as follows:

CURRENT                         METAMODEL v1
instrument
   │
   ├── id                  → AssessmentModel.id
   ├── name                → AssessmentModel.name
   ├── version             → AssessmentModel.version
   ├── domain              → classification metadata
   ├── maturity_target     → maturity_models[]
   ├── dimensions          → dimensions[]
   │     └── questions     → AssessmentQuestion
   └── relationships       → registered relationships

The current scoring rubric becomes:

scoring-rubric.md
        ↓
dea:scoring-four-point@1.0.0

And the existing maturity target becomes:

maturity_target
        ↓
MaturityModel Reference

This is an additive migration, not a rewrite.

⸻

15. Recommended GitHub Implementation Sequence

I would implement the actual repository in this order:

Commit 1 — Repository foundation

dea-metamodel/
├── README.md
├── LICENSE
├── model/
└── schemas/

Commit 2 — Core UML

Add:

assessment-metamodel.puml

Commit 3 — Common schema

Add:

common.schema.json

Commit 4 — Assessment model

Add:

assessment-model.schema.json

Commit 5 — Result model

Add:

assessment-result.schema.json

Commit 6 — Component schemas

Add:

capability.schema.json
scenario.schema.json
measure.schema.json
evidence.schema.json
scoring-model.schema.json

Commit 7 — Governance

Add:

compatibility.md
versioning.md
lifecycle.md

Commit 8 — Pilot migration

Update one existing assessment instrument to reference the new metamodel.

Commit 9 — Validation

Add CI that validates both:

legacy instrument

and:

canonical assessment model

Commit 10 — Maturity integration

Modify dea-catalog-maturity-models to consume the new model reference semantics.

⸻

16. The Key Architectural Test

Before migrating all existing repositories, the following four scenarios should work.

Test A — Enterprise Heatmap

Enterprise
 → Multiple Capabilities
 → Assessment Results
 → Heatmap

Test B — Capability Assessment

Organization
 → Capability
 → Scenario
 → Assessment
 → Result

Test C — Maturity Assessment

Capability
 → Assessment
 → Result
 → Maturity Model
 → Level

Test D — Benchmark

Organization A ─┐
Organization B ─┼─ Scenario
Organization C ─┤  Capability
Organization D ─┘  Assessment Model
                   ↓
               Benchmark

If the metamodel handles all four without special-case constructs, the metamodel is doing its job.

⸻

The most important implementation decision

I would make one further refinement to the previous CR:

AssessmentModel should be the central contract, not AssessmentInstrument.

The hierarchy should be:

             AssessmentModel
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
 Capability      Scenario      Measures
       │            │            │
       └────────────┼────────────┘
                    ▼
             AssessmentMethod
                    │
                    ▼
          AssessmentInstrument
                    │
                    ▼
          AssessmentExecution
                    │
                    ▼
            AssessmentResult
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    MaturityModel       BenchmarkModel

That gives OpenDEA a stable semantic spine. Instruments can change, questions can evolve, maturity models can be replaced, scenarios can be added, and benchmark populations can change—while the underlying assessment result remains traceable to the exact models that generated it.

The next artifact after this should therefore be a repository-ready dea-metamodel package, consisting of the PlantUML above, complete JSON Schemas, vocabulary files, three canonical YAML examples, and a migration mapping for the existing dea-catalog-assessment-tools schema. That is the point at which this design can be dropped directly into GitHub and validated against the current repository contents.