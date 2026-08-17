# OpenDEA Relationship Catalogue (generated)

Version 1.0.0 — 104 relationship types. Canonical direction is source-to-target (CR-2 R002); inverses are query aliases.

| Relationship | Category | Inverse | Temporal | Definition |
|---|---|---|---|---|
| `dea:composes` | structural | `dea:part-of` | yes | The target is structurally part of the source and normally has a dependent lifecycle (composition, section 14). |
| `dea:aggregates` | structural | `dea:aggregated-in` | yes | The target participates in the source but retains an independent lifecycle (aggregation, section 14). |
| `dea:specializes` | structural | `dea:generalizes` | no | The source is a more specific form of the target (generalization/specialization hierarchy). |
| `dea:instantiates` | structural | `dea:instantiated-by` | yes | A concrete instance is created from a type or model (section 5). |
| `dea:part-of` | structural | `dea:composes` | yes | Inverse view of composes. Never stored as an independent relationship (section 8). [VIRTUAL inverse view — never stored] |
| `dea:realizes` | realization | `dea:realized-by` | yes | The source architectural element provides the realization of an abstract capability, service, or outcome (section 5). |
| `dea:implements` | realization | `dea:implemented-by` | yes | An implementation satisfies a specification, requirement, or design (section 5). Narrowed: not used for capability realization (use realizes) or technology enablement (use supports). |
| `dea:operationalizes` | realization | `dea:operationalized-by` | yes | A policy, tenet, or strategy is translated into operational practice (section 5). |
| `dea:depends-on` | dependency | `dea:depended-on-by` | yes | The source requires the target for some purpose, without containment or realization semantics (section 14). |
| `dea:requires` | dependency | `dea:required-by` | yes | The source cannot fulfil its definition without the target (mandatory dependency). |
| `dea:enables` | dependency | `dea:enabled-by` | yes | The source makes the target possible or materially more effective, without being required by it. |
| `dea:constrains` | dependency | `dea:constrained-by` | yes | The source limits the permissible design or behaviour space of the target. |
| `dea:flows-to` | flow | `dea:flows-from` | yes | Information, material, control, or value moves from the source to the target. |
| `dea:produces` | flow | `dea:produced-by` | yes | The source creates or emits the target as an output. |
| `dea:consumes` | flow | `dea:consumed-by` | yes | The source takes the target as an input it uses up or processes. |
| `dea:exchanges` | flow | `dea:exchanges` | yes | The source and target participate in a bidirectional exchange of value, data, or signals. |
| `dea:serves` | serving | `dea:served-by` | yes | The source delivers value or service to the target party or channel. |
| `dea:provides` | serving | `dea:provided-by` | yes | The source makes the target service or capability available to consumers. |
| `dea:uses` | serving | `dea:used-by` | yes | The source consumes the target service or resource as offered (usage, not depletion — contrast consumes). |
| `dea:exposes` | serving | `dea:exposed-via` | yes | The source presents the target as an accessible interface, product, or representation to consumers. |
| `dea:performs` | execution | `dea:performed-by` | yes | The source actor or organizational unit carries out the target process or function (section 12). |
| `dea:executes` | execution | `dea:executed-by` | yes | The source system function or component carries out the target process or activity automatically. |
| `dea:orchestrates` | execution | `dea:orchestrated-by` | yes | The source coordinates the execution ordering and interaction of the targets. |
| `dea:triggers` | execution | `dea:triggered-by` | yes | The source event or signal initiates the target process, experiment, or retraining. |
| `dea:governs` | governance | `dea:governed-by` | yes | The source directs, constrains, or oversees the target through policy, agreement, or strategy. |
| `dea:mandates` | governance | `dea:mandated-by` | yes | The source imposes a binding obligation on the target (regulatory or policy force). |
| `dea:controls` | governance | `dea:controlled-by` | yes | The source mitigates, protects against, or otherwise controls the target risk or exposure. |
| `dea:owns` | governance | `dea:owned-by` | yes | The source holds ownership of the target — accountability for its lifecycle and value. |
| `dea:accountable-for` | governance | `dea:accountable-to` | yes | The source holds single-point accountability for the target (RACI 'A'). |
| `dea:responsible-for` | governance | `dea:responsible-to` | yes | The source performs or manages the target day-to-day (RACI 'R'), including custodianship and role fulfilment. |
| `dea:threatens` | governance | `dea:threatened-by` | yes | The source risk exposes the target to potential harm or failure (risk relation, section 17 placement per D5). |
| `dea:represents` | information | `dea:represented-by` | no | One information representation corresponds to another conceptual entity (section 5). |
| `dea:informs` | information | `dea:informed-by` | yes | The source provides knowledge, evidence, or meaning that shapes the target (incl. semantic definition and weak influence — section 17). |
| `dea:curates` | information | `dea:curated-into` | yes | The source selects, organizes, and maintains the target as governed content or product. |
| `dea:publishes` | information | `dea:published-by` | yes | The source makes the target event or information available to subscribers. |
| `dea:subscribes-to` | information | `dea:subscribed-by` | yes | The source consumes publications of the target event or information feed. |
| `dea:trained-on` | information | `dea:training-of` | yes | The source AI/ML model is trained on the target data product or dataset. |
| `dea:derived-from` | information | `dea:derived-into` | yes | The source is derived from the target information, event, or actor knowledge (lineage). |
| `dea:assessed-by` | assessment | `dea:assesses` | yes | The source is evaluated by the target assessment instrument, experiment, or framework. |
| `dea:measured-by` | assessment | `dea:measures` | yes | The source's performance, health, or maturity is quantified by the target metric. |
| `dea:evidenced-by` | assessment | `dea:evidences` | yes | The source relationship or claim is supported by the target evidence artefact (section 6). |
| `dea:benchmarked-against` | assessment | `dea:benchmark-of` | yes | The source is compared against the target reference, standard, or peer. Extended by CR-5 §28: AssessmentResult vs BenchmarkReference (a benchmark is never a result, A011). |
| `dea:transitions-to` | transformation | `dea:transitions-from` | yes | The source evolves into the target state, maturity, or technology over time (CR-6 will add temporal semantics). |
| `dea:replaces` | transformation | `dea:replaced-by` | yes | The source takes over the function of the target, which is retired. |
| `dea:supersedes` | transformation | `dea:superseded-by` | yes | The source version or concept supersedes the target in definition or governance. |
| `dea:migrates-to` | transformation | `dea:migrated-from` | yes | The source is moved to the target platform, component, or state during a change initiative. |
| `dea:maps-to` | traceability | `dea:mapped-from` | yes | An explicit crosswalk or correspondence between two modelling systems or classification schemes (section 9). NOT a generic 'somehow related'. |
| `dea:traces-to` | traceability | `dea:traced-from` | yes | Audit lineage from the source to the target artefact that justifies or originates it. |
| `dea:supports` | dependency | `dea:supported-by` | yes | The source contributes to the target's function, funding, or effectiveness without realizing, enabling, or being required by it. |
| `dea:makes` | governance | `dea:made-by` | yes | An Actor or Organization makes (authors/commits to) a Decision (CR-4 §13/§20). |
| `dea:results-in` | transformation | `dea:resulting-from` | yes | A Decision or Change produces an Outcome (CR-4 §13/§17). |
| `dea:targets` | governance | `dea:targeted-by` | yes | A Decision or Change intends an Outcome (CR-4 §14). Resolves the parked CR-2 targets label: ChangeInitiative change-scope uses dea:affects. |
| `dea:affects` | transformation | `dea:affected-by` | yes | A Change modifies the state of an architectural element (CR-4 §17). Broad endpoint by design; profiles constrain further. |
| `dea:contributes-to` | realization | `dea:contributed-to-by` | yes | Partial causal contribution: a BusinessFunction contributes to a Capability; a Capability contributes to an Outcome (CR-4 §8/§14). |
| `dea:assesses` | assessment | `dea:assessed-by` | yes | The source assessment construct evaluates the target subject against a framework (CR-5 §4/§10/§23). DMM dimensions assess DEA concepts rather than replacing them. |
| `dea:conducted-under` | assessment | `dea:governs-assessment` | yes | An Assessment is conducted under exactly one AssessmentFramework (CR-5 §5; A001). |
| `dea:defines` | assessment | `dea:defined-by` | no | An AssessmentFramework or MaturityModel declares the target element as part of its methodology (CR-5 §5/§12) — dimensions, criteria, indicators, levels, scales and rules. |
| `dea:quantifies` | assessment | `dea:quantified-by` | yes | A Measure quantifies an Indicator or Observation (CR-5 §9/§27): Observation → Measure in the result chain. |
| `dea:derives-from` | assessment | `dea:feeds` | yes | The source is derived from the target: Score from Measure (CR-5 §11), AssessmentGap from current result and target (CR-5 §30), BenchmarkReference from Benchmark (CR-5 §28). Derived objects are never authoritative source data. |
| `dea:evaluated-by` | assessment | `dea:evaluates` | no | An AssessmentResult is produced under a declared AggregationRule or ScoringRule (CR-5 §26; A009) — arithmetic is never hard-coded into the ontology. |
| `dea:maps-onto` | assessment | `dea:mapped-from` | no | A ScoringRule, MaturityMappingRule or MaturityRule maps values onto MaturityLevels or Scales (CR-5 §11/§25): the framework defines the score→maturity transformation. |
| `dea:attains` | assessment | `dea:attained-by` | yes | An AssessmentResult attains a MaturityLevel, or an AssessmentTarget sets one as goal (CR-5 §13). Maturity is attributed through results, never stored on the architectural entity (A008). |
| `dea:addressed-by` | assessment | `dea:addresses` | yes | An AssessmentGap is addressed by a Change or ChangeInitiative (CR-5 §31): Assessment → Current State → Gap → Required Change → Target Architecture → Outcome. |
| `dea:scoped-by` | assessment | `dea:scopes` | no | An Assessment or AssessmentSubject is bounded by an explicit AssessmentScope (CR-5 §15). |
| `dea:refers-to` | assessment | `dea:referenced-by` | no | Generic reference from an assessment-layer object to a DEA entity (CR-5 §14/§15/§16): subjects and scopes reference actual enterprise entities rather than free-text labels. |
| `dea:originates-from` | assessment | `dea:origin-of` | yes | Evidence, EvidenceArtifacts, Measures and Observations originate from a declared EvidenceSource (CR-5 §16/§19 provenance). |
| `dea:valid-during` | temporal | `dea:validity-of` | yes | The source holds or is captured over the target TemporalInterval (CR-6 §9/§14/§19/§30). Valid time is distinct from transaction, observation, planned and effective time (§5). |
| `dea:contains` | structural | `dea:contained-in` | no | An ArchitectureState, Snapshot or Scenario contains architecture elements as members (CR-6 §9/§26/§30). Membership in a state — not structural composition (contrast dea:composes). |
| `dea:from-state` | temporal | `dea:origin-of-transition` | yes | The source transition, lifecycle transition or delta starts from the target state (CR-6 §14/§32). |
| `dea:to-state` | temporal | `dea:destination-of-transition` | yes | The source transition, lifecycle transition or delta arrives at the target state (CR-6 §14/§32). |
| `dea:caused-by` | temporal | `dea:causes` | yes | A Transition between architecture states is caused by a Change (CR-6 §14). Planned transitions caused by planned changes are never actual architecture (§16). |
| `dea:introduces` | transformation | `dea:introduced-by` | yes | A Change introduces a new architecture element into a state (CR-6 §15). |
| `dea:removes` | transformation | `dea:removed-by` | yes | A Change removes an architecture element from a state (CR-6 §15). History is preserved: removal is an event with temporal bounds, never a silent delete (§17). |
| `dea:modifies` | transformation | `dea:modified-by` | yes | A Change modifies an architecture element in place (CR-6 §15) — more specific than the broad dea:affects. |
| `dea:in-state` | temporal | `dea:state-of` | yes | The source entity is in the target LifecycleState over a temporal extent (CR-6 §7/§17). State history is preserved: Active 2024→2027, Retired effective 2027 — never overwritten (T005). |
| `dea:records` | temporal | `dea:recorded-by` | yes | A LifecycleEvent records something that happened to the target entity (CR-6 §28) — the auditable lifecycle history of the architecture. |
| `dea:captures` | temporal | `dea:captured-by` | yes | An ArchitectureSnapshot captures an ArchitectureState at a point in time (CR-6 §30). |
| `dea:may-become` | temporal | `dea:adopted-from` | yes | An ArchitectureSnapshot may be formally adopted as a BaselineState (CR-6 §31). Snapshot ≠ Baseline until adopted. |
| `dea:version-of` | structural | `dea:has-version` | no | A Version identifies one identity-evolution step of the target entity (CR-6 §19/§20). Distinct from lifecycle state and from supersession. |
| `dea:precedes` | temporal | `dea:follows` | no | A Version precedes the next Version in an entity's identity evolution (CR-6 §19). Version chains are acyclic (T008). |
| `dea:motivates` | governance | `dea:motivated-by` | no | An Intent motivates an Objective (CR-7 §4); objectives may decompose further. Composition is supported without a forced universal hierarchy. |
| `dea:seeks` | governance | `dea:sought-by` | no | An Intent or Objective seeks an Outcome (CR-7 §4/§6). Objective = intended; Outcome = actual. |
| `dea:constrained-by` | governance | `dea:constrains` | no | The source is limited or directed by a Policy, PolicyRule or Constraint (CR-7 §4/§9; G004/G008). Policy directs; Constraint limits — the two are not conflated (§9). |
| `dea:authorizes` | governance | `dea:authorized-by-decision` | yes | A Decision, Authority or GovernanceBody authorizes or directs a Change or Action (CR-7 §12/§35; G001). The decision authorizes the change; it does not constitute it (G003). |
| `dea:performed-by` | execution | `dea:performs` | yes | An Action is performed by an Actor or Agent (CR-7 §65): 'Agent Action' is Action + performed-by Agent, never a separate AgentAction type. |
| `dea:informed-by` | traceability | `dea:informs-decision` | no | A Decision or PolicyDecision is informed by Evidence (CR-7 §16; G002) — reusing the CR-5 Evidence ontology (assessment, measure, observation, simulation, forecast, benchmark, judgement, agent analysis) rather than a separate DecisionEvidence type. |
| `dea:delegates` | governance | `dea:delegated-to` | yes | An Actor or GovernanceBody delegates to another Actor or Agent (CR-7 §19/§51) — the delegation act; the Delegation entity carries scope, constraints, duration and revocation (G005). |
| `dea:grants` | governance | `dea:granted-to` | yes | A Delegation or Authority grants rights to an Actor or Agent (CR-7 §18/§19). |
| `dea:authorized-by` | governance | `dea:authorizes-party` | no | The source acts or decides under the target Authority or Delegation (CR-7 §18; G006/G010). Autonomous action must stay within delegated authority. |
| `dea:approves` | governance | `dea:approved-by` | yes | A GovernanceBody, Actor or Approval approves a Decision, Change or Action (CR-7 §25/§35). |
| `dea:establishes` | governance | `dea:established-by` | no | A GovernanceBody establishes a Policy or PolicyRule (CR-7 §35). |
| `dea:consults` | traceability | `dea:consulted-by` | no | The source consults the target in a decision or action context (CR-7 §37) — the 'C' in RACI-style semantics without making RACI itself foundational. |
| `dea:mitigates` | governance | `dea:mitigated-by` | yes | A Decision, Control or Change mitigates a Risk (CR-7 §42; G012). Decisions may also create, accept or transfer risk — mitigation is the control-bearing disposition. |
| `dea:escalates-to` | governance | `dea:escalated-from` | yes | An Action, Agent or Escalation escalates to an Actor or GovernanceBody when authority, confidence or policy boundaries are exceeded (CR-7 §25/§43; G011) — escalate or fail safely. |
| `dea:evaluates` | governance | `dea:evaluated-by-policy` | no | A PolicyEvaluation evaluates a Policy/PolicyRule against an Action or Agent (CR-7 §38), producing a PolicyDecision (permit/deny/escalate). |
| `dea:has-skill` | structural | `dea:skill-of` | no | An Agent possesses an AgentSkill (CR-7 §48/§50). AgentSkill ≠ BusinessCapability — a skill may implement or contribute to one (G014). |
| `dea:invokes` | execution | `dea:invoked-by` | yes | A Tool, Orchestrator or AgentSkill invokes a Service, API, Task or Agent (CR-7 §30/§46). |
| `dea:coordinates` | execution | `dea:coordinated-by` | yes | An Orchestrator coordinates Agents, Workflows, Tasks and Services toward a goal (CR-7 §46/§50). |
| `dea:enforces` | governance | `dea:enforced-by` | no | A Controller enforces Policies, PolicyRules or Constraints on execution (CR-7 §46). |
| `dea:permits` | governance | `dea:permitted-by` | no | An AgentProfile, AutonomyPolicy or ToolPermission permits an Action, Tool use or Skill invocation (CR-7 §24; G009/G014) — the positive half of the agent action boundary. |
| `dea:prohibits` | governance | `dea:prohibited-by` | no | An AgentProfile, AutonomyPolicy or ToolPermission prohibits an Action, Tool use or Skill invocation (CR-7 §24) — the negative half of the agent action boundary. |
| `dea:requires-approval` | governance | `dea:approval-for` | no | An Action, Tool use or Skill invocation requires an Approval or HumanOversight gate before or after execution (CR-7 §24/§25). |
| `dea:has-oversight` | governance | `dea:oversees` | no | An Agent or AgenticSystem operates under a HumanOversight pattern (CR-7 §25; G011). |
| `dea:accesses` | serving | `dea:accessed-by` | no | An Agent accesses Information, knowledge assets or Memory (CR-7 §32/§33) — reusing DEA information semantics rather than AgentKnowledge/AgentData duplicates. |
