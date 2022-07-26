import json
import logging
import unittest

import os
from pathlib import Path

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def setUp(self) -> None:
        self.orig_metadata = metadata_integration.check_metadata

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

    def test_record_has_severity(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'severity': Severities[BcSeverities.LOW]
            }
        }

        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', checks=['CKV_SECRET_2']))
        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_runner_check_severity(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'severity': Severities[BcSeverities.LOW]
            },
            'CKV_SECRET_6': {
                'severity': Severities[BcSeverities.HIGH]
            }
        }

        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', checks=['MEDIUM']))
        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_skip_check_severity(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'severity': Severities[BcSeverities.LOW]
            },
            'CKV_SECRET_6': {
                'severity': Severities[BcSeverities.HIGH]
            }
        }

        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', skip_checks=['MEDIUM']))
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
        self.assertEqual(7, len(report.failed_checks))
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(len(report.skipped_checks), 1)

    def test_runner_bc_ids(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        # the other tests will implicitly test this value being None

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'id': 'BC_GIT_2'
            }
        }

        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        for fc in report.failed_checks:
            if fc.check_id == 'CKV_SECRET_2':
                self.assertEqual(fc.bc_check_id, 'BC_GIT_2')
            else:
                self.assertIsNone(fc.bc_check_id)

    def tearDown(self) -> None:
        metadata_integration.check_metadata = self.orig_metadata

    def test_runner_requested_file_type_only_ts(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', secrets_scan_file_type=['.ts']))
        self.assertEqual(len(report.failed_checks), 2)

    def test_runner_requested_file_type_only_py(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', secrets_scan_file_type=['.py']))
        self.assertEqual(len(report.failed_checks), 2)

    def test_runner_requested_file_type_only_yml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', secrets_scan_file_type=['.yml']))
        self.assertEqual(len(report.failed_checks), 2)

    def test_runner_requested_file_type_only_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets',
                                                       secrets_scan_file_type=['.tf']))
        self.assertEqual(len(report.failed_checks), 3)

    def test_runner_requested_file_type_only_py_ts_yml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', secrets_scan_file_type=['.yml', '.tf']))
        self.assertEqual(len(report.failed_checks), 5)

    def test_runner_requested_file_type_all(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', secrets_scan_file_type=['all']))
        self.assertEqual(len(report.failed_checks), 11)

    def test_runner_requested_file_only_dockerfile(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', secrets_scan_file_type=['Dockerfile']))
        self.assertEqual(len(report.failed_checks), 2)

    def test_runner_no_requested_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', secrets_scan_file_type=[]))
        self.assertEqual(len(report.failed_checks), 7)


if __name__ == '__main__':
    unittest.main()
