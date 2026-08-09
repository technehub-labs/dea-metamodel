// DEA Metamodel — TypeScript Interfaces
// Auto-generated from schemas/entities/*.json
// Do not edit manually — regenerate with: npm run generate

export type EntityStatus = 'draft' | 'candidate' | 'approved' | 'deprecated';
export type RelationshipType =
  | 'maps-to'
  | 'realizes'
  | 'implements'
  | 'influenced-by'
  | 'decomposes'
  | 'orchestrates'
  | 'consumes'
  | 'provides'
  | 'governs'
  | 'measured-by';

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

export type MetricType = 'kpi' | 'health' | 'maturity' | 'performance' | 'adoption' | 'compliance' | 'risk';
export type MetricFrequency = 'realtime' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'quarterly';

export interface Metric extends BaseEntity {
  type: 'Metric';
  metric_type: MetricType;
  unit: string;
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
  | Viewpoint;

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
] as const;

export const RELATIONSHIP_TYPES: RelationshipType[] = [
  'maps-to',
  'realizes',
  'implements',
  'influenced-by',
  'decomposes',
  'orchestrates',
  'consumes',
  'provides',
  'governs',
  'measured-by',
];
