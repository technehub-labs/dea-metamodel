# OpenDEA and DMM — the relationship (CR-10 §F)

> The two concepts are complementary and easily confused. This document is the
> canonical disambiguation.

## The one-sentence version

- **DMM measures:** how capable/mature is the enterprise?
- **OpenDEA represents:** what exists, how it is related, how it operates, and
  how it can change.

DMM is an **assessment/diagnostic instrument**. OpenDEA is the **semantic
architecture and transformation substrate** the diagnosis acts upon.

## The loop (CR-10 §F)

```
DMM
 │
 │ Assessment
 ↓
Maturity Gap
 │
 ↓
OpenDEA
 │
 │ Architecture + dependencies
 ↓
Transformation Options
 │
 ↓
Scenarios
 │
 ↓
Decision
 │
 ↓
Change
 │
 ↓
DMM Reassessment
```

A DMM score on its own says *"technology maturity is 2.8."* Connected to the
OpenDEA graph, the question becomes *"which technology weaknesses are
preventing strategic capabilities from reaching their target state?"* (CR-9Y)
— a much stronger proposition. With CR-10, DMM becomes a **transformation
decision mechanism**, not merely an assessment instrument (CR-10R):

```
DMM Assessment → Maturity Gap → Candidate Initiatives → Scenario
     → Projected Maturity → Investment Decision        (CR-10S)
```

## Projected maturity (CR-10R)

Scenario evaluation can project maturity movement:

```
Customer Capability
Current:     2.7
Scenario A:  3.5
Scenario B:  4.1
Target:      4.0
```

This is what lets a maturity model drive investment sequencing: each scenario
carries its projected maturity delta with uncertainty classes (CR-10O), never
as deterministic fact.

## Terrain semantics (CR-10AN/AO)

The DMM "enterprise terrain" concept maps naturally onto OpenDEA scenarios:

| Terrain element | Semantic meaning |
|---|---|
| Elevation | maturity |
| Heat | weakness / risk |
| Structures | capabilities |
| Infrastructure | technology / data |
| Roads | dependencies |
| Buildings | services / applications |
| Utilities | platforms / infrastructure |

Scenario mode then renders CURRENT TERRAIN → PROPOSED TERRAIN → DELTA —
"where should the enterprise build next?" in the city-planning metaphor
(CR-10AQ).

The six DMM dimensions — Strategy, Customer, Culture, Operations, Technology,
Data — are **semantic layers** underlying Capability, Architecture, Operating
Model and Transformation, not six colors on a map (CR-10AO).

## Heatmap discipline (CR-10AP)

A heatmap MUST distinguish five separate dimensions — never one ambiguous
"heat" value:

| Dimension | Example |
|---|---|
| Current maturity | 2.1 |
| Target maturity | 4.0 |
| Gap | 1.9 |
| Criticality | High |
| Risk | High |

## Where the semantics live

DMM-specific constructs (Pillar, Dimension, maturity scales) belong to the
**DMM profile**, never the Core (CR-10 §I, ADR-002). Assessment machinery
(Assessment, AssessmentResult, evidence, confidence) is profile-layer since
CR-5; the CR-10 scenario machinery references it without redefining it.
