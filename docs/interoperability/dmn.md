# DMN Interoperability (CR-9AD / CR-11Z)

> **KB note — DMN is the executable decision machinery most enterprise
> platforms already speak; OpenDEA's contribution is to govern the
> decision as a semantic object.** Companion to [bpmn.md](bpmn.md),
> [dmn.md](dmn.md) and [overview.md](overview.md).

## 1. Why DMN is the most relevant decision-engine mapping (CR-11Z §1)

CR-7 made `dea:Decision` first-class (authority, governance, evidence,
accountability). CR-9 added the runtime machinery. CR-10 layers
scenarios and recommendations on top. Almost every enterprise, in
parallel, already runs DMN decision services that **execute** decision
logic. The two belong together: a DMN engine *executes*; OpenDEA
*governs*. CR-9AD calls this out explicitly as **decision EXECUTION
vs decision SUPPORT**; CR-11Z is the vehicle that ties them into a
single, provable artefact.

```
CR-9AD — Decision EXECUTION vs Decision SUPPORT

  DMN engine        →  executes decision logic, returns a result
  OpenDEA runtime   →  governs the decision: who decides, on what
                       evidence, with what authority, recorded how

  The two are complementary, not duplicative. A conformant
  deployment can have one without the other; both together is the
  ideal: governed decision + auditable execution.
```

## 2. The mapping at a glance

The CR-8 §46 sketch set the shape:

```
OpenDEA Decision
       ↓
DMN Decision
       ↓
Decision Logic
       ↓
Decision Result
```

— with the explicit caveat that OpenDEA's `dea:Decision` is **broader**
than a DMN Decision because it also carries authority, governance,
enterprise context, architecture impact, change and accountability.
A DMN profile is the natural vehicle for a deployment that wants the
bridge; CR-11Z is the mapping file the profile will consult.

## 3. Mapping table

| DMN concept                          | OpenDEA concept(s)                                  | Relationship | Confidence | Lossiness   |
|--------------------------------------|-----------------------------------------------------|--------------|------------|-------------|
| Decision                             | `dea:Decision`                                      | Approximate  | high       | minor-loss  |
| Decision Logic (Hit Policy + Tables) | `dea:DecisionLogic` *(extension namespace)* / `dea:DecisionOption` × N | Composite | high | minor-loss |
| Input Data / Input Expression        | `dea:InformationClass` / `dea:DataEntity`           | Composite    | high       | minor-loss  |
| Output                               | `dea:Outcome` (with provenance)                     | Exact        | high       | lossless    |
| Business Knowledge Model             | `dea:KnowledgeAsset`                                | Approximate  | medium     | minor-loss  |
| Authority Requirement                | `dea:Authority` (CR-7 §25)                          | Approximate  | high       | lossless    |
| Knowledge Source                     | `dea:Evidence` + `dea:EvidenceSource`               | Composite    | high       | lossless    |
| Decision Service (deployment)        | `dea:ModelDeployment` (`kind = decision-service`)    | Exact        | high       | lossless    |
| DMN *Decision Result*                | `dea:DecisionRecord` + `dea:DecisionOutcome` profile | Exact        | high       | lossless    |
| Hit Policy                           | `dea:DecisionCriterion` (`method`, `weight`, `rule` fields) | Composite | high | minor-loss |

Notes on the rows that are not exact:

- **Decision (the top-level concept) is Approximate.** OpenDEA's
  `dea:Decision` has governance semantics DMN does not encode;
  projecting back to DMN drops governance, project to OpenDEA from
  DMN *adds* it (without inventing facts, by attaching real
  governance from authoritative sources).
- **Decision Logic is Composite.** A DMN decision table with
  hit-policy `FIRST` and N rules → one `dea:Decision` with N
  `dea:DecisionOption`s, each option carrying `priority` and
  `criterion_values` derived from the rule columns. This is
  exactly the CR-7 §14 decomposition.
- **Knowledge Source → Evidence.** OpenDEA's evidence layer is
  richer (CR-5 §17 — EvidenceArtifact, confidence, validity,
  assessor); DMN's *Knowledge Source* is a thin pointer. The
  mapping records the upstream-to-downside gap explicitly; see
  [provenance.md](provenance.md).
- **Hit Policy → Composite.** Rules with aggregation (SUM, MIN,
  MAX, COUNT, COLLECT) carry semantics not in the basic OpenDEA
  schema; the Decision Outcome profile carries aggregation kind
  and the resulting composite value.

## 4. The Decision Outcome profile (extension namespace)

CR-9AD's execution-vs-support split is realised in a profile:

```
profile: dea:decision-outcome@1.0.0
  kind: profile
  extends: [dea:core, dea:decision]
  types:
    - id: dea:DecisionOutcome
      definition: >-
        The recorded outcome of a Decision: result, supporting evidence,
        authority evaluation, the rule(s)/scenario option(s) that fired,
        the hit policy that aggregated them, the runner (engine, version,
        model_id), and the timestamp. First-class to support auditing;
        see provenance.md.
    - id: dea:DecisionExecutionRecord
      definition: >-
        The bridge artefact. Each execution of a governed decision
        produces one of these, attached via dea:produced to the
        dea:DecisionOutcome. Carries the engine identifier, the model
        version, inputs hash, output, latency and any human-in-the-loop
        annotations.
```

The profile lives in `specification/profiles/`; this note simply calls
out the *shape* of the bridge.

## 5. What conformance tests assert

The DMN tests under `/conformance/mapping-tests/` (see
[conformance.md](conformance.md)) cover:

- One canonical DMN sample (a loan-eligibility decision with two
  decision tables, an Authority Requirement, and a Knowledge
  Source) → OpenDEA → DMN. The Approximate row is a lossiness
  record, the Exact rows survive; Decision Logic's rules appear
  as `DecisionOption`s.
- A `decision-outcome@1.0.0` profile binding is honoured; running
  the same DMN model twice produces two `dea:DecisionExecutionRecord`s
  with distinct timestamps, shared `inputs_hash` semantics, and
  identical authority evaluation results (CR-9AD conformance).
- A governed decision (`dea:Decision` with `authority_policy_id`
  bound to a `dea:Policy`) cannot execute without a recorded
  authority evaluation result; the absence fails the test.

## 6. See also

- [bpmn.md](bpmn.md) — DMN and BPMN pair in execution stacks
- [archimate.md](archimate.md) — ArchiMate has no Decision; that's why this mapping exists
- [provenance.md](provenance.md) — Decision Outcome carries the Evidence chain
- [conformance.md](conformance.md) — Mapping class + Decision Outcome profile tests
- `docs/opendea-and-agents.md` — agent's view (CR-9AH `requestDecision`)
