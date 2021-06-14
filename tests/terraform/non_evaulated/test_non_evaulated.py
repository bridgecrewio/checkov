import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.runner import Runner


class TestNonEvaluated(unittest.TestCase):

    def test_resource_value_doesnt_exist(self):
        resources_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      "resources", "resource_value_without_var")
        source_files = ["main.tf", "variables.tf"]
        runner = Runner()
        checks_allow_list = ['CKV_AWS_21']
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allow_list))

        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(len(report.failed_checks), 1)

    def test_resource_negative_value_doesnt_exist(self):
        resources_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      "resources", "resource_negative_value_without_var")
        source_files = ["main.tf", "variables.tf"]

        runner = Runner()
        checks_allow_list = ['CKV_AWS_57']
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allow_list))

        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(len(report.failed_checks), 1)

    def tearDown(self):
        parser_registry.definitions_context = {}


if __name__ == '__main__':
    unittest.main()
