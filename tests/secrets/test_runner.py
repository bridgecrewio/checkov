import unittest

import os
from pathlib import Path

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def test_runner_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/terraform"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_tf_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/terraform_failed"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(2, len(report.failed_checks))
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_tf_skip_check(self):
        valid_dir_path = Path(__file__).parent / "resources/terraform_skip"

        report = Runner().run(
            root_folder=valid_dir_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework='secrets')
        )

        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(len(report.skipped_checks), 1)

        report.print_console()

    def test_runner_specific_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', checks=['CKV_SECRET_2']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_wildcard_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', checks=['CKV_SECRET*']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_skip_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', skip_checks=['CKV_SECRET_2']))
        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_skip_check_wildcard(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', skip_checks=['CKV_SECRET*']))
        self.assertEqual(len(report.skipped_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_multiple_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(5, len(report.failed_checks))
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(len(report.skipped_checks), 1)

    def test_runner_bc_ids(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        # the other tests will implicitly test this value being None
        bc_integration.ckv_to_bc_id_mapping = {
            'CKV_SECRET_2': 'BC_GIT_2'
        }
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        for fc in report.failed_checks:
            if fc.check_id == 'CKV_SECRET_2':
                self.assertEqual(fc.bc_check_id, 'BC_GIT_2')
            else:
                self.assertIsNone(fc.bc_check_id)


if __name__ == '__main__':
    unittest.main()
