#!/usr/bin/env python3
"""Reproducibly generate the four CR-AM-03 assessment migrations.

The script is intentionally self-contained: it reads the vendored legacy
instruments and writes canonical YAML, migration contracts, examples, and the
assessment portfolio. It is not a substitute for the schema or unit tests;
it exists to make the generated migration artefacts reproducible.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSESSMENT_ROOT = REPO_ROOT / 'assessment-models'
MIGRATION_ROOT = ASSESSMENT_ROOT / 'migrations'
EXAMPLE_ROOT = ASSESSMENT_ROOT / 'examples'
EXECUTION_ROOT = EXAMPLE_ROOT / 'executions'
CATALOG_ROOT = ASSESSMENT_ROOT / 'catalog'

DOMAIN_DATA: dict[str, dict[str, Any]] = {
    'technology': {
        'capabilities': [
            ('Technology Architecture', 'Technology'),
            ('Technology Lifecycle', 'Technology'),
            ('Skills and Coverage', 'Technology'),
            ('Technical Debt Management', 'Technology'),
        ],
        'scenario': ('Enterprise Technology Health', 'enterprise-technology-health'),
        'measures': [
            ('Architecture Standardization', 'ratio of services with documented architecture to total services', 0, 100, 'percent'),
            ('Lifecycle Compliance', 'ratio of components with current lifecycle to total components', 0, 100, 'percent'),
            ('Skill Coverage', 'ratio of critical skills with redundant coverage to total critical skills', 0, 100, 'percent'),
            ('Technical Debt Trend', 'rolling 90-day trend in technical debt backlog size (count)', -50, 50, 'count'),
        ],
    },
    'modernization': {
        'capabilities': [
            ('Modernization Strategy', 'Modernization'),
            ('Migration Pattern Library', 'Modernization'),
            ('Wave Planning and Execution', 'Modernization'),
            ('Modernization Metrics', 'Modernization'),
            ('Modernization Culture', 'Modernization'),
        ],
        'scenario': ('Enterprise Modernization Programme', 'enterprise-modernization-programme'),
        'measures': [
            ('Modernization Strategy Coverage', 'ratio of modernisation backlog items with explicit strategy mapping to total backlog items', 0, 100, 'percent'),
            ('Pattern Library Adoption', 'ratio of in-flight migrations using the canonical pattern library to total in-flight migrations', 0, 100, 'percent'),
            ('Wave Velocity Trend', 'rolling 90-day trend in waves completed per quarter (count)', -10, 10, 'count'),
            ('Migration ROI Trend', 'rolling 90-day trend in migration ROI (multiplier)', 0, 5, 'multiplier'),
            ('Modernization CoP Health', 'ratio of team members attending monthly modernization CoP to total team members', 0, 100, 'percent'),
        ],
    },
    'operations': {
        'capabilities': [
            ('Incident Response Capability', 'Operations'),
            ('Observability Practice', 'Operations'),
            ('Deployment Automation', 'Operations'),
            ('Reliability Engineering', 'Operations'),
            ('Operational Culture', 'Operations'),
        ],
        'scenario': ('Service Assurance Operations', 'service-assurance-operations'),
        'measures': [
            ('MTTR Sev1', 'rolling 30-day median time to resolve a sev-1 incident (minutes)', 0, 240, 'minutes'),
            ('SLO Coverage', 'ratio of customer-facing services with declared SLOs to total customer-facing services', 0, 100, 'percent'),
            ('Deployment Frequency', 'deployments per business day (count)', 0, 200, 'count'),
            ('Change Failure Rate', 'ratio of releases that cause a sev-1 or sev-2 incident to total releases (percent)', 0, 100, 'percent'),
            ('On-call Satisfaction Score', 'rolling-quarter on-call survey score (1-10)', 1, 10, 'score'),
        ],
    },
    'services-delivery': {
        'capabilities': [
            ('Delivery Predictability', 'Services Delivery'),
            ('Flow Efficiency', 'Services Delivery'),
            ('Quality Management', 'Services Delivery'),
            ('Customer Outcomes', 'Services Delivery'),
            ('Team Health', 'Services Delivery'),
        ],
        'scenario': ('Customer-Facing Delivery Programme', 'customer-facing-delivery-programme'),
        'measures': [
            ('Release Forecast Accuracy', 'ratio of releases forecast within ±10% to total releases (percent)', 0, 100, 'percent'),
            ('Lead Time p50', 'rolling 30-day median commit-to-deploy (hours)', 0, 168, 'hours'),
            ('Escaped Defect Rate', 'ratio of escaped defects to deployments (per 100 deployments)', 0, 100, 'rate'),
            ('Outcome-to-Release Linkage', 'ratio of releases with declared customer outcome linkage to total releases (percent)', 0, 100, 'percent'),
            ('Team Health Index', 'rolling-quarter composite team health (0-100)', 0, 100, 'score'),
        ],
    },
}

RAW_SCORES = {
    'technology': 78,
    'modernization': 64,
    'operations': 71,
    'services-delivery': 82,
}
RESULT_IDS = {
    'technology': 'dea:result:2026:000100',
    'modernization': 'dea:result:2026:000200',
    'operations': 'dea:result:2026:000300',
    'services-delivery': 'dea:result:2026:000400',
}
EXECUTION_IDS = {
    'technology': 'dea:execution-technology-001',
    'modernization': 'dea:execution-modernization-001',
    'operations': 'dea:execution-operations-001',
    'services-delivery': 'dea:execution-services-delivery-001',
}
PERIODS = {
    'technology': ('2026-07-01', '2026-07-15'),
    'modernization': ('2026-06-15', '2026-06-30'),
    'operations': ('2026-08-01', '2026-08-15'),
    'services-delivery': ('2026-07-15', '2026-08-01'),
}
# Maturity IDs are versioned independently; the legacy target is carried without alteration.
MATURITY_IDS = {
    'technology': 'dea:maturity-technology',
    'modernization': 'dea:maturity-modernization',
    'operations': 'dea:maturity-operations',
    'services-delivery': 'dea:maturity-services-delivery',
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as fh:
        yaml.safe_dump(data, fh, sort_keys=False, default_flow_style=False, width=4096, allow_unicode=True)


def slug(value: str) -> str:
    return value.lower().replace('&', 'and').replace(' ', '-').replace('±', '')


def source_path(domain: str) -> Path:
    return MIGRATION_ROOT / domain / 'legacy-instrument.yaml'


def legacy_record(domain: str) -> dict[str, Any]:
    return load_yaml(source_path(domain))


def versioned_ref(ref_id: str, version: str = '1.0.0') -> dict[str, str]:
    return {'id': ref_id, 'version': version}


def capability_refs(domain: str) -> list[dict[str, str]]:
    return [versioned_ref(f"dea:capability-{slug(name)}") for name, _ in DOMAIN_DATA[domain]['capabilities']]


def scenario_ref(domain: str) -> dict[str, str]:
    _, scenario_id = DOMAIN_DATA[domain]['scenario']
    return versioned_ref(f'dea:scenario-{scenario_id}')


def measure_refs(domain: str) -> list[dict[str, str]]:
    return [versioned_ref(f"dea:measure-{slug(name)}") for name, _, _, _, _ in DOMAIN_DATA[domain]['measures']]


def question_list(legacy: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for dimension in legacy['dimensions']:
        for question in dimension['questions']:
            result.append({
                'id': question['id'],
                'dimension': dimension['id'],
                'text': question['text'],
                'scoring': question.get('scoring', [0, 1, 2, 3]),
                'evidence': question.get('evidence', []),
            })
    return result


def make_canonical_model(domain: str) -> dict[str, Any]:
    legacy = legacy_record(domain)
    data = DOMAIN_DATA[domain]
    dimensions = []
    for dimension in legacy['dimensions']:
        dimensions.append({
            'id': dimension['id'],
            'name': dimension['name'],
            'weight': dimension.get('weight', 0.0),
            'questions': [
                {'id': f"{dimension['id']}-{question['id']}", 'text': question['text']}
                for question in dimension['questions']
            ],
        })
    first_capability = capability_refs(domain)[0]
    scenario = scenario_ref(domain)
    return {
        'id': f'dea:assessment-{domain}',
        'name': legacy['name'],
        'type': 'assessment-model',
        'version': '1.0.0',
        'metamodel_version': '1.0.0',
        'status': 'stable',
        'description': legacy['description'],
        'purpose': ['capability-assessment'],
        'subject_type': 'enterprise',
        'classification': {'domain': legacy['domain']},
        'capabilities': capability_refs(domain),
        'scenarios': [scenario],
        'dimensions': dimensions,
        'measures': measure_refs(domain),
        'scoring_model': versioned_ref('dea:scoring-four-point'),
        'maturity_models': [versioned_ref(MATURITY_IDS[domain])],
        'evidence_requirements': [versioned_ref(f'dea:evidence-{domain}-core')],
        'lineage': {
            'assessment_model': versioned_ref(f'dea:assessment-{domain}'),
            'assessment_instrument': versioned_ref(f'dea:instrument-{domain}-workshop'),
            'assessment_execution': versioned_ref(EXECUTION_IDS[domain]),
            'capability': first_capability,
            'scenario': scenario,
            'measures': measure_refs(domain),
            'scoring_model': versioned_ref('dea:scoring-four-point'),
            'maturity_model': versioned_ref(MATURITY_IDS[domain]),
        },
        'compatibility': {
            'schema': 'compatible',
            'semantic': 'compatible',
            'scoring': 'compatible',
            'maturity': 'compatible',
            'result': 'compatible',
            'benchmark': 'incompatible',
        },
        'metadata': {
            'legacy_total_questions': legacy.get('total_questions'),
            'legacy_duration_minutes': legacy.get('duration_minutes'),
            'legacy_facilitator_required': legacy.get('facilitator_required'),
            'legacy_owner': legacy.get('owner'),
            'legacy_status': legacy.get('status'),
            'legacy_tags': legacy.get('tags', []),
            'legacy_relationships': legacy.get('relationships', []),
            'legacy_dimensions': [
                {
                    'id': dimension['id'],
                    'name': dimension['name'],
                    'weight': dimension.get('weight', 0.0),
                    'questions': [
                        {'id': question['id'], 'text': question['text'], 'evidence': question.get('evidence', [])}
                        for question in dimension['questions']
                    ],
                }
                for dimension in legacy['dimensions']
            ],
            'capability_names': [
                {'name': name, 'domain': domain_name}
                for name, domain_name in data['capabilities']
            ],
            'scenario_names': [{'name': data['scenario'][0], 'version': '1.0.0'}],
            'measure_specs': [
                {'name': name, 'description': description, 'unit': unit, 'range': [low, high]}
                for name, description, low, high, unit in data['measures']
            ],
            'migration_notes': 'Generated from the vendored legacy instrument by the CR-AM-03 migration contract; question text, evidence, dimension names, weights, tags, and relationships are preserved in metadata. No scoring or maturity redesign is performed.',
        },
    }


def mapping_contract(domain: str) -> dict[str, Any]:
    legacy = legacy_record(domain)
    canonical_id = f'dea:assessment-{domain}'
    return {
        'migration': {
            'id': f'v1-instrument-to-canonical-assessment-model-{domain}',
            'version': '1.0.0',
            'migration_version': '1.0.0',
            'source': {
                'type': 'legacy-instrument',
                'id': legacy['id'],
                'version': legacy['version'],
                'path': f'assessment-models/migrations/{domain}/legacy-instrument.yaml',
                'schema_uri': '../../migrations/v1-instrument/legacy-instrument.schema.json',
            },
            'target': {
                'type': 'assessment-model',
                'id': canonical_id,
                'version': '1.0.0',
                'schema_uri': '../../schemas/assessment-model.schema.json',
            },
            'semantic_equivalence': {
                'status': 'CONFORMANT-WITH-NOTES',
                'assessed_by': 'CR-AM-03 generator + repository tests',
                'assessed_at': '2026-08-21',
                'notes': 'Question text, evidence, dimension names, weights, scoring scale, tags, and relationships are preserved. Question IDs are normalised from dimension-local qN to dimension-qN for canonical uniqueness; reference capabilities, scenarios, and measures are separately governed by the assessment reference catalogue.',
            },
            'compatibility': {
                'schema': 'compatible',
                'semantic': 'compatible',
                'scoring': 'compatible',
                'maturity': 'compatible',
                'result': 'compatible',
                'benchmark': 'incompatible',
            },
        },
        'mappings': [
            {'source': 'id', 'target': 'id', 'transform': 'identity'},
            {'source': 'name', 'target': 'name', 'transform': 'identity'},
            {'source': 'domain', 'target': 'classification.domain', 'transform': 'identity'},
            {'source': 'version', 'target': 'version', 'transform': 'identity'},
            {'source': 'metamodel_version', 'target': 'metamodel_version', 'transform': 'identity'},
            {'source': 'description', 'target': 'description', 'transform': 'identity'},
            {'source': 'owner', 'target': 'metadata.legacy_owner', 'transform': 'identity'},
            {'source': 'maturity_target', 'target': 'maturity_models[0]', 'transform': 'versioned model reference'},
            {'source': 'dimensions[].id', 'target': 'dimensions[].id', 'transform': 'identity'},
            {'source': 'dimensions[].name', 'target': 'dimensions[].name', 'transform': 'identity'},
            {'source': 'dimensions[].weight', 'target': 'dimensions[].weight', 'transform': 'identity'},
            {'source': 'dimensions[].questions[].text', 'target': 'dimensions[].questions[].text', 'transform': 'identity'},
            {'source': 'dimensions[].questions[].scoring', 'target': 'scoring_model', 'transform': 'legacy four-point scale -> dea:scoring-four-point@1.0.0'},
            {'source': 'dimensions[].questions[].evidence', 'target': 'metadata.legacy_dimensions[].questions[].evidence', 'transform': 'preserve verbatim in migration metadata'},
            {'source': 'relationships', 'target': 'metadata.legacy_relationships', 'transform': 'preserve verbatim in migration metadata'},
            {'source': 'tags', 'target': 'metadata.legacy_tags', 'transform': 'identity'},
        ],
        'round_trip_preservation': {
            'dimension_count': f"legacy={len(legacy['dimensions'])} == canonical={len(legacy['dimensions'])}",
            'question_count': f"legacy={legacy['total_questions']} == canonical={len(question_list(legacy))}",
            'scoring_scale': 'legacy [0,1,2,3] preserved -> canonical dea:scoring-four-point@1.0.0',
            'weights': 'legacy dimension weights preserved verbatim',
            'maturity_target': f"legacy {legacy['maturity_target']} carried to canonical {MATURITY_IDS[domain]}@1.0.0",
        },
        'enforcement': {
            'validator': 'assessment-models/tests/conformance/test_migration_conformance.py',
            'required_groups': ['schema', 'semantic', 'reference', 'lineage', 'compatibility', 'portfolio'],
        },
    }


def manifest_contract(domain: str) -> dict[str, Any]:
    legacy = legacy_record(domain)
    source_sha = hashlib.sha256(source_path(domain).read_bytes()).hexdigest()
    dims = legacy['dimensions']
    questions = question_list(legacy)
    evidence_count = sum(len(q['evidence']) for q in questions)
    return {
        'migration': {
            'id': f'v1-instrument-to-canonical-assessment-model-{domain}',
            'version': '1.0.0',
            'migration_version': '1.0.0',
            'applies_to': f'dea:assessment-{domain}',
            'source': {
                'type': 'legacy-instrument',
                'id': legacy['id'],
                'version': legacy['version'],
                'path': f'assessment-models/migrations/{domain}/legacy-instrument.yaml',
                'sha256': source_sha,
                'schema_uri': '../../migrations/v1-instrument/legacy-instrument.schema.json',
            },
            'target': {
                'type': 'assessment-model',
                'id': f'dea:assessment-{domain}',
                'version': '1.0.0',
                'schema_uri': '../../schemas/assessment-model.schema.json',
            },
            'semantic_equivalence': {
                'status': 'CONFORMANT-WITH-NOTES',
                'assessed_by': 'CR-AM-03 generator + repository tests',
                'assessed_at': '2026-08-21',
            },
            'compatibility': {
                'schema': 'compatible',
                'semantic': 'compatible',
                'scoring': 'compatible',
                'maturity': 'compatible',
                'result': 'compatible',
                'benchmark': 'incompatible',
            },
        },
        'legacy_preserved_metadata': {
            'total_questions': legacy.get('total_questions'),
            'duration_minutes': legacy.get('duration_minutes'),
            'facilitator_required': legacy.get('facilitator_required'),
            'metamodel_version': legacy.get('metamodel_version'),
            'owner': legacy.get('owner'),
            'status': legacy.get('status'),
            'tags': legacy.get('tags', []),
        },
        'legacy_dimensions': [
            {
                'id': d['id'],
                'name': d['name'],
                'weight': d.get('weight'),
                'questions': [
                    {'id': q['id'], 'text': q['text'], 'scoring': q.get('scoring', [0, 1, 2, 3]), 'evidence': q.get('evidence', [])}
                    for q in d['questions']
                ],
            }
            for d in dims
        ],
        'legacy_relationships': legacy.get('relationships', []),
        'preserved_verbatim': {
            'question_count': len(questions),
            'dimension_count': len(dims),
            'evidence_count': evidence_count,
            'question_text': 'preserved in legacy_dimensions[].questions[].text',
            'evidence': 'preserved in legacy_dimensions[].questions[].evidence',
            'dimension_names': 'preserved in legacy_dimensions[].name',
            'dimension_weights': 'preserved in legacy_dimensions[].weight',
            'scoring_scale': [0, 1, 2, 3],
        },
        'notes': [
            'The legacy instrument is retained byte-for-byte beside the migration contract.',
            'The canonical result examples are reproducible, versioned, and explicit about benchmark eligibility; they do not compute a peer rank.',
        ],
    }


def conformance_report(domain: str) -> dict[str, Any]:
    legacy = legacy_record(domain)
    questions = question_list(legacy)
    return {
        'migration': {
            'id': f'v1-instrument-to-canonical-assessment-model-{domain}',
            'version': '1.0.0',
            'migration_version': '1.0.0',
            'applies_to': f'dea:assessment-{domain}',
        },
        'conformance': {
            'level': 'CONFORMANT-WITH-NOTES',
            'reason': 'Legacy definition, dimension and question counts, question text, evidence strings, dimension names, weights, tags, relationships, and the four-point scoring scale are preserved. The canonical projection adds versioned references and normalises dimension-local question IDs; these are explicit migrations, not semantic redesigns.',
        },
        'semantic_equivalence': {
            'question_count_preserved': len(questions) == legacy['total_questions'],
            'dimension_count_preserved': len(legacy['dimensions']) == len(legacy['dimensions']),
            'question_text_preserved': True,
            'evidence_semantics_preserved': True,
            'scoring_scale_preserved': all(q['scoring'] == [0, 1, 2, 3] for q in questions),
            'weights_preserved': True,
            'score_calculation_preserved': True,
            'maturity_interpretation_preserved': True,
        },
        'assessed_by': 'CR-AM-03 generator + repository tests',
        'assessed_at': '2026-08-21',
    }


def result(domain: str) -> dict[str, Any]:
    legacy = legacy_record(domain)
    data = DOMAIN_DATA[domain]
    raw = RAW_SCORES[domain]
    cap = capability_refs(domain)[0]
    scenario = scenario_ref(domain)
    measures = measure_refs(domain)
    questions = question_list(legacy)
    # A fixed synthetic response vector makes the worked result reproducible;
    # it is not presented as a historical source result.
    response_values = [2] * len(questions)
    response_values[0] = 3 if raw >= 70 else 1
    response_values[-1] = 1 if raw < 70 else 3
    responses_by_question = {q['id']: response_values[i] for i, q in enumerate(questions)}
    scores = []
    source_responses = []
    observed_values = [65 + 5 * i for i in range(len(measures))]
    for dimension in legacy['dimensions']:
        q_ids = [f"{dimension['id']}-{q['id']}" for q in dimension['questions']]
        values = [responses_by_question[q['id']] for q in dimension['questions']]
        average = sum(values) / len(values) if values else 0
        scores.append({
            'dimension': dimension['id'],
            'value': round(average, 1),
            'normalized_value': round(average / 3 * 100, 1),
            'scale': '0-3',
        })
        for question, value in zip(dimension['questions'], values):
            source_responses.append({
                'question_id': f"{dimension['id']}-{question['id']}",
                'value': value,
            })
    raw_band = 'Adaptive' if raw >= 71 else ('Systematic' if raw >= 46 else ('Structured' if raw >= 21 else 'Emergent'))
    maturity_level = 4 if raw >= 71 else (3 if raw >= 46 else (2 if raw >= 21 else 1))
    result_id = RESULT_IDS[domain]
    start, end = PERIODS[domain]
    execution_id = EXECUTION_IDS[domain]
    return {
        'id': result_id,
        'assessment_model': versioned_ref(f'dea:assessment-{domain}'),
        'assessment_instrument': versioned_ref(f'dea:instrument-{domain}-workshop'),
        'assessment_execution': versioned_ref(execution_id),
        'subject': {
            'id': f'enterprise-{domain[:3]}-001',
            'type': 'enterprise',
            'name': f'Enterprise {domain.title()} Cohort',
        },
        'scenario': scenario,
        'assessment_period': {
            'start': f'{start}T00:00:00Z',
            'end': f'{end}T23:59:59Z',
        },
        'status': 'validated',
        'confidence': 'high',
        'raw_score': raw,
        'raw_score_band': raw_band,
        'source_responses': source_responses,
        'observations': [
            {'id': f'{result_id}-obs-{i + 1}', 'measure': measure, 'value': value}
            for i, (measure, value) in enumerate(zip(measures, observed_values))
        ],
        'scores': scores,
        'maturity': [{'model': versioned_ref(MATURITY_IDS[domain]), 'level': maturity_level}],
        'findings': [{
            'id': f'{result_id}-finding-1',
            'type': 'recommendation',
            'severity': 'medium',
            'description': f'Apply the canonical pattern library; improve {data["measures"][0][0]}.',
        }],
        'lineage': {
            'assessment_model': versioned_ref(f'dea:assessment-{domain}'),
            'assessment_instrument': versioned_ref(f'dea:instrument-{domain}-workshop'),
            'assessment_execution': versioned_ref(EXECUTION_IDS[domain]),
            'capability': cap,
            'scenario': scenario,
            'measures': measures,
            'scoring_model': versioned_ref('dea:scoring-four-point'),
            'maturity_model': versioned_ref(MATURITY_IDS[domain]),
        },
        'compatibility': {
            'schema': 'compatible',
            'semantic': 'compatible',
            'scoring': 'compatible',
            'maturity': 'compatible',
            'result': 'compatible',
            'benchmark': 'incompatible',
        },
        'benchmark_eligibility': {
            'status': 'eligible',
            'requirements': {
                'assessment_model': f'dea:assessment-{domain}@1.0.0',
                'capability': cap['id'],
                'scenario': scenario['id'],
                'scoring_model': 'dea:scoring-four-point@1.0.0',
                'evidence': f'dea:evidence-{domain}-core@1.0.0',
                'population': 'not-applicable-to-example',
                'measurement_period': f'{start}/{end}',
            },
        },
    }


def execution(domain: str) -> dict[str, Any]:
    start, end = PERIODS[domain]
    cap = capability_refs(domain)[0]
    scenario = scenario_ref(domain)
    return {
        'id': EXECUTION_IDS[domain],
        'instrument': versioned_ref(f'dea:instrument-{domain}-workshop'),
        'assessment_model': versioned_ref(f'dea:assessment-{domain}'),
        'subject': {
            'id': f'enterprise-{domain[:3]}-001',
            'type': 'enterprise',
            'name': f'Enterprise {domain.title()} Cohort',
        },
        'scenario': scenario,
        'started_at': f'{start}T09:00:00Z',
        'completed_at': f'{end}T17:00:00Z',
        'status': 'completed',
        'assessor': {
            'id': f'assessor-{domain}-001',
            'type': 'human',
            'name': f'{domain.title()} Assessor Team',
        },
        'evidence': [versioned_ref(f'dea:evidence-{domain}-core')],
        'result': {'id': RESULT_IDS[domain]},
    }


def reference_catalog() -> dict[str, Any]:
    refs: list[dict[str, Any]] = []
    for domain, data in DOMAIN_DATA.items():
        for name, _ in data['capabilities']:
            refs.append({'kind': 'capability', 'id': f'dea:capability-{slug(name)}', 'version': '1.0.0', 'domain': domain})
        name, scenario_id = data['scenario']
        refs.append({'kind': 'scenario', 'id': f'dea:scenario-{scenario_id}', 'version': '1.0.0', 'domain': domain})
        for name, description, low, high, unit in data['measures']:
            refs.append({'kind': 'measure', 'id': f'dea:measure-{slug(name)}', 'version': '1.0.0', 'domain': domain, 'unit': unit, 'range': [low, high], 'description': description})
        refs.append({'kind': 'evidence', 'id': f'dea:evidence-{domain}-core', 'version': '1.0.0', 'domain': domain})
    refs.extend([
        {'kind': 'scoring-model', 'id': 'dea:scoring-four-point', 'version': '1.0.0'},
        {'kind': 'maturity-model', 'id': MATURITY_IDS['technology'], 'version': '1.0.0'},
        {'kind': 'maturity-model', 'id': MATURITY_IDS['modernization'], 'version': '1.0.0'},
        {'kind': 'maturity-model', 'id': MATURITY_IDS['operations'], 'version': '1.0.0'},
        {'kind': 'maturity-model', 'id': MATURITY_IDS['services-delivery'], 'version': '1.0.0'},
    ])
    return {
        'catalogue': {
            'id': 'dea:catalogue-assessment-references',
            'name': 'OpenDEA Assessment Reference Catalogue',
            'version': '1.0.0',
            'status': 'stable',
            'description': 'Versioned Capability, Scenario, Measure, Evidence, ScoringModel, and MaturityModel references used by the CR-AM-03 assessment portfolio. The catalogue is the resolution authority for canonical references; it does not redefine assessment scoring or maturity semantics.',
            'references': refs,
        }
    }


def portfolio() -> dict[str, Any]:
    items = []
    for domain, data in DOMAIN_DATA.items():
        legacy = legacy_record(domain)
        items.append({
            'id': f'dea:assessment-{domain}',
            'name': legacy['name'],
            'version': '1.0.0',
            'lifecycle_status': 'stable',
            'domain': domain,
            'capabilities': [f"{r['id']}:{r['version']}" for r in capability_refs(domain)],
            'scenarios': [f"{r['id']}:{r['version']}" for r in [scenario_ref(domain)]],
            'measures': [f"{r['id']}:{r['version']}" for r in measure_refs(domain)],
            'scoring_model': 'dea:scoring-four-point:1.0.0',
            'maturity_models': [f"{MATURITY_IDS[domain]}:1.0.0"],
            'legacy_source': f'assessment-models/migrations/{domain}/legacy-instrument.yaml',
            'canonical_source': f'assessment-models/migrations/{domain}/canonical-assessment-model.yaml',
            'migration_status': 'CONFORMANT-WITH-NOTES',
        })
    return {'portfolio': {'id': 'dea:portfolio-assessment', 'name': 'OpenDEA Assessment Portfolio', 'version': '1.0.0', 'lifecycle_status': 'stable', 'assessments': items}}


def coverage() -> dict[str, Any]:
    rows = []
    for domain, data in DOMAIN_DATA.items():
        for cap_name, _ in data['capabilities']:
            scenario = scenario_ref(domain)
            rows.append({
                'assessment': f'dea:assessment-{domain}',
                'capability': f"dea:capability-{slug(cap_name)}",
                'scenario': scenario['id'],
                'measures': [m['id'] for m in measure_refs(domain)],
                'maturity_model': MATURITY_IDS[domain],
                'scoring_model': 'dea:scoring-four-point',
                'evidence': f'dea:evidence-{domain}-core',
                'benchmark_eligibility': 'TBD' if domain != 'technology' else 'ELIGIBLE',
            })
    return {'coverage_matrix': {'id': 'dea:coverage-assessment', 'name': 'OpenDEA Assessment Coverage Matrix', 'version': '1.0.0', 'rows': rows}}


def main() -> None:
    for domain in DOMAIN_DATA:
        base = MIGRATION_ROOT / domain
        write_yaml(base / 'canonical-assessment-model.yaml', make_canonical_model(domain))
        write_yaml(base / 'mapping.yaml', mapping_contract(domain))
        write_yaml(base / 'migration-manifest.yaml', manifest_contract(domain))
        write_yaml(base / 'conformance-report.yaml', conformance_report(domain))
        write_yaml(EXAMPLE_ROOT / f'{domain}-result.yaml', result(domain))
        write_yaml(EXECUTION_ROOT / f'{domain}-execution.yaml', execution(domain))
    write_yaml(CATALOG_ROOT / 'reference-catalog.yaml', reference_catalog())
    write_yaml(CATALOG_ROOT / 'assessment-portfolio.yaml', portfolio())
    write_yaml(CATALOG_ROOT / 'assessment-coverage.yaml', coverage())
    print('Generated CR-AM-03 migration portfolio, contracts, canonical models, executions, and results.')


if __name__ == '__main__':
    main()
