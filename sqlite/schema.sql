-- DEA Metamodel SQLite Schema
-- Version: 0.1.0-alpha
-- All tables include source tracking and soft-delete for auditability.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ═══════════════════════════════════════════════════════════
-- Entity tables
-- ═══════════════════════════════════════════════════════════

CREATE TABLE entities (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL CHECK(type IN (
        'Principle','ArchitecturePattern','Standard','ReferenceModel',
        'Capability','Process','BusinessService','SolutionComponent',
        'ApplicationComponent','InfrastructureComponent','IntegrationComponent',
        'Technology','Metric','GlossaryTerm','TaxonomyNode','Viewpoint'
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

-- Principles
CREATE TABLE principles (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    statement       TEXT NOT NULL,
    rationale       TEXT,
    applicability   TEXT,                          -- JSON array
    exceptions      TEXT,                          -- JSON array
    conflicts_with  TEXT,                          -- JSON array of IDs
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

-- Standards
CREATE TABLE standards (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    standard_body   TEXT,
    domain          TEXT,
    url             TEXT,
    license         TEXT,
    coverage        TEXT,                          -- JSON array
    conforms_to     TEXT                           -- JSON array
);

-- Reference Models
CREATE TABLE reference_models (
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

-- Glossary Terms
CREATE TABLE glossary_terms (
    entity_id       TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    definition      TEXT NOT NULL,
    abbreviation    TEXT,
    synonyms        TEXT,                          -- JSON array
    antonyms        TEXT,                          -- JSON array
    usage_context   TEXT,
    metamodel_entity TEXT
);

-- Viewpoints
CREATE TABLE viewpoints (
    entity_id               TEXT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    stakeholder             TEXT NOT NULL,
    concern                 TEXT NOT NULL,
    entities_included       TEXT,                  -- JSON array
    entities_excluded       TEXT,                  -- JSON array
    relationships_included TEXT,                  -- JSON array
    filter_criteria_json   TEXT,
    presentation_format     TEXT CHECK(presentation_format IN ('diagram','table','matrix','dashboard','narrative','multi'))
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
    ref_type        TEXT NOT NULL,   -- e.g. 'related_patterns', 'related_principles'
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
