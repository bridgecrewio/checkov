import os
from unittest import TestCase
from unittest import mock
from unittest.mock import MagicMock

from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.terraform.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class TestBaseSolver(TestCase):
    checks_dir = ""

    def setUp(self):
        if not hasattr(self, 'graph_framework'):
            self.graph_framework = "NETWORKX"
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

    def test_get_cached_jsonpath_statement(self):
        # given
        statement = "policy.Statement[?(@.Effect == Allow)].Action[*]"
        solver_1 = BaseAttributeSolver(
            resource_types=["aws_iam_policy"],
            attribute=statement,
            value="iam:*",
            is_jsonpath_check=True,
        )
        solver_2 = BaseAttributeSolver(
            resource_types=["aws_iam_policy"],
            attribute=statement,
            value="iam:*",
            is_jsonpath_check=True,
        )
        jsonpath_parse_mock = MagicMock()

        self.assertEqual(len(BaseAttributeSolver.jsonpath_parsed_statement_cache), 0)

        # when
        solver_1._get_cached_jsonpath_statement(statement=statement)
        self.assertEqual(len(BaseAttributeSolver.jsonpath_parsed_statement_cache), 1)

        # patch jsonpath_ng.parse to be able to check it was really not called again and the cache was properly used
        with mock.patch("checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver.parse", side_effect=jsonpath_parse_mock):
            solver_2._get_cached_jsonpath_statement(statement=statement)

        # then
        self.assertEqual(len(BaseAttributeSolver.jsonpath_parsed_statement_cache), 1)
        jsonpath_parse_mock.assert_not_called()  # jsonpath_ng.parse shouldn't have been called again


def verify_report(report, expected_results):
    for check_id in expected_results:
        found = False
        for resource in expected_results[check_id]['should_pass']:
            for record in report.passed_checks:
                if record.check_id == check_id and record.resource == resource:
                    found = True
                    break
            if not found:
                return f"expected resource {resource} to pass in check {check_id}"
        found = False
        for resource in expected_results[check_id]['should_fail']:
            for record in report.failed_checks:
                if record.check_id == check_id and record.resource == resource:
                    found = True
                    break
            if not found:
                return f"expected resource {resource} to fail in check {check_id}"

    return None
