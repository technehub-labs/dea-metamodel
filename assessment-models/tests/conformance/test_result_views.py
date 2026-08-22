"""CR-AM-04 result operations — view derivation conformance tests."""
from __future__ import annotations

import unittest

from runtime.result_operations import AssessmentResultOperations


class TestResultViews(unittest.TestCase):
    def test_views_for_technology(self) -> None:
        result = AssessmentResultOperations.from_domain("technology")
        views = AssessmentResultOperations.views_for(result)
        self.assertEqual(set(views), {"enterprise", "capability", "scenario"})
        self.assertEqual(views["capability"]["capability_id"], "dea:capability-technology-architecture")
        self.assertEqual(views["scenario"]["scenario_id"], "dea:scenario-enterprise-technology-health")
        self.assertGreater(len(views["enterprise"]["measure_ids"]), 0)

    def test_views_for_all_four_domains(self) -> None:
        for d in ("technology", "modernization", "operations", "services-delivery"):
            with self.subTest(domain=d):
                result = AssessmentResultOperations.from_domain(d)
                views = AssessmentResultOperations.views_for(result)
                self.assertEqual(set(views), {"enterprise", "capability", "scenario"})
                self.assertIn(views["scenario"]["scenario_id"], result["lineage"]["scenario"]["id"])

    def test_views_do_not_invent_new_assessment_model(self) -> None:
        """Enterprise/Capability/Scenario views are projections over result facts."""
        result = AssessmentResultOperations.from_domain("operations")
        views = AssessmentResultOperations.views_for(result)
        for view_name, view in views.items():
            self.assertEqual(view["result_id"], result["id"])
            self.assertIn("measure_ids", view)
            self.assertIsInstance(view["measure_ids"], list)
