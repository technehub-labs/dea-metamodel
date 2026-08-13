// DEA Metamodel — TypeScript Interfaces
// Auto-generated from schemas/entities/*.json
// Do not edit manually — regenerate with: npm run generate

// v0.2.0 (ADR-0002): architecture layers L1–L5. Measurement is a
// cross-cutting dimension, not a layer — Metrics carry scope_layers.
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

// v1.0.0-alpha: Stakeholder (SH) — external/affected parties.
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

// v1.0.0-alpha: Actor (AC) — internal performers.
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

export type PrincipleTier = 'mandatory' | 'recommended' | 'aspirational';

export interface Principle extends BaseEntity {
  type: 'Principle';
  statement: string;
  rationale: string;
  applicability: string[];
  exceptions?: string[];
  conflicts_with?: string[];
  related_patterns?: string[];
  related_standards?: string[];
  tier?: PrincipleTier;
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
  related_principles?: string[];
  related_standards?: string[];
  maturity?: PatternMaturity;
  implementation_hints?: string[];
}

export type StandardDomain =
  | 'enterprise-architecture'
  | 'data-architecture'
  | 'software-architecture'
  | 'security-architecture'
  | 'cloud-architecture'
  | 'integration-architecture'
  | 'process-architecture'
  | 'governance';

export interface Standard extends BaseEntity {
  type: 'Standard';
  standard_body: string;
  domain: StandardDomain;
  url?: string;
  license?: string;
  coverage?: string[];
  conforms_to?: string[];
  related_patterns?: string[];
  related_principles?: string[];
}

export type AbstractionLevel = 'conceptual' | 'logical' | 'physical';

export interface ReferenceModel extends BaseEntity {
  type: 'ReferenceModel';
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
  related_reference_models?: string[];
  related_standards?: string[];
  related_principles?: string[];
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
  | 'supply-resources'
  | 'people-organization'
  | 'customer-demand'
  | 'product-offering'
  | 'operations-delivery'
  | 'finance-value';

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

// v1.0.0-alpha: Business Object (BO) — atom of the ECF matrix.
// Mirrors schemas/entities/business-object.json. Catalog:
// technehub-labs/dea-catalog-business-objects.
export type EcfDomain =
  | 'governance-existence'
  | 'supply-resources'
  | 'people-organization'
  | 'customer-demand'
  | 'product-offering'
  | 'operations-delivery'
  | 'finance-value';

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

// v1.0.0-alpha: Organizational Unit (OU) — owner of capabilities,
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

// v1.0.0-alpha: TaxonomyNode. Mirrors schemas/entities/taxonomy-node.json.
// Catalog: technehub-labs/dea-catalog-taxonomy.
export interface TaxonomyNode extends BaseEntity {
  type: 'TaxonomyNode';
  taxonomy: string;
  parent_node?: string;
  child_nodes?: string[];
}

export type MetricType = 'kpi' | 'health' | 'maturity' | 'performance' | 'adoption' | 'compliance' | 'risk';
export type MetricFrequency = 'realtime' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'quarterly';

export interface Metric extends BaseEntity {
  type: 'Metric';
  metric_type: MetricType;
  unit: string;
  // v0.2.0 (ADR-0002 D1): Metric belongs to the cross-cutting Measurement
  // Dimension — scope_layers declares which layers it may evaluate.
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

export interface GlossaryTerm extends BaseEntity {
  type: 'GlossaryTerm';
  definition: string;
  abbreviation?: string;
  synonyms?: string[];
  antonyms?: string[];
  related_terms?: string[];
  metamodel_entity?: string;
  usage_context?: string;
}

export type PresentationFormat = 'diagram' | 'table' | 'matrix' | 'dashboard' | 'narrative' | 'multi';

export interface Viewpoint extends BaseEntity {
  type: 'Viewpoint';
  stakeholder: string;
  concern: string;
  entities_included?: string[];
  entities_excluded?: string[];
  relationships_included?: RelationshipType[];
  filter_criteria?: Record<string, unknown>;
  presentation_format?: PresentationFormat;
  generated_from?: string;
}

// ─── v0.2.0 entities (ADR-0002) ───────────────────────────

// EcosystemActor (EA) — L1 External Parties. Active value-exchange party;
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

// ValueExchange (VE) — L1 Value Flows.
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

// CollaborationAgreement (CA) — L1 Agreements (moved from L2 by ADR-0002 D2).
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

// BusinessFunction (BF) — L3 Work Organization. Groups capabilities
// (CAP → BF), owned by an Organizational Unit (BF → OU, 1:1).
// Mirrors schemas/entities/business-function.json. Catalog repo TBD (planned).
export interface BusinessFunction extends BaseEntity {
  type: 'BusinessFunction';
  grouped_capabilities?: string[];
  owning_unit_ref?: string;
}

// ─── Union type for all concrete entities ─────────────────

export type AnyEntity =
  | Principle
  | ArchitecturePattern
  | Standard
  | ReferenceModel
  | Capability
  | Process
  | BusinessService
  | SolutionComponent
  | Metric
  | GlossaryTerm
  | Viewpoint
  | EcosystemActor
  | ValueExchange
  | CollaborationAgreement
  | BusinessFunction;

// ─── Metamodel index ──────────────────────────────────────

export const ENTITY_TYPES = [
  'Principle',
  'ArchitecturePattern',
  'Standard',
  'ReferenceModel',
  'Capability',
  'Process',
  'BusinessService',
  'SolutionComponent',
  'ApplicationComponent',
  'InfrastructureComponent',
  'IntegrationComponent',
  'Technology',
  'Metric',
  'GlossaryTerm',
  'TaxonomyNode',
  'Viewpoint',
  'EcosystemActor',
  'ValueExchange',
  'CollaborationAgreement',
  'BusinessFunction',
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
