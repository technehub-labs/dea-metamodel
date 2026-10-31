#!/usr/bin/env python3
"""CR-MET-018: ECF identifier mirror test (metamodel <-> metaframework).

Asserts, for all 49 coordinates, that the metaframework's normative
identifier builder (tools/ecf_coordinates.py coordinate_identifier, made
conventional by CR-ECF-012) produces exactly the identifiers this
repository's drift detector treats as canonical (DOMAIN_ID x STAGE_ID).
This is the bridge that closes the dual-source-of-truth defect: if either
repo changes its identifier convention without the other, this test fails
in whichever CI runs it.

Requires the metaframework checkout at ECF_FRAMEWORK_ROOT (the
ecf-conformance.yml workflow exports it after cloning). Skips offline so
the plain conformance suite (ci.yml, no clone) stays green.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
FWK = Path(os.environ.get('ECF_FRAMEWORK_ROOT', '/home/hermes/dea-work/dea-metaframework'))

DOMAIN_ID = {
    'GovernanceAndExistence': 'governanceExistence',
    'StrategyAndDirection': 'strategyDirection',
    'AgencyAndOrganization': 'agencyOrganization',
    'PartyAndRelationship': 'partyRelationship',
    'ProductAndValue': 'productValue',
    'EnablementAndOperations': 'enablementAndOperations',
    'FinanceAndAccounting': 'financeAccounting',
}
STAGES = ['Conceive', 'Design', 'Build', 'Activate', 'Operate', 'Improve', 'Retire']


def _load_metaframework_module():
    sys.path.insert(0, str(FWK / 'tools'))
    spec = importlib.util.spec_from_file_location('ecf_coordinates', FWK / 'tools' / 'ecf_coordinates.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pytestmark = pytest.mark.skipif(
    not (FWK / 'tools' / 'ecf_coordinates.py').exists(),
    reason=f"metaframework checkout not present at {FWK} (offline run; enforced online by ecf-conformance.yml)",
)


def test_metaframework_has_domain_id_table() -> None:
    ecf = _load_metaframework_module()
    assert ecf.DOMAIN_ID == DOMAIN_ID, (
        "metaframework DOMAIN_ID drifted from the metamodel convention; "
        "reconcile before merging either side"
    )


@pytest.mark.parametrize('domain,domain_id', sorted(DOMAIN_ID.items()))
def test_coordinate_identifier_matches_domain_id(domain: str, domain_id: str) -> None:
    ecf = _load_metaframework_module()
    for stage in STAGES:
        got = ecf.coordinate_identifier(domain, stage)
        want = f"ecf:{domain_id}.{stage.lower()}"
        assert got == want, f"{domain}/{stage}: builder {got!r} != detector-canonical {want!r}"


def test_full_49_space_equality() -> None:
    ecf = _load_metaframework_module()
    builder_space = {
        ecf.coordinate_identifier(d, s) for d in DOMAIN_ID for s in STAGES
    }
    detector_space = {f"ecf:{i}.{s.lower()}" for i in DOMAIN_ID.values() for s in STAGES}
    assert builder_space == detector_space
    assert len(builder_space) == 49
