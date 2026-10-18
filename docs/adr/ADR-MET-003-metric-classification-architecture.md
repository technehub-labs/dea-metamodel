# ADR-MET-003: Metric classification via the existing OpenDEAM classification architecture

- Status: Proposed
- Date: 2026-10-18
- Deciders: OpenDEA Metric capability programme
- Programme: CR-MET-000..012
- Source CR: CR-MET-002 (Metric Classification and Taxonomy)
- Supersedes: nothing
- Referenced by: CR-MET-002, CR-MET-008, CR-MET-009

## Context

The Metric capability requires a consistent classification framework
to support discovery, comparison, governance, analytics, and
interoperability. Six classification dimensions are in scope (per
user-supplied CR-MET-002 §3):

- Measurement subject (what the Metric measures)
- Measurement purpose (why the Metric is used)
- Measurement orientation (leading / lagging / diagnostic / concurrent)
- Measurement nature (quantitative / qualitative / categorical /
  ordinal / binary / composite)
- Measurement scope (enterprise / domain / unit / process / etc.)
- Management significance (KPI / KRI / KCI / SLI / etc.; see ADR-MET-008)

Four options were considered:

- A: introduce Metric-specific classification entities
  (`MetricSubject`, `MetricPurpose`, etc.) as new metamodel kinds.
- B: extend the existing `dea:Indicator` / `dea:Measure` / `dea:Score`
  / `dea:Result` / `dea:Target` / `dea:AggregationRule` entities
  (CR-5 §8..§25) with Metric classification fields.
- C: reuse the existing OpenDEAM classification metamodel (the
  classification concepts, classification schemes, and classification
  assignment relationships established in the canonical source) without
  introducing Metric-specific classification entities.
- D: collapse all six dimensions into a single `MetricKind` field
  on Metric.

Position A violates the ADR-013 anti-accumulation rule (no Metric-
specific concepts for symmetry) and duplicates the existing
classification architecture. Position B overloads existing entities
with Metric-specific fields and creates tight coupling. Position D
collapses orthogonal dimensions into one and loses the multidimensional
classification the user requires. Position C reuses the proven
classification architecture; classification is a cross-cutting concern
that does not require a Metric-specific mechanism.

The user-supplied CR-MET-002 §4 explicitly states: "The preferred
implementation should reuse the existing OpenDEAM classification
metamodel, rather than create a Metric-specific classification
mechanism. Where multiple classification schemes apply, their
assignments must remain independently identifiable."

The reconciliation CR (CR-MET-000 §4) records this disposition as
EXTEND for `dea:Indicator` (line 1835): Indicator stays in
`dea:assessment` profile; CR-MET-002 may add a `kind` discriminator
or repurpose Indicator as the assessment-side observation of a Metric.

## Decision

1. CR-MET-002 SHALL NOT introduce Metric-specific classification
   entities. The implementation reuses the existing OpenDEAM
   classification architecture (classification concepts, classification
   schemes, classification assignment relationships).
2. The six dimensions (subject, purpose, orientation, nature, scope,
   management significance) SHALL each be a classification scheme.
   Each scheme's values SHALL be classification concepts. Each
   assignment of a value to a Metric SHALL be a classification
   assignment relationship.
3. A Metric MAY have multiple subject classifications, multiple
   purpose classifications, multiple orientation classifications,
   multiple scope classifications, and multiple management-significance
   designations (see ADR-MET-008 for KPI/KRI/KCI designations).
4. A Metric MUST have a measurement-nature classification (per
   user-supplied CR-MET-002 §5).
5. Deprecated classifications SHALL remain historically traceable.
   Classification MUST NOT alter the fundamental identity of a Metric
   (changing a subject classification does not change the Metric id).
6. The `dea:Indicator` entity (line 1835; CR-5 §8) MAY be extended
   with a `kind` discriminator (e.g. `kind: observable | composite |
   diagnostic`) to support the measurement-orientation classification.
   The implementation decision is owned by CR-MET-002.
7. The management-significance dimension (KPI / KRI / KCI / SLI) is
   bound by ADR-MET-008 (governed designations, not specializations).
8. The classification assignments SHALL be independently identifiable
   per the existing OpenDEAM classification architecture: a Metric
   may carry zero or one assignment per (scheme, concept) pair; the
   scheme and concept references are part of the assignment.
9. No `MetricKind` field SHALL be added to Metric. The six
   classification dimensions are the binding axes.
10. The existing conformance test that validates classification
    assignment integrity SHALL be reused (extended if necessary for
    the new Metric-side use cases).

## Consequences

- Positive: ADR-013 anti-accumulation rule is preserved (no new
  Metric-specific classification concepts).
- Positive: the existing classification architecture is reused; no
  parallel classification mechanism.
- Positive: the six dimensions are orthogonal and independently
  classifiable; a Metric carries a vector of classifications.
- Positive: the user-supplied CR-MET-002 §4 directive is enforced at
  the ADR level.
- Positive: classification extensions and deprecations follow the
  existing classification governance, not a Metric-specific regime.
- Negative: the implementation must extend the existing
  classification-scheme registry to declare the six new schemes; the
  existing tests must be extended to validate the new schemes.
- Forecloses: Metric-specific classification entities (Position A);
  Indicator/Measure overload (Position B); single-field collapse
  (Position D).

## References

- CR-MET-002 (Metric Classification and Taxonomy).
- CR-MET-000 §4 disposition table (dea:Indicator EXTEND).
- ADR-013 (Core non-accumulation).
- metamodel/dea-metamodel.yaml line 1835 (current dea:Indicator).
- Existing OpenDEAM classification metamodel (classification concepts,
  schemes, assignment relationships).
- User-supplied CR-MET-002 §4 directive.
- ADR-MET-008 (KPI/KRI/KCI designations).
