-- DEA Metamodel SQLite Schema
-- Version: 0.9.0
-- Derived from normative source: metamodel/dea-metamodel.yaml (CR-001). Do not edit semantics here.
-- All tables include source tracking and soft-delete for auditability.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ═══════════════════════════════════════════════════════════
-- Entity tables
-- ═══════════════════════════════════════════════════════════

CREATE TABLE entities (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL CHECK(type IN (
        'Tenet','ArchitecturePattern','Guardrail','Blueprint',
        'Capability','Process','BusinessService','SolutionComponent',
        'ApplicationComponent','InfrastructureComponent','IntegrationComponent',
        'InformationSystemFunction','InformationSystemComponent',
        'InformationSystemService','IntegrationInterface',
        'Technology','Metric','Concept',
        -- Metric programme (CR-MET-001..012). Every table below references
        -- entities(id); without these type values the Metric tables are
        -- declared but unwritable, so this list must admit them.
        'Measurement','MeasurementObservation','Baseline','PerformanceTarget',
        'Threshold','PerformanceInterpretation','IndicatorDesignation',
        'ReportingPeriod','Provenance','AnalyticalResult','Correlation',
        'CausalHypothesis'
    )),
    name            TEXT NOT NULL,
    description     TEXT,
    version         TEXT NOT NULL DEFAULT '1.0.0',
    tags            TEXT,                          -- JSON array
    metadata_json   TEXT,                          -- JSON object
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    status          TEXT NOT NULL DEFAULT 'draft'
        CHECK(status IN ('draft','candidate','approved','deprecated')),
    deleted         INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_entities_type       ON entities(type);
CREATE INDEX idx_entities_status     ON entities(status);
CREATE INDEX idx_entities_tags       ON entities(tags);

-- ═══════════════════════════════════════════════════════════
-- Entity extension tables (type-specific fields)
-- ═══════════════════════════════════════════════════════════

-- Tenets (v0.4.0 : renamed from principles, ADR-0004 D3)
CREATE TABLE tenets (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT NOT NULL,
    rationale       TEXT,
    applicability   TEXT,
    tier            TEXT CHECK(tier IN ('mandatory','recommended','aspirational'))
);

-- Architecture Patterns
CREATE TABLE architecture_patterns (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    problem             TEXT,
    solution            TEXT,
    forces              TEXT,                      -- JSON array
    consequences_json   TEXT,                      -- {benefits,drawbacks,tradeoffs}
    anti_patterns       TEXT,                      -- JSON array
    maturity             TEXT CHECK(maturity IN ('emerging','established','canonical','deprecated'))
);

-- Guardrails (v0.4.0 : renamed from standards, ADR-0004 D4; adds enforcement)
CREATE TABLE guardrails (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    enforcement     TEXT NOT NULL CHECK(enforcement IN ('advisory','automated-warn','automated-block','platform-enforced')),
    domain          TEXT,
    source          TEXT,
    url             TEXT,
    coverage        TEXT                           -- JSON array
);

-- Blueprints (v0.4.0 : renamed from reference_models, ADR-0004 D5)
CREATE TABLE blueprints (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    domain              TEXT,
    abstraction_level   TEXT CHECK(abstraction_level IN ('conceptual','logical','physical')),
    scope               TEXT,
    layers_json         TEXT                         -- JSON array of {name,description,components}
);

-- Capabilities
-- CR-003 (CR-3B): maturity_level removed : intrinsic maturity on architectural
-- entities is an anti-pattern; maturity moves to the Assessment model (CR-5).
CREATE TABLE capabilities (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    capability_type TEXT CHECK(capability_type IN ('business','technical','hybrid')),
    domain          TEXT
);

-- Processes
-- v3.0.0-alpha: replaced process_type (4-value legacy enum) with two
-- orthogonal axes (process_intent, process_audience) per
-- docs/process-type-taxonomy.md. Mirrors schemas/entities/process.json.
CREATE TABLE processes (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    process_intent      TEXT NOT NULL CHECK(process_intent IN ('operational','support','management')),
    process_audience    TEXT NOT NULL CHECK(process_audience IN (
                            'governance-existence',
                            'strategy-direction',
                            'agency-organization',
                            'party-relationship',
                            'product-value',
                            'enablement-operations',
                            'finance-accounting'
                            )),
    trigger             TEXT,
    outcome             TEXT
);

-- Business Objects (v1.0.0-alpha)
-- Atom of the ECF matrix. The (ecf_domain, ecf_stage) tuple places the object
-- in a specific matrix cell. object_class / object_subclass are free-form
-- (e.g. customer / retail-customer). current_state is a domain-specific
-- business label distinct from the universal ecf_stage coordinate. State
-- history + identity are stored as JSON for flexibility.
CREATE TABLE business_objects (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    object_class        TEXT NOT NULL,
    object_subclass     TEXT,
    ecf_domain          TEXT NOT NULL CHECK(ecf_domain IN (
                            'governance-existence',
                            'strategy-direction',
                            'agency-organization',
                            'party-relationship',
                            'product-value',
                            'enablement-operations',
                            'finance-accounting'
                            )),
    ecf_stage           TEXT NOT NULL CHECK(ecf_stage IN (
                            'conceive','design','build','activate','operate','improve','retire')),
    current_state       TEXT,
    state_history_json  TEXT,    -- JSON array of BusinessObjectStateTransition
    identity_json       TEXT     -- JSON BusinessObjectIdentity { primary_id, external_ids }
);
CREATE INDEX ix_business_objects_ecf ON business_objects(ecf_domain, ecf_stage);
CREATE INDEX ix_business_objects_class ON business_objects(object_class);

-- Organizational Units (v1.0.0-alpha)
-- Owner of capabilities, runner of processes, custodian of business objects.
-- (ou_type, ou_scope, ou_lifecycle) classify the structural / temporal shape;
-- ecf_domain + ecf_stage are the optional primary coordinates when the unit
-- primarily serves one cell of the ECF matrix. CR-003: hierarchy moved to
-- composes relationship instances (parent_ou/child_ous removed).
CREATE TABLE organizational_units (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    ou_type             TEXT NOT NULL CHECK(ou_type IN (
                            'business-unit','division','department','team',
                            'role-cluster','virtual-team','governance-body',
                            'external-partner-role')),
    ou_scope            TEXT NOT NULL CHECK(ou_scope IN (
                            'individual','team','departmental','division',
                            'enterprise','ecosystem')),
    ou_lifecycle        TEXT NOT NULL CHECK(ou_lifecycle IN (
                            'permanent','temporary','ad-hoc','sunsetting')),
    ecf_domain          TEXT CHECK(ecf_domain IN (
                            'governance-existence',
                            'strategy-direction',
                            'agency-organization',
                            'party-relationship',
                            'product-value',
                            'enablement-operations',
                            'finance-accounting'
                            )),
    ecf_stage           TEXT CHECK(ecf_stage IN (
                            'conceive','design','build','activate','operate','improve','retire')),
    cost_center         TEXT,
    head_count          INTEGER
);
CREATE INDEX ix_organizational_units_type ON organizational_units(ou_type);

-- Business Services
CREATE TABLE business_services (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    service_type    TEXT CHECK(service_type IN ('internal','external','partner','public')),
    sla_json        TEXT
);

-- Solution Components
CREATE TABLE solution_components (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    component_type      TEXT CHECK(component_type IN ('application','infrastructure','integration')),
    deployment_model    TEXT CHECK(deployment_model IN ('on-premise','iaas','paas','saas','faas','hybrid','multi-cloud')),
    technology_stack    TEXT,                      -- JSON array of Technology IDs
    security_classification TEXT CHECK(security_classification IN ('public','internal','confidential','restricted'))
);

-- Metrics
CREATE TABLE metrics (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    metric_type         TEXT CHECK(metric_type IN ('kpi','health','maturity','performance','adoption','compliance','risk')),
    unit                TEXT NOT NULL,
    measurement_method  TEXT,
    baseline_value      TEXT,
    target_value        TEXT,
    thresholds_json     TEXT,
    frequency           TEXT CHECK(frequency IN ('realtime','hourly','daily','weekly','monthly','quarterly'))
);

-- Concepts (v0.4.0 : merged from glossary_terms + taxonomy_nodes, ADR-0004 D2)
CREATE TABLE concepts (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    definition      TEXT NOT NULL,
    abbreviation    TEXT,
    synonyms        TEXT,                          -- JSON array
    usage_context   TEXT
);

-- ═══════════════════════════════════════════════════════════
-- Relationships (polymorphic with type discriminator)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE relationships (
    id              TEXT PRIMARY KEY,
    source_id       TEXT NOT NULL REFERENCES entities(id),
    target_id       TEXT NOT NULL REFERENCES entities(id),
    relationship_type TEXT NOT NULL CHECK(relationship_type IN (
        'composes',
        'aggregates',
        'specializes',
        'instantiates',
        'realizes',
        'implements',
        'operationalizes',
        'depends-on',
        'requires',
        'enables',
        'constrains',
        'flows-to',
        'produces',
        'consumes',
        'exchanges',
        'serves',
        'provides',
        'uses',
        'exposes',
        'performs',
        'executes',
        'orchestrates',
        'triggers',
        'governs',
        'mandates',
        'controls',
        'owns',
        'accountable-for',
        'responsible-for',
        'threatens',
        'represents',
        'informs',
        'curates',
        'publishes',
        'subscribes-to',
        'trained-on',
        'derived-from',
        'assessed-by',
        'measured-by',
        'evidenced-by',
        'benchmarked-against',
        'transitions-to',
        'replaces',
        'supersedes',
        'migrates-to',
        'maps-to',
        'traces-to',
        'supports',
        -- v1.0.0 (CR-022 closure): new relationship type introduced in the IS
        -- Semantic Architecture programme (CR-017..CR-021). See
        -- metamodel/dea-metamodel.yaml relationships[].id for canonical kebab-case ids.
        'specifies'
    )),
    -- CR-002 §6/§20: instance metadata
    status          TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('proposed','active','deprecated','retired')),
    effective_from  TEXT,
    effective_to    TEXT,
    confidence      REAL CHECK(confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    asserted_by     TEXT,
    rationale       TEXT,
    evidence        TEXT,
    provenance_json TEXT CHECK(provenance_json IS NULL OR json_valid(provenance_json)),
    mapping_kind    TEXT CHECK(mapping_kind IS NULL OR mapping_kind IN ('equivalent','broader','narrower','related','traceability','external-crosswalk')),
    -- deprecated pre-0.7.0 columns retained for readability (CR-2G)
    weight          REAL,
    bidirectional   INTEGER NOT NULL DEFAULT 0,
    description     TEXT,
    provenance      TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    deleted         INTEGER NOT NULL DEFAULT 0,
    UNIQUE(source_id, target_id, relationship_type)
);

CREATE INDEX idx_rel_source     ON relationships(source_id);
CREATE INDEX idx_rel_target     ON relationships(target_id);
CREATE INDEX idx_rel_type       ON relationships(relationship_type);

-- ═══════════════════════════════════════════════════════════
-- Cross-references (entity-to-entity lookup arrays)
-- Stored as JSON arrays on the primary entity for fast graph traversal.
-- ═══════════════════════════════════════════════════════════

CREATE TABLE entity_cross_refs (
    entity_id       TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    ref_type        TEXT NOT NULL,   -- e.g. 'related_patterns', 'related_tenets'
    ref_ids         TEXT NOT NULL,   -- JSON array of entity IDs
    PRIMARY KEY (entity_id, ref_type)
);

-- ═══════════════════════════════════════════════════════════
-- Metamodel version tracking
-- ═══════════════════════════════════════════════════════════

CREATE TABLE schema_version (
    version      TEXT PRIMARY KEY,
    applied_at   TEXT NOT NULL DEFAULT (datetime('now')),
    notes        TEXT
);

INSERT INTO schema_version (version, notes) VALUES ('0.1.0-alpha', 'Initial DEA metamodel schema');


-- Core ontology concretes (CR-4 §27)
CREATE TABLE IF NOT EXISTS decisions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT
);

CREATE TABLE IF NOT EXISTS outcomes (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT
);

CREATE TABLE IF NOT EXISTS requirements (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT
);

CREATE TABLE IF NOT EXISTS constraints (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT
);

CREATE TABLE IF NOT EXISTS changes (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT
);

-- ═══════════════════════════════════════════════════════════
-- Metamodel provenance (CR-001): source version this projection derives from

-- ═══════════════════════════════════════════════════════════
-- CR-5: Assessment, Measurement & DMM integration (profile dea:assessment)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS assessments (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    framework_ref   TEXT,
    assessment_status TEXT,
    started_at      TEXT,
    completed_at    TEXT
);

CREATE TABLE IF NOT EXISTS assessment_frameworks (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    framework_version TEXT,
    authority       TEXT
);

CREATE TABLE IF NOT EXISTS assessment_dimensions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    dimension_order INTEGER
);

CREATE TABLE IF NOT EXISTS assessment_criteria (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    dimension_ref   TEXT,
    evaluation_guidance TEXT
);

CREATE TABLE IF NOT EXISTS indicators (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    criterion_ref   TEXT,
    signal_type     TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT,
    observed_at     TEXT,
    source_ref      TEXT
);

CREATE TABLE IF NOT EXISTS measures (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    indicator_ref   TEXT,
    value           REAL,
    unit_ref        TEXT,
    observed_at     TEXT
);

CREATE TABLE IF NOT EXISTS scores (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    value           REAL,
    scale_ref       TEXT
);

CREATE TABLE IF NOT EXISTS scales (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    scale_type      TEXT,
    minimum         REAL,
    maximum         REAL
);

CREATE TABLE IF NOT EXISTS units (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    symbol          TEXT,
    quantity_kind   TEXT
);

CREATE TABLE IF NOT EXISTS assessment_results (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    assessment_ref  TEXT,
    subject_ref     TEXT,
    criterion_ref   TEXT,
    score_value     REAL,
    maturity_level_ref TEXT,
    confidence_value REAL,
    state_role      TEXT,
    assessed_at     TEXT,
    valid_from      TEXT
);

CREATE TABLE IF NOT EXISTS assessment_subjects (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    entity_ref      TEXT
);

CREATE TABLE IF NOT EXISTS assessment_scopes (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    scope_kind      TEXT
);

CREATE TABLE IF NOT EXISTS assessment_targets (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    subject_ref     TEXT,
    target_value    REAL,
    target_level_ref TEXT,
    target_date     TEXT
);

CREATE TABLE IF NOT EXISTS assessment_gaps (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    subject_ref     TEXT,
    current_result_ref TEXT,
    target_ref      TEXT,
    gap_value       REAL
);

CREATE TABLE IF NOT EXISTS maturity_models (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    framework_ref   TEXT,
    model_version   TEXT,
    level_count     INTEGER
);

CREATE TABLE IF NOT EXISTS maturity_levels (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    model_ref       TEXT,
    level_order     INTEGER,
    level_name      TEXT
);

CREATE TABLE IF NOT EXISTS maturity_scales (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    model_ref       TEXT,
    minimum         REAL,
    maximum         REAL
);

CREATE TABLE IF NOT EXISTS maturity_rules (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    rule_type       TEXT,
    expression      TEXT
);

CREATE TABLE IF NOT EXISTS aggregation_rules (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    rule_kind       TEXT,
    expression      TEXT
);

CREATE TABLE IF NOT EXISTS scoring_rules (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    expression      TEXT,
    output_scale_ref TEXT
);

CREATE TABLE IF NOT EXISTS maturity_mapping_rules (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    score_scale_ref TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    evidence_type   TEXT,
    source_ref      TEXT,
    reference       TEXT,
    collected_at    TEXT,
    collected_by    TEXT
);

CREATE TABLE IF NOT EXISTS evidence_sources (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    source_kind     TEXT,
    system_ref      TEXT,
    locator         TEXT
);

CREATE TABLE IF NOT EXISTS evidence_artifacts (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    artifact_type   TEXT,
    artifact_ref    TEXT,
    collected_at    TEXT
);

CREATE TABLE IF NOT EXISTS benchmarks (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    framework_ref   TEXT,
    population_ref  TEXT,
    authority       TEXT,
    published_at    TEXT
);

CREATE TABLE IF NOT EXISTS benchmark_populations (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    segment         TEXT,
    population_size INTEGER
);

CREATE TABLE IF NOT EXISTS benchmark_references (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    benchmark_ref   TEXT,
    value           REAL,
    percentile      REAL
);


-- ═══════════════════════════════════════════════════════════
-- CR-5: Assessment, Measurement & DMM integration (profile dea:assessment)
-- ═══════════════════════════════════════════════════════════






























-- ═══════════════════════════════════════════════════════════
-- CR-6: Temporal, Lifecycle & Transition semantics (profile dea:lifecycle)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS temporal_intervals (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    valid_from      TEXT,
    valid_to        TEXT,
    recorded_at     TEXT,
    observed_at     TEXT
);

CREATE TABLE IF NOT EXISTS lifecycle_states (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    state_name      TEXT,
    sequence        INTEGER,
    terminal        INTEGER
);

CREATE TABLE IF NOT EXISTS lifecycle_events (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    event_type      TEXT,
    subject_ref     TEXT,
    occurred_at     TEXT,
    actor           TEXT,
    reason          TEXT
);

CREATE TABLE IF NOT EXISTS lifecycle_transitions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    from_state_ref  TEXT,
    to_state_ref    TEXT,
    entity_scope    TEXT,
    reactivation    INTEGER
);

CREATE TABLE IF NOT EXISTS transitions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    from_state_ref  TEXT,
    to_state_ref    TEXT,
    change_ref      TEXT,
    planned_start   TEXT,
    planned_end     TEXT,
    transition_status TEXT
);

CREATE TABLE IF NOT EXISTS architecture_states (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    state_kind      TEXT,
    captured_at     TEXT,
    valid_at        TEXT,
    scope           TEXT
);

CREATE TABLE IF NOT EXISTS baseline_states (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    captured_at     TEXT,
    valid_at        TEXT,
    adopted_by      TEXT
);

CREATE TABLE IF NOT EXISTS current_states (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    as_of           TEXT,
    scope           TEXT
);

CREATE TABLE IF NOT EXISTS target_states (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    target_date     TEXT,
    approved_by     TEXT
);

CREATE TABLE IF NOT EXISTS transition_states (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    sequence        INTEGER,
    phase_ref       TEXT
);

CREATE TABLE IF NOT EXISTS scenarios (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    scenario_status TEXT
);

CREATE TABLE IF NOT EXISTS scenario_states (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    scenario_ref    TEXT
);

CREATE TABLE IF NOT EXISTS scenario_assumptions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    scenario_ref    TEXT,
    statement       TEXT
);

CREATE TABLE IF NOT EXISTS architecture_snapshots (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    scope           TEXT,
    captured_at     TEXT,
    valid_at        TEXT,
    model_version   TEXT,
    approved        INTEGER,
    revision_of     TEXT
);

CREATE TABLE IF NOT EXISTS architecture_deltas (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    from_state_ref  TEXT,
    to_state_ref    TEXT
);

CREATE TABLE IF NOT EXISTS versions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    entity_ref      TEXT,
    version_number  TEXT,
    predecessor_ref TEXT,
    released_at     TEXT
);


-- ═══════════════════════════════════════════════════════════
-- CR-7: Decision, Intent, Policy & Governance (profile dea:governance)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS intents (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    intent_kind        TEXT
    statement          TEXT
);

CREATE TABLE IF NOT EXISTS objectives (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    intent_ref         TEXT
    statement          TEXT
    target_value       TEXT
    unit               TEXT
);

CREATE TABLE IF NOT EXISTS policies (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    policy_kind        TEXT
    statement          TEXT
    applicability      TEXT
);

CREATE TABLE IF NOT EXISTS policy_rules (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    policy_ref         TEXT
    expression         TEXT
    applies_to         TEXT
);

CREATE TABLE IF NOT EXISTS policy_evaluations (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    policy_ref         TEXT
    subject_ref        TEXT
    action_ref         TEXT
    context            TEXT
);

CREATE TABLE IF NOT EXISTS policy_decisions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    evaluation_ref     TEXT
    decision           TEXT
    decided_at         TEXT
);

CREATE TABLE IF NOT EXISTS decision_options (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    decision_ref       TEXT
    cost               TEXT
    benefit            TEXT
    risk               TEXT
);

CREATE TABLE IF NOT EXISTS decision_criteria (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    criterion_kind     TEXT
    weight             TEXT
    evaluation_guidance TEXT
);

CREATE TABLE IF NOT EXISTS decision_records (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    decision_ref       TEXT
    recorded_at        TEXT
    authority_ref      TEXT
    rationale          TEXT
);

CREATE TABLE IF NOT EXISTS authorities (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    scope              TEXT
    limits             TEXT
    valid_from         TEXT
    valid_to           TEXT
);

CREATE TABLE IF NOT EXISTS delegations (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    delegator_ref      TEXT
    delegate_ref       TEXT
    authority_ref      TEXT
    scope              TEXT
);

CREATE TABLE IF NOT EXISTS governance_bodies (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    body_kind          TEXT
    mandate            TEXT
);

CREATE TABLE IF NOT EXISTS governance_rules (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    body_ref           TEXT
    statement          TEXT
    enforced_by        TEXT
);

CREATE TABLE IF NOT EXISTS actions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    action_kind        TEXT
    decision_ref       TEXT
    reversibility      TEXT
    materiality        TEXT
);

-- ═══════════════════════════════════════════════════════════
-- CR-7: Agentic semantics (profile dea:agentic)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS agents (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    agent_type         TEXT
    purpose            TEXT
    autonomy_level_ref TEXT
    owner_ref          TEXT
);

CREATE TABLE IF NOT EXISTS agent_profiles (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    agent_ref          TEXT
    decision_scope     TEXT
    action_scope       TEXT
    human_oversight_ref TEXT
);

CREATE TABLE IF NOT EXISTS agent_skills (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    purpose            TEXT
    inputs             TEXT
    outputs            TEXT
    preconditions      TEXT
);

CREATE TABLE IF NOT EXISTS tools (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    tool_kind          TEXT
    endpoint_ref       TEXT
);

CREATE TABLE IF NOT EXISTS tool_permissions (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    tool_ref           TEXT
    agent_ref          TEXT
    scope              TEXT
    constraints        TEXT
);

CREATE TABLE IF NOT EXISTS orchestrators (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    coordination_scope TEXT
);

CREATE TABLE IF NOT EXISTS controllers (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    control_scope      TEXT
);

CREATE TABLE IF NOT EXISTS orchestrations (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    orchestrator_ref   TEXT
    workflow_ref       TEXT
    orchestration_status TEXT
);

CREATE TABLE IF NOT EXISTS workflows (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    definition         TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    workflow_ref       TEXT
    sequence           TEXT
    task_kind          TEXT
);

CREATE TABLE IF NOT EXISTS autonomy_policies (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    policy_ref         TEXT
    rules              TEXT
);

CREATE TABLE IF NOT EXISTS autonomy_levels (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    model_ref          TEXT
    level_order        TEXT
    level_name         TEXT
);

CREATE TABLE IF NOT EXISTS human_oversight (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    oversight_pattern  TEXT
    overseer_ref       TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    approver_ref       TEXT
    subject_ref        TEXT
    decision           TEXT
    approved_at        TEXT
);

CREATE TABLE IF NOT EXISTS escalations (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    trigger            TEXT
    raised_by          TEXT
    target_ref         TEXT
    reason             TEXT
);

CREATE TABLE IF NOT EXISTS agentic_systems (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    system_purpose     TEXT
);

CREATE TABLE IF NOT EXISTS agent_opportunities (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    subject_ref        TEXT
    potential_agent_ref TEXT
    expected_value     TEXT
    risk               TEXT
);

CREATE TABLE IF NOT EXISTS memories (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    memory_kind        TEXT
    retention          TEXT
    controller_ref     TEXT
);

-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS metamodel_meta (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL
);

INSERT OR REPLACE INTO metamodel_meta (key, value) VALUES
    ('metamodel_version', '1.0.0'),
    ('normative_source', 'metamodel/dea-metamodel.yaml');

-- ═══════════════════════════════════════════════════════════
-- External references (CR-3P): external identifiers are separate from OpenDEA identity
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS entity_external_references (
    entity_id       TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    system          TEXT NOT NULL,
    identifier      TEXT NOT NULL,
    UNIQUE(entity_id, system, identifier)
);

CREATE INDEX IF NOT EXISTS ix_ext_ref ON entity_external_references(system, identifier);

-- ═══════════════════════════════════════════════════════════
-- Metric programme tables (CR-MET-001..012)
--
-- Generated from the canonical JSON Schemas: column names and CHECK
-- constraints are derived from each schema's properties and enums, so
-- these cannot drift from metamodel/dea-metamodel.yaml. Regenerate
-- rather than hand-edit when a column needs to change. The artifact
-- drift gate (.github/scripts/validate_artifacts.py) enforces that the
-- declared table for every entity exists.
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS measurements (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    applies_metric       TEXT,
    measures_subject     TEXT,
    measurement_method   TEXT,
    measurement_time     TEXT,
    reporting_period_start TEXT,
    reporting_period_end TEXT,
    measurement_source   TEXT,
    measurement_status   TEXT CHECK(measurement_status IN ('planned','initiated','in_progress','pending_validation','validated','completed','failed','cancelled','rejected','superseded')),
    execution_mode       TEXT CHECK(execution_mode IN ('automated','manual','calculated','aggregated','external','assessed','simulated','ai_assisted')),
    state_transitions    TEXT,
    logical_measurement_event TEXT,
    configuration_reference TEXT,
    evidence_reference   TEXT,
    context              TEXT,
    temporal             TEXT,
    responsible_party    TEXT,
    configuration        TEXT
);

CREATE TABLE IF NOT EXISTS measurement_observations (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    produced_by          TEXT,
    value                REAL,
    observed_at          TEXT,
    valid_from           TEXT,
    valid_to             TEXT,
    reporting_period_start TEXT,
    reporting_period_end TEXT,
    observation_quality  TEXT,
    observation_status   TEXT CHECK(observation_status IN ('proposed','active','superseded','retired')),
    verification_state   TEXT CHECK(verification_state IN ('unverified','ai_estimated','independently_verified','human_verified')),
    supersedes_observation TEXT,
    provenance_reference TEXT,
    uncertainty_reference TEXT,
    comparability_requirements TEXT,
    precision            REAL,
    evidence_reference   TEXT,
    unit                 TEXT,
    temporal             TEXT,
    record_state         TEXT CHECK(record_state IN ('original','corrected','superseded','invalid','retracted')),
    correction_reason    TEXT,
    corrects_observation_ref TEXT,
    supersedes_observation_reason TEXT,
    confidence           REAL
);

CREATE TABLE IF NOT EXISTS baselines (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    kind                 TEXT CHECK(kind IN ('historical','initial','strategic','operational','regulatory','scenario_derived')),
    approval_status      TEXT CHECK(approval_status IN ('draft','proposed','approved','retired')),
    reference_metric_ref TEXT,
    subject_ref          TEXT,
    reference_value      TEXT,
    establishment_date   TEXT,
    applicable_period    TEXT,
    organizational_scope TEXT,
    measurement_methodology TEXT,
    source_evidence      TEXT,
    supersedes_baselines TEXT
);

CREATE TABLE IF NOT EXISTS performance_targets (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    target_metric_ref    TEXT,
    target_subject_ref   TEXT,
    target_scope         TEXT,
    target_value         REAL,
    target_range         TEXT,
    target_direction     TEXT CHECK(target_direction IN ('increase','decrease','maintain','bounded','exact_match')),
    effective_period     TEXT,
    owner_ref            TEXT,
    associated_objective_ref TEXT,
    approval_status      TEXT CHECK(approval_status IN ('draft','proposed','approved','retired')),
    supporting_rationale TEXT
);

CREATE TABLE IF NOT EXISTS thresholds (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    threshold_metric_ref TEXT,
    threshold_value      TEXT,
    threshold_level      TEXT CHECK(threshold_level IN ('critical','warning','acceptable','optimal')),
    direction            TEXT CHECK(direction IN ('higher_is_better','lower_is_better','bounded_optimum','exact_match')),
    effective_period     TEXT,
    owner_ref            TEXT,
    escalation_rule_ref  TEXT
);

CREATE TABLE IF NOT EXISTS performance_interpretations (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    interprets_metric_ref TEXT,
    interprets_observation_ref TEXT,
    interpretation_kind  TEXT CHECK(interpretation_kind IN ('variance_evaluation','threshold_evaluation','benchmark_evaluation','composite_judgment')),
    interpretation_state TEXT CHECK(interpretation_state IN ('exceeds_target','meets_target','within_tolerance','warning','critical','unknown')),
    reference_used       TEXT,
    absolute_variance    REAL,
    relative_variance    REAL,
    narrative            TEXT,
    evaluator_ref        TEXT,
    evaluated_at         TEXT
);

CREATE TABLE IF NOT EXISTS indicator_designations (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    designation_type     TEXT CHECK(designation_type IN ('KPI','KRI','KCI','SLI','Operational')),
    associated_metric_ref TEXT,
    management_purpose   TEXT,
    associated_objective_ref TEXT,
    organizational_scope TEXT,
    accountable_owner_ref TEXT,
    reporting_frequency  TEXT CHECK(reporting_frequency IN ('real_time','hourly','daily','weekly','monthly','quarterly','semi_annual','annual')),
    target_reference     TEXT,
    threshold_reference  TEXT,
    escalation_rules     TEXT,
    measurement_orientation TEXT CHECK(measurement_orientation IN ('leading','lagging','neutral')),
    effective_period     TEXT,
    approval_status      TEXT CHECK(approval_status IN ('draft','proposed','approved','retired'))
);

CREATE TABLE IF NOT EXISTS reporting_periods (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    period_type          TEXT CHECK(period_type IN ('instantaneous','point_in_time','fixed_duration','rolling','cumulative','event_based','irregular')),
    period_semantics     TEXT CHECK(period_semantics IN ('calendar','fiscal','rolling','event_based','custom')),
    period_start         TEXT,
    period_end           TEXT,
    anchor_reference     TEXT,
    window_size          TEXT,
    interval_count       REAL,
    calendar_reference   TEXT,
    fiscal_year_ref      TEXT,
    effective_from       TEXT,
    effective_to         TEXT,
    organizational_scope_ref TEXT
);

CREATE TABLE IF NOT EXISTS provenances (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    source_ref           TEXT,
    source_record_ref    TEXT,
    collection_activity  TEXT,
    calculation_activity TEXT,
    transformation_chain TEXT,
    responsible_party_ref TEXT,
    configuration_ref    TEXT,
    formula_version_ref  TEXT,
    metric_version_ref   TEXT,
    evidence_refs        TEXT,
    timestamps           TEXT,
    reproducibility      TEXT
);

CREATE TABLE IF NOT EXISTS analytical_results (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    result_type          TEXT CHECK(result_type IN ('estimate','forecast','simulation_result','recommendation')),
    analytical_capability TEXT CHECK(analytical_capability IN ('descriptive','diagnostic','predictive','prescriptive','comparative','scenario_simulation')),
    subject_ref          TEXT,
    value                REAL,
    unit                 TEXT,
    reporting_period_ref TEXT,
    horizon_ref          TEXT,
    evidence_refs        TEXT,
    provenance_reference TEXT,
    confidence           REAL,
    uncertainty          TEXT,
    model_ref            TEXT,
    scenario_ref         TEXT,
    aggregation_rule_ref TEXT,
    alternative_considered TEXT,
    responsible_party_ref TEXT
);

CREATE TABLE IF NOT EXISTS correlations (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    source_phenomenon_ref TEXT,
    target_phenomenon_ref TEXT,
    coefficient          REAL,
    method               TEXT,
    sample_size          REAL,
    reporting_period_ref TEXT,
    evidence_refs        TEXT,
    confounder_candidates TEXT,
    confusion_guard      INTEGER CHECK(confusion_guard IN (0,1)),
    strength             TEXT CHECK(strength IN ('negligible','weak','moderate','strong','very_strong')),
    directional_note     TEXT,
    provenance_reference TEXT
);

CREATE TABLE IF NOT EXISTS causal_hypotheses (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    cause_ref            TEXT,
    effect_ref           TEXT,
    mechanism            TEXT,
    confidence           REAL,
    uncertainty          TEXT,
    validation_state     TEXT CHECK(validation_state IN ('asserted','correlation_supported','experiment_running','validated','refuted')),
    supporting_correlation_refs TEXT,
    counter_evidence     TEXT,
    falsification_test   TEXT,
    responsible_party_ref TEXT
);

-- ══════════════════════════════════════════════════════════════════════
-- Generated entity tables.
--
-- Column names and CHECK constraints are derived from each entity's canonical
-- JSON Schema (properties and enums), so they cannot drift from
-- metamodel/dea-metamodel.yaml. Regenerate rather than hand-edit:
--     python3 .github/scripts/generate_db_and_ts_artifacts.py
-- The artifact drift gate (.github/scripts/validate_artifacts.py) enforces that
-- every entity's declared table exists.
-- ══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS collaboration_agreements (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    agreement_kind       TEXT CHECK(agreement_kind IN ('cooperative','mandated')),
    effective_from       TEXT,
    effective_to         TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS ecosystem_actors (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    actor_kind           TEXT CHECK(actor_kind IN ('customer','supplier','partner','regulator','platform','competitor')),
    exchange_directions  TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS ecosystem_platforms (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    platform_kind        TEXT CHECK(platform_kind IN ('marketplace','developer-portal','partner-api-program','data-exchange')),
    participant_count    REAL,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS stakeholders (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    stakeholder_type     TEXT CHECK(stakeholder_type IN ('customer','partner','supplier','regulator','investor','community','board')),
    primary_contact      TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS value_exchanges (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    flow_type            TEXT CHECK(flow_type IN ('information','goods','funds','service')),
    direction            TEXT CHECK(direction IN ('inbound','outbound','bidirectional')),
    counterparty_ref     TEXT,
    payload_refs         TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS controls (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    control_type         TEXT CHECK(control_type IN ('preventive','detective','corrective')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS experiments (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    hypothesis           TEXT,
    signal_ref           TEXT,
    outcome              TEXT CHECK(outcome IN ('pending','validated','invalidated','inconclusive')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS regulations (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    jurisdiction         TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS risks (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    risk_category        TEXT CHECK(risk_category IN ('strategic','operational','regulatory','technology','financial','reputational')),
    likelihood           TEXT CHECK(likelihood IN ('rare','unlikely','possible','likely','almost-certain')),
    impact               TEXT CHECK(impact IN ('negligible','minor','moderate','major','severe')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS signals (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    signal_source        TEXT CHECK(signal_source IN ('market','technology','regulatory','competitor','customer')),
    strength             TEXT CHECK(strength IN ('weak','emerging','strong')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS technology_radar_entries (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    radar_ring           TEXT CHECK(radar_ring IN ('assess','trial','adopt','hold')),
    graduates_to         TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS actors (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    actor_type           TEXT CHECK(actor_type IN ('human','team','system','ai-agent','hybrid')),
    scope                TEXT CHECK(scope IN ('individual','team','departmental','enterprise','ecosystem')),
    links                TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS business_functions (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    owning_unit_ref      TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS change_initiatives (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    change_scope         TEXT CHECK(change_scope IN ('skills','roles','culture','structure')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS financial_resources (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    liquidity            TEXT CHECK(liquidity IN ('cash','near-liquid','credit-facility','instrument','other')),
    currency             TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS intangible_resources (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    protection_type      TEXT CHECK(protection_type IN ('patent','trademark','copyright','trade-secret','license','brand','other')),
    protection_expiry    TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS physical_resources (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    maintenance_regime   TEXT,
    location             TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS resources (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    resource_kind        TEXT CHECK(resource_kind IN ('financial','physical','intangible')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS roles (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS skills (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    skill_domain         TEXT,
    proficiency_levels   TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS information_assets (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    consumption_form     TEXT CHECK(consumption_form IN ('report','dashboard','document','feed','other')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS knowledge_assets (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    knowledge_form       TEXT CHECK(knowledge_form IN ('playbook','runbook','guideline','case-study','lesson-learned','other')),
    review_cycle         TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS model_deployments (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    model_ref            TEXT,
    environment          TEXT CHECK(environment IN ('dev','staging','production')),
    deployment_kind      TEXT CHECK(deployment_kind IN ('api-endpoint','batch','embedded','streaming')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS information_system_components (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS application_components (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    deployment_unit      TEXT CHECK(deployment_unit IN ('service','batch-job','scheduled-task','event-handler','lambda','daemon')),
    runtime              TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS integration_interfaces (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS infrastructure_components (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    infrastructure_type  TEXT CHECK(infrastructure_type IN ('compute','network','storage','security','container','serverless','database-host')),
    iac_tool             TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS integration_components (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    integration_pattern  TEXT CHECK(integration_pattern IN ('api-gateway','message-queue','file-transfer','event-stream','etl','rpc','graphql-federation')),
    direction            TEXT CHECK(direction IN ('inbound','outbound','bidirectional')),
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS information_system_services (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS information_system_functions (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    is_part_of           TEXT,
    enabled_by_components TEXT,
    realizes_capability  TEXT,
    enables_process      TEXT,
    consumes_data        TEXT,
    produces_data        TEXT,
    consumes_events      TEXT,
    produces_events      TEXT,
    tags                 TEXT
);

CREATE TABLE IF NOT EXISTS technologies (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    technology_category  TEXT CHECK(technology_category IN ('language','framework','runtime','database','library','build-tool','ci-cd','monitoring','orchestration','platform')),
    vendor               TEXT,
    version_requirement  TEXT,
    tags                 TEXT,
    adoption_status      TEXT CHECK(adoption_status IN ('approved','deprecated','banned','experimental'))
);
