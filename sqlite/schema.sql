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
        'Technology','Metric','Concept'
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

-- Tenets (v0.4.0 — renamed from principles, ADR-0004 D3)
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

-- Guardrails (v0.4.0 — renamed from standards, ADR-0004 D4; adds enforcement)
CREATE TABLE guardrails (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    enforcement     TEXT NOT NULL CHECK(enforcement IN ('advisory','automated-warn','automated-block','platform-enforced')),
    domain          TEXT,
    source          TEXT,
    url             TEXT,
    coverage        TEXT                           -- JSON array
);

-- Blueprints (v0.4.0 — renamed from reference_models, ADR-0004 D5)
CREATE TABLE blueprints (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    domain              TEXT,
    abstraction_level   TEXT CHECK(abstraction_level IN ('conceptual','logical','physical')),
    scope               TEXT,
    layers_json         TEXT                         -- JSON array of {name,description,components}
);

-- Capabilities
-- CR-003 (CR-3B): maturity_level removed — intrinsic maturity on architectural
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
                            'governance-existence','supply-resources','people-organization',
                            'customer-demand','product-offering','operations-delivery','finance-value')),
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
                            'governance-existence','supply-resources','people-organization',
                            'customer-demand','product-offering','operations-delivery','finance-value')),
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
                            'governance-existence','supply-resources','people-organization',
                            'customer-demand','product-offering','operations-delivery','finance-value')),
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

-- Concepts (v0.4.0 — merged from glossary_terms + taxonomy_nodes, ADR-0004 D2)
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
        'supports'
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

CREATE TABLE IF NOT EXISTS metamodel_meta (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL
);

INSERT OR REPLACE INTO metamodel_meta (key, value) VALUES
    ('metamodel_version', '0.10.0'),
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
