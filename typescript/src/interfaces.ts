// DEA Metamodel : TypeScript Interfaces
// Auto-generated from schemas/entities/*.json
// Do not edit manually : regenerate with: npm run generate

// Canonical metamodel version this artifact derives from (CR-001).
export const METAMODEL_VERSION = '1.0.0';

// v0.2.0 (ADR-0002): architecture layers L1-L5. Measurement is a
// cross-cutting dimension, not a layer : Metrics carry scope_layers.
export type ArchitectureLayerId = 'L1' | 'L2' | 'L3' | 'L4' | 'L5';

export type EntityStatus = 'draft' | 'candidate' | 'approved' | 'deprecated';
// v1.0.0-alpha: Relationship type vocabulary. CamelCase to match
// ttl/dea-metamodel-ontology.ttl ObjectProperty declarations and
// metamodel.yaml relationships[].
export type RelationshipType =
  | 'mapsTo'
  | 'realizes'
  | 'implements'
  | 'influencedBy'
  | 'decomposes'
  | 'orchestrates'
  | 'consumes'
  | 'provides'
  | 'governs'
  | 'measuredBy';

export interface EntityMetadata {
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  status?: EntityStatus;
}

export interface RelationshipInstance {
  source_id: string;
  target_id: string;
  relationship_type: RelationshipType;
  description?: string;
  weight?: number;
  provenance?: string;
  bidirectional?: boolean;
}

export interface BaseEntity {
  id: string;
  type: string;
  name: string;
  description?: string;
  version: string;
  tags?: string[];
  relationships?: RelationshipInstance[];
  metadata?: EntityMetadata;
}

// ─── Entity Sub-types ───────────────────────────────────────

// v1.0.0-alpha: Stakeholder (SH) : external/affected parties.
// Mirrors schemas/entities/stakeholder.json. Catalog:
// technehub-labs/dea-catalog-stakeholders.
export type StakeholderType =
  | 'customer'
  | 'partner'
  | 'supplier'
  | 'regulator'
  | 'investor'
  | 'community'
  | 'board';

export type StakeholderRelationshipDirection =
  | 'inbound'
  | 'outbound'
  | 'bidirectional'
  | 'governance';

export interface Stakeholder extends BaseEntity {
  type: 'Stakeholder';
  stakeholder_type: StakeholderType;
  relationship_direction?: StakeholderRelationshipDirection;
  primary_contact?: string;
  external_identifiers?: Record<string, string>;
}

// v1.0.0-alpha: Actor (AC) : internal performers.
// Mirrors schemas/entities/actor.json. Catalog:
// technehub-labs/dea-catalog-actors.
export type ActorType = 'human' | 'team' | 'system' | 'ai-agent' | 'hybrid';
export type ActorScope = 'individual' | 'team' | 'departmental' | 'enterprise' | 'ecosystem';

export interface ActorLinks {
  stakeholder_ref?: string;
  digital_identity_ref?: string;
}

export interface Actor extends BaseEntity {
  type: 'Actor';
  actor_type: ActorType;
  scope?: ActorScope;
  owner?: string;
  capabilities?: string[];
  processes_performed?: string[];
  links?: ActorLinks;
}

export type TenetTier = 'mandatory' | 'recommended' | 'aspirational';

// v0.4.0 (ADR-0004 D3): renamed from Principle. Non-binding belief that
// informs Guardrails; enforces nothing on its own.
// Mirrors schemas/entities/tenet.json. Catalog: technehub-labs/dea-catalog-tenets.
export interface Tenet extends BaseEntity {
  type: 'Tenet';
  statement: string;
  rationale: string;
  applicability: string;
  tier?: TenetTier;
  informs_guardrails?: string[];
  related_tenets?: string[];
}

export type PatternMaturity = 'emerging' | 'established' | 'canonical' | 'deprecated';

export interface ArchitecturePattern extends BaseEntity {
  type: 'ArchitecturePattern';
  problem: string;
  solution: string;
  forces?: string[];
  consequences?: {
    benefits?: string[];
    drawbacks?: string[];
    tradeoffs?: string[];
  };
  applicability: string[];
  anti_patterns?: string[];
  related_patterns?: string[];
  related_tenets?: string[];
  related_guardrails?: string[];
  maturity?: PatternMaturity;
  implementation_hints?: string[];
}

export type GuardrailDomain =
  | 'enterprise-architecture'
  | 'data-architecture'
  | 'software-architecture'
  | 'security-architecture'
  | 'cloud-architecture'
  | 'integration-architecture'
  | 'process-architecture'
  | 'governance';

// v0.4.0 (ADR-0004 D4): renamed from Standard. Enforceable constraint with
// an enforcement maturity ladder : policy-as-code, not a static document.
// Mirrors schemas/entities/guardrail.json. Catalog: technehub-labs/dea-catalog-guardrails.
export type GuardrailEnforcement = 'advisory' | 'automated-warn' | 'automated-block' | 'platform-enforced';

export interface Guardrail extends BaseEntity {
  type: 'Guardrail';
  enforcement: GuardrailEnforcement;
  domain: GuardrailDomain;
  source?: string;
  url?: string;
  implements_controls?: string[];
  informed_by_tenets?: string[];
  coverage?: string[];
  related_guardrails?: string[];
}

export type AbstractionLevel = 'conceptual' | 'logical' | 'physical';

// v0.4.0 (ADR-0004 D5): renamed from ReferenceModel. Composed, reusable
// target-state design assembled from Architecture Patterns.
// Mirrors schemas/entities/blueprint.json. Catalog: technehub-labs/dea-catalog-blueprints.
export interface Blueprint extends BaseEntity {
  type: 'Blueprint';
  domain: string;
  abstraction_level: AbstractionLevel;
  scope?: string;
  layers?: Array<{
    name: string;
    description: string;
    components?: string[];
  }>;
  key_components?: string[];
  patterns?: string[];
  related_blueprints?: string[];
  related_guardrails?: string[];
  related_tenets?: string[];
}

export type CapabilityType = 'business' | 'technical' | 'hybrid';
export type MaturityLevel = 'nascent' | 'emerging' | 'defined' | 'managed' | 'optimizing';

export interface Capability extends BaseEntity {
  type: 'Capability';
  capability_type: CapabilityType;
  maturity_level: MaturityLevel;
  domain?: string;
  owner?: string;
  parent_capability?: string;
  child_capabilities?: string[];
  realized_by?: string[];
  processes?: string[];
  metrics?: string[];
}

export type ProcessType = 'business' | 'operational' | 'support' | 'management';

export type ProcessIntent = 'operational' | 'support' | 'management';

export type ProcessAudience =
  | 'governance-existence'
  | 'strategy-direction'
  | 'agency-organization'
  | 'party-relationship'
  | 'product-value'
  | 'enablement-operations'
  | 'finance-accounting';

export interface Process extends BaseEntity {
  type: 'Process';
  // v3.0.0-alpha: replaced process_type (4-value legacy enum) with two
  // orthogonal axes. See docs/process-type-taxonomy.md for rationale.
  process_intent: ProcessIntent;
  process_audience: ProcessAudience;
  stakeholders?: string[];
  actors?: string[];
  owner?: string;
  trigger?: string;
  outcome?: string;
  parent_process?: string;
  child_processes?: string[];
  capabilities_delivered?: string[];
  services_provided?: string[];
  components_involved?: string[];
  kpis?: string[];
}

// v1.0.0-alpha: Business Object (BO) : atom of the ECF matrix.
// Mirrors schemas/entities/business-object.json. Catalog:
// technehub-labs/dea-catalog-business-objects.
export type EcfDomain =
  | 'governance-existence'
  | 'strategy-direction'
  | 'agency-organization'
  | 'party-relationship'
  | 'product-value'
  | 'enablement-operations'
  | 'finance-accounting';

export type EcfStage =
  | 'conceive'
  | 'design'
  | 'build'
  | 'activate'
  | 'operate'
  | 'improve'
  | 'retire';

export interface BusinessObjectStateTransition {
  state: string;
  ecf_stage?: EcfStage;
  entered: string;
  exited?: string;
  note?: string;
}

export interface BusinessObjectIdentity {
  primary_id?: string;
  external_ids?: Record<string, string>;
}

export interface BusinessObject extends BaseEntity {
  type: 'BusinessObject';
  object_class: string;
  object_subclass?: string;
  ecf_domain: EcfDomain;
  ecf_stage: EcfStage;
  current_state?: string;
  state_history?: BusinessObjectStateTransition[];
  identity?: BusinessObjectIdentity;
  owner?: string;
  stakeholders?: string[];
  capabilities_consumed?: string[];
  processes_involved?: string[];
  events?: string[];
  data_entities?: string[];
  components_realizing?: string[];
}

// v1.0.0-alpha: Organizational Unit (OU) : owner of capabilities,
// runner of processes, custodian of business objects. Mirrors
// schemas/entities/organizational-unit.json. Catalog:
// technehub-labs/dea-catalog-organizational-units.
//
// Reuses EcfDomain + EcfStage from the BusinessObject declaration above.
export type OUType =
  | 'business-unit'
  | 'division'
  | 'department'
  | 'team'
  | 'role-cluster'
  | 'virtual-team'
  | 'governance-body'
  | 'external-partner-role';

export type OUScope =
  | 'individual'
  | 'team'
  | 'departmental'
  | 'division'
  | 'enterprise'
  | 'ecosystem';

export type OULifecycle = 'permanent' | 'temporary' | 'ad-hoc' | 'sunsetting';

export interface OrganizationalUnit extends BaseEntity {
  type: 'OrganizationalUnit';
  ou_type: OUType;
  ou_scope: OUScope;
  ou_lifecycle: OULifecycle;
  ecf_domain?: EcfDomain;
  ecf_stage?: EcfStage;
  parent_ou?: string;
  child_ous?: string[];
  owned_capabilities?: string[];
  owned_processes?: string[];
  owned_objects?: string[];
  actors?: string[];
  stakeholders?: string[];
  cost_center?: string;
  head_count?: number;
}

export type ServiceType = 'internal' | 'external' | 'partner' | 'public';

export interface BusinessService extends BaseEntity {
  type: 'BusinessService';
  service_type: ServiceType;
  owner?: string;
  provided_by?: string[];
  consumed_by?: string[];
  sla?: {
    availability?: string;
    latency_p99_ms?: number;
    throughput_rps?: number;
  };
}

export type ComponentType = 'application' | 'infrastructure' | 'integration';
export type DeploymentModel =
  | 'on-premise'
  | 'iaas'
  | 'paas'
  | 'saas'
  | 'faas'
  | 'hybrid'
  | 'multi-cloud';
export type SecurityClassification = 'public' | 'internal' | 'confidential' | 'restricted';

// v0.2.0 (ADR-0002 D3): SolutionComponent is an ABSTRACT parent declared in
// L3; its concrete subclasses are realized in L5 (discriminated by
// component_type). Do not instantiate directly.
export interface SolutionComponent extends BaseEntity {
  type: 'SolutionComponent';
  component_type: ComponentType;
  deployment_model: DeploymentModel;
  technology_stack?: string[];
  capabilities_realized?: string[];
  services_provided?: string[];
  services_consumed?: string[];
  patterns_applied?: string[];
  owner?: string;
  dependencies?: string[];
  security_classification?: SecurityClassification;
}

// v1.0.0-alpha: SolutionComponent subClasses (discriminated union by
// component_type). Each subClass narrows component_type to one of the
// three SolutionComponent.component_type enum values.
// Mirrors schemas/entities/{application,infrastructure,integration}-component.json.
// Catalog: technehub-labs/dea-catalog-application-components.
export type ApplicationDeploymentUnit =
  | 'service' | 'batch-job' | 'scheduled-task'
  | 'event-handler' | 'lambda' | 'daemon';

export interface ApplicationComponent extends BaseEntity {
  type: 'ApplicationComponent';
  component_type: 'application';
  deployment_unit: ApplicationDeploymentUnit;
  runtime?: string;
}

export type InfrastructureType =
  | 'compute' | 'network' | 'storage' | 'security'
  | 'container' | 'serverless' | 'database-host';

export interface InfrastructureComponent extends BaseEntity {
  type: 'InfrastructureComponent';
  component_type: 'infrastructure';
  infrastructure_type: InfrastructureType;
  iac_tool?: string;
}

export type IntegrationPattern =
  | 'api-gateway' | 'message-queue' | 'file-transfer'
  | 'event-stream' | 'etl' | 'rpc' | 'graphql-federation';
export type IntegrationDirection = 'inbound' | 'outbound' | 'bidirectional';

export interface IntegrationComponent extends BaseEntity {
  type: 'IntegrationComponent';
  component_type: 'integration';
  integration_pattern: IntegrationPattern;
  direction: IntegrationDirection;
}

// v1.0.0 (CR-018, CR-019, CR-020, CR-021, CR-022): Information Systems
// sub-tree introduced in the IS Semantic Architecture programme (ADR-ISA-000).
// Mirrors schemas/entities/{information-system-function,information-system-
// component,information-system-service,integration-interface}.json.
// Catalog: technehub-labs/dea-catalog-information-system-{functions,
// components,services,integration-interfaces} (renames + new repos owned by
// CR-IS-CAT-01..04). CR-022 closure: artifacts.* paths populated.
export interface InformationSystemFunction extends BaseEntity {
  type: 'InformationSystemFunction';
  classification?: string;
  function_class?: string;
  trigger?: string;
  output_type?: string;
}

export interface InformationSystemComponent extends BaseEntity {
  type: 'InformationSystemComponent';
  component_responsibility?: string;
  component_class?: string;
}

export interface InformationSystemService extends BaseEntity {
  type: 'InformationSystemService';
  service_purpose?: string;
  service_class?: string;
  consumer_context?: string;
}

export interface IntegrationInterface extends BaseEntity {
  type: 'IntegrationInterface';
  interface_purpose?: string;
  interaction_pattern?:
    | 'synchronous-request-response'
    | 'asynchronous-message'
    | 'publish-subscribe'
    | 'event-stream'
    | 'batch-file-transfer'
    | 'shared-data-access'
    | 'streaming'
    | 'other';
  protocol?: string;
}

// v1.0.0-alpha: Technology. Mirrors schemas/entities/technology.json.
// Catalog: technehub-labs/dea-catalog-patterns.
export type TechnologyCategory =
  | 'language' | 'framework' | 'runtime' | 'database' | 'library'
  | 'build-tool' | 'ci-cd' | 'monitoring' | 'orchestration' | 'platform';
export type TechnologyLifecycleStatus =
  | 'approved' | 'deprecated' | 'banned' | 'experimental';

export interface Technology extends BaseEntity {
  type: 'Technology';
  technology_category: TechnologyCategory;
  vendor?: string;
  version_requirement?: string;
  lifecycle_status?: TechnologyLifecycleStatus;
}

export type MetricType = 'kpi' | 'health' | 'maturity' | 'performance' | 'adoption' | 'compliance' | 'risk';
export type MetricFrequency = 'realtime' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'quarterly';

export interface Metric extends BaseEntity {
  type: 'Metric';
  metric_type: MetricType;
  unit: string;
  // v0.2.0 (ADR-0002 D1): Metric belongs to the cross-cutting Measurement
  // Dimension : scope_layers declares which layers it may evaluate.
  scope_layers?: ArchitectureLayerId[];
  measurement_method?: string;
  baseline_value?: string | number;
  target_value?: string | number;
  thresholds?: {
    red?: string | number;
    amber?: string | number;
    green?: string | number;
  };
  frequency?: MetricFrequency;
  entities_measured?: string[];
  owner?: string;
}

// v0.4.0 (ADR-0004 D2): Concept merges GlossaryTerm + TaxonomyNode into a
// single dimension entity of semantic-dimension : a queryable concept graph.
// Mirrors schemas/entities/concept.json. Catalog: technehub-labs/dea-catalog-concepts.
export interface Concept extends BaseEntity {
  type: 'Concept';
  definition: string;
  abbreviation?: string;
  synonyms?: string[];
  parent_concept?: string | null;
  related_concepts?: string[];
  defines_entities?: string[];
  usage_context?: string;
}

// ─── v0.2.0 entities (ADR-0002) ───────────────────────────

// EcosystemActor (EA) : L1 External Parties. Active value-exchange party;
// distinct from Stakeholder (affected/engaged, may be passive).
// Mirrors schemas/entities/ecosystem-actor.json. Catalog repo TBD (planned).
export type EcosystemActorKind =
  | 'customer' | 'supplier' | 'partner' | 'regulator' | 'platform' | 'competitor';

export interface EcosystemActor extends BaseEntity {
  type: 'EcosystemActor';
  actor_kind: EcosystemActorKind;
  exchange_directions?: ('inbound' | 'outbound')[];
  digital_identity_ref?: string;
}

// ValueExchange (VE) : L1 Value Flows.
// Mirrors schemas/entities/value-exchange.json. Catalog repo TBD (planned).
export type ValueFlowType = 'information' | 'goods' | 'funds' | 'service';
export type ValueFlowDirection = 'inbound' | 'outbound' | 'bidirectional';

export interface ValueExchange extends BaseEntity {
  type: 'ValueExchange';
  flow_type: ValueFlowType;
  direction: ValueFlowDirection;
  counterparty_ref?: string;
  governed_by_ref?: string;
  payload_refs?: string[];
}

// CollaborationAgreement (CA) : L1 Agreements (moved from L2 by ADR-0002 D2).
// Mirrors schemas/entities/collaboration-agreement.json. Catalog repo TBD (planned).
export type AgreementKind = 'cooperative' | 'mandated';

export interface CollaborationAgreement extends BaseEntity {
  type: 'CollaborationAgreement';
  agreement_kind: AgreementKind;
  parties?: string[];
  governs_exchanges?: string[];
  effective_from?: string;
  effective_to?: string;
}

// BusinessFunction (BF) : L3 Work Organization. Groups capabilities
// (CAP → BF), owned by an Organizational Unit (BF → OU, 1:1).
// Mirrors schemas/entities/business-function.json. Catalog repo TBD (planned).
export interface BusinessFunction extends BaseEntity {
  type: 'BusinessFunction';
  grouped_capabilities?: string[];
  owning_unit_ref?: string;
}

// ─── v0.3.0 entities (ADR-0003 comprehensiveness expansion) ──

// EcosystemPlatform (EP) : L1 Ecosystem Platforms. Multi-sided standing
// structure for repeated exchange (marketplace, developer portal, partner
// API program). Mirrors schemas/entities/ecosystem-platform.json.
export type PlatformKind = 'marketplace' | 'developer-portal' | 'partner-api-program' | 'data-exchange';
export interface EcosystemPlatform extends BaseEntity {
  type: 'EcosystemPlatform';
  platform_kind: PlatformKind;
  participant_count?: number;
}

// Risk (RSK) / Control (CTL) / Regulation (REG) : L2 Risk & Compliance.
export type RiskCategory = 'strategic' | 'operational' | 'regulatory' | 'technology' | 'financial' | 'reputational';
export interface Risk extends BaseEntity {
  type: 'Risk';
  risk_category: RiskCategory;
  likelihood?: 'rare' | 'unlikely' | 'possible' | 'likely' | 'almost-certain';
  impact?: 'negligible' | 'minor' | 'moderate' | 'major' | 'severe';
}
export type ControlType = 'preventive' | 'detective' | 'corrective';
export interface Control extends BaseEntity {
  type: 'Control';
  control_type: ControlType;
  mitigates?: string[];
}
export interface Regulation extends BaseEntity {
  type: 'Regulation';
  jurisdiction?: string;
  mandates?: string[];
}

// Signal (SIG) / Experiment (EXP) / TechnologyRadarEntry (TRE) : L2 Innovation & Foresight.
export interface Signal extends BaseEntity {
  type: 'Signal';
  signal_source: 'market' | 'technology' | 'regulatory' | 'competitor' | 'customer';
  strength?: 'weak' | 'emerging' | 'strong';
}
export interface Experiment extends BaseEntity {
  type: 'Experiment';
  hypothesis: string;
  signal_ref?: string;
  outcome?: 'pending' | 'validated' | 'invalidated' | 'inconclusive';
}
export interface TechnologyRadarEntry extends BaseEntity {
  type: 'TechnologyRadarEntry';
  radar_ring: 'assess' | 'trial' | 'adopt' | 'hold';
  graduates_to?: string;
}

// Skill (SKL) / Role (ROL) / ChangeInitiative (CHI) : L3 People, Skills & Culture.
export interface Skill extends BaseEntity {
  type: 'Skill';
  skill_domain?: string;
  proficiency_levels?: string;
}
export interface Role extends BaseEntity {
  type: 'Role';
  required_skills?: string[];
  fulfilled_by?: string[];
}
export interface ChangeInitiative extends BaseEntity {
  type: 'ChangeInitiative';
  change_scope: 'skills' | 'roles' | 'culture' | 'structure';
  targets?: string[];
  funded_by?: string;
}

// Resource (RES) : L3 Enterprise Resources (v0.5.0, ADR-0005 D3). ABSTRACT
// category root carrying a completeness_contract: specializing catalogs must
// classify instances along exactly one dimension (liquidity / maintenance
// regime / legal protection type). Repo-per-specialization : no shared
// catalog, no discriminator (unlike SolutionComponent).
export interface Resource extends BaseEntity {
  type: 'Resource';
  resource_kind: 'financial' | 'physical' | 'intangible';
}
export interface FinancialResource extends BaseEntity {
  type: 'FinancialResource';
  liquidity?: 'cash' | 'near-liquid' | 'credit-facility' | 'instrument' | 'other';
  currency?: string;
}
export interface PhysicalResource extends BaseEntity {
  type: 'PhysicalResource';
  maintenance_regime?: string;
  location?: string;
}
export interface IntangibleResource extends BaseEntity {
  type: 'IntangibleResource';
  protection_type?: 'patent' | 'trademark' | 'copyright' | 'trade-secret' | 'license' | 'brand' | 'other';
  protection_expiry?: string;
}

// ModelDeployment (MDP) / ModelFeedbackSignal (MFS) : L4 Model Operations.
// Share dea-catalog-model-deployments, discriminated by deployment_kind /
// signal_kind respectively (ADR-0002 D6).
export interface ModelDeployment extends BaseEntity {
  type: 'ModelDeployment';
  model_ref: string;
  environment: 'dev' | 'staging' | 'production';
  deployment_kind: 'api-endpoint' | 'batch' | 'embedded' | 'streaming';
}
export interface ModelFeedbackSignal extends BaseEntity {
  type: 'ModelFeedbackSignal';
  signal_kind: 'drift' | 'performance-degradation' | 'outcome-quality';
  derived_from?: string[];
}

// InformationAsset (IA) / KnowledgeAsset (KA) : L4 Information & Knowledge
// (v0.5.0, ADR-0005 D4). Completes Data->Information->Knowledge on the
// digital plane. KA is distinct from Skill (L3): a Skill is possessed by a
// person; a KnowledgeAsset survives the person leaving.
export interface InformationAsset extends BaseEntity {
  type: 'InformationAsset';
  consumption_form?: 'report' | 'dashboard' | 'document' | 'feed' | 'other';
  source_data_entities?: string[];
}
export interface KnowledgeAsset extends BaseEntity {
  type: 'KnowledgeAsset';
  knowledge_form?: 'playbook' | 'runbook' | 'guideline' | 'case-study' | 'lesson-learned' | 'other';
  captured_from?: string[];
  review_cycle?: string;
}

// ─── Union type for all concrete entities ─────────────────

export type AnyEntity =
  | Tenet
  | ArchitecturePattern
  | Guardrail
  | Blueprint
  | Capability
  | Process
  | BusinessService
  | SolutionComponent
  | Metric
  | Measurement
  | MeasurementObservation
  | Baseline
  | PerformanceTarget
  | Threshold
  | PerformanceInterpretation
  | IndicatorDesignation
  | ReportingPeriod
  | Provenance
  | AnalyticalResult
  | Correlation
  | CausalHypothesis
  | Concept
  | EcosystemActor
  | ValueExchange
  | CollaborationAgreement
  | BusinessFunction
  | EcosystemPlatform
  | Risk
  | Control
  | Regulation
  | Signal
  | Experiment
  | TechnologyRadarEntry
  | Skill
  | Role
  | ChangeInitiative
  | Resource
  | FinancialResource
  | PhysicalResource
  | IntangibleResource
  | ModelDeployment
  | ModelFeedbackSignal
  | InformationAsset
  | KnowledgeAsset
  | InformationSystemFunction
  | InformationSystemComponent
  | InformationSystemService
  | IntegrationInterface;

// ─── Metamodel index ──────────────────────────────────────

export const ENTITY_TYPES = [
  'Tenet',
  'ArchitecturePattern',
  'Guardrail',
  'Blueprint',
  'Capability',
  'Process',
  'BusinessService',
  'SolutionComponent',
  'ApplicationComponent',
  'InfrastructureComponent',
  'IntegrationComponent',
  'Technology',
  'Metric',
  'Measurement',
  'MeasurementObservation',
  'Baseline',
  'PerformanceTarget',
  'Threshold',
  'PerformanceInterpretation',
  'IndicatorDesignation',
  'ReportingPeriod',
  'Provenance',
  'AnalyticalResult',
  'Correlation',
  'CausalHypothesis',
  'Concept',
  'EcosystemActor',
  'ValueExchange',
  'CollaborationAgreement',
  'BusinessFunction',
  'EcosystemPlatform',
  'Risk',
  'Control',
  'Regulation',
  'Signal',
  'Experiment',
  'TechnologyRadarEntry',
  'Skill',
  'Role',
  'ChangeInitiative',
  'Resource',
  'FinancialResource',
  'PhysicalResource',
  'IntangibleResource',
  'ModelDeployment',
  'ModelFeedbackSignal',
  'InformationAsset',
  'KnowledgeAsset',
  'InformationSystemFunction',
  'InformationSystemComponent',
  'InformationSystemService',
  'IntegrationInterface',
] as const;

export const RELATIONSHIP_TYPES: RelationshipType[] = [
  'mapsTo',
  'realizes',
  'implements',
  'influencedBy',
  'decomposes',
  'orchestrates',
  'consumes',
  'provides',
  'governs',
  'measuredBy',
];

// ═══════════════════════════════════════════════════════════
// Metric programme interfaces (CR-MET-001..012)
//
// Generated from the canonical JSON Schemas: field names, optionality,
// and union types are derived from each schema's properties, required
// list, and enums, so these cannot drift from
// metamodel/dea-metamodel.yaml.
// ═══════════════════════════════════════════════════════════

export interface Measurement extends BaseEntity {
  type: 'Measurement';
  // Reference to the dea:PerformanceMetric definition version applied. Cardinality 1:1 (every Measurement applies exactly one Metric). The reference MAY include the semantic version (e.g. dea:metric-customer-retention-rate@1.0.0). (CR-MET-003 binding ADR-MET-002 decision 6.)
  applies_metric: string;
  // Reference to the entity that was measured. Cardinality 1:1 (every Measurement targets one subject). Current source list (7 entity types) matches the dea:measured-by source endpoint; CR-MET-007 widens to 17 per ADR-MET-004. (CR-MET-003 binding ADR-MET-002 decision 7.)
  measures_subject: string;
  // Method applied to perform the measurement (CR-MET-003 binding). Required.
  measurement_method: string;
  // Time of measurement execution or capture (CR-MET-003 binding). Required.
  measurement_time: string;
  // Start of the reporting period represented by the measurement. Conditional on the parent Metric having a reporting-period concept; full binding in CR-MET-006.
  reporting_period_start?: string;
  // End of the reporting period represented by the measurement. Conditional on the parent Metric having a reporting-period concept; full binding in CR-MET-006.
  reporting_period_end?: string;
  // Data source or originating system. Recommended.
  measurement_source?: string;
  // Execution or record status (CR-MET-003 binding). The 10-value enum is the canonical Measurement lifecycle; CR-MET-004 binds the legal transitions between these states. Required.
  measurement_status: 'planned' | 'initiated' | 'in_progress' | 'pending_validation' | 'validated' | 'completed' | 'failed' | 'cancelled' | 'rejected' | 'superseded';
  // Canonical execution mode classification (CR-MET-004). Execution classifications, not separate Measurement subclasses. Required.
  execution_mode: 'automated' | 'manual' | 'calculated' | 'aggregated' | 'external' | 'assessed' | 'simulated' | 'ai_assisted';
  // The declared lifecycle state transition record (CR-MET-004). The from_state and to_state pair MUST be a legal transition per metamodel/vocabularies/measurement-lifecycle.yaml. Recommended.
  state_transitions?: Record<string, unknown>[];
  // Key identifying the logical measurement event (the same Metric applied to the same subject in the same reporting period). A retry of the same logical event MUST reuse the same key; two Measurements MUST NOT both be completed with the same key (CR-MET-004 idempotency semantics). Optional; required when a retry is possible.
  logical_measurement_event?: string;
  // Versioned measurement configuration reference. Recommended.
  configuration_reference?: string;
  // Supporting evidence references. Each reference is a string handle that the future governance / evidence CRs will resolve. Recommended.
  evidence_reference?: string[];
  // Free-form measurement context. Recommended.
  context?: Record<string, unknown>;
  // Temporal context placeholder. Full specification in CR-MET-004 (lifecycle) and CR-MET-011 (temporal dimensions).
  temporal?: Record<string, unknown>;
  // Reference to the responsible party. Full governance object spec in CR-MET-010.
  responsible_party?: string;
  // Configuration parameters necessary to reproduce the result. Full specification in CR-MET-003.
  configuration?: Record<string, unknown>;
}

export interface MeasurementObservation extends BaseEntity {
  type: 'MeasurementObservation';
  // Reference to the dea:Measurement that produced this observation. Cardinality 1:0..1 (a MeasurementObservation is the result of one Measurement; a Measurement MAY produce zero or more observations).
  produced_by: string;
  // The recorded value. Typed to support the four measurement_nature values from the parent Metric: numeric (number), ordinal (number or string), nominal (string), boolean (boolean), composite (object). (CR-MET-003 binding CR-MET-001.)
  value: number;
  // Time the value was observed (CR-MET-003 binding). Required.
  observed_at: string;
  // Start of validity period. Conditional on observations that have a validity period concept.
  valid_from?: string;
  // End of validity period. Conditional on observations that have a validity period concept.
  valid_to?: string;
  // Start of the reporting period represented by this observation. Recommended.
  reporting_period_start?: string;
  // End of the reporting period represented by this observation. Recommended.
  reporting_period_end?: string;
  // Quality assessment (textual). Recommended.
  observation_quality?: string;
  // Validity or supersession status (CR-MET-003 binding). Required. The 4-value enum covers proposed -> active -> superseded -> retired.
  observation_status: 'proposed' | 'active' | 'superseded' | 'retired';
  // Verification state of the observation value (CR-MET-004). An ai_assisted Measurement MUST NOT produce an independently_verified or human_verified observation unless an independent verification step occurred. An ai_estimated observation is NOT equivalent to a verified observation for reporting, aggregation, or comparison.
  verification_state?: 'unverified' | 'ai_estimated' | 'independently_verified' | 'human_verified';
  // DEPRECATED. CR-MET-011 Q19a separates the two semantics: this field historically conflated correction (the prior Observation was erroneous) with supersession (a newer authoritative Observation replaced it). New records MUST use corrects_observation_ref for correction and the dea:supersedes relationship for supersession. Retained for one release cycle for backward compatibility.
  supersedes_observation?: string;
  // CR-MET-011 section 5: reference to the dea:Provenance record for this Observation. 1:1. REQUIRED for any Observation that is published or relied upon. Carries the 11 provenance elements: source, source record, collection activity, calculation activity, transformation chain, responsible party, configuration, formula version, metric version, evidence, and the distinct temporal dimensions.
  provenance_reference?: string;
  // Reference to the measurement uncertainty (CR-MET-005 binding handle). Full uncertainty model is CR-MET-012.
  uncertainty_reference?: string;
  // Comparability requirements for this observation (CR-MET-005 binding). Documents any conditions under which this observation is comparable to others (e.g. same Unit, same Scale, same reporting period, same population).
  comparability_requirements?: string;
  // Significant figures for the observed value (CR-MET-005 binding).
  precision?: number;
  // Supporting evidence references. Recommended.
  evidence_reference?: string[];
  // Optional reference to the unit registry per CR-MET-005. Required when the parent Metric has measurement_nature: numeric.
  unit?: string;
  // CR-MET-011 section 3 (Q17b): the 7 temporal dimensions on one nested object. The dimensions MUST NOT be collapsed into one timestamp; each is a distinct fact. Observed at is when the value was observed; measured at is when the measurement was performed; reporting period is the interval the result represents (a dea:ReportingPeriod reference); valid from and valid to are the period during which the result applies; recorded at is when the information entered the system (transaction time); effective from and effective to are when the governing definition or configuration became applicable; published at is when the result became available to consumers.
  temporal?: Record<string, unknown>;
  // CR-MET-011 section 7 (Q19): the 5 record states. original is the first recorded result. corrected is a revised result that replaces an erroneous original. superseded is replaced by a newer authoritative Observation for the same period. invalid is marked as not to be used. retracted is withdrawn from publication. A correction MUST NOT silently overwrite the original value.
  record_state?: 'original' | 'corrected' | 'superseded' | 'invalid' | 'retracted';
  // CR-MET-011 section 7: the reason a corrected Observation differs from the original. REQUIRED when record_state is corrected; MUST be null otherwise.
  correction_reason?: string;
  // CR-MET-011 section 7 (dea:corrects): the original Observation this record restates. REQUIRED when record_state is corrected; MUST be null otherwise.
  corrects_observation_ref?: string;
  // CR-MET-011 section 7 (dea:supersedes): why a newer authoritative Observation replaces this one for the same reporting period. REQUIRED when record_state is superseded; MUST be null otherwise.
  supersedes_observation_reason?: string;
  // Optional confidence value in the range 0..1.
  confidence?: number;
}

export interface Baseline extends BaseEntity {
  type: 'Baseline';
  // CR-MET-006 binding (Baseline.kind controlled vocabulary; 6 values).
  kind: 'historical' | 'initial' | 'strategic' | 'operational' | 'regulatory' | 'scenario_derived';
  // CR-MET-006 binding (Baseline.approval_status controlled vocabulary; 4 values).
  approval_status: 'draft' | 'proposed' | 'approved' | 'retired';
  // The PerformanceMetric id this Baseline is a reference for (relationship dea:references).
  reference_metric_ref: string;
  // The subject the Baseline concerns (relationship dea:applies-to; target is Entity or AssessmentSubject).
  subject_ref: string;
  // The reference value or observation summary. Numeric for ratio/interval Metrics; ordinal for ordinal Metrics; categorical for categorical Metrics.
  reference_value: unknown;
  establishment_date: string;
  // Reference to a TemporalInterval; CR-MET-006 binding.
  applicable_period: string;
  // The organizational scope (enterprise, business_domain, business_unit, capability, process, product_or_service, system). String or array of strings.
  organizational_scope: unknown;
  measurement_methodology?: string;
  // Source and evidence supporting the Baseline. String or array of strings/references.
  source_evidence?: unknown;
  // Previous Baseline ids this Baseline supersedes (relationship dea:supersedes, extended in CR-MET-004).
  supersedes_baselines?: string[];
}

export interface PerformanceTarget extends BaseEntity {
  type: 'PerformanceTarget';
  // The PerformanceMetric id being targeted (relationship dea:specifies-target).
  target_metric_ref: string;
  // The subject being targeted (relationship dea:applies-to).
  target_subject_ref: string;
  // The scope (enterprise, business_domain, business_unit, capability, process, product_or_service, system). Aligns with Metric.scope_classification (CR-MET-002). String or array of strings.
  target_scope: unknown;
  // The desired value (numeric). Mutually exclusive with target_range.
  target_value?: number;
  // The desired range {min, max}. Mutually exclusive with target_value.
  target_range?: Record<string, unknown>;
  // CR-MET-006 binding (PerformanceTarget.direction controlled vocabulary; 5 values).
  target_direction: 'increase' | 'decrease' | 'maintain' | 'bounded' | 'exact_match';
  // Reference to a TemporalInterval.
  effective_period: string;
  // Responsible owner (Actor ref).
  owner_ref: string;
  // The StrategicObjective or Outcome this Target supports. Relationship dea:has-target (StrategicObjective -> PerformanceTarget).
  associated_objective_ref?: string;
  // CR-MET-006 binding (PerformanceTarget.approval_status controlled vocabulary; 4 values).
  approval_status: 'draft' | 'proposed' | 'approved' | 'retired';
  supporting_rationale?: string;
}

export interface Threshold extends BaseEntity {
  type: 'Threshold';
  // The PerformanceMetric id being constrained (relationship dea:constrains, extended in CR-MET-006).
  threshold_metric_ref: string;
  // The boundary value(s). A number for single-direction thresholds (higher_is_better, lower_is_better, exact_match); an object {min, max} for bounded_optimum.
  threshold_value: unknown;
  // CR-MET-006 binding (Threshold.level controlled vocabulary; 4 values). A Metric MAY have multiple Thresholds (one per level).
  threshold_level: 'critical' | 'warning' | 'acceptable' | 'optimal';
  // CR-MET-006 binding (Threshold.direction controlled vocabulary; 4 values).
  direction: 'higher_is_better' | 'lower_is_better' | 'bounded_optimum' | 'exact_match';
  // Reference to a TemporalInterval.
  effective_period: string;
  // Responsible owner (Actor ref).
  owner_ref?: string;
  // Reference to an escalation rule (e.g. notification policy, runbook).
  escalation_rule_ref?: string;
}

export interface PerformanceInterpretation extends BaseEntity {
  type: 'PerformanceInterpretation';
  // The PerformanceMetric id being interpreted.
  interprets_metric_ref: string;
  // The MeasurementObservation id being interpreted (relationship dea:interprets).
  interprets_observation_ref: string;
  // CR-MET-006 binding (PerformanceInterpretation.kind controlled vocabulary; 4 values).
  interpretation_kind: 'variance_evaluation' | 'threshold_evaluation' | 'benchmark_evaluation' | 'composite_judgment';
  // CR-MET-006 binding (PerformanceInterpretation.state controlled vocabulary; 6 values).
  interpretation_state: 'exceeds_target' | 'meets_target' | 'within_tolerance' | 'warning' | 'critical' | 'unknown';
  // Which reference was used (Baseline ref, PerformanceTarget ref, Threshold ref, BenchmarkReference ref).
  reference_used: string;
  // Computed absolute variance (ObservedValue - ReferenceValue). Optional; populated when interpretation_kind is variance_evaluation.
  absolute_variance?: number;
  // Computed relative variance percentage ((ObservedValue - ReferenceValue) / ReferenceValue * 100). Optional; populated when interpretation_kind is variance_evaluation.
  relative_variance?: number;
  narrative?: string;
  // Who/what performed the interpretation (Actor or system ref).
  evaluator_ref?: string;
  evaluated_at: string;
}

export interface IndicatorDesignation extends BaseEntity {
  type: 'IndicatorDesignation';
  // CR-MET-008 binding (IndicatorDesignation.designation_type controlled vocabulary; 5 values).
  designation_type: 'KPI' | 'KRI' | 'KCI' | 'SLI' | 'Operational';
  // The PerformanceMetric id being designated (relationship dea:has-designation, inverse dea:designates).
  associated_metric_ref: string;
  // Why the designation exists. For KPI: 'evaluating performance against objective X'. For KRI: 'monitoring risk exposure of risk Y'. For KCI: 'evaluating control effectiveness of control Z'.
  management_purpose: string;
  // The StrategicObjective, Outcome, Risk, or Control this designation supports. KPI points to business objective; KRI points to risk-objective; KCI points to control objective. The user-supplied sections 6-8 requirement.
  associated_objective_ref?: string;
  // Scope of application (enterprise, business_domain, business_unit, capability, process, product_or_service, system). Aligns with Metric.scope_classification (CR-MET-002). String or array of strings.
  organizational_scope: unknown;
  // Responsible management authority (Actor ref).
  accountable_owner_ref: string;
  // CR-MET-008 binding (IndicatorDesignation.reporting_frequency controlled vocabulary; 8 values).
  reporting_frequency: 'real_time' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'semi_annual' | 'annual';
  // Reference to a PerformanceTarget (CR-MET-006) applicable to this designation.
  target_reference?: string;
  // Reference to a Threshold (CR-MET-006) applicable to this designation.
  threshold_reference?: string;
  // Required management response (e.g., notification policy, runbook, escalation chain). String or array of strings/references.
  escalation_rules?: unknown;
  // CR-MET-008 binding (IndicatorDesignation.measurement_orientation controlled vocabulary; 3 values). Cross-cutting attribute: the same Metric may be designated as KPI Leading for one purpose and KPI Lagging for another.
  measurement_orientation: 'leading' | 'lagging' | 'neutral';
  // Reference to a TemporalInterval; CR-MET-006 binding (also applies to designation).
  effective_period: string;
  // CR-MET-008 binding (IndicatorDesignation.approval_status controlled vocabulary; 4 values).
  approval_status: 'draft' | 'proposed' | 'approved' | 'retired';
}

export interface ReportingPeriod extends BaseEntity {
  type: 'ReportingPeriod';
  // CR-MET-011 section 4: the 7 supported period shapes. instantaneous and point_in_time carry no bounded interval; fixed_duration, rolling, and cumulative carry a bounded interval; event_based is anchored to an event occurrence; irregular carries an explicitly non-uniform interval.
  period_type: 'instantaneous' | 'point_in_time' | 'fixed_duration' | 'rolling' | 'cumulative' | 'event_based' | 'irregular';
  // CR-MET-011 section 4: the basis on which the period is measured. calendar and fiscal fix the boundaries to a convention; rolling is relative to an anchor; event_based is defined by an occurrence.
  period_semantics: 'calendar' | 'fiscal' | 'rolling' | 'event_based' | 'custom';
  // Inclusive period start. MUST be null for instantaneous and point_in_time periods; MUST be non-null for fixed_duration, rolling, cumulative, and irregular periods.
  period_start?: string;
  // Exclusive or inclusive period end as declared by period_semantics. MUST be null for instantaneous and point_in_time periods.
  period_end?: string;
  // The anchor a rolling or event-based period is measured from. REQUIRED for period_semantics rolling and event_based; MUST be null otherwise.
  anchor_reference?: string;
  // The rolling window size (e.g. 30d, 12w, 7q). REQUIRED for period_type rolling; MUST be null otherwise.
  window_size?: string;
  // Number of irregular sub-intervals composing this period. REQUIRED for period_type irregular; MUST be null otherwise.
  interval_count?: number;
  // The organizational or regulatory calendar that fixes the period boundaries. REQUIRED for period_semantics calendar and fiscal.
  calendar_reference?: string;
  // The fiscal year the period belongs to. REQUIRED for period_semantics fiscal.
  fiscal_year_ref?: string;
  // CR-MET-011 section 3 effective time: when this period definition becomes applicable.
  effective_from?: string;
  // CR-MET-011 section 3 effective time: when this period definition ceases to apply. null when still current.
  effective_to?: string;
  // The organizational scope in effect during the period (CR-MET-011 section 6). Organizational structure changes MUST NOT retrospectively change the scope of a recorded period.
  organizational_scope_ref?: string;
}

export interface Provenance extends BaseEntity {
  type: 'Provenance';
  // Provenance element 1: the original data source (a dea:EvidenceSource). Never a free-text label.
  source_ref: string;
  // Provenance element 2: the specific originating record or dataset.
  source_record_ref: string;
  // Provenance element 3: how the information was acquired (a dea:BusinessProcess or a described extraction step). The W3C PROV activity.
  collection_activity: string;
  // Provenance element 4: how the result was derived (the dea:Measurement that executed the formula). The W3C PROV activity.
  calculation_activity: string;
  // Provenance element 5: the ordered processing and conversion steps applied between collection and calculation.
  transformation_chain?: Record<string, unknown>[];
  // Provenance element 6: the party accountable for the result (a dea:Actor). The W3C PROV responsible-party concept. Covers person, system, or automated process.
  responsible_party_ref: string;
  // Provenance element 7: the measurement configuration in effect when the result was produced.
  configuration_ref: string;
  // Provenance element 8: the exact calculation definition applied, including the version. A result MUST NOT be attributed to a formula without its version.
  formula_version_ref: string;
  // Provenance element 9: the exact Metric definition applied, including the version. This is the binding record for historical reconstruction: the meaning of a historical result is the meaning the Metric had at the version recorded here.
  metric_version_ref: string;
  // Provenance element 10: supporting source material (dea:Evidence / dea:EvidenceArtifact).
  evidence_refs?: string[];
  // Provenance element 11: the relevant temporal information. The 7 CR-MET-011 temporal dimensions MUST NOT be collapsed into one timestamp (Q17).
  timestamps?: Record<string, unknown>;
  // CR-MET-011 section 6: the declared reproducibility posture of the recorded result.
  reproducibility?: Record<string, unknown>;
}

export interface AnalyticalResult extends BaseEntity {
  type: 'AnalyticalResult';
  // CR-MET-012 section 7 (Q20b-prime). observation is NOT a member: dea:MeasurementObservation is the first-class Observation. decision is NOT a member: dea:Decision is the first-class authorized management choice. The user-supplied section 7 requirement that these MUST NOT be conflated or published as equivalent measurement facts is enforced structurally.
  result_type: 'estimate' | 'forecast' | 'simulation_result' | 'recommendation';
  // CR-MET-012 section 3: the 6 complementary analytical capabilities. descriptive answers what happened; diagnostic answers why; predictive answers what is likely; prescriptive answers what should we do; comparative answers how do we compare; scenario_simulation answers what would happen if.
  analytical_capability: 'descriptive' | 'diagnostic' | 'predictive' | 'prescriptive' | 'comparative' | 'scenario_simulation';
  // The subject the analytical result speaks about (a Metric, MeasurementObservation, or other measurable entity).
  subject_ref: string;
  // The analytical output value, when the result type produces a value. Null for a recommendation that proposes an action rather than a quantity.
  value?: number;
  unit?: string;
  // The dea:ReportingPeriod the result speaks about (CR-MET-011).
  reporting_period_ref?: string;
  // The forward-looking dea:ReportingPeriod a forecast or simulation result projects onto. REQUIRED for forecast and simulation_result; MUST be null otherwise.
  horizon_ref?: string;
  // The measurement evidence (dea:MeasurementObservation) the result was derived from. An AnalyticalResult MUST cite its evidence; an unsupported analytical output is not admissible.
  evidence_refs: string[];
  // Reference to the dea:Provenance record (CR-MET-011 section 5) describing how this result came to exist.
  provenance_reference: string;
  // Declared confidence in the analytical output. REQUIRED for every result type; an unquantified analytical output is not admissible.
  confidence: number;
  // Explicit uncertainty statement. REQUIRED for forecast and simulation_result, which are inherently uncertain; optional otherwise.
  uncertainty?: Record<string, unknown>;
  // The analytical model or AIML model that produced the result. REQUIRED for forecast and simulation_result.
  model_ref?: string;
  // The dea:Scenario a simulation_result or scenario-dependent recommendation is conditioned on. REQUIRED for simulation_result; MUST be null otherwise.
  scenario_ref?: string;
  // CR-MET-012 Q21a: the dea:AggregationRule applied. Aggregation MUST respect the CR-MET-005 rules: a simple arithmetic average is NOT a universal aggregation method; ratios MUST NOT be summed; ratios MUST NOT be naively averaged; weighted means MUST declare explicit weights.
  aggregation_rule_ref?: string;
  // Prescriptive results SHOULD record the alternatives considered, so the recommendation is auditable rather than opaque.
  alternative_considered?: Record<string, unknown>[];
  // The accountable party for the analytical result (W3C PROV responsible-party concept; CR-MET-011 section 5).
  responsible_party_ref?: string;
}

export interface Correlation extends BaseEntity {
  type: 'Correlation';
  // The first measured phenomenon in the association.
  source_phenomenon_ref: string;
  // The second measured phenomenon in the association.
  target_phenomenon_ref: string;
  // The correlation coefficient in the range -1 to 1. A coefficient near 0 means no linear association; near 1 a strong positive association; near -1 a strong negative association.
  coefficient: number;
  // The statistical method used (pearson, spearman, kendall, mutual_information, and so on). Required so the result is reproducible.
  method: string;
  // The number of paired observations the coefficient was computed from. A correlation computed from a small sample MUST declare it.
  sample_size: number;
  // The dea:ReportingPeriod over which the association was observed (CR-MET-011).
  reporting_period_ref: string;
  // The dea:MeasurementObservation records the coefficient was computed from.
  evidence_refs?: string[];
  // Candidate confounding variables identified. A correlation WITH declared confounders is more honest than one without; absence of confounders is not evidence of their absence.
  confounder_candidates?: string[];
  // MUST be false. This record asserts association ONLY. A correlation does not establish a causal mechanism. A dea:CausalHypothesis carries the asserted mechanism, separately, with explicit confidence.
  confusion_guard: boolean;
  // A plain-language classification of the coefficient magnitude.
  strength?: 'negligible' | 'weak' | 'moderate' | 'strong' | 'very_strong';
  // A note on direction of association. Association direction is NOT causal direction.
  directional_note?: string;
  // Reference to the dea:Provenance record (CR-MET-011 section 5) for the computation.
  provenance_reference?: string;
}

export interface CausalHypothesis extends BaseEntity {
  type: 'CausalHypothesis';
  // The asserted cause. The direction is what distinguishes a hypothesis from a correlation.
  cause_ref: string;
  // The asserted effect of the cause.
  effect_ref: string;
  // The asserted causal pathway. A hypothesis without a stated mechanism is an assertion, not a hypothesis.
  mechanism: string;
  // Declared confidence in the asserted mechanism, distinct from the strength of any supporting correlation.
  confidence: number;
  // Explicit uncertainty: unmeasured mediators, plausible alternative mechanisms, and known limits of the inference.
  uncertainty?: Record<string, unknown>;
  // How far the hypothesis has been tested. asserted means nobody has tested it; correlation_supported means a co-variation was observed, which is weaker than validated; validated requires an experimental or quasi-experimental basis; refuted means the mechanism was tested and did not hold.
  validation_state: 'asserted' | 'correlation_supported' | 'experiment_running' | 'validated' | 'refuted';
  // The dea:Correlation records that were observed in support. Supporting correlations are evidence, not proof.
  supporting_correlation_refs?: string[];
  // Evidence AGAINST the hypothesis. A hypothesis with no recorded counter-evidence is either trivially true or not honestly recorded.
  counter_evidence: Record<string, unknown>[];
  // The test that would refute the hypothesis. A hypothesis with no falsification test is not testable.
  falsification_test: string;
  // The accountable party for the hypothesis assertion.
  responsible_party_ref?: string;
}
