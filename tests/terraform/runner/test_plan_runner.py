import unittest

import os

from checkov.runner_filter import RunnerFilter
from checkov.terraform.plan_runner import Runner


class TestRunnerValid(unittest.TestCase):

    def test_runner_two_checks_only(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()
        checks_allowlist = ['CKV_AWS_21']
        report = runner.run(root_folder=None,files=[valid_plan_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all', checks=checks_allowlist))
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)
        self.assertEqual(report.get_summary()["failed"],3)
        self.assertEqual(report.get_summary()["passed"],3)


    def test_runner_child_modules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_with_child_modules/tfplan.json"
        runner = Runner()
        report = runner.run(root_folder=None,files=[valid_plan_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all'))
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertEqual(report.get_summary()["failed"],3)
        self.assertEqual(report.get_summary()["passed"],4)

if __name__ == '__main__':
    unittest.main()
