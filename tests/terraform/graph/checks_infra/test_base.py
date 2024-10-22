import os
from unittest import TestCase
from unittest import mock

from parameterized import parameterized_class

from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.terraform.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS


@parameterized_class(
    PARAMETERIZED_GRAPH_FRAMEWORKS
)
class TestBaseSolver(TestCase):
    checks_dir = ""

    def setUp(self):
        with mock.patch.dict(os.environ, {"CHECKOV_GRAPH_FRAMEWORK": self.graph_framework}):
            self.source = "Terraform"
            self.registry = Registry(parser=GraphCheckParser(), checks_dir=self.checks_dir)
            self.registry.load_checks()
            self.runner = Runner(external_registries=[self.registry])

    def run_test(self, root_folder, expected_results, check_id):
        root_folder = os.path.realpath(os.path.join(self.checks_dir, root_folder))
        report = self.runner.run(root_folder=root_folder, runner_filter=RunnerFilter(checks=[check_id]))
        verification_results = verify_report(report=report, expected_results=expected_results)
        self.assertIsNone(verification_results, verification_results)

    def test_unrendered_variable_source(self):
        self.assertTrue(BaseAttributeSolver._is_variable_dependant("var.location", "Terraform"))
        self.assertTrue(BaseAttributeSolver._is_variable_dependant("var.location", "terraform"))


def verify_report(report, expected_results):
    for check_id in expected_results:
        found = False
        should_pass_checks = expected_results[check_id].get('should_pass', [])
        for resource in should_pass_checks:
            for record in report.passed_checks:
                if record.check_id == check_id and record.resource == resource:
                    found = True
                    break
            if not found:
                return f"expected resource {resource} to pass in check {check_id}"
        found = False
        should_fail_checks = expected_results[check_id].get('should_fail', [])
        for resource in should_fail_checks:
            for record in report.failed_checks:
                if record.check_id == check_id and record.resource == resource:
                    found = True
                    break
            if not found:
                return f"expected resource {resource} to fail in check {check_id}"

    return None
