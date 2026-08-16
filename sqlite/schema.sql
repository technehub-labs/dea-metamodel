-- DEA Metamodel SQLite Schema
-- Version: 0.6.0
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
CREATE TABLE capabilities (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    capability_type TEXT CHECK(capability_type IN ('business','technical','hybrid')),
    domain          TEXT,
    maturity_level  TEXT CHECK(maturity_level IN ('nascent','emerging','defined','managed','optimizing')),
    owner           TEXT
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
    owner               TEXT,
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
    identity_json       TEXT,    -- JSON BusinessObjectIdentity { primary_id, external_ids }
    owner               TEXT
);
CREATE INDEX ix_business_objects_ecf ON business_objects(ecf_domain, ecf_stage);
CREATE INDEX ix_business_objects_class ON business_objects(object_class);

-- Organizational Units (v1.0.0-alpha)
-- Owner of capabilities, runner of processes, custodian of business objects.
-- (ou_type, ou_scope, ou_lifecycle) classify the structural / temporal shape;
-- ecf_domain + ecf_stage are the optional primary coordinates when the unit
-- primarily serves one cell of the ECF matrix. Hierarchical structure via
-- parent_ou / child_ous forms a forest under the enterprise root.
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
    parent_ou           TEXT,    -- self-reference; forest under enterprise root
    cost_center         TEXT,
    head_count          INTEGER
);
CREATE INDEX ix_organizational_units_type ON organizational_units(ou_type);
CREATE INDEX ix_organizational_units_parent ON organizational_units(parent_ou);

-- Business Services
CREATE TABLE business_services (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    service_type    TEXT CHECK(service_type IN ('internal','external','partner','public')),
    owner           TEXT,
    sla_json        TEXT
);

-- Solution Components
CREATE TABLE solution_components (
    entity_id           TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    component_type      TEXT CHECK(component_type IN ('application','infrastructure','integration')),
    deployment_model    TEXT CHECK(deployment_model IN ('on-premise','iaas','paas','saas','faas','hybrid','multi-cloud')),
    owner               TEXT,
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
    frequency           TEXT CHECK(frequency IN ('realtime','hourly','daily','weekly','monthly','quarterly')),
    owner               TEXT
);

-- Concepts (v0.4.0 — merged from glossary_terms + taxonomy_nodes, ADR-0004 D2)
CREATE TABLE concepts (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    definition      TEXT NOT NULL,
    abbreviation    TEXT,
    synonyms        TEXT,                          -- JSON array
    parent_concept  TEXT,                          -- ID of parent Concept (NULL = root)
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
        'maps-to','realizes','implements','influenced-by',
        'decomposes','orchestrates','consumes','provides',
        'governs','measured-by'
    )),
    description     TEXT,
    weight          REAL,
    provenance      TEXT,
    bidirectional   INTEGER NOT NULL DEFAULT 0,
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

-- ═══════════════════════════════════════════════════════════
-- Metamodel provenance (CR-001): source version this projection derives from
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS metamodel_meta (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL
);

INSERT OR REPLACE INTO metamodel_meta (key, value) VALUES
    ('metamodel_version', '0.6.0'),
    ('normative_source', 'metamodel/dea-metamodel.yaml');
